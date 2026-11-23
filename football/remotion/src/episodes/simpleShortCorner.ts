// FB-SETPIECE-001 — "The simple short corner" (Set Pieces Studio, level 1).
// Play data: football/tactical-library/plays/FB-PLAY-SP001-simple-short-corner.json, built and validated by
// football/scripts/fb_motion.py from FB-SETPIECE-001.spec.json (fictional teams).
// Play times: idle 0-1.55 · A (7) run-up 1.55-3.0 · short corner A->B at 3.0, B (10) controls at 3.85 ·
// D (4) closes B 3.0-5.25 · A support run 3.0-6.25 · B returns it at 5.4, A controls at 6.25 · end 7.6.
import playJson from '../../../tactical-library/plays/FB-PLAY-SP001-simple-short-corner.json';
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

/** chosen script: VERSION A (educational) — every line describes what is on screen at that moment */
export const SCRIPT: [number, number, string][] = [
  [0.15, 2.3, 'One pass. One defender out of position.'],
  [2.7, 4.3, 'Short corner. Player A takes it.'],
  [4.4, 5.9, 'B offers a short option. D guards the space.'],
  [6.2, 8.0, 'A plays it short, along the ground.'],
  [8.2, 9.8, 'B controls it.'],
  [10.2, 12.0, 'D steps out to close B down.'],
  [12.2, 13.9, 'Look where he was standing.'],
  [14.2, 15.9, 'A runs into that space.'],
  [16.0, 17.8, 'B gives it back. A is onside.'],
  [18.2, 19.9, 'Now A has time on the ball,'],
  [20.0, 21.8, 'and a free lane towards the box.'],
  [22.2, 24.4, 'One short pass moved one defender.'],
];

const words = SCRIPT.flatMap(([a, b, s]) => line(a, b, s));

const CORNER: V2 = [52.5, -34];
const D_START: V2 = [45.6, -25.4];
const SPACE: V2 = [50.2, -27.3];
const LANE_END: V2 = [49.6, -22.2];

export const simpleShortCorner: Episode = {
  id: 'FB-SETPIECE-001',
  title: 'The simple short corner',
  duration: 25,
  play,
  words,
  keywords: ['short', 'space', 'onside', 'time', 'free', 'lane', 'one'],
  subtitleHide: [[0, 2.5]],
  subtitleY: 1345,
  shots: [
    // 01 · HOOK (0-2.5): camera B, the end of the move in slow motion: D has left, A is free
    {
      name: 'hook',
      from: 0,
      remap: [[0, 5.15], [2.5, 6.6]],
      cam: [
        {at: 0, mode: 'tracking', focus: [{player: 'A7'}, {player: 'D4', w: 0.7}, {ball: true, w: 0.5}], dist: 18, elev: 34, azim: -55, fov: 34, lift: 2.5},
        {at: 2.5, mode: 'tracking', focus: [{player: 'A7'}, {player: 'D4', w: 0.7}, {ball: true, w: 0.5}], dist: 16.5, elev: 36, azim: -47, fov: 34, lift: 2.5},
      ],
      ov: [
        {from: 0.2, type: 'ring', player: 'D4', color: RED},
        {from: 1.2, type: 'ring', player: 'A7', color: GOLD},
        {from: 1.3, type: 'zone', c: SPACE, r: [2.2, 2.2], color: GOLD},
      ],
      screen: [
        {from: 0.05, to: 1.2, type: 'title', lines: ['ONE PASS.'], y: 330, size: 124},
        {from: 1.2, to: 2.5, type: 'title', lines: ['ONE DEFENDER', 'OUT OF POSITION.'], gold: [1], y: 330, size: 104},
      ],
    },
    // 02 · SETUP (2.5-6): camera A, the starting picture, who is who, the 9.15 m and the short option
    {
      name: 'setup',
      from: 2.5,
      flash: 0.25,
      remap: [[0, 0.2], [3.5, 1.5]],
      cam: [
        {at: 0, mode: 'overview', focus: [{p: [49.4, -30.4]}], dist: 18.5, elev: 55, azim: -40, fov: 40, lift: 1.2},
        {at: 3.5, mode: 'overview', focus: [{p: [49.4, -30.4]}], dist: 17.5, elev: 53, azim: -37, fov: 40, lift: 1.2},
      ],
      ov: [
        {from: 0.2, type: 'ring', player: 'A7', color: GOLD},
        {from: 0.55, type: 'ring', player: 'A10', color: GOLD},
        {from: 0.9, type: 'ring', player: 'D4', color: RED},
        {from: 1.6, type: 'circle', c: CORNER, r: 10.15, arc: [Math.PI / 2, Math.PI], color: WHITE, dashed: true, width: 0.06},
        {from: 2.3, type: 'arrow', p0: [51.7, -33.2], p1: [48.3, -31.15], color: GOLD, dashed: true, width: 0.12},
      ],
      screen: [
        {from: 0.25, to: 1.65, type: 'pin', player: 'A7', text: 'A', tone: 'gold', dy: 120, size: 50},
        {from: 0.6, type: 'pin', player: 'A10', text: 'B', tone: 'gold', dy: 120, size: 50},
        {from: 0.95, type: 'pin', player: 'D4', text: 'D', tone: 'red', dy: 120, size: 50},
        {from: 1.7, to: 3.5, type: 'stamp', text: '9.15 M UNTIL THE KICK', y: 310, tone: 'white'},
      ],
    },
    // 03 · THE SHORT PASS (6-10): camera B follows the ball, discreetly
    {
      name: 'short-pass',
      from: 6.0,
      flash: 0.2,
      remap: [[0, 1.6], [4.0, 4.6]],
      cam: [
        {at: 0, mode: 'tracking', focus: [{player: 'A7'}, {ball: true}, {player: 'A10', w: 1}], dist: 16.5, elev: 34, azim: -24, fov: 38, lift: 4.2},
        {at: 2.2, mode: 'tracking', focus: [{ball: true}, {player: 'A10', w: 0.8}, {player: 'A7', w: 0.4}], dist: 13.5, elev: 32, azim: -18, fov: 36, lift: 3},
        {at: 4.0, mode: 'tracking', focus: [{player: 'A10'}, {player: 'D4', w: 0.6}, {player: 'A7', w: 0.4}], dist: 14, elev: 34, azim: -20, fov: 36, lift: 3},
      ],
      ov: [
        {from: 0, to: 1.8, type: 'ring', player: 'A7', color: GOLD},
        {from: 1.85, type: 'pass', t0: 3.0, t1: 3.85, color: GOLD, trail: true},
        {from: 2.6, type: 'ring', player: 'A10', color: GOLD},
      ],
      screen: [{from: 0.2, to: 1.8, type: 'tag', text: 'SLOW-MO', icon: 'slow'}],
    },
    // 04 · DEFENSIVE MOVEMENT (10-14): camera A, D closes B, freeze on where D came from
    {
      name: 'defence',
      from: 10.0,
      flash: 0.2,
      remap: [[0, 3.55], [2.4, 5.25]],
      cam: [
        {at: 0, mode: 'overview', focus: [{player: 'D4'}, {player: 'A10', w: 0.6}, {p: D_START, w: 1}], dist: 15, elev: 56, azim: -40, fov: 38, lift: 3},
        {at: 4.0, mode: 'overview', focus: [{player: 'D4'}, {player: 'A10', w: 0.6}, {p: D_START, w: 1}], dist: 14.5, elev: 58, azim: -36, fov: 38, lift: 3},
      ],
      ov: [
        {from: 0.1, type: 'ring', player: 'D4', color: RED},
        {from: 0.3, type: 'run', player: 'D4', t0: 3.0, t1: 5.25, color: RED, draw: 2.0},
        {from: 2.4, type: 'circle', c: D_START, r: 0.9, color: WHITE, dashed: true},
      ],
      screen: [
        {from: 0.5, to: 2.4, type: 'pin', player: 'D4', text: 'D STEPS OUT', tone: 'red', dy: 140, dx: -120},
        {from: 2.5, type: 'pin', p: D_START, z: 0.2, text: 'HE WAS HERE', tone: 'white', dy: 150, size: 40},
        {from: 2.4, type: 'tag', text: 'PAUSE', icon: 'pause'},
      ],
      freeze: [[2.4, 4.0]],
    },
    // 05 · THE SUPPORT RUN (14-18): camera B on A's run, the return pass, onside at the pass
    {
      name: 'support-run',
      from: 14.0,
      flash: 0.2,
      remap: [[0, 3.75], [4.0, 6.35]],
      cam: [
        {at: 0, mode: 'tracking', focus: [{player: 'A7'}, {player: 'A10', w: 0.6}, {player: 'D4', w: 0.4}], dist: 15.5, elev: 46, azim: -36, fov: 34, lift: 3},
        {at: 4.0, mode: 'tracking', focus: [{player: 'A7'}, {player: 'A10', w: 0.4}, {player: 'D4', w: 0.4}], dist: 15, elev: 48, azim: -40, fov: 34, lift: 2.2},
      ],
      ov: [
        {from: 0.1, type: 'ring', player: 'A7', color: GOLD},
        {from: 0.2, type: 'run', player: 'A7', t0: 3.75, t1: 6.25, color: GOLD, dashed: true, draw: 1.6},
        {from: 2.55, to: 3.9, type: 'offside', at: 5.4, color: WHITE, span: [-34, -24]},
        {from: 2.5, type: 'pass', t0: 5.4, t1: 6.25, color: GOLD, trail: true},
      ],
      screen: [
        {from: 0.3, to: 2.4, type: 'pin', player: 'A7', text: 'A RUNS INTO IT', tone: 'gold', dy: 140, dx: -80, size: 40},
        {from: 2.6, to: 3.95, type: 'stamp', text: 'ONSIDE', y: 310, tone: 'gold', badge: '✓'},
      ],
    },
    // 06 · TACTICAL PAYOFF (18-22): camera A, A controls, freeze, the space and the new option
    {
      name: 'payoff',
      from: 18.0,
      flash: 0.25,
      remap: [[0, 6.2], [0.9, 6.75]],
      cam: [
        {at: 0, mode: 'overview', focus: [{player: 'A7'}, {player: 'D4', w: 0.6}, {p: D_START, w: 0.6}, {p: LANE_END, w: 0.5}], dist: 19, elev: 56, azim: -42, fov: 38, lift: 2.5},
        {at: 4.0, mode: 'overview', focus: [{player: 'A7'}, {player: 'D4', w: 0.6}, {p: D_START, w: 0.6}, {p: LANE_END, w: 0.5}], dist: 18, elev: 58, azim: -38, fov: 38, lift: 2.5},
      ],
      ov: [
        {from: 0.0, type: 'ring', player: 'A7', color: GOLD},
        {from: 0.9, type: 'zone', c: SPACE, r: [2.6, 2.6], color: GOLD},
        {from: 1.2, type: 'circle', c: D_START, r: 0.9, color: WHITE, dashed: true},
        {from: 1.2, type: 'run', player: 'D4', t0: 3.0, t1: 5.25, color: RED, draw: 0.8},
        {from: 2.2, type: 'arrow', p0: [50.2, -26.6], p1: LANE_END, color: GOLD, width: 0.16},
      ],
      screen: [
        {from: 0.9, type: 'tag', text: 'PAUSE', icon: 'pause'},
        {from: 1.0, to: 2.2, type: 'stamp', text: 'D PULLED OUT', y: 310, tone: 'red'},
        {from: 2.2, to: 4.0, type: 'stamp', text: 'TIME + A FREE LANE', y: 310, tone: 'gold'},
      ],
      freeze: [[0.9, 4.0]],
    },
    // 07 · FINAL REPLAY (22-25): camera A, the whole move at speed, ends on the open picture
    {
      name: 'replay',
      from: 22.0,
      flash: 0.3,
      remap: [[0, 2.2], [2.75, 6.6], [3.0, 6.75]],
      cam: [
        {at: 0, mode: 'overview', focus: [{p: [48.8, -29.6]}], dist: 18.5, elev: 54, azim: -40, fov: 40, lift: 2.8},
        {at: 3.0, mode: 'overview', focus: [{p: [49.0, -29.0]}], dist: 18, elev: 55, azim: -40, fov: 40, lift: 2.8},
      ],
      ov: [
        {from: 0.6, type: 'pass', t0: 3.0, t1: 3.85, color: GOLD, draw: 0.4},
        {from: 1.0, type: 'run', player: 'A7', t0: 3.0, t1: 6.25, color: GOLD, dashed: true, draw: 1.2},
        {from: 1.0, type: 'run', player: 'D4', t0: 3.0, t1: 5.25, color: RED, draw: 0.9},
        {from: 1.9, type: 'pass', t0: 5.4, t1: 6.25, color: GOLD, draw: 0.4},
      ],
      screen: [{from: 0, type: 'tag', text: 'REPLAY', icon: 'replay'}],
    },
  ],
};
