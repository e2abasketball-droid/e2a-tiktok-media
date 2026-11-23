// E2A Football — Remotion root. Composition ids carry the FB prefix (football/config/division.json).
import React from 'react';
import {Composition} from 'remotion';
import {FBTactical3D} from './FBTactical3D';
import {thirdManRun} from './episodes/thirdManRun';

export const Root: React.FC = () => (
  <>
    <Composition id="FBTactical3D" component={FBTactical3D} durationInFrames={Math.round(thirdManRun.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: thirdManRun}} />
  </>
);
