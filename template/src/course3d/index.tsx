// Course3D entry (V4 common master, 2026-11-15): registers only the clean 16:9 course profile, so a course
// render does not bundle the reels. The play comes from the props (same play JSON as the 9:16 social episode),
// so one play id + revision feeds both outputs. Ported from the film-room v0.7 prototype (Spain A only).
import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {Course3D, COURSE3D_PROFILE, course3dFrames} from './Course3D';
import spainA from '../../tactical/plays/spain-a-roll.json';

const CourseRoot: React.FC = () => (
  <Composition id="Course3D" component={Course3D} fps={COURSE3D_PROFILE.fps} width={COURSE3D_PROFILE.width} height={COURSE3D_PROFILE.height}
    durationInFrames={61} defaultProps={{play: spainA as any, from: 0, to: 2.0}}
    calculateMetadata={({props}) => ({durationInFrames: course3dFrames(props)})} />
);
registerRoot(CourseRoot);
