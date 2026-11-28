// E2A YouTube Comedy — EP002 ball probe: ball under the floor, or passing through a head / torso / elbow.
// node_modules/.bin/esbuild scripts/comedy-ball-probe-ep002.ts --bundle --platform=node --outfile=/tmp/bp.js --loader:.json=json && node /tmp/bp.js
import * as THREE from 'three';
import {poseAt, ballAt, CAST, LOOKS, FPS, DURATION} from '../src/comedy/ep002';
import {fk} from '../src/comedy/toon';
const bones = ['head', 'spine', 'lHand', 'rHand', 'lEl', 'rEl', 'root'] as const;
for (let f = 0; f <= DURATION * FPS; f++) {
  const t = f / FPS; const b = ballAt(t).pos;
  if (b.y < 0.115) console.log(t.toFixed(2), 'ball below floor', b.y.toFixed(3));
  for (const w of CAST) {
    const s = fk(poseAt(w, t), LOOKS[w].build);
    for (const k of bones) {
      const p = new THREE.Vector3().setFromMatrixPosition(s[k]);
      const d = p.distanceTo(b);
      const lim = k === 'head' ? 0.36 : k === 'spine' || k === 'root' ? 0.2 : 0.14;
      if (d < lim && !(k.endsWith('Hand'))) console.log(t.toFixed(2), w, k, d.toFixed(2));
    }
  }
}
