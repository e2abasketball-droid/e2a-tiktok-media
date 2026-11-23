// E2A Football — 3D environment: mown grass with fine detail, IFAB lines (105 x 68), goals with posts,
// crossbar and a deformable net, perimeter boards, dark stands and floodlight lighting with soft shadows.
import React from 'react';
import * as THREE from 'three';
import {GOLD, NAVY} from './brand';
import {W3} from './athlete';

export const PITCH = {L: 105, W: 68, goalW: 7.32, goalH: 2.44, netDepth: 2.0, paL: 16.5, paW: 40.32, gaL: 5.5, gaW: 18.32, spot: 11, circle: 9.15};
const HL = PITCH.L / 2;
const HW = PITCH.W / 2;
const LINE = 0.12;
const Y0 = 0.004;

const rnd = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

let grassTex: THREE.Texture | null = null;
const grassDetail = () => {
  if (grassTex) return grassTex;
  const S = 512;
  const c = document.createElement('canvas');
  c.width = S;
  c.height = S;
  const g = c.getContext('2d')!;
  g.fillStyle = 'rgb(128,128,128)';
  g.fillRect(0, 0, S, S);
  // blades: short strokes with random tone, tileable (wrap around edges)
  for (let i = 0; i < 26000; i++) {
    const x = rnd(i) * S;
    const y = rnd(i + 7.3) * S;
    const l = 2 + rnd(i + 1.7) * 6;
    const a = -Math.PI / 2 + (rnd(i + 3.1) - 0.5) * 0.9;
    const v = 95 + rnd(i + 5.9) * 75;
    g.strokeStyle = `rgba(${v},${v},${v},0.55)`;
    g.lineWidth = 1;
    for (const dx of [0, -S, S])
      for (const dy of [0, -S, S]) {
        g.beginPath();
        g.moveTo(x + dx, y + dy);
        g.lineTo(x + dx + Math.cos(a) * l, y + dy + Math.sin(a) * l);
        g.stroke();
      }
  }
  // soft patches (wear) so repetition does not show
  for (let i = 0; i < 60; i++) {
    const x = rnd(i + 99) * S;
    const y = rnd(i + 199) * S;
    const r = 20 + rnd(i + 299) * 60;
    const grd = g.createRadialGradient(x, y, 0, x, y, r);
    const v = rnd(i + 399) > 0.5 ? 150 : 105;
    grd.addColorStop(0, `rgba(${v},${v},${v},0.18)`);
    grd.addColorStop(1, 'rgba(128,128,128,0)');
    g.fillStyle = grd;
    g.fillRect(x - r, y - r, 2 * r, 2 * r);
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  t.colorSpace = THREE.SRGBColorSpace;
  grassTex = t;
  return t;
};

/** flat line segment on the grass from (x0, y0) to (x1, y1) */
const Seg: React.FC<{a: [number, number]; b: [number, number]; m: THREE.Material}> = ({a, b, m}) => {
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const L = Math.hypot(dx, dy);
  const c = W3([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, Y0]);
  return (
    <mesh position={c} rotation={[-Math.PI / 2, 0, Math.atan2(dy, dx)]} material={m} receiveShadow>
      <planeGeometry args={[L + LINE, LINE]} />
    </mesh>
  );
};
const Arc: React.FC<{c: [number, number]; r: number; a0: number; a1: number; m: THREE.Material}> = ({c, r, a0, a1, m}) => (
  // ringGeometry lies in the XY plane; after the -90deg X rotation its angles are world pitch angles.
  <mesh position={W3([c[0], c[1], Y0])} rotation={[-Math.PI / 2, 0, 0]} material={m} receiveShadow>
    <ringGeometry args={[r - LINE / 2, r + LINE / 2, 96, 1, a0, a1 - a0]} />
  </mesh>
);

const Lines: React.FC = () => {
  const m = React.useMemo(() => new THREE.MeshStandardMaterial({color: '#F2F4F2', roughness: 0.9, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2}), []);
  const segs: [[number, number], [number, number]][] = [
    [[-HL, -HW], [HL, -HW]],
    [[-HL, HW], [HL, HW]],
    [[-HL, -HW], [-HL, HW]],
    [[HL, -HW], [HL, HW]],
    [[0, -HW], [0, HW]],
  ];
  for (const s of [-1, 1]) {
    const gx = s * HL;
    const px = s * (HL - PITCH.paL);
    const ax = s * (HL - PITCH.gaL);
    segs.push([[gx, -PITCH.paW / 2], [px, -PITCH.paW / 2]], [[gx, PITCH.paW / 2], [px, PITCH.paW / 2]], [[px, -PITCH.paW / 2], [px, PITCH.paW / 2]]);
    segs.push([[gx, -PITCH.gaW / 2], [ax, -PITCH.gaW / 2]], [[gx, PITCH.gaW / 2], [ax, PITCH.gaW / 2]], [[ax, -PITCH.gaW / 2], [ax, PITCH.gaW / 2]]);
  }
  // penalty arc: the part of the 9.15 m circle around the spot outside the area
  const arcA = Math.acos((PITCH.paL - PITCH.spot) / PITCH.circle);
  return (
    <group>
      {segs.map(([a, b], i) => (
        <Seg key={i} a={a} b={b} m={m} />
      ))}
      <Arc c={[0, 0]} r={PITCH.circle} a0={0} a1={Math.PI * 2} m={m} />
      {[-1, 1].map((s) => (
        <React.Fragment key={s}>
          <mesh position={W3([s * (HL - PITCH.spot), 0, Y0])} rotation={[-Math.PI / 2, 0, 0]} material={m}>
            <circleGeometry args={[0.12, 20]} />
          </mesh>
          {s > 0 ? <Arc c={[HL - PITCH.spot, 0]} r={PITCH.circle} a0={Math.PI - arcA} a1={Math.PI + arcA} m={m} /> : <Arc c={[-HL + PITCH.spot, 0]} r={PITCH.circle} a0={-arcA} a1={arcA} m={m} />}
          {[-1, 1].map((q) => (
            <Arc key={q} c={[s * HL, q * HW]} r={1} a0={s > 0 ? (q > 0 ? Math.PI : Math.PI / 2) : q > 0 ? -Math.PI / 2 : 0} a1={s > 0 ? (q > 0 ? 1.5 * Math.PI : Math.PI) : q > 0 ? 0 : Math.PI / 2} m={m} />
          ))}
        </React.Fragment>
      ))}
      <mesh position={W3([0, 0, Y0])} rotation={[-Math.PI / 2, 0, 0]} material={m}>
        <circleGeometry args={[0.15, 20]} />
      </mesh>
    </group>
  );
};

const Grass: React.FC = () => {
  const det = grassDetail();
  const stripes = 18;
  const w = PITCH.L / stripes;
  const mk = (color: string, rx: number, ry: number) => {
    const t = det.clone();
    t.needsUpdate = true;
    t.repeat.set(rx, ry);
    return new THREE.MeshStandardMaterial({color, map: t, roughness: 0.96, metalness: 0});
  };
  const mA = React.useMemo(() => mk('#3F8A3A', w / 1.6, PITCH.W / 1.6), []);
  const mB = React.useMemo(() => mk('#4A9A43', w / 1.6, PITCH.W / 1.6), []);
  const mOut = React.useMemo(() => mk('#356F31', 60, 40), []);
  return (
    <group>
      {Array.from({length: stripes}, (_, i) => (
        <mesh key={i} position={W3([-HL + w * (i + 0.5), 0, 0])} rotation={[-Math.PI / 2, 0, 0]} material={i % 2 ? mA : mB} receiveShadow>
          <planeGeometry args={[w, PITCH.W]} />
        </mesh>
      ))}
      {/* run-off around the field of play */}
      <mesh position={[0, -0.06, 0]} rotation={[-Math.PI / 2, 0, 0]} material={mOut} receiveShadow>
        <planeGeometry args={[PITCH.L + 16, PITCH.W + 14]} />
      </mesh>
    </group>
  );
};

// ---------- goal with a deformable net ----------
export type NetHit = {age: number; at: [number, number, number]} | null;

let netTex: THREE.Texture | null = null;
const netTexture = () => {
  if (netTex) return netTex;
  const c = document.createElement('canvas');
  c.width = 128;
  c.height = 128;
  const g = c.getContext('2d')!;
  g.clearRect(0, 0, 128, 128);
  g.strokeStyle = 'rgba(255,255,255,0.95)';
  g.lineWidth = 7;
  // diamond mesh
  g.beginPath();
  g.moveTo(0, 64);
  g.lineTo(64, 0);
  g.lineTo(128, 64);
  g.lineTo(64, 128);
  g.closePath();
  g.stroke();
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  netTex = t;
  return t;
};

/** a net panel through 4 corners (pitch coords), bulged by a ball impact */
const NetPanel: React.FC<{c: [number, number, number][]; rep: [number, number]; hit: NetHit; normal: [number, number, number]}> = ({c, rep, hit, normal}) => {
  const geo = React.useMemo(() => {
    const sx = 24;
    const sy = 12;
    const g = new THREE.BufferGeometry();
    const pos: number[] = [];
    const uv: number[] = [];
    const idx: number[] = [];
    for (let j = 0; j <= sy; j++)
      for (let i = 0; i <= sx; i++) {
        const u = i / sx;
        const v = j / sy;
        const p = [0, 1, 2].map((k) => (1 - u) * (1 - v) * c[0][k] + u * (1 - v) * c[1][k] + u * v * c[2][k] + (1 - u) * v * c[3][k]) as [number, number, number];
        pos.push(...W3(p));
        uv.push(u * rep[0], v * rep[1]);
      }
    for (let j = 0; j < sy; j++)
      for (let i = 0; i < sx; i++) {
        const a = j * (sx + 1) + i;
        idx.push(a, a + 1, a + sx + 2, a, a + sx + 2, a + sx + 1);
      }
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    g.setIndex(idx);
    g.userData.base = pos.slice();
    return g;
  }, [c, rep]);
  // deform per frame (net slack sag + impact bulge that rings down)
  const base = geo.userData.base as number[];
  const P = geo.getAttribute('position') as THREE.BufferAttribute;
  const n3 = W3(normal);
  for (let k = 0; k < P.count; k++) {
    let x = base[3 * k];
    let y = base[3 * k + 1];
    let z = base[3 * k + 2];
    if (hit) {
      const h3 = W3(hit.at);
      const d2 = (x - h3[0]) ** 2 + (y - h3[1]) ** 2 + (z - h3[2]) ** 2;
      const amp = 0.55 * Math.exp(-hit.age * 3.2) * Math.cos(hit.age * 9) * Math.exp(-d2 / 0.9);
      const grow = Math.min(1, hit.age / 0.06);
      x += n3[0] * amp * grow;
      y += n3[1] * amp * grow;
      z += n3[2] * amp * grow;
    }
    P.setXYZ(k, x, y, z);
  }
  P.needsUpdate = true;
  geo.computeVertexNormals();
  const m = React.useMemo(() => {
    const t = netTexture().clone();
    t.needsUpdate = true;
    return new THREE.MeshStandardMaterial({map: t, transparent: true, alphaTest: 0.35, side: THREE.DoubleSide, roughness: 0.9, color: '#FFFFFF'});
  }, []);
  return <mesh geometry={geo} material={m} castShadow />;
};

const Goal: React.FC<{side: 1 | -1; hit: NetHit}> = ({side, hit}) => {
  const gx = side * HL;
  const hw = PITCH.goalW / 2;
  const H = PITCH.goalH;
  const D = PITCH.netDepth;
  const bx = gx + side * D; // back of the net at ground
  const tx = gx + side * 1.0; // top of the net goes back 1 m then drops
  const post = React.useMemo(() => new THREE.MeshStandardMaterial({color: '#FAFAFA', roughness: 0.35, metalness: 0.1}), []);
  const frame = React.useMemo(() => new THREE.MeshStandardMaterial({color: '#B9BEC5', roughness: 0.6}), []);
  const cyl = (a: [number, number, number], b: [number, number, number], r: number, m: THREE.Material, key: string) => {
    const A = new THREE.Vector3(...W3(a));
    const B = new THREE.Vector3(...W3(b));
    const mid = A.clone().add(B).multiplyScalar(0.5);
    const dir = B.clone().sub(A);
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
    return (
      <mesh key={key} position={mid} quaternion={q} material={m} castShadow>
        <cylinderGeometry args={[r, r, dir.length(), 16]} />
      </mesh>
    );
  };
  const c = React.useMemo(
    () => ({
      back: [[tx, -hw, H * 0.92], [tx, hw, H * 0.92], [bx, hw, 0], [bx, -hw, 0]] as [number, number, number][],
      top: [[gx, -hw, H], [gx, hw, H], [tx, hw, H * 0.92], [tx, -hw, H * 0.92]] as [number, number, number][],
      left: [[gx, -hw, H], [tx, -hw, H * 0.92], [bx, -hw, 0], [gx, -hw, 0]] as [number, number, number][],
      right: [[gx, hw, H], [tx, hw, H * 0.92], [bx, hw, 0], [gx, hw, 0]] as [number, number, number][],
    }),
    [gx, hw, H, tx, bx],
  );
  return (
    <group>
      {cyl([gx, -hw, 0], [gx, -hw, H], 0.06, post, 'p1')}
      {cyl([gx, hw, 0], [gx, hw, H], 0.06, post, 'p2')}
      {cyl([gx, -hw - 0.06, H], [gx, hw + 0.06, H], 0.06, post, 'bar')}
      {cyl([tx, -hw, H * 0.92], [tx, hw, H * 0.92], 0.025, frame, 'f1')}
      {cyl([bx, -hw, 0.02], [bx, hw, 0.02], 0.025, frame, 'f2')}
      {cyl([gx, -hw, H], [tx, -hw, H * 0.92], 0.02, frame, 'f3')}
      {cyl([gx, hw, H], [tx, hw, H * 0.92], 0.02, frame, 'f4')}
      {cyl([tx, -hw, H * 0.92], [bx, -hw, 0.02], 0.02, frame, 'f5')}
      {cyl([tx, hw, H * 0.92], [bx, hw, 0.02], 0.02, frame, 'f6')}
      <NetPanel c={c.back} rep={[PITCH.goalW / 0.14, 2.6 / 0.14]} hit={hit} normal={[side, 0, 0.35]} />
      <NetPanel c={c.top} rep={[PITCH.goalW / 0.14, 1.0 / 0.14]} hit={null} normal={[0, 0, 1]} />
      <NetPanel c={c.left} rep={[2.0 / 0.14, H / 0.14]} hit={null} normal={[0, -1, 0]} />
      <NetPanel c={c.right} rep={[2.0 / 0.14, H / 0.14]} hit={null} normal={[0, 1, 0]} />
    </group>
  );
};

let boardTex: THREE.Texture | null = null;
const boardTexture = () => {
  if (boardTex) return boardTex;
  const c = document.createElement('canvas');
  c.width = 1024;
  c.height = 64;
  const g = c.getContext('2d')!;
  g.fillStyle = NAVY;
  g.fillRect(0, 0, 1024, 64);
  g.fillStyle = GOLD;
  g.fillRect(0, 54, 1024, 5);
  g.font = '40px Anton, Impact, sans-serif';
  g.textBaseline = 'middle';
  g.fillStyle = 'rgba(255,255,255,0.92)';
  for (let x = 40; x < 1024; x += 512) g.fillText('E2A SPORTS  ·  FOOTBALL', x, 30);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = THREE.RepeatWrapping;
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  boardTex = t;
  return t;
};

const Surroundings: React.FC = () => {
  const stands = React.useMemo(() => new THREE.MeshStandardMaterial({color: '#141C2C', roughness: 0.95}), []);
  const seats = React.useMemo(() => new THREE.MeshStandardMaterial({color: '#1E2B45', roughness: 0.9}), []);
  const boardL = React.useMemo(() => {
    const t = boardTexture().clone();
    t.needsUpdate = true;
    t.repeat.set(PITCH.L / 12, 1);
    return new THREE.MeshStandardMaterial({map: t, roughness: 0.55, emissive: new THREE.Color('#0B1C3D'), emissiveIntensity: 0.35, emissiveMap: t});
  }, []);
  const boardW = React.useMemo(() => {
    const t = boardTexture().clone();
    t.needsUpdate = true;
    t.repeat.set(PITCH.W / 12, 1);
    return new THREE.MeshStandardMaterial({map: t, roughness: 0.55, emissive: new THREE.Color('#0B1C3D'), emissiveIntensity: 0.35, emissiveMap: t});
  }, []);
  const off = 5;
  return (
    <group>
      {/* perimeter boards */}
      {[-1, 1].map((s) => (
        <mesh key={`l${s}`} position={W3([0, s * (HW + off), 0.5])} rotation={[0, s > 0 ? 0 : Math.PI, 0]} material={boardL} castShadow>
          <planeGeometry args={[PITCH.L + 6, 1]} />
        </mesh>
      ))}
      {[-1, 1].map((s) => (
        <mesh key={`w${s}`} position={W3([s * (HL + off + 1), 0, 0.5])} rotation={[0, s > 0 ? Math.PI / 2 : -Math.PI / 2, 0]} material={boardW} castShadow>
          <planeGeometry args={[PITCH.W + 6, 1]} />
        </mesh>
      ))}
      {/* tiered stands (simple masses: the action stays on the pitch) */}
      {[0, 1, 2].map((k) => (
        <React.Fragment key={k}>
          {[-1, 1].map((s) => (
            <mesh key={`sl${s}${k}`} position={W3([0, s * (HW + 9 + k * 4), 1.5 + k * 2.6])} material={k % 2 ? seats : stands}>
              <boxGeometry args={[PITCH.L + 30, 3 + k * 2.6, 4]} />
            </mesh>
          ))}
          {[-1, 1].map((s) => (
            <mesh key={`sw${s}${k}`} position={W3([s * (HL + 10 + k * 4), 0, 1.5 + k * 2.6])} material={k % 2 ? seats : stands}>
              <boxGeometry args={[4, 3 + k * 2.6, PITCH.W + 30]} />
            </mesh>
          ))}
        </React.Fragment>
      ))}
    </group>
  );
};

export const Lights: React.FC<{focus: [number, number]}> = ({focus}) => {
  const ref = React.useRef<THREE.DirectionalLight>(null);
  const tgt = React.useMemo(() => new THREE.Object3D(), []);
  const f = W3([focus[0], focus[1], 0]);
  tgt.position.set(f[0], f[1], f[2]);
  tgt.updateMatrixWorld();
  const key = W3([focus[0] - 22, focus[1] + 28, 46]);
  return (
    <>
      <hemisphereLight args={['#C9D6F0', '#2B4A24', 0.9]} />
      <ambientLight intensity={0.18} />
      <primitive object={tgt} />
      <directionalLight
        ref={ref}
        position={key}
        target={tgt}
        intensity={2.4}
        color="#FFF6E8"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-left={-34}
        shadow-camera-right={34}
        shadow-camera-top={34}
        shadow-camera-bottom={-34}
        shadow-camera-near={10}
        shadow-camera-far={140}
        shadow-bias={-0.0004}
        shadow-normalBias={0.02}
        shadow-radius={3}
      />
      {/* opposite floodlight bank: soft fill, second faint shadow direction is skipped for speed */}
      <directionalLight position={W3([focus[0] + 30, focus[1] - 30, 40])} intensity={0.55} color="#DCE6FF" />
    </>
  );
};

/** corner flagposts (Law 1: at least 1.5 m high, non-pointed top), set on the corner point */
const CornerFlags: React.FC = () => {
  const pole = React.useMemo(() => new THREE.MeshStandardMaterial({color: '#F1F2F4', roughness: 0.4}), []);
  const flag = React.useMemo(() => {
    const g = new THREE.PlaneGeometry(0.42, 0.3, 8, 4);
    const pos = g.getAttribute('position') as THREE.BufferAttribute;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i) + 0.21; // 0 at the pole
      pos.setZ(i, Math.sin(x * 7) * 0.035 * x * 2.4);
    }
    g.computeVertexNormals();
    return g;
  }, []);
  const cloth = React.useMemo(() => new THREE.MeshStandardMaterial({color: '#C9A24D', roughness: 0.7, side: THREE.DoubleSide}), []);
  const HL = PITCH.L / 2;
  const HW = PITCH.W / 2;
  return (
    <>
      {[1, -1].flatMap((sx) =>
        [1, -1].map((sy) => (
          <group key={`${sx}${sy}`} position={W3([sx * HL, sy * HW, 0])}>
            <mesh position={[0, 0.8, 0]} material={pole} castShadow>
              <cylinderGeometry args={[0.018, 0.022, 1.6, 10]} />
            </mesh>
            <group position={[0, 1.43, 0]} rotation={[0, sx > 0 ? Math.PI * 0.75 : Math.PI * 0.25, 0]}>
              <mesh position={[0.21, 0, 0]} geometry={flag} material={cloth} castShadow />
            </group>
          </group>
        )),
      )}
    </>
  );
};

export const Pitch3D: React.FC<{hit: NetHit}> = ({hit}) => (
  <group>
    <Grass />
    <Lines />
    <CornerFlags />
    <Goal side={1} hit={hit} />
    <Goal side={-1} hit={null} />
    <Surroundings />
  </group>
);
