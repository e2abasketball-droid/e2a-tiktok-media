// E2A Realism V3.2 (2026-11-22) — one entry point for "what does the V3.2 athlete look like at t" (Scene.tsx, the
// frame dumper of the mesh QC and the tests all call this, so the numbers are measured on the rendered code path).
// Players WITHOUT a V3.2 clip (e.g. extras of a play) fall back to the engine pose on the V3.2 mesh (V3 bridge).
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
import {clothV31, framesV31, motionV31} from '../realism-v3-1/motion.ts';
import type {BallState} from './motion32.ts';
import {ballState32, clothV32, framesV32, motionV32} from './motion32.ts';

export type Motion = 'engine' | 'v31' | 'v32';
export type Athlete32 = {
  sc: number; fr: V3Frame; pose: Pose; cloth: {jersey?: Cloth & {maxDisp?: number}; shorts?: Cloth & {maxDisp?: number}}; ball?: V3;
  debug?: {state: BallState; owner: string | null; hands: ('L' | 'R')[]; palm: [V3 | null, V3 | null]; feet: {g: V3; planted: boolean; support: number}[]; stage: string};
};
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
type BallCtx = {holder?: string | null; pos: V3; lag?: V3};

/** the athlete of player `id` at play time t on the rig `rig`, moved by `motion` (default: V3.2 library clip) */
export const athleteV32 = (play: Play, id: string, t: number, rig: RigV3, ball: BallCtx, motion: Motion = 'v32'): Athlete32 => {
  if (motion === 'v32') {
    const m = motionV32(play, id, t, rig);
    if (m) {
      const fr = framesV32(rig, m);
      const st = ballState32(m.clip, play, id, t);
      return {
        sc: m.c.scale, fr, pose: m.pose, cloth: clothV32(play, id, t, rig) ?? {}, ball: m.ball,
        debug: {...st, palm: m.arms.palm, feet: m.feet.map((f) => ({g: f.g, planted: f.planted && f.support > 0.5, support: f.support})), stage: m.body.shot.stage},
      };
    }
  }
  if (motion === 'v31') {
    const m = motionV31(play, id, t, rig);
    if (m) {
      const cl = clothV31(play, id, t, rig);
      return {sc: m.c.scale, fr: framesV31(rig, m), pose: m.pose, cloth: {jersey: cl, shorts: cl}, ball: m.ball};
    }
  }
  const pose = poseAt(play as PlayWithActions, id, t, {holder: ball.holder ?? undefined, pos: ball.pos, lag: ball.lag ?? ball.pos}, RIM);
  const sc = meshScale(rig, pose);
  const fr = bonesV3(rig, pose, sc, {pos: ball.pos, held: ball.holder === id});
  const cl = clothAt(play, id, t);
  return {sc, fr, pose, cloth: {jersey: cl, shorts: cl}};
};
