#!/usr/bin/env python3
"""Rebrand an unpacked VectorCraft source tree as Horix Vectors (Saber Group).

Usage: python3 -I apps/horix-vectors/rebrand.py <path-to-vectorcraft-source>

Every edit is an exact find/replace that must match, so an upstream change that moves the code
fails loudly here instead of silently shipping the old branding. Run it on a fresh copy of the
source; it is not meant to run twice on the same tree.

What it changes (UI only; licence files stay as the licences require):
  - "VectorCraft" -> "Horix Vectors" in every user-visible string and translation.
  - The ArtCraft Discord / website / GitHub links -> Saber Group (Facebook, website, WhatsApp) and
    the HORIX download page.
  - The HORIX falcon app icon (apps/horix-vectors/assets/app-icon/) everywhere the app shows or
    packages its icon.
  - HORIX colours: Horus Ink greys, Vision Amber for what is on, Horix Red for primary buttons;
    the darkest interface brightness is the default.
  - Web page: title, favicon, HORIX loading screen.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "horix-common"))
import horix_rebrand as hx  # noqa: E402

APP_NAME = "Horix Vectors"
PRODUCT_LINE = "THE VECTOR STUDIO"
CODE = ["crates/**/*.rs", "apps/**/*.rs", "crates/ui-egui/src/i18n/*.tsv"]
WEB = "apps/vectorcraft-web/index.html"


def links(root: Path) -> None:
    # Labels first: they contain the old product name, which rename() changes afterwards.
    hx.replace_everywhere(root, CODE, [
        ('"https://getartcraft.com/apps/vectorcraft"', f'"{hx.DOWNLOADS_PAGE}"'),
        ('"https://github.com/storytold/vectorcraft"', f'"{hx.WHATSAPP}"'),
        ('"https://discord.gg/artcraft"', f'"{hx.FACEBOOK}"'),
        ('"https://getartcraft.com"', f'"{hx.SABER_SITE}"'),
        ("VectorCraft on getartcraft.com", "Download the Desktop App (Windows / Mac)"),
        ("VectorCraft on GitHub", "Contact Us: Courses & Services"),
        ("Join Our Discord", "Saber Group Academy on Facebook"),
        ("ArtCraft Website", "Saber Group Academy Website"),
        ("ArtCraft website", "Saber Group Academy website"),
        ("Join our Discord", "Saber Group Academy"),
    ])
    edit = hx.edit
    edit(root, "crates/engine/src/cmd/help.rs", [
        ('    format!("{WEBSITE_URL}/apps/{APP_ID}")', f'    "{hx.DOWNLOADS_PAGE}".to_string()'),
        ('    format!("https://github.com/storytold/{APP_ID}")', f'    "{hx.WHATSAPP}".to_string()'),
        ("the ArtCraft community Discord", "Saber Group Academy on Facebook"),
        ("source code, issues and releases", "WhatsApp: courses and services"),
    ])
    # The Discord button becomes the Saber Group button, in Horix Red.
    edit(root, "crates/ui-egui/src/community.rs", [
        ("const DISCORD: Color32 = Color32::from_rgb(0x58, 0x65, 0xF2);", "const DISCORD: Color32 = Color32::from_rgb(0xD6, 0x3C, 0x32);"),
        ('egui::FontId::proportional(12.0), "Discord")', 'egui::FontId::proportional(12.0), "Saber Group")'),
        ('tl!("Join the ArtCraft community on Discord (discord.gg/artcraft)")', 'tl!("Saber Group Academy on Facebook")'),
        ('tl!("Source code on GitHub")', 'tl!("Contact us on WhatsApp")'),
        ('link(app, ui, "git-branch",', 'link(app, ui, "message-circle",'),
    ])
    edit(root, "crates/ui-egui/src/titlebar.rs", [('has("Discord")', 'has("Saber Group")')])
    edit(root, "crates/ui-egui/src/dialogs/about.rs", [
        ('"Part of ArtCraft. MIT OR Apache-2.0.', '"By Saber Group. Built on open-source software (MIT OR Apache-2.0).'),
    ])


def theme(root: Path) -> None:
    """The HORIX palette on VectorCraft's token system. The accent pair is (on / focus, filled
    button with white lettering): Vision Amber and Horix Red. The greys turn from cool slate to
    the warm Horus Ink and Graphite of the brand."""
    rel = "crates/ui-egui/src/theme.rs"
    a, r = hx.hexrgb(hx.AMBER), hx.hexrgb(hx.RED)
    hx.edit(root, rel, [
        ("(Accent::Coral, true) => (0xf06a52, 0xe8573f),", f"(Accent::Coral, true) => ({a}, {r}),"),
        ("(Accent::Coral, false) => (0xd9472f, 0xd14a33),", f"(Accent::Coral, false) => (0xb5651a, {r}),"),
        # Brightness::Dark, the base of every level.
        ("            app_bar: hex(0x0b0d12),\n            panel: hex(0x181b22),\n            panel_darker: hex(0x13161c),\n"
         "            input: hex(0x0f1116),\n            input_border: hex(0x2c323e),\n            border: hex(0x06070a),\n"
         "            divider: hex(0x232832),\n            text: hex(0xdfe4ec),\n            text_dim: hex(0x969faf),\n"
         "            text_disabled: hex(0x5a6271),\n            icon: hex(0xc9d0dc),\n            hover: hex(0x262b35),\n"
         "            tool_active: hex(0x2f3541),\n            accent: hex(0xf06a52),\n            accent_strong: hex(0xe8573f),\n"
         "            row_selected: hex(0x3a2a2c),\n            pasteboard: hex(0x101217),\n            ruler: hex(0x13161c),\n"
         "            ruler_tick: hex(0x6f788a),",
         f"            app_bar: hex(0x0e0d0e),\n            panel: hex({hx.hexrgb(hx.INK)}),\n            panel_darker: hex(0x100f10),\n"
         "            input: hex(0x0c0b0c),\n            input_border: hex(0x3a3535),\n            border: hex(0x060506),\n"
         f"            divider: hex({hx.hexrgb(hx.GRAPHITE)}),\n            text: hex({hx.hexrgb(hx.IVORY)}),\n            text_dim: hex(0x9e9891),\n"
         "            text_disabled: hex(0x5f5a56),\n            icon: hex(0xd2ccc4),\n            hover: hex(0x2a2727),\n"
         f"            tool_active: hex(0x353131),\n            accent: hex({a}),\n            accent_strong: hex({r}),\n"
         "            row_selected: hex(0x3b2a1c),\n            pasteboard: hex(0x0b0a0b),\n            ruler: hex(0x100f10),\n"
         "            ruler_tick: hex(0x7a736d),"),
        ("            flyout_active: hex(0xff8a74),", "            flyout_active: hex(0xf2b36e),"),
        ("            measure_bg: Color32::from_rgba_unmultiplied(24, 27, 34, 235),\n            button: hex(0x282d37),",
         "            measure_bg: Color32::from_rgba_unmultiplied(20, 19, 20, 235),\n            button: hex(0x2a2727),"),
        ("            tab_strip: hex(0x0f1116),\n            button_border: hex(0x4a5363),",
         "            tab_strip: hex(0x0c0b0c),\n            button_border: hex(0x4f4848),"),
        # Medium Dark (Charcoal upstream): Graphite panels.
        ("                app_bar: hex(0x1b1f27),\n                panel: hex(0x272c36),\n                panel_darker: hex(0x21262f),\n"
         "                tab_strip: hex(0x1e222a),\n                input: hex(0x1a1e26),\n                input_border: hex(0x3a414e),\n"
         "                border: hex(0x11141a),\n                divider: hex(0x323946),\n                text: hex(0xe4e9f1),\n"
         "                text_dim: hex(0x99a2b2),\n                text_disabled: hex(0x626b7a),\n                icon: hex(0xccd3de),\n"
         "                hover: hex(0x353c49),\n                tool_active: hex(0x3d4553),\n                row_selected: hex(0x4a3236),\n"
         "                pasteboard: hex(0x1e222a),\n                ruler: hex(0x21262f),\n                ruler_tick: hex(0x7c8597),\n"
         "                measure_bg: Color32::from_rgba_unmultiplied(39, 44, 54, 235),\n                button: hex(0x39404d),\n"
         "                button_border: hex(0x5a6476),",
         "                app_bar: hex(0x1a1818),\n                panel: hex(0x2a2727),\n                panel_darker: hex(0x221f1f),\n"
         "                tab_strip: hex(0x1d1b1b),\n                input: hex(0x191717),\n                input_border: hex(0x464040),\n"
         "                border: hex(0x111010),\n                divider: hex(0x383333),\n                text: hex(0xf3efe8),\n"
         "                text_dim: hex(0xa39d96),\n                text_disabled: hex(0x6a6460),\n                icon: hex(0xd6d0c8),\n"
         "                hover: hex(0x3a3535),\n                tool_active: hex(0x433d3d),\n                row_selected: hex(0x4a3420),\n"
         "                pasteboard: hex(0x1d1b1b),\n                ruler: hex(0x221f1f),\n                ruler_tick: hex(0x857e77),\n"
         "                measure_bg: Color32::from_rgba_unmultiplied(42, 39, 39, 235),\n                button: hex(0x3d3838),\n"
         "                button_border: hex(0x625a5a),"),
        ("Coral, the\n/// default, is the app icon's.", "Coral (HORIX's Vision Amber\n/// and Horix Red in this build), the default, is the app icon's."),
    ])
    # Darkest level by default, as in HORIX.
    hx.edit(root, "crates/ui-egui/src/state.rs", [("            brightness: Brightness::MediumDark,", "            brightness: Brightness::Dark,")])
    hx.edit(root, "crates/engine/src/lib.rs", [('            ui_brightness: s("mediumDark"),', '            ui_brightness: s("dark"),')])
    hx.edit(root, "crates/ui-egui/src/theme.rs", [("    Dark,\n    #[default]\n    MediumDark,", "    #[default]\n    Dark,\n    MediumDark,")])
    hx.replace_everywhere(root, ["crates/engine/src/cmd/prefscmds.rs"], [('("coral", "Coral")', '("coral", "HORIX")')])


def web(root: Path) -> None:
    icons = HERE / "assets/app-icon"
    hx.edit(root, WEB, [
        ('<meta name="theme-color" content="#262626">', '<meta name="theme-color" content="#141314">'),
        ("<title>VectorCraft</title>", f'<title>{APP_NAME}</title>\n  <link rel="icon" href="{hx.favicon_data_uri(icons)}">'),
        ("background: #262626;", "background: #141314;"),
        ("color: #b8b8b8; font: 14px system-ui, sans-serif; pointer-events: none; }",
         "color: #b8b8b8; font: 14px system-ui, sans-serif; pointer-events: none; background: #141314; }\n"
         "    #horix_loading_text { margin-top: 18px; font-size: 13px; color: #9e9891; }" + hx.LOADER_CSS),
        ('<div id="vectorcraft_loading">Loading VectorCraft&hellip;</div>',
         f'<div id="vectorcraft_loading">{hx.loader_html(APP_NAME, PRODUCT_LINE)}\n    <div id="horix_loading_text">Loading VectorCraft&hellip;</div>\n  </div>'),
    ])
    # The app writes the translated loading text into the page: into the status line, so the logo
    # stays; the whole loader is still removed once the app runs.
    hx.edit(root, "apps/vectorcraft-web/src/web.rs", [
        ("    if let Some(el) = element(LOADING_ID) {\n        el.set_text_content(",
         '    if let Some(el) = element("horix_loading_text") {\n        el.set_text_content('),
    ])


def web_prefs(root: Path) -> None:
    """Preferences in the browser: upstream's web build keeps none, so Brightness (and every other
    preference) went back to the default on the next visit. They now live in localStorage, read at
    start and written whenever they change, as the desktop app keeps its preferences file."""
    hx.edit(root, "apps/vectorcraft-web/Cargo.toml", [("log = { workspace = true }\n", "log = { workspace = true }\nserde_json = { workspace = true }\n")])
    hx.edit(root, "Cargo.lock", [(' "rfd",\n "vectorcraft-engine",\n "vectorcraft-format",\n "vectorcraft-text",\n "vectorcraft-ui-egui",\n "wasm-bindgen",',
                                  ' "rfd",\n "serde_json",\n "vectorcraft-engine",\n "vectorcraft-format",\n "vectorcraft-text",\n "vectorcraft-ui-egui",\n "wasm-bindgen",')])
    hx.edit(root, "apps/vectorcraft-web/src/web.rs", [
        ("                    None => VectorcraftApp::new(Session::new(), services),\n",
         "                    None => {\n                        let mut app = VectorcraftApp::new(Session::new(), services);\n"
         "                        restore_prefs(&mut app);\n                        app\n                    }\n"),
        ("                Ok(Box::new(WebShell { app: Some(app), host, canvas: page, loss }))",
         "                let saved_prefs = app.session.prefs.clone();\n"
         "                Ok(Box::new(WebShell { app: Some(app), host, canvas: page, loss, saved_prefs }))"),
        ("    canvas: web_sys::HtmlCanvasElement,\n    loss: GraphicsLoss,\n}\n",
         "    canvas: web_sys::HtmlCanvasElement,\n    loss: GraphicsLoss,\n"
         "    /// The preferences last written to the browser's storage.\n    saved_prefs: vectorcraft_engine::Prefs,\n}\n"),
        ("        app.logic(ctx);\n    }\n",
         "        app.logic(ctx);\n"
         "        if app.session.prefs != self.saved_prefs {\n"
         "            self.saved_prefs = app.session.prefs.clone();\n"
         "            if let Ok(s) = local_storage() {\n"
         "                // Best effort, as the desktop preferences file: a full or blocked storage keeps the old copy.\n"
         "                let _ = s.set_item(PREFS_KEY, &app.session.prefs.to_json().to_string());\n"
         "            }\n        }\n    }\n"),
        ('const RECOVERY_PREFIX: &str = "vectorcraft-recovery/";\n',
         'const RECOVERY_PREFIX: &str = "vectorcraft-recovery/";\n'
         'const PREFS_KEY: &str = "horix-vectors/prefs";\n\n'
         "/// The preferences saved by an earlier visit, applied the way the desktop app applies its file.\n"
         "fn restore_prefs(app: &mut VectorcraftApp) {\n"
         "    let saved = local_storage().ok().and_then(|s| s.get_item(PREFS_KEY).ok().flatten());\n"
         "    if let Some(prefs) = saved.and_then(|t| serde_json::from_str::<serde_json::Value>(&t).ok()) {\n"
         "        app.ui.engine_prefs = prefs;\n"
         "        vectorcraft_ui_egui::prefs_dialog::restore(app);\n"
         "    }\n}\n"),
    ])


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1]).resolve()
    if not (root / "crates/ui-egui/src/community.rs").is_file():
        sys.exit(f"rebrand: {root} is not a VectorCraft source tree")
    links(root)
    theme(root)
    web(root)
    web_prefs(root)
    hx.exe_version(root, "apps/vectorcraft/build.rs")
    dropped = hx.drop_branded_translations_tsv(root, "crates/ui-egui/src/i18n/*.tsv")
    n = hx.rename(root, CODE + [WEB], "VectorCraft", APP_NAME)
    icons = hx.replace_icons(root, HERE / "assets/app-icon", "assets/app-icon")
    hx.check_no_upstream_brand(root, CODE + [WEB], allowed=["crates/text/"])
    print(f"rebrand: done ({n} name replacements, {icons} icons, {dropped} old-link translations dropped)")


if __name__ == "__main__":
    main()
