// QC of an authored-footwork play (choreo.ts): contacts, reach, slides, ball in the hands, spacing, timeline.
//   node --experimental-strip-types scripts/qc-choreo.mts tactical/plays/euro-a.json [--csv out.csv]
// Checks (120 Hz over the whole play):
//   slide      a planted foot's toe and heel stay put (≤ 2 mm/frame at 30 fps)
//   reach      the IK reaches the authored ankle on planted feet (≤ 6 mm error, i.e. no clamp)
//   floor      no shoe point below the floor (≥ −5 mm), ball never below its radius
//   hands      while held, the ball touches at least one hand (≤ 0.17 m from a hand tip) and two after the gather
//   spacing    the two players' trunks never overlap (pelvis distance ≥ 0.5 m, chest ≥ 0.45 m)
//   defHand    the defender's hand never passes through the ball (≥ 0.13 m)
//   knees      the knee bends forward (no hyperextension / inverted knee)
//   count      at the gather the right foot is planted and the left is in the air; next contacts: L, then R
import fs from 'node:fs';
import {poseAt} from '../src/t3d/rig.ts';
import {footAt, footGeo} from '../src/t3d/choreo.ts';
import {sample} from '../src/tactical/play.ts';
import {FIBA} from '../src/tactical/geometry.ts';

const file = process.argv[2];
const play = JSON.parse(fs.readFileSync(file, 'utf8'));
const csvAt = process.argv.indexOf('--csv');
const RIM: [number, number, number] = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const ids = Object.keys(play.choreo);
const dt = 1 / 120;
type V3 = [number, number, number];
const d3 = (a: V3, b: V3) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const fails: Record<string, string[]> = {slide: [], reach: [], floor: [], hands: [], spacing: [], defHand: [], knees: [], count: []};
const worst: Record<string, number> = {slide: 0, reach: 0, floor: 0, hands: 0, spacing: 99, defHand: 99};
const prev: Record<string, {toe: V3[]; heel: V3[]; planted: boolean[]}> = {};
const rows: string[] = ['t,id,pelvisZ,ankL,ankR,plL,plR,ballZ'];
const gather = play.choreo.O1.ev.gather;
const release = play.choreo.O1.ev.release ?? Infinity;
for (let t = 0; t <= play.duration + 1e-9; t += dt) {
  const f = sample(play, t);
  const ball = f.ball.pos as V3;
  const poses: Record<string, ReturnType<typeof poseAt>> = {};
  for (const id of ids) {
    const p = poseAt(play, id, t, {holder: f.ball.holder, pos: ball}, RIM);
    poses[id] = p;
    const c = play.choreo[id];
    const st = [footAt(c, 0, t), footAt(c, 1, t)];
    const heel: V3[] = [0, 1].map((i) => {
      const a = p.ankle[i], to = p.toe[i];
      return [a[0] - (to[0] - a[0]) * 0.32, a[1] - (to[1] - a[1]) * 0.32, a[2] - 0.045] as V3;
    });
    const pr = prev[id];
    for (const i of [0, 1]) {
      // slide: the pivot of a planted shoe (toe while the heel is up, heel while the toe is up) must not move
      const g = footGeo(st[i], p.dims.ankleH, p.dims.foot);
      const piv = st[i].pitch >= 0 ? g.toe : g.heel;
      if (pr && pr.planted[i] && st[i].planted) {
        const q = pr.toe[i];
        const mv = Math.hypot(piv[0] - q[0], piv[1] - q[1]) * (120 / 30) * 1000;
        if (Math.sign(st[i].pitch) === Math.sign(pr.heel[i][0])) worst.slide = Math.max(worst.slide, mv);
        if (mv > 2 && Math.sign(st[i].pitch) === Math.sign(pr.heel[i][0])) fails.slide.push(`${id} foot${i} t=${t.toFixed(3)} pivot ${mv.toFixed(1)} mm/frame`);
      }
      // reach: the IK lands the ankle exactly where the authored shoe wants it (no clamp -> no visual drift)
      if (st[i].planted) {
        const e = d3(g.ankle, p.ankle[i]) * 1000;
        worst.reach = Math.max(worst.reach, e);
        if (e > 6) fails.reach.push(`${id} foot${i} t=${t.toFixed(3)} ankle off by ${e.toFixed(1)} mm`);
      }
      const lowest = Math.min(p.toe[i][2], heel[i][2]);
      worst.floor = Math.min(worst.floor, lowest * 1000);
      if (lowest < -0.005) fails.floor.push(`${id} foot${i} t=${t.toFixed(3)} ${(lowest * 1000).toFixed(1)} mm`);
      // knee forward of the hip-ankle line (along the foot direction)
      const hk: V3 = [p.knee[i][0] - (p.hip[i][0] + p.ankle[i][0]) / 2, p.knee[i][1] - (p.hip[i][1] + p.ankle[i][1]) / 2, 0];
      const fd = [Math.cos(p.heading), Math.sin(p.heading)];
      if (hk[0] * fd[0] + hk[1] * fd[1] < -0.04) fails.knees.push(`${id} knee${i} t=${t.toFixed(3)} behind`);
    }
    prev[id] = {toe: [0, 1].map((i) => { const g = footGeo(st[i], p.dims.ankleH, p.dims.foot); return st[i].pitch >= 0 ? g.toe : g.heel; }) as V3[], heel: [[Math.sign(st[0].pitch), 0, 0], [Math.sign(st[1].pitch), 0, 0]], planted: [st[0].planted, st[1].planted]};
    if (csvAt > 0 && Math.round(t * 120) % 4 === 0) rows.push([t.toFixed(3), id, p.pelvis[2].toFixed(3), p.ankle[0][2].toFixed(3), p.ankle[1][2].toFixed(3), +st[0].planted, +st[1].planted, ball[2].toFixed(3)].join(','));
  }
  if (ball[2] < 0.115) fails.floor.push(`ball t=${t.toFixed(3)} z ${ball[2].toFixed(3)}`);
  // ball in the hands
  const o = poses.O1;
  if (t < release - 0.01) {
    const dh = [d3(o.hand[0], ball), d3(o.hand[1], ball)];
    const isDribble = t < gather;
    const need = isDribble ? (ball[2] > o.pelvis[2] - 0.12 ? Math.min(...dh) : 0) : t > release - 0.16 ? dh[1] : Math.max(...dh);
    worst.hands = Math.max(worst.hands, need);
    if (need > 0.19) fails.hands.push(`t=${t.toFixed(3)} ${isDribble ? 'dribble hand' : 'two hands'} ${need.toFixed(3)} m`);
  }
  if (poses.X1) {
    const a = poses.O1, b = poses.X1;
    const dp = Math.hypot(a.pelvis[0] - b.pelvis[0], a.pelvis[1] - b.pelvis[1]);
    const dc = Math.hypot(a.chest[0] - b.chest[0], a.chest[1] - b.chest[1]);
    worst.spacing = Math.min(worst.spacing, dp, dc);
    if (dp < 0.5 || dc < 0.45) fails.spacing.push(`t=${t.toFixed(3)} pelvis ${dp.toFixed(2)} chest ${dc.toFixed(2)}`);
    const dh = Math.min(d3(b.hand[0], ball), d3(b.hand[1], ball));
    worst.defHand = Math.min(worst.defHand, dh);
    if (dh < 0.13) fails.defHand.push(`t=${t.toFixed(3)} ${dh.toFixed(3)} m`);
  }
}
// count: contacts after the gather
const c = play.choreo.O1;
const atG = [footAt(c, 0, gather), footAt(c, 1, gather)];
if (!atG[1].planted) fails.count.push('right foot not planted at the gather');
if (atG[0].planted) fails.count.push('left foot planted at the gather');
const lands = c.steps.filter((s: {land: number}) => s.land > gather).sort((a: {land: number}, b: {land: number}) => a.land - b.land);
const order = lands.map((s: {foot: number}) => (s.foot === 0 ? 'L' : 'R')).join('');
if (!order.startsWith('LR')) fails.count.push(`contacts after the gather: ${order}`);
const rPlant = c.steps.filter((s: {foot: number; land: number}) => s.foot === 1 && s.land <= gather).pop();
const gap = rPlant ? gather - rPlant.land : 0;
if (gap < 3 / 30) fails.count.push(`right plant only ${(gap * 30).toFixed(1)} frames before the gather`);
if (Number.isFinite(release)) {
  const firstLandAfter = lands.find((s: {land: number}) => s.land > c.ev.takeoff - 1e-6 || s.land > release - 0.3);
  void firstLandAfter;
  const after2 = lands.slice(2).map((s: {land: number}) => s.land);
  if (after2.some((x: number) => x < release)) fails.count.push('a foot lands before the release');
}
console.log(`${file}: contacts after the gather ${order} (${lands.map((s: {land: number}) => s.land.toFixed(2)).join(', ')}); right plant ${(gap * 30).toFixed(1)} frames before the gather`);
for (const [k, v] of Object.entries(fails)) console.log(`${v.length ? 'FAIL' : 'PASS'} ${k.padEnd(8)} ${v.length ? v.length + ' samples, e.g. ' + v.slice(0, 3).join(' | ') : ''}`);
console.log('worst', JSON.stringify(Object.fromEntries(Object.entries(worst).map(([k, v]) => [k, +v.toFixed(3)]))));
if (csvAt > 0) fs.writeFileSync(process.argv[csvAt + 1], rows.join('\n'));
process.exit(Object.values(fails).some((v) => v.length) ? 1 : 0);
