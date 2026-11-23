// FB-20261123-third-man-run — edit of VIDEO 001 "The third-man run" (concept FB-C01).
// Play data: football/tactical-library/plays/FB-PLAY-third-man-run.json (v2, fictional teams).
// Play times used below: build-up 0-3.0 · A6 passes into A9 at 3.9 (arrives 4.75) · D4 jumps with A9 ·
// A9 sets first time into the space at 5.0 · A8 receives behind the line at 6.2 · shot 7.4 · goal 8.5.
import playJson from '../../../tactical-library/plays/FB-PLAY-third-man-run.json';
import type {Episode} from '../FBTactical3D';
import type {FBPlay} from '../play';
import type {Word} from '../screen';
import {GOLD, RED, WHITE} from '../brand';

const play = playJson as unknown as FBPlay;

/** caption timing for the silent cut: words spread over each line's window by length.
 *  When the Deuce take exists, these are replaced by the real word timings of that take. */
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

export const SCRIPT: [number, number, string][] = [
  [0.15, 1.55, 'The defender follows the pass.'],
  [1.7, 2.85, "That's exactly the trap."],
  [3.25, 5.6, "Navy's six has the ball."],
  [5.75, 8.6, 'White are compact: no space between the lines.'],
  [9.05, 11.4, 'So the nine drops short.'],
  [11.6, 13.9, 'The centre-back jumps with him…'],
  [14.05, 16.5, '…and leaves a hole behind.'],
  [17.05, 18.9, 'Now watch the third man.'],
  [19.05, 21.7, 'He goes before the pass even arrives.'],
  [21.85, 24.6, 'His marker? Watching the ball.'],
  [25.05, 26.9, 'One touch into the space.'],
  [27.05, 28.9, 'Onside. Behind the line.'],
  [29.7, 30.05, 'Goal.'],
  [30.25, 32.0, "Great football isn't just about the pass."],
  [32.15, 34.0, "It's about the run nobody sees."],
];

const words = SCRIPT.flatMap(([a, b, s]) => line(a, b, s));

const HOLE: [number, number] = [14.6, 3.3];

export const thirdManRun: Episode = {
  id: 'FB-20261123-third-man-run',
  title: 'The third-man run',
  duration: 35,
  play,
  words,
  subtitleHide: [[0, 3.0], [30.1, 35]],
  keywords: ['trap', 'third', 'man', 'hole', 'space', 'onside', 'nobody', 'sees', 'goal.'],
  shots: [
    // 1 · HOOK (0-3 s): tracking from behind the play, D4 steps out with the 9, freeze on the trap
    {
      name: 'hook',
      from: 0,
      remap: [[0, 3.75], [1.55, 4.85], [1.95, 5.0]],
      cam: [
        {at: 0, mode: 'tracking', focus: [{player: 'A9'}, {player: 'D4'}], dist: 19, elev: 17, azim: 8, fov: 32},
        {at: 1.95, mode: 'tracking', focus: [{player: 'A9'}, {player: 'D4'}, {p: HOLE, w: 0.6}], dist: 15.5, elev: 21, azim: 2, fov: 32},
        {at: 3.0, mode: 'detail', focus: [{player: 'D4'}, {p: HOLE, w: 0.8}], dist: 14, elev: 26, azim: -6, fov: 32},
      ],
      ov: [
        {from: 0.35, to: 3.0, type: 'ring', player: 'D4', color: RED},
        {from: 1.1, to: 3.0, type: 'run', player: 'D4', t0: 3.75, t1: 5.0, color: RED, draw: 0.5},
        {from: 1.95, to: 3.0, type: 'zone', c: HOLE, r: [3.4, 3.2], color: GOLD},
      ],
      screen: [
        {from: 0.05, to: 1.62, type: 'title', lines: ['THE DEFENDER', 'FOLLOWS THE PASS.'], y: 330, size: 104},
        {from: 1.68, to: 3.0, type: 'title', lines: ["THAT'S", 'THE TRAP.'], gold: [1], y: 330, size: 118},
        {from: 1.95, to: 3.0, type: 'tag', text: 'PAUSE', icon: 'pause'},
      ],
      freeze: [[1.95, 3.0]],
    },
    // 2 · PROBLEM (3-9 s): tactical overview, the build-up at (slightly slowed) speed, compact block
    {
      name: 'problem',
      from: 3.0,
      flash: 0.3,
      remap: [[0, 0.3], [6.0, 3.75]],
      cam: [
        {at: 0, mode: 'overview', focus: [{p: [3, 0]}], dist: 46, elev: 56, azim: 0, fov: 46},
        {at: 6.0, mode: 'overview', focus: [{p: [5, 0.5]}], dist: 40, elev: 50, azim: 6, fov: 46},
      ],
      ov: [
        {from: 0.3, to: 6.0, type: 'ring', player: 'A6', color: GOLD},
        {from: 1.6, to: 6.0, type: 'defline', players: ['D3', 'D5', 'D4', 'D2'], color: WHITE},
        {from: 2.3, to: 6.0, type: 'defline', players: ['D11', 'D8', 'D6', 'D7'], color: WHITE},
        {from: 3.0, to: 6.0, type: 'zone', c: [8.6, 0.6], r: [4.4, 9.5], color: RED},
      ],
      screen: [
        {from: 0.4, to: 2.6, type: 'pin', player: 'A6', text: 'NAVY 6', tone: 'gold', dy: 150},
        {from: 1.2, to: 3.0, type: 'stamp', text: 'COMPACT 4-4-2', y: 260, tone: 'white'},
        {from: 3.0, to: 6.0, type: 'stamp', text: 'NO SPACE BETWEEN THE LINES', y: 260, tone: 'gold'},
      ],
    },
    // 3 · MOVEMENT (9-17 s): tracking, the 9 drops, D4 jumps, freeze on the hole, camera orbits to reveal it
    {
      name: 'movement',
      from: 9.0,
      flash: 0.3,
      remap: [[0, 3.55], [1.55, 4.35], [2.9, 5.0]],
      cam: [
        {at: 0, mode: 'tracking', focus: [{player: 'A9'}, {ball: true, w: 0.6}, {player: 'D4'}], dist: 22, elev: 22, azim: 12, fov: 34},
        {at: 2.9, mode: 'tracking', focus: [{player: 'A9'}, {player: 'D4'}, {p: HOLE, w: 0.6}], dist: 21, elev: 26, azim: 6, fov: 34},
        {at: 6.4, mode: 'overview', focus: [{player: 'D4', w: 0.8}, {p: HOLE}], dist: 33, elev: 48, azim: -24, fov: 40},
        {at: 8.0, mode: 'overview', focus: [{player: 'D4', w: 0.8}, {p: HOLE}], dist: 32, elev: 52, azim: -30, fov: 40},
      ],
      ov: [
        {from: 0.3, to: 3.2, type: 'pass', t0: 3.9, t1: 4.75, color: GOLD, draw: 1.2},
        {from: 0.2, to: 8.0, type: 'ring', player: 'A9', color: GOLD},
        {from: 1.4, to: 8.0, type: 'run', player: 'D4', t0: 3.6, t1: 5.0, color: RED, draw: 1.2},
        {from: 1.4, to: 8.0, type: 'ring', player: 'D4', color: RED},
        {from: 3.1, to: 8.0, type: 'defline', players: ['D3', 'D5', 'D4', 'D2'], color: WHITE},
        {from: 4.6, to: 8.0, type: 'zone', c: HOLE, r: [3.6, 3.4], color: GOLD},
      ],
      screen: [
        {from: 0.4, to: 2.9, type: 'pin', player: 'A9', text: 'THE 9 DROPS', tone: 'gold', dy: 150},
        {from: 3.0, to: 6.2, type: 'pin', player: 'D4', text: 'CENTRE-BACK JUMPS', tone: 'red', dy: 170},
        {from: 4.9, to: 8.0, type: 'pin', p: HOLE, z: 0.2, text: 'THE HOLE', tone: 'gold', dy: 190},
        {from: 2.9, to: 8.0, type: 'tag', text: 'PAUSE', icon: 'pause'},
      ],
      freeze: [[2.9, 8.0]],
    },
    // 4 · THIRD MAN (17-25 s): detail/reveal from the touchline side, the run starts, marker ball-watching
    {
      name: 'third-man',
      from: 17.0,
      flash: 0.3,
      remap: [[0, 3.25], [2.6, 4.55], [4.4, 4.55], [8.0, 6.35]],
      cam: [
        {at: 0, mode: 'detail', focus: [{player: 'A8'}, {player: 'D6', w: 0.8}], dist: 14, elev: 10, azim: 62, fov: 32, shake: 0.4},
        {at: 2.6, mode: 'detail', focus: [{player: 'A8'}, {player: 'D6', w: 0.8}], dist: 13, elev: 12, azim: 72, fov: 32, shake: 0.4},
        {at: 4.4, mode: 'detail', focus: [{player: 'A8'}, {player: 'D6', w: 0.8}], dist: 14, elev: 16, azim: 84, fov: 32},
        {at: 6.0, mode: 'tracking', focus: [{player: 'A8'}, {ball: true}], dist: 15, elev: 15, azim: -20, fov: 34, shake: 0.5},
        {at: 8.0, mode: 'tracking', focus: [{player: 'A8'}, {ball: true}], dist: 14, elev: 14, azim: -6, fov: 34, shake: 0.5},
      ],
      ov: [
        {from: 0.1, to: 0.6, type: 'ring', player: 'A8', color: GOLD},
        {from: 0.6, to: 8.0, type: 'ring', player: 'A8', color: GOLD},
        {from: 2.6, to: 4.6, type: 'ring', player: 'D6', color: RED},
        {from: 2.7, to: 8.0, type: 'run', player: 'A8', t0: 4.55, t1: 6.2, color: GOLD, draw: 0.9, dashed: true},
        {from: 5.0, to: 7.2, type: 'offside', at: 5.0, color: GOLD, span: [-14, 14]},
        {from: 5.2, to: 8.0, type: 'pass', t0: 5.0, t1: 6.2, color: WHITE, draw: 0.9},
      ],
      screen: [
        {from: 0.3, to: 2.6, type: 'tag', text: 'SLOW-MO', icon: 'slow'},
        {from: 0.5, to: 4.4, type: 'pin', player: 'A8', text: 'THE THIRD MAN', tone: 'gold', dy: 95, z: 1.95},
        {from: 2.8, to: 4.4, type: 'pin', player: 'D6', text: 'BALL-WATCHING', tone: 'red', dy: 90, dx: -60, size: 38},
        {from: 2.6, to: 4.4, type: 'tag', text: 'PAUSE', icon: 'pause'},
        {from: 5.3, to: 7.4, type: 'stamp', text: 'ONSIDE', y: 270, tone: 'gold', badge: '✓'},
      ],
      freeze: [[2.6, 4.4]],
    },
    // 5 · PAYOFF (25-29.8 s): replay from above with the three actions, then crane down behind the finish
    {
      name: 'payoff',
      from: 25.0,
      flash: 0.35,
      remap: [[0, 3.7], [2.3, 6.0], [5.1, 8.95]],
      cam: [
        {at: 0, mode: 'overview', focus: [{p: [9, 2]}], dist: 36, elev: 58, azim: 0, fov: 44},
        {at: 2.2, mode: 'overview', focus: [{player: 'A8', w: 1}, {p: [14, 2]}], dist: 30, elev: 44, azim: 0, fov: 42},
        {at: 3.1, mode: 'tracking', focus: [{player: 'A8'}, {ball: true}, {p: [50, 0], w: 0.5}], dist: 17, elev: 16, azim: -4, fov: 36, shake: 0.5},
        {at: 5.1, mode: 'tracking', focus: [{ball: true}, {p: [51, -1.5]}], dist: 15, elev: 11, azim: -12, fov: 34, shake: 0.4},
      ],
      ov: [
        {from: 0.15, to: 3.0, type: 'pass', t0: 3.9, t1: 4.75, color: GOLD, draw: 0.7},
        {from: 0.4, to: 3.0, type: 'run', player: 'A8', t0: 3.9, t1: 6.2, color: WHITE, draw: 1.3, dashed: true},
        {from: 1.2, to: 3.0, type: 'pass', t0: 5.0, t1: 6.2, color: GOLD, draw: 0.7},
      ],
      screen: [
        {from: 0, to: 2.4, type: 'tag', text: 'REPLAY', icon: 'replay'},
        {from: 0.2, to: 2.4, type: 'pin', player: 'A6', text: '1', tone: 'gold', dy: 110, size: 52},
        {from: 0.8, to: 2.4, type: 'pin', player: 'A9', text: '2', tone: 'gold', dy: 110, size: 52},
        {from: 1.4, to: 2.4, type: 'pin', player: 'A8', text: '3', tone: 'gold', dy: 110, size: 52},
        {from: 4.7, to: 5.1, type: 'stamp', text: 'GOAL', y: 300, tone: 'gold'},
      ],
    },
    // 6 · CONCLUSION (29.8-35 s): slow high orbit, navy veil, the line, end card
    {
      name: 'conclusion',
      from: 30.1,
      flash: 0.2,
      remap: [[0, 8.95], [1.5, 9.4]],
      cam: [
        {at: 0, mode: 'detail', focus: [{player: 'A8'}, {p: [52.5, -1], w: 0.12}], dist: 7.5, elev: 11, azim: -14, fov: 42, z: 1.4},
        {at: 4.9, mode: 'detail', focus: [{player: 'A8'}, {p: [52.5, -1], w: 0.12}], dist: 10, elev: 15, azim: -38, fov: 42, z: 1.4},
      ],
      screen: [
        {from: 0.1, type: 'scrim', opacity: 0.5},
        {from: 0.1, to: 1.9, type: 'title', lines: ['GREAT FOOTBALL', "ISN'T JUST", 'THE PASS.'], y: 520, size: 120, align: 'center'},
        {from: 2.0, to: 3.9, type: 'title', lines: ["IT'S THE RUN", 'NOBODY SEES.'], gold: [1], y: 560, size: 128, align: 'center'},
        {from: 3.9, type: 'end'},
      ],
    },
  ],
};
