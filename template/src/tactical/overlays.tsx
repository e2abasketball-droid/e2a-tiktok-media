// World-space tactical graphics, projected with the same camera as the players so they stay glued to
// the floor in every view: AnimatedRoute, PlayerTracking trail, ScreenCorridor, ScreenDoors
// (collision zone), DefenderTracking (separation), PassingLaneHighlight, OpenSpace, ShotWindow,
// DefensiveSwitch, rings and labels.
import React from 'react';
import {random} from 'remotion';
import {BODY, DISPLAY, GOLD, NAVY, WHITE} from '../pro/brand';
import type {Projector, V2, V3} from './geometry.ts';
import {floorCircle, floorPath, polyPath} from './geometry.ts';
import type {Frame, Play} from './play.ts';
import {mark, posAt, routeOf} from './play.ts';
import {TEAM} from './Player';

export const ROUTE = {O: '#E9C46A', X: '#FF5A5F', pass: '#FFFFFF', casing: 'rgba(8,18,40,0.85)', open: 'rgba(255,236,170,0.55)'};

export type OvCtx = {pr: Projector; play: Play; f: Frame; pt: number; frameAt: (t: number) => Frame; id: string};

const easeOut = (x: number) => 1 - Math.pow(1 - Math.max(0, Math.min(1, x)), 3);

const toPx = (pr: Projector, pts: V2[], z = 0.01) => pts.map((q) => pr.p([q[0], q[1], z]));

const head = (a: {x: number; y: number}, b: {x: number; y: number}, size: number) => {
  const ang = Math.atan2(b.y - a.y, b.x - a.x);
  const p = (d: number) => `${b.x - size * Math.cos(ang + d)} ${b.y - size * Math.sin(ang + d)}`;
  return `M${p(0.5)} L${b.x} ${b.y} L${p(-0.5)} Z`;
};

/** A route that draws itself: up to the current play time (progressive) or over `reveal` seconds. */
export const AnimatedRoute: React.FC<{c: OvCtx; player: string; from: number; to: number; age: number; mode?: 'progressive' | 'reveal' | 'full'; tone?: 'O' | 'X'; dashed?: boolean; width?: number; opacity?: number}> = ({
  c,
  player,
  from,
  to,
  age,
  mode = 'progressive',
  tone,
  dashed,
  width = 0.16,
  opacity = 1,
}) => {
  const team = tone ?? (player.startsWith('O') ? 'O' : 'X');
  let end = to;
  if (mode === 'progressive') end = Math.min(to, Math.max(from, c.pt));
  if (mode === 'reveal') end = from + (to - from) * easeOut(age / 0.9);
  if (end - from < 0.04) return null;
  const pts = routeOf(c.play, player, from, end);
  const px = toPx(c.pr, pts).filter((s) => s.z > 0.3);
  if (px.length < 2) return null;
  const s = c.pr.p([pts[pts.length - 1][0], pts[pts.length - 1][1], 0]).s;
  const w = Math.max(4, width * s);
  const d = px.map((q, i) => `${i ? 'L' : 'M'}${q.x.toFixed(1)} ${q.y.toFixed(1)}`).join('');
  const col = ROUTE[team];
  const a = px[Math.max(0, px.length - 4)];
  const b = px[px.length - 1];
  return (
    <g opacity={opacity * Math.min(1, age / 0.15)}>
      <path d={d} fill="none" stroke={ROUTE.casing} strokeWidth={w + 5} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dashed ? `${w * 2.2} ${w * 1.6}` : undefined} />
      <path d={d} fill="none" stroke={col} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dashed ? `${w * 2.2} ${w * 1.6}` : undefined} />
      <path d={head(a, b, w * 2.6)} fill={col} stroke={ROUTE.casing} strokeWidth={2} />
      <circle cx={px[0].x} cy={px[0].y} r={w * 0.9} fill={col} stroke={ROUTE.casing} strokeWidth={2} />
    </g>
  );
};

/** Player tracking: fading trail of the last `len` seconds. */
export const Trail: React.FC<{c: OvCtx; player: string; len?: number; age: number}> = ({c, player, len = 1.2, age}) => {
  const t0 = Math.max(0, c.pt - len);
  if (c.pt - t0 < 0.05) return null;
  const pts = routeOf(c.play, player, t0, c.pt, 1 / 30);
  const px = toPx(c.pr, pts);
  const col = ROUTE[player.startsWith('O') ? 'O' : 'X'];
  const s = c.pr.p([pts[0][0], pts[0][1], 0]).s;
  return (
    <g opacity={Math.min(1, age / 0.2)}>
      {px.slice(1).map((q, i) =>
        q.z > 0.3 && px[i].z > 0.3 ? <path key={i} d={`M${px[i].x} ${px[i].y}L${q.x} ${q.y}`} stroke={col} strokeOpacity={(i / px.length) * 0.9} strokeWidth={Math.max(3, s * 0.13)} strokeLinecap="round" /> : null,
      )}
    </g>
  );
};

/** The corridor between two screeners: glowing lane while open, red bar once closed. */
export const Corridor: React.FC<{c: OvCtx; a: string; b: string; lineY: number; age: number; label?: string; extend?: [number, number]}> = ({c, a, b, lineY, age, label, extend = [2.6, 2.6]}) => {
  const pa = c.f.players[a].pos;
  const pb = c.f.players[b].pos;
  const gap = Math.abs(pb[0] - pa[0]) - 0.5;
  const x0 = Math.min(pa[0], pb[0]) + 0.25;
  const x1 = Math.max(pa[0], pb[0]) - 0.25;
  const k = easeOut(age / 0.6);
  const closed = gap < 0.2;
  const lane = polyPath(c.pr, [
    [x0, lineY - extend[0] * k, 0.008],
    [x1, lineY - extend[0] * k, 0.008],
    [x1, lineY + extend[1] * k, 0.008],
    [x0, lineY + extend[1] * k, 0.008],
  ]);
  const edgeL = floorPath(c.pr, [[x0, lineY - extend[0] * k], [x0, lineY + extend[1] * k]], false, 0.01);
  const edgeR = floorPath(c.pr, [[x1, lineY - extend[0] * k], [x1, lineY + extend[1] * k]], false, 0.01);
  const s = c.pr.p([0, lineY, 0]).s;
  const lp = c.pr.p([0, lineY + extend[1] * k + 0.5, 0]);
  return (
    <g opacity={Math.min(1, age / 0.3)}>
      {!closed && lane && <path d={lane} fill="rgba(233,196,106,0.32)" />}
      {!closed && edgeL && <path d={edgeL} stroke={GOLD} strokeWidth={Math.max(2, s * 0.05)} strokeDasharray="10 7" />}
      {!closed && edgeR && <path d={edgeR} stroke={GOLD} strokeWidth={Math.max(2, s * 0.05)} strokeDasharray="10 7" />}
      {closed && (() => {
        const d = polyPath(c.pr, [[x0 - 0.55, lineY - 0.32, 0.01], [x1 + 0.55, lineY - 0.32, 0.01], [x1 + 0.55, lineY - 0.18, 0.01], [x0 - 0.55, lineY - 0.18, 0.01]]);
        return d ? <path d={d} fill="#FF5A5F" opacity={0.9} /> : null;
      })()}
      {label && !closed && <Tag x={lp.x} y={lp.y} text={label} tone="gold" size={30} />}
    </g>
  );
};

/** Screen collision zone: door panels that slide shut; contact burst when the chaser hits them. */
export const Doors: React.FC<{c: OvCtx; a: string; b: string; lineY: number; contact?: number; age: number}> = ({c, a, b, lineY, contact, age}) => {
  const out: React.ReactNode[] = [];
  [a, b].forEach((id, i) => {
    const p = c.f.players[id].pos;
    const dir = i === 0 ? 1 : -1;
    const d = polyPath(c.pr, [
      [p[0] - 0.42, lineY - 0.5, 0.012],
      [p[0] + 0.42, lineY - 0.5, 0.012],
      [p[0] + 0.42, lineY - 0.36, 0.012],
      [p[0] - 0.42, lineY - 0.36, 0.012],
    ]);
    if (d) out.push(<path key={id} d={d} fill={GOLD} stroke={NAVY} strokeWidth={2} opacity={0.95} />);
    // slide arrow while closing
    const v = c.f.players[id].vel[0] * dir;
    if (v > 0.3) {
      const s0 = c.pr.p([p[0] + dir * 0.5, lineY - 0.43, 0.02]);
      const s1 = c.pr.p([p[0] + dir * 0.95, lineY - 0.43, 0.02]);
      out.push(<path key={`${id}a`} d={head(s0, s1, 18)} fill={WHITE} />);
    }
  });
  let burst: React.ReactNode = null;
  if (contact !== undefined && c.pt >= contact - 0.02) {
    const age2 = c.pt - contact;
    const at = c.pr.p([0, lineY - 0.55, 1.0]);
    const n = 14;
    burst = (
      <g>
        {Array.from({length: n}, (_, i) => {
          const ang = (i / n) * Math.PI * 2 + random(`b${i}`) * 0.4;
          const sp = 40 + random(`s${i}`) * 90;
          const r = Math.max(0, Math.min(1, age2 * 4 + 0.6));
          const o = Math.max(0, 1 - age2 * 2.2);
          return <circle key={i} cx={at.x + Math.cos(ang) * sp * r} cy={at.y + Math.sin(ang) * sp * r * 0.6} r={3 + random(`r${i}`) * 3} fill={i % 2 ? GOLD : WHITE} opacity={o} />;
        })}
        <circle cx={at.x} cy={at.y} r={30 + Math.max(0, age2) * 160} fill="none" stroke="#FF5A5F" strokeWidth={4} opacity={Math.max(0, 0.9 - age2 * 2.5)} />
      </g>
    );
  }
  return <g opacity={Math.min(1, age / 0.25)}>{out}{burst}</g>;
};

/** Defender tracking: bracket between the attacker and his defender, labelled (no invented numbers). */
export const Separation: React.FC<{c: OvCtx; a: string; b: string; label?: string; age: number}> = ({c, a, b, label = 'SEPARATION', age}) => {
  const pa = c.f.players[a].pos;
  const pb = c.f.players[b].pos;
  const k = easeOut(age / 0.5);
  const mid: V2 = [pa[0] + (pb[0] - pa[0]) * 0.5, pa[1] + (pb[1] - pa[1]) * 0.5];
  const A: V2 = [mid[0] + (pa[0] - mid[0]) * k, mid[1] + (pa[1] - mid[1]) * k];
  const B: V2 = [mid[0] + (pb[0] - mid[0]) * k, mid[1] + (pb[1] - mid[1]) * k];
  const sa = c.pr.p([A[0], A[1], 0.02]);
  const sb = c.pr.p([B[0], B[1], 0.02]);
  const sm = c.pr.p([mid[0], mid[1], 0.02]);
  const nx = -(sb.y - sa.y);
  const ny = sb.x - sa.x;
  const L = Math.hypot(nx, ny) || 1;
  const t = 16;
  return (
    <g>
      <path d={`M${sa.x} ${sa.y}L${sb.x} ${sb.y}`} stroke={NAVY} strokeWidth={9} strokeLinecap="round" />
      <path d={`M${sa.x} ${sa.y}L${sb.x} ${sb.y}`} stroke={WHITE} strokeWidth={4} strokeDasharray="12 8" strokeLinecap="round" />
      {[sa, sb].map((q, i) => (
        <path key={i} d={`M${q.x + (nx / L) * t} ${q.y + (ny / L) * t}L${q.x - (nx / L) * t} ${q.y - (ny / L) * t}`} stroke={WHITE} strokeWidth={5} strokeLinecap="round" />
      ))}
      {age > 0.35 && <Tag x={sm.x - (nx / L) * 120} y={sm.y - (ny / L) * 120} text={label} tone="white" size={28} />}
    </g>
  );
};

/** Passing lane: a glowing corridor from the passer to where the receiver will catch it. */
export const PassLane: React.FC<{c: OvCtx; from: string; to: string; at: number; age: number; label?: string; width?: number}> = ({c, from, to, at, age, label, width = 0.9}) => {
  const a = c.f.players[from].pos;
  const b = posAt(c.play.tracks[to], at);
  const k = easeOut(age / 0.6);
  const e: V2 = [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k];
  const dx = e[0] - a[0];
  const dy = e[1] - a[1];
  const L = Math.hypot(dx, dy) || 1;
  const nx = (-dy / L) * width * 0.5;
  const ny = (dx / L) * width * 0.5;
  const lane = polyPath(c.pr, [
    [a[0] + nx, a[1] + ny, 0.015],
    [e[0] + nx * 0.6, e[1] + ny * 0.6, 0.015],
    [e[0] - nx * 0.6, e[1] - ny * 0.6, 0.015],
    [a[0] - nx, a[1] - ny, 0.015],
  ]);
  const center = floorPath(c.pr, [a, e], false, 0.02);
  const sm = c.pr.p([(a[0] + e[0]) / 2, (a[1] + e[1]) / 2, 0]);
  return (
    <g opacity={Math.min(1, age / 0.2)}>
      {lane && <path d={lane} fill="rgba(255,255,255,0.22)" stroke="rgba(255,255,255,0.75)" strokeWidth={2} />}
      {center && <path d={center} stroke="#F28C28" strokeWidth={5} strokeDasharray="3 12" strokeLinecap="round" />}
      {label && age > 0.4 && <Tag x={sm.x} y={sm.y + 46} text={label} tone="white" size={28} />}
    </g>
  );
};

/** Soft highlight of free space on the floor. */
export const OpenSpace: React.FC<{c: OvCtx; at: V2; r: number; age: number; label?: string; tone?: 'gold' | 'white'}> = ({c, at, r, age, label, tone = 'gold'}) => {
  const k = easeOut(age / 0.7);
  const pulse = 1 + Math.sin(age * 5) * 0.03;
  const rings = [1, 0.7, 0.42].map((m) => floorCircle(c.pr, at, r * m * k * pulse, 40, 0.009));
  const lp = c.pr.p([at[0], at[1], 0]);
  const col = tone === 'gold' ? '255,226,150' : '255,255,255';
  return (
    <g>
      {rings.map((d, i) => (d ? <path key={i} d={d} fill={`rgba(${col},${0.13 + i * 0.07})`} /> : null))}
      {rings[0] && <path d={rings[0]} fill="none" stroke={`rgba(${col},0.9)`} strokeWidth={3} strokeDasharray="10 8" />}
      {label && age > 0.3 && <Tag x={lp.x} y={lp.y} text={label} tone={tone} size={32} />}
    </g>
  );
};

/** Shot opportunity: a ring around the shooter whose arc shrinks as the closest defender closes in. */
export const ShotWindow: React.FC<{c: OvCtx; player: string; age: number; label?: string}> = ({c, player, age, label = 'OPEN LOOK'}) => {
  const p = c.f.players[player].pos;
  const near = Math.min(...Object.values(c.f.players).filter((q) => q.spec.team === 'X').map((q) => Math.hypot(q.pos[0] - p[0], q.pos[1] - p[1])));
  const frac = Math.max(0, Math.min(1, (near - 0.8) / 2.2));
  const s = c.pr.p([p[0], p[1], 0]);
  const R = Math.max(40, s.s * 1.1) * easeOut(age / 0.4);
  const a1 = -Math.PI / 2 + frac * Math.PI * 2;
  const large = frac > 0.5 ? 1 : 0;
  const col = frac > 0.45 ? '#7BE0A8' : '#FFB347';
  return (
    <g>
      <circle cx={s.x} cy={s.y - R * 0.15} r={R} fill="none" stroke="rgba(255,255,255,0.25)" strokeWidth={8} />
      {frac > 0.01 && (
        <path d={`M${s.x} ${s.y - R * 0.15 - R} A${R} ${R} 0 ${large} 1 ${s.x + R * Math.cos(a1)} ${s.y - R * 0.15 + R * Math.sin(a1)}`} fill="none" stroke={col} strokeWidth={8} strokeLinecap="round" />
      )}
      {age > 0.3 && <Tag x={s.x + R * 1.1} y={c.pr.p([p[0], p[1], 2.25]).y} text={frac > 0.45 ? label : 'WINDOW CLOSING'} tone={frac > 0.45 ? 'mint' : 'amber'} size={30} />}
    </g>
  );
};

/** Defensive switch: curved red arrow from a defender to the man he jumps to. */
export const SwitchArrow: React.FC<{c: OvCtx; from: string; toPoint: V2; age: number; label?: string}> = ({c, from, toPoint, age, label = 'EARLY SWITCH'}) => {
  const a = c.f.players[from].pos;
  const k = easeOut(age / 0.7);
  const mid: V2 = [(a[0] + toPoint[0]) / 2 + 1.0, (a[1] + toPoint[1]) / 2];
  const pts: V2[] = [];
  for (let i = 0; i <= 20 * k; i++) {
    const u = i / 20;
    pts.push([
      (1 - u) * (1 - u) * a[0] + 2 * (1 - u) * u * mid[0] + u * u * toPoint[0],
      (1 - u) * (1 - u) * a[1] + 2 * (1 - u) * u * mid[1] + u * u * toPoint[1],
    ]);
  }
  if (pts.length < 2) return null;
  const px = toPx(c.pr, pts, 0.02);
  const d = px.map((q, i) => `${i ? 'L' : 'M'}${q.x} ${q.y}`).join('');
  const s = c.pr.p([a[0], a[1], 0]).s;
  const w = Math.max(5, s * 0.14);
  const lp = px[Math.floor(px.length / 2)];
  return (
    <g>
      <path d={d} fill="none" stroke={ROUTE.casing} strokeWidth={w + 5} strokeDasharray={`${w * 2} ${w * 1.4}`} />
      <path d={d} fill="none" stroke={ROUTE.X} strokeWidth={w} strokeDasharray={`${w * 2} ${w * 1.4}`} />
      <path d={head(px[px.length - 3] ?? px[0], px[px.length - 1], w * 2.6)} fill={ROUTE.X} />
      {age > 0.5 && <Tag x={lp.x + 60} y={lp.y} text={label} tone="red" size={30} />}
    </g>
  );
};

export const Ring: React.FC<{c: OvCtx; player: string; age: number; label?: string; tone?: 'gold' | 'red' | 'white'}> = ({c, player, age, label, tone}) => {
  const p = c.f.players[player];
  const team = p.spec.team;
  const col = tone === 'gold' ? GOLD : tone === 'red' ? '#FF5A5F' : tone === 'white' ? WHITE : TEAM[team].ring;
  const k = easeOut(age / 0.4);
  const pulse = 0.85 + 0.15 * Math.sin(age * 7);
  const d = floorCircle(c.pr, p.pos, 0.95 * k + 0.05, 36, 0.02);
  const s = c.pr.p([p.pos[0], p.pos[1], 0]);
  const top = c.pr.p([p.pos[0], p.pos[1], 2.3]);
  return (
    <g>
      {d && <path d={d} fill="none" stroke={col} strokeWidth={Math.max(4, s.s * 0.08)} opacity={pulse} />}
      {label && age > 0.25 && <Tag x={top.x} y={Math.min(top.y, s.y - 70) - 40} text={label} tone={tone === 'red' ? 'red' : tone === 'white' ? 'white' : team === 'O' ? 'gold' : 'red'} size={30} />}
    </g>
  );
};

/** where tags may sit inside the current viewport (keeps labels on screen and above the subtitles) */
export const TagBounds = React.createContext({x0: 70, x1: 1010, y0: 250, y1: 1290, scale: 1});

export const Tag: React.FC<{x: number; y: number; text: string; tone?: 'gold' | 'white' | 'red' | 'mint' | 'amber'; size?: number}> = ({x, y, text, tone = 'gold', size: size0 = 30}) => {
  const B = React.useContext(TagBounds);
  const size = size0 * B.scale;
  const bg = {gold: GOLD, white: WHITE, red: '#E4434A', mint: '#7BE0A8', amber: '#FFB347'}[tone];
  const fg = tone === 'red' ? WHITE : NAVY;
  const w = text.length * size * 0.62 + size * 1.1;
  const cx = Math.max(B.x0 + w / 2, Math.min(B.x1 - w / 2, x));
  const cy = Math.max(B.y0, Math.min(B.y1, y));
  return (
    <g transform={`translate(${cx} ${cy})`}>
      <rect x={-w / 2} y={-size * 0.82} width={w} height={size * 1.42} rx={size * 0.28} fill={bg} stroke={NAVY} strokeWidth={3} />
      <text x={0} y={size * 0.25} textAnchor="middle" fontFamily={BODY} fontWeight={900} fontSize={size} fill={fg} letterSpacing={1.5}>
        {text}
      </text>
    </g>
  );
};

/** A label pinned to a world point. */
export const WorldLabel: React.FC<{c: OvCtx; at: V3; text: string; tone?: 'gold' | 'white' | 'red' | 'mint'; size?: number}> = ({c, at, text, tone, size}) => {
  const s = c.pr.p(at);
  if (s.z <= 0.3) return null;
  return <Tag x={s.x} y={s.y} text={text} tone={tone} size={size} />;
};

export const resolveT = (play: Play, v: unknown): number => (typeof v === 'string' ? mark(play, v) : (v as number));
export {DISPLAY};
