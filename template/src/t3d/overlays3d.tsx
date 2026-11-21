// E2A 3D engine — tactical graphics that live INSIDE the 3D scene (same camera, same perspective,
// same depth as the players): floor rings, progressive route ribbons with arrowheads, staggered
// screen markers, animated passing lanes, separation bands, open-space zones, denial wedges.
// Colours: offence gold, defence red, neutral white. Everything eases in and out (no popping).
import React from 'react';
import * as THREE from 'three';
import type {V2, V3} from '../tactical/geometry.ts';
import type {Play} from '../tactical/play.ts';
import {posAt, routeOf, sample} from '../tactical/play.ts';
import {W3} from './Athlete';
import {poseAt} from './rig.ts';
import type {PlayWithActions} from './rig.ts';
import type {ChoreoPlay} from './choreo.ts';
import type {TeleOv} from './telestration3d';
import {PassTravel, Telestration3D, floorQuad, textTex, yawAxes} from './telestration3d';
import type {TeleOvBP} from './telestration3d-bp';
import {TelestrationBP} from './telestration3d-bp';
import type {ZoneGridOv} from './zone3d';
import {ZoneGrid3D} from './zone3d';
import type {CoverageFamilyOv} from './coverage3d';
import {Coverage3D, CoverageFx3D} from './coverage3d';

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
  | {type: 'ring'; player: string; color?: string; pulse?: boolean; size?: number}
  /** consume (2026-11-19): the route ahead of the player only (born under him, eaten as he runs it) */
  | {type: 'route'; player: string; t0: number; t1: number; color?: string; draw?: number; dashed?: boolean; width?: number; pts?: V2[]; trail?: boolean; consume?: boolean;
     /** 2026-11-21 (BLOB V2 fork): a plated floor label at the arrow tip, read from camera yaw `labelYaw` */
     label?: string; labelYaw?: number; labelOffset?: V2; labelSize?: number}
  | {type: 'screen'; player?: string; at?: V2; n: number; facing?: number}
  /** travel (2026-11-19): seconds for a lit segment to run from the passer to the catch point; dstAt = play time of the catch */
  | {type: 'passLane'; src: string; dst: string | V2; color?: string; travel?: number; dstAt?: number}
  /** 2026-11-19 broadcast telestration (telestration3d.tsx): spot, ripple, floorText, ballTrail, ghostTrail */
  | TeleOv
  /** 2026-11-19 telestration v2 (Blind Pig, telestration3d-bp.tsx): arrow3d, lockRing, vision, tether, ghost, ballPath, motionTrail */
  | TeleOvBP
  | {type: 'separation'; a: string; b: string; color?: string}
  | {type: 'openSpace'; at: V2; r: number; rx?: number; angle?: number; color?: string}
  | {type: 'deny'; player: string; toward: V2; color?: string}
  | {type: 'blocked'; at: V2; color?: string}
  /** 2026-11-18 (Break the 3-2): defensive WALL tied to the real defenders (see wall3d below) */
  | WallOv
  /** floor light (radial) at a spot or under a player; hoop:true also lights the rim */
  | {type: 'glow'; at?: V2; player?: string; r?: number; color?: string; hoop?: boolean; strength?: number}
  /** 2026-11-18 (Eurostep): shoe print pinned to the floor where a COUNTED step lands (n = 1, 2 after the gather);
   *  it appears on the contact frame (play time), so rewinds and slow motion keep it honest. opacity dims it. */
  | {type: 'print'; player: string; n: number; color?: string; opacity?: number}
  /** coral hip axis at hip height (defender's hip signal) with a small arrow where the hips point */
  | {type: 'hipMark'; player: string; color?: string}
  /** 2026-11-21 (2-3 Zone): ZoneGridMorph, five zone areas that move with their defenders (zone3d.tsx) */
  | ZoneGridOv
  /** 2026-11-21 (2-3 Zone V2): E2A Dynamic Defensive Coverage + its effects (coverage3d.tsx) */
  | CoverageFamilyOv;

/** counted steps of a choreo player: the first plants after the gather, in order */
export const countedSteps = (play: Play, id: string) => {
  const c = (play as unknown as ChoreoPlay).choreo?.[id];
  if (!c) return [];
  return c.steps.filter((s) => s.land > c.ev.gather).sort((a, b) => a.land - b.land);
};

const printTex = (() => {
  const cache = new Map<string, THREE.Texture>();
  return (foot: number, label: string, color: string) => {
    const key = `${foot}|${label}|${color}`;
    const hit = cache.get(key);
    if (hit) return hit;
    const c = document.createElement('canvas');
    c.width = 256;
    c.height = 512;
    const g = c.getContext('2d')!;
    g.translate(128, 256);
    if (foot === 1) g.scale(-1, 1);
    // sole outline (toe up): wide forefoot, waist on the inside, round heel
    const sole = () => {
      g.beginPath();
      g.moveTo(-8, -238);
      g.bezierCurveTo(60, -240, 98, -170, 92, -80);
      g.bezierCurveTo(88, -10, 66, 40, 62, 110);
      g.bezierCurveTo(58, 190, 40, 236, -6, 238);
      g.bezierCurveTo(-58, 238, -70, 190, -66, 120);
      g.bezierCurveTo(-62, 60, -30, 20, -50, -60);
      g.bezierCurveTo(-74, -150, -72, -236, -8, -238);
      g.closePath();
    };
    sole();
    g.fillStyle = color;
    g.globalAlpha = 0.62;
    g.fill();
    g.globalAlpha = 1;
    g.lineWidth = 16;
    g.strokeStyle = '#FFF6DF';
    g.stroke();
    if (foot === 1) g.scale(-1, 1);
    g.fillStyle = '#0B1C3D';
    g.font = '900 190px Anton, Inter, sans-serif';
    g.textAlign = 'center';
    g.textBaseline = 'middle';
    g.fillText(label, 0, -70);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    cache.set(key, t);
    return t;
  };
})();

/** Zone wall: translucent panels between consecutive defenders (chain), floor to ~waist height, ice-white edges and
 *  a fine grid. Everything follows the engine's real positions at the current play time.
 *  - draw: seconds to draw the top edge along the chain (the fill fades in after it); rise: seconds to raise the panels
 *  - opacity: global multiplier (dim a wall while the focus is elsewhere)
 *  - pass: the pass whose ball path defines WHERE the gap / crack / break happen (first crossing of the chain)
 *  - open: hole that grows on the crossed panel, centred on the crossing point, from play time pt0 to pt1 (width w, m)
 *  - crack: short glowing crack at the crossing (play time of the crossing), lasting `dur` s
 *  - shatter: the panel breaks in a small zone (radius r) around the crossing; n seeded fragments fly for `dur` s */
export type WallOv = {type: 'wall'; chain: string[]; h?: number; color?: string; draw?: number; rise?: number; opacity?: number;
  pass?: {from: string; to: string}; open?: {pt0: number; pt1: number; w?: number}; crack?: {dur?: number};
  shatter?: {r?: number; n?: number; seed?: number; dur?: number; at?: number}; grid?: boolean};

export type LiveOv3 = Ov3 & {age: number; dur: number; fin?: number; fout?: number};

export const ICE3 = '#C8ECFF';

/** first crossing of a pass's ball path with a chain of defenders: segment index, fraction along it, play time, height */
type Cross = {seg: number; u: number; pt: number; z: number; dir: V2};
const crossCache = new Map<string, Cross | null>();
export const wallCrossing = (play: Play, chain: string[], from: string, to: string): Cross | null => {
  const key = `${play.id}|${chain.join(',')}|${from}>${to}`;
  if (crossCache.has(key)) return crossCache.get(key)!;
  const ev = play.ball.find((e) => e.type === 'pass' && e.from === from && e.to === to) as {t0: number; t1: number} | undefined;
  let res: Cross | null = null;
  if (ev) {
    const P = (id: string, t: number) => posAt(play.tracks[id], t);
    const side = (a: V2, b: V2, q: V2) => (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]);
    let prev = sample(play, ev.t0).ball.pos;
    const step = 1 / 240;
    for (let t = ev.t0 + step; t <= ev.t1 && !res; t += step) {
      const cur = sample(play, t).ball.pos;
      for (let i = 0; i + 1 < chain.length && !res; i++) {
        const a = P(chain[i], t);
        const b = P(chain[i + 1], t);
        const s0 = side(a, b, [prev[0], prev[1]]);
        const s1 = side(a, b, [cur[0], cur[1]]);
        if (s0 === 0 || Math.sign(s0) === Math.sign(s1)) continue;
        const f = s0 / (s0 - s1);
        const q: V2 = [prev[0] + (cur[0] - prev[0]) * f, prev[1] + (cur[1] - prev[1]) * f];
        const L2 = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2 || 1;
        const u = ((q[0] - a[0]) * (b[0] - a[0]) + (q[1] - a[1]) * (b[1] - a[1])) / L2;
        if (u < 0 || u > 1) continue;
        const d: V2 = [cur[0] - prev[0], cur[1] - prev[1]];
        const dl = Math.hypot(d[0], d[1]) || 1;
        res = {seg: i, u, pt: t - step + step * f, z: prev[2] + (cur[2] - prev[2]) * f, dir: [d[0] / dl, d[1] / dl]};
      }
      prev = cur;
    }
  }
  crossCache.set(key, res);
  return res;
};

const gridTex = (() => {
  let t: THREE.Texture | null = null;
  return () => {
    if (t) return t;
    const c = document.createElement('canvas');
    c.width = 64;
    c.height = 64;
    const g = c.getContext('2d')!;
    g.clearRect(0, 0, 64, 64);
    g.fillStyle = 'rgba(255,255,255,1)';
    g.fillRect(0, 0, 64, 3);
    g.fillRect(0, 0, 3, 64);
    t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.anisotropy = 4;
    return t;
  };
})();

const glowTex = (() => {
  let t: THREE.Texture | null = null;
  return () => {
    if (t) return t;
    const c = document.createElement('canvas');
    c.width = 128;
    c.height = 128;
    const g = c.getContext('2d')!;
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.45, 'rgba(255,255,255,0.55)');
    gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr;
    g.fillRect(0, 0, 128, 128);
    t = new THREE.CanvasTexture(c);
    return t;
  };
})();

/** quad in the vertical plane of a panel: s along the panel (m from A), z height */
const vquad = (A: V2, d: V2, s0: number, s1: number, z0: number, z1: number, grid = false) => {
  const p = (s: number, z: number) => W3([A[0] + d[0] * s, A[1] + d[1] * s, z]);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute([...p(s0, z0), ...p(s1, z0), ...p(s1, z1), ...p(s0, z1)], 3));
  if (grid) {
    const k = 1 / 0.26; // one grid cell every 26 cm
    g.setAttribute('uv', new THREE.Float32BufferAttribute([s0 * k, z0 * k, s1 * k, z0 * k, s1 * k, z1 * k, s0 * k, z1 * k], 2));
  }
  g.setIndex([0, 1, 2, 0, 2, 3]);
  return g;
};

/** thin strip along a polyline drawn in a panel's plane (local (s, z) coordinates) */
const vstrip = (A: V2, d: V2, pts: [number, number][], w: number) => {
  const pos: number[] = [];
  const idx: number[] = [];
  pts.forEach((q, i) => {
    const a = pts[Math.max(0, i - 1)];
    const b = pts[Math.min(pts.length - 1, i + 1)];
    let ds = b[0] - a[0];
    let dz = b[1] - a[1];
    const L = Math.hypot(ds, dz) || 1;
    ds /= L;
    dz /= L;
    const ns = -dz * (w / 2);
    const nz = ds * (w / 2);
    pos.push(...W3([A[0] + d[0] * (q[0] + ns), A[1] + d[1] * (q[0] + ns), q[1] + nz]));
    pos.push(...W3([A[0] + d[0] * (q[0] - ns), A[1] + d[1] * (q[0] - ns), q[1] - nz]));
    if (i > 0) {
      const k = i * 2;
      idx.push(k - 2, k - 1, k, k - 1, k + 1, k);
    }
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
};

const rng = (seed: number) => {
  let x = seed >>> 0 || 1;
  return () => {
    x ^= x << 13;
    x ^= x >>> 17;
    x ^= x << 5;
    return ((x >>> 0) % 100000) / 100000;
  };
};

const Wall3D: React.FC<{play: Play; pt: number; o: WallOv & {age: number; dur: number}; a: number}> = ({play, pt, o, a}) => {
  const ptc = Math.max(0, Math.min(play.duration, pt));
  const H = o.h ?? 1.05;
  const col = o.color ?? ICE3;
  const op = (o.opacity ?? 1) * a;
  const rise = o.rise ? easeOut(o.age / o.rise) : 1;
  const draw = o.draw ? easeOut(o.age / o.draw) : 1;
  const fillIn = o.draw ? clamp((o.age - o.draw * 0.55) / 0.35) : 1;
  const pts = o.chain.map((id) => posAt(play.tracks[id], ptc));
  const segs = pts.slice(1).map((b, i) => {
    const A = pts[i];
    const L = Math.hypot(b[0] - A[0], b[1] - A[1]) || 1e-3;
    return {A, B: b, L, d: [(b[0] - A[0]) / L, (b[1] - A[1]) / L] as V2};
  });
  const total = segs.reduce((x, s) => x + s.L, 0);
  const cr = o.pass ? wallCrossing(play, o.chain, o.pass.from, o.pass.to) : null;
  // holes per segment, in metres along the segment
  const holes: [number, number][][] = segs.map(() => []);
  let hs = 0;
  if (cr && o.open) {
    const g = clamp((ptc - o.open.pt0) / Math.max(0.01, o.open.pt1 - o.open.pt0));
    hs = easeOut(g);
    const S = segs[cr.seg];
    const w = (o.open.w ?? 1.2) * hs;
    if (w > 0.01) holes[cr.seg].push([Math.max(0, cr.u * S.L - w / 2), Math.min(S.L, cr.u * S.L + w / 2)]);
  }
  const shT = o.shatter ? (o.shatter.at ?? cr?.pt ?? 1e9) : 1e9;
  const shAge = ptc - shT;
  if (cr && o.shatter && shAge >= 0) {
    const S = segs[cr.seg];
    const r = o.shatter.r ?? 0.6;
    holes[cr.seg].push([Math.max(0, cr.u * S.L - r), Math.min(S.L, cr.u * S.L + r)]);
  }
  const pieces = (L: number, hl: [number, number][]) => {
    let out: [number, number][] = [[0, L]];
    for (const [h0, h1] of hl) out = out.flatMap(([p0, p1]) => (h1 <= p0 || h0 >= p1 ? [[p0, p1]] : ([[p0, h0], [h1, p1]] as [number, number][]).filter(([x, y]) => y - x > 0.02)));
    return out;
  };
  const els: React.ReactNode[] = [];
  let acc = 0;
  const gridMat = (alpha: number) => new THREE.MeshBasicMaterial({color: col, map: gridTex(), transparent: true, opacity: alpha, depthWrite: false, toneMapped: false, side: THREE.DoubleSide});
  segs.forEach((S, i) => {
    const visTo = clamp((draw * total - acc) / S.L) * S.L; // drawn length of this segment
    acc += S.L;
    const zt = H * rise;
    for (const [p0, p1raw] of pieces(S.L, holes[i])) {
      const p1 = Math.min(p1raw, visTo);
      if (p1 - p0 < 0.02) continue;
      if (fillIn > 0) {
        els.push(<mesh key={`f${i}-${p0}`} geometry={vquad(S.A, S.d, p0, p1, 0, zt)} material={basic(col, 0.2 * op * fillIn)} />);
        if (o.grid !== false) els.push(<mesh key={`g${i}-${p0}`} geometry={vquad(S.A, S.d, p0, p1, 0, zt, true)} material={gridMat(0.32 * op * fillIn)} />);
        // soft glow just under the top edge (gives the panel its volume)
        els.push(<mesh key={`h${i}-${p0}`} geometry={vquad(S.A, S.d, p0, p1, zt * 0.72, zt)} material={basic(col, 0.22 * op * fillIn)} />);
      }
      // top edge: vertical strip (low cameras) + horizontal ribbon at the top (overhead cameras)
      els.push(<mesh key={`t${i}-${p0}`} geometry={vquad(S.A, S.d, p0, p1, zt - 0.035, zt + 0.035)} material={basic('#F4FBFF', 1.0 * op)} />);
      els.push(<mesh key={`r${i}-${p0}`} geometry={ribbon([[S.A[0] + S.d[0] * p0, S.A[1] + S.d[1] * p0], [S.A[0] + S.d[0] * p1, S.A[1] + S.d[1] * p1]], 0.07, zt)} material={basic('#F4FBFF', 0.95 * op)} />);
      // floor line + floor glow
      els.push(<mesh key={`b${i}-${p0}`} geometry={ribbon([[S.A[0] + S.d[0] * p0, S.A[1] + S.d[1] * p0], [S.A[0] + S.d[0] * p1, S.A[1] + S.d[1] * p1]], 0.07, 0.014)} material={basic('#F4FBFF', 0.9 * op)} />);
      els.push(<mesh key={`bg${i}-${p0}`} geometry={ribbon([[S.A[0] + S.d[0] * p0, S.A[1] + S.d[1] * p0], [S.A[0] + S.d[0] * p1, S.A[1] + S.d[1] * p1]], 0.45, 0.012)} material={basic(col, 0.22 * op * fillIn)} />);
    }
  });
  // the opening: gold jambs on both sides of the hole
  if (cr && o.open && hs > 0.02 && shAge < 0) {
    const S = segs[cr.seg];
    const w = (o.open.w ?? 1.2) * hs;
    for (const sg of [-1, 1]) {
      const s = Math.max(0, Math.min(S.L, cr.u * S.L + (sg * w) / 2));
      els.push(<mesh key={`j${sg}`} geometry={vquad(S.A, S.d, s - 0.02, s + 0.02, 0, H * rise)} material={basic(GOLD3, 0.95 * op)} />);
    }
  }
  // crack: short branching gold-white lines from the crossing point (deterministic)
  if (cr && o.crack) {
    const ca = ptc - cr.pt;
    const cd = o.crack.dur ?? 0.55;
    if (ca >= -0.02 && ca < cd) {
      const S = segs[cr.seg];
      const sc = cr.u * S.L;
      const zc = Math.max(0.25, Math.min(H * 0.8, cr.z));
      const grow = easeOut(clamp((ca + 0.02) / 0.12));
      const fadeC = 1 - clamp((ca - cd * 0.55) / (cd * 0.45));
      const R = rng(7);
      for (let k = 0; k < 8; k++) {
        const ang = (k / 8) * Math.PI * 2 + (R() - 0.5) * 0.5;
        let s = sc;
        let z = zc;
        const line: [number, number][] = [[s, z]];
        const len = (0.35 + R() * 0.35) * grow;
        for (let j = 0; j < 3; j++) {
          const aj = ang + (R() - 0.5) * 0.9;
          s += Math.cos(aj) * len / 3;
          z = Math.max(0.01, Math.min(H, z + Math.sin(aj) * len / 3));
          line.push([s, z]);
        }
        els.push(<mesh key={`c${k}`} geometry={vstrip(S.A, S.d, line, 0.028)} material={basic('#FFF3D6', 0.95 * fadeC * a)} />);
      }
      els.push(<mesh key="cg" position={W3([S.A[0] + S.d[0] * sc, S.A[1] + S.d[1] * sc, zc])} rotation={[0, Math.atan2(S.d[1], S.d[0]), 0]} material={new THREE.MeshBasicMaterial({color: GOLD3, map: glowTex(), transparent: true, opacity: 0.8 * fadeC * a, depthWrite: false, toneMapped: false, side: THREE.DoubleSide})}>
        <planeGeometry args={[0.9 * grow + 0.05, 0.9 * grow + 0.05]} />
      </mesh>);
    }
  }
  // shatter: seeded fragments from the crossing zone, carried along the ball's direction, gravity, fade
  if (cr && o.shatter && shAge >= 0 && shAge < (o.shatter.dur ?? 0.42)) {
    const S = segs[cr.seg];
    const sc = cr.u * S.L;
    const r = o.shatter.r ?? 0.6;
    const n = o.shatter.n ?? 14;
    const R = rng(o.shatter.seed ?? 32);
    const life = o.shatter.dur ?? 0.42;
    const fa = 1 - clamp((shAge - life * 0.35) / (life * 0.65));
    const nrm: V2 = [-S.d[1], S.d[0]];
    const sideOfBall = Math.sign(nrm[0] * cr.dir[0] + nrm[1] * cr.dir[1]) || 1;
    for (let k = 0; k < n; k++) {
      const s0 = sc + (R() * 2 - 1) * r * 0.9;
      const z0 = 0.08 + R() * (H - 0.12);
      const sp = 1.4 + R() * 2.2;
      const vN = sideOfBall * sp;
      const vS = (s0 - sc) / r * (0.8 + R());
      const vZ = 0.4 + R() * 1.6;
      const tt = shAge;
      const s = s0 + vS * tt;
      const off = vN * tt;
      const z = Math.max(0.02, z0 + vZ * tt - 4.9 * tt * tt);
      const x = S.A[0] + S.d[0] * s + nrm[0] * off;
      const y = S.A[1] + S.d[1] * s + nrm[1] * off;
      const size = 0.07 + R() * 0.1;
      const rot = R() * 6 + tt * (6 + R() * 10);
      els.push(<mesh key={`s${k}`} position={W3([x, y, z])} rotation={[rot, rot * 0.7 + Math.atan2(S.d[0], S.d[1]), rot * 0.4]} material={basic(k % 4 === 0 ? '#FFE7AE' : col, 0.85 * fa * a)}>
        <circleGeometry args={[size, 3]} />
      </mesh>);
    }
    // brief flash at the break point
    const fl = 1 - clamp(shAge / 0.25);
    els.push(<mesh key="sf" position={W3([S.A[0] + S.d[0] * sc, S.A[1] + S.d[1] * sc, Math.max(0.3, Math.min(H * 0.8, cr.z))])} rotation={[0, Math.atan2(S.d[1], S.d[0]), 0]} material={new THREE.MeshBasicMaterial({color: GOLD3, map: glowTex(), transparent: true, opacity: 0.7 * fl * a, depthWrite: false, toneMapped: false, side: THREE.DoubleSide})}>
      <planeGeometry args={[1.3, 1.3]} />
    </mesh>);
  }
  return <group>{els}</group>;
};

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
        const a = fade(o.age, o.dur, o.fin ?? 0.25, o.fout ?? 0.25);
        if (a <= 0.001) return null;
        switch (o.type) {
          case 'ring': {
            const p = P(o.player);
            const pulse = o.pulse ? 1 + 0.12 * Math.sin(o.age * 7) : 1;
            const grow = (0.6 + 0.4 * easeOut(o.age / 0.3)) * (o.size ?? 1);
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
            const t0 = o.consume ? Math.max(o.t0, Math.min(pt, o.t1)) : o.t0;
            if (t1 - t0 < 0.05 && !o.pts) return null;
            const pts = o.pts ?? routeOf(play, o.player, t0, t1, 1 / 30);
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
                {o.label && u > 0.85 && (() => {
                  const t = textTex(o.label, col, true);
                  const {right, up} = yawAxes(o.labelYaw ?? 0);
                  const h = o.labelSize ?? 0.5;
                  const c: V2 = [tip[0] + (o.labelOffset?.[0] ?? 0), tip[1] + (o.labelOffset?.[1] ?? 0)];
                  return <mesh geometry={floorQuad(c, right, up, h * t.aspect, h, 0.022)} material={new THREE.MeshBasicMaterial({color: '#FFFFFF', map: t.tex, transparent: true, opacity: 0.97 * a * Math.min(1, (u - 0.85) / 0.15), depthWrite: false, toneMapped: false, side: THREE.DoubleSide})} />;
                })()}
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
            if (o.travel) return <PassTravel key={i} play={play} pt={pt} src={o.src} dst={o.dst} dstAt={o.dstAt} travel={o.travel} age={o.age} a={a} color={o.color} ribbon={ribbon} arrowHead={arrowHead} />;
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
          case 'zoneGrid':
            return <ZoneGrid3D key={i} play={play} pt={pt} o={o} a={a} />;
          case 'coverage':
            return <Coverage3D key={i} play={play} pt={pt} o={o} a={a} />;
          case 'covLink':
          case 'gapReveal':
          case 'covHull':
          case 'closeout':
          case 'shotWindow':
          case 'covGhost':
            return <CoverageFx3D key={i} play={play} pt={pt} o={o} a={a} />;
          case 'wall':
            return <Wall3D key={i} play={play} pt={pt} o={o} a={a} />;
          case 'print': {
            const st = countedSteps(play, o.player)[o.n - 1];
            if (!st || pt < st.land - 1 / 60) return null;
            const since = pt - st.land;
            const pop = since < 0.22 ? 1 + 0.35 * Math.sin((Math.PI * Math.max(0, since)) / 0.22) : 1;
            const op = clamp((since + 1 / 60) / 0.06) * a * (o.opacity ?? 1);
            return (
              <group key={i} position={W3([st.at[0], st.at[1], 0.017])} rotation={[-Math.PI / 2, 0, st.yaw - Math.PI / 2]} scale={pop}>
                <mesh material={new THREE.MeshBasicMaterial({map: printTex(st.foot, String(o.n), o.color ?? GOLD3), transparent: true, opacity: op, depthWrite: false, toneMapped: false})}>
                  <planeGeometry args={[0.2, 0.4]} />
                </mesh>
                <mesh position={[0, 0, -0.002]} material={new THREE.MeshBasicMaterial({color: o.color ?? GOLD3, map: glowTex(), transparent: true, opacity: 0.55 * op, depthWrite: false, toneMapped: false, blending: THREE.AdditiveBlending})}>
                  <planeGeometry args={[0.62, 0.8]} />
                </mesh>
              </group>
            );
          }
          case 'hipMark': {
            const b = sample(play, pt).ball;
            const ps = poseAt(play as PlayWithActions, o.player, pt, {holder: b.holder, pos: b.pos}, [0, 1.575, 3.05]);
            const col = o.color ?? '#F06A55';
            const hz = ps.pelvis[2] + 0.02;
            const fwdH: V2 = [Math.cos(ps.heading), Math.sin(ps.heading)];
            const tip: V2 = [ps.pelvis[0] + fwdH[0] * 0.42, ps.pelvis[1] + fwdH[1] * 0.42];
            return (
              <group key={i}>
                <mesh position={W3([ps.pelvis[0], ps.pelvis[1], hz])} rotation={[0, ps.heading - Math.PI / 2, 0]} material={basic(col, 0.95 * a)}>
                  <boxGeometry args={[0.7, 0.05, 0.05]} />
                </mesh>
                <mesh geometry={ribbon([[ps.pelvis[0], ps.pelvis[1]], [tip[0] - fwdH[0] * 0.08, tip[1] - fwdH[1] * 0.08]], 0.05, hz)} material={basic(col, 0.95 * a)} />
                <mesh geometry={arrowHead(tip, fwdH, 0.2, hz)} material={basic(col, 0.95 * a)} />
              </group>
            );
          }
          case 'glow': {
            const at = o.player ? P(o.player) : o.at ?? [0, 1.575];
            const grow = easeOut(o.age / 0.4);
            const col = o.color ?? GOLD3;
            const k = o.strength ?? 1;
            return (
              <group key={i}>
                <mesh position={W3([at[0], at[1], 0.008])} rotation={[-Math.PI / 2, 0, 0]} scale={(o.r ?? 1.2) * (0.7 + 0.3 * grow)} material={new THREE.MeshBasicMaterial({color: col, map: glowTex(), transparent: true, opacity: 0.85 * k * a * grow, depthWrite: false, toneMapped: false, blending: THREE.AdditiveBlending})}>
                  <planeGeometry args={[2, 2]} />
                </mesh>
                {o.hoop && (
                  <group>
                    <mesh position={W3([0, 1.575, 3.05])} rotation={[-Math.PI / 2, 0, 0]} material={basic(col, 0.95 * a * grow)}>
                      <torusGeometry args={[0.235, 0.022, 10, 48]} />
                    </mesh>
                    <mesh position={W3([0, 1.575, 3.05])} rotation={[-Math.PI / 2, 0, 0]} material={new THREE.MeshBasicMaterial({color: col, map: glowTex(), transparent: true, opacity: 0.5 * a * grow, depthWrite: false, toneMapped: false, side: THREE.DoubleSide})}>
                      <planeGeometry args={[1.1, 1.1]} />
                    </mesh>
                  </group>
                )}
              </group>
            );
          }
          case 'spot':
          case 'ripple':
          case 'floorText':
          case 'ballTrail':
          case 'ghostTrail':
          case 'screenTag':
            return <Telestration3D key={i} play={play} pt={pt} o={o} a={a} />;
          case 'arrow3d':
          case 'lockRing':
          case 'vision':
          case 'tether':
          case 'ghost':
          case 'ballPath':
          case 'motionTrail':
          case 'debugCatch':
            return <TelestrationBP key={i} play={play} pt={pt} o={o} a={a} />;
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
