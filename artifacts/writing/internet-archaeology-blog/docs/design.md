# Design brief: The Dead Web Gazette

> Presentation-layer specification for the redesign (Task `blog-design-overhaul`,
> 2026-08-29). Every template and stylesheet decision in `pipeline/site.py` and
> `src/styles.css` traces to a decision ID (D1, D2, ...) defined here.

## Concept

A **museum of the early web**. The site is a modern editorial periodical --
warm archive paper, serif headlines, mono wall labels, generous whitespace --
that mounts period-flavored artifacts as exhibits: the procedurally generated
mini-homepage SVGs sit on dark "screen" mats inside framed figures; the 468x60
banner and the hit counter are quarantined in the footer as period pieces.

It must read as a crafted periodical, not as literal 1997 HTML (no tiled page
backgrounds, no table layout, no blinking anything in the chrome) and not as a
generic bootstrap-era template (no centered gray cards on white, no default
blue). The period flavor lives inside the artifact mounts; the chrome stays
contemporary editorial.

## Decisions

- **D1 -- Modern editorial chrome.** Serif masthead with double rules, mono
  uppercase labels with wide letter-spacing, one accent color used sparingly
  (oxide red), a clear type hierarchy, generous margins.
- **D2 -- Artifacts are mounted, not reenacted.** Every period motif (mini
  homepage SVG, 88x31-button banner, hit counter) appears inside an explicit
  mount: a bordered frame on a dark screen-colored mat, with a caption. The
  page around it stays paper.
- **D3 -- Long-form reading first.** Post bodies are the product: 66ch measure,
  1.7+ line height, 17-18px body, drop cap on the opening paragraph.
- **D4 -- Provenance is an exhibit label.** The SOURCES and PROVENANCE boxes
  are styled as museum wall labels: small mono caps heading, paper-deep ground,
  oxide left rule. Truthfulness is a design feature, so the labels are first
  class, not footer noise.
- **D5 -- Wayfinding everywhere.** One consistent nav (dispatches /
  categories / about / rss) on every page; every post page carries a back-to
  -index affordance in the pager; the current nav item carries
  `aria-current="page"`.
- **D6 -- Deterministic ornament only.** Every decorative number derives from
  build inputs: the hit counter is a fixed formula of the post count, exhibit
  and plate numbers derive from publication order. Nothing random enters the
  chrome; reruns are byte-identical.
- **D7 -- System fonts only, two families.** No webfont downloads (D8 in the
  Task: no network). A serif for display and body; a mono for labels, metadata,
  and counter digits. Two families keep the identity coherent without shipping
  a single font byte.
- **D8 -- file:// safe, script-free.** One hand-written stylesheet linked
  relatively (`styles.css`, `../styles.css`), relative links everywhere, no
  JavaScript for any core function, no external requests of any kind.
- **D9 -- Accessible by default.** Visible focus states, AA-contrast text
  pairs on paper, `figure`/`figcaption` for art, `time` elements for dates,
  `aria-current` for nav, decorative SVG art labeled with `role="img"`.
- **D10 -- Scale without walls of cards.** Added at the 20-post corpus
  (Task `blog-publish-all`): the index front page is lead-plus-register, not
  a card grid. A category chip row (one chip per category, each with its
  count) sits under the deck; the newest post keeps the lead card with its
  art; every remaining post is one compact row of a complete dispatch list
  (date + category on the left, title + dek on the right). Every post is
  reachable from the index in one click at any corpus size, the page stays
  scannable at 20+ entries, and only one inline SVG (the lead) keeps the
  index small. The categories page remains the full grouped archive.

## Typography

Families (system stacks only):

```css
--serif: Georgia, 'Iowan Old Style', 'Times New Roman', Times, serif;
--mono: ui-monospace, 'Cascadia Mono', 'SF Mono', Menlo, Consolas,
        'DejaVu Sans Mono', monospace;
```

Scale (rem values at the 16px root; the masthead and post titles use clamp()
so phone widths shrink gracefully):

| Role              | Family | Size / line-height        | Notes                            |
| ----------------- | ------ | ------------------------- | -------------------------------- |
| Masthead title    | serif  | clamp(2.75, 7vw, 4.25)/1.05 | weight 700                       |
| Masthead kicker   | mono   | 0.78/1.4                  | uppercase, ls 0.18em, oxide      |
| Masthead tagline  | serif  | 1.1/1.4                   | italic, ink-soft                 |
| Post h1           | serif  | clamp(2, 4vw, 2.6)/1.15   | weight 700                       |
| Section h2        | serif  | 1.45/1.25                 |                                  |
| Section h3        | serif  | 1.15/1.3                  |                                  |
| Body              | serif  | 1.06/1.72                 | max-width 66ch                   |
| Dek               | serif  | 1.2/1.45                  | italic, ink-soft                 |
| Card title        | serif  | 1.5/1.2                   | lead card 1.9rem                 |
| Card dek          | serif  | 1.0/1.55                  | italic, ink-soft                 |
| Meta / labels     | mono   | 0.78/1.5                  | uppercase, ls 0.14em, ink-soft   |
| Exhibit text      | mono   | 0.82/1.7                  |                                  |
| Counter digits    | mono   | 1.0/1                     | phosphor on night                |
| Colophon          | mono   | 0.75/1.6                  | ink-soft, centered               |

## Palette

| Token        | Hex       | Role                                                |
| ------------ | --------- | --------------------------------------------------- |
| paper        | `#f6f1e6` | page background (warm archive paper)                |
| paper-deep   | `#ece4d2` | exhibit labels, page-head ground                    |
| ink          | `#26221a` | primary text                                        |
| ink-soft     | `#6b6350` | metadata, deks, colophons                           |
| line         | `#d8cfba` | hairlines, rules, card borders                      |
| oxide        | `#8f2d1c` | accent: kickers, exhibit rules, stamps, hover       |
| teal         | `#0e6f6a` | links (period teal darkened for contrast on paper)  |
| night        | `#101426` | artifact mats (kin to the SVGs' own `#000030`)      |
| phosphor     | `#58d67d` | hit-counter digits on night                         |

Contrast pairs used (checked against WCAG AA thresholds): ink on paper
(about 12:1), ink-soft on paper (about 5:1), teal on paper (about 5.5:1),
oxide on paper (about 7:1), phosphor on night (about 8:1).

## Grid and layout

- **Chrome container** `.wrap`: `max-width: 68rem`, centered, side padding
  `1.25rem` (mobile `0.9rem`).
- **Reading column** `.prose`: `max-width: 66ch`, centered -- the hero figure
  shares the column's width so art and text align to one edge.
- **Card grid** `.cards`: holds the lead card only (D10). The newest card
  `.card-lead` spans all columns with an internal `5fr 4fr` split (art |
  text).
- **Dispatch list** `.dispatch-list`: one `.dispatch-row` per non-lead post,
  `grid-template-columns: 12rem 1fr` (meta | title+dek), dashed hairline
  separators; collapses to one column below `50rem`.
- **Pager**: `grid-template-columns: 1fr auto 1fr` (older | index | newer).
- **Breakpoints**: below `50rem` the lead card stacks art-over-text and cards
  drop to the auto-fill minimum; below `35rem` the pager stacks vertically and
  the masthead shrinks via its clamp().
- Rules: the masthead uses a classic double rule (3px ink over 1px line);
  sections separate with 1px `line` hairlines; period dashed rules are
  reserved for `hr` inside prose (the one deliberate period echo in the
  chrome).

## Component inventory

Class names as implemented in `src/styles.css` and emitted by `pipeline/site.py`:

| Component      | Classes                                                        | Decision |
| -------------- | -------------------------------------------------------------- | -------- |
| Masthead       | `.site-masthead`, `.masthead-kicker/-title/-tagline/-stats`    | D1, D6   |
| Nav            | `.site-nav` (+ `aria-current`)                                 | D5, D9   |
| Subpage head   | `.site-head` (wordmark + nav, compact)                         | D5       |
| Index deck     | `.deck`, `.deck-lede`                                          | D1       |
| Category chips | `.cat-chips`, `.chip`, `.chip-count`                           | D10      |
| Cards          | `.cards`, `.card`, `.card-lead`, `.card-art` (night mat), `.card-body`, `.card-meta`, `.card-cat`, `.card-title`, `.card-dek` | D2, D1, D10 |
| Dispatch list  | `.dispatches`, `.list-head`, `.list-count`, `.dispatch-list`, `.dispatch-row`, `.dispatch-meta`, `.dispatch-body`, `.dispatch-title`, `.dispatch-dek` | D10 |
| Post header    | `.post-head`, `.kicker`, `.post-title`, `.post-dek`, `.post-byline` | D1, D3 |
| Hero figure    | `.hero` (mount + night mat), `figcaption` caption              | D2, D9   |
| Prose          | `.prose` (66ch, drop cap, styled quotes/rules/lists)           | D3       |
| Exhibit labels | `.exhibit`, `.exhibit-title`, `.prov-table`, `.src-list`       | D4       |
| Pager          | `.pager`, `.pager-newer/-home/-older`, `.pager-label`         | D5       |
| Page head      | `.page-head`, `.page-title`, `.page-dek` (about, categories)  | D1       |
| Category group | `.cat-group`, `.cat-name`, `.cat-count`, `.cat-list`           | D5       |
| Footer         | `.site-foot`, `.foot-banner`, `.foot-counter`, `.counter-digits`, `.foot-colophon` | D2, D6 |
| RSS            | `site/rss.xml` (built from `site_config.json` `base_url`)      | D8       |

## Traceability: template elements to decisions

| Template element (builder)                                    | Decision(s) |
| ------------------------------------------------------------- | ----------- |
| Masthead typography + double rules (index)                    | D1, D6      |
| Stats line (dispatches/categories/sources counted at build)   | D6, D4      |
| Nav on every page, `aria-current` marking                     | D5, D9      |
| One card per post, newest first, SVG on `.card-art` mat       | D1, D2, D6  |
| Lead card treatment for the newest post                       | D1, D10     |
| Category chips with counts above the fold (index)             | D10         |
| Complete dispatch list, one compact row per older post        | D10         |
| Categories page groups every post with per-category counts    | D5, D10     |
| Hero figure + plate caption on post pages                     | D2, D9      |
| 66ch `.prose`, drop cap, elided duplicate body H1             | D3          |
| Exhibit-label PROVENANCE / SOURCES boxes                      | D4          |
| Pager with older / all dispatches / newer                     | D5          |
| Exhibit and plate numbers from publication order              | D6          |
| Footer banner + simulated hit counter (post-count formula)    | D2, D6      |
| `styles.css` relative link, no `<script>` anywhere            | D8          |
| `time[datetime]`, `figure/figcaption`, focus styles           | D9          |
| RSS from `base_url` config, deterministic dates               | D6, D8      |

## Dek policy

Cards need a one-line dek. Posts may carry `dek:` front matter (an additive,
presentation-adjacent metadata field; post bodies are frozen). If a post has
no `dek:`, the builder derives a neutral fallback -- "A memorial from the
{category} wing of the archive." -- rather than editing the post. The choice
and the fallback are recorded in RESULT.md.

## Source of truth for the stylesheet

`src/styles.css` is the hand-written source. The build copies it
byte-identically into `site/styles.css` (the path pages link). The copy step
keeps the clean-state guarantee intact: a build into an empty directory
reproduces `site/` exactly, stylesheet included, so the tracked `site/` tree
stays a pure build product.
