#!/usr/bin/env python3
"""Arabic UI text for HORIX (start screen, title bar), as SVG outlines.

egui does not shape Arabic (no letter joining, no right-to-left order), so the few Arabic lines
on the start screen are shaped here with HarfBuzz and saved as white SVG paths; the app tints
them with the theme colour. Re-run after changing a line:

    pip install uharfbuzz fonttools
    python3 -I apps/sg-ps/tools/arabic_svg.py <Cairo variable font .ttf> apps/sg-ps/assets/text

The Cairo variable font is https://github.com/google/fonts/tree/main/ofl/cairo (OFL).
"""

import re
import sys
from io import BytesIO
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

# name -> (text, weight)
LINES = {
    "soon-title": ("قريبًا", 800),
    "soon-apps": ("بدائل After Effects و Premiere و Illustrator و Lightroom", 500),
    "soon-cta": ("احجز تجربتك المُبكرة", 700),
    "dl-short": ("نسخة ويندوز وماك", 600),
    "dl-cta": ("حمّل HORIX على ويندوز أو ماك", 700),
}
UPM_SIZE = 100.0  # SVG units per em


def instance(src: Path, weight: int) -> bytes:
    font = TTFont(src)
    axes = {"wght": weight}
    if "fvar" in font and any(a.axisTag == "slnt" for a in font["fvar"].axes):
        axes["slnt"] = 0
    out = BytesIO()
    instantiateVariableFont(font, axes, inplace=False).save(out)
    return out.getvalue()


def runs(text: str):
    """Split into directional runs, in visual order for a right-to-left line.
    Latin words (with the spaces between them) are left-to-right runs; everything else is Arabic."""
    parts = re.split(r"([A-Za-z0-9][A-Za-z0-9 .]*[A-Za-z0-9]|[A-Za-z0-9])", text)
    logical = [(p, "ltr" if re.match(r"[A-Za-z0-9]", p) else "rtl") for p in parts if p]
    return list(reversed(logical))


def render(font_bytes: bytes, text: str) -> tuple[str, float, tuple[float, float]]:
    face = hb.Face(font_bytes)
    font = hb.Font(face)
    tt = TTFont(BytesIO(font_bytes))
    upem = tt["head"].unitsPerEm
    scale = UPM_SIZE / upem
    glyph_set = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    hhea = tt["hhea"]
    asc, desc = hhea.ascent * scale, -hhea.descent * scale
    paths, x, top, bottom = [], 0.0, float("inf"), float("-inf")
    for chunk, direction in runs(text):
        buf = hb.Buffer()
        buf.add_str(chunk)
        buf.guess_segment_properties()
        buf.direction = direction
        hb.shape(font, buf, {"kern": True, "liga": True})
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            pen = SVGPathPen(glyph_set)
            gx, gy = x + pos.x_offset * scale, asc - pos.y_offset * scale
            glyph_set[order[info.codepoint]].draw(TransformPen(pen, (scale, 0, 0, -scale, gx, gy)))
            bounds = BoundsPen(glyph_set)
            glyph_set[order[info.codepoint]].draw(TransformPen(bounds, (scale, 0, 0, -scale, gx, gy)))
            if bounds.bounds:
                top, bottom = min(top, bounds.bounds[1]), max(bottom, bounds.bounds[3])
            d = pen.getCommands()
            if d:
                paths.append(d)
            x += pos.x_advance * scale
    return " ".join(paths), x, (top, bottom)


def main() -> None:
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    cache: dict[int, bytes] = {}
    shaped = {name: render(cache.setdefault(weight, instance(src, weight)), text) for name, (text, weight) in LINES.items()}
    # One vertical box for every line (the tallest marks of all of them), so equal heights in the
    # app mean equal type sizes and a shared baseline.
    top = min(b[0] for _, _, b in shaped.values()) - 2
    bottom = max(b[1] for _, _, b in shaped.values()) + 2
    for name, (d, w, _) in shaped.items():
        (out / f"{name}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {top:.1f} {w:.1f} {bottom - top:.1f}">'
            f'<path fill="#FFFFFF" d="{d}"/></svg>\n', encoding="utf-8")
        print(f"{name}: {w:.1f} x {bottom - top:.1f}")


if __name__ == "__main__":
    main()
