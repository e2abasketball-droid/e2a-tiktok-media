#!/usr/bin/env python3
"""Finishing for Double Drag en transicion (2026-11-20): B assembly, social encode, SRT, measurements.
  python3 tactical/episodes/_finish-ddtr.py <version V1|V2> <out_dir>
Inputs (template/out/ddtr/): ddtr-main-a.raw.mp4 (full A render), ddtr-main-b-hook.raw.mp4 (B frames 0-95),
(its audio track covers 0-3.17 s).
B = B hook frames 0..SPLIT-1 + A frames SPLIT.. (the episodes are identical after the hook: same shots, cameras, words
from "As" on, music); audio = B hook render to 3.0 s, then A. Final encode = tools/tactical_studio.social_encode (2-pass H.264 + ONE
fixed master gain to -14 LUFS, true peak <= -1; no loudnorm / limiter)."""
import json, os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D)); R = os.path.dirname(T)
sys.path.insert(0, os.path.join(R, "tools"))
import tactical_studio as ts  # noqa: E402
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
groups = import_module("_gen-ddtr").groups

VER, OUT = sys.argv[1], sys.argv[2]
SUF = "" if VER == "V1" else ".v2"   # V2 = V1 with the re-rendered frame range spliced in (see _splice-ddtr-v2.sh)
os.makedirs(OUT, exist_ok=True)
W = os.path.join(T, "out", "ddtr")
SPLIT = 92          # first frame of the shared body ("As" - 0.1 s = 3.057 s -> frame 92)
run = lambda *a: subprocess.run(list(a), check=True)


def srt(eid, path):
    words = json.load(open(os.path.join(D, f"{eid}.words.json")))
    gs = groups(words)
    ts_ = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    out, i = [], 0
    for n, g in enumerate(gs, 1):
        ws = words[i:i + g]; i += g
        out.append(f"{n}\n{ts_(ws[0]['start'])} --> {ts_(ws[-1]['end'] + 0.15)}\n{' '.join(w['text'] for w in ws)}\n")
    open(path, "w").write("\n".join(out))


def b_master(path):
    """video: B hook frames 0..SPLIT-1 + A frames SPLIT..; audio: B hook render 0..3.0 s + A audio from 3.0 s (both are
    music + room tone only around 3.0 s: the voice is silent from 2.75 s to 3.16 s in both takes, the music is the same
    file at the same time, so the cut is seamless)"""
    a, h = (os.path.join(W, f) for f in (f"ddtr-main-a{SUF}.raw.mp4", "ddtr-main-b-hook.raw.mp4"))
    run("ffmpeg", "-v", "error", "-y", "-i", h, "-i", a, "-filter_complex",
        f"[0:v]trim=end_frame={SPLIT},setpts=PTS-STARTPTS[v0];[1:v]trim=start_frame={SPLIT},setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[v];"
        "[0:a]atrim=end=3.0,asetpts=PTS-STARTPTS[a0];[1:a]atrim=start=3.0,asetpts=PTS-STARTPTS[a1];[a0][a1]concat=n=2:v=0:a=1[au]",
        "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "pcm_s16le", path.replace(".mp4", ".mov"))
    os.replace(path.replace(".mp4", ".mov"), path)


c = ts.cfg()
rep = {}
for v, master in (("A", os.path.join(W, f"ddtr-main-a{SUF}.raw.mp4")), ("B", os.path.join(W, f"ddtr-main-b{SUF}.master.mp4"))):
    if v == "B":
        b_master(master)
    final = os.path.join(OUT, f"E2A-double-drag-transition-{v}-{VER}.mp4")
    enc = ts.social_encode(master, final, c)
    I, TP = ts.ebur128(final)
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,sample_rate:format=duration",
                                    "-of", "json", final], capture_output=True, text=True).stdout)
    rep[v] = {"file": final, "encode": enc, "I": I, "TP": TP, "ffprobe": pr}
    srt(f"ddtr-main-{v.lower()}", final.replace(".mp4", ".srt"))
    print(v, final, "I", I, "TP", TP, "dur", pr["format"]["duration"])
json.dump(rep, open(os.path.join(OUT, f"export-{VER}.json"), "w"), indent=1)
