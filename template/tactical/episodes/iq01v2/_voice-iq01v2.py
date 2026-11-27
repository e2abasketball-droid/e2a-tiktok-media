#!/usr/bin/env python3
"""BASKETBALL IQ 01 V2 narration: ONE Deuce take (eleven_v3, 492 cr, flow AgamQpcSd9itToUVLBcA; Scribe 187 cr).
The take contains the master script AND the alternative hook line ("One defender gives this whole play away.") at the end.
No regeneration, no time-stretch, no pitch change: the take is split mid-gap (silencedetect -40 dB) and only silence is
inserted: the honest 2.0 s decision window after "Two seconds." (the on-screen bar lasts exactly this silence).
  python3 tactical/episodes/iq01v2/_voice-iq01v2.py --hook A|B   -> public/iq01v2/voice-<hook>.wav + iq01v2-<hook>.words.json"""
import json, os, subprocess, sys
import numpy as np
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(os.path.dirname(D)))
RAW = os.path.join(T, "public/iq01v2/deuce-v2-take-raw.mp3")
HOOK = sys.argv[sys.argv.index("--hook") + 1] if "--hook" in sys.argv else "A"
THINK = 2.0
HOOKS = {"A": (0.00, 2.69),    # Three teammates. One right pass.
         "B": (31.39, 34.08)}  # One defender gives this whole play away.
BODY = [(2.69, 9.45, THINK),   # He beats his man. Here comes the help. Freeze. A, B, or C? Two seconds.  -> 2.0 s decision
        (9.45, 31.39, 0.0)]    # A is the easy pass ... Run it back.
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
ha, hb = HOOKS[HOOK]
lead = 0.12 if HOOK == "B" else 0.0          # hook B line starts late in its segment; keep frame 0 voice-ready
segs = [(ha + lead, hb, 0.08 if HOOK == "B" else 0.0)] + BODY
parts, offs, t = [], [], 0.0
for a, b, g in segs:
    seg = v[int(a * SR):min(len(v), int(b * SR))]
    offs.append((a, b, t))
    parts += [fade(seg), np.zeros(int(g * SR), np.float32)]
    t += len(seg) / SR + g
y = np.concatenate(parts)
out = os.path.join(T, f"public/iq01v2/voice-{HOOK}.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", out],
               input=y.astype(np.float32).tobytes(), check=True)
res = []
for w in json.load(open(os.path.join(D, "iq01v2-voice.words-raw.json")))["words"]:
    if w.get("type") != "word" or w["text"].startswith("["):
        continue
    m = (w["start"] + w["end"]) / 2
    for a, b, o in offs:
        if a <= m < b:
            res.append({"text": w["text"].replace("’", "'"), "start": round(max(o, w["start"] - a + o), 3), "end": round(min(b, w["end"]) - a + o, 3)})
            break
res.sort(key=lambda w: w["start"])
for i in range(len(res) - 1):
    res[i]["end"] = round(min(res[i]["end"], res[i + 1]["start"]), 3)
# Scribe heard "C, kick it." - the script line is "That's the read. C." + "Kick it."; restore the script punctuation
for i, w in enumerate(res):
    if w["text"] == "C," and i + 1 < len(res) and res[i + 1]["text"].lower() == "kick":
        w["text"] = "C."; res[i + 1]["text"] = "Kick"
    if w["text"] == "pass," and i + 1 < len(res) and res[i + 1]["text"] == "but":
        w["text"] = "pass."; res[i + 1]["text"] = "But"
    if w["text"] == "B," and i + 1 < len(res) and res[i + 1]["text"] == "his":
        w["text"] = "B?"; res[i + 1]["text"] = "His"
json.dump(res, open(os.path.join(D, f"iq01v2-{HOOK}.words.json"), "w"), indent=0)
print(f"hook {HOOK}: voice {len(y)/SR:.2f} s, {len(res)} words, last word ends {res[-1]['end']}")
for a, b, o in offs:
    print(f"  raw {a:5.2f}-{b:5.2f} -> {o:6.2f}")
