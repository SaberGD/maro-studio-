"""Build HORIX Home's assets (assets/) from the HORIX Saber Group UI Kit.

Usage: python3 make_assets.py <HORIX-Saber-Group-UI-Kit dir>

- icons.a8: the kit's 48 px icons (Lucide, ISC; social logos from Simple Icons, CC0) as one
  alpha-only atlas, ICON_COLUMNS wide, in ICONS order (horix_home.rs's `Icon` follows it). egui
  draws them tinted, so every app shows them the same without an image decoder.
- inter-*.ttf, barlow-condensed-700.ttf: the kit's interface and display faces (SIL OFL), as
  TrueType for egui (the kit ships WOFF2).
- saber-group-logo.rgba: Saber Group's logo (brand/saber-group-logo.png, white with the amber
  +AI tab) at LOGO_SIZE, straight RGBA, for the Academy band.
"""
import shutil
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image

ICONS = [
    "plus", "folder", "home", "workspace", "courses", "external", "layers", "image",
    "pen", "book", "camera", "globe", "arrow", "file", "more", "grid",
    "list", "upload", "sparkles", "masks", "brush", "type", "files", "columns",
    "print", "sliders", "whatsapp", "facebook", "instagram", "telegram", "x", "check",
]
ICON_SIZE = 48
LOGO_SIZE = (376, 64)
ICON_COLUMNS = 8
FONTS = {
    "inter-latin-400-normal.woff2": "inter-400.ttf",
    "inter-latin-500-normal.woff2": "inter-500.ttf",
    "inter-latin-600-normal.woff2": "inter-600.ttf",
    "barlow-condensed-latin-700-normal.woff2": "barlow-condensed-700.ttf",
}
LICENSES = ["Inter-OFL.txt", "BarlowCondensed-OFL.txt", "Lucide-ISC.txt", "Simple-Icons-CC0.md"]


def main() -> None:
    kit = Path(sys.argv[1])
    out = Path(__file__).resolve().parent / "assets"
    out.mkdir(exist_ok=True)
    rows = -(-len(ICONS) // ICON_COLUMNS)
    atlas = Image.new("L", (ICON_COLUMNS * ICON_SIZE, rows * ICON_SIZE), 0)
    for i, name in enumerate(ICONS):
        icon = Image.open(kit / "assets/icons-png" / f"{name}.png").convert("RGBA")
        if icon.size != (ICON_SIZE, ICON_SIZE):
            icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
        atlas.paste(icon.getchannel("A"), ((i % ICON_COLUMNS) * ICON_SIZE, (i // ICON_COLUMNS) * ICON_SIZE))
    (out / "icons.a8").write_bytes(atlas.tobytes())
    for src, dst in FONTS.items():
        font = TTFont(kit / "assets/fonts" / src)
        font.flavor = None
        font.save(out / dst)
    here = Path(__file__).resolve().parent
    logo = Image.open(here / "brand/saber-group-logo.png").convert("RGBA").resize(LOGO_SIZE, Image.LANCZOS)
    (out / "saber-group-logo.rgba").write_bytes(logo.tobytes())
    for name in LICENSES:
        shutil.copy(kit / "licenses" / name, out / name)
    print(f"assets: {len(ICONS)} icons ({atlas.size[0]}x{atlas.size[1]}), {len(FONTS)} fonts")


if __name__ == "__main__":
    main()
