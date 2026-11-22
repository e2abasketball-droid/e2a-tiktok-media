# E2A Realism V3.2 (2026-11-22) — export the skinning data of a built player (.blend) for the per-frame cloth QC
# (template/scripts/qc_cloth_v32.py). Headless bpy, no Blender binary:
#   python -I tools/blender/export_qc_mesh.py -- player.blend out.npz
# Per mesh (E2A_Body, E2A_Jersey, E2A_Shorts, E2A_JerseyTrim, E2A_ShortsTrim): rest positions (Blender world = rig rest
# space, metres, z up), triangles, dense skin weights over the armature bones (rig order), _E2A_HEM / _E2A_EASE
# attributes when present, shape-key deltas by name. Read-only: the .blend is not saved.
import sys
import bpy
import numpy as np

argv = sys.argv[sys.argv.index('--') + 1:]
blend, out = argv[0], argv[1]
bpy.ops.wm.open_mainfile(filepath=blend)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
bones = [b.name for b in arm.data.bones]
data = {'bones': np.array(bones)}
for name in ('E2A_Body', 'E2A_Jersey', 'E2A_Shorts', 'E2A_JerseyTrim', 'E2A_ShortsTrim'):
    ob = bpy.data.objects.get(name)
    if ob is None:
        continue
    me = ob.data
    n = len(me.vertices)
    P = np.zeros(n * 3)
    me.vertices.foreach_get('co', P)
    P = P.reshape(n, 3)
    mw = np.array(ob.matrix_world)
    P = P @ mw[:3, :3].T + mw[:3, 3]
    me.calc_loop_triangles()
    T = np.zeros(len(me.loop_triangles) * 3, dtype=np.int32)
    me.loop_triangles.foreach_get('vertices', T)
    W = np.zeros((n, len(bones)), dtype=np.float32)
    gi = {g.index: g.name for g in ob.vertex_groups}
    for v in me.vertices:
        for g in v.groups:
            nm = gi.get(g.group)
            if nm in bones:
                W[v.index, bones.index(nm)] = g.weight
    s = W.sum(1, keepdims=True)
    W = np.where(s > 0, W / np.maximum(s, 1e-9), W)
    k = name.replace('E2A_', '')
    data[k + '_P'] = P.astype(np.float32)
    data[k + '_T'] = T.reshape(-1, 3)
    data[k + '_W'] = W
    for at in ('_E2A_HEM', '_E2A_EASE'):
        a = me.attributes.get(at)
        if a is not None:
            v = np.zeros(n)
            a.data.foreach_get('value', v)
            data[k + at] = v.astype(np.float32)
    if me.shape_keys:
        basis = me.shape_keys.reference_key
        B = np.zeros(n * 3)
        basis.data.foreach_get('co', B)
        for kb in me.shape_keys.key_blocks:
            if kb == basis:
                continue
            K = np.zeros(n * 3)
            kb.data.foreach_get('co', K)
            D = (K - B).reshape(n, 3) @ mw[:3, :3].T
            if np.abs(D).max() > 1e-6:
                data[k + '_SK_' + kb.name] = D.astype(np.float32)
    print(name, n, 'verts', len(T) // 3, 'tris', 'sk', [kb.name for kb in me.shape_keys.key_blocks] if me.shape_keys else [])
np.savez_compressed(out, **data)
print('wrote', out)
