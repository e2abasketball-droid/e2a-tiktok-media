// E2A Realism V3.3 Gate 3: load the L2 bake export (jersey + one morph target per baked frame) with three.js GLTFLoader
// in node and check it is playable as vertex animation (morph count, vertex count, finite positions, per-frame max offset).
//   tsx scripts/qc-cloth-l2-v33.mts <jersey_morph.glb> [out.json]
import fs from 'node:fs';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import * as THREE from 'three';
const [f, out] = process.argv.slice(2);
const buf = fs.readFileSync(f);
const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
new GLTFLoader().parse(ab, '', (g) => {
  let mesh: THREE.Mesh | null = null;
  g.scene.traverse((o) => { if ((o as THREE.Mesh).isMesh && !mesh) mesh = o as THREE.Mesh; });
  if (!mesh) throw new Error('no mesh');
  const m = mesh as THREE.Mesh;
  const geo = m.geometry as THREE.BufferGeometry;
  const pos = geo.attributes.position;
  const morph = geo.morphAttributes.position ?? [];
  let finite = true, maxOff = 0;
  const perFrame: number[] = [];
  for (const a of morph) {
    let mx = 0;
    for (let i = 0; i < a.count; i++) {
      const x = a.getX(i), y = a.getY(i), z = a.getZ(i);
      if (!Number.isFinite(x + y + z)) finite = false;
      // glTF morph targets are deltas from the base positions
      mx = Math.max(mx, Math.hypot(x, y, z));
    }
    perFrame.push(Math.round(mx * 1000) / 1000);
    maxOff = Math.max(maxOff, mx);
  }
  const res = {file: f.split('/').pop(), loaded: true, mesh: m.name, vertices: pos.count, morphTargets: morph.length, morphRelative: geo.morphTargetsRelative, finite,
    maxMorphDeltaM: Math.round(maxOff * 1000) / 1000, influencesSlots: m.morphTargetInfluences?.length ?? 0, perFrameMaxDelta: perFrame};
  console.log(JSON.stringify({...res, perFrameMaxDelta: `${perFrame.length} values`}));
  if (out) fs.writeFileSync(out, JSON.stringify(res, null, 1));
}, (e) => { console.error('LOAD FAILED', e); process.exit(1); });
