# HORIX patches for PhotoCraft 0.23.1

Diffs here apply in name order after `rebrand.py`, against the rebranded 0.23.1 tree.

PhotoCraft 0.21-0.23 changed several things these patches (and `rebrand.py`) had to follow:
- the interface translations left the source tree: they are in storytold/craft-i18n at the commit
  named in `craft-i18n.rev`. HORIX is for Arabic and English only (Saber Group, 2026-11-11), so
  `rebrand.py` (`i18n()`) unpacks only the Arabic catalogs (`archive/photocraft/craft-i18n-<rev>-ar.tar.gz`,
  made by `tools/pack_i18n.sh`), renames PhotoCraft in them, points `build.rs` at them and cuts the
  language registry to English + Arabic. No patch for it: it is a few exact edits that fail loudly.
- selections are sparse `Surface`s and `matting::refine_mask` / `region_reader` are test-only, so
  50's `enhance_region` goes through `refine_surface`.
- the start screen was rebuilt and upstream's own `home_screen_up()` now hides the panels under
  Home; HORIX Home still replaces the start screen (80).

PhotoCraft 0.16-0.20 split most large files into modules (`canvas.rs` -> `canvas/`, `panels.rs` ->
`panels/`, `lib.rs` -> `app/`, the engine's `*_cmds.rs` -> `engine/src/cmd/`), so every patch was
re-made against the new layout; what each one does is unchanged unless said below.

- `50-horix-ai`: MobileSAM Quick / Object Selection, IS-Net Select Subject, preload, the
  AI/GPU status chip. The AI drives upstream's Object Finder hover and click when the model is
  ready; without a model every tool falls back to upstream's own algorithm. Upstream (0.20.1)
  still has no learned segmentation (its ONNX attempt was reverted), so nothing here is
  superseded. Wiring in 0.20: the engine helpers (`sample_rgb8`, `enhance_region`,
  `set_selection_from`) live in `engine/src/cmd/smartselect_cmds.rs`; Select Subject is caught in
  `PhotocraftApp::run` (`ui-egui/src/app/commands.rs`); the model is polled each frame from
  `app/frame.rs`; Quick / Object Selection in `tools/retouch_ui.rs`, the Object Finder hover in
  `tools/object_finder.rs`; the `segmenter` service is in `services.rs`; the status chip in
  `panels/status_bar.rs`. Cargo.lock gets `ort` (and ndarray, matrixmultiply, rawpointer,
  smallvec 2.0.0-alpha.10) and nothing else.
- `60-horix-ux`: P before/after, profile mismatch off by default, overset mark, Ungroup in the
  context menu (and Ungroup on a layer inside a group), group-delete dialog, Color-panel
  eyedropper, Properties auto-raise, Select › Modify preview, and Path Blur's on-canvas controls
  (`blur_handles.rs`).
- `70-horix-one`: the web page's channel for HORIX One (apps/horix-one): `horix_command(id,
  params)` runs a command as the menus do, `horix_open(name, bytes)` opens a file, and a file a
  command writes goes to `window.horixOneCapture(name, bytes)` when the page defines it, instead
  of downloading. HORIX on its own is unchanged.
- `80-horix-home`: the HORIX family's shared Home (`../../horix-common/home/horix_home.rs`, copied
  in by `rebrand.py` with `horix_app_home.rs`). It replaces the start card (`canvas/tabs.rs`) and
  covers the window below the title bar (`app/frame.rs`: no options bar, toolbar, status bar or
  dock while it shows), as Photoshop's Home does; Workspace (or Esc) leaves the empty canvas, and
  the Home button (now in every theme) brings it back.
- `85-horix-chords`: Colour Chords at the top of Swatches and under the Color tab (every Color
  panel mode since 0.20's `color_panel_ui`), from the foreground colour; a short docked group
  shows a "Colour Chords →" button to the Swatches tab instead.
- `90-horix-paste-as`: pasting vector art asks how, as Photoshop does for Illustrator art:
  Smart Object (a "Vector Smart Object" layer), Pixels, Path or Shape Layer
  (`horix_paste_as.rs`). It comes up for a plain Edit › Paste when the system clipboard holds SVG
  markup (Horix Vectors, HORIX One's Vector persona and Illustrator copy art so); on the web the
  page's paste event brings the SVG (`horix_paste_svg`). Pixels, Path and Shape are upstream's
  own `edit.paste {"as": …}`.

Dropped when moving from 0.15.1 to 0.20.1, because upstream now does them:
- `60`: the `TextLayout::overflow` flag and the overset mark drawn while editing paragraph text:
  upstream's `TextLayout::overflows()` and its own enlarged "+" handle (`tools/type_tool/overlay.rs`)
  do that. HORIX keeps its mark on the layer when it is not being edited (Type or Move tool),
  now computed with upstream's `overflows()`.
- `rebrand.py`: File › Place Embedded in the browser (upstream enables it wherever there is a file
  picker, `menus/view_cmds/dispatch.rs`) and the web History budget cap (upstream's
  `WASM_MEMORY_USAGE_CAP_MB`, the same 1536 MB).

Dropped when moving from 0.9.0 to 0.15.1, because upstream does them:
- New Document › Color Profile (upstream 0.12, `new_doc_ui.rs`).
- Blur Gallery handles for Iris, Spin and Tilt-Shift, with several pins (upstream 0.10,
  `blur_pins.rs`). `blur_handles.rs` owns Path Blur only.
- `rebrand.py`'s plain-background Select Subject (upstream 0.13's backdrop pass, #2788).

Regenerating after an upstream bump: unpack the new source, run `rebrand.py` without the patches,
commit, cherry-pick (or `git apply -3`) each patch commit onto it, fix the conflicts, then
`git diff` each patch commit against its parent (Cargo.lock included in 50, for `ort`) and check
with `cargo check --locked` / `cargo test` as in `../UPGRADE-0.9.md`.

The 0.3.0 patches are kept in `../patches-0.3/` for reference (see `../UPGRADE-0.9.md`).
