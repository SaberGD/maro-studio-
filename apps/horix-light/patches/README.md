# Horix Light patches

Diffs here apply in name order after `rebrand.py`'s edits (`hx.apply_patches`), against the
rebranded tree. Made against LightCraft 0.21.1 (`v0.21.1`).

- `50-horix-ai`: HORIX AI masks in the browser (MobileSAM Object, IS-Net Subject/Background; the
  page runs the models with onnxruntime-web, `window.horixLight` in `index.html`; the engine queues
  requests in `Segmenter::external`, `crates/engine/src/segment/external.rs`, and the page answers with
  `mask.horixResult`). Desktop keeps upstream's SAM 3.
- `80-horix-home`: the HORIX family's shared Home (`../../horix-common/home/horix_home.rs`, copied in by
  `rebrand.py` with `../home/horix_app_home.rs`). It covers the window below the top bar
  (`app/frame.rs`), as Photoshop's Home does; the Home button (`panels/topbar.rs`) brings it back.
  Home also lists the recent libraries and opens one, so upstream's start-up library chooser
  (`Launch::Ask`) is never seen: Home covers it.
- `85-horix-chords`: Colour Chords under Color Grading (`panels/edit/grading.rs`), from the
  highlights' (else midtones', shadows') hue, set on the wheels in one step.
- `90-horix-languages`: Arabic and English only. The Language menu, the Settings row and the browser's
  language detection offer English (and Arabic, if a catalogue ever ships); the other translations stay
  in the code, hidden (their commands and saved settings still work, for the control channel and old
  settings files).

To refresh one after an upstream update: rebrand a clean tree, commit it, cherry-pick (or
`git apply -3`) the old diff, resolve, and write `git diff` back here.
