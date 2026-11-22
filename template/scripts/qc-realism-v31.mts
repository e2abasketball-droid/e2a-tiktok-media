// E2A Realism V3.1 (2026-11-22) — numeric QA of the AUTHORED V3.1 athlete (gates A-C + motion amplitude vs legacy).
//   npx tsx scripts/qc-realism-v31.mts [play.json] [--player O1] [--json out.json]
// Mesh-space measures from the solved V3.1 bones (FK of the e2a-player-v31 rig, not the engine joints):
//   foot lock   ball-of-foot drift while a foot is planted (landing -> lift), sole height (min of heel / ball points)
//   ball        palm gap of each gripping hand while held; ball jump per 1/120 s over the whole take (catch / release)
//   seek        frames 100 -> 5 -> 250 -> 100 with the memo caches emptied: bone quaternions + hips identical
//   smoothness  max joint acceleration at 120 Hz (pops), pelvis / trunk / head ranges vs the legacy engine pose
import fs from 'node:fs';
import '../src/t3d/rig.ts';
import '../src/t3d/players/index.ts';
import {FIBA} from '../src/tactical/geometry.ts';
import type {V3} from '../src/tactical/geometry.ts';
import {sample} from '../src/tactical/play.ts';
import {poseAt} from '../src/t3d/rig.ts';
import type {PlayWithActions} from '../src/t3d/rig.ts';
import {qconj, qmul, qrot} from '../src/t3d/skelclip.ts';
import {PLAYER3D_V31} from '../src/t3d/realism-v3-1/index.ts';
import {fkHeads, palmWorld} from '../src/t3d/realism-v3/athleteV3.ts';
import {clothV31, framesV31, motionV31, resetV31Caches} from '../src/t3d/realism-v3-1/motion.ts';
import {clipFor} from '../src/t3d/realism-v3-1/clips.ts';

const args = process.argv.slice(2);
const opt = (k: string, d: string) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const file = args.find((a) => a.endsWith('.json') && args[args.indexOf(a) - 1] !== '--json') ?? 'tactical/plays/realism-v3-1-onetake.json';
const play = JSON.parse(fs.readFileSync(file, 'utf8')) as PlayWithActions;
const id = opt('--player', 'O1');
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const rig = PLAYER3D_V31[play.players.find((p) => p.id === id)!.team === 'X' ? 'def' : 'off'].rig;
const clip = clipFor(play, id)!;
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const q = (xs: number[], p: number) => {
  const s = [...xs].sort((a, b) => a - b);
  return s.length ? s[Math.min(s.length - 1, Math.floor(p * (s.length - 1)))] : NaN;
};
const by = new Map(rig.bones.map((b) => [b.name, b] as const));
const footPts = (fr: ReturnType<typeof framesV31>, sc: number, s: 'L' | 'R') => {
  const at = fkHeads(rig, fr.bones, fr.hips, sc);
  const fb = by.get(`foot.${s}`)!;
  const D = qmul(fr.bones[`foot.${s}`], qconj(fb.R));
  const A = at(`foot.${s}`);
  const P = (k: string): V3 => {
    const v = qrot(D, sub(rig.restJoints[k], fb.head).map((x) => x * sc) as V3);
    return [A[0] + v[0], A[1] + v[1], A[2] + v[2]];
  };
  return {ankle: A, ball: P(`ball${s}`), heel: P(`heel${s}`)};
};
const N = Math.round(play.duration * 30);
const frames: {t: number; m: NonNullable<ReturnType<typeof motionV31>>; fr: ReturnType<typeof framesV31>}[] = [];
for (let f = 0; f <= N; f++) {
  const t = f / 30;
  const m = motionV31(play, id, t, rig)!;
  frames.push({t, m, fr: framesV31(rig, m)});
}
// ---- foot lock: per landed step, drift of the ball-of-foot point from its position 0.1 s after landing until lift
const steps = [...clip.steps].sort((a, b) => a.land - b.land);
const slides: {side: string; land: number; drift: number}[] = [];
for (const s of ['L', 'R'] as const) {
  const si = s === 'L' ? 0 : 1;
  const mine = steps.filter((x) => x.s === si);
  for (let k = 0; k < mine.length; k++) {
    const t0 = mine[k].land + (mine[k].air ? 0.16 : 0.1), t1 = (mine[k + 1]?.lift ?? play.duration) - 1 / 30;
    const pts = frames.filter((x) => x.t >= t0 && x.t <= t1);
    if (pts.length < 2) continue;
    // pivots rotate the foot on purpose: measure the ball of the foot (the pivot point)
    const ref = footPts(pts[0].fr, pts[0].m.c.scale, s).ball;
    let drift = 0;
    for (const x of pts) {
      const b = footPts(x.fr, x.m.c.scale, s).ball;
      drift = Math.max(drift, Math.hypot(b[0] - ref[0], b[1] - ref[1]));
    }
    slides.push({side: s, land: mine[k].land, drift: r3(drift)});
  }
}
// sole height while planted (support 1, flat): min of heel / ball z
const soleZ: number[] = [];
for (const x of frames) for (const s of ['L', 'R'] as const) {
  const f = x.m.feet[s === 'L' ? 0 : 1];
  if (f.support < 1 || Math.abs(f.pitch) > 0.02) continue;
  const p = footPts(x.fr, x.m.c.scale, s);
  soleZ.push(Math.min(p.ball[2], p.heel[2]) - (rig.restJoints[`ball${s}`][2] * x.m.c.scale));
}
// ---- ball: palm gaps while held, continuity at 120 Hz of the SHOWN ball (hand socket while held, engine otherwise)
const gaps: number[] = [];
const gapAt: {t: number; side: string; gap: number}[] = [];
for (const x of frames) {
  if (!x.m.ball) continue;
  for (let i = 0; i < 2; i++) {
    if (!x.m.arms.palm[i] || (x.m.arms.pw?.[i] ?? 1) < 0.99) continue;
    const p = palmWorld(rig, x.fr.bones, x.fr.hips, x.m.c.scale, i === 0 ? 'L' : 'R');
    gaps.push(len(sub(p, x.m.ball)) - 0.121);
    gapAt.push({t: r3(x.t), side: i === 0 ? 'L' : 'R', gap: r3(len(sub(p, x.m.ball)) - 0.121)});
  }
}
const shown = (t: number) => motionV31(play, id, t, rig)!.ball ?? (sample(play, t).ball.pos as V3);
let jump = {d: 0, t: 0};
const jumps: {t: number; d: number}[] = [];
for (let k = 1; k <= play.duration * 120; k++) {
  const t = k / 120;
  const d = len(sub(shown(t), shown(t - 1 / 120)));
  if (d > jump.d) jump = {d, t};
  for (const ev of [clip.ball.catchT!, clip.ball.releaseT!, clip.ball.dribble!.push, clip.ball.dribble!.catch]) if (Math.abs(t - ev) < 1 / 240 + 1e-9) jumps.push({t: r3(t), d: r3(d)});
}
// ---- smoothness: max acceleration of a few mesh joints at 120 Hz
const acc: Record<string, {a: number; t: number}> = {};
const J = (t: number) => {
  const m = motionV31(play, id, t, rig)!;
  const fr = framesV31(rig, m);
  const at = fkHeads(rig, fr.bones, fr.hips, m.c.scale);
  return {hips: fr.hips, head: at('head'), handR: at('hand.R'), handL: at('hand.L'), footL: at('foot.L'), footR: at('foot.R')};
};
const sampleT = [];
for (let k = 2; k < play.duration * 60 - 2; k++) sampleT.push(k / 60);
let prev2 = J(0), prev1 = J(1 / 60);
for (const t of sampleT) {
  const cur = J(t);
  for (const k of Object.keys(cur) as (keyof typeof cur)[]) {
    const a = len([cur[k][0] - 2 * prev1[k][0] + prev2[k][0], cur[k][1] - 2 * prev1[k][1] + prev2[k][1], cur[k][2] - 2 * prev1[k][2] + prev2[k][2]] as V3) * 3600;
    if (!acc[k] || a > acc[k].a) acc[k] = {a: r3(a), t: r3(t)};
  }
  prev2 = prev1;
  prev1 = cur;
}
// ---- seek determinism (caches emptied before each frame)
const snap = (f: number) => {
  resetV31Caches();
  const m = motionV31(play, id, f / 30, rig)!;
  const fr = framesV31(rig, m);
  const c = clothV31(play, id, f / 30, rig)!;
  return JSON.stringify({b: fr.bones, h: fr.hips, m: fr.morph, ball: m.ball ?? null, c});
};
// Gate B: the brief's order + 2 more orders; each first frame is recomputed last and compared byte for byte
const orders = [[100, 5, 250, 100], [312, 17, 180, 312], [60, 340, 222, 60]];
const seekRes = orders.map((o) => {
  const sn = o.map(snap);
  return {order: o, identical: sn[0] === sn[3]};
});
const snaps = [snap(100)];
const seekOK = seekRes.every((r) => r.identical);
// ---- amplitude vs legacy (engine pose on the same play)
const amp = (get: (t: number) => {pz: number; lean: number; head: number; armY: number; air: number}) => {
  const xs = Array.from({length: N + 1}, (_, f) => get(f / 30));
  const rng = (k: 'pz' | 'lean' | 'head' | 'armY' | 'air') => r3(Math.max(...xs.map((x) => x[k])) - Math.min(...xs.map((x) => x[k])));
  return {pelvisZRange: rng('pz'), leanRange: rng('lean'), headYawOffRange: rng('head'), handFwdRange: rng('armY'), airMax: r3(Math.max(...xs.map((x) => x.air)))};
};
const legacy = amp((t) => {
  const b = sample(play, t).ball;
  const P = poseAt(play, id, t, {holder: b.holder, pos: b.pos, lag: sample(play, Math.max(0, t - 0.2)).ball.pos}, RIM);
  const fx = [Math.cos(P.chestYaw), Math.sin(P.chestYaw)];
  return {pz: P.pelvis[2], lean: P.lean, head: Math.atan2(Math.sin(P.headYaw - P.chestYaw), Math.cos(P.headYaw - P.chestYaw)), armY: (P.hand[1][0] - P.shoulder[1][0]) * fx[0] + (P.hand[1][1] - P.shoulder[1][1]) * fx[1], air: P.airborne};
});
const v31 = amp((t) => {
  const P = motionV31(play, id, t, rig)!.pose;
  const fx = [Math.cos(P.chestYaw), Math.sin(P.chestYaw)];
  return {pz: P.pelvis[2], lean: P.lean, head: Math.atan2(Math.sin(P.headYaw - P.chestYaw), Math.cos(P.headYaw - P.chestYaw)), armY: (P.hand[1][0] - P.shoulder[1][0]) * fx[0] + (P.hand[1][1] - P.shoulder[1][1]) * fx[1], air: P.airborne};
});
const out = {
  play: play.id, player: id, rig: rig.version, frames: N + 1, jumpHeight: r3(frames[0].m.jumpH),
  footLock: {steps: slides.length, driftMax: Math.max(...slides.map((s) => s.drift)), driftMedian: q(slides.map((s) => s.drift), 0.5), worst: [...slides].sort((a, b) => b.drift - a.drift).slice(0, 4)},
  soleFlatZ: {min: r3(Math.min(...soleZ)), max: r3(Math.max(...soleZ)), median: r3(q(soleZ, 0.5)), n: soleZ.length},
  ballHeld: {palmGapMedian: r3(q(gaps, 0.5)), palmGapP95: r3(q(gaps, 0.95)), palmGapMax: r3(Math.max(...gaps)), palmGapMin: r3(Math.min(...gaps)), n: gaps.length,
    worst: [...gapAt].sort((a, b) => Math.abs(b.gap - 0.012) - Math.abs(a.gap - 0.012)).slice(0, 6)},
  ballContinuity: {maxStep120: r3(jump.d), at: r3(jump.t), atEvents: jumps},
  jointAccelMax: acc,
  seek: {orders: seekRes, identical: seekOK, bytes: snaps[0].length},
  amplitude: {legacy, v31},
};
console.log(JSON.stringify(out, null, 1));
if (args.includes('--json')) fs.writeFileSync(opt('--json', 'qc-v31.json'), JSON.stringify(out, null, 1));
