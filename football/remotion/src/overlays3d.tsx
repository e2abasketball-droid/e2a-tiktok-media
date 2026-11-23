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
  | {type: 'run'; player: string; t0: number; t1: number; color?: string; width?: number; dashed?: boolean; trail?: boolean} // trail (V05): drawn up to the player in play time — shows the TIMING of the run
  | {type: 'zone'; c: V2; r: V2; color?: string; label?: string; follow?: string}
  | {type: 'defline'; players: string[]; at?: number; color?: string}
  | {type: 'ring'; player: string; color?: string; r?: number}
  | {type: 'offside'; at: number; color?: string; span?: [number, number]}
  // FB-SETPIECE-001: a ring at a fixed point (ghost of a player's start spot, a legal distance) and a straight arrow
  | {type: 'circle'; c: V2; r: number; color?: string; dashed?: boolean; arc?: [number, number]; width?: number; fill?: number}
  | {type: 'arrow'; p0: V2; p1: V2; color?: string; dashed?: boolean; width?: number}
  // V05 analytical graphics: a marking connection between two players (follows them), and a ground wedge
  // from a player or a point — orientation / line of sight (dir 'heading'), passing window or finishing lane
  // (dir = a point or a player). `len` metres, `half` = half-angle in radians.
  | {type: 'link'; a: string; b: string; color?: string; dashed?: boolean; width?: number}
  | {type: 'cone'; player?: string; p?: V2; dir: 'heading' | V2 | string; len: number; half: number; color?: string; opacity?: number};
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

// ---------- graphics v2 (FB-SETPIECE-001 V03): smoothed curves, tapered tails, notched heads, dark under-stroke
const chaikin = (pts: V2[], it = 2): V2[] => {
  let p = pts;
  for (let k = 0; k < it && p.length > 2; k++) {
    const q: V2[] = [p[0]];
    for (let i = 0; i < p.length - 1; i++) {
      const a = p[i];
      const b = p[i + 1];
      q.push([0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]], [0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]]);
    }
    q.push(p[p.length - 1]);
    p = q;
  }
  return p;
};
/** thin out a dense polyline (keeps the curve, avoids thousands of tiny quads) */
const decimate = (pts: V2[], minStep = 0.25): V2[] => {
  if (pts.length < 3) return pts;
  const out: V2[] = [pts[0]];
  for (let i = 1; i < pts.length - 1; i++) {
    const l = out[out.length - 1];
    if (Math.hypot(pts[i][0] - l[0], pts[i][1] - l[1]) >= minStep) out.push(pts[i]);
  }
  out.push(pts[pts.length - 1]);
  return out;
};
const ribbon2 = (raw: V2[], w: number, dashed: boolean, head: boolean, h = H) => {
  const pts = chaikin(decimate(raw));
  if (pts.length < 2) return null;
  const L: number[] = [0];
  for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const total = L[L.length - 1];
  if (total < 0.08) return null;
  const headL = head ? Math.min(1.25, Math.max(0.45, total * 0.3)) : 0;
  const bodyEnd = total - headL * 0.72;
  const pos: number[] = [];
  const push = (p: V2, z = h) => pos.push(...W3([p[0], p[1], z]));
  const at = (d: number): {p: V2; n: V2} => {
    let i = 1;
    while (i < L.length - 1 && L[i] < d) i++;
    const a = pts[i - 1];
    const b = pts[i];
    const u = (d - L[i - 1]) / Math.max(1e-6, L[i] - L[i - 1]);
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1;
    return {p: [a[0] + dx * u, a[1] + dy * u], n: [-dy / l, dx / l]};
  };
  const width = (d: number) => w * (0.3 + 0.7 * smooth(d / Math.max(0.6, total * 0.3)));
  const step = 0.18;
  const dash = 0.75;
  const gap = 0.45;
  for (let d = 0; d < bodyEnd - 1e-4; d += step) {
    let d1 = Math.min(bodyEnd, d + step);
    if (dashed) {
      const m = d % (dash + gap);
      if (m >= dash) continue;
      d1 = Math.min(d1, d - m + dash);
    }
    const A = at(d);
    const B = at(d1);
    const wa = width(d);
    const wb = width(d1);
    const a1: V2 = [A.p[0] + A.n[0] * wa, A.p[1] + A.n[1] * wa];
    const a2: V2 = [A.p[0] - A.n[0] * wa, A.p[1] - A.n[1] * wa];
    const b1: V2 = [B.p[0] + B.n[0] * wb, B.p[1] + B.n[1] * wb];
    const b2: V2 = [B.p[0] - B.n[0] * wb, B.p[1] - B.n[1] * wb];
    push(a1);
    push(a2);
    push(b1);
    push(b1);
    push(a2);
    push(b2);
  }
  if (head) {
    const tip = at(total).p;
    const base = at(total - headL);
    const notch = at(total - headL * 0.72).p;
    const hw = Math.max(w * 2.6, 0.32);
    const l1: V2 = [base.p[0] + base.n[0] * hw, base.p[1] + base.n[1] * hw];
    const r1: V2 = [base.p[0] - base.n[0] * hw, base.p[1] - base.n[1] * hw];
    push(l1, h + 0.001);
    push(notch, h + 0.001);
    push(tip, h + 0.001);
    push(notch, h + 0.001);
    push(r1, h + 0.001);
    push(tip, h + 0.001);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  return g;
};

/** v2 paint: dark under-stroke (legible on bright grass) + the colour stroke */
const Paint2: React.FC<{pts: V2[]; w: number; dashed: boolean; head: boolean; color: string; opacity: number}> = ({pts, w, dashed, head, color, opacity}) => {
  const key = pts.length ? `${pts.length}:${pts[pts.length - 1][0].toFixed(3)},${pts[pts.length - 1][1].toFixed(3)}:${w}:${dashed}:${head}` : '';
  const g = React.useMemo(() => ribbon2(pts, w, dashed, head, H + 0.004), [key]);
  const gs = React.useMemo(() => ribbon2(pts, w * 1.7, dashed, head, H), [key]);
  useDispose(g);
  useDispose(gs);
  if (!g) return null;
  return (
    <>
      {gs && (
        <mesh geometry={gs} renderOrder={4}>
          <meshBasicMaterial color="#06122A" transparent opacity={opacity * 0.38} depthWrite={false} side={THREE.DoubleSide} toneMapped={false} />
        </mesh>
      )}
      <mesh geometry={g} renderOrder={5}>
        <meshBasicMaterial color={color} transparent opacity={opacity} depthWrite={false} side={THREE.DoubleSide} toneMapped={false} />
      </mesh>
    </>
  );
};

let zoneTex: THREE.Texture | null = null;
const zoneTexture = () => {
  if (zoneTex) return zoneTex;
  const c = document.createElement('canvas');
  c.width = 256;
  c.height = 256;
  const g = c.getContext('2d')!;
  const grd = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  grd.addColorStop(0, 'rgba(255,255,255,0.75)');
  grd.addColorStop(0.55, 'rgba(255,255,255,0.45)');
  grd.addColorStop(0.92, 'rgba(255,255,255,0.12)');
  grd.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grd;
  g.fillRect(0, 0, 256, 256);
  zoneTex = new THREE.CanvasTexture(c);
  return zoneTex;
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

const PassLine: React.FC<{play: FBPlay; pt: number; o: Extract<LiveOv, {type: 'pass'}>; v2?: boolean}> = ({play, pt, o, v2}) => {
  const prog = smooth(o.age / (o.draw ?? 0.6));
  if (v2) {
    const end = o.trail ? Math.max(o.t0, Math.min(o.t1, pt)) : o.t1;
    const pts = o.trail ? (end - o.t0 > 0.02 ? ballPath(play, o.t0, end, 1 / 60) : []) : cut(ballPath(play, o.t0, o.t1, 1 / 60), prog);
    return <Paint2 pts={pts} w={o.width ?? 0.11} dashed={o.dashed ?? false} head color={o.color ?? GOLD} opacity={0.96 * fade(o)} />;
  }
  const end = o.trail ? Math.max(o.t0, Math.min(o.t1, pt)) : o.t1;
  const g = React.useMemo(
    () => (o.trail ? (end - o.t0 > 0.02 ? ribbon(ballPath(play, o.t0, end, 1 / 60), o.width ?? 0.16, o.dashed ?? true, true) : null) : ribbon(cut(ballPath(play, o.t0, o.t1), prog), o.width ?? 0.16, o.dashed ?? true, true)),
    [play, o.t0, o.t1, end, o.trail, prog, o.width, o.dashed],
  );
  return <Paint g={g} color={o.color ?? GOLD} opacity={0.95 * fade(o)} />;
};

const Run: React.FC<{play: FBPlay; o: Extract<LiveOv, {type: 'run'}>; v2?: boolean; pt?: number}> = ({play, o, v2, pt}) => {
  const prog = smooth(o.age / (o.draw ?? 0.8));
  if (v2 && o.trail) {
    const end = Math.max(o.t0, Math.min(o.t1, pt ?? o.t1));
    const pts = end - o.t0 > 0.05 ? routeOf(play, o.player, o.t0, end) : [];
    return <Paint2 pts={pts} w={o.width ?? 0.085} dashed={o.dashed ?? true} head color={o.color ?? WHITE} opacity={0.95 * fade(o)} />;
  }
  if (v2) return <Paint2 pts={cut(routeOf(play, o.player, o.t0, o.t1), prog)} w={o.width ?? 0.085} dashed={o.dashed ?? true} head color={o.color ?? WHITE} opacity={0.95 * fade(o)} />;
  const g = React.useMemo(() => ribbon(cut(routeOf(play, o.player, o.t0, o.t1), prog), o.width ?? 0.2, o.dashed ?? false, true), [play, o.player, o.t0, o.t1, prog, o.width, o.dashed]);
  return <Paint g={g} color={o.color ?? WHITE} opacity={0.92 * fade(o)} />;
};

const Zone: React.FC<{play: FBPlay; pt: number; o: Extract<LiveOv, {type: 'zone'}>; v2?: boolean}> = ({play, pt, o, v2}) => {
  const a = fade(o);
  const grow = smooth(o.age / 0.5);
  const pulse = 0.85 + 0.15 * Math.sin(o.age * 5);
  const c = o.follow ? playerAt(play, o.follow, pt).pos : o.c;
  const col = o.color ?? GOLD;
  if (v2) {
    // soft radial light on the grass (texture stays visible) + a fine edge
    const breathe = 0.92 + 0.08 * Math.sin(o.age * 3.2);
    return (
      <group position={W3([c[0], c[1], H - 0.012])} scale={[o.r[0] * (0.7 + 0.3 * grow), 1, o.r[1] * (0.7 + 0.3 * grow)]}>
        <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={3}>
          <circleGeometry args={[1, 64]} />
          <meshBasicMaterial color={col} alphaMap={zoneTexture()} transparent opacity={0.42 * a * grow * breathe} depthWrite={false} toneMapped={false} />
        </mesh>
        <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={4}>
          <ringGeometry args={[0.985, 1, 128]} />
          <meshBasicMaterial color={col} transparent opacity={0.55 * a * grow} depthWrite={false} toneMapped={false} />
        </mesh>
      </group>
    );
  }
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

const Ring: React.FC<{play: FBPlay; pt: number; o: Extract<LiveOv, {type: 'ring'}>; v2?: boolean}> = ({play, pt, o, v2}) => {
  const p = playerAt(play, o.player, pt).pos;
  const a = fade(o);
  if (v2) {
    // proportioned to a body (r 0.62 m), thin line, faint fill, a short pop on entry
    const r = (o.r ?? 0.62) * (0.75 + 0.25 * smooth(o.age / 0.3)) * (1 + 0.12 * Math.exp(-o.age * 6) * Math.sin(o.age * 18));
    const col = o.color ?? GOLD;
    return (
      <group position={W3([p[0], p[1], H])}>
        <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={6}>
          <ringGeometry args={[r * 0.9, r, 64]} />
          <meshBasicMaterial color={col} transparent opacity={0.95 * a} depthWrite={false} toneMapped={false} />
        </mesh>
        <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={5}>
          <ringGeometry args={[r, r * 1.16, 64]} />
          <meshBasicMaterial color="#06122A" transparent opacity={0.3 * a} depthWrite={false} toneMapped={false} />
        </mesh>
        <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={5}>
          <circleGeometry args={[r * 0.9, 48]} />
          <meshBasicMaterial color={col} transparent opacity={0.1 * a} depthWrite={false} toneMapped={false} />
        </mesh>
      </group>
    );
  }
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

const Arrow: React.FC<{o: Extract<LiveOv, {type: 'arrow'}>; v2?: boolean}> = ({o, v2}) => {
  const prog = smooth(o.age / (o.draw ?? 0.6));
  if (v2) {
    // gentle curve (quadratic, bulging to the left of travel by 12 % of the length)
    const dx = o.p1[0] - o.p0[0];
    const dy = o.p1[1] - o.p0[1];
    const m: V2 = [(o.p0[0] + o.p1[0]) / 2 - dy * 0.12, (o.p0[1] + o.p1[1]) / 2 + dx * 0.12];
    const pts: V2[] = [];
    for (let i = 0; i <= 24; i++) {
      const u = i / 24;
      pts.push([(1 - u) ** 2 * o.p0[0] + 2 * u * (1 - u) * m[0] + u * u * o.p1[0], (1 - u) ** 2 * o.p0[1] + 2 * u * (1 - u) * m[1] + u * u * o.p1[1]]);
    }
    return <Paint2 pts={cut(pts, prog)} w={o.width ?? 0.11} dashed={o.dashed ?? false} head color={o.color ?? GOLD} opacity={0.95 * fade(o)} />;
  }
  const g = React.useMemo(() => ribbon(cut([o.p0, o.p1], prog), o.width ?? 0.16, o.dashed ?? false, true), [o.p0[0], o.p0[1], o.p1[0], o.p1[1], prog, o.width, o.dashed]);
  return <Paint g={g} color={o.color ?? GOLD} opacity={0.92 * fade(o)} />;
};

const Link: React.FC<{play: FBPlay; pt: number; o: Extract<LiveOv, {type: 'link'}>}> = ({play, pt, o}) => {
  const a = playerAt(play, o.a, pt).pos;
  const b = playerAt(play, o.b, pt).pos;
  const L = Math.hypot(b[0] - a[0], b[1] - a[1]);
  if (L < 0.5) return null;
  // stop 0.45 m short of each body so the line connects the players without crossing their feet
  const u: V2 = [(b[0] - a[0]) / L, (b[1] - a[1]) / L];
  const g = smooth(o.age / 0.35);
  const p0: V2 = [a[0] + u[0] * 0.45, a[1] + u[1] * 0.45];
  const p1: V2 = [p0[0] + u[0] * (L - 0.9) * g, p0[1] + u[1] * (L - 0.9) * g];
  return <Paint2 pts={[p0, p1]} w={o.width ?? 0.05} dashed={o.dashed ?? false} head={false} color={o.color ?? WHITE} opacity={0.9 * fade(o)} />;
};

let fanTex: THREE.Texture | null = null;
/** linear fade along the wedge (bright at the apex, gone at the end) */
const fanTexture = () => {
  if (fanTex) return fanTex;
  const c = document.createElement('canvas');
  c.width = 256;
  c.height = 256;
  const x = c.getContext('2d')!;
  const g = x.createRadialGradient(128, 128, 0, 128, 128, 128);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.55, 'rgba(255,255,255,0.55)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g;
  x.fillRect(0, 0, 256, 256);
  fanTex = new THREE.CanvasTexture(c);
  return fanTex;
};

const Cone: React.FC<{play: FBPlay; pt: number; o: Extract<LiveOv, {type: 'cone'}>}> = ({play, pt, o}) => {
  const st = o.player ? playerAt(play, o.player, pt) : null;
  const c: V2 = st ? st.pos : o.p!;
  let ang: number;
  if (o.dir === 'heading') ang = st!.heading;
  else {
    const q: V2 = typeof o.dir === 'string' ? playerAt(play, o.dir, pt).pos : o.dir;
    ang = Math.atan2(q[1] - c[1], q[0] - c[0]);
  }
  const grow = smooth(o.age / 0.45);
  // world angle -> three: the ground circle lies in x/z with z = -y, rotated -90 deg about x
  return (
    <mesh position={W3([c[0], c[1], H - 0.008])} rotation={[-Math.PI / 2, 0, 0]} renderOrder={3} scale={[o.len * grow, o.len * grow, 1]}>
      <circleGeometry args={[1, 48, ang - o.half, 2 * o.half]} />
      <meshBasicMaterial color={o.color ?? WHITE} alphaMap={fanTexture()} transparent opacity={(o.opacity ?? 0.34) * fade(o)} depthWrite={false} toneMapped={false} side={THREE.DoubleSide} />
    </mesh>
  );
};

export const Overlays3D: React.FC<{play: FBPlay; pt: number; items: LiveOv[]; v2?: boolean}> = ({play, pt, items, v2}) => (
  <group>
    {items.map((o, i) => {
      switch (o.type) {
        case 'pass':
          return <PassLine key={i} play={play} pt={pt} o={o} v2={v2} />;
        case 'run':
          return <Run key={i} play={play} o={o} v2={v2} pt={pt} />;
        case 'zone':
          return <Zone key={i} play={play} pt={pt} o={o} v2={v2} />;
        case 'defline':
          return <DefLine key={i} play={play} pt={pt} o={o} />;
        case 'offside':
          return <Offside key={i} play={play} o={o} />;
        case 'ring':
          return <Ring key={i} play={play} pt={pt} o={o} v2={v2} />;
        case 'circle':
          return <Circle key={i} o={o} />;
        case 'arrow':
          return <Arrow key={i} o={o} v2={v2} />;
        case 'link':
          return <Link key={i} play={play} pt={pt} o={o} />;
        case 'cone':
          return <Cone key={i} play={play} pt={pt} o={o} />;
        default:
          return null;
      }
    })}
  </group>
);

export {RED};
