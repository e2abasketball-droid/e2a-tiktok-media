# E2A Realism V3.2 (2026-11-22) — per-frame MESH-level QC of the apparel (what the render actually deforms):
#   /tmp/.../venv3d/bin/python -I scripts/qc_cloth_v32.py mesh.npz frames.json --player O1 --out qc.json [--rig rig.json]
# mesh.npz  tools/blender/export_qc_mesh.py of the built .blend (rest positions, skin weights, hem / ease, shape keys)
# frames    scripts/dump-frames-v32.mts (bones, hips, scale, corrective weights, cloth uniforms of each frame)
# Re-implements the GPU path on the CPU: corrective morphs -> linear blend skinning (same FK as athleteV3.fkHeads) ->
# cloth displacement (cloth2.clothDisplace / the v32 shader: sway, twist, panel, ease clamp, v32 clamps). Flutter (a
# <= 6 mm normal ripple) is left out. Per frame and garment (Jersey, Shorts):
#   stretch   max / p99 edge length ratio posed / rest (rest x scale): > 1.25 = visible stretch, < 0.7 = collapse
#   spike     max growth of the umbrella Laplacian |p - mean(neighbours)| over its rest value (m): a single vertex pulled
#             out of its ring (the 3.75 s "triangle" of V3.1) reads as a spike; folds raise it only a little
#   disp      max cloth displacement (m) and the share of the hem that moves > 5 cm
#   pen       garment vertex BELOW the body surface (signed distance along the nearest body vertex normal, m; only where
#             that vertex lies within 2.5 cm sideways: the build removes the skin under the garments): the render
#             hides < bias (jersey 1.2 cm, shorts 5 cm depth bias), so pen < -bias is a visible poke-through
# Thresholds are provisional, from fabric sizes: knit jersey / mesh shorts stretch ~10-20 % in use; 1 cm Laplacian
# growth is a visible fold, 3 cm a spike.
import sys, json, argparse
import bpy  # noqa: F401  (mathutils comes with bpy)
from mathutils import kdtree
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('npz'); ap.add_argument('frames')
ap.add_argument('--player', default='O1'); ap.add_argument('--out', default='')
ap.add_argument('--rig', required=True)
ap.add_argument('--v32', action='store_true', help='apply the v32 cloth shader rules (per-garment uniforms, clamps)')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
D = np.load(a.npz)
rig = json.load(open(a.rig))
F = json.load(open(a.frames))['players'][a.player]
bones = [b['name'] for b in rig['bones']]
npz_bones = list(D['bones'])
assert npz_bones == bones or set(npz_bones) == set(bones), 'bone sets differ'
perm = [npz_bones.index(b) for b in bones]
by = {b['name']: b for b in rig['bones']}

def qmul(a, b):
    ax, ay, az, aw = a; bx, by_, bz, bw = b
    return np.array([aw*bx + ax*bw + ay*bz - az*by_, aw*by_ - ax*bz + ay*bw + az*bx, aw*bz + ax*by_ - ay*bx + az*bw, aw*bw - ax*bx - ay*by_ - az*bz])
def qconj(q): return np.array([-q[0], -q[1], -q[2], q[3]])
def qmat(q):
    x, y, z, w = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])

def bone_mats(row):
    sc = row['sc']; Q = {k: np.array(v) for k, v in row['bones'].items()}
    pos = {bones[0]: np.array(row['hips'])}
    def at(n):
        if n in pos: return pos[n]
        b = by[n]; p = by[b['parent']]
        local = qmat(qconj(np.array(p['R']))) @ ((np.array(b['head']) - np.array(p['head'])) * sc)
        pos[n] = at(p['name']) + qmat(Q[p['name']]) @ local
        return pos[n]
    R, T = [], []
    for n in bones:
        Dq = qmul(Q[n], qconj(np.array(by[n]['R'])))
        M = qmat(Dq)
        R.append(M); T.append(at(n) - M @ (np.array(by[n]['head']) * sc))
    return np.array(R), np.array(T), sc

def skin(name, row, Rm, Tm, sc):
    P = D[name + '_P'].astype(np.float64)
    for k, w in row['morph'].items():
        key = f'{name}_SK_{k}'
        if key in D and w:
            P = P + D[key] * w
    W = D[name + '_W'][:, perm]
    Ps = P * sc
    out = np.zeros_like(Ps)
    for j in np.where(W.sum(0) > 0)[0]:
        out += W[:, j:j+1] * (Ps @ Rm[j].T + Tm[j])
    return out

def edges_of(T):
    E = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
    E.sort(1)
    return np.unique(E, axis=0)

def nbr_mean_op(n, E):
    deg = np.bincount(E.ravel(), minlength=n).astype(np.float64)
    def mean(P):
        S = np.zeros_like(P)
        np.add.at(S, E[:, 0], P[E[:, 1]]); np.add.at(S, E[:, 1], P[E[:, 0]])
        return S / np.maximum(deg, 1)[:, None]
    return mean

def vnormals(P, T):
    N = np.zeros_like(P)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    for i in range(3): np.add.at(N, T[:, i], fn)
    return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)

PANEL, PANEL_REF = 0.3, 0.02
def cloth_disp(P, hem, ease, c, pelvis, sc, panel, v32):
    if c is None: return np.zeros_like(P)
    rx = P[:, 0] - pelvis[0]; ry = P[:, 1] - pelvis[1]
    a_ = c['twist'] * hem; ca, sa = np.cos(a_), np.sin(a_)
    dx = rx * ca - ry * sa - rx; dy = rx * sa + ry * ca - ry
    sx, sy, sz = c['sway']
    pf = np.ones_like(hem)
    if panel:
        sl = np.hypot(sx, sy); rl = np.hypot(rx, ry)
        ok = (sl > 1e-5) & (rl > 1e-5)
        pf = np.where(ok, 1 + PANEL * (rx * sx + ry * sy) / np.maximum(rl * sl, 1e-9) * min(1, sl / PANEL_REF), 1)
    dx = dx + sx * hem * pf; dy = dy + sy * hem * pf; dz = sz * hem
    d = np.stack([dx, dy, dz], 1)
    if v32 and c.get('maxDisp'):
        m = np.linalg.norm(d, axis=1); lim = c['maxDisp'] * np.maximum(hem, 1e-6)
        d *= np.minimum(1, lim / np.maximum(m, 1e-9))[:, None]
    return d

body_T = D['Body_T']
res = {'player': a.player, 'frames': []}
gar = [g for g in ('Jersey', 'Shorts') if g + '_P' in D]
topo = {}
for g in gar:
    T = D[g + '_T']; E = edges_of(T); n = len(D[g + '_P'])
    topo[g] = (T, E, nbr_mean_op(n, E))
for row in F:
    Rm, Tm, sc = bone_mats(row)
    body = skin('Body', row, Rm, Tm, sc)
    bn = vnormals(body, body_T)
    kd = kdtree.KDTree(len(body))
    for i, p in enumerate(body): kd.insert(p, i)
    kd.balance()
    fr = {'t': row['t']}
    for g in gar:
        T, E, mean = topo[g]
        P0 = D[g + '_P'].astype(np.float64) * sc
        P = skin(g, row, Rm, Tm, sc)
        hem = D[g + '_E2A_HEM'] if g + '_E2A_HEM' in D else None; ease = D[g + '_E2A_EASE'] if g + '_E2A_EASE' in D else None
        c = (row['cloth'] or {}).get(g.lower())
        if hem is not None and c is not None:
            P = P + cloth_disp(P, hem.astype(np.float64), ease, c, np.array(row['hips']), sc, g == 'Jersey' or g == 'Shorts', a.v32)
            dmag = np.linalg.norm(cloth_disp(P, hem.astype(np.float64), ease, c, np.array(row['hips']), sc, True, a.v32), axis=1)
        else:
            dmag = np.zeros(len(P))
        L0 = np.linalg.norm(P0[E[:, 0]] - P0[E[:, 1]], axis=1); L1 = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1)
        ratio = L1 / np.maximum(L0, 1e-9)
        ratio = np.where(L0 > 0.008 * sc, ratio, 1.0)  # sub-8 mm edges (seams, the fly) are left out
        zr = D[g + '_P'][:, 2]
        hz = (hem[E[:, 0]] > 0.2) if hem is not None else np.zeros(len(E), bool)
        top = zr[E[:, 0]] > (zr.max() - (0.3 if g == 'Jersey' else 0.0))
        hemR = ratio[hz] if hz.any() else np.ones(1)
        topR = ratio[top & (zr[E[:, 0]] > zr.max() - 0.3)] if g == 'Jersey' else np.ones(1)
        lap0 = np.linalg.norm(P0 - mean(P0), axis=1); lap1 = np.linalg.norm(P - mean(P), axis=1)
        spike = lap1 - lap0
        iv = int(np.argmax(spike))
        pen = np.empty(len(P))
        for i, p in enumerate(P):
            co, j, dd = kd.find(p)
            sd = float(np.dot(p - body[j], bn[j]))
            # the skin under the garments is cut away in the build (only arms, neck, thighs remain near the cloth): a
            # nearest vertex more than 2.5 cm off to the side is not a surface under this point
            pen[i] = sd if (dd * dd - sd * sd) < 0.025 ** 2 else 1.0
        ipen = int(np.argmin(pen))
        fr[g] = {'stretchMax': round(float(ratio.max()), 3), 'stretchP99': round(float(np.quantile(ratio, 0.99)), 3), 'compressMin': round(float(ratio.min()), 3),
                 'nStretch125': int((ratio > 1.25).sum()), 'hemStretchMax': round(float(hemR.max()), 3), 'hemStretchP95': round(float(np.quantile(hemR, 0.95)), 3),
                 'strapStretchMax': round(float(topR.max()), 3), 'strapStretchP95': round(float(np.quantile(topR, 0.95)), 3), 'spike': round(float(spike.max()), 4), 'spikeAt': [round(float(x), 3) for x in P[iv]], 'spikeV': iv,
                 'nSpike2cm': int((spike > 0.02).sum()), 'dispMax': round(float(dmag.max()), 4), 'penMin': round(float(pen.min()), 4), 'penAt': [round(float(x), 3) for x in P[ipen]],
                 'nPen1cm': int((pen < -0.01).sum()), 'nPen3cm': int((pen < -0.03).sum())}
    res['frames'].append(fr)

def summ(g, k, f=max):
    v = [fr[g][k] for fr in res['frames']]
    i = int(np.argmax(v) if f is max else np.argmin(v))
    return {'value': v[i], 't': res['frames'][i]['t']}
res['summary'] = {g: {'stretchMax': summ(g, 'stretchMax'), 'stretchP99': summ(g, 'stretchP99'), 'compressMin': summ(g, 'compressMin', min), 'spike': summ(g, 'spike'),
                      'dispMax': summ(g, 'dispMax'), 'hemStretchMax': summ(g, 'hemStretchMax'), 'hemStretchP95': summ(g, 'hemStretchP95'), 'strapStretchMax': summ(g, 'strapStretchMax'),
                      'strapStretchP95': summ(g, 'strapStretchP95'), 'framesHem130': sum(1 for fr in res['frames'] if fr[g]['hemStretchMax'] > 1.3), 'penMin': summ(g, 'penMin', min),
                      'framesSpike2cm': sum(1 for fr in res['frames'] if fr[g]['spike'] > 0.02),
                      'framesStretch125': sum(1 for fr in res['frames'] if fr[g]['stretchMax'] > 1.25),
                      'framesPen3cm': sum(1 for fr in res['frames'] if fr[g]['nPen3cm'] > 0)} for g in gar}
s = json.dumps(res)
if a.out: open(a.out, 'w').write(s)
print(json.dumps(res['summary'], indent=1))
