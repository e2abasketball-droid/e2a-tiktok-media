// E2A Tactical engine — a play is DATA: players, their timed waypoints, ball events and named
// moments ("marks"). Everything here is pure (no React) so the same code drives the render and the
// tactical-accuracy tests (scripts/test-tactical.mts).
import type {V2, V3} from './geometry.ts';
import {FIBA} from './geometry.ts';

export type Team = 'O' | 'X';

export type PlayerSpec = {
  id: string; // "O1".."O5", "X1".."X5"
  team: Team;
  role: string; // "Passer", "Shooter", ...
  /** id of the attacker this defender guards (defence only) */
  guards?: string;
};

/** [seconds, x, y] — the player is exactly there at that time. Two equal points = standing still. */
export type Waypoint = [number, number, number];

export type BallEvent =
  | {type: 'hold'; player: string; from: number; to: number; dribble?: boolean}
  | {type: 'pass'; from: string; to: string; t0: number; t1: number; style?: 'chest' | 'bounce' | 'overhead'; side?: number}
  | {type: 'shot'; player: string; t0: number; t1: number; make?: boolean}
  | {type: 'layup'; player: string; t0: number; t1: number; make?: boolean};

export type Screen = {
  /** the screeners that close the gap */
  screeners: [string, string];
  /** the cutter that goes through the gap */
  cutter: string;
  /** the defender the screen is meant for */
  target: string;
  /** y of the screen line (metres) */
  lineY: number;
  closeFrom: number;
  closeTo: number;
};

export type Play = {
  id: string;
  title: string;
  duration: number;
  players: PlayerSpec[];
  tracks: Record<string, Waypoint[]>;
  ball: BallEvent[];
  screens?: Screen[];
  /** named moments in play-seconds, used by the edit ("doorsClosed", "catch", ...) */
  marks: Record<string, number>;
  notes?: string[];
};

type Run = {t: number[]; x: number[][]; m: number[][]}; // knots, values per axis, second derivatives per axis

const runCache = new WeakMap<Waypoint[], Run[]>();

/** Clamped cubic spline (C2: smooth speed AND acceleration) through each moving run of waypoints.
 *  A run starts and ends at rest; equal consecutive waypoints are a stop that splits runs. */
const clamped = (t: number[], y: number[]): number[] => {
  const n = t.length;
  if (n < 2) return [0];
  const h = t.slice(1).map((v, i) => v - t[i]);
  // tridiagonal system for second derivatives M with y'(t0) = y'(tn) = 0
  const a = new Array(n).fill(0);
  const b = new Array(n).fill(0);
  const c = new Array(n).fill(0);
  const d = new Array(n).fill(0);
  b[0] = 2 * h[0];
  c[0] = h[0];
  d[0] = 6 * ((y[1] - y[0]) / h[0]);
  for (let i = 1; i < n - 1; i++) {
    a[i] = h[i - 1];
    b[i] = 2 * (h[i - 1] + h[i]);
    c[i] = h[i];
    d[i] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1]);
  }
  a[n - 1] = h[n - 2];
  b[n - 1] = 2 * h[n - 2];
  d[n - 1] = 6 * (0 - (y[n - 1] - y[n - 2]) / h[n - 2]);
  for (let i = 1; i < n; i++) {
    const w = a[i] / b[i - 1];
    b[i] -= w * c[i - 1];
    d[i] -= w * d[i - 1];
  }
  const M = new Array(n).fill(0);
  M[n - 1] = d[n - 1] / b[n - 1];
  for (let i = n - 2; i >= 0; i--) M[i] = (d[i] - c[i] * M[i + 1]) / b[i];
  return M;
};

const runs = (wp: Waypoint[]): Run[] => {
  const hit = runCache.get(wp);
  if (hit) return hit;
  const out: Run[] = [];
  let cur: Waypoint[] = [wp[0]];
  const same = (p: Waypoint, q: Waypoint) => Math.abs(p[1] - q[1]) < 1e-6 && Math.abs(p[2] - q[2]) < 1e-6;
  const flush = () => {
    if (cur.length < 2) return;
    const t = cur.map((w) => w[0]);
    const x = [cur.map((w) => w[1]), cur.map((w) => w[2])];
    out.push({t, x, m: x.map((col) => clamped(t, col))});
  };
  for (let i = 1; i < wp.length; i++) {
    if (same(wp[i], wp[i - 1])) {
      flush();
      cur = [wp[i]];
    } else cur.push(wp[i]);
  }
  flush();
  runCache.set(wp, out);
  return out;
};

export const posAt = (wp: Waypoint[], t: number): V2 => {
  if (t <= wp[0][0]) return [wp[0][1], wp[0][2]];
  const last = wp[wp.length - 1];
  if (t >= last[0]) return [last[1], last[2]];
  const r = runs(wp).find((g) => t >= g.t[0] && t <= g.t[g.t.length - 1]);
  if (!r) {
    // standing still between runs
    const prev = [...wp].reverse().find((w) => w[0] <= t)!;
    return [prev[1], prev[2]];
  }
  let i = 0;
  while (i < r.t.length - 2 && t > r.t[i + 1]) i++;
  const h = r.t[i + 1] - r.t[i];
  const A = (r.t[i + 1] - t) / h;
  const B = (t - r.t[i]) / h;
  const ev = (k: number) => {
    const y = r.x[k];
    const M = r.m[k];
    return A * y[i] + B * y[i + 1] + ((A * A * A - A) * M[i] + (B * B * B - B) * M[i + 1]) * (h * h) / 6;
  };
  return [ev(0), ev(1)];
};

export const velAt = (wp: Waypoint[], t: number, dt = 1 / 120): V2 => {
  const a = posAt(wp, t - dt);
  const b = posAt(wp, t + dt);
  return [(b[0] - a[0]) / (2 * dt), (b[1] - a[1]) / (2 * dt)];
};

/** distance run since t=0 (drives the stride animation) */
export const distAt = (wp: Waypoint[], t: number): number => {
  let d = 0;
  let prev = posAt(wp, wp[0][0]);
  const step = 1 / 30;
  for (let x = wp[0][0] + step; x <= t; x += step) {
    const p = posAt(wp, x);
    d += Math.hypot(p[0] - prev[0], p[1] - prev[1]);
    prev = p;
  }
  return d;
};

export type PlayerState = {spec: PlayerSpec; pos: V2; vel: V2; speed: number; facing: number; stride: number};

export type BallState = {pos: V3; holder?: string; inFlight?: 'pass' | 'shot' | 'layup'; event?: BallEvent; progress?: number};

export type Frame = {t: number; players: Record<string, PlayerState>; ball: BallState};

const hand = (p: PlayerState, side = 1): V3 => {
  const a = p.facing;
  const fx = Math.cos(a);
  const fy = Math.sin(a);
  // ball held in front and slightly to the side of the body
  return [p.pos[0] + fx * 0.32 - fy * 0.18 * side, p.pos[1] + fy * 0.32 + fx * 0.18 * side, 1.15];
};

const release = (p: PlayerState, type: 'shot' | 'layup'): V3 => [p.pos[0] + Math.cos(p.facing) * 0.2, p.pos[1] + Math.sin(p.facing) * 0.2, type === 'shot' ? 2.6 : 2.5];

const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];

const ballAt = (play: Play, t: number, ps: Record<string, PlayerState>): BallState => {
  const ev = play.ball;
  const cur = ev.find((e) => (e.type === 'hold' ? t >= e.from && t <= e.to : t >= e.t0 && t <= e.t1));
  if (cur) {
    if (cur.type === 'hold') {
      const h = hand(ps[cur.player]);
      // gather: the ball rises into the shooting pocket before a shot or layup
      const next = play.ball.find((e): e is Extract<BallEvent, {type: 'shot' | 'layup'}> => (e.type === 'shot' || e.type === 'layup') && e.player === cur.player && Math.abs(e.t0 - cur.to) < 1e-6);
      if (next && t > cur.to - 0.3) {
        const g = Math.min(1, (t - (cur.to - 0.3)) / 0.3);
        const e = g * g * (3 - 2 * g);
        const r = release(ps[cur.player], next.type);
        return {pos: [h[0] + (r[0] - h[0]) * e, h[1] + (r[1] - h[1]) * e, h[2] + (r[2] - h[2]) * e], holder: cur.player, event: cur};
      }
      if (cur.dribble) {
        const ph = Math.abs(Math.sin(Math.PI * 2.1 * (t - cur.from)));
        return {pos: [h[0], h[1], 0.12 + ph * 0.95], holder: cur.player, event: cur};
      }
      return {pos: h, holder: cur.player, event: cur};
    }
    const u = (t - cur.t0) / (cur.t1 - cur.t0);
    if (cur.type === 'pass') {
      const a = hand(ps[cur.from]);
      // the passer's release follows him at t0, the catch point follows the receiver at t1
      const a0 = hand(stateOf(play, cur.from, cur.t0));
      const b1 = hand(stateOf(play, cur.to, cur.t1));
      void a;
      const x = a0[0] + (b1[0] - a0[0]) * u;
      const y = a0[1] + (b1[1] - a0[1]) * u;
      let z: number;
      if (cur.style === 'bounce') {
        // straight down to a bounce at 62 % of the way, then up into the hands
        const k = 0.62;
        z = u < k ? a0[2] * (1 - u / k) ** 1.15 + 0.12 * (u / k) : 0.12 + (b1[2] - 0.12) * Math.sin(((u - k) / (1 - k)) * Math.PI * 0.5);
      } else if (cur.style === 'overhead') {
        z = 2.1 + (b1[2] - 2.1) * u + 0.6 * Math.sin(Math.PI * u);
      } else {
        z = a0[2] + (b1[2] - a0[2]) * u + 0.35 * Math.sin(Math.PI * u);
      }
      return {pos: [x, y, z], inFlight: 'pass', event: cur, progress: u};
    }
    // shot or layup: release above the head, parabola into the rim
    const r0 = release(stateOf(play, cur.player, cur.t0), cur.type);
    const apex = cur.type === 'shot' ? 4.75 : 3.45;
    const x = r0[0] + (RIM[0] - r0[0]) * u;
    const y = r0[1] + (RIM[1] - r0[1]) * u;
    // quadratic through r0 (u=0), apex-ish (u~0.55), rim (u=1)
    const zLin = r0[2] + (RIM[2] + 0.05 - r0[2]) * u;
    const bump = (apex - (r0[2] + RIM[2]) / 2) * 4 * u * (1 - u);
    return {pos: [x, y, zLin + bump], inFlight: cur.type, event: cur, progress: u};
  }
  // between events: after a made basket the ball drops through the net and bounces under it
  const done = [...ev].reverse().find((e) => (e.type === 'hold' ? e.to : e.t1) <= t);
  if (done && (done.type === 'shot' || done.type === 'layup')) {
    const dt = t - done.t1;
    const fall = Math.max(0, RIM[2] - 0.5 * 9.8 * dt * dt);
    if (fall > 0.12) return {pos: [RIM[0], RIM[1] + 0.05, fall], event: done};
    const tb = Math.sqrt((2 * (RIM[2] - 0.12)) / 9.8);
    const after = dt - tb;
    const bounce = 0.12 + Math.max(0, 1.6 * Math.abs(Math.sin(after * 3.2)) * Math.exp(-after * 2.2));
    return {pos: [RIM[0], RIM[1] + 0.05 + after * 0.4, bounce], event: done};
  }
  if (done && done.type === 'hold') return {pos: hand(ps[done.player]), holder: done.player};
  if (done && done.type === 'pass') return {pos: hand(ps[done.to]), holder: done.to};
  const first = ev[0];
  const holder = first.type === 'hold' ? first.player : first.type === 'pass' ? first.from : first.player;
  return {pos: hand(ps[holder]), holder};
};

const stateCache = new Map<string, PlayerState>();

export const stateOf = (play: Play, id: string, t: number): PlayerState => {
  const key = `${play.id}|${id}|${t.toFixed(4)}`;
  const hit = stateCache.get(key);
  if (hit) return hit;
  const spec = play.players.find((p) => p.id === id)!;
  const wp = play.tracks[id];
  const pos = posAt(wp, t);
  const vel = velAt(wp, t);
  const speed = Math.hypot(vel[0], vel[1]);
  // facing: direction of travel when moving, otherwise toward the ball holder (offence) or the man guarded
  let facing: number;
  const look = (q: V2) => Math.atan2(q[1] - pos[1], q[0] - pos[0]);
  const rest = spec.team === 'X' && spec.guards ? look(posAt(play.tracks[spec.guards], t)) : look(spec.team === 'O' ? (ballHolderPos(play, t) ?? FIBA.basket) : FIBA.basket);
  if (speed > 0.6) {
    const mv = Math.atan2(vel[1], vel[0]);
    const w = Math.min(1, (speed - 0.6) / 1.4);
    facing = blendAngle(rest, mv, w);
  } else facing = rest;
  const st: PlayerState = {spec, pos, vel, speed, facing, stride: distAt(wp, t)};
  if (stateCache.size > 20000) stateCache.clear();
  stateCache.set(key, st);
  return st;
};

const ballHolderPos = (play: Play, t: number): V2 | undefined => {
  const e = play.ball.find((x) => x.type === 'hold' && t >= x.from && t <= x.to) as Extract<BallEvent, {type: 'hold'}> | undefined;
  return e ? posAt(play.tracks[e.player], t) : undefined;
};

export const blendAngle = (a: number, b: number, w: number) => {
  let d = b - a;
  while (d > Math.PI) d -= 2 * Math.PI;
  while (d < -Math.PI) d += 2 * Math.PI;
  return a + d * w;
};

export const sample = (play: Play, t: number): Frame => {
  const tt = Math.max(0, Math.min(play.duration, t));
  const players: Record<string, PlayerState> = {};
  play.players.forEach((p) => (players[p.id] = stateOf(play, p.id, tt)));
  return {t: tt, players, ball: ballAt(play, tt, players)};
};

/** route of a player between two play times, as floor points (for animated arrows) */
export const routeOf = (play: Play, id: string, t0: number, t1: number, step = 1 / 20): V2[] => {
  const out: V2[] = [];
  for (let t = t0; t < t1; t += step) out.push(posAt(play.tracks[id], t));
  out.push(posAt(play.tracks[id], t1));
  return out;
};

export const mark = (play: Play, m: string | number): number => {
  if (typeof m === 'number') return m;
  const v = play.marks[m];
  if (v === undefined) throw new Error(`play ${play.id}: unknown mark "${m}"`);
  return v;
};
