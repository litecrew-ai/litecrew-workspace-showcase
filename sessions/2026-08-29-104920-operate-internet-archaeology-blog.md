# Session 2026-08-29 10:49 UTC — Goal operate-internet-archaeology-blog, Task blog-screenshots-and-paths

## Trigger

User reports: "use real screenshots instead of fake svgs" and "style missing when i
mount the site as relative path like localhost/site/" (production mount path will
differ).

## Active Goals at activation

- `operate-internet-archaeology-blog` (active): SC 0/3; this was its first Task.

## Task handled

- Created and dispatched `blog-screenshots-and-paths`; supervised to closure.

## Dispatched subagent

- `web-product-engineer` (by agent type), 120 tool uses, 7 logged rounds.

## Key decisions and outputs

- **Path bug root-caused by reproduction, not guesswork**: the built pages' relative
  refs were always conforming; the breakage appears on servers that serve `/site`
  without a trailing-slash redirect, where page-relative refs degrade to
  root-absolute 404s. Fix: `path_prefix` in site_config.json (default "" = unchanged
  behavior; set to the production mount, e.g. "/gazette/", and every internal ref
  emits prefix-absolute via a single `_url` resolver). New verify stage serves the
  workspace over loopback and asserts all refs return 200 in BOTH modes. Final
  verify: ALL CHECKS PASS, 392 checks.
- **Real screenshots: capability shipped, honestly degraded here**.
  `run.py --fetch-screenshots` (Wayback CDX timestamp lookup + screenshot fetch,
  binaries as source assets copied by the builder). All 20 subjects attempted;
  every attempt failed (`Errno 101`, archive unreachable from this environment);
  0 binaries stored; zero images fabricated. Every post carries
  `illustration: generated` front matter and a visible "generated memorial art"
  plate label; the about page states the policy. The rendering path was verified
  with a synthetic PNG in a scratch build, recorded as a code-path test.
- RESULT.md record style condensed (file at 91.9KB, ~6-8 runs of headroom under the
  100KB gate); rotation of historical verification sections flagged as follow-up.
- Eve merged the deferred one-liner into `knowledge/writing/dead-web-source-catalog.md`
  (screenshot endpoint reachability + fetcher pointer, change-history row).

## Blockers and follow-up suggestions

- **Operator actions**: (1) set `path_prefix` in site_config.json to the production
  mount path and rebuild; (2) run `--fetch-screenshots` from a network with egress
  to web.archive.org (or a CI runner), then `--rebuild-only` — plates will flip to
  real screenshots with provenance labels; (3) decide the binary-gate question:
  screenshot PNG/JPEGs are exempt from the 100KB TEXT gate but each is
  size-reported; a hard per-image cap is a one-line change if wanted.
- Follow-up Tasks under this Goal: RESULT.md rotation policy; cadence decision
  (SC1) still first among the success criteria; visual QA by eye (SC3) still open.

## Knowledge and handbook changes

- Knowledge: two sections merged into
  `knowledge/writing/post-generation-pipeline.md` (truthful image plates, subpath
  mounting) + INDEX purpose updated; Eve merged the catalog one-liner
  (`dead-web-source-catalog.md`). Handbook: no change (backlog item stands).
- Task closed and archived to `archive/tasks/blog-screenshots-and-paths.md`;
  Goal progress log updated. No git actions; the operator commits.
