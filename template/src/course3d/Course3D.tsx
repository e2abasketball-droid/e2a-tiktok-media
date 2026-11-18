// E2A Course3D profile (private prototype, working copy only).
// Same 3D engine as Tactical3DV2 (Scene3D: court, athletes, ball, rig) and the same play JSON,
// but a COURSE profile: 16:9, one fixed elevated tactical camera, real play speed, and NONE of the
// reel layers (no pins, stamps, titles, subtitles, freeze labels or narration) that could give the answer.
// A clip covers play time [from, to]; the course uses setup = [0, read] and outcome = [read, end].
import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import type {PlayWithActions} from '../t3d/rig.ts';
import {Scene3D} from '../t3d/Scene';
import {camera3At} from '../t3d/camera3d.ts';
import type {CamKey3} from '../t3d/camera3d.ts';
import {useAssets} from '../t3d/Probe';
import '../theme';

export type Course3DProps = {play: PlayWithActions; from: number; to: number; cam?: CamKey3[]; mirrorX?: boolean};
// Orientation: the 3D world maps play x to three.js X and play y to -Z, so a camera behind half court that
// looks at the basket shows play -x ("left corner" in the play roles) on the RIGHT of the screen. The course
// board draws -x on the LEFT. The course profile therefore mirrors x (data only: textures, numbers and the logo
// stay readable) so that left and right match the board and the text descriptions.
export const mirrorPlay = (play: PlayWithActions): PlayWithActions => {
  const q = JSON.parse(JSON.stringify(play));
  for (const id in q.tracks) q.tracks[id] = q.tracks[id].map((k: number[]) => [k[0], -k[1], k[2], ...k.slice(3)]);
  for (const id in q.actions || {}) for (const a of q.actions[id]) { if (typeof a.face === 'number') a.face = Math.PI - a.face; if (typeof a.side === 'number') a.side = -a.side; }
  return q;
};
export const COURSE3D_PROFILE = {id: 'course3d-0.2', width: 1280, height: 720, fps: 30, layers: 'court+athletes+ball only'};
// Elevated "tactical" camera: behind half court looking at the basket, high enough to see every player
// and the spacing, low enough to read bodies (who is on whose hip). Fixed: no follow, no cuts.
export const TACTICAL_CAM: CamKey3[] = [{at: 0, rig: {type: 'orbit', target: [0, 4.9, 0], dist: 15.5, pitch: 42, yaw: 0, fov: 42}}];

export const course3dFrames = (p: Course3DProps, fps = COURSE3D_PROFILE.fps) => Math.round((p.to - p.from) * fps) + 1;

export const Course3D: React.FC<Course3DProps> = ({play: raw, from, to, cam, mirrorX = true}) => {
  const play = React.useMemo(() => (mirrorX ? mirrorPlay(raw) : raw), [raw, mirrorX]);
  const f = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const logo = useAssets();
  const pt = Math.min(to, from + f / fps);
  const c = camera3At(play, cam ?? TACTICAL_CAM, f / fps, pt);
  if (!logo) return null;
  return (
    <AbsoluteFill style={{background: '#050A15'}}>
      <Scene3D play={play} pt={pt} cam={c} W={width} H={height} logo={logo} />
    </AbsoluteFill>
  );
};
