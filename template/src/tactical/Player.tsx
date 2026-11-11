// PlayerAvatar and BallSprite: depth-scaled 2.5D billboards on the projected floor.
// Standing figures for court-level cameras, floor tokens for top-down cameras (cross-faded by how
// upright the figure projects), soft contact shadow, facing wedge and an always-readable ID badge.
import React from 'react';
import {BODY, DISPLAY, GOLD, NAVY} from '../pro/brand';
import type {Projector, V3} from './geometry.ts';
import {floorCircle, polyPath} from './geometry.ts';
import type {PlayerState} from './play.ts';

export const TEAM = {
  O: {jersey: NAVY, jersey2: '#1B3566', trim: GOLD, number: GOLD, ring: GOLD, badgeBg: NAVY, badgeFg: GOLD},
  X: {jersey: '#F3F4F6', jersey2: '#C9CED8', trim: '#E4572E', number: '#C8361B', ring: '#F2545B', badgeBg: '#FFFFFF', badgeFg: '#C8361B'},
};
const SKIN = '#6C7486'; // neutral mannequin tone: no faces, no identities
const SKIN_LIGHT = '#8E97AA';
const H = 1.95;

export type PlayerLook = {dim?: number; highlight?: boolean; ghost?: boolean; label?: boolean};

export const uprightness = (pr: Projector, p: PlayerState) => {
  const f = pr.p([p.pos[0], p.pos[1], 0]);
  const h = pr.p([p.pos[0], p.pos[1], H]);
  return Math.min(1, Math.hypot(h.x - f.x, h.y - f.y) / (H * f.s));
};

export const PlayerShadow: React.FC<{pr: Projector; p: PlayerState}> = ({pr, p}) => {
  const d = polyPath(
    pr,
    Array.from({length: 20}, (_, i) => {
      const a = (i / 20) * 2 * Math.PI;
      return [p.pos[0] + 0.12 + 0.48 * Math.cos(a), p.pos[1] - 0.18 + 0.36 * Math.sin(a), 0.003] as V3;
    }),
  );
  return d ? <path d={d} fill="rgba(5,10,25,0.38)" /> : null;
};

const Figure: React.FC<{p: PlayerState; team: 'O' | 'X'; ph: number; moving: number}> = ({p, team, ph, moving}) => {
  const c = TEAM[team];
  const sw = Math.sin(ph) * moving; // -1..1 stride phase
  const def = team === 'X' && moving < 0.45; // defensive stance: lower, wider, active hands
  const cr = def ? 0.1 : moving * 0.04; // crouch
  const hip = -1.0 + cr;
  const shY = -1.56 + cr;
  const leg = (s: number) => {
    const k = s * sw; // this leg's swing
    const lift = Math.max(0, -k) * 0.12; // the back leg lifts its foot
    const hipX = s * 0.085;
    const kneeX = s * (def ? 0.2 : 0.1) + k * 0.16;
    const kneeY = -0.52 + cr * 0.6 - Math.max(0, k) * 0.05;
    const footX = s * (def ? 0.27 : 0.11) + k * 0.3;
    const footY = -0.07 - lift;
    return {hipX, kneeX, kneeY, footX, footY};
  };
  const arm = (s: number) => {
    const k = -s * sw;
    const out = def ? 0.22 : 0.03;
    const elbX = s * (0.3 + out * 0.6) + k * 0.06;
    const elbY = shY + 0.33 - (def ? 0.06 : 0);
    const handX = s * (0.3 + out) + k * 0.16;
    const handY = def ? shY + 0.42 : shY + 0.62 - Math.abs(k) * 0.08;
    return {elbX, elbY, handX, handY};
  };
  const legs = [-1, 1].map((s) => ({s, ...leg(s)}));
  const arms = [-1, 1].map((s) => ({s, ...arm(s)}));
  return (
    <g strokeLinecap="round" strokeLinejoin="round">
      {legs.map((l) => (
        <g key={l.s}>
          <path d={`M${l.hipX} ${hip + 0.1} L${l.kneeX} ${l.kneeY}`} stroke={SKIN} strokeWidth={0.13} />
          <path d={`M${l.kneeX} ${l.kneeY} L${l.footX} ${l.footY - 0.04}`} stroke={SKIN} strokeWidth={0.095} />
          <path d={`M${l.kneeX + (l.footX - l.kneeX) * 0.72} ${l.kneeY + (l.footY - l.kneeY) * 0.72} L${l.footX} ${l.footY - 0.05}`} stroke="#E9EDF3" strokeWidth={0.1} />
          <ellipse cx={l.footX + 0.02 * l.s} cy={l.footY} rx={0.11} ry={0.055} fill={team === 'O' ? '#0A1328' : '#1C1C22'} stroke={c.trim} strokeWidth={0.02} />
        </g>
      ))}
      {/* shorts */}
      <path d={`M-0.2 ${hip - 0.05} L0.2 ${hip - 0.05} L0.25 ${hip + 0.4} L0.04 ${hip + 0.42} L0 ${hip + 0.26} L-0.04 ${hip + 0.42} L-0.25 ${hip + 0.4} Z`} fill={c.jersey} />
      <path d={`M-0.22 ${hip} L-0.25 ${hip + 0.4} M0.22 ${hip} L0.25 ${hip + 0.4}`} stroke={c.trim} strokeWidth={0.035} />
      {/* arms behind the torso edges */}
      {arms.map((a) => (
        <g key={a.s}>
          <path d={`M${a.s * 0.23} ${shY + 0.06} L${a.elbX} ${a.elbY}`} stroke={SKIN} strokeWidth={0.1} />
          <path d={`M${a.elbX} ${a.elbY} L${a.handX} ${a.handY}`} stroke={SKIN} strokeWidth={0.08} />
          <circle cx={a.handX} cy={a.handY + 0.03} r={0.05} fill={SKIN_LIGHT} />
        </g>
      ))}
      {/* sleeveless jersey: broad shoulders tapering to the waist, lit from the top left */}
      <path
        d={`M-0.17 ${shY - 0.05} Q-0.08 ${shY + 0.06} 0 ${shY + 0.07} Q0.08 ${shY + 0.06} 0.17 ${shY - 0.05} L0.22 ${shY + 0.02} Q0.17 ${shY + 0.16} 0.19 ${shY + 0.3} L0.18 ${hip + 0.02} L-0.18 ${hip + 0.02} L-0.19 ${shY + 0.3} Q-0.17 ${shY + 0.16} -0.22 ${shY + 0.02} Z`}
        fill={`url(#jersey-${team})`}
        stroke={c.trim}
        strokeWidth={0.028}
      />
      <text x={0} y={shY + 0.36} fontSize={0.25} textAnchor="middle" fontFamily={DISPLAY} fill={c.number}>
        {p.spec.id.slice(1)}
      </text>
      {/* neck and head: no face, no identity */}
      <path d={`M0 ${shY + 0.02} L0 ${shY - 0.12}`} stroke={SKIN} strokeWidth={0.09} />
      <ellipse cx={0} cy={shY - 0.24} rx={0.095} ry={0.115} fill="url(#skin)" />
    </g>
  );
};

export const PlayerDefs: React.FC = () => (
  <defs>
    <linearGradient id="jersey-O" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stopColor={TEAM.O.jersey2} />
      <stop offset="1" stopColor={TEAM.O.jersey} />
    </linearGradient>
    <linearGradient id="jersey-X" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stopColor="#FFFFFF" />
      <stop offset="1" stopColor={TEAM.X.jersey2} />
    </linearGradient>
    <radialGradient id="skin" cx="0.35" cy="0.3" r="0.8">
      <stop offset="0" stopColor={SKIN_LIGHT} />
      <stop offset="1" stopColor={SKIN} />
    </radialGradient>
    <radialGradient id="ballGrad" cx="0.35" cy="0.3" r="0.75">
      <stop offset="0" stopColor="#FFB869" />
      <stop offset="0.6" stopColor="#F28C28" />
      <stop offset="1" stopColor="#B4560F" />
    </radialGradient>
  </defs>
);

/** Floor ring + facing wedge (always), standing figure (court level) or token (top-down), badge. */
export const PlayerAvatar: React.FC<{pr: Projector; p: PlayerState; look?: PlayerLook; badgeMin?: number}> = ({pr, p, look = {}, badgeMin = 26}) => {
  const team = p.spec.team;
  const c = TEAM[team];
  const foot = pr.p([p.pos[0], p.pos[1], 0]);
  if (foot.z <= 0.3) return null;
  const head = pr.p([p.pos[0], p.pos[1], H]);
  const up = uprightness(pr, p);
  const figA = Math.max(0, Math.min(1, (up - 0.25) / 0.25));
  const opacity = (look.ghost ? 0.35 : 1) * (1 - (look.dim ?? 0) * 0.65);
  const ring = floorCircle(pr, p.pos, 0.42);
  const ringIn = floorCircle(pr, p.pos, 0.3);
  const fa = p.facing;
  const wedge = polyPath(pr, [
    [p.pos[0] + Math.cos(fa) * 0.72, p.pos[1] + Math.sin(fa) * 0.72, 0.006],
    [p.pos[0] + Math.cos(fa + 0.55) * 0.46, p.pos[1] + Math.sin(fa + 0.55) * 0.46, 0.006],
    [p.pos[0] + Math.cos(fa - 0.55) * 0.46, p.pos[1] + Math.sin(fa - 0.55) * 0.46, 0.006],
  ]);
  // figure transform: x along screen-right scaled by depth, y along the projected vertical
  const ux = (head.x - foot.x) / H;
  const uy = (head.y - foot.y) / H;
  const m = `matrix(${foot.s} 0 ${-ux} ${-uy} ${foot.x} ${foot.y})`;
  const moving = Math.min(1, p.speed / 2.5);
  const ph = p.stride * 2.4;
  const bob = Math.abs(Math.sin(ph)) * 0.03 * moving;
  const badgeY = figA > 0.5 ? head.y - Math.max(16, foot.s * 0.32) : foot.y - Math.max(30, foot.s * 0.62);
  const fs = Math.max(badgeMin, Math.min(46, foot.s * 0.36));
  const tokenR = Math.max(16, foot.s * 0.42);
  return (
    <g opacity={opacity}>
      {ring && <path d={ring} fill={team === 'O' ? 'rgba(201,162,77,0.20)' : 'rgba(242,84,91,0.16)'} stroke={c.ring} strokeWidth={Math.max(2, foot.s * 0.05)} />}
      {wedge && <path d={wedge} fill={c.ring} opacity={0.95} />}
      {look.highlight && ringIn && <path d={floorCircle(pr, p.pos, 0.7)} fill="none" stroke={c.ring} strokeWidth={Math.max(2, foot.s * 0.04)} strokeDasharray="6 5" />}
      {figA > 0 && (
        <g opacity={figA} transform={m}>
          <g transform={`translate(0 ${-bob})`}>
            <Figure p={p} team={team} ph={ph} moving={moving} />
          </g>
        </g>
      )}
      {figA < 1 && (
        <g opacity={1 - figA}>
          <circle cx={foot.x} cy={foot.y} r={tokenR} fill={c.jersey} stroke={c.trim} strokeWidth={Math.max(3, tokenR * 0.16)} />
          <text x={foot.x} y={foot.y + tokenR * 0.3} textAnchor="middle" fontFamily={DISPLAY} fontSize={tokenR * 0.86} fill={c.number} letterSpacing={0.5}>
            {p.spec.id}
          </text>
        </g>
      )}
      {look.label !== false && figA > 0.5 && (
        <g transform={`translate(${foot.x + (head.x - foot.x)} ${badgeY})`}>
          <rect x={-fs * 0.95} y={-fs * 0.62} width={fs * 1.9} height={fs * 1.12} rx={fs * 0.3} fill={c.badgeBg} stroke={c.trim} strokeWidth={2} opacity={0.95} />
          <text x={0} y={fs * 0.3} textAnchor="middle" fontFamily={BODY} fontWeight={800} fontSize={fs * 0.8} fill={c.badgeFg}>
            {p.spec.id}
          </text>
        </g>
      )}
    </g>
  );
};

export const BallSprite: React.FC<{pr: Projector; pos: V3; spin: number}> = ({pr, pos, spin}) => {
  const s = pr.p(pos);
  if (s.z <= 0.3) return null;
  const r = Math.max(5, 0.12 * s.s);
  return (
    <g>
      <circle cx={s.x} cy={s.y} r={r} fill="url(#ballGrad)" stroke="#5A2A06" strokeWidth={Math.max(1, r * 0.08)} />
      <g transform={`rotate(${spin} ${s.x} ${s.y})`} stroke="#3A1A04" strokeWidth={Math.max(0.8, r * 0.07)} fill="none" opacity={0.85}>
        <path d={`M${s.x - r} ${s.y} L${s.x + r} ${s.y}`} />
        <path d={`M${s.x} ${s.y - r} Q${s.x + r * 0.55} ${s.y} ${s.x} ${s.y + r}`} />
        <path d={`M${s.x} ${s.y - r} Q${s.x - r * 0.55} ${s.y} ${s.x} ${s.y + r}`} />
      </g>
    </g>
  );
};

export const BallShadow: React.FC<{pr: Projector; pos: V3}> = ({pr, pos}) => {
  const d = floorCircle(pr, [pos[0] + 0.05, pos[1] - 0.05], 0.13 + pos[2] * 0.04, 14);
  return d ? <path d={d} fill="rgba(5,10,25,0.4)" opacity={Math.max(0.15, 0.6 - pos[2] * 0.12)} /> : null;
};
