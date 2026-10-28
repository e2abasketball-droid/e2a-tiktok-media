import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';

export const FPS = 30;
export const DURATION = 1660; // ~55.3 s: narration (54.1 s) + short tail

export const Root: React.FC = () => (
  <Composition
    id="Main"
    component={Main}
    durationInFrames={DURATION}
    fps={FPS}
    width={1080}
    height={1920}
  />
);
