#!/usr/bin/env python3
"""Reel cover (1080x1920 PNG) from a frame of the finished video: navy/gold title card over the reel frame,
the official 2026 E2A logo (src/brand.ts -> public/brand/e2a-logo-2026.png), no other branding.
  python3 scripts/make-cover.py <video.mp4> <t_seconds> <out.png> --title "BLIND PIG" [--sub "DENY · FLASH · BACKDOOR"]
Fonts: public/anton.woff2 is converted on the fly only if a TTF is unavailable; falls back to DejaVu Sans Bold."""
import argparse, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(HERE)
ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("t", type=float); ap.add_argument("out")
ap.add_argument("--title", required=True); ap.add_argument("--sub", default="")
a = ap.parse_args()
NAVY, GOLD, WHITE = (11, 28, 61), (242, 199, 106), (255, 255, 255)

with tempfile.TemporaryDirectory() as td:
    fr = os.path.join(td, "f.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.t), "-i", a.video, "-frames:v", "1", fr], check=True)
    im = Image.open(fr).convert("RGB").resize((1080, 1920))


def font(size, bold=True):
    for p in [os.path.join(T, "public", "fonts", "Anton-Regular.ttf"), "/usr/share/fonts/truetype/anton/Anton-Regular.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    woff = os.path.join(T, "public", "anton.woff2")
    try:
        from fontTools.ttLib import TTFont
        tt = os.path.join(tempfile.gettempdir(), "anton-cover.ttf")
        if not os.path.exists(tt):
            f = TTFont(woff); f.flavor = None; f.save(tt)
        return ImageFont.truetype(tt, size)
    except Exception:
        return ImageFont.load_default()


# navy gradient at the top for the title, soft vignette at the bottom for the logo
ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
for y in range(0, 760):
    d.line([(0, y), (1080, y)], fill=NAVY + (int(235 * (1 - y / 760) ** 1.3),))
for y in range(1500, 1920):
    d.line([(0, y), (1080, y)], fill=NAVY + (int(220 * ((y - 1500) / 420) ** 1.2),))
im = Image.alpha_composite(im.convert("RGBA"), ov)
d = ImageDraw.Draw(im)
F = font(200)
x0, y0 = 80, 250
d.text((x0 + 6, y0 + 8), a.title, font=F, fill=(0, 0, 0, 140))
d.text((x0, y0), a.title, font=F, fill=GOLD)
tb = d.textbbox((x0, y0), a.title, font=F)
d.rectangle([x0, tb[3] + 26, x0 + 230, tb[3] + 34], fill=GOLD)
if a.sub:
    d.text((x0, tb[3] + 60), a.sub, font=font(64), fill=WHITE)
logo = Image.open(os.path.join(T, "public", "brand", "e2a-logo-2026.png")).convert("RGBA")
lw = 300
logo = logo.resize((lw, int(logo.height * lw / logo.width)))
im.alpha_composite(logo, ((1080 - lw) // 2, 1920 - logo.height - 120))
im.convert("RGB").save(a.out)
print(a.out, a.title, a.sub)
