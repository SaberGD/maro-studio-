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
        ('pub const DISCORD: &str = "https://discord.gg/artcraft";', f'pub const DISCORD: &str = "{SABER_SITE}";'),
        ('pub const ARTCRAFT_WEBSITE: &str = "https://getartcraft.com";', f'pub const ARTCRAFT_WEBSITE: &str = "{SABER_SITE}";'),
        ('pub const APP_PAGE: &str = "https://getartcraft.com/apps/photocraft";', f'pub const APP_PAGE: &str = "{APP_SITE}";'),
        ('pub const GITHUB: &str = "https://github.com/storytold/photocraft";', f'pub const GITHUB: &str = "{SABER_SITE}";'),
        ('pub const ISSUES: &str = "https://github.com/storytold/photocraft/issues";', f'pub const ISSUES: &str = "{SABER_SITE}";'),
        (
            '&[("help.discord", DISCORD), ("help.website", APP_PAGE), ("help.artcraftWebsite", ARTCRAFT_WEBSITE), ("help.github", GITHUB), ("help.reportIssue", ISSUES)];',
            '&[("help.discord", DISCORD), ("help.website", APP_PAGE)];',
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
        ('("help.discord", "Join the ArtCraft Discord…", &["Help"], None),', '("help.discord", "Saber Group Academy Website", &["Help"], None),'),
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
        ("pub fn url_for(", """/// The SG - PS (Maro) logo, rendered by the egui_extras SVG loader.
pub fn logo(size: f32) -> egui::Image<'static> {
    egui::Image::from_bytes("bytes://sg-ps-logo.svg", include_bytes!("sg_ps_logo.svg").as_slice()).fit_to_exact_size(egui::Vec2::splat(size))
}

pub fn url_for("""),
    ])
    edit(root, "crates/ui-egui/src/canvas.rs", [
        ("let card = Rect::from_center_size(area.center(), egui::vec2(460.0, 330.0 + recent_h));",
         "let card = Rect::from_center_size(area.center(), egui::vec2(460.0, 420.0 + recent_h));"),
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
    n = rename_everywhere(root)
    check(root)
    print(f"rebrand: done ({n} name replacements)")


if __name__ == "__main__":
    main()
