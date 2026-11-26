// E2A body cues (2026-11-26, Zero Cut TEST "aggressive hook" brief). Two opt-in ov3 types that read the RENDERED V3.3
// body (motionV33), so they sit on the leg / hips that are drawn, not on the track. Pure functions of (play, play time
// pt, age): freezes, slow motion and rewinds carry them like every other overlay.
//   legLoad   {player, leg: 'L' | 'R' | 'auto', color?, blinks?, period?, width?}
//             the LOADED leg highlighted: a translucent tube hip -> knee -> ankle -> toe drawn over the body (no depth
//             test, so the far leg of a defender facing away is still readable) + a floor ring under that foot.
//             It blinks `blinks` times (default 3, `period` 0.36 s: short, tactical) and then holds steady.
//             'auto' = the foot with the larger compiled support at that instant (the leg the weight is on).
//   pivotArc  {player, t0, t1, color?, r?, draw?, fake?}
//             the change of direction around the hips: a ghost arrow along the direction of travel at play time t0
//             (the fake: body angle into the handoff), a gold arc sweeping round the pelvis to the direction of
//             travel at t1 (the real cut angle), gold arrowhead on the new direction. Centred on the live pelvis,
//             at hip height. The sweep draws in `draw` s (default 0.45) and then holds.
import React from 'react';
import * as THREE from 'three';
import type {V3} from '../tactical/geometry.ts';
import type {Play} from '../tactical/play.ts';
import {W3} from './Athlete';
import {PLAYER3D_V32} from './realism-v3-2/index.ts';
import {motionV33} from './realism-v3-3/motion33.ts';

export type CueOv =
  | {type: 'legLoad'; player: string; leg?: 'L' | 'R' | 'auto'; color?: string; blinks?: number; period?: number; width?: number}
  | {type: 'pivotArc'; player: string; t0: number; t1: number; color?: string; r?: number; draw?: number; fake?: string};

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const top = (color: string, opacity: number, add = false) =>
  new THREE.MeshBasicMaterial({color, transparent: true, opacity, depthWrite: false, depthTest: false, toneMapped: false, side: THREE.DoubleSide,
    ...(add ? {blending: THREE.AdditiveBlending} : {})});
const rigOf = (play: Play, id: string) => PLAYER3D_V32[play.players.find((p) => p.id === id)?.team === 'X' ? 'def' : 'off'].rig;

/** blink envelope: n smooth flashes (0.28 -> 1) of `period` s, then steady 0.9 */
export const blinkAt = (age: number, n = 3, period = 0.36) => {
  if (age >= n * period) return 0.9;
  const ph = (age % period) / period;
  return 0.28 + 0.72 * Math.pow(Math.sin(Math.PI * ph), 0.6);
};

const tube = (pts: V3[], r: number) => {
  const curve = new THREE.CatmullRomCurve3(pts.map((p) => new THREE.Vector3(...W3(p))), false, 'centripetal');
  return new THREE.TubeGeometry(curve, 24, r, 10, false);
};

/** horizontal ribbon along an arc (centre c, radius r, angles a0 -> a1) at height z */
const arcRibbon = (c: V3, r: number, a0: number, a1: number, w: number) => {
  const N = 40;
  const pos: number[] = [];
  const idx: number[] = [];
  for (let k = 0; k <= N; k++) {
    const t = a0 + ((a1 - a0) * k) / N;
    for (const s of [-0.5, 0.5]) pos.push(...W3([c[0] + Math.cos(t) * (r + s * w), c[1] + Math.sin(t) * (r + s * w), c[2]]));
    if (k < N) idx.push(2 * k, 2 * k + 1, 2 * k + 2, 2 * k + 1, 2 * k + 3, 2 * k + 2);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
};
/** flat triangle (arrowhead) at p pointing along angle ang, horizontal at height p[2] */
const head = (p: V3, ang: number, s: number) => {
  const d = [Math.cos(ang), Math.sin(ang)], n = [-d[1], d[0]];
  const pts: V3[] = [[p[0] + d[0] * s, p[1] + d[1] * s, p[2]], [p[0] + n[0] * s * 0.6, p[1] + n[1] * s * 0.6, p[2]], [p[0] - n[0] * s * 0.6, p[1] - n[1] * s * 0.6, p[2]]];
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pts.flatMap((q) => W3(q)), 3));
  g.setIndex([0, 1, 2]);
  return g;
};
/** straight horizontal bar from a to b, width w (dashed: `dash` pieces) */
const bar = (a: V3, b: V3, w: number, dash = 0) => {
  const d = [b[0] - a[0], b[1] - a[1]];
  const L = Math.hypot(d[0], d[1]) || 1;
  const n = [(-d[1] / L) * w * 0.5, (d[0] / L) * w * 0.5];
  const segs = dash ? Array.from({length: dash}, (_, k) => [k / dash, (k + 0.6) / dash]) : [[0, 1]];
  const pos: number[] = [];
  const idx: number[] = [];
  segs.forEach(([u0, u1], k) => {
    const p0 = [a[0] + d[0] * u0, a[1] + d[1] * u0], p1 = [a[0] + d[0] * u1, a[1] + d[1] * u1];
    for (const p of [p0, p1]) for (const s of [-1, 1]) pos.push(...W3([p[0] + n[0] * s, p[1] + n[1] * s, a[2]]));
    const o = k * 4;
    idx.push(o, o + 1, o + 2, o + 1, o + 3, o + 2);
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
};

/** direction of travel (radians) of a player's pelvis at play time t (V3.3 body, 0.08 s window) */
export const travelDir = (play: Play, id: string, t: number) => {
  const rig = rigOf(play, id);
  const a = motionV33(play, id, Math.max(0, t - 0.04), rig), b = motionV33(play, id, Math.min(play.duration, t + 0.04), rig);
  if (!a || !b) return 0;
  return Math.atan2(b.body.pelvis[1] - a.body.pelvis[1], b.body.pelvis[0] - a.body.pelvis[0]);
};

export const Cues3D: React.FC<{play: Play; pt: number; o: CueOv & {age: number}; a: number}> = ({play, pt, o, a}) => {
  const t = clamp(pt, 0, play.duration);
  const m = motionV33(play, o.player, t, rigOf(play, o.player));
  if (!m) return null;
  switch (o.type) {
    case 'legLoad': {
      const i = o.leg === 'L' ? 0 : o.leg === 'R' ? 1 : m.body.feet[0].support >= m.body.feet[1].support ? 0 : 1;
      const P = m.pose;
      const col = o.color ?? '#E5483A';
      const k = blinkAt(o.age, o.blinks ?? 3, o.period ?? 0.36) * a;
      const w = o.width ?? 0.072;
      const pts: V3[] = [P.hip[i], P.knee[i], P.ankle[i], P.toe[i]];
      const f = P.toe[i], an = P.ankle[i];
      const c: V3 = [(f[0] + an[0]) / 2, (f[1] + an[1]) / 2, 0.012];
      return (
        <group>
          <mesh geometry={tube(pts, w * 1.9)} material={top(col, 0.22 * k, true)} renderOrder={20} />
          <mesh geometry={tube(pts, w)} material={top(col, 0.55 * k)} renderOrder={21} />
          <mesh position={W3(c)} rotation={[-Math.PI / 2, 0, 0]} scale={0.3} material={top(col, 0.95 * k)} renderOrder={19}>
            <ringGeometry args={[0.78, 1.0, 64]} />
          </mesh>
        </group>
      );
    }
    case 'pivotArc': {
      const A = travelDir(play, o.player, o.t0);
      let B = travelDir(play, o.player, o.t1);
      // shortest sweep from the fake angle to the real one
      while (B - A > Math.PI) B -= 2 * Math.PI;
      while (B - A < -Math.PI) B += 2 * Math.PI;
      const r = o.r ?? 0.78;
      const col = o.color ?? '#F2C76A';
      const pel = m.body.pelvis;
      const c: V3 = [pel[0], pel[1], Math.max(0.5, pel[2] - 0.05)];
      const u = eo(o.age / (o.draw ?? 0.45));
      const Bu = A + (B - A) * u;
      const ghostIn = eo(o.age / 0.18);
      const fakeCol = o.fake ?? '#FFFFFF';
      const tipA: V3 = [c[0] + Math.cos(A) * (r + 0.75), c[1] + Math.sin(A) * (r + 0.75), c[2]];
      const tipB: V3 = [c[0] + Math.cos(Bu) * (r + 0.85), c[1] + Math.sin(Bu) * (r + 0.85), c[2]];
      const onArc = (ang: number, rr = r): V3 => [c[0] + Math.cos(ang) * rr, c[1] + Math.sin(ang) * rr, c[2]];
      return (
        <group>
          {/* the fake: where the body was going (into the handoff) */}
          <mesh geometry={bar(onArc(A), tipA, 0.09, 5)} material={top(fakeCol, 0.92 * a * ghostIn)} renderOrder={20} />
          <mesh geometry={head(tipA, A, 0.24)} material={top(fakeCol, 0.92 * a * ghostIn)} renderOrder={20} />
          {/* the sweep round the hips */}
          {u > 0.02 && <mesh geometry={arcRibbon(c, r, A, Bu, 0.2)} material={top(col, 0.22 * a, true)} renderOrder={20} />}
          {u > 0.02 && <mesh geometry={arcRibbon(c, r, A, Bu, 0.1)} material={top(col, 0.97 * a)} renderOrder={21} />}
          {/* the real cut angle */}
          {u > 0.6 && <mesh geometry={bar(onArc(Bu), tipB, 0.12)} material={top(col, 0.97 * a * clamp((u - 0.6) / 0.25))} renderOrder={21} />}
          {u > 0.6 && <mesh geometry={head(tipB, Bu, 0.32)} material={top(col, 0.97 * a * clamp((u - 0.6) / 0.25))} renderOrder={21} />}
        </group>
      );
    }
    default:
      return null;
  }
};
