#!/usr/bin/env python3
"""Finishing for Double Drag V2 + PCD hooks (2026-11-20): Hook-B assembly, social encode, SRT, measurements.
  python3 tactical/episodes/_finish-ddtr2.py <out_dir> [tag]   -> E2A-double-drag-transition-V2-Hook-{A,B}.mp4 + .srt, export-V2.json
(derived from _finish-ddtr.py; V2 inputs: out/ddtr2/ddtr2-main-a.raw.mp4 (full Hook-A render), ddtr2-main-b-hook.raw.mp4 (Hook-B frames 0-100))
B = Hook-B frames 0..97 + Hook-A frames 98.. (the episodes are identical after the hook: same shots, cameras, words
from "Two" on, music); audio = Hook-B render to 3.2 s, then A (the voices are sample-identical after 3.168 s). Final encode = tools/tactical_studio.social_encode (2-pass H.264 + ONE
fixed master gain to -14 LUFS, true peak <= -1; no loudnorm / limiter)."""
import json, os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D)); R = os.path.dirname(T)
sys.path.insert(0, os.path.join(R, "tools"))
import tactical_studio as ts  # noqa: E402
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
groups = import_module("_gen-ddtr2").groups

OUT = sys.argv[1]; VER = "V2"
# optional tag (2026-11-20 pass + audio fix): `... <out_dir> pase-audio-fix` -> Hook-A = E2A-double-drag-transition-V2-<tag>.mp4,
# Hook-B = ...-V2-<tag>-Hook-B.mp4, export-V2-<tag>.json (the delivered V2 files are not overwritten)
TAG = sys.argv[2] if len(sys.argv) > 2 else ""
os.makedirs(OUT, exist_ok=True)
W = os.path.join(T, "out", "ddtr2")
SPLIT = 98          # first frame of the shared body (hook ends at 3.257 s -> frame 97.7); audio cut at 3.2 s (> splice 3.168 s)
ACUT = 3.2
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
    a, h = (os.path.join(W, f) for f in ("ddtr2-main-a.raw.mp4", "ddtr2-main-b-hook.raw.mp4"))
    run("ffmpeg", "-v", "error", "-y", "-i", h, "-i", a, "-filter_complex",
        f"[0:v]trim=end_frame={SPLIT},setpts=PTS-STARTPTS[v0];[1:v]trim=start_frame={SPLIT},setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[v];"
        f"[0:a]atrim=end={ACUT},asetpts=PTS-STARTPTS[a0];[1:a]atrim=start={ACUT},asetpts=PTS-STARTPTS[a1];[a0][a1]concat=n=2:v=0:a=1[au]",
        "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "pcm_s16le", path.replace(".mp4", ".mov"))
    os.replace(path.replace(".mp4", ".mov"), path)


c = ts.cfg()
rep = {}
for v, master in (("A", os.path.join(W, "ddtr2-main-a.raw.mp4")), ("B", os.path.join(W, "ddtr2-main-b.master.mp4"))):
    if v == "B":
        b_master(master)
    final = os.path.join(OUT, f"E2A-double-drag-transition-V2-Hook-{v}.mp4" if not TAG else (f"E2A-double-drag-transition-V2-{TAG}.mp4" if v == "A" else f"E2A-double-drag-transition-V2-{TAG}-Hook-{v}.mp4"))
    enc = ts.social_encode(master, final, c)
    I, TP = ts.ebur128(final)
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,sample_rate:format=duration",
                                    "-of", "json", final], capture_output=True, text=True).stdout)
    rep[v] = {"file": final, "encode": enc, "I": I, "TP": TP, "ffprobe": pr}
    srt(f"ddtr2-main-{v.lower()}", final.replace(".mp4", ".srt"))
    print(v, final, "I", I, "TP", TP, "dur", pr["format"]["duration"])
json.dump(rep, open(os.path.join(OUT, f"export-{VER}{'-' + TAG if TAG else ''}.json"), "w"), indent=1)
