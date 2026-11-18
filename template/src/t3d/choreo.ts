// E2A 3D engine — authored footwork ("choreo", 2026-11-18, Eurostep episode).
// The procedural rig (rig.ts) simulates steps from a track; that is right for team plays but cannot
// show a two-count finish where WHICH foot lands WHERE and WHEN is the lesson. A play can now carry
//   play.choreo[id] = {feet0, steps[], pelvis[], body[], look[], arms, ev, ballKeys?, dribble?, flight?, contest?}
// for one or more players. For those players poseAt() returns the authored pose:
//   * every foot is either planted at its own step spot (fixed: it cannot slide) or swinging between two
//     spots; the heel peels off the floor before a lift (toe stays) and the heel lands first on a plant;
//   * the pelvis follows authored keys (cubic Hermite), and is capped by a smooth reach envelope so a
//     planted foot is always reachable (no IK clamp, no foot drift);
//   * hips, chest and head turn separately (hip signal of the defender, chest/eyes sell of the attacker);
//   * the ball is ONE path: dribble -> gather (two hands) -> carried in the body frame -> released from the
//     right hand -> ballistic to the glass -> ballistic to the rim -> through the net -> floor.
// Everything is a pure function of play time: identical in preview, render and seek.
import type {V2, V3} from '../tactical/geometry.ts';
import {FIBA} from '../tactical/geometry.ts';

/** hover (s): the swing reaches its top in `hover` seconds, holds there (balance on the other foot), and comes down
 *  over the last `hover` seconds — a foot kept off the floor without a slow-motion drag */
export type Step = {foot: 0 | 1; lift: number; land: number; at: V2; yaw: number; h?: number; drive?: number; hover?: number};
export type Choreo = {
  /** initial plants: [x, y, yaw] for the left (0) and right (1) foot */
  feet0: [[number, number, number], [number, number, number]];
  steps: Step[];
  /** [t, x, y, z] pelvis keys (z = pelvis height before the reach cap) */
  pelvis: [number, number, number, number][];
  /** [t, heading, hipOff, chestOff, lean, roll] — angles in radians, continuous (unwrapped) */
  body: [number, number, number, number, number, number][];
  /** [t, x, y, z] where the eyes go */
  look?: [number, number, number, number][];
  arms: 'attacker' | 'defender';
  /** named moments in play time: gather, release, land, ... */
  ev: Record<string, number>;
  /** attacker: [t, fwd, side(+ = player's right), zRel(pelvis)] ball in the body frame from the gather to the release */
  ballKeys?: [number, number, number, number][];
  /** attacker: n bounces from `from`, back in the hand at ev.gather */
  dribble?: {from: number; n: number};
  /** attacker: the finish off the glass */
  flight?: {glass: V3; tGlass: number; rim: V3; tRim: number};
  /** defender: contest with hand 0 (left) or 1 (right) */
  contest?: {from: number; peak: number; to: number; hand: 0 | 1};
};
export type ChoreoPlay = {id: string; duration: number; choreo?: Record<string, Choreo>; ballHolder?: string};

// ---------- helpers ----------
const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const mul = (a: V3, s: number): V3 => [a[0] * s, a[1] * s, a[2] * s];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const norm = (a: V3): V3 => {
  const l = len(a) || 1;
  return [a[0] / l, a[1] / l, a[2] / l];
};
const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
const lerp3 = (a: V3, b: V3, u: number): V3 => [lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u)];
const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const smooth = (x: number) => {
  const u = clamp(x);
  return u * u * (3 - 2 * u);
};
const smoother = (x: number) => {
  const u = clamp(x);
  return u * u * u * (u * (u * 6 - 15) + 10);
};
const wrap = (a: number) => {
  while (a > Math.PI) a -= 2 * Math.PI;
  while (a < -Math.PI) a += 2 * Math.PI;
  return a;
};
const fwd = (h: number): V3 => [Math.cos(h), Math.sin(h), 0];
const right = (h: number): V3 => [Math.sin(h), -Math.cos(h), 0];

/** cubic Hermite through keys [t, ...values] with Catmull-Rom tangents (non-uniform), flat at both ends */
export const hermite = (keys: number[][], t: number): number[] => {
  const n = keys.length;
  const dim = keys[0].length - 1;
  if (t <= keys[0][0]) return keys[0].slice(1);
  if (t >= keys[n - 1][0]) return keys[n - 1].slice(1);
  let i = 0;
  while (i < n - 2 && t > keys[i + 1][0]) i++;
  const a = keys[i];
  const b = keys[i + 1];
  const h = b[0] - a[0];
  const u = (t - a[0]) / h;
  const tan = (k: number, d: number) => {
    if (k === 0 || k === n - 1) return 0;
    return (keys[k + 1][d] - keys[k - 1][d]) / (keys[k + 1][0] - keys[k - 1][0]);
  };
  const h00 = 2 * u ** 3 - 3 * u ** 2 + 1;
  const h10 = u ** 3 - 2 * u ** 2 + u;
  const h01 = -2 * u ** 3 + 3 * u ** 2;
  const h11 = u ** 3 - u ** 2;
  const out: number[] = [];
  for (let d = 1; d <= dim; d++) out.push(h00 * a[d] + h10 * h * tan(i, d) + h01 * b[d] + h11 * h * tan(i + 1, d));
  return out;
};

// ---------- feet ----------
export type FootState = {c: V3; yaw: number; pitch: number; planted: boolean; swingU: number; step?: Step};

/** where foot i is at time t: c = floor point under the middle of the shoe (z = lift height) */
export const footAt = (c: Choreo, i: 0 | 1, t: number): FootState => {
  let px = c.feet0[i][0];
  let py = c.feet0[i][1];
  let pyaw = c.feet0[i][2];
  let lastLand = -1e9;
  for (const s of c.steps) {
    if (s.foot !== i) continue;
    if (t < s.lift) {
      // planted; the heel peels off over the last 0.16 s before the lift (pivot on the toe)
      const heel = 0.55 * smooth((t - (s.lift - 0.12)) / 0.12);
      const strike = -0.16 * (1 - smooth((t - lastLand) / 0.09));
      return {c: [px, py, 0], yaw: pyaw, pitch: heel + (t - lastLand < 0.09 ? strike : 0), planted: true, swingU: 0, step: s};
    }
    if (t < s.land) {
      let u = (t - s.lift) / (s.land - s.lift);
      if (s.hover) {
        const hv = Math.min(s.hover, (s.land - s.lift) / 2);
        u = t < s.lift + hv ? (0.5 * (t - s.lift)) / hv : t > s.land - hv ? 0.5 + (0.5 * (t - (s.land - hv))) / hv : 0.5;
      }
      const e = smoother(u);
      const d = Math.hypot(s.at[0] - px, s.at[1] - py);
      const hh = s.h ?? clamp(0.06 + 0.07 * d, 0.07, 0.2);
      const z = hh * Math.sin(Math.PI * Math.pow(u, 0.85));
      // toe down after the push, level and then toe up for a heel-first plant
      const pitch = 0.55 * (1 - smooth(u / 0.45)) - 0.22 * smooth((u - 0.7) / 0.3);
      return {c: [lerp(px, s.at[0], e), lerp(py, s.at[1], e), z], yaw: pyaw + wrap(s.yaw - pyaw) * e, pitch, planted: false, swingU: u, step: s};
    }
    px = s.at[0];
    py = s.at[1];
    pyaw = s.yaw;
    lastLand = s.land;
  }
  const strike = -0.16 * (1 - smooth((t - lastLand) / 0.09));
  return {c: [px, py, 0], yaw: pyaw, pitch: t - lastLand < 0.09 ? strike : 0, planted: true, swingU: 0};
};

type FootGeo = {ankle: V3; toe: V3; heel: V3};
/** shoe geometry from the foot state: rotate the flat foot about the toe (heel up) or the heel (toe up) */
export const footGeo = (f: FootState, ankleH: number, foot: number): FootGeo => {
  const F = fwd(f.yaw);
  const A0: V3 = add(add(f.c, mul(F, -0.05)), [0, 0, ankleH]);
  const T0: V3 = add(A0, add(mul(F, foot * 0.78), [0, 0, -ankleH * 0.7]));
  const H0: V3 = add(A0, add(mul(F, -foot * 0.25), [0, 0, -ankleH * 0.7]));
  const rot = (q: V3, piv: V3, p: number): V3 => {
    const r = sub(q, piv);
    const d = r[0] * F[0] + r[1] * F[1];
    const v = r[2];
    const d2 = d * Math.cos(p) + v * Math.sin(p);
    const v2 = v * Math.cos(p) - d * Math.sin(p);
    return [piv[0] + F[0] * d2, piv[1] + F[1] * d2, piv[2] + v2];
  };
  const piv = f.pitch >= 0 ? T0 : H0;
  return {ankle: rot(A0, piv, f.pitch), toe: rot(T0, piv, f.pitch), heel: rot(H0, piv, f.pitch)};
};

// ---------- pelvis with the reach cap ----------
type D = {thigh: number; shin: number; ankleH: number; foot: number; hipW: number};
const pelvisRaw = (c: Choreo, t: number): V3 => {
  const p = hermite(c.pelvis, t);
  return [p[0], p[1], p[2]];
};
const bodyAt = (c: Choreo, t: number) => {
  const b = hermite(c.body, t);
  return {heading: b[0], hipOff: b[1], chestOff: b[2], lean: b[3], roll: b[4]};
};
const capAt = (c: Choreo, t: number, dm: D): number => {
  const p = pelvisRaw(c, t);
  const b = bodyAt(c, t);
  const L = (dm.thigh + dm.shin) * 0.975;
  let cap = Infinity;
  for (const i of [0, 1] as const) {
    const f = footAt(c, i, t);
    if (!f.planted) continue;
    const g = footGeo(f, dm.ankleH, dm.foot);
    const side = i === 0 ? -1 : 1;
    const hp = add(p, mul(right(b.heading + b.hipOff), side * dm.hipW));
    const dx = hp[0] - g.ankle[0];
    const dy = hp[1] - g.ankle[1];
    cap = Math.min(cap, g.ankle[2] + Math.sqrt(Math.max(0.04 * L * L, L * L - dx * dx - dy * dy)));
  }
  return cap;
};
export const pelvisAt = (c: Choreo, t: number, dm: D): V3 => {
  const p = pelvisRaw(c, t);
  // smooth lower envelope of the cap over ±0.06 s (min-filter, then mean): always ≤ the exact cap, never pops
  const w = 0.06;
  const n = 3;
  const caps: number[] = [];
  for (let j = -2 * n; j <= 2 * n; j++) caps.push(capAt(c, t + (j * w) / n, dm));
  let s = 0;
  let k = 0;
  for (let j = 0; j <= 2 * n; j++) {
    const m = Math.min(...caps.slice(j, j + 2 * n + 1));
    if (Number.isFinite(m)) {
      s += m;
      k++;
    }
  }
  if (k === 2 * n + 1) {
    const capS = s / k;
    const kSoft = 0.015;
    const x = (capS - p[2]) / kSoft;
    if (x < 30) p[2] = capS - kSoft * Math.log1p(Math.exp(x));
  }
  return p;
};

// ---------- ball ----------
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const G = 9.8;
const para = (p0: V3, p1: V3, T: number, tau: number): V3 => {
  const v: V3 = [(p1[0] - p0[0]) / T, (p1[1] - p0[1]) / T, (p1[2] - p0[2] + 0.5 * G * T * T) / T];
  return [p0[0] + v[0] * tau, p0[1] + v[1] * tau, p0[2] + v[2] * tau - 0.5 * G * tau * tau];
};
const paraVel = (p0: V3, p1: V3, T: number, tau: number): V3 => [(p1[0] - p0[0]) / T, (p1[1] - p0[1]) / T, (p1[2] - p0[2] + 0.5 * G * T * T) / T - G * tau];

const STAND_FRAC = 0.955;
/** the ball in the holder's body frame (fwd, side, zRel) -> world */
const bodyBall = (c: Choreo, t: number, dm: D, f: number, s: number, zr: number): V3 => {
  const p = pelvisAt(c, t, dm);
  const b = bodyAt(c, t);
  const yaw = b.heading + b.chestOff * 0.6;
  return add(add(add(p, mul(fwd(yaw), f)), mul(right(yaw), s)), [0, 0, zr]);
};

export type ChoreoBall = {pos: V3; holder?: string; phase: 'dribble' | 'held' | 'flight' | 'net' | 'floor'};
export const choreoBall = (play: ChoreoPlay, t: number, dimsOf: (id: string) => D): ChoreoBall | undefined => {
  const id = play.ballHolder;
  if (!id || !play.choreo?.[id]) return undefined;
  const c = play.choreo[id];
  const dm = dimsOf(id);
  const keys = c.ballKeys!;
  const tg = c.ev.gather;
  const k0 = keys[0];
  if (c.dribble && t < tg) {
    const from = c.dribble.from;
    const u = clamp((t - from) / (tg - from));
    const cyc = u * c.dribble.n;
    const down = Math.abs(Math.cos(Math.PI * cyc)); // 1 in the hand, 0 on the floor
    const handZ = pelvisAt(c, t, dm)[2] + k0[3];
    const pos = bodyBall(c, t, dm, k0[1] + 0.16 * (1 - down), k0[2] + 0.03 * (1 - down), 0);
    pos[2] = 0.121 + (handZ - 0.121) * Math.pow(down, 0.8);
    return {pos, holder: id, phase: 'dribble'};
  }
  const tr = c.ev.release ?? Infinity;
  if (t < tr || !c.flight) {
    const k = hermite(keys, Math.min(t, keys[keys.length - 1][0]));
    return {pos: bodyBall(c, t, dm, k[0], k[1], k[2]), holder: id, phase: 'held'};
  }
  const fl = c.flight;
  const kr = hermite(keys, tr);
  const P0 = bodyBall(c, tr, dm, kr[0], kr[1], kr[2]);
  if (t < fl.tGlass) return {pos: para(P0, fl.glass, fl.tGlass - tr, t - tr), phase: 'flight'};
  if (t < fl.tRim) return {pos: para(fl.glass, fl.rim, fl.tRim - fl.tGlass, t - fl.tGlass), phase: 'flight'};
  // through the net: the arc's downward speed braked by the net, centred under the ring, then the floor
  const vIn = paraVel(fl.glass, fl.rim, fl.tRim - fl.tGlass, fl.tRim - fl.tGlass);
  const dt = t - fl.tRim;
  const v0 = 0.45 * Math.min(0, vIn[2]);
  const z0 = fl.rim[2];
  const cx = lerp(fl.rim[0], RIM[0], smooth(dt / 0.12));
  const cy = lerp(fl.rim[1], RIM[1], smooth(dt / 0.12));
  const fall = z0 + v0 * dt - 0.5 * G * dt * dt;
  if (fall > 0.121) return {pos: [cx, cy, fall], phase: 'net'};
  const tb = (v0 + Math.sqrt(v0 * v0 + 2 * G * (z0 - 0.121))) / G;
  let after = dt - tb;
  let vz = 0.55 * Math.abs(v0 - G * tb);
  let x = cx;
  let y = cy;
  const vx = 0.25;
  const vy = 0.55;
  for (let i = 0; i < 8; i++) {
    const tf = (2 * vz) / G;
    if (after <= tf || vz < 0.3) {
      const tt = Math.min(after, tf);
      return {pos: [x + vx * tt, y + vy * tt, 0.121 + Math.max(0, vz * tt - 0.5 * G * tt * tt)], phase: 'floor'};
    }
    after -= tf;
    x += vx * tf;
    y += vy * tf;
    vz *= 0.6;
  }
  return {pos: [x, y, 0.121], phase: 'floor'};
};

// ---------- pose ----------
export type ChoreoDims = D & {H: number; upper: number; fore: number; hand: number; shW: number; trunk: number; neck: number; headR: number};
type IK = (root: V3, target: V3, a: number, b: number, pole: V3) => {mid: V3; end: V3};

export const choreoPose = (play: ChoreoPlay, id: string, t: number, ballPos: V3, rim: V3, dm: ChoreoDims, ik2: IK) => {
  const c = play.choreo![id];
  const pelvis = pelvisAt(c, t, dm);
  const b = bodyAt(c, t);
  const h = b.heading;
  const hipYaw = h + b.hipOff;
  const chestYaw = h + b.chestOff;
  const up: V3 = [0, 0, 1];
  const trunkDir = norm(add(add(mul(up, Math.cos(b.lean)), mul(fwd(chestYaw), Math.sin(b.lean))), mul(right(h), -Math.sin(b.roll))));
  const chest = add(pelvis, mul(trunkDir, dm.trunk));
  const head = add(chest, mul(norm(add(trunkDir, mul(up, 0.6))), dm.neck + dm.headR * 0.85));
  const legLen = dm.thigh + dm.shin + dm.ankleH;
  const airborne = Math.max(0, pelvis[2] - legLen * STAND_FRAC);

  // legs
  const hips: [V3, V3] = [add(pelvis, mul(right(hipYaw), -dm.hipW)), add(pelvis, mul(right(hipYaw), dm.hipW))];
  const knee: V3[] = [];
  const ankle: V3[] = [];
  const toe: V3[] = [];
  for (const i of [0, 1] as const) {
    const side = i === 0 ? -1 : 1;
    const f = footAt(c, i, t);
    let g = footGeo(f, dm.ankleH, dm.foot);
    // knee drive: during a long swing the foot is pulled up under the hips (tucked), then reaches for the floor
    const drive = !f.planted ? (f.step?.drive ?? 0) : 0;
    if (drive > 0) {
      const w = drive * Math.pow(Math.sin(Math.PI * f.swingU), 0.6);
      const tuck: V3 = add(add(add(pelvis, mul(fwd(hipYaw), 0.2)), mul(right(hipYaw), side * 0.1)), [0, 0, -(dm.thigh + dm.shin) * 0.62]);
      const off = sub(g.toe, g.ankle);
      const a2 = lerp3(g.ankle, tuck, w);
      const pt = 0.5 * w; // toe points down when tucked
      const F = fwd(f.yaw);
      const toe2 = add(a2, add(mul(F, dm.foot * 0.78 * Math.cos(pt)), [0, 0, -dm.ankleH * 0.7 - dm.foot * 0.6 * Math.sin(pt)]));
      g = {ankle: a2, toe: lerp3(add(a2, off), toe2, w), heel: g.heel};
    }
    const F = fwd(f.yaw);
    const pole = norm(add(add(lerp3(F, fwd(hipYaw), 0.5), mul(right(hipYaw), side * 0.18)), [0, 0, 0.08]));
    const s = ik2(hips[i], g.ankle, dm.thigh, dm.shin, pole);
    knee.push(s.mid);
    ankle.push(s.end);
    toe.push(add(s.end, sub(g.toe, g.ankle)));
  }

  // arms
  const chestR = right(chestYaw);
  const chestF = fwd(chestYaw);
  const shoulderBase = add(chest, mul(trunkDir, -0.04));
  const shoulder: [V3, V3] = [add(shoulderBase, mul(chestR, -dm.shW)), add(shoulderBase, mul(chestR, dm.shW))];
  const armLen = dm.upper + dm.fore;
  const hand: V3[] = [];
  const poles: V3[] = [];
  const ev = c.ev;
  for (const i of [0, 1] as const) {
    const side = i === 0 ? -1 : 1;
    const sh = shoulder[i];
    const L = (x: number, y: number, z: number): V3 => add(sh, add(add(mul(chestR, x * side), mul(chestF, y)), [0, 0, z]));
    let tgt: V3 = L(0.12, 0.12, -armLen * 0.9);
    let pole: V3 = norm(add(add(mul(chestF, -1), mul(chestR, side * 0.3)), [0, 0, -0.2]));
    const blend = (w: number, p: V3, pp?: V3) => {
      if (w <= 0) return;
      tgt = lerp3(tgt, p, clamp(w));
      if (pp) pole = norm(lerp3(pole, pp, clamp(w)));
    };
    const onBall = (dx: number, df: number, dz = 0): V3 => add(add(add(ballPos, mul(chestR, side * dx)), mul(chestF, df)), [0, 0, dz]);
    if (c.arms === 'attacker') {
      const tg = ev.gather;
      const tr = ev.release ?? Infinity;
      const tl = ev.land ?? Infinity;
      // run swing before the gather (left arm), dribble hand on the ball (right)
      if (t < tg) {
        if (i === 1) {
          const handOn: V3 = [ballPos[0], ballPos[1], Math.max(ballPos[2] + 0.1, pelvis[2] - 0.05)];
          blend(1, handOn, norm(add(mul(chestR, 0.6), [0, 0, -0.6])));
        } else blend(1, L(0.26, 0.3, -0.32), norm(add(mul(chestR, side), [0, 0, -0.5])));
      }
      // gather: the left hand comes over the ball in the last 0.12 s, both hands secure it at tg
      const both = smooth((t - (tg - 0.12)) / 0.12) * (1 - smooth((t - tr) / 0.06));
      if (both > 0) blend(both, onBall(0.118, -0.025, i === 1 ? -0.01 : 0.01), norm(add(mul(chestR, side), [0, 0, -0.7])));
      if (Number.isFinite(tr)) {
        // release: the right hand under and behind the ball until it leaves, then follows through to the rim
        const toRim = norm(sub(rim, sh));
        if (i === 1) {
          const ride = smooth((t - (tr - 0.14)) / 0.08) * (1 - smooth((t - tr) / 0.02));
          blend(ride, add(add(ballPos, mul(toRim, -0.05)), [0, 0, -0.16]), norm(add(mul(chestR, 0.7), [0, 0, -0.5])));
          const follow = smooth((t - tr + 0.02) / 0.16) * (1 - smooth((t - (tl - 0.05)) / 0.3));
          blend(follow, add(sh, add(mul(toRim, armLen * 0.97), [0, 0, 0.05])), norm(add(mul(chestR, 0.7), [0, 0, -0.5])));
        } else {
          // the off arm leaves the ball and shields: forearm up between the ball and the defender
          const guard = smooth((t - (tr - 0.14)) / 0.1) * (1 - smooth((t - (tl - 0.05)) / 0.35));
          blend(guard, L(0.3, 0.26, 0.1), norm(add(mul(chestR, side), [0, 0, -0.6])));
        }
      }
    } else {
      // defender: active stance hands, the lead hand mirrors the ball
      const sway = 0.03 * Math.sin(t * 7 + i);
      blend(1, L(0.36, 0.3, -0.3 + (i === 1 ? 0.12 : 0) + sway), norm(add(mul(chestR, side), [0, 0, -0.5])));
      if (c.contest && i === c.contest.hand) {
        const k = c.contest;
        const w = smooth((t - k.from) / Math.max(0.05, k.peak - k.from)) * (1 - smooth((t - k.to) / 0.35));
        // reach toward the ball, but stop short of it (the hand stays behind the ball, never through it)
        const d = sub(ballPos, sh);
        const reach = Math.min(armLen * 0.97, Math.max(0.2, len(d) - 0.3));
        blend(w, add(sh, mul(norm(add(norm(d), [0, 0, 0.35])), reach)), norm(add(mul(chestF, -0.3), [0, 0, -1])));
      }
    }
    hand.push(tgt);
    poles.push(pole);
  }
  const elbow: V3[] = [];
  const wrist: V3[] = [];
  const tips: V3[] = [];
  for (const i of [0, 1] as const) {
    const s = ik2(shoulder[i], hand[i], dm.upper, dm.fore, poles[i]);
    elbow.push(s.mid);
    wrist.push(s.end);
    tips.push(add(s.end, mul(norm(sub(s.end, s.mid)), dm.hand)));
  }
  // head: eyes on the look target (or the ball), the neck turns within its range
  const lk = c.look ? hermite(c.look, t) : ballPos;
  const lookA = Math.atan2(lk[1] - head[1], lk[0] - head[0]);
  const headYaw = chestYaw + clamp(wrap(lookA - chestYaw), -1.15, 1.15) * 0.9;
  const headPitch = clamp(Math.atan2(head[2] - lk[2], Math.hypot(lk[0] - head[0], lk[1] - head[1])) * 0.5, -0.35, 0.45);
  return {
    pelvis,
    chest,
    head,
    heading: hipYaw,
    chestYaw,
    lean: b.lean,
    roll: b.roll,
    hip: hips,
    knee: [knee[0], knee[1]] as [V3, V3],
    ankle: [ankle[0], ankle[1]] as [V3, V3],
    toe: [toe[0], toe[1]] as [V3, V3],
    shoulder,
    elbow: [elbow[0], elbow[1]] as [V3, V3],
    wrist: [wrist[0], wrist[1]] as [V3, V3],
    hand: [tips[0], tips[1]] as [V3, V3],
    airborne,
    headYaw,
    headPitch,
  };
};
