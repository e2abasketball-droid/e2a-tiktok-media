#!/usr/bin/env python3
"""Level a narration take phrase by phrase (owner brief: audible intensity changes but a comfortable final volume).
Each phrase [a, b] (seconds in the take) gets a constant gain so its active-speech RMS lands on its target dBFS;
gains change only inside the silence between phrases, with 40 ms ramps. Never time-stretches.
Usage: phrase-level.py in.mp3 out.wav '[[a, b, target_db], ...]'"""
import json, subprocess, sys
import numpy as np
SR = 44100
src, dst, plan = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, dtype=np.float32).copy()
def act_rms(s):
    h = int(0.02 * SR); fr = s[:len(s) // h * h].reshape(-1, h); r = np.sqrt((fr ** 2).mean(1)); r = r[r > 10 ** (-50 / 20)]
    return 20 * np.log10(np.sqrt((r ** 2).mean()))
g = np.ones(len(x), dtype=np.float64)
gains = []
for i, (a, b, tgt) in enumerate(plan):
    gdb = tgt - act_rms(x[int(a * SR):int(b * SR)]); gains.append(round(float(gdb), 1))
    lo = 0 if i == 0 else int((plan[i - 1][1] + a) / 2 * SR)
    hi = len(x) if i == len(plan) - 1 else int((b + plan[i + 1][0]) / 2 * SR)
    g[lo:hi] = 10 ** (gdb / 20)
# 40 ms ramps at every gain change
k = int(0.04 * SR); ker = np.ones(k) / k
g = np.convolve(g, ker, mode='same'); g[:k] = g[k]; g[-k:] = g[-k - 1]
y = (x * g).astype(np.float32)
pk = np.abs(y).max()
if pk > 0.95: y *= 0.95 / pk
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le', dst], input=y.tobytes(), check=True)
print(json.dumps({"gains_db": gains, "peak": float(pk)}))
