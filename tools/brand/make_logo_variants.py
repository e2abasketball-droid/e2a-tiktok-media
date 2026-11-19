#!/usr/bin/env python3
"""Clean variants of the official E2A logo (2026, "E2A Sports Academy") from the owner's JPG on a flat navy background.

    python3 tools/brand/make_logo_variants.py SOURCE.jpg OUT_DIR

The source is a 1254x1254 JPG: white "E2A" + Australia silhouette, white basketball lines, gold ring, on a flat
near-black navy (1, 3, 24). The logo itself is not redrawn or altered: the background is removed by colour-difference
keying (alpha = distance from the background colour, colour un-premultiplied), then cropped to the artwork.

Outputs (PNG, RGBA unless noted):
- e2a_logo_2026_color.png       original colours (white + gold) on transparency: default overlay on dark/navy video
- e2a_logo_2026_white.png       one-colour white on transparency: small bugs, watermarks, court floor
- e2a_logo_2026_navy.png        one-colour navy #0B1C3D on transparency: light/white backgrounds (documents, web)
- e2a_logo_2026_on_navy.png     colour logo on brand navy #0B1C3D, square, opaque (RGB): avatars, end cards, covers
"""
import os, sys

import numpy as np
from PIL import Image

BG = np.array([1, 3, 24], float)   # flat background of the source JPG
NAVY = (11, 28, 61)                # #0B1C3D brand navy
FLOOR, FULL = 14.0, 150.0          # colour distance: below FLOOR -> transparent, above FULL -> opaque
PAD = 24                           # px of transparent air around the cropped artwork


def key(src):
    rgb = np.asarray(Image.open(src).convert("RGB")).astype(float)
    dist = np.abs(rgb - BG).max(axis=2)
    a = np.clip((dist - FLOOR) / (FULL - FLOOR), 0, 1)
    a = a * a * (3 - 2 * a)  # smoothstep: crisp edges, no grey fringe
    safe = np.maximum(a, 1e-3)[..., None]
    col = np.clip((rgb - BG * (1 - a[..., None])) / safe, 0, 255)
    col[a == 0] = 0
    ys, xs = np.where(a > 0.02)
    y0, y1, x0, x1 = max(ys.min() - PAD, 0), min(ys.max() + PAD, rgb.shape[0]), max(xs.min() - PAD, 0), min(xs.max() + PAD, rgb.shape[1])
    return col[y0:y1, x0:x1], a[y0:y1, x0:x1]


def save_rgba(col, a, path):
    out = np.dstack([col, a * 255]).round().astype(np.uint8)
    Image.fromarray(out, "RGBA").save(path, optimize=True)


def main(src, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    col, a = key(src)
    save_rgba(col, a, os.path.join(out_dir, "e2a_logo_2026_color.png"))
    # one-colour versions keep the shape only: the soft lens flare on the gold ring would read as a smudge in one
    # colour, so their alpha is hardened (semi-transparent glow dropped, solid strokes kept)
    m = np.clip((a - 0.45) / 0.35, 0, 1)
    m = m * m * (3 - 2 * m)
    save_rgba(np.full_like(col, 255), m, os.path.join(out_dir, "e2a_logo_2026_white.png"))
    save_rgba(np.broadcast_to(np.array(NAVY, float), col.shape), m, os.path.join(out_dir, "e2a_logo_2026_navy.png"))
    # square on brand navy, artwork at ~78% of the side
    color = Image.open(os.path.join(out_dir, "e2a_logo_2026_color.png"))
    side = 1254
    s = 0.78 * side / max(color.size)
    color = color.resize((round(color.width * s), round(color.height * s)), Image.LANCZOS)
    sq = Image.new("RGBA", (side, side), NAVY + (255,))
    sq.alpha_composite(color, ((side - color.width) // 2, (side - color.height) // 2))
    sq.convert("RGB").save(os.path.join(out_dir, "e2a_logo_2026_on_navy.png"), optimize=True)
    for f in sorted(os.listdir(out_dir)):
        if f.startswith("e2a_logo_2026"):
            im = Image.open(os.path.join(out_dir, f))
            print(f, im.size, im.mode, os.path.getsize(os.path.join(out_dir, f)))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
