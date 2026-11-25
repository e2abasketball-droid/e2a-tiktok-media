// E2A YouTube Comedy — "Every Court Has One" stylised toon athlete.
// One reusable character model: big expressive head (eyes with lids, thick brows, lip-synced
// mouth projected on the face), sleeveless jersey with number, shorts, socks, shoes.
// The skeleton is pure forward kinematics (fk) so the renderer, the ball and the cameras all read
// the same joint positions. Character looks come from a `Look` record (see characters.ts).
import React from 'react';
import * as THREE from 'three';
import type {Face, Pose} from './pose';

export type Look = {
  id: string;
  skin: string;
  hair: string;
  hairStyle: 'fade' | 'curls';
  jersey: string;
  trim: string;
  number: string;
  numColor: string;
  shorts: string;
  shoe: string;
  shoeAccent: string;
  sock: string;
  headband?: {base: string; stripe: string};
  wristband?: string;
  /** brow thickness multiplier (AND1 = very expressive brows) */
  brow: number;
  browColor: string;
  iris: string;
  /** body build: shoulder width multiplier */
  build: number;
};

// ---------- dimensions (metres) ----------
export const D = {
  shin: 0.44,
  thigh: 0.44,
  foot: 0.08,
  hipW: 0.095,
  torso: 0.52,
  shY: 0.445,
  shW: 0.215,
  upper: 0.29,
  fore: 0.26,
  neck: 0.06,
  headR: 0.21,
  headY: 0.165,
};

export type Bone = 'root' | 'spine' | 'head' | 'lSh' | 'lUp' | 'lEl' | 'lHand' | 'rSh' | 'rUp' | 'rEl' | 'rHand' | 'lHip' | 'lKnee' | 'lAnkle' | 'rHip' | 'rKnee' | 'rAnkle';
export type Skel = Record<Bone, THREE.Matrix4>;

const V = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
const M = () => new THREE.Matrix4();
const TR = (x: number, y: number, z: number) => M().makeTranslation(x, y, z);
const ROT = (x: number, y: number, z: number, order: THREE.EulerOrder = 'XYZ') => M().makeRotationFromEuler(new THREE.Euler(x, y, z, order));
const mul = (...ms: THREE.Matrix4[]) => ms.reduce((a, b) => a.clone().multiply(b));

const fkAt = (p: Pose, rootY: number, build = 1): Skel => {
  const root = mul(TR(p.x, rootY, p.z), ROT(0, p.yaw, 0), ROT(p.lean, 0, p.roll));
  const spine = mul(root, TR(0, 0.02, 0), ROT(p.spineBend, p.spineTwist, p.spineSide, 'YXZ'));
  const head = mul(spine, TR(0, D.torso + D.neck, 0.0), ROT(p.headPitch, p.headYaw, p.headRoll, 'YXZ'));
  const arm = (s: 1 | -1, pitch: number, out: number, twist: number, elbow: number) => {
    const sh = mul(spine, TR(s * D.shW * build, D.shY, -0.01), ROT(-pitch, 0, s * out, 'XZY'));
    const up = mul(sh, ROT(0, s * twist, 0));
    const el = mul(up, TR(0, -D.upper, 0), ROT(-elbow, 0, 0));
    const hand = mul(el, TR(0, -D.fore, 0));
    return {sh, up, el, hand};
  };
  const L = arm(1, p.lShPitch, p.lShOut, p.lShTwist, p.lElbow);
  const R = arm(-1, p.rShPitch, p.rShOut, p.rShTwist, p.rElbow);
  const leg = (s: 1 | -1, hip: number, out: number, knee: number, ankle: number) => {
    const h = mul(root, TR(s * D.hipW, -0.02, 0), ROT(-hip, 0, s * out, 'XZY'));
    const k = mul(h, TR(0, -D.thigh, 0), ROT(knee, 0, 0));
    const a = mul(k, TR(0, -D.shin, 0), ROT(-ankle - knee + hip, 0, 0));
    return {h, k, a};
  };
  const LL = leg(1, p.lHip, p.lHipOut, p.lKnee, p.lAnkle);
  const RL = leg(-1, p.rHip, p.rHipOut, p.rKnee, p.rAnkle);
  return {
    root, spine, head,
    lSh: L.sh, lUp: L.up, lEl: L.el, lHand: L.hand,
    rSh: R.sh, rUp: R.up, rEl: R.el, rHand: R.hand,
    lHip: LL.h, lKnee: LL.k, lAnkle: LL.a,
    rHip: RL.h, rKnee: RL.k, rAnkle: RL.a,
  };
};

const posOf = (m: THREE.Matrix4) => V(0, 0, 0).applyMatrix4(m);

/** full FK with automatic ground contact: the lowest foot touches the floor (+ p.lift when airborne);
 *  sitting lerps the pelvis down onto the floor. */
export const fk = (p: Pose, build = 1): Skel => {
  const probe = fkAt(p, 0, build);
  const minAnkle = Math.min(posOf(probe.lAnkle).y, posOf(probe.rAnkle).y);
  const stand = D.foot - minAnkle + Math.max(0, p.lift);
  const seat = 0.15;
  const y = p.sit > 0 ? stand + (seat - stand) * p.sit : stand;
  return fkAt(p, y, build);
};

export const bonePos = (s: Skel, b: Bone) => posOf(s[b]);
/** where a held ball sits: in front of the palm of a hand */
export const ballInHand = (s: Skel, side: 'l' | 'r') => V(0, -0.1, 0.07).applyMatrix4(s[side === 'l' ? 'lHand' : 'rHand']);
/** world point between the eyes, and the head's forward direction */
export const eyePoint = (s: Skel) => V(0, D.headY + 0.02, 0.12).applyMatrix4(s.head);

// ---------- geometry ----------
const prof = (keys: [number, number][], seg = 32) => {
  const pts: THREE.Vector2[] = [];
  const n = 18;
  for (let i = 0; i <= n; i++) {
    const v = i / n;
    let j = 0;
    while (j < keys.length - 2 && v > keys[j + 1][0]) j++;
    const [v0, r0] = keys[j];
    const [v1, r1] = keys[j + 1];
    const u = Math.max(0, Math.min(1, (v - v0) / (v1 - v0)));
    const e = u * u * (3 - 2 * u);
    pts.push(new THREE.Vector2(Math.max(0.001, r0 + (r1 - r0) * e), v));
  }
  return new THREE.LatheGeometry(pts, seg, Math.PI);
};

const G = (() => {
  const torso = prof([[0, 0.165], [0.2, 0.152], [0.45, 0.17], [0.7, 0.198], [0.84, 0.2], [0.94, 0.16], [1, 0.07]], 40);
  const shorts = prof([[0, 0.175], [0.6, 0.172], [1, 0.172]], 32);
  const shortLeg = prof([[0, 0.112], [1, 0.098]], 24);
  const cap = (r: number, l: number) => new THREE.CapsuleGeometry(r, l, 8, 18);
  return {
    torso, shorts, shortLeg,
    thigh: cap(0.074, D.thigh - 0.06),
    shin: cap(0.058, D.shin - 0.06),
    upper: cap(0.053, D.upper - 0.05),
    fore: cap(0.046, D.fore - 0.05),
    sphere: new THREE.SphereGeometry(1, 40, 28),
    lowSphere: new THREE.SphereGeometry(1, 20, 14),
    capTop: new THREE.SphereGeometry(1, 40, 18, 0, Math.PI * 2, 0, Math.PI * 0.5),
    cyl: new THREE.CylinderGeometry(1, 1, 1, 24, 1, true),
    cylClosed: new THREE.CylinderGeometry(1, 1, 1, 24),
    finger: cap(0.014, 0.06),
    shoe: new THREE.CapsuleGeometry(1, 1.6, 8, 20),
    neck: new THREE.CylinderGeometry(0.058, 0.066, 0.12, 20),
  };
})();

const matCache = new Map<string, THREE.Material>();
const std = (color: string, rough = 0.62, extra: Partial<THREE.MeshStandardMaterialParameters> = {}) => {
  const key = `${color}|${rough}|${JSON.stringify(extra)}`;
  let m = matCache.get(key);
  if (!m) {
    m = new THREE.MeshStandardMaterial({color, roughness: rough, ...extra});
    matCache.set(key, m);
  }
  return m;
};

const texCache = new Map<string, THREE.Texture>();
const jerseyTex = (look: Look) => {
  const hit = texCache.get(look.id);
  if (hit) return hit;
  const W = 1024;
  const H = 512;
  const c = document.createElement('canvas');
  c.width = W;
  c.height = H;
  const g = c.getContext('2d')!;
  g.fillStyle = look.jersey;
  g.fillRect(0, 0, W, H);
  for (let i = 0; i < 12000; i++) {
    g.fillStyle = i % 2 ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.05)';
    g.fillRect((i * 7919) % W, (i * 104729) % H, 2, 2);
  }
  g.fillStyle = look.trim;
  // side panels (u = 0.25 / 0.75), collar + armhole band at the top, hem
  for (const u of [0.25, 0.75]) g.fillRect(u * W - 16, H * 0.12, 32, H * 0.88);
  g.fillRect(0, 0, W, 22);
  g.fillRect(0, H - 14, W, 14);
  // V neck (front = u 0.5)
  g.beginPath();
  g.moveTo(W * 0.5 - 64, 0);
  g.lineTo(W * 0.5, 64);
  g.lineTo(W * 0.5 + 64, 0);
  g.closePath();
  g.fill();
  g.fillStyle = look.jersey;
  g.beginPath();
  g.moveTo(W * 0.5 - 44, 0);
  g.lineTo(W * 0.5, 42);
  g.lineTo(W * 0.5 + 44, 0);
  g.closePath();
  g.fill();
  g.font = '400 200px Anton, "Arial Black", sans-serif';
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  const num = (x: number, s: number) => {
    g.save();
    g.translate(x, H * 0.46);
    g.scale(0.55 * s, 1 * s);
    g.lineWidth = 14;
    g.strokeStyle = look.trim;
    g.strokeText(look.number, 0, 0);
    g.fillStyle = look.numColor;
    g.fillText(look.number, 0, 0);
    g.restore();
  };
  num(W * 0.5, 1);
  num(0, 0.9);
  num(W, 0.9);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  texCache.set(look.id, t);
  return t;
};

const shortsTex = (look: Look) => {
  const key = look.id + '|shorts';
  const hit = texCache.get(key);
  if (hit) return hit;
  const c = document.createElement('canvas');
  c.width = 512;
  c.height = 256;
  const g = c.getContext('2d')!;
  g.fillStyle = look.shorts;
  g.fillRect(0, 0, 512, 256);
  g.fillStyle = look.trim;
  for (const u of [0.25, 0.75]) g.fillRect(u * 512 - 9, 0, 18, 256);
  g.fillRect(0, 0, 512, 22);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  texCache.set(key, t);
  return t;
};

// ---------- small render helpers ----------
const Mat: React.FC<{m: THREE.Matrix4; children: React.ReactNode}> = ({m, children}) => {
  const p = new THREE.Vector3();
  const q = new THREE.Quaternion();
  const s = new THREE.Vector3();
  m.decompose(p, q, s);
  return (
    <group position={p} quaternion={q}>
      {children}
    </group>
  );
};

/** a capsule hanging down from a joint (along -Y) */
const Seg: React.FC<{geo: THREE.BufferGeometry; len: number; mat: THREE.Material; sx?: number; sz?: number}> = ({geo, len, mat, sx = 1, sz = 1}) => (
  <mesh geometry={geo} material={mat} position={[0, -len / 2, 0]} scale={[sx, 1, sz]} castShadow receiveShadow />
);

// ---------- the face ----------
/** head = ellipsoid (a, b, c) = R * HEAD_SCALE; features are projected onto its front surface */
export const HEAD_SCALE: [number, number, number] = [1, 1.06, 0.96];
export const headZ = (x: number, y: number, R = D.headR) => {
  const [a, b, c] = HEAD_SCALE;
  return c * R * Math.sqrt(Math.max(0.0004, 1 - (x / (a * R)) ** 2 - (y / (b * R)) ** 2));
};
const projectOnHead = (g: THREE.BufferGeometry, R: number, lift: number, cy: number, rot = 0, cx = 0) => {
  const pos = g.attributes.position as THREE.BufferAttribute;
  const cr = Math.cos(rot);
  const sr = Math.sin(rot);
  for (let i = 0; i < pos.count; i++) {
    const x0 = pos.getX(i);
    const y0 = pos.getY(i);
    const x = x0 * cr - y0 * sr + cx;
    const y = x0 * sr + y0 * cr + cy;
    pos.setXYZ(i, x, y, headZ(x, y, R) + lift);
  }
  pos.needsUpdate = true;
  g.computeVertexNormals();
  return g;
};

/** mouth outline: upper and lower lip curves; corners lifted by `smile`, `open` separates lips */
const mouthGeo = (w: number, open: number, smile: number, smirk: number, R: number, cy: number, inner: number, lift = 0.001) => {
  const n = 22;
  const up: THREE.Vector2[] = [];
  const lo: THREE.Vector2[] = [];
  for (let i = 0; i <= n; i++) {
    const u = (i / n) * 2 - 1; // -1..1
    const x = u * w;
    const corner = u * u;
    const sm = smile * 0.42 * w * corner + smirk * 0.25 * w * u * corner;
    const gap = open * (1 - corner);
    const yUp = sm + gap * 0.28 * inner + 0.0035 * (1 - corner);
    const yLo = sm - gap * inner - 0.0035 * (1 - corner);
    up.push(new THREE.Vector2(x, yUp));
    lo.push(new THREE.Vector2(x, yLo));
  }
  const shape = new THREE.Shape([...up, ...lo.reverse()]);
  return projectOnHead(new THREE.ShapeGeometry(shape, 1), R, lift, cy);
};

const browGeo = (len: number, thick: number, side: 1 | -1) => {
  // a tapered, slightly arched bar (inner end thicker) - built flat, bent onto the head later
  const s = new THREE.Shape();
  const n = 12;
  const top: THREE.Vector2[] = [];
  const bot: THREE.Vector2[] = [];
  for (let i = 0; i <= n; i++) {
    const u = i / n; // 0 inner .. 1 outer
    const x = u * len;
    const arch = Math.sin(u * Math.PI) * thick * 0.5;
    const t = thick * (1.15 - 0.55 * u);
    top.push(new THREE.Vector2(x, arch + t / 2));
    bot.push(new THREE.Vector2(x, arch - t / 2));
  }
  s.setFromPoints([...top, ...bot.reverse()].map((v) => new THREE.Vector2(v.x * side, v.y)));
  const g = new THREE.ShapeGeometry(s, 1);
  // subdivide-free bend is fine: 12 segments along the bar
  return g;
};

const Eye: React.FC<{side: 1 | -1; face: Face; look: Look; R: number}> = ({side, face, look, R}) => {
  const er = 0.25 * R;
  const ex = side * 0.37 * R;
  const ey = 0.08 * R;
  const ez = headZ(ex, ey, R) - 0.5 * er;
  // gaze: rotate the eyeball (iris on its front)
  const gx = face.gazeX * 0.45;
  const gy = face.gazeY * 0.35;
  const lidA = -0.82 + face.lid * 2.45; // upper lid rotation
  const loA = -0.95 + face.squint * 0.6;
  const skin = std(look.skin, 0.55);
  return (
    <group position={[ex, ey, ez]}>
      <mesh geometry={G.sphere} material={std('#F7F4EE', 0.25)} scale={[er, er * 1.08, er * 0.92]} />
      <group rotation={[-gy, gx, 0]}>
        <mesh geometry={G.lowSphere} material={std(look.iris, 0.3)} position={[0, 0, er * 0.74]} scale={[er * 0.56, er * 0.6, er * 0.32]} />
        <mesh geometry={G.lowSphere} material={std('#0B0705', 0.2)} position={[0, 0, er * 0.86]} scale={[er * 0.3, er * 0.32, er * 0.18]} />
        <mesh geometry={G.lowSphere} material={std('#ffffff', 0.1, {emissive: '#ffffff', emissiveIntensity: 0.9})} position={[er * 0.16, er * 0.2, er * 0.97]} scale={er * 0.1} />
      </group>
      {/* upper lid (skin shell) + lash line */}
      <group rotation={[lidA, 0, side * -0.08]}>
        <mesh geometry={G.capTop} material={skin} scale={er * 1.12} />
        <mesh rotation={[Math.PI / 2, 0, 0]} scale={[er * 1.13, er * 1.13, 0.006]} material={std('#1A0F0A', 0.6)}>
          <torusGeometry args={[1, 0.055, 6, 32, Math.PI]} />
        </mesh>
      </group>
      {/* lower lid */}
      <group rotation={[Math.PI - loA, 0, 0]}>
        <mesh geometry={G.capTop} material={skin} scale={er * 1.1} />
      </group>
    </group>
  );
};

const Head: React.FC<{look: Look; face: Face; mouth: number}> = ({look, face, mouth}) => {
  const R = D.headR;
  const skin = std(look.skin, 0.55);
  const hairM = std(look.hair, 0.85);
  const open = Math.min(1, mouth + face.open);
  const mouthCy = -0.44 * R;
  const mouthW = 0.24 * R * face.wide * (1 - open * 0.2);
  const gap = open * 0.34 * R;
  const mg = React.useMemo(() => mouthGeo(mouthW, gap, face.smile, face.smirk, R, mouthCy, 1), [mouthW, gap, face.smile, face.smirk, R, mouthCy]);
  const lipG = React.useMemo(() => mouthGeo(mouthW * 1.1, gap + 0.008, face.smile, face.smirk, R, mouthCy, 1.12, -0.0015), [mouthW, gap, face.smile, face.smirk, R, mouthCy]);
  const teethG = React.useMemo(() => {
    if (open < 0.12) return null;
    return mouthGeo(mouthW * 0.78, gap * 0.22, face.smile * 0.85, face.smirk, R, mouthCy + gap * 0.2, 1, 0.0022);
  }, [mouthW, gap, open, face.smile, face.smirk, R, mouthCy]);
  const brow = (side: 1 | -1, h: number) => {
    // inner end near the nose bridge, outer end toward the temple; tilt + = inner end up (worry)
    const rot = side * (-face.browTilt * 0.38) + side * 0.12;
    const g = browGeo(0.44 * R, 0.1 * R * look.brow, side);
    projectOnHead(g, R, 0.0035, 0.41 * R + h * 0.13 * R, rot, side * 0.13 * R);
    return <mesh geometry={g} material={std(look.browColor, 0.8, {side: THREE.DoubleSide})} />;
  };
  return (
    <group position={[0, D.headY, 0.012]}>
      {/* skull + jaw/cheeks */}
      <mesh geometry={G.sphere} material={skin} scale={[R * HEAD_SCALE[0], R * HEAD_SCALE[1], R * HEAD_SCALE[2]]} castShadow />
      {/* jaw/chin volume sits behind the face surface so the mouth stays visible */}
      {/* nose */}
      <mesh geometry={G.lowSphere} material={skin} position={[0, -0.12 * R, headZ(0, -0.12 * R) - 0.02 * R]} scale={[0.15 * R, 0.13 * R, 0.16 * R]} castShadow />
      {/* ears */}
      {[1, -1].map((s) => (
        <mesh key={s} geometry={G.lowSphere} material={skin} position={[s * R * 0.98, -0.05 * R, -0.03 * R]} scale={[0.09 * R, 0.21 * R, 0.15 * R]} />
      ))}
      {/* hair */}
      {look.hairStyle === 'fade' ? (
        <group rotation={[-0.74, 0, 0]}>
          <mesh geometry={G.capTop} material={hairM} scale={[R * 1.025, R * 1.07, R * 1.0]} />
        </group>
      ) : (
        <group rotation={[-0.6, 0, 0]}>
          <mesh geometry={G.capTop} material={hairM} scale={[R * 1.05, R * 1.16, R * 1.03]} />
          {Array.from({length: 26}, (_, i) => {
            const a = (i / 26) * Math.PI * 2 * 2.618;
            const r = 0.35 + ((i * 37) % 10) / 16;
            const x = Math.cos(a) * r * R * 0.8;
            const z = Math.sin(a) * r * R * 0.8;
            const y = Math.sqrt(Math.max(0, (R * 1.12) ** 2 - x * x - z * z)) * 1.02;
            return <mesh key={i} geometry={G.lowSphere} material={hairM} position={[x, y, z]} scale={0.04 + ((i * 13) % 5) * 0.004} />;
          })}
        </group>
      )}
      {look.headband ? (
        <group position={[0, 0.45 * R, -0.1 * R]} rotation={[-0.35, 0, 0]}>
          <mesh rotation={[Math.PI / 2, 0, 0]} material={std(look.headband.base, 0.7)} scale={[1, 1, 1.9]}>
            <torusGeometry args={[R * 0.88, 0.017, 10, 48]} />
          </mesh>
          <mesh rotation={[Math.PI / 2, 0, 0]} material={std(look.headband.stripe, 0.35, {metalness: 0.4})}>
            <torusGeometry args={[R * 0.895, 0.0055, 8, 48]} />
          </mesh>
        </group>
      ) : null}
      {/* eyes, brows, mouth */}
      <Eye side={1} face={face} look={look} R={R} />
      <Eye side={-1} face={face} look={look} R={R} />
      {brow(1, face.browL)}
      {brow(-1, face.browR)}
      <mesh geometry={lipG} material={std(shade(look.skin, -0.28), 0.5)} />
      <mesh geometry={mg} material={std('#3A0E0C', 0.7)} position={[0, 0, 0.0012]} />
      {teethG ? <mesh geometry={teethG} material={std('#F4F1EA', 0.35)} position={[0, 0, 0.0022]} /> : null}
    </group>
  );
};

export const shade = (hex: string, k: number) => {
  const c = new THREE.Color(hex);
  const hsl = {h: 0, s: 0, l: 0};
  c.getHSL(hsl);
  c.setHSL(hsl.h, hsl.s, Math.max(0, Math.min(1, hsl.l * (1 + k))));
  return '#' + c.getHexString();
};

const Hand: React.FC<{look: Look; point: number; side: 1 | -1}> = ({look, point, side}) => {
  const skin = std(look.skin, 0.55);
  return (
    <group position={[0, -0.045, 0]}>
      <mesh geometry={G.sphere} material={skin} scale={[0.056, 0.066, 0.038]} castShadow />
      {/* thumb */}
      <mesh geometry={G.lowSphere} material={skin} position={[side * 0.03, 0.005, 0.03]} scale={[0.017, 0.032, 0.017]} rotation={[0.4, 0, side * 0.5]} />
      {/* index finger when pointing */}
      {point > 0.02 ? <mesh geometry={G.finger} material={skin} position={[side * 0.012, -0.05 - 0.035 * point, 0.012]} scale={[1, point, 1]} /> : null}
    </group>
  );
};

export const Toon: React.FC<{look: Look; pose: Pose; mouth?: number; skel?: Skel}> = ({look, pose, mouth = 0, skel}) => {
  const s = skel ?? fk(pose, look.build);
  const skin = std(look.skin, 0.55);
  const jersey = React.useMemo(() => new THREE.MeshStandardMaterial({map: jerseyTex(look), roughness: 0.78}), [look]);
  const shortsM = React.useMemo(() => new THREE.MeshStandardMaterial({map: shortsTex(look), roughness: 0.7}), [look]);
  const shortsPlain = std(look.shorts, 0.7);
  const sock = std(look.sock, 0.8);
  const shoe = std(look.shoe, 0.45);
  const accent = std(look.shoeAccent, 0.4);
  const leg = (h: Bone, k: Bone, a: Bone, side: 1 | -1) => (
    <>
      <Mat m={s[h]}>
        <Seg geo={G.thigh} len={D.thigh} mat={skin} />
        <mesh geometry={G.shortLeg} material={shortsPlain} position={[0, -0.3, 0]} scale={[1, 0.34, 1]} castShadow />
      </Mat>
      <Mat m={s[k]}>
        <Seg geo={G.shin} len={D.shin} mat={skin} />
        <mesh geometry={G.cyl} material={sock} position={[0, -D.shin + 0.1, 0]} scale={[0.05, 0.14, 0.05]} />
      </Mat>
      <Mat m={s[a]}>
        <group position={[0, -D.foot + 0.045, 0.06]} rotation={[Math.PI / 2, 0, 0]}>
          <mesh geometry={G.shoe} material={shoe} scale={[0.07, 0.085, 0.058]} castShadow />
          <mesh geometry={G.shoe} material={accent} position={[0, 0, 0.038]} scale={[0.072, 0.087, 0.022]} />
          <mesh geometry={G.lowSphere} material={accent} position={[side * 0.05, -0.02, 0.0]} scale={[0.012, 0.05, 0.02]} />
        </group>
      </Mat>
    </>
  );
  const arm = (up: Bone, el: Bone, hand: Bone, side: 1 | -1, point: number) => (
    <>
      <Mat m={s[up]}>
        <Seg geo={G.upper} len={D.upper} mat={skin} />
        <mesh geometry={G.sphere} material={skin} position={[0, -0.01, 0]} scale={0.062} castShadow />
      </Mat>
      <Mat m={s[el]}>
        <Seg geo={G.fore} len={D.fore} mat={skin} />
        {look.wristband ? <mesh geometry={G.cylClosed} material={std(look.wristband, 0.5)} position={[0, -D.fore + 0.05, 0]} scale={[0.045, 0.05, 0.045]} /> : null}
      </Mat>
      <Mat m={s[hand]}>
        <Hand look={look} point={point} side={side} />
      </Mat>
    </>
  );
  return (
    <group>
      <Mat m={s.root}>
        {/* shorts */}
        <mesh geometry={G.shorts} material={shortsM} position={[0, -0.13, 0]} scale={[1, 0.2, 0.78]} castShadow />
      </Mat>
      <Mat m={s.spine}>
        <mesh geometry={G.torso} material={jersey} scale={[look.build, D.torso, 0.74]} castShadow receiveShadow />
        {/* shoulders (deltoids) */}
        {[1, -1].map((sd) => (
          <mesh key={sd} geometry={G.sphere} material={skin} position={[sd * D.shW * look.build, D.shY + 0.005, -0.01]} scale={[0.07, 0.065, 0.068]} castShadow />
        ))}
        <mesh geometry={G.neck} material={skin} position={[0, D.torso + 0.01, 0]} />
      </Mat>
      <Mat m={s.head}>
        <Head look={look} face={pose.face} mouth={mouth} />
      </Mat>
      {arm('lUp', 'lEl', 'lHand', 1, pose.lPoint)}
      {arm('rUp', 'rEl', 'rHand', -1, pose.rPoint)}
      {leg('lHip', 'lKnee', 'lAnkle', 1)}
      {leg('rHip', 'rKnee', 'rAnkle', -1)}
    </group>
  );
};
