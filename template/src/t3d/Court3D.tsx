// E2A 3D engine — BasketballCourt3D: maple parquet (procedural planks + grain, roughness variation),
// FIBA lines, navy paint, gold accents, E2A logo at the centre circle, a full basket unit (padded
// stanchion, glass board, rim, net) and a dark arena around it (apron, stands, light strips,
// overhead rigs) so the court reads as a physical space instead of a floating rectangle.
import React from 'react';
import * as THREE from 'three';
import {FIBA, threeJoinY} from '../tactical/geometry.ts';
import {W3} from './Athlete';
import {useThree} from '@react-three/fiber';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';

// texture covers x in [-8.5, 8.5], y in [-1.5, 15.5] (17 m x 17 m)
const X0 = -8.5;
const Y0 = -1.5;
const SPAN = 17;
const PX = 2560;
const toPx = (x: number, y: number): [number, number] => [((x - X0) / SPAN) * PX, PX - ((y - Y0) / SPAN) * PX];
const m2px = (m: number) => (m / SPAN) * PX;

let floorTex: {map: THREE.Texture; rough: THREE.Texture} | null = null;

const makeCanvas = (w: number, h: number) => {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  return c;
};

// deterministic noise
const rnd = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

export const buildFloor = (logo?: HTMLImageElement) => {
  if (floorTex) return floorTex;
  const c = makeCanvas(PX, PX);
  const g = c.getContext('2d')!;
  const r = makeCanvas(PX / 2, PX / 2);
  const gr = r.getContext('2d')!;
  // planks run along y (toward half court), 0.07 m wide, random lengths
  const plankW = m2px(0.075);
  let n = 0;
  gr.fillStyle = 'rgb(120,120,120)';
  gr.fillRect(0, 0, PX / 2, PX / 2);
  for (let x = 0; x < PX; x += plankW) {
    let y = -rnd(n++) * 400;
    while (y < PX) {
      const L = m2px(1.2 + rnd(n++) * 2.2);
      const tone = rnd(n++);
      const base = [168 + tone * 30, 112 + tone * 24, 64 + tone * 18];
      const grad = g.createLinearGradient(x, y, x + plankW, y + L);
      grad.addColorStop(0, `rgb(${base[0]},${base[1]},${base[2]})`);
      grad.addColorStop(1, `rgb(${base[0] - 10},${base[1] - 10},${base[2] - 8})`);
      g.fillStyle = grad;
      g.fillRect(x, y, plankW, L);
      // grain streaks
      for (let k = 0; k < 6; k++) {
        g.strokeStyle = `rgba(110,62,28,${0.05 + rnd(n++) * 0.08})`;
        g.lineWidth = 1 + rnd(n++) * 1.5;
        const gx = x + rnd(n++) * plankW;
        g.beginPath();
        g.moveTo(gx, y);
        g.bezierCurveTo(gx + 3, y + L * 0.3, gx - 3, y + L * 0.6, gx + 1, y + L);
        g.stroke();
      }
      // seams
      g.fillStyle = 'rgba(70,40,18,0.35)';
      g.fillRect(x, y, 1.5, L);
      g.fillRect(x, y, plankW, 1.5);
      // roughness: each plank slightly different sheen
      gr.fillStyle = `rgb(${95 + tone * 50},${95 + tone * 50},${95 + tone * 50})`;
      gr.fillRect(x / 2, y / 2, plankW / 2, L / 2);
      y += L;
    }
  }
  // paint (navy) — the key, slightly translucent so the wood shows
  const paint = (x0: number, y0: number, x1: number, y1: number, col: string) => {
    const [a, b] = toPx(x0, y1);
    const [c2, d] = toPx(x1, y0);
    g.fillStyle = col;
    g.fillRect(a, b, c2 - a, d - b);
  };
  // out of bounds apron (navy) around the court
  g.fillStyle = 'rgba(11,28,61,0.94)';
  const [lx] = toPx(-FIBA.halfW, 0);
  const [rx] = toPx(FIBA.halfW, 0);
  const [, by] = toPx(0, 0);
  g.fillRect(0, 0, lx, PX);
  g.fillRect(rx, 0, PX - rx, PX);
  g.fillRect(0, by, PX, PX - by);
  paint(-FIBA.keyHalfW, 0, FIBA.keyHalfW, FIBA.ftY, 'rgba(11,28,61,0.9)');
  // lines
  g.strokeStyle = 'rgba(250,248,240,0.96)';
  g.lineWidth = m2px(0.05);
  const line = (pts: [number, number][]) => {
    g.beginPath();
    pts.forEach(([x, y], i) => {
      const [px, py] = toPx(x, y);
      if (i) g.lineTo(px, py);
      else g.moveTo(px, py);
    });
    g.stroke();
  };
  // boundary
  line([[-FIBA.halfW, 0], [FIBA.halfW, 0], [FIBA.halfW, FIBA.halfL], [-FIBA.halfW, FIBA.halfL], [-FIBA.halfW, 0]]);
  // key
  line([[-FIBA.keyHalfW, 0], [-FIBA.keyHalfW, FIBA.ftY], [FIBA.keyHalfW, FIBA.ftY], [FIBA.keyHalfW, 0]]);
  // free-throw circle
  const arc = (cx: number, cy: number, R: number, a0: number, a1: number, dashed = false) => {
    const pts: [number, number][] = [];
    for (let i = 0; i <= 90; i++) {
      const a = a0 + ((a1 - a0) * i) / 90;
      pts.push([cx + R * Math.cos(a), cy + R * Math.sin(a)]);
    }
    if (dashed) g.setLineDash([m2px(0.35), m2px(0.3)]);
    line(pts);
    g.setLineDash([]);
  };
  arc(0, FIBA.ftY, FIBA.ftR, 0, Math.PI);
  arc(0, FIBA.ftY, FIBA.ftR, Math.PI, 2 * Math.PI, true);
  // three-point line
  const ja = Math.atan2(threeJoinY - FIBA.basket[1], FIBA.cornerX);
  line([[-FIBA.cornerX, 0], [-FIBA.cornerX, threeJoinY]]);
  line([[FIBA.cornerX, 0], [FIBA.cornerX, threeJoinY]]);
  arc(FIBA.basket[0], FIBA.basket[1], FIBA.threeR, ja, Math.PI - ja);
  // restricted area
  arc(FIBA.basket[0], FIBA.basket[1], FIBA.restrictedR, 0, Math.PI);
  // lane marks
  for (const y of [1.75, 2.6, 3.45, 4.3]) {
    line([[-FIBA.keyHalfW - 0.1, y], [-FIBA.keyHalfW, y]]);
    line([[FIBA.keyHalfW, y], [FIBA.keyHalfW + 0.1, y]]);
  }
  // centre circle (at half court) with the logo
  arc(0, FIBA.halfL, FIBA.centreR, Math.PI, 2 * Math.PI);
  if (logo) {
    const [cx, cy] = toPx(0, FIBA.halfL - 0.9);
    const w = m2px(1.6);
    const h = (w * logo.height) / logo.width;
    g.globalAlpha = 0.5;
    g.drawImage(logo, cx - w / 2, cy - h / 2, w, h);
    g.globalAlpha = 1;
  }
  // gold baseline accent stripe on the apron
  g.fillStyle = 'rgba(201,162,77,0.85)';
  const [, by2] = toPx(0, -0.55);
  g.fillRect(lx, by2, rx - lx, m2px(0.06));
  const map = new THREE.CanvasTexture(c);
  map.colorSpace = THREE.SRGBColorSpace;
  map.anisotropy = 8;
  const rough = new THREE.CanvasTexture(r);
  floorTex = {map, rough};
  return floorTex;
};

const NetGeo = (() => {
  // a tapered net: lathe wireframe lines
  const pts: THREE.Vector3[] = [];
  const top = FIBA.rimR;
  const bot = 0.15;
  const h = 0.42;
  const N = 16;
  for (let i = 0; i < N; i++) {
    const a = (i / N) * Math.PI * 2;
    const a2 = ((i + 0.5) / N) * Math.PI * 2;
    // diagonal strands make the diamond pattern
    for (let k = 0; k < 4; k++) {
      const v0 = k / 4;
      const v1 = (k + 1) / 4;
      const r0 = top + (bot - top) * v0;
      const r1 = top + (bot - top) * v1;
      const aa = k % 2 === 0 ? a : a2;
      const bb = k % 2 === 0 ? a2 : a;
      pts.push(new THREE.Vector3(r0 * Math.cos(aa), -h * v0, r0 * Math.sin(aa)));
      pts.push(new THREE.Vector3(r1 * Math.cos(bb), -h * v1, r1 * Math.sin(bb)));
      pts.push(new THREE.Vector3(r0 * Math.cos(bb + 0.0), -h * v0, r0 * Math.sin(bb)));
      pts.push(new THREE.Vector3(r1 * Math.cos(aa), -h * v1, r1 * Math.sin(aa)));
    }
  }
  return new THREE.BufferGeometry().setFromPoints(pts);
})();

export const Basket: React.FC<{swish?: number}> = ({swish = 0}) => {
  const [bx, by, bz] = W3([FIBA.basket[0], FIBA.basket[1], FIBA.rimZ]);
  const boardZ = W3([0, FIBA.boardY, 0])[2];
  const boardW = FIBA.boardHalfW * 2;
  const boardH = FIBA.boardZ1 - FIBA.boardZ0;
  const netScale = 1 + 0.12 * Math.sin(swish * Math.PI) * (1 - swish);
  return (
    <group>
      {/* glass */}
      <mesh position={[0, (FIBA.boardZ0 + FIBA.boardZ1) / 2, boardZ]}>
        <boxGeometry args={[boardW, boardH, 0.03]} />
        <meshPhysicalMaterial color="#cfe3ff" transparent opacity={0.16} roughness={0.05} metalness={0.1} />
      </mesh>
      {/* board frame + shooter's square */}
      {[
        [0, FIBA.boardZ1, boardW, 0.05],
        [0, FIBA.boardZ0, boardW, 0.05],
        [-boardW / 2, (FIBA.boardZ0 + FIBA.boardZ1) / 2, 0.05, boardH],
        [boardW / 2, (FIBA.boardZ0 + FIBA.boardZ1) / 2, 0.05, boardH],
        [0, FIBA.rimZ + 0.15 + 0.45, 0.59, 0.05],
        [0, FIBA.rimZ + 0.15, 0.59, 0.05],
        [-0.295, FIBA.rimZ + 0.375, 0.05, 0.45],
        [0.295, FIBA.rimZ + 0.375, 0.05, 0.45],
      ].map(([x, y, w, h], i) => (
        <mesh key={i} position={[x, y, boardZ + 0.02]}>
          <boxGeometry args={[w, h, 0.02]} />
          <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.15} roughness={0.4} />
        </mesh>
      ))}
      {/* support arm + stanchion */}
      <mesh position={[0, FIBA.boardZ0 + 0.2, boardZ + 0.75]} castShadow>
        <boxGeometry args={[0.16, 0.16, 1.5]} />
        <meshStandardMaterial color="#1B2A4A" roughness={0.5} metalness={0.3} />
      </mesh>
      <mesh position={[0, 1.6, boardZ + 1.5]} castShadow>
        <boxGeometry args={[0.28, 3.2, 0.28]} />
        <meshStandardMaterial color="#1B2A4A" roughness={0.5} metalness={0.3} />
      </mesh>
      <mesh position={[0, 0.45, boardZ + 1.9]} castShadow receiveShadow>
        <boxGeometry args={[1.4, 0.9, 1.4]} />
        <meshStandardMaterial color="#0B1C3D" roughness={0.6} />
      </mesh>
      <mesh position={[0, 0.91, boardZ + 1.9]}>
        <boxGeometry args={[1.42, 0.03, 1.42]} />
        <meshStandardMaterial color="#C9A24D" roughness={0.35} metalness={0.6} />
      </mesh>
      {/* rim */}
      <mesh position={[bx, by, bz]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <torusGeometry args={[FIBA.rimR, 0.012, 10, 48]} />
        <meshStandardMaterial color="#E2552A" roughness={0.35} metalness={0.4} emissive="#5a1a05" emissiveIntensity={0.4} />
      </mesh>
      <mesh position={[bx, by, (bz + boardZ) / 2]} castShadow>
        <boxGeometry args={[0.05, 0.02, Math.abs(bz - boardZ) - FIBA.rimR]} />
        <meshStandardMaterial color="#E2552A" roughness={0.4} />
      </mesh>
      <lineSegments geometry={NetGeo} position={[bx, by, bz]} scale={[netScale, 1, netScale]}>
        <lineBasicMaterial color="#f4f4f4" transparent opacity={0.85} />
      </lineSegments>
    </group>
  );
};

export const Court3D: React.FC<{logo?: HTMLImageElement; swish?: number}> = ({logo, swish}) => {
  const tex = React.useMemo(() => buildFloor(logo), [logo]);
  const cx = 0;
  const cy = Y0 + SPAN / 2;
  const [px, , pz] = W3([cx, cy, 0]);
  return (
    <group>
      {/* parquet */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[px, 0, pz]} receiveShadow>
        <planeGeometry args={[SPAN, SPAN]} />
        <meshStandardMaterial map={tex.map} roughnessMap={tex.rough} roughness={0.85} metalness={0.0} envMapIntensity={0.8} />
      </mesh>
      {/* dark arena floor beyond the texture */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.005, -7]} receiveShadow>
        <planeGeometry args={[80, 80]} />
        <meshStandardMaterial color="#070D1A" roughness={0.9} />
      </mesh>
      <Arena />
      <Basket swish={swish} />
    </group>
  );
};

/** arena light rig: overhead key light with soft shadows, fill, rim/back light, ambient */
export const ArenaLights: React.FC<{focus?: [number, number, number]}> = ({focus = [0, 0, -5]}) => {
  const target = React.useMemo(() => new THREE.Object3D(), []);
  target.position.set(...focus);
  return (
    <>
      <hemisphereLight args={['#9fb4dc', '#2a1a0e', 0.55]} />
      <primitive object={target} />
      <spotLight
        position={[focus[0] + 3, 14, focus[2] + 5]}
        target={target}
        angle={0.62}
        penumbra={0.85}
        intensity={760}
        decay={2}
        color="#fff3e2"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-bias={-0.0002}
        shadow-normalBias={0.02}
        shadow-radius={4}
      />
      <spotLight position={[focus[0] - 7, 9, focus[2] - 6]} target={target} angle={0.7} penumbra={0.9} intensity={260} decay={2} color="#cdd9ff" />
      {/* back/rim light for silhouette separation */}
      <directionalLight position={[2, 6, -18]} intensity={1.1} color="#ffd9a0" />
      <ambientLight intensity={0.12} />
    </>
  );
};

// ---------- arena: tiered stands with a dim crowd, LED ribbon, ceiling lights, env reflections ----------
const crowdGeo = new THREE.CapsuleGeometry(0.15, 0.3, 3, 6);
const rowGeo = new THREE.BoxGeometry(1, 1, 1);

const Stand: React.FC<{origin: [number, number, number]; along: [number, number, number]; out: [number, number, number]; length: number; rows: number; seed: number}> = ({origin, along, out, length, rows, seed}) => {
  const crowd = React.useMemo(() => {
    const m = new THREE.InstancedMesh(crowdGeo, new THREE.MeshStandardMaterial({roughness: 0.9}), Math.ceil((length / 0.62) * rows));
    const o = new THREE.Object3D();
    let n = 0;
    const col = new THREE.Color();
    for (let r = 0; r < rows; r++) {
      for (let i = 0; i < length / 0.62; i++) {
        const k = seed * 1000 + r * 97 + i;
        if (rnd(k) < 0.22) continue; // empty seats
        const a = -length / 2 + i * 0.62 + (rnd(k + 1) - 0.5) * 0.2;
        o.position.set(origin[0] + along[0] * a + out[0] * (r * 0.85 + 0.4), origin[1] + r * 0.42 + 0.55 + rnd(k + 2) * 0.08, origin[2] + along[2] * a + out[2] * (r * 0.85 + 0.4));
        o.scale.setScalar(0.9 + rnd(k + 3) * 0.25);
        o.updateMatrix();
        m.setMatrixAt(n, o.matrix);
        const tone = rnd(k + 4);
        col.setHSL(0.6 + tone * 0.08, 0.2, 0.025 + tone * 0.035);
        if (rnd(k + 5) < 0.1) col.set('#1c160c'); // a few gold-ish shirts
        m.setColorAt(n, col);
        n++;
      }
    }
    m.count = n;
    return m;
  }, [origin, along, out, length, rows, seed]);
  const steps = Array.from({length: rows}, (_, r) => r);
  const rotY = Math.atan2(along[0], along[2]);
  return (
    <group>
      {steps.map((r) => (
        <mesh key={r} geometry={rowGeo} position={[origin[0] + out[0] * (r * 0.85 + 0.4), origin[1] + r * 0.42 + 0.2, origin[2] + out[2] * (r * 0.85 + 0.4)]} rotation={[0, rotY, 0]} scale={[0.85, 0.42 + r * 0.0 + 0.4, length]}>
          <meshStandardMaterial color={r % 2 ? '#0B1424' : '#0D182B'} roughness={0.95} />
        </mesh>
      ))}
      <primitive object={crowd} />
      {/* LED ribbon on the front wall of the stand */}
      <mesh position={[origin[0] - out[0] * 0.05, origin[1] + 0.55, origin[2] - out[2] * 0.05]} rotation={[0, rotY, 0]}>
        <boxGeometry args={[0.02, 0.12, length]} />
        <meshBasicMaterial color="#C9A24D" toneMapped={false} />
      </mesh>
      <mesh position={[origin[0] - out[0] * 0.03, origin[1] + 0.3, origin[2] - out[2] * 0.03]} rotation={[0, rotY, 0]}>
        <boxGeometry args={[0.03, 0.6, length]} />
        <meshStandardMaterial color="#0B1C3D" roughness={0.6} />
      </mesh>
    </group>
  );
};

const EnvMap: React.FC = () => {
  const {gl, scene} = useThree();
  React.useMemo(() => {
    const pm = new THREE.PMREMGenerator(gl);
    const env = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = env;
    scene.environmentIntensity = 0.35;
  }, [gl, scene]);
  return null;
};

export const Arena: React.FC = () => (
  <group>
    <EnvMap />
    {/* behind the baseline (world y < 0 -> three z > 0) */}
    <Stand origin={[0, 0, 4.2]} along={[1, 0, 0]} out={[0, 0, 1]} length={30} rows={14} seed={1} />
    {/* both sidelines */}
    <Stand origin={[-10.2, 0, -8]} along={[0, 0, 1]} out={[-1, 0, 0]} length={30} rows={14} seed={2} />
    <Stand origin={[10.2, 0, -8]} along={[0, 0, 1]} out={[1, 0, 0]} length={30} rows={14} seed={3} />
    {/* far end */}
    <Stand origin={[0, 0, -30]} along={[1, 0, 0]} out={[0, 0, -1]} length={30} rows={14} seed={4} />
    {/* ceiling light banks */}
    {Array.from({length: 18}, (_, i) => {
      const x = ((i % 6) - 2.5) * 4.2;
      const z = -Math.floor(i / 6) * 9 - 2;
      return (
        <mesh key={i} position={[x, 17, z]} rotation={[Math.PI / 2, 0, 0]}>
          <circleGeometry args={[0.55, 20]} />
          <meshBasicMaterial color="#fff6e6" toneMapped={false} side={THREE.DoubleSide} />
        </mesh>
      );
    })}
  </group>
);
