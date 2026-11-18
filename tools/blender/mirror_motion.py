"""E2A 3D lab — mirror a retargeted motion (motion.json) left <-> right about the clip's x = 0 plane.
5452 mirrored = the same screen-and-roll to the other side (pivot on the RIGHT ball, turn to his LEFT, chest open
to the ball on his right), i.e. the case of 5451; used because the lab play rolls that way (see the report).
  python -I tools/blender/mirror_motion.py motion.json motion_mirror.json
Rotations: world delta D = R R_rest^T is conjugated by S = diag(-1, 1, 1) and re-applied to the swapped bone's rest.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retarget import quat_to_rot, rot_to_quat

m = json.load(open(sys.argv[1]))
S = np.diag([-1.0, 1, 1])
sw = lambda n: n.replace('.L', '.#').replace('.R', '.L').replace('.#', '.R') if ('.L' in n or '.R' in n) else n
swk = lambda k: (k[:-1] + {'L': 'R', 'R': 'L'}[k[-1]]) if k[-1] in 'LR' and k not in ('pelvis',) else k
rest = {b['name']: quat_to_rot(np.array(b['R'])) for b in m['bones']}
out = dict(m)
out['root'] = (np.array(m['root']) @ S).round(5).tolist()
out['joints'] = {swk(k): (np.array(v) @ S).round(4).tolist() for k, v in m['joints'].items()}
q2 = {}
for b, qs in m['q'].items():
    R = quat_to_rot(np.array(qs))
    D = R @ rest[b].T
    Dm = S @ D @ S
    q = rot_to_quat(Dm @ rest[sw(b)])
    for i in range(1, len(q)):
        if (q[i] * q[i - 1]).sum() < 0:
            q[i] = -q[i]
    q2[sw(b)] = q.round(5).tolist()
out['q'] = q2
for k in ('heading', 'chestYaw', 'headYaw'):
    out[k] = (np.pi - np.array(m[k])).round(4).tolist()
out['contacts'] = [{**c, 'foot': {'L': 'R', 'R': 'L'}[c['foot']], 'anchor': (np.array(c['anchor']) @ S).round(4).tolist()} for c in m['contacts']]
ren = {'brake_R': 'brake_L', 'plant_L': 'plant_R', 'plant_R': 'plant_L', 'unweight_R': 'unweight_L', 'R_touch': 'L_touch', 'L_release': 'R_release',
       'L_land': 'R_land', 'R_land': 'L_land'}
out['milestones'] = {ren.get(k, k): v for k, v in m['milestones'].items()}
out['mirrored'] = True
out['corrections'] = m['corrections'] + ['mirrored left <-> right (mirror_motion.py)']
json.dump(out, open(sys.argv[2], 'w'))
print('mirrored ->', sys.argv[2])
