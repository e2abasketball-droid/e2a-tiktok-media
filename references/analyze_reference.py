#!/usr/bin/env python3
"""Measure the editing of a reference video (E2A edit-reference library, phase 1).

Usage:
  python3 references/analyze_reference.py <video.mp4> <out_dir> [--ref-id R-0001]

Writes to <out_dir>:
  measures.json   cuts, shot lengths, motion per shot, text bands, loudness, silences, beat density
  sheet.jpg       one row per shot (first / middle / last frame) for the visual review
  frames/         the individual frames used in sheet.jpg

Only ffmpeg, ffprobe and numpy are needed (all present in the cloud container).
The video itself is never copied to the repository: only the measures and the
technique cards written from them. sheet.jpg stays in the run's scratch folder.
"""
import argparse, json, os, re, subprocess, sys, hashlib
import numpy as np

SCENE_THRESHOLD = 0.30     # ffmpeg scene score for a cut
MIN_SHOT = 0.25            # s; closer cuts are merged (flashes, glitches)
LOW_W, LOW_H = 72, 128     # analysis resolution (9:16)
LOW_FPS = 10
STATIC_DIFF = 1.2          # mean abs luma diff per frame below this = static picture


def run(cmd, binary=False):
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {p.stderr.decode(errors='ignore')[-400:]}")
    return p.stdout if binary else p.stdout.decode(errors="ignore") + p.stderr.decode(errors="ignore")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path):
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path])
    data = json.loads(out[out.index("{"):])
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    if v is None:
        raise RuntimeError("no video stream")
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    return {
        "duration_s": round(float(data["format"]["duration"]), 2),
        "width": int(v["width"]), "height": int(v["height"]),
        "fps": round(float(num) / float(den or 1), 2),
        "has_audio": a is not None,
        "size_bytes": int(data["format"].get("size", 0)),
    }


def detect_cuts(path, duration):
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an",
               "-vf", f"select='gt(scene,{SCENE_THRESHOLD})',showinfo", "-f", "null", "-"])
    times = [float(t) for t in re.findall(r"pts_time:([0-9.]+)", out)]
    cuts = []
    for t in times:
        if t < MIN_SHOT or t > duration - MIN_SHOT:
            continue
        if cuts and t - cuts[-1] < MIN_SHOT:
            continue
        cuts.append(round(t, 2))
    return cuts


def detect_cuts_lowres(frames):
    """Cuts and animated transitions on graphic videos (dark backgrounds fool the scene score).
    Returns events [{t, dur, kind}] where kind is 'hard' (one frame) or 'animated' (several frames)."""
    if len(frames) < 3:
        return []
    d = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
    thr = max(3.0, 6 * float(np.median(d)))
    hot = d > thr
    events, i = [], 0
    while i < len(hot):
        if hot[i]:
            j = i
            while j + 1 < len(hot) and (hot[j + 1] or (j + 2 < len(hot) and hot[j + 2])):
                j += 1
            peak = i + int(np.argmax(d[i:j + 1]))
            events.append({"t": round((peak + 1) / LOW_FPS, 2), "dur": round((j - i + 1) / LOW_FPS, 2),
                           "kind": "hard" if j == i else "animated"})
            i = j + 1
        else:
            i += 1
    return events


def low_frames(path):
    raw = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an",
               "-vf", f"fps={LOW_FPS},scale={LOW_W}:{LOW_H},format=gray",
               "-f", "rawvideo", "-"], binary=True)
    n = len(raw) // (LOW_W * LOW_H)
    return np.frombuffer(raw[: n * LOW_W * LOW_H], dtype=np.uint8).reshape(n, LOW_H, LOW_W).astype(np.float32)


def shot_motion(frames, start, end):
    a, b = int(start * LOW_FPS), max(int(end * LOW_FPS), int(start * LOW_FPS) + 2)
    seg = frames[a:b]
    if len(seg) < 2:
        return {"motion": 0.0, "kind": "static", "zoom": None, "changes_per_s": 0.0}
    diffs = np.abs(np.diff(seg, axis=0)).mean(axis=(1, 2))
    motion = float(np.median(diffs))
    # graphic changes inside the shot (text pop-ins, counters, bars): frames that change visibly
    changes = float((diffs[1:-1] > 0.8).sum()) / max(len(seg) / LOW_FPS, 0.1) if len(diffs) > 2 else 0.0
    # zoom hint: energy of the centre vs the border changes steadily during a push-in / pull-out
    h, w = seg.shape[1:]
    def ratio(f):
        gy, gx = np.gradient(f)
        e = np.hypot(gx, gy)
        c = e[h // 4: 3 * h // 4, w // 4: 3 * w // 4].mean()
        return c / (e.mean() + 1e-6)
    r0, r1 = ratio(seg[0]), ratio(seg[-1])
    zoom = None
    if motion >= STATIC_DIFF and abs(r1 - r0) > 0.12:
        zoom = "in?" if r1 < r0 else "out?"
    kind = "static" if motion < STATIC_DIFF else ("moving" if motion < 8 else "fast")
    return {"motion": round(motion, 2), "kind": kind, "zoom": zoom, "changes_per_s": round(changes, 2)}


def text_bands(frames):
    """Where on-screen text and graphics sit: share of strong horizontal edges per vertical band."""
    sample = frames[:: max(1, LOW_FPS // 2)]
    bands = {"top": (0.0, 0.25), "upper_mid": (0.25, 0.5), "lower_mid": (0.5, 0.75), "bottom": (0.75, 1.0)}
    out = {}
    for name, (a, b) in bands.items():
        y0, y1 = int(a * LOW_H), int(b * LOW_H)
        part = sample[:, y0:y1, :]
        gx = np.abs(np.diff(part, axis=2))
        out[name] = round(float((gx > 60).mean()), 4)
    total = sum(out.values()) or 1
    return {k: round(v / total, 3) for k, v in out.items()}


def audio_measures(path, duration):
    res = {}
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    summary = out[out.rfind("Summary:"):] if "Summary:" in out else out
    m = re.search(r"I:\s+(-?[0-9.]+) LUFS", summary)
    lra = re.search(r"LRA:\s+([0-9.]+) LU", summary)
    pk = re.search(r"Peak:\s+(-?[0-9.]+) dBFS", summary)
    res["integrated_lufs"] = float(m.group(1)) if m else None
    res["lra_lu"] = float(lra.group(1)) if lra else None
    res["true_peak_dbfs"] = float(pk.group(1)) if pk else None
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "silencedetect=n=-35dB:d=0.25", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    res["silences"] = [[round(s, 2), round(e, 2)] for s, e in zip(starts, ends)]
    raw = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], binary=True)
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    hop = 400  # 50 ms
    n = len(x) // hop
    if n > 4:
        env = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
        db = 20 * np.log10(env)
        flux = np.maximum(np.diff(db), 0)
        thr = flux.mean() + 2.0 * flux.std()
        peaks = [i for i in range(1, len(flux) - 1) if flux[i] > thr and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]]
        res["hits_per_10s"] = round(len(peaks) / max(duration, 1) * 10, 1)
        res["hit_times"] = [round((p + 1) * hop / 8000, 2) for p in peaks][:80]
        res["level_db_p10_p90"] = [round(float(np.percentile(db, 10)), 1), round(float(np.percentile(db, 90)), 1)]
    return res


def contact_sheet(path, shots, out_dir, max_rows=24):
    fdir = os.path.join(out_dir, "frames")
    os.makedirs(fdir, exist_ok=True)
    rows = []
    for i, s in enumerate(shots[:max_rows]):
        pts = [s["start"] + 0.05, (s["start"] + s["end"]) / 2, max(s["start"], s["end"] - 0.08)]
        files = []
        for j, t in enumerate(pts):
            fn = os.path.join(fdir, f"s{i:02d}_{j}.jpg")
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", path,
                 "-frames:v", "1", "-vf", "scale=216:384", fn])
            files.append(fn)
        rows.append(files)
    if not rows:
        return None
    sheet = os.path.join(out_dir, "sheet.jpg")
    inputs, filt = [], []
    for r, files in enumerate(rows):
        for f in files:
            inputs += ["-i", f]
    k = 0
    row_labels = []
    for r, files in enumerate(rows):
        filt.append("".join(f"[{k + c}:v]" for c in range(len(files))) + f"hstack=inputs={len(files)}[r{r}]")
        row_labels.append(f"[r{r}]")
        k += len(files)
    if len(rows) > 1:
        filt.append("".join(row_labels) + f"vstack=inputs={len(rows)}[out]")
        last = "[out]"
    else:
        last = "[r0]"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", last, "-q:v", "4", sheet])
    return sheet


def analyse(path, out_dir, ref_id=None):
    os.makedirs(out_dir, exist_ok=True)
    info = probe(path)
    dur = info["duration_s"]
    frames = low_frames(path)
    events = detect_cuts_lowres(frames)
    merged = sorted(set(detect_cuts(path, dur)) | {e["t"] for e in events})
    cuts = []
    for t in merged:
        if MIN_SHOT <= t <= dur - MIN_SHOT and (not cuts or t - cuts[-1] >= MIN_SHOT):
            cuts.append(t)
    bounds = [0.0] + cuts + [dur]
    shots = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        shots.append({"start": round(a, 2), "end": round(b, 2), "len": round(b - a, 2), **shot_motion(frames, a, b)})
    lens = np.array([s["len"] for s in shots]) if shots else np.array([dur])
    static_long = [s for s in shots if s["kind"] == "static" and s["len"] > 3.5 and s["changes_per_s"] < 0.5]
    zooms = [s for s in shots if s["zoom"]]
    measures = {
        "ref_id": ref_id,
        "sha256": sha256(path),
        "video": info,
        "editing": {
            "cuts": cuts,
            "transitions": events,
            "animated_transition_share": round(sum(e["kind"] == "animated" for e in events) / max(len(events), 1), 2),
            "shots": shots,
            "shot_count": len(shots),
            "shot_len_s": {"median": round(float(np.median(lens)), 2), "min": round(float(lens.min()), 2),
                            "max": round(float(lens.max()), 2), "p90": round(float(np.percentile(lens, 90)), 2)},
            "cuts_per_10s": round(len(cuts) / max(dur, 1) * 10, 1),
            "first_cut_s": cuts[0] if cuts else None,
            "static_share": round(sum(s["len"] for s in shots if s["kind"] == "static") / max(dur, 1), 2),
            "static_over_3_5s": len(static_long),
            "zoom_hint_share": round(len(zooms) / max(len(shots), 1), 2),
            "text_bands": text_bands(frames),
        },
        "audio": audio_measures(path, dur) if info["has_audio"] else None,
        "tool": "references/analyze_reference.py v1",
    }
    with open(os.path.join(out_dir, "measures.json"), "w") as f:
        json.dump(measures, f, indent=1)
    sheet = contact_sheet(path, shots, out_dir)
    return measures, sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out_dir")
    ap.add_argument("--ref-id")
    a = ap.parse_args()
    try:
        m, sheet = analyse(a.video, a.out_dir, a.ref_id)
    except Exception as e:  # the caller records the reason and moves on
        print(json.dumps({"ok": False, "reason": str(e)[:300]}))
        sys.exit(2)
    e = m["editing"]
    print(json.dumps({"ok": True, "duration_s": m["video"]["duration_s"], "shots": e["shot_count"],
                      "median_shot_s": e["shot_len_s"]["median"], "cuts_per_10s": e["cuts_per_10s"],
                      "sheet": sheet}))


if __name__ == "__main__":
    main()
