#!/usr/bin/env python3
"""Word-level timings for a narration mp3 -> JSON [{w,s,e}], corrected to the *known script* text.
Usage: align-words.py vo.mp3 script.txt out.json   (faster-whisper 'base.en'; falls back error if model download is blocked)"""
import json, re, sys
from faster_whisper import WhisperModel
audio, script_f, out = sys.argv[1:4]
model = WhisperModel("base.en", device="cpu", compute_type="int8")
import subprocess, numpy as np
# decode with ffmpeg ourselves (avoids PyAV container API incompatibilities)
pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", audio, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
wave = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
segs, _ = model.transcribe(wave, word_timestamps=True, language="en")
heard = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
script = re.findall(r"\S+", open(script_f).read())
norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
# map each script word to heard timing by sequence alignment (difflib), interpolate unmatched words
import difflib
sm = difflib.SequenceMatcher(None, [norm(w) for w, _, _ in heard], [norm(w) for w in script], autojunk=False)
t = [None] * len(script)
for a, b, n in sm.get_matching_blocks():
    for k in range(n): t[b + k] = (heard[a + k][1], heard[a + k][2])
dur = heard[-1][2]
i = 0
while i < len(t):
    if t[i] is None:
        j = i
        while j < len(t) and t[j] is None: j += 1
        s0 = t[i - 1][1] if i > 0 else 0.0
        e0 = t[j][0] if j < len(t) else dur
        step = (e0 - s0) / (j - i)
        for k in range(i, j): t[k] = (s0 + (k - i) * step, s0 + (k - i + 1) * step)
        i = j
    else: i += 1
json.dump([{"w": w, "s": round(a, 2), "e": round(b, 2)} for w, (a, b) in zip(script, t)], open(out, "w"))
print(f"{len(script)} words, matched {sum(n for _,_,n in sm.get_matching_blocks())}/{len(script)}")
