#!/usr/bin/env python3
"""NBA vs EuroLeague V2 - voice edit of Deuce take B (eleven_v3, one continuous take, no pitch/speed change).
The take is kept whole; only a few short breaths are LENGTHENED at section boundaries so each graphic has time to land
(the take's own pauses are 0.25-0.38 s; nothing is cut, nothing is sped up). Digital silence is inserted at the middle
of the existing pause after the listed word, and the word timings are shifted to match.
  python3 tactical/episodes/nbaeu-v2/_voice-v2.py RAW.mp3 WORDS_RAW.json OUT.wav OUT_WORDS.json"""
import json, subprocess, sys
import numpy as np

SR = 48000
# (word, occurrence, extra seconds) - section boundaries only
GAPS = [("this.", 1, 0.25), ("ten.", 1, 0.5), ("arc.", 1, 0.7), ("six.", 1, 0.55), ("seconds.", 1, 0.55), ("differently.", 1, 0.3)]

raw, wj, out, outw = sys.argv[1:5]
W = json.load(open(wj))
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", raw, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)
cuts = []
for word, n, extra in GAPS:
    i = [k for k, w in enumerate(W) if w["text"] == word][n - 1]
    t = (W[i]["end"] + W[i + 1]["start"]) / 2
    cuts.append((t, extra))
cuts.sort()
parts, prev, shift = [], 0, 0.0
for t, extra in cuts:
    s = int(t * SR)
    parts += [x[prev:s], np.zeros(int(extra * SR), np.float32)]
    prev = s
parts.append(x[prev:])
y = np.concatenate(parts)
for w in W:
    add = sum(e for t, e in cuts if w["start"] >= t)
    w["start"] = round(w["start"] + add, 3)
    w["end"] = round(w["end"] + add, 3)
    w.pop("_tok", None)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", out], input=y.tobytes(), check=True)
json.dump(W, open(outw, "w"), indent=0)
print(json.dumps({"dur": round(len(y) / SR, 3), "added": round(sum(e for _, e in cuts), 3), "gaps": cuts}))
