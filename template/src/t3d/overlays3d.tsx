// E2A 3D engine — tactical graphics that live INSIDE the 3D scene (same camera, same perspective,
// same depth as the players): floor rings, progressive route ribbons with arrowheads, staggered
// screen markers, animated passing lanes, separation bands, open-space zones, denial wedges.
// Colours: offence gold, defence red, neutral white. Everything eases in and out (no popping).
import React from 'react';
import * as THREE from 'three';
import type {V2, V3} from '../tactical/geometry.ts';
import type {Play} from '../tactical/play.ts';
import {posAt, routeOf} from '../tactical/play.ts';
import {W3} from './Athlete';

export const GOLD3 = '#E0B455';
export const RED3 = '#E5483A';
export const WHITE3 = '#FFFFFF';

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const easeOut = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
/** fade in over `fin`, out over `fout` (age and dur in seconds) */
export const fade = (age: number, dur: number, fin = 0.25, fout = 0.25) => Math.min(easeOut(age / fin), easeOut((dur - age) / fout));

const basic = (color: string, opacity: number) => new THREE.MeshBasicMaterial({color, transparent: true, opacity, depthWrite: false, toneMapped: false, side: THREE.DoubleSide});

/** ribbon geometry on the floor along a polyline (metres), width w, z lift */
const ribbon = (pts: V2[], w: number, z = 0.012, dashed = false) => {
  const pos: number[] = [];
  const idx: number[] = [];
  let acc = 0;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[Math.max(0, i - 1)];
    const b = pts[Math.min(pts.length - 1, i + 1)];
    let dx = b[0] - a[0];
    let dy = b[1] - a[1];
    const L = Math.hypot(dx, dy) || 1;
    dx /= L;
    dy /= L;
    const nx = -dy * (w / 2);
    const ny = dx * (w / 2);
    const p = pts[i];
    const l = W3([p[0] + nx, p[1] + ny, z]);
    const r = W3([p[0] - nx, p[1] - ny, z]);
    pos.push(...l, ...r);
    if (i > 0) {
      acc += Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]);
      const on = !dashed || Math.floor(acc / 0.35) % 2 === 0;
      if (on) {
        const k = i * 2;
        idx.push(k - 2, k - 1, k, k - 1, k + 1, k);
      }
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
};

const arrowHead = (tip: V2, dir: V2, size: number, z = 0.014) => {
  const L = Math.hypot(dir[0], dir[1]) || 1;
  const d: V2 = [dir[0] / L, dir[1] / L];
  const n: V2 = [-d[1], d[0]];
  const a = W3([tip[0] + d[0] * size * 0.55, tip[1] + d[1] * size * 0.55, z]);
  const b = W3([tip[0] - d[0] * size * 0.45 + n[0] * size * 0.55, tip[1] - d[1] * size * 0.45 + n[1] * size * 0.55, z]);
  const c = W3([tip[0] - d[0] * size * 0.45 - n[0] * size * 0.55, tip[1] - d[1] * size * 0.45 - n[1] * size * 0.55, z]);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute([...a, ...b, ...c], 3));
  return g;
};

const cut = (pts: V2[], u: number): V2[] => {
  // keep the first fraction u of the polyline (by length)
  if (u >= 1) return pts;
  let total = 0;
  for (let i = 1; i < pts.length; i++) total += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  const want = total * clamp(u);
  const out: V2[] = [pts[0]];
  let acc = 0;
  for (let i = 1; i < pts.length; i++) {
    const s = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    if (acc + s >= want) {
      const f = (want - acc) / (s || 1);
      out.push([pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f]);
      return out;
    }
    acc += s;
    out.push(pts[i]);
  }
  return out;
};

export type Ov3 =
  | {type: 'ring'; player: string; color?: string; pulse?: boolean}
  | {type: 'route'; player: string; t0: number; t1: number; color?: string; draw?: number; dashed?: boolean; width?: number; pts?: V2[]; trail?: boolean}
  | {type: 'screen'; player?: string; at?: V2; n: number; facing?: number}
  | {type: 'passLane'; src: string; dst: string | V2; color?: string}
  | {type: 'separation'; a: string; b: string; color?: string}
  | {type: 'openSpace'; at: V2; r: number; rx?: number; angle?: number; color?: string}
  | {type: 'deny'; player: string; toward: V2; color?: string}
  | {type: 'blocked'; at: V2; color?: string};

export type LiveOv3 = Ov3 & {age: number; dur: number};

const hatchTex = (() => {
  let t: THREE.Texture | null = null;
  return () => {
    if (t) return t;
    const c = document.createElement('canvas');
    c.width = 256;
    c.height = 256;
    const g = c.getContext('2d')!;
    g.clearRect(0, 0, 256, 256);
    g.strokeStyle = 'rgba(255,255,255,1)';
    g.lineWidth = 14;
    for (let i = -256; i < 512; i += 40) {
      g.beginPath();
      g.moveTo(i, 0);
      g.lineTo(i + 256, 256);
      g.stroke();
    }
    t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(3, 3);
    return t;
  };
})();

export const Overlays3D: React.FC<{play: Play; pt: number; items: LiveOv3[]}> = ({play, pt, items}) => {
  const P = (id: string): V2 => posAt(play.tracks[id], Math.max(0, Math.min(play.duration, pt)));
  return (
    <group>
      {items.map((o, i) => {
        const a = fade(o.age, o.dur);
        if (a <= 0.001) return null;
        switch (o.type) {
          case 'ring': {
            const p = P(o.player);
            const pulse = o.pulse ? 1 + 0.12 * Math.sin(o.age * 7) : 1;
            const grow = 0.6 + 0.4 * easeOut(o.age / 0.3);
            const col = o.color ?? (o.player.startsWith('O') ? GOLD3 : RED3);
            return (
              <group key={i} position={W3([p[0], p[1], 0.015])} rotation={[-Math.PI / 2, 0, 0]} scale={grow * pulse}>
                <mesh material={basic(col, 0.95 * a)}>
                  <ringGeometry args={[0.46, 0.56, 48]} />
                </mesh>
                <mesh material={basic(col, 0.22 * a)}>
                  <circleGeometry args={[0.46, 48]} />
                </mesh>
              </group>
            );
          }
          case 'route': {
            const t1 = o.trail ? Math.min(o.t1, pt) : o.t1;
            if (t1 - o.t0 < 0.05 && !o.pts) return null;
            const pts = o.pts ?? routeOf(play, o.player, o.t0, t1, 1 / 30);
            const u = o.draw ? easeOut(o.age / o.draw) : 1;
            const part = cut(pts, u);
            if (part.length < 2) return null;
            const col = o.color ?? (o.player.startsWith('O') ? GOLD3 : RED3);
            const tip = part[part.length - 1];
            const prev = part[Math.max(0, part.length - 4)];
            const w = o.width ?? 0.2;
            return (
              <group key={i}>
                <mesh geometry={ribbon(part, w * 2.2, 0.011)} material={basic(col, 0.18 * a)} />
                <mesh geometry={ribbon(part, w, 0.013, o.dashed)} material={basic(col, 0.95 * a)} />
                <mesh geometry={arrowHead(tip, [tip[0] - prev[0], tip[1] - prev[1]], w * 3.2)} material={basic(col, 0.95 * a)} />
              </group>
            );
          }
          case 'screen': {
            // staggered screen marker: a translucent upright panel at the screener + floor bar + number
            const p = o.at ?? P(o.player!);
            const f = o.facing ?? 0;
            const pop = easeOut(o.age / 0.35);
            const n: V2 = [Math.cos(f), Math.sin(f)];
            const side: V2 = [-n[1], n[0]];
            const c = W3([p[0] + n[0] * 0.38, p[1] + n[1] * 0.38, 0.9 * pop]);
            const rotY = Math.atan2(side[0], -side[1]);
            return (
              <group key={i}>
                <mesh position={c} rotation={[0, rotY, 0]} scale={[1, pop, 1]} material={basic(GOLD3, 0.24 * a)}>
                  <planeGeometry args={[1.25, 1.8]} />
                </mesh>
                <mesh position={[c[0], 1.8 * pop, c[2]]} rotation={[0, rotY, 0]} material={basic(GOLD3, 0.95 * a)}>
                  <planeGeometry args={[1.25, 0.05]} />
                </mesh>
                <mesh geometry={ribbon([[p[0] + n[0] * 0.38 - side[0] * 0.75, p[1] + n[1] * 0.38 - side[1] * 0.75], [p[0] + n[0] * 0.38 + side[0] * 0.75, p[1] + n[1] * 0.38 + side[1] * 0.75]], 0.12, 0.016)} material={basic(GOLD3, 0.95 * a)} />
              </group>
            );
          }
          case 'passLane': {
            const s = P(o.src);
            const e = typeof o.dst === 'string' ? P(o.dst) : o.dst;
            const pts: V2[] = Array.from({length: 40}, (_, k) => [s[0] + ((e[0] - s[0]) * k) / 39, s[1] + ((e[1] - s[1]) * k) / 39]);
            const u = easeOut(o.age / 0.45);
            const part = cut(pts, u);
            if (part.length < 2) return null;
            const col = o.color ?? WHITE3;
            const tip = part[part.length - 1];
            // marching dashes
            const shift = (o.age * 0.9) % 0.7;
            const shifted = cut(pts, 1).map((q) => q);
            void shifted;
            return (
              <group key={i}>
                <mesh geometry={ribbon(part, 0.34, 0.01)} material={basic(col, 0.14 * a)} />
                <mesh geometry={ribbon(part.map((q, k) => (k === 0 ? q : q)), 0.09, 0.013, true)} material={basic(col, 0.9 * a)} position={[0, 0, 0]} />
                <mesh geometry={arrowHead(tip, [e[0] - s[0], e[1] - s[1]], 0.5)} material={basic(col, 0.95 * a)} />
                {void shift}
              </group>
            );
          }
          case 'separation': {
            const pa = P(o.a);
            const pb = P(o.b);
            const u = easeOut(o.age / 0.4);
            const mid: V2 = [(pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2];
            const A: V2 = [mid[0] + (pa[0] - mid[0]) * u, mid[1] + (pa[1] - mid[1]) * u];
            const B: V2 = [mid[0] + (pb[0] - mid[0]) * u, mid[1] + (pb[1] - mid[1]) * u];
            const col = o.color ?? GOLD3;
            const d: V2 = [pb[0] - pa[0], pb[1] - pa[1]];
            const L = Math.hypot(d[0], d[1]) || 1;
            const n: V2 = [-d[1] / L, d[0] / L];
            const capA: V2[] = [[A[0] + n[0] * 0.3, A[1] + n[1] * 0.3], [A[0] - n[0] * 0.3, A[1] - n[1] * 0.3]];
            const capB: V2[] = [[B[0] + n[0] * 0.3, B[1] + n[1] * 0.3], [B[0] - n[0] * 0.3, B[1] - n[1] * 0.3]];
            return (
              <group key={i}>
                <mesh geometry={ribbon([A, B], 0.55, 0.01)} material={basic(col, 0.2 * a)} />
                <mesh geometry={ribbon([A, B], 0.08, 0.014)} material={basic(col, 0.95 * a)} />
                <mesh geometry={ribbon(capA, 0.08, 0.014)} material={basic(col, 0.95 * a)} />
                <mesh geometry={ribbon(capB, 0.08, 0.014)} material={basic(col, 0.95 * a)} />
              </group>
            );
          }
          case 'openSpace': {
            const grow = easeOut(o.age / 0.5);
            const col = o.color ?? GOLD3;
            return (
              <group key={i} position={W3([o.at[0], o.at[1], 0.009])} rotation={[-Math.PI / 2, 0, o.angle ?? 0]} scale={[(o.rx ?? o.r) * grow, o.r * grow, 1]}>
                <mesh material={new THREE.MeshBasicMaterial({color: col, map: hatchTex(), transparent: true, opacity: 0.45 * a, depthWrite: false, toneMapped: false})}>
                  <circleGeometry args={[1, 48]} />
                </mesh>
                <mesh material={basic(col, 0.9 * a)}>
                  <ringGeometry args={[0.96, 1.0, 64]} />
                </mesh>
              </group>
            );
          }
          case 'deny': {
            // red wedge from the defender toward the route he takes away
            const p = P(o.player);
            const dir = Math.atan2(o.toward[1] - p[1], o.toward[0] - p[0]);
            const R = Math.min(2.4, Math.hypot(o.toward[0] - p[0], o.toward[1] - p[1])) * easeOut(o.age / 0.45);
            const pts: number[] = [...W3([p[0], p[1], 0.012])];
            const N = 20;
            for (let k = 0; k <= N; k++) {
              const ang = dir - 0.45 + (0.9 * k) / N;
              pts.push(...W3([p[0] + Math.cos(ang) * R, p[1] + Math.sin(ang) * R, 0.012]));
            }
            const idx: number[] = [];
            for (let k = 1; k <= N; k++) idx.push(0, k, k + 1);
            const g = new THREE.BufferGeometry();
            g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
            g.setIndex(idx);
            return <mesh key={i} geometry={g} material={basic(o.color ?? RED3, 0.38 * a)} />;
          }
          case 'blocked': {
            const s = 0.35 * easeOut(o.age / 0.3);
            const c = o.color ?? RED3;
            return (
              <group key={i}>
                <mesh geometry={ribbon([[o.at[0] - s, o.at[1] - s], [o.at[0] + s, o.at[1] + s]], 0.12, 0.016)} material={basic(c, a)} />
                <mesh geometry={ribbon([[o.at[0] - s, o.at[1] + s], [o.at[0] + s, o.at[1] - s]], 0.12, 0.016)} material={basic(c, a)} />
              </group>
            );
          }
          default:
            return null;
        }
      })}
    </group>
  );
};

/** world point -> screen px for a Cam3 (same maths as three's PerspectiveCamera) */
export const projector = (cam: {pos: V3; target: V3; up: V3; fov: number; roll?: number}, W: number, H: number) => {
  const c = new THREE.PerspectiveCamera(cam.fov, W / H, 0.1, 120);
  c.position.set(...W3(cam.pos));
  c.up.set(...W3(cam.up));
  c.lookAt(...W3(cam.target));
  if (cam.roll) c.rotateZ((cam.roll * Math.PI) / 180);
  c.updateMatrixWorld();
  c.updateProjectionMatrix();
  return (p: V3) => {
    const v = new THREE.Vector3(...W3(p)).project(c);
    return {x: ((v.x + 1) / 2) * W, y: ((1 - v.y) / 2) * H, visible: v.z < 1 && v.z > -1};
  };
};
