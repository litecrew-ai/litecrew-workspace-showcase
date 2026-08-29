---
status: done
goal: operate-internet-archaeology-blog.md
assigned_agent: web-product-engineer
created: 2026-08-29
updated: 2026-08-29
---

# Task: Image-search acquisition route — real historical images, no browser

## Description

The archived-page render route failed on the operator's Mac three times (latest:
hang with only updater stderr noise). The operator redirects the approach, on the
record: "rather than grabbing screenshots from web.archive.org, we can just search
for images using search engines to get the screenshots we need." This Task
implements image-search acquisition. Operator authorization for the search-engine
route (and its licensing posture, documented below) is this quoted instruction.

Eve's probes (2026-08-29, from this box — the build environment, not the laptop):

- `www.bing.com` reachable; `/images/search?q=...` 302-redirects to `cn.bing.com`
  and serves ~260KB server-rendered HTML containing 36 `iusc`/`m="..."` metadata
  blocks per query (title, original image URL `murl`, Bing thumbnail URL `turl`,
  source page `purl`). **The search route is live from this box.**
- `tse1.mm.bing.net` (thumbnail host) answers HTTP 200 from this box.
- `duckduckgo.com`, `commons.wikimedia.org`, `upload.wikimedia.org`, `google.com`:
  unreachable from this box (reachable presumably from the laptop).

## Scope

1. **Route 1 — Bing image search (primary; live from this box)**:
   - New module `pipeline/imagesearch.py`: fetch
     `https://www.bing.com/images/search?q=<query>` with a desktop UA, following
     redirects (urllib handles the cn.bing.com hop); parse the server-rendered
     `class="iusc" m="..."` attributes (HTML-unescaped JSON: `murl`, `turl`,
     `purl`, `t`); rank candidates.
   - **Strict subject match** before accepting a candidate: the subject's name or
     domain must appear in the title `t` or source page `purl` (case-insensitive);
     reject everything else. Build the query from the subject name + era hint
     (e.g. "<name> <peak-or-death-year> website screenshot") — experiment and
     record what query shape yields the best matched candidates.
   - **Fetch strategy per accepted candidate**: try `murl` (original host) first
     with a per-host timeout; on failure fall back to the Bing thumbnail `turl`
     (tse hosts are reachable here); thumbnails may be requested at a larger width
     by adjusting the `w` parameter — prefer >= 500px when the host honors it.
     Every attempt (host, HTTP code, bytes) logged per subject.
   - Guards on the stored binary: magic bytes for jpeg/png/gif/webp; size floor
     (reject tiny spacer images), size cap 100KB preferred (pick the best
     candidate that fits; a larger original may be accepted ONLY from the laptop
     route and must be individually size-reported); min width ~300px where
     metadata allows checking.
   - Politeness: ~4s between subjects; single query per subject per run.
2. **Route 2 — Wikimedia Commons (license-clean; laptop-run)**: API search
   (`commons.wikimedia.org/w/api.php`, generator=search, namespace 6,
   prop=imageinfo with extmetadata) for "<subject> screenshot"; accept only
   image/* mime; provenance includes the file page URL, author, and license short
   name from extmetadata; attribution rendered on the plate (CC-BY family needs
   author + license visible — we render both). Unreachable from this box: code
   path implemented and unit-tested, live-verified on the laptop.
3. **Route 3 — archived-page render (kept, last)**: the existing browser path
   stays available (CI with Chrome, or the operator's Mac once the probe passes);
   it runs only when routes 1-2 yield nothing, and the auto-probe gates it as
   today.
4. **Mode semantics and truthfulness**: search-sourced and Commons-sourced images
   are NOT claimed as our own renders. Front matter: `illustration: sourced-image`
   with `image_source: bing-image-search | wikimedia-commons`, source page URL,
   image URL, retrieval date; plate labels accordingly ("Historical image: Bing
   image search" with source host, or "Via Wikimedia Commons, <license>"). The
   existing `screenshot` mode is reserved for archive renders. The about page
   illustration policy is updated to describe all three sources honestly.
5. **CLI**: a `--fetch-images` mode runs the route cascade (bing -> commons ->
   render); `--fetch-screenshots` remains as an alias for the render-only path;
   README documents both plus per-route env toggles.
6. **THE GOAL OF THIS TASK: land real images now.** If Route 1 works end-to-end
   from this box (probes say it should), actually run it for all 20 subjects,
   store the binaries under `assets/images/<slug>.<ext>` (source assets the
   builder copies, like styles.css), rebuild, and ship real plates in this
   commit. Subjects with no acceptable matched candidate stay on generated art —
   honestly labeled as before. Record the per-subject outcome table in RESULT.md.
7. **Licensing note, on the record**: search-result images are of varying rights;
   the operator chose this route by instruction; every plate carries source-page
   attribution and the README documents the rights posture and the swap path
   (Commons route, license-clean). Do not strip or obscure attribution anywhere.
8. Docs (README route docs + troubleshooting + licensing; about-page policy),
   knowledge merge (Bing parse recipe + reachability map update in
   `dead-web-source-catalog.md`; route-cascade pattern in
   `post-generation-pipeline.md`), INDEX sync, RESULT.md records, verify-suite
   extension for the new mode (mode/binary/label consistency, plate attribution
   presence for sourced images), tests for parse/match/guards (live-loopback
   where feasible; the Bing parser can be tested against a saved fixture of the
   real HTML you fetch during the live run — store a SMALL sanitized fixture
   under tests/fixtures/, under the size gates).

## Completion criteria

- [ ] Route 1 implemented and, if the network permits, executed live from this
      box: per-subject outcome table in RESULT.md; binaries stored and shipped for
      accepted subjects; strict-match rejects recorded.
- [ ] Route 2 implemented, unit-tested with fixtures, documented for the laptop;
      attribution fields plumbed to plate rendering.
- [ ] Route cascade order + env toggles + CLI documented; render route gated by
      the probe as before.
- [ ] Mode semantics honest (sourced-image vs screenshot), about-page policy
      updated, plate attribution visible for every sourced image.
- [ ] Binary guards enforced (magic, floors, caps, width when known); per-binary
      size report in RESULT.md; nothing over 100KB unless individually flagged.
- [ ] Verify suite extended and ALL CHECKS PASS; tests green; post bodies
      byte-identical (additive front matter only); RESULT.md within gate (rotate
      per policy if needed).
- [ ] Docs + knowledge merged + INDEX synced; Task file completed honestly
      (including anything only verifiable on the laptop).
- [ ] Usual rules: English; ASCII text; no emoji; no check-mark glyphs (U+2713,
      U+2714, U+2705, U+2611 family); no text file over 100KB; stdlib only; no
      git; no network beyond bing.com/cn.bing.com/tse hosts, wikimedia endpoints
      (attempt), existing keyless endpoints, and loopback.

## Context and constraints

- **Write boundaries**: this Task file; `artifacts/writing/internet-archaeology-blog/`
  (including `assets/images/` and `tests/fixtures/`); `knowledge/writing/`.
  Nothing else. No git; no `.github/`.
- Post bodies frozen; additive front matter only.
- If Bing's layout serves different metadata from this network (cn.bing.com),
  parse defensively (attribute shape may vary) and record what you saw; the
  parser must fail closed (no candidate -> generated art), never store an
  unmatched image.
- Truthfulness law: an image is stored only for a matched subject with recorded
  provenance; anything unverifiable stays generated.
- Fastest context load: `pipeline/screenshots.py` (guards, provenance, modes),
  `run.py`, `pipeline/site.py` (plate rendering), `archive/tasks/blog-render-profile-fix.md`,
  README screenshot section.

## Execution steps

<!-- Subagent fills -->

Preparation (retrieval flow summary, 2026-08-29):

- Knowledge: `knowledge/writing/dead-web-source-catalog.md` (reachability split
  Algolia live / Wikipedia + archive unreachable from this box; render-don't-
  fetch law), `knowledge/writing/post-generation-pipeline.md` (truthful-images
  section: two-mode labeling, layered payload guards, additive front matter
  with body-hash post-condition, binary gate split, never-clobber binaries).
- Handbook: only `handbooks/README.md` exists; no domain handbook applies.
- Code context loaded: `pipeline/screenshots.py` (guards, front-matter editor,
  era-anchor year rule), `run.py` (CLI, verify suite, RESULT rotation policy),
  `pipeline/site.py` (plate caption / provenance / art_for mode logic),
  `tests/test_screenshots.py` (test conventions, loopback-server patterns).
- Own probes this run (recorded for the knowledge merge): `www.bing.com`
  reachable; `/images/search?q=...` 302s to `cn.bing.com` and the server-
  rendered grid there is BOT-FILLER JUNK for our queries (cat memes for
  "GeoCities", anime wallpapers for "Winamp"; 0/35 candidates matched) while
  the page title/chrome echo the right query. The REAL result set comes from
  the async endpoint `www.bing.com/images/async?q=...&first=0&count=35&
  mmasync=1`: 35 candidates, 33/35 strict-matching "GeoCities website
  screenshot", including era screenshots (webdesignmuseum.org). Thumbnail
  hosts `ts2/ts3/ts4.mm.bing.net` answer 200; `pid=15.1&w=600` honors the
  width param (600x768 jpeg measured); `pid=Api` ignores it. One original-host
  murl measured 403 (hotlink protection) -- the murl-then-turl cascade is
  required. Wikimedia endpoints expected unreachable here (to be probed once).

Plan:

1. Probe Wikimedia Commons once from this box; record the failure verbatim
   (Route 2 is laptop-only here).
2. Experiment with query shape (`<name> website screenshot` vs `<name> <year>
   website screenshot`) on 4 subjects via the async endpoint; record matched
   counts; pick and document the winner.
3. Implement `pipeline/imagesearch.py`: Bing route (async fetch with desktop
   UA + redirects, `iusc` m="..." parse with HTML-unescaped JSON, strict
   subject match on name/alias/domain in title/purl, deterministic ranking,
   murl-then-turl(w>=500) fetch, magic/floor/width/size guards, ~4s
   politeness), Commons route (API + extmetadata + attribution fields,
   fixture-testable), front-matter stamping (`illustration: sourced-image`,
   `image_source`, `image_page_url`, `image_url`, `image_retrieved`, commons
   license/author) with body-hash post-condition, never-clobber binaries under
   `assets/images/`.
4. Wire `run.py`: `--fetch-images` cascade (bing -> commons -> probe-gated
   render) with env toggles; `--fetch-screenshots` stays the render alias;
   verify-suite extension (sourced-image mode/binary/label consistency,
   attribution presence, images-dir binary gate, orphan guard); rebuild
   plumbing for `assets/images/` in `site.py` (art_for, plate caption,
   provenance rows, about-page policy).
5. Save a small sanitized ASCII fixture under `tests/fixtures/` from the real
   fetch; write `tests/test_imagesearch.py` (parse/match/rank/guards/attrs/
   loopback attempt + site consistency).
6. Run Route 1 LIVE for all 20 subjects; store binaries; rebuild; verify
   ALL CHECKS PASS; unit tests green; post bodies sha256-identical.
7. Docs: README (routes, troubleshooting, licensing posture + attribution
   policy + swap path), about-page policy; RESULT.md per-subject outcome
   table + binary size report (rotate if past gate).
8. Knowledge merges + INDEX sync; complete Task conclusions.

## Execution log

<!-- Append after each subagent iteration -->

| Round | Date       | Progress | Notes |
| ----- | ---------- | -------- | ----- |
| 1 | 2026-08-29 | Retrieval + probes + plan written | KEY FINDING: cn.bing.com /images/search grid is bot-filler junk (0/35 matched for two test queries); the mmasync=1 async endpoint serves the real 35-candidate set (33/35 strict matches). tse thumbnails honor `pid=15.1&w=600`; one murl 403s -- murl-then-turl cascade required. |
| 2 | 2026-08-29 | Commons probed (SSL handshake timeout from this box -- laptop-only, recorded); query-shape experiment: era-year form wins (matched counts equal or better on all 4 subjects, 4-vs-0 on pets-com) | Query shape locked: "<name> <era-year> website screenshot", era year from the existing peak>death>launch anchor. |
| 3 | 2026-08-29 | pipeline/imagesearch.py implemented (Bing async route, strict match with raw-title matching + non-ASCII-run separation, deterministic ranking, murl-then-turl(w=600) fetch, magic/dims/floor/cap guards, Commons API + extmetadata + license-required rule, additive front-matter stamping); site.py sourced-image mode (plate labels, provenance link row, about policy for three sources); run.py --fetch-images cascade + env toggles + verify extension; sanitized ASCII fixture (5.7KB) from the real fetch; tests/test_imagesearch.py (32 tests) | Full suite 87 tests OK (was 55). Fixed during tests: webp VP8L outer length guard; descriptor-protocol trap (class-attribute function restore became a bound method); strict match now runs on RAW titles with non-ASCII runs as separators (folding had glued "GeoCities"+CJK into a non-match). |
| 4 | 2026-08-29 | LIVE Route 1 run #1: 5 subjects stored (aim, altavista, cuil, delicious, digg), then a crash on etoys -- a candidate murl contained raw spaces and http.client raised InvalidURL (not in the except set) | Fixed: URLs percent-encoded before request (_clean_url), InvalidURL/ValueError/OSError caught, and stored front-matter URLs ASCII-validated via the same path. |
| 5 | 2026-08-29 | LIVE Route 1 run #2 (resumed): all 20/20 subjects stored real strict-matched images; post bodies sha256-identical; site rebuilt; per-subject outcome table + binary size report appended to RESULT.md (39.8KB, within the rotation gate) | Commons never reached (bing 20/20); render probe passed pre-flight but never needed. |
| 6 | 2026-08-29 | Verify extension debugging: two honest failures fixed -- source-page URL with query string renders HTML-escaped (& -> &amp;) so the literal check needed the escaped form; about-policy check updated for the new three-source heading | --verify 475 checks ALL PASS; 87 unit tests OK; README routes/troubleshooting/licensing updated; knowledge merges done (dead-web-source-catalog.md Bing recipe + reachability; post-generation-pipeline.md cascade item 13) with INDEX sync. |

## Conclusions and output

**The goal of the Task is met: real images shipped in this commit.** All 20
subjects carry a real, strict-matched, attributed historical image acquired
LIVE from this box via Route 1 (Bing image search, async endpoint). Zero
subjects stayed on generated art; the Commons and render routes were never
needed (bing stored 20/20). Post bodies proven byte-identical (sha256) across
the additive front-matter stamps. `--verify`: 475 checks ALL PASS. Unit
tests: 87 OK (32 new). RESULT.md at 39.8KB, within the rotation gate.

Per-subject outcome (full table with queries, match counts, source hosts,
and fetch paths in RESULT.md, run entry "fetch-images per-subject outcome
table"):

| subject | stored | bytes | subject | stored | bytes |
| --- | --- | --- | --- | --- | --- |
| aim | aim.webp | 18844 | msn-messenger | msn-messenger.jpg | 58800 |
| altavista | altavista.jpg | 41338 | myspace | myspace.jpg | 53404 |
| cuil | cuil.jpg | 51016 | napster | napster.jpg | 31392 |
| delicious | delicious.jpg | 16753 | newgrounds | newgrounds.webp | 72320 |
| digg | digg.png | 76255 | pets-com | pets-com.jpg | 17963 |
| etoys | etoys.jpg | 10823 | posterous | posterous.png | 64842 |
| friendster | friendster.jpg | 39191 | somethingawful | somethingawful.jpg | 18999 |
| geocities | geocities.webp | 69008 | stumbleupon | stumbleupon.jpg | 21102 |
| google-plus | google-plus.jpg | 15744 | vine | vine.jpg | 21206 |
| google-reader | google-reader.jpg | 96323 | winamp | winamp.jpg | 21646 |

Binary weight: 816969 bytes across 20 files under
`artifacts/writing/internet-archaeology-blog/assets/images/` (largest
google-reader.jpg at 96323 bytes; nothing over the 100KB cap, so nothing
needs the individual over-cap flag). Binaries are copied into
`site/assets/` by the builder; every plate prints the mode label plus the
source-page host, and the provenance box carries the full source-page URL
as a link, the image URL, and the retrieval date (2026-08-29).

Key decisions and findings:

1. **The async endpoint is the real Bing.** The plain `/images/search` page
   serves bot-filler junk from this network (0/35 matched on two test
   queries); `www.bing.com/images/async?q=...&first=0&count=35&mmasync=1`
   serves the real 35-candidate set. Recorded in the knowledge catalog.
2. **Query shape**: "<name> <era-year> website screenshot" (era year from
   the existing peak>death>launch fact-sheet anchor) -- equal-or-more strict
   matches on all 4 experimented subjects.
3. **Third plate mode `sourced-image`** with honest labels ("historical
   image: Bing image search" / "via Wikimedia Commons, <license>");
   `screenshot` stays reserved for archive renders; about page states the
   three-source policy and the rights posture in public.
4. **Route 2 (Commons) is implemented and fixture-tested but laptop-only**
   from this network (SSL handshake timeout, recorded verbatim in RESULT.md
   run entries). It is fail-closed: a file without a license short name is
   never stored; author + license are plumbed to the plate.
5. Two live-run bugs found and fixed: candidate URLs with raw spaces
   (InvalidURL crash mid-run; now percent-encoded pre-request), and the
   verify attribution check needing the HTML-escaped URL form.

What remains laptop-only / for the operator:

- **Commons route live run** (needs wikimedia egress):
  `GAZETTE_BING=0 GAZETTE_RENDER=0 python3 run.py --fetch-images` after
  deleting any `assets/images/<slug>.<ext>` meant to be replaced -- then
  `--rebuild-only` and `--verify`.
- **Render route**: unchanged, probe-gated; `--probe-render` remains the
   10-second first check on the operator's Mac.
- Pixel-level appearance of the found images was not eyeballed (no browser
  screenshot tooling here); structural rendering is verified (img tag,
  labels, links, dimensions parsed from the stored binaries).

Verification status: `--verify` 475 checks ALL PASS (mode/binary/label
consistency for sourced-image plates, attribution visibility, orphan-binary
guards, glyph/size/binary gates, clean-state byte-identical rebuild,
mounted-subpath serving in both modes); 87 unit tests OK; post bodies
sha256-identical. Laptop-only items are listed above and nowhere claimed
done.

## Knowledge-capture suggestions

Captured (see the files):

- `knowledge/writing/dead-web-source-catalog.md` -- new "Bing image search:
  the async endpoint is the real one" section (bot-filler junk-grid trap,
  mmasync recipe, query shape, murl/turl strategy with w-param behavior,
  raw-space URL hazard) plus the reachability map update (bing live;
  duckduckgo/google/wikimedia unreachable from this box) and change history.
- `knowledge/writing/post-generation-pipeline.md` -- truthful-images item
  13 (the acquisition cascade pattern: route ordering, the sourced-image
  mode contract, strict raw-title matching, shared guards, fixture
  practice, escaped-URL attribution checks, descriptor-protocol and
  InvalidURL traps), reuse-checklist addition, verification entry, change
  history; INDEX.md one-liners synced.

Not captured (single-use facts live in RESULT.md): the per-subject outcome
table and the binary size report.

Handbook suggestion (for Eve to review; none edited by me): no handbook
exists yet for this domain. If one is created later, the acquisition-
cascade checklist from `post-generation-pipeline.md` item 13 is the natural
seed.
