"""E2A 3D lab — reduced game skeleton fitted to the MakeHuman body (numpy only; shared by retarget.py and the bpy build).

21 deforming bones (Blender convention: +Y along the bone, roll chosen so +Z points forward/up, see ROLL):
hips spine chest neck head | clavicle upperarm forearm hand (L/R) | thigh shin foot toe (L/R).
MakeHuman's 163 bones are collapsed onto these for the skin weights (MH2E2A).
Coordinates: play/Blender, metres, z up, rest pose faces -y.
"""
import numpy as np
import mh_body

SOLE = 0.02  # the shoe sole lifts the barefoot body 2 cm off the floor

BONES = [  # name, parent, head joint, tail joint, roll target ('fwd' = -y, 'up' = +z)
    ('hips', None, 'HIPC', 'spine03____head', 'fwd'),
    ('spine', 'hips', 'spine03____head', 'spine01____head', 'fwd'),
    ('chest', 'spine', 'spine01____head', 'neck01____head', 'fwd'),
    ('neck', 'chest', 'neck01____head', 'head____head', 'fwd'),
    ('head', 'neck', 'head____head', 'head____tail', 'fwd'),
]
for s in 'LR':
    BONES += [
        (f'clavicle.{s}', 'chest', f'clavicle.{s}____head', f'upperarm01.{s}____head', 'fwd'),
        (f'upperarm.{s}', f'clavicle.{s}', f'upperarm01.{s}____head', f'lowerarm01.{s}____head', 'fwd'),
        (f'forearm.{s}', f'upperarm.{s}', f'lowerarm01.{s}____head', f'wrist.{s}____head', 'fwd'),
        (f'hand.{s}', f'forearm.{s}', f'wrist.{s}____head', f'finger3-1.{s}____head', 'fwd'),
        (f'thigh.{s}', 'hips', f'upperleg01.{s}____head', f'lowerleg01.{s}____head', 'fwd'),
        (f'shin.{s}', f'thigh.{s}', f'lowerleg01.{s}____head', f'foot.{s}____head', 'fwd'),
        (f'foot.{s}', f'shin.{s}', f'foot.{s}____head', f'toe3-1.{s}____head', 'up'),
        (f'toe.{s}', f'foot.{s}', f'toe3-1.{s}____head', f'toe3-3.{s}____tail', 'up'),
    ]
NAMES = [b[0] for b in BONES]

# ---- Realism V3 (2026-11-22, opt-in: enable_fingers()): 3 finger bones per hand so the hand can CLOSE on the ball
# (the 21-bone rig weights every finger to `hand`: a rigid open hand, fingertips 4+ cm off the ball).
#   fingers1.s  proximal phalanges of fingers 2-5 (pivot on the middle knuckle, finger3-1 head)
#   fingers2.s  middle + distal phalanges of fingers 2-5 (pivot on finger3-2 head)
#   thumb.s     thumb phalanges 2-3 (finger1-1 = thumb metacarpal stays on `hand`)
# One bone drives four fingers (one curl angle): a deliberate simplification (cheap, deterministic, glTF-safe).
FINGERS = []
for _s in 'LR':
    FINGERS += [
        (f'fingers1.{_s}', f'hand.{_s}', f'finger3-1.{_s}____head', f'finger3-2.{_s}____head', 'fwd'),
        (f'fingers2.{_s}', f'fingers1.{_s}', f'finger3-2.{_s}____head', f'finger3-3.{_s}____tail', 'fwd'),
        (f'thumb.{_s}', f'hand.{_s}', f'finger1-2.{_s}____head', f'finger1-3.{_s}____tail', 'fwd'),
    ]
FINGERS_ON = False


def enable_fingers():
    """switch this module to the V3 skeleton (21 + 6 = 27 bones). Call before build()."""
    global FINGERS_ON
    if FINGERS_ON:
        return
    FINGERS_ON = True
    BONES.extend(FINGERS)
    NAMES[:] = [b[0] for b in BONES]


def mh2e2a(mh):
    """MakeHuman bone -> E2A bone (skin weights)."""
    side = mh[-1] if mh[-2:] in ('.L', '.R') else None
    base = mh[:-2] if side else mh
    S = f'.{side}' if side else ''
    if base in ('root', 'spine05', 'spine04', 'pelvis'):
        return 'hips'
    if base in ('spine03', 'spine02'):
        return 'spine'
    if base in ('spine01', 'breast'):
        return 'chest'
    if base.startswith('neck'):
        return 'neck'
    if base in ('clavicle', 'shoulder01'):
        return 'clavicle' + S
    if base.startswith('upperarm'):
        return 'upperarm' + S
    if base.startswith('lowerarm'):
        return 'forearm' + S
    if FINGERS_ON and base.startswith('finger') and base != 'finger1-1':
        if base.startswith('finger1-'):
            return 'thumb' + S
        return ('fingers1' if base.endswith('-1') else 'fingers2') + S
    if base in ('wrist',) or base.startswith(('metacarpal', 'finger')):
        return 'hand' + S
    if base.startswith('upperleg'):
        return 'thigh' + S
    if base.startswith('lowerleg'):
        return 'shin' + S
    if base == 'foot':
        return 'foot' + S
    if base.startswith('toe'):
        return 'toe' + S
    return 'head'  # face, jaw, eyes, tongue, ...


def frame(y, ref):
    """Blender bone matrix: +Y = y, +Z towards ref (orthogonalised), X = Y x Z."""
    y = y / np.linalg.norm(y)
    z = ref - y * (ref @ y)
    z /= np.linalg.norm(z)
    x = np.cross(y, z)
    return np.stack([x, y, z], 1)


def build(body=None):
    body = body or mh_body.build()
    J = dict(body['J'])
    for k in J:
        J[k] = J[k] + np.array([0, 0, SOLE])
    J['HIPC'] = (J['upperleg01.L____head'] + J['upperleg01.R____head']) / 2
    V = body['V'] + np.array([0, 0, SOLE])
    rest = {}
    for name, parent, h, t, roll in BONES:
        hd, tl = J[h], J[t]
        ref = np.array([0, -1.0, 0]) if roll == 'fwd' else np.array([0, 0, 1.0])
        rest[name] = {'parent': parent, 'head': hd, 'tail': tl, 'R': frame(tl - hd, ref), 'len': float(np.linalg.norm(tl - hd))}
    # virtual landmarks of the rest pose, MediaPipe semantics (for the retarget frames)
    r = body['B']['regions'][:mh_body.NBODY]
    idx = np.arange(mh_body.NBODY)
    lm = {}
    for s, sgn in (('L', 1), ('R', -1)):
        foot = idx[(r == 9) & (np.sign(V[:mh_body.NBODY, 0]) == sgn)]
        low = foot[V[foot, 2] < V[foot, 2].min() + 0.03]
        lm['heel' + s] = V[low[np.argmax(V[low, 1])]].copy()       # back-most low point
        lm['toe' + s] = V[low[np.argmin(V[low, 1])]].copy()        # front-most low point
        lm['ball' + s] = J[f'toe3-1.{s}____head'].copy(); lm['ball' + s][2] = SOLE
        lm['hip' + s] = J[f'upperleg01.{s}____head']
        lm['knee' + s] = J[f'lowerleg01.{s}____head']
        lm['ankle' + s] = J[f'foot.{s}____head']
        lm['shoulder' + s] = J[f'upperarm01.{s}____head']
        lm['elbow' + s] = J[f'lowerarm01.{s}____head']
        lm['wrist' + s] = J[f'wrist.{s}____head']
        lm['index' + s] = J[f'finger2-1.{s}____head']
        lm['pinky' + s] = J[f'finger5-1.{s}____head']
        lm['knuckle' + s] = J[f'finger3-1.{s}____head']
        lm['handtip' + s] = J[f'finger3-3.{s}____tail']
        head = idx[(r == 0)]
        ear_z = J['head____head'][2] + 0.06
        band = head[np.abs(V[head, 2] - ear_z) < 0.02]
        lm['ear' + s] = V[band[np.argmax(sgn * V[band, 0])]].copy()
    head = idx[(r == 0)]
    front = head[np.abs(V[head, 0]) < 0.01]
    nz = J['head____head'][2] + 0.05
    cand = front[np.abs(V[front, 2] - nz) < 0.04]
    lm['nose'] = V[cand[np.argmin(V[cand, 1])]].copy()
    lm['headtop'] = V[head[np.argmax(V[head, 2])]].copy()
    return {'rest': rest, 'J': J, 'lm': lm, 'V': V, 'body': body}


if __name__ == '__main__':
    sk = build()
    for n in NAMES:
        b = sk['rest'][n]
        print(f"{n:12s} len {b['len']:.3f} head {np.round(b['head'], 3)}")
    for k, v in sk['lm'].items():
        print(k, np.round(v, 3))
