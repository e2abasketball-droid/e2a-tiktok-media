// E2A 3D engine — E2A DYNAMIC DEFENSIVE COVERAGE (2026-11-21, 2-3 Zone V2, owner brief "Dynamic Coverage" sec. 3-8).
// Replaces the V1 ZoneGridMorph "tubes" (zone3d.tsx stays for older episodes) with five floor-level responsibility areas
// that are DERIVED FROM THE SCENE every frame, never key-framed by hand:
//
//   CoverageController  coverageState(play, pt, scheme)  -> per defender: smoothed real position (trailing window, so an
//                       area can never move before its player), home spot, ball direction, speed (activity), polygon.
//   CoverageGeometry    area = convex hull( egg around the defender, stretched toward the ball  +  a disc at his home spot
//                       that shrinks as he leaves it )  ∩  Voronoi half-planes against the other defenders (a thin gap
//                       keeps the five areas separate: no double / triple borders)  ∩  court, then Chaikin-rounded.
//                       -> the areas slide AND deform with the real defenders; the space a defender leaves really opens.
//   CoverageMaterials   navy veil fill 10-18 % (active gold 18-25 %) with a soft inner gradient (vertex alpha), thin edge
//                       (5-7 cm) + small glow; cool blue = secondary / waiting, gold = active, coral = vulnerable / late.
//   CoverageAnimations  reveal (scale + fade + light sweep along the edge + one pulse, staggered by `order`), modes
//                       FULL / ACTIVE / CLEAN, compression (real positions + optional extra scale), recovery
//                       (coral -> normal as the defender closes the distance to his reset spot).
//   Effects             covLink (help / relay line), gapReveal (space opens only after the trigger defender has moved),
//                       covHull (defensive compression: hull of the five now vs a dashed ghost hull), closeout (real route,
//                       destination, distance, LATE), shotWindow (time between catch and release vs the closing defender),
//                       ghost (previous spot of ONE defender, < 1 s).
// Deterministic: everything is a pure function of play time + overlay age (no Date.now, no state); depth-tested (players
// occlude the floor graphics), depthWrite off, polygonOffset against z-fighting, lifted 5-12 mm, clipped to the court.
// Other schemes (3-2, 1-3-1, box-and-one) = another entry in COVERAGE_SCHEMES (ids, labels, radii, home spots).
import React from 'react';
import * as THREE from 'three';
import type {V2} from '../tactical/geometry.ts';
import type {Play} from '../tactical/play.ts';
import {posAt, sample, velAt} from '../tactical/play.ts';
import {W3} from './Athlete';
import {floorQuad, textTex, yawAxes} from './telestration3d';

// ---------------------------------------------------------------- schemes (configuration, reusable)
export type CoverageRole = {
  /** discreet floor label, e.g. 'X1 · TOP' */
  label: string;
  /** lateral / depth half-size of the area around the defender (m) */
  r: [number, number];
  /** radius of the home-spot disc (m) */
  rh: number;
  /** home spot (repo axes); default = the defender's position at play time `base` */
  home?: V2;
  /** label offset from the defender (m, repo axes) */
  labelOff: V2;
};
export type CoverageScheme = {name: string; ids: string[]; roles: Record<string, CoverageRole>; gap: number; reveal: string[]};
export const COVERAGE_SCHEMES: Record<string, CoverageScheme> = {
  // repo axes (x = -brief x): X1 top / brief-left, X2 top / brief-right, X3 low / brief-left, X4 low / brief-right, X5 middle
  '2-3': {
    name: '2-3 zone',
    ids: ['X1', 'X2', 'X3', 'X4', 'X5'],
    gap: 0.16,
    reveal: ['X1', 'X2', 'X3', 'X5', 'X4'],
    roles: {
      X1: {label: 'X1 · TOP', r: [1.75, 1.45], rh: 1.35, labelOff: [0, 1.25]},
      X2: {label: 'X2 · TOP', r: [1.75, 1.45], rh: 1.35, labelOff: [0, 1.25]},
      X3: {label: 'X3 · LOW', r: [1.6, 1.75], rh: 1.3, labelOff: [0, -1.55]},
      X4: {label: 'X4 · LOW', r: [1.6, 1.75], rh: 1.3, labelOff: [0, -1.55]},
      X5: {label: 'X5 · CENTER', r: [1.55, 1.45], rh: 1.3, labelOff: [0, -1.2]},
    },
  },
  // 2026-11-23 (1-3-1 Zone reel): half-court corner-trapping 1-3-1. X1 chaser/top, X2 left wing (repo x > 0), X3 right
  // wing, X5 center, X4 tail/warrior: a wide, shallow band along the baseline (both corners over time, never at once).
  '1-3-1': {
    name: '1-3-1 zone',
    ids: ['X1', 'X2', 'X3', 'X4', 'X5'],
    gap: 0.16,
    reveal: ['X1', 'X2', 'X5', 'X3', 'X4'],
    roles: {
      X1: {label: 'X1 · TOP', r: [1.95, 1.3], rh: 1.3, labelOff: [0, 1.3]},
      X2: {label: 'X2 · WING', r: [1.55, 1.55], rh: 1.25, labelOff: [0, 1.2]},
      X3: {label: 'X3 · WING', r: [1.55, 1.55], rh: 1.25, labelOff: [0, 1.2]},
      X5: {label: 'X5 · CENTER', r: [1.35, 1.25], rh: 1.15, labelOff: [0, -1.05]},
      X4: {label: 'X4 · TAIL', r: [3.1, 0.85], rh: 1.1, labelOff: [0, -0.95]},
    },
  },
  // 2026-11-25 (3-2 Zone Defense reel): conventional half-court 3-2, low defender takes the corner. Three on ONE line up
  // top (X1 middle, X2 LEFT wing repo x > 0, X3 RIGHT wing), two low (X4 left block, X5 right block). Wider, shallower top
  // areas (perimeter), deeper low areas (block + short corner + corner). Rules: produccion/zone32d-2026-11-25/.
  '3-2': {
    name: '3-2 zone',
    ids: ['X1', 'X2', 'X3', 'X4', 'X5'],
    gap: 0.16,
    reveal: ['X1', 'X2', 'X3', 'X4', 'X5'],
    roles: {
      X1: {label: 'X1 · TOP', r: [1.6, 1.4], rh: 1.25, labelOff: [0, 1.3]},
      X2: {label: 'X2 · WING', r: [1.75, 1.5], rh: 1.3, labelOff: [0, 1.3]},
      X3: {label: 'X3 · WING', r: [1.75, 1.5], rh: 1.3, labelOff: [0, 1.3]},
      X4: {label: 'X4 · LOW', r: [1.7, 1.6], rh: 1.25, labelOff: [0, -1.4]},
      X5: {label: 'X5 · LOW', r: [1.7, 1.6], rh: 1.25, labelOff: [0, -1.4]},
    },
  },
  // 2026-11-24 (1-3-1 ARROW press reel): three-quarter-court 1-3-1 press, full-court play (`court: 'full'`). Bigger
  // areas: five players cover the whole width of the floor. X1 point (turns the ball to the sideline), X2 left wing /
  // X3 right wing (the trap line at half court), X5 middle (the middle lane), X4 safety (the long pass, the rim).
  'arrow-131': {
    name: '1-3-1 arrow press',
    ids: ['X1', 'X2', 'X3', 'X4', 'X5'],
    gap: 0.2,
    reveal: ['X1', 'X2', 'X5', 'X3', 'X4'],
    roles: {
      X1: {label: 'X1 · POINT', r: [2.6, 2.1], rh: 1.6, labelOff: [0, 1.6]},
      X2: {label: 'X2 · WING', r: [2.5, 2.4], rh: 1.6, labelOff: [0, 1.5]},
      X3: {label: 'X3 · WING', r: [2.5, 2.4], rh: 1.6, labelOff: [0, 1.5]},
      X5: {label: 'X5 · MIDDLE', r: [2.2, 2.1], rh: 1.5, labelOff: [0, -1.5]},
      X4: {label: 'X4 · SAFETY', r: [3.3, 2.7], rh: 1.7, labelOff: [0, -1.7]},
    },
  },
};

// ---------------------------------------------------------------- overlay types
export type CoverageMode = 'full' | 'active' | 'clean';
export type CoverageOv = {
  type: 'coverage';
  scheme?: string;
  mode?: CoverageMode;
  /** ACTIVE: the 2-3 responsibilities that matter for the action (gold); the others go cool blue + dim */
  active?: string[];
  /** draw only these ids (one idea at a time) */
  only?: string[];
  /** coral (vulnerable / late) */
  vulnerable?: string[];
  /** reveal: staggered appearance in scheme order (s between areas; 0/absent = no reveal animation) */
  reveal?: number;
  /** play time of the home spots (default 0) */
  base?: number;
  /** labels: all | active | none (default none) */
  labels?: 'all' | 'active' | 'none' | string[];
  labelYaw?: number;
  labelSize?: number;
  /** opacity multiplier of the secondary areas in ACTIVE mode (default 0.55) */
  dim?: number;
  /** extra visual squeeze toward the ball (0..1, on top of the real positions) */
  compress?: number;
  /** recovery: ids turn from coral back to normal as they close the distance to their position at play time `t1` */
  recover?: {ids: string[]; t0: number; t1: number};
  /** lag of the trailing smoothing window (s, default 0.12) */
  lag?: number;
  /** 2026-11-24 (Floor Graphics Stability Standard): ACTIVE set changes INSIDE one overlay, [[overlaySecond, ids], ...],
   *  cross-faded over `activeFade` s (default 0.3). Replaces chains of abutting coverage overlays, whose fade-out +
   *  fade-in made every area dip to ~0 and come back at each change (a visible blink). */
  activeKeys?: [number, string[]][];
  activeFade?: number;
  /** 2026-11-24 E2A Floor Graphics Stability Standard: no speed-driven edge brightening/thickening, no reveal pulse,
   *  dense (21-sample) ball reference so a dribble cannot alias into the ball-side stretch. Default off (old episodes
   *  render exactly as before). */
  stable?: boolean;
};
export type CovLinkOv = {type: 'covLink'; a: string; b: string; color?: string};
export type GapRevealOv = {type: 'gapReveal'; at: V2; r?: number; trigger: {id: string; dist?: number; base?: number}; arrowFrom?: string; arrowTo?: V2; color?: string};
export type CovHullOv = {type: 'covHull'; ids?: string[]; base: number; color?: string};
export type CloseoutOv = {type: 'closeout'; id: string; t0: number; t1: number; late?: number; label?: boolean};
export type ShotWindowOv = {type: 'shotWindow'; shooter: string; t0: number; t1: number; defender?: string};
export type CovGhostOv = {type: 'covGhost'; id: string; at: number};
export type CoverageFamilyOv = CoverageOv | CovLinkOv | GapRevealOv | CovHullOv | CloseoutOv | ShotWindowOv | CovGhostOv;

// ---------------------------------------------------------------- materials
const NAVY = '#13284D', EDGE = '#F0D28C', GOLD = '#FFC447', GOLD_FILL = '#F6B53F', COOL = '#A9C8EE', CORAL = '#F06A55';
const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const mix = (c1: string, c2: string, u: number) => '#' + new THREE.Color(c1).lerp(new THREE.Color(c2), clamp(u)).getHexString();
const COURT = {x0: -7.42, x1: 7.42, y0: 0.05, y1: 13.95};
/** 2026-11-24: full-court plays (`court: 'full'`, arrow press) clip the areas to the far baseline instead of half court */
const courtY1 = (play: Play) => ((play as {court?: string}).court === 'full' ? 27.95 : COURT.y1);
const mat = (color: string, opacity: number, map?: THREE.Texture, additive = false) =>
  new THREE.MeshBasicMaterial({color, ...(map ? {map} : {}), transparent: true, opacity: clamp(opacity), depthWrite: false, toneMapped: false, side: THREE.DoubleSide,
    polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, ...(additive ? {blending: THREE.AdditiveBlending} : {})});
const vmat = (opacity: number) =>
  new THREE.MeshBasicMaterial({vertexColors: true, transparent: true, opacity: clamp(opacity), depthWrite: false, toneMapped: false, side: THREE.DoubleSide,
    polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2});

// ---------------------------------------------------------------- 2D geometry helpers
const sub = (a: V2, b: V2): V2 => [a[0] - b[0], a[1] - b[1]];
const len = (a: V2) => Math.hypot(a[0], a[1]);
const hull = (ps: V2[]): V2[] => {
  const p = [...ps].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cr = (o: V2, a: V2, b: V2) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo: V2[] = [], up: V2[] = [];
  for (const q of p) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  for (const q of p.reverse()) { while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
};
/** keep the part of a convex polygon where dot(x, n) <= c */
const clipHalf = (poly: V2[], n: V2, c: number): V2[] => {
  const out: V2[] = [];
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length];
    const da = a[0] * n[0] + a[1] * n[1] - c, db = b[0] * n[0] + b[1] * n[1] - c;
    if (da <= 0) out.push(a);
    if ((da < 0 && db > 0) || (da > 0 && db < 0)) {
      const f = da / (da - db);
      out.push([a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f]);
    }
  }
  return out;
};
const chaikin = (poly: V2[], it = 2): V2[] => {
  let p = poly;
  for (let k = 0; k < it; k++) {
    const q: V2[] = [];
    for (let i = 0; i < p.length; i++) {
      const a = p[i], b = p[(i + 1) % p.length];
      q.push([a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25], [a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75]);
    }
    p = q;
  }
  return p;
};
const centroid = (p: V2[]): V2 => p.reduce((s, q) => [s[0] + q[0] / p.length, s[1] + q[1] / p.length] as V2, [0, 0] as V2);
const area = (p: V2[]) => Math.abs(p.reduce((s, q, i) => { const r = p[(i + 1) % p.length]; return s + q[0] * r[1] - r[0] * q[1]; }, 0)) / 2;

/** gradient fill: fan from the centroid, vertex alpha lower in the middle (soft inner gradient) */
const fill = (pts: V2[], z: number, color: string, aIn: number, aOut: number) => {
  const c = centroid(pts);
  const col = new THREE.Color(color);
  const pos: number[] = [...W3([c[0], c[1], z])];
  const cl: number[] = [col.r, col.g, col.b, aIn];
  for (const p of pts) { pos.push(...W3([p[0], p[1], z])); cl.push(col.r, col.g, col.b, aOut); }
  const idx: number[] = [];
  for (let i = 0; i < pts.length; i++) idx.push(0, 1 + i, 1 + ((i + 1) % pts.length));
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(cl, 4));
  g.setIndex(idx);
  return g;
};
/** band along a polyline (closed when `closed`) of width w, from fraction u0 to u1 of its length */
export const band = (pts0: V2[], w: number, z: number, closed: boolean, u0 = 0, u1 = 1) => {
  const pts = closed ? [...pts0, pts0[0]] : pts0;
  const cum = [0];
  for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + len(sub(pts[i], pts[i - 1])));
  const tot = cum[cum.length - 1] || 1;
  const at = (s: number): V2 => {
    let i = 1;
    while (i < cum.length - 1 && cum[i] < s) i++;
    const f = (s - cum[i - 1]) / ((cum[i] - cum[i - 1]) || 1);
    return [pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f];
  };
  const s0 = clamp(u0) * tot, s1 = clamp(u1) * tot;
  const sel: V2[] = [at(s0)];
  for (let i = 0; i < pts.length; i++) if (cum[i] > s0 && cum[i] < s1) sel.push(pts[i]);
  sel.push(at(s1));
  const pos: number[] = [];
  const idx: number[] = [];
  for (let i = 0; i < sel.length; i++) {
    const a = sel[Math.max(0, i - 1)], b = sel[Math.min(sel.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const L = Math.hypot(dx, dy) || 1;
    dx /= L; dy /= L;
    const p = sel[i];
    pos.push(...W3([p[0] - dy * w / 2, p[1] + dx * w / 2, z]), ...W3([p[0] + dy * w / 2, p[1] - dx * w / 2, z]));
    if (i > 0) idx.push(i * 2 - 2, i * 2 - 1, i * 2, i * 2 - 1, i * 2 + 1, i * 2);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
};
const dashed = (a: V2, b: V2, w: number, z: number, dash: number, phase: number) => {
  const L = len(sub(b, a));
  const segs: V2[][] = [];
  for (let s = -dash * 2 + (phase % (dash * 2)); s < L; s += dash * 2) {
    const s0 = Math.max(0, s), s1 = Math.min(L, s + dash);
    if (s1 > s0) segs.push([[a[0] + (b[0] - a[0]) * s0 / L, a[1] + (b[1] - a[1]) * s0 / L], [a[0] + (b[0] - a[0]) * s1 / L, a[1] + (b[1] - a[1]) * s1 / L]]);
  }
  return segs.map((sg) => band(sg, w, z, false));
};
const circle = (c: V2, r: number, n = 40): V2[] => Array.from({length: n}, (_, i) => [c[0] + Math.cos((i / n) * Math.PI * 2) * r, c[1] + Math.sin((i / n) * Math.PI * 2) * r] as V2);
const glowDisc = (() => {
  let t: THREE.Texture | null = null;
  return () => {
    if (t) return t;
    const c = document.createElement('canvas');
    c.width = c.height = 128;
    const g = c.getContext('2d')!;
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.55, 'rgba(255,255,255,0.45)');
    gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr;
    g.fillRect(0, 0, 128, 128);
    t = new THREE.CanvasTexture(c);
    return t;
  };
})();
const flatDisc = (c: V2, r: number, z: number, color: string, op: number, key: string) => (
  <mesh key={key} position={W3([c[0], c[1], z])} rotation={[-Math.PI / 2, 0, 0]} material={mat(color, op, glowDisc())}>
    <planeGeometry args={[r * 2, r * 2]} />
  </mesh>
);

// ---------------------------------------------------------------- CoverageController
export type DefState = {id: string; pos: V2; home: V2; speed: number; away: number; poly: V2[]};
const cl = (play: Play, t: number) => clamp(t, 0, play.duration);
/** trailing-window smoothed position (only past samples: the area can never lead its defender) */
const trail = (play: Play, id: string, pt: number, lag: number): V2 => {
  const tr = play.tracks[id];
  const ts = [pt, pt - lag / 2, pt - lag];
  const ps = ts.map((t) => posAt(tr, cl(play, t)));
  return [(ps[0][0] * 2 + ps[1][0] + ps[2][0] * 0.5) / 3.5, (ps[0][1] * 2 + ps[1][1] + ps[2][1] * 0.5) / 3.5];
};
export const coverageState = (play: Play, pt: number, o: Pick<CoverageOv, 'scheme' | 'base' | 'lag' | 'compress' | 'stable'>): DefState[] => {
  const sc = COVERAGE_SCHEMES[o.scheme ?? '2-3'];
  const ids = sc.ids.filter((id) => play.tracks[id]);
  // ball reference: trailing 0.4 s average (the areas answer the ball after it moves, never ahead, and a pass in
  // flight does not whip the ball-side stretch around)
  const bs = (o.stable ? Array.from({length: 21}, (_, k) => k * 0.02) : [0, 0.1, 0.2, 0.3, 0.4]).map((d) => sample(play, cl(play, pt - d)).ball.pos);
  const ball: V2 = [bs.reduce((s, q) => s + q[0], 0) / bs.length, bs.reduce((s, q) => s + q[1], 0) / bs.length];
  const P = Object.fromEntries(ids.map((id) => [id, trail(play, id, pt, o.lag ?? 0.12)])) as Record<string, V2>;
  const cmp = clamp(o.compress ?? 0);
  return ids.map((id) => {
    const ro = sc.roles[id];
    const p = P[id];
    const home = ro.home ?? posAt(play.tracks[id], cl(play, o.base ?? 0));
    const away = len(sub(p, home));
    const v = velAt(play.tracks[id], cl(play, pt));
    const speed = len(v);
    // egg around the defender, stretched toward the ball (more when the ball is near: ball-side intensity)
    const tb = sub(ball, p);
    const db = len(tb) || 1;
    const th = Math.atan2(tb[1], tb[0]);
    const near = clamp(1 - (db - 2) / 7);
    const e = 0.08 + 0.13 * near;
    const pts: V2[] = [];
    const N = 28;
    const k = 1 - 0.28 * cmp;
    for (let i = 0; i < N; i++) {
      const a = (i / N) * Math.PI * 2;
      const rr = Math.hypot(ro.r[0] * Math.cos(a), ro.r[1] * Math.sin(a)) * (1 + e * Math.cos(a - th)) * k;
      pts.push([p[0] + Math.cos(a) * rr, p[1] + Math.sin(a) * rr]);
    }
    // home disc: shrinks to nothing as the defender leaves it -> the area stretches, then lets the space go
    // ... and its centre slides toward him, so the stretched part retracts continuously (no snap when it vanishes)
    const rh = ro.rh * clamp(1 - away / 3.4) * k;
    const pu = clamp((away - 0.6) / 3.4), pull = pu * pu * (3 - 2 * pu);
    const hc: V2 = [home[0] + (p[0] - home[0]) * pull, home[1] + (p[1] - home[1]) * pull];
    if (rh > 0.02) pts.push(...circle(hc, rh, 20));
    let poly = hull(pts);
    // Voronoi half-planes vs the other defenders (thin gap)
    for (const j of ids) {
      if (j === id) continue;
      const q = P[j];
      const d = sub(q, p);
      const L = len(d);
      if (L < 0.05) continue;
      const n: V2 = [d[0] / L, d[1] / L];
      const m: V2 = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2];
      poly = clipHalf(poly, n, m[0] * n[0] + m[1] * n[1] - sc.gap / 2);
    }
    poly = clipHalf(poly, [1, 0], COURT.x1);
    poly = clipHalf(poly, [-1, 0], -COURT.x0);
    poly = clipHalf(poly, [0, 1], courtY1(play));
    poly = clipHalf(poly, [0, -1], -COURT.y0);
    if (poly.length >= 3) poly = chaikin(poly, 3);
    return {id, pos: p, home, speed, away, poly};
  });
};

// ---------------------------------------------------------------- renderers
export const Coverage3D: React.FC<{play: Play; pt: number; o: CoverageOv & {age: number}; a: number}> = ({play, pt, o, a}) => {
  const sc = COVERAGE_SCHEMES[o.scheme ?? '2-3'];
  const st = coverageState(play, pt, o);
  const mode = o.mode ?? 'full';
  const act = new Set(o.active ?? []);
  const vul = new Set(o.vulnerable ?? []);
  const els: React.ReactNode[] = [];
  st.forEach((d, i) => {
    if (o.only && !o.only.includes(d.id)) return;
    if (d.poly.length < 3 || area(d.poly) < 0.05) return;
    const order = sc.reveal.indexOf(d.id);
    const ra = o.reveal ? o.age - Math.max(0, order) * o.reveal : 99;
    if (ra <= 0) return;
    const rev = eo(ra / 0.4);
    // active weight 0..1 (activeKeys: smooth cross-fade between consecutive sets, no dip)
    let wa = act.has(d.id) ? 1 : 0;
    if (o.activeKeys && o.activeKeys.length) {
      const ks = o.activeKeys, F = o.activeFade ?? 0.3;
      wa = ks[0][1].includes(d.id) ? 1 : 0;
      for (let k = 1; k < ks.length; k++) {
        if (o.age < ks[k][0]) break;
        const prev = wa, next = ks[k][1].includes(d.id) ? 1 : 0;
        const u = clamp((o.age - ks[k][0]) / F);
        wa = prev + (next - prev) * (u * u * (3 - 2 * u));
      }
    }
    const isAct = wa > 0.5;
    let vulK = vul.has(d.id) ? 1 : 0;
    if (o.recover && o.recover.ids.includes(d.id)) {
      // recovery derived from the real defender: coral while far from his reset spot, back to normal as he gets there
      const tgt = posAt(play.tracks[d.id], cl(play, o.recover.t1));
      const d0 = len(sub(posAt(play.tracks[d.id], cl(play, o.recover.t0)), tgt)) || 1;
      // only from t0 (the moment the weakness exists, e.g. the skip leaves), never before
      vulK = clamp(len(sub(d.pos, tgt)) / d0 * 1.25) * clamp((pt - o.recover.t0) / 0.2);
    }
    // mode weights
    let w = 1, edgeCol = EDGE, fillCol = NAVY, fa = 0.16, ew = 0.05;
    if (mode === 'clean') w = 0.0;
    if (mode === 'active') {
      // interpolated by the active weight (identical to the old branches at wa = 0 / 1)
      edgeCol = mix(COOL, GOLD, wa); fillCol = mix(NAVY, GOLD_FILL, wa);
      fa = 0.1 + 0.11 * wa; ew = 0.05 + 0.015 * wa; w = (o.dim ?? 0.55) + (1 - (o.dim ?? 0.55)) * wa;
    }
    if (vulK > 0) { edgeCol = mix(edgeCol, CORAL, vulK); fillCol = mix(fillCol, CORAL, vulK * 0.9); fa = Math.max(fa, 0.12 + 0.08 * vulK); }
    const activity = o.stable ? 0 : clamp((d.speed - 0.9) / 2.6);
    const op = a * rev * w;
    if (op <= 0.002) return;
    // reveal: grows from 85 % about the defender
    const g = 0.85 + 0.15 * rev;
    const poly = d.poly.map((q) => [d.pos[0] + (q[0] - d.pos[0]) * g, d.pos[1] + (q[1] - d.pos[1]) * g] as V2);
    const z = 0.006 + i * 0.0012;
    els.push(<mesh key={`f${d.id}`} geometry={fill(poly, z, fillCol, fa * 0.55, fa)} material={vmat(op)} />);
    // edge: glow + line (+ brighter while the defender is moving: activity indicator)
    const lw = ew * (1 + 0.35 * activity);
    els.push(<mesh key={`g${d.id}`} geometry={band(poly, lw * 3.6, z + 0.001, true)} material={mat(edgeCol, (0.12 + 0.1 * activity + 0.08 * (mode === "active" ? wa : act.has(d.id) ? 1 : 0)) * op)} />);
    els.push(<mesh key={`n${d.id}`} geometry={band(poly, lw * 1.9, z + 0.0015, true)} material={mat(NAVY, 0.32 * op)} />);
    els.push(<mesh key={`l${d.id}`} geometry={band(poly, lw, z + 0.002, true)} material={mat(edgeCol, (0.82 + 0.18 * activity) * op)} />);
    // reveal light sweep + one pulse when the area becomes active
    if (o.reveal && ra < 0.75) {
      const u = clamp(ra / 0.6);
      els.push(<mesh key={`s${d.id}`} geometry={band(poly, lw * 2.4, z + 0.0025, true, Math.max(0, u - 0.16), u)} material={mat('#FFF6DE', 0.9 * a * (1 - clamp((ra - 0.6) / 0.15)), undefined, true)} />);
    }
    if (o.reveal && !o.stable && ra > 0.4 && ra < 0.9) {
      const u = (ra - 0.4) / 0.5;
      els.push(<mesh key={`p${d.id}`} geometry={band(poly, lw * 5 * (1 + u), z + 0.0005, true)} material={mat(edgeCol, 0.25 * Math.sin(Math.PI * u) * a)} />);
    }
    // labels 'active' + activeKeys: the label fades with the active weight instead of popping at wa = 0.5
    const labK = o.labels === 'active' && o.activeKeys ? wa : 1;
    const showLab = o.labels === 'all' || (o.labels === 'active' && (o.activeKeys ? wa > 0.02 : isAct)) || (Array.isArray(o.labels) && o.labels.includes(d.id));
    if (showLab) {
      const ro = sc.roles[d.id];
      const {right, up} = yawAxes(o.labelYaw ?? 90);
      const t = textTex(ro.label, isAct ? '#FFE2A0' : '#F4EBDD', false);
      const h = o.labelSize ?? 0.38;
      const c: V2 = [clamp(d.pos[0] + ro.labelOff[0], COURT.x0 + 1.2, COURT.x1 - 1.2), clamp(d.pos[1] + ro.labelOff[1], COURT.y0 + 0.4, courtY1(play) - 0.4)];
      els.push(<mesh key={`tb${d.id}`} geometry={floorQuad(c, right, up, h * t.aspect * 1.04 + 0.16, h * 1.25, z + 0.003)} material={mat(NAVY, 0.55 * op * rev * labK)} />);
      els.push(<mesh key={`t${d.id}`} geometry={floorQuad(c, right, up, h * t.aspect, h, z + 0.0035)} material={mat('#FFFFFF', 0.95 * op * rev * labK, t.tex)} />);
    }
  });
  return <group>{els}</group>;
};

const P2 = (play: Play, id: string, t: number): V2 => posAt(play.tracks[id], cl(play, t));

export const CoverageFx3D: React.FC<{play: Play; pt: number; o: CoverageFamilyOv & {age: number; dur?: number}; a: number}> = ({play, pt, o, a}) => {
  const els: React.ReactNode[] = [];
  switch (o.type) {
    case 'covLink': {
      // help / relay line between two defenders (follows their real positions)
      const p = P2(play, o.a, pt), q = P2(play, o.b, pt);
      const col = o.color ?? COOL;
      const grow = eo(o.age / 0.35);
      const qq: V2 = [p[0] + (q[0] - p[0]) * grow, p[1] + (q[1] - p[1]) * grow];
      dashed(p, qq, 0.05, 0.014, 0.28, o.age * 0.9).forEach((g, k) => els.push(<mesh key={`d${k}`} geometry={g} material={mat(col, 0.9 * a)} />));
      els.push(flatDisc(p, 0.32, 0.013, col, 0.6 * a, 'e0'), flatDisc(qq, 0.32 * grow, 0.013, col, 0.6 * a, 'e1'));
      break;
    }
    case 'gapReveal': {
      // the space only lights up once the trigger defender has really moved away from his spot
      const base = P2(play, o.trigger.id, o.trigger.base ?? 0);
      const now = P2(play, o.trigger.id, pt);
      const open = clamp((len(sub(now, base)) - (o.trigger.dist ?? 0.35)) / 0.55);
      if (open <= 0) break;
      const col = o.color ?? GOLD;
      const r = (o.r ?? 1.2) * (0.7 + 0.3 * eo(open));
      const pulse = 1 + 0.18 * Math.sin(Math.PI * clamp(open * 1.6)) ;
      els.push(flatDisc(o.at, r * pulse * 1.3, 0.011, col, 0.42 * open * a, 'gl'));
      els.push(<mesh key="rg" geometry={band(circle(o.at, r * pulse, 56), 0.05, 0.012, true)} material={mat(col, 0.9 * open * a)} />);
      if (o.arrowFrom && o.arrowTo) {
        const s = P2(play, o.arrowFrom, pt);
        const d = sub(o.arrowTo, s);
        const L = len(d);
        const u = eo((open - 0.3) / 0.7);
        if (L > 0.5 && u > 0) {
          const e: V2 = [s[0] + d[0] * (1 - 0.6 / L) * u, s[1] + d[1] * (1 - 0.6 / L) * u];
          const n: V2 = [d[0] / L, d[1] / L];
          const st: V2 = [s[0] + n[0] * 0.55, s[1] + n[1] * 0.55];
          els.push(<mesh key="ar" geometry={band([st, e], 0.08, 0.013, false)} material={mat(col, 0.95 * a * u)} />);
          const hd: V2[] = [[e[0] + n[0] * 0.38, e[1] + n[1] * 0.38], [e[0] - n[1] * 0.24, e[1] + n[0] * 0.24], [e[0] + n[1] * 0.24, e[1] - n[0] * 0.24]];
          els.push(<mesh key="ah" geometry={fill(hd, 0.013, col, 1, 1)} material={vmat(0.95 * a * u)} />);
        }
      }
      break;
    }
    case 'covHull': {
      // defensive compression: the hull of the five NOW (gold) vs where they were (dashed ghost)
      const ids = o.ids ?? COVERAGE_SCHEMES['2-3'].ids;
      const now = chaikin(hull(ids.map((id) => P2(play, id, pt))), 2);
      const was = chaikin(hull(ids.map((id) => P2(play, id, o.base))), 2);
      const col = o.color ?? GOLD;
      for (let k = 0; k < was.length; k += 2) {
        const p = was[k], q = was[(k + 1) % was.length];
        els.push(<mesh key={`w${k}`} geometry={band([p, q], 0.035, 0.012, false)} material={mat(COOL, 0.55 * a)} />);
      }
      els.push(<mesh key="hn" geometry={band(now, 0.06, 0.013, true)} material={mat(col, 0.95 * a)} />);
      els.push(<mesh key="hf" geometry={fill(now, 0.0125, col, 0.05, 0.14)} material={vmat(a)} />);
      break;
    }
    case 'closeout': {
      // the defender's REAL route t0 -> t1: travelled part solid, the rest faint; destination ring; LATE when the ball
      // is released before he gets there
      const tr = play.tracks[o.id];
      const pts: V2[] = [];
      for (let t = o.t0; t <= o.t1 + 1e-6; t += 1 / 30) pts.push(posAt(tr, cl(play, t)));
      const u = clamp((pt - o.t0) / (o.t1 - o.t0));
      const draw = eo(o.age / 0.3);
      els.push(<mesh key="rest" geometry={band(pts, 0.05, 0.013, false, u, draw)} material={mat('#F4EBDD', 0.55 * a)} />);
      if (u > 0) els.push(<mesh key="done" geometry={band(pts, 0.09, 0.0135, false, 0, u)} material={mat(GOLD, 0.95 * a)} />);
      const dst = pts[pts.length - 1];
      const late = o.late !== undefined && pt >= o.late;
      const dcol = late ? CORAL : GOLD;
      els.push(<mesh key="dr" geometry={band(circle(dst, 0.42, 40), 0.05, 0.014, true)} material={mat(dcol, 0.95 * a * draw)} />);
      if (late) els.push(flatDisc(dst, 0.85 * (1 + 0.2 * Math.sin(Math.PI * clamp((pt - (o.late ?? 0)) / 0.4))), 0.0125, CORAL, 0.45 * a, 'lg'));
      if (o.label !== false) {
        let L = 0;
        for (let k = 1; k < pts.length; k++) L += len(sub(pts[k], pts[k - 1]));
        const mid = pts[Math.floor(pts.length / 2)];
        const {right, up} = yawAxes(90);
        const t = textTex(`${L.toFixed(1)} m`, '#FFFFFF', true);
        els.push(<mesh key="lb" geometry={floorQuad([mid[0] + 0.0, mid[1] + 0.75], right, up, 0.42 * t.aspect, 0.42, 0.015)} material={mat('#FFFFFF', 0.95 * a * draw, t.tex)} />);
      }
      break;
    }
    case 'shotWindow': {
      // ring around the shooter that fills from the catch to the release; the closing defender's distance is the "cost"
      const s = P2(play, o.shooter, pt);
      const u = clamp((pt - o.t0) / (o.t1 - o.t0));
      const R = 0.75;
      const ring = circle(s, R, 64);
      els.push(<mesh key="bg" geometry={band(ring, 0.06, 0.013, true)} material={mat('#F4EBDD', 0.35 * a)} />);
      if (u > 0) els.push(<mesh key="fg" geometry={band(ring, 0.1, 0.0135, true, 0, u)} material={mat(GOLD, 0.95 * a)} />);
      if (o.defender) {
        const d = P2(play, o.defender, pt);
        const dd = len(sub(d, s));
        const near = clamp((2.2 - dd) / 1.2);
        if (dd > R + 0.1) els.push(<mesh key="gap" geometry={band([[s[0] + (d[0] - s[0]) * R / dd, s[1] + (d[1] - s[1]) * R / dd], d], 0.04, 0.013, false)} material={mat(mix(GOLD, CORAL, near), 0.8 * a)} />);
      }
      break;
    }
    case 'covGhost': {
      // where ONE defender was, for less than a second
      const was = P2(play, o.id, o.at);
      const now = P2(play, o.id, pt);
      const k = 1 - clamp((o.age - 0.45) / 0.45);
      if (k <= 0) break;
      els.push(flatDisc(was, 0.55, 0.012, COOL, 0.55 * a * k, 'gd'));
      els.push(<mesh key="gr" geometry={band(circle(was, 0.36, 40), 0.035, 0.0125, true)} material={mat(COOL, 0.8 * a * k)} />);
      if (len(sub(now, was)) > 0.6) dashed(was, now, 0.035, 0.0125, 0.18, 0).forEach((g, j) => els.push(<mesh key={`gl${j}`} geometry={g} material={mat(COOL, 0.6 * a * k)} />));
      break;
    }
    default:
      break;
  }
  return <group>{els}</group>;
};
