#!/usr/bin/env python3
"""The Dead Web Gazette -- single-command pipeline entry point.

Usage:
  python3 run.py                discover -> skip covered -> draft -> rebuild
  python3 run.py --posts 3      draft up to 3 new subjects this run
  python3 run.py --rebuild-only just rebuild the static site
  python3 run.py --probe-render
                                offline first-run check: render a data: page
                                through the exact production browser
                                invocation and validate the png; run this
                                FIRST on any new machine (a fail-fast probe
                                also opens --fetch-screenshots)
  python3 run.py --fetch-screenshots
                                render real archived pages per subject with
                                a headless browser (CHROME_BIN or a PATH
                                probe; needs egress to web.archive.org;
                                every attempt is logged; degrades honestly)
  python3 run.py --verify       verify the built site (links, SVG, sizes,
                                glyphs, mounted-subpath serving)

Pipeline stages: discovery (keyless APIs + offline seed corpus) -> fact
research (distilled fact sheets) -> deterministic post scaffolds (drafts) ->
procedural SVG illustration -> static site assembly (museum-of-the-early-web
design; see docs/design.md; site_config.json carries base_url, titles, and
path_prefix). A dedup ledger at data/ledger.json makes repeat runs skip
already-covered subjects. Drafts in content/drafts/ await a human editorial
pass, which publishes to content/posts/; the pipeline never overwrites either.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import re
import socketserver
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pipeline import discovery, facts, screenshots, site, svgart, util, writing  # noqa: E402

LEDGER = ROOT / "data" / "ledger.json"
SEED = ROOT / "data" / "seed_corpus.json"
FACTS_DIR = ROOT / "data" / "facts"
DRAFTS = ROOT / "content" / "drafts"
POSTS = ROOT / "content" / "posts"
SITE = ROOT / "site"
RESULT = ROOT / "RESULT.md"
CONFIG = ROOT / "site_config.json"
CSS_SRC = ROOT / "src" / "styles.css"
SCREENSHOTS = ROOT / "assets" / "screenshots"

SIZE_LIMIT = 100 * 1024  # publication gate: no text file over 100KB
# When the run log is this close to the gate, per-subject fetch lines stay on
# stdout and RESULT.md gets a condensed outcome summary instead.
RESULT_CONDENSE_THRESHOLD = 88 * 1024
# Rotation policy (full text in RESULT.md and docs/result-log/archive-1.md):
# when RESULT.md exceeds this threshold, move everything except the header,
# the current verification-methods section, and the last ~10 run entries into
# the next docs/result-log/archive-<N>.md. Nothing is deleted; history moves.
RESULT_ROTATE_THRESHOLD = 60 * 1024
RESULT_LOG_DIR = ROOT / "docs" / "result-log"


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
    if RESULT.stat().st_size > RESULT_ROTATE_THRESHOLD:
        print(f"note: RESULT.md is past the {RESULT_ROTATE_THRESHOLD // 1024}KB "
              "rotation threshold -- rotate per the policy in "
              "docs/result-log/ (move all but the newest verification-methods "
              "section and the last ~10 entries into the next archive file)")


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
    summary = site.build_site(SITE, POSTS, CSS_SRC, site.load_config(CONFIG),
                              screenshots_dir=SCREENSHOTS)

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
    summary = site.build_site(SITE, POSTS, CSS_SRC, site.load_config(CONFIG),
                              screenshots_dir=SCREENSHOTS)
    log = [f"mode: rebuild-only; site rebuilt with {summary['posts']} post(s) "
           f"[{', '.join(summary['slugs']) if summary['slugs'] else 'none'}]"]
    append_result(log)
    print("\n".join(log))


# ---------------------------------------------------------------------------
# Screenshot fetch (operator-runnable; needs egress to web.archive.org)
# ---------------------------------------------------------------------------

def _outcome_class(result: dict) -> str:
    """A short, human-readable failure class for the condensed run record.

    CDX notes carry the per-subject URL ("cdx http://x: cdx: timeout ..."),
    which would make every subject its own group; the URL is dropped so the
    log groups by what actually happened.
    """
    if result.get("stored"):
        return "stored"
    first = next((n for n in result["note"]
                  if n.startswith(("cdx ", "archived page", "skipped",
                                   "render:", "rejected"))), "other")
    if first.startswith("cdx ") and first.count(":") >= 2:
        return first.split(":", 2)[-1].strip()[:70]
    return first.split(":")[0][:70]


def condense_outcomes(results: list[dict]) -> list[str]:
    """Group per-subject outcomes into class -> slug-list log lines."""
    groups: dict[str, list[str]] = {}
    for r in results:
        groups.setdefault(_outcome_class(r), []).append(r["slug"])
    return [f"  {key}: {len(groups[key])} subject(s) "
            f"[{', '.join(groups[key])[:400]}]" for key in sorted(groups)]


def probe_render_mode() -> int:
    """CLI mode for the offline render self-probe (screenshots.probe_render).

    The FIRST thing to run on any new machine: it exercises the exact
    browser_cmd() invocation -- fresh temp profile included -- against a
    data: URL (no network), then validates the written png (magic, window
    dimensions, non-blank floor). A browser that cannot run this recipe
    headlessly fails here in seconds with an actionable message, instead of
    during a 25-minute subject batch. --fetch-screenshots runs the same probe
    automatically and stops before the first subject when it fails.
    """
    browser, browser_note = screenshots.find_browser()
    print(browser_note)
    if not browser:
        append_result([f"mode: probe-render -- FAIL (no browser binary)"])
        return 1
    r = screenshots.probe_render(browser)
    print("probe invocation (temp paths differ per run; the probe page is a"
          " data: URL):")
    shown = [a if not a.startswith("data:")
             else a[:24] + f"...({len(a)}-char data: page)" for a in r["flags"]]
    print("  " + " ".join(shown))
    verdict = "PASS" if r["ok"] else "FAIL"
    print(f"probe result: {verdict} -- {r['reason']}")
    print(f"elapsed: {r['elapsed_s']:.1f}s; bytes written: {r['bytes']}")
    if r["hint"]:
        print(r["hint"])
    append_result([
        f"mode: probe-render -- {verdict}",
        f"browser: {browser_note}",
        f"result: {r['reason']}; elapsed {r['elapsed_s']:.1f}s",
    ] + ([] if r["ok"] else [f"hint: {r['hint']}"]))
    return 0 if r["ok"] else 1


def fetch_screenshots() -> int:
    """Render a real archived page per published subject, headlessly.

    Strategy is render-don't-fetch: the former web.archive.org/screenshot
    endpoint is dead (operator run 2026-08-29: HTTP 404 + an HTML error page
    for all 20 subjects). A pre-flight render probe (the --probe-render
    check, offline data: page through the exact invocation) runs first and
    the batch STOPS before the first subject when it fails -- no more
    25-minute doomed runs. Each subject resolves a snapshot via hardened CDX
    (25s timeout, one retry, 200-preference, circuit breaker; a CDX miss of
    any kind falls back to Wayback's era-anchored nearest-capture
    /web/<YYYY>/<url> form using the fact sheet's peak/death/launch year --
    /web/2/, which resolves to the MOST RECENT capture, only when the sheet
    has no year), pre-checks the playback URL (HTTP 503 backed off ~15s and
    retried once), then renders it with a browser subprocess located through
    $CHROME_BIN or a PATH probe. The capture bound is Chrome's own --timeout
    (the laptop run of 2026-08-29 lost all 20 renders to a
    --virtual-time-budget-only invocation that never reached load-complete);
    our 75s wall budget is only the outer guard, every render runs in its own
    fresh temp profile, and chrome's filtered stderr (head+tail, chrome/
    updater noise dropped) rides along in every failure line. Every attempt
    lands in RESULT.md; failures degrade the subject to the labeled generated
    plate. When no browser binary exists the run degrades once, with the
    actionable message, and touches no network at all. Post bodies are
    hash-checked before/after: only front-matter fields may change.
    """
    subjects = screenshots.load_subjects(SEED)
    posts = sorted(POSTS.glob("*.md"))
    if not posts:
        print("no published posts to fetch for")
        return 0
    fetch_date = date.today().isoformat()
    before = {p.name: screenshots.body_sha256(p) for p in posts}

    browser, browser_note = screenshots.find_browser()
    print(browser_note)
    log = [
        "mode: fetch-screenshots (render strategy: pre-flight probe, then "
        "resolve via CDX (misses fall back to the era-anchored /web/<YYYY>/ "
        "form from the fact sheet's peak/death/launch year; /web/2/ only "
        "when the sheet has no year), pre-check the playback url (503 -> "
        "backoff + one retry), then screenshot it with a headless browser in "
        "a fresh temp profile; chrome's own --timeout is the capture bound, "
        "the 75s wall budget is only the outer guard)",
        browser_note,
    ]

    if browser:
        # Fail fast: prove the browser can run this recipe at all before the
        # first 25s CDX lookup or 30s render is spent (the operator's third
        # laptop run hung on all 20 subjects with nothing but updater noise
        # on stderr; the probe turns that into a 10-second diagnosis).
        probe = screenshots.probe_render(browser)
        verdict = "PASS" if probe["ok"] else "FAIL"
        print(f"pre-flight render probe: {verdict} -- {probe['reason']} "
              f"({probe['elapsed_s']:.1f}s, {probe['bytes']} bytes)")
        if not probe["ok"]:
            log.append(f"pre-flight render probe: FAIL -- {probe['reason']}")
            log.append("subjects NOT attempted (fail fast): fix the browser "
                       "environment first; python3 run.py --probe-render "
                       "re-runs the probe alone")
            log.append(f"hint: {probe['hint']}")
            append_result(log)
            print("\n".join(log))
            return 1
        log.append(f"pre-flight render probe: PASS -- {probe['reason']}")

    cdx_state: dict = {"fails": 0, "tripped": False}
    results = []
    did_work = False
    for i, p in enumerate(posts):
        if i and did_work:
            time.sleep(screenshots.INTER_SUBJECT_DELAY)
        subj = subjects.get(p.stem, {"slug": p.stem, "name": p.stem})
        # Era anchor from the subject's own fact sheet (peak/death/launch
        # year); None -> the /web/2/ fallback form.
        sheet = util.load_json(FACTS_DIR / f"{p.stem}.json", {})
        era = screenshots.era_anchor_year(sheet)
        r, worked = screenshots.attempt_subject(
            p, subj, SCREENSHOTS, fetch_date, browser=browser,
            cdx_state=cdx_state, era_year=era)
        did_work = did_work or worked
        results.append(r)
        print(screenshots.result_line(r))

    bodies_ok = all(screenshots.body_sha256(p) == before[p.name] for p in posts)
    stored = [r for r in results if r.get("stored")]
    log.append(
        f"subjects attempted: {len(results)}; screenshots stored: {len(stored)}; "
        f"degraded to generated art: {len(results) - len(stored)}"
    )
    log.append(
        f"post bodies byte-identical after front-matter updates (sha256): "
        f"{'yes' if bodies_ok else 'MISMATCH - INVESTIGATE'}"
    )
    if not browser:
        # No browser: one actionable message above; per-subject detail stays
        # on stdout so the run record degrades once, not twenty times.
        log.append("skipped (no browser binary): " + ", ".join(r["slug"] for r in results))
    elif RESULT.exists() and RESULT.stat().st_size > RESULT_CONDENSE_THRESHOLD:
        log.append(
            f"RESULT.md near the size gate ({RESULT.stat().st_size / 1024:.1f}KB of "
            f"{SIZE_LIMIT // 1024}KB); per-subject lines kept on stdout only; "
            "condensed outcomes:"
        )
        log.extend(condense_outcomes(results))
    else:
        for r in results:
            log.append(screenshots.result_line(r))
    if stored:
        log.append("binary size report:")
        for r in stored:
            log.append(f'  assets/screenshots/{r["stored"]} -- {r["bytes"]} bytes')
    else:
        log.append("no binaries stored this run (nothing to size-report)")
    summary = site.build_site(SITE, POSTS, CSS_SRC, site.load_config(CONFIG),
                              screenshots_dir=SCREENSHOTS)
    log.append(f"site rebuilt: {summary['posts']} published post(s)")
    append_result(log)
    print("\n".join(log))
    return 0 if bodies_ok else 1


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify() -> int:
    """Check the built site for renderability and gate compliance."""
    failures: list[str] = []
    lines: list[str] = ["mode: verify"]
    # `lines` is the full stdout listing; `record` is the condensed version
    # appended to RESULT.md. The run log is itself under the 100KB size
    # gate, so it carries section outcomes, method notes, and every
    # failure -- not 300+ per-check PASS lines.
    record: list[str] = []

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

    # Every post has a page, art, provenance and sources.
    for m in metas:
        page = SITE / "posts" / f'{m["slug"]}.html'
        check(f"page exists for {m['slug']}", page.exists())
        fm_mode = str(m.get("illustration", "") or "")
        check(f"{m['slug']}: illustration mode declared (screenshot|generated)",
              fm_mode in ("screenshot", "generated"), fm_mode or "missing")
        shot_slug = site.screenshot_file_for(SCREENSHOTS, m["slug"])
        if page.exists():
            txt = page.read_text(encoding="utf-8")
            if '<figure class="hero">' in txt and "</figure>" in txt:
                hero = txt.split('<figure class="hero">', 1)[1].split("</figure>", 1)[0]
            else:
                hero = ""
            gen_label = "generated memorial art" in txt
            shot_label = "screenshot: Wayback Machine" in txt
            if fm_mode == "screenshot" and shot_slug:
                check(f"{m['slug']}: screenshot plate renders an <img>",
                      '<div class="hero-mount"><img' in txt)
                check(f"{m['slug']}: screenshot plate label visible", shot_label)
                check(f"{m['slug']}: generated label absent on screenshot plate",
                      not gen_label)
                check(f"{m['slug']}: screenshot provenance fields in front matter",
                      bool(m.get("screenshot_url")) and bool(m.get("screenshot_fetched")))
                if m.get("screenshot_timestamp"):
                    check(f"{m['slug']}: snapshot timestamp on the plate",
                          str(m["screenshot_timestamp"]) in txt)
                if m.get("screenshot_capture_mode"):
                    # A nearest-capture render with no recoverable timestamp
                    # must be labeled as such, never dated by guesswork.
                    check(f"{m['slug']}: nearest-capture label on the plate",
                          str(m["screenshot_capture_mode"]) in txt)
                if m.get("screenshot_archived_url"):
                    check(f"{m['slug']}: archived page url is a playback form",
                          str(m["screenshot_archived_url"]).startswith(
                              "https://web.archive.org/web/"),
                          str(m["screenshot_archived_url"])[:60])
                    check(f"{m['slug']}: archived page url on the plate",
                          str(m["screenshot_archived_url"]) in txt)
                check(f"{m['slug']}: fetch date on the plate",
                      str(m.get("screenshot_fetched", "")) in txt)
                check(f"{m['slug']}: screenshot binary copied into site/assets",
                      (SITE / "assets" / shot_slug).is_file())
            else:
                # Generated plate (the default, and the honest fallback when
                # a screenshot post's binary is missing).
                check(f"{m['slug']}: inline <svg> present", "<svg" in hero)
                check(f"{m['slug']}: generated plate label visible", gen_label)
                check(f"{m['slug']}: no screenshot label on generated plate",
                      not shot_label)
                check(f"{m['slug']}: no screenshot <img> on generated plate",
                      "<img" not in hero)
            check(f"{m['slug']}: hero figure present", '<figure class="hero">' in txt)
            check(f"{m['slug']}: provenance box present", "PROVENANCE" in txt)
            check(f"{m['slug']}: provenance box carries an Illustration row",
                  "Illustration:" in txt)
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

    # Orphan-binary guard: a stored screenshot binary with no screenshot-mode
    # post would be an unlabeled image in the tree.
    shot_mode_slugs = {m["slug"] for m in metas
                       if str(m.get("illustration", "")) == "screenshot"}
    orphans = []
    if SCREENSHOTS.is_dir():
        for f in sorted(SCREENSHOTS.iterdir()):
            if f.is_file() and f.suffix.lower() in (".png", ".jpg"):
                if f.stem not in shot_mode_slugs:
                    orphans.append(f.name)
    check("no orphan screenshot binaries (stored binary must match a "
          "screenshot-mode post)", not orphans, "; ".join(orphans[:3]))

    # About and categories pages exist, styled, and link back.
    about = SITE / "about.html"
    check("about.html exists", about.exists())
    if about.exists():
        atxt = about.read_text(encoding="utf-8")
        check("about links index", 'href="index.html"' in atxt)
        check("about links categories", 'href="categories.html"' in atxt)
        check("about states the illustration policy (screenshots vs generated)",
              "screenshots versus generated plates" in atxt
              and "Screenshot: Wayback Machine" in atxt)
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

    # The dead screenshot endpoint must never resurface as a live dependency.
    dead_refs = [str(h.relative_to(SITE)) for h in SITE.rglob("*.html")
                 if "web.archive.org/screenshot" in h.read_text(encoding="utf-8")]
    check("dead /screenshot/ endpoint not referenced by built pages",
          not dead_refs, "; ".join(dead_refs[:3]))

    # RSS feed: parses as XML and lists every published post.
    rss_ok, rss_detail = _rss_check(metas)
    check("rss.xml parses and lists every published post", rss_ok, rss_detail)

    # Config: documented base_url present and well-formed.
    cfg = site.load_config(CONFIG)
    base = cfg.get("base_url", "")
    check("base_url configured (absolute http url, no trailing slash)",
          base.startswith(("http://", "https://")) and not base.endswith("/"), base)
    pp = str(cfg.get("path_prefix", ""))
    check("path_prefix well-formed (empty, or /sub/path/ with slashes both ends)",
          pp == "" or (pp.startswith("/") and pp.endswith("/") and len(pp) >= 2
                       and " " not in pp), repr(pp))

    # Determinism, whole-site edition: clean-state rebuild is byte-identical.
    ok_clean, detail = _clean_state_rebuild_identical()
    check("clean-state rebuild byte-identical to tracked site", ok_clean, detail)

    # Mounted-subpath serving test (reproduces the "localhost/site/" report):
    # browse the tracked default-mode build over real HTTP at its workspace
    # subpath, then a scratch prefix-mode build at /site/ -- in both modes
    # every internal reference a browser would fetch must answer HTTP 200.
    mount_fail, mount_notes = _mounted_subpath_test(cfg)
    for note in mount_notes:
        lines.append(note)
        record.append(note)
    a_fails = [f for f in mount_fail if f.startswith("[A]")]
    b_fails = [f for f in mount_fail if f.startswith("[B]")]
    check("mounted-subpath http test, relative default mode "
          "(stylesheet + all internal refs 200 under the workspace subpath)",
          not a_fails and any("mode A ok" in n for n in mount_notes),
          "; ".join(a_fails[:3]))
    check("mounted-subpath http test, path_prefix=/site/ mode "
          "(prefix-absolute refs, all 200 under /site/)",
          not b_fails and any("mode B ok" in n for n in mount_notes),
          "; ".join(b_fails[:3]))

    # Determinism: regenerate an SVG and compare.
    if metas:
        probe = metas[0]["slug"]
        regen = site.illustration_for(metas[0])
        on_disk = (SITE / "assets" / f"{probe}.svg").read_text(encoding="utf-8").strip()
        check(f"svg deterministic for {probe}", regen.strip() == on_disk)

    # Publication gates across every text file in the artifact tree.
    # Screenshot binaries (png/jpg under assets/screenshots or site/assets)
    # are the one deliberate exception to the size gate: allowed as image
    # assets, but individually size-reported so the operator sees them.
    violations = []
    oversize = []
    binaries: list[str] = []
    rogue_binaries = []
    for p in ROOT.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            try:
                content = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, ValueError):
                rel = p.relative_to(ROOT).as_posix()
                if (p.suffix.lower() in (".png", ".jpg")
                        and (rel.startswith("assets/screenshots/")
                             or rel.startswith("site/assets/"))):
                    binaries.append(f"{rel} -- {p.stat().st_size} bytes")
                else:
                    rogue_binaries.append(rel)
                continue
            if p.stat().st_size > SIZE_LIMIT:
                oversize.append(str(p.relative_to(ROOT)))
            hits = util.glyph_scan(content)
            if hits:
                violations.append(f"{p.relative_to(ROOT)}: {', '.join(hits[:3])}")
    check("glyph gate (ASCII-only, no emoji, no check marks)", not violations,
          "; ".join(violations[:5]))
    check(f"size gate (no text file over {SIZE_LIMIT // 1024}KB)", not oversize,
          "; ".join(oversize[:5]))
    check("binary gate (only png/jpg screenshot assets; no rogue binaries)",
          not rogue_binaries, "; ".join(rogue_binaries[:5]))
    if binaries:
        lines.append("binary asset size report: " + "; ".join(binaries))
        record.append("binary asset size report: " + "; ".join(binaries))
    else:
        lines.append("binary asset size report: no screenshot binaries stored")
        record.append("binary asset size report: no screenshot binaries stored")

    # Ledger sanity: every published post is covered.
    ledger = util.load_json(LEDGER, {})
    for m in metas:
        check(f"ledger covers {m['slug']}", m["slug"] in ledger)

    ok = not failures
    lines.append(f"verify result: {'ALL CHECKS PASS' if ok else 'FAILURES: ' + ', '.join(failures)}")
    n_checks = sum(1 for l in lines if l.startswith(("PASS -", "FAIL -")))
    shot_n = sum(1 for m in metas if str(m.get("illustration", "")) == "screenshot")
    gen_n = sum(1 for m in metas if str(m.get("illustration", "")) != "screenshot")
    record.insert(0, f"mode: verify -- {n_checks} checks, "
                     f"{'ALL PASS' if ok else 'FAILURES: ' + ', '.join(failures[:6])}")
    record.insert(1, f"posts: {len(metas)}; illustration modes: {shot_n} "
                     f"screenshot, {gen_n} generated (labels on every page)")
    record.append("full per-check listing printed to stdout; this record "
                  "carries section outcomes, methods, and all failures")
    append_result(record)
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
        site.build_site(scratch, POSTS, CSS_SRC, site.load_config(CONFIG),
                        screenshots_dir=SCREENSHOTS)
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


# ---------------------------------------------------------------------------
# Mounted-subpath serving test (the "localhost/site/" reproduction)
# ---------------------------------------------------------------------------

def _workspace_root() -> Path:
    """Walk up from the artifact to the workspace root (goals/tasks/workflows
    markers); fall back to the artifact directory itself."""
    for cand in [ROOT, *ROOT.parents]:
        if all((cand / m).is_dir() for m in ("goals", "tasks", "workflows")):
            return cand
    return ROOT


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # silence per-request stderr noise
        pass


def _http_get(opener, url: str):
    """GET with redirects followed (browser-like). Returns (status, final_url,
    body_bytes); status None means a transport-level error."""
    try:
        with opener.open(urllib.request.Request(
                url, headers={"User-Agent": "gazette-verify/1.0"}), timeout=10) as r:
            return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as exc:
        return exc.code, url, b""
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, url, str(exc).encode()


def _browse_page(opener, page_url: str, prefix_check: str | None):
    """Fetch a page, then fetch every internal href/src a browser would
    resolve from it. Returns (failures, fetched_ref_count)."""
    fails: list[str] = []
    st, final, body = _http_get(opener, page_url)
    if st != 200:
        return [f"{page_url} -> HTTP {st}"], 0
    refs = re.findall(r'(?:href|src)="([^"]+)"', body.decode("utf-8"))
    internal, seen = [], set()
    for ref in refs:
        if ref.startswith(("http://", "https://", "mailto:", "#", "data:")):
            continue
        if prefix_check and not ref.startswith(prefix_check):
            fails.append(f"non-prefixed internal ref {ref!r} on {page_url}")
            continue
        target = urljoin(final, ref.split("#")[0])
        if target not in seen:
            seen.add(target)
            internal.append((ref, target))
    for ref, target in internal:
        st2, _, _ = _http_get(opener, target)
        if st2 != 200:
            fails.append(f"{target} (from {ref!r}) -> HTTP {st2}")
    return fails, len(internal)


def _mounted_subpath_test(cfg: dict) -> tuple[list[str], list[str]]:
    """Reproduce the user report: serve the site under a subpath with the
    stdlib http.server on an ephemeral port and browse it as a browser would.

    Mode A (default, page-relative refs): the tracked site/ is served from
    the workspace root at its real deep subpath; a conforming server either
    redirects /site -> /site/ (301, recorded) or the browser lands on the
    slash form, after which every relative ref resolves under the mount.
    Mode B (path_prefix=/site/): a scratch build with prefix-absolute refs,
    served from a temp root -- the literal localhost/site/ mount -- where
    root-relative refs must also all answer 200.

    Returns (failures, notes); notes carry the method record for RESULT.md.
    """
    import tempfile

    fails: list[str] = []
    notes: list[str] = []
    probe_slug = None
    post_files = sorted(POSTS.glob("*.md"))
    if post_files:
        probe_slug = post_files[0].stem

    # ---- Mode A: tracked default-mode build at its workspace subpath.
    ws_root = _workspace_root()
    try:
        site_rel = SITE.relative_to(ws_root).as_posix()
    except ValueError:
        site_rel = "site"
        ws_root = ROOT
    httpd = _serve_dir(ws_root)
    try:
        opener = urllib.request.build_opener()
        base = f"http://127.0.0.1:{httpd.server_address[1]}"
        mount = f"{base}/{site_rel}"
        st, _, _ = _http_get(_no_redirect_opener(), mount)
        notes.append(f"mount diag: GET /{site_rel} without trailing slash -> "
                     f"HTTP {st} (a conforming server 301-redirects to the "
                     f"slash form; a rewriting server that does not is what "
                     f"breaks page-relative refs)")
        a_fails, n_refs = _browse_page(opener, mount + "/", None)
        if probe_slug:
            f2, n2 = _browse_page(opener, f"{mount}/posts/{probe_slug}.html", None)
            a_fails += f2
            n_refs += n2
        css_url = urljoin(mount + "/", "styles.css")
        st_css, _, _ = _http_get(opener, css_url)
        if st_css != 200:
            a_fails.append(f"stylesheet {css_url} -> HTTP {st_css}")
        if a_fails:
            fails += [f"[A] {f}" for f in a_fails[:4]]
        else:
            notes.append(f"mode A ok: {n_refs} internal refs answered 200 under "
                         f"/{site_rel}/ (default page-relative mode)")
    finally:
        httpd.shutdown()
        httpd.server_close()

    # ---- Mode B: scratch prefix-mode build served at /site/.
    with tempfile.TemporaryDirectory(prefix="gazette-mount-") as tmp:
        root_b = Path(tmp)
        cfg_b = dict(cfg)
        cfg_b["path_prefix"] = "/site/"
        site.build_site(root_b / "site", POSTS, CSS_SRC, cfg_b,
                        screenshots_dir=SCREENSHOTS)
        httpd = _serve_dir(root_b)
        try:
            opener = urllib.request.build_opener()
            base = f"http://127.0.0.1:{httpd.server_address[1]}/site"
            b_fails, n_refs = _browse_page(opener, base + "/", "/site/")
            if probe_slug:
                f2, n2 = _browse_page(opener, f"{base}/posts/{probe_slug}.html",
                                      "/site/")
                b_fails += f2
                n_refs += n2
            rss_txt = (root_b / "site" / "rss.xml").read_text(encoding="utf-8")
            want = cfg["base_url"].rstrip("/") + "/site/posts/"
            if want not in rss_txt:
                b_fails.append(f"rss links do not combine base_url + prefix "
                               f"(expected {want})")
            if b_fails:
                fails += [f"[B] {f}" for f in b_fails[:4]]
            else:
                notes.append(f"mode B ok: {n_refs} prefix-absolute internal refs "
                             f"answered 200 under /site/ (path_prefix mode); rss "
                             f"links = base_url + prefix")
        finally:
            httpd.shutdown()
            httpd.server_close()
    notes.append("mount test method: stdlib http.server on 127.0.0.1 ephemeral "
                 "port, browser-like GETs (redirects followed), every internal "
                 "href/src fetched; mode A rooted at the workspace root, mode B "
                 "at a temp root with path_prefix=/site/")
    return fails, notes


def _serve_dir(directory: Path):
    handler = functools.partial(_QuietHandler, directory=str(directory))
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def _no_redirect_opener():
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    return urllib.request.build_opener(NoRedirect)


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
    ap.add_argument("--fetch-screenshots", action="store_true",
                    help="render real archived pages per subject with a "
                         "headless browser (CHROME_BIN or PATH probe; "
                         "web.archive.org egress required); every attempt "
                         "logged; failures degrade to labeled generated art; "
                         "a fail-fast render probe runs first")
    ap.add_argument("--probe-render", action="store_true",
                    help="offline first-run check: render a data: page "
                         "through the exact production invocation (fresh "
                         "temp profile included) and validate the png "
                         "(magic, dimensions, non-blank floor); also run "
                         "automatically (fail-fast) at the start of "
                         "--fetch-screenshots")
    ap.add_argument("--verify", action="store_true",
                    help="verify the built site and gate compliance")
    args = ap.parse_args()

    if args.verify:
        return verify()
    if args.probe_render:
        return probe_render_mode()
    if args.fetch_screenshots:
        return fetch_screenshots()
    if args.rebuild_only:
        rebuild_only()
        return 0
    run_pipeline(args.posts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
