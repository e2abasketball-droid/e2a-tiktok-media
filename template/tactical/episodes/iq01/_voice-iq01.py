#!/usr/bin/env python3
"""BASKETBALL IQ 01 narration: ONE Deuce take (eleven_v3, 461 cr, flow 1pTn5uvKMIOx2UDpt8GV; Scribe words 156 cr).
No regeneration, no time-stretch, no pitch change: the take is split inside its own natural gaps (silencedetect) and
silences are inserted where the edit needs room: the THINK window after "A, B, or C?" (the viewer decides), the
reveal beat after "C, wide open." and the shot after "too late." 15 ms fades at every splice.
Writes public/iq01/voice.wav (48 kHz mono) + iq01-voice.words.json (times on the edit timeline).
  python3 tactical/episodes/iq01/_voice-iq01.py [--think 1.9]"""
import json, os, subprocess, sys
import numpy as np
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(os.path.dirname(D)))
RAW = os.path.join(T, "public/iq01/deuce-take-raw.mp3")
THINK = float(sys.argv[sys.argv.index("--think") + 1]) if "--think" in sys.argv else 1.9
# (raw start, raw end, silence AFTER): split points mid-gap of the take's measured silences
SEGS = [(0.00, 2.88, 0.05),    # He beats his man, and here comes the help.
        (2.88, 7.18, THINK),   # Freeze it. Who's open? A, B, or C?      -> THINK (no voice, no timer)
        (7.18, 8.15, 0.25),    # Lock it in.
        (8.15, 12.27, 0.15),   # Now watch the low defender. He leaves the corner to stop the drive.
        (12.27, 14.69, 0.05),  # A, his defender is still home.
        (14.69, 18.48, 0.05),  # B, still guarded, and his defender is sitting in the passing lane.
        (18.48, 20.43, 0.30),  # C, wide open.
        (20.43, 23.66, 0.45),  # Kick it to the corner. The next rotation is too late.   (the shot)
        (23.66, 26.01, 0.15),  # Don't watch the ball. Watch the help.
        (26.01, 99.0, 0.0)]    # Did you find him? Tell us what you picked.
F = int(0.015 * SR)


def load(p):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True, check=True).stdout, dtype=np.float32).copy()


def fade(s):
    s = s.copy()
    s[:F] *= np.linspace(0, 1, F)
    s[-F:] *= np.linspace(1, 0, F)
    return s


v = load(RAW)
parts, offs, t = [], [], 0.0
for a, b, g in SEGS:
    seg = v[int(a * SR):min(len(v), int(b * SR))]
    offs.append((a, b, t))
    parts += [fade(seg), np.zeros(int(g * SR), np.float32)]
    t += len(seg) / SR + g
y = np.concatenate(parts)
out = os.path.join(T, "public/iq01/voice.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", out],
               input=y.astype(np.float32).tobytes(), check=True)
res = []
for w in json.load(open(os.path.join(D, "iq01-voice.words-raw.json")))["words"]:
    if w.get("type") != "word" or w["text"].startswith("["):
        continue
    m = (w["start"] + w["end"]) / 2
    for a, b, o in offs:
        if a <= m < b:
            res.append({"text": w["text"], "start": round(max(o, w["start"] - a + o), 3), "end": round(min(b, w["end"]) - a + o, 3)})
            break
for i in range(len(res) - 1):
    res[i]["end"] = round(min(res[i]["end"], res[i + 1]["start"]), 3)
json.dump(res, open(os.path.join(D, "iq01-voice.words.json"), "w"), indent=0)
print(f"voice {len(y)/SR:.2f} s, {len(res)} words, last word ends {res[-1]['end']}")
for a, b, o in offs:
    print(f"  raw {a:5.2f}-{b:5.2f} -> {o:6.2f}")
