#!/usr/bin/env python3
"""Pistol Fake Handoff voices (2026-11-20, from _voice-ddtr2.py). ONE Deuce take for the body + hook A (voice-raw.mp3) and
ONE short take for hook B (hookB-raw.mp3); never re-synthesised.
  python3 scripts/tactical-voice.py tactical/episodes/pfh-a.json        (A: gaps (digital silence) -> voice-a.wav, pfh-a.words.json)
  python3 tactical/episodes/_voice-pfh.py                               (B: hook B take to the splice, then A; mixes)
B = hook B take (same 0.1 s preroll) until T (in A's silence between "lie." and "The", after hook B ends at 2.74 s: T = 2.78 s), then the A
track from T: the body is sample-identical in A and B. Mix chain (E2A voice standard): highpass 80, +2 dB at 3.2 kHz,
compressor 2.5:1, loudnorm I -16 / TP -2 / LRA 7. Both tracks end with the take's own room tone faded out once, then silence, to the episode end (no looped slice)."""
import json, os, subprocess
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)); T_ = os.path.dirname(os.path.dirname(D)); P = os.path.join(T_, 'public', 'tactical', 'pfh')
SR = 44100; PRE = 0.1; END = 30.0   # episode end (s): last shot "@end"
rd = lambda f: np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, dtype=np.float32).copy()
wr = lambda f, y: subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le', f], input=y.astype(np.float32).tobytes(), check=True)
wa = json.load(open(os.path.join(D, 'pfh-a.words.json')))
wh = json.load(open(os.path.join(D, 'pfh-hookb.words-raw.json')))
a = rd(os.path.join(P, 'voice-a.wav'))
hb = rd(os.path.join(P, 'hookB-raw.mp3'))
i_two = next(i for i, w in enumerate(wa) if w['text'] == 'The')   # first word of the body
T = round(max((wa[i_two - 1]['end'] + wa[i_two]['start']) / 2, PRE + wh[-1]['end'] + 0.04), 3)   # after the B line
n = int(T * SR)
def fill(k, tone):
    """k samples of room tone WITHOUT looping (2026-11-20 audio fix): np.resize() repeated the 0.217 s slice with a hard
    seam every 0.217 s (four audible ticks at the end of V2-Hook-A, 27.5-30.0 s). Now: the slice once, faded out over its
    length, then digital silence (the music bed carries the tail)."""
    k = max(0, int(k)); m = min(k, len(tone))
    seg = tone[:m] * (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, m, dtype=np.float32))) if m else tone[:0]
    return np.concatenate([seg, np.zeros(k - m, np.float32)]).astype(np.float32)
def pad(y, tone):
    """the take's own end (room tone after the last word) fades out over its last 0.15 s, then silence to END"""
    k = int(END * SR) - len(y)
    if k <= 0:
        return y
    f = min(len(y), int(0.15 * SR)); y = y.copy(); y[-f:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, f, dtype=np.float32))
    return np.concatenate([y, np.zeros(k, np.float32)])
tone = a[int((wa[i_two - 1]['end'] + 0.08) * SR): int((wa[i_two]['start'] - 0.08) * SR)]   # room tone of the take (0.217 s, used once, never looped)
head = np.concatenate([tone[:int(PRE * SR)], hb])[:n]   # 0.1 s < the 0.217 s slice: no loop
head = np.concatenate([head, fill(n - len(head), tone)])
f = int(0.008 * SR); ramp = np.linspace(0, 1, f, dtype=np.float32)
b = np.concatenate([head, a[n:]]); b[n - f:n] = head[n - f:n] * ramp[::-1] + a[n - f:n] * ramp
a, b = pad(a, tone), pad(b, tone)
wr(os.path.join(P, 'voice-a.wav'), a); wr(os.path.join(P, 'voice-b.wav'), b)
wb = [{'text': w['text'], 'start': round(w['start'] + PRE, 3), 'end': round(w['end'] + PRE, 3)} for w in wh] + wa[i_two:]
json.dump(wb, open(os.path.join(D, 'pfh-b.words.json'), 'w'), indent=0)
for v in 'ab':
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(P, f'voice-{v}.wav'), '-af',
                    'highpass=f=80,equalizer=f=3200:t=q:w=1.0:g=2.0,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-2:LRA=7',
                    '-ar', '48000', '-ac', '2', os.path.join(P, f'voice-{v}.mix.wav')], check=True)
print('splice T', T, 'hook B ends', round(PRE + wh[-1]['end'], 3), 'A "The"', wa[i_two]['start'], 'len', len(a) / SR)
