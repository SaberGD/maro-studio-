# HORIX patches for PhotoCraft 0.15.1

Diffs here apply in name order after `rebrand.py`, against the rebranded 0.15.1 tree.

- `50-horix-ai`: MobileSAM Quick / Object Selection, IS-Net Select Subject, preload, the
  AI/GPU status chip. The AI drives upstream's Object Finder hover and click when the model is
  ready; without a model every tool falls back to upstream's own algorithm. Upstream (0.15.1)
  still has no learned segmentation, so nothing here is superseded. Sample All Layers is per
  tool since 0.12 (`tool_options.sample_all.get(tool)`).
- `60-horix-ux`: P before/after, profile mismatch off by default, overset mark, Ungroup in the
  context menu, group-delete dialog, Color-panel eyedropper, Properties auto-raise,
  Select › Modify preview, and Path Blur's on-canvas controls (`blur_handles.rs`).
- `70-horix-one`: the web page's channel for HORIX One (apps/horix-one): `horix_command(id,
  params)` runs a command as the menus do, `horix_open(name, bytes)` opens a file, and a file a
  command writes goes to `window.horixOneCapture(name, bytes)` when the page defines it, instead
  of downloading. HORIX on its own is unchanged.
- `80-horix-home`: the HORIX family's shared Home (`../../horix-common/home/horix_home.rs`, copied
  in by `rebrand.py` with `horix_app_home.rs`). It replaces the start card and covers the window
  below the title bar, as Photoshop's Home does; Workspace (or Esc) leaves the empty canvas, and
  the Home button (now in every workspace) brings it back.

Dropped when moving from 0.9.0 to 0.15.1, because upstream now does them:
- New Document › Color Profile (upstream 0.12, `new_doc_ui.rs`); keeping ours showed it twice.
- Blur Gallery handles for Iris, Spin and Tilt-Shift, with several pins (upstream 0.10,
  `blur_pins.rs`). `blur_handles.rs` now owns Path Blur only.
- `rebrand.py`'s plain-background Select Subject (upstream 0.13's backdrop pass, #2788, does the
  same job in the classic fallback; IS-Net is the main path).

Regenerating after an upstream bump: unpack the new source, run `rebrand.py` without the patches,
commit, `git apply --reject` each patch, fix the rejects, then `git diff` the rebranded commit
(Cargo.lock included in 50, for `ort`) and check with `cargo check` / `cargo test` as in
`../UPGRADE-0.9.md`.

The 0.3.0 patches are kept in `../patches-0.3/` for reference (see `../UPGRADE-0.9.md`).
