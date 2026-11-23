// E2A Football — Remotion root. Composition ids carry the FB prefix (football/config/division.json).
import React from 'react';
import {Composition} from 'remotion';
import {FBTactical3D} from './FBTactical3D';
import {thirdManRun} from './episodes/thirdManRun';
import {simpleShortCorner} from './episodes/simpleShortCorner';
import {shortCornerCutback, shortCornerCutbackHookB, shortCornerCutbackV04} from './episodes/shortCornerCutback';

export const Root: React.FC = () => (
  <>
    <Composition id="FBTactical3D" component={FBTactical3D} durationInFrames={Math.round(thirdManRun.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: thirdManRun}} />
    <Composition id="FBTactical3DSilent" component={FBTactical3D} durationInFrames={Math.round(thirdManRun.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: {...thirdManRun, music: undefined}}} />
    {/* Set Pieces Studio — FB-SETPIECE-001 (silent until the voice is approved) */}
    <Composition id="FBSetPiece001" component={FBTactical3D} durationInFrames={Math.round(simpleShortCorner.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: simpleShortCorner}} />
    {/* FB-SETPIECE-001 V03 (owner review of V02): the short corner cutback, 11 v 11, ends in a goal; silent cut */}
    <Composition id="FBSetPiece001V03" component={FBTactical3D} durationInFrames={Math.round(shortCornerCutback.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: shortCornerCutback}} />
    <Composition id="FBSetPiece001V04" component={FBTactical3D} durationInFrames={Math.round(shortCornerCutbackV04.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: shortCornerCutbackV04}} />
    <Composition id="FBSetPiece001V03HookB" component={FBTactical3D} durationInFrames={Math.round(shortCornerCutbackHookB.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: shortCornerCutbackHookB}} />
  </>
);
