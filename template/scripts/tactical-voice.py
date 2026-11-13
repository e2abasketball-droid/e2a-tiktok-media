#!/usr/bin/env python3
"""Build the narration track of a tactical episode from the ONE approved take (never re-synthesised,
never sped up) and shift the real word timings accordingly.

v2 (pilot 01, revision): pauses are TOTAL target silences, measured acoustically.
  episode.gaps = [{"after": "<phrase>", "sec": <total silence wanted>, "why": "..."}]
  - the natural silence after the phrase is found with silencedetect on the source take
    (Scribe word ends are not precise enough to cut on);
  - the cut is made in the quietest 20 ms inside that natural silence, so no consonant or word tail is touched;
  - only the missing time (sec - natural) is inserted, as the take's own room tone
    (a slice of that same natural silence, looped), never as digital zero;
  - every splice gets 8 ms fades (no clicks).
  episode.pauses (v1: extra digital silence after a phrase) is still read when gaps is absent.
Writes episode.voice (wav in public/), <id>.words.json and <id>.voice-report.json next to the episode.
Usage: python3 scripts/tactical-voice.py tactical/episodes/<id>.json"""
import json, os, re, subprocess, sys
import numpy as np

SR = 44100
ep_file = sys.argv[1]
ep = json.load(open(ep_file))
words = json.load(open(os.path.join(os.path.dirname(ep_file), ep['wordsRaw'])))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
keys = [norm(w['text']) for w in words]
src = os.path.join('public', ep['voiceRaw'])


def find_end(phrase):
    p = [norm(x) for x in phrase.split() if norm(x)]
    for i in range(len(keys) - len(p) + 1):
        if keys[i:i + len(p)] == p:
            return i + len(p) - 1
    raise SystemExit(f'pause anchor not found: {phrase}')


raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32).copy()


def silences(th_db=-45, min_d=0.06):
    """natural silences of the take: (start, end) where a 10 ms RMS stays under th_db"""
    hop = int(0.01 * SR)
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    quiet = 20 * np.log10(rms) < th_db
    out, s = [], None
    for i, q in enumerate(quiet):
        if q and s is None:
            s = i
        if not q and s is not None:
            if (i - s) * 0.01 >= min_d:
                out.append((s * 0.01, i * 0.01))
            s = None
    return out, rms


SIL, RMS = silences()


def natural_gap(idx):
    """the acoustic silence between word idx and idx+1 (closest to the Scribe boundary)"""
    a = words[idx]['end']
    b = words[idx + 1]['start'] if idx + 1 < len(words) else a + 0.5
    mid = (a + b) / 2
    cands = [s for s in SIL if s[1] > a - 0.25 and s[0] < b + 0.25]
    if not cands:
        raise SystemExit(f'no acoustic silence after "{words[idx]["text"]}" ({a:.2f}s): cannot cut there without touching speech')
    return min(cands, key=lambda s: abs((s[0] + s[1]) / 2 - mid))


gaps = ep.get('gaps')
plan = []  # (word idx, cut time, inserted seconds, info)
if gaps is not None:
    for g in gaps:
        idx = find_end(g['after'])
        s0, s1 = natural_gap(idx)
        nat = s1 - s0
        add = max(0.0, float(g['sec']) - nat)
        # quietest 20 ms inside the middle of the natural silence
        lo, hi = int((s0 + 0.25 * nat) * 100), max(int((s0 + 0.75 * nat) * 100), int((s0 + 0.25 * nat) * 100) + 1)
        k = lo + int(np.argmin(RMS[lo:hi]))
        cut = k * 0.01 + 0.005
        plan.append((idx, cut, add, {'after': g['after'], 'natural_silence': [round(s0, 3), round(s1, 3)], 'natural_sec': round(nat, 3), 'target_sec': g['sec'], 'inserted_sec': round(add, 3), 'cut_at_source': round(cut, 3), 'why': g.get('why', '')}))
else:  # v1 behaviour
    for pz in ep.get('pauses', []):
        idx = find_end(pz['after'])
        nxt = words[idx + 1]['start'] if idx + 1 < len(words) else words[idx]['end'] + 0.2
        plan.append((idx, (words[idx]['end'] + nxt) / 2, float(pz['sec']), {'after': pz['after'], 'inserted_sec': pz['sec']}))
plan.sort()

pre = float(ep.get('preroll', 0))
FADE = int(0.008 * SR)


def fade(seg, fin=True, fout=True):
    seg = seg.copy()
    n = min(FADE, len(seg) // 2)
    if n and fin:
        seg[:n] *= np.linspace(0, 1, n)
    if n and fout:
        seg[-n:] *= np.linspace(1, 0, n)
    return seg


def room_tone(sec, around):
    """loop a slice of the take's own silence (crossfaded) to fill `sec` seconds"""
    n = int(round(sec * SR))
    if n <= 0:
        return np.zeros(0, np.float32)
    s0, s1 = around
    a, b = int((s0 + 0.05) * SR), int((s1 - 0.05) * SR)
    base = x[a:b] if b - a > 0.05 * SR else np.zeros(int(0.1 * SR), np.float32)
    reps = int(np.ceil(n / len(base))) + 1
    tone = np.concatenate([fade(base) for _ in range(reps)])[:n]
    return fade(tone).astype(np.float32)


parts = [np.zeros(int(round(pre * SR)), np.float32)]
t0 = 0
for idx, cut, add, info in plan:
    c = int(round(cut * SR))
    parts.append(fade(x[t0:c], fin=t0 > 0, fout=add > 0))
    if add > 0:
        parts.append(room_tone(add, info.get('natural_silence', (cut - 0.1, cut + 0.1)) if isinstance(info.get('natural_silence'), list) else (cut - 0.1, cut + 0.1)))
    t0 = c
parts.append(fade(x[t0:], fin=t0 > 0 and plan and plan[-1][2] > 0, fout=False))
y = np.concatenate(parts)
out = os.path.join('public', ep['voice'])
pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', out], input=pcm, check=True)

# shifted timings: words after a cut move by the inserted time
res, add_total = [], pre
cuts = {idx: add for idx, _, add, _ in plan}
for i, w in enumerate(words):
    res.append({'text': w['text'], 'start': round(w['start'] + add_total, 3), 'end': round(w['end'] + add_total, 3)})
    add_total += cuts.get(i, 0.0)
wf = ep_file.replace('.json', '.words.json')
json.dump(res, open(wf, 'w'))
report = {'source': src, 'source_sec': round(len(x) / SR, 3), 'preroll': pre, 'output': out, 'output_sec': round(len(y) / SR, 3),
          'inserted_total_sec': round(sum(p[2] for p in plan), 3), 'last_word_end': res[-1]['end'], 'gaps': [p[3] for p in plan],
          'note': 'one approved take, never re-synthesised or time-stretched; only room tone inserted at acoustic silences'}
json.dump(report, open(ep_file.replace('.json', '.voice-report.json'), 'w'), indent=1)
print(json.dumps({k: report[k] for k in ('output_sec', 'inserted_total_sec', 'last_word_end')}))
