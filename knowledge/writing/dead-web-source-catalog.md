---
subject: writing
slug: dead-web-source-catalog
tags: [dead-web, keyless-apis, hn-algolia, wikipedia-api, wayback-cdx, research-sources]
related_goals: [internet-archaeology-blog]
related_tasks: [blog-v0-pipeline, blog-screenshots-and-paths, blog-screenshot-renderer]
last_verified_date: 2026-08-29
status: active
---

# Dead-web research sources: keyless public APIs and their reachability

> A catalog of the three keyless public APIs used to research dead/old-web
> subjects, what each is actually good for, and which of them answer from this
> build environment -- so future runs know what will be live versus degraded
> before they write a line of code.

## Background and trigger conditions

Any Task that needs to discover or fact-check subjects from the dead and old
web (defunct sites, dead startups, old software) without API keys. Symptoms:
you are about to hardcode a Wikipedia fetch and do not know whether it will
answer, or you need citable reaction evidence for a shutdown story.

## Core conclusion

- **HN Algolia** (`https://hn.algolia.com/api/v1/search`, keyless): the
  workhorse. Story search with `tags=story` and `numericFilters=points>50`
  returns title, date, points, comment count, and a permanent item URL --
  directly citable as reaction evidence. Answered live from this environment.
- **Wikipedia API** (`https://en.wikipedia.org/w/api.php`): category members
  for defunct-site lists, intro extracts for fact sheets. Unreachable from
  this build environment (connection-level failure); code the path, but never
  rely on it here.
- **Wayback CDX** (`http://web.archive.org/cdx/search/cdx`): domain lifespan
  from first/last snapshot timestamps. Also unreachable from this
  environment.
- Therefore: design every fetch with a short timeout and a recorded fallback,
  and store the per-source live/offline status with each artifact so no
  output overstates its sourcing.

## Detailed explanation

### What each source gives you

| Source | Endpoint shape | Best used for | Citable output |
| ------ | -------------- | ------------- | -------------- |
| HN Algolia | `/api/v1/search?query=...&tags=story` | discovery ("shutting down", "is dead") and per-subject reaction threads | title, created date, points, comments, `news.ycombinator.com/item?id=` URL |
| Wikipedia | `action=query&list=categorymembers` / `prop=extracts` | defunct-website lists, intro summaries | canonical `en.wikipedia.org/wiki/...` URL |
| Wayback CDX | `cdx/search/cdx?url=<domain>&output=json&fl=timestamp` | domain birth/death dates | snapshot timestamps (attribute as "Internet Archive CDX data") |

### Traps found in practice

- HN titles contain arbitrary Unicode (en dashes, curly quotes). Fold to
  ASCII at ingestion or downstream glyph gates will fail (see
  `post-generation-pipeline.md`).
- Discovery by generic queries only surfaces subjects that had shutdown
  chatter on HN (founded 2007 or later, or retrospectively covered). Older
  deaths (e.g. 2001 Napster) need per-subject queries or seed-corpus seeding.
- Algolia relevance search outranks recency; keep `points>50` to suppress
  noise, then filter by title substring match against your subject aliases.
- CDX latency is routine, not failure: from a reachable network it answered
  5/20 lookups inside 5s and timed out on the rest. A 5s timeout throws away
  most of the index; 25s + one retry + a circuit breaker after repeated
  transport failures is the working budget, with ~2s between subjects to
  stay out of the 503 rate-limit class.
- A documented-but-dead endpoint (the screenshot service) looks identical to
  an outage from inside an unreachable network. Only a run from a reachable
  network can tell "dead" from "blocked" -- get that evidence before
  designing around either.

### Verification

All three endpoints were probed on 2026-08-29: Algolia returned HTTP 200 and
live data; Wikipedia and web.archive.org failed at the connection level
(curl timeout / Python `Errno 101`). The pipeline log at
`artifacts/writing/internet-archaeology-blog/RESULT.md` records the same
split across four pipeline runs.

Re-probed 2026-08-29 (Task blog-screenshots-and-paths): the Wayback screenshot
endpoint (`https://web.archive.org/screenshot/<url>`) and CDX both failed
per-subject for all 20 subjects (`Errno 101`). The fetcher exists as an
operator-runnable step (`run.py --fetch-screenshots`) for runners with wider
egress; until it succeeds somewhere, all plates are honestly labeled generated
memorial art.

Definitive 2026-08-29 (Task blog-screenshot-renderer, operator laptop run from
a network WITH archive egress): the screenshot endpoint is **dead** -- it
returned HTTP 404 with an HTML error page for every one of the 20 subjects
(plus one 503 challenge page). It is not an outage to wait out; do not build
on it. The same run showed CDX is alive but slow: 5 of 20 lookups answered
inside 5s, the rest timed out -- budget a 25s timeout plus one retry, and
expect to fall back to Wayback's nearest-capture form. The working pattern is
**render, don't fetch**: resolve a timestamp via CDX, then screenshot
`https://web.archive.org/web/<ts>/<original-url>` with a headless browser
(see `post-generation-pipeline.md`, truthful-images section).

## Boundaries and counter-examples

- This catalog is about sources for the dead web specifically. For general
  research, other keyless APIs may fit better.
- Reachability is an environment property, not a universal: re-probe before
  assuming the same split in another network context.
- HN evidence proves reaction, not facts. A 957-point thread is a citable
  datum about attention, never a substitute for a source on dates or numbers.

## Reuse checklist

- [ ] Probe all three endpoints before writing fetch code (timeout ~8s).
- [ ] Record per-source live/offline status in the run output.
- [ ] ASCII-fold fetched text at the ingestion boundary.
- [ ] Treat API-provided URLs as the citation; never reconstruct item IDs.

## Related

- Downstream application: `[[blog-v0-pipeline]]` / `[[internet-archaeology-blog]]`
- Companion recipe: `writing/post-generation-pipeline.md`

## Change history

| Date       | Change                                       | Triggered by (Task / Goal) |
| ---------- | -------------------------------------------- | -------------------------- |
| 2026-08-29 | Initial version from v0 blog build           | tasks/blog-v0-pipeline.md  |
| 2026-08-29 | Added Wayback screenshot-endpoint reachability + fetcher pointer | tasks/blog-screenshots-and-paths.md |
| 2026-08-29 | Screenshot endpoint marked dead with reachable-network evidence (404 html x 20); CDX slow-but-alive timings; render-don't-fetch pointer | tasks/blog-screenshot-renderer.md |
