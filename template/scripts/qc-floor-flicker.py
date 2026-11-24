#!/usr/bin/env python3
"""E2A Floor Graphics Stability QC (2026-11-24, Arrow Press 1-3-1 V2) - measures flicker on EXPORTED video files.

For each video (same edit, same timing) it reports, on the court band of the frame (rows 380-1330 of 1080x1920):
  bad        render failures: dark frames or tiled frames (5-row periodic copy) - the V1 GPU-memory failure mode
  frozen     spans where play and camera are frozen (only graphics can change): frame-to-frame mean abs diff
             (mean, p99), BLINKS (a frame that differs from both neighbours while the neighbours agree: a one-frame
             flash or drop) and DIPS (court luminance or gold-pixel count falls and comes back within 0.7 s)
  gold       per shot: gold-pixel count and its relative 2nd difference (pulse / shimmer of gold graphics), max
  cuts       frame diff at every listed cut (a same-frame "invisible" cut must be ~0)

  python3 scripts/qc-floor-flicker.py --spans spans.json --out report.json NAME=video.mp4 [NAME2=video2.mp4 ...]
spans.json: {"fps":30, "frozen":[[a,b],...], "shots":[[name,a,b],...], "cuts":[t,...], "exclude":[[a,b],...]}
"""
import argparse, json, subprocess
import numpy as np

W, H = 270, 480          # analysis size (1/4)
Y0, Y1 = 95, 332         # court band (380-1330 px at 1920)


def frames(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H}:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def analyse(path, sp):
    fps = sp.get("fps", 30)
    fr = frames(path)
    n = len(fr)
    g = fr[..., 0] * 0.299 + fr[..., 1] * 0.587 + fr[..., 2] * 0.114
    band = g[:, Y0:Y1].astype(np.float32)
    R, G, B = (fr[:, Y0:Y1, :, k].astype(np.int16) for k in range(3))
    gold = ((R > 150) & (G > 110) & (G < 225) & (B < 150) & (R - B > 60)).sum(axis=(1, 2)).astype(float)
    luma = band.mean(axis=(1, 2))
    d1 = np.r_[0, np.abs(np.diff(band, axis=0)).mean(axis=(1, 2))]          # diff to previous frame
    # bad frames (full-frame test at 108x192 equivalent)
    small = g[:, ::2, ::2]
    hh = small.shape[1]
    p = hh // 5
    r0, r1 = int(hh * 0.31), int(hh * 0.94)
    bad = [i for i in range(n) if small[i, r0:r1].mean() < 60 or np.abs(small[i, :p * 4] - small[i, p:p * 5]).mean() < 6]
    excl = np.zeros(n, bool)
    for a, b in sp.get("exclude", []):
        excl[int(a * fps):int(b * fps) + 1] = True
    rep = {"file": path, "frames": n, "bad_frames": len(bad), "bad_list": bad[:50], "frozen": [], "shots": [], "cuts": []}
    for a, b in sp["frozen"]:
        i0, i1 = int(round(a * fps)), min(n - 1, int(round(b * fps)))
        idx = [i for i in range(i0 + 1, i1) if not excl[i]]
        dd = d1[idx]
        blinks = []
        for i in idx:
            if i + 1 >= n:
                continue
            around = np.abs(band[i + 1] - band[i - 1]).mean()
            if d1[i] > 0.6 and d1[i + 1] > 0.6 and around < 0.35 * min(d1[i], d1[i + 1]):
                blinks.append(i)
        dips = []
        for series, name, thr in ((luma, "luma", 0.35), (gold, "gold", None)):
            s = series[i0:i1 + 1]
            t = thr if thr is not None else max(40.0, 0.06 * float(np.median(s)))
            k = 1
            while k < len(s) - 1:
                pre = s[max(0, k - 3):k].mean()
                if pre - s[k] > t:
                    j = k
                    while j < len(s) - 1 and j - k < int(0.7 * fps) and pre - s[j] > t / 3:
                        j += 1
                    if pre - s[j] <= t / 3 and j - k < int(0.7 * fps):
                        dips.append({"series": name, "frame": i0 + k, "t": round((i0 + k) / fps, 2), "depth": round(float(pre - s[k:j].min()), 2), "frames": j - k})
                        k = j
                k += 1
        rep["frozen"].append({"span": [a, b], "n": len(idx), "diff_mean": round(float(dd.mean()), 3), "diff_p99": round(float(np.percentile(dd, 99)), 3),
                              "diff_max": round(float(dd.max()), 3), "blinks": len(blinks), "blink_frames": blinks[:20], "dips": dips})
    for name, a, b in sp["shots"]:
        i0, i1 = int(round(a * fps)) + 2, min(n - 1, int(round(b * fps)) - 2)
        c = gold[i0:i1]
        d2 = np.abs(c[2:] - 2 * c[1:-1] + c[:-2]) / np.maximum(c[1:-1], 50)
        rep["shots"].append({"shot": name, "gold_mean": round(float(c.mean()), 1), "gold_jitter_mean": round(float(d2.mean()), 4),
                             "gold_jitter_p99": round(float(np.percentile(d2, 99)), 4), "gold_jitter_max": round(float(d2.max()), 4)})
    for t in sp.get("cuts", []):
        i = int(round(t * fps))
        if 0 < i < n:
            rep["cuts"].append({"t": t, "frame": i, "diff": round(float(d1[i]), 3)})
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spans", required=True)
    ap.add_argument("--out")
    ap.add_argument("videos", nargs="+")
    a = ap.parse_args()
    sp = json.load(open(a.spans))
    out = {}
    for v in a.videos:
        name, path = v.split("=", 1)
        r = analyse(path, sp)
        out[name] = r
        print(f"== {name}: {r['frames']} frames, bad {r['bad_frames']}")
        for f in r["frozen"]:
            print(f"  frozen {f['span']}: diff mean {f['diff_mean']} p99 {f['diff_p99']} max {f['diff_max']} blinks {f['blinks']} dips {len(f['dips'])} "
                  + " ".join(f"{d['series']}@{d['t']}({d['depth']})" for d in f["dips"][:8]))
        print("  gold jitter p99/max: " + "  ".join(f"{s['shot']} {s['gold_jitter_p99']}/{s['gold_jitter_max']}" for s in r["shots"]))
        print("  cuts: " + "  ".join(f"{c['t']}:{c['diff']}" for c in r["cuts"]))
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)
