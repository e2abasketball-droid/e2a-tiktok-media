// EVERY COURT HAS ONE — episode renderer (YouTube Shorts 1080x1920, 30 fps).
// Picture only: the audio master is mixed separately (tools/comedy/mix_ep.py) and muxed after.
import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import '../theme';
import {AND1, ACE} from './characters';
import {Ball, Stage} from './stage';
import {Toon, fk} from './toon';
import {CAPTION_Y, DURATION, FPS, HIGHLIGHT, LINES, SHOTS, ballAt, mouthOf, poseAt, swishAt} from './ep001';

export const comedyDuration = () => Math.round(DURATION * FPS);

const GOLD = '#E3BE68';

const Caption: React.FC<{t: number; y: number; shotStart: number}> = ({t, y, shotStart}) => {
  // a line shows while it is spoken (+0.2 s); it never carries over into the next shot
  const line = LINES.lines.find((l) => t >= l.words[0].start - 0.04 && t < l.end + 0.2 && !(shotStart > l.words[l.words.length - 1].end + 0.05));
  if (!line) return null;
  const hl = HIGHLIGHT.has(line.id);
  // words appear exactly when they are spoken (never early)
  const shown = line.words.filter((w) => t >= w.start - 0.04);
  if (!shown.length) return null;
  const first = line.words[0].start;
  const pop = interpolate(t, [first - 0.04, first + 0.08], [0.9, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const text = shown.map((w) => w.text).join(' ');
  const upper = hl ? text.toUpperCase() : text;
  return (
    <div style={{position: 'absolute', left: 150, right: 150, top: y, transform: `translateY(-50%) scale(${pop})`, textAlign: 'center'}}>
      <span
        style={{
          fontFamily: 'Anton',
          fontSize: hl ? 100 : 74,
          lineHeight: 1.08,
          letterSpacing: hl ? 1.5 : 0.5,
          color: hl ? GOLD : '#FFFFFF',
          WebkitTextStroke: '10px #05070C',
          paintOrder: 'stroke fill',
          textShadow: '0 6px 18px rgba(0,0,0,0.55)',
        }}
      >
        {upper}
      </span>
    </div>
  );
};

const Title: React.FC<{t: number}> = ({t}) => {
  if (t > 2.0) return null;
  const a = interpolate(t, [0, 0.12, 1.75, 1.95], [0, 1, 1, 0], {extrapolateRight: 'clamp'});
  const s = interpolate(t, [0, 0.18], [1.08, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 90, right: 90, top: 250, textAlign: 'center', opacity: a, transform: `scale(${s})`}}>
      <span style={{fontFamily: 'Anton', fontSize: 84, lineHeight: 1.05, color: '#fff', WebkitTextStroke: '9px #05070C', paintOrder: 'stroke fill', textShadow: '0 6px 18px rgba(0,0,0,0.5)'}}>
        EVERY COURT HAS <span style={{color: GOLD}}>THIS GUY...</span>
      </span>
    </div>
  );
};

const EndCard: React.FC<{t: number}> = ({t}) => {
  if (t < 21.95) return null;
  const a = interpolate(t, [21.95, 22.1], [0, 1], {extrapolateRight: 'clamp'});
  const s = interpolate(t, [21.95, 22.12], [1.12, 1], {extrapolateRight: 'clamp'});
  const sig = interpolate(t, [22.55, 22.8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <>
      <div style={{position: 'absolute', left: 100, right: 100, top: 1250, textAlign: 'center', opacity: a, transform: `scale(${s})`}}>
        <span style={{fontFamily: 'Anton', fontSize: 104, color: '#fff', WebkitTextStroke: '10px #05070C', paintOrder: 'stroke fill', textShadow: '0 6px 18px rgba(0,0,0,0.55)'}}>
          YOU KNOW <span style={{color: GOLD}}>THIS GUY.</span>
        </span>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1420, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 14, opacity: sig * 0.92}}>
        <Img src={staticFile('comedy/e2a_logo_2026_color.png')} style={{height: 72}} />
        <span style={{fontFamily: 'Inter', fontWeight: 700, fontSize: 26, letterSpacing: 4, color: '#fff', textShadow: '0 2px 8px rgba(0,0,0,0.7)'}}>E2A SPORTS</span>
      </div>
    </>
  );
};

export const ComedyShort: React.FC<{only?: string}> = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const shots = SHOTS();
  const shot = shots.find((s) => t >= s.t0 && t < s.t1) ?? shots[shots.length - 1];
  const cam = shot.cam(t);
  const pa = poseAt('AND1', t);
  const pc = poseAt('ACE', t);
  const ball = ballAt(t);
  return (
    <AbsoluteFill style={{backgroundColor: '#111'}}>
      <Stage W={1080} H={1920} cam={cam} focus={shot.focus} swish={swishAt(t)}>
        <Toon look={AND1} pose={pa} mouth={mouthOf('AND1', t)} skel={fk(pa, AND1.build)} />
        <Toon look={ACE} pose={pc} mouth={mouthOf('ACE', t)} skel={fk(pc, ACE.build)} />
        <Ball pos={ball.pos} spin={ball.spin} />
      </Stage>
      {/* soft vignette for a filmic look */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.35) 100%)'}} />
      <Title t={t} />
      <Caption t={t} y={CAPTION_Y[shot.id] ?? 1320} shotStart={shot.t0} />
      <EndCard t={t} />
    </AbsoluteFill>
  );
};
