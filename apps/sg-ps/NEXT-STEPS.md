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

## Videos requested (after the fixes ship)

Status: both rendered (promo.mp4 31 s, fixes.mp4 42 s, 1920x1080 with music). Sources: HTML scenes + render.mjs + music.py in the session scratchpad; a vertical 9:16 cut is a possible follow-up.

1. Short promo motion video: SG - PS features, browser and desktop. Quick, nice animations, motion-designer quality.
2. Before / after video: the problems in the old version and how they are fixed now.

Plan: HTML/CSS animation scenes + real screen captures of the app (Playwright, headless Chromium), rendered frame by frame and encoded with ffmpeg (1080x1920 and 1920x1080). Deliver the MP4s to the user.
