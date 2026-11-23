"""E2A Realism V3.3 (2026-11-22) — Gate 3, BOUNDED L2 cloth experiment (brief V3.3 Gate 3). Same test as V3.1's
cloth_bake_l2.py (run-in, hard stop, 0.35 m jump, landing) on the V3.2 offence GLB (the mesh V3.3 renders), with the
three V3.1 failure causes addressed:
  1. 41 % edge stretch      -> tension / compression 40 (was 12), quality 10 (was 6), structural springs limited
  2. 4-9 cm drop at rest     -> 30-frame static pre-roll so the garment reaches its hanging equilibrium before t=0
                                (the measured frames start after the pre-roll; drift at rest is reported)
  3. "no path into Three.js" -> the baked frames are exported as glTF morph targets on the jersey (one key per frame)
                                and loaded back with three.js GLTFLoader (scripts/qc-cloth-l2-v33.mts)
  python3 -I tools/blender/cloth_bake_l2_v33.py -- <player.glb> <out.json> <out_jersey_morph.glb> [frames=90] [--weld]
Nothing here is used by the renderer."""
import bpy, sys, json, time
import numpy as np

argv = sys.argv[sys.argv.index('--') + 1:]
glb, out, out_glb = argv[0], argv[1], argv[2]
NF = int(argv[3]) if len(argv) > 3 and argv[3].isdigit() else 90
PRE = 30
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
scn = bpy.context.scene
scn.render.fps = 30
scn.frame_start, scn.frame_end = 1, PRE + NF
arm = bpy.data.objects['E2A_Rig']
J = bpy.data.objects['E2A_Jersey']
Bd = bpy.data.objects['E2A_Body']
for o in list(bpy.data.objects):
    if o.name not in ('E2A_Rig', 'E2A_Jersey', 'E2A_Body'):
        bpy.data.objects.remove(o, do_unlink=True)
keys = [(1, 0.0, 0.0), (20, 0.0, 0.0), (38, -1.4, 0.0), (44, -1.9, -0.06), (50, -2.0, -0.08), (56, -2.0, -0.12), (60, -2.0, 0.0),
        (66, -2.0, 0.3), (71, -2.0, 0.35), (76, -2.0, 0.3), (82, -2.0, -0.1), (90, -2.0, 0.0)]
arm.location = (0.0, 0.0, 0.0)
arm.keyframe_insert('location', frame=1)
for f, y, z in keys:
    if f > NF:
        continue
    arm.location = (0.0, y, z)
    arm.keyframe_insert('location', frame=f + PRE)
WELD = '--weld' in argv
if WELD:
    # glTF splits vertices along UV seams: unwelded, the seams are free edges and the cloth tears open there (run 1:
    # max edge stretch 3.6 with p99 1.12). Weld for the bake (vertex count then differs from the runtime mesh).
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(J.data)
    n0 = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(J.data)
    bm.free()
    print('welded', n0, '->', len(J.data.vertices))
hem = J.data.attributes.get('_E2A_HEM')
nv = len(J.data.vertices)
hemv = np.array([hem.data[i].value for i in range(nv)]) if hem else np.zeros(nv)
vg = J.vertex_groups.new(name='pin')
for i in range(nv):
    vg.add([i], float(max(0.0, 1.0 - hemv[i] * 1.25)), 'REPLACE')
cl = J.modifiers.new('Cloth', 'CLOTH')
s = cl.settings
s.quality = 10
s.mass = 0.15
s.tension_stiffness = 40; s.compression_stiffness = 40; s.shear_stiffness = 10; s.bending_stiffness = 0.3
s.air_damping = 1.0
s.vertex_group_mass = 'pin'
s.pin_stiffness = 1.0
cl.collision_settings.use_collision = True
cl.collision_settings.distance_min = 0.006
cl.point_cache.frame_start, cl.point_cache.frame_end = 1, PRE + NF
Bd.modifiers.new('Collision', 'COLLISION')
Bd.collision.thickness_outer = 0.004


def sample(f):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    je = J.evaluated_get(dg)
    me = je.to_mesh()
    P = np.empty(nv * 3, np.float32)
    me.vertices.foreach_get('co', P)
    je.to_mesh_clear()
    return P.reshape(-1, 3).copy()


rest = np.array([v.co[:] for v in J.data.vertices])
edges = np.array([e.vertices[:] for e in J.data.edges])
L0 = np.linalg.norm(rest[edges[:, 0]] - rest[edges[:, 1]], axis=1)
t_all = time.time()
times, frames = [], []
for f in range(1, PRE + NF + 1):
    t0 = time.time()
    P = sample(f)
    times.append(time.time() - t0)
    if f > PRE:
        frames.append(P)
bake = time.time() - t_all
F = np.array(frames)
cl.show_viewport = False
cl.show_render = False
R = np.array([sample(f) for f in range(PRE + 1, PRE + NF + 1)])
off = np.linalg.norm(F - R, axis=2)
spd = np.linalg.norm(np.diff(F, axis=0), axis=2).max(axis=1) * 30
stretch = np.array([(np.linalg.norm(x[edges[:, 0]] - x[edges[:, 1]], axis=1) / np.maximum(L0, 1e-6)).max() for x in F])
stretch_p99 = np.array([np.percentile(np.linalg.norm(x[edges[:, 0]] - x[edges[:, 1]], axis=1) / np.maximum(L0, 1e-6), 99) for x in F])
H = hemv > 0.5
rest_drift = float(np.linalg.norm(F[:19] - F[0], axis=2).max())  # frames 1-19 of the test: the body does not move yet
res = {'glb': glb.split('/')[-1], 'welded': WELD, 'frames': NF, 'preroll': PRE, 'verts': nv, 'bake_s': round(bake, 2),
       'per_frame_ms_median': round(float(np.median(times)) * 1000, 1), 'finite': bool(np.isfinite(F).all()),
       'max_vertex_speed_mps': round(float(spd.max()), 2), 'max_edge_stretch': round(float(stretch.max()), 3),
       'edge_stretch_p99_max': round(float(stretch_p99.max()), 3),
       'rest_drop_vs_skinned_hem_median_m': round(float(np.median(off[0, H])), 4) if H.any() else None,
       'rest_drift_after_preroll_m': round(rest_drift, 4),
       'cloth_offset_hem_median_m': round(float(np.median(off[:, H])), 4) if H.any() else None,
       'cloth_offset_hem_max_m': round(float(off[:, H].max()), 4) if H.any() else None,
       'cloth_offset_pinned_max_m': round(float(off[:, hemv < 0.05].max()), 4),
       'v31_reference': {'max_edge_stretch': 1.41, 'rest_drop_m': '0.04-0.09'}}
# ---- export: the baked frames as morph targets (shape keys) on a static copy of the jersey (object space)
J.modifiers.remove(cl)
for m in list(J.modifiers):
    J.modifiers.remove(m)
J.parent = None
J.shape_key_add(name='Basis', from_mix=False)
for k in range(NF):
    sk = J.shape_key_add(name=f'f{k:03d}', from_mix=False)
    sk.data.foreach_set('co', F[k].reshape(-1))
bpy.data.objects.remove(Bd, do_unlink=True)
bpy.data.objects.remove(arm, do_unlink=True)
t0 = time.time()
bpy.ops.export_scene.gltf(filepath=out_glb, export_format='GLB', export_morph=True, export_morph_normal=False, export_apply=False, export_animations=False, export_materials='NONE')  # geometry only (node loader has no image decoder)
res['export'] = {'path': out_glb.split('/')[-1], 'seconds': round(time.time() - t0, 2), 'morph_targets': NF}
import os
res['export']['bytes'] = os.path.getsize(out_glb)
json.dump(res, open(out, 'w'), indent=1)
print(json.dumps(res, indent=1))
