#!/usr/bin/env python3
"""Frame extraction for ANALYZE.

  python3 extract_frames.py <video> <out_dir> [--times 0.5,2.0,...] [--every 1.0] [--sheet]

- Low-resolution frame arrays (grey and colour) for the measurements in analyze_video.py.
- Representative full frames (JPEG, 360 px wide) at given timestamps, named f_<seconds>.jpg.
- A contact sheet (sheet.jpg) for the visual review by Claude.

Frames of third-party videos are working material: they stay in the run's scratch folder and are
never committed to the repository.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import AnalysisError, run  # noqa: E402

LOW_FPS = 10


def low_size(width, height, long_side=128):
    if height >= width:
        h = long_side
        w = max(16, int(round(long_side * width / height / 2)) * 2)
    else:
        w = long_side
        h = max(16, int(round(long_side * height / width / 2)) * 2)
    return w, h


def low_frames(path, width, height, color=False, fps=LOW_FPS):
    """All frames at `fps`, downscaled. Returns float32 array (n, h, w) or (n, h, w, 3)."""
    w, h = low_size(width, height)
    fmt, ch = ("rgb24", 3) if color else ("gray", 1)
    raw = run(["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "error", "-i", path, "-an",
               "-vf", f"fps={fps},scale={w}:{h}:flags=area,format={fmt}", "-f", "rawvideo", "-"], binary=True)
    n = len(raw) // (w * h * ch)
    if n < 1:
        raise AnalysisError("no se pudieron decodificar fotogramas")
    arr = np.frombuffer(raw[: n * w * h * ch], dtype=np.uint8).astype(np.float32)
    return arr.reshape((n, h, w, 3) if color else (n, h, w))


def frame_at(path, t, out_file, width=360):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{max(0.0, t):.3f}", "-i", path,
         "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "4", out_file])
    if not os.path.exists(out_file):
        raise AnalysisError(f"no se pudo extraer el fotograma en {t:.2f} s")
    return out_file


def extract(path, out_dir, times):
    os.makedirs(out_dir, exist_ok=True)
    files = []
    for t in times:
        fn = os.path.join(out_dir, f"f_{t:07.2f}.jpg")
        files.append({"t": round(t, 2), "file": frame_at(path, t, fn)})
    return files


def contact_sheet(files, out_file, cols=6, tile_w=180):
    """Tile frames (in order) into one JPEG with the timestamp burnt in the corner."""
    if not files:
        return None
    inputs, parts = [], []
    for k, f in enumerate(files):
        inputs += ["-i", f["file"]]
        parts.append(f"[{k}:v]scale={tile_w}:-2,drawtext=text='{f['t']:.1f}s':x=4:y=4:fontsize=14:"
                     f"fontcolor=white:box=1:boxcolor=black@0.6[t{k}]")
    rows = (len(files) + cols - 1) // cols
    layout = "|".join(f"{(k % cols) * tile_w}_{'+'.join(['h0'] * (k // cols)) or 0}" for k in range(len(files)))
    filt = ";".join(parts) + ";" + "".join(f"[t{k}]" for k in range(len(files)))
    if len(files) == 1:
        filt = parts[0].replace("[t0]", "[out]")
    else:
        filt += f"xstack=inputs={len(files)}:layout={layout}:fill=0x111111[out]"
    p = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", filt,
             "-map", "[out]", "-frames:v", "1", "-q:v", "4", out_file], check=False)
    if not os.path.exists(out_file):  # drawtext needs a font; retry without labels
        filt2 = ";".join(f"[{k}:v]scale={tile_w}:-2[t{k}]" for k in range(len(files)))
        filt2 += ";" + "".join(f"[t{k}]" for k in range(len(files)))
        filt2 = filt2 + (f"xstack=inputs={len(files)}:layout={layout}:fill=0x111111[out]" if len(files) > 1 else "")
        if len(files) == 1:
            filt2 = f"[0:v]scale={tile_w}:-2[out]"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", filt2,
             "-map", "[out]", "-frames:v", "1", "-q:v", "4", out_file])
    _ = rows, p
    return out_file


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("out_dir")
    ap.add_argument("--times", help="comma-separated seconds")
    ap.add_argument("--every", type=float, help="one frame every N seconds")
    ap.add_argument("--sheet", action="store_true")
    a = ap.parse_args()
    from common import probe
    try:
        info = probe(a.video)
        if a.times:
            times = [float(x) for x in a.times.split(",") if x.strip()]
        else:
            step = a.every or max(1.0, info["duration_s"] / 12)
            times = list(np.arange(0.1, info["duration_s"] - 0.05, step))
        files = extract(a.video, a.out_dir, times)
        sheet = contact_sheet(files, os.path.join(a.out_dir, "sheet.jpg")) if a.sheet else None
    except AnalysisError as e:
        print(json.dumps({"ok": False, "reason": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "frames": len(files), "sheet": sheet}, ensure_ascii=False))


if __name__ == "__main__":
    main()
