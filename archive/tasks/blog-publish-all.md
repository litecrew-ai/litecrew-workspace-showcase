---
status: done
goal: internet-archaeology-blog.md
assigned_agent: web-product-engineer
created: 2026-08-29
updated: 2026-08-29
---

# Task: Publish the full corpus — every draft posted, site tuned for browsing

## Description

The user asked to "post all content" and "make sure our user can see more content on
site". Concretely, in one batch:

1. **Draft the remaining seed subjects.** 11 of the 20 seed-corpus subjects have
   drafts; 9 do not. Run the pipeline to draft them (`python3 run.py --posts 9`).
   Record the data-source mode honestly per run (network reachability has varied
   between sessions).
2. **Reconcile the ledger.** The ledger currently claims 12 covered subjects while
   only 11 drafts exist — explain the drift in RESULT.md and make ledger, drafts,
   and posts consistent (never by deleting editorial work).
3. **Editorial pass on ALL drafts** (17: the 8 pending plus the 9 new). Each becomes
   a published post in `content/posts/` per the established standard: 400+ words in
   the gazette register ("In 2004, someone built a website. That website once had 3
   million users. Today, no one remembers it."), every factual claim traced to the
   fact sheet's sources or explicitly hedged, additive `dek:` front matter, one h1
   elision convention as already implemented. The 3 existing published posts are NOT
   rewritten (their bodies stay byte-identical).
4. **Tune the presentation for 20 posts.** The current index was tuned for 3 posts
   (the design overhaul's own follow-up note). Every published post must be reachable
   from the index in at most one click; a wall of 20 large cards is not acceptable.
   Likely shape (your call within the design brief): lead card for the newest, a
   compact grid or complete-dispatch list for the rest, category chips with counts,
   and a categories page that groups all 20. Update `docs/design.md` if you add or
   change a component (new decision IDs, traceability matrix row).
5. **Verify at scale.** All 20 posts: word counts, sources render, SVGs, pager,
   RSS lists 20, categories complete, clean-state rebuild byte-identical, `--verify`
   ALL CHECKS PASS. RESULT.md records the runs, modes, and the category coverage
   table (the corpus spans all 9 Goal categories: early internet products 6,
   defunct websites 5, online subcultures 2, dead startups 2, and one each for
   strange personal homepages, old software, 2000s blogs, old forums, forgotten
   stories — confirm and report as-built).

## Completion criteria

- [ ] All 20 seed-corpus subjects are published posts on the built site; zero drafts
      remain in `content/drafts/`; ledger drift explained and consistent.
- [ ] Each of the 17 new posts: 400+ words, gazette register, cited sources that
      render on the page, PROVENANCE box, generated SVG, dek; the 3 existing posts
      byte-identical except nothing (untouched).
- [ ] Index reaches every post in <= 1 click with a layout that stays scannable at
      20 entries; design.md updated for any component change; categories page groups
      all posts with counts.
- [ ] `run.py --verify` ALL CHECKS PASS on the 20-post site, including the automated
      clean-state byte-compare; RESULT.md records runs, modes, verification methods,
      the as-built category coverage table, and anything not verified.
- [ ] README updated (post counts, any run instructions change); knowledge captured
      or merged per sediment protocol (an editorial-batch-at-scale section merged
      into `knowledge/writing/post-generation-pipeline.md` is the expected shape;
      a third note only if it genuinely cannot fit); INDEX in sync.
- [ ] Content rules hold everywhere: English; ASCII-safe; no emoji; no check-mark or
      checkbox glyphs (U+2713, U+2714, U+2705, U+2611 family); no text file over
      100KB; no new dependencies, no network beyond the established keyless APIs.

## Context and constraints

- **Write boundaries**: this Task file; `artifacts/writing/internet-archaeology-blog/`;
  `knowledge/writing/`. Nothing else. No git commands; no `.github/` changes.
- **Stack**: unchanged (Python 3.11 stdlib only).
- **Truthfulness law**: unchanged and now load-bearing — 17 narratives in one batch
  is exactly where fabrication pressure appears. If a fact sheet is thin, write a
  shorter, hedged post rather than inventing texture. A boring-but-sourced post
  beats a vivid-but-fabricated one; if a subject genuinely cannot support 400
  sourced words, publish the best-sourced post you honestly can and flag it in
  RESULT.md (word-count criterion satisfied for that post via your editorial
  latitude ONLY if sourcing stays clean — otherwise report the shortfall to Eve
  instead of padding).
- **Quality over speed, but finish**: this is a large single batch. If you hit a
  hard blocker partway (e.g., drafting fails for some subjects), publish what is
  publishable, record the gap explicitly, and report — a 19/20 with an honest gap
  beats a fabricated 20/20.
- Fastest context load: artifact README + RESULT.md, `docs/design.md`,
  `knowledge/writing/post-generation-pipeline.md`, and the two archived Task records
  (`archive/tasks/blog-v0-pipeline.md`, `archive/tasks/blog-design-overhaul.md`).

## Execution steps

<!-- Subagent fills -->

### Preparation (mandatory retrieval, round 1)

- `handbooks/`: only `README.md` exists (known gap, recorded by both prior Tasks);
  nothing to retrieve. Memory note `publication-gate-policy` honored (no check-mark
  glyphs anywhere I write).
- `knowledge/writing/`: `post-generation-pipeline.md` (determinism, never-clobber,
  glyph gates at write time, verifier-first, design-brief workflow, falsy-list trap)
  and `INDEX.md`; `dead-web-source-catalog.md` skimmed (reachability varies per
  session; record mode per run).
- Read in full: Goal, this Task, artifact README + RESULT.md, `docs/design.md`,
  `run.py`, all of `pipeline/` (discovery, facts, writing, site, svgart stub via
  site usage, util), `src/styles.css`, all 3 published posts, sample drafts +
  every fact sheet, both archived Task records, `workflows/subagent-workflow.md`,
  `workflows/knowledge-sediment-protocol.md`.
- **Ledger drift, diagnosed before any write**: the Task premise says "ledger
  claims 12 covered, only 11 drafts exist". On disk both are 12 (aim, altavista,
  delicious, friendster, geocities, google-plus, google-reader, msn-messenger,
  myspace, napster, stumbleupon, winamp). Explanation: Task `blog-v0-pipeline`
  closed at 11 drafts / 11 ledger entries; a later one-off run (RESULT.md
  2026-08-29 15:48:33, between v0 and the design overhaul) drafted stumbleupon as
  #12, updating both ledger and drafts together. Eve's snapshot compared the v0
  Task conclusion (11) against the current ledger (12). There is no actual
  inconsistency today; remaining subjects to draft = 8, not 9. Will be recorded in
  RESULT.md and the ledger made fully consistent (post_exists, draft lifecycle)
  at the end of the batch.

### Plan

1. Run `python3 run.py --posts 9`. Eight subjects are not yet covered (digg,
   posterous, pets-com, etoys, vine, somethingawful, newgrounds, cuil), so the
   run should draft 8 regardless of the requested 9. Record data-source mode
   honestly per run.
2. Editorial pass on all 17 pending drafts (9 existing + 8 new) into
   `content/posts/`: gazette register, 400+ words, every claim sourced [SN] or
   hedged, additive `dek:` front matter, one h1 elision convention. The 3
   existing posts stay untouched (byte-identical).
3. Reconcile ledger (post_exists true for all 20, draft lifecycle recorded) and
   empty `content/drafts/` per the completion criterion (machine scaffolds only;
   no editorial work deleted -- posts and fact sheets carry everything forward).
4. Tune the index for 20 posts: category chips with counts, lead card for the
   newest, compact dispatch list for the rest; categories page groups all 20.
   Update `docs/design.md` (new decision IDs, component inventory, traceability
   rows) and `src/styles.css`; extend `run.py --verify` for the new shape.
5. Rebuild + `run.py --verify` to ALL CHECKS PASS (including automated
   clean-state byte-compare, RSS 20 items, categories complete).
6. RESULT.md: batch verification record, drift explanation + reconciliation, runs
   and modes, as-built category coverage table, honest shortfalls if any.
7. README update (post counts, presentation, run instructions unchanged).
8. Knowledge: merge an editorial-batch-at-scale section into
   `knowledge/writing/post-generation-pipeline.md`; keep INDEX in sync.
9. Self-check against every completion criterion; fill Conclusions.

## Execution log

<!-- Append after each subagent iteration -->

| Round | Date       | Progress | Notes |
| ----- | ---------- | -------- | ----- |
| 1 | 2026-08-29 | Retrieval done, plan set, ledger drift diagnosed | Drift is historical (v0 Task text vs a post-v0 stumbleupon run), not an on-disk inconsistency; 8 subjects remain to draft, not 9 |
| 2 | 2026-08-29 | Pipeline run `--posts 9`: 8 new drafts (digg, posterous, pets-com, etoys, vine, somethingawful, newgrounds, cuil) | Mode honest: hn_algolia live; wikipedia offline (SSL handshake timeout); wayback_cdx offline (network unreachable); RESULT.md entry auto-appended |
| 3 | 2026-08-29 | All 17 editorial passes published into content/posts/ (9 pending + 8 new); 3 existing posts untouched | Word counts 442-615 all >= 400 (incl. etoys 496 on the thinnest fact sheet, handled by cross-citation + explicit no-decoration framing); glyphs clean; every post has dek + cited sources |
| 4 | 2026-08-29 | Ledger reconciled (20/20/20 asserted by set equality; post_exists true, draft null) and content/drafts/ emptied (20 scaffolds retired) | No editorial work deleted; fact sheets + posts carry everything; never-clobber and dedup guarantees unchanged |
| 5 | 2026-08-29 | D10 presentation: index = category chips with counts + lead card + complete compact dispatch list; design.md, styles.css updated; run.py --verify rewritten for the new shape | Every post one click from the index; index stays 31KB with a single inline SVG |
| 6 | 2026-08-29 | Rebuilt + verified: 286 PASS lines, ALL CHECKS PASS, including clean-state byte-compare, RSS 20 items, chips/groups counts | Browser navigation via file:// OK but screenshot/DOM extraction still broken (CDP client / LLM key) -- recorded honestly in RESULT.md, third session with the same breakage |
| 7 | 2026-08-29 | RESULT.md batch record (drift explanation, reconciliation, runs+modes, coverage table, verified-vs-not, honesty notes); README refreshed; knowledge merged into post-generation-pipeline.md + INDEX synced | Several unsourced texture numbers caught and removed during drafting (del.icio.us reader figure, MySpace derived percentage, Pets.com loss specifics, Cuil pronunciation) -- recorded in RESULT.md |

## Conclusions and output

### What was published

All 20 seed-corpus subjects are published posts on the built site; zero
drafts remain. The batch: `run.py --posts 9` drafted the 8 not-yet-covered
subjects (the Task said 9; the drift analysis below explains why only 8
remained), and 17 editorial passes were written into `content/posts/`
(the 9 pending drafts + the 8 new). Word counts 442-615, all >= 400; gazette
register throughout; every post carries additive `dek:` front matter, cited
sources that render in the SOURCES box, a PROVENANCE box, and its generated
SVG. The 3 v0 posts were not touched (no write issued against them; counts
unchanged 553/534/442).

### Ledger drift and reconciliation

- Diagnosis: the premise "ledger 12 vs 11 drafts" was stale prose, not an
  on-disk inconsistency. Task blog-v0-pipeline closed at 11; a one-off run
  at 15:48:33 (recorded in RESULT.md between the v0 and redesign sections)
  drafted stumbleupon as #12, updating ledger and drafts together.
- Reconciliation: script asserted set equality seed/ledger/posts (20/20/20)
  before mutating; every ledger entry now `post_exists: true`, `draft: null`;
  the 20 machine scaffolds were removed from `content/drafts/` (scaffolds
  are deterministic drafts, not editorial work; facts persist in
  `data/facts/`). Never-clobber and dedup behavior unchanged.

### As-built category coverage (all 9 Goal categories)

| Category                   | Count | Posts |
| -------------------------- | ----- | ----- |
| early internet products    | 6     | aim, google-reader, msn-messenger, napster, stumbleupon, vine |
| defunct websites           | 5     | altavista, delicious, friendster, google-plus, myspace |
| online subcultures         | 2     | digg, newgrounds |
| dead startups              | 2     | etoys, pets-com |
| strange personal homepages | 1     | geocities |
| old software               | 1     | winamp |
| 2000s blogs                | 1     | posterous |
| old forums                 | 1     | somethingawful |
| forgotten stories          | 1     | cuil |

Matches the Task's expected distribution exactly (6/5/2/2/1/1/1/1/1);
verifier asserts chips-with-counts and categories groups (9/9).

### Presentation (D10) and verification

- Index: category chips with counts (9), lead card for the newest post
  (winamp), complete compact dispatch list (19 rows); every post reachable
  in <= 1 click; index 31KB with one inline SVG. `docs/design.md` gained
  decision D10, component rows, traceability rows; `src/styles.css` gained
  the chip and dispatch-list styles with a mobile collapse.
- `run.py --verify`: index checks rewritten for D10 (lead count/identity,
  row count, chips-with-counts, newest-first order) plus categories
  group/count checks. Final result: 286 PASS lines, ALL CHECKS PASS,
  including the automated clean-state rebuild byte-compare, rss.xml listing
  20 items, per-post source rendering, glyph and size gates tree-wide.
- Data-source modes recorded per run: batch run had hn_algolia live,
  wikipedia offline (SSL handshake timeout -- a new failure signature),
  wayback_cdx offline. One extra HN Algolia probe for etoys found nothing
  usable (same keyless API).

### Verified versus assumed

- Verified by execution: everything above (see RESULT.md "Verification
  record (publish-all batch)" and the two verify run entries).
- Not verified: pixel-level rendering by eye (browser navigates via
  file:// but screenshot/DOM extraction is broken in this environment --
  third session in a row; structural checks carry the confidence).
- Honest notes: several unsourced texture numbers were caught and removed
  or hedged during drafting (recorded in RESULT.md); etoys, the thinnest
  sheet, declares its thinness in the post and cross-cites Pets.com for
  era context -- no padding was needed anywhere, so no word-count shortfall
  had to be flagged.

### Limitations / follow-ups (non-blocking)

- base_url remains a documented placeholder; set it when the gazette gets a
  real domain and rebuild.
- Wikipedia/Wayback code paths remain exercised only via their failure
  handlers in this environment.
- Visual QA by eye still outstanding until browser tooling works here; a
  human opening site/index.html settles it in one glance.
- Next growth step is discovery beyond the 20-subject seed corpus (the
  ledger and pipeline already support it).

## Knowledge-capture suggestions

Captured (merged, no new note created) into
`knowledge/writing/post-generation-pipeline.md`: a new section "Editorial
batch at scale (from the publish-all run)" -- number auditing against fact
sheets, thin-sheet honesty (declared thinness + cross-citation), re-probing
the evidence API before accepting thinness, lead-plus-register index shape
for scale, ledger-drift diagnosis by set equality, and scaffold retirement
semantics. Verification section and reuse checklist extended; change
history row added; `knowledge/writing/INDEX.md` one-liner updated.
