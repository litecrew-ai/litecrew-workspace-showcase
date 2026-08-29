---
status: done
goal: internet-archaeology-blog.md
assigned_agent: web-product-engineer
created: 2026-08-29
updated: 2026-08-29
---

# Task: Gazette design overhaul — a beautiful site from the existing pipeline

## Description

The user asked to "build it into a beautiful web site, or use an existing blog system
to display it". Eve's decision, recorded here: **redesign the presentation layer of
the existing deterministic pipeline** rather than adopting an off-the-shelf static
site generator (Hugo / Jekyll / Pelican / Astro).

Rationale (Eve, 2026-08-29):

- This environment cannot install software: no pip, no Node, no Ruby; network
  reachability is partial (HN Algolia only during v0 runs), and fetching generator
  binaries or themes would both require user authorization for installs and drag
  large binaries into a repo whose gates cap file sizes.
- The v0 pipeline already has a proven deterministic builder, verifier, ledger, and
  provenance machinery; swapping its template/CSS layer is low-risk and keeps every
  guarantee (byte-identical rebuilds, glyph gates, never-clobber editorial safety).
- Content is and stays portable: posts are Markdown-subset files with front matter —
  a future migration to any SSG is mechanical if ever wanted. Record this migration
  note in the artifact README.
- For a blog about the old web, a bespoke period-flavored design is editorially
  stronger than a generic theme.

Design direction (Eve's brief, refine and execute): "museum of the early web" — a
clean, modern-editorial chrome (strong masthead, clear type hierarchy, generous
whitespace) around period-flavored artifacts (the generated SVG mini-homepages,
88x31-button motifs, hit-counter typography). The design must read as a crafted
periodical, not as literal 1997 HTML and not as a generic bootstrap-era template.

Scope, concretely:

1. **Design brief first**: write `docs/design.md` inside the artifact directory —
   typography scale (system font stacks only; no webfont downloads), palette (with
   hex values, era-inspired accents), layout grid, and component inventory. Every
   template decision must trace back to this brief.
2. **Index page**: magazine-style front page — masthead, tagline, category
   navigation, and one card per published post showing the post's SVG illustration
   (scaled as thumbnail), title, date, category, and a one-line dek. Newest first.
3. **Post pages**: illustrated header (the SVG art as a hero), readable article
   typography (comfortable measure, ~65ch), styled SOURCES and PROVENANCE boxes that
   read as exhibit labels, prev/next post navigation, and a back-to-index affordance
   on every page.
4. **About page**: restyled to match; must still state what the blog is and how posts
   are generated.
5. **Category archive**: one page grouping published posts by category (the Goal's
   subject categories), linked from the nav.
6. **RSS feed**: `site/rss.xml`, valid XML, ASCII-safe, listing published posts.
   Introduce a `base_url` config (documented default; no real domain exists yet).
7. **CSS**: one hand-written `site/styles.css` (relative link, file://-safe), no CSS
   frameworks, no JS required for any core function.
8. **Verifier extensions**: `run.py --verify` additionally checks that styles.css
   resolves from every page, every index card links its post, thumbnails/hero SVGs
   present, rss.xml parses and lists every published post, and the clean-state
   rebuild stays byte-identical. All previous checks keep passing.
9. **Do not rewrite post bodies.** The editorial layer (content/posts/) is frozen;
   this Task changes presentation only.

## Completion criteria

- [ ] `docs/design.md` exists with the brief (type, palette, grid, components) and
      the design-to-template traceability described above.
- [ ] Index renders as specified: masthead, nav, one card per published post with
      SVG thumbnail, title, date, category, dek; newest first.
- [ ] Every post page: hero SVG, article typography per brief, styled SOURCES and
      PROVENANCE boxes, prev/next links, back-to-index; about and category pages
      restyled and linked in nav.
- [ ] `site/rss.xml` exists, parses as XML, lists all published posts; `base_url`
      config documented in the README.
- [ ] `run.py --verify` passes with the extended checks; clean-state build remains
      byte-identical to the tracked build; verification method and results recorded
      in RESULT.md (including anything you could not verify, as before).
- [ ] Artifact README updated (design decisions, RSS/base_url, the SSG-migration
      note, updated architecture map); RESULT.md gains the redesign run entries.
- [ ] Knowledge updated by merging a design/template-layer section into
      `knowledge/writing/post-generation-pipeline.md` (merge-over-create; update its
      INDEX line if the purpose statement changes). Do not create a third note
      unless it truly cannot fit.
- [ ] Content rules hold: English; ASCII-safe; no emoji; no check-mark/checkbox
      glyphs (U+2713, U+2714, U+2705, U+2611 family); no text file over 100KB; no
      new binary assets, package installs, webfont fetches, or external network use
      at all (this Task needs no network).

## Context and constraints

- **Write boundaries**: this Task file; `artifacts/writing/internet-archaeology-blog/`
      (all of it, including content/ presentation-adjacent metadata if a dek is
      needed — but not post body rewrites); `knowledge/writing/` (merge-edit the
      pipeline note, keep INDEX in sync). Nothing else.
- **Stack**: unchanged — Python 3.11 stdlib only, no network, no git commands
      (operator commits), no changes under `.github/`.
- **Dek extraction**: if a post has no dek, derive a neutral one from its front
      matter/category at build time rather than editing post bodies; or extend front
      matter with a `dek:` field, which IS an allowed metadata edit (additive, not a
      body rewrite). Record the choice in RESULT.md.
- **Truthfulness**: unchanged — nothing in the new UI may overstate sourcing;
      PROVENANCE stays visible on every post page.
- Prior context: `archive/tasks/blog-v0-pipeline.md`, the artifact README, and
  `knowledge/writing/post-generation-pipeline.md` are the fastest way to load
  context. The site builder is `pipeline/site.py`; the verifier lives in `run.py`.

## Execution steps

<!-- Subagent fills -->

### Preparation (retrieval, round 1)

- `handbooks/`: only `README.md` (no domain handbook; backlog notes the
  development.md gap already). No new retrieval available.
- `knowledge/writing/`: `post-generation-pipeline.md` (v0 recipe: determinism,
  never-clobber, glyph gates, verifier-first), `dead-web-source-catalog.md`
  skimmed (no network needed this Task).
- Read in full: Task file, Goal, artifact README + RESULT.md + docs/scheduling.md,
  `run.py`, `pipeline/site.py`, `pipeline/svgart.py`, `pipeline/util.py`, all 3
  published posts, v0 Task record. PUBLICATION.md gates re-checked read-only
  (ASCII, no emoji/check marks, 100KB cap, no absolute operator paths, business
  dir `writing/` whitelisted). Memory note `publication-gate-policy` honored.
- Constraint digested: post bodies stay byte-identical; only additive `dek:`
  front matter may be added (choice recorded per Task).

### Plan

1. Write `docs/design.md`: concept, type scale (system stacks), palette (hex),
   grid, component inventory, decision IDs D1..Dn, traceability matrix.
2. Add `src/styles.css` (hand-written source of the one stylesheet; builder
   copies it byte-identical into `site/styles.css` so clean-state rebuilds stay
   complete) and `site_config.json` (`base_url` + titles, documented default).
3. Rewrite the presentation layer of `pipeline/site.py`: magazine index (masthead,
   nav, stats line, cards with SVG thumbnails), post pages (hero figure, 66ch
   prose, exhibit-label PROVENANCE/SOURCES, prev/next pager, back-to-index),
   restyled about, new categories archive, RSS 2.0 build, footer with period
   banner + simulated counter. No JS, relative links only.
4. Add additive `dek:` front matter to the 3 published posts (bodies untouched;
   verify with sha256 before/after). Build-time neutral fallback dek for any
   post lacking one.
5. Extend `run.py --verify`: stylesheet resolves from every page, card-per-post
   links, hero figures, rss.xml parses + lists all posts, categories page,
   script-free pages, automated clean-state rebuild byte-compare. Keep all v0
   checks.
6. Rebuild + verify to green; record in RESULT.md.
7. Attempt real-browser render check via file:// (screenshot tooling was broken
   in v0; try again, record honestly either way).
8. Update artifact README (design decisions, RSS/base_url, SSG-migration note,
   architecture map) and RESULT.md redesign entries.
9. Merge a design/template-layer section into
   `knowledge/writing/post-generation-pipeline.md` (+INDEX line if purpose
   shifts).
10. Self-check against every completion criterion; fill conclusions.

## Execution log

<!-- Append after each subagent iteration -->

| Round | Date       | Progress | Notes |
| ----- | ---------- | -------- | ----- |
| 1 | 2026-08-29 | Retrieval done, plan set | No handbooks exist (known gap); v0 recipe + artifact code fully loaded; post-body freeze constraint handled via planned sha256 before/after proof |
| 2 | 2026-08-29 | docs/design.md written (D1-D9 + traceability matrix); src/styles.css; site_config.json (base_url) | Stylesheet is a build product: builder copies src/styles.css byte-identical into site/styles.css so clean-state rebuilds stay complete |
| 3 | 2026-08-29 | pipeline/site.py presentation layer rewritten (masthead/nav/cards/hero/prose/exhibits/pager/categories/rss/footer); additive dek front matter on 3 posts | Two syntax fixes on first run (f-string nesting, 3.11); post bodies proven byte-identical via sha256 before/after |
| 4 | 2026-08-29 | run.py --verify extended; first full run ALL CHECKS PASS -- but stats line exposed a real v0 defect | Front-matter list parser dropped every source item (`and current_list` truthiness on an empty list); v0 SOURCES boxes had shipped "(no sources recorded)". Fixed with `is not None` + new regression guard asserting every source URL renders |
| 5 | 2026-08-29 | Browser render check re-attempted: navigation via file:// OK; screenshot/DOM extraction still broken (CDP client uninitialized / no LLM key) | Recorded honestly in RESULT.md; compensated with CSS brace lint inside verify |
| 6 | 2026-08-29 | Docs closed out: README (design, RSS/base_url, SSG migration note, architecture map, decisions, limitations), RESULT.md overhaul record; knowledge merged into post-generation-pipeline.md (+INDEX line) | Final verify ALL CHECKS PASS (63 PASS lines); gate sweep over 57 files: zero glyph/size violations (the 8 em dashes in this Task file are Eve's original prose, untouched) |

## Conclusions and output

### What changed

- `docs/design.md` (new): the "museum of the early web" brief -- system-font
  type scale, 9-token palette with hex values, grid, component inventory,
  decisions D1-D9, and a traceability matrix mapping every template element
  to a decision.
- `src/styles.css` (new): the one hand-written stylesheet (~480 lines, no
  framework); the builder copies it byte-identical into `site/styles.css`.
- `site_config.json` (new): `base_url` (documented placeholder
  `https://example.org/dead-web-gazette`), site title, tagline, description.
- `pipeline/site.py`: presentation layer rewritten -- magazine index
  (masthead with double rules, kicker, stats line, nav, deck, cards with SVG
  thumbnails, lead card for the newest post), post pages (kicker/title/dek/
  byline header, hero figure with plate caption, 66ch prose with drop cap,
  exhibit-label PROVENANCE and SOURCES boxes, older/all/newer pager),
  restyled about page, new categories archive, RSS 2.0, footer with the
  468x60 banner and a simulated hit counter (post-count formula). Post
  bodies render through the unchanged markdown subset; the body's leading
  `# title` line is elided only when it equals the front-matter title (one
  h1 per page).
- `content/posts/*.md`: additive `dek:` front matter only. Bodies proven
  byte-identical by sha256 of the body region before and after the edit.
- `run.py --verify`: extended (see below); build calls now carry
  css_src + config.
- `README.md`: architecture map updated; new "Design and RSS" section with
  the SSG migration note; key decisions and limitations refreshed.
- `RESULT.md`: design-overhaul verification record appended between the v0
  runs and the redesign run entries.

### Key decisions and why

- **Stylesheet as a build product.** A hand-written file inside `site/`
  would break the clean-state guarantee (an empty-dir rebuild could not
  reproduce it). Source at `src/styles.css`, byte-copied by the builder,
  gives both "hand-written" and "byte-identical rebuild".
- **Dek via additive front matter**, with a neutral build-time fallback for
  posts without one -- presentation metadata, not a body rewrite.
- **Deterministic ornament only.** Counter, exhibit numbers, plate numbers,
  and RSS dates all derive from build inputs; no `datetime.now()` anywhere
  in templates, so rebuilds stay byte-identical.
- **Two f-string-era portability fixes** (Python 3.11 rejects nested
  same-quote f-strings) were the only code failures en route.

### Verified versus assumed

- Verified by execution: `run.py --rebuild-only` + extended `--verify`
  ALL CHECKS PASS (63 checks) -- including new checks for card count/order,
  thumbnail links, hero figures, pager/back-to-index, categories listing,
  stylesheet existence + byte-identity + resolution from every page + brace
  lint, script-free pages, rss.xml parse + item coverage, base_url shape,
  per-post source URLs actually rendering, and the clean-state rebuild
  byte-compare now automated inside verify. Post bodies byte-identical
  (sha256). Gate sweep over 57 files: zero glyph/size violations.
- Not verified: pixel-level appearance in a real browser. Navigation to
  site/index.html via file:// succeeded, but every screenshot/DOM extraction
  path still fails in this environment (CDP client not initialized; no LLM
  key for content extraction) -- same breakage class as v0, recorded in
  RESULT.md. Confidence rests on structural checks plus the CSS being
  deliberately conservative (system fonts, standard properties only).

### Limitations and follow-ups

- `base_url` is a placeholder; set it when the gazette gets a domain, then
  rebuild (one line in site_config.json).
- The design is tuned for the current 3 posts; the lead-card treatment and
  category page should be re-eyed once the 8 pending drafts are published.
- Visual QA by eye remains outstanding until browser tooling works in this
  environment; a human opening site/index.html in any browser settles it in
  one glance.

## Knowledge-capture suggestions

Merged (no new note created) into
`knowledge/writing/post-generation-pipeline.md`:

- New section "The presentation layer (from the design overhaul)": design
  brief before templates with decision IDs + traceability; stylesheet as a
  build product; config-not-code for environment facts; the falsy-list
  front-matter parser trap (assert data renders, not that boxes exist);
  verifier extensions that generalize (stylesheet resolution, script-free,
  feed parse, in-verify clean-state byte-compare); deterministic ornament.
- Reuse checklist extended by five items; change-history row added; the
  INDEX.md one-liner now mentions the design/template layer.

Eve may also want to fold the falsy-list trap into the future
`handbooks/development.md` backlog item ("verify what you publish"): the
v0 verifier passed while every SOURCES box was empty because it checked for
the box, not the contents.
