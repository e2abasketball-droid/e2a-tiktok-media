#!/usr/bin/env python3
"""2-3 Zone V2: splice ONE Deuce pickup take into the V1 take (the narration is NOT regenerated).
Owner V2 brief sec. 11: new hook 'FIVE DEFENDERS. ONE GAP. WATCH IT OPEN.' and rehook 'But what happens when the
defense collapses?'. Pickup = ONE eleven_v4 generation (bnFpeATgm9EQf3OKUClG, 130.99 credits) holding only those two lines.
  pickup[hook]           replaces V1 'FIVE defenders. ONE gap they hate. Right... HERE.'
  pickup[rehook]         replaces V1 'So the zone squeezes the middle.' (same picture: the zone collapses to the middle)
Every cut is made in the quietest 20 ms inside a NATURAL silence of its source (silencedetect -45 dB), 8 ms fades,
and each pickup segment is gain-matched (speech-gated RMS) to the V1 take. Writes:
  public/tactical/zona23/voice-v2-raw.wav  (gitignored; rebuilt by this script from the two committed mp3)
  tactical/episodes/zona23-v2-voice.words-raw.json  (Scribe words of both takes, re-timed)
Usage: python3 tactical/episodes/_splice-zona23-v2.py"""
import json, os, subprocess
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, '..', '..', 'public', 'tactical', 'zona23')
SR = 44100


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(P, f), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def quiet_cut(x, a, b):
    """quietest 20 ms window inside [a, b] s -> its centre (s)"""
    w = int(0.02 * SR)
    i0, i1 = int(a * SR), int(b * SR) - w
    best, bi = 1e9, i0
    for i in range(i0, max(i0 + 1, i1), int(0.005 * SR)):
        e = float(np.mean(x[i:i + w] ** 2))
        if e < best:
            best, bi = e, i
    return (bi + w / 2) / SR


def speech_rms(x):
    hop = int(0.02 * SR)
    n = len(x) // hop
    r = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    g = r[20 * np.log10(r) > -35]
    return float(np.sqrt(np.mean(g ** 2)))


def fade(seg):
    n = int(0.008 * SR)
    seg = seg.copy()
    seg[:n] *= np.linspace(0, 1, n)
    seg[-n:] *= np.linspace(1, 0, n)
    return seg


v1, pk = load('voice-raw.mp3'), load('pickup-v2-raw.mp3')
w1 = json.load(open(os.path.join(D, 'zona23-voice.words-raw.json')))
wp = json.load(open(os.path.join(D, 'zona23-v2-pickup.words-raw.json')))
# natural silences (measured with silencedetect n=-45dB d=0.06 on each source)
c_pk = quiet_cut(pk, 3.811, 4.2485)      # pickup: after 'OPEN.' / before 'But'
c_v1a = quiet_cut(v1, 4.732, 5.078)      # V1: after 'HERE.' / before 'Two'
c_v1b = quiet_cut(v1, 16.737, 17.026)    # V1: after 'Layup.' / before 'So'
c_v1c = quiet_cut(v1, 18.730, 19.060)    # V1: after 'middle.' / before 'Now'
g = speech_rms(v1) / speech_rms(pk)
segs = [('pk', 0.0, c_pk), ('v1', c_v1a, c_v1b), ('pk', c_pk, len(pk) / SR), ('v1', c_v1c, len(v1) / SR)]
out, words, t = [], [], 0.0
for src, a, b in segs:
    x, ww = (pk * g, wp) if src == 'pk' else (v1, w1)
    out.append(fade(x[int(a * SR):int(b * SR)]))
    for w in ww:
        if w['start'] >= a - 0.02 and w['end'] <= b + 0.08:
            words.append({'text': w['text'], 'start': round(w['start'] - a + t, 3), 'end': round(min(w['end'], b) - a + t, 3)})
    t += b - a
y = np.concatenate(out)
dst = os.path.join(P, 'voice-v2-raw.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le', dst], input=y.astype(np.float32).tobytes(), check=True)
json.dump(words, open(os.path.join(D, 'zona23-v2-voice.words-raw.json'), 'w'), indent=0)
print(f'cuts pickup {c_pk:.3f} | v1 {c_v1a:.3f} {c_v1b:.3f} {c_v1c:.3f} | pickup gain {20 * np.log10(g):+.2f} dB | {len(y) / SR:.2f} s, {len(words)} words')
print(' '.join(w['text'] for w in words))
