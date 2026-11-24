// FB-SETPIECE-001 V03 — "The short corner cutback" (Set Pieces Studio, level 1, rebuilt after the owner's V02 review).
// Play data: football/tactical-library/plays/FB-PLAY-SP001-V03-short-corner-cutback.json, built and validated by
// football/scripts/fb_motion.py from FB-SETPIECE-001-V03.spec.json (fictional teams, 11 v 11).
// Play times: A (7) run-up 1.5-3.0 · short corner A->B at 3.0, B (10) controls 3.85 · D (4) steps out 3.0-5.25 ·
// A runs the byline 3.0-6.05 · B returns it 5.3 -> 6.05 · A carries it 6.05-7.15 · E (8) is drawn to the near post
// 5.0-8.0 · C (9) checks away 5.5-6.3 and attacks the space 6.3-8.45 · cutback A->C 7.15 -> 8.45 · first-time
// side-foot finish 8.45, crosses the line 9.05, net 9.22 · keeper (D1) shifts near post, dives 8.6-9.15 · end 10.6.
import playJson from '../../../tactical-library/plays/FB-PLAY-SP001-V03-short-corner-cutback.json';
import type {Episode, Shot} from '../FBTactical3D';
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

/** narration for Deuce (English), timed to this cut; NOT rendered in the silent version */
export const SCRIPT: [number, number, string][] = [
  [0.2, 1.7, 'Three passes. One goal.'],
  [2.3, 4.2, 'Watch the defender on the edge of the box.'],
  [4.8, 6.4, 'The short pass draws him out.'],
  [7.6, 9.4, 'The return puts A on the byline.'],
  [10.0, 11.6, 'Now the box has to react.'],
  [11.8, 13.4, 'One cutback. One perfectly timed run.'],
  [13.6, 14.6, 'And the finish.'],
  [16.6, 19.0, 'Look again. One step out from D...'],
  [19.2, 21.4, 'E drops to protect the near post...'],
  [21.6, 23.4, 'and the space behind him is gone.'],
  [24.0, 26.6, 'Move the defender. Attack the space.'],
];
const words = SCRIPT.flatMap(([a, b, s]) => line(a, b, s));

const CORNER: V2 = [52.5, -34];
const D_START: V2 = [45.6, -25.4];
const SPACE: V2 = [44.8, -6.4];

// video time <-> play time helpers for each shot (the remaps below are linear between keys)
const OPEN: Shot = {
  name: 'opening',
  from: 0,
  remap: [[0, 0.5], [4.5, 2.75]],
  cam: [
    {at: 0, mode: 'overview', focus: [{p: [16, -8]}], dist: 118, elev: 57, azim: -14, fov: 38, spline: true},
    {at: 2.3, mode: 'overview', focus: [{p: [42, -16]}], dist: 66, elev: 56, azim: 30, fov: 38},
    {at: 4.5, mode: 'overview', focus: [{p: [47.6, -21.0]}], dist: 56, elev: 60, azim: 78, fov: 38, lift: 0},
  ],
  ov: [
    {from: 2.9, type: 'ring', player: 'A7', color: GOLD},
    {from: 3.1, type: 'ring', player: 'A10', color: GOLD},
    {from: 3.3, type: 'ring', player: 'D4', color: RED},
    {from: 3.5, type: 'ring', player: 'A9', color: GOLD},
  ],
  screen: [
    {from: 0.08, to: 1.95, type: 'title', lines: ['3 PASSES.', '1 GOAL.'], gold: [1], y: 300, size: 132},
    {from: 2.95, type: 'chip', player: 'A7', text: 'A', tone: 'gold', dy: 70, letter: true},
    {from: 3.15, type: 'chip', player: 'A10', text: 'B', tone: 'gold', dy: 70, letter: true},
    {from: 3.35, type: 'chip', player: 'D4', text: 'D', tone: 'red', dy: 70, letter: true},
    {from: 3.55, type: 'chip', player: 'A9', text: 'C', tone: 'gold', dy: 70, letter: true},
  ],
};

export const shortCornerCutback: Episode = {
  id: 'FB-SETPIECE-001',
  title: 'The short corner cutback',
  duration: 28.6,
  play,
  words,
  keywords: ['three', 'one', 'goal', 'defender', 'space', 'cutback', 'finish'],
  look: 'day',
  grade: 'clean',
  graphicsV2: true,
  subtitles: false,
  shots: [
    // 01 · HOOK + APPROACH + SETUP (0-4.5): ONE continuous move, stadium -> attacking third -> the corner
    OPEN,
    // 02 · CORNER ACTION (4.5-9.6): short pass, the defender steps out, the return (play 2.75 -> 6.2, 0.68x)
    {
      name: 'corner-action',
      from: 4.5,
      remap: [[0, 2.75], [5.1, 6.2]],
      cam: [
        {at: 0, mode: 'tracking', focus: [{player: 'A7'}, {player: 'A10'}, {player: 'D4', w: 0.8}], dist: 21, elev: 40, azim: -42, fov: 36, lift: 2.2, spline: true},
        {at: 2.6, mode: 'tracking', focus: [{player: 'A10'}, {player: 'D4'}, {player: 'A7', w: 0.9}], dist: 19.5, elev: 40, azim: -36, fov: 36, lift: 2.4},
        {at: 5.1, mode: 'tracking', focus: [{player: 'A7'}, {ball: true, w: 0.6}, {player: 'A10', w: 0.5}, {player: 'D4', w: 0.4}], dist: 21, elev: 40, azim: -26, fov: 36, lift: 3.2},
      ],
      ov: [
        {from: 0.35, to: 2.4, type: 'pass', t0: 3.0, t1: 3.85, color: GOLD, trail: true},
        {from: 1.55, to: 3.9, type: 'run', player: 'D4', t0: 3.0, t1: 5.25, color: RED, draw: 2.0},
        {from: 1.55, to: 3.9, type: 'circle', c: D_START, r: 0.62, color: WHITE, dashed: true, width: 0.05},
        {from: 3.75, type: 'pass', t0: 5.3, t1: 6.05, color: GOLD, trail: true},
        {from: 3.7, type: 'ring', player: 'A7', color: GOLD},
      ],
      screen: [
        {from: 0.4, to: 1.9, type: 'chip', player: 'A7', text: 'SHORT PASS', tone: 'gold', dy: 120, dx: -120},
        {from: 1.9, to: 3.7, type: 'chip', player: 'D4', text: 'DEFENDER STEPS OUT', tone: 'red', dy: 130, dx: -60},
        {from: 3.8, to: 5.1, type: 'chip', player: 'A10', text: 'RETURN', tone: 'gold', dy: 120, dx: -90},
      ],
    },
    // 03 · GOAL ACTION (9.6-14.6): the carry, E is drawn, C's run, cutback, first-time finish, the net (speed ramp)
    {
      name: 'goal-action',
      from: 9.6,
      remap: [[0, 6.2], [1.9, 7.9], [3.9, 8.75], [5.0, 9.6]],
      cam: [
        {at: 0, mode: 'tracking', focus: [{player: 'A7'}, {player: 'A9', w: 0.8}, {player: 'D8', w: 0.6}, {p: [51, -1], w: 0.6}], dist: 28, elev: 38, azim: 62, fov: 36, lift: 0.5, spline: true},
        {at: 2.4, mode: 'tracking', focus: [{ball: true}, {player: 'A9', w: 1.2}, {p: [51.5, 0], w: 0.7}], dist: 23, elev: 30, azim: 50, fov: 36, lift: 0.8},
        {at: 5.0, mode: 'tracking', focus: [{player: 'A9', w: 0.8}, {p: [52.2, 1.6], w: 1.2}], dist: 19, elev: 22, azim: 38, fov: 36, lift: 0.6},
      ],
      ov: [
        {from: 0.2, to: 2.2, type: 'ring', player: 'D8', color: RED},
        {from: 0.3, to: 2.6, type: 'run', player: 'D8', t0: 5.6, t1: 8.0, color: RED, draw: 1.6},
        {from: 0.6, to: 3.5, type: 'run', player: 'A9', t0: 6.3, t1: 8.45, color: GOLD, draw: 2.2},
        {from: 1.0, to: 3.6, type: 'pass', t0: 7.15, t1: 8.45, color: GOLD, trail: true},
        {from: 3.15, to: 5.0, type: 'pass', t0: 8.45, t1: 9.05, color: GOLD, trail: true, width: 0.09},
      ],
      screen: [
        {from: 1.0, to: 2.7, type: 'chip', player: 'A7', text: 'CUTBACK', tone: 'gold', dy: 120, dx: 60},
        {from: 3.15, to: 4.5, type: 'chip', player: 'A9', text: 'FINISH', tone: 'gold', dy: 230, dx: -200},
      ],
    },
    // 04 · BEHIND THE GOAL (14.6-16.4): the net bulges towards us, the keeper is beaten (0.55x)
    {
      name: 'behind-goal',
      from: 14.6,
      remap: [[0, 8.72], [1.8, 9.72]],
      cam: [
        {at: 0, mode: 'detail', focus: [{p: [51.2, 0.6]}], dist: 8.6, elev: 11, azim: 196, fov: 42, z: 0.9},
        {at: 1.8, mode: 'detail', focus: [{p: [51.2, 0.6]}], dist: 7.6, elev: 12, azim: 190, fov: 42, z: 0.9},
      ],
    },
    // 05 · TACTICAL REPLAY (16.4-23.6): the whole move from above, minimal graphics, one short pause on the space
    {
      name: 'replay',
      from: 16.4,
      remap: [[0, 2.8], [5.9, 8.05], [6.6, 8.05], [7.2, 9.0]],
      freeze: [[5.9, 6.6]],
      cam: [
        {at: 0, mode: 'overview', focus: [{p: [47.6, -21.0]}], dist: 56, elev: 62, azim: 80, fov: 38, lift: 0, spline: true},
        {at: 4.0, mode: 'overview', focus: [{p: [46.6, -16.0]}], dist: 48, elev: 63, azim: 78, fov: 38, lift: 0},
        {at: 7.2, mode: 'overview', focus: [{p: [47.0, -12.0]}], dist: 46, elev: 62, azim: 74, fov: 38, lift: 0},
      ],
      ov: [
        {from: 0.15, type: 'pass', t0: 3.0, t1: 3.85, color: GOLD, trail: true},
        {from: 0.3, type: 'circle', c: D_START, r: 0.62, color: WHITE, dashed: true, width: 0.05},
        {from: 0.3, type: 'run', player: 'D4', t0: 3.0, t1: 5.25, color: RED, draw: 2.4},
        {from: 0.3, type: 'run', player: 'A7', t0: 3.0, t1: 6.05, color: GOLD, draw: 3.3},
        {from: 2.75, type: 'pass', t0: 5.3, t1: 6.05, color: GOLD, trail: true},
        {from: 2.7, type: 'run', player: 'D8', t0: 5.0, t1: 8.0, color: RED, draw: 3.2},
        {from: 4.0, type: 'run', player: 'A9', t0: 6.3, t1: 8.45, color: GOLD, draw: 2.3},
        {from: 4.9, type: 'zone', c: SPACE, r: [2.4, 2.4], color: GOLD},
        {from: 4.9, type: 'pass', t0: 7.15, t1: 8.45, color: GOLD, trail: true},
        {from: 6.6, type: 'pass', t0: 8.45, t1: 9.05, color: GOLD, trail: true, width: 0.09},
      ],
      screen: [
        {from: 0, to: 7.2, type: 'tag', text: 'REPLAY', icon: 'replay'},
        {from: 0.6, to: 2.7, type: 'chip', player: 'D4', text: 'DEFENDER STEPS OUT', tone: 'red', dy: 110, dx: -40},
        {from: 5.95, to: 6.6, type: 'chip', p: SPACE, z: 0.2, text: 'THE SPACE', tone: 'gold', dy: 130, dx: -80},
      ],
    },
    // 06 · PAYOFF (23.6-27.4): the ball in the net, slow push, the lesson
    {
      name: 'payoff',
      from: 23.6,
      remap: [[0, 9.9], [3.8, 10.6]],
      cam: [
        {at: 0, mode: 'detail', focus: [{player: 'A9', w: 0.8}, {p: [53.2, 2.8], w: 1}], dist: 15, elev: 17, azim: 34, fov: 36, lift: -1.2},
        {at: 3.8, mode: 'detail', focus: [{player: 'A9', w: 0.8}, {p: [53.2, 2.8], w: 1}], dist: 12.5, elev: 15, azim: 40, fov: 36, lift: -1.2},
      ],
      screen: [{from: 0.2, to: 3.8, type: 'title', lines: ['MOVE THE DEFENDER.', 'ATTACK THE SPACE.'], gold: [1], y: 300, size: 96}],
    },
    // 07 · END (27.4-28.6)
    {
      name: 'end',
      from: 27.4,
      remap: [[0, 10.6]],
      cam: [{at: 0, mode: 'detail', focus: [{player: 'A9', w: 0.8}, {p: [53.2, 2.8], w: 1}], dist: 12.5, elev: 15, azim: 40, fov: 36, lift: -1.2}],
      screen: [
        {from: 0, type: 'scrim', opacity: 0.86},
        {from: 0.1, type: 'end'},
      ],
    },
  ],
};

/** hook test B: a 1.4 s goal teaser from behind the net, then the same continuous approach (shorter) */
export const shortCornerCutbackHookB: Episode = {
  ...shortCornerCutback,
  shots: [
    {
      name: 'teaser',
      from: 0,
      remap: [[0, 8.75], [1.4, 9.55]],
      cam: [
        {at: 0, mode: 'detail', focus: [{p: [51.2, 0.6]}], dist: 8.2, elev: 11, azim: 196, fov: 42, z: 0.9},
        {at: 1.4, mode: 'detail', focus: [{p: [51.2, 0.6]}], dist: 7.6, elev: 12, azim: 192, fov: 42, z: 0.9},
      ],
      screen: [{from: 0.05, type: 'title', lines: ['3 PASSES.', '1 GOAL.'], gold: [1], y: 300, size: 132}],
    },
    {
      ...OPEN,
      from: 1.4,
      remap: [[0, 1.2], [3.1, 2.75]],
      cam: [
        {...OPEN.cam[0], at: 0},
        {...OPEN.cam[1], at: 1.5},
        {...OPEN.cam[2], at: 3.1},
      ],
      ov: OPEN.ov!.map((o) => ({...o, from: o.from - 1.4})),
      screen: [
        {from: 0, to: 1.0, type: 'title', lines: ['HOW?'], y: 300, size: 132},
        ...OPEN.screen!.filter((x) => x.type === 'chip').map((x) => ({...x, from: x.from - 1.4})),
      ],
    },
    ...shortCornerCutback.shots.slice(1),
  ],
};

/** V04 (after the V03 inspection): FINISH label kept clear of the keeper and the goal mouth, and a stronger
 *  payoff — instead of a near-static shot of the keeper on the grass, the whole move is drawn over the final
 *  picture from above (D out, E drawn, C's run into the space, cutback and finish), then the lesson. */
const v03 = shortCornerCutback.shots;
export const shortCornerCutbackV04: Episode = {
  ...shortCornerCutback,
  shots: [
    ...v03.slice(0, 2),
    {
      ...v03[2],
      screen: v03[2].screen!.map((x) => (x.type === 'chip' && x.text === 'FINISH' ? {...x, dy: -150, dx: -170} : x)),
    },
    ...v03.slice(3, 5),
    {
      name: 'payoff',
      from: 23.6,
      remap: [[0, 9.6], [3.8, 10.6]],
      cam: [
        {at: 0, mode: 'overview', focus: [{p: [47.2, -11.5]}], dist: 44, elev: 62, azim: 74, fov: 38},
        {at: 3.8, mode: 'overview', focus: [{p: [47.4, -10.5]}], dist: 41.5, elev: 64, azim: 71, fov: 38},
      ],
      ov: [
        {from: 0.0, type: 'circle', c: D_START, r: 0.62, color: WHITE, dashed: true, width: 0.05},
        {from: 0.0, type: 'run', player: 'D4', t0: 3.0, t1: 5.25, color: RED, draw: 0.5},
        {from: 0.15, type: 'run', player: 'D8', t0: 5.0, t1: 8.0, color: RED, draw: 0.5},
        {from: 0.3, type: 'zone', c: SPACE, r: [2.4, 2.4], color: GOLD},
        {from: 0.45, type: 'run', player: 'A9', t0: 6.3, t1: 8.45, color: GOLD, draw: 0.5},
        {from: 0.6, type: 'pass', t0: 7.15, t1: 8.45, color: GOLD, draw: 0.5},
        {from: 0.8, type: 'pass', t0: 8.45, t1: 9.05, color: GOLD, draw: 0.4, width: 0.09},
      ],
      screen: [{from: 0.9, to: 3.8, type: 'title', lines: ['MOVE THE DEFENDER.', 'ATTACK THE SPACE.'], gold: [1], y: 1190, size: 96}],
    },
    v03[6],
  ],
};
