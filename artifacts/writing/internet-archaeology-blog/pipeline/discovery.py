"""Stage 1: discovery.

Assembles candidate subjects from keyless public APIs, with graceful
degradation to the bundled offline seed corpus:

  * Hacker News Algolia search (live stories about shutdowns and dead sites)
  * Wikipedia category members ("Category:Defunct websites" family)
  * Wayback CDX (used later, in facts.py, for domain lifespan metadata)

Whatever answers becomes a live signal; whatever times out is recorded as
unreachable in the run log, and the seed corpus fills the gap. Each candidate
carries its provenance so every post can state honestly which mode produced it.
"""

from __future__ import annotations

from . import util

ALGOLIA_SEARCH = "https://hn.algolia.com/api/v1/search"
WIKI_API = "https://en.wikipedia.org/w/api.php"

# Generic shutdown-story queries used to surface dead-web chatter on HN.
DISCOVERY_QUERIES = ("shutting down", "is dead", "shut down", "closing down")

WIKI_CATEGORIES = (
    "Category:Defunct_websites",
    "Category:Defunct_web_services",
)

TIMEOUT_ALGOLIA = 10.0
TIMEOUT_WIKI = 8.0


def _algolia_stories(query: str, limit: int):
    payload, err = util.fetch_json(
        ALGOLIA_SEARCH,
        {
            "query": query,
            "tags": "story",
            "hitsPerPage": limit,
            "numericFilters": "points>50",
        },
        timeout=TIMEOUT_ALGOLIA,
    )
    if err:
        return None, err
    hits = []
    for h in payload.get("hits", []):
        hits.append(
            {
                "title": util.to_ascii((h.get("title") or "").strip()),
                "url": util.to_ascii((h.get("url") or "").strip()),
                "date": (h.get("created_at") or "")[:10],
                "points": h.get("points") or 0,
                "comments": h.get("num_comments") or 0,
                "hn_url": "https://news.ycombinator.com/item?id=" + str(h.get("objectID", "")),
            }
        )
    return hits, None


def algolia_evidence_for(name: str, aliases: list[str], limit: int = 4):
    """Fetch subject-specific HN threads usable as citable reaction evidence."""
    hits, err = _algolia_stories(f'"{name}"', limit * 3)
    if err:
        return None, err
    wanted = [a.lower() for a in aliases] + [name.lower()]
    matched = []
    for h in hits:
        title = h["title"].lower()
        if any(w in title for w in wanted):
            matched.append(h)
        if len(matched) >= limit:
            break
    return matched, None


def _wiki_category_members(category: str):
    payload, err = util.fetch_json(
        WIKI_API,
        {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category,
            "cmlimit": 200,
            "cmtype": "page",
            "format": "json",
        },
        timeout=TIMEOUT_WIKI,
    )
    if err:
        return None, err
    titles = [
        m.get("title", "")
        for m in payload.get("query", {}).get("categorymembers", [])
    ]
    return titles, None


def discover(seed_subjects: list[dict]):
    """Return (candidates, source_status).

    candidates: list of dicts {slug, name, via, evidence} where via is a list
    like ["hn-algolia", "seed-corpus"] and evidence is a list of HN threads.
    source_status: per-API status dict for the run log.
    """
    source_status = {}

    # --- HN Algolia: broad shutdown chatter -> alias matches ---------------
    algolia_ok = True
    seen_threads: dict[str, list[dict]] = {}
    for q in DISCOVERY_QUERIES:
        hits, err = _algolia_stories(q, 50)
        if err:
            algolia_ok = False
            source_status["hn_algolia"] = f"offline ({err})"
            seen_threads.clear()
            break
        for h in hits:
            slug = _match_seed(h["title"], seed_subjects)
            if slug:
                seen_threads.setdefault(slug, []).append(h)
    if algolia_ok:
        source_status["hn_algolia"] = "live"

    # --- Wikipedia: defunct-site category members --------------------------
    wiki_titles: list[str] = []
    wiki_ok = True
    for cat in WIKI_CATEGORIES:
        titles, err = _wiki_category_members(cat)
        if err:
            wiki_ok = False
            source_status["wikipedia"] = f"offline ({err})"
            break
        wiki_titles.extend(titles or [])
    if wiki_ok:
        source_status["wikipedia"] = f"live ({len(wiki_titles)} category pages)"
    else:
        wiki_titles = []

    # --- Wayback CDX reachability probe (facts.py uses it for lifespans) ---
    cdx_probe, cdx_err = util.fetch_json(
        "http://web.archive.org/cdx/search/cdx",
        {"url": "geocities.com", "output": "json", "limit": 1, "fl": "timestamp"},
        timeout=12.0,
    )
    if cdx_err:
        source_status["wayback_cdx"] = f"offline ({cdx_err})"
    else:
        source_status["wayback_cdx"] = "live"

    # --- Assemble candidates ------------------------------------------------
    candidates = []
    for subj in seed_subjects:
        slug = subj["slug"]
        via = []
        evidence = seen_threads.get(slug, [])
        if evidence:
            via.append("hn-algolia")
        if wiki_ok and _wiki_match(subj, wiki_titles):
            via.append("wikipedia-category")
        via.append("seed-corpus")
        candidates.append(
            {
                "slug": slug,
                "name": subj["name"],
                "category": subj["category"],
                "via": via,
                "evidence": evidence,
            }
        )
    # Subjects with live evidence rank first, then seed order.
    candidates.sort(key=lambda c: (0 if len(c["via"]) > 1 else 1))
    return candidates, source_status


def _match_seed(title: str, seed_subjects: list[dict]) -> str | None:
    t = title.lower()
    for subj in seed_subjects:
        for alias in [subj["name"].lower()] + subj.get("aliases", []):
            if alias in t:
                return subj["slug"]
    return None


def _wiki_match(subj: dict, wiki_titles: list[str]) -> bool:
    names = [subj["name"].lower()]
    for t in wiki_titles:
        tl = t.lower()
        if any(n == tl or n in tl for n in names):
            return True
    return False
