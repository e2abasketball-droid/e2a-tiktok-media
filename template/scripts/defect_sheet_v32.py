#!/usr/bin/env python3
"""E2A Realism V3.2 (2026-11-22) — defect contact sheet from the RENDERED A/B/C (3 stacked panels LEGACY / V3.1 / V3.2,
1080 x 640 each): for every defect of the V3.1 review, the V3.1 and V3.2 panels at the same instant, side by side, with
the measured QC value written under it (from the QC JSON files given). Frames are read from the exported MP4 itself.
  python3 scripts/defect_sheet_v32.py abc.mp4 out.jpg [--note 't|label|v31 text|v32 text' ...]
Needs ffmpeg and Pillow."""
import argparse, io, subprocess
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument('mp4'); ap.add_argument('out')
ap.add_argument('--note', action='append', default=[], help="'t|label|v31 text|v32 text'")
a = ap.parse_args()


def frame(t):
    png = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', a.mp4, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'],
                         capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert('RGB')


try:
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
    f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
except OSError:
    F = f2 = ImageFont.load_default()
W, H = 420, 480  # centre crops of the panels (the follow camera keeps O1 near the centre), upscaled
rows = []
for n in a.note:
    t, label, n31, n32 = (n.split('|') + ['', '', ''])[:4]
    im = frame(float(t))
    p31 = im.crop((330, 690, 750, 1170)).resize((W, H))
    p32 = im.crop((330, 1330, 750, 1810)).resize((W, H))
    rows.append((float(t), label, n31, n32, p31, p32))
sheet = Image.new('RGB', (2 * W + 20, len(rows) * (H + 74) + 50), (12, 16, 28))
d = ImageDraw.Draw(sheet)
d.text((10, 12), 'V3.2 defects: left V3.1, right V3.2 (exported A/B/C)', fill=(240, 220, 160), font=F)
y = 50
for t, label, n31, n32, p31, p32 in rows:
    d.text((10, y), f'{t:.2f} s  {label}', fill=(255, 255, 255), font=F)
    sheet.paste(p31, (0, y + 28)); sheet.paste(p32, (W + 20, y + 28))
    d.text((6, y + 30 + H - 24), n31, fill=(150, 190, 255), font=f2)
    d.text((W + 26, y + 30 + H - 24), n32, fill=(255, 210, 120), font=f2)
    y += H + 74
sheet.save(a.out, quality=88)
print('sheet', a.out, len(rows), 'rows')
