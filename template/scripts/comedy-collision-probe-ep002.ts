// E2A YouTube Comedy — EP002 collision probe: prints every frame where any body proxy of a character goes below the court.
// Build + run: node_modules/.bin/esbuild scripts/comedy-collision-probe-ep002.ts --bundle --platform=node --outfile=/tmp/probe.js --loader:.json=json && node /tmp/probe.js BUCKETS|ACE|DEF1|DEF2|AND1 [t0] [t1] [all]
import * as THREE from 'three';
import {poseAt, DURATION, FPS, LOOKS} from '../src/comedy/ep002';
import type {Who} from '../src/comedy/ep002';
import {fk, D} from '../src/comedy/toon';
const P = (m: THREE.Matrix4, x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z).applyMatrix4(m);
const who = (process.argv[2] ?? 'BUCKETS') as Who;
const build = LOOKS[who].build;
const t0 = Number(process.argv[3] ?? 0), t1 = Number(process.argv[4] ?? DURATION);
for (let f = Math.round(t0 * FPS); f <= Math.round(t1 * FPS); f++) {
  const t = f / FPS;
  const p = poseAt(who, t);
  const s = fk(p, build);
  const probes: [string, number][] = [];
  // shoe: approx sole points: heel & toe (ankle frame)
  for (const a of ['lAnkle', 'rAnkle'] as const) {
    for (const z of [-0.03, 0.06, 0.15]) probes.push([a + 'sole' + z, P(s[a], 0, -0.093, z).y]);
  }
  for (const k of ['lKnee', 'rKnee'] as const) probes.push([k, P(s[k]).y - 0.07]);
  for (const k of ['lKnee', 'rKnee'] as const) probes.push([k + 'mid', P(s[k], 0, -D.shin / 2, 0).y - 0.058]);
  for (const k of ['lHip', 'rHip'] as const) probes.push([k + 'mid', P(s[k], 0, -D.thigh / 2, 0).y - 0.074]);
  // pelvis/shorts bottom: ring of radius 0.15 at y=-0.13 in root frame
  for (let i = 0; i < 8; i++) { const a = (i / 8) * Math.PI * 2; probes.push(['seat' + i, P(s.root, 0.15 * Math.cos(a), -0.13, 0.12 * Math.sin(a)).y]); }
  for (const h of ['lHand', 'rHand'] as const) probes.push([h, P(s[h], 0, -0.045, 0).y - 0.066]);
  for (const h of ['lEl', 'rEl'] as const) probes.push([h, P(s[h]).y - 0.05]);
  probes.sort((a, b) => a[1] - b[1]);
  const seat = Math.min(...probes.filter((x) => x[0].startsWith('seat')).map((x) => x[1]));
  const low = probes[0];
  const hands = Math.min(...probes.filter((x) => x[0].endsWith('Hand')).map((x) => x[1]));
  if (process.argv[5] === 'all') console.log('   hands', hands.toFixed(3));
  if (process.argv[5] === 'all' || low[1] < -0.005) console.log(t.toFixed(2), 'min', low[0], low[1].toFixed(3), 'seat', seat.toFixed(3), 'sit', p.sit.toFixed(2), 'lean', p.lean.toFixed(2));
}
