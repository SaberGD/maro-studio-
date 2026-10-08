#!/usr/bin/env python3
"""Rebrand an unpacked PhotoCraft source tree as SG - PS (Saber Group).

Usage: python3 -I rebrand.py <path-to-photocraft-source>

Every edit is an exact find/replace that must match, so an upstream change that moves the code
fails loudly here instead of silently shipping the old branding. Re-run on a fresh copy of the
source; the script is not meant to run twice on the same tree.

What it changes (UI only; licence files are kept as the licences require):
  - App name "PhotoCraft" -> "SG - PS" in every user-visible string and translation.
  - Removes the ArtCraft Discord, website and GitHub links; Help/start-screen links go to Saber.
  - New Maro logo on the start screen, About dialog and browser tab.
  - Maro colour theme (dark, red-orange accent) as the default theme.
  - Full tool options bar in every theme (upstream shows it only in the Pro themes).
  - Select Subject: spatial prior around the salient mass (see segeval/), fewer leaks into busy
    backgrounds.
  - Web build output renamed to sg-ps-*.js / sg-ps-*_bg.wasm.
"""

import re
import shutil
import sys
from pathlib import Path

APP_NAME = "SG - PS"
SABER_SITE = "https://sabergroupacademy.com"
APP_SITE = "https://studio.engsaber.space"
FACEBOOK = "https://www.facebook.com/SABERGROUP.Courses/"
# WhatsApp with a ready message: "Hello, I am coming from SG - PS and want to know about the courses and services".
WHATSAPP = ("https://wa.me/201103221873?text=%D9%85%D8%B1%D8%AD%D8%A8%D9%8B%D8%A7%D8%8C%20%D8%AC%D8%A7%D9%8A%20%D9%85%D9%86%20"
            "SG%20-%20PS%20%D9%88%D8%B9%D8%A7%D9%8A%D8%B2%20%D8%A3%D8%B9%D8%B1%D9%81%20%D8%B9%D9%86%20%D8%A7%D9%84%D9%83%D9%88%D8%B1%D8%B3%D8%A7%D8%AA%20"
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


def links(root: Path) -> None:
    edit(root, "crates/ui-egui/src/links.rs", [
        ('pub const DISCORD: &str = "https://discord.gg/artcraft";', f'pub const DISCORD: &str = "{FACEBOOK}";\npub const CONTACT: &str = "{WHATSAPP}";'),
        ('pub const ARTCRAFT_WEBSITE: &str = "https://getartcraft.com";', f'pub const ARTCRAFT_WEBSITE: &str = "{SABER_SITE}";'),
        ('pub const APP_PAGE: &str = "https://getartcraft.com/apps/photocraft";', f'pub const APP_PAGE: &str = "{APP_SITE}";'),
        ('pub const GITHUB: &str = "https://github.com/storytold/photocraft";', f'pub const GITHUB: &str = "{SABER_SITE}";'),
        ('pub const ISSUES: &str = "https://github.com/storytold/photocraft/issues";', f'pub const ISSUES: &str = "{SABER_SITE}";'),
        (
            '&[("help.discord", DISCORD), ("help.website", APP_PAGE), ("help.artcraftWebsite", ARTCRAFT_WEBSITE), ("help.github", GITHUB), ("help.reportIssue", ISSUES)];',
            '&[("help.discord", DISCORD), ("help.contact", CONTACT), ("help.website", APP_PAGE)];',
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
        ('("help.discord", "Join the ArtCraft Discord…", &["Help"], None),', '("help.discord", "Saber Group Academy on Facebook", &["Help"], None),\n    ("help.contact", "Contact Us: Courses & Services…", &["Help"], None),'),
        ('("help.website", "PhotoCraft Website", &["Help"], None),', f'("help.website", "{APP_NAME} Website", &["Help"], None),'),
        ('    ("help.artcraftWebsite", "ArtCraft Website", &["Help"], None),\n', ""),
        ('    ("help.github", "PhotoCraft on GitHub", &["Help"], None),\n', ""),
        ('    ("help.reportIssue", "Report an Issue…", &["Help"], None),\n', ""),
        ('("window.theme.pro", "Pro Theme", &["Window", "Theme"], None),', '("window.theme.pro", "Maro Theme", &["Window", "Theme"], None),'),
    ])


def title_bar(root: Path) -> None:
    # The title-bar Discord button goes; nothing replaces it.
    remove_block(root, "crates/ui-egui/src/panels.rs", "// Always one click away: the community Discord.",
                 "                        }")


def logo(root: Path) -> None:
    shutil.copyfile(HERE / "assets" / "sg-ps-logo.svg", root / "crates/ui-egui/src/sg_ps_logo.svg")
    edit(root, "crates/ui-egui/src/links.rs", [
        ("pub fn url_for(", """/// SG - PS: "Contact us" (WhatsApp, courses and services), next to the Facebook button.
pub fn contact_button(app: &mut PhotocraftApp, ui: &mut egui::Ui, min_width: f32) -> egui::Response {
    let r = crate::widgets::secondary_button(ui, tl!("Contact us"), min_width).on_hover_text(tl!("Courses and services: chat with us on WhatsApp"));
    if r.clicked() {
        open(app, ui.ctx(), CONTACT);
    }
    r
}

/// SG - PS: the next apps of the suite, announced on the start screen.
pub fn coming_soon(ui: &mut egui::Ui) {
    let t = crate::theme::Tokens::get(ui.ctx());
    ui.label(egui::RichText::new(tl!("COMING SOON")).size(11.0).strong().color(t.accent));
    ui.add_space(6.0);
    let items = [("SG - AI", tl!("Vector design")), ("SG - PR", tl!("Video editing")), ("SG - AE", tl!("Motion graphics"))];
    let (w, gap) = (132.0, 10.0);
    ui.horizontal(|ui| {
        ui.add_space(((ui.available_width() - (3.0 * w + 2.0 * gap)) / 2.0).max(0.0));
        ui.spacing_mut().item_spacing.x = gap;
        for (name, what) in items {
            egui::Frame::NONE
                .stroke(egui::Stroke::new(1.0, t.accent_border))
                .corner_radius(t.radius)
                .inner_margin(egui::Margin::symmetric(8, 6))
                .show(ui, |ui| {
                    ui.set_width(w - 18.0);
                    ui.vertical_centered(|ui| {
                        ui.label(egui::RichText::new(name).size(14.0).strong().color(t.text));
                        ui.label(egui::RichText::new(what).size(11.0).color(t.text_dim));
                    });
                });
        }
    });
}

/// The SG - PS (Maro) logo, rendered by the egui_extras SVG loader.
pub fn logo(size: f32) -> egui::Image<'static> {
    egui::Image::from_bytes("bytes://sg-ps-logo.svg", include_bytes!("sg_ps_logo.svg").as_slice()).fit_to_exact_size(egui::Vec2::splat(size))
}

pub fn url_for("""),
    ])
    edit(root, "crates/ui-egui/src/canvas.rs", [
        ("let card = Rect::from_center_size(area.center(), egui::vec2(460.0, 330.0 + recent_h));",
         "let card = Rect::from_center_size(area.center(), egui::vec2(460.0, 520.0 + recent_h));"),
        ("""            crate::links::discord_button(app, ui, 190.0);
            ui.add_space(10.0);
            crate::links::link_row(app, ui);""",
         """            ui.horizontal(|ui| {
                ui.add_space(((card.width() - 2.0 * 190.0 - 12.0) / 2.0).max(0.0));
                ui.spacing_mut().item_spacing.x = 12.0;
                crate::links::discord_button(app, ui, 190.0);
                crate::links::contact_button(app, ui, 190.0);
            });
            ui.add_space(10.0);
            crate::links::link_row(app, ui);
            ui.add_space(22.0);
            crate::links::coming_soon(ui);"""),
        ("""        ui.vertical_centered(|ui| {
            ui.horizontal(|ui| {
                let title = ui.painter().layout_no_wrap(tl!("PhotoCraft").into()""",
         """        ui.vertical_centered(|ui| {
            ui.add(crate::links::logo(80.0));
            ui.add_space(8.0);
            ui.horizontal(|ui| {
                let title = ui.painter().layout_no_wrap(tl!("PhotoCraft").into()"""),
        ('let by = ui.painter().layout_no_wrap("open source".into()', 'let by = ui.painter().layout_no_wrap("by Saber Group".into()'),
    ])
    edit(root, "crates/ui-egui/src/dialogs.rs", [
        ('ui.label(tl!("PhotoCraft — an open-source, native image editor written in Rust."));',
         'ui.vertical_centered(|ui| ui.add(crate::links::logo(64.0)));\n'
         '                    ui.add_space(6.0);\n'
         '                    ui.label(tl!("PhotoCraft — the image editor of Saber Group Academy."));'),
        ('ui.weak("egui · wgpu · photocraft-engine");',
         'ui.weak("Built on open-source software (MIT / Apache-2.0). Licence texts ship with the app.");'),
    ])


def theme(root: Path) -> None:
    rel = "crates/ui-egui/src/theme.rs"
    edit(root, rel, [
        ("    Pro,\n    /// Photoshop's default (second) interface brightness: #535353 panels, #282828 canvas (default).\n    #[default]\n    ProMedium,",
         "    #[default]\n    Pro,\n    /// Photoshop's default (second) interface brightness: #535353 panels, #282828 canvas.\n    ProMedium,"),
        ('ThemeKind::Pro => "Pro (Dark)",', 'ThemeKind::Pro => "Maro (Dark)",'),
        ('"pro" | "prodark" | "photoshop" | "dark" =>', '"pro" | "prodark" | "photoshop" | "dark" | "maro" =>'),
    ])
    # Maro palette: charcoal #151515/#1c1c1c, red-orange #c4321f/#e85c3b, amber #fbbf24.
    path = root / rel
    text = path.read_text(encoding="utf-8")
    start = text.index("            ThemeKind::Pro => Tokens {")
    end = text.index("            ThemeKind::Studio => Tokens {")
    maro = """            ThemeKind::Pro => Tokens {
                kind,
                chrome: Color32::from_rgb(28, 28, 28),
                canvas: Color32::from_rgb(18, 18, 18),
                canvas_dot: Color32::from_rgb(18, 18, 18),
                dock: Color32::from_rgb(15, 15, 15),
                card: Color32::from_rgb(28, 28, 28),
                card_border: Color32::from_rgb(15, 15, 15),
                field: Color32::from_rgb(21, 21, 21),
                field_border: Color32::from_rgb(70, 54, 50),
                hover: Color32::from_rgb(52, 40, 37),
                pressed: Color32::from_rgb(72, 46, 40),
                text: Color32::from_rgb(236, 236, 236),
                text_dim: Color32::from_rgb(190, 184, 182),
                text_faint: Color32::from_rgb(134, 127, 125),
                icon: Color32::from_rgb(218, 212, 210),
                accent: Color32::from_rgb(232, 92, 59),
                accent_soft: Color32::from_rgb(74, 44, 37),
                accent_border: Color32::from_rgb(232, 92, 59),
                accent_text: Color32::WHITE,
                separator: Color32::from_rgb(12, 12, 12),
                shadow: Color32::from_black_alpha(160),
                primary_bg: Color32::from_rgb(196, 50, 31),
                primary_text: Color32::WHITE,
                danger: Color32::from_rgb(255, 112, 112),
                warning: Color32::from_rgb(251, 191, 36),
                radius_sm: 4.0,
                radius: 6.0,
                radius_lg: 8.0,
                bevel: false,
                pro: true,
                tab_strip: Color32::from_rgb(21, 21, 21),
                row_selected: Color32::from_rgb(92, 40, 30),
            },
"""
    path.write_text(text[:start] + maro + text[end:], encoding="utf-8")
    edit(root, "crates/engine/src/prefs.rs", [
        ('Classic = "classic" } default ProMedium);', 'Classic = "classic" } default Pro);'),
        ("            theme: Theme::ProMedium,", "            theme: Theme::Pro,"),
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
    if n != 8:
        sys.exit(f"rebrand: {rel}: expected 8 Pro-only option arms, found {n}")
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
        var k = (e.key || '').toLowerCase();
        if (k === 'f12') return;
        if (k === 'f11') { e.preventDefault(); toggleFullscreen(); return; }
        var cmd = e.ctrlKey || e.metaKey;
        if (cmd && !e.altKey && clipboard[k]) return;
        if (cmd || e.altKey || k === 'alt' || /^f([1-9]|10)$/.test(k)) e.preventDefault();
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
      background: #1c1c1c; color: #ececec; border: 1px solid #c4321f; border-radius: 8px;
      font: 13px/1.5 system-ui, 'Segoe UI', Tahoma, sans-serif; box-shadow: 0 6px 24px rgba(0,0,0,.45); }
    #sgps_hint b { color: #fbbf24; }
    #sgps_hint button { background: none; border: 0; color: #e85c3b; font-size: 18px; cursor: pointer; padding: 0 4px; }
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
      padding: 10px 14px; background: #1c1c1c; color: #ececec; border: 1px solid #c4321f; border-radius: 8px;
      font: 13px/1.5 system-ui, 'Segoe UI', Tahoma, sans-serif; box-shadow: 0 6px 24px rgba(0,0,0,.45); }
    #sgps_toast b { color: #fbbf24; }
  </style>
"""


def device_fonts(root: Path) -> None:
    """Fonts installed on the computer, in the browser build (upstream only reads them on desktop)."""
    edit(root, "crates/ui-egui/src/type_tool.rs", [(
        """/// Font families (bundled + system), cached for the process.
pub fn families() -> &'static [String] {
    static FAMILIES: std::sync::OnceLock<Vec<String>> = std::sync::OnceLock::new();
    FAMILIES.get_or_init(|| photocraft_text::shared().lock().map(|mut e| e.fonts.families()).unwrap_or_default())
}""",
        """/// SG - PS: bumped whenever fonts are added while the app runs (device fonts in the browser).
pub static FONTS_GENERATION: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
/// SG - PS: set by Type > Load Device Fonts; the web shell picks it up and asks the browser.
pub static DEVICE_FONTS_REQUESTED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);

/// SG - PS: registers a font file (TTF/OTF/TTC) while the app runs. Returns its family names.
pub fn register_font(bytes: Vec<u8>) -> Vec<String> {
    let names = photocraft_text::shared().lock().map(|mut e| e.fonts.register_font_data(bytes)).unwrap_or_default();
    FONTS_GENERATION.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    names
}

/// Font families (bundled + system + device fonts added at run time). Rebuilt when fonts are added.
pub fn families() -> &'static [String] {
    static FAMILIES: std::sync::Mutex<(u64, &'static [String])> = std::sync::Mutex::new((u64::MAX, &[]));
    let generation = FONTS_GENERATION.load(std::sync::atomic::Ordering::Relaxed);
    let mut cached = FAMILIES.lock().unwrap_or_else(|e| e.into_inner());
    if cached.0 != generation {
        let list = photocraft_text::shared().lock().map(|mut e| e.fonts.families()).unwrap_or_default();
        *cached = (generation, Box::leak(list.into_boxed_slice()));
    }
    cached.1
}""")])
    edit(root, "crates/ui-egui/src/menus.rs", [
        ('    ("edit.search", "Search…", &["Edit"], Some("Cmd+K")),',
         '    ("edit.search", "Search…", &["Edit"], Some("Cmd+K")),\n'
         '    ("type.loadDeviceFonts", "Load Device Fonts…", &["Type"], None),'),
        ('"file.open" | "file.exit" | "file.clearRecent" | "help.about" | "help.systemInfo" | "edit.search" => true,',
         '"file.open" | "file.exit" | "file.clearRecent" | "help.about" | "help.systemInfo" | "edit.search" | "type.loadDeviceFonts" => true,'),
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
        ("""        self.app.logic(ctx, frame);
    }""", """        if photocraft_ui_egui::type_tool::DEVICE_FONTS_REQUESTED.swap(false, std::sync::atomic::Ordering::Relaxed) {
            call_page("sgpsLoadDeviceFonts");
        }
        self.app.logic(ctx, frame);
    }"""),
        ("fn query() -> String {", """/// SG - PS: calls `window[name]()` defined by the page (index.html), if it exists.
fn call_page(name: &str) {
    use wasm_bindgen::JsCast;
    let Some(window) = web_sys::window() else { return };
    if let Ok(f) = js_sys::Reflect::get(&window, &name.into())
        && let Some(f) = f.dyn_ref::<js_sys::Function>()
    {
        let _ = f.call0(&window);
    }
}

/// SG - PS: registers a font file read by the page (Local Font Access API). Returns the family
/// names, one per line.
#[wasm_bindgen::prelude::wasm_bindgen]
pub fn sgps_register_font(bytes: Vec<u8>) -> String {
    photocraft_ui_egui::type_tool::register_font(bytes).join("\\n")
}

fn query() -> String {"""),
    ])
    edit(root, "apps/photocraft-web/index.html", [("</body>", FONTS_SCRIPT + "</body>")])


def web_page_behaviour(root: Path) -> None:
    edit(root, "apps/photocraft-web/index.html", [("</body>", KEYBOARD_SCRIPT + "</body>")])
    # A new storage key: browsers that ran the original build start from the SG - PS defaults
    # (Maro theme, Essentials workspace) instead of the old saved theme.
    edit(root, "apps/photocraft-web/src/web.rs", [
        ('const PREFS_KEY: &str = "photocraft.preferences";', 'const PREFS_KEY: &str = "sgps.preferences";'),
    ])


def web(root: Path) -> None:
    edit(root, "apps/photocraft-web/Cargo.toml", [('name = "photocraft-web"\npath = "src/main.rs"', 'name = "sg-ps"\npath = "src/main.rs"')])
    shutil.copyfile(HERE / "assets" / "sg-ps-logo.svg", root / "apps/photocraft-web/sg-ps-logo.svg")
    edit(root, "apps/photocraft-web/index.html", [
        ('data-bin="photocraft-web"', 'data-bin="sg-ps"'),
        ("<title>PhotoCraft</title>", f'<title>{APP_NAME}</title>\n  <link data-trunk rel="icon" href="sg-ps-logo.svg">\n'
                                      f'  <meta name="theme-color" content="#151515">'),
        ("background: #262626;", "background: #151515;"),
        ("color: #e0e0e0;", "color: #e85c3b;"),
    ])
    for rel in ("apps/photocraft-web/index.html", "apps/photocraft-web/src/web.rs", "apps/photocraft-web/src/main.rs"):
        path = root / rel
        text = path.read_text(encoding="utf-8")
        for old, new in (("photocraft_canvas", "sgps_canvas"), ("photocraft_loading", "sgps_loading"),
                         ("photocraft_stalled", "sgps_stalled"), ("photocraft-stalled", "sgps-stalled")):
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


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
    web(root)
    web_page_behaviour(root)
    device_fonts(root)
    n = rename_everywhere(root)
    drop_old_translations(root)
    check(root)
    print(f"rebrand: done ({n} name replacements)")


if __name__ == "__main__":
    main()
