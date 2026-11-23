// E2A Football — graphics drawn ON the pitch (world space): pass lines that follow the real ball path,
// run arrows from the real player route, zones, the defensive line through the defenders, offside line,
// player rings. They are lit like paint on grass (unlit, slightly emissive) and drawn progressively.
import React from 'react';
import * as THREE from 'three';
import {GOLD, RED, WHITE} from './brand';
import {W3} from './athlete';
import type {FBPlay, V2} from './play';
import {ballPath, offsideLine, playerAt, routeOf, smooth} from './play';

export type Ov =
  | {type: 'pass'; t0: number; t1: number; color?: string; dashed?: boolean; width?: number; trail?: boolean} // trail: the line follows the real ball (head at the ball)
  | {type: 'run'; player: string; t0: number; t1: number; color?: string; width?: number; dashed?: boolean}
  | {type: 'zone'; c: V2; r: V2; color?: string; label?: string; follow?: string}
  | {type: 'defline'; players: string[]; at?: number; color?: string}
  | {type: 'ring'; player: string; color?: string; r?: number}
  | {type: 'offside'; at: number; color?: string; span?: [number, number]}
  // FB-SETPIECE-001: a ring at a fixed point (ghost of a player's start spot, a legal distance) and a straight arrow
  | {type: 'circle'; c: V2; r: number; color?: string; dashed?: boolean; arc?: [number, number]; width?: number; fill?: number}
  | {type: 'arrow'; p0: V2; p1: V2; color?: string; dashed?: boolean; width?: number};
export type LiveOv = Ov & {age: number; dur: number; draw?: number};

const H = 0.03;

const cut = (pts: V2[], f: number): V2[] => {
  if (f >= 1 || pts.length < 2) return pts;
  const L: number[] = [0];
  for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const target = L[L.length - 1] * Math.max(0, f);
  const out: V2[] = [pts[0]];
  for (let i = 1; i < pts.length; i++) {
    if (L[i] <= target) out.push(pts[i]);
    else {
      const u = (target - L[i - 1]) / Math.max(1e-6, L[i] - L[i - 1]);
      out.push([pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * u, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * u]);
      break;
    }
  }
  return out;
};

/** flat ribbon along a polyline (+ optional arrow head), as a single BufferGeometry */
const ribbon = (pts: V2[], w: number, dashed: boolean, head: boolean, h = H) => {
  const pos: number[] = [];
  const push = (p: V2, z = h) => pos.push(...W3([p[0], p[1], z]));
  const quad = (a: V2, b: V2, wa: number, wb: number) => {
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1;
    const nx = -dy / l;
    const ny = dx / l;
    const a1: V2 = [a[0] + nx * wa, a[1] + ny * wa];
    const a2: V2 = [a[0] - nx * wa, a[1] - ny * wa];
    const b1: V2 = [b[0] + nx * wb, b[1] + ny * wb];
    const b2: V2 = [b[0] - nx * wb, b[1] - ny * wb];
    push(a1);
    push(a2);
    push(b1);
    push(b1);
    push(a2);
    push(b2);
  };
  if (pts.length < 2) return null;
  // total length and resample
  let total = 0;
  for (let i = 1; i < pts.length; i++) total += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  if (total < 0.05) return null;
  const headL = head ? Math.min(1.6, total * 0.4) : 0;
  // walk along, stop before the head
  let acc = 0;
  const dash = 0.9;
  const gap = 0.55;
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1];
    const b = pts[i];
    const sl = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (sl < 1e-6) continue;
    let s0 = 0;
    while (s0 < sl) {
      const g = acc + s0;
      if (g >= total - headL) break;
      let s1 = Math.min(sl, s0 + 0.5, total - headL - acc);
      if (dashed) {
        const m = g % (dash + gap);
        if (m >= dash) {
          s0 += Math.max(1e-3, Math.min(sl - s0, dash + gap - m));
          continue;
        }
        s1 = Math.min(s1, s0 + Math.max(1e-3, dash - m));
      }
      const u0 = s0 / sl;
      const u1 = s1 / sl;
      quad([a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0], [a[0] + (b[0] - a[0]) * u1, a[1] + (b[1] - a[1]) * u1], w, w);
      if (s1 <= s0) break;
      s0 = s1;
    }
    acc += sl;
  }
  if (head) {
    const e = pts[pts.length - 1];
    // direction from the point headL back along the line
    let k = pts.length - 2;
    while (k > 0 && Math.hypot(e[0] - pts[k][0], e[1] - pts[k][1]) < headL) k--;
    const s = pts[k];
    const dx = e[0] - s[0];
    const dy = e[1] - s[1];
    const l = Math.hypot(dx, dy) || 1;
    const ux = dx / l;
    const uy = dy / l;
    const bx = e[0] - ux * headL;
    const by = e[1] - uy * headL;
    const hw = w * 3.2;
    push([bx - uy * hw, by + ux * hw], h + 0.001);
    push([bx + uy * hw, by - ux * hw], h + 0.001);
    push(e, h + 0.001);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  return g;
};

const useDispose = (g: THREE.BufferGeometry | null) => {
  React.useEffect(() => () => g?.dispose(), [g]);
};

const Paint: React.FC<{g: THREE.BufferGeometry | null; color: string; opacity: number; glow?: boolean}> = ({g, color, opacity, glow}) => {
  useDispose(g);
  if (!g) return null;
  return (
    <>
      <mesh geometry={g} renderOrder={5}>
        <meshBasicMaterial color={color} transparent opacity={opacity} depthWrite={false} side={THREE.DoubleSide} toneMapped={false} />
      </mesh>
      {glow && (
        <mesh geometry={g} renderOrder={4} scale={[1, 1, 1]}>
          <meshBasicMaterial color={color} transparent opacity={opacity * 0.25} depthWrite={false} side={THREE.DoubleSide} toneMapped={false} />
        </mesh>
      )}
    </>
  );
};

const fade = (o: LiveOv) => Math.min(1, o.age / 0.18) * Math.min(1, Math.max(0, (o.dur - o.age) / 0.2));

const PassLine: React.FC<{play: FBPlay; pt: number; o: Extract<LiveOv, {type: 'pass'}>}> = ({play, pt, o}) => {
  const prog = smooth(o.age / (o.draw ?? 0.6));
  const end = o.trail ? Math.max(o.t0, Math.min(o.t1, pt)) : o.t1;
  const g = React.useMemo(
    () => (o.trail ? (end - o.t0 > 0.02 ? ribbon(ballPath(play, o.t0, end, 1 / 60), o.width ?? 0.16, o.dashed ?? true, true) : null) : ribbon(cut(ballPath(play, o.t0, o.t1), prog), o.width ?? 0.16, o.dashed ?? true, true)),
    [play, o.t0, o.t1, end, o.trail, prog, o.width, o.dashed],
  );
  return <Paint g={g} color={o.color ?? GOLD} opacity={0.95 * fade(o)} />;
};

const Run: React.FC<{play: FBPlay; o: Extract<LiveOv, {type: 'run'}>}> = ({play, o}) => {
  const prog = smooth(o.age / (o.draw ?? 0.8));
  const g = React.useMemo(() => ribbon(cut(routeOf(play, o.player, o.t0, o.t1), prog), o.width ?? 0.2, o.dashed ?? false, true), [play, o.player, o.t0, o.t1, prog, o.width, o.dashed]);
  return <Paint g={g} color={o.color ?? WHITE} opacity={0.92 * fade(o)} />;
};

const Zone: React.FC<{play: FBPlay; pt: number; o: Extract<LiveOv, {type: 'zone'}>}> = ({play, pt, o}) => {
  const a = fade(o);
  const grow = smooth(o.age / 0.5);
  const pulse = 0.85 + 0.15 * Math.sin(o.age * 5);
  const c = o.follow ? playerAt(play, o.follow, pt).pos : o.c;
  const col = o.color ?? GOLD;
  return (
    <group position={W3([c[0], c[1], H - 0.01])} scale={[o.r[0] * grow, 1, o.r[1] * grow]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={3}>
        <circleGeometry args={[1, 64]} />
        <meshBasicMaterial color={col} transparent opacity={0.2 * a * pulse} depthWrite={false} toneMapped={false} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={4}>
        <ringGeometry args={[0.965, 1, 96]} />
        <meshBasicMaterial color={col} transparent opacity={0.9 * a} depthWrite={false} toneMapped={false} />
      </mesh>
    </group>
  );
};

const DefLine: React.FC<{play: FBPlay; pt: number; o: Extract<LiveOv, {type: 'defline'}>}> = ({play, pt, o}) => {
  const t = o.at ?? pt;
  const pts = o.players.map((id) => playerAt(play, id, t).pos).sort((a, b) => a[1] - b[1]);
  const prog = smooth(o.age / 0.6);
  const g = React.useMemo(() => {
    const ext: V2[] = [[pts[0][0], pts[0][1] - 3], ...pts, [pts[pts.length - 1][0], pts[pts.length - 1][1] + 3]];
    // draw from the centre outwards
    const mid = Math.floor(ext.length / 2);
    const left = cut(ext.slice(0, mid + 1).reverse(), prog);
    const right = cut(ext.slice(mid), prog);
    const gl = ribbon(left, 0.2, true, false);
    const gr = ribbon(right, 0.2, true, false);
    if (!gl || !gr) return gl ?? gr;
    const a = gl.getAttribute('position').array as Float32Array;
    const b = gr.getAttribute('position').array as Float32Array;
    const m = new THREE.BufferGeometry();
    m.setAttribute('position', new THREE.Float32BufferAttribute([...a, ...b], 3));
    gl.dispose();
    gr.dispose();
    return m;
  }, [pts.map((p) => p.join(',')).join(';'), prog]);
  return <Paint g={g} color={o.color ?? WHITE} opacity={0.95 * fade(o)} glow />;
};

const Offside: React.FC<{play: FBPlay; o: Extract<LiveOv, {type: 'offside'}>}> = ({play, o}) => {
  const x = offsideLine(play, o.at);
  const [y0, y1] = o.span ?? [-22, 22];
  const prog = smooth(o.age / 0.5);
  const c = (y0 + y1) / 2;
  const g = React.useMemo(() => ribbon([[x, c - (c - y0) * prog], [x, c + (y1 - c) * prog]], 0.07, true, false), [x, c, y0, y1, prog]);
  return <Paint g={g} color={o.color ?? GOLD} opacity={0.95 * fade(o)} />;
};

const Ring: React.FC<{play: FBPlay; pt: number; o: Extract<LiveOv, {type: 'ring'}>}> = ({play, pt, o}) => {
  const p = playerAt(play, o.player, pt).pos;
  const a = fade(o);
  const r = (o.r ?? 0.85) * (0.6 + 0.4 * smooth(o.age / 0.35));
  const col = o.color ?? GOLD;
  return (
    <group position={W3([p[0], p[1], H])}>
      <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={6}>
        <ringGeometry args={[r * 0.82, r, 64]} />
        <meshBasicMaterial color={col} transparent opacity={0.95 * a} depthWrite={false} toneMapped={false} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={5}>
        <circleGeometry args={[r * 0.82, 48]} />
        <meshBasicMaterial color={col} transparent opacity={0.16 * a} depthWrite={false} toneMapped={false} />
      </mesh>
    </group>
  );
};

const Circle: React.FC<{o: Extract<LiveOv, {type: 'circle'}>}> = ({o}) => {
  const prog = smooth(o.age / (o.draw ?? 0.5));
  const [a0, a1] = o.arc ?? [0, Math.PI * 2];
  const g = React.useMemo(() => {
    const n = Math.max(12, Math.round(Math.abs(a1 - a0) * o.r * 3));
    const pts: V2[] = [];
    for (let i = 0; i <= n; i++) {
      const a = a0 + ((a1 - a0) * i) / n;
      pts.push([o.c[0] + Math.cos(a) * o.r, o.c[1] + Math.sin(a) * o.r]);
    }
    return ribbon(cut(pts, prog), o.width ?? 0.07, o.dashed ?? true, false);
  }, [o.c[0], o.c[1], o.r, a0, a1, prog, o.dashed, o.width]);
  const a = fade(o);
  return (
    <>
      <Paint g={g} color={o.color ?? WHITE} opacity={0.95 * a} />
      {o.fill ? (
        <mesh position={W3([o.c[0], o.c[1], H - 0.012])} rotation={[-Math.PI / 2, 0, 0]} renderOrder={3}>
          <circleGeometry args={[o.r, 48]} />
          <meshBasicMaterial color={o.color ?? WHITE} transparent opacity={o.fill * a * smooth(o.age / 0.4)} depthWrite={false} toneMapped={false} />
        </mesh>
      ) : null}
    </>
  );
};

const Arrow: React.FC<{o: Extract<LiveOv, {type: 'arrow'}>}> = ({o}) => {
  const prog = smooth(o.age / (o.draw ?? 0.6));
  const g = React.useMemo(() => ribbon(cut([o.p0, o.p1], prog), o.width ?? 0.16, o.dashed ?? false, true), [o.p0[0], o.p0[1], o.p1[0], o.p1[1], prog, o.width, o.dashed]);
  return <Paint g={g} color={o.color ?? GOLD} opacity={0.92 * fade(o)} />;
};

export const Overlays3D: React.FC<{play: FBPlay; pt: number; items: LiveOv[]}> = ({play, pt, items}) => (
  <group>
    {items.map((o, i) => {
      switch (o.type) {
        case 'pass':
          return <PassLine key={i} play={play} pt={pt} o={o} />;
        case 'run':
          return <Run key={i} play={play} o={o} />;
        case 'zone':
          return <Zone key={i} play={play} pt={pt} o={o} />;
        case 'defline':
          return <DefLine key={i} play={play} pt={pt} o={o} />;
        case 'offside':
          return <Offside key={i} play={play} o={o} />;
        case 'ring':
          return <Ring key={i} play={play} pt={pt} o={o} />;
        case 'circle':
          return <Circle key={i} o={o} />;
        case 'arrow':
          return <Arrow key={i} o={o} />;
        default:
          return null;
      }
    })}
  </group>
);

export {RED};
