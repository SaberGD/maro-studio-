# HORIX: upgrade assessment, PhotoCraft v0.3.0 to v0.9.0

Read-only research. Nothing in `/home/user/maro-studio-` was changed.

## Sources

- HORIX: `apps/sg-ps/README.md`, `NEXT-STEPS.md`, `rebrand.py` (20 edit functions), `patches/10…91-*.diff` (about 10.3k diff lines).
- Upstream: full clone `scratchpad/up/photocraft`, with `git log v0.3.0..v0.9.0` (1,879 commits; 1,374 files changed, +384k/−17.6k lines). The log is saved at `scratchpad/uplog.txt`.
- Pristine v0.9.0 tree `scratchpad/pc09`, and the attempted-apply tree `scratchpad/pc09t` with its `*.rej` files.
- Release dates: v0.3.0 was tagged 2026-10-07 and v0.9.0 on 2026-10-14. Upstream moves very fast: there are 232 more commits on `main` after v0.9.0.

Each verdict below was checked against the v0.9.0 source as well as the commit log.

Note on the `.rej` counts: `git apply --reject` overwrites a file's `.rej` each time a later patch touches the same file. The `.rej` files left in `pc09t` therefore show only the last patch's failures per file. They are useful for reading context, not for counting.

---

## 1. Feature-by-feature verdicts

Legend:
- **SUPERSEDED**: upstream v0.9.0 has the feature natively. Drop the HORIX code.
- **PARTIAL**: upstream covers part of it. The missing part is stated.
- **HORIX-ONLY**: upstream has nothing equivalent, so it must be ported.

### 1a. Selection tools and AI

| Feature (HORIX source) | Verdict | Evidence in upstream v0.9.0 | What to do |
|---|---|---|---|
| Magnetic Lasso (patch 40 selection_cmds; patch 60 `algo/scissors.rs`, `magnetic_ui.rs`; NEXT-STEPS R5#1) | **SUPERSEDED** | `0f16bce0` "Add the Magnetic Lasso tool (#864)". `Tool::MagneticLasso`, `ui-egui/src/magnetic_lasso_ui.rs`, `algo/src/magnetic.rs`. It uses the same Mortensen & Barrett live wire inside a detection corridor that pulls toward the pointer's path. Options-bar Width/Contrast/Frequency, stylus pressure, `[`/`]`, Backspace/Delete, Alt straight/freehand segments, double-click/Enter/click-on-start to close, Esc. Lazy block reads for 36 MP. | Drop `scissors.rs`, `magnetic_ui.rs` and the patch 40 selection_cmds hunk. Optionally re-run `segeval/magneval.rs` against upstream for the record. |
| Quick Selection work budget, 3 sweeps, Enhance Edge on by default (`rebrand.py selection_quality`) | **SUPERSEDED / obsolete** | Upstream rewrote Quick Selection: `9da40a1c` "Photoshop's behaviour, measured and fitted", `76fa2176` hybrid graph cuts (3.5× faster), `0fbba911` parallel cut windows. `WORK_PX` no longer exists in `quick.rs`. | Drop the quick.rs edits. Keep `enhance_edge: true` only if a re-measure shows it helps. |
| Select Subject (classic): focus prior, plain-background trimap, bigger native budget (`better_select_subject`, `plain_background_subject`, `selection_quality`) | **HORIX-ONLY** (low value once AI is ported) | Upstream's `subject.rs` is still the GrabCut/saliency design. Its only changes are perf and cancel (`a030d194`, `25a82978`). The anchors failed because rustfmt reflowed the file. | Re-anchor if the classic path is still wanted as the fallback when the AI model can't load. Otherwise drop it. |
| HORIX AI selection: MobileSAM for Quick/Object Selection, IS-Net for Select Subject, onnxruntime on desktop (`ai_model.rs`) and onnxruntime-web/WebGPU in the browser (`ai_segment.rs`, index.html `horixAi`), preload, progress chip, GPU status (patches 60/80/90/91) | **HORIX-ONLY** (largest port) | The upstream tree has no ONNX, ML runtime or model at all. ROADMAP lists "AI features 10%, 300–600 h, needs owner decisions". | Re-make it as a fresh patch against the 0.9.0 hook points. The new files (`ai_segment.rs` 992 lines, `ai_model.rs` 700, `gpu_status.rs` 298) mostly carry over. The glue in `lib.rs`, `retouch_ui.rs`, `smartselect_cmds.rs`, `panels.rs`, `canvas.rs`, `menus.rs`, `jobs_ui.rs` and `web.rs` must be redone. |
| Object Finder (hover highlight, click selects) | **PARTIAL** | `858fbcf1` "Object Selection: hover preview of the object it would select (Object Finder)", using the classic segmenter. | Keep only the MobileSAM backend for the hover and click path, wired into upstream's Object Finder UI. |
| Select and Mask live preview with view modes (R1#2) | **SUPERSEDED** | `0aaf5b60`: live preview in Photoshop's view modes (Onion Skin, Marching Ants, Overlay, On Black, On White, B&W, On Layers) in `select_mask_view.rs`. Also Output To New Document (`28874bbf`). | Drop. |
| Refine Edge Brush (paint on canvas, Alt erases, Clear Brush Strokes) | **PARTIAL** | `c1bd296d` "Select and Mask: Refine Edge Brush". Upstream `algo/matting.rs` already uses a guided filter with Smart Radius. | Missing: HORIX's colour guided-filter refinement tuned on AIM-500 (SAD 4.23 to 2.74). Re-measure upstream's brush with HORIX's segeval harness first. Port `refine_brush.rs` and the matting hunk only if HORIX's version still wins. |
| Refine Hair (whole-edge refinement, R5#6) | **HORIX-ONLY** | No "Refine Hair" in the upstream tree. | Re-make it on top of upstream's Select and Mask (small). |
| Select › Modify live preview | **HORIX-ONLY** (minor) | No upstream equivalent found. | Re-make it if the team wants it. |

### 1b. Pen, shapes and vectors

| Feature | Verdict | Evidence | What to do |
|---|---|---|---|
| Curvature Pen | **SUPERSEDED** | `c436aa72` "Tools: Freeform Pen and Curvature Pen". `Tool::CurvaturePen` is a real toolbox tool, where HORIX had a Pen mode. | Drop the patch 40 vector_ui Catmull-Rom code and the `pen_construction` option. |
| Freeform Pen | **SUPERSEDED** (HORIX never had it) | `Tool::FreeformPen` with Curve Fit and Alt straight segments (`f0d3156a`). | Nothing to do. |
| Add / Delete Anchor Point, Convert Point | **SUPERSEDED** | `d96bb501` Add/Delete Anchor tools, `d8d8d9f3` Convert Point tool, `c1e3ae9f` Pen Auto Add/Delete. `Tool::AddAnchorPoint`, `DeleteAnchorPoint`, `ConvertPoint`. | Drop. |
| Pen behaviours (patch 91): Cmd = Direct Selection, Alt converts or breaks handles, Cmd+Z/Backspace removes the last point, new subpaths join the Work Path | **SUPERSEDED (mostly)** | `1e916a4e` Ctrl/Cmd edits the path being drawn in place; `bd3be487` Alt breaks a handle; `ffb62ec9` Cmd+Z undoes in-progress points; `1168a9dd` a new path joins the selected path; `2f3e1c08` Esc keeps the work path; `72ef526d`/`f2c52a92` close cue. | Port HORIX's `pen_tool_tests.rs` as tests against upstream. Re-make only what fails: probably "click an open end point to continue the path" and "hide Work Path after Make Selection". |
| Pen/Path right-click menu with Make Selection dialog (`path_menu_ui.rs`) | **SUPERSEDED** | `canvas_tool_menu.rs` has "Make Selection…", Fill/Stroke Path and related items. | Drop. |
| Shape Fill/Stroke options (independent colours, stroke width; also Pen in Shape mode) | **SUPERSEDED** | The options bar has Fill (checkbox and swatch, default FG), a Stroke swatch (default BG), a width field and a full stroke-style editor (`shape_stroke_ui.rs`: align, caps, joins, dashes). The same controls apply to Pen Shape mode. Fill/Stroke edit the selected shape (`bbb05cab`). | Drop. |
| Alt/Ctrl+Backspace recolours a shape (patch 10 `fill_key_cmds`) | **SUPERSEDED** | `049a92c2`. `fill_key_cmds.rs` recolours a shape's fill or a type layer's text. | Drop. |
| One-click "Use Foreground Color" on the Fill swatch (patch 10 vector_ui) | **PARTIAL** | The swatch opens the Color Picker, and the fill keys exist. | Tiny convenience. Re-make only if users miss it. |
| Alt+Backspace fills the targeted mask (patch 30) | **SUPERSEDED** | `fill_key_cmds.rs` routes to the layer-mask, Quick Mask or channel target (`channel_view.target == LayerMask`). | Drop patch 30. |

### 1c. Transform, colour and dialogs

| Feature | Verdict | Evidence | What to do |
|---|---|---|---|
| Transform reference point follows the box (patch 10) | **SUPERSEDED** | `9b08da8d` "Free Transform: the reference point moves with the box when scaling (#1329)". | Drop. |
| Proportional edge handles (`proportional_edges`) | **SUPERSEDED** | `transform_tool.rs`: "The default is proportional for both, with ⇧ freeing them", plus the Use Legacy Free Transform preference and the options-bar link. | Drop (the anchor no longer matches anyway). |
| Undo / commit of an open Free Transform (`stability()` TRANSFORM_GUARD, bugs 1–3) | **PARTIAL (re-test)** | Undo/Redo step through the transform session itself (`transform_tool::intercept`). The transform is applied on tool switch (`3bea3f31`), on layer select (`086d78a0`), on an outside click (`d5bab136`) and before Layer Style (`997406a5`). Not found: a generic "any journaled command commits first". | Re-run bugs 1–3 on 0.9.0 before re-adding the guard. If any still fails, re-add a slimmer guard (commit only) without touching Undo. |
| Camera Raw curve grabs from the press and drags smoothly, endpoints pinned (patch 40) | **SUPERSEDED** | A shared `point_curve.rs` serves Camera Raw, the adjustment dialogs and Properties. It uses `press_origin`, keeps the endpoints, has a 16-point limit and drag-off delete. | Drop. |
| Color Picker "Pick from Image" (patch 40 color_picker_ui) | **SUPERSEDED** | `color_picker_ui.rs`: while the picker is on top, the image is its eyedropper (`sample_at`), with a pipette cursor. It also has a screen colour picker with a loupe (`0256eaa4`, `caabe4b8`). | Drop. |
| Eyedropper buttons in the Color panel (patch 10 panels) | **HORIX-ONLY** (small) | Photoshop has no such button, and upstream doesn't either. | Re-make it (about 20 lines) if the team wants to keep it. |
| Properties brings its layer tab forward on shape/type/gradient layers; opens on picking shape/type/pen tools (patches 10 and 60, NEXT-STEPS 5 and 11) | **PARTIAL** | Upstream brings Properties to the front for new adjustment and fill layers (`40427f25`), and the Studio themes show it for every layer (`e777690a`). | Missing: auto-raise on picking shape/type/pen tools and on selecting shape/type layers. Re-make (small). |
| Gradient swatch in the options bar opens a picker; Classic mode paints the picked gradient (60) | **SUPERSEDED (mostly)** | The options-bar swatch opens the Gradient Editor, and live and classic modes use the same engine-owned preset (`#1651`, `gradient_ui::preset_swatch`). Gradient controls show in every theme (`c7c60312`). | Drop. Photoshop's separate preset dropdown arrow is optional. |
| P toggles before/after in every previewing dialog (60 filter_dialog) | **HORIX-ONLY** | P exists only in Crop and Select and Mask view keys. | Re-make (about 10 lines in the shared dialog code). |
| Blend If (This Layer / Underlying sliders, Alt-split) | **SUPERSEDED** | `layer_style.rs` Blend If with This Layer / Underlying Layer split sliders. GPU-composited (`f57db2b5`). | Drop. |
| Multiple Stroke, Inner Shadow, Colour/Gradient Overlay and Drop Shadow with "+"/"−" | **SUPERSEDED** | `b436950a` multi-instance effects. `MULTI = [stroke, dropShadow, innerShadow, colorOverlay, gradientOverlay]` with a "+" button. | Drop (it was the biggest rejected file, `layer_style.rs`). |
| Create Layer(s) from effects | **SUPERSEDED** | The effects-row menu has "Create Layer" (`layer.layerStyle.createLayer`). | Drop. Add it to the main layer-row context menu only if wanted. |
| Blur Gallery on-canvas handles and multiple pins: Path Blur arrows and bends, Tilt-Shift lines, Iris/Spin ellipses and pins (`blur_handles.rs`, R4#3, R5#2) | **PARTIAL** | `be7a1f80` "Blur Gallery: Field Blur pins on the image" (`blur_pins.rs`: add, select, delete, ring drag, `pins` param). | Missing: Iris, Spin, Tilt-Shift and Path on-canvas controls, and multiple pins and paths for those. Port `blur_handles.rs` (614 lines) but reuse upstream's `blur_pins.rs` structure for Field. Also re-check "dialog opens at the right edge". |
| Reset Tool / Reset All Tools (`tool_reset.rs`, R4#4) | **SUPERSEDED** | `830541de`. Upstream's own `tool_reset.rs` uses right-click on the options-bar tool icon, as in Photoshop. | Drop. HORIX's file name collides with upstream's. |
| Embedded Profile Mismatch off by default (R4#1) | **HORIX-ONLY** (tiny) | `color_cmds.rs` `ask_on_mismatch: true` by default. This matches Photoshop, but HORIX users asked for it off. | Re-make: flip the default under a new prefs key (about 10 lines). |
| New Document › Color Profile (R4#2) | **HORIX-ONLY** | `new_doc_ui.rs` has no profile control, and `file.new` has no `profile`. | Re-make (60 `commands.rs`/`color_cmds.rs`/`new_doc_ui.rs` hunks, medium-small). |
| Overset-text red "+" mark (R1#12) | **HORIX-ONLY** | Text layout detects overflow (`layout.rs:733`), but nothing draws a mark. | Re-make (small: `text/layout.rs` flag plus a canvas overlay). |

### 1d. Layers, clipboard and keyboard

| Feature | Verdict | Evidence | What to do |
|---|---|---|---|
| Ctrl+C on shape, type and smart object layers (patch 20) | **SUPERSEDED (better), PARTIAL for selections** | With no selection, Copy keeps type, shape, smart object and group layers whole (`69110750`, `93599a18`), and Copy takes every selected layer (`5d8e5c13`). | Missing: Copy with a selection on a vector or type layer is still disabled (`can_copy` requires pixels). HORIX copied the rendered pixels. Re-make it only if users ask (small). |
| Arabic keyboard layout for Ctrl+C/V/X on the web (`KEYBOARD_SCRIPT`, patch 20) | **HORIX-ONLY (verify)** | Upstream matches physical keys only for `.` and `,` (`POSITIONAL`). Web paste dedup exists (`0f6d3dfe`). | Keep the index.html KEYBOARD_SCRIPT, which still applies by `</body>`. Test Ctrl+C/V/Z/S with the Arabic layout on web and desktop. Native egui may need a physical-key fallback for letters (re-make, small). |
| Alt+click toggles clipping (patch 20) | **SUPERSEDED** | `clip_line_ui.rs`: Alt+click the line between layers, as in Photoshop (`#967`), with a clipping cursor. | Drop. Note that HORIX's "whole row" variant becomes the Photoshop "line" gesture. |
| Ctrl+Alt+G toggles the clipping mask | **SUPERSEDED** | `026de5e2`, `clip_key_command`. | Drop. |
| Tab / Shift+Tab hide panels (patch 20) | **SUPERSEDED** | `31cb502c` "Tab hides all panels, Shift+Tab the panel dock" (in the shortcut table, so the web gets it too). | Drop. |
| Delete with no selection deletes the layer (`stability()`) | **SUPERSEDED** | `shortcut_dispatch::delete_key_command` deletes the layer, or the mask when the mask is targeted; also `873e92db`. | Drop. |
| Delete on a group asks "Group and Contents / Group Only" (patch 91 `group_delete_ui.rs`) | **HORIX-ONLY** | No such dialog upstream. | Re-make (133-line file plus small hooks). |
| Ungroup (patch 60) | **PARTIAL** | Layer › Ungroup Layers and Properties (group) exist. | Missing: Ungroup in the Layers context menu, and "Ungroup on a layer inside a group takes it out" (`extra_cmds.rs` hunk). Re-make (small). |
| Copy/Cut/Paste a channel | **SUPERSEDED** | `96198fe4`, `engine/src/channel_clip.rs` (colour and alpha channels as grayscale; Cut fills with BG). | Drop. |
| Import Brushes… in the brush picker (60) | **SUPERSEDED** | `brush_picker.rs` "Import Brushes…". | Drop. |

### 1e. Workspace and themes

| Feature | Verdict | Evidence | What to do |
|---|---|---|---|
| Floating panels: drag a tab strip out, Dock button, Window › Workspace › Reset Essentials (patch 40 `dock.rs`/`panels.rs`/menus) | **SUPERSEDED** | The shared docking layout (`craft_ui::docking`, `panel_docking.rs`): dragging a dock tab sideways detaches a floating group; `window.panel.float`/`dock`/`move` commands; tab moves between groups (`28622aab`); Workspace › Essentials / Reset Workspace re-apply defaults; New/Delete/Lock Workspace. | Drop. If the team liked the exact name, rename "Reset Workspace" via rebrand. |
| Studio theme hid panels / every theme shows the same panels (R1#4b) | **PARTIAL** | Upstream improved Studio (Properties for every layer, opaque floating-group titles). Studio still differs. | Keep HORIX's approach of hiding Studio from the list (theme/prefs edits, see 1f). |
| Full tool options in every theme (`full_tool_options`) | **HORIX-ONLY** | `panels.rs` still has 7 `if t.pro =>` arms (rebrand expects 8). Gradient left that list (`c7c60312`). | Re-make: change the expected count to 7. Better: count ≥1 instead of an exact number. |

### 1f. Branding, web shell and desktop (rebrand.py)

| Feature | Verdict | Notes |
|---|---|---|
| Name replacement, links, Help menu, title-bar Discord button, About text, licence collapsible | **HORIX-ONLY** | Re-anchor. The dry run found misses in `menus.rs`, `panels.rs` (Discord comment), `dialogs.rs` (about text). Upstream now also has a contributor/credits screen (`credits.rs`, `44303db5` "contributor and model credits"). Check that it shows no ArtCraft or Discord branding. |
| HORIX logo on the start screen, About and favicon; Arabic start-screen line; waitlist form | **HORIX-ONLY** | `canvas.rs` start screen changed. Re-anchor. |
| HORIX theme as default (Pro tokens recoloured; Studio hidden and migrated) | **HORIX-ONLY** | Upstream now has 14 themes (ProLightGray, ProLight, SolarizedDark, Adwaita/Dark, Breeze Light/Dark, SoftDark/Light). The `ALL` array and the `choice!(Theme …)` line both changed. Rewrite these edits with a regex or a list filter (remove `Studio` from `ALL`) instead of an exact string. The token-block slice between `Pro =>` and the next arm can stay index-based. |
| Barlow Condensed display font | **HORIX-ONLY** | `theme.rs` font registration: re-check the anchors. |
| Web loader screen ("the eye opens"), crash overlay, KEYBOARD/FONTS/WAITLIST scripts, PREFS_KEY, build output `sg-ps-*` | **HORIX-ONLY** | Upstream index.html still has the plain "Loading PhotoCraft…" and stalled hint, and no panic overlay. The `web.rs` anchor missed. Upstream now stores the catalog and fonts deflated so the wasm stays under a 24 MiB gate (`0c72d954`), which is good for HORIX's Brotli path. |
| wasm History cap 1.5 GB, desktop autosave every 3 min | **HORIX-ONLY** | `history_budget_bytes` and `autosave_minutes: 10` are unchanged upstream. Upstream hardened autosave recovery (`c20b81b2`, `ed7df56a`, `269d8fed`). Keep both edits; they still match. |
| Web device fonts (Local Font Access, Type › Load Device Fonts) | **HORIX-ONLY (easier now)** | Upstream serves fonts next to the app on demand (`66b022cd`, `photocraft_text::served`), and `families()` is now generation-keyed (`fonts::shared_generation()`). HORIX's `FONTS_GENERATION`/`register_font` should plug into upstream's `shared_generation`. Re-make it rather than re-anchor. |
| Desktop font scan off the UI thread (`font_warmup`) | **SUPERSEDED** | `7aba2bd3` "Type: scan system fonts off the UI thread", `233b6c63`. Drop. |
| Web File › Place Embedded | **HORIX-ONLY (much smaller now)** | Upstream already uses an asynchronous picker with a callback (`app.pick_file_bytes(…place_bytes…)` in `view_cmds.rs`). But `file.placeEmbedded` is still guarded by `native_doc`, which is false on wasm, so the menu item stays grey. Port: change the guard to `has_doc` (one edit in `file_cmds.rs`). Drop HORIX's PLACE_TAG/inbox machinery. |
| Desktop icons, company names, `APP_ID`, portable `HORIX-Data` (`desktop()`) | **HORIX-ONLY** | Re-check anchors in `build.rs`, `app_dirs.rs`, `main.rs`. Patch 50 (rustfmt of HORIX edits) must be regenerated. |

### 1g. Retouching

| Feature | Verdict | Notes |
|---|---|---|
| Spot Healing / Healing Brush quality (patches 40 and 60 `retouch_cmds`: wider margin, fringe handling, soft-tip ghost fix; segeval/healeval) | **PARTIAL (re-measure)** | Upstream reworked Spot Healing: Content-Aware dab (`1608b7b3`), Create Texture with min-error cuts (`1320dac5`), Proximity Match on the original pixels (`c02ffa97`), the drag trail. It also added the Remove tool (`897f9f37`). The margin line HORIX edits still exists (`retouch_cmds.rs:383`). Run `segeval/healeval.rs` on upstream first, then re-apply only the parts that still lower the error. |

---

## 2. Valuable new upstream features in 0.4–0.9 (HORIX users gain these for free)

### Tools (19 new tools since v0.3.0)
- Selection: Magnetic Lasso; Single Row / Single Column Marquee; marquee Fixed Ratio and Fixed Size; Object Finder hover; Select › Sky.
- Pen family: Freeform Pen, Curvature Pen, Add/Delete Anchor Point, Convert Point, Direct Selection (arrow-key nudge), Pen Auto Add/Delete.
- Retouch: Remove tool (non-local patch completion), Patch tool with live preview, Content-Aware Move (live preview, Transform On Drop), Red Eye, Pattern Stamp, Mixer Brush, Color Replacement.
- Other: Artboard tool, Frame tool, Perspective Crop, Color Sampler, Rotate View, Vertical Type and the Type Mask tools.
- Spring-loaded tool letters, a brush per painting tool, Caps Lock precise cursor.
- Vanishing Point plane editor, Curves/Levels black/grey/white eyedroppers, Curves pencil and Smooth, Gradient Map stop editing, Gradient interpolation methods, guide layout dialog, angle dials, Photoshop-style preview windows in generic filter dialogs, Alt+Cancel → Reset.

### Layers and effects
- Multi-instance effects, Blend If (GPU), Advanced Blending (knockout, blend as group), contour picker and Contour Editor.
- Copy/Paste of whole layers, masks, multiple layers and channels.
- Clip groups follow arrange/delete. Layers/canvas hover highlighting.

### File formats
- **SVG** opens as editable shape layers or places as a vector smart object (`f41eb4f7`, `1f76d839`). This covers HORIX bug #10's SVG part for free.
- New imports: Krita `.kra` (`0a32b359`, `4705fc59`), OpenRaster `.ora` read/write (`77221725`), Paint.NET `.pdn` layered (`db0fb078`), Affinity Photo/Designer 1 and 2 (`ae0313d3`, artboards, vectors, text), EXR multi-part and deep.
- Photoshop Actions `.atn` load and save (`3204231d`), Camera Raw settings `.xmp` (`ccfc878a`), `.abr` folder hierarchy, GRD import for Gradient Map presets.
- **PSD**: about 70 commits. Type styles from run sheets and Txt2 frames, smart object warps, Backgrounds round-trip, Gradient Map in CMYK/Lab, parallel RLE decode, many hardening fixes from fuzzing.
- WebP lossy/lossless kept on Save, export quality controls.
- **PDF / .ai: still not supported.** PDF is raster export only; there is no PDF or .ai import (docs/file-format-parity.md: "No vector/text PDF"). HORIX bug #10's PDF/.ai part remains HORIX's job.
- **RAW**: measured camera profiles (Nikon D4, D5100), Camera Raw Clarity/Texture/Dehaze in linear light, CR3 embedded previews, parallel preview conversion. Full CR3 decode is still unsupported.

### Performance and GPU
- GPU compositing reuse (unchanged lower-stack chunks), GPU Blend If, Navigator drawn from the GPU texture.
- Recomposite only where an edit draws (paste, duplicate, add/remove layer, undo/redo).
- Tile sharing on Copy and fills, row-wise marquee and lasso rasterising.
- Parallel canvas encode, Quick Selection 3.5× faster, Free Transform warps applied in the background with Esc to cancel.
- WebGPU shader fixes, a macOS Intel Iris crash fix, a DX12 screen-picker crash fix.
- These may well help HORIX's open "brush lags on Windows" report.

### UI
- Real docking: floating groups, tab moves between groups, splitter push, workspaces (Essentials, Photography, Painting, Pixel Art, Graphic and Web, Motion; New/Delete/Lock), Narrow Options Bar, Auto-Collapse Iconic Panels.
- 14 themes, including three more Photoshop brightness levels.
- Floating Brush Settings with a hamburger menu, drag a document tab off to float it.
- Contributor credits screen.
- Automation and MCP: control protocol, plugins, batch commands.

### i18n (important for HORIX)
- The catalog count grew from 6 (cs, es, ja, ru, zh-hans, zh-hant) to 21: de, el, fr, hu, id, it, ko, nl, pl, pt-br, sr, tr, uk and vi were added.
- **There is no Arabic catalog (`ar.tsv` does not exist).** But upstream added full **RTL shell mirroring** (`ade57991`, "Mirror the shell for right-to-left UI languages"; `i18n::dir_for_code` includes `ar`). With an RTL language the menu bar starts at the right, the toolbox docks on the right, the dock goes to the left, flyouts and popups mirror, and the status and options bars read right to left.
- Upstream also added lazy Arabic UI-font fallback (`aa509ca9`) and Arabic samples in font menus (`1e0f8844`). The text engine uses parley with Unicode bidi.
- **This makes a HORIX Arabic UI realistic**: add `ar.tsv` (about 3.1–3.8k rows, the size of the de/ja catalogs) and one `LangInfo` row. A strong candidate to upstream as a contribution, since it would then be maintained by them.

---

## 3. Porting plan

### Keep as is (applies by `</body>` or unchanged anchors)
- The `KEYBOARD_SCRIPT`, `CRASH_SCRIPT`, `FONTS_SCRIPT` and `WAITLIST_SCRIPT` injections.
- The History cap and the 3-minute autosave.
- `desktop()` icons and licences (re-check anchors).
- Model fetching and packaging in `ai/fetch.py` and `desktop/package.sh`.

### Drop entirely (superseded)
- **Patch 30** (mask fill shortcut).
- **Patch 10** except the Color-panel eyedropper and the Properties auto-raise (pivot and recolour are upstream).
- **Patch 20** except possibly a physical-key fallback for Ctrl+letter on Arabic layouts, re-made only after testing. Tab, clipping, Ctrl+Alt+G and shape copy are all upstream.
- **Patch 40** almost entirely: Magnetic Lasso, Curvature Pen and anchors, shape fill/stroke, Camera Raw curve, Pick from Image, floating panels and Reset Essentials. Keep only the `retouch_cmds` healing hunk, and only if re-measuring shows it still helps.
- **Patch 50**: regenerate it from scratch after the rest (rustfmt output).
- **rebrand.py**: `font_warmup`, `proportional_edges`, the `quick.rs` part of `selection_quality`, the Delete-key dispatch in `stability()`. Probably the transform guard too, after re-testing bugs 1–3.
- **Patch 60**: drop the parts upstream has: scissors and Magnetic Lasso, Blend If, multi-effects, Create Layers, channel copy, gradient picker, path menu, Import Brushes, Reset Tool, Select and Mask preview.
- **Patch 91**: drop the pen behaviours and test-fixture churn, keeping the tests as regression checks.

### Re-make as new, smaller patches against 0.9.0
1. **`00-branding` (rebrand.py)**: fix the ~26 misses. Rewrite fragile edits (ThemeKind `ALL`, `choice!(Theme…)`, `full_tool_options` count) as regex or structural edits. Switch web Place to a one-line `native_doc` to `has_doc` change. Rewrite device fonts against `fonts::shared_generation()`.
2. **`10-horix-ux`**: P preview toggle, profile mismatch default off, New Document colour profile, overset mark, Ungroup in context menu and out of a group, group-delete dialog, Color-panel eyedropper, Properties auto-raise for shape/type/pen, and, if testing calls for them, the transform commit guard and copy-with-selection on vector layers.
3. **`20-blur-gallery-handles`**: Iris, Spin, Tilt-Shift and Path on-canvas controls and multiple pins, built on upstream's `blur_pins.rs` pattern.
4. **`30-refine`**: Refine Hair, plus HORIX's guided-filter Refine Edge Brush weighting, only if segeval shows a gain over upstream.
5. **`40-healing`**: only the measured wins over upstream's new Spot Healing.
6. **`50-horix-ai`** (patches 60 AI + 80 + 90 + 91 preload): MobileSAM Quick/Object Selection, Object Finder backend, IS-Net Select Subject (desktop fp32, web fp16 with WebGPU), preload and progress chip, GPU and model status. Hook it into upstream's rewritten `smartselect_cmds.rs` and Object Finder. Re-run `segeval/quickloop.rs` and the DUTS/HRSOD numbers.
7. **Optional `60-arabic`**: an `ar.tsv` catalog. With upstream's RTL mirroring this gives a fully Arabic, mirrored HORIX. Best done as an upstream PR.

### Effort estimate (one engineer familiar with HORIX)

| Work | Days |
|---|---|
| Build check on 0.9.0: `craft-libs` git dependencies need network in CI; 24 MiB wasm gate; Rust 1.95 is unchanged | 0.5 |
| rebrand.py re-anchoring and rewrites (branding, theme, web shell, Place, device fonts) | 2–3 |
| Re-test superseded items against the team's bug list (transform undo, copy/paste on web, Arabic keys, Tab, clipping, Delete) | 1 |
| Small HORIX UX patch (item 2) | 2–3 |
| Blur Gallery handles (item 3) | 2–3 |
| Refine Hair, brush and healing (items 4–5, including segeval re-measure) | 2 |
| AI selection port (item 6, including web and desktop packaging and headless-Chromium checks) | 5–8 |
| Regenerate the rustfmt patch, full test run, desktop CI (Windows/macOS), deploy check | 2 |
| **Total** | **≈ 17–23 engineer-days (3.5–4.5 weeks)** |
| Optional Arabic catalog (machine draft plus native review) | +3–5 |

The code HORIX maintains would shrink substantially. Roughly 60% of the patch volume (patches 10, 20, 30 and 40, and most of 60's non-AI hunks) becomes upstream's responsibility. What remains is branding, the AI layer, Blur Gallery handles and a handful of small UX items.

### Process recommendations
- Make every `rebrand.py` edit fail with a clear message (it already does). Prefer structural edits (regex, count ≥1, insert-after-function-signature) over multi-line exact blocks. Upstream reformats often.
- Upstream moves about 250 commits a day. Pin to a tag (v0.9.0), or wait for a 0.9.x, and re-run the dry run before each bump.
- Several HORIX fixes match upstream issues one for one (Magnetic Lasso, pivot, Tab, Delete, Blend If, multi-effects, Reset Tool, Select and Mask). Contribute the remaining generic ones upstream (P toggle, overset mark, New Document profile, group-delete dialog, Blur Gallery handles) so the next upgrade is cheaper.
