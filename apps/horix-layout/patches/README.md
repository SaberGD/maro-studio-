# Horix patches

Diffs here apply in name order after `rebrand.py`'s edits (`hx.apply_patches`), against the
rebranded tree.

- `80-horix-home`: the HORIX family's shared Home (`../../horix-common/home/horix_home.rs`, copied
  in by `rebrand.py` with `../home/horix_app_home.rs`). It replaces the welcome/start screen and
  covers the window below the app bar, as Photoshop's Home does; Workspace (or Esc) leaves the
  empty workspace, and the Home button brings it back.
- `85-horix-chords`: HORIX Colour Chords (`../../horix-common/home/horix_chords.rs`) under the
  Color panel (`panels/swatches.rs`), after upstream's ramp and Add to Swatches: a chord colour
  applies as the ramp does (`object.color`), and Add to Swatches makes its colours swatches
  (`swatch.create`) in a colour group of their own (`swatch.newColorGroup`). A gradient fill shows
  upstream's gradient-stop editor without chords.

Made against DesignCraft 0.17.0 (`v0.17.0`). To refresh one after an upstream update: rebrand a
clean tree, commit it, apply the old diff with `git apply -3` (or cherry-pick), resolve, and write
`git diff` back here.
