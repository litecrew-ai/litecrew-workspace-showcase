# Run log

One entry per pipeline invocation. Modes and verification results
are recorded honestly, including failures and degradations.

## Verification record (v0, 2026-08-29)

Data-source mode of the v0 runs: HN Algolia live; Wikipedia API and Wayback
CDX unreachable from this environment (connection-level failure, recorded per
run below); seed corpus always the factual base; every post's front matter
carries its exact mode string.

How the built site was verified (methods, then results):

1. `python3 run.py --verify` -- automated checks over `site/` and the whole
   artifact tree: index lists every post; per-post page exists, contains an
   inline `<svg>`, a PROVENANCE box, and a SOURCES box; word count >= 400;
   every internal href/src resolves to an existing file (file:// renderability
   proxy); every HTML file parses with balanced tags (stdlib html.parser with
   a tag-stack checker); SVG regeneration is byte-identical to the stored
   asset (determinism); glyph gate (pure ASCII, no emoji, no check-mark
   codepoints) and size gate (no text file over 100KB) across every text file.
   Final result: ALL CHECKS PASS (see the last verify entry). Two earlier
   verify entries record genuine failures that were then fixed (about page
   home link missing; verifier calling the SVG generator with a different
   subtitle than the builder -- a verifier bug, not an artwork bug).
2. Clean-state build -- `site.build_site()` into an empty scratch directory
   produced output byte-identical to the tracked `site/` (verified with
   `diff -r`), proving the site builds from a clean state and deterministically.
3. Dedup ledger -- a second pipeline pass with `--posts 0` against an
   11-subject ledger: candidates 20, skipped (in ledger) 11, new drafts 0.
   The same behavior is visible across the earlier runs as coverage grew
   (3 skipped on the second run).
4. SVG XML well-formedness -- every standalone asset and every inline SVG
   fragment in the built HTML parsed with stdlib ElementTree: all OK
   (200 elements per post illustration).
5. Rendering in a real browser -- a browser session navigated to
   `site/index.html` via file:// successfully, but the screenshot and DOM
   extraction tooling failed in this environment (CDP client not
   initialized), so pixel-level rendering was NOT verified by eye. Rendering
   confidence rests on items 1, 2, and 4 plus the fact that the pages use
   only standard inline SVG 1.1 shapes, relative links, and inline CSS with
   no scripts.

Honesty notes:

- One intermediate pipeline invocation crashed before writing a run entry
  (a fetched HN title contained an en dash and the glyph guard aborted the
  draft). The ingestion path now ASCII-folds fetched text; the crash is
  recorded here because it left no entry below.
- Facts in posts trace to the seed corpus (canonical URLs listed per post)
  and to live HN Algolia API responses (thread title, date, points, URL,
  each stored in `data/facts/<slug>.json`). Medium-confidence facts appear
  hedged. No statistic in any post was invented.

### Run 2026-08-29 15:15:14

- mode: pipeline (max 3 new subject(s) this run)
- sources: {'hn_algolia': 'live', 'wikipedia': 'offline (URL error ([Errno 101] Network is unreachable) from en.wikipedia.org)', 'wayback_cdx': 'offline (URL error ([Errno 101] Network is unreachable) from web.archive.org)'}
- candidates: 20; skipped (in ledger): 0 [none]
- new drafts: 3 [google-reader, delicious, winamp]
- site rebuilt: 0 published post(s) [none]
- editorial pass: drafts await a human pass in content/drafts/ (publish by writing content/posts/<slug>.md, then re-run or use --rebuild-only)

### Run 2026-08-29 15:17:43

- mode: pipeline (max 8 new subject(s) this run)
- sources: {'hn_algolia': 'live', 'wikipedia': 'offline (URL error ([Errno 101] Network is unreachable) from en.wikipedia.org)', 'wayback_cdx': 'offline (URL error ([Errno 101] Network is unreachable) from web.archive.org)'}
- candidates: 20; skipped (in ledger): 3 [google-reader, delicious, winamp]
- new drafts: 8 [aim, google-plus, geocities, napster, friendster, msn-messenger, altavista, myspace]
- site rebuilt: 0 published post(s) [none]
- editorial pass: drafts await a human pass in content/drafts/ (publish by writing content/posts/<slug>.md, then re-run or use --rebuild-only)

### Run 2026-08-29 15:21:05

- mode: rebuild-only; site rebuilt with 3 post(s) [winamp, google-reader, geocities]

### Run 2026-08-29 15:21:05

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index links post google-reader
- PASS - index links post winamp
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- FAIL - about links index
- PASS - all internal links resolve
- FAIL - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: FAILURES: about links index, svg deterministic for geocities

### Run 2026-08-29 15:21:36

- mode: rebuild-only; site rebuilt with 3 post(s) [winamp, google-reader, geocities]

### Run 2026-08-29 15:21:36

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index links post google-reader
- PASS - index links post winamp
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - all internal links resolve
- PASS - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 15:22:23

- mode: rebuild-only; site rebuilt with 3 post(s) [winamp, google-reader, geocities]

### Run 2026-08-29 15:22:23

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index links post google-reader
- PASS - index links post winamp
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 15:23:07

- mode: pipeline (max 0 new subject(s) this run)
- sources: {'hn_algolia': 'live', 'wikipedia': 'offline (URL error ([Errno 101] Network is unreachable) from en.wikipedia.org)', 'wayback_cdx': 'offline (URL error ([Errno 101] Network is unreachable) from web.archive.org)'}
- candidates: 20; skipped (in ledger): 11 [google-reader, delicious, winamp, aim, google-plus, geocities, napster, friendster, msn-messenger, altavista, myspace]
- new drafts: 0 [none]
- site rebuilt: 3 published post(s) [winamp, google-reader, geocities]

### Run 2026-08-29 15:33:29

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index links post google-reader
- PASS - index links post winamp
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 15:48:33

- mode: pipeline (max 1 new subject(s) this run)
- sources: {'hn_algolia': 'live', 'wikipedia': 'offline (URL error ([Errno 101] Network is unreachable) from en.wikipedia.org)', 'wayback_cdx': 'offline (URL error ([Errno 101] Network is unreachable) from web.archive.org)'}
- candidates: 20; skipped (in ledger): 11 [google-reader, delicious, winamp, aim, google-plus, geocities, napster, friendster, msn-messenger, altavista, myspace]
- new drafts: 1 [stumbleupon]
- site rebuilt: 3 published post(s) [winamp, google-reader, geocities]
- editorial pass: drafts await a human pass in content/drafts/ (publish by writing content/posts/<slug>.md, then re-run or use --rebuild-only)

## Verification record (design overhaul, 2026-08-29)

Task `blog-design-overhaul`: presentation-layer redesign ("museum of the
early web", brief in docs/design.md). No post body was rewritten; the only
content/ edit is the additive `dek:` front-matter field on the three
published posts.

Dek choice (per Task): front-matter `dek:` written per post; posts without
one get a build-time fallback ("A memorial from the {category} wing of the
archive."). Bodies proven untouched by sha256 of the body region before and
after the edit (all three unchanged).

How the redesign was verified (methods, then results):

1. `python3 run.py --rebuild-only` + `python3 run.py --verify` (several
   rounds; see the run entries below). New checks beyond the v0 set: index
   card count equals post count; card order is newest first; every card's
   thumbnail link resolves; hero figure on every post page; pager and
   back-to-index present; categories page exists and lists every post;
   site/styles.css exists, is a byte-identical copy of src/styles.css, is
   linked from every page, resolves relative to each page, and passes a
   brace-balance lint; no `<script>` in any built page; rss.xml parses as
   XML and lists every published post; base_url configured as an absolute
   http URL; clean-state rebuild into a scratch directory is byte-identical
   to the tracked site/ (file set and bytes, now automated inside --verify
   instead of a manual diff); per-post sources box lists all front-matter
   source URLs. Final result: ALL CHECKS PASS (63 PASS lines).
2. Real defect found and fixed during the redesign: the front-matter list
   parser dropped every `- ` source item (a freshly opened list is empty
   and therefore falsy, so the `and current_list` guard never fired). All
   v0 SOURCES boxes had shipped "(no sources recorded)". The index stats
   line ("0 sources cited") exposed it; fixed with an `is not None` check
   and locked in with the per-post sources-render regression guard above.
3. Browser check: navigation to site/index.html via file:// succeeded, but
   every content-extraction path failed in this environment (screenshot and
   get_html: "Root CDP client not initialized"; get_state: no handler
   returned a result; extract_content: no LLM key configured). Same
   breakage class as v0. Pixel-level rendering was therefore NOT verified
   by eye; rendering confidence rests on the structural checks (HTML tag
   balance, internal link resolution, stylesheet link resolution plus
   brace lint, SVG XML parse, script-free pages, standard CSS only).

Design-iteration honesty note: the first rebuilt index passed all automated
checks but showed "0 sources cited" (defect above) and a masthead double
rule with an over-wide gap; both were corrected before the final verify.
The intermediate verify entries below record those rounds.

### Run 2026-08-29 16:04:34

- mode: rebuild-only; site rebuilt with 3 post(s) [winamp, google-reader, geocities]

### Run 2026-08-29 16:04:34

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index card thumbnail links geocities
- PASS - index links post google-reader
- PASS - index card thumbnail links google-reader
- PASS - index links post winamp
- PASS - index card thumbnail links winamp
- PASS - index card count equals post count (3 cards / 3 posts)
- PASS - index card order is newest first
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: hero figure present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: pager present
- PASS - geocities: back-to-index present
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: hero figure present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: pager present
- PASS - google-reader: back-to-index present
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: hero figure present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: pager present
- PASS - winamp: back-to-index present
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - about links categories
- PASS - categories.html exists
- PASS - categories links index
- PASS - categories lists post geocities
- PASS - categories lists post google-reader
- PASS - categories lists post winamp
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - site/styles.css exists
- PASS - site/styles.css is a byte-identical copy of src/styles.css
- PASS - styles.css resolves from every page
- PASS - no scripts in built pages
- PASS - rss.xml parses and lists every published post (3 items)
- PASS - base_url configured (absolute http url, no trailing slash) (https://example.org/dead-web-gazette)
- PASS - clean-state rebuild byte-identical to tracked site (byte-identical)
- PASS - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 16:05:31

- mode: rebuild-only; site rebuilt with 3 post(s) [winamp, google-reader, geocities]

### Run 2026-08-29 16:05:31

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index card thumbnail links geocities
- PASS - index links post google-reader
- PASS - index card thumbnail links google-reader
- PASS - index links post winamp
- PASS - index card thumbnail links winamp
- PASS - index card count equals post count (3 cards / 3 posts)
- PASS - index card order is newest first
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: hero figure present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: pager present
- PASS - geocities: back-to-index present
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: hero figure present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: pager present
- PASS - google-reader: back-to-index present
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: hero figure present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: pager present
- PASS - winamp: back-to-index present
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - about links categories
- PASS - categories.html exists
- PASS - categories links index
- PASS - categories lists post geocities
- PASS - categories lists post google-reader
- PASS - categories lists post winamp
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - site/styles.css exists
- PASS - site/styles.css is a byte-identical copy of src/styles.css
- PASS - styles.css resolves from every page
- PASS - no scripts in built pages
- PASS - rss.xml parses and lists every published post (3 items)
- PASS - base_url configured (absolute http url, no trailing slash) (https://example.org/dead-web-gazette)
- PASS - clean-state rebuild byte-identical to tracked site (byte-identical)
- PASS - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 16:05:51

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index card thumbnail links geocities
- PASS - index links post google-reader
- PASS - index card thumbnail links google-reader
- PASS - index links post winamp
- PASS - index card thumbnail links winamp
- PASS - index card count equals post count (3 cards / 3 posts)
- PASS - index card order is newest first
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: hero figure present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: pager present
- PASS - geocities: back-to-index present
- PASS - geocities: sources box lists all 5 front-matter sources
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: hero figure present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: pager present
- PASS - google-reader: back-to-index present
- PASS - google-reader: sources box lists all 4 front-matter sources
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: hero figure present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: pager present
- PASS - winamp: back-to-index present
- PASS - winamp: sources box lists all 2 front-matter sources
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - about links categories
- PASS - categories.html exists
- PASS - categories links index
- PASS - categories lists post geocities
- PASS - categories lists post google-reader
- PASS - categories lists post winamp
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - site/styles.css exists
- PASS - site/styles.css is a byte-identical copy of src/styles.css
- PASS - styles.css resolves from every page
- PASS - no scripts in built pages
- PASS - rss.xml parses and lists every published post (3 items)
- PASS - base_url configured (absolute http url, no trailing slash) (https://example.org/dead-web-gazette)
- PASS - clean-state rebuild byte-identical to tracked site (byte-identical)
- PASS - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 16:07:11

- mode: rebuild-only; site rebuilt with 3 post(s) [winamp, google-reader, geocities]

### Run 2026-08-29 16:07:12

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index card thumbnail links geocities
- PASS - index links post google-reader
- PASS - index card thumbnail links google-reader
- PASS - index links post winamp
- PASS - index card thumbnail links winamp
- PASS - index card count equals post count (3 cards / 3 posts)
- PASS - index card order is newest first
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: hero figure present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: pager present
- PASS - geocities: back-to-index present
- PASS - geocities: sources box lists all 5 front-matter sources
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: hero figure present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: pager present
- PASS - google-reader: back-to-index present
- PASS - google-reader: sources box lists all 4 front-matter sources
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: hero figure present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: pager present
- PASS - winamp: back-to-index present
- PASS - winamp: sources box lists all 2 front-matter sources
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - about links categories
- PASS - categories.html exists
- PASS - categories links index
- PASS - categories lists post geocities
- PASS - categories lists post google-reader
- PASS - categories lists post winamp
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - site/styles.css exists
- PASS - site/styles.css is a byte-identical copy of src/styles.css
- PASS - styles.css resolves from every page
- PASS - styles.css braces balanced (truncation lint) (open-minus-close: 0)
- PASS - no scripts in built pages
- PASS - rss.xml parses and lists every published post (3 items)
- PASS - base_url configured (absolute http url, no trailing slash) (https://example.org/dead-web-gazette)
- PASS - clean-state rebuild byte-identical to tracked site (byte-identical)
- PASS - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 16:07:12

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index card thumbnail links geocities
- PASS - index links post google-reader
- PASS - index card thumbnail links google-reader
- PASS - index links post winamp
- PASS - index card thumbnail links winamp
- PASS - index card count equals post count (3 cards / 3 posts)
- PASS - index card order is newest first
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: hero figure present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: pager present
- PASS - geocities: back-to-index present
- PASS - geocities: sources box lists all 5 front-matter sources
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: hero figure present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: pager present
- PASS - google-reader: back-to-index present
- PASS - google-reader: sources box lists all 4 front-matter sources
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: hero figure present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: pager present
- PASS - winamp: back-to-index present
- PASS - winamp: sources box lists all 2 front-matter sources
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - about links categories
- PASS - categories.html exists
- PASS - categories links index
- PASS - categories lists post geocities
- PASS - categories lists post google-reader
- PASS - categories lists post winamp
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - site/styles.css exists
- PASS - site/styles.css is a byte-identical copy of src/styles.css
- PASS - styles.css resolves from every page
- PASS - styles.css braces balanced (truncation lint) (open-minus-close: 0)
- PASS - no scripts in built pages
- PASS - rss.xml parses and lists every published post (3 items)
- PASS - base_url configured (absolute http url, no trailing slash) (https://example.org/dead-web-gazette)
- PASS - clean-state rebuild byte-identical to tracked site (byte-identical)
- PASS - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 16:10:04

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index card thumbnail links geocities
- PASS - index links post google-reader
- PASS - index card thumbnail links google-reader
- PASS - index links post winamp
- PASS - index card thumbnail links winamp
- PASS - index card count equals post count (3 cards / 3 posts)
- PASS - index card order is newest first
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: hero figure present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: pager present
- PASS - geocities: back-to-index present
- PASS - geocities: sources box lists all 5 front-matter sources
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: hero figure present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: pager present
- PASS - google-reader: back-to-index present
- PASS - google-reader: sources box lists all 4 front-matter sources
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: hero figure present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: pager present
- PASS - winamp: back-to-index present
- PASS - winamp: sources box lists all 2 front-matter sources
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - about links categories
- PASS - categories.html exists
- PASS - categories links index
- PASS - categories lists post geocities
- PASS - categories lists post google-reader
- PASS - categories lists post winamp
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - site/styles.css exists
- PASS - site/styles.css is a byte-identical copy of src/styles.css
- PASS - styles.css resolves from every page
- PASS - styles.css braces balanced (truncation lint) (open-minus-close: 0)
- PASS - no scripts in built pages
- PASS - rss.xml parses and lists every published post (3 items)
- PASS - base_url configured (absolute http url, no trailing slash) (https://example.org/dead-web-gazette)
- PASS - clean-state rebuild byte-identical to tracked site (byte-identical)
- PASS - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 16:11:34

- mode: rebuild-only; site rebuilt with 3 post(s) [winamp, google-reader, geocities]

### Run 2026-08-29 16:11:34

- mode: verify
- PASS - site/index.html exists
- PASS - index links post geocities
- PASS - index card thumbnail links geocities
- PASS - index links post google-reader
- PASS - index card thumbnail links google-reader
- PASS - index links post winamp
- PASS - index card thumbnail links winamp
- PASS - index card count equals post count (3 cards / 3 posts)
- PASS - index card order is newest first
- posts discovered: 3 [geocities, google-reader, winamp]
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: hero figure present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: pager present
- PASS - geocities: back-to-index present
- PASS - geocities: sources box lists all 5 front-matter sources
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: hero figure present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: pager present
- PASS - google-reader: back-to-index present
- PASS - google-reader: sources box lists all 4 front-matter sources
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: hero figure present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: pager present
- PASS - winamp: back-to-index present
- PASS - winamp: sources box lists all 2 front-matter sources
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - about links categories
- PASS - categories.html exists
- PASS - categories links index
- PASS - categories lists post geocities
- PASS - categories lists post google-reader
- PASS - categories lists post winamp
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - site/styles.css exists
- PASS - site/styles.css is a byte-identical copy of src/styles.css
- PASS - styles.css resolves from every page
- PASS - styles.css braces balanced (truncation lint) (open-minus-close: 0)
- PASS - no scripts in built pages
- PASS - rss.xml parses and lists every published post (3 items)
- PASS - base_url configured (absolute http url, no trailing slash) (https://example.org/dead-web-gazette)
- PASS - clean-state rebuild byte-identical to tracked site (byte-identical)
- PASS - svg deterministic for geocities
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers geocities
- PASS - ledger covers google-reader
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 16:33:48

- mode: pipeline (max 9 new subject(s) this run)
- sources: {'hn_algolia': 'live', 'wikipedia': 'offline (URL error (_ssl.c:975: The handshake operation timed out) from en.wikipedia.org)', 'wayback_cdx': 'offline (URL error ([Errno 101] Network is unreachable) from web.archive.org)'}
- candidates: 20; skipped (in ledger): 12 [google-reader, delicious, winamp, aim, google-plus, geocities, napster, friendster, msn-messenger, altavista, myspace, stumbleupon]
- new drafts: 8 [digg, posterous, pets-com, etoys, vine, somethingawful, newgrounds, cuil]
- site rebuilt: 3 published post(s) [winamp, google-reader, geocities]
- editorial pass: drafts await a human pass in content/drafts/ (publish by writing content/posts/<slug>.md, then re-run or use --rebuild-only)

### Run 2026-08-29 16:47:45

- mode: rebuild-only; site rebuilt with 20 post(s) [winamp, vine, stumbleupon, somethingawful, posterous, pets-com, newgrounds, napster, myspace, msn-messenger, google-reader, google-plus, geocities, friendster, etoys, digg, delicious, cuil, altavista, aim]

### Run 2026-08-29 16:47:52

- mode: verify
- PASS - site/index.html exists
- PASS - index links post aim
- PASS - index links post altavista
- PASS - index links post cuil
- PASS - index links post delicious
- PASS - index links post digg
- PASS - index links post etoys
- PASS - index links post friendster
- PASS - index links post geocities
- PASS - index links post google-plus
- PASS - index links post google-reader
- PASS - index links post msn-messenger
- PASS - index links post myspace
- PASS - index links post napster
- PASS - index links post newgrounds
- PASS - index links post pets-com
- PASS - index links post posterous
- PASS - index links post somethingawful
- PASS - index links post stumbleupon
- PASS - index links post vine
- PASS - index links post winamp
- PASS - index lead card count is one (1 lead card(s))
- PASS - index lead card is the newest post (expected winamp)
- PASS - index dispatch rows cover the remaining posts (19 rows / 19 non-lead posts)
- PASS - index order is newest first
- PASS - index category chips with counts (one per category) (9 categories)
- posts discovered: 20 [aim, altavista, cuil, delicious, digg, etoys, friendster, geocities, google-plus, google-reader, msn-messenger, myspace, napster, newgrounds, pets-com, posterous, somethingawful, stumbleupon, vine, winamp]
- PASS - page exists for aim
- PASS - aim: inline <svg> present
- PASS - aim: hero figure present
- PASS - aim: provenance box present
- PASS - aim: sources box present
- PASS - aim: pager present
- PASS - aim: back-to-index present
- PASS - aim: sources box lists all 2 front-matter sources
- PASS - aim: word count >= 400 (533)
- PASS - aim: standalone svg asset exists
- PASS - page exists for altavista
- PASS - altavista: inline <svg> present
- PASS - altavista: hero figure present
- PASS - altavista: provenance box present
- PASS - altavista: sources box present
- PASS - altavista: pager present
- PASS - altavista: back-to-index present
- PASS - altavista: sources box lists all 5 front-matter sources
- PASS - altavista: word count >= 400 (615)
- PASS - altavista: standalone svg asset exists
- PASS - page exists for cuil
- PASS - cuil: inline <svg> present
- PASS - cuil: hero figure present
- PASS - cuil: provenance box present
- PASS - cuil: sources box present
- PASS - cuil: pager present
- PASS - cuil: back-to-index present
- PASS - cuil: sources box lists all 4 front-matter sources
- PASS - cuil: word count >= 400 (549)
- PASS - cuil: standalone svg asset exists
- PASS - page exists for delicious
- PASS - delicious: inline <svg> present
- PASS - delicious: hero figure present
- PASS - delicious: provenance box present
- PASS - delicious: sources box present
- PASS - delicious: pager present
- PASS - delicious: back-to-index present
- PASS - delicious: sources box lists all 2 front-matter sources
- PASS - delicious: word count >= 400 (548)
- PASS - delicious: standalone svg asset exists
- PASS - page exists for digg
- PASS - digg: inline <svg> present
- PASS - digg: hero figure present
- PASS - digg: provenance box present
- PASS - digg: sources box present
- PASS - digg: pager present
- PASS - digg: back-to-index present
- PASS - digg: sources box lists all 4 front-matter sources
- PASS - digg: word count >= 400 (569)
- PASS - digg: standalone svg asset exists
- PASS - page exists for etoys
- PASS - etoys: inline <svg> present
- PASS - etoys: hero figure present
- PASS - etoys: provenance box present
- PASS - etoys: sources box present
- PASS - etoys: pager present
- PASS - etoys: back-to-index present
- PASS - etoys: sources box lists all 2 front-matter sources
- PASS - etoys: word count >= 400 (496)
- PASS - etoys: standalone svg asset exists
- PASS - page exists for friendster
- PASS - friendster: inline <svg> present
- PASS - friendster: hero figure present
- PASS - friendster: provenance box present
- PASS - friendster: sources box present
- PASS - friendster: pager present
- PASS - friendster: back-to-index present
- PASS - friendster: sources box lists all 4 front-matter sources
- PASS - friendster: word count >= 400 (591)
- PASS - friendster: standalone svg asset exists
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: hero figure present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: pager present
- PASS - geocities: back-to-index present
- PASS - geocities: sources box lists all 5 front-matter sources
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-plus
- PASS - google-plus: inline <svg> present
- PASS - google-plus: hero figure present
- PASS - google-plus: provenance box present
- PASS - google-plus: sources box present
- PASS - google-plus: pager present
- PASS - google-plus: back-to-index present
- PASS - google-plus: sources box lists all 2 front-matter sources
- PASS - google-plus: word count >= 400 (476)
- PASS - google-plus: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: hero figure present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: pager present
- PASS - google-reader: back-to-index present
- PASS - google-reader: sources box lists all 4 front-matter sources
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for msn-messenger
- PASS - msn-messenger: inline <svg> present
- PASS - msn-messenger: hero figure present
- PASS - msn-messenger: provenance box present
- PASS - msn-messenger: sources box present
- PASS - msn-messenger: pager present
- PASS - msn-messenger: back-to-index present
- PASS - msn-messenger: sources box lists all 2 front-matter sources
- PASS - msn-messenger: word count >= 400 (496)
- PASS - msn-messenger: standalone svg asset exists
- PASS - page exists for myspace
- PASS - myspace: inline <svg> present
- PASS - myspace: hero figure present
- PASS - myspace: provenance box present
- PASS - myspace: sources box present
- PASS - myspace: pager present
- PASS - myspace: back-to-index present
- PASS - myspace: sources box lists all 4 front-matter sources
- PASS - myspace: word count >= 400 (566)
- PASS - myspace: standalone svg asset exists
- PASS - page exists for napster
- PASS - napster: inline <svg> present
- PASS - napster: hero figure present
- PASS - napster: provenance box present
- PASS - napster: sources box present
- PASS - napster: pager present
- PASS - napster: back-to-index present
- PASS - napster: sources box lists all 4 front-matter sources
- PASS - napster: word count >= 400 (587)
- PASS - napster: standalone svg asset exists
- PASS - page exists for newgrounds
- PASS - newgrounds: inline <svg> present
- PASS - newgrounds: hero figure present
- PASS - newgrounds: provenance box present
- PASS - newgrounds: sources box present
- PASS - newgrounds: pager present
- PASS - newgrounds: back-to-index present
- PASS - newgrounds: sources box lists all 2 front-matter sources
- PASS - newgrounds: word count >= 400 (459)
- PASS - newgrounds: standalone svg asset exists
- PASS - page exists for pets-com
- PASS - pets-com: inline <svg> present
- PASS - pets-com: hero figure present
- PASS - pets-com: provenance box present
- PASS - pets-com: sources box present
- PASS - pets-com: pager present
- PASS - pets-com: back-to-index present
- PASS - pets-com: sources box lists all 2 front-matter sources
- PASS - pets-com: word count >= 400 (539)
- PASS - pets-com: standalone svg asset exists
- PASS - page exists for posterous
- PASS - posterous: inline <svg> present
- PASS - posterous: hero figure present
- PASS - posterous: provenance box present
- PASS - posterous: sources box present
- PASS - posterous: pager present
- PASS - posterous: back-to-index present
- PASS - posterous: sources box lists all 4 front-matter sources
- PASS - posterous: word count >= 400 (516)
- PASS - posterous: standalone svg asset exists
- PASS - page exists for somethingawful
- PASS - somethingawful: inline <svg> present
- PASS - somethingawful: hero figure present
- PASS - somethingawful: provenance box present
- PASS - somethingawful: sources box present
- PASS - somethingawful: pager present
- PASS - somethingawful: back-to-index present
- PASS - somethingawful: sources box lists all 5 front-matter sources
- PASS - somethingawful: word count >= 400 (547)
- PASS - somethingawful: standalone svg asset exists
- PASS - page exists for stumbleupon
- PASS - stumbleupon: inline <svg> present
- PASS - stumbleupon: hero figure present
- PASS - stumbleupon: provenance box present
- PASS - stumbleupon: sources box present
- PASS - stumbleupon: pager present
- PASS - stumbleupon: back-to-index present
- PASS - stumbleupon: sources box lists all 4 front-matter sources
- PASS - stumbleupon: word count >= 400 (540)
- PASS - stumbleupon: standalone svg asset exists
- PASS - page exists for vine
- PASS - vine: inline <svg> present
- PASS - vine: hero figure present
- PASS - vine: provenance box present
- PASS - vine: sources box present
- PASS - vine: pager present
- PASS - vine: back-to-index present
- PASS - vine: sources box lists all 4 front-matter sources
- PASS - vine: word count >= 400 (511)
- PASS - vine: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: hero figure present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: pager present
- PASS - winamp: back-to-index present
- PASS - winamp: sources box lists all 2 front-matter sources
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - about links categories
- PASS - categories.html exists
- PASS - categories links index
- PASS - categories lists post aim
- PASS - categories lists post altavista
- PASS - categories lists post cuil
- PASS - categories lists post delicious
- PASS - categories lists post digg
- PASS - categories lists post etoys
- PASS - categories lists post friendster
- PASS - categories lists post geocities
- PASS - categories lists post google-plus
- PASS - categories lists post google-reader
- PASS - categories lists post msn-messenger
- PASS - categories lists post myspace
- PASS - categories lists post napster
- PASS - categories lists post newgrounds
- PASS - categories lists post pets-com
- PASS - categories lists post posterous
- PASS - categories lists post somethingawful
- PASS - categories lists post stumbleupon
- PASS - categories lists post vine
- PASS - categories lists post winamp
- PASS - categories group count equals distinct categories (9 groups / 9 categories)
- PASS - categories page shows per-category counts
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - site/styles.css exists
- PASS - site/styles.css is a byte-identical copy of src/styles.css
- PASS - styles.css resolves from every page
- PASS - styles.css braces balanced (truncation lint) (open-minus-close: 0)
- PASS - no scripts in built pages
- PASS - rss.xml parses and lists every published post (20 items)
- PASS - base_url configured (absolute http url, no trailing slash) (https://example.org/dead-web-gazette)
- PASS - clean-state rebuild byte-identical to tracked site (byte-identical)
- PASS - svg deterministic for aim
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers aim
- PASS - ledger covers altavista
- PASS - ledger covers cuil
- PASS - ledger covers delicious
- PASS - ledger covers digg
- PASS - ledger covers etoys
- PASS - ledger covers friendster
- PASS - ledger covers geocities
- PASS - ledger covers google-plus
- PASS - ledger covers google-reader
- PASS - ledger covers msn-messenger
- PASS - ledger covers myspace
- PASS - ledger covers napster
- PASS - ledger covers newgrounds
- PASS - ledger covers pets-com
- PASS - ledger covers posterous
- PASS - ledger covers somethingawful
- PASS - ledger covers stumbleupon
- PASS - ledger covers vine
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS


## Verification record (publish-all batch, 2026-08-29)

Task `blog-publish-all`: full corpus published -- 20 posts, zero drafts
remaining, index and categories tuned for browsing at 20 entries.

### Ledger drift, explained and reconciled

The Task text said the ledger claimed 12 covered subjects while only 11
drafts existed. On disk, before this batch, both were 12. The drift was
historical, not a real inconsistency: Task `blog-v0-pipeline` closed with 11
drafted subjects (11 ledger entries); a later one-off pipeline run (entry
"Run 2026-08-29 15:48:33" above, executed between the v0 close and the design
overhaul) drafted stumbleupon as the 12th, updating ledger and drafts
together. Eve's Task premise compared the archived v0 Task conclusion (11)
against the current ledger (12). No draft was ever missing; 8 subjects
remained to draft, not 9.

Reconciliation performed at the end of this batch (after all 20 posts
existed):

- ledger: 20 entries = 20 seed subjects = 20 published posts (asserted by
  script before writing); every entry now has `post_exists: true` and
  `draft: null`.
- `content/drafts/`: emptied (20 scaffold files removed). The scaffolds were
  deterministic machine drafts, never editorial content; everything they
  carried forward lives in `data/facts/*.json` (facts, provenance) and
  `content/posts/*.md` (the published editorial text). No editorial work was
  deleted; the three v0 posts were not touched at all.
- The never-clobber and ledger guarantees are unchanged: a future pipeline
  run still skips all 20 (they are in the ledger) and would draft only new
  subjects.

### Runs in this batch (modes recorded per run)

- `python3 run.py --posts 9` (16:33:48): candidates 20, skipped 12, new
  drafts 8 [digg, posterous, pets-com, etoys, vine, somethingawful,
  newgrounds, cuil]. Data-source mode: hn_algolia live; wikipedia offline
  (SSL handshake timeout -- a different failure signature than the v0 runs'
  network-unreachable); wayback_cdx offline (network unreachable). All 8 new
  fact sheets therefore ground in the seed corpus plus live HN Algolia
  subject queries; each post's front matter carries its exact mode string.
- One extra HN Algolia probe (same keyless API, via the pipeline's own
  `algolia_evidence_for` plus three raw queries) hunting reaction threads
  for eToys: no usable results (only irrelevant matches). etoys is the only
  subject with no HN reaction evidence; see honesty notes.
- `python3 run.py --rebuild-only` (16:47:45): 20 posts.
- `python3 run.py --verify` (16:47:52): 286 PASS lines, ALL CHECKS PASS.

### As-built category coverage (all 9 Goal categories, 20 posts)

| Category                 | Posts                                             |
| ------------------------ | ------------------------------------------------- |
| early internet products  | 6: aim, google-reader, msn-messenger, napster, stumbleupon, vine |
| defunct websites         | 5: altavista, delicious, friendster, google-plus, myspace |
| online subcultures       | 2: digg, newgrounds                               |
| dead startups            | 2: etoys, pets-com                                |
| strange personal homepages | 1: geocities                                    |
| old software             | 1: winamp                                         |
| 2000s blogs              | 1: posterous                                      |
| old forums               | 1: somethingawful                                 |
| forgotten stories        | 1: cuil                                           |

This matches the Task's expected distribution exactly (6/5/2/2/1/1/1/1/1).
Rendered counts are asserted by the verifier ("index category chips with
counts (one per category) (9 categories)"; "categories group count equals
distinct categories (9 groups / 9 categories)").

### The 17 editorial passes

Word counts as counted by the site's own counter (includes citation markers
and the sources section, same standard as the v0 posts): aim 533, altavista
615, cuil 549, delicious 548, digg 569, etoys 496, friendster 591,
google-plus 476, msn-messenger 496, myspace 566, napster 587, newgrounds
459, pets-com 539, posterous 516, somethingawful 547, stumbleupon 540,
vine 511. All >= 400; no shortfall needed flagging.

Sourcing rules held under batch pressure: every date, number, name, and
event in the 17 posts traces to its fact sheet (seed facts with confidence
levels, plus live HN Algolia thread metadata: title, date, points,
comments, URL). Medium-confidence facts appear hedged ("reported at the
time", "by most accounts", "the company's own claims"). During drafting,
several unsourced texture numbers were caught and removed or hedged before
publishing (e.g. an invented reader figure for the del.icio.us panic, a
derived percentage for the MySpace sale, "at a loss" specifics for
Pets.com, a pronunciation aside for Cuil); the record here is the honest
residue. Cultural-memory texture rides only on sourced claims, hedged where
thin. eToys, the thinnest sheet (3 facts, no reaction threads), says so in
the post itself ("that is nearly the whole sourced record, and this gazette
will not decorate it") and cross-cites the Pets.com record for the
dot-com-context facts it uses.

The three v0 posts (geocities, google-reader, winamp) were not rewritten,
not re-edited, and did not receive new front matter; no write was issued
against their files, and their word counts above are unchanged from the
prior verification records (553/534/442).

### Presentation changes for 20 posts (D10)

- Index: category chip row with counts under the deck (9 chips); lead card
  (newest post, with its SVG) as the only large card; complete dispatch
  list -- one compact row per remaining post (date + category left, title +
  dek right). Every post is one click from the front page; the index
  carries a single inline SVG and stays 31KB.
- Categories page: unchanged grouping logic, now 9 groups with per-group
  counts (asserted by the verifier).
- `docs/design.md`: new decision D10, updated grid section, three new
  component rows (chips, dispatch list, lead-card note), three new
  traceability rows.
- `run.py --verify`: index checks rewritten for the D10 shape (lead card
  count and identity, dispatch-row count, chips-with-counts per category,
  newest-first order across lead plus rows) plus categories group/count
  checks. 286 PASS lines on the 20-post site, including the automated
  clean-state rebuild byte-compare and rss.xml listing 20 items.

### Verified versus not verified

- Verified by execution: pipeline run (8 new drafts, honest modes), all 17
  editorial passes published, ledger/drafts/posts reconciled 20/0/20,
  rebuild, and `--verify` ALL CHECKS PASS (286 checks) -- word counts,
  inline SVG + standalone asset per post, PROVENANCE and SOURCES boxes with
  every front-matter source URL rendered, pager and back-to-index, all
  internal links resolving, balanced HTML, stylesheet byte-identity and
  resolution, script-free pages, RSS parse with 20 items, base_url shape,
  clean-state rebuild byte-identical, SVG determinism probe, glyph and size
  gates tree-wide, ledger coverage.
- Not verified: pixel-level rendering by eye. A real browser navigated to
  site/index.html via file:// successfully, but every extraction path failed
  in this environment (screenshot/get_html: "Root CDP client not
  initialized"; extract_content: no LLM key) -- the same breakage class as
  the v0 and redesign sessions. Rendering confidence rests on the structural
  checks above plus deliberately conservative CSS (system fonts, standard
  properties, no scripts).
### Run 2026-08-29 16:52:12

- mode: verify
- PASS - site/index.html exists
- PASS - index links post aim
- PASS - index links post altavista
- PASS - index links post cuil
- PASS - index links post delicious
- PASS - index links post digg
- PASS - index links post etoys
- PASS - index links post friendster
- PASS - index links post geocities
- PASS - index links post google-plus
- PASS - index links post google-reader
- PASS - index links post msn-messenger
- PASS - index links post myspace
- PASS - index links post napster
- PASS - index links post newgrounds
- PASS - index links post pets-com
- PASS - index links post posterous
- PASS - index links post somethingawful
- PASS - index links post stumbleupon
- PASS - index links post vine
- PASS - index links post winamp
- PASS - index lead card count is one (1 lead card(s))
- PASS - index lead card is the newest post (expected winamp)
- PASS - index dispatch rows cover the remaining posts (19 rows / 19 non-lead posts)
- PASS - index order is newest first
- PASS - index category chips with counts (one per category) (9 categories)
- posts discovered: 20 [aim, altavista, cuil, delicious, digg, etoys, friendster, geocities, google-plus, google-reader, msn-messenger, myspace, napster, newgrounds, pets-com, posterous, somethingawful, stumbleupon, vine, winamp]
- PASS - page exists for aim
- PASS - aim: inline <svg> present
- PASS - aim: hero figure present
- PASS - aim: provenance box present
- PASS - aim: sources box present
- PASS - aim: pager present
- PASS - aim: back-to-index present
- PASS - aim: sources box lists all 2 front-matter sources
- PASS - aim: word count >= 400 (533)
- PASS - aim: standalone svg asset exists
- PASS - page exists for altavista
- PASS - altavista: inline <svg> present
- PASS - altavista: hero figure present
- PASS - altavista: provenance box present
- PASS - altavista: sources box present
- PASS - altavista: pager present
- PASS - altavista: back-to-index present
- PASS - altavista: sources box lists all 5 front-matter sources
- PASS - altavista: word count >= 400 (615)
- PASS - altavista: standalone svg asset exists
- PASS - page exists for cuil
- PASS - cuil: inline <svg> present
- PASS - cuil: hero figure present
- PASS - cuil: provenance box present
- PASS - cuil: sources box present
- PASS - cuil: pager present
- PASS - cuil: back-to-index present
- PASS - cuil: sources box lists all 4 front-matter sources
- PASS - cuil: word count >= 400 (549)
- PASS - cuil: standalone svg asset exists
- PASS - page exists for delicious
- PASS - delicious: inline <svg> present
- PASS - delicious: hero figure present
- PASS - delicious: provenance box present
- PASS - delicious: sources box present
- PASS - delicious: pager present
- PASS - delicious: back-to-index present
- PASS - delicious: sources box lists all 2 front-matter sources
- PASS - delicious: word count >= 400 (548)
- PASS - delicious: standalone svg asset exists
- PASS - page exists for digg
- PASS - digg: inline <svg> present
- PASS - digg: hero figure present
- PASS - digg: provenance box present
- PASS - digg: sources box present
- PASS - digg: pager present
- PASS - digg: back-to-index present
- PASS - digg: sources box lists all 4 front-matter sources
- PASS - digg: word count >= 400 (569)
- PASS - digg: standalone svg asset exists
- PASS - page exists for etoys
- PASS - etoys: inline <svg> present
- PASS - etoys: hero figure present
- PASS - etoys: provenance box present
- PASS - etoys: sources box present
- PASS - etoys: pager present
- PASS - etoys: back-to-index present
- PASS - etoys: sources box lists all 2 front-matter sources
- PASS - etoys: word count >= 400 (496)
- PASS - etoys: standalone svg asset exists
- PASS - page exists for friendster
- PASS - friendster: inline <svg> present
- PASS - friendster: hero figure present
- PASS - friendster: provenance box present
- PASS - friendster: sources box present
- PASS - friendster: pager present
- PASS - friendster: back-to-index present
- PASS - friendster: sources box lists all 4 front-matter sources
- PASS - friendster: word count >= 400 (591)
- PASS - friendster: standalone svg asset exists
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: hero figure present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: pager present
- PASS - geocities: back-to-index present
- PASS - geocities: sources box lists all 5 front-matter sources
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-plus
- PASS - google-plus: inline <svg> present
- PASS - google-plus: hero figure present
- PASS - google-plus: provenance box present
- PASS - google-plus: sources box present
- PASS - google-plus: pager present
- PASS - google-plus: back-to-index present
- PASS - google-plus: sources box lists all 2 front-matter sources
- PASS - google-plus: word count >= 400 (476)
- PASS - google-plus: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: hero figure present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: pager present
- PASS - google-reader: back-to-index present
- PASS - google-reader: sources box lists all 4 front-matter sources
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for msn-messenger
- PASS - msn-messenger: inline <svg> present
- PASS - msn-messenger: hero figure present
- PASS - msn-messenger: provenance box present
- PASS - msn-messenger: sources box present
- PASS - msn-messenger: pager present
- PASS - msn-messenger: back-to-index present
- PASS - msn-messenger: sources box lists all 2 front-matter sources
- PASS - msn-messenger: word count >= 400 (496)
- PASS - msn-messenger: standalone svg asset exists
- PASS - page exists for myspace
- PASS - myspace: inline <svg> present
- PASS - myspace: hero figure present
- PASS - myspace: provenance box present
- PASS - myspace: sources box present
- PASS - myspace: pager present
- PASS - myspace: back-to-index present
- PASS - myspace: sources box lists all 4 front-matter sources
- PASS - myspace: word count >= 400 (566)
- PASS - myspace: standalone svg asset exists
- PASS - page exists for napster
- PASS - napster: inline <svg> present
- PASS - napster: hero figure present
- PASS - napster: provenance box present
- PASS - napster: sources box present
- PASS - napster: pager present
- PASS - napster: back-to-index present
- PASS - napster: sources box lists all 4 front-matter sources
- PASS - napster: word count >= 400 (587)
- PASS - napster: standalone svg asset exists
- PASS - page exists for newgrounds
- PASS - newgrounds: inline <svg> present
- PASS - newgrounds: hero figure present
- PASS - newgrounds: provenance box present
- PASS - newgrounds: sources box present
- PASS - newgrounds: pager present
- PASS - newgrounds: back-to-index present
- PASS - newgrounds: sources box lists all 2 front-matter sources
- PASS - newgrounds: word count >= 400 (459)
- PASS - newgrounds: standalone svg asset exists
- PASS - page exists for pets-com
- PASS - pets-com: inline <svg> present
- PASS - pets-com: hero figure present
- PASS - pets-com: provenance box present
- PASS - pets-com: sources box present
- PASS - pets-com: pager present
- PASS - pets-com: back-to-index present
- PASS - pets-com: sources box lists all 2 front-matter sources
- PASS - pets-com: word count >= 400 (539)
- PASS - pets-com: standalone svg asset exists
- PASS - page exists for posterous
- PASS - posterous: inline <svg> present
- PASS - posterous: hero figure present
- PASS - posterous: provenance box present
- PASS - posterous: sources box present
- PASS - posterous: pager present
- PASS - posterous: back-to-index present
- PASS - posterous: sources box lists all 4 front-matter sources
- PASS - posterous: word count >= 400 (516)
- PASS - posterous: standalone svg asset exists
- PASS - page exists for somethingawful
- PASS - somethingawful: inline <svg> present
- PASS - somethingawful: hero figure present
- PASS - somethingawful: provenance box present
- PASS - somethingawful: sources box present
- PASS - somethingawful: pager present
- PASS - somethingawful: back-to-index present
- PASS - somethingawful: sources box lists all 5 front-matter sources
- PASS - somethingawful: word count >= 400 (547)
- PASS - somethingawful: standalone svg asset exists
- PASS - page exists for stumbleupon
- PASS - stumbleupon: inline <svg> present
- PASS - stumbleupon: hero figure present
- PASS - stumbleupon: provenance box present
- PASS - stumbleupon: sources box present
- PASS - stumbleupon: pager present
- PASS - stumbleupon: back-to-index present
- PASS - stumbleupon: sources box lists all 4 front-matter sources
- PASS - stumbleupon: word count >= 400 (540)
- PASS - stumbleupon: standalone svg asset exists
- PASS - page exists for vine
- PASS - vine: inline <svg> present
- PASS - vine: hero figure present
- PASS - vine: provenance box present
- PASS - vine: sources box present
- PASS - vine: pager present
- PASS - vine: back-to-index present
- PASS - vine: sources box lists all 4 front-matter sources
- PASS - vine: word count >= 400 (511)
- PASS - vine: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: hero figure present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: pager present
- PASS - winamp: back-to-index present
- PASS - winamp: sources box lists all 2 front-matter sources
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - about links categories
- PASS - categories.html exists
- PASS - categories links index
- PASS - categories lists post aim
- PASS - categories lists post altavista
- PASS - categories lists post cuil
- PASS - categories lists post delicious
- PASS - categories lists post digg
- PASS - categories lists post etoys
- PASS - categories lists post friendster
- PASS - categories lists post geocities
- PASS - categories lists post google-plus
- PASS - categories lists post google-reader
- PASS - categories lists post msn-messenger
- PASS - categories lists post myspace
- PASS - categories lists post napster
- PASS - categories lists post newgrounds
- PASS - categories lists post pets-com
- PASS - categories lists post posterous
- PASS - categories lists post somethingawful
- PASS - categories lists post stumbleupon
- PASS - categories lists post vine
- PASS - categories lists post winamp
- PASS - categories group count equals distinct categories (9 groups / 9 categories)
- PASS - categories page shows per-category counts
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - site/styles.css exists
- PASS - site/styles.css is a byte-identical copy of src/styles.css
- PASS - styles.css resolves from every page
- PASS - styles.css braces balanced (truncation lint) (open-minus-close: 0)
- PASS - no scripts in built pages
- PASS - rss.xml parses and lists every published post (20 items)
- PASS - base_url configured (absolute http url, no trailing slash) (https://example.org/dead-web-gazette)
- PASS - clean-state rebuild byte-identical to tracked site (byte-identical)
- PASS - svg deterministic for aim
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers aim
- PASS - ledger covers altavista
- PASS - ledger covers cuil
- PASS - ledger covers delicious
- PASS - ledger covers digg
- PASS - ledger covers etoys
- PASS - ledger covers friendster
- PASS - ledger covers geocities
- PASS - ledger covers google-plus
- PASS - ledger covers google-reader
- PASS - ledger covers msn-messenger
- PASS - ledger covers myspace
- PASS - ledger covers napster
- PASS - ledger covers newgrounds
- PASS - ledger covers pets-com
- PASS - ledger covers posterous
- PASS - ledger covers somethingawful
- PASS - ledger covers stumbleupon
- PASS - ledger covers vine
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 16:52:12

- mode: verify
- PASS - site/index.html exists
- PASS - index links post aim
- PASS - index links post altavista
- PASS - index links post cuil
- PASS - index links post delicious
- PASS - index links post digg
- PASS - index links post etoys
- PASS - index links post friendster
- PASS - index links post geocities
- PASS - index links post google-plus
- PASS - index links post google-reader
- PASS - index links post msn-messenger
- PASS - index links post myspace
- PASS - index links post napster
- PASS - index links post newgrounds
- PASS - index links post pets-com
- PASS - index links post posterous
- PASS - index links post somethingawful
- PASS - index links post stumbleupon
- PASS - index links post vine
- PASS - index links post winamp
- PASS - index lead card count is one (1 lead card(s))
- PASS - index lead card is the newest post (expected winamp)
- PASS - index dispatch rows cover the remaining posts (19 rows / 19 non-lead posts)
- PASS - index order is newest first
- PASS - index category chips with counts (one per category) (9 categories)
- posts discovered: 20 [aim, altavista, cuil, delicious, digg, etoys, friendster, geocities, google-plus, google-reader, msn-messenger, myspace, napster, newgrounds, pets-com, posterous, somethingawful, stumbleupon, vine, winamp]
- PASS - page exists for aim
- PASS - aim: inline <svg> present
- PASS - aim: hero figure present
- PASS - aim: provenance box present
- PASS - aim: sources box present
- PASS - aim: pager present
- PASS - aim: back-to-index present
- PASS - aim: sources box lists all 2 front-matter sources
- PASS - aim: word count >= 400 (533)
- PASS - aim: standalone svg asset exists
- PASS - page exists for altavista
- PASS - altavista: inline <svg> present
- PASS - altavista: hero figure present
- PASS - altavista: provenance box present
- PASS - altavista: sources box present
- PASS - altavista: pager present
- PASS - altavista: back-to-index present
- PASS - altavista: sources box lists all 5 front-matter sources
- PASS - altavista: word count >= 400 (615)
- PASS - altavista: standalone svg asset exists
- PASS - page exists for cuil
- PASS - cuil: inline <svg> present
- PASS - cuil: hero figure present
- PASS - cuil: provenance box present
- PASS - cuil: sources box present
- PASS - cuil: pager present
- PASS - cuil: back-to-index present
- PASS - cuil: sources box lists all 4 front-matter sources
- PASS - cuil: word count >= 400 (549)
- PASS - cuil: standalone svg asset exists
- PASS - page exists for delicious
- PASS - delicious: inline <svg> present
- PASS - delicious: hero figure present
- PASS - delicious: provenance box present
- PASS - delicious: sources box present
- PASS - delicious: pager present
- PASS - delicious: back-to-index present
- PASS - delicious: sources box lists all 2 front-matter sources
- PASS - delicious: word count >= 400 (548)
- PASS - delicious: standalone svg asset exists
- PASS - page exists for digg
- PASS - digg: inline <svg> present
- PASS - digg: hero figure present
- PASS - digg: provenance box present
- PASS - digg: sources box present
- PASS - digg: pager present
- PASS - digg: back-to-index present
- PASS - digg: sources box lists all 4 front-matter sources
- PASS - digg: word count >= 400 (569)
- PASS - digg: standalone svg asset exists
- PASS - page exists for etoys
- PASS - etoys: inline <svg> present
- PASS - etoys: hero figure present
- PASS - etoys: provenance box present
- PASS - etoys: sources box present
- PASS - etoys: pager present
- PASS - etoys: back-to-index present
- PASS - etoys: sources box lists all 2 front-matter sources
- PASS - etoys: word count >= 400 (496)
- PASS - etoys: standalone svg asset exists
- PASS - page exists for friendster
- PASS - friendster: inline <svg> present
- PASS - friendster: hero figure present
- PASS - friendster: provenance box present
- PASS - friendster: sources box present
- PASS - friendster: pager present
- PASS - friendster: back-to-index present
- PASS - friendster: sources box lists all 4 front-matter sources
- PASS - friendster: word count >= 400 (591)
- PASS - friendster: standalone svg asset exists
- PASS - page exists for geocities
- PASS - geocities: inline <svg> present
- PASS - geocities: hero figure present
- PASS - geocities: provenance box present
- PASS - geocities: sources box present
- PASS - geocities: pager present
- PASS - geocities: back-to-index present
- PASS - geocities: sources box lists all 5 front-matter sources
- PASS - geocities: word count >= 400 (553)
- PASS - geocities: standalone svg asset exists
- PASS - page exists for google-plus
- PASS - google-plus: inline <svg> present
- PASS - google-plus: hero figure present
- PASS - google-plus: provenance box present
- PASS - google-plus: sources box present
- PASS - google-plus: pager present
- PASS - google-plus: back-to-index present
- PASS - google-plus: sources box lists all 2 front-matter sources
- PASS - google-plus: word count >= 400 (476)
- PASS - google-plus: standalone svg asset exists
- PASS - page exists for google-reader
- PASS - google-reader: inline <svg> present
- PASS - google-reader: hero figure present
- PASS - google-reader: provenance box present
- PASS - google-reader: sources box present
- PASS - google-reader: pager present
- PASS - google-reader: back-to-index present
- PASS - google-reader: sources box lists all 4 front-matter sources
- PASS - google-reader: word count >= 400 (534)
- PASS - google-reader: standalone svg asset exists
- PASS - page exists for msn-messenger
- PASS - msn-messenger: inline <svg> present
- PASS - msn-messenger: hero figure present
- PASS - msn-messenger: provenance box present
- PASS - msn-messenger: sources box present
- PASS - msn-messenger: pager present
- PASS - msn-messenger: back-to-index present
- PASS - msn-messenger: sources box lists all 2 front-matter sources
- PASS - msn-messenger: word count >= 400 (496)
- PASS - msn-messenger: standalone svg asset exists
- PASS - page exists for myspace
- PASS - myspace: inline <svg> present
- PASS - myspace: hero figure present
- PASS - myspace: provenance box present
- PASS - myspace: sources box present
- PASS - myspace: pager present
- PASS - myspace: back-to-index present
- PASS - myspace: sources box lists all 4 front-matter sources
- PASS - myspace: word count >= 400 (566)
- PASS - myspace: standalone svg asset exists
- PASS - page exists for napster
- PASS - napster: inline <svg> present
- PASS - napster: hero figure present
- PASS - napster: provenance box present
- PASS - napster: sources box present
- PASS - napster: pager present
- PASS - napster: back-to-index present
- PASS - napster: sources box lists all 4 front-matter sources
- PASS - napster: word count >= 400 (587)
- PASS - napster: standalone svg asset exists
- PASS - page exists for newgrounds
- PASS - newgrounds: inline <svg> present
- PASS - newgrounds: hero figure present
- PASS - newgrounds: provenance box present
- PASS - newgrounds: sources box present
- PASS - newgrounds: pager present
- PASS - newgrounds: back-to-index present
- PASS - newgrounds: sources box lists all 2 front-matter sources
- PASS - newgrounds: word count >= 400 (459)
- PASS - newgrounds: standalone svg asset exists
- PASS - page exists for pets-com
- PASS - pets-com: inline <svg> present
- PASS - pets-com: hero figure present
- PASS - pets-com: provenance box present
- PASS - pets-com: sources box present
- PASS - pets-com: pager present
- PASS - pets-com: back-to-index present
- PASS - pets-com: sources box lists all 2 front-matter sources
- PASS - pets-com: word count >= 400 (539)
- PASS - pets-com: standalone svg asset exists
- PASS - page exists for posterous
- PASS - posterous: inline <svg> present
- PASS - posterous: hero figure present
- PASS - posterous: provenance box present
- PASS - posterous: sources box present
- PASS - posterous: pager present
- PASS - posterous: back-to-index present
- PASS - posterous: sources box lists all 4 front-matter sources
- PASS - posterous: word count >= 400 (516)
- PASS - posterous: standalone svg asset exists
- PASS - page exists for somethingawful
- PASS - somethingawful: inline <svg> present
- PASS - somethingawful: hero figure present
- PASS - somethingawful: provenance box present
- PASS - somethingawful: sources box present
- PASS - somethingawful: pager present
- PASS - somethingawful: back-to-index present
- PASS - somethingawful: sources box lists all 5 front-matter sources
- PASS - somethingawful: word count >= 400 (547)
- PASS - somethingawful: standalone svg asset exists
- PASS - page exists for stumbleupon
- PASS - stumbleupon: inline <svg> present
- PASS - stumbleupon: hero figure present
- PASS - stumbleupon: provenance box present
- PASS - stumbleupon: sources box present
- PASS - stumbleupon: pager present
- PASS - stumbleupon: back-to-index present
- PASS - stumbleupon: sources box lists all 4 front-matter sources
- PASS - stumbleupon: word count >= 400 (540)
- PASS - stumbleupon: standalone svg asset exists
- PASS - page exists for vine
- PASS - vine: inline <svg> present
- PASS - vine: hero figure present
- PASS - vine: provenance box present
- PASS - vine: sources box present
- PASS - vine: pager present
- PASS - vine: back-to-index present
- PASS - vine: sources box lists all 4 front-matter sources
- PASS - vine: word count >= 400 (511)
- PASS - vine: standalone svg asset exists
- PASS - page exists for winamp
- PASS - winamp: inline <svg> present
- PASS - winamp: hero figure present
- PASS - winamp: provenance box present
- PASS - winamp: sources box present
- PASS - winamp: pager present
- PASS - winamp: back-to-index present
- PASS - winamp: sources box lists all 2 front-matter sources
- PASS - winamp: word count >= 400 (442)
- PASS - winamp: standalone svg asset exists
- PASS - about.html exists
- PASS - about links index
- PASS - about links categories
- PASS - categories.html exists
- PASS - categories links index
- PASS - categories lists post aim
- PASS - categories lists post altavista
- PASS - categories lists post cuil
- PASS - categories lists post delicious
- PASS - categories lists post digg
- PASS - categories lists post etoys
- PASS - categories lists post friendster
- PASS - categories lists post geocities
- PASS - categories lists post google-plus
- PASS - categories lists post google-reader
- PASS - categories lists post msn-messenger
- PASS - categories lists post myspace
- PASS - categories lists post napster
- PASS - categories lists post newgrounds
- PASS - categories lists post pets-com
- PASS - categories lists post posterous
- PASS - categories lists post somethingawful
- PASS - categories lists post stumbleupon
- PASS - categories lists post vine
- PASS - categories lists post winamp
- PASS - categories group count equals distinct categories (9 groups / 9 categories)
- PASS - categories page shows per-category counts
- PASS - all internal links resolve
- PASS - html parses with balanced tags
- PASS - site/styles.css exists
- PASS - site/styles.css is a byte-identical copy of src/styles.css
- PASS - styles.css resolves from every page
- PASS - styles.css braces balanced (truncation lint) (open-minus-close: 0)
- PASS - no scripts in built pages
- PASS - rss.xml parses and lists every published post (20 items)
- PASS - base_url configured (absolute http url, no trailing slash) (https://example.org/dead-web-gazette)
- PASS - clean-state rebuild byte-identical to tracked site (byte-identical)
- PASS - svg deterministic for aim
- PASS - glyph gate (ASCII-only, no emoji, no check marks)
- PASS - size gate (no text file over 100KB)
- PASS - ledger covers aim
- PASS - ledger covers altavista
- PASS - ledger covers cuil
- PASS - ledger covers delicious
- PASS - ledger covers digg
- PASS - ledger covers etoys
- PASS - ledger covers friendster
- PASS - ledger covers geocities
- PASS - ledger covers google-plus
- PASS - ledger covers google-reader
- PASS - ledger covers msn-messenger
- PASS - ledger covers myspace
- PASS - ledger covers napster
- PASS - ledger covers newgrounds
- PASS - ledger covers pets-com
- PASS - ledger covers posterous
- PASS - ledger covers somethingawful
- PASS - ledger covers stumbleupon
- PASS - ledger covers vine
- PASS - ledger covers winamp
- verify result: ALL CHECKS PASS

### Run 2026-08-29 18:39:49

- mode: rebuild-only; site rebuilt with 20 post(s) [winamp, vine, stumbleupon, somethingawful, posterous, pets-com, newgrounds, napster, myspace, msn-messenger, google-reader, google-plus, geocities, friendster, etoys, digg, delicious, cuil, altavista, aim]

### Run 2026-08-29 18:45:14

- mode: fetch-screenshots
- subjects attempted: 20; screenshots stored: 0; degraded to generated art: 20
- post bodies byte-identical after front-matter updates (sha256): yes
- aim: -- url=http://aim.com -- not stored; illustration=generated -- cdx http://aim.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- altavista: -- url=http://altavista.com -- not stored; illustration=generated -- cdx http://altavista.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- cuil: -- url=http://cuil.com -- not stored; illustration=generated -- cdx http://cuil.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- delicious: -- url=http://del.icio.us -- not stored; illustration=generated -- cdx http://del.icio.us: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- digg: -- url=http://digg.com -- not stored; illustration=generated -- cdx http://digg.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- etoys: -- url=http://etoys.com -- not stored; illustration=generated -- cdx http://etoys.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- friendster: -- url=http://friendster.com -- not stored; illustration=generated -- cdx http://friendster.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- geocities: -- url=http://geocities.com -- not stored; illustration=generated -- cdx http://geocities.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- google-plus: -- url=http://plus.google.com -- not stored; illustration=generated -- cdx http://plus.google.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- google-reader: -- url=http://google.com/reader -- not stored; illustration=generated -- cdx http://google.com/reader: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- msn-messenger: -- url=http://messenger.msn.com -- not stored; illustration=generated -- cdx http://messenger.msn.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- myspace: -- url=http://myspace.com -- not stored; illustration=generated -- cdx http://myspace.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- napster: -- url=http://napster.com -- not stored; illustration=generated -- cdx http://napster.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- newgrounds: -- url=http://newgrounds.com -- not stored; illustration=generated -- cdx http://newgrounds.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- pets-com: -- url=http://pets.com -- not stored; illustration=generated -- cdx http://pets.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- posterous: -- url=http://posterous.com -- not stored; illustration=generated -- cdx http://posterous.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- somethingawful: -- url=http://somethingawful.com -- not stored; illustration=generated -- cdx http://somethingawful.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- stumbleupon: -- url=http://stumbleupon.com -- not stored; illustration=generated -- cdx http://stumbleupon.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- vine: -- url=http://vine.co -- not stored; illustration=generated -- cdx http://vine.co: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- winamp: -- url=http://winamp.com -- not stored; illustration=generated -- cdx http://winamp.com: cdx: URL error ([Errno 101] Network is unreachable) from web.archive.org -- screenshot: URL error ([Errno 101] Network is unreachable) from web.archive.org -- front matter: 1 field(s) applied
- no binaries stored this run (nothing to size-report)
- site rebuilt: 20 published post(s)

### Run 2026-08-29 18:45:31

- mode: verify -- 392 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 18:45:41

- mode: verify -- 392 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 18:45:42

- mode: verify -- 392 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 18:46:37

- mode: scratch verification of the screenshot rendering path (not a fetch)
- method: synthetic 1x1 PNG (built in /tmp, never in the artifact tree) + a /tmp copy of one post flipped to illustration: screenshot with provenance fields
- results: img rendered with ../assets/<slug>.png and /gz/assets/<slug>.png (prefix mode); plate label 'screenshot: Wayback Machine, snapshot <ts>, fetched <date>'; PROVENANCE gained an Illustration row and a 'Screenshot of' url row; binary copied byte-identically into site/assets; missing-binary fallback rendered the generated SVG labeled 'generated memorial art' (no mislabel possible); front-matter editor idempotent on second run and body sha256 unchanged
- note: this exercises code paths the unreachable archive cannot; it stores no image and publishes nothing -- the tracked tree remains all-generated, honestly labeled

### Run 2026-08-29 18:47:00

- mode: verify -- 392 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 19:33:57

- mode: fetch-screenshots (render strategy: resolve via CDX, then screenshot https://web.archive.org/web/<ts>/<url> with a headless browser; the former /screenshot/ endpoint returned 404 html for every subject in the operator run of 2026-08-29 and is no longer called)
- browser: chromium found at /usr/bin/chromium (PATH probe)
- subjects attempted: 20; screenshots stored: 0; degraded to generated art: 20
- post bodies byte-identical after front-matter updates (sha256): yes
- RESULT.md near the size gate (89.8KB of 100KB); per-subject lines kept on stdout only; condensed outcomes:
-   cdx http: 20 subject(s) [aim, altavista, cuil, delicious, digg, etoys, friendster, geocities, google-plus, google-reader, msn-messenger, myspace, napster, newgrounds, pets-com, posterous, somethingawful, stumbleupon, vine, winamp]
- no binaries stored this run (nothing to size-report)
- site rebuilt: 20 published post(s)

### Run 2026-08-29 19:36:08

- mode: fetch-screenshots (render strategy: resolve via CDX, then screenshot https://web.archive.org/web/<ts>/<url> with a headless browser; the former /screenshot/ endpoint returned 404 html for every subject in the operator run of 2026-08-29 and is no longer called)
- browser: none found -- set CHROME_BIN=/path/to/a/chrome-or-chromium binary, or install Google Chrome / Chromium / Microsoft Edge, then re-run python3 run.py --fetch-screenshots
- subjects attempted: 20; screenshots stored: 0; degraded to generated art: 20
- post bodies byte-identical after front-matter updates (sha256): yes
- skipped (no browser binary): aim, altavista, cuil, delicious, digg, etoys, friendster, geocities, google-plus, google-reader, msn-messenger, myspace, napster, newgrounds, pets-com, posterous, somethingawful, stumbleupon, vine, winamp
- no binaries stored this run (nothing to size-report)
- site rebuilt: 20 published post(s)

### Run 2026-08-29 19:36:26

- mode: task diagnosis record (blog-screenshot-renderer) -- why the fetch strategy changed
- operator laptop run 2026-08-29 (network WITH archive egress), on the record: the
-   https://web.archive.org/screenshot/<url> endpoint returned HTTP 404 with an html
-   error page for all 20 subjects (plus one 503 challenge page for somethingawful)
-   -- the service is dead; the dependency is removed and the endpoint is kept only
-   as a tombstone constant in pipeline/screenshots.py
- same run, CDX: answered inside 5s for 5 of 20 subjects (delicious 20031004064641,
-   etoys 20010130072000, google-plus 20120215235515, msn-messenger 19991012062956,
-   winamp 19981205015145) and timed out for the other 15 -> CDX client hardened:
-   25s timeout, one retry, 200-status preference kept, circuit breaker after 4
-   consecutive transport failures, ~2s inter-subject delay
- new strategy: render, do not fetch -- screenshot
-   https://web.archive.org/web/<ts>/<original-url> with a headless browser located
-   via CHROME_BIN / PATH probe / macOS bundles (subprocess, stdlib only)
- payload-guard calibration on this box chromium (1024x640 headless): blank page
-   3301 bytes; browser error page (closed loopback port) 21768 bytes; real content
-   page (gazette index served on loopback) 67398 bytes -> near-blank floor 24576
- hang behavior measured: an unroutable host makes the browser never exit and write
-   no file (killed at 100s in the probe) -> the render owns a 45s wall clock and
-   kills the process group; a fast-failing target writes a genuine png of the
-   browser error page, which is why the floor + dimension + pre-check guards exist

### Run 2026-08-29 19:36:27

- mode: verify -- 393 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 19:36:38

- mode: verify -- 393 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 19:36:40

- mode: verify -- 393 checks, ALL PASS
- posts: 20; illustration modes: 0 screenshot, 20 generated (labels on every page)
- mount diag: GET /artifacts/writing/internet-archaeology-blog/site without trailing slash -> HTTP 301 (a conforming server 301-redirects to the slash form; a rewriting server that does not is what breaks page-relative refs)
- mode A ok: 31 internal refs answered 200 under /artifacts/writing/internet-archaeology-blog/site/ (default page-relative mode)
- mode B ok: 31 prefix-absolute internal refs answered 200 under /site/ (path_prefix mode); rss links = base_url + prefix
- mount test method: stdlib http.server on 127.0.0.1 ephemeral port, browser-like GETs (redirects followed), every internal href/src fetched; mode A rooted at the workspace root, mode B at a temp root with path_prefix=/site/
- binary asset size report: no screenshot binaries stored
- full per-check listing printed to stdout; this record carries section outcomes, methods, and all failures

### Run 2026-08-29 19:37:34

- mode: offline unit tests (blog-screenshot-renderer) -- 24 tests, OK
- python3 -m unittest discover -s tests: url construction, cdx params, payload
-   guards (magic/dimensions/floor), browser detection (PATH probe, CHROME_BIN
-   override + broken-override), additive+idempotent front matter, no-browser
-   degradation, never-clobber, RESULT-condensation grouping, scratch-build
-   consistency with a synthetic png, and two real local renders with this
-   box chromium (gazette index over loopback -> valid 1024x640 png above the
-   floor; closed loopback port -> browser error page rejected by the guards)

