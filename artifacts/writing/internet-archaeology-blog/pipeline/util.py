"""Shared helpers: fetching, slugs, JSON io, glyph hygiene.

Everything here is Python 3.11 stdlib only. All network access in this pipeline
goes through fetch_json() so timeouts and error recording stay uniform.
"""

from __future__ import annotations

import json
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "DeadWebGazette/0.1 (small static-site pipeline; keyless public APIs)"

# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------


def fetch_json(url: str, params: dict | None = None, timeout: float = 8.0):
    """GET a JSON document. Returns (data, None) on success or (None, reason).

    Never raises: every failure is converted into a reason string so callers
    can record the degradation honestly instead of crashing.
    """
    if params:
        sep = "&" if "?" in url else "?"
        url = url + sep + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return json.loads(body.decode("utf-8")), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code} from {host_of(url)}"
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        return None, f"URL error ({reason}) from {host_of(url)}"
    except TimeoutError:
        return None, f"timeout after {timeout:.0f}s ({host_of(url)})"
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, f"bad payload ({exc}) from {host_of(url)}"


def host_of(url: str) -> str:
    try:
        return urllib.parse.urlsplit(url).netloc
    except Exception:  # pragma: no cover - urlsplit does not really raise
        return url


# ---------------------------------------------------------------------------
# Slugs and text
# ---------------------------------------------------------------------------

_SLUG_RE = re.compile("[^a-z0-9]+")


def slugify(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = _SLUG_RE.sub("-", norm.lower()).strip("-")
    return slug or "untitled"


def word_count(text: str) -> int:
    return len(re.findall("[A-Za-z0-9][A-Za-z0-9'&.-]*", text))


# ---------------------------------------------------------------------------
# ASCII folding for fetched text (publication gate: ASCII-safe typography)
# ---------------------------------------------------------------------------

_ASCII_MAP = {
    0x2013: "--",  # en dash
    0x2014: "--",  # em dash
    0x2018: "'", 0x2019: "'",  # curly single quotes
    0x201C: '"', 0x201D: '"',  # curly double quotes
    0x2026: "...",  # ellipsis
    0x00A0: " ",  # nbsp
    0x2022: "*",  # bullet
}


def to_ascii(text: str) -> str:
    """Fold common typographic codepoints to ASCII and drop the rest.

    Fetched API text (HN titles and the like) can contain anything; this is
    the single boundary where it gets normalized before storage.
    """
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append(_ASCII_MAP.get(ord(ch), ""))
    return "".join(out)


# ---------------------------------------------------------------------------
# Glyph hygiene (publication gate: ASCII-only, no emoji, no check marks)
#
# All ranges are built from chr() on purpose: this source file must
# itself stay pure ASCII or it would fail its own scan.
# ---------------------------------------------------------------------------


def _char_range(lo: int, hi: int) -> str:
    return chr(lo) + "-" + chr(hi)


# CJK ideographs, extensions, radicals, kana, and fullwidth forms.
_FORBIDDEN_CJK = re.compile(
    "["
    + _char_range(0x2E80, 0x9FFF)   # CJK radicals through Yi radicals / Han
    + _char_range(0x3000, 0x303F)   # CJK punctuation
    + _char_range(0xFF00, 0xFFEF)   # fullwidth forms
    + "]"
)
# Emoji, misc symbols, dingbats (covers U+2713 U+2714 U+2705 U+2611), plus
# variation selectors such as U+FE0F.
_FORBIDDEN_EMOJI = re.compile(
    "["
    + _char_range(0x1F000, 0x1FAFF)
    + _char_range(0x2600, 0x27BF)
    + chr(0xFE0F)
    + "]"
)
_NON_ASCII = re.compile("[^\x00-\x7f]")


def glyph_scan(text: str):
    """Return glyph violations found in the text (empty list = clean).

    The hard rule is zero non-ASCII: the categorization below only makes the
    report nicer to read.
    """
    hits = []
    for m in _FORBIDDEN_CJK.finditer(text):
        hits.append(f"CJK codepoint U+{ord(m.group(0)):04X}")
    for m in _FORBIDDEN_EMOJI.finditer(text):
        hits.append(f"emoji/forbidden symbol U+{ord(m.group(0)):04X}")
    for m in _NON_ASCII.finditer(text):
        hits.append(f"non-ASCII codepoint U+{ord(m.group(0)):04X}")
    seen, ordered = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return ordered


# ---------------------------------------------------------------------------
# JSON io (compact, deterministic key order, ASCII-safe)
# ---------------------------------------------------------------------------


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=1, sort_keys=True, ensure_ascii=True)
    # indent=1 keeps files readable but compact; the size gate (100KB per text
    # file) is asserted by run.py --verify, not here.
    path.write_text(text + "\n", encoding="utf-8")
