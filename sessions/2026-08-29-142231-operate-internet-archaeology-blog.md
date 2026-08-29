# Session 2026-08-29 14:22 UTC — Goal operate-internet-archaeology-blog, Task blog-render-profile-fix

## Trigger

Operator's third laptop run: every render hung ("wall guard killed after 75s, no
file; chrome never reached its own --timeout"), stderr tail only chrome/updater
noise. Upstream stages all worked (CDX, 503 backoff recoveries visible, fallback
redirects resolving).

## Task handled

- Created and dispatched `blog-render-profile-fix`; supervised to closure.

## Dispatched subagent

- `web-product-engineer`, 95 tool uses. Delivered the scope AND disproved Eve's
  diagnosis — the honesty-law working as designed.

## Key decisions and outputs

- **Eve's diagnosis was wrong and the record says so**: code inspection showed
  `browser_cmd()` already passed a fresh temp `--user-data-dir` per render plus
  `--no-first-run`; the operator's hang occurred WITH profile isolation. The
  remaining suspect (Eve's updated read, not laptop-verified): the macOS
  Chrome.app bundle binary blocking on a single-instance handshake while the
  daily Chrome is running. Discriminator shipped instead of a claimed fix.
- **`run.py --probe-render`**: offline (data-URL) render through the exact
  production code path; validates PNG; prints browser, flags, elapsed, bytes;
  auto-runs fail-fast before any fetch attempt. Passes on this box's chromium
  (10990 bytes, ~1s, deterministic across five runs). The operator's 10-second
  first step on any machine.
- Invocation hardened further (`--disable-crash-reporter
  --disable-component-update --disable-background-networking`); stderr reporting
  keeps head+tail with chrome/updater lines filtered and an explicit
  profile-lock/single-instance hint on empty filtered output.
- **Era-anchored fallback**: `/web/<YYYY>/<url>` from the fact sheet's era
  (peak > death > launch) replaces `/web/2/` as primary fallback — the
  operator's log showed /web/2/ resolving to 2026 parked pages for dead domains
  (altavista); provenance keeps printing the RESOLVED timestamp. Anchor
  selection unit-tested (verb-object traps included).
- **RESULT.md rotated**: history verbatim to `docs/result-log/archive-1.md`
  (91.4KB); RESULT.md rebuilt to 19.3KB with rotation policy + ~60KB threshold
  warning in run.py. Nothing deleted.
- 55 tests green; verify 393 checks ALL PASS; post bodies untouched (fetch
  rehearsals in /tmp scratch only); final gate scan of all 104 artifact files
  clean.

## Blockers and follow-up suggestions

- **Operator next step (decisive)**: `python3 run.py --probe-render`. If it hangs
  with daily Chrome open -> quit Chrome and re-probe; if it then passes, the
  single-instance handshake is confirmed and fetches should run with Chrome quit
  (or a side-installed Chromium via CHROME_BIN). If the probe passes outright,
  run the full fetch; any remaining failures will now carry diagnostic reasons.
- After screenshots land: by-eye plate check (SC3 gap), then push binaries.
- Then: cadence decision (SC1), discovery enrichment (SC2).
- Handbook suggestion logged: "verify the diagnosis against the code before
  shipping the fix narrative" for development.md.

## Knowledge and handbook changes

- Knowledge: `post-generation-pipeline.md` truthful-images section — new item 12
  (environment divergence; isolate profile; ship a self-probe; verify the
  diagnosis against the code), items 3/6 rewritten, checklist extended, change
  history; INDEX synced. `/web/<YYYY>/` year-anchored form noted for the source
  catalog once live-confirmed.
- Task archived to `archive/tasks/blog-render-profile-fix.md`; Goal progress log
  updated. Commit+push follows per the standing submit-when-finished instruction.
