#!/usr/bin/env python3
"""SHUFFLE CUT V1 narration: ONE fresh take by the E2A narrator (Nathaniel 9rR45HW0vcBmpCbkc4m9, eleven_v4,
generations_count 1, no voice settings; 731 cr, flow 0Rmg1yfcGfDiYjI0T38M, generation 8n7SbK94O80fawhfNdud;
Scribe 185 cr, 88 words, transcript identical to the script). Never regenerate this take.
No time-stretch, no pitch change: the take is split mid-gap and only silence is inserted (two edit beats: the full play in real
time after "This is the Shuffle Cut.", the make after "there's your layup!").
  python3 tactical/episodes/shuffle/_voice-shuffle.py -> public/shuffle/voice.wav + shuffle.words.json + voice-dynamics.json"""
import json, os, subprocess
import numpy as np
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(os.path.dirname(D)))
RAW = os.path.join(T, "public/shuffle/nathaniel-shuffle-take-raw.mp3")
GAPS = [(6.04, 1.90),           # after "Shuffle Cut." (5.82) / before "First," (6.26): the full play runs in real time
        (25.06, 0.45)]          # after "layup." (24.82) / before "Screen," (25.30): the make lands
F = int(0.015 * SR)
LINES = [("hook", "One screen. One cut. And the defender never sees it coming!", 1.0, "A"),
         ("name", "This is the Shuffle Cut.", 0.5, "A"),
         ("swing", "First, the ball swings to the wing.", 0.0, "B"),
         ("watch", "Now watch the big man.", 0.0, "B"),
         ("sets", "He sets the back screen... right behind the defender.", 0.0, "B"),
         ("waits", "The cutter waits for it.", 0.0, "C"),
         ("slow", "Slow... slow...", 0.0, "C"),
         ("explodes", "then he explodes off the screener's shoulder!", 1.0, "D"),
         ("chasing", "The defender gets caught chasing, right into the screen.", 0.5, "D"),
         ("stride", "The wing hits the cutter in stride...", 0.5, "D"),
         ("layup", "and there's your layup!", 1.0, "D"),
         ("scf", "Screen. Cut. Finish.", 0.0, "E"),
         ("timing", "That's why timing matters more than just speed.", 0.0, "E"),
         ("close", "One screen. Perfect timing. Easy advantage.", 0.5, "E")]


def load(p):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True, check=True).stdout, dtype=np.float32).copy()


def fade(s):
    s = s.copy()
    s[:F] *= np.linspace(0, 1, F)
    s[-F:] *= np.linspace(1, 0, F)
    return s


if __name__ == "__main__":
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
                    os.path.join(T, "public/shuffle/voice.wav")], input=y.tobytes(), check=True)
    raw = [w for w in json.load(open(os.path.join(D, "shuffle.words-raw.json")))["words"] if w.get("type") == "word"]
    script = " ".join(l[1] for l in LINES).split()
    assert len(raw) == len(script), (len(raw), len(script))
    norm = lambda s: "".join(c for c in s.lower() if c.isalnum())
    out = []
    for w, s in zip(raw, script):
        assert norm(w["text"]) == norm(s), (w["text"], s)
        m = (w["start"] + w["end"]) / 2
        a, b, o = next(x for x in offs if x[0] <= m < x[1])
        out.append({"text": s, "start": round(w["start"] - a + o, 3), "end": round(w["end"] - a + o, 3)})   # script spelling and punctuation
    for i in range(len(out) - 1):
        out[i]["end"] = round(min(out[i]["end"], out[i + 1]["start"]), 3)
    json.dump(out, open(os.path.join(D, "shuffle.words.json"), "w"), indent=0)
    json.dump({"lines": [[l[1], l[2], l[3]] for l in LINES]}, open(os.path.join(D, "voice-dynamics.json"), "w"), indent=1)
    print(f"voice {len(y) / SR:.2f} s, {len(out)} words, last ends {out[-1]['end']}")
