"""E2A 3D lab — MediaPipe (floor frame, pose_solve.py) -> E2A game skeleton (skeleton.py): bone rotations, root,
foot contacts and pins, hand-made corrections. numpy only; bpy keys the result (build_blender.py).

  python -I tools/blender/retarget.py solved.json --config tools/blender/clip_5452.json --out motion.json

Method
  * bone frames from two vectors (primary = bone direction from the landmarks, secondary = hinge / side axis),
    calibrated on the SAME landmark semantics measured on the rest skeleton: R(t) = F(t) F_rest^T R_rest
    (so a bone never inherits the offset between a MediaPipe point and the real joint);
  * hinge axes of knees / elbows fall back to the parent frame when the limb is straight (no roll flips);
  * root: least squares (PnP root, smoothness, and every planted foot point fixed on the floor);
  * pins: the contact point of each stance (ball / mid / heel, from the config, read frame by frame on the video)
    stays fixed; during the pivot only the yaw (about the ball) and the heel lift change; two-bone IK on the leg;
  * quaternions: hemisphere continuity + light smoothing; angular speed report per bone.
"""
import argparse, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skeleton as SK

MP = {'nose': 0, 'earL': 7, 'earR': 8, 'shoulderL': 11, 'shoulderR': 12, 'elbowL': 13, 'elbowR': 14, 'wristL': 15,
      'wristR': 16, 'pinkyL': 17, 'pinkyR': 18, 'indexL': 19, 'indexR': 20, 'hipL': 23, 'hipR': 24, 'kneeL': 25,
      'kneeR': 26, 'ankleL': 27, 'ankleR': 28, 'heelL': 29, 'heelR': 30, 'toeL': 31, 'toeR': 32}


def nrm(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-9)


def two_vec(p, s):
    p = nrm(p)
    s = nrm(s - p * (s * p).sum(-1, keepdims=True))
    return np.stack([p, s, np.cross(p, s)], -1)  # columns


def rot_to_quat(R):
    """(..., 3, 3) -> (..., 4) x y z w"""
    R = np.asarray(R)
    q = np.zeros(R.shape[:-2] + (4,))
    tr = R[..., 0, 0] + R[..., 1, 1] + R[..., 2, 2]
    for idx in np.ndindex(R.shape[:-2]):
        m = R[idx]
        t = tr[idx]
        if t > 0:
            S = np.sqrt(t + 1.0) * 2
            q[idx] = [(m[2, 1] - m[1, 2]) / S, (m[0, 2] - m[2, 0]) / S, (m[1, 0] - m[0, 1]) / S, 0.25 * S]
        elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
            S = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
            q[idx] = [0.25 * S, (m[0, 1] + m[1, 0]) / S, (m[0, 2] + m[2, 0]) / S, (m[2, 1] - m[1, 2]) / S]
        elif m[1, 1] > m[2, 2]:
            S = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
            q[idx] = [(m[0, 1] + m[1, 0]) / S, 0.25 * S, (m[1, 2] + m[2, 1]) / S, (m[0, 2] - m[2, 0]) / S]
        else:
            S = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
            q[idx] = [(m[0, 2] + m[2, 0]) / S, (m[1, 2] + m[2, 1]) / S, 0.25 * S, (m[1, 0] - m[0, 1]) / S]
    return q / np.linalg.norm(q, axis=-1, keepdims=True)


def quat_to_rot(q):
    x, y, z, w = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    R = np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w),
                  2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w),
                  2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)], -1)
    return R.reshape(q.shape[:-1] + (3, 3))


def slerp_R(A, B, u):
    qa, qb = rot_to_quat(A), rot_to_quat(B)
    d = (qa * qb).sum(-1, keepdims=True)
    qb = np.where(d < 0, -qb, qb)
    q = nrm(qa * (1 - u) + qb * u)
    return quat_to_rot(q)


def axis_angle(axis, ang):
    axis = nrm(axis)
    x, y, z = axis[..., 0], axis[..., 1], axis[..., 2]
    c, s = np.cos(ang), np.sin(ang)
    C = 1 - c
    R = np.stack([c + x * x * C, x * y * C - z * s, x * z * C + y * s,
                  y * x * C + z * s, c + y * y * C, y * z * C - x * s,
                  z * x * C - y * s, z * y * C + x * s, c + z * z * C], -1)
    return R.reshape(np.shape(ang) + (3, 3))


def Rz(a):
    return axis_angle(np.broadcast_to([0, 0, 1.0], np.shape(a) + (3,)), a)


def swing(a, b):
    """minimal rotation taking direction a to b"""
    a, b = nrm(a), nrm(b)
    ax = np.cross(a, b)
    s = np.linalg.norm(ax, axis=-1)
    c = (a * b).sum(-1)
    ang = np.arctan2(s, c)
    ax = np.where(s[..., None] > 1e-9, ax, np.array([1.0, 0, 0]))
    return axis_angle(ax, ang)


def smooth(x, passes=1, taps=(1, 4, 6, 4, 1)):
    k = np.array(taps, float)
    k /= k.sum()
    h = len(k) // 2
    for _ in range(passes):
        xp = np.concatenate([x[:1].repeat(h, 0), x, x[-1:].repeat(h, 0)])
        x = sum(k[i] * xp[i:i + len(x)] for i in range(len(k)))
    return x


def yaw_of(v):
    return np.arctan2(v[..., 1], v[..., 0])


def frames_for(D, rest_R=None, fallback=None):
    """bone frames from a landmark dict D (arrays (..., 3)). fallback: dict bone -> secondary vector in parent frame."""
    F = {}
    side = D['hipL'] - D['hipR']
    midH = (D['hipL'] + D['hipR']) / 2
    midS = (D['shoulderL'] + D['shoulderR']) / 2
    up = midS - midH
    F['hips'] = two_vec(up, side)
    F['chest'] = two_vec(up, D['shoulderL'] - D['shoulderR'])
    hs = D['earL'] - D['earR']
    hf = D['nose'] - (D['earL'] + D['earR']) / 2
    F['head'] = two_vec(np.cross(hf, hs), hs)
    hinge = {}
    for s in 'LR':
        F['clavicle.' + s] = two_vec(D['shoulder' + s] - midS, up)
        for limb, a, b, c, par in (('arm', 'shoulder', 'elbow', 'wrist', 'chest'), ('leg', 'hip', 'knee', 'ankle', 'hips')):
            p = D[b + s] - D[a + s]
            q = D[c + s] - D[b + s]
            n = np.cross(p, q)
            ln = np.linalg.norm(n, axis=-1, keepdims=True)
            w = np.clip(ln / (np.linalg.norm(p, axis=-1, keepdims=True) * np.linalg.norm(q, axis=-1, keepdims=True) * np.sin(np.radians(25))), 0, 1)
            if fallback is not None:
                fb = np.einsum('...ij,j->...i', F[par], fallback[limb + s])
                n = nrm(nrm(n) * w + fb * (1 - w))
            hinge[limb + s] = nrm(n)
        F['upperarm.' + s] = two_vec(D['elbow' + s] - D['shoulder' + s], hinge['arm' + s])
        F['forearm.' + s] = two_vec(D['wrist' + s] - D['elbow' + s], hinge['arm' + s])
        kn = (D['index' + s] + D['pinky' + s]) / 2
        F['hand.' + s] = two_vec(kn - D['wrist' + s], D['index' + s] - D['pinky' + s])
        F['thigh.' + s] = two_vec(D['knee' + s] - D['hip' + s], hinge['leg' + s])
        F['shin.' + s] = two_vec(D['ankle' + s] - D['knee' + s], hinge['leg' + s])
        F['foot.' + s] = two_vec(D['toe' + s] - D['heel' + s], D['ankle' + s] - D['heel' + s])
        F['toe.' + s] = F['foot.' + s]
    return F, hinge


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('solved')
    ap.add_argument('--config', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    S = json.load(open(a.solved))
    T = np.array(S['t'])
    sel = (T >= cfg['t0'] - 1e-6) & (T <= cfg['t1'] + 1e-6)
    T = T[sel]
    n = len(T)
    Lraw = np.array(S['local_raw'])[sel]
    Lm = np.array(S['local'])[sel]
    root_pnp = np.array(S['root'])[sel]
    # extra smoothing: hands are the noisiest landmarks, then feet
    Ls = Lm.copy()
    for j in (15, 16, 17, 18, 19, 20, 21, 22):
        Ls[:, j] = smooth(Lm[:, j], 2)
    for j in (27, 28, 29, 30, 31, 32, 0, 7, 8):
        Ls[:, j] = smooth(Lm[:, j], 1)
    sk = SK.build()
    rest = sk['rest']
    lm = sk['lm']
    D = {k: Ls[:, i] for k, i in MP.items()}
    # scale MediaPipe units -> skeleton metres from the legs
    mp_leg = np.median(np.linalg.norm(D['kneeL'] - D['hipL'], axis=-1) + np.linalg.norm(D['ankleL'] - D['kneeL'], axis=-1))
    sc = (rest['thigh.L']['len'] + rest['shin.L']['len']) / mp_leg
    # rest frames + hinge fallbacks expressed in the parent frame
    Drest = {k: np.asarray(lm[k]) for k in MP}
    Frest, hrest = frames_for(Drest)
    fallback = {}
    for s in 'LR':
        fallback['arm' + s] = Frest['chest'].T @ hrest['arm' + s]
        fallback['leg' + s] = Frest['hips'].T @ hrest['leg' + s]
    Frest, _ = frames_for(Drest, fallback=fallback)
    F, hinge = frames_for(D, fallback=fallback)
    R = {}
    for b in SK.NAMES:
        if b in F:
            R[b] = np.einsum('nij,kj,kl->nil', F[b], Frest[b], rest[b]['R'])
    R['spine'] = slerp_R(R['hips'], R['chest'], 0.5)
    R['neck'] = slerp_R(R['chest'], R['head'], 0.5)
    # chest, spine, neck, head: the hips->chest frame gives the trunk; spine/neck are halfway rotations
    corrections = []

    # ---------- FK
    def fk(Rd, root):
        P = {}
        for name, parent, *_ in SK.BONES:
            if parent is None:
                P[name] = root.copy()
            else:
                off = rest[name]['head'] - rest[parent]['head']
                loc = rest[parent]['R'].T @ off
                P[name] = P[parent] + np.einsum('nij,j->ni', Rd[parent], loc)
        tails = {}
        for name in SK.NAMES:
            tails[name] = P[name] + np.einsum('nij,j->ni', Rd[name], np.array([0, rest[name]['len'], 0]))
        return P, tails

    def foot_point(Rd, P, s, which):
        """world position of a sole point (rest landmark, z on the floor) carried by the foot bone"""
        loc = rest['foot.' + s]['R'].T @ (np.array(which) - rest['foot.' + s]['head'])
        return P['foot.' + s] + np.einsum('nij,j->ni', Rd['foot.' + s], loc)

    sole = {}
    for s in 'LR':
        ball = lm['ball' + s].copy(); ball[2] = 0.0
        heel = lm['heel' + s].copy(); heel[2] = 0.0
        sole['ball' + s] = ball
        sole['heel' + s] = heel
        sole['mid' + s] = (ball + heel) / 2
    root0 = root_pnp * sc
    P0, _ = fk(R, root0)
    # ---------- contacts (from the config, read on the video frame by frame)
    C = cfg['contacts']
    fi = lambda t: int(np.clip(np.searchsorted(T, t - 1e-6), 0, n - 1))
    for c in C:
        c['i0'], c['i1'] = fi(c['t0']), fi(c['t1'])
    # ---------- root least squares
    K = len(C)
    nu = 3 * n + 3 * K
    rows, rhs = [], []
    def eq(coefs, b):
        r = np.zeros(nu)
        for j, v in coefs:
            r[j] += v
        rows.append(r); rhs.append(b)
    wd = np.array(cfg.get('w_data', [1.0, 0.6, 0.3]))
    trust = np.ones(n)
    for a0, a1, w in cfg.get('trust_pnp', []):
        trust[(T >= a0) & (T <= a1)] = w
    for i in range(n):
        for ax in range(3):
            w = wd[ax] * (trust[i] if ax < 2 else 1.0)
            eq([(3 * i + ax, w)], w * root0[i, ax])
    ws = cfg.get('w_smooth', 4.0)
    for i in range(1, n - 1):
        for ax in range(3):
            eq([(3 * (i - 1) + ax, ws), (3 * i + ax, -2 * ws), (3 * (i + 1) + ax, ws)], 0.0)
    wc = cfg.get('w_contact', 4.0)
    root0s = smooth(root0, 3)
    for k, c in enumerate(C):
        s = c['foot']
        if c.get('anchor') == 'root':
            # back to the camera the MediaPipe legs have no usable depth: the stance foot is placed under the
            # (PnP) root at mid-stance, offset sideways; the root is not pulled by this contact (ESTIMATED)
            im = (c['i0'] + c['i1']) // 2
            v = root0s[min(n - 1, im + 2), :2] - root0s[max(0, im - 2), :2]
            v = v / max(1e-6, np.linalg.norm(v))
            left = np.array([-v[1], v[0]])
            lat = c.get('lateral', 0.11) * (1 if s == 'L' else -1)
            xy = root0s[im, :2] + left * lat + v * c.get('forward', 0.0)
            eq([(3 * n + 3 * k + 0, 30.0)], 30.0 * xy[0]); eq([(3 * n + 3 * k + 1, 30.0)], 30.0 * xy[1])
            eq([(3 * n + 3 * k + 2, 30.0)], 0.0)
            continue
        pt = foot_point(R, P0, s, sole[c.get('point', 'ball') + s]) - root0  # offset from the root
        for i in range(c['i0'], c['i1'] + 1):
            for ax in range(3):
                eq([(3 * i + ax, wc), (3 * n + 3 * k + ax, -wc)], -wc * pt[i, ax])
        eq([(3 * n + 3 * k + 2, 30.0)], 0.0)  # anchors on the floor
    A = np.array(rows)
    bvec = np.array(rhs)
    sol = np.linalg.lstsq(A, bvec, rcond=None)[0]
    root = sol[:3 * n].reshape(n, 3)
    anchors = sol[3 * n:].reshape(K, 3)
    anchors[:, 2] = 0.0
    # ---------- pins: foot orientation + IK
    Rp = {k: v.copy() for k, v in R.items()}
    foot_yaw = {}
    for s in 'LR':
        fwd = D['toe' + s] - D['heel' + s]
        foot_yaw[s] = np.unwrap(yaw_of(fwd))
    rest_yaw = {s: float(yaw_of(lm['toe' + s] - lm['heel' + s])) for s in 'LR'}
    lat = np.array([1.0, 0, 0])
    target_foot = {s: [None] * n for s in 'LR'}
    weight_pin = {s: np.zeros(n) for s in 'LR'}
    for k, c in enumerate(C):
        s = c['foot']
        i0, i1 = c['i0'], c['i1']
        yaw = foot_yaw[s][i0:i1 + 1]
        pitch_src = (D['heel' + s][:, 2] - D['toe' + s][:, 2])[i0:i1 + 1] * sc
        pitch = np.arcsin(np.clip(pitch_src / np.linalg.norm(lm['toe' + s] - lm['heel' + s]), -1, 1))
        if c.get('pivot'):
            # pivot on the ball: the yaw follows the video (smoothed, monotonic over the turn), heel lift from the video
            p0, p1 = fi(c['pivot'][0]), fi(c['pivot'][1])
            yv = smooth(yaw, 3)
            y0 = np.mean(yv[:max(1, p0 - i0)])
            y1 = yv[min(len(yv) - 1, p1 - i0)] if c.get('yaw_end') is None else np.radians(c['yaw_end'])
            u = np.clip((np.arange(i0, i1 + 1) - p0) / max(1, p1 - p0), 0, 1)
            u = u * u * (3 - 2 * u)
            yaw = y0 + (y1 - y0) * u
            corrections.append(f"{s} pivot {c['pivot'][0]:.2f}-{c['pivot'][1]:.2f}s: ball fixed, yaw {np.degrees(y0):.0f}->{np.degrees(y1):.0f} deg (smoothstep), heel lift from video")
        else:
            yaw = np.full_like(yaw, np.mean(yaw))
        hl = c.get('heel_lift')  # [t, deg] keys: hand-set heel lift (push-off) where the video is ambiguous
        if c.get('point', 'ball') != 'ball' and not c.get('pivot'):
            pitch = np.zeros_like(pitch)
        pitch = np.clip(smooth(pitch, 2), 0, np.radians(45))
        if hl:
            tk = np.array([h[0] for h in hl]); vk = np.radians([h[1] for h in hl])
            pitch = np.interp(T[i0:i1 + 1], tk, vk)
            corrections.append(f"{s} {c['t0']:.2f}-{c['t1']:.2f}s heel lift keyed by hand {hl}")
        pt_name = c.get('point', 'ball')
        for j, i in enumerate(range(i0, i1 + 1)):
            Rf = Rz(yaw[j] - rest_yaw[s]) @ axis_angle(lat, pitch[j]) @ rest['foot.' + s]['R']
            target_foot[s][i] = (Rf, anchors[k], pt_name)
            weight_pin[s][i] = 1.0
    # soften entry/exit of the pins over 3 frames (blend the foot from the swing into the pin)
    BL = cfg.get('pin_blend_frames', 3)
    for s in 'LR':
        w = weight_pin[s]
        for i in range(n):
            if w[i] == 1.0:
                continue
            d = min([abs(i - j) for j in range(n) if weight_pin[s][j] == 1.0] or [99])
            w[i] = max(0.0, 1 - d / (BL + 1)) if d <= BL else 0.0
    # IK passes (lower the root where a pinned foot is out of reach)
    L1, L2 = rest['thigh.L']['len'], rest['shin.L']['len']
    reach_fix = np.zeros(n)
    for it in range(3):
        rootc = root.copy()
        rootc[:, 2] -= np.minimum(smooth(reach_fix[:, None], 2)[:, 0], cfg.get('max_root_drop', 0.06))
        P, _ = fk(R, rootc)
        need = np.zeros(n)
        short = {s_: np.zeros(n) for s_ in 'LR'}
        out = {k: v.copy() for k, v in R.items()}
        for s in 'LR':
            hip = P['thigh.' + s]
            for i in range(n):
                tf = target_foot[s][i]
                w = weight_pin[s][i]
                if tf is None:
                    # nearest pin for the blend zone
                    near = [j for j in range(max(0, i - BL), min(n, i + BL + 1)) if target_foot[s][j] is not None]
                    if not near or w <= 0:
                        continue
                    j = min(near, key=lambda j: abs(j - i))
                    tf = target_foot[s][j]
                Rf, anc, pt_name = tf
                loc = rest['foot.' + s]['R'].T @ (sole[pt_name + s] - rest['foot.' + s]['head'])
                ankle_pin = anc - Rf @ loc
                ankle_fk = P['foot.' + s][i]
                ankle_t = ankle_fk * (1 - w) + ankle_pin * w
                Rfoot = slerp_R(R['foot.' + s][i], Rf, w)
                d = np.linalg.norm(ankle_t - hip[i])
                if d > (L1 + L2) * 0.997:
                    need[i] = max(need[i], d - (L1 + L2) * 0.997)
                    short[s][i] = d - (L1 + L2) * 0.9995
                # two-bone IK, pole = the knee from the video
                knee_fk = P['shin.' + s][i]
                dd = min(d, (L1 + L2) * 0.9995)
                ca = np.clip((L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd), -1, 1)
                ax = nrm(ankle_t - hip[i])
                pole = knee_fk - hip[i]
                pole = nrm(pole - ax * (pole @ ax))
                knee = hip[i] + ax * L1 * ca + pole * L1 * np.sqrt(1 - ca * ca)
                ankle = knee + nrm(ankle_t - knee) * L2
                Rt = swing(P['shin.' + s][i] - hip[i], knee - hip[i]) @ R['thigh.' + s][i]
                # shin: rotate the shin (as carried by the new thigh) onto knee->ankle
                Rs0 = Rt @ R['thigh.' + s][i].T @ R['shin.' + s][i]
                cur = Rs0 @ np.array([0, 1.0, 0])
                Rs = swing(cur, ankle - knee) @ Rs0
                out['thigh.' + s][i] = Rt
                out['shin.' + s][i] = Rs
                out['foot.' + s][i] = Rfoot
                out['toe.' + s][i] = Rfoot @ rest['foot.' + s]['R'].T @ rest['toe.' + s]['R']
        Rp = out
        if need.max() < 1e-3:
            break
        reach_fix += need * 1.05
    root = rootc
    if reach_fix.max() > 0:
        corrections.append(f'root lowered where a pinned foot was out of reach: max {min(reach_fix.max(), cfg.get("max_root_drop", 0.06))*1000:.0f} mm')
    # frames still out of reach: the foot leaves the floor there (earlier toe-off / later touch-down, ESTIMATED)
    eff = {}
    for s_ in 'LR':
        for i in range(n):
            if weight_pin[s_][i] == 1.0 and short[s_][i] > 0.004:
                weight_pin[s_][i] = 0.999  # counted as swing in the stance QC
        eff[s_] = weight_pin[s_] == 1.0
    lost = {s_: int(((short[s_] > 0.004)).sum()) for s_ in 'LR'}
    if sum(lost.values()):
        corrections.append(f'pinned frames out of leg reach turned into early toe-off / late touch-down: {lost}')
    # toes: never below the floor (bend the toe up when the heel lifts)
    P, tails = fk(Rp, root)
    for s in 'LR':
        for i in range(n):
            tip = tails['toe.' + s][i]
            if tip[2] < 0.012:
                base = P['toe.' + s][i]
                v = tip - base
                want = v.copy(); want[2] = 0.012 - base[2]
                hz = np.sqrt(max(1e-6, (v @ v) - want[2] ** 2))
                hv = nrm(v[:2]) * hz
                want = np.array([hv[0], hv[1], want[2]])
                Rp['toe.' + s][i] = swing(v, want) @ Rp['toe.' + s][i]
    # ---------- hands during the screen (observed 5449-5452: one hand over the other at the groin) -> arm IK
    hc = cfg.get('hands_clasp')
    if hc:
        P, tails = fk(Rp, root)
        ta, tb, bl = hc['from'], hc['to'], hc.get('blend', 0.15)
        wv = np.clip((T - ta) / bl, 0, 1) * np.clip((tb - T) / bl, 0, 1)
        wv = wv * wv * (3 - 2 * wv)
        side_ax = nrm(P['thigh.L'] - P['thigh.R'])
        upv = np.broadcast_to([0, 0, 1.0], (n, 3))
        fwd_ax = nrm(np.cross(side_ax, upv))
        La, Lb = rest['upperarm.L']['len'], rest['forearm.L']['len']
        for s_, lat in (('L', hc.get('lateral', 0.03)), ('R', -hc.get('lateral', 0.03))):
            tgt = P['hips'] + fwd_ax * hc.get('forward', 0.16) + upv * hc.get('up', -0.14) + side_ax * lat
            for i in range(n):
                if wv[i] <= 0:
                    continue
                sh = P['upperarm.' + s_][i]; el = P['forearm.' + s_][i]; wr = P['hand.' + s_][i]
                want = wr * (1 - wv[i]) + tgt[i] * wv[i]
                d = min(np.linalg.norm(want - sh), (La + Lb) * 0.999)
                ax = nrm(want - sh)
                ca = np.clip((La * La + d * d - Lb * Lb) / (2 * La * d), -1, 1)
                pole = el - sh + side_ax[i] * (0.08 if s_ == 'L' else -0.08)  # elbows a little open (observed)
                pole = nrm(pole - ax * (pole @ ax))
                el2 = sh + ax * La * ca + pole * La * np.sqrt(1 - ca * ca)
                wr2 = el2 + nrm(sh + ax * d - el2) * Lb
                Ru = swing(el - sh, el2 - sh) @ Rp['upperarm.' + s_][i]
                Rf0 = Ru @ Rp['upperarm.' + s_][i].T @ Rp['forearm.' + s_][i]
                Rf = swing(Rf0 @ np.array([0, 1.0, 0]), wr2 - el2) @ Rf0
                Rh = Rf @ Rp['forearm.' + s_][i].T @ Rp['hand.' + s_][i]
                Rp['upperarm.' + s_][i], Rp['forearm.' + s_][i], Rp['hand.' + s_][i] = Ru, Rf, Rh
        corrections.append(f"hands clasped at the groin during the screen {ta:.2f}-{tb:.2f}s (arm IK, blend {bl}s; MediaPipe hands are noisy there)")
    # ---------- hand-made corrections from the config (keyed offsets, documented)
    for corr in cfg.get('corrections', []):
        b = corr['bone']
        tk = np.array([k[0] for k in corr['keys']])
        ang = np.radians(np.array([k[1] for k in corr['keys']]))
        u = np.interp(T, tk, ang, left=0, right=0)
        ax = np.array(corr['axis'], float)
        if corr.get('space', 'world') == 'world':
            Rp[b] = axis_angle(np.broadcast_to(ax, (n, 3)), u) @ Rp[b]
        else:
            Rp[b] = Rp[b] @ rest[b]['R'].T @ axis_angle(np.broadcast_to(ax, (n, 3)), u) @ rest[b]['R']
        corrections.append(f"{b}: {corr['why']} (keys {corr['keys']})")
    # ---------- quaternion continuity + smoothing
    Q = {}
    speed = {}
    for b in SK.NAMES:
        q = rot_to_quat(Rp[b])
        for i in range(1, n):
            if (q[i] * q[i - 1]).sum() < 0:
                q[i] = -q[i]
        if b.startswith(('foot', 'toe', 'thigh', 'shin')):
            qs = q  # legs are already constrained by the pins (smoothing would re-introduce sliding)
        else:
            qs = nrm(smooth(q, 1))
        Q[b] = qs
        dots = np.clip(np.abs((qs[1:] * qs[:-1]).sum(-1)), 0, 1)
        speed[b] = float(np.degrees(2 * np.arccos(dots)).max() * 29.97)
        Rp[b] = quat_to_rot(qs)
    P, tails = fk(Rp, root)
    # ---------- pose-space joints for the engine (Pose layout) + checks
    def hand_tip(s):
        loc = rest['hand.' + s]['R'].T @ (lm['handtip' + s] - rest['hand.' + s]['head'])
        return P['hand.' + s] + np.einsum('nij,j->ni', Rp['hand.' + s], loc)
    def head_c():
        loc = rest['head']['R'].T @ (np.array([0, -0.06, rest['head']['head'][2] + 0.07]) - rest['head']['head'])
        return P['head'] + np.einsum('nij,j->ni', Rp['head'], loc)
    joints = {'pelvis': P['hips'], 'chest': P['neck'], 'head': head_c()}
    for s in 'LR':
        joints['hip' + s] = P['thigh.' + s]; joints['knee' + s] = P['shin.' + s]; joints['ankle' + s] = P['foot.' + s]
        joints['toe' + s] = tails['toe.' + s]; joints['shoulder' + s] = P['upperarm.' + s]
        joints['elbow' + s] = P['forearm.' + s]; joints['wrist' + s] = P['hand.' + s]; joints['hand' + s] = hand_tip(s)
        joints['ball' + s] = foot_point(Rp, P, s, sole['ball' + s])
        joints['heel' + s] = foot_point(Rp, P, s, sole['heel' + s])
    heading = np.unwrap(yaw_of(np.cross(joints['hipL'] - joints['hipR'], np.broadcast_to([0, 0, 1.0], (n, 3)))))
    chest_side = joints['shoulderL'] - joints['shoulderR']
    chestYaw = np.unwrap(yaw_of(np.cross(chest_side, np.broadcast_to([0, 0, 1.0], (n, 3)))))
    headv = D['nose'] - (D['earL'] + D['earR']) / 2
    headYaw = np.unwrap(yaw_of(smooth(headv, 2)))
    # contact QC inside the clip: accumulated drift of the pinned point during each stance
    qc = []
    for k, c in enumerate(C):
        s = c['foot']; pt = joints[c.get('point', 'ball') + s] if c.get('point', 'ball') != 'mid' else (joints['ball' + s] + joints['heel' + s]) / 2
        ii = [i for i in range(c['i0'], c['i1'] + 1) if eff[s][i]]
        if not ii:
            continue
        seg = pt[ii]
        qc.append({'foot': s, 't0': c['t0'], 't1': c['t1'], 'eff': [float(T[ii[0]]), float(T[ii[-1]])], 'point': c.get('point', 'ball'),
                   'drift_mm': round(float(np.linalg.norm(seg - seg[0], axis=-1).max() * 1000), 2), 'height_mm': round(float(np.abs(seg[:, 2]).max() * 1000), 2)})
        c['eff'] = [float(T[ii[0]]), float(T[ii[-1]])]
    out = {
        'source': os.path.basename(cfg.get('video', '')), 'fps': 30000 / 1001, 't': T.round(4).tolist(), 'scale_mp_to_m': float(sc),
        'bones': [{'name': b, 'parent': rest[b]['parent'], 'head': rest[b]['head'].round(5).tolist(), 'tail': rest[b]['tail'].round(5).tolist(),
                   'R': rot_to_quat(rest[b]['R']).round(6).tolist()} for b in SK.NAMES],
        'root': root.round(5).tolist(),
        'q': {b: Q[b].round(5).tolist() for b in SK.NAMES},
        'joints': {k: v.round(4).tolist() for k, v in joints.items()},
        'heading': heading.round(4).tolist(), 'chestYaw': chestYaw.round(4).tolist(), 'headYaw': headYaw.round(4).tolist(),
        'contacts': [{'foot': c['foot'], 't0': c['t0'], 't1': c['t1'], 'eff': c.get('eff'), 'point': c.get('point', 'ball'), 'pivot': c.get('pivot'),
                      'anchor': anchors[k].round(4).tolist()} for k, c in enumerate(C)],
        'milestones': cfg['milestones'], 'corrections': corrections, 'angular_speed_max_deg_s': {k: round(v) for k, v in speed.items()},
        'stance_qc': qc,
        'restJoints': {**{'pelvis': rest['hips']['head'], 'chest': rest['neck']['head'],
                          'head': rest['head']['head'] + rest['head']['R'] @ (rest['head']['R'].T @ (np.array([0, -0.06, rest['head']['head'][2] + 0.07]) - rest['head']['head']))},
                       **{k + s_: v for s_ in 'LR' for k, v in (('hip', rest['thigh.' + s_]['head']), ('knee', rest['shin.' + s_]['head']),
                          ('ankle', rest['foot.' + s_]['head']), ('toe', rest['toe.' + s_]['tail']), ('shoulder', rest['upperarm.' + s_]['head']),
                          ('elbow', rest['forearm.' + s_]['head']), ('wrist', rest['hand.' + s_]['head']), ('hand', lm['handtip' + s_]),
                          ('ball', sole['ball' + s_]), ('heel', sole['heel' + s_]))}},
    }
    out['restJoints'] = {k: np.asarray(v).round(5).tolist() for k, v in out['restJoints'].items()}
    json.dump(out, open(a.out, 'w'))
    raw = {'t': T.tolist(), 'mp_local_raw': Lraw.round(4).tolist(), 'mp_local_smoothed': Ls.round(4).tolist(), 'root_pnp_m': root0.round(4).tolist()}
    json.dump(raw, open(os.path.splitext(a.out)[0] + '.mp.json', 'w'))
    print('frames', n, 'scale', round(sc, 3))
    for q_ in qc:
        print('stance', q_)
    print('corrections:', *corrections, sep='\n  ')
    print('max angular speed deg/s', {k: round(v) for k, v in speed.items()})


if __name__ == '__main__':
    main()
