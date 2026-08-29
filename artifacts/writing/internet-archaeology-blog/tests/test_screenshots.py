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
import struct
import sys
import tempfile
import threading
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
            "https://web.archive.org/web/http://winamp.com",
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


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@unittest.skipUnless(screenshots.find_browser()[0], "no headless browser on this machine")
class TestLocalRender(unittest.TestCase):
    """Real browser runs against loopback only: proves the subprocess
    invocation, the process-group timeout bound, and the payload guards.
    No archive URL is ever requested."""

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


if __name__ == "__main__":
    unittest.main()
