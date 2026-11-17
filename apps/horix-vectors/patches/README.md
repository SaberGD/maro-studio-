# Horix patches

Diffs here apply in name order after `rebrand.py`'s edits (`hx.apply_patches`), against the
rebranded tree of VectorCraft 0.24.1.

- `80-horix-home`: the HORIX family's shared Home (`../../horix-common/home/horix_home.rs`, copied
  in by `rebrand.py` with `../home/horix_app_home.rs`). It replaces the welcome/start screen and
  covers the window below the app bar, as Photoshop's Home does; Workspace (or Esc) leaves the
  empty workspace, and the Home button brings it back.
  The Home replaces the canvas inside upstream's docking layout (craft-ui, 0.18+), which hides
  every panel while it shows.
- `85-horix-chords`: HORIX Colour Chords (`../../horix-common/home/horix_chords.rs`) as a section
  under the Color panel; a chord colour applies as a Color panel pick (and becomes the Color
  Guide's base, as upstream's picks do since 0.19).
- `90-horix-languages`: HORIX is for Arabic and English only (Saber Group, 2026-11-11). The interface
  language pickers (Preferences and the app menu's Language) list English and العربية only
  (`Lang::horix_offered`, `Lang::for_picker`), and a saved or system language outside those shows
  English (`Lang::horix_from_pref`, used by `VectorcraftApp::ui_language`). Upstream's other
  translations stay in the code, hidden. VectorCraft has no Arabic interface catalog yet, so
  today the picker shows English alone; an `ar` catalog from upstream would show up by itself.
