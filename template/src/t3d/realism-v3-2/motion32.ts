// E2A Realism V3.2 (2026-11-22) — motion runtime of the V3.2 athlete (athleteRenderer 'v32', opt-in).
// Evaluates the Clip32 that library.ts BUILDS from a script of primitives (no per-play hand keys). Same contract as
// V3.1 (realism-v3-1/motion.ts, untouched): a PURE function of (play, id, t, rig), so Remotion seeks are exact.
// What changed from V3.1 (owner review of legacy_vs_v3_1_locked_ab_close.mp4):
//   jump shot   ONE phase clock (shotPhase) drives pelvis height, trunk lean, knees (through the feet), ankles (heel
//               rise / toe point), arms and ball: gather -> dip -> load -> takeoff (pelvis leaves with the ballistic
//               velocity v0 = sqrt(2 g H), C1-continuous) -> rise -> release 35 ms before the apex -> follow-through ->
//               descent -> landing on the balls of the feet -> absorption (pelvis 17 cm down, velocity matched) ->
//               recovery. Feet in the air move WITH the pelvis (minus a small knee tuck). V3.1 raised the body on its
//               own parabola while the arms ran an independent schedule.
//   stances     ready / triple threat / defense (wide base, hands outside the shoulders, low hips) / closeout / relaxed
//   ball        explicit states (FREE, INCOMING, FIRST_CONTACT, CONTROLLED, SECURED, DRIBBLE, SHOOT_PREP, RELEASE,
//               FLIGHT, PASS) with owner, hands and palm targets per frame (ballState32, debug overlay)
//   cloth       jersey and shorts get SEPARATE cloth states (cloth32): the shorts swing 3x less, never twist and are
//               capped at 2.5 cm (V3.1 moved the shorts hem 13 cm -> the 3.75 s triangle); per-vertex clamps in the shader
import type {V3} from '../../tactical/geometry.ts';
import type {Play} from '../../tactical/play.ts';
import {posAt, sample} from '../../tactical/play.ts';
import type {Dims, Pose} from '../rig.ts';
import {BALL_R, PLAYER_BUILD, PLAYER_HEIGHTS, dimsFor} from '../rig.ts';
import type {Q} from '../skelclip.ts';
import {bonesFromPose, qconj, qmul, qrot} from '../skelclip.ts';
import type {Cloth} from '../cloth2.ts';
import type {RigV3, V3Frame} from '../realism-v3/athleteV3.ts';
import {baseRig, bonesV3, fkHeads, palmWorld} from '../realism-v3/athleteV3.ts';
import {keyAt} from '../realism-v3-1/motion.ts';
import type {Step} from '../realism-v3-1/clips.ts';
import type {ArmKey32, Clip32} from './library.ts';
import {clip32For} from './clips32.ts';

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
const G = 9.81;
const axisAngle = (ax: V3, th: number): Q => {
  const s = Math.sin(th / 2);
  const n = norm(ax);
  return [n[0] * s, n[1] * s, n[2] * s, Math.cos(th / 2)];
};
/** cubic Hermite on [0, 1] with end values and end slopes (slopes in units per unit u) */
const herm = (p0: number, m0: number, p1: number, m1: number, u: number) => {
  const u2 = u * u, u3 = u2 * u;
  return (2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * m0 + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * m1;
};

// ---------------------------------------------------------------- rig-derived constants (mesh space, scaled)
export type RigC = {scale: number; ankleOff: number; ankleZ: number; dBall: number; dHeel: number; hipHalf: number; pelvisZ: number; legLen: number; arm: number; handLen: number; dims: Dims};
const rigCache = new WeakMap<RigV3, Map<string, RigC>>();
export const rigConsts = (rig: RigV3, id: string): RigC => {
  let m = rigCache.get(rig);
  if (!m) rigCache.set(rig, (m = new Map()));
  const hit = m.get(id);
  if (hit) return hit;
  const dims = dimsFor(PLAYER_HEIGHTS[id] ?? 2.0, PLAYER_BUILD[id] ?? 1);
  const R = rig.restJoints;
  const legRest = len(sub(R.kneeL, R.hipL)) + len(sub(R.ankleL, R.kneeL));
  const scale = (dims.thigh + dims.shin) / legRest;
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
    legLen: len(sub(S('kneeL'), S('hipL'))) + len(sub(S('ankleL'), S('kneeL'))),
    arm: len(sub(S('elbowL'), S('shoulderL'))) + len(sub(S('wristL'), S('elbowL'))),
    handLen: len(sub(S('handL'), S('wristL'))),
  };
  m.set(id, c);
  return c;
};

// ---------------------------------------------------------------- the jump-shot phase clock
export type ShotStage = 'none' | 'gather' | 'dip' | 'load' | 'takeoff' | 'rise' | 'release' | 'follow' | 'descent' | 'landing' | 'recovery';
type ShotP = {stage: ShotStage; dz: number | null; lean: number | null; air: number; w: number; v0: number};
const PUSH = 0.17; // s of leg extension before the feet leave the floor
const ABS = 0.2; // s of landing absorption
/** pelvis height offset (from the standing pelvis), lean and stage of the jump shot at time t (dz = null: not driven) */
export const shotPhase = (clip: Clip32, t: number, baseDrop: number): ShotP => {
  const s = clip.shot;
  if (!s || t <= s.gatherT || t >= s.recoverT) return {stage: 'none', dz: null, lean: null, air: 0, w: 0, v0: 0};
  const v0 = Math.sqrt(2 * G * s.H);
  const DIP = 0.24 + 0.4 * (clip.vary.k.drop ?? 0);
  const zTo = 0.035; // pelvis over its standing height at toe-off (heels up, legs straight)
  const loadT = s.t0 - PUSH;
  const w = smooth((t - s.gatherT) / 0.2) * (1 - smooth((t - (s.recoverT - 0.25)) / 0.25));
  if (t < s.dipT) {
    const u = (t - s.gatherT) / (s.dipT - s.gatherT);
    return {stage: 'gather', dz: -lerp(baseDrop, 0.12, smooth(u)), lean: lerp(0.14, 0.18, smooth(u)), air: 0, w, v0};
  }
  if (t < loadT) {
    const u = (t - s.dipT) / (loadT - s.dipT);
    return {stage: u < 0.7 ? 'dip' : 'load', dz: -lerp(0.12, DIP, smooth(u)), lean: lerp(0.18, 0.3, smooth(u)), air: 0, w, v0};
  }
  if (t < s.t0) {
    const u = (t - loadT) / PUSH;
    // leg extension: from the bottom of the dip (at rest) to toe-off with the take-off velocity (C1 into the flight)
    return {stage: 'takeoff', dz: herm(-DIP, 0, zTo, v0 * PUSH, u), lean: lerp(0.3, 0.05, smooth(u * 1.2)), air: 0, w, v0};
  }
  if (t < s.t1) {
    const tau = t - s.t0;
    const dz = zTo + v0 * tau - 0.5 * G * tau * tau;
    const st: ShotStage = t < s.release - 0.06 ? 'rise' : t < s.release + 0.03 ? 'release' : t < s.release + 0.2 ? 'follow' : 'descent';
    return {stage: st, dz, lean: t < s.release ? lerp(0.05, -0.02, smooth((t - s.t0) / (s.release - s.t0))) : lerp(-0.02, 0.1, smooth((t - s.release) / (s.t1 - s.release))), air: dz - zTo, w, v0};
  }
  if (t < s.t1 + ABS) {
    const u = (t - s.t1) / ABS;
    // landing: velocity -v0 absorbed into a 17 cm knee / hip flexion, zero velocity at the bottom
    return {stage: 'landing', dz: herm(zTo, -v0 * ABS, -0.17, 0, u), lean: lerp(0.1, 0.24, smooth(u)), air: 0, w, v0};
  }
  const u = (t - s.t1 - ABS) / (s.recoverT - s.t1 - ABS);
  return {stage: 'recovery', dz: lerp(-0.17, -baseDrop, smooth(u)), lean: lerp(0.24, 0.18, smooth(u)), air: 0, w, v0};
};

// ---------------------------------------------------------------- feet
export type FootState = {g: V3; yaw: number; pitch: number; support: number; fwdness: number; ankle: V3; planted: boolean};
const anchorOf = (clip: Clip32, root: (t: number) => V3, st: {f: number; l: number; yaw?: number}, t: number, side: 0 | 1): {g: V3; yaw: number} => {
  const h = keyAt(clip.heading, t);
  const r = root(t);
  const w = keyAt(clip.stanceW, t) * (side === 0 ? -1 : 1);
  const p = add(add(r, mul(fwd(h), st.f)), mul(right(h), st.l + w));
  return {g: [p[0], p[1], 0], yaw: h + (st.yaw ?? 0) + (side === 0 ? 0.1 : -0.1) + (side === 0 ? 1 : -1) * 2.2 * keyAt(clip.stanceW, t) * 0.5};
};

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

const plantedAt = (clip: Clip32, c: RigC, side: 0 | 1, anchor: {g: V3; yaw: number}, landT: number, t: number): {g: V3; yaw: number} => {
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

const footAt = (clip: Clip32, c: RigC, root: (t: number) => V3, side: 0 | 1, t: number): FootState => {
  const steps = clip.steps.filter((s) => s.s === side);
  let prev = anchorOf(clip, root, clip.init[side], 0, side);
  let prevLand = -1;
  let prevStep: Step | undefined;
  for (let k = 0; k < steps.length; k++) {
    const st = steps[k];
    if (t < st.lift) break;
    const tgt = anchorOf(clip, root, st, st.land, side);
    if (t < st.land) {
      prev = plantedAt(clip, c, side, prev, prevLand, st.lift);
      const u = (t - st.lift) / (st.land - st.lift);
      const hs = 0.5 - 0.5 * Math.cos(Math.PI * clamp(u * 1.08));
      let z: number;
      let pitch: number;
      if (st.air) {
        // in the jump the feet ride WITH the pelvis (coupled), knees tuck a little at the apex, toes point down
        const ph = shotPhase(clip, t, 0);
        z = Math.max(0, ph.air) + 0.05 * Math.sin(Math.PI * u);
        pitch = 0.62 * (1 - u) * (1 - u) + 0.42 * Math.sin(Math.PI * u) + (st.heel ?? 0.3) * u * u * u;
      } else {
        z = (st.h ?? 0.09) * Math.pow(Math.sin(Math.PI * u), 0.85);
        const toeOff = st.toeOff ?? 0.42;
        pitch = toeOff * (1 - u) * (1 - u) + 0.28 * Math.sin(Math.PI * u) + (st.heel ?? 0.05) * u * u * u;
      }
      const yaw = prev.yaw + wrap(tgt.yaw - prev.yaw) * hs;
      const g: V3 = [lerp(prev.g[0], tgt.g[0], hs), lerp(prev.g[1], tgt.g[1], hs), z];
      return {g, yaw, pitch, support: 0, fwdness: -1 + 2 * smooth(u), ankle: ankleOf(c, g, yaw, pitch), planted: false};
    }
    prev = tgt;
    prevLand = st.land;
    prevStep = st;
  }
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
  let support = prevLand < 0 ? 1 : smooth((t - prevLand) / 0.12);
  if (next) support = Math.min(support, 1 - smooth((t - (next.lift - 0.08)) / 0.08));
  let fwdness = 1;
  if (next) {
    // heel rise before the lift; for the jump it follows the leg extension (the ankle plantar-flexes during the push)
    const toeOff = next.air ? 0.62 : next.toeOff ?? 0.42;
    const win = next.air ? PUSH : 0.13;
    pitch += toeOff * smooth((t - (next.lift - win)) / win);
    // continuous at both ends: from standing (no previous landing) it eases 0 -> -1 into the lift, after the last
    // landing 1 -> 0 (a jump 0 -> -1 at the first lift swung the opposite arm 12 cm in one frame, QC 1.92 s)
    fwdness = prevLand < 0 ? -smooth((t - (next.lift - 0.3)) / 0.3) : 1 - 2 * clamp((t - prevLand) / Math.max(0.05, next.lift - prevLand));
  } else fwdness = prevLand < 0 ? 0 : 1 - smooth((t - prevLand) / 0.3);
  return {g, yaw, pitch, support, fwdness, ankle: ankleOf(c, g, yaw, pitch), planted: true};
};

// ---------------------------------------------------------------- body
export type Body = {
  t: number; root: V3; speed: number; h: number; chestYaw: number; hipYaw: number; lean: number; roll: number;
  feet: [FootState, FootState]; pelvis: V3; hipsUp: V3; hips: [V3, V3]; trunk: V3; chest: V3; head: V3; shoulders: [V3, V3]; amp: number; air: number; shot: ShotP;
};

export const bodyAt = (clip: Clip32, play: Play, id: string, c: RigC, t: number): Body => {
  const wp = play.tracks[id];
  const root = (x: number): V3 => {
    const p = posAt(wp, clamp(x, 0, play.duration));
    return [p[0], p[1], 0];
  };
  const r = root(t);
  const r0 = root(t - 0.05), r1 = root(t + 0.05);
  const speed = Math.hypot(r1[0] - r0[0], r1[1] - r0[1]) / 0.1;
  const amp = smooth(speed / 3.2) * clip.vary.k.swing;
  const h = keyAt(clip.heading, t);
  const fL = footAt(clip, c, root, 0, t);
  const fR = footAt(clip, c, root, 1, t);
  const feet: [FootState, FootState] = [fL, fR];
  const legDiff = (fR.fwdness - fL.fwdness) / 2;
  const hipYaw = h + 0.16 * amp * legDiff;
  let chestYaw = h + keyAt(clip.chest, t) - 0.13 * amp * legDiff;
  const baseDrop = keyAt(clip.drop, t);
  const sp = shotPhase(clip, t, baseDrop);
  let lean = keyAt(clip.lean, t);
  if (sp.lean !== null) lean = lerp(lean, sp.lean, sp.w);
  const roll = keyAt(clip.roll, t);
  let bob = 0;
  for (const st of clip.steps) if (!st.air && Math.abs(t - st.land - 0.07) < 0.2) bob += 0.03 * amp * Math.exp(-(((t - st.land - 0.07) / 0.075) ** 2));
  const sw = [fL.support, fR.support];
  const wsum = sw[0] + sw[1];
  const R = right(h);
  const latAt = (x: number, a: FootState, z: FootState) => {
    const ws = a.support + z.support;
    if (ws <= 1e-4) return 0;
    const mid = add(mul(a.g, a.support / ws), mul(z.g, z.support / ws));
    return clamp(dot(sub(mid, root(x)), right(keyAt(clip.heading, x))), -0.12, 0.12) * 0.35 * smooth(ws / 0.3);
  };
  // Gaussian low-pass over +-0.08 s at 10 ms (5 taps at 40 ms aliased the support switches: 1 cm pelvis jitter, QC 3.27 s)
  let lat = 0, lw = 0;
  for (let k = -8; k <= 8; k++) {
    const x = t + k * 0.01;
    const w = Math.exp(-(((k * 0.01) / 0.045) ** 2) / 2);
    lat += w * (k === 0 ? latAt(t, fL, fR) : latAt(x, footAt(clip, c, root, 0, x), footAt(clip, c, root, 1, x)));
    lw += w;
  }
  lat /= lw;
  const pxy = add(r, mul(R, lat));
  const stand = c.pelvisZ * 0.992;
  let pz = stand - baseDrop - bob;
  if (sp.dz !== null) pz = lerp(pz, stand + sp.dz, sp.w);
  const inAir = !!clip.shot && t > clip.shot.t0 && t < clip.shot.t1;
  // leg-reach cap: how far a supporting leg pulls the pelvis down at time x. On the ground it is low-passed over
  // +-0.12 s (Gaussian): a hard cap that releases at lift-off popped the pelvis up to 19 cm in 3 frames (QC, 2.78 s)
  const capDrop = (x: number, pz0: number, fs: [FootState, FootState], pc: V3, air: boolean) => {
    let z = pz0;
    for (let i = 0; i < 2; i++) {
      const f = fs[i];
      if (f.support <= 0.001 && !air) continue;
      const side = i === 0 ? -1 : 1;
      const hp = add(pc, mul(right(hipYaw), side * c.hipHalf));
      const dh = Math.hypot(hp[0] - f.ankle[0], hp[1] - f.ankle[1]);
      const L = c.legLen * 0.955; // margin for the mesh hip joint (pelvis tilt / width), so the mesh reach guard stays idle
      const zmax = f.ankle[2] + Math.sqrt(Math.max(0, L * L - dh * dh)) + (air ? 0 : (1 - f.support) * 0.3);
      const over = z - (zmax - 0.02);
      const w = air ? 1 : smooth(f.support / 0.35);
      if (over > 0) z = lerp(z, zmax - 0.02 + 0.02 * (1 - Math.exp(-over / 0.02)), w);
    }
    return pz0 - z;
  };
  if (inAir) pz -= capDrop(t, pz, feet, pxy, true);
  else {
    // smooth maximum (log-sum-exp, tau 1 cm) of the Gaussian-tapered drops: never less than the drop needed now
    // (the leg reaches its planted foot), C1 in time (no pop when a leg's cap hands over)
    const TAU = 0.01;
    let acc = 0;
    for (let k = -12; k <= 12; k++) {
      const x = t + k * 0.01;
      const w = Math.exp(-(((k * 0.01) / 0.07) ** 2) / 2);
      const fx: [FootState, FootState] = k === 0 ? feet : [footAt(clip, c, root, 0, x), footAt(clip, c, root, 1, x)];
      acc += w * Math.exp(capDrop(x, pz, fx, add(root(x), mul(R, lat)), false) * w / TAU);
    }
    pz -= Math.max(0, TAU * Math.log(acc));
  }
  const pelvis: V3 = [pxy[0], pxy[1], pz];
  const pLean = 0.38 * lean + 0.04;
  const pRoll = 0.075 * amp * (sw[0] - sw[1]) * (wsum < 1.5 ? 1 : 0) + 0.25 * roll + keyAt(clip.pelvisRoll ?? [[0, 0]], t);
  const hipsUp = norm(add(add(mul(UP, Math.cos(pLean)), mul(fwd(hipYaw), Math.sin(pLean))), mul(right(hipYaw), -Math.sin(pRoll))));
  const pr = norm(cross(fwd(hipYaw), hipsUp));
  const prr: V3 = dot(pr, right(hipYaw)) < 0 ? mul(pr, -1) : pr;
  const hips: [V3, V3] = [add(pelvis, mul(prr, -c.hipHalf)), add(pelvis, mul(prr, c.hipHalf))];
  const trunk = norm(add(add(mul(UP, Math.cos(lean)), mul(fwd(chestYaw), Math.sin(lean))), mul(right(h), -Math.sin(roll))));
  const chest = add(pelvis, mul(trunk, c.dims.trunk));
  const head = add(chest, mul(norm(add(trunk, mul(UP, 0.6))), c.dims.neck + c.dims.headR * 0.85));
  const cr = right(chestYaw);
  const sb = add(chest, mul(trunk, -0.04));
  // shoulder girdle: elevates with the arms in the shot (shrug follows the raised arms instead of a rigid yoke)
  const shrug = sp.stage === 'rise' || sp.stage === 'release' || sp.stage === 'follow' ? 0.025 : 0;
  const shoulders: [V3, V3] = [add(add(sb, mul(cr, -c.dims.shW)), [0, 0, shrug * 0.6]), add(add(sb, mul(cr, c.dims.shW)), [0, 0, shrug])];
  chestYaw = wrap(chestYaw);
  return {t, root: r, speed, h, chestYaw, hipYaw, lean, roll, feet, pelvis, hipsUp, hips, trunk, chest, head, shoulders, amp, air: sp.air, shot: sp};
};

// ---------------------------------------------------------------- arms + ball
export type ArmOut = {tip: [V3, V3]; dir: [V3, V3]; pole: [V3, V3]; palm: [V3 | null, V3 | null]; ball?: V3; pw?: [number, number]};
const BR = BALL_R + 0.012;
const engineBall = (play: Play, t: number): V3 => sample(play, clamp(t, 0, play.duration)).ball.pos as V3;

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

/** shooting grip: right palm under / behind the ball, fingers up, guide hand on the left side (thumb back) */
const gripShot = (b: Body, c: RigC, ball: V3, rel: number): ArmOut => {
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  const n = norm(lerp3(add(mul(F, -0.62), mul(UP, -0.78)), add(mul(F, -0.92), mul(UP, -0.38)), rel));
  const palmR = add(ball, mul(n, BR));
  const dd = lerp3(UP, add(mul(UP, 0.55), mul(F, 0.83)), rel);
  const dR = norm(sub(dd, mul(n, dot(dd, n))));
  const palmL = add(ball, mul(norm(add(mul(R, -0.95), mul(F, -0.12))), BR));
  const dL = norm(add(mul(UP, 0.88), mul(F, 0.2)));
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
const free = (f: (i: number) => {tip: V3; dir: V3; pole: V3}): ArmOut => {
  const a = f(0), z = f(1);
  return {tip: [a.tip, z.tip], dir: [a.dir, z.dir], pole: [a.pole, z.pole], palm: [null, null]};
};

// ball anchors: clear of the trunk / thigh / face capsules by >= 1 cm (QC ball-body: pocket 4.8 cm into the chest,
// dribble floor point 5 cm into the stepping thigh, set point 4.9 cm into the face — V3.2 moved them out)
const pocketBall = (b: Body) => add(add(b.chest, mul(fwd(b.chestYaw), 0.34)), add(mul(UP, -0.24), mul(right(b.chestYaw), 0.04)));
const tripleBall = (b: Body) => add(add(b.pelvis, mul(fwd(b.chestYaw), 0.27)), add(mul(right(b.chestYaw), 0.2), mul(UP, 0.2)));
const jabBall = (b: Body) => add(add(b.pelvis, mul(fwd(b.chestYaw), 0.16)), add(mul(right(b.chestYaw), 0.27), mul(UP, 0.1)));
const gatherBall = (b: Body) => add(add(b.chest, mul(fwd(b.chestYaw), 0.33)), add(mul(UP, -0.3), mul(right(b.chestYaw), 0.06)));
const chestBall = (b: Body) => add(add(b.chest, mul(fwd(b.chestYaw), 0.28)), add(mul(UP, -0.02), mul(right(b.chestYaw), 0.08)));
const setBall = (b: Body) => add(add(b.head, mul(fwd(b.chestYaw), 0.24)), add(mul(UP, 0.12), mul(right(b.chestYaw), 0.11)));

type Ctx = {clip: Clip32; play: Play; id: string; c: RigC};

/** the jump-shot arms + ball, driven by the SAME phase clock as the legs (shotPhase): the ball travels pocket -> chest
 *  (dip) -> set point over the forehead (during the leg push, one motion) -> the release point (elbow extension while
 *  rising) -> released 35 ms before the apex; follow-through (wrist flexed, arm high) until the landing, arms come down
 *  with the absorption */
const jumpshotOut = (x: Ctx, b: Body): ArmOut => {
  const s = x.clip.shot!;
  const t = b.t;
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  const loadT = s.t0 - PUSH;
  if (t < s.release) {
    let ball: V3;
    let rel = 0;
    if (t < s.dipT) ball = lerp3(gatherBall(b), pocketBall(b), smooth((t - s.gatherT) / (s.dipT - s.gatherT)));
    else if (t < loadT) ball = lerp3(pocketBall(b), chestBall(b), smooth((t - s.dipT) / (loadT - s.dipT)));
    else if (t < s.t0 + 0.06) ball = lerp3(chestBall(b), setBall(b), smooth((t - loadT) / (PUSH + 0.06)));
    else {
      const u = smooth((t - (s.t0 + 0.06)) / (s.release - s.t0 - 0.06));
      ball = lerp3(setBall(b), engineBall(x.play, s.release), u * u);
      rel = u;
    }
    return gripShot(b, x.c, ball, rel);
  }
  // follow-through: shooting arm high, wrist flexed ("hand in the cookie jar"), guide hand stays up, then comes down;
  // blended out of the release grip over 0.12 s (a hard switch popped both wrists at 8.20 s)
  const fo = followOut(x, b, s);
  const u = smooth((t - s.release) / 0.18);
  if (u >= 1) return fo;
  const g = gripShot(b, x.c, engineBall(x.play, s.release), 1);
  const L = (a: V3, z: V3) => lerp3(a, z, u);
  // the hand direction turns through "forward" (quadratic Bezier, the wrist snaps over the ball, not through a
  // near-zero lerp of opposite directions)
  const Fc = fwd(b.chestYaw);
  const D = (a: V3, z: V3) => norm(lerp3(lerp3(a, Fc, u), lerp3(Fc, z, u), u));
  return {tip: [L(g.tip[0], fo.tip[0]), L(g.tip[1], fo.tip[1])], dir: [D(g.dir[0], fo.dir[0]), D(g.dir[1], fo.dir[1])], pole: [norm(L(g.pole[0], fo.pole[0])), norm(L(g.pole[1], fo.pole[1]))], palm: g.palm, pw: [g.palm[0] ? 1 - u : 0, 1 - u]};
};
const followOut = (x: Ctx, b: Body, s: NonNullable<Clip32['shot']>): ArmOut => {
  const t = b.t;
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  const reach = x.c.arm * 0.985;
  const down = smooth((t - s.t1) / 0.32);
  const dR = norm(add(mul(F, 0.62), mul(UP, -0.78)));
  const wR = add(b.shoulders[1], mul(norm(add(add(mul(F, lerp(0.5, 0.75, down)), mul(UP, lerp(0.86, -0.4, down))), mul(R, -0.05))), reach * lerp(1, 0.92, down)));
  const wL = add(b.shoulders[0], mul(norm(add(add(mul(F, lerp(0.38, 0.6, down)), mul(UP, lerp(0.88, -0.5, down))), mul(R, 0.14))), reach * lerp(0.9, 0.88, down)));
  const dL = norm(lerp3(add(mul(UP, 0.75), mul(F, 0.4)), add(mul(F, 0.5), mul(UP, -0.85)), down));
  const dR2 = norm(lerp3(dR, add(mul(F, 0.5), mul(UP, -0.85)), down));
  return {tip: [add(wL, mul(dL, x.c.handLen)), add(wR, mul(dR2, x.c.handLen))], dir: [dL, dR2], pole: [norm(add(mul(R, -0.8), mul(UP, -0.4))), norm(add(mul(R, 0.6), mul(UP, -0.6)))], palm: [null, null]};
};

const modeOut = (x: Ctx, m: ArmKey32['m'], b: Body): ArmOut => {
  const {clip, play, c} = x;
  const t = b.t;
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  switch (m) {
    case 'ready':
      // athletic ready: elbows bent, hands in front of the hips, palms in
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.15, 0.3, -0.42), dir: norm(add(add(mul(F, 0.6), mul(UP, -0.7)), mul(R, s * -0.1))), pole: norm(add(add(mul(R, s * 0.55), mul(F, -0.5)), mul(UP, -0.4)))};
      });
    case 'relaxed':
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.07, 0.08, -0.62), dir: norm(add(add(mul(F, 0.15), mul(UP, -0.98)), mul(R, s * -0.05))), pole: norm(add(mul(F, -0.9), mul(R, s * 0.3)))};
      });
    case 'run':
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        const sw = clamp(b.feet[1 - i].fwdness, -1, 1);
        const a = b.amp;
        const y = 0.07 + 0.29 * sw * a;
        const z = -0.5 * (1 - a) + a * (-0.38 + 0.12 * sw);
        const fw = Math.max(0, sw);
        return {tip: armRel(b, i, 0.07 - 0.03 * fw * a, y, z), dir: norm(add(add(mul(F, 0.3 + 0.5 * fw * a), mul(UP, -(0.9 - 0.45 * fw * a))), mul(R, s * -0.15))),
          pole: norm(add(add(mul(F, -0.85), mul(R, s * 0.35)), mul(UP, -0.2)))};
      });
    case 'brake':
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.3, 0.28, -0.28 + (i === 0 ? 0.06 : 0)), dir: norm(add(add(mul(F, 0.75), mul(UP, -0.3)), mul(R, s * 0.3))), pole: norm(add(add(mul(R, s * 0.7), mul(UP, -0.6)), mul(F, -0.2)))};
      });
    case 'reach':
      return grip2(b, c, engineBall(play, clip.ball.catchT!));
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
    case 'pass': {
      // two-hand chest pass: from the chest the ball is pushed to the engine's pass start point, thumbs turn down after
      const tp = clip.pass!.t;
      if (t < tp) {
        const u = smooth((t - (tp - 0.14)) / 0.14);
        return grip2(b, c, lerp3(chestBall(b), engineBall(play, tp), u));
      }
      const u = smooth((t - tp) / 0.25);
      const to = posAt(play.tracks[clip.pass!.to], clamp(t, 0, play.duration));
      const dirTo = norm([to[0] - b.chest[0], to[1] - b.chest[1], 0]);
      const fo = free((i) => {
        const s = i === 0 ? -1 : 1;
        const tip = add(add(b.shoulders[i], mul(dirTo, c.arm * lerp(0.95, 0.85, u))), add(mul(R, s * 0.05), [0, 0, -0.08]));
        return {tip, dir: norm(add(mul(dirTo, 0.6), add(mul(R, s * 0.5), mul(UP, -0.4)))), pole: norm(add(mul(R, s * 0.8), mul(UP, -0.5)))};
      });
      // out of the release grip over 0.12 s (a hard switch popped both wrists at the pass, QC trio 2.70 s)
      const w = smooth((t - tp) / 0.12);
      if (w >= 1) return fo;
      const g = grip2(b, c, engineBall(play, tp));
      const L = (a: V3, z: V3) => lerp3(a, z, w);
      return {tip: [L(g.tip[0], fo.tip[0]), L(g.tip[1], fo.tip[1])], dir: [norm(L(g.dir[0], fo.dir[0])), norm(L(g.dir[1], fo.dir[1]))], pole: [norm(L(g.pole[0], fo.pole[0])), norm(L(g.pole[1], fo.pole[1]))], palm: g.palm, pw: [1 - w, 1 - w]};
    }
    case 'dribble': {
      const d = clip.ball.dribble!;
      const S0 = jabBall(bodyAt(clip, play, x.id, c, d.push));
      const S1 = gatherBall(bodyAt(clip, play, x.id, c, d.catch));
      const bf = bodyAt(clip, play, x.id, c, d.floor);
      const Fp: V3 = add(add(bf.root, add(mul(fwd(bf.chestYaw), 0.5), mul(right(bf.chestYaw), 0.4))), [0, 0, BALL_R]);
      let ball: V3;
      if (t <= d.floor) {
        const u = clamp((t - d.push) / (d.floor - d.push));
        ball = lerp3(S0, Fp, u * u * (1.6 - 0.6 * u));
      } else {
        const u = clamp((t - d.floor) / (d.catch - d.floor));
        ball = lerp3(Fp, S1, 1 - (1 - u) * (1 - u) * (1 - 0.35 * u));
      }
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
        tip: [armRel(b, 0, 0.3, 0.32, -0.26), add(palmR, mul(dR, c.handLen * 0.55))],
        pole: [norm(add(mul(R, -0.7), mul(UP, -0.6))), norm(add(add(mul(R, 0.75), mul(F, -0.3)), mul(UP, -0.3)))],
      };
    }
    case 'jumpshot':
      return jumpshotOut(x, b);
    case 'set':
      return gripShot(b, c, setBall(b), 0);
    case 'shoot':
    case 'follow':
      return jumpshotOut(x, b);
    case 'land':
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.2, 0.26, -0.4), dir: norm(add(add(mul(F, 0.45), mul(UP, -0.85)), mul(R, s * 0.15))), pole: norm(add(mul(R, s * 0.7), mul(UP, -0.6)))};
      });
    case 'defense':
      // defensive stance: hands outside the shoulders, palms forward-up, active (one hand a little higher: deny lane)
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        const hi = i === 1 ? 0.08 : 0;
        return {tip: armRel(b, i, 0.52, 0.3, -0.1 + hi), dir: norm(add(add(mul(R, s * 0.45), mul(F, 0.4)), mul(UP, 0.55))), pole: norm(add(add(mul(UP, -0.8), mul(F, -0.35)), mul(R, s * 0.3)))};
      });
    case 'closeout':
      // closeout: the near hand high to contest, the other out low to the side
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        if (i === 1) return {tip: armRel(b, i, 0.08, 0.3, 0.62), dir: norm(add(mul(UP, 0.9), mul(F, 0.35))), pole: norm(add(mul(R, s * 0.7), mul(F, -0.3)))};
        return {tip: armRel(b, i, 0.5, 0.22, -0.22), dir: norm(add(add(mul(R, s * 0.6), mul(F, 0.3)), mul(UP, 0.2))), pole: norm(add(mul(UP, -0.8), mul(F, -0.3)))};
      });
  }
  return modeOut(x, 'ready', b);
};

const armsAt = (x: Ctx, b: Body): ArmOut => {
  const ks = x.clip.arms;
  let k = 0;
  while (k + 1 < ks.length && ks[k + 1].t <= b.t) k++;
  return armsK(x, b, k);
};
/** the arms under key k: a blend from what the arms were doing under key k-1 AT THIS TIME (itself possibly still
 *  blending), so a key that arrives before the previous blend has finished does not jump (QC wrist pop 9.30 s) */
const armsK = (x: Ctx, b: Body, k: number): ArmOut => {
  const ks = x.clip.arms;
  const cur = modeOut(x, ks[k].m, b);
  if (k === 0) return cur;
  const u = ks[k].b > 0 ? smooth((b.t - ks[k].t) / ks[k].b) : 1;
  if (u >= 1) return cur;
  const prev = armsK(x, b, k - 1);
  const L = (a: V3, z: V3) => lerp3(a, z, u);
  const out: ArmOut = {
    tip: [L(prev.tip[0], cur.tip[0]), L(prev.tip[1], cur.tip[1])],
    dir: [norm(L(prev.dir[0], cur.dir[0])), norm(L(prev.dir[1], cur.dir[1]))],
    pole: [norm(L(prev.pole[0], cur.pole[0])), norm(L(prev.pole[1], cur.pole[1]))],
    palm: [cur.palm[0] && prev.palm[0] ? L(prev.palm[0], cur.palm[0]) : cur.palm[0] ?? prev.palm[0], cur.palm[1] && prev.palm[1] ? L(prev.palm[1], cur.palm[1]) : cur.palm[1] ?? prev.palm[1]],
    pw: [0, 1].map((i) => (cur.palm[i] && prev.palm[i] ? 1 : cur.palm[i] ? u : prev.palm[i] ? 1 - u : 0)) as [number, number],
  };
  if (cur.ball && prev.ball) out.ball = L(prev.ball, cur.ball);
  else out.ball = cur.ball ?? prev.ball;
  return out;
};

// ---------------------------------------------------------------- ball state machine (explicit, per frame)
export type BallState = 'FREE' | 'INCOMING' | 'FIRST_CONTACT' | 'CONTROLLED' | 'SECURED' | 'DRIBBLE' | 'SHOOT_PREP' | 'RELEASE' | 'FLIGHT' | 'PASS';
/** ball state of this clip's player at t: owner, hands in contact, exact transition times (from the clip / play) */
export const ballState32 = (clip: Clip32, play: Play, id: string, t: number): {state: BallState; owner: string | null; hands: ('L' | 'R')[]} => {
  const bl = clip.ball;
  const hold0 = holdStart(clip, play, id);
  const rel = bl.releaseT ?? Infinity;
  if (hold0 === null || t < hold0 - 0.6) return {state: 'FREE', owner: sample(play, clamp(t, 0, play.duration)).ball.holder ?? null, hands: []};
  if (t < hold0 - 0.03) return {state: 'INCOMING', owner: null, hands: []};
  if (t < hold0 + 0.05 && bl.catchT !== undefined) return {state: 'FIRST_CONTACT', owner: id, hands: ['L', 'R']};
  if (bl.catchT !== undefined && t < bl.catchT + 0.38) return {state: 'CONTROLLED', owner: id, hands: ['L', 'R']};
  if (bl.dribble && t >= bl.dribble.push && t < bl.dribble.catch) return {state: 'DRIBBLE', owner: id, hands: ['R']};
  if (clip.shot && t >= clip.shot.gatherT && t < rel - 0.02) return {state: 'SHOOT_PREP', owner: id, hands: ['L', 'R']};
  if (Math.abs(t - rel) <= 0.02) return {state: 'RELEASE', owner: id, hands: clip.shot ? ['R'] : ['L', 'R']};
  if (t > rel) return {state: clip.pass ? 'PASS' : 'FLIGHT', owner: null, hands: []};
  return {state: 'SECURED', owner: id, hands: ['L', 'R']};
};
/** when this clip's player starts holding the ball: the catch, or 0 when the play gives it the ball from the start */
const holdStart = (clip: Clip32, play: Play, id: string): number | null => {
  if (clip.ball.catchT !== undefined) return clip.ball.catchT;
  const h0 = play.ball.find((e) => e.type === 'hold' && (e as {player?: string}).player === id) as {from?: number} | undefined;
  return h0 ? h0.from ?? 0 : null;
};

// ---------------------------------------------------------------- head
const lookAt = (x: Ctx, b: Body): {yaw: number; pitch: number} => {
  const ks = x.clip.look;
  const eye = b.head;
  const yawPitchOf = (at: string | number): [number, number] => {
    if (typeof at === 'number') return [at, 0.12];
    if (at === 'path') return [b.h, 0.18];
    if (at === 'ahead') return [keyAt(x.clip.heading, b.t + 0.35), 0.15];
    let p: V3;
    if (at === 'rim') p = [0, 1.575, 3.05];
    else if (at === 'ball') p = ballOf(x, b.t);
    else {
      const q = posAt(x.play.tracks[at], clamp(b.t, 0, x.play.duration));
      p = [q[0], q[1], 1.45];
    }
    const d = sub(p, eye);
    return [Math.atan2(d[1], d[0]), clamp(Math.atan2(-d[2], Math.hypot(d[0], d[1])), -0.45, 0.45)];
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
  const off = clamp(wrap(yw - b.chestYaw), -1.22, 1.22);
  return {yaw: b.chestYaw + off, pitch: pt};
};

// ---------------------------------------------------------------- public API
export type Motion32 = {pose: Pose; hipsUp: V3; ball?: V3; held: boolean; feet: [FootState, FootState]; body: Body; arms: ArmOut; c: RigC; clip: Clip32};

const ballOf = (x: Ctx, t: number): V3 => {
  const h0 = holdStart(x.clip, x.play, x.id);
  if (h0 !== null && t >= h0 && t < (x.clip.ball.releaseT ?? Infinity)) {
    const b = bodyAt(x.clip, x.play, x.id, x.c, t);
    const a = armsAt(x, b);
    if (a.ball) return a.ball;
  }
  return engineBall(x.play, t);
};

const mcache = new Map<string, Motion32 | null>();
export const motionV32 = (play: Play, id: string, t: number, rig: RigV3): Motion32 | null => {
  const clip = clip32For(play, id);
  if (!clip) return null;
  const key = `${play.id}|${id}|${t.toFixed(5)}|${rig.variant}`;
  const hit = mcache.get(key);
  if (hit !== undefined) return hit;
  const c = rigConsts(rig, id);
  const x: Ctx = {clip, play, id, c};
  const b = bodyAt(clip, play, id, c, t);
  const a = armsAt(x, b);
  const h0 = holdStart(clip, play, id);
  const held = h0 !== null && t >= h0 && t < (clip.ball.releaseT ?? Infinity) && !!a.ball;
  const look = lookAt(x, b);
  const dz: V3 = [0, 0, -c.ankleOff];
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
    reachW: [smooth(b.feet[0].support / 0.5), smooth(b.feet[1].support / 0.5)],
    headYaw: look.yaw,
    headPitch: look.pitch,
    dims: c.dims,
  };
  const out: Motion32 = {pose, hipsUp: b.hipsUp, ball: held ? a.ball : undefined, held, feet: b.feet, body: b, arms: a, c, clip};
  if (mcache.size > 30000) mcache.clear();
  mcache.set(key, out);
  return out;
};

/** the V3.2 bones: palm correction onto the hand socket (2 IK passes), V3 hands / grip / correctives (incl. the V3.2
 *  garment correctives: trunk folds, strap pull), pelvis on its own axis, foot pitch (heel rise, toe point, heel strike) */
export const framesV32 = (rig: RigV3, m: Motion32): V3Frame => {
  const P: Pose = {...m.pose, hand: [...m.pose.hand] as [V3, V3], wrist: [...m.pose.wrist] as [V3, V3]};
  const sc = m.c.scale;
  for (let it = 0; it < 2; it++) {
    if (!m.arms.palm[0] && !m.arms.palm[1]) break;
    const base = bonesFromPose(baseRig(rig), P, sc, m.hipsUp);
    for (let i = 0; i < 2; i++) {
      const want = m.arms.palm[i];
      if (!want) continue;
      const got = palmWorld(rig, base.bones, base.hips, sc, i === 0 ? 'L' : 'R');
      const lim = m.c.arm * 0.97 + m.c.handLen * 0.45;
      const reachW = 1 - smooth((len(sub(want, m.body.shoulders[i])) - (lim - 0.1)) / 0.1);
      let e = mul(sub(want, got), (m.arms.pw?.[i] ?? 1) * reachW);
      if (len(e) > 0.08) e = mul(norm(e), 0.08);
      P.hand[i] = add(P.hand[i], e);
      P.wrist[i] = add(P.wrist[i], e);
    }
  }
  const fr = bonesV3(rig, P, sc, m.ball ? {pos: m.ball, held: m.held} : undefined, undefined, m.hipsUp);
  const at = fkHeads(rig, fr.bones, fr.hips, sc);
  for (let i = 0; i < 2; i++) {
    const s = i === 0 ? 'L' : 'R';
    const f = m.feet[i];
    const fb = rig.bones.find((b) => b.name === `foot.${s}`)!;
    const D = qmul(fr.bones[`foot.${s}`], qconj(fb.R));
    const A = at(`foot.${s}`);
    const Pp = (k: string): V3 => add(A, qrot(D, mul(sub(rig.restJoints[k], fb.head), sc)));
    const hb = Pp(`heel${s}`), bb = Pp(`ball${s}`);
    const slope = Math.atan2(bb[2] - hb[2], Math.hypot(bb[0] - hb[0], bb[1] - hb[1]));
    const q = axisAngle(right(f.yaw), -f.pitch - slope);
    fr.bones[`foot.${s}`] = qmul(q, fr.bones[`foot.${s}`]);
    // toe joint: stays flat on the floor when the heel rises (the shoe FLEXES at the ball, V3.2 shoe weights), follows
    // the foot when the toe lifts or the foot swings
    if (f.pitch < 0 || f.support < 1) fr.bones[`toe.${s}`] = qmul(q, fr.bones[`toe.${s}`]);
  }
  return fr;
};

export const ballV32 = (play: Play, t: number, rigOf: (id: string) => RigV3): V3 | undefined => {
  for (const p of play.players) {
    const m = clip32For(play, p.id) ? motionV32(play, p.id, t, rigOf(p.id)) : null;
    if (m?.ball) return m.ball;
  }
  return undefined;
};

export const resetV32Caches = () => {
  mcache.clear();
  ccache.clear();
};

// ---------------------------------------------------------------- cloth (jersey / shorts separately)
/** jersey: inertia without flag behaviour (more damping, smaller limits than V3.1); shorts: a third of the jersey's
 *  swing, no twist, hard 2.5 cm cap (they are held by the thighs); maxDisp = per-vertex clamp in the shader (x hem) */
export const CLOTH32 = {
  jersey: {hz: 1.9, zeta: 0.42, gain: 0.6, vgain: 0.016, drag: 0.0011, maxH: 0.055, maxUp: 0.05, maxDown: 0.03, maxTwist: 0.12, flutter: 0.004, maxDisp: 0.06},
  shorts: {scale: 0.33, maxH: 0.02, maxUp: 0.015, maxDown: 0.012, maxDisp: 0.025},
};
export type Cloth32 = Cloth & {maxDisp: number};
const ccache = new Map<string, {jersey: Cloth32; shorts: Cloth32}>();
export const clothV32 = (play: Play, id: string, t: number, rig: RigV3): {jersey: Cloth32; shorts: Cloth32} | undefined => {
  const clip = clip32For(play, id);
  if (!clip) return undefined;
  const key = `${play.id}|${id}|${t.toFixed(5)}`;
  const hit = ccache.get(key);
  if (hit) return hit;
  const c = rigConsts(rig, id);
  const J = CLOTH32.jersey;
  const dt = 1 / 120, w = 2 * Math.PI * J.hz, z = J.zeta;
  const T0 = Math.max(0, t - 1.2);
  const n = Math.max(1, Math.round((t - T0) / dt));
  const pv: {p: V3; yaw: number}[] = [];
  for (let k = -1; k <= n + 1; k++) {
    const b = bodyAt(clip, play, id, c, T0 + k * dt);
    pv.push({p: b.pelvis, yaw: b.hipYaw});
  }
  let x = 0, y = 0, zz = 0, th = 0, vx = 0, vy = 0, vz = 0, vth = 0;
  for (let k = 1; k <= n; k++) {
    const A = pv[k], B = pv[k + 1], C = pv[k + 2];
    const ax = (C.p[0] - 2 * B.p[0] + A.p[0]) / (dt * dt), ay = (C.p[1] - 2 * B.p[1] + A.p[1]) / (dt * dt), az = (C.p[2] - 2 * B.p[2] + A.p[2]) / (dt * dt);
    const al = (wrap(C.yaw - B.yaw) - wrap(B.yaw - A.yaw)) / (dt * dt);
    vx += (-w * w * x - 2 * z * w * vx - J.gain * clamp(ax, -40, 40)) * dt; x += vx * dt;
    vy += (-w * w * y - 2 * z * w * vy - J.gain * clamp(ay, -40, 40)) * dt; y += vy * dt;
    vz += (-w * w * zz - 2 * z * w * vz - J.vgain * w * clamp(az, -60, 60)) * dt; zz += vz * dt;
    vth += (-w * w * th - 2 * z * w * vth - 0.45 * clamp(al, -80, 80)) * dt; th += vth * dt;
  }
  const last = pv[n + 1], prev = pv[n];
  const v = [(last.p[0] - prev.p[0]) / dt, (last.p[1] - prev.p[1]) / dt];
  const sp = Math.hypot(v[0], v[1]);
  let sx = x - J.drag * v[0] * sp, sy = y - J.drag * v[1] * sp;
  const hl = Math.hypot(sx, sy);
  if (hl > J.maxH) {
    sx *= J.maxH / hl;
    sy *= J.maxH / hl;
  }
  const up = clamp(zz + 0.0025 * sp, -J.maxDown, J.maxUp);
  const b = bodyAt(clip, play, id, c, t);
  const ph = (b.feet[0].fwdness + 1) / 4;
  const S = CLOTH32.shorts;
  let qx = sx * S.scale, qy = sy * S.scale;
  const ql = Math.hypot(qx, qy);
  if (ql > S.maxH) {
    qx *= S.maxH / ql;
    qy *= S.maxH / ql;
  }
  const out = {
    jersey: {sway: [sx, sy, up] as V3, twist: clamp(th, -J.maxTwist, J.maxTwist), flutter: J.flutter * Math.min(1, sp / 5), phase: ph, maxDisp: J.maxDisp},
    shorts: {sway: [qx, qy, clamp(up * S.scale, -S.maxDown, S.maxUp)] as V3, twist: 0, flutter: 0, phase: ph, maxDisp: S.maxDisp},
  };
  if (ccache.size > 40000) ccache.clear();
  ccache.set(key, out);
  return out;
};
