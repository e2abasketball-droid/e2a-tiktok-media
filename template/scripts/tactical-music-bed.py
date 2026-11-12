#!/usr/bin/env python3
"""Fit a pre-made instrumental (e.g. music/cinematic/cine-09.mp3, E2A's licensed library) under a
Tactical3D episode without re-composing it:

  1. choose the start offset inside the track so its strongest hits land on the episode's key actions
     (screens, release, make, backdoor cut) and its own ending lands on the closing card,
  2. soft-duck it under the narration (default -4 dB, 80 ms attack / 350 ms release),
  3. scale it so the bed has the SAME integrated loudness as a reference bed (the previous version),
     i.e. no louder music, and fade the edges.

  python3 scripts/tactical-music-bed.py --track ../music/cinematic/cine-09.mp3 \
     --voice public/tactical/stagger/voice.mix.wav --duration 33.333 \
     --events 11.49,13.06,14.96,15.93,21.73 --end-card 31.36 \
     --match public/tactical/stagger/music.mp3 --out public/tactical/stagger/music-v2.mp3 --report r.json
"""
import argparse
import json
import re
import subprocess

import numpy as np

SR = 48000


def load(p, ch=2):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def lufs(x):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'ebur128', '-f', 'null', '-'], input=x.astype(np.float32).tobytes(), capture_output=True)
    s = p.stderr.decode()
    return float(re.findall(r'I:\s+(-?[\d.]+)', s[s.rfind('Summary'):])[0])


def onset_env(x, hop=0.01):
    m = x.mean(1)
    n, h = 2048, int(hop * SR)
    fr = np.lib.stride_tricks.sliding_window_view(m, n)[::h] * np.hanning(n)
    S = np.log1p(np.abs(np.fft.rfft(fr, axis=1)))
    f = np.maximum(0, np.diff(S, axis=0)).sum(1)
    f = (f - np.median(f)) / (np.percentile(f, 99) - np.median(f) + 1e-9)
    return np.concatenate([[0], f]), hop


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--track', required=True)
    ap.add_argument('--voice', required=True)
    ap.add_argument('--duration', type=float, required=True)
    ap.add_argument('--events', required=True)
    ap.add_argument('--end-card', type=float)
    ap.add_argument('--match', required=True, help='reference bed whose integrated loudness is kept')
    ap.add_argument('--duck-db', type=float, default=4.0)
    ap.add_argument('--offset', type=float, help='force the start offset in the track')
    ap.add_argument('--out', required=True)
    ap.add_argument('--report')
    a = ap.parse_args()
    ev = [float(v) for v in a.events.split(',')]
    tr = load(a.track)
    tdur = len(tr) / SR
    env, hop = onset_env(tr)
    rms = np.sqrt(np.convolve(tr.mean(1) ** 2, np.ones(int(0.5 * SR)) / int(0.5 * SR), 'same'))[:: int(hop * SR)]
    rms_db = 20 * np.log10(rms + 1e-9)
    hi = np.percentile(rms_db, 90)
    # offsets that leave the whole video inside the track
    offs = np.arange(0, tdur - a.duration - 0.05, hop)
    scores = []
    for o in offs:
        sc = 0.0
        for t in ev:
            i0, i1 = int((o + t - 0.06) / hop), int((o + t + 0.06) / hop) + 1
            sc += env[i0:i1].max()
        # keep the bed energetic: penalise a quiet stretch inside the narration (before the end card)
        lim = a.end_card if a.end_card else a.duration
        seg = rms_db[int(o / hop): int((o + lim) / hop)]
        sc -= 0.15 * max(0.0, hi - 6 - seg.min())
        scores.append(sc)
    scores = np.array(scores)
    o = a.offset if a.offset is not None else float(offs[int(np.argmax(scores))])
    x = tr[int(o * SR): int(o * SR) + int(a.duration * SR)]
    x = np.pad(x, ((0, max(0, int(a.duration * SR) - len(x))), (0, 0)))
    # soft ducking from the narration envelope
    v = load(a.voice).mean(1)[: len(x)]
    v = np.pad(v, (0, len(x) - len(v)))
    H = int(0.01 * SR)
    ve = np.sqrt(np.mean(v[: len(v) // H * H].reshape(-1, H) ** 2, axis=1))
    ve_db = 20 * np.log10(ve + 1e-9)
    act = (ve_db > ve_db.max() - 32).astype(float)
    g = np.zeros_like(act)
    for i in range(len(act)):
        prev = g[i - 1] if i else 0
        k = 0.01 / (0.08 if act[i] > prev else 0.35)
        g[i] = prev + (act[i] - prev) * min(1.0, k * 3)
    gain = 10 ** (-a.duck_db * g / 20)
    gain = np.repeat(gain, H)[: len(x)]
    gain = np.pad(gain, (0, len(x) - len(gain)), constant_values=gain[-1])
    x = x * gain[:, None]
    # edges: 120 ms fade-in, fade-out over the last 0.7 s
    fi, fo = int(0.12 * SR), int(0.7 * SR)
    x[:fi] *= np.linspace(0, 1, fi)[:, None]
    x[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    ref = load(a.match)
    target = lufs(ref)
    cur = lufs(x)
    x *= 10 ** ((target - cur) / 20)
    final = lufs(x)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '256k', a.out], input=x.astype(np.float32).tobytes(), check=True)
    hits = []
    for t in ev:
        i0, i1 = int((o + t - 0.06) / hop), int((o + t + 0.06) / hop) + 1
        j = i0 + int(np.argmax(env[i0:i1]))
        hits.append({'event_s': t, 'hit_s': round(j * hop - o, 3), 'strength': round(float(env[j]), 2)})
    rep = {'track': a.track, 'offset_s': round(o, 2), 'duck_db': a.duck_db, 'reference_lufs': target, 'bed_lufs': final, 'event_hits': hits,
           'onset_strength_percentile_of_hits': [round(float((env < h['strength']).mean() * 100), 1) for h in hits]}
    print(json.dumps(rep, indent=1))
    if a.report:
        json.dump(rep, open(a.report, 'w'), indent=1)


if __name__ == '__main__':
    main()
