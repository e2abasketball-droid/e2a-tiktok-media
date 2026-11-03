// Word-by-word subtitles from the real ElevenLabs timings: at most two lines, numbers and
// key words highlighted, always inside the Reels/TikTok/Shorts safe area.
import React from 'react';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {DISPLAY, GOLD, NAVY, SAFE, WHITE} from './brand';
import {norm} from './timing';
import type {Word} from './types';

type Tok = {text: string; start: number; end: number; emph: boolean};

const NUMBER_WORDS = new Set(
  'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million'.split(' '),
);

/** Merge display phrases ("eight point nine" -> "8.9") and flag emphasis. */
export const tokenize = (words: Word[], display: Record<string, string> = {}, emphasis: string[] = []): Tok[] => {
  const phrases = Object.entries(display)
    .map(([k, v]) => ({k: k.split(/\s+/).map(norm), v}))
    .sort((a, b) => b.k.length - a.k.length);
  const emph = new Set(emphasis.map(norm));
  const out: Tok[] = [];
  for (let i = 0; i < words.length; ) {
    const hit = phrases.find((p) => p.k.every((w, j) => words[i + j] && norm(words[i + j].text) === w));
    if (hit) {
      const last = words[i + hit.k.length - 1];
      const trail = /[.,?!]$/.test(last.text) ? last.text.slice(-1) : '';
      out.push({text: hit.v + trail, start: words[i].start, end: last.end, emph: true});
      i += hit.k.length;
      continue;
    }
    const w = words[i];
    const n = norm(w.text);
    out.push({text: w.text, start: w.start, end: w.end, emph: /\d/.test(w.text) || NUMBER_WORDS.has(n) || emph.has(n)});
    i++;
  }
  return out;
};

const chunk = (toks: Tok[], maxChars: number) => {
  const out: Tok[][] = [];
  let cur: Tok[] = [];
  const len = (c: Tok[]) => c.reduce((n, x) => n + x.text.length + 1, 0);
  toks.forEach((w, i) => {
    if (cur.length && len(cur) + w.text.length > maxChars) {
      out.push(cur);
      cur = [];
    }
    cur.push(w);
    const next = toks[i + 1];
    const stop = /[.?!]$/.test(w.text) || (next ? next.start - w.end > 0.35 : true) || (/,$/.test(w.text) && len(cur) > maxChars * 0.5);
    if (stop || cur.length >= 6) {
      out.push(cur);
      cur = [];
    }
  });
  if (cur.length) out.push(cur);
  return out;
};

export const Subtitles: React.FC<{words: Word[]; display?: Record<string, string>; emphasis?: string[]; size?: number; hideAfter?: number; highRanges?: [number, number][]}> = ({
  words,
  highRanges = [],
  display,
  emphasis,
  size = 84,
  hideAfter,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const maxChars = Math.round((SAFE.right - SAFE.left) / (size * 0.47)) * 2 - 4; // two lines
  const chunks = React.useMemo(() => chunk(tokenize(words, display, emphasis), maxChars), [words, display, emphasis, maxChars]);
  if (hideAfter !== undefined && t > hideAfter) return null;
  const idx = chunks.findIndex((c, i) => {
    const nextStart = chunks[i + 1] ? chunks[i + 1][0].start : c[c.length - 1].end + 0.6;
    return t >= c[0].start - 0.05 && t < nextStart - 0.02;
  });
  if (idx < 0) return null;
  const c = chunks[idx];
  const high = highRanges.some(([a, b]) => c[0].start >= a && c[0].start < b);
  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.left,
        width: SAFE.right - SAFE.left,
        bottom: high ? 1920 - 640 : 1920 - SAFE.bottom,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        alignContent: 'flex-end',
        gap: `0 ${Math.round(size * 0.22)}px`,
      }}
    >
      {c.map((w, i) => {
        const shown = t >= w.start - 0.04;
        const s = spring({frame: (t - w.start + 0.04) * fps, fps, config: {damping: 14, mass: 0.35}});
        const active = t >= w.start - 0.04 && t < w.end + 0.06;
        const clean = w.text.replace(/[.,;:]$/, '');
        return (
          <span
            key={i}
            style={{
              fontFamily: DISPLAY,
              fontSize: size,
              lineHeight: 1.18,
              textTransform: 'uppercase',
              letterSpacing: 1,
              color: w.emph ? (active ? NAVY : GOLD) : WHITE,
              background: w.emph && active ? GOLD : 'transparent',
              padding: w.emph ? '0 10px' : 0,
              borderRadius: 10,
              opacity: shown ? s : 0,
              transform: `translateY(${(1 - s) * 22}px) scale(${active ? 1.06 : 1})`,
              textShadow: w.emph && active ? 'none' : '0 4px 0 rgba(0,0,0,0.55), 0 8px 24px rgba(0,0,0,0.6)',
              WebkitTextStroke: w.emph && active ? undefined : '1.5px rgba(0,0,0,0.45)',
            }}
          >
            {clean}
          </span>
        );
      })}
    </div>
  );
};
