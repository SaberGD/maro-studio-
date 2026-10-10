# HORIX ad (24.8 s, Stomp Clap track)

- `ad.html`: the scenes. Every frame is `render(t)`; the cut times come from the track's measured hits (128 BPM: claps 0–3.8 s, stomps 3.77–6.6 s, break, drop at 7.595 s).
- `cap4.mjs` (1x) and `caphd.mjs` (2x, used for the macro close-ups): Playwright captures of the live app at sabergroupacademy.com/horix into `hero/` and `hd/`. Photos are free Unsplash images in `img/`.
- `render.mjs ad.html out.mp4 30` renders the video; `sfx.json` + `../sfx.py` give the transition sounds, mixed at 35% under the music.
- Needs `lib.js` from `../` and the brand fonts and logo in `a/` (from `../../assets/fonts` and `../../brand`).
- `fix.py` puts the supplied photos (original, clean cutout, red wall) into the app screenshots (`fix/`): the marching ants follow the cutout's edge, and the Hue/Saturation dialog stays on top.
- Break and drop (6.9–8 s) use the app's own loading screen: the logo lights up with the progress, the red rule fills, and the amber eye opens on the drop.
