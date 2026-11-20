#!/usr/bin/env python3
"""Double Drag V2 voices (2026-11-20). ONE Deuce take for the body + hook A (v2-voice-raw.mp3) and ONE short take for
hook B (v2-hookB-raw.mp3); never re-synthesised.
  python3 scripts/tactical-voice.py tactical/episodes/ddtr2-a.json      (A: gaps -> v2-voice-a.wav, ddtr2-a.words.json)
  python3 tactical/episodes/_voice-ddtr2.py                             (B: hook B take to the splice, then A; mixes)
B = hook B take (same 0.1 s preroll) until T (the middle of A's natural silence between "foot." and "Two"), then the A
track from T: the body is sample-identical in A and B. Mix chain (E2A voice standard): highpass 80, +2 dB at 3.2 kHz,
compressor 2.5:1, loudnorm I -16 / TP -2 / LRA 7. Both tracks are padded with the take's own room tone to the episode end."""
import json, os, subprocess
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)); T_ = os.path.dirname(os.path.dirname(D)); P = os.path.join(T_, 'public', 'tactical', 'ddtr')
SR = 44100; PRE = 0.1; END = 30.1   # episode end (s): last shot "@end"
rd = lambda f: np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, dtype=np.float32).copy()
wr = lambda f, y: subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le', f], input=y.astype(np.float32).tobytes(), check=True)
wa = json.load(open(os.path.join(D, 'ddtr2-a.words.json')))
wh = json.load(open(os.path.join(D, 'ddtr2-hookb.words-raw.json')))
a = rd(os.path.join(P, 'v2-voice-a.wav'))
hb = rd(os.path.join(P, 'v2-hookB-raw.mp3'))
i_two = next(i for i, w in enumerate(wa) if w['text'] == 'Two')
T = round((wa[i_two - 1]['end'] + wa[i_two]['start']) / 2, 3)
n = int(T * SR)
pad = lambda y, tone: np.concatenate([y, np.resize(tone, max(0, int(END * SR) - len(y)))])
tone = a[int((wa[i_two - 1]['end'] + 0.08) * SR): int((wa[i_two]['start'] - 0.08) * SR)]   # room tone of the take
head = np.concatenate([np.resize(tone, int(PRE * SR)), hb])[:n]
head = np.concatenate([head, np.resize(tone, n - len(head))])
f = int(0.008 * SR); ramp = np.linspace(0, 1, f, dtype=np.float32)
b = np.concatenate([head, a[n:]]); b[n - f:n] = head[n - f:n] * ramp[::-1] + a[n - f:n] * ramp
a, b = pad(a, tone), pad(b, tone)
wr(os.path.join(P, 'v2-voice-a.wav'), a); wr(os.path.join(P, 'v2-voice-b.wav'), b)
wb = [{'text': w['text'], 'start': round(w['start'] + PRE, 3), 'end': round(w['end'] + PRE, 3)} for w in wh] + wa[i_two:]
json.dump(wb, open(os.path.join(D, 'ddtr2-b.words.json'), 'w'), indent=0)
for v in 'ab':
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(P, f'v2-voice-{v}.wav'), '-af',
                    'highpass=f=80,equalizer=f=3200:t=q:w=1.0:g=2.0,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-2:LRA=7',
                    '-ar', '48000', '-ac', '2', os.path.join(P, f'v2-voice-{v}.mix.wav')], check=True)
print('splice T', T, 'hook B ends', round(PRE + wh[-1]['end'], 3), 'A "Two"', wa[i_two]['start'], 'len', len(a) / SR)
