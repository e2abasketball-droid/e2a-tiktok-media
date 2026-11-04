// Backdrops for scenes without real footage. They are built from layers at different depths,
// so the virtual camera produces parallax instead of sliding a flat card.
import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Layer, useCam} from './camera';
import {BODY, GOLD, NAVY, NAVY_DEEP, WHITE} from './brand';
import type {Backdrop, Layout, Media, PhotoBg} from './types';

const Crowd: React.FC<{seed: string}> = ({seed}) => {
  const frame = useCurrentFrame();
  const dots = React.useMemo(
    () =>
      new Array(260).fill(0).map((_, i) => ({
        x: random(`${seed}x${i}`) * 1300 - 110,
        y: 260 + random(`${seed}y${i}`) * 620,
        r: 3 + random(`${seed}r${i}`) * 9,
        o: 0.12 + random(`${seed}o${i}`) * 0.3,
        f: random(`${seed}f${i}`),
      })),
    [seed],
  );
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', filter: 'blur(2.5px)'}}>
      {dots.map((d, i) => {
        // occasional camera flashes in the stands
        const flash = d.f > 0.985 && Math.floor((frame + i * 7) / 9) % 11 === 0;
        return <circle key={i} cx={d.x} cy={d.y} r={flash ? d.r * 1.8 : d.r} fill={flash ? WHITE : '#9DB0D6'} opacity={flash ? 0.9 : d.o} />;
      })}
    </svg>
  );
};

const Floor: React.FC = () => (
  <div style={{position: 'absolute', left: -500, right: -500, top: 880, height: 1900, perspective: 1100, perspectiveOrigin: '50% 0%'}}>
    <div
      style={{
        position: 'absolute',
        inset: 0,
        transform: 'rotateX(68deg)',
        transformOrigin: '50% 100%',
        background: `linear-gradient(180deg, #1A3A70 0%, ${NAVY} 70%)`,
      }}
    >
      <svg viewBox="0 0 94 50" width="100%" height="100%" preserveAspectRatio="none" style={{position: 'absolute', opacity: 0.55}}>
        <g fill="none" stroke={GOLD} strokeWidth={0.25}>
          <rect x={2} y={2} width={90} height={46} />
          <line x1={47} y1={2} x2={47} y2={48} />
          <circle cx={47} cy={25} r={6} />
          <rect x={2} y={17} width={19} height={16} />
          <rect x={73} y={17} width={19} height={16} />
          <path d="M2 4 H6 A22 22 0 0 1 6 46 H2" />
          <path d="M92 4 H88 A22 22 0 0 0 88 46 H92" />
        </g>
      </svg>
      <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 10%, rgba(255,255,255,0.22), transparent 55%)'}} />
    </div>
  </div>
);

const Beams: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{mixBlendMode: 'screen'}}>
      {[-1, 1].map((side) => (
        <div
          key={side}
          style={{
            position: 'absolute',
            top: -200,
            left: 540 + side * 260 - 160,
            width: 320,
            height: 1700,
            transformOrigin: '50% 0%',
            transform: `rotate(${side * (18 + Math.sin(frame / 50 + side) * 3)}deg)`,
            background: 'linear-gradient(180deg, rgba(255,240,200,0.28), rgba(255,240,200,0) 85%)',
            filter: 'blur(28px)',
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

const Haze: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at ${50 + Math.sin(frame / 70) * 12}% 55%, rgba(201,162,77,0.14), transparent 60%)`,
      }}
    />
  );
};

export const BackdropView: React.FC<{kind: Backdrop; seed: string}> = ({kind, seed}) => {
  if (kind === 'navy') {
    return (
      <AbsoluteFill style={{background: `radial-gradient(circle at 50% 38%, #18366B 0%, ${NAVY_DEEP} 70%)`}}>
        <Layer depth={0.5}>
          <Haze />
        </Layer>
      </AbsoluteFill>
    );
  }
  if (kind === 'archive') {
    return (
      <AbsoluteFill style={{background: '#16130F'}}>
        <Layer depth={0.4}>
          <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, rgba(201,162,77,0.25), transparent 65%)'}} />
        </Layer>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{background: `linear-gradient(180deg, ${NAVY_DEEP} 0%, #0E2350 45%, ${NAVY_DEEP} 100%)`}}>
      <Layer depth={0.35}>
        <Crowd seed={seed} />
      </Layer>
      {kind === 'spotlight' || kind === 'arena' ? (
        <Layer depth={0.6}>
          <Beams />
        </Layer>
      ) : null}
      <Layer depth={1.25}>
        <Floor />
      </Layer>
      <Layer depth={0.8}>
        <Haze />
      </Layer>
    </AbsoluteFill>
  );
};

/** Real photo or clip, cover-fit (never stretched), with a blurred copy behind for depth. */
export const MediaView: React.FC<{media: Media}> = ({media}) => {
  const c = useCam();
  const [fx, fy] = media.focus ?? [0.5, 0.45];
  const src = staticFile(media.src);
  const fit: React.CSSProperties = {width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${fx * 100}% ${fy * 100}%`};
  const isVideo = /\.(mp4|mov|webm)$/i.test(media.src);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Layer depth={0.4} style={{filter: 'blur(30px) brightness(0.5)'}}>
        {isVideo ? <OffthreadVideo src={src} muted style={fit} startFrom={Math.round((media.startFrom ?? 0) * 30)} /> : <Img src={src} style={fit} />}
      </Layer>
      {media.fit === 'print' && !isVideo ? (
        <Layer depth={1.15}>
          <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
            <div
              style={{
                width: 880,
                marginTop: -120,
                padding: 18,
                background: '#EFE6D2',
                boxShadow: '0 40px 90px rgba(0,0,0,0.7), 0 0 0 2px rgba(201,162,77,0.6)',
                transform: `rotate(${media.tilt ?? -2}deg)`,
              }}
            >
              <Img src={src} style={{width: '100%', display: 'block', filter: 'sepia(0.25) contrast(1.05)'}} />
            </div>
          </AbsoluteFill>
        </Layer>
      ) : (
        <Layer depth={1}>
          {isVideo ? <OffthreadVideo src={src} muted style={fit} startFrom={Math.round((media.startFrom ?? 0) * 30)} /> : <Img src={src} style={fit} />}
        </Layer>
      )}
      <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(11,28,61,0.55) 0%, transparent 25%, transparent 55%, rgba(11,28,61,0.85) 100%)`, opacity: 0.9 + c.punch * 0.1}} />
    </AbsoluteFill>
  );
};

const GRADE: Record<NonNullable<PhotoBg['treatment']>, {img: string; wash: string; washBlend: React.CSSProperties['mixBlendMode']; washO: number}> = {
  // navy/gold brand grade: the photo turns into a duotone that every graphic reads well on
  duotone: {img: 'grayscale(1) contrast(1.2) brightness(1.35)', wash: '#1B3F86', washBlend: 'multiply', washO: 0.85},
  tint: {img: 'saturate(0.95) contrast(1.05)', wash: NAVY_DEEP, washBlend: 'normal', washO: 0.3},
  blur: {img: 'blur(16px) saturate(0.8) brightness(0.8)', wash: NAVY_DEEP, washBlend: 'normal', washO: 0.45},
};

/** A real photo/clip graded as the plate behind a graphic scene (stat, scoreboard, headline...). */
export const PhotoBackdrop: React.FC<{media: PhotoBg; layout?: Layout}> = ({media, layout = 'center'}) => {
  const frame = useCurrentFrame();
  const g = GRADE[media.treatment ?? 'duotone'];
  const [fx, fy] = media.focus ?? [0.5, 0.4];
  const src = staticFile(media.src);
  const isVideo = /\.(mp4|mov|webm)$/i.test(media.src);
  const fit: React.CSSProperties = {width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${fx * 100}% ${fy * 100}%`, filter: g.img};
  // darken where the graphic sits so it always reads
  const shade =
    layout === 'low'
      ? 'linear-gradient(180deg, rgba(6,15,34,0.25) 0%, rgba(6,15,34,0.1) 30%, rgba(6,15,34,0.85) 62%, rgba(6,15,34,0.95) 100%)'
      : layout === 'high'
        ? 'linear-gradient(180deg, rgba(6,15,34,0.9) 0%, rgba(6,15,34,0.75) 45%, rgba(6,15,34,0.15) 72%, rgba(6,15,34,0.7) 100%)'
        : 'radial-gradient(ellipse 60% 35% at 50% 40%, rgba(6,15,34,0.45), transparent 75%), linear-gradient(180deg, rgba(6,15,34,0.45), transparent 25%, transparent 62%, rgba(6,15,34,0.8))';
  return (
    <AbsoluteFill style={{background: NAVY_DEEP}}>
      <Layer depth={0.75}>
        {isVideo ? <OffthreadVideo src={src} muted style={fit} startFrom={Math.round((media.startFrom ?? 0) * 30)} /> : <Img src={src} style={fit} />}
      </Layer>
      <AbsoluteFill style={{background: g.wash, mixBlendMode: g.washBlend, opacity: g.washO}} />
      {media.treatment !== 'tint' && media.treatment !== 'blur' && (
        // gold catches the highlights of the duotone, drifting slowly
        <AbsoluteFill
          style={{
            mixBlendMode: 'screen',
            opacity: 0.4,
            background: `radial-gradient(ellipse 70% 50% at ${40 + Math.sin(frame / 60) * 15}% 30%, ${GOLD}, transparent 70%)`,
          }}
        />
      )}
      <AbsoluteFill style={{background: shade}} />
    </AbsoluteFill>
  );
};

/** Framed photo card (picture-in-picture) that slides in beside a graphic. */
export const Inset: React.FC<{media: Media; at: number; corner?: 'tl' | 'tr'; caption?: string}> = ({media, at, corner = 'tl', caption}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - at * fps, fps, config: {damping: 14, mass: 0.6}});
  if (frame < at * fps) return null;
  const left = corner === 'tl';
  const [fx, fy] = media.focus ?? [0.5, 0.35];
  return (
    <div
      style={{
        position: 'absolute',
        top: 260,
        [left ? 'left' : 'right']: left ? 70 : 170,
        width: 400,
        padding: 12,
        background: WHITE,
        boxShadow: '0 30px 70px rgba(0,0,0,0.65), 0 0 0 3px rgba(201,162,77,0.8)',
        transform: `translateX(${(1 - s) * (left ? -520 : 520)}px) rotate(${(left ? -4 : 4) * s}deg)`,
      }}
    >
      <Img src={staticFile(media.src)} style={{width: '100%', height: 300, objectFit: 'cover', objectPosition: `${fx * 100}% ${fy * 100}%`, display: 'block'}} />
      {caption && <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 24, letterSpacing: 3, color: NAVY, textTransform: 'uppercase', paddingTop: 10, textAlign: 'center'}}>{caption}</div>}
    </div>
  );
};
