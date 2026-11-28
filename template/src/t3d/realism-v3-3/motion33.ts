// E2A Realism V3.3 (2026-11-22) — motion runtime of the V3.3 athlete (athleteRenderer 'v33', opt-in). Copy of the V3.2
// runtime (realism-v3-2/motion32.ts, untouched) with:
//   ball        ONE source of truth for the ball (ballV33): held = the holder's hand anchor (after the contact solver),
//               in flight = ballistic arcs between the release point and the catch point computed from the BODIES of the
//               passer / receiver / shooter (g = 9.81), C1 hand-offs into and out of the hands (push / give)
//   contact     contact solver: the held ball is pushed out of the trunk / thigh / head volumes of its holder (solved
//               bones, the QC radii + 1.2 cm margin) and the hands in contact move with it
//   dribble     multi-bounce live dribble (floor contact, rebound, hand on top of the ball, smooth free-hand path)
//   hand-off    passer presents the ball, the receiver's hands take it hand to hand
//   locomotion  running swing with heel recovery (the foot stays behind, rises early), idle weight shift and active
//               defensive feet for players standing (no frozen bodies), screen stance
//   cloth       the cloth oscillator is integrated ONCE per play from t = 0 (deterministic cache, same as a seek)
//   speed       foot / body evaluations memoised on a fixed grid (pure functions of the clip and t)
// --- V3.2 header follows ---
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
import {PLAYER3D_V32} from '../realism-v3-2/index.ts';
import type {Step} from '../realism-v3-1/clips.ts';
import type {BallEvent} from '../../tactical/play.ts';
import {FIBA} from '../../tactical/geometry.ts';
import type {ArmKey32, Clip32} from './library33.ts';
import {clip33For} from './clips33.ts';
import {anatomicalHits} from './anat33.ts';

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
  const LU = !!s.layup; // V4 running layup: the penultimate step is the dip (short), the trunk stays forward in the air
  const DIP = LU ? 0.11 : (0.24 + 0.4 * (clip.vary.k.drop ?? 0)) * (s.quick ? 0.6 : 1); // V3.3: a quick release dips less
  const zTo = 0.035; // pelvis over its standing height at toe-off (heels up, legs straight)
  const LL = LU ? 0.26 : s.quick ? 0.2 : 0.3; // V3.3: a quick release loads with less forward lean (0.3 -> 0.05 in 0.17 s: head 313 m/s^2)
  const loadT = s.t0 - PUSH;
  const w = smooth((t - s.gatherT) / 0.2) * (1 - smooth((t - (s.recoverT - 0.25)) / 0.25));
  if (t < s.dipT) {
    const u = (t - s.gatherT) / (s.dipT - s.gatherT);
    return {stage: 'gather', dz: -lerp(baseDrop, 0.12, smooth(u)), lean: lerp(0.14, 0.18, smooth(u)), air: 0, w, v0};
  }
  if (t < loadT) {
    const u = (t - s.dipT) / (loadT - s.dipT);
    return {stage: u < 0.7 ? 'dip' : 'load', dz: -lerp(0.12, DIP, smooth(u)), lean: lerp(0.18, LL, smooth(u)), air: 0, w, v0};
  }
  if (t < s.t0) {
    const u = (t - loadT) / PUSH;
    // leg extension: from the bottom of the dip (at rest) to toe-off with the take-off velocity (C1 into the flight)
    return {stage: 'takeoff', dz: herm(-DIP, 0, zTo, v0 * PUSH, u), lean: lerp(LL, LU ? 0.22 : 0.05, smooth(u * 1.2)), air: 0, w, v0};
  }
  if (t < s.t1) {
    const tau = t - s.t0;
    const dz = zTo + v0 * tau - 0.5 * G * tau * tau;
    const st: ShotStage = t < s.release - 0.06 ? 'rise' : t < s.release + 0.03 ? 'release' : t < s.release + 0.2 ? 'follow' : 'descent';
    if (LU) return {stage: st, dz, lean: t < s.release ? lerp(0.22, 0.12, smooth((t - s.t0) / (s.release - s.t0))) : lerp(0.12, 0.2, smooth((t - s.release) / (s.t1 - s.release))), air: dz - zTo, w, v0};
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
const anchorOf = (clip: Clip32, root: (t: number) => V3, st: {f: number; l: number; yaw?: number; dir?: number}, t: number, side: 0 | 1): {g: V3; yaw: number} => {
  const h = keyAt(clip.heading, t);
  const r = root(t);
  const w = keyAt(clip.stanceW, t) * (side === 0 ? -1 : 1);
  const hd = st.dir ?? h; // V4: strides of an 'open' run are placed along the travel direction
  const p = add(add(r, mul(fwd(hd), st.f)), mul(right(hd), st.l + w));
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

const fmemo = new WeakMap<Clip32, Map<string, FootState>>();
const footAt = (clip: Clip32, c: RigC, root: (t: number) => V3, side: 0 | 1, t: number): FootState => {
  let m = fmemo.get(clip);
  if (!m) fmemo.set(clip, (m = new Map()));
  const k = `${side}|${t.toFixed(5)}`;
  const hit = m.get(k);
  if (hit) return hit;
  const out = footAt0(clip, c, root, side, t);
  if (m.size > 60000) m.clear();
  m.set(k, out);
  return out;
};
const footAt0 = (clip: Clip32, c: RigC, root: (t: number) => V3, side: 0 | 1, t: number): FootState => {
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
        // V4 layup knee drive: the free leg swings up and forward (thigh ~ horizontal at the release), comes down first
        const kd = (st as Step & {kd?: number}).kd;
        if (kd) {
          z = Math.max(z, kd * Math.pow(Math.sin(Math.PI * clamp(u * 1.15)), 0.6) + Math.max(0, ph.air) * 0.7);
          pitch = 0.35 * (1 - u) * (1 - u) + 0.25 * Math.sin(Math.PI * u) + (st.heel ?? 0.25) * u * u * u;
        }
      } else {
        // V3.3 running swing: above ~2.2 m/s the foot stays behind longer after toe-off (heel recovery), rises EARLY
        // (peak at ~37 % of the swing instead of 50 %) and higher, then swings through and comes down flat-ish; the
        // walk / shuffle swing is the V3.2 one. Stride speed = landing-to-landing travel / swing time.
        const vs = Math.hypot(tgt.g[0] - prev.g[0], tgt.g[1] - prev.g[1]) / Math.max(0.1, st.land - st.lift);
        const rn = smooth((vs - 2.2) / 2.0);
        const h0 = (st.h ?? 0.09) + 0.05 * rn;
        const zW = h0 * Math.pow(Math.sin(Math.PI * u), 0.85);
        const zR = h0 * Math.sin(Math.PI * Math.pow(clamp(u), 0.8));
        z = lerp(zW, zR, rn);
        const toeOff = st.toeOff ?? 0.42;
        pitch = toeOff * (1 - u) * (1 - u) + (0.28 + 0.12 * rn) * Math.sin(Math.PI * u) + (st.heel ?? 0.05) * u * u * u;
      }
      const vs2 = st.air ? 0 : Math.hypot(tgt.g[0] - prev.g[0], tgt.g[1] - prev.g[1]) / Math.max(0.1, st.land - st.lift);
      const hsR = 0.5 - 0.5 * Math.cos(Math.PI * Math.pow(clamp(u * 1.06), 1.2));
      // V4 knee drive: the free foot comes THROUGH early (under / in front of the hips by ~35 % of the flight)
      const hsx = (st as Step & {kd?: number}).kd ? smooth(clamp(u * 2.4)) : lerp(hs, hsR, smooth((vs2 - 2.2) / 2.0));
      const yaw = prev.yaw + wrap(tgt.yaw - prev.yaw) * hs;
      let g: V3 = [lerp(prev.g[0], tgt.g[0], hsx), lerp(prev.g[1], tgt.g[1], hsx), z];
      if ((st as Step & {kd?: number}).kd) {
        // V4 knee drive: in the air the free foot rides UNDER the driven knee (just in front of the hips, shin ~ vertical),
        // relative to the moving body; it reaches its landing spot only in the last 20 % of the flight
        const hh = keyAt(clip.heading, t);
        const rel = add(add(root(t), mul(fwd(hh), 0.2)), mul(right(hh), st.l * 0.6));
        const a1 = smooth(u / 0.35), a2 = smooth((u - 0.8) / 0.2);
        const px = lerp(lerp(prev.g[0], rel[0], a1), tgt.g[0], a2), py = lerp(lerp(prev.g[1], rel[1], a1), tgt.g[1], a2);
        g = [px, py, z];
      }
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

const bmemo = new WeakMap<Clip32, Map<string, Body>>();
export const bodyAt = (clip: Clip32, play: Play, id: string, c: RigC, t: number): Body => {
  let m = bmemo.get(clip);
  if (!m) bmemo.set(clip, (m = new Map()));
  const k = t.toFixed(5);
  const hit = m.get(k);
  if (hit) return hit;
  const out = bodyAt0(clip, play, id, c, t);
  if (m.size > 30000) m.clear();
  m.set(k, out);
  return out;
};
const GRID = 0.01;
const bodyAt0 = (clip: Clip32, play: Play, id: string, c: RigC, t: number): Body => {
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
  // Gaussian low-pass (sigma 45 ms) sampled on a FIXED 10 ms grid (V3.3: memoised foot states are shared by every
  // frame; the weights follow the exact offset, so the result is still a smooth function of t)
  let lat = 0, lw = 0;
  const g0 = Math.round(t / GRID);
  for (let k = -14; k <= 14; k++) {
    const x = (g0 + k) * GRID;
    const w = Math.exp(-(((x - t) / 0.045) ** 2) / 2);
    lat += w * latAt(x, footAt(clip, c, root, 0, x), footAt(clip, c, root, 1, x));
    lw += w;
  }
  lat /= lw;
  // V3.3 idle life: a player standing shifts his weight slowly (period 3.4-4.6 s, +-1.4 cm) instead of freezing
  // "still" uses the fastest of t-0.3 / t / t+0.3: the root speed passes ~0 for a few frames at every V-cut, and a
  // still-gated sway that switched on there for 50 ms popped the pelvis (trio O2 1.43 s)
  const spAt = (x: number) => {
    const a0 = root(x - 0.05), a1 = root(x + 0.05);
    return Math.hypot(a1[0] - a0[0], a1[1] - a0[1]) / 0.1;
  };
  const still = 1 - smooth(Math.max(speed, spAt(t - 0.3), spAt(t + 0.3)) / 0.35);
  const ph = (clip.vary.seed % 97) * 0.37;
  lat += still * 0.014 * Math.sin((2 * Math.PI * t) / (3.4 + (clip.vary.seed % 7) * 0.2) + ph);
  const pxy = add(r, mul(R, lat));
  const stand = c.pelvisZ * 0.992;
  const inStance = (p: string) => clip.stances.some((s) => s.pose === p && t >= s.t0 && t <= s.t1);
  const active = inStance('defense') ? still * 0.007 * (0.5 + 0.5 * Math.sin(2 * Math.PI * 1.7 * t + ph)) : 0; // live feet in the stance
  let pz = stand - baseDrop - bob - active;
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
  // V3.3: the ground cap (smooth max) hands over to the air cap over 0.1 s after the takeoff / before the landing (a
  // hard switch at the takeoff was a 1.6 m/s step in the pelvis climb: head 313 m/s^2, 5v5 O2 6.26 s)
  const groundCap = () => {
    const TAU = 0.01;
    let acc = 0;
    const g1 = Math.round(t / GRID);
    for (let k = -20; k <= 20; k++) {
      const x = (g1 + k) * GRID;
      const w = Math.exp(-(((x - t) / 0.07) ** 2) / 2);
      const fx: [FootState, FootState] = [footAt(clip, c, root, 0, x), footAt(clip, c, root, 1, x)];
      acc += w * Math.exp(capDrop(x, pz, fx, add(root(x), mul(R, lat)), false) * w / TAU);
    }
    return Math.max(0, TAU * Math.log(acc));
  };
  const edge = inAir ? Math.min(t - clip.shot!.t0, clip.shot!.t1 - t) : 1;
  if (inAir && edge >= 0.1) pz -= capDrop(t, pz, feet, pxy, true);
  else if (inAir) {
    const u = smooth(edge / 0.1);
    pz -= lerp(groundCap(), capDrop(t, pz, feet, pxy, true), u);
  } else {
    // smooth maximum (log-sum-exp, tau 1 cm) of the Gaussian-tapered drops: never less than the drop needed now
    // (the leg reaches its planted foot), C1 in time (no pop when a leg's cap hands over)
    pz -= groundCap();
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
export type ArmOut = {tip: [V3, V3]; dir: [V3, V3]; pole: [V3, V3]; palm: [V3 | null, V3 | null]; ball?: V3; pw?: [number, number]; contact?: string};
const BR = BALL_R + 0.012;
const engineBall = (play: Play, t: number): V3 => sample(play, clamp(t, 0, play.duration)).ball.pos as V3;
const RIM3: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const rigFor = (play: Play, id: string): RigV3 => PLAYER3D_V32[play.players.find((p) => p.id === id)?.team === 'X' ? 'def' : 'off'].rig;
/** the V3.3 body of any player of the play at t (null: no V3.3 clip) */
const bodyOf = (play: Play, id: string, t: number): Body | null => {
  const clip = clip33For(play, id);
  if (!clip) return null;
  return bodyAt(clip, play, id, rigConsts(rigFor(play, id), id), clamp(t, 0, play.duration));
};
const flat = (v: V3): V3 => norm([v[0], v[1], 0]);

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
// (V3.3 tried a 'strong hand on top' triple-threat grip: anatomical forearm contacts went UP (4.5 cm, 5.98-6.09 s),
// so the V3.2 two-side grip is kept for triple threat and jab; see produccion/realism-v3-3/02_CONTACT_QA.md)
/** shooting grip: right palm under / behind the ball, fingers up, guide hand on the left side (thumb back) */
const gripShot = (b: Body, c: RigC, ball: V3, rel: number): ArmOut => {
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  const n = norm(lerp3(add(mul(F, -0.62), mul(UP, -0.78)), add(mul(F, -0.92), mul(UP, -0.38)), rel));
  // V3.3: the shooting hand holds the ball on the finger pads ("space under the ball"), palm 1.5 cm further off than
  // the two-hand grip: the cocked wrist / forearm stays clear of the ball (anatomical contact 2 cm, 7.74-8.19 s)
  const palmR = add(ball, mul(n, BR + 0.015));
  const dd = lerp3(UP, add(mul(UP, 0.55), mul(F, 0.83)), rel);
  const dR = norm(sub(dd, mul(n, dot(dd, n))));
  const palmL = add(ball, mul(norm(add(mul(R, -0.95), mul(F, -0.12))), BR));
  const dL = norm(add(mul(UP, 0.88), mul(F, 0.2)));
  return {
    ball,
    // V3.3: the guide hand fades off the ball (a hard palm cut at rel 0.85 snapped the wrist: 744 m/s^2, trio O2 4.75 s)
    palm: [palmL, palmR],
    pw: [1 - smooth((rel - 0.6) / 0.35), 1],
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

// ball anchors (V3.2) + V3.3 hand-off / catch / release spots computed from the BODIES (never from the engine pose)
const pocketBall = (b: Body) => add(add(b.chest, mul(fwd(b.chestYaw), 0.34)), add(mul(UP, -0.24), mul(right(b.chestYaw), 0.04)));
const TF = 0.32, TR = 0.2, TZ = 0.2;
const tripleBall = (b: Body, hand = 1) => add(add(b.pelvis, mul(fwd(b.chestYaw), TF)), add(mul(right(b.chestYaw), TR * hand), mul(UP, TZ)));
// V3.3: jab / triple-threat ball 12 / 5 cm further out than V3.2 (arms less folded: strong forearm clear of the ball)
const JF = 0.28, JR = 0.24, JZ = 0.14;
const jabBall = (b: Body, hand = 1) => add(add(b.pelvis, mul(fwd(b.chestYaw), JF)), add(mul(right(b.chestYaw), JR * hand), mul(UP, JZ)));
const gatherBall = (b: Body) => add(add(b.chest, mul(fwd(b.chestYaw), 0.33)), add(mul(UP, -0.3), mul(right(b.chestYaw), 0.06)));
const chestBall = (b: Body) => add(add(b.chest, mul(fwd(b.chestYaw), 0.28)), add(mul(UP, -0.02), mul(right(b.chestYaw), 0.08)));
const setBall = (b: Body) => add(add(b.head, mul(fwd(b.chestYaw), 0.24)), add(mul(UP, 0.12), mul(right(b.chestYaw), 0.11)));
/** the shot release point: arm extended up and forward over the shooting shoulder */
const releaseBall = (b: Body) => add(add(b.head, mul(fwd(b.chestYaw), 0.34)), add(mul(UP, 0.4), mul(right(b.chestYaw), 0.13)));
/** opt-in layup event `reach` (2026-11-26, Zero Cut TEST): the release of a running layup, arm extended further UP and
 *  FORWARD toward the rim (finger-roll finish) instead of the jump shot's release over the forehead */
const layupBall = (b: Body) => add(add(b.head, mul(fwd(b.chestYaw), 0.42)), add(mul(UP, 0.46), mul(right(b.chestYaw), 0.14)));

/** V4 layup anchors: the ball ripped to the chest on the finishing-hand side (protected), and the one-hand release
 *  point (arm extended up and toward the rim over the finishing shoulder) */
const ripBall = (b: Body, hand: number) => add(add(b.chest, mul(fwd(b.chestYaw), 0.25)), add(mul(UP, -0.06), mul(right(b.chestYaw), 0.15 * hand)));
const layupRel = (b: Body, hand: number) => add(add(b.head, mul(fwd(b.chestYaw), 0.3)), add(mul(UP, 0.42), mul(right(b.chestYaw), 0.15 * hand)));

type PassEv = Extract<BallEvent, {type: 'pass'}>;
type ShotEv = Extract<BallEvent, {type: 'shot' | 'layup'}>;
const passTo = (play: Play, id: string, t: number) => play.ball.find((e): e is PassEv => e.type === 'pass' && e.to === id && Math.abs(e.t1 - t) < 0.02);
const passFrom = (play: Play, id: string, t: number) => play.ball.find((e): e is PassEv => e.type === 'pass' && e.from === id && (Math.abs(e.t0 - t) < 0.02 || Math.abs(e.t1 - t) < 0.02));
/** where the receiver catches a pass (his body at t1, facing the passer at t0): in front of the chest, lower for a bounce pass */
const catchSpot = (play: Play, ev: PassEv): V3 => {
  const rb = bodyOf(play, ev.to, ev.t1);
  const pb = bodyOf(play, ev.from, ev.t0);
  if (!rb) return engineBall(play, ev.t1);
  const from = pb ? pb.chest : (() => {
    const q = posAt(play.tracks[ev.from], ev.t0);
    return [q[0], q[1], 1.3] as V3;
  })();
  // in front of the chest: the direction to the passer blended with the chest facing (a pass from the side is still
  // caught in front, never beside the shoulder: QC upper-arm contact 4.96-5.04 s with the pure passer direction)
  const dp = flat(sub(from, rb.chest)), dc = fwd(rb.chestYaw);
  const d = dot(dp, dc) > -0.3 ? norm(add(mul(dp, 0.45), mul(dc, 0.55))) : dc;
  return add(add(rb.chest, mul(d, 0.44)), [0, 0, ev.style === 'bounce' ? -0.34 : -0.1]);
};
/** where the passer releases (his body at t0, toward the catch spot) */
const releaseSpot = (play: Play, ev: PassEv): V3 => {
  const pb = bodyOf(play, ev.from, ev.t0);
  if (!pb) return engineBall(play, ev.t0);
  const d = flat(sub(catchSpot(play, ev), pb.chest));
  return add(add(pb.chest, mul(d, 0.44)), [0, 0, ev.style === 'overhead' ? 0.42 : -0.06]);
};
/** hand-off: the passer presents the ball at hip height toward the receiver; the receiver takes it into a low pocket */
const presentSpot = (play: Play, ev: PassEv, t: number): V3 => {
  const pb = bodyOf(play, ev.from, t)!;
  const rb = bodyOf(play, ev.to, t);
  const to = rb ? rb.pelvis : (() => {
    const q = posAt(play.tracks[ev.to], clamp(t, 0, play.duration));
    return [q[0], q[1], 1] as V3;
  })();
  const d = flat(sub(to, pb.pelvis));
  return add(add(pb.pelvis, mul(d, 0.42)), [0, 0, 0.12]);
};
const takeSpot = (play: Play, ev: PassEv, t: number): V3 => {
  const rb = bodyOf(play, ev.to, t)!;
  const pb = bodyOf(play, ev.from, t);
  const d = pb ? flat(sub(pb.pelvis, rb.pelvis)) : fwd(rb.chestYaw);
  return add(add(rb.pelvis, mul(d, 0.36)), [0, 0, 0.16]);
};
const shotOf = (play: Play, id: string, t: number) => play.ball.find((e): e is ShotEv => (e.type === 'shot' || e.type === 'layup') && e.player === id && Math.abs(e.t0 - t) < 0.02);

// ---------------------------------------------------------------- flights (ballistic, from body-derived end points)
type Flight = {t0: number; t1: number; P0: V3; P1: V3; style: string; ev: BallEvent; bank?: V3};
const fcache = new Map<string, Flight>();
const flightOf = (play: Play, ev: BallEvent, k: number): Flight => {
  const key = `${play.id}|${k}`;
  const hit = fcache.get(key);
  if (hit) return hit;
  let f: Flight;
  if (ev.type === 'pass') f = {t0: ev.t0, t1: ev.t1, P0: releaseSpot(play, ev), P1: catchSpot(play, ev), style: ev.style ?? 'chest', ev};
  else if (ev.type === 'shot' || ev.type === 'layup') {
    const sb = bodyOf(play, ev.player, ev.t0);
    const lh = ev.type === 'layup' ? (ev as {hand?: number}).hand : undefined; // V4: one-hand layup release on the finishing side
    const P0 = sb ? (lh ? layupRel(sb, lh) : ev.type === 'layup' && (ev as {reach?: boolean}).reach ? layupBall(sb) : releaseBall(sb)) : engineBall(play, ev.t0);
    const aim: V3 = ev.make === false ? engineBall(play, ev.t1) : [RIM3[0], RIM3[1], RIM3[2] + 0.05];
    f = {t0: ev.t0, t1: ev.t1, P0, P1: aim, style: ev.type, ev};
    // V4 opt-in bank shot: the ball meets the glass at `glass` = [x, z] (front face of the board, ball centre one radius
    // off it) at 60 % of the flight and drops into the rim from there (two gravity arcs; the board reverses vy)
    const gl = (ev as {glass?: [number, number]}).glass;
    if (gl) f.bank = [gl[0], FIBA.basket[1] - 0.375 + BALL_R, gl[1]];
  } else throw new Error('not a flight');
  fcache.set(key, f);
  return f;
};
/** ballistic arc through P0 at t0 and P1 at t1 under gravity: position and velocity */
const arc = (P0: V3, P1: V3, t0: number, t1: number, t: number): {p: V3; v: V3} => {
  const T = Math.max(1e-3, t1 - t0), tau = clamp(t - t0, 0, T), u = tau / T;
  const p: V3 = [lerp(P0[0], P1[0], u), lerp(P0[1], P1[1], u), lerp(P0[2], P1[2], u) + 0.5 * G * tau * (T - tau)];
  const v: V3 = [(P1[0] - P0[0]) / T, (P1[1] - P0[1]) / T, (P1[2] - P0[2]) / T + 0.5 * G * (T - 2 * tau)];
  return {p, v};
};
const flightAt = (play: Play, f: Flight, t: number): {p: V3; v: V3} => {
  if (f.style === 'handoff' && f.ev.type === 'pass') {
    const u = clamp((t - f.t0) / (f.t1 - f.t0));
    const e = u * u * (3 - 2 * u);
    const a = presentSpot(play, f.ev, t), z = takeSpot(play, f.ev, t);
    return {p: lerp3(a, z, e), v: [0, 0, 0]};
  }
  if (f.bank) {
    const tb = f.t0 + 0.6 * (f.t1 - f.t0);
    return t < tb ? arc(f.P0, f.bank, f.t0, tb, t) : arc(f.bank, f.P1, tb, f.t1, t);
  }
  if (f.style === 'bounce') {
    const tb = f.t0 + 0.58 * (f.t1 - f.t0);
    const F = lerp3(f.P0, f.P1, 0.62);
    F[2] = BALL_R;
    // first arc: thrown DOWN (no rise): solve with a flatter gravity-free line + gravity sag, second arc up into the hands
    return t < tb ? arc(f.P0, F, f.t0, tb, t) : arc(F, f.P1, tb, f.t1, t);
  }
  return arc(f.P0, f.P1, f.t0, f.t1, t);
};
const flightIdx = (play: Play, t: number): number => play.ball.findIndex((e) => (e.type === 'pass' || e.type === 'shot' || e.type === 'layup') && t >= e.t0 && t < e.t1);

/** cubic Hermite between two points (vectors), with end velocities (m/s) and duration T */
const herm3 = (p0: V3, v0: V3, p1: V3, v1: V3, T: number, u: number): V3 => [0, 1, 2].map((k) => herm(p0[k], v0[k] * T, p1[k], v1[k] * T, clamp(u))) as V3;

type Ctx = {clip: Clip32; play: Play; id: string; c: RigC};

/** the jump-shot arms + ball, driven by the SAME phase clock as the legs (shotPhase); V3.3: the ball is accelerated
 *  from the set point to the body-derived release point and leaves with (close to) the ballistic launch velocity */
const jumpshotOut = (x: Ctx, b: Body): ArmOut => {
  const s = x.clip.shot!;
  const t = b.t;
  const loadT = s.t0 - PUSH;
  const ev = shotOf(x.play, x.id, s.release);
  const REL = ev ? flightOf(x.play, ev, x.play.ball.indexOf(ev)).P0 : releaseBall(bodyAt(x.clip, x.play, x.id, x.c, s.release));
  if (t < s.release) {
    let ball: V3;
    let rel = 0;
    // V3.3 quick catch-and-shoot (the play leaves < ~0.3 s between the catch and the load): no pocket / dip phases,
    // the ball goes from the catch straight up to the set point (the gather / dip / load phases came out of order at
    // the 5v5 hand-off three, 0.33 s catch-to-release: wrist 2-7 km/s^2)
    const g0 = s.armT ?? s.gatherT;
    const quickPath = !!s.quick || loadT < g0 + 0.12;
    if (quickPath && t < s.t0 + 0.06) ball = lerp3(gatherBall(b), setBall(b), smooth((t - g0) / Math.max(0.1, s.t0 + 0.06 - g0)));
    else if (t < s.dipT) ball = lerp3(gatherBall(b), pocketBall(b), smooth((t - s.gatherT) / (s.dipT - s.gatherT)));
    else if (t < loadT) ball = lerp3(pocketBall(b), chestBall(b), smooth((t - s.dipT) / (loadT - s.dipT)));
    else if (t < s.t0 + 0.06) ball = lerp3(chestBall(b), setBall(b), smooth((t - loadT) / (PUSH + 0.06)));
    else {
      const T = s.release - s.t0 - 0.06;
      const u = clamp((t - (s.t0 + 0.06)) / T);
      const S = setBall(bodyAt(x.clip, x.play, x.id, x.c, s.t0 + 0.06));
      // ease-in exponent so the ball leaves the fingers at ~ the ballistic launch speed
      const v0 = ev ? len(arc(REL, flightOf(x.play, ev, x.play.ball.indexOf(ev)).P1, ev.t0, ev.t1, ev.t0).v) : 7;
      const kx = clamp((v0 * T) / Math.max(0.05, len(sub(REL, S))), 1.6, 4);
      const w = Math.pow(u, kx);
      ball = add(lerp3(setBall(b), REL, w), mul(sub(S, setBall(b)), 0));
      rel = smooth(u);
    }
    // gather / dip / load: both palms on the sides of the ball (two-hand grip); the shooting hand turns UNDER the ball
    // only while it rises to the set point (gripShot all the way from the gather ran the right forearm under the low
    // pocket ball: anatomical contact 1.9 cm, 6.9-7.5 s)
    const gs = gripShot(b, x.c, ball, rel);
    const wS = smooth((t - (loadT - 0.05)) / (PUSH + 0.1));
    if (wS >= 1) return gs;
    const g2 = grip2(b, x.c, ball);
    const L = (a: V3, z: V3) => lerp3(a, z, wS);
    return {ball, tip: [L(g2.tip[0], gs.tip[0]), L(g2.tip[1], gs.tip[1])], dir: [norm(L(g2.dir[0], gs.dir[0])), norm(L(g2.dir[1], gs.dir[1]))], pole: [norm(L(g2.pole[0], gs.pole[0])), norm(L(g2.pole[1], gs.pole[1]))],
      palm: [gs.palm[0] && g2.palm[0] ? L(g2.palm[0], gs.palm[0]) : g2.palm[0], L(g2.palm[1]!, gs.palm[1]!)]};
  }
  const fo = followOut(x, b, s);
  const u = smooth((t - s.release) / 0.18);
  if (u >= 1) return fo;
  // the fingers keep travelling along the launch and brake over 0.18 s (a dead stop at the release point: wrist pop
  // 441 m/s^2, trio O2 4.80 s)
  const T = s.release - s.t0 - 0.06;
  const S = setBall(bodyAt(x.clip, x.play, x.id, x.c, s.t0 + 0.06));
  const v0 = ev ? len(arc(REL, flightOf(x.play, ev, x.play.ball.indexOf(ev)).P1, ev.t0, ev.t1, ev.t0).v) : 7;
  const kx = clamp((v0 * T) / Math.max(0.05, len(sub(REL, S))), 1.6, 4);
  const vh = mul(norm(sub(REL, S)), (kx * len(sub(REL, S))) / Math.max(0.05, T));
  const tau = clamp(t - s.release, 0, 0.18);
  const g = gripShot(b, x.c, add(REL, mul(vh, tau - (tau * tau) / (2 * 0.18))), 1);
  const L = (a: V3, z: V3) => lerp3(a, z, u);
  const Fc = fwd(b.chestYaw);
  const D = (a: V3, z: V3) => norm(lerp3(lerp3(a, Fc, u), lerp3(Fc, z, u), u));
  return {tip: [L(g.tip[0], fo.tip[0]), L(g.tip[1], fo.tip[1])], dir: [D(g.dir[0], fo.dir[0]), D(g.dir[1], fo.dir[1])], pole: [norm(L(g.pole[0], fo.pole[0])), norm(L(g.pole[1], fo.pole[1]))], palm: g.palm, pw: [(g.pw?.[0] ?? 1) * (1 - u), (g.pw?.[1] ?? 1) * (1 - u)]};
};
/** V4 one-hand grip: the finishing palm behind / under the ball (fingers up toward the release), the other palm on the
 *  far side of the ball, fading off as the ball rises (it becomes the shield arm) */
const gripOne = (b: Body, c: RigC, ball: V3, rel: number, hand: number): ArmOut => {
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  const li = hand === 1 ? 1 : 0, oi = 1 - li;
  const n = norm(lerp3(add(mul(F, -0.55), mul(UP, -0.83)), add(mul(F, -0.85), mul(UP, -0.5)), rel));
  const palmLead = add(ball, mul(n, BR + 0.015));
  const dd = lerp3(UP, add(mul(UP, 0.7), mul(F, 0.7)), rel);
  const dLead = norm(sub(dd, mul(n, dot(dd, n))));
  const palmOff = add(ball, mul(norm(add(mul(R, -hand * 0.95), mul(F, -0.1))), BR));
  const dOff = norm(add(mul(UP, 0.85), mul(F, 0.25)));
  const shieldTip = armRel(b, oi, 0.22, 0.34, 0.02); // off arm: forearm up in front of the face, toward the defender
  const shieldDir = norm(add(add(mul(UP, 0.75), mul(F, 0.45)), mul(R, hand * 0.3)));
  const wOff = 1 - smooth((rel - 0.35) / 0.4);
  const out: ArmOut = {ball, palm: [null, null], pw: [1, 1], dir: [UP, UP], tip: [UP, UP], pole: [UP, UP]};
  out.palm[li] = palmLead;
  out.dir[li] = dLead;
  out.tip[li] = add(palmLead, mul(dLead, c.handLen * 0.55));
  out.pole[li] = norm(add(add(mul(UP, -0.7), mul(F, 0.2)), mul(R, hand * 0.35)));
  out.palm[oi] = palmOff;
  out.dir[oi] = norm(lerp3(dOff, shieldDir, 1 - wOff));
  out.tip[oi] = lerp3(add(palmOff, mul(dOff, c.handLen * 0.55)), shieldTip, 1 - wOff);
  out.pole[oi] = norm(add(mul(R, -hand * 0.8), mul(UP, -0.5)));
  out.pw![oi] = wOff;
  return out;
};
/** V4 running layup arms + ball (same phase clock as the legs): rip to the protected side during the gather, rise to
 *  the one-hand release with the off arm shielding, follow-through of the finishing hand, arms down for the landing */
const layupOut = (x: Ctx, b: Body): ArmOut => {
  const s = x.clip.shot!;
  const hand = s.layup!.hand;
  const t = b.t;
  const ev = shotOf(x.play, x.id, s.release);
  const REL = ev ? flightOf(x.play, ev, x.play.ball.indexOf(ev)).P0 : layupRel(bodyAt(x.clip, x.play, x.id, x.c, s.release), hand);
  const ta = s.t0 - 0.08;
  if (t < ta) {
    const ball = lerp3(gatherBall(b), ripBall(b, hand), smooth((t - s.gatherT) / Math.max(0.12, ta - s.gatherT)));
    return grip2(b, x.c, ball);
  }
  if (t < s.release) {
    const u = clamp((t - ta) / Math.max(0.05, s.release - ta));
    const ball = lerp3(ripBall(b, hand), REL, Math.pow(u, 1.5));
    const g1 = gripOne(b, x.c, ball, smooth(u), hand);
    const w = smooth(u / 0.35);
    if (w >= 1) return g1;
    const g2 = grip2(b, x.c, ball);
    const L = (a: V3, z: V3) => lerp3(a, z, w);
    return {ball, tip: [L(g2.tip[0], g1.tip[0]), L(g2.tip[1], g1.tip[1])], dir: [norm(L(g2.dir[0], g1.dir[0])), norm(L(g2.dir[1], g1.dir[1]))], pole: [norm(L(g2.pole[0], g1.pole[0])), norm(L(g2.pole[1], g1.pole[1]))],
      palm: [L(g2.palm[0]!, g1.palm[0]!), L(g2.palm[1]!, g1.palm[1]!)], pw: [lerp(1, g1.pw![0], w), lerp(1, g1.pw![1], w)]};
  }
  // follow-through: the finishing hand keeps going up toward the glass, then both arms come down for the landing
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  const li = hand === 1 ? 1 : 0, oi = 1 - li;
  const down = smooth((t - s.t1 + 0.05) / 0.35);
  const reach = x.c.arm * 0.98;
  const dLead = norm(add(add(mul(F, lerp(0.42, 0.55, down)), mul(UP, lerp(0.9, -0.6, down))), mul(R, hand * 0.08)));
  const wLead = add(b.shoulders[li], mul(dLead, reach * lerp(1, 0.9, down)));
  const hd = norm(lerp3(add(mul(UP, 0.6), mul(F, 0.8)), add(mul(F, 0.4), mul(UP, -0.9)), down));
  const out: ArmOut = {palm: [null, null], tip: [UP, UP], dir: [UP, UP], pole: [UP, UP]};
  out.tip[li] = add(wLead, mul(hd, x.c.handLen));
  out.dir[li] = hd;
  out.pole[li] = norm(add(mul(R, hand * 0.7), mul(UP, -0.6)));
  out.tip[oi] = lerp3(armRel(b, oi, 0.22, 0.34, 0.02), armRel(b, oi, 0.2, 0.22, -0.42), down);
  out.dir[oi] = norm(lerp3(add(mul(UP, 0.7), mul(F, 0.5)), add(mul(F, 0.4), mul(UP, -0.85)), down));
  out.pole[oi] = norm(add(mul(R, -hand * 0.8), mul(UP, -0.5)));
  const u = smooth((t - s.release) / 0.12);
  if (u >= 1) return out;
  const g = gripOne(b, x.c, REL, 1, hand);
  const L = (a: V3, z: V3) => lerp3(a, z, u);
  return {tip: [L(g.tip[0], out.tip[0]), L(g.tip[1], out.tip[1])], dir: [norm(L(g.dir[0], out.dir[0])), norm(L(g.dir[1], out.dir[1]))], pole: [norm(L(g.pole[0], out.pole[0])), norm(L(g.pole[1], out.pole[1]))], palm: g.palm, pw: [(g.pw?.[0] ?? 1) * (1 - u), (g.pw?.[1] ?? 1) * (1 - u)]};
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

// ---------------------------------------------------------------- live dribble (V3.3)
type Drib = Clip32['dribbles'][number];
const DOWN = 0.31, UPF = 0.37;
const NU = 0.8, NF = -0.3, NR = 0.4; // palm on the top-OUTSIDE of the ball (forearm clear of it, QC 6.84-7.0 s) // shares of a bounce period: ball falling after the push / rising into the hand
/** one live dribble: the ball's path (free fall after the push, floor contact, rebound, caught by the hand on top of it,
 *  pushed again) and the dribbling hand's palm (on the ball while in contact, a smooth path while the ball is free) */
const dribbleAt = (x: Ctx, d: Drib, t: number): {ball: V3; palm: V3; touching: boolean} => {
  const fl = d.floors;
  const spot = (q: number): V3 => {
    const b = bodyAt(x.clip, x.play, x.id, x.c, clamp(q, 0, x.play.duration));
    const sp = Math.min(5, b.speed);
    return add(add(b.root, mul(right(b.chestYaw), d.hand * (0.4 + 0.015 * sp))), mul(fwd(b.chestYaw), 0.3 + 0.05 * sp));
  };
  const topZ = (q: number) => {
    const b = bodyAt(x.clip, x.play, x.id, x.c, clamp(q, 0, x.play.duration));
    return b.pelvis[2] - 0.02 - 0.03 * Math.min(1, b.speed / 5);
  };
  const per = (k: number) => (k + 1 < fl.length ? fl[k + 1] - fl[k] : k > 0 ? fl[k] - fl[k - 1] : 0.5);
  // phase boundaries: push p_k before floor k, catch c_k after floor k
  const P = (k: number) => d.push?.[k] ?? fl[k] - DOWN * per(k > 0 ? k - 1 : k);
  const C = (k: number) => d.catch?.[k] ?? fl[k] + UPF * per(k);
  const zAt = (q: number): {z: number; v: number} => {
    for (let k = 0; k < fl.length; k++) {
      const pk = P(k), ck = C(k);
      if (q < pk) {
        // contact before push k: from the previous catch (or the start) to the push
        const a = k > 0 ? C(k - 1) : Math.min(d.t0, pk - 0.05);
        const za = k > 0 ? ballisticUp(k - 1, C(k - 1)) : {z: topZ(a) - 0.05, v: 0};
        const zb = topZ(pk) - 0.03;
        const vb = -downV(k, zb);
        const T = Math.max(0.04, pk - a);
        const u = clamp((q - a) / T);
        return {z: herm(za.z, za.v * T, zb, vb * T, u), v: 0};
      }
      if (q < fl[k]) {
        const zb = topZ(pk) - 0.03;
        const v0 = downV(k, zb);
        const tau = q - pk;
        return {z: zb - v0 * tau - 0.5 * G * tau * tau, v: -(v0 + G * tau)};
      }
      if (q < ck) return ballisticUp(k, q);
    }
    // after the last catch: in the hand until the end of the dribble (pick-up)
    const k = fl.length - 1;
    const a = C(k);
    const za = ballisticUp(k, a);
    const zb = topZ(d.t1) - 0.08;
    const T = Math.max(0.05, d.t1 - a);
    return {z: herm(za.z, za.v * T, zb, 0, clamp((q - a) / T)), v: 0};
  };
  function downV(k: number, zb: number) {
    const T1 = fl[k] - P(k);
    return Math.max(0, (zb - BALL_R - 0.5 * G * T1 * T1) / T1);
  }
  function ballisticUp(k: number, q: number): {z: number; v: number} {
    const T2 = C(k) - fl[k];
    const zc = topZ(C(k)) - 0.07;
    const vu = (zc - BALL_R + 0.5 * G * T2 * T2) / T2;
    const tau = clamp(q - fl[k], 0, T2);
    return {z: BALL_R + vu * tau - 0.5 * G * tau * tau, v: vu - G * tau};
  }
  const z = zAt(t);
  const sp = spot(t);
  const ball: V3 = [sp[0], sp[1], z.z];
  const b = bodyAt(x.clip, x.play, x.id, x.c, t);
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  const n = norm(add(add(mul(UP, NU), mul(F, NF)), mul(R, d.hand * NR)));
  const palmOn = (q: number): V3 => {
    const s2 = spot(q);
    const bb = bodyAt(x.clip, x.play, x.id, x.c, clamp(q, 0, x.play.duration));
    const n2 = norm(add(add(mul(UP, NU), mul(fwd(bb.chestYaw), NF)), mul(right(bb.chestYaw), d.hand * NR)));
    return add([s2[0], s2[1], zAt(q).z], mul(n2, BR));
  };
  // contact intervals: [C(k-1) or start, P(k)] and [C(last), t1]
  let touching = false, palm: V3;
  let k = 0;
  while (k < fl.length && t >= P(k)) k++;
  // k = index of the next push (or fl.length after the last push)
  const lastC = fl.length ? C(fl.length - 1) : d.t0;
  if (k < fl.length && (k === 0 || t >= C(k - 1))) touching = true;
  if (k === fl.length && t >= lastC) touching = true;
  if (touching) palm = add(ball, mul(n, BR));
  else {
    // free ball: the hand rides up from the push (wrist follow-through) and waits for the ball at the catch height
    const a = P(k - 1), z1 = C(k - 1);
    const pa = palmOn(a), pz = palmOn(z1);
    const T = Math.max(0.05, z1 - a);
    const u = clamp((t - a) / T);
    // hand velocity continuous with the ball at the push (it follows it down a little) and at the catch
    const zb0 = topZ(a) - 0.03;
    const va: V3 = [0, 0, -0.6 * downV(k - 1, zb0)], vz: V3 = [0, 0, Math.max(0.2, ballisticUp(k - 1, z1).v)];
    palm = herm3(pa, va, pz, vz, T, u);
  }
  return {ball, palm, touching};
};

const modeOut = (x: Ctx, m: ArmKey32['m'], b: Body): ArmOut => {
  const {clip, play, c} = x;
  const t = b.t;
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  const hand = clip.profile.hand;
  switch (m) {
    case 'ready':
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.15, 0.3, -0.42), dir: norm(add(add(mul(F, 0.6), mul(UP, -0.7)), mul(R, s * -0.1))), pole: norm(add(add(mul(R, s * 0.55), mul(F, -0.5)), mul(UP, -0.4)))};
      });
    case 'relaxed':
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.07, 0.08, -0.62), dir: norm(add(add(mul(F, 0.15), mul(UP, -0.98)), mul(R, s * -0.05))), pole: norm(add(mul(F, -0.9), mul(R, s * 0.3)))};
      });
    case 'screen':
      // legal screen: hands crossed low in front of the hips (protect), elbows in, no hands out
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, -0.06, 0.24, -0.5), dir: norm(add(add(mul(F, 0.25), mul(UP, -0.85)), mul(R, s * -0.45))), pole: norm(add(add(mul(R, s * 0.6), mul(F, -0.3)), mul(UP, -0.5)))};
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
    case 'reach': {
      const ct = clip.catches.filter((q) => q.t >= t - 0.02).sort((a, z) => a.t - z.t)[0] ?? clip.catches[clip.catches.length - 1];
      const ev = ct ? passTo(play, x.id, ct.t) : undefined;
      return grip2(b, c, ev ? catchSpot(play, ev) : engineBall(play, clip.ball.catchT!));
    }
    case 'take': {
      // hand-off receiver: the hands come to the presented ball and ride with it
      const ct = clip.catches.filter((q) => q.t >= t - 0.02).sort((a, z) => a.t - z.t)[0];
      const ev = ct ? passTo(play, x.id, ct.t) : undefined;
      if (!ev) return modeOut(x, 'ready', b);
      // before the exchange the hands track the presented ball where it is NOW (a fixed t0 target, reached from a run at
      // 3.6 m/s, hit the reach limit: 1 km/s^2 wrist pops, 5v5 O2 5.78 s)
      return grip2(b, c, t < ev.t0 ? presentSpot(play, ev, t) : flightAt(play, flightOf(play, ev, play.ball.indexOf(ev)), t).p);
    }
    case 'give': {
      // catch absorption: the ball keeps its incoming velocity into the hands (C1), then the elbows absorb it to the pocket
      const ct = [...clip.catches].filter((q) => q.t <= t + 0.02).sort((a, z) => z.t - a.t)[0];
      const ev = ct ? passTo(play, x.id, ct.t) : undefined;
      if (!ev) {
        const tc = clip.ball.catchT!;
        return grip2(b, c, lerp3(engineBall(play, tc), pocketBall(b), smooth((t - tc) / 0.38)));
      }
      const T = ev.style === 'handoff' ? 0.3 : 0.38;
      const f = flightOf(play, ev, play.ball.indexOf(ev));
      const P1 = ev.style === 'handoff' ? takeSpot(play, ev, ev.t1) : f.P1;
      const v1 = ev.style === 'handoff' ? ([0, 0, 0] as V3) : mul(flightAt(play, f, ev.t1 - 1e-4).v, 0.35);
      const tgt = pocketBall(bodyAt(clip, play, x.id, c, ev.t1 + T));
      const u = clamp((t - ev.t1) / T);
      const p = herm3(P1, v1, tgt, [0, 0, 0], T, u);
      // follow the body while absorbing: the offset of the pocket target moves with the chest
      const pk = pocketBall(b);
      return grip2(b, c, add(p, mul(sub(pk, tgt), smooth(u))));
    }
    case 'pocket':
      return grip2(b, c, pocketBall(b));
    case 'triple':
      return grip2(b, c, tripleBall(b, hand));
    case 'jab':
      return grip2(b, c, jabBall(b, hand));
    case 'gather':
      return grip2(b, c, gatherBall(b));
    case 'pass': {
      const ps = [...clip.passes].filter((q) => q.t >= t - 0.6).sort((a, z) => a.t - z.t)[0] ?? clip.passes[clip.passes.length - 1];
      const tp = ps?.t ?? clip.pass!.t;
      const ev = passFrom(play, x.id, tp);
      const REL = ev ? flightOf(play, ev, play.ball.indexOf(ev)).P0 : engineBall(play, tp);
      if (t < tp) {
        // push from the chest to the release point: ease-in so the ball leaves with ~ the flight's launch speed
        const T = 0.16;
        const u = clamp((t - (tp - T)) / T);
        const S = chestBall(bodyAt(clip, play, x.id, c, tp - T));
        const v0 = ev ? len(flightAt(play, flightOf(play, ev, play.ball.indexOf(ev)), ev.t0).v) : 6;
        const kx = clamp((v0 * T) / Math.max(0.05, len(sub(REL, S))), 1.5, 2);
        return grip2(b, c, lerp3(chestBall(b), REL, Math.pow(u, kx)));
      }
      const u = smooth((t - tp) / 0.25);
      const toId = ps?.to ?? clip.pass!.to;
      const to = posAt(play.tracks[toId], clamp(t, 0, play.duration));
      const dirTo = norm([to[0] - b.chest[0], to[1] - b.chest[1], 0]);
      const fo = free((i) => {
        const s = i === 0 ? -1 : 1;
        const tip = add(add(b.shoulders[i], mul(dirTo, c.arm * lerp(0.95, 0.85, u))), add(mul(R, s * 0.05), [0, 0, -0.08]));
        return {tip, dir: norm(add(mul(dirTo, 0.6), add(mul(R, s * 0.5), mul(UP, -0.4)))), pole: norm(add(mul(R, s * 0.8), mul(UP, -0.5)))};
      });
      const w = smooth((t - tp) / 0.16);
      if (w >= 1) return fo;
      // after the release the hands keep moving along the pass and brake over 0.16 s (no dead stop at the release
      // point: V3.3 first pass, 600 m/s^2 wrist pop at the trio pass 2.70 s)
      const T0 = 0.16;
      const S0 = chestBall(bodyAt(clip, play, x.id, c, tp - T0));
      const ev0 = passFrom(play, x.id, tp);
      const v0 = ev0 ? len(flightAt(play, flightOf(play, ev0, play.ball.indexOf(ev0)), ev0.t0).v) : 6;
      const kx0 = clamp((v0 * T0) / Math.max(0.05, len(sub(REL, S0))), 1.5, 2);
      const vh = mul(norm(sub(REL, S0)), (kx0 * len(sub(REL, S0))) / T0); // hand speed at the release
      const tau = clamp(t - tp, 0, 0.16);
      const g = grip2(b, c, add(REL, mul(vh, tau - (tau * tau) / (2 * 0.16))));
      const L = (a: V3, z: V3) => lerp3(a, z, w);
      return {tip: [L(g.tip[0], fo.tip[0]), L(g.tip[1], fo.tip[1])], dir: [norm(L(g.dir[0], fo.dir[0])), norm(L(g.dir[1], fo.dir[1]))], pole: [norm(L(g.pole[0], fo.pole[0])), norm(L(g.pole[1], fo.pole[1]))], palm: g.palm, pw: [(g.pw?.[0] ?? 1) * (1 - w), (g.pw?.[1] ?? 1) * (1 - w)]};
    }
    case 'handoff': {
      // hand-off passer: the ball goes from the pocket / dribble to the presented spot, the hands stay on it until the
      // receiver has it (t1), then let go
      const ps = [...clip.passes].filter((q) => q.style === 'handoff').sort((a, z) => Math.abs(a.t - t) - Math.abs(z.t - t))[0];
      const ev = ps ? passFrom(play, x.id, ps.t) : undefined;
      if (!ev) return modeOut(x, 'pocket', b);
      if (t < ev.t0) {
        const k0 = Math.max(0, ev.t0 - 0.36);
        const u = smooth((t - k0) / (ev.t0 - k0));
        return grip2(b, c, lerp3(pocketBall(b), presentSpot(play, ev, t), u));
      }
      if (t < ev.t1) {
        const p = flightAt(play, flightOf(play, ev, play.ball.indexOf(ev)), t).p;
        const g = grip2(b, c, p);
        const u = clamp((t - ev.t0) / (ev.t1 - ev.t0));
        return {...g, ball: p, pw: [1 - u, 1 - u]};
      }
      const g = grip2(b, c, takeSpot(play, ev, ev.t1));
      const fo = modeOut(x, 'screen', b);
      const w = smooth((t - ev.t1) / 0.18);
      const L = (a: V3, z: V3) => lerp3(a, z, w);
      return {tip: [L(g.tip[0], fo.tip[0]), L(g.tip[1], fo.tip[1])], dir: [norm(L(g.dir[0], fo.dir[0])), norm(L(g.dir[1], fo.dir[1]))], pole: [norm(L(g.pole[0], fo.pole[0])), norm(L(g.pole[1], fo.pole[1]))], palm: g.palm, pw: [(g.pw?.[0] ?? 1) * (1 - w), (g.pw?.[1] ?? 1) * (1 - w)]};
    }
    case 'dribble': {
      const d = clip.dribbles.find((q) => t >= q.t0 - 0.3 && t <= q.t1 + 0.3);
      if (!d) {
        // V3.2 single-bounce dribble (one-take): kept for the compatibility scripts
        return dribble32(x, b);
      }
      const di = dribbleAt(x, d, clamp(t, d.t0, d.t1));
      const si = d.hand > 0 ? 1 : 0, oi = 1 - si;
      const dR = norm(add(add(mul(F, 0.85), mul(UP, -0.25)), mul(R, -d.hand * 0.1)));
      const out: ArmOut = {ball: di.ball, palm: [null, null], dir: [UP, UP], tip: [UP, UP], pole: [UP, UP]};
      // the dribble hand follows its palm path in BOTH phases (palm on the ball, hand waiting above it): switching the
      // palm correction on / off at every touch popped the wrist 450-670 m/s^2 per bounce (5v5 O1)
      out.palm[si] = di.palm;
      out.dir[si] = dR;
      out.tip[si] = add(di.palm, mul(dR, c.handLen * 0.55));
      out.pole[si] = norm(add(add(mul(R, d.hand * 0.75), mul(F, -0.3)), mul(UP, -0.3)));
      // off hand: protects the ball (forearm up in front, toward the defender side)
      out.tip[oi] = armRel(b, oi, 0.3, 0.34, -0.24);
      out.dir[oi] = norm(add(mul(F, 0.7), mul(R, -d.hand * 0.35)));
      out.pole[oi] = norm(add(mul(R, -d.hand * 0.7), mul(UP, -0.6)));
      return out;
    }
    case 'jumpshot':
      return clip.shot?.layup ? layupOut(x, b) : jumpshotOut(x, b);
    case 'layup':
      return layupOut(x, b);
    case 'trap':
      // V4 trap (blitz): both hands HIGH and wide, palms toward the ball handler: the pass over the top is taken away
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        const ph = (clip.vary.seed % 11) * 0.6 + i * 2.1;
        const wv = 0.03 * Math.sin(2 * Math.PI * 1.4 * t + ph);
        return {tip: armRel(b, i, 0.42 + wv, 0.3, 0.32 + wv), dir: norm(add(add(mul(UP, 0.75), mul(F, 0.5)), mul(R, s * 0.35))), pole: norm(add(add(mul(R, s * 0.7), mul(UP, -0.5)), mul(F, -0.3)))};
      });
    case 'wall':
      // V4 help defender showing the wall: hands out at chest height, wide (makes himself big in the driving lane)
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        return {tip: armRel(b, i, 0.5, 0.24, -0.08), dir: norm(add(add(mul(R, s * 0.55), mul(F, 0.55)), mul(UP, 0.35))), pole: norm(add(mul(UP, -0.85), mul(F, -0.3)))};
      });
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
      // defensive stance: hands outside the shoulders, palms forward-up, ACTIVE (V3.3: small deterministic hand work)
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        const hi = i === 1 ? 0.08 : 0;
        const ph = (clip.vary.seed % 13) * 0.7 + i * 1.9;
        const wob = 0.035 * Math.sin(2 * Math.PI * 1.15 * t + ph), wob2 = 0.025 * Math.sin(2 * Math.PI * 0.8 * t + ph * 1.3);
        return {tip: armRel(b, i, 0.52 + wob2, 0.3, -0.1 + hi + wob), dir: norm(add(add(mul(R, s * 0.45), mul(F, 0.4)), mul(UP, 0.55))), pole: norm(add(add(mul(UP, -0.8), mul(F, -0.35)), mul(R, s * 0.3)))};
      });
    case 'closeout':
      return free((i) => {
        const s = i === 0 ? -1 : 1;
        if (i === 1) return {tip: armRel(b, i, 0.08, 0.3, 0.62), dir: norm(add(mul(UP, 0.9), mul(F, 0.35))), pole: norm(add(mul(R, s * 0.7), mul(F, -0.3)))};
        return {tip: armRel(b, i, 0.5, 0.22, -0.22), dir: norm(add(add(mul(R, s * 0.6), mul(F, 0.3)), mul(UP, 0.2))), pole: norm(add(mul(UP, -0.8), mul(F, -0.3)))};
      });
  }
  return modeOut(x, 'ready', b);
};

/** V3.2 single-bounce dribble, unchanged (one-take compatibility scripts) */
const dribble32 = (x: Ctx, b: Body): ArmOut => {
  const {clip, play, c} = x;
  const t = b.t;
  const F = fwd(b.chestYaw), R = right(b.chestYaw);
  const d = clip.ball.dribble!;
  const S0 = jabBall(bodyAt(clip, play, x.id, c, d.push));
  const S1 = gatherBall(bodyAt(clip, play, x.id, c, d.catch));
  const bf = bodyAt(clip, play, x.id, c, d.floor);
  // V3.3: floor point further out (0.48 m to the side instead of 0.40) so the falling ball clears the stepping thigh
  const Fp: V3 = add(add(bf.root, add(mul(fwd(bf.chestYaw), 0.5), mul(right(bf.chestYaw), 0.48))), [0, 0, BALL_R]);
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
};

const armsAt = (x: Ctx, b: Body): ArmOut => {
  const ks = x.clip.arms;
  let k = 0;
  while (k + 1 < ks.length && ks[k + 1].t <= b.t) k++;
  return armsK(x, b, k);
};
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
    pw: [0, 1].map((i) => {
      const a = cur.palm[i] ? cur.pw?.[i] ?? 1 : 0, z = prev.palm[i] ? prev.pw?.[i] ?? 1 : 0;
      return cur.palm[i] && prev.palm[i] ? lerp(z, a, u) : cur.palm[i] ? a * u : prev.palm[i] ? z * (1 - u) : 0;
    }) as [number, number],
  };
  if (cur.ball && prev.ball) out.ball = L(prev.ball, cur.ball);
  else out.ball = cur.ball ?? prev.ball;
  return out;
};

// ---------------------------------------------------------------- contact solver (V3.3)
/** push a held ball out of its holder's trunk / head / thigh volumes (anatomical volumes measured on the mesh, anat33.ts;
 *  solved body bones; 4 mm margin); the hands that touch the ball move with it. Returns the region it was pushed from */
const CLEAR = 0.004;
const clearBall = (rig: RigV3, P: Pose, sc: number, hipsUp: V3, a: ArmOut): ArmOut => {
  if (!a.ball) return a;
  const base = bonesFromPose(baseRig(rig), P, sc, hipsUp);
  const at = fkHeads(rig, base.bones, base.hips, sc);
  // the joints the QC reads (same bone heads); arms are not used (the hands hold the ball: grips handle the forearms)
  const J: Record<string, V3> = {pelvis: at('hips'), chest: at('chest'), neck: at('neck'), head: at('head'), shL: at('upperarm.L'), shR: at('upperarm.R'),
    hipL: at('thigh.L'), knL: at('shin.L'), hipR: at('thigh.R'), knR: at('shin.R'),
    // arm joints far away so anatomicalHits ignores them here
    elL: [0, 0, -50], elR: [0, 0, -50], wrL: [0, 0, -50.1], wrR: [0, 0, -50.1]};
  let ball = a.ball;
  let hit = '';
  // SOFT push (softplus, 1 cm): C-infinity in the ball position, so the hands do not jerk when the ball starts touching
  const S = 0.01;
  for (let it = 0; it < 6; it++) {
    // arms excluded: the arm joints are parked far away above, so an upperarm capsule would run from the shoulder
    // down through the trunk (V3.3 5v5 first compile: 40 cm hand jump at O2 6.18 s); the holder's arms move with the ball
    const hs = anatomicalHits(J, ball, -CLEAR - 4 * S).filter((h) => !h.region.includes('arm'));
    if (!hs.length) break;
    const w = hs.reduce((m, h) => (h.depth > m.depth ? h : m));
    const push = S * Math.log(1 + Math.exp((w.depth + CLEAR) / S));
    if (push < 2e-4) break;
    const f = (p: V3) => anatomicalHits(J, p, -1).find((h) => h.region === w.region)?.depth ?? -1;
    const e = 0.002;
    let gv: V3 = [(f(add(ball, [e, 0, 0])) - f(add(ball, [-e, 0, 0]))) / (2 * e), (f(add(ball, [0, e, 0])) - f(add(ball, [0, -e, 0]))) / (2 * e), (f(add(ball, [0, 0, e])) - f(add(ball, [0, 0, -e]))) / (2 * e)];
    if (len(gv) < 1e-6) gv = mul(fwd(P.chestYaw), -1);
    ball = add(ball, mul(norm(gv), -push));
    if (w.depth > -CLEAR) hit = w.region;
    if (push < w.depth + CLEAR + 0.0005 && it < 5) continue;
    break;
  }
  const delta = sub(ball, a.ball);
  if (len(delta) < 1e-6) return a;
  const sh = (v: V3, i: number) => (a.palm[i] ? add(v, delta) : v);
  return {...a, ball, palm: [a.palm[0] ? add(a.palm[0], delta) : null, a.palm[1] ? add(a.palm[1], delta) : null], tip: [sh(a.tip[0], 0), sh(a.tip[1], 1)], contact: hit};
};

// ---------------------------------------------------------------- ball state machine (explicit, per frame)
export type BallState = 'FREE' | 'INCOMING' | 'FIRST_CONTACT' | 'CONTROLLED' | 'SECURED' | 'DRIBBLE' | 'SHOOT_PREP' | 'RELEASE' | 'FLIGHT' | 'PASS';
/** ball state of this clip's player at t: owner, hands in contact, exact transition times (from the windows of the clip) */
export const ballState33 = (clip: Clip32, play: Play, id: string, t: number): {state: BallState; owner: string | null; hands: ('L' | 'R')[]} => {
  const W = clip.windows;
  const w = W.find((q) => t >= q.a - 0.6 && t < q.b + 0.6 && !(t >= q.b + 0.02 && W.some((r) => r !== q && t >= r.a - 0.6 && r.a > q.a)));
  if (!w) return {state: 'FREE', owner: sample(play, clamp(t, 0, play.duration)).ball.holder ?? null, hands: []};
  if (t < w.a - 0.03 && w.start !== 'start') return {state: 'INCOMING', owner: null, hands: []};
  if (t < w.a + 0.05 && w.start !== 'start') return {state: 'FIRST_CONTACT', owner: id, hands: ['L', 'R']};
  if (w.start !== 'start' && t < w.a + 0.38) return {state: 'CONTROLLED', owner: id, hands: ['L', 'R']};
  const d = clip.dribbles.find((q) => t >= q.t0 && t < q.t1);
  if (d) return {state: 'DRIBBLE', owner: id, hands: [d.hand > 0 ? 'R' : 'L']};
  if (clip.shot && t >= (clip.shot.armT ?? clip.shot.gatherT) && t < w.b - 0.02 && w.end === 'shot') return {state: 'SHOOT_PREP', owner: id, hands: ['L', 'R']};
  if (Math.abs(t - w.b) <= 0.02) return {state: 'RELEASE', owner: id, hands: w.end === 'shot' ? ['R'] : ['L', 'R']};
  if (t > w.b) return {state: w.end === 'shot' ? 'FLIGHT' : 'PASS', owner: null, hands: []};
  return {state: 'SECURED', owner: id, hands: ['L', 'R']};
};
const inWindow = (clip: Clip32, t: number) => clip.windows.some((w) => t >= w.a && t < w.b);

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
    // own ball in the hands: eyes up the floor, slightly down; blended over 0.3-0.7 m (a hard switch at 0.5 m stepped
    // the head 2.4 cm in one frame: 5v5 O2 6.20 s)
    const hd = Math.hypot(d[0], d[1]);
    const far: [number, number] = [Math.atan2(d[1], d[0]), clamp(Math.atan2(-d[2], Math.max(1e-3, hd)), -0.45, 0.45)];
    const wn = 1 - smooth((hd - 0.3) / 0.4);
    if (wn <= 0) return far;
    return [far[0] + wrap(b.chestYaw - far[0]) * wn, lerp(far[1], 0.35, wn)];
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
export type Motion33 = {pose: Pose; hipsUp: V3; ball?: V3; held: boolean; feet: [FootState, FootState]; body: Body; arms: ArmOut; c: RigC; clip: Clip32};

const ballOf = (x: Ctx, t: number): V3 => {
  if (inWindow(x.clip, t)) {
    const b = bodyAt(x.clip, x.play, x.id, x.c, t);
    const a = armsAt(x, b);
    if (a.ball) return a.ball;
  }
  return ballV33(x.play, t);
};

const mcache = new Map<string, Motion33 | null>();
/** opt-in (2026-11-24, 4 Rules reel, illegal hold): `play.v33grab = [{player, target, hand: 0 | 1, from, to}]` puts the
 *  free hand of `player` on the waist of `target` (surface of the near hip, solved on the target's own V3.3 body) with a
 *  0.18 s blend in / out. Plays without the key are unchanged. */
export type Grab33 = {player: string; target: string; hand: 0 | 1; from: number; to: number; z?: number; reach?: number};
const grab33 = (play: Play, id: string, t: number, b: Body, a: ArmOut): ArmOut => {
  const gs = ((play as Play & {v33grab?: Grab33[]}).v33grab ?? []).filter((g) => g.player === id);
  let out = a;
  for (const g of gs) {
    const w = smooth((t - g.from) / 0.18) * smooth((g.to - t) / 0.18);
    if (w <= 1e-4) continue;
    const team = play.players.find((p) => p.id === g.target)?.team === 'X' ? 'def' : 'off';
    const m = motionV33(play, g.target, t, PLAYER3D_V32[team].rig);
    if (!m) continue;
    const tb = m.body;
    const sh = b.shoulders[g.hand];
    // the near hip of the target (to the grabber's shoulder), pushed out to the body surface at waist height
    const hip = len(sub(tb.hips[0], sh)) < len(sub(tb.hips[1], sh)) ? tb.hips[0] : tb.hips[1];
    const side = norm([hip[0] - tb.pelvis[0], hip[1] - tb.pelvis[1], 0]);
    const toG = norm([sh[0] - tb.pelvis[0], sh[1] - tb.pelvis[1], 0]);
    const out3 = norm(add(side, mul(toG, 0.8)));
    let P: V3 = add([tb.pelvis[0], tb.pelvis[1], tb.pelvis[2] + (g.z ?? 0.08)], mul(out3, 0.19));
    // the PALM sits on the surface: the hand tip goes 7 cm further along the reach (fingers wrap the jersey)
    P = add(P, mul(norm(sub(P, sh)), 0.07));
    const reach = g.reach ?? 0.64;
    const d = sub(P, sh);
    if (len(d) > reach) P = add(sh, mul(norm(d), reach));
    const tip = [...out.tip] as [V3, V3];
    const dir = [...out.dir] as [V3, V3];
    const palm = [...out.palm] as [V3 | null, V3 | null];
    tip[g.hand] = lerp3(out.tip[g.hand], P, w);
    dir[g.hand] = norm(lerp3(out.dir[g.hand], norm(sub(P, sh)), w));
    if (w > 0.5) palm[g.hand] = tip[g.hand];
    out = {...out, tip, dir, palm, contact: out.contact ?? (w > 0.5 ? `grab ${g.target}` : undefined)};
  }
  return out;
};

export const motionV33 = (play: Play, id: string, t: number, rig: RigV3): Motion33 | null => {
  const clip = clip33For(play, id);
  if (!clip) return null;
  const key = `${play.id}|${id}|${t.toFixed(5)}|${rig.variant}`;
  const hit = mcache.get(key);
  if (hit !== undefined) return hit;
  const c = rigConsts(rig, id);
  const x: Ctx = {clip, play, id, c};
  const b = bodyAt(clip, play, id, c, t);
  let a = grab33(play, id, t, b, armsAt(x, b));
  const held = inWindow(clip, t) && !!a.ball;
  const look = lookAt(x, b);
  const dz: V3 = [0, 0, -c.ankleOff];
  const E = (p: V3) => add(p, dz);
  const toeOf = (f: FootState): V3 => add(E(f.ankle), add(mul(fwd(f.yaw), c.dims.foot * 0.78), [0, 0, -c.dims.ankleH * 0.7]));
  const elbow = (i: number): V3 => add(b.shoulders[i], mul(a.pole[i], 0.2));
  const mk = (aa: ArmOut): Pose => ({
    pelvis: E(b.pelvis), chest: E(b.chest), head: E(b.head), heading: b.h, chestYaw: b.chestYaw, lean: b.lean, roll: b.roll,
    hip: [E(b.hips[0]), E(b.hips[1])],
    knee: [E(add(lerp3(b.hips[0], b.feet[0].ankle, 0.5), mul(fwd(b.feet[0].yaw), 0.3))), E(add(lerp3(b.hips[1], b.feet[1].ankle, 0.5), mul(fwd(b.feet[1].yaw), 0.3)))],
    ankle: [E(b.feet[0].ankle), E(b.feet[1].ankle)],
    toe: [toeOf(b.feet[0]), toeOf(b.feet[1])],
    shoulder: [E(b.shoulders[0]), E(b.shoulders[1])],
    elbow: [E(add(b.shoulders[0], mul(aa.pole[0], 0.2))), E(add(b.shoulders[1], mul(aa.pole[1], 0.2)))],
    wrist: [E(sub(aa.tip[0], mul(aa.dir[0], 0.1))), E(sub(aa.tip[1], mul(aa.dir[1], 0.1)))],
    hand: [E(aa.tip[0]), E(aa.tip[1])],
    airborne: Math.max(0, b.air),
    reachW: [smooth(b.feet[0].support / 0.5), smooth(b.feet[1].support / 0.5)],
    headYaw: look.yaw,
    headPitch: look.pitch,
    dims: c.dims,
  });
  void elbow;
  let pose = mk(a);
  // contact solver on the held ball (ball, palms and hand targets move together)
  if (held && a.ball) {
    const a2 = clearBall(rig, pose, c.scale, b.hipsUp, a);
    if (a2 !== a) {
      a = a2;
      pose = mk(a);
    }
  }
  const out: Motion33 = {pose, hipsUp: b.hipsUp, ball: held ? a.ball : undefined, held, feet: b.feet, body: b, arms: a, c, clip};
  if (mcache.size > 30000) mcache.clear();
  mcache.set(key, out);
  return out;
};

/** the V3.3 bones: palm correction onto the hand socket (2 IK passes), V3 hands / grip / correctives, pelvis on its own
 *  axis, foot pitch (heel rise, toe point, heel strike) — same as V3.2 */
export const framesV33 = (rig: RigV3, m: Motion33): V3Frame => {
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
    if (f.pitch < 0 || f.support < 1) fr.bones[`toe.${s}`] = qmul(q, fr.bones[`toe.${s}`]);
  }
  return fr;
};

/** V3.3 single source of truth for the ball at play time t: held -> the holder's hand anchor (contact-solved), in flight
 *  -> the ballistic arc between body-derived release and catch points, otherwise the engine (rim / net / loose ball) */
export const ballV33 = (play: Play, t: number): V3 => {
  const tt = clamp(t, 0, play.duration);
  const fi = flightIdx(play, tt);
  if (fi >= 0) {
    const ev = play.ball[fi];
    const f = flightOf(play, ev, fi);
    if (ev.type === 'pass' && ev.style === 'handoff') {
      const m = motionV33(play, ev.from, tt, rigFor(play, ev.from));
      if (m?.arms.ball) return m.arms.ball;
    }
    return flightAt(play, f, tt).p;
  }
  const h = play.ball.find((e): e is Extract<BallEvent, {type: 'hold'}> => e.type === 'hold' && tt >= e.from && tt < e.to);
  if (h) {
    const m = motionV33(play, h.player, tt, rigFor(play, h.player));
    if (m?.ball) return m.ball;
  }
  return engineBall(play, tt);
};
/** who owns the ball for the debug / QA counters: holder id, 'flight', or null */
export const ballOwner33 = (play: Play, t: number): string | null => {
  const tt = clamp(t, 0, play.duration);
  if (flightIdx(play, tt) >= 0) return 'flight';
  const h = play.ball.find((e): e is Extract<BallEvent, {type: 'hold'}> => e.type === 'hold' && tt >= e.from && tt < e.to);
  return h ? h.player : null;
};

export const resetV33Caches = () => {
  mcache.clear();
  ccache.clear();
  fcache.clear();
  osc.clear();
};

// ---------------------------------------------------------------- cloth (jersey / shorts separately)
export const CLOTH33 = {
  jersey: {hz: 1.9, zeta: 0.42, gain: 0.6, vgain: 0.016, drag: 0.0011, maxH: 0.055, maxUp: 0.05, maxDown: 0.03, maxTwist: 0.12, flutter: 0.004, maxDisp: 0.06},
  shorts: {scale: 0.33, maxH: 0.02, maxUp: 0.015, maxDown: 0.012, maxDisp: 0.025},
};
export type Cloth33 = Cloth & {maxDisp: number};
const ccache = new Map<string, {jersey: Cloth33; shorts: Cloth33}>();
const OSC_DT = 1 / 120;
/** V3.3: the jersey oscillator integrated ONCE over the whole play from t = 0 at 120 Hz (V3.2 restarted it from rest
 *  1.2 s before every frame): exact for any seek order, and ~100x cheaper per frame */
const osc = new Map<string, Float64Array>();
const oscOf = (clip: Clip32, play: Play, id: string, c: RigC): Float64Array => {
  const key = `${play.id}|${id}`;
  const hit = osc.get(key);
  if (hit) return hit;
  const J = CLOTH33.jersey;
  const dt = OSC_DT, w = 2 * Math.PI * J.hz, z = J.zeta;
  const n = Math.ceil(play.duration / dt) + 2;
  const pv: {p: V3; yaw: number}[] = [];
  for (let k = -1; k <= n + 1; k++) {
    const b = bodyAt(clip, play, id, c, clamp(k * dt, 0, play.duration));
    pv.push({p: b.pelvis, yaw: b.hipYaw});
  }
  const st = new Float64Array((n + 1) * 4);
  let x = 0, y = 0, zz = 0, th = 0, vx = 0, vy = 0, vz = 0, vth = 0;
  for (let k = 0; k <= n; k++) {
    if (k > 0) {
      const A = pv[k], B = pv[k + 1], C = pv[k + 2]; // pv[j] is time (j - 1) * dt
      const ax = (C.p[0] - 2 * B.p[0] + A.p[0]) / (dt * dt), ay = (C.p[1] - 2 * B.p[1] + A.p[1]) / (dt * dt), az = (C.p[2] - 2 * B.p[2] + A.p[2]) / (dt * dt);
      const al = (wrap(C.yaw - B.yaw) - wrap(B.yaw - A.yaw)) / (dt * dt);
      vx += (-w * w * x - 2 * z * w * vx - J.gain * clamp(ax, -40, 40)) * dt; x += vx * dt;
      vy += (-w * w * y - 2 * z * w * vy - J.gain * clamp(ay, -40, 40)) * dt; y += vy * dt;
      vz += (-w * w * zz - 2 * z * w * vz - J.vgain * w * clamp(az, -60, 60)) * dt; zz += vz * dt;
      vth += (-w * w * th - 2 * z * w * vth - 0.45 * clamp(al, -80, 80)) * dt; th += vth * dt;
    }
    st[k * 4] = x; st[k * 4 + 1] = y; st[k * 4 + 2] = zz; st[k * 4 + 3] = th;
  }
  osc.set(key, st);
  return st;
};
export const clothV33 = (play: Play, id: string, t: number, rig: RigV3): {jersey: Cloth33; shorts: Cloth33} | undefined => {
  const clip = clip33For(play, id);
  if (!clip) return undefined;
  const key = `${play.id}|${id}|${t.toFixed(5)}`;
  const hit = ccache.get(key);
  if (hit) return hit;
  const c = rigConsts(rig, id);
  const J = CLOTH33.jersey;
  const st = oscOf(clip, play, id, c);
  // linear interpolation between the two 120 Hz states around t
  const fk = clamp(t, 0, play.duration) / OSC_DT, k0 = Math.floor(fk), u = fk - k0;
  const S = (j: number) => lerp(st[k0 * 4 + j] ?? 0, st[(k0 + 1) * 4 + j] ?? st[k0 * 4 + j] ?? 0, u);
  const x = S(0), y = S(1), zz = S(2), th = S(3);
  const b0 = bodyAt(clip, play, id, c, Math.max(0, t - OSC_DT)), b = bodyAt(clip, play, id, c, t);
  const v = [(b.pelvis[0] - b0.pelvis[0]) / OSC_DT, (b.pelvis[1] - b0.pelvis[1]) / OSC_DT];
  const sp = Math.hypot(v[0], v[1]);
  let sx = x - J.drag * v[0] * sp, sy = y - J.drag * v[1] * sp;
  const hl = Math.hypot(sx, sy);
  if (hl > J.maxH) {
    sx *= J.maxH / hl;
    sy *= J.maxH / hl;
  }
  const up = clamp(zz + 0.0025 * sp, -J.maxDown, J.maxUp);
  const ph = (b.feet[0].fwdness + 1) / 4;
  const Sh = CLOTH33.shorts;
  let qx = sx * Sh.scale, qy = sy * Sh.scale;
  const ql = Math.hypot(qx, qy);
  if (ql > Sh.maxH) {
    qx *= Sh.maxH / ql;
    qy *= Sh.maxH / ql;
  }
  const out = {
    jersey: {sway: [sx, sy, up] as V3, twist: clamp(th, -J.maxTwist, J.maxTwist), flutter: J.flutter * Math.min(1, sp / 5), phase: ph, maxDisp: J.maxDisp},
    shorts: {sway: [qx, qy, clamp(up * Sh.scale, -Sh.maxDown, Sh.maxUp)] as V3, twist: 0, flutter: 0, phase: ph, maxDisp: Sh.maxDisp},
  };
  if (ccache.size > 40000) ccache.clear();
  ccache.set(key, out);
  return out;
};
