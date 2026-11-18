"""E2A 3D — head pitch calibration of a retargeted motion (motion.json), applied at the ORIGIN of the data.

Why (measured 2026-11-19 on 5452): retarget.py builds the head frame from MediaPipe nose - ear midpoint and calibrates
it on the MakeHuman rest landmarks. MediaPipe's ear points sit higher on the head than the MakeHuman ear band, so the
captured face direction is pitched UP by a constant: +10..+30 deg above the horizon through the whole take, while the
video (1.5, 2.2, 2.9, 3.6 s) shows the eyes level on the handler. The engine used to hide it with a clamp; the .blend
and the .glb still looked up. Fix:
  1. constant calibration: rotate the head about its own side axis so the MEDIAN face pitch over the take is
     `--target` deg (default -4: eyes level, slightly down on the ball handler);
  2. anatomical limit of the head relative to the chest: [-8, +24] deg (back / forward) — continuity with the trunk;
  3. absolute face pitch in [-12, +6] deg (MediaPipe nose-ear noise is not a gesture: eyes level in the take);
  4. neck = halfway (slerp) between chest and head, so the bend is shared by neck and head;
  5. the 'head' joint (Pose layout) is moved with the head rotation; headYaw unchanged (it is the gaze yaw).
  python -I tools/blender/fix_head.py motion.json motion_fixed.json [--target -4]
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retarget import quat_to_rot, rot_to_quat


def axis_rot(ax, ang):
    ax = ax / np.linalg.norm(ax)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K


def slerp_R(A, B, u):
    qa, qb = rot_to_quat(A[None])[0], rot_to_quat(B[None])[0]
    if qa @ qb < 0:
        qb = -qb
    d = np.clip(qa @ qb, -1, 1)
    th = np.arccos(d)
    q = qa if th < 1e-6 else (np.sin((1 - u) * th) * qa + np.sin(u * th) * qb) / np.sin(th)
    return quat_to_rot(q / np.linalg.norm(q))


def face_pitch(R):
    """bones use +Y along the bone and +Z to the front: pitch of the face direction above the horizon (rad)"""
    return np.arcsin(np.clip(R[:, 2][2], -1, 1))


def fix(m, target_deg=-4.0, lim=(-8.0, 24.0)):
    n = len(m['t'])
    Rc = [quat_to_rot(np.array(q)) for q in m['q']['chest']]
    Rh = [quat_to_rot(np.array(q)) for q in m['q']['head']]
    p = np.array([face_pitch(R) for R in Rh])
    cal = np.radians(target_deg) - np.median(p)
    out_h, out_n, rel_before, rel_after = [], [], [], []
    for i in range(n):
        R = Rh[i]
        # 1. constant calibration about the head's own side axis (bone x)
        sgn = 1.0
        R1 = axis_rot(R[:, 0], cal) @ R
        if abs(face_pitch(R1) - (face_pitch(R) + cal)) > abs(face_pitch(axis_rot(R[:, 0], -cal) @ R) - (face_pitch(R) + cal)):
            sgn = -1.0
            R1 = axis_rot(R[:, 0], -cal) @ R
        # 2. limit relative to the chest (positive rel = face more up than the chest front)
        rel = face_pitch(R1) - face_pitch(Rc[i])
        rel_before.append(np.degrees(face_pitch(R) - face_pitch(Rc[i])))
        lo, hi = np.radians(lim[0]), np.radians(lim[1])
        want = np.clip(rel, lo, hi)
        if abs(want - rel) > 1e-5:
            R1 = axis_rot(R1[:, 0], sgn * (want - rel)) @ R1
        # 3. absolute face pitch kept in [-12, +6] deg (eyes on the handler / defender, never at the floor or the sky):
        #    MediaPipe's per-frame nose-ear noise (±10 deg) is not a gesture of the player (5452: eyes level throughout)
        fp = face_pitch(R1)
        want = np.clip(fp, np.radians(-12), np.radians(6))
        if abs(want - fp) > 1e-5:
            R1 = axis_rot(R1[:, 0], sgn * (want - fp)) @ R1
        rel_after.append(np.degrees(face_pitch(R1) - face_pitch(Rc[i])))
        out_h.append(R1)
        out_n.append(slerp_R(Rc[i], R1, 0.5))
    m = dict(m)
    q = dict(m['q'])
    qh = rot_to_quat(np.array(out_h)); qn = rot_to_quat(np.array(out_n))
    for arr in (qh, qn):
        for i in range(1, len(arr)):
            if arr[i] @ arr[i - 1] < 0:
                arr[i] = -arr[i]
    q['head'] = qh.round(6).tolist(); q['neck'] = qn.round(6).tolist()
    m['q'] = q
    # head joint (Pose layout) follows the head rotation about the base of the neck
    J = dict(m['joints'])
    hj, cj = np.array(J['head']), np.array(J['chest'])
    J['head'] = [(cj[i] + out_h[i] @ Rh[i].T @ (hj[i] - cj[i])).round(4).tolist() for i in range(n)]
    m['joints'] = J
    pa = np.degrees([face_pitch(R) for R in out_h])
    note = (f'head pitch calibrated at the origin (fix_head.py): constant {np.degrees(cal):+.1f} deg (median face pitch '
            f'{np.degrees(np.median(p)):+.1f} -> {target_deg:+.1f}), head vs chest limited to [{lim[0]}, {lim[1]}] deg, face pitch in [-12, +6] deg, neck = slerp(chest, head, 0.5)')
    m['corrections'] = list(m.get('corrections', [])) + [note]
    m['head_fix'] = {'cal_deg': round(float(np.degrees(cal)), 2), 'face_pitch_deg_before': [round(float(np.degrees(p.min())), 1), round(float(np.degrees(np.median(p))), 1), round(float(np.degrees(p.max())), 1)],
                     'face_pitch_deg_after': [round(float(pa.min()), 1), round(float(np.median(pa)), 1), round(float(pa.max()), 1)],
                     'rel_chest_deg_before': [round(float(min(rel_before)), 1), round(float(max(rel_before)), 1)],
                     'rel_chest_deg_after': [round(float(min(rel_after)), 1), round(float(max(rel_after)), 1)]}
    return m


if __name__ == '__main__':
    args = sys.argv[1:]
    tgt = float(args[args.index('--target') + 1]) if '--target' in args else -4.0
    m = fix(json.load(open(args[0])), tgt)
    json.dump(m, open(args[1], 'w'))
    print(args[1], m['head_fix'])
