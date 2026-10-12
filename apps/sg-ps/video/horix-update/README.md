# HORIX update ad (60 s, 16:9)

Every feature of the selection/AI update with its before/after capture and the measured improvement
(numbers from `../../REPORT.md`), cut on the bars of the "Dynamic" track.

- Music: `a/horix-60s.mp3` is a 59.64 s edit of `onaldin_dynamic_main.wav` (125 BPM, bar 1.92 s). The source holds
  four versions of the same loop with silences between them; the edit joins them on bar lines with no gaps:
  intro + build (0–23.25 s), second build (23.25–42.44 s), climax and the end hit at 57.80 s. Bar times are in
  `a/horix-60s.json`.
- Scenes: logo as the app's loading screen (0–4.05), headline, nine feature scenes of two bars each (7.89–42.44),
  six stats on the climax (one per bar), end card with the URL and platforms.
- Colours follow the default HORIX (Dark) theme: neutral #0E0E0F canvas, ivory text, amber #EA993F accent;
  red only on the X of the logo.

Render (from this folder):

    node ../horix-ad/render.mjs update.html v.mp4 30
    ffmpeg -i v.mp4 -i a/horix-60s.mp3 -c:v copy -c:a aac -b:a 256k -shortest HORIX-Update-Ad.mp4

Stills: `mkdir -p stills && node ../horix-ad/render.mjs update.html --stills 10.5,30,45`.
