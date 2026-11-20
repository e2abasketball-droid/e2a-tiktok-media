// E2A 3D engine — contact QC for a play, WITHOUT rendering (rig poses only):
//   1. planted-foot sliding: while the simulated foot is planted, how far the RENDERED ankle (after IK) moves
//      between two video frames (mm/frame). Catches IK reach clamps and snaps, not only the footstep sim;
//   2. body interpenetration: minimum clearance between the torso capsules (pelvis->chest) of every pair of
//      players, and between their hips (thigh-top spheres); negative = bodies inside each other;
//   3. hand-ball: while a player holds the ball (not dribbling) the gap between the nearest hand and the ball
//      surface; while dribbling, the worst per-bounce contact gap of the dribbling hand.
//
//   node --experimental-strip-types scripts/qc-contact.mts tactical/plays/<id>.json [--fps 30] [--from s] [--to s] [--json out.json]
//
// Thresholds (FAIL above): slide 2 mm/frame, clearance < -0.02 m, held gap 0.06 m, dribble contact gap 0.08 m.
import fs from 'node:fs';
import {FIBA} from '../src/tactical/geometry.ts';
import type {V3} from '../src/tactical/geometry.ts';
import {dribbleSide, sample} from '../src/tactical/play.ts';
import {footTrack} from '../src/t3d/rig.ts';
import type {PlayWithActions, Pose} from '../src/t3d/rig.ts';
import {registerClip, skelPoseAt} from '../src/t3d/skelclip.ts';
import type {PlayWithSkel, SkelClip, SkelPose} from '../src/t3d/skelclip.ts';

const args = process.argv.slice(2);
const opt = (k: string, d?: string) => {
  const i = args.indexOf(k);
  return i >= 0 ? args[i + 1] : d;
};
const file = args.find((a) => a.endsWith('.json') && args[args.indexOf(a) - 1] !== '--json');
if (!file) throw new Error('usage: qc-contact.mts <play.json> [--fps 30] [--from s] [--to s] [--json out.json]');
const play = JSON.parse(fs.readFileSync(file, 'utf8')) as PlayWithSkel;
// LAB skeletal clips (opt-in per play): register the clip data the play asks for
for (const sp of Object.values(play.skel ?? {})) {
  const f = new URL(`../src/t3d/clips/${sp.clip}.json`, import.meta.url);
  if (fs.existsSync(f)) registerClip(sp.clip, JSON.parse(fs.readFileSync(f, 'utf8')) as SkelClip);
}
if (opt('--look')) for (const sp of Object.values(play.skel ?? {})) sp.look = opt('--look') as 'A' | 'B' | 'C';
const fps = Number(opt('--fps', '30'));
const t0 = Number(opt('--from', '0'));
const t1 = Number(opt('--to', String(play.duration)));
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const BALL_R = 0.121;
const ids = play.players.map((p) => p.id);

const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
/** closest distance between segments p1-q1 and p2-q2 */
const segDist = (p1: V3, q1: V3, p2: V3, q2: V3) => {
  const d1 = sub(q1, p1);
  const d2 = sub(q2, p2);
  const r = sub(p1, p2);
  const a = dot(d1, d1);
  const e = dot(d2, d2);
  const f = dot(d2, r);
  let s = 0;
  let t = 0;
  const c = dot(d1, r);
  const b = dot(d1, d2);
  const den = a * e - b * b;
  s = den > 1e-9 ? Math.max(0, Math.min(1, (b * f - c * e) / den)) : 0;
  t = (b * s + f) / e;
  if (t < 0) {
    t = 0;
    s = Math.max(0, Math.min(1, -c / a));
  } else if (t > 1) {
    t = 1;
    s = Math.max(0, Math.min(1, (b - c) / a));
  }
  const c1: V3 = [p1[0] + d1[0] * s, p1[1] + d1[1] * s, p1[2] + d1[2] * s];
  const c2: V3 = [p2[0] + d2[0] * t, p2[1] + d2[1] * t, p2[2] + d2[2] * t];
  return len(sub(c1, c2));
};

const n = Math.floor((t1 - t0) * fps + 1e-6);
const poses: Record<string, Pose[]> = {};
const skelP: Record<string, SkelPose[]> = {};
const balls: {holder?: string; pos: V3}[] = [];
for (let f = 0; f <= n; f++) {
  const t = t0 + f / fps;
  const s = sample(play, t);
  balls.push({holder: s.ball.holder, pos: s.ball.pos as V3});
  for (const id of ids) {
    const sp = skelPoseAt(play, id, t, {holder: s.ball.holder, pos: s.ball.pos as V3}, RIM);
    (poses[id] ??= []).push(sp.pose);
    (skelP[id] ??= []).push(sp);
  }
}

// ---- 1. planted-foot sliding (rendered ankle while the sim foot is planted over the whole frame interval)
type Row = {player: string; slideMaxMm: number; at: string; plantedFrames: number; clearMin: number; clearWho: string; heldGapMax: number | null; heldAt: string; dribbleGapMax: number | null};
const rows: Row[] = [];
for (const id of ids) {
  const sim = footTrack(play, id);
  const plantedBetween = (ta: number, tb: number, i: number) => {
    for (const r of sim.rows) {
      if (r.t < ta - 1e-9 || r.t > tb + 1e-9) continue;
      if (r.feet[i][2] > 1e-4) return false;
    }
    // also require the sim foot to stay put (a swing that just landed counts from its landing)
    const a = sim.rows.find((r) => r.t >= ta - 1e-9);
    const b = [...sim.rows].reverse().find((r) => r.t <= tb + 1e-9);
    return !!a && !!b && Math.hypot(a.feet[i][0] - b.feet[i][0], a.feet[i][1] - b.feet[i][1]) < 1e-4;
  };
  let slideMax = 0;
  let at = '-';
  let planted = 0;
  for (let f = 0; f < n; f++) {
    const ta = t0 + f / fps;
    const tb = ta + 1 / fps;
    for (let i = 0; i < 2; i++) {
      if (poses[id][f].airborne > 0.001 || poses[id][f + 1].airborne > 0.001) continue;
      if (skelP[id][f].w > 0 || skelP[id][f + 1].w > 0) continue; // skeletal clip: measured below on its own contacts
      if (!plantedBetween(ta, tb, i)) continue;
      planted++;
      const a = poses[id][f].ankle[i];
      const b = poses[id][f + 1].ankle[i];
      const d = Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]) * 1000;
      if (d > slideMax) [slideMax, at] = [d, `${i === 0 ? 'L' : 'R'}@${ta.toFixed(2)}s`];
    }
  }
  rows.push({player: id, slideMaxMm: slideMax, at, plantedFrames: planted, clearMin: Infinity, clearWho: '-', heldGapMax: null, heldAt: '-', dribbleGapMax: null});
}

// ---- 1b. skeletal clips: accumulated drift of the pinned ball of the foot over each stance (the foot may rotate about
// that point: pivot), per-frame slide of that point, and the ankle speed of grounded feet inside the blends
type SkelRow = {player: string; stances: number; driftMaxMm: number; driftAt: string; slideMaxMm: number; blendAnkleMm: number; window: string};
const skelRows: SkelRow[] = [];
for (const id of ids) {
  if (!skelP[id].some((x) => x.w > 0)) continue;
  const r: SkelRow = {player: id, stances: 0, driftMaxMm: 0, driftAt: '-', slideMaxMm: 0, blendAnkleMm: 0, window: ''};
  const ws = skelP[id].map((x) => x.w);
  const f0 = ws.findIndex((w) => w > 0);
  const f1 = ws.length - 1 - [...ws].reverse().findIndex((w) => w > 0);
  r.window = `${(t0 + f0 / fps).toFixed(2)}–${(t0 + f1 / fps).toFixed(2)} s`;
  for (let i = 0; i < 2; i++) {
    let start: V3 | null = null;
    let anchor: V3 | null = null;
    for (let f = 0; f <= n; f++) {
      const sp = skelP[id][f];
      const pin = sp.pins[i];
      const b = sp.balls?.[i];
      if (!pin || !b) {
        start = null;
        anchor = null;
        continue;
      }
      if (!anchor || len(sub(anchor, pin)) > 1e-6) {
        anchor = pin;
        start = b;
        r.stances++;
        continue;
      }
      const d = len(sub(b, start!)) * 1000;
      if (d > r.driftMaxMm) [r.driftMaxMm, r.driftAt] = [d, `${i ? 'R' : 'L'}@${(t0 + f / fps).toFixed(2)}s`];
      const prev = skelP[id][f - 1].balls![i];
      r.slideMaxMm = Math.max(r.slideMaxMm, len(sub(b, prev)) * 1000);
    }
    for (let f = 0; f < n; f++) {
      const a = skelP[id][f];
      const b = skelP[id][f + 1];
      if (!(a.w > 0 && a.w < 1) && !(b.w > 0 && b.w < 1)) continue;
      const A = poses[id][f].ankle[i];
      const B = poses[id][f + 1].ankle[i];
      if (A[2] > 0.16 || B[2] > 0.16) continue; // airborne foot (ankle height ~0.1 m on the floor)
      r.blendAnkleMm = Math.max(r.blendAnkleMm, len(sub(A, B)) * 1000);
    }
  }
  skelRows.push(r);
}

// ---- 2. body clearance: torso capsule (pelvis -> chest, radius 0.15·k) and hip spheres (radius 0.095·k)
let worst = {v: Infinity, who: '-'};
for (let a = 0; a < ids.length; a++)
  for (let b = a + 1; b < ids.length; b++)
    for (let f = 0; f <= n; f++) {
      const A = poses[ids[a]][f];
      const B = poses[ids[b]][f];
      const ka = A.dims.H / 2;
      const kb = B.dims.H / 2;
      let c = segDist(A.pelvis, A.chest, B.pelvis, B.chest) - 0.15 * ka - 0.15 * kb;
      for (const ha of A.hip) for (const hb of B.hip) c = Math.min(c, len(sub(ha, hb)) - 0.095 * ka - 0.095 * kb);
      const who = `${ids[a]}-${ids[b]}@${(t0 + f / fps).toFixed(2)}s`;
      for (const [id, other] of [[ids[a], ids[b]], [ids[b], ids[a]]]) {
        const r = rows.find((x) => x.player === id)!;
        if (c < r.clearMin) [r.clearMin, r.clearWho] = [c, `${other}@${(t0 + f / fps).toFixed(2)}s`];
      }
      if (c < worst.v) worst = {v: c, who};
    }

// ---- 3. hand-ball
for (const id of ids) {
  const r = rows.find((x) => x.player === id)!;
  const acts = [...(play.ball as {type: string; player?: string; from?: number; to?: number; dribble?: boolean}[])];
  const dribbleAt = (t: number) => acts.some((e) => e.type === 'hold' && e.player === id && e.dribble && t >= (e.from ?? 0) && t <= (e.to ?? 0));
  let held = -Infinity;
  let cycleMin = Infinity;
  let dribbleWorst = -Infinity;
  let rising = false;
  let prevZ = Infinity;
  for (let f = 0; f <= n; f++) {
    const t = t0 + f / fps;
    const bl = balls[f];
    if (bl.holder !== id) continue;
    const P = poses[id][f];
    const gap = Math.min(len(sub(P.hand[0], bl.pos)), len(sub(P.hand[1], bl.pos))) - BALL_R;
    if (dribbleAt(t)) {
      // one bounce cycle = from the top of the ball path to the next top; contact = the min gap in the cycle
      const z = bl.pos[2];
      if (z > prevZ) rising = true;
      if (rising && z < prevZ) {
        if (cycleMin < Infinity) dribbleWorst = Math.max(dribbleWorst, cycleMin);
        cycleMin = Infinity;
        rising = false;
      }
      // the dribbling hand (2026-11-20): a handed dribble (hand / cross) switches it; before, always the right hand
      // (a left-hand or crossover dribble read as a 0.7 m gap)
      const ev = acts.find((e) => e.type === 'hold' && e.player === id && e.dribble && t >= (e.from ?? 0) && t <= (e.to ?? 0)) as {hand?: 1 | -1; cross?: number[]} | undefined;
      const hi = ev && (ev.hand !== undefined || ev.cross?.length) && dribbleSide(ev, t) < 0 ? 0 : 1;
      cycleMin = Math.min(cycleMin, len(sub(P.hand[hi], bl.pos)) - BALL_R);
      prevZ = z;
    } else {
      // skip the 0.1 s after a catch and around shots/layups/passes (the hands travel with the ball by design)
      const busy = acts.some((e) => (e.type === 'pass' || e.type === 'shot' || e.type === 'layup') && Math.abs(t - ((e as unknown as {t0: number}).t0 ?? -9)) < 0.25);
      if (!busy && gap > held) [held, r.heldAt] = [gap, `${t.toFixed(2)}s`];
    }
  }
  r.heldGapMax = held > -Infinity ? held : null;
  r.dribbleGapMax = dribbleWorst > -Infinity ? dribbleWorst : null;
}

const fmt = (v: number | null, d = 3) => (v === null ? '-' : v.toFixed(d));
console.log(`qc-contact ${play.id}  ${t0.toFixed(2)}–${t1.toFixed(2)} s @ ${fps} fps`);
console.log('player | slide max mm/frame (where) | planted frames | min clearance m (vs) | held gap max m | dribble contact gap max m');
for (const r of rows) console.log(`${r.player} | ${r.slideMaxMm.toFixed(2)} (${r.at}) | ${r.plantedFrames} | ${r.clearMin.toFixed(3)} (${r.clearWho}) | ${fmt(r.heldGapMax)}${r.heldGapMax !== null ? ` (${r.heldAt})` : ''} | ${fmt(r.dribbleGapMax)}`);
for (const r of skelRows)
  console.log(`skeletal clip ${r.player} [${r.window}]: ${r.stances} stances, accumulated drift of the pinned ball max ${r.driftMaxMm.toFixed(2)} mm (${r.driftAt}), per-frame slide max ${r.slideMaxMm.toFixed(2)} mm, grounded ankle in blends max ${r.blendAnkleMm.toFixed(1)} mm/frame`);
const slideMax = Math.max(...rows.map((r) => r.slideMaxMm));
const held = Math.max(...rows.map((r) => r.heldGapMax ?? -1));
const drib = Math.max(...rows.map((r) => r.dribbleGapMax ?? -1));
const checks = [
  {check: 'planted feet do not slide (≤ 2 mm/frame)', ok: slideMax <= 2, value: `${slideMax.toFixed(2)} mm/frame`},
  {check: 'no body interpenetration (clearance ≥ -0.02 m)', ok: worst.v >= -0.02, value: `${worst.v.toFixed(3)} m (${worst.who})`},
  {check: 'held ball stays in the hands (gap ≤ 0.06 m)', ok: held <= 0.06, value: `${held.toFixed(3)} m`},
  {check: 'dribbling hand meets the ball every bounce (gap ≤ 0.08 m)', ok: drib <= 0.08, value: `${drib.toFixed(3)} m`},
  ...skelRows.map((r) => ({check: `skeletal clip ${r.player}: pinned ball of the foot does not drift over a stance (≤ 5 mm)`, ok: r.driftMaxMm <= 5, value: `${r.driftMaxMm.toFixed(2)} mm`})),
];
for (const c of checks) console.log(`${c.ok ? 'PASS' : 'FAIL'}  ${c.check} — ${c.value}`);
const out = opt('--json');
if (out) fs.writeFileSync(out, JSON.stringify({play: play.id, from: t0, to: t1, fps, rows, skelRows, checks}, null, 1));
process.exitCode = checks.every((c) => c.ok) ? 0 : 1;
