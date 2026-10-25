#!/usr/bin/env python3
"""Rebrand an unpacked DesignCraft source tree as Horix Layout (Saber Group).

Usage: python3 -I apps/horix-layout/rebrand.py <path-to-designcraft-source>

Every edit is an exact find/replace that must match, so an upstream change that moves the code
fails loudly here instead of silently shipping the old branding. Run it on a fresh copy of the
source; it is not meant to run twice on the same tree.

What it changes (UI only; licence files stay as the licences require):
  - "DesignCraft" -> "Horix Layout" in every user-visible string and translation.
  - The ArtCraft Discord / website / GitHub links -> Saber Group (Facebook, website, WhatsApp) and
    the HORIX download page; the About window's other apps are the HORIX family.
  - The HORIX falcon in place of the ArtCraft mark (About, start screen), and the HORIX app icon
    (apps/horix-layout/assets/app-icon/) everywhere the app shows or packages its icon.
  - HORIX colours: Horus Ink greys, Vision Amber for what is on, Horix Red for primary buttons;
    the darkest interface brightness is the default.
  - Web page: title, favicon, HORIX loading screen.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "horix-common"))
import horix_rebrand as hx  # noqa: E402

APP_NAME = "Horix Layout"
PRODUCT_LINE = "THE PAGE LAYOUT STUDIO"
CODE = ["crates/**/*.rs", "apps/**/*.rs"]
WEB = "apps/designcraft-web/index.html"
FACEBOOK_SHORT = "facebook.com/SABERGROUP.Courses"
# The HORIX family on the About window: (web address, name, what it is). The descriptions are
# upstream's own translated ones.
FAMILY = [
    ("horix.live", "HORIX", "image editing"),
    ("vectors.horix.live", "Horix Vectors", "vector illustration"),
    ("light.horix.live", "Horix Light", "photo library and raw development"),
]


def links(root: Path) -> None:
    hx.edit(root, "crates/engine/src/links.rs", [
        ('pub const DISCORD: &str = "https://discord.gg/artcraft";', f'pub const DISCORD: &str = "{hx.FACEBOOK}";'),
        ('pub const WEBSITE: &str = "https://getartcraft.com";', f'pub const WEBSITE: &str = "{hx.SABER_SITE}";'),
        ('pub const APP_PAGE: &str = "https://getartcraft.com/apps/designcraft";', f'pub const APP_PAGE: &str = "{hx.DOWNLOADS_PAGE}";'),
        ('pub const GITHUB: &str = "https://github.com/storytold/designcraft";', f'pub const GITHUB: &str = "{hx.WHATSAPP}";'),
        ('pub const ISSUES: &str = "https://github.com/storytold/designcraft/issues";', f'pub const ISSUES: &str = "{hx.WHATSAPP}";'),
        # The links are Saber Group's now, not built from the app's slug.
        ('        assert!(APP_PAGE.ends_with(&format!("/apps/{APP}")));\n        assert!(GITHUB.ends_with(&format!("/storytold/{APP}")));\n        assert!(ISSUES.starts_with(GITHUB));\n',
         '        assert!(APP_PAGE.starts_with("https://"));\n        assert!(ISSUES.starts_with(GITHUB));\n'),
    ])
    # Labels, in the UI, its tests and every translation table alike (the English text is the
    # key). Before rename(), which changes the product name in them.
    hx.replace_everywhere(root, CODE, [
        ("discord.gg/artcraft — help, feedback and show-and-tell", f"{FACEBOOK_SHORT} — courses, help and news"),
        ("Join the ArtCraft Discord", "Saber Group Academy on Facebook"),
        ("Join the ArtCraft community", "Saber Group Academy"),
        ("Join our Discord", "Follow us on Facebook"),
        ("ArtCraft Website", "Saber Group Academy Website"),
        ("ArtCraft App Page", "Download the Desktop App"),
        ("DesignCraft Website", "Download the Desktop App (Windows / Mac)"),
        ("DesignCraft on GitHub", "Contact Us on WhatsApp"),
        ("Part of the ArtCraft suite of open creative tools.", "By Saber Group. Built on open-source software."),
        ("More ArtCraft apps", "The HORIX family"),
        ('("DesignCraft page", "help.appPage"), ("GitHub", "help.github"), ("getartcraft.com", "help.website")',
         '("Desktop app", "help.appPage"), ("WhatsApp", "help.github"), ("Saber Group Academy", "help.website")'),
        ('("DesignCraft page", "appPage"), ("GitHub", "github"), ("getartcraft.com", "website"), ("Report an issue", "issues")',
         '("Desktop app", "appPage"), ("WhatsApp", "github"), ("Saber Group Academy", "website")'),
        ("opens https://discord.gg/artcraft in the browser", f"opens {hx.FACEBOOK} in the browser"),
        ("opens https://getartcraft.com/apps/designcraft", f"opens {hx.DOWNLOADS_PAGE}"),
        ("opens https://github.com/storytold/designcraft", "opens Saber Group's WhatsApp"),
        ('opens https://getartcraft.com"', f'opens {hx.SABER_SITE}"'),
        ("opens https://getartcraft.com/apps/{app} (e.g. photocraft)", "opens the HORIX download page"),
    ])
    translations(root)
    hx.edit(root, "crates/ui-egui/src/about.rs", [
        # The Discord button becomes the Saber Group button, in Horix Red.
        ("pub const DISCORD: Color32 = Color32::from_rgb(0x58, 0x65, 0xf2);", "pub const DISCORD: Color32 = Color32::from_rgb(0xd6, 0x3c, 0x32);"),
        ("pub const BRAND: Color32 = Color32::from_rgb(0x4e, 0x7b, 0xfb);", "pub const BRAND: Color32 = Color32::from_rgb(0xea, 0x99, 0x3f);"),
        # The HORIX falcon (apps/sg-ps/assets/horix-symbol.svg) in place of the ArtCraft mark,
        # centred in a square of its width.
        (f'const MARK_PATH: &str = "{upstream_mark(root)}";', f'const MARK_PATH: &str = "{falcon_path()}";'),
        ("        let k = px as f64 / 136.34;\n        rc.set_transform(kurbo::Affine::scale(k) * kurbo::Affine::translate((10.0, 19.42)));",
         "        let k = px as f64 / 1051.0;\n        rc.set_transform(kurbo::Affine::scale(k) * kurbo::Affine::translate((-345.0, -167.0)));"),
        (sibling_block(root), "pub const SIBLINGS: &[(&str, &str, &str)] = &[\n"
         + "".join(f'    ("{site}", "{name}", "{what}"),\n' for site, name, what in FAMILY) + "];\n"),
        ('                    let url = format!("{}/apps/{slug}", links::WEBSITE);', '                    let url = format!("https://{slug}/");'),
        ("    let fill = if resp.hovered() { Color32::from_rgb(0x47, 0x52, 0xc4) } else { DISCORD };",
         "    let fill = if resp.hovered() { Color32::from_rgb(0xb0, 0x2e, 0x25) } else { DISCORD };"),
    ])
    hx.edit(root, "crates/ui-egui/src/chrome.rs", [
        ('                            // Always one click away: the ArtCraft community Discord.\n'
         '                            if crate::about::discord_button(ui, "Discord", vec2(78.0, 22.0)) {',
         '                            // Always one click away: Saber Group Academy.\n'
         '                            if crate::about::discord_button(ui, "Saber Group", vec2(112.0, 22.0)) {'),
    ])
    hx.edit(root, "apps/designcraft/build.rs", [('.set("CompanyName", "Learning Machines LLC")', '.set("CompanyName", "Saber Group Academy")')])


TAINTED = re.compile(r"ArtCraft|Discord|discord|getartcraft|GitHub")
STR = r'"(?:[^"\\]|\\.)*"'
# Arabic for the labels this build wrote (the app's interface is translated into Arabic).
ARABIC = [
    ("Saber Group Academy", "أكاديمية صابر جروب"),
    ("Saber Group Academy on Facebook", "أكاديمية صابر جروب على فيسبوك"),
    ("Saber Group Academy on Facebook…", "أكاديمية صابر جروب على فيسبوك…"),
    ("Follow us on Facebook", "تابعنا على فيسبوك"),
    (f"{FACEBOOK_SHORT} — courses, help and news", f"{FACEBOOK_SHORT} — كورسات ومساعدة وأخبار"),
    ("Saber Group Academy Website", "موقع أكاديمية صابر جروب"),
    ("Saber Group Academy Website…", "موقع أكاديمية صابر جروب…"),
    ("Download the Desktop App", "حمّل نسخة الديسكتوب"),
    ("Download the Desktop App…", "حمّل نسخة الديسكتوب…"),
    ("Download the Desktop App (Windows / Mac)", "حمّل نسخة الديسكتوب (ويندوز / ماك)"),
    ("Download the Desktop App (Windows / Mac)…", "حمّل نسخة الديسكتوب (ويندوز / ماك)…"),
    ("Contact Us on WhatsApp", "كلّمنا على واتساب"),
    ("Contact Us on WhatsApp…", "كلّمنا على واتساب…"),
    ("By Saber Group. Built on open-source software.", "من صابر جروب. مبني على برمجيات مفتوحة المصدر."),
    ("The HORIX family", "عائلة HORIX"),
    ("Desktop app", "نسخة الديسكتوب"),
    ("WhatsApp", "واتساب"),
]


def translations(root: Path) -> None:
    """The labels this build replaced keep upstream's translations of the old wording (ArtCraft,
    Discord, GitHub, the app's website): the language catalogs drop those entries (the labels show
    the new English wording), the shared table keeps them with the English text in every column,
    and Arabic gets its own wording of the new labels."""
    new_keys = {k for k, _ in ARABIC}
    stale = lambda key, text: key[1:-1] in new_keys or bool(TAINTED.search(text))
    pair = re.compile(rf"[ \t]*\(\s*({STR})\s*,\s*({STR})\s*,?\s*\),[ \t]*\n")
    for path in sorted((root / "crates/ui-egui/src/i18n").glob("*.rs")):
        text = path.read_text(encoding="utf-8")
        text = pair.sub(lambda m: "" if stale(m.group(1), m.group(2)) else m.group(0), text)
        path.write_text(text, encoding="utf-8")
    shared = root / "crates/ui-egui/src/i18n.rs"
    text = shared.read_text(encoding="utf-8")
    entry = re.compile(rf"\(\s*({STR})\s*,\s*\[((?:\s*{STR}\s*,?){{5}})\s*\]\s*,?\s*\)")
    text = entry.sub(lambda m: f"({m.group(1)}, [{', '.join([m.group(1)] * 5)}])" if stale(m.group(1), m.group(2)) else m.group(0), text)
    shared.write_text(text, encoding="utf-8")
    ar = root / "crates/ui-egui/src/i18n/ar.rs"
    text = ar.read_text(encoding="utf-8")
    end = text.index("\n];", text.index("const TABLE")) + 1
    lines = "".join(f'    ("{k}", "{v}"),\n' for k, v in ARABIC)
    ar.write_text(text[:end] + lines + text[end:], encoding="utf-8")


def upstream_mark(root: Path) -> str:
    text = (root / "crates/ui-egui/src/about.rs").read_text(encoding="utf-8")
    m = re.search(r'const MARK_PATH: &str = "([^"]+)";', text)
    if not m:
        hx.fail("crates/ui-egui/src/about.rs: MARK_PATH not found")
    return m.group(1)


def falcon_path() -> str:
    """The falcon's ivory shapes as one SVG path (its eye is drawn over them in the logo)."""
    svg = (hx.REPO / "apps/sg-ps/assets/horix-symbol.svg").read_text(encoding="utf-8")
    paths = re.findall(r'<path fill="#F3EFE8" d="([^"]+)"', svg)
    if len(paths) != 2:
        hx.fail("horix-symbol.svg: expected the falcon's two ivory paths")
    return " ".join(paths)


def sibling_block(root: Path) -> str:
    text = (root / "crates/ui-egui/src/about.rs").read_text(encoding="utf-8")
    start = text.index("pub const SIBLINGS: &[(&str, &str, &str)] = &[\n")
    return text[start:text.index("];\n", start) + 3]


def theme(root: Path) -> None:
    """The HORIX palette on DesignCraft's tokens: the Dark level (the base the others start from)
    turns from neutral grey to Horus Ink and Graphite, the accent pair is Vision Amber (on, focus)
    and Horix Red (filled buttons), and Dark is the default."""
    a, r = hx.hexrgb(hx.AMBER), hx.hexrgb(hx.RED)
    rel = "crates/ui-egui/src/theme.rs"
    hx.edit(root, rel, [
        ("            app_bar: hex(0x262626),\n            panel: hex(0x323232),\n            panel_darker: hex(0x282828),\n"
         "            input: hex(0x1f1f1f),\n            input_border: hex(0x4a4a4a),\n            divider: hex(0x1e1e1e),\n"
         "            text: hex(0xd8d8d8),\n            text_strong: hex(0xf2f2f2),\n            text_dim: hex(0xa3a3a3),\n"
         "            text_disabled: hex(0x6a6a6a),\n            icon: hex(0xc8c8c8),\n            hover: hex(0x424242),\n"
         "            tool_active: hex(0x1b1b1b),\n            accent: hex(0x378ef0),\n            accent_strong: hex(0x1473e6),\n"
         "            row_selected: hex(0x2d4f7c),\n            pasteboard: hex(0x232323),\n            ruler: hex(0x2e2e2e),\n"
         "            ruler_tick: hex(0x9a9a9a),\n            tab_inactive: hex(0x262626),\n            button: hex(0x404040),\n",
         "            app_bar: hex(0x0e0d0e),\n            panel: hex(0x1d1b1c),\n            panel_darker: hex(0x161415),\n"
         "            input: hex(0x0f0e0f),\n            input_border: hex(0x423c3c),\n            divider: hex(0x0e0d0e),\n"
         f"            text: hex(0xe6e1da),\n            text_strong: hex({hx.hexrgb(hx.IVORY)}),\n            text_dim: hex(0x9e9891),\n"
         "            text_disabled: hex(0x605a56),\n            icon: hex(0xd2ccc4),\n            hover: hex(0x353131),\n"
         f"            tool_active: hex(0x0c0b0c),\n            accent: hex({a}),\n            accent_strong: hex({r}),\n"
         f"            row_selected: hex(0x4a3420),\n            pasteboard: hex({hx.hexrgb(hx.INK)}),\n            ruler: hex(0x1a1818),\n"
         f"            ruler_tick: hex(0x857e77),\n            tab_inactive: hex(0x161415),\n            button: hex({hx.hexrgb(hx.GRAPHITE)}),\n"),
    ])
    # Darkest level by default, as in HORIX.
    hx.edit(root, "crates/ui-egui/src/lib.rs", [("            brightness: theme::Brightness::MediumDark,", "            brightness: theme::Brightness::Dark,")])


def arabic_on_the_web(root: Path) -> None:
    """The web build embeds craft-fonts' Arabic faces too (upstream's embeds only the Japanese UI
    face): the browser has no system fonts to fall back to, so Arabic text in a document would
    show as boxes. The Chinese, Japanese and Korean faces stay out (the wasm's size)."""
    hx.edit(root, "crates/fonts/build.rs", [
        ('        if wasm && !(*family == "BIZ UDPGothic" && *style == "Regular") {',
         '        if wasm && !(*family == "BIZ UDPGothic" && *style == "Regular") && !scripts.split(\',\').any(|s| s.trim() == "Arab") {'),
    ])


def web(root: Path) -> None:
    icons = HERE / "assets/app-icon"
    hx.edit(root, WEB, [
        ("<title>DesignCraft</title>", f'<title>{APP_NAME}</title>\n  <link rel="icon" href="{hx.favicon_data_uri(icons)}">\n  <meta name="theme-color" content="#141314">'),
        ("background: #262626;", "background: #141314;"),
        ("      color: #b8b8b8; font: 14px system-ui, sans-serif; pointer-events: none; }",
         "      color: #b8b8b8; font: 14px system-ui, sans-serif; pointer-events: none; background: #141314; }\n"
         "    #horix_loading_text { margin-top: 18px; font-size: 13px; color: #9e9891; }" + hx.LOADER_CSS),
        ('<div id="designcraft_loading">Loading DesignCraft&hellip;</div>',
         f'<div id="designcraft_loading">{hx.loader_html(APP_NAME, PRODUCT_LINE)}\n    <div id="horix_loading_text">Loading DesignCraft&hellip;</div>\n  </div>'),
    ])


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1]).resolve()
    if not (root / "crates/engine/src/links.rs").is_file() or not (root / "apps/designcraft").is_dir():
        sys.exit(f"rebrand: {root} is not a DesignCraft source tree")
    links(root)
    theme(root)
    arabic_on_the_web(root)
    web(root)
    hx.exe_version(root, "apps/designcraft/build.rs")
    n = hx.rename(root, CODE + [WEB], "DesignCraft", APP_NAME)
    icons = hx.replace_icons(root, HERE / "assets/app-icon", "assets/app-icon")
    hx.check_no_upstream_brand(root, CODE + [WEB], allowed=[])
    if (HERE / "patches").is_dir():
        hx.apply_patches(root, HERE / "patches")
    print(f"rebrand: done ({n} name replacements, {icons} icons)")


if __name__ == "__main__":
    main()
