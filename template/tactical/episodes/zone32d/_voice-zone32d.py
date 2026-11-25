#!/usr/bin/env python3
"""3-2 Zone Defense narration from the ONE approved Deuce take (eleven_v3, 838 cr, flow 7WLls3ifsRu3t5RauvNZ).
No regeneration, no time-stretch, no pitch change. Two secondary phrases are removed by cutting inside the take's own
natural silences (brief sec. 4: 'remove secondary words before sacrificing clarity'), 10 ms fades at every splice:
  - "The goal?"        (raw 7.35 -> 8.21 s)   the purpose is still said: "Control the wings... and make outside shots difficult."
  - "On every shot:"   (raw 40.50 -> 41.93 s) "Find a body. Box out." follows "defensive rebounding" directly
Writes public/zone32d/voice-cut.wav (48 kHz mono) + zone32d-voice.words.json (tags removed, times shifted).
  python3 tactical/episodes/zone32d/_voice-zone32d.py [--full]   (--full keeps every phrase: the uncut 49.2 s take)"""
import json, os, subprocess, sys
import numpy as np
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(os.path.dirname(D)))
RAW = os.path.join(T, "public/zone32d/deuce-take-raw.mp3")
CUTS = [] if "--full" in sys.argv else [(7.35, 8.21), (40.50, 41.93)]
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", RAW, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True, check=True).stdout, dtype=np.float32).copy()
keep, t = [], 0.0
for a, b in CUTS:
    keep.append((t, a)); t = b
keep.append((t, len(x) / SR))
F = int(0.01 * SR)
parts = []
for a, b in keep:
    seg = x[int(a * SR):int(b * SR)].copy()
    seg[:F] *= np.linspace(0, 1, F); seg[-F:] *= np.linspace(1, 0, F)
    parts.append(seg)
y = np.concatenate(parts)
out = os.path.join(T, "public/zone32d/voice-cut.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", out],
               input=y.astype(np.float32).tobytes(), check=True)
words = json.load(open(os.path.join(D, "zone32d-voice.words-raw.json")))["words"]
res = []
for w in words:
    if w["text"].startswith("[") or w.get("type") != "word":
        continue
    if any(a <= w["start"] < b for a, b in CUTS):
        continue
    sh = sum(b - a for a, b in CUTS if b <= w["start"])
    res.append({"text": w["text"], "start": round(w["start"] - sh, 3), "end": round(w["end"] - sh, 3)})
json.dump(res, open(os.path.join(D, "zone32d-voice.words.json"), "w"), indent=0)
print(f"voice {len(y)/SR:.2f} s, {len(res)} words, removed {[r['text'] for r in []]} cuts {CUTS}")
