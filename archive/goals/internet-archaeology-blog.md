---
status: completed
blocked_task:
created: 2026-08-29
updated: 2026-08-29
tags: [internet-archaeology, blog, content-automation, static-site]
success_criteria:
  - "SC1: An automated pipeline (discovery -> fact research -> post writing -> illustration -> site build) runs end to end via one command, with a dedup ledger so repeat runs only cover new subjects."
  - "SC2: The blog ships at least 12 published posts spanning the subject categories (defunct websites, old forums, 2000s blogs, early internet products, strange personal homepages, dead startups, old software, online subcultures, forgotten stories), each with at least one illustration and cited sources."
  - "SC3: The site builds from a clean state and renders correctly, and a recurring-run recipe (scheduling via cron or CI sample) is documented without touching .github/."
  - "SC4: Reusable knowledge (dead-web source catalog, generation pipeline recipe) is captured under knowledge/writing/ per the sediment protocol."
---

# Goal: Internet archaeology blog

## Description

Build and operate a blog that regularly scours the internet for subjects from the dead
and old web — defunct websites, old forums, 2000s blogs, early internet products,
strange personal homepages, dead startups, old software, online subcultures, and
forgotten stories — and automatically generates a blog post for each subject.

Each post combines:

- **Text**: an evocative, narrative description in the requested style ("In 2004,
  someone built a website. That website once had 3 million users. Today, no one
  remembers it.") grounded in verifiable facts with cited sources — never invented
  statistics or quotes.
- **Illustrations**: procedurally generated artwork in a period-appropriate early-web
  aesthetic (no external image-generation services; none are authorized).

The product is a static site owned as a live asset at
`artifacts/writing/internet-archaeology-blog/` (working display title "The Dead Web
Gazette"; the Task 1 agent may rename it with rationale). The pipeline must be
repeatable: each run discovers candidate subjects, skips already-covered ones via a
ledger, and grows the site.

Operating constraints (standing):

- English-only content; ASCII-safe typography; no emoji and no check-mark glyphs in
  produced files (publication gate).
- Python 3.11 stdlib only; no package installs; external network limited to keyless
  public APIs (Wikipedia/Wikimedia, Internet Archive Wayback CDX, Hacker News Algolia).
- No git operations by agents; the human operator commits.
- Truthfulness over drama: facts must be attributable to a cited source; uncertain
  details are hedged or omitted.

Related assets: artifacts/writing/README.md

## Success criteria

- [x] SC1 — automated pipeline, one command, dedup ledger (met by Task blog-v0-pipeline: `run.py` end to end, ledger proven 20 candidates / 11 skipped / 0 new)
- [x] SC2 — 12+ posts across categories, illustrated, cited (met and exceeded by Task blog-publish-all: 20/20 seed subjects published, all 9 Goal categories covered, as-built table in RESULT.md)
- [x] SC3 — clean build, verified rendering, recurring-run recipe documented (`docs/scheduling.md`; clean-state build byte-identical; pixel-level rendering not eyeballed, recorded honestly in RESULT.md)
- [x] SC4 — knowledge captured under knowledge/writing/ (dead-web-source-catalog, post-generation-pipeline, +INDEX)

## Related Tasks

<!-- Appended automatically each time you split off a Task -->

| Created    | Task file                            | Status |
| ---------- | ------------------------------------ | ------ |
| 2026-08-29 | archive/tasks/blog-v0-pipeline.md    | done   |
| 2026-08-29 | archive/tasks/blog-design-overhaul.md | done  |
| 2026-08-29 | tasks/blog-publish-all.md             | done   |

## Progress log

| Date       | Progress summary                                           | Key decisions                                                             |
| ---------- | ---------------------------------------------------------- | ------------------------------------------------------------------------- |
| 2026-08-29 | Goal created; first Task split off (v0 pipeline + posts)    | Live asset under artifacts/writing/; stdlib-only stack; SVG illustrations |
| 2026-08-29 | Task blog-v0-pipeline done: v0 pipeline live, 3 posts published, SC1/SC3/SC4 met; next: editorial batch toward SC2 | Dispatched as general-purpose container carrying the web-product-engineer contract (agent registry lags file creation); editorial split (automation drafts, pass publishes) |
| 2026-08-29 | Task blog-design-overhaul done: "museum of the early web" redesign, RSS + categories page, extended verifier (63 checks); real v0 defect found+fixed (front-matter falsy-list dropped all source items) | Custom redesign over off-the-shelf SSG (no installs possible; content stays portable); stylesheet as build product (src -> site byte-copy); post bodies untouched (sha256-proven) |
| 2026-08-29 | Task blog-publish-all done: all 20 seed subjects published (17 editorial passes), index re-tuned for scale (D10), verifier 286 checks PASS. SC2 met and exceeded — all four success criteria met, Goal completed and archived | 17 narratives held the truthfulness bar (4 unsourced figures caught pre-publish; etoys thin-sheet handled by declared-thinness, not padding); ledger drift was Eve's stale snapshot, not disk state (stumbleupon drafted by a one-off run between Tasks); live asset stays at current path under successor operations Goal |
