"""Procedural promo track: punchy electronic beat + pads, with whooshes on scene cuts.

Usage: python3 music.py out.wav duration_seconds cut1,cut2,... [bpm]
"""
import sys
import wave

import numpy as np

SR = 44100
out, dur = sys.argv[1], float(sys.argv[2])
cuts = [float(x) for x in sys.argv[3].split(",") if x]
bpm = float(sys.argv[4]) if len(sys.argv) > 4 else 112.0
beat = 60.0 / bpm
n = int(SR * dur)
L = np.zeros(n)
R = np.zeros(n)
rng = np.random.default_rng(7)


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= n:
        return
    sig = sig[: n - i]
    L[i : i + len(sig)] += sig * gain * (1 - max(pan, 0))
    R[i : i + len(sig)] += sig * gain * (1 + min(pan, 0))


def env_ad(length, attack, decay_pow=4.0):
    t = np.linspace(0, 1, int(length * SR), endpoint=False)
    a = np.minimum(1, t * length / max(attack, 1e-4))
    return a * (1 - t) ** decay_pow


def lowpass(x, cutoff):
    # One-pole low-pass (cutoff may be an array).
    a = np.exp(-2 * np.pi * np.asarray(cutoff) / SR) * np.ones(len(x))
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def kick():
    length = 0.45
    t = np.arange(int(length * SR)) / SR
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7) + 0.3 * np.sin(ph * 2) * np.exp(-t * 30)


def snare():
    length = 0.25
    t = np.arange(int(length * SR)) / SR
    noise = rng.standard_normal(len(t))
    noise = noise - lowpass(noise, 1500)
    return (0.7 * noise * np.exp(-t * 18) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25))


def hat(open_=False):
    length = 0.18 if open_ else 0.05
    t = np.arange(int(length * SR)) / SR
    noise = rng.standard_normal(len(t))
    noise = noise - lowpass(noise, 7000)
    return noise * np.exp(-t * (14 if open_ else 70))


def saw(freq, length, detune=0.0):
    t = np.arange(int(length * SR)) / SR
    out_ = np.zeros(len(t))
    for d in (-detune, 0, detune):
        ph = (t * freq * (1 + d)) % 1.0
        out_ += 2 * ph - 1
    return out_ / 3


def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# Chords (A minor - F - C - G), one per bar.
prog = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
bass = [45, 41, 36, 43]
bar = 4 * beat
nbars = int(np.ceil(dur / bar))
intro = cuts[0] if cuts else 2.0

for b in range(nbars):
    t0 = b * bar
    ch = prog[b % 4]
    # Pad: detuned saws, low-passed, slow attack.
    pad = sum(saw(note(m + 12), bar, 0.004) for m in ch) / 3
    pad = lowpass(pad, 1400) * env_ad(bar, 0.25, 0.6)[: len(pad)]
    add(pad, t0, 0.22, 0.0)
    # Bass on 8ths after the intro.
    if t0 >= intro - 0.01:
        for e in range(8):
            bl = saw(note(bass[b % 4]), beat / 2 * 0.9, 0.002)
            bl = lowpass(bl, 500) * env_ad(len(bl) / SR, 0.005, 1.5)[: len(bl)]
            add(bl, t0 + e * beat / 2, 0.35)
    # Arp: chord tones on 16ths, sparkle.
    for s in range(16):
        m = ch[s % 3] + 24
        ar = np.sin(2 * np.pi * note(m) * np.arange(int(0.12 * SR)) / SR) * env_ad(0.12, 0.002, 3)
        add(ar, t0 + s * beat / 4, 0.05 if t0 >= intro else 0.03, 0.4 if s % 2 else -0.4)

# Drums.
t = 0.0
i = 0
while t < dur - 0.2:
    if t >= intro - 0.01:
        if i % 4 in (0, 2) or (i % 8 == 7):
            add(kick(), t, 0.9)
        if i % 4 in (1, 3):
            add(snare(), t, 0.35)
        add(hat(), t + beat / 2, 0.12, 0.3)
        add(hat(), t, 0.06, -0.3)
    t += beat
    i += 1

# Whooshes before cuts and an impact on each cut.
for c in cuts:
    length = 0.6
    tt = np.arange(int(length * SR)) / SR
    nz = rng.standard_normal(len(tt))
    sweep = lowpass(nz, 300 + 6000 * (tt / length) ** 2)
    w = sweep * np.sin(np.pi * tt / length) ** 2
    add(w, c - length + 0.05, 0.5)
    imp = kick() * 0.8
    add(imp, c, 0.5)

# Logo hit at the start.
hit_t = np.arange(int(1.5 * SR)) / SR
hit = (np.sin(2 * np.pi * 55 * hit_t) + 0.5 * rng.standard_normal(len(hit_t)) * np.exp(-hit_t * 20)) * np.exp(-hit_t * 3)
add(hit, 0.25, 0.6)

mixL, mixR = L, R
# Fades.
fade_in = np.minimum(1, np.arange(n) / (0.05 * SR))
fade_out = np.minimum(1, (n - np.arange(n)) / (1.2 * SR))
mixL *= fade_in * fade_out
mixR *= fade_in * fade_out
peak = max(np.abs(mixL).max(), np.abs(mixR).max(), 1e-6)
# Soft clip and normalise to -1 dBFS.
mixL = np.tanh(mixL / peak * 1.2) / np.tanh(1.2) * 0.89
mixR = np.tanh(mixR / peak * 1.2) / np.tanh(1.2) * 0.89
data = (np.stack([mixL, mixR], 1) * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(data.tobytes())
print("wrote", out)
