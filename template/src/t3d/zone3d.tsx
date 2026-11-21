// E2A 3D engine — ZONE RESPONSIBILITY GRID (2026-11-21, 2-3 Zone 40 s cinematic, owner brief sec. 11).
// ZoneGridMorph: one rounded, chamfered floor area per zone defender (an ILLUSTRATIVE diagram, the areas overlap),
// thin warm outline + very discreet fill; only the SELECTED area gets a live edge, a fine grid and a soft pulse.
// Every area MOVES WITH ITS DEFENDER (never ahead of him): centre = base centre + follow * (defender now - defender at
// `base`), and it stretches a little along that displacement, so the box slides to the ball side as the zone shifts.
// compress (0..1) pulls every area toward the rim (the zone squeezing the middle). Deterministic per frame (play time
// + overlay age only), depth-tested (players occlude the lines behind them), clipped to the court, lifted 6-14 mm.
import React from 'react';
import * as THREE from 'three';
import type {V2} from '../tactical/geometry.ts';
import type {Play} from '../tactical/play.ts';
import {posAt} from '../tactical/play.ts';
import {W3} from './Athlete';
import {floorQuad, textTex, yawAxes} from './telestration3d';

export type ZoneGridOv = {
  type: 'zoneGrid';
  /** base areas in repo axes [x0, x1, y0, y1] (m), one per defender id */
  areas: Record<string, [number, number, number, number]>;
  /** defenders whose area is selected (live edge, grid, pulse) */
  select?: string[];
  /** overlay age (s) at which the selection lights up (default 0) */
  selectAt?: number;
  /** reveal stagger between consecutive areas (s, order of `areas`); 0 = all together */
  stagger?: number;
  /** how much of the defender's displacement the area follows (0..1, default 0.8) */
  follow?: number;
  /** play time of the reference positions (default 0 = the neutral set) */
  base?: number;
  /** compress toward the rim, 0..1 (eased in over `compressIn` s of overlay age) */
  compress?: number;
  compressIn?: number;
  /** floor labels at the area centres (2-4 words), read from camera yaw labelYaw */
  labels?: Record<string, string>;
  labelYaw?: number;
  labelSize?: number;
  /** only the selected areas carry their label */
  labelsSelectedOnly?: boolean;
  /** label placement inside the area: hi = near its top edge (y1), lo = near its baseline edge (y0), c = centre (default);
   *  keeps the word off the defender standing in the middle of his area */
  labelPos?: Record<string, 'hi' | 'lo' | 'c'>;
  /** global opacity multiplier for the unselected areas */
  dim?: number;
  /** draw ONLY the selected areas (one idea at a time) */
  only?: boolean;
  /** red tone (WrongTempo comparison) */
  tone?: 'warm' | 'red';
  /** transfer pulse: from play time `at`, the listed areas flash then dim for `dur` s (side left less covered) */
  pulse?: {at: number; ids: string[]; dur?: number};
};

// (probe 1: warm amber lines vanished on the maple floor) idle edge = cream, idle fill = a navy veil that reads on wood;
// the selected area = live gold edge + warm fill + grid + halo
const WARM = '#FFF1D2', FILL = '#13284D', LIVE = '#FFC447', LIVE_FILL = '#F6B53F', RED = '#E5483A', RED_LIVE = '#FF6A55';
const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const RIM: V2 = [0, 1.575];
const COURT = {x0: -7.45, x1: 7.45, y0: 0.03, y1: 13.97};

const mat = (color: string, opacity: number, map?: THREE.Texture) =>
  new THREE.MeshBasicMaterial({color, ...(map ? {map} : {}), transparent: true, opacity, depthWrite: false, toneMapped: false, side: THREE.DoubleSide,
    polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2});

/** rounded rectangle outline (counter-clockwise), corner radius r, `n` points per corner */
const roundRect = (x0: number, x1: number, y0: number, y1: number, r: number, n = 6): V2[] => {
  const rr = Math.max(0.01, Math.min(r, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01));
  const cs: [V2, number][] = [[[x1 - rr, y0 + rr], -Math.PI / 2], [[x1 - rr, y1 - rr], 0], [[x0 + rr, y1 - rr], Math.PI / 2], [[x0 + rr, y0 + rr], Math.PI]];
  const out: V2[] = [];
  for (const [c, a0] of cs) for (let i = 0; i <= n; i++) {
    const a = a0 + (Math.PI / 2) * (i / n);
    out.push([c[0] + Math.cos(a) * rr, c[1] + Math.sin(a) * rr]);
  }
  return out;
};

const fan = (pts: V2[], z: number) => {
  const c = pts.reduce((s, p) => [s[0] + p[0] / pts.length, s[1] + p[1] / pts.length] as V2, [0, 0] as V2);
  const pos: number[] = [...W3([c[0], c[1], z])];
  for (const p of pts) pos.push(...W3([p[0], p[1], z]));
  const idx: number[] = [];
  for (let i = 0; i < pts.length; i++) idx.push(0, 1 + i, 1 + ((i + 1) % pts.length));
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
};

/** outline band along a polyline (closed when `closed`), width w, drawn up to fraction `u` of its length */
const band = (pts0: V2[], w: number, z: number, closed: boolean, u = 1) => {
  let pts = closed ? [...pts0, pts0[0]] : pts0;
  if (u < 1) {
    let tot = 0;
    for (let i = 1; i < pts.length; i++) tot += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    const want = tot * clamp(u);
    const out: V2[] = [pts[0]];
    let acc = 0;
    for (let i = 1; i < pts.length; i++) {
      const s = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      if (acc + s >= want) {
        const f = (want - acc) / (s || 1);
        out.push([pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f]);
        break;
      }
      acc += s;
      out.push(pts[i]);
    }
    pts = out;
  }
  const pos: number[] = [];
  const idx: number[] = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const L = Math.hypot(dx, dy) || 1;
    dx /= L; dy /= L;
    const p = pts[i];
    pos.push(...W3([p[0] - dy * w / 2, p[1] + dx * w / 2, z]), ...W3([p[0] + dy * w / 2, p[1] - dx * w / 2, z]));
    if (i > 0) idx.push(i * 2 - 2, i * 2 - 1, i * 2, i * 2 - 1, i * 2 + 1, i * 2);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
};

/** the live (morphed) rectangle of one area at play time pt */
export const zoneRect = (play: Play, o: ZoneGridOv, id: string, pt: number, age: number): [number, number, number, number] => {
  const [x0, x1, y0, y1] = o.areas[id];
  const tr = play.tracks[id];
  const cl = (t: number) => Math.max(0, Math.min(play.duration, t));
  const now = tr ? posAt(tr, cl(pt)) : ([0, 0] as V2);
  const ref = tr ? posAt(tr, cl(o.base ?? 0)) : ([0, 0] as V2);
  const k = o.follow ?? 0.8;
  const d: V2 = [now[0] - ref[0], now[1] - ref[1]];
  let cx = (x0 + x1) / 2 + k * d[0], cy = (y0 + y1) / 2 + k * d[1];
  let hx = (x1 - x0) / 2 + 0.18 * Math.abs(d[0]), hy = (y1 - y0) / 2 + 0.18 * Math.abs(d[1]);
  const cmp = (o.compress ?? 0) * eo(age / (o.compressIn ?? 0.6));
  if (cmp > 0) {
    cx += (RIM[0] - cx) * 0.16 * cmp;
    cy += (RIM[1] - cy) * 0.16 * cmp;
    hx *= 1 - 0.12 * cmp;
    hy *= 1 - 0.12 * cmp;
  }
  return [Math.max(COURT.x0, cx - hx), Math.min(COURT.x1, cx + hx), Math.max(COURT.y0, cy - hy), Math.min(COURT.y1, cy + hy)];
};

export const ZoneGrid3D: React.FC<{play: Play; pt: number; o: ZoneGridOv & {age: number}; a: number}> = ({play, pt, o, a}) => {
  const ids = Object.keys(o.areas);
  const sel = new Set(o.select ?? []);
  const selOn = eo((o.age - (o.selectAt ?? 0)) / 0.3);
  const red = o.tone === 'red';
  const els: React.ReactNode[] = [];
  ids.forEach((id, i) => {
    const ai = o.age - i * (o.stagger ?? 0);
    if (ai <= 0) return;
    const rev = eo(ai / 0.35);
    const isSel = sel.has(id) && o.age >= (o.selectAt ?? 0);
    if (o.only && !sel.has(id)) return;
    const s = isSel ? selOn : 0;
    let [x0, x1, y0, y1] = zoneRect(play, o, id, pt, o.age);
    // reveal: grows from 88 % about its centre
    const g = 0.88 + 0.12 * rev, cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    [x0, x1, y0, y1] = [cx + (x0 - cx) * g, cx + (x1 - cx) * g, cy + (y0 - cy) * g, cy + (y1 - cy) * g];
    let pk = 1;
    if (o.pulse && o.pulse.ids.includes(id) && pt >= o.pulse.at) {
      const u = (pt - o.pulse.at) / (o.pulse.dur ?? 0.7);
      if (u < 1) pk = 1 + 0.9 * Math.sin(Math.PI * clamp(u * 2)) * (u < 0.5 ? 1 : 0) - 0.45 * clamp((u - 0.4) / 0.6);
      else pk = 0.55;
    }
    const dimK = isSel ? 1 : o.dim ?? 1;
    const op = a * rev * dimK * pk;
    const pts = roundRect(x0, x1, y0, y1, 0.38);
    const z = 0.006 + i * 0.0015;
    const lineCol = red ? (s > 0 ? RED_LIVE : RED) : s > 0 ? LIVE : WARM;
    const breathe = s > 0 ? 0.85 + 0.15 * Math.sin(o.age * 5.2) : 1;
    els.push(<mesh key={`f${id}`} geometry={fan(pts, z)} material={mat(red ? RED : FILL, (red ? 0.1 : 0.16) * (1 - s) * op)} />);
    if (s > 0) els.push(<mesh key={`fs${id}`} geometry={fan(pts, z + 0.0005)} material={mat(red ? RED : LIVE_FILL, 0.2 * s * op)} />);
    // (coordinator note on PREVIEW-1: low contrast on the maple at 390 px) dark under-stroke + wider line
    els.push(<mesh key={`u${id}`} geometry={band(pts, 0.2 + 0.06 * s, z + 0.0015, true, rev)} material={mat('#0A1630', 0.55 * op)} />);
    els.push(<mesh key={`l${id}`} geometry={band(pts, 0.085 + 0.055 * s, z + 0.002, true, rev)} material={mat(lineCol, (0.9 + 0.1 * s) * op * breathe)} />);
    if (s > 0) {
      // fine grid inside the selected area (0.5 m), inset from the rounded edge
      const gr: React.ReactNode[] = [];
      for (let x = Math.ceil((x0 + 0.3) / 0.5) * 0.5; x < x1 - 0.3; x += 0.5) gr.push(<mesh key={`gx${x.toFixed(2)}`} geometry={band([[x, y0 + 0.3], [x, y1 - 0.3]], 0.014, z + 0.001, false)} material={mat(lineCol, 0.3 * s * op)} />);
      for (let y = Math.ceil((y0 + 0.3) / 0.5) * 0.5; y < y1 - 0.3; y += 0.5) gr.push(<mesh key={`gy${y.toFixed(2)}`} geometry={band([[x0 + 0.3, y], [x1 - 0.3, y]], 0.02, z + 0.001, false)} material={mat(lineCol, 0.3 * s * op)} />);
      els.push(<group key={`g${id}`}>{gr}</group>);
      // soft outer halo of the live edge
      els.push(<mesh key={`h${id}`} geometry={band(pts, 0.22, z + 0.0005, true)} material={mat(lineCol, 0.22 * s * op * breathe)} />);
    }
    const lab = o.labels?.[id];
    if (lab && (!o.labelsSelectedOnly || isSel)) {
      const {right, up} = yawAxes(o.labelYaw ?? 0);
      const t = textTex(lab, red ? '#FFB3A8' : '#FFE6B8', false);
      const h = o.labelSize ?? 0.42;
      const lp = o.labelPos?.[id] ?? 'c';
      const ly = lp === 'hi' ? y1 - 0.5 - h / 2 : lp === 'lo' ? y0 + 0.4 + h / 2 : cy;
      els.push(<mesh key={`t${id}`} geometry={floorQuad([cx, ly], right, up, h * t.aspect, h, z + 0.004)} material={mat('#FFFFFF', 0.9 * op * (isSel ? 1 : 0.75), t.tex)} />);
    }
  });
  return <group>{els}</group>;
};
