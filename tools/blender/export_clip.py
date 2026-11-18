"""E2A 3D lab — motion.json (retarget.py) -> compact clip for the engine (template/src/t3d/clips/<name>.json).
Same numbers that build_blender.py keys into the .blend / .glb action (bone world rotations in play coords,
hips root, Pose-layout joints, contacts, milestones), rounded to 0.1 mm / 1e-5.
  python -I tools/blender/export_clip.py motion.json template/src/t3d/clips/screen-roll-5452.json
"""
import json, sys
m = json.load(open(sys.argv[1]))
r = lambda v, d=4: [round(x, d) for x in v]
keep = ['pelvis', 'chest', 'head'] + [k + s for s in 'LR' for k in ('hip', 'knee', 'ankle', 'toe', 'shoulder', 'elbow', 'wrist', 'hand', 'ball', 'heel')]
out = {
    'source': m['source'], 'fps': m['fps'], 't0': m['t'][0], 'n': len(m['t']),
    'bones': [{'name': b['name'], 'parent': b['parent'], 'head': r(b['head']), 'tail': r(b['tail']), 'R': r(b['R'], 6)} for b in m['bones']],
    'restJoints': {k: r(v) for k, v in m['restJoints'].items()},
    'root': [r(v) for v in m['root']],
    'q': {b: [r(q, 5) for q in qs] for b, qs in m['q'].items()},
    'joints': {k: [r(v) for v in m['joints'][k]] for k in keep},
    'heading': r(m['heading']), 'chestYaw': r(m['chestYaw']),
    'contacts': m['contacts'], 'milestones': m['milestones'], 'mirrored': bool(m.get('mirrored')),
}
# side-neutral milestone names for the engine (skelclip.ts)
ms = m['milestones']
pick = lambda *ks: next((ms[k] for k in ks if k in ms), None)
out['milestones'] = {**ms, 'brake': pick('brake_R', 'brake_L'), 'plant': pick('plant_L', 'plant_R') if not m.get('mirrored') else pick('plant_R'),
                     'set': ms['set'], 'unweight': pick('unweight_R', 'unweight_L'), 'pivot_start': ms['pivot_start'],
                     'release': pick('L_release', 'R_release'), 'end': ms['end']}
json.dump(out, open(sys.argv[2], 'w'), separators=(',', ':'))
print(sys.argv[2], len(json.dumps(out, separators=(',', ':'))) // 1024, 'KB')
