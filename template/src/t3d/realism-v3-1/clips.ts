// E2A Realism V3.1 (2026-11-22) — AUTHORED clips. Every number below is HAND-KEYED (timed against the fixture
// tactical/plays/realism-v3-1-onetake.json, 30 fps). No motion capture, no retargeted library, no paid asset.
// The tactical track stays the root constraint: step landing spots are offsets {f forward, l lateral (+ right)} from
// the root at the landing time, in the heading frame at that time (motion.ts anchors and locks them).
//
// Timeline of the one-take (brief V3.1 sec. 8):
//   0.00-1.50 ready / intent (load at 1.1-1.45)      1.50-3.00 accelerate (7 steps, forward lean 0.5 -> 0.25)
//   3.00-4.50 brake (heel strikes, counter-lean) + right-foot plant at 3.28 + 80 deg cut to the left (shoulders lead)
//   4.50-6.00 catch of O2's pass at 4.933 (hands meet the ball), give into the pocket, 1-2 stop, front pivot to the rim
//   6.00-7.00 jab, ONE bounce (6.15 push / 6.42 floor / 6.72 back in the hand) on a step-back, 1-2 gather
//   7.00-9.50 read, dip 7.6-7.95, jump 7.95-8.58, release 8.20 (engine release point), follow-through held to the make
//   9.50-11.5 recover, back-pedal 10.0-11.1, widen into a defensive stance     11.5-12.5 hold
import type {Play} from '../../tactical/play.ts';

export type Key = [number, number];
/** one footstep: side 0 = left / 1 = right, lift / land times, landing offsets, optional foot yaw (relative to the
 *  heading), swing height h, heel = landing pitch (- = heel strike / toes up, + = lands on the ball of the foot),
 *  toeOff = heel rise before the lift, air = jump (follows the ballistic pelvis) */
export type Step = {s: 0 | 1; lift: number; land: number; f: number; l: number; yaw?: number; h?: number; heel?: number; toeOff?: number; air?: boolean};
export type ArmKey = {t: number; m: 'ready' | 'run' | 'brake' | 'reach' | 'give' | 'pocket' | 'triple' | 'jab' | 'dribble' | 'gather' | 'set' | 'shoot' | 'follow' | 'land' | 'defense'; b: number};
export type Clip31 = {
  label: string;
  heading: Key[];
  chest: Key[];
  lean: Key[];
  roll: Key[];
  pelvisRoll?: Key[];
  drop: Key[];
  init: [{f: number; l: number; yaw?: number}, {f: number; l: number; yaw?: number}];
  steps: Step[];
  pivots: {s: 0 | 1; t0: number; t1: number; dyaw: number}[];
  jump?: {t0: number; t1: number; H: number};
  look: {t: number; at: string | number; b?: number}[];
  arms: ArmKey[];
  ball: {catchT?: number; releaseT?: number; dribble?: {push: number; floor: number; catch: number}};
  back?: [number, number];
};

// fixture geometry (tactical/specs/_gen-realism-v3-1-onetake.py)
const hA = -1.0184; // A -> B (acceleration line)
const hCut = 0.384; // B -> C (22 deg, an 80 deg cut to the left)
const hCatch = 0.66; // between the run (22 deg) and the passer at the top of the key (71 deg)
const hRim = -1.19; // C1 / D toward the rim

const ONETAKE_O1: Clip31 = {
  label: 'hand-keyed V3.1 one-take (O1)',
  heading: [[0, hA], [2.95, hA], [3.28, hA + 0.45], [3.62, hCut], [4.45, hCut], [4.93, hCatch], [5.28, hCatch], [5.86, hRim], [12.5, hRim]],
  // shoulders lead the cut and the pivot, counter-rotate on the plant, shooting shoulder slightly forward
  chest: [[0, 0], [2.95, 0], [3.15, 0.38], [3.32, 0.55], [3.62, 0.12], [4.4, 0.06], [4.85, 0.2], [5.22, 0.05], [5.42, -0.38], [5.86, 0], [6.1, 0.08], [7.9, 0.15], [8.65, 0.12], [9.3, 0], [12.5, 0]],
  lean: [[0, 0.14], [1.1, 0.14], [1.45, 0.34], [1.75, 0.52], [2.35, 0.32], [2.85, 0.22], [3.08, -0.06], [3.3, -0.2], [3.5, 0.28], [3.9, 0.3], [4.6, 0.2], [4.93, 0.12],
    [5.2, 0.22], [5.7, 0.24], [6.02, 0.3], [6.18, 0.38], [6.55, 0.12], [6.9, 0.24], [7.4, 0.14], [7.62, 0.14], [7.88, 0.27], [7.98, 0.06], [8.2, 0.0], [8.58, 0.06], [8.76, 0.26],
    [9.05, 0.12], [9.9, 0.1], [10.2, 0.04], [10.9, 0.14], [11.35, 0.36], [12.5, 0.36]],
  // + = bank to the left: into the left cut on the right-foot plant
  roll: [[0, 0], [2.95, 0], [3.12, 0.08], [3.3, 0.22], [3.55, 0.3], [3.85, 0.1], [4.2, 0], [5.3, 0], [5.55, -0.1], [5.86, 0], [12.5, 0]],
  // the pelvis drops on the plant side (right) while the trunk banks left
  pelvisRoll: [[0, 0], [3.1, 0], [3.3, -0.1], [3.55, -0.04], [3.8, 0], [12.5, 0]],
  drop: [[0, 0.07], [1.1, 0.07], [1.45, 0.14], [1.72, 0.1], [2.7, 0.07], [3.05, 0.11], [3.3, 0.18], [3.5, 0.13], [3.8, 0.08], [4.6, 0.08], [4.93, 0.1], [5.18, 0.14],
    [5.6, 0.12], [6.0, 0.14], [6.18, 0.15], [6.55, 0.11], [6.85, 0.16], [7.2, 0.11], [7.6, 0.1], [7.88, 0.21], [7.96, 0.0], [8.58, 0.02], [8.76, 0.21], [9.08, 0.09],
    [9.8, 0.06], [10.1, 0.08], [11.0, 0.12], [11.38, 0.2], [12.5, 0.2]],
  init: [{f: 0.06, l: -0.17}, {f: -0.12, l: 0.19}],
  steps: [
    // acceleration (forefoot, short ground contacts)
    {s: 1, lift: 1.55, land: 1.8, f: 0.1, l: 0.1, heel: 0.12, toeOff: 0.55, h: 0.13},
    {s: 0, lift: 1.74, land: 1.98, f: 0.12, l: -0.09, heel: 0.08, h: 0.14},
    {s: 1, lift: 1.93, land: 2.15, f: 0.14, l: 0.08, heel: 0.05, h: 0.15},
    {s: 0, lift: 2.1, land: 2.31, f: 0.15, l: -0.08, h: 0.16},
    {s: 1, lift: 2.27, land: 2.47, f: 0.16, l: 0.08, h: 0.16},
    {s: 0, lift: 2.43, land: 2.63, f: 0.16, l: -0.08, h: 0.16},
    {s: 1, lift: 2.59, land: 2.79, f: 0.18, l: 0.08, h: 0.15},
    // brake: heel strikes ahead of the body, then the wide right-foot plant turned into the cut
    {s: 0, lift: 2.75, land: 2.96, f: 0.3, l: -0.1, heel: -0.28, h: 0.12},
    {s: 1, lift: 2.97, land: 3.28, f: 0.36, l: 0.36, yaw: 0.5, heel: -0.22, h: 0.11},
    // cut: open step with the left foot, push off the plant, run to the catch
    {s: 0, lift: 3.3, land: 3.52, f: 0.18, l: -0.12, h: 0.1},
    {s: 1, lift: 3.46, land: 3.72, f: 0.2, l: 0.09, toeOff: 0.6, h: 0.14},
    {s: 0, lift: 3.67, land: 3.92, f: 0.2, l: -0.08, h: 0.14},
    {s: 1, lift: 3.88, land: 4.12, f: 0.2, l: 0.08, h: 0.14},
    {s: 0, lift: 4.08, land: 4.32, f: 0.2, l: -0.08, h: 0.13},
    {s: 1, lift: 4.28, land: 4.52, f: 0.19, l: 0.08, h: 0.12},
    {s: 0, lift: 4.48, land: 4.72, f: 0.18, l: -0.09, h: 0.11},
    // 1-2 stop with the catch
    {s: 1, lift: 4.68, land: 4.93, f: 0.16, l: 0.12, heel: -0.16, h: 0.1},
    {s: 0, lift: 4.9, land: 5.12, f: 0.2, l: -0.18, heel: -0.1, h: 0.08},
    // front pivot on the right foot to face the rim: the left foot swings round
    {s: 0, lift: 5.32, land: 5.8, f: 0.04, l: -0.2, h: 0.07, toeOff: 0.2},
    {s: 1, lift: 5.84, land: 6.0, f: 0.0, l: 0.19, h: 0.05, toeOff: 0.2},
    // jab, step-back with the bounce, 1-2 gather
    {s: 1, lift: 6.04, land: 6.16, f: 0.3, l: 0.17, heel: -0.08, h: 0.06},
    {s: 1, lift: 6.24, land: 6.52, f: -0.14, l: 0.2, h: 0.1, toeOff: 0.5},
    {s: 0, lift: 6.38, land: 6.68, f: -0.06, l: -0.2, h: 0.1},
    {s: 1, lift: 6.74, land: 6.92, f: 0.05, l: 0.18, h: 0.06},
    {s: 0, lift: 6.86, land: 7.04, f: -0.02, l: -0.18, h: 0.06},
    // jump shot: both feet leave at 7.95 and land on the balls of the feet at 8.58, a few cm forward
    {s: 1, lift: 7.95, land: 8.58, f: 0.1, l: 0.17, heel: 0.32, air: true},
    {s: 0, lift: 7.95, land: 8.58, f: 0.08, l: -0.17, heel: 0.32, air: true},
    {s: 0, lift: 9.05, land: 9.3, f: 0.0, l: -0.2, h: 0.05, toeOff: 0.2},
    // back-pedal (facing the rim), then widen into the stance
    {s: 1, lift: 10.0, land: 10.2, f: -0.04, l: 0.15, h: 0.07, toeOff: 0.25},
    {s: 0, lift: 10.15, land: 10.38, f: -0.04, l: -0.15, h: 0.07, toeOff: 0.25},
    {s: 1, lift: 10.33, land: 10.56, f: -0.04, l: 0.15, h: 0.07, toeOff: 0.25},
    {s: 0, lift: 10.51, land: 10.74, f: -0.04, l: -0.15, h: 0.07, toeOff: 0.25},
    {s: 1, lift: 10.69, land: 10.92, f: -0.03, l: 0.15, h: 0.07, toeOff: 0.25},
    {s: 0, lift: 10.87, land: 11.1, f: 0.0, l: -0.16, h: 0.06, toeOff: 0.2},
    {s: 0, lift: 11.12, land: 11.32, f: 0.03, l: -0.36, h: 0.05, toeOff: 0.15},
    {s: 1, lift: 11.24, land: 11.44, f: -0.03, l: 0.36, h: 0.05, toeOff: 0.15},
  ],
  pivots: [{s: 1, t0: 5.3, t1: 5.84, dyaw: -1.65}],
  jump: {t0: 7.95, t1: 8.58, H: 0.4},
  // the head leads: into the cut before the body, onto the passer, the ball in flight, the rim
  look: [{t: 0, at: 'path'}, {t: 1.2, at: 'path'}, {t: 2.95, at: hCut, b: 0.22}, {t: 3.5, at: 'O2', b: 0.3}, {t: 4.55, at: 'ball', b: 0.2}, {t: 5.08, at: 'rim', b: 0.35},
    {t: 8.25, at: 'ball', b: 0.25}, {t: 9.3, at: 'rim', b: 0.4}, {t: 10.05, at: 'O2', b: 0.45}],
  arms: [{t: 0, m: 'ready', b: 0}, {t: 1.5, m: 'run', b: 0.22}, {t: 2.98, m: 'brake', b: 0.18}, {t: 3.42, m: 'run', b: 0.22}, {t: 4.5, m: 'reach', b: 0.3},
    {t: 4.9333, m: 'give', b: 0}, {t: 5.35, m: 'pocket', b: 0.2}, {t: 5.85, m: 'triple', b: 0.22}, {t: 6.04, m: 'jab', b: 0.1}, {t: 6.15, m: 'dribble', b: 0.18},
    {t: 6.72, m: 'gather', b: 0.08}, {t: 7.2, m: 'pocket', b: 0.25}, {t: 7.72, m: 'set', b: 0.26}, {t: 8.0, m: 'shoot', b: 0}, {t: 8.2, m: 'follow', b: 0.14},
    {t: 8.95, m: 'land', b: 0.45}, {t: 9.5, m: 'ready', b: 0.4}, {t: 10.0, m: 'run', b: 0.3}, {t: 11.0, m: 'defense', b: 0.45}],
  ball: {catchT: 148 / 30, releaseT: 246 / 30, dribble: {push: 6.15, floor: 6.42, catch: 6.72}},
  back: [9.9, 11.2],
};

const CLIPS: Record<string, Record<string, Clip31>> = {
  'realism-v3-1-onetake': {O1: ONETAKE_O1},
};

/** the authored clip of a player in a play (by play id; benchmark copies use the `v31clip` field of the play), or null */
export const clipFor = (play: Play, id: string): Clip31 | null => {
  const src = (play as Play & {v31clip?: Record<string, string>}).v31clip;
  if (src?.[id]) {
    const [pid, pl] = src[id].split(':');
    return CLIPS[pid]?.[pl] ?? null;
  }
  return CLIPS[play.id]?.[id] ?? null;
};
