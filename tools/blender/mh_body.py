"""E2A 3D lab — E2A screener body from the MakeHuman base mesh (ara3d-data, CC0-1.0), numpy only.

Macro morph (young male, athletic, tall, ideal proportions) + local targets oriented by the owner's references
5438/5440 (head ≈ 0.125–0.133 H; deltoid width / head width ≈ 2.6–3.0; see tactical/reports/3d-animation-2026-11-18).
Output in play / Blender coordinates: metres, z up, the body faces -y, soles on z = 0.
"""
import os
import numpy as np
import mh_pack as M

ASSETS = os.environ.get('E2A_MH_ASSETS', '/tmp/claude-0/lab3/assets_ara/package/assets')

MACRO = {
    # universal young male: 45 % muscle towards max, average weight (athletic but not a bodybuilder)
    'macrodetails/universal-male-young-averagemuscle-averageweight': 0.55,
    'macrodetails/universal-male-young-maxmuscle-averageweight': 0.45,
    'macrodetails/caucasian-male-young': 0.8,
    'macrodetails/african-male-young': 0.1,
    'macrodetails/asian-male-young': 0.1,
    'macrodetails/height/male-young-averagemuscle-averageweight-maxheight': 0.75,
    'macrodetails/proportions/male-young-averagemuscle-averageweight-idealproportions': 0.8,
}
LOCAL = {
    # long-limbed basketball build, shoulders a bit wider than the default, narrow waist
    'torso/torso-vshape-incr': 0.35,
    'torso/torso-muscle-dorsi-incr': 0.25,
    'torso/torso-scale-horiz-incr': 0.25,
    'hip/hip-scale-horiz-decr': 0.35,
    'hip/hip-scale-depth-decr': 0.2,
    'stomach/stomach-tone-incr': 0.4,
    'armslegs/l-upperarm-muscle-incr': 0.3, 'armslegs/r-upperarm-muscle-incr': 0.3,
    'armslegs/l-lowerleg-muscle-incr': 0.25, 'armslegs/r-lowerleg-muscle-incr': 0.25,
    'armslegs/l-upperleg-muscle-incr': 0.2, 'armslegs/r-upperleg-muscle-incr': 0.2,
    'neck/neck-scale-horiz-incr': 0.25,
    # head 0.123 H -> ~0.128 H (5438 front: 0.133 incl. hair volume)
    'head/head-scale-vert-incr': 0.35,
    'head/head-scale-horiz-incr': 0.3,
    'head/head-scale-depth-incr': 0.25,
}
H_BODY = 2.08  # barefoot; the shoe sole adds ~2 cm -> 2.10 m (PLAYER_HEIGHTS.O5)
NBODY = 13380  # vertices used by the body faces (the rest are MakeHuman helpers)


def mh_to_play(P):
    return np.stack([P[:, 0], -P[:, 2], P[:, 1]], 1)


def build(extra=None):
    B = M.base(os.path.join(ASSETS, 'base.pack'))
    T = M.Targets(os.path.join(ASSETS, 'targets.pack'))
    P = B['P'].copy()
    n = len(P)
    for name, w in {**MACRO, **LOCAL, **(extra or {})}.items():
        if name in T.meta['targets'] and w:
            P += w * T.delta(name, n)
        elif w:
            print('missing target', name)
    J = M.joints(B['meta'], P)                 # MakeHuman joints (head/tail of every bone), same units
    P = curl_fingers(P, B, J)
    used = np.unique(B['F'])
    Q = mh_to_play(P)
    zmin = Q[used, 2].min()
    hgt = Q[used, 2].max() - zmin
    s = H_BODY / hgt
    org = np.array([0, 0, zmin])
    Q = (Q - org) * s
    Jp = {k: ((mh_to_play(v[None])[0] - org) * s) for k, v in J.items()}
    return {'B': B, 'P_mh': P, 'V': Q, 'J': Jp, 'scale': s, 'origin': org, 'used': used}


def curl_fingers(P, B, J, curl=(28, 34, 22), thumb=(10, 12, 8)):
    """bake a relaxed, slightly closed hand into the rest mesh (linear blend with the MakeHuman finger weights):
    open MakeHuman hands read as 'spread' at game distance; a soft curl reads as a basketball hand."""
    names = [b['name'] for b in B['meta']['bones']]
    P = P.copy()
    n = len(P)
    W = np.zeros((n, len(names)))
    for i in range(n):
        bi, bv = B['W'][i]
        W[i, bi] = bv
    out = P.copy()
    for s in 'LR':
        mid = J[f'finger3-1.{s}____tail'] - J[f'finger3-1.{s}____head']
        across = J[f'finger2-1.{s}____head'] - J[f'finger5-1.{s}____head']
        thumb_base = J[f'finger1-1.{s}____head']
        for f in range(1, 6):
            chain = [f'finger{f}-{k}.{s}' for k in (1, 2, 3)]
            angs = thumb if f == 1 else curl
            T = np.eye(4)
            for k, bn in enumerate(chain):
                h = J[bn + '____head']; t = J[bn + '____tail']
                d = (t - h) / np.linalg.norm(t - h)
                ax = np.cross(d, across); ax /= np.linalg.norm(ax)
                best = None
                for sg in (1, -1):
                    R = _axis_angle(ax * sg, np.radians(angs[k]))
                    tip = h + R @ (t - h)
                    dd = np.linalg.norm(tip - thumb_base) if f > 1 else np.linalg.norm(tip - J[f'finger3-1.{s}____head'])
                    if best is None or dd < best[0]:
                        best = (dd, R)
                R = best[1]
                Tk = np.eye(4); Tk[:3, :3] = R; Tk[:3, 3] = h - R @ h
                Hh = T @ np.append(h, 1)
                T = T @ Tk
                bi = names.index(bn)
                w = W[:, bi]
                m = w > 0
                if m.any():
                    Ph = np.c_[P[m], np.ones(m.sum())]
                    out[m] += w[m, None] * ((Ph @ T.T)[:, :3] - P[m])
    return out


def _axis_angle(ax, ang):
    x, y, z = ax
    c, s_ = np.cos(ang), np.sin(ang)
    C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s_, x * z * C + y * s_], [y * x * C + z * s_, c + y * y * C, y * z * C - x * s_],
                     [z * x * C - y * s_, z * y * C + x * s_, c + z * z * C]])


def proportions(body):
    V, J, B = body['V'], body['J'], body['B']
    r = B['regions']
    head = np.where(r[:NBODY] == 0)[0]
    H = H_BODY
    chin = V[head, 2].min()
    top = V[head, 2].max()
    ear_z = (J['head____head'][2] + top) / 2
    band = head[np.abs(V[head, 2] - ear_z) < 0.03]
    head_w = np.ptp(V[band, 0])
    # deltoid width: outermost upper-arm / shoulder vertices from the acromion down to 6 cm below the shoulder joint
    zs = J['upperarm01.L____head'][2]
    sh = np.where(np.isin(r[:NBODY], [2, 4]))[0]
    dl = sh[(V[sh, 2] > zs - 0.06) & (V[sh, 2] < zs + 0.06)]
    del_w = 2 * np.abs(V[dl, 0]).max()
    return {'H': H, 'head_h': top - chin, 'head_ratio': (top - chin) / H, 'head_w': head_w, 'deltoid_w': del_w,
            'deltoid_over_head': del_w / head_w, 'shoulder_z_ratio': zs / H}


if __name__ == '__main__':
    b = build()
    print({k: round(float(v), 3) for k, v in proportions(b).items()})
