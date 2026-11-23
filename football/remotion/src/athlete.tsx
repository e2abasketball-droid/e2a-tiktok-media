// E2A Football — stylised footballer with a procedural gait.
// The gait phase advances with the distance actually travelled (play.ts), and the stride length grows
// with speed, so the feet keep pace with the ground (no skating). Lean follows acceleration, the body
// banks into turns, arms swing against the legs, kicks and the goalkeeper's dive are layered on top.
import React from 'react';
import * as THREE from 'three';
import type {Action, Kick, PlayerState} from './play';
import {smooth} from './play';

/** pitch (x, y, z-up) -> three.js (x, y-up, -z) */
export const W3 = (p: [number, number, number]): [number, number, number] => [p[0], p[2], -p[1]];

export type Kit = {shirt: string; shorts: string; socks: string; trim: string; number: string};
export const KITS: Record<string, Kit> = {
  navy: {shirt: '#0B1C3D', shorts: '#0B1C3D', socks: '#0B1C3D', trim: '#C9A24D', number: '#C9A24D'},
  white: {shirt: '#F4F5F7', shorts: '#F4F5F7', socks: '#F4F5F7', trim: '#9AA3B2', number: '#0B1C3D'},
  keeper: {shirt: '#2F7D4F', shorts: '#1E2A22', socks: '#2F7D4F', trim: '#D8E8DC', number: '#FFFFFF'},
};
export const SKINS = ['#C68B63', '#8D5A3B', '#E0B48F', '#5E3B26', '#B77B52', '#D9A07A', '#6E452D'];
const HAIR = ['#1B1410', '#2B1D14', '#120D0A', '#3A2718', '#1A1A1A'];

const G = (() => {
  let g: Record<string, THREE.BufferGeometry> | null = null;
  return () => {
    if (g) return g;
    g = {
      torso: new THREE.CapsuleGeometry(0.15, 0.3, 6, 14),
      pelvis: new THREE.CapsuleGeometry(0.14, 0.08, 4, 12),
      thigh: new THREE.CapsuleGeometry(0.075, 0.33, 4, 10),
      shin: new THREE.CapsuleGeometry(0.058, 0.33, 4, 10),
      upper: new THREE.CapsuleGeometry(0.05, 0.22, 4, 8),
      fore: new THREE.CapsuleGeometry(0.042, 0.2, 4, 8),
      hand: new THREE.SphereGeometry(0.045, 10, 8),
      head: new THREE.SphereGeometry(0.105, 18, 14),
      hair: new THREE.SphereGeometry(0.11, 18, 10, 0, Math.PI * 2, 0, Math.PI * 0.55),
      neck: new THREE.CylinderGeometry(0.05, 0.055, 0.1, 10),
      boot: new THREE.BoxGeometry(0.095, 0.075, 0.26),
      sleeve: new THREE.CapsuleGeometry(0.058, 0.1, 4, 8),
      plate: new THREE.PlaneGeometry(0.24, 0.24),
      shadow: new THREE.CircleGeometry(0.42, 24),
    };
    return g;
  };
})();

const numTex = new Map<string, THREE.Texture>();
const numberTexture = (n: number, color: string) => {
  const k = `${n}-${color}`;
  if (numTex.has(k)) return numTex.get(k)!;
  const c = document.createElement('canvas');
  c.width = 256;
  c.height = 256;
  const g = c.getContext('2d')!;
  g.clearRect(0, 0, 256, 256);
  g.fillStyle = color;
  g.font = '220px Anton, Impact, sans-serif';
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  g.fillText(String(n), 128, 140);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  numTex.set(k, t);
  return t;
};

const mats = new Map<string, THREE.Material>();
const mat = (color: string, rough = 0.75, sheen = 0) => {
  const k = `${color}-${rough}-${sheen}`;
  if (!mats.has(k)) mats.set(k, new THREE.MeshStandardMaterial({color, roughness: rough, metalness: 0}));
  return mats.get(k)!;
};

export type AthleteProps = {
  s: PlayerState;
  t: number;
  kit: Kit;
  number: number;
  skin: string;
  hairIdx: number;
  kicks: Kick[];
  actions?: Action[];
  receives?: number[]; // arrival times of passes to this player (reception pose)
  dim?: number; // 0..1 fade for non-focus players
  v2?: boolean; // animation v2 (FB-SETPIECE-001 V03+)
  keeper?: boolean; // goalkeeper set position (v2)
  guard?: number; // 0..1 defensive stance (v2): knees bent, low centre, arms out
};
export type PoseOpts = {v2?: boolean; keeper?: boolean; guard?: number};

type Pose = {
  y: number;
  lean: number;
  bank: number;
  twist: number;
  hipL: number;
  hipR: number;
  kneeL: number;
  kneeR: number;
  shL: number;
  shR: number;
  abL: number;
  abR: number;
  elL: number;
  elR: number;
  head: number;
  roll: number;
  shift: [number, number];
  yawL: number; // v2: leg rotation about its own axis (+ turns the toe outwards)
  yawR: number;
  abdL: number; // v2: leg abduction (side-steps)
  abdR: number;
};

const clamp = (x: number, a: number, b: number) => Math.max(a, Math.min(b, x));

export const computePose = (s: PlayerState, t: number, kicks: Kick[], actions: Action[] = [], receives: number[] = [], o: PoseOpts = {}): Pose => {
  if (o.v2) return computePoseV2(s, t, kicks, actions, receives, o);
  const v = s.speed;
  const run = smooth((v - 0.2) / 0.9);
  const k = clamp(v / 8, 0, 1);
  const ph = s.phase;
  const A = run * clamp(0.16 + 0.078 * v, 0, 0.8);
  const sl = Math.sin(ph);
  const cl = Math.cos(ph);
  const knee = (c: number) => 0.1 + run * (0.12 + (0.35 + 1.15 * k) * Math.pow(Math.max(0, c), 1.3));
  const idle = 1 - run;
  const breathe = Math.sin(t * 2.2 + s.phase) * 0.012;
  const p: Pose = {
    y: -run * (0.015 + 0.04 * k) * (0.5 + 0.5 * Math.cos(2 * ph)) - idle * 0.05 + breathe * idle,
    lean: 0.05 + 0.17 * k + clamp(s.accel * 0.03, -0.12, 0.14) + idle * 0.1,
    bank: clamp(-s.turn * v * 0.018, -0.22, 0.22),
    twist: 0.14 * A * sl,
    hipL: A * sl + idle * 0.18,
    hipR: -A * sl + idle * 0.12,
    kneeL: knee(cl) + idle * 0.28,
    kneeR: knee(-cl) + idle * 0.24,
    shL: -0.85 * A * sl - idle * 0.05,
    shR: 0.85 * A * sl - idle * 0.05,
    abL: 0.08 + idle * 0.12,
    abR: 0.08 + idle * 0.12,
    elL: 0.3 + 0.95 * k + idle * 0.25,
    elR: 0.3 + 0.95 * k + idle * 0.25,
    head: -0.06 - 0.1 * k,
    roll: 0,
    shift: [0, 0],
    yawL: 0,
    yawR: 0,
    abdL: 0,
    abdR: 0,
  };
  // idle (FB-SETPIECE-001): slow weight shift from foot to foot instead of a frozen pose
  if (idle > 0) {
    const ws = Math.sin(t * 1.25 + s.phase * 0.7);
    p.bank += idle * 0.028 * ws;
    p.hipL += idle * 0.05 * ws;
    p.hipR -= idle * 0.05 * ws;
    p.kneeL += idle * 0.06 * Math.max(0, -ws);
    p.kneeR += idle * 0.06 * Math.max(0, ws);
    p.twist += idle * 0.04 * Math.sin(t * 0.8 + s.phase);
    p.head += idle * 0.03 * Math.sin(t * 0.9 + 1.3 + s.phase);
  }
  // reception (inside of the right foot): the foot meets the ball slightly in front, then gives with it
  for (const rt of receives) {
    const r = t - rt;
    if (r < -0.4 || r > 0.4) continue;
    let hip: number;
    let kn: number;
    if (r < 0) {
      const u = smooth((r + 0.4) / 0.4);
      hip = 0.38 * u;
      kn = 0.25 + 0.15 * u;
    } else {
      const u = smooth(r / 0.3);
      hip = 0.38 - 0.3 * u;
      kn = 0.4 - 0.12 * u;
    }
    const w = r < -0.3 ? smooth((r + 0.4) / 0.1) : r > 0.3 ? 1 - smooth((r - 0.3) / 0.1) : 1;
    const ww = w * (1 - smooth((s.speed - 2.5) / 1.5)); // a fast runner receives in stride
    p.hipR += (hip - p.hipR) * ww;
    p.kneeR += (kn - p.kneeR) * ww;
    p.kneeL += (0.38 - p.kneeL) * ww; // flexed standing leg
    p.hipL += (0.16 - p.hipL) * ww;
    p.y += -0.03 * ww;
    p.head += (-0.32 - p.head) * ww; // eyes on the ball
    p.abL += (0.3 - p.abL) * ww;
    p.abR += (0.3 - p.abR) * ww;
  }
  // kicks (right foot): back-swing, strike at the kick time, follow-through
  for (const kk of kicks) {
    const r = t - kk.t;
    if (r < -0.34 || r > 0.3) continue;
    const pw = kk.power;
    let hip: number;
    let kn: number;
    if (r < -0.08) {
      const u = smooth((r + 0.34) / 0.26);
      hip = -0.55 * (0.5 + pw) * u;
      kn = 0.3 + 1.2 * u;
    } else if (r < 0.04) {
      const u = smooth((r + 0.08) / 0.12);
      hip = -0.55 * (0.5 + pw) + (0.55 * (0.5 + pw) + 0.35 + 0.75 * pw) * u;
      kn = 1.5 - 1.35 * u;
    } else {
      const u = (r - 0.04) / 0.26;
      hip = 0.35 + 0.75 * pw - 0.25 * u;
      kn = 0.15 + 0.2 * u;
    }
    const w = r < -0.24 ? smooth((r + 0.34) / 0.1) : r > 0.18 ? 1 - smooth((r - 0.18) / 0.12) : 1;
    p.hipR = p.hipR + (hip - p.hipR) * w;
    p.kneeR = p.kneeR + (kn - p.kneeR) * w;
    p.hipL = p.hipL + (0.12 - p.hipL) * w; // planted standing leg
    p.kneeL = p.kneeL + (0.3 - p.kneeL) * w;
    p.abL = p.abL + (0.7 - p.abL) * w; // balance arm out
    p.shL = p.shL + (-0.35 - p.shL) * w;
    p.lean = p.lean + (-0.04 - 0.08 * pw - p.lean) * w;
    p.twist = p.twist + (-0.25 * pw - p.twist) * w;
  }
  for (const a of actions) {
    if (a.type !== 'dive') continue;
    const u = (t - a.t0) / (a.t1 - a.t0);
    if (u < -0.3) continue;
    const pre = smooth((u + 0.3) / 0.3); // set position before the dive
    const d = smooth(u * 1.5);
    p.kneeL = p.kneeL + (0.5 - p.kneeL) * pre * (1 - d) + 0.2 * d;
    p.kneeR = p.kneeR + (0.5 - p.kneeR) * pre * (1 - d) + 0.2 * d;
    p.hipL += 0.3 * pre * (1 - d);
    p.hipR += 0.3 * pre * (1 - d);
    p.y += -0.12 * pre * (1 - d) - 0.62 * d;
    p.lean = p.lean * (1 - d) + 0.05 * d;
    p.roll = 1.28 * d * a.side; // sign resolved by the caller against the facing direction
    p.shift = [0, 1.15 * d * a.side];
    p.abL = p.abL + (2.7 - p.abL) * d;
    p.abR = p.abR + (2.7 - p.abR) * d;
    p.shL = p.shL * (1 - d) - 0.2 * d;
    p.shR = p.shR * (1 - d) - 0.2 * d;
    p.elL = p.elL * (1 - d) + 0.15 * d;
    p.elR = p.elR * (1 - d) + 0.15 * d;
    p.hipL = p.hipL * (1 - d) + 0.25 * d;
    p.hipR = p.hipR * (1 - d) - 0.1 * d;
  }
  return p;
};

/** Animation v2 (FB-SETPIECE-001 V03). Same inputs, richer body mechanics:
 *  - run: stride amplitude and knee drive grow with speed, the trailing shin folds up, arms bent ~90 deg and
 *    swinging against the legs, torso lean from speed AND acceleration, head counter-tilted to stay level,
 *    vertical bounce twice per stride; braking leans back
 *  - direction of travel vs facing: backpedal (legs cycle backwards) and side-steps (abduction) instead of a
 *    forward gait while moving sideways, so the feet never slide across the grass
 *  - side-foot technique for passes and finishes: foot turned out (leg external rotation), short back-swing,
 *    plant leg flexed, body over the ball, follow-through towards the target; the shot is firmer
 *  - stances: goalkeeper set position (low, hands ready), defenders on guard near the ball */
const computePoseV2 = (s: PlayerState, t: number, kicks: Kick[], actions: Action[], receives: number[], o: PoseOpts): Pose => {
  const v = s.speed;
  const run = smooth((v - 0.25) / 1.1);
  const k = clamp(v / 8, 0, 1);
  // travel direction relative to the facing direction
  const vang = Math.atan2(s.vel[1], s.vel[0]);
  let rel = vang - s.heading;
  while (rel > Math.PI) rel -= 2 * Math.PI;
  while (rel < -Math.PI) rel += 2 * Math.PI;
  const fwd = Math.cos(rel);
  const side = Math.sin(rel);
  const back = v > 0.3 ? smooth((-fwd - 0.3) / 0.4) : 0;
  const lat = v > 0.3 ? smooth((Math.abs(side) - 0.55) / 0.3) * (1 - back) : 0;
  const ph = back > 0.5 ? -s.phase : s.phase;
  const sl = Math.sin(ph);
  const cl = Math.cos(ph);
  const A = run * clamp(0.2 + 0.1 * v, 0, 0.95) * (1 - 0.75 * lat) * (1 - 0.35 * back);
  // knee: swing-leg fold (bigger at speed) + small stance flex
  const knee = (c: number, sn: number) => 0.12 + run * (0.1 + (0.45 + 1.25 * k) * Math.pow(Math.max(0, c), 1.25) + 0.12 * Math.max(0, -sn));
  const idle = 1 - run;
  const breathe = Math.sin(t * 2.2 + s.phase) * 0.012;
  const brake = clamp(-s.accel / 6, 0, 1);
  const p: Pose = {
    y: -run * (0.02 + 0.045 * k) * (0.5 + 0.5 * Math.cos(2 * ph)) - idle * 0.04 + breathe * idle,
    lean: 0.06 + 0.24 * k + clamp(s.accel * 0.045, -0.2, 0.2) - 0.1 * back + idle * 0.06,
    bank: clamp(-s.turn * v * 0.02, -0.26, 0.26),
    twist: 0.18 * A * sl,
    hipL: A * sl + idle * 0.12,
    hipR: -A * sl + idle * 0.1,
    kneeL: knee(cl, sl) + idle * 0.2,
    kneeR: knee(-cl, -sl) + idle * 0.18,
    shL: -1.05 * A * sl - idle * 0.04,
    shR: 1.05 * A * sl - idle * 0.04,
    abL: 0.1 + 0.06 * k + idle * 0.1,
    abR: 0.1 + 0.06 * k + idle * 0.1,
    elL: 0.35 + run * (0.75 + 0.45 * k) + idle * 0.2,
    elR: 0.35 + run * (0.75 + 0.45 * k) + idle * 0.2,
    head: 0,
    roll: 0,
    shift: [0, 0],
    yawL: 0.06,
    yawR: 0.06,
    abdL: 0,
    abdR: 0,
  };
  p.head = -0.55 * p.lean - 0.02; // eyes stay level
  if (brake > 0 && run > 0) {
    p.kneeL += 0.15 * brake * run;
    p.kneeR += 0.15 * brake * run;
  }
  // side-steps: legs open and close, feet stay under the hips
  if (lat > 0) {
    const sw = run * lat * clamp(0.1 + 0.05 * v, 0, 0.3) * Math.sin(s.phase);
    p.abdL += Math.max(0, sw) * 1.0 + 0.05 * lat;
    p.abdR += Math.max(0, -sw) * 1.0 + 0.05 * lat;
    p.kneeL += 0.25 * lat * run;
    p.kneeR += 0.25 * lat * run;
    p.y -= 0.05 * lat * run;
    p.lean += 0.1 * lat * run;
    p.bank += -0.05 * Math.sign(side) * lat * run;
  }
  // idle: slow weight shift
  if (idle > 0) {
    const ws = Math.sin(t * 1.25 + s.phase * 0.7);
    p.bank += idle * 0.03 * ws;
    p.hipL += idle * 0.05 * ws;
    p.hipR -= idle * 0.05 * ws;
    p.kneeL += idle * 0.06 * Math.max(0, -ws);
    p.kneeR += idle * 0.06 * Math.max(0, ws);
    p.twist += idle * 0.05 * Math.sin(t * 0.8 + s.phase);
    p.head += idle * 0.04 * Math.sin(t * 0.9 + 1.3 + s.phase);
  }
  // stances
  const set = o.keeper ? 1 - 0.6 * run * (1 - lat) : clamp(o.guard ?? 0, 0, 1) * (1 - 0.55 * run * (1 - lat));
  if (set > 0) {
    const kn = o.keeper ? 0.62 : 0.5;
    p.kneeL += (kn - p.kneeL) * set * 0.85;
    p.kneeR += (kn - p.kneeR) * set * 0.85;
    p.hipL += ((o.keeper ? 0.42 : 0.32) - p.hipL) * set * 0.7 * (1 - run);
    p.hipR += ((o.keeper ? 0.42 : 0.3) - p.hipR) * set * 0.7 * (1 - run);
    p.y += -(o.keeper ? 0.12 : 0.08) * set;
    p.lean += (o.keeper ? 0.28 : 0.18) * set;
    p.head -= (o.keeper ? 0.22 : 0.12) * set;
    p.abdL += 0.08 * set;
    p.abdR += 0.08 * set;
    if (o.keeper) {
      p.shL += (0.6 - p.shL) * set;
      p.shR += (0.6 - p.shR) * set;
      p.abL += (0.42 - p.abL) * set;
      p.abR += (0.42 - p.abR) * set;
      p.elL += (0.85 - p.elL) * set;
      p.elR += (0.85 - p.elR) * set;
    } else {
      p.abL += (0.4 - p.abL) * set * 0.8;
      p.abR += (0.4 - p.abR) * set * 0.8;
      p.elL += (0.55 - p.elL) * set * 0.6;
      p.elR += (0.55 - p.elR) * set * 0.6;
    }
  }
  // reception (inside of the right foot): the foot meets the ball, then gives with it
  for (const rt of receives) {
    const r = t - rt;
    if (r < -0.45 || r > 0.45) continue;
    let hip: number;
    let kn: number;
    if (r < 0) {
      const u = smooth((r + 0.45) / 0.45);
      hip = 0.34 * u;
      kn = 0.28 + 0.12 * u;
    } else {
      const u = smooth(r / 0.32);
      hip = 0.34 - 0.28 * u;
      kn = 0.4 - 0.14 * u;
    }
    const w = (r < -0.33 ? smooth((r + 0.45) / 0.12) : r > 0.33 ? 1 - smooth((r - 0.33) / 0.12) : 1) * (1 - smooth((v - 2.2) / 1.6));
    p.hipR += (hip - p.hipR) * w;
    p.kneeR += (kn - p.kneeR) * w;
    p.yawR += (0.85 - p.yawR) * w;
    p.kneeL += (0.36 - p.kneeL) * w;
    p.hipL += (0.12 - p.hipL) * w;
    p.y += -0.035 * w;
    p.lean += (0.16 - p.lean) * w;
    p.head = p.head + (-0.4 - p.head) * w;
    p.abL += (0.45 - p.abL) * w;
    p.abR += (0.32 - p.abR) * w;
  }
  // kicks (right foot)
  for (const kk of kicks) {
    const r = t - kk.t;
    const inside = kk.inside !== false;
    const pw = kk.power;
    const pre = inside ? (kk.shot ? 0.36 : 0.3) : 0.34;
    if (r < -pre || r > 0.42) continue;
    let hip: number;
    let kn: number;
    let yaw: number;
    // phases: approach / back-swing (-pre..-0.07), strike (-0.07..0.03), follow-through (0.03..0.42)
    const backH = inside ? -0.32 - 0.25 * (kk.shot ? 1 : 0) : -0.55 * (0.5 + pw);
    const backK = inside ? 0.85 + 0.25 * (kk.shot ? 1 : 0) : 1.5;
    const thruH = inside ? 0.38 + 0.3 * pw : 0.35 + 0.75 * pw;
    if (r < -0.07) {
      const u = smooth((r + pre) / (pre - 0.07));
      hip = backH * u;
      kn = 0.3 + (backK - 0.3) * u;
      yaw = inside ? 0.9 * u : 0;
    } else if (r < 0.03) {
      const u = smooth((r + 0.07) / 0.1);
      hip = backH + (0.12 - backH) * u;
      kn = backK + (0.12 - backK) * u;
      yaw = inside ? 0.9 : 0;
    } else {
      const u = smooth((r - 0.03) / 0.39);
      hip = 0.12 + (thruH - 0.12) * smooth((r - 0.03) / 0.14) - 0.3 * u;
      kn = 0.12 + 0.3 * u;
      yaw = inside ? 0.9 * (1 - u) : 0;
    }
    const w = r < -pre + 0.1 ? smooth((r + pre) / 0.1) : r > 0.3 ? 1 - smooth((r - 0.3) / 0.12) : 1;
    p.hipR += (hip - p.hipR) * w;
    p.kneeR += (kn - p.kneeR) * w;
    p.yawR += (yaw - p.yawR) * w;
    p.hipL += (0.08 - p.hipL) * w; // planted beside the ball
    p.kneeL += (0.38 - p.kneeL) * w;
    p.y += -0.04 * w;
    p.abL += (0.85 - p.abL) * w; // balance arm out
    p.shL += (-0.15 - p.shL) * w;
    p.abR += (0.35 - p.abR) * w;
    p.lean += ((kk.shot ? 0.2 : 0.12) - p.lean) * w; // over the ball keeps it low
    p.twist += ((inside ? 0.28 : -0.25) * pw * (r < 0 ? 1 : -0.6) - p.twist) * w;
    p.head += (-0.35 - p.head) * w * (r < 0.1 ? 1 : 0.5);
  }
  for (const a of actions) {
    if (a.type !== 'dive') continue;
    const u = (t - a.t0) / (a.t1 - a.t0);
    if (u < -0.3) continue;
    const pre = smooth((u + 0.3) / 0.3); // set and load the legs
    const d = smooth(u * 1.4);
    p.kneeL = p.kneeL + (0.7 - p.kneeL) * pre * (1 - d) + 0.25 * d;
    p.kneeR = p.kneeR + (0.7 - p.kneeR) * pre * (1 - d) + 0.15 * d;
    p.y += -0.14 * pre * (1 - d) - 0.62 * d;
    p.lean = p.lean * (1 - d) + 0.05 * d;
    p.roll = 1.32 * d * a.side;
    p.shift = [0, 1.25 * d * a.side];
    p.abL = p.abL + (2.75 - p.abL) * d;
    p.abR = p.abR + (2.75 - p.abR) * d;
    p.shL = p.shL * (1 - d) - 0.15 * d;
    p.shR = p.shR * (1 - d) - 0.15 * d;
    p.elL = p.elL * (1 - d) + 0.1 * d;
    p.elR = p.elR * (1 - d) + 0.1 * d;
    p.hipL = p.hipL * (1 - d) + 0.3 * d;
    p.hipR = p.hipR * (1 - d) - 0.05 * d;
    p.head = p.head * (1 - d) - 0.1 * d;
  }
  return p;
};

const HIP = 0.93;

export const Athlete: React.FC<AthleteProps> = ({s, t, kit, number, skin, hairIdx, kicks, actions, receives, dim = 0, v2, keeper, guard}) => {
  const g = G();
  const p = computePose(s, t, kicks, actions, receives, {v2, keeper, guard});
  const h = s.heading;
  // world -> three: rotation about Y so local +Z points along the heading
  const rotY = Math.atan2(Math.cos(h), -Math.sin(h));
  const leftX = Math.cos(h + Math.PI / 2);
  const leftY = Math.sin(h + Math.PI / 2);
  // dive roll: towards the keeper's left (+X local) is a negative z rotation
  const toLeft = p.shift[1] * leftY + p.shift[0] * leftX;
  const roll = toLeft !== 0 ? -Math.sign(toLeft) * Math.abs(p.roll) : 0;
  const pos = W3([s.pos[0] + p.shift[0], s.pos[1] + p.shift[1], 0]);
  const shirt = mat(kit.shirt, 0.8);
  const shorts = mat(kit.shorts, 0.8);
  const socks = mat(kit.socks, 0.85);
  const skinM = mat(skin, 0.6);
  const hairM = mat(HAIR[hairIdx % HAIR.length], 0.9);
  const boot = mat('#14161A', 0.45);
  const trim = mat(kit.trim, 0.6);
  const tex = numberTexture(number, kit.number);
  // yaw: + turns the toe outwards (left leg is +X local, so its outward rotation is the opposite sign)
  const leg = (side: 1 | -1, hip: number, kn: number, yaw = 0, abd = 0) => (
    <group position={[0.1 * side, 0, 0]} rotation={[-hip, side * yaw, side * abd]}>
      <mesh geometry={g.thigh} material={shorts} position={[0, -0.12, 0]} castShadow scale={[1.08, 0.55, 1.08]} />
      <mesh geometry={g.thigh} material={skinM} position={[0, -0.24, 0]} castShadow />
      <group position={[0, -0.45, 0]} rotation={[kn, 0, 0]}>
        <mesh geometry={g.shin} material={socks} position={[0, -0.2, 0]} castShadow />
        <mesh geometry={g.boot} material={boot} position={[0, -0.43, 0.06]} castShadow />
      </group>
    </group>
  );
  const arm = (side: 1 | -1, sh: number, ab: number, el: number) => (
    <group position={[0.2 * side, 0.46, 0]} rotation={[-sh, 0, ab * side]}>
      <mesh geometry={g.sleeve} material={shirt} position={[0, -0.06, 0]} castShadow />
      <mesh geometry={g.upper} material={skinM} position={[0, -0.15, 0]} castShadow />
      <group position={[0, -0.29, 0]} rotation={[-el, 0, 0]}>
        <mesh geometry={g.fore} material={skinM} position={[0, -0.13, 0]} castShadow />
        <mesh geometry={g.hand} material={skinM} position={[0, -0.27, 0]} castShadow />
      </group>
    </group>
  );
  return (
    <group position={pos} rotation={[0, rotY, 0]}>
      <mesh geometry={g.shadow} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.012, 0]}>
        <meshBasicMaterial color="#000" transparent opacity={0.18 * (1 - dim)} depthWrite={false} />
      </mesh>
      <group rotation={[0, 0, roll]} position={[0, Math.max(-HIP + 0.22, p.y) + HIP, 0]}>
        {/* bank into turns, applied at the hips so the feet stay under the body */}
        <group rotation={[0, 0, p.bank]}>
          <mesh geometry={g.pelvis} material={shorts} rotation={[0, 0, Math.PI / 2]} position={[0, 0.02, 0]} castShadow />
          {leg(1, p.hipL, p.kneeL, p.yawL, p.abdL)}
          {leg(-1, p.hipR, p.kneeR, p.yawR, p.abdR)}
          <group rotation={[p.lean, p.twist, 0]}>
            <mesh geometry={g.torso} material={shirt} position={[0, 0.29, 0]} scale={[1.2, 1, 0.78]} castShadow />
            <mesh geometry={g.neck} material={skinM} position={[0, 0.58, 0]} />
            <mesh geometry={g.plate} position={[0, 0.33, -0.122]} rotation={[0, Math.PI, 0]}>
              <meshStandardMaterial map={tex} transparent roughness={0.8} depthWrite={false} />
            </mesh>
            <mesh geometry={g.plate} position={[0.07, 0.42, 0.121]} scale={[0.32, 0.32, 1]}>
              <meshStandardMaterial map={tex} transparent roughness={0.8} depthWrite={false} />
            </mesh>
            <mesh position={[0, 0.555, 0]} rotation={[Math.PI / 2, 0, 0]} material={trim}>
              <torusGeometry args={[0.07, 0.014, 6, 16]} />
            </mesh>
            {arm(1, p.shL, p.abL, p.elL)}
            {arm(-1, p.shR, p.abR, p.elR)}
            <group position={[0, 0.72, 0.01]} rotation={[p.head, 0, 0]}>
              <mesh geometry={g.head} material={skinM} scale={[0.95, 1.1, 1]} castShadow />
              <mesh geometry={g.hair} material={hairM} position={[0, 0.02, -0.008]} scale={[0.97, 1.05, 1.02]} />
            </group>
          </group>
        </group>
      </group>
    </group>
  );
};
