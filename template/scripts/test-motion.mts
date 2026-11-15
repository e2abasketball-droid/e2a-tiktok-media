// E2A Tactical3D — focused motion tests for the shared rig and the ball sampler (2026-11-13).
// Everything must be a pure function of PLAY time, so freezes, rewinds and out-of-order frame rendering
// (Remotion renders frames in parallel, in any order) reproduce exactly the same state.
//   node --experimental-strip-types scripts/test-motion.mts tactical/plays/<id>.json [...]
import fs from 'node:fs';
import {FIBA} from '../src/tactical/geometry.ts';
import {sample} from '../src/tactical/play.ts';
import {poseAt, PLAYER_BUILD} from '../src/t3d/rig.ts';

type V3 = [number, number, number];
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const d3 = (a: number[], b: number[]) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
let failed = 0;
let total = 0;
const check = (play: string, name: string, ok: boolean, value: string) => {
  total++;
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  [${play}] ${name} — ${value}`);
};
const poseOf = (p: any, id: string, t: number) => {
  const b = sample(p, t).ball;
  return poseAt(p, id, t, {holder: b.holder, pos: b.pos as V3}, RIM);
};

for (const f of process.argv.slice(2)) {
  const p = JSON.parse(fs.readFileSync(f, 'utf8'));
  const ids: string[] = p.players.map((x: any) => x.id);
  // 1. order independence: the same play time gives the same pose and ball, whatever was sampled before
  const ts = [0.3, p.duration * 0.5, p.duration - 0.2];
  const first = ts.map((t) => ids.map((id) => poseOf(p, id, t)));
  for (let k = 0; k < 40; k++) sample(p, ((k * 7.31) % p.duration));
  const again = [...ts].reverse().map((t) => ids.map((id) => poseOf(p, id, t))).reverse();
  let dmax = 0;
  first.forEach((row, i) => row.forEach((ps, j) => (dmax = Math.max(dmax, d3(ps.pelvis, again[i][j].pelvis), d3(ps.hand[1], again[i][j].hand[1])))));
  check(p.id, 'pose and ball are a pure function of play time (freeze / rewind / out-of-order frames)', dmax < 1e-9, `max diff ${dmax.toExponential(1)} m`);

  // 2. ball handling: dribbles leave and return to the hand, passes leave from and arrive at real hands
  let worstTop = 0, topWho = '';
  let endJump = 0, endWho = '';
  for (const e of p.ball) {
    if (e.type !== 'hold' || !e.dribble) continue;
    let prev = sample(p, e.from).ball.pos[2];
    let prev2 = prev;
    for (let t = e.from + 1 / 240; t <= e.to; t += 1 / 240) {
      const z = sample(p, t).ball.pos[2];
      if (prev > z && prev >= prev2 && prev > 0.6) {
        // top of a bounce: the dribbling (right) hand is on the ball
        const ps = poseOf(p, e.player, t - 1 / 240);
        const g = d3(ps.hand[1], sample(p, t - 1 / 240).ball.pos) - 0.121;
        if (g > worstTop) [worstTop, topWho] = [g, `${e.player}@${t.toFixed(2)}`];
      }
      prev2 = prev;
      prev = z;
    }
    const zEnd = sample(p, e.to - 1e-4).ball.pos[2];
    const next = p.ball.find((x: any) => (x.type === 'hold' ? x.from : x.t0) >= e.to - 1e-6 && x !== e);
    const zNext = next ? sample(p, e.to + 1e-3).ball.pos[2] : zEnd;
    if (Math.abs(zNext - zEnd) > endJump) [endJump, endWho] = [Math.abs(zNext - zEnd), `${e.player}@${e.to}`];
  }
  check(p.id, 'dribble: the hand is on the ball at the top of every bounce (≤ 0.12 m gap)', worstTop <= 0.12, `${worstTop.toFixed(3)} m ${topWho}`);
  check(p.id, 'dribble ends with the ball back in the hand (no vertical jump ≥ 0.2 m)', endJump < 0.2, `${endJump.toFixed(3)} m ${endWho}`);
  for (const e of p.ball.filter((x: any) => x.type === 'pass')) {
    const pa = poseOf(p, e.from, e.t0);
    const a = Math.min(d3(sample(p, e.t0 + 1e-3).ball.pos, pa.hand[0]), d3(sample(p, e.t0 + 1e-3).ball.pos, pa.hand[1]));
    const b = d3(sample(p, e.t1 - 1e-3).ball.pos, poseOf(p, e.to, e.t1).hand[0]) ;
    const b2 = d3(sample(p, e.t1 - 1e-3).ball.pos, poseOf(p, e.to, e.t1).hand[1]);
    check(p.id, `pass ${e.from}→${e.to}: leaves from the passer's hands and lands in the receiver's (≤ 0.45 m)`, a <= 0.45 && Math.min(b, b2) <= 0.45, `release ${a.toFixed(2)} m, catch ${Math.min(b, b2).toFixed(2)} m`);
  }

  // 3. bodies: landing absorbs, heads stay inside the neck's range, builds are distinct
  for (const e of p.ball.filter((x: any) => x.type === 'shot' || x.type === 'layup')) {
    // reference: the same player standing after he has recovered (1.3 s after the take-off)
    const stand = poseOf(p, e.player, Math.min(p.duration, e.t0 + 1.3)).pelvis[2];
    let low = 9;
    for (let t = e.t0 + 0.3; t < e.t0 + 1.0 && t < p.duration; t += 1 / 120) if (poseOf(p, e.player, t).airborne < 0.001) low = Math.min(low, poseOf(p, e.player, t).pelvis[2]);
    check(p.id, `${e.player} lands with bent knees after the ${e.type} (pelvis drops ≥ 6 cm below standing)`, stand - low >= 0.06, `${((stand - low) * 100).toFixed(1)} cm`);
  }
  let neck = 0;
  for (let t = 0; t <= p.duration; t += 0.05) for (const id of ids) {
    const ps = poseOf(p, id, t);
    let d = ps.headYaw - ps.chestYaw;
    while (d > Math.PI) d -= 2 * Math.PI;
    while (d < -Math.PI) d += 2 * Math.PI;
    neck = Math.max(neck, Math.abs(d));
  }
  check(p.id, 'heads turn to the ball within the neck range (≤ 1.0 rad from the chest)', neck <= 1.0, `${neck.toFixed(2)} rad`);
  const builds = ids.map((id) => PLAYER_BUILD[id] ?? 1);
  check(p.id, 'point guard and big read as different bodies (build ratio ≥ 1.15)', (PLAYER_BUILD.O5 ?? 1) / (PLAYER_BUILD.O1 ?? 1) >= 1.15, `O5/O1 ${((PLAYER_BUILD.O5 ?? 1) / (PLAYER_BUILD.O1 ?? 1)).toFixed(2)} (builds ${builds.join(',')})`);
}
console.log(`\n${total - failed}/${total} motion checks passed`);
process.exit(failed ? 1 : 0);
