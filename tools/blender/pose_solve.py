"""E2A 3D lab — from MediaPipe world+image landmarks to a floor-frame motion (root trajectory + joints + contacts).

  python -I tools/blender/pose_solve.py raw.json --t0 1.0 --t1 4.8 --out solved.json [--f 1400]

1. per-frame root translation in camera space: linear least squares of the pinhole projection of the 33 world
   landmarks (hip centred, camera axes) onto their image positions (only visibility > 0.5);
2. focal length self-calibration: the f that makes the lowest foot points of the take most planar;
3. floor frame: plane fit to the foot points in contact (lowest 30 %) -> z up, y = away from the camera on the floor;
4. temporal filtering of joints (centred 5-tap binomial; raw kept) and of the root (depth is the noisy axis);
5. foot contacts: heel / toe height above the floor and horizontal speed thresholds, per foot.
Output: everything in metres of MediaPipe scale (the body is rescaled later to the engine player height).
"""
import argparse, json
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('raw')
ap.add_argument('--t0', type=float, default=0.0)
ap.add_argument('--t1', type=float, default=99.0)
ap.add_argument('--f', type=float, default=0.0)
ap.add_argument('--out', required=True)
a = ap.parse_args()
d = json.load(open(a.raw))
F = [r for r in d['frames'] if r['ok'] and a.t0 - 0.2 <= r['t'] <= a.t1 + 0.2]
T = np.array([r['t'] for r in F])
Wl = np.array([r['world'] for r in F])            # (n,33,3) camera axes: x right, y down, z away
P = np.array([[p[:2] for p in r['img']] for r in F])
Vis = np.array([[p[3] for p in r['img']] for r in F])
cx, cy = d['w'] / 2, d['h'] / 2


def roots(f):
    R = []
    for k in range(len(F)):
        A, b = [], []
        for j in range(33):
            if Vis[k, j] < 0.5:
                continue
            X, Y, Z = Wl[k, j]
            u, v = P[k, j] - (cx, cy)
            A.append([f, 0, -u]); b.append(u * Z - f * X)
            A.append([0, f, -v]); b.append(v * Z - f * Y)
        R.append(np.linalg.lstsq(np.array(A), np.array(b), rcond=None)[0])
    return np.array(R)


FOOT = [29, 30, 31, 32]  # heels L R, toes L R


def plane_fit(pts):
    c = pts.mean(0)
    u, s, vt = np.linalg.svd(pts - c)
    n = vt[2]
    if n[1] > 0:  # camera y is down: the floor normal must point up (negative y)
        n = -n
    return c, n, np.abs((pts - c) @ n)


def floor_for(f):
    R = roots(f)
    G = Wl + R[:, None, :]
    pts = G[:, FOOT, :].reshape(-1, 3)
    # lowest points per frame (largest y in camera = lower, roughly)
    low = []
    for k in range(len(F)):
        g = G[k, FOOT]
        low.append(g[np.argmax(g[:, 1])])
    low = np.array(low)
    c, n, res = plane_fit(low)
    keep = res < np.percentile(res, 70)
    c, n, res2 = plane_fit(low[keep])
    return R, G, c, n, float(np.median(res2))


if a.f > 0:
    best = (a.f,) + floor_for(a.f)
else:
    best = None
    for f in np.arange(900, 2401, 100):
        r = floor_for(f)
        print(f'f={f:.0f} floor residual {r[4]*1000:.1f} mm')
        if best is None or r[4] < best[5]:
            best = (f,) + r
f, R, G, c, n, res = best
print('focal', f, 'residual mm', round(res * 1000, 1))
# floor frame: z = n (up), y = camera forward projected on the floor, x = y cross z (right-handed: x right)
zf = n / np.linalg.norm(n)
fw = np.array([0, 0, 1.0]); yf = fw - zf * (fw @ zf); yf /= np.linalg.norm(yf)
xf = np.cross(yf, zf)
M = np.stack([xf, yf, zf])                 # rows: floor axes in camera coords
cam_h = float(-(c @ zf))     # camera height above the floor (MediaPipe metres)
pitch = float(np.degrees(np.arcsin(np.clip(fw @ zf, -1, 1))))
Gf = (G - c) @ M.T                          # joints in the floor frame (n,33,3)


def smooth(x, taps=(1, 4, 6, 4, 1)):
    k = np.array(taps, float); k /= k.sum(); h = len(k) // 2
    xp = np.concatenate([x[:1].repeat(h, 0), x, x[-1:].repeat(h, 0)])
    return sum(k[i] * xp[i:i + len(x)] for i in range(len(k)))


rootF = ((R - c) @ M.T)                    # hip-centre in the floor frame
rootS = smooth(smooth(rootF))
localW = Wl @ M.T                          # hip-centred joints rotated into floor axes
localS = smooth(localW)
JS = localS + rootS[:, None, :]
# contacts
dt = np.gradient(T)
cont = {}
for side, (heel, toe) in {'L': (29, 31), 'R': (30, 32)}.items():
    hz = np.minimum(JS[:, heel, 2], JS[:, toe, 2])
    vel = np.linalg.norm(np.gradient(JS[:, [heel, toe], :2].mean(1), axis=0), axis=1) / dt
    cont[side] = {'low': hz.round(4).tolist(), 'vel': vel.round(3).tolist()}
out = {'source': a.raw, 'focal_px': float(f), 'cx': cx, 'cy': cy, 'floor_M': M.round(6).tolist(), 'floor_c': c.round(6).tolist(), 'floor_residual_mm': round(res * 1000, 1), 'camera_height': round(cam_h, 3),
       'camera_pitch_deg': round(pitch, 1), 't': T.round(4).tolist(), 'vis': Vis.round(3).tolist(),
       'root_raw': rootF.round(4).tolist(), 'root': rootS.round(4).tolist(),
       'local_raw': localW.round(4).tolist(), 'local': localS.round(4).tolist(), 'feet': cont}
json.dump(out, open(a.out, 'w'))
print('camera height', round(cam_h, 2), 'pitch', round(pitch, 1), 'frames', len(T), '->', a.out)
