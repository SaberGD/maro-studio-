#!/usr/bin/env python3
"""Rebrand an unpacked LightCraft source tree as Horix Light (Saber Group).

Usage: python3 -I apps/horix-light/rebrand.py <path-to-lightcraft-source>

Every edit is an exact find/replace that must match, so an upstream change that moves the code
fails loudly here instead of silently shipping the old branding. Run it on a fresh copy of the
source; it is not meant to run twice on the same tree.

What it changes (UI only; licence files stay as the licences require):
  - "LightCraft" -> "Horix Light" in every user-visible string and translation.
  - The ArtCraft Discord / website / GitHub links -> Saber Group (Facebook, website, WhatsApp) and
    the HORIX download page.
  - The HORIX falcon app icon (apps/horix-light/assets/app-icon/) everywhere the app shows or
    packages its icon.
  - HORIX colours on the default Charcoal theme: Graphite chrome, Horus Ink canvas, Falcon Ivory
    text, Horix Red accent.
  - Web page: title, favicon, HORIX loading screen.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "horix-common"))
import horix_rebrand as hx  # noqa: E402

APP_NAME = "Horix Light"
PRODUCT_LINE = "THE PHOTO DEVELOPER"
CODE = ["crates/**/*.rs", "apps/**/*.rs", "crates/ui-egui/locales/*.json"]
WEB = "apps/lightcraft-web/index.html"


def links(root: Path) -> None:
    hx.edit(root, "crates/ui-egui/src/links.rs", [
        ('pub const DISCORD: &str = "https://discord.gg/artcraft";', f'pub const DISCORD: &str = "{hx.FACEBOOK}";'),
        ('pub const WEBSITE: &str = "https://getartcraft.com";', f'pub const WEBSITE: &str = "{hx.SABER_SITE}";'),
        ('pub const APP_PAGE: &str = "https://getartcraft.com/apps/lightcraft";', f'pub const APP_PAGE: &str = "{hx.DOWNLOADS_PAGE}";'),
        ('pub const GITHUB: &str = "https://github.com/storytold/lightcraft";', f'pub const GITHUB: &str = "{hx.WHATSAPP}";'),
        # Help and feedback stay useful: the user guide upstream wrote, and our WhatsApp.
        ('pub const FEEDBACK: &str = "https://github.com/storytold/lightcraft/issues/new";', f'pub const FEEDBACK: &str = "{hx.WHATSAPP}";'),
    ])
    # Labels (UI, tests and translation keys alike); before rename(), which changes the name.
    hx.replace_everywhere(root, ["crates/**/*.rs", "apps/**/*.rs"], [
        ("Join the ArtCraft Discord…", "Saber Group Academy on Facebook…"),
        ("Join the ArtCraft Discord", "Saber Group Academy on Facebook"),
        ("Join the ArtCraft community on Discord", "Saber Group Academy on Facebook"),
        ("ArtCraft — more creative apps", "Saber Group Academy — courses and services"),
        ("ArtCraft Website", "Saber Group Academy Website"),
        ("LightCraft on GitHub", "Contact Us: Courses & Services"),
        ("Source code on GitHub", "Contact us on WhatsApp"),
        ('("LightCraft website", crate::links::APP_PAGE)', '("Download the desktop app (Windows / Mac)", crate::links::APP_PAGE)'),
        ('("app.website", "LightCraft Website"', '("app.website", "Download the Desktop App (Windows / Mac)"'),
    ])
    hx.edit(root, "crates/ui-egui/src/panels/dialogs.rs", [
        # tr_format! only takes the format strings its catalog knows, so the licence line stays
        # and the Saber Group line goes above it.
        ('                            ui.label(crate::i18n::tr_format!(\n                                "MIT OR Apache-2.0. Fonts: {} (OFL). Icons: original.",',
         '                            ui.label(crate::i18n::tr("By Saber Group. Built on open-source software."));\n'
         '                            ui.label(crate::i18n::tr_format!(\n                                "MIT OR Apache-2.0. Fonts: {} (OFL). Icons: original.",'),
    ])


def theme(root: Path) -> None:
    rel = "crates/ui-egui/src/theme.rs"
    path = root / rel
    text = path.read_text(encoding="utf-8")
    start = text.index("impl Default for Tokens {")
    end = text.index("top_bar_h:", start)
    block = text[start:end]
    rgb = lambda v: f"Color32::from_rgb(0x{v >> 16:02x}, 0x{(v >> 8) & 255:02x}, 0x{v & 255:02x})"
    for field, old, new in [
        ("chrome", 0x2D2D2D, hx.GRAPHITE),
        ("canvas", 0x1C1C1C, hx.INK),
        ("grid_bg", 0x0F0F0F, 0x0E0D0E),
        ("cell", 0x1C1C1C, hx.INK),
        ("cell_selected", 0x2D2D2D, hx.GRAPHITE),
        ("divider", 0x1C1C1C, hx.INK),
        ("inset", 0x232323, 0x1F1C1C),
        ("field", 0x222222, 0x1E1B1B),
        ("field_border", 0x3C3C3C, 0x423C3C),
        ("button", 0x242424, 0x211E1E),
        ("button_border", 0x4C4C4C, 0x524B4B),
        ("hover", 0x3A3A3A, 0x3A3535),
        ("pressed", 0x3F3F3F, 0x433D3D),
        ("tool_active", 0x3F3F3F, 0x433D3D),
        ("text", 0xE2E2E2, hx.IVORY),
        ("text_label", 0xBCBCBC, 0xC4BEB6),
        ("text_dim", 0x8E8E8E, 0x97918A),
        ("text_disabled", 0x5C5C5C, 0x605A56),
        ("icon", 0x9A9A9A, 0xA39D96),
        ("accent", 0x0165DD, hx.RED),
        ("caution", 0xE3A83C, hx.AMBER),
    ]:
        old_line = f"            {field}: {rgb(old)},"
        if block.count(old_line) != 1:
            hx.fail(f"{rel}: default tokens: expected once: {old_line}")
        block = block.replace(old_line, f"            {field}: {rgb(new)},")
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")
    hx.edit(root, rel, [('ThemeKind::Charcoal => "Charcoal",', 'ThemeKind::Charcoal => "HORIX",')])


def drop_branded_translations_json(root: Path) -> int:
    n = 0
    for path in hx.files(root, ["crates/ui-egui/locales/*.json"]):
        if path.name.endswith("-formats.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        keep = {k: v for k, v in data.items() if not (isinstance(v, str) and hx.UPSTREAM_IN_TRANSLATION.search(v))}
        n += len(data) - len(keep)
        path.write_text(json.dumps(keep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return n


def web(root: Path) -> None:
    icons = HERE / "assets/app-icon"
    hx.edit(root, WEB, [
        ('<link rel="icon" href="data:,">', f'<link rel="icon" href="{hx.favicon_data_uri(icons)}">'),
        ("background: #1c1c1c;", "background: #141314;"),
        ('color: #b8b8b8; font: 15px/1.4 system-ui, -apple-system, "Segoe UI", sans-serif; pointer-events: none;\n    }',
         'color: #b8b8b8; font: 15px/1.4 system-ui, -apple-system, "Segoe UI", sans-serif; pointer-events: none;\n'
         '      background: #141314; flex-direction: column;\n    }\n'
         '    #horix_loading_text { margin-top: 18px; font-size: 13px; color: #9e9891; }' + hx.LOADER_CSS),
        ('<div id="lightcraft_loading">Loading LightCraft…</div>',
         f'<div id="lightcraft_loading">{hx.loader_html(APP_NAME, PRODUCT_LINE)}\n    <div id="horix_loading_text">Loading LightCraft…</div>\n  </div>'),
        ('const el = document.getElementById("lightcraft_loading");', 'const el = document.getElementById("horix_loading_text");'),
    ])


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1]).resolve()
    if not (root / "crates/ui-egui/src/links.rs").is_file() or not (root / "apps/lightcraft").is_dir():
        sys.exit(f"rebrand: {root} is not a LightCraft source tree")
    links(root)
    theme(root)
    web(root)
    hx.exe_version(root, "apps/lightcraft/build.rs")
    dropped = drop_branded_translations_json(root)
    n = hx.rename(root, CODE + [WEB], "LightCraft", APP_NAME)
    icons = hx.replace_icons(root, HERE / "assets/app-icon", "assets/app-icon")
    hx.check_no_upstream_brand(root, CODE + [WEB], allowed=["apps/lightcraft/src/editors.rs"])
    # HORIX AI masks in the browser (patches/50-horix-ai.diff: Object, Subject, Background).
    hx.install_home(root, HERE, (HERE / "VERSION").read_text(encoding="utf-8").strip())
    hx.apply_patches(root, HERE / "patches")
    print(f"rebrand: done ({n} name replacements, {icons} icons, {dropped} old-link translations dropped)")


if __name__ == "__main__":
    main()
