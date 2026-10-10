"""Onset envelope, tempo and beat grid of a wav (numpy only). Prints JSON."""
import json, sys, wave
import numpy as np
w = wave.open(sys.argv[1]); sr = w.getframerate(); ch = w.getnchannels()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float).reshape(-1, ch).mean(1) / 32768
hop = 441  # 10 ms
win = 2048
frames = (len(x) - win) // hop
spec_prev = None
flux = np.zeros(frames)
lowflux = np.zeros(frames)
wnd = np.hanning(win)
freqs = np.fft.rfftfreq(win, 1 / sr)
for i in range(frames):
    s = np.abs(np.fft.rfft(x[i * hop:i * hop + win] * wnd))
    s = np.log1p(100 * s)
    if spec_prev is not None:
        d = np.maximum(0, s - spec_prev)
        flux[i] = d.sum()
        lowflux[i] = d[freqs < 200].sum()
    spec_prev = s
def norm(v):
    v = v - np.convolve(v, np.ones(50) / 50, mode='same')
    v = np.maximum(v, 0)
    return v / (v.max() or 1)
on = norm(flux); low = norm(lowflux)
# tempo by autocorrelation in 80..170 bpm
ac = np.correlate(on, on, mode='full')[len(on) - 1:]
lags = np.arange(len(ac))
best = max(range(int(6000 / 170), int(6000 / 80)), key=lambda L: ac[L])
period = best / 100.0
# beat phase: maximise onset sum on the grid
phases = np.arange(0, period, 0.01)
score = [sum(on[int(round((p + k * period) * 100))] for k in range(int((frames / 100 - p) / period))) for p in phases]
phase = phases[int(np.argmax(score))]
beats = [round(phase + k * period, 3) for k in range(int((frames / 100 - phase) / period))]
json.dump({"bpm": round(60 / period, 2), "period": period, "beats": beats,
           "onset": [round(float(v), 3) for v in on], "low": [round(float(v), 3) for v in low]}, open(sys.argv[2], 'w'))
print("bpm", round(60 / period, 2), "period", period, "phase", phase, "beats", len(beats))
