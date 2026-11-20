// Pose dump (2026-11-20, Double Drag Blender pilot): the rig joints of chosen players + the ball, per frame, for an
// external check / render (tools/blender/catch_pilot.py). Same pure functions as the 3D render and the QC.
//   node --experimental-strip-types scripts/pose-dump.mts tactical/plays/<id>.json out.json t0 t1 O5,X5[,..] [--fps 30]
import fs from 'node:fs';
import {FIBA} from '../src/tactical/geometry.ts';
import {sample} from '../src/tactical/play.ts';
import {poseAt} from '../src/t3d/rig.ts';
const [pf, out, a, b, ids] = process.argv.slice(2);
const fi = process.argv.indexOf('--fps');
const fps = fi > 0 ? Number(process.argv[fi + 1]) : 30;
const play = JSON.parse(fs.readFileSync(pf, 'utf8'));
const RIM: [number, number, number] = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const rows = [];
for (let f = Math.round(+a * fps); f <= Math.round(+b * fps); f++) {
  const t = f / fps;
  const s = sample(play, t);
  const players: Record<string, unknown> = {};
  for (const id of ids.split(',')) {
    const p = poseAt(play, id, t, {holder: s.ball.holder, pos: s.ball.pos}, RIM) as unknown as Record<string, unknown>;
    const {dims, ...rest} = p;
    players[id] = {...rest, dims};
  }
  rows.push({f, t, ball: s.ball.pos, holder: s.ball.holder ?? null, phase: (s.ball as {phase?: string}).phase ?? null, players});
}
fs.writeFileSync(out, JSON.stringify({id: play.id, fps, rows}));
console.log(`${out}: ${rows.length} frames`);
