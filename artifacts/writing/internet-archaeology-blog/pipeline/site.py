"""Stage 5: static site assembly -- the presentation layer.

Builds site/ from content/posts/*.md. Python 3.11 stdlib only, output works
when opened via file:// (relative links, one stylesheet, no scripts, no JS).

Design: "museum of the early web" (docs/design.md) -- a modern editorial
chrome (serif masthead, mono wall labels, warm archive paper) around
period-flavored artifacts (the procedural mini-homepage SVGs on dark screen
mats, the 468x60 banner and a simulated hit counter in the footer).

Determinism: nothing in the output depends on the build clock. Exhibit and
plate numbers derive from publication order, the counter from the post count,
RSS dates from post front matter, the stylesheet is copied byte-identical
from src/styles.css. Two builds from the same inputs are byte-identical.

Supported Markdown subset (the editorial passes stay inside it):
headings (#..###), paragraphs, "- " bullet lists, "> " blockquotes,
"---" horizontal rules, [text](url) links, and **bold**.
"""

from __future__ import annotations

import json
import re
from calendar import month_name
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from . import svgart, util

DEFAULT_CONFIG = {
    "base_url": "https://example.org/dead-web-gazette",
    "site_title": "The Dead Web Gazette",
    "tagline": "field notes from the old web",
    "description": (
        "A periodical of digital archaeology: illustrated, sourced memorials "
        "for things the internet used to have."
    ),
    "path_prefix": "",
}


def norm_prefix(cfg: dict) -> str:
    """path_prefix normalized to "" (page-relative mode, the default) or
    "/sub/path/" (prefix-absolute mode for servers that need it)."""
    p = str(cfg.get("path_prefix") or "").strip()
    if not p:
        return ""
    if not p.startswith("/"):
        p = "/" + p
    return p.rstrip("/") + "/"


def _url(cfg: dict, prefix: str, target: str) -> str:
    """Every internal URL goes through here. Default mode keeps the page-
    relative refs that make the site render via file:// (prefix is "" at the
    site root, "../" on post pages). When path_prefix is configured, internal
    refs are prefix-absolute (/site/styles.css) from every depth, which is
    what subpath mounts behind rewriting servers need."""
    p = norm_prefix(cfg)
    if p:
        return p + target.lstrip("/")
    return prefix + target


def load_config(path: Path | None) -> dict:
    """Merge site_config.json over DEFAULT_CONFIG. Degrades to defaults when
    the file is missing or malformed; run.py --verify flags a broken file."""
    cfg = dict(DEFAULT_CONFIG)
    if path and path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, dict):
            cfg.update({k: v for k, v in loaded.items() if isinstance(v, str)})
    return cfg


# ---------------------------------------------------------------------------
# Front matter and markdown-subset rendering
# ---------------------------------------------------------------------------

def parse_post(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ValueError(f"{path.name}: missing front matter")
    end = raw.find("\n---", 3)
    if end < 0:
        raise ValueError(f"{path.name}: unterminated front matter")
    fm_text = raw[3:end].strip("\n")
    body = raw[end + 4:].strip("\n")

    meta: dict = {"sources": []}
    current_list: list | None = None
    for line in fm_text.splitlines():
        # NB: `is not None`, not truthiness -- a freshly opened list is
        # empty (falsy) and truthiness here silently drops every item.
        # (Real v0 defect: SOURCES boxes shipped "(no sources recorded)"
        # for every post until the redesign's stats line exposed it.)
        if line.startswith("  - ") and current_list is not None:
            current_list.append(line[4:].strip())
            continue
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            meta[key] = []
            current_list = meta[key]
        else:
            meta[key] = _unquote(val)
            current_list = None

    meta["slug"] = meta.get("slug") or path.stem
    meta["body"] = body
    meta["words"] = util.word_count(_plain_text(body))
    meta["path"] = str(path)
    return meta


def _unquote(v: str) -> str:
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def _plain_text(md: str) -> str:
    txt = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    txt = re.sub(r"[#>*`-]", " ", txt)
    return txt


_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def _inline(text: str) -> str:
    out = _LINK_RE.sub(lambda m: f'<a href="{m.group(2)}">{escape(m.group(1))}</a>', text)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    return out


def render_markdown(md: str) -> str:
    html: list[str] = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("### "):
            html.append(f"<h3>{_inline(line[4:])}</h3>")
        elif line.startswith("## "):
            html.append(f"<h2>{_inline(line[3:])}</h2>")
        elif line.startswith("# "):
            html.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line.strip() == "---":
            html.append("<hr/>")
        elif line.startswith("> "):
            quote = []
            while i < len(lines) and lines[i].startswith("> "):
                quote.append(lines[i][2:])
                i += 1
            html.append(f"<blockquote><p>{_inline(' '.join(quote))}</p></blockquote>")
            continue
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{_inline(lines[i][2:])}</li>")
                i += 1
            html.append("<ul>" + "".join(items) + "</ul>")
            continue
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("# ", "## ", "### ", "- ", "> ", "---")):
                para.append(lines[i])
                i += 1
            html.append(f"<p>{_inline(' '.join(para))}</p>")
            continue
        i += 1
    return "\n".join(html)


# ---------------------------------------------------------------------------
# Presentation helpers (see docs/design.md for decision IDs)
# ---------------------------------------------------------------------------

def _fmt_date(iso: str) -> str:
    try:
        d = datetime.strptime(iso, "%Y-%m-%d").date()
        return f"{month_name[d.month]} {d.day}, {d.year}"
    except (ValueError, TypeError):
        return iso


def _rfc822(iso: str) -> str:
    try:
        d = datetime.strptime(iso, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return format_datetime(d)
    except (ValueError, TypeError):
        return ""


def _dek(m: dict) -> str:
    """One-line dek: the additive front-matter field if present, else a
    neutral fallback derived from the category (bodies stay untouched)."""
    d = str(m.get("dek", "")).strip()
    if d:
        return d
    cat = m.get("category") or "archive"
    return f"A memorial from the {cat} wing of the archive."


def _strip_leading_title(m: dict) -> str:
    """The post template renders its own title header, so the body's leading
    '# <title>' line (identical to the front-matter title) is elided to keep
    exactly one h1 per page. Anything else is left byte-for-byte."""
    lines = m["body"].splitlines()
    if lines and lines[0].strip() == f"# {m.get('title', '')}".strip():
        return "\n".join(lines[1:]).strip("\n")
    return m["body"]


def _cat_href(cfg: dict, m: dict, prefix: str) -> str:
    cat = m.get("category") or "uncategorized"
    return _url(cfg, prefix, f"categories.html#cat-{util.slugify(cat)}")


def _nav(cfg: dict, prefix: str, active: str) -> str:
    items = [
        ("index", "dispatches", _url(cfg, prefix, "index.html")),
        ("categories", "categories", _url(cfg, prefix, "categories.html")),
        ("about", "about", _url(cfg, prefix, "about.html")),
        ("rss", "rss", _url(cfg, prefix, "rss.xml")),
    ]
    parts = []
    for key, label, href in items:
        if key == active:
            parts.append(f'<a aria-current="page" href="{href}">{label}</a>')
        else:
            parts.append(f'<a href="{href}">{label}</a>')
    return '<nav class="site-nav" aria-label="site">\n' + "\n".join(parts) + "\n</nav>\n"


def _site_head(cfg: dict, prefix: str, active: str) -> str:
    """Compact wordmark bar used on every page except the index (D5)."""
    return (
        f'<header class="site-head">\n'
        f'<a class="wordmark" href="{_url(cfg, prefix, "index.html")}">'
        f'{escape(cfg["site_title"])}</a>\n'
        f"{_nav(cfg, prefix, active)}\n"
        f"</header>\n"
    )


def _masthead(cfg: dict, posts: list[dict]) -> str:
    cats = sorted({m.get("category") or "uncategorized" for m in posts})
    srcs = sum(len(m.get("sources", [])) for m in posts)
    stats = (
        f"{len(posts)} dispatch{'es' if len(posts) != 1 else ''} filed"
        f" -- {len(cats)} categor{'ies' if len(cats) != 1 else 'y'}"
        f" -- {srcs} source{'s' if srcs != 1 else ''} cited"
        f" -- est. 2026"
    )
    return (
        '<header class="site-masthead">\n'
        f'<p class="masthead-kicker">a periodical of digital archaeology</p>\n'
        f'<h1 class="masthead-title">{escape(cfg["site_title"])}</h1>\n'
        f'<p class="masthead-tagline">{escape(cfg["tagline"])}</p>\n'
        f'<p class="masthead-stats">{stats}</p>\n'
        "</header>\n"
    )


def _footer(cfg: dict, posts: list[dict]) -> str:
    counter = 19_980_000 + len(posts) * 7  # deterministic ornament (D6)
    banner = svgart.site_banner(cfg["site_title"], cfg["tagline"])
    return (
        '<footer class="site-foot">\n<div class="wrap">\n'
        f'<div class="foot-banner">{banner}</div>\n'
        f'<p class="foot-counter">you are visitor no. '
        f'<span class="counter-digits">{counter:08d}</span>'
        f" -- a simulated hit counter, in memoriam</p>\n"
        f'<p class="foot-colophon">{escape(cfg["site_title"])} -- built with the '
        f"python 3.11 standard library; one hand-written stylesheet; no javascript, "
        f"no trackers, no cookies -- best viewed in any browser</p>\n"
        "</div>\n</footer>\n"
    )


def illustration_for(m: dict) -> str:
    """The canonical per-post illustration. Deterministic per slug; the
    title/category only affect text labels, so the same post meta always
    yields the same SVG. Kept in one place so the builder and the verifier
    cannot drift apart."""
    subtitle = f"{m.get('category', '')} - a memorial in svg"
    return svgart.post_illustration(m["slug"], m.get("title", m["slug"]), subtitle)


SCREENSHOT_EXTS = (".png", ".jpg")


def screenshot_file_for(screenshots_dir: Path | None, slug: str) -> str | None:
    """Name of a stored source screenshot for this slug, or None."""
    if not screenshots_dir:
        return None
    for ext in SCREENSHOT_EXTS:
        if (screenshots_dir / f"{slug}{ext}").is_file():
            return f"{slug}{ext}"
    return None


def art_for(m: dict, cfg: dict, prefix: str,
            screenshots_dir: Path | None) -> tuple[str, str]:
    """(mode, html) for the hero/card art. The rendered mode is the truth:
    "screenshot" only when the front matter says so AND the stored binary
    exists -- a missing binary degrades to the generated SVG, labeled as
    such. A generated plate can never masquerade as a screenshot."""
    if str(m.get("illustration", "")) == "screenshot":
        fname = screenshot_file_for(screenshots_dir, m["slug"])
        if fname:
            alt = (f"Archived screenshot of {m.get('title', m['slug'])} as "
                   f"captured by the Wayback Machine")
            img = (f'<img src="{_url(cfg, prefix, "assets/" + fname)}" '
                   f'alt="{escape(alt)}"/>')
            return "screenshot", img
    return "generated", illustration_for(m)


def _plate_caption(m: dict, mode: str, exhibit_no: int) -> str:
    """The visible plate label (D11): the mode is printed on the page, with
    the archive provenance for screenshots."""
    if mode == "screenshot":
        ts = str(m.get("screenshot_timestamp", "") or "")
        fd = str(m.get("screenshot_fetched", "") or "")
        label = f"plate {exhibit_no:02d} -- screenshot: Wayback Machine"
        if ts:
            label += f", snapshot {ts}"
        if fd:
            label += f", fetched {fd}"
        label += ("; bytes actually retrieved from the Internet Archive for "
                  "this subject's url, not a reconstruction")
        return label
    return (
        f"plate {exhibit_no:02d} -- generated memorial art: a procedural "
        f'card seeded by the slug "{m["slug"]}"; the verifier regenerates it '
        "byte-for-byte"
    )


def _card(cfg: dict, m: dict, lead: bool, art_html: str) -> str:
    cls = "card card-lead" if lead else "card"
    post_href = _url(cfg, "", "posts/%s.html" % m["slug"])
    return (
        f'<article class="{cls}">\n'
        f'<a class="card-art" href="{post_href}">{art_html}</a>\n'
        f'<div class="card-body">\n'
        f'<p class="card-meta"><time datetime="{escape(m.get("date", ""))}">'
        f"{escape(_fmt_date(m.get('date', '')))}</time> -- "
        f'<a href="{_cat_href(cfg, m, "")}">'
        f"{escape(m.get('category') or 'uncategorized')}</a></p>\n"
        f'<h2 class="card-title"><a href="{post_href}">'
        f'{escape(m["title"])}</a></h2>\n'
        f'<p class="card-dek">{escape(_dek(m))}</p>\n'
        "</div>\n</article>"
    )


def _chip_row(cfg: dict, by_cat: dict[str, list[dict]]) -> str:
    """Category chips with counts (D10): every wing of the museum one
    click from the front page."""
    chips = []
    for cat in sorted(by_cat):
        n = len(by_cat[cat])
        count = f'<span class="chip-count">{n}</span>'
        target = _url(cfg, "", "categories.html#cat-%s" % util.slugify(cat))
        chips.append(f'<a class="chip" href="{target}">{escape(cat)} {count}</a>')
    return '<nav class="cat-chips" aria-label="categories">\n' + "\n".join(chips) + "\n</nav>"


def _dispatch_row(cfg: dict, m: dict) -> str:
    """One compact row of the complete-dispatch list (D10)."""
    cat = m.get("category") or "uncategorized"
    post_href = _url(cfg, "", "posts/%s.html" % m["slug"])
    return (
        '<li class="dispatch-row">\n'
        f'<p class="dispatch-meta"><time datetime="{escape(m.get("date", ""))}">'
        f"{escape(_fmt_date(m.get('date', '')))}</time><br/>"
        f'<a href="{_cat_href(cfg, m, "")}">{escape(cat)}</a></p>\n'
        f'<div class="dispatch-body">\n'
        f'<h3 class="dispatch-title"><a href="{post_href}">'
        f'{escape(m["title"])}</a></h3>\n'
        f'<p class="dispatch-dek">{escape(_dek(m))}</p>\n'
        "</div>\n</li>"
    )


def _provenance_html(m: dict, exhibit_no: int, mode: str) -> str:
    if mode == "screenshot":
        illus = "screenshot -- Wayback Machine"
        if m.get("screenshot_timestamp"):
            illus += ", snapshot %s" % m["screenshot_timestamp"]
        if m.get("screenshot_fetched"):
            illus += ", fetched %s" % m["screenshot_fetched"]
    else:
        illus = "generated memorial art (procedural svg)"
    rows = [
        ("Exhibit no.", f"{exhibit_no:03d}"),
        ("Data-source mode", m.get("data_source_mode", "not recorded")),
        ("Illustration", illus),
    ]
    if mode == "screenshot" and m.get("screenshot_url"):
        rows.append(("Screenshot of", str(m["screenshot_url"])))
    rows += [
        ("Generated", m.get("generated", "not recorded")),
        ("Generator", m.get("generator", "not recorded")),
        ("Editorial pass", m.get("editor", "(none)")),
        ("Status", m.get("status", "draft")),
    ]
    trs = "".join(
        f"<tr><td>{escape(k)}:</td><td>{escape(str(v))}</td></tr>" for k, v in rows
    )
    return (
        '<section class="exhibit">\n<h2 class="exhibit-title">PROVENANCE</h2>\n'
        f'<table class="prov-table">{trs}</table>\n</section>'
    )


def _sources_html(m: dict) -> str:
    items = []
    for s in m.get("sources", []):
        if "|" in s:
            name, url = s.split("|", 1)
            items.append(
                f'<li>{escape(name.strip())} -- '
                f'<a href={quoteattr(url.strip())} rel="noopener">{escape(url.strip())}</a></li>'
            )
        else:
            items.append(f"<li>{escape(s)}</li>")
    if not items:
        items.append("<li>(no sources recorded)</li>")
    return (
        '<section class="exhibit">\n<h2 class="exhibit-title">SOURCES</h2>\n'
        f'<ul class="src-list">{"".join(items)}</ul>\n</section>'
    )


def _pager(cfg: dict, prefix: str, newer: dict | None, older: dict | None) -> str:
    def cell(cls: str, label: str, m: dict | None) -> str:
        if not m:
            return f'<p class="{cls}"></p>'
        href = _url(cfg, prefix, "posts/%s.html" % m["slug"])
        return (
            f'<p class="{cls}"><span class="pager-label">{label}</span>'
            f'<a href="{href}">{escape(m["title"])}</a></p>'
        )

    home = _url(cfg, prefix, "index.html")
    return (
        '<nav class="pager" aria-label="post navigation">\n'
        f"{cell('pager-newer', 'newer dispatch', newer)}\n"
        f'<p class="pager-home"><a href="{home}">all dispatches</a></p>\n'
        f"{cell('pager-older', 'older dispatch', older)}\n"
        "</nav>"
    )


def _rss(cfg: dict, posts: list[dict]) -> str:
    base = cfg["base_url"].rstrip("/")
    # Default mode keeps the historical "{base}/posts/..." shape byte-for-byte;
    # prefix mode combines base_url + path_prefix ("/site/" -> "{base}/site/").
    effective = norm_prefix(cfg) or "/"
    newest_date = max((m.get("date", "") for m in posts), default="")
    items = []
    for m in posts:
        link = f"{base}{effective}posts/{m['slug']}.html"
        pub = _rfc822(m.get("date", ""))
        pub_line = f"    <pubDate>{pub}</pubDate>\n" if pub else ""
        items.append(
            "<item>\n"
            f"    <title>{escape(m['title'])}</title>\n"
            f"    <link>{escape(link)}</link>\n"
            f'    <guid isPermaLink="true">{escape(link)}</guid>\n'
            f"{pub_line}"
            f"    <description>{escape(_dek(m))}</description>\n"
            "</item>"
        )
    build_date = _rfc822(newest_date)
    build_line = f"    <lastBuildDate>{build_date}</lastBuildDate>\n" if build_date else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f"<!-- {escape(cfg['site_title'])} rss feed; regenerated deterministically by the pipeline -->\n"
        '<rss version="2.0">\n<channel>\n'
        f"    <title>{escape(cfg['site_title'])}</title>\n"
        f"    <link>{escape(base + effective)}</link>\n"
        f"    <description>{escape(cfg['description'])}</description>\n"
        "    <language>en</language>\n"
        f"{build_line}"
        + "\n".join(items)
        + "\n</channel>\n</rss>\n"
    )


def _page(cfg: dict, title: str, body_html: str, desc: str, depth: str = "") -> str:
    css = _url(cfg, depth, "styles.css")
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8"/>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>\n'
        f"<title>{escape(title)}</title>\n"
        f"<meta name=\"description\" content={quoteattr(desc)}/>\n"
        f'<link rel="stylesheet" href="{css}"/>\n'
        "</head>\n<body>\n"
        f"{body_html}\n</body>\n</html>\n"
    )


def _about_markdown() -> str:
    return (
        "The Dead Web Gazette is a small museum of things the internet used to have: "
        "defunct websites, old forums, 2000s blogs, early internet products, strange "
        "personal homepages, dead startups, old software, online subcultures, and "
        "forgotten stories. Each dispatch remembers one subject.\n\n"
        "## How dispatches are made\n\n"
        "- **Discover.** A Python pipeline (standard library only) queries keyless public "
        "APIs -- Hacker News Algolia, the Wikipedia API, and the Internet Archive Wayback "
        "CDX -- and falls back to a bundled offline seed corpus when the network is "
        "unavailable. The data-source mode of every post is recorded and printed in its "
        "provenance label.\n"
        "- **Distill facts.** Each subject gets a fact sheet with confidence levels and "
        "canonical source URLs. Medium-confidence facts appear only in hedged wording.\n"
        "- **Draft.** A deterministic scaffold is assembled from the fact sheet. No "
        "language model is called; an LLM hook is a documented extension point.\n"
        "- **Edit.** A human editorial pass turns the draft into the dispatch you are "
        "reading, keeping every claim sourced or explicitly hedged.\n"
        "- **Illustrate.** Each dispatch carries one SVG generated procedurally offline, "
        "seeded by the post slug: starfields, 88x31 buttons, hit counters, barricade "
        "stripes. The same slug always regenerates the same plate.\n"
        "- **Assemble.** A static site is built that renders from the file system with "
        "one hand-written stylesheet. No JavaScript, no servers, no trackers.\n\n"
        "## Truthfulness policy\n\n"
        "Dramatic tone, never fiction. Numbers that cannot be traced to a cited source "
        "do not appear, or appear hedged with the source named. Sources are printed as "
        "an exhibit label at the foot of every dispatch.\n\n"
        "## Illustrations: screenshots versus generated plates\n\n"
        "Every plate carries its mode as a visible label, and the two modes never "
        "blend. \"Screenshot: Wayback Machine\" means the image is made of bytes "
        "actually fetched from the Internet Archive for the subject's real URL; the "
        "snapshot timestamp and the fetch date are printed on the plate and recorded "
        "in the post's provenance box. \"Generated memorial art\" means the plate is "
        "the gazette's own procedural SVG, seeded by the post slug -- a memorial "
        "card, not a reproduction. There is no middle state: when the archive "
        "cannot be reached, the gazette ships the generated plate and says so "
        "rather than passing anything else off as a screenshot. Real screenshots "
        "can be refreshed at any time with `python3 run.py --fetch-screenshots` "
        "(needs egress to web.archive.org).\n\n"
        "## The site\n\n"
        "The design follows a museum-of-the-early-web brief: a modern editorial chrome "
        "around period artifacts. The illustrations, the 468x60 banner in the footer, "
        "and the hit counter are the period pieces, mounted on dark mats; everything "
        "else -- the typography, the grid, the labels -- is deliberately contemporary. "
        "The visitor counter is simulated and always has been; the number is a function "
        "of how many dispatches exist. A full design brief lives in docs/design.md.\n\n"
        "An RSS feed is published at rss.xml; set its link origin via base_url in "
        "site_config.json (documented in the README).\n\n"
        "## Colophon\n\n"
        "Built with the Python 3.11 standard library only. Repeat runs discover new "
        "subjects, skip already-covered ones via a ledger, and rebuild the site "
        "byte-identically."
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_site(site_dir: Path, posts_dir: Path, css_src: Path | None = None,
               config: dict | None = None,
               screenshots_dir: Path | None = None) -> dict:
    """Build index, about, categories, rss, and one page per post.
    Returns a build summary."""
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(config or {})
    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "posts").mkdir(exist_ok=True)
    (site_dir / "assets").mkdir(exist_ok=True)

    posts = sorted(
        (parse_post(p) for p in posts_dir.glob("*.md")),
        key=lambda m: (m.get("date", ""), m["slug"]),
        reverse=True,
    )
    # Accession numbers: oldest published post = exhibit 001 (D6).
    total = len(posts)

    if css_src and css_src.exists():
        (site_dir / "styles.css").write_bytes(css_src.read_bytes())
    # Screenshot source assets are copied into the build exactly like the
    # stylesheet: byte-identical copy of a source-of-truth file, so clean
    # state rebuilds stay reproducible.
    if screenshots_dir and screenshots_dir.is_dir():
        for shot in sorted(screenshots_dir.iterdir()):
            if shot.is_file() and shot.suffix.lower() in SCREENSHOT_EXTS:
                (site_dir / "assets" / shot.name).write_bytes(shot.read_bytes())

    # Post pages.
    for idx, m in enumerate(posts):
        illus = illustration_for(m)
        (site_dir / "assets" / f"{m['slug']}.svg").write_text(illus + "\n", encoding="utf-8")
        exhibit_no = total - idx
        newer = posts[idx - 1] if idx > 0 else None
        older = posts[idx + 1] if idx + 1 < total else None
        mode, art_html = art_for(m, cfg, "../", screenshots_dir)
        post_body = (
            f'<div class="wrap">\n{_site_head(cfg, "../", "index")}\n<main>\n'
            f'<article class="post">\n'
            f'<header class="post-head">\n'
            f'<p class="kicker"><a href="{_cat_href(cfg, m, "../")}">{escape(m.get("category") or "uncategorized")}</a></p>\n'
            f'<h1 class="post-title">{escape(m["title"])}</h1>\n'
            f'<p class="post-dek">{escape(_dek(m))}</p>\n'
            f'<p class="post-byline"><time datetime="{escape(m.get("date", ""))}">'
            f"{escape(_fmt_date(m.get('date', '')))}</time> -- {m['words']} words"
            f" -- exhibit no. {exhibit_no:03d}</p>\n"
            "</header>\n"
            f'<figure class="hero">\n<div class="hero-mount">{art_html}</div>\n'
            f"<figcaption>{escape(_plate_caption(m, mode, exhibit_no))}</figcaption>\n</figure>\n"
            f'<div class="prose">\n{render_markdown(_strip_leading_title(m))}\n</div>\n'
            f"{_provenance_html(m, exhibit_no, mode)}\n{_sources_html(m)}\n"
            f'{_pager(cfg, "../", newer, older)}\n'
            "</article>\n</main>\n</div>\n"
            f"{_footer(cfg, posts)}"
        )
        page = _page(
            cfg, f'{m["title"]} - {cfg["site_title"]}', post_body, _dek(m), "../"
        )
        (site_dir / "posts" / f'{m["slug"]}.html').write_text(page, encoding="utf-8")

    # Index page (D10 scale layout): masthead, nav, deck, category chips
    # with counts, lead card for the newest post, then a compact complete
    # dispatch list -- every post one click from the front page, scannable
    # at any corpus size.
    by_cat: dict[str, list[dict]] = {}
    for m in posts:
        by_cat.setdefault(m.get("category") or "uncategorized", []).append(m)

    if posts:
        lead_mode, lead_art = art_for(posts[0], cfg, "", screenshots_dir)
        cards_html = (
            '<section class="cards" aria-label="latest dispatch">\n'
            + _card(cfg, posts[0], lead=True, art_html=lead_art)
            + "\n</section>"
        )
        rows = "\n".join(_dispatch_row(cfg, m) for m in posts[1:])
        list_head = (
            '<h2 class="list-head">the complete dispatch list '
            f'<span class="list-count">({len(posts)} total)</span></h2>'
        )
        list_html = (
            f'<section class="dispatches" aria-label="all dispatches">\n'
            f"{list_head}\n<ul class=\"dispatch-list\">\n{rows}\n</ul>\n</section>"
        )
    else:
        cards_html = (
            '<section class="cards" aria-label="dispatches">\n'
            '<p class="deck-lede">No dispatches yet. Run the pipeline and an '
            "editorial pass.</p>\n</section>"
        )
        list_html = ""
    deck = (
        '<section class="deck">\n'
        '<p class="deck-lede">Each dispatch remembers one thing the web killed -- a '
        "site, a service, a piece of software -- with an illustration generated "
        "offline or an archived screenshot, labeled for what it is, and every "
        "claim sourced or explicitly hedged. "
        f'<a href="{_url(cfg, "", "about.html")}">How the gazette is made.</a></p>\n</section>'
    )
    index_body = (
        f'<div class="wrap">\n{_masthead(cfg, posts)}{_nav(cfg, "", "index")}\n'
        f"<main>\n{deck}\n{_chip_row(cfg, by_cat)}\n{cards_html}\n{list_html}\n</main>\n</div>\n"
        f"{_footer(cfg, posts)}"
    )
    (site_dir / "index.html").write_text(
        _page(cfg, f'{cfg["site_title"]} - {cfg["tagline"]}', index_body, cfg["description"]),
        encoding="utf-8",
    )

    # Categories page: published posts grouped by category.
    groups = []
    for cat in sorted(by_cat):
        members = by_cat[cat]
        rows = []
        for m in members:
            post_href = _url(cfg, "", "posts/%s.html" % m["slug"])
            rows.append(
                "<li>\n"
                f'<p class="cat-meta"><time datetime="{escape(m.get("date", ""))}">'
                f"{escape(_fmt_date(m.get('date', '')))}</time></p>\n"
                f'<h3 class="cat-title"><a href="{post_href}">'
                f'{escape(m["title"])}</a></h3>\n'
                f'<p class="cat-dek">{escape(_dek(m))}</p>\n'
                "</li>"
            )
        count = f"{len(members)} dispatch{'es' if len(members) != 1 else ''}"
        groups.append(
            f'<section class="cat-group" id="cat-{util.slugify(cat)}">\n'
            f'<div class="cat-name-row">\n<h2 class="cat-name">{escape(cat)}</h2>\n'
            f'<span class="cat-count">({count})</span>\n</div>\n'
            f'<ul class="cat-list">\n' + "\n".join(rows) + "\n</ul>\n</section>"
        )
    cat_body = (
        f'<div class="wrap">\n{_site_head(cfg, "", "categories")}\n<main>\n'
        '<div class="page-head">\n'
        '<p class="kicker">the collection</p>\n'
        '<h1 class="page-title">Categories</h1>\n'
        '<p class="page-dek">Dispatches grouped by the kind of thing they mourn.</p>\n'
        "</div>\n" + "\n".join(groups) + "\n</main>\n</div>\n"
        f"{_footer(cfg, posts)}"
    )
    (site_dir / "categories.html").write_text(
        _page(cfg, f'Categories - {cfg["site_title"]}', cat_body, cfg["description"]),
        encoding="utf-8",
    )

    # About page.
    about_body = (
        f'<div class="wrap">\n{_site_head(cfg, "", "about")}\n<main>\n'
        '<article class="post">\n'
        '<div class="page-head">\n'
        '<p class="kicker">the museum</p>\n'
        '<h1 class="page-title">About this gazette</h1>\n'
        f'<p class="page-dek">{escape(cfg["description"])}</p>\n'
        "</div>\n"
        f'<div class="prose">\n{render_markdown(_about_markdown())}\n</div>\n'
        "</article>\n</main>\n</div>\n"
        f"{_footer(cfg, posts)}"
    )
    (site_dir / "about.html").write_text(
        _page(cfg, f'About - {cfg["site_title"]}', about_body, cfg["description"]),
        encoding="utf-8",
    )

    # RSS feed.
    (site_dir / "rss.xml").write_text(_rss(cfg, posts), encoding="utf-8")

    return {"posts": len(posts), "slugs": [m["slug"] for m in posts]}
