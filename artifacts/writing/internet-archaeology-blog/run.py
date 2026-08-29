#!/usr/bin/env python3
"""The Dead Web Gazette -- single-command pipeline entry point.

Usage:
  python3 run.py                discover -> skip covered -> draft -> rebuild
  python3 run.py --posts 3      draft up to 3 new subjects this run
  python3 run.py --rebuild-only just rebuild the static site
  python3 run.py --verify       verify the built site (links, SVG, sizes, glyphs)

Pipeline stages: discovery (keyless APIs + offline seed corpus) -> fact
research (distilled fact sheets) -> deterministic post scaffolds (drafts) ->
procedural SVG illustration -> static site assembly (museum-of-the-early-web
design; see docs/design.md; site_config.json carries base_url and titles).
A dedup ledger at data/ledger.json makes repeat runs skip already-covered
subjects. Drafts in content/drafts/ await a human editorial pass, which
publishes to content/posts/; the pipeline never overwrites either.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pipeline import discovery, facts, site, svgart, util, writing  # noqa: E402

LEDGER = ROOT / "data" / "ledger.json"
SEED = ROOT / "data" / "seed_corpus.json"
FACTS_DIR = ROOT / "data" / "facts"
DRAFTS = ROOT / "content" / "drafts"
POSTS = ROOT / "content" / "posts"
SITE = ROOT / "site"
RESULT = ROOT / "RESULT.md"
CONFIG = ROOT / "site_config.json"
CSS_SRC = ROOT / "src" / "styles.css"

SIZE_LIMIT = 100 * 1024  # publication gate: no text file over 100KB


# ---------------------------------------------------------------------------
# Run log
# ---------------------------------------------------------------------------

def append_result(lines: list[str]) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    block = [f"### Run {stamp}", ""] + [f"- {l}" for l in lines] + [""]
    if not RESULT.exists():
        RESULT.write_text(
            "# Run log\n\n"
            "One entry per pipeline invocation. Modes and verification results\n"
            "are recorded honestly, including failures and degradations.\n\n",
            encoding="utf-8",
        )
    with RESULT.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(block) + "\n")


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(max_new: int) -> dict:
    seed = util.load_json(SEED, None)
    if not seed:
        raise SystemExit("seed corpus missing: data/seed_corpus.json")
    subjects = seed["subjects"]

    candidates, status = discovery.discover(subjects)
    ledger = util.load_json(LEDGER, {})

    covered = set(ledger)
    skipped = [c["slug"] for c in candidates if c["slug"] in covered]
    fresh = [c for c in candidates if c["slug"] not in covered][:max_new]

    drafted = []
    for cand in fresh:
        subj = next(s for s in subjects if s["slug"] == cand["slug"])
        sheet = facts.build_fact_sheet(subj, cand, status)
        util.save_json(FACTS_DIR / f"{cand['slug']}.json", sheet)
        draft_path = writing.write_draft(sheet, DRAFTS)
        drafted.append(cand["slug"])
        ledger[cand["slug"]] = {
            "name": cand["name"],
            "category": cand["category"],
            "covered": date.today().isoformat(),
            "via": cand["via"],
            "data_source_mode": sheet["data_source_mode"],
            "draft": str(draft_path.relative_to(ROOT)),
            "post": str((POSTS / f"{cand['slug']}.md").relative_to(ROOT)),
            "post_exists": (POSTS / f"{cand['slug']}.md").exists(),
        }

    util.save_json(LEDGER, ledger)
    summary = site.build_site(SITE, POSTS, CSS_SRC, site.load_config(CONFIG))

    log = [
        f"mode: pipeline (max {max_new} new subject(s) this run)",
        f"sources: {status}",
        f"candidates: {len(candidates)}; skipped (in ledger): {len(skipped)} "
        f"[{', '.join(skipped) if skipped else 'none'}]",
        f"new drafts: {len(drafted)} [{', '.join(drafted) if drafted else 'none'}]",
        f"site rebuilt: {summary['posts']} published post(s) "
        f"[{', '.join(summary['slugs']) if summary['slugs'] else 'none'}]",
    ]
    if drafted:
        log.append(
            "editorial pass: drafts await a human pass in content/drafts/ "
            "(publish by writing content/posts/<slug>.md, then re-run or use --rebuild-only)"
        )
    append_result(log)
    print("\n".join(log))
    return {"drafted": drafted, "skipped": skipped, "status": status}


def rebuild_only() -> None:
    summary = site.build_site(SITE, POSTS, CSS_SRC, site.load_config(CONFIG))
    log = [f"mode: rebuild-only; site rebuilt with {summary['posts']} post(s) "
           f"[{', '.join(summary['slugs']) if summary['slugs'] else 'none'}]"]
    append_result(log)
    print("\n".join(log))


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify() -> int:
    """Check the built site for renderability and gate compliance."""
    failures: list[str] = []
    lines: list[str] = ["mode: verify"]

    def check(name: str, ok: bool, detail: str = "") -> None:
        lines.append(f"{'PASS' if ok else 'FAIL'} - {name}" + (f" ({detail})" if detail else ""))
        if not ok:
            failures.append(name)

    # Index lists every published post.
    index = SITE / "index.html"
    check("site/index.html exists", index.exists())
    post_files = sorted(POSTS.glob("*.md"))
    metas = [site.parse_post(p) for p in post_files]
    if index.exists():
        idx_txt = index.read_text(encoding="utf-8")
        for m in metas:
            linked = f'href="posts/{m["slug"]}.html"' in idx_txt
            check(f'index links post {m["slug"]}', linked)
        # D10 scale layout: one lead card (newest) + compact rows for the rest.
        lead_count = idx_txt.count('<article class="card card-lead">')
        check("index lead card count is one", lead_count == 1,
              f"{lead_count} lead card(s)")
        newest = sorted(metas, key=lambda m: (m.get("date", ""), m["slug"]), reverse=True)[0]
        lead_links_newest = (
            f'class="card-art" href="posts/{newest["slug"]}.html"' in idx_txt
        )
        check("index lead card is the newest post", lead_links_newest,
              f"expected {newest['slug']}")
        row_count = idx_txt.count('class="dispatch-row"')
        check("index dispatch rows cover the remaining posts",
              row_count == len(metas) - 1,
              f"{row_count} rows / {len(metas) - 1} non-lead posts")
        check("index order is newest first",
              _newest_first_order_ok(idx_txt, metas))
        # Category chips with counts (D10): one chip per category, count text.
        by_cat: dict[str, int] = {}
        for m in metas:
            cat = m.get("category") or "uncategorized"
            by_cat[cat] = by_cat.get(cat, 0) + 1
        chip_ok = True
        for cat, n in sorted(by_cat.items()):
            wanted = (
                f">{cat} <span class=\"chip-count\">{n}</span>"
            )
            if wanted not in idx_txt:
                chip_ok = False
        check("index category chips with counts (one per category)", chip_ok,
              f"{len(by_cat)} categories")
    lines.append(f"posts discovered: {len(metas)} [{', '.join(m['slug'] for m in metas) or 'none'}]")

    # Every post has a page, inline SVG, provenance and sources.
    for m in metas:
        page = SITE / "posts" / f'{m["slug"]}.html'
        check(f"page exists for {m['slug']}", page.exists())
        if page.exists():
            txt = page.read_text(encoding="utf-8")
            check(f"{m['slug']}: inline <svg> present", "<svg" in txt)
            check(f"{m['slug']}: hero figure present", '<figure class="hero">' in txt)
            check(f"{m['slug']}: provenance box present", "PROVENANCE" in txt)
            check(f"{m['slug']}: sources box present", "SOURCES" in txt)
            check(f"{m['slug']}: pager present", 'class="pager"' in txt)
            check(f"{m['slug']}: back-to-index present", 'href="../index.html"' in txt)
            # Regression guard: front-matter sources must actually render
            # (a v0 parser bug shipped empty SOURCES boxes unnoticed).
            missing_src = [
                s for s in m.get("sources", [])
                if "|" in s and f'href="{s.split("|", 1)[1].strip()}"' not in txt
            ]
            check(f"{m['slug']}: sources box lists all {len(m.get('sources', []))} "
                  f"front-matter sources", not missing_src, "; ".join(missing_src[:2]))
            check(f"{m['slug']}: word count >= 400 ({m['words']})", m["words"] >= 400)
        asset = SITE / "assets" / f'{m["slug"]}.svg'
        check(f"{m['slug']}: standalone svg asset exists", asset.exists())

    # About and categories pages exist, styled, and link back.
    about = SITE / "about.html"
    check("about.html exists", about.exists())
    if about.exists():
        atxt = about.read_text(encoding="utf-8")
        check("about links index", 'href="index.html"' in atxt)
        check("about links categories", 'href="categories.html"' in atxt)
    cats_page = SITE / "categories.html"
    check("categories.html exists", cats_page.exists())
    if cats_page.exists():
        ctxt = cats_page.read_text(encoding="utf-8")
        check("categories links index", 'href="index.html"' in ctxt)
        for m in metas:
            check(f"categories lists post {m['slug']}",
                  f'href="posts/{m["slug"]}.html"' in ctxt)
        cat_counts: dict[str, int] = {}
        for m in metas:
            cat = m.get("category") or "uncategorized"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        group_count = ctxt.count('class="cat-group"')
        check("categories group count equals distinct categories",
              group_count == len(cat_counts),
              f"{group_count} groups / {len(cat_counts)} categories")
        counts_ok = all(
            f"({n} dispatch{'es' if n != 1 else ''})" in ctxt
            for n in cat_counts.values()
        )
        check("categories page shows per-category counts", counts_ok)

    # Internal links resolve to files (file:// renderability proxy).
    bad_links = []
    for html in list(SITE.rglob("*.html")):
        txt = html.read_text(encoding="utf-8")
        for target in _link_targets(txt):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            dest = (html.parent / target.split("#")[0]).resolve()
            if not dest.exists():
                bad_links.append(f"{html.relative_to(SITE)} -> {target}")
    check("all internal links resolve", not bad_links, "; ".join(bad_links[:5]))

    # HTML is well-formed enough for a real parser (balanced non-void tags).
    unbalanced = []
    for html in SITE.rglob("*.html"):
        msg = _html_balance_check(html.read_text(encoding="utf-8"))
        if msg:
            unbalanced.append(f"{html.relative_to(SITE)}: {msg}")
    check("html parses with balanced tags", not unbalanced, "; ".join(unbalanced[:5]))

    # Stylesheet: one hand-written css, linked and resolving from every page.
    css = SITE / "styles.css"
    check("site/styles.css exists", css.exists())
    if css.exists():
        check("site/styles.css is a byte-identical copy of src/styles.css",
              CSS_SRC.exists() and css.read_bytes() == CSS_SRC.read_bytes())
    css_link_problems = []
    for html in SITE.rglob("*.html"):
        txt = html.read_text(encoding="utf-8")
        links = re.findall(r'<link rel="stylesheet" href="([^"]+)"', txt)
        if not links:
            css_link_problems.append(f"{html.relative_to(SITE)}: no stylesheet link")
            continue
        for target in links:
            if not (html.parent / target).resolve().exists():
                css_link_problems.append(f"{html.relative_to(SITE)} -> {target}")
    check("styles.css resolves from every page", not css_link_problems,
          "; ".join(css_link_problems[:5]))
    if css.exists():
        css_txt = css.read_text(encoding="utf-8")
        bal = css_txt.count("{") - css_txt.count("}")
        check("styles.css braces balanced (truncation lint)", bal == 0,
              f"open-minus-close: {bal}")

    # No JavaScript anywhere (file:// safety, no-JS promise).
    scripted = [str(h.relative_to(SITE)) for h in SITE.rglob("*.html")
                if "<script" in h.read_text(encoding="utf-8")]
    check("no scripts in built pages", not scripted, "; ".join(scripted[:5]))

    # RSS feed: parses as XML and lists every published post.
    rss_ok, rss_detail = _rss_check(metas)
    check("rss.xml parses and lists every published post", rss_ok, rss_detail)

    # Config: documented base_url present and well-formed.
    cfg = site.load_config(CONFIG)
    base = cfg.get("base_url", "")
    check("base_url configured (absolute http url, no trailing slash)",
          base.startswith(("http://", "https://")) and not base.endswith("/"), base)

    # Determinism, whole-site edition: clean-state rebuild is byte-identical.
    ok_clean, detail = _clean_state_rebuild_identical()
    check("clean-state rebuild byte-identical to tracked site", ok_clean, detail)

    # Determinism: regenerate an SVG and compare.
    if metas:
        probe = metas[0]["slug"]
        regen = site.illustration_for(metas[0])
        on_disk = (SITE / "assets" / f"{probe}.svg").read_text(encoding="utf-8").strip()
        check(f"svg deterministic for {probe}", regen.strip() == on_disk)

    # Publication gates across every text file in the artifact tree.
    violations = []
    oversize = []
    for p in ROOT.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            if p.stat().st_size > SIZE_LIMIT:
                oversize.append(str(p.relative_to(ROOT)))
            try:
                content = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, ValueError):
                continue  # binaries are not our concern here
            hits = util.glyph_scan(content)
            if hits:
                violations.append(f"{p.relative_to(ROOT)}: {', '.join(hits[:3])}")
    check("glyph gate (ASCII-only, no emoji, no check marks)", not violations,
          "; ".join(violations[:5]))
    check(f"size gate (no text file over {SIZE_LIMIT // 1024}KB)", not oversize,
          "; ".join(oversize[:5]))

    # Ledger sanity: every published post is covered.
    ledger = util.load_json(LEDGER, {})
    for m in metas:
        check(f"ledger covers {m['slug']}", m["slug"] in ledger)

    ok = not failures
    lines.append(f"verify result: {'ALL CHECKS PASS' if ok else 'FAILURES: ' + ', '.join(failures)}")
    append_result(lines)
    print("\n".join(lines))
    return 0 if ok else 1


def _link_targets(html_text: str) -> list[str]:
    out = []
    for attr in ("href", "src"):
        out += re.findall(f'{attr}="([^"]+)"', html_text)
    return out


def _newest_first_order_ok(idx_txt: str, metas: list[dict]) -> bool:
    """The index must list cards newest first (same key as the builder)."""
    expected = [m["slug"] for m in
                sorted(metas, key=lambda m: (m.get("date", ""), m["slug"]), reverse=True)]
    found, seen = [], set()
    for slug in re.findall(r'href="posts/([a-z0-9-]+)\.html"', idx_txt):
        if slug not in seen:
            seen.add(slug)
            found.append(slug)
    return found == expected


def _rss_check(metas: list[dict]) -> tuple[bool, str]:
    """rss.xml must parse and carry one item per published post."""
    import xml.etree.ElementTree as ET

    rss = SITE / "rss.xml"
    if not rss.exists():
        return False, "site/rss.xml missing"
    try:
        root = ET.parse(rss).getroot()
    except ET.ParseError as exc:
        return False, f"parse error: {exc}"
    items = root.findall("./channel/item")
    refs = [(i.findtext("guid") or "") for i in items] + \
           [(i.findtext("link") or "") for i in items]
    got = set()
    for ref in refs:
        m = re.search(r"/posts/([a-z0-9-]+)\.html$", ref.strip())
        if m:
            got.add(m.group(1))
    want = {m["slug"] for m in metas}
    if len(items) != len(metas):
        return False, f"{len(items)} items for {len(metas)} posts"
    if want != got:
        return False, (f"missing: {sorted(want - got)[:3]}; "
                       f"extra: {sorted(got - want)[:3]}")
    return True, f"{len(items)} items"


def _clean_state_rebuild_identical() -> tuple[bool, str]:
    """Build into an empty scratch dir; compare file set and bytes to site/."""
    import tempfile

    with tempfile.TemporaryDirectory(prefix="gazette-verify-") as tmp:
        scratch = Path(tmp) / "site"
        site.build_site(scratch, POSTS, CSS_SRC, site.load_config(CONFIG))
        tracked = sorted(p.relative_to(SITE) for p in SITE.rglob("*") if p.is_file())
        built = sorted(p.relative_to(scratch) for p in scratch.rglob("*") if p.is_file())
        if tracked != built:
            only_site = sorted(set(tracked) - set(built))[:3]
            only_build = sorted(set(built) - set(tracked))[:3]
            return False, (f"file sets differ; only in site/: {only_site}; "
                           f"only in clean build: {only_build}")
        for rel in tracked:
            if (SITE / rel).read_bytes() != (scratch / rel).read_bytes():
                return False, f"{rel} differs from clean-state rebuild"
    return True, "byte-identical"


_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
         "link", "meta", "param", "source", "track", "wbr"}


def _html_balance_check(text: str) -> str:
    """Parse with html.parser; return "" when balanced, else the problem."""
    from html.parser import HTMLParser

    class Checker(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack: list[str] = []
            self.problem = ""

        def handle_starttag(self, tag, attrs):
            if tag not in _VOID:
                self.stack.append(tag)

        def handle_endtag(self, tag):
            if tag in _VOID:
                return
            if not self.stack or self.stack[-1] != tag:
                self.problem = self.problem or (
                    f"unexpected </{tag}> (stack top: "
                    f"{self.stack[-1] if self.stack else 'empty'})"
                )
            else:
                self.stack.pop()

    c = Checker()
    try:
        c.feed(text)
        c.close()
    except Exception as exc:  # parser raised outright
        return f"parse error: {exc}"
    if c.problem:
        return c.problem
    if c.stack:
        return f"unclosed tags: {', '.join(c.stack[:4])}"
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="The Dead Web Gazette pipeline")
    ap.add_argument("--posts", type=int, default=1,
                    help="max new subjects to draft this run (default 1)")
    ap.add_argument("--rebuild-only", action="store_true",
                    help="skip discovery; just rebuild the site")
    ap.add_argument("--verify", action="store_true",
                    help="verify the built site and gate compliance")
    args = ap.parse_args()

    if args.verify:
        return verify()
    if args.rebuild_only:
        rebuild_only()
        return 0
    run_pipeline(args.posts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
