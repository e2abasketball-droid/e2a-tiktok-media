// E2A YouTube Comedy — character lab: turnaround + expression sheet (QC of the cast).
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import '../theme';
import {AND1, ACE} from './characters';
import {POSE0, apply} from './pose';
import type {PosePatch} from './pose';
import {Stage} from './stage';
import {Toon} from './toon';

const EXPR: Record<string, PosePatch> = {
  neutral: {},
  shout: {face: {browL: 0.9, browR: 0.9, browTilt: -0.3, open: 0.9, wide: 1.2, lid: 0, smile: 0.2}, headPitch: -0.15},
  deadpan: {face: {lid: 0.45, browL: -0.1, browR: -0.1, smile: -0.15, wide: 0.9}},
  annoyed: {face: {browL: -0.8, browR: -0.8, browTilt: -0.9, lid: 0.3, squint: 0.5, smile: -0.6}},
  serious: {face: {browL: -0.35, browR: -0.35, browTilt: -0.4, lid: 0.25, smile: -0.2, wide: 0.85}},
  disbelief: {face: {browL: 0.8, browR: -0.2, browTilt: 0.5, lid: 0.05, open: 0.25, smile: -0.4}},
};

import * as MV from './moves';
const BODY: [string, PosePatch][] = [['FLEX', MV.FLEX], ['CHOP_UP', MV.CHOP_UP], ['CHOP_DOWN', MV.CHOP_DOWN], ['WAVE_A', MV.WAVE_A], ['WAVE_B', MV.WAVE_B], ['SHOT_SET', MV.SHOT_SET], ['SHOT_RELEASE', MV.SHOT_RELEASE], ['ARMS_UP', {...MV.STAND, ...MV.ARMS_UP}], ['SIT', MV.SIT], ['SIT_REST', MV.SIT_REST], ['SIT_POINT', MV.SIT_POINT], ['CROSSED', MV.CROSSED], ['READY', MV.READY], ['RELAXED', MV.RELAXED]];

export const ComedyLab: React.FC<{mode: 'turn' | 'faces' | 'body'; who: 'AND1' | 'ACE'; yaw?: number}> = ({mode, who, yaw: y0 = 0.5}) => {
  const f = useCurrentFrame();
  const look = who === 'AND1' ? AND1 : ACE;
  if (mode === 'turn') {
    const yaw = (f / 8) * (Math.PI / 2);
    const pose = apply(POSE0, {x: 0, z: -5, yaw});
    return (
      <AbsoluteFill>
        <Stage W={1080} H={1920} cam={{pos: [0, 1.3, -0.6], target: [0, 1.05, -5], fov: 34}} focus={[0, 1, -5]}>
          <Toon look={look} pose={pose} />
        </Stage>
      </AbsoluteFill>
    );
  }
  if (mode === 'body') {
    const [name, patch] = BODY[f % BODY.length];
    const pose = apply(POSE0, {...patch, x: 0, z: -5, yaw: y0});
    return (
      <AbsoluteFill>
        <Stage W={1080} H={1920} cam={{pos: [0, 1.2, -1.2], target: [0, 0.95, -5], fov: 40}} focus={[0, 1, -5]}>
          <Toon look={look} pose={pose} />
        </Stage>
        <div style={{position: 'absolute', top: 80, width: '100%', textAlign: 'center', color: 'white', fontFamily: 'Anton', fontSize: 70}}>{name}</div>
      </AbsoluteFill>
    );
  }
  const keys = Object.keys(EXPR);
  const k = keys[f % keys.length];
  const pose = apply(POSE0, {x: 0, z: -5, yaw: 0, ...EXPR[k], face: {...POSE0.face, ...(EXPR[k].face ?? {})}});
  return (
    <AbsoluteFill>
      <Stage W={1080} H={1920} cam={{pos: [0, 1.76, -3.3], target: [0, 1.72, -5], fov: 20}} focus={[0, 1.5, -5]}>
        <Toon look={look} pose={pose} />
      </Stage>
      <div style={{position: 'absolute', top: 80, width: '100%', textAlign: 'center', color: 'white', fontFamily: 'Anton', fontSize: 70}}>{k}</div>
    </AbsoluteFill>
  );
};
