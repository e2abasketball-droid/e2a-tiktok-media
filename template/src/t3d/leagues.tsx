// E2A NBA vs EuroLeague screen graphics (2026-11-24). Original E2A graphics: league names as plain lettering in a
// secondary tone (no league logos, no player images). E2A navy + gold stay the main identity.
//   LeagueTag   pill "NBA" / "EUROLEAGUE"
//   VsTitle     NBA vs EUROLEAGUE lock-up (hook / close)
//   ClockDuel   two scoreboard clocks: 12:00 x 4 = 48 MIN vs 10:00 x 4 = 40 MIN (regulation time, NOT a running clock)
//   FoulTrack   personal-foul counter of ONE player: 1..N lights up, the last one = FOULED OUT
//   Count3      big 1 - 2 - 3 count with a ring
// All are pure functions of their age (seek-safe), times in seconds from the item's start.
import React from 'react';

export const LEAGUE = {
  nba: {name: 'NBA', col: '#2F6FE4', deep: '#16357A'},
  el: {name: 'EUROLEAGUE', col: '#F28C28', deep: '#7A3A0C'},
} as const;
export type League = keyof typeof LEAGUE;
const GOLD = '#C9A24D';
const NAVY = '#0B1C3D';
const RED = '#E5483A';
const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const pop = (age: number, d = 0.28) => {
  const u = clamp(age / d);
  return u < 0.6 ? 1.35 - 0.41 * (u / 0.6) : 0.94 + 0.06 * ((u - 0.6) / 0.4);
};
const fade = (age: number, dur: number, i = 0.15, o = 0.22) => clamp(Math.min(age / i, (dur - age) / o));
const ANTON = 'Anton, Impact, sans-serif';

export const LeagueTag: React.FC<{league: League; age: number; dur: number; y?: number; align?: 'left' | 'center' | 'right'; size?: number}> = ({league, age, dur, y = 150, align = 'center', size = 64}) => {
  const L = LEAGUE[league];
  const x = 1 - clamp(age / 0.22);
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: y, display: 'flex', justifyContent: align === 'left' ? 'flex-start' : align === 'right' ? 'flex-end' : 'center', opacity: fade(age, dur)}}>
      <div data-qc="stamp" style={{transform: `translateY(${(-16 * x * x).toFixed(1)}px)`, display: 'flex', alignItems: 'stretch', borderRadius: 12, overflow: 'hidden', boxShadow: '0 8px 26px rgba(0,0,0,0.5)'}}>
        <span style={{width: 14, background: GOLD}} />
        <span style={{background: L.col, color: '#FFFFFF', font: `400 ${size}px ${ANTON}`, letterSpacing: 4, padding: '6px 26px 2px', lineHeight: 1.1}}>{L.name}</span>
      </div>
    </div>
  );
};

export const VsTitle: React.FC<{age: number; dur: number; y?: number; size?: number; question?: string}> = ({age, dur, y = 250, size = 110, question}) => {
  const a = fade(age, dur, 0.12, 0.2);
  const k1 = pop(age), k2 = pop(age - 0.12), k3 = pop(age - 0.22);
  const box = (lg: League, k: number, t: number): React.CSSProperties => ({display: 'inline-block', transform: `scale(${k.toFixed(3)})`, opacity: clamp(t / 0.1), background: LEAGUE[lg].col, color: '#FFFFFF',
    font: `400 ${size}px ${ANTON}`, letterSpacing: 4, padding: '4px 26px 0', borderRadius: 14, lineHeight: 1.12, boxShadow: '0 10px 30px rgba(0,0,0,0.55)'});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, opacity: a}}>
      {question && <div data-qc="stamp" style={{font: `400 ${Math.round(size * 0.66)}px ${ANTON}`, color: '#FFFFFF', letterSpacing: 2, textShadow: '0 6px 24px rgba(0,0,0,0.7)', marginBottom: 10, transform: `scale(${pop(age).toFixed(3)})`}}>{question}</div>}
      <div data-qc="stamp" style={box('nba', k1, age)}>NBA</div>
      <div data-qc="stamp" style={{transform: `scale(${k2.toFixed(3)})`, opacity: clamp((age - 0.12) / 0.1), font: `400 ${Math.round(size * 0.6)}px ${ANTON}`, color: GOLD, letterSpacing: 6, textShadow: '0 4px 18px rgba(0,0,0,0.8)'}}>VS</div>
      <div data-qc="stamp" style={box('el', k3, age - 0.22)}>EUROLEAGUE</div>
    </div>
  );
};

/** one scoreboard clock: league strip, LED 12:00, four quarter pips, total */
const Board: React.FC<{lg: League; mins: number; on: number; pips: number; total: number; dim: boolean}> = ({lg, mins, on, pips, total, dim}) => {
  const L = LEAGUE[lg];
  const k = on > 0 ? pop(on, 0.3) : 0.9;
  const tk = total > 0 ? pop(total, 0.32) : 0;
  return (
    <div style={{width: 450, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: on > 0 ? (dim ? 0.55 : 1) : 0, transform: `scale(${(dim ? 0.9 : k).toFixed(3)})`, transition: 'none'}}>
      <div data-qc="stamp" style={{width: '100%', borderRadius: 22, overflow: 'hidden', background: 'linear-gradient(180deg, #0E1424 0%, #05080F 100%)', border: `4px solid ${L.col}`, boxShadow: `0 0 34px ${L.col}55, 0 14px 40px rgba(0,0,0,0.6)`}}>
        <div style={{background: L.col, color: '#FFFFFF', font: `400 52px ${ANTON}`, letterSpacing: 4, textAlign: 'center', padding: '4px 0 0'}}>{L.name}</div>
        <div style={{font: `700 132px 'JetBrains Mono', 'DejaVu Sans Mono', monospace`, color: '#FFB547', textAlign: 'center', letterSpacing: 2, lineHeight: 1.15, textShadow: '0 0 18px rgba(255,170,60,0.75)', padding: '8px 0 0'}}>{mins}:00</div>
        <div style={{display: 'flex', justifyContent: 'center', gap: 14, padding: '6px 0 18px'}}>
          {[1, 2, 3, 4].map((q) => (
            <div key={q} style={{width: 78, padding: '4px 0 0', borderRadius: 8, textAlign: 'center', font: `400 36px ${ANTON}`, letterSpacing: 1,
              background: q <= pips ? GOLD : 'rgba(255,255,255,0.08)', color: q <= pips ? NAVY : 'rgba(255,255,255,0.45)'}}>Q{q}</div>
          ))}
        </div>
      </div>
      <div data-qc="stamp" style={{marginTop: 18, opacity: clamp(total / 0.08), transform: `scale(${tk.toFixed(3)})`, font: `400 150px ${ANTON}`, color: '#FFFFFF', lineHeight: 1, letterSpacing: 2,
        textShadow: `0 0 30px ${L.col}AA, 0 10px 30px rgba(0,0,0,0.7)`, WebkitTextStroke: `3px ${NAVY}`}}>
        {mins * 4}<span style={{fontSize: 70, color: GOLD, marginLeft: 10}}>MIN</span>
      </div>
    </div>
  );
};

/** times relative to the item's start: nba / el = board appears, *Pips = the four quarters light (0.12 s apart), *Total = big total pops */
export const ClockDuel: React.FC<{age: number; dur: number; y?: number; nba: number; nbaTotal: number; el: number; elTotal: number; sub?: string}> = ({age, dur, y = 300, nba, nbaTotal, el, elTotal, sub}) => {
  const pipsOf = (t0: number, t1: number) => Math.max(0, Math.min(4, Math.floor((age - t0) / ((t1 - t0) / 4.2)) + 1));
  const a = fade(age, dur, 0.15, 0.25);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: a}}>
      <div style={{display: 'flex', justifyContent: 'center', gap: 40}}>
        <Board lg="nba" mins={12} on={age - nba} pips={age >= nba ? pipsOf(nba, nbaTotal) : 0} total={age - nbaTotal} dim={age >= el + 0.2 && age < elTotal + 0.6} />
        <Board lg="el" mins={10} on={age - el} pips={age >= el ? pipsOf(el, elTotal) : 0} total={age - elTotal} dim={false} />
      </div>
      {sub && <div data-qc="stamp" style={{marginTop: 26, opacity: clamp((age - elTotal - 0.3) / 0.25), padding: '8px 20px', borderRadius: 8, background: 'rgba(5,10,21,0.72)', border: '1.5px solid rgba(201,162,77,0.8)', color: '#FFE6B8', font: '700 32px Inter, sans-serif', letterSpacing: 3}}>{sub}</div>}
    </div>
  );
};

/** personal fouls of one player; ticks = seconds (from the item start) at which fouls 1..N light up; out = FOULED OUT */
export const FoulTrack: React.FC<{league: League; max: number; ticks: number[]; out: number; age: number; dur: number; y?: number; label?: string}> = ({league, max, ticks, out, age, dur, y = 300, label = 'PERSONAL FOULS'}) => {
  const L = LEAGUE[league];
  const n = ticks.filter((t) => age >= t).length;
  const sz = max >= 6 ? 128 : 138;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16, opacity: fade(age, dur)}}>
      {/* label '' (2026-11-24 V3 opt-in): no header at all (the league is identified elsewhere) */}
      {label ? (
        <div data-qc="stamp" style={{display: 'flex', alignItems: 'stretch', borderRadius: 10, overflow: 'hidden', boxShadow: '0 6px 22px rgba(0,0,0,0.5)'}}>
          <span style={{background: L.col, color: '#FFFFFF', font: `400 50px ${ANTON}`, letterSpacing: 3, padding: '4px 18px 0'}}>{L.name}</span>
          <span style={{background: 'rgba(11,28,61,0.94)', color: '#FFFFFF', font: `700 32px Inter, sans-serif`, letterSpacing: 3, padding: '14px 18px 0'}}>{label}</span>
        </div>
      ) : null}
      <div data-qc="stamp" style={{display: 'flex', gap: 14}}>
        {Array.from({length: max}, (_, i) => {
          const lit = i < n;
          const last = i === max - 1;
          const k = lit ? pop(age - ticks[i], 0.24) : 0.92;
          return (
            <div key={i} style={{width: sz, height: sz, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${k.toFixed(3)})`,
              background: lit ? (last ? RED : '#FFFFFF') : 'rgba(5,10,21,0.7)', border: `5px solid ${lit ? (last ? '#FFFFFF' : GOLD) : 'rgba(255,255,255,0.35)'}`,
              boxShadow: lit && last ? '0 0 34px rgba(229,72,58,0.9)' : '0 6px 18px rgba(0,0,0,0.45)',
              font: `400 ${Math.round(sz * 0.62)}px ${ANTON}`, color: lit ? (last ? '#FFFFFF' : NAVY) : 'rgba(255,255,255,0.55)', paddingTop: 6, boxSizing: 'border-box'}}>{i + 1}</div>
          );
        })}
      </div>
      {age >= out && (
        <div data-qc="stamp" style={{transform: `scale(${pop(age - out).toFixed(3)})`, padding: '8px 28px 2px', borderRadius: 14, background: RED, color: '#FFFFFF', font: `400 86px ${ANTON}`, letterSpacing: 3, boxShadow: '0 10px 30px rgba(0,0,0,0.5)'}}>FOULED OUT</div>
      )}
    </div>
  );
};

/** big 1 - 2 - 3 count: ticks = seconds from the item start; ring fills between ticks; red at 3 */
export const Count3: React.FC<{ticks: number[]; age: number; dur: number; y?: number; size?: number}> = ({ticks, age, dur, y = 380, size = 240}) => {
  const n = ticks.filter((t) => age >= t).length;
  if (n === 0) return null;
  const t0 = ticks[n - 1];
  const red = n >= ticks.length;
  const col = red ? RED : '#FFFFFF';
  const R = size * 0.62;
  const fill = red ? 1 : clamp((age - t0) / ((ticks[n] ?? t0 + 1) - t0));
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center', opacity: fade(age, dur, 0.08, 0.2)}}>
      <div data-qc="stamp" style={{position: 'relative', width: R * 2 + 24, height: R * 2 + 24, transform: `scale(${pop(age - t0, 0.22).toFixed(3)})`}}>
        <svg width={R * 2 + 24} height={R * 2 + 24} style={{position: 'absolute', left: 0, top: 0}}>
          <circle cx={R + 12} cy={R + 12} r={R} fill="rgba(5,10,21,0.72)" stroke="rgba(255,255,255,0.25)" strokeWidth={12} />
          <circle cx={R + 12} cy={R + 12} r={R} fill="none" stroke={red ? RED : GOLD} strokeWidth={12} strokeLinecap="round"
            strokeDasharray={`${(2 * Math.PI * R * fill).toFixed(1)} 9999`} transform={`rotate(-90 ${R + 12} ${R + 12})`} />
        </svg>
        <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', font: `400 ${size}px ${ANTON}`, color: col, paddingTop: size * 0.08, textShadow: '0 8px 26px rgba(0,0,0,0.6)'}}>{n}</div>
      </div>
    </div>
  );
};
