# Shared pieces of the HORIX family

Copied into every app's tree by its `rebrand.py` (through `horix_rebrand.py`):

- `home/`: the family's Home screen (`horix_home.rs`, per-app `horix_app_home.rs`) and Colour Chords
  (`horix_chords.rs`). Written once; it has to compile on every app's egui. Since the 2026-11-13
  bump all apps (HORIX, Vectors, Layout, Light, One) are on egui 0.37 (the storytold fork), but keep
  to APIs that exist on 0.36 and 0.37 where there is a choice (`widget_info` rather than
  `accessible_name`).
- `desktop-package.sh`: the Windows and macOS packaging of each app's desktop build.
- `craft-fonts.sh`, `loader-site.sh`, `deploy-static.sh`, `ensure-subdomain.sh`, `*.htaccess`: the web
  build and hosting steps.

HORIX is for Arabic and English only: the language menus offer those two (`patches/90-horix-languages`
in each app, or the `i18n()` step of HORIX's `rebrand.py`).
