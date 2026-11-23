#!/usr/bin/env python3
"""Re-edit an APPROVED narration take into a new order / selection of its own phrases (2026-11-23, 1-3-1 V2).
Nothing is synthesised, nothing is sped up or pitch-shifted, no word is cut in the middle: every segment is a run of
consecutive words of the take, cut only inside an acoustic silence (quietest 10 ms of the natural pause before the first
word and after the last word, like scripts/tactical-voice.py), with 8 ms fades. Between segments: digital silence so the
TOTAL pause (natural tail + inserted + natural lead) equals the requested gap (owner rule: never pad with loops).
Spec (JSON):
  {"voiceRaw": "tactical/zone131/voice-raw.mp3", "wordsRaw": "<path to words-raw.json>", "voice": "tactical/x/voice-v2.wav",
   "preroll": 0.08, "tail": 0.6,
   "segments": [{"text": "One defender. Two corners.", "gap": 0.35, "why": "..."}, ...]}
  (gap = total silence after the segment; the last one's is ignored)
Writes public/<voice>, <spec>.words.json (new word timings) and <spec>.voice-report.json.
Usage: python3 scripts/tactical-voice-edit.py tactical/episodes/<x>/<spec>.json"""
import json, os, re, subprocess, sys
import numpy as np

SR = 44100
spec_file = sys.argv[1]
sp = json.load(open(spec_file))
words = json.load(open(sp['wordsRaw'] if os.path.isabs(sp['wordsRaw']) else os.path.join(os.path.dirname(spec_file), sp['wordsRaw'])))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
keys = [norm(w['text']) for w in words]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join('public', sp['voiceRaw']), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32).copy()
HOP = int(0.01 * SR)
n = len(x) // HOP
RMS = np.sqrt(np.mean(x[: n * HOP].reshape(n, HOP) ** 2, axis=1) + 1e-12)
DB = 20 * np.log10(RMS)
TH = float(sp.get('silenceDb', -45))


def find(phrase, start=0):
    p = [norm(t) for t in phrase.split() if norm(t)]
    for i in range(start, len(keys) - len(p) + 1):
        if keys[i:i + len(p)] == p:
            return i, i + len(p) - 1
    for i in range(0, len(keys) - len(p) + 1):
        if keys[i:i + len(p)] == p:
            return i, i + len(p) - 1
    raise SystemExit(f'phrase not in the take: {phrase}')


def quiet_run(a, b):
    """longest run of 10 ms frames under TH between a and b (seconds) -> (s0, s1) or None"""
    lo, hi = max(0, int(a * 100)), min(n, int(b * 100) + 1)
    best, s = None, None
    for i in range(lo, hi + 1):
        q = i < hi and DB[i] < TH
        if q and s is None:
            s = i
        if not q and s is not None:
            if best is None or (i - s) > (best[1] - best[0]):
                best = (s, i)
            s = None
    return None if best is None else (best[0] * 0.01, best[1] * 0.01)


def cut_point(prev_end, next_start, side):
    """cut inside the acoustic pause between two words; side 'in' (segment starts after) or 'out' (segment ends before)"""
    q = quiet_run(prev_end - 0.35, next_start + 0.1)  # Scribe word ends can run 0.1-0.3 s late
    if q is None or q[1] - q[0] < 0.03:
        raise SystemExit(f'no acoustic silence between {prev_end:.2f} and {next_start:.2f}: cannot cut without touching speech')
    s0, s1 = q
    # keep the natural breath close to the word: cut 35 % into the pause on the way out, 65 % on the way in
    t = s0 + (0.35 if side == 'out' else 0.65) * (s1 - s0)
    k = int(t * 100)
    lo, hi = max(int(s0 * 100), k - 2), min(int(s1 * 100), k + 3)
    k = lo + int(np.argmin(RMS[lo:max(hi, lo + 1)]))
    return k * 0.01 + 0.005, (round(s0, 3), round(s1, 3))


FADE = int(0.008 * SR)


def fade(seg):
    seg = seg.copy()
    m = min(FADE, len(seg) // 2)
    if m:
        seg[:m] *= np.linspace(0, 1, m)
        seg[-m:] *= np.linspace(1, 0, m)
    return seg


parts = [np.zeros(int(round(float(sp.get('preroll', 0.08)) * SR)), np.float32)]
t_out = float(sp.get('preroll', 0.08))
new_words, report, cursor = [], [], 0
segs = sp['segments']
for j, sg in enumerate(segs):
    i0, i1 = find(sg['text'], cursor)
    cursor = i1 + 1
    if i0 > 0:
        a, pin = cut_point(words[i0 - 1]['end'], words[i0]['start'], 'in')
        sp_start = pin[1]  # acoustic speech onset
    else:
        a, sp_start = max(0.0, words[i0]['start'] - 0.12), words[i0]['start']
    if i1 + 1 < len(words):
        b, pause = cut_point(words[i1]['end'], words[i1 + 1]['start'], 'out')
    else:
        b, pause = min(len(x) / SR, words[i1]['end'] + 0.35), None
    seg = fade(x[int(a * SR):int(b * SR)])
    for w in words[i0:i1 + 1]:
        new_words.append({'text': w['text'], 'start': round(w['start'] - a + t_out, 3), 'end': round(w['end'] - a + t_out, 3)})
    parts.append(seg)
    lead = sp_start - a
    tail_nat = b - (pause[0] if pause else words[i1]['end'])  # acoustic: from the end of speech to the cut
    t_out += len(seg) / SR
    rep = {'text': sg['text'], 'take_words': [i0, i1], 'cut_in': round(a, 3), 'cut_out': round(b, 3), 'lead_kept': round(lead, 3),
           'tail_kept': round(tail_nat, 3), 'why': sg.get('why', '')}
    if j + 1 < len(segs):
        nxt0, _ = find(segs[j + 1]['text'], cursor)
        nxt_a, nxt_p = cut_point(words[nxt0 - 1]['end'], words[nxt0]['start'], 'in')
        nxt_lead = nxt_p[1] - nxt_a
        add = max(0.0, float(sg['gap']) - tail_nat - nxt_lead)
        parts.append(np.zeros(int(round(add * SR)), np.float32))
        t_out += add
        rep.update({'gap_target': sg['gap'], 'gap_real': round(tail_nat + add + nxt_lead, 3), 'inserted': round(add, 3)})
    report.append(rep)
parts.append(np.zeros(int(round(float(sp.get('tail', 0.6)) * SR)), np.float32))
y = np.concatenate(parts)
out = os.path.join('public', sp['voice'])
pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', out], input=pcm, check=True)
base = spec_file[:-5]
json.dump(new_words, open(base + '.words.json', 'w'), indent=0)
json.dump({'source': sp['voiceRaw'], 'duration': round(len(y) / SR, 3), 'segments': report, 'synthesised': 0, 'time_stretch': 0},
          open(base + '.voice-report.json', 'w'), indent=1)
print(f'{out}: {len(y) / SR:.2f} s, {len(segs)} segments, {len(new_words)} words')
