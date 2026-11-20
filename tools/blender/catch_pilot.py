#!/usr/bin/env python3
"""E2A Tactical: Blender pilot of a key event (2026-11-20, Double Drag, master prompt 3D sec. 5).
Rebuilds the rig pose of the receiver (and the nearest defender) from scripts/pose-dump.mts as simple meshes in bpy
(capsule limbs, trunk, head; FIBA size-7 ball; rim), renders the catch from the SIDE and the 3/4 view (Workbench, fast,
deterministic), and measures on the MESHES, not on the joints:
  - ball vs trunk: signed distance of the ball surface to the trunk mesh (negative = the ball sinks into the body);
  - ball vs hands: nearest hand-mesh surface to the ball surface (contact once the ball is CAUGHT);
  - ball in front of the trunk (along the chest direction) at the contact.
  python3 tools/blender/catch_pilot.py pose.json out_dir --player O5 --frames 95,98,101,105 [--defender X5] [--inject behind]
--inject behind moves the ball centre 0.12 m BEHIND the trunk at the contact frames (injected failure: the check must FAIL).
Needs `pip install bpy` (5.x). Writes out_dir/<tag>-f<frame>-{side,34}.png, out_dir/<tag>-report.json."""
import argparse, json, math, os
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BALL_R = 0.121
ap = argparse.ArgumentParser()
ap.add_argument('pose'); ap.add_argument('out')
ap.add_argument('--player', default='O5'); ap.add_argument('--defender', default='')
ap.add_argument('--frames', default=''); ap.add_argument('--inject', default='')
ap.add_argument('--tag', default='catch'); ap.add_argument('--res', type=int, default=540)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
D = json.load(open(a.pose))
rows = {r['f']: r for r in D['rows']}
frames = [int(x) for x in a.frames.split(',')] if a.frames else sorted(rows)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'MATERIAL'
    sc.display.shading.show_shadows = True
    sc.render.resolution_x, sc.render.resolution_y = a.res, int(a.res * 16 / 9)
    sc.render.film_transparent = False
    sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.02, 0.03, 0.06)
    return sc


def mat(name, rgb):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    return m


def capsule(name, p, q, r, m):
    p, q = Vector(p), Vector(q)
    bm = bmesh.new()
    L = (q - p).length
    bmesh.ops.create_cone(bm, segments=16, radius1=r, radius2=r, depth=max(L, 1e-4), cap_ends=True)
    for c in (-L / 2, L / 2):
        s = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=r)
        bmesh.ops.translate(bm, verts=s['verts'], vec=(0, 0, c))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    ob.location = (p + q) / 2
    ob.rotation_mode = 'QUATERNION'; ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference((q - p).normalized())
    ob.data.materials.append(m)
    return ob


def sphere(name, c, r, m):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    ob.location = c; ob.data.materials.append(m)
    return ob


def body(pid, P, team):
    d = P['dims']; b = d['build']
    jer = mat(f'jersey{team}', (0.06, 0.13, 0.32) if team == 'O' else (0.92, 0.92, 0.9))
    skin = mat('skin', (0.45, 0.30, 0.22))
    parts = {'trunk': [], 'hands': [], 'other': []}
    parts['trunk'].append(capsule(f'{pid}_trunk', P['pelvis'], P['chest'], 0.13 * (0.7 + 0.3 * b), jer))
    parts['other'].append(sphere(f'{pid}_head', P['head'], d['headR'], skin))
    for s in (0, 1):
        parts['other'].append(capsule(f'{pid}_up{s}', P['shoulder'][s], P['elbow'][s], 0.045 * b, jer if team == 'X' else skin))
        parts['other'].append(capsule(f'{pid}_fo{s}', P['elbow'][s], P['wrist'][s], 0.038 * b, skin))
        parts['hands'].append(capsule(f'{pid}_hand{s}', P['wrist'][s], P['hand'][s], 0.035, skin))
        parts['other'].append(capsule(f'{pid}_th{s}', P['hip'][s], P['knee'][s], 0.075 * b, jer))
        parts['other'].append(capsule(f'{pid}_sh{s}', P['knee'][s], P['ankle'][s], 0.055 * b, skin))
        parts['other'].append(capsule(f'{pid}_ft{s}', P['ankle'][s], P['toe'][s], 0.045, mat('shoe', (0.9, 0.9, 0.9))))
    parts['other'].append(capsule(f'{pid}_shl', P['shoulder'][0], P['shoulder'][1], 0.06 * b, jer))
    return parts


def bvh(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    for o in objs:
        me = o.evaluated_get(dg).to_mesh(); me.transform(o.matrix_world); bm.from_mesh(me); o.evaluated_get(dg).to_mesh_clear()
    t = BVHTree.FromBMesh(bm); bm.free()
    return t


def surf_dist(tree, c):
    """signed distance of point c to a closed mesh (negative inside), via nearest + normal side"""
    loc, nor, _, dist = tree.find_nearest(Vector(c))
    if loc is None:
        return 9.0
    return dist if (Vector(c) - loc).dot(nor) >= 0 else -dist


def cam(sc, target, yaw_deg, pitch_deg, dist, lens=50):
    t = Vector(target)
    y, p = math.radians(yaw_deg), math.radians(pitch_deg)
    pos = t + Vector((math.cos(y) * math.cos(p), math.sin(y) * math.cos(p), math.sin(p))) * dist
    c = bpy.data.objects.get('cam')
    if not c:
        c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(c)
    c.data.lens = lens; c.location = pos
    c.rotation_mode = 'QUATERNION'; c.rotation_quaternion = (t - pos).to_track_quat('-Z', 'Y')
    sc.camera = c


report = {'pose': os.path.basename(a.pose), 'player': a.player, 'inject': a.inject, 'frames': []}
for f in frames:
    r = rows[f]
    sc = reset()
    floor = bpy.data.meshes.new('floor'); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=7.5)
    bm.to_mesh(floor); bm.free(); fo = bpy.data.objects.new('floor', floor); sc.collection.objects.link(fo)
    fo.location = (0, 7, 0); fo.data.materials.append(mat('wood', (0.78, 0.6, 0.38)))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.2286, minor_radius=0.01, location=(0, 1.575, 3.05))
    bpy.context.object.data.materials.append(mat('rim', (0.9, 0.35, 0.1)))
    P = r['players'][a.player]
    parts = body(a.player, P, a.player[0])
    if a.defender:
        body(a.defender, r['players'][a.defender], a.defender[0])
    ball = list(r['ball'])
    heading = P['chestYaw']
    fwd = Vector((math.cos(heading), math.sin(heading), 0))
    if a.inject == 'behind':
        trunk_mid = (Vector(P['pelvis']) + Vector(P['chest'])) / 2
        ball = list(trunk_mid - fwd * 0.12)   # centre 12 cm behind the trunk axis: inside the body
    sphere('ball', ball, BALL_R, mat('ball', (0.85, 0.33, 0.08)))
    tt, th = bvh(parts['trunk']), bvh(parts['hands'])
    d_trunk = surf_dist(tt, ball) - BALL_R
    d_hand = surf_dist(th, ball) - BALL_R
    ahead = (Vector(ball) - (Vector(P['pelvis']) + Vector(P['chest'])) / 2).dot(fwd)
    held = r['holder'] == a.player
    row = {'f': f, 'S': f, 't': round(r['t'], 4), 'holder': r['holder'], 'ball_to_trunk_m': round(d_trunk, 4),
           'ball_to_hand_m': round(d_hand, 4), 'ball_ahead_of_trunk_m': round(ahead, 4),
           'ok': d_trunk >= -0.02 and (not held or (d_hand <= 0.05 and ahead >= 0.1))}
    report['frames'].append(row)
    tgt = ((Vector(P['pelvis']) + Vector(ball)) / 2)
    for tag, yaw, pitch in (('side', math.degrees(heading) + 90, 12), ('34', math.degrees(heading) + 40, 20)):
        cam(sc, tgt, yaw, pitch, 4.2)
        sc.render.filepath = os.path.join(a.out, f'{a.tag}-f{f:03d}-{tag}.png')
        bpy.ops.render.render(write_still=True)
report['pass'] = all(x['ok'] for x in report['frames'])
json.dump(report, open(os.path.join(a.out, f'{a.tag}-report.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in report.items() if k != 'frames'}), [(x['f'], x['ball_to_trunk_m'], x['ball_to_hand_m'], x['ok']) for x in report['frames']])
