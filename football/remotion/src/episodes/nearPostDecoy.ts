// FB-SETPIECE-001 V05 — "Short corner: near-post decoy + late arrival" (training proposal, fictional teams).
// Play data: football/tactical-library/plays/FB-PLAY-SP001-V05-near-post-decoy-late-arrival.json, built from
// FB-SETPIECE-001-V05.spec.json by tactical-library/setpieces/gen/FB-SETPIECE-001-V05.gen.py: attackers + keeper
// authored, every outfield defender driven by behaviours (mark / zone / press / chase) — validated by
// fb_motion.py (rules + physics) and fb_tactics.py (tactical checks).
// Play times: short corner A7 -> A10 3.0 (D4 presses) · return 4.3 -> 4.95 (TRIGGER) · A4 near-post decoy
// 4.1-6.25 (D7 follows) · A9 second run 4.85-7.1 (D8 follows, D5 shifts to the near post) · A6 late run from
// D9's blind side 4.4-7.75 · cutback A7 -> A6 6.5 -> 7.75 · first-time finish 7.75, line 8.33 · D1 dives 7.92.
import playJson from '../../../tactical-library/plays/FB-PLAY-SP001-V05-near-post-decoy-late-arrival.json';
import type {Episode} from '../FBTactical3D';
import type {FBPlay, V2} from '../play';
import type {Word} from '../screen';
import {GOLD, RED, WHITE} from '../brand';

const play = playJson as unknown as FBPlay;

const line = (start: number, end: number, text: string): Word[] => {
  const ws = text.split(/\s+/).filter(Boolean);
  const weight = ws.map((w) => 0.6 + w.replace(/[^A-Za-z0-9]/g, '').length);
  const total = weight.reduce((a, b) => a + b, 0);
  let t = start;
  return ws.map((w, i) => {
    const d = ((end - start) * weight[i]) / total;
    const out: Word = {text: w, start: t, end: t + d * 0.92, br: i === ws.length - 1};
    t += d;
    return out;
  });
};

/** narration for Deuce (English), timed to this cut; NOT rendered in the silent version (no voice generated) */
export const SCRIPT_V05: [number, number, string][] = [
  [0.2, 2.6, "The space isn't there. Until they create it."],
  [2.8, 4.6, 'Three markers, three zones, a man on the post.'],
  [4.9, 6.6, 'Short corner. The nearest defender presses.'],
  [6.8, 8.0, 'The return beats him.'],
  [8.3, 10.2, 'Now two runs attack the near post...'],
  [10.4, 12.0, '...and the central zone goes with them.'],
  [12.2, 14.0, 'The late runner arrives behind the edge defender.'],
  [14.3, 15.8, 'Cutback. First time. Far corner.'],
  [16.3, 18.6, 'Look again. The line shifts to the near post.'],
  [18.8, 20.6, 'The edge defender is facing the ball.'],
  [20.8, 22.4, 'Three metres. Enough to finish.'],
  [22.9, 25.6, 'Drag the line. Arrive late.'],
];
const words = SCRIPT_V05.flatMap(([a, b, s]) => line(a, b, s));

const D5_START: V2 = [47.5, -1.2];
const STRIKE: V2 = [43.25, -6.35];
const TARGET: V2 = [52.6, 3.15];
const CUT_AT: V2 = [50.35, -20.6];
const SETUP = {mode: 'overview' as const, focus: [{p: [47.2, -14.5] as V2}], dist: 52, elev: 62, azim: 90, fov: 38, lift: 0};

export const nearPostDecoyV05: Episode = {
  id: 'FB-SETPIECE-001',
  title: 'Short corner: near-post decoy + late arrival',
  duration: 27.6,
  play,
  words,
  keywords: ['space', 'markers', 'zones', 'presses', 'near', 'late', 'line', 'shifts', 'cutback'],
  look: 'day',
  grade: 'clean',
  graphicsV2: true,
  subtitles: false,
  shots: [
    // 01 · HOOK + STRUCTURE (0-3.6): a fast push from the attacking third onto an organised box; the mixed
    // defence is drawn while the hook is on screen (no pure panorama)
    {
      name: 'hook-structure',
      from: 0,
      remap: [[0, 0.4], [3.6, 2.3]],
      cam: [
        {at: 0, mode: 'overview', focus: [{p: [38, -14]}], dist: 86, elev: 58, azim: 78, fov: 38, spline: true},
        {at: 1.5, ...SETUP, dist: 57},
        {at: 3.6, ...SETUP},
      ],
      ov: [
        {from: 0.9, type: 'link', a: 'D7', b: 'A4', color: WHITE},
        {from: 1.0, type: 'link', a: 'D8', b: 'A9', color: WHITE},
        {from: 1.1, type: 'link', a: 'D10', b: 'A5', color: WHITE},
        {from: 1.5, type: 'ring', player: 'D3', color: RED, r: 0.7},
        {from: 1.6, type: 'ring', player: 'D5', color: RED, r: 0.7},
        {from: 1.7, type: 'ring', player: 'D6', color: RED, r: 0.7},
      ],
      screen: [
        {from: 0.08, to: 3.5, type: 'title', lines: ["THE SPACE ISN'T THERE.", 'UNTIL THEY CREATE IT.'], gold: [1], y: 1180, size: 86},
        {from: 1.9, to: 3.6, type: 'chip', p: [43.0, -13.0], z: 0.2, text: 'MAN + ZONE', tone: 'white', dy: 0, dx: 0},
      ],
    },
    // 02 · CORNER ACTION (3.6-8.0): short corner, D4 presses, the return beats him (play 2.3 -> 5.3, 0.68x)
    {
      name: 'corner-action',
      from: 3.6,
      remap: [[0, 2.3], [4.4, 5.3]],
      cam: [
        {at: 0, mode: 'tracking', focus: [{player: 'A7'}, {player: 'A10'}, {player: 'D4', w: 0.8}], dist: 21, elev: 40, azim: -42, fov: 36, lift: 2.2, spline: true},
        {at: 2.4, mode: 'tracking', focus: [{player: 'A10'}, {player: 'D4'}, {player: 'A7', w: 0.9}], dist: 19.5, elev: 40, azim: -36, fov: 36, lift: 2.4},
        {at: 4.4, mode: 'tracking', focus: [{player: 'A7'}, {ball: true, w: 0.6}, {player: 'D4', w: 0.5}], dist: 23, elev: 42, azim: -22, fov: 36, lift: 3.4},
      ],
      ov: [
        {from: 0.95, to: 2.4, type: 'pass', t0: 3.0, t1: 3.7, color: GOLD, trail: true},
        {from: 1.2, to: 4.4, type: 'run', player: 'D4', t0: 3.0, t1: 5.3, color: RED, trail: true},
        {from: 2.85, to: 4.0, type: 'pass', t0: 4.3, t1: 4.95, color: GOLD, trail: true},
        {from: 3.75, type: 'ring', player: 'A7', color: GOLD},
      ],
      screen: [
        {from: 1.3, to: 2.8, type: 'chip', player: 'D4', text: 'PRESSES', tone: 'red', dy: 130, dx: -60},
        {from: 2.9, to: 3.75, type: 'chip', player: 'A10', text: 'RETURN', tone: 'gold', dy: 120, dx: -90},
        {from: 3.8, to: 4.4, type: 'chip', player: 'A7', text: 'TRIGGER', tone: 'gold', dy: 130, dx: 40},
      ],
    },
    // 03 · TACTICAL ACTION (8.0-14.2): one camera holds the ball, the passer, the shifted line, the late runner
    // and the finishing zone (play 5.3 -> 8.5, slower around the cutback)
    {
      name: 'tactical-action',
      from: 8.0,
      remap: [[0, 5.3], [2.3, 6.45], [4.4, 7.7], [6.2, 8.5]],
      cam: [
        {at: 0, mode: 'overview', focus: [{p: [44.2, -10.5]}], dist: 39, elev: 50, azim: 92, fov: 36, lift: 0.5, spline: true},
        {at: 2.6, mode: 'overview', focus: [{p: [46.0, -10.0]}], dist: 35, elev: 46, azim: 94, fov: 36, lift: 0.6},
        {at: 6.2, mode: 'tracking', focus: [{player: 'A6', w: 0.8}, {p: [51.6, 0.5], w: 1.2}], dist: 25, elev: 36, azim: 70, fov: 36, lift: 0.4},
      ],
      ov: [
        {from: 0, to: 1.6, type: 'link', a: 'D7', b: 'A4', color: WHITE},
        {from: 0, to: 2.0, type: 'link', a: 'D8', b: 'A9', color: WHITE},
        {from: 0.1, to: 4.4, type: 'run', player: 'A4', t0: 4.4, t1: 6.6, color: WHITE, trail: true},
        {from: 0.3, to: 4.4, type: 'run', player: 'A9', t0: 5.0, t1: 7.2, color: WHITE, trail: true},
        {from: 0.9, to: 4.4, type: 'circle', c: D5_START, r: 0.62, color: WHITE, dashed: true, width: 0.05},
        {from: 0.9, to: 4.4, type: 'run', player: 'D5', t0: 5.6, t1: 7.3, color: RED, trail: true},
        {from: 1.2, to: 2.9, type: 'cone', player: 'D9', dir: 'heading', len: 4, half: 0.45, color: WHITE, opacity: 0.22},
        {from: 1.4, to: 4.6, type: 'run', player: 'A6', t0: 5.4, t1: 7.75, color: GOLD, trail: true},
        {from: 2.2, to: 3.6, type: 'cone', p: CUT_AT, dir: STRIKE, len: 15, half: 0.07, color: GOLD, opacity: 0.32},
        {from: 2.25, to: 4.6, type: 'pass', t0: 6.5, t1: 7.75, color: GOLD, trail: true},
        {from: 4.25, to: 5.6, type: 'cone', player: 'A6', dir: TARGET, len: 9.6, half: 0.075, color: GOLD, opacity: 0.3},
        {from: 4.4, to: 6.2, type: 'pass', t0: 7.75, t1: 8.33, color: GOLD, trail: true, width: 0.09},
      ],
      screen: [
        {from: 0.4, to: 1.8, type: 'chip', player: 'A4', text: 'DECOY', tone: 'white', dy: 120, dx: 60},
        {from: 1.0, to: 2.4, type: 'chip', player: 'D5', text: 'LINE SHIFTS', tone: 'red', dy: -120, dx: 60},
        {from: 1.6, to: 3.2, type: 'chip', player: 'A6', text: 'LATE RUN', tone: 'gold', dy: 120, dx: -40},
        {from: 2.3, to: 3.5, type: 'chip', player: 'A7', text: 'CUTBACK', tone: 'gold', dy: 120, dx: 40},
      ],
    },
    // 04 · GOAL CAMERA (14.2-16.0): behind the goal, the strike, the keeper set and diving, the net (0.6x)
    {
      name: 'goal-camera',
      from: 14.2,
      remap: [[0, 7.62], [1.8, 8.7]],
      cam: [
        {at: 0, mode: 'detail', focus: [{p: [50.8, -0.6]}], dist: 9.2, elev: 11, azim: 194, fov: 44, z: 0.9},
        {at: 1.8, mode: 'detail', focus: [{p: [51.0, 0.4]}], dist: 8.0, elev: 12, azim: 190, fov: 44, z: 0.9},
      ],
    },
    // 05 · ANALYTICAL REPLAY (16.0-22.6): from above, same orientation as the opening; the shift, the
    // defender's orientation, the timing of the late run, the window, the lane (one short pause at the cutback)
    {
      name: 'replay',
      from: 16.0,
      remap: [[0, 4.6], [2.7, 6.5], [3.3, 6.5], [5.2, 7.95], [6.6, 8.45]],
      freeze: [[2.7, 3.3]],
      cam: [
        {at: 0, mode: 'overview', focus: [{p: [45.0, -10.5]}], dist: 39, elev: 68, azim: 90, fov: 38, lift: 0, spline: true},
        {at: 3.0, mode: 'overview', focus: [{p: [46.0, -10.0]}], dist: 37, elev: 70, azim: 90, fov: 38, lift: 0},
        {at: 6.6, mode: 'overview', focus: [{p: [47.6, -7.0]}], dist: 33, elev: 70, azim: 90, fov: 38, lift: 0},
      ],
      ov: [
        {from: 0.1, type: 'circle', c: D5_START, r: 0.62, color: WHITE, dashed: true, width: 0.05},
        {from: 0.1, type: 'run', player: 'D5', t0: 5.0, t1: 7.6, color: RED, trail: true},
        {from: 0.2, type: 'run', player: 'A4', t0: 4.6, t1: 6.6, color: WHITE, trail: true},
        {from: 0.2, type: 'run', player: 'A9', t0: 5.0, t1: 7.2, color: WHITE, trail: true},
        {from: 0.4, to: 3.3, type: 'cone', player: 'D9', dir: 'heading', len: 4.5, half: 0.45, color: WHITE, opacity: 0.24},
        {from: 0.4, type: 'run', player: 'A6', t0: 4.6, t1: 7.75, color: GOLD, trail: true},
        {from: 2.7, to: 3.9, type: 'cone', p: CUT_AT, dir: STRIKE, len: 15, half: 0.07, color: GOLD, opacity: 0.34},
        {from: 2.75, type: 'pass', t0: 6.5, t1: 7.75, color: GOLD, trail: true},
        {from: 4.9, to: 6.6, type: 'cone', player: 'A6', dir: TARGET, len: 9.6, half: 0.075, color: GOLD, opacity: 0.32},
        {from: 5.2, type: 'pass', t0: 7.75, t1: 8.33, color: GOLD, trail: true, width: 0.09},
      ],
      screen: [
        {from: 0, to: 6.6, type: 'tag', text: 'REPLAY', icon: 'replay'},
        {from: 0.6, to: 2.6, type: 'chip', player: 'D5', text: 'LINE SHIFTS', tone: 'red', dy: -110, dx: 80},
        {from: 1.2, to: 3.3, type: 'chip', player: 'D9', text: 'FACING THE BALL', tone: 'white', dy: 120, dx: 150},
        {from: 2.75, to: 3.3, type: 'chip', player: 'A6', text: 'ARRIVES NOW', tone: 'gold', dy: -120, dx: -60},
        {from: 4.0, to: 5.6, type: 'chip', player: 'A6', text: '3 M', tone: 'gold', dy: 120, dx: -40},
      ],
    },
    // 06 · TACTICAL CONCLUSION (22.6-26.4): the finished picture from above, the lesson
    {
      name: 'payoff',
      from: 22.6,
      remap: [[0, 9.2], [3.8, 10.4]],
      cam: [
        {at: 0, mode: 'overview', focus: [{p: [47.6, -7.0]}], dist: 33, elev: 70, azim: 90, fov: 38},
        {at: 3.8, mode: 'overview', focus: [{p: [47.8, -6.4]}], dist: 31, elev: 71, azim: 90, fov: 38},
      ],
      ov: [
        {from: 0, type: 'circle', c: D5_START, r: 0.62, color: WHITE, dashed: true, width: 0.05},
        {from: 0, type: 'run', player: 'D5', t0: 5.0, t1: 7.6, color: RED, draw: 0.4},
        {from: 0.1, type: 'run', player: 'A4', t0: 4.6, t1: 6.6, color: WHITE, draw: 0.4},
        {from: 0.15, type: 'run', player: 'A9', t0: 5.0, t1: 7.2, color: WHITE, draw: 0.4},
        {from: 0.3, type: 'run', player: 'A6', t0: 4.6, t1: 7.75, color: GOLD, draw: 0.5},
        {from: 0.5, type: 'pass', t0: 6.5, t1: 7.75, color: GOLD, draw: 0.5},
        {from: 0.75, type: 'pass', t0: 7.75, t1: 8.33, color: GOLD, draw: 0.35, width: 0.09},
      ],
      screen: [{from: 0.9, to: 3.8, type: 'title', lines: ['DRAG THE LINE.', 'ARRIVE LATE.'], gold: [1], y: 1250, size: 100}],
    },
    // 07 · END (26.4-27.6)
    {
      name: 'end',
      from: 26.4,
      remap: [[0, 10.4]],
      cam: [{at: 0, mode: 'overview', focus: [{p: [47.8, -6.4]}], dist: 31, elev: 71, azim: 90, fov: 38}],
      screen: [
        {from: 0, type: 'scrim', opacity: 0.86},
        {from: 0.1, type: 'end'},
      ],
    },
  ],
};

/** V06 (after the V05 review in motion): the hook ends closer on the box (players were small), the tactical
 *  action keeps the passer off the frame edge, and the goal camera is wider and turned towards the shooter so
 *  the strike, the ball path and the keeper's dive are in one picture. Play, graphics and timing unchanged. */
const v05 = nearPostDecoyV05.shots;
export const nearPostDecoyV06: Episode = {
  ...nearPostDecoyV05,
  shots: [
    {...v05[0], cam: [v05[0].cam[0], {...v05[0].cam[1], dist: 52}, {...v05[0].cam[2], focus: [{p: [47.4, -11.5]}], dist: 46}]},
    v05[1],
    {
      ...v05[2],
      cam: [
        {...v05[2].cam[0], focus: [{p: [44.8, -12.0]}]},
        {...v05[2].cam[1], focus: [{p: [46.0, -11.4]}]},
        v05[2].cam[2],
      ],
      // LINE SHIFTS under D5 (it sat on top of DECOY in V05)
      screen: v05[2].screen!.map((x) => (x.type === 'chip' && x.text === 'LINE SHIFTS' ? {...x, dy: 130, dx: 110} : x)),
    },
    {
      ...v05[3],
      cam: [
        {at: 0, mode: 'detail', focus: [{p: [49.4, -2.2]}], dist: 12.5, elev: 12, azim: 202, fov: 50, z: 0.9},
        {at: 1.8, mode: 'detail', focus: [{p: [50.2, -0.6]}], dist: 11.0, elev: 12, azim: 198, fov: 50, z: 0.9},
      ],
    },
    {
      ...v05[4],
      // FACING THE BALL and ARRIVES NOW stacked on each other in the V05 pause: one at a time, apart
      screen: v05[4].screen!.map((x) =>
        x.type === 'chip' && x.text === 'FACING THE BALL' ? {...x, to: 2.6} : x.type === 'chip' && x.text === 'ARRIVES NOW' ? {...x, dy: 130, dx: 120} : x,
      ),
    },
    ...v05.slice(5),
  ],
};
