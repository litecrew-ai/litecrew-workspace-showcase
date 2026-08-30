# Workspace recent summary

> Last updated: 2026-08-30 08:09 by Eve
> Window: last 7 days · full history in sessions/archive/

## Active Goal snapshot (≤ 30 lines per Goal, only current state + next step)

- **operate-internet-archaeology-blog** (active, opened 2026-08-29): SC 0/3; first
  Task done (screenshots capability + path_prefix mounting, 392-check verify).
  Next: cadence decision (cron / CI / scheduled activations — needs a user call);
  operator to run --fetch-screenshots from a network with archive.org egress.
- **internet-archaeology-blog** (completed 2026-08-29, archived): built the
  gazette; 20/20 founding corpus published across all 9 categories; redesigned
  site. Live asset: `artifacts/writing/internet-archaeology-blog/`.

## Last 7 days of sessions (reverse chronological, ≤ 3 lines each)

| Date       | Task                                  | Result  | Key output                                                       |
| ---------- | ------------------------------------- | ------- | ---------------------------------------------------------------- |
| 2026-08-30 | (README publication pass, no Task)    | done | root README rewritten as the showcase introduction (workspace intro + GitHub link, gazette preview link, honesty notes updated); see `2026-08-30-080919-workspace-readme-publication.md` |
| 2026-08-29 | blog-image-search-route (goal: operate-internet-archaeology-blog) | done | PIVOT LANDED: 20/20 real historical images via Bing image search fetched live from this box (strict-matched, attributed, 844KB); Commons + render routes behind it; 87 tests, 475 checks; operator by-eye QA pending; see `2026-08-29-153803-operate-internet-archaeology-blog.md` |
| 2026-08-29 | blog-render-profile-fix (goal: operate-internet-archaeology-blog) | done | probe-render self-test (auto fail-fast), era-anchored /web/YYYY/ fallback, RESULT.md rotation, updater-flag hardening; Eve's profile-lock diagnosis disproven by code inspection and recorded; 55 tests, 393 checks; see `2026-08-29-142231-operate-internet-archaeology-blog.md` |
| 2026-08-29 | blog-render-timeout-fix (goal: operate-internet-archaeology-blog) | done | Chrome --timeout self-capture proven by local stalled-page reproduction; 503 backoff; /web/2/ nearest-capture; 36 tests, 393 checks; operator re-run pending; see `2026-08-29-130019-operate-internet-archaeology-blog.md` |
| 2026-08-29 | blog-screenshot-renderer (goal: operate-internet-archaeology-blog) | done | render-don't-fetch (dead endpoint removed, hardened CDX, headless-browser screenshots, PNG guards, 24 tests, 393 checks); operator laptop run pending; see `2026-08-29-114008-operate-internet-archaeology-blog.md` |
| 2026-08-29 | blog-screenshots-and-paths (goal: operate-internet-archaeology-blog) | done | --fetch-screenshots capability (degraded here, archive unreachable, zero fabrication), path_prefix + mounted-subpath verify, 392 checks; see `2026-08-29-104920-operate-internet-archaeology-blog.md` |
| 2026-08-29 | (git ops, no Task)                    | done | Task output committed and pushed at operator instruction (continuation of the recorded git-ops pattern); same detail file |
| 2026-08-29 | (git ops, no Task)                    | done | commit 4d8276d + push to github.com/litecrew-ai/litecrew-workspace-showcase via SoraKlein key at operator instruction; see `2026-08-29-100422-workspace-git-ops.md` |
| 2026-08-29 | blog-publish-all (goal: internet-archaeology-blog) | done | all 20 subjects published, index D10 re-tune, 286 checks PASS, Goal completed; see `2026-08-29-085527-operate-internet-archaeology-blog.md` |
| 2026-08-29 | blog-design-overhaul (goal: internet-archaeology-blog) | done | museum-style redesign, RSS + categories, verifier 63 checks, v0 SOURCES bug fixed; see `2026-08-29-081351-internet-archaeology-blog.md` |
| 2026-08-29 | blog-v0-pipeline (goal: internet-archaeology-blog) | done | v0 pipeline + The Dead Web Gazette, 3 published posts; see `2026-08-29-073711-internet-archaeology-blog.md` |

## Currently open Tasks (active items in tasks/)

- (none — blog-publish-all closed and archived this session)

## Important decisions (last 7 days only · older decisions in archive/)

- 2026-08-29: subpath-mount fix is a `path_prefix` config through one resolver (reproduced first: no-redirect servers break page-relative refs); screenshots capability shipped, degraded honestly here (archive.org unreachable), plates labeled by mode. See `sessions/2026-08-29-104920-operate-internet-archaeology-blog.md`
- 2026-08-29: build Goal completed at 20/20 posts; successor operations Goal `operate-internet-archaeology-blog` opened; live asset deliberately kept at its path (not moved to _closed-goals) because the operations Goal references it. See `sessions/2026-08-29-085527-operate-internet-archaeology-blog.md`
- 2026-08-29: truthfulness at batch scale — thin subjects get declared-thinness posts, never padded texture (eToys pattern); 4 unsourced figures caught pre-publish. Same detail file.
- 2026-08-29: redesign the existing pipeline instead of adopting an SSG (no installs possible; content stays portable); stylesheet is a build product (src -> site byte-copy). See `sessions/2026-08-29-081351-internet-archaeology-blog.md`
- 2026-08-29: falsy-list front-matter bug had shipped empty SOURCES boxes in v0 — fixed; verify must assert data renders, not that boxes exist. Same detail file.
- 2026-08-29: blog product is a live asset at `artifacts/writing/internet-archaeology-blog/`; automation drafts, editorial pass publishes (never-clobber). See `sessions/2026-08-29-073711-internet-archaeology-blog.md`
