#!/usr/bin/env python3
"""E2A narrator consistency check (2026-11-27): measures a new take against the approved reference take.
Objective proxies only (no listening): voice identity = long-term average spectrum correlation (1/3-octave bands,
100 Hz-8 kHz) and median pitch; expressiveness = pitch range (5-95 %, semitones) and pitch movement; rhythm = pause share;
artifacts = clipping and sudden level jumps. Controls (other voices) show how far a different speaker lands.
  python3 tools/narrator_compare.py REF.mp3 NAME=take.mp3 [NAME2=take2.mp3 ...] [--json out.json]"""
import json, subprocess, sys
import numpy as np
SR = 16000


def load(p):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True, check=True).stdout, dtype=np.float32).copy()


def f0_track(x, hop=160, win=640, lo=70, hi=400):
    out = []
    for i in range(0, len(x) - win, hop):
        f = x[i:i + win] * np.hanning(win)
        if np.sqrt((f ** 2).mean()) < 0.01:
            out.append(np.nan); continue
        ac = np.correlate(f, f, "full")[win - 1:]
        a, b = SR // hi, SR // lo
        k = a + int(np.argmax(ac[a:b]))
        out.append(SR / k if ac[k] > 0.35 * ac[0] else np.nan)
    return np.array(out)


def ltas(x):
    n = 2048
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::512] * np.hanning(n)
    rms = np.sqrt((fr ** 2).mean(axis=1))
    sp = (np.abs(np.fft.rfft(fr[rms > 0.01], axis=1)) ** 2).mean(axis=0)
    fq = np.fft.rfftfreq(n, 1 / SR)
    edges = 100 * 2 ** (np.arange(0, 19) / 3)
    return np.array([10 * np.log10(sp[(fq >= edges[i]) & (fq < edges[i + 1])].mean() + 1e-12) for i in range(len(edges) - 1)])


def metrics(p):
    x = load(p)
    f0 = f0_track(x)
    v = f0[~np.isnan(f0)]
    st = 12 * np.log2(v / np.median(v))
    fr = np.lib.stride_tricks.sliding_window_view(x, 320)[::160]
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + 1e-9)
    return {"dur_s": round(len(x) / SR, 2), "f0_median_hz": round(float(np.median(v)), 1),
            "f0_range_st": round(float(np.percentile(st, 95) - np.percentile(st, 5)), 1),
            "f0_movement_st_per_s": round(float(np.nanmean(np.abs(np.diff(12 * np.log2(f0))))) * 100, 1),
            "pause_share": round(float((db < -40).mean()), 3), "clip_samples": int((np.abs(x) > 0.999).sum()),
            "ltas": ltas(x)}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    if out in args: args.remove(out)
    ref = metrics(args[0]); res = {}
    for spec in ["REF=" + args[0]] + args[1:]:
        name, p = spec.split("=", 1)
        m = dict(ref) if name == "REF" else metrics(p)
        l1, l2 = ref["ltas"] - ref["ltas"].mean(), m["ltas"] - m["ltas"].mean()
        m["ltas_corr_vs_ref"] = round(float(np.corrcoef(l1, l2)[0, 1]), 3)
        m["ltas_rms_diff_db"] = round(float(np.sqrt(((l1 - l2) ** 2).mean())), 2)
        m["f0_median_diff_st"] = round(float(12 * np.log2(m["f0_median_hz"] / ref["f0_median_hz"])), 2)
        m.pop("ltas"); res[name] = m
        print(f"{name:14s}", json.dumps(m))
    if out:
        json.dump(res, open(out, "w"), indent=1)
