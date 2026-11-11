// Tactical-accuracy tests for E2A plays (pure data + the same engine the render uses).
// Run: node --experimental-strip-types scripts/test-tactical.mts tactical/plays/*.json
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
      check(p.id, `${e.player} is open at release (nearest defender ≥ 1.8 m)`, near >= 1.8, `${near.toFixed(2)} m`);
      const fl = e.t1 - e.t0;
      check(p.id, 'shot flight 0.9–1.3 s', fl >= 0.9 && fl <= 1.3, `${fl.toFixed(2)} s`);
    } else {
      check(p.id, `${e.player} lays up within 1.5 m of the rim`, distToBasket(at) <= 1.5, `${distToBasket(at).toFixed(2)} m`);
      check(p.id, `${e.player} has space for the layup (nearest defender ≥ 1.5 m)`, near >= 1.5, `${near.toFixed(2)} m`);
    }
  }

  // screens: legal elevator doors
  for (const s of p.screens ?? []) {
    const cutAt = posAt(p.tracks[s.cutter], s.closeFrom);
    check(p.id, 'doors close only after the cutter is through (≥ 0.3 m past the line)', cutAt[1] >= s.lineY + 0.3, `cutter at y=${cutAt[1].toFixed(2)} when doors start (line ${s.lineY})`);
    const tgt = posAt(p.tracks[s.target], s.closeTo);
    check(p.id, 'screen is set before the defender arrives (≥ 0.7 m away when stationary)', s.lineY - tgt[1] >= 0.7, `${(s.lineY - tgt[1]).toFixed(2)} m`);
    // stationary from closeTo until the defender reaches them
    let vmaxS = 0;
    const contact = p.marks.contact ?? s.closeTo + 0.3;
    for (const id of s.screeners)
      for (let t = s.closeTo; t <= contact; t += DT) {
        const a = posAt(p.tracks[id], t);
        const b = posAt(p.tracks[id], t + DT);
        vmaxS = Math.max(vmaxS, d2(a, b) / DT);
      }
    check(p.id, 'screeners stationary at contact (≤ 0.1 m/s)', vmaxS <= 0.1, `${vmaxS.toFixed(3)} m/s`);
    const [a, b] = s.screeners.map((id) => posAt(p.tracks[id], s.closeTo));
    const gap = d2(a, b) - 2 * BODY;
    check(p.id, 'doors really closed (gap between screeners ≤ 0.15 m)', gap <= 0.15, `${gap.toFixed(2)} m`);
    // the chaser never passes through the closed doors
    let through = false;
    for (let t = s.closeTo; t <= p.duration; t += DT) {
      const q = posAt(p.tracks[s.target], t);
      const xs = s.screeners.map((id) => posAt(p.tracks[id], t)[0]);
      if (q[1] > s.lineY - 0.1 && q[1] < s.lineY + 0.1 && q[0] > Math.min(...xs) - BODY && q[0] < Math.max(...xs) + BODY) through = true;
    }
    check(p.id, `${s.target} has to go around the closed doors`, !through, through ? 'goes through' : 'goes around');
  }
}

// cross-play checks
const A = plays.find((p) => p.id.includes('-a-'));
const B = plays.find((p) => p.id.includes('-b-'));
if (A && B) {
  const same = A.players.every((pl) => d2(posAt(A.tracks[pl.id], 0), posAt(B.tracks[pl.id], 0)) < 1e-9);
  check('A+B', 'both cases start from the same alignment', same, same ? 'identical t=0' : 'different');
  const sameCut = [0.5, 1.0, 1.5, 2.0].every((t) => d2(posAt(A.tracks.O2, t), posAt(B.tracks.O2, t)) < 1e-9);
  check('A+B', 'the shooter runs the same cut in both cases', sameCut, sameCut ? 'identical' : 'different');
  // Case B: the screener leaves before any contact and only after the defender commits
  const leave = B.marks.x5Leaves;
  const read = B.marks.read;
  check('B', 'O5 reads the switch after X5 commits (reaction 0.15–0.5 s)', read - leave >= 0.15 && read - leave <= 0.5, `${(read - leave).toFixed(2)} s`);
  let minC = 99;
  for (let t = 0; t <= B.marks.catch; t += DT) {
    const f = sample(B, t);
    for (const x of ['X2', 'X4', 'X5']) minC = Math.min(minC, d2(f.players.O5.pos, f.players[x].pos));
  }
  check('B', 'O5 slips without screen contact (stays ≥ 0.6 m from X2/X4/X5)', minC >= 0.6, `${minC.toFixed(2)} m`);
  const fc = sample(B, B.marks.catch);
  const nearCatch = Math.min(...B.players.filter((p) => p.team === 'X').map((x) => d2(fc.players.O5.pos, fc.players[x.id].pos)));
  check('B', 'real space at the catch (nearest defender ≥ 2 m)', nearCatch >= 2, `${nearCatch.toFixed(2)} m`);
  const fs2 = sample(B, B.marks.catch);
  const onShooter = ['X2', 'X5'].filter((x) => d2(fs2.players.O2.pos, fs2.players[x].pos) < 1.6);
  check('B', 'the over-commit is visible: two defenders end up on the shooter', onShooter.length === 2, onShooter.join('+') || 'none');
  const x3Start = B.tracks.X3.find((w, i) => i > 0 && (w[1] !== B.tracks.X3[0][1] || w[2] !== B.tracks.X3[0][2]));
  const x3Move = B.tracks.X3[B.tracks.X3.indexOf(x3Start!) - 1][0];
  check('B', 'help defender X3 reacts after the pass is thrown (≥ 0.1 s)', x3Move - B.marks.pass >= 0.1, `${(x3Move - B.marks.pass).toFixed(2)} s`);
  const fa = sample(A, A.marks.release);
  const sep = d2(fa.players.O2.pos, fa.players.X2.pos);
  check('A', 'chaser is trapped: X2 ≥ 1.8 m from O2 at the release', sep >= 1.8, `${sep.toFixed(2)} m`);
}

const out = process.env.TACTICAL_REPORT;
if (out) fs.writeFileSync(out, JSON.stringify({passed: results.filter((r) => r.ok).length, failed, results}, null, 1));
console.log(`\n${results.length - failed}/${results.length} tactical checks passed`);
process.exit(failed ? 1 : 0);
