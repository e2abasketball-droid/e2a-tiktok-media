// E2A Realism V3.3 (2026-11-22) — one entry point for "what does the V3.3 athlete look like at t" (Scene.tsx, the QC
// and the frame dumper call this, so what is measured is what is rendered). Players WITHOUT a V3.3 clip fall back to the
// engine pose on the same mesh (counted as 'legacy-fallback' by sourceOf33 / the QA, never silently).
import type {V3} from '../../tactical/geometry.ts';
import type {Play} from '../../tactical/play.ts';
import {FIBA} from '../../tactical/geometry.ts';
import {poseAt} from '../rig.ts';
import type {PlayWithActions, Pose} from '../rig.ts';
import {meshScale} from '../skelclip.ts';
import type {Cloth} from '../cloth2.ts';
import {clothAt} from '../cloth2.ts';
import type {RigV3, V3Frame} from '../realism-v3/athleteV3.ts';
import {bonesV3} from '../realism-v3/athleteV3.ts';
import type {BallState} from './motion33.ts';
import {ballState33, clothV33, framesV33, motionV33} from './motion33.ts';
import {source33} from './clips33.ts';

export type Athlete33 = {
  sc: number; fr: V3Frame; pose: Pose; cloth: {jersey?: Cloth & {maxDisp?: number}; shorts?: Cloth & {maxDisp?: number}}; ball?: V3;
  source: 'v33-compiled' | 'v33-compat-script' | 'legacy-fallback';
  debug?: {state: BallState; owner: string | null; hands: ('L' | 'R')[]; palm: [V3 | null, V3 | null]; feet: {g: V3; planted: boolean; support: number}[]; stage: string; contact?: string};
};
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
type BallCtx = {holder?: string | null; pos: V3; lag?: V3};

export const athleteV33 = (play: Play, id: string, t: number, rig: RigV3, ball: BallCtx): Athlete33 => {
  const m = motionV33(play, id, t, rig);
  if (m) {
    const fr = framesV33(rig, m);
    const st = ballState33(m.clip, play, id, t);
    const src = source33(play, id);
    return {
      sc: m.c.scale, fr, pose: m.pose, cloth: clothV33(play, id, t, rig) ?? {}, ball: m.ball, source: src === 'none' ? 'legacy-fallback' : src,
      debug: {...st, palm: m.arms.palm, feet: m.feet.map((f) => ({g: f.g, planted: f.planted && f.support > 0.5, support: f.support})), stage: m.body.shot.stage, contact: m.arms.contact},
    };
  }
  const pose = poseAt(play as PlayWithActions, id, t, {holder: ball.holder ?? undefined, pos: ball.pos, lag: ball.lag ?? ball.pos}, RIM);
  const sc = meshScale(rig, pose);
  const fr = bonesV3(rig, pose, sc, {pos: ball.pos, held: ball.holder === id});
  const cl = clothAt(play, id, t);
  return {sc, fr, pose, cloth: {jersey: cl, shorts: cl}, source: 'legacy-fallback'};
};
