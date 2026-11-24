// E2A Broadcast Scoreboard + E2A League Comparison Intro logo slot (2026-11-24, NBA vs EuroLeague V2).
// Opt-in screen items (`scoreboard`, `leagueLogo`); nothing else uses them. Original E2A design inspired by broadcast
// conventions (dark bar, team rows, period + game clock, separate shot clock), not a copy of any network's graphics.
//   BroadcastScoreboard  league ID | two team rows (colour bar, name, score) | period + game clock | shot clock
//   LeagueLogo           official league logo on a white plate (object-fit contain = never distorted). When the file is
//                        not supplied (src null) it draws a clearly marked PLACEHOLDER, never an invented logo.
// `plate` = the plate colour; for a logo delivered on a flat background (EuroLeague JPG, #E6E6E6) the plate takes that
// colour so the file is shown as delivered (no background removal, no recolouring).
// All pure functions of their age (seek-safe). Times in seconds from the item's start.
import React from 'react';
import {Img, staticFile} from 'remotion';
import {LEAGUE} from './leagues';
import type {League} from './leagues';

const GOLD = '#C9A24D';
const ANTON = 'Anton, Impact, sans-serif';
const INTER = 'Inter, sans-serif';
const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = (u: number) => 1 - Math.pow(1 - clamp(u), 3);
const fade = (age: number, dur: number, i = 0.2, o = 0.25) => clamp(Math.min(age / i, (dur - age) / o));

export type SbTeam = {name: string; color: string; ink?: string; score: number};

/** age-based clock: `clock` = "MM:SS" at `runFrom` (s from item start); if `run` it counts down 1 s per second after runFrom */
const fmt = (sec: number) => `${Math.floor(sec / 60)}:${String(Math.floor(sec % 60)).padStart(2, '0')}`;
const parse = (s: string) => {
  const [m, x] = s.split(':').map(Number);
  return m * 60 + x;
};

export const BroadcastScoreboard: React.FC<{
  league: League; age: number; dur: number; y?: number; logo?: string | null; teams: [SbTeam, SbTeam]; period: string;
  clock: string; shot?: number | null; run?: number | null; highlight?: number | null; dim?: number | null; width?: number; plate?: string;
}> = ({league, age, dur, y = 600, logo, plate = '#FFFFFF', teams, period, clock, shot = 24, run = null, highlight = null, dim = null, width = 980}) => {
  const L = LEAGUE[league];
  const u = ease(age / 0.38);                       // wipe in from the left, no bounce
  const running = run != null && age > run ? age - run : 0;
  const gc = fmt(Math.max(0, parse(clock) - Math.floor(running)));
  const sc = shot == null ? null : Math.max(0, shot - Math.floor(running));
  const hl = highlight != null ? ease((age - highlight) / 0.35) : 0;
  const dm = dim != null ? ease((age - dim) / 0.3) : 0;
  const H = 176;
  const row = (t: SbTeam, i: number) => (
    <div key={i} style={{display: 'flex', alignItems: 'center', height: H / 2 - 6, padding: '0 18px 0 0', borderTop: i ? '1px solid rgba(255,255,255,0.08)' : 'none'}}>
      <span style={{width: 12, alignSelf: 'stretch', margin: '10px 16px 10px 0', borderRadius: 2, background: t.color, boxShadow: 'inset 0 0 0 1.5px rgba(255,255,255,0.55)'}} />
      <span style={{flex: 1, font: `400 46px ${ANTON}`, letterSpacing: 2.5, color: '#FFFFFF', paddingTop: 4}}>{t.name}</span>
      <span style={{font: `800 54px ${INTER}`, fontVariantNumeric: 'tabular-nums', color: '#FFFFFF', minWidth: 70, textAlign: 'right'}}>{t.score}</span>
    </div>
  );
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center', opacity: fade(age, dur) * (1 - 0.45 * dm)}}>
      <div data-qc="stamp" style={{width, height: H, display: 'flex', borderRadius: 14, overflow: 'hidden', clipPath: `inset(0 ${((1 - u) * 100).toFixed(2)}% 0 0 round 14px)`,
        transform: `translateY(${((1 - u) * 14).toFixed(1)}px)`, background: 'linear-gradient(180deg, #121A2C 0%, #070B14 100%)',
        border: '1.5px solid rgba(255,255,255,0.14)', boxShadow: '0 14px 34px rgba(0,0,0,0.55)'}}>
        {/* league ID */}
        <div style={{width: 214, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', background: plate}}>
          {logo ? (
            <Img src={staticFile(logo)} style={{maxWidth: 190, maxHeight: 136, objectFit: 'contain'}} />
          ) : (
            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2}}>
              <span style={{font: `400 ${league === 'el' ? 40 : 64}px ${ANTON}`, color: L.deep, letterSpacing: 2}}>{L.name}</span>
            </div>
          )}
          <span style={{position: 'absolute', right: 0, top: 0, bottom: 0, width: 8, background: L.col}} />
        </div>
        {/* teams */}
        <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '0 0 0 22px'}}>{teams.map(row)}</div>
        {/* period + game clock */}
        <div style={{width: 300, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.04)', borderLeft: '1px solid rgba(255,255,255,0.1)', position: 'relative'}}>
          <span style={{font: `700 26px ${INTER}`, letterSpacing: 5, color: GOLD, marginBottom: 2}}>{period}</span>
          <span style={{font: `800 92px ${INTER}`, fontVariantNumeric: 'tabular-nums', letterSpacing: -1, color: '#FFFFFF', lineHeight: 1}}>{gc}</span>
          <span style={{position: 'absolute', inset: 8, borderRadius: 10, border: `3px solid ${GOLD}`, opacity: hl, boxShadow: `0 0 ${(14 * hl).toFixed(1)}px rgba(201,162,77,0.45)`}} />
        </div>
        {/* shot clock */}
        {sc != null && (
          <div style={{width: 118, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', borderLeft: '1px solid rgba(255,255,255,0.1)', background: '#05070C'}}>
            <span style={{font: `700 18px ${INTER}`, letterSpacing: 3, color: 'rgba(255,255,255,0.55)'}}>SHOT</span>
            <span style={{font: `800 58px ${INTER}`, fontVariantNumeric: 'tabular-nums', color: '#FFC23D', lineHeight: 1.05}}>{sc}</span>
          </div>
        )}
      </div>
    </div>
  );
};

/** official league logo on a white plate; placeholder frame when the file has not been supplied */
export const LeagueLogo: React.FC<{league: League; src?: string | null; age: number; dur: number; y: number; h?: number; w?: number; delay?: number; align?: 'left' | 'center'; plate?: string}> = ({league, src, age, dur, y, h = 210, w = 470, delay = 0, align = 'center', plate = '#FFFFFF'}) => {
  const a = age - delay;
  if (a <= 0) return null;
  const u = ease(a / 0.45);
  const L = LEAGUE[league];
  return (
    <div style={{position: 'absolute', left: align === 'left' ? 40 : 0, right: align === 'left' ? undefined : 0, top: y, display: 'flex', justifyContent: 'center', opacity: u * fade(age, dur, 0.01, 0.25)}}>
      <div data-qc="stamp" style={{width: w, height: h, borderRadius: 22, background: src ? plate : 'rgba(7,11,20,0.78)', display: 'flex', alignItems: 'center', justifyContent: 'center',
        transform: `scale(${(0.92 + 0.08 * u).toFixed(4)})`, boxShadow: '0 16px 40px rgba(0,0,0,0.45)', border: src ? `3px solid ${L.col}` : `3px dashed ${L.col}`, boxSizing: 'border-box', padding: 18}}>
        {src ? (
          <Img src={staticFile(src)} style={{maxWidth: '100%', maxHeight: '100%', objectFit: 'contain'}} />
        ) : (
          <div style={{textAlign: 'center', color: '#FFFFFF'}}>
            <div style={{font: `700 ${w < 260 ? 15 : 24}px ${INTER}`, letterSpacing: 2, color: L.col}}>{w < 260 ? <>LOGO<br />PLACEHOLDER</> : 'LOGO PLACEHOLDER'}</div>
            <div style={{font: `700 ${w < 260 ? 12 : w < 340 ? 13 : 20}px ${INTER}`, letterSpacing: 1, opacity: 0.8, marginTop: 6, wordBreak: 'break-all'}}>{league === 'nba' ? 'leagues/nba.svg' : 'leagues/euroleague.svg'}</div>
          </div>
        )}
      </div>
    </div>
  );
};
