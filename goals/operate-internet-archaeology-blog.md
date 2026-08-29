---
status: active
blocked_task:
created: 2026-08-29
updated: 2026-08-29
tags: [internet-archaeology, blog, content-automation, operations]
success_criteria:
  - "SC1: A recurring-run cadence is ratified by the user and recorded in the workspace (local cron, CI workflow, or scheduled Eve activations), with the first cadence-driven content batch produced under it."
  - "SC2: Subject discovery grows beyond the founding 20-subject seed corpus (corpus extended to at least 30 sourced subjects or discovery wired to at least one additional keyless source), with thin categories (one-post categories) brought to at least two posts where the record permits."
  - "SC3: Quality bar holds across batches: run.py --verify green, a truthfulness audit of each batch recorded, and at least one by-eye visual QA of the built site recorded in RESULT.md (closing the standing gap: rendering has only ever been verified structurally in this environment)."
---

# Goal: Operate the internet archaeology blog

## Description

Successor to Goal `internet-archaeology-blog` (completed 2026-08-29, archived at
`archive/goals/internet-archaeology-blog.md`), which built The Dead Web Gazette and
published its founding corpus of 20 illustrated, sourced posts. This Goal covers
operating the product on a recurring cadence, per the user's standing request to
"keep content updated automatically" and to keep growing what visitors can see.

The product remains the live asset at `artifacts/writing/internet-archaeology-blog/`
(one-command pipeline `python3 run.py`; automation drafts, editorial passes publish;
never-clobber; provenance on every post). Operating constraints are unchanged:
Python 3.11 stdlib only, keyless public APIs only, English/ASCII publication gates,
truthfulness law, no git actions by agents (the operator commits).

Known operational facts carried forward:

- Network reachability varies per session (HN Algolia usually live; Wikipedia /
  Wayback CDX often unreachable); every post records its exact data-source mode.
- Pixel-level rendering has never been eyeballed in this environment (browser
  screenshot tooling broken across three sessions); structural verification is
  strong (286 checks) but SC3 exists to close this by recording a human check.
- `base_url` in `site_config.json` is a placeholder until the gazette has a domain.

Related assets: artifacts/writing/README.md

## Success criteria

- [ ] SC1 — cadence ratified and first cadence-driven batch produced
- [ ] SC2 — discovery beyond the founding corpus; thin categories balanced
- [ ] SC3 — quality bar held across batches; by-eye visual QA recorded

## Related Tasks

<!-- Appended automatically each time you split off a Task -->

| Created    | Task file  | Status |
| ---------- | ---------- | ------ |
| 2026-08-29 | archive/tasks/blog-screenshots-and-paths.md | done |
| 2026-08-29 | archive/tasks/blog-screenshot-renderer.md | done |
| 2026-08-29 | archive/tasks/blog-render-timeout-fix.md | done |
| 2026-08-29 | archive/tasks/blog-render-profile-fix.md | done |

## Progress log

| Date       | Progress summary                                          | Key decisions                                                             |
| ---------- | --------------------------------------------------------- | ------------------------------------------------------------------------- |
| 2026-08-29 | Goal created as successor on completion of the build Goal | Live asset stays at its established path (cron/CI docs reference it); assets-lifecycle _closed-goals move deliberately not taken while an operating Goal references the asset |
| 2026-08-29 | Task blog-screenshots-and-paths done: --fetch-screenshots capability (20/20 attempts failed here, archive unreachable; zero fabrication, all plates labeled generated), path_prefix resolver for subpath mounts, mounted-subpath verify stage; 392 checks PASS | Single _url resolver for every internal ref; verify now serves the site over loopback in two mount modes; RESULT.md records condensed (91.9KB, rotation flagged for a future Task); operator decision pending: binary gate exemption + optional per-image cap when screenshots first land |
| 2026-08-29 | Task blog-screenshot-renderer done: dead Wayback screenshot endpoint replaced with render-don't-fetch (hardened CDX -> headless-browser screenshot of the archived page, CHROME_BIN resolution, PNG guards, 24 unit tests incl. 2 real local chromium renders); 393 checks PASS | Operator laptop run proved endpoint dead (404 html x 20) and CDX slow-but-alive (5/20 within 5s) — evidence recorded; render machinery verified locally against loopback (premise correction: this box ships chromium); RESULT.md at 99.2KB of the 100KB gate — rotation is now the next maintenance decision |
| 2026-08-29 | Task blog-render-timeout-fix done: Chrome-internal --timeout (self-capture on stalled pages, proven by local stalled-subresource reproduction), 503 backoff+retry, nearest-capture /web/2/ fallback, stderr in failure logs; 36 tests, 393 checks PASS | Honest caveat on record: a fully-hung page yields a blank frame the floor rejects — such subjects degrade with chrome's own "Page load timed out" reason; CHROME_TIMEOUT_MS is the tuning knob; RESULT.md at 101.9KB of 102.4KB gate — rotation MUST be the next Task |
| 2026-08-29 | Task blog-render-profile-fix done: updater-suppression flags, filtered stderr with profile-lock hint, run.py --probe-render (offline data-URL self-probe, auto fail-fast before fetch; passes on this box), era-anchored /web/YYYY/ fallback, RESULT.md rotation (19.3KB + docs/result-log/archive-1.md 91.4KB); 55 tests, 393 checks PASS | Eve's profile-lock diagnosis DISPROVEN by code inspection (temp --user-data-dir was already in place) — recorded honestly; remaining suspect: macOS bundle-binary single-instance handshake while daily Chrome runs; the probe is the discriminator the operator runs in 10s; honest claim is "environment-independent and self-verifying", not "fixed" |
