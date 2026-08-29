"""Image-search acquisition stage: real historical images, honestly labeled.

A "sourced-image" plate is a real image file found through an image search
(Bing) or a license-clean repository (Wikimedia Commons), attributed to its
source page on the plate. It is deliberately NOT called a screenshot: the
"screenshot" mode stays reserved for pixels a real browser rendered from the
subject's archived page (screenshots.py). Three routes, tried in order:

  Route 1 -- Bing image search (primary; live from the build box).
    Eve's probes and this run's probes (2026-08-29) agree that
    www.bing.com/images/search 302-redirects to cn.bing.com from this
    network, and that the server-rendered grid there is BOT-FILLER JUNK for
    our queries (cat memes for "GeoCities website screenshot", anime
    wallpapers for "Winamp"; 0/35 candidates matched while the page title
    echoed the right query). The REAL result set comes from the async
    endpoint the grid itself paginates with:

        https://www.bing.com/images/async?q=<query>&first=0&count=35&mmasync=1

    which answered 200 with 35 parseable candidates, 33/35 strict-matching
    the GeoCities query. Query shape (experimented on 4 subjects, recorded
    in RESULT.md): "<name> <era-year> website screenshot" -- the era year
    raised or held the strict-matched count on every subject tested
    (4-vs-0 on pets-com) and raised era-relevant matches. The era year is
    the same deterministic peak>death>launch anchor the render route uses
    (screenshots.era_anchor_year), read from the subject's own fact sheet.

    Per candidate: STRICT subject match first -- a word-boundary form of the
    subject name, an alias, or the domain must appear in the title `t` or
    the source page `purl` (case-insensitive); everything else is rejected.
    Matched candidates are ranked deterministically (era year present,
    "screenshot" wording, subject domain in the source page, direct image
    extension; stock-preview hosts demoted). Fetch tries the original host
    (`murl`) first -- some hosts hotlink-protect (a 403 was measured) -- and
    falls back to the Bing thumbnail (`turl`, tse hosts reachable here) at a
    requested width of 600px (`pid=15.1&w=600` honors the width; measured
    600x768 jpeg; `pid=Api` ignores `w`).

  Route 2 -- Wikimedia Commons (license-clean; needs a network with
    wikimedia egress, e.g. the operator laptop -- the build box gets an SSL
    handshake timeout, recorded in RESULT.md). API search in namespace 6
    with prop=imageinfo + extmetadata; only image/* mime; provenance
    includes the file page URL, author, and license short name, all
    rendered on the plate (CC-BY family needs author + license visible).
    Fails closed: a file without a license short name is never stored.

  Route 3 -- archived-page render (screenshots.py, probe-gated) stays the
    last resort and is invoked by the caller (run.py --fetch-images), not
    here.

Binary guards on anything stored: magic bytes (jpeg/png/gif/webp),
parseable dimensions with width >= 300, a size floor against spacer images,
and a hard 100KB cap (the preferred cap; larger originals are a laptop-route
concern and must be individually size-reported there -- from this box they
are simply rejected and the next candidate is tried). ~4s politeness between
subjects, one query per subject per run. Stored binaries live under
assets/images/<slug>.<ext> as never-clobbered source assets the builder
copies. Front matter is stamped additively only (illustration +
image_source + image_page_url + image_url + image_retrieved [+ license and
author for Commons]); post bodies are preserved byte-for-byte and hash-
checked by the caller. Any doubt -- parse failure, no match, rejected
payload -- degrades the subject to the labeled generated plate.
"""

from __future__ import annotations

import html
import http.client
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import screenshots, util

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BING_ASYNC_URL = "https://www.bing.com/images/async"
COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"

# A desktop UA is required in practice: cn.bing.com serves the junk filler
# grid to anything it can cheaply classify as a bot, and some original hosts
# hotlink-protect against non-browser agents (a 403 was measured with the
# pipeline's own UA in early probing).
DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

QUERY_TAIL = "website screenshot"

SEARCH_TIMEOUT = 25.0
IMAGE_TIMEOUT = 12.0
COMMONS_TIMEOUT = 20.0
INTER_SUBJECT_DELAY = 4.0  # politeness (same budget as the render route)

THUMB_WIDTH = 600          # requested from tse hosts (pid=15.1 honors w)
MAX_CANDIDATES_TRIED = 5   # per subject, in ranked order

# Payload guards. Floor sits well above spacer/tracking pixels (a 1x1 gif is
# tens of bytes; real thumbnails measured 30-50KB). The cap is the preferred
# AND hard cap from this box: over-size originals are a laptop-route concern.
MIN_IMAGE_BYTES = 6000
MAX_IMAGE_BYTES = 100 * 1024
MIN_IMAGE_WIDTH = 300

# Stock-preview hosts serve watermarked, licensed comp images; not first
# choice for a memorial plate. Demoted hard, not banned: the operator chose
# the search route knowingly (see the README licensing section).
STOCK_HOSTS = (
    "alamy.", "gettyimages.", "istockphoto.", "shutterstock.",
    "dreamstime.", "123rf.", "stockphoto", "depositphotos",
)

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


# ---------------------------------------------------------------------------
# Shared fetch (desktop UA; never raises)
# ---------------------------------------------------------------------------

def _clean_url(url: str) -> str:
    """Percent-encode characters http.client refuses to send (spaces and
    control characters appear in real Bing murls -- measured: a candidate
    whose path contained 'PBS Kids - EToys.com ... .jpg'). Structural URL
    characters and existing %XX escapes are left alone."""
    return urllib.parse.quote(url, safe=":/?#[]@!$&'()*+,;=%")


def _fetch(url: str, timeout: float) -> tuple[bytes | None, int | None, str, str]:
    """GET with the desktop UA. Returns (data, status, content_type, err);
    err is "" only when status is 2xx and data is present."""
    req = urllib.request.Request(_clean_url(url), headers={
        "User-Agent": DESKTOP_UA,
        "Accept": "image/*,text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            return data, resp.status, resp.headers.get("Content-Type", ""), ""
    except urllib.error.HTTPError as exc:
        try:
            exc.read(64)
        except Exception:
            pass
        return None, exc.code, "", f"HTTP {exc.code} from {util.host_of(url)}"
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        return None, None, "", f"URL error ({reason}) from {util.host_of(url)}"
    except (TimeoutError, http.client.InvalidURL, ValueError, OSError) as exc:
        return None, None, "", (f"{type(exc).__name__}: {str(exc)[:80]} "
                                f"from {util.host_of(url)}")


# ---------------------------------------------------------------------------
# Route 1: Bing image search
# ---------------------------------------------------------------------------

def search_url(query: str, first: int = 0, count: int = 35) -> str:
    """The async endpoint URL. first/count/mmasync are load-bearing: the
    plain /images/search page serves bot-filler junk from this network."""
    return BING_ASYNC_URL + "?" + urllib.parse.urlencode({
        "q": query, "first": first, "count": count, "mmasync": 1,
    })


def parse_candidates(text: str) -> list[dict]:
    """Parse the server-rendered `class="iusc" m="..."` metadata blocks.

    The m attribute is HTML-escaped JSON ({&quot;...}); a plain-quote shape
    is tolerated. A block counts only when it unescapes to a dict carrying
    both an original image URL (murl) and a thumbnail URL (turl) -- anything
    else is dropped. Fails closed: empty/garbage input yields [].
    """
    out: list[dict] = []
    for raw in re.findall(r'\bm="([^"]+)"', text or ""):
        try:
            payload = json.loads(html.unescape(raw))
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(payload, dict):
            continue
        murl = str(payload.get("murl") or "").strip()
        turl = str(payload.get("turl") or "").strip()
        if not (murl.startswith(("http://", "https://"))
                and turl.startswith(("http://", "https://"))):
            continue
        out.append({
            # t is the ASCII-folded title (storage/labels are ASCII-gated);
            # t_raw keeps the original for MATCHING -- folding can glue a
            # word to a following non-ASCII token ("GeoCities90") and break
            # the word-boundary match on a genuinely relevant candidate.
            "t": util.to_ascii(str(payload.get("t") or "")),
            "t_raw": str(payload.get("t") or ""),
            "purl": str(payload.get("purl") or ""),
            "murl": murl,
            "turl": turl,
            "index": len(out),
        })
    return out


def _term_pattern(key: str) -> re.Pattern:
    """Word-boundary pattern for one match key. The trailing boundary is
    only added when the key ends with a word character ('google+' would
    otherwise never match)."""
    esc = re.escape(key.strip().lower())
    lead = r"\b" if key[:1].isalnum() else ""
    trail = r"\b" if key[-1:].isalnum() else ""
    return re.compile(lead + esc + trail)


def subject_patterns(subject: dict) -> list[re.Pattern]:
    """Strict-match patterns: the subject name, its aliases, and its domain.
    Short generic aliases (aim, msn, vine...) are word-boundary matched so
    'claim'/'domain' can never match 'aim'."""
    keys: list[str] = []
    name = str((subject or {}).get("name") or "").strip()
    if name:
        keys.append(name)
    for alias in (subject or {}).get("aliases") or []:
        alias = str(alias).strip()
        if alias and alias.lower() != name.lower():
            keys.append(alias)
    domain = str((subject or {}).get("domain") or "").strip().strip("/")
    if domain and domain.lower() not in [k.lower() for k in keys]:
        keys.append(domain)
    pats = []
    for k in keys:
        try:
            pats.append(_term_pattern(k))
        except re.error:
            continue
    return pats


def candidate_text(cand: dict) -> str:
    """The text strict match runs against: the RAW title (see parse_candidates
    for why) plus the source page URL. Non-ASCII runs become spaces first --
    a CJK title glued to the subject name ("GeoCities<token>") would
    otherwise defeat the word-boundary match on a genuinely relevant
    candidate."""
    raw = f'{cand.get("t_raw", cand.get("t", ""))} {cand.get("purl", "")}'
    return re.sub(r"[^\x00-\x7f]+", " ", raw).lower()


def matches_subject(cand: dict, patterns: list[re.Pattern]) -> bool:
    """STRICT subject match: name/alias/domain must appear in the title or
    the source page URL. Everything else is rejected outright."""
    if not patterns:
        return False
    text = candidate_text(cand)
    return any(p.search(text) for p in patterns)


def build_query(subject: dict, era_year: int | None) -> str:
    """"<name> <era-year> website screenshot" (the experimented winner);
    without an era year the name carries the query alone."""
    name = str((subject or {}).get("name") or (subject or {}).get("slug") or "").strip()
    parts = [name]
    if era_year:
        parts.append(str(int(era_year)))
    parts.append(QUERY_TAIL)
    return " ".join(parts)


def rank_candidates(matched: list[dict], subject: dict,
                    era_year: int | None) -> list[dict]:
    """Deterministic ranking of strict-matched candidates (best first).

    Scoring: subject domain in the source page (+30); era year visible in
    title/source/image URL (+20); "screenshot" wording (+10); direct image
    extension on the original URL (+5); stock-preview host (-40). Ties keep
    Bing's relevance order (stable sort by candidate index).
    """
    domain = str((subject or {}).get("domain") or "").strip().strip("/").lower()
    year = str(int(era_year)) if era_year else ""

    def score(cand: dict) -> int:
        blob_t = f'{cand.get("t", "")} {cand.get("purl", "")}'.lower()
        blob_all = (blob_t + " " + cand.get("murl", "")).lower()
        s = 0
        if domain and domain in blob_t:
            s += 30
        if year and year in blob_all:
            s += 20
        if "screenshot" in blob_t:
            s += 10
        if cand.get("murl", "").lower().endswith(IMAGE_EXTS):
            s += 5
        if any(h in blob_all for h in STOCK_HOSTS):
            s -= 40
        return s

    return sorted(matched, key=lambda c: (-score(c), c["index"]))


def thumbnail_url(turl: str, width: int = THUMB_WIDTH) -> str:
    """The tse thumbnail URL at a requested width. `pid=15.1` honors `w`
    (measured 600x768); `pid=Api` ignores it, so an existing pid is kept and
    only `w` is set (or added)."""
    parts = urllib.parse.urlsplit(turl)
    query = dict(urllib.parse.parse_qsl(parts.query))
    query["w"] = str(int(width))
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path,
         urllib.parse.urlencode(query), parts.fragment))


# ---------------------------------------------------------------------------
# Binary guards (shared by both routes)
# ---------------------------------------------------------------------------

JPEG_SOFS = frozenset((0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                       0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF))


def sniff_image(data: bytes | None) -> str | None:
    """Return the extension for a real image payload, else None."""
    if not data:
        return None
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:8] == screenshots.PNG_MAGIC:
        return ".png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None


def image_dimensions(data: bytes | None) -> tuple[int, int] | None:
    """(width, height) for jpeg/png/gif/webp, else None (fail closed)."""
    if not data:
        return None
    if data[:8] == screenshots.PNG_MAGIC and len(data) >= 24:
        return (int.from_bytes(data[16:20], "big"),
                int.from_bytes(data[20:24], "big"))
    if data[:6] in (b"GIF87a", b"GIF89a") and len(data) >= 10:
        return (int.from_bytes(data[6:8], "little"),
                int.from_bytes(data[8:10], "little"))
    if data[:3] == b"\xff\xd8\xff":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            if marker == 0xFF:
                i += 1
                continue
            if marker in JPEG_SOFS:
                return (int.from_bytes(data[i + 7:i + 9], "big"),
                        int.from_bytes(data[i + 5:i + 7], "big"))
            i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
        return None
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP" and len(data) >= 20:
        chunk = data[12:16]
        if chunk == b"VP8 " and len(data) >= 30:
            # lossy: 3-byte frame tag, 3-byte start code, then 14-bit
            # width/height (no minus-one encoding here)
            return (int.from_bytes(data[26:28], "little") & 0x3FFF,
                    int.from_bytes(data[28:30], "little") & 0x3FFF)
        if chunk == b"VP8L" and len(data) >= 25:
            # lossless: signature byte, then 14-bit (width-1)/(height-1)
            bits = int.from_bytes(data[21:25], "little")
            return (1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF))
        if chunk == b"VP8X":
            # extended: 24-bit canvas width-1 / height-1
            return (1 + int.from_bytes(data[24:27], "little"),
                    1 + int.from_bytes(data[27:30], "little"))
    return None


def validate_image(data: bytes | None) -> str:
    """Return "" when the payload may be stored, else the rejection reason.

    Layered guards: real image magic; parseable dimensions (an unparseable
    header is rejected, not assumed fine); width floor; size floor against
    spacer images; hard 100KB cap (the preferred cap is the hard cap from
    this box -- a bigger original is a laptop-route concern, individually
    size-reported there).
    """
    if not data:
        return "no bytes"
    ext = sniff_image(data)
    if not ext:
        return (f"payload is not an image (starts {data[:24]!r}) -- likely an "
                "html error document")
    dims = image_dimensions(data)
    if dims is None:
        return f"image header unparseable ({ext}); rejected rather than guessed"
    width, _height = dims
    if width < MIN_IMAGE_WIDTH:
        return (f"image only {width}px wide (< {MIN_IMAGE_WIDTH}px floor); "
                "spacers and buttons are not memorial plates")
    if len(data) < MIN_IMAGE_BYTES:
        return (f"image only {len(data)} bytes (< {MIN_IMAGE_BYTES} floor); "
                "tiny payloads are treated as spacer/tracking images")
    if len(data) > MAX_IMAGE_BYTES:
        return (f"image {len(data)} bytes (> {MAX_IMAGE_BYTES} cap); from this "
                "box only candidates up to the cap are stored -- try the "
                "next candidate (the thumbnail usually fits)")
    return ""


# ---------------------------------------------------------------------------
# Front matter (additive only; body preserved byte-for-byte)
# ---------------------------------------------------------------------------

def _safe_url(url: str) -> str:
    """A URL safe to store in front matter: percent-encoded (no raw spaces
    or control characters -- real candidates carry both) and ASCII-folded
    (the post .md files are under the ASCII glyph gate)."""
    return util.to_ascii(_clean_url(url))


def _stamp(post_path: Path, result: dict, fetch_date: str) -> None:
    """Write illustration front matter to match what is actually stored."""
    fields = {"illustration": result["illustration"]}
    if result["illustration"] == "sourced-image":
        fields["image_source"] = result["image_source"]
        if result.get("image_page_url"):
            fields["image_page_url"] = _safe_url(result["image_page_url"])
        if result.get("image_url"):
            fields["image_url"] = _safe_url(result["image_url"])
        fields["image_retrieved"] = fetch_date
        if result.get("image_license"):
            fields["image_license"] = result["image_license"]
        if result.get("image_author"):
            fields["image_author"] = result["image_author"]
    changed, note = screenshots.set_front_matter_fields(post_path, fields)
    result["note"].append(f"front matter: {note}")


def stored_image_for(images_dir: Path, slug: str) -> str | None:
    """Name of an already-stored image for this slug, or None (any of the
    accepted extensions -- never-clobber covers them all)."""
    for ext in IMAGE_EXTS:
        if (images_dir / f"{slug}{ext}").is_file():
            return f"{slug}{ext}"
    return None


# ---------------------------------------------------------------------------
# Route 1: one subject end to end
# ---------------------------------------------------------------------------

def attempt_bing(post_path: Path, subject: dict, images_dir: Path,
                 fetch_date: str, era_year: int | None = None
                 ) -> tuple[dict, bool]:
    """Search + strict-match + fetch + guard + store + stamp one subject.

    Returns (result_dict_for_the_log, did_network_work). Fails closed: any
    doubt (search error, zero candidates, no strict match, every candidate
    rejected) leaves the subject on the labeled generated plate.
    """
    slug = str(subject.get("slug") or post_path.stem)
    query = build_query(subject, era_year)
    result = {
        "slug": slug, "route": "bing", "query": query, "stored": None,
        "bytes": None, "illustration": "generated", "image_source": None,
        "image_page_url": None, "image_url": None, "note": [],
        "candidates": 0, "matched": 0,
    }

    existing = stored_image_for(images_dir, slug)
    if existing:
        size = (images_dir / existing).stat().st_size
        result.update(
            stored=existing, bytes=size, illustration="sourced-image",
            image_source="bing-image-search",
            note=[f"already stored ({existing}, {size} bytes); fetch skipped "
                  "(never-clobber)"],
        )
        _stamp(post_path, result, fetch_date)
        return result, False

    text, status, _ctype, err = _fetch(search_url(query), SEARCH_TIMEOUT)
    if err or status != 200 or not text:
        result["note"].append(
            f"bing search: {err or f'HTTP {status}'}; no image stored")
        _stamp(post_path, result, fetch_date)
        return result, True
    html_text = text.decode("utf-8", "replace")
    candidates = parse_candidates(html_text)
    result["candidates"] = len(candidates)
    if not candidates:
        result["note"].append(
            "bing search: no iusc metadata parsed (layout change or block "
            "page); fail closed to generated art")
        _stamp(post_path, result, fetch_date)
        return result, True

    patterns = subject_patterns(subject)
    matched = [c for c in candidates if matches_subject(c, patterns)]
    result["matched"] = len(matched)
    if not matched:
        result["note"].append(
            f"bing search: {len(candidates)} candidates parsed, 0 strict "
            "subject matches in title/source page; fail closed to generated art")
        _stamp(post_path, result, fetch_date)
        return result, True

    ranked = rank_candidates(matched, subject, era_year)
    result["note"].append(
        f"bing search: {len(candidates)} parsed, {len(matched)} strict match"
        f"{'es' if len(matched) != 1 else ''} for query '{query}'")
    for cand in ranked[:MAX_CANDIDATES_TRIED]:
        for label, url in (("murl", cand["murl"]),
                           ("turl", thumbnail_url(cand["turl"]))):
            data, status2, _ct, err2 = _fetch(url, IMAGE_TIMEOUT)
            if err2 or status2 != 200 or not data:
                result["note"].append(
                    f"{label} {util.host_of(url)}: {err2 or f'HTTP {status2}'}")
                continue
            bad = validate_image(data)
            if bad:
                result["note"].append(
                    f"{label} {util.host_of(url)}: {len(data)} bytes rejected "
                    f"({bad})")
                continue
            ext = sniff_image(data)
            images_dir.mkdir(parents=True, exist_ok=True)
            (images_dir / f"{slug}{ext}").write_bytes(data)
            result.update(
                stored=f"{slug}{ext}", bytes=len(data),
                illustration="sourced-image", image_source="bing-image-search",
                image_page_url=cand["purl"],
                image_url=url if label == "murl" else cand["turl"],
            )
            result["note"].append(
                f"stored {slug}{ext} via {label} {util.host_of(url)} "
                f"({len(data)} bytes, source page {util.host_of(cand['purl'])})")
            _stamp(post_path, result, fetch_date)
            return result, True
    result["note"].append(
        f"all {min(len(ranked), MAX_CANDIDATES_TRIED)} ranked candidate(s) "
        "tried (murl then turl each); none passed the guards")
    _stamp(post_path, result, fetch_date)
    return result, True


# ---------------------------------------------------------------------------
# Route 2: Wikimedia Commons (license-clean; laptop-run from this network's
# perspective -- this box gets an SSL handshake timeout)
# ---------------------------------------------------------------------------

def commons_api_url(query: str, limit: int = 10) -> str:
    """Commons API search URL: generator=search in namespace 6 (File:) with
    imageinfo + extmetadata so one call yields urls, size, mime, author, and
    license short name."""
    return COMMONS_API_URL + "?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query, "gsrnamespace": 6, "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
    })


_TAG_RE = re.compile(r"<[^>]+>")


def _clean_metadata(value: str) -> str:
    """extmetadata values are HTML (author credit especially): strip tags,
    fold to ASCII, squeeze whitespace."""
    text = _TAG_RE.sub(" ", value or "")
    return " ".join(util.to_ascii(text).split())


def parse_commons(payload: dict | None) -> list[dict]:
    """Parse the API payload into candidates. A file counts only when it has
    an image/* mime, a direct URL, and a file-page URL; the license short
    name is REQUIRED to store (fail closed -- unknown rights are not
    published), the author is kept when present. Empty/garbage -> []."""
    if not isinstance(payload, dict):
        return []
    pages = ((payload.get("query") or {}).get("pages") or {})
    out: list[dict] = []
    for page_id in sorted(pages, key=lambda k: int(k)):
        page = pages[page_id] or {}
        info = ((page.get("imageinfo") or [{}])[0]) or {}
        mime = str(info.get("mime") or "")
        url = str(info.get("url") or "")
        page_url = str(info.get("descriptionurl") or "")
        if not (mime.startswith("image/") and url and page_url):
            continue
        ext = (info.get("extmetadata") or {})
        license_name = _clean_metadata(
            str((ext.get("LicenseShortName") or {}).get("value") or ""))
        if not license_name:
            continue
        out.append({
            "title": util.to_ascii(str(page.get("title") or "")),
            "image_url": url,
            "page_url": page_url,
            "license": license_name,
            "author": _clean_metadata(
                str((ext.get("Artist") or {}).get("value") or "")),
            "width": int(info.get("width") or 0),
            "height": int(info.get("height") or 0),
            "mime": mime,
            "index": len(out),
        })
    return out


def attempt_commons(post_path: Path, subject: dict, images_dir: Path,
                    fetch_date: str) -> tuple[dict, bool]:
    """Commons route for one subject. Same guards + stamping as Bing, plus
    license/author fields so the plate can carry the required attribution."""
    slug = str(subject.get("slug") or post_path.stem)
    query = f'{(subject or {}).get("name") or slug} screenshot'
    result = {
        "slug": slug, "route": "commons", "query": query, "stored": None,
        "bytes": None, "illustration": "generated", "image_source": None,
        "image_page_url": None, "image_url": None, "image_license": None,
        "image_author": None, "note": [], "candidates": 0, "matched": 0,
    }

    existing = stored_image_for(images_dir, slug)
    if existing:
        size = (images_dir / existing).stat().st_size
        result.update(
            stored=existing, bytes=size, illustration="sourced-image",
            image_source="wikimedia-commons",
            note=[f"already stored ({existing}, {size} bytes); fetch skipped "
                  "(never-clobber)"],
        )
        _stamp(post_path, result, fetch_date)
        return result, False

    url = commons_api_url(query)
    req = urllib.request.Request(url, headers={"User-Agent": util.USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=COMMONS_TIMEOUT) as resp:
            body = resp.read()
        payload, err = json.loads(body.decode("utf-8")), ""
    except urllib.error.HTTPError as exc:
        payload, err = None, f"HTTP {exc.code} from commons.wikimedia.org"
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        payload, err = None, f"URL error ({reason}) from commons.wikimedia.org"
    except TimeoutError:
        payload, err = None, "timeout from commons.wikimedia.org"
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        payload, err = None, f"bad payload ({exc}) from commons.wikimedia.org"
    if err:
        result["note"].append(f"commons search: {err}; route degrades "
                              "(laptop-only from the build box network)")
        _stamp(post_path, result, fetch_date)
        return result, True

    candidates = parse_commons(payload)
    result["candidates"] = len(candidates)
    if not candidates:
        result["note"].append(
            "commons search: no licensed image/* files parsed; fail closed")
        _stamp(post_path, result, fetch_date)
        return result, True

    for cand in candidates[:MAX_CANDIDATES_TRIED]:
        if 0 < cand["width"] < MIN_IMAGE_WIDTH:
            result["note"].append(
                f"commons {cand['title']}: {cand['width']}px wide, under the "
                "width floor")
            continue
        data, status, _ct, err2 = _fetch(cand["image_url"], IMAGE_TIMEOUT)
        if err2 or status != 200 or not data:
            result["note"].append(
                f"commons {cand['title']}: {err2 or f'HTTP {status}'}")
            continue
        bad = validate_image(data)
        if bad:
            result["note"].append(
                f"commons {cand['title']}: {len(data)} bytes rejected ({bad})")
            continue
        ext = sniff_image(data)
        images_dir.mkdir(parents=True, exist_ok=True)
        (images_dir / f"{slug}{ext}").write_bytes(data)
        result.update(
            stored=f"{slug}{ext}", bytes=len(data),
            illustration="sourced-image", image_source="wikimedia-commons",
            image_page_url=cand["page_url"], image_url=cand["image_url"],
            image_license=cand["license"], image_author=cand["author"],
        )
        result["note"].append(
            f"stored {slug}{ext} from Commons ({len(data)} bytes, "
            f"{cand['license']}, author {cand['author'] or 'not recorded'})")
        _stamp(post_path, result, fetch_date)
        return result, True
    result["note"].append("commons: no candidate passed the guards")
    _stamp(post_path, result, fetch_date)
    return result, True


def result_line(r: dict) -> str:
    parts = [f'{r["slug"]} [{r.get("route", "?")}]:']
    if r.get("query"):
        parts.append(f'query "{r["query"]}"')
    if r.get("candidates"):
        parts.append(f'{r["candidates"]} parsed / {r.get("matched", 0)} matched')
    if r.get("stored"):
        parts.append(f'STORED {r["stored"]} ({r["bytes"]} bytes)')
    else:
        parts.append(f"not stored; illustration={r['illustration']}")
    parts += r["note"]
    return " -- ".join(parts)
