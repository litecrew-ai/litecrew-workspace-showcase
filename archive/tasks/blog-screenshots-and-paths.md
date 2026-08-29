---
status: done
goal: operate-internet-archaeology-blog.md
assigned_agent: web-product-engineer
created: 2026-08-29
updated: 2026-08-29
---

# Task: Real screenshots (with honest fallback) and mount-path robustness

## Description

Two user reports drive this Task:

1. **"use real screenshots instead of fake svgs"** — replace (where possible) the
   procedurally generated SVG mini-homepages with real screenshots of the dead
   sites, sourced from the Internet Archive Wayback Machine.
2. **"style missing when i mount the site as relative path like localhost/site/"**
   (and: the production mount path will differ) — the site must work mounted under
   an arbitrary subpath.

Eve's reconnaissance, on the record:

- The built pages already use page-relative refs (`styles.css` from root-level
  pages, `../styles.css` from `posts/`). The reported breakage therefore comes
  from serving context (for example a directory index served without a trailing
  slash, or a production mount that wants prefix-absolute URLs). Do not guess —
  reproduce it: serve the site under a subpath with `python3 -m http.server`
  rooted at the workspace root, fetch `/site/` and a post page the way a browser
  would, and confirm what resolves and what does not before fixing.
- **web.archive.org is unreachable from this environment** (screenshot endpoint
  timed out at 10s on 2026-08-29; CDX and Wikipedia failed in all prior sessions
  too). Real screenshots therefore cannot be fetched here, today. This must not
  become fabricated or fake "real" images — see the rules below.

### Scope A — real screenshots, honestly

1. Implement screenshot support in the pipeline:
   - `python3 run.py --fetch-screenshots` as a standalone, documented step: for
     each post, look up a representative snapshot timestamp (Wayback CDX) for the
     subject's canonical URL, then fetch a screenshot
     (`https://web.archive.org/screenshot/<url>?timestamp=<ts>` is the known
     endpoint; verify its current behavior and record what you find), storing the
     binary under `assets/screenshots/<slug>.<ext>` (source assets; the builder
     copies them into `site/` the same way `src/styles.css` is copied, preserving
     the clean-state byte-identical rebuild).
   - Per-source timeouts, per-subject degradation, and a run record: every fetch
     attempt (success, failure, HTTP code, bytes) lands in RESULT.md.
2. **Illustration mode metadata**: each post's front matter gains
   `illustration: screenshot | generated` plus, for screenshots, source URL,
   snapshot timestamp, and fetch date. The page renders the mode as a visible
   plate label ("Screenshot: Wayback Machine, <date>" vs "Generated memorial
   art"). The about page explains the policy. A generated SVG must never be
   presented as a screenshot.
3. In this environment the fetch will degrade (archive unreachable). Expected
   end state here: capability implemented + all 20 posts still on generated art,
   honestly labeled, with the operator-runnable fetch path documented in README
   and docs/scheduling.md (the fetcher is exactly what the operator or a CI
   runner with wider egress runs later). If the network happens to work during
   the Task, fetch what you can and label it.
4. Binary handling: PNG/JPEG binaries are allowed as screenshot assets. Report
   every binary's size in RESULT.md; the repo's gates cap text files at 100KB
   and the operator must consciously allow binaries — so keep count and sizes
   minimal, and Eve will flag the gate question to the operator. (Stdlib cannot
   resize images; no attempt to game the gate by base64-wrapping binaries into
   text files.)

### Scope B — mount-path robustness

1. Add `path_prefix` to `site_config.json` (default `""` = current page-relative
   behavior). When set (e.g. `/site/` or `/gazette/`), all internal hrefs/srcs
   emit prefix-absolute URLs (`/gazette/styles.css`), and RSS item links combine
   `base_url` + prefix. Documented in README for production mounts.
2. Audit every internal reference at every directory depth: stylesheets, nav,
   post links, pager, categories anchors, rss link, any `url()` inside
   `styles.css`, favicon if any. No page may reference an asset that 404s under
   either mode.
3. Extend `run.py --verify` with a **mounted-subpath server test**: start
   `http.server` on an ephemeral port rooted at the workspace root, request
   `<prefix>/site/` (and a post page) as a browser would, follow the stylesheet
   reference, assert HTTP 200 for each asset. This reproduces the user's exact
   failure mode and must pass in BOTH modes (relative default and a prefix
   configured for the test). Record the method and results in RESULT.md.

## Completion criteria

- [x] `--fetch-screenshots` implemented and attempted for all 20 subjects; every
      attempt's outcome recorded in RESULT.md; degraded state here documented
      (or screenshots fetched and stored, if the network permitted).
      (Run 2026-08-29: 20/20 attempted against real canonical URLs; CDX and
      screenshot endpoint both failed per subject with `Errno 101 Network is
      unreachable`; 0 stored; 20 degraded; every attempt a log line.)
- [x] Illustration mode in front matter + visible plate labels on every post;
      about page states the policy; zero mislabeled art.
      (All 20 posts carry `illustration: generated`; every plate prints
      "generated memorial art"; about has the policy section; verify asserts
      FM/label/art/binary agreement both ways.)
- [x] `path_prefix` config implemented and documented; every internal reference
      audited at both depths; no 404ing asset refs in either mode.
      (Single `_url` resolver covers nav, wordmark, stylesheet, category
      anchors, post/card/row/pager links, deck link, rss link, screenshot
      img; styles.css has no `url()` and there is no favicon; 34/34 internal
      refs prefix-absolute in a prefix-mode scratch build; mounted HTTP test
      green in both modes.)
- [x] `run.py --verify` includes the mounted-subpath server test and passes in
      both modes; all previous checks stay green; clean-state rebuild stays
      byte-identical (screenshots, if any, stored as source assets the builder
      copies).
      (Final run: ALL CHECKS PASS, 392 checks, including mode A (31 refs 200
      under /artifacts/writing/internet-archaeology-blog/site/) and mode B
      (/site/ prefix build, 31 refs 200, rss = base_url + prefix);
      clean-state rebuild byte-identical.)
- [x] Screenshot binaries (if any) individually size-reported; none disguised as
      text; RESULT.md carries the size report.
      (0 binaries stored; "binary asset size report: no screenshot binaries
      stored" logged by the fetch run and by verify; binary gate added.)
- [x] docs/design.md updated (real-screenshot mount decision + label
      component); README and docs/scheduling.md updated (path_prefix, the
      operator-runnable screenshot fetch); knowledge merged per sediment
      protocol with INDEX in sync.
      (design.md D11 + inventory/traceability rows; README quick start,
      architecture, mounting note, illustration section, limitations;
      scheduling.md cron + CI fetch steps; knowledge merged into
      knowledge/writing/post-generation-pipeline.md, INDEX purpose updated.)
- [x] Usual content rules: English; ASCII-safe text; no emoji; no check-mark
      glyphs (U+2713, U+2714, U+2705, U+2611 family); no text file over 100KB;
      stdlib only; no git; no network beyond the established keyless APIs.
      (Glyph/size gates green across the tree; RESULT.md at 91.9KB after the
      runs; stdlib only; zero git commands; network touched only
      web.archive.org keyless endpoints and 127.0.0.1 loopback.)

## Context and constraints

- **Write boundaries**: this Task file; `artifacts/writing/internet-archaeology-blog/`;
  `knowledge/writing/`. Nothing else. No git commands; no `.github/` changes.
- **Truthfulness law (load-bearing for images)**: a "real screenshot" is bytes
  actually fetched from the archive of the actual subject URL, with provenance
  recorded. Anything else is `generated` and labeled as such. No intermediate
  states, no mockups-as-screenshots.
- Fastest context load: artifact README + RESULT.md, `docs/design.md`,
  `run.py`, `pipeline/site.py`, `knowledge/writing/post-generation-pipeline.md`,
  the three archived Task records.
- The 20 published post bodies remain untouched (additive front-matter fields
  only). The 3 v0 posts and the 17 batch posts are all frozen prose.

## Preparation (retrieval summary, 2026-08-29)

- Handbooks: none exist yet (only `handbooks/README.md`; `development.md` is
  backlog). Relevant standing knowledge: `knowledge/writing/post-generation-pipeline.md`
  (determinism, never-clobber, verifier patterns), `dead-web-source-catalog.md`
  (keyless API reachability split), INDEX in sync.
- Artifact context loaded: README, RESULT.md tail (286-check verify green),
  `run.py`, `pipeline/site.py`, `pipeline/util.py`, `docs/design.md` (D1-D10),
  `docs/scheduling.md`, `site_config.json`, seed corpus (20 subjects, each with
  a canonical `domain`), sample post front matter.
- Reference-audit surface confirmed: nav (4 links), wordmark, stylesheet link
  (`_page` depth arg), category anchors, post links (cards/rows/categories/pager),
  rss link. `src/styles.css` contains **no `url()`** rules; no favicon; no
  `<img>` anywhere today (all art is inline SVG).
- Network probe (2026-08-29, this session): web.archive.org screenshot and CDX
  endpoints both fail at the connection level (`Errno 101 Network is unreachable`,
  ~8s); HN Algolia answers 200. Matches Eve's recon: Scope A will run fully
  degraded here; the fetcher ships as the operator-runnable path.

## Execution steps

<!-- Subagent fills -->

1. Reproduce the mount-path report before fixing: serve the workspace root with
   `http.server`, browse `/artifacts/writing/internet-archaeology-blog/site/`
   (and a post page) the way a browser would; record what resolves.
2. Scope B: `path_prefix` in `site_config.json` + prefix-aware URL emission in
   `pipeline/site.py` (all internal refs); RSS links = base_url + prefix.
3. Scope B: extend `run.py --verify` with the mounted-subpath server test in
   both modes (default relative; a scratch build configured with a prefix).
4. Scope A: `pipeline/screenshots.py` (CDX timestamp lookup + screenshot fetch,
   per-attempt logging), `util.fetch_bytes`, front-matter additive editor
   (`illustration` + screenshot provenance fields; bodies untouched).
5. Scope A: builder renders screenshot or generated art with visible plate
   labels; provenance box gains an Illustration row; about page states the
   policy; verify guards against mislabeling.
6. Run `--fetch-screenshots` for all 20 subjects (expected: all degrade here),
   add `illustration: generated` front matter, rebuild, full `--verify`.
7. Docs: README (path_prefix, fetch step), docs/scheduling.md (operator/CI
   screenshot fetch), docs/design.md (D11 mount + label decision).
8. Knowledge capture per sediment protocol; INDEX in sync; conclusions.

## Execution log

<!-- Append after each subagent iteration -->

| Round | Date       | Progress | Notes |
| ----- | ---------- | -------- | ----- |
| 1 | 2026-08-29 | Retrieval + plan; network probe; audit surface mapped | web.archive.org unreachable (Errno 101) as expected; HN Algolia live; no url()/favicon refs in CSS or pages |
| 2 | 2026-08-29 | Path-bug reproduction (pre-fix, stdlib http.server at workspace root) | With trailing slash, the tracked page-relative site serves 100% clean under `/artifacts/.../site/` (42/42 internal refs 200, stylesheet 200); `/site` (no slash) is 301-redirected properly; the reproducible failure is root-absolute refs (`/styles.css` -> 404). Conclusion: report is consistent with a server serving `/site` without the slash-redirect; fix = `path_prefix` + mounted verify in both modes |
| 3 | 2026-08-29 | Scope B implemented: `path_prefix` config + single `_url` resolver in site.py (all internal refs), RSS = base_url+prefix; scratch-build probe shows 34/34 internal refs prefix-absolute under `/site/` | default mode output unchanged (page-relative, file:// safe) |
| 4 | 2026-08-29 | Scope A implemented: `pipeline/screenshots.py` (CDX earliest-200 lookup, screenshot endpoint fetch, magic-byte image sniffing, additive front-matter editor with body-sha256 post-condition), `util.fetch_bytes`, builder art_for/plate labels/provenance row/about policy, drafts now carry `illustration: generated`, CSS for screenshot mats | zero-mislabel guards added to --verify |
| 5 | 2026-08-29 | `run.py --fetch-screenshots` mode + verify extensions (illustration mode agreement, orphan-binary guard, binary-aware gates with size report, mounted-subpath HTTP test in both modes); docs updated (README, design D11, scheduling) | fetch run in progress; expected full degradation |
| 6 | 2026-08-29 | Fetch executed: 20/20 subjects attempted, 0 stored (Errno 101 both endpoints, every attempt logged), 20 degraded to labeled generated art, bodies sha256-identical after additive front matter | full degradation as predicted; `assets/screenshots/` intentionally not created (nothing to store) |
| 7 | 2026-08-29 | Verify: ALL CHECKS PASS (392 checks) incl. both mounted-subpath modes; scratch-dir test of the screenshot rendering path (synthetic PNG in /tmp only) also all-pass; RESULT.md condensed verify records introduced to stay under the 100KB gate (91.9KB) | screenshot code paths verified without fabricating any artifact |

## Conclusions and output

### What was implemented

**Scope A -- real screenshots, honestly (capability shipped; degraded here).**

- New `pipeline/screenshots.py`: canonical URL from the seed-corpus domain;
  Wayback CDX lookup of the representative snapshot (defined as the earliest
  status-200 capture of the exact canonical URL); screenshot fetch from
  `https://web.archive.org/screenshot/<url>?timestamp=<ts>`; magic-byte image
  sniffing (an HTML error page with HTTP 200 is a failure, not a screenshot);
  never-clobber storage under `assets/screenshots/<slug>.{png,jpg}`; an
  additive-only front-matter editor with a hard body-sha256 post-condition.
- `python3 run.py --fetch-screenshots` (documented in README quick start,
  cron, and the CI sample): one line per subject in RESULT.md with both
  endpoint outcomes, a binary size report when anything is stored, an
  automatic rebuild, and non-zero exit if any post body changed.
- Illustration mode metadata: every post now carries `illustration: generated`
  (screenshots would carry `screenshot` plus `screenshot_url`,
  `screenshot_timestamp`, `screenshot_fetched`). Pages print a visible plate
  label ("generated memorial art: ..." or "screenshot: Wayback Machine,
  snapshot <ts>, fetched <date>"), the PROVENANCE box gains an Illustration
  row (plus "Screenshot of" for screenshots), and about.html states the
  policy. New drafts from `writing.py` ship with `illustration: generated`.
- Render-time guard: `illustration: screenshot` renders an img only when the
  binary actually exists; otherwise it degrades to the generated SVG labeled
  generated. A generated plate can never be presented as a screenshot.

**Scope B -- mount-path robustness.**

- `path_prefix` in `site_config.json` (default `""` = byte-compatible
  page-relative behavior). One `_url()` resolver in `pipeline/site.py` now
  emits every internal reference (nav, wordmark, stylesheet link, category
  anchors, post/card/row/pager links, deck link, rss link, screenshot img);
  when a prefix is set, refs are prefix-absolute from every depth and RSS
  links are `base_url + prefix`. `src/styles.css` contains no `url()` and
  there is no favicon, so the audit surface is closed. Verified in a scratch
  prefix build: 34/34 internal refs prefix-absolute.
- `run.py --verify` gained a mounted-subpath server test: stdlib
  `http.server` on 127.0.0.1 ephemeral port; mode A browses the tracked
  default build at its real workspace subpath; mode B builds a scratch
  `/site/`-prefixed site in a temp root and browses it there, also asserting
  no non-prefixed internal ref survives and rss links join correctly. Both
  modes fetch every internal href/src the way a browser would.

### The path-bug reproduction (asked-for finding)

Reproduced before any fix, stdlib http.server rooted at the workspace root:

- `GET .../site` (no trailing slash) -> HTTP 301 to the slash form; a browser
  follows it. With the slash form, the tracked page-relative site serves
  completely clean under the subpath: stylesheet 200, and every one of the
  42 distinct internal references on the index + a post page returned 200.
- The failure that does reproduce under a subpath mount is any root-absolute
  reference: `GET /styles.css` -> 404. Page-relative refs degrade into
  exactly that when a server serves `/site` without the trailing-slash
  redirect (some rewrites/static hosts do).
- Conclusion (recorded in README + RESULT.md): the reported "style missing
  under localhost/site/" is a serving-context failure, not a bug in the
  emitted refs; conforming servers were never broken. The robust fix is the
  `path_prefix` mode for servers that need prefix-absolute URLs, plus the
  mounted verify that now proves both modes over real HTTP on every run.

### Fetched versus degraded (truthfulness record)

- 2026-08-29 fetch run: 20/20 subjects attempted against their real canonical
  URLs (from seed-corpus domains). Both the CDX and the screenshot endpoint
  failed for every subject with `Errno 101 Network is unreachable` (~5s/~10s
  timeouts). 0 binaries stored; all 20 posts degraded to (and remain on)
  generated plates, visibly labeled; front matter applied additively; post
  bodies verified byte-identical by sha256 before/after.
- The rendering path for real screenshots was verified in a scratch dir with
  a synthetic PNG (never in the artifact tree): img rendering in both modes,
  label, provenance rows, byte-identical copy into `site/assets`, and the
  missing-binary honest fallback all pass. Nothing was fabricated: the
  tracked tree contains zero images.

### Verified versus assumed

- Verified: 392-check verify ALL PASS (both mounted modes included);
  clean-state rebuild byte-identical; post bodies unchanged (sha256, in-run
  assertion + spot reads); scratch screenshot-path test; prefix emission
  (34/34 refs); RSS join in prefix mode; about policy renders; RESULT.md
  under the size gate (91.9KB).
- Assumed / not verifiable here: that the Wayback screenshot endpoint behaves
  as documented for real traffic (unreachable from this network; its HTTP
  contract was never observed live this session); that the earliest-200 CDX
  capture is the most "representative" look (a defensible editorial choice,
  documented, single knob to change); pixel-level rendering still
  not eyeballed (standing limitation, now partially covered by the HTTP
  browse test, which does confirm the stylesheet is served and linked).

### Limitations / decisions for Eve

- RESULT.md headroom: 91.9KB of the 100KB gate. Verify now appends condensed
  records (~1.2KB/run) instead of 300-line listings (noted inside the log
  entries). Roughly 6-8 more verify/fetch runs fit; suggest archiving the
  three historical "Verification record" sections into the artifact docs or
  letting Eve rotate the file in a future Task.
- Binary-gate policy for the operator (Task anticipated this): png/jpg under
  `assets/screenshots/` + `site/assets/` are exempt from the 100KB text gate
  and size-reported everywhere; anything else binary fails. If the operator
  wants a hard byte cap per screenshot (e.g. 2MB), that is a one-line change
  in run.py -- flagging as an Eve/operator decision.
- Canonical URL scheme is `http://<seed domain>`; some subjects (e.g.
  `plus.google.com`) may have better-represented https captures -- the CDX
  lookup will simply find whatever exists for the exact URL; operator can
  adjust `domain` values in the seed corpus without code changes.

### Artifacts touched (all inside the allowed boundary)

- Code: `run.py`, `pipeline/site.py`, `pipeline/screenshots.py` (new),
  `pipeline/util.py`, `pipeline/writing.py`, `src/styles.css`.
- Config: `site_config.json` (+`path_prefix`).
- Content: 20 post files (additive `illustration: generated` only; bodies
  untouched); `site/` rebuilt (deterministic).
- Docs: `README.md`, `docs/design.md` (D11), `docs/scheduling.md`, plus
  RESULT.md run records.

## Knowledge-capture suggestions

Captured during this run (merge-over-create, per sediment protocol):

- `knowledge/writing/post-generation-pipeline.md` -- two new sections:
  "Truthful images: real screenshots versus generated art" (two-mode
  labeling, magic-byte payload sniffing, per-subject degradation,
  additive-only front matter with a body-hash post-condition, binary/text
  gate split) and "Subpath mount robustness" (reproduce-first diagnosis of
  the no-slash redirect trap, single URL resolver with path_prefix,
  mounted-subpath HTTP browse test inside verify). Reuse checklist extended
  with two items; change history row added.
- `knowledge/writing/INDEX.md` -- purpose line for the pipeline note updated
  to cover the new sections (no new knowledge files created).

Suggested for Eve (not done by me, outside my boundary):

- `knowledge/writing/dead-web-source-catalog.md` could take a one-line merge:
  this session probed the Wayback screenshot endpoint itself (Errno 101
  after timeout), complementing the catalog's existing reachability record.
- Handbook backlog: the planned "verify what you publish" handbook section
  could cite the mounted-subpath test and the image-truthfulness gates as
  default exit criteria for any Task producing a generated site.
