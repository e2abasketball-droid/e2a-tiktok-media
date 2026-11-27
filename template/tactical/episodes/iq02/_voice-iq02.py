#!/usr/bin/env python3
"""BASKETBALL IQ 02 "BEAT THE BLITZ" narration: ONE fresh take by the E2A narrator (Nathaniel 9rR45HW0vcBmpCbkc4m9,
eleven_v4, generations_count 1, no voice settings; 609 cr, flow 00N67gIgNnqYisFd5RPg, generation JIW1EcKC1WB5WCujPk5q;
Scribe 126 cr, 67 words). Alternative key-line take: generation Pk957tK9NrdCA2NdWFl8 (173 cr; delivered for review, not
spliced into the master: one continuous performance keeps the intonation consistent).
No regeneration, no time-stretch, no pitch change: the take is split mid-gap and only silence is inserted (edit beats):
the honest 2.0 s decision window after "Drive? Corner? Or cut?" and short breaths for the visual beats.
  python3 tactical/episodes/iq02/_voice-iq02.py  -> public/iq02/voice.wav + tactical/episodes/iq02/iq02.words.json"""
import json, os, subprocess
import numpy as np
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(os.path.dirname(D)))
RAW = os.path.join(T, "public/iq02/nathaniel-iq02-take-raw.mp3")
THINK = 2.0
# (split point in the raw take = middle of the gap between two lines, silence inserted there)
GAPS = [(1.70, 0.9),    # They send TWO at the ball!  | blitz beat
        (4.52, 0.7),    # ...Four on three.           | 4-on-3 beat
        (6.98, 0.4),    # Looks easy... until the help moves.
        (8.88, THINK),  # Drive? Corner? Or cut?      | the decision window
        (13.26, 0.9),   # Corner? His defender never left. | rewind
        (19.42, 2.4),   # THERE'S the pass!           | layup + replay at real speed
        (22.10, 0.4)]   # Attack the space it leaves. | before the close
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
cuts = [0.0] + [g[0] for g in GAPS] + [len(v) / SR]
sil = [g[1] for g in GAPS] + [0.0]
parts, offs, t = [], [], 0.0
for (a, b), g in zip(zip(cuts, cuts[1:]), sil):
    seg = v[int(a * SR):int(b * SR)]
    offs.append((a, b, t))
    parts += [fade(seg), np.zeros(int(g * SR), np.float32)]
    t += len(seg) / SR + g
y = np.concatenate(parts)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le",
                os.path.join(T, "public/iq02/voice.wav")], input=y.tobytes(), check=True)
res = []
for w in json.load(open(os.path.join(D, "iq02.words-raw.json")))["words"]:
    if w.get("type") != "word" or w["text"].startswith("["):
        continue
    m = (w["start"] + w["end"]) / 2
    for a, b, o in offs:
        if a <= m < b:
            res.append({"text": w["text"].replace("’", "'"), "start": round(w["start"] - a + o, 3), "end": round(w["end"] - a + o, 3)})
            break
# script words where Scribe split or merged ("catch is" = "catches"; "weak side" = "weak-side") and script punctuation
out = []
for w in res:
    if out and out[-1]["text"] == "catch" and w["text"] == "is":
        out[-1] = {"text": "catches", "start": out[-1]["start"], "end": w["end"]}
    elif out and out[-1]["text"] == "weak" and w["text"] == "side":
        out[-1] = {"text": "weak-side", "start": out[-1]["start"], "end": w["end"]}
    else:
        out.append(dict(w))
FIX = {"easy": "easy...", "Drive,": "Drive?", "corner,": "Corner?", "or": "Or", "paint": "paint...", "cutter.": "cutter!"}
for w in out:
    w["text"] = FIX.get(w["text"], w["text"])
for i in range(len(out) - 1):
    out[i]["end"] = round(min(out[i]["end"], out[i + 1]["start"]), 3)
json.dump(out, open(os.path.join(D, "iq02.words.json"), "w"), indent=0)
print(f"voice {len(y) / SR:.2f} s, {len(out)} words, last ends {out[-1]['end']}")
print(" ".join(w["text"] for w in out))
