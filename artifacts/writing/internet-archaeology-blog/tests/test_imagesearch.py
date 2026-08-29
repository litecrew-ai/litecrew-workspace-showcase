"""Unit tests for the image-search acquisition stage (pipeline/imagesearch).
Stdlib only; run from the artifact root:

    python3 -m unittest discover -s tests -v

Everything here is offline: the Bing parser runs against the sanitized
fixture under tests/fixtures/ (rebuilt from a real async fetch), the Commons
parser against a synthetic API payload, and the full subject attempt against
a loopback server that stands in for both the search endpoint and the image
hosts. No test touches the tracked content tree -- scratch posts, scratch
image directories, and scratch builds live in a TemporaryDirectory.
"""

from __future__ import annotations

import http.server
import json
import struct
import sys
import tempfile
import threading
import unittest
import urllib.parse
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import imagesearch, screenshots, site, util  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "bing_images_async_geocities.html"
GEO_SUBJ = {
    "slug": "geocities", "name": "GeoCities", "aliases": ["geocities"],
    "domain": "geocities.com",
}


def make_png(width: int = 640, height: int = 480, pad: int = 0) -> bytes:
    """A valid grayscale PNG (white pixels), optionally padded past the
    payload floor to imitate a content-rich image."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return (struct.pack(">I", len(data)) + body
                + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\xff" * width for _ in range(height))
    return (screenshots.PNG_MAGIC + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
            + b"\x00" * pad)


def make_jpeg(width: int = 640, height: int = 480, pad: int = 0) -> bytes:
    """Minimal JPEG: SOI + an SOF0 segment carrying the dimensions."""
    sof = struct.pack(">BHH", 8, height, width) + b"\x03" + b"\x00" * 6
    return (b"\xff\xd8\xff\xc0" + struct.pack(">H", len(sof) + 2) + sof
            + b"\xff\xd9" + b"\x00" * pad)


def make_gif(width: int = 640, height: int = 480) -> bytes:
    return (b"GIF89a" + struct.pack("<HH", width, height)
            + b"\x00" * 16 + b"\x3b")


def make_webp_vp8l(width: int = 640, height: int = 480) -> bytes:
    bits = ((width - 1) & 0x3FFF) | (((height - 1) & 0x3FFF) << 14)
    body = b"\x2f" + bits.to_bytes(4, "little")
    return (b"RIFF" + struct.pack("<I", 4 + 8 + len(body)) + b"WEBP"
            + b"VP8L" + struct.pack("<I", len(body)) + body)


POST_FIXTURE = (
    "---\ntitle: A Subject\nslug: subject\nsources:\n  - N | https://e.org/x\n"
    "---\nbody\n"
)


class TestSearchUrl(unittest.TestCase):
    def test_async_endpoint_with_pagination_params(self):
        url = imagesearch.search_url("GeoCities 1999 website screenshot")
        self.assertTrue(url.startswith(
            "https://www.bing.com/images/async?"))
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
        self.assertEqual(q["q"], "GeoCities 1999 website screenshot")
        self.assertEqual(q["mmasync"], "1")   # load-bearing (junk grid otherwise)
        self.assertEqual(q["first"], "0")
        self.assertEqual(q["count"], "35")


class TestParseCandidates(unittest.TestCase):
    """The Bing parser against the sanitized fixture of a real fetch."""

    @classmethod
    def setUpClass(cls):
        cls.cands = imagesearch.parse_candidates(
            FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_parses_real_candidates(self):
        self.assertGreaterEqual(len(self.cands), 6)
        for c in self.cands:
            self.assertTrue(c["murl"].startswith("http"))
            self.assertTrue(c["turl"].startswith("https://ts"))
            self.assertIn("purl", c)

    def test_malformed_block_is_dropped_fail_closed(self):
        self.assertFalse(any("broken.example" in c["purl"] for c in self.cands))

    def test_garbage_and_empty_fail_closed(self):
        self.assertEqual(imagesearch.parse_candidates(""), [])
        self.assertEqual(imagesearch.parse_candidates("<html>nothing</html>"), [])
        self.assertEqual(imagesearch.parse_candidates('m="not json at all"'), [])
        # m blocks without both murl and turl never become candidates
        self.assertEqual(
            imagesearch.parse_candidates(
                'm="{&quot;purl&quot;:&quot;https://x.example/a&quot;}"'),
            [])

    def test_titles_are_ascii_folded_but_raw_kept_for_matching(self):
        cjk = next(c for c in self.cands if "huntscreens" in c["purl"])
        self.assertTrue(cjk["t"].isascii())
        # the raw title carries non-ASCII (the live one is CJK) or at least
        # differs from the folded form on this fixture's CJK entry
        self.assertNotEqual(cjk["t_raw"], "")
        pats = imagesearch.subject_patterns(GEO_SUBJ)
        # the folded title glued "GeoCities" to a number; matching runs on
        # the RAW title, which still contains the subject name
        self.assertTrue(imagesearch.matches_subject(cjk, pats))

    def test_candidate_index_preserves_document_order(self):
        idx = [c["index"] for c in self.cands]
        self.assertEqual(idx, sorted(idx))


class TestStrictMatch(unittest.TestCase):
    def test_title_match_case_insensitive(self):
        pats = imagesearch.subject_patterns(GEO_SUBJ)
        cand = {"t": "What Ever Happened to GeoCities?",
                "purl": "https://www.techspot.com/article/2401-geocities/"}
        self.assertTrue(imagesearch.matches_subject(cand, pats))

    def test_near_miss_spelling_is_rejected(self):
        # "Geocites" (stock site spelling) must NOT count as "GeoCities".
        pats = imagesearch.subject_patterns(GEO_SUBJ)
        cand = {"t": "Geocites hi-res stock photography",
                "purl": "https://www.alamy.com/stock-photo/geocites.html"}
        self.assertFalse(imagesearch.matches_subject(cand, pats))

    def test_short_alias_matches_on_word_boundaries_only(self):
        # "aim" must not match inside "claim" or "domain".
        subj = {"slug": "aim", "name": "AOL Instant Messenger",
                "aliases": ["aim", "aol instant messenger"], "domain": "aim.com"}
        pats = imagesearch.subject_patterns(subj)
        self.assertFalse(imagesearch.matches_subject(
            {"t": "The claim a domain was lost", "purl": "https://x.example/"},
            pats))
        self.assertTrue(imagesearch.matches_subject(
            {"t": "AIM buddy list nostalgia", "purl": "https://x.example/"},
            pats))

    def test_plus_sign_alias_matches(self):
        subj = {"slug": "google-plus", "name": "Google+",
                "aliases": ["google plus", "google+"], "domain": "plus.google.com"}
        pats = imagesearch.subject_patterns(subj)
        self.assertTrue(imagesearch.matches_subject(
            {"t": "Inside Google+ after the shutdown",
             "purl": "https://x.example/a"}, pats))

    def test_dotted_domain_alias_is_escaped(self):
        subj = {"slug": "delicious", "name": "del.icio.us",
                "aliases": ["delicious"], "domain": "del.icio.us"}
        pats = imagesearch.subject_patterns(subj)
        self.assertTrue(imagesearch.matches_subject(
            {"t": "Social bookmarking history",
             "purl": "https://del.icio.us/tag1"}, pats))
        self.assertFalse(imagesearch.matches_subject(
            {"t": "del icio us tribute", "purl": "https://x.example/"}, pats))

    def test_no_patterns_means_no_match(self):
        self.assertFalse(imagesearch.matches_subject(
            {"t": "GeoCities", "purl": "https://x.example/"}, []))


class TestRanking(unittest.TestCase):
    def _c(self, t, purl, murl="https://img.example/x.png", i=0):
        return {"t": t, "t_raw": t, "purl": purl, "murl": murl,
                "turl": "https://ts1.mm.bing.net/th?id=OIP.x&pid=15.1",
                "index": i}

    def test_era_year_and_screenshot_wording_outrank_plain(self):
        subj = dict(GEO_SUBJ, slug="geocities")
        plain = self._c("GeoCities remembered", "https://a.example/1", i=0)
        rich = self._c("GeoCities 1999 website screenshot",
                       "https://www.geocities.com/", i=1)
        ranked = imagesearch.rank_candidates([plain, rich], subj, 1999)
        self.assertIs(ranked[0], rich)

    def test_stock_host_demoted_below_non_stock(self):
        subj = dict(GEO_SUBJ, slug="geocities")
        stock = self._c("GeoCities stock photo", "https://www.alamy.com/x",
                        i=0)
        plain = self._c("GeoCities remembered", "https://a.example/1", i=1)
        ranked = imagesearch.rank_candidates([stock, plain], subj, None)
        self.assertIs(ranked[0], plain)

    def test_ties_keep_bing_order(self):
        subj = dict(GEO_SUBJ, slug="geocities")
        a = self._c("GeoCities one", "https://a.example/1", i=0)
        b = self._c("GeoCities two", "https://b.example/2", i=1)
        ranked = imagesearch.rank_candidates([a, b], subj, None)
        self.assertEqual([c["index"] for c in ranked], [0, 1])


class TestThumbnailUrl(unittest.TestCase):
    def test_width_param_set_on_pid_15_1(self):
        out = imagesearch.thumbnail_url(
            "https://ts2.mm.bing.net/th?id=OIP.ABC&pid=15.1", 600)
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(out).query))
        self.assertEqual(q["w"], "600")
        self.assertEqual(q["id"], "OIP.ABC")
        self.assertEqual(q["pid"], "15.1")  # the pid that honors w


class TestImageGuards(unittest.TestCase):
    def test_sniff_magic_bytes(self):
        self.assertEqual(imagesearch.sniff_image(b"\xff\xd8\xff\xe0junk"), ".jpg")
        self.assertEqual(imagesearch.sniff_image(screenshots.PNG_MAGIC + b"x"), ".png")
        self.assertEqual(imagesearch.sniff_image(b"GIF89a\x00"), ".gif")
        self.assertEqual(imagesearch.sniff_image(b"RIFF\x00\x00\x00\x00WEBP"), ".webp")
        self.assertIsNone(imagesearch.sniff_image(b"<html>error page</html>"))
        self.assertIsNone(imagesearch.sniff_image(b""))
        self.assertIsNone(imagesearch.sniff_image(None))

    def test_dimensions_all_four_formats(self):
        self.assertEqual(imagesearch.image_dimensions(make_png(640, 480)), (640, 480))
        self.assertEqual(imagesearch.image_dimensions(make_jpeg(640, 480)), (640, 480))
        self.assertEqual(imagesearch.image_dimensions(make_gif(640, 480)), (640, 480))
        self.assertEqual(
            imagesearch.image_dimensions(make_webp_vp8l(640, 480)), (640, 480))
        self.assertIsNone(imagesearch.image_dimensions(b"\x89PNG\r\n\x1a\nshort"))
        self.assertIsNone(imagesearch.image_dimensions(b"RIFF____WEBPjunkjunk__"))

    def test_validate_rejects_html_and_unparseable(self):
        self.assertIn("not an image",
                      imagesearch.validate_image(b"<html>404</html>"))
        truncated = screenshots.PNG_MAGIC + b"\x00\x00\x00\x00IHDRbroken"
        self.assertIn("unparseable", imagesearch.validate_image(truncated))

    def test_validate_rejects_narrow_spacer_and_floor(self):
        narrow = make_png(120, 80, pad=imagesearch.MIN_IMAGE_BYTES)
        self.assertIn("floor", imagesearch.validate_image(narrow))  # width floor
        thin = make_png(640, 480)  # a few hundred bytes: under the size floor
        self.assertIn("bytes", imagesearch.validate_image(thin))

    def test_validate_enforces_the_100kb_cap(self):
        fat = make_png(640, 480, pad=imagesearch.MAX_IMAGE_BYTES + 100)
        self.assertIn("cap", imagesearch.validate_image(fat))

    def test_validate_accepts_content_image(self):
        ok = make_png(640, 480, pad=imagesearch.MIN_IMAGE_BYTES)
        self.assertEqual(imagesearch.validate_image(ok), "")


class TestCommons(unittest.TestCase):
    PAYLOAD = {
        "query": {"pages": {
            "10": {"title": "File:GeoCities screenshot 1999.png",
                   "imageinfo": [{
                       "url": "https://upload.wikimedia.org/wikipedia/"
                              "commons/a/a1/GeoCities_1999.png",
                       "descriptionurl": "https://commons.wikimedia.org/"
                                         "wiki/File:GeoCities_screenshot_1999.png",
                       "mime": "image/png", "width": 800, "height": 600,
                       "extmetadata": {
                           "LicenseShortName": {"value": "CC BY-SA 4.0"},
                           "Artist": {"value": "<a href='https://x.example/u'>"
                                               "Some Photographer</a>"}}}]},
            "11": {"title": "File:No license marker.jpg",
                   "imageinfo": [{
                       "url": "https://upload.wikimedia.org/x.jpg",
                       "descriptionurl": "https://commons.wikimedia.org/wiki/"
                                         "File:No_license_marker.jpg",
                       "mime": "image/jpeg", "width": 800, "height": 600,
                       "extmetadata": {}}]},
            "12": {"title": "File:Not an image.pdf",
                   "imageinfo": [{
                       "url": "https://upload.wikimedia.org/x.pdf",
                       "descriptionurl": "https://commons.wikimedia.org/wiki/"
                                         "File:Not_an_image.pdf",
                       "mime": "application/pdf", "width": 800, "height": 600,
                       "extmetadata": {
                           "LicenseShortName": {"value": "Public domain"}}}]},
        }}
    }

    def test_api_url_shape(self):
        url = imagesearch.commons_api_url("GeoCities screenshot")
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
        self.assertEqual(url.split("/")[2], "commons.wikimedia.org")
        self.assertEqual(q["gsrnamespace"], "6")       # File: namespace
        self.assertEqual(q["generator"], "search")
        self.assertIn("extmetadata", q["iiprop"])

    def test_parse_keeps_only_licensed_images(self):
        cands = imagesearch.parse_commons(self.PAYLOAD)
        self.assertEqual(len(cands), 1)  # license-less and non-image dropped
        c = cands[0]
        self.assertEqual(c["license"], "CC BY-SA 4.0")
        self.assertEqual(c["author"], "Some Photographer")  # html stripped
        self.assertTrue(c["page_url"].startswith(
            "https://commons.wikimedia.org/wiki/File:"))

    def test_parse_fails_closed(self):
        self.assertEqual(imagesearch.parse_commons(None), [])
        self.assertEqual(imagesearch.parse_commons({}), [])
        self.assertEqual(imagesearch.parse_commons({"query": {}}), [])
        self.assertEqual(imagesearch.parse_commons({"garbage": 1}), [])


class _SearchHandler(http.server.BaseHTTPRequestHandler):
    """Loopback stand-in: /search serves the fixture; /img.png serves a
    valid padded PNG; anything else 404s."""

    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.startswith("/search"):
            body = FIXTURE.read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
        elif self.path.startswith("/img.png"):
            body = make_png(640, 480, pad=imagesearch.MIN_IMAGE_BYTES)
            self.send_response(200)
        elif self.path.startswith("/tiny.png"):
            body = make_png(640, 480)  # under the size floor
            self.send_response(200)
        elif self.path.startswith("/blocked.png"):
            self.send_response(403)
            self.end_headers()
            return
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TestAttemptBingLoopback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0), _SearchHandler)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _subject_with_loopback_match(self) -> dict:
        """A subject whose strict matches (techspot/glitchback titles) exist
        in the fixture."""
        return {
            "slug": "geocities", "name": "GeoCities", "aliases": ["geocities"],
            "domain": "geocities.com",
        }

    def _run_attempt(self, tmp: Path, subject: dict, query_html: str | None):
        p = tmp / "subject.md"
        p.write_text(POST_FIXTURE, encoding="utf-8")
        body_before = screenshots.body_sha256(p)
        # Point the search endpoint at loopback, and rewrite every non-
        # loopback image URL so the fetch path stays fully offline: original
        # hosts (murl) serve an under-floor PNG (guards reject -> turl
        # fallback), tse thumbnails (turl) serve a valid padded PNG.
        # NB: originals are held in LOCALS -- a plain function stored on the
        # class would come back as a bound method via the descriptor
        # protocol and poison later restores.
        orig_search = imagesearch.search_url
        orig_fetch = imagesearch._fetch
        base = self.base

        def _search(q, first=0, count=35):
            return (query_html if query_html is not None
                    else f"{base}/search?q={urllib.parse.quote(q)}")

        def patched_fetch(url, timeout):
            if url.startswith("http://127.0.0.1"):
                return orig_fetch(url, timeout)
            if "mm.bing.net" in url:
                return orig_fetch(base + "/img.png", timeout)
            return orig_fetch(base + "/tiny.png", timeout)

        def _restore():
            imagesearch.search_url = orig_search
            imagesearch._fetch = orig_fetch

        self.addCleanup(_restore)
        imagesearch.search_url = _search
        imagesearch._fetch = patched_fetch
        result, worked = imagesearch.attempt_bing(
            p, subject, tmp / "images", "2026-08-29", era_year=1999)
        return result, worked, p, body_before

    def test_matched_candidate_is_stored_and_stamped(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, worked, p, body_before = self._run_attempt(
                Path(tmp), self._subject_with_loopback_match(), None)
            self.assertTrue(worked)
            self.assertEqual(result["illustration"], "sourced-image")
            self.assertEqual(result["image_source"], "bing-image-search")
            self.assertTrue(result["stored"])
            self.assertEqual(result["bytes"],
                             (Path(tmp) / "images" / result["stored"]).stat().st_size)
            self.assertLessEqual(result["bytes"], imagesearch.MAX_IMAGE_BYTES)
            # murl attempts hit the under-floor image and were rejected; the
            # stored binary came through the tse-thumbnail fallback, and the
            # recorded image_url is the real thumbnail URL
            self.assertTrue(any("rejected" in n for n in result["note"]))
            self.assertIn("mm.bing.net", result["image_url"])
            # front matter stamped additively; body byte-identical
            self.assertEqual(screenshots.body_sha256(p), body_before)
            raw = p.read_text(encoding="utf-8")
            self.assertIn("illustration: sourced-image", raw)
            self.assertIn("image_source: bing-image-search", raw)
            self.assertIn("image_page_url:", raw)
            self.assertIn("image_url:", raw)
            self.assertIn("image_retrieved: 2026-08-29", raw)

    def test_unmatched_subject_stays_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            subject = {"slug": "cuil", "name": "Cuil", "aliases": ["cuil"],
                       "domain": "cuil.com", "_patch": {}}
            result, worked, p, body_before = self._run_attempt(
                Path(tmp), subject, None)
            self.assertTrue(worked)
            self.assertIsNone(result["stored"])
            self.assertEqual(result["illustration"], "generated")
            self.assertFalse(any((Path(tmp) / "images").glob("*")))
            self.assertEqual(screenshots.body_sha256(p), body_before)
            self.assertTrue(any("0 strict" in n for n in result["note"]))

    def test_search_failure_degrades_without_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            subject = self._subject_with_loopback_match()
            result, worked, p, _ = self._run_attempt(
                Path(tmp), subject, f"{self.base}/no-such-path")
            self.assertTrue(worked)
            self.assertIsNone(result["stored"])
            self.assertEqual(result["illustration"], "generated")
            self.assertTrue(any("bing search:" in n for n in result["note"]))

    def test_existing_binary_never_clobbered(self):
        with tempfile.TemporaryDirectory() as tmp:
            images_dir = Path(tmp) / "images"
            images_dir.mkdir()
            payload = make_png(4, 4)
            (images_dir / "geocities.png").write_bytes(payload)
            p = Path(tmp) / "subject.md"
            p.write_text(POST_FIXTURE, encoding="utf-8")
            result, worked = imagesearch.attempt_bing(
                p, {"slug": "geocities", "name": "GeoCities",
                    "aliases": ["geocities"], "domain": "geocities.com"},
                images_dir, "2026-08-29")
            self.assertFalse(worked)
            self.assertEqual(result["stored"], "geocities.png")
            self.assertEqual((images_dir / "geocities.png").read_bytes(), payload)
            self.assertIn("never-clobber", " ".join(result["note"]))


class TestSourcedImageBuild(unittest.TestCase):
    """Scratch build: sourced-image front matter + a stored binary must
    render an <img>, the honest label, and the attribution link; a missing
    binary must degrade to the labeled generated plate."""

    def _build(self, tmp, fields: dict, store: bool, ext=".png"):
        tmp = Path(tmp)
        posts = sorted((ROOT / "content" / "posts").glob("*.md"))
        posts_dir = tmp / "posts"
        posts_dir.mkdir(parents=True, exist_ok=True)
        src = posts[0].read_text(encoding="utf-8")
        slug = posts[0].stem
        p = posts_dir / posts[0].name
        p.write_text(src, encoding="utf-8")
        body_before = screenshots.body_sha256(p)
        screenshots.set_front_matter_fields(p, fields)
        self.assertEqual(screenshots.body_sha256(p), body_before)
        images = tmp / "images"
        if store:
            images.mkdir(exist_ok=True)
            (images / f"{slug}{ext}").write_bytes(make_png(4, 4))
        out = tmp / "site"
        site.build_site(out, posts_dir, ROOT / "src" / "styles.css",
                        site.load_config(ROOT / "site_config.json"),
                        images_dir=images if store else None)
        return (out / "posts" / f"{slug}.html").read_text(encoding="utf-8"), slug

    def test_bing_sourced_plate_renders_img_label_and_attribution(self):
        with tempfile.TemporaryDirectory() as tmp:
            txt, slug = self._build(tmp, {
                "illustration": "sourced-image",
                "image_source": "bing-image-search",
                "image_page_url": "https://www.techspot.com/article/2401-geocities/",
                "image_url": "https://static.techspot.com/images/x.jpg",
                "image_retrieved": "2026-08-29",
            }, store=True)
            self.assertIn('<div class="hero-mount"><img', txt)
            self.assertIn("historical image: Bing image search", txt)
            self.assertIn("www.techspot.com", txt)
            self.assertIn("retrieved 2026-08-29", txt)
            # attribution is visible as a real link on the page
            self.assertIn('href="https://www.techspot.com/article/2401-geocities/"',
                          txt)
            self.assertIn("Found via", txt)
            self.assertNotIn("generated memorial art", txt)
            self.assertNotIn("screenshot: Wayback Machine", txt)

    def test_commons_plate_renders_license_and_author(self):
        with tempfile.TemporaryDirectory() as tmp:
            txt, _ = self._build(tmp, {
                "illustration": "sourced-image",
                "image_source": "wikimedia-commons",
                "image_page_url": "https://commons.wikimedia.org/wiki/File:X.png",
                "image_url": "https://upload.wikimedia.org/x.png",
                "image_retrieved": "2026-08-29",
                "image_license": "CC BY-SA 4.0",
                "image_author": "Some Photographer",
            }, store=True)
            self.assertIn("via Wikimedia Commons", txt)
            self.assertIn("CC BY-SA 4.0", txt)
            self.assertIn("Some Photographer", txt)

    def test_missing_binary_degrades_to_generated_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            txt, _ = self._build(tmp, {
                "illustration": "sourced-image",
                "image_source": "bing-image-search",
                "image_page_url": "https://x.example/a",
                "image_url": "https://x.example/a.jpg",
                "image_retrieved": "2026-08-29",
            }, store=False)
            self.assertIn("generated memorial art", txt)
            self.assertIn("<svg", txt)
            self.assertNotIn("historical image: Bing image search", txt)


if __name__ == "__main__":
    unittest.main()
