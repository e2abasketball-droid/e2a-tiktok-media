// E2A 3D engine — TacticalTrackingCamera / CinematicCameraTransition.
// Every camera is expressed as an ORBIT (target, distance, pitch from straight down, yaw, fov) so
// that any two cameras — a defender POV at eye level and a top-down tactical view — can be blended
// continuously (no spatial jumps, the court never flips). Rigs can follow players; following uses a
// time-window average of the play so the camera has weight instead of shaking with every step.
import type {V3} from '../tactical/geometry.ts';
import type {Play} from '../tactical/play.ts';
import {posAt} from '../tactical/play.ts';

export type Cam3 = {pos: V3; target: V3; up: V3; fov: number; roll?: number};
export type Orbit = {target: V3; dist: number; pitch: number; yaw: number; fov: number; roll?: number};

const rad = (d: number) => (d * Math.PI) / 180;
const deg = (r: number) => (r * 180) / Math.PI;

/** yaw 0 = camera on the half-court side looking toward the basket (basket at the top of the screen) */
const back = (yaw: number): [number, number] => [-Math.sin(rad(yaw)), Math.cos(rad(yaw))];

export const toCam = (o: Orbit): Cam3 => {
  const p = rad(o.pitch);
  const [bx, by] = back(o.yaw);
  const pos: V3 = [o.target[0] + o.dist * Math.sin(p) * bx, o.target[1] + o.dist * Math.sin(p) * by, o.target[2] + o.dist * Math.cos(p)];
  const up: V3 = [-Math.cos(p) * bx, -Math.cos(p) * by, Math.sin(p)];
  return {pos, target: o.target, up, fov: o.fov, roll: o.roll};
};

export const fromPosTarget = (pos: V3, target: V3, fov: number, roll = 0): Orbit => {
  const d: V3 = [pos[0] - target[0], pos[1] - target[1], pos[2] - target[2]];
  const dist = Math.hypot(d[0], d[1], d[2]);
  const pitch = deg(Math.acos(Math.max(-1, Math.min(1, d[2] / dist))));
  const yaw = deg(Math.atan2(-d[0], d[1]));
  return {target, dist, pitch, yaw, fov, roll};
};

type Target = V3 | {follow: string | string[]; z?: number; lead?: number; window?: number; offset?: [number, number]};

export type Rig =
  | {type: 'orbit'; target: Target; dist: number; pitch: number; yaw: number; fov: number; roll?: number}
  /** eye-level camera behind a player (e.g. the chasing defender) looking at another player */
  | {type: 'pov'; behind: string; look: string | V3; back?: number; height?: number; side?: number; fov: number; lookZ?: number; window?: number};

export type CamKey3 = {at: number; rig: Rig; ease?: 'inOut' | 'out' | 'in' | 'linear' | 'hold'};

const smoothPos = (play: Play, id: string, t: number, w = 0.35): [number, number] => {
  // average over a window -> weight, no step jitter
  let x = 0;
  let y = 0;
  const n = 9;
  for (let i = 0; i < n; i++) {
    const tt = Math.max(0, Math.min(play.duration, t - w / 2 + (w * i) / (n - 1)));
    const p = posAt(play.tracks[id], tt);
    x += p[0];
    y += p[1];
  }
  return [x / n, y / n];
};

const resolveTarget = (play: Play, tg: Target, pt: number): V3 => {
  if (Array.isArray(tg)) return tg as V3;
  const ids = Array.isArray(tg.follow) ? tg.follow : [tg.follow];
  let x = 0;
  let y = 0;
  ids.forEach((id) => {
    const p = smoothPos(play, id, pt + (tg.lead ?? 0), tg.window ?? 0.35);
    x += p[0];
    y += p[1];
  });
  return [x / ids.length + (tg.offset?.[0] ?? 0), y / ids.length + (tg.offset?.[1] ?? 0), tg.z ?? 1.0];
};

export const rigOrbit = (play: Play, r: Rig, pt: number): Orbit => {
  if (r.type === 'orbit') return {target: resolveTarget(play, r.target, pt), dist: r.dist, pitch: r.pitch, yaw: r.yaw, fov: r.fov, roll: r.roll};
  const me = smoothPos(play, r.behind, pt, r.window ?? 0.3);
  const look: V3 = typeof r.look === 'string' ? [...smoothPos(play, r.look, pt, r.window ?? 0.3), r.lookZ ?? 1.25] as V3 : r.look;
  const dx = look[0] - me[0];
  const dy = look[1] - me[1];
  const L = Math.hypot(dx, dy) || 1;
  const f = [dx / L, dy / L];
  const s = [f[1], -f[0]];
  const b = r.back ?? 1.6;
  const pos: V3 = [me[0] - f[0] * b + s[0] * (r.side ?? 0.4), me[1] - f[1] * b + s[1] * (r.side ?? 0.4), r.height ?? 1.75];
  return fromPosTarget(pos, look, r.fov);
};

const EASE = {
  linear: (x: number) => x,
  inOut: (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  out: (x: number) => 1 - Math.pow(1 - x, 3),
  in: (x: number) => x * x * x,
  hold: () => 0,
};

const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
const lerpAngle = (a: number, b: number, u: number) => {
  let d = b - a;
  while (d > 180) d -= 360;
  while (d < -180) d += 360;
  return a + d * u;
};

export const blendOrbit = (a: Orbit, b: Orbit, u: number): Orbit => ({
  target: [lerp(a.target[0], b.target[0], u), lerp(a.target[1], b.target[1], u), lerp(a.target[2], b.target[2], u)],
  // distance blends in log space so dolly moves feel even
  dist: Math.exp(lerp(Math.log(a.dist), Math.log(b.dist), u)),
  pitch: lerp(a.pitch, b.pitch, u),
  yaw: lerpAngle(a.yaw, b.yaw, u),
  fov: lerp(a.fov, b.fov, u),
  roll: lerp(a.roll ?? 0, b.roll ?? 0, u),
});

/** camera at local time lt (keys already resolved to local seconds) for play time pt */
export const camera3At = (play: Play, keys: CamKey3[], lt: number, pt: number): Cam3 => {
  if (keys.length === 1 || lt <= keys[0].at) return toCam(rigOrbit(play, keys[0].rig, pt));
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i];
    const b = keys[i + 1];
    if (lt >= a.at && lt <= b.at) {
      const u = (lt - a.at) / Math.max(1e-6, b.at - a.at);
      const e = EASE[b.ease ?? 'inOut'](u);
      return toCam(blendOrbit(rigOrbit(play, a.rig, pt), rigOrbit(play, b.rig, pt), e));
    }
  }
  return toCam(rigOrbit(play, keys[keys.length - 1].rig, pt));
};
