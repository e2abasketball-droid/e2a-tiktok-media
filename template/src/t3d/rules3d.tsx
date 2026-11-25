// E2A Rules overlays (2026-11-24, "4 Rules Every Player Must Know"). Opt-in ov3 types, pure functions of (play, play
// time, age) like every other overlay (seek = replay, freezes and rewinds carry them). They read the RENDERED V3.3
// bodies (motionV33 / ballV33), so a ring on a foot is on the foot that is drawn, not on the track.
//   footRing  {player, foot: 'L' | 'R', color?, r?}            ring + soft glow under the ball of one foot; the ring
//             rises with the sole (a lifted pivot foot visibly lifts its ring 0..1:1, capped 0.25 m)
//   ballRing  {color?, r?}                                       horizontal ring around the ball at the ball height
//   handRing  {player, hand: 0 | 1, color?}                      contact marker at the hand (illegal hold)
//   area2     {color?, opacity?}                                 the FIBA two-point field-goal area, filled (inside the
//             arc + the corner lanes down to the baseline). Stable: no opacity oscillation, depthTest on, no depthWrite
//   arc3      {color?, width?, draw?}                             the three-point line traced (corner + arc), static width
// 2026-11-25 (4 Rules Part 2), same rules:
//   paint      {color?, opacity?, edge?}                          the restricted area (4.90 x 5.80 m, lines included) softly
//              filled + its outline (offensive 3 seconds)
//   centerLine {color?, width?, draw?}                            the half-court line lit (full court: y = 14), drawn from the
//              centre out; the line itself belongs to the backcourt (FIBA)
//   rimLine    {color?, half?}                                    a thin horizontal line at ring height (3.05 m) through the
//              ring, so "above the ring" reads in a close shot (goaltending)
// Floor graphics follow the E2A Floor Graphics Stability Standard: one mesh per idea, constant geometry while active,
// fixed height (8-14 mm), polygonOffset, fade only by the shot's fin / fout.
import React from 'react';
import * as THREE from 'three';
import type {V3} from '../tactical/geometry.ts';
import {FIBA} from '../tactical/geometry.ts';
import type {Play} from '../tactical/play.ts';
import {W3} from './Athlete';
import {PLAYER3D_V32} from './realism-v3-2/index.ts';
import {ballV33, motionV33} from './realism-v3-3/motion33.ts';

export type RulesOv =
  | {type: 'footRing'; player: string; foot: 'L' | 'R'; color?: string; r?: number}
  | {type: 'ballRing'; color?: string; r?: number}
  | {type: 'handRing'; player: string; hand: 0 | 1; color?: string}
  | {type: 'area2'; color?: string; opacity?: number}
  | {type: 'arc3'; color?: string; width?: number; draw?: number}
  | {type: 'paint'; color?: string; opacity?: number; edge?: number}
  | {type: 'centerLine'; color?: string; width?: number; draw?: number}
  | {type: 'rimLine'; color?: string; half?: number};

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const mat = (color: string, opacity: number, add = false) =>
  new THREE.MeshBasicMaterial({color, transparent: true, opacity, depthWrite: false, toneMapped: false, side: THREE.DoubleSide,
    polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, ...(add ? {blending: THREE.AdditiveBlending} : {})});
const glowTex = (() => {
  let t: THREE.Texture | null = null;
  return () => {
    if (t) return t;
    const c = document.createElement('canvas');
    c.width = c.height = 128;
    const g = c.getContext('2d')!;
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.45, 'rgba(255,255,255,0.35)');
    gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr;
    g.fillRect(0, 0, 128, 128);
    t = new THREE.CanvasTexture(c);
    return t;
  };
})();
const rigOf = (play: Play, id: string) => PLAYER3D_V32[play.players.find((p) => p.id === id)?.team === 'X' ? 'def' : 'off'].rig;

/** the two-point area outline (floor polygon, metres): baseline corners, corner lanes, the arc */
export const area2Poly = (): [number, number][] => {
  const [bx, by] = FIBA.basket;
  const yJ = by + Math.sqrt(FIBA.threeR ** 2 - FIBA.cornerX ** 2);
  const a0 = Math.atan2(yJ - by, FIBA.cornerX), a1 = Math.PI - a0;
  const pts: [number, number][] = [[FIBA.cornerX, 0], [FIBA.cornerX, yJ]];
  for (let i = 1; i < 64; i++) {
    const a = a0 + ((a1 - a0) * i) / 64;
    pts.push([bx + FIBA.threeR * Math.cos(a), by + FIBA.threeR * Math.sin(a)]);
  }
  pts.push([-FIBA.cornerX, yJ], [-FIBA.cornerX, 0]);
  return pts;
};
const shapeGeo = (() => {
  let g: THREE.ShapeGeometry | null = null;
  return () => {
    if (g) return g;
    // floor (x, y) -> local plane (x, y); the mesh is rotated -90 deg about X so local y = world -z = floor y
    const s = new THREE.Shape(area2Poly().map(([x, y]) => new THREE.Vector2(x, y)));
    g = new THREE.ShapeGeometry(s, 4);
    return g;
  };
})();
const ribbonGeo = (pts: [number, number][], w: number, z: number) => {
  const pos: number[] = [];
  const idx: number[] = [];
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i], q = pts[Math.min(pts.length - 1, i + 1)], o = pts[Math.max(0, i - 1)];
    const dx = q[0] - o[0], dy = q[1] - o[1];
    const L = Math.hypot(dx, dy) || 1;
    const nx = -dy / L, ny = dx / L;
    for (const s of [-1, 1]) {
      const w3 = W3([p[0] + nx * s * w * 0.5, p[1] + ny * s * w * 0.5, z]);
      pos.push(...w3);
    }
    if (i < pts.length - 1) idx.push(2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 1, 2 * i + 3, 2 * i + 2);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
};
/** restricted area (FIBA: 4.90 m wide outside the lines, 5.80 m from the inner edge of the end line) */
export const PAINT = {halfW: FIBA.keyHalfW, depth: FIBA.ftY};
const paintGeo = (() => {
  let g: THREE.ShapeGeometry | null = null;
  return () => {
    if (g) return g;
    const {halfW: w, depth: d} = PAINT;
    g = new THREE.ShapeGeometry(new THREE.Shape([new THREE.Vector2(-w, 0), new THREE.Vector2(w, 0), new THREE.Vector2(w, d), new THREE.Vector2(-w, d)]), 1);
    return g;
  };
})();
const arcPts = (): [number, number][] => {
  const p = area2Poly();
  return p.slice(0, p.length);
};

export const Rules3D: React.FC<{play: Play; pt: number; o: RulesOv & {age: number}; a: number}> = ({play, pt, o, a}) => {
  const t = clamp(pt, 0, play.duration);
  switch (o.type) {
    case 'footRing': {
      const m = motionV33(play, o.player, t, rigOf(play, o.player));
      if (!m) return null;
      const i = o.foot === 'L' ? 0 : 1;
      const f = m.pose.toe[i], an = m.pose.ankle[i];
      // centre between the ankle and the toe (the ball of the foot), sole height from the foot state
      const c: V3 = [(f[0] + an[0]) / 2, (f[1] + an[1]) / 2, 0];
      const lift = Math.min(0.25, Math.max(0, Math.min(f[2], an[2] - 0.08)));
      const col = o.color ?? '#E0B455';
      const r = o.r ?? 0.24;
      const grow = 0.75 + 0.25 * eo(o.age / 0.25);
      return (
        <group>
          <mesh position={W3([c[0], c[1], 0.011 + lift])} rotation={[-Math.PI / 2, 0, 0]} scale={r * grow} material={mat(col, 0.95 * a)}>
            <ringGeometry args={[0.8, 1.0, 64]} />
          </mesh>
          <mesh position={W3([c[0], c[1], 0.009])} rotation={[-Math.PI / 2, 0, 0]} scale={r * 1.9} material={new THREE.MeshBasicMaterial({color: col, map: glowTex(), transparent: true, opacity: 0.45 * a, depthWrite: false, toneMapped: false, blending: THREE.AdditiveBlending})}>
            <planeGeometry args={[2, 2]} />
          </mesh>
        </group>
      );
    }
    case 'ballRing': {
      const b = ballV33(play, t);
      const col = o.color ?? '#E0B455';
      const r = o.r ?? 0.24;
      const grow = 1.25 - 0.25 * eo(o.age / 0.25);
      return (
        <mesh position={W3(b)} rotation={[-Math.PI / 2, 0, 0]} scale={grow} material={new THREE.MeshBasicMaterial({color: col, transparent: true, opacity: 0.95 * a, toneMapped: false, depthWrite: false})}>
          <torusGeometry args={[r, 0.016, 10, 64]} />
        </mesh>
      );
    }
    case 'handRing': {
      const m = motionV33(play, o.player, t, rigOf(play, o.player));
      if (!m) return null;
      const h = m.pose.hand[o.hand];
      const col = o.color ?? '#E5483A';
      const pulse = 1 + 0.18 * Math.max(0, 1 - o.age / 0.4);
      return (
        <group position={W3(h)}>
          <mesh scale={pulse} material={new THREE.MeshBasicMaterial({color: col, map: glowTex(), transparent: true, opacity: 0.55 * a, depthWrite: false, depthTest: false, toneMapped: false, blending: THREE.AdditiveBlending})}>
            <sphereGeometry args={[0.16, 24, 16]} />
          </mesh>
          <mesh scale={pulse} material={new THREE.MeshBasicMaterial({color: col, transparent: true, opacity: 0.95 * a, depthTest: false, toneMapped: false})}>
            <torusGeometry args={[0.15, 0.012, 8, 48]} />
          </mesh>
        </group>
      );
    }
    case 'area2': {
      const col = o.color ?? '#E0B455';
      return (
        <mesh geometry={shapeGeo()} position={[0, 0.02, 0]} renderOrder={2} rotation={[-Math.PI / 2, 0, 0]} material={mat(col, (o.opacity ?? 0.2) * a)} />
      );
    }
    case 'arc3': {
      const col = o.color ?? '#E0B455';
      const pts = arcPts();
      const n = Math.max(2, Math.round(pts.length * clamp(o.draw ? o.age / o.draw : 1)));
      return <mesh geometry={ribbonGeo(pts.slice(0, n), o.width ?? 0.11, 0.012)} material={mat(col, 0.95 * a)} />;
    }
    case 'paint': {
      const col = o.color ?? '#E0B455';
      const {halfW: w, depth: d} = PAINT;
      const ew = o.edge ?? 0.08;
      return (
        <group>
          <mesh geometry={paintGeo()} position={[0, 0.02, 0]} renderOrder={2} rotation={[-Math.PI / 2, 0, 0]} material={mat(col, (o.opacity ?? 0.22) * a)} />
          <mesh geometry={ribbonGeo([[-w + ew / 2, 0], [-w + ew / 2, d - ew / 2], [w - ew / 2, d - ew / 2], [w - ew / 2, 0]], ew, 0.013)} material={mat(col, 0.9 * a)} />
        </group>
      );
    }
    case 'centerLine': {
      const col = o.color ?? '#E0B455';
      const half = FIBA.halfW;
      const k = clamp(o.draw ? eo(o.age / o.draw) : 1);
      const x = Math.max(0.05, half * k);
      return <mesh geometry={ribbonGeo([[-x, FIBA.halfL], [0, FIBA.halfL], [x, FIBA.halfL]], o.width ?? 0.12, 0.013)} material={mat(col, 0.95 * a)} />;
    }
    case 'rimLine': {
      const col = o.color ?? '#FFFFFF';
      const [bx, by] = FIBA.basket;
      const h = o.half ?? 1.1;
      return (
        <mesh position={W3([bx, by, FIBA.rimZ])} rotation={[0, 0, Math.PI / 2]} material={new THREE.MeshBasicMaterial({color: col, transparent: true, opacity: 0.85 * a, toneMapped: false, depthWrite: false})}>
          <cylinderGeometry args={[0.009, 0.009, 2 * h, 8]} />
        </mesh>
      );
    }
  }
  return null;
};
