#!/usr/bin/env python3
"""HIDE IN GAMES V4: composite raw narration from three Deuce eleven_v4 blocks (one take each, never regenerated):
  A main narration   683 cr  flow 3bOayrI8XimxPaEcpaUW  ('One miss.' .. 'One more pass.')
  B #8's thought      72 cr  flow Oqed1CPIlUKJ2TJYKDfC  ('What if I miss again?', quiet and close)
  C conclusion       258 cr  flow a3QtJZC0Ne7jywtozLq4  ('Even the best players miss.' .. 'Make the next read.')
Order: A[.. 'that miss.'] + B + A['He starts' ..] + C. Seams are cut at the quietest 20 ms inside natural silence
(kept short, ~0.1 s, so tactical-voice.py can set every pause with room tone). B is matched to A's loudness, then
-3 dB and a touch of low-mid warmth / softer top so it reads as an inner voice.
Writes public/tactical/hide4/voice-raw.mp3 and tactical/episodes/hide4.words-raw.json"""
import json, os, re, subprocess
import numpy as np
T_ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SR = 44100
P = lambda *a: os.path.join(T_, *a)
TMP = '/tmp/claude-0/hide4'
os.makedirs(TMP, exist_ok=True)


def load(f, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', f] + (['-af', af] if af else []) + ['-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).copy()


def rms_db(x, t, w=0.01):
    i = int(t * SR)
    s = x[i:i + int(w * SR)]
    return 10 * np.log10(float(np.mean(s ** 2)) + 1e-12)


def onset(x, a, b, th=-40):
    """first 10 ms frame above th dB between a and b"""
    t = a
    while t < b:
        if rms_db(x, t) > th:
            return t
        t += 0.005
    return b


def offset(x, a, b, th=-40):
    """last 10 ms frame above th dB between a and b"""
    t = b
    while t > a:
        if rms_db(x, t) > th:
            return t + 0.01
        t -= 0.005
    return a


def fade(seg, ms=8):
    n = int(ms / 1000 * SR)
    seg = seg.copy()
    seg[:n] *= np.linspace(0, 1, n)
    seg[-n:] *= np.linspace(1, 0, n)
    return seg


def lufs(seg):
    open(f'{TMP}/_m.f32', 'wb').write(seg.astype(np.float32).tobytes())
    r = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', f'{TMP}/_m.f32',
                        '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])


A = load(P('public/tactical/hide4/voice-a.mp3'))
B = load(P('public/tactical/hide4/voice-b.mp3'), 'equalizer=f=220:t=q:w=1.0:g=2.0,lowpass=f=7000')
C = load(P('public/tactical/hide4/voice-c.mp3'))
wa, wb, wc = (json.load(open(P(f'tactical/episodes/hide4.words-{k}.json'))) for k in 'abc')
ix = lambda ws, t: next(i for i, w in enumerate(ws) if w['text'] == t)

PAD = 0.06   # natural silence kept on each side of a seam
# A1: start .. 'that miss.'   A2: 'He starts' .. end
i_miss = [i for i, w in enumerate(wa) if w['text'] == 'miss.'][1]
s0 = wa[i_miss]['end'] - 0.2          # 'that miss.' tail fades below -55 dB, then 'He starts' rises
while rms_db(A, s0) > -55:
    s0 += 0.005
a1_end = s0 + PAD
a2_beg = onset(A, s0, s0 + 0.6) - PAD
b_beg = onset(B, 0.0, 0.6) - PAD
b_end = min(len(B) / SR, offset(B, 1.2, len(B) / SR - 0.02, th=-58) + PAD)   # breathy tail of 'again?'
c_beg = max(0.0, onset(C, 0.0, 0.4) - PAD)
a_end = offset(A, 32.0, len(A) / SR - 0.02, th=-58) + PAD
c_end = min(len(C) / SR, offset(C, 9.8, len(C) / SR - 0.02, th=-58) + 0.12)

A1, A2 = A[:int(a1_end * SR)], A[int(a2_beg * SR):int(a_end * SR)]
Bs, Cs = B[int(b_beg * SR):int(b_end * SR)], C[int(c_beg * SR):int(c_end * SR)]
gA = lufs(np.concatenate([A1, A2]))
Bs = Bs * 10 ** ((gA - lufs(Bs) - 3.0) / 20)
Cs = Cs * 10 ** ((gA - lufs(Cs)) / 20)
segs = [(A1, 0.0, wa[:i_miss + 1]),
        (Bs, b_beg, wb),
        (A2, a2_beg, wa[i_miss + 1:]),
        (Cs, c_beg, wc)]
out, words, off = [], [], 0.0
for seg, src0, ws in segs:
    out.append(fade(seg))
    words += [{'text': w['text'], 'start': round(max(0, w['start'] - src0) + off, 3), 'end': round(w['end'] - src0 + off, 3)} for w in ws]
    off += len(seg) / SR
out = np.concatenate(out)
open(f'{TMP}/raw.f32', 'wb').write(out.astype(np.float32).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', f'{TMP}/raw.f32',
                '-c:a', 'libmp3lame', '-b:a', '192k', P('public/tactical/hide4/voice-raw.mp3')], check=True)
json.dump(words, open(P('tactical/episodes/hide4.words-raw.json'), 'w'), indent=0)
print(f'A1<{a1_end:.3f}  B {b_beg:.3f}-{b_end:.3f}  A2 {a2_beg:.3f}-{a_end:.3f}  C {c_beg:.3f}-{c_end:.3f}  '
      f'gain B {gA - lufs(B):+.1f}(-3) total {len(out) / SR:.2f}s words {len(words)}')
