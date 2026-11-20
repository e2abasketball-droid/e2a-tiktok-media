#!/usr/bin/env python3
"""Finishing for Pistol Fake Handoff (2026-11-20): Hook-B assembly, social encode, SRT, measurements, trial variant.
  python3 tactical/episodes/_finish-pfh.py <out_dir>   -> E2A-pistol-fake-handoff-transition-Hook-{A,B}.mp4 + .srt, export.json
(derived from _finish-ddtr2.py; inputs: out/pfh/pfh-main-a.raw.mp4 (full Hook-A render), pfh-main-b-hook.raw.mp4 (Hook-B frames 0-95))
B = Hook-B frames 0..83 + Hook-A frames 84.. (the episodes are identical after the hook: same shots, cameras, words
from "The" on, music); audio = Hook-B render to 2.80 s, then A (the voices are sample-identical after the 2.78 s splice). Final encode = tools/tactical_studio.social_encode (2-pass H.264 + ONE
fixed master gain to -14 LUFS, true peak <= -1; no loudnorm / limiter)."""
import json, os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D)); R = os.path.dirname(T)
sys.path.insert(0, os.path.join(R, "tools"))
import tactical_studio as ts  # noqa: E402
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
groups = import_module("_gen-pfh").groups

OUT = sys.argv[1]; VER = "pfh"
# optional tag: `... <out_dir> <tag>` -> ...-Hook-{A,B}-<tag>.mp4, export-<tag>.json (delivered files are not overwritten)
TAG = sys.argv[2] if len(sys.argv) > 2 else ""
os.makedirs(OUT, exist_ok=True)
W = os.path.join(T, "out", "pfh")
SPLIT = 84          # first frame of the shared body (hook ends at 2.80 s = frame 84); audio cut at 2.80 s (> splice 2.78 s)
ACUT = 2.8
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
    """video: Hook-B frames 0..SPLIT-1 + Hook-A frames SPLIT..; audio: Hook-B render to ACUT, then Hook-A (same voice
    samples and same music file after the 3.168 s voice splice, so the cut is seamless)"""
    a, h = (os.path.join(W, f) for f in ("pfh-main-a.raw.mp4", "pfh-main-b-hook.raw.mp4"))
    run("ffmpeg", "-v", "error", "-y", "-i", h, "-i", a, "-filter_complex",
        f"[0:v]trim=end_frame={SPLIT},setpts=PTS-STARTPTS[v0];[1:v]trim=start_frame={SPLIT},setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[v];"
        f"[0:a]atrim=end={ACUT},asetpts=PTS-STARTPTS[a0];[1:a]atrim=start={ACUT},asetpts=PTS-STARTPTS[a1];[a0][a1]concat=n=2:v=0:a=1[au]",
        "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "pcm_s16le", path.replace(".mp4", ".mov"))
    os.replace(path.replace(".mp4", ".mov"), path)


c = ts.cfg()
rep = {}
for v, master in (("A", os.path.join(W, "pfh-main-a.raw.mp4")), ("B", os.path.join(W, "pfh-main-b.master.mp4"))):
    if v == "B":
        b_master(master)
    final = os.path.join(OUT, f"E2A-pistol-fake-handoff-transition-Hook-{v}{'-' + TAG if TAG else ''}.mp4")
    enc = ts.social_encode(master, final, c)
    I, TP = ts.ebur128(final)
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,sample_rate:format=duration",
                                    "-of", "json", final], capture_output=True, text=True).stdout)
    rep[v] = {"file": final, "encode": enc, "I": I, "TP": TP, "ffprobe": pr}
    srt(f"pfh-main-{v.lower()}", final.replace(".mp4", ".srt"))
    print(v, final, "I", I, "TP", TP, "dur", pr["format"]["duration"])
trial = os.path.join(OUT, f"E2A-pistol-fake-handoff-transition-Hook-A{'-' + TAG if TAG else ''}-trial.mp4")
rep["trial"] = {"file": trial, "log": subprocess.run(["bash", os.path.join(T, "scripts", "trial-variant.sh"), rep["A"]["file"], trial], capture_output=True, text=True).stdout}
print("trial", trial, rep["trial"]["log"])
json.dump(rep, open(os.path.join(OUT, f"export{'-' + TAG if TAG else ''}.json"), "w"), indent=1)
