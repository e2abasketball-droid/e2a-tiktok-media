// E2A 3D engine — RealisticBasketballPlayer: a stylised but anatomical athlete built from smooth
// lathe-profiled limbs (thigh/calf/upper arm/forearm muscle shapes), a V-tapered torso wearing a
// textured jersey (trim, side panels, number front and back), loose shorts, socks and basketball
// shoes. Every part is placed from the procedural rig pose (rig.ts), so animation and anatomy stay
// in one place. No faces by design (brand rule for recreations); team colours come from `kit`.
import React from 'react';
import * as THREE from 'three';
import type {V3} from '../tactical/geometry.ts';
import type {Pose} from './rig.ts';

/** play world (x across, y from baseline, z up) -> three.js (x, y up, z toward the camera side) */
export const W3 = (p: V3): [number, number, number] => [p[0], p[2], -p[1]];

export type Kit = {jersey: string; trim: string; number: string; shorts: string; shoe: string; sole: string; sock: string};

export const KITS: Record<'O' | 'X', Kit> = {
  // E2A: navy with gold
  O: {jersey: '#0E2147', trim: '#C9A24D', number: '#E3BE68', shorts: '#0E2147', shoe: '#F2F2F0', sole: '#1A1A1A', sock: '#F4F4F4'},
  // opponent: white with crimson
  X: {jersey: '#F3F1EC', trim: '#B8322A', number: '#B8322A', shorts: '#F3F1EC', shoe: '#1D1F24', sole: '#F2F2F2', sock: '#1D1F24'},
};

export const SKINS = ['#6B4630', '#C68E63', '#8D5A3B', '#E0B08A', '#4E3122', '#B57A52', '#9C6847', '#D9A27A', '#5C3B28', '#A87250'];

// ---------- geometry (built once) ----------
const prof = (pts: [number, number][], seg = 22, cap = 0) => {
  const all: [number, number][] = [...pts];
  if (cap > 0) {
    const r0 = pts[0][1];
    const r1 = pts[pts.length - 1][1];
    for (let i = 1; i <= 5; i++) {
      const a = (i / 5) * (Math.PI / 2);
      all.unshift([-Math.sin(a) * cap * 0.5, r0 * Math.cos(a)]);
      all.push([1 + Math.sin(a) * cap * 0.5, r1 * Math.cos(a)]);
    }
  }
  return new THREE.LatheGeometry(
    all.map(([v, r]) => new THREE.Vector2(Math.max(0.0005, r), v)),
    seg,
    Math.PI, // so u = 0.5 is the front (+Z)
  );
};

const smoothProfile = (keys: [number, number][], n = 14): [number, number][] => {
  const out: [number, number][] = [];
  for (let i = 0; i <= n; i++) {
    const v = i / n;
    let j = 0;
    while (j < keys.length - 2 && v > keys[j + 1][0]) j++;
    const [v0, r0] = keys[j];
    const [v1, r1] = keys[j + 1];
    const u = Math.max(0, Math.min(1, (v - v0) / (v1 - v0)));
    const e = u * u * (3 - 2 * u);
    out.push([v, r0 + (r1 - r0) * e]);
  }
  return out;
};

const G = (() => {
  // radii in metres for a 2.00 m athlete; length along +Y is 1 (scaled to the bone length)
  const thigh = prof(smoothProfile([[0, 0.088], [0.25, 0.094], [0.62, 0.076], [0.9, 0.058], [1, 0.054]]), 24, 0.2);
  const shin = prof(smoothProfile([[0, 0.054], [0.22, 0.066], [0.5, 0.052], [0.85, 0.036], [1, 0.034]]), 24, 0.14);
  const upper = prof(smoothProfile([[0, 0.062], [0.3, 0.058], [0.55, 0.051], [0.85, 0.042], [1, 0.038]]), 22, 0.26);
  const fore = prof(smoothProfile([[0, 0.038], [0.22, 0.045], [0.7, 0.031], [1, 0.026]]));
  const neck = prof(smoothProfile([[0, 0.07], [0.5, 0.06], [1, 0.056]], 6), 18);
  // torso from the waist (0) to the base of the neck (1): hips, waist, lats/chest, shoulder slope
  const torso = prof(
    smoothProfile([[0, 0.162], [0.18, 0.145], [0.42, 0.155], [0.66, 0.188], [0.8, 0.186], [0.92, 0.15], [1, 0.072]], 20),
    40,
  );
  const shortsBody = prof(smoothProfile([[0, 0.17], [0.5, 0.166], [0.8, 0.15], [1, 0.06]], 8), 32);
  const shortsLeg = prof(smoothProfile([[0, 0.128], [0.3, 0.122], [1, 0.112]], 6), 20);
  const sock = prof(smoothProfile([[0, 0.04], [1, 0.044]], 3), 14);
  const sphere = new THREE.SphereGeometry(1, 28, 20);
  const hair = new THREE.SphereGeometry(1, 28, 14, 0, Math.PI * 2, 0, Math.PI * 0.52);
  const shoe = new THREE.CapsuleGeometry(1, 1, 6, 16);
  return {thigh, shin, upper, fore, neck, torso, shortsBody, shortsLeg, sock, sphere, hair, shoe};
})();

// ---------- sculpted head (no facial detail, but a real skull, jaw, brow, nose and hairline) ----------
const headCache = new Map<string, THREE.BufferGeometry>();
const gauss = (d2: number, s: number) => Math.exp(-d2 / (2 * s * s));
export const headGeo = (skin: string, hair = '#16100B') => {
  const hit = headCache.get(skin);
  if (hit) return hit;
  const g = new THREE.SphereGeometry(1, 48, 36);
  const pos = g.attributes.position as THREE.BufferAttribute;
  const cols: number[] = [];
  const cs = new THREE.Color(skin);
  const ch = new THREE.Color(hair);
  for (let i = 0; i < pos.count; i++) {
    let x = pos.getX(i);
    let y = pos.getY(i);
    let z = pos.getZ(i);
    // jaw narrows toward the chin, chin forward, back of skull fuller
    if (y < -0.1) x *= 1 - 0.32 * Math.min(1, (-y - 0.1) / 0.9);
    if (y < -0.35 && z > 0) z *= 1 - 0.18 * ((-y - 0.35) / 0.65);
    if (y > 0.0 && z < 0) z *= 1.08;
    let r = 1;
    // brow ridge, nose, cheekbones, eye sockets (front = +z)
    if (z > 0) {
      r += 0.05 * gauss(x * x + (y - 0.2) ** 2 * 6, 0.35) * z;
      r += 0.13 * gauss(x * x * 9 + (y + 0.08) ** 2 * 2.2, 0.16) * z;
      r -= 0.04 * (gauss((x - 0.36) ** 2 + (y - 0.08) ** 2, 0.12) + gauss((x + 0.36) ** 2 + (y - 0.08) ** 2, 0.12)) * z;
      r += 0.03 * (gauss((x - 0.55) ** 2 + (y + 0.12) ** 2, 0.15) + gauss((x + 0.55) ** 2 + (y + 0.12) ** 2, 0.15));
      r += 0.05 * gauss(x * x * 3 + (y + 0.82) ** 2 * 2, 0.2) * z; // chin
    }
    pos.setXYZ(i, x * r, y * r, z * r);
    // hairline: short cropped hair on the top/back of the skull
    const hairLine = z > 0 ? 0.42 - 0.1 * Math.abs(x) : -0.05 - 0.25 * Math.max(0, -z);
    const hairW = Math.min(1, Math.max(0, (y - hairLine) / 0.08));
    const c = cs.clone().lerp(ch, hairW * 0.92);
    cols.push(c.r, c.g, c.b);
  }
  g.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3));
  g.computeVertexNormals();
  headCache.set(skin, g);
  return g;
};

// ---------- jersey texture (per team + number) ----------
const texCache = new Map<string, THREE.Texture>();
const jerseyTex = (kit: Kit, num: string, kind: 'jersey' | 'shorts') => {
  const key = `${kind}|${kit.jersey}|${kit.trim}|${num}`;
  const hit = texCache.get(key);
  if (hit) return hit;
  const W = 1024;
  const H = 512;
  const c = typeof OffscreenCanvas !== 'undefined' ? new OffscreenCanvas(W, H) : (document.createElement('canvas') as unknown as OffscreenCanvas);
  c.width = W;
  c.height = H;
  const g = c.getContext('2d') as OffscreenCanvasRenderingContext2D;
  g.fillStyle = kind === 'jersey' ? kit.jersey : kit.shorts;
  g.fillRect(0, 0, W, H);
  // fabric: fine mesh noise
  for (let i = 0; i < 9000; i++) {
    const x = (i * 7919) % W;
    const y = ((i * 104729) % H) | 0;
    g.fillStyle = i % 2 ? 'rgba(255,255,255,0.035)' : 'rgba(0,0,0,0.05)';
    g.fillRect(x, y, 2, 2);
  }
  if (kind === 'jersey') {
    // v = 1 is the top of the texture (lathe v grows with height) -> canvas y = (1 - v) * H
    // side panels (under the arms: u = 0.25 and 0.75)
    g.fillStyle = kit.trim;
    for (const u of [0.25, 0.75]) g.fillRect(u * W - 14, H * 0.08, 28, H * 0.9);
    // armholes + collar trim near the top
    g.fillRect(0, 0, W, 16);
    // V-neck at the front (u = 0.5)
    g.beginPath();
    g.moveTo(W * 0.5 - 70, 0);
    g.lineTo(W * 0.5, 70);
    g.lineTo(W * 0.5 + 70, 0);
    g.lineTo(W * 0.5 + 52, 0);
    g.lineTo(W * 0.5, 50);
    g.lineTo(W * 0.5 - 52, 0);
    g.closePath();
    g.fill();
    // numbers: front (u = 0.5) and back (u = 0 / 1)
    g.font = '900 150px Anton, Impact, sans-serif';
    g.textAlign = 'center';
    g.textBaseline = 'middle';
    const drawNum = (x: number, s: number) => {
      g.save();
      g.translate(x, H * 0.42);
      g.scale(0.62 * s, 1);
      g.lineWidth = 10;
      g.strokeStyle = kit.trim === kit.number ? kit.jersey : kit.trim;
      g.strokeText(num, 0, 0);
      g.fillStyle = kit.number;
      g.fillText(num, 0, 0);
      g.restore();
    };
    drawNum(W * 0.5, 1);
    drawNum(0, 1.2);
    drawNum(W, 1.2);
    // hem
    g.fillStyle = 'rgba(0,0,0,0.12)';
    g.fillRect(0, H - 10, W, 10);
  } else {
    g.fillStyle = kit.trim;
    for (const u of [0.25, 0.75]) g.fillRect(u * W - 10, 0, 20, H);
    g.fillRect(0, 0, W, 24); // waistband
  }
  const t = new THREE.CanvasTexture(c as unknown as HTMLCanvasElement);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  texCache.set(key, t);
  return t;
};

const matCache = new Map<string, THREE.Material>();
const mat = (key: string, make: () => THREE.Material) => {
  const hit = matCache.get(key);
  if (hit) return hit;
  const m = make();
  matCache.set(key, m);
  return m;
};

// ---------- placing segments ----------
const UP = new THREE.Vector3(0, 1, 0);
const tmpA = new THREE.Vector3();
const tmpB = new THREE.Vector3();

type Seg = {pos: [number, number, number]; quat: THREE.Quaternion; len: number};
const seg = (a: V3, b: V3): Seg => {
  const A = W3(a);
  const B = W3(b);
  tmpA.set(A[0], A[1], A[2]);
  tmpB.set(B[0] - A[0], B[1] - A[1], B[2] - A[2]);
  const len = tmpB.length();
  const q = new THREE.Quaternion().setFromUnitVectors(UP, tmpB.normalize());
  return {pos: A, quat: q, len};
};

/** quaternion for a frame: +Y along `upDir`, +Z toward `fwdDir` (world play coordinates) */
const frameQuat = (upDir: V3, fwdDir: V3) => {
  const u = new THREE.Vector3(...W3(upDir)).normalize();
  const f0 = new THREE.Vector3(...W3(fwdDir));
  const f = f0.sub(u.clone().multiplyScalar(f0.dot(u))).normalize();
  const r = new THREE.Vector3().crossVectors(u, f).normalize();
  const m = new THREE.Matrix4().makeBasis(r, u, f);
  return new THREE.Quaternion().setFromRotationMatrix(m);
};

type Props = {pose: Pose; team: 'O' | 'X'; num: string; skin: string; opacity?: number; highlight?: number};

const Limb: React.FC<{a: V3; b: V3; geo: THREE.BufferGeometry; m: THREE.Material; s: number; from?: number; to?: number}> = ({a, b, geo, m, s, from = 0, to = 1}) => {
  const S = seg(a, b);
  const off = new THREE.Vector3(0, S.len * from, 0).applyQuaternion(S.quat);
  return (
    <mesh geometry={geo} material={m} position={[S.pos[0] + off.x, S.pos[1] + off.y, S.pos[2] + off.z]} quaternion={S.quat} scale={[s, S.len * (to - from), s]} castShadow receiveShadow />
  );
};

export const Athlete: React.FC<Props> = ({pose: P, team, num, skin}) => {
  const kit = KITS[team];
  const k = P.dims.H / 2;
  const skinM = mat(`skin${skin}`, () => new THREE.MeshPhysicalMaterial({color: skin, roughness: 0.46, metalness: 0.0, clearcoat: 0.18, clearcoatRoughness: 0.45}));
  const jerseyM = mat(`jersey${team}${num}`, () => new THREE.MeshStandardMaterial({map: jerseyTex(kit, num, 'jersey'), roughness: 0.72, metalness: 0.0, side: THREE.DoubleSide}));
  const shortsM = mat(`shorts${team}`, () => new THREE.MeshStandardMaterial({map: jerseyTex(kit, num, 'shorts'), roughness: 0.75, side: THREE.DoubleSide}));
  const shoeM = mat(`shoe${team}`, () => new THREE.MeshStandardMaterial({color: kit.shoe, roughness: 0.42}));
  const soleM = mat(`sole${team}`, () => new THREE.MeshStandardMaterial({color: kit.sole, roughness: 0.6}));
  const sockM = mat(`sock${team}`, () => new THREE.MeshStandardMaterial({color: kit.sock, roughness: 0.85}));
  const headM = mat('headV', () => new THREE.MeshPhysicalMaterial({vertexColors: true, roughness: 0.5, clearcoat: 0.15, clearcoatRoughness: 0.5}));

  const up: V3 = [P.chest[0] - P.pelvis[0], P.chest[1] - P.pelvis[1], P.chest[2] - P.pelvis[2]];
  const chestFwd: V3 = [Math.cos(P.chestYaw), Math.sin(P.chestYaw), 0];
  const hipFwd: V3 = [Math.cos(P.heading), Math.sin(P.heading), 0];
  const torsoQ = frameQuat(up, chestFwd);
  const hipQ = frameQuat([0, 0, 1], hipFwd);
  const waist: V3 = [P.pelvis[0], P.pelvis[1], P.pelvis[2] - 0.05 * k];
  const torsoLen = Math.hypot(...up) + 0.11 * k;
  const Wp = W3(waist);
  const headW = W3(P.head);
  const neckBase: V3 = P.chest;
  const headQ = frameQuat([P.head[0] - P.chest[0], P.head[1] - P.chest[1], P.head[2] - P.chest[2]], chestFwd);

  const parts: React.ReactNode[] = [];
  // torso (jersey) — elliptical: wide across the shoulders, shallow front-to-back
  parts.push(<mesh key="torso" geometry={G.torso} material={jerseyM} position={Wp} quaternion={torsoQ} scale={[1.0 * k, torsoLen, 0.66 * k]} castShadow receiveShadow />);
  // shorts body around the hips
  const sb: V3 = [P.pelvis[0], P.pelvis[1], P.pelvis[2] - 0.2 * k];
  parts.push(<mesh key="shorts" geometry={G.shortsBody} material={shortsM} position={W3(sb)} quaternion={hipQ} scale={[1.04 * k, 0.25 * k, 0.98 * k]} castShadow receiveShadow />);
  // neck + head + hair
  parts.push(<Limb key="neck" a={[neckBase[0], neckBase[1], neckBase[2] - 0.04 * k]} b={P.head} geo={G.neck} m={skinM} s={k} to={0.62} />);
  parts.push(<mesh key="head" geometry={headGeo(skin)} material={headM} position={headW} quaternion={headQ} scale={[0.082 * k, 0.112 * k, 0.098 * k]} castShadow />);
  // ears / jaw hint (gives the head a readable orientation without a face)
  for (const s of [-1, 1]) {
    const r: V3 = [Math.sin(P.chestYaw) * s, -Math.cos(P.chestYaw) * s, 0];
    const e: V3 = [P.head[0] + r[0] * 0.08 * k, P.head[1] + r[1] * 0.08 * k, P.head[2] - 0.0];
    parts.push(<mesh key={`ear${s}`} geometry={G.sphere} material={skinM} position={W3(e)} scale={[0.018 * k, 0.03 * k, 0.022 * k]} />);
  }
  for (let i = 0; i < 2; i++) {
    const sfx = i === 0 ? 'L' : 'R';
    // legs
    parts.push(<Limb key={`th${sfx}`} a={P.hip[i]} b={P.knee[i]} geo={G.thigh} m={skinM} s={k} from={0.12} />);
    parts.push(<Limb key={`sl${sfx}`} a={P.hip[i]} b={P.knee[i]} geo={G.shortsLeg} m={shortsM} s={k} from={0.0} to={0.56} />);
    parts.push(<Limb key={`sh${sfx}`} a={P.knee[i]} b={P.ankle[i]} geo={G.shin} m={skinM} s={k} />);
    parts.push(<Limb key={`so${sfx}`} a={P.knee[i]} b={P.ankle[i]} geo={G.sock} m={sockM} s={k} from={0.78} to={1.03} />);
    // shoe: capsule along heel -> toe, flattened
    const heel: V3 = [P.ankle[i][0] - (P.toe[i][0] - P.ankle[i][0]) * 0.32, P.ankle[i][1] - (P.toe[i][1] - P.ankle[i][1]) * 0.32, P.ankle[i][2] - 0.045 * k];
    const S = seg(heel, P.toe[i]);
    const mid = W3([(heel[0] + P.toe[i][0]) / 2, (heel[1] + P.toe[i][1]) / 2, (heel[2] + P.toe[i][2]) / 2]);
    const shoeQ = S.quat;
    parts.push(<mesh key={`shoe${sfx}`} geometry={G.shoe} material={shoeM} position={mid} quaternion={shoeQ} scale={[0.052 * k, S.len * 0.42, 0.06 * k]} castShadow receiveShadow />);
    parts.push(<mesh key={`sole${sfx}`} geometry={G.shoe} material={soleM} position={[mid[0], mid[1] - 0.026 * k, mid[2]]} quaternion={shoeQ} scale={[0.056 * k, S.len * 0.45, 0.03 * k]} castShadow />);
    // arms: deltoid, upper arm, elbow, forearm, hand
    parts.push(<mesh key={`dl${sfx}`} geometry={G.sphere} material={skinM} position={W3(P.shoulder[i])} scale={[0.06 * k, 0.058 * k, 0.058 * k]} castShadow />);
    parts.push(<Limb key={`ua${sfx}`} a={P.shoulder[i]} b={P.elbow[i]} geo={G.upper} m={skinM} s={k} />);
    parts.push(<Limb key={`fa${sfx}`} a={P.elbow[i]} b={P.wrist[i]} geo={G.fore} m={skinM} s={k} />);
    const hm: V3 = [(P.wrist[i][0] + P.hand[i][0]) / 2, (P.wrist[i][1] + P.hand[i][1]) / 2, (P.wrist[i][2] + P.hand[i][2]) / 2];
    const HS = seg(P.wrist[i], P.hand[i]);
    parts.push(<mesh key={`hd${sfx}`} geometry={G.sphere} material={skinM} position={W3(hm)} quaternion={HS.quat} scale={[0.034 * k, 0.062 * k, 0.026 * k]} castShadow />);
  }
  return <group>{parts}</group>;
};
