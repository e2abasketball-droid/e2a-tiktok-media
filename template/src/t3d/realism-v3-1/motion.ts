// E2A Realism V3.1 (2026-11-22) — AUTHORED motion layer of the V3.1 athlete (athleteRenderer 'v31', opt-in).
//
// Why: in V3 the mesh was driven 1:1 by the engine pose (rig.ts poseAt), so V3 moved exactly like legacy; only the skin
// changed and the owner could not tell the two apart. V3.1 replaces the BODY motion of a player that has an authored
// clip (clips.ts) with a hand-keyed performance; the tactical track is only the ROOT constraint (where the player is).
//
// What is authored (clips.ts, labelled "hand-keyed", no motion capture, no paid asset):
//   steps     a footstep schedule {side, lift, land, offset}: each landing spot is fixed at its landing time from the
//             root track, then the foot is LOCKED (no slide) until it lifts; swing arcs, toe-off, heel strike / landing
//             on the ball of the foot (foot pitch), pivots on the ball of the foot
//   channels  heading, chest offset (shoulders lead / counter-rotate), trunk lean and roll, pelvis drop — monotone cubic
//             keys (Fritsch-Butland: no overshoot) — plus gait layers computed from the steps: pelvis bob at each
//             landing, pelvic drop on the swing side, pelvis / chest counter-rotation, arm swing opposite the legs
//   look      head target keys (path / player / rim / ball) blended over time, the head leads turns
//   arms      mode keys (ready, run, brake, reach, give, pocket, triple, jab, dribble, gather, set, shoot, follow, land,
//             defense) cross-faded; while O1 holds the ball the BALL is the hand socket of the mode (FREE -> RECEIVING ->
//             HELD -> DRIBBLE -> HELD -> GATHER -> RELEASED -> IN_FLIGHT): the catch meets the engine ball at the pass
//             arrival time, the release meets the engine release point (jump height adapted so it is reachable)
//   jump      ballistic pelvis (4 H u (1 - u)) between takeoff and landing
// PURE function of (play, id, t, rig): nothing is integrated frame to frame, so Remotion seeks (100 -> 5 -> 250 -> 100)
// give identical poses. The cloth spring (clothV31) is integrated from t - 1.2 s like cloth2, also pure.
import type {V3} from '../../tactical/geometry.ts';
import type {Play} from '../../tactical/play.ts';
import {posAt, sample} from '../../tactical/play.ts';
import type {Dims, Pose} from '../rig.ts';
import {BALL_R, PLAYER_BUILD, PLAYER_HEIGHTS, dimsFor} from '../rig.ts';
import type {Q} from '../skelclip.ts';
import {qconj, qmul, qrot} from '../skelclip.ts';
import type {Cloth} from '../cloth2.ts';
import type {RigV3, V3Frame} from '../realism-v3/athleteV3.ts';
import {baseRig, bonesV3, fkHeads, palmWorld} from '../realism-v3/athleteV3.ts';
import {bonesFromPose} from '../skelclip.ts';
import type {ArmKey, Clip31, Step} from './clips.ts';
import {clipFor} from './clips.ts';

// ---------------------------------------------------------------- small maths
const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const mul = (a: V3, k: number): V3 => [a[0] * k, a[1] * k, a[2] * k];
const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const norm = (a: V3): V3 => mul(a, 1 / Math.max(1e-9, len(a)));
const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
const lerp3 = (a: V3, b: V3, u: number): V3 => [lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u)];
const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const smooth = (x: number) => {
  const u = clamp(x);
  return u * u * (3 - 2 * u);
};
const wrap = (a: number) => Math.atan2(Math.sin(a), Math.cos(a));
const fwd = (h: number): V3 => [Math.cos(h), Math.sin(h), 0];
const right = (h: number): V3 => [Math.sin(h), -Math.cos(h), 0];
const UP: V3 = [0, 0, 1];
const axisAngle = (ax: V3, th: number): Q => {
  const s = Math.sin(th / 2);
  const n = norm(ax);
  return [n[0] * s, n[1] * s, n[2] * s, Math.cos(th / 2)];
};

/** monotone cubic keys (Fritsch-Butland tangents): smooth, never overshoots a held value */
export const keyAt = (k: [number, number][], t: number): number => {
  const n = k.length;
  if (t <= k[0][0]) return k[0][1];
  if (t >= k[n - 1][0]) return k[n - 1][1];
  let i = 0;
  while (k[i + 1][0] < t) i++;
  const sl = (a: number, b: number) => (k[b][1] - k[a][1]) / Math.max(1e-9, k[b][0] - k[a][0]);
  const tan = (j: number) => {
    if (j <= 0 || j >= n - 1) return 0;
    const s0 = sl(j - 1, j), s1 = sl(j, j + 1);
    if (s0 * s1 <= 0) return 0;
    return 2 / (1 / s0 + 1 / s1);
  };
  const h = k[i + 1][0] - k[i][0];
  const u = (t - k[i][0]) / h;
  const m0 = tan(i) * h, m1 = tan(i + 1) * h;
  const u2 = u * u, u3 = u2 * u;
  return (2 * u3 - 3 * u2 + 1) * k[i][1] + (u3 - 2 * u2 + u) * m0 + (-2 * u3 + 3 * u2) * k[i + 1][1] + (u3 - u2) * m1;
};

// ---------------------------------------------------------------- rig-derived constants (mesh space, scaled)
type RigC = {scale: number; ankleOff: number; ankleZ: number; dBall: number; dHeel: number; hipHalf: number; pelvisZ: number; legLen: number; arm: number; handLen: number; dims: Dims};
const rigCache = new WeakMap<RigV3, Map<string, RigC>>();
const rigConsts = (rig: RigV3, id: string): RigC => {
  let m = rigCache.get(rig);
  if (!m) rigCache.set(rig, (m = new Map()));
  const hit = m.get(id);
  if (hit) return hit;
  const dims = dimsFor(PLAYER_HEIGHTS[id] ?? 2.0, PLAYER_BUILD[id] ?? 1);
  const R = rig.restJoints;
  const legRest = len(sub(R.kneeL, R.hipL)) + len(sub(R.ankleL, R.kneeL));
  const scale = (dims.thigh + dims.shin) / legRest; // = meshScale(rig, pose)
  const S = (k: string): V3 => mul(R[k], scale);
  const hz = (a: V3, b: V3) => Math.hypot(a[0] - b[0], a[1] - b[1]);
  const c: RigC = {
    scale, dims,
    ankleOff: S('ankleL')[2] - dims.ankleH,
    ankleZ: S('ankleL')[2],
    dBall: hz(S('ballL'), S('ankleL')),
    dHeel: hz(S('heelL'), S('ankleL')),
    hipHalf: len(sub(S('hipL'), S('hipR'))) / 2,
    pelvisZ: (S('hipL')[2] + S('hipR')[2]) / 2,
    legLen: (len(sub(S('kneeL'), S('hipL'))) + len(sub(S('ankleL'), S('kneeL')))),
    arm: len(sub(S('elbowL'), S('shoulderL'))) + len(sub(S('wristL'), S('elbowL'))),
    handLen: len(sub(S('handL'), S('wristL'))),
  };
  m.set(id, c);
  return c;
};

// ---------------------------------------------------------------- feet
type FootState = {g: V3; yaw: number; pitch: number; support: number; fwdness: number; ankle: V3};
const anchorOf = (clip: Clip31, play: Play, root: (t: number) => V3, st: {f: number; l: number; yaw?: number}, t: number, side: 0 | 1): {g: V3; yaw: number} => {
  const h = keyAt(clip.heading, t);
  const r = root(t);
  const p = add(add(r, mul(fwd(h), st.f)), mul(right(h), st.l));
  return {g: [p[0], p[1], 0], yaw: h + (st.yaw ?? 0) + (side === 0 ? 0.1 : -0.1)};
};

/** ankle joint (mesh) of a foot whose flat ground point is g, yaw, pitch (+ = heel up about the ball of the foot,
 *  - = toe up about the heel), lifted by g[2] */
const ankleOf = (c: RigC, g: V3, yaw: number, pitch: number): V3 => {
  const F = fwd(yaw);
  if (pitch >= 0) {
    const B = add(g, mul(F, c.dBall));
    const vx = -c.dBall * Math.cos(pitch) + c.ankleZ * Math.sin(pitch);
    const vz = c.dBall * Math.sin(pitch) + c.ankleZ * Math.cos(pitch);
    return add(add(B, mul(F, vx)), [0, 0, vz]);
  }
  const th = -pitch;
  const Hh = sub(g, mul(F, c.dHeel));
  const vx = c.dHeel * Math.cos(th) - c.ankleZ * Math.sin(th);
  const vz = c.dHeel * Math.sin(th) + c.ankleZ * Math.cos(th);
  return add(add(Hh, mul(F, vx)), [0, 0, vz]);
};

/** a planted foot (anchor landed at landT) at time t: pivots on the ball of the foot applied */
const plantedAt = (clip: Clip31, c: RigC, side: 0 | 1, anchor: {g: V3; yaw: number}, landT: number, t: number): {g: V3; yaw: number} => {
  let yaw = anchor.yaw;
  let g = anchor.g;
  for (const pv of clip.pivots.filter((p) => p.s === side && p.t0 >= landT - 1e-6)) {
    if (t <= pv.t0) continue;
    const u = smooth((t - pv.t0) / (pv.t1 - pv.t0));
    const B = add(g, mul(fwd(yaw), c.dBall));
    yaw = yaw + pv.dyaw * u;
    const g2 = sub(B, mul(fwd(yaw), c.dBall));
    g = [g2[0], g2[1], 0];
  }
  return {g, yaw};
};

const footAt = (clip: Clip31, play: Play, c: RigC, root: (t: number) => V3, side: 0 | 1, t: number, jumpH: number): FootState => {
  const steps = clip.steps.filter((s) => s.s === side);
  let prev = anchorOf(clip, play, root, clip.init[side], 0, side);
  let prevLand = -1;
  let prevStep: Step | undefined;
  for (let k = 0; k < steps.length; k++) {
    const st = steps[k];
    if (t < st.lift) break;
    const tgt = anchorOf(clip, play, root, st, st.land, side);
    if (t < st.land) {
      prev = plantedAt(clip, c, side, prev, prevLand, st.lift);
      // swing: horizontal ease, arc, toe-off -> toes down -> landing attitude
      const u = (t - st.lift) / (st.land - st.lift);
      const hs = 0.5 - 0.5 * Math.cos(Math.PI * clamp(u * 1.08));
      let z: number;
      if (st.air) z = 4 * jumpH * u * (1 - u) * 0.92 + 0.06 * Math.sin(Math.PI * u);
      else z = (st.h ?? 0.09) * Math.pow(Math.sin(Math.PI * u), 0.85);
      const toeOff = st.air ? 0.6 : st.toeOff ?? 0.42;
      const land = st.heel ?? 0.05;
      const pitch = toeOff * (1 - u) * (1 - u) + (st.air ? 0.45 : 0.28) * Math.sin(Math.PI * u) + land * u * u * u;
      const yaw = prev.yaw + wrap(tgt.yaw - prev.yaw) * hs;
      const g: V3 = [lerp(prev.g[0], tgt.g[0], hs), lerp(prev.g[1], tgt.g[1], hs), z];
      return {g, yaw, pitch, support: 0, fwdness: -1 + 2 * smooth(u), ankle: ankleOf(c, g, yaw, pitch)};
    }
    prev = tgt;
    prevLand = st.land;
    prevStep = st;
  }
  // planted (locked) since prevLand; pivots on the ball of the foot, then heel rise before the next lift
  const pl = plantedAt(clip, c, side, prev, prevLand, t);
  const yaw = pl.yaw;
  const g = pl.g;
  const next = steps.find((s) => s.lift > t);
  let pitch = 0;
  if (prevStep) {
    const land = prevStep.heel ?? 0.05;
    pitch = land * (1 - smooth((t - prevLand) / (prevStep.air ? 0.14 : 0.09)));
  }
  const piv = clip.pivots.find((p) => p.s === side && t > p.t0 - 0.08 && t < p.t1 + 0.08);
  if (piv) pitch += 0.16 * Math.sin(Math.PI * clamp((t - piv.t0 + 0.08) / (piv.t1 - piv.t0 + 0.16)));
  // support weight: ramps in over 0.12 s after the landing, out over the last 0.08 s before the lift (pelvis shift continuous)
  let support = prevLand < 0 ? 1 : smooth((t - prevLand) / 0.12);
  if (next) support = Math.min(support, 1 - smooth((t - (next.lift - 0.08)) / 0.08));
  let fwdness = 1;
  if (next) {
    const toeOff = next.air ? 0.6 : next.toeOff ?? 0.42;
    const win = next.air ? 0.1 : 0.13;
    pitch += toeOff * smooth((t - (next.lift - win)) / win);
    fwdness = prevLand < 0 ? 0 : 1 - 2 * clamp((t - prevLand) / Math.max(0.05, next.lift - prevLand));
  } else fwdness = 0;
  return {g, yaw, pitch, support, fwdness, ankle: ankleOf(c, g, yaw, pitch)};
};

// ---------------------------------------------------------------- body (everything but the arms)
type Body = {
  t: number; root: V3; speed: number; h: number; chestYaw: number; hipYaw: number; lean: number; roll: number;
  feet: [FootState, FootState]; pelvis: V3; hipsUp: V3; hips: [V3, V3]; trunk: V3; chest: V3; head: V3; shoulders: [V3, V3]; amp: number; air: number;
};

const bodyAt = (clip: Clip31, play: Play, id: string, c: RigC, t: number, jumpH: number): Body => {
  const wp = play.tracks[id];
  const root = (x: number): V3 => {
    const p = posAt(wp, clamp(x, 0, play.duration));
    return [p[0], p[1], 0];
  };
  const r = root(t);
  const r0 = root(t - 0.05), r1 = root(t + 0.05);
  const speed = Math.hypot(r1[0] - r0[0], r1[1] - r0[1]) / 0.1;
  const amp = smooth(speed / 3.2) * (clip.back && t > clip.back[0] && t < clip.back[1] ? 0.55 : 1);
  const h = keyAt(clip.heading, t);
  const fL = footAt(clip, play, c, root, 0, t, jumpH);
  const fR = footAt(clip, play, c, root, 1, t, jumpH);
  const feet: [FootState, FootState] = [fL, fR];
  // gait layers
  const legDiff = (fR.fwdness - fL.fwdness) / 2; // + = right leg forward
  const hipYaw = h + 0.16 * amp * legDiff;
  let chestYaw = h + keyAt(clip.chest, t) - 0.13 * amp * legDiff;
  const lean = keyAt(clip.lean, t);
  const roll = keyAt(clip.roll, t);
  let bob = 0;
  for (const st of clip.steps) if (!st.air && Math.abs(t - st.land - 0.07) < 0.2) bob += 0.032 * amp * Math.exp(-(((t - st.land - 0.07) / 0.075) ** 2));
  // jump: ballistic pelvis
  let jz = 0;
  let air = 0;
  if (clip.jump && t > clip.jump.t0 && t < clip.jump.t1) {
    const u = (t - clip.jump.t0) / (clip.jump.t1 - clip.jump.t0);
    jz = 4 * jumpH * u * (1 - u);
    air = Math.min(fL.g[2], fR.g[2]);
  }
  // pelvis over the support: lateral shift toward the planted foot (continuous: feet are continuous, weights smooth)
  const sw = [fL.support, fR.support];
  const wsum = sw[0] + sw[1];
  const R = right(h);
  // lateral weight transfer over the support, averaged over +-0.08 s (a weight shift takes time; pure in t)
  const latAt = (x: number, a: FootState, z: FootState) => {
    const ws = a.support + z.support;
    if (ws <= 1e-4) return 0; // both feet unloaded (flight): no shift
    const mid = add(mul(a.g, a.support / ws), mul(z.g, z.support / ws));
    return clamp(dot(sub(mid, root(x)), right(keyAt(clip.heading, x))), -0.1, 0.1) * 0.35 * smooth(ws / 0.3);
  };
  let lat = 0;
  for (const k of [-2, -1, 0, 1, 2]) {
    const x = t + k * 0.04;
    lat += (k === 0 ? latAt(t, fL, fR) : latAt(x, footAt(clip, play, c, root, 0, x, jumpH), footAt(clip, play, c, root, 1, x, jumpH))) / 5;
  }
  const pxy = add(r, mul(R, lat));
  let pz = c.pelvisZ * 0.992 - keyAt(clip.drop, t) - bob + jz;
  // reach limiter: a planted foot is never further than 98.5 % of the leg from its hip (no knee pop, no foot slide)
  for (let i = 0; i < 2; i++) {
    const f = feet[i];
    const inJump = !!clip.jump && t > clip.jump.t0 && t < clip.jump.t1;
    if (f.support <= 0.001 && !inJump) continue;
    const side = i === 0 ? -1 : 1;
    const hp = add(pxy, mul(right(hipYaw), side * c.hipHalf));
    const dh = Math.hypot(hp[0] - f.ankle[0], hp[1] - f.ankle[1]);
    const L = c.legLen * 0.985;
    // an unloading foot releases the pelvis progressively (no pop when it lifts)
    const zmax = f.ankle[2] + Math.sqrt(Math.max(0, L * L - dh * dh)) + (inJump ? 0 : (1 - f.support) * 0.3);
    // soft cap: within 2 cm of the limit the pelvis eases in (no visible kink when a leg straightens)
    const over = pz - (zmax - 0.02);
    if (over > 0) pz = zmax - 0.02 + 0.02 * (1 - Math.exp(-over / 0.02));
  }
  const pelvis: V3 = [pxy[0], pxy[1], pz];
  // pelvis attitude: 35 % of the trunk pitch, pelvic drop on the swing side (Trendelenburg) + keyed roll share
  const pLean = 0.35 * lean + 0.04;
  const pRoll = 0.075 * amp * (sw[0] - sw[1]) * (wsum < 1.5 ? 1 : 0) + 0.25 * roll + (clip.pelvisRoll ? keyAt(clip.pelvisRoll, t) : 0);
  const hipsUp = norm(add(add(mul(UP, Math.cos(pLean)), mul(fwd(hipYaw), Math.sin(pLean))), mul(right(hipYaw), -Math.sin(pRoll))));
  const pr = norm(cross(fwd(hipYaw), hipsUp)); // pelvis right (tilted)
  const prr: V3 = dot(pr, right(hipYaw)) < 0 ? mul(pr, -1) : pr;
  const hips: [V3, V3] = [add(pelvis, mul(prr, -c.hipHalf)), add(pelvis, mul(prr, c.hipHalf))];
  // trunk
  const trunk = norm(add(add(mul(UP, Math.cos(lean)), mul(fwd(chestYaw), Math.sin(lean))), mul(right(h), -Math.sin(roll))));
  const chest = add(pelvis, mul(trunk, c.dims.trunk));
  const head = add(chest, mul(norm(add(trunk, mul(UP, 0.6))), c.dims.neck + c.dims.headR * 0.85));
  const cr = right(chestYaw);
  const sb = add(chest, mul(trunk, -0.04));
  const shoulders: [V3, V3] = [add(sb, mul(cr, -c.dims.shW)), add(sb, mul(cr, c.dims.shW))];
  chestYaw = wrap(chestYaw);
  return {t, root: r, speed, h, chestYaw, hipYaw, lean, roll, feet, pelvis, hipsUp, hips, trunk, chest, head, shoulders, amp, air};
};

// ---------------------------------------------------------------- arms + ball
type ArmOut = {tip: [V3, V3]; dir: [V3, V3]; pole: [V3, V3]; palm: [V3 | null, V3 | null]; ball?: V3; pw?: [number, number]};
const BR = BALL_R + 0.012; // palm centre to ball centre

const engineBall = (play: Play, t: number): V3 => sample(play, clamp(t, 0, play.duration)).ball.pos as V3;

/** two hands on the sides of the ball, fingers forward-up, from the body toward the ball */
const grip2 = (b: Body, c: RigC, ball: V3): ArmOut => {
  const toB = sub(ball, b.chest);
  const Fb = norm([toB[0], toB[1], 0]);
  const Rb: V3 = [Fb[1], -Fb[0], 0];
  const out: ArmOut = {tip: [ball, ball], dir: [UP, UP], pole: [UP, UP], palm: [null, null], ball};
  for (let i = 0; i < 2; i++) {
    const s = i === 0 ? -1 : 1;
    const n = norm(add(add(mul(Rb, s * 0.92), mul(Fb, -0.3)), mul(UP, 0.04)));
    const palm = add(ball, mul(n, BR));
    const d = norm(add(mul(Fb, 0.72), mul(UP, 0.62)));
    out.palm[i] = palm;
    out.dir[i] = d;
    out.tip[i] = add(palm, mul(d, c.handLen * 0.55));
    out.pole[i] = norm(add(add(mul(Rb, s * 0.8), mul(UP, -0.55)), mul(Fb, -0.2)));
  }
  return out;
};

/** shooting grip: right palm under / behind the ball (n = palm side), guide hand on the left side */
const gripShot = (b: Body, c: RigC, ball: V3, rel: number): ArmOut => {
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  const n = norm(lerp3(add(mul(F, -0.7), mul(UP, -0.7)), add(mul(F, -0.92), mul(UP, -0.38)), rel));
  const palmR = add(ball, mul(n, BR));
  const dR = norm(sub(lerp3(UP, add(mul(UP, 0.55), mul(F, 0.83)), rel), mul(n, dot(lerp3(UP, add(mul(UP, 0.55), mul(F, 0.83)), rel), n))));
  const palmL = add(ball, mul(norm(add(mul(R, -0.95), mul(F, -0.15))), BR));
  const dL = norm(add(mul(UP, 0.85), mul(F, 0.25)));
  return {
    ball,
    palm: [rel > 0.85 ? null : palmL, palmR],
    dir: [dL, dR],
    tip: [add(palmL, mul(dL, c.handLen * 0.55)), add(palmR, mul(dR, c.handLen * 0.55))],
    pole: [norm(add(mul(R, -0.8), mul(UP, -0.5))), norm(add(add(mul(UP, -0.75), mul(F, 0.25)), mul(R, 0.2)))],
  };
};

const armRel = (b: Body, i: number, x: number, y: number, z: number): V3 => {
  const s = i === 0 ? -1 : 1;
  return add(b.shoulders[i], add(add(mul(right(b.chestYaw), s * x), mul(fwd(b.chestYaw), y)), [0, 0, z]));
};
const free = (b: Body, f: (i: number) => {tip: V3; dir: V3; pole: V3}): ArmOut => {
  const a = f(0), z = f(1);
  return {tip: [a.tip, z.tip], dir: [a.dir, z.dir], pole: [a.pole, z.pole], palm: [null, null]};
};

const pocketBall = (b: Body) => add(add(b.chest, mul(fwd(b.chestYaw), 0.3)), add(mul(UP, -0.24), mul(right(b.chestYaw), 0.04)));
const tripleBall = (b: Body) => add(add(b.pelvis, mul(fwd(b.chestYaw), 0.27)), add(mul(right(b.chestYaw), 0.2), mul(UP, 0.2)));
const jabBall = (b: Body) => add(add(b.pelvis, mul(fwd(b.chestYaw), 0.16)), add(mul(right(b.chestYaw), 0.27), mul(UP, 0.1)));
const gatherBall = (b: Body) => add(add(b.chest, mul(fwd(b.chestYaw), 0.3)), add(mul(UP, -0.3), mul(right(b.chestYaw), 0.06)));
const setBall = (b: Body) => add(add(b.head, mul(fwd(b.chestYaw), 0.2)), add(mul(UP, 0.08), mul(right(b.chestYaw), 0.1)));

type Ctx = {clip: Clip31; play: Play; id: string; c: RigC; jumpH: number};

const modeOut = (x: Ctx, m: ArmKey['m'], b: Body): ArmOut => {
  const {clip, play, c} = x;
  const t = b.t;
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  switch (m) {
    case 'ready':
      return free(b, (i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.12, 0.24, -0.5), dir: norm(add(add(mul(F, 0.5), mul(UP, -0.85)), mul(R, s * 0.12))), pole: norm(add(add(mul(R, s * 0.6), mul(F, -0.5)), mul(UP, -0.3)))};
      });
    case 'run':
      return free(b, (i) => {
        const s = i === 0 ? -1 : 1;
        const sw = clamp(b.feet[1 - i].fwdness, -1, 1); // this arm goes forward with the opposite leg
        const a = b.amp;
        const y = 0.07 + 0.27 * sw * a;
        const z = -0.5 * (1 - a) + a * (-0.39 + 0.11 * sw);
        const fw = Math.max(0, sw);
        return {tip: armRel(b, i, 0.07 - 0.03 * fw * a, y, z), dir: norm(add(add(mul(F, 0.3 + 0.5 * fw * a), mul(UP, -(0.9 - 0.45 * fw * a))), mul(R, s * -0.15))),
          pole: norm(add(add(mul(F, -0.85), mul(R, s * 0.35)), mul(UP, -0.2)))};
      });
    case 'brake':
      return free(b, (i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.26, 0.3, -0.3 + (i === 0 ? 0.06 : 0)), dir: norm(add(add(mul(F, 0.8), mul(UP, -0.35)), mul(R, s * 0.25))), pole: norm(add(add(mul(R, s * 0.7), mul(UP, -0.6)), mul(F, -0.2)))};
      });
    case 'reach': {
      const tc = clip.ball.catchT!;
      return grip2(b, c, engineBall(play, tc));
    }
    case 'give': {
      const tc = clip.ball.catchT!;
      const u = smooth((t - tc) / 0.38);
      return grip2(b, c, lerp3(engineBall(play, tc), pocketBall(b), u));
    }
    case 'pocket':
      return grip2(b, c, pocketBall(b));
    case 'triple':
      return grip2(b, c, tripleBall(b));
    case 'jab':
      return grip2(b, c, jabBall(b));
    case 'gather':
      return grip2(b, c, gatherBall(b));
    case 'dribble': {
      const d = clip.ball.dribble!;
      const S0 = jabBall(bodyAt(clip, play, x.id, c, d.push, x.jumpH));
      const S1 = gatherBall(bodyAt(clip, play, x.id, c, d.catch, x.jumpH));
      const bf = bodyAt(clip, play, x.id, c, d.floor, x.jumpH);
      const Fp: V3 = add(add(bf.root, add(mul(fwd(bf.chestYaw), 0.46), mul(right(bf.chestYaw), 0.32))), [0, 0, BALL_R]);
      let ball: V3;
      if (t <= d.floor) {
        const u = clamp((t - d.push) / (d.floor - d.push));
        ball = lerp3(S0, Fp, u * u * (1.6 - 0.6 * u)); // pushed down: accelerating
      } else {
        const u = clamp((t - d.floor) / (d.catch - d.floor));
        ball = lerp3(Fp, S1, 1 - (1 - u) * (1 - u) * (1 - 0.35 * u)); // rebound: decelerating into the hand
      }
      // right hand rides the top of the ball while in contact, hovers at the waist while the ball is away
      const u0 = clamp((t - d.push) / (d.catch - d.push));
      const hover = lerp(S0[2] + BR, S1[2] + BR, u0) - 0.16 * Math.sin(Math.PI * u0);
      const top = ball[2] + BR;
      const palmR: V3 = [ball[0], ball[1], Math.max(top, hover)];
      const dR = norm(add(add(mul(F, 0.85), mul(UP, -0.25)), mul(R, -0.1)));
      const touching = top >= hover - 0.005;
      return {
        ball,
        palm: [null, touching ? palmR : null],
        dir: [norm(add(mul(F, 0.7), mul(R, 0.35))), dR],
        tip: [armRel(b, 0, 0.28, 0.32, -0.26), add(palmR, mul(dR, c.handLen * 0.55))],
        pole: [norm(add(mul(R, -0.7), mul(UP, -0.6))), norm(add(add(mul(R, 0.75), mul(F, -0.3)), mul(UP, -0.3)))],
      };
    }
    case 'set':
      return gripShot(b, c, setBall(b), 0);
    case 'shoot': {
      const tr = clip.ball.releaseT!;
      const u = smooth((t - (tr - 0.2)) / 0.2);
      const Rp = engineBall(play, tr);
      return gripShot(b, c, lerp3(setBall(b), Rp, u), u);
    }
    case 'follow': {
      const reach = c.arm * 0.985;
      const dR = norm(add(mul(F, 0.62), mul(UP, -0.78)));
      const wR = add(b.shoulders[1], mul(norm(add(add(mul(F, 0.5), mul(UP, 0.86)), mul(R, -0.05))), reach));
      const wL = add(b.shoulders[0], mul(norm(add(add(mul(F, 0.38), mul(UP, 0.88)), mul(R, 0.12))), reach * 0.9));
      const dL = norm(add(mul(UP, 0.75), mul(F, 0.4)));
      return {tip: [add(wL, mul(dL, c.handLen)), add(wR, mul(dR, c.handLen))], dir: [dL, dR], pole: [norm(add(mul(R, -0.8), mul(UP, -0.4))), norm(add(mul(R, 0.6), mul(UP, -0.6)))], palm: [null, null]};
    }
    case 'land':
      return free(b, (i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.2, 0.26, -0.4), dir: norm(add(add(mul(F, 0.45), mul(UP, -0.85)), mul(R, s * 0.15))), pole: norm(add(mul(R, s * 0.7), mul(UP, -0.6)))};
      });
    case 'defense':
      return free(b, (i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.5, 0.2, -0.14), dir: norm(add(add(mul(R, s * 0.65), mul(F, 0.35)), mul(UP, 0.3))), pole: norm(add(mul(UP, -0.85), mul(F, -0.3)))};
      });
  }
};

const armsAt = (x: Ctx, b: Body): ArmOut => {
  const ks = x.clip.arms;
  let k = 0;
  while (k + 1 < ks.length && ks[k + 1].t <= b.t) k++;
  const cur = modeOut(x, ks[k].m, b);
  if (k === 0) return cur;
  const u = ks[k].b > 0 ? smooth((b.t - ks[k].t) / ks[k].b) : 1;
  if (u >= 1) return cur;
  const prev = modeOut(x, ks[k - 1].m, b);
  const L = (a: V3, z: V3) => lerp3(a, z, u);
  const out: ArmOut = {
    tip: [L(prev.tip[0], cur.tip[0]), L(prev.tip[1], cur.tip[1])],
    dir: [norm(L(prev.dir[0], cur.dir[0])), norm(L(prev.dir[1], cur.dir[1]))],
    pole: [norm(L(prev.pole[0], cur.pole[0])), norm(L(prev.pole[1], cur.pole[1]))],
    palm: [cur.palm[0] && prev.palm[0] ? L(prev.palm[0], cur.palm[0]) : cur.palm[0] ?? prev.palm[0], cur.palm[1] && prev.palm[1] ? L(prev.palm[1], cur.palm[1]) : cur.palm[1] ?? prev.palm[1]],
    // contact weight of each palm target: a hand that is joining / leaving the ball is corrected only in proportion
    pw: [0, 1].map((i) => (cur.palm[i] && prev.palm[i] ? 1 : cur.palm[i] ? u : prev.palm[i] ? 1 - u : 0)) as [number, number],
  };
  if (cur.ball && prev.ball) out.ball = L(prev.ball, cur.ball);
  else out.ball = cur.ball ?? prev.ball;
  return out;
};

// ---------------------------------------------------------------- head
const lookAt = (x: Ctx, b: Body): {yaw: number; pitch: number} => {
  const ks = x.clip.look;
  const eye = b.head;
  const yawPitchOf = (at: string | number): [number, number] => {
    if (typeof at === 'number') return [at, 0.12];
    if (at === 'path') return [b.h, 0.18];
    let p: V3;
    if (at === 'rim') p = [0, 1.575, 3.05];
    else if (at === 'ball') p = x.play && b.t ? ballOf(x, b.t) : [0, 0, 1];
    else {
      const q = posAt(x.play.tracks[at], clamp(b.t, 0, x.play.duration));
      p = [q[0], q[1], 1.45];
    }
    const d = sub(p, eye);
    return [Math.atan2(d[1], d[0]), clamp(Math.atan2(-(d[2]), Math.hypot(d[0], d[1])), -0.45, 0.45)];
  };
  let k = 0;
  while (k + 1 < ks.length && ks[k + 1].t <= b.t) k++;
  let [yw, pt] = yawPitchOf(ks[k].at);
  if (k > 0) {
    const u = smooth((b.t - ks[k].t) / (ks[k].b ?? 0.25));
    if (u < 1) {
      const [y0, p0] = yawPitchOf(ks[k - 1].at);
      yw = y0 + wrap(yw - y0) * u;
      pt = lerp(p0, pt, u);
    }
  }
  // the neck turns at most 70 deg off the shoulders
  const off = clamp(wrap(yw - b.chestYaw), -1.22, 1.22);
  return {yaw: b.chestYaw + off, pitch: pt};
};

// ---------------------------------------------------------------- public API
export type Motion31 = {pose: Pose; hipsUp: V3; ball?: V3; held: boolean; feet: [FootState, FootState]; body: Body; arms: ArmOut; jumpH: number; c: RigC};

/** the ball position while this player's clip owns it (hand socket), else undefined (engine ball) */
const ballOf = (x: Ctx, t: number): V3 => {
  const bl = x.clip.ball;
  if (t >= bl.catchT! && t < bl.releaseT!) {
    const b = bodyAt(x.clip, x.play, x.id, x.c, t, x.jumpH);
    const a = armsAt(x, b);
    if (a.ball) return a.ball;
  }
  return engineBall(x.play, t);
};

const jumpCache = new Map<string, number>();
/** jump height so that the engine release point is reachable by the shooting palm (+ the minimum authored height) */
const jumpHeight = (clip: Clip31, play: Play, id: string, c: RigC): number => {
  if (!clip.jump) return 0;
  const key = `${play.id}|${id}|${c.scale}`;
  const hit = jumpCache.get(key);
  if (hit !== undefined) return hit;
  const tr = clip.ball.releaseT!;
  const Rp = engineBall(play, tr);
  const u = (tr - clip.jump.t0) / (clip.jump.t1 - clip.jump.t0);
  const f = 4 * u * (1 - u);
  let H = clip.jump.H;
  for (let it = 0; it < 30; it++) {
    const b = bodyAt(clip, play, id, c, tr, H);
    const sh = b.shoulders[1];
    const reach = c.arm * 0.985 + c.handLen * 0.42 + BR * 0.55; // shoulder -> ball centre with the palm behind it
    const dh = Math.hypot(Rp[0] - sh[0], Rp[1] - sh[1]);
    const need = Rp[2] - (sh[2] + Math.sqrt(Math.max(0, reach * reach - dh * dh)));
    if (need <= 0.002) break;
    H += need / Math.max(0.3, f);
  }
  H = clamp(H, clip.jump.H, 0.68);
  jumpCache.set(key, H);
  return H;
};

const mcache = new Map<string, Motion31 | null>();
/** authored V3.1 motion of player `id` at play time t, or null when the play has no V3.1 clip for this player */
export const motionV31 = (play: Play, id: string, t: number, rig: RigV3): Motion31 | null => {
  const clip = clipFor(play, id);
  if (!clip) return null;
  const key = `${play.id}|${id}|${t.toFixed(5)}|${rig.variant}`;
  const hit = mcache.get(key);
  if (hit !== undefined) return hit;
  const c = rigConsts(rig, id);
  const jumpH = jumpHeight(clip, play, id, c);
  const x: Ctx = {clip, play, id, c, jumpH};
  const b = bodyAt(clip, play, id, c, t, jumpH);
  const a = armsAt(x, b);
  const held = t >= clip.ball.catchT! && t < clip.ball.releaseT!;
  const look = lookAt(x, b);
  const dz: V3 = [0, 0, -c.ankleOff]; // mesh space -> engine space (bonesFromPose adds ankleOff back)
  const E = (p: V3) => add(p, dz);
  const toeOf = (f: FootState): V3 => add(E(f.ankle), add(mul(fwd(f.yaw), c.dims.foot * 0.78), [0, 0, -c.dims.ankleH * 0.7]));
  const elbow = (i: number): V3 => add(b.shoulders[i], mul(a.pole[i], 0.2));
  const pose: Pose = {
    pelvis: E(b.pelvis), chest: E(b.chest), head: E(b.head), heading: b.h, chestYaw: b.chestYaw, lean: b.lean, roll: b.roll,
    hip: [E(b.hips[0]), E(b.hips[1])],
    knee: [E(add(lerp3(b.hips[0], b.feet[0].ankle, 0.5), mul(fwd(b.feet[0].yaw), 0.3))), E(add(lerp3(b.hips[1], b.feet[1].ankle, 0.5), mul(fwd(b.feet[1].yaw), 0.3)))],
    ankle: [E(b.feet[0].ankle), E(b.feet[1].ankle)],
    toe: [toeOf(b.feet[0]), toeOf(b.feet[1])],
    shoulder: [E(b.shoulders[0]), E(b.shoulders[1])],
    elbow: [E(elbow(0)), E(elbow(1))],
    wrist: [E(sub(a.tip[0], mul(a.dir[0], 0.1))), E(sub(a.tip[1], mul(a.dir[1], 0.1)))],
    hand: [E(a.tip[0]), E(a.tip[1])],
    airborne: Math.max(0, b.air),
    headYaw: look.yaw,
    headPitch: look.pitch,
    dims: c.dims,
  };
  const out: Motion31 = {pose, hipsUp: b.hipsUp, ball: held ? a.ball : undefined, held, feet: b.feet, body: b, arms: a, jumpH, c};
  if (mcache.size > 20000) mcache.clear();
  mcache.set(key, out);
  return out;
};

/** the V3.1 bones: palm correction (the real mesh palm onto the hand socket, 2 passes of the arm IK), V3 hands / grip /
 *  correctives, pelvis tilted on its own axis (hipsUp), foot pitch (toe-off, heel strike, landing on the ball) */
export const framesV31 = (rig: RigV3, m: Motion31): V3Frame => {
  const P: Pose = {...m.pose, hand: [...m.pose.hand] as [V3, V3], wrist: [...m.pose.wrist] as [V3, V3]};
  const sc = m.c.scale;
  for (let it = 0; it < 2; it++) {
    if (!m.arms.palm[0] && !m.arms.palm[1]) break;
    const base = bonesFromPose(baseRig(rig), P, sc, m.hipsUp);
    for (let i = 0; i < 2; i++) {
      const want = m.arms.palm[i];
      if (!want) continue;
      const got = palmWorld(rig, base.bones, base.hips, sc, i === 0 ? 'L' : 'R');
      // only where the socket is within reach of the mesh shoulder (a straight arm flips its hinge: no chasing)
      const lim = m.c.arm * 0.97 + m.c.handLen * 0.45;
      const reachW = 1 - smooth((len(sub(want, m.body.shoulders[i])) - (lim - 0.1)) / 0.1); // fades out near full reach
      let e = mul(sub(want, got), (m.arms.pw?.[i] ?? 1) * reachW);
      if (len(e) > 0.08) e = mul(norm(e), 0.08);
      P.hand[i] = add(P.hand[i], e);
      P.wrist[i] = add(P.wrist[i], e);
    }
  }
  const fr = bonesV3(rig, P, sc, m.ball ? {pos: m.ball, held: m.held} : undefined, undefined, m.hipsUp);
  // foot pitch about the foot's own lateral axis (world): + = heel up (toes stay flat), - = toe up (toes follow). The
  // shared bonesFromPose leaves the e2a foot ~4.7 deg toes-down (ball of the foot 1.2 cm under the floor, heel 0.5 cm
  // over it, measured by qc-realism-v31): the slope heel -> ball is measured on the solved bones and removed first
  const at = fkHeads(rig, fr.bones, fr.hips, sc);
  for (let i = 0; i < 2; i++) {
    const s = i === 0 ? 'L' : 'R';
    const f = m.feet[i];
    const fb = rig.bones.find((b) => b.name === `foot.${s}`)!;
    const D = qmul(fr.bones[`foot.${s}`], qconj(fb.R));
    const A = at(`foot.${s}`);
    const P = (k: string): V3 => add(A, qrot(D, mul(sub(rig.restJoints[k], fb.head), sc)));
    const hb = P(`heel${s}`), bb = P(`ball${s}`);
    const slope = Math.atan2(bb[2] - hb[2], Math.hypot(bb[0] - hb[0], bb[1] - hb[1]));
    const q = axisAngle(right(f.yaw), -f.pitch - slope);
    fr.bones[`foot.${s}`] = qmul(q, fr.bones[`foot.${s}`]);
    if (f.pitch < 0 || f.support < 1) fr.bones[`toe.${s}`] = qmul(q, fr.bones[`toe.${s}`]);
  }
  return fr;
};

/** the ball as V3.1 shows it: the hand socket of the clip that holds it, else the engine ball (undefined) */
export const ballV31 = (play: Play, t: number, rigOf: (id: string) => RigV3): V3 | undefined => {
  for (const p of play.players) {
    const m = clipFor(play, p.id) ? motionV31(play, p.id, t, rigOf(p.id)) : null;
    if (m?.ball) return m.ball;
  }
  return undefined;
};

/** QA only: empty the memo caches (the seek test recomputes a frame from scratch) */
export const resetV31Caches = () => {
  mcache.clear();
  ccache.clear();
  jumpCache.clear();
};

// ---------------------------------------------------------------- cloth L1 driven by the authored body
export const CLOTH31 = {hz: 1.7, zeta: 0.26, gain: 0.85, vgain: 0.02, drag: 0.0016, maxH: 0.085, maxUp: 0.075, maxDown: 0.035, maxTwist: 0.24, flutter: 0.006};
const ccache = new Map<string, Cloth>();
/** hem secondary motion from the AUTHORED pelvis (horizontal accel -> lag / swing, vertical accel -> flare in the jump
 *  and settle on landing, pelvis yaw accel -> twist), damped spring integrated from t - 1.2 s at 120 Hz: pure in t */
export const clothV31 = (play: Play, id: string, t: number, rig: RigV3): Cloth | undefined => {
  const clip = clipFor(play, id);
  if (!clip) return undefined;
  const key = `${play.id}|${id}|${t.toFixed(5)}`;
  const hit = ccache.get(key);
  if (hit) return hit;
  const c = rigConsts(rig, id);
  const jumpH = jumpHeight(clip, play, id, c);
  const dt = 1 / 120, w = 2 * Math.PI * CLOTH31.hz, z = CLOTH31.zeta;
  const T0 = Math.max(0, t - 1.2);
  const n = Math.max(1, Math.round((t - T0) / dt));
  const pv: {p: V3; yaw: number}[] = [];
  for (let k = -1; k <= n + 1; k++) {
    const b = bodyAt(clip, play, id, c, T0 + k * dt, jumpH);
    pv.push({p: b.pelvis, yaw: b.hipYaw});
  }
  let x = 0, y = 0, zz = 0, th = 0, vx = 0, vy = 0, vz = 0, vth = 0;
  for (let k = 1; k <= n; k++) {
    const A = pv[k], B = pv[k + 1], C = pv[k + 2];
    const ax = (C.p[0] - 2 * B.p[0] + A.p[0]) / (dt * dt), ay = (C.p[1] - 2 * B.p[1] + A.p[1]) / (dt * dt), az = (C.p[2] - 2 * B.p[2] + A.p[2]) / (dt * dt);
    const al = (wrap(C.yaw - B.yaw) - wrap(B.yaw - A.yaw)) / (dt * dt);
    vx += (-w * w * x - 2 * z * w * vx - CLOTH31.gain * clamp(ax, -40, 40)) * dt; x += vx * dt;
    vy += (-w * w * y - 2 * z * w * vy - CLOTH31.gain * clamp(ay, -40, 40)) * dt; y += vy * dt;
    vz += (-w * w * zz - 2 * z * w * vz - CLOTH31.vgain * w * clamp(az, -60, 60)) * dt; zz += vz * dt;
    vth += (-w * w * th - 2 * z * w * vth - 0.6 * clamp(al, -80, 80)) * dt; th += vth * dt;
  }
  const last = pv[n + 1], prev = pv[n];
  const v = [(last.p[0] - prev.p[0]) / dt, (last.p[1] - prev.p[1]) / dt];
  const sp = Math.hypot(v[0], v[1]);
  let sx = x - CLOTH31.drag * v[0] * sp, sy = y - CLOTH31.drag * v[1] * sp;
  const hl = Math.hypot(sx, sy);
  if (hl > CLOTH31.maxH) {
    sx *= CLOTH31.maxH / hl;
    sy *= CLOTH31.maxH / hl;
  }
  const up = clamp(zz + 0.003 * sp, -CLOTH31.maxDown, CLOTH31.maxUp);
  const b = bodyAt(clip, play, id, c, t, jumpH);
  const ph = (b.feet[0].fwdness + 1) / 4;
  const out: Cloth = {sway: [sx, sy, up], twist: clamp(th, -CLOTH31.maxTwist, CLOTH31.maxTwist), flutter: CLOTH31.flutter * Math.min(1, sp / 5), phase: ph};
  if (ccache.size > 40000) ccache.clear();
  ccache.set(key, out);
  return out;
};
