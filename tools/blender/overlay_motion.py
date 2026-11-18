"""E2A 3D lab — QC: project the retargeted skeleton (motion.json, metres) back onto the reference frames.
  python -I tools/blender/overlay_motion.py solved.json motion.json FRAMES_DIR out.jpg [--every 3] [--crop]
Green = left side, magenta = right side, white = trunk; yellow dots = pinned contact points while planted.
"""
import argparse, json
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('solved'); ap.add_argument('motion'); ap.add_argument('frames'); ap.add_argument('out')
ap.add_argument('--every', type=int, default=3); ap.add_argument('--t0', type=float, default=-1); ap.add_argument('--t1', type=float, default=99)
ap.add_argument('--cols', type=int, default=8)
a = ap.parse_args()
S = json.load(open(a.solved)); Mo = json.load(open(a.motion))
M = np.array(S['floor_M']); c = np.array(S['floor_c']); f = S['focal_px']; cx, cy = S['cx'], S['cy']; sc = Mo['scale_mp_to_m']
J = {k: np.array(v) for k, v in Mo['joints'].items()}
T = np.array(Mo['t'])


def proj(X):
    Xc = (X / sc) @ M + c
    return np.stack([f * Xc[..., 0] / Xc[..., 2] + cx, f * Xc[..., 1] / Xc[..., 2] + cy], -1)


E = [('pelvis', 'chest', (255, 255, 255)), ('chest', 'head', (255, 255, 255))]
for s, col in (('L', (60, 220, 60)), ('R', (220, 60, 220))):
    E += [('pelvis', 'hip' + s, col), ('hip' + s, 'knee' + s, col), ('knee' + s, 'ankle' + s, col), ('ankle' + s, 'heel' + s, col),
          ('heel' + s, 'ball' + s, col), ('ball' + s, 'toe' + s, col), ('ankle' + s, 'ball' + s, col),
          ('chest', 'shoulder' + s, col), ('shoulder' + s, 'elbow' + s, col), ('elbow' + s, 'wrist' + s, col), ('wrist' + s, 'hand' + s, col)]
tiles = []
for i in range(0, len(T), a.every):
    t = T[i]
    if t < a.t0 - 1e-6 or t > a.t1 + 1e-6:
        continue
    fr = int(round(t * 30000 / 1001)) + 1
    im = cv2.imread(f'{a.frames}/f{fr:04d}.jpg')
    pts = {k: proj(v[i]) for k, v in J.items()}
    for p, q, col in E:
        cv2.line(im, tuple(map(int, pts[p])), tuple(map(int, pts[q])), col, 3, cv2.LINE_AA)
    for ct in Mo['contacts']:
        if ct['t0'] <= t <= ct['t1']:
            cv2.circle(im, tuple(map(int, proj(np.array(ct['anchor'])))), 7, (0, 230, 255), -1)
    allp = np.array(list(pts.values()))
    x0, x1 = allp[:, 0].min(), allp[:, 0].max(); y0, y1 = allp[:, 1].min(), allp[:, 1].max()
    h = max(y1 - y0, 150) * 1.25
    cxx, cyy = (x0 + x1) / 2, (y0 + y1) / 2
    X0, Y0 = int(max(0, cxx - h * 0.4)), int(max(0, cyy - h * 0.55))
    crop = im[Y0:Y0 + int(h * 1.1), X0:X0 + int(h * 0.8)]
    crop = cv2.resize(crop, (240, 330))
    cv2.putText(crop, f'{t:.2f}', (4, 18), 0, 0.6, (0, 255, 255), 2)
    tiles.append(crop)
while len(tiles) % a.cols:
    tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(a.out, np.vstack([np.hstack(tiles[k:k + a.cols]) for k in range(0, len(tiles), a.cols)]), [cv2.IMWRITE_JPEG_QUALITY, 85])
print(a.out, len(tiles))
