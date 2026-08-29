---
status: done
goal: operate-internet-archaeology-blog.md
assigned_agent: web-product-engineer
created: 2026-08-29
updated: 2026-08-29
---

# Task: Fix the macOS render hang — isolated profile, self-probe, era-anchored fallback

## Description

The operator's third laptop run (macOS Chrome via app bundle). Everything upstream
now works — CDX resolves or falls back, pre-checks fetch real archived HTML (the
503 backoff visibly recovered newgrounds and pets-com), nearest-capture redirects
resolve timestamps — but every render dies identically:

    render: wall guard killed the process group after 75s with no file
    (chrome never reached its own --timeout=30000ms)
    chrome stderr tail: [only chrome/updater VERBOSE2 crash-handler noise]

Eve's diagnosis (to verify as far as this box allows): the invocation does not pass
`--user-data-dir`, so headless Chrome tries to use the DEFAULT profile. On the
operator's laptop the daily Chrome is running and holds the profile lock — the
headless instance hangs without rendering (the updater/crash-handler noise in the
stderr tail is consistent: helpers spawned, browser never proceeded). It works on
this box only because chromium here runs with clean profile state and nothing else
running. This is an environment-divergence bug in our recipe, not in Chrome.

## Scope — the decisive iteration

1. **Invocation hardening** in `pipeline/screenshots.py` (single flag source stays
   `browser_cmd()`):
   - `--user-data-dir=<fresh temp dir per render>` (created under the system temp,
     removed after) — removes any dependence on the user's running browser/profile.
   - `--no-first-run --no-default-browser-check` (dialog suppression).
   - `--disable-crash-reporter --disable-component-update --disable-background-networking`
     (fewer helper spawns, less stderr noise, no updater side-trips).
   - Keep `--headless=new --screenshot ... --window-size=1024,640 --timeout=...
     --virtual-time-budget=... --hide-scrollbars --disable-gpu`.
   - Smarter stderr capture: keep BOTH the first ~400 and last ~500 chars, and
     filter `chrome/updater` lines out of what gets reported; if the filtered tail
     is empty and no file was written, print the profile-lock hint explicitly.
2. **Self-probe (`run.py --probe-render`)**: run the exact `browser_cmd()` path
   against a `data:text/html` URL (no network needed) and validate the written PNG
   (magic, dimensions, non-blank). Prints browser path, full flag list, elapsed,
   bytes. Exit non-zero with the actionable message on failure. Document as the
   FIRST thing to run on any new machine. ALSO auto-run the probe at the start of
   `--fetch-screenshots`: if it fails, stop before subject attempts (fail fast —
   no more 25-minute doomed runs).
3. **Era-anchored nearest-capture fallback**: `/web/2/<url>` resolves to the
   MOST RECENT capture — for dead sites whose domains are now parked (altavista ->
   a 2026 page), that screenshots a parked domain, not the remembered site. Use the
   fact sheet's era (peak or death year) to anchor `/web/<YYYY>/<url>` (Wayback's
   year-anchored nearest form); fall back to `/web/2/` only when no era data
   exists. Provenance continues to print the RESOLVED timestamp, so labels stay
   truthful either way. Unit-test URL construction and the anchor-year selection.
4. **RESULT.md rotation (now mandatory — the file is at 99.6KB of the 100KB
   gate)**: move historical run/verify entries into `docs/result-log/archive-1.md`
   (create dir; keep each file under the gate; add a rotation policy line: when
   RESULT.md exceeds ~60KB, move all but the newest verification-methods section
   and last ~10 entries into the next archive file). RESULT.md keeps: purpose,
   current verification methods, rotation pointer, recent entries. Nothing is
   deleted — history moves.
5. **Docs + knowledge**: README screenshot section gets a troubleshooting table
   keyed to observed signatures (updater-noise hang -> profile lock, fixed by temp
   user-data-dir; "Page load timed out" -> slow page, raise CHROME_TIMEOUT_MS;
   blank frame -> never-composited page, rejected by floor). Merge the
   environment-divergence lesson into `knowledge/writing/post-generation-pipeline.md`
   (a headless recipe that works on a clean CI box can hang on a daily-driver
   laptop; isolate the profile; always ship a self-probe) + INDEX sync.

## Completion criteria

- [ ] Every render uses a fresh temp `--user-data-dir` removed afterwards; first-
      run/dialog/updater suppression flags present; README documents the exact
      invocation; stderr reporting keeps head+tail with updater lines filtered and
      an explicit profile-lock hint on the empty-filtered-tail case.
- [ ] `run.py --probe-render` exists, is documented as the first-run check, is
      auto-run (fail-fast) at the start of `--fetch-screenshots`, and passes on
      this box's chromium through the real code path.
- [ ] Era-anchored `/web/<YYYY>/<url>` fallback implemented (fact-sheet era
      preferred, `/web/2/` only as last resort); URL construction and anchor
      selection unit-tested; provenance labels unchanged in truthfulness.
- [ ] RESULT.md rotated (history preserved in `docs/result-log/archive-1.md`,
      both files under the 100KB gate, rotation policy documented); the fetch mode
      and verify mode write comfortably within the new headroom.
- [ ] Unit tests extended and green (probe, temp-profile cleanup, era anchoring);
      full verify suite ALL CHECKS PASS; post bodies byte-identical; stdlib only.
- [ ] Knowledge merged + INDEX synced; Task file completed honestly (the profile-
      lock hypothesis cannot be reproduced on this box — no running GUI Chrome —
      so state exactly what was verified locally versus what the next laptop run
      confirms).
- [ ] Usual rules: English; ASCII; no emoji; no check-mark glyphs (U+2713, U+2714,
      U+2705, U+2611 family); no text file over 100KB; no git; no network beyond
      keyless endpoints + loopback.

## Context and constraints

- **Write boundaries**: this Task file; `artifacts/writing/internet-archaeology-blog/`
  (including the new `docs/result-log/`); `knowledge/writing/`. Nothing else. No
  git; no `.github/`.
- Post bodies frozen (additive front matter only).
- Chrome flag semantics vary by version/channel: the probe exists precisely so the
  OPERATOR'S browser proves ITSELF in seconds. Do not claim the laptop is fixed —
  claim the recipe is environment-independent and self-verifying.
- Fastest context load: `pipeline/screenshots.py`, `run.py`, `tests/test_screenshots.py`,
  `archive/tasks/blog-render-timeout-fix.md`, README screenshot section, RESULT.md
  head.

## Preparation (retrieval + diagnosis verification, 2026-08-29)

- Handbooks: only `handbooks/README.md` exists. Loaded knowledge:
  `post-generation-pipeline.md` (truthful-images section), `dead-web-source-catalog.md`,
  INDEX. Protocols: `subagent-workflow.md`, `knowledge-sediment-protocol.md`.
- Artifact context loaded: `pipeline/screenshots.py`, `run.py`,
  `tests/test_screenshots.py` (36 tests), README screenshot section, RESULT.md
  (101940 B of the 102400 B gate), `pipeline/facts.py`, `data/facts/*.json`,
  `archive/tasks/blog-render-timeout-fix.md`.
- **Diagnosis verification (code inspection, on the record)**: Eve's hypothesis says
  the invocation does not pass `--user-data-dir`. The tracked code DOES:
  `browser_cmd()` in `pipeline/screenshots.py` passes
  `--user-data-dir=<fresh temp dir>` per render (inside a per-render
  `tempfile.TemporaryDirectory`, removed after) plus `--no-first-run` and
  `--no-default-browser-check`. Decisive corroboration: the operator's third-run
  signature "wall guard killed the process group after 75s" is a message string that
  only exists in this post-timeout-fix code, which includes those flags. So the
  laptop hung WITH a fresh temp profile in the invocation -- the default-profile-lock
  mechanism, as stated, cannot be confirmed as the cause; some other
  environment-specific behavior of the operator's Chrome (app-bundle singleton
  behavior, flag-set divergence in their channel, helper interference) is at play.
  The profile-lock hang itself cannot be reproduced on this box (no running GUI
  Chrome; chromium here runs with clean profile state). Consequence, per the Task's
  own framing: harden everything that CAN be hardened, and ship the self-probe so
  the operator's browser proves itself in seconds; claim environment-independence
  and self-verification, never "the laptop is fixed".
- Era data check: every `data/facts/<slug>.json` carries years inside its
  confidence-tagged facts (launch/peak/death phrasings differ per subject);
  `cdx_lifespan` is null on all 20 sheets (archive was unreachable at build time),
  so the anchor year must be derived from the fact texts by a documented,
  deterministic, unit-tested rule (peak phrasing preferred, then death phrasing,
  then launch phrasing; `/web/2/` only when a sheet yields no year).

## Execution steps

<!-- Subagent fills -->

1. Task file: record retrieval and the diagnosis verification above.
2. `pipeline/screenshots.py` invocation hardening: add
   `--disable-crash-reporter --disable-component-update
   --disable-background-networking` to `browser_cmd()` (user-data-dir and dialog
   suppression already present; pin all of it with tests); replace the tail-only
   stderr capture with head ~400 + tail ~500 after filtering chrome/updater noise
   lines; explicit profile-lock/run-probe hint when the filtered stderr is empty and
   no file was written.
3. Self-probe: `screenshots.probe_render()` renders a `data:text/html` page through
   the real `render_screenshot` -> `browser_cmd()` path, validates magic /
   dimensions / a locally calibrated non-blank floor; `run.py --probe-render` CLI
   printing browser path, full flag list, elapsed, bytes; fail-fast auto-probe at
   the start of `--fetch-screenshots`.
4. Era-anchored fallback: `era_anchor_year(sheet)` (peak > death > launch phrasing,
   from the fact sheet's own sourced facts), `archived_page_url(url, ts, era_year)`
   emitting `/web/<YYYY>/<url>`, `/web/2/` only when no era year exists;
   `attempt_subject` wiring + honest notes; provenance keeps printing the resolved
   timestamp.
5. Tests: flag-set pinning (new flags), stderr head+tail+filter+hint, fresh temp
   profile per render created/removed (fake-browser recorder, no network), probe
   assessment, era-anchor selection on synthetic + real tracked sheets, era URL
   construction. Full suite green.
6. Calibration + tracked probe: measure the probe page's render size on this box's
   chromium, set the probe floor with the measurement recorded, run
   `python3 run.py --probe-render` tracked.
7. Scratch-tree fetch rehearsal (artifact copy in /tmp, real chromium, archive
   unreachable): proves the fail-fast probe integration and the era-anchored
   fallback notes end to end without touching the tracked tree.
8. RESULT.md rotation: create `docs/result-log/archive-1.md`, move history there
   verbatim, keep purpose + current verification methods + rotation policy + the
   last ~10 entries in RESULT.md, both files under the 100KB gate; rotation-policy
   warning in `run.py` when RESULT.md exceeds ~60KB.
9. Docs + knowledge: README (exact invocation, --probe-render as the documented
   first-run check, era-anchored fallback, troubleshooting table keyed to observed
   signatures, rotation pointer), `docs/scheduling.md` step note, knowledge merge
   into `knowledge/writing/post-generation-pipeline.md` + INDEX sync.
10. Tracked `--verify` (ALL CHECKS PASS expected), condensed fix entry in the
    rotated RESULT.md, Task file conclusions and knowledge suggestions.

## Execution log

<!-- Append after each subagent iteration -->

| Round | Date       | Progress | Notes |
| ----- | ---------- | -------- | ----- |
| 1 | 2026-08-29 | Retrieval + diagnosis verification + plan recorded | Tracked `browser_cmd()` ALREADY passes a fresh temp `--user-data-dir` per render; the operator's "75s wall guard" message only exists in this code, so the laptop ran it WITH the temp profile and still hung -- default-profile lock not confirmable as the cause; hang not reproducible here (no running GUI Chrome). Hardening + self-probe proceed as scoped |
| 2 | 2026-08-29 | Code: `pipeline/screenshots.py` (3 suppression flags in `browser_cmd`; stderr head 400 + tail 500 with chrome/updater lines filtered; `PROFILE_LOCK_HINT`; `PROBE_URL`/`probe_assess`/`probe_render`; `era_anchor_year` + era-anchored `archived_page_url` + `attempt_subject` wiring), `run.py` (`--probe-render` CLI; fail-fast pre-flight probe in fetch; era from `data/facts/`; rotation constants + threshold warning) | Death-phrase regex needed a fix mid-run ("shut AltaVista down" verb-object form escaped `shut down`, leaving altavista at launch 1995); all 20 tracked sheets now anchor inside the subject's life (verified listing). Probe calibrated on this box's chromium: 10990 bytes deterministic, 1.0s; `PROBE_MIN_PNG_BYTES=6000` (blank 3301 < floor < 10990) |
| 3 | 2026-08-29 | Tests: 36 -> 55, all green in 48.6s (flag-set pin incl. new flags + user-data-dir; stderr head/tail/filter/hint; fresh temp profile per render created-in-root/not-precreated/removed, proven with a recorder "browser" with no network; noise-only failure prints the probe hint; probe page offline + assessment matrix + floor calibration contract + real-chromium probe pass; era-anchor priority order + founder-death exclusion + grounded expectations on tracked sheets; era URL construction) | Two first-draft test bugs fixed by asserting the REAL contract: filtered-short stderr carries no snip marker (fixture now forces >900 chars of non-noise), and the profile path is deliberately NOT pre-created (the browser creates it; the per-render temp root is what exists at launch) |
| 4 | 2026-08-29 | RESULT.md rotated: history (v0 through blog-render-timeout-fix) moved verbatim to docs/result-log/archive-1.md (91398 B); RESULT.md rebuilt with purpose + rotation policy + current verification methods + last 10 entries (13235 B, 18.2KB after this Task's records); run.py gained the ~60KB rotation-threshold warning | Split computed by exact bytes before writing (90898 history / 11042 recent); boundary checks confirm the archive starts at the v0 verification record and the recent block starts at "### Run 2026-08-29 18:47:00"; both files far under the 100KB gate |
| 5 | 2026-08-29 | Tracked runs: `--probe-render` PASS (10990 bytes, 1024x640, ~1s, exit 0; invocation printed with the data: URL truncated); scratch-tree fetch rehearsal in /tmp (full artifact copy, real chromium, archive unreachable): pre-flight probe PASS, all 20 subjects carried era-anchored fallback URLs with correct anchors (aim 2017, altavista 2013, myspace 2006, napster 2000, newgrounds 1995, ...), CDX breaker tripped after 4 transport failures, 20/20 degraded honestly, post bodies sha256-identical, exit 0 | Rehearsal confirms the fail-fast integration and the era anchoring end to end through run.py, without touching the tracked tree; tracked RESULT.md gained only the small probe/verify/fix records |
| 6 | 2026-08-29 | Docs + knowledge: README (probe as the documented first-run check, hardened invocation with flag-by-flag rationale, era-anchored fallback, 8-row troubleshooting table keyed to observed signatures, rotation policy), docs/scheduling.md step note, knowledge/writing/post-generation-pipeline.md (item 3 invocation update, item 6 rewritten for era anchoring, NEW item 12 environment-divergence lesson, reuse checklist, verification, change history; frontmatter related_tasks) + INDEX purpose line; final gates: 55 tests OK in 62.9s, tracked --verify 393 checks ALL CHECKS PASS (twice post-change), glyph/size audit CLEAN on all produced files | The only glyph flag in the boundary is 13 em dashes in EVE'S original Task prose (lines 9-105, untouched, same as the archived predecessor Task); every section this agent wrote is pure ASCII |
| 7 | 2026-08-29 | Completion: conclusions, operator next-steps, and knowledge suggestions written; standalone final gate scan over all 104 artifact files: no glyph/size/binary violations in the FINAL state (after the last RESULT.md records); RESULT.md 19256 B, archive-1.md 91398 B, both under the 100KB gate with headroom | All completion criteria walked and met; the one honest deviation is the diagnosis itself (see Conclusions): the missing --user-data-dir theory was disproven by code inspection, recorded on the Task file, in RESULT.md, and in knowledge item 12; zero git commands; network touched only web.archive.org keyless endpoints (scratch tree) and loopback |

## Conclusions and output

### The diagnosis-verification finding (read first)

Eve's hypothesis -- "the invocation does not pass --user-data-dir, so
headless Chrome uses the locked default profile" -- does not match the code
the operator ran. `browser_cmd()` already passed a fresh temp
`--user-data-dir` (inside a per-render TemporaryDirectory, removed after)
plus `--no-first-run --no-default-browser-check`; decisive corroboration:
the operator's third-run signature "wall guard killed the process group
after 75s" is a message string that exists only in the post-timeout-fix
code carrying those flags. So the laptop hung WITH profile isolation in the
invocation. The hang could not be reproduced on this box (no running GUI
Chrome; the chromium here has clean profile state), so the true laptop-only
cause is unknown from here. Everything in the Task was implemented anyway --
the recipe is now maximally environment-independent and self-verifying, and
the probe is the 10-second instrument that tells the operator's browser
apart from theory. Nothing here claims the laptop is fixed.

### What changed (all inside the write boundary)

- `pipeline/screenshots.py`:
  - `browser_cmd()` adds `--disable-crash-reporter`,
    `--disable-component-update`, `--disable-background-networking`
    (user-data-dir and dialog suppression were already present; the flag set
    is pinned by tests).
  - Stderr reporting rebuilt: chrome/updater noise lines filtered, BOTH the
    first ~400 and last ~500 chars kept, and when nothing survives the
    filter with no file written the report prints the explicit
    `PROFILE_LOCK_HINT` (which states the temp profile was already in the
    invocation and points at `--probe-render`).
  - Self-probe: `PROBE_URL` (offline data: page, deterministic), calibrated
    `PROBE_MIN_PNG_BYTES = 6000` (blank 3301 < floor < measured 10990),
    `probe_assess()` (magic/dimensions/floor), `probe_render()` through the
    exact `render_screenshot -> browser_cmd` path.
  - Era anchoring: `PEAK_RE`/`DEATH_RE`/`LAUNCH_RE` + `era_anchor_year()`
    (peak phrasing > death > launch; first matching fact's first year),
    `archived_page_url(url, ts, era_year)` emitting `/web/<YYYY>/<url>` on
    CDX misses with `/web/2/` only when no year exists, `attempt_subject`
    wiring with honest per-subject notes; provenance unchanged (RESOLVED
    timestamp or "nearest capture", never the anchor year).
- `run.py`: `--probe-render` CLI mode (browser path, full flag list with the
  data: URL truncated, elapsed, bytes, actionable failure message);
  fail-fast pre-flight probe at the start of `--fetch-screenshots`; era
  years loaded from `data/facts/`; RESULT rotation constants with a ~60KB
  threshold warning; mode lines and docstrings updated.
- `tests/test_screenshots.py`: 36 -> 55 tests, all green (~49-63s): new
  flag-contract pins, stderr filter/head+tail/hint, fresh-temp-profile
  lifecycle proven offline with a recorder "browser" (fresh per render, not
  pre-created, removed after, distinct roots across renders; plus a
  noise-only "browser" proving the hint path), probe offline assertions +
  assessment matrix + floor-calibration contract + real-chromium probe,
  era-anchor priority order with founder-death exclusion and grounded
  expectations against the tracked fact sheets, era URL construction.
- RESULT.md rotated: history moved verbatim to
  `docs/result-log/archive-1.md` (89.3KB), RESULT.md rebuilt with purpose +
  rotation policy + current verification methods + last 10 entries; after
  this Task's probe/verify/fix records it sits at ~19KB -- fetch and verify
  modes write comfortably within the new headroom.
- README: `--probe-render` documented as the first-run check (first line of
  the copy-paste block), hardened invocation with flag-by-flag rationale,
  era-anchored fallback description, an 8-row troubleshooting table keyed to
  observed signatures, rotation policy; `docs/scheduling.md` fetch-step note
  updated.
- Knowledge: see below.

### What was verified on this box

- 55/55 unit tests OK; tracked `--verify` 393 checks ALL CHECKS PASS (run
  after every code/doc change).
- Tracked `python3 run.py --probe-render`: PASS -- 10990 bytes, 1024x640,
  ~1s, exit 0, through the real `/usr/bin/chromium` and the exact
  production code path (deterministic across five measured runs).
- Scratch-tree fetch rehearsal (full artifact copy in /tmp, real chromium,
  archive unreachable): pre-flight probe PASS; all 20 subjects degraded
  honestly with era-anchored fallback URLs and correct anchor years; CDX
  circuit breaker tripped after 4 transport failures; post bodies
  sha256-identical; exit 0. The tracked tree was never fetched against.
- Glyph/size audit CLEAN on every file this agent produced; the only flags
  in the write boundary are 13 em dashes in Eve's original Task prose
  (lines 9-105, untouched, same situation the archived predecessor Task
  recorded).

### What the operator runs next (the 10-second probe, then the batch)

    cd /path/to/internet-archaeology-blog
    python3 run.py --probe-render        # seconds, offline; PASS/FAIL + hint

If PASS, run the full block from the README:

    export CHROME_BIN="$(command -v google-chrome || command -v google-chrome-stable \
      || command -v chromium || command -v chromium-browser || command -v msedge)"
    python3 run.py --fetch-screenshots
    python3 run.py --rebuild-only
    python3 run.py --verify

Reading the probe output: PASS means this browser runs this recipe
headlessly, so a subsequent subject failure is page/network-specific (see
the README table). FAIL or a hang means the browser environment itself --
try `CHROME_BIN` at a chromium build, or close the running browser once and
re-probe; the probe's message says this. The fetch run now stops before the
first subject on a probe failure, so no more 25-minute doomed runs.

### Limitations (laptop-only; do not claim otherwise)

- The profile-lock/updater-noise hang itself is NOT reproducible here; the
  specific cause on the operator's Chrome remains unknown. Verified: the
  recipe's isolation properties (by construction + offline recorder tests)
  and its self-probe on this box's chromium.
- That the operator's Chrome passes the probe, and that real Wayback
  playback pages produce content-rich captures, remains unobserved from
  this box (web.archive.org unreachable here).
- That `/web/<YYYY>/<url>` resolves era-correctly on the live archive (and
  that the redirect target yields a recoverable 14-digit timestamp) is
  unit-tested against loopback stand-ins only.
- Pixel-level appearance of any real archived page (standing SC3 gap since
  v0): the first successful laptop run should record one.

## Knowledge-capture suggestions

Captured during this run (merge-over-create, sediment protocol followed;
no new knowledge files needed):

- `knowledge/writing/post-generation-pipeline.md`:
  - NEW item 12 (environment divergence): verify a diagnosis against the
    code before shipping the fix narrative; fresh temp profile per render;
    first-run/helper-suppression flags; noise-filtered head+tail stderr with
    an explicit all-noise hint; an offline self-probe as a CLI mode AND a
    fail-fast pre-flight; recorder-browser profile-lifecycle proof; never
    claim the other machine fixed from a clean box.
  - Item 3 updated (full hardened flag list; filtered head+tail stderr).
  - Item 6 rewritten (era-anchored /web/<YYYY>/ fallback; the /web/2/
    most-recent/parked-domain hazard; peak>death>launch year rule with the
    verb-object "shut X down" trap; provenance still the resolved
    timestamp).
  - Reuse checklist extended (two new bullets); verification section +
    change-history row added; frontmatter related_tasks updated.
- `knowledge/writing/INDEX.md`: purpose line for post-generation-pipeline.md
  updated (era-anchored fallback, environment-divergence hardening,
  self-probe). No new rows -- merge, not fragment.

Suggested for Eve (outside this agent's boundary):

- The planned `development.md` handbook could carry an "environment
  independence for subprocess-driven stages" pattern distilled from
  knowledge item 12 (isolate state per invocation; suppress helpers; filter
  noise; ship a self-probe; verify diagnoses against code). Suggested by
  this Task; not merged anywhere per the handbooks rule.
- `dead-web-source-catalog.md` could record, once the operator confirms it
  on the live archive, that `/web/<YYYY>/<url>` year-anchored resolution
  works as documented (left unmerged: no live-archive evidence from this
  box).
