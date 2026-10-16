#!/usr/bin/env python3
"""A wide HORIX wordmark (falcon beside the HORIX letters) for places that need a one-line logo,
such as the launcher's header. Made from the official paths without redrawing them:
apps/sg-ps/assets/horix-symbol.svg (falcon) and horix-lockup.svg (letters).

    python3 -I apps/horix-common/tools/make_wordmark.py <out-dir>

Writes horix-wordmark-on-dark.svg (Falcon Ivory letters) and horix-wordmark-on-light.svg
(Horus Ink letters); the amber eye and the red X keep their colours. Prints the aspect ratio.
"""

import re
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[2] / "sg-ps/assets"
# Measured from the lockup (rendered at 1:1): falcon x 345..1394, y 316..1069; letters
# x 227..1560, y 1153..1423.
LETTERS = (227, 1153, 1333, 270)
FALCON = (345, 316, 1049, 753)
H = 360.0
GAP = 64.0


def paths(svg: str) -> list[str]:
    """Every shape element (path, polygon, rect), in document order."""
    return re.findall(r"<(?:path|polygon|rect) [^>]+/>", svg)


def main() -> None:
    out = Path(sys.argv[1])
    symbol = paths((ASSETS / "horix-symbol.svg").read_text(encoding="utf-8"))
    lockup = paths((ASSETS / "horix-lockup.svg").read_text(encoding="utf-8"))
    letters = [p for p in lockup if p not in symbol]
    s = H / FALCON[3]
    fw = FALCON[2] * s
    ly = (H - LETTERS[3]) / 2
    width = fw + GAP + LETTERS[2]
    for name, ink in (("on-dark", "#F3EFE8"), ("on-light", "#141314")):
        fal = "\n".join(p.replace('fill="#F3EFE8"', f'fill="{ink}"') for p in symbol)
        let = "\n".join(p.replace('fill="#F3EFE8"', f'fill="{ink}"') for p in letters)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {H:.0f}" role="img" aria-label="HORIX">\n'
               f'<g transform="scale({s:.5f}) translate({-FALCON[0]} {-FALCON[1]})">\n{fal}\n</g>\n'
               f'<g transform="translate({fw + GAP - LETTERS[0]:.2f} {ly - LETTERS[1]:.2f})">\n{let}\n</g>\n</svg>\n')
        (out / f"horix-wordmark-{name}.svg").write_text(svg, encoding="utf-8")
    print(f"aspect {width / H:.4f} ({width:.0f} x {H:.0f})")


if __name__ == "__main__":
    main()
