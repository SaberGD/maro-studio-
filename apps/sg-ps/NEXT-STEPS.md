# SG - PS: work in progress (handover notes)

Kept up to date so a new session can continue where the last one stopped.

## Bug round from the team (Oct 2026)

| # | Report | Status |
|---|--------|--------|
| 1 | Undo skips a rotation | Fixed (`stability()` in rebrand.py): Ctrl+Z cancels an open Free Transform; any other edit applies it first |
| 2 | Undo doesn't restore a move | Same cause as 1 (moves went to the pending transform box). After a crash/reload the recovered doc has no history (by design) |
| 3 | Placed image stays below objects after reordering | Same cause as 1 (canvas frozen on the open transform preview); layer order itself is fine (engine test) |
| 4 | Reference point doesn't follow the box when scaling | Fixed: patches/10-transform-pivot-color.diff |
| 5 | No eyedropper in the Color panel; shape Fill/Stroke "sometimes" missing in Properties | Fixed: eyedropper buttons, Properties switches to the layer tab for shape/text layers, Fill swatch "Use Foreground Color", Alt/Ctrl+Backspace recolour a shape (same diff) |
| 6 | Ctrl+C / Ctrl+V don't work (web and desktop) | Fixed: patches/20 (copy works on shape / smart object / type layers; Arabic keyboard layout; web input hook) |
| 7 | Alt+click clipping mask doesn't work | Fixed: Alt+click a layer toggles clipping; Ctrl+Alt+G toggles (patches/20) |
| 8 | Floating panels without open/close shortcuts | Window menu + F5-F8 already toggle; added Tab / Shift+Tab hide-show panels (patches/20) |
| 11 | Delete clears the layer instead of deleting it | Fixed: Delete with no selection deletes the layer (stability() in rebrand.py) |
| 9 | Sudden crashes | Not reproduced (web session + 30k-step native fuzz). Added: crash message overlay on the web with the panic text, wasm History memory cap 1.5 GB, desktop autosave every 3 min |
| 10 | .ai / non-image formats | Not done. SVG import ~1 day (resvg already in the build); PDF / PDF-compatible .ai as flattened pages ~2-4 days (hayro crate) |

Follow-ups worth doing: Path Selection click selects the shape layer; options-bar Fill edits the selected shape; Studio themes show shape Fill/Stroke; web autosave to IndexedDB.

## Windows user's report (Oct 2026): patches/60-photoshop-parity.diff

| # | Report | Status |
|---|--------|--------|
| 1 | Quick Selection results | HORIX AI: MobileSAM (ai_segment.rs; desktop onnxruntime via ai_model.rs, web onnxruntime-web in index.html). Plain strokes add points, Alt-strokes background points, each decode starts from the previous mask; edges snapped at full resolution. Object Selection uses it with a box. 60 composites, IoU after the stroke / +1 / +2 / +3 corrections: classic 0.697 / 0.737 / 0.704 / 0.736, HORIX AI 0.724 / 0.925 / 0.972 / 0.980 (ai_model.rs ignored test, segeval/quickloop.rs). Web: the model (44 MB) is fetched once from /horix/models/, the runtime from jsDelivr; checked end to end in headless Chromium. Falls back to the classic tools if the model can't load |
| 1b | Select Subject | HORIX AI: IS-Net on the desktop (179 MB), U²-Netp in the browser (4.6 MB), both Apache-2.0 (ai_segment.rs `subject`). IoU on 80 DUTS-TE photos: classic 0.416, U²-Netp 0.748, IS-Net 0.930 in the app (1.0 s); on 20 high-resolution HRSOD photos classic 0.486, IS-Net 0.800. Snapping the edge to the image measured no better, so the model's soft edge is kept. Checked in headless Chromium (ai/screenshots/web-select-subject.png). Falls back to the classic command |
| 2 | Select and Mask has no preview | Live preview with view modes (Overlay, On Black, On White, Black & White); also Select › Modify. Refine Edge Brush: tick it in the dialog, paint over hair / fur on the canvas (Alt erases, Clear Brush Strokes), the strokes are the command's `brush` parameter. Under the strokes a colour guided filter (radius 0.6% of the long side) refines the edge. On 41 AIM-500 photos (hair, fur), edge error SAD 4.23 -> 2.74; closed-form, KNN and learning-based matting scored 4.56 / 5.15 / 5.23 (slower too). Checked in headless Chromium |
| 3 | Preview in dialogs | P toggles before / after in every previewing dialog (Photoshop) |
| 4b | Studio theme hid panels | Every theme now shows the same panels and controls: Properties / Adjustments docked (no floating card), layer Kind filter, the five lock buttons, Home button, Edit Toolbar, Quick Mask and Screen Mode buttons |
| 4 | Brush lags on Windows | Not reproduced here. The surface already runs low-latency (1 frame queued) and the live stroke recomposites only its damage. Needs Help › System Info from the user's PC (GPU backend, adapter) |
| 5 | Can't ungroup | Ungroup Layers in the layer context menu; Ungroup on a layer inside a group takes it out (Photoshop) |
| 6 | Can't copy a channel | Copy / Cut / Paste with an alpha or colour channel targeted work on that channel as grayscale |
| 7 | Healing results | Soft tips no longer leave a ghost (Spot Healing blemish error 25 -> 14, Healing Brush 28 -> 20, of 255; segeval/healeval.rs) |
| 8 | Gradient controlled from the side panel | Options-bar swatch opens the gradient picker; Classic gradient paints the picked gradient too |
| 9 | No Blend If | Blending Options: Blend If channel, This Layer / Underlying Layer sliders, Alt-drag splits |
| 10 | One stroke only | "+" / "−" on Stroke, Inner Shadow, Colour / Gradient Overlay, Drop Shadow, up to 10 each |
| 11 | Properties doesn't open with tools | Opens on picking a shape, type or pen tool, and on selecting shape / type / gradient layers, in every theme (was Pro themes only) |
| 12 | No overset-text mark | Red "+" on the paragraph box corner while editing and with Type / Move on the layer |
| 13 | Can't Create Layers from effects | In the layer context menu and the effects rows' context menu |

Files: apps/sg-ps/ai/fetch.py downloads and SHA-256-checks the model and onnxruntime 1.22.0 for build.sh (web: horix/models/) and desktop/package.sh (Windows: onnxruntime.dll + models/ beside HORIX.exe; macOS: Contents/Frameworks + Contents/Resources/models). Licences: ai/LICENSE-MobileSAM.txt, ai/LICENSE-SegmentAnything.txt, onnxruntime's own files.

## Round 4 (team feedback)

| # | Report | Status |
|---|--------|--------|
| 1 | "Embedded Profile Mismatch" message on every open | Off by default now: the file opens at once and keeps its own profile (Photoshop's Preserve Embedded Profiles). Edit › Color Settings › Ask When Opening still turns it on (stored under a new key, so the old saved default doesn't come back) |
| 2 | No colour profile in New Document | New Document › Color Profile: Working (default) or any built-in profile of the colour mode (Display P3, Adobe RGB, ProPhoto, Rec. 2020…); `file.new {"profile"}` |
| 3 | Blur Gallery has no on-canvas controls | Path Blur arrow and end points, Tilt-Shift focus / transition lines and rotate dot, Iris and Spin ellipses with size (and Iris feather) handles, centre pins; they edit the dialog's fields so the preview follows (blur_handles.rs). Blur Gallery and Select and Mask open at the right edge, off the image |
| 4 | Tool preset arrow has no Reset Tool | The arrow (and the tool icon) open Reset Tool / Reset All Tools (tool_reset.rs) |

## Round 5 (selection tools)

| # | Item | Status |
|---|------|--------|
| 1 | Magnetic Lasso as Photoshop's | Intelligent Scissors live wire (algo/scissors.rs; Mortensen & Barrett costs) kept in Photoshop's detection corridor (Width, screen px, around the pointer's track) and pulled toward it; click to start, move without a button, fastening points by Frequency and by clicking, Backspace / Delete back, Alt straight segments, Enter / double-click / click on the start closes, Esc cancels; Width / Contrast / Frequency in the options bar (magnetic_ui.rs). 69 DUTS-TE objects traced by a simulated hand (segeval/magneval.rs), IoU with a 12 px wobble: plain lasso 0.841, old magnetic 0.856, new 0.862; 4 px wobble 0.898 / 0.874 / 0.889. Checked in headless Chromium |
| 2 | Several Blur Gallery pins | Field / Iris / Spin: click adds a pin, click selects, Delete removes, the ring sets blur (Spin: arc); Path Blur: several paths, click a segment for a bend point. They travel as `pins` / `paths` (blur_handles.rs). Checked in headless Chromium |
| 3 | Quick / Object Selection on real photos | 79 DUTS-TE photos (ai_model.rs ignored tests, segeval/quickloop.rs): Quick Selection after the stroke / +3 corrections classic 0.447 / 0.505, HORIX AI 0.727 / 0.863; Object Selection (box 5% larger than the object) classic 0.630, HORIX AI 0.800 |

## Videos requested (after the fixes ship)

Status: both rendered (promo.mp4 31 s, fixes.mp4 42 s, 1920x1080 with music). Sources: HTML scenes + render.mjs + music.py in the session scratchpad; a vertical 9:16 cut is a possible follow-up.

1. Short promo motion video: SG - PS features, browser and desktop. Quick, nice animations, motion-designer quality.
2. Before / after video: the problems in the old version and how they are fixed now.

Plan: HTML/CSS animation scenes + real screen captures of the app (Playwright, headless Chromium), rendered frame by frame and encoded with ffmpeg (1080x1920 and 1920x1080). Deliver the MP4s to the user.
