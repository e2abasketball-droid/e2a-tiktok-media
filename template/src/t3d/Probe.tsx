import React from 'react';
import {AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import playA from '../../tactical/plays/stagger-a-trail.json';
import type {PlayWithActions} from './rig.ts';
import {Scene3D} from './Scene';
import {camera3At} from './camera3d.ts';
import type {CamKey3} from './camera3d.ts';
import '../theme';

export const useAssets = () => {
  const [logo, setLogo] = React.useState<HTMLImageElement | undefined>();
  const [h] = React.useState(() => delayRender('assets'));
  React.useEffect(() => {
    const img = new Image();
    img.src = staticFile('e2a_logo_white.png');
    Promise.all([new Promise((r) => (img.onload = r)), document.fonts.load('150px Anton')]).then(() => {
      setLogo(img);
      continueRender(h);
    });
  }, [h]);
  return logo;
};

export const Probe: React.FC<{cam?: string}> = ({cam = 'broadcast'}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const logo = useAssets();
  const play = playA as unknown as PlayWithActions;
  const pt = 0.6 + f / fps;
  const keys: Record<string, CamKey3[]> = {
    broadcast: [{at: 0, rig: {type: 'orbit', target: {follow: ['O2', 'X2'], z: 1.0}, dist: 11, pitch: 58, yaw: -20, fov: 38}}],
    pov: [{at: 0, rig: {type: 'pov', behind: 'X2', look: 'O2', back: 2.6, height: 2.15, side: 0.45, fov: 50, lookZ: 1.0}}],
    low: [{at: 0, rig: {type: 'orbit', target: {follow: 'O2', z: 1.1}, dist: 5.5, pitch: 80, yaw: 150, fov: 45}}],
    back: [{at: 0, rig: {type: 'orbit', target: {follow: 'X2', z: 0.9}, dist: 2.6, pitch: 82, yaw: 180, fov: 40}}],
    top: [{at: 0, rig: {type: 'orbit', target: [-1.5, 5.5, 0], dist: 24, pitch: 0, yaw: 0, fov: 40}}],
  };
  const c = camera3At(play, keys[cam], f / fps, pt);
  if (!logo) return null;
  return (
    <AbsoluteFill style={{background: '#050A15'}}>
      <Scene3D play={play} pt={pt} cam={c} W={1080} H={1920} logo={logo} />
    </AbsoluteFill>
  );
};
