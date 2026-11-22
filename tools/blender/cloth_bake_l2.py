"""E2A Realism V3.1 (2026-11-22) — L2 EXPERIMENT: can a headless bpy Cloth bake give the jersey real cloth motion
that the engine could play back as per-frame vertex animation? (brief V3.1 sec. garment, "TEST L2").
  /tmp/claude-0/venv3d/bin/python -I tools/blender/cloth_bake_l2.py -- <player_v31.blend> <out.json> [frames=90]
Scene: the V3.1 player's armature is keyed with a short authored test move (rest -> 2 m forward run-in with a hard stop,
then a 0.35 m vertical jump and a landing), the jersey gets a Cloth modifier (cotton-like, pinned above the chest via the
_E2A_HEM attribute: pin = 1 - hem), the body gets a Collision modifier. The cache is baked by stepping frame_set (the
same as ptcache.bake_all for a single cache, but measurable per frame). Reports bake time, per-frame stability
(NaN, max vertex speed, max stretch vs rest edges), hem-to-body penetration, and the size a per-frame vertex animation
would have (float32 / float16 / quantised delta) for 12.5 s at 30 fps. Nothing here is used by the renderer."""
import bpy, sys, json, time, math
import numpy as np

argv = sys.argv[sys.argv.index('--') + 1:]
blend, out = argv[0], argv[1]
NF = int(argv[2]) if len(argv) > 2 else 90
bpy.ops.wm.open_mainfile(filepath=blend)
scn = bpy.context.scene
scn.frame_start, scn.frame_end = 1, NF
arm = bpy.data.objects['E2A_Rig']
J = bpy.data.objects['E2A_Jersey']
Bd = bpy.data.objects['E2A_Body']
# ---- authored test move on the root bone (hips): run-in, hard stop, jump, land
pb = arm.pose.bones['hips']
pb.rotation_mode = 'QUATERNION'
keys = [(1, 0.0, 0.0), (20, 0.0, 0.0), (38, -1.4, 0.0), (44, -1.9, -0.06), (50, -2.0, -0.08), (56, -2.0, -0.12), (60, -2.0, 0.0),
        (66, -2.0, 0.3), (71, -2.0, 0.35), (76, -2.0, 0.3), (82, -2.0, -0.1), (90, -2.0, 0.0)]
# armature local: bone 'hips' rest axes -> move in pose space along the bone's own axes; use the object instead for clarity
for f, y, z in keys:
    if f > NF:
        continue
    arm.location = (0.0, y, z)
    arm.keyframe_insert('location', frame=f)
for fc in arm.animation_data.action.fcurves if hasattr(arm.animation_data.action, 'fcurves') else []:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'
# ---- cloth on the jersey: pin group from _E2A_HEM (1 at the hem = free)
hem = J.data.attributes.get('_E2A_HEM')
vg = J.vertex_groups.new(name='pin')
for i in range(len(J.data.vertices)):
    h = hem.data[i].value if hem else 0.0
    vg.add([i], float(max(0.0, 1.0 - h * 1.25)), 'REPLACE')
# the cloth modifier must run AFTER the armature
cl = J.modifiers.new('Cloth', 'CLOTH')
s = cl.settings
s.quality = 6
s.mass = 0.15
s.tension_stiffness = 12; s.compression_stiffness = 12; s.shear_stiffness = 6; s.bending_stiffness = 0.3
s.air_damping = 1.0
s.vertex_group_mass = 'pin'
s.pin_stiffness = 1.0
cl.collision_settings.use_collision = True
cl.collision_settings.distance_min = 0.006
cl.collision_settings.use_self_collision = False
cl.point_cache.frame_start, cl.point_cache.frame_end = 1, NF
col = Bd.modifiers.new('Collision', 'COLLISION')
Bd.collision.thickness_outer = 0.004
# ---- bake by stepping
dg = bpy.context.evaluated_depsgraph_get()
rest = np.array([v.co[:] for v in J.data.vertices])
edges = np.array([e.vertices[:] for e in J.data.edges])
L0 = np.linalg.norm(rest[edges[:, 0]] - rest[edges[:, 1]], axis=1)
nv = len(rest)
frames = []
times = []
t_all = time.time()
for f in range(1, NF + 1):
    t0 = time.time()
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    je = J.evaluated_get(dg)
    me = je.to_mesh()
    P = np.empty(nv * 3, np.float32)
    me.vertices.foreach_get('co', P)
    je.to_mesh_clear()
    frames.append(P.reshape(-1, 3).copy())
    times.append(time.time() - t0)
bake = time.time() - t_all
F = np.array(frames)  # world-ish (object space of the jersey, parented to the moving armature object)
# skinned-only reference: same frames without cloth
cl.show_viewport = False; cl.show_render = False
ref = []
for f in range(1, NF + 1):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    je = J.evaluated_get(dg)
    me = je.to_mesh()
    P = np.empty(nv * 3, np.float32)
    me.vertices.foreach_get('co', P)
    je.to_mesh_clear()
    ref.append(P.reshape(-1, 3).copy())
R = np.array(ref)
D = F - R  # cloth offset over plain skinning
finite = bool(np.isfinite(F).all())
spd = np.linalg.norm(np.diff(F, axis=0), axis=2).max(axis=1) * 30  # m/s per frame
stretch = np.array([(np.linalg.norm(x[edges[:, 0]] - x[edges[:, 1]], axis=1) / np.maximum(L0, 1e-6)).max() for x in F])
off = np.linalg.norm(D, axis=2)
hemv = np.array([hem.data[i].value for i in range(nv)]) if hem else np.zeros(nv)
res = {
    'blend': blend.split('/')[-1], 'frames': NF, 'verts': nv, 'bake_s': round(bake, 2), 'per_frame_ms_median': round(float(np.median(times)) * 1000, 1),
    'per_frame_ms_max': round(float(np.max(times)) * 1000, 1), 'finite': finite,
    'max_vertex_speed_mps': round(float(spd.max()), 2), 'max_vertex_speed_frame': int(spd.argmax()) + 2,
    'max_edge_stretch': round(float(stretch.max()), 3), 'cloth_offset_hem_max_m': round(float(off[:, hemv > 0.5].max()), 4) if (hemv > 0.5).any() else None,
    'cloth_offset_hem_median_m': round(float(np.median(off[:, hemv > 0.5])), 4) if (hemv > 0.5).any() else None,
    'cloth_offset_pinned_max_m': round(float(off[:, hemv < 0.05].max()), 4),
    'offset_by_frame_hem_max': [round(float(x), 4) for x in off[:, hemv > 0.5].max(axis=1)] if (hemv > 0.5).any() else [],
}
# vertex-animation size for the 12.5 s take at 30 fps (375 frames), jersey only, one player
moving = int((off.max(axis=0) > 0.002).sum())
res['size_estimate_375f'] = {
    'float32_all_verts_MB': round(nv * 3 * 4 * 375 / 1e6, 2),
    'float16_moving_verts_MB': round(moving * 3 * 2 * 375 / 1e6, 2),
    'int8_quantised_delta_moving_MB': round(moving * 3 * 1 * 375 / 1e6, 2),
    'moving_verts': moving,
    'note': 'per player and per authored take: a baked cache only exists for one fixed motion; any new play needs a new bake',
}
json.dump(res, open(out, 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'offset_by_frame_hem_max'}, indent=1))
