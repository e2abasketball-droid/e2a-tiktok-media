// diagnosis probe: per-foot support (weight) + body heading + pelvis velocity direction of one player (V3.3)
//   node --experimental-strip-types scripts/_probe-support33.mts <play.json> <id> <t0> <t1> [step]
import fs from 'node:fs';
import '../src/t3d/rig.ts';
import '../src/t3d/players/index.ts';
import {PLAYER3D_V32} from '../src/t3d/realism-v3-2/index.ts';
import {motionV33} from '../src/t3d/realism-v3-3/motion33.ts';
const [f, id, a, z, st] = process.argv.slice(2);
const play = JSON.parse(fs.readFileSync(f, 'utf8'));
const rig = PLAYER3D_V32[play.players.find((p: any) => p.id === id)?.team === 'X' ? 'def' : 'off'].rig;
const dt = +(st ?? 0.05);
for (let t = +a; t <= +z + 1e-9; t += dt) {
  const m = motionV33(play, id, t, rig)!;
  const m2 = motionV33(play, id, t + 0.04, rig)!;
  const p = m.body.pelvis, q = m2.body.pelvis;
  const v = Math.hypot(q[0] - p[0], q[1] - p[1]) / 0.04;
  const dir = Math.atan2(q[1] - p[1], q[0] - p[0]);
  console.log(t.toFixed(3), 'sup L', m.body.feet[0].support.toFixed(2), 'R', m.body.feet[1].support.toFixed(2),
    'h', (m.body.h * 180 / Math.PI).toFixed(0), 'vdir', (dir * 180 / Math.PI).toFixed(0), 'v', v.toFixed(2),
    'ankL', m.pose.ankle[0].map((x: number) => x.toFixed(2)).join(','), 'ankR', m.pose.ankle[1].map((x: number) => x.toFixed(2)).join(','));
}
