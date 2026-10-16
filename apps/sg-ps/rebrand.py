#!/usr/bin/env python3
"""Rebrand an unpacked PhotoCraft source tree as HORIX (Saber Group).

Usage: python3 -I rebrand.py <path-to-photocraft-source>

Every edit is an exact find/replace that must match, so an upstream change that moves the code
fails loudly here instead of silently shipping the old branding. Re-run on a fresh copy of the
source; the script is not meant to run twice on the same tree.

What it changes (UI only; licence files are kept as the licences require):
  - App name "PhotoCraft" -> "HORIX" in every user-visible string and translation.
  - Removes the ArtCraft Discord, website and GitHub links; Help/start-screen links go to Saber.
  - HORIX logo (apps/sg-ps/brand/) on the start screen, About dialog, loading screen and browser tab.
  - HORIX colour theme (Horus Ink, Graphite, Horix Red, Vision Amber) as the default theme.
  - Barlow Condensed ExtraBold as the display face for headlines (brand guide: condensed grotesk).
  - Full tool options bar in every theme (upstream shows it only in the Pro themes).
  - Select Subject: spatial prior around the salient mass (see segeval/), fewer leaks into busy
    backgrounds.
  - Web build output renamed to sg-ps-*.js / sg-ps-*_bg.wasm.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "HORIX"
SABER_SITE = "https://sabergroupacademy.com"
APP_SITE = "https://horix.live"
DOWNLOADS_PAGE = "https://horix.si/"
FACEBOOK = "https://www.facebook.com/SABERGROUP.Courses/"
# WhatsApp with a ready message: "Hello, I am coming from HORIX and want to know about the courses and services".
WHATSAPP = ("https://wa.me/201103221873?text=%D9%85%D8%B1%D8%AD%D8%A8%D9%8B%D8%A7%D8%8C%20%D8%AC%D8%A7%D9%8A%20%D9%85%D9%86%20"
            "HORIX%20%D9%88%D8%B9%D8%A7%D9%8A%D8%B2%20%D8%A3%D8%B9%D8%B1%D9%81%20%D8%B9%D9%86%20%D8%A7%D9%84%D9%83%D9%88%D8%B1%D8%B3%D8%A7%D8%AA%20"
            "%D9%88%D8%A7%D9%84%D8%AE%D8%AF%D9%85%D8%A7%D8%AA")
HERE = Path(__file__).resolve().parent


def edit(root: Path, rel: str, pairs: list[tuple[str, str]]) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            sys.exit(f"rebrand: {rel}: expected text not found:\n{old}")
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def remove_block(root: Path, rel: str, start: str, end: str) -> None:
    """Remove from the line containing `start` through the first following line equal to `end`."""
    path = root / rel
    lines = path.read_text(encoding="utf-8").split("\n")
    i = next((k for k, l in enumerate(lines) if start in l), None)
    if i is None:
        sys.exit(f"rebrand: {rel}: block start not found: {start}")
    j = next((k for k in range(i, len(lines)) if lines[k] == end), None)
    if j is None:
        sys.exit(f"rebrand: {rel}: block end not found after {start}")
    del lines[i : j + 1]
    path.write_text("\n".join(lines), encoding="utf-8")


DESKTOP_BUTTONS = """/// HORIX: Lucide "monitor-down" (ISC), white, tinted where it is drawn.
const DOWNLOAD_ICON: &[u8] = br##"<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 13V7"/><path d="m15 10-3 3-3-3"/><rect width="20" height="14" x="2" y="3" rx="2"/><path d="M12 17v4"/><path d="M8 21h8"/></svg>"##;

fn download_icon(size: f32, color: egui::Color32) -> egui::Image<'static> {
    egui::Image::from_bytes("bytes://horix-download.svg", DOWNLOAD_ICON).fit_to_exact_size(egui::vec2(size, size)).tint(color)
}

/// HORIX (web only): "Windows and Mac versions" in the title bar, to the download page.
pub fn desktop_title_button(app: &mut PhotocraftApp, ui: &mut egui::Ui) {
    if !cfg!(target_arch = "wasm32") {
        return;
    }
    let t = crate::theme::Tokens::get(ui.ctx());
    let (icon, text_h, pad, gap) = (14.0, 13.0, 9.0, 6.0);
    let text_w = text_h * DL_SHORT_ASPECT;
    let (rect, r) = ui.allocate_exact_size(egui::vec2(pad + icon + gap + text_w + pad, 24.0), egui::Sense::click());
    let r = r.on_hover_cursor(egui::CursorIcon::PointingHand).on_hover_text(DOWNLOAD);
    let color = if r.hovered() { t.accent } else { t.text_dim };
    if r.hovered() {
        ui.painter().rect_filled(rect, t.radius_sm, t.hover);
    }
    ui.painter().rect_stroke(rect, t.radius_sm, egui::Stroke::new(1.0, t.field_border), egui::StrokeKind::Inside);
    let y = rect.center().y;
    download_icon(icon, color).paint_at(ui, egui::Rect::from_min_size(egui::pos2(rect.left() + pad, y - icon / 2.0), egui::vec2(icon, icon)));
    arabic("bytes://dl-short.svg", include_bytes!("dl_short.svg"), DL_SHORT_ASPECT, text_h, color)
        .paint_at(ui, egui::Rect::from_min_size(egui::pos2(rect.left() + pad + icon + gap, y - text_h / 2.0), egui::vec2(text_w, text_h)));
    if r.clicked() {
        open(app, ui.ctx(), DOWNLOAD);
    }
}

/// HORIX (web only): the start screen's way to the Windows / macOS apps.
pub fn desktop_cta(app: &mut PhotocraftApp, ui: &mut egui::Ui) {
    if !cfg!(target_arch = "wasm32") {
        return;
    }
    let t = crate::theme::Tokens::get(ui.ctx());
    ui.add_space(14.0);
    let (icon, text_h, gap) = (16.0, 16.0, 8.0);
    let text_w = text_h * DL_CTA_ASPECT;
    let (rect, r) = ui.allocate_exact_size(egui::vec2(text_w + icon + gap + 40.0, 36.0), egui::Sense::click());
    let r = r.on_hover_cursor(egui::CursorIcon::PointingHand).on_hover_text(DOWNLOAD);
    let (fill, stroke) = if r.hovered() { (t.accent_soft, t.accent) } else { (egui::Color32::TRANSPARENT, t.accent_border) };
    ui.painter().rect_filled(rect, t.radius, fill);
    ui.painter().rect_stroke(rect, t.radius, egui::Stroke::new(1.0, stroke), egui::StrokeKind::Inside);
    let x = rect.center().x - (icon + gap + text_w) / 2.0;
    let y = rect.center().y;
    download_icon(icon, t.accent).paint_at(ui, egui::Rect::from_min_size(egui::pos2(x, y - icon / 2.0), egui::vec2(icon, icon)));
    arabic("bytes://dl-cta.svg", include_bytes!("dl_cta.svg"), DL_CTA_ASPECT, text_h, t.text)
        .paint_at(ui, egui::Rect::from_min_size(egui::pos2(x + icon + gap, y - text_h / 2.0), egui::vec2(text_w, text_h)));
    if r.clicked() {
        open(app, ui.ctx(), DOWNLOAD);
    }
}

"""

def links(root: Path) -> None:
    edit(root, "crates/ui-egui/src/links.rs", [
        ('pub const DISCORD: &str = "https://discord.gg/artcraft";', f'pub const DISCORD: &str = "{FACEBOOK}";\npub const CONTACT: &str = "{WHATSAPP}";\npub const DOWNLOAD: &str = "{DOWNLOADS_PAGE}";'),
        ('pub const ARTCRAFT_WEBSITE: &str = "https://getartcraft.com";', f'pub const ARTCRAFT_WEBSITE: &str = "{SABER_SITE}";'),
        ('pub const APP_PAGE: &str = "https://getartcraft.com/apps/photocraft";', f'pub const APP_PAGE: &str = "{APP_SITE}";'),
        ('pub const GITHUB: &str = "https://github.com/storytold/photocraft";', f'pub const GITHUB: &str = "{SABER_SITE}";'),
        ('pub const ISSUES: &str = "https://github.com/storytold/photocraft/issues";', f'pub const ISSUES: &str = "{SABER_SITE}";'),
        (
            '&[("help.discord", DISCORD), ("help.website", APP_PAGE), ("help.artcraftWebsite", ARTCRAFT_WEBSITE), ("help.github", GITHUB), ("help.reportIssue", ISSUES)];',
            '&[("help.discord", DISCORD), ("help.contact", CONTACT), ("help.download", DOWNLOAD), ("help.website", APP_PAGE)];',
        ),
        ('tl!("Join us on Discord")', 'tl!("Saber Group Academy")'),
        (
            'let links = [(tl!("PhotoCraft website"), APP_PAGE), (tl!("GitHub"), GITHUB), (tl!("ArtCraft"), ARTCRAFT_WEBSITE)];',
            f'let links = [(tl!("{APP_NAME}"), APP_PAGE), (tl!("sabergroupacademy.com"), ARTCRAFT_WEBSITE)];',
        ),
        ("+ 2.0 * ui.painter().layout_no_wrap(sep.into()", "+ (links.len() - 1) as f32 * ui.painter().layout_no_wrap(sep.into()"),
    ])


def menus(root: Path) -> None:
    edit(root, "crates/ui-egui/src/menus.rs", [
        ('("help.discord", "Join the ArtCraft Discord…", &["Help"], None),', '("help.discord", "Saber Group Academy on Facebook", &["Help"], None),\n    ("help.contact", "Contact Us: Courses & Services…", &["Help"], None),\n    ("help.download", "Download the Desktop App (Windows / Mac)…", &["Help"], None),'),
        ('("help.website", "PhotoCraft Website", &["Help"], None),', f'("help.website", "{APP_NAME} Website", &["Help"], None),'),
        # The legacy Studio shell hides or simplifies several panels.  Keep its enum for loading
        # old preference files, but do not expose it as a user-selectable theme.
        ('    ("window.theme.studio", "Studio Theme", &["Window", "Theme"], None),\n', ""),
        ('    ("help.artcraftWebsite", "ArtCraft Website", &["Help"], None),\n', ""),
        ('    ("help.github", "PhotoCraft on GitHub", &["Help"], None),\n', ""),
        ('    ("help.reportIssue", "Report an Issue…", &["Help"], None),\n', ""),
        ('("window.theme.pro", "Pro Theme", &["Window", "Theme"], None),', '("window.theme.pro", "HORIX Theme", &["Window", "Theme"], None),'),
    ])


def title_bar(root: Path) -> None:
    # The title-bar Discord button goes; in the browser a "desktop apps" button takes its place.
    edit(root, "crates/ui-egui/src/panels.rs", [(
        """                    // The community Discord, one click away while the bar has room for it
                    // (narrow windows drop it first; it is also Help › Discord).
                    if ui.available_width() >= DISCORD_ROOM {
                        let discord = egui::Button::image_and_text(
                            icons::image("message-square", 14.0, t.text_dim),
                            egui::RichText::new(tl!("Discord")).color(t.text_dim).size(12.0),
                        )
                        .frame(false);
                        if ui
                            .add(discord)
                            .on_hover_text({
                                let template = "Join the ArtCraft Discord ({url})";
                                crate::i18n::fmt(tl!(template), &[("url", crate::links::DISCORD)])
                            })
                            .clicked()
                        {
                            crate::links::open(app, ui.ctx(), crate::links::DISCORD);
                        }
                    }
""",
        """                    // HORIX (web): the Windows / macOS apps, one click away while the bar has room.
                    if ui.available_width() >= DISCORD_ROOM {
                        crate::links::desktop_title_button(app, ui);
                    }
""")])


def logo(root: Path) -> None:
    assets = HERE / "assets"
    shutil.copyfile(assets / "horix-symbol.svg", root / "crates/ui-egui/src/horix_symbol.svg")
    shutil.copyfile(assets / "horix-lockup.svg", root / "crates/ui-egui/src/horix_lockup.svg")
    # Arabic lines of the start screen, pre-shaped (tools/arabic_svg.py): width / height of each.
    aspect = {}
    for name in ("soon-title", "soon-apps", "soon-cta", "dl-short", "dl-cta"):
        svg = (assets / "text" / f"{name}.svg").read_text(encoding="utf-8")
        _, _, w, h = (float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split())
        aspect[name] = w / h
        shutil.copyfile(assets / "text" / f"{name}.svg", root / f"crates/ui-egui/src/{name.replace('-', '_')}.svg")
    edit(root, "crates/ui-egui/src/links.rs", [
        ("pub fn url_for(", """/// SG - PS: "Contact us" (WhatsApp, courses and services), next to the Facebook button.
pub fn contact_button(app: &mut PhotocraftApp, ui: &mut egui::Ui, min_width: f32) -> egui::Response {
    let r = crate::widgets::secondary_button(ui, tl!("Contact us"), min_width).on_hover_text(tl!("Courses and services: chat with us on WhatsApp"));
    if r.clicked() {
        open(app, ui.ctx(), CONTACT);
    }
    r
}

/// HORIX: a waitlist request for `product` ("early": early access to the coming apps, or "general").
/// In the browser the page shows its Arabic form; the desktop app opens the site with the form.
pub static WAITLIST_REQUEST: std::sync::Mutex<Option<String>> = std::sync::Mutex::new(None);

pub fn waitlist(app: &mut PhotocraftApp, ctx: &egui::Context, product: &str) {
    if cfg!(target_arch = "wasm32") {
        *WAITLIST_REQUEST.lock().unwrap_or_else(|e| e.into_inner()) = Some(product.to_string());
        ctx.request_repaint();
    } else {
        let url = format!("{APP_PAGE}/?waitlist={}", product.replace(' ', ""));
        open(app, ctx, &url);
    }
}

/// HORIX: one line of Arabic, pre-shaped into white outlines (egui does not shape Arabic), tinted.
fn arabic(uri: &'static str, bytes: &'static [u8], aspect: f32, height: f32, color: egui::Color32) -> egui::Image<'static> {
    egui::Image::from_bytes(uri, bytes).fit_to_exact_size(egui::vec2(height * aspect, height)).tint(color)
}

/// HORIX: the coming alternatives, announced on the start screen, with an early-access waitlist.
pub fn coming_soon(app: &mut PhotocraftApp, ui: &mut egui::Ui) {
    let t = crate::theme::Tokens::get(ui.ctx());
    ui.add(arabic("bytes://soon-title.svg", include_bytes!("soon_title.svg"), SOON_TITLE_ASPECT, 23.0, t.accent));
    ui.add_space(3.0);
    ui.add(arabic("bytes://soon-apps.svg", include_bytes!("soon_apps.svg"), SOON_APPS_ASPECT, 16.3, t.text_dim));
    ui.add_space(10.0);
    let (rect, r) = ui.allocate_exact_size(egui::vec2(190.0, 32.0), egui::Sense::click());
    let r = r.on_hover_cursor(egui::CursorIcon::PointingHand);
    let [cr, cg, cb, _] = t.primary_bg.to_array();
    let fill = if r.hovered() { egui::Color32::from_rgb(cr.saturating_add(14), cg.saturating_add(14), cb.saturating_add(14)) } else { t.primary_bg };
    ui.painter().rect_filled(rect, t.radius, fill);
    arabic("bytes://soon-cta.svg", include_bytes!("soon_cta.svg"), SOON_CTA_ASPECT, 15.7, t.primary_text)
        .paint_at(ui, egui::Rect::from_center_size(rect.center(), egui::vec2(15.7 * SOON_CTA_ASPECT, 15.7)));
    if r.clicked() {
        waitlist(app, ui.ctx(), "early");
    }
}

/// The HORIX falcon symbol, `height` tall, rendered by the egui_extras SVG loader.
pub fn logo(height: f32) -> egui::Image<'static> {
    egui::Image::from_bytes("bytes://horix-symbol.svg", include_bytes!("horix_symbol.svg").as_slice())
        .fit_to_exact_size(egui::vec2(height * 1051.0 / 753.0, height))
}

/// The HORIX logo (falcon over the HORIX letters), `width` wide.
pub fn lockup(width: f32) -> egui::Image<'static> {
    egui::Image::from_bytes("bytes://horix-lockup.svg", include_bytes!("horix_lockup.svg").as_slice())
        .fit_to_exact_size(egui::vec2(width, width * 1107.0 / 1334.0))
}

pub fn url_for("""),
    ])
    consts = "".join(f"const {n.upper().replace('-', '_')}_ASPECT: f32 = {v:.4f};\n" for n, v in aspect.items())
    edit(root, "crates/ui-egui/src/links.rs", [("/// HORIX: one line of Arabic", consts + "\n" + DESKTOP_BUTTONS + "/// HORIX: one line of Arabic")])
    edit(root, "crates/ui-egui/src/canvas.rs", [
        ("let card = Rect::from_center_size(area.center(), egui::vec2(460.0, 330.0 + recent_h));",
         "let card = Rect::from_center_size(area.center(), egui::vec2(470.0, 560.0 + recent_h));"),
        ("""            crate::links::discord_button(app, ui, 190.0);
            ui.add_space(10.0);
            crate::links::link_row(app, ui);""",
         """            ui.add_space(8.0);
            crate::links::coming_soon(app, ui);"""),
        # The official lockup in place of the typed title: logo, descriptor, a short red rule, "BY SABER GROUP".
        ("""            ui.horizontal(|ui| {
                let title = ui.painter().layout_no_wrap(tl!("PhotoCraft").into(), crate::theme::semibold(38.0), t.text);
                let by = ui.painter().layout_no_wrap(tl!("open source").into(), egui::FontId::proportional(13.0), t.text_faint);
                let total = title.size().x + by.size().x + 10.0;
                ui.add_space(((card.width() - total) / 2.0).max(0.0));
                let (r, _) = ui.allocate_exact_size(title.size(), Sense::hover());
                ui.painter().galley(r.min, title, t.text);
                let (r2, _) = ui.allocate_exact_size(egui::vec2(by.size().x + 10.0, r.height()), Sense::hover());
                ui.painter().galley(egui::pos2(r2.left() + 10.0, r.bottom() - by.size().y - 8.0), by, t.text_faint);
            });
""", """            ui.add(crate::links::lockup(190.0));
            ui.add_space(12.0);
            ui.label(egui::RichText::new("THE VISIONARY AI EDITOR").font(crate::theme::medium(12.0)).color(t.text));
            ui.add_space(4.0);
            let (rule, _) = ui.allocate_exact_size(egui::vec2(28.0, 2.0), Sense::hover());
            ui.painter().rect_filled(rule, 0.0, egui::Color32::from_rgb(214, 60, 50)); // Horix Red, as in the logo
            ui.add_space(4.0);
            ui.label(egui::RichText::new("BY SABER GROUP").font(crate::theme::medium(10.5)).color(t.text_faint));
            ui.add_space(10.0);
"""),
        # HORIX (web): a clear way to the Windows / macOS apps, under "Drop an image".
        ("""                ui.label(egui::RichText::new(msg).color(t.text_faint));
            });
""", """                ui.label(egui::RichText::new(msg).color(t.text_faint));
            });
            crate::links::desktop_cta(app, ui);
"""),
    ])
    edit(root, "crates/ui-egui/src/dialogs.rs", [
        ('ui.label(tl!("PhotoCraft — an open-source, native image editor written in Rust."));',
         'ui.vertical_centered(|ui| ui.add(crate::links::logo(64.0)));\n'
         '                    ui.add_space(6.0);\n'
         '                    ui.label(tl!("PhotoCraft — the visionary AI editor by Saber Group."));'),
        ('ui.weak("egui · wgpu · photocraft-engine");',
         'ui.weak("Built on open-source software (MIT / Apache-2.0). Licence texts ship with the app.");'),
    ])


def theme(root: Path) -> None:
    rel = "crates/ui-egui/src/theme.rs"
    edit(root, rel, [
        # HORIX uses the complete Pro shell, recoloured with the quieter Studio palette.  The
        # legacy Studio shell remains deserializable for compatibility but is hidden and migrated.
        ("    Pro,\n    /// Photoshop's default (second) interface brightness: #535353 panels, #282828 canvas (default).\n    #[default]\n    ProMedium,",
         "    #[default]\n    Pro,\n    /// Photoshop's default (second) interface brightness: #535353 panels, #282828 canvas.\n    ProMedium,"),
        ('ThemeKind::Pro => "Pro (Dark)",', 'ThemeKind::Pro => "HORIX (Dark)",'),
        ('ThemeKind::Studio => "Studio (Dark)",', 'ThemeKind::Studio => "HORIX (Legacy)",'),
        ('"pro" | "prodark" | "photoshop" | "dark" =>', '"pro" | "prodark" | "photoshop" | "dark" | "horix" | "horixpro" =>'),
        ('"studio" | "studiodark" => Some(ThemeKind::Studio),', '"studio" | "studiodark" => Some(ThemeKind::Pro),'),
        ('unwrap_or_else(|| Tokens::for_kind(ThemeKind::Studio))', 'unwrap_or_else(|| Tokens::for_kind(ThemeKind::Pro))'),
        ('assert_eq!(ThemeKind::from_name("studio"), Some(ThemeKind::Studio));',
         'assert_eq!(ThemeKind::from_name("studio"), Some(ThemeKind::Pro));\n'
         '        assert!(!ThemeKind::ALL.contains(&ThemeKind::Studio));'),
    ])
    # Studio leaves the selectable list (structural: the list length is upstream's to change).
    path = root / rel
    text = path.read_text(encoding="utf-8")
    m = re.search(r"pub const ALL: \[ThemeKind; (\d+)\] = \[\n((?:        ThemeKind::\w+,\n)+)    \];", text)
    if not m or "        ThemeKind::Studio,\n" not in m.group(2):
        sys.exit("rebrand: theme.rs: ThemeKind::ALL list not found")
    kinds = m.group(2).replace("        ThemeKind::Studio,\n", "")
    text = text[:m.start()] + f"pub const ALL: [ThemeKind; {int(m.group(1)) - 1}] = [\n{kinds}    ];" + text[m.end():]
    # The fully featured Pro shell gets the exact visual palette of the preferred Studio theme.
    # Keep `pro: true`, plus opaque tab/row colours, because those drive the complete panel UI.
    start = text.index("            ThemeKind::Pro => Tokens {")
    end = text.index("            ThemeKind::Studio => Tokens {")
    horix = """            ThemeKind::Pro => Tokens {
                kind,
                chrome: Color32::from_rgb(20, 20, 21),
                canvas: Color32::from_rgb(14, 14, 15),
                canvas_dot: Color32::from_rgb(46, 46, 50),
                dock: Color32::from_rgb(17, 17, 18),
                card: Color32::from_rgb(26, 26, 28),
                card_border: Color32::from_rgb(40, 40, 44),
                field: Color32::from_rgb(35, 35, 38),
                field_border: Color32::from_rgb(52, 52, 57),
                hover: Color32::from_rgb(44, 44, 48),
                pressed: Color32::from_rgb(56, 56, 62),
                text: Color32::from_rgb(243, 239, 232),
                text_dim: Color32::from_rgb(150, 150, 158),
                text_faint: Color32::from_rgb(96, 96, 104),
                icon: Color32::from_rgb(196, 196, 204),
                accent: Color32::from_rgb(234, 153, 63),
                accent_soft: Color32::from_rgba_unmultiplied(234, 153, 63, 46),
                accent_border: Color32::from_rgba_unmultiplied(234, 153, 63, 120),
                accent_text: Color32::from_rgb(246, 200, 148),
                separator: Color32::from_rgb(38, 38, 42),
                shadow: Color32::from_black_alpha(140),
                primary_bg: Color32::from_rgb(243, 239, 232),
                primary_text: Color32::from_rgb(20, 19, 20),
                danger: Color32::from_rgb(240, 96, 96),
                warning: Color32::from_rgb(240, 190, 90),
                radius_sm: 6.0,
                radius: 8.0,
                radius_lg: 12.0,
                bevel: false,
                pro: true,
                round_chips: false,
                tab_strip: Color32::from_rgb(20, 20, 21),
                row_selected: Color32::from_rgb(44, 44, 48),
                histogram_bg: Color32::from_rgb(14, 14, 15),
                histogram_level: 225,
                caption_close: Color32::from_rgb(214, 60, 50),
                caption_close_text: Color32::WHITE,
                scrim: Color32::from_black_alpha(110),
            },
"""
    text = text[:start] + horix + text[end:]
    path.write_text(text, encoding="utf-8")
    # Display face for headlines: Barlow Condensed ExtraBold (OFL), falling back to Inter.
    shutil.copyfile(HERE / "assets/fonts/BarlowCondensed-ExtraBold.ttf", root / "crates/ui-egui/src/horix_display.ttf")
    edit(root, rel, [
        ('    let mono = add(&mut fonts, "JetBrainsMono", photocraft_text::fonts::JETBRAINS_MONO_REGULAR.as_slice());\n',
         '    let mono = add(&mut fonts, "JetBrainsMono", photocraft_text::fonts::JETBRAINS_MONO_REGULAR.as_slice());\n'
         '    let display = add(&mut fonts, "HorixDisplay", include_bytes!("horix_display.ttf").as_slice());\n'),
        ('for (fam, primary) in [("medium", medium), ("semibold", semibold)] {',
         'for (fam, primary) in [("medium", medium), ("semibold", semibold), ("display", display)] {'),
        ("pub fn mono(size: f32) -> FontId {",
         "/// HORIX: the brand's display face (condensed, heavy) for headlines.\n"
         "pub fn display(size: f32) -> FontId {\n    FontId::new(size, FontFamily::Name(\"display\".into()))\n}\n"
         "pub fn mono(size: f32) -> FontId {"),
    ])
    # Preferences: HORIX (Pro) is the default dark theme; `studio` still loads (old files) but is
    # no longer offered, and maps to HORIX.
    prefs = "crates/engine/src/prefs.rs"
    edit(root, prefs, [
        ('SoftDark = "softDark", SoftLight = "softLight" } default ProMedium);', 'SoftDark = "softDark", SoftLight = "softLight" } default Pro);'),
        ('BreezeDark = "breezeDark", SoftDark = "softDark" } default ProMedium);', 'BreezeDark = "breezeDark", SoftDark = "softDark" } default Pro);'),
        ("            theme: Theme::ProMedium,", "            theme: Theme::Pro,"),
        ("            dark_theme: DarkTheme::ProMedium,", "            dark_theme: DarkTheme::Pro,"),
        ('        "interface.theme" => Theme::NAMES,', '        "interface.theme" => &HORIX_THEME_NAMES,'),
        ('        "interface.darkTheme" => DarkTheme::NAMES,', '        "interface.darkTheme" => &HORIX_DARK_THEME_NAMES,'),
    ])
    path = root / prefs
    text = path.read_text(encoding="utf-8")
    for enum, const in (("Theme", "HORIX_THEME_NAMES"), ("DarkTheme", "HORIX_DARK_THEME_NAMES")):
        m = re.search(rf"^choice!\({enum} \{{ (.*?) \}} default Pro\);$", text, re.M)
        if not m:
            sys.exit(f"rebrand: prefs.rs: choice!({enum} ...) not found")
        names = [v for v in re.findall(r'= "(\w+)"', m.group(1)) if v != "studio"]
        decl = f"\n// HORIX: `studio` remains deserializable for old files, but is no longer selectable.\nconst {const}: [&str; {len(names)}] = [{', '.join(repr(n).replace(chr(39), chr(34)) for n in names)}];"
        text = text[:m.end()] + decl + text[m.end():]
    path.write_text(text, encoding="utf-8")
    edit(root, "crates/ui-egui/src/state.rs", [
        ("            theme: crate::theme::ThemeKind::ProMedium,", "            theme: crate::theme::ThemeKind::Pro,"),
    ])
    edit(root, "crates/ui-egui/src/prefs_ui.rs", [
        # Existing preferences can still contain `studio`: load it into the HORIX shell.
        ("            DarkTheme::Studio => ThemeKind::Studio,", "            DarkTheme::Studio => ThemeKind::Pro,"),
        # HORIX first in the Dark Theme list; Studio no longer offered.
        ('    ("proMedium", ThemeKind::ProMedium),\n    ("pro", ThemeKind::Pro),\n    ("studio", ThemeKind::Studio),\n',
         '    ("pro", ThemeKind::Pro),\n    ("proMedium", ThemeKind::ProMedium),\n'),
    ])


def full_tool_options(root: Path) -> None:
    """Every theme gets the full tool options bar.

    Upstream only builds the complete options (blend mode, opacity, feather, gradient type, crop
    ratio, align buttons...) for the Pro themes; the Studio and Classic themes get a one-line hint
    such as "Drag to draw a gradient". The guards become a constant, so the full arms always win."""
    rel = "crates/ui-egui/src/panels.rs"
    path = root / rel
    text = path.read_text(encoding="utf-8")
    n = text.count(" if t.pro => ")
    if n < 1:
        sys.exit(f"rebrand: {rel}: no Pro-only option arms found")
    text = text.replace(" if t.pro => ", " if FULL_TOOL_OPTIONS => ")
    marker = "pub fn options_bar(app: &mut PhotocraftApp, ui: &mut egui::Ui) {"
    if marker not in text:
        sys.exit(f"rebrand: {rel}: options_bar not found")
    text = text.replace(marker, "/// SG - PS: show the full tool options in every theme, not only the Pro ones.\n"
                                "const FULL_TOOL_OPTIONS: bool = true;\n\n" + marker, 1)
    path.write_text(text, encoding="utf-8")


SUBJECT_PRIOR = '''    for v in &mut out {
        *v = (*v - lo) / r;
    }
    focus_prior(&mut out, w, h);
    out
}

/// SG - PS: spatial prior around the salient mass. The centroid and spread of the most salient
/// pixels locate the subject; saliency far from it (a busy background that happens to contrast)
/// is damped with a Gaussian, so the GrabCut seeds stay on one object. Measured with
/// apps/sg-ps/segeval: mean IoU 0.756 -> 0.867 over 15 cases; busy backgrounds 0.26 -> 0.94.
fn focus_prior(sal: &mut [f32], w: usize, h: usize) {
    let (mut sx, mut sy, mut sw) = (0f64, 0f64, 0f64);
    for y in 0..h {
        for x in 0..w {
            let v = (sal[y * w + x] as f64).powi(4);
            sx += v * x as f64;
            sy += v * y as f64;
            sw += v;
        }
    }
    if sw <= 1e-9 {
        return;
    }
    let (cx, cy) = (sx / sw, sy / sw);
    let (mut vx, mut vy) = (0f64, 0f64);
    for y in 0..h {
        for x in 0..w {
            let v = (sal[y * w + x] as f64).powi(4);
            vx += v * (x as f64 - cx).powi(2);
            vy += v * (y as f64 - cy).powi(2);
        }
    }
    let sdx = (vx / sw).sqrt().max(w as f64 * 0.12) * PRIOR_SPREAD;
    let sdy = (vy / sw).sqrt().max(h as f64 * 0.12) * PRIOR_SPREAD;
    for y in 0..h {
        for x in 0..w {
            let (dx, dy) = ((x as f64 - cx) / sdx, (y as f64 - cy) / sdy);
            sal[y * w + x] *= (-(dx * dx + dy * dy) / 2.0).exp() as f32;
        }
    }
    let hi = sal.iter().copied().fold(0.0f32, f32::max).max(1e-6);
    for v in sal.iter_mut() {
        *v /= hi;
    }
}'''


def better_select_subject(root: Path) -> None:
    edit(root, "crates/algo/src/segment/subject.rs", [
        ("""    for v in &mut out {
        *v = (*v - lo) / r;
    }
    out
}""", SUBJECT_PRIOR),
        ("const SIGMA_SPA: f32 = 0.25;",
         "const SIGMA_SPA: f32 = 0.25;\n/// Width of the subject prior, in standard deviations of the salient mass (tuned with segeval).\n"
         "const PRIOR_SPREAD: f64 = 1.5;"),
    ])


PLAIN_SUBJECT_OLD = r'''    let mut trimap = vec![PR_BG; w * h];
    let mut any_fg = false;
    for y in 0..h {
        for x in 0..w {
            let i = y * w + x;
            let border = x == 0 || y == 0 || x + 1 == w || y + 1 == h;
            trimap[i] = if sal[i] >= t {
                any_fg = true;
                PR_FG
            } else if border || sal[i] < 0.4 * t {
                BG
            } else {
                PR_BG
            };
        }
    }
    if !any_fg {
        return Ok(None);
    }
    let Some((fg, bg)) = grabcut::grabcut_with(&img, &mut trimap, 6, ctl)? else { return Ok(None) };
    let low: Vec<bool> = trimap.iter().map(|v| *v == PR_FG || *v == grabcut::FG).collect();
    let low = super::clean_mask(&low, w, h, 0.2, 0.05);
    if !low.iter().any(|v| *v) {
        return Ok(None);
    }
    super::finish_region_with(sampler, canvas, step, &low, w, h, Some((&fg, &bg)), ctl)
}
'''

PLAIN_SUBJECT = r'''    // SG - PS: on a plain background (studio white, a flat colour, a soft gradient) the
    // background itself is the better cue. A colour model of the canvas border marks what is
    // background; pixels that look like it and connect to the border are background for sure,
    // and everything else (bar soft shadows) starts as subject, so dark or thin parts the
    // saliency misses (fingers, black joints) stay in. Busy backgrounds keep the saliency trimap.
    let ring = (w.min(h) / 40).max(2);
    let on_ring = |i: usize| {
        let (x, y) = (i % w, i / w);
        x < ring || y < ring || x + ring >= w || y + ring >= h
    };
    let ring_px: Vec<[f32; 3]> = (0..w * h).filter(|i| on_ring(*i)).map(|i| img.px[i]).collect();
    let mut mean = [0f64; 3];
    for p in &ring_px {
        for c in 0..3 {
            mean[c] += p[c] as f64;
        }
    }
    let mean = mean.map(|v| (v / ring_px.len() as f64) as f32);
    // How plain the border is: RMS distance of its colours from their mean.
    let spread = (ring_px.iter().map(|p| super::d2(*p, mean) as f64).sum::<f64>() / ring_px.len() as f64).sqrt() as f32;
    let plain = spread < PLAIN_SPREAD;
    let mut bg_like = vec![false; w * h];
    let mut reach = vec![false; w * h];
    if plain {
        let Some(bgm) = Gmm::fit(&subsample(&ring_px, 20_000), 3, DEFAULT_REG) else { return Ok(None) };
        let nl: Vec<f32> = img.px.iter().map(|p| bgm.neg_log(*p)).collect();
        let mut ring_nl: Vec<f32> = (0..w * h).filter(|i| on_ring(*i)).map(|i| nl[i]).collect();
        ring_nl.sort_by(f32::total_cmp);
        let thr = ring_nl[(ring_nl.len() - 1) * BG_PCT / 100] + BG_SLACK;
        bg_like = nl.iter().map(|v| *v <= thr).collect();
        reach = border_flood(&bg_like, w, h);
    }
    // Shadows: a darker copy of the background colour (only visible on a light background).
    let light_bg = 0.299 * mean[0] + 0.587 * mean[1] + 0.114 * mean[2] > 0.35;
    let mm = (mean[0] * mean[0] + mean[1] * mean[1] + mean[2] * mean[2]).max(1e-4);
    let shadow = |p: [f32; 3]| {
        let k = (p[0] * mean[0] + p[1] * mean[1] + p[2] * mean[2]) / mm;
        light_bg && (0.45..1.03).contains(&k) && super::d2(p, mean.map(|c| c * k)).sqrt() < SHADOW_TOL
    };
    let mut trimap = vec![PR_BG; w * h];
    let mut any_fg = false;
    for y in 0..h {
        for x in 0..w {
            let i = y * w + x;
            let border = x == 0 || y == 0 || x + 1 == w || y + 1 == h;
            trimap[i] = if plain {
                if border || (reach[i] && sal[i] < REACH_SAL) {
                    BG
                } else if reach[i] || shadow(img.px[i]) {
                    PR_BG
                } else {
                    any_fg = true;
                    PR_FG
                }
            } else if sal[i] >= t {
                any_fg = true;
                PR_FG
            } else if border || sal[i] < 0.4 * t {
                BG
            } else {
                PR_BG
            };
        }
    }
    if !any_fg {
        return Ok(None);
    }
    let Some((fg, bg)) = grabcut::grabcut_with(&img, &mut trimap, 6, ctl)? else { return Ok(None) };
    let low: Vec<bool> = trimap.iter().map(|v| *v == PR_FG || *v == grabcut::FG).collect();
    // Islands on a plain background are parts of the subject (a hand past a dark wrist).
    let mut low = super::clean_mask(&low, w, h, if plain { 0.02 } else { 0.2 }, 0.05);
    if plain {
        // Enclosed areas of the background colour are gaps in the subject (between a raised arm
        // and the head, say): open them unless they are specks (highlights).
        let area = low.iter().filter(|v| **v).count();
        let gap: Vec<bool> = (0..w * h).map(|i| low[i] && bg_like[i] && !reach[i]).collect();
        let (lab, sizes) = super::components(&gap, w, h);
        for (o, l) in low.iter_mut().zip(&lab) {
            if *l != 0 && sizes[*l as usize] * GAP_PER_MILLE >= area {
                *o = false;
            }
        }
    }
    if !low.iter().any(|v| *v) {
        return Ok(None);
    }
    let Some(r) = super::finish_region_with(sampler, canvas, step, &low, w, h, Some((&fg, &bg)), ctl)? else { return Ok(None) };
    // Soft edges where the background is plain enough to estimate them.
    Ok(Some(if plain { matte_edges(sampler, canvas, r) } else { r }))
}

/// Border colour spread (RMS, 0..1 RGB) under which the background counts as plain.
const PLAIN_SPREAD: f32 = 0.15;
/// Percentile of the border's own pixels the background model must explain, and extra slack
/// (in negative log-likelihood) so gradients and soft noise still count as background.
const BG_PCT: usize = 97;
const BG_SLACK: f32 = 4.0;
/// Background-coloured pixels connected to the border stay background below this saliency.
const REACH_SAL: f32 = 0.8;
/// RGB distance within which a darker copy of the background colour is a shadow.
const SHADOW_TOL: f32 = 0.05;
/// Enclosed background-coloured areas of at least 1/GAP_PER_MILLE of the subject are gaps.
const GAP_PER_MILLE: usize = 400;

/// Pixels of `mask` 4-connected to the image border through `mask`.
fn border_flood(mask: &[bool], w: usize, h: usize) -> Vec<bool> {
    let mut out = vec![false; w * h];
    let mut stack: Vec<usize> = (0..w * h).filter(|i| {
        let (x, y) = (i % w, i / w);
        mask[*i] && (x == 0 || y == 0 || x + 1 == w || y + 1 == h)
    }).collect();
    for i in &stack {
        out[*i] = true;
    }
    while let Some(i) = stack.pop() {
        let (x, y) = (i % w, i / w);
        let n = [(x > 0).then(|| i - 1), (x + 1 < w).then(|| i + 1), (y > 0).then(|| i - w), (y + 1 < h).then(|| i + w)];
        for j in n.into_iter().flatten() {
            if mask[j] && !out[j] {
                out[j] = true;
                stack.push(j);
            }
        }
    }
    out
}

/// SG - PS: soft edges. Pixels within 2 px of the cut get the coverage the local colours imply:
/// with F and B the mean colours of the sure foreground and sure background within `R` pixels,
/// alpha is the projection of the pixel onto the line from B to F (a closed-form colour-line
/// matte). Where F and B are too alike to tell apart the cut's own edge is kept.
fn matte_edges(sampler: &dyn Sampler, canvas: Rect, r: Region) -> Region {
    const R: i32 = 6;
    const E: i32 = 2;
    const STRIP: i32 = 128;
    let win = r.bbox.inflate(R + E + 1).intersect(&canvas);
    let w = win.width() as usize;
    let mut a = vec![0u8; w * win.height() as usize];
    for y in r.bbox.y0..r.bbox.y1 {
        let bw = r.bbox.width() as usize;
        let src = &r.mask[(y - r.bbox.y0) as usize * bw..][..bw];
        let o = (y - win.y0) as usize * w + (r.bbox.x0 - win.x0) as usize;
        a[o..o + bw].copy_from_slice(src);
    }
    let src = a.clone();
    let mut y0 = win.y0;
    while y0 < win.y1 {
        let y1 = (y0 + STRIP).min(win.y1);
        let s = Rect::new(win.x0, (y0 - R - E).max(win.y0), win.x1, (y1 + R + E).min(win.y1));
        let sh = s.height() as usize;
        let soff = (s.y0 - win.y0) as usize * w;
        let hard: Vec<u8> = src[soff..soff + w * sh].iter().map(|v| (*v >= 128) as u8).collect();
        // Integral image helper over (w+1)×(sh+1).
        let integral = |f: &dyn Fn(usize) -> f64| -> Vec<f64> {
            let mut t = vec![0f64; (w + 1) * (sh + 1)];
            for y in 0..sh {
                let mut row = 0.0;
                for x in 0..w {
                    row += f(y * w + x);
                    t[(y + 1) * (w + 1) + x + 1] = t[y * (w + 1) + x + 1] + row;
                }
            }
            t
        };
        let boxsum = |t: &[f64], x: usize, y: usize, rr: usize| -> f64 {
            let (xa, ya) = (x.saturating_sub(rr), y.saturating_sub(rr));
            let (xb, yb) = ((x + rr + 1).min(w), (y + rr + 1).min(sh));
            t[yb * (w + 1) + xb] - t[ya * (w + 1) + xb] - t[yb * (w + 1) + xa] + t[ya * (w + 1) + xa]
        };
        let ih = integral(&|i| hard[i] as f64);
        let e = E as usize;
        let full = |x: usize, y: usize| {
            let (xa, ya) = (x.saturating_sub(e), y.saturating_sub(e));
            (((x + e + 1).min(w) - xa) * ((y + e + 1).min(sh) - ya)) as f64
        };
        // Sure foreground / background: the whole (2E+1)² neighbourhood agrees.
        let mut sure = vec![0u8; w * sh];
        for y in 0..sh {
            for x in 0..w {
                let c = boxsum(&ih, x, y, e);
                sure[y * w + x] = if c >= full(x, y) - 0.5 { 1 } else if c < 0.5 { 2 } else { 0 };
            }
        }
        if sure.iter().all(|v| *v != 0) {
            y0 = y1;
            continue;
        }
        let img = sampler.rgb(s);
        let mut sums = Vec::new();
        for side in [1u8, 2] {
            sums.push(integral(&|i| (sure[i] == side) as u8 as f64));
            for c in 0..3 {
                sums.push(integral(&|i| if sure[i] == side { img.px[i][c] as f64 } else { 0.0 }));
            }
        }
        let rr = R as usize;
        for y in (y0 - s.y0) as usize..(y1 - s.y0) as usize {
            for x in 0..w {
                let i = y * w + x;
                if sure[i] != 0 {
                    continue;
                }
                let (nf, nb) = (boxsum(&sums[0], x, y, rr), boxsum(&sums[4], x, y, rr));
                if nf < 1.0 || nb < 1.0 {
                    continue;
                }
                let f: [f64; 3] = [0, 1, 2].map(|c| boxsum(&sums[1 + c], x, y, rr) / nf);
                let b: [f64; 3] = [0, 1, 2].map(|c| boxsum(&sums[5 + c], x, y, rr) / nb);
                let p = img.px[i];
                let (mut num, mut den) = (0.0, 0.0);
                for c in 0..3 {
                    let d = f[c] - b[c];
                    num += (p[c] as f64 - b[c]) * d;
                    den += d * d;
                }
                if den < 0.004 {
                    continue;
                }
                let alpha = (num / den).clamp(0.0, 1.0);
                let conf = (den / 0.03).min(1.0);
                let o = soff + i;
                let old = src[o] as f64 / 255.0;
                a[o] = ((conf * alpha + (1.0 - conf) * old) * 255.0).round() as u8;
            }
        }
        y0 = y1;
    }
    super::trim_region(Region { bbox: win, mask: a }).unwrap_or(r)
}
'''


def plain_background_subject(root: Path) -> None:
    """Select Subject on plain backgrounds: border colour model, gap opening, colour-line soft edges.

    Measured with the segeval harness (Maro renders with exact alpha over white, gray, gradient,
    soft texture, shadow, black and navy): IoU 0.94 -> 0.999 on white, edge error 0.157 -> 0.026;
    busy backgrounds unchanged.
    """
    edit(root, "crates/algo/src/segment/subject.rs", [
        ("use super::{Region, Sampler};", "use super::gmm::{DEFAULT_REG, Gmm};\nuse super::{Region, Sampler, subsample};"),
        (PLAIN_SUBJECT_OLD, PLAIN_SUBJECT),
    ])
    edit(root, "crates/algo/src/segment/mod.rs", [("\nfn d2(a: [f32; 3], b: [f32; 3]) -> f32 {", "\npub(crate) fn d2(a: [f32; 3], b: [f32; 3]) -> f32 {")])


KEYBOARD_SCRIPT = """  <script>
    // SG - PS: while the editor is open, keyboard shortcuts belong to the editor, not the browser.
    // The listener runs in the capture phase and only cancels the browser's default action, so the
    // editor still receives every key. Ctrl/Cmd+C/V/X keep their default: the browser must fire the
    // copy, paste and cut events the editor reads the clipboard from. F12 stays the developer tools.
    (function () {
      var clipboard = { c: 1, v: 1, x: 1 };
      function lockKeys() {
        if (navigator.keyboard && navigator.keyboard.lock) navigator.keyboard.lock().catch(function () {});
      }
      // Chrome never lets a page cancel Ctrl+N, Ctrl+T, Ctrl+W or Ctrl+Tab, except in fullscreen
      // with the Keyboard Lock API. F11 therefore enters the page's own fullscreen and locks the keys
      // (hold Esc to leave).
      function toggleFullscreen() {
        if (document.fullscreenElement) document.exitFullscreen().catch(function () {});
        else document.documentElement.requestFullscreen().then(lockKeys).catch(function () {});
      }
      document.addEventListener('fullscreenchange', function () {
        if (!document.fullscreenElement && navigator.keyboard && navigator.keyboard.unlock) navigator.keyboard.unlock();
      });
      window.addEventListener('keydown', function (e) {
        if (e.target && /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return;
        var k = (e.key || '').toLowerCase();
        if (k === 'f12') return;
        if (k === 'f11') { e.preventDefault(); toggleFullscreen(); return; }
        var cmd = e.ctrlKey || e.metaKey;
        // The physical key too: with an Arabic (or other non-Latin) layout Ctrl+C reports e.key 'ؤ'.
        var code = (e.code || '').replace(/^Key/, '').toLowerCase();
        if (cmd && !e.altKey && (clipboard[k] || clipboard[code])) return;
        if (cmd || e.altKey || k === 'alt' || /^f([1-9]|10)$/.test(k)) e.preventDefault();
      }, true);
      // Releasing Alt (or F10) would move the keyboard to the browser's menu (Windows) and the
      // editor would stop getting keys: Alt+click in the Layers panel, Alt+drag, Ctrl+Alt+G...
      window.addEventListener('keyup', function (e) {
        if (e.target && /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return;
        var k = (e.key || '').toLowerCase();
        if (k === 'alt' || k === 'f10') e.preventDefault();
      }, true);
      // Ctrl+wheel and pinch zoom the canvas, not the page.
      window.addEventListener('wheel', function (e) { if (e.ctrlKey) e.preventDefault(); }, { passive: false, capture: true });
      // Closing or reloading the tab asks first, so unsaved work isn't lost by a stray key.
      window.addEventListener('beforeunload', function (e) { e.preventDefault(); e.returnValue = ''; });
      // One-time hint about F11.
      var HINT = 'sgps.hint.fullscreen';
      function showHint() {
        try { if (localStorage.getItem(HINT)) return; } catch (err) {}
        var d = document.createElement('div');
        d.id = 'sgps_hint';
        d.dir = 'rtl';
        d.innerHTML = '<span>اضغط <b><bdi>F11</bdi></b> لوضع ملء الشاشة: كل الاختصارات، حتى <bdi>Ctrl+N</bdi> و <bdi>Ctrl+W</bdi>، هتشتغل للبرنامج بس. للخروج اضغط مطوّلًا على <bdi>Esc</bdi>.<br>ولو المتصفح سألك عن الخطوط اختار <b><bdi>Allow</bdi></b>: خطوط جهازك هتظهر في أداة النص.</span>' +
          '<button type="button" aria-label="إغلاق">×</button>';
        d.querySelector('button').onclick = function () {
          d.remove();
          try { localStorage.setItem(HINT, '1'); } catch (err) {}
        };
        document.body.appendChild(d);
        setTimeout(function () { if (d.isConnected) d.remove(); }, 12000);
      }
      var waitForApp = setInterval(function () {
        if (!document.getElementById('sgps_loading')) { clearInterval(waitForApp); setTimeout(showHint, 1500); }
      }, 500);
    })();
  </script>
  <style>
    #sgps_hint { position: fixed; left: 50%; bottom: 36px; transform: translateX(-50%); z-index: 10;
      max-width: calc(100% - 32px); display: flex; gap: 12px; align-items: center; padding: 10px 14px;
      background: #2A2727; color: #F3EFE8; border: 1px solid #443D3A; border-radius: 8px;
      font: 13px/1.5 Inter, system-ui, 'Segoe UI', Tahoma, sans-serif; box-shadow: 0 6px 24px rgba(0,0,0,.45); }
    #sgps_hint b { color: #EA993F; }
    #sgps_hint button { background: none; border: 0; color: #EA993F; font-size: 18px; cursor: pointer; padding: 0 4px; }
  </style>
"""


FONTS_SCRIPT = """  <script>
    // SG - PS: fonts installed on this computer, through the Local Font Access API (Chrome / Edge).
    // Type > Load Device Fonts calls sgpsLoadDeviceFonts(); after the first time, the fonts load
    // again by themselves on the first click (the browser remembers the permission).
    (function () {
      var ENABLED = 'sgps.deviceFonts';
      var toastEl = null, toastTimer = null;
      function toast(html, ms) {
        if (!toastEl) {
          toastEl = document.createElement('div');
          toastEl.id = 'sgps_toast';
          toastEl.dir = 'rtl';
          document.body.appendChild(toastEl);
        }
        toastEl.innerHTML = html;
        toastEl.style.display = 'block';
        clearTimeout(toastTimer);
        if (ms) toastTimer = setTimeout(function () { toastEl.style.display = 'none'; }, ms);
      }
      var running = false, seen = {};
      async function load(quiet) {
        if (running) return;
        if (!window.queryLocalFonts) {
          if (!quiet) toast('المتصفح ده مش بيسمح بقراءة خطوط الجهاز. افتح البرنامج من <b>Chrome</b> أو <b>Edge</b>.', 8000);
          return;
        }
        var register = window.wasmBindings && window.wasmBindings.sgps_register_font;
        if (!register) return;
        var fonts;
        try { fonts = await window.queryLocalFonts(); } catch (e) {
          if (!quiet) toast('محتاج إذنك: لما المتصفح يسأل، اختار <b>Allow</b> عشان البرنامج يقرا خطوط جهازك.', 9000);
          return;
        }
        running = true;
        var families = {}, files = 0, skipped = 0;
        toast('جاري تحميل خطوط جهازك…');
        for (var i = 0; i < fonts.length; i++) {
          try {
            var blob = await fonts[i].blob();
            // Faces of one collection file share the blob: register each file once.
            var key = blob.size + '|' + fonts[i].family;
            if (seen[key]) continue;
            seen[key] = 1;
            if (blob.size > 40 * 1024 * 1024) { skipped++; continue; }
            var names = register(new Uint8Array(await blob.arrayBuffer()));
            if (names) names.split('\\n').forEach(function (n) { families[n] = 1; });
            files++;
          } catch (e) { skipped++; }
          if (i % 20 === 0) {
            toast('جاري تحميل خطوط جهازك… ' + Math.round(100 * i / fonts.length) + '%');
            await new Promise(function (r) { setTimeout(r, 0); });
          }
        }
        running = false;
        try { localStorage.setItem(ENABLED, '1'); } catch (e) {}
        var n = Object.keys(families).length;
        if (quiet && !n) { if (toastEl) toastEl.style.display = 'none'; return; }
        toast(n ? 'تم تحميل <b>' + n + '</b> خط من جهازك. هتلاقيهم في قائمة الخطوط في أداة النص (<bdi>T</bdi>).'
                : 'مفيش خطوط جديدة اتحمّلت من الجهاز.', 7000);
      }
      window.sgpsLoadDeviceFonts = function () { load(false); };
      // Device fonts load by themselves: on the first click of every visit the page asks the
      // browser (Chrome shows its "use your fonts" prompt once; after Allow it never asks again).
      // A page cannot read installed fonts before that click: browsers require a user gesture.
      if (window.queryLocalFonts) {
        window.addEventListener('pointerdown', function first() {
          window.removeEventListener('pointerdown', first, true);
          var go = function () { setTimeout(function () { load(true); }, 0); };
          if (!navigator.permissions) return go();
          navigator.permissions.query({ name: 'local-fonts' }).then(function (p) {
            if (p.state !== 'denied') go();
          }).catch(go);
        }, true);
      }
    })();
  </script>
  <style>
    #sgps_toast { display: none; position: fixed; right: 16px; bottom: 36px; z-index: 11; max-width: min(460px, calc(100% - 32px));
      padding: 10px 14px; background: #2A2727; color: #F3EFE8; border: 1px solid #443D3A; border-radius: 8px;
      font: 13px/1.5 Inter, system-ui, 'Segoe UI', Tahoma, sans-serif; box-shadow: 0 6px 24px rgba(0,0,0,.45); }
    #sgps_toast b { color: #EA993F; }
  </style>
"""


WAITLIST_SCRIPT = """  <div id="sgps_wl" dir="rtl" hidden>
    <form id="sgps_wl_form" novalidate>
      <button type="button" class="x" aria-label="إغلاق" data-close>×</button>
      <div class="badge" id="sgps_wl_badge">قريبًا</div>
      <h2 id="sgps_wl_title">احجز تجربتك المجانية</h2>
      <p id="sgps_wl_lead">سيب بياناتك وفريق صابر جروب هيتواصل معاك على واتساب.</p>
      <label>الاسم<input name="name" autocomplete="name" required maxlength="80"></label>
      <label>رقم الواتساب<input name="phone" type="tel" inputmode="tel" autocomplete="tel" required placeholder="01xxxxxxxxx" dir="ltr"></label>
      <fieldset>
        <legend>مهتم تتعلم إيه؟ (اختار كل اللي يهمك)</legend>
        <label class="chk"><input type="checkbox" name="interests" value="graphic-design-101">تصميم جرافيك من الصفر <small>Graphic Design 101</small></label>
        <label class="chk"><input type="checkbox" name="interests" value="advertising-mastery">تصميم إعلانات احترافي <small>Advertising Mastery</small></label>
        <label class="chk"><input type="checkbox" name="interests" value="ai-101">الذكاء الاصطناعي من الصفر <small>AI &amp; Automation 101</small></label>
        <label class="chk"><input type="checkbox" name="interests" value="ai-mastery">بناء Agents وأتمتة الشغل <small>AI &amp; Automation Mastery</small></label>
        <label class="chk"><input type="checkbox" name="interests" value="ai-100x-creatives">AI للصور والفيديو والحملات <small>AI 100x Creatives</small></label>
        <label class="chk"><input type="checkbox" name="interests" value="not-sure">لسه مش متأكد، محتاج حد يساعدني أختار</label>
      </fieldset>
      <label class="chk consent"><input type="checkbox" name="consent">موافق إن فريق صابر جروب يتواصل معايا على واتساب</label>
      <p class="err" id="sgps_wl_err" role="alert"></p>
      <button type="submit" class="go">ابعت</button>
    </form>
    <div id="sgps_wl_done" hidden>
      <button type="button" class="x" aria-label="إغلاق" data-close>×</button>
      <h2>تمام، وصلتنا بياناتك ✓</h2>
      <p id="sgps_wl_done_text"></p>
      <a class="go" id="sgps_wl_wa" target="_blank" rel="noopener">كلّمنا على واتساب دلوقتي</a>
    </div>
  </div>
  <script>
    // HORIX waitlist form: the start screen's early-access button calls sgpsOpenWaitlist('early');
    // /?waitlist=early opens it too (desktop app links; the old ?waitlist=SG-AI links as well).
    (function () {
      var WHATSAPP = '__WHATSAPP__';
      var NAMES = { 'early': 'بدائل After Effects و Premiere و Illustrator و Lightroom' };
      var box = document.getElementById('sgps_wl'), form = document.getElementById('sgps_wl_form');
      var done = document.getElementById('sgps_wl_done'), err = document.getElementById('sgps_wl_err');
      var product = 'general';
      function field(n) { return form.querySelector('[name=' + n + ']'); }
      function open(p) {
        product = NAMES[p] ? p : 'general';
        var soon = product !== 'general';
        document.getElementById('sgps_wl_badge').hidden = !soon;
        document.getElementById('sgps_wl_title').textContent = soon ? 'احجز تجربتك المُبكرة' : 'احجز تجربتك المجانية';
        document.getElementById('sgps_wl_lead').textContent = soon
          ? NAMES[product] + ' جاية قريب. سيب بياناتك وهنبلغك أول ما تنزل، وتكون من أول اللي يجربوها.'
          : 'سيب بياناتك وفريق صابر جروب هيتواصل معاك على واتساب يحدد معاك تجربتك المجانية.';
        err.textContent = '';
        form.hidden = false; done.hidden = true; box.hidden = false;
        setTimeout(function () { field('name').focus(); }, 50);
      }
      function close() { box.hidden = true; }
      window.sgpsOpenWaitlist = open;
      box.addEventListener('click', function (e) { if (e.target === box || e.target.hasAttribute('data-close')) close(); });
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !box.hidden) close(); });
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var name = field('name').value.trim(), phone = field('phone').value.trim();
        var digits = phone.replace(/\\D/g, '');
        if (!name) { err.textContent = 'اكتب اسمك.'; return; }
        if (digits.length < 8 || digits.length > 15) { err.textContent = 'اكتب رقم واتساب صحيح.'; return; }
        if (!field('consent').checked) { err.textContent = 'محتاجين موافقتك عشان نقدر نتواصل معاك.'; return; }
        var interests = Array.prototype.filter.call(form.querySelectorAll('[name=interests]'), function (c) { return c.checked; })
          .map(function (c) { return c.value; });
        var btn = form.querySelector('.go'); btn.disabled = true; err.textContent = '';
        fetch('waitlist.php', { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: name, phone: phone, product: product, interests: interests, consent: true, page: location.pathname + location.search }) })
          .then(function (r) { return r.json().then(function (j) { return [r.status, j]; }); })
          .then(function (res) {
            if (res[1] && res[1].ok) {
              var soon = product !== 'general';
              document.getElementById('sgps_wl_done_text').textContent = soon
                ? 'هنبلغك على واتساب أول ما البدائل تنزل، وتكون من أول اللي يجربوها.'
                : 'فريقنا هيتواصل معاك قريب يحدد معاك تجربتك المجانية.';
              var msg = 'مرحبًا، أنا ' + name + ' وسجلت في HORIX' + (soon ? ' وعايز أحجز تجربتي المُبكرة لـ' + NAMES[product] : ' وعايز أحجز تجربتي المجانية');
              document.getElementById('sgps_wl_wa').href = WHATSAPP + '?text=' + encodeURIComponent(msg);
              form.hidden = true; done.hidden = false; form.reset();
            } else if (res[0] === 429) {
              err.textContent = 'طلبات كتير من نفس الجهاز، جرّب كمان شوية أو كلّمنا على واتساب.';
            } else {
              err.textContent = 'حصلت مشكلة في الإرسال، جرّب تاني أو كلّمنا على واتساب.';
            }
          })
          .catch(function () { err.textContent = 'مفيش اتصال بالإنترنت، جرّب تاني.'; })
          .then(function () { btn.disabled = false; });
      });
      var q = new URLSearchParams(location.search).get('waitlist');
      if (q) {
        var wanted = /^(early|SG-*(AI|PR|AE))$/i.test(q.replace(/[\\s-]+/g, '-')) ? 'early' : 'general';
        var wait = setInterval(function () {
          if (!document.getElementById('sgps_loading')) { clearInterval(wait); open(NAMES[wanted] ? wanted : 'general'); }
        }, 400);
      }
    })();
  </script>
  <style>
    #sgps_wl { position: fixed; inset: 0; z-index: 20; display: flex; align-items: center; justify-content: center;
      padding: 16px; background: rgba(0,0,0,.6); font: 14px/1.6 Inter, system-ui, 'Segoe UI', Tahoma, sans-serif; color: #F3EFE8; }
    #sgps_wl[hidden], #sgps_wl [hidden] { display: none !important; }
    #sgps_wl form, #sgps_wl_done { position: relative; width: min(460px, 100%); max-height: calc(100vh - 32px); overflow: auto;
      background: #2A2727; border: 1px solid #443D3A; border-radius: 12px; padding: 20px 22px; box-shadow: 0 12px 40px rgba(0,0,0,.5); }
    #sgps_wl h2 { margin: 0 0 6px; font-size: 20px; color: #F3EFE8; }
    #sgps_wl p { margin: 0 0 14px; color: #C4BDB4; }
    #sgps_wl .badge { display: inline-block; margin-bottom: 8px; padding: 2px 10px; border-radius: 999px; background: #D63C32; color: #F3EFE8; font-size: 12px; }
    #sgps_wl label { display: block; margin-bottom: 10px; color: #ddd; }
    #sgps_wl input[name=name], #sgps_wl input[name=phone] { display: block; width: 100%; box-sizing: border-box; margin-top: 4px; padding: 9px 10px;
      background: #141314; color: #F3EFE8; border: 1px solid #443D3A; border-radius: 8px; font: inherit; }
    #sgps_wl input:focus { outline: 2px solid #EA993F; outline-offset: -1px; }
    #sgps_wl fieldset { border: 1px solid #443D3A; border-radius: 8px; margin: 4px 0 12px; padding: 8px 12px 2px; }
    #sgps_wl legend { padding: 0 6px; color: #EA993F; }
    #sgps_wl .chk { display: flex; gap: 8px; align-items: baseline; margin-bottom: 8px; }
    #sgps_wl .chk input { accent-color: #EA993F; }
    #sgps_wl .chk small { color: #8f8885; margin-inline-start: auto; direction: ltr; }
    #sgps_wl .consent { color: #F3EFE8; }
    #sgps_wl .err { color: #ff8a70; min-height: 1.2em; margin: 0 0 8px; }
    #sgps_wl .go { display: block; width: 100%; box-sizing: border-box; padding: 10px; border: 0; border-radius: 8px; background: #D63C32;
      color: #F3EFE8; font: inherit; font-weight: 700; text-align: center; text-decoration: none; cursor: pointer; }
    #sgps_wl .go:disabled { opacity: .6; cursor: wait; }
    #sgps_wl .x { position: absolute; top: 8px; left: 10px; background: none; border: 0; color: #EA993F; font-size: 22px; cursor: pointer; }
  </style>
"""


def device_fonts(root: Path) -> None:
    """Fonts installed on the computer, in the browser build (upstream only reads them on desktop).
    Registering a font moves upstream's shared font generation, so the font menus refresh."""
    edit(root, "crates/ui-egui/src/type_tool.rs", [(
        "/// Font families: bundled, system, and those the host serves",
        """/// HORIX: set by Type > Load Device Fonts; the web shell picks it up and asks the browser.
pub static DEVICE_FONTS_REQUESTED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);

/// HORIX: registers a font file (TTF/OTF/TTC) while the app runs. Returns its family names.
pub fn register_font(bytes: Vec<u8>) -> Vec<String> {
    photocraft_text::shared().lock().map(|mut e| e.fonts.register_font_data(bytes)).unwrap_or_default()
}

/// Font families: bundled, system, and those the host serves""")])
    edit(root, "crates/ui-egui/src/menus.rs", [
        ('    ("edit.search", "Search…", &["Edit"], Some("Cmd+F")),',
         '    ("edit.search", "Search…", &["Edit"], Some("Cmd+F")),\n'
         '    ("type.loadDeviceFonts", "Load Device Fonts…", &["Type"], None),'),
        ('| "help.about" | "help.systemInfo" | "edit.search" => true,',
         '| "help.about" | "help.systemInfo" | "edit.search" | "type.loadDeviceFonts" => true,'),
        ("""    if let Some(url) = crate::links::url_for(id) {
        return Ok(crate::links::open(app, ctx, url));
    }""", """    if let Some(url) = crate::links::url_for(id) {
        return Ok(crate::links::open(app, ctx, url));
    }
    if id == "type.loadDeviceFonts" {
        crate::type_tool::DEVICE_FONTS_REQUESTED.store(true, std::sync::atomic::Ordering::Relaxed);
        app.ui.status = "Loading the fonts installed on this computer…".into();
        return Ok(Value::Null);
    }"""),
    ])
    edit(root, "apps/photocraft-web/src/web.rs", [
        ("""        self.serve_fonts(ctx);
        self.app.logic(ctx, frame);""", """        self.serve_fonts(ctx);
        if photocraft_ui_egui::type_tool::DEVICE_FONTS_REQUESTED.swap(false, std::sync::atomic::Ordering::Relaxed) {
            call_page("sgpsLoadDeviceFonts", None);
        }
        let waitlist = photocraft_ui_egui::links::WAITLIST_REQUEST.lock().unwrap_or_else(|e| e.into_inner()).take();
        if let Some(product) = waitlist {
            call_page("sgpsOpenWaitlist", Some(&product));
        }
        self.app.logic(ctx, frame);"""),
        ("fn query() -> String {", """/// HORIX: calls `window[name](arg)` defined by the page (index.html), if it exists.
fn call_page(name: &str, arg: Option<&str>) {
    use wasm_bindgen::JsCast;
    let Some(window) = web_sys::window() else { return };
    if let Ok(f) = js_sys::Reflect::get(&window, &name.into())
        && let Some(f) = f.dyn_ref::<js_sys::Function>()
    {
        let _ = match arg {
            Some(a) => f.call1(&window, &a.into()),
            None => f.call0(&window),
        };
    }
}

/// HORIX: registers a font file read by the page (Local Font Access API). Returns the family
/// names, one per line.
#[wasm_bindgen::prelude::wasm_bindgen]
pub fn sgps_register_font(bytes: Vec<u8>) -> String {
    photocraft_ui_egui::type_tool::register_font(bytes).join("\\n")
}

fn query() -> String {"""),
    ])
    edit(root, "apps/photocraft-web/index.html", [("</body>", FONTS_SCRIPT + "</body>")])
    whatsapp = WHATSAPP.split("?")[0]
    edit(root, "apps/photocraft-web/index.html", [("</body>", WAITLIST_SCRIPT.replace("__WHATSAPP__", whatsapp) + "</body>")])


def web_page_behaviour(root: Path) -> None:
    edit(root, "apps/photocraft-web/index.html", [("</body>", KEYBOARD_SCRIPT + "</body>")])
    # A new storage key: browsers that ran the original build start from the SG - PS defaults
    # (Maro theme, Essentials workspace) instead of the old saved theme.
    edit(root, "apps/photocraft-web/src/web.rs", [
        # A new key when the defaults change, so returning visitors get them (HORIX theme).
        ('const PREFS_KEY: &str = "photocraft.preferences";', 'const PREFS_KEY: &str = "horix.preferences";'),
    ])


def web(root: Path) -> None:
    edit(root, "apps/photocraft-web/Cargo.toml", [('name = "photocraft-web"\npath = "src/main.rs"', 'name = "sg-ps"\npath = "src/main.rs"')])
    shutil.copyfile(HERE / "assets" / "horix-favicon.svg", root / "apps/photocraft-web/horix-favicon.svg")
    # The loading screen: the HORIX logo inline (it shows before anything else downloads), built from
    # the lockup's own shapes: a faint copy, a lit copy revealed by a clip, and the eye on its own.
    lockup = (HERE / "assets" / "horix-lockup.svg").read_text(encoding="utf-8")
    shapes = re.findall(r"<(?:path|polygon|rect)[^>]*/>", lockup)
    eyes = [s for s in shapes if 'fill="#EA993F"' in s]
    if len(eyes) != 1:
        sys.exit("rebrand: horix-lockup.svg: expected exactly one amber eye shape")
    body = "".join(s.replace(' fill="#F3EFE8"', "").replace(' fill="#D63C32"', ' class="x"') for s in shapes if s not in eyes)
    eye = eyes[0].replace(' fill="#EA993F"', ' class="hx-eye"')
    view = re.search(r'viewBox="([^"]+)"', lockup).group(1)
    vx, vy, vw, vh = (float(v) for v in view.split())
    loading = (
        f'<svg class="hx-mark" viewBox="{view}" data-w="{vw:g}" role="img" aria-label="HORIX">'
        f'<defs><clipPath id="hx_reveal"><rect id="hx_wipe" x="{vx:g}" y="{vy - 20:g}" width="0" height="{vh + 40:g}"/></clipPath></defs>'
        f'<g class="hx-dim">{body}</g><g class="hx-lit" clip-path="url(#hx_reveal)">{body}</g>{eye}</svg>\n'
        '    <div class="hx-desc">THE VISIONARY AI EDITOR</div>\n'
        '    <div class="hx-rule"></div>\n'
        '    <div class="hx-by">BY SABER GROUP</div>\n'
        '    <div class="hx-track"><div class="hx-bar"></div></div>\n'
        '    <p class="hx-status" id="hx_status">بنحمّل HORIX…</p>')
    edit(root, "apps/photocraft-web/index.html", [
        ('data-bin="photocraft-web"', 'data-bin="sg-ps"'),
        ("<title>PhotoCraft</title>", f'<title>{APP_NAME}</title>\n  <link data-trunk rel="icon" href="horix-favicon.svg">\n'
                                      f'  <meta name="theme-color" content="#0E0E0F">'),
        # The loading screen takes the default HORIX (Dark) theme's neutral canvas and dim text,
        # so the first frame of the app follows it without a colour jump (it read reddish).
        ("background: #262626;", "background: #0E0E0F;"),
        ("color: #b8b8b8;", "color: #96969E;"),
        ("color: #e0e0e0;", "color: #EA993F;"),
        ("<p>Loading PhotoCraft&hellip;</p>", loading),
        ("""    <p id="photocraft_stalled">This is taking longer than usual. If PhotoCraft doesn't start, its files may have failed to
      download or come from a different version of this page. <a href="">Reload</a> to try again; the browser
      console lists what failed.</p>""",
         """    <p id="photocraft_stalled">التحميل واقف من شوية. اتأكد من النت و<a href="">اعمل Reload</a>، ولو فضلت المشكلة كلّمنا.</p>"""),
        ("  </style>\n</head>", LOADER_CSS + "  </style>\n</head>"),
        ("</body>", LOADER_SCRIPT + "</body>"),
    ])
    edit(root, "apps/photocraft-web/src/web.rs", [(
        '"<p>PhotoCraft failed to start: {e:?}</p><p>A browser with WebGPU or WebGL2 is required.</p>"',
        '"<p>HORIX مقدرش يشتغل على المتصفح ده. جرّب آخر نسخة من Chrome أو Edge (محتاج WebGPU أو WebGL2).</p><p dir=\\"ltr\\">{e:?}</p>"',
    )])
    for rel in ("apps/photocraft-web/index.html", "apps/photocraft-web/src/web.rs", "apps/photocraft-web/src/main.rs"):
        path = root / rel
        text = path.read_text(encoding="utf-8")
        for old, new in (("photocraft_canvas", "sgps_canvas"), ("photocraft_loading", "sgps_loading"),
                         ("photocraft_stalled", "sgps_stalled"), ("photocraft-stalled", "sgps-stalled")):
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


LOADER_CSS = """
    /* HORIX loading screen: the start screen's own card (same canvas and dot grid, lockup, descriptor,
       red rule, "BY SABER GROUP"), so the app opens on the same picture. The logo is revealed toward the
       beak as the app downloads (real bytes, see LOADER_SCRIPT), a thin bar under it is the progress, and
       the amber eye opens when the app is ready. Inter comes from the downloads page's fonts. */
    @font-face { font-family: HorixInter; font-weight: 500; font-display: swap; src: url(fonts/inter-latin-500-normal.woff2) format('woff2'); }
    @font-face { font-family: HorixCairo; font-weight: 700; font-display: swap; src: url(fonts/cairo-arabic-700-normal.woff2) format('woff2'); }
    #photocraft_loading { font-family: HorixCairo, Cairo, 'Segoe UI', Tahoma, system-ui, sans-serif; transition: opacity .45s ease;
      background-image: radial-gradient(circle, #1C1C1F 1.3px, transparent 1.8px); background-size: 22px 22px; background-position: 11px 11px; }
    #photocraft_loading.hx-out { opacity: 0; }
    .hx-mark { display: block; width: 190px; height: auto; overflow: visible; }
    .hx-dim path, .hx-dim polygon, .hx-dim rect { fill: rgba(242, 239, 233, .07); }
    .hx-dim .x { fill: rgba(214, 60, 50, .12); }
    .hx-lit path, .hx-lit polygon, .hx-lit rect { fill: #F2EFE9; }
    .hx-lit .x { fill: #D63C32; }
    #hx_wipe { transition: width .35s cubic-bezier(.2, .8, .2, 1); }
    .hx-eye { fill: #EA993F; opacity: .55; transform-box: fill-box; transform-origin: 50% 40%; transform: scaleY(.12);
      transition: transform .55s cubic-bezier(.3, 1.6, .5, 1), opacity .3s; }
    .hx-ready .hx-eye { opacity: 1; transform: none; }
    .hx-desc { margin-top: 12px; color: #F2EFE9; font: 500 12px/1.2 HorixInter, Inter, 'Segoe UI', system-ui, sans-serif; letter-spacing: 0; direction: ltr; }
    .hx-rule { width: 28px; height: 2px; margin: 7px 0 6px; background: #D63C32; }
    .hx-by { color: #606067; font: 500 10.5px/1.2 HorixInter, Inter, 'Segoe UI', system-ui, sans-serif; direction: ltr; }
    .hx-track { position: relative; width: 160px; height: 2px; margin: 22px 0 14px; border-radius: 1px; overflow: hidden; background: #232326; }
    .hx-bar { position: absolute; inset: 0 auto 0 0; width: 0; background: #D63C32; transition: width .35s cubic-bezier(.2, .8, .2, 1); }
    .hx-busy .hx-bar { width: 100% !important; animation: hx-breathe 1.1s ease-in-out infinite; }
    @keyframes hx-breathe { 50% { opacity: .45; } }
    .hx-status { min-height: 1.6em; margin: 0 0 8px; font-size: 13px; line-height: 1.5; direction: rtl; }
    .hx-status bdi { unicode-bidi: isolate; direction: ltr; color: #606067; font: 12px HorixInter, Inter, system-ui, sans-serif; }
    /* While bytes keep arriving the "taking long" hint stays hidden; the script shows it after 15 s without progress. */
    #photocraft_loading.hx-flowing #photocraft_stalled { visibility: hidden; animation: none; }
    #photocraft_loading.hx-stuck #photocraft_stalled { visibility: visible; animation: none; }
    #photocraft_stalled { direction: rtl; }
    @media (prefers-reduced-motion: reduce) {
      #hx_wipe, .hx-bar, .hx-eye, #photocraft_loading { transition: none; }
      .hx-busy .hx-bar { animation: none; }
    }
"""

LOADER_SCRIPT = """  <script>
    // HORIX loading screen: real download progress of the WebAssembly file. The page's own loader
    // (trunk / wasm-bindgen) fetches it; fetch is wrapped for that one URL to count the bytes as they
    // arrive (already decompressed, so they compare to the file's size written at build time).
    (function () {
      var SIZE = Number('__HORIX_WASM_SIZE__') || 0;
      var box = document.getElementById('sgps_loading');
      if (!box || !window.fetch || !window.ReadableStream) return;
      var wipe = document.getElementById('hx_wipe'), mark = wipe && wipe.ownerSVGElement;
      var bar = box.querySelector('.hx-bar'), status = document.getElementById('hx_status');
      var full = mark ? Number(mark.getAttribute('data-w')) : 0, last = Date.now();
      function mb(n) { return (n / 1048576).toFixed(1); }
      function show(got, total) {
        last = Date.now();
        box.classList.add('hx-flowing'); box.classList.remove('hx-stuck');
        var p = total ? Math.min(1, got / total) : 0;
        if (wipe) wipe.setAttribute('width', String(full * p + 2));
        if (bar) bar.style.width = (p * 100).toFixed(1) + '%';
        // A percentage: the bytes counted here are decompressed, so megabytes would not match the download.
        status.innerHTML = 'بنحمّل HORIX… <bdi>' + (total ? Math.floor(p * 100) + '%' : mb(got) + ' MB') + '</bdi>';
      }
      function busy() {
        if (wipe) wipe.setAttribute('width', String(full + 2));
        box.classList.add('hx-busy');
        status.textContent = 'بنجهّز الأدوات…';
      }
      var watch = setInterval(function () {
        if (!document.body.contains(box)) return clearInterval(watch);
        if (box.classList.contains('hx-flowing') && !box.classList.contains('hx-busy') && Date.now() - last > 15000) {
          box.classList.remove('hx-flowing'); box.classList.add('hx-stuck');
        }
      }, 1000);
      var realFetch = window.fetch;
      window.fetch = function (input, init) {
        var url = typeof input === 'string' ? input : (input && input.url) || '';
        var res = realFetch.apply(this, arguments);
        if (!/_bg\\.wasm(\\?|$)/.test(url)) return res;
        return res.then(function (r) {
          if (!r.ok || !r.body) return r;
          var total = SIZE || Number(r.headers.get('Content-Length')) || 0, got = 0, reader = r.body.getReader();
          show(0, total);
          var counted = new ReadableStream({
            pull: function (ctl) {
              return reader.read().then(function (c) {
                if (c.done) { busy(); ctl.close(); return; }
                got += c.value.byteLength; show(got, total); ctl.enqueue(c.value);
              }, function (e) { ctl.error(e); });
            },
            cancel: function (why) { return reader.cancel(why); }
          });
          return new Response(counted, { status: r.status, statusText: r.statusText, headers: r.headers });
        });
      };
      // The app removes the loading screen when it starts: a copy stays a moment so the eye opens
      // and the screen fades out over the app.
      new MutationObserver(function (_, obs) {
        if (document.body.contains(box)) return;
        obs.disconnect(); window.fetch = realFetch;
        if (box.querySelector('.hx-mark') === null) return;
        var out = box.cloneNode(true);
        out.removeAttribute('id'); out.id = 'hx_loading_out';
        out.className = 'hx-flowing hx-busy';
        out.style.cssText = 'position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;' +
          'background:#0E0E0F radial-gradient(circle, #1C1C1F 1.3px, transparent 1.8px) 11px 11px / 22px 22px;color:#96969E;' +
          'font:14px HorixCairo,Cairo,system-ui,sans-serif;pointer-events:none;z-index:5;transition:opacity .45s ease';
        var st = out.querySelector('.hx-status'); if (st) st.textContent = 'جاهز';
        var stalled = out.querySelector('#sgps_stalled'); if (stalled) { stalled.removeAttribute('id'); stalled.style.visibility = 'hidden'; }
        document.body.appendChild(out);
        requestAnimationFrame(function () { out.classList.add('hx-ready'); });
        setTimeout(function () { out.style.opacity = '0'; }, 650);
        setTimeout(function () { out.remove(); }, 1150);
      }).observe(document.body, { childList: true });
    })();
  </script>
"""

NAME_RE = re.compile(r"(?<![A-Za-z0-9_])Photo[cC]raft(?![A-Za-z0-9_])")


def rename_everywhere(root: Path) -> int:
    """PhotoCraft/Photocraft as a standalone word -> SG - PS, in sources, translations and the web page.
    Identifiers (PhotocraftApp, photocraft_engine, ...) are untouched: they never reach the UI."""
    count = 0
    for path in list(root.glob("crates/**/*.rs")) + list(root.glob("apps/**/*.rs")) + \
            list(root.glob("crates/ui-egui/src/i18n/*.tsv")) + [root / "apps/photocraft-web/index.html"]:
        text = path.read_text(encoding="utf-8")
        new, n = NAME_RE.subn(APP_NAME, text)
        if n:
            path.write_text(new, encoding="utf-8")
            count += n
    return count


def desktop(root: Path) -> None:
    """The native desktop app (Windows/macOS): HORIX icons, Saber names, own data folder."""
    # Every upstream app icon becomes HORIX's, by kind and size (assets/app-icon/, made from
    # assets/desktop/horix-1024.png): the title-bar mark (brand.rs), installers, the window icon.
    icons = HERE / "assets" / "app-icon"
    replaced = 0
    for f in sorted((root / "assets/app-icon").rglob("*")):
        size = re.search(r"(\d+)x\1|-(\d+)\.png$", f.as_posix())
        if f.suffix == ".png" and size:
            src = icons / f"icon-{size.group(1) or size.group(2)}.png"
        elif f.suffix in (".ico", ".icns"):
            src = icons / f"icon{f.suffix}"
        elif f.suffix == ".svg":
            src = icons / "icon.svg"
        else:
            continue
        if not src.is_file():
            sys.exit(f"rebrand: no HORIX icon for {f.relative_to(root)}")
        shutil.copyfile(src, f)
        replaced += 1
    if replaced < 5:
        sys.exit(f"rebrand: assets/app-icon: only {replaced} icons replaced")
    edit(root, "apps/photocraft/build.rs", [
        ('.set("CompanyName", "Learning Machines LLC")', '.set("CompanyName", "Saber Group Academy")'),
        ('.set("OriginalFilename", "photocraft.exe")', '.set("OriginalFilename", "HORIX.exe")'),
        ('.set("InternalName", "photocraft")', '.set("InternalName", "HORIX")'),
    ])
    edit(root, "apps/photocraft/src/app_dirs.rs", [
        ('pub const PORTABLE_DATA_DIR: &str = "PhotoCraftData";', 'pub const PORTABLE_DATA_DIR: &str = "HORIX-Data";'),
        ("""    let platform = platform_dir(&env);
    let Some((exe_dir, marker)) = exe_dir.and_then(|d| portable_marker(d).map(|m| (d, m))) else {
        return DataDir { dir: platform, mode: Mode::Platform, warning: None };
    };""", """    let platform = platform_dir(&env);
    // HORIX's Windows ZIP is compiled as portable, so it needs no marker file beside the EXE.
    // Other native builds retain the upstream marker behaviour.
    let packaged_portable = cfg!(windows) && option_env!("HORIX_PORTABLE") == Some("1");
    let Some((exe_dir, marker)) = exe_dir.and_then(|d| {
        portable_marker(d).map(|m| (d, Some(m))).or_else(|| packaged_portable.then_some((d, None)))
    }) else {
        return DataDir { dir: platform, mode: Mode::Platform, warning: None };
    };"""),
        ("""            let warning =
                format!("portable mode ({} found) but {} isn't writable ({e}); settings are kept in {fallback} instead", marker.display(), data.display());""", """            let source = marker.as_ref().map_or_else(|| "portable Windows build".to_string(), |m| format!("{} found", m.display()));
            let warning =
                format!("portable mode ({source}) but {} isn't writable ({e}); settings are kept in {fallback} instead", data.display());"""),
    ])
    notices = [
        ("HORIX application core — MIT License", root / "LICENSE-MIT"),
        ("Upstream notice", root / "NOTICE"),
        ("Inter font — SIL Open Font License 1.1", root / "assets/fonts/OFL-Inter.txt"),
        ("JetBrains Mono font — SIL Open Font License 1.1", root / "assets/fonts/OFL-JetBrainsMono.txt"),
        ("Lucide icons — ISC License", root / "assets/icons/LICENSE-lucide.txt"),
        ("SCOWL dictionaries", root / "assets/dict/LICENSE-SCOWL.txt"),
        ("Barlow Condensed font — SIL Open Font License 1.1", HERE / "assets/fonts/OFL-BarlowCondensed.txt"),
    ]
    licence_text = "HORIX OPEN-SOURCE LICENCES AND NOTICES\n\n" + "\n\n".join(
        f"{'=' * 72}\n{title}\n{'=' * 72}\n\n{path.read_text(encoding='utf-8').strip()}"
        for title, path in notices
    ) + "\n"
    (root / "crates/ui-egui/src/horix_licenses.txt").write_text(licence_text, encoding="utf-8")
    edit(root, "crates/ui-egui/src/dialogs.rs", [
        ('            ui.weak("Built on open-source software (MIT / Apache-2.0). Licence texts ship with the app.");',
         '            ui.weak("Built on open-source software. Required licence texts are included in the app.");\n'
         '            ui.add_space(6.0);\n'
         '            ui.collapsing("Open-source licences", |ui| {\n'
         '                egui::ScrollArea::vertical().max_height(260.0).show(ui, |ui| {\n'
         '                    ui.add(egui::Label::new(egui::RichText::new(include_str!("horix_licenses.txt")).font(crate::theme::mono(10.0))).selectable(true));\n'
         '                });\n'
         '            });'),
    ])
    edit(root, "apps/photocraft/src/main.rs", [
        ('const APP_ID: &str = "ai.storyteller.photocraft";', 'const APP_ID: &str = "com.sabergroup.sgps";'),
    ])


def web_place(root: Path) -> None:
    """File > Place Embedded in the browser. Upstream's picker is asynchronous on every platform
    and places the picked bytes, but the command is still greyed out where there is no file system
    (`native_doc`); with an open document it works on the web too."""
    edit(root, "crates/engine/src/file_cmds.rs", [(
        """(default: Preferences > General > Always Create Smart Objects When Placing),"center":[x,y]?}"##,
            native_doc,
            |s, p| place(s, p, false)""",
        """(default: Preferences > General > Always Create Smart Objects When Placing),"center":[x,y]?}"##,
            has_doc,
            |s, p| place(s, p, false)""")])


def drop_old_translations(root: Path) -> int:
    """Translation rows for the removed ArtCraft/Discord menu items (and the translator notes that
    name ArtCraft) are compiled into the app even though nothing shows them: drop them."""
    dropped = 0
    for path in root.glob("crates/ui-egui/src/i18n/*.tsv"):
        lines = path.read_text(encoding="utf-8").split("\n")
        keep = [l for l in lines if not re.search(r"ArtCraft|Discord", l)]
        dropped += len(lines) - len(keep)
        path.write_text("\n".join(keep), encoding="utf-8")
    return dropped


def check(root: Path) -> None:
    """No ArtCraft/Discord string literal may remain in UI code."""
    bad = []
    for path in list(root.glob("crates/ui-egui/src/**/*.rs")) + list(root.glob("apps/photocraft-web/**/*")):
        if not path.is_file() or path.suffix not in {".rs", ".html"}:
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            code = line.split("//")[0] if not line.strip().startswith('"') else line
            if re.search(r'"[^"]*(ArtCraft|artcraft|discord\.gg|storytold|Discord)[^"]*"', code) and "#[test]" not in line:
                bad.append(f"{path.relative_to(root)}:{n}: {line.strip()}")
    # Unit tests inside the files still mention the old links; they are not compiled into the app.
    bad = [b for b in bad if "assert" not in b and "help.discord\", \"https://discord" not in b]
    if bad:
        print("rebrand: remaining brand strings (check they are test-only):\n" + "\n".join(bad))


def selection_quality(root: Path) -> None:
    """Spend more pixels on native Select Subject (the classic fallback when the AI can't load).
    Quick Selection is upstream's rewrite (0.9.0, measured against Photoshop): left as it is."""
    edit(root, "crates/algo/src/segment/subject.rs", [(
        "/// Working-resolution budget (pixels).\npub const WORK_PX: usize = 110_000;",
        "/// The browser keeps the conservative budget; native HORIX resolves finer subject boundaries.\n"
        "#[cfg(target_arch = \"wasm32\")]\n"
        "pub const WORK_PX: usize = 110_000;\n"
        "#[cfg(not(target_arch = \"wasm32\"))]\n"
        "pub const WORK_PX: usize = 220_000;",
    )])


CRASH_SCRIPT = """  <script>
    // SG - PS: if the app stops (an internal error or the browser running out of memory), say so
    // instead of leaving a frozen canvas, and show the technical details to send to the team.
    (function () {
      var shown = false;
      function show(detail) {
        if (shown) return; shown = true;
        var d = document.createElement('div');
        d.id = 'sgps_crash'; d.dir = 'rtl';
        d.innerHTML = '<div class="box"><h2>البرنامج وقف بسبب مشكلة 😕</h2>' +
          '<p>اعمل <b>Reload</b> للصفحة وكمّل. لو المشكلة اتكررت صوّر الرسالة دي وابعتهالنا على واتساب عشان نصلّحها.</p>' +
          '<pre></pre><div class="row"><button type="button" data-r>Reload</button><a target="_blank" rel="noopener">كلّمنا على واتساب</a></div></div>';
        d.querySelector('pre').textContent = String(detail || '').slice(0, 1500);
        d.querySelector('[data-r]').onclick = function () { location.reload(); };
        d.querySelector('a').href = '__WHATSAPP__';
        document.body.appendChild(d);
      }
      var origError = console.error;
      console.error = function () {
        try {
          var text = Array.prototype.join.call(arguments, ' ');
          if (/panicked at/.test(text)) show(text);
        } catch (e) {}
        return origError.apply(console, arguments);
      };
      function fatal(e) {
        var msg = (e && (e.message || e.reason && e.reason.message)) || '';
        var stack = (e && (e.error && e.error.stack || e.reason && e.reason.stack)) || '';
        if (/RuntimeError|unreachable|out of memory|Out of memory/i.test(msg + ' ' + stack)) show(msg + '\\n' + stack);
      }
      window.addEventListener('error', fatal);
      window.addEventListener('unhandledrejection', fatal);
    })();
  </script>
  <style>
    #sgps_crash { position: fixed; inset: 0; z-index: 50; display: flex; align-items: center; justify-content: center;
      padding: 16px; background: rgba(0,0,0,.7); font: 14px/1.6 Inter, system-ui, 'Segoe UI', Tahoma, sans-serif; color: #F3EFE8; }
    #sgps_crash .box { width: min(520px, 100%); background: #2A2727; border: 1px solid #443D3A; border-radius: 12px; padding: 20px 22px; }
    #sgps_crash h2 { margin: 0 0 6px; font-size: 20px; color: #F3EFE8; }
    #sgps_crash p { margin: 0 0 10px; color: #C4BDB4; }
    #sgps_crash pre { direction: ltr; text-align: left; max-height: 160px; overflow: auto; white-space: pre-wrap; word-break: break-all;
      background: #141314; border: 1px solid #443D3A; border-radius: 8px; padding: 8px; font-size: 11px; color: #ff8a70; }
    #sgps_crash .row { display: flex; gap: 10px; }
    #sgps_crash button, #sgps_crash a { flex: 1; padding: 10px; border-radius: 8px; border: 0; background: #D63C32; color: #F3EFE8;
      font: inherit; font-weight: 700; text-align: center; text-decoration: none; cursor: pointer; }
    #sgps_crash a { background: #3A3535; }
  </style>
"""


def stability(root: Path) -> None:
    """Crash safety on the web and desktop. (Upstream 0.9 commits an open Free Transform before other
    edits and deletes the layer on Delete, which HORIX used to patch in here.)"""
    edit(root, "crates/engine/src/prefs.rs", [
        # The browser has at most 4 GiB for the app: History must trim itself well before that.
        ("""    pub fn history_budget_bytes(&self) -> usize {
        (self.memory_usage_mb as usize).saturating_mul(1 << 20)
    }""", """    pub fn history_budget_bytes(&self) -> usize {
        let mb = self.memory_usage_mb as usize;
        // SG - PS: wasm32 has at most 4 GiB; keep pixels + History well below it.
        #[cfg(target_arch = "wasm32")]
        let mb = mb.min(1536);
        mb.saturating_mul(1 << 20)
    }"""),
        # Desktop crash recovery loses at most a few minutes of work.
        ("            autosave_minutes: 10,", "            autosave_minutes: 3,"),
    ])
    edit(root, "apps/photocraft-web/index.html", [("</body>", CRASH_SCRIPT.replace("__WHATSAPP__", WHATSAPP) + "</body>")])


def version(root: Path) -> None:
    """HORIX's own version (apps/sg-ps/VERSION, e.g. 0.2), with the CI build number as its last
    part (0.2.57), in About, System Info, --version and on the start screen. Every change that
    ships moves VERSION up one step (0.3, 0.4, ...); see CHANGELOG.md."""
    v = (HERE / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+", v):
        sys.exit(f"rebrand: VERSION must look like 0.2, not {v!r}")
    edit(root, "crates/engine/src/build_info.rs", [(
        "pub fn long_version() -> String {\n    format_long(VERSION, short_sha(), build_date())\n}",
        f"/// HORIX's version (apps/sg-ps/VERSION); CI adds its build number: `{v}.57`.\n"
        f"pub const HORIX_VERSION: &str = \"{v}\";\n\n"
        "/// `0.2.57`, or `0.2` for a build without a build number.\n"
        "pub fn horix_version() -> String {\n"
        "    match option_env!(\"HORIX_BUILD_NUMBER\").map(str::trim).filter(|s| !s.is_empty()) {\n"
        "        Some(n) => format!(\"{HORIX_VERSION}.{n}\"),\n"
        "        None => HORIX_VERSION.to_string(),\n"
        "    }\n"
        "}\n\n"
        "pub fn long_version() -> String {\n    format_long(&horix_version(), short_sha(), build_date())\n}",
    )])
    edit(root, "crates/ui-egui/src/canvas.rs", [(
        'ui.label(egui::RichText::new("BY SABER GROUP").font(crate::theme::medium(10.5)).color(t.text_faint));',
        'ui.label(egui::RichText::new("BY SABER GROUP").font(crate::theme::medium(10.5)).color(t.text_faint));\n'
        '            ui.label(egui::RichText::new(format!("v{}", photocraft_engine::build_info::horix_version())).size(10.0).color(t.text_faint));',
    )])


def apply_patches(root: Path) -> None:
    """Unified diffs in apps/sg-ps/patches/ (made against the rebranded tree), applied in name order."""
    for diff in sorted((HERE / "patches").glob("*.diff")):
        # Normalise line endings (a Windows checkout may hand us CRLF) and apply from stdin, so the
        # patch is read the same everywhere.
        data = diff.read_bytes().replace(b"\r\n", b"\n")
        # The work dir may sit inside another git repository (CI builds in .sgps-build/ of this
        # repo). There `git apply` resolves the paths against that repository's root and silently
        # skips every file outside the current directory, i.e. all of them. The ceiling stops git
        # from finding the outer repository, and --verbose lets a skipped file fail the build.
        env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(Path(root).resolve().parent)}
        r = subprocess.run(["git", "apply", "--verbose", "--whitespace=nowarn", "-p1", "-"], cwd=root, input=data, capture_output=True, env=env)
        err = r.stderr.decode(errors="replace")
        if r.returncode != 0 or "Skipped patch" in err:
            sys.exit(f"rebrand: patch {diff.name} does not apply:\n{err}")
        print(f"rebrand: applied {diff.name}")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1]).resolve()
    if not (root / "crates/ui-egui/src/links.rs").is_file():
        sys.exit(f"rebrand: {root} is not a PhotoCraft source tree")
    links(root)
    menus(root)
    title_bar(root)
    logo(root)
    theme(root)
    full_tool_options(root)
    better_select_subject(root)
    plain_background_subject(root)
    web(root)
    web_page_behaviour(root)
    device_fonts(root)
    n = rename_everywhere(root)
    drop_old_translations(root)
    desktop(root)
    web_place(root)
    selection_quality(root)
    stability(root)
    version(root)
    apply_patches(root)
    check(root)
    print(f"rebrand: done ({n} name replacements)")


if __name__ == "__main__":
    main()
