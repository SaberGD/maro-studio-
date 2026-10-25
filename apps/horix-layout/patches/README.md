# Horix patches

Diffs here apply in name order after `rebrand.py`'s edits (`hx.apply_patches`), against the
rebranded tree.

- `80-horix-home`: the HORIX family's shared Home (`../../horix-common/home/horix_home.rs`, copied
  in by `rebrand.py` with `../home/horix_app_home.rs`). It replaces the welcome/start screen and
  covers the window below the app bar, as Photoshop's Home does; Workspace (or Esc) leaves the
  empty workspace, and the Home button brings it back.
