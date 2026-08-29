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

### Run 2026-08-29 23:30:01

- mode: fetch-images (cascade: bing image search -> wikimedia commons -> probe-gated archive render; env toggles GAZETTE_BING / GAZETTE_COMMONS / GAZETTE_RENDER, default on)
- routes enabled: bing=True commons=True render=True
- browser: chromium found at /usr/bin/chromium (PATH probe)
- pre-flight render probe: PASS -- probe png 10990 bytes, 1024x640
- subjects attempted: 20; plates with real images: 20; degraded to generated art: 0
- post bodies byte-identical after front-matter updates (sha256): yes
- aim [skip]: -- STORED aim.webp (18844 bytes) -- already stored (aim.webp, 18844 bytes); fetch skipped (never-clobber)
- altavista [skip]: -- STORED altavista.jpg (41338 bytes) -- already stored (altavista.jpg, 41338 bytes); fetch skipped (never-clobber)
- cuil [skip]: -- STORED cuil.jpg (51016 bytes) -- already stored (cuil.jpg, 51016 bytes); fetch skipped (never-clobber)
- delicious [skip]: -- STORED delicious.jpg (16753 bytes) -- already stored (delicious.jpg, 16753 bytes); fetch skipped (never-clobber)
- digg [skip]: -- STORED digg.png (76255 bytes) -- already stored (digg.png, 76255 bytes); fetch skipped (never-clobber)
- etoys [bing]: -- query "eToys 2001 website screenshot" -- 35 parsed / 12 matched -- STORED etoys.jpg (10823 bytes) -- bing search: 35 parsed, 12 strict matches for query 'eToys 2001 website screenshot' -- murl archive.org: URL error ([Errno 101] Network is unreachable) from archive.org -- stored etoys.jpg via turl ts2.mm.bing.net (10823 bytes, source page archive.org) -- front matter: 5 field(s) applied
- friendster [bing]: -- query "Friendster 2015 website screenshot" -- 27 parsed / 23 matched -- STORED friendster.jpg (39191 bytes) -- bing search: 27 parsed, 23 strict matches for query 'Friendster 2015 website screenshot' -- murl cdn-image.hipwee.com: HTTP 403 from cdn-image.hipwee.com -- stored friendster.jpg via turl ts3.mm.bing.net (39191 bytes, source page www.hipwee.com) -- front matter: 5 field(s) applied
- geocities [bing]: -- query "GeoCities 2009 website screenshot" -- 34 parsed / 23 matched -- STORED geocities.webp (69008 bytes) -- bing search: 34 parsed, 23 strict matches for query 'GeoCities 2009 website screenshot' -- stored geocities.webp via murl glitchback.com (69008 bytes, source page glitchback.com) -- front matter: 5 field(s) applied
- google-plus [bing]: -- query "Google+ 2019 website screenshot" -- 35 parsed / 2 matched -- STORED google-plus.jpg (15744 bytes) -- bing search: 35 parsed, 2 strict matches for query 'Google+ 2019 website screenshot' -- murl woshipm.com: 170754 bytes rejected (image 170754 bytes (> 102400 cap); from this box only candidates up to the cap are stored -- try the next candidate (the thumbnail usually fits)) -- stored google-plus.jpg via turl ts4.mm.bing.net (15744 bytes, source page www.woshipm.com) -- front matter: 5 field(s) applied
- google-reader [bing]: -- query "Google Reader 2013 website screenshot" -- 35 parsed / 10 matched -- STORED google-reader.jpg (96323 bytes) -- bing search: 35 parsed, 10 strict matches for query 'Google Reader 2013 website screenshot' -- stored google-reader.jpg via murl www.weste.net (96323 bytes, source page www.weste.net) -- front matter: 5 field(s) applied
- msn-messenger [bing]: -- query "MSN Messenger 2013 website screenshot" -- 35 parsed / 28 matched -- STORED msn-messenger.jpg (58800 bytes) -- bing search: 35 parsed, 28 strict matches for query 'MSN Messenger 2013 website screenshot' -- stored msn-messenger.jpg via murl image.woshipm.com (58800 bytes, source page www.woshipm.com) -- front matter: 5 field(s) applied
- myspace [bing]: -- query "MySpace 2006 website screenshot" -- 35 parsed / 28 matched -- STORED myspace.jpg (53404 bytes) -- bing search: 35 parsed, 28 strict matches for query 'MySpace 2006 website screenshot' -- murl www.webdesignmuseum.org: HTTP 403 from www.webdesignmuseum.org -- stored myspace.jpg via turl ts2.mm.bing.net (53404 bytes, source page www.webdesignmuseum.org) -- front matter: 5 field(s) applied
- napster [bing]: -- query "Napster 2000 website screenshot" -- 35 parsed / 25 matched -- STORED napster.jpg (31392 bytes) -- bing search: 35 parsed, 25 strict matches for query 'Napster 2000 website screenshot' -- murl www.webdesignmuseum.org: HTTP 403 from www.webdesignmuseum.org -- stored napster.jpg via turl ts4.mm.bing.net (31392 bytes, source page www.webdesignmuseum.org) -- front matter: 5 field(s) applied
- newgrounds [bing]: -- query "Newgrounds 1995 website screenshot" -- 35 parsed / 34 matched -- STORED newgrounds.webp (72320 bytes) -- bing search: 35 parsed, 34 strict matches for query 'Newgrounds 1995 website screenshot' -- stored newgrounds.webp via murl image.gcores.com (72320 bytes, source page www.gcores.com) -- front matter: 5 field(s) applied
- pets-com [bing]: -- query "Pets.com 2000 website screenshot" -- 35 parsed / 4 matched -- STORED pets-com.jpg (17963 bytes) -- bing search: 35 parsed, 4 strict matches for query 'Pets.com 2000 website screenshot' -- murl www.superbowl-ads.com: 497754 bytes rejected (image 497754 bytes (> 102400 cap); from this box only candidates up to the cap are stored -- try the next candidate (the thumbnail usually fits)) -- stored pets-com.jpg via turl ts1.mm.bing.net (17963 bytes, source page www.superbowl-ads.com) -- front matter: 5 field(s) applied
- posterous [bing]: -- query "Posterous 2013 website screenshot" -- 35 parsed / 33 matched -- STORED posterous.png (64842 bytes) -- bing search: 35 parsed, 33 strict matches for query 'Posterous 2013 website screenshot' -- stored posterous.png via murl cdn.brudtkuhl.com (64842 bytes, source page brudtkuhl.com) -- front matter: 5 field(s) applied
- somethingawful [bing]: -- query "Something Awful 1999 website screenshot" -- 34 parsed / 17 matched -- STORED somethingawful.jpg (18999 bytes) -- bing search: 34 parsed, 17 strict matches for query 'Something Awful 1999 website screenshot' -- murl i.somethingawful.com: HTTP 403 from i.somethingawful.com -- stored somethingawful.jpg via turl ts4.mm.bing.net (18999 bytes, source page forums.somethingawful.com) -- front matter: 5 field(s) applied
- stumbleupon [bing]: -- query "StumbleUpon 2018 website screenshot" -- 35 parsed / 32 matched -- STORED stumbleupon.jpg (21102 bytes) -- bing search: 35 parsed, 32 strict matches for query 'StumbleUpon 2018 website screenshot' -- murl www.howtogeek.com: RemoteDisconnected: Remote end closed connection without response from www.howtogeek.com -- stored stumbleupon.jpg via turl ts1.mm.bing.net (21102 bytes, source page wetenschap.net) -- front matter: 5 field(s) applied
- vine [bing]: -- query "Vine 2016 website screenshot" -- 35 parsed / 35 matched -- STORED vine.jpg (21206 bytes) -- bing search: 35 parsed, 35 strict matches for query 'Vine 2016 website screenshot' -- murl vine.co: 497806 bytes rejected (image 497806 bytes (> 102400 cap); from this box only candidates up to the cap are stored -- try the next candidate (the thumbnail usually fits)) -- stored vine.jpg via turl ts4.mm.bing.net (21206 bytes, source page vine.co) -- front matter: 5 field(s) applied
- winamp [bing]: -- query "Winamp 2013 website screenshot" -- 35 parsed / 35 matched -- STORED winamp.jpg (21646 bytes) -- bing search: 35 parsed, 35 strict matches for query 'Winamp 2013 website screenshot' -- murl p5.itc.cn: HTTP 403 from p5.itc.cn -- stored winamp.jpg via turl ts3.mm.bing.net (21646 bytes, source page www.mydigit.cn) -- front matter: 5 field(s) applied
- binary size report (assets/images unless noted):
-   assets/images/aim.webp -- 18844 bytes [via skip]
-   assets/images/altavista.jpg -- 41338 bytes [via skip]
-   assets/images/cuil.jpg -- 51016 bytes [via skip]
-   assets/images/delicious.jpg -- 16753 bytes [via skip]
-   assets/images/digg.png -- 76255 bytes [via skip]
-   assets/images/etoys.jpg -- 10823 bytes [via bing]
-   assets/images/friendster.jpg -- 39191 bytes [via bing]
-   assets/images/geocities.webp -- 69008 bytes [via bing]
-   assets/images/google-plus.jpg -- 15744 bytes [via bing]
-   assets/images/google-reader.jpg -- 96323 bytes [via bing]
-   assets/images/msn-messenger.jpg -- 58800 bytes [via bing]
-   assets/images/myspace.jpg -- 53404 bytes [via bing]
-   assets/images/napster.jpg -- 31392 bytes [via bing]
-   assets/images/newgrounds.webp -- 72320 bytes [via bing]
-   assets/images/pets-com.jpg -- 17963 bytes [via bing]
-   assets/images/posterous.png -- 64842 bytes [via bing]
-   assets/images/somethingawful.jpg -- 18999 bytes [via bing]
-   assets/images/stumbleupon.jpg -- 21102 bytes [via bing]
-   assets/images/vine.jpg -- 21206 bytes [via bing]
-   assets/images/winamp.jpg -- 21646 bytes [via bing]
- site rebuilt: 20 published post(s)

### Run 2026-08-29 23:31:04

- mode: verify -- 475 checks, FAILURES: somethingawful: source page url visible on the plate, about states the illustration policy (screenshots vs generated)
- posts: 20; illustration modes: 0 screenshot, 20 sourced-image, 0 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 33 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 33 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: site/assets/winamp.jpg -- 21646 bytes; site/assets/stumbleupon.jpg -- 21102 bytes; site/assets/etoys.jpg -- 10823 bytes; site/assets/friendster.jpg -- 39191 bytes; site/assets/altavista.jpg -- 41338 bytes; site/assets/somethingawful.jpg -- 18999 bytes; site/assets/geocities.webp -- 69008 bytes; site/assets/google-plus.jpg -- 15744 bytes; site/assets/cuil.jpg -- 51016 bytes; site/assets/vine.jpg -- 21206 bytes; site/assets/newgrounds.webp -- 72320 bytes; site/assets/google-reader.jpg -- 96323 bytes; site/assets/msn-messenger.jpg -- 58800 bytes; site/assets/posterous.png -- 64842 bytes; site/assets/myspace.jpg -- 53404 bytes; site/assets/pets-com.jpg -- 17963 bytes; site/assets/delicious.jpg -- 16753 bytes; site/assets/napster.jpg -- 31392 bytes; site/assets/aim.webp -- 18844 bytes; site/assets/digg.png -- 76255 bytes; assets/images/winamp.jpg -- 21646 bytes; assets/images/stumbleupon.jpg -- 21102 bytes; assets/images/etoys.jpg -- 10823 bytes; assets/images/friendster.jpg -- 39191 bytes; assets/images/altavista.jpg -- 41338 bytes; assets/images/somethingawful.jpg -- 18999 bytes; assets/images/geocities.webp -- 69008 bytes; assets/images/google-plus.jpg -- 15744 bytes; assets/images/cuil.jpg -- 51016 bytes; assets/images/vine.jpg -- 21206 bytes; assets/images/newgrounds.webp -- 72320 bytes; assets/images/google-reader.jpg -- 96323 bytes; assets/images/msn-messenger.jpg -- 58800 bytes; assets/images/posterous.png -- 64842 bytes; assets/images/myspace.jpg -- 53404 bytes; assets/images/pets-com.jpg -- 17963 bytes; assets/images/delicious.jpg -- 16753 bytes; assets/images/napster.jpg -- 31392 bytes; assets/images/aim.webp -- 18844 bytes; assets/images/digg.png -- 76255 bytes
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 23:31:41

- mode: verify -- 475 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 sourced-image, 0 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 33 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 33 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: site/assets/winamp.jpg -- 21646 bytes; site/assets/stumbleupon.jpg -- 21102 bytes; site/assets/etoys.jpg -- 10823 bytes; site/assets/friendster.jpg -- 39191 bytes; site/assets/altavista.jpg -- 41338 bytes; site/assets/somethingawful.jpg -- 18999 bytes; site/assets/geocities.webp -- 69008 bytes; site/assets/google-plus.jpg -- 15744 bytes; site/assets/cuil.jpg -- 51016 bytes; site/assets/vine.jpg -- 21206 bytes; site/assets/newgrounds.webp -- 72320 bytes; site/assets/google-reader.jpg -- 96323 bytes; site/assets/msn-messenger.jpg -- 58800 bytes; site/assets/posterous.png -- 64842 bytes; site/assets/myspace.jpg -- 53404 bytes; site/assets/pets-com.jpg -- 17963 bytes; site/assets/delicious.jpg -- 16753 bytes; site/assets/napster.jpg -- 31392 bytes; site/assets/aim.webp -- 18844 bytes; site/assets/digg.png -- 76255 bytes; assets/images/winamp.jpg -- 21646 bytes; assets/images/stumbleupon.jpg -- 21102 bytes; assets/images/etoys.jpg -- 10823 bytes; assets/images/friendster.jpg -- 39191 bytes; assets/images/altavista.jpg -- 41338 bytes; assets/images/somethingawful.jpg -- 18999 bytes; assets/images/geocities.webp -- 69008 bytes; assets/images/google-plus.jpg -- 15744 bytes; assets/images/cuil.jpg -- 51016 bytes; assets/images/vine.jpg -- 21206 bytes; assets/images/newgrounds.webp -- 72320 bytes; assets/images/google-reader.jpg -- 96323 bytes; assets/images/msn-messenger.jpg -- 58800 bytes; assets/images/posterous.png -- 64842 bytes; assets/images/myspace.jpg -- 53404 bytes; assets/images/pets-com.jpg -- 17963 bytes; assets/images/delicious.jpg -- 16753 bytes; assets/images/napster.jpg -- 31392 bytes; assets/images/aim.webp -- 18844 bytes; assets/images/digg.png -- 76255 bytes
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 23:31:53

- mode: verify -- 475 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 sourced-image, 0 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 33 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 33 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: site/assets/winamp.jpg -- 21646 bytes; site/assets/stumbleupon.jpg -- 21102 bytes; site/assets/etoys.jpg -- 10823 bytes; site/assets/friendster.jpg -- 39191 bytes; site/assets/altavista.jpg -- 41338 bytes; site/assets/somethingawful.jpg -- 18999 bytes; site/assets/geocities.webp -- 69008 bytes; site/assets/google-plus.jpg -- 15744 bytes; site/assets/cuil.jpg -- 51016 bytes; site/assets/vine.jpg -- 21206 bytes; site/assets/newgrounds.webp -- 72320 bytes; site/assets/google-reader.jpg -- 96323 bytes; site/assets/msn-messenger.jpg -- 58800 bytes; site/assets/posterous.png -- 64842 bytes; site/assets/myspace.jpg -- 53404 bytes; site/assets/pets-com.jpg -- 17963 bytes; site/assets/delicious.jpg -- 16753 bytes; site/assets/napster.jpg -- 31392 bytes; site/assets/aim.webp -- 18844 bytes; site/assets/digg.png -- 76255 bytes; assets/images/winamp.jpg -- 21646 bytes; assets/images/stumbleupon.jpg -- 21102 bytes; assets/images/etoys.jpg -- 10823 bytes; assets/images/friendster.jpg -- 39191 bytes; assets/images/altavista.jpg -- 41338 bytes; assets/images/somethingawful.jpg -- 18999 bytes; assets/images/geocities.webp -- 69008 bytes; assets/images/google-plus.jpg -- 15744 bytes; assets/images/cuil.jpg -- 51016 bytes; assets/images/vine.jpg -- 21206 bytes; assets/images/newgrounds.webp -- 72320 bytes; assets/images/google-reader.jpg -- 96323 bytes; assets/images/msn-messenger.jpg -- 58800 bytes; assets/images/posterous.png -- 64842 bytes; assets/images/myspace.jpg -- 53404 bytes; assets/images/pets-com.jpg -- 17963 bytes; assets/images/delicious.jpg -- 16753 bytes; assets/images/napster.jpg -- 31392 bytes; assets/images/aim.webp -- 18844 bytes; assets/images/digg.png -- 76255 bytes
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures


### Run 2026-08-29 23:33:52

- mode: fetch-images per-subject outcome table (2026-08-29, live Route 1 run
-   from the build box; all 20 subjects stored a real, strict-matched image
-   via Bing image search; every binary under the 100KB cap)
- columns: subject | query (era year from the fact-sheet anchor) | candidates
-   parsed/strict-matched | stored binary | bytes | source page host | fetch
-   path (murl = original host, turl = bing thumbnail fallback)

- | aim | AOL Instant Messenger 2017 website screenshot | 35/26 | aim.webp | 18844 | www.smithsonianmag.com | murl |
- | altavista | AltaVista 2013 website screenshot | 35/4 | altavista.jpg | 41338 | www.neoteo.com | turl |
- | cuil | Cuil 2010 website screenshot | 35/31 | cuil.jpg | 51016 | guy.pastre.org | turl |
- | delicious | del.icio.us 2010 website screenshot | 31/27 | delicious.jpg | 16753 | www.techtudo.com.br | murl |
- | digg | Digg 2004 website screenshot | 35/29 | digg.png | 76255 | rip.so | murl |
- | etoys | eToys 2001 website screenshot | 35/12 | etoys.jpg | 10823 | archive.org | turl |
- | friendster | Friendster 2015 website screenshot | 27/23 | friendster.jpg | 39191 | www.hipwee.com | turl |
- | geocities | GeoCities 2009 website screenshot | 34/23 | geocities.webp | 69008 | glitchback.com | murl |
- | google-plus | Google+ 2019 website screenshot | 35/2 | google-plus.jpg | 15744 | www.woshipm.com | turl |
- | google-reader | Google Reader 2013 website screenshot | 35/10 | google-reader.jpg | 96323 | www.weste.net | murl |
- | msn-messenger | MSN Messenger 2013 website screenshot | 35/28 | msn-messenger.jpg | 58800 | www.woshipm.com | murl |
- | myspace | MySpace 2006 website screenshot | 35/28 | myspace.jpg | 53404 | www.webdesignmuseum.org | turl |
- | napster | Napster 2000 website screenshot | 35/25 | napster.jpg | 31392 | www.webdesignmuseum.org | turl |
- | newgrounds | Newgrounds 1995 website screenshot | 35/34 | newgrounds.webp | 72320 | www.gcores.com | murl |
- | pets-com | Pets.com 2000 website screenshot | 35/4 | pets-com.jpg | 17963 | www.superbowl-ads.com | turl |
- | posterous | Posterous 2013 website screenshot | 35/33 | posterous.png | 64842 | brudtkuhl.com | murl |
- | somethingawful | Something Awful 1999 website screenshot | 34/17 | somethingawful.jpg | 18999 | forums.somethingawful.com | turl |
- | stumbleupon | StumbleUpon 2018 website screenshot | 35/32 | stumbleupon.jpg | 21102 | wetenschap.net | turl |
- | vine | Vine 2016 website screenshot | 35/35 | vine.jpg | 21206 | vine.co | turl |
- | winamp | Winamp 2013 website screenshot | 35/35 | winamp.jpg | 21646 | www.mydigit.cn | turl |

- total binary weight: 816969 bytes across 20 files (largest google-reader.jpg
- 96323 bytes, smallest etoys.jpg 10823 bytes); nothing over the 100KB cap, so
- nothing needs the individual over-cap flag
- rejections that shaped the run (all logged per subject in the entries above):
- hotlink 403s from i.somethingawful.com and p5.itc.cn; over-cap originals for
- cuil (306972 bytes) and vine (497806 bytes) rejected in favor of thumbnails;
- a 404 from www.neoteo.com and a RemoteDisconnected from www.howtogeek.com,
- both carried by the turl fallback; one candidate URL with raw spaces (etoys,
- a youtube-thumbnail path) crashed the first run before the fix -- URLs are
- now percent-encoded before the request and ASCII-validated before storage
- commons route: never reached -- bing stored 20/20 (wikimedia egress is
- SSL-handshake-blocked from this box; recorded earlier this run)
- render route: pre-flight probe passed but was never needed (bing 20/20)
### Run 2026-08-29 23:35:48

- mode: verify -- 475 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 sourced-image, 0 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 33 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 33 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: site/assets/winamp.jpg -- 21646 bytes; site/assets/stumbleupon.jpg -- 21102 bytes; site/assets/etoys.jpg -- 10823 bytes; site/assets/friendster.jpg -- 39191 bytes; site/assets/altavista.jpg -- 41338 bytes; site/assets/somethingawful.jpg -- 18999 bytes; site/assets/geocities.webp -- 69008 bytes; site/assets/google-plus.jpg -- 15744 bytes; site/assets/cuil.jpg -- 51016 bytes; site/assets/vine.jpg -- 21206 bytes; site/assets/newgrounds.webp -- 72320 bytes; site/assets/google-reader.jpg -- 96323 bytes; site/assets/msn-messenger.jpg -- 58800 bytes; site/assets/posterous.png -- 64842 bytes; site/assets/myspace.jpg -- 53404 bytes; site/assets/pets-com.jpg -- 17963 bytes; site/assets/delicious.jpg -- 16753 bytes; site/assets/napster.jpg -- 31392 bytes; site/assets/aim.webp -- 18844 bytes; site/assets/digg.png -- 76255 bytes; assets/images/winamp.jpg -- 21646 bytes; assets/images/stumbleupon.jpg -- 21102 bytes; assets/images/etoys.jpg -- 10823 bytes; assets/images/friendster.jpg -- 39191 bytes; assets/images/altavista.jpg -- 41338 bytes; assets/images/somethingawful.jpg -- 18999 bytes; assets/images/geocities.webp -- 69008 bytes; assets/images/google-plus.jpg -- 15744 bytes; assets/images/cuil.jpg -- 51016 bytes; assets/images/vine.jpg -- 21206 bytes; assets/images/newgrounds.webp -- 72320 bytes; assets/images/google-reader.jpg -- 96323 bytes; assets/images/msn-messenger.jpg -- 58800 bytes; assets/images/posterous.png -- 64842 bytes; assets/images/myspace.jpg -- 53404 bytes; assets/images/pets-com.jpg -- 17963 bytes; assets/images/delicious.jpg -- 16753 bytes; assets/images/napster.jpg -- 31392 bytes; assets/images/aim.webp -- 18844 bytes; assets/images/digg.png -- 76255 bytes
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 23:35:49

- mode: verify -- 475 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 sourced-image, 0 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 33 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 33 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: site/assets/winamp.jpg -- 21646 bytes; site/assets/stumbleupon.jpg -- 21102 bytes; site/assets/etoys.jpg -- 10823 bytes; site/assets/friendster.jpg -- 39191 bytes; site/assets/altavista.jpg -- 41338 bytes; site/assets/somethingawful.jpg -- 18999 bytes; site/assets/geocities.webp -- 69008 bytes; site/assets/google-plus.jpg -- 15744 bytes; site/assets/cuil.jpg -- 51016 bytes; site/assets/vine.jpg -- 21206 bytes; site/assets/newgrounds.webp -- 72320 bytes; site/assets/google-reader.jpg -- 96323 bytes; site/assets/msn-messenger.jpg -- 58800 bytes; site/assets/posterous.png -- 64842 bytes; site/assets/myspace.jpg -- 53404 bytes; site/assets/pets-com.jpg -- 17963 bytes; site/assets/delicious.jpg -- 16753 bytes; site/assets/napster.jpg -- 31392 bytes; site/assets/aim.webp -- 18844 bytes; site/assets/digg.png -- 76255 bytes; assets/images/winamp.jpg -- 21646 bytes; assets/images/stumbleupon.jpg -- 21102 bytes; assets/images/etoys.jpg -- 10823 bytes; assets/images/friendster.jpg -- 39191 bytes; assets/images/altavista.jpg -- 41338 bytes; assets/images/somethingawful.jpg -- 18999 bytes; assets/images/geocities.webp -- 69008 bytes; assets/images/google-plus.jpg -- 15744 bytes; assets/images/cuil.jpg -- 51016 bytes; assets/images/vine.jpg -- 21206 bytes; assets/images/newgrounds.webp -- 72320 bytes; assets/images/google-reader.jpg -- 96323 bytes; assets/images/msn-messenger.jpg -- 58800 bytes; assets/images/posterous.png -- 64842 bytes; assets/images/myspace.jpg -- 53404 bytes; assets/images/pets-com.jpg -- 17963 bytes; assets/images/delicious.jpg -- 16753 bytes; assets/images/napster.jpg -- 31392 bytes; assets/images/aim.webp -- 18844 bytes; assets/images/digg.png -- 76255 bytes
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

