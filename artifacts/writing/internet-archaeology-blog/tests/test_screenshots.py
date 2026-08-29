"""Unit tests for the screenshot (render-don't-fetch) stage. Stdlib only.

Run from the artifact root:

    python3 -m unittest discover -s tests -v

Everything here is offline and environment-neutral except the two
local-render cases, which skip when no browser binary exists. No test
touches the tracked content tree: scratch copies of posts, scratch
screenshot directories, and scratch builds all live in a TemporaryDirectory,
so a test can never publish an image or edit a real post.
"""

from __future__ import annotations

import functools
import http.server
import shutil
import struct
import sys
import tempfile
import threading
import time
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import screenshots, site  # noqa: E402
import run  # noqa: E402


def make_png(width: int = 1024, height: int = 640, pad: int = 0) -> bytes:
    """A valid grayscale PNG built with stdlib zlib/crc32 (white pixels),
    optionally padded past the payload floor to imitate a content-rich render.
    """

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return (struct.pack(">I", len(data)) + body
                + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\xff" * width for _ in range(height))
    return (screenshots.PNG_MAGIC + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
            + b"\x00" * pad)


class TestUrlConstruction(unittest.TestCase):
    def test_playback_url_with_timestamp(self):
        self.assertEqual(
            screenshots.archived_page_url("http://winamp.com", "19981205015145"),
            "https://web.archive.org/web/19981205015145/http://winamp.com",
        )

    def test_playback_url_without_timestamp_is_nearest_capture_form(self):
        self.assertEqual(
            screenshots.archived_page_url("http://winamp.com", None),
            "https://web.archive.org/web/2/http://winamp.com",
        )

    def test_playback_url_strips_slashes_from_timestamp(self):
        self.assertEqual(
            screenshots.archived_page_url("http://a.com", "/20010130072000/"),
            "https://web.archive.org/web/20010130072000/http://a.com",
        )

    def test_cdx_params_prefer_status_200_earliest_capture(self):
        params = screenshots.cdx_params("http://etoys.com")
        self.assertEqual(params["filter"], "statuscode:200")
        self.assertEqual(params["limit"], 1)
        self.assertIn("timestamp", params["fl"])
        self.assertIn("statuscode", params["fl"])

    def test_canonical_url_from_seed_domain(self):
        self.assertEqual(
            screenshots.canonical_url_for({"slug": "s", "domain": "vine.co/"}),
            "http://vine.co",
        )
        self.assertIsNone(screenshots.canonical_url_for({"slug": "s"}))
        self.assertIsNone(screenshots.canonical_url_for({"slug": "s", "domain": ""}))

    def test_timestamp_recovered_from_final_url_after_redirect(self):
        self.assertEqual(
            screenshots.timestamp_from_final_url(
                "https://web.archive.org/web/19970605000000/http://winamp.com"),
            "19970605000000",
        )

    def test_timestamp_recovery_returns_none_when_not_resolvable(self):
        # The nearest-capture form itself carries no 14-digit timestamp.
        self.assertIsNone(screenshots.timestamp_from_final_url(
            "https://web.archive.org/web/2/http://winamp.com"))
        self.assertIsNone(screenshots.timestamp_from_final_url(None))
        self.assertIsNone(screenshots.timestamp_from_final_url(""))


class TestBrowserInvocation(unittest.TestCase):
    """The flag set is a contract (documented in the README as invoked); pin
    it without launching anything."""

    def _cmd(self, **kw):
        return screenshots.browser_cmd(
            "/usr/bin/chromium", Path("/tmp/shot.png"), Path("/tmp/profile"),
            "https://web.archive.org/web/19981205015145/http://winamp.com", **kw)

    def test_chrome_internal_timeout_is_the_capture_bound(self):
        self.assertIn(f"--timeout={screenshots.CHROME_TIMEOUT_MS}",
                      self._cmd())
        # and it is configurable (tests scale it down)
        self.assertIn("--timeout=8000", self._cmd(chrome_timeout_ms=8000))

    def test_virtual_time_budget_is_the_smaller_settle_budget(self):
        self.assertIn(f"--virtual-time-budget={screenshots.VIRTUAL_TIME_BUDGET}",
                      self._cmd())
        self.assertLess(screenshots.VIRTUAL_TIME_BUDGET,
                        screenshots.CHROME_TIMEOUT_MS)

    def test_flag_set_is_the_documented_recipe(self):
        cmd = self._cmd()
        self.assertEqual(cmd[0], "/usr/bin/chromium")
        for flag in ("--headless=new", "--hide-scrollbars", "--disable-gpu",
                     "--no-first-run", "--no-default-browser-check",
                     "--window-size=1024,640"):
            self.assertIn(flag, cmd)
        self.assertEqual(cmd[-1],
                         "https://web.archive.org/web/19981205015145/http://winamp.com")

    def test_wall_guard_has_headroom_over_chromes_own_timeout(self):
        # The wall budget must sit clearly above chrome's --timeout so the
        # browser self-captures first; the guard is for a browser that
        # ignores the flag.
        self.assertGreater(screenshots.RENDER_TIMEOUT,
                           screenshots.CHROME_TIMEOUT_MS / 1000.0 + 15)


class TestPayloadGuards(unittest.TestCase):
    def test_sniff_image(self):
        self.assertEqual(screenshots.sniff_image(screenshots.PNG_MAGIC + b"rest"), ".png")
        self.assertEqual(screenshots.sniff_image(b"\xff\xd8\xff\xe0junk"), ".jpg")
        self.assertIsNone(screenshots.sniff_image(b"<!DOCTYPE html><html>"))
        self.assertIsNone(screenshots.sniff_image(b""))

    def test_png_dimensions(self):
        self.assertEqual(screenshots.png_dimensions(make_png(1024, 640)), (1024, 640))
        self.assertIsNone(screenshots.png_dimensions(b"\x89PNG\r\n\x1a\nshort"))
        self.assertIsNone(screenshots.png_dimensions(b"not a png at all"))

    def test_validate_rejects_empty_and_html(self):
        self.assertNotEqual(screenshots.validate_png(b""), "")
        self.assertNotEqual(screenshots.validate_png(b"<html>404</html>"), "")

    def test_validate_rejects_wrong_dimensions(self):
        small = make_png(800, 600, pad=screenshots.MIN_PNG_BYTES)
        self.assertIn("expected 1024x640", screenshots.validate_png(small))

    def test_validate_rejects_near_blank_render(self):
        blank = make_png(1024, 640)  # a few hundred bytes, far under the floor
        self.assertIn("floor", screenshots.validate_png(blank))

    def test_validate_accepts_content_rich_render(self):
        rich = make_png(1024, 640, pad=screenshots.MIN_PNG_BYTES)
        self.assertEqual(screenshots.validate_png(rich), "")


class TestBrowserDetection(unittest.TestCase):
    def test_no_browser_on_empty_path_reports_actionable_hint(self):
        found, note = screenshots.find_browser(env={"PATH": "/nonexistent"})
        self.assertIsNone(found)
        self.assertIn("CHROME_BIN", note)

    def test_chrome_bin_override_wins(self):
        found, note = screenshots.find_browser(
            env={"PATH": "/nonexistent", "CHROME_BIN": sys.executable})
        self.assertEqual(found, sys.executable)
        self.assertIn("CHROME_BIN", note)

    def test_broken_chrome_bin_is_reported_not_silently_ignored(self):
        found, note = screenshots.find_browser(
            env={"PATH": "/nonexistent", "CHROME_BIN": "/no/such/browser"})
        self.assertIsNone(found)
        self.assertIn("not an executable", note)

    def test_probed_names_are_the_documented_set(self):
        for name in ("google-chrome", "chromium", "msedge", "chrome"):
            self.assertIn(name, screenshots.BROWSER_NAMES)


class TestFrontMatter(unittest.TestCase):
    def _post(self, tmp: Path) -> Path:
        p = tmp / "subject.md"
        p.write_text(
            "---\ntitle: A Subject\nslug: subject\ndate: 2026-08-29\n"
            "illustration: generated\nsources:\n  - Name | https://example.org/x\n"
            "---\n\nFrozen editorial body.\n",
            encoding="utf-8",
        )
        return p

    def test_fields_are_additive_and_body_frozen(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._post(Path(tmp))
            before = screenshots.body_sha256(p)
            changed, note = screenshots.set_front_matter_fields(p, {
                "illustration": "screenshot",
                "screenshot_url": "http://winamp.com",
                "screenshot_archived_url":
                    "https://web.archive.org/web/19981205015145/http://winamp.com",
                "screenshot_timestamp": "19981205015145",
                "screenshot_fetched": "2026-08-29",
            })
            self.assertTrue(changed)
            self.assertEqual(screenshots.body_sha256(p), before)
            raw = p.read_text(encoding="utf-8")
            self.assertIn("illustration: screenshot", raw)
            # New keys insert before the sources list, which stays last.
            self.assertLess(raw.index("screenshot_fetched:"), raw.index("sources:"))
            self.assertTrue(raw.rstrip().endswith("Frozen editorial body."))

    def test_second_run_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._post(Path(tmp))
            fields = {"illustration": "screenshot", "screenshot_fetched": "2026-08-29"}
            screenshots.set_front_matter_fields(p, fields)
            snap = p.read_bytes()
            changed, note = screenshots.set_front_matter_fields(p, fields)
            self.assertFalse(changed)
            self.assertEqual(note, "already up to date")
            self.assertEqual(p.read_bytes(), snap)


POST_FIXTURE = (
    "---\ntitle: A Subject\nslug: subject\nsources:\n  - N | https://e.org/x\n"
    "---\nbody\n"
)


class TestAttemptSubjectDegradation(unittest.TestCase):
    def test_no_browser_degrades_without_touching_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "subject.md"
            p.write_text(POST_FIXTURE, encoding="utf-8")
            body_before = screenshots.body_sha256(p)
            result, worked = screenshots.attempt_subject(
                p, {"slug": "subject", "domain": "winamp.com"},
                root / "shots", "2026-08-29", browser=None)
            self.assertFalse(worked)
            self.assertEqual(result["illustration"], "generated")
            self.assertIsNone(result["stored"])
            self.assertTrue(any("no headless browser" in n for n in result["note"]))
            self.assertEqual(screenshots.body_sha256(p), body_before)
            self.assertFalse((root / "shots").exists())

    def test_existing_binary_is_never_clobbered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "subject.md"
            p.write_text(POST_FIXTURE, encoding="utf-8")
            shots = root / "shots"
            shots.mkdir()
            payload = make_png(4, 4)
            (shots / "subject.png").write_bytes(payload)
            result, worked = screenshots.attempt_subject(
                p, {"slug": "subject", "domain": "winamp.com"},
                shots, "2026-08-29", browser="/bin/true")
            self.assertFalse(worked)
            self.assertEqual(result["illustration"], "screenshot")
            self.assertEqual(result["stored"], "subject.png")
            self.assertEqual((shots / "subject.png").read_bytes(), payload)
            self.assertIn("never-clobber", " ".join(result["note"]))


_PLAYBACK_BODY = (b"<!DOCTYPE html><html><body>"
                  b"<div>web.archive.org playback toolbar</div>"
                  b"<h1>The archived page</h1></body></html>")


class _ArchiveHandler(http.server.BaseHTTPRequestHandler):
    """Loopback stand-in for web.archive.org pre-check behavior: 503 challenge
    (once or forever), a redirecting nearest-capture form, a plain playback
    page. State is per-path so tests stay order-independent."""

    state: dict[str, int] = {}

    def log_message(self, *args):
        pass

    def _send(self, status: int, body: bytes, ctype: str, loc: str = ""):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if loc:
            self.send_header("Location", loc)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        n = self.state.get(self.path, 0) + 1
        self.state[self.path] = n
        if self.path == "/challenge-once":
            if n == 1:
                self._send(503, b"Internet Archive challenge", "text/html")
            else:
                self._send(200, _PLAYBACK_BODY, "text/html")
        elif self.path == "/challenge-always":
            self._send(503, b"Internet Archive challenge", "text/html")
        elif self.path == "/web/2/http://winamp.example":
            self._send(301, b"", "text/html",
                       loc="/web/19990401120000/http://winamp.example")
        elif self.path == "/web/19990401120000/http://winamp.example":
            self._send(200, _PLAYBACK_BODY, "text/html")
        else:
            self._send(404, b"not found", "text/html")


class TestPrecheckBackoffAndFallback(unittest.TestCase):
    """The 503 challenge path: back off, retry exactly once, then judge; and
    the nearest-capture redirect resolving to a real timestamp."""

    @classmethod
    def setUpClass(cls):
        cls.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _ArchiveHandler)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_503_is_backed_off_and_retried_once(self):
        url = f"{self.base}/challenge-once"
        ok, report, _ = screenshots.precheck_archived(url, backoff_503=0.05)
        self.assertTrue(ok, report)
        self.assertIn("retried once", report)
        self.assertEqual(_ArchiveHandler.state["/challenge-once"], 2)

    def test_503_twice_degrades_after_the_single_retry(self):
        url = f"{self.base}/challenge-always"
        ok, report, _ = screenshots.precheck_archived(url, backoff_503=0.05)
        self.assertFalse(ok)
        self.assertIn("HTTP 503", report)
        self.assertIn("retried once", report)
        self.assertEqual(_ArchiveHandler.state["/challenge-always"], 2)

    def test_transport_error_never_sleeps_or_retries(self):
        # A closed loopback port fails at the transport layer: no retry (the
        # backoff is for 503 challenges only, not for unreachable networks).
        ok, report, _ = screenshots.precheck_archived(
            "http://127.0.0.1:1/", backoff_503=0.05)
        self.assertFalse(ok)
        self.assertIn("pre-check", report)
        self.assertNotIn("retried", report)

    def test_nearest_capture_precheck_resolves_timestamp_via_redirect(self):
        url = f"{self.base}/web/2/http://winamp.example"
        ok, report, final_url = screenshots.precheck_archived(url, backoff_503=0.05)
        self.assertTrue(ok, report)
        self.assertEqual(
            screenshots.timestamp_from_final_url(final_url), "19990401120000")
        # and the unresolved form still yields None (label rule)
        self.assertIsNone(screenshots.timestamp_from_final_url(url))


class TestCondensedOutcomes(unittest.TestCase):
    """The RESULT.md size-gate fallback: group by failure class, not by URL."""

    def test_subjects_group_by_failure_class_not_by_url(self):
        results = [
            {"slug": "a", "stored": None, "note": [
                "cdx http://a.com: cdx: URL error (unreachable) from web.archive.org",
                "archived page pre-check: URL error (unreachable)"]},
            {"slug": "b", "stored": None, "note": [
                "cdx http://b.com: cdx: URL error (unreachable) from web.archive.org",
                "archived page pre-check: URL error (unreachable)"]},
            {"slug": "c", "stored": None, "note": [
                "cdx http://c.com: cdx: skipped (circuit open after repeated failures)"]},
            {"slug": "d", "stored": "d.png", "bytes": 40000, "note": []},
        ]
        lines = run.condense_outcomes(results)
        joined = "\n".join(lines)
        self.assertEqual(len(lines), 3)  # two cdx classes + stored
        self.assertIn("stored: 1 subject(s) [d]", joined)
        self.assertIn("URL error (unreachable)", joined)
        self.assertIn("circuit open", joined)
        # The per-subject URL must not leak into the class key.
        self.assertNotIn("http://a.com", joined)

    def test_no_browser_note_is_its_own_class(self):
        results = [{"slug": "x", "stored": None, "note": [
            "skipped: no headless browser binary (see the browser line)"]}]
        self.assertIn("skipped", run.condense_outcomes(results)[0])


class TestScratchBuildConsistency(unittest.TestCase):
    """Flip one scratch post to screenshot mode and check the built page."""

    def test_screenshot_mode_build_is_consistent(self):
        cfg = site.load_config(ROOT / "site_config.json")
        posts = sorted((ROOT / "content" / "posts").glob("*.md"))
        self.assertTrue(posts)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            posts_dir = root / "posts"
            posts_dir.mkdir()
            src = posts[0].read_text(encoding="utf-8")
            slug = posts[0].stem
            p = posts_dir / posts[0].name
            p.write_text(src, encoding="utf-8")
            body_before = screenshots.body_sha256(p)
            screenshots.set_front_matter_fields(p, {
                "illustration": "screenshot",
                "screenshot_url": "http://" + slug + ".example",
                "screenshot_archived_url":
                    "https://web.archive.org/web/19990101000000/http://" + slug + ".example",
                "screenshot_timestamp": "19990101000000",
                "screenshot_fetched": "2026-08-29",
            })
            self.assertEqual(screenshots.body_sha256(p), body_before)
            shots = root / "shots"
            shots.mkdir()
            (shots / f"{slug}.png").write_bytes(make_png(4, 4))
            out = root / "site"
            site.build_site(out, posts_dir, ROOT / "src" / "styles.css", cfg,
                            screenshots_dir=shots)
            txt = (out / "posts" / f"{slug}.html").read_text(encoding="utf-8")
            self.assertIn("screenshot: Wayback Machine", txt)
            self.assertIn("snapshot 19990101000000", txt)
            self.assertIn("Rendered from", txt)
            self.assertIn("https://web.archive.org/web/19990101000000/", txt)
            self.assertNotIn("generated memorial art", txt)
            self.assertTrue((out / "assets" / f"{slug}.png").is_file())
            self.assertEqual((out / "assets" / f"{slug}.png").read_bytes(),
                             (shots / f"{slug}.png").read_bytes())

            # Missing binary: the honest fallback, never a broken img.
            (shots / f"{slug}.png").unlink()
            out2 = root / "site2"
            site.build_site(out2, posts_dir, ROOT / "src" / "styles.css", cfg,
                            screenshots_dir=shots)
            txt2 = (out2 / "posts" / f"{slug}.html").read_text(encoding="utf-8")
            self.assertIn("generated memorial art", txt2)
            self.assertNotIn("screenshot: Wayback Machine", txt2)
            self.assertIn("<svg", txt2)

    def test_nearest_capture_plate_is_labeled_not_dated(self):
        """A /web/2/ render whose timestamp never resolved must print
        'nearest capture', never an invented snapshot date."""
        cfg = site.load_config(ROOT / "site_config.json")
        posts = sorted((ROOT / "content" / "posts").glob("*.md"))
        self.assertTrue(len(posts) > 1)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            posts_dir = root / "posts"
            posts_dir.mkdir()
            src = posts[1].read_text(encoding="utf-8")
            slug = posts[1].stem
            p = posts_dir / posts[1].name
            p.write_text(src, encoding="utf-8")
            body_before = screenshots.body_sha256(p)
            screenshots.set_front_matter_fields(p, {
                "illustration": "screenshot",
                "screenshot_url": "http://" + slug + ".example",
                "screenshot_archived_url":
                    "https://web.archive.org/web/2/http://" + slug + ".example",
                "screenshot_capture_mode": "nearest capture",
                "screenshot_fetched": "2026-08-29",
            })
            self.assertEqual(screenshots.body_sha256(p), body_before)
            shots = root / "shots"
            shots.mkdir()
            (shots / f"{slug}.png").write_bytes(make_png(4, 4))
            out = root / "site"
            site.build_site(out, posts_dir, ROOT / "src" / "styles.css", cfg,
                            screenshots_dir=shots)
            txt = (out / "posts" / f"{slug}.html").read_text(encoding="utf-8")
            self.assertIn("screenshot: Wayback Machine", txt)
            self.assertIn("nearest capture", txt)
            self.assertIn("https://web.archive.org/web/2/", txt)
            self.assertNotIn("snapshot ", txt.split("PROVENANCE")[0])


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@unittest.skipUnless(screenshots.find_browser()[0], "no headless browser on this machine")
class TestLocalRender(unittest.TestCase):
    """Real browser runs against loopback only: proves the subprocess
    invocation, the chrome-internal capture bound, the process-group outer
    guard, and the payload guards. No archive URL is ever requested."""

    @classmethod
    def setUpClass(cls):
        cls.browser = screenshots.find_browser()[0]
        handler = functools.partial(_QuietHandler, directory=str(ROOT / "site"))
        cls.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_renders_content_page_to_valid_png(self):
        data, report = screenshots.render_screenshot(
            self.browser, f"{self.base}/index.html")
        self.assertIsNotNone(data, report)
        self.assertEqual(screenshots.validate_png(data), "")
        self.assertEqual(screenshots.png_dimensions(data), (1024, 640))
        # A page that finishes loading must NOT be captured at the timeout.
        self.assertNotIn("load incomplete", report)

    def test_error_page_render_is_rejected_by_guards(self):
        # A closed loopback port fails fast: the browser writes its own error
        # page as a real PNG. The guards must reject it (or no file at all).
        data, report = screenshots.render_screenshot(
            self.browser, "http://127.0.0.1:1/")
        if data is None:
            self.assertIn("render:", report)
        else:
            reason = screenshots.validate_png(data)
            self.assertNotEqual(reason, "", "an error page must not pass")
            self.assertTrue(
                "floor" in reason or "dimensions" in reason or "not an image" in reason,
                f"unexpected rejection reason: {reason}")


class _StallHandler(http.server.SimpleHTTPRequestHandler):
    """Serves the scratch stall root; /hang.png never answers (the operator's
    Wayback failure mode: one archived subresource never finishes loading)."""

    def __init__(self, *a, directory=None, **kw):
        super().__init__(*a, directory=directory, **kw)

    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.startswith("/hang"):
            time.sleep(600)
            self.send_response(200)
            self.end_headers()
            return
        super().do_GET()


@unittest.skipUnless(screenshots.find_browser()[0], "no headless browser on this machine")
class TestStalledPageRender(unittest.TestCase):
    """THE regression test for the laptop-run failure of 2026-08-29: all 20
    renders died as "timed out after 45s and wrote no file (the archived page
    never finished loading)". Reproduction: a rich real page (the gazette
    index, 67398 bytes rendered) whose first subresource never completes.

    Contract proven here with the real chromium: Chrome's own --timeout
    self-captures (process exits at ~timeout+1s, a PNG is ALWAYS written) even
    when load never completes. On this box's chromium 150 the timeout capture
    of an unloaded page is a BLANK frame (3301 bytes) -- the calibrated floor
    must reject it, so the subject degrades WITH chrome's stderr evidence
    instead of a silent wall kill. A future chromium that composites painted
    content at timeout passes this test too: either way the browser must write
    a valid PNG and exit inside the wall budget."""

    @classmethod
    def setUpClass(cls):
        cls.browser = screenshots.find_browser()[0]
        cls.tmp = tempfile.TemporaryDirectory(prefix="gazette-stall-")
        root = Path(cls.tmp.name)
        for item in ("index.html", "styles.css"):
            shutil.copy2(ROOT / "site" / item, root / item)
        html = (root / "index.html").read_text(encoding="utf-8")
        marker = html.find(">", html.find("<body")) + 1
        (root / "index.html").write_text(
            html[:marker] + '\n<img src="/hang.png" alt="never loads"/>'
            + html[marker:], encoding="utf-8")
        handler = functools.partial(_StallHandler, directory=str(root))
        cls.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.tmp.cleanup()

    def test_stalled_subresource_still_yields_a_written_png_within_budget(self):
        data, report = screenshots.render_screenshot(
            self.browser, f"{self.base}/index.html",
            timeout=30.0, chrome_timeout_ms=8000)
        # The core regression: the browser self-captured instead of being
        # killed by our wall guard (which would return None).
        self.assertIsNotNone(data, report)
        self.assertIsNotNone(screenshots.sniff_image(data))
        self.assertEqual(screenshots.png_dimensions(data), (1024, 640))
        reason = screenshots.validate_png(data)
        if reason:
            # Blank timeout capture (this chromium does not composite before
            # load): the floor must be the rejection, never a silent accept.
            self.assertIn("floor", reason, f"unexpected rejection: {reason}")
            self.assertIn("load incomplete", report)
        else:
            # A chromium that composites painted content at timeout: a real
            # content screenshot of a partially loaded page.
            self.assertNotIn("load incomplete", reason)


if __name__ == "__main__":
    unittest.main()
