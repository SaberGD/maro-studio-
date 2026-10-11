# HORIX ad (24.8 s, Stomp Clap track)

- `ad.html`: the scenes. Every frame is `render(t)`; the cut times come from the track's measured hits (128 BPM: claps 0–3.8 s, stomps 3.77–6.6 s, break, drop at 7.595 s).
- `cap4.mjs` (1x) and `caphd.mjs` (2x, used for the macro close-ups): Playwright captures of the live app at sabergroupacademy.com/horix into `hero/` and `hd/`. Photos are free Unsplash images in `img/`.
- `render.mjs ad.html out.mp4 30` renders the video; `sfx.json` + `../sfx.py` give the transition sounds, mixed at 35% under the music.
- Needs `lib.js` from `../` and the brand fonts and logo in `a/` (from `../../assets/fonts` and `../../brand`).
- `fix.py` puts the supplied photos (original, clean cutout, red wall) into the app screenshots (`fix/`): the marching ants follow the cutout's edge, and the Hue/Saturation dialog stays on top.
- Break and drop (6.9–8 s) use the app's own loading screen: the logo lights up with the progress, the red rule fills, and the amber eye opens on the drop.
- `reel.html`: the 9:16 reel (1080x1920), laid out for portrait from scratch on the same beat map: one word per line for the question, a portrait window on the canvas, menus side by side, safe area kept clear of the bottom UI. Render with `VW=1080 VH=1920 node render.mjs reel.html out.mp4 30`.
- Full quality: `PNG=1 CRF=12 PRESET=slow` (lossless frames, x264 CRF 12), audio AAC 320k.
- `reel2.html` («إيدك عارفة الطريق»): second 9:16 reel on the same track. Keyboard keys slam on the stomps, then each feature in the real app on the bars: Free Transform with the pivot, Ctrl+Z steps, eyedropper + Alt+Backspace recolour, Alt+click clipping into "HORIX", Ctrl+C/V, Select Subject, Delete, Tab, desktop autosave. Captures in `cap2/` come from `driver.mjs`, which drives the live app over HTTP one step at a time.
