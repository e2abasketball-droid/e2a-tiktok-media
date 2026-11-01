import React from 'react';
import './theme';
import {AbsoluteFill, Audio, Easing, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

export const NAVY = '#0B1C3D';
export const NAVY2 = '#14305F';
export const GOLD = '#C9A24D';
export const GOLD_D = '#A9842F';
export const WHITE = '#FFFFFF';
export const MUTED = 'rgba(255,255,255,0.65)';
export const BALL = '#E8833A';
export const RED = '#E4572E';
const DISPLAY = 'Anton, Impact, sans-serif';
const BODY = 'Inter, Arial, sans-serif';

export type Word = {text: string; start: number; end: number};
export type Pt = [number, number];
export const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, '');

/** time (s) at which a phrase starts in the narration */
export const makeT = (words: Word[]) => (phrase: string, off = 0, occurrence = 0): number => {
  const p = phrase.split(/\s+/).map(norm).filter(Boolean);
  let seen = 0;
  for (let i = 0; i + p.length <= words.length; i++) {
    if (p.every((w, k) => norm(words[i + k].text) === w)) {
      if (seen === occurrence) return words[i].start + off;
      seen++;
    }
  }
  throw new Error('phrase not found: ' + phrase);
};

// ------------------------------------------------------------------ court
export type Track = {id: string; side: 'O' | 'X'; kf: [number, number, number][]};
const ease = Easing.inOut(Easing.cubic);
export const posAt = (kf: [number, number, number][], t: number): Pt => {
  if (t <= kf[0][0]) return [kf[0][1], kf[0][2]];
  for (let i = 1; i < kf.length; i++) {
    if (t <= kf[i][0]) {
      const [t0, x0, y0] = kf[i - 1];
      const [t1, x1, y1] = kf[i];
      const k = t1 === t0 ? 1 : ease((t - t0) / (t1 - t0));
      return [x0 + (x1 - x0) * k, y0 + (y1 - y0) * k];
    }
  }
  const l = kf[kf.length - 1];
  return [l[1], l[2]];
};

export type Arrow = {t: number; until?: number; pts: Pt[]; kind: 'move' | 'pass' | 'screen' | 'shot' | 'chase'};
export type Ring = {t: number; until: number; at: string | Pt; text?: string; color?: string; dy?: number};
export type Zone = {t: number; until: number; cx: number; cy: number; rx: number; ry: number; text?: string; color?: string};
export type CourtSpec = {
  title: string;
  tracks: Track[];
  ball: [number, number, number][];
  arrows: Arrow[];
  rings: Ring[];
  zones: Zone[];
  steps: [number, string][];
};

export const OffCtx = React.createContext(0);
export const useAbsT = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return frame / fps + React.useContext(OffCtx);
};

const S = 960 / 46; // px per foot

const CourtLines: React.FC = () => (
  <g fill="none" stroke="rgba(255,255,255,0.75)" strokeWidth={0.28}>
    <rect x={0} y={0} width={50} height={47} />
    <rect x={17} y={0} width={16} height={19} fill="rgba(201,162,77,0.14)" />
    <path d="M19 19 A6 6 0 0 0 31 19" />
    <path d="M19 19 A6 6 0 0 1 31 19" strokeDasharray="1 1" />
    <path d="M21 5.25 A4 4 0 0 0 29 5.25" />
    <line x1={22} y1={4} x2={28} y2={4} strokeWidth={0.5} />
    <circle cx={25} cy={5.25} r={0.75} stroke={BALL} strokeWidth={0.35} />
    <path d="M3 0 V14.2 A23.75 23.75 0 1 0 47 14.2 V0" />
    <path d="M19 47 A6 6 0 0 1 31 47" />
  </g>
);

const arrowHead = (a: Pt, b: Pt, size = 1.5) => {
  const ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
  const p = (d: number): Pt => [b[0] - size * Math.cos(ang + d), b[1] - size * Math.sin(ang + d)];
  const l = p(0.45);
  const r = p(-0.45);
  return `M${l[0]} ${l[1]} L${b[0]} ${b[1]} L${r[0]} ${r[1]}`;
};

const pathOf = (pts: Pt[]) => 'M' + pts.map((p) => `${p[0]} ${p[1]}`).join(' L');

export const Court: React.FC<{spec: CourtSpec}> = ({spec}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const cur: Record<string, Pt> = {};
  spec.tracks.forEach((tr) => (cur[tr.id] = posAt(tr.kf, t)));
  const ball = posAt(spec.ball, t);
  const step = [...spec.steps].reverse().find((s) => t >= s[0]);
  const stepAge = step ? t - step[0] : 0;
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', top: 232, left: 0, right: 0, textAlign: 'center', fontFamily: DISPLAY, fontSize: 70, color: GOLD, letterSpacing: 3}}>
        {spec.title}
      </div>
      <svg viewBox="2 0 46 38.5" width={960} height={38.5 * S} style={{position: 'absolute', left: 60, top: 330, background: NAVY2, borderRadius: 14}}>
        <CourtLines />
        {spec.zones.map((z, i) => {
          if (t < z.t || t > z.until) return null;
          const o = Math.min(1, (t - z.t) / 0.4, (z.until - t) / 0.4);
          return (
            <g key={i} opacity={o}>
              <ellipse cx={z.cx} cy={z.cy} rx={z.rx} ry={z.ry} fill={z.color ?? 'rgba(201,162,77,0.25)'} stroke={GOLD} strokeWidth={0.25} strokeDasharray="1 0.8" />
              {z.text && (
                <text x={z.cx} y={z.cy + 0.9} fontSize={2.3} fontWeight={900} fill={WHITE} textAnchor="middle" fontFamily={BODY}>
                  {z.text}
                </text>
              )}
            </g>
          );
        })}
        {spec.arrows.map((a, i) => {
          if (t < a.t || (a.until !== undefined && t > a.until)) return null;
          const p = Math.min(1, (t - a.t) / 0.5);
          const fade = a.until !== undefined ? Math.min(1, (a.until - t) / 0.3) : 1;
          const col = a.kind === 'pass' ? WHITE : a.kind === 'shot' ? BALL : a.kind === 'chase' ? 'rgba(255,255,255,0.8)' : GOLD;
          const dash = a.kind === 'pass' || a.kind === 'shot' || a.kind === 'chase';
          const last = a.pts[a.pts.length - 1];
          const prev = a.pts[a.pts.length - 2];
          const perp = (() => {
            const ang = Math.atan2(last[1] - prev[1], last[0] - prev[0]) + Math.PI / 2;
            return [Math.cos(ang) * 1.6, Math.sin(ang) * 1.6];
          })();
          return (
            <g key={i} opacity={fade}>
              <path d={pathOf(a.pts)} pathLength={1} fill="none" stroke={col} strokeWidth={0.4} strokeLinecap="round"
                strokeDasharray={dash ? undefined : `${p} 1`} opacity={dash ? p : 1} {...(dash ? {style: {strokeDasharray: '0.04 0.025'}} : {})} />
              {p > 0.9 && a.kind !== 'screen' && <path d={arrowHead(prev, last)} fill="none" stroke={col} strokeWidth={0.4} strokeLinecap="round" />}
              {p > 0.9 && a.kind === 'screen' && <line x1={last[0] - perp[0]} y1={last[1] - perp[1]} x2={last[0] + perp[0]} y2={last[1] + perp[1]} stroke={col} strokeWidth={0.6} strokeLinecap="round" />}
            </g>
          );
        })}
        {spec.tracks.map((tr) => {
          const [x, y] = cur[tr.id];
          const off = tr.side === 'O';
          return (
            <g key={tr.id} transform={`translate(${x} ${y})`}>
              <circle r={1.75} fill={off ? GOLD : NAVY} stroke={off ? GOLD_D : WHITE} strokeWidth={0.4} />
              <text y={0.9} fontSize={2.0} fontWeight={900} textAnchor="middle" fill={off ? NAVY : WHITE} fontFamily={BODY}>{tr.id}</text>
            </g>
          );
        })}
        {spec.rings.map((r, i) => {
          if (t < r.t || t > r.until) return null;
          const at = typeof r.at === 'string' ? cur[r.at] : r.at;
          const o = Math.min(1, (t - r.t) / 0.25, (r.until - t) / 0.25);
          const pulse = 3.4 + Math.sin(t * 8) * 0.35;
          return (
            <g key={i} opacity={o}>
              <circle cx={at[0]} cy={at[1]} r={pulse} fill="none" stroke={r.color ?? GOLD} strokeWidth={0.45} />
              {r.text && (
                <g transform={`translate(${at[0]} ${at[1] + (r.dy ?? -5.2)})`}>
                  <rect x={-r.text.length * 0.78 - 0.8} y={-1.7} width={r.text.length * 1.56 + 1.6} height={2.9} rx={1.4} fill={r.color ?? GOLD} />
                  <text x={0} y={0.5} fontSize={1.9} fontWeight={900} fill={NAVY} textAnchor="middle" fontFamily={BODY}>{r.text}</text>
                </g>
              )}
            </g>
          );
        })}
        <g transform={`translate(${ball[0] + 1.9} ${ball[1] - 1.9})`}>
          <circle r={1} fill={BALL} stroke="#7A3B10" strokeWidth={0.2} />
          <path d="M-1 0 H1 M0 -1 V1" stroke="#7A3B10" strokeWidth={0.15} />
        </g>
      </svg>
      {step && (
        <div style={{position: 'absolute', top: 1185, left: 60, right: 60, textAlign: 'center', fontFamily: BODY, fontWeight: 800, fontSize: 44, color: WHITE, letterSpacing: 2, textTransform: 'uppercase', opacity: Math.min(1, stepAge / 0.3)}}>
          {step[1]}
        </div>
      )}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------ card scenes
const usePop = (delay = 0) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: frame - delay * fps, fps, config: {damping: 14, mass: 0.6}});
};

const Pop: React.FC<{at?: number; children: React.ReactNode}> = ({at = 0, children}) => {
  const s = usePop(at);
  return <div style={{transform: `scale(${interpolate(s, [0, 1], [0.6, 1])}) translateY(${interpolate(s, [0, 1], [40, 0])}px)`, opacity: s}}>{children}</div>;
};

export const Big: React.FC<{children: React.ReactNode; size?: number; color?: string}> = ({children, size = 150, color = WHITE}) => (
  <div style={{fontFamily: DISPLAY, fontSize: size, lineHeight: 1.02, color, textAlign: 'center', textTransform: 'uppercase', letterSpacing: 2}}>{children}</div>
);
export const Tag: React.FC<{children: React.ReactNode; color?: string; size?: number}> = ({children, color = GOLD, size = 42}) => (
  <div style={{fontFamily: BODY, fontWeight: 800, fontSize: size, color, letterSpacing: 7, textTransform: 'uppercase', textAlign: 'center'}}>{children}</div>
);

export const Stage: React.FC<{children: React.ReactNode}> = ({children}) => (
  <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', paddingTop: 140, paddingBottom: 480, gap: 34, flexDirection: 'column'}}>{children}</AbsoluteFill>
);

/** count-up number */
export const Count: React.FC<{to: number; from?: number; start: number; dur?: number; size?: number; color?: string; dec?: number}> = ({to, from = 0, start, dur = 1.2, size = 260, color = GOLD, dec = 0}) => {
  const t = useAbsT();
  const k = interpolate(t, [start, start + dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const v = from + (to - from) * k;
  return <div style={{fontFamily: DISPLAY, fontSize: size, color, lineHeight: 1, opacity: t >= start - 0.05 ? 1 : 0}}>{v.toFixed(dec)}</div>;
};

/** scoreboard with time-keyed scores */
export const Board: React.FC<{
  rows: {name: string; kf: [number, number][]; color?: string}[];
  clock?: [number, number, number]; // [t0, t1, startValue] counts to 0
  label?: string;
}> = ({rows, clock, label}) => {
  const t = useAbsT();
  const score = (kf: [number, number][]) => {
    let v = kf[0][1];
    kf.forEach(([tt, vv]) => { if (t >= tt) v = vv; });
    return v;
  };
  const clk = clock ? Math.max(0, clock[2] * (1 - (t - clock[0]) / (clock[1] - clock[0]))) : null;
  return (
    <div style={{width: 900, background: 'rgba(0,0,0,0.35)', border: `4px solid ${GOLD}`, borderRadius: 28, padding: '34px 44px', display: 'flex', flexDirection: 'column', gap: 18}}>
      {label && <Tag size={34}>{label}</Tag>}
      {rows.map((r, i) => {
        const v = score(r.kf);
        const prev = r.kf.filter(([tt]) => t >= tt).length;
        const lastT = prev > 1 ? r.kf[prev - 1][0] : -9;
        const bump = 1 + Math.max(0, 0.22 - (t - lastT)) * 1.6;
        return (
          <div key={i} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div style={{fontFamily: DISPLAY, fontSize: 84, color: r.color ?? WHITE, letterSpacing: 3}}>{r.name}</div>
            <div style={{fontFamily: DISPLAY, fontSize: 150, color: r.color ?? GOLD, transform: `scale(${bump})`}}>{v}</div>
          </div>
        );
      })}
      {clk !== null && (
        <div style={{textAlign: 'center', fontFamily: DISPLAY, fontSize: 90, color: clk > 0 ? RED : MUTED}}>{clk.toFixed(1)}s</div>
      )}
    </div>
  );
};

export const Popup: React.FC<{at: number; dur?: number; text: string; color?: string}> = ({at, dur = 1.3, text, color = GOLD}) => {
  const {fps} = useVideoConfig();
  const t = useAbsT() - at;
  if (t < 0 || t > dur) return null;
  const s = spring({frame: t * fps, fps, config: {damping: 12, mass: 0.5}});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 360 + 0, textAlign: 'center', fontFamily: DISPLAY, fontSize: 130, color, opacity: Math.min(1, (dur - t) / 0.3) * s, transform: `scale(${0.7 + 0.3 * s})`, textShadow: '0 6px 20px rgba(0,0,0,0.6)'}}>
      {text}
    </div>
  );
};

// -------------------------------------------------------------- captions
const chunkWords = (ws: Word[]) => {
  const chunks: Word[][] = [];
  let cur: Word[] = [];
  const chars = (c: Word[]) => c.reduce((n, x) => n + x.text.length + 1, 0);
  ws.forEach((w, i) => {
    if (cur.length && chars(cur) + w.text.length > 20) { chunks.push(cur); cur = []; }
    cur.push(w);
    const next = ws[i + 1];
    const endsSentence = /[.,?!:]$/.test(w.text);
    const gap = next ? next.start - w.end > 0.45 : true;
    if (cur.length >= 4 || endsSentence || gap) { chunks.push(cur); cur = []; }
  });
  if (cur.length) chunks.push(cur);
  return chunks;
};

export const Captions: React.FC<{words: Word[]; top?: number}> = ({words, top = 1390}) => {
  const chunks = React.useMemo(() => chunkWords(words), [words]);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const idx = chunks.findIndex((c, i) => {
    const nextStart = chunks[i + 1] ? chunks[i + 1][0].start : c[c.length - 1].end + 1.2;
    return t >= c[0].start && t < nextStart;
  });
  if (idx < 0) return null;
  const chunk = chunks[idx];
  const local = frame - Math.round(chunk[0].start * fps);
  const s = spring({frame: local, fps, config: {damping: 16, mass: 0.5}});
  return (
    <div style={{position: 'absolute', left: 70, right: 70, top, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 22px', transform: `scale(${interpolate(s, [0, 1], [0.88, 1])})`, opacity: s}}>
      {chunk.map((w, i) => {
        const active = t >= w.start && t < w.end + 0.08;
        return (
          <span key={i} style={{fontFamily: DISPLAY, fontSize: 88, lineHeight: 1.15, textTransform: 'uppercase', color: active ? GOLD : WHITE, textShadow: '0 6px 18px rgba(0,0,0,0.65)', WebkitTextStroke: '2px rgba(0,0,0,0.35)'}}>
            {w.text.replace(/[.,:]$/, '')}
          </span>
        );
      })}
    </div>
  );
};

// ------------------------------------------------------------ main shell
export type Scene = {from: number; to: number; node: React.ReactNode};
export type Plan = {sub: string; scenes: Scene[]; court?: CourtSpec; overlays?: React.ReactNode};

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = Math.sin(frame / 90) * 60;
  return (
    <AbsoluteFill style={{background: `radial-gradient(circle at 50% ${35 + drift / 20}%, ${NAVY2} 0%, ${NAVY} 64%)`}}>
      <svg width={1080} height={1920} style={{position: 'absolute', opacity: 0.06}}>
        <circle cx={540} cy={960 + drift} r={260} stroke={WHITE} strokeWidth={6} fill="none" />
        <line x1={0} y1={960 + drift} x2={1080} y2={960 + drift} stroke={WHITE} strokeWidth={6} />
      </svg>
    </AbsoluteFill>
  );
};

const Header: React.FC<{sub: string}> = ({sub}) => (
  <div style={{position: 'absolute', top: 150, left: 0, right: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 18}}>
    <div style={{fontFamily: DISPLAY, fontSize: 52, color: GOLD, letterSpacing: 4}}>E2A</div>
    <div style={{width: 3, height: 34, background: GOLD, opacity: 0.6}} />
    <div style={{fontFamily: BODY, fontWeight: 600, fontSize: 30, color: MUTED, letterSpacing: 6}}>{sub}</div>
  </div>
);

export const Shell: React.FC<{plan: Plan; words: Word[]; n: number; total: number}> = ({plan, words, n, total}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill style={{backgroundColor: NAVY}}>
      <Background />
      {plan.court && <Court spec={plan.court} />}
      {plan.scenes.map((sc, i) => {
        if (t < sc.from || t >= sc.to) return null;
        const local = t - sc.from;
        const o = Math.min(1, local / 0.18);
        return (
          <AbsoluteFill key={i} style={{opacity: o}}>
            <SceneClock offset={Math.round(sc.from * fps)}>{sc.node}</SceneClock>
          </AbsoluteFill>
        );
      })}
      {plan.overlays}
      <Header sub={plan.sub} />
      <Captions words={words} />
      <Audio src={staticFile(`audio/v${n}.mp3`)} />
      <Audio
        src={staticFile('music.mp3')}
        loop
        volume={(f) => interpolate(f, [0, 20, total - 45, total], [0, 0.12, 0.12, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}
      />
    </AbsoluteFill>
  );
};

/** shifts the frame clock so scene-local hooks (spring) start at 0 */
import {Sequence} from 'remotion';
const SceneClock: React.FC<{offset: number; children: React.ReactNode}> = ({offset, children}) => {
  const {fps} = useVideoConfig();
  return (
    <OffCtx.Provider value={offset / fps}>
      <Sequence from={offset} layout="none">{children}</Sequence>
    </OffCtx.Provider>
  );
};
export {Pop};
