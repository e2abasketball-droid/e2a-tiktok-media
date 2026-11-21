// E2A 3D engine — REALISM V2 apparel secondary motion (2026-11-21, opt-in play.realism >= 2).
// The jersey of the v2 player mesh (tools/blender/build_player.py --garment v2) hangs from the chest; its lower part
// (vertex attribute _E2A_HEM, 0 above the chest line -> 1 at the hem) reacts to the athlete with a LAG instead of being
// painted on the skin:
//   sway   damped spring (1.6 Hz, damping 0.32) driven by the pelvis acceleration (inertia: the hem stays behind when he
//          accelerates, swings forward when he brakes, outward in a cut) + air drag (back and slightly up with speed);
//   twist  the hem lags the trunk's turn (spring on the heading's angular acceleration, about the vertical pelvis axis);
//   lift   the hem floats up a little on the way down from a jump and settles on landing;
//   flutter a 6-lobe ripple round the hem synchronised with the stride phase (never free random noise), <= 5 mm.
// Pure function of (play, player, t): the spring is integrated from t - 1.2 s at 120 Hz from rest (the transient has
// decayed to < 0.1 %), so a frame rendered alone, out of order or slowed down gets the same cloth. No collision solver:
// the shader / QC never let the hem move INWARD more than 85 % of its ease (_E2A_EASE, the gap to the body measured at
// build time), so the swing cannot push the cloth into the skin. Same maths in GLSL (SkinnedAthlete) and here (QC).
import type {V3} from '../tactical/geometry.ts';
import {posAt} from '../tactical/play.ts';
import type {PlayWithActions} from './rig.ts';
import {bodyRowAt, jumpHeightAt} from './rig.ts';

export type Cloth = {sway: V3; twist: number; flutter: number; phase: number};
export const CLOTH2 = {hz: 1.6, zeta: 0.32, gain: 0.45, drag: 0.0009, lift: 0.0025, maxH: 0.05, maxUp: 0.04, maxDown: 0.02, maxTwist: 0.14, flutter: 0.005, easeUse: 0.85};
const cache = new Map<string, Cloth>();
const wrap = (a: number) => Math.atan2(Math.sin(a), Math.cos(a));

export const clothAt = (play: PlayWithActions, id: string, t: number): Cloth => {
  const key = `${play.id}|${id}|${t.toFixed(5)}`;
  const hit = cache.get(key);
  if (hit) return hit;
  const wp = play.tracks[id];
  const dt = 1 / 120, w = 2 * Math.PI * CLOTH2.hz, z = CLOTH2.zeta;
  const T0 = Math.max(0, t - 1.2);
  const n = Math.max(1, Math.round((t - T0) / dt));
  const P = (x: number) => posAt(wp, Math.max(0, Math.min(play.duration, x)));
  const Z = (x: number) => jumpHeightAt(play, id, x);
  const H = (x: number) => bodyRowAt(play, id, Math.max(0, Math.min(play.duration, x))).heading;
  // state: x, y (horizontal), zz (vertical), th (twist) and their speeds
  let x = 0, y = 0, zz = 0, th = 0, vx = 0, vy = 0, vz = 0, vth = 0;
  let v0: [number, number] | undefined;
  for (let k = 1; k <= n; k++) {
    const tk = T0 + k * dt;
    const a = P(tk - dt), b = P(tk), c = P(tk + dt);
    const ax = (c[0] - 2 * b[0] + a[0]) / (dt * dt), ay = (c[1] - 2 * b[1] + a[1]) / (dt * dt);
    const az = (Z(tk + dt) - 2 * Z(tk) + Z(tk - dt)) / (dt * dt);
    const hA = H(tk - dt), hB = H(tk), hC = H(tk + dt);
    const alpha = (wrap(hC - hB) - wrap(hB - hA)) / (dt * dt);
    const g = CLOTH2.gain;
    vx += (-w * w * x - 2 * z * w * vx - g * ax) * dt; x += vx * dt;
    vy += (-w * w * y - 2 * z * w * vy - g * ay) * dt; y += vy * dt;
    vz += (-w * w * zz - 2 * z * w * vz - g * Math.max(-30, Math.min(30, az))) * dt; zz += vz * dt;
    vth += (-w * w * th - 2 * z * w * vth - 0.5 * Math.max(-60, Math.min(60, alpha))) * dt; th += vth * dt;
    v0 = [(c[0] - a[0]) / (2 * dt), (c[1] - a[1]) / (2 * dt)];
  }
  const v = v0 ?? [0, 0];
  const sp = Math.hypot(v[0], v[1]);
  // drag: back along the run, a little up with speed
  let sx = x - CLOTH2.drag * v[0] * sp, sy = y - CLOTH2.drag * v[1] * sp;
  const hl = Math.hypot(sx, sy);
  if (hl > CLOTH2.maxH) {
    sx *= CLOTH2.maxH / hl;
    sy *= CLOTH2.maxH / hl;
  }
  const up = Math.max(-CLOTH2.maxDown, Math.min(CLOTH2.maxUp, zz + CLOTH2.lift * sp));
  const row = bodyRowAt(play, id, Math.max(0, Math.min(play.duration, t)));
  const out: Cloth = {sway: [sx, sy, up], twist: Math.max(-CLOTH2.maxTwist, Math.min(CLOTH2.maxTwist, th)), flutter: CLOTH2.flutter * Math.min(1, sp / 6), phase: row.phase};
  if (cache.size > 40000) cache.clear();
  cache.set(key, out);
  return out;
};

/** the cloth displacement of one garment vertex in PLAY space (the GLSL in SkinnedAthlete does the same):
 *  p, n = skinned position and normal, hem = _E2A_HEM, ease = _E2A_EASE, pelvis = pelvis point (play space) */
export const clothDisplace = (p: V3, n: V3, hem: number, ease: number, c: Cloth, pelvis: V3): V3 => {
  if (hem <= 0) return p;
  const rx = p[0] - pelvis[0], ry = p[1] - pelvis[1];
  // twist about the vertical axis through the pelvis
  const a = c.twist * hem, ca = Math.cos(a), sa = Math.sin(a);
  let dx = rx * ca - ry * sa - rx, dy = rx * sa + ry * ca - ry;
  dx += c.sway[0] * hem;
  dy += c.sway[1] * hem;
  let dz = c.sway[2] * hem;
  // flutter: 6 lobes round the trunk, travelling with the stride phase, along the normal
  const ang = Math.atan2(ry, rx);
  const fl = c.flutter * hem * Math.sin(6 * ang + 2 * Math.PI * c.phase);
  dx += n[0] * fl;
  dy += n[1] * fl;
  dz += n[2] * fl;
  // never more than 85 % of the ease INTO the body (horizontal normal)
  const nh = Math.hypot(n[0], n[1]);
  if (nh > 1e-6) {
    const hx = n[0] / nh, hy = n[1] / nh;
    const inward = -(dx * hx + dy * hy);
    const lim = CLOTH2.easeUse * ease;
    if (inward > lim) {
      dx += hx * (inward - lim);
      dy += hy * (inward - lim);
    }
  }
  return [p[0] + dx, p[1] + dy, p[2] + dz];
};
