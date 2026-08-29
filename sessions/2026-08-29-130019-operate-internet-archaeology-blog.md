# Session 2026-08-29 13:00 UTC — Goal operate-internet-archaeology-blog, Task blog-render-timeout-fix

## Trigger

Operator's second laptop run: CDX resolved 17/20 timestamps and pre-checks fetched
real archived HTML, but every render failed identically — "timed out after 45s and
wrote no file (the archived page never finished loading)". Five subjects also hit
HTTP 503 challenge pages at pre-check.

## Task handled

- Created and dispatched `blog-render-timeout-fix`; supervised to closure.

## Dispatched subagent

- `web-product-engineer`, 87 tool uses, 5 rounds.

## Key decisions and outputs

- Root cause confirmed locally: the invocation had no Chrome-internal timeout, so
  stalled Wayback subresource loading never reached load-complete. Fix:
  `--timeout=30000` (CHROME_TIMEOUT_MS knob), virtual-time-budget 15000 -> 10000,
  wall guard 45 -> 75s with headroom test, chrome stderr tail (last ~500 chars) in
  every failure report.
- **Failure reproduced before the fix was shipped** (per the emerging handbook
  pattern): a loopback page with one hanging subresource — old recipe never exits;
  new recipe self-exits at ~timeout+1s and always writes a PNG. Honest caveat: on
  this chromium a never-loading page composites as a blank 3301B frame, which the
  24576B floor correctly rejects — fully-stalled subjects will degrade on the
  laptop, now with chrome's own "Page load timed out" reason instead of silence.
- 503 handling: 15s backoff, single retry, inter-subject delay 2 -> 4s (four
  loopback tests). Nearest-capture fallback `/web/2/<url>` for CDX-miss subjects
  (google-plus, myspace, google-reader) with `screenshot_capture_mode: nearest
  capture` labeling — never an invented timestamp.
- 36 unit tests (was 24), verify 393 checks ALL PASS, post bodies sha256-identical
  (scratch-tree rehearsal kept the tracked tree clean).
- RESULT.md at 101,940 of 102,400 bytes — **rotation must be the next Task**; the
  fetch mode self-condenses but essentially no verify-record headroom remains.
- Knowledge merged (truthful-images items rewritten; reproduce-before-fix pattern
  logged as a handbook suggestion for the development.md backlog).

## Blockers and follow-up suggestions

- Operator next step: pull and re-run the README laptop block. Expectations set
  honestly: subjects that composite within CHROME_TIMEOUT_MS capture; fully
  stalled ones degrade with a diagnostic reason; the knob can be raised (e.g.
  60000) if the run log shows blank-frame rejections. Eyeball one stored plate.
- Next Task (forced by the gate): RESULT.md rotation.
- Then: cadence decision (SC1), discovery enrichment (SC2).

## Knowledge and handbook changes

- Knowledge: `post-generation-pipeline.md` truthful-images section updated
  (--timeout is the capture mechanism; virtual-time-budget alone stalls on
  Wayback; wall kill is only a guard); INDEX purpose line synced. The optional
  `/web/2/` note for the source catalog was left unmerged (no live evidence from
  this box) — noted for the next reachable-network run.
- Task archived to `archive/tasks/blog-render-timeout-fix.md`; Goal progress log
  updated. Commit+push follows per the standing submit-when-finished instruction.
