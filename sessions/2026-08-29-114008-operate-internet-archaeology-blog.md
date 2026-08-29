# Session 2026-08-29 11:40 UTC — Goal operate-internet-archaeology-blog, Task blog-screenshot-renderer

## Trigger

User: "i still see the fake screenshots on the latest version site", then ran the
fetcher from their laptop (which has archive.org egress) and shared the output:
0 images, 20 degraded — Wayback screenshot endpoint returned HTTP 404 HTML for
every subject (dead service, not an outage), CDX answered 5/20 within 5s.

## Task handled

- Created and dispatched `blog-screenshot-renderer`; supervised to closure. Eve's
  egress probe first characterized this box (archive.org/wikimedia unreachable;
  example.com and hn.algolia.com reachable) so the limitation was evidence-based.

## Dispatched subagent

- `web-product-engineer`, 91 tool uses. Rewrote the acquisition strategy:
  render-don't-fetch.

## Key decisions and outputs

- **Diagnosis on the record**: the Wayback screenshot endpoint is DEAD (404 html
  x 20 from a reachable network — recorded in knowledge as "a documented-but-dead
  endpoint looks identical to an outage from inside an unreachable network").
- **New strategy**: hardened CDX (25s timeout, retry, status-200 preference,
  circuit breaker, 2s inter-subject delay) -> playback-URL pre-check -> headless
  browser screenshot (CHROME_BIN override or PATH/macOS-bundle probe; documented
  flags; 45s wall budget) -> PNG guards (magic bytes, exact 1024x640, calibrated
  near-blank floor) -> provenance front matter (`screenshot_archived_url`) with
  visible "Rendered from" plate row.
- **Premise correction by the subagent**: this box ships `/usr/bin/chromium`, so
  the render machinery was verified locally (2 real chromium renders in unit
  tests: loopback page passes guards; browser error page rejected). No-browser
  path verified by hiding PATH. 24 unit tests green; full verify 393 checks
  ALL PASS x3.
- **RESULT.md at 99.2KB of the 100KB gate** — near full; fetch mode self-condenses
  but rotation of historical sections is the next maintenance decision.
- README carries the exact laptop command block; CI sample sets
  `CHROME_BIN: /usr/bin/google-chrome` (ubuntu-latest preinstalled) and adds the
  unit-test step.
- The real archive path (CDX answering + real playback page above the guard
  floor) remains verifiable only from a reachable network — recorded as such,
  with the two calibration knobs named.

## Blockers and follow-up suggestions

- **Operator next step**: pull, then run the README laptop block (export CHROME_BIN
  -> fetch -> rebuild -> verify), eyeball one plate (closes the standing by-eye
  SC3 gap for screenshots), and land the binaries (push from laptop or coordinate
  with Eve).
- RESULT.md rotation Task needed soon (next verify record may cross the gate).
- Cadence decision (SC1) still pending with the operator.

## Knowledge and handbook changes

- Knowledge: truthful-images section rewritten in
  `knowledge/writing/post-generation-pipeline.md`; `dead-web-source-catalog.md`
  updated (endpoint dead with reachable-network evidence; CDX budget; render
  pointer); change-history rows; INDEX purpose lines synced.
- Handbook suggestion (logged for the development.md backlog item): "verify an
  external HTTP contract from a reachable network before designing on it" and
  "calibrate binary payload guards locally rather than trusting magic bytes".
- Task archived to `archive/tasks/blog-screenshot-renderer.md`; Goal progress log
  updated. Commit+push follows per the operator's standing submit-when-finished
  instruction.
