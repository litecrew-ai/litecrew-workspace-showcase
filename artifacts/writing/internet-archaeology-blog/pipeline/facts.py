"""Stage 2: fact research.

Distills a per-subject fact sheet. Sources, in order of preference:

  * Wikipedia intro extract (when Wikipedia is reachable)
  * Wayback CDX first/last snapshot timestamps (when the CDX is reachable)
  * HN Algolia discussion threads (reaction evidence, always attributed)
  * The bundled seed corpus (always available; confidence-tagged facts)

The sheet is written to data/facts/<slug>.json. Sheets stay small by design:
distilled facts only, never raw payloads.
"""

from __future__ import annotations

from . import util
from .discovery import WIKI_API, algolia_evidence_for

CDX_URL = "http://web.archive.org/cdx/search/cdx"


def _wikipedia_extract(name: str):
    payload, err = util.fetch_json(
        WIKI_API,
        {
            "action": "query",
            "prop": "extracts",
            "exintro": 1,
            "explaintext": 1,
            "redirects": 1,
            "titles": name,
            "format": "json",
        },
        timeout=8.0,
    )
    if err:
        return None, err
    pages = payload.get("query", {}).get("pages", {})
    for page in pages.values():
        extract = (page.get("extract") or "").strip()
        if extract:
            return {
                "title": util.to_ascii(page.get("title", name)),
                "extract_first_600": util.to_ascii(extract[:600]),
                "canonical_url": "https://en.wikipedia.org/wiki/"
                + util.to_ascii(str(page.get("title", name))).replace(" ", "_"),
            }, None
    return None, "no extract returned"


def cdx_lifespan(domain: str):
    """First and last archived snapshots of a domain (live CDX only).

    Kept simple and honest: two limit-1 queries with reversed sort order.
    Returns None with a reason string when the CDX is unreachable, so the
    sheet records the gap instead of guessing.
    """
    rows, err = util.fetch_json(
        CDX_URL,
        {
            "url": domain,
            "matchType": "prefix",
            "output": "json",
            "fl": "timestamp",
            "collapse": "timestamp:4",
            "limit": 500,
        },
        timeout=15.0,
    )
    if err:
        return None, err
    if not isinstance(rows, list) or len(rows) < 2:
        return None, "no snapshots returned"
    stamps = [r[0] for r in rows[1:] if r]
    if not stamps:
        return None, "no snapshots returned"
    return {
        "first_snapshot": stamps[0][:8],
        "last_snapshot": stamps[-1][:8],
        "sampled_years": sorted({s[:4] for s in stamps}),
    }, None


def build_fact_sheet(subject: dict, candidate: dict, source_status: dict):
    """Merge seed facts with whatever live sources answered."""
    mode_parts = ["facts: seed-corpus"]

    sheet = {
        "slug": subject["slug"],
        "name": subject["name"],
        "category": subject["category"],
        "domain": subject.get("domain", ""),
        "facts": subject["facts"],
        "hn_threads": candidate.get("evidence", []),
        "wikipedia": None,
        "cdx_lifespan": None,
        "source_status": source_status,
    }

    # Wikipedia extract, when reachable.
    if source_status.get("wikipedia", "").startswith("live"):
        extract, err = _wikipedia_extract(subject["name"])
        if extract:
            sheet["wikipedia"] = extract
            mode_parts.append("wikipedia-extract (live)")
    else:
        mode_parts.append("wikipedia-unreachable")

    # Wayback CDX lifespan, when reachable.
    if source_status.get("wayback_cdx", "").startswith("live") and sheet["domain"]:
        lifespan, err = cdx_lifespan(sheet["domain"])
        if lifespan:
            sheet["cdx_lifespan"] = lifespan
            mode_parts.append("wayback-cdx (live)")
    else:
        mode_parts.append("wayback-cdx-unreachable")

    # HN Algolia evidence, when the candidate was matched live.
    if source_status.get("hn_algolia", "").startswith("live"):
        if candidate.get("via") and "hn-algolia" in candidate["via"]:
            mode_parts.append("hn-algolia (live)")
        else:
            extra, err = algolia_evidence_for(subject["name"], subject.get("aliases", []))
            if extra:
                sheet["hn_threads"] = (sheet["hn_threads"] or []) + extra
                mode_parts.append("hn-algolia (live, subject query)")
    else:
        mode_parts.append("hn-algolia-unreachable")

    sheet["data_source_mode"] = "; ".join(mode_parts)
    return sheet
