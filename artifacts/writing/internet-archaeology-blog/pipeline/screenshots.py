"""Screenshot stage: render archived pages with a real browser, honestly labeled.

A "screenshot" plate is pixels a real headless browser rendered from the
subject's real archived page -- never a mockup, never a stand-in. The original
strategy (the `https://web.archive.org/screenshot/<url>` endpoint) is dead:
an operator run from a reachable network on 2026-08-29 recorded HTTP 404 with
an HTML error page for all 20 subjects. The strategy here is therefore
**render, don't fetch**:

  1. resolve each subject's canonical URL (seed-corpus domain);
  2. look up a representative snapshot timestamp via the Wayback CDX API
     (earliest status-200 capture of the exact URL) -- hardened after the
     operator run answered only 5 of 20 lookups inside 5s: 25s timeout, one
     retry, a circuit breaker after repeated transport failures, and a
     ~2s inter-subject delay;
  3. confirm the archived page URL `https://web.archive.org/web/<ts>/<url>`
     actually serves (HTTP 200, and a body that looks like a Wayback playback
     page) BEFORE spending a browser run on it;
  4. render that URL with a headless browser via subprocess (no Python
     packages): the binary comes from $CHROME_BIN or a probe of common
     names/macOS bundles. The capture is bounded by Chrome's OWN
     `--timeout=<ms>` (the browser writes the screenshot when the budget
     expires even if the page never finishes loading -- the laptop run of
     2026-08-29 proved a `--virtual-time-budget`-only invocation stalls
     forever on Wayback pages). Our subprocess wall budget is only the outer
     guard; the browser's stderr tail is reported so runs diagnose themselves;
  5. store the PNG only when the payload passes the layered guards (magic
     bytes, exact window dimensions, a non-trivial size floor calibrated
     against blank/error renders), then stamp the post front matter
     additively (illustration mode plus provenance fields). Post bodies are
     preserved byte-for-byte.

Every attempt (success, HTTP code, bytes, error string) is returned as a log
line for RESULT.md. When the archive is unreachable, or no browser binary
exists, the subject degrades to `illustration: generated` and the page says
so. Run via `python3 run.py --fetch-screenshots`.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.parse import quote

from . import util

CDX_URL = "http://web.archive.org/cdx/search/cdx"
WAYBACK_WEB = "https://web.archive.org/web/"

# The former screenshot endpoint. Kept only as a tombstone: an operator run
# from a reachable network (2026-08-29) got HTTP 404 + an HTML error page for
# every subject, proving the service dead. Nothing in this module calls it.
DEAD_SCREENSHOT_ENDPOINT = "https://web.archive.org/screenshot/<url>"

# CDX hardening: the laptop run answered 5/20 lookups inside 5s and timed out
# on the rest -- CDX is routinely slow for large domains. 25s + one retry,
# and stop hammering after repeated transport-level failures.
CDX_TIMEOUT = 25.0
CDX_RETRIES = 1
CDX_BREAK_AFTER = 4

PRECHECK_TIMEOUT = 20.0     # archived page must answer before the browser runs
PRECHECK_503_BACKOFF = 15.0  # archive 503 challenge/rate limit: wait, retry once
RENDER_TIMEOUT = 75.0       # outer guard ONLY; chrome self-captures at the
                            # --timeout below and exits on its own (measured:
                            # ~timeout + 1s). The guard exists for a browser
                            # that ignores everything; it kills the process group.
INTER_SUBJECT_DELAY = 4.0   # politeness between subjects (raised from 2.0 after
                            # one laptop run drew five HTTP 503 challenge pages)

WINDOW_SIZE = "1024,640"
VIRTUAL_TIME_BUDGET = 10000
# The capture mechanism. Chrome's --timeout is a page-load timeout after which
# the screenshot is written regardless of load state; --virtual-time-budget
# alone NEVER fires a capture while a network load is pending (measured on this
# box's chromium 150 against a stalled subresource: no exit, no file, killed at
# the wall; with --timeout the browser exits at ~timeout+0.8s and always writes
# the PNG). Caveat recorded with the calibration below: when load never
# completes, the timeout capture is a BLANK frame -- the floor rejects it, so
# the subject still degrades, but with chrome's "Page load timed out" stderr
# line in the log instead of a silent wall kill.
CHROME_TIMEOUT_MS = 30000

# Payload guards. Calibration on this machine's chromium, 1024x640 headless:
#   blank page (about:blank)          3301 bytes
#   chrome connection-error page     21768 bytes
#   real content page (gazette index) 67398 bytes
# The floor sits just above the measured chrome error page so a browser error
# render can never be stored as a subject screenshot. Real Wayback playback
# pages carry the archive toolbar plus the archived site and land far above it.
MIN_PNG_BYTES = 24576

IMAGE_EXTS = (".png", ".jpg")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

BROWSER_NAMES = (
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "msedge", "chrome", "edge",
)
MACOS_BROWSERS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
)

NO_BROWSER_HINT = (
    "browser: none found -- set CHROME_BIN=/path/to/a/chrome-or-chromium "
    "binary, or install Google Chrome / Chromium / Microsoft Edge, then "
    "re-run python3 run.py --fetch-screenshots"
)


def canonical_url_for(subject: dict) -> str | None:
    """The subject's canonical URL from the seed corpus domain."""
    domain = (subject or {}).get("domain") or ""
    domain = domain.strip().strip("/")
    if not domain or "." not in domain:
        return None
    return "http://" + domain


def cdx_params(url: str) -> dict:
    """CDX query parameters: earliest status-200 capture of the exact URL."""
    return {
        "url": url,
        "output": "json",
        "limit": 1,
        "fl": "timestamp,original,statuscode",
        "filter": "statuscode:200",
    }


def lookup_timestamp(url: str, timeout: float = CDX_TIMEOUT,
                     retries: int = CDX_RETRIES) -> tuple[str | None, str]:
    """Earliest Wayback CDX capture with status 200 for the exact URL.

    CDX default order is ascending by timestamp, so limit=1 after the status
    filter yields the oldest clean capture -- the most archaeological look we
    can cite. Transport failures are retried once (CDX is routinely slow);
    returns (timestamp, "") or (None, reason).
    """
    last = "cdx: no attempt made"
    for _ in range(max(0, retries) + 1):
        data, err = util.fetch_json(CDX_URL, params=cdx_params(url), timeout=timeout)
        if not err:
            rows = (data or [])[1:] if isinstance(data, list) else []
            if not rows:
                return None, "cdx: no status-200 snapshot for the canonical url"
            return str(rows[0][0]), ""
        last = f"cdx: {err}"
    return None, f"{last} (after {max(0, retries) + 1} attempt(s))"


# Era anchoring for the nearest-capture fallback. /web/2/<url> resolves to
# the MOST RECENT capture Wayback has: for a dead site whose domain is now
# parked (the operator's third laptop run, 2026-08-29, showed altavista
# resolving to a 2026 parked page), that screenshots the parked domain, not
# the remembered site. Wayback's year-anchored form /web/<YYYY>/<url>
# resolves to the capture NEAREST that year, so an anchor taken from the
# subject's own sourced fact sheet keeps the fallback inside the subject's
# life. Selection is deterministic, documented, and unit-tested: a peak
# phrasing (the remembered era) beats a death phrasing (last days of the real
# site), which beats a launch phrasing; a sheet with no year-bearing fact
# degrades to /web/2/ exactly as before. Provenance keeps printing the
# RESOLVED timestamp (recovered from the redirect target), never the anchor
# year, so plate labels stay truthful either way.
YEAR_RE = re.compile(r"\b(19[89]\d|20[0-2]\d)\b")
PEAK_RE = re.compile(
    r"most[- ]visited|most popular|at its peak|peak(?:ed|ing)?|"
    r"tens of millions", re.IGNORECASE)
DEATH_RE = re.compile(
    r"shut[^.]{0,40}\bdown|\bclos(?:e|es|ed|ing)\b|retire(?:d|ment)|"
    r"discontinued|went dark|sunset|wound down|liquidat|bankruptcy",
    re.IGNORECASE)
LAUNCH_RE = re.compile(
    r"launch(?:ed|ing)?|founded|created|first released|released|went public",
    re.IGNORECASE)


def era_anchor_year(sheet: dict | None) -> int | None:
    """Anchor year for the era-anchored fallback URL, read from the fact
    sheet's own confidence-tagged facts: the first fact whose text matches a
    peak / death / launch phrasing (in that priority order) contributes its
    first mentioned year. Returns None when the sheet carries no usable year
    -- the caller then falls back to the /web/2/ form."""
    facts = ((sheet or {}).get("facts")) or []
    for pattern in (PEAK_RE, DEATH_RE, LAUNCH_RE):
        for fact in facts:
            text = str(fact.get("text", ""))
            years = YEAR_RE.findall(text)
            if years and pattern.search(text):
                return int(years[0])
    return None


def archived_page_url(url: str, timestamp: str | None = None,
                      era_year: int | None = None) -> str:
    """The playback URL a browser renders: /web/<ts>/<original-url>. Without a
    timestamp (CDX miss, open circuit breaker) the era-anchored nearest-capture
    form /web/<YYYY>/<original-url> is used when the fact sheet yields an
    anchor year (Wayback resolves it to the capture nearest that year);
    /web/2/<original-url> -- which resolves to the closest capture Wayback
    has, most recent included -- remains only when no era year exists, so the
    render is never skipped just because the CDX index timed out."""
    ts = (timestamp or "").strip().strip("/")
    if ts:
        return WAYBACK_WEB + ts + "/" + url
    anchor = str(int(era_year)) if era_year else "2"
    return WAYBACK_WEB + anchor + "/" + url


FINAL_TS_RE = re.compile(r"/web/(\d{14})/")


def timestamp_from_final_url(url: str | None) -> str | None:
    """Recover the real snapshot timestamp from the URL a nearest-capture
    request landed on (after Wayback's redirect). None when the final URL
    carries no 14-digit timestamp."""
    m = FINAL_TS_RE.search(url or "")
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Browser discovery
# ---------------------------------------------------------------------------

def find_browser(env: dict | None = None) -> tuple[str | None, str]:
    """Locate a headless-capable browser binary.

    $CHROME_BIN wins when it points at an executable file (a bad CHROME_BIN is
    reported as not-found with the fix in the message rather than silently
    falling back). Otherwise common binary names are probed on PATH, then the
    usual macOS app bundles. Returns (path_or_None, note_for_the_log).
    """
    e = os.environ if env is None else env
    override = str(e.get("CHROME_BIN") or "").strip()
    if override:
        if os.path.isfile(override) and os.access(override, os.X_OK):
            return override, f"browser: CHROME_BIN={override}"
        return None, (
            f"browser: CHROME_BIN={override} is not an executable file; "
            "unset it or fix the path (or leave it unset to probe PATH)"
        )
    path = str(e.get("PATH") or "")
    for name in BROWSER_NAMES:
        hit = shutil.which(name, path=path) if path else None
        if hit:
            return hit, f"browser: {name} found at {hit} (PATH probe)"
    for cand in MACOS_BROWSERS:
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand, f"browser: {cand} (macOS app bundle)"
    return None, NO_BROWSER_HINT


# ---------------------------------------------------------------------------
# Render + payload guards
# ---------------------------------------------------------------------------

def sniff_image(data: bytes) -> str | None:
    """Return the extension for a real image payload, else None."""
    if data[:8] == PNG_MAGIC:
        return ".png"
    if data[:2] == b"\xff\xd8":
        return ".jpg"
    return None


def png_dimensions(data: bytes) -> tuple[int, int] | None:
    """(width, height) from a PNG IHDR, or None when absent/truncated."""
    if len(data) < 24 or data[:8] != PNG_MAGIC:
        return None
    return (int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big"))


def validate_png(data: bytes | None) -> str:
    """Return "" when the payload is a plausible rendered page, else a reason.

    Layered anti-fabrication guards: a 0-byte or HTML payload is not an
    image; a PNG of the wrong dimensions is not our render; a PNG under the
    calibrated floor is a blank or browser-error page, not the subject.
    """
    if not data:
        return "render produced no bytes"
    ext = sniff_image(data)
    if not ext:
        return (f"payload is not an image (starts {data[:40]!r}) -- likely an "
                "html error document")
    if ext == ".png":
        dims = png_dimensions(data)
        want = tuple(int(x) for x in WINDOW_SIZE.split(","))
        if dims is None:
            return "png header truncated (no IHDR dimensions)"
        if dims != want:
            return (f"png is {dims[0]}x{dims[1]}, expected "
                    f"{want[0]}x{want[1]} (the render window)")
        if len(data) < MIN_PNG_BYTES:
            return (f"png only {len(data)} bytes (< {MIN_PNG_BYTES} floor); "
                    "near-blank output is treated as a blank or browser-error "
                    "page, not a screenshot of the subject")
    return ""


def precheck_archived(url: str, timeout: float = PRECHECK_TIMEOUT,
                      backoff_503: float = PRECHECK_503_BACKOFF
                      ) -> tuple[bool, str, str | None]:
    """Confirm the render target is a live Wayback playback page first.

    Two guards for the price of one fetch: HTTP 200 (after redirects), and a
    body that references web.archive.org (the playback toolbar does). If the
    archive is unreachable we learn it here, fast, instead of hanging a
    75s browser run; if the URL is not a playback page there is nothing to
    render. An HTTP 503 (the Internet Archive challenge / rate-limit page --
    five of them hit one laptop run) is backed off and retried exactly once.
    Returns (ok, report, final_url_after_redirects) -- the final URL is how a
    nearest-capture form resolves to a real timestamp.
    """
    retried = False
    for attempt in (1, 2):
        body, status, ctype, final_url, err = util.fetch_follow(url, timeout=timeout)
        if err:
            return False, f"archived page pre-check: {err}", final_url
        if status == 503 and attempt == 1:
            time.sleep(max(0.0, backoff_503))
            retried = True
            continue
        break
    note = " (503; backed off and retried once)" if retried else ""
    if status != 200:
        return False, (f"archived page pre-check: HTTP {status}{note}"), final_url
    if b"web.archive.org" not in (body or b""):
        return False, ("archived page pre-check: HTTP 200 but the body does "
                       "not reference web.archive.org (not a playback page)"), final_url
    return True, (f"archived page pre-check: HTTP 200{note}, {len(body or b'')} "
                  f"bytes {ctype or ''}".rstrip()), final_url


def _kill_group(proc: subprocess.Popen) -> None:
    """Kill the browser and every child it spawned (renderers survive a
    parent-only kill). The render runs in its own session for exactly this."""
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except OSError:
            pass
    try:
        proc.wait(timeout=10)
    except Exception:
        pass


STDERR_HEAD_CHARS = 400  # chrome stderr HEAD kept in failure reports: the
                         # fatal launch error usually sits in the first lines
STDERR_TAIL_CHARS = 500  # chrome stderr TAIL kept in failure reports: the
                         # last state before exit

# Chrome/updater bookkeeping lines are diagnostic noise for us: crash-handler
# handshakes, component-updater chatter, background-service VERBOSE logs. The
# operator's third laptop run (2026-08-29) hung with its ENTIRE stderr being
# these lines -- which is itself a signature (see PROFILE_LOCK_HINT): a
# browser that spawned helpers but never proceeded to render.
STDERR_NOISE_RE = re.compile(
    r"crash[-_ ]?handler|crash[-_ ]?reporter|component[-_ ]?updater|"
    r"updater\b|VERBOSE\d|background[-_ ]?network",
    re.IGNORECASE,
)

PROFILE_LOCK_HINT = (
    "filtered stderr is empty after dropping chrome/updater noise and no file "
    "was written: the browser stalled before rendering. Note the invocation "
    "already uses a fresh temp --user-data-dir per render, so the classic "
    "default-profile singleton lock should not apply to THIS code -- the "
    "suspects are environment-specific browser behavior (app-bundle "
    "singleton, flag-set divergence in this Chrome channel, helper "
    "interference). Run `python3 run.py --probe-render` first: it renders an "
    "offline data: page through the same invocation in seconds and says "
    "whether THIS browser can run this recipe headlessly at all. Then try "
    "CHROME_BIN=/path/to/a/chromium, or close the running browser once and "
    "re-probe."
)


def _stderr_report(err: bytes | None, head: int = STDERR_HEAD_CHARS,
                   tail: int = STDERR_TAIL_CHARS) -> str:
    """Chrome's stderr, cleaned for failure reports: drop chrome/updater
    noise lines, squeeze whitespace, then keep BOTH the first ~head and the
    last ~tail chars (the middle is repetition). Empty string when nothing
    survives the filter -- callers treat that as its own signal and print
    PROFILE_LOCK_HINT instead."""
    text = (err or b"").decode("utf-8", "replace")
    keep = [" ".join(l.split()) for l in text.splitlines()]
    keep = [l for l in keep if l and not STDERR_NOISE_RE.search(l)]
    if not keep:
        return ""
    joined = " | ".join(keep)
    if len(joined) <= head + tail:
        return joined
    return joined[:head] + " ...[snip]... " + joined[-tail:]


def browser_cmd(browser: str, shot_path: Path, profile: Path, page_url: str,
                chrome_timeout_ms: int = CHROME_TIMEOUT_MS) -> list[str]:
    """The exact headless invocation, in one place: the README documents these
    flags as invoked, the unit tests assert them without launching anything.

    --timeout is the capture mechanism (see CHROME_TIMEOUT_MS); the window
    size, hidden scrollbars, and GPU flags are unchanged from the recipe proven
    on this machine's chromium.

    Environment independence: --user-data-dir points at a FRESH temp dir
    created per render (see render_screenshot), so the browser never touches
    -- or waits on -- the user's default profile, whose singleton lock the
    daily running browser holds. --no-first-run / --no-default-browser-check
    suppress first-run dialogs; the --disable-* trio keeps helper processes
    (crash reporter, component updater, background networking) from spawning
    at all, which both shrinks stderr noise and removes updater side-trips
    during a 20-subject batch."""
    return [
        browser,
        "--headless=new",
        f"--screenshot={shot_path}",
        f"--window-size={WINDOW_SIZE}",
        f"--virtual-time-budget={VIRTUAL_TIME_BUDGET}",
        f"--timeout={chrome_timeout_ms}",
        "--hide-scrollbars",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-crash-reporter",
        "--disable-component-update",
        "--disable-background-networking",
        f"--user-data-dir={profile}",
        page_url,
    ]


def render_screenshot(browser: str, page_url: str,
                      timeout: float = RENDER_TIMEOUT,
                      chrome_timeout_ms: int = CHROME_TIMEOUT_MS
                      ) -> tuple[bytes | None, str]:
    """Render page_url to PNG bytes with a headless browser. Stdlib only.

    The invocation is the one proven on this machine's chromium and documented
    in the README: Chrome's own --timeout writes the screenshot when the budget
    expires even on a page that never finishes loading (the laptop run of
    2026-08-29 lost all 20 renders because a --virtual-time-budget-only
    invocation never reached load-complete on Wayback). Our subprocess wall
    budget is the outer guard. Every render runs with its OWN fresh temp
    profile dir (created and removed here) so the invocation is independent of
    the machine's browser/profile state. The browser's stderr -- filtered of
    chrome/updater noise, head + tail -- rides along in every failure report
    (an all-noise stderr plus no file prints the profile-lock/probe hint), and
    a "Page load timed out" stderr line is flagged on the success path too
    (that capture is blank on this chromium and the payload guards reject it
    -- the point is the run log says WHY).
    Returns (png_bytes_or_None, report).
    """
    with tempfile.TemporaryDirectory(prefix="gazette-render-") as tmp:
        shot = Path(tmp) / "shot.png"
        profile = Path(tmp) / "profile"  # fresh per render, removed with tmp
        cmd = browser_cmd(browser, shot, profile, page_url, chrome_timeout_ms)
        try:
            proc = subprocess.Popen(
                cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE, start_new_session=True,
            )
        except OSError as exc:
            return None, f"render: cannot launch browser ({exc})"
        try:
            _, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_group(proc)
            try:
                _, err = proc.communicate(timeout=5)
            except Exception:
                err = b""
            diag = _stderr_report(err) or PROFILE_LOCK_HINT
            return None, (
                f"render: wall guard killed the process group after "
                f"{timeout:.0f}s with no file (chrome never reached its own "
                f"--timeout={chrome_timeout_ms}ms; the invocation used a "
                f"fresh temp --user-data-dir); chrome stderr: {diag}"
            )
        if not shot.is_file():
            diag = _stderr_report(err) or PROFILE_LOCK_HINT
            return None, (
                f"render: browser exited {proc.returncode} without writing a "
                f"file; chrome stderr: {diag}"
            )
        data = shot.read_bytes()
        stalled = b"Page load timed out" in (err or b"")
        note = ("; captured at --timeout with load incomplete (chrome: Page "
                "load timed out) -- expect the near-blank guard to reject this"
                if stalled else "")
        return data, (f"render: exit {proc.returncode}, {len(data)} bytes "
                      f"png{note}")


# ---------------------------------------------------------------------------
# Self-probe: does THIS browser run THIS recipe headlessly?
# ---------------------------------------------------------------------------

# A deterministic offline page: big text plus varied-color bars. Text
# anti-aliasing and color variety give the PNG enough entropy that a real
# capture lands well above a blank render (a flat-color page compresses too
# well to separate from blank by size). No network references of any kind.
PROBE_BARS = (
    (96, "#7a1f1f"), (12, "#f0c419"), (63, "#2d6a4f"), (38, "#144e8c"),
    (81, "#8c4314"), (24, "#5f2d8c"), (55, "#0f7f8b"), (70, "#b03a6d"),
    (44, "#3d3d3d"), (89, "#1a2b4a"), (18, "#c9d1c8"), (77, "#6d3b12"),
    (33, "#274c77"), (60, "#5c8a5c"), (48, "#8a5c8a"), (66, "#c9a227"),
    (29, "#40241a"), (84, "#20344f"), (51, "#0e5e4a"), (72, "#7c2c2c"),
    (15, "#d7d7ff"), (58, "#334433"), (87, "#613a61"), (41, "#22517a"),
)

PROBE_PAGE_HTML = (
    "<!DOCTYPE html><html><head><meta charset='utf-8'>"
    "<title>gazette render probe</title></head>"
    "<body style='margin:0;background:#f5f1e6;font-family:monospace'>"
    "<div style='background:#1a2b4a;color:#f5f1e6;font-size:40px;"
    "font-weight:700;padding:26px 20px'>DEAD WEB GAZETTE RENDER PROBE</div>"
    + "".join(
        f"<div style='height:21px'><div style='width:{w}%;height:21px;"
        f"background:{c}'></div></div>"
        for w, c in PROBE_BARS
    )
    + "<p style='font-size:22px;padding:18px 20px;margin:0'>offline probe "
    "page -- zero network references; a valid capture of this page proves "
    "the browser ran the recipe headlessly and composited a frame.</p>"
    "</body></html>"
)

# data: URL form; the browser needs no network to load it.
PROBE_URL = "data:text/html," + quote(PROBE_PAGE_HTML, safe="")

# Payload floor for the probe page, calibrated like MIN_PNG_BYTES: a blank
# 1024x640 render on the reference chromium is 3301 bytes; the probe page
# rendered 10990 bytes there (deterministic across repeated runs). The 6000
# floor sits between them with ~2x margin on both sides, so a blank or
# browser-error capture can never pass the probe while a real capture of
# this deliberately busy page passes comfortably.
PROBE_MIN_PNG_BYTES = 6000


def probe_assess(data: bytes | None, render_report: str) -> tuple[bool, str]:
    """Validate a probe render: PNG magic, exact render-window dimensions, and
    the probe-specific non-blank floor. Returns (ok, reason_or_summary)."""
    if not data:
        return False, render_report
    if sniff_image(data) != ".png":
        return False, f"probe payload is not a png (starts {data[:24]!r})"
    dims = png_dimensions(data)
    want = tuple(int(x) for x in WINDOW_SIZE.split(","))
    if dims != want:
        return False, (f"probe png is {dims[0]}x{dims[1]}, expected "
                       f"{want[0]}x{want[1]} (the render window)")
    if len(data) < PROBE_MIN_PNG_BYTES:
        return False, (f"probe png only {len(data)} bytes (< probe floor "
                       f"{PROBE_MIN_PNG_BYTES}) -- a blank or never-composited "
                       "capture, not the probe page")
    return True, f"probe png {len(data)} bytes, {want[0]}x{want[1]}"


def probe_render(browser: str) -> dict:
    """The first-run check: render the offline probe page through the EXACT
    production path (render_screenshot -> browser_cmd, fresh temp profile and
    all) and assess the payload. Needs no network, so it works on any machine
    in seconds -- if THIS browser cannot run this recipe headlessly, the probe
    says so before a 25-minute subject batch burns itself down. Returns a
    report dict: ok, browser, flags, elapsed_s, bytes, reason, render_report,
    hint."""
    t0 = time.monotonic()
    data, render_report = render_screenshot(browser, PROBE_URL)
    elapsed = time.monotonic() - t0
    ok, reason = probe_assess(data, render_report)
    flags = browser_cmd(browser, Path("<tmp>/shot.png"), Path("<tmp>/profile"),
                        PROBE_URL)
    return {
        "ok": ok,
        "browser": browser,
        "flags": flags,
        "elapsed_s": elapsed,
        "bytes": len(data) if data else 0,
        "reason": reason,
        "render_report": render_report,
        "hint": "" if ok else PROFILE_LOCK_HINT,
    }


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
                    fetch_date: str, browser: str | None = None,
                    cdx_state: dict | None = None,
                    era_year: int | None = None) -> tuple[dict, bool]:
    """Resolve + pre-check + render + store + stamp one subject.

    era_year (from the fact sheet, see era_anchor_year) anchors the
    nearest-capture fallback URL inside the subject's life when CDX yields no
    timestamp; it is ignored whenever CDX resolves one. Returns
    (result_dict_for_the_log, did_network_work). With no browser the subject
    degrades immediately and touches no network at all.
    """
    slug = subject["slug"]
    result = {
        "slug": slug, "canonical_url": None, "stored": None, "timestamp": None,
        "archived_url": None, "bytes": None, "illustration": "generated",
        "capture_mode": None, "era_anchor": era_year, "note": [],
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
        return result, False

    url = canonical_url_for(subject)
    result["canonical_url"] = url
    if not url:
        result["note"].append("no canonical url in seed corpus; degraded to generated")
        _stamp(post_path, result, fetch_date)
        return result, False

    if not browser:
        result["note"].append(
            "skipped: no headless browser binary (see the browser line in this run)")
        _stamp(post_path, result, fetch_date)
        return result, False

    # Snapshot resolution, hardened. A tripped circuit breaker skips the CDX
    # lookup; a CDX miss of any kind (timeout, no status-200 row, open circuit)
    # falls back to the nearest-capture /web/2/ form instead of skipping the
    # render -- Wayback itself redirects to the closest capture it has.
    if cdx_state is not None and cdx_state.get("tripped"):
        ts, cdx_err = None, ("cdx: skipped (circuit open after repeated "
                             "transport failures)")
    else:
        ts, cdx_err = lookup_timestamp(url)
    if ts:
        result["timestamp"] = ts
        result["note"].append(f"cdx {url}: {ts}")
        if cdx_state is not None:
            cdx_state["fails"] = 0
    else:
        fallback = archived_page_url(url, None, era_year)
        if era_year:
            result["note"].append(
                f"cdx miss -> era-anchored nearest-capture fallback {fallback} "
                f"(anchor year {era_year} from the fact sheet's peak/death/"
                "launch facts; wayback resolves to the capture nearest that "
                "year, not to whatever the domain serves today)")
        else:
            result["note"].append(
                f"cdx miss -> nearest-capture fallback {fallback} (no anchor "
                "year in the fact sheet; /web/2/ resolves to the MOST RECENT "
                "capture -- for parked dead domains that is the parked page)")
        if cdx_state is not None and "no status-200" not in cdx_err:
            cdx_state["fails"] = cdx_state.get("fails", 0) + 1
            if cdx_state["fails"] >= CDX_BREAK_AFTER and not cdx_state.get("tripped"):
                cdx_state["tripped"] = True
                result["note"].append(
                    f"cdx: {cdx_state['fails']} consecutive transport failures; "
                    "remaining subjects skip the CDX lookup and render the "
                    "era-anchored nearest-capture form directly")

    target = archived_page_url(url, ts, era_year)
    result["archived_url"] = target

    ok, report, final_url = precheck_archived(target)
    result["note"].append(report)
    if not ok:
        _stamp(post_path, result, fetch_date)
        return result, True

    if not ts:
        recovered = timestamp_from_final_url(final_url)
        if recovered:
            result["timestamp"] = recovered
            result["note"].append(
                f"nearest-capture redirect resolved to {recovered}")
        else:
            result["capture_mode"] = "nearest capture"
            result["note"].append(
                "provenance: nearest capture (no 14-digit timestamp in the "
                "redirect target; the plate label says so)")

    data, report = render_screenshot(browser, target)
    result["note"].append(report)
    bad = validate_png(data)
    if bad:
        result["note"].append(f"rejected: {bad}")
        _stamp(post_path, result, fetch_date)
        return result, True

    shots_dir.mkdir(parents=True, exist_ok=True)
    (shots_dir / f"{slug}.png").write_bytes(data)
    result.update(stored=f"{slug}.png", bytes=len(data), illustration="screenshot")
    _stamp(post_path, result, fetch_date)
    return result, True


def _stamp(post_path: Path, result: dict, fetch_date: str) -> None:
    """Write illustration front matter to match what is actually stored."""
    fields = {"illustration": result["illustration"]}
    if result["illustration"] == "screenshot" and result.get("canonical_url"):
        fields["screenshot_url"] = result["canonical_url"]
        if result.get("archived_url"):
            fields["screenshot_archived_url"] = result["archived_url"]
        if result.get("timestamp"):
            fields["screenshot_timestamp"] = result["timestamp"]
        elif result.get("capture_mode"):
            # Nearest-capture render whose timestamp could not be recovered
            # from the redirect target: the plate label says "nearest capture".
            fields["screenshot_capture_mode"] = result["capture_mode"]
        fields["screenshot_fetched"] = fetch_date
    changed, note = set_front_matter_fields(post_path, fields)
    result["note"].append(f"front matter: {note}")


def result_line(r: dict) -> str:
    parts = [f'{r["slug"]}:']
    if r.get("canonical_url"):
        parts.append(f'url={r["canonical_url"]}')
    if r.get("timestamp"):
        parts.append(f'ts={r["timestamp"]}')
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
