# Session 2026-08-29 15:38 UTC — Goal operate-internet-archaeology-blog, Task blog-image-search-route

## Trigger

Operator after three failed Mac render runs: "Perhaps we should take a different
route — rather than grabbing screenshots from web.archive.org, we can just search
for images using search engines to get the screenshots we need."

## Task handled

- Eve probed search-host reachability from THIS box first: bing.com reachable
  (images search 302 -> cn.bing.com, ~260KB server-rendered HTML with iusc/m
  metadata; tse thumbnail hosts 200); duckduckgo/wikimedia/google unreachable.
  Framed and dispatched `blog-image-search-route`; supervised to closure.

## Dispatched subagent

- `web-product-engineer`, 162 tool uses, the largest Task of the Goal.

## Key decisions and outputs

- **The pivot worked: 20/20 subjects now carry real historical images**, fetched
  live from this box via Bing image search, strict-matched (subject name/domain
  in candidate title or source page), stored under `assets/images/` (844KB total,
  largest 96KB), rebuilt into plates with visible attribution and a rights note.
- Key discovery (now in knowledge): the plain `/images/search` page serves
  bot-filler junk from this network (0/35 matched); the real candidate set comes
  from the `mmasync=1` async endpoint (33/35 matched). Query shape
  "<name> <era-year> website screenshot" won the experiment.
- Route cascade: Bing (primary) -> Wikimedia Commons (license-clean, laptop-only;
  author+license attribution plumbed) -> archived-page render (kept, probe-gated).
  CLI: `--fetch-images`; `--fetch-screenshots` remains the render alias; env
  toggles documented.
- Honest third mode `illustration: sourced-image` with `image_source`, source
  page + image URLs, retrieval date; plate labels "historical image: Bing image
  search" (with source host) vs "via Wikimedia Commons, <license>"; about page
  states the three-source policy and rights posture. `screenshot` mode stays
  reserved for archive renders.
- Two live-run bugs found and fixed en route: candidate URLs with raw spaces
  crashed http.client mid-batch (percent-encoding added); verify's attribution
  check needed the HTML-escaped URL form.
- 87 unit tests (32 new, on a sanitized real-fetch fixture); verify 475 checks
  ALL PASS; post bodies sha256-identical; RESULT.md at 39.8KB with the
  per-subject outcome table.

## Blockers and follow-up suggestions

- **By-eye QA remains the operator's**: Eve attempted to view three stored images
  but this environment's image reading uploads to a CDN instead of rendering —
  honestly recorded. One glance at `site/index.html` closes it (SC3).
- Licensing posture on search-result images documented in README (rights vary;
  attribution on every plate; Commons route is the license-clean swap, runnable
  from the laptop: `GAZETTE_BING=0 GAZETTE_RENDER=0 python3 run.py --fetch-images`
  after deleting a subject's `assets/images/<slug>.*` to force re-fetch).
- Operator gate FYI recorded: 20 binary images now sit in the baseline..HEAD
  diff; the operator's gate-3 emoji grep lacks a binary skip (-I) — random JPEG
  bytes may false-positive; operator's call.
- Next: cadence decision (SC1), discovery enrichment (SC2).

## Knowledge and handbook changes

- Knowledge: `dead-web-source-catalog.md` reachability map updated (bing.com +
  tse hosts reachable; the mmasync=1 recipe; wikimedia still unreachable here);
  `post-generation-pipeline.md` route-cascade pattern + truthful sourced-image
  mode; INDEX synced.
- Task archived to `archive/tasks/blog-image-search-route.md`; Goal progress log
  updated. Commit+push follows per the standing submit-when-finished instruction.
