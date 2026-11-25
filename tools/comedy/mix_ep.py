#!/usr/bin/env python3
"""E2A YouTube Comedy - episode audio mix.
dialogue.wav (+ light gym room reverb) + a few intentional one-shots + very low room tone,
then loudness-normalised to -14 LUFS / -1.5 dBTP (YouTube). No music, no ball-bounce SFX.
Usage: python3 tools/comedy/mix_ep.py <episode_dir with dialogue.wav + sfx.json> <sfx_dir> <out.wav>
sfx.json: {"duration": s, "cues": [{"file": "swish.mp3", "at": 0.32, "gain_db": -12, "lowpass": 0, "fade": 0}]}"""
import json, os, subprocess, sys, wave
import numpy as np

SR = 48000
ep, sfx_dir, out = sys.argv[1], sys.argv[2], sys.argv[3]
cfg = json.load(open(os.path.join(ep, 'sfx.json')))
N = int(cfg['duration'] * SR)

def load(path, ch=2):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64).reshape(-1, ch).T

def lowpass(x, fc):
    # one-pole, applied twice
    a = np.exp(-2 * np.pi * fc / SR)
    for _ in range(2):
        y = np.zeros_like(x)
        acc = np.zeros(x.shape[0])
        for i in range(x.shape[1]):
            acc = (1 - a) * x[:, i] + a * acc
            y[:, i] = acc
        x = y
    return x

rng = np.random.default_rng(11)
mix = np.zeros((2, N))
# dialogue (mono -> centre) + short gym reverb (synthetic IR, ~0.7 s, -19 dB wet)
d = load(os.path.join(ep, 'dialogue.wav'), 1)[0]
d = np.pad(d, (0, max(0, N - len(d))))[:N]
L = int(0.7 * SR)
t = np.arange(L) / SR
irL = rng.standard_normal(L) * np.exp(-t / 0.16)
irR = rng.standard_normal(L) * np.exp(-t / 0.16)
irL[: int(0.012 * SR)] = 0
irR[: int(0.017 * SR)] = 0
irL /= np.sqrt(np.sum(irL ** 2))
irR /= np.sqrt(np.sum(irR ** 2))
wet = 10 ** (-19 / 20)
from numpy.fft import rfft, irfft
n = 1 << int(np.ceil(np.log2(N + L)))
D = rfft(d, n)
mix[0] += d + wet * irfft(D * rfft(irL, n), n)[:N]
mix[1] += d + wet * irfft(D * rfft(irR, n), n)[:N]
# room tone: soft filtered noise, about -56 dBFS
noise = rng.standard_normal((2, N))
noise = lowpass(noise[:, :], 900) if N < 3_000_000 else noise
noise *= 10 ** (-56 / 20) / (np.sqrt(np.mean(noise ** 2)) + 1e-12)
mix += noise
# one-shots
for c in cfg['cues']:
    x = load(os.path.join(sfx_dir, c['file']))
    if c.get('trim'):
        x = x[:, : int(c['trim'] * SR)]
    if c.get('lowpass'):
        x = lowpass(x, c['lowpass'])
    f = int(c.get('fade', 0.03) * SR)
    if f:
        x[:, -f:] *= np.linspace(1, 0, f)
    x *= 10 ** (c['gain_db'] / 20)
    s0 = int(c['at'] * SR)
    e = min(N, s0 + x.shape[1])
    mix[:, s0:e] += x[:, : e - s0]
    print('cue', c['file'], c['at'], c['gain_db'])
# 50 ms fade in/out
f = int(0.05 * SR)
mix[:, :f] *= np.linspace(0, 1, f)
mix[:, -f:] *= np.linspace(1, 0, f)
tmp = out + '.raw.wav'
pcm = (np.clip(mix.T, -1, 1) * 32767).astype(np.int16)
w = wave.open(tmp, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
# two-pass loudnorm
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
js = json.loads(r[r.rfind('{'):r.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
      f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', af, '-ar', str(SR), out], check=True)
os.remove(tmp)
print('wrote', out, 'input I', js['input_i'])
