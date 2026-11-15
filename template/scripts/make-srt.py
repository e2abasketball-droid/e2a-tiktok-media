#!/usr/bin/env python3
"""SRT from the real word timings and the episode's subtitleGroups (sense units), one cue per group.
Usage: python3 scripts/make-srt.py tactical/episodes/<id>.json out.srt"""
import json, sys
ep = json.load(open(sys.argv[1]))
words = json.load(open(sys.argv[1].replace('.json', '.words.json')))
groups = ep.get('subtitleGroups') or [len(words)]
fmt = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round(s % 1 * 1000)) % 1000:03d}"
cues, i = [], 0
for g in groups:
    ws = words[i:i + g]; i += g
    if ws:
        cues.append([ws[0]['start'], ws[-1]['end'] + 0.25, ' '.join(w['text'] for w in ws)])
for k in range(len(cues) - 1):
    cues[k][1] = min(cues[k][1], cues[k + 1][0] - 0.02)
with open(sys.argv[2], 'w') as f:
    for n, (a, b, t) in enumerate(cues, 1):
        t = t[0] + t[1:].lower() if t.isupper() else t
        f.write(f"{n}\n{fmt(a)} --> {fmt(b)}\n{t.replace('OPEN', 'open')}\n\n")
print(len(cues), 'cues')
