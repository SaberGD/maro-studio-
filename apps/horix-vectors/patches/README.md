# Horix patches

Diffs here apply in name order after `rebrand.py`'s edits (`hx.apply_patches`), against the
rebranded tree of VectorCraft 0.21.0.

- `80-horix-home`: the HORIX family's shared Home (`../../horix-common/home/horix_home.rs`, copied
  in by `rebrand.py` with `../home/horix_app_home.rs`). It replaces the welcome/start screen and
  covers the window below the app bar, as Photoshop's Home does; Workspace (or Esc) leaves the
  empty workspace, and the Home button brings it back.
  The Home replaces the canvas inside upstream's docking layout (craft-ui, 0.18+), which hides
  every panel while it shows.
- `85-horix-chords`: HORIX Colour Chords (`../../horix-common/home/horix_chords.rs`) as a section
  under the Color panel; a chord colour applies as a Color panel pick (and becomes the Color
  Guide's base, as upstream's picks do since 0.19).
