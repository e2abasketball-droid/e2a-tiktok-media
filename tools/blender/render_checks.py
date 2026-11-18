"""E2A 3D lab — check renders of the .blend (bpy, background).
  python -I tools/blender/render_checks.py BLEND OUTDIR --mode ref|views [--frames 1,20,...] [--engine CYCLES|BLENDER_WORKBENCH|BLENDER_EEVEE_NEXT]
ref:   the character over the reference take, from the solved video camera (transparent film -> composited by ffmpeg/PIL)
views: front / three-quarter / profile / back close views around the character at the given frames
"""
import argparse, math, os, sys
import bpy, mathutils
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('blend'); ap.add_argument('outdir')
ap.add_argument('--mode', default='views'); ap.add_argument('--frames', default='30')
ap.add_argument('--engine', default='CYCLES'); ap.add_argument('--samples', type=int, default=24)
ap.add_argument('--res', type=int, default=640); ap.add_argument('--views', default='front,34,profile,back')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
bpy.ops.wm.open_mainfile(filepath=a.blend)
scn = bpy.context.scene
os.makedirs(a.outdir, exist_ok=True)
scn.render.engine = a.engine
if a.engine == 'CYCLES':
    scn.cycles.device = 'CPU'
    scn.cycles.samples = a.samples
    scn.cycles.use_denoising = True
    scn.render.threads_mode = 'FIXED'; scn.render.threads = 4
scn.view_settings.view_transform = 'AgX' if 'AgX' in [v.identifier for v in scn.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
if bpy.data.objects.get('REF_floor'):
    bpy.data.objects['REF_floor'].hide_render = a.mode == 'ref'
# lights: key, fill, rim (like the arena: high key + cool fill)
world = bpy.data.worlds.new('W'); scn.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.06, 0.08, 1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
for nm, loc, en, sz in (('key', (3, -4, 6), 900, 3), ('fill', (-4, -2, 3), 300, 4), ('rim', (0, 5, 5), 600, 2)):
    ld = bpy.data.lights.new(nm, 'AREA'); ld.energy = en; ld.size = sz
    lo = bpy.data.objects.new(nm, ld); scn.collection.objects.link(lo); lo.location = loc
    lo.rotation_euler = (mathutils.Vector((0.5, 0, 1.0)) - mathutils.Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
arm = bpy.data.objects['E2A_Rig']
frames = [int(f) for f in a.frames.split(',')]
if a.mode == 'ref':
    scn.render.film_transparent = True
    scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
    scn.render.resolution_percentage = 50
    for f in frames:
        scn.frame_set(f)
        scn.render.filepath = os.path.join(a.outdir, f'ref_{f:04d}.png')
        bpy.ops.render.render(write_still=True)
else:
    cam_d = bpy.data.cameras.new('views'); cam_d.lens = 70
    cam = bpy.data.objects.new('views', cam_d); scn.collection.objects.link(cam); scn.camera = cam
    scn.render.resolution_x, scn.render.resolution_y = a.res, int(a.res * 1.4)
    scn.render.resolution_percentage = 100
    yaw_of = {'front': 0, '34': 45, 'profile': 90, 'back': 180, 'profile_r': -90, '34r': -45}
    for f in frames:
        scn.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        hips = arm.matrix_world @ arm.pose.bones['hips'].head
        chest = arm.pose.bones['chest'].matrix
        # facing of the pelvis (bone -Z rest = forward? use the rest forward -y carried by the hips)
        Rh = np.array(arm.pose.bones['hips'].matrix)[:3, :3]
        Rr = np.array(arm.data.bones['hips'].matrix_local)[:3, :3]
        fwd = (Rh @ Rr.T) @ np.array([0, -1.0, 0])
        base = math.atan2(fwd[1], fwd[0])
        for v in a.views.split(','):
            ang = base + math.radians(yaw_of[v])
            d = 4.2
            tgt = mathutils.Vector((hips.x, hips.y, 0.95))
            cam.location = (tgt.x + d * math.cos(ang), tgt.y + d * math.sin(ang), 1.25)
            cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
            scn.render.filepath = os.path.join(a.outdir, f'view_{f:04d}_{v}.png')
            bpy.ops.render.render(write_still=True)
print('done')
