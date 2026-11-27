// E2A 3D engine — telestration family v2 (2026-11-19, Blind Pig brief). Extends telestration3d.tsx (Spain PnR 2.0)
// with seven world-space graphics. Same contract: pure functions of (play, play time pt, age, dur) drawn inside the
// 3D scene (perspective + depth test with the players), dispatched from Overlays3D by `type`, entry / hold / exit.
//   arrow3d      CourtArrow3D: a RAISED arrow along a player's real route (thick top + side walls + chevron glints
//                running toward the tip); `consume` eats it from the player's feet, `draw` grows it
//   lockRing     PlayerLockRing: ring on the floor + four reticle brackets that fly in, rotate and LOCK on the player
//   vision       VisionConflict: the defender's two lines of sight on the floor (to the ball, to his man) and the
//                angle between them; past `split` degrees the arc turns red and pulses (he cannot see both)
//   tether       AssignmentTether: elastic band defender -> man; thins and turns coral as it stretches, snaps open
//                (gap in the middle) beyond `snap` metres
//   ghost        GhostPosition: translucent disc + column where a player WAS at play time `t` (or a fixed spot),
//                optional dashed link to where he is now
//   ballPath     BallTrajectory: the real 3D path of one pass of the play (sampled from play.ts, so it is exactly
//                the flight that follows), drawn ahead of the ball as a dotted arc; the bounce point gets a ring
//   motionTrail  MotionTrail: a fading ribbon of the player's last `len` seconds on the floor
import React from 'react';
import * as THREE from 'three';
import type {V2, V3} from '../tactical/geometry.ts';
import type {Play} from '../tactical/play.ts';
import {posAt, routeOf, sample, ballPhase} from '../tactical/play.ts';
import {poseAt, BALL_R} from './rig';
import {W3} from './Athlete';

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const mat = (color: string, opacity: number, additive = false) =>
  new THREE.MeshBasicMaterial({color, transparent: true, opacity, depthWrite: false, toneMapped: false, side: THREE.DoubleSide, ...(additive ? {blending: THREE.AdditiveBlending} : {})});
const GOLD = '#F2C76A';
const CORAL = '#F06A55';
const RED = '#E5483A';
const WHITE = '#FFFFFF';

export type TeleOvBP =
  | {type: 'arrow3d'; player: string; t0: number; t1: number; color?: string; width?: number; draw?: number; consume?: boolean; h?: number}
  | {type: 'lockRing'; player: string; color?: string; size?: number}
  | {type: 'vision'; player: string; man: string; split?: number; color?: string; len?: number}
  | {type: 'tether'; a: string; b: string; rest?: number; snap?: number}
  | {type: 'ghost'; player?: string; t?: number; at?: V2; color?: string; link?: boolean}
  | {type: 'ballPath'; src: string; dst: string; color?: string; draw?: number}
  | {type: 'motionTrail'; player: string; len?: number; color?: string; width?: number}
  /** 2026-11-26 (Zero Cut): OpenLane — translucent corridor that opens BEHIND a beaten defender toward a target (the
   *  rim by default). Anchored to the defender's REAL position every frame (live), so it only exists where the space
   *  really is; `anchor` = a player id (corridor starts `gap` m behind him on the target side) or a fixed spot. Grows
   *  from the defender to `target` over `draw` s; chevrons run toward the target. Width tapers to `tip` at the end.
   *  (`from` / `to` stay the overlay's shot-time window, as for every overlay.) */
  | {type: 'openLane'; anchor: string | V2; target?: V2 | string; width?: number; tip?: number; gap?: number; color?: string; draw?: number; chevrons?: boolean}
  /** DEBUG ONLY (2026-11-19 catch fix; never in a published edit): trunk volume (elliptic cylinder used by
   *  scripts/qc-catch.mts), ball sphere coloured by ball phase, palm contact points, body forward vector (cyan),
   *  chest forward (white) and the ball's direction of travel (magenta) */
  | {type: 'debugCatch'; player: string};

const P = (play: Play, id: string, t: number): V2 => posAt(play.tracks[id], clamp(t, 0, play.duration));

/** floor ribbon along a polyline at height z (optionally dashed) */
const ribbon = (pts: V2[], w: number, z = 0.012, dashed = 0) => {
  const pos: number[] = [];
  const idx: number[] = [];
  let acc = 0;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[Math.max(0, i - 1)];
    const b = pts[Math.min(pts.length - 1, i + 1)];
    const L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
    const nx = (-(b[1] - a[1]) / L) * (w / 2);
    const ny = ((b[0] - a[0]) / L) * (w / 2);
    const p = pts[i];
    pos.push(...W3([p[0] + nx, p[1] + ny, z]), ...W3([p[0] - nx, p[1] - ny, z]));
    if (i > 0) {
      acc += Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]);
      if (!dashed || Math.floor(acc / dashed) % 2 === 0) {
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

/** vertical wall strip along a polyline, offset sideways by `off`, from z0 to z1 (side of a raised arrow) */
const wall = (pts: V2[], off: number, z0: number, z1: number) => {
  const pos: number[] = [];
  const idx: number[] = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[Math.max(0, i - 1)];
    const b = pts[Math.min(pts.length - 1, i + 1)];
    const L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
    const nx = (-(b[1] - a[1]) / L) * off;
    const ny = ((b[0] - a[0]) / L) * off;
    const p = pts[i];
    pos.push(...W3([p[0] + nx, p[1] + ny, z0]), ...W3([p[0] + nx, p[1] + ny, z1]));
    if (i > 0) {
      const k = i * 2;
      idx.push(k - 2, k - 1, k, k - 1, k + 1, k);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
};

const polyLen = (pts: V2[]) => pts.slice(1).reduce((s, q, i) => s + Math.hypot(q[0] - pts[i][0], q[1] - pts[i][1]), 0);
/** point and direction at arclength fraction u */
const along = (pts: V2[], u: number): {p: V2; d: V2} => {
  const total = polyLen(pts);
  let want = total * clamp(u);
  for (let i = 1; i < pts.length; i++) {
    const s = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    if (want <= s || i === pts.length - 1) {
      const f = s > 0 ? clamp(want / s) : 0;
      const d: V2 = [(pts[i][0] - pts[i - 1][0]) / (s || 1), (pts[i][1] - pts[i - 1][1]) / (s || 1)];
      return {p: [pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f], d};
    }
    want -= s;
  }
  return {p: pts[pts.length - 1], d: [1, 0]};
};
const cut = (pts: V2[], u0: number, u1: number): V2[] => {
  const N = Math.max(2, Math.ceil(pts.length * (u1 - u0)) + 2);
  return Array.from({length: N}, (_, k) => along(pts, u0 + ((u1 - u0) * k) / (N - 1)).p);
};

/** raised arrowhead (prism): triangle top at z + three side quads */
const headPrism = (tip: V2, d: V2, size: number, z: number) => {
  const n: V2 = [-d[1], d[0]];
  const A: V2 = [tip[0] + d[0] * size * 0.55, tip[1] + d[1] * size * 0.55];
  const B: V2 = [tip[0] - d[0] * size * 0.45 + n[0] * size * 0.55, tip[1] - d[1] * size * 0.45 + n[1] * size * 0.55];
  const C: V2 = [tip[0] - d[0] * size * 0.45 - n[0] * size * 0.55, tip[1] - d[1] * size * 0.45 - n[1] * size * 0.55];
  const v = (q: V2, h: number) => W3([q[0], q[1], h]);
  const pos = [...v(A, z), ...v(B, z), ...v(C, z), ...v(A, 0.01), ...v(B, 0.01), ...v(C, 0.01)];
  const idx = [0, 1, 2, 0, 3, 4, 0, 4, 1, 1, 4, 5, 1, 5, 2, 2, 5, 3, 2, 3, 0];
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
};

const ring = (r0: number, r1: number) => <ringGeometry args={[r0, r1, 64]} />;

export const TelestrationBP: React.FC<{play: Play; pt: number; o: TeleOvBP & {age: number; dur: number}; a: number}> = ({play, pt, o, a}) => {
  switch (o.type) {
    case 'arrow3d': {
      const all = routeOf(play, o.player, o.t0, o.t1, 1 / 30);
      if (all.length < 2 || polyLen(all) < 0.2) return null;
      const col = o.color ?? (o.player.startsWith('X') ? RED : GOLD);
      const w = o.width ?? 0.26;
      const h = o.h ?? 0.07;
      const total = polyLen(all);
      // consume: the part already run disappears from under the player's feet
      let u0 = 0;
      if (o.consume && pt > o.t0) {
        const here = P(play, o.player, Math.min(pt, o.t1));
        let best = 0;
        let bd = 1e9;
        for (let k = 0; k <= 60; k++) {
          const q = along(all, k / 60).p;
          const dd = Math.hypot(q[0] - here[0], q[1] - here[1]);
          if (dd < bd) [bd, best] = [dd, k / 60];
        }
        u0 = best;
      }
      const u1 = o.draw ? eo(o.age / o.draw) : 1;
      if (u1 - u0 < 0.03) return null;
      const end = along(all, u1);
      const body = cut(all, u0, Math.max(u0 + 0.01, u1 - (w * 1.6) / total));
      // chevron glints: short bright bands that run toward the tip
      const glints = [0, 0.33, 0.66].map((k) => u0 + (u1 - u0) * ((o.age * 0.55 + k) % 1));
      return (
        <group>
          <mesh geometry={ribbon(body, w * 2.4, 0.009)} material={mat(col, 0.16 * a, true)} />
          <mesh geometry={ribbon(body, w, h)} material={mat(col, 0.95 * a)} />
          <mesh geometry={wall(body, w / 2, 0.01, h)} material={mat(col, 0.55 * a)} />
          <mesh geometry={wall(body, -w / 2, 0.01, h)} material={mat(col, 0.55 * a)} />
          <mesh geometry={headPrism(end.p, end.d, w * 3.1, h)} material={mat(col, 0.95 * a)} />
          {glints.map((g, i) => {
            if (g > u1 - 0.04) return null;
            const s = cut(all, Math.max(u0, g - 0.02), g);
            return <mesh key={i} geometry={ribbon(s, w * 0.9, h + 0.003)} material={mat('#FFF4D6', 0.75 * a, true)} />;
          })}
        </group>
      );
    }
    case 'debugCatch': {
      const b = sample(play, pt).ball;
      const ps = poseAt(play as never, o.player, pt, {holder: b.holder, pos: b.pos as V3}, [0, 1.575, 3.05]);
      const k = ps.dims.H / 2;
      const D = 0.115 * k, Wd = 0.9 * ps.dims.shW;
      const z0 = ps.pelvis[2], z1 = ps.chest[2];
      const mid: V3 = [(ps.pelvis[0] + ps.chest[0]) / 2, (ps.pelvis[1] + ps.chest[1]) / 2, (z0 + z1) / 2];
      const ph = ballPhase(play, pt).phase;
      const phCol: Record<string, string> = {OWNED_BY_PASSER: '#3BA0FF', RELEASED: '#FFFFFF', IN_FLIGHT: '#FFE14D', CONTACT: '#FF8A00', SECURED: '#36D17A', GATHER: '#B57BFF', HELD: '#3BA0FF', SHOT: '#FFFFFF', LOOSE: '#888888'};
      const b2 = sample(play, Math.min(play.duration, pt + 1 / 60)).ball.pos as V3;
      const dir: V3 = [b2[0] - b.pos[0], b2[1] - b.pos[1], b2[2] - b.pos[2]];
      const dl = Math.hypot(...dir) || 1;
      const seg = (p0: V3, p1: V3, col: string, w = 0.025) => {
        const a3 = new THREE.Vector3(...W3(p0)), b3 = new THREE.Vector3(...W3(p1));
        const len = a3.distanceTo(b3);
        const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), b3.clone().sub(a3).normalize());
        return <mesh position={a3.clone().add(b3).multiplyScalar(0.5)} quaternion={q} material={mat(col, 0.95)}><cylinderGeometry args={[w, w, len, 8]} /></mesh>;
      };
      const palms = [0, 1].map((i) => ps.wrist[i].map((w, j) => (w + ps.hand[i][j]) / 2) as V3);
      return (
        <group renderOrder={20}>
          {/* trunk: elliptic cylinder (half-depth D along the chest forward, half-width Wd), chest yaw */}
          <mesh position={W3(mid)} rotation={[0, ps.chestYaw, 0]} scale={[D, z1 - z0, Wd]}>
            <cylinderGeometry args={[1, 1, 1, 24, 1, true]} />
            <meshBasicMaterial color="#00E5FF" wireframe transparent opacity={0.55} depthTest={false} />
          </mesh>
          {/* ball sphere (physical radius), colour = ball phase */}
          <mesh position={W3(b.pos as V3)}>
            <sphereGeometry args={[BALL_R + 0.004, 16, 12]} />
            <meshBasicMaterial color={phCol[ph] ?? '#fff'} wireframe transparent opacity={0.9} depthTest={false} />
          </mesh>
          {palms.map((q, i) => (
            <mesh key={i} position={W3(q)}><sphereGeometry args={[0.03, 10, 8]} /><meshBasicMaterial color={i ? '#FF3B3B' : '#3BFF6A'} depthTest={false} /></mesh>
          ))}
          {seg([ps.pelvis[0], ps.pelvis[1], 0.05], [ps.pelvis[0] + Math.cos(ps.heading) * 0.9, ps.pelvis[1] + Math.sin(ps.heading) * 0.9, 0.05], '#00E5FF')}
          {seg([ps.chest[0], ps.chest[1], ps.chest[2]], [ps.chest[0] + Math.cos(ps.chestYaw) * 0.6, ps.chest[1] + Math.sin(ps.chestYaw) * 0.6, ps.chest[2]], '#FFFFFF', 0.015)}
          {dl > 1e-4 ? seg(b.pos as V3, [b.pos[0] + (dir[0] / dl) * 0.7, b.pos[1] + (dir[1] / dl) * 0.7, b.pos[2] + (dir[2] / dl) * 0.7], '#FF2BD6', 0.015) : null}
        </group>
      );
    }
    case 'lockRing': {
      const p = P(play, o.player, pt);
      const col = o.color ?? (o.player.startsWith('X') ? RED : GOLD);
      const s = o.size ?? 0.95;
      const k = eo(o.age / 0.32);
      const R = s * (1.9 - 0.9 * k);
      const rot = (1 - k) * 1.6 + o.age * 0.35;
      const snap = o.age > 0.32 && o.age < 0.5 ? 1 + 0.12 * Math.sin(((o.age - 0.32) / 0.18) * Math.PI) : 1;
      return (
        <group position={W3([p[0], p[1], 0.016])} rotation={[-Math.PI / 2, 0, 0]}>
          <mesh material={mat(col, 0.9 * a * k)} scale={s * 0.62 * snap}>{ring(0.88, 1.0)}</mesh>
          <mesh material={mat(col, 0.14 * a * k)} scale={s * 0.62}>
            <circleGeometry args={[0.88, 48]} />
          </mesh>
          {[0, 1, 2, 3].map((i) => (
            <mesh key={i} rotation={[0, 0, rot + (i * Math.PI) / 2]} material={mat(col, 0.95 * a)}>
              <ringGeometry args={[R * 0.8, R * 0.8 + 0.07, 16, 1, -0.32, 0.64]} />
            </mesh>
          ))}
        </group>
      );
    }
    case 'vision': {
      // eyes: defender -> ball (white) and defender -> man (coral); the angle between them
      const d = P(play, o.player, pt);
      const b = sample(play, clamp(pt, 0, play.duration)).ball.pos;
      const m = P(play, o.man, pt);
      const toB = Math.atan2(b[1] - d[1], b[0] - d[0]);
      const toM = Math.atan2(m[1] - d[1], m[0] - d[0]);
      let diff = toM - toB;
      while (diff > Math.PI) diff -= 2 * Math.PI;
      while (diff < -Math.PI) diff += 2 * Math.PI;
      const deg = Math.abs(diff) * 57.3;
      const split = o.split ?? 110;
      const conflict = clamp((deg - split + 15) / 30);
      const L = o.len ?? 2.6;
      const grow = eo(o.age / 0.4);
      const beam = (ang: number, len: number, col: string, wid: number) => {
        const tip: V2 = [d[0] + Math.cos(ang) * len * grow, d[1] + Math.sin(ang) * len * grow];
        const n: V2 = [-Math.sin(ang), Math.cos(ang)];
        const pts = [...W3([d[0] + n[0] * 0.05, d[1] + n[1] * 0.05, 0.02]), ...W3([d[0] - n[0] * 0.05, d[1] - n[1] * 0.05, 0.02]), ...W3([tip[0] + n[0] * wid, tip[1] + n[1] * wid, 0.02]), ...W3([tip[0] - n[0] * wid, tip[1] - n[1] * wid, 0.02])];
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
        g.setIndex([0, 1, 2, 1, 3, 2]);
        return g;
      };
      const dB = Math.min(L, Math.hypot(b[0] - d[0], b[1] - d[1]));
      const dM = Math.min(L, Math.hypot(m[0] - d[0], m[1] - d[1]));
      const arcCol = conflict > 0.5 ? RED : GOLD;
      const pulse = conflict > 0.5 ? 0.75 + 0.25 * Math.sin(o.age * 9) : 1;
      // arc between the two sight lines (sector ring), radius 0.9 m
      const a0 = diff >= 0 ? toB : toM;
      return (
        <group>
          <mesh geometry={beam(toB, dB, WHITE, 0.42)} material={mat(WHITE, 0.45 * a)} />
          <mesh geometry={ribbon([d, [d[0] + Math.cos(toB) * dB * grow, d[1] + Math.sin(toB) * dB * grow]], 0.1, 0.022, 0.18)} material={mat(WHITE, 0.95 * a)} />
          <mesh geometry={beam(toM, dM, CORAL, 0.42)} material={mat(CORAL, 0.45 * a)} />
          <mesh geometry={ribbon([d, [d[0] + Math.cos(toM) * dM * grow, d[1] + Math.sin(toM) * dM * grow]], 0.1, 0.022, 0.18)} material={mat(CORAL, 0.95 * a)} />
          <mesh position={W3([d[0], d[1], 0.024])} rotation={[-Math.PI / 2, 0, 0]} material={mat(arcCol, 0.85 * a * pulse * grow)}>
            <ringGeometry args={[0.8, 1.0, 48, 1, a0, Math.abs(diff) * grow]} />
          </mesh>
          <mesh position={W3([d[0], d[1], 0.023])} rotation={[-Math.PI / 2, 0, 0]} material={mat(arcCol, 0.3 * a * pulse * grow)}>
            <circleGeometry args={[0.82, 48, a0, Math.abs(diff) * grow]} />
          </mesh>
        </group>
      );
    }
    case 'tether': {
      const A = P(play, o.a, pt);
      const B = P(play, o.b, pt);
      const L = Math.hypot(B[0] - A[0], B[1] - A[1]);
      const rest = o.rest ?? 1.5;
      const snapAt = o.snap ?? 3.2;
      const s = clamp((L - rest) / (snapAt - rest));
      const col = s > 0.5 ? CORAL : WHITE;
      const w = 0.12 * (1 - 0.6 * s);
      const grow = eo(o.age / 0.35);
      const N = 28;
      // a slight sag sideways (elastic), shrinking as it stretches
      const nx = -(B[1] - A[1]) / (L || 1);
      const ny = (B[0] - A[0]) / (L || 1);
      const pts: V2[] = Array.from({length: N}, (_, k) => {
        const u = (k / (N - 1)) * grow;
        const sag = Math.sin(Math.PI * u) * 0.18 * (1 - s);
        return [A[0] + (B[0] - A[0]) * u + nx * sag, A[1] + (B[1] - A[1]) * u + ny * sag];
      });
      const broken = L > snapAt;
      const gapU = broken ? clamp((L - snapAt) / 1.5, 0.12, 0.4) : 0;
      const left = broken ? pts.filter((_, k) => k / (N - 1) < 0.5 - gapU / 2) : pts;
      const right = broken ? pts.filter((_, k) => k / (N - 1) > 0.5 + gapU / 2) : [];
      return (
        <group>
          {left.length > 1 && <mesh geometry={ribbon(left, w, 0.018)} material={mat(col, 0.95 * a)} />}
          {right.length > 1 && <mesh geometry={ribbon(right, w, 0.018)} material={mat(col, 0.95 * a)} />}
          {[A, B].map((q, i) => (
            <mesh key={i} position={W3([q[0], q[1], 0.017])} rotation={[-Math.PI / 2, 0, 0]} material={mat(col, 0.9 * a)}>
              <circleGeometry args={[0.09, 20]} />
            </mesh>
          ))}
        </group>
      );
    }
    case 'ghost': {
      const g: V2 = o.at ?? P(play, o.player!, o.t ?? 0);
      const col = o.color ?? (o.player?.startsWith('X') ? CORAL : GOLD);
      const k = eo(o.age / 0.3);
      const now = o.player ? P(play, o.player, pt) : g;
      return (
        <group>
          <mesh position={W3([g[0], g[1], 0.014])} rotation={[-Math.PI / 2, 0, 0]} material={mat(col, 0.85 * a * k)} scale={0.5}>
            {ring(0.82, 1.0)}
          </mesh>
          <mesh position={W3([g[0], g[1], 0.013])} rotation={[-Math.PI / 2, 0, 0]} material={mat(col, 0.16 * a * k)} scale={0.5}>
            <circleGeometry args={[0.82, 40]} />
          </mesh>
          <mesh position={W3([g[0], g[1], 0.95 * k])} scale={[1, k, 1]} material={mat(col, 0.16 * a)}>
            <cylinderGeometry args={[0.22, 0.27, 1.9, 24, 1, true]} />
          </mesh>
          {o.link && Math.hypot(now[0] - g[0], now[1] - g[1]) > 0.6 && <mesh geometry={ribbon([g, now], 0.05, 0.02, 0.2)} material={mat(col, 0.8 * a)} />}
        </group>
      );
    }
    case 'ballPath': {
      const e = play.ball.find((x) => x.type === 'pass' && x.from === o.src && x.to === o.dst);
      if (!e || e.type !== 'pass') return null;
      const N = 26;
      const pts: V3[] = Array.from({length: N}, (_, k) => sample(play, e.t0 + ((e.t1 - e.t0) * (k + 0.5)) / N).ball.pos as V3);
      const show = o.draw ? eo(o.age / o.draw) : 1;
      const col = o.color ?? '#FFE3A3';
      let lo = 0;
      pts.forEach((q, k) => {
        if (q[2] < pts[lo][2]) lo = k;
      });
      // (2026-11-27, IQ 02) a ballistic bounce pass hits the floor where its own physics put it (the lowest sample)
      const bounce = e.style === 'bounce' ? ((e as {ballistic?: boolean}).ballistic ? pts[lo] : sample(play, e.t0 + ((e.t1 - e.t0) * 0.62)).ball.pos) : undefined;
      // dots already passed by the ball fade out (the path is consumed by the flight)
      const flown = clamp((pt - e.t0) / (e.t1 - e.t0));
      return (
        <group>
          {pts.map((q, k) => {
            const u = (k + 0.5) / N;
            if (u > show) return null;
            const op = u < flown ? 0.15 : 0.9;
            return (
              <mesh key={k} position={W3(q)} material={mat(col, op * a, true)}>
                <sphereGeometry args={[0.055, 10, 8]} />
              </mesh>
            );
          })}
          {bounce && show > 0.62 && (
            <group position={W3([bounce[0], bounce[1], 0.02])} rotation={[-Math.PI / 2, 0, 0]}>
              <mesh material={mat(col, 0.9 * a)} scale={0.32 + 0.06 * Math.sin(o.age * 8)}>
                {ring(0.8, 1.0)}
              </mesh>
              <mesh material={mat(col, 0.25 * a, true)} scale={0.32}>
                <circleGeometry args={[0.8, 32]} />
              </mesh>
            </group>
          )}
        </group>
      );
    }
    case 'openLane': {
      const col = o.color ?? GOLD;
      const tg: V2 = typeof o.target === 'string' ? P(play, o.target, pt) : o.target ?? [0, 1.575];
      const base: V2 = typeof o.anchor === 'string' ? P(play, o.anchor, pt) : o.anchor;
      const dx = tg[0] - base[0];
      const dy = tg[1] - base[1];
      const L = Math.hypot(dx, dy);
      if (L < 0.6) return null;
      const ux = dx / L;
      const uy = dy / L;
      const g0 = typeof o.anchor === 'string' ? (o.gap ?? 0.45) : 0;
      const s0: V2 = [base[0] + ux * g0, base[1] + uy * g0];
      const grow = o.draw ? eo(o.age / o.draw) : 1;
      const s1: V2 = [s0[0] + (tg[0] - s0[0]) * grow, s0[1] + (tg[1] - s0[1]) * grow];
      const w0 = o.width ?? 1.5;
      const w1 = (o.tip ?? 0.7) * grow + w0 * (1 - grow);
      const nx = -uy;
      const ny = ux;
      const quad = (wa: number, wb: number, z: number) => {
        const g = new THREE.BufferGeometry();
        const v = [
          ...W3([s0[0] + (nx * wa) / 2, s0[1] + (ny * wa) / 2, z]), ...W3([s0[0] - (nx * wa) / 2, s0[1] - (ny * wa) / 2, z]),
          ...W3([s1[0] + (nx * wb) / 2, s1[1] + (ny * wb) / 2, z]), ...W3([s1[0] - (nx * wb) / 2, s1[1] - (ny * wb) / 2, z]),
        ];
        g.setAttribute('position', new THREE.Float32BufferAttribute(v, 3));
        g.setIndex([0, 1, 2, 1, 3, 2]);
        return g;
      };
      const els: React.ReactNode[] = [
        <mesh key="soft" geometry={quad(w0 * 1.25, w1 * 1.25, 0.011)} material={mat(col, 0.12 * a, true)} renderOrder={2} />,
        <mesh key="core" geometry={quad(w0, w1, 0.013)} material={mat(col, 0.22 * a, true)} renderOrder={3} />,
        <mesh key="edgeL" geometry={ribbon([[s0[0] + (nx * w0) / 2, s0[1] + (ny * w0) / 2], [s1[0] + (nx * w1) / 2, s1[1] + (ny * w1) / 2]], 0.05, 0.016)} material={mat(col, 0.8 * a)} renderOrder={4} />,
        <mesh key="edgeR" geometry={ribbon([[s0[0] - (nx * w0) / 2, s0[1] - (ny * w0) / 2], [s1[0] - (nx * w1) / 2, s1[1] - (ny * w1) / 2]], 0.05, 0.016)} material={mat(col, 0.8 * a)} renderOrder={4} />,
      ];
      if (o.chevrons !== false && grow > 0.6) {
        const run = (o.age * 1.6) % 1;
        for (let k = 0; k < 3; k++) {
          const u = ((run + k / 3) % 1) * grow;
          const c: V2 = [s0[0] + (tg[0] - s0[0]) * u, s0[1] + (tg[1] - s0[1]) * u];
          const cw = 0.32;
          const pts: V2[] = [[c[0] + nx * cw - ux * 0.22, c[1] + ny * cw - uy * 0.22], c, [c[0] - nx * cw - ux * 0.22, c[1] - ny * cw - uy * 0.22]];
          els.push(<mesh key={'ch' + k} geometry={ribbon(pts, 0.07, 0.017)} material={mat(WHITE, 0.7 * a * Math.sin(Math.PI * ((run + k / 3) % 1)))} renderOrder={5} />);
        }
      }
      return <group>{els}</group>;
    }
    case 'motionTrail': {
      const len = o.len ?? 0.6;
      const col = o.color ?? (o.player.startsWith('X') ? CORAL : GOLD);
      const segs = 6;
      const w = o.width ?? 0.34;
      const els: React.ReactNode[] = [];
      for (let k = 0; k < segs; k++) {
        const t1 = pt - (len * k) / segs;
        const t0 = pt - (len * (k + 1)) / segs;
        if (t1 <= 0) break;
        const pts = routeOf(play, o.player, Math.max(0, t0), Math.min(play.duration, t1), 1 / 60);
        if (polyLen(pts) < 0.05) continue;
        els.push(<mesh key={k} geometry={ribbon(pts, w * (1 - k / segs * 0.6), 0.015)} material={mat(col, 0.55 * (1 - k / segs) * a, true)} />);
      }
      return <group>{els}</group>;
    }
    default:
      return null;
  }
};
