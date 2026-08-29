---
status: done
goal: operate-internet-archaeology-blog.md
assigned_agent: web-product-engineer
created: 2026-08-29
updated: 2026-08-29
---

# Task: Fix the render timeout — Chrome never finishes loading Wayback pages

## Description

The operator ran the render-don't-fetch fetcher from their laptop (Chrome found via
macOS app bundle; network fine). Evidence from their run, on the record:

- CDX now resolves timestamps for 17/20 subjects (the 25s budget fixed it); 2 CDX
  timeouts (google-plus, myspace), 1 "no status-200 snapshot" (google-reader).
- Pre-check fetches real archived HTML (HTTP 200, 12KB-285KB) for 15 subjects; 5
  subjects hit HTTP 503 "Internet Archive" challenge/rate-limit pages (geocities,
  newgrounds, posterous, somethingawful, stumbleupon) — plausibly self-inflicted by
  our polling cadence.
- **Every render fails the same way**: "render: timed out after 45s and wrote no
  file (the archived page never finished loading)". Chrome launches, the page loads
  subresources (each archived asset is itself served via web.archive.org with
  redirect chains), "load complete" never arrives within 45s, our subprocess kill
  fires, no PNG is written.

Root cause hypothesis (to verify locally): the invocation relies on
`--virtual-time-budget` and our own wall-clock kill, but has no Chrome-internal
`--timeout`, so Chrome never emits the screenshot on pages that stall. The standard
remedy is Chrome's `--timeout=<ms>` headless flag, which captures the screenshot
after the budget even if the page has not finished loading.

## Scope — a focused fix, not a rebuild

1. **Invocation fix** in `pipeline/screenshots.py`:
   - Add `--timeout=30000` (configurable constant) so Chrome self-captures at ~30s
     regardless of load state; keep or shrink `--virtual-time-budget` (evaluate:
     with `--timeout` present, a smaller budget ~10s is the common working recipe).
   - Raise our subprocess wall budget to ~75s headroom above Chrome's own timeout;
     keep the process-group kill as the outer guard.
   - Capture Chrome's stderr (last ~500 chars) into the per-subject failure log so
     the next operator run diagnoses itself.
   - Keep `--hide-scrollbars`, window size 1024x640, GPU flags as-is.
2. **Local reproduction test (the proof)**: extend `tests/test_screenshots.py` with
   a stalled-page case — a loopback `http.server` whose main page loads but a
   subresource handler sleeps past any sane budget. Assert: with the new flags the
   browser still writes a valid PNG within the wall budget. This reproduces the
   operator's exact failure mode ("never finished loading") on this box's chromium
   and proves the fix before the next laptop run. If this box's chromium lacks
   `--timeout` support, that fact itself is the finding — record it and fall back
   to evaluating old-headless mode or a budget-only recipe, documenting what was
   verifiable.
3. **503 backoff**: at the pre-check (and only there), on an HTTP 503 from
   web.archive.org, sleep ~15s, retry once, then degrade for that subject. Keep the
   inter-subject delay; consider raising it modestly (2s -> 4s) given five 503s in
   one run.
4. **Nearest-capture fallback**: when CDX yields no usable timestamp (timeout after
   retries, or no status-200 row), fall back to Wayback's nearest-capture form
   `https://web.archive.org/web/2/<canonical-url>` (which redirects to the closest
   capture) instead of skipping the render; label provenance with the resolved
   timestamp if recoverable from the final URL, else "nearest capture". Covers
   google-plus, myspace, google-reader.
5. **Docs + knowledge**: README flag documentation updated; RESULT.md condensed
   entry for this Task (mind the ~97KB gate — summarize, do not append raw); merge
   the lesson into `knowledge/writing/post-generation-pipeline.md` (truthful-images
   section: virtual-time-budget alone stalls on Wayback; `--timeout` is the
   capture mechanism; wall kill is only a guard) and INDEX sync.

## Completion criteria

- [x] Invocation carries a Chrome-internal `--timeout` (configurable), stderr is
      captured into failure logs, wall budget has headroom; flags documented in the
      README exactly as invoked.
      (`CHROME_TIMEOUT_MS = 30000` plus a `chrome_timeout_ms` parameter so tests
      scale it; `browser_cmd()` is the single flag source (README documents the
      same list), `RENDER_TIMEOUT` 45 -> 75s with a wall-guard-headroom unit
      test; chrome's stderr tail (last ~500 chars) rides in every failure
      report, and a success-path capture taken at timeout is flagged with
      chrome's own "Page load timed out" wording; `VIRTUAL_TIME_BUDGET`
      15000 -> 10000 per the field recipe.)
- [x] Stalled-page loopback test exists and passes on this box: browser writes a
      valid PNG despite a subresource that never completes. (Or, if chromium here
      cannot honor `--timeout`, the finding is recorded with the chosen fallback
      recipe and the test asserts THAT behavior.)
      (`tests/test_screenshots.py::TestStalledPageRender` -- rich real page (the
      gazette index, 67398B rendered) with one hanging subresource; chromium 150
      DOES honor `--timeout`: the browser self-exits at ~timeout+1s and always
      writes a 1024x640 PNG. Recorded honestly: the timeout capture of a
      never-loading page is a BLANK 3301B frame on this chromium, so the test
      asserts the shipped behavior -- file always written, blank payload
      rejected by the floor -- and passes only if BOTH hold.)
- [x] 503 pre-check backoff+retry implemented; inter-subject delay tuned; behavior
      covered by a unit test where feasible.
      (`precheck_archived(..., backoff_503=15.0)`: HTTP 503 -> sleep -> exactly
      one retry, then degrade; `INTER_SUBJECT_DELAY` 2.0 -> 4.0; four loopback
      unit tests: 503-then-200 recovers, 503-twice degrades after the single
      retry, transport errors never sleep/retry, and the nearest-capture
      redirect resolves a timestamp via the reported final URL.)
- [x] Nearest-capture fallback implemented for CDX-miss subjects; unit-tested for
      URL construction; provenance label rule documented.
      (`archived_page_url(url, None)` now emits `https://web.archive.org/web/2/
      <url>`; `timestamp_from_final_url()` recovers the 14-digit timestamp from
      the redirect target; when unrecoverable the additive front-matter field
      `screenshot_capture_mode: nearest capture` makes the plate label and the
      PROVENANCE box say "nearest capture" -- never an invented date; verify
      gained a conditional label check; README documents the rule.)
- [x] Full verify suite stays ALL CHECKS PASS; post bodies byte-identical; tests
      green; no new dependencies; RESULT.md stays under 100KB.
      (36 unit tests OK (was 24); `--verify` 393 checks ALL CHECKS; tracked
      posts untouched (scratch-tree rehearsal compared every body by sha256
      against the tracked tree: identical; the tracked tree itself was never
      fetched against); stdlib only; RESULT.md at 101940 of 102400 bytes after
      one condensed fix entry + one verify record.)
- [x] Knowledge merged + INDEX synced; Task file completed honestly (including
      anything only verifiable on a reachable network).
      (truthful-images items 3 and 6 rewritten + reuse checklist + change
      history in `knowledge/writing/post-generation-pipeline.md`; INDEX purpose
      line updated; laptop-only items listed in Conclusions below.)
- [x] Usual rules: English; ASCII; no emoji; no check-mark glyphs (U+2713, U+2714,
      U+2705, U+2611 family); no text file over 100KB; stdlib only; no git; no
      network beyond keyless endpoints + loopback.
      (Targeted glyph/size audit over every touched file: CLEAN -- the six em
      dashes flagged in this file are in Eve's original Task prose, untouched,
      same as the archived predecessor Task; zero git commands; network touched
      only web.archive.org keyless endpoints (all failed at the connection
      layer here) and 127.0.0.1 loopback; no downloads, no new imports beyond
      stdlib.)

## Context and constraints

- **Write boundaries**: this Task file; `artifacts/writing/internet-archaeology-blog/`;
  `knowledge/writing/`. Nothing else. No git; no `.github/`.
- Post bodies frozen (additive front matter only, as before).
- The real end-to-end path remains laptop-only; make the next laptop run
  self-diagnosing (stderr in logs, clear per-subject reasons) so a third iteration,
  if needed, is data-driven.
- Fastest context load: `pipeline/screenshots.py`, `tests/test_screenshots.py`,
  `archive/tasks/blog-screenshot-renderer.md`, README screenshot section.

## Preparation (retrieval summary, 2026-08-29)

- Handbooks: only `handbooks/README.md` exists (no domain handbook yet). Standing
  knowledge loaded: `knowledge/writing/post-generation-pipeline.md` (truthful-images
  section), `dead-web-source-catalog.md`, INDEX in sync.
- Artifact context loaded: `pipeline/screenshots.py`, `tests/test_screenshots.py`,
  `run.py` (fetch + verify modes), `pipeline/site.py` (plate caption, provenance rows),
  `pipeline/util.py`, README, `docs/scheduling.md`, prior Task record
  `archive/tasks/blog-screenshot-renderer.md`, RESULT.md tail (393 checks ALL PASS;
  file at 99203 bytes of the 102400-byte gate = ~3.1KB headroom; every new entry
  must stay condensed).
- Environment recon (this box, on the record; chromium =
  `/usr/bin/chromium` 150.0.7871.100, new headless only):
  - Reproduced the operator's exact failure with a loopback stalled page (rich
    real index.html + one hanging subresource): current recipe (vtb=15000, no
    chrome timeout) NEVER exits and writes NO file (killed at 35s wall).
  - `--timeout=<ms>` IS honored: the browser self-exits at ~timeout+0.8s, always
    writes the PNG, and logs `Page load timed out ... N bytes written` on stderr.
    Also proven for the unroutable-host case (http://192.0.2.1/ exits at 8.8s
    with --timeout=8000; without it the process never exits -- the previous
    Task's 100s corpse).
  - Blank-capture caveat: when load never completes, the timeout capture is a
    BLANK frame (3301 bytes at 1024x640) on this chromium -- headless screenshot
    mode does not composite before load-complete. The 24576-byte floor rejects
    it, so stalled subjects degrade, but now with the chrome stderr evidence in
    the log instead of a silent wall kill. Clean pages capture full content and
    exit early (vtb=10000 + timeout=25000 -> 67398 bytes at 21.5s).

## Execution steps

<!-- Subagent fills -->

1. Record retrieval + local reproduction findings in this file (done above).
2. `pipeline/screenshots.py`: add `CHROME_TIMEOUT_MS=30000` + `--timeout` flag
   (parameterized for tests), shrink `VIRTUAL_TIME_BUDGET` 15000 -> 10000, raise
   `RENDER_TIMEOUT` 45 -> 75 (outer guard only), capture chrome stderr (last
   ~500 chars) into failure reports and surface the "Page load timed out"
   signal on success-path reports too; extract `browser_cmd()` for offline flag
   tests.
3. 503 backoff: `precheck_archived` retries once after ~15s on HTTP 503
   (parameterized backoff for tests), returns the FINAL url after redirects;
   `INTER_SUBJECT_DELAY` 2.0 -> 4.0. New `util.fetch_follow()` (only caller is
   the pre-check).
4. Nearest-capture fallback: `archived_page_url(url, None)` now emits the
   `/web/2/<url>` form; `timestamp_from_final_url()` recovers the resolved
   timestamp from the redirect target; provenance label "nearest capture" via a
   new additive `screenshot_capture_mode` front-matter field rendered on the
   plate (`pipeline/site.py` caption) and asserted by verify.
5. `tests/test_screenshots.py`: stalled-page loopback test with the real
   chromium (browser must write a PNG and exit within the wall budget despite a
   subresource that never completes; blank capture must be rejected by the
   floor), flag-set unit test, 503-backoff unit test (loopback), nearest-capture
   URL + timestamp-recovery unit tests.
6. Runs: full unit suite; a scratch-tree fetch rehearsal (copy of the artifact
   in /tmp, with-browser, unreachable archive -> honest degradation) so the
   tracked RESULT.md gains no bulk; one tracked `--verify` (ALL CHECKS PASS
   expected) and ONE condensed RESULT.md entry for the fix.
7. Docs + knowledge: README flag documentation exactly as invoked (timeout,
   budget, backoff, fallback, 4s delay, self-diagnosing stderr), scheduling
   budget note; merge the --timeout lesson into
   `knowledge/writing/post-generation-pipeline.md` truthful-images section +
   INDEX sync; complete this Task file honestly (what is laptop-only).

## Execution log

<!-- Append after each subagent iteration -->

| Round | Date       | Progress | Notes |
| ----- | ---------- | -------- | ----- |
| 1 | 2026-08-29 | Retrieval + environment recon + local reproduction + plan recorded | Operator failure reproduced on this box (vtb-only recipe: no exit, no file); `--timeout` honored by chromium 150 new headless (self-exit ~timeout+0.8s, file always written, "Page load timed out" on stderr, also for unroutable hosts); stalled capture is a blank 3301B frame the 24576B floor rejects; RESULT.md headroom only ~3.1KB |
| 2 | 2026-08-29 | Code: `pipeline/screenshots.py` (CHROME_TIMEOUT_MS + `--timeout`, vtb 10000, wall 75s, stderr tails, `browser_cmd()`, `/web/2/` nearest-capture form, `timestamp_from_final_url`, 503 backoff in `precheck_archived`, 4s delay, capture-mode stamping), `pipeline/util.py` (`fetch_follow` reporting the final URL; HTTP statuses travel in `status`, `err` is transport-only), `pipeline/site.py` (nearest-capture plate label), `run.py` (mode line, docstring, conditional verify check) | Contract bug caught by the new tests on the first run: urllib raises HTTPError for 503, which the first `fetch_follow` draft mapped to `err`, hiding the status from the retry logic; fixed by contract change, then 4/4 backoff tests green |
| 3 | 2026-08-29 | Tests: flag-set contract, wall-headroom, timestamp recovery, 4 precheck/backoff loopback tests, nearest-capture plate-label scratch build, and `TestStalledPageRender` (the proof: real chromium, hanging subresource, file always written, blank rejected) | 36 tests OK in ~62s (was 24); stalled test passes on this box exactly as shipped |
| 4 | 2026-08-29 | Scratch-tree with-browser rehearsal (full artifact copy in /tmp, real chromium, archive unreachable): 20/20 degraded honestly, CDX breaker tripped after 4 transport failures, every miss carried the nearest-capture fallback note, bodies sha256-identical to the tracked tree, exit 0 | Tracked tree never fetched against; first attempt was killed at 600s by my own outer timeout before flushing (archive connections hang the full 25s here), re-run unbuffered completed in ~9 min |
| 5 | 2026-08-29 | Docs + knowledge + records: README (history, exact invocation, budget math, nearest-capture labeling, stalled-page regression note), docs/scheduling.md budgets, knowledge merge + INDEX, one condensed RESULT.md fix entry, tracked `--verify` 393 checks ALL PASS | RESULT.md 101940B of the 102400B gate after the entry + verify record (~460B spare; rotation remains an operator/Eve decision); targeted glyph/size audit CLEAN |

## Conclusions and output

### What changed (all inside the write boundary)

- `pipeline/screenshots.py`: `CHROME_TIMEOUT_MS = 30000` added to the
  invocation (`browser_cmd()` is now the single flag source); 
  `VIRTUAL_TIME_BUDGET` 15000 -> 10000; `RENDER_TIMEOUT` 45 -> 75s (outer
  guard only); chrome stderr tail (last ~500 chars) in every failure report
  plus a "captured at --timeout with load incomplete" flag on success-path
  timeout captures; `precheck_archived` returns the final URL, backs off
  ~15s and retries once on HTTP 503; `archived_page_url(url, None)` emits the
  nearest-capture `/web/2/` form; `timestamp_from_final_url()`; additive
  `screenshot_capture_mode` stamping; `INTER_SUBJECT_DELAY` 2 -> 4s.
- `pipeline/util.py`: `fetch_follow()` (final URL after redirects; HTTP
  statuses in `status`, `err` transport-only).
- `pipeline/site.py`: "nearest capture" on the plate label and in the
  PROVENANCE Illustration row when `screenshot_capture_mode` is set.
- `run.py`: fetch-mode docstring + RESULT mode line rewritten; verify gained
  a conditional nearest-capture-label check.
- `tests/test_screenshots.py`: 24 -> 36 tests, including the stalled-page
  regression proof, the flag-set contract, the 503 backoff matrix, timestamp
  recovery, and the nearest-capture plate-label scratch build.
- Docs: README (history + exact invocation + budget math + labeling rule +
  stalled-page test note), `docs/scheduling.md` (cron/CI budgets).
- Records: RESULT.md one condensed fix entry (file at 101940B of the 102400B
  gate); knowledge merged and INDEX synced. No post body changed anywhere.

### The local reproduction outcome (the proof the Task demanded)

On this box's `/usr/bin/chromium` 150.0.7871.100 (new headless), with a
loopback stalled page (the real gazette index plus one never-responding
subresource):

- Old recipe (vtb=15000, no chrome timeout): the browser NEVER exits and
  writes NO file -- killed at the wall. This is the operator's 20/20 failure,
  reproduced exactly, on a rich real page.
- New recipe (vtb=10000 + `--timeout`): the browser self-exits at
  ~timeout+1s and ALWAYS writes a 1024x640 PNG; stderr says
  `Page load timed out ... N bytes written to file`. Same for unroutable
  hosts (the previous Task's 100s corpse case) -- `--timeout` bounds those
  too.
- Honest caveat, on the record: the timeout capture of a never-loading page
  is a BLANK 3301B frame on this chromium (new headless does not composite
  before load-complete). The calibrated 24576B floor rejects it, so a fully
  stalled Wayback subject will still degrade on the laptop -- but with
  chrome's own stderr line in the log and a flagged capture note, instead of
  a silent wall kill. Wayback subjects whose load DOES complete within 30s
  capture full content and exit early (locally: 67398B at 21.5s).
- `TestStalledPageRender` pins all of the above; it passes on this box and
  stays portable (a future chromium that composites painted content at
  timeout passes it too).

### What remains laptop-only (do not claim otherwise)

- That real Wayback playback pages complete load within 30s (or at all) and
  therefore produce content-rich captures on the laptop. Local evidence only
  covers loopback pages; every claim about live archive behavior is a
  hypothesis until the operator's run.
- That the CDX `/web/2/` redirect actually resolves to a 14-digit timestamp
  recoverable from the final URL on the live archive (unit-tested against a
  faithful loopback stand-in only).
- That HTTP 503 challenges stop after one 15s-backed-off retry (the backoff
  is calibrated from the operator's five-503 run report, not observed here).
- Pixel-level appearance of any real archived page (standing SC3 gap: no
  by-eyeball QA of a real screenshot plate has happened anywhere yet; the
  first successful laptop run should record one).

### Exact next operator command block (laptop)

    cd /path/to/internet-archaeology-blog
    export CHROME_BIN="$(command -v google-chrome || command -v google-chrome-stable \
      || command -v chromium || command -v chromium-browser || command -v msedge)"
    python3 run.py --fetch-screenshots
    python3 run.py --rebuild-only
    python3 run.py --verify

What to expect, so the run reads itself: ~20-50 min; each subject either
stores a PNG (plate flips to screenshot with timestamp provenance, or
"nearest capture" for CDX-miss subjects), or degrades with a reason line
that now carries chrome's stderr tail. If a subject's line says
"captured at --timeout with load incomplete" followed by a floor rejection,
that subject's archived page stalls past 30s -- raise `CHROME_TIMEOUT_MS` in
`pipeline/screenshots.py` (e.g. 60000) and re-run for just those subjects
(after deleting any stored binaries, which never happens for rejected
renders anyway). Pull before running; RESULT.md is ~460B under the gate, so
this workspace cannot absorb another full run record -- rotate or prune
first (operator/Eve decision).

### Decisions worth recording

- Kept `--virtual-time-budget` at 10000 alongside `--timeout` (field recipe;
  locally harmless: clean pages exit at ~vtb+11s with full content).
- The blank-at-timeout capture is REJECTED, not stored: storing a blank
  frame would violate the truthfulness law (it is not the subject's page).
- `fetch_follow` deliberately diverges from `fetch_bytes` on HTTP errors
  (status vs err) -- documented in its docstring; the pre-check is its only
  caller.
- Did not touch Eve's original em dashes in this file (the produced-artifact
  tree and all my additions are pure ASCII; the archived predecessor Task
  file carries the same Eve-style dashes).

## Knowledge-capture suggestions

Captured during this run (merge-over-create, sediment protocol followed):

- `knowledge/writing/post-generation-pipeline.md` -- truthful-images item 3
  rewritten (virtual-time-budget alone never captures while a load is
  pending; `--timeout` is the capture mechanism; wall kill is only a guard;
  stderr tails make runs self-diagnosing; blank-frame caveat on new headless)
  and item 6 extended (nearest-capture `/web/2/` fallback with timestamp
  recovery and honest labeling; 503 backoff at the pre-check; 4s spacing);
  reuse checklist updated; change-history row added; verification section
  gained the reproduction line.
- `knowledge/writing/INDEX.md` -- purpose line updated (no new files).

Suggested for Eve (outside my boundary):

- The planned `development.md` handbook should carry a "reproduce the
  failure before shipping the fix" pattern: this Task's loopback
  stalled-subresource server converted an unverifiable operator-only failure
  into a local regression test. Suggested section skeleton: (1) build the
  minimal server that exhibits the exact external symptom, (2) assert the
  SHIPPED behavior including its honest degradation, (3) keep the test
  portable across environment behavior differences.
- `dead-web-source-catalog.md` could gain one line that the nearest-capture
  form `/web/2/<url>` is a live Wayback behavior worth probing when CDX is
  slow (left unmerged: no live-archive evidence from this box).
