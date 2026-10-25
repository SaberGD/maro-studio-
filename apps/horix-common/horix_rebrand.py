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
FACEBOOK = "https://www.facebook.com/sabergroup.academy/"
INSTAGRAM = "https://www.instagram.com/sabergroup.academy"
TELEGRAM = "https://t.me/SABERGROUPEG"
# WhatsApp with a ready message ("Hello, I am coming from HORIX and want to know about the courses
# and services"), as in HORIX.
WHATSAPP = ("https://wa.me/201040784390?text=%D9%85%D8%B1%D8%AD%D8%A8%D9%8B%D8%A7%D8%8C%20%D8%AC%D8%A7%D9%8A%20%D9%85%D9%86%20"
            "HORIX%20%D9%88%D8%B9%D8%A7%D9%8A%D8%B2%20%D8%A3%D8%B9%D8%B1%D9%81%20%D8%B9%D9%86%20%D8%A7%D9%84%D9%83%D9%88%D8%B1%D8%B3%D8%A7%D8%AA%20"
            "%D9%88%D8%A7%D9%84%D8%AE%D8%AF%D9%85%D8%A7%D8%AA")

# HORIX palette (apps/sg-ps/brand/HORIX-Brand-Guide.md).
INK = 0x141314
GRAPHITE = 0x2A2727
AMBER = 0xEA993F
RED = 0xD63C32
IVORY = 0xF3EFE8
# HORIX's own dark theme (apps/sg-ps, theme.rs `Horix`): the colours every HORIX app's interface
# takes, so the family looks like one program.
UI = {
    "canvas": 0x0E0E0F,  # the page behind documents
    "chrome": 0x141415,  # bars
    "dock": 0x111112,  # docked panels' ground
    "card": 0x1A1A1C,  # panels
    "border": 0x28282C,
    "field": 0x232326,
    "field_border": 0x343439,
    "hover": 0x2C2C30,
    "pressed": 0x38383E,
    "separator": 0x26262A,
    "text": 0xF3EFE8,
    "text_dim": 0x96969E,
    "text_faint": 0x606068,
    "icon": 0xC4C4CC,
    "accent": 0xEA993F,
    "accent_text": 0xF6C894,
    "selected": 0x2C2C30,
    "edge": 0x0A0A0B,  # hairlines between bars
}

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


EXE_VERSION = """\
    // HORIX: the release's version (HORIX_VERSION, set by the desktop build) as the exe's, which
    // HORIX Launcher checks against the release it installed; upstream's package version otherwise.
    println!("cargo:rerun-if-env-changed=HORIX_VERSION");
    if let Ok(v) = std::env::var("HORIX_VERSION") {
        res.set("ProductVersion", &v).set("FileVersion", &v);
    }
"""
WINRES = "    let mut res = winresource::WindowsResource::new();\n"


def exe_version(root: Path, rel: str) -> None:
    """The Windows exe's ProductVersion is the release's (HORIX_VERSION from the desktop build),
    not upstream's package version: HORIX Launcher rolls back a portable install whose exe reports
    another version than the release it downloaded."""
    edit(root, rel, [(WINRES, WINRES + EXE_VERSION)])


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


def ui(name: str) -> str:
    """HORIX's dark theme colour `name` as a Rust hex literal."""
    return hexrgb(UI[name])


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


def apply_patches(root: Path, patches: Path) -> int:
    """Unified diffs in `patches` (made against the rebranded tree), applied in name order.
    Returns how many were applied."""
    import os
    import subprocess
    n = 0
    for diff in sorted(patches.glob("*.diff")):
        # LF everywhere (a Windows checkout may hand us CRLF), from stdin, so it reads the same.
        data = diff.read_bytes().replace(b"\r\n", b"\n")
        # The work dir may sit inside this repository (CI builds in .horix-build/): without the
        # ceiling git would resolve paths against the outer repository and skip every file.
        env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(Path(root).resolve().parent)}
        r = subprocess.run(["git", "apply", "--verbose", "--whitespace=nowarn", "-p1", "-"], cwd=root, input=data, capture_output=True, env=env)
        err = r.stderr.decode(errors="replace")
        if r.returncode != 0 or "Skipped patch" in err:
            fail(f"patch {diff.name} does not apply:\n{err}")
        print(f"rebrand: applied {diff.name}")
        n += 1
    return n


def install_home(root: Path, app_dir: Path, version: str, ui_src: str = "crates/ui-egui/src") -> None:
    """HORIX Home, the start screen the HORIX family shares (home/horix_home.rs), and the app's use
    of it (<app>/home/horix_app_home.rs, its version filled in, and its other files), into the app's UI crate. The app's
    patches (patches/*-horix-home.diff) declare the modules and show the screen."""
    dest = root / ui_src
    if not dest.is_dir():
        fail(f"{ui_src}: not found")
    (dest / "horix_home.rs").write_bytes((HERE / "home/horix_home.rs").read_bytes())
    # Its icons and faces (home/make_assets.py), beside it.
    assets = dest / "horix_home_assets"
    assets.mkdir(exist_ok=True)
    for f in sorted((HERE / "home/assets").iterdir()):
        if f.suffix in (".a8", ".rgba", ".ttf"):
            (assets / f.name).write_bytes(f.read_bytes())
    glue = (app_dir / "home/horix_app_home.rs").read_text(encoding="utf-8")
    (dest / "horix_app_home.rs").write_text(glue.replace("@HORIX_APP_VERSION@", version), encoding="utf-8")
    # Anything else the glue includes (a logo), as is.
    for extra in sorted((app_dir / "home").iterdir()):
        if extra.is_file() and extra.name != "horix_app_home.rs":
            (dest / extra.name).write_bytes(extra.read_bytes())
