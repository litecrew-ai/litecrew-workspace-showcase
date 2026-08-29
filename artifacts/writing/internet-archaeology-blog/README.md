# The Dead Web Gazette

A static blog that scours the internet for subjects from the dead and old web
-- defunct websites, old forums, 2000s blogs, early internet products, strange
personal homepages, dead startups, old software, online subcultures, forgotten
stories -- and produces an illustrated, sourced memorial post per subject.

Live asset of Goal `internet-archaeology-blog`. Built and operated by the
`web-product-engineer` agent; v0 produced by Task `blog-v0-pipeline`.

## Name rationale

The working title "The Dead Web Gazette" was kept. "Gazette" carries the
register the product wants: a small periodical of record for things that no
longer exist. Alternatives considered and rejected: "Ghost Sites Quarterly"
(too literary, hides the subject), "404 Museum" (numeric titles age badly and
read as tech-insider). Recorded here per the Task's naming requirement.

## Quick start

    python3 run.py             # discover -> skip covered -> draft -> rebuild
    python3 run.py --posts 3   # draft up to 3 new subjects this run
    python3 run.py --rebuild-only
    python3 run.py --verify    # structure + gate checks; prints PASS/FAIL

Requirements: Python 3.11, standard library only. No pip packages, no Node,
no server. The built site under `site/` opens directly via `file://`.

See `docs/scheduling.md` for recurring-run recipes (cron and CI sample).

## Architecture

    run.py                     single-command entry point and verifier
    pipeline/
      discovery.py             stage 1: candidate subjects from live APIs + seed
      facts.py                 stage 2: distilled per-subject fact sheets
      writing.py               stage 3: deterministic post scaffolds (drafts)
      svgart.py                stage 4: procedural SVG illustration
      site.py                  stage 5: static site assembly (presentation layer)
      util.py                  fetch/json/slugs/glyph hygiene helpers
    data/
      seed_corpus.json         offline corpus: 20 subjects, sourced facts
      facts/<slug>.json        distilled fact sheets (small by design)
      ledger.json              dedup ledger of covered subjects
    content/
      drafts/<slug>.md         pipeline scaffolds (machine, never overwritten)
      posts/<slug>.md          published posts (human editorial pass)
    src/
      styles.css               the one hand-written stylesheet (source of truth)
    site_config.json           base_url + titles/description (feeds RSS + meta)
    site/                      built output: index.html, categories.html,
                               about.html, rss.xml, styles.css, posts/, assets/
    docs/design.md             design brief: type, palette, grid, components
    docs/scheduling.md         cron + CI recipes
    RESULT.md                  run log: every invocation, mode, verification

Pipeline flow per run: discover candidates -> skip slugs already in the
ledger -> build fact sheets for up to N new subjects -> write scaffold drafts
-> rebuild the site from `content/posts/`. Drafts and posts are never
overwritten; the editorial pass is the act that turns a draft into a post.

## Design and RSS

The presentation follows a **museum-of-the-early-web** brief: a modern
editorial chrome (serif masthead, mono wall labels, warm archive paper)
around period artifacts (the generated mini-homepage SVGs on dark screen
mats, the 468x60 footer banner, a simulated hit counter). The full brief --
typography scale (system font stacks only, no webfonts), palette with hex
values, grid, component inventory, and a template-to-decision traceability
matrix -- lives in `docs/design.md`.

Mechanics worth knowing:

- `src/styles.css` is the hand-written source; the build copies it
  byte-identical into `site/styles.css` so the tracked `site/` tree stays a
  pure build product (clean-state rebuilds reproduce it exactly).
- No JavaScript anywhere; relative links only; the site renders via file://.
- The index is a lead-plus-register layout (decision D10, added when the
  corpus reached 20 posts): category chips with counts, one lead card for
  the newest dispatch, then a compact complete-dispatch list -- every post
  one click from the front page, scannable at any corpus size.
- `site/rss.xml` is built from the published posts. Link origins come from
  `base_url` in `site_config.json`. The documented default is the
  placeholder `https://example.org/dead-web-gazette` -- no real domain
  exists yet; set `base_url` to the real origin (no trailing slash) when
  the gazette is hosted, then rebuild.

**SSG migration note.** The presentation layer is bespoke on purpose (see
Key decisions), but the content stays portable: posts are Markdown-subset
files with plain front matter (`title`, `slug`, `date`, `category`, `dek`,
`status`, `sources`, provenance fields), and the build consumes only
`content/posts/`. Migrating to Hugo / Jekyll / Pelican / Astro later is
mechanical: map the front matter to its template variables, port
`src/styles.css` as-is, and re-point the illustration generator's output at
the target's asset pipeline. Nothing in the editorial layer would need to
change.

## Data sources and degradation

| Source            | Use                                    | Mode in the v0 runs            | Mode in the publish-all batch |
| ----------------- | -------------------------------------- | ------------------------------ | ----------------------------- |
| HN Algolia API    | shutdown-story discovery; citable reaction threads (title, date, points, URL) | live | live |
| Wikipedia API     | defunct-site category members; intro extracts | offline (unreachable from this environment) | offline (SSL handshake timeout) |
| Wayback CDX       | domain lifespan (first/last snapshot)  | offline (unreachable from this environment) | offline (unreachable) |
| Offline seed corpus | 20 well-documented subjects, confidence-tagged facts with canonical URLs | always available | always available |

Every API call has a short timeout and every failure degrades to the seed
corpus instead of crashing. Each post's front matter records the exact
`data_source_mode` string, and the site renders it in a PROVENANCE box, so no
post can silently pretend to better sourcing than it had. Across every run to
date (v0, redesign, publish-all), HN Algolia was reachable while Wikipedia
and the Wayback CDX were not; all factual bases therefore trace to the seed
corpus plus live HN threads.

## Post lifecycle (the editorial split)

1. The pipeline writes `content/drafts/<slug>.md`: a deterministic scaffold
   whose every sentence is a fact plus a citation marker, plus front matter
   with sources and provenance.
2. A human (in v0 and the publish-all batch: the resident writer agent)
   rewrites the body into the narrative register, keeps or extends the
   sources, sets `status: published`, and saves to `content/posts/<slug>.md`.
3. The next rebuild publishes it. Word count, citations, and glyphs are then
   checked by `run.py --verify`.
4. When a draft's editorial pass is published, the scaffold has served its
   purpose; after the publish-all batch the ledger marks it (`draft: null`,
   `post_exists: true`) and `content/drafts/` is empty. A future run drafts
   only subjects not yet in the ledger.

As of 2026-08-29 all 20 seed-corpus subjects are published (editorial passes
1 and 2); the corpus spans all 9 subject categories (6 early internet
products, 5 defunct websites, 2 online subcultures, 2 dead startups, and one
each strange personal homepages, old software, 2000s blogs, old forums,
forgotten stories).

**LLM-API extension point (future).** `pipeline/writing.py` is the single
module to extend: replace `render_scaffold_body` with a call that prompts a
language model with the fact sheet and returns narrative prose under the same
truthfulness rules (no unsourced numbers; keep the sources list). Front
matter, ledger, SVG, and site stages need no changes. No API keys exist in
this environment, so v0 calls no LLM.

## Illustration

`svgart.py` generates one 760x420 "mini homepage" SVG per post, seeded with a
CRC32 of the slug: tiled starfield, table-border bevel frame, two 88x31
buttons, a green hit counter, and barricade stripes. The same slug always
reproduces the same artwork (asserted by `--verify`). No external image
services; SVGs are inlined into the HTML and also saved standalone under
`site/assets/`.

## Key decisions

- **Determinism over cleverness.** Same inputs, same outputs; the clean-state
  build is byte-identical to the tracked build (asserted inside `--verify`,
  not by hand). This makes the exhibit auditable and re-runs safe.
- **Never clobber editorial work.** Drafts and posts are written once; re-runs
  skip existing files. Human text cannot be destroyed by automation. The
  redesign touched presentation only: post bodies were proven byte-identical
  (sha256) after the additive `dek:` front-matter field.
- **Facts carry their own provenance.** Each seed fact has a confidence level
  and a canonical URL; medium-confidence facts must appear hedged in prose.
  Fetched HN text is ASCII-folded at ingestion. SOURCES and PROVENANCE render
  as exhibit labels on every post page, and the verifier asserts every
  front-matter source URL actually appears there.
- **Bespoke presentation layer, portable content.** No off-the-shelf static
  site generator: this environment cannot install software, the v0 pipeline
  already had proven deterministic build/verify machinery, swapping the
  template/CSS layer keeps every guarantee, and for a blog about the old web
  a crafted periodical reads stronger than a generic theme. Content stays
  portable Markdown regardless (migration note above).
- **One stylesheet, system fonts, no JavaScript.** `src/styles.css` is
  hand-written (no framework), copied byte-identical into the build; fonts
  are system stacks only; every core function works without scripts.
- **Verification is a first-class command.** `run.py --verify` re-derives the
  artwork, re-parses every HTML file, resolves every internal link and the
  stylesheet from every page, parses rss.xml, performs a clean-state rebuild
  byte-compare, scans all text files for glyph violations and size limits,
  and walks the ledger.

## Current limitations

- The narrative pass is manual. All 20 seed-corpus subjects are published
  (as of 2026-08-29); future pipeline runs draft new subjects that the
  editor must then pass by hand before they appear on the site.
- Wikipedia and the Wayback CDX have been unreachable from the build
  environment in every session to date (with two different failure
  signatures; see RESULT.md), so category discovery and lifespan metadata
  run in fallback mode; the code paths are live but were exercised only by
  their failure handling here.
- No LLM API is called anywhere; drafting is deterministic assembly, which
  produces scaffolds, not prose.
- The `base_url` in `site_config.json` is a documented placeholder; there is
  no real domain yet, so the RSS links are correct in shape but not
  reachable in practice until it is set.
- Pixel-level rendering was never eyeballed: browser screenshot/DOM tooling
  is broken in the build environment (in v0, the redesign, and the
  publish-all batch); see the verification records in RESULT.md for what was
  verified structurally instead. Posts are English-only and ASCII-safe by
  gate.

## Content rules enforced

English only; ASCII-safe typography; no emoji; no check-mark or checkbox
glyphs (U+2713, U+2714, U+2705, U+2611 family); no invented statistics, dates,
or quotes -- every factual claim is cited or explicitly hedged with the source
named; no text file over 100KB.
