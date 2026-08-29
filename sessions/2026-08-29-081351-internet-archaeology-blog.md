# Session 2026-08-29 08:13 UTC — Goal internet-archaeology-blog, Task blog-design-overhaul

## Trigger

User request: "Build it into a beautiful web site, or use an existing blog system to
display it."

## Active Goals at activation

- `internet-archaeology-blog` (active): SC1/SC3/SC4 met, SC2 open (3 of 12 posts
  published; 8 drafts pending). Live asset healthy after the v0 Task.

## Task handled

- Created and dispatched `blog-design-overhaul` (presentation-layer redesign);
  supervised to closure in this activation. Dispatched by agent type
  `web-product-engineer` (hire of the previous activation — type dispatch worked
  this session).

## Dispatched subagent

- `web-product-engineer`, 6 logged rounds. Rewrote the site's presentation layer in
  `pipeline/site.py` + a hand-written stylesheet; extended the verifier.

## Key decisions and outputs

- **Eve decision: redesign the existing pipeline, not adopt an SSG** (Hugo/Jekyll/
  Pelican rejected: environment cannot install software; partial network; large
  binaries clash with repo gates; bespoke period design is editorially stronger).
  Content stays portable Markdown; SSG-migration note recorded in the README.
- Design brief first: `docs/design.md` ("museum of the early web" — modern editorial
  chrome, period artifacts mounted in framed exhibits; decisions D1-D9 with a
  template traceability matrix).
- Built: magazine index (masthead, stats line, lead card, SVG thumbnails), post
  pages (hero figure, 66ch prose, exhibit-label PROVENANCE/SOURCES, pager),
  categories archive, about restyle, RSS 2.0 with documented `base_url` placeholder
  config, one `styles.css` (no frameworks, no JS).
- **Stylesheet as build product**: hand-written at `src/styles.css`, byte-copied by
  the builder into `site/styles.css` — preserves the byte-identical clean-state
  rebuild guarantee.
- **Real v0 defect found and fixed**: the front-matter parser's falsy-list bug
  dropped every `- ` source item, so all v0 post pages had shipped "(no sources
  recorded)". Fixed (`is not None`) with a new render-regression guard (every source
  URL must appear in output). Eve independently confirmed the fix in the built HTML.
- Post bodies untouched: sha256-proven; only additive `dek:` front matter.
- Verification: extended `run.py --verify` ALL CHECKS PASS (63 checks; includes
  automated clean-state byte-compare). Browser screenshot/DOM tooling still broken
  in this environment (same class as v0, recorded honestly in RESULT.md);
  pixel-level appearance remains unverified by eye — a human opening
  `site/index.html` settles it in one glance.

## Blockers and follow-up suggestions

- None blocking. Next suggested Task (toward SC2): editorial passes on the 8 pending
  drafts (+ optionally the 9 uncovered seed subjects), then visual QA and re-tuning
  of the lead-card/category layouts with a fuller index.
- When a real domain exists: set `base_url` in `site_config.json` and rerun
  `--rebuild-only`.

## Knowledge and handbook changes

- Knowledge merged (no new note): presentation-layer section + 5 checklist items +
  change-history row in `knowledge/writing/post-generation-pipeline.md`; INDEX
  one-liner updated.
- Handbook backlog entry in `handbooks/README.md` amended with the falsy-list
  lesson (assert data renders, not that boxes exist).
- Task closed and archived to `archive/tasks/blog-design-overhaul.md`; Goal
  progress log updated (SC2 still open). No git actions; operator commits.
