// E2A Tactical — dump a play as a 30 fps table (2026-11-20, master prompt 3D sec. 4.2 "2D pass first").
// One row per video frame of PLAY time: every player's floor position, body facing (rad, play axes), chest yaw of the
// rendered rig, the ball (x, y, z), its owner and its explicit phase (play.ts ballPhase). Same pure functions as the
// render, so the 2D pass (tools/tactical_2d.py), the 3D scene and the QC read the same events and timings.
//   node --experimental-strip-types scripts/play-dump.mts tactical/plays/<id>.json out.json [--fps 30]
import fs from 'node:fs';
import {ballPhase, sample, stateOf} from '../src/tactical/play.ts';
import {poseAt} from '../src/t3d/rig.ts';
import type {V3} from '../src/tactical/geometry.ts';

const [, , src, out] = process.argv;
const fps = Number(process.argv[process.argv.indexOf('--fps') + 1]) || 30;
const p = JSON.parse(fs.readFileSync(src, 'utf8'));
const RIM: V3 = [0, 1.575, 3.05];
const rows: unknown[] = [];
for (let f = 0; f <= Math.round(p.duration * fps); f++) {
  const t = f / fps;
  const fr = sample(p, t);
  const ph = ballPhase(p, t);
  const players: Record<string, unknown> = {};
  for (const pl of p.players) {
    const st = stateOf(p, pl.id, t);
    const ps = poseAt(p, pl.id, t, {holder: fr.ball.holder, pos: fr.ball.pos as V3}, RIM);
    players[pl.id] = {x: +st.pos[0].toFixed(3), y: +st.pos[1].toFixed(3), facing: +st.facing.toFixed(3), chestYaw: +ps.chestYaw.toFixed(3), speed: +st.speed.toFixed(2)};
  }
  rows.push({f, t: +t.toFixed(4), ball: fr.ball.pos.map((v: number) => +v.toFixed(3)), holder: fr.ball.holder ?? null, phase: ph.phase, owner: ph.owner ?? null, players});
}
fs.writeFileSync(out, JSON.stringify({id: p.id, title: p.title, fps, duration: p.duration, marks: p.marks, players: p.players, rows}));
console.log(`${out}: ${rows.length} frames of ${p.id}`);
