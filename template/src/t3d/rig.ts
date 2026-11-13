// E2A 3D engine — procedural athlete rig (pure, no React / no three.js).
// Turns a Play (timed waypoints + ball events + optional per-player actions) into a full-body pose
// for every player at any play time:
//   * footsteps are SIMULATED once per play (120 Hz, deterministic, cached): each foot is either
//     planted (fixed on the floor -> no foot sliding by construction) or swinging to its next plant;
//   * the gait phase advances with the distance actually run (stride grows with speed), so cadence
//     and step length follow the waypoints;
//   * legs and arms are solved with two-bone IK (hip->knee->ankle, shoulder->elbow->wrist);
//   * the torso leans with speed and acceleration, banks into turns and counter-rotates the hips;
//   * actions (screen, stance, topLock, catch, shoot, layup, pass, dribble, contest) blend in/out.
// World units: metres on the FIBA half court (x across, y from the baseline, z up), as play.ts.
import type {V2, V3} from '../tactical/geometry.ts';
import type {Play} from '../tactical/play.ts';
import {posAt, stateOf} from '../tactical/play.ts';

export type ActionType = 'screen' | 'stance' | 'topLock' | 'catchReady' | 'shoot' | 'layup' | 'pass' | 'dribble' | 'contest' | 'seal' | 'celebrate';
export type Action = {type: ActionType; from: number; to: number; face?: string | number; side?: number; pose?: 'low'};
/** topLock pose 'low' (prototype 2026-11-13, opt-in per action): deeper, more upright, hips open to the
 *  screen side, weight over the inside foot, denial arm straighter into the lane. Without `pose` nothing changes. */

export type PlayWithActions = Play & {actions?: Record<string, Action[]>};

export type Pose = {
  pelvis: V3;
  chest: V3; // base of the neck
  head: V3;
  heading: number; // body yaw (radians, 0 = +x)
  chestYaw: number;
  lean: number; // forward pitch of the trunk
  roll: number; // sideways bank
  hip: [V3, V3]; // L, R
  knee: [V3, V3];
  ankle: [V3, V3];
  toe: [V3, V3];
  shoulder: [V3, V3];
  elbow: [V3, V3];
  wrist: [V3, V3];
  hand: [V3, V3];
  airborne: number; // metres above the floor (jumps)
  dims: Dims;
};

export type Dims = {H: number; thigh: number; shin: number; ankleH: number; foot: number; upper: number; fore: number; hand: number; hipW: number; shW: number; trunk: number; neck: number; headR: number};

export const dimsFor = (H: number): Dims => {
  const k = H / 2.0;
  return {H, thigh: 0.5 * k, shin: 0.49 * k, ankleH: 0.085 * k, foot: 0.27 * k, upper: 0.34 * k, fore: 0.29 * k, hand: 0.17 * k, hipW: 0.105 * k, shW: 0.215 * k, trunk: 0.55 * k, neck: 0.075 * k, headR: 0.112 * k};
};

// ---------- small vector helpers ----------
const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const mul = (a: V3, s: number): V3 => [a[0] * s, a[1] * s, a[2] * s];
const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
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
const wrap = (a: number) => {
  while (a > Math.PI) a -= 2 * Math.PI;
  while (a < -Math.PI) a += 2 * Math.PI;
  return a;
};

/** two-bone IK: returns the middle joint for root->end with lengths a, b and a pole direction */
export const ik2 = (root: V3, target: V3, a: number, b: number, pole: V3): {mid: V3; end: V3} => {
  let d = sub(target, root);
  let L = len(d);
  const maxL = (a + b) * 0.999;
  const minL = Math.abs(a - b) + 0.02;
  if (L > maxL) {
    d = mul(norm(d), maxL);
    L = maxL;
  } else if (L < minL) {
    d = mul(norm(d), minL);
    L = minL;
  }
  const dir = norm(d);
  const cosA = clamp((a * a + L * L - b * b) / (2 * a * L), -1, 1);
  const sinA = Math.sqrt(1 - cosA * cosA);
  // pole projected perpendicular to the bone direction
  let p = sub(pole, mul(dir, dot(pole, dir)));
  if (len(p) < 1e-5) p = Math.abs(dir[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0];
  p = norm(p);
  const mid = add(root, add(mul(dir, a * cosA), mul(p, a * sinA)));
  return {mid, end: add(root, d)};
};

// ---------- body frame ----------
const fwd = (h: number): V3 => [Math.cos(h), Math.sin(h), 0];
const right = (h: number): V3 => [Math.sin(h), -Math.cos(h), 0];

// ---------- per-player simulation (footsteps, heading, speed) ----------
type Foot = {planted: boolean; p: V3; from: V3; to: V3; t0: number; dur: number};
type SimRow = {t: number; heading: number; speed: number; acc: number; turn: number; feet: [V3, V3]; phase: number; lift: [number, number]};
type Sim = {dt: number; t0: number; rows: SimRow[]};

const simCache = new Map<string, Sim>();
const DT = 1 / 120;

export const actionsOf = (play: PlayWithActions, id: string): Action[] => {
  const own = play.actions?.[id] ?? [];
  const out: Action[] = [...own];
  // automatic actions from the ball events
  for (const e of play.ball) {
    if (e.type === 'shot' && e.player === id) out.push({type: 'shoot', from: e.t0 - 0.5, to: e.t0 + 0.75});
    if (e.type === 'layup' && e.player === id) out.push({type: 'layup', from: e.t0 - 0.38, to: e.t0 + 0.55});
    if (e.type === 'pass' && e.from === id) out.push({type: 'pass', from: e.t0 - 0.22, to: e.t0 + 0.18});
    if (e.type === 'pass' && e.to === id && !own.some((a) => a.type === 'catchReady' && a.to >= e.t1 - 0.05 && a.from <= e.t1)) out.push({type: 'catchReady', from: e.t1 - 0.45, to: e.t1 + 0.1});
    if (e.type === 'hold' && e.player === id && e.dribble) out.push({type: 'dribble', from: e.from, to: e.to});
  }
  return out;
};

/** weight of an action at time t (smooth in/out over `blend` seconds) */
const weight = (a: Action, t: number, blend = 0.18) => {
  if (t < a.from - blend || t > a.to + blend) return 0;
  return Math.min(smooth((t - (a.from - blend)) / blend), smooth((a.to + blend - t) / blend));
};

const activeW = (acts: Action[], type: ActionType, t: number, blend?: number) => {
  let w = 0;
  let hit: Action | undefined;
  for (const a of acts) {
    if (a.type !== type) continue;
    const x = weight(a, t, blend);
    if (x > w) {
      w = x;
      hit = a;
    }
  }
  return {w, a: hit};
};

/** where the player looks / faces when not running: ball, man, or an explicit target */
const lookAngle = (play: PlayWithActions, id: string, t: number, acts: Action[]): number | undefined => {
  for (const a of acts) {
    if (a.face !== undefined && t >= a.from - 0.1 && t <= a.to + 0.1) {
      if (typeof a.face === 'number') return a.face;
      const me = posAt(play.tracks[id], t);
      const q = posAt(play.tracks[a.face], t);
      return Math.atan2(q[1] - me[1], q[0] - me[0]);
    }
  }
  return undefined;
};

const simulate = (play: PlayWithActions, id: string, dims: Dims): Sim => {
  const key = `${play.id}|${id}`;
  const hit = simCache.get(key);
  if (hit) return hit;
  const acts = actionsOf(play, id);
  const wp = play.tracks[id];
  const T0 = -0.5;
  const T1 = play.duration + 0.5;
  const rows: SimRow[] = [];
  let heading = stateOf(play, id, 0).facing;
  let headingVel = 0;
  let phase = 0;
  const stanceHalf = (stanceW: number) => stanceW / 2;
  // initial feet: parallel stance
  const p0 = posAt(wp, 0);
  const restOff = (side: number, h: number, stanceW: number, stagger: number): V3 => {
    const r = right(h);
    const f = fwd(h);
    return [r[0] * side * stanceHalf(stanceW) + f[0] * stagger * side, r[1] * side * stanceHalf(stanceW) + f[1] * stagger * side, 0];
  };
  const feet: [Foot, Foot] = [0, 1].map((i) => {
    const side = i === 0 ? -1 : 1;
    const o = restOff(side, heading, 0.42, 0);
    const p: V3 = [p0[0] + o[0], p0[1] + o[1], 0];
    return {planted: true, p, from: p, to: p, t0: 0, dur: 0};
  }) as [Foot, Foot];
  let prevVel: V2 = [0, 0];
  let prevHeading = heading;
  for (let t = T0; t <= T1 + 1e-9; t += DT) {
    const tc = clamp(t, 0, play.duration);
    const p = posAt(wp, tc);
    const pa = posAt(wp, tc - DT);
    const pb = posAt(wp, tc + DT);
    const vel: V2 = [(pb[0] - pa[0]) / (2 * DT), (pb[1] - pa[1]) / (2 * DT)];
    const speed = Math.hypot(vel[0], vel[1]);
    const acc = (speed - Math.hypot(prevVel[0], prevVel[1])) / DT;
    prevVel = vel;
    // ----- heading: critically damped toward the desired facing
    const look = lookAngle(play, id, tc, acts);
    const base = stateOf(play, id, tc).facing;
    let want = look ?? base;
    // when sprinting, the body points where it runs unless an action forces a facing
    if (look === undefined && speed > 2.2) want = Math.atan2(vel[1], vel[0]);
    const k = 26; // stiffness
    const err = wrap(want - heading);
    headingVel += (k * k * err - 2 * k * headingVel) * DT;
    heading = wrap(heading + headingVel * DT);
    const turn = wrap(heading - prevHeading) / DT;
    prevHeading = heading;
    // ----- stance width by action
    const screenW = activeW(acts, 'screen', tc).w;
    const stanceW0 = activeW(acts, 'stance', tc).w;
    const lockA = activeW(acts, 'topLock', tc);
    const lockW = lockA.w;
    const lowW = lockA.a?.pose === 'low' ? lockW : 0;
    const sealW = activeW(acts, 'seal', tc).w;
    const stanceW = lerp(0.36, 0.62, Math.max(screenW, stanceW0, lockW * 0.9, sealW)) + 0.08 * lowW;
    // ----- gait phase from distance (stride grows with speed)
    const cycleLen = clamp(0.8 + 0.5 * speed, 0.9, 3.4);
    let rate = speed / cycleLen;
    // settle: if a foot is far from its rest spot while standing, keep stepping slowly
    const restDev = [0, 1].map((i) => {
      const side = i === 0 ? -1 : 1;
      const o = restOff(side, heading, stanceW, 0.05);
      const r: V3 = [p[0] + o[0], p[1] + o[1], 0];
      return Math.hypot(feet[i].p[0] - r[0], feet[i].p[1] - r[1]);
    });
    const anySwing = !feet[0].planted || !feet[1].planted;
    if (speed < 0.9 && (Math.max(...restDev) > 0.13 || anySwing)) rate = Math.max(rate, 1.6);
    phase += rate * DT;
    const beta = lerp(0.6, 0.3, clamp(speed / 6)); // stance fraction of the cycle
    const cycleDur = rate > 1e-3 ? 1 / rate : 1;
    const lift: [number, number] = [0, 0];
    for (let i = 0; i < 2; i++) {
      const side = i === 0 ? -1 : 1;
      const fp = (((phase + (i === 0 ? 0 : 0.5)) % 1) + 1) % 1;
      const inStance = fp < beta;
      const f = feet[i];
      if (inStance) {
        // a swing still in the air finishes its own arc (never snaps to the target)
        if (!f.planted && t - f.t0 < f.dur - 0.08) {
          f.t0 = t - 0.5 * 0.16;
          f.dur = 0.16;
          f.from = [f.p[0] - (f.to[0] - f.p[0]), f.p[1] - (f.to[1] - f.p[1]), 0];
        }
      } else if (f.planted) {
        // lift off: commit the next plant, predicted at mid-stance of the next contact
        const swingT = (1 - fp) * cycleDur;
        const tPlant = tc + swingT;
        const tMid = tPlant + (beta * cycleDur) / 2;
        const pm = posAt(wp, Math.min(play.duration, tMid));
        const hFuture = heading + clamp(turn, -6, 6) * Math.min(0.25, swingT);
        const o = restOff(side, hFuture, stanceW, 0.05);
        const target: V3 = [pm[0] + o[0], pm[1] + o[1], 0];
        f.planted = false;
        f.from = f.p;
        f.to = target;
        f.t0 = t;
        f.dur = Math.max(0.12, swingT);
      }
      if (!f.planted) {
        const u = clamp((t - f.t0) / f.dur);
        const e = smooth(u);
        const h = Math.sin(Math.PI * u) * clamp(0.05 + 0.045 * speed, 0.06, 0.3) * Math.min(1, Math.hypot(f.to[0] - f.from[0], f.to[1] - f.from[1]) / 0.3 + 0.25);
        f.p = [lerp(f.from[0], f.to[0], e), lerp(f.from[1], f.to[1], e), h];
        lift[i] = u;
        if (u >= 1) {
          f.planted = true;
          f.p = f.to;
        }
      }
    }
    rows.push({t, heading, speed, acc, turn, feet: [[...feet[0].p] as V3, [...feet[1].p] as V3], phase, lift});
  }
  const sim = {dt: DT, t0: T0, rows};
  simCache.set(key, sim);
  return sim;
};

const rowAt = (sim: Sim, t: number): SimRow => {
  const f = (t - sim.t0) / sim.dt;
  const i = clamp(Math.floor(f), 0, sim.rows.length - 2);
  const u = clamp(f - i);
  const a = sim.rows[i];
  const b = sim.rows[i + 1];
  return {
    t,
    heading: a.heading + wrap(b.heading - a.heading) * u,
    speed: lerp(a.speed, b.speed, u),
    acc: lerp(a.acc, b.acc, u),
    turn: lerp(a.turn, b.turn, u),
    feet: [lerp3(a.feet[0], b.feet[0], u), lerp3(a.feet[1], b.feet[1], u)],
    phase: lerp(a.phase, b.phase, u),
    lift: [lerp(a.lift[0], b.lift[0], u), lerp(a.lift[1], b.lift[1], u)],
  };
};

/** mean of a value over a short window (removes the 120 Hz jitter of acceleration) */
const avg = (sim: Sim, t: number, pick: (r: SimRow) => number, w = 0.12) => {
  let s = 0;
  const n = 7;
  for (let i = 0; i < n; i++) s += pick(rowAt(sim, t - w / 2 + (w * i) / (n - 1)));
  return s / n;
};

export const PLAYER_HEIGHTS: Record<string, number> = {O1: 1.9, O2: 1.98, O3: 2.0, O4: 2.06, O5: 2.1, X1: 1.91, X2: 1.99, X3: 2.01, X4: 2.05, X5: 2.09};

/** jump height for shots and layups */
const jumpAt = (acts: Action[], t: number) => {
  let z = 0;
  for (const a of acts) {
    if (a.type === 'shoot') {
      // dip 0.0-0.25, take-off at 0.30, release near the apex, land ~0.9
      const tt = t - a.from;
      const up = 0.3;
      const air = 0.5;
      if (tt > up && tt < up + air) z = Math.max(z, 0.42 * Math.sin((Math.PI * (tt - up)) / air));
    }
    if (a.type === 'layup') {
      const tt = t - a.from;
      const up = 0.22;
      const air = 0.62;
      if (tt > up && tt < up + air) z = Math.max(z, 0.62 * Math.sin((Math.PI * (tt - up)) / air));
    }
    if (a.type === 'contest') {
      const tt = t - a.from;
      if (tt > 0.05 && tt < 0.5) z = Math.max(z, 0.25 * Math.sin((Math.PI * (tt - 0.05)) / 0.45));
    }
  }
  return z;
};

export type BallHint = {holder?: string; pos: V3};

/**
 * Full pose of player `id` at play time t. `ball` is the ball state (from play.ts) so the
 * hands can hold it, `rim` is the basket for shooting arms.
 */
export const poseAt = (play: PlayWithActions, id: string, t: number, ball: BallHint, rim: V3): Pose => {
  const H = PLAYER_HEIGHTS[id] ?? 2.0;
  const D = dimsFor(H);
  const sim = simulate(play, id, D);
  const r = rowAt(sim, t);
  const acts = actionsOf(play, id);
  const tc = clamp(t, 0, play.duration);
  const p2 = posAt(play.tracks[id], tc);
  const h = r.heading;
  const F = fwd(h);
  const R = right(h);
  const speed = r.speed;
  const run = clamp((speed - 0.4) / 3.2);
  const acc = avg(sim, t, (x) => x.acc, 0.2);
  const turn = avg(sim, t, (x) => x.turn, 0.2);

  const w = (type: ActionType, blend?: number) => activeW(acts, type, tc, blend);
  const screen = w('screen');
  const stance = w('stance');
  const lock = w('topLock');
  const low = lock.a?.pose === 'low' ? lock.w : 0;
  const seal = w('seal');
  const catchR = w('catchReady', 0.15);
  const shoot = w('shoot', 0.12);
  const layup = w('layup', 0.12);
  const pass = w('pass', 0.1);
  const dribble = w('dribble');
  const contest = w('contest', 0.12);
  const celebrate = w('celebrate', 0.2);
  const crouchAmt = Math.max(stance.w, lock.w, screen.w * 0.5, seal.w * 0.7, catchR.w * 0.5) * (1 - run * 0.6);

  // ----- pelvis
  const legLen = D.thigh + D.shin + D.ankleH;
  const air = jumpAt(acts, tc);
  // shot dip before take-off
  let dip = 0;
  if (shoot.a) {
    const tt = tc - shoot.a.from;
    if (tt > 0 && tt < 0.3) dip = 0.1 * Math.sin((Math.PI * tt) / 0.3);
  }
  if (layup.a) {
    const tt = tc - layup.a.from;
    if (tt > 0 && tt < 0.22) dip = Math.max(dip, 0.08 * Math.sin((Math.PI * tt) / 0.22));
  }
  const bob = run * 0.035 * Math.cos(4 * Math.PI * r.phase);
  const pelvisZ = legLen * (0.955 - 0.1 * run - 0.13 * crouchAmt) - dip + bob + air - 0.06 * low;
  // the hips sit slightly behind/ahead of the feet midpoint depending on speed; use the track position
  // (low top-lock: weight shifted 5 cm over the inside foot, toward the lock side)
  const pelvis: V3 = low > 0 ? add([p2[0], p2[1], pelvisZ], mul(R, 0.05 * low * (lock.a?.side ?? 1))) : [p2[0], p2[1], pelvisZ];

  // ----- trunk orientation
  const lean = clamp(0.06 + 0.05 * speed + 0.025 * acc, -0.12, 0.42) * (1 - Math.max(shoot.w, layup.w) * 0.7) + crouchAmt * 0.28 + catchR.w * 0.06 - celebrate.w * 0.05 - 0.12 * low;
  const roll = clamp(speed * turn * 0.035, -0.28, 0.28);
  const counter = run * 0.16 * Math.sin(2 * Math.PI * r.phase);
  const sideTurn = (lock.w * 0.5 + 0.35 * low) * (lock.a?.side ?? 1) + seal.w * 0.6 * (seal.a?.side ?? 1);
  const chestYaw = h + counter + sideTurn * 0.35;
  const up: V3 = [0, 0, 1];
  // trunk direction: up tilted forward by lean and sideways by roll
  const trunkDir = norm(add(add(mul(up, Math.cos(lean)), mul(fwd(chestYaw), Math.sin(lean))), mul(right(h), -Math.sin(roll))));
  const chest = add(pelvis, mul(trunkDir, D.trunk));
  const head = add(chest, mul(norm(add(trunkDir, mul(up, 0.6))), D.neck + D.headR * 0.85));

  // ----- legs
  const hipL = add(pelvis, mul(right(h + counter * -0.6), -D.hipW));
  const hipR = add(pelvis, mul(right(h + counter * -0.6), D.hipW));
  const hips: [V3, V3] = [hipL, hipR];
  const knee: V3[] = [];
  const ankle: V3[] = [];
  const toe: V3[] = [];
  for (let i = 0; i < 2; i++) {
    const side = i === 0 ? -1 : 1;
    let fp = r.feet[i];
    // in the air the feet follow the body (tucked)
    if (air > 0.001) {
      const tuck: V3 = add(add(p2.length ? [p2[0], p2[1], 0] : [0, 0, 0], mul(R, side * 0.16)), mul(F, side * 0.05));
      fp = lerp3(fp, [tuck[0], tuck[1], air * 0.85], clamp(air / 0.12));
    }
    const a: V3 = [fp[0], fp[1], fp[2] + D.ankleH];
    // foot direction: heading, splayed slightly outward
    const fdir = fwd(h + side * -0.12 + (crouchAmt > 0.3 ? side * -0.12 : 0));
    // knee pole: forward, slightly outward
    const pole = norm(add(add(F, mul(R, side * 0.25)), [0, 0, 0.1]));
    const s = ik2(hips[i], a, D.thigh, D.shin, pole);
    knee.push(s.mid);
    ankle.push(s.end);
    // toe: pointing down a bit while swinging
    const pitchDown = (fp[2] > 0.02 ? 0.35 : 0) + (air > 0.02 ? 0.6 : 0);
    toe.push(add(s.end, add(mul(fdir, D.foot * 0.78 * Math.cos(pitchDown)), [0, 0, -D.ankleH * 0.7 - D.foot * 0.6 * Math.sin(pitchDown)])));
  }

  // ----- arms
  const chestR = right(chestYaw);
  const chestF = fwd(chestYaw);
  const shoulderBase = add(chest, mul(trunkDir, -0.04));
  const shoulder: [V3, V3] = [add(shoulderBase, mul(chestR, -D.shW)), add(shoulderBase, mul(chestR, D.shW))];
  const armLen = D.upper + D.fore;
  const hand: V3[] = [];
  const elbowPoles: V3[] = [];
  const isBallHolder = ball.holder === id;
  for (let i = 0; i < 2; i++) {
    const side = i === 0 ? -1 : 1;
    const sh = shoulder[i];
    // local helper: target = shoulder + right*x + forward*y + up*z (chest frame)
    const L = (x: number, y: number, z: number): V3 => add(sh, add(add(mul(chestR, x * side), mul(chestF, y)), [0, 0, z]));
    // run swing: opposite to the leg on the same side
    const sw = Math.sin(2 * Math.PI * (r.phase + (i === 0 ? 0.5 : 0)));
    let tgt = L(0.13 - 0.04 * run, 0.13 - 0.07 * run + (0.04 + 0.38 * run) * sw, -armLen * (0.92 - 0.3 * run) + Math.max(0, sw) * 0.18 * run);
    let pole: V3 = norm(add(add(mul(chestF, -1), mul(chestR, side * 0.25)), [0, 0, -0.2]));
    const blend = (wgt: number, t2: V3, p2pole?: V3) => {
      if (wgt <= 0) return;
      tgt = lerp3(tgt, t2, wgt);
      if (p2pole) pole = norm(lerp3(pole, p2pole, wgt));
    };
    // defensive stance: hands wide and active
    blend(stance.w * (1 - run * 0.7), L(0.4, 0.3, -0.34 + (i === 1 ? 0.14 : 0)), norm(add(mul(chestR, side), [0, 0, -0.5])));
    // top-lock: denial arm out into the lane, other arm feels the cutter
    if (lock.w > 0) {
      const lockSide = lock.a?.side ?? 1;
      const deny = side === lockSide;
      const denyT = low > 0 ? L(0.58, 0.36, 0.16) : L(0.5, 0.42, 0.1);
      const feelT = low > 0 ? L(0.2, 0.26, -0.22) : L(0.22, 0.38, -0.25);
      blend(lock.w, deny ? denyT : feelT, norm(add(mul(chestR, side), [0, 0, -0.4])));
    }
    // screen: arms crossed low in front of the body (legal screen posture)
    blend(screen.w, L(-0.06, 0.24, -0.38), norm(add(mul(chestR, side), [0, 0, -0.6])));
    // seal: forearm and back against the defender
    blend(seal.w, L(0.3, 0.12, -0.18), norm(add(mul(chestR, side), [0, 0, -0.4])));
    // contest: one hand high
    blend(contest.w, i === 1 ? L(0.08, 0.32, 0.55) : L(0.35, 0.15, -0.35), norm(add(mul(chestF, -0.3), [0, 0, -1])));
    // catch ready: hands showing a target at chest height
    blend(catchR.w * (isBallHolder ? 0.3 : 1), L(-0.02, 0.4, -0.12), norm(add(mul(chestR, side), [0, 0, -0.8])));
    // holding the ball: both hands on it
    if (isBallHolder && dribble.w < 0.5 && shoot.w < 0.01 && layup.w < 0.01) {
      const ballSide: V3 = add(ball.pos, mul(chestR, side * 0.115));
      blend(0.95, add(ballSide, mul(chestF, -0.03)), norm(add(mul(chestR, side), [0, 0, -0.7])));
    }
    // dribble: right hand on top of the ball, left arm protects
    if (dribble.w > 0 && isBallHolder) {
      if (i === 1) blend(dribble.w, add(ball.pos, [0, 0, 0.11]), norm(add(mul(chestF, -1), [0, 0, 0.2])));
      else blend(dribble.w, L(0.3, 0.32, -0.28), norm(add(mul(chestR, -1), [0, 0, -0.5])));
    }
    // pass: hands follow the ball and push forward
    if (pass.a && pass.w > 0) {
      const tt = (tc - pass.a.from) / (pass.a.to - pass.a.from);
      const ext = smooth((tt - 0.4) / 0.4);
      blend(pass.w, L(0.1, 0.25 + 0.4 * ext, -0.15 + 0.05 * ext), norm(add(mul(chestR, side), [0, 0, -0.6])));
    }
    // shooting: gather at chest -> set above the forehead -> release to the rim -> follow-through
    if (shoot.a && shoot.w > 0) {
      const tt = tc - shoot.a.from;
      const toRim = norm(sub(rim, sh));
      const gather = L(0.0, 0.3, -0.2);
      const set = add(head, add(mul(chestF, 0.16), [0, 0, 0.1 + 0.02 * side]));
      const setSide = add(set, mul(chestR, side * 0.1));
      const follow = add(sh, add(mul(toRim, armLen * 0.98), [0, 0, 0.12]));
      let tg: V3;
      if (tt < 0.22) tg = lerp3(gather, setSide, smooth(tt / 0.22) * 0.4);
      else if (tt < 0.48) tg = lerp3(lerp3(gather, setSide, 0.4), setSide, smooth((tt - 0.22) / 0.26));
      else if (tt < 0.64) tg = i === 1 ? lerp3(setSide, follow, smooth((tt - 0.48) / 0.16)) : lerp3(setSide, add(setSide, [0, 0, 0.12]), smooth((tt - 0.48) / 0.16));
      else tg = i === 1 ? follow : add(setSide, mul(chestR, side * 0.12));
      blend(shoot.w, tg, norm(add(mul(chestR, side * 0.8), [0, 0, -0.4])));
    }
    // layup: carry the ball up with the outside hand toward the rim
    if (layup.a && layup.w > 0) {
      const tt = tc - layup.a.from;
      const toRim = norm(sub(rim, sh));
      const reach = add(sh, add(mul(toRim, armLen * 0.97), [0, 0, 0.0]));
      const carry = L(0.05, 0.3, -0.05);
      const tg = i === 1 ? lerp3(carry, reach, smooth((tt - 0.12) / 0.38)) : lerp3(carry, L(0.3, 0.25, -0.15), smooth((tt - 0.3) / 0.2));
      blend(layup.w, tg, norm(add(mul(chestR, side * 0.6), [0, 0, -0.6])));
    }
    // celebrate: small fist pump
    blend(celebrate.w, L(0.15, 0.2, -0.05 + 0.08 * Math.sin(tc * 12)), norm(add(mul(chestR, side), [0, 0, -1])));
    hand.push(tgt);
    elbowPoles.push(pole);
  }
  const elbow: V3[] = [];
  const wrist: V3[] = [];
  const handTip: V3[] = [];
  for (let i = 0; i < 2; i++) {
    const s = ik2(shoulder[i], hand[i], D.upper, D.fore, elbowPoles[i]);
    elbow.push(s.mid);
    wrist.push(s.end);
    const dir = norm(sub(s.end, s.mid));
    handTip.push(add(s.end, mul(dir, D.hand)));
  }
  void cross;
  return {
    pelvis,
    chest,
    head,
    heading: h,
    chestYaw,
    lean,
    roll,
    hip: hips,
    knee: [knee[0], knee[1]],
    ankle: [ankle[0], ankle[1]],
    toe: [toe[0], toe[1]],
    shoulder,
    elbow: [elbow[0], elbow[1]],
    wrist: [wrist[0], wrist[1]],
    hand: [handTip[0], handTip[1]],
    airborne: air,
    dims: D,
  };
};

/** feet positions over time — used by the QC (foot sliding test) */
export const footTrack = (play: PlayWithActions, id: string) => {
  const D = dimsFor(PLAYER_HEIGHTS[id] ?? 2);
  return simulate(play, id, D);
};
