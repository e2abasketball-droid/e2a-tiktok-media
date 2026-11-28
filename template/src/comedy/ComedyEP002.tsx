// EVERY COURT HAS ONE — EP002 "THE BALL HOG" renderer (YouTube Shorts 1080x1920, 30 fps).
// Picture only: the audio master is mixed separately (tools/comedy/mix_ep_v2.py) and muxed after.
import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import '../theme';
import {Ball, Stage} from './stage';
import {Toon, fk} from './toon';
import {CAPTION_Y, CAST, DURATION, FPS, HIGHLIGHT, LINES, LOOKS, NO_CAPTION, SHOTS, ballAt, mouthOf, poseAt} from './ep002';
import type {Hook} from './ep002';

export const ep002Duration = () => Math.round(DURATION * FPS);

const GOLD = '#E3BE68';
const stroke = {WebkitTextStroke: '10px #05070C', paintOrder: 'stroke fill', textShadow: '0 6px 18px rgba(0,0,0,0.55)'} as const;

const Caption: React.FC<{t: number; y: number; shotStart: number}> = ({t, y, shotStart}) => {
  // a line shows while it is spoken (+0.2 s); never carried into a shot that starts after it ended
  const line = LINES.lines.find((l) => !NO_CAPTION.has(l.id) && t >= l.words[0].start - 0.04 && t < l.end + 0.2 && !(shotStart > l.words[l.words.length - 1].end + 0.05));
  if (!line) return null;
  const hl = HIGHLIGHT.has(line.id);
  // words appear exactly when they are spoken (a punchline is never revealed early)
  const shown = line.words.filter((w) => t >= w.start - 0.04);
  if (!shown.length) return null;
  const first = line.words[0].start;
  const pop = interpolate(t, [first - 0.04, first + 0.08], [0.9, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const text = shown.map((w) => w.text).join(' ');
  return (
    <div style={{position: 'absolute', left: 130, right: 130, top: y, transform: `translateY(-50%) scale(${pop})`, textAlign: 'center'}}>
      <span style={{fontFamily: 'Anton', fontSize: hl ? 100 : 74, lineHeight: 1.08, letterSpacing: hl ? 1.5 : 0.5, color: hl ? GOLD : '#FFFFFF', ...stroke}}>
        {hl ? text.toUpperCase() : text}
      </span>
    </div>
  );
};

// series title: only once the hook is already running, small, at the top (never over the joke)
const T_IN = 0.9;
const T_OUT = 2.55;
const Title: React.FC<{t: number}> = ({t}) => {
  if (t < T_IN || t > T_OUT) return null;
  const a = interpolate(t, [T_IN, T_IN + 0.12, T_OUT - 0.2, T_OUT], [0, 1, 1, 0]);
  const s = interpolate(t, [T_IN, T_IN + 0.18], [1.08, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 90, right: 90, top: 230, textAlign: 'center', opacity: a, transform: `scale(${s})`}}>
      <span style={{fontFamily: 'Anton', fontSize: 74, lineHeight: 1.05, color: '#fff', ...stroke, WebkitTextStroke: '9px #05070C'}}>
        EVERY COURT HAS <span style={{color: GOLD}}>THIS GUY...</span>
      </span>
    </div>
  );
};

// shareable ending: lands with ACE's spoken "Tag that friend." (never before it)
const END_IN = 27.55;
const EndCard: React.FC<{t: number}> = ({t}) => {
  if (t < END_IN) return null;
  const a = interpolate(t, [END_IN, END_IN + 0.12], [0, 1], {extrapolateRight: 'clamp'});
  const s = interpolate(t, [END_IN, END_IN + 0.15], [1.12, 1], {extrapolateRight: 'clamp'});
  const a2 = interpolate(t, [END_IN + 0.4, END_IN + 0.55], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sig = interpolate(t, [END_IN + 0.9, END_IN + 1.15], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <>
      <div style={{position: 'absolute', left: 70, right: 70, top: 1190, textAlign: 'center', opacity: a, transform: `scale(${s})`}}>
        <span style={{fontFamily: 'Anton', fontSize: 104, lineHeight: 1.0, letterSpacing: 1.5, color: '#fff', ...stroke}}>
          TAG <span style={{color: GOLD}}>THAT FRIEND</span>
        </span>
      </div>
      <div style={{position: 'absolute', left: 60, right: 60, top: 1315, textAlign: 'center', opacity: a2}}>
        <span style={{fontFamily: 'Anton', fontSize: 84, lineHeight: 1.0, letterSpacing: 1, color: '#fff', ...stroke}}>
          WHO <span style={{color: GOLD}}>NEVER PASSES.</span>
        </span>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1445, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 12, opacity: sig * 0.9}}>
        <Img src={staticFile('comedy/e2a_logo_2026_color.png')} style={{height: 60}} />
        <span style={{fontFamily: 'Inter', fontWeight: 700, fontSize: 24, letterSpacing: 4, color: '#fff', textShadow: '0 2px 8px rgba(0,0,0,0.7)'}}>E2A SPORTS</span>
      </div>
    </>
  );
};

export const ComedyEP002: React.FC<{hook?: Hook; clean?: boolean}> = ({hook = 'A', clean = false}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const shots = SHOTS(hook);
  const shot = shots.find((s) => t >= s.t0 && t < s.t1) ?? shots[shots.length - 1];
  const cam = shot.cam(t);
  const ball = ballAt(t);
  return (
    <AbsoluteFill style={{backgroundColor: '#111'}}>
      <Stage W={1080} H={1920} cam={cam} focus={shot.focus}>
        {CAST.map((who) => {
          const p = poseAt(who, t);
          return <Toon key={who} look={LOOKS[who]} pose={p} mouth={mouthOf(who, t)} skel={fk(p, LOOKS[who].build)} />;
        })}
        <Ball pos={ball.pos} spin={ball.spin} />
      </Stage>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.35) 100%)'}} />
      {clean ? null : (
        <>
          <Title t={t} />
          <Caption t={t} y={CAPTION_Y[shot.id] ?? 1330} shotStart={shot.t0} />
          <EndCard t={t} />
        </>
      )}
    </AbsoluteFill>
  );
};
