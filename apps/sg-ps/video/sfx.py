"""Motion sound effects only (no music), synthesised and placed on a timeline.

Usage: python3 sfx.py out.wav duration events.json
events.json: [[time_seconds, "type", gain?], ...]
types: whoosh (ends on the time), impact, hit, pop, click, tick, swoosh, riser (starts on the time,
       optional duration as 4th item), scan (with duration), ding, chime, buzz, boing, shimmer
"""
import json
import sys
import wave

import numpy as np

SR = 44100
out, dur, events_path = sys.argv[1], float(sys.argv[2]), sys.argv[3]
events = json.load(open(events_path))
n = int(SR * dur)
L = np.zeros(n)
R = np.zeros(n)
rng = np.random.default_rng(11)


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(round(t0 * SR))
    if i < 0:
        sig, i = sig[-i:], 0
    if i >= n or len(sig) == 0:
        return
    sig = sig[: n - i]
    L[i : i + len(sig)] += sig * gain * (1 - max(pan, 0))
    R[i : i + len(sig)] += sig * gain * (1 + min(pan, 0))


def t_(length):
    return np.arange(int(length * SR)) / SR


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * np.asarray(cutoff, dtype=float) / SR) * np.ones(len(x))
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def noise(length):
    return rng.standard_normal(int(length * SR))


def whoosh(length=0.55):
    t = t_(length)
    sweep = lowpass(noise(length), 250 + 7000 * (t / length) ** 2.2)
    return sweep * np.sin(np.pi * t / length) ** 2 * 1.4


def swoosh(length=0.28):
    t = t_(length)
    sweep = lowpass(noise(length), 1500 + 5000 * np.sin(np.pi * t / length))
    return (sweep - lowpass(sweep, 600)) * np.sin(np.pi * t / length) ** 3 * 1.2


def impact():
    t = t_(0.7)
    f = 40 + 90 * np.exp(-t * 22)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    crack = lowpass(noise(0.7), 3000) * np.exp(-t * 35) * 0.6
    return body + crack


def hit():
    t = t_(1.6)
    sub = np.sin(2 * np.pi * (48 + 60 * np.exp(-t * 10)) * t) * np.exp(-t * 2.5)
    air = lowpass(noise(1.6), 2500 + 4000 * np.exp(-t * 3)) * np.exp(-t * 4) * 0.5
    return sub + air


def pop():
    t = t_(0.12)
    f = 900 * np.exp(-t * 30) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)


def click():
    t = t_(0.06)
    nz = noise(0.06)
    nz = nz - lowpass(nz, 2500)
    return (nz * np.exp(-t * 120) + 0.5 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 90)) * 0.9


def tick():
    t = t_(0.03)
    nz = noise(0.03)
    return (nz - lowpass(nz, 4000)) * np.exp(-t * 200) * 0.6


def riser(length):
    t = t_(length)
    f = 200 * 2 ** (3 * t / length)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    air = lowpass(noise(length), 500 + 6000 * (t / length) ** 2) * 0.6
    return (tone + air) * (t / length) ** 1.8


def scan(length):
    t = t_(length)
    f = 600 + 900 * t / length
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 22 * t)) * 0.25
    return tone * np.sin(np.pi * t / length) ** 0.5


def ding():
    t = t_(0.9)
    return (np.sin(2 * np.pi * 1318.5 * t) + 0.5 * np.sin(2 * np.pi * 1975.5 * t) + 0.25 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t * 6) * 0.5


def chime():
    out_ = np.zeros(int(0.9 * SR))
    for k, f in enumerate((1046.5, 1318.5, 1568.0)):
        t = t_(0.9 - k * 0.07)
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) * 0.35
        i = int(k * 0.07 * SR)
        out_[i : i + len(s)] += s
    return out_


def buzz():
    t = t_(0.32)
    sq = np.sign(np.sin(2 * np.pi * 140 * t)) * 0.3 + np.sign(np.sin(2 * np.pi * 147 * t)) * 0.3
    return lowpass(sq, 1800) * np.minimum(1, t * 60) * np.exp(-t * 6)


def boing():
    t = t_(0.5)
    f = 180 + 220 * np.exp(-t * 6) * (1 + 0.3 * np.sin(2 * np.pi * 14 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 0.7


def shimmer():
    out_ = np.zeros(int(1.2 * SR))
    for k in range(8):
        f = 1800 + 400 * k
        t = t_(1.2 - k * 0.05)
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 5) * 0.08
        i = int(k * 0.05 * SR)
        out_[i : i + len(s)] += s
    return out_


for ev in events:
    at, kind = float(ev[0]), ev[1]
    g = float(ev[2]) if len(ev) > 2 else 1.0
    pan = float(rng.uniform(-0.25, 0.25))
    if kind == "whoosh":
        s = whoosh()
        add(s, at - len(s) / SR + 0.04, 0.55 * g, pan)
    elif kind == "impact":
        add(impact(), at, 0.6 * g)
    elif kind == "hit":
        add(hit(), at, 0.8 * g)
    elif kind == "pop":
        add(pop(), at, 0.45 * g, pan)
    elif kind == "click":
        add(click(), at, 0.6 * g, pan)
    elif kind == "tick":
        add(tick(), at, 0.35 * g, pan)
    elif kind == "swoosh":
        add(swoosh(), at, 0.45 * g, pan)
    elif kind == "riser":
        add(riser(float(ev[3]) if len(ev) > 3 else 1.5), at, 0.4 * g)
    elif kind == "scan":
        add(scan(float(ev[3]) if len(ev) > 3 else 1.0), at, 0.5 * g)
    elif kind == "ding":
        add(ding(), at, 0.4 * g, pan)
    elif kind == "chime":
        add(chime(), at, 0.45 * g, pan)
    elif kind == "buzz":
        add(buzz(), at, 0.4 * g)
    elif kind == "boing":
        add(boing(), at, 0.5 * g)
    elif kind == "shimmer":
        add(shimmer(), at, 0.7 * g)
    else:
        raise SystemExit(f"unknown sound {kind}")

fade_out = np.minimum(1, (n - np.arange(n)) / (0.8 * SR))
L *= fade_out
R *= fade_out
peak = max(np.abs(L).max(), np.abs(R).max(), 1e-6)
L = np.tanh(L / peak * 1.1) / np.tanh(1.1) * 0.89
R = np.tanh(R / peak * 1.1) / np.tanh(1.1) * 0.89
data = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(data.tobytes())
print("wrote", out, len(events), "sounds")
