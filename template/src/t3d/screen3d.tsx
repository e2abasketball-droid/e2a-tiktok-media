// E2A 3D engine — screen-space layer: kinetic titles, result stamps, projected player labels,
// premium word-by-word subtitles, freeze/rewind treatments and the logo. Designed for 1080x1920
// inside the Reels/TikTok/Shorts safe area (top 220 px, bottom 420 px, right 150 px kept clear).
import React from 'react';
import {Img, staticFile} from 'remotion';
import {BODY, DISPLAY, GOLD, NAVY, WHITE} from '../pro/brand';

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const eo = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const inOut = (age: number, dur: number, fin = 0.28, fout = 0.22) => Math.min(eo(age / fin), eo((dur - age) / fout));

/** big kinetic title: mask-wipe reveal per line, gold rule, gentle settle */
export const KineticTitle: React.FC<{lines: string[]; age: number; dur: number; y?: number; size?: number; gold?: number[]; sub?: string}> = ({lines, age, dur, y = 300, size = 120, gold = [], sub}) => {
  const out = clamp((dur - age) / 0.22);
  return (
    <div style={{position: 'absolute', left: 70, right: 160, top: y, opacity: eo(out)}}>
      {lines.map((l, i) => {
        const a = eo((age - i * 0.14) / 0.32);
        return (
          <div key={i} style={{overflow: 'hidden', height: size * 1.04}}>
            <div
              data-qc="title"
              data-qc-text="1"
              style={{
                fontFamily: DISPLAY,
                fontSize: size,
                lineHeight: 1.04,
                letterSpacing: 1,
                color: gold.includes(i) ? GOLD : WHITE,
                transform: `translateY(${(1 - a) * 100}%) scale(${1 + 0.04 * (1 - eo(age / 0.6))})`,
                transformOrigin: 'left bottom',
                textShadow: '0 6px 30px rgba(0,0,0,0.65), 0 2px 0 rgba(0,0,0,0.35)',
              }}
            >
              {l}
            </div>
          </div>
        );
      })}
      <div style={{height: 7, width: `${eo((age - 0.15) / 0.4) * 180}px`, background: GOLD, marginTop: 14, borderRadius: 4}} />
      {sub && (
        <div data-qc="title-sub" data-qc-text="1" style={{fontFamily: BODY, fontWeight: 800, fontSize: 38, letterSpacing: 4, color: 'rgba(255,255,255,0.85)', marginTop: 16, opacity: eo((age - 0.25) / 0.3), textTransform: 'uppercase'}}>{sub}</div>
      )}
    </div>
  );
};

/** result stamp: navy plate with gold edge, slides up and settles */
export const Stamp: React.FC<{text: string; age: number; dur: number; y?: number; tone?: 'gold' | 'white'; badge?: string}> = ({text, age, dur, y = 360, tone = 'gold', badge}) => {
  const a = inOut(age, dur, 0.25, 0.2);
  const s = 0.9 + 0.1 * eo(age / 0.3);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center', opacity: a, transform: `translateY(${(1 - eo(age / 0.3)) * 30}px) scale(${s})`}}>
      <div data-qc="stamp" style={{display: 'flex', alignItems: 'center', gap: 18, background: 'rgba(11,28,61,0.92)', border: `3px solid ${GOLD}`, borderRadius: 18, padding: '14px 30px', boxShadow: '0 14px 50px rgba(0,0,0,0.55)'}}>
        {badge && <span style={{fontFamily: DISPLAY, fontSize: 70, color: NAVY, background: GOLD, borderRadius: 12, padding: '0 16px', lineHeight: 1.15}}>{badge}</span>}
        <span style={{fontFamily: DISPLAY, fontSize: 78, letterSpacing: 2, color: tone === 'gold' ? GOLD : WHITE, lineHeight: 1.1}}>{text}</span>
      </div>
    </div>
  );
};

/** text width with the real font (canvas measureText), used to keep projected labels inside the safe area */
let measureCtx: CanvasRenderingContext2D | null = null;
export const textWidth = (text: string, font: string, letterSpacing = 0) => {
  if (!measureCtx) measureCtx = document.createElement('canvas').getContext('2d');
  if (!measureCtx) return text.length * 0.6 * parseFloat(font.match(/(\d+)px/)?.[1] ?? '40');
  measureCtx.font = font;
  return measureCtx.measureText(text).width + letterSpacing * text.length;
};

/** Reels/TikTok/Shorts safe area in a 1080x1920 frame (same numbers as scripts/qc-bounds.mts): header
 *  220 px, caption 420 px, 40 px side margins, and the action-button rail (right 150 px from y 760 down) */
export const SAFE = {left: 40, right: 1080 - 40, top: 220, bottom: 1920 - 420, railX: 1080 - 150, railY0: 760};

/** label pinned to a player (projected from 3D), with a short leader line. The label box is kept inside
 *  the safe area (it slides sideways / down when the player is near an edge); the leader line keeps
 *  pointing at the player. Script, play and edit timing are untouched. */
export const PinLabel: React.FC<{x: number; y: number; text: string; age: number; dur: number; tone?: 'gold' | 'red' | 'white'; dy?: number; size?: number}> = ({x, y, text, age, dur, tone = 'gold', dy = -70, size = 40}) => {
  // the player itself is out of shot: no label (it was never visible before either)
  if (x < 0 || x > 1080 || y < 0 || y > 1920) return null;
  const a = inOut(age, dur, 0.25, 0.2);
  const bg = tone === 'red' ? '#E5483A' : tone === 'white' ? 'rgba(255,255,255,0.95)' : GOLD;
  const fg = tone === 'white' ? NAVY : tone === 'red' ? WHITE : NAVY;
  const ty = Math.max(SAFE.top + size * 1.5, y + dy);
  // full-scale box (the pop-in scale only shrinks it): text + horizontal padding 2x16 + safety 6
  const half = (textWidth(text, `900 ${size}px ${BODY}`, 1.5) + 32 + 6) / 2;
  const right = ty > SAFE.railY0 ? SAFE.railX : SAFE.right; // ty = bottom edge of the label box
  const cx = Math.min(Math.max(x, SAFE.left + half), right - half);
  const lead = Math.abs(y - ty);
  return (
    <>
      <div style={{position: 'absolute', left: x - 1.5, top: Math.min(y, ty), width: 3, height: lead * eo(age / 0.25), background: bg, opacity: a * 0.9}} />
      <div style={{position: 'absolute', left: cx, top: ty, transform: `translate(-50%, -100%) scale(${0.85 + 0.15 * eo(age / 0.25)})`, opacity: a}}>
        <div data-qc="pin" style={{fontFamily: BODY, fontWeight: 900, fontSize: size, letterSpacing: 1.5, color: fg, background: bg, padding: '6px 16px', borderRadius: 10, whiteSpace: 'nowrap', boxShadow: '0 8px 24px rgba(0,0,0,0.45)'}}>{text}</div>
      </div>
    </>
  );
};

/** freeze treatment: thin gold corner brackets and a small "PAUSE" tag, no flash */
export const FreezeFrame: React.FC<{age: number; dur: number; label?: string}> = ({age, dur, label = 'FREEZE'}) => {
  const a = inOut(age, dur, 0.15, 0.15);
  const L = 70;
  const corner = (s: React.CSSProperties) => <div style={{position: 'absolute', width: L, height: L, borderColor: GOLD, borderStyle: 'solid', borderWidth: 0, opacity: a, ...s}} />;
  return (
    <>
      {corner({left: 40, top: 240, borderLeftWidth: 5, borderTopWidth: 5})}
      {corner({right: 40, top: 240, borderRightWidth: 5, borderTopWidth: 5})}
      {corner({left: 40, bottom: 440, borderLeftWidth: 5, borderBottomWidth: 5})}
      {corner({right: 40, bottom: 440, borderRightWidth: 5, borderBottomWidth: 5})}
      <div data-qc="freeze" style={{position: 'absolute', right: 60, top: 258, fontFamily: BODY, fontWeight: 900, fontSize: 26, letterSpacing: 5, color: NAVY, background: GOLD, padding: '4px 12px', borderRadius: 6, opacity: a}}>❚❚ {label}</div>
    </>
  );
};

export const RewindTag: React.FC<{age: number; dur: number}> = ({age, dur}) => {
  const a = inOut(age, dur, 0.08, 0.12);
  return (
    <>
      <div style={{position: 'absolute', inset: 0, background: 'rgba(11,28,61,0.18)', opacity: a}} />
      <div data-qc="rewind" data-qc-text="1" style={{position: 'absolute', left: 60, top: 258, fontFamily: BODY, fontWeight: 900, fontSize: 30, letterSpacing: 5, color: WHITE, opacity: a}}>◀◀ REWIND</div>
      {Array.from({length: 5}, (_, i) => (
        <div key={i} style={{position: 'absolute', left: 0, right: 0, top: ((age * 2400 + i * 380) % 1920) | 0, height: 2, background: 'rgba(255,255,255,0.18)', opacity: a}} />
      ))}
    </>
  );
};

export const Logo: React.FC<{age: number; big?: boolean}> = ({age, big}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: big ? 1010 : 1640, display: 'flex', justifyContent: 'center', opacity: eo(age / 0.4)}}>
    <Img data-qc="logo" src={staticFile('e2a_logo_white.png')} style={{width: big ? 300 : 150, opacity: 0.92}} />
  </div>
);

type W = {text: string; start: number; end: number};
const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, '');

/** premium subtitles: max two short lines, words appear exactly when spoken, key words in gold */
export const PremiumSubtitles: React.FC<{words: W[]; t: number; keys: string[]; y?: number; size?: number; hideRanges?: [number, number][]}> = ({words, t, keys, y = 1290, size = 56, hideRanges = []}) => {
  const groups = React.useMemo(() => {
    const out: W[][] = [];
    let cur: W[] = [];
    const len = (c: W[]) => c.reduce((n, w) => n + w.text.length + 1, 0);
    words.forEach((w, i) => {
      if (cur.length && len(cur) + w.text.length > 26) {
        out.push(cur);
        cur = [];
      }
      cur.push(w);
      const next = words[i + 1];
      if (/[.?!:]$/.test(w.text) || (next && next.start - w.end > 0.4) || cur.length >= 5) {
        out.push(cur);
        cur = [];
      }
    });
    if (cur.length) out.push(cur);
    return out;
  }, [words]);
  if (hideRanges.some(([a, b]) => t >= a && t < b)) return null;
  const kset = keys.map((k) => k.split(/\s+/).map(norm));
  const g = groups.find((c, i) => t >= c[0].start - 0.03 && t < Math.min(c[c.length - 1].end + 0.35, groups[i + 1]?.[0].start ?? 1e9));
  if (!g) return null;
  // key words (single or two-word keys like "stagger screen")
  const isKey = (i: number) =>
    kset.some((k) => {
      for (let s = 0; s < k.length; s++) {
        const st = i - s;
        if (st < 0 || st + k.length > g.length) continue;
        if (k.every((kw, j) => norm(g[st + j].text) === kw)) return true;
      }
      return false;
    });
  const end = g[g.length - 1].end + 0.35;
  const outA = clamp((end - t) / 0.18);
  return (
    <div style={{position: 'absolute', left: 90, right: 170, top: y, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: `4px ${size * 0.26}px`, opacity: outA}}>
      {g.map((w, i) => {
        const on = t >= w.start - 0.03;
        const a = eo((t - w.start + 0.03) / 0.12);
        const k = isKey(i);
        return (
          <span
            key={i}
            data-qc="subtitle"
            style={{
              fontFamily: BODY,
              fontWeight: 900,
              fontSize: size,
              lineHeight: 1.2,
              letterSpacing: 0.5,
              textTransform: 'uppercase',
              color: k ? GOLD : WHITE,
              opacity: on ? 0.35 + 0.65 * a : 0.0,
              transform: `translateY(${(1 - a) * 10}px)`,
              textShadow: '0 3px 0 rgba(0,0,0,0.6), 0 6px 22px rgba(0,0,0,0.75)',
            }}
          >
            {w.text.replace(/[,;]$/, '')}
          </span>
        );
      })}
    </div>
  );
};
