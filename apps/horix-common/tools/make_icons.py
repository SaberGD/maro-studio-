#!/usr/bin/env python3
"""App icons for the HORIX family (Horix Vectors, Horix Light), from the HORIX falcon.

The falcon is copied from apps/sg-ps/assets/horix-symbol.svg without changing its geometry (brand
guide). Each product adds one small Horix Red badge in the lower right: a pen anchor with its
handles (Vectors), an aperture (Light), four app tiles (Launcher), a pixel grid under a pen
curve (One).

    pip install cairosvg pillow
    python3 -I apps/horix-common/tools/make_icons.py vectors apps/horix-vectors/assets/app-icon
    python3 -I apps/horix-common/tools/make_icons.py light   apps/horix-light/assets/app-icon
    python3 -I apps/horix-common/tools/make_icons.py launcher apps/horix-launcher/assets/app-icon
    python3 -I apps/horix-common/tools/make_icons.py one     apps/horix-one/assets/app-icon

Writes icon.svg (1024 tile), favicon.svg, and PNGs at 16..1024 plus icon.ico; macOS .icns is
built from the PNGs by Pillow.
"""

import math
import re
import sys
from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image

HERE = Path(__file__).resolve().parent
SYMBOL = HERE.parent.parent / "sg-ps/assets/horix-symbol.svg"
INK, IVORY, RED = "#141314", "#F3EFE8", "#D63C32"

BADGES = {
    # Pen anchor: a curve through a square anchor, with its two handles.
    "vectors": f"""
  <path d="M -118 70 C -60 -60, 60 -60, 118 70" fill="none" stroke="{IVORY}" stroke-width="20" stroke-linecap="round"/>
  <line x1="-96" y1="-28" x2="96" y2="-28" stroke="{IVORY}" stroke-width="12" stroke-linecap="round"/>
  <circle cx="-96" cy="-28" r="20" fill="{IVORY}"/>
  <circle cx="96" cy="-28" r="20" fill="{IVORY}"/>
  <rect x="-30" y="-58" width="60" height="60" rx="6" fill="{RED}" stroke="{IVORY}" stroke-width="14"/>""",
    # HORIX One: a pixel grid (Pixel) under a pen curve with its anchors (Vector), one product.
    "one": "".join(
        f'\n  <rect x="{x}" y="{y}" width="56" height="56" rx="8" fill="{IVORY}"/>' for x in (-112, -50) for y in (-10, 52)
    ) + f"""
  <path d="M -112 -40 C -40 -150, 60 -150, 112 -10" fill="none" stroke="{IVORY}" stroke-width="18" stroke-linecap="round"/>
  <rect x="-130" y="-58" width="36" height="36" rx="5" fill="{RED}" stroke="{IVORY}" stroke-width="10"/>
  <rect x="94" y="-28" width="36" height="36" rx="5" fill="{RED}" stroke="{IVORY}" stroke-width="10"/>""",
    # Launcher: four app tiles.
    "launcher": "".join(
        f'\n  <rect x="{x}" y="{y}" width="92" height="92" rx="20" fill="{IVORY}"/>' for x in (-104, 12) for y in (-104, 12)
    ),
    # Aperture: a ring, a hexagonal opening, and the six blade edges running from it to the ring.
    "light": f'''
  <circle r="118" fill="none" stroke="{IVORY}" stroke-width="18"/>
  <polygon points="{' '.join(f'{46*math.cos(math.radians(a)):.1f},{46*math.sin(math.radians(a)):.1f}' for a in range(0, 360, 60))}" fill="none" stroke="{IVORY}" stroke-width="14" stroke-linejoin="round"/>''' + "".join(
        f'\n  <line x1="{46*math.cos(math.radians(a)):.1f}" y1="{46*math.sin(math.radians(a)):.1f}" x2="{112*math.cos(math.radians(a+62)):.1f}" y2="{112*math.sin(math.radians(a+62)):.1f}" stroke="{IVORY}" stroke-width="14" stroke-linecap="round"/>' for a in range(0, 360, 60)),
}


def falcon_paths() -> str:
    svg = SYMBOL.read_text(encoding="utf-8")
    return "\n".join(re.findall(r"<path [^>]+/>", svg))


def tile(product: str, badge: bool = True) -> str:
    # The falcon sits a little up and left of centre so the badge has room (clear space kept).
    falcon = f'<g transform="translate(-160 -70) scale(.74)">\n{falcon_paths()}\n</g>'
    b = ""
    if badge:
        b = f"""
<g transform="translate(760 760)">
  <rect x="-170" y="-170" width="340" height="340" rx="78" fill="{RED}"/>{BADGES[product]}
</g>"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" role="img" aria-label="Horix {product.title()}">
<rect width="1024" height="1024" rx="176" fill="{INK}"/>
{falcon}{b}
</svg>
"""


def png(svg: str, size: int) -> Image.Image:
    return Image.open(BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size))).convert("RGBA")


def main() -> None:
    product, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    svg = tile(product)
    (out / "icon.svg").write_text(svg, encoding="utf-8")
    # Small sizes: the badge would turn to noise; the bare falcon tile reads better.
    small = tile(product, badge=False)
    (out / "favicon.svg").write_text(small, encoding="utf-8")
    for s in (16, 24, 32, 48, 64, 128, 256, 512, 1024):
        png(svg if s >= 48 else small, s).save(out / f"icon-{s}.png", optimize=True)
    big = png(svg, 1024)
    big.save(out / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    big.save(out / "icon.icns")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
