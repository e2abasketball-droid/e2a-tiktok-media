// E2A Tactical3D — ball-only pass (RAM Screen V2, 2026-11-13). Follows the ball through every contact of a
// play at 240 Hz and checks it is continuous and always "owned": floor contact on each bounce, in the hands
// while held, out of the hands on a pass/shot, at the rim on a make, then through the net and down to the
// floor. Pure play time, so cuts and rewinds in the edit reuse exactly these positions.
//   node --experimental-strip-types scripts/test-ball.mts tactical/plays/<id>.json [...] [--trace out.csv]
import fs from 'node:fs';
import {FIBA} from '../src/tactical/geometry.ts';
import {sample} from '../src/tactical/play.ts';
import {poseAt} from '../src/t3d/rig.ts';

type V3 = [number, number, number];
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const R = 0.121;
const d3 = (a: number[], b: number[]) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const args = process.argv.slice(2);
const traceAt = args.indexOf('--trace');
const traceFile = traceAt >= 0 ? args[traceAt + 1] : '';
const files = args.filter((a, i) => a.endsWith('.json') && (traceAt < 0 || i !== traceAt + 1));
let failed = 0, total = 0;
const check = (play: string, name: string, ok: boolean, value: string) => {
  total++;
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  [${play}] ${name} — ${value}`);
};
const trace: string[] = ['play,t,x,y,z,holder,hand_gap'];

for (const f of files) {
  const p = JSON.parse(fs.readFileSync(f, 'utf8'));
  const dt = 1 / 240;
  let maxStep = 0, stepAt = 0, minZ = 9, minZAt = 0, holdGap = 0, holdWho = '';
  let prev = sample(p, 0).ball.pos as V3;
  for (let t = dt; t <= p.duration; t += dt) {
    const b = sample(p, t).ball;
    const pos = b.pos as V3;
    const step = d3(pos, prev) / dt;
    if (step > maxStep) [maxStep, stepAt] = [step, t];
    if (pos[2] < minZ) [minZ, minZAt] = [pos[2], t];
    // held (no dribble, not in flight): one of the holder's hands on the ball
    const ev = p.ball.find((e: any) => e.type === 'hold' && t >= e.from && t <= e.to);
    let gap = NaN;
    if (ev && !ev.dribble && b.holder) {
      const ps = poseAt(p, b.holder, t, {holder: b.holder, pos}, RIM);
      gap = Math.min(d3(ps.hand[0], pos), d3(ps.hand[1], pos)) - R;
      if (gap > holdGap) [holdGap, holdWho] = [gap, `${b.holder}@${t.toFixed(2)}`];
    }
    if (traceFile && Math.round(t * 240) % 8 === 0) trace.push(`${p.id},${t.toFixed(3)},${pos.map((v) => v.toFixed(3)).join(',')},${b.holder ?? ''},${Number.isNaN(gap) ? '' : gap.toFixed(3)}`);
    prev = pos;
  }
  check(p.id, 'ball path continuous: 3D speed ≤ 20 m/s at 240 Hz (no jump at any contact)', maxStep <= 20, `${maxStep.toFixed(1)} m/s @${stepAt.toFixed(3)}`);
  check(p.id, 'ball never below the floor (centre ≥ radius − 1 cm)', minZ >= R - 0.01, `${minZ.toFixed(3)} m @${minZAt.toFixed(2)}`);
  check(p.id, 'held ball: a hand on it the whole time (gap ≤ 0.10 m)', holdGap <= 0.1, `${holdGap.toFixed(3)} m ${holdWho}`);
  // bounces touch the floor
  for (const e of p.ball.filter((x: any) => x.type === 'hold' && x.dribble)) {
    let lows = 0, worst = 0;
    let z1 = sample(p, e.from).ball.pos[2], z0 = z1;
    for (let t = e.from + dt; t <= e.to; t += dt) {
      const z = sample(p, t).ball.pos[2];
      if (z1 < z0 && z1 <= z) {
        lows++;
        worst = Math.max(worst, z1 - R);
      }
      z0 = z1;
      z1 = z;
    }
    check(p.id, `dribble ${e.player} ${e.from}–${e.to}: every bounce reaches the floor (≤ 2 cm)`, lows > 0 && worst <= 0.02, `${lows} bounces, worst ${worst.toFixed(3)} m`);
  }
  // shots: at the rim at t1 on a make, then down through the net to the floor without a jump
  for (const e of p.ball.filter((x: any) => x.type === 'shot' || x.type === 'layup')) {
    const atRim = sample(p, e.t1).ball.pos as V3;
    const rimGap = Math.hypot(atRim[0] - RIM[0], atRim[1] - RIM[1]);
    if (e.make) check(p.id, `${e.type} ${e.player}: ball inside the rim at the make (≤ 0.15 m from centre)`, rimGap <= 0.15 && Math.abs(atRim[2] - RIM[2]) < 0.35, `${rimGap.toFixed(3)} m, z ${atRim[2].toFixed(2)}`);
    let low = 9;
    for (let t = e.t1; t <= Math.min(p.duration, e.t1 + 1.2); t += dt) low = Math.min(low, sample(p, t).ball.pos[2]);
    if (e.make && p.duration > e.t1 + 0.7) check(p.id, `${e.type} ${e.player}: after the net the ball reaches the floor`, low <= R + 0.03, `lowest ${low.toFixed(3)} m`);
    const rel = sample(p, e.t0 + 0.02).ball.pos as V3;
    const ps = poseAt(p, e.player, e.t0, {holder: e.player, pos: rel}, RIM);
    const relGap = Math.min(d3(ps.hand[0], rel), d3(ps.hand[1], rel)) - R;
    check(p.id, `${e.type} ${e.player}: ball leaves from the hands (≤ 0.30 m)`, relGap <= 0.3, `${relGap.toFixed(3)} m`);
  }
}
if (traceFile) fs.writeFileSync(traceFile, trace.join('\n') + '\n');
console.log(`\n${total - failed}/${total} ball checks passed`);
process.exit(failed ? 1 : 0);
