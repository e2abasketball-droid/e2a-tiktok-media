import React from 'react';
import {GOLD, WHITE} from './theme';
import type {Pt} from './types';

export const SCALE = 17.6; // px per foot → 50ft = 880px
export const CW = 50 * SCALE;
export const CH = 47 * SCALE;
export const toPx = (p: Pt): Pt => [p[0] * SCALE, (47 - p[1]) * SCALE]; // basket at bottom

const L = 'rgba(255,255,255,0.75)';

/** Half court (FIBA-style proportions) drawn in SVG, basket at the bottom. */
export const Court: React.FC = () => {
  const bx = 25 * SCALE;
  const by = (47 - 5.25) * SCALE;
  const arcR = 22.1 * SCALE; // 6.75 m
  const laneW = 16 * SCALE;
  return (
    <svg width={CW} height={CH} style={{position: 'absolute', left: 0, top: 0}}>
      <rect width={CW} height={CH} fill="#102a52" />
      <rect x={0} y={0} width={CW} height={CH} fill="none" stroke={L} strokeWidth={5} />
      <rect x={(CW - laneW) / 2} y={CH - 19 * SCALE} width={laneW} height={19 * SCALE} fill="rgba(201,164,76,0.14)" stroke={L} strokeWidth={4} />
      <circle cx={bx} cy={CH - 19 * SCALE} r={6 * SCALE} fill="none" stroke={L} strokeWidth={4} />
      <path d={`M ${bx - arcR} ${CH} L ${bx - arcR} ${by} A ${arcR} ${arcR} 0 0 1 ${bx + arcR} ${by} L ${bx + arcR} ${CH}`} fill="none" stroke={L} strokeWidth={4} />
      <path d={`M ${bx - 4 * SCALE} ${by + 1.25 * SCALE} A ${4 * SCALE} ${4 * SCALE} 0 0 1 ${bx + 4 * SCALE} ${by + 1.25 * SCALE}`} fill="none" stroke={L} strokeWidth={4} />
      <line x1={bx - 3 * SCALE} x2={bx + 3 * SCALE} y1={CH - 4 * SCALE} y2={CH - 4 * SCALE} stroke={WHITE} strokeWidth={5} />
      <circle cx={bx} cy={by} r={0.75 * SCALE} fill="none" stroke={GOLD} strokeWidth={5} />
    </svg>
  );
};
