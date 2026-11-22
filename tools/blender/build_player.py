"""E2A 3D — build the production E2A player (offense or defense variant) in Blender (bpy as a module, background).
Phase 4 (2026-11-19) of tools/blender/build_blender.py: same body / clothes / rig pipeline, plus
  * --variant off|def: offense = E2A navy #0E2147 + gold (engine KITS.O), curly hair volume on top (5440);
    defense = white #F3F1EC + garnet #B8322A, black shoes (engine KITS.X), heavier frame, buzz cut, lighter skin;
  * the clip actions are keyed from HEAD-CALIBRATED motions (fix_head.py) and an `E2A_rest` action is added;
  * --out-rig: the engine rig descriptor (bones + rest joints + height, same layout as the clip JSON) that
    src/t3d/player3d.ts uses to drive the mesh from ANY engine pose (procedural rig, choreo, clips);
  * smoother trims (collar / armholes / hems) and slightly bigger hands and deltoids (basketball build).
The reference camera (solved 5452 camera + SDR video) is only added when --solved / --ref-video are given.

  /tmp/claude-0/venv3d/bin/python -I tools/blender/build_player.py -- --variant off \
      --action E2A_screen_roll_5452=5452_motion_hf.json --action E2A_screen_roll_5452m=5452m_motion_hf.json \
      --solved 5452_solved.json --out-blend e2a_player_off.blend --out-glb e2a_player_off.glb --out-rig e2a-off.rig.json

* body: MakeHuman base mesh (ara3d-data, CC0-1.0) morphed by mh_body.py, face neutralised (brand rule: no facial
  detail in recreations), soles 2 cm up for the shoe;
* clothes from the body surface (same vertices -> same skin weights): sleeveless jersey (E2A navy #0B1C3D, gold
  #C9A24D trims, gold number front and back), loose shorts (legs flared, 30 % of the thigh weight moved to the hips so
  the hem does not stick to the thigh), white socks, shoes (white upper, dark sole), short hair shell with volume on top;
* armature: skeleton.py (23 bones), MakeHuman weights collapsed per bone, top 4 influences;
* action: motion.json (retarget.py) keyed per frame (quaternions + hips location), 29.97 fps;
* reference: a camera at the solved video camera (focal, height, pitch) with the SDR video as background, so the clip
  can be checked / edited against the take in Blender.
"""
import argparse, json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import mathutils
import mh_body
import skeleton as SK

ap = argparse.ArgumentParser()
ap.add_argument('--variant', choices=['off', 'def'], default='off')
ap.add_argument('--action', action='append', default=[], help='NAME=motion.json (first one is the active action)')
ap.add_argument('--solved', default='')
ap.add_argument('--out-rig', default='')
ap.add_argument('--ref-video', default='')
ap.add_argument('--out-blend', required=True)
ap.add_argument('--out-glb', required=True)
ap.add_argument('--number', default='')
ap.add_argument('--skin', default='')
ap.add_argument('--cloth-cut', choices=['iso', 'legacy'], default='iso', help='garment / hidden-skin edges (see iso_clip)')
ap.add_argument('--rig', choices=['v1', 'v3'], default='v1',
                help='v3 (Realism V3, 2026-11-22): + 6 finger bones (fingers1 / fingers2 / thumb per hand, skeleton.enable_fingers) and '
                     'pose-space corrective shape keys on the body (knee / elbow / hip, delta-mush, see corrective(); hip also carried to the shorts). v1 = byte-identical')
ap.add_argument('--body', choices=['v1', 'v31'], default='v1',
                help='v31 (Realism V3.1, 2026-11-22): athletic morph set on top of the variant EXTRA (broader shoulders / lats, '
                     'defined calves and forearms, trapezius / neck, narrower hips, longer thighs). v1 = byte-identical')
ap.add_argument('--shoe', choices=['v1', 'v31', 'v32'], default='v1',
                help='v31: a separate sole slab (heel 3.2 cm -> toe 1.7 cm, toe spring, 5 mm wider than the upper) under the hull upper')
ap.add_argument('--out-meta', default='', help='write a metadata JSON (bones, meshes, triangles, materials, morphs, animations)')
ap.add_argument('--garment', choices=['v1', 'v2', 'v3', 'v31', 'v32'], default='v1',
                help='v2 (Realism V2, 2026-11-21): looser jersey that HANGS from the chest (straight drape, not painted on the '
                     'belly), 5 cm longer, always outside the shorts waistband, hem weights off the thighs, and per-vertex '
                     '_E2A_HEM / _E2A_EASE attributes for the engine secondary motion (src/t3d/cloth2.ts). v1 = byte-identical')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
RV3 = a.rig == 'v3'
if RV3:
    SK.enable_fingers()

# kits = engine KITS (src/t3d/Athlete.tsx) so the capsule (A) and the mesh (C) read the same on screen
VAR = {
    'off': dict(jersey='#0E2147', trim='#C9A24D', number='#E3BE68', shoe='#F2F2F0', sole='#1A1A1A', sock='#F4F4F4', hair='#15100C',
                skin='#4E3122', num='5', hair_style='curly'),
    'def': dict(jersey='#F3F1EC', trim='#B8322A', number='#B8322A', shoe='#1D1F24', sole='#F2F2F2', sock='#1D1F24', hair='#2A1C12',
                skin='#C68E63', num='1', hair_style='buzz'),
}[a.variant]
NAVY = VAR['jersey']


def shade(h, f):
    c = [int(h[i:i + 2], 16) for i in (1, 3, 5)]
    c = [min(255, max(0, int(round(x * f)))) for x in c]
    return '#%02X%02X%02X' % tuple(c)


NOISE = (shade(VAR['jersey'], 1.35 if VAR['jersey'] < '#8' else 1.03), shade(VAR['jersey'], 0.62 if VAR['jersey'] < '#8' else 0.94))
GOLD = VAR['trim']
NUMBER = VAR['number']
a.number = a.number or VAR['num']
a.skin = a.skin or VAR['skin']
# body morphs on top of mh_body.MACRO/LOCAL (estimated from 5438/5440/5449/5452 silhouettes; the defense variant is
# a heavier, broader frame so the two teams read apart in silhouette, not only by colour)
EXTRA = {
    'off': {'armslegs/l-upperarm-shoulder-muscle-incr': 0.25, 'armslegs/r-upperarm-shoulder-muscle-incr': 0.25,
            'armslegs/l-hand-scale-incr': 0.15, 'armslegs/r-hand-scale-incr': 0.15},
    'def': {'macrodetails/universal-male-young-averagemuscle-averageweight': 0.35, 'macrodetails/universal-male-young-maxmuscle-averageweight': 0.65,
            'torso/torso-scale-horiz-incr': 0.45, 'torso/torso-vshape-incr': 0.2, 'hip/hip-scale-horiz-decr': 0.15,
            'neck/neck-scale-horiz-incr': 0.45, 'armslegs/l-upperarm-shoulder-muscle-incr': 0.4, 'armslegs/r-upperarm-shoulder-muscle-incr': 0.4,
            'armslegs/l-hand-scale-incr': 0.12, 'armslegs/r-hand-scale-incr': 0.12,
            'armslegs/l-upperleg-muscle-incr': 0.35, 'armslegs/r-upperleg-muscle-incr': 0.35},
}[a.variant]
if a.body == 'v31':
    # Realism V3.1 (2026-11-22): the owner read the V3 body as a mannequin (narrow shoulders, tube limbs, no neck). Athletic
    # build on top of the variant set: muscle macro 0.45 -> 0.75 max, wide lats / V, shoulder caps, forearms, calves,
    # trapezius (neck back depth) and a longer thigh. Every target exists in targets.pack (mh_body prints missing ones).
    V31 = {'macrodetails/universal-male-young-averagemuscle-averageweight': -0.3, 'macrodetails/universal-male-young-maxmuscle-averageweight': 0.3,
           'torso/torso-scale-horiz-incr': 0.35, 'torso/torso-vshape-incr': 0.5, 'torso/torso-muscle-dorsi-incr': 0.45,
           'torso/torso-muscle-pectoral-incr': 0.35, 'neck/neck-scale-horiz-incr': 0.4, 'neck/neck-back-scale-depth-incr': 0.6,
           'hip/hip-scale-horiz-decr': 0.25, 'buttocks/buttocks-volume-decr': 0.3, 'armslegs/upperlegs-height-incr': 0.2}
    for s_ in 'lr':
        V31.update({f'armslegs/{s_}-upperarm-shoulder-muscle-incr': 0.45, f'armslegs/{s_}-upperarm-muscle-incr': 0.4,
                    f'armslegs/{s_}-lowerarm-muscle-incr': 0.6, f'armslegs/{s_}-lowerleg-muscle-incr': 0.7,
                    f'armslegs/{s_}-upperleg-muscle-incr': 0.35, f'armslegs/{s_}-hand-scale-incr': 0.08})
    for k_, w_ in V31.items():
        EXTRA[k_] = EXTRA.get(k_, 0.0) + w_


def hex2lin(h, alpha=1.0):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, alpha)


# ---------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.fps = 30
scn.render.fps_base = 1.001
body = mh_body.build(EXTRA)
sk = SK.build(body)
V = sk['V'][:mh_body.NBODY].copy()
B = body['B']
F = B['F']
FU = B['FU']
UV = B['UV']
reg = B['regions'][:mh_body.NBODY]
bones = [b['name'] for b in B['meta']['bones']]

# adjacency
nb = [set() for _ in range(len(V))]
for f in F:
    for k in range(4):
        i, j = f[k], f[(k + 1) % 4]
        nb[i].add(j); nb[j].add(i)
nbl = [np.array(sorted(s)) for s in nb]


def laplace(P, mask_w, iters):
    P = P.copy()
    idx = np.where(mask_w > 0)[0]
    for _ in range(iters):
        avg = np.array([P[nbl[i]].mean(0) for i in idx])
        P[idx] = P[idx] + (avg - P[idx]) * mask_w[idx, None] * 0.6
    return P


# face neutralisation: smooth the front of the head below the hairline (keeps skull, jaw, brow mass and a soft nose)
J = sk['J']
head_c = J['head____head']
face_w = np.zeros(len(V))
hd = np.where(reg == 0)[0]
front = -(V[hd, 1] - (head_c[1] - 0.02))
fz = V[hd, 2]
w = np.clip(front / 0.06, 0, 1) * np.clip((2.035 + mh_body.H_BODY * 0 - fz) / 0.03, 0, 1) * np.clip((fz - (head_c[2] - 0.01)) / 0.03, 0, 1)
face_w[hd] = w
V = laplace(V, face_w, 40)
# keep a soft nose: push the central strip forward a little
nose = sk['lm']['nose']
dn = np.linalg.norm((V - nose) * [1.6, 1.0, 0.8], axis=1)
V[:, 1] -= 0.012 * np.exp(-(dn / 0.025) ** 2) * (reg == 0)

# ---------------------------------------------------------------- weights
WGT = np.zeros((len(V), len(SK.NAMES)))
for i in range(len(V)):
    bi, bv = B['W'][i]
    for b_, v_ in zip(bi, bv):
        WGT[i, SK.NAMES.index(SK.mh2e2a(bones[b_]))] += v_
WGT /= np.maximum(WGT.sum(1, keepdims=True), 1e-9)


def top4(W):
    W = W.copy()
    for i in range(len(W)):
        o = np.argsort(W[i])[::-1]
        W[i, o[4:]] = 0
    return W / np.maximum(W.sum(1, keepdims=True), 1e-9)


WGT = top4(WGT)


# ---------------------------------------------------------------- Realism V3 pose-space correctives (2026-11-22, --rig v3)
# Linear blend skinning collapses the knee and the elbow when they bend (the MakeHuman weights blend thigh/shin over
# ~10 cm: a deep knee flexion folds the back of the knee and flattens the front). Per joint: pose the bind mesh with
# LBS at a key angle, run DELTA MUSH on the posed region (Laplacian smoothing + the rest-pose detail offsets rotated by
# the per-vertex blended rotation) and store the difference, carried back to the bind space through the LBS linear map,
# as a shape key. glTF exports it as a morph target; the engine drives its weight from the joint angle (0 at rest,
# 1 at the key angle) -> deterministic, no simulation, no state.
def _rot(axis, th):
    k = axis / np.linalg.norm(axis)
    K_ = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(th) * K_ + (1 - math.cos(th)) * K_ @ K_


def _desc(b):
    out = [b]
    for n_, par, *_ in SK.BONES:
        if par in out and n_ not in out:
            out.append(n_)
    return out


def corrective(bone, pivot, axis, theta, radius, iters=24):
    moved = _desc(bone)
    wm = WGT[:, [SK.NAMES.index(n_) for n_ in moved]].sum(1)
    R = _rot(axis, theta)
    Pp = V + wm[:, None] * ((V - pivot) @ R.T + pivot - V)
    d = np.linalg.norm(V - pivot, axis=1)
    mask = np.exp(-(d / radius) ** 2)
    mask[mask < 0.03] = 0
    idx = np.where(mask > 0)[0]

    def dm(P):
        Q = P.copy()
        for _ in range(iters):
            avg = np.array([Q[nbl[i]].mean(0) for i in idx])
            Q[idx] += (avg - Q[idx]) * 0.5 * mask[idx, None]
        return Q
    off = V - dm(V)
    k = axis / np.linalg.norm(axis)
    ang = (wm * theta)[:, None]
    roff = off * np.cos(ang) + np.cross(k, off) * np.sin(ang) + np.outer(off @ k, k) * (1 - np.cos(ang))
    corr = dm(Pp) + roff - Pp
    corr[mask == 0] = 0
    M_ = (1 - wm)[:, None, None] * np.eye(3)[None] + wm[:, None, None] * R[None]
    delta = np.linalg.solve(M_, corr[..., None])[..., 0]
    CORR_POSED[bone] = (corr, moved, R)
    return delta, float(np.linalg.norm(corr, axis=1).max())


def transfer_corrective(bone, Wg, extra, gate):
    """the body's posed-space fix of one corrective, carried to a garment built on the body (same iso-cut source
    vertices), re-solved through the GARMENT's own skin weights, faded by gate (0 = untouched, e.g. waistband / trim)"""
    corr, moved, R = CORR_POSED[bone]
    cg = extend(corr, extra) * gate[:, None]
    wm = Wg[:, [SK.NAMES.index(n_) for n_ in moved]].sum(1)
    M_ = (1 - wm)[:, None, None] * np.eye(3)[None] + wm[:, None, None] * R[None]
    return np.linalg.solve(M_, cg[..., None])[..., 0]


CORR = []  # (name, delta, meta)
JCORR = []  # V3.2 garment-only correctives (jersey + its trim): (name, None, meta)
CORR_POSED = {}
if RV3:
    for s_ in 'LR':
        kp = J[f'lowerleg01.{s_}____head']
        dk, mk = corrective(f'shin.{s_}', kp, np.array([1.0, 0, 0]), math.radians(110), 0.12)
        CORR.append((f'knee.{s_}', dk, {'bone': f'shin.{s_}', 'parent': f'thigh.{s_}', 'key': 110}))
        ep_ = J[f'lowerarm01.{s_}____head']
        ua = ep_ - J[f'upperarm01.{s_}____head']; ua /= np.linalg.norm(ua)
        eax = np.cross(ua, np.array([0, -1.0, 0])); eax /= np.linalg.norm(eax)
        de, me_ = corrective(f'forearm.{s_}', ep_, eax, math.radians(100), 0.09)
        CORR.append((f'elbow.{s_}', de, {'bone': f'forearm.{s_}', 'parent': f'upperarm.{s_}', 'key': 100, 'axis': np.round(eax, 5).tolist()}))
        print(f'corrective knee.{s_}: max posed-space fix {mk * 100:.2f} cm; elbow.{s_}: {me_ * 100:.2f} cm')
    # hip flexion (defensive stance / gather): LBS on the thigh-weighted seat folds the glute into a bulge. Signed
    # sagittal flexion at runtime (mode 'flex'), key 80 deg; the same posed-space fix is carried to the shorts.
    for s_ in 'LR':
        hp = J[f'upperleg01.{s_}____head']
        dh, mh = corrective(f'thigh.{s_}', hp, np.array([-1.0, 0, 0]), math.radians(80), 0.2)
        CORR.append((f'hip.{s_}', dh, {'bone': f'thigh.{s_}', 'parent': 'hips', 'key': 80, 'mode': 'flex'}))
        print(f'corrective hip.{s_}: max posed-space fix {mh * 100:.2f} cm')


# vertex normals (area weighted from quads)
def vnormals(P, faces):
    N = np.zeros_like(P)
    for f in faces:
        p = P[f]
        n = np.cross(p[2] - p[0], p[3] - p[1]) if len(f) == 4 else np.cross(p[1] - p[0], p[2] - p[0])
        N[f] += n
    return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)


NRM = vnormals(V, F)
cent = V[F].mean(1)
freg = reg[F[:, 0]]
hip_z = J['HIPC'][2]
knee_z = J['lowerleg01.L____head'][2]

def boundary_loops(faces):
    E = {}
    for f in faces:
        for k in range(len(f)):
            e = (min(f[k], f[(k + 1) % len(f)]), max(f[k], f[(k + 1) % len(f)]))
            E[e] = E.get(e, 0) + 1
    adj = {}
    for (i, j), c in E.items():
        if c == 1:
            adj.setdefault(i, []).append(j); adj.setdefault(j, []).append(i)
    loops, seen = [], set()
    for st in adj:
        if st in seen:
            continue
        loop, cur, prev = [st], st, None
        seen.add(st)
        while True:
            nx = [x for x in adj[cur] if x != prev and x not in seen]
            if not nx:
                break
            prev, cur = cur, nx[0]
            seen.add(cur); loop.append(cur)
        loops.append(loop)
    return loops


def smooth_boundary(P, faces, iters=12, ring_iters=6, flat=None):
    """straighten the jagged boundary of a face subset (1-D Laplacian along each loop, then relax the next ring);
    flat(loop_points) -> z or None: snap a loop onto a horizontal plane (hems)."""
    P = P.copy()
    loops = boundary_loops(faces)
    on = set()
    for lp in loops:
        idx = np.array(lp)
        on.update(lp)
        for _ in range(iters):
            q = P[idx]
            P[idx] = 0.5 * q + 0.25 * (np.roll(q, 1, 0) + np.roll(q, -1, 0))
        if flat is not None:
            z = flat(P[idx])
            if z is not None:
                P[idx, 2] = z
    used = set(np.unique(np.concatenate([np.asarray(f) for f in faces])).tolist())
    ring = [v for v in used if v not in on and any(n_ in on for n_ in nbl[v])]
    for _ in range(ring_iters):
        for v in ring:
            nn = [x for x in nbl[v] if x in used]
            P[v] = 0.5 * P[v] + 0.5 * P[nn].mean(0)
    return P, on


# ---------------------------------------------------------------- face sets
jersey_f = np.where(((freg == 2) & (cent[:, 2] > hip_z - 0.06)))[0]
shorts_f = np.where(((freg == 2) & (cent[:, 2] < hip_z + 0.11)) | (freg == 3) | ((freg == 7) & (cent[:, 2] > knee_z + 0.10)) |
                    ((freg == 255) & (cent[:, 2] < hip_z + 0.11) & (cent[:, 2] > knee_z + 0.10)))[0]
shoe_f = np.where((freg == 9) | ((freg == 255) & (cent[:, 2] < 0.13)) | ((freg == 8) & (cent[:, 2] < 0.12)))[0]
hair_line = lambda P: np.interp(P[:, 1] - head_c[1], [-0.2, -0.08, 0.0, 0.08], [2.045, 2.02, 1.975, 1.935])
hair_v = (reg == 0) & (V[:, 2] > hair_line(V))
hair_f = np.where(hair_v[F].all(1))[0]
# body faces hidden under clothes / shoes (margin so no gap shows)
hide = np.zeros(len(F), bool)
hide[np.where((freg == 2) & (cent[:, 2] > hip_z - 0.03) & (cent[:, 2] < J['neck01____head'][2] - 0.06))[0]] = True
hide[np.where(((freg == 7) | (freg == 3) | (freg == 255)) & (cent[:, 2] > knee_z + 0.14) & (cent[:, 2] < hip_z + 0.08))[0]] = True
hide[np.where((freg == 9))[0]] = True
# keep the shoulders / armpits of the torso visible (sleeveless): only hide faces well inside the jersey
armpit = (freg == 2) & (np.abs(cent[:, 0]) > 0.16) & (cent[:, 2] > J['upperarm01.L____head'][2] - 0.12)
hide[armpit] = False
body_f = np.where(~hide)[0]

# ---------------------------------------------------------------- cloth edges cut on iso-lines (2026-11-20)
# The face sets above follow the MakeHuman quads, so their boundary is a staircase; smoothing that boundary loop
# moved its vertices but left the staircase in the skin under it and in the ring next to it (jagged collar /
# armholes / hems, skin quads poking through at the shoulder straps and at the shorts hem, Pistol cover 2026-11-20).
# --cloth-cut iso (default): each garment is a SMOOTH FIELD on the body surface (the face-set indicator diffused over
# the mesh graph, capped by a horizontal plane at the hem) and the garment / the hidden skin are the parts of the
# quads on one side of an iso-line of that field, cut exactly through the quads (new vertices on the edges, skin
# weights / normals / UVs interpolated). The skin is cut on a DEEPER iso-line than the cloth, so its hidden-region
# edge is always ~2 quads under the garment and never shows. --cloth-cut legacy rebuilds the 2026-11-19 meshes.
EV = np.unique(np.sort(np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 3]], F[:, [3, 0]]]), 1), axis=0)
DEG = np.zeros(len(V)); np.add.at(DEG, EV.ravel(), 1)


def face_indicator(face_idx):
    m = np.zeros(len(F)); m[face_idx] = 1
    s = np.zeros(len(V)); c = np.zeros(len(V))
    np.add.at(s, F.ravel(), np.repeat(m, 4)); np.add.at(c, F.ravel(), 1)
    return s / np.maximum(c, 1)


def diffuse(g, iters, lam=0.5):
    g = g.copy()
    for _ in range(iters):
        s = np.zeros(len(V)); np.add.at(s, EV[:, 0], g[EV[:, 1]]); np.add.at(s, EV[:, 1], g[EV[:, 0]])
        g = g + lam * (s / np.maximum(DEG, 1) - g)
    return g


def plane_up(z0, width=0.03):
    """0.5 on the plane z = z0, growing upwards: min(field, plane_up(hem)) puts a flat hem at z0"""
    return 0.5 + (V[:, 2] - z0) / width


def iso_clip(face_idx, g, thr=0.5):
    """the parts of the quads face_idx where g >= thr. Returns (polygons over the extended vertex list,
    extra = [(i, j, t)] new vertices i + t (j - i) numbered from len(V), corner sources per polygon
    [(corner a, corner b, t)] to interpolate per-corner data such as UVs, source quad of each polygon)."""
    n = len(V); extra, key, out, src, fids = [], {}, [], [], []

    def edge_vertex(i, j):
        a_, b_ = (i, j) if i < j else (j, i)
        if (a_, b_) not in key:
            t = float(np.clip((thr - g[a_]) / (g[b_] - g[a_]), 0.0, 1.0))
            key[(a_, b_)] = n + len(extra); extra.append((a_, b_, t))
        return key[(a_, b_)]

    for fi in face_idx:
        f = F[fi]; gv = g[f] - thr
        inside = gv >= 0
        if inside.all():
            out.append([int(x) for x in f]); src.append([(k, k, 0.0) for k in range(4)]); fids.append(int(fi)); continue
        if not inside.any():
            continue
        poly, cs = [], []
        for k in range(4):
            k2 = (k + 1) % 4
            if inside[k]:
                poly.append(int(f[k])); cs.append((k, k, 0.0))
            if inside[k] != inside[k2]:
                poly.append(edge_vertex(int(f[k]), int(f[k2]))); cs.append((k, k2, float(gv[k] / (gv[k] - gv[k2]))))
        if len(poly) >= 3:
            out.append(poly); src.append(cs); fids.append(int(fi))
    return out, extra, src, fids


def extend(A, extra, unit=False, weights=False):
    """per-vertex data A on the extended vertex list of iso_clip"""
    if not extra:
        return A.copy()
    i = np.array([e[0] for e in extra]); j = np.array([e[1] for e in extra]); t = np.array([e[2] for e in extra])
    t = t.reshape((-1,) + (1,) * (A.ndim - 1))
    B_ = np.concatenate([A, A[i] * (1 - t) + A[j] * t])
    if unit:
        B_ /= np.maximum(np.linalg.norm(B_, axis=1, keepdims=True), 1e-9)
    if weights:
        B_ = top4(B_)
    return B_


def smooth_loops(P, faces, iters=4, flat=None):
    """light 1-D Laplacian along each boundary loop (the iso-cut is already smooth: this only evens the spacing)"""
    P = P.copy()
    for lp in boundary_loops(faces):
        idx = np.array(lp)
        if len(idx) < 6:
            continue
        for _ in range(iters):
            q = P[idx]
            P[idx] = 0.5 * q + 0.25 * (np.roll(q, 1, 0) + np.roll(q, -1, 0))
        if flat is not None:
            z = flat(P[idx])
            if z is not None:
                P[idx, 2] = z
    return P


def smooth_field(X, faces, mask, iters=20, lam=0.5, renorm=False):
    """Realism V3.2: Laplacian smoothing of a per-vertex field (skin weights n x B, or a scalar n) over the garment's
    edge graph, only on `mask` vertices (the rest stay fixed and act as boundary). Weights are renormalised per row.
    Why: a skin-weight change over ONE ring of edges (strap: chest -> clavicle, shorts hem: hips -> thigh) is what
    stretches those triangles by 2-3x in a raised-arm / high-knee pose (qc_cloth_v32 on V3.1); spreading the same
    change over 6-10 rings keeps the stretch near the fabric's (<= ~1.3)."""
    E = set()
    for f in faces:
        for i in range(len(f)):
            a_, b_ = f[i], f[(i + 1) % len(f)]
            E.add((min(a_, b_), max(a_, b_)))
    E = np.array(sorted(E))
    Y = np.array(X, dtype=np.float64, copy=True)
    one = Y.ndim == 1
    if one:
        Y = Y[:, None]
    n = len(Y)
    deg = np.bincount(E.ravel(), minlength=n).astype(np.float64)
    m = np.zeros(n, bool)
    mk = np.asarray(mask)
    if mk.dtype == bool:
        m[:len(mk)] = mk
    else:
        m[mk] = True
    m &= deg > 0
    for _ in range(iters):
        S = np.zeros_like(Y)
        np.add.at(S, E[:, 0], Y[E[:, 1]])
        np.add.at(S, E[:, 1], Y[E[:, 0]])
        Nb = S / np.maximum(deg, 1)[:, None]
        Y[m] = (1 - lam) * Y[m] + lam * Nb[m]
        if renorm:
            Y[m] /= np.maximum(Y[m].sum(1, keepdims=True), 1e-9)
    return Y[:, 0] if one else Y


def fourier_loops(P, faces, K=10, flat=None, min_len=12):
    """Realism V3: low-pass every boundary loop of a garment (keep the first K harmonics of the closed curve): the iso-cut
    hem / armhole / collar lines keep a few-mm ripple from the quads that the gold piping (a tube along the loop) turned
    into a visibly WAVY trim. Only the loop vertices move (sub-cm)."""
    P = P.copy()
    for lp in boundary_loops(faces):
        idx = np.array(lp)
        if len(idx) < min_len:
            continue
        Fq = np.fft.rfft(P[idx], axis=0)
        Fq[min(K, len(Fq) - 1) + 1:] = 0
        P[idx] = np.fft.irfft(Fq, n=len(idx), axis=0)
        if flat is not None:
            z = flat(P[idx])
            if z is not None:
                P[idx, 2] = z
    return P


def taubin_garment(P, polys, Vsrc, Nsrc, iters=30, min_off=0.006, lam=0.5, mu=-0.53):
    """Realism V3: fabric does not follow every muscle. Taubin (lambda/mu, no shrink) smoothing of a garment surface over its
    own mesh graph, boundary loops (hems, armholes, collar) pinned, then every vertex pushed back out to >= min_off along the
    body normal of the vertex it was cut from (no penetration). Removes the lumpy back / seat of the v1-v2 garments."""
    P = P.copy()
    E_ = set()
    for f_ in polys:
        for k in range(len(f_)):
            i_, j_ = f_[k], f_[(k + 1) % len(f_)]
            E_.add((min(i_, j_), max(i_, j_)))
    E_ = np.array(sorted(E_))
    used = np.unique(E_)
    pinned = np.zeros(len(P), bool)
    for lp in boundary_loops(polys):
        pinned[np.array(lp)] = True
    deg = np.zeros(len(P)); np.add.at(deg, E_.ravel(), 1)
    free = np.zeros(len(P), bool); free[used] = True; free &= ~pinned
    for it in range(iters):
        for f_ in (lam, mu):
            acc = np.zeros_like(P)
            np.add.at(acc, E_[:, 0], P[E_[:, 1]]); np.add.at(acc, E_[:, 1], P[E_[:, 0]])
            L = acc / np.maximum(deg, 1)[:, None] - P
            P[free] += f_ * L[free]
        off = np.einsum('ij,ij->i', P - Vsrc, Nsrc)
        low = free & (off < min_off)
        P[low] += Nsrc[low] * (min_off - off[low])[:, None]
    return P


GV2 = a.garment in ('v2', 'v3', 'v31', 'v32')  # v3 keeps the v2 jersey drape and adds the v3 shorts / trims / attributes below
GV3 = a.garment in ('v3', 'v31', 'v32')
GV31 = a.garment in ('v31', 'v32')  # Realism V3.1: loose jersey (deeper armholes, air gap) and looser shorts on top of v3
GV32 = a.garment == 'v32'  # Realism V3.2: V3.1 cut + smoothed weights / hem fields, fold + strap correctives (see GV32 blocks)
hem_j = hip_z - (0.085 if GV2 else 0.05)
hem_s = knee_z + 0.12
ISO_DIFF = 10  # graph diffusion steps (lam 0.5): rounds the staircase (quads ~2-3 cm) without eating the straps
# iso mode: the garment sets reach PAST their hems (jersey to the pelvis, shorts to the knee) so that, near a hem, the
# diffused field is ~1 and the hem is the plane alone (flat, no notch where a MakeHuman region boundary dips); the
# jersey then overlaps the shorts' waistband by 7 cm (its hem piping never z-fights the waist piping)
jersey_iso_f = np.union1d(jersey_f, np.where(((freg == 2) | (freg == 3)) & (cent[:, 2] > hem_j - 0.04) & (cent[:, 2] < hip_z + 0.2))[0])
shorts_iso_f = np.union1d(shorts_f, np.where(((freg == 7) | (freg == 255)) & (cent[:, 2] > knee_z + 0.02) & (cent[:, 2] < hip_z + 0.11))[0])
D_jersey = diffuse(face_indicator(jersey_iso_f), ISO_DIFF)
D_shorts = diffuse(face_indicator(shorts_iso_f), ISO_DIFF)
G_jersey = np.minimum(D_jersey, plane_up(hem_j))
G_shorts = np.minimum(D_shorts, plane_up(hem_s))
# skin hidden only DEEP inside a garment: the 0.80 iso-line of the diffused set and 4 cm above the hems
G_skin_hide = np.maximum(np.minimum(D_jersey - 0.30, plane_up(hem_j + 0.04)), np.minimum(D_shorts - 0.30, plane_up(hem_s + 0.04)))
if GV3:
    # Realism V3: keep 10 cm of thigh skin inside the loose leg opening (the hem swings with cloth2: never a see-through hole)
    G_skin_hide = np.maximum(np.minimum(D_jersey - 0.30, plane_up(hem_j + 0.04)), np.minimum(D_shorts - 0.30, plane_up(hem_s + 0.10)))
if GV31:
    # Realism V3.1: DEEP armholes of a basketball jersey (the MakeHuman torso region stops at the shoulder joint, the V3
    # jersey hugged the armpit like a tank top). An ellipse in the x-z plane round each shoulder joint (any y): the jersey
    # ends on it (bottom 21 cm under the joint, 6 cm straps), the skin stays visible 3 cm inside it (the gap shows body)
    _sh = J['upperarm01.L____head']; AH_X, AH_Z = abs(float(_sh[0])), float(_sh[2]) - 0.06
    AH_R = (0.078, 0.15)
    _ah = np.hypot((np.abs(V[:, 0]) - AH_X) / AH_R[0], (V[:, 2] - AH_Z) / AH_R[1])
    G_jersey = np.minimum(G_jersey, 0.5 + (_ah - 1.0) / 0.08)
    G_skin_hide = np.minimum(G_skin_hide, 0.5 + (_ah - 1.3) / 0.08)

# ---------------------------------------------------------------- textures (PIL)
from PIL import Image, ImageDraw, ImageFont
TEXDIR = os.path.join(os.path.dirname(os.path.abspath(a.out_blend)), 'tex')
os.makedirs(TEXDIR, exist_ok=True)


def font(size):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def jersey_texture(path, num):
    W, H = 2048, 1024
    im = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(im)
    import random
    rnd = random.Random(5)
    for _ in range(26000):  # mesh fabric
        x, y = rnd.randrange(W), rnd.randrange(H)
        d.point((x, y), fill=NOISE[0] if rnd.random() < 0.5 else NOISE[1])
    # side panels (under the arms: u = 0 / 0.5 are the left / right sides)
    for u in (0.0, 0.5, 1.0):  # thin side piping under the arms
        d.rectangle([u * W - 7, 0, u * W + 7, H], fill=GOLD)
    f = font(380)
    for u, s in ((0.25, 1.0), (0.75, 1.25)):  # front, back
        cx, cy = u * W, H * 0.42
        bb = d.textbbox((0, 0), num, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tmp = Image.new('RGBA', (tw + 60, th + 80), (0, 0, 0, 0))
        dt = ImageDraw.Draw(tmp)
        dt.text((30 - bb[0], 40 - bb[1]), num, font=f, fill=NUMBER, stroke_width=12, stroke_fill=GOLD)
        tmp = tmp.resize((int(tmp.width * 0.62 * s), int(tmp.height * s)))
        im.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)), tmp)
    im.save(path)


jersey_texture(os.path.join(TEXDIR, 'jersey_navy_gold.png'), a.number)


def shorts_texture(path):
    W, H = 1024, 512
    im = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(im)
    import random
    rnd = random.Random(7)
    for _ in range(9000):
        d.point((rnd.randrange(W), rnd.randrange(H)), fill=NOISE[0] if rnd.random() < 0.5 else NOISE[1])
    for u in (0.0, 0.5, 1.0):  # gold side stripes (outer side of each leg)
        d.rectangle([u * W - 16, 0, u * W + 16, H], fill=GOLD)
    im.save(path)


shorts_texture(os.path.join(TEXDIR, 'shorts_navy_gold.png'))


# ---------------------------------------------------------------- materials
def mat(name, color, rough=0.7, tex=None, sss=0.0, sheen=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = hex2lin(color)
    bsdf.inputs['Roughness'].default_value = rough
    if 'Subsurface Weight' in bsdf.inputs and sss:
        bsdf.inputs['Subsurface Weight'].default_value = sss
        bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.35, 0.2)
        bsdf.inputs['Subsurface Scale'].default_value = 0.01
    if sheen and 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = sheen
        # glTF KHR_materials_sheen exports the tint as sheenColor (weight ignored): keep it dark, or three.js turns the cloth silver
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (0.10, 0.11, 0.15, 1.0)
    if tex:
        img = bpy.data.images.load(tex)
        tn = m.node_tree.nodes.new('ShaderNodeTexImage')
        tn.image = img
        m.node_tree.links.new(tn.outputs['Color'], bsdf.inputs['Base Color'])
    return m


M_SKIN = mat('E2A_skin', a.skin, 0.52, sss=0.15)
M_JERSEY = mat('E2A_jersey', NAVY, 0.78, tex=os.path.join(TEXDIR, 'jersey_navy_gold.png'), sheen=0.2)
M_TRIM = mat('E2A_trim_gold', GOLD, 0.6)
M_SHORTS = mat('E2A_shorts', NAVY, 0.8, tex=os.path.join(TEXDIR, 'shorts_navy_gold.png'), sheen=0.2)
M_SOCK = mat('E2A_sock', VAR['sock'], 0.9)
M_SHOE = mat('E2A_shoe', VAR['shoe'], 0.42)
M_SOLE = mat('E2A_sole', VAR['sole'], 0.6)
M_HAIR = mat('E2A_hair', VAR['hair'], 0.92)


# ---------------------------------------------------------------- mesh helpers
def make_mesh(name, P, faces, mats, face_mat, uvs=None, W=None):
    used = np.unique(np.concatenate([np.asarray(f) for f in faces]))
    remap = -np.ones(len(P), int)
    remap[used] = np.arange(len(used))
    me = bpy.data.meshes.new(name)
    fl = [[int(remap[i]) for i in f] for f in faces]
    me.from_pydata(P[used].tolist(), [], fl)
    me.update()
    for m in mats:
        me.materials.append(m)
    for pi, poly in enumerate(me.polygons):
        poly.material_index = int(face_mat[pi])
        poly.use_smooth = True
    if uvs is not None:
        uvl = me.uv_layers.new(name='UVMap')
        k = 0
        for pi, poly in enumerate(me.polygons):
            for li in poly.loop_indices:
                uvl.data[li].uv = uvs[pi][li - poly.loop_start]
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if W is not None:
        for bi, bn in enumerate(SK.NAMES):
            vg = ob.vertex_groups.new(name=bn)
            for vi_new, vi_old in enumerate(used):
                if W[vi_old, bi] > 1e-4:
                    vg.add([vi_new], float(W[vi_old, bi]), 'REPLACE')
    return ob, used


def pipe_loops(name, P, faces, W, radius=0.006, keep=lambda q: True, inset=0.004, keys=None):
    """gold piping: a thin tube along every boundary loop of a clothing mesh, skinned like its nearest vertex
    (V3.2: keys = {shape key: delta per source vertex} -> the same shape keys on the tube, so it stays on its edge)"""
    verts, quads, wts, src = [], [], [], []
    Nl = vnormals(P, faces)
    for lp in boundary_loops(faces):
        q = P[lp]
        if len(lp) < 6 or not keep(q):
            continue
        m = len(lp)
        base = len(verts)
        for k in range(m):
            tng = q[(k + 1) % m] - q[k - 1]
            tng /= max(np.linalg.norm(tng), 1e-9)
            nn = Nl[lp[k]]
            bn = np.cross(tng, nn)
            c = q[k] + nn * 0.002 - bn * 0  # on the edge
            for r in range(6):
                ang = 2 * math.pi * r / 6
                verts.append(c + radius * (math.cos(ang) * nn + math.sin(ang) * bn))
                wts.append(W[lp[k]])
                src.append(lp[k])
        for k in range(m):
            for r in range(6):
                a0 = base + k * 6 + r; a1 = base + k * 6 + (r + 1) % 6
                b0 = base + ((k + 1) % m) * 6 + r; b1 = base + ((k + 1) % m) * 6 + (r + 1) % 6
                quads.append([a0, a1, b1, b0])
    if not verts:
        return None
    verts = np.array(verts); wts = np.array(wts)
    ob, used_ = make_mesh(name, verts, quads, [M_TRIM], [0] * len(quads), None, wts)
    if keys:
        ob.shape_key_add(name='Basis', from_mix=False)
        for nm, dl in keys.items():
            kb = ob.shape_key_add(name=nm, from_mix=False)
            for vi_new, vi_old in enumerate(used_):
                kb.data[vi_new].co = (verts[vi_old] + dl[src[vi_old]]).tolist()
    return ob


# body (skin + socks)
ISO = a.cloth_cut == 'iso'
sock_face = (cent[:, 2] < 0.26) & ((freg == 8) | (freg == 255))
# V3.2 shoe: low open collar, so the sock of the ankle / upper foot (above FOOT_SHOW_Z) is kept and enters the collar
FOOT_SHOW_Z = 0.075 if a.shoe == 'v32' else 9.0
foot_show = (freg == 9) & (cent[:, 2] > FOOT_SHOW_Z)
sock_face = sock_face | foot_show
if ISO:
    UVa = np.asarray(UV, float)
    bpoly, bextra, bsrc, bfid = iso_clip(np.where((freg != 9) | foot_show)[0], 1.0 - G_skin_hide, 0.5)  # feet: under the shoes
    bmat = [1 if sock_face[fi] else 0 for fi in bfid]
    buv = [[(UVa[FU[fi][c0]] * (1 - t) + UVa[FU[fi][c1]] * t).tolist() for c0, c1, t in cs] for fi, cs in zip(bfid, bsrc)]
    ob_body, bused = make_mesh('E2A_Body', extend(V, bextra), bpoly, [M_SKIN, M_SOCK], bmat, buv, extend(WGT, bextra, weights=True))
    if CORR:
        Vext = extend(V, bextra)
        ob_body.shape_key_add(name='Basis', from_mix=False)
        for nm, dl, _m in CORR:
            kb = ob_body.shape_key_add(name=nm, from_mix=False)
            de = extend(dl, bextra)
            for vi_new, vi_old in enumerate(bused):
                kb.data[vi_new].co = (Vext[vi_old] + de[vi_old]).tolist()
else:
    bf = [F[i] for i in body_f]
    bmat = [1 if sock_face[i] else 0 for i in body_f]
    buv = [[UV[FU[i][k]] for k in range(4)] for i in body_f]
    ob_body, _ = make_mesh('E2A_Body', V, bf, [M_SKIN, M_SOCK], bmat, buv, WGT)


def garment(G, face_set):
    """(polygons, vertices, normals, weights) of a garment: iso-cut of G (default) or the legacy face set"""
    if ISO:
        poly, extra, _, _ = iso_clip(np.where((G[F] >= 0.5).any(1))[0], G, 0.5)
        GEXTRA[id(G)] = extra
        return poly, extend(V, extra), extend(NRM, extra, unit=True), extend(WGT, extra, weights=True)
    GEXTRA[id(G)] = []
    return [list(F[i]) for i in face_set], V.copy(), NRM, WGT


GEXTRA = {}


# cylindrical UV around the trunk axis: u = 0 his left side, 0.25 front, 0.5 right side, 0.75 back
def cyl_uv(p, z0, z1):
    phi = math.atan2(-(p[1] - 0.02), p[0])
    u = 1.0 - (phi % (2 * math.pi)) / (2 * math.pi)  # u grows clockwise seen from above -> text reads correctly outside
    return [u, (p[2] - z0) / (z1 - z0)]


def cyl_uvs(P, polys, z0, z1):
    out = []
    for f in polys:
        uvq = [cyl_uv(P[v], z0, z1) for v in f]
        us = [q[0] for q in uvq]
        if max(us) - min(us) > 0.5:  # seam: keep the polygon on one side
            uvq = [[q[0] + (1 if q[0] < 0.5 else 0), q[1]] for q in uvq]
        out.append(uvq)
    return out


# jersey: offset outward, looser below the chest, flared hem
jpoly, Vj, Nj, Wj = garment(G_jersey, jersey_f)
chest_z = J['spine01____head'][2]
off = 0.02 + 0.01 * np.clip((chest_z - Vj[:, 2]) / 0.25, 0, 1) + (0.026 if ISO else 0.012) * np.clip((hip_z + 0.02 - Vj[:, 2]) / 0.08, 0, 1)
Pj = Vj + Nj * off[:, None]
jflat = lambda q: hem_j if q[:, 2].max() < hip_z + 0.02 else None
if ISO:
    Pj = smooth_loops(Pj, jpoly, 4, flat=jflat)
else:
    Pj, jon = smooth_boundary(Pj, jpoly, 26, 8, flat=jflat)
z0j, z1j = (hem_j - 0.01) if GV2 else (hip_z - 0.06), J['neck01____head'][2]
jmat = [0] * len(jpoly)  # trims are a separate piping mesh (pipe_loops) along the boundaries
if GV2:
    # ---- Realism V2 drape: below the chest the jersey falls STRAIGHT from the widest chest/back section (radial target
    # per direction round the trunk axis), blended in over the top third so there is no kink under the chest; the hem
    # flares 1.5 cm. Radii about a vertical axis through x = 0, y = mean of the chest band.
    inj = np.zeros(len(Pj), bool); inj[np.unique(np.concatenate([np.asarray(f_) for f_ in jpoly]))] = True  # jersey vertices only
    band = inj & (Pj[:, 2] > chest_z - 0.06) & (Pj[:, 2] < chest_z + 0.05)
    yc = float(Pj[band, 1].mean())
    th = np.arctan2(Pj[:, 1] - yc, Pj[:, 0]); rr = np.hypot(Pj[:, 0], Pj[:, 1] - yc)
    NB = 48
    bi = ((th + math.pi) / (2 * math.pi) * NB).astype(int) % NB
    rch = np.zeros(NB)
    for k in range(NB):
        m = band & (bi == k)
        rch[k] = rr[m].max() if m.any() else 0.0
    for k in range(NB):  # empty bins (armholes): neighbours
        if rch[k] == 0:
            rch[k] = max(rch[(k - 1) % NB], rch[(k + 1) % NB])
    rch = np.array([max(rch[(k - 1) % NB], rch[k], rch[(k + 1) % NB]) * 0.5 + rch[k] * 0.5 for k in range(NB)])
    u = np.clip((chest_z - Pj[:, 2]) / (chest_z - hem_j), 0, 1)
    tgt = rch[bi] * (1 - 0.05 * u) + 0.015 * u ** 2
    wb = np.clip(u / 0.35, 0, 1); wb = wb * wb * (3 - 2 * wb)
    rn = np.maximum(rr, rr + (tgt - rr) * wb)
    if GV3:
        # ---- Realism V3 drape (2026-11-22 second pass): V2 fell STRAIGHT from the widest chest/back section -> a stiff
        # box with a flat back panel. V3 hangs from the shoulders and TAPERS to the hips: below the chest the target
        # radius moves from the chest section to the body's own radius at that height + an ease that grows toward the
        # hem (2.2 -> 3.6 cm), so the hem follows the body (Taubin + the shorts clearance below keep it smooth / outside)
        rbody = np.hypot(Vj[:, 0], Vj[:, 1] - yc)
        s3 = np.clip((u - 0.08) / 0.55, 0, 1); s3 = s3 * s3 * (3 - 2 * s3)
        t3 = rch[bi] * (1 - s3) + (rbody + 0.022 + 0.014 * u) * s3
        if GV31:
            # V3.1 loose cut: 1.2 cm of air over the widest chest section, the taper 70 % of the way to the body and an
            # ease of 3 -> 4.6 cm toward the hem (a real jersey hangs off the shoulders and lats, it never touches the belly)
            s3h = s3 * 0.7
            t3 = (rch[bi] + 0.012) * (1 - s3h) + (rbody + 0.03 + 0.016 * u) * s3h
        rn = np.where(inj & (u > 0), np.maximum(rbody + 0.012, rr + (t3 - rr) * wb), rn)
    Pj[:, 0] = np.cos(th) * rn; Pj[:, 1] = yc + np.sin(th) * rn
    if GV31:
        # air gap at the armhole edge / upper back: 0.9 cm along the normal from the shoulder line down to the chest
        _g = inj & (Pj[:, 2] < AH_Z + 0.04) & (Pj[:, 2] > chest_z - 0.12)
        Pj[_g] += Nj[_g] * (0.009 * np.clip((AH_Z + 0.04 - Pj[_g, 2]) / 0.06, 0, 1) * np.clip((Pj[_g, 2] - chest_z + 0.12) / 0.06, 0, 1))[:, None]
        th = np.arctan2(Pj[:, 1] - yc, Pj[:, 0]); rn = np.hypot(Pj[:, 0], Pj[:, 1] - yc)
    J_EASE = rn - np.hypot(Vj[:, 0], Vj[:, 1] - yc)  # horizontal gap to the body surface it was cut from
    J_TH, J_YC = th, yc
else:
    juv = cyl_uvs(Pj, jpoly, z0j, z1j)
    ob_jersey, _ = make_mesh('E2A_Jersey', Pj, jpoly, [M_JERSEY, M_TRIM], jmat, juv, Wj)
    ob_jpipe = pipe_loops('E2A_JerseyTrim', Pj, jpoly, Wj, 0.0062)

# shorts: loose; leg part pushed away from the thigh axis, flared towards the hem
spoly, Vs, Ns, Wsh = garment(G_shorts, shorts_f)
Ps = Vs.copy()
offs = np.full(len(Vs), 0.022)
for s in 'LR':
    h0 = J[f'upperleg01.{s}____head']; k0 = J[f'lowerleg01.{s}____head']
    ax = (k0 - h0) / np.linalg.norm(k0 - h0)
    side = (Vs[:, 0] > 0) if s == 'L' else (Vs[:, 0] <= 0)
    legp = side & (Vs[:, 2] < hip_z - 0.02)
    rel = Vs - h0
    along = rel @ ax
    radial = rel - np.outer(along, ax)
    rn = radial / np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
    u = np.clip((hip_z - 0.02 - Vs[:, 2]) / (hip_z - knee_z - 0.12), 0, 1)
    push = 0.012 + 0.035 * u
    Ps[legp] += rn[legp] * push[legp, None]
Ps += Ns * offs[:, None]
Wsh = Wsh.copy()
hips_i = SK.NAMES.index('hips')
for s in 'LR':
    ti = SK.NAMES.index('thigh.' + s)
    u = np.clip((hip_z - Vs[:, 2]) / 0.4, 0, 1) * 0.3
    if GV3:
        # Realism V3: the leg TUBE follows the thigh rigidly (the 30 % hips share made it lag ~0.3 x the thigh swing on
        # a sprint stride and opened the hidden-skin hole at the hem); swing comes from the cloth2 hem band instead
        u = u * np.clip((Vs[:, 2] - (hip_z - 0.12)) / 0.08, 0, 1)
    mv = Wsh[:, ti] * u
    Wsh[:, ti] -= mv
    Wsh[:, hips_i] += mv
if GV2:
    # Realism V2: the shorts WAISTBAND follows the pelvis, not the thighs (MakeHuman weights the lower belly ~0.8 to
    # the thigh, so on a high knee the waistband swung 15-20 cm through the jersey; qc-realism cloth_clip 2026-11-21)
    for s in 'LR':
        ti = SK.NAMES.index('thigh.' + s)
        uu = np.clip((Vs[:, 2] - (hip_z - 0.06)) / 0.08, 0, 1)
        mv = Wsh[:, ti] * uu
        Wsh[:, ti] -= mv
        Wsh[:, hips_i] += mv
S_HEM = S_EASE = None
if GV3:
    # ---- Realism V3 shorts (2026-11-22). V1/V2 = body surface + 2.2 cm along the normal + a per-vertex push of the leg
    # (1.2 -> 4.7 cm): every bump of the glutes and thighs is kept and inflated -> "balloon shorts". V3 = fabric cut:
    #   waistband snug (0.6 cm ease, elastic), seat / hips 1.0 cm, and each leg a TUBE round the thigh axis whose
    #   cross-section is 55 % the mean radius at that height + 45 % the (angularly smoothed) body radius, plus an ease
    #   growing from 1.6 cm at the crotch to 3.4 cm at the hem (A-line, room for the stride); the inner side near the
    #   crotch gets at most 1.2 cm so the two legs never meet. Never closer than 0.8 cm to the body.
    inS = np.zeros(len(Vs), bool); inS[np.unique(np.concatenate([np.asarray(f_) for f_ in spoly]))] = True
    sm = lambda x: x * x * (3 - 2 * x)
    wz = sm(np.clip((Vs[:, 2] - (hip_z + 0.02)) / 0.06, 0, 1))
    Ps = Vs + Ns * (0.010 * (1 - wz) + 0.006 * wz)[:, None]
    S_EASE = np.full(len(Vs), 0.008)
    S_HEM = np.zeros(len(Vs))
    top_leg = hip_z - 0.04
    for s_, sg in (('L', 1), ('R', -1)):
        h0 = J[f'upperleg01.{s_}____head']; k0 = J[f'lowerleg01.{s_}____head']
        ax = (k0 - h0) / np.linalg.norm(k0 - h0)
        e1 = np.array([1.0, 0, 0]) - ax * ax[0]; e1 /= np.linalg.norm(e1); e2 = np.cross(ax, e1)
        legp = inS & (np.sign(Vs[:, 0]) == sg) & (Vs[:, 2] < top_leg + 0.02)
        idx = np.where(legp)[0]
        rel = Vs[idx] - h0
        along = rel @ ax
        rad = rel - np.outer(along, ax)
        r = np.linalg.norm(rad, axis=1)
        rn = rad / np.maximum(r[:, None], 1e-9)
        ang = np.arctan2(rn @ e2, rn @ e1)
        NB, NA = 20, 24
        a0, a1 = along.min(), along.max()
        bi = np.clip(((along - a0) / max(1e-6, a1 - a0) * NB).astype(int), 0, NB - 1)
        ai = ((ang + math.pi) / (2 * math.pi) * NA).astype(int) % NA
        rmean = np.array([r[bi == k].mean() if (bi == k).any() else r.mean() for k in range(NB)])
        rb = np.zeros((NB, NA))
        for k in range(NB):
            for q in range(NA):
                m_ = (bi == k) & (ai == q)
                rb[k, q] = r[m_].max() if m_.any() else np.nan
        for k in range(NB):  # empty angle bins: circular fill, then a 5-bin circular moving average
            row = rb[k]
            if np.isnan(row).all():
                row[:] = rmean[k]
            for q in range(NA):
                if np.isnan(row[q]):
                    j_ = q
                    while np.isnan(row[j_ % NA]):
                        j_ += 1
                    row[q] = row[j_ % NA]
            rb[k] = np.mean([np.roll(row, d) for d in (-2, -1, 0, 1, 2)], axis=0)
        # second pass: the BACK of each leg hangs straight down from the widest glute section (cumulative max along
        # the leg for back-facing angles): fabric bridges the under-glute fold instead of following it ("seat bulge")
        qa = (np.arange(NA) + 0.5) / NA * 2 * math.pi - math.pi
        backq = ((np.cos(qa) * e1[1] + np.sin(qa) * e2[1]) > 0.15)[None, :]
        rb = np.where(backq, np.maximum.accumulate(rb, axis=0), rb)
        u = np.clip((top_leg - Vs[idx, 2]) / (top_leg - hem_s), 0, 1)
        # second pass (2026-11-22): looser, separate openings: ease 1.6 cm at the crotch -> 5.4 cm at the hem
        target = 0.55 * rmean[bi] + 0.45 * rb[bi, ai] + 0.016 + 0.038 * u ** 1.3
        if GV31:  # V3.1: a little wider (2.0 cm at the crotch -> 5.8 cm at the hem): the V3.1 thighs are already bigger
            target = 0.6 * rmean[bi] + 0.4 * rb[bi, ai] + 0.02 + 0.038 * u ** 1.2
        wt = sm(np.clip((top_leg + 0.02 - Vs[idx, 2]) / 0.08, 0, 1))
        newr = r + (target - r) * wt
        inner = (rn @ np.array([-sg, 0.0, 0.0])) > 0.3
        cap = np.where(inner & (Vs[idx, 2] > hip_z - 0.22), r + 0.012, np.inf)
        newr = np.clip(newr, r + 0.008, cap)
        P_tube = h0 + np.outer(along, ax) + rn * newr[:, None]
        Ps[idx] = Ps[idx] * (1 - wt[:, None]) + P_tube * wt[:, None]
        S_EASE[idx] = newr - r
        S_HEM[idx] = 0.9 * np.clip(1 - (Vs[idx, 2] - hem_s) / 0.18, 0, 1) ** 1.3
    # second pass: the SEAT (above the leg tubes, back half) bridges the gluteal cleft: per 2 cm height slice the radius
    # about the vertical pelvis axis is the circular max over +-20 deg (a sheet of fabric over two round shapes)
    yc_s = float((J['upperleg01.L____head'][1] + J['upperleg01.R____head'][1]) / 2)
    mid = inS & (np.abs(Vs[:, 0]) < 0.015) & (Vs[:, 1] > yc_s)
    crotch_z = float(Vs[mid, 2].min()) if mid.any() else top_leg - 0.03  # the back seam meets the legs here
    seat = inS & (Ps[:, 1] > yc_s) & (Vs[:, 2] > crotch_z + 0.01) & (Vs[:, 2] < hip_z + 0.02)
    if seat.any():
        sidx = np.where(seat)[0]
        thS = np.arctan2(Ps[sidx, 1] - yc_s, Ps[sidx, 0]); rS = np.hypot(Ps[sidx, 0], Ps[sidx, 1] - yc_s)
        NQ = 72
        qi = ((thS + math.pi) / (2 * math.pi) * NQ).astype(int) % NQ
        zi = ((Vs[sidx, 2] - crotch_z) / 0.02).astype(int)
        newr = rS.copy()
        for zz in np.unique(zi):
            m_ = zi == zz
            mx = np.full(NQ, -1.0)
            np.maximum.at(mx, qi[m_], rS[m_])
            filt = np.max([np.roll(mx, d) for d in range(-4, 5)], axis=0)
            newr[m_] = np.minimum(np.maximum(rS[m_], filt[qi[m_]] - 0.004), rS[m_] + 0.03)  # at most 3 cm of fill
        wS = np.clip((hip_z + 0.02 - Vs[sidx, 2]) / 0.05, 0, 1)
        newr = rS + (newr - rS) * wS
        Ps[sidx, 0] = np.cos(thS) * newr; Ps[sidx, 1] = yc_s + np.sin(thS) * newr
        S_EASE[sidx] += newr - rS
        print('garment v3 seat bridge: crotch z', round(crotch_z, 3), 'hip z', round(hip_z, 3), 'max fill (cm)', round(float((newr - rS).max() * 100), 2))
    print('garment v3 shorts: leg ease (m) min/med/max', round(float(S_EASE[inS].min()), 3), round(float(np.median(S_EASE[inS])), 3), round(float(S_EASE[inS].max()), 3))
sflat = lambda q: hem_s if q[:, 2].max() < hip_z - 0.1 else None
if ISO:
    Ps = smooth_loops(Ps, spoly, 4, flat=sflat)
else:
    Ps, son = smooth_boundary(Ps, spoly, 22, 8, flat=sflat)
if GV3:
    Ps = taubin_garment(Ps, spoly, Vs, Ns, iters=24, min_off=0.007)
    Ps = fourier_loops(Ps, spoly, 10, flat=sflat)
z0s, z1s = hem_s, hip_z + 0.12
suv = cyl_uvs(Ps, spoly, z0s, z1s)
shm = [0] * len(spoly)
if GV32:
    # V3.2 (owner review of V3.1 at 3.75 s: a triangular point on the shorts): (1) the hips -> thigh weight change of the
    # leg tubes and the crotch is spread over ~8 rings (smooth_field) instead of 1-2; (2) the leg-opening cloth field
    # _E2A_HEM is smoothed and capped at 0.45 (the runtime also gives the shorts their own small, thigh-relative swing)
    _sv = np.unique(np.concatenate([np.asarray(f_) for f_ in spoly]))
    _ms = np.zeros(len(Ps), bool); _ms[_sv] = True
    _w0 = Wsh.copy()
    Wsh = smooth_field(Wsh, spoly, _ms & (Vs[:, 2] < hip_z - 0.04), iters=28, lam=0.5, renorm=True)
    S_HEM = np.clip(smooth_field(S_HEM, spoly, _ms, iters=12, lam=0.5), 0, None) * 0.5
    print('garment v32 shorts: weights smoothed, max change', round(float(np.abs(Wsh - _w0)[_sv].max()), 3), 'hem max', round(float(S_HEM[_sv].max()), 3))
ob_shorts, sused = make_mesh('E2A_Shorts', Ps, spoly, [M_SHORTS, M_TRIM], shm, suv, Wsh)
if GV3:
    # leg openings swing with the engine cloth2 spring (same attributes as the jersey: _E2A_HEM free-ness, _E2A_EASE gap)
    for nm, arr in (('_E2A_HEM', S_HEM), ('_E2A_EASE', S_EASE)):
        at = ob_shorts.data.attributes.new(nm, 'FLOAT', 'POINT')
        for vi_new, vi_old in enumerate(sused):
            at.data[vi_new].value = float(arr[vi_old])
if CORR and any(m_.get('mode') == 'flex' for _n, _d, m_ in CORR):
    # hip correctives on the shorts: the skin's fix, gated off at the waistband (stays with its trim) and the leg hem
    sg_ = np.clip((hip_z - 0.01 - Vs[:, 2]) / 0.05, 0, 1) * np.clip((Vs[:, 2] - hem_s - 0.03) / 0.06, 0, 1)
    sg_ = sg_ * sg_ * (3 - 2 * sg_)
    ob_shorts.shape_key_add(name='Basis', from_mix=False)
    for nm, _dl, m_ in CORR:
        kb = ob_shorts.shape_key_add(name=nm, from_mix=False)
        if m_.get('mode') != 'flex':
            continue  # knee / elbow keys: present (same names on every mesh), zero delta
        ds = transfer_corrective(m_['bone'], Wsh, GEXTRA[id(G_shorts)], sg_)
        if GV32:
            # V3.2: hip flexion folds on the FRONT of that leg tube (3 soft creases +-5 mm, 6-20 cm below the waist)
            _sd = 1.0 if nm.endswith('.L') else -1.0
            _Ns = vnormals(Ps, spoly)
            _fr = np.clip(-(Ps[:, 1] - 0.0) / 0.06, 0, 1) * (np.sign(Ps[:, 0]) == _sd)
            _bd = np.clip((Ps[:, 2] - (hip_z - 0.24)) / 0.05, 0, 1) * np.clip(((hip_z - 0.05) - Ps[:, 2]) / 0.05, 0, 1)
            ds = ds + _Ns * (0.005 * np.sin(2 * math.pi * (Ps[:, 2] - hip_z) / 0.05) * _fr * _bd)[:, None]
        for vi_new, vi_old in enumerate(sused):
            kb.data[vi_new].co = (Ps[vi_old] + ds[vi_old]).tolist()
        print(f'shorts {nm}: max fix {np.linalg.norm(ds, axis=1).max() * 100:.2f} cm')
ob_spipe = pipe_loops('E2A_ShortsTrim', Ps, spoly, Wsh, 0.006, keep=lambda q: q[:, 2].min() > hip_z)

if GV2:
    # ---- Realism V2: the jersey stays OUTSIDE the shorts waistband (>= 1.4 cm radially over the nearest shorts vertex)
    if GV3:  # smooth fabric first, so the waistband clearance below is enforced on the final surface
        Pj = taubin_garment(Pj, jpoly, Vj, Nj, iters=30, min_off=0.008)
    from mathutils import kdtree as _kd
    kd_s = _kd.KDTree(len(Ps))
    for i_, p_ in enumerate(Ps):
        kd_s.insert(p_.tolist(), i_)
    kd_s.balance()
    low = np.where(inj & (Pj[:, 2] < hip_z + 0.16))[0]
    for i_ in low:
        co, k_, dd = kd_s.find(Pj[i_].tolist())
        rs = math.hypot(Ps[k_][0], Ps[k_][1] - J_YC)
        rj = math.hypot(Pj[i_][0], Pj[i_][1] - J_YC)
        if rj < rs + 0.014:
            sc = (rs + 0.014) / max(rj, 1e-6)
            Pj[i_, 0] *= sc; Pj[i_, 1] = J_YC + (Pj[i_, 1] - J_YC) * sc
            J_EASE[i_] += rs + 0.014 - rj
    # the hem does not follow the thighs (a shirt hangs from the shoulders): thigh weights -> hips under the waist
    Wj = Wj.copy()
    for sd in 'LR':
        ti = SK.NAMES.index('thigh.' + sd)
        # 45 % of the thigh weight stays: a high knee still pushes the front hem out (the shorts must not poke
        # through the longer hem; qc-realism cloth_clip, 2026-11-21)
        uu = np.clip((hip_z + 0.08 - Pj[:, 2]) / 0.08, 0, 1) * 0.55
        mv = Wj[:, ti] * uu
        Wj[:, ti] -= mv
        Wj[:, SK.NAMES.index('hips')] += mv
    if GV31:
        # V3.1 (coordinator review 2026-11-22): the deep armhole edge carried MakeHuman upper-arm weights, so a raised arm
        # lifted the strap off the shoulder like a hard shell. A jersey hangs from the shoulder girdle: 85 % of every
        # upperarm weight goes to the clavicle, and 40 % of the clavicle weight below the strap to the chest
        for sd in 'LR':
            ua, cl_, ch_ = SK.NAMES.index('upperarm.' + sd), SK.NAMES.index('clavicle.' + sd), SK.NAMES.index('chest')
            mv = Wj[:, ua] * 0.85
            Wj[:, ua] -= mv
            Wj[:, cl_] += mv
            low_ = np.clip((AH_Z + 0.02 - Pj[:, 2]) / 0.08, 0, 1) * 0.4
            mv = Wj[:, cl_] * low_
            Wj[:, cl_] -= mv
            Wj[:, ch_] += mv
    if GV32:
        # V3.2: the strap / armhole carries chest -> clavicle -> upperarm weights; with the change over one ring the strap
        # stretched 3.4x and lifted off as a shell (qc_cloth_v32 on V3.1, 3.33 s). Spread over the top 14 cm
        _jv = np.unique(np.concatenate([np.asarray(f_) for f_ in jpoly]))
        _mj = np.zeros(len(Pj), bool); _mj[_jv] = True
        _w0 = Wj.copy()
        Wj = smooth_field(Wj, jpoly, _mj & (Pj[:, 2] > AH_Z - 0.14), iters=30, lam=0.5, renorm=True)
        # and the spine -> chest band of the torso (the V3.1 chest counter-rotation of 0.55 rad at the 3.3 s plant stretched
        # its 1 cm edges 2.6x): 40 passes over the whole trunk part above the waistband
        Wj = smooth_field(Wj, jpoly, _mj, iters=150, lam=0.5, renorm=True)
        print('garment v32 jersey: strap weights smoothed, max change', round(float(np.abs(Wj - _w0)[_jv].max()), 3))
    Pj = smooth_loops(Pj, jpoly, 4, flat=jflat)
    if GV3:
        Pj = fourier_loops(Pj, jpoly, 12, flat=jflat)
    juv = cyl_uvs(Pj, jpoly, z0j, z1j)
    ob_jersey, jused = make_mesh('E2A_Jersey', Pj, jpoly, [M_JERSEY, M_TRIM], jmat, juv, Wj)
    # V3: no gold ring on the jersey hem (read as a hard hoop): piping on the neck and armholes only
    JKEYS = {}
    if GV32:
        # ---- V3.2 garment correctives (pose-space shape keys, driven at runtime by the joint angles, rig correctives):
        #   trunk       forward trunk flexion (chest vs hips, key 45 deg): 3 soft horizontal folds on the front belly band
        #               (+-6 mm along the normal) and the front panel shortened 1 cm (fabric bunches instead of stretching)
        #   shoulder.L/R arm raise (upperarm vs chest, key 90 deg): the strap / armhole edge on that side pulled 1 cm onto
        #               the shoulder and 6 mm down (in V3.1 a raised arm lifted it off like a shell)
        Nj_ = vnormals(Pj, jpoly)
        zz = Pj[:, 2]
        front = np.clip(-(Pj[:, 1] - J_YC) / 0.08, 0, 1)
        band = np.clip((zz - (hip_z + 0.04)) / 0.05, 0, 1) * np.clip((chest_z + 0.02 - zz) / 0.06, 0, 1)
        z0 = hip_z + 0.04
        fold = 0.006 * np.sin(2 * math.pi * (zz - z0) / 0.055)
        dT = Nj_ * (fold * front * band)[:, None]
        dT[:, 2] += -0.010 * front * np.clip((zz - z0) / max(1e-6, chest_z - z0), 0, 1) * np.clip((chest_z + 0.1 - zz) / 0.1, 0, 1)
        JKEYS['trunk'] = dT
        for sd, sg in (('L', 1.0), ('R', -1.0)):
            near = np.clip(1 - np.hypot(np.abs(Pj[:, 0]) - AH_X * 0.85, (zz - (AH_Z + 0.06)) * 1.2) / 0.12, 0, 1) * (np.sign(Pj[:, 0]) == sg)
            near = near * near * (3 - 2 * near)
            dS = -Nj_ * (0.010 * near)[:, None]
            dS[:, 2] += -0.006 * near
            JKEYS[f'shoulder.{sd}'] = dS
        ob_jersey.shape_key_add(name='Basis', from_mix=False)
        for nm, dl in JKEYS.items():
            kb = ob_jersey.shape_key_add(name=nm, from_mix=False)
            for vi_new, vi_old in enumerate(jused):
                kb.data[vi_new].co = (Pj[vi_old] + dl[vi_old]).tolist()
            print(f'jersey corrective {nm}: max {np.linalg.norm(dl[jused], axis=1).max() * 100:.2f} cm')
        JCORR.extend([('trunk', None, {'bone': 'chest', 'parent': 'hips', 'key': 45, 'mode': 'flexUp'}),
                      ('shoulder.L', None, {'bone': 'upperarm.L', 'parent': 'chest', 'key': 90, 'mode': 'raise'}),
                      ('shoulder.R', None, {'bone': 'upperarm.R', 'parent': 'chest', 'key': 90, 'mode': 'raise'})])
    ob_jpipe = pipe_loops('E2A_JerseyTrim', Pj, jpoly, Wj, 0.0062, **({'keep': lambda q: q[:, 2].min() > hip_z + 0.12} if GV3 else {}), keys=JKEYS or None)
    # per-vertex data for the engine secondary motion (src/t3d/cloth2.ts): _E2A_HEM 0 above the chest line -> 1 at the
    # hem (how free the cloth is), _E2A_EASE = horizontal gap to the body (m, how far the hem may swing inward)
    hem_w = np.clip((chest_z - 0.04 - Pj[:, 2]) / (chest_z - 0.04 - hem_j), 0, 1) ** 1.6
    if GV32:  # V3.2: no single hem vertex freer than its ring (side "spikes" at 5.3-5.8 s in V3.1)
        hem_w = np.clip(smooth_field(hem_w, jpoly, np.unique(np.concatenate([np.asarray(f_) for f_ in jpoly])), iters=10, lam=0.5), 0, 1)
    me_ = ob_jersey.data
    for nm, arr in (('_E2A_HEM', hem_w), ('_E2A_EASE', np.maximum(0.0, J_EASE))):
        at = me_.attributes.new(nm, 'FLOAT', 'POINT')
        for vi_new, vi_old in enumerate(jused):
            at.data[vi_new].value = float(arr[vi_old])
    print('garment v2: jersey ease (m) min/med/max', round(float(J_EASE[inj].min()), 3), round(float(np.median(J_EASE[inj])), 3), round(float(J_EASE[inj].max()), 3),
          'hem', round(hem_j, 3))

# shoes: per foot, convex hull of the inflated foot + ankle (a smooth sneaker last, no toes), sole flat on the floor,
# weights from the nearest body vertex
import bmesh
from mathutils import kdtree
Pf = V.copy() + NRM * 0.010
shoe_obs = []
sv_all = np.unique(F[shoe_f])
for s_, sg in (('L', 1), ('R', -1)):
    ids = sv_all[np.sign(V[sv_all, 0]) == sg]
    bm = bmesh.new()
    for p_ in Pf[ids]:
        bm.verts.new(p_.tolist())
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    kd = kdtree.KDTree(len(ids))
    for k_, i_ in enumerate(ids):
        kd.insert(V[i_].tolist(), k_)
    kd.balance()
    for vv in bm.verts:
        if vv.co.z < 0.03:
            vv.co.z = max(0.0, (vv.co.z - 0.03) * 0.1)
    me = bpy.data.meshes.new('E2A_Shoe.' + s_)
    bm.to_mesh(me); bm.free()
    me.materials.append(M_SHOE); me.materials.append(M_SOLE)
    for poly in me.polygons:
        cz = sum(me.vertices[v].co.z for v in poly.vertices) / len(poly.vertices)
        poly.material_index = (1 if cz < 0.03 else 0) if a.shoe == 'v1' else 0
        poly.use_smooth = True
    if a.shoe in ('v31', 'v32'):
        # ---- Realism V3.1 sole: the V3 shoe was a convex hull of the foot ("a sock with a dark bottom"). A SEPARATE slab
        # under it: outline = 2-D hull of the upper's lower 6 cm + 5 mm (the wall shows round the upper), heel 3.2 cm -> forefoot 1.8 cm, toe spring (the
        # front 22 % lifts 1.3 cm off the floor), heel bevel 6 mm, a 3 mm outward bulge at mid height (cupsole wall)
        fp = np.array([[v.co.x, v.co.y] for v in me.vertices if v.co.z < 0.06])  # widest part of the upper's lower 6 cm
        o_ = np.lexsort((fp[:, 1], fp[:, 0])); fp = fp[o_]
        def _half(pts):
            h_ = []
            for q in pts:
                while len(h_) >= 2 and ((h_[-1][0] - h_[-2][0]) * (q[1] - h_[-2][1]) - (h_[-1][1] - h_[-2][1]) * (q[0] - h_[-2][0])) <= 0:
                    h_.pop()
                h_.append(q)
            return h_
        hull = np.array(_half(fp)[:-1] + _half(fp[::-1])[:-1])
        seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.vstack([hull, hull[:1]]), axis=0), axis=1))]
        NS = 72
        ss = np.linspace(0, seg[-1], NS, endpoint=False)
        ring = np.stack([np.interp(ss, seg, np.r_[hull[:, k], hull[0, k]]) for k in (0, 1)], 1)
        for _ in range(3):  # round the hull corners
            ring = 0.5 * ring + 0.25 * (np.roll(ring, 1, 0) + np.roll(ring, -1, 0))
        cen = ring.mean(0)
        tang = np.roll(ring, -1, 0) - np.roll(ring, 1, 0)
        nrm2 = np.stack([tang[:, 1], -tang[:, 0]], 1); nrm2 /= np.linalg.norm(nrm2, axis=1, keepdims=True)
        nrm2 *= np.sign(((ring - cen) * nrm2).sum(1))[:, None]
        yh, yt = ring[:, 1].max(), ring[:, 1].min()
        uu = (yh - ring[:, 1]) / (yh - yt)  # 0 heel -> 1 toe (the body faces -y)
        smo = lambda x: np.clip(x, 0, 1) ** 2 * (3 - 2 * np.clip(x, 0, 1))
        bot = 0.013 * smo((uu - 0.78) / 0.22) + 0.006 * smo((0.06 - uu) / 0.06)
        topz = 0.032 - 0.014 * smo(uu / 0.75) + 0.004 * smo((uu - 0.8) / 0.2)
        layers = [(bot, 0.004), (bot + 0.004, 0.006), (bot + 0.45 * (topz - bot), 0.008), (topz, 0.005)]
        sv, sf = [], []
        for zl, offl in layers:
            for k_ in range(NS):
                xy = ring[k_] + nrm2[k_] * offl
                sv.append([xy[0], xy[1], zl[k_]])
        for li in range(len(layers) - 1):
            for k_ in range(NS):
                a0, a1 = li * NS + k_, li * NS + (k_ + 1) % NS
                sf.append([a0, a1, a1 + NS, a0 + NS])
        cb = len(sv); sv.append([cen[0], cen[1], float(bot.mean() * 0.3)])
        ct = len(sv); sv.append([cen[0], cen[1], float(topz.mean())])
        for k_ in range(NS):
            sf.append([cb, (k_ + 1) % NS, k_])
            tb = (len(layers) - 1) * NS
            sf.append([ct, tb + k_, tb + (k_ + 1) % NS])
        mes = bpy.data.meshes.new('E2A_Sole.' + s_)
        mes.from_pydata([tuple(v) for v in sv], [], [tuple(f) for f in sf])
        mes.materials.append(M_SOLE)
        for poly in mes.polygons:
            poly.use_smooth = len(poly.vertices) == 4
        obs_ = bpy.data.objects.new('E2A_Sole.' + s_, mes)
        bpy.context.collection.objects.link(obs_)
        vgs_ = {bn: obs_.vertex_groups.new(name=bn) for bn in SK.NAMES}
        for vv in mes.vertices:
            co, k_, dist = kd.find(vv.co)
            src = ids[k_]
            for bi, bn in enumerate(SK.NAMES):
                if WGT[src, bi] > 1e-4:
                    vgs_[bn].add([vv.index], float(WGT[src, bi]), 'REPLACE')
        shoe_obs.append(obs_)
        if a.shoe == 'v32':
            # ---- Realism V3.2 upper: a MODELED LAST lofted on the sole outline instead of the convex hull of the foot
            # ("slipper" in the V3.1 review). Heel counter (near-vertical back wall), padded collar with a dark lining
            # and an open ankle (the sock goes in), a rounded toe box lower than the instep, a vamp that closes over
            # the foot; every height is kept >= the foot inside (+5 mm) so no hidden body face can show
            footv = np.where(freg[np.arange(len(F))] == 9)[0]
            fv = np.unique(F[footv]); fv = fv[np.sign(V[fv, 0]) == sg]
            hv = np.array([[v.co.x, v.co.y, v.co.z] for v in me.vertices])
            NB = 24
            def _topin(P_, u_):
                b_ = np.clip((u_ * NB).astype(int), 0, NB - 1)
                out = np.zeros(NB)
                np.maximum.at(out, b_, P_[:, 2])
                for _ in range(2):
                    out = np.maximum(out, np.maximum(np.r_[out[1:], 0], np.r_[0, out[:-1]]))
                return out
            hullTop = _topin(hv, np.clip((yh - hv[:, 1]) / (yh - yt), 0, 1))
            fv = fv[V[fv, 2] < 0.112]  # the ankle above the throat passes through the opening
            footTop = _topin(V[fv], np.clip((yh - V[fv, 1]) / (yh - yt), 0, 1))
            ub = lambda u_: np.clip((u_ * NB).astype(int), 0, NB - 1)
            closed = smo((uu - 0.36) / 0.14)  # 0 = collar region (open), 1 = vamp / toe box (closed over the foot)
            # mid-top basketball profile: heel counter / collar 12.5 cm, throat 11.5, instep, low rounded toe box
            Hprof = np.interp(uu, [0.0, 0.05, 0.2, 0.34, 0.45, 0.6, 0.8, 0.95, 1.0], [0.128, 0.126, 0.12, 0.114, 0.104, 0.088, 0.066, 0.05, 0.042])
            # closed part: over every foot vertex (+5 mm); collar: over the hidden foot faces (FOOT_SHOW_Z) + 1.2 cm
            Hmin = np.where(closed > 0.5, footTop[ub(uu)] + 0.005, FOOT_SHOW_Z + 0.012)
            Htop = np.maximum(Hprof, Hmin)
            for _ in range(12):  # smooth along the outline (no dents from the per-bin foot heights)
                Htop = np.maximum(Htop, 0.5 * Htop + 0.25 * (np.roll(Htop, 1) + np.roll(Htop, -1))) if _ < 2 else 0.5 * Htop + 0.25 * (np.roll(Htop, 1) + np.roll(Htop, -1))
            Htop = np.maximum(Htop, Hmin - 0.002)
            # the collar wraps the ANKLE: top ring = 2-D hull of the leg at collar height + 1.3 cm, reached along rays
            # from the ankle centre (the heel counter / collar is a shaft around the leg, not a slipper rim)
            legv = np.where((V[:, 2] > 0.095) & (V[:, 2] < 0.14) & (np.sign(V[:, 0]) == sg))[0]
            lp = V[legv][:, :2]
            lc = 0.5 * (lp.min(0) + lp.max(0))
            ax_ = 0.5 * (lp.max(0) - lp.min(0)) + 0.014  # ellipse round the leg, 1.4 cm clearance (smooth collar edge)
            def ankle_pt(xy_):
                th = math.atan2((xy_[1] - lc[1]) / ax_[1], (xy_[0] - lc[0]) / ax_[0])
                return lc + ax_ * np.array([math.cos(th), math.sin(th)])
            z0 = topz - 0.004
            ring_u = ring + nrm2 * 0.002
            NJ = 10
            levels = [math.sin(0.5 * math.pi * j / (NJ - 1)) for j in range(NJ)]
            uv, uf, umat = [], [], []
            cx = cen[0]
            heelc = (uu < 0.2)
            for j, vj in enumerate(levels):
                dome = 1 - math.sqrt(max(0.0, 1 - vj ** 2))
                for k_ in range(NS):
                    c_ = np.array([cx, ring_u[k_, 1]])
                    xyd = c_ + (ring_u[k_] - c_) * (1 - dome)
                    toe_ = smo((uu[k_] - 0.86) / 0.14)
                    xyd = xyd + np.array([0.0, 0.035 * toe_ * dome])  # toe box rounds back over the toes (+y = back)
                    a_ = ankle_pt(ring_u[k_])
                    wv = float(smo((vj - 0.25) / 0.75))
                    xyc = ring_u[k_] + (a_ - ring_u[k_]) * wv
                    xy = xyc + (xyd - xyc) * closed[k_]
                    uv.append([xy[0], xy[1], z0[k_] + vj * (Htop[k_] - z0[k_])])
            # padded collar roll: one more level, 7 mm inward and 9 mm down (closed region: a duplicate, merged below)
            for k_ in range(NS):
                top_ = np.array(uv[(NJ - 1) * NS + k_])
                d_ = np.array([lc[0] - top_[0], lc[1] - top_[1], 0.0]); n_ = np.linalg.norm(d_)
                lip = float(1 - smo(closed[k_] / 0.5))
                uv.append((top_ + d_ / max(n_, 1e-6) * 0.006 * lip + np.array([0, 0, -0.01 * lip])).tolist())
            for j in range(NJ):
                for k_ in range(NS):
                    a0, a1 = j * NS + k_, j * NS + (k_ + 1) % NS
                    uf.append([a0, a1, a1 + NS, a0 + NS])
                    # dark lining on the collar roll, dark heel counter cap (a sneaker cue, not a slipper)
                    # + lace panel over the instep (top 2 levels, u 0.4-0.66) and a mid-height side stripe (u 0.22-0.7)
                    lace = j >= NJ - 2 and 0.4 < uu[k_] < 0.66 and closed[k_] > 0.5
                    stripe = j == 3 and 0.22 < uu[k_] < 0.7
                    umat.append(1 if (j == NJ - 1 and closed[k_] < 0.5) or (uu[k_] < 0.12 and j >= NJ // 2) or lace or stripe else 0)
            bm = bmesh.new()
            for p_ in uv:
                bm.verts.new(p_)
            bm.verts.ensure_lookup_table()
            for f_, m_ in zip(uf, umat):
                try:
                    fc = bm.faces.new([bm.verts[i_] for i_ in f_])
                    fc.material_index = m_
                except ValueError:
                    pass
            bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0015)
            # close the vamp seam: the left / right top edges meet on the centre line at slightly different y
            topv = [v_ for v_ in bm.verts if abs(v_.co.x - cx) < 0.002 and v_.co.z > 0.03]
            bmesh.ops.remove_doubles(bm, verts=topv, dist=0.006)
            bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-5)
            bm.normal_update()
            me.clear_geometry()
            bm.to_mesh(me); bm.free()
            for poly in me.polygons:
                poly.use_smooth = True
            print(f'upper v32 {s_}: {len(me.vertices)} verts, heel collar {100 * Htop[uu < 0.04].mean():.1f} cm, instep {100 * Htop[(uu > 0.4) & (uu < 0.5)].mean():.1f} cm, toe box {100 * Htop[(uu > 0.75) & (uu < 0.85)].mean():.1f} cm')
        print(f'sole v31 {s_}: {len(sv)} verts, length {100 * (yh - yt):.1f} cm, heel {100 * topz[uu < 0.05].mean():.1f} cm, toe {100 * topz[uu > 0.9].mean():.1f} cm, toe spring {100 * bot.max():.1f} cm')
    ob = bpy.data.objects.new('E2A_Shoe.' + s_, me)
    bpy.context.collection.objects.link(ob)
    vgs = {bn: ob.vertex_groups.new(name=bn) for bn in SK.NAMES}
    for vv in me.vertices:
        co, k_, dist = kd.find(vv.co)
        src = ids[k_]
        for bi, bn in enumerate(SK.NAMES):
            if WGT[src, bi] > 1e-4:
                vgs[bn].add([vv.index], float(WGT[src, bi]), 'REPLACE')
    shoe_obs.append(ob)
    if a.shoe == 'v32':
        # V3.2: foot / toe split of upper AND sole at the ball joint (3 cm blend), so the shoe bends at the ball when the
        # heel rises (motion32 keeps the toe bone flat on the floor) instead of the whole shoe tilting like a slipper
        yb = J[f'toe3-1.{s_}____head'][1]
        fi, ti = SK.NAMES.index('foot.' + s_), SK.NAMES.index('toe.' + s_)
        for ob_ in (ob, *[o for o in shoe_obs if o.name.startswith('E2A_Sole.' + s_)]):
            gF, gT = ob_.vertex_groups['foot.' + s_], ob_.vertex_groups['toe.' + s_]
            for vv in ob_.data.vertices:
                ws_ = {g.group: g.weight for g in vv.groups}
                ft = ws_.get(gF.index, 0.0) + ws_.get(gT.index, 0.0)
                if ft < 1e-4:
                    continue
                wt = float(smo((yb + 0.012 - vv.co.y) / 0.03))
                gF.add([vv.index], ft * (1 - wt), 'REPLACE')
                gT.add([vv.index], ft * wt, 'REPLACE')
ob_shoes = shoe_obs[0]

# hair: short shell, volume on top (5440: curly on top, short sides and nape)
Ph = V.copy()
top = np.clip((V[:, 2] - 2.0) / 0.1, 0, 1)
if VAR['hair_style'] == 'buzz':
    Ph += NRM * (0.004 + 0.003 * top)[:, None]  # buzz cut: a thin even shell
else:
    Ph += NRM * (0.006 + 0.016 * top)[:, None]
Ph, _ = smooth_boundary(Ph, [F[i] for i in hair_f], 16, 6)
ob_hair, _ = make_mesh('E2A_Hair', Ph, [F[i] for i in hair_f], [M_HAIR], [0] * len(hair_f), None, WGT)

# ---------------------------------------------------------------- armature
arm = bpy.data.armatures.new('E2A_Rig')
ob_arm = bpy.data.objects.new('E2A_Rig', arm)
bpy.context.collection.objects.link(ob_arm)
bpy.context.view_layer.objects.active = ob_arm
bpy.ops.object.mode_set(mode='EDIT')
for name, parent, h, t, roll in SK.BONES:
    r = sk['rest'][name]
    eb = arm.edit_bones.new(name)
    eb.head = r['head'].tolist()
    eb.tail = r['tail'].tolist()
    eb.align_roll(mathutils.Vector(r['R'][:, 2].tolist()))
    if parent:
        eb.parent = arm.edit_bones[parent]
        eb.use_connect = False
bpy.ops.object.mode_set(mode='OBJECT')
# check the rest matrices against skeleton.py
err = 0
for name in SK.NAMES:
    m = np.array(arm.bones[name].matrix_local)[:3, :3]
    err = max(err, np.abs(m - sk['rest'][name]['R']).max())
print('rest matrix max diff vs skeleton.py', err)
for ob in [o for o in (ob_body, ob_jersey, ob_jpipe, ob_shorts, ob_spipe, *shoe_obs, ob_hair) if o is not None]:
    ob.parent = ob_arm
    md = ob.modifiers.new('Armature', 'ARMATURE')
    md.object = ob_arm
    md.use_deform_preserve_volume = True  # Blender viewport; glTF / three.js use linear skinning

# ---------------------------------------------------------------- actions from motion.json (head-calibrated)
rest = sk['rest']


def q2m(q):
    x, y, z, w = q
    return np.array(mathutils.Quaternion((w, x, y, z)).to_matrix())


def key_action(act_name, Mo):
    """key one motion.json as an action of the rig (world rotations -> local, hips location)"""
    n = len(Mo['t'])
    act = bpy.data.actions.new(act_name)
    act.use_fake_user = True
    ob_arm.animation_data.action = act
    root = np.array(Mo['root'])
    Rw = {b: np.array([q2m(q) for q in Mo['q'][b]]) for b in SK.NAMES}
    for i in range(n):
        for name in SK.NAMES:
            pb = ob_arm.pose.bones[name]
            par = rest[name]['parent']
            if par is None:
                Bm = rest[name]['R'].T @ Rw[name][i]
                loc = rest[name]['R'].T @ (root[i] - rest[name]['head'])
                pb.location = loc.tolist()
                pb.keyframe_insert('location', frame=i + 1)
            else:
                Bm = rest[name]['R'].T @ rest[par]['R'] @ Rw[par][i].T @ Rw[name][i]
            q = mathutils.Matrix(Bm.tolist()).to_quaternion()
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = q
            pb.keyframe_insert('rotation_quaternion', frame=i + 1)
    return act


ob_arm.animation_data_create()
# E2A_rest: one key of the rest pose (engine-driven players start from here)
act_rest = bpy.data.actions.new('E2A_rest'); act_rest.use_fake_user = True
ob_arm.animation_data.action = act_rest
for name in SK.NAMES:
    pb = ob_arm.pose.bones[name]; pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = (1, 0, 0, 0); pb.keyframe_insert('rotation_quaternion', frame=1)
    if rest[name]['parent'] is None:
        pb.location = (0, 0, 0); pb.keyframe_insert('location', frame=1)
tr = ob_arm.animation_data.nla_tracks.new(); tr.name = 'E2A_rest'; tr.strips.new('E2A_rest', 1, act_rest); tr.mute = True
fps = 30000 / 1001
n = 1
Mo = None
acts = [x.split('=', 1) for x in a.action]
for k_, (nm, pth) in enumerate(acts[::-1]):  # the first --action stays the active one
    Mx = json.load(open(pth))
    ex = key_action(nm, Mx)
    print('action', nm, len(Mx['t']), 'frames', Mx.get('head_fix', {}))
    if k_ < len(acts) - 1:
        tr = ob_arm.animation_data.nla_tracks.new(); tr.name = nm; tr.strips.new(nm, 1, ex); tr.mute = True
    else:
        Mo = Mx; n = len(Mx['t'])
scn.frame_start = 1
scn.frame_end = n
if Mo is not None:
    scn.frame_set(int(n * 0.6))
    pbx = ob_arm.pose.bones['shin.L']
    pos = np.array(ob_arm.matrix_world @ pbx.head)
    want = np.array(Mo['joints']['kneeL'][int(n * 0.6) - 1])
    print('FK check knee.L blender vs motion.json (m):', np.linalg.norm(pos - want))
    t0 = Mo['t'][0]

# ---------------------------------------------------------------- engine rig descriptor (src/t3d/players/*.rig.json)
if a.out_rig:
    from retarget import rot_to_quat
    lm = sk['lm']
    rj = {'pelvis': rest['hips']['head'], 'chest': rest['neck']['head'], 'head': rest['head']['head'] + np.array([0, -0.06, 0.07])}
    for s_ in 'LR':
        rj.update({'hip' + s_: rest['thigh.' + s_]['head'], 'knee' + s_: rest['shin.' + s_]['head'], 'ankle' + s_: rest['foot.' + s_]['head'],
                   'toe' + s_: rest['toe.' + s_]['tail'], 'shoulder' + s_: rest['upperarm.' + s_]['head'], 'elbow' + s_: rest['forearm.' + s_]['head'],
                   'wrist' + s_: rest['hand.' + s_]['head'], 'hand' + s_: lm['handtip' + s_],
                   'ball' + s_: np.array([lm['ball' + s_][0], lm['ball' + s_][1], 0.0]), 'heel' + s_: np.array([lm['heel' + s_][0], lm['heel' + s_][1], 0.0])})
    hv = np.where(np.isin(np.arange(len(V)), np.unique(np.concatenate([F[i] for i in body_f]))))[0]
    rig = {'version': ('e2a-player-v32' if GV32 else 'e2a-player-v31' if GV31 else 'e2a-player-v3') if RV3 else 'e2a-player-v1', 'variant': a.variant, 'H': round(float(sk['V'][:mh_body.NBODY, 2].max()), 4),
           'source': 'MakeHuman base mesh (ara3d-data 1.1.0, CC0-1.0) morphed by tools/blender/mh_body.py + build_player.py',
           'kit': {k: VAR[k] for k in ('jersey', 'trim', 'number', 'shoe', 'sole', 'sock', 'hair', 'skin')},
           'bones': [{'name': b, 'parent': rest[b]['parent'], 'head': np.round(rest[b]['head'], 5).tolist(), 'tail': np.round(rest[b]['tail'], 5).tolist(),
                      'R': rot_to_quat(rest[b]['R']).round(6).tolist()} for b in SK.NAMES],
           'restJoints': {k: np.round(np.asarray(v, float), 5).tolist() for k, v in rj.items()}}
    if RV3:
        # finger rest geometry for the engine grip solver (src/t3d/realism-v3/hands.ts): knuckle K, middle joint M, tip T of
        # the middle finger, thumb base / tip, and the CURL axes (rotating +angle about them closes the hand toward the palm)
        fing = {}
        for s_ in 'LR':
            g_ = lambda k: np.asarray(J[k.replace('#', s_)], float)
            K_, M_, T_ = g_('finger3-1.#____head'), g_('finger3-2.#____head'), g_('finger3-3.#____tail')
            TB, TT, W_ = g_('finger1-2.#____head'), g_('finger1-3.#____tail'), g_('wrist.#____head')
            seg = (M_ - K_) / np.linalg.norm(M_ - K_)
            pn = (T_ - M_) - seg * ((T_ - M_) @ seg)  # rest curl of the MakeHuman hand: the tip bends toward the palm
            if np.linalg.norm(pn) < 1e-4 or pn @ (TT - K_) < 0:
                pn = (TT - K_) - seg * ((TT - K_) @ seg)
            pn /= np.linalg.norm(pn)
            ax = np.cross(seg, pn); ax /= np.linalg.norm(ax)
            tseg = (TT - TB) / np.linalg.norm(TT - TB)
            tax = np.cross(tseg, pn); tax /= np.linalg.norm(tax)
            palm = (W_ + K_) / 2 + pn * 0.012
            fing[s_] = {k: np.round(v, 5).tolist() for k, v in (('K', K_), ('M', M_), ('T', T_), ('TB', TB), ('TT', TT), ('W', W_), ('palm', palm),
                                                               ('axis', ax), ('thumbAxis', tax), ('palmN', pn))}
        rig['fingers'] = fing
        rig['correctives'] = [{'name': nm, **m_} for nm, _d, m_ in CORR + JCORR]
    os.makedirs(os.path.dirname(os.path.abspath(a.out_rig)), exist_ok=True)
    json.dump(rig, open(a.out_rig, 'w'), separators=(',', ':'))
    print('rig', a.out_rig, rig['H'])

# ---------------------------------------------------------------- reference camera (solved video camera)
S = json.load(open(a.solved)) if a.solved else None
if S is not None and Mo is not None:
    Mf = np.array(S['floor_M']); cf = np.array(S['floor_c']); sc = Mo['scale_mp_to_m']
    cam_pos = ((np.zeros(3) - cf) @ Mf.T) * sc
    # camera axes in the floor frame: camera x right, y down, z forward (OpenCV) -> Blender camera looks down -Z, +Y up
    xc = Mf[:, 0]; yc = Mf[:, 1]; zc = Mf[:, 2]  # columns: camera axes expressed in floor coords
    Rb = np.stack([xc, -yc, -zc], 1)
    camd = bpy.data.cameras.new('REF_5452_cam')
    camd.sensor_fit = 'HORIZONTAL'
    camd.sensor_width = 36.0
    camd.lens = S['focal_px'] / 1920 * 36.0
    ob_cam = bpy.data.objects.new('REF_5452_cam', camd)
    bpy.context.collection.objects.link(ob_cam)
    M4 = mathutils.Matrix.Identity(4)
    for r_ in range(3):
        for c_ in range(3):
            M4[r_][c_] = Rb[r_, c_]
        M4[r_][3] = cam_pos[r_]
    ob_cam.matrix_world = M4
    scn.camera = ob_cam
    scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
    if a.ref_video and os.path.exists(a.ref_video):
        clip = bpy.data.movieclips.load(a.ref_video)
        camd.show_background_images = True
        bg = camd.background_images.new()
        bg.source = 'MOVIE_CLIP'
        bg.clip = clip
        bg.alpha = 0.6
        bg.frame_method = 'FIT'
        # clip frame 1 = video frame round(t0*fps)+1
        bg.clip_user.frame_current = 1
        clip.frame_offset = int(round(t0 * fps))
        print('reference movie clip', a.ref_video, 'offset', clip.frame_offset)
# floor
bpy.ops.mesh.primitive_plane_add(size=12, location=(0.5, 0, 0))
bpy.context.object.name = 'REF_floor'
txt = bpy.data.texts.new('E2A_README')
txt.write(('E2A player (%s variant, %s). Armature E2A_Rig: %d deforming bones, metres, z up, rest faces -y.\n'
           'Actions: E2A_rest + %s (head-calibrated motions, fix_head.py). REF_5452_cam = solved camera of 5452 when present.\n'
           'Rebuild: tools/blender/build_player.py (see template/tactical/reports/3d-animation-mpfb-2026-11-19/INFORME.md).\n')
          % (a.variant, 'e2a-player-v3' if RV3 else 'e2a-player-v1', len(SK.NAMES), ', '.join(x.split('=')[0] for x in a.action)))
os.makedirs(os.path.dirname(os.path.abspath(a.out_blend)), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.out_blend), relative_remap=True)
print('saved', a.out_blend)
# ---------------------------------------------------------------- glb (mesh + skeleton + clip)
for o in list(bpy.data.objects):
    o.select_set(o.name.startswith('E2A_'))
bpy.ops.export_scene.gltf(filepath=os.path.abspath(a.out_glb), export_format='GLB', use_selection=True, export_animations=True,
                          export_skins=True, export_yup=True, export_apply=False, export_texcoords=True, export_normals=True,
                          export_materials='EXPORT', export_image_format='AUTO', export_def_bones=False, export_frame_range=True,
                          **({'export_attributes': True} if GV2 else {}))
print('glb', a.out_glb, os.path.getsize(a.out_glb))
if a.out_meta:
    meta = {'glb': os.path.basename(a.out_glb), 'bytes': os.path.getsize(a.out_glb), 'args': {k: v for k, v in vars(a).items() if not k.startswith('out')},
            'bones': SK.NAMES, 'meshes': [], 'materials': sorted({m.name for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('E2A_') for m in o.data.materials}),
            'animations': [ac.name for ac in bpy.data.actions]}
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name.startswith('E2A_'):
            o.data.calc_loop_triangles()
            meta['meshes'].append({'name': o.name, 'verts': len(o.data.vertices), 'tris': len(o.data.loop_triangles),
                                   'morphs': [k.name for k in o.data.shape_keys.key_blocks[1:]] if o.data.shape_keys else []})
    meta['tris'] = sum(m['tris'] for m in meta['meshes'])
    json.dump(meta, open(a.out_meta, 'w'), indent=1)
    print('meta', a.out_meta, meta['tris'], 'tris')
