import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Court, CW, CH, SCALE, toPx} from './court';
import {BODY, DISPLAY, FPS, GOLD, NAVY, NAVY_2, WHITE, SAFE} from './theme';
import type {Arrow, Episode, Pt, Player, Word} from './types';

const ease = Easing.inOut(Easing.cubic);

function posAt(p: Player, t: number): {x: number; y: number; dribbling: boolean} {
  const w = p.path;
  if (t <= w[0].t) return {x: w[0].x, y: w[0].y, dribbling: false};
  for (let i = 0; i < w.length - 1; i++) {
    if (t <= w[i + 1].t) {
      const k = ease(interpolate(t, [w[i].t, w[i + 1].t], [0, 1]));
      return {x: w[i].x + (w[i + 1].x - w[i].x) * k, y: w[i].y + (w[i + 1].y - w[i].y) * k, dribbling: !!w[i + 1].dribble};
    }
  }
  const l = w[w.length - 1];
  return {x: l.x, y: l.y, dribbling: false};
}

function ballAt(ep: Episode, t: number): Pt {
  const resolve = (b: Episode['ball'][number]): Pt => {
    if (b.at) {
      const p = ep.players.find((q) => q.id === b.at)!;
      const s = posAt(p, b.t);
      return [s.x + 0.9, s.y + 0.9];
    }
    return [b.x!, b.y!];
  };
  const bs = ep.ball;
  if (t <= bs[0].t) return resolve(bs[0]);
  for (let i = 0; i < bs.length - 1; i++) {
    if (t <= bs[i + 1].t) {
      // while a player holds the ball (same holder both ends) follow them live
      if (bs[i].at && bs[i].at === bs[i + 1].at) {
        const s = posAt(ep.players.find((q) => q.id === bs[i].at)!, t);
        return [s.x + 0.9, s.y + 0.9];
      }
      const a = resolve(bs[i]);
      const b = resolve(bs[i + 1]);
      const k = interpolate(t, [bs[i].t, bs[i + 1].t], [0, 1]);
      return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k];
    }
  }
  return resolve(bs[bs.length - 1]);
}

const resolvePt = (ep: Episode, v: Pt | string, t: number): Pt => {
  if (typeof v !== 'string') return v;
  const s = posAt(ep.players.find((q) => q.id === v)!, t);
  return [s.x, s.y];
};

const ArrowShape: React.FC<{ep: Episode; a: Arrow; t: number}> = ({ep, a, t}) => {
  const grow = interpolate(t, [a.t0, a.t1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const fade = interpolate(t, [a.t1 + (a.show ?? 2.2), a.t1 + (a.show ?? 2.2) + 0.5], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (t < a.t0 || fade <= 0) return null;
  const f = toPx(resolvePt(ep, a.from, a.t0));
  const e = toPx(resolvePt(ep, a.to, a.t1));
  const dx = e[0] - f[0];
  const dy = e[1] - f[1];
  const len = Math.hypot(dx, dy) || 1;
  const nx = -dy / len;
  const ny = dx / len;
  const cur: Pt = [f[0] + dx * grow, f[1] + dy * grow];
  const color = a.kind === 'screen' ? GOLD : WHITE;
  let d = `M ${f[0]} ${f[1]} L ${cur[0]} ${cur[1]}`;
  if (a.kind === 'dribble') {
    const n = Math.max(4, Math.round(len / 28));
    d = `M ${f[0]} ${f[1]}`;
    for (let i = 1; i <= n * grow; i++) {
      const k = i / n;
      const s = i % 2 ? 1 : -1;
      d += ` L ${f[0] + dx * k + nx * 11 * s} ${f[1] + dy * k + ny * 11 * s}`;
    }
  }
  const ang = (Math.atan2(dy, dx) * 180) / Math.PI;
  return (
    <g opacity={fade}>
      <path d={d} fill="none" stroke={color} strokeWidth={a.kind === 'screen' ? 8 : 6} strokeLinecap="round" strokeDasharray={a.kind === 'pass' ? '4 18' : undefined} />
      {a.kind === 'screen' ? (
        <line x1={cur[0] + nx * 26} y1={cur[1] + ny * 26} x2={cur[0] - nx * 26} y2={cur[1] - ny * 26} stroke={GOLD} strokeWidth={9} strokeLinecap="round" />
      ) : (
        grow > 0.9 && <polygon points="0,0 -22,-11 -22,11" fill={color} transform={`translate(${e[0]} ${e[1]}) rotate(${ang})`} />
      )}
    </g>
  );
};

const PlayerDot: React.FC<{p: Player; t: number}> = ({p, t}) => {
  const s = posAt(p, t);
  const [x, y] = toPx([s.x, s.y]);
  const bob = s.dribbling ? Math.sin(t * 22) * 3 : 0;
  if (p.team === 'o')
    return (
      <g transform={`translate(${x} ${y + bob})`}>
        <circle r={30} fill={NAVY} stroke={GOLD} strokeWidth={6} />
        <text textAnchor="middle" dy={13} fontFamily={DISPLAY} fontSize={36} fill={WHITE}>{p.label}</text>
      </g>
    );
  return (
    <g transform={`translate(${x} ${y})`} stroke={WHITE} strokeWidth={9} strokeLinecap="round">
      <line x1={-18} y1={-18} x2={18} y2={18} />
      <line x1={18} y1={-18} x2={-18} y2={18} />
    </g>
  );
};

const Captions: React.FC<{words: Word[]; t: number}> = ({words, t}) => {
  let idx = words.findIndex((w) => t >= w.s && t < w.e + 0.15);
  if (idx < 0) idx = words.filter((w) => w.s <= t).length - 1;
  if (idx < 0) return null;
  // group into chunks of up to 4 words, breaking on sentence punctuation
  let start = idx;
  while (start > 0 && idx - start < 3 && !/[.!?]$/.test(words[start - 1].w)) start--;
  let end = idx;
  while (end < words.length - 1 && end - start < 3 && !/[.!?,]$/.test(words[end].w)) end++;
  const chunk = words.slice(start, end + 1);
  if (t > words[words.length - 1].e + 0.6) return null;
  return (
    <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 18px', fontFamily: DISPLAY, fontSize: 74, textTransform: 'uppercase', lineHeight: 1.15}}>
      {chunk.map((w, i) => (
        <span key={start + i} style={{color: start + i === idx ? GOLD : WHITE, transform: start + i === idx ? 'scale(1.08)' : undefined, textShadow: '0 4px 14px rgba(0,0,0,0.6)'}}>
          {w.w.replace(/[.,!?]$/, '')}
        </span>
      ))}
    </div>
  );
};

const Logo: React.FC<{size: number}> = ({size}) => (
  // Official logo, white on transparent: used directly on the navy background (no card)
  <Img src={staticFile('e2a_logo_white.png')} style={{width: size, height: size * 0.752, objectFit: 'contain'}} />
);

export const Breakdown: React.FC<{episode: Episode}> = ({episode: ep}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const t = frame / FPS;
  const dur = durationInFrames / FPS;
  const step = ep.steps.find((s) => t >= s.t0 && t < s.t1) ?? ep.steps[ep.steps.length - 1];
  const stepIdx = ep.steps.indexOf(step);

  // camera: slow push toward the step's focus point, eased between steps
  const focus = step.focus ?? {x: 25, y: 23, zoom: 1};
  const prev = ep.steps[Math.max(0, stepIdx - 1)].focus ?? {x: 25, y: 23, zoom: 1};
  const k = ease(interpolate(t, [step.t0, step.t0 + 0.9], [0, 1], {extrapolateRight: 'clamp'}));
  const cam = {x: prev.x + (focus.x - prev.x) * k, y: prev.y + (focus.y - prev.y) * k, zoom: prev.zoom + (focus.zoom - prev.zoom) * k + (t - step.t0) * 0.004};
  const [fx, fy] = toPx([cam.x, cam.y]);
  const tagIn = interpolate(t - step.t0, [0, 0.35], [0, 1], {extrapolateRight: 'clamp'});

  const ball = toPx(ballAt(ep, t));
  const endStart = dur - 3.2;
  const showEnd = t >= endStart;

  return (
    <AbsoluteFill style={{background: `radial-gradient(circle at 50% 30%, ${NAVY_2}, ${NAVY} 70%)`, fontFamily: BODY}}>
      <Audio src={staticFile(ep.voice)} />
      <Audio src={staticFile('music.mp3')} volume={(f) => interpolate(f / FPS, [0, 1, dur - 2, dur], [0, 0.1, 0.1, 0], {extrapolateRight: 'clamp'})} loop />
      {ep.sfx.map((s, i) => (
        <Sequence key={i} from={Math.round(s.t * FPS)}>
          <Audio src={staticFile(`sfx/${s.file}.mp3`)} volume={s.volume ?? 0.5} />
        </Sequence>
      ))}

      {/* header (inside safe area) */}
      <div style={{position: 'absolute', top: SAFE.top, left: 60, right: SAFE.right, display: 'flex', alignItems: 'center', gap: 24}}>
        <Logo size={120} />
        <div>
          <div style={{fontFamily: DISPLAY, fontSize: 30, letterSpacing: 6, color: GOLD}}>{ep.kicker} · E2A BREAKDOWN</div>
          <div style={{fontFamily: DISPLAY, fontSize: 66, color: WHITE, textTransform: 'uppercase', lineHeight: 1.05}}>{ep.title}</div>
        </div>
      </div>

      {/* court with camera */}
      <div style={{position: 'absolute', left: 30, top: 395, width: CW, height: CH, overflow: 'hidden', borderRadius: 24, border: `3px solid ${GOLD}`}}>
        <div style={{width: CW, height: CH, transformOrigin: `${fx}px ${fy}px`, transform: `scale(${cam.zoom})`}}>
          <Court />
          <svg width={CW} height={CH} style={{position: 'absolute', left: 0, top: 0}}>
            {ep.highlights.map((h, i) => {
              const o = interpolate(t, [h.t0, h.t0 + 0.3, h.t1 - 0.3, h.t1], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
              const [hx, hy] = toPx([h.x, h.y]);
              const pulse = 1 + Math.sin(t * 6) * 0.06;
              return o > 0 ? <circle key={i} cx={hx} cy={hy} r={h.r * SCALE * pulse} fill="rgba(201,164,76,0.22)" stroke={GOLD} strokeWidth={5} opacity={o} /> : null;
            })}
            {ep.arrows.map((a, i) => <ArrowShape key={i} ep={ep} a={a} t={t} />)}
            {ep.players.map((p) => <PlayerDot key={p.id} p={p} t={t} />)}
            <circle cx={ball[0]} cy={ball[1]} r={15} fill="#E07B2A" stroke="#6b2f08" strokeWidth={3} />
          </svg>
        </div>
      </div>

      {/* step tag */}
      <div style={{position: 'absolute', left: 60, top: 395 + CH + 22, opacity: tagIn, transform: `translateY(${(1 - tagIn) * 20}px)`, display: 'flex', alignItems: 'center', gap: 18}}>
        <div style={{background: GOLD, color: NAVY, fontFamily: DISPLAY, fontSize: 38, padding: '6px 22px', borderRadius: 10}}>{step.tag}</div>
        <div style={{color: WHITE, fontFamily: BODY, fontWeight: 700, fontSize: 40}}>{step.label}</div>
      </div>

      {/* captions: bottom of safe zone, above 450px bottom margin */}
      <div style={{position: 'absolute', left: 60, right: SAFE.right, top: 1920 - SAFE.bottom - 170, height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <Captions words={ep.words} t={t} />
      </div>

      {showEnd && (
        <AbsoluteFill style={{background: NAVY, opacity: interpolate(t, [endStart, endStart + 0.5], [0, 1], {extrapolateRight: 'clamp'}), alignItems: 'center', justifyContent: 'center'}}>
          <Logo size={420} />
          <div style={{marginTop: 50, fontFamily: DISPLAY, fontSize: 70, color: GOLD, textTransform: 'uppercase', textAlign: 'center', padding: '0 80px'}}>Follow E2A for more breakdowns</div>
          <div style={{marginTop: 18, fontFamily: BODY, fontWeight: 600, fontSize: 36, color: WHITE, letterSpacing: 4}}>MORE THAN A GAME</div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
