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
    python3 run.py --fetch-images
                                # image-search acquisition cascade per
                                # subject: Bing image search (strict subject
                                # match, source attribution) -> Wikimedia
                                # Commons (license-clean) -> the probe-gated
                                # archived-page render; every attempt logged
                                # in RESULT.md; failures degrade to the
                                # labeled generated plate -- never a
                                # stand-in image
    python3 run.py --fetch-screenshots
                                # render-only alias: archived-page render for
                                # every subject with a headless browser
                                # (located via CHROME_BIN or a PATH probe;
                                # needs egress to web.archive.org); every
                                # attempt logged in RESULT.md; failures
                                # degrade to the labeled generated plate
    python3 run.py --verify    # structure + gate checks + mounted-subpath
                                # serving test; prints PASS/FAIL

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
      imagesearch.py           optional stage: image-search acquisition
                               (Route 1 Bing async endpoint; Route 2 Wikimedia
                               Commons; strict subject match + binary guards)
      screenshots.py           optional stage: real Wayback Machine screenshots
                               (Route 3, render-don't-fetch)
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
    assets/
      screenshots/             archived-page render binaries (source assets;
                               .png/.jpg only; the builder copies them into
                               site/assets/; never clobbered by re-runs)
      images/                  sourced-image binaries from the search/Commons
                               routes (.png/.jpg/.jpeg/.gif/.webp; same
                               copying and never-clobber rules)
    tests/
      test_screenshots.py      render-route unit tests (loopback where feasible)
      test_imagesearch.py      image-search unit tests (fixture + loopback)
      fixtures/                sanitized real-fetch HTML for parser tests
    site_config.json           base_url + titles/description + path_prefix
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
- No JavaScript anywhere; internal links are page-relative by default (the
  site renders via file://) or prefix-absolute when `path_prefix` is set
  (see the mounting note above); every mode is exercised by `--verify`.
- The index is a lead-plus-register layout (decision D10, added when the
  corpus reached 20 posts): category chips with counts, one lead card for
  the newest dispatch, then a compact complete-dispatch list -- every post
  one click from the front page, scannable at any corpus size.
- `site/rss.xml` is built from the published posts. Link origins come from
  `base_url` in `site_config.json`. The documented default is the
  placeholder `https://example.org/dead-web-gazette` -- no real domain
  exists yet; set `base_url` to the real origin (no trailing slash) when
  the gazette is hosted, then rebuild.

**Mounting under a subpath (`path_prefix`).** The default build uses
page-relative refs (`styles.css`, `../styles.css`), which work via `file://`
and on any conforming static server (including a server that 301-redirects
`/site` to `/site/`). If your production server serves the index at a
subpath URL **without** that trailing-slash redirect (some rewrites and
static hosts do), page-relative refs resolve against the host root and the
stylesheet 404s -- the reported "style missing under localhost/site/"
failure mode. For those servers, set `"path_prefix": "/site/"` in
`site_config.json` and rebuild: every internal href/src is then emitted
prefix-absolute (`/site/styles.css`, `/site/posts/<slug>.html`) from every
page depth, and RSS links combine `base_url` + prefix. `run.py --verify`
exercises both modes by serving the site over real HTTP under a subpath
(mounted-subpath test) and asserting every internal reference answers
HTTP 200.

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

Every post carries exactly one plate, and the plate's mode is part of the
published page (decision D11 in `docs/design.md`). Three plate kinds, no
middle state:

- **Sourced-image plates** ("historical image: Bing image search" / "via
  Wikimedia Commons, <license>") are real image files found through image
  search or a license-clean repository, stored only when the title or source
  page of the candidate actually names the subject, and attributed on the
  plate: the source-page host rides in the visible label, the full source
  page URL rides as a link in the post's PROVENANCE box, and the retrieval
  date is recorded in front matter and printed. Produced by Route 1/2 of
  `run.py --fetch-images` (see the cascade below); binaries live under
  `assets/images/<slug>.<ext>` and are copied into `site/assets/` like the
  stylesheet.
- **Screenshot plates** are pixels a real headless browser rendered from the
  subject's real archived page. `run.py --fetch-screenshots` (the render
  route, also Route 3 of the cascade) resolves a
  representative snapshot (the earliest status-200 capture in the CDX index,
  falling back to Wayback's era-anchored nearest-capture form
  `/web/<YYYY>/<original-url>`, where YYYY comes from the subject's own fact
  sheet -- a peak, death, or launch year -- so the fallback lands inside the
  subject's life instead of on whatever the domain serves today; the
  `/web/2/` form, which resolves to the MOST RECENT capture, is used only
  when a sheet carries no year), then screenshots
  `https://web.archive.org/web/<ts>/<original-url>`. The page then prints a
  visible label -- "screenshot: Wayback Machine, snapshot <ts>, fetched
  <date>" -- plus the provenance (subject URL, rendered URL, timestamp, fetch
  date) in the post's front matter and PROVENANCE box. When the render came
  through a nearest-capture fallback and the redirect did not resolve to a
  timestamp, the label says "nearest capture" instead of a date -- never an
  invented one, and never the anchor year presented as a snapshot date.
  Stored binaries are never clobbered; delete
  `assets/screenshots/<slug>.<ext>` to refetch one.

  History, so nobody re-walks the dead end: the original implementation
  called the documented screenshot service
  `https://web.archive.org/screenshot/<url>`. An operator run from a network
  with archive egress (2026-08-29) recorded **HTTP 404 with an HTML error
  page for all 20 subjects** -- the service is dead, and the fetcher no
  longer calls it. The same run recorded CDX answering only 5 of 20 lookups
  inside 5s, which is why the CDX client now uses a 25s timeout, one retry,
  a circuit breaker after repeated transport failures, and a ~4s
  inter-subject delay (raised from 2s after one run drew five HTTP 503
  challenge pages; the pre-check also backs off ~15s and retries once on a
  503). A second laptop run the same day resolved 17/20 timestamps but lost
  **every render** to a 45s wall kill: a `--virtual-time-budget`-only
  invocation never fires a capture while a Wayback subresource is still
  loading. The render now carries Chrome's own `--timeout` -- the browser
  writes the screenshot when the budget expires regardless of load state,
  and its filtered stderr lands in the failure log (see the render recipe
  below). One caveat is calibrated and honest: on the reference chromium
  (150, new headless) the timeout capture of a never-loading page is a
  blank frame, which the near-blank guard rejects -- such a subject still
  degrades, but the log then says exactly that, with chrome's own
  "Page load timed out" line, instead of a silent wall kill. A third laptop
  run then hung differently -- every render killed at the 75s wall guard
  with nothing but chrome/updater crash-handler noise on stderr -- while
  running the code that already passes a fresh temp `--user-data-dir` per
  render, so the classic default-profile lock does not explain it. That is
  the environment-divergence case the self-probe (`--probe-render`, below)
  and the troubleshooting table exist for: the recipe is
  environment-independent and self-verifying, and the probe lets the
  operator's own browser prove it in seconds.
- **Generated plates** are the procedural 760x420 "mini homepage" SVGs from
  `svgart.py`, seeded with a CRC32 of the slug (starfield, bevel frame,
  88x31 buttons, hit counter, barricade stripes), labeled "generated
  memorial art" on the page. The same slug always reproduces the same
  artwork (asserted by `--verify`).

There is no middle state. A subject with no acceptable, attributable image
ships the generated plate and says so on the page. `--verify` asserts mode
agreement across front matter, plate label, rendered art, and stored
binaries, so nothing can be mislabeled. SVGs are inlined into the HTML and
also saved standalone under `site/assets/`; image and screenshot binaries
are copied into `site/assets/` by the builder like the stylesheet. Stored
binaries are never clobbered; delete `assets/images/<slug>.<ext>` (or
`assets/screenshots/<slug>.<ext>`) to refetch one.

### The image-search cascade (`run.py --fetch-images`)

Route order per subject -- the first route that stores a binary wins:

1. **Route 1 -- Bing image search** (primary; proven live from the build
   box). The pipeline queries
   `www.bing.com/images/async?q=<query>&first=0&count=35&mmasync=1` with a
   desktop UA and parses the server-rendered `class="iusc" m="..."` JSON
   (title `t`, original image `murl`, Bing thumbnail `turl`, source page
   `purl`). Two things learned the hard way (also recorded in
   `knowledge/writing/dead-web-source-catalog.md`):
   - the plain `/images/search` page 302-redirects to cn.bing.com from this
     network and serves **bot-filler junk** in its server-rendered grid (cat
     memes for "GeoCities", anime wallpapers for "Winamp"; 0/35 candidates
     matched while the page title echoed the right query). The async
     endpoint above serves the real candidate set.
   - the query shape is `<name> <era-year> website screenshot`, where the
     era year is the same deterministic peak>death>launch anchor the render
     route uses (read from the subject's own fact sheet). Experiment on 4
     subjects: the era-year form matched equal-or-more strict candidates on
     every subject (4-vs-0 on pets-com) and raised era-relevant hits.
   Per candidate: **strict subject match** (a word-boundary form of the
   subject name, an alias, or the domain must appear in the RAW title or
   the source page URL -- near-miss spellings like "Geocites" never match,
   short aliases like "aim" match only on word boundaries, and non-ASCII
   title runs count as separators so a CJK title glued to the name still
   matches); deterministic ranking (subject domain in the source page, era
   year visible, "screenshot" wording, direct image extension; stock-preview
   hosts demoted); then fetch **murl first, turl fallback** (some original
   hosts hotlink-protect with 403; the tse thumbnail hosts answer reliably
   and honor `pid=15.1&w=600` for a >=500px image).
2. **Route 2 -- Wikimedia Commons** (license-clean; needs wikimedia egress
   -- the build box gets an SSL handshake timeout, recorded in RESULT.md,
   so this route runs from the laptop). API search in namespace 6 with
   `prop=imageinfo&iiprop=url|size|mime|extmetadata`; only `image/*` mime;
   **a file without a license short name is never stored** (fail closed);
   author and license are stamped into front matter and printed on the
   plate as CC-BY-family attribution requires.
3. **Route 3 -- archived-page render** (the strategy documented below,
   unchanged): runs last, only when routes 1-2 stored nothing, and stays
   probe-gated -- `--fetch-images` runs the same fail-fast pre-flight
   render probe, and a failed probe skips the render route for every
   subject (routes 1-2 are still attempted).

Env toggles: `GAZETTE_BING=0`, `GAZETTE_COMMONS=0`, `GAZETTE_RENDER=0`
disable a route for a run (default all on) -- e.g. from the laptop,
`GAZETTE_BING=0 GAZETTE_RENDER=0 python3 run.py --fetch-images` runs the
Commons route alone. Politeness: ~4s between subjects, one search query per
subject per run.

Binary guards on anything stored (both routes): magic bytes
(jpeg/png/gif/webp), parseable dimensions with width >= 300px, a 6KB floor
against spacer/tracking images, and a hard 100KB cap from this box (larger
originals are a laptop-route concern and must be individually size-reported
there). Every attempt (host, HTTP code, bytes, rejection reason) lands in
RESULT.md; any doubt degrades that subject to the labeled generated plate.

**Licensing posture (on the record).** Search-result images are of varying
rights; the operator chose this route by instruction. The gazette's posture
is attribution-first: every sourced plate names and links its source page,
nothing strips or obscures attribution, and every sourced image can be
swapped for a license-clean Commons file (Route 2) or removed without
touching the written record. The about page states the same policy in
public. Screenshot plates remain reserved for actual archive renders -- a
found historical image is never labeled a screenshot.

### Producing real screenshot plates (the operator / laptop run)

**Run `python3 run.py --probe-render` first on any new machine** (it is the
first line of the block below). It renders an offline `data:` page through
the exact production invocation -- fresh temp profile included -- and
validates the PNG (magic, 1024x640 window, a non-blank floor calibrated at
blank 3301 / real probe page 10990 bytes on the reference chromium). No
network, ~1s when healthy: it proves THIS browser can run THIS recipe
headlessly before any subject time is spent. `--fetch-screenshots` runs the
same probe automatically and stops before the first subject if it fails.

The fetch stage needs a **headless-capable browser binary** on the machine
that has egress to `web.archive.org`, plus ~20-50 minutes for 20 subjects
(each subject: a CDX lookup allowed up to 25s plus one retry, an archived-page
pre-check at 20s that backs off ~15s and retries once on an HTTP 503
challenge, a browser render bounded by Chrome's own 30s `--timeout` under a
75s wall guard, and a 4s inter-subject pause; slow CDX lookups are the usual
cost, and a CDX miss of any kind -- timeout, no status-200 row, or the
circuit breaker after repeated transport failures -- falls back to Wayback's
era-anchored nearest-capture form
`https://web.archive.org/web/<YYYY>/<canonical-url>`, where YYYY is read
from the subject's fact sheet -- the first fact matching a peak phrasing
(the remembered era), else a death phrasing (the last days of the real
site), else a launch phrasing; the `/web/2/` form, which resolves to the
MOST RECENT capture Wayback has (for a dead, parked domain that is the
parked page), is used only when the sheet carries no year at all).

The exact render invocation (constants in `pipeline/screenshots.py`;
`WINDOW_SIZE` 1024x640, `VIRTUAL_TIME_BUDGET` 10000, `CHROME_TIMEOUT_MS`
30000, `RENDER_TIMEOUT` 75s outer guard):

    --headless=new --screenshot=<tmp>/shot.png --window-size=1024,640 \
    --virtual-time-budget=10000 --timeout=30000 --hide-scrollbars \
    --disable-gpu --no-first-run --no-default-browser-check \
    --disable-crash-reporter --disable-component-update \
    --disable-background-networking \
    --user-data-dir=<fresh temp profile, created and removed per render> \
    <archived-page-url>

Environment independence, flag by flag: every render runs in its OWN fresh
temp `--user-data-dir` (created and removed per render), so nothing depends
on the machine's browser/profile state or on whether the daily browser is
running; `--no-first-run` / `--no-default-browser-check` suppress first-run
dialogs; the `--disable-*` trio keeps the crash reporter, component updater,
and background networking from spawning helpers at all (fewer processes,
less stderr noise, no updater side-trips mid-batch).

Why both budgets: `--virtual-time-budget` settles timers but **never fires a
capture while a network load is pending** (measured on the reference
chromium against a page with one hanging subresource: no exit, no file,
killed at the wall); `--timeout` is the mechanism that actually captures --
the browser exits at ~timeout+1s and always writes the PNG. The 75s wall
guard exists only for a browser that ignores the flag, and kills the process
group. Chrome's stderr rides along in every failure line with the
chrome/updater noise lines filtered out and BOTH the first ~400 and last
~500 chars kept; when nothing survives the filter and no file was written,
the report says so explicitly and points at `--probe-render` (an all-noise
stderr with no file is itself a signature -- see the table below). A render
captured at timeout is flagged in the log, so the next run diagnoses itself.

Browser resolution order, printed as the first line of every run:

1. `$CHROME_BIN` when it points at an executable file (a broken CHROME_BIN is
   reported with the fix, never silently ignored);
2. a PATH probe of `google-chrome`, `google-chrome-stable`, `chromium`,
   `chromium-browser`, `msedge`, `chrome`, `edge`;
3. the macOS app bundles for Chrome, Chromium, and Edge.

The whole run is one copy-paste block (search/Commons cascade first; the
render-only alias stays below it):

    cd /path/to/internet-archaeology-blog
    python3 run.py --fetch-images        # bing -> commons -> render cascade
    python3 run.py --rebuild-only
    python3 run.py --verify

    # render-only (the old alias), or Commons alone from a network with
    # wikimedia egress:
    export CHROME_BIN="$(command -v google-chrome || command -v google-chrome-stable \
      || command -v chromium || command -v chromium-browser || command -v msedge)"
    python3 run.py --probe-render
    python3 run.py --fetch-screenshots
    # GAZETTE_BING=0 GAZETTE_RENDER=0 python3 run.py --fetch-images

Notes for that run:

- On macOS the `export` line usually comes up empty; that is fine -- unset or
  empty `CHROME_BIN` falls through to the PATH probe and the app bundles.
- `--probe-render` is the 10-second health check of the browser environment;
  if it fails or hangs, fix that first (its message says how) -- the fetch
  run would stop on the same failure anyway, by design.
- `--fetch-screenshots` already rebuilds the site at the end;
  `--rebuild-only` is included as an explicit, idempotent safety line.
- Optional, before or after: `python3 -m unittest discover -s tests -v`
  (offline unit tests for the URL construction and era anchoring, the render
  flag contract, the stderr filter, the fresh-temp-profile lifecycle, the
  probe, the 503 backoff, payload guards, browser detection, front-matter
  editor, and scratch-build consistency; the local-render tests -- including
  a stalled-subresource regression case that reproduces the "never finished
  loading" failure with a hanging loopback subresource -- are skipped
  automatically when no browser exists).
- Every stored plate survives four guards before it is written: the archived
  URL must answer HTTP 200 and look like a Wayback playback page, the render
  must be a PNG with exactly the 1024x640 window, and it must clear a
  calibrated near-blank size floor (a blank page renders ~3KB and a browser
  error page ~22KB on the reference chromium; real content lands far higher).
  Anything else degrades that subject to the labeled generated plate with the
  reason in RESULT.md. A subject whose render is rejected can be retried by
  simply re-running (nothing was stored), or by deleting
  `assets/screenshots/<slug>.png` first if a previous run stored one.
- If no browser is found at all, the run degrades **once** with the message
  `browser: none found -- set CHROME_BIN=... or install ...`, touches no
  network, and leaves every post on the labeled generated plate.

### Troubleshooting by observed signature

Every render failure line carries Chrome's filtered stderr (head ~400 +
tail ~500 chars, chrome/updater noise dropped); match what you see against
this table before changing anything:

| Observed signature | Most likely cause | What to do |
| --- | --- | --- |
| `bing search: no iusc metadata parsed (layout change or block page)` for every subject | the async endpoint changed shape, or this network/proxy started serving a block page instead of results | fetch the endpoint by hand and compare with `tests/fixtures/bing_images_async_geocities.html`; if the `m="..."` JSON keys changed, update `parse_candidates` (it fails closed -- nothing is stored on parse doubt) |
| `bing search: N candidates parsed, 0 strict subject matches ...` for one subject | no candidate's title or source page actually names the subject (strict match doing its job) | honest degradation by design; try re-running later (results rotate) or accept the generated plate -- never loosen the matcher to "close enough" |
| `murl <host>: HTTP 403` then `stored <slug>.<ext> via turl` | the original host hotlink-protects (measured on webdesignmuseum.org) | nothing to do; the tse-thumbnail fallback carried it and the provenance keeps the source-page URL |
| `commons search: URL error (... handshake ...) from commons.wikimedia.org` | wikimedia egress blocked from this network (the build box; recorded in RESULT.md) | run the Commons route from the laptop: `GAZETTE_BING=0 GAZETTE_RENDER=0 python3 run.py --fetch-images` |
| `image NNNNN bytes rejected (image ... over ... cap)` | a candidate larger than the 100KB hard cap from this box | by design; the next candidate (usually the tse thumbnail) is tried; a deliberately larger original is a laptop-route concern |
| `wall guard killed the process group ... chrome stderr: filtered stderr is empty ...` -- the raw stderr was only crash-handler / updater VERBOSE noise, no file was written, typically on a machine whose daily browser is running | the browser stalled before rendering. Not the classic default-profile lock in this code -- every render already passes a fresh temp `--user-data-dir`; suspects are app-bundle singleton behavior, flag-set divergence in that Chrome channel, or helper interference | run `python3 run.py --probe-render` (seconds, offline). If it fails or hangs, point `CHROME_BIN` at a chromium build, or close the running browser once and re-probe; the fetch run runs this probe automatically and stops early |
| `Page load timed out ... bytes written` followed by `rejected: png only N bytes (< ... floor)` | slow archived page: Chrome captured at its `--timeout` before the page composited (new headless does not composite a never-loading page) | raise `CHROME_TIMEOUT_MS` in `pipeline/screenshots.py` (e.g. 60000) and re-run for just those subjects (nothing was stored) |
| `rejected: png only N bytes (< floor)` with no timeout line | blank or browser-error render (wrong-page capture, error page) | the guards did their job; check the subject's `archived_url` in RESULT.md and re-run that subject |
| `png is WxH, expected 1024x640` | render-window drift (a flag or constant changed) | compare the invocation above with `browser_cmd()`; fix the constant or the window flag |
| `archived page pre-check: HTTP 503 ... (503; backed off and retried once)` | Internet Archive challenge / rate limit | wait a while and re-run; the 4s spacing and the 15s backoff are already in place |
| `cdx: timeout` / `cdx: URL error` lines until `circuit open` | CDX index slow or unreachable from that network | subjects still render through the era-anchored fallback; re-run when CDX answers, or accept the fallback captures |
| `pre-flight render probe: FAIL -- ...` and the batch stops before subject 1 | the browser cannot run this recipe headlessly at all | read the probe's hint (same as row 1); fix the browser environment first |

**Coordination with an existing clone.** A previous laptop run appended its
own entries to this repository's `RESULT.md` and may have left local
artifacts. Pull before re-running, and if your clone recorded a run that this
repository never saw, expect `RESULT.md` to differ until the operator
reconciles the two histories (do not attempt to reconcile from inside the
pipeline). If `RESULT.md` approaches the 100KB text gate, the fetch run
automatically appends a condensed outcome summary instead of per-subject
lines and says so in the entry; past that, the documented rotation policy
applies: when `RESULT.md` exceeds ~60KB, move all but the newest
verification-methods section and the last ~10 run entries into the next
`docs/result-log/archive-<N>.md` (nothing is deleted -- `archive-1.md`
already holds the 2026-08-29 v0-through-render-timeout-fix history, moved
when the file reached 99.6KB), and `run.py` prints a rotation note once the
threshold is passed.

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
- Real archive renders cannot be produced from this build environment
  (web.archive.org is network-unreachable here -- connections hang until
  timeout; see RESULT.md for every recorded attempt, including the full
  render-path rehearsal that degrades 20/20). Sourced historical images CAN
  be produced here: Route 1 (Bing image search via the async endpoint) is
  live from this box and shipped real plates in the 2026-08-29 run; see
  RESULT.md for the per-subject outcome table. Route 2 (Wikimedia Commons)
  needs wikimedia egress and is laptop-run. The `--fetch-screenshots` render
  stage is likewise operator-runnable from any machine with a
  Chrome/Chromium-class browser and egress to web.archive.org. The browser
  machinery itself (subprocess invocation, payload guards) is exercised
  locally against loopback by the unit tests, including on this box, which
  does carry a chromium binary. Image and screenshot binaries are exempt
  from the 100KB-per-text-file gate by design and are individually
  size-reported in RESULT.md and by `--verify`; the operator decides whether
  to keep them in the repository.
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
