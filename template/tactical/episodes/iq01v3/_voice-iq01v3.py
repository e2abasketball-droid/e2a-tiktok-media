#!/usr/bin/env python3
"""BASKETBALL IQ 01 V3 narration: ONE take by Nathaniel (9rR45HW0vcBmpCbkc4m9, eleven_v4, 693 cr, flow 6GOo3uZ0cfVXdKo1XftG; Scribe 176 cr).
The take contains the master script AND the alternative hook line ("One defender just left a shooter wide open. Can you spot him?") at the end.
No regeneration, no time-stretch, no pitch change: the take is split mid-gap (silencedetect -40 dB) and only silence is
inserted: the honest 2.0 s decision window after "Two seconds. Make your call." (the on-screen bar lasts exactly this silence).
  python3 tactical/episodes/iq01v3/_voice-iq01v3.py --hook A|B   -> public/iq01v3/voice-<hook>.wav + iq01v3-<hook>.words.json"""
import json, os, subprocess, sys
import numpy as np
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(os.path.dirname(D)))
RAW = os.path.join(T, "public/iq01v3/nathaniel-v3-take-raw.mp3")
HOOK = sys.argv[sys.argv.index("--hook") + 1] if "--hook" in sys.argv else "A"
THINK = 2.0
HOOKS = {"A": (0.00, 1.90),    # The easy pass here is a trap.
         "B": (28.40, 32.08)}  # One defender just left a shooter wide open. Can you spot him?
BODY = [(1.90, 7.93, THINK),   # He beats his man ... Freeze. A, B, or C? Two seconds. Make your call.  -> 2.0 s decision
        (7.93, 28.40, 0.0)]    # A looks easy ... Run it back.
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
lead = 0.10 if HOOK == "B" else 0.0          # hook B line starts late in its segment; keep frame 0 voice-ready
segs = [(ha + lead, hb, 0.08 if HOOK == "B" else 0.0)] + BODY
parts, offs, t = [], [], 0.0
for a, b, g in segs:
    seg = v[int(a * SR):min(len(v), int(b * SR))]
    offs.append((a, b, t))
    parts += [fade(seg), np.zeros(int(g * SR), np.float32)]
    t += len(seg) / SR + g
y = np.concatenate(parts)
out = os.path.join(T, f"public/iq01v3/voice-{HOOK}.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", out],
               input=y.astype(np.float32).tobytes(), check=True)
res = []
for w in json.load(open(os.path.join(D, "iq01v3-voice.words-raw.json")))["words"]:
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
# restore the script punctuation where Scribe merged sentences
FIX = {("easy,", "but"): ("easy.", "But"), ("B,", "his"): ("B?", "His"), ("There,", "that's"): ("There!", "That's"),
       ("C,", "kick"): ("C!", "Kick")}
for i in range(len(res) - 1):
    k = (res[i]["text"], res[i + 1]["text"])
    if k in FIX:
        res[i]["text"], res[i + 1]["text"] = FIX[k]
json.dump(res, open(os.path.join(D, f"iq01v3-{HOOK}.words.json"), "w"), indent=0)
print(f"hook {HOOK}: voice {len(y)/SR:.2f} s, {len(res)} words, last word ends {res[-1]['end']}")
for a, b, o in offs:
    print(f"  raw {a:5.2f}-{b:5.2f} -> {o:6.2f}")
