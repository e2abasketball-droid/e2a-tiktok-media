// EVERY COURT HAS ONE — EP001 "THE AND-ONE GUY"
// Timeline built AROUND the locked dialogue (comedy/ep001/lines.json): body keys, face keys,
// blinks, ball, cameras and captions. All times in seconds (episode clock, 30 fps).
import * as THREE from 'three';
import {POSE0, apply, evalKeys, clamp, lerp, smooth} from './pose';
import type {Key, Pose, PosePatch, Face} from './pose';
import * as MV from './moves';
import {ballInHand, bonePos, fk, D} from './toon';
import type {Cam} from './stage';
import {RIM} from './gym';
import lines from '../../comedy/ep001/lines.json';

export const FPS = 30;
export const DURATION = 24.4;
export const LINES = lines as {lines: {id: string; who: 'AND1' | 'ACE'; start: number; end: number; text: string; words: {text: string; start: number; end: number}[]}[]; mouth: Record<'AND1' | 'ACE', number[]>};

type V2 = [number, number];
const faceTo = (from: V2, to: V2) => Math.atan2(to[0] - from[0], to[1] - from[1]);

// ---------- blocking (x, z on the floor) ----------
const A_LAY: V2 = [0.45, -2.1]; // AND1 after the layup
const ACE_1: V2 = [-0.6, -7.0]; // ACE, scenes 1-4 (top of the key, far from everything)
const A_SHOT: V2 = [1.2, -5.4]; // AND1 open jumper (right elbow)
const A_RUN0: V2 = [3.9, -6.4]; // drive start (right wing)
const A_TRIP: V2 = [1.75, -3.9];
const A_SEAT: V2 = [1.42, -3.42];
const ACE_2: V2 = ACE_1; // ACE, scene 4 (same spot)
const ACE_3: V2 = [2.5, -4.75]; // ACE stops at AND1's left, looking down at him

const Y_A1_ACE = faceTo(A_LAY, ACE_1);
const Y_ACE_A1 = faceTo(ACE_1, A_LAY);
const Y_SHOT = faceTo(A_SHOT, [0, -1.575]);
const Y_SHOT_ACE = faceTo(A_SHOT, ACE_1);
const Y_ACE_SHOT = faceTo(ACE_1, A_SHOT);
const Y_RUN = faceTo(A_RUN0, A_TRIP);
const Y_SEAT = faceTo(A_SEAT, [6.0, -1.6]); // sits facing the wide camera (we see his face for FOUL!)
const HEAD_TO_ACE = faceTo(A_SEAT, ACE_3) - Y_SEAT; // how far he must turn to look at ACE
const Y_ACE2 = faceTo(ACE_2, A_SEAT);
const Y_ACE3 = faceTo(ACE_3, A_SEAT);
// shot A camera sits on the right sideline; AND1 turns to it ("to the world")
const CAM_A: [number, number, number] = [4.6, 1.45, -4.3];
const Y_A1_CAM = faceTo(A_LAY, [CAM_A[0], CAM_A[2]]);

const K = (t: number, p: PosePatch, ease?: Key['ease']): Key => ({t, p, ease});
const F = (t: number, name: keyof typeof MV.FACES | Partial<Face>, extra: Partial<Face> = {}, ease?: Key['ease']): Key => ({
  t,
  p: {face: {...(typeof name === 'string' ? MV.FACES[name] : name), ...extra}},
  ease,
});

// ================= AND1 =================
const AND1_BODY: Key[] = [
  // SCENE 1 — layup already in the air at frame 0, nobody near
  K(0, {...MV.STAND, x: 0.66, z: -2.38, yaw: faceTo([0.66, -2.38], [0, -1.575]), lift: 0.5, rShPitch: 2.95, rShOut: 0.12, rElbow: 0.12, lShPitch: 1.1, lShOut: 0.45, lElbow: 0.9,
    lHip: 1.15, lKnee: 1.55, rHip: 0.1, rKnee: 0.25, rAnkle: 0.5, headPitch: -0.3}),
  K(0.2, {x: 0.52, z: -2.2, lift: 0.36, rShPitch: 2.55, rElbow: 0.4, lHip: 0.8, lKnee: 1.2}, 'out'),
  K(0.4, {x: A_LAY[0], z: A_LAY[1], lift: 0, lean: 0.24, lHip: 0.55, rHip: 0.55, lKnee: 0.95, rKnee: 0.95, lAnkle: -0.3, rAnkle: -0.3, lHipOut: 0.15, rHipOut: 0.15,
    lShPitch: 0.5, rShPitch: 0.65, lElbow: 0.6, rElbow: 0.6, lShOut: 0.3, rShOut: 0.3, headPitch: 0.05}, 'in'),
  K(0.5, {lean: 0.12, lKnee: 0.6, rKnee: 0.6, lHip: 0.35, rHip: 0.35, yaw: faceTo([0.66, -2.38], [0, -1.575]) + 0.9}),
  K(0.72, {...MV.FLEX, yaw: Y_A1_CAM}, 'back'),
  K(1.1, {...MV.FLEX, yaw: Y_A1_CAM, lHip: 0.55, lKnee: 0.9, lean: 0.04}),
  K(1.24, {...MV.FLEX, yaw: Y_A1_CAM, spineBend: -0.24, lean: -0.1, headPitch: -0.26}, 'back'),
  K(1.95, {...MV.FLEX, yaw: Y_A1_CAM, spineBend: -0.2, lean: -0.08, headPitch: -0.2}),
  // SCENE 2 — (cut) faces ACE, dismissive wave
  K(4.9, {...MV.STAND, yaw: Y_A1_ACE, headPitch: -0.1}, 'step'),
  K(5.05, {...MV.WAVE_A, yaw: Y_A1_ACE}),
  K(5.28, {...MV.WAVE_B, yaw: Y_A1_ACE + 0.12, headYaw: 0.25}, 'back'),
  K(5.72, {...MV.WAVE_B, yaw: Y_A1_ACE + 0.15, headYaw: 0.35, rShPitch: 0.5, rElbow: 0.5}),
  // SCENE 3 — open jumper, misses badly
  K(5.74, {...MV.SHOT_SET, x: A_SHOT[0], z: A_SHOT[1], yaw: Y_SHOT, headYaw: 0, headRoll: 0}, 'step'),
  K(5.86, {...MV.SHOT_SET, x: A_SHOT[0], z: A_SHOT[1], yaw: Y_SHOT, lKnee: 0.8, rKnee: 0.8, lHip: 0.45, rHip: 0.45}),
  K(6.0, {...MV.SHOT_RELEASE, yaw: Y_SHOT}, 'out'),
  K(6.22, {...MV.SHOT_RELEASE, yaw: Y_SHOT, lift: 0.2}),
  K(6.38, {...MV.SHOT_RELEASE, yaw: Y_SHOT, lift: 0, lAnkle: 0, rAnkle: 0, lKnee: 0.35, rKnee: 0.35, lHip: 0.2, rHip: 0.2, lShPitch: 0.6, lElbow: 0.4}, 'in'),
  K(6.74, {...MV.STAND, yaw: Y_SHOT, rShPitch: 2.6, rElbow: 0.3, headPitch: -0.12}),
  // second AND ONE: foul-call chop toward ACE
  K(6.8, {...MV.CHOP_UP, yaw: Y_SHOT_ACE - 0.35, headYaw: 0.2}, 'out'),
  K(6.97, {...MV.CHOP_DOWN, yaw: Y_SHOT_ACE - 0.35, headYaw: 0.2}, 'in'),
  K(7.28, {...MV.CHOP_UP, yaw: Y_SHOT_ACE - 0.35, headYaw: 0.2}),
  K(7.46, {...MV.CHOP_DOWN, yaw: Y_SHOT_ACE - 0.35, headYaw: 0.2, lean: 0.06}, 'in'),
  K(8.1, {...MV.CHOP_DOWN, yaw: Y_SHOT_ACE - 0.35, headYaw: 0.2}),
  // annoyed beat after "You missed."
  K(9.5, {...MV.STAND, x: A_SHOT[0], z: A_SHOT[1], yaw: Y_SHOT_ACE - 0.25, headYaw: 0.1, lShOut: 0.12, rShOut: 0.12}, 'step'),
  K(9.9, {headYaw: 0.05, headPitch: 0.06, headRoll: -0.06, spineBend: 0.06}),
  K(10.24, {headRoll: -0.08}),
  // SCENE 4 — drive (gait layer adds the steps + dribble), trip, spin, sit, FOUL!
  K(10.25, {...MV.STAND, x: A_RUN0[0], z: A_RUN0[1], yaw: Y_RUN, lean: 0.2, spineBend: 0.12, headYaw: 0, headRoll: 0, headPitch: -0.05, rShPitch: 0.35, rElbow: 0.9, lShPitch: 0.25, lElbow: 1.0}, 'step'),
  K(11.33, {x: A_TRIP[0], z: A_TRIP[1], lean: 0.22}, 'linear'),
  K(11.5, {x: A_TRIP[0] - 0.22, z: A_TRIP[1] + 0.24, lift: 0.14, lean: 0.55, lShPitch: 1.7, lShOut: 0.95, rShPitch: 2.3, rShOut: 0.7, lElbow: 0.4, rElbow: 0.5,
    lHip: -0.35, lKnee: 1.1, rHip: 0.95, rKnee: 0.45, headPitch: -0.25}, 'out'),
  K(11.7, {x: A_TRIP[0] - 0.32, z: A_TRIP[1] + 0.38, lift: 0.08, lean: 0.75, lShPitch: 2.7, rShPitch: 0.8, rShOut: 1.1, lHip: 0.7, lKnee: 0.4, rHip: -0.2, rKnee: 1.0, yaw: Y_RUN - 0.4}),
  K(11.86, {x: A_SEAT[0], z: A_SEAT[1], yaw: Y_SEAT + 0.9, lean: 0.1, sit: 0.55, roll: 0.12, lift: 0, lHip: 1.0, rHip: 1.1, lKnee: 0.6, rKnee: 0.7, lShPitch: 1.6, rShPitch: 1.9}),
  K(12.02, {...MV.SIT, yaw: Y_SEAT + 0.15, lean: -0.34, roll: 0, headPitch: 0.1}, 'in'),
  K(12.18, {...MV.SIT, yaw: Y_SEAT, lean: -0.18, headPitch: 0}, 'out'),
  K(12.42, {...MV.SIT, yaw: Y_SEAT, lShPitch: 0.9, rShPitch: 1.0, lShOut: 0.5, rShOut: 0.5}),
  K(12.6, {...MV.SIT, ...MV.ARMS_UP, yaw: Y_SEAT, lean: -0.08, spineBend: 0.0, headPitch: -0.12}, 'back'),
  K(13.4, {...MV.SIT, ...MV.ARMS_UP, yaw: Y_SEAT, lean: -0.08, spineBend: 0.0, lShPitch: 2.7, rShPitch: 2.75, headPitch: -0.1}),
  K(13.85, {...MV.SIT_REST, yaw: Y_SEAT, headYaw: -0.1}),
  // SCENE 5 — keeps looking ahead (away from ACE) while ACE walks over; slow head turn in the silence
  K(16.0, {...MV.SIT_REST, yaw: Y_SEAT, headYaw: -0.15, headPitch: 0.05}),
  K(18.05, {...MV.SIT_REST, yaw: Y_SEAT, headYaw: -0.15, headPitch: 0.05}),
  K(18.95, {...MV.SIT_REST, yaw: Y_SEAT, spineTwist: HEAD_TO_ACE * 0.35, headYaw: HEAD_TO_ACE * 0.65, headPitch: -0.28}),
  // SCENE 6 — points down at the floor (left hand: the side facing ACE and the camera)
  K(19.12, {...MV.SIT_REST, yaw: Y_SEAT, spineTwist: HEAD_TO_ACE * 0.35, headYaw: HEAD_TO_ACE * 0.65, headPitch: -0.28}),
  K(19.5, {...MV.SIT_POINT_L, yaw: Y_SEAT, spineTwist: HEAD_TO_ACE * 0.35, headYaw: HEAD_TO_ACE * 0.65, headPitch: -0.28}, 'back'),
  K(19.98, {...MV.SIT_POINT_L, yaw: Y_SEAT, spineTwist: HEAD_TO_ACE * 0.35, headYaw: HEAD_TO_ACE * 0.65, headPitch: -0.2}),
  K(20.25, {...MV.SIT_POINT_L, yaw: Y_SEAT, spineTwist: HEAD_TO_ACE * 0.35, headYaw: HEAD_TO_ACE * 0.65, headPitch: -0.28, lShPitch: 0.28}),
  K(24.4, {...MV.SIT_POINT_L, yaw: Y_SEAT, spineTwist: HEAD_TO_ACE * 0.35, headYaw: HEAD_TO_ACE * 0.65, headPitch: -0.28, lShPitch: 0.28}),
];

const AND1_FACE: Key[] = [
  F(0, 'serious', {gazeY: 0.5, smile: 0.1}),
  F(0.42, 'triumph', {gazeY: 0}),
  F(0.62, 'shout', {gazeX: 0, gazeY: 0.05}),
  F(1.75, 'triumph', {smile: 0.55}),
  F(1.95, 'triumph', {smile: 0.55}),
  // scene 2: dismissive
  F(4.9, 'neutral', {gazeX: 0}, 'step'),
  F(5.1, 'smug', {lid: 0.85}),
  F(5.72, 'smug', {lid: 0.8, gazeX: 0.3}),
  // scene 3
  F(5.74, 'serious', {gazeY: 0.55, smile: 0.15}, 'step'),
  F(6.3, 'triumph', {gazeY: 0.3, smile: 0.3}),
  F(6.72, 'shout', {gazeX: 0.25, gazeY: 0}),
  F(8.05, 'outrage', {gazeX: 0.25, smile: -0.1}),
  F(9.5, 'annoyed', {gazeX: 0.25}, 'step'),
  F(9.8, 'annoyed', {gazeX: 0.3, lid: 0.42, squint: 0.65}),
  // scene 4
  F(10.25, 'smug', {lid: 0.15, gazeX: 0, gazeY: 0.1, smile: 0.35}, 'step'),
  F(11.3, 'smug', {lid: 0.15, smile: 0.35}),
  F(11.42, 'shock'),
  F(12.0, 'shock', {open: 0.3}),
  F(12.2, {browL: 0.2, browR: 0.2, browTilt: 0.5, lid: 0.35, squint: 0, smile: -0.2, open: 0.05, wide: 0.9, gazeX: 0, gazeY: 0}),
  F(12.48, 'outrage', {gazeY: 0.25}),
  F(13.55, 'outrage', {gazeY: 0.2}),
  F(13.9, 'annoyed', {gazeY: 0, gazeX: 0.2}),
  // scene 5: looking away, slow turn; stays SERIOUS
  F(16.0, 'serious', {gazeX: -0.1, gazeY: -0.1}),
  F(18.05, 'serious', {gazeX: 0.0, gazeY: -0.1}),
  F(18.4, 'serious', {gazeX: 0.6, gazeY: 0.2}),
  F(18.95, 'serious', {gazeX: 0.1, gazeY: 0.42, lid: 0.22}),
  // scene 6: dead serious punchline
  F(19.4, 'serious', {gazeX: 0.0, gazeY: 0.45, lid: 0.2, browTilt: -0.3}),
  F(20.5, 'serious', {gazeX: 0.0, gazeY: 0.45, lid: 0.24, browTilt: -0.35}),
  F(24.4, 'serious', {gazeX: 0.0, gazeY: 0.45, lid: 0.24, browTilt: -0.35}),
];

// ================= ACE =================
const ACE_BODY: Key[] = [
  K(0, {...MV.RELAXED, x: ACE_1[0], z: ACE_1[1], yaw: Y_ACE_A1 + 0.2, headYaw: 0.1}),
  // scene 2: slow head turn to AND1
  K(2.0, {...MV.RELAXED, x: ACE_1[0], z: ACE_1[1], yaw: Y_ACE_A1 + 0.2, headYaw: 0.55, headPitch: 0.05}),
  K(2.62, {...MV.RELAXED, yaw: Y_ACE_A1 + 0.2, headYaw: -0.12, headPitch: 0.0}, 'smooth'),
  K(3.7, {headRoll: 0.05}),
  K(4.4, {headRoll: 0.09, headPitch: 0.03}),
  // scene 3: arms crossed, facing the shooter
  K(5.74, {...MV.CROSSED, x: ACE_1[0], z: ACE_1[1], yaw: Y_ACE_SHOT, headYaw: 0, headRoll: 0, headPitch: 0}, 'step'),
  K(8.4, {...MV.CROSSED, yaw: Y_ACE_SHOT, headRoll: 0.03}),
  K(9.2, {...MV.CROSSED, yaw: Y_ACE_SHOT, headRoll: 0.1, headPitch: 0.04}),
  // scene 4: left wing; looks around the empty court
  K(10.25, {...MV.RELAXED, x: ACE_2[0], z: ACE_2[1], yaw: Y_ACE2, headYaw: 0, headRoll: 0, headPitch: 0}, 'step'),
  K(13.85, {...MV.RELAXED, yaw: Y_ACE2, headYaw: 0, headPitch: 0.08, lShOut: 0.4, rShOut: 0.4, lElbow: 0.9, rElbow: 0.9, lShPitch: 0.35, rShPitch: 0.35}),
  K(14.2, {headYaw: 0.85, headPitch: 0.0, spineTwist: 0.18}),
  K(14.4, {headYaw: 0.85, spineTwist: 0.18}),
  K(14.75, {headYaw: -0.85, spineTwist: -0.18}),
  K(14.92, {headYaw: -0.85, spineTwist: -0.18}),
  // scene 5: walks over (gait layer), stops at AND1's side, looks down at him
  K(15.05, {...MV.RELAXED, headYaw: 0, spineTwist: 0, headPitch: 0.15, x: ACE_2[0], z: ACE_2[1], yaw: faceTo(ACE_2, ACE_3), lShOut: 0.14, rShOut: 0.14, lElbow: 0.3, rElbow: 0.3, lShPitch: 0.05, rShPitch: 0.05}),
  K(16.75, {x: ACE_3[0], z: ACE_3[1], yaw: faceTo(ACE_2, ACE_3), headPitch: 0.3}, 'smooth'),
  K(16.95, {yaw: Y_ACE3, headPitch: 0.34}),
  K(17.2, {...MV.RELAXED, x: ACE_3[0], z: ACE_3[1], yaw: Y_ACE3, headPitch: 0.36, headRoll: 0.06}),
  K(21.3, {...MV.RELAXED, x: ACE_3[0], z: ACE_3[1], yaw: Y_ACE3, headPitch: 0.38, headRoll: 0.06}),
  // scene 7: turns his head to the camera; gives up
  K(21.85, {headPitch: 0.02, headYaw: 0.42, headRoll: 0.0, spineTwist: 0.12}),
  K(23.3, {headPitch: 0.04, headYaw: 0.42, headRoll: 0.03, spineBend: 0.06, lShOut: 0.1, rShOut: 0.1}),
  K(24.4, {headPitch: 0.04, headYaw: 0.42, headRoll: 0.03, spineBend: 0.06}),
];

const ACE_FACE: Key[] = [
  F(0, 'flat', {gazeX: 0.2}),
  F(2.0, 'flat', {gazeX: 0.6}),
  F(2.55, 'flat', {gazeX: -0.1, lid: 0.25, browL: 0.25, browR: 0.1}),
  F(2.85, 'deadpan', {gazeX: -0.1}),
  F(3.75, 'doubt', {gazeX: -0.1}),
  F(4.9, 'deadpan', {gazeX: -0.1}),
  F(5.74, 'deadpan', {gazeX: 0, lid: 0.4}, 'step'),
  F(8.3, 'deadpan', {lid: 0.5}),
  F(8.6, 'deadpan', {lid: 0.52, smile: -0.18}),
  F(9.4, 'doubt', {lid: 0.45, browL: 0.55}),
  F(10.25, 'flat', {gazeX: 0}, 'step'),
  F(13.85, 'lookAround', {gazeX: 0}),
  F(14.2, 'lookAround', {gazeX: 0.85}),
  F(14.42, 'lookAround', {gazeX: 0.85}),
  F(14.75, 'lookAround', {gazeX: -0.85}),
  F(14.95, 'lookAround', {gazeX: -0.85}),
  F(15.15, 'flat', {gazeX: 0, gazeY: -0.25}),
  F(16.0, 'deadpan', {gazeY: -0.45, lid: 0.35}),
  F(17.8, 'deadpan', {gazeY: -0.45, lid: 0.38}),
  F(19.9, 'deadpan', {gazeY: -0.5, lid: 0.3, browL: 0.3, browR: 0.3}),
  F(20.4, {browL: 0.55, browR: 0.5, browTilt: 0.3, lid: 0.18, squint: 0, smile: -0.25, open: 0.0, wide: 0.85, gazeY: -0.5}),
  F(21.3, 'done', {gazeY: -0.5, gazeX: 0, lid: 0.3}),
  F(21.8, 'done', {gazeY: 0, gazeX: -0.3, lid: 0.22, browL: 0.35, browR: 0.2}),
  F(24.4, 'done', {gazeY: 0, gazeX: -0.3, lid: 0.24, browL: 0.4, browR: 0.22}),
];

// blinks (start times); lids close over 0.06 s and open over 0.1 s. Long blink = [t, 0.35]
const BLINKS: Record<'AND1' | 'ACE', [number, number?][]> = {
  AND1: [[1.85], [5.05], [9.62], [12.25], [16.6], [17.7], [19.05], [20.95, 0.18], [22.9]],
  ACE: [[0.9], [2.52], [4.65], [8.25], [9.45], [13.95], [15.6], [17.95], [20.6], [22.45, 0.42], [23.9]],
};

const blinkAt = (who: 'AND1' | 'ACE', t: number) => {
  let v = 0;
  for (const [t0, hold = 0.02] of BLINKS[who]) {
    const u = t - t0;
    if (u < 0 || u > 0.06 + hold + 0.1) continue;
    v = Math.max(v, u < 0.06 ? u / 0.06 : u < 0.06 + hold ? 1 : 1 - (u - 0.06 - hold) / 0.1);
  }
  return v;
};

const mouthAt = (who: 'AND1' | 'ACE', t: number) => {
  const arr = LINES.mouth[who];
  const f = t * FPS;
  const i = Math.floor(f);
  const a = arr[i] ?? 0;
  const b = arr[i + 1] ?? 0;
  return lerp(a, b, f - i);
};

// ---------- procedural gait (steps) for the drive and ACE's walk ----------
type Gait = {t0: number; t1: number; stride: number; amp: number; run: boolean; dribble?: boolean};
const GAITS: Record<'AND1' | 'ACE', Gait[]> = {
  AND1: [{t0: 10.25, t1: 11.36, stride: 0.95, amp: 1, run: true, dribble: true}],
  ACE: [{t0: 15.05, t1: 16.8, stride: 0.74, amp: 0.85, run: false}],
};

const rootAt = (keys: Key[], t: number): V2 => {
  const p = evalKeys(POSE0, keys, t);
  return [p.x, p.z];
};

const gaitPhase = (keys: Key[], g: Gait, t: number) => {
  // distance travelled since g.t0 (numerical), -> step phase
  let d = 0;
  let prev = rootAt(keys, g.t0);
  const n = 24;
  for (let i = 1; i <= n; i++) {
    const ti = g.t0 + ((t - g.t0) * i) / n;
    const p = rootAt(keys, ti);
    d += Math.hypot(p[0] - prev[0], p[1] - prev[1]);
    prev = p;
  }
  return (d / g.stride) * Math.PI;
};

const applyGait = (who: 'AND1' | 'ACE', keys: Key[], p: Pose, t: number): {pose: Pose; phase: number; active: boolean} => {
  for (const g of GAITS[who]) {
    if (t < g.t0 || t > g.t1 + 0.25) continue;
    const env = clamp((t - g.t0) / 0.15) * clamp((g.t1 + 0.25 - t) / 0.25);
    const ph = gaitPhase(keys, g, Math.min(t, g.t1));
    const s = Math.sin(ph);
    const c = Math.cos(ph);
    const a = g.amp * env;
    const run = g.run;
    const q = {...p};
    q.lHip += a * (run ? 0.7 : 0.45) * s;
    q.rHip -= a * (run ? 0.7 : 0.45) * s;
    q.lKnee += a * ((run ? 0.35 : 0.12) + (run ? 0.95 : 0.6) * Math.max(0, -Math.sin(ph - 0.7)));
    q.rKnee += a * ((run ? 0.35 : 0.12) + (run ? 0.95 : 0.6) * Math.max(0, Math.sin(ph - 0.7)));
    q.lAnkle += a * 0.25 * Math.max(0, s);
    q.rAnkle += a * 0.25 * Math.max(0, -s);
    q.lShPitch -= a * (run ? 0.55 : 0.3) * s;
    if (!g.dribble) q.rShPitch += a * (run ? 0.55 : 0.3) * s;
    q.spineTwist += a * 0.08 * s;
    q.roll += a * 0.03 * c;
    q.lift += run ? a * 0.05 * Math.abs(Math.cos(ph)) : 0;
    if (g.dribble) {
      // dribbling hand pumps once per step pair
      const d = 0.5 + 0.5 * Math.cos(ph);
      q.rShPitch = lerp(0.25, 0.5, d);
      q.rElbow = lerp(0.6, 1.05, d);
      q.rShOut = 0.32;
    }
    return {pose: q, phase: ph, active: true};
  }
  return {pose: p, phase: 0, active: false};
};

export const poseAt = (who: 'AND1' | 'ACE', t: number): Pose => {
  const body = who === 'AND1' ? AND1_BODY : ACE_BODY;
  const face = who === 'AND1' ? AND1_FACE : ACE_FACE;
  let p = evalKeys(POSE0, body, t);
  p = applyGait(who, body, p, t).pose;
  const fp = evalKeys(POSE0, face, t).face;
  // breathing + idle micro motion
  const br = Math.sin(t * 2.2 + (who === 'AND1' ? 0 : 1.3));
  const m = mouthAt(who, t);
  const talk = Math.sin(t * 17) * 0.5 + 0.5;
  p = {
    ...p,
    spineBend: p.spineBend + 0.012 * br,
    headPitch: p.headPitch - 0.008 * br + m * 0.05 * (who === 'AND1' ? -1.3 : 0.6) * talk,
    face: {
      ...fp,
      lid: Math.min(1, fp.lid + (1 - fp.lid) * blinkAt(who, t)),
      // talking brows: AND1 brows jump with loudness
      browL: fp.browL + (who === 'AND1' ? m * 0.25 : m * 0.06),
      browR: fp.browR + (who === 'AND1' ? m * 0.25 : m * 0.06),
    },
  };
  return p;
};

export const mouthOf = mouthAt;

// ---------- ball ----------
const arc = (a: THREE.Vector3, b: THREE.Vector3, h: number, u: number) => {
  const p = a.clone().lerp(b, u);
  p.y += 4 * h * u * (1 - u);
  return p;
};
const bounceRoll = (from: THREE.Vector3, to: THREE.Vector3, u: number, h0: number) => {
  // decaying bounces from `from` (on the floor) to `to` (rests)
  const p = from.clone().lerp(to, 1 - (1 - u) ** 2);
  const seg = [0.45, 0.3, 0.25];
  let acc = 0;
  let h = h0;
  for (const s of seg) {
    if (u < acc + s) {
      const v = (u - acc) / s;
      p.y = 0.121 + 4 * h * v * (1 - v);
      return p;
    }
    acc += s;
    h *= 0.35;
  }
  p.y = 0.121;
  return p;
};

const handBall = (who: 'AND1' | 'ACE', t: number, side: 'l' | 'r' = 'r') => ballInHand(fk(poseAt(who, t), 1.06), side);
const twoHand = (t: number) => {
  const s = fk(poseAt('AND1', t), 1.06);
  return ballInHand(s, 'l').add(ballInHand(s, 'r')).multiplyScalar(0.5);
};

const RIM_TOP = RIM.clone().add(new THREE.Vector3(0, 0.15, 0));
const FLOOR_UNDER_RIM = new THREE.Vector3(0.05, 0.121, -1.45);
const AIRBALL_LAND = new THREE.Vector3(-1.55, 0.121, -0.85);

export const ballAt = (t: number): {pos: THREE.Vector3; spin: number} => {
  if (t < 0.3) {
    const a = handBall('AND1', 0);
    return {pos: arc(a, RIM_TOP, 0.12, smooth(t / 0.3)), spin: t * 6};
  }
  if (t < 0.62) {
    const u = (t - 0.3) / 0.32;
    const p = RIM_TOP.clone().lerp(FLOOR_UNDER_RIM, u);
    p.y = lerp(RIM_TOP.y, 0.121, u * u);
    return {pos: p, spin: t * 6};
  }
  if (t < 5.74) {
    const u = clamp((t - 0.62) / 1.6);
    return {pos: bounceRoll(FLOOR_UNDER_RIM, new THREE.Vector3(-0.9, 0.121, -0.2), u, 0.55), spin: t * 4};
  }
  if (t < 6.0) return {pos: twoHand(t), spin: 0};
  if (t < 6.62) {
    const a = handBall('AND1', 6.0);
    return {pos: arc(a, AIRBALL_LAND, 1.5, (t - 6.0) / 0.62), spin: t * 8};
  }
  if (t < 10.25) {
    const u = clamp((t - 6.62) / 1.8);
    return {pos: bounceRoll(AIRBALL_LAND, new THREE.Vector3(-2.6, 0.121, 0.6), u, 0.6), spin: t * 5};
  }
  if (t < 11.36) {
    // dribble: hand height -> floor once per step pair, beside the right foot
    const g = GAITS.AND1[0];
    const ph = gaitPhase(AND1_BODY, g, t);
    const s = fk(poseAt('AND1', t), 1.06);
    const hand = ballInHand(s, 'r');
    const root = bonePos(s, 'root');
    const fwd = new THREE.Vector3(Math.sin(Y_RUN), 0, Math.cos(Y_RUN));
    const k = Math.abs(Math.cos(ph / 2));
    const p = hand.clone().add(fwd.multiplyScalar(0.12));
    p.y = lerp(0.121, hand.y, k);
    void root;
    return {pos: p, spin: t * 3};
  }
  // trip: the ball squirts forward and rolls away to the left
  const start = handBall('AND1', 11.36);
  const land = new THREE.Vector3(0.6, 0.121, -2.6);
  if (t < 11.7) return {pos: arc(start, land, 0.25, (t - 11.36) / 0.34), spin: t * 9};
  const u = clamp((t - 11.7) / 2.4);
  return {pos: bounceRoll(land, new THREE.Vector3(-1.9, 0.121, -1.2), u, 0.35), spin: t * 4};
};

export const swishAt = (t: number) => (t > 0.3 && t < 0.95 ? (t - 0.3) / 0.65 : 0);

// ---------- cameras ----------
const headOf = (who: 'AND1' | 'ACE', t: number) => {
  const s = fk(poseAt(who, t), who === 'AND1' ? 1.06 : 1);
  return new THREE.Vector3(0, D.headY, 0.02).applyMatrix4(s.head);
};
const V = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
const arr = (v: THREE.Vector3): [number, number, number] => [v.x, v.y, v.z];

export type Shot = {id: string; t0: number; t1: number; cam: (t: number) => Cam; focus: [number, number, number]};

/** camera that frames a head from a direction (dist, side offset, height offset), with a slow push */
const frameHead = (who: 'AND1' | 'ACE', at: number, toward: V2, dist: number, side: number, dy: number, fov: number, push = 0.04, tdy = 0) => {
  const h = headOf(who, at);
  const dir = V(toward[0] - h.x, 0, toward[1] - h.z).normalize();
  const left = V(dir.z, 0, -dir.x);
  const pos = h.clone().add(dir.clone().multiplyScalar(dist)).add(left.multiplyScalar(side));
  pos.y = h.y + dy;
  const target = h.clone();
  target.y += tdy;
  return {pos, target, fov, push};
};

const still = (c: {pos: THREE.Vector3; target: THREE.Vector3; fov: number; push: number}, t0: number, t1: number) => (t: number): Cam => {
  const u = smooth((t - t0) / (t1 - t0));
  const pos = c.pos.clone().lerp(c.target, c.push * u);
  return {pos: arr(pos), target: arr(c.target), fov: c.fov};
};

const SHOTS_DEF = (): Shot[] => {
  const s: Shot[] = [];
  // A — wide: layup with nobody near; AND1 turns to camera
  s.push({id: 'A_hook', t0: 0, t1: 1.95, focus: [0.5, 1, -2.2], cam: (t) => {
    const u = smooth(t / 1.95);
    return {pos: arr(V(...CAM_A).lerp(V(3.5, 1.5, -3.7), u)), target: [lerp(0.0, 0.3, u), lerp(1.85, 1.4, u), lerp(-2.0, -2.1, u)], fov: 47};
  }});
  // B — ACE slow look + "Bro, nobody touched you."
  s.push({id: 'B_ace', t0: 1.95, t1: 4.97, focus: [ACE_1[0], 1.3, ACE_1[1]], cam: still(frameHead('ACE', 2.62, A_LAY, 2.0, -0.38, -0.05, 30, 0.06, -0.2), 1.95, 4.97)});
  // C — AND1 dismissive wave
  s.push({id: 'C_wave', t0: 4.97, t1: 5.74, focus: [A_LAY[0], 1.3, A_LAY[1]], cam: still(frameHead('AND1', 5.2, ACE_1, 2.6, 0.35, -0.1, 34, 0.05, -0.38), 4.97, 5.74)});
  // D — wide from behind the shooter: wide open, misses badly
  s.push({id: 'D_shot', t0: 5.74, t1: 6.78, focus: [0.4, 1, -3.5], cam: (t) => {
    const u = smooth((t - 5.74) / 1.04);
    return {pos: arr(V(2.9, 2.2, -10.6).lerp(V(2.6, 2.3, -9.9), u)), target: [lerp(0.0, -0.4, u), lerp(1.9, 1.4, u), -2.6], fov: 50};
  }});
  // E — AND1 chop: "AND ONE!"
  s.push({id: 'E_chop', t0: 6.78, t1: 8.15, focus: [A_SHOT[0], 1.2, A_SHOT[1]], cam: still(frameHead('AND1', 7.2, ACE_1, 2.5, 0.45, -0.25, 36, 0.06, -0.38), 6.78, 8.15)});
  // F — ACE: "You missed."
  s.push({id: 'F_missed', t0: 8.15, t1: 9.55, focus: [ACE_1[0], 1.3, ACE_1[1]], cam: still(frameHead('ACE', 8.6, A_SHOT, 1.75, 0.2, -0.03, 30, 0.08, -0.2), 8.15, 9.55)});
  // G — AND1 annoyed close-up
  s.push({id: 'G_annoyed', t0: 9.55, t1: 10.25, focus: [A_SHOT[0], 1.3, A_SHOT[1]], cam: still(frameHead('AND1', 9.9, ACE_1, 1.45, 0.15, -0.02, 30, 0.06, -0.14), 9.55, 10.25)});
  // H — high wide: drive, trip, spin, sit, "FOUL!" on an empty court
  s.push({id: 'H_trip', t0: 10.25, t1: 13.78, focus: [1.8, 0.8, -4.2], cam: (t) => {
    const u = smooth((t - 10.25) / 3.53);
    return {pos: arr(V(6.4, 3.4, -1.3).lerp(V(5.6, 2.9, -1.6), u)), target: [lerp(1.6, 0.6, u), lerp(1.0, 0.7, u), lerp(-4.8, -4.3, u)], fov: 54};
  }});
  // I — ACE looks around the empty court
  s.push({id: 'I_look', t0: 13.78, t1: 15.32, focus: [ACE_2[0], 1.2, ACE_2[1]], cam: still(frameHead('ACE', 14.0, A_SEAT, 2.6, -0.4, -0.3, 40, 0.04, -0.35), 13.78, 15.32)});
  // J — low over AND1's shoulder: ACE walks over, "Who fouled you?"; silence; AND1 turns
  s.push({id: 'J_who', t0: 15.32, t1: 18.75, focus: [0.6, 1, -4.2], cam: (t) => {
    const a = V(A_SEAT[0], 0, A_SEAT[1]);
    const dir = V(ACE_3[0] - a.x, 0, ACE_3[1] - a.z).normalize();
    const right = V(-dir.z, 0, dir.x);
    const pos = a.clone().add(dir.clone().multiplyScalar(-1.45)).add(right.multiplyScalar(0.8));
    pos.y = 1.3;
    const u = smooth((t - 15.32) / 3.43);
    // follow ACE's head (slightly lagged) as he walks in, then settle between the two
    const h = headOf('ACE', Math.min(t, 17.2));
    const tgt = V(h.x, lerp(h.y - 0.25, h.y - 0.45, u), h.z).lerp(V(A_SEAT[0], 0.9, A_SEAT[1]), 0.12 * u);
    return {pos: arr(pos.lerp(tgt, 0.06 * u)), target: arr(tgt), fov: 46};
  }});
  // K — AND1 close-up: points at the floor. "The floor."
  s.push({id: 'K_floor', t0: 18.75, t1: 21.25, focus: [A_SEAT[0], 0.8, A_SEAT[1]], cam: (t) => {
    const c = frameHead('AND1', 19.6, ACE_3, 1.95, 0.7, 0.15, 46, 0, -0.52);
    // slow push-in that lands right after "floor."
    const u = smooth((t - 18.75) / 2.0);
    const pos = c.pos.clone().lerp(c.target, 0.1 * u);
    return {pos: arr(pos), target: arr(c.target), fov: c.fov};
  }});
  // L — ACE looks into the lens. Speechless.
  s.push({id: 'L_done', t0: 21.25, t1: DURATION, focus: [ACE_3[0], 1.3, ACE_3[1]], cam: (t) => {
    const h = headOf('ACE', 22.4);
    const yaw = Y_ACE3 + 0.42 + 0.12;
    const dir = V(Math.sin(yaw), 0, Math.cos(yaw));
    const pos = h.clone().add(dir.multiplyScalar(1.95));
    pos.y = h.y + 0.03;
    const u = smooth((t - 21.25) / 3.1);
    return {pos: arr(pos.lerp(h, 0.1 * u)), target: [h.x, h.y - 0.2, h.z], fov: 30};
  }});
  return s;
};

let SHOTS_CACHE: Shot[] | null = null;
export const SHOTS = () => (SHOTS_CACHE ??= SHOTS_DEF());

// ---------- captions ----------
export const HIGHLIGHT = new Set(['L1', 'L3', 'L4', 'L7']);
/** caption vertical centre per shot (px from top, 1920 frame) — kept clear of faces and YouTube UI */
export const CAPTION_Y: Record<string, number> = {
  A_hook: 1300, B_ace: 1330, C_wave: 1330, D_shot: 1300, E_chop: 1320, F_missed: 1330, G_annoyed: 1350, H_trip: 1300, I_look: 1330, J_who: 1300, K_floor: 1340, L_done: 1320,
};
