---
status: done
goal: operate-internet-archaeology-blog.md
assigned_agent: web-product-engineer
created: 2026-08-29
updated: 2026-08-29
---

# Task: Real screenshots via headless-browser rendering of archived pages

## Description

The operator ran `run.py --fetch-screenshots` from a machine WITH archive.org egress
(their laptop). Outcome: 0 images, 20 degraded. Their run output, on the record:

- The Wayback screenshot endpoint returned **HTTP 404 with an HTML error page for
  every subject** (and one 503 challenge page for somethingawful). The assumption
  that `https://web.archive.org/screenshot/<url>` serves images is wrong — that
  service is dead as assumed. This is a real bug in our fetcher's design, now proven
  by evidence from a reachable network.
- The CDX lookup **succeeded within 5s for 5 subjects** (delicious 20031004064641,
  etoys 20010130072000, google-plus 20120215235515, msn-messenger 19991012062956,
  winamp 19981205015145) and **timed out for the other 15** — the 5s timeout is too
  aggressive for CDX, which is routinely slow under load for large domains.

Correct strategy, implemented in this Task:

1. **CDX first (fixed)**: raise the CDX timeout to ~25s with one retry; prefer a
   200-status snapshot; keep per-subject outcome logging. A polite inter-subject
   delay (~2s) to avoid the 503 rate-limit class.
2. **Render, don't fetch**: build the archived page URL
   `https://web.archive.org/web/<ts>/<original-url>` and screenshot it with a
   headless browser via `subprocess` — no Python packages:
   - Locate a browser binary: `$CHROME_BIN` env override, else probe common names
     (`google-chrome`, `google-chrome-stable`, `chromium`, `chromium-browser`,
     `msedge`, `chrome` — plus macOS app-bundle paths).
   - Invoke headless screenshot mode (e.g. `--headless=new --screenshot=<out>
     --window-size=1024,640 --virtual-time-budget=15000 --hide-scrollbars
     --disable-gpu <url>`); capture PNG to a temp path, then move into
     `assets/screenshots/<slug>.png` with the existing provenance machinery
     (front matter: snapshot timestamp, archived URL, fetch date).
   - Wayback pages are slow; allow the process ~45s wall time; treat a 0-byte or
     HTML-content output as failure with the reason logged.
   - If no browser binary is found: degrade per subject with ONE clear, actionable
     message (set CHROME_BIN or install Chrome/Chromium), not 20 repetitions.
3. **This box cannot end-to-end test the real path** (no archive egress, no browser
   binary). Therefore: (a) unit-test what is testable here — URL construction,
   browser-binary detection (expect the clean not-found degradation here), PNG
   magic-byte validation, front-matter/binary/label consistency using a synthetic
   PNG in a scratch build as before; (b) verify the existing 392-check suite stays
   green; (c) write the exact operator commands in the README so the laptop run is
   one copy-paste block.
4. **CI sample**: extend the workflow sample in `docs/scheduling.md` with the
   screenshot step (ubuntu-latest runners ship `google-chrome` preinstalled; export
   CHROME_BIN accordingly) so the automated path also produces real screenshots.
5. Docs: README (CHROME_BIN, expectations, laptop one-liner), design.md if the
   plate component changes at all (it should not — same plate, real image),
   RESULT.md records this Task's diagnosis (dead endpoint, CDX timings) and runs.

## Completion criteria

- [x] Screenshot endpoint dependency removed; fetcher renders archived pages via a
      headless browser located through CHROME_BIN / common-binary probing; the
      subprocess invocation and its flags are documented in the README.
      (`pipeline/screenshots.py` rewritten: no call to `/screenshot/` anywhere, a
      tombstone constant documents why; `find_browser()` resolves CHROME_BIN ->
      PATH probe -> macOS bundles; `render_screenshot()` runs the exact documented
      flag set with a 45s process-group timeout; README "Producing real screenshot
      plates" carries the invocation and flags; verify gained a check that built
      pages never reference the dead endpoint.)
- [x] CDX client hardened (>= 25s timeout, retry, 200-status preference, inter-
      subject delay); per-subject outcome logging preserved.
      (CDX_TIMEOUT=25.0, CDX_RETRIES=1, statuscode:200 filter and earliest-first
      limit kept, CDX_BREAK_AFTER=4 circuit breaker, INTER_SUBJECT_DELAY=2.0;
      per-subject lines printed always, logged per subject while RESULT.md has
      room, grouped by outcome class when it nears the gate. Exercised for real:
      the with-browser rehearsal logged 4 retried transport failures, the breaker
      tripping, then per-subject pre-check failures.)
- [x] No-browser-found path degrades once, clearly, with the actionable message;
      verified here (this box has no browser binary).
      (Correction to the Task's premise: this box DOES ship `/usr/bin/chromium`.
      The no-browser path was still verified for real by hiding it: run with
      `PATH=/nonexistent` -> one actionable message ("set CHROME_BIN=... or
      install..."), zero network calls, one condensed RESULT line instead of 20
      repetitions, all bodies unchanged, exit 0.)
- [x] PNG handling: magic-byte validation on ingest; front matter updated only
      additively; post bodies remain byte-identical; verifier gains (or keeps)
      binary/front-matter/label consistency checks and stays ALL CHECKS PASS
      overall (target: full suite green on this box in degraded mode).
      (validate_png layers magic bytes + exact 1024x640 dimensions + a calibrated
      near-blank floor behind an HTTP-200-and-playback pre-check; additive fields
      only, plus a new `screenshot_archived_url` provenance field; bodies
      sha256-identical across both tracked-tree fetch runs; full suite 393 checks
      ALL PASS.)
- [x] README carries the exact laptop command block (fetch + rebuild + verify) and
      CHROME_BIN documentation; docs/scheduling.md CI sample includes the
      screenshot step with the runner's Chrome.
      (README block: cd + export CHROME_BIN via command -v chain + fetch +
      rebuild + verify, with macOS and unit-test notes; CI sample sets
      `CHROME_BIN: /usr/bin/google-chrome` on ubuntu-latest and adds the offline
      unit-test step; cron note updated with the browser requirement and the
      ~25-45 min budget.)
- [x] RESULT.md records the dead-endpoint diagnosis and this Task's runs honestly;
      knowledge merged (update the screenshots/pipeline sections in
      `knowledge/writing/post-generation-pipeline.md` and the endpoint note in
      `dead-web-source-catalog.md`) with INDEX in sync.
      (Diagnosis entry with the operator's 404/503 evidence and the five CDX
      timings; run entries for the with-browser rehearsal, the no-browser run,
      three verify records, and the unit-test record; RESULT.md at 99.2KB of the
      100KB gate -- near full, see limitations. Knowledge: truthful-images section
      rewritten for render-don't-fetch + change-history rows in both notes; INDEX
      purpose lines updated.)
- [x] Usual rules: English; ASCII text; no emoji; no check-mark glyphs (U+2713,
      U+2714, U+2705, U+2611 family); no text file over 100KB; stdlib only (the
      browser is an external binary invoked via subprocess, not a dependency
      install); no git; no network beyond the established keyless endpoints.
      (Full-suite glyph/size gates green plus a targeted audit after the last doc
      edit: CLEAN; browser is an external binary, no packages installed, nothing
      downloaded; zero git commands; network touched only web.archive.org keyless
      endpoints (all failed at the connection layer here) and 127.0.0.1 loopback.)

## Context and constraints

- **Write boundaries**: this Task file; `artifacts/writing/internet-archaeology-blog/`;
  `knowledge/writing/`. Nothing else. No git commands; no `.github/` changes.
- **Truthfulness law, unchanged**: `illustration: screenshot` only for bytes that a
  real browser rendered from the subject's real archived page, with timestamp and
  URL recorded. Everything else stays `generated` and labeled.
- **Coordinate with the operator's clone**: their laptop run appended RESULT.md
  entries in their local clone; our commits may diverge from it. Note the
  coordination line in the README (pull before re-running; local run artifacts may
  need discarding). Do not attempt to reconcile their clone from here.
- Fastest context load: `pipeline/screenshots.py`, `run.py` (fetch-screenshots mode),
  the prior Task record `archive/tasks/blog-screenshots-and-paths.md`,
  `docs/scheduling.md`, artifact README.

## Preparation (retrieval summary, 2026-08-29)

- Handbooks: none exist (`handbooks/README.md` only; `development.md` still
  backlog). Standing knowledge loaded: `knowledge/writing/post-generation-pipeline.md`
  (truthful-images section, verifier patterns, RESULT.md condensation rule),
  `dead-web-source-catalog.md` (endpoint reachability record), INDEX in sync.
- Artifact context loaded: `pipeline/screenshots.py`, `run.py`
  (fetch-screenshots + verify modes), `pipeline/site.py` (art_for, plate
  caption, provenance), `pipeline/util.py`, README, `docs/scheduling.md`,
  prior Task record `archive/tasks/blog-screenshots-and-paths.md`, RESULT.md
  tail (392 checks ALL PASS; file at 91.9KB of the 100KB gate -- ~10KB
  headroom, entries must stay condensed).
- Environment recon (this box, on the record):
  - **A browser binary EXISTS here**: `/usr/bin/chromium` (the Task text
    assumed none). The no-browser degradation path is still verifiable by
    hiding it from PATH / pointing CHROME_BIN at a nonexistent path, recorded
    as such. The real subprocess machinery is additionally verifiable locally
    against loopback only.
  - Chromium headless works: `--headless=new --screenshot --window-size=
    1024,640 --virtual-time-budget=15000 --hide-scrollbars --disable-gpu
    --no-first-run --no-default-browser-check --user-data-dir=<tmp>` rendered
    `about:blank` (3301-byte PNG) and the gazette index over loopback
    (67398-byte PNG), both exactly 1024x640, PNG magic ok.
  - **Hang behavior**: with an unroutable host (192.0.2.1) and with an
    NXDOMAIN host, chromium NEVER exits and writes NO file (killed at 100s).
    So on hanging networks the render must be bounded by our own subprocess
    timeout; no error-page PNG is produced in that case. On fast-fail
    networks chrome would write its error page as a real PNG -- that case
    needs a non-payload guard (size floor + dimensions + HTTP pre-check).
  - web.archive.org from this box: connections hang until timeout (CDX probe
    consumed its full 25s). The real archived-page path stays unverifiable
    here, as the Task anticipated.

## Execution steps

<!-- Subagent fills -->

1. Rewrite `pipeline/screenshots.py`: remove the dead `/screenshot/` endpoint
   dependency; hardened CDX (25s, one retry, 200-preference, circuit breaker);
   `archived_page_url()` builder; `find_browser()` (CHROME_BIN, PATH names,
   macOS bundles); `render_screenshot()` subprocess (flag set proven locally,
   process-group kill on timeout); layered payload guards (HTTP 200 pre-check,
   PNG magic, dimensions, near-blank size floor).
2. `run.py`: fetch_screenshots resolves the browser ONCE (no-browser = one
   actionable message, no network at all); inter-subject ~2s delay; per-subject
   logging preserved; verify gains the archived-URL provenance check.
3. `pipeline/site.py`: provenance box gains a "Rendered from" row for the
   archived page URL (screenshot mode only; tracked output unchanged since all
   20 posts are generated-mode).
4. Add `tests/test_screenshots.py` (stdlib unittest): URL construction,
   binary detection, browser detection incl. restricted-PATH degradation,
   front-matter idempotence, scratch-build consistency with a synthetic PNG,
   and a real local-chromium render of a loopback page (skipUnless a browser
   exists) into a scratch tree only.
5. Runs: no-browser fetch (PATH hidden) on the tracked tree; unit tests;
   full `--verify` ALL CHECKS PASS; RESULT.md records the dead-endpoint
   diagnosis, the calibration data, and each run honestly.
6. Docs: README (CHROME_BIN, exact laptop command block, coordination note,
   expectations), `docs/scheduling.md` (CI step with the runner's Chrome),
   RESULT.md; knowledge merges (pipeline + source-catalog) with INDEX in sync.

## Execution log

<!-- Append after each subagent iteration -->

| Round | Date       | Progress | Notes |
| ----- | ---------- | -------- | ----- |
| 1 | 2026-08-29 | Retrieval + environment recon + plan recorded | chromium exists on this box (Task assumed none); hang-case renders write no file; blank=3301B vs real content=67398B calibrated; RESULT.md headroom ~10KB |
| 2 | 2026-08-29 | `pipeline/screenshots.py` rewritten to render-don't-fetch: dead endpoint removed (tombstone constant), hardened CDX (25s + retry + breaker + 2s delay), `archived_page_url`, `find_browser` (CHROME_BIN / PATH / macOS bundles), `render_screenshot` (documented flags, own session, process-group kill at 45s), layered payload guards (HTTP 200 + playback-body pre-check, magic bytes, exact dimensions, calibrated 24576B floor) | run.py: browser resolved once, one-message no-browser degradation with zero network, RESULT auto-condensation near the size gate; site.py: "Rendered from" provenance row; verify: archived-url provenance checks + dead-endpoint regression guard (393 checks) |
| 3 | 2026-08-29 | `tests/test_screenshots.py` added; 24 tests OK | offline: url/cdx construction, payload guards, browser detection (restricted PATH, CHROME_BIN override, broken override), additive+idempotent front matter, no-browser degradation, never-clobber, condensation grouping, scratch-build consistency; real: two local chromium renders over loopback (content page -> valid 1024x640 PNG above the floor; closed port -> browser error page rejected by the guards); no test touches the tracked tree |
| 4 | 2026-08-29 | Tracked-tree runs, both recorded in RESULT.md: (a) with-browser full rehearsal -- chromium found via PATH probe, CDX failed fast (Errno 101) with the retry and circuit breaker behaving exactly as designed, per-subject pre-checks failed, 0 stored, 20 degraded, bodies sha256-identical; (b) no-browser run with PATH hidden -- one actionable message, zero network, one condensed RESULT line | both honest degradations; RESULT.md auto-condensed during (a); posts proven unchanged by independent sha256 of all 20 bodies after every run |
| 5 | 2026-08-29 | Docs + knowledge: README (render strategy, history note, CHROME_BIN resolution order, laptop command block, guard documentation, clone-coordination note), docs/scheduling.md (CI CHROME_BIN + unit-test step, cron budget note), docs/design.md D11 wording (rendered pixels, "Rendered from" row), knowledge merges + INDEX | verify 393 checks ALL PASS (recorded 3x); targeted glyph/size audit after the last doc edit: CLEAN; RESULT.md 99.2KB of the 100KB gate |

## Conclusions and output

### What changed (all inside the write boundary)

- Code: `pipeline/screenshots.py` (rewritten to render-don't-fetch), `run.py`
  (browser-resolve-once fetch flow, size-aware RESULT condensation, verify
  additions), `pipeline/site.py` (one new provenance row, screenshot mode
  only), new `tests/test_screenshots.py` (24 tests).
- Content: no post body changed. All 20 published posts were sha256-hashed
  before and after every run (in-run assertion plus independent shell hashes);
  front matter untouched in practice ("already up to date" on every subject).
  `site/` rebuilt deterministically (clean-state byte-identity is a verify
  check and passed).
- Docs: `README.md` (strategy + history, CHROME_BIN resolution order, the
  laptop command block, guard documentation, clone-coordination note),
  `docs/scheduling.md` (CI step with the runner's Chrome + unit-test step,
  cron browser/budget note), `docs/design.md` (D11 wording updated to
  rendered pixels + the new provenance row), `RESULT.md` (diagnosis + runs).
- Knowledge: `knowledge/writing/post-generation-pipeline.md` (truthful-images
  section rewritten), `knowledge/writing/dead-web-source-catalog.md`
  (endpoint proven dead + CDX timings), INDEX in sync.

### The design that replaced the dead endpoint

Per subject: never-clobber check -> canonical URL -> hardened CDX (25s, one
retry, earliest status-200 capture, circuit breaker after 4 consecutive
transport failures) -> pre-check that the playback URL
`https://web.archive.org/web/<ts>/<url>` answers HTTP 200 with a body that
references web.archive.org -> headless render (CHROME_BIN / PATH probe /
macOS bundle; `--headless=new --screenshot --window-size=1024,640
--virtual-time-budget=15000 --hide-scrollbars --disable-gpu --no-first-run
--no-default-browser-check --user-data-dir=<throwaway profile>`, 45s wall
clock, process-group kill on timeout) -> payload guards (PNG magic, exact
1024x640 dimensions, 24576-byte near-blank floor) -> store + additive front
matter (`illustration`, `screenshot_url`, `screenshot_archived_url`,
`screenshot_timestamp`, `screenshot_fetched`). ~2s between subjects.

The guards exist because of a measured asymmetry: an unroutable host makes
chromium never exit and write nothing (so we own the wall clock), while a
fast-failing target makes chromium write a genuine PNG of its own error page
(21768 bytes locally) that passes any magic-byte check. Local calibration:
blank 3301, error 21768, real content 67398 bytes.

### Verified here versus only verifiable on a reachable machine

Verified on this box (evidence in RESULT.md and the test log):

- 393-check `--verify` ALL PASS, three times, including the clean-state
  byte-identical rebuild, both mounted-subpath modes, and the new
  dead-endpoint and archived-url checks; targeted glyph/size audit clean.
- 24 unit tests OK, including two REAL local chromium renders through the
  actual subprocess path: the gazette index served on loopback renders to a
  valid 1024x640 PNG above the floor, and a deliberately closed loopback
  port yields the browser error page, which the guards reject.
- The with-browser tracked-tree rehearsal: browser discovery, CDX retry,
  circuit-breaker trip, per-subject pre-check failures, 20/20 honest
  degradation, bodies unchanged.
- The no-browser path (browser hidden from PATH): one actionable message,
  zero network, one condensed RESULT line.
- The hang case (unroutable IP and NXDOMAIN): chromium wrote no file until
  killed at 100s -- measured in /tmp during recon, recorded in the
  diagnosis entry.

NOT verifiable here (recorded as assumptions, not facts):

- That CDX returns real timestamps from a reachable network and that the
  25s+retry budget converts the operator's 5/20 success rate into ~20/20.
  The five timestamps in the Task's laptop evidence are the only live CDX
  data this Task has; nothing here observed CDX succeed.
- That a real Wayback playback page renders above the 24576-byte floor and
  passes the playback-body pre-check on the live archive. The floor and the
  pre-check are calibrated locally and reasoned, not observed against real
  archive pages; if the laptop run rejects real pages, the constants
  (MIN_PNG_BYTES, the pre-check content rule) are the two knobs, both in
  `pipeline/screenshots.py` with the calibration data in comments.
- Pixel-level appearance of real archived pages (standing SC3 gap at the
  Goal level: no by-eyeball QA of a real screenshot plate has happened
  anywhere yet).

### Exact operator commands (laptop, one copy-paste block)

    cd /path/to/internet-archaeology-blog
    export CHROME_BIN="$(command -v google-chrome || command -v google-chrome-stable \
      || command -v chromium || command -v chromium-browser || command -v msedge)"
    python3 run.py --fetch-screenshots
    python3 run.py --rebuild-only
    python3 run.py --verify

On macOS the export can stay empty (the app bundles are probed). Expect
~25-45 minutes for 20 subjects. Also documented in README and wired into
the CI sample in `docs/scheduling.md` (`CHROME_BIN: /usr/bin/google-chrome`,
preinstalled on ubuntu-latest).

### Limitations and decisions for Eve

- **RESULT.md is nearly full: 99.2KB of the 100KB gate.** The fetch mode now
  self-condenses near the gate (per-subject lines stay on stdout), so runs
  will not overflow it, but roughly one more verify record fits. Rotation of
  the historical sections is an operator/Eve decision; this Task flagged it
  rather than editing history.
- The Task premise "this box has no browser binary" was wrong (chromium
  ships here); both the no-browser degradation and the real browser
  machinery were therefore verified locally, which is strictly more coverage
  than planned. The dead box assumption still holds for the archive itself.
- The near-blank floor (24576) and the playback-body pre-check are the two
  calibration knobs if the laptop run rejects legitimate pages; both are
  single constants/one predicate in `pipeline/screenshots.py`.
- Standing gap inherited from the Goal: nobody has eyeballed a real
  screenshot plate yet (SC3). The first successful laptop run should include
  a by-eye check recorded in RESULT.md.

## Knowledge-capture suggestions

Captured during this run (merge-over-create, sediment protocol followed):

- `knowledge/writing/post-generation-pipeline.md` -- truthful-images section
  rewritten around render-don't-fetch: dead-endpoint evidence from a
  reachable network, subprocess browser invocation with process-group
  timeout, the hang-vs-fast-fail forgery asymmetry and the layered payload
  guards with locally calibrated floor, resolve-browser-once degradation,
  the CDX latency budget with circuit breaker, RESULT self-condensation, and
  "test the untestable path without pretending". Reuse checklist item
  updated; change-history row added.
- `knowledge/writing/dead-web-source-catalog.md` -- the screenshot endpoint
  marked dead with the 404-html-x-20 evidence, the CDX slow-but-alive
  timings with the working timeout budget, and the "dead looks like blocked
  from inside a blocked network" trap. Change-history row added.
- `knowledge/writing/INDEX.md` -- both purpose lines updated (no new files).

Suggested for Eve (outside my boundary):

- The planned `development.md` handbook section ("verify what you publish")
  should cite two patterns from this Task: verify an external HTTP contract
  from a reachable network before designing on it, and calibrate binary
  payload guards locally (blank / error / real-content samples) instead of
  trusting magic bytes.
