import React from 'react';
import {Composition, getInputProps} from 'remotion';
import {Breakdown} from './Breakdown';
import {FPS, H, W} from './theme';
import type {Episode} from './types';
import demo from './episodes/demo.json';

export const Root: React.FC = () => (
  <Composition
    id="Breakdown"
    component={Breakdown as React.FC<any>}
    width={W}
    height={H}
    fps={FPS}
    durationInFrames={Math.round(demo.durationSec * FPS)}
    defaultProps={{episode: demo as unknown as Episode}}
    calculateMetadata={({props}) => ({durationInFrames: Math.round((props.episode as Episode).durationSec * FPS)})}
  />
);
