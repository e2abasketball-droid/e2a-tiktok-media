#!/usr/bin/env python3
"""Finishing for Double Drag en transicion (2026-11-20): B assembly, social encode, SRT, measurements.
  python3 tactical/episodes/_finish-ddtr.py <version V1|V2> <out_dir>
Inputs (template/out/ddtr/): ddtr-main-a.raw.mp4 (full A render), ddtr-main-b-hook.raw.mp4 (B frames 0-95),
ddtr-main-b.audio.wav (B audio, audio-only render of the same composition).
B = B hook frames 0..SPLIT-1 + A frames SPLIT.. (the episodes are identical after the hook: same shots, cameras, words
from "As" on, music); audio = B's own render. Final encode = tools/tactical_studio.social_encode (2-pass H.264 + ONE
fixed master gain to -14 LUFS, true peak <= -1; no loudnorm / limiter)."""
import json, os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D)); R = os.path.dirname(T)
sys.path.insert(0, os.path.join(R, "tools"))
import tactical_studio as ts  # noqa: E402
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
groups = import_module("_gen-ddtr").groups

VER, OUT = sys.argv[1], sys.argv[2]
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
    a, h, au = (os.path.join(W, f) for f in ("ddtr-main-a.raw.mp4", "ddtr-main-b-hook.raw.mp4", "ddtr-main-b.audio.wav"))
    run("ffmpeg", "-v", "error", "-y", "-i", h, "-i", a, "-i", au, "-filter_complex",
        f"[0:v]trim=end_frame={SPLIT},setpts=PTS-STARTPTS[v0];[1:v]trim=start_frame={SPLIT},setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[v]",
        "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "pcm_s16le", "-shortest", path.replace(".mp4", ".mov"))
    os.replace(path.replace(".mp4", ".mov"), path)


c = ts.cfg()
rep = {}
for v, master in (("A", os.path.join(W, "ddtr-main-a.raw.mp4")), ("B", os.path.join(W, "ddtr-main-b.master.mp4"))):
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
