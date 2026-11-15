// Compare a player's pose between two versions of a play (prototype review): pelvis height, knee flexion,
// trunk lean, hip opening, denial hand height, and the closest approach between this player's arms and any
// other player's limbs/torso (arm crossings). Feet sliding / floor penetration are covered by qc-tactical3d.
//   node --experimental-strip-types scripts/pose-compare.mts <playA.json> <playB.json> <player> <t0> <t1> [report.json]
import fs from 'node:fs';
import {poseAt, PLAYER_HEIGHTS} from '../src/t3d/rig.ts';
import {sample} from '../src/tactical/play.ts';
import {FIBA} from '../src/tactical/geometry.ts';
const [fa, fb, who, t0s, t1s, out] = process.argv.slice(2);
const load = (f: string) => JSON.parse(fs.readFileSync(f, 'utf8'));
const rim = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ] as [number, number, number];
type V = number[];
const sub = (a: V, b: V) => a.map((x, i) => x - b[i]);
const dot = (a: V, b: V) => a.reduce((s, x, i) => s + x * b[i], 0);
const len = (a: V) => Math.sqrt(dot(a, a));
const angle = (a: V, b: V, c: V) => (Math.acos(Math.max(-1, Math.min(1, dot(sub(a, b), sub(c, b)) / (len(sub(a, b)) * len(sub(c, b)))))) * 180) / Math.PI;
const segDist = (p1: V, q1: V, p2: V, q2: V) => {
  // closest distance between two 3D segments (sampled; enough for a review metric)
  let m = 99;
  for (let i = 0; i <= 10; i++) for (let j = 0; j <= 10; j++) {
    const a = p1.map((x, k) => x + ((q1[k] - x) * i) / 10), b = p2.map((x, k) => x + ((q2[k] - x) * j) / 10);
    m = Math.min(m, len(sub(a, b)));
  }
  return m;
};
const limbs = (p: any) => [[p.shoulder[0], p.elbow[0]], [p.elbow[0], p.hand[0]], [p.shoulder[1], p.elbow[1]], [p.elbow[1], p.hand[1]], [p.pelvis, p.chest], [p.hip[0], p.knee[0]], [p.hip[1], p.knee[1]], [p.knee[0], p.ankle[0]], [p.knee[1], p.ankle[1]]];
const arms = (p: any) => limbs(p).slice(0, 4);
const RADIUS = 0.06 + 0.12; // arm half-thickness + torso/leg half-thickness (approx.)
const run = (f: string) => {
  const play = load(f);
  const t0 = +t0s, t1 = +t1s;
  const rows: any[] = [];
  for (let t = t0; t <= t1 + 1e-9; t += 1 / 30) {
    const s = sample(play, t);
    const ball = {holder: s.ball.holder, pos: s.ball.pos};
    const me = poseAt(play, who, t, ball, rim);
    let cross = 99, crossWho = '';
    for (const o of play.players) {
      if (o.id === who) continue;
      const po = poseAt(play, o.id, t, {holder: s.ball.holder, pos: s.ball.pos}, rim);
      for (const a of arms(me)) for (const b of limbs(po)) { const d = segDist(a[0], a[1], b[0], b[1]); if (d < cross) [cross, crossWho] = [d, o.id]; }
    }
    const kneeL = angle(me.hip[0], me.knee[0], me.ankle[0]), kneeR = angle(me.hip[1], me.knee[1], me.ankle[1]);
    rows.push({t: +t.toFixed(3), pelvisZ: +me.pelvis[2].toFixed(3), knee: +Math.min(kneeL, kneeR).toFixed(1), lean: +((me.lean * 180) / Math.PI).toFixed(1),
      hipOpen: +(((me.chestYaw - me.heading) * 180) / Math.PI).toFixed(1), handHigh: +Math.max(me.hand[0][2], me.hand[1][2]).toFixed(2),
      feetW: +len(sub(me.ankle[0], me.ankle[1])).toFixed(2), armGap: +(cross - RADIUS).toFixed(3), armGapWho: crossWho});
  }
  const minGap = rows.reduce((m, r) => (r.armGap < m.armGap ? r : m), rows[0]);
  const lock = rows.filter((r) => r.t >= 0.95 && r.t <= 1.1);
  const mean = (k: string) => +(lock.reduce((s, r) => s + r[k], 0) / Math.max(1, lock.length)).toFixed(3);
  return {play: f, atLock: {pelvisZ: mean('pelvisZ'), kneeDeg: mean('knee'), leanDeg: mean('lean'), hipOpenDeg: mean('hipOpen'), denyHandZ: mean('handHigh'), feetWidth: mean('feetW')},
    minArmGap: {m: minGap.armGap, t: minGap.t, vs: minGap.armGapWho}, armIntersections: rows.filter((r) => r.armGap < 0).length};
};
const res = {player: who, window: [+t0s, +t1s], before: run(fa), after: run(fb)};
console.log(JSON.stringify(res, null, 1));
if (out) fs.writeFileSync(out, JSON.stringify(res, null, 1));
