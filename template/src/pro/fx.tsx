// Finishing layers: film grain, vignette, light leak and the transition flashes.
import React from 'react';
import {AbsoluteFill, interpolate, random, useCurrentFrame} from 'remotion';

export const Grain: React.FC<{amount: number}> = ({amount}) => {
  const frame = useCurrentFrame();
  if (amount <= 0) return null;
  // a new noise pattern every 2 frames reads as film, every frame reads as static
  const seed = Math.floor(frame / 2) % 24;
  const dx = Math.round(random(`gx${seed}`) * 200);
  const dy = Math.round(random(`gy${seed}`) * 200);
  return (
    <AbsoluteFill style={{opacity: amount * 0.35, mixBlendMode: 'overlay', pointerEvents: 'none'}}>
      <svg width={1080} height={1920}>
        <filter id={`g${seed}`} x="0" y="0">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={seed} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect x={-dx} y={-dy} width={1300} height={2140} filter={`url(#g${seed})`} />
      </svg>
    </AbsoluteFill>
  );
};

export const Vignette: React.FC<{amount: number}> = ({amount}) => (
  <AbsoluteFill
    style={{background: `radial-gradient(ellipse at 50% 45%, transparent 45%, rgba(0,0,0,${0.75 * amount}) 100%)`, pointerEvents: 'none'}}
  />
);

export const LightLeak: React.FC = () => {
  const frame = useCurrentFrame();
  const x = interpolate(Math.sin(frame / 95), [-1, 1], [-10, 110]);
  return (
    <AbsoluteFill
      style={{
        mixBlendMode: 'screen',
        opacity: 0.22,
        background: `radial-gradient(ellipse 45% 30% at ${x}% 12%, rgba(255,190,90,0.9), transparent 70%)`,
        pointerEvents: 'none',
      }}
    />
  );
};

/** White/gold flash over a cut. `age` = seconds since the cut. */
export const Flash: React.FC<{age: number; color?: string; strength?: number}> = ({age, color = '#FFFFFF', strength = 0.85}) => {
  if (age < 0 || age > 0.35) return null;
  const o = strength * Math.exp(-age * 14);
  return <AbsoluteFill style={{background: color, opacity: o, mixBlendMode: 'screen', pointerEvents: 'none'}} />;
};
