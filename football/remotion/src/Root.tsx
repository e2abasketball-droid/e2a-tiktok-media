// E2A Football — Remotion root. Composition ids carry the FB prefix (football/config/division.json).
import React from 'react';
import {Composition} from 'remotion';
import {FBTactical3D} from './FBTactical3D';
import {thirdManRun} from './episodes/thirdManRun';
import {simpleShortCorner} from './episodes/simpleShortCorner';
import {shortCornerCutback, shortCornerCutbackHookB, shortCornerCutbackV04} from './episodes/shortCornerCutback';
import {nearPostDecoyV05, nearPostDecoyV06} from './episodes/nearPostDecoy';
import {offBallTimingV07, offBallTimingV07Wide, offBallTimingV08} from './episodes/offBallTiming';
import {cornerRateTest, narratedV09, narratedV09Silent} from './episodes/narratedV09';

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
    {/* FB-SETPIECE-001 V05 (owner directive V05): mixed defence first, near-post decoy + late arrival; silent cut */}
    <Composition id="FBSetPiece001V05" component={FBTactical3D} durationInFrames={Math.round(nearPostDecoyV05.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: nearPostDecoyV05}} />
    <Composition id="FBSetPiece001V06" component={FBTactical3D} durationInFrames={Math.round(nearPostDecoyV06.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: nearPostDecoyV06}} />
    {/* FB-SETPIECE-001 V07 (owner directive V07): off-ball timing — master timeline, box-first camera + corner inset */}
    <Composition id="FBSetPiece001V07" component={FBTactical3D} durationInFrames={Math.round(offBallTimingV07.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: offBallTimingV07}} />
    <Composition id="FBSetPiece001V08" component={FBTactical3D} durationInFrames={Math.round(offBallTimingV08.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: offBallTimingV08}} />
    {/* FB-SETPIECE-001 V09 (owner directive V09): narrated release candidate (Deuce, music, subtitles) */}
    <Composition id="FBSetPiece001V09" component={FBTactical3D} durationInFrames={Math.round(narratedV09.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: narratedV09}} />
    <Composition id="FBSetPiece001V09Silent" component={FBTactical3D} durationInFrames={Math.round(narratedV09Silent.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: narratedV09Silent}} />
    {[1, 0.9, 0.85, 0.8].map((k) => (
      <Composition key={k} id={`FBSetPiece001V09Rate${Math.round(k * 100)}`} component={FBTactical3D} durationInFrames={Math.round(cornerRateTest(k).duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: cornerRateTest(k)}} />
    ))}
    <Composition id="FBSetPiece001V07WideTest" component={FBTactical3D} durationInFrames={Math.round(offBallTimingV07Wide.duration * 30)} fps={30} width={1080} height={1920} defaultProps={{episode: offBallTimingV07Wide}} />
  </>
);
