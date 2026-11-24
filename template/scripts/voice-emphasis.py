#!/usr/bin/env python3
"""E2A Voice Emphasis (2026-11-24, 4 Rules reel) - credit-free WORD-level gain on an existing narrator take.

voice-dynamics.py shapes whole lines; some takes deliver the key word of a line (TRAVEL!, ONE! TWO! THREE!) softer than
the explanation around it. This lifts ONLY those words: a static gain per word, with 25 ms raised-cosine ramps placed in
the gaps around the word (never inside it), no pitch or time change, no new audio. Run it BEFORE voice-dynamics.py.

Emphasis file (JSON): {"words": [["TRAVEL!", 13.04, 4.5], ...]} = word text, its start time in the words file (to pick
the right occurrence), gain in dB (max +8).
  python3 scripts/voice-emphasis.py --voice in.wav --words w.json --emphasis e.json --out out.wav [--report r.json]"""
import argparse, json, subprocess
import numpy as np

SR = 48000


def main():
    ap = argparse.ArgumentParser()
    for k in ("--voice", "--words", "--emphasis", "--out"):
        ap.add_argument(k, required=True)
    ap.add_argument("--report")
    a = ap.parse_args()
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", a.voice, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                     capture_output=True, check=True).stdout, dtype=np.float32).copy()
    W = json.load(open(a.words))
    E = json.load(open(a.emphasis))["words"]
    g = np.zeros(len(x))
    rep = []
    R = int(0.025 * SR)
    for text, t, db in E:
        i = min(range(len(W)), key=lambda k: abs(W[k]["start"] - t))
        w = W[i]
        assert w["text"] == text, (text, w["text"])
        db = max(-6.0, min(8.0, float(db)))
        prev_end = W[i - 1]["end"] if i else 0.0
        nxt = W[i + 1]["start"] if i + 1 < len(W) else len(x) / SR
        a0 = int(max(prev_end, w["start"] - 0.06) * SR)
        a1 = int(min(nxt, w["end"] + 0.12) * SR)
        env = np.ones(a1 - a0)
        r = min(R, (a1 - a0) // 4)
        ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, r))
        env[:r], env[-r:] = ramp, ramp[::-1]
        g[a0:a1] = np.maximum(g[a0:a1], env * db)
        seg = x[int(w["start"] * SR):int(w["end"] * SR)]
        rep.append({"word": text, "t": w["start"], "gain_db": db, "rms_before_dbfs": round(float(20 * np.log10(np.sqrt(np.mean(seg * seg)) + 1e-9)), 1)})
    y = x * (10 ** (g / 20))
    pk = float(np.max(np.abs(y)))
    if pk > 0.98:
        y *= 0.98 / pk
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", a.out],
                   input=y.astype(np.float32).tobytes(), check=True)
    for r in rep:
        seg = y[int(r["t"] * SR):int((r["t"] + 0.5) * SR)]
        r["rms_after_dbfs_first500ms"] = round(float(20 * np.log10(np.sqrt(np.mean(seg * seg)) + 1e-9)), 1)
    out = {"peak_norm": round(min(1.0, 0.98 / pk), 3), "words": rep}
    if a.report:
        json.dump(out, open(a.report, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
