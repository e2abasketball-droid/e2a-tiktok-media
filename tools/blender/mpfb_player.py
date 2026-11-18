"""E2A 3D — MPFB entry point (prepared 2026-11-19, NOT executed yet: the session cannot download MPFB).

What it does once the owner drops the ZIPs in the project Library (/mnt/project-files/ or /mnt/project-files/uploads/):
  1. finds  mpfb-2.0.*.zip  (extension, must contain blender_manifest.toml with id = "mpfb") and
     makehuman_system_assets*.zip (asset pack, CC0); never modifies them (extracts copies to --work);
  2. registers MPFB in bpy-as-a-module (5.3): adds the extracted extension to sys.path as package `mpfb`, calls
     register(); points MPFB's user data dir at the extracted system assets;
  3. minimal test of the official samples: create a human, add the GameEngine rig, pose one bone, save .blend,
     reopen it, export .glb — every step logged with the exact exception if it fails (the log says which operator
     needs Blender Desktop, if any);
  4. writes the MPFB base mesh (vertices in MakeHuman order, metres, play coords) to --out-mesh .npz so that
     tools/blender/mh_body.py can use it instead of the ara3d-data pack (same hm08 topology: 13380 body vertices),
     and the GameEngine rig bone list for the bone map (E2A 21 bones <- GameEngine).
Then (one step, written once the npz exists because MPFB's units/axes must be checked on the real file): feed
mpfb_basemesh.npz to mh_body.build() in place of base.pack positions and rerun build_player.py (INFORME §2).

  /tmp/claude-0/venv3d/bin/python -I tools/blender/mpfb_player.py -- --work /tmp/mpfb --out-dir <dir>
"""
import argparse, glob, importlib, json, os, sys, traceback, zipfile

ap = argparse.ArgumentParser()
ap.add_argument('--search', action='append', default=['/mnt/project-files', '/mnt/project-files/uploads', '/mnt/project-files/uploads/hearth'])
ap.add_argument('--work', default='/tmp/mpfb')
ap.add_argument('--out-dir', required=True)
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
os.makedirs(a.out_dir, exist_ok=True)
LOG = []


def log(step, ok, info=''):
    LOG.append({'step': step, 'ok': ok, 'info': str(info)[:2000]})
    print(('OK   ' if ok else 'FAIL ') + f'{step}: {info}')


def find_zips():
    ext, assets = None, None
    for d in a.search:
        for z in sorted(glob.glob(os.path.join(d, '*'))):
            if not os.path.isfile(z):
                continue
            try:
                with zipfile.ZipFile(z) as zf:
                    names = zf.namelist()
                    man = [n for n in names if n.endswith('blender_manifest.toml')]
                    if man and b'id = "mpfb"' in zf.read(man[0]):
                        ext = ext or (z, man[0], zf.read(man[0]).decode('utf8', 'replace'))
                    elif any('/skins/' in n or n.startswith('skins/') for n in names):
                        assets = assets or z
            except zipfile.BadZipFile:
                continue
    return ext, assets


ext, assets = find_zips()
if not ext:
    log('find MPFB zip', False, f'no zip with blender_manifest.toml id="mpfb" in {a.search}')
    json.dump(LOG, open(os.path.join(a.out_dir, 'mpfb_log.json'), 'w'), indent=1)
    sys.exit(2)
log('find MPFB zip', True, f'{ext[0]} manifest {ext[1]}: ' + ' '.join(l for l in ext[2].splitlines() if l.startswith(('version', 'blender_version_min', 'license'))))
log('find system assets zip', bool(assets), assets or 'not found (skins/eyes/teeth will be missing; mesh and rig still work)')

import bpy  # noqa: E402
log('bpy', True, f'{bpy.app.version_string} module={getattr(bpy.app, "module", None)} binary={bpy.app.binary_path!r}')
root = os.path.join(a.work, 'ext')
os.makedirs(root, exist_ok=True)
with zipfile.ZipFile(ext[0]) as zf:
    zf.extractall(os.path.join(root, 'mpfb'))
pkg_dir = os.path.dirname(os.path.join(root, 'mpfb', ext[1]))
if pkg_dir != os.path.join(root, 'mpfb'):  # manifest inside a sub folder
    root = os.path.dirname(pkg_dir)
    name = os.path.basename(pkg_dir)
else:
    name = 'mpfb'
sys.path.insert(0, root)
try:
    mpfb = importlib.import_module(name)
    mpfb.register()
    log('register MPFB', True, name)
except Exception as e:  # noqa: BLE001
    log('register MPFB', False, traceback.format_exc())
    json.dump(LOG, open(os.path.join(a.out_dir, 'mpfb_log.json'), 'w'), indent=1)
    sys.exit(3)
if assets:
    ud = os.path.join(a.work, 'user_data')
    with zipfile.ZipFile(assets) as zf:
        zf.extractall(os.path.join(ud, 'data'))
    try:
        from importlib import import_module
        LocationService = import_module(f'{name}.services.locationservice').LocationService
        LocationService.update_user_data(ud) if hasattr(LocationService, 'update_user_data') else None
        log('system assets', True, ud)
    except Exception:  # noqa: BLE001
        log('system assets', False, traceback.format_exc())

blend = os.path.join(a.out_dir, 'mpfb_test.blend')
glb = os.path.join(a.out_dir, 'mpfb_test.glb')
try:
    HumanService = importlib.import_module(f'{name}.services.humanservice').HumanService
    basemesh = HumanService.create_human()
    log('create human', True, basemesh.name)
    try:
        HumanService.add_builtin_rig(basemesh, 'game_engine', import_weights=True)
        rig = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
        log('GameEngine rig', True, f'{rig.name}: {len(rig.data.bones)} bones')
        pb = rig.pose.bones[0]
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler[0] = 0.2
        log('pose', True, pb.name)
        json.dump([b.name for b in rig.data.bones], open(os.path.join(a.out_dir, 'game_engine_bones.json'), 'w'))
    except Exception:  # noqa: BLE001
        log('GameEngine rig / pose', False, traceback.format_exc())
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    bpy.ops.wm.open_mainfile(filepath=blend)
    log('save + reopen .blend', True, blend)
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', export_skins=True, export_yup=True)
    log('export .glb', True, f'{glb} {os.path.getsize(glb)} B')
    import numpy as np
    bm = [o for o in bpy.data.objects if o.type == 'MESH'][0]
    V = np.array([v.co[:] for v in bm.data.vertices], float)
    np.savez(os.path.join(a.out_dir, 'mpfb_basemesh.npz'), V=V)
    log('base mesh', True, f'{len(V)} vertices -> mpfb_basemesh.npz')
except Exception:  # noqa: BLE001
    log('MPFB minimal test', False, traceback.format_exc())
json.dump(LOG, open(os.path.join(a.out_dir, 'mpfb_log.json'), 'w'), indent=1)
print('log', os.path.join(a.out_dir, 'mpfb_log.json'))
