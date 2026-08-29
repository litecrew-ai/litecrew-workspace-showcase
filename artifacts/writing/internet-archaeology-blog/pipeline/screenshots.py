"""Screenshot stage: real archived screenshots, honestly labeled.

A "screenshot" plate is bytes actually fetched from the Internet Archive for
the subject's canonical URL -- never a mockup, never a stand-in. The stage:

  1. resolves each subject's canonical URL (seed-corpus domain);
  2. looks up a representative snapshot timestamp via the Wayback CDX API
     (the earliest capture with status 200 -- a site's first archived look);
  3. fetches https://web.archive.org/screenshot/<url>?timestamp=<ts>;
  4. stores the binary only if the payload is a real image (magic-byte
     sniffed; an HTML error page is a failure, not a screenshot);
  5. stamps the post front matter additively (illustration mode plus
     provenance fields); post bodies are preserved byte-for-byte.

Every attempt (success, HTTP code, bytes, error string) is returned as a log
line for RESULT.md. When the archive is unreachable -- the norm in this build
environment -- the subject degrades to `illustration: generated` and the page
says so. Run via `python3 run.py --fetch-screenshots`.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from . import util

CDX_URL = "http://web.archive.org/cdx/search/cdx"
SCREENSHOT_URL = "https://web.archive.org/screenshot/"

CDX_TIMEOUT = 5.0
SHOT_TIMEOUT = 10.0

IMAGE_EXTS = (".png", ".jpg")


def canonical_url_for(subject: dict) -> str | None:
    """The subject's canonical URL from the seed corpus domain."""
    domain = (subject or {}).get("domain") or ""
    domain = domain.strip().strip("/")
    if not domain or "." not in domain:
        return None
    return "http://" + domain


def lookup_timestamp(url: str, timeout: float = CDX_TIMEOUT) -> tuple[str | None, str]:
    """Earliest Wayback CDX capture with status 200 for the exact URL.

    CDX default order is ascending by timestamp, so limit=1 after the status
    filter yields the oldest clean capture -- the most archaeological look we
    can cite. Returns (timestamp, "") or (None, reason).
    """
    params = {
        "url": url,
        "output": "json",
        "limit": 1,
        "fl": "timestamp,original,statuscode",
        "filter": "statuscode:200",
    }
    data, err = util.fetch_json(CDX_URL, params=params, timeout=timeout)
    if err:
        return None, f"cdx: {err}"
    rows = (data or [])[1:] if isinstance(data, list) else []
    if not rows:
        return None, "cdx: no status-200 snapshot for the canonical url"
    return str(rows[0][0]), ""


def sniff_image(data: bytes) -> str | None:
    """Return the extension for a real image payload, else None."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:2] == b"\xff\xd8":
        return ".jpg"
    return None


def fetch_screenshot(url: str, timestamp: str | None,
                     timeout: float = SHOT_TIMEOUT) -> tuple[bytes | None, str, str]:
    """Fetch the archived screenshot. Returns (data, ext, report).

    `ext` is set only when the payload is a genuine PNG/JPEG; anything else
    (HTML error page, redirect notice, empty body) is a failure by the
    truthfulness law, reported with a short payload hint.
    """
    target = SCREENSHOT_URL + url
    if timestamp:
        target += "?timestamp=" + timestamp
    data, status, ctype, err = util.fetch_bytes(target, timeout=timeout)
    if err:
        return None, "", f"screenshot: {err}"
    ext = sniff_image(data or b"")
    if not ext:
        hint = (data or b"")[:60]
        return None, "", (
            f"screenshot: HTTP {status}, not an image "
            f"(content-type {ctype or '?'}, {len(data or b'')} bytes, starts {hint!r})"
        )
    return data, ext, f"screenshot: HTTP {status} {ctype}, {len(data)} bytes"


# ---------------------------------------------------------------------------
# Front matter: additive-only illustration fields
# ---------------------------------------------------------------------------

FM_KEY_RE = re.compile(r"^([a-z_]+):")


def set_front_matter_fields(path: Path, fields: dict[str, str]) -> tuple[bool, str]:
    """Insert or update keys in a post's front matter; body stays byte-identical.

    New keys are inserted before the `sources:` list when present (keeping the
    list last), else appended at the end of the block. Existing keys are
    replaced in place when the value differs. Returns (changed, note).
    """
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return False, "missing front matter"
    end = raw.find("\n---", 3)
    if end < 0:
        return False, "unterminated front matter"
    body = raw[end:]  # preserved byte-for-byte, delimiter included
    fm_lines = raw[3:end].strip("\n").splitlines()

    changed = False
    for key, value in fields.items():
        new_line = f"{key}: {value}"
        idx = next((i for i, l in enumerate(fm_lines)
                    if FM_KEY_RE.match(l) and FM_KEY_RE.match(l).group(1) == key), None)
        if idx is not None:
            if fm_lines[idx].strip() != new_line:
                fm_lines[idx] = new_line
                changed = True
        else:
            src_idx = next((i for i, l in enumerate(fm_lines)
                            if l.startswith("sources:")), None)
            fm_lines.insert(src_idx if src_idx is not None else len(fm_lines), new_line)
            changed = True

    if not changed:
        return False, "already up to date"
    new_raw = raw[:3] + "\n" + "\n".join(fm_lines) + "\n" + body
    if not new_raw.endswith("\n") and raw.endswith("\n"):
        new_raw += "\n"
    # Post-condition: everything after the closing delimiter is untouched.
    assert new_raw.split("\n---", 1)[1] == raw.split("\n---", 1)[1]
    path.write_text(new_raw, encoding="utf-8")
    return True, f"{len(fields)} field(s) applied"


def body_sha256(path: Path) -> str:
    """Hash of everything after the front-matter closing delimiter."""
    raw = path.read_text(encoding="utf-8")
    end = raw.find("\n---", 3)
    return hashlib.sha256(raw[end + 4:].encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# One subject end to end
# ---------------------------------------------------------------------------

def attempt_subject(post_path: Path, subject: dict, shots_dir: Path,
                    fetch_date: str) -> dict:
    """Fetch + store + stamp one subject. Returns a result dict for the log."""
    slug = subject["slug"]
    result = {
        "slug": slug, "canonical_url": None, "stored": None, "timestamp": None,
        "bytes": None, "illustration": "generated", "note": [],
    }

    existing = [e for e in IMAGE_EXTS if (shots_dir / f"{slug}{e}").exists()]
    if existing:
        # Never-clobber: a stored screenshot is a source asset; refetch by
        # deleting the file first (documented in README).
        ext = existing[0]
        size = (shots_dir / f"{slug}{ext}").stat().st_size
        result.update(
            stored=f"{slug}{ext}", bytes=size, illustration="screenshot",
            note=[f"already stored ({size} bytes); fetch skipped (never-clobber)"],
        )
        _stamp(post_path, result, fetch_date)
        return result

    url = canonical_url_for(subject)
    result["canonical_url"] = url
    if not url:
        result["note"].append("no canonical url in seed corpus; degraded to generated")
        _stamp(post_path, result, fetch_date)
        return result

    ts, cdx_err = lookup_timestamp(url)
    if ts:
        result["timestamp"] = ts
    result["note"].append(f"cdx {url}: {ts if ts else cdx_err}")
    if cdx_err and "no status-200" not in cdx_err:
        # CDX unreachable: still attempt the screenshot endpoint without a
        # timestamp (it falls back to the latest capture) so the attempt is a
        # real probe, not an assumption that the host is down.
        data, ext, report = fetch_screenshot(url, None)
        result["note"].append(report)
    else:
        data, ext, report = fetch_screenshot(url, ts)
        result["note"].append(report)

    if data and ext:
        shots_dir.mkdir(parents=True, exist_ok=True)
        (shots_dir / f"{slug}{ext}").write_bytes(data)
        result.update(stored=f"{slug}{ext}", bytes=len(data),
                      illustration="screenshot")
    _stamp(post_path, result, fetch_date)
    return result


def _stamp(post_path: Path, result: dict, fetch_date: str) -> None:
    """Write illustration front matter to match what is actually stored."""
    fields = {"illustration": result["illustration"]}
    if result["illustration"] == "screenshot" and result.get("canonical_url"):
        fields["screenshot_url"] = result["canonical_url"]
        if result.get("timestamp"):
            fields["screenshot_timestamp"] = result["timestamp"]
        fields["screenshot_fetched"] = fetch_date
    changed, note = set_front_matter_fields(post_path, fields)
    result["note"].append(f"front matter: {note}")


def result_line(r: dict) -> str:
    parts = [f'{r["slug"]}:']
    if r.get("canonical_url"):
        parts.append(f'url={r["canonical_url"]}')
    if r.get("stored"):
        parts.append(f'STORED {r["stored"]} ({r["bytes"]} bytes)')
    else:
        parts.append(f"not stored; illustration={r['illustration']}")
    parts += r["note"]
    return " -- ".join(parts)


def load_subjects(seed_path: Path) -> dict[str, dict]:
    """slug -> subject map from the seed corpus."""
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    return {s["slug"]: s for s in seed.get("subjects", [])}
