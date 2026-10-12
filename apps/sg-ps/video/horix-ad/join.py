import wave, numpy as np
w = wave.open('dyn.wav'); sr = w.getframerate()
X = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float).reshape(-1, 2) / 32768
mono = X.mean(1)
hop = 128; win = 1024
fr = np.lib.stride_tricks.sliding_window_view(mono, win)[::hop] * np.hanning(win)
S = np.abs(np.fft.rfft(fr, axis=1)); f = np.fft.rfftfreq(win, 1 / sr)
on = np.maximum(0, np.diff(np.log1p(S[:, (f > 30) & (f < 8000)].sum(1) * 10), prepend=0))
fps = sr / hop; tt = np.arange(len(on)) / fps
P = 60 / 166.7
import sys
segs = eval(sys.argv[1]) if len(sys.argv) > 1 else [(0.0, 39.857), (42.311, 51.377), (53.831, 70.577), (73.029, 97.457)]
OUT = sys.argv[2] if len(sys.argv) > 2 else 'dyn-joined.wav'
def phase(s0, s1):
    ph = np.linspace(0, P, 400, endpoint=False)
    n = np.arange(int((s0 + 1.5) / P), int((s1 - 0.5) / P))
    sc = [np.interp(n * P + p, tt, on).sum() for p in ph]
    return ph[int(np.argmax(sc))]
def first_onset(s0, s1):
    i0, i1 = int(s0 * fps), int(s1 * fps); seg = on[i0:i1]
    return tt[i0 + int(np.argmax(seg > seg.max() * 0.3))]
FIX = eval(sys.argv[3]) if len(sys.argv) > 3 else {3: 0.12}  # measured on the joined file: part 4's quiet intro biased its phase estimate by a third of a beat
out = []; cur = 0.0; grid = None; report = []
for k, (s0, s1) in enumerate(segs):
    ph = phase(s0, s1); fo = first_onset(s0, s1)
    lead = max(0.0, fo - s0 - 0.05)  # keep a little air before the first hit
    a = s0 + (fo - s0 - min(lead, 1.0)) if k else s0
    if k == 0:
        shift = 0.0; grid = ph
    else:
        # place this part so its beats continue the previous grid, starting right after the previous part ends
        target = cur + (fo - a)  # where its first onset would land with no gap
        base = fo + 0  # its first onset sits at phase ph locally: fo ≈ ph + mP + e
        e = (fo - ph) % P
        m = int(np.ceil((target - 0.01 - grid - e) / P))
        t_on = grid + m * P + e
        shift = t_on - fo + FIX.get(k, 0.0)
    seg = X[int(a * sr):int(s1 * sr)]
    start = int(round((a + shift) * sr))
    out.append((start, seg)); report.append((k, a, s1, a + shift, s1 + shift))
    cur = s1 + shift
L = max(s + len(g) for s, g in out)
Y = np.zeros((L, 2))
for s, g in out:
    fade = np.ones(len(g)); n = int(0.01 * sr); fade[:n] = np.linspace(0, 1, n)
    Y[s:s + len(g)] += g * fade[:, None]
Y = np.clip(Y, -1, 1)
with wave.open(OUT, 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(sr); o.writeframes((Y * 32767).astype(np.int16).tobytes())
for r in report: print('part %d: src %.3f-%.3f -> out %.3f-%.3f' % r)
print('length %.2f s' % (L / sr))
