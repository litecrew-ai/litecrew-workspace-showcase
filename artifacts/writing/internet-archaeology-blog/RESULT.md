# Run log

One entry per pipeline invocation. Modes and verification results
are recorded honestly, including failures and degradations.

## Rotation policy

This file is the ACTIVE run log. Older history (2026-08-29, v0 through
the blog-render-timeout-fix Task) lives verbatim in
docs/result-log/archive-1.md -- moved when this file reached 99.6KB of
the 100KB text gate; nothing was deleted. When this file again exceeds
~60KB, move all but the newest verification-methods section and the last
~10 run entries into the next docs/result-log/archive-<N>.md; run.py
prints a rotation note once the threshold is passed. Every file stays
under the 100KB publication gate.

## Current verification methods

- `python3 run.py --verify` re-derives artwork, re-parses every built
  HTML file with a tag-stack checker, resolves every internal link,
  asserts index/categories arrangement, provenance and source rendering,
  checks RSS as XML, copies the stylesheet byte-identically, rebuilds the
  whole site into a scratch dir and byte-compares it to the tracked
  build, serves the site over loopback HTTP at a subpath and fetches
  every internal reference a browser would (both ref modes), and walks
  the glyph/size/binary publication gates over the artifact tree.
- `python3 run.py --probe-render` (new, 2026-08-29) renders an offline
  data: page through the exact production browser invocation (fresh
  temp profile included) and validates the PNG: magic, 1024x640 window,
  calibrated non-blank floor. First-run check on any new machine;
  --fetch-screenshots runs it fail-fast before the first subject.
- `python3 -m unittest discover -s tests` runs the offline suite (55
  tests at this rotation): URL construction and era anchoring, render
  flag contract, stderr filtering, fresh-profile-per-render lifecycle
  (recorder browser), probe assessment, payload guards, browser
  detection, front-matter editor, condensation, scratch-build
  consistency, plus real-browser loopback renders (including the
  stalled-subresource regression and the probe) when a browser exists.
- Screenshot runs hash post bodies (sha256) before/after: only
  front-matter fields may change.

## Recent entries

### Run 2026-08-29 18:47:00

- mode: verify -- 392 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 19:33:57

- mode: fetch-screenshots (render strategy: resolve via CDX, then screenshot https://web.archive.org/web/<ts>/<url> with a headless browser; the former /screenshot/ endpoint returned 404 html for every subject in the operator run of 2026-08-29 and is no longer called)
- browser: chromium found at /usr/bin/chromium (PATH probe)
- subjects attempted: 20; screenshots stored: 0; degraded to generated art: 20
- post bodies byte-identical after front-matter updates (sha256): yes
- RESULT.md near the size gate (89.8KB of 100KB); per-subject lines kept on stdout only; condensed outcomes:
-   cdx http: 20 subject(s) [aim, altavista, cuil, delicious, digg, etoys, friendster, geocities, google-plus, google-reader, msn-messenger, myspace, napster, newgrounds, pets-com, posterous, somethingawful, stumbleupon, vine, winamp]
- no binaries stored this run (nothing to size-report)
- site rebuilt: 20 published post(s)

### Run 2026-08-29 19:36:08

- mode: fetch-screenshots (render strategy: resolve via CDX, then screenshot https://web.archive.org/web/<ts>/<url> with a headless browser; the former /screenshot/ endpoint returned 404 html for every subject in the operator run of 2026-08-29 and is no longer called)
- browser: none found -- set CHROME_BIN=/path/to/a/chrome-or-chromium binary, or install Google Chrome / Chromium / Microsoft Edge, then re-run python3 run.py --fetch-screenshots
- subjects attempted: 20; screenshots stored: 0; degraded to generated art: 20
- post bodies byte-identical after front-matter updates (sha256): yes
- skipped (no browser binary): aim, altavista, cuil, delicious, digg, etoys, friendster, geocities, google-plus, google-reader, msn-messenger, myspace, napster, newgrounds, pets-com, posterous, somethingawful, stumbleupon, vine, winamp
- no binaries stored this run (nothing to size-report)
- site rebuilt: 20 published post(s)

### Run 2026-08-29 19:36:26

- mode: task diagnosis record (blog-screenshot-renderer) -- why the fetch strategy changed
- operator laptop run 2026-08-29 (network WITH archive egress), on the record: the
-   https://web.archive.org/screenshot/<url> endpoint returned HTTP 404 with an html
-   error page for all 20 subjects (plus one 503 challenge page for somethingawful)
-   -- the service is dead; the dependency is removed and the endpoint is kept only
-   as a tombstone constant in pipeline/screenshots.py
- same run, CDX: answered inside 5s for 5 of 20 subjects (delicious 20031004064641,
-   etoys 20010130072000, google-plus 20120215235515, msn-messenger 19991012062956,
-   winamp 19981205015145) and timed out for the other 15 -> CDX client hardened:
-   25s timeout, one retry, 200-status preference kept, circuit breaker after 4
-   consecutive transport failures, ~2s inter-subject delay
- new strategy: render, do not fetch -- screenshot
-   https://web.archive.org/web/<ts>/<original-url> with a headless browser located
-   via CHROME_BIN / PATH probe / macOS bundles (subprocess, stdlib only)
- payload-guard calibration on this box chromium (1024x640 headless): blank page
-   3301 bytes; browser error page (closed loopback port) 21768 bytes; real content
-   page (gazette index served on loopback) 67398 bytes -> near-blank floor 24576
- hang behavior measured: an unroutable host makes the browser never exit and write
-   no file (killed at 100s in the probe) -> the render owns a 45s wall clock and
-   kills the process group; a fast-failing target writes a genuine png of the
-   browser error page, which is why the floor + dimension + pre-check guards exist

### Run 2026-08-29 19:36:27

- mode: verify -- 393 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 19:36:38

- mode: verify -- 393 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 19:36:40

- mode: verify -- 393 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 19:37:34

- mode: offline unit tests (blog-screenshot-renderer) -- 24 tests, OK
- python3 -m unittest discover -s tests: url construction, cdx params, payload
-   guards (magic/dimensions/floor), browser detection (PATH probe, CHROME_BIN
-   override + broken-override), additive+idempotent front matter, no-browser
-   degradation, never-clobber, RESULT-condensation grouping, scratch-build
-   consistency with a synthetic png, and two real local renders with this
-   box chromium (gazette index over loopback -> valid 1024x640 png above the
-   floor; closed loopback port -> browser error page rejected by the guards)

### Run 2026-08-29 20:56:33

- mode: verify -- 393 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 20:57:00

- mode: fix (blog-render-timeout-fix) -- render-stage repair after the second
-   laptop run (17/20 cdx timestamps resolved, real archived html pre-checked
-   for 15 subjects, every render dead: 45s wall kill, no file written)
- render now carries chrome's own --timeout=30000 (vtb 10000, wall guard 75s,
-   stderr tail in every failure line). Proven on this box's chromium 150 with
-   a loopback stalled-subresource page: the vtb-only recipe never exits and
-   writes no file (the operator's failure, reproduced); with --timeout the
-   browser self-captures at ~timeout+1s and always writes a png (unroutable
-   hosts too). Caveat, on the record: the timeout capture of a never-loading
-   page is a blank 3301B frame on this chromium, the 24576B floor rejects
-   it -- such subjects still degrade, now with chrome's 'Page load timed
-   out' stderr line in the log instead of a silent kill
- pre-check: http 503 -> 15s backoff + exactly one retry; inter-subject delay
-   2s -> 4s (one laptop run drew five 503 challenge pages)
- cdx misses (timeout, no status-200 row, open breaker) now render the
-   nearest-capture form https://web.archive.org/web/2/<url>; timestamp
-   recovered from the redirect target when possible, else the plate is
-   labeled 'nearest capture' (additive screenshot_capture_mode field)
- regression test added: 36 unit tests OK, incl. the stalled-page case; a
-   scratch-tree with-browser rehearsal here (archive unreachable) degraded
-   20/20 honestly with the breaker + fallback path exercised, bodies
-   sha256-identical, exit 0; verify 393 checks ALL PASS. The real
-   archived-page path remains laptop-only (web.archive.org unreachable here)

### Run 2026-08-29 22:14:40

- mode: probe-render -- PASS
- browser: browser: chromium found at /usr/bin/chromium (PATH probe)
- result: probe png 10990 bytes, 1024x640; elapsed 0.9s

### Run 2026-08-29 22:16:59

- mode: verify -- 393 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 22:17:05

- mode: verify -- 393 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 22:17:21

- mode: fix (blog-render-profile-fix) -- environment-divergence hardening: isolated profile, self-probe, era-anchored fallback, RESULT rotation
- diagnosis verification, on the record: the tracked browser_cmd() ALREADY passed a fresh temp --user-data-dir per render (plus --no-first-run/--no-default-browser-check), and the operator's third-run signature 'wall guard killed the process group after 75s' exists only in this code -- so the laptop hung WITH the temp profile in the invocation and the default-profile-lock theory is NOT confirmed; the hang could not be reproduced on this box (no running GUI Chrome)
- invocation: added --disable-crash-reporter --disable-component-update --disable-background-networking; failure reports now carry chrome's stderr with chrome/updater noise lines filtered and BOTH head ~400 + tail ~500 chars kept; an all-noise stderr with no file prints the explicit profile-lock/probe hint
- self-probe: run.py --probe-render renders an offline data: page through the exact production path and validates magic/dimensions/non-blank (floor 6000; blank 3301 < floor < measured 10990 on this chromium); --fetch-screenshots runs it fail-fast before the first subject; documented as the first-run check
- era-anchored fallback: CDX misses now use /web/<YYYY>/<url> with YYYY from the fact sheet (peak phrasing > death > launch; first matching fact's first year); /web/2/ only when no year; all 20 tracked sheets anchor inside the subject's life (e.g. altavista 2013, myspace 2006, napster 2000, newgrounds 1995); provenance still prints the RESOLVED timestamp
- RESULT.md rotation: 2026-08-29 history moved verbatim to docs/result-log/archive-1.md (this file was at 99.6KB of the 100KB gate); rotation policy documented in both files and in run.py (~60KB threshold warning)
- local verification: 55 unit tests OK in ~49s (was 36; new: flag contract with suppression flags, stderr filter/hint, fresh-temp-profile lifecycle via a recorder browser, probe matrix + real-chromium probe, era-anchor order incl. founder-death exclusion, era URL construction); tracked --probe-render PASS (10990 bytes, ~1s); scratch-tree fetch rehearsal (real chromium, archive unreachable): pre-flight probe PASS, 20/20 degraded honestly with era-anchored fallback URLs, circuit breaker tripped after 4 transport failures, post bodies sha256-identical, exit 0; --verify 393 checks ALL PASS
- laptop-only (do not claim otherwise): that the operator's Chrome passes the probe and renders real Wayback pages; that /web/<YYYY>/ resolves era-correctly on the live archive; pixel-level appearance of any real archived page (standing gap). Next operator step: python3 run.py --probe-render (seconds), then the full --fetch-screenshots block in the README

### Run 2026-08-29 22:19:59

- mode: verify -- 393 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

