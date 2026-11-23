"""E2A Realism V3.3 (2026-11-22): measure the anatomical volumes of the V3.2 player GLB for the V3.3 contact solver /
QC (anat33.ts): per-bone P50 distance of the skinned body vertices to the bone axis. Trunk ellipse: see the report 01.
  python3 -I template/tools/blender/measure_anat_v33.py -- template/public/players3d/e2a_player_off_v32.glb"""
import bpy, sys, json, mathutils, statistics
glb = sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
arm = [o for o in bpy.data.objects if o.type=='ARMATURE'][0]
bones = {b.name:(arm.matrix_world@b.head_local, arm.matrix_world@b.tail_local) for b in arm.data.bones}
print('bones', sorted(bones))
meshes=[o for o in bpy.data.objects if o.type=='MESH']
print('meshes',[ (m.name,len(m.data.vertices)) for m in meshes])
regions = {'trunk':['spine','chest','hips'],'upperarmL':['upperarm.L'],'forearmL':['forearm.L'],'upperarmR':['upperarm.R'],'forearmR':['forearm.R'],'thighL':['thigh.L'],'thighR':['thigh.R'],'head':['head','neck'],'handL':['hand.L'],'handR':['hand.R']}
segs = {'trunk':('hips','chest'), 'upperarmL':('upperarm.L',None),'forearmL':('forearm.L',None),'upperarmR':('upperarm.R',None),'forearmR':('forearm.R',None),'thighL':('thigh.L',None),'thighR':('thigh.R',None),'head':('neck','head')}
def segOf(r):
    a,b = segs[r]
    if b is None: return bones[a][0], bones[a][1]
    return bones[a][0], bones[b][1]
res={}
for r,names in regions.items():
    if r not in segs: continue
    A,B = segOf(r)
    d=[]  # (u, dist)
    for m in meshes:
        gi={g.index:g.name for g in m.vertex_groups}
        mw=m.matrix_world
        for v in m.data.vertices:
            if not v.groups: continue
            g=max(v.groups,key=lambda x:x.weight)
            if gi.get(g.group) not in names or g.weight<0.5: continue
            p=mw@v.co
            ab=B-A; u=max(0,min(1,(p-A).dot(ab)/ab.length_squared)); c=A+ab*u
            d.append((u,(p-c).length,m.name))
    out={}
    for k,(lo,hi) in {'prox':(0,0.5),'dist':(0.5,1.0)}.items():
        x=sorted(q[1] for q in d if lo<=q[0]<=hi)
        if x: out[k]={'n':len(x),'p50':round(x[len(x)//2],4),'p90':round(x[int(len(x)*0.9)],4),'max':round(x[-1],4)}
    out['len']=round((B-A).length,4)
    res[r]=out
print(json.dumps(res,indent=1))
json.dump(res,open(sys.argv[-1],'w'),indent=1)
