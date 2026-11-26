#!/usr/bin/env python3
"""ZERO CUT narration from the ONE approved Deuce take (eleven_v3, 572 cr, flow QarXx5mV4GLHeDHp93XQ, Scribe 0 cr).
No regeneration, no time-stretch, no pitch change: silences are INSERTED inside the take's own natural gaps at sentence
boundaries so the edit can breathe on the payoffs (owner brief: no long silences, 38-42 s). 15 ms fades at each splice.
Writes public/zerocut/voice-gaps.wav (48 kHz mono) + zerocut-voice.words.json (tags removed, times shifted).
  python3 tactical/episodes/zerocut/_voice-zerocut.py"""
import json, os, subprocess
import numpy as np
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(os.path.dirname(D)))
RAW = os.path.join(T, "public/zerocut/deuce-take-raw.mp3")
# (split point inside a measured natural gap, extra silence seconds)
GAPS = [(3.73, 0.35), (6.79, 0.5), (8.39, 0.4), (11.72, 0.6), (14.79, 0.7), (20.64, 0.9), (25.46, 0.5), (31.32, 0.8)]
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", RAW, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True, check=True).stdout, dtype=np.float32).copy()
F = int(0.015 * SR)
parts, last = [], 0
for t, g in GAPS:
    i = int(t * SR)
    seg = x[last:i].copy()
    if last: seg[:F] *= np.linspace(0, 1, F)
    seg[-F:] *= np.linspace(1, 0, F)
    parts += [seg, np.zeros(int(g * SR), np.float32)]
    last = i
seg = x[last:].copy(); seg[:F] *= np.linspace(0, 1, F); parts.append(seg)
y = np.concatenate(parts)
out = os.path.join(T, "public/zerocut/voice-gaps.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", out],
               input=y.astype(np.float32).tobytes(), check=True)
words = json.load(open(os.path.join(D, "zerocut-voice.words-raw.json")))["words"]
res = []
for w in words:
    if w["text"].startswith("[") or w["text"] in ("—", "-") or w.get("type") != "word":
        continue
    sh = sum(g for t, g in GAPS if w["end"] > t + 0.05)   # Scribe starts run ~0.1 s early: decide by the word end
    res.append({"text": w["text"], "start": round(w["start"] + sh, 3), "end": round(w["end"] + sh, 3)})
json.dump(res, open(os.path.join(D, "zerocut-voice.words.json"), "w"), indent=0)
print(f"voice {len(y)/SR:.2f} s, {len(res)} words, last word ends {res[-1]['end']}")
