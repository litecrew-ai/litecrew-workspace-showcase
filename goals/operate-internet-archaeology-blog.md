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

## Progress log

| Date       | Progress summary                                          | Key decisions                                                             |
| ---------- | --------------------------------------------------------- | ------------------------------------------------------------------------- |
| 2026-08-29 | Goal created as successor on completion of the build Goal | Live asset stays at its established path (cron/CI docs reference it); assets-lifecycle _closed-goals move deliberately not taken while an operating Goal references the asset |
