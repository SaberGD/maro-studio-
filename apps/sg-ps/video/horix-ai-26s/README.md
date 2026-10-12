# HORIX AI ad (26 s, 16:9)

Same style as `../horix-ad/full.html` (charcoal, falcon watermark, red accent, Arabic words popping on the
hits, flashes on the cuts), on parts 2 and 3 of the "Dynamic" track only (`a/horix-30s.mp3`, 25.7 s): part 2
from 42.40 s of the source, part 3 placed so its first hit lands 25 beats (0.36 s) after part 2's. Each part
is built from 3.84 s phrases ending in a triple stab (+1.625 / +1.985 / +2.345 s); every cut sits on one.

Scenes: macro flash cuts → "تحديد بالذكاء الاصطناعي" on the stabs → logo with the eye opening → "والفرق بالأرقام"
on part 2's release → seven features (before/after wipe + measured number from `../../REPORT.md`) → end card.

    node ../horix-ad/render.mjs ad30.html v.mp4 30
    ffmpeg -i v.mp4 -i a/horix-30s.mp3 -c:v copy -c:a aac -b:a 256k -shortest HORIX-AI-Ad-26s.mp4
