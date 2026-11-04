// Virtual camera. A scene gets one move over its whole life; every layer inside reads the
// camera through context and scales the offset by its own depth, which gives parallax.
import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CameraMove} from './types';

export type Cam = {scale: number; x: number; y: number; punch: number};
const CamCtx = React.createContext<Cam>({scale: 1, x: 0, y: 0, punch: 0});

const MOVES: Record<CameraMove, {s: [number, number]; x: [number, number]; y: [number, number]}> = {
  'push-in': {s: [1.0, 1.14], x: [0, 0], y: [0, -20]},
  'pull-out': {s: [1.16, 1.02], x: [0, 0], y: [-10, 10]},
  'pan-left': {s: [1.12, 1.12], x: [60, -60], y: [0, 0]},
  'pan-right': {s: [1.12, 1.12], x: [-60, 60], y: [0, 0]},
  'tilt-up': {s: [1.12, 1.12], x: [0, 0], y: [-70, 50]},
  'tilt-down': {s: [1.12, 1.12], x: [0, 0], y: [50, -70]},
  drift: {s: [1.04, 1.08], x: [-20, 20], y: [10, -10]},
  static: {s: [1, 1], x: [0, 0], y: [0, 0]},
};

/** beats: frames (scene-local) where the camera punches in briefly */
export const Camera: React.FC<{move: CameraMove; durationInFrames: number; beats?: number[]; children: React.ReactNode}> = ({
  move,
  durationInFrames,
  beats = [],
  children,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const m = MOVES[move];
  const p = interpolate(frame, [0, Math.max(1, durationInFrames)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.33, 0, 0.2, 1),
  });
  let punch = 0;
  for (const b of beats) {
    const d = (frame - b) / fps;
    if (d >= 0 && d < 0.45) punch = Math.max(punch, Math.exp(-d * 9) * (1 - Math.exp(-d * 60)));
  }
  const cam: Cam = {
    scale: interpolate(p, [0, 1], m.s) * (1 + punch * 0.06),
    x: interpolate(p, [0, 1], m.x),
    y: interpolate(p, [0, 1], m.y),
    punch,
  };
  return <CamCtx.Provider value={cam}>{children}</CamCtx.Provider>;
};

export const useCam = () => React.useContext(CamCtx);

/** A layer at a given depth: 1 = moves with the camera, 0.3 = far background, 1.4 = foreground. */
export const Layer: React.FC<{depth?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
  depth = 1,
  children,
  style,
}) => {
  const c = useCam();
  const s = 1 + (c.scale - 1) * depth;
  return (
    <AbsoluteFill style={{transform: `translate(${c.x * depth}px, ${c.y * depth}px) scale(${s})`, transformOrigin: '50% 45%', ...style}}>
      {children}
    </AbsoluteFill>
  );
};
