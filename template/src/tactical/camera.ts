// E2A Tactical engine — TacticalCamera: named presets, player-following modes and smooth moves.
// A camera key is either a fixed state, a preset name, or a dynamic mode resolved every frame:
//   {mode:'follow', player:'O2', pitch, yaw, dist}  — keeps a player (or the ball) framed
//   {mode:'pov', player:'X2', look:'O2'}            — eye-level view from behind a player
import type {CameraState, V3} from './geometry.ts';
import type {Frame} from './play.ts';

export type CamSpec =
  | string
  | (Partial<CameraState> & {preset?: string})
  | {mode: 'follow'; player: string; pitch?: number; yaw?: number; dist?: number; fov?: number; shiftY?: number; z?: number; lead?: number}
  | {mode: 'pov'; player: string; look: string; height?: number; back?: number; fov?: number; side?: number; lookZ?: number; at?: number};

export type CamKey = {at: number; cam: CamSpec; ease?: 'inOut' | 'out' | 'in' | 'linear'};

// Top-down framing of the whole half court above the subtitles (court width ~1000 px).
export const PRESETS: Record<string, CameraState> = {
  top: {target: [0, 7.0, 0], dist: 41, pitch: 0, yaw: 0, fov: 40, shiftY: -150},
  topTight: {target: [0, 6.2, 0], dist: 30, pitch: 0, yaw: 0, fov: 40, shiftY: -150},
  broadcast: {target: [0.4, 6.6, 0.8], dist: 15.5, pitch: 60, yaw: 0, fov: 42, shiftY: -150},
  broadcastHigh: {target: [0, 6.0, 0], dist: 25, pitch: 38, yaw: 0, fov: 40, shiftY: -160},
  gapClose: {target: [0, 6.3, 0.7], dist: 13, pitch: 52, yaw: 28, fov: 40, shiftY: -170},
  gapTop: {target: [0, 5.6, 0], dist: 22, pitch: 10, yaw: 0, fov: 40, shiftY: -170},
  reverse: {target: [0.6, 4.2, 0.6], dist: 15, pitch: 60, yaw: 180, fov: 42, shiftY: -170},
  split: {target: [0, 5.4, 0.4], dist: 22.5, pitch: 44, yaw: 0, fov: 40, shiftY: -60},
};

const BASE: CameraState = PRESETS.top;

const smoothPos = (frameAt: (t: number) => Frame, t: number, id: string): V3 => {
  // average over a short window so the camera never jitters with the player's steps
  let x = 0;
  let y = 0;
  let z = 0;
  const n = 7;
  for (let i = 0; i < n; i++) {
    const f = frameAt(t + (i - (n - 1) / 2) * 0.05);
    if (id === 'ball') {
      x += f.ball.pos[0];
      y += f.ball.pos[1];
      z += f.ball.pos[2];
    } else {
      x += f.players[id].pos[0];
      y += f.players[id].pos[1];
    }
  }
  return [x / n, y / n, z / n];
};

/** Resolve one key to a concrete camera state at play time t. */
export const resolveCam = (spec: CamSpec, frameAt: (t: number) => Frame, t: number): CameraState => {
  if (typeof spec === 'string') {
    const p = PRESETS[spec];
    if (!p) throw new Error(`unknown camera preset ${spec}`);
    return p;
  }
  if ('mode' in spec && spec.mode === 'follow') {
    const p = smoothPos(frameAt, t, spec.player);
    const lead = spec.lead ?? 0;
    return {target: [p[0], p[1] + lead, spec.z ?? (spec.player === 'ball' ? p[2] * 0.6 : 0.8)], dist: spec.dist ?? 14, pitch: spec.pitch ?? 50, yaw: spec.yaw ?? 0, fov: spec.fov ?? 40, shiftY: spec.shiftY ?? -170};
  }
  if ('mode' in spec && spec.mode === 'pov') {
    if (spec.at !== undefined) t = spec.at; // frozen point of view (e.g. while the play rewinds)
    const me = smoothPos(frameAt, t, spec.player);
    const them = smoothPos(frameAt, t, spec.look);
    const dx = them[0] - me[0];
    const dy = them[1] - me[1];
    const d = Math.max(0.5, Math.hypot(dx, dy));
    const ux = dx / d;
    const uy = dy / d;
    const back = spec.back ?? 0.9;
    const side = spec.side ?? 0;
    const eye: V3 = [me[0] - ux * back - uy * side, me[1] - uy * back + ux * side, spec.height ?? 1.75];
    const look: V3 = [them[0], them[1], spec.lookZ ?? 1.0];
    const fx = look[0] - eye[0];
    const fy = look[1] - eye[1];
    const fz = look[2] - eye[2];
    const L = Math.hypot(fx, fy, fz);
    return {target: look, dist: L, pitch: (Math.acos(-fz / L) * 180) / Math.PI, yaw: (Math.atan2(fx, fy) * 180) / Math.PI, fov: spec.fov ?? 62, shiftY: 0};
  }
  const s = spec as Partial<CameraState> & {preset?: string};
  return {...(s.preset ? PRESETS[s.preset] : BASE), ...s} as CameraState;
};

const EASE = {
  linear: (x: number) => x,
  inOut: (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  out: (x: number) => 1 - Math.pow(1 - x, 3),
  in: (x: number) => x * x * x,
};

const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
const lerpAngle = (a: number, b: number, u: number) => {
  let d = b - a;
  while (d > 180) d -= 360;
  while (d < -180) d += 360;
  return a + d * u;
};

export const blendCam = (a: CameraState, b: CameraState, u: number): CameraState => ({
  target: [lerp(a.target[0], b.target[0], u), lerp(a.target[1], b.target[1], u), lerp(a.target[2], b.target[2], u)],
  dist: Math.exp(lerp(Math.log(a.dist), Math.log(b.dist), u)),
  pitch: lerp(a.pitch, b.pitch, u),
  yaw: lerpAngle(a.yaw, b.yaw, u),
  fov: lerp(a.fov, b.fov, u),
  shiftY: lerp(a.shiftY ?? 0, b.shiftY ?? 0, u),
  roll: lerp(a.roll ?? 0, b.roll ?? 0, u),
});

/** Camera at local time `lt` (seconds in the shot) for play time `pt`. Keys move with ease in/out. */
export const cameraAt = (keys: CamKey[], lt: number, pt: number, frameAt: (t: number) => Frame): CameraState => {
  if (!keys.length) return BASE;
  const ks = [...keys].sort((a, b) => a.at - b.at);
  if (lt <= ks[0].at) return resolveCam(ks[0].cam, frameAt, pt);
  for (let i = 0; i < ks.length - 1; i++) {
    const a = ks[i];
    const b = ks[i + 1];
    if (lt >= a.at && lt <= b.at) {
      const u = EASE[b.ease ?? 'inOut']((lt - a.at) / Math.max(1e-6, b.at - a.at));
      return blendCam(resolveCam(a.cam, frameAt, pt), resolveCam(b.cam, frameAt, pt), u);
    }
  }
  return resolveCam(ks[ks.length - 1].cam, frameAt, pt);
};
