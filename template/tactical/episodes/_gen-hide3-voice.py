#!/usr/bin/env python3
"""HIDE IN GAMES V3: composite raw narration. Reuses the V2 take (692 cr, never regenerated) and adds ONE new Deuce
eleven_v4 take (294 cr, flow zktE4XNkK1LM0dmi24xi) with the new ending. Cuts are made at the quietest 20 ms
inside the natural silence between two words, with 8 ms fades.
  A  V2 raw  0 .. 'somewhere else.'            (hook, practice/game, miss, possession 2)
  B  V2 raw  'Breathe out.' .. 'Call for it.'  ('Give yourself one job.' and the old ending are dropped)
  C  new take 'The defender closes out.' .. 'Read the play in front of you.'
Writes public/tactical/hide3/voice-raw.mp3 and tactical/episodes/hide3.words-raw.json"""
import json, os, re, subprocess
import numpy as np
T_ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SR = 44100
P = lambda *a: os.path.join(T_, *a)


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def quiet(x, a, b):
    """time of the quietest 20 ms window between a and b"""
    w = int(0.02 * SR)
    i0, i1 = int(a * SR), max(int(b * SR) - w, int(a * SR) + 1)
    best = min(range(i0, i1, int(0.005 * SR)), key=lambda i: float(np.mean(x[i:i + w] ** 2)))
    return (best + w // 2) / SR


def fade(seg, ms=8):
    n = int(ms / 1000 * SR)
    seg = seg.copy()
    seg[:n] *= np.linspace(0, 1, n)
    seg[-n:] *= np.linspace(1, 0, n)
    return seg


def lufs(seg):
    open('/tmp/claude-0/hide3/_m.f32', 'wb').write(seg.astype(np.float32).tobytes())
    r = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '/tmp/claude-0/hide3/_m.f32',
                        '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])


v2 = load(P('public/tactical/hide2/voice-raw.mp3'))
nw = load(P('public/tactical/hide3/voice-new.mp3'))
w2 = json.load(open(P('tactical/episodes/hide2.words-raw.json')))
wn, _tag = [], False
for w in json.load(open(P('tactical/episodes/hide3.words-new.json'))):   # drop [tone tags], which can span several tokens
    if w['text'].startswith('['):
        _tag = True
    if not _tag:
        wn.append(w)
    if w['text'].endswith(']'):
        _tag = False

a_end = quiet(v2, 17.64, 17.92)
b0, b1 = quiet(v2, 19.56, 19.76), quiet(v2, 26.06, 26.16)
c0, c1 = quiet(nw, 0.0, 0.10), min(len(nw) / SR, 13.68 + 0.6)
A, B, C = v2[: int(a_end * SR)], v2[int(b0 * SR): int(b1 * SR)], nw[int(c0 * SR): int(c1 * SR)]
gA = lufs(np.concatenate([A, B]))
gC = lufs(C)
C = C * 10 ** ((gA - gC) / 20)            # match the new take's loudness to the V2 take
segs = [fade(A), fade(B), fade(C)]
out = np.concatenate(segs)
oB, oC = len(A) / SR, (len(A) + len(B)) / SR
words = [w for w in w2 if w['start'] < a_end] + \
        [{**w, 'start': round(w['start'] - b0 + oB, 3), 'end': round(w['end'] - b0 + oB, 3)} for w in w2 if b0 <= w['start'] and w['start'] < b1] + \
        [{'text': w['text'], 'start': round(w['start'] - c0 + oC, 3), 'end': round(w['end'] - c0 + oC, 3)} for w in wn]
open('/tmp/claude-0/hide3/raw.f32', 'wb').write(out.astype(np.float32).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '/tmp/claude-0/hide3/raw.f32',
                '-c:a', 'libmp3lame', '-b:a', '192k', P('public/tactical/hide3/voice-raw.mp3')], check=True)
json.dump(words, open(P('tactical/episodes/hide3.words-raw.json'), 'w'), indent=0)
print(f'cuts A<{a_end:.3f} B {b0:.3f}-{b1:.3f} C {c0:.3f}-{c1:.3f}  gain C {gA - gC:+.1f} dB  total {len(out) / SR:.2f}s  words {len(words)}')
