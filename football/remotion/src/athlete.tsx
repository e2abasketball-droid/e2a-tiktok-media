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
};

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
};

const clamp = (x: number, a: number, b: number) => Math.max(a, Math.min(b, x));

export const computePose = (s: PlayerState, t: number, kicks: Kick[], actions: Action[] = [], receives: number[] = []): Pose => {
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

const HIP = 0.93;

export const Athlete: React.FC<AthleteProps> = ({s, t, kit, number, skin, hairIdx, kicks, actions, receives, dim = 0}) => {
  const g = G();
  const p = computePose(s, t, kicks, actions, receives);
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
  const leg = (side: 1 | -1, hip: number, kn: number) => (
    <group position={[0.1 * side, 0, 0]} rotation={[-hip, 0, 0]}>
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
          {leg(1, p.hipL, p.kneeL)}
          {leg(-1, p.hipR, p.kneeR)}
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
