// Reusable motion graphics. All timing is scene-local seconds; anchors are converted with useAt().
import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {BODY, DISPLAY, GOLD, GOLD_LIGHT, MUTED, NAVY, NAVY_DEEP, RED, WHITE} from './brand';
import type {Anchor, ScoreTeam} from './types';

export type SceneInfo = {resolve: (a: Anchor, off?: number) => number; start: number; end: number};
export const SceneCtx = React.createContext<SceneInfo>({resolve: (a) => (typeof a === 'number' ? a : 0), start: 0, end: 1});

export const useLocalT = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return frame / fps;
};
/** anchor -> scene-local seconds */
export const useAt = () => {
  const s = React.useContext(SceneCtx);
  return (a: Anchor, off = 0) => s.resolve(a, off) - s.start;
};

const springAt = (t: number, fps: number, at: number, damping = 13, mass = 0.55) =>
  spring({frame: (t - at) * fps, fps, config: {damping, mass}});

const tone = (k?: 'gold' | 'white' | 'red') => (k === 'red' ? RED : k === 'white' ? WHITE : GOLD);

// ------------------------------------------------------------------ impact burst
/** Gold shock ring + rays when a number lands. age = seconds since the hit. */
export const Burst: React.FC<{age: number; size?: number; color?: string}> = ({age, size = 700, color = GOLD}) => {
  if (age < 0 || age > 0.55) return null;
  const k = age / 0.55;
  const e = 1 - Math.pow(1 - k, 3);
  return (
    <div style={{position: 'absolute', left: '50%', top: '50%', width: 0, height: 0, pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          left: (-size / 2) * e,
          top: (-size / 2) * e,
          width: size * e,
          height: size * e,
          borderRadius: '50%',
          border: `${14 * (1 - k) + 2}px solid ${color}`,
          opacity: 1 - k,
          boxShadow: `0 0 60px ${color}`,
        }}
      />
      {new Array(12).fill(0).map((_, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: 0,
            top: -4,
            width: size * 0.32,
            height: 8,
            background: `linear-gradient(90deg, transparent, ${color})`,
            transformOrigin: '0 50%',
            transform: `rotate(${i * 30 + 15}deg) translateX(${size * 0.18 + size * 0.3 * e}px) scaleX(${1 - k})`,
            opacity: 0.9 * (1 - k),
          }}
        />
      ))}
    </div>
  );
};

// ------------------------------------------------------------------ kicker
export const Kicker: React.FC<{text: string; top?: number; at?: number; boxed?: boolean}> = ({text, top = 300, at = 0.05, boxed = false}) => {
  const t = useLocalT();
  const {fps} = useVideoConfig();
  const s = springAt(t, fps, at, 18);
  return (
    <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 18, opacity: s, transform: `translateY(${(1 - s) * -24}px)`, ...(boxed ? {background: 'rgba(11,28,61,0.82)', padding: '12px 26px', borderRadius: 6} : {})}}>
        <div style={{width: 46 * s, height: 5, background: GOLD}} />
        <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 34, letterSpacing: 7, color: GOLD_LIGHT, textTransform: 'uppercase', whiteSpace: 'nowrap'}}>{text}</div>
        <div style={{width: 46 * s, height: 5, background: GOLD}} />
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ headline
/** Cinematic title: each line is revealed by a mask sweeping up, with a slight overshoot. */
export const Headline: React.FC<{lines: string[]; accent?: number[]; size?: number; top?: number}> = ({lines, accent = [], size = 170, top = 560}) => {
  const t = useLocalT();
  const {fps} = useVideoConfig();
  return (
    <div style={{position: 'absolute', top, left: 70, right: 70, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      {lines.map((l, i) => {
        const at = 0.08 + i * 0.16;
        const s = springAt(t, fps, at, 15, 0.5);
        const isAccent = accent.includes(i);
        const fs = l.length > 12 ? size * 0.72 : size;
        return (
          <div key={i} style={{overflow: 'hidden', paddingTop: 6}}>
            <div
              style={{
                fontFamily: DISPLAY,
                fontSize: fs,
                lineHeight: 1.0,
                color: isAccent ? GOLD : WHITE,
                textTransform: 'uppercase',
                letterSpacing: 2,
                textAlign: 'center',
                transform: `translateY(${(1 - s) * 105}%) skewY(${(1 - s) * 6}deg)`,
                textShadow: '0 10px 40px rgba(0,0,0,0.55)',
              }}
            >
              {l}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ------------------------------------------------------------------ stat
export const Stat: React.FC<{
  value: number;
  from?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  label: string;
  countFor?: number;
  second?: {at: number; value: string; label: string};
}> = ({value, from = 0, decimals = 0, prefix = '', suffix = '', label, countFor = 0.7, second}) => {
  const t = useLocalT();
  const {fps} = useVideoConfig();
  const k = interpolate(t, [0.05, 0.05 + countFor], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const v = from + (value - from) * k;
  const landAt = 0.05 + countFor;
  const landed = t > landAt;
  const land = landed ? springAt(t, fps, landAt, 9, 0.5) : 0;
  // the figure slams down from 1.5x with motion blur when it lands
  const slam = landed ? 1 + 0.5 * Math.exp(-(t - landAt) * 11) : 1;
  const slamBlur = landed ? 10 * Math.exp(-(t - landAt) * 25) : 0;
  const s2 = second ? springAt(t, fps, second.at, 12, 0.55) : 0;
  const shrink = second ? interpolate(s2, [0, 1], [1, 0.62]) : 1;
  return (
    <div style={{position: 'absolute', top: 420, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div style={{position: 'relative', transform: `scale(${shrink * slam})`, transformOrigin: '50% 30%', display: 'flex', flexDirection: 'column', alignItems: 'center', filter: slamBlur > 0.3 ? `blur(${slamBlur}px)` : undefined}}>
        <Burst age={t - landAt} size={760} />
        <div style={{fontFamily: DISPLAY, fontSize: 470, lineHeight: 0.9, color: GOLD, textShadow: `0 0 ${60 + land * 40}px rgba(201,162,77,0.45), 0 18px 50px rgba(0,0,0,0.6)`}}>
          {prefix}
          {v.toFixed(decimals)}
          {suffix}
        </div>
        <div style={{fontFamily: DISPLAY, fontSize: 96, color: WHITE, letterSpacing: 10, marginTop: 4}}>{label}</div>
      </div>
      {second && t >= second.at - 0.02 && (
        <div style={{position: 'relative', marginTop: -40, transform: `scale(${(0.6 + 0.4 * s2) * (1 + 0.35 * Math.exp(-(t - second.at) * 11))})`, opacity: s2, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <Burst age={t - second.at} size={560} color={WHITE} />
          <div style={{fontFamily: DISPLAY, fontSize: 250, color: WHITE, lineHeight: 0.95}}>{second.value}</div>
          <div style={{fontFamily: DISPLAY, fontSize: 80, color: GOLD, letterSpacing: 10}}>{second.label}</div>
        </div>
      )}
    </div>
  );
};

// ------------------------------------------------------------------ scoreboard
const scoreAt = (team: ScoreTeam, at: (a: Anchor) => number, t: number) => {
  let v = team.score[0][1];
  let changed = -99;
  team.score.forEach(([a, val], i) => {
    const tt = i === 0 ? -1 : at(a);
    if (t >= tt) {
      if (val !== v) changed = tt;
      v = val;
    }
  });
  return {v, changed};
};

export const Scoreboard: React.FC<{
  label?: string;
  home: ScoreTeam;
  away: ScoreTeam;
  timer?: {start: number; end: number; to: number; label: string};
}> = ({label, home, away, timer}) => {
  const t = useLocalT();
  const {fps} = useVideoConfig();
  const at = useAt();
  const enter = springAt(t, fps, 0.02, 16, 0.6);
  const row = (team: ScoreTeam) => {
    const {v, changed} = scoreAt(team, at, t);
    const age = t - changed;
    const bump = age >= 0 && age < 0.6 ? 1 + 0.6 * Math.exp(-age * 9) : 1;
    const blurS = age >= 0 && age < 0.15 ? 8 * (1 - age / 0.15) : 0;
    const glow = age >= 0 && age < 0.8 ? 1 - age / 0.8 : 0;
    return (
      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 40px', borderRadius: 16, background: team.accent ? 'rgba(201,162,77,0.10)' : 'transparent'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 24}}>
          <div style={{width: 12, height: 86, background: team.accent ? GOLD : WHITE, borderRadius: 3}} />
          <div style={{fontFamily: DISPLAY, fontSize: 92, color: WHITE, letterSpacing: 4}}>{team.name}</div>
        </div>
        <div style={{position: 'relative', fontFamily: DISPLAY, fontSize: 168, color: team.accent ? GOLD : WHITE, transform: `scale(${bump})`, transformOrigin: '70% 50%', filter: blurS ? `blur(${blurS}px)` : undefined, textShadow: `0 0 ${glow * 70}px rgba(230,195,116,${glow})`, minWidth: 260, textAlign: 'right'}}>
          {age >= 0 && <Burst age={age} size={420} />}
          {v}
        </div>
      </div>
    );
  };
  const timerV = timer ? interpolate(t, [timer.start, timer.end], [0, timer.to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  return (
    <div style={{position: 'absolute', top: 470, left: 70, right: 70, transform: `perspective(1400px) rotateX(${(1 - enter) * 50}deg) translateY(${(1 - enter) * 120}px)`, opacity: enter}}>
      {label && (
        <div style={{background: GOLD, color: NAVY, fontFamily: BODY, fontWeight: 900, fontSize: 32, letterSpacing: 6, padding: '12px 28px', textTransform: 'uppercase', display: 'inline-block', borderRadius: '10px 10px 0 0'}}>
          {label}
        </div>
      )}
      <div style={{background: 'rgba(6,15,34,0.82)', border: `3px solid rgba(201,162,77,0.6)`, borderRadius: label ? '0 18px 18px 18px' : 18, overflow: 'visible', backdropFilter: 'blur(6px)', boxShadow: '0 40px 80px rgba(0,0,0,0.5)'}}>
        {row(away)}
        <div style={{height: 2, background: 'rgba(255,255,255,0.12)', margin: '0 40px'}} />
        {row(home)}
      </div>
      {timer && t >= timer.start - 0.1 && (
        <div style={{marginTop: 26, display: 'flex', justifyContent: 'center'}}>
          <div style={{display: 'flex', alignItems: 'baseline', gap: 18, background: NAVY_DEEP, border: `3px solid ${RED}`, borderRadius: 16, padding: '10px 34px'}}>
            <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 30, color: MUTED, letterSpacing: 5}}>{timer.label}</div>
            <div style={{fontFamily: DISPLAY, fontSize: 96, color: RED, fontVariantNumeric: 'tabular-nums', minWidth: 190, textAlign: 'right'}}>{timerV.toFixed(1)}</div>
            <div style={{fontFamily: DISPLAY, fontSize: 50, color: RED}}>SEC</div>
          </div>
        </div>
      )}
    </div>
  );
};

// ------------------------------------------------------------------ callout stamp
export const Callout: React.FC<{at: number; text: string; color?: string; top?: number}> = ({at, text, color = GOLD, top = 1080}) => {
  const t = useLocalT();
  const {fps} = useVideoConfig();
  const age = t - at;
  if (age < 0 || age > 1.6) return null;
  const s = springAt(t, fps, at, 10, 0.45);
  const out = interpolate(age, [1.3, 1.6], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: out}}>
      <div
        style={{
          fontFamily: DISPLAY,
          fontSize: 110,
          color: color === WHITE ? NAVY : NAVY,
          background: color,
          padding: '0 38px',
          borderRadius: 14,
          transform: `scale(${interpolate(s, [0, 1], [2.1, 1])}) rotate(${interpolate(s, [0, 1], [-9, -3])}deg)`,
          opacity: Math.min(1, s * 2),
          boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
          letterSpacing: 3,
        }}
      >
        {text}
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ timeline
export const Timeline: React.FC<{title?: string; items: {at: number; label: string; value?: string; tone?: 'gold' | 'white' | 'red'}[]}> = ({title, items}) => {
  const t = useLocalT();
  const {fps} = useVideoConfig();
  const lastOn = items.filter((i) => t >= i.at).length;
  const lineP = interpolate(t, [0, Math.max(0.3, items[items.length - 1].at + 0.3)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', top: 400, left: 110, right: 150}}>
      {title && <div style={{fontFamily: DISPLAY, fontSize: 64, color: GOLD, letterSpacing: 4, marginBottom: 30, textTransform: 'uppercase'}}>{title}</div>}
      <div style={{position: 'relative'}}>
        <div style={{position: 'absolute', left: 21, top: 30, width: 4, height: `${lineP * (items.length - 1) * 150}px`, background: `linear-gradient(${GOLD}, rgba(201,162,77,0.2))`}} />
        {items.map((it, i) => {
          const s = springAt(t, fps, it.at, 14, 0.5);
          const active = i === lastOn - 1;
          return (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 34, height: 150, opacity: 0.25 + 0.75 * s, transform: `translateX(${(1 - s) * 60}px)`}}>
              <div style={{width: 46, height: 46, borderRadius: 23, background: t >= it.at ? tone(it.tone) : 'transparent', border: `4px solid ${tone(it.tone)}`, boxShadow: active ? `0 0 30px ${GOLD}` : 'none', flexShrink: 0}} />
              <div style={{flex: 1, fontFamily: DISPLAY, fontSize: active ? 64 : 54, color: active ? WHITE : MUTED, textTransform: 'uppercase', letterSpacing: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{it.label}</div>
              {it.value && <div style={{fontFamily: DISPLAY, fontSize: 84, color: tone(it.tone)}}>{it.value}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ split screen
export const Split: React.FC<{title?: string; left: {name: string; stats: [string, string][]}; right: {name: string; stats: [string, string][]}; winner?: 'left' | 'right'}> = ({title, left, right, winner}) => {
  const t = useLocalT();
  const {fps} = useVideoConfig();
  const wipe = springAt(t, fps, 0, 18, 0.7);
  const col = (side: typeof left, isLeft: boolean) => (
    <div style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 26, transform: `translateX(${(1 - wipe) * (isLeft ? -540 : 540)}px)`}}>
      <div style={{fontFamily: DISPLAY, fontSize: 84, color: (winner === 'left') === isLeft && winner ? GOLD : WHITE, textAlign: 'center', lineHeight: 1}}>{side.name}</div>
      {side.stats.map(([k, v], i) => {
        const s = springAt(t, fps, 0.35 + i * 0.22, 14, 0.5);
        return (
          <div key={i} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: s, transform: `scale(${0.7 + 0.3 * s})`}}>
            <div style={{fontFamily: DISPLAY, fontSize: 120, color: WHITE, lineHeight: 1}}>{v}</div>
            <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 28, color: MUTED, letterSpacing: 5, textTransform: 'uppercase'}}>{k}</div>
          </div>
        );
      })}
    </div>
  );
  return (
    <AbsoluteFill>
      {title && <Kicker text={title} top={300} />}
      <div style={{position: 'absolute', top: 400, left: 60, right: 60, display: 'flex'}}>
        {col(left, true)}
        <div style={{width: 4, background: GOLD, transform: `scaleY(${wipe})`, margin: '0 10px'}} />
        {col(right, false)}
      </div>
    </AbsoluteFill>
  );
};

/** Small credit chip for media (top-left, inside the safe area). */
export const Credit: React.FC<{text: string}> = ({text}) => (
  <div style={{position: 'absolute', top: 232, left: 80, fontFamily: BODY, fontWeight: 600, fontSize: 22, color: 'rgba(255,255,255,0.75)', background: 'rgba(0,0,0,0.35)', padding: '6px 14px', borderRadius: 8, letterSpacing: 1}}>
    {text}
  </div>
);
