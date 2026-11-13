// Tactical-accuracy tests for the STAGGER SCREEN plays (generic checks shared with test-tactical.mts
// + stagger-specific checks). Run: node --experimental-strip-types scripts/test-stagger.mts tactical/plays/stagger-*.json
// Exit 1 if any check fails. Every check prints PASS/FAIL with the measured value.
import fs from 'node:fs';
import {FIBA, isThree, distToBasket} from '../src/tactical/geometry.ts';
import type {Play} from '../src/tactical/play.ts';
import {posAt, sample} from '../src/tactical/play.ts';

const files = process.argv.slice(2).filter((f) => f.endsWith('.json'));
const plays: Play[] = files.map((f) => JSON.parse(fs.readFileSync(f, 'utf8')));
let failed = 0;
const results: {play: string; check: string; ok: boolean; value: string}[] = [];
const check = (play: string, name: string, ok: boolean, value: string) => {
  results.push({play, check: name, ok, value});
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  [${play}] ${name} — ${value}`);
};
const d2 = (a: number[], b: number[]) => Math.hypot(a[0] - b[0], a[1] - b[1]);
const DT = 1 / 120;
const BODY = 0.25; // body radius, metres

for (const p of plays) {
  const O = p.players.filter((x) => x.team === 'O');
  const X = p.players.filter((x) => x.team === 'X');
  const ids = p.players.map((x) => x.id);
  check(p.id, '5 attackers and 5 defenders', O.length === 5 && X.length === 5, `${O.length} O / ${X.length} X`);
  check(p.id, 'no duplicated players', new Set(ids).size === ids.length && ids.every((i) => p.tracks[i]), ids.join(','));

  // continuity: speed and acceleration limits (no teleporting)
  let vmax = 0;
  let vWho = '';
  let amax = 0;
  let aWho = '';
  for (const id of ids) {
    const wp = p.tracks[id];
    check(p.id, `${id} track starts at 0 and covers the play`, wp[0][0] === 0 && wp[wp.length - 1][0] >= p.duration - 1e-9, `${wp[0][0]}..${wp[wp.length - 1][0]}`);
    let prevV = [0, 0];
    for (let t = 0; t <= p.duration; t += DT) {
      const a = posAt(wp, t);
      const b = posAt(wp, t + DT);
      const v = [(b[0] - a[0]) / DT, (b[1] - a[1]) / DT];
      const s = Math.hypot(v[0], v[1]);
      if (s > vmax) [vmax, vWho] = [s, `${id}@${t.toFixed(2)}`];
      if (t > 0) {
        const acc = Math.hypot(v[0] - prevV[0], v[1] - prevV[1]) / DT;
        if (acc > amax) [amax, aWho] = [acc, `${id}@${t.toFixed(2)}`];
      }
      prevV = v;
    }
  }
  check(p.id, 'top speed ≤ 7.5 m/s (no teleports)', vmax <= 7.5, `${vmax.toFixed(2)} m/s (${vWho})`);
  check(p.id, 'acceleration ≤ 22 m/s² (no jerks)', amax <= 22, `${amax.toFixed(1)} m/s² (${aWho})`);

  // spacing: bodies never overlap
  let minGap = 99;
  let gapWho = '';
  for (let t = 0; t <= p.duration; t += 1 / 60) {
    const f = sample(p, t);
    for (let i = 0; i < ids.length; i++)
      for (let j = i + 1; j < ids.length; j++) {
        const g = d2(f.players[ids[i]].pos, f.players[ids[j]].pos);
        if (g < minGap) [minGap, gapWho] = [g, `${ids[i]}-${ids[j]}@${t.toFixed(2)}`];
      }
  }
  check(p.id, 'no two bodies overlap (≥ 0.5 m centre to centre)', minGap >= 2 * BODY - 1e-6, `${minGap.toFixed(2)} m (${gapWho})`);

  // in bounds
  const oob = ids.filter((id) => p.tracks[id].some((w) => Math.abs(w[1]) > FIBA.halfW - 0.2 || w[2] < 0.2 || w[2] > FIBA.halfL));
  check(p.id, 'everyone stays in bounds', oob.length === 0, oob.join(',') || 'ok');

  // ball: continuous, believable speeds, always with a holder or in flight
  let bmax = 0;
  let prevB = sample(p, 0).ball.pos;
  let lost = 0;
  for (let t = DT; t <= p.duration; t += DT) {
    const b = sample(p, t).ball;
    const s = Math.hypot(b.pos[0] - prevB[0], b.pos[1] - prevB[1]) / DT; // horizontal speed
    bmax = Math.max(bmax, s);
    if (!b.holder && !b.inFlight && !b.event) lost++;
    prevB = b.pos;
  }
  check(p.id, 'ball horizontal speed ≤ 15 m/s and continuous', bmax <= 15, `${bmax.toFixed(1)} m/s`);
  check(p.id, 'ball always held, in flight or dropping after a make', lost === 0, `${lost} orphan samples`);

  // passes: the lane must be open (no defender within reach of the ball while it is below 2.4 m)
  for (const e of p.ball) {
    if (e.type !== 'pass') continue;
    let near = 99;
    let who = '';
    for (let t = e.t0 + 0.04; t <= e.t1 - 0.04; t += DT) {
      const f = sample(p, t);
      if (f.ball.pos[2] > 2.4) continue;
      for (const x of X) {
        const g = d2(f.ball.pos, f.players[x.id].pos);
        if (g < near) [near, who] = [g, `${x.id}@${t.toFixed(2)}`];
      }
    }
    check(p.id, `pass ${e.from}→${e.to}: ball stays ≥ 0.6 m from every defender`, near >= 0.6, `${near.toFixed(2)} m (${who})`);
    const len = d2(posAt(p.tracks[e.from], e.t0), posAt(p.tracks[e.to], e.t1));
    const sp = len / (e.t1 - e.t0);
    check(p.id, `pass ${e.from}→${e.to}: speed 6–14 m/s`, sp >= 6 && sp <= 14, `${sp.toFixed(1)} m/s over ${len.toFixed(1)} m`);
    const rv = Math.hypot(...(sample(p, e.t1).players[e.to].vel as [number, number]));
    check(p.id, `pass ${e.from}→${e.to}: receiver under control at the catch (≤ 3.5 m/s)`, rv <= 3.5, `${rv.toFixed(2)} m/s`);
  }

  // shots
  for (const e of p.ball) {
    if (e.type !== 'shot' && e.type !== 'layup') continue;
    const f = sample(p, e.t0);
    const at = f.players[e.player].pos;
    const near = Math.min(...X.map((x) => d2(at, f.players[x.id].pos)));
    if (e.type === 'shot') {
      check(p.id, `${e.player} shoots from behind the FIBA 3-pt line`, isThree(at), `${distToBasket(at).toFixed(2)} m from the basket`);
      check(p.id, `${e.player} is open at release (nearest defender ≥ 1.6 m)`, near >= 1.6, `${near.toFixed(2)} m`);
      const fl = e.t1 - e.t0;
      check(p.id, 'shot flight 0.9–1.3 s', fl >= 0.9 && fl <= 1.3, `${fl.toFixed(2)} s`);
    } else {
      check(p.id, `${e.player} lays up within 1.5 m of the rim`, distToBasket(at) <= 1.5, `${distToBasket(at).toFixed(2)} m`);
      check(p.id, `${e.player} has space for the layup (nearest defender ≥ 0.8 m: help arrives late, not absent)`, near >= 0.8, `${near.toFixed(2)} m`);
    }
  }

  }

// ---------------- stagger-specific checks ----------------
const A = plays.find((p) => p.id.includes('-a-'))!;
const B = plays.find((p) => p.id.includes('-b-'))!;
const P = (p: Play, id: string, t: number) => posAt(p.tracks[id], t);
const closest = (p: Play, a: string, b: string, t0 = 0, t1 = p.duration) => {
  let best = 99;
  let at = 0;
  for (let t = t0; t <= t1; t += DT) {
    const g = d2(P(p, a, t), P(p, b, t));
    if (g < best) [best, at] = [g, t];
  }
  return {d: best, t: at};
};
/** first moment a reaches b's body (≤ r) after t0: the contact of a screen */
const contact = (p: Play, a: string, b: string, t0: number, r = 0.78) => {
  for (let t = t0; t <= p.duration; t += DT) {
    const g = d2(P(p, a, t), P(p, b, t));
    if (g <= r) return {d: closest(p, a, b, t, t + 0.3).d, t};
  }
  return {d: 99, t: p.duration};
};
const still = (p: Play, id: string, t0: number, t1: number) => {
  let v = 0;
  for (let t = t0; t <= t1; t += DT) v = Math.max(v, d2(P(p, id, t), P(p, id, t + DT)) / DT);
  return v;
};
if (A && B) {
  const same = A.players.every((pl) => d2(P(A, pl.id, 0), P(B, pl.id, 0)) < 1e-9);
  check('A+B', 'both cases start from the same alignment', same, same ? 'identical t=0' : 'different');
  // geometry of the stagger
  const s1 = P(A, 'O4', 1.0);
  const s2 = P(A, 'O5', 1.2);
  const gap = d2(s1, s2);
  check('A', 'screens are staggered (≥ 2.2 m apart, one higher than the other)', gap >= 2.2 && Math.abs(s2[1] - s1[1]) >= 1.5, `${gap.toFixed(2)} m apart, Δy ${(s2[1] - s1[1]).toFixed(2)} m`);
  check('A', 'not an elevator: the screeners never stand side by side (no gap < 1.2 m between them)', closest(A, 'O4', 'O5').d >= 1.2, `${closest(A, 'O4', 'O5').d.toFixed(2)} m minimum`);
  // order of use
  const u1 = closest(A, 'O2', 'O4', 0.5, 3);
  const u2 = closest(A, 'O2', 'O5', 0.5, 3);
  check('A', 'O2 uses O4 first, then O5', u1.t < u2.t, `O4 at ${u1.t.toFixed(2)} s, O5 at ${u2.t.toFixed(2)} s`);
  check('A', 'O2 runs shoulder to shoulder off both screens (≤ 1.0 m)', u1.d <= 1.0 && u2.d <= 1.0, `${u1.d.toFixed(2)} / ${u2.d.toFixed(2)} m`);
  // legal screens: stationary from set until the defender has gone by
  const h1 = contact(A, 'X2', 'O4', u1.t);
  const h2 = contact(A, 'X2', 'O5', u2.t);
  check('A', 'X2 is hit by O4, then by O5 (contact ≤ 0.75 m, no overlap)', h1.d <= 0.75 && h2.d <= 0.75 && h1.d >= 0.5 && h2.d >= 0.5 && h1.t < h2.t, `${h1.d.toFixed(2)} m @${h1.t.toFixed(2)} s, ${h2.d.toFixed(2)} m @${h2.t.toFixed(2)} s`);
  const v1 = still(A, 'O4', 0.8, h1.t + 0.3);
  const v2 = still(A, 'O5', 1.05, h2.t + 0.2);
  check('A', 'both screeners stationary at contact (legal screens, ≤ 0.1 m/s)', v1 <= 0.1 && v2 <= 0.1, `${v1.toFixed(3)} / ${v2.toFixed(3)} m/s`);
  // the defender trails: separation grows after each screen
  const sepAt = (t: number) => d2(P(A, 'O2', t), P(A, 'X2', t));
  check('A', 'X2 trails and loses ground at each screen', sepAt(h1.t + 0.25) > sepAt(h1.t - 0.25) && sepAt(h2.t + 0.2) > sepAt(h1.t + 0.25), `${sepAt(h1.t - 0.25).toFixed(2)} → ${sepAt(h1.t + 0.25).toFixed(2)} → ${sepAt(h2.t + 0.2).toFixed(2)} m`);
  check('A', 'X2 keeps chasing (never stands still between the screens)', still(A, 'X2', 1.0, 3.3) > 2, 'moving');
  // helpers occupied in A
  const x5 = closest(A, 'X5', 'O5', 2.6, 4.0);
  check('A', 'X5 stays with the rolling O5 (≤ 1.3 m) instead of helping on the shooter', x5.d <= 1.3 && d2(P(A, 'X5', A.marks.release), P(A, 'O2', A.marks.release)) > 3, `${d2(P(A, 'X5', A.marks.release), P(A, 'O2', A.marks.release)).toFixed(2)} m from O2 at the release`);
  // ---- Case B
  const lockT = B.marks.lock;
  const o2 = P(B, 'O2', lockT);
  const x2 = P(B, 'X2', lockT);
  const sB = P(B, 'O4', lockT);
  const between = d2(x2, sB) < d2(o2, sB) && x2[1] > o2[1];
  check('B', 'top-lock: X2 sits on the high side, between O2 and the first screen', between, `X2 ${d2(x2, sB).toFixed(2)} m from O4 vs O2 ${d2(o2, sB).toFixed(2)} m`);
  const reach = closest(B, 'O2', 'O4', 0, B.duration);
  check('B', 'O2 rejects BOTH screens (never closer than 1.4 m to O4, 3 m to O5)', reach.d >= 1.4 && closest(B, 'O2', 'O5').d >= 3, `${reach.d.toFixed(2)} m / ${closest(B, 'O2', 'O5').d.toFixed(2)} m`);
  check('B', 'top-lock happens before the exit attempt (lock ≥ 0.05 s before the plant)', B.marks.plant - lockT >= 0.05, `${(B.marks.plant - lockT).toFixed(2)} s`);
  const v4b = still(B, 'O4', 0.8, 2.6);
  check('B', 'screeners stay legal (stationary) while the cut happens', v4b <= 0.1 && still(B, 'O5', 1.05, 2.6) <= 0.1, `${v4b.toFixed(3)} m/s`);
  const fc = sample(B, B.marks.catch);
  const nearCatch = Math.min(...B.players.filter((p) => p.team === 'X').map((x) => d2(fc.players.O2.pos, fc.players[x.id].pos)));
  check('B', 'backdoor catch with space (nearest defender ≥ 1.4 m)', nearCatch >= 1.4, `${nearCatch.toFixed(2)} m`);
  const fl = sample(B, B.marks.release);
  const helpD = d2(fl.players.O2.pos, fl.players.X4.pos);
  check('B', 'help exists but is late (X4 within 2 m at the release, ≥ 0.8 m)', helpD <= 2 && helpD >= 0.8, `${helpD.toFixed(2)} m`);
  const x3 = Math.max(...[0, 1, 2, 2.6].map((t) => d2(P(B, 'X3', t), P(B, 'O3', t))));
  check('B', 'X3 stays home on the ball-side corner (≤ 2.2 m from O3)', x3 <= 2.2, `${x3.toFixed(2)} m max`);
  check('B', 'nobody disappears: 10 players inside the court at the finish', B.players.every((pl) => Math.abs(P(B, pl.id, B.marks.make)[0]) < FIBA.halfW), 'ok');
}

const out = process.env.TACTICAL_REPORT;
if (out) fs.writeFileSync(out, JSON.stringify({passed: results.filter((r) => r.ok).length, failed, results}, null, 1));
console.log(`\n${results.length - failed}/${results.length} tactical checks passed`);
process.exit(failed ? 1 : 0);
