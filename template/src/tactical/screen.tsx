// Screen-space graphics for tactical videos: TacticalText (kinetic titles), ResultStamp,
// FreezeFrameOverlay, RewindFX, TimingWindow bar, DecisionBranch, case kicker and the logo bug.
import React from 'react';
import {AbsoluteFill, Img, random, staticFile} from 'remotion';
import {BODY, DISPLAY, GOLD, NAVY, WHITE} from '../pro/brand';

const clamp = (x: number) => Math.max(0, Math.min(1, x));
const easeOut = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const back = (x: number) => {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  const t = clamp(x);
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
};

/** Kinetic title: words rise in one by one with a gold accent word and a wipe bar. */
export const TacticalText: React.FC<{text: string; age: number; dur: number; y?: number; size?: number; accent?: string[]; sub?: string; align?: 'center'}> = ({
  text,
  age,
  dur,
  y = 330,
  size = 104,
  accent = [],
  sub,
}) => {
  const out = clamp((age - (dur - 0.3)) / 0.3);
  const words = text.split(' ');
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: y, textAlign: 'center', opacity: 1 - out, transform: `translateY(${-out * 30}px)`}}>
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: `0 ${size * 0.24}px`}}>
        {words.map((w, i) => {
          const k = back((age - i * 0.07) / 0.45);
          const acc = accent.includes(w.replace(/[^A-Z0-9—-]/gi, ''));
          return (
            <span
              key={i}
              style={{
                fontFamily: DISPLAY,
                fontSize: size,
                lineHeight: 1.05,
                color: acc ? GOLD : WHITE,
                letterSpacing: 2,
                opacity: clamp((age - i * 0.07) / 0.15),
                transform: `translateY(${(1 - k) * 60}px)`,
                display: 'inline-block',
                textShadow: '0 6px 0 rgba(0,0,0,0.45), 0 10px 30px rgba(0,0,0,0.55)',
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
      <div style={{height: 8, margin: '14px auto 0', width: `${easeOut((age - 0.2) / 0.5) * 46}%`, background: GOLD, borderRadius: 4}} />
      {sub && (
        <div style={{marginTop: 14, fontFamily: BODY, fontWeight: 800, fontSize: 34, letterSpacing: 6, color: 'rgba(255,255,255,0.85)', opacity: clamp((age - 0.4) / 0.3)}}>{sub}</div>
      )}
    </div>
  );
};

/** Result stamp ("OPEN THREE", "SLIP TO THE RIM"): slams in, holds, fades. */
export const ResultStamp: React.FC<{text: string; age: number; dur: number; tone?: 'gold' | 'mint'; y?: number; badge?: string}> = ({text, age, dur, tone = 'gold', y = 300, badge}) => {
  const k = back(age / 0.35);
  const out = clamp((age - (dur - 0.3)) / 0.3);
  const bg = tone === 'gold' ? GOLD : '#7BE0A8';
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center', opacity: clamp(age / 0.08) * (1 - out)}}>
      <div style={{transform: `scale(${1.6 - 0.6 * k}) rotate(-2deg)`, background: bg, color: NAVY, fontFamily: DISPLAY, fontSize: 112, padding: '6px 38px 10px', borderRadius: 18, border: `6px solid ${NAVY}`, boxShadow: '0 18px 50px rgba(0,0,0,0.5)', letterSpacing: 3, display: 'flex', alignItems: 'center', gap: 24}}>
        {text}
        {badge && <span style={{background: NAVY, color: bg, borderRadius: 12, padding: '0 16px', fontSize: 84}}>{badge}</span>}
      </div>
    </div>
  );
};

/** Freeze-frame treatment: cool grade, frame corners, "FREEZE" tag and a pause glyph. */
export const FreezeFrameOverlay: React.FC<{age: number; dur: number; label?: string}> = ({age, dur, label = 'FREEZE'}) => {
  const k = easeOut(age / 0.25) * (1 - clamp((age - dur + 0.2) / 0.2));
  const c = 70;
  return (
    <AbsoluteFill style={{pointerEvents: 'none', opacity: k}}>
      <AbsoluteFill style={{background: 'rgba(20,40,80,0.16)', mixBlendMode: 'multiply'}} />
      <svg width={1080} height={1920} style={{position: 'absolute'}}>
        {[
          [40, 250, 1, 1],
          [1040, 250, -1, 1],
          [40, 1230, 1, -1],
          [1040, 1230, -1, -1],
        ].map(([x, y, sx, sy], i) => (
          <path key={i} d={`M${x} ${y + sy * c}L${x} ${y}L${x + sx * c} ${y}`} stroke={WHITE} strokeWidth={6} fill="none" />
        ))}
      </svg>
      <div style={{position: 'absolute', top: 262, left: 62, display: 'flex', alignItems: 'center', gap: 12, fontFamily: BODY, fontWeight: 900, fontSize: 28, letterSpacing: 5, color: WHITE}}>
        <span style={{display: 'inline-flex', gap: 5}}>
          <span style={{width: 8, height: 26, background: GOLD}} />
          <span style={{width: 8, height: 26, background: GOLD}} />
        </span>
        {label}
      </div>
    </AbsoluteFill>
  );
};

/** Rewind: scan lines, horizontal jitter and a ◀◀ glyph. */
export const RewindFX: React.FC<{age: number; dur: number}> = ({age, dur}) => {
  const k = Math.sin(clamp(age / dur) * Math.PI);
  const off = Math.floor(age * 40);
  return (
    <AbsoluteFill style={{pointerEvents: 'none', opacity: k}}>
      <AbsoluteFill style={{background: 'repeating-linear-gradient(0deg, rgba(255,255,255,0.06) 0 2px, transparent 2px 6px)'}} />
      {Array.from({length: 5}, (_, i) => (
        <div key={i} style={{position: 'absolute', left: 0, right: 0, top: 200 + random(`rw${off}-${i}`) * 1300, height: 4 + random(`rh${off}-${i}`) * 14, background: 'rgba(255,255,255,0.18)'}} />
      ))}
      <div style={{position: 'absolute', top: 262, right: 170, fontFamily: DISPLAY, fontSize: 64, color: WHITE, letterSpacing: -8, textShadow: '0 4px 20px rgba(0,0,0,0.6)'}}>◀◀</div>
    </AbsoluteFill>
  );
};

/** Timing window: the phases of the action and where we are in them (no invented numbers). */
export const TimingBar: React.FC<{phases: {label: string; t: number}[]; pt: number; age: number; y?: number}> = ({phases, pt, age, y = 1300}) => {
  const t0 = phases[0].t;
  const t1 = phases[phases.length - 1].t;
  const W = 820;
  const x0 = 130;
  const pos = (t: number) => x0 + ((t - t0) / (t1 - t0)) * W;
  const k = easeOut(age / 0.4);
  const cur = Math.max(t0, Math.min(t1, pt));
  return (
    <svg width={1080} height={120} style={{position: 'absolute', left: 0, top: y - 60, opacity: k}}>
      <rect x={x0} y={56} width={W} height={8} rx={4} fill="rgba(255,255,255,0.25)" />
      <rect x={x0} y={56} width={pos(cur) - x0} height={8} rx={4} fill={GOLD} />
      {phases.map((p, i) => {
        const on = pt >= p.t - 1e-3;
        return (
          <g key={i}>
            <circle cx={pos(p.t)} cy={60} r={13} fill={on ? GOLD : NAVY} stroke={on ? NAVY : 'rgba(255,255,255,0.6)'} strokeWidth={4} />
            <text x={pos(p.t)} y={i % 2 ? 108 : 30} textAnchor="middle" fontFamily={BODY} fontWeight={900} fontSize={24} letterSpacing={2} fill={on ? WHITE : 'rgba(255,255,255,0.5)'}>
              {p.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

/** Two possible outcomes branching from one defensive decision. */
export const DecisionBranch: React.FC<{age: number; root: string; left: [string, string]; right: [string, string]; highlight?: 'left' | 'right' | 'both'; y?: number}> = ({age, root, left, right, highlight = 'both', y = 300}) => {
  const k = easeOut(age / 0.8);
  const on = (s: 'left' | 'right') => highlight === 'both' || highlight === s;
  const box = (x: number, t: [string, string], side: 'left' | 'right', d: number) => (
    <g opacity={clamp((age - d) / 0.3) * (on(side) ? 1 : 0.4)} transform={`translate(${x} ${y + 190})`}>
      <rect x={-200} y={-12} width={400} height={128} rx={18} fill={NAVY} stroke={side === 'left' ? GOLD : '#7BE0A8'} strokeWidth={5} />
      <text x={0} y={42} textAnchor="middle" fontFamily={BODY} fontWeight={900} fontSize={34} letterSpacing={3} fill={WHITE}>
        {t[0]}
      </text>
      <text x={0} y={92} textAnchor="middle" fontFamily={DISPLAY} fontSize={40} letterSpacing={2} fill={side === 'left' ? GOLD : '#7BE0A8'}>
        {t[1]}
      </text>
    </g>
  );
  return (
    <svg width={1080} height={700} style={{position: 'absolute', left: 0, top: 0}} viewBox={`0 0 1080 700`}>
      <g transform={`translate(0 ${y - 300})`}>
        <path d={`M540 ${330} C540 ${400} 300 ${400} 300 ${480}`} stroke={GOLD} strokeWidth={6} fill="none" strokeDasharray={600} strokeDashoffset={600 * (1 - k)} opacity={on('left') ? 1 : 0.4} />
        <path d={`M540 ${330} C540 ${400} 780 ${400} 780 ${480}`} stroke="#7BE0A8" strokeWidth={6} fill="none" strokeDasharray={600} strokeDashoffset={600 * (1 - k)} opacity={on('right') ? 1 : 0.4} />
        <g opacity={clamp(age / 0.25)}>
          <rect x={540 - 190} y={250} width={380} height={80} rx={40} fill={WHITE} />
          <text x={540} y={304} textAnchor="middle" fontFamily={BODY} fontWeight={900} fontSize={34} letterSpacing={4} fill={NAVY}>
            {root}
          </text>
        </g>
      </g>
      {box(300, left, 'left', 0.5)}
      {box(780, right, 'right', 0.65)}
    </svg>
  );
};

/** Persistent case kicker in the top band. */
export const Kicker: React.FC<{text: string; age: number; tone?: 'gold' | 'mint'}> = ({text, age, tone = 'gold'}) => (
  <div style={{position: 'absolute', top: 236, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: clamp(age / 0.3)}}>
    <div style={{fontFamily: BODY, fontWeight: 900, fontSize: 30, letterSpacing: 7, color: NAVY, background: tone === 'gold' ? GOLD : '#7BE0A8', padding: '8px 22px', borderRadius: 10}}>{text}</div>
  </div>
);

export const LogoBug: React.FC<{age: number; big?: boolean}> = ({age, big}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: big ? 1060 : 1400, display: 'flex', justifyContent: 'center', opacity: clamp(age / 0.5)}}>
    <Img src={staticFile('e2a_logo_white.png')} style={{height: big ? 210 : 120, transform: `scale(${0.92 + 0.08 * easeOut(age / 0.8)})`, filter: 'drop-shadow(0 8px 24px rgba(0,0,0,0.5))'}} />
  </div>
);

/** Constant small brand bug, top-left, inside the safe area. */
export const BrandBug: React.FC = () => (
  <div style={{position: 'absolute', top: 160, left: 70, display: 'flex', alignItems: 'center', gap: 14, opacity: 0.9}}>
    <Img src={staticFile('e2a_logo_white.png')} style={{height: 46}} />
    <div style={{width: 3, height: 30, background: GOLD}} />
    <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 24, letterSpacing: 6, color: 'rgba(255,255,255,0.85)'}}>TACTICS</div>
  </div>
);

/** "Split of possibilities": the frame cracks into two halves, one per defensive choice. */
export const Fork: React.FC<{age: number; dur: number; left: string; right: string; y?: number}> = ({age, dur, left, right, y = 760}) => {
  const k = easeOut(age / 0.5) * (1 - clamp((age - dur + 0.35) / 0.35));
  const h = 1000 * k;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: 0, width: 540, top: 300, height: 1000, background: 'rgba(8,18,40,0.45)', opacity: k}} />
      <div style={{position: 'absolute', left: 537, width: 6, top: 300 + (1000 - h) / 2, height: h, background: GOLD, boxShadow: `0 0 24px ${GOLD}`}} />
      <div style={{position: 'absolute', left: 0, width: 540, top: y, textAlign: 'center', opacity: k}}>
        <span style={{fontFamily: DISPLAY, fontSize: 64, color: 'rgba(255,255,255,0.75)', letterSpacing: 2, textShadow: '0 4px 18px rgba(0,0,0,0.8)'}}>{left}</span>
      </div>
      <div style={{position: 'absolute', left: 540, width: 540, top: y, textAlign: 'center', opacity: k}}>
        <span style={{fontFamily: DISPLAY, fontSize: 64, color: '#7BE0A8', letterSpacing: 2, textShadow: '0 4px 18px rgba(0,0,0,0.8)'}}>{right}</span>
      </div>
    </AbsoluteFill>
  );
};
