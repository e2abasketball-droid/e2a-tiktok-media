// E2A 3D engine — broadcast telestration layer (2026-11-19, Spain Pick & Roll 2.0 brief).
// Reusable world-space graphics that live INSIDE the 3D scene (same camera, perspective and depth test as the players,
// so a body in front hides them). Every one is a pure function of (play, play time pt, age, dur): seek = playback,
// rewinds and freezes carry them with the play. Dispatched from Overlays3D (overlays3d.tsx) by `type`:
//   spot        PlayerSpotlight: floor halo + soft light cone that follows a player (pulse in, hold, fade)
//   ripple      ImpactPulse: two floor rings expanding from a contact point (screen contact, catch, rim)
//   floorText   floor decal label painted on the court (OPEN, EASY 2, OPEN 3...), oriented for a camera yaw
//   ballTrail   BallTrail: short fading trail of the ball's real past positions (passes and shots only)
//   ghostTrail  GhostTrail: afterimages of a player's last positions (floor discs + translucent columns), shows direction
//   passLane + travel   PassWindow that TRAVELS: a lit segment runs from the passer to the catch point, comet head first
// Colours follow the engine rule: offence gold, defence red/coral, neutral white.
import React from 'react';
import * as THREE from 'three';
import type {V2, V3} from '../tactical/geometry.ts';
import type {Play} from '../tactical/play.ts';
import {posAt, sample} from '../tactical/play.ts';
import {W3} from './Athlete';

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const add = (color: string, opacity: number, map?: THREE.Texture) =>
  new THREE.MeshBasicMaterial({color, ...(map ? {map} : {}), transparent: true, opacity, depthWrite: false, toneMapped: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending});
const flat = (color: string, opacity: number, map?: THREE.Texture) =>
  new THREE.MeshBasicMaterial({color, ...(map ? {map} : {}), transparent: true, opacity, depthWrite: false, toneMapped: false, side: THREE.DoubleSide});

export type TeleOv =
  | {type: 'spot'; player?: string; at?: V2; color?: string; r?: number; h?: number; strength?: number; beam?: boolean}
  | {type: 'ripple'; player?: string; at?: V2; color?: string; r?: number; rings?: number; period?: number}
  | {type: 'floorText'; text: string; at?: V2; player?: string; offset?: V2; yaw?: number; size?: number; color?: string; plate?: boolean}
  | {type: 'ballTrail'; len?: number; color?: string}
  | {type: 'ghostTrail'; player: string; len?: number; n?: number; color?: string; columns?: boolean}
  /** 2026-11-21 (BLOB V2, brief VFX 02 + 08): ONE screen annotation = floor stencil under the screener's feet with a
   *  facing arrow toward the defender he screens, a circled screen number and a plated floor label ("O2 SCREENS X5").
   *  Nothing is drawn before `plantAt` (play time of the two-foot plant); the stencil pops and pulses once from there. */
  | {type: 'screenTag'; player: string; vs: string; n: number; label: string; plantAt: number; yaw?: number; labelOffset?: V2; size?: number};

const radial = (() => {
  let t: THREE.Texture | null = null;
  return () => {
    if (t) return t;
    const c = document.createElement('canvas');
    c.width = c.height = 128;
    const g = c.getContext('2d')!;
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.5, 'rgba(255,255,255,0.5)');
    gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr;
    g.fillRect(0, 0, 128, 128);
    return (t = new THREE.CanvasTexture(c));
  };
})();

/** vertical falloff for the light cone: bright at the floor, gone at the top, soft edges */
const beamTex = (() => {
  let t: THREE.Texture | null = null;
  return () => {
    if (t) return t;
    const c = document.createElement('canvas');
    c.width = 64;
    c.height = 128;
    const g = c.getContext('2d')!;
    const gr = g.createLinearGradient(0, 128, 0, 0);
    gr.addColorStop(0, 'rgba(255,255,255,0.9)');
    gr.addColorStop(0.35, 'rgba(255,255,255,0.35)');
    gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr;
    g.fillRect(0, 0, 64, 128);
    return (t = new THREE.CanvasTexture(c));
  };
})();

/** floor label texture (Anton, already loaded by the composition before the scene mounts) */
export const textTex = (() => {
  const cache = new Map<string, {tex: THREE.Texture; aspect: number}>();
  return (text: string, color: string, plate: boolean) => {
    const key = `${text}|${color}|${plate}`;
    const hit = cache.get(key);
    if (hit) return hit;
    const c = document.createElement('canvas');
    const g = c.getContext('2d')!;
    const fs = 160;
    g.font = `${fs}px Anton`;
    const w = Math.ceil(g.measureText(text).width + fs * 0.7);
    c.width = w;
    c.height = Math.round(fs * 1.5);
    const g2 = c.getContext('2d')!;
    g2.clearRect(0, 0, c.width, c.height);
    if (plate) {
      g2.fillStyle = 'rgba(11,28,61,0.78)';
      const r = 26;
      g2.beginPath();
      g2.roundRect(4, 4, c.width - 8, c.height - 8, r);
      g2.fill();
      g2.strokeStyle = color;
      g2.lineWidth = 8;
      g2.stroke();
    }
    g2.font = `${fs}px Anton`;
    g2.textAlign = 'center';
    g2.textBaseline = 'middle';
    g2.fillStyle = color;
    g2.fillText(text, c.width / 2, c.height / 2 + fs * 0.04);
    const tex = new THREE.CanvasTexture(c);
    tex.anisotropy = 8;
    const out = {tex, aspect: c.width / c.height};
    cache.set(key, out);
    return out;
  };
})();

/** quad lying on the floor: centre, baseline direction (screen right), height direction (screen up) */
export const floorQuad = (c: V2, right: V2, up: V2, w: number, h: number, z = 0.02, uMax = 1) => {
  const p = (sx: number, sy: number) => W3([c[0] + right[0] * sx * w * 0.5 + up[0] * sy * h * 0.5, c[1] + right[1] * sx * w * 0.5 + up[1] * sy * h * 0.5, z]);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute([...p(-1, -1), ...p(1, -1), ...p(1, 1), ...p(-1, 1)], 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute([0, 0, uMax, 0, uMax, 1, 0, 1], 2));
  g.setIndex([0, 1, 2, 0, 2, 3]);
  return g;
};

/** screen axes of an orbit camera with this yaw (camera3d.ts convention: yaw 0 looks at the basket from half court) */
export const yawAxes = (yawDeg: number): {right: V2; up: V2} => {
  const y = (yawDeg * Math.PI) / 180;
  const fwd: V2 = [Math.sin(y), -Math.cos(y)];
  return {right: [-Math.cos(y), -Math.sin(y)], up: fwd};
};

const at2 = (play: Play, pt: number, player?: string, at?: V2): V2 => (player ? posAt(play.tracks[player], clamp(pt, 0, play.duration)) : at ?? [0, 1.575]);

export const Telestration3D: React.FC<{play: Play; pt: number; o: TeleOv & {age: number; dur: number}; a: number}> = ({play, pt, o, a}) => {
  switch (o.type) {
    case 'spot': {
      const p = at2(play, pt, o.player, o.at);
      const col = o.color ?? (o.player?.startsWith('X') ? '#F06A55' : '#F2C76A');
      const k = o.strength ?? 1;
      // pulse in (overshoot), then a slow breath while it holds
      const pop = o.age < 0.35 ? 0.75 + 0.35 * Math.sin((Math.PI / 2) * (o.age / 0.35)) : 1.1 - 0.1 * eo((o.age - 0.35) / 0.25);
      const breath = 1 + 0.04 * Math.sin(o.age * 4.2);
      const r = (o.r ?? 0.9) * pop * breath;
      const h = o.h ?? 2.6;
      return (
        <group>
          <mesh position={W3([p[0], p[1], 0.011])} rotation={[-Math.PI / 2, 0, 0]} scale={r} material={add(col, 0.75 * k * a, radial())}>
            <planeGeometry args={[2, 2]} />
          </mesh>
          <mesh position={W3([p[0], p[1], 0.013])} rotation={[-Math.PI / 2, 0, 0]} scale={r * 0.62} material={flat(col, 0.9 * a)}>
            <ringGeometry args={[0.92, 1.0, 64]} />
          </mesh>
          {o.beam !== false && (
            <mesh position={W3([p[0], p[1], h / 2])} material={add(col, 0.22 * k * a, beamTex())}>
              <cylinderGeometry args={[r * 0.42, r * 0.62, h, 40, 1, true]} />
            </mesh>
          )}
        </group>
      );
    }
    case 'ripple': {
      const p = at2(play, pt, o.player, o.at);
      const col = o.color ?? '#F2C76A';
      const R = o.r ?? 1.6;
      const per = o.period ?? 0.55;
      const n = o.rings ?? 2;
      return (
        <group>
          {Array.from({length: n}, (_, i) => {
            const u = (o.age - i * 0.16) / per;
            if (u < 0 || u > 1) return null;
            const rr = 0.25 + (R - 0.25) * eo(u);
            const op = (1 - u) * a;
            return (
              <mesh key={i} position={W3([p[0], p[1], 0.016 + i * 0.001])} rotation={[-Math.PI / 2, 0, 0]} scale={rr} material={flat(col, 0.9 * op)}>
                <ringGeometry args={[0.9, 1.0, 72]} />
              </mesh>
            );
          })}
          {o.age < 0.3 && (
            <mesh position={W3([p[0], p[1], 0.012])} rotation={[-Math.PI / 2, 0, 0]} scale={0.9} material={add(col, (1 - o.age / 0.3) * 0.8 * a, radial())}>
              <planeGeometry args={[2, 2]} />
            </mesh>
          )}
        </group>
      );
    }
    case 'floorText': {
      const base = at2(play, pt, o.player, o.at);
      const c: V2 = [base[0] + (o.offset?.[0] ?? 0), base[1] + (o.offset?.[1] ?? 0)];
      const {right, up} = yawAxes(o.yaw ?? 0);
      const t = textTex(o.text, o.color ?? '#F2C76A', o.plate ?? false);
      const h = (o.size ?? 0.9) * (0.92 + 0.08 * eo(o.age / 0.3));
      // mask reveal from the left (baseline direction), then hold
      const rev = eo(o.age / 0.35);
      const w = h * t.aspect;
      const ws = w * rev;
      const cc: V2 = [c[0] - right[0] * (w - ws) / 2, c[1] - right[1] * (w - ws) / 2];
      return <mesh geometry={floorQuad(cc, right, up, Math.max(0.01, ws), h, 0.021, Math.max(0.001, rev))} material={flat('#FFFFFF', 0.95 * a, t.tex)} />;
    }
    case 'ballTrail': {
      const f = sample(play, pt).ball;
      if (!f.inFlight) return null;
      const len = o.len ?? 0.22;
      const N = 12;
      const col = o.color ?? '#FFE3A3';
      return (
        <group>
          {Array.from({length: N}, (_, i) => {
            const u = (i + 1) / N;
            const tt = pt - len * u;
            const b = sample(play, Math.max(0, tt)).ball;
            if (!b.inFlight) return null;
            const s = 0.11 * (1 - u * 0.7);
            return (
              <mesh key={i} position={W3(b.pos as V3)} material={add(col, 0.45 * (1 - u) * a)}>
                <sphereGeometry args={[s, 12, 8]} />
              </mesh>
            );
          })}
        </group>
      );
    }
    case 'ghostTrail': {
      const n = o.n ?? 5;
      const len = o.len ?? 0.45;
      const col = o.color ?? (o.player.startsWith('X') ? '#F06A55' : '#F2C76A');
      const now = posAt(play.tracks[o.player], clamp(pt, 0, play.duration));
      return (
        <group>
          {Array.from({length: n}, (_, i) => {
            const u = (i + 1) / n;
            const p = posAt(play.tracks[o.player], clamp(pt - len * u, 0, play.duration));
            if (Math.hypot(p[0] - now[0], p[1] - now[1]) < 0.12 * (i + 1)) return null; // standing still: no ghosts
            const op = (1 - u) * a;
            return (
              <group key={i}>
                <mesh position={W3([p[0], p[1], 0.012])} rotation={[-Math.PI / 2, 0, 0]} scale={0.42} material={add(col, 0.55 * op, radial())}>
                  <planeGeometry args={[2, 2]} />
                </mesh>
                {o.columns !== false && (
                  <mesh position={W3([p[0], p[1], 0.95])} material={add(col, 0.12 * op, beamTex())}>
                    <cylinderGeometry args={[0.2, 0.26, 1.9, 20, 1, true]} />
                  </mesh>
                )}
              </group>
            );
          })}
        </group>
      );
    }
    case 'screenTag': {
      const since = pt - o.plantAt;
      if (since < -1e-6) return null;
      const pop = eo(Math.max(since / 0.3, Math.min(1, o.age / 0.35) * (since > 0 ? 1 : 0.999)));
      // drawn where the screen WAS set (screens are stationary, so this is also where the screener stands while it
      // lasts); a recap after he has left keeps the marker on the real screen spot
      const at = posAt(play.tracks[o.player], clamp(o.plantAt, 0, play.duration));
      const me = at;
      const vs = posAt(play.tracks[o.vs], clamp(o.plantAt, 0, play.duration));
      const L = Math.hypot(vs[0] - at[0], vs[1] - at[1]) || 1;
      const n: V2 = [(vs[0] - at[0]) / L, (vs[1] - at[1]) / L];
      const side: V2 = [-n[1], n[0]];
      const gold = '#F2C76A';
      const c: V2 = [me[0] + n[0] * 0.18, me[1] + n[1] * 0.18];
      // stencil: a short wide bar (the wall the defender meets) + a soft pad under both feet
      const bar = floorQuad(c, side, n, 1.25 * pop, 0.16, 0.015);
      const pad = floorQuad([me[0], me[1]], side, n, 1.05 * pop, 0.7 * pop, 0.012);
      // facing arrow: triangle from the bar toward the defender
      const tipD = 0.62;
      const tri = new THREE.BufferGeometry();
      const q = (a: number, b: number) => W3([c[0] + n[0] * a + side[0] * b, c[1] + n[1] * a + side[1] * b, 0.016]);
      tri.setAttribute('position', new THREE.Float32BufferAttribute([...q(0.14, -0.2 * pop), ...q(0.14, 0.2 * pop), ...q(0.14 + (tipD - 0.14) * pop, 0)], 3));
      tri.setIndex([0, 1, 2]);
      // one pulse ring at the plant (play time, so a rewind / slow motion keeps it honest)
      const pu = clamp(since / 0.5);
      const {right, up} = yawAxes(o.yaw ?? 0);
      const num = textTex(String(o.n), '#0B1C3D', false);
      const lab = textTex(o.label, gold, true);
      const hs = (o.size ?? 0.42) * pop;
      const off = o.labelOffset ?? [0, 0];
      const lc: V2 = [me[0] + off[0], me[1] + off[1]];
      const nc: V2 = [me[0] - side[0] * 0.95, me[1] - side[1] * 0.95];
      return (
        <group>
          <mesh geometry={pad} material={add(gold, 0.38 * a, radial())} />
          <mesh geometry={bar} material={flat(gold, 0.95 * a)} />
          <mesh geometry={tri} material={flat(gold, 0.95 * a)} />
          {pu < 1 && (
            <mesh position={W3([me[0], me[1], 0.017])} rotation={[-Math.PI / 2, 0, 0]} scale={0.4 + 1.1 * eo(pu)} material={flat(gold, 0.85 * (1 - pu) * a)}>
              <ringGeometry args={[0.9, 1.0, 64]} />
            </mesh>
          )}
          <mesh position={W3([nc[0], nc[1], 0.018])} rotation={[-Math.PI / 2, 0, 0]} scale={0.27 * pop} material={flat(gold, 0.97 * a)}>
            <circleGeometry args={[1, 40]} />
          </mesh>
          <mesh geometry={floorQuad(nc, right, up, 0.3 * pop * num.aspect, 0.3 * pop, 0.019)} material={flat('#FFFFFF', a, num.tex)} />
          {o.label && <mesh geometry={floorQuad(lc, right, up, Math.max(0.01, hs * lab.aspect), Math.max(0.01, hs), 0.02)} material={flat('#FFFFFF', 0.97 * a, lab.tex)} />}
        </group>
      );
    }
    default:
      return null;
  }
};

/** PassWindow that travels (passLane with `travel`): from the passer's hands to the catch point at `dstAt` (play time,
 *  where the receiver WILL be), a lit segment runs ahead of the ball with a comet head, then the lane holds dimmed. */
export const PassTravel: React.FC<{play: Play; pt: number; src: string; dst: string | V2; dstAt?: number; travel: number; age: number; a: number; color?: string;
  ribbon: (pts: V2[], w: number, z?: number, dashed?: boolean) => THREE.BufferGeometry; arrowHead: (tip: V2, dir: V2, size: number, z?: number) => THREE.BufferGeometry}> = ({play, pt, src, dst, dstAt, travel, age, a, color, ribbon, arrowHead}) => {
  const s = posAt(play.tracks[src], clamp(pt, 0, play.duration));
  const e: V2 = typeof dst === 'string' ? posAt(play.tracks[dst], clamp(dstAt ?? pt, 0, play.duration)) : dst;
  const L = Math.hypot(e[0] - s[0], e[1] - s[1]) || 1;
  const dir: V2 = [(e[0] - s[0]) / L, (e[1] - s[1]) / L];
  const u = eo(age / travel);
  const P = (k: number): V2 => [s[0] + dir[0] * L * k, s[1] + dir[1] * L * k];
  const line = Array.from({length: 24}, (_, k) => P((u * k) / 23));
  const col = color ?? '#FFFFFF';
  const head = P(u);
  const tail = Array.from({length: 8}, (_, k) => P(Math.max(0, u - 0.18) + ((u - Math.max(0, u - 0.18)) * k) / 7));
  return (
    <group>
      <mesh geometry={ribbon(line, 0.42, 0.01)} material={flat(col, 0.12 * a)} />
      <mesh geometry={ribbon(line, 0.08, 0.013)} material={flat(col, 0.75 * a)} />
      {u < 0.999 && <mesh geometry={ribbon(tail, 0.2, 0.015)} material={add('#FFE3A3', 0.9 * a)} />}
      {u < 0.999 && (
        <mesh position={W3([head[0], head[1], 0.016])} rotation={[-Math.PI / 2, 0, 0]} scale={0.38} material={add('#FFE3A3', 0.9 * a, radial())}>
          <planeGeometry args={[2, 2]} />
        </mesh>
      )}
      {u > 0.6 && <mesh geometry={arrowHead(P(Math.min(1, u)), dir, 0.55)} material={flat(col, 0.95 * a * eo((u - 0.6) / 0.3))} />}
    </group>
  );
};
