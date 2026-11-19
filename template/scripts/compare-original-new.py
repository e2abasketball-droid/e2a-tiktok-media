#!/usr/bin/env python3
"""ORIGINAL -> NEW comparison (review only, never published): per moment, original (left) | new (right), each
540x960 on a 1080x1920 navy card with labels; the shorter side holds its last frame. New audio underneath.
usage: compare.py original.mp4 new.mp4 out.mp4"""
import subprocess, sys, os, tempfile
orig, new, out = sys.argv[1:4]
# (label, original [t0, t1], new [t0, t1])
SEG = [("HOOK", (0.0, 2.7), (0.0, 4.4)),
       ("BALL SCREEN", (4.3, 6.0), (4.38, 6.6)),
       ("BACK SCREEN", (6.0, 9.0), (6.6, 10.74)),
       ("READ A", (11.6, 17.4), (10.74, 17.72)),
       ("READ B", (17.9, 24.0), (17.72, 25.1)),
       ("TAKEAWAY", (24.6, 29.6), (25.1, 30.7))]
FONT = "/home/user/e2a-tiktok-media/template/public/anton.woff2"
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not os.path.exists(font):
    font = subprocess.run(["fc-match", "-f", "%{file}", "DejaVu Sans:bold"], capture_output=True, text=True).stdout
td = tempfile.mkdtemp()
parts = []
for i, (lab, (a0, a1), (b0, b1)) in enumerate(SEG):
    d = max(a1 - a0, b1 - b0)
    p = os.path.join(td, f"s{i}.mp4")
    fc = (f"[0:v]trim={a0}:{a1},setpts=PTS-STARTPTS,scale=540:960,tpad=stop_mode=clone:stop_duration={d - (a1 - a0) + 0.05},trim=0:{d}[L];"
          f"[1:v]trim={b0}:{b1},setpts=PTS-STARTPTS,scale=540:960,tpad=stop_mode=clone:stop_duration={d - (b1 - b0) + 0.05},trim=0:{d}[R];"
          f"color=c=0x0B1C3D:s=1080x1920:r=30:d={d}[bg];[bg][L]overlay=0:520[t1];[t1][R]overlay=540:520,"
          f"drawtext=fontfile={font}:text='{lab}':fontcolor=0xE6C374:fontsize=84:x=(w-tw)/2:y=250,"
          f"drawtext=fontfile={font}:text='ORIGINAL (15 Nov, published)':fontcolor=white:fontsize=30:x=(540-tw)/2:y=460,"
          f"drawtext=fontfile={font}:text='NEW (Spain PnR 2.0)':fontcolor=0xE6C374:fontsize=30:x=540+(540-tw)/2:y=460,"
          f"drawtext=fontfile={font}:text='review only - not for publication':fontcolor=0xFFFFFF@0.6:fontsize=26:x=(w-tw)/2:y=1520[v];"
          f"[1:a]atrim={b0}:{b1},asetpts=PTS-STARTPTS,apad,atrim=0:{d}[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", orig, "-i", new, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", p], check=True)
    parts.append(p)
lst = os.path.join(td, "l.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out], check=True)
print(out)
