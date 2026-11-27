"""E2A Basketball IQ: build a Blender scene from a validated play (2026-11-27, EP02 "Beat the Blitz").

The scene reproduces exactly what the engine validated: it is keyed from the frame dump of
template/scripts/dump-play-frames.mts (player centres, body headings, the 3D ball) in ENGINE coordinates, which are
right-handed like Blender's (the owner's diagram frame is its mirror image: owner x = -engine x). Camera A looks straight
down with the basket at the top, so the owner's +x (the ball side) is on the right of the frame, as on his diagram.
Contents: FIBA half court (floor, lines, hoop at 3.05 m), 10 player proxies (capsule body + head + a nose marker for
the heading, offence white/gold, defence navy/red, height from the engine), the ball (radius 0.121 m), and the
directive's eight named cameras A-H (static views a director can key further). 30 fps, frame 1 = engine t 0.

This is a BLOCKING / LAYOUT scene for camera and staging work in Blender, not the final character render (the
deformable E2A player rig lives in tools/blender/build_blender.py and needs the MakeHuman / MPFB assets).

  python -I tools/blender/iq_scene_from_play.py --frames frames.json --out scene.blend [--fps 30] [--offset 1.2]
(needs bpy: Blender's Python, or `pip install bpy`)
"""
import argparse, json, math
import bpy

ap = argparse.ArgumentParser()
ap.add_argument("--frames", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--offset", type=float, default=1.2, help="engine time of the owner's K0 (marker only)")
a = ap.parse_args()
dump = json.load(open(a.frames))
F = dump["frames"]
step = max(1, round(dump["fps"] / a.fps))
F = F[::step]

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = a.fps
sc.frame_start, sc.frame_end = 1, len(F)
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.unit_settings.system = "METRIC"


def mat(name, rgb, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


hexrgb = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
M_FLOOR, M_LINE = mat("floor", (0.72, 0.52, 0.32)), mat("line", (1, 1, 1), 0.5)
M_O, M_OTRIM = mat("offence", (0.95, 0.95, 0.95)), mat("gold", hexrgb("#C9A24D"))
M_X, M_XTRIM = mat("defence", hexrgb("#0B1C3D")), mat("red", hexrgb("#E5483A"))
M_BALL, M_RIM = mat("ball", (0.9, 0.42, 0.1)), mat("rim", (0.95, 0.35, 0.1))


def link(o, coll="IQ"):
    c = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    if c.name not in sc.collection.children:
        sc.collection.children.link(c)
    for u in o.users_collection:
        u.objects.unlink(o)
    c.objects.link(o)
    return o


# court -------------------------------------------------------------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 7, 0))
fl = bpy.context.object; fl.name = "floor"; fl.scale = (15, 14, 1); fl.data.materials.append(M_FLOOR); link(fl, "court")


def polyline(name, pts, w=0.05):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = w / 2
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for p, (x, y) in zip(sp.points, pts):
        p.co = (x, y, 0.003, 1)
    o = bpy.data.objects.new(name, cu); o.data.materials.append(M_LINE); sc.collection.objects.link(o); link(o, "court")


HOOP = (0.0, 1.575)
polyline("endline", [(-7.5, 0), (7.5, 0)]); polyline("sidelines", [(-7.5, 0), (-7.5, 14), (7.5, 14), (7.5, 0)])
polyline("lane", [(-2.45, 0), (-2.45, 5.8), (2.45, 5.8), (2.45, 0)])
jy = HOOP[1] + math.sqrt(6.75 ** 2 - 6.6 ** 2); a0 = math.asin((jy - HOOP[1]) / 6.75)
polyline("three", [(6.6, 0), (6.6, jy)] + [(6.75 * math.cos(t), HOOP[1] + 6.75 * math.sin(t)) for t in [a0 + (math.pi - 2 * a0) * i / 64 for i in range(65)]] + [(-6.6, jy), (-6.6, 0)])
polyline("ft_circle", [(1.8 * math.cos(t), 5.8 + 1.8 * math.sin(t)) for t in [i * 2 * math.pi / 64 for i in range(65)]])
bpy.ops.mesh.primitive_torus_add(major_radius=0.2295, minor_radius=0.01, location=(HOOP[0], HOOP[1], 3.05))
r = bpy.context.object; r.name = "rim"; r.data.materials.append(M_RIM); link(r, "court")
bpy.ops.mesh.primitive_cube_add(location=(0, 1.2, 3.35)); bb = bpy.context.object; bb.name = "backboard"; bb.scale = (0.9, 0.025, 0.525); link(bb, "court")

# players + ball ----------------------------------------------------------------------------------------------------
pos = lambda f, i: (f["P"][i][0], f["P"][i][1])
head = lambda f, i: f["P"][i][4]                      # engine heading (radians from +x), right-handed like Blender
objs = {}
for i, H in dump["heights"].items():
    off = i[0] == "O"
    root = bpy.data.objects.new(i, None); sc.collection.objects.link(root); link(root, "players")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.23, depth=H * 0.78, location=(0, 0, H * 0.39))
    body = bpy.context.object; body.name = f"{i}_body"; body.parent = root; body.data.materials.append(M_O if off else M_X); link(body, "players")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0, H - 0.12))
    hd = bpy.context.object; hd.name = f"{i}_head"; hd.parent = root; hd.data.materials.append(M_OTRIM if off else M_XTRIM); link(hd, "players")
    bpy.ops.mesh.primitive_cube_add(size=0.12, location=(0.2, 0, H * 0.82))     # heading marker (chest, +x local)
    nz = bpy.context.object; nz.name = f"{i}_heading"; nz.parent = root; nz.data.materials.append(M_OTRIM if off else M_XTRIM); link(nz, "players")
    objs[i] = root
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.121); ball = bpy.context.object; ball.name = "ball"; ball.data.materials.append(M_BALL); link(ball, "players")

for n, f in enumerate(F, start=1):
    for i, o in objs.items():
        x, y = pos(f, i)
        o.location = (x, y, 0); o.rotation_euler = (0, 0, head(f, i))
        o.keyframe_insert("location", frame=n); o.keyframe_insert("rotation_euler", frame=n)
    ball.location = (f["B"][0], f["B"][1], f["B"][2]); ball.keyframe_insert("location", frame=n)
sc.timeline_markers.new("K0", frame=1 + round(a.offset * a.fps))

# the directive's cameras A-H (named static views) ---------------------------------------------------------------------
CAMS = {"A_overhead_tactical": ((0.3, 5.4, 19.0), (0.3, 5.4, 0)), "B_high_wide": ((0.3, 15.5, 11.0), (0.3, 5.0, 0)),
        "C_behind_ball_handler": ((5.4, 13.0, 3.2), (3.6, 8.8, 1.0)), "D_behind_short_roll": ((0.7, 9.4, 3.0), (0.3, 3.0, 1.0)),
        "E_weak_side_wing": ((-7.5, 9.0, 6.0), (-1.2, 4.2, 0.6)), "F_baseline": ((-1.0, -2.5, 2.2), (0.0, 4.5, 1.0)),
        "G_corner_low": ((-7.0, 0.8, 1.6), (-0.5, 4.5, 1.0)), "H_x4_isolation": ((-3.6, 8.0, 2.4), (0.3, 4.0, 1.0))}
E = lambda p: (-p[0], p[1], p[2])                     # camera spots are written in owner coordinates
for name, (loc, tgt) in CAMS.items():
    loc, tgt = E(loc), E(tgt)
    cd = bpy.data.cameras.new(name); cd.lens = 28
    c = bpy.data.objects.new(name, cd); c.location = loc; sc.collection.objects.link(c); link(c, "cameras")
    if name.startswith("A_"):
        c.rotation_euler = (0, 0, math.pi)                # straight down, basket at the top of the frame
        continue
    t = bpy.data.objects.new(name + "_target", None); t.location = tgt; sc.collection.objects.link(t); link(t, "cameras")
    k = c.constraints.new("TRACK_TO"); k.target = t; k.track_axis = "TRACK_NEGATIVE_Z"; k.up_axis = "UP_Y"
sc.camera = bpy.data.objects["B_high_wide"]
bpy.ops.object.light_add(type="SUN", location=(0, 6, 20)); link(bpy.context.object, "court")
bpy.ops.wm.save_as_mainfile(filepath=a.out)
print(f"saved {a.out}: {len(objs)} players, {len(F)} frames, {len(CAMS)} cameras")
