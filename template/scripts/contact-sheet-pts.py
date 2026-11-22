#!/usr/bin/env python3
"""E2A (Chicago V3, 2026-11-22) contact sheet from an EXPORTED MP4 at given times (brief sec. 13.5): frame index = round(t*30)
usage: python3 scripts/contact-sheet-pts.py video.mp4 out.jpg cols t1 t2 ...  [--title TEXT]"""
import subprocess, sys, json, os, tempfile
from PIL import Image, ImageDraw, ImageFont
args = sys.argv[1:]
title = None
if "--title" in args:
    i = args.index("--title"); title = args[i + 1]; del args[i:i + 2]
vid, out, cols = args[0], args[1], int(args[2]); ts = [float(x) for x in args[3:]]
n = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", vid], capture_output=True, text=True).stdout.strip().strip(","))
tmp = tempfile.mkdtemp()
tiles = []
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26) if os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") else ImageFont.load_default()
fr = sorted(set(min(n - 1, max(0, round(t * 30))) for t in ts))
sel = "+".join(f"eq(n\\,{f})" for f in fr)
r = subprocess.run(["ffmpeg", "-v", "info", "-y", "-i", vid, "-vf", f"select='{sel}',showinfo", "-vsync", "0", os.path.join(tmp, "o%04d.png")], capture_output=True, text=True).stderr
ptsl = [l.split("pts_time:")[1].split()[0] for l in r.splitlines() if "pts_time:" in l]
for t in ts:
    f = min(n - 1, max(0, round(t * 30)))
    k = fr.index(f)
    pts = ptsl[k] if k < len(ptsl) else "?"
    im = Image.open(os.path.join(tmp, f"o{k + 1:04d}.png")).convert("RGB")
    w = 360; h = int(im.height * w / im.width)
    im = im.resize((w, h))
    d = ImageDraw.Draw(im)
    d.rectangle([0, h - 40, w, h], fill=(0, 0, 0))
    d.text((8, h - 36), f"f={f} pts={float(pts):.3f}" if pts != "?" else f"t={t:.2f} f={f}", font=F, fill=(255, 220, 90))
    tiles.append(im)
w, h = tiles[0].size
rows = (len(tiles) + cols - 1) // cols
top = 60 if title else 0
S = Image.new("RGB", (cols * w, rows * h + top), (20, 20, 24))
if title:
    ImageDraw.Draw(S).text((12, 14), title, font=F, fill=(255, 255, 255))
for i, im in enumerate(tiles):
    S.paste(im, ((i % cols) * w, top + (i // cols) * h))
S.save(out, quality=86)
print(out, len(tiles), "tiles", S.size)
