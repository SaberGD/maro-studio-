"""Shared rebrand helpers for the HORIX family apps (Horix Vectors, Horix Light).

Each app's rebrand.py imports this module and applies its edits to a pristine, unpacked upstream
source tree at build time (the same approach as apps/sg-ps/rebrand.py for HORIX). Every edit must
match, so an upstream change fails the build loudly instead of shipping the old branding; then
only the reported line needs updating.

Licence files (LICENSE-MIT, LICENSE-APACHE, NOTICE, ASSETS/ATTRIBUTION) are never touched: the
licences require the original copyright lines to stay.
"""

import base64
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

SABER_SITE = "https://sabergroupacademy.com"
DOWNLOADS_PAGE = "https://horix.si/"
FACEBOOK = "https://www.facebook.com/SABERGROUP.Courses/"
# WhatsApp with a ready message ("Hello, I am coming from HORIX and want to know about the courses
# and services"), as in HORIX.
WHATSAPP = ("https://wa.me/201103221873?text=%D9%85%D8%B1%D8%AD%D8%A8%D9%8B%D8%A7%D8%8C%20%D8%AC%D8%A7%D9%8A%20%D9%85%D9%86%20"
            "HORIX%20%D9%88%D8%B9%D8%A7%D9%8A%D8%B2%20%D8%A3%D8%B9%D8%B1%D9%81%20%D8%B9%D9%86%20%D8%A7%D9%84%D9%83%D9%88%D8%B1%D8%B3%D8%A7%D8%AA%20"
            "%D9%88%D8%A7%D9%84%D8%AE%D8%AF%D9%85%D8%A7%D8%AA")

# HORIX palette (apps/sg-ps/brand/HORIX-Brand-Guide.md).
INK = 0x141314
GRAPHITE = 0x2A2727
AMBER = 0xEA993F
RED = 0xD63C32
IVORY = 0xF3EFE8

# Files that carry licence or attribution text: left exactly as upstream wrote them.
LICENCE_FILES = re.compile(r"(^|/)(LICEN[CS]E[^/]*|NOTICE[^/]*|ASSETS\.md|ATTRIBUTION\.md|OFL-[^/]*)$", re.I)


def fail(msg: str) -> None:
    sys.exit(f"rebrand: {msg}")


def edit(root: Path, rel: str, pairs: list[tuple[str, str]]) -> None:
    """Exact find/replace in one file; each `old` must occur (all occurrences are replaced)."""
    path = root / rel
    if not path.is_file():
        fail(f"{rel}: file not found")
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            fail(f"{rel}: expected text not found:\n{old}")
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def files(root: Path, globs: list[str]) -> list[Path]:
    out: list[Path] = []
    for g in globs:
        out += [p for p in root.glob(g) if p.is_file() and not LICENCE_FILES.search(p.relative_to(root).as_posix())]
    return sorted(set(out))


def replace_everywhere(root: Path, globs: list[str], pairs: list[tuple[str, str]]) -> None:
    """Literal replacements across many files (UI code, its tests and translations alike, so the
    tests keep agreeing with the UI). Each `old` must occur at least once somewhere."""
    found = {old: 0 for old, _ in pairs}
    for path in files(root, globs):
        text = path.read_text(encoding="utf-8")
        new = text
        for old, rep in pairs:
            n = new.count(old)
            if n:
                found[old] += n
                new = new.replace(old, rep)
        if new != text:
            path.write_text(new, encoding="utf-8")
    missing = [old for old, n in found.items() if n == 0]
    if missing:
        fail("expected text not found anywhere:\n" + "\n".join(missing))


def rename(root: Path, globs: list[str], old: str, new: str) -> int:
    """The product name as a standalone word (VectorCraft -> Horix Vectors). Identifiers such as
    VectorcraftApp or vectorcraft_engine are untouched: they never reach the UI, and keeping them
    keeps upstream updates a re-run of this script."""
    name_re = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])")
    count = 0
    for path in files(root, globs):
        text = path.read_text(encoding="utf-8")
        out, n = name_re.subn(new, text)
        if n:
            path.write_text(out, encoding="utf-8")
            count += n
    if count == 0:
        fail(f"the name {old} was not found")
    return count


def hexrgb(v: int) -> str:
    return f"0x{v:06x}"


def png_size(path: Path) -> tuple[int, int]:
    """Width and height from a PNG's IHDR chunk (no image library: the build runs `python3 -I`)."""
    head = path.read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        fail(f"{path}: not a PNG")
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def replace_icons(root: Path, icon_dir: Path, upstream_dir: str) -> int:
    """Overwrite every upstream app icon with the HORIX one of the same kind and size, so every
    place that embeds or packages the icon (title bar, About, installers) shows HORIX. Each PNG
    size upstream uses must exist in `icon_dir` (tools/make_icons.py writes them)."""
    n = 0
    for p in sorted((root / upstream_dir).rglob("*")):
        if not p.is_file():
            continue
        if p.suffix == ".png":
            w, h = png_size(p)
            src = icon_dir / f"icon-{max(w, h)}.png"
            if w != h or not src.is_file():
                fail(f"{p.relative_to(root)}: no HORIX icon of {w}x{h}")
            p.write_bytes(src.read_bytes())
        elif p.suffix == ".svg":
            p.write_bytes((icon_dir / ("favicon.svg" if "small" in p.name else "icon.svg")).read_bytes())
        elif p.suffix == ".ico":
            p.write_bytes((icon_dir / "icon.ico").read_bytes())
        elif p.suffix == ".icns":
            p.write_bytes((icon_dir / "icon.icns").read_bytes())
        else:
            continue
        n += 1
    if n == 0:
        fail(f"{upstream_dir}: no icons found")
    return n


def favicon_data_uri(icon_dir: Path) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode((icon_dir / "favicon.svg").read_bytes()).decode()


def loader_html(name: str, product_line: str) -> str:
    """The loading screen: the HORIX falcon, the product name, a Horix Red rule, BY SABER GROUP."""
    symbol = (REPO / "apps/sg-ps/assets/horix-symbol.svg").read_text(encoding="utf-8")
    symbol = symbol.replace('role="img"', 'role="img" width="132" height="95"')
    return f"""
    <div class="horix-loader">
      {symbol.strip()}
      <div class="horix-name">{name}</div>
      <div class="horix-line">{product_line}</div>
      <div class="horix-rule"></div>
      <div class="horix-by">BY SABER GROUP</div>
    </div>"""


LOADER_CSS = f"""
    .horix-loader {{ display: flex; flex-direction: column; align-items: center; gap: 10px; color: #{IVORY:06X};
      font-family: Inter, system-ui, -apple-system, "Segoe UI", sans-serif; }}
    .horix-loader svg {{ animation: horix-breathe 1.8s ease-in-out infinite; }}
    .horix-name {{ font: 800 34px/1 "Barlow Condensed", "Arial Narrow", Inter, sans-serif; letter-spacing: 0; text-transform: uppercase; }}
    .horix-line {{ font-size: 12px; font-weight: 500; letter-spacing: .12em; color: #{IVORY:06X}; opacity: .85; }}
    .horix-rule {{ width: 28px; height: 2px; background: #{RED:06X}; }}
    .horix-by {{ font-size: 10.5px; font-weight: 500; letter-spacing: .12em; color: #8f8a84; }}
    @keyframes horix-breathe {{ 0%, 100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
    @media (prefers-reduced-motion: reduce) {{ .horix-loader svg {{ animation: none; }} }}
"""


def check_no_upstream_brand(root: Path, globs: list[str], allowed: list[str]) -> None:
    """No ArtCraft Discord / website link or old product name may be left in user-visible code."""
    bad = re.compile(r"discord\.gg/artcraft|getartcraft\.com|Join (our|Our|the ArtCraft) Discord")
    hits = []
    for path in files(root, globs):
        rel = path.relative_to(root).as_posix()
        if any(a in rel for a in allowed):
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            if bad.search(line) and not line.lstrip().startswith("//"):
                hits.append(f"{rel}:{i}: {line.strip()[:160]}")
    if hits:
        fail("upstream brand still visible:\n" + "\n".join(hits[:40]))


UPSTREAM_IN_TRANSLATION = re.compile(r"ArtCraft|Discord|getartcraft|GitHub", re.I)


def drop_branded_translations_tsv(root: Path, glob: str) -> int:
    """Translation lines (key TAB text) whose text still names ArtCraft, Discord or GitHub belong
    to links this build replaced: drop them, so those labels show in English (the new wording)
    instead of a translation of the old one."""
    n = 0
    for path in files(root, [glob]):
        lines = path.read_text(encoding="utf-8").split("\n")
        keep = [l for l in lines if not ("\t" in l and UPSTREAM_IN_TRANSLATION.search(l.split("\t", 1)[1]))]
        n += len(lines) - len(keep)
        path.write_text("\n".join(keep), encoding="utf-8")
    return n
