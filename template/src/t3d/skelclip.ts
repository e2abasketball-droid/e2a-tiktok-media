// E2A 3D engine — LAB: skeletal clips (motion captured from a reference take, retargeted in Blender) played INSIDE a
// tactical play, for one player, opt-in per play (`play.skel = {O5: {clip: 'screen-roll-5452', look: 'C'}}`).
// Pure functions of the play time (no mixer, no state): freezing, rewinding or rendering frames in parallel gives the
// same pose. The tactical engine stays the source of game time, ball and placement:
//   * time warp by milestones: approach and roll matched by the distance run along the play track, screen hold
//     mapped linearly between the screen action and the roll action;
//   * placement: a rotation + translation per phase (approach / hold / roll) that keeps the stance foot fixed while it
//     changes (rotation about the planted ball of the foot), so the clip's own root motion is preserved;
//   * every stance of the clip is pinned in play space (ball of the foot) and the leg is solved with two-bone IK;
//   * short blends with the procedural rig (poseAt) before and after.
// Data: src/t3d/clips/<name>.json, exported by tools/blender/export_clip.py from the same numbers keyed in the .blend /
// .glb (bone world rotations in play coordinates, Blender bone convention: +Y along the bone).
import type {V3} from '../tactical/geometry.ts';
import {posAt} from '../tactical/play.ts';
import type {BallHint, PlayWithActions, Pose} from './rig.ts';
import {actionsOf, dimsFor, ik2, poseAt, PLAYER_HEIGHTS} from './rig.ts';

export type Q = [number, number, number, number]; // x y z w
export type ClipBone = {name: string; parent: string | null; head: V3; tail: V3; R: Q};
export type ClipContact = {foot: 'L' | 'R'; t0: number; t1: number; eff: [number, number] | null; point: string; pivot: [number, number] | null; anchor: V3};
export type SkelClip = {
  source: string;
  fps: number;
  t0: number;
  n: number;
  bones: ClipBone[];
  restJoints: Record<string, V3>;
  root: V3[];
  q: Record<string, Q[]>;
  joints: Record<string, V3[]>;
  heading: number[];
  chestYaw: number[];
  contacts: ClipContact[];
  milestones: Record<string, number>;
};
/** look: 'A' = clip off (procedural rig), 'B' = clip on the capsule athlete, 'C' = clip on the deformable mesh */
/** from / to: first and last clip seconds used (the rest is left to the procedural rig) */
export type SkelSpec = {clip: string; look?: 'A' | 'B' | 'C'; blend?: number; glb?: string; from?: number; to?: number};
export type PlayWithSkel = PlayWithActions & {skel?: Record<string, SkelSpec>};

const CLIPS = new Map<string, SkelClip>();
export const registerClip = (name: string, data: SkelClip) => {
  CLIPS.set(name, data);
};
export const getClip = (name: string) => CLIPS.get(name);

// ---------------------------------------------------------------- small math
const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const mul = (a: V3, s: number): V3 => [a[0] * s, a[1] * s, a[2] * s];
const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const norm = (a: V3): V3 => {
  const l = len(a);
  return l > 1e-9 ? [a[0] / l, a[1] / l, a[2] / l] : [0, 0, 1];
};
const lerp3 = (a: V3, b: V3, u: number): V3 => [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u];
const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const smooth = (x: number) => {
  const u = clamp(x);
  return u * u * (3 - 2 * u);
};
const wrap = (a: number) => {
  while (a > Math.PI) a -= 2 * Math.PI;
  while (a < -Math.PI) a += 2 * Math.PI;
  return a;
};
export const qmul = (a: Q, b: Q): Q => [
  a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1],
  a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
  a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3],
  a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2],
];
export const qconj = (q: Q): Q => [-q[0], -q[1], -q[2], q[3]];
export const qrot = (q: Q, v: V3): V3 => {
  const p = qmul(qmul(q, [v[0], v[1], v[2], 0]), qconj(q));
  return [p[0], p[1], p[2]];
};
const qnorm = (q: Q): Q => {
  const l = Math.hypot(q[0], q[1], q[2], q[3]) || 1;
  return [q[0] / l, q[1] / l, q[2] / l, q[3] / l];
};
export const qslerp = (a: Q, b: Q, u: number): Q => {
  let d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
  const bb: Q = d < 0 ? [-b[0], -b[1], -b[2], -b[3]] : b;
  d = Math.abs(d);
  if (d > 0.9995) return qnorm([a[0] + (bb[0] - a[0]) * u, a[1] + (bb[1] - a[1]) * u, a[2] + (bb[2] - a[2]) * u, a[3] + (bb[3] - a[3]) * u]);
  const th = Math.acos(d);
  const s = Math.sin(th);
  const wa = Math.sin((1 - u) * th) / s;
  const wb = Math.sin(u * th) / s;
  return [a[0] * wa + bb[0] * wb, a[1] * wa + bb[1] * wb, a[2] * wa + bb[2] * wb, a[3] * wa + bb[3] * wb];
};
const qaxis = (ax: V3, ang: number): Q => {
  const n = norm(ax);
  const s = Math.sin(ang / 2);
  return [n[0] * s, n[1] * s, n[2] * s, Math.cos(ang / 2)];
};
const qz = (ang: number): Q => [0, 0, Math.sin(ang / 2), Math.cos(ang / 2)];
/** minimal rotation taking direction a onto b */
export const qswing = (a: V3, b: V3): Q => {
  const u = norm(a);
  const v = norm(b);
  const c = dot(u, v);
  if (c < -0.99999) {
    const ax = Math.abs(u[0]) < 0.9 ? cross(u, [1, 0, 0]) : cross(u, [0, 1, 0]);
    return qaxis(ax, Math.PI);
  }
  const x = cross(u, v);
  return qnorm([x[0], x[1], x[2], 1 + c]);
};
/** quaternion of a 3x3 frame given by its columns (x, y, z) */
const qFromCols = (x: V3, y: V3, z: V3): Q => {
  const m00 = x[0], m10 = x[1], m20 = x[2], m01 = y[0], m11 = y[1], m21 = y[2], m02 = z[0], m12 = z[1], m22 = z[2];
  const tr = m00 + m11 + m22;
  let q: Q;
  if (tr > 0) {
    const s = Math.sqrt(tr + 1) * 2;
    q = [(m21 - m12) / s, (m02 - m20) / s, (m10 - m01) / s, 0.25 * s];
  } else if (m00 > m11 && m00 > m22) {
    const s = Math.sqrt(1 + m00 - m11 - m22) * 2;
    q = [0.25 * s, (m01 + m10) / s, (m02 + m20) / s, (m21 - m12) / s];
  } else if (m11 > m22) {
    const s = Math.sqrt(1 + m11 - m00 - m22) * 2;
    q = [(m01 + m10) / s, 0.25 * s, (m12 + m21) / s, (m02 - m20) / s];
  } else {
    const s = Math.sqrt(1 + m22 - m00 - m11) * 2;
    q = [(m02 + m20) / s, (m12 + m21) / s, 0.25 * s, (m10 - m01) / s];
  }
  return qnorm(q);
};
/** frame from a primary direction p and a secondary s (orthogonalised): columns (p, s, p x s) */
const twoVec = (p: V3, s: V3): Q => {
  const a = norm(p);
  const b = norm(sub(s, mul(a, dot(s, a))));
  return qFromCols(a, b, cross(a, b));
};

// ---------------------------------------------------------------- clip sampling
export type ClipFrame = {root: V3; q: Record<string, Q>; j: Record<string, V3>; heading: number; chestYaw: number};
export const sampleClip = (c: SkelClip, ct: number): ClipFrame => {
  const x = clamp((ct - c.t0) * c.fps, 0, c.n - 1);
  const i = Math.min(c.n - 2, Math.floor(x));
  const u = x - i;
  const q: Record<string, Q> = {};
  for (const b of c.bones) q[b.name] = qslerp(c.q[b.name][i], c.q[b.name][i + 1], u);
  const j: Record<string, V3> = {};
  for (const k of Object.keys(c.joints)) j[k] = lerp3(c.joints[k][i], c.joints[k][i + 1], u);
  return {root: lerp3(c.root[i], c.root[i + 1], u), q, j, heading: c.heading[i] + (c.heading[i + 1] - c.heading[i]) * u, chestYaw: c.chestYaw[i] + (c.chestYaw[i + 1] - c.chestYaw[i]) * u};
};
const clipEnd = (c: SkelClip) => c.t0 + (c.n - 1) / c.fps;

// ---------------------------------------------------------------- plan (cached per play + player)
type EngContact = {foot: 0 | 1; c0: number; c1: number; anchor: V3; ballLocal: V3};
/** swing between two pinned stances of the same foot: ankle from lift-off to touch-down (play space) */
type EngSwing = {foot: 0 | 1; c0: number; c1: number; a0: V3; a1: V3};
export type SkelPlan = {
  clip: SkelClip;
  spec: SkelSpec;
  knots: [number, number][]; // [engine t, clip t], increasing
  eStart: number;
  eEnd: number;
  blend: number;
  thetaAt: (ct: number) => number;
  tauAt: (ct: number) => V3;
  contacts: EngContact[];
  swings: EngSwing[];
  info: Record<string, number | string>;
};
const planCache = new WeakMap<object, Map<string, SkelPlan | null>>();

const xy = (v: V3): [number, number] => [v[0], v[1]];
const rotZ = (v: V3, a: number): V3 => [v[0] * Math.cos(a) - v[1] * Math.sin(a), v[0] * Math.sin(a) + v[1] * Math.cos(a), v[2]];

export const skelPlan = (play: PlayWithSkel, id: string): SkelPlan | null => {
  const spec = play.skel?.[id];
  if (!spec || spec.look === 'A') return null;
  let m = planCache.get(play);
  if (!m) planCache.set(play, (m = new Map()));
  if (m.has(id)) return m.get(id)!;
  const clip = CLIPS.get(spec.clip);
  if (!clip) {
    m.set(id, null);
    return null;
  }
  const ms = clip.milestones;
  const acts = actionsOf(play, id);
  const screen = acts.find((a) => a.type === 'screen');
  const roll = acts.find((a) => a.type === 'roll');
  if (!screen || !roll) {
    m.set(id, null);
    return null;
  }
  const wp = play.tracks[id];
  const P = (t: number): V3 => {
    const p = posAt(wp, Math.max(0, Math.min(play.duration, t)));
    return [p[0], p[1], 0];
  };
  const cidx = (ct: number) => Math.round(clamp((ct - clip.t0) * clip.fps, 0, clip.n - 1));
  const cRoot = (ct: number) => clip.root[cidx(ct)];
  // ---- engine path, sampled
  const DT = 1 / 240;
  const eT: number[] = [];
  const eD: number[] = [];
  let acc = 0;
  for (let t = 0, prev = P(0); t <= play.duration + 1e-9; t += DT) {
    const p = P(t);
    acc += Math.hypot(p[0] - prev[0], p[1] - prev[1]);
    eT.push(t);
    eD.push(acc);
    prev = p;
  }
  const eDist = (t: number) => eD[Math.max(0, Math.min(eD.length - 1, Math.round(t / DT)))];
  const eTimeAtDist = (d: number, from: number, to: number) => {
    // first engine time in [from, to] at which the distance run reaches d
    for (let k = Math.round(from / DT); k <= Math.round(to / DT) && k < eD.length; k++) if (eD[k] >= d) return eT[k];
    return to;
  };
  // ---- clip path distances (root, horizontal)
  const cD: number[] = [0];
  for (let i = 1; i < clip.n; i++) cD.push(cD[i - 1] + Math.hypot(clip.root[i][0] - clip.root[i - 1][0], clip.root[i][1] - clip.root[i - 1][1]));
  const cDist = (ct: number) => cD[cidx(ct)];
  // ---- the screen spot: the engine stops there; the clip "set" = middle of the two planted feet
  const eSet = screen.from;
  const eRoll = roll.from;
  const setC = ms.set;
  const unw = ms.unweight ?? ms.unweight_R;
  const atSet = clip.contacts.filter((c) => c.t0 <= setC && c.t1 >= setC);
  const Sc: V3 = atSet.length ? mul(atSet.reduce((a, c) => add(a, c.anchor), [0, 0, 0] as V3), 1 / atSet.length) : cRoot(setC);
  // engine track stands still somewhere in [eSet - 0.2, eRoll]: its position there is the screen spot
  const Se = P(eSet);
  // ---- knots: approach (distance to the spot), hold (linear), roll (distance from the spot)
  const knots: [number, number][] = [];
  const stepC = 1 / clip.fps;
  const dSetC = cDist(setC);
  const eArrive = eTimeAtDist(eDist(eSet) - 1e-4, 0, eSet); // engine reaches the spot
  const cFrom = Math.max(clip.t0, Math.min(setC - 0.2, spec.from ?? clip.t0));
  for (let ct = cFrom; ct < setC - 1e-6; ct += stepC) {
    const remain = dSetC - cDist(ct);
    const e = eTimeAtDist(eDist(eArrive) - remain, 0, eArrive);
    knots.push([e, ct]);
  }
  knots.push([eSet, setC]);
  knots.push([eRoll, unw]);
  const d0 = eDist(eRoll);
  const dU = cDist(unw);
  const cTo = Math.min(clipEnd(clip), Math.max(unw + 0.3, spec.to ?? clipEnd(clip)));
  for (let ct = unw + stepC; ct <= cTo + 1e-6; ct += stepC) {
    const e = eTimeAtDist(d0 + (cDist(ct) - dU), eRoll, play.duration);
    knots.push([e, ct]);
  }
  // monotone, at least 0.55x and at most 1.8x the clip speed between knots (keeps the cadence human)
  const K: [number, number][] = [knots[0]];
  for (let k = 1; k < knots.length; k++) {
    const [e, c] = knots[k];
    const [pe, pc] = K[K.length - 1];
    const dc = c - pc;
    const de = clamp(e - pe, dc / 1.8, dc / 0.55);
    K.push([pe + de, c]);
  }
  // re-anchor the hold knots exactly (the clamp may have shifted them)
  const shiftTo = (cTarget: number, eTarget: number) => {
    const k = K.findIndex((x) => Math.abs(x[1] - cTarget) < 1e-6);
    if (k < 0) return;
    const delta = eTarget - K[k][0];
    for (let i = 0; i <= k; i++) K[i] = [K[i][0] + delta * (i / Math.max(1, k)) ** 2, K[i][1]];
  };
  shiftTo(setC, eSet);
  // ---- rotations: approach, hold (face the screen target), roll (run along the play track)
  const faceAt = (t: number) => {
    const f = screen.face;
    if (typeof f === 'number') return f;
    if (typeof f === 'string' && play.tracks[f]) {
      const o = P(t);
      const q = posAt(play.tracks[f], t);
      return Math.atan2(q[1] - o[1], q[0] - o[0]);
    }
    return Math.atan2(Se[1] - P(eSet - 0.6)[1], Se[0] - P(eSet - 0.6)[0]);
  };
  let cFace = 0;
  {
    let sx = 0;
    let sy = 0;
    for (let ct = setC; ct <= unw; ct += stepC) {
      const i = cidx(ct);
      const a = (clip.heading[i] + clip.chestYaw[i]) / 2;
      sx += Math.cos(a);
      sy += Math.sin(a);
    }
    cFace = Math.atan2(sy, sx);
  }
  const thH = wrap(faceAt(eSet + 0.3) - cFace);
  const brakeC = ms.brake ?? ms.brake_R ?? ms.plant_L;
  const plantC = ms.plant ?? ms.plant_L;
  const pivC0 = ms.pivot_start;
  const pivC1 = ms.release ?? ms.L_release;
  const eStart0 = K[0][0];
  const tauH0 = sub(Se, rotZ(Sc, thH));
  const brake0 = clip.contacts.find((c) => Math.abs(c.t0 - brakeC) < 0.05);
  const B0 = brake0 ? brake0.anchor : Sc;
  // approach: the clip start lands on the engine track, rotating about the brake foot (where hold and approach meet)
  const appE = sub(add(rotZ(B0, thH), tauH0), P(eStart0));
  const appC = sub(B0, cRoot(cFrom));
  const thA = Math.hypot(appE[0], appE[1]) > 0.3 ? wrap(Math.atan2(appE[1], appE[0]) - Math.atan2(appC[1], appC[0])) : thH;
  const pivot = clip.contacts.find((c) => c.pivot);
  const A = pivot ? pivot.anchor : Sc;
  const cEnd = cTo;
  const eEndK = K[K.length - 1][0];
  const runE = sub(P(eEndK), Se);
  const runC = sub(cRoot(cEnd), A);
  const thRun = wrap(Math.atan2(runE[1], runE[0]) - Math.atan2(runC[1], runC[0]));
  const thR = thH + wrap(thRun - thH);
  const thAa = thH + wrap(thA - thH);
  const tauH = sub(Se, rotZ(Sc, thH));
  const brake = clip.contacts.find((c) => Math.abs(c.t0 - brakeC) < 0.05);
  const B = brake ? brake.anchor : Sc;
  const Bp = add(rotZ(B, thH), tauH);
  const Ap = add(rotZ(A, thH), tauH);
  const thetaAt = (ct: number) => {
    if (ct < brakeC) return thAa;
    if (ct < plantC) return thAa + (thH - thAa) * smooth((ct - brakeC) / (plantC - brakeC));
    if (ct < pivC0) return thH;
    if (ct < pivC1) return thH + (thR - thH) * smooth((ct - pivC0) / (pivC1 - pivC0));
    return thR;
  };
  const tauAt = (ct: number): V3 => {
    const th = thetaAt(ct);
    if (ct < plantC) return sub(Bp, rotZ(B, th));
    if (ct < pivC0) return tauH;
    return sub(Ap, rotZ(A, th));
  };
  // ---- contacts in play space (anchor transformed at touch-down)
  const fb = (s: 'L' | 'R') => clip.bones.find((b) => b.name === `foot.${s}`)!;
  const contacts: EngContact[] = [];
  for (const c of clip.contacts) {
    const e = c.eff ?? [c.t0, c.t1];
    const th = thetaAt(e[0]);
    const anchor = add(rotZ(c.anchor, th), tauAt(e[0]));
    anchor[2] = 0;
    const b = fb(c.foot);
    const ballLocal = qrot(qconj(b.R), sub(clip.restJoints[`ball${c.foot}`], clip.restJoints[`ankle${c.foot}`]));
    contacts.push({foot: c.foot === 'L' ? 0 : 1, c0: e[0], c1: e[1], anchor, ballLocal});
  }
  // ---- swings: the tracked swing foot is noisy when the player runs away from the camera (depth of the legs), so between
  // two stances of the same foot the ankle follows a minimum-jerk path from lift-off to touch-down (height from the clip)
  const swings: EngSwing[] = [];
  const ankleAt = (k: EngContact, ct: number): V3 => {
    const s = k.foot === 0 ? 'L' : 'R';
    const qf = qmul(qz(thetaAt(ct)), sampleClip(clip, ct).q[`foot.${s}`]);
    return sub(k.anchor, qrot(qf, k.ballLocal));
  };
  for (const foot of [0, 1] as const) {
    const ks = contacts.filter((k) => k.foot === foot).sort((a, b) => a.c0 - b.c0);
    for (let i = 0; i + 1 < ks.length; i++) {
      const a = ks[i];
      const b = ks[i + 1];
      if (b.c0 - a.c1 < 2 / clip.fps) continue;
      swings.push({foot, c0: a.c1, c1: b.c0, a0: ankleAt(a, a.c1), a1: ankleAt(b, b.c0)});
    }
  }
  const blend = spec.blend ?? 0.18;
  const plan: SkelPlan = {
    clip,
    spec,
    knots: K,
    eStart: K[0][0],
    eEnd: K[K.length - 1][0],
    blend,
    thetaAt,
    tauAt,
    contacts,
    swings,
    info: {thetaApproachDeg: (thAa * 180) / Math.PI, thetaHoldDeg: (thH * 180) / Math.PI, thetaRunDeg: (thR * 180) / Math.PI, eStart: K[0][0], eEnd: K[K.length - 1][0]},
  };
  m.set(id, plan);
  return plan;
};

/** engine time -> clip time (piecewise linear through the knots) */
export const warp = (plan: SkelPlan, t: number) => {
  const K = plan.knots;
  if (t <= K[0][0]) return K[0][1];
  if (t >= K[K.length - 1][0]) return K[K.length - 1][1];
  let lo = 0;
  let hi = K.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (K[mid][0] <= t) lo = mid;
    else hi = mid;
  }
  const [e0, c0] = K[lo];
  const [e1, c1] = K[hi];
  return c0 + ((t - e0) / Math.max(1e-9, e1 - e0)) * (c1 - c0);
};

// ---------------------------------------------------------------- pose from the clip (play space)
export type SkelPose = {
  pose: Pose;
  w: number; // 0 = procedural rig, 1 = clip
  bones?: Record<string, Q>; // world rotations (play coords), clip skeleton
  hips?: V3; // hips bone head (play coords)
  pins: (V3 | null)[]; // pinned ball-of-foot anchor per foot (null = swinging)
  balls?: V3[]; // rendered ball-of-foot points (clip skeleton), for the contact QC
  ct?: number;
};

const PIN_BLEND = 3; // frames, as in retarget.py

const clipPose = (plan: SkelPlan, play: PlayWithSkel, id: string, t: number) => {
  const c = plan.clip;
  const ct = warp(plan, t);
  const f = sampleClip(c, ct);
  const th = plan.thetaAt(ct);
  const tau = plan.tauAt(ct);
  const qT = qz(th);
  const X = (p: V3) => add(rotZ(p, th), tau);
  const j: Record<string, V3> = {};
  for (const k of Object.keys(f.j)) j[k] = X(f.j[k]);
  const bones: Record<string, Q> = {};
  for (const b of c.bones) bones[b.name] = qmul(qT, f.q[b.name]);
  const hips = X(f.root);
  // ---- pins: contact windows in clip time (blend PIN_BLEND frames in/out), ankle IK in play space
  const len = (n: string) => {
    const b = c.bones.find((x) => x.name === n)!;
    return Math.hypot(b.tail[0] - b.head[0], b.tail[1] - b.head[1], b.tail[2] - b.head[2]);
  };
  const L1 = len('thigh.L');
  const L2 = len('shin.L');
  const pins: (V3 | null)[] = [null, null];
  const bw = PIN_BLEND / c.fps;
  const bests: ({w: number; k: EngContact} | null)[] = [null, null];
  const targets: (V3 | null)[] = [null, null];
  for (let i = 0; i < 2; i++) {
    const s = i === 0 ? 'L' : 'R';
    let best: {w: number; k: EngContact} | null = null;
    for (const k of plan.contacts) {
      if (k.foot !== i) continue;
      const w = ct >= k.c0 && ct <= k.c1 ? 1 : ct < k.c0 ? 1 - (k.c0 - ct) / (bw + 1e-9) : 1 - (ct - k.c1) / (bw + 1e-9);
      if (w > 0 && (!best || w > best.w)) best = {w: Math.min(1, w), k};
    }
    let free: V3 = j[`ankle${s}`];
    const sw = plan.swings.find((x) => x.foot === i && ct > x.c0 && ct < x.c1);
    if (sw) {
      const u = (ct - sw.c0) / (sw.c1 - sw.c0);
      const m = u * u * u * (10 - 15 * u + 6 * u * u); // minimum jerk
      const p = lerp3(sw.a0, sw.a1, m);
      // the foot clears the floor in a swing (tracked height kept when higher); long strides lift more
      const lift = Math.min(0.14, 0.06 * Math.hypot(sw.a1[0] - sw.a0[0], sw.a1[1] - sw.a0[1])) * Math.sin(Math.PI * u);
      free = [p[0], p[1], Math.max(p[2] + lift, j[`ankle${s}`][2])];
    }
    if (!best) {
      if (sw) targets[i] = free;
      continue;
    }
    bests[i] = best;
    const ankleWant = sub(best.k.anchor, qrot(bones[`foot.${s}`], best.k.ballLocal));
    targets[i] = lerp3(free, ankleWant, best.w);
  }
  // soft reach: when a pinned leg would have to over-extend (time warp + placement stretch the clip a little), the
  // whole body sinks just enough (the same rule as the retarget's root drop, capped at 6 cm)
  let drop = 0;
  const reach = 0.997 * (L1 + L2);
  for (let i = 0; i < 2; i++) {
    const tg = targets[i];
    if (!tg || !bests[i]) continue;
    const h = j[`hip${i === 0 ? 'L' : 'R'}`];
    const dxy = Math.hypot(h[0] - tg[0], h[1] - tg[1]);
    if (dxy >= reach) continue;
    const zMax = tg[2] + Math.sqrt(reach * reach - dxy * dxy);
    drop = Math.max(drop, h[2] - zMax);
  }
  drop = Math.min(0.06, Math.max(0, drop));
  if (drop > 0) {
    for (const k of Object.keys(j)) j[k] = [j[k][0], j[k][1], j[k][2] - drop];
    hips[2] -= drop;
  }
  for (let i = 0; i < 2; i++) {
    const s = i === 0 ? 'L' : 'R';
    const best = bests[i];
    const target = targets[i];
    if (!target) continue;
    const hip = j[`hip${s}`];
    const ankle0 = j[`ankle${s}`];
    const knee0 = j[`knee${s}`];
    const pole = sub(knee0, hip);
    const sol = ik2(hip, target, L1, L2, pole);
    // re-aim thigh and shin onto the solved knee / ankle (swing), the foot keeps its world rotation
    const qTh = qmul(qswing(sub(knee0, hip), sub(sol.mid, hip)), bones[`thigh.${s}`]);
    const shinNow = qmul(qmul(qTh, qconj(bones[`thigh.${s}`])), bones[`shin.${s}`]);
    const shinDir = qrot(shinNow, [0, 1, 0]);
    const qSh = qmul(qswing(shinDir, sub(sol.end, sol.mid)), shinNow);
    bones[`thigh.${s}`] = qTh;
    bones[`shin.${s}`] = qSh;
    const dA = sub(sol.end, ankle0);
    j[`knee${s}`] = sol.mid;
    j[`ankle${s}`] = sol.end;
    for (const k of ['toe', 'ball', 'heel']) j[`${k}${s}`] = add(j[`${k}${s}`], dA);
    if (best && best.w >= 1) pins[i] = best.k.anchor;
  }
  // head pitch: the tracked head of the take tips back (MediaPipe face landmarks while he looks at the handler); the
  // pitch relative to the chest is limited to [-6 deg back, +20 deg forward], yaw and roll stay as captured
  {
    const cUp = qrot(bones.chest, [0, 1, 0]);
    const hUp = qrot(bones.head, [0, 1, 0]);
    const fwd = norm([Math.cos(f.chestYaw + th), Math.sin(f.chestYaw + th), 0]);
    const pc = Math.asin(clamp(dot(cUp, fwd), -1, 1));
    const ph = Math.asin(clamp(dot(hUp, fwd), -1, 1));
    const rel = ph - pc;
    const lim = clamp(rel, (-6 * Math.PI) / 180, (20 * Math.PI) / 180);
    if (Math.abs(lim - rel) > 1e-4) {
      const side = norm(cross([0, 0, 1], fwd));
      const ang = lim - rel; // rotation about his left axis: positive tips the top of the head forward
      const qa: Q = [side[0] * Math.sin(ang / 2), side[1] * Math.sin(ang / 2), side[2] * Math.sin(ang / 2), Math.cos(ang / 2)];
      bones.head = qmul(qa, bones.head);
      bones.neck = qslerp(bones.chest, bones.head, 0.5);
      j.head = add(j.chest, qrot(qa, sub(j.head, j.chest)));
    }
  }
  return {ct, j, bones, hips, heading: f.heading + th, chestYaw: f.chestYaw + th, pins, balls: [j.ballL, j.ballR]};
};

const poseFromJoints = (j: Record<string, V3>, heading: number, chestYaw: number, H: number): Pose => ({
  pelvis: j.pelvis,
  chest: j.chest,
  head: j.head,
  heading,
  chestYaw,
  headYaw: chestYaw,
  lean: 0,
  roll: 0,
  hip: [j.hipL, j.hipR],
  knee: [j.kneeL, j.kneeR],
  ankle: [j.ankleL, j.ankleR],
  toe: [j.toeL, j.toeR],
  shoulder: [j.shoulderL, j.shoulderR],
  elbow: [j.elbowL, j.elbowR],
  wrist: [j.wristL, j.wristR],
  hand: [j.handL, j.handR],
  airborne: 0,
  dims: dimsFor(H),
});

const lerpPose = (a: Pose, b: Pose, u: number): Pose => {
  const L = (x: V3, y: V3) => lerp3(x, y, u);
  const L2 = (x: [V3, V3], y: [V3, V3]): [V3, V3] => [L(x[0], y[0]), L(x[1], y[1])];
  return {
    ...b,
    pelvis: L(a.pelvis, b.pelvis),
    chest: L(a.chest, b.chest),
    head: L(a.head, b.head),
    heading: a.heading + wrap(b.heading - a.heading) * u,
    chestYaw: a.chestYaw + wrap(b.chestYaw - a.chestYaw) * u,
    hip: L2(a.hip, b.hip),
    knee: L2(a.knee, b.knee),
    ankle: L2(a.ankle, b.ankle),
    toe: L2(a.toe, b.toe),
    shoulder: L2(a.shoulder, b.shoulder),
    elbow: L2(a.elbow, b.elbow),
    wrist: L2(a.wrist, b.wrist),
    hand: L2(a.hand, b.hand),
    airborne: a.airborne * (1 - u),
    dims: a.dims,
  };
};

// ---------------------------------------------------------------- Pose -> bone rotations (for the mesh outside the clip)
// Same two-vector frames as tools/blender/retarget.py, calibrated on the clip's rest joints.
type Frames = Record<string, Q>;
const framesOf = (J: Record<string, V3>, chestYaw?: number, hinge0?: Record<string, V3>): Frames => {
  const side = sub(J.hipL, J.hipR);
  const midS = mul(add(J.shoulderL, J.shoulderR), 0.5);
  const up = sub(J.chest, J.pelvis);
  const F: Frames = {};
  F.hips = twoVec(up, side);
  F.chest = twoVec(up, sub(J.shoulderL, J.shoulderR));
  const hs: V3 = chestYaw !== undefined ? [-Math.sin(chestYaw), Math.cos(chestYaw), 0] : sub(J.shoulderL, J.shoulderR);
  F.head = twoVec(sub(J.head, J.chest), hs);
  for (const s of ['L', 'R']) {
    F[`clavicle.${s}`] = twoVec(sub(J[`shoulder${s}`], midS), up);
    const hingeOf = (a: V3, b: V3, c: V3, fb: V3) => {
      const p = sub(b, a);
      const q = sub(c, b);
      const n = cross(p, q);
      const w = clamp(len(n) / (len(p) * len(q) * Math.sin((25 * Math.PI) / 180)));
      return norm(add(mul(norm(n), w), mul(fb, 1 - w)));
    };
    const armH = hingeOf(J[`shoulder${s}`], J[`elbow${s}`], J[`wrist${s}`], hinge0 ? qrot(F.chest, hinge0[`arm${s}`]) : [0, 0, 1]);
    const legH = hingeOf(J[`hip${s}`], J[`knee${s}`], J[`ankle${s}`], hinge0 ? qrot(F.hips, hinge0[`leg${s}`]) : [1, 0, 0]);
    F[`upperarm.${s}`] = twoVec(sub(J[`elbow${s}`], J[`shoulder${s}`]), armH);
    F[`forearm.${s}`] = twoVec(sub(J[`wrist${s}`], J[`elbow${s}`]), armH);
    F[`hand.${s}`] = twoVec(sub(J[`hand${s}`], J[`wrist${s}`]), armH);
    F[`thigh.${s}`] = twoVec(sub(J[`knee${s}`], J[`hip${s}`]), legH);
    F[`shin.${s}`] = twoVec(sub(J[`ankle${s}`], J[`knee${s}`]), legH);
    F[`foot.${s}`] = twoVec(sub(J[`toe${s}`], J[`heel${s}`]), sub(J[`ankle${s}`], J[`heel${s}`]));
    F[`toe.${s}`] = F[`foot.${s}`];
  }
  return F;
};
const adapterCache = new WeakMap<SkelClip, {rest: Frames; hinge0: Record<string, V3>}>();
const adapterRest = (c: SkelClip) => {
  let a = adapterCache.get(c);
  if (a) return a;
  const R = c.restJoints;
  const rest0 = framesOf(R);
  // hinge directions of the rest pose expressed in the chest / hips frames (fallback when a limb is straight)
  const hinge0: Record<string, V3> = {};
  for (const s of ['L', 'R']) {
    const armN = norm(cross(sub(R[`elbow${s}`], R[`shoulder${s}`]), sub(R[`wrist${s}`], R[`elbow${s}`])));
    const legN: V3 = norm(sub(R.hipL, R.hipR)); // the rest legs are straight: the knee hinge is the pelvis side axis
    hinge0[`arm${s}`] = qrot(qconj(rest0.chest), armN);
    hinge0[`leg${s}`] = qrot(qconj(rest0.hips), s === 'L' ? legN : legN);
  }
  a = {rest: framesOf(R, undefined, hinge0), hinge0};
  adapterCache.set(c, a);
  return a;
};

/** bone world rotations (play coords, clip skeleton) for an engine Pose: legs re-solved with the clip's leg lengths
 *  so the feet land where the engine puts them. Returns rotations + hips head position. */
export const bonesFromPose = (c: SkelClip, P: Pose): {bones: Record<string, Q>; hips: V3} => {
  const {rest, hinge0} = adapterRest(c);
  const R = c.restJoints;
  // heel / ball of the engine foot: from ankle -> toe
  const J: Record<string, V3> = {pelvis: P.pelvis, chest: P.chest, head: P.head};
  const S = ['L', 'R'];
  const legRest = len(sub(R.kneeL, R.hipL)) + len(sub(R.ankleL, R.kneeL));
  const legEng = P.dims.thigh + P.dims.shin;
  // the mesh pelvis sits higher by the leg-length difference (hips bone head = middle of the hip joints)
  const lift: V3 = [0, 0, (legRest - legEng) * 0.9];
  for (let i = 0; i < 2; i++) {
    const s = S[i];
    J[`hip${s}`] = add(P.hip[i], lift);
    J[`shoulder${s}`] = P.shoulder[i];
    J[`elbow${s}`] = P.elbow[i];
    J[`wrist${s}`] = P.wrist[i];
    J[`hand${s}`] = P.hand[i];
    const fwd = norm([P.toe[i][0] - P.ankle[i][0], P.toe[i][1] - P.ankle[i][1], 0]);
    J[`toe${s}`] = P.toe[i];
    J[`heel${s}`] = [P.ankle[i][0] - fwd[0] * 0.08, P.ankle[i][1] - fwd[1] * 0.08, Math.max(0, P.toe[i][2] - 0.01)];
    // mesh leg lengths: knee from IK onto the engine ankle
    const L1 = len(sub(R[`knee${s}`], R[`hip${s}`]));
    const L2 = len(sub(R[`ankle${s}`], R[`knee${s}`]));
    const sol = ik2(J[`hip${s}`], P.ankle[i], L1, L2, sub(P.knee[i], P.hip[i]));
    J[`knee${s}`] = sol.mid;
    J[`ankle${s}`] = sol.end;
  }
  J.pelvis = add(J.pelvis, lift);
  J.chest = add(J.chest, lift);
  J.head = add(J.head, lift);
  const F = framesOf(J, P.chestYaw, hinge0);
  const bones: Record<string, Q> = {};
  for (const b of c.bones) {
    const key = b.name === 'spine' || b.name === 'neck' ? null : b.name;
    if (key && F[key]) bones[b.name] = qmul(qmul(F[key], qconj(rest[key])), b.R);
  }
  bones.spine = qslerp(bones.hips, bones.chest, 0.5);
  bones.neck = qslerp(bones.chest, bones.head, 0.5);
  const hipsRest = c.bones.find((b) => b.name === 'hips')!.head;
  const midRest = mul(add(R.hipL, R.hipR), 0.5);
  const midNow = mul(add(J.hipL, J.hipR), 0.5);
  const hips = add(midNow, qrot(bones.hips, qrot(qconj(c.bones[0].R), sub(hipsRest, midRest))));
  return {bones, hips};
};

// ---------------------------------------------------------------- public entry: pose of a player at play time t
export const skelPoseAt = (play: PlayWithSkel, id: string, t: number, ball: BallHint, rim: V3, withBones = false): SkelPose => {
  const base = poseAt(play, id, t, ball, rim);
  const plan = skelPlan(play, id);
  if (!plan) return {pose: base, w: 0, pins: [null, null]};
  const b = plan.blend;
  const w = smooth((t - plan.eStart) / b) * (1 - smooth((t - (plan.eEnd - b)) / b));
  const H = PLAYER_HEIGHTS[id] ?? 2;
  if (w <= 0) {
    if (!withBones) return {pose: base, w: 0, pins: [null, null]};
    const r = bonesFromPose(plan.clip, base);
    return {pose: base, w: 0, bones: r.bones, hips: r.hips, pins: [null, null]};
  }
  const cp = clipPose(plan, play, id, t);
  const pc = poseFromJoints(cp.j, cp.heading, cp.chestYaw, H);
  const pose = w >= 1 ? pc : lerpPose(base, pc, w);
  if (!withBones) return {pose, w, pins: w >= 1 ? cp.pins : [null, null], balls: cp.balls, ct: cp.ct};
  let bones = cp.bones;
  let hips = cp.hips;
  if (w < 1) {
    const r = bonesFromPose(plan.clip, base);
    const out: Record<string, Q> = {};
    for (const k of Object.keys(bones)) out[k] = qslerp(r.bones[k], bones[k], w);
    bones = out;
    hips = lerp3(r.hips, hips, w);
  }
  return {pose, w, bones, hips, pins: w >= 1 ? cp.pins : [null, null], balls: cp.balls, ct: cp.ct};
};

/** drop-in for poseAt: the clip pose for players with a skeletal clip, the procedural rig for everyone else */
export const posePlayer = (play: PlayWithSkel, id: string, t: number, ball: BallHint, rim: V3): Pose => skelPoseAt(play, id, t, ball, rim).pose;
