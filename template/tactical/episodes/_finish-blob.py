#!/usr/bin/env python3
"""Finishing for BLOB Box Screen-the-Screener (2026-11-20): ONE publishable MP4 (no A/B, no trial copy), SRT,
measurements, cover PNG.
  python3 tactical/episodes/_finish-blob.py <out_dir>   -> E2A-BLOB-ScreenTheScreener-FINAL.mp4 + .srt + cover + export.json
Input: out/blob/blob-box-screen-the-screener-v1.raw.mp4 (full render). Final encode = tools/tactical_studio.social_encode
(2-pass H.264 + ONE fixed master gain to -14 LUFS, true peak <= -1; no loudnorm / limiter)."""
import hashlib, json, os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D)); R = os.path.dirname(T)
sys.path.insert(0, os.path.join(R, "tools"))
import tactical_studio as ts  # noqa: E402
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
groups = import_module("_gen-blob").groups

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
EID = "blob-box-screen-the-screener-v1"
RAW = os.path.join(T, "out", "blob", f"{EID}.raw.mp4")
FINAL = os.path.join(OUT, "E2A-BLOB-ScreenTheScreener-FINAL.mp4")
COVER_T = 0.9   # hook frame: O3 with the ball, X4 at the rim, O2 with the gold ring (no caption yet at 0.9? see export)


def srt(path):
    words = json.load(open(os.path.join(D, f"{EID}.words.json")))
    gs = groups(words)
    tc = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    out, i = [], 0
    for n, g in enumerate(gs, 1):
        ws = words[i:i + g]; i += g
        text = " ".join(w["text"] for w in ws).replace("X-four", "X4")
        out.append(f"{n}\n{tc(ws[0]['start'])} --> {tc(ws[-1]['end'] + 0.15)}\n{text}\n")
    open(path, "w").write("\n".join(out))


c = ts.cfg()
enc = ts.social_encode(RAW, FINAL, c)
I, TP = ts.ebur128(FINAL)
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries",
                                "stream=codec_type,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,sample_rate,sample_aspect_ratio:format=duration",
                                "-of", "json", FINAL], capture_output=True, text=True).stdout)
srt(FINAL.replace(".mp4", ".srt"))
cover = os.path.join(OUT, "E2A-BLOB-ScreenTheScreener-portada.png")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(COVER_T), "-i", FINAL, "-frames:v", "1", cover], check=True)
sha = hashlib.sha256(open(FINAL, "rb").read()).hexdigest()
rep = {"file": FINAL, "sha256": sha, "raw": RAW, "raw_sha256": hashlib.sha256(open(RAW, "rb").read()).hexdigest(),
       "encode": enc, "I": I, "TP": TP, "ffprobe": pr, "cover": cover, "cover_t": COVER_T}
json.dump(rep, open(os.path.join(OUT, "export.json"), "w"), indent=1)
print(FINAL, "I", I, "TP", TP, "dur", pr["format"]["duration"], "sha", sha[:12])
