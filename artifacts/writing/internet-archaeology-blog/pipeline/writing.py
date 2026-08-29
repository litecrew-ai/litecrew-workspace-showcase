"""Stage 3: post scaffolding (deterministic).

Renders a scaffolded draft from a fact sheet. No language model is involved:
every sentence is assembled from a fact (which carries its source) plus fixed
framing, so the same fact sheet always yields the same scaffold.

Editorial split (v0):
  * the pipeline writes content/drafts/<slug>.md
  * a human editorial pass turns it into content/posts/<slug>.md (published)
  * the site builder only publishes what is in content/posts/

The pipeline never overwrites either file. When an LLM API becomes available,
the intended hook is a single function here: take the fact sheet and produce
narrative prose; everything else (front matter, sources, dedup) stays.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from . import util

GENERATOR = "deadweb-pipeline 0.1 (deterministic scaffold)"

HEDGES = {
    "medium": [
        "Reported at the time as follows, though figures vary: {fact}",
        "By most accounts, {fact_lower}",
        "Contemporary reports say {fact_lower}",
    ],
    "high": ["{fact}"],
}


def _fact_sources(sheet: dict) -> list[dict]:
    """Deduplicate sources from facts and HN threads into an ordered list."""
    out: list[dict] = []
    seen: set[str] = set()

    def add(name: str, url: str):
        if url and url not in seen:
            seen.add(url)
            out.append({"name": name, "url": url})

    for f in sheet.get("facts", []):
        add(f.get("source", "source"), f.get("url", ""))
    if sheet.get("wikipedia"):
        add("Wikipedia (intro extract)", sheet["wikipedia"]["canonical_url"])
    for t in sheet.get("hn_threads", []):
        add(
            f'Hacker News thread: "{t["title"]}" ({t["date"]})',
            t["hn_url"],
        )
    return out


def render_front_matter(sheet: dict, sources: list[dict], status: str, editor: str) -> str:
    lines = [
        "---",
        f'title: "{sheet["name"]}"',
        f"slug: {sheet['slug']}",
        f"date: {date.today().isoformat()}",
        f"category: {sheet['category']}",
        f"status: {status}",
        f"generator: {GENERATOR}",
        f"editor: {editor}",
        f'data_source_mode: "{sheet["data_source_mode"]}"',
        f"generated: {date.today().isoformat()}",
        # Illustration mode (D11): drafts start as generated art; the
        # screenshot stage flips this to "screenshot" with provenance fields
        # when it actually fetches bytes from the Internet Archive.
        "illustration: generated",
        "sources:",
    ]
    for s in sources:
        lines.append(f"  - {s['name']} | {s['url']}")
    lines.append("---")
    return "\n".join(lines)


def render_scaffold_body(sheet: dict, sources: list[dict]) -> str:
    """Deterministic scaffold: framing text plus sourced fact sentences."""
    facts = sheet.get("facts", [])
    high = [f for f in facts if f.get("confidence") == "high"]
    medium = [f for f in facts if f.get("confidence") != "high"]

    def cite(f: dict) -> str:
        for i, s in enumerate(sources, 1):
            if s["url"] == f.get("url"):
                return f"[S{i}]"
        return ""

    parts: list[str] = []
    parts.append(
        f"<!-- MACHINE SCAFFOLD: deterministic draft awaiting the editorial pass. "
        f"Every sentence below is fact-framing plus a citation marker; the "
        f"editorial pass replaces this body but must keep every claim sourced "
        f"or hedged. -->"
    )
    parts.append(f"# {sheet['name']}\n")
    parts.append("## Lede\n")
    parts.append(
        f"[Editorial: open with the terse evocative register. Anchor fact: "
        f"{_first_lede_fact(high, medium)}]\n"
    )
    parts.append("## What it was\n")
    for f in high[:3]:
        parts.append(f"- {f['text']} {cite(f)}\n")
    parts.append("## Reported, though numbers vary\n")
    if medium:
        for f in medium[:3]:
            parts.append(f"- Reported: {f['text']} {cite(f)}\n")
    else:
        parts.append("- (No medium-confidence facts kept for this subject.)\n")
    parts.append("## The end\n")
    ending = [f for f in high if any(w in f["text"].lower() for w in
              ("shut", "clos", "retir", "bankrupt", "liquid", "end", "wound"))]
    for f in ending[:3]:
        parts.append(f"- {f['text']} {cite(f)}\n")
    parts.append("## Afterlife\n")
    leftover = [f for f in high if f not in ending][:3]
    for f in leftover:
        parts.append(f"- {f['text']} {cite(f)}\n")
    if sheet.get("cdx_lifespan"):
        ls = sheet["cdx_lifespan"]
        parts.append(
            f"\nWayback CDX snapshot years for {sheet['domain']}: "
            f"{ls['first_snapshot'][:4]} to {ls['last_snapshot'][:4]} "
            f"(sampled: {', '.join(ls['sampled_years'])}).\n"
        )
    if sheet.get("hn_threads"):
        parts.append("## Reaction on Hacker News\n")
        for t in sheet["hn_threads"][:4]:
            parts.append(
                f'- "{t["title"]}" ({t["date"]}, {t["points"]} points, '
                f'{t["comments"]} comments): {t["hn_url"]}\n'
            )
    parts.append("## Sources\n")
    for i, s in enumerate(sources, 1):
        parts.append(f"- S{i}: {s['name']} -- {s['url']}\n")
    return "\n".join(parts)


def _first_lede_fact(high: list[dict], medium: list[dict]) -> str:
    pool = high or medium
    if not pool:
        return "none recorded"
    return pool[0]["text"]


def write_draft(sheet: dict, drafts_dir: Path) -> Path:
    """Write content/drafts/<slug>.md unless it already exists. Never clobbers."""
    drafts_dir.mkdir(parents=True, exist_ok=True)
    path = drafts_dir / f"{sheet['slug']}.md"
    if path.exists():
        return path
    sources = _fact_sources(sheet)
    content = (
        render_front_matter(sheet, sources, "draft", "(awaiting editorial pass)")
        + "\n\n"
        + render_scaffold_body(sheet, sources)
        + "\n"
    )
    violations = util.glyph_scan(content)
    if violations:
        raise ValueError(f"front matter/body glyph violations: {violations}")
    path.write_text(content, encoding="utf-8")
    return path
