// QC: 4 Basketball Rules, Part 2 (2026-11-25). Checks every rule moment on the RENDERED V3.3 bodies (motionV33 /
// ballV33), at the play marks the edit uses. FIBA Official Basketball Rules: Art. 28 (8 s), 30 (backcourt),
// 26 (3 s), 31 (goaltending). Court: offence attacks y = 0; full court half line y = 14 (line belongs to the backcourt,
// 5 cm wide: 13.975..14.025); restricted area |x| <= 2.45, y <= 5.80 (lines included); ring 3.05 m, r 0.225.
// Run: npx tsx scripts/qc-rules4p2.mts   (exit 1 on any FAIL)
import fs from 'node:fs';
import {motionV33, ballV33, ballOwner33} from '../src/t3d/realism-v3-3/motion33.ts';
import {PLAYER3D_V32} from '../src/t3d/realism-v3-2/index.ts';

const load = (k: string) => JSON.parse(fs.readFileSync(`tactical/plays/rules4p2-${k}.json`, 'utf8'));
const rig = (play: any, id: string) => PLAYER3D_V32[play.players.find((p: any) => p.id === id)?.team === 'X' ? 'def' : 'off'].rig;
const BR = 0.12, HEEL = 0.06, TIP = 0.07, LINE0 = 13.975, LINE1 = 14.025;
let fails = 0;
const ok = (name: string, pass: boolean, info: string) => {
  if (!pass) fails++;
  console.log(`${pass ? 'PASS' : 'FAIL'}  ${name} — ${info}`);
};
const f2 = (v: number) => v.toFixed(2);
/** floor extent of a foot along y: [toe tip, heel] (attackers move toward -y) and its lowest point */
const foot = (m: any, i: number) => ({front: Math.min(m.pose.toe[i][1], m.pose.ankle[i][1]) - TIP, back: Math.max(m.pose.toe[i][1], m.pose.ankle[i][1]) + HEEL,
  z: Math.min(m.pose.toe[i][2], m.pose.ankle[i][2]), x: [m.pose.toe[i][0], m.pose.ankle[i][0]]});

// ---------------------------------------------------------------- 8 SECONDS (Art. 28.1.2: a dribbler from back to
// frontcourt is in the frontcourt only when BOTH feet AND the ball touch it)
{
  const p = load('eight'), t = p.marks.eight;
  const b = ballV33(p, t), m = motionV33(p, 'O1', t, rig(p, 'O1'))!;
  const L = foot(m, 0), R = foot(m, 1);
  const zPrev = ballV33(p, t - 1 / 120)[2], zNext = ballV33(p, t + 1 / 120)[2];
  ok('8s: at the 8 the ball is on the floor (bounce)', b[2] < BR + 0.03 && b[2] <= zPrev && b[2] <= zNext, `ball z ${f2(b[2])} m`);
  ok('8s: the bounce is in the frontcourt (clear of the line)', b[1] < LINE0, `ball y ${f2(b[1])} < ${LINE0}`);
  ok('8s: left foot planted fully over the line', L.back < LINE0 && L.z < 0.05, `L foot y ${f2(L.front)}..${f2(L.back)}, z ${f2(L.z)}`);
  ok('8s: right foot still behind the line (backcourt)', R.front > LINE1 && R.z < 0.1, `R foot y ${f2(R.front)}..${f2(R.back)}, z ${f2(R.z)}`);
  ok('8s: the dribble is live (O1 dribbling, no hold)', ballOwner33(p, t) === 'O1', `owner ${ballOwner33(p, t)}`);
  let dmin = 9;
  for (let q = 0; q <= t; q += 1 / 60) {
    const mx = motionV33(p, 'X1', q, rig(p, 'X1'))!; const bb = ballV33(p, q);
    for (const h of mx.pose.hand) dmin = Math.min(dmin, Math.hypot(h[0] - bb[0], h[1] - bb[1], h[2] - bb[2]));
  }
  ok('8s: X1 never touches the ball', dmin > 0.3, `closest hand-ball ${f2(dmin)} m`);
}
// ---------------------------------------------------------------- BACKCOURT (Art. 30)
{
  const p = load('back'), M = p.marks;
  const m1 = motionV33(p, 'O1', M.pass, rig(p, 'O1'))!, b0 = ballV33(p, M.pass);
  const F = [foot(m1, 0), foot(m1, 1)];
  ok('back: team control in the frontcourt (O1 both feet + ball, y < 14)', F.every((x) => x.back < LINE0) && b0[1] < LINE0, `O1 feet back ${f2(Math.max(F[0].back, F[1].back))}, ball y ${f2(b0[1])}`);
  const m2 = motionV33(p, 'O2', M.catch, rig(p, 'O2'))!;
  const G = [foot(m2, 0), foot(m2, 1)];
  ok('back: O2 (team-mate) stands in the backcourt at the touch', G.every((x) => x.front > LINE1), `O2 feet front ${f2(Math.min(G[0].front, G[1].front))}`);
  const bc = ballV33(p, M.catch), hd = Math.min(...m2.pose.hand.map((h: number[]) => Math.hypot(h[0] - bc[0], h[1] - bc[1], h[2] - bc[2])));
  ok('back: O2 is the FIRST to touch it (ball in his hands at the catch)', ballOwner33(p, M.catch + 0.01) === 'O2' && hd < 0.25, `hand-ball ${f2(hd)} m`);
  let dmin = 9, crossT = -1;
  for (let q = M.pass; q <= M.catch; q += 1 / 120) {
    const bb = ballV33(p, q);
    if (crossT < 0 && bb[1] > 14) crossT = q;
    const mx = motionV33(p, 'X1', q, rig(p, 'X1'))!;
    for (const h of mx.pose.hand) dmin = Math.min(dmin, Math.hypot(h[0] - bb[0], h[1] - bb[1], h[2] - bb[2]));
    for (const id of ['O1', 'X1']) for (const ff of [0, 1]) { /* floor touch check below */ }
    if (bb[2] < BR + 0.02) dmin = -1; // the ball must not touch the floor in flight
  }
  ok('back: the pass crosses the half-court line in the air', crossT > 0, `crosses y 14 at ${f2(crossT)} s`);
  ok('back: no defender touches it, no bounce', dmin > 0.6, dmin < 0 ? 'ball touched the floor' : `closest defender hand ${f2(dmin)} m`);
}
// ---------------------------------------------------------------- OFFENSIVE 3 SECONDS (Art. 26)
{
  const p = load('three'), M = p.marks;
  const inP = (q: number[]) => Math.abs(q[0]) <= 2.45 && q[1] <= 5.8;
  let first = -1, out = false;
  for (let q = 0; q <= M.viol + 1e-6; q += 1 / 60) {
    const m = motionV33(p, 'O5', q, rig(p, 'O5'))!;
    const pts = [m.pose.toe[0], m.pose.ankle[0], m.pose.toe[1], m.pose.ankle[1]];
    if (first < 0 && pts.some(inP)) first = q;
    if (first >= 0 && !pts.some(inP)) out = true;
  }
  ok('3s: the count starts when O5 first touches the restricted area', Math.abs(first - M.enter) < 0.05, `first touch ${f2(first)} s, mark ${M.enter}`);
  ok('3s: O5 never re-establishes outside (no reset)', !out, out ? 'left the area' : 'stays in');
  ok('3s: the violation is called after MORE than 3 s', M.viol - first > 3.0, `${f2(M.viol - first)} s`);
  let live = true;
  for (let q = first; q <= M.viol; q += 1 / 30) if (ballOwner33(p, q) !== 'O1') live = false;
  ok('3s: team control of a live ball in the frontcourt all along (O1 dribbling, no shot)', live, live ? 'O1' : 'lost');
}
// ---------------------------------------------------------------- GOALTENDING (Art. 31.2.1 / 31.3.1)
{
  const p = load('goal'), M = p.marks, t = M.contact;
  const b = ballV33(p, t), b1 = ballV33(p, t + 1 / 120);
  const m = motionV33(p, 'X5', t, rig(p, 'X5'))!;
  const hd = Math.min(...m.pose.hand.map((h: number[]) => Math.hypot(h[0] - b[0], h[1] - b[1], h[2] - b[2])));
  const hand = m.pose.hand[0];
  const shooter = motionV33(p, 'O1', M.release, rig(p, 'O1'))!;
  const dShot = Math.hypot(shooter.body.pelvis[0], shooter.body.pelvis[1] - 1.575);
  ok('goal: two-point attempt (shooter inside 6.75 m)', dShot < 6.6, `${f2(dShot)} m from the basket`);
  ok('goal: X5 touches the ball at the contact mark', hd < 0.16, `palm-ball centre ${f2(hd)} m`);
  ok('goal: the ball is on its downward flight', b1[2] < b[2], `vz ${f2((b1[2] - b[2]) * 120)} m/s`);
  ok('goal: the ball is COMPLETELY above ring level', b[2] - BR > 3.05, `ball bottom ${f2(b[2] - BR)} m`);
  ok('goal: it can still enter (heading into the ring, not touched it)', Math.hypot(b[0], b[1] - 1.575) < 0.6 && ballOwner33(p, t) === 'flight', `${f2(Math.hypot(b[0], b[1] - 1.575))} m from the ring centre`);
  ok('goal: not basket interference (hand outside the ring cylinder)', Math.hypot(hand[0], hand[1] - 1.575) > 0.225, `hand ${f2(Math.hypot(hand[0], hand[1] - 1.575))} m from the ring centre`);
  const jump = Math.min(m.pose.ankle[0][2], m.pose.ankle[1][2]) - 0.08;
  ok('goal: plausible jump (ankle rise <= 0.85 m)', jump <= 0.85, `${f2(jump)} m`);
}
console.log(fails ? `\n${fails} FAIL` : '\nALL PASS');
process.exit(fails ? 1 : 0);
