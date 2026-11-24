// E2A Football — screen-space layer for 1080x1920 YouTube Shorts: kinetic titles, stamps, projected
// player labels, word-by-word subtitles, freeze / replay tags, logo bug and end card.
// Safe area kept clear of the Shorts UI: top 220 px, bottom 440 px, right 160 px.
import React from 'react';
import {Img, staticFile} from 'remotion';
import {BODY, DISPLAY, GOLD, LOGO, NAVY, RED, WHITE} from './brand';

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const inOut = (age: number, dur: number, fin = 0.25, fout = 0.2) => Math.min(eo(age / fin), eo((dur - age) / fout));
export const SAFE = {top: 220, bottom: 440, right: 160, left: 64};

export const KineticTitle: React.FC<{lines: string[]; age: number; dur: number; y?: number; size?: number; gold?: number[]; sub?: string; align?: 'left' | 'center'}> = ({lines, age, dur, y = 330, size = 112, gold = [], sub, align = 'left'}) => {
  const out = clamp((dur - age) / 0.22);
  return (
    <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: y, opacity: eo(out), textAlign: align}}>
      {lines.map((l, i) => {
        const a = eo((age - i * 0.12) / 0.3);
        return (
          <div key={i} style={{overflow: 'hidden', height: size * 1.06}}>
            <div
              data-qc="title"
              style={{
                fontFamily: DISPLAY,
                fontSize: size,
                lineHeight: 1.06,
                letterSpacing: 1,
                color: gold.includes(i) ? GOLD : WHITE,
                transform: `translateY(${(1 - a) * 100}%)`,
                textShadow: '0 6px 28px rgba(0,0,0,0.7), 0 2px 0 rgba(0,0,0,0.4)',
              }}
            >
              {l}
            </div>
          </div>
        );
      })}
      <div style={{height: 7, width: `${eo((age - 0.15) / 0.4) * 170}px`, background: GOLD, marginTop: 12, borderRadius: 4, marginLeft: align === 'center' ? 'auto' : 0, marginRight: align === 'center' ? 'auto' : 0}} />
      {sub && (
        <div data-qc="title-sub" style={{fontFamily: BODY, fontWeight: 800, fontSize: 36, letterSpacing: 4, color: 'rgba(255,255,255,0.88)', marginTop: 14, opacity: eo((age - 0.25) / 0.3), textTransform: 'uppercase', textShadow: '0 3px 14px rgba(0,0,0,0.7)'}}>
          {sub}
        </div>
      )}
    </div>
  );
};

export const Stamp: React.FC<{text: string; age: number; dur: number; y?: number; tone?: 'gold' | 'white' | 'red'; badge?: string}> = ({text, age, dur, y = 380, tone = 'gold', badge}) => {
  const a = inOut(age, dur, 0.22, 0.2);
  const s = 0.92 + 0.08 * eo(age / 0.28);
  const col = tone === 'gold' ? GOLD : tone === 'red' ? RED : WHITE;
  return (
    <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: y, display: 'flex', justifyContent: 'center', opacity: a, transform: `translateY(${(1 - eo(age / 0.28)) * 26}px) scale(${s})`}}>
      <div data-qc="stamp" style={{display: 'flex', alignItems: 'center', gap: 16, background: 'rgba(11,28,61,0.92)', border: `3px solid ${col}`, borderRadius: 16, padding: '12px 28px', boxShadow: '0 14px 44px rgba(0,0,0,0.5)'}}>
        {badge && <span style={{fontFamily: DISPLAY, fontSize: 60, color: NAVY, background: col, borderRadius: 10, padding: '0 14px', lineHeight: 1.15}}>{badge}</span>}
        <span style={{fontFamily: DISPLAY, fontSize: text.length > 18 ? 52 : text.length > 12 ? 60 : 70, letterSpacing: 2, color: col, lineHeight: 1.1, whiteSpace: 'nowrap'}}>{text}</span>
      </div>
    </div>
  );
};

/** label pinned to a player (projected from 3D), with a thin leader line */
export const Pin: React.FC<{x: number; y: number; text: string; age: number; dur: number; tone?: 'gold' | 'white' | 'red'; dy?: number; dx?: number; size?: number}> = ({x, y, text, age, dur, tone = 'gold', dy = 120, dx = 0, size = 44}) => {
  const a = inOut(age, dur, 0.2, 0.18);
  const col = tone === 'gold' ? GOLD : tone === 'red' ? RED : WHITE;
  const lx = clamp(x + dx, SAFE.left + 150, 1080 - SAFE.right - 150);
  const ly = clamp(y - dy, SAFE.top + 90, 1920 - SAFE.bottom - 60); // +90: clear of the logo bug
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, opacity: a, pointerEvents: 'none'}}>
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        <line x1={x} y1={y - 8} x2={lx} y2={ly + 30} stroke={col} strokeWidth={4} strokeDasharray="10 8" opacity={eo(age / 0.3)} />
        <circle cx={x} cy={y - 8} r={7} fill={col} />
      </svg>
      <div
        data-qc="pin"
        style={{
          position: 'absolute',
          left: lx,
          top: ly,
          transform: `translate(-50%, -50%) scale(${0.85 + 0.15 * eo(age / 0.25)})`,
          background: 'rgba(11,28,61,0.94)',
          border: `3px solid ${col}`,
          borderRadius: 12,
          padding: '6px 18px',
          fontFamily: DISPLAY,
          fontSize: size,
          letterSpacing: 1.5,
          color: col,
          whiteSpace: 'nowrap',
          boxShadow: '0 10px 30px rgba(0,0,0,0.45)',
        }}
      >
        {text}
      </div>
    </div>
  );
};

export type Word = {text: string; start: number; end: number; br?: boolean};

/** word-by-word subtitles: 2 lines max, the spoken word lights up gold, keywords stay gold */
export const Subtitles: React.FC<{words: Word[]; t: number; keys: string[]; y?: number; mode?: 'karaoke' | 'keys'; size?: number}> = ({words, t, keys, y = 1920 - SAFE.bottom - 210, mode = 'karaoke', size = 58}) => {
  // phrases: break on punctuation or every ~5 words
  const phrases: Word[][] = [];
  let cur: Word[] = [];
  words.forEach((w, i) => {
    cur.push(w);
    const next = words[i + 1];
    const brk = w.br || cur.length >= 9 || !next || next.start - w.end > 0.35;
    if (brk) {
      phrases.push(cur);
      cur = [];
    }
  });
  const ph = phrases.find((p) => t >= p[0].start - 0.08 && t <= p[p.length - 1].end + 0.25);
  if (!ph) return null;
  const age = t - (ph[0].start - 0.08);
  const left = ph[ph.length - 1].end + 0.25 - t;
  const a = Math.min(eo(age / 0.12), eo(left / 0.12));
  const isKey = (s: string) => keys.includes(s.replace(/[^A-Za-z'-]/g, '').toLowerCase());
  return (
    <div style={{position: 'absolute', left: SAFE.left + 10, right: SAFE.right - 40, top: y, display: 'flex', justifyContent: 'center', opacity: a, transform: `translateY(${(1 - eo(age / 0.15)) * 14}px)`}}>
      <div data-qc="subtitle" style={{textAlign: 'center', fontFamily: BODY, fontWeight: 900, fontSize: size, lineHeight: 1.18, letterSpacing: 0.3, textTransform: 'uppercase', maxWidth: 860, ...(mode === 'keys' ? {background: 'rgba(11,28,61,0.58)', borderRadius: 14, padding: '8px 14px'} : {})}}>
        {ph.map((w, i) => {
          const on = t >= w.start - 0.03;
          const now = t >= w.start - 0.03 && t <= w.end + 0.05;
          // V09 'keys': white text, gold ONLY on the tactical keywords; the spoken word is marked by opacity, not colour
          const col = isKey(w.text) ? GOLD : mode === 'keys' ? WHITE : now ? GOLD : WHITE;
          return (
            <span key={i} style={{color: col, opacity: on ? 1 : mode === 'keys' ? 0.5 : 0.55, textShadow: mode === 'keys' ? '0 2px 0 rgba(0,0,0,0.5)' : '0 4px 0 rgba(0,0,0,0.55), 0 0 22px rgba(0,0,0,0.65)', display: 'inline-block', transform: `scale(${now && mode !== 'keys' ? 1.05 : 1})`, margin: mode === 'keys' ? '0 7px' : '0 9px'}}>
              {w.text}
            </span>
          );
        })}
      </div>
    </div>
  );
};

export const Tag: React.FC<{text: string; age: number; dur: number; icon?: 'pause' | 'replay' | 'slow'}> = ({text, age, dur, icon = 'pause'}) => {
  const a = inOut(age, dur, 0.15, 0.15);
  return (
    <div style={{position: 'absolute', right: SAFE.right + 10, top: SAFE.top + 20, opacity: a, display: 'flex', alignItems: 'center', gap: 12, background: 'rgba(11,28,61,0.88)', border: `2px solid ${GOLD}`, borderRadius: 40, padding: '8px 22px 8px 16px'}}>
      <svg width={30} height={30} viewBox="0 0 30 30">
        {icon === 'pause' && (
          <g fill={GOLD}>
            <rect x={6} y={5} width={6} height={20} rx={1.5} />
            <rect x={18} y={5} width={6} height={20} rx={1.5} />
          </g>
        )}
        {icon === 'replay' && <path d="M15 5a10 10 0 1 1-9.5 7" stroke={GOLD} strokeWidth={4} fill="none" strokeLinecap="round" />}
        {icon === 'replay' && <path d="M3 5l3 8 7-4z" fill={GOLD} />}
        {icon === 'slow' && <path d="M6 6l10 9-10 9zM16 6l10 9-10 9z" fill={GOLD} opacity={0.9} />}
      </svg>
      <span style={{fontFamily: BODY, fontWeight: 900, fontSize: 30, letterSpacing: 4, color: WHITE}}>{text}</span>
    </div>
  );
};

export const LogoBug: React.FC<{opacity?: number}> = ({opacity = 0.9}) => (
  <Img src={staticFile(LOGO)} style={{position: 'absolute', left: SAFE.left - 10, top: SAFE.top - 30, height: 88, opacity, filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.6))'}} />
);

export const EndCard: React.FC<{age: number}> = ({age}) => {
  const a = eo(age / 0.4);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: a}}>
      <Img src={staticFile(LOGO)} style={{height: 330, transform: `scale(${0.9 + 0.1 * eo(age / 0.6)})`, filter: 'drop-shadow(0 10px 30px rgba(0,0,0,0.6))'}} />
      <div style={{marginTop: 26, fontFamily: BODY, fontWeight: 900, fontSize: 34, letterSpacing: 9, color: GOLD, opacity: eo((age - 0.25) / 0.4)}}>E2A FOOTBALL · TACTICS</div>
    </div>
  );
};

/** quick cut accent: a soft light flash on shot changes */
export const Flash: React.FC<{age: number; strength?: number}> = ({age, strength = 0.35}) => {
  if (age > 0.25) return null;
  return <div style={{position: 'absolute', inset: 0, background: '#FFFFFF', opacity: strength * (1 - eo(age / 0.25))}} />;
};

/** V03 label chip: compact pill anchored to a player or a pitch point, short leader line, accent bar.
 *  Replaces the big pins/stamps for in-play annotations (SHORT PASS, DEFENDER STEPS OUT, ...). */
export const Chip: React.FC<{x: number; y: number; text: string; age: number; dur: number; tone?: 'gold' | 'white' | 'red'; dy?: number; dx?: number; size?: number; letter?: boolean}> = ({x, y, text, age, dur, tone = 'gold', dy = 110, dx = 0, size = 34, letter}) => {
  const a = inOut(age, dur, 0.22, 0.2);
  const col = tone === 'gold' ? GOLD : tone === 'red' ? RED : WHITE;
  const lx = clamp(x + dx, SAFE.left + 60, 1080 - SAFE.right - 60);
  const ly = clamp(y - dy, SAFE.top + 90, 1920 - 260);
  const grow = eo(age / 0.3);
  const ex = x + (lx - x) * grow;
  const ey = y - 6 + (ly + 24 - (y - 6)) * grow;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, opacity: a, pointerEvents: 'none'}}>
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        <line x1={x} y1={y - 6} x2={ex} y2={ey} stroke="rgba(6,18,42,0.55)" strokeWidth={6} strokeLinecap="round" />
        <line x1={x} y1={y - 6} x2={ex} y2={ey} stroke={col} strokeWidth={2.5} strokeLinecap="round" />
        <circle cx={x} cy={y - 6} r={5.5} fill={col} stroke="rgba(6,18,42,0.6)" strokeWidth={2} />
      </svg>
      <div
        data-qc="chip"
        style={{
          position: 'absolute',
          left: lx,
          top: ly,
          transform: `translate(-50%, -50%) translateX(${(1 - grow) * -18}px)`,
          display: 'flex',
          alignItems: 'stretch',
          background: 'rgba(11,28,61,0.92)',
          borderRadius: 10,
          overflow: 'hidden',
          boxShadow: '0 8px 24px rgba(0,0,0,0.35)',
        }}
      >
        <div style={{width: letter ? 0 : 8, background: col}} />
        <div style={{fontFamily: letter ? DISPLAY : BODY, fontWeight: 900, fontSize: letter ? size + 8 : size, letterSpacing: letter ? 1 : 3, color: letter ? col : WHITE, padding: letter ? '2px 16px' : '8px 18px 8px 14px', whiteSpace: 'nowrap', textTransform: 'uppercase', lineHeight: 1.15}}>{text}</div>
      </div>
    </div>
  );
};

/** V07 run-trigger marker: WHEN a player moves (a small gold kicker label over the cue text), anchored to the
 *  player like a chip. `now` = the decisive "go" moment: gold text, one short pulse. */
export const Cue: React.FC<{x: number; y: number; text: string; kicker?: string; age: number; dur: number; dy?: number; dx?: number; now?: boolean}> = ({x, y, text, kicker, age, dur, dy = 120, dx = 0, now}) => {
  const a = inOut(age, dur, 0.18, 0.2);
  const lx = clamp(x + dx, SAFE.left + 80, 1080 - SAFE.right - 40);
  const ly = clamp(y - dy, SAFE.top + 90, 1920 - 260);
  const grow = eo(age / 0.25);
  const pulse = now ? 1 + 0.1 * Math.exp(-age * 5) * Math.sin(age * 16) : 1;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, opacity: a, pointerEvents: 'none'}}>
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
        <line x1={x} y1={y - 6} x2={x + (lx - x) * grow} y2={y - 6 + (ly + 26 - (y - 6)) * grow} stroke="rgba(6,18,42,0.5)" strokeWidth={5} strokeLinecap="round" />
        <line x1={x} y1={y - 6} x2={x + (lx - x) * grow} y2={y - 6 + (ly + 26 - (y - 6)) * grow} stroke={GOLD} strokeWidth={2} strokeLinecap="round" />
      </svg>
      <div
        data-qc="chip"
        style={{
          position: 'absolute',
          left: lx,
          top: ly,
          transform: `translate(-50%, -50%) scale(${pulse})`,
          background: now ? 'rgba(201,162,77,0.96)' : 'rgba(11,28,61,0.9)',
          border: now ? 'none' : `2px solid ${GOLD}`,
          borderRadius: 10,
          padding: now ? '6px 20px' : '6px 16px 7px',
          boxShadow: '0 8px 22px rgba(0,0,0,0.32)',
          textAlign: 'center',
        }}
      >
        {kicker && <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 18, letterSpacing: 4, color: now ? NAVY : GOLD, lineHeight: 1.2}}>{kicker}</div>}
        <div style={{fontFamily: now ? DISPLAY : BODY, fontWeight: 900, fontSize: now ? 46 : 28, letterSpacing: now ? 2 : 2.5, color: now ? NAVY : WHITE, whiteSpace: 'nowrap', textTransform: 'uppercase', lineHeight: 1.15}}>{text}</div>
      </div>
    </div>
  );
};

/** V07 trigger timeline: CORNER -> DECOY -> LATE RUN -> DELIVERY -> FINISH; the step whose play time has been
 *  reached is lit (driven by the master timeline, not by video time — it is NOT a playback bar) */
export const Steps: React.FC<{steps: [string, number][]; pt: number; age: number; dur: number; y?: number; x?: number; fin?: number; fout?: number}> = ({steps, pt, age, dur, y = 1470, x, fin = 0.25, fout = 0.25}) => {
  // fin / fout 0 (V08): the bar continues across a cut without blinking
  const a = Math.min(fin > 0 ? eo(age / fin) : 1, fout > 0 ? eo((dur - age) / fout) : 1);
  let cur = -1;
  steps.forEach(([, t], i) => {
    if (pt >= t) cur = i;
  });
  return (
    <div style={{position: 'absolute', left: x ?? 0, right: x === undefined ? 0 : undefined, top: y, display: 'flex', justifyContent: x === undefined ? 'center' : 'flex-start', alignItems: 'center', gap: 8, opacity: a}}>
      {steps.map(([label], i) => {
        const on = i === cur;
        const past = i < cur;
        return (
          <React.Fragment key={label}>
            {i > 0 && <div style={{width: 18, height: 2, background: past || on ? GOLD : 'rgba(255,255,255,0.45)'}} />}
            <div
              style={{
                fontFamily: BODY,
                fontWeight: 900,
                fontSize: 21,
                letterSpacing: 2,
                padding: '6px 11px',
                borderRadius: 8,
                color: on ? NAVY : past ? GOLD : 'rgba(255,255,255,0.78)',
                background: on ? GOLD : 'rgba(11,28,61,0.78)',
                transform: `scale(${on ? 1.06 : 1})`,
                whiteSpace: 'nowrap',
              }}
            >
              {label}
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};

/** V07 goal payoff accent: a thin gold light along the frame edges that breathes once (no flash, no text) */
export const GoalAccent: React.FC<{age: number; dur: number}> = ({age, dur}) => {
  const a = Math.sin(Math.PI * Math.min(1, Math.max(0, age / dur)));
  return <div style={{position: 'absolute', inset: 0, boxShadow: `inset 0 0 ${60 + 60 * a}px rgba(201,162,77,${0.42 * a})`, border: `3px solid rgba(201,162,77,${0.5 * a})`, pointerEvents: 'none'}} />;
};

/** V07 discreet signature: small logo + line at the bottom, over the still-moving picture (no scrim, no card) */
export const Signature: React.FC<{age: number}> = ({age}) => {
  const a = eo(age / 0.35);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 1300, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: a}}>
      <Img src={staticFile(LOGO)} style={{height: 150, filter: 'drop-shadow(0 6px 18px rgba(0,0,0,0.55))', transform: `translateY(${(1 - a) * 14}px)`}} />
      <div style={{marginTop: 10, fontFamily: BODY, fontWeight: 900, fontSize: 24, letterSpacing: 7, color: GOLD, textShadow: '0 2px 8px rgba(0,0,0,0.6)'}}>E2A FOOTBALL · TACTICS</div>
    </div>
  );
};
