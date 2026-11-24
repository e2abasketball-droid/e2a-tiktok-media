#!/usr/bin/env python3
"""E2A Voice Energy QC (2026-11-24, 4 Rules reel). Credit-free measurements to compare a narration with earlier reels:
  * pitch variation: F0 (autocorrelation, 40 ms frames) range p5-p95 and std, in semitones around the take's median
  * energy range: frame RMS p10-p95 (dB) over voiced frames
  * optional --words + --keys: RMS (dBFS) and median F0 of each key word (to check that impact words are not under the
    explanation, and that a count like ONE < TWO < THREE really climbs)
  python3 scripts/voice-energy-qc.py name=path.wav [name2=path2.mp3 ...] [--words w.json --keys ONE!,TWO!,THREE!]"""
import json, subprocess, sys
import numpy as np

SR = 16000


def dec(p):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True, check=True).stdout, dtype=np.float32)


def f0s(x):
    fr, hop = int(0.04 * SR), int(0.01 * SR)
    f, e = [], []
    for i in range(0, len(x) - fr, hop):
        s = x[i:i + fr]
        r = float(np.sqrt(np.mean(s * s)))
        e.append(r)
        if r < 0.02:
            f.append(np.nan)
            continue
        s = s - s.mean()
        ac = np.correlate(s, s, "full")[fr - 1:]
        lo, hi = int(SR / 320), int(SR / 70)
        k = lo + int(np.argmax(ac[lo:hi]))
        f.append(SR / k if ac[k] > 0.35 * ac[0] else np.nan)
    return np.array(f), np.array(e)


def main():
    args = sys.argv[1:]
    words = keys = None
    if "--words" in args:
        words = json.load(open(args[args.index("--words") + 1]))
    if "--keys" in args:
        keys = args[args.index("--keys") + 1].split(",")
    takes = [a.split("=", 1) for a in args if "=" in a and not a.startswith("--")]
    out = {}
    for name, p in takes:
        x = dec(p)
        f, e = f0s(x)
        v = f[~np.isnan(f)]
        st = 12 * np.log2(v / np.median(v))
        edb = 20 * np.log10(e[e > 0.02])
        out[name] = {"dur_s": round(len(x) / SR, 2), "f0_median_hz": round(float(np.median(v)), 1),
                     "f0_range_st_p5_p95": round(float(np.percentile(st, 95) - np.percentile(st, 5)), 2),
                     "f0_std_st": round(float(np.std(st)), 2), "energy_range_db_p10_p95": round(float(np.percentile(edb, 95) - np.percentile(edb, 10)), 2)}
        if words and keys:
            kw = []
            for w in words:
                if w["text"] in keys:
                    s = x[int(w["start"] * SR):int(w["end"] * SR)]
                    ff, _ = f0s(s)
                    vv = ff[~np.isnan(ff)]
                    kw.append({"word": w["text"], "t": w["start"], "rms_dbfs": round(float(20 * np.log10(np.sqrt(np.mean(s * s)) + 1e-9)), 1),
                               "f0_hz": round(float(np.median(vv)), 1) if len(vv) else None})
            out[name]["keys"] = kw
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
