#!/usr/bin/env python3
"""Finishing for 2-3 ZONE 40 s CINEMATIC (2026-11-21): ONE MP4 (no A/B, no trial copy), SRT,
measurements. ONE version only.
  python3 tactical/episodes/_finish-zona23.py <out_dir> [--srt-only]   -> E2A-2-3-Zone-MASTER.mp4 + .srt + export.json
Input: out/blob/zona-2-3-zone.raw.mp4 (full render). Final encode = tools/tactical_studio.social_encode
(2-pass H.264 + ONE fixed master gain to -14 LUFS, true peak <= -1; no loudnorm / limiter).
Captions in the SRT use the same caption units as the burned-in subtitles (episode subtitleGroups).
The cover is made separately from a clean still (no captions, no text; only the zone areas and the nail light): see ENTREGA.md."""
import hashlib, json, os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D)); R = os.path.dirname(T)
sys.path.insert(0, os.path.join(R, "tools"))
import tactical_studio as ts  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
EID = "zona-2-3-zone"
RAW = os.path.join(T, "out", "blob", f"{EID}.raw.mp4")
FINAL = os.path.join(OUT, "E2A-2-3-Zone-MASTER.mp4")
ep = json.load(open(os.path.join(D, f"{EID}.json")))


def srt(path):
    words = json.load(open(os.path.join(D, f"{EID}.words.json")))
    gs = ep["subtitleGroups"]
    assert sum(gs) == len(words), (sum(gs), len(words))
    tc = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    out, i, units = [], 0, []
    for g in gs:
        units.append(words[i:i + g]); i += g
    for n, ws in enumerate(units, 1):
        text = " ".join(w["text"] for w in ws).replace("X-FOUR", "X4").replace("X-four", "X4")
        end = ws[-1]["end"] + 0.15
        if n < len(units):
            end = min(end, units[n][0]["start"] - 0.01)   # cues never overlap
        out.append(f"{n}\n{tc(ws[0]['start'])} --> {tc(end)}\n{text}\n")
    open(path, "w").write("\n".join(out))


if "--srt-only" in sys.argv:
    srt(FINAL.replace(".mp4", ".srt")); sys.exit(0)
c = ts.cfg()
enc = ts.social_encode(RAW, FINAL, c)
I, TP = ts.ebur128(FINAL)
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries",
                                "stream=codec_type,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,sample_rate,sample_aspect_ratio:format=duration",
                                "-of", "json", FINAL], capture_output=True, text=True).stdout)
srt(FINAL.replace(".mp4", ".srt"))
sha = hashlib.sha256(open(FINAL, "rb").read()).hexdigest()
rep = {"file": FINAL, "sha256": sha, "raw": RAW, "raw_sha256": hashlib.sha256(open(RAW, "rb").read()).hexdigest(),
       "encode": enc, "I": I, "TP": TP, "ffprobe": pr}
json.dump(rep, open(os.path.join(OUT, "export.json"), "w"), indent=1)
print(FINAL, "I", I, "TP", TP, "dur", pr["format"]["duration"], "sha", sha[:12])
