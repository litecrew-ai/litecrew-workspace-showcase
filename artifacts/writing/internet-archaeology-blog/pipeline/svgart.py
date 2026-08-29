"""Stage 4: procedural illustration.

Generates deterministic SVGs in a period-appropriate early-web aesthetic:
tiled starfields, table borders, 88x31 buttons, hit counters, and barricade
stripes. Randomness comes from random.Random seeded with a CRC32 of the slug,
so the same slug always yields the same artwork. Pure stdlib, no external
image services, and the output is inline-able in HTML (file:// safe).
"""

from __future__ import annotations

import binascii
import random
from xml.sax.saxutils import escape

# Classic 90s web palette: teal, purple, navy, olive, maroon, orange.
ACCENTS = ["#008080", "#800080", "#000080", "#808000", "#800000", "#ff6600", "#008000"]
BUTTON_SLOGANS = [
    "NETSCAPE NOW!",
    "BEST VIEWED 800x600",
    "MADE WITH NOTEPAD",
    "NO FRAMES ZONE",
    "SIGN MY GUESTBOOK",
    "WEBRING MEMBER",
    "UNDER CONSTRUCTION",
    "KEEP THE WEB FREE",
    "OPTIMIZED FOR IE3",
    "EMAIL ME!!",
]
COUNTER_LABELS = [
    "visitors since 1997",
    "hits! you are visitor",
    "souls passed through",
    "pages served",
]
BG_STYLES = [("#000030", "#c0c0ff"), ("#000000", "#ffffff"), ("#100040", "#ffd0f0"), ("#001830", "#b0ffd0")]


def _rng_for(slug: str) -> random.Random:
    return random.Random(binascii.crc32(slug.encode("utf-8")))


def _starfield(rng: random.Random, w: int, h: int, bg: str, star: str) -> str:
    """Tiled-starfield look: dark background with scattered pixel stars."""
    parts = [f'<rect width="{w}" height="{h}" fill="{bg}"/>']
    for _ in range(90):
        x, y = rng.randrange(0, w), rng.randrange(0, h)
        s = rng.choice([1, 1, 1, 2, 2, 3])
        bright = rng.random() < 0.25
        fill = "#ffffff" if bright else star
        parts.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{fill}"/>')
    return "\n".join(parts)


def _bevel_frame(x: int, y: int, w: int, h: int) -> str:
    """Netscape-style table border: light top-left, dark bottom-right."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#c0c0c0" '
        f'stroke="#808080" stroke-width="2"/>'
        f'<rect x="{x+4}" y="{y+4}" width="{w-8}" height="{h-8}" fill="none" '
        f'stroke="#000000" stroke-width="1"/>'
    )


def _button(rng: random.Random, x: int, y: int, slogan: str, accent: str) -> str:
    """The canonical 88x31 web button."""
    dark = "#000000"
    return (
        f'<g>'
        f'<rect x="{x}" y="{y}" width="88" height="31" fill="{dark}"/>'
        f'<rect x="{x+1}" y="{y+1}" width="86" height="29" fill="none" stroke="{accent}" stroke-width="1"/>'
        f'<rect x="{x+3}" y="{y+3}" width="82" height="11" fill="{accent}"/>'
        f'<text x="{x+44}" y="{y+11}" font-family="monospace" font-size="8" '
        f'fill="#ffffff" text-anchor="middle" font-weight="bold">DEAD WEB</text>'
        f'<text x="{x+44}" y="{y+24}" font-family="monospace" font-size="6" '
        f'fill="{accent}" text-anchor="middle">{escape(slogan[:20])}</text>'
        f'</g>'
    )


def _hit_counter(rng: random.Random, x: int, y: int, label: str) -> str:
    digits = "".join(str(rng.randrange(0, 10)) for _ in range(7))
    cells = []
    for i, d in enumerate(digits):
        cx = x + i * 13
        cells.append(
            f'<rect x="{cx}" y="{y}" width="11" height="18" fill="#000000" stroke="#00ff00" stroke-width="1"/>'
            f'<text x="{cx+5}" y="{y+14}" font-family="monospace" font-size="13" '
            f'fill="#00ff00" text-anchor="middle">{d}</text>'
        )
    text = (
        f'<text x="{x}" y="{y+30}" font-family="monospace" font-size="8" '
        f'fill="#c0c0c0">{escape(label)}</text>'
    )
    return "<g>" + "".join(cells) + text + "</g>"


def _barricade(x: int, y: int, w: int, h: int) -> str:
    """Under-construction stripes, diagonal in two alternating colors."""
    stripes = []
    stripe_w = 12
    i = 0
    for sx in range(x - h, x + w, stripe_w):
        color = "#ffcc00" if i % 2 == 0 else "#000000"
        stripes.append(
            f'<polygon points="{sx},{y+h} {sx+stripe_w},{y+h} {sx+stripe_w+h},{y} {sx+h},{y}" fill="{color}"/>'
        )
        i += 1
    clip = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#ffcc00"/>'
    )
    return (
        f'<g>{clip}{"".join(stripes)}'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#808080" stroke-width="2"/></g>'
    )


def post_illustration(slug: str, title: str, subtitle: str) -> str:
    """A 760x420 'mini homepage' card for a post. Deterministic per slug."""
    rng = _rng_for(slug)
    w, h = 760, 420
    bg, star = rng.choice(BG_STYLES)
    accent = rng.choice(ACCENTS)
    accent2 = rng.choice([c for c in ACCENTS if c != accent])
    slogan1 = rng.choice(BUTTON_SLOGANS)
    slogan2 = rng.choice([s for s in BUTTON_SLOGANS if s != slogan1])
    counter_label = rng.choice(COUNTER_LABELS)
    updated_year = rng.randrange(1996, 2003)

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)} memorial card">')
    svg.append(_starfield(rng, w, h, bg, star))
    svg.append(_bevel_frame(10, 10, w - 20, h - 20))
    # Masthead bar
    svg.append(f'<rect x="22" y="22" width="{w-44}" height="54" fill="#000000" stroke="{accent}" stroke-width="1"/>')
    svg.append(
        f'<text x="{w//2}" y="48" font-family="monospace" font-size="21" font-weight="bold" '
        f'fill="{accent}" text-anchor="middle">{escape(title.upper()[:26])}</text>'
    )
    svg.append(
        f'<text x="{w//2}" y="66" font-family="monospace" font-size="10" '
        f'fill="#c0c0c0" text-anchor="middle">{escape(subtitle[:64])}</text>'
    )
    # Content "cells" like a table layout
    svg.append(f'<rect x="22" y="86" width="{w-44}" height="180" fill="#000000" opacity="0.72" stroke="#808080"/>')
    lines = [
        "+++ SERVICE TERMINATED +++",
        "this page is a memorial",
        "the site it remembers is gone",
        "what remains: snapshots, stories,",
        "and the buttons below.",
        "",
        "please do not feed the 404",
    ]
    for i, line in enumerate(lines):
        ly = 108 + i * 22
        color = accent if i == 0 else "#00ff66" if "404" in line else "#c0c0c0"
        svg.append(
            f'<text x="40" y="{ly}" font-family="monospace" font-size="13" fill="{color}">{escape(line)}</text>'
        )
    # Barricade strip
    svg.append(_barricade(22, 276, w - 44, 26))
    # Buttons row
    svg.append(_button(rng, 34, 322, slogan1, accent))
    svg.append(_button(rng, 132, 322, slogan2, accent2))
    svg.append(
        f'<text x="240" y="334" font-family="monospace" font-size="10" fill="#c0c0c0">'
        f'[ this site is best viewed in any browser ]</text>'
    )
    # Hit counter
    svg.append(_hit_counter(rng, 34, 366, counter_label))
    svg.append(
        f'<text x="{w-36}" y="{h-24}" font-family="monospace" font-size="9" fill="#808080" '
        f'text-anchor="end">last updated {updated_year} - gfx generated offline</text>'
    )
    svg.append("</svg>")
    return "\n".join(svg)


def site_banner(title: str, subtitle: str) -> str:
    """A 468x60 classic ad-banner-size masthead for the site chrome."""
    rng = _rng_for("site-banner:" + title)
    w, h = 468, 60
    bg, star = BG_STYLES[0][0], "#ffffff"
    accent = "#00ff66"
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)} banner">',
        _starfield(rng, w, h, bg, star),
        f'<rect x="2" y="2" width="{w-4}" height="{h-4}" fill="none" stroke="{accent}" stroke-width="2"/>',
        f'<text x="{w//2}" y="30" font-family="monospace" font-size="22" font-weight="bold" fill="{accent}" text-anchor="middle">{escape(title)}</text>',
        f'<text x="{w//2}" y="48" font-family="monospace" font-size="10" fill="#c0c0c0" text-anchor="middle">{escape(subtitle)}</text>',
        "</svg>",
    ]
    return "\n".join(svg)
