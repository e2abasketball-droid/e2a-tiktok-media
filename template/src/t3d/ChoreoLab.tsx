// Choreography review (brief §8 pass 1): the master take without overlays, from a fixed camera, with a HUD of the
// play clock, which foot is on the floor and the named milestones. Render top / side / three-quarter separately.
//   npx remotion render src/index.ts ChoreoLab out.mp4 --props='{"play":<play json>,"view":"side","t0":1.1,"t1":3.4,"rate":0.25}'
import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import type {PlayWithActions} from './rig.ts';
import {Scene3D} from './Scene';
import {camera3At} from './camera3d.ts';
import type {CamKey3} from './camera3d.ts';
import {useAssets} from './Probe';
import {footAt} from './choreo.ts';
import type {ChoreoPlay} from './choreo.ts';

export type ChoreoLabProps = {play: PlayWithActions; view: string; t0: number; t1: number; rate: number; cams?: Record<string, CamKey3[]>};

const VIEWS: Record<string, CamKey3[]> = {
  top: [{at: 0, rig: {type: 'orbit', target: {follow: ['O1', 'X1'], z: 0, window: 0.6}, dist: 9, pitch: 0, yaw: 0, fov: 40}}],
  side: [{at: 0, rig: {type: 'orbit', target: {follow: 'O1', z: 0.9, window: 0.6}, dist: 7.5, pitch: 84, yaw: 90, fov: 36}}],
  front: [{at: 0, rig: {type: 'orbit', target: {follow: 'O1', z: 1.0, window: 0.6}, dist: 7.5, pitch: 80, yaw: 180, fov: 36}}],
  tq: [{at: 0, rig: {type: 'orbit', target: {follow: ['O1', 'X1'], z: 0.8, window: 0.6}, dist: 7.0, pitch: 62, yaw: 20, fov: 42}}],
  back: [{at: 0, rig: {type: 'orbit', target: {follow: ['O1', 'X1'], z: 1.0, window: 0.6}, dist: 6.2, pitch: 70, yaw: 0, fov: 44}}],
};

export const ChoreoLab: React.FC<ChoreoLabProps> = ({play, view, t0, t1, rate, cams}) => {
  const f = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const logo = useAssets();
  const pt = Math.min(t1, t0 + (f / fps) * rate);
  const c = camera3At(play, (cams ?? VIEWS)[view], 0, pt);
  if (!logo) return null;
  const cp = play as unknown as ChoreoPlay;
  const marks = Object.entries(play.marks).filter(([, v]) => Math.abs(v - pt) < 0.5 / fps * rate + 1e-6 || (pt >= v && pt - v < 0.12)).map(([k]) => k);
  const feet = (id: string) => {
    const ch = cp.choreo?.[id];
    if (!ch) return '';
    const s = [footAt(ch, 0, pt), footAt(ch, 1, pt)];
    return `${id}  L ${s[0].planted ? (s[0].pitch > 0.05 ? 'heel up' : 'DOWN') : 'air'} · R ${s[1].planted ? (s[1].pitch > 0.05 ? 'heel up' : 'DOWN') : 'air'}`;
  };
  return (
    <AbsoluteFill style={{background: '#050A15'}}>
      <Scene3D play={play} pt={pt} cam={c} W={width} H={height} logo={logo} />
      <div style={{position: 'absolute', left: 24, top: 18, color: '#fff', font: '600 30px monospace', textShadow: '0 2px 4px #000', lineHeight: 1.35}}>
        <div>
          {play.id} · {view} · t={pt.toFixed(3)} s · ×{rate}
        </div>
        <div>{feet('O1')}</div>
        <div>{feet('X1')}</div>
        <div style={{color: '#E0B455'}}>{marks.join('  ')}</div>
      </div>
    </AbsoluteFill>
  );
};
