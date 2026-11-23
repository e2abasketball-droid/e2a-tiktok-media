// E2A Football — the three cameras. Every camera is an orbit around a focus point that follows players
// and/or the ball (smoothed over a short play-time window so it never jitters):
//   TACTICAL OVERVIEW: high (45-70 deg), wide, behind the attack: the whole structure is readable.
//   DYNAMIC TRACKING:  medium height (12-25 deg), 14-22 m away, follows the ball or the runner.
//   DETAIL / REVEAL:   low (4-10 deg), close, long lens: the defender's head turn, the run nobody sees.
// Keys interpolate distance, elevation, azimuth and lens with ease in/out; the focus blends too.
import * as THREE from 'three';
import {W3} from './athlete';
import type {FBPlay, V2, V3} from './play';
import {ballAt, playerAt, smooth} from './play';

export type FocusItem = {player?: string; ball?: boolean; p?: V2; w?: number};
export type CamMode = 'overview' | 'tracking' | 'detail';
export type CamKey = {at: number; mode: CamMode; focus: FocusItem[]; dist: number; elev: number; azim: number; fov: number; z?: number; shake?: number; lift?: number; spline?: boolean};
// spline (set on the first key, V03+): the whole shot is ONE continuous move: every parameter follows a
// Catmull-Rom curve through the keys (continuous velocity), eased only at the first and last key, so a
// wide-to-close approach never stops at the intermediate keys.
// lift (m): the camera aims this far in front of the focus, towards itself, so the focus sits higher in the
// vertical frame (clear of the subtitles) without changing the angle. Default 0 (older episodes unchanged).
export type Cam = {pos: V3; target: V3; fov: number; mode: CamMode};

const focusAt = (play: FBPlay, f: FocusItem[], pt: number): V2 => {
  let x = 0;
  let y = 0;
  let w = 0;
  // smoothing window: 7 samples over [pt-0.35, pt+0.1] (a camera operator anticipates a little)
  for (let k = 0; k < 7; k++) {
    const t = Math.max(0, Math.min(play.duration, pt - 0.35 + (0.45 * k) / 6));
    for (const it of f) {
      const wi = it.w ?? 1;
      const p = it.p ?? (it.ball ? (ballAt(play, t).pos.slice(0, 2) as V2) : playerAt(play, it.player!, t).pos);
      x += p[0] * wi;
      y += p[1] * wi;
      w += wi;
    }
  }
  return [x / w, y / w];
};

const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
const lerpAng = (a: number, b: number, u: number) => {
  let d = b - a;
  while (d > 180) d -= 360;
  while (d < -180) d += 360;
  return a + d * u;
};

const cr = (ts: number[], vs: number[], t: number) => {
  // Catmull-Rom in time (non-uniform), zero tangent at the ends
  const n = ts.length;
  if (t <= ts[0]) return vs[0];
  if (t >= ts[n - 1]) return vs[n - 1];
  let i = 0;
  while (i < n - 2 && t > ts[i + 1]) i++;
  const tan = (k: number) => (k === 0 || k === n - 1 ? 0 : (vs[k + 1] - vs[k - 1]) / (ts[k + 1] - ts[k - 1]));
  const h = ts[i + 1] - ts[i];
  const u = (t - ts[i]) / h;
  const u2 = u * u;
  const u3 = u2 * u;
  return (2 * u3 - 3 * u2 + 1) * vs[i] + (u3 - 2 * u2 + u) * h * tan(i) + (-2 * u3 + 3 * u2) * vs[i + 1] + (u3 - u2) * h * tan(i + 1);
};

const camSpline = (play: FBPlay, keys: CamKey[], lt: number, pt: number): Cam => {
  const ts = keys.map((k) => k.at);
  const unwrap: number[] = [];
  for (const k of keys) {
    let a = k.azim;
    if (unwrap.length) {
      const prev = unwrap[unwrap.length - 1];
      while (a - prev > 180) a -= 360;
      while (a - prev < -180) a += 360;
    }
    unwrap.push(a);
  }
  const f = keys.map((k) => focusAt(play, k.focus, pt));
  const P = (vs: number[]) => cr(ts, vs, lt);
  const az = (P(unwrap) * Math.PI) / 180;
  const el = (P(keys.map((k) => k.elev)) * Math.PI) / 180;
  const dist = P(keys.map((k) => k.dist));
  const lift = P(keys.map((k) => k.lift ?? 0));
  const tz = P(keys.map((k) => k.z ?? 0.9));
  const fx = P(f.map((q) => q[0]));
  const fy = P(f.map((q) => q[1]));
  const target: V3 = [fx - Math.cos(az) * lift, fy - Math.sin(az) * lift, tz];
  const pos: V3 = [target[0] - Math.cos(az) * Math.cos(el) * dist, target[1] - Math.sin(az) * Math.cos(el) * dist, target[2] + Math.sin(el) * dist];
  let i = 0;
  while (i < keys.length - 1 && lt >= keys[i + 1].at) i++;
  return {pos, target, fov: P(keys.map((k) => k.fov)), mode: keys[i].mode};
};

export const camAt = (play: FBPlay, keys: CamKey[], lt: number, pt: number): Cam => {
  if (keys[0].spline && keys.length > 2) return camSpline(play, keys, lt, pt);
  let i = 0;
  while (i < keys.length - 1 && lt >= keys[i + 1].at) i++;
  const a = keys[i];
  const b = keys[Math.min(keys.length - 1, i + 1)];
  const u = b === a || b.at <= a.at ? 0 : smooth((lt - a.at) / (b.at - a.at));
  const fa = focusAt(play, a.focus, pt);
  const fb = b === a ? fa : focusAt(play, b.focus, pt);
  const tz = lerp(a.z ?? 0.9, b.z ?? 0.9, u);
  const dist = lerp(a.dist, b.dist, u);
  const el = (lerp(a.elev, b.elev, u) * Math.PI) / 180;
  const shake = lerp(a.shake ?? 0, b.shake ?? 0, u);
  const az = ((lerpAng(a.azim, b.azim, u) + shake * (Math.sin(lt * 1.7) * 0.6 + Math.sin(lt * 3.1 + 1) * 0.4)) * Math.PI) / 180;
  const lift = lerp(a.lift ?? 0, b.lift ?? 0, u);
  const target: V3 = [lerp(fa[0], fb[0], u) - Math.cos(az) * lift, lerp(fa[1], fb[1], u) - Math.sin(az) * lift, tz];
  const pos: V3 = [target[0] - Math.cos(az) * Math.cos(el) * dist, target[1] - Math.sin(az) * Math.cos(el) * dist, target[2] + Math.sin(el) * dist + shake * 0.05 * Math.sin(lt * 2.3)];
  return {pos, target, fov: lerp(a.fov, b.fov, u), mode: u < 0.5 ? a.mode : b.mode};
};

/** project a pitch point to composition pixels with the same camera the scene uses */
export const projector = (cam: Cam, W: number, H: number) => {
  const c = new THREE.PerspectiveCamera(cam.fov, W / H, 0.1, 400);
  c.position.set(...W3(cam.pos));
  c.up.set(0, 1, 0);
  c.lookAt(new THREE.Vector3(...W3(cam.target)));
  c.updateMatrixWorld();
  c.updateProjectionMatrix();
  return (p: V3) => {
    const v = new THREE.Vector3(...W3(p)).project(c);
    return {x: ((v.x + 1) / 2) * W, y: ((1 - v.y) / 2) * H, visible: v.z < 1 && v.z > -1 && Math.abs(v.x) < 1.1 && Math.abs(v.y) < 1.1};
  };
};
