// E2A NBA vs EuroLeague reel (2026-11-24) — rule + body QC on the RENDERED V3.3 bodies (fork of qc-rules4.mts).
//   npx tsx scripts/qc-nbaeu.mts tactical/plays/nbaeu-<id>.json [--json out.json]
//   three-el/-nba  every sole point clear of BOTH painted lines (line width 5 cm, centred on the radius): outside the
//                  6.75 m arc (> 6.80) and inside the 7.24 m arc (< 7.19) at takeoff = 3 in EuroLeague, 2 in the NBA
//   d3s-*          X5 inside the lane all play, > 1.2 m from every attacker (no attacker within arm's length), all
//                  attackers' feet outside the lane, ball held / dribbled by O1 in the frontcourt
//   walkoff        X1 ends off the court (beyond the sideline)
//   foul-*         as 4 Rules (palm on the waist, driver restrained)
// Checks per play kind:
//   travel   the pivot foot (left) stays planted 1.6-2.9 s; after 'lift' its sole leaves the floor (> 4 cm) and lands
//            again before the ball is released (the ball never leaves the holder) = travelling
//   dribble  first dribble ends with both palms on the ball; ball held (no floor contact) for the whole hold window;
//            a floor contact AFTER the hold window = second dribble
//   line     the lowest point of the front sole is on the painted line (6.70-6.75 m from the basket centre) at takeoff
//   three    every sole point > 6.75 m at takeoff; two / ft: inside / behind the FT line
//   foul     X1's grabbing palm is within 6 cm of O1's body surface while the grab is active; no body interpenetration
// Generic: ball never inside a torso, feet never below the floor, no foot slide while planted (> 2 cm), pelvis jumps.
import fs from 'node:fs';
import type {V3} from '../src/tactical/geometry.ts';
import type {PlayWithActions} from '../src/t3d/rig.ts';
import {sample} from '../src/tactical/play.ts';
import {qconj, qmul, qrot} from '../src/t3d/skelclip.ts';
import {fkHeads, palmWorld} from '../src/t3d/realism-v3/athleteV3.ts';
import {PLAYER3D_V32} from '../src/t3d/realism-v3-2/index.ts';
import {athleteV33} from '../src/t3d/realism-v3-3/scene33.ts';
import {ballV33, ballOwner33} from '../src/t3d/realism-v3-3/motion33.ts';

const args = process.argv.slice(2);
const file = args[0];
const play = JSON.parse(fs.readFileSync(file, 'utf8')) as PlayWithActions & {marks: Record<string, number>; v33grab?: {player: string; target: string; hand: number; from: number; to: number}[]};
const kind = play.id.replace('nbaeu-', '').replace(/-(el|nba)$/, '');
import {COURTS} from '../src/tactical/geometry.ts';
const CL = COURTS[((play as {courtRules?: 'fiba' | 'nba'}).courtRules) ?? 'fiba'];
const FPS = 60;
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a: V3, k: number): V3 => [a[0] * k, a[1] * k, a[2] * k];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const rigOf = (id: string) => PLAYER3D_V32[play.players.find((p) => p.id === id)?.team === 'X' ? 'def' : 'off'].rig;
type J = Record<string, V3>;
const jointsOf = (id: string, t: number) => {
  const rig = rigOf(id);
  const b = sample(play, t).ball;
  const a = athleteV33(play, id, t, rig, {holder: b.holder, pos: b.pos, lag: sample(play, Math.max(0, t - 0.2)).ball.pos});
  const at = fkHeads(rig, a.fr.bones, a.fr.hips, a.sc);
  const by = new Map(rig.bones.map((x) => [x.name, x] as const));
  const pt = (bone: string, k: string): V3 => {
    const fb = by.get(bone)!;
    const D = qmul(a.fr.bones[bone], qconj(fb.R));
    return add(at(bone), qrot(D, mul(sub(rig.restJoints[k], fb.head), a.sc)));
  };
  const j: J = {pelvis: at('hips'), chest: at('chest'), head: at('head')};
  for (const s of ['L', 'R']) {
    j[`an${s}`] = at(`foot.${s}`);
    j[`heel${s}`] = pt(`foot.${s}`, `heel${s}`);
    j[`ball${s}`] = pt(`foot.${s}`, `ball${s}`);
    j[`toe${s}`] = add(j[`ball${s}`], mul(sub(j[`ball${s}`], j[`heel${s}`]), 0.35));
    j[`palm${s}`] = palmWorld(rig, a.fr.bones, a.fr.hips, a.sc, s as 'L' | 'R');
    j[`hip${s}`] = at(`thigh.${s}`);
  }
  return {j, src: a.source};
};
const rows: {t: number; ball: V3; owner: string | null; P: Record<string, J>}[] = [];
for (let f = 0; f <= Math.round(play.duration * FPS); f++) {
  const t = f / FPS;
  const P: Record<string, J> = {};
  for (const p of play.players) P[p.id] = jointsOf(p.id, t).j;
  rows.push({t, ball: ballV33(play, t), owner: ballOwner33(play, t), P});
}
const srcs = Object.fromEntries(play.players.map((p) => [p.id, jointsOf(p.id, 1).src]));
const res: {check: string; ok: boolean; info: string}[] = [];
const ck = (check: string, ok: boolean, info: string) => res.push({check, ok, info});
const M = play.marks;
const sole = (j: J, s: 'L' | 'R') => Math.min(j[`heel${s}`][2], j[`ball${s}`][2]);
const flat = (p: V3): [number, number] => [p[0], p[1]];
const d2 = (a: [number, number], b: [number, number]) => Math.hypot(a[0] - b[0], a[1] - b[1]);
const B: [number, number] = [0, 1.575];
ck('all players on V3.3 bodies', Object.values(srcs).every((s) => s !== 'legacy-fallback'), JSON.stringify(srcs));
// generic: feet not below the floor, ball not inside torso of anyone
let minSole = 9;
let ballIn = 0;
for (const r of rows) for (const id in r.P) {
  minSole = Math.min(minSole, sole(r.P[id], 'L'), sole(r.P[id], 'R'));
  const c = r.P[id].chest, pv = r.P[id].pelvis;
  const mid: V3 = mul(add(c, pv), 0.5);
  if (Math.hypot(r.ball[0] - mid[0], r.ball[1] - mid[1]) < 0.17 && r.ball[2] > pv[2] - 0.1 && r.ball[2] < c[2] + 0.1) ballIn++;
}
ck('soles not below the floor (>-2 cm)', minSole > -0.02, `min sole z ${r3(minSole)} m`);
ck('ball never inside a torso', ballIn === 0, `${ballIn} samples`);
// interpenetration between two players (pelvis/chest distance)
if (play.players.length > 1) {
  let minD = 9;
  for (const r of rows) {
    const ids = Object.keys(r.P);
    for (let i = 0; i < ids.length; i++) for (let k = i + 1; k < ids.length; k++) {
      for (const a of ['pelvis', 'chest']) minD = Math.min(minD, d2(flat(r.P[ids[i]][a]), flat(r.P[ids[k]][a])));
    }
  }
  ck('bodies never overlap (torso centres > 0.42 m)', minD > 0.42, `min torso distance ${r3(minD)} m`);
}
const at = (t: number) => rows[Math.min(rows.length - 1, Math.round(t * FPS))];
if (kind === 'travel') {
  // pivot = LEFT foot (L) planted from the pivot to the lift: horizontal slide of the ball of the foot
  const a0 = at(M.pivot0 + 0.05).P.O1.ballL, a1 = at(M.lift - 0.05).P.O1.ballL;
  ck('pivot foot (L) stays on the floor during the legal pivot', Math.max(...rows.filter((r) => r.t > M.pivot0 && r.t < M.lift - 0.05).map((r) => sole(r.P.O1, 'L'))) < 0.035, `max L sole z ${r3(Math.max(...rows.filter((r) => r.t > M.pivot0 && r.t < M.lift - 0.05).map((r) => sole(r.P.O1, 'L'))))}`);
  ck('pivot foot ball does not slide (< 4 cm) while pivoting', d2(flat(a0), flat(a1)) < 0.04, `${r3(d2(flat(a0), flat(a1)))} m`);
  const up = Math.max(...rows.filter((r) => r.t > M.lift && r.t < M.land).map((r) => sole(r.P.O1, 'L')));
  ck('pivot foot LIFTED (> 4 cm)', up > 0.04, `max sole ${r3(up)} m`);
  const back = sole(at(M.land + 0.1).P.O1, 'L');
  ck('pivot foot back DOWN', back < 0.02, `sole ${r3(back)} m at land+0.1`);
  const moved = d2(flat(at(M.land + 0.15).P.O1.anL), flat(at(M.lift - 0.05).P.O1.anL));
  ck('pivot foot relocated (visible, > 15 cm)', moved > 0.15, `${r3(moved)} m`);
  ck('ball held by O1 through the landing (no pass / shot)', rows.filter((r) => r.t > M.catch + 0.2 && r.t < play.duration - 0.02).every((r) => r.owner === 'O1'), 'owner O1');
  const rLift = Math.max(...rows.filter((r) => r.t > M.lift && r.t < M.land + 0.3).map((r) => sole(r.P.O1, 'R')));
  ck('right foot stays down during the illegal step', rLift < 0.03, `max R sole ${r3(rLift)}`);
}
if (kind === 'dribble') {
  const hold = rows.filter((r) => r.t > M.pickup + 0.1 && r.t < M.hold1);
  const minZ = Math.min(...hold.map((r) => r.ball[2]));
  ck('ball held (never near the floor) during the hold', minZ > 0.6, `min ball z ${r3(minZ)} m`);
  const both = hold.filter((r) => len(sub(r.P.O1.palmL, r.ball)) < 0.2 && len(sub(r.P.O1.palmR, r.ball)) < 0.2).length / hold.length;
  ck('both hands on the ball while held (> 90 %)', both > 0.9, `${Math.round(both * 100)} %`);
  const floor2 = rows.find((r) => r.t > M.hold1 && r.ball[2] < 0.2);
  ck('second dribble reaches the floor', !!floor2, floor2 ? `floor at ${r3(floor2.t)} s` : 'none');
  let maxStep = 0;
  for (let i = 1; i < rows.length - 2; i++) maxStep = Math.max(maxStep, len(sub(rows[i].ball, rows[i - 1].ball)));
  ck('ball continuous (< 0.25 m per 1/60 s)', maxStep < 0.25, `max ${r3(maxStep)} m`);
}
if (['ft', 'two', 'three', 'line'].includes(kind)) {
  // takeoff = last frame before release with both soles down
  const rel = M.release;
  const pre = rows.filter((r) => r.t < rel && r.t > rel - 0.7 && sole(r.P.O1, 'L') < 0.02 && sole(r.P.O1, 'R') < 0.02);
  const r = pre[pre.length - 1] ?? at(rel - 0.4);
  const pts = (['L', 'R'] as const).flatMap((s) => [r.P.O1[`heel${s}`], r.P.O1[`ball${s}`], r.P.O1[`toe${s}`]]).map((p) => d2(flat(p), B));
  const near = Math.min(...pts), far = Math.max(...pts);
  if (kind === 'three') ck('both feet behind the arc (> 6.75 m) at takeoff', near > 6.75, `nearest sole ${r3(near)} m`);
  if (kind === 'two') ck('both feet inside the arc (< 6.70 m) at takeoff', far < 6.7, `farthest sole ${r3(far)} m`);
  if (kind === 'line') ck('front toe ON the line (6.70-6.75 m) at takeoff', near >= 6.69 && near <= 6.76, `nearest sole ${r3(near)} m, farthest ${r3(far)} m`);
  if (kind === 'ft') {
    const minY = Math.min(...(['L', 'R'] as const).flatMap((s) => [r.P.O1[`toe${s}`][1], r.P.O1[`ball${s}`][1]]));
    ck('feet behind the free-throw line (y > 5.80 + 0.05)', minY > 5.85, `min toe y ${r3(minY)} m`);
  }
  const mk = at(M.make);
  ck('ball through the rim at make', d2(flat(mk.ball), B) < 0.2 && mk.ball[2] < 3.1 && mk.ball[2] > 2.3, `ball ${mk.ball.map(r3)}`);
  ck('takeoff frame found', pre.length > 0, `t ${r3(r.t)} s`);
}
if (kind === 'foul') {
  const g = play.v33grab![0];
  const act = rows.filter((r) => r.t > g.from + 0.2 && r.t < g.to - 0.2);
  const gap = act.map((r) => {
    const palm = g.hand === 0 ? r.P.X1.palmL : r.P.X1.palmR;
    const pv = r.P.O1.pelvis; void pv;
    return Math.abs(Math.hypot(palm[0] - pv[0], palm[1] - pv[1]) - 0.2);
  });
  ck('grabbing palm on O1 waist surface (|d-0.20| < 0.07 m)', Math.max(...gap) < 0.07, `max ${r3(Math.max(...gap))} m`);
  const sp = (t: number) => d2(flat(at(t + 0.05).P.O1.pelvis), flat(at(t - 0.05).P.O1.pelvis)) / 0.1;
  ck('O1 restrained (speed < 0.4 m/s after stopped)', sp(M.stopped + 0.2) < 0.4, `${r3(sp(M.stopped + 0.2))} m/s`);
}
if (kind === 'three') {
  const rel = M.release;
  const pre = rows.filter((r) => r.t < rel && r.t > rel - 0.7 && sole(r.P.O1, 'L') < 0.02 && sole(r.P.O1, 'R') < 0.02);
  const r = pre[pre.length - 1] ?? at(rel - 0.4);
  const pts = (['L', 'R'] as const).flatMap((s) => [r.P.O1[`heel${s}`], r.P.O1[`ball${s}`], r.P.O1[`toe${s}`]]).map((p) => d2(flat(p), B));
  const near = Math.min(...pts), far = Math.max(...pts);
  ck('takeoff frame found', pre.length > 0, `t ${r3(r.t)} s`);
  ck('EuroLeague: every sole point outside the 6.75 m line (> 6.80 incl. paint) = 3', near > 6.8, `nearest ${r3(near)} m`);
  ck('NBA: every sole point inside the 7.24 m line (< 7.19 incl. paint) = 2', far < 7.19, `farthest ${r3(far)} m`);
  const mk = at(M.make);
  ck('ball through the rim at make', d2(flat(mk.ball), B) < 0.2 && mk.ball[2] < 3.1 && mk.ball[2] > 2.3, `ball ${mk.ball.map(r3)}`);
  const air = rows.filter((r) => r.t > M.release + 0.15 && r.t < M.make - 0.1);
  ck('ball released and in flight (above 3.05 m mid-flight)', Math.max(...air.map((r) => r.ball[2])) > 3.5, `apex ${r3(Math.max(...air.map((r) => r.ball[2])))} m`);
}
if (kind === 'd3s') {
  const inLane = (p: V3, m = 0) => Math.abs(p[0]) < CL.keyHalfW - m && p[1] < CL.ftY - m && p[1] > CL.baseY;
  ck('X5 pelvis inside the lane the whole play', rows.every((r) => inLane(r.P.X5.pelvis, 0.2)), `x ${r3(Math.max(...rows.map((r) => Math.abs(r.P.X5.pelvis[0]))))} max`);
  let minD = 9;
  for (const r of rows) for (const id of ['O1', 'O2', 'O3', 'O4', 'O5']) minD = Math.min(minD, d2(flat(r.P.X5.pelvis), flat(r.P[id].pelvis)), d2(flat(r.P.X5.palmL), flat(r.P[id].pelvis)), d2(flat(r.P.X5.palmR), flat(r.P[id].pelvis)));
  ck('X5 not within arm\'s length of any attacker (> 1.2 m, hands included)', minD > 1.2, `min ${r3(minD)} m`);
  const offIn = rows.filter((r) => ['O1', 'O2', 'O3', 'O4', 'O5'].some((id) => (['L', 'R'] as const).some((s) => inLane(r.P[id][`ball${s}`]) || inLane(r.P[id][`heel${s}`])))).length;
  ck('no attacker foot in the lane (offensive 3 s not involved)', offIn === 0, `${offIn} samples`);
  ck('only O1 touches the ball (dribble: O1 or the floor bounce) = team control', rows.every((r) => r.owner === 'O1' || r.owner === null), [...new Set(rows.map((r) => r.owner))].join(','));
  ck('ball in the frontcourt', rows.every((r) => r.ball[1] < 14 && Math.abs(r.ball[0]) < 7.5), 'ok');
  const cnt = rows.filter((r) => r.t >= M.count0 && r.t <= M.count3);
  ck('3-second count window fully covered by the play', cnt.length >= Math.round(3 * FPS), `${r3(cnt.length / FPS)} s`);
}
if (kind === 'walkoff') {
  const e = rows[rows.length - 1].P.X1.pelvis;
  ck('X1 ends off the court (beyond the sideline)', Math.abs(e[0]) > 7.62, `x ${r3(e[0])}`);
}
const ok = res.every((x) => x.ok);
for (const x of res) console.log(`${x.ok ? 'PASS' : 'FAIL'}  ${x.check}  (${x.info})`);
console.log(`${play.id}: ${ok ? 'PASS' : 'FAIL'} ${res.filter((x) => x.ok).length}/${res.length}`);
if (args.includes('--json')) fs.writeFileSync(args[args.indexOf('--json') + 1], JSON.stringify({id: play.id, ok, res}, null, 1));
if (args.includes('--dump')) fs.writeFileSync(args[args.indexOf('--dump') + 1], JSON.stringify(rows.filter((_, i) => i % 2 === 0).map((r) => ({t: r3(r.t), ball: r.ball.map(r3), owner: r.owner, P: Object.fromEntries(Object.entries(r.P).map(([k, j]) => [k, Object.fromEntries(Object.entries(j).map(([n, v]) => [n, v.map(r3)]))]))}))));
process.exitCode = ok ? 0 : 1;
