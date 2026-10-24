#!/usr/bin/env python3
"""Rebrand an unpacked craft-launcher (ArtCraft Launcher) source tree as HORIX Launcher.

Usage: python3 -I apps/horix-launcher/rebrand.py <path-to-craft-launcher-source>

The launcher installs, updates and opens the HORIX apps: HORIX, Horix Vectors and Horix Light.
Every edit is an exact find/replace that must match, so an upstream change fails loudly here.

What it changes:
  - "ArtCraft Launcher" -> "HORIX Launcher" everywhere (UI, data folders, single-instance ids);
    the binary is horix-launcher(.exe), as its own updates expect.
  - The app catalog: the three HORIX apps, all released from SaberGD/maro-studio-. One repository
    holds every app's releases, told apart by tag prefix (`horix-v0.2.57`,
    `horix-vectors-v0.11.3`, ...): a catalog repo `owner/repo#prefix` makes the GitHub fallback
    read only that app's releases.
  - The release feed: https://horix.si/launcher/release_info.json (apps/horix-launcher/feed/),
    published by CI after every release, instead of ArtCraft's API.
  - Links: Saber Group (Facebook, website, WhatsApp) instead of ArtCraft's Discord, socials, GitHub.
  - HORIX look: falcon icons, the HORIX wordmark, Horus Ink / Falcon Ivory / Vision Amber.
  - Details pages for the three apps, with pictures from horix.si (apps/horix-launcher/screenshots/).
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "horix-common"))
import horix_rebrand as hx  # noqa: E402

NAME = "HORIX Launcher"
REPO = "SaberGD/maro-studio-"
FEED_URL = "https://horix.si/launcher/release_info.json"
CODE = ["crates/**/*.rs", "apps/**/*.rs"]

# (id, name, tagline, colour [surface, ink on light, ink on dark], website, tag prefix)
APPS = [
    ("horix", "HORIX", "Image editing with AI", [[0xd6, 0x3c, 0x32], [0xb0, 0x2e, 0x25], [0xff, 0x8a, 0x70]], "https://horix.live", "horix-v"),
    ("horix-vectors", "Horix Vectors", "Vector illustration", [[0xea, 0x99, 0x3f], [0x9a, 0x5a, 0x12], [0xf2, 0xb3, 0x6e]],
     "https://vectors.horix.live", "horix-vectors-v"),
    ("horix-light", "Horix Light", "Photo library and raw development", [[0x4a, 0x44, 0x40], [0x4a, 0x44, 0x40], [0xd8, 0xd0, 0xc6]],
     "https://light.horix.live", "horix-light-v"),
]


def rgb3(c: list[list[int]]) -> str:
    return "[" + ", ".join("[" + ", ".join(f"0x{v:02x}" for v in t) + "]" for t in c) + "]"


def catalog(root: Path) -> None:
    rel = "crates/core/src/catalog.rs"
    path = root / rel
    text = path.read_text(encoding="utf-8")
    s = text.index("/// The Craft App Suite, in display order")
    e = text.index("/// ArtCraft's website.")
    apps = "".join(
        f'    app(\n        "{i}",\n        "{n}",\n        "{t}",\n        AppGroup::Classic,\n        {rgb3(c)},\n        "{REPO}#{p}",\n    ),\n'
        for i, n, t, c, _, p in APPS
    )
    text = text[:s] + f"/// The HORIX apps, in display order. All of them release from {REPO}, told apart by tag prefix.\n" \
        f"pub const SUITE: [CraftApp; {len(APPS)}] = [\n{apps}];\n\n" + text[e:]
    path.write_text(text, encoding="utf-8")
    sites = "\n".join(f'            "{i}" => "{w}".into(),' for i, _, _, _, w, _ in APPS)
    hx.edit(root, rel, [
        ("    pub fn releases_url(&self) -> String {\n        format!(\"https://github.com/{}/releases\", self.repo)\n    }",
         "    pub fn releases_url(&self) -> String {\n        format!(\"https://github.com/{}/releases\", crate::release::split_repo(self.repo).0)\n    }"),
        ("    pub fn repo_url(&self) -> String {\n        format!(\"https://github.com/{}\", self.repo)\n    }",
         "    pub fn repo_url(&self) -> String {\n        format!(\"https://github.com/{}\", crate::release::split_repo(self.repo).0)\n    }"),
        ("    pub fn website(&self) -> String {\n        format!(\"https://getartcraft.com/apps/{}\", self.id)\n    }",
         f"    pub fn website(&self) -> String {{\n        match self.id {{\n{sites}\n            _ => \"{hx.DOWNLOADS_PAGE}\".into(),\n        }}\n    }}"),
        ('pub const WEBSITE_URL: &str = "https://getartcraft.com";', f'pub const WEBSITE_URL: &str = "{hx.SABER_SITE}";'),
        # HORIX's Mac app has been com.sabergroup.sgps since 0.1 (its settings and permissions are
        # keyed to it); the launcher only takes a bundle with the id it expects, so "the disk image
        # doesn't contain the app" until it expects that one. Vectors and Light keep upstream's scheme.
        ("    pub fn bundle_id(&self) -> String {\n        format!(\"ai.storyteller.{}\", self.id)\n    }",
         "    pub fn bundle_id(&self) -> String {\n        if self.id == \"horix\" {\n            return \"com.sabergroup.sgps\".into();\n        }\n"
         "        format!(\"ai.storyteller.{}\", self.id)\n    }"),
        ('pub const GITHUB_OWNER: &str = "storytold";', 'pub const GITHUB_OWNER: &str = "SaberGD";'),
        ('pub const GITHUB_URL: &str = "https://github.com/storytold";', f'pub const GITHUB_URL: &str = "{hx.WHATSAPP}";'),
        ('pub const DISCORD_URL: &str = "https://discord.gg/artcraft";', f'pub const DISCORD_URL: &str = "{hx.FACEBOOK}";'),
        ('    "artcraft-launcher",\n    "ArtCraft Launcher",\n    "Installs and updates the Craft App Suite",',
         '    "horix-launcher",\n    "HORIX Launcher",\n    "Installs and updates the HORIX apps",'),
        ('    "storytold/craft-launcher",\n);', f'    "{REPO}#horix-launcher-v",\n);'),
        ('pub const LAUNCHER_REPO: &str = "storytold/craft-launcher";', f'pub const LAUNCHER_REPO: &str = "{REPO}#horix-launcher-v";'),
        ('pub const LAUNCHER_ID: &str = "artcraft-launcher";', 'pub const LAUNCHER_ID: &str = "horix-launcher";'),
    ])
    # No social icons (Saber Group's accounts are the Facebook and WhatsApp links).
    text = path.read_text(encoding="utf-8")
    m = re.search(r"pub const SOCIAL: \[\(&str, &str\); \d+\] = \[\n(?:    \(.*\),\n)+\];", text)
    if not m:
        hx.fail(f"{rel}: SOCIAL list not found")
    path.write_text(text[:m.start()] + "pub const SOCIAL: [(&str, &str); 0] = [];" + text[m.end():], encoding="utf-8")


def tag_prefixes(root: Path) -> None:
    """`owner/repo#prefix`: several apps' releases in one repository."""
    hx.edit(root, "crates/core/src/release.rs", [
        ("/// The prefix every download of `repo` must start with.\npub fn download_prefix(repo: &str) -> String {\n    format!(",
         "/// HORIX: a catalog repo `owner/repo#prefix` is the repository plus the tag prefix of the app's\n"
         "/// releases in it (`horix-v`, `horix-vectors-v`, ...): several apps release from one repository.\n"
         "pub fn split_repo(repo: &str) -> (&str, Option<&str>) {\n"
         "    match repo.split_once('#') {\n        Some((r, p)) => (r, Some(p)),\n        None => (repo, None),\n    }\n}\n\n"
         "/// The prefix every download of `repo` must start with.\npub fn download_prefix(repo: &str) -> String {\n"
         "    let repo = split_repo(repo).0;\n    format!("),
        ("    let tag = v[\"tag_name\"].as_str().filter(|t| !t.is_empty() && t.len() <= 64).ok_or(\"no release found\")?.to_string();\n"
         "    let releases = format!(\"https://github.com/{repo}/releases\");",
         "    let tag = v[\"tag_name\"].as_str().filter(|t| !t.is_empty() && t.len() <= 64).ok_or(\"no release found\")?.to_string();\n"
         "    let (base, tag_prefix) = split_repo(repo);\n"
         "    if tag_prefix.is_some_and(|p| !tag.starts_with(p)) {\n        return Err(\"another app's release\".into());\n    }\n"
         "    let releases = format!(\"https://github.com/{base}/releases\");"),
    ])
    hx.edit(root, "crates/core/src/version.rs", [
        ("    let t = text.trim();\n    let t = t.strip_prefix(['v', 'V']).unwrap_or(t);\n    if t.is_empty() || t.len() > 64 {",
         "    let t = text.trim();\n"
         "    // HORIX: an app's tag carries its name (`horix-vectors-v0.11.3`).\n"
         "    let t = t.rsplit_once(\"-v\").filter(|(_, v)| v.starts_with(|c: char| c.is_ascii_digit())).map_or(t, |(_, v)| v);\n"
         "    let t = t.strip_prefix(['v', 'V']).unwrap_or(t);\n    if t.is_empty() || t.len() > 64 {"),
    ])
    hx.edit(root, "crates/core/src/feed.rs", [
        ('        let releases_page = format!("https://github.com/{repo}/releases/");',
         '        let releases_page = format!("https://github.com/{}/releases/", release::split_repo(repo).0);'),
    ])
    hx.edit(root, "crates/native/src/source.rs", [
        # A tag prefix needs the release list (the newest of that app's releases), not `latest`.
        ("        let url = if prereleases {\n            format!(\"https://api.github.com/repos/{repo}/releases?per_page=30\")",
         "        let (base, tag_prefix) = release::split_repo(repo);\n"
         "        let url = if prereleases || tag_prefix.is_some() {\n            format!(\"https://api.github.com/repos/{base}/releases?per_page=100\")"),
        ("                let release = if prereleases {\n                    release::parse_github_release_list(&text, repo, true)?",
         "                let release = if prereleases || tag_prefix.is_some() {\n                    release::parse_github_release_list(&text, repo, prereleases)?"),
        ("    fn ask_pages(&self, repo: &str) -> Result<Answer, String> {\n",
         "    fn ask_pages(&self, repo: &str) -> Result<Answer, String> {\n"
         "        if release::split_repo(repo).1.is_some() {\n"
         "            return Err(\"releases/latest is the whole repository's, not this app's\".into());\n        }\n"),
    ])

    hx.edit(root, "apps/artcraft-launcher-web/src/web.rs", [
        ("async fn latest(repo: &str, prereleases: bool) -> Result<LatestRelease, Option<i64>> {\n    let url = if prereleases {\n"
         "        format!(\"https://api.github.com/repos/{repo}/releases?per_page=30\")",
         "async fn latest(repo: &str, prereleases: bool) -> Result<LatestRelease, Option<i64>> {\n"
         "    let (base, tag_prefix) = release::split_repo(repo);\n"
         "    let list = prereleases || tag_prefix.is_some();\n"
         "    let url = if list {\n"
         "        format!(\"https://api.github.com/repos/{base}/releases?per_page=100\")"),
        ("    let found: Option<Release> = if prereleases {\n        release::parse_github_release_list(&text, repo, true).map_err(|_| None)?",
         "    let found: Option<Release> = if list {\n        release::parse_github_release_list(&text, repo, prereleases).map_err(|_| None)?"),
    ])


def names(root: Path) -> None:
    hx.replace_everywhere(root, CODE + ["apps/*/index.html"], [
        ("ArtCraft Launcher", NAME),
        ("artcraft-launcher:show", "horix-launcher:show"),
        ("artcraft-launcher:hello ", "horix-launcher:hello "),
        ("artcraft-launcher:running ", "horix-launcher:running "),
        ('"ai.storyteller.artcraft-launcher"', '"ai.storyteller.horix-launcher"'),
        ('{ "artcraft-launcher" }', '{ "horix-launcher" }'),
        ("X-ArtCraft-Launcher=true", "X-HORIX-Launcher=true"),
        (r"Software\Learning Machines LLC\HORIX Launcher", r"Software\Saber Group Academy\HORIX Launcher"),
    ])
    hx.replace_everywhere(root, CODE, [
        ('tl!("Join the ArtCraft community on Discord")', 'tl!("Saber Group Academy on Facebook")'),
        ('tl!("Discord")', 'tl!("Facebook")'),
        ('tl!("Join the Discord")', 'tl!("Saber Group on Facebook")'),
        ('tl!("GitHub")', 'tl!("Contact us")'),
        ('tl!("ArtCraft on {name}")', 'tl!("Saber Group on {name}")'),
        ('tl!("Questions, ideas and news from the ArtCraft team")', 'tl!("Questions, courses and news from the Saber Group team")'),
        ('alt_text(tl!("ArtCraft"))', 'alt_text(tl!("HORIX"))'),
        ('i18n::t("ArtCraft on GitHub")', 'i18n::t("Contact Us: Courses & Services")'),
        ('"Join the ArtCraft Discord"', '"Saber Group Academy on Facebook"'),
        ('"Visit getartcraft.com"', '"Visit sabergroupacademy.com"'),
        ('"ArtCraftLauncherData"', '"HORIXLauncherData"'),
        ('concat!("ArtCraftLauncher/"', 'concat!("HORIXLauncher/"'),
        ('Self::ArtCraftApi => "ArtCraft API"', 'Self::ArtCraftApi => "HORIX feed"'),
        ('Self::Feed => "ArtCraft"', 'Self::Feed => "HORIX"'),
        ("Install and update the Craft App Suite", "Install and update the HORIX apps"),
        ("Craft App Suite", "HORIX Apps"),
        ("Craft Apps", "HORIX apps"),
        ("Craft App", "HORIX app"),
    ])
    hx.edit(root, "crates/core/src/feed.rs", [
        ('pub const FEED_URL: &str = "https://api.storyteller.ai/v1/craft_apps/release_info";', f'pub const FEED_URL: &str = "{FEED_URL}";'),
    ])
    # The binary is `horix-launcher` (self-update looks for `<id>.exe` / `bin/<id>`).
    hx.edit(root, "apps/artcraft-launcher/Cargo.toml", [
        ('default-run = "artcraft-launcher"', 'default-run = "horix-launcher"'),
        ("[lints]\nworkspace = true\n", '[[bin]]\nname = "horix-launcher"\npath = "src/main.rs"\n\n[lints]\nworkspace = true\n'),
    ])
    hx.edit(root, "apps/artcraft-launcher-web/index.html", [("Loading HORIX Launcher&hellip;", "Loading HORIX Launcher&hellip;")])


def look(root: Path) -> None:
    assets = HERE / "assets"
    # App icons inside the launcher.
    hx.edit(root, "crates/ui-egui/src/icons.rs", [(
        '        "photocraft" => egui::include_image!("../../../assets/app-icons/photocraft.png"),',
        "".join(f'        "{i}" => egui::include_image!("../../../assets/app-icons/{i}.png"),\n' for i, *_ in APPS)
        + '        "photocraft" => egui::include_image!("../../../assets/app-icons/photocraft.png"),',
    ), ("pub const ARTCRAFT_LOGO_ASPECT: f32 = 1038.05 / 108.0;", "pub const ARTCRAFT_LOGO_ASPECT: f32 = 1899.0 / 360.0;")])
    for i, *_ in APPS:
        (root / f"assets/app-icons/{i}.png").write_bytes((assets / f"app-icons/{i}.png").read_bytes())
    # The wordmark and mark (shown where ArtCraft's were).
    (root / "docs/brand/artcraft-logo-white.svg").write_bytes((assets / "horix-wordmark-on-dark.svg").read_bytes())
    (root / "docs/brand/artcraft-logo.svg").write_bytes((assets / "horix-wordmark-on-light.svg").read_bytes())
    (root / "docs/brand/artcraft-mark.svg").write_bytes((assets / "app-icon/favicon.svg").read_bytes())
    n = hx.replace_icons(root, assets / "app-icon", "assets/app-icon")
    # HORIX colours.
    rel = "crates/ui-egui/src/theme.rs"
    hx.edit(root, rel, [
        ("        bg: hex(0x121316),\n        sunken: hex(0x060607),\n        ink: hex(0xf2f1ee),",
         "        bg: hex(0x141314),\n        sunken: hex(0x0b0a0b),\n        ink: hex(0xf3efe8),"),
        ("        accent: hex(0x2d81ff),\n        accent_ink: hex(0x74aaff),\n        invert_bg: hex(0xffffff),",
         "        accent: hex(0xd63c32),\n        accent_ink: hex(0xf2b36e),\n        invert_bg: hex(0xf3efe8),"),
        ("        bg: hex(0xf2f1ee),\n        sunken: hex(0xe9e8e4),\n        ink: hex(0x101014),",
         "        bg: hex(0xf3efe8),\n        sunken: hex(0xe8e2d8),\n        ink: hex(0x141314),"),
        ("        accent: hex(0x2d81ff),\n        accent_ink: hex(0x1659c4),",
         "        accent: hex(0xd63c32),\n        accent_ink: hex(0xb02e25),"),
    ])
    for a, b in (("ink_alpha(0xf2f1ee,", "ink_alpha(0xf3efe8,"), ("ink_alpha(0x101014,", "ink_alpha(0x141314,")):
        hx.replace_everywhere(root, [rel], [(a, b)])
    hx.edit(root, "apps/artcraft-launcher-web/index.html", [
        ("<title>HORIX Launcher</title>", f'<title>{NAME}</title>\n  <link rel="icon" href="{hx.favicon_data_uri(assets / "app-icon")}">'),
    ])
    print(f"rebrand: {n} launcher icons")


def version(root: Path) -> None:
    """HORIX Launcher's own version (apps/horix-launcher/VERSION) as the workspace version: it is
    what the launcher reports, compares its own releases with, and names its files after."""
    v = (HERE / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", v):
        hx.fail(f"VERSION must look like 1.0.0, not {v!r}")
    path = root / "Cargo.toml"
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(r'(\[workspace\.package\][^\[]*?\nversion = ")[^"]+(")', rf"\g<1>{v}\g<2>", text, count=1)
    if n != 1:
        hx.fail("Cargo.toml: [workspace.package] version not found")
    path.write_text(new, encoding="utf-8")
    # Cargo.lock records the workspace crates' versions too.
    lock = root / "Cargo.lock"
    text = lock.read_text(encoding="utf-8")
    text, n = re.subn(r'(name = "(?:artcraft-launcher[\w-]*|xtask)"\nversion = ")[^"]+(")', rf"\g<1>{v}\g<2>", text)
    if n == 0:
        hx.fail("Cargo.lock: workspace crates not found")
    lock.write_text(text, encoding="utf-8")


# Pictures for the details pages: apps/horix-launcher/screenshots/v1/<app>/<key>.jpg, published
# on horix.si by horix-feed.yml (1200 x 750 JPEG each, as the launcher expects).
SCREENSHOTS_BASE = "https://horix.si/launcher/screenshots"

DETAILS = """const PLATFORMS: &str = "Windows, macOS, web";

pub const DETAILS: [AppDetails; 3] = [
    AppDetails {
        id: "horix",
        headline: "The visionary AI editor by Saber Group.",
        about: "A layered image editor with the menus, shortcuts and panels Photoshop users already know, \\
            built for Saber Group Academy's students and designers.\\n\\n\\
            HORIX selects with AI on your own computer: Select Subject, Object Selection and Quick \\
            Selection run local models, so your images never leave the device.",
        features: &[
            feature("AI selection, on device", "Select Subject, Object Selection and Quick Selection run local AI models, with the classic tools as a fallback."),
            feature("Real layered files", "Opens and saves layered PSD and PSB documents, and opens Krita, GIMP and Affinity files."),
            feature("Non-destructive editing", "Adjustment layers, smart objects, smart filters, layer styles and masks."),
            feature("Content-Aware tools", "Content-Aware Fill, Move, Patch and Remove, plus Spot Healing and the Healing Brush."),
            feature("Blur Gallery on the image", "Field, Iris, Spin, Tilt-Shift and Path Blur, edited with handles on the canvas."),
            feature("Serious color", "8-, 16- and 32-bit RGB, CMYK, Lab and Grayscale with ICC color management."),
        ],
        shots: &[
            shot("ai-select", "Select Subject with HORIX AI, on the device"),
            shot("start", "HORIX, ready to work"),
            shot("editing", "A photo open with the full toolset"),
        ],
        platforms: PLATFORMS,
    },
    AppDetails {
        id: "horix-vectors",
        headline: "Vector illustration from the HORIX family.",
        about: "A vector illustration app with the pen, panels and shortcuts illustrators expect, \\
            in the HORIX look. It runs on the desktop and in the browser at vectors.horix.live.",
        features: &[
            feature("The workflow you know", "Pen, direct selection, Shape Builder, booleans, snapping guides and an appearance panel."),
            feature("Live, editable effects", "Blends, envelope distort, gradient mesh, repeats, glows and the Effect Gallery stay editable."),
            feature("Type, including Arabic", "Area and path type, variable and color fonts, and Arabic text with Noto Sans Arabic on the web."),
            feature("Open formats", "Illustrator .ai, EPS, PDF and SVG import, Word and RTF text, SVG, PDF and PNG export."),
        ],
        shots: &[
            shot("start", "Horix Vectors, ready to draw"),
            shot("drawing", "Arabic type on a perspective drawing"),
        ],
        platforms: PLATFORMS,
    },
    AppDetails {
        id: "horix-light",
        headline: "Organize and develop your photos.",
        about: "A photo library and non-destructive raw developer in the spirit of Lightroom, from the HORIX \\
            family. It runs on the desktop and in the browser at light.horix.live.",
        features: &[
            feature("Library and catalogs", "Import folders, rate, flag and keyword, smart albums, and Lightroom catalog import."),
            feature("Raw development", "White balance, tone, curves, color grading, lens corrections and hundreds of cameras."),
            feature("AI masks, even in the browser", "Object, Subject and Background masks with HORIX AI, on the device; brush, linear, radial and range masks too."),
            feature("Export your way", "JPEG, PNG, TIFF and more, with sizing, sharpening and watermarks."),
        ],
        shots: &[
            shot("ai-mask", "A Subject mask with HORIX AI, in the browser"),
            shot("start", "Horix Light's library"),
            shot("develop", "Developing a photo"),
        ],
        platforms: PLATFORMS,
    },
];
"""


def details(root: Path) -> None:
    """The details pages: the three HORIX apps, with pictures from horix.si."""
    rel = "crates/core/src/details.rs"
    path = root / rel
    text = path.read_text(encoding="utf-8")
    s = text.index('/// Where every Craft App runs')
    e = text.index("];\n\nimpl AppDetails {") + len("];\n")
    path.write_text(text[:s] + DETAILS + text[e:], encoding="utf-8")
    hx.edit(root, rel, [
        ('pub const SCREENSHOTS_BASE: &str = "https://raw.githubusercontent.com/storytold/craft-launcher-assets";',
         f'pub const SCREENSHOTS_BASE: &str = "{SCREENSHOTS_BASE}";'),
        ('        let page = AppDetails::by_id("photocraft").unwrap();\n        assert_eq!(\n            page.screenshot_url("demo").as_deref(),\n'
         '            Some("https://raw.githubusercontent.com/storytold/craft-launcher-assets/v1/photocraft/demo.jpg")\n        );\n'
         '        for key in ["", "nope", "../vectorcraft/neon", "demo/../masks", "demo.jpg", "/etc/passwd", "demo?x=1", "demo#"] {',
         '        let page = AppDetails::by_id("horix").unwrap();\n        assert_eq!(\n            page.screenshot_url("start").as_deref(),\n'
         f'            Some("{SCREENSHOTS_BASE}/v1/horix/start.jpg")\n        );\n'
         '        for key in ["", "nope", "../horix-vectors/start", "start/../editing", "start.jpg", "/etc/passwd", "start?x=1", "start#"] {'),
    ])


def upstream_fixes(root: Path) -> None:
    """Fixes to craft-launcher 0.4.1 itself."""
    # install_dmg gained a `replace` flag; the macOS self-update (and its test) still passed the
    # old 6 arguments, so the macOS build doesn't compile. The launcher's own bundle is never
    # "someone else's app", so it doesn't need replace.
    hx.edit(root, "crates/native/src/self_update.rs", [
        ("install_dmg(&LAUNCHER, &file, Some(&existing), None, paths,", "install_dmg(&LAUNCHER, &file, Some(&existing), None, false, paths,"),
        ("install_dmg(&LAUNCHER, &dmg, Some(&existing), None, &Paths::under(dir.path()),",
         "install_dmg(&LAUNCHER, &dmg, Some(&existing), None, false, &Paths::under(dir.path()),"),
    ])


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1]).resolve()
    if not (root / "crates/core/src/catalog.rs").is_file():
        sys.exit(f"rebrand: {root} is not a craft-launcher source tree")
    upstream_fixes(root)
    catalog(root)
    details(root)
    tag_prefixes(root)
    names(root)
    look(root)
    version(root)
    # Inline unit tests in catalog.rs / feed.rs and the tests/ folders keep upstream fixtures.
    hx.check_no_upstream_brand(root, CODE, allowed=["/tests/", "crates/core/src/catalog.rs", "crates/core/src/feed.rs"])
    print("rebrand: done")


if __name__ == "__main__":
    main()
