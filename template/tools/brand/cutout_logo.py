#!/usr/bin/env python3
"""Cut the 2026 E2A logo out of its dark navy square (JPEG) into a transparent PNG.
Colour un-mixing against the measured background: alpha = max_c (C-B)/(255-B), colour = (C-(1-a)B)/a, so edges and
the gold glow keep their light with no dark halo. Soft noise floor (smoothstep) removes JPEG grain in the background.
usage: cutout_logo.py src.jpg out.png"""
import sys
import numpy as np
from PIL import Image
src, out = sys.argv[1:3]
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float64)
h, w, _ = im.shape
k = max(8, h // 40)  # background = median of the four corner patches
B = np.median(np.concatenate([im[:k, :k], im[:k, -k:], im[-k:, :k], im[-k:, -k:]]).reshape(-1, 3), axis=0)
a = np.clip(((im - B) / (255.0 - B)).max(axis=2), 0, 1)
lo, hi = 0.035, 0.10  # soft matte: below lo is background grain, ramps to the raw alpha by hi
s = np.clip((a - lo) / (hi - lo), 0, 1); s = s * s * (3 - 2 * s)
a = a * s
safe = np.maximum(a, 1e-6)[..., None]
rgb = np.clip((im - (1 - a[..., None]) * B) / safe, 0, 255)
rgb[a <= 0] = 0
rgba = np.dstack([rgb, a * 255]).round().astype(np.uint8)
ys, xs = np.where(a > 0.01)
pad = 12
y0, y1, x0, x1 = max(ys.min() - pad, 0), min(ys.max() + pad, h), max(xs.min() - pad, 0), min(xs.max() + pad, w)
Image.fromarray(rgba[y0:y1, x0:x1], 'RGBA').save(out, optimize=True)
print(out, 'bg', B.tolist(), 'crop', (x0, y0, x1, y1))
