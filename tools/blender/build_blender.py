"""E2A 3D lab — build the deformable E2A screener in Blender (bpy as a module, background) and key the clip.

  /tmp/claude-0/venv3d/bin/python -I tools/blender/build_blender.py --motion motion.json --solved solved.json \
      --ref-video ref_5452_sdr.mp4 --out-blend e2a_bloqueador_lab.blend --out-glb e2a_bloqueador_screen_roll.glb

* body: MakeHuman base mesh (ara3d-data, CC0-1.0) morphed by mh_body.py, face neutralised (brand rule: no facial
  detail in recreations), soles 2 cm up for the shoe;
* clothes from the body surface (same vertices -> same skin weights): sleeveless jersey (E2A navy #0B1C3D, gold
  #C9A24D trims, gold number front and back), loose shorts (legs flared, 30 % of the thigh weight moved to the hips so
  the hem does not stick to the thigh), white socks, shoes (white upper, dark sole), short hair shell with volume on top;
* armature: skeleton.py (23 bones), MakeHuman weights collapsed per bone, top 4 influences;
* action: motion.json (retarget.py) keyed per frame (quaternions + hips location), 29.97 fps;
* reference: a camera at the solved video camera (focal, height, pitch) with the SDR video as background, so the clip
  can be checked / edited against the take in Blender.
"""
import argparse, json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import mathutils
import mh_body
import skeleton as SK

ap = argparse.ArgumentParser()
ap.add_argument('--motion', required=True)
ap.add_argument('--solved', required=True)
ap.add_argument('--ref-video', default='')
ap.add_argument('--out-blend', required=True)
ap.add_argument('--out-glb', required=True)
ap.add_argument('--motion-extra', action='append', default=[], help='NAME=motion.json: extra action (e.g. the mirrored take)')
ap.add_argument('--number', default='5')
ap.add_argument('--skin', default='#4E3122')  # SKINS[4] of the engine (O5), same tone as the capsule athlete
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])

NAVY = '#0B1C3D'
GOLD = '#C9A24D'
NUMBER = '#E3BE68'


def hex2lin(h, alpha=1.0):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, alpha)


# ---------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.fps = 30
scn.render.fps_base = 1.001
body = mh_body.build()
sk = SK.build(body)
V = sk['V'][:mh_body.NBODY].copy()
B = body['B']
F = B['F']
FU = B['FU']
UV = B['UV']
reg = B['regions'][:mh_body.NBODY]
bones = [b['name'] for b in B['meta']['bones']]

# adjacency
nb = [set() for _ in range(len(V))]
for f in F:
    for k in range(4):
        i, j = f[k], f[(k + 1) % 4]
        nb[i].add(j); nb[j].add(i)
nbl = [np.array(sorted(s)) for s in nb]


def laplace(P, mask_w, iters):
    P = P.copy()
    idx = np.where(mask_w > 0)[0]
    for _ in range(iters):
        avg = np.array([P[nbl[i]].mean(0) for i in idx])
        P[idx] = P[idx] + (avg - P[idx]) * mask_w[idx, None] * 0.6
    return P


# face neutralisation: smooth the front of the head below the hairline (keeps skull, jaw, brow mass and a soft nose)
J = sk['J']
head_c = J['head____head']
face_w = np.zeros(len(V))
hd = np.where(reg == 0)[0]
front = -(V[hd, 1] - (head_c[1] - 0.02))
fz = V[hd, 2]
w = np.clip(front / 0.06, 0, 1) * np.clip((2.035 + mh_body.H_BODY * 0 - fz) / 0.03, 0, 1) * np.clip((fz - (head_c[2] - 0.01)) / 0.03, 0, 1)
face_w[hd] = w
V = laplace(V, face_w, 40)
# keep a soft nose: push the central strip forward a little
nose = sk['lm']['nose']
dn = np.linalg.norm((V - nose) * [1.6, 1.0, 0.8], axis=1)
V[:, 1] -= 0.012 * np.exp(-(dn / 0.025) ** 2) * (reg == 0)

# ---------------------------------------------------------------- weights
WGT = np.zeros((len(V), len(SK.NAMES)))
for i in range(len(V)):
    bi, bv = B['W'][i]
    for b_, v_ in zip(bi, bv):
        WGT[i, SK.NAMES.index(SK.mh2e2a(bones[b_]))] += v_
WGT /= np.maximum(WGT.sum(1, keepdims=True), 1e-9)


def top4(W):
    W = W.copy()
    for i in range(len(W)):
        o = np.argsort(W[i])[::-1]
        W[i, o[4:]] = 0
    return W / np.maximum(W.sum(1, keepdims=True), 1e-9)


WGT = top4(WGT)


# vertex normals (area weighted from quads)
def vnormals(P, faces):
    N = np.zeros_like(P)
    for f in faces:
        p = P[f]
        n = np.cross(p[2] - p[0], p[3] - p[1]) if len(f) == 4 else np.cross(p[1] - p[0], p[2] - p[0])
        N[f] += n
    return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)


NRM = vnormals(V, F)
cent = V[F].mean(1)
freg = reg[F[:, 0]]
hip_z = J['HIPC'][2]
knee_z = J['lowerleg01.L____head'][2]

def boundary_loops(faces):
    E = {}
    for f in faces:
        for k in range(len(f)):
            e = (min(f[k], f[(k + 1) % len(f)]), max(f[k], f[(k + 1) % len(f)]))
            E[e] = E.get(e, 0) + 1
    adj = {}
    for (i, j), c in E.items():
        if c == 1:
            adj.setdefault(i, []).append(j); adj.setdefault(j, []).append(i)
    loops, seen = [], set()
    for st in adj:
        if st in seen:
            continue
        loop, cur, prev = [st], st, None
        seen.add(st)
        while True:
            nx = [x for x in adj[cur] if x != prev and x not in seen]
            if not nx:
                break
            prev, cur = cur, nx[0]
            seen.add(cur); loop.append(cur)
        loops.append(loop)
    return loops


def smooth_boundary(P, faces, iters=12, ring_iters=6, flat=None):
    """straighten the jagged boundary of a face subset (1-D Laplacian along each loop, then relax the next ring);
    flat(loop_points) -> z or None: snap a loop onto a horizontal plane (hems)."""
    P = P.copy()
    loops = boundary_loops(faces)
    on = set()
    for lp in loops:
        idx = np.array(lp)
        on.update(lp)
        for _ in range(iters):
            q = P[idx]
            P[idx] = 0.5 * q + 0.25 * (np.roll(q, 1, 0) + np.roll(q, -1, 0))
        if flat is not None:
            z = flat(P[idx])
            if z is not None:
                P[idx, 2] = z
    used = set(np.unique(np.concatenate([np.asarray(f) for f in faces])).tolist())
    ring = [v for v in used if v not in on and any(n_ in on for n_ in nbl[v])]
    for _ in range(ring_iters):
        for v in ring:
            nn = [x for x in nbl[v] if x in used]
            P[v] = 0.5 * P[v] + 0.5 * P[nn].mean(0)
    return P, on


# ---------------------------------------------------------------- face sets
jersey_f = np.where(((freg == 2) & (cent[:, 2] > hip_z - 0.06)))[0]
shorts_f = np.where(((freg == 2) & (cent[:, 2] < hip_z + 0.11)) | (freg == 3) | ((freg == 7) & (cent[:, 2] > knee_z + 0.10)) |
                    ((freg == 255) & (cent[:, 2] < hip_z + 0.11) & (cent[:, 2] > knee_z + 0.10)))[0]
shoe_f = np.where((freg == 9) | ((freg == 255) & (cent[:, 2] < 0.13)) | ((freg == 8) & (cent[:, 2] < 0.12)))[0]
hair_line = lambda P: np.interp(P[:, 1] - head_c[1], [-0.2, -0.08, 0.0, 0.08], [2.045, 2.02, 1.975, 1.935])
hair_v = (reg == 0) & (V[:, 2] > hair_line(V))
hair_f = np.where(hair_v[F].all(1))[0]
# body faces hidden under clothes / shoes (margin so no gap shows)
hide = np.zeros(len(F), bool)
hide[np.where((freg == 2) & (cent[:, 2] > hip_z - 0.03) & (cent[:, 2] < J['neck01____head'][2] - 0.06))[0]] = True
hide[np.where(((freg == 7) | (freg == 3) | (freg == 255)) & (cent[:, 2] > knee_z + 0.14) & (cent[:, 2] < hip_z + 0.08))[0]] = True
hide[np.where((freg == 9))[0]] = True
# keep the shoulders / armpits of the torso visible (sleeveless): only hide faces well inside the jersey
armpit = (freg == 2) & (np.abs(cent[:, 0]) > 0.16) & (cent[:, 2] > J['upperarm01.L____head'][2] - 0.12)
hide[armpit] = False
body_f = np.where(~hide)[0]

# ---------------------------------------------------------------- textures (PIL)
from PIL import Image, ImageDraw, ImageFont
TEXDIR = os.path.join(os.path.dirname(os.path.abspath(a.out_blend)), 'tex')
os.makedirs(TEXDIR, exist_ok=True)


def font(size):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def jersey_texture(path, num):
    W, H = 2048, 1024
    im = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(im)
    import random
    rnd = random.Random(5)
    for _ in range(26000):  # mesh fabric
        x, y = rnd.randrange(W), rnd.randrange(H)
        d.point((x, y), fill='#14284F' if rnd.random() < 0.5 else '#081530')
    # side panels (under the arms: u = 0 / 0.5 are the left / right sides)
    for u in (0.0, 0.5, 1.0):  # thin side piping under the arms
        d.rectangle([u * W - 7, 0, u * W + 7, H], fill=GOLD)
    f = font(380)
    for u, s in ((0.25, 1.0), (0.75, 1.25)):  # front, back
        cx, cy = u * W, H * 0.42
        bb = d.textbbox((0, 0), num, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tmp = Image.new('RGBA', (tw + 60, th + 80), (0, 0, 0, 0))
        dt = ImageDraw.Draw(tmp)
        dt.text((30 - bb[0], 40 - bb[1]), num, font=f, fill=NUMBER, stroke_width=12, stroke_fill=GOLD)
        tmp = tmp.resize((int(tmp.width * 0.62 * s), int(tmp.height * s)))
        im.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)), tmp)
    im.save(path)


jersey_texture(os.path.join(TEXDIR, 'jersey_navy_gold.png'), a.number)


def shorts_texture(path):
    W, H = 1024, 512
    im = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(im)
    import random
    rnd = random.Random(7)
    for _ in range(9000):
        d.point((rnd.randrange(W), rnd.randrange(H)), fill='#14284F' if rnd.random() < 0.5 else '#081530')
    for u in (0.0, 0.5, 1.0):  # gold side stripes (outer side of each leg)
        d.rectangle([u * W - 16, 0, u * W + 16, H], fill=GOLD)
    im.save(path)


shorts_texture(os.path.join(TEXDIR, 'shorts_navy_gold.png'))


# ---------------------------------------------------------------- materials
def mat(name, color, rough=0.7, tex=None, sss=0.0, sheen=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = hex2lin(color)
    bsdf.inputs['Roughness'].default_value = rough
    if 'Subsurface Weight' in bsdf.inputs and sss:
        bsdf.inputs['Subsurface Weight'].default_value = sss
        bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.35, 0.2)
        bsdf.inputs['Subsurface Scale'].default_value = 0.01
    if sheen and 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = sheen
        # glTF KHR_materials_sheen exports the tint as sheenColor (weight ignored): keep it dark, or three.js turns the cloth silver
        if 'Sheen Tint' in bsdf.inputs:
            bsdf.inputs['Sheen Tint'].default_value = (0.10, 0.11, 0.15, 1.0)
    if tex:
        img = bpy.data.images.load(tex)
        tn = m.node_tree.nodes.new('ShaderNodeTexImage')
        tn.image = img
        m.node_tree.links.new(tn.outputs['Color'], bsdf.inputs['Base Color'])
    return m


M_SKIN = mat('E2A_skin', a.skin, 0.52, sss=0.15)
M_JERSEY = mat('E2A_jersey', NAVY, 0.78, tex=os.path.join(TEXDIR, 'jersey_navy_gold.png'), sheen=0.2)
M_TRIM = mat('E2A_trim_gold', GOLD, 0.6)
M_SHORTS = mat('E2A_shorts', NAVY, 0.8, tex=os.path.join(TEXDIR, 'shorts_navy_gold.png'), sheen=0.2)
M_SOCK = mat('E2A_sock', '#F4F4F4', 0.9)
M_SHOE = mat('E2A_shoe', '#F2F2F0', 0.42)
M_SOLE = mat('E2A_sole', '#1A1A1A', 0.6)
M_HAIR = mat('E2A_hair', '#15100C', 0.92)


# ---------------------------------------------------------------- mesh helpers
def make_mesh(name, P, faces, mats, face_mat, uvs=None, W=None):
    used = np.unique(np.concatenate([np.asarray(f) for f in faces]))
    remap = -np.ones(len(P), int)
    remap[used] = np.arange(len(used))
    me = bpy.data.meshes.new(name)
    fl = [[int(remap[i]) for i in f] for f in faces]
    me.from_pydata(P[used].tolist(), [], fl)
    me.update()
    for m in mats:
        me.materials.append(m)
    for pi, poly in enumerate(me.polygons):
        poly.material_index = int(face_mat[pi])
        poly.use_smooth = True
    if uvs is not None:
        uvl = me.uv_layers.new(name='UVMap')
        k = 0
        for pi, poly in enumerate(me.polygons):
            for li in poly.loop_indices:
                uvl.data[li].uv = uvs[pi][li - poly.loop_start]
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if W is not None:
        for bi, bn in enumerate(SK.NAMES):
            vg = ob.vertex_groups.new(name=bn)
            for vi_new, vi_old in enumerate(used):
                if W[vi_old, bi] > 1e-4:
                    vg.add([vi_new], float(W[vi_old, bi]), 'REPLACE')
    return ob, used


def pipe_loops(name, P, faces, W, radius=0.006, keep=lambda q: True, inset=0.004):
    """gold piping: a thin tube along every boundary loop of a clothing mesh, skinned like its nearest vertex"""
    verts, quads, wts = [], [], []
    Nl = vnormals(P, faces)
    for lp in boundary_loops(faces):
        q = P[lp]
        if len(lp) < 6 or not keep(q):
            continue
        m = len(lp)
        base = len(verts)
        for k in range(m):
            tng = q[(k + 1) % m] - q[k - 1]
            tng /= max(np.linalg.norm(tng), 1e-9)
            nn = Nl[lp[k]]
            bn = np.cross(tng, nn)
            c = q[k] + nn * 0.002 - bn * 0  # on the edge
            for r in range(6):
                ang = 2 * math.pi * r / 6
                verts.append(c + radius * (math.cos(ang) * nn + math.sin(ang) * bn))
                wts.append(W[lp[k]])
        for k in range(m):
            for r in range(6):
                a0 = base + k * 6 + r; a1 = base + k * 6 + (r + 1) % 6
                b0 = base + ((k + 1) % m) * 6 + r; b1 = base + ((k + 1) % m) * 6 + (r + 1) % 6
                quads.append([a0, a1, b1, b0])
    if not verts:
        return None
    verts = np.array(verts); wts = np.array(wts)
    ob, _ = make_mesh(name, verts, quads, [M_TRIM], [0] * len(quads), None, wts)
    return ob


# body (skin + socks)
sock_face = (cent[:, 2] < 0.26) & ((freg == 8) | (freg == 255))
bf = [F[i] for i in body_f]
bmat = [1 if sock_face[i] else 0 for i in body_f]
buv = [[UV[FU[i][k]] for k in range(4)] for i in body_f]
ob_body, _ = make_mesh('E2A_Body', V, bf, [M_SKIN, M_SOCK], bmat, buv, WGT)

# jersey: offset outward, looser below the chest, flared hem
Pj = V.copy()
chest_z = J['spine01____head'][2]
off = 0.02 + 0.01 * np.clip((chest_z - V[:, 2]) / 0.25, 0, 1) + 0.012 * np.clip((hip_z + 0.02 - V[:, 2]) / 0.08, 0, 1)
Pj += NRM * off[:, None]
hem_j = hip_z - 0.05
Pj, jon = smooth_boundary(Pj, [F[i] for i in jersey_f], 14, 6, flat=lambda q: hem_j if q[:, 2].max() < hip_z + 0.02 else None)
jv = np.unique(F[jersey_f])
# cylindrical UV around the trunk axis: u = 0 his left side, 0.25 front, 0.5 right side, 0.75 back
def cyl_uv(p, z0, z1):
    phi = math.atan2(-(p[1] - 0.02), p[0])
    u = 1.0 - (phi % (2 * math.pi)) / (2 * math.pi)  # u grows clockwise seen from above -> text reads correctly outside
    return [u, (p[2] - z0) / (z1 - z0)]
z0j, z1j = hip_z - 0.06, J['neck01____head'][2]
juv = []
for i in jersey_f:
    uvq = [cyl_uv(Pj[v], z0j, z1j) for v in F[i]]
    us = [q[0] for q in uvq]
    if max(us) - min(us) > 0.5:  # seam: keep the quad on one side
        uvq = [[q[0] + (1 if q[0] < 0.5 else 0), q[1]] for q in uvq]
    juv.append(uvq)
# gold trims: faces touching the jersey boundary (collar, armholes, hem)
Ej = {}
for i in jersey_f:
    f = F[i]
    for k in range(4):
        e = (min(f[k], f[(k + 1) % 4]), max(f[k], f[(k + 1) % 4]))
        Ej[e] = Ej.get(e, 0) + 1
jmat = [0 for i in jersey_f]  # trims are a separate piping mesh (pipe_loops) along the smoothed boundaries
ob_jersey, _ = make_mesh('E2A_Jersey', Pj, [F[i] for i in jersey_f], [M_JERSEY, M_TRIM], jmat, juv, WGT)
ob_jpipe = pipe_loops('E2A_JerseyTrim', Pj, [F[i] for i in jersey_f], WGT, 0.007)



# shorts: loose; leg part pushed away from the thigh axis, flared towards the hem
Ps = V.copy()
offs = np.full(len(V), 0.022)
for s in 'LR':
    h0 = J[f'upperleg01.{s}____head']; k0 = J[f'lowerleg01.{s}____head']
    ax = (k0 - h0) / np.linalg.norm(k0 - h0)
    side = (V[:, 0] > 0) if s == 'L' else (V[:, 0] <= 0)
    legp = side & (V[:, 2] < hip_z - 0.02)
    rel = V - h0
    along = rel @ ax
    radial = rel - np.outer(along, ax)
    rn = radial / np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
    u = np.clip((hip_z - 0.02 - V[:, 2]) / (hip_z - knee_z - 0.12), 0, 1)
    push = 0.012 + 0.035 * u
    Ps[legp] += rn[legp] * push[legp, None]
Ps += NRM * offs[:, None]
Wsh = WGT.copy()
hips_i = SK.NAMES.index('hips')
for s in 'LR':
    ti = SK.NAMES.index('thigh.' + s)
    u = np.clip((hip_z - V[:, 2]) / 0.4, 0, 1) * 0.3
    mv = Wsh[:, ti] * u
    Wsh[:, ti] -= mv
    Wsh[:, hips_i] += mv
# gold side stripe on the shorts: faces near the outer side
hem_s = knee_z + 0.12
Ps, son = smooth_boundary(Ps, [F[i] for i in shorts_f], 14, 6, flat=lambda q: hem_s if q[:, 2].max() < hip_z - 0.1 else None)
z0s, z1s = hem_s, hip_z + 0.12
suv = []
for i in shorts_f:
    uvq = [cyl_uv(Ps[v], z0s, z1s) for v in F[i]]
    us = [q[0] for q in uvq]
    if max(us) - min(us) > 0.5:
        uvq = [[q[0] + (1 if q[0] < 0.5 else 0), q[1]] for q in uvq]
    suv.append(uvq)
shm = [0 for i in shorts_f]
ob_shorts, _ = make_mesh('E2A_Shorts', Ps, [F[i] for i in shorts_f], [M_SHORTS, M_TRIM], shm, suv, Wsh)
ob_spipe = pipe_loops('E2A_ShortsTrim', Ps, [F[i] for i in shorts_f], Wsh, 0.006, keep=lambda q: q[:, 2].min() > hip_z)

# shoes: per foot, convex hull of the inflated foot + ankle (a smooth sneaker last, no toes), sole flat on the floor,
# weights from the nearest body vertex
import bmesh
from mathutils import kdtree
Pf = V.copy() + NRM * 0.010
shoe_obs = []
sv_all = np.unique(F[shoe_f])
for s_, sg in (('L', 1), ('R', -1)):
    ids = sv_all[np.sign(V[sv_all, 0]) == sg]
    bm = bmesh.new()
    for p_ in Pf[ids]:
        bm.verts.new(p_.tolist())
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    kd = kdtree.KDTree(len(ids))
    for k_, i_ in enumerate(ids):
        kd.insert(V[i_].tolist(), k_)
    kd.balance()
    for vv in bm.verts:
        if vv.co.z < 0.03:
            vv.co.z = max(0.0, (vv.co.z - 0.03) * 0.1)
    me = bpy.data.meshes.new('E2A_Shoe.' + s_)
    bm.to_mesh(me); bm.free()
    me.materials.append(M_SHOE); me.materials.append(M_SOLE)
    for poly in me.polygons:
        cz = sum(me.vertices[v].co.z for v in poly.vertices) / len(poly.vertices)
        poly.material_index = 1 if cz < 0.03 else 0
        poly.use_smooth = True
    ob = bpy.data.objects.new('E2A_Shoe.' + s_, me)
    bpy.context.collection.objects.link(ob)
    vgs = {bn: ob.vertex_groups.new(name=bn) for bn in SK.NAMES}
    for vv in me.vertices:
        co, k_, dist = kd.find(vv.co)
        src = ids[k_]
        for bi, bn in enumerate(SK.NAMES):
            if WGT[src, bi] > 1e-4:
                vgs[bn].add([vv.index], float(WGT[src, bi]), 'REPLACE')
    shoe_obs.append(ob)
ob_shoes = shoe_obs[0]

# hair: short shell, volume on top (5440: curly on top, short sides and nape)
Ph = V.copy()
top = np.clip((V[:, 2] - 2.0) / 0.1, 0, 1)
Ph += NRM * (0.006 + 0.016 * top)[:, None]
Ph, _ = smooth_boundary(Ph, [F[i] for i in hair_f], 16, 6)
ob_hair, _ = make_mesh('E2A_Hair', Ph, [F[i] for i in hair_f], [M_HAIR], [0] * len(hair_f), None, WGT)

# ---------------------------------------------------------------- armature
arm = bpy.data.armatures.new('E2A_Rig')
ob_arm = bpy.data.objects.new('E2A_Rig', arm)
bpy.context.collection.objects.link(ob_arm)
bpy.context.view_layer.objects.active = ob_arm
bpy.ops.object.mode_set(mode='EDIT')
for name, parent, h, t, roll in SK.BONES:
    r = sk['rest'][name]
    eb = arm.edit_bones.new(name)
    eb.head = r['head'].tolist()
    eb.tail = r['tail'].tolist()
    eb.align_roll(mathutils.Vector(r['R'][:, 2].tolist()))
    if parent:
        eb.parent = arm.edit_bones[parent]
        eb.use_connect = False
bpy.ops.object.mode_set(mode='OBJECT')
# check the rest matrices against skeleton.py
err = 0
for name in SK.NAMES:
    m = np.array(arm.bones[name].matrix_local)[:3, :3]
    err = max(err, np.abs(m - sk['rest'][name]['R']).max())
print('rest matrix max diff vs skeleton.py', err)
for ob in [o for o in (ob_body, ob_jersey, ob_jpipe, ob_shorts, ob_spipe, *shoe_obs, ob_hair) if o is not None]:
    ob.parent = ob_arm
    md = ob.modifiers.new('Armature', 'ARMATURE')
    md.object = ob_arm
    md.use_deform_preserve_volume = True  # Blender viewport; glTF / three.js use linear skinning

# ---------------------------------------------------------------- action from motion.json
Mo = json.load(open(a.motion))
n = len(Mo['t'])
rest = sk['rest']


def q2m(q):
    x, y, z, w = q
    return np.array(mathutils.Quaternion((w, x, y, z)).to_matrix())


def key_action(act_name, Mo):
    """key one motion.json as an action of the rig (world rotations -> local, hips location)"""
    n = len(Mo['t'])
    act = bpy.data.actions.new(act_name)
    act.use_fake_user = True
    ob_arm.animation_data.action = act
    root = np.array(Mo['root'])
    Rw = {b: np.array([q2m(q) for q in Mo['q'][b]]) for b in SK.NAMES}
    for i in range(n):
        for name in SK.NAMES:
            pb = ob_arm.pose.bones[name]
            par = rest[name]['parent']
            if par is None:
                Bm = rest[name]['R'].T @ Rw[name][i]
                loc = rest[name]['R'].T @ (root[i] - rest[name]['head'])
                pb.location = loc.tolist()
                pb.keyframe_insert('location', frame=i + 1)
            else:
                Bm = rest[name]['R'].T @ rest[par]['R'] @ Rw[par][i].T @ Rw[name][i]
            q = mathutils.Matrix(Bm.tolist()).to_quaternion()
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = q
            pb.keyframe_insert('rotation_quaternion', frame=i + 1)
    return act


ob_arm.animation_data_create()
t0 = Mo['t'][0]
fps = 30000 / 1001
scn.frame_start = 1
scn.frame_end = n
# extra actions first (stashed in NLA tracks, muted), then the main take stays the active action
for spec_ in a.motion_extra:
    nm, pth = spec_.split('=', 1)
    ex = key_action(nm, json.load(open(pth)))
    tr = ob_arm.animation_data.nla_tracks.new()
    tr.name = nm
    tr.strips.new(nm, 1, ex)
    tr.mute = True
    print('extra action', nm, len(json.load(open(pth))['t']), 'frames')
act = key_action('E2A_screen_roll_5452', Mo)
print('keyed frames', n)

# verify FK of the keyed action against motion.json joints
scn.frame_set(int(n * 0.6))
dg = bpy.context.evaluated_depsgraph_get()
pbx = ob_arm.pose.bones['shin.L']
pos = np.array(ob_arm.matrix_world @ pbx.head)
want = np.array(Mo['joints']['kneeL'][int(n * 0.6) - 1])
print('FK check knee.L blender vs motion.json (m):', np.round(pos, 4), np.round(want, 4), np.linalg.norm(pos - want))

# ---------------------------------------------------------------- reference camera (solved video camera)
S = json.load(open(a.solved))
Mf = np.array(S['floor_M']); cf = np.array(S['floor_c']); sc = Mo['scale_mp_to_m']
cam_pos = ((np.zeros(3) - cf) @ Mf.T) * sc
# camera axes in the floor frame: camera x right, y down, z forward (OpenCV) -> Blender camera looks down -Z, +Y up
xc = Mf[:, 0]; yc = Mf[:, 1]; zc = Mf[:, 2]  # columns: camera axes expressed in floor coords
Rb = np.stack([xc, -yc, -zc], 1)
camd = bpy.data.cameras.new('REF_5452_cam')
camd.sensor_fit = 'HORIZONTAL'
camd.sensor_width = 36.0
camd.lens = S['focal_px'] / 1920 * 36.0
ob_cam = bpy.data.objects.new('REF_5452_cam', camd)
bpy.context.collection.objects.link(ob_cam)
M4 = mathutils.Matrix.Identity(4)
for r_ in range(3):
    for c_ in range(3):
        M4[r_][c_] = Rb[r_, c_]
    M4[r_][3] = cam_pos[r_]
ob_cam.matrix_world = M4
scn.camera = ob_cam
scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
if a.ref_video and os.path.exists(a.ref_video):
    clip = bpy.data.movieclips.load(a.ref_video)
    camd.show_background_images = True
    bg = camd.background_images.new()
    bg.source = 'MOVIE_CLIP'
    bg.clip = clip
    bg.alpha = 0.6
    bg.frame_method = 'FIT'
    # clip frame 1 = video frame round(t0*fps)+1
    bg.clip_user.frame_current = 1
    clip.frame_offset = int(round(t0 * fps))
    print('reference movie clip', a.ref_video, 'offset', clip.frame_offset)
# floor
bpy.ops.mesh.primitive_plane_add(size=12, location=(0.5, 0, 0))
bpy.context.object.name = 'REF_floor'
txt = bpy.data.texts.new('E2A_README')
txt.write('E2A screener lab (5452). Armature E2A_Rig, action E2A_screen_roll_5452 keyed from motion.json (retarget.py).\n'
          'REF_5452_cam = solved camera of the take; background = SDR copy of the MOV (tonemapped, not for colour).\n'
          'Frame 1 = video t0 = %.3f s. Rebuild: tools/blender/build_blender.py.\n' % t0)
os.makedirs(os.path.dirname(os.path.abspath(a.out_blend)), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.out_blend), relative_remap=True)
print('saved', a.out_blend)
# ---------------------------------------------------------------- glb (mesh + skeleton + clip)
for o in list(bpy.data.objects):
    o.select_set(o.name.startswith('E2A_'))
bpy.ops.export_scene.gltf(filepath=os.path.abspath(a.out_glb), export_format='GLB', use_selection=True, export_animations=True,
                          export_skins=True, export_yup=True, export_apply=False, export_texcoords=True, export_normals=True,
                          export_materials='EXPORT', export_image_format='AUTO', export_def_bones=False, export_frame_range=True)
print('glb', a.out_glb, os.path.getsize(a.out_glb))
