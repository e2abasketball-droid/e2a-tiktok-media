// EVERY COURT HAS ONE — EP002 "THE BALL HOG"
// Timeline built AROUND the locked dialogue (comedy/ep002/lines.json): body keys, face keys,
// blinks, ball, cameras and captions. All times in seconds (episode clock, 30 fps). No edit cuts:
// the timeline was authored directly at its final length.
import * as THREE from 'three';
import {POSE0, evalKeys, clamp, lerp, smooth} from './pose';
import type {Key, Pose, PosePatch, Face} from './pose';
import * as MV from './moves';
import {ballInHand, fk, D} from './toon';
import type {Look} from './toon';
import type {Cam} from './stage';
import {RIM} from './gym';
import {ACE, AND1, BUCKETS, DEF1, DEF2} from './characters';
import lines from '../../comedy/ep002/lines.json';

export const FPS = 30;
export const DURATION = 30.0;

export type Who = 'BUCKETS' | 'ACE' | 'DEF1' | 'DEF2' | 'AND1';
export const CAST: Who[] = ['BUCKETS', 'ACE', 'DEF1', 'DEF2', 'AND1'];
export const LOOKS: Record<Who, Look> = {BUCKETS, ACE, DEF1, DEF2, AND1};
type Speaker = 'BUCKETS' | 'ACE';
export const LINES = lines as {lines: {id: string; who: Speaker; start: number; end: number; text: string; words: {text: string; start: number; end: number}[]}[]; mouth: Record<string, number[]>};

type V2 = [number, number];
const faceTo = (from: V2, to: V2) => Math.atan2(to[0] - from[0], to[1] - from[1]);
const rot = (v: V2, a: number): V2 => [v[0] * Math.cos(a) + v[1] * Math.sin(a), -v[0] * Math.sin(a) + v[1] * Math.cos(a)];
const add = (a: V2, b: V2, k = 1): V2 => [a[0] + b[0] * k, a[1] + b[1] * k];
const norm = (v: V2): V2 => {
  const l = Math.hypot(v[0], v[1]);
  return [v[0] / l, v[1] / l];
};

// ---------- blocking (x, z on the floor) ----------
export const BK: V2 = [3.3, -6.0]; // BUCKETS, right wing, never moves his feet much (he never goes anywhere)
export const ACE0: V2 = [-0.95, -2.25]; // ACE, alone under the basket (left block)
export const ACE1: V2 = [-0.62, -2.7]; // after his one small step toward BUCKETS
const RIM2: V2 = [RIM.x, RIM.z];
const dBK = norm([ACE0[0] - BK[0], ACE0[1] - BK[1]]);
export const DEF1P = add(BK, rot(dBK, 0.92), 0.9);
export const DEF2P = add(BK, rot(dBK, -0.92), 0.9);
export const AND1P: V2 = [-6.2, -9.6]; // silent cameo: far sideline, arms crossed, watching

const Y_BK_ACE = faceTo(BK, ACE0);
const Y_BK_RIM = faceTo(BK, RIM2);
const Y_ACE_BK = faceTo(ACE0, BK);
const Y_ACE1_BK = faceTo(ACE1, BK);
const Y_ACE_REB = faceTo(ACE0, [0.75, 0.6]); // toward the wall rebound
const Y_D1 = faceTo(DEF1P, BK);
const Y_D2 = faceTo(DEF2P, BK);

const K = (t: number, p: PosePatch, ease?: Key['ease']): Key => ({t, p, ease});
const F = (t: number, name: keyof typeof MV.FACES | Partial<Face>, extra: Partial<Face> = {}, ease?: Key['ease']): Key => ({
  t,
  p: {face: {...(typeof name === 'string' ? MV.FACES[name] : name), ...extra}},
  ease,
});

// ---------- EP002 poses (ball handling) ----------
/** ball held at the chest with both hands */
const HOLD: PosePatch = {...MV.STAND, lShPitch: 0.62, rShPitch: 0.62, lShOut: 0.02, rShOut: 0.02, lShTwist: -0.55, rShTwist: -0.55, lElbow: 1.55, rElbow: 1.55};
/** BUCKETS carries it lower (belly), so his face stays clear in close-ups */
const HOLD_BK: PosePatch = {...HOLD, lShPitch: 0.42, rShPitch: 0.42, lElbow: 1.4, rElbow: 1.4, lShTwist: -0.6, rShTwist: -0.6};
/** ball protected high, at the chin, elbows out (BUCKETS in the double team) */
const HOLD_HIGH: PosePatch = {...MV.STAND, lShPitch: 0.72, rShPitch: 0.72, lShOut: 0.5, rShOut: 0.5, lShTwist: -0.75, rShTwist: -0.75, lElbow: 1.6, rElbow: 1.6, lHip: 0.15, rHip: 0.15, lKnee: 0.25, rKnee: 0.25};
/** ball held low at the waist (ACE, end) */
const HOLD_LOW: PosePatch = {...MV.RELAXED, lShPitch: 0.3, rShPitch: 0.3, lShOut: 0.0, rShOut: 0.0, lShTwist: -0.45, rShTwist: -0.45, lElbow: 1.15, rElbow: 1.15};
/** two-hand catch target, arms out in front */
const CATCH: PosePatch = {lShPitch: 1.15, rShPitch: 1.15, lShOut: 0.12, rShOut: 0.12, lShTwist: -0.35, rShTwist: -0.35, lElbow: 0.75, rElbow: 0.75};
/** "pass it here": both arms forward, palms open (ACE) */
const HANDS_OPEN: PosePatch = {lShPitch: 1.0, rShPitch: 1.0, lShOut: 0.3, rShOut: 0.3, lShTwist: 0.35, rShTwist: 0.35, lElbow: 0.45, rElbow: 0.45};
/** overhead pass wind-up (ball behind the head) and thrust */
const OVER_UP: PosePatch = {lShPitch: 2.75, rShPitch: 2.75, lShOut: 0.28, rShOut: 0.28, lShTwist: -0.4, rShTwist: -0.4, lElbow: 1.35, rElbow: 1.35, spineBend: -0.12, headPitch: -0.08};
const OVER_OUT: PosePatch = {lShPitch: 1.95, rShPitch: 1.95, lShOut: 0.12, rShOut: 0.12, lShTwist: -0.35, rShTwist: -0.35, lElbow: 0.35, rElbow: 0.35, spineBend: 0.14, lean: 0.06};
/** defender: wide stance, both arms straight up */
const DEF_UP: PosePatch = {...MV.READY, lean: 0.0, spineBend: -0.04, lShPitch: 3.0, rShPitch: 3.0, lShOut: 0.3, rShOut: 0.3, lShTwist: 0, rShTwist: 0, lElbow: 0.25, rElbow: 0.25, lHipOut: 0.22, rHipOut: 0.22};
const DEF_LOW: PosePatch = {...MV.READY, lShPitch: 0.25, rShPitch: 0.25, lShOut: 0.95, rShOut: 0.95, lElbow: 0.35, rElbow: 0.35, lHipOut: 0.22, rHipOut: 0.22};

// shot timing (seconds)
const T_SHOT1 = 5.72; // wild shot release
const T_WALL = 6.47; // ball hits the wall pad
const T_FLOOR = 6.78; // one bounce on the way back
const T_CATCH1 = 7.25; // ACE catches the rebound
const T_PASS = 8.85; // ACE's pass release
const T_RECV = 9.55; // BUCKETS catches
const T_SHOT2 = 15.88; // contested shot after the fake
const T_RIM = 16.6; // front rim
const T_CATCH2 = 17.15; // rebound to ACE

// ================= BUCKETS =================
const BK_BODY: Key[] = [
  // S1 — double-teamed, ball protected high, yelling at ACE over the defenders
  K(0, {...HOLD_HIGH, x: BK[0], z: BK[1], yaw: Y_BK_ACE + 0.1, headPitch: -0.16, spineBend: -0.08}),
  K(0.35, {yaw: Y_BK_ACE - 0.05, headPitch: -0.2, spineBend: -0.1, lean: -0.04}, 'out'),
  K(0.9, {yaw: Y_BK_ACE + 0.12, headPitch: -0.12}),
  K(1.55, {yaw: Y_BK_ACE - 0.06, headPitch: -0.22, spineBend: -0.12}, 'out'),
  K(2.3, {yaw: Y_BK_ACE + 0.06, headPitch: -0.14}),
  K(3.2, {yaw: Y_BK_ACE + 0.02, headPitch: -0.06, spineBend: -0.02}),
  // S2 — "I see a window!": peeks left/right between the defenders' arms
  K(4.2, {yaw: Y_BK_ACE, headPitch: 0.02, headYaw: 0.22, spineSide: 0.08, spineTwist: 0.05}),
  K(4.55, {headYaw: -0.2, spineSide: -0.08, spineTwist: -0.06}),
  K(4.9, {headYaw: 0.05, headPitch: -0.06, spineSide: 0.0, spineTwist: 0}, 'out'),
  // the wild shot
  K(5.42, {...HOLD_HIGH, yaw: Y_BK_RIM, headYaw: 0, headPitch: -0.1}),
  K(5.49, {...HOLD_BK, yaw: Y_BK_RIM, lShPitch: 1.45, rShPitch: 1.45, lShOut: 0.2, rShOut: 0.2, lShTwist: -0.5, rShTwist: -0.5, lElbow: 1.15, rElbow: 1.15}),
  K(5.56, {...MV.SHOT_SET, yaw: Y_BK_RIM, rElbow: 1.5, lElbow: 1.4, rShPitch: 2.4, headPitch: -0.05}),
  K(T_SHOT1, {...MV.SHOT_RELEASE, yaw: Y_BK_RIM, lift: 0.28}, 'out'),
  K(5.98, {...MV.SHOT_RELEASE, yaw: Y_BK_RIM, lift: 0.24}),
  K(6.16, {...MV.SHOT_RELEASE, yaw: Y_BK_RIM, lift: 0, lAnkle: 0, rAnkle: 0, lKnee: 0.35, rKnee: 0.35, lHip: 0.2, rHip: 0.2, lShPitch: 0.6, lElbow: 0.4}, 'in'),
  // holds the follow-through like it went in
  K(6.9, {...MV.STAND, yaw: Y_BK_RIM, rShPitch: 2.55, rElbow: 0.35, rShOut: 0.2, headPitch: -0.12}),
  K(7.4, {...MV.STAND, yaw: Y_BK_ACE, rShPitch: 0.3, rElbow: 0.5, headPitch: -0.05}),
  // receives ACE's pass
  K(9.2, {...MV.STAND, yaw: Y_BK_ACE, ...CATCH}),
  K(T_RECV, {...MV.STAND, yaw: Y_BK_ACE, ...CATCH, lElbow: 1.0, rElbow: 1.0}),
  K(9.85, {...HOLD_BK, yaw: Y_BK_ACE}),
  // S3 — "I do pass." chin up; "Warmups." proud nod
  K(10.25, {...HOLD_BK, yaw: Y_BK_ACE, headPitch: -0.04, headRoll: 0.04}),
  K(10.55, {headPitch: -0.14, headRoll: -0.06, spineBend: -0.06}, 'out'),
  K(11.3, {headPitch: -0.1, headRoll: -0.04}),
  K(12.7, {headPitch: -0.08, headRoll: 0.0, spineBend: -0.04}),
  K(12.95, {headPitch: -0.18, spineBend: -0.1}, 'out'),
  K(13.3, {headPitch: 0.06}, 'smooth'),
  K(13.6, {headPitch: -0.14}),
  K(14.4, {headPitch: -0.1, spineBend: -0.06}),
  // S4 — the fake pass: up, toward ACE... and back
  K(14.7, {...HOLD_BK, yaw: Y_BK_ACE, headPitch: -0.05}),
  K(14.98, {...MV.STAND, yaw: Y_BK_ACE, ...OVER_UP}, 'out'),
  K(15.12, {...MV.STAND, yaw: Y_BK_ACE, ...OVER_OUT}, 'in'),
  K(15.32, {...MV.STAND, yaw: Y_BK_ACE, ...OVER_OUT, lElbow: 0.45, rElbow: 0.45}),
  K(15.44, {...HOLD_BK, yaw: Y_BK_ACE + 0.15}, 'smooth'),
  K(15.55, {...HOLD_BK, yaw: Y_BK_RIM - 0.1, lShPitch: 1.45, rShPitch: 1.45, lShOut: 0.2, rShOut: 0.2, lShTwist: -0.5, rShTwist: -0.5, lElbow: 1.15, rElbow: 1.15}),
  K(15.62, {...MV.SHOT_SET, yaw: Y_BK_RIM, rElbow: 1.5, lElbow: 1.4, rShPitch: 2.4, headPitch: -0.05}),
  K(T_SHOT2, {...MV.SHOT_RELEASE, yaw: Y_BK_RIM, lift: 0.26}, 'out'),
  K(16.12, {...MV.SHOT_RELEASE, yaw: Y_BK_RIM, lift: 0.22}),
  K(16.3, {...MV.SHOT_RELEASE, yaw: Y_BK_RIM, lift: 0, lAnkle: 0, rAnkle: 0, lKnee: 0.35, rKnee: 0.35, lHip: 0.2, rHip: 0.2, lShPitch: 0.6, lElbow: 0.4}, 'in'),
  K(16.9, {...MV.STAND, yaw: Y_BK_RIM, rShPitch: 2.4, rElbow: 0.35, headPitch: -0.15}),
  // S5 — hands up, "Yo! I'm open!" (still double-teamed)
  K(17.3, {...MV.STAND, yaw: Y_BK_ACE, ...MV.ARMS_UP, headPitch: -0.12}, 'out'),
  K(17.7, {...MV.STAND, yaw: Y_BK_ACE + 0.05, ...MV.ARMS_UP, lShPitch: 2.6, rShPitch: 3.0, headPitch: -0.16}),
  K(18.15, {lShPitch: 3.0, rShPitch: 2.6, headPitch: -0.2, spineBend: -0.08}, 'out'),
  K(18.6, {lShPitch: 2.7, rShPitch: 2.95}),
  K(19.25, {lShPitch: 3.0, rShPitch: 2.65, headPitch: -0.22, spineBend: -0.1}, 'out'),
  K(19.9, {lShPitch: 2.8, rShPitch: 2.8, headPitch: -0.14}),
  K(20.4, {...MV.STAND, yaw: Y_BK_ACE, lShPitch: 0.45, rShPitch: 0.45, lShOut: 0.4, rShOut: 0.4, lElbow: 0.8, rElbow: 0.8, headPitch: -0.06}),
  // S6 — "Bro, don't be selfish!": offended, one open palm toward ACE, dead serious
  K(22.55, {...MV.STAND, yaw: Y_BK_ACE, headPitch: -0.04, lShOut: 0.2, rShOut: 0.2, lElbow: 0.4, rElbow: 0.4}),
  K(22.85, {rShPitch: 0.75, rShOut: 0.3, rElbow: 1.0, rShTwist: 0.8, spineBend: 0.06, headPitch: 0.04}, 'out'),
  K(23.5, {headPitch: 0.1, rShPitch: 0.7}),
  K(24.1, {headPitch: -0.02, rShPitch: 0.8, rElbow: 0.95, headRoll: -0.04}, 'out'),
  K(24.7, {headPitch: 0.02}),
  K(30, {headPitch: 0.03, rShPitch: 0.55, rElbow: 0.8}),
];

const BK_FACE: Key[] = [
  F(0, 'shout', {gazeX: 0, gazeY: 0.05}),
  F(1.3, 'shout', {smile: 0.25, browTilt: -0.2}),
  F(2.75, 'triumph', {smile: 0.3}),
  F(3.3, 'annoyed', {lid: 0.2, squint: 0.3}),
  F(4.2, 'serious', {squint: 0.75, lid: 0.35, gazeX: 0.45}),
  F(4.55, 'serious', {squint: 0.75, lid: 0.35, gazeX: -0.45}),
  F(4.85, 'triumph', {smile: 0.75, smirk: 0.3, gazeX: 0}),
  F(5.4, 'serious', {gazeY: 0.5}),
  F(6.9, 'smug', {gazeY: 0.3, smile: 0.4}),
  F(9.6, 'smug', {gazeX: 0, lid: 0.55}),
  // "I do pass." offended, eyebrows up
  F(10.25, 'smug', {browL: 0.75, browR: 0.75, browTilt: 0.15, lid: 0.35, smile: 0.25}),
  F(11.3, 'smug', {lid: 0.6, smile: 0.4}),
  // "Warmups." proud, not sarcastic
  F(12.7, 'triumph', {smile: 0.6, lid: 0.3, browL: 0.55, browR: 0.55}),
  F(13.7, 'smug', {smile: 0.65, lid: 0.5}),
  F(14.6, 'smug', {smile: 0.5, lid: 0.45}),
  F(14.95, 'serious', {gazeY: 0.1}),
  F(15.5, 'serious', {gazeY: 0.5, smile: 0.1}),
  F(17.3, 'shout', {smile: 0.0}),
  F(19.95, 'shout', {smile: 0.1}),
  F(20.4, 'annoyed', {lid: 0.25}),
  // S6 — offended, dead serious; holds it through the freeze
  F(22.5, 'serious', {browTilt: -0.7, lid: 0.22, smile: -0.3}),
  F(23.4, 'serious', {browTilt: -0.8, lid: 0.26, smile: -0.32, browL: -0.2, browR: -0.55}),
  F(24.7, 'serious', {browTilt: -0.75, lid: 0.3, smile: -0.3}),
  F(30, 'serious', {browTilt: -0.75, lid: 0.3, smile: -0.3}),
];

// ================= ACE =================
const ACE_BODY: Key[] = [
  // S1 — wide open under the basket, both arms up waving
  K(0, {...MV.STAND, x: ACE0[0], z: ACE0[1], yaw: Y_ACE_BK, ...MV.ARMS_UP, lShPitch: 2.6, rShPitch: 3.0, lShOut: 0.55, rShOut: 0.4}),
  K(0.45, {lShPitch: 3.0, rShPitch: 2.6, lShOut: 0.4, rShOut: 0.55}),
  K(0.9, {lShPitch: 2.6, rShPitch: 3.0, lShOut: 0.55, rShOut: 0.4}),
  K(1.35, {lShPitch: 3.0, rShPitch: 2.6, lShOut: 0.4, rShOut: 0.55}),
  K(1.8, {lShPitch: 2.65, rShPitch: 2.95, lShOut: 0.55, rShOut: 0.4}),
  K(2.3, {lShPitch: 2.9, rShPitch: 2.7}),
  // "You're double-teamed!": both hands open, pointing at the two defenders
  K(2.7, {...MV.STAND, yaw: Y_ACE_BK, lShPitch: 1.25, rShPitch: 1.25, lShOut: 0.45, rShOut: 0.45, lShTwist: 0.5, rShTwist: 0.5, lElbow: 0.3, rElbow: 0.3, spineBend: 0.05}, 'out'),
  K(3.15, {lShPitch: 1.35, rShPitch: 1.35, lShOut: 0.7, rShOut: 0.7, headPitch: 0.04, lean: 0.04}, 'out'),
  K(3.65, {lShPitch: 1.2, rShPitch: 1.2, lShOut: 0.55, rShOut: 0.55, headRoll: 0.06}),
  K(4.2, {...MV.RELAXED, yaw: Y_ACE_BK, lShOut: 0.4, rShOut: 0.4, lElbow: 0.9, rElbow: 0.9, lShPitch: 0.35, rShPitch: 0.35, headRoll: 0.04}),
  // the wild shot: follows the ball over his head, turns to the wall, catches the rebound
  K(5.75, {headPitch: -0.2, headYaw: 0.25}),
  K(6.3, {...MV.RELAXED, yaw: Y_ACE_REB, headPitch: -0.12, headYaw: 0}, 'smooth'),
  K(6.85, {...MV.STAND, yaw: Y_ACE_REB, ...CATCH, headPitch: 0.15}),
  K(T_CATCH1, {...MV.STAND, yaw: Y_ACE_REB, ...CATCH, lElbow: 1.05, rElbow: 1.05, headPitch: 0.12, lean: -0.03}, 'out'),
  K(7.45, {...HOLD, yaw: Y_ACE_REB + 0.3, headPitch: 0.05}),
  // "That's a wall." — turns back to BUCKETS, deadpan
  K(7.85, {...HOLD, yaw: Y_ACE_BK, headPitch: 0.02, headRoll: 0.04}),
  K(8.3, {headRoll: 0.08}),
  // "Just pass once." — demonstrates: a clean chest pass over the double team
  K(8.6, {...HOLD, yaw: Y_ACE_BK, lElbow: 1.62, rElbow: 1.62, lShPitch: 0.5, rShPitch: 0.5, spineBend: -0.02}),
  K(T_PASS, {...MV.STAND, yaw: Y_ACE_BK, lShPitch: 1.55, rShPitch: 1.55, lShOut: 0.12, rShOut: 0.12, lShTwist: 0.3, rShTwist: 0.3, lElbow: 0.12, rElbow: 0.12, lean: 0.06, spineBend: 0.06}, 'out'),
  K(9.15, {lShPitch: 1.4, rShPitch: 1.4}),
  K(9.6, {...MV.RELAXED, x: ACE0[0], z: ACE0[1], yaw: Y_ACE_BK, lShOut: 0.12, rShOut: 0.12, lElbow: 0.35, rElbow: 0.35, lShPitch: 0.08, rShPitch: 0.08}),
  // one small step toward him (gait layer adds the step)
  K(10.15, {x: ACE1[0], z: ACE1[1], yaw: Y_ACE1_BK}, 'smooth'),
  K(10.5, {...MV.RELAXED, x: ACE1[0], z: ACE1[1], yaw: Y_ACE1_BK, lShOut: 0.4, rShOut: 0.4, lElbow: 0.9, rElbow: 0.9, lShPitch: 0.35, rShPitch: 0.35}),
  // "When?" — one palm up
  K(11.55, {rShPitch: 0.75, rShOut: 0.55, rElbow: 0.9, rShTwist: 0.9, headRoll: 0.1, headPitch: 0.02}, 'out'),
  K(12.1, {rShPitch: 0.7, headRoll: 0.12}),
  K(12.6, {...MV.RELAXED, x: ACE1[0], z: ACE1[1], yaw: Y_ACE1_BK, lShOut: 0.4, rShOut: 0.4, lElbow: 0.9, rElbow: 0.9, lShPitch: 0.35, rShPitch: 0.35, headRoll: 0.06}),
  // the silent stare after "Warmups."
  K(13.8, {headRoll: 0.08, headPitch: 0.04}),
  K(14.6, {headRoll: 0.1, headPitch: 0.06}),
  // S4 — opens his hands for the pass... that never comes
  K(14.95, {...MV.STAND, x: ACE1[0], z: ACE1[1], yaw: Y_ACE1_BK, ...HANDS_OPEN, headRoll: 0, headPitch: 0}, 'out'),
  K(15.35, {...MV.STAND, yaw: Y_ACE1_BK, ...HANDS_OPEN, lShPitch: 1.05, rShPitch: 1.05, lean: 0.04}),
  K(15.75, {...MV.RELAXED, yaw: Y_ACE1_BK, lShOut: 0.2, rShOut: 0.2, lElbow: 0.35, rElbow: 0.35, lShPitch: 0.15, rShPitch: 0.15, headPitch: -0.15}),
  K(16.4, {headPitch: -0.3, headYaw: -0.25}),
  K(16.75, {...MV.STAND, yaw: Y_ACE1_BK - 0.25, ...CATCH, headPitch: -0.05, headYaw: 0}),
  K(T_CATCH2, {...MV.STAND, yaw: Y_ACE1_BK - 0.25, ...CATCH, lElbow: 1.05, rElbow: 1.05, headPitch: 0.05}, 'out'),
  K(17.45, {...HOLD, yaw: Y_ACE1_BK, headPitch: 0.02}),
  // S5 — "Now you want a pass?" holding the ball, head tilt
  K(20.3, {...HOLD, yaw: Y_ACE1_BK, headRoll: 0.04}),
  K(20.6, {headRoll: 0.14, headPitch: 0.05, spineBend: 0.05}, 'out'),
  K(21.5, {headRoll: 0.12}),
  // S6 — freezes
  K(22.6, {headRoll: 0.06, headPitch: 0.02, spineBend: 0.02}),
  K(24.75, {headRoll: 0.04, headPitch: 0.0}),
  K(25.4, {headRoll: 0.04}),
  // S7 — lowers the ball, turns to the lens, small head shake, "Tag that friend."
  K(25.9, {...HOLD_LOW, x: ACE1[0], z: ACE1[1], yaw: Y_ACE1_BK, headRoll: 0.04}),
  K(26.25, {headYaw: 0.5, spineTwist: 0.12, headPitch: 0.04, headRoll: 0}, 'out'),
  K(26.42, {headYaw: 0.4}),
  K(26.58, {headYaw: 0.56}),
  K(26.74, {headYaw: 0.46}),
  K(27.5, {headYaw: 0.48, headRoll: 0.04}),
  K(30, {headYaw: 0.48, headRoll: 0.06}),
];

const ACE_FACE: Key[] = [
  F(0, 'lookAround', {gazeX: 0, browL: 0.85, browR: 0.85, open: 0.15}),
  F(2.6, 'doubt', {browL: 0.95, browR: 0.6, lid: 0.1}),
  F(3.3, 'doubt', {browL: 0.9, browR: 0.55, lid: 0.18, smile: -0.35}),
  F(4.2, 'flat', {lid: 0.3}),
  F(5.75, 'lookAround', {gazeY: 0.4}),
  F(6.5, 'flat', {gazeY: 0.1}),
  F(7.3, 'deadpan', {lid: 0.4}),
  F(8.3, 'deadpan', {lid: 0.45, browL: 0.25}),
  F(8.65, 'flat', {lid: 0.3, browL: 0.35, browR: 0.25}),
  F(9.6, 'flat', {lid: 0.3}),
  F(11.5, 'doubt', {browL: 0.85, browR: 0.1, lid: 0.25}),
  F(12.4, 'doubt', {browL: 0.6, lid: 0.3}),
  F(13.75, 'deadpan', {lid: 0.42}),
  F(14.6, 'deadpan', {lid: 0.48, browL: 0.15}),
  // hopeful for half a second
  F(14.95, {browL: 0.55, browR: 0.55, browTilt: 0.25, lid: 0.08, squint: 0, smile: 0.12, open: 0.06, wide: 1.0, gazeX: 0, gazeY: 0, smirk: 0}),
  F(15.4, 'done', {lid: 0.3}),
  F(16.0, 'done', {lid: 0.35, gazeY: 0.3}),
  F(16.8, 'flat', {gazeY: 0.1}),
  F(17.4, 'deadpan', {lid: 0.4}),
  F(20.3, 'doubt', {browL: 0.95, browR: 0.25, lid: 0.22, smile: -0.3}),
  F(21.9, 'doubt', {browL: 0.8, browR: 0.2, lid: 0.3}),
  // the freeze: eyes a little wider, nothing else moves
  F(23.9, 'flat', {lid: 0.12, browL: 0.35, browR: 0.35}),
  F(24.6, {browL: 0.55, browR: 0.5, browTilt: 0.3, lid: 0.05, squint: 0, smile: -0.25, open: 0.0, wide: 0.85, gazeX: 0, gazeY: 0, smirk: 0}),
  F(25.6, {browL: 0.55, browR: 0.5, browTilt: 0.3, lid: 0.05, squint: 0, smile: -0.25, open: 0.0, wide: 0.85, gazeX: 0, gazeY: 0, smirk: 0}),
  F(25.9, 'done', {lid: 0.55}),
  F(26.3, 'done', {gazeX: -0.3, lid: 0.32, browL: 0.35, browR: 0.2}),
  F(27.4, 'done', {gazeX: -0.3, lid: 0.26, browL: 0.55, browR: 0.22}),
  F(30, 'done', {gazeX: -0.3, lid: 0.26, browL: 0.55, browR: 0.22}),
];

// ================= defenders (glued to BUCKETS all episode) =================
const defBody = (P: V2, Y: number, ph: number): Key[] => [
  K(0, {...DEF_UP, x: P[0], z: P[1], yaw: Y, spineSide: 0.03 * ph}),
  K(1.2, {spineSide: -0.04 * ph, headYaw: 0.05 * ph}),
  K(2.6, {spineSide: 0.04 * ph, headYaw: -0.04 * ph}),
  K(4.4, {spineSide: -0.03 * ph}),
  // contest the wild shot
  K(5.6, {...DEF_UP, yaw: Y, lift: 0}),
  K(5.82, {...DEF_UP, yaw: Y, lift: 0.22, lKnee: 0.15, rKnee: 0.15, lHip: 0.1, rHip: 0.1, lAnkle: 0.4, rAnkle: 0.4}, 'out'),
  K(6.12, {...DEF_UP, yaw: Y, lift: 0, headPitch: -0.25}, 'in'),
  K(6.5, {headPitch: -0.1, headYaw: 0.6 * ph}),
  // arms down while ACE's pass sails over
  K(8.4, {...DEF_LOW, yaw: Y, headYaw: 0.4 * ph}),
  K(9.0, {headPitch: -0.3, headYaw: 0.2 * ph}),
  K(9.7, {...DEF_UP, yaw: Y, headPitch: 0, headYaw: 0}),
  K(12.0, {spineSide: 0.04 * ph}),
  K(14.4, {spineSide: -0.03 * ph}),
  // bite on the fake (heads snap toward ACE), then contest
  K(15.0, {headYaw: 0.7 * ph, spineTwist: 0.12 * ph}),
  K(15.4, {headYaw: 0.75 * ph, spineTwist: 0.12 * ph}),
  K(15.62, {...DEF_UP, yaw: Y, headYaw: 0, spineTwist: 0}),
  K(15.95, {...DEF_UP, yaw: Y, lift: 0.22, lKnee: 0.15, rKnee: 0.15, lHip: 0.1, rHip: 0.1, lAnkle: 0.4, rAnkle: 0.4}, 'out'),
  K(16.25, {...DEF_UP, yaw: Y, lift: 0}, 'in'),
  K(18.0, {spineSide: 0.04 * ph}),
  K(21.0, {spineSide: -0.04 * ph}),
  K(25.0, {spineSide: 0.03 * ph}),
  K(30, {spineSide: -0.02 * ph}),
];
const DEF_FACE: Key[] = [F(0, 'serious', {lid: 0.25}), F(30, 'serious', {lid: 0.25})];
const AND1_BODY: Key[] = [K(0, {...MV.CROSSED, x: AND1P[0], z: AND1P[1], yaw: faceTo(AND1P, BK) - 0.2, headPitch: 0.02}), K(30, {headRoll: 0.06})];
const AND1_FACE: Key[] = [F(0, 'smug', {lid: 0.6}), F(30, 'smug', {lid: 0.6})];

const BODY: Record<Who, Key[]> = {BUCKETS: BK_BODY, ACE: ACE_BODY, DEF1: defBody(DEF1P, Y_D1, 1), DEF2: defBody(DEF2P, Y_D2, -1), AND1: AND1_BODY};
const FACE: Record<Who, Key[]> = {BUCKETS: BK_FACE, ACE: ACE_FACE, DEF1: DEF_FACE, DEF2: DEF_FACE, AND1: AND1_FACE};

// blinks (start times); long blink = [t, hold]
const BLINKS: Record<Who, [number, number?][]> = {
  BUCKETS: [[2.95], [6.95], [9.9], [11.9], [14.45], [16.95], [20.6], [22.3], [25.3, 0.05], [27.6]],
  ACE: [[1.0], [4.35], [7.6], [10.0], [12.5], [14.42], [17.6], [22.1], [25.95, 0.3], [28.6]],
  DEF1: [[1.7], [5.2], [8.9], [13.1], [17.2], [21.4], [26.0]],
  DEF2: [[2.4], [6.6], [10.9], [14.0], [19.0], [23.6], [27.9]],
  AND1: [[3.1], [9.5], [16.1], [22.7], [28.2]],
};
const blinkAt = (who: Who, t: number) => {
  let v = 0;
  for (const [t0, hold = 0.02] of BLINKS[who]) {
    const u = t - t0;
    if (u < 0 || u > 0.06 + hold + 0.1) continue;
    v = Math.max(v, u < 0.06 ? u / 0.06 : u < 0.06 + hold ? 1 : 1 - (u - 0.06 - hold) / 0.1);
  }
  return v;
};
const mouthAt = (who: Who, t: number) => {
  const arr = LINES.mouth[who];
  if (!arr) return 0;
  const f = t * FPS;
  const i = Math.floor(f);
  return lerp(arr[i] ?? 0, arr[i + 1] ?? 0, f - i);
};

// ---------- procedural gait: ACE's one small step ----------
type Gait = {t0: number; t1: number; stride: number; amp: number; run: boolean; fade?: number};
const GAITS: Partial<Record<Who, Gait[]>> = {ACE: [{t0: 9.62, t1: 10.15, stride: 0.6, amp: 0.7, run: false, fade: 0.2}]};
const rootAt = (keys: Key[], t: number): V2 => {
  const p = evalKeys(POSE0, keys, t);
  return [p.x, p.z];
};
const gaitPhase = (keys: Key[], g: Gait, t: number) => {
  let d = 0;
  let prev = rootAt(keys, g.t0);
  const n = 16;
  for (let i = 1; i <= n; i++) {
    const p = rootAt(keys, g.t0 + ((t - g.t0) * i) / n);
    d += Math.hypot(p[0] - prev[0], p[1] - prev[1]);
    prev = p;
  }
  return (d / g.stride) * Math.PI;
};
const applyGait = (who: Who, keys: Key[], p: Pose, t: number): Pose => {
  for (const g of GAITS[who] ?? []) {
    const fo = g.fade ?? 0.25;
    if (t < g.t0 || t > g.t1 + fo) continue;
    const env = clamp((t - g.t0) / 0.12) * clamp((g.t1 + fo - t) / fo);
    const ph = gaitPhase(keys, g, Math.min(t, g.t1));
    const s = Math.sin(ph);
    const a = g.amp * env;
    const q = {...p};
    q.lHip += a * 0.45 * s;
    q.rHip -= a * 0.45 * s;
    q.lKnee += a * (0.12 + 0.6 * Math.max(0, -Math.sin(ph - 0.7)));
    q.rKnee += a * (0.12 + 0.6 * Math.max(0, Math.sin(ph - 0.7)));
    q.lAnkle += a * 0.25 * Math.max(0, s);
    q.rAnkle += a * 0.25 * Math.max(0, -s);
    q.lShPitch -= a * 0.25 * s;
    q.rShPitch += a * 0.25 * s;
    q.roll += a * 0.03 * Math.cos(ph);
    return q;
  }
  return p;
};

export const poseAt = (who: Who, t: number): Pose => {
  const body = BODY[who];
  let p = evalKeys(POSE0, body, t);
  p = applyGait(who, body, p, t);
  const fp = evalKeys(POSE0, FACE[who], t).face;
  const ix = CAST.indexOf(who);
  const br = Math.sin(t * 2.2 + ix * 1.3);
  const m = mouthAt(who, t);
  const talk = Math.sin(t * 17) * 0.5 + 0.5;
  const loud = who === 'BUCKETS';
  return {
    ...p,
    spineBend: p.spineBend + 0.012 * br,
    headPitch: p.headPitch - 0.008 * br + m * 0.05 * (loud ? -1.2 : 0.6) * talk,
    face: {
      ...fp,
      lid: Math.min(1, fp.lid + (1 - fp.lid) * blinkAt(who, t)),
      wide: fp.wide * lerp(1, mouthWide(who, t), clamp(m * 4)),
      browL: fp.browL + (loud ? m * 0.22 : m * 0.06),
      browR: fp.browR + (loud ? m * 0.22 : m * 0.06),
    },
  };
};

// ---------- lip-sync: amplitude x phoneme shapes (same table as EP001) ----------
const VIS: Record<string, [number, number]> = {
  A: [1, 1.12], O: [0.78, 0.62], U: [0.5, 0.5], E: [0.55, 1.3], I: [0.45, 1.2],
  M: [0, 0.95], F: [0.12, 1.05], N: [0.3, 1.0], T: [0.28, 1.05], L: [0.38, 1.0], R: [0.35, 0.72], H: [0.5, 0.85], C: [0.25, 0.7], S: [0.16, 1.22], D: [0.28, 1.05],
};
const WORD_PH: Record<string, string> = {
  im: 'AIM', open: 'OUMEN', youre: 'IUR', doubleteamed: 'DAMELTIMD', i: 'AI', see: 'SI', a: 'A', window: 'UINDOU', thats: 'DATS', wall: 'UOL',
  just: 'DSAST', pass: 'MAS', once: 'UANS', do: 'DU', when: 'UEN', warmups: 'UORMAMS', yo: 'IO', now: 'NAU', you: 'IU', want: 'UANT',
  bro: 'MRO', dont: 'DONT', be: 'MI', selfish: 'SELFIS', tag: 'TAC', that: 'DAT', friend: 'FREND',
};
const isV = (c: string) => 'AOUEI'.includes(c);
const visemeAt = (who: Who, t: number): [number, number] | null => {
  for (const l of LINES.lines) {
    if (l.who !== who) continue;
    for (const w of l.words) {
      if (t < w.start - 0.03 || t > w.end + 0.03) continue;
      const ph = WORD_PH[w.text.toLowerCase().replace(/[^a-z]/g, '')];
      if (!ph) return null;
      const wts = [...ph].map((c) => (isV(c) ? 2 : 1));
      const tot = wts.reduce((a, b) => a + b, 0);
      const u = clamp((t - w.start) / Math.max(0.05, w.end - w.start)) * tot;
      let acc = 0;
      for (let i = 0; i < ph.length; i++) {
        if (u <= acc + wts[i] || i === ph.length - 1) {
          const cur = VIS[ph[i]];
          const nxt = VIS[ph[Math.min(ph.length - 1, i + 1)]];
          const k = smooth(clamp((u - acc) / wts[i] - 0.55) / 0.45);
          return [lerp(cur[0], nxt[0], k), lerp(cur[1], nxt[1], k)];
        }
        acc += wts[i];
      }
    }
  }
  return null;
};
export const mouthOf = (who: Who, t: number) => {
  const amp = mouthAt(who, t);
  const v = visemeAt(who, t);
  if (!v) return amp;
  return clamp(amp * (0.3 + 0.95 * v[0]) * (v[0] < 0.05 ? 0.1 : 1));
};
export const mouthWide = (who: Who, t: number) => visemeAt(who, t)?.[1] ?? 1;

// ---------- ball (one ball, always somewhere physical) ----------
const skelAt = (who: Who, t: number) => fk(poseAt(who, t), LOOKS[who].build);
const twoHand = (who: Who, t: number) => {
  const s = skelAt(who, t);
  return ballInHand(s, 'l').add(ballInHand(s, 'r')).multiplyScalar(0.5);
};
const arc = (a: THREE.Vector3, b: THREE.Vector3, h: number, u: number) => {
  const p = a.clone().lerp(b, u);
  p.y += 4 * h * u * (1 - u);
  return p;
};
const V = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
/** padded baseline wall: front face at z = 3.1 (wall box 0.2 deep at z = 3.2); ball centre one radius off it */
export const WALL_HIT = V(1.55, 1.5, 2.97);
const FLOOR_HIT = V(1.2, 0.121, 0.15); // lands clear of the stanchion base (box x ±0.7, z 0..1.4)
const toShooter = norm([BK[0] - RIM.x, BK[1] - RIM.z]);
/** front rim, on the shooter's side: ball centre = rim radius 0.225 + tube + ball radius away from the rim centre */
export const RIM_HIT = V(RIM.x + toShooter[0] * 0.36, RIM.y + 0.1, RIM.z + toShooter[1] * 0.36);

const C1 = () => twoHand('ACE', T_CATCH1);
const C2 = () => twoHand('ACE', T_CATCH2);

export const ballAt = (t: number): {pos: THREE.Vector3; spin: number} => {
  if (t < 5.58) return {pos: twoHand('BUCKETS', t), spin: 0};
  if (t < T_SHOT1) {
    // set point: still in both hands, the right hand behind it
    return {pos: twoHand('BUCKETS', t).lerp(ballInHand(skelAt('BUCKETS', t), 'r'), smooth((t - 5.58) / 0.14)), spin: 0};
  }
  if (t < T_WALL) {
    const a = ballInHand(skelAt('BUCKETS', T_SHOT1), 'r');
    return {pos: arc(a, WALL_HIT, 2.2, (t - T_SHOT1) / (T_WALL - T_SHOT1)), spin: (t - T_SHOT1) * 9};
  }
  if (t < T_FLOOR) {
    const u = (t - T_WALL) / (T_FLOOR - T_WALL);
    const p = WALL_HIT.clone().lerp(FLOOR_HIT, u);
    p.y = lerp(WALL_HIT.y, 0.121, u * u * 0.6 + u * 0.4);
    return {pos: p, spin: -t * 6};
  }
  if (t < T_CATCH1) return {pos: arc(FLOOR_HIT, C1(), 0.55, (t - T_FLOOR) / (T_CATCH1 - T_FLOOR)), spin: -t * 6};
  if (t < T_PASS) return {pos: twoHand('ACE', t), spin: 0};
  if (t < T_RECV) return {pos: arc(twoHand('ACE', T_PASS), twoHand('BUCKETS', T_RECV), 1.35, (t - T_PASS) / (T_RECV - T_PASS)), spin: -(t - T_PASS) * 10};
  if (t < 15.66) return {pos: twoHand('BUCKETS', t), spin: 0};
  if (t < T_SHOT2) return {pos: twoHand('BUCKETS', t).lerp(ballInHand(skelAt('BUCKETS', t), 'r'), smooth((t - 15.66) / 0.14)), spin: 0};
  if (t < T_RIM) {
    const a = ballInHand(skelAt('BUCKETS', T_SHOT2), 'r');
    return {pos: arc(a, RIM_HIT, 1.25, (t - T_SHOT2) / (T_RIM - T_SHOT2)), spin: (t - T_SHOT2) * 9};
  }
  if (t < T_CATCH2) return {pos: arc(RIM_HIT, C2(), 0.45, (t - T_RIM) / (T_CATCH2 - T_RIM)), spin: -t * 7};
  return {pos: twoHand('ACE', t), spin: 0};
};

// ---------- cameras ----------
export const headOf = (who: Who, t: number) => new THREE.Vector3(0, D.headY, 0.02).applyMatrix4(skelAt(who, t).head);
const arr = (v: THREE.Vector3): [number, number, number] => [v.x, v.y, v.z];
export type Shot = {id: string; t0: number; t1: number; cam: (t: number) => Cam; focus: [number, number, number]};
type Rig = {pos: THREE.Vector3; target: THREE.Vector3; fov: number; push: number};

const frameHead = (who: Who, at: number, toward: V2, dist: number, side: number, dy: number, fov: number, push = 0.04, tdy = 0): Rig => {
  const h = headOf(who, at);
  const dir = V(toward[0] - h.x, 0, toward[1] - h.z).normalize();
  const left = V(dir.z, 0, -dir.x);
  const pos = h.clone().add(dir.clone().multiplyScalar(dist)).add(left.multiplyScalar(side));
  pos.y = h.y + dy;
  const target = h.clone();
  target.y += tdy;
  return {pos, target, fov, push};
};
const still = (c: Rig, t0: number, t1: number) => (t: number): Cam => {
  const u = smooth((t - t0) / (t1 - t0));
  return {pos: arr(c.pos.clone().lerp(c.target, c.push * u)), target: arr(c.target), fov: c.fov};
};
const move = (p0: THREE.Vector3, p1: THREE.Vector3, g0: THREE.Vector3, g1: THREE.Vector3, fov: number, t0: number, t1: number) => (t: number): Cam => {
  const u = smooth((t - t0) / (t1 - t0));
  return {pos: arr(p0.clone().lerp(p1, u)), target: arr(g0.clone().lerp(g1, u)), fov};
};

// wide "behind ACE": the open man in the foreground, the ball hog shouting in the double team behind
const BEHIND_ACE_P = V(-2.75, 3.55, -0.05);
const BEHIND_ACE_T = V(1.55, 1.3, -4.4);
// wide "behind BUCKETS": shot lines, the wall, the rim and ACE facing us
const BEHIND_BK_P = V(5.95, 3.15, -8.55);
const BEHIND_BK_T = V(0.85, 1.45, -3.2);
// the baseline wall pad seen from the left elbow: the ball slaps the pad, bounces back, ACE catches it
const WALL_P = V(-2.6, 2.2, -7.6);
const WALL_T = V(1.0, 1.25, 1.5);

export type Hook = 'A' | 'B' | 'C';
const hookShots = (hook: Hook): Shot[] => {
  const f: [number, number, number] = [1.2, 1, -4.2];
  if (hook === 'B') {
    // B: tight on BUCKETS yelling, then the reveal of ACE alone under the basket
    return [
      {id: 'H_bk', t0: 0, t1: 1.25, focus: [BK[0], 1.4, BK[1]], cam: still(bkCam(0.5, 0.08, 2.7, 0.12, 22, 0.05, -0.1), 0, 1.25)},
      {id: 'H_reveal', t0: 1.25, t1: 2.62, focus: f, cam: move(BEHIND_ACE_P.clone().add(V(-0.2, 0.15, 0.3)), BEHIND_ACE_P, BEHIND_ACE_T, BEHIND_ACE_T, 46, 1.25, 2.62)},
    ];
  }
  if (hook === 'C') {
    // C: fast high wide from the right sideline, quick push-in
    return [{id: 'H_wide', t0: 0, t1: 2.62, focus: f, cam: move(V(7.2, 4.3, 2.5), V(6.3, 3.9, 1.4), V(1.2, 1.0, -4.1), V(1.3, 1.05, -4.2), 58, 0, 2.62)}];
  }
  // A: visual contradiction in one frame (the open man big in the foreground, slight push)
  return [{id: 'H_a', t0: 0, t1: 2.62, focus: f, cam: move(BEHIND_ACE_P.clone().add(V(-0.25, 0.1, 0.25)), BEHIND_ACE_P, BEHIND_ACE_T, BEHIND_ACE_T.clone().add(V(0.1, 0.05, -0.1)), 46, 0, 2.62)}];
};

/** BUCKETS close-up from a 3/4 angle (ang rad off his line to ACE), so the defenders' raised arms stay out of frame */
const bkCam = (at: number, ang: number, dist: number, dy: number, fov: number, push: number, tdy: number) =>
  frameHead('BUCKETS', at, add(BK, rot(dBK, ang), 3), dist, 0, dy, fov < 30 ? fov * 1.12 : fov, push, fov < 30 ? tdy + 0.08 : tdy);
const SHOTS_DEF = (hook: Hook): Shot[] => {
  const s: Shot[] = [...hookShots(hook)];
  // S1b — ACE: "You're double-teamed!"
  s.push({id: 'ace_double', t0: 2.62, t1: 4.2, focus: [ACE0[0], 1.3, ACE0[1]], cam: still(frameHead('ACE', 3.0, BK, 2.7, -0.35, -0.18, 38, 0.05, -0.38), 2.62, 4.2)});
  // S2 — BUCKETS peeks for a "window" between the defenders' arms
  s.push({id: 'bk_window', t0: 4.2, t1: 5.42, focus: [BK[0], 1.4, BK[1]], cam: still(bkCam(4.6, -0.08, 2.8, 0.1, 23, 0.06, -0.12), 4.2, 5.42)});
  // S2 — the wild shot into the wall pad, rebound to ACE (wide, behind the shooter)
  s.push({id: 'shot_wall', t0: 5.42, t1: 6.15, focus: [2.0, 1.2, -4.5], cam: move(BEHIND_BK_P, BEHIND_BK_P.clone().add(V(-0.1, 0.15, 0.2)), BEHIND_BK_T, BEHIND_BK_T.clone().add(V(-0.2, 0.6, 1.0)), 50, 5.42, 6.15)});
  s.push({id: 'wall_hit', t0: 6.15, t1: 7.35, focus: [0.3, 1.2, 0.0], cam: move(WALL_P, WALL_P.clone().add(V(0.1, -0.05, 0.35)), WALL_T, WALL_T.clone().add(V(-0.6, -0.05, -1.2)), 42, 6.15, 7.35)});
  // ACE: "That's a wall."
  s.push({id: 'ace_wall', t0: 7.35, t1: 8.5, focus: [ACE0[0], 1.3, ACE0[1]], cam: still(frameHead('ACE', 8.0, BK, 2.1, -0.3, -0.12, 34, 0.06, -0.3), 7.35, 8.5)});
  // ACE passes over the double team: "Just pass once."
  s.push({id: 'pass', t0: 8.5, t1: 10.15, focus: [1.2, 1, -4.2], cam: move(BEHIND_ACE_P.clone().add(V(-0.1, 0.25, 0.15)), BEHIND_ACE_P.clone().add(V(0.15, 0.2, -0.15)), BEHIND_ACE_T.clone().add(V(0.0, 0.25, 0)), BEHIND_ACE_T.clone().add(V(0.1, 0.2, -0.1)), 48, 8.5, 10.15)});
  // BUCKETS: "I do pass."
  s.push({id: 'bk_idopass', t0: 10.15, t1: 11.45, focus: [BK[0], 1.4, BK[1]], cam: still(bkCam(10.6, 0.1, 2.8, 0.1, 23, 0.05, -0.14), 10.15, 11.45)});
  // ACE: "When?"
  s.push({id: 'ace_when', t0: 11.45, t1: 12.45, focus: [ACE1[0], 1.3, ACE1[1]], cam: still(frameHead('ACE', 11.8, BK, 1.75, -0.22, -0.05, 30, 0.06, -0.2), 11.45, 12.45)});
  // BUCKETS: "Warmups." (proud)
  s.push({id: 'bk_warmups', t0: 12.45, t1: 13.85, focus: [BK[0], 1.4, BK[1]], cam: still(bkCam(13.0, -0.1, 2.7, 0.1, 21, 0.07, -0.1), 12.45, 13.85)});
  // ACE: the silent stare
  s.push({id: 'ace_stare', t0: 13.85, t1: 14.62, focus: [ACE1[0], 1.3, ACE1[1]], cam: still(frameHead('ACE', 14.2, BK, 2.0, -0.2, -0.02, 28, 0.05, -0.18), 13.85, 14.62)});
  // S4 — fake pass, contested miss, rebound to ACE (wide, behind the shooter: ACE's open hands face us)
  s.push({id: 'fake', t0: 14.62, t1: 17.42, focus: [1.5, 1.2, -3.5], cam: move(BEHIND_BK_P.clone().add(V(0.15, 0.0, -0.2)), BEHIND_BK_P.clone().add(V(-0.2, 0.05, 0.3)), BEHIND_BK_T.clone().add(V(0, 0.15, 0)), BEHIND_BK_T.clone().add(V(-0.15, 0.3, 0.2)), 50, 14.62, 17.42)});
  // S5 — BUCKETS, hands up in the double team: "Yo! I'm open!"
  s.push({id: 'bk_open2', t0: 17.42, t1: 20.15, focus: [BK[0], 1.4, BK[1]], cam: still(bkCam(18.4, 0.05, 4.6, -0.15, 32, 0.05, -0.3), 17.42, 20.15)});
  // ACE: "Now you want a pass?"
  s.push({id: 'ace_nowpass', t0: 20.15, t1: 22.4, focus: [ACE1[0], 1.3, ACE1[1]], cam: still(frameHead('ACE', 20.8, BK, 2.0, -0.28, -0.1, 32, 0.06, -0.28), 20.15, 22.4)});
  // S6 — close-up: "Bro, don't be selfish!"
  s.push({id: 'bk_selfish', t0: 22.4, t1: 24.95, focus: [BK[0], 1.5, BK[1]], cam: still(bkCam(23.4, 0.04, 2.6, 0.08, 18, 0.08, -0.05), 22.4, 24.95)});
  // ACE freezes
  s.push({id: 'ace_freeze', t0: 24.95, t1: 26.15, focus: [ACE1[0], 1.3, ACE1[1]], cam: still(frameHead('ACE', 25.3, BK, 1.7, -0.2, -0.04, 30, 0.04, -0.2), 24.95, 26.15)});
  // S7 — ACE to the lens: "Tag that friend."
  s.push({id: 'ace_tag', t0: 26.15, t1: DURATION, focus: [ACE1[0], 1.3, ACE1[1]], cam: (t) => {
    const h = headOf('ACE', 27.2);
    const yaw = Y_ACE1_BK + 0.48 + 0.12;
    const pos = h.clone().add(V(Math.sin(yaw), 0, Math.cos(yaw)).multiplyScalar(1.9));
    pos.y = h.y + 0.03;
    const u = smooth((t - 26.15) / 3.85);
    return {pos: arr(pos.lerp(h, 0.1 * u)), target: [h.x, h.y - 0.2, h.z], fov: 30};
  }});
  return s;
};
const CACHE: Partial<Record<Hook, Shot[]>> = {};
export const SHOTS = (hook: Hook = 'A') => (CACHE[hook] ??= SHOTS_DEF(hook));

// ---------- captions ----------
export const HIGHLIGHT = new Set(['B1', 'A2', 'B4', 'A5', 'B6']);
export const NO_CAPTION = new Set(['A6']);
export const CAPTION_Y: Record<string, number> = {
  H_a: 1150, H_bk: 1380, H_reveal: 1330, H_wide: 1330, ace_double: 1340, bk_window: 1380, shot_wall: 1330, wall_hit: 1330, ace_wall: 1340, pass: 1330, bk_idopass: 1380,
  ace_when: 1360, bk_warmups: 1380, ace_stare: 1360, fake: 1330, bk_open2: 1340, ace_nowpass: 1360, bk_selfish: 1420, ace_freeze: 1360, ace_tag: 1340,
};
