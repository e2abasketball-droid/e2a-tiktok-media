// FB-SETPIECE-001 V07 — "Short corner: near-post decoy + late arrival" · OFF-BALL TIMING edit.
// THE BALL IS VISIBLE. THE MOVEMENT IS THE STORY.
// Play: football/tactical-library/plays/FB-PLAY-SP001-V07-off-ball-timing.json (V05 play + pre-run behaviour +
// MASTER MATCH TIMELINE). Every play time below is read from the timeline by name (ev(play, 'NAME')), so the
// runs, the defensive reactions, the cues, the camera and the graphics share ONE clock. 'live' shots continue
// that clock across cuts (qa/qc_edit.mjs checks it); only the REVEAL rewinds.
import playJson from '../../../tactical-library/plays/FB-PLAY-SP001-V07-off-ball-timing.json';
import type {Episode, Shot} from '../FBTactical3D';
import type {FBPlay, V2} from '../play';
import {ev} from '../play';
import type {Word} from '../screen';
import {GOLD, WHITE} from '../brand';

const play = playJson as unknown as FBPlay;
const E = (id: string) => ev(play, id);

const KICK = E('CORNER_KICK_CONTACT');
const B_RECV = E('PLAYER_B_RECEIVES');
const DECOY = E('DECOY_RUN_BEGINS');
const RET = E('RETURN_PASS_CONTACT');
const LATE = E('LATE_RUNNER_STARTS');
const DECOY2 = E('SECOND_DECOY_BEGINS');
const A7_RECV = E('TAKER_RECEIVES_RETURN');
const ACCEL = E('LATE_RUNNER_ACCELERATES');
const SHIFT = E('DEFENSIVE_LINE_ADJUSTS');
const CUT = E('FINAL_PASS_CONTACT');
const STRIKE = E('SHOT_CONTACT');
const GOAL = E('BALL_CROSSES_GOAL_LINE');

const STRIKE_AT: V2 = [43.25, -6.35];
const TARGET: V2 = [52.6, 3.15];
const D5_START: V2 = [47.5, -1.2];

/** narration for Deuce (English) timed to this cut — NOT recorded (no ElevenLabs credits); also the subtitle /
 *  music markers for a future voiced version */
export const SCRIPT_V07: [number, number, string][] = [
  [0.2, 2.0, 'The goal starts off the ball.'],
  [2.3, 4.0, 'One decoy. One runner.'],
  [4.4, 6.2, 'Short corner. On the first touch, the decoy goes.'],
  [6.4, 7.9, 'On the return, the runner leaves his spot...'],
  [8.0, 9.1, '...waits... now.'],
  [9.3, 11.0, 'Two runs pull the line to the near post.'],
  [11.3, 13.2, 'The cutback arrives with the runner.'],
  [13.5, 15.4, 'First time. Far corner.'],
  [17.0, 18.6, 'Watch the timing again.'],
  [18.8, 21.0, 'The decoy goes. The line shifts. The runner arrives.'],
  [21.5, 23.3, 'Create the space. Time the run.'],
];
const words: Word[] = [];

// CAMERA A — master tactical view: the box, the decoys, their markers, the late runner and the finishing zone.
// It does NOT leave the box when the ball is touched at the corner (the corner is in the picture-in-picture).
const MASTER = {mode: 'overview' as const, azim: 0, fov: 40, lift: 0};
const STEPS_Y = 222;
const STEPS_X = 178;
const STEPS: [string, number][] = [['CORNER', KICK], ['DECOY', DECOY], ['LATE RUN', LATE], ['DELIVERY', CUT], ['FINISH', STRIKE]];

// live play clock (video s -> play s); one continuous function across the live shots
const L1 = 0.9; // hook starts just before the taker's approach
const L3 = 2.9; // simultaneous action starts just before the kick
const L4 = 5.9;
const L5 = 6.5;
const L6 = 7.6;
const L7 = 8.65;
const L9 = 9.35;

const shots: Shot[] = [
  // 01 HOOK + 02 SETUP (0-4.2): the organised box, the zone of the decisive run lit for a moment, then only
  // the two protagonists labelled; everybody else muted
  {
    name: 'hook-setup',
    kind: 'live',
    from: 0,
    remap: [[0, L1], [4.2, L3]],
    cam: [
      {at: 0, ...MASTER, focus: [{p: [43.0, -2.0]}], dist: 50, elev: 76, spline: true},
      {at: 2.2, ...MASTER, focus: [{p: [44.8, -6.4]}, {player: 'A6', w: 0.75}], dist: 43.1, elev: 72},
      {at: 4.2, ...MASTER, focus: [{p: [44.8, -6.8]}, {player: 'A6', w: 0.75}], dist: 42.0, elev: 72},
    ],
    ov: [
      {from: 0.35, to: 2.1, type: 'zone', c: STRIKE_AT, r: [2.4, 2.4], color: GOLD},
      {from: 2.3, to: 4.2, type: 'ring', player: 'A4', color: WHITE},
      {from: 2.45, to: 4.2, type: 'ring', player: 'A6', color: GOLD},
    ],
    focus: [{from: 2.2, to: 4.2, keep: ['A4', 'A6', 'A7'], k: 0.7}],
    screen: [
      {from: 0.08, to: 2.15, type: 'title', lines: ['THE GOAL STARTS', 'OFF THE BALL.'], gold: [1], y: 330, size: 92},
      {from: 2.35, to: 4.15, type: 'chip', player: 'A4', text: 'THE DECOY', tone: 'white', dy: 120, dx: 70},
      {from: 2.5, to: 4.15, type: 'chip', player: 'A6', text: 'THE RUNNER', tone: 'gold', dy: -110, dx: 40},
    ],
  },
  // 03 SIMULTANEOUS ACTION (4.2-9.2): the corner is played in the inset while the main picture holds the box:
  // the decoy goes on B's first touch, the runner leaves on the return, waits, then goes
  {
    name: 'simultaneous',
    kind: 'live',
    from: 4.2,
    remap: [[0, L3], [5.0, L4]],
    cam: [
      {at: 0, ...MASTER, focus: [{p: [44.8, -6.8]}, {player: 'A6', w: 0.75}], dist: 42.0, elev: 72, spline: true},
      {at: 2.6, ...MASTER, focus: [{p: [45.2, -7.0]}, {player: 'A6', w: 0.75}], dist: 41.0, elev: 71},
      {at: 5.0, ...MASTER, focus: [{p: [45.8, -7.4]}, {player: 'A6', w: 0.75}], dist: 37.8, elev: 69},
    ],
    pip: [
      {
        from: 0.15,
        to: 4.0,
        x: 64,
        y: 850,
        w: 320,
        h: 380,
        label: 'CORNER',
        cam: [
          {at: 0, mode: 'tracking', focus: [{player: 'A7'}, {player: 'A10'}, {player: 'D4', w: 0.8}], dist: 17, elev: 38, azim: -40, fov: 38, lift: 1.6, spline: true},
          {at: 2.0, mode: 'tracking', focus: [{player: 'A10'}, {player: 'D4'}, {player: 'A7', w: 0.9}], dist: 16, elev: 38, azim: -36, fov: 38, lift: 1.6},
          {at: 3.85, mode: 'tracking', focus: [{player: 'A7'}, {ball: true, w: 0.6}], dist: 17, elev: 40, azim: -30, fov: 38, lift: 1.8},
        ],
      },
    ],
    focus: [{from: 1.0, to: 5.0, keep: ['A4', 'D7', 'A6', 'A7', 'A9', 'D8'], k: 0.55}],
    ov: [
      {from: 0.3, to: 3.4, type: 'link', a: 'D7', b: 'A4', color: WHITE},
      {from: 1.0, to: 2.4, type: 'halo', player: 'A4'},
      {from: 1.95, type: 'run', player: 'A4', t0: DECOY, t1: 6.6, role: 'decoy', trail: true},
      {from: 2.05, to: 2.75, type: 'halo', player: 'A6'},
      {from: 2.6, type: 'run', player: 'A6', t0: LATE, t1: STRIKE, role: 'decisive', trail: true},
      {from: 3.3, type: 'run', player: 'A9', t0: DECOY2, t1: 7.2, role: 'support', trail: true},
      {from: 3.4, type: 'run', player: 'D7', t0: DECOY, t1: 6.6, role: 'defence', trail: true},
    ],
    screen: [
      {from: 0.4, type: 'steps', steps: STEPS, y: STEPS_Y, x: STEPS_X},
      {from: 1.35, to: 2.85, type: 'cue', player: 'A4', kicker: 'TRIGGER', text: 'ON THE FIRST TOUCH', dy: 130, dx: 90},
      {from: 2.4, to: 3.55, type: 'cue', player: 'A6', kicker: 'LATE RUNNER', text: 'ON THE RETURN', dy: -120, dx: 60},
      {from: 3.6, to: 4.15, type: 'cue', player: 'A6', kicker: 'LATE RUNNER', text: 'WAIT', dy: -120, dx: 60},
      {from: (ACCEL - L3) / 0.6, to: 5.0, type: 'cue', player: 'A6', text: 'NOW', now: true, dy: -125, dx: 60},
    ],
  },
  // 04 TACTICAL TRIGGER (9.2-11.2): a short freeze at the moment the shifted line opens the space; only the
  // central zonal defender and the runner stay lit; the play resumes from the same instant
  {
    name: 'trigger',
    kind: 'live',
    from: 9.2,
    remap: [[0, L4], [0.45, 6.15], [1.25, 6.15], [2.0, L5]],
    freeze: [[0.45, 1.25]],
    cam: [
      {at: 0, ...MASTER, focus: [{p: [45.8, -7.4]}, {player: 'A6', w: 0.75}], dist: 37.8, elev: 69, spline: true},
      {at: 1.0, ...MASTER, focus: [{p: [46.2, -7.6]}, {player: 'A6', w: 0.75}], dist: 35.7, elev: 69},
      {at: 2.0, ...MASTER, focus: [{p: [46.6, -7.8]}, {player: 'A6', w: 0.75}], dist: 33.6, elev: 66},
    ],
    focus: [{from: 0.35, to: 1.4, keep: ['D5', 'A6', 'A7'], k: 0.75}],
    ov: [
      {from: 0, type: 'run', player: 'A4', t0: DECOY, t1: 6.6, role: 'decoy', trail: true},
      {from: 0, type: 'run', player: 'A9', t0: DECOY2, t1: 7.2, role: 'support', trail: true},
      {from: 0, type: 'run', player: 'A6', t0: LATE, t1: STRIKE, role: 'decisive', trail: true},
      {from: 0.3, to: 1.6, type: 'circle', c: D5_START, r: 0.6, color: WHITE, dashed: true, width: 0.045},
      {from: 0.3, to: 1.6, type: 'run', player: 'D5', t0: SHIFT - 0.2, t1: 7.3, role: 'defence', trail: true},
      {from: 0.5, to: 1.3, type: 'cone', player: 'D9', dir: 'heading', len: 4, half: 0.45, color: WHITE, opacity: 0.2},
      {from: 0.65, to: 1.3, type: 'zone', c: STRIKE_AT, r: [1.6, 1.6], color: GOLD},
    ],
    screen: [
      {from: 0, to: 0.4, type: 'steps', steps: STEPS, y: STEPS_Y, x: STEPS_X},
      {from: 1.3, type: 'steps', steps: STEPS, y: STEPS_Y, x: STEPS_X},
      {from: 0.45, to: 1.25, type: 'tag', text: 'PAUSE', icon: 'pause'},
      {from: 0.5, to: 1.3, type: 'chip', player: 'D5', text: 'LINE SHIFTS', tone: 'red', dy: -110, dx: 90},
      {from: 0.65, to: 1.3, type: 'chip', p: STRIKE_AT, z: 0.1, text: 'THE SPACE', tone: 'gold', dy: -90, dx: -60},
    ],
  },
  // 05 FINAL DELIVERY (11.2-13.4): the cutback is timed to the runner's arrival, not to where he is
  {
    name: 'delivery',
    kind: 'live',
    from: 11.2,
    remap: [[0, L5], [2.2, L6]],
    cam: [
      {at: 0, ...MASTER, focus: [{p: [46.6, -7.8]}, {player: 'A6', w: 0.75}], dist: 33.6, elev: 66, spline: true},
      {at: 1.2, mode: 'overview', focus: [{player: 'A6', w: 0.8}, {p: [48.5, -6.0], w: 1.2}], dist: 27, elev: 50, azim: 12, fov: 40, lift: 0.4},
      {at: 2.2, mode: 'tracking', focus: [{player: 'A6', w: 0.9}, {player: 'D9', w: 0.4}, {p: [50.0, -3.0], w: 1.1}], dist: 26, elev: 44, azim: 22, fov: 40, lift: 0.4},
    ],
    ov: [
      {from: 0, type: 'run', player: 'A6', t0: LATE, t1: STRIKE, role: 'decisive', trail: true},
      {from: 0, to: 1.0, type: 'run', player: 'A4', t0: DECOY, t1: 6.6, role: 'decoy', trail: true},
      {from: 0.05, type: 'pass', t0: CUT, t1: STRIKE, color: GOLD, trail: true, width: 0.06},
      {from: 1.5, type: 'cone', player: 'A6', dir: TARGET, len: 9.6, half: 0.07, color: GOLD, opacity: 0.26},
    ],
    focus: [{from: 0, to: 2.2, keep: ['A6', 'A7', 'D9', 'D5', 'D1'], k: 0.4}],
    screen: [
      {from: 0, to: 2.1, type: 'steps', steps: STEPS, y: STEPS_Y, x: STEPS_X},
      {from: 0.5, to: 2.0, type: 'cue', player: 'A6', kicker: 'ARRIVES WITH', text: 'THE BALL', dy: -120, dx: -30},
    ],
  },
  // 06 THE GOAL (13.4-15.8): CAMERA C behind the shooter — contact, keeper, ball in; micro slow motion around
  // the contact is editorial only (the play physics are unchanged)
  {
    name: 'goal',
    kind: 'live',
    from: 13.4,
    remap: [[0, L6], [0.4, 7.7], [1.2, 7.84], [2.4, L7]],
    cam: [
      {at: 0, mode: 'detail', focus: [{p: [46.8, -3.4]}], dist: 12.5, elev: 9, azim: 38, fov: 48, z: 1.0, spline: true},
      {at: 1.2, mode: 'detail', focus: [{p: [48.3, -1.6]}], dist: 11.5, elev: 8, azim: 40, fov: 46, z: 1.0},
      {at: 2.4, mode: 'detail', focus: [{p: [50.4, 0.6]}], dist: 10.5, elev: 8, azim: 44, fov: 44, z: 1.0},
    ],
  },
  // 07 CINEMATIC PAYOFF (15.8-16.9): reverse from the goal side — the net, the scorer, a single gold breath
  {
    name: 'payoff',
    kind: 'live',
    from: 15.8,
    remap: [[0, L7], [1.1, L9]],
    cam: [
      {at: 0, mode: 'detail', focus: [{p: [50.0, -2.0]}], dist: 13, elev: 12, azim: 214, fov: 46, z: 1.0},
      {at: 1.1, mode: 'detail', focus: [{p: [49.0, -3.6]}], dist: 14.5, elev: 14, azim: 206, fov: 46, z: 1.0},
    ],
    screen: [{from: 0, to: 1.1, type: 'accent'}],
  },
  // 08 REVEAL (16.9-21.3): selective replay from above with ghosts at the REAL positions of each key moment:
  // the decoy's start, the defensive reaction, the runner's timing, the connection, the advantage
  {
    name: 'reveal',
    kind: 'replay',
    from: 16.9,
    remap: [[0, 3.95], [4.4, 7.85]],
    cam: [
      {at: 0, ...MASTER, focus: [{p: [45.2, -7.0]}, {player: 'A6', w: 0.75}], dist: 41.0, elev: 74, spline: true},
      {at: 2.2, ...MASTER, focus: [{p: [45.8, -7.4]}, {player: 'A6', w: 0.75}], dist: 37.8, elev: 73},
      {at: 4.4, ...MASTER, focus: [{p: [46.4, -7.8]}, {player: 'A6', w: 0.75}], dist: 34.6, elev: 71},
    ],
    focus: [{from: 0.2, to: 4.4, keep: ['A4', 'D7', 'D5', 'A6', 'A7', 'D9'], k: 0.5}],
    ov: [
      {from: 0, type: 'ghost', player: 'A4', times: [DECOY], color: WHITE},
      {from: 0, type: 'run', player: 'A4', t0: DECOY, t1: 6.6, role: 'decoy', trail: true},
      {from: 0, type: 'ghost', player: 'A6', times: [LATE, ACCEL, CUT], color: GOLD, opacity: 0.4},
      {from: 0, type: 'run', player: 'A6', t0: LATE, t1: STRIKE, role: 'decisive', trail: true},
      {from: 1.2, type: 'circle', c: D5_START, r: 0.6, color: WHITE, dashed: true, width: 0.045},
      {from: 1.2, type: 'run', player: 'D5', t0: SHIFT - 0.2, t1: 7.3, role: 'defence', trail: true},
      {from: 2.6, type: 'pass', t0: CUT, t1: STRIKE, color: GOLD, trail: true, width: 0.06},
    ],
    screen: [
      {from: 0, to: 4.4, type: 'tag', text: 'REPLAY', icon: 'replay'},
      {from: 0.15, to: 1.25, type: 'cue', player: 'A4', kicker: '1', text: 'DECOY GOES', dy: 130, dx: 90},
      {from: 1.6, to: 2.6, type: 'cue', player: 'D5', kicker: '2', text: 'LINE SHIFTS', dy: -110, dx: 100},
      {from: 2.7, to: 3.6, type: 'cue', player: 'A6', kicker: '3', text: 'RUNNER ARRIVES', dy: -120, dx: 40},
      {from: 3.75, to: 4.4, type: 'chip', player: 'A6', text: '3 M', tone: 'gold', dy: 120, dx: -40},
    ],
  },
  // 09 ENDING (21.3-24.2): the play clock continues after the goal; slow rise over the box, the lesson,
  // a discreet signature (no static outro)
  {
    name: 'ending',
    kind: 'live',
    from: 21.3,
    remap: [[0, L9], [2.9, 10.4]],
    cam: [
      {at: 0, mode: 'overview', focus: [{p: [47.0, -4.0]}], dist: 30, elev: 46, azim: 70, fov: 40, spline: true},
      {at: 1.5, mode: 'overview', focus: [{p: [46.0, -5.0]}], dist: 36, elev: 56, azim: 80, fov: 40},
      {at: 2.9, mode: 'overview', focus: [{p: [45.0, -6.0]}], dist: 42, elev: 64, azim: 88, fov: 40},
    ],
    ov: [
      {from: 0.2, type: 'run', player: 'A4', t0: DECOY, t1: 6.6, role: 'decoy', draw: 0.5},
      {from: 0.35, type: 'run', player: 'A6', t0: LATE, t1: STRIKE, role: 'decisive', draw: 0.6},
    ],
    screen: [
      {from: 0.15, to: 2.0, type: 'title', lines: ['CREATE THE SPACE.', 'TIME THE RUN.'], gold: [1], y: 330, size: 96},
      {from: 1.95, type: 'sig'},
    ],
  },
];

export const offBallTimingV07: Episode = {
  id: 'FB-SETPIECE-001',
  title: 'Short corner: near-post decoy + late arrival (off-ball timing)',
  duration: 24.2,
  play,
  words,
  keywords: [],
  look: 'day',
  grade: 'clean',
  graphicsV2: true,
  subtitles: false,
  shots,
};

export {KICK, B_RECV, RET, A7_RECV, GOAL};

/** PiP TEST (directive 5.1): the same edit with ONE wide tactical shot instead of box view + corner inset during
 *  the simultaneous action (camera from the side, corner at the bottom of the frame, box above). Used only for
 *  the comparison stills / metrics; the delivered cut is offBallTimingV07. */
export const offBallTimingV07Wide: Episode = {
  ...offBallTimingV07,
  shots: offBallTimingV07.shots.map((s) =>
    s.name === 'simultaneous'
      ? {
          ...s,
          pip: undefined,
          cam: [
            {at: 0, mode: 'overview', focus: [{p: [44.5, -15.0]}], dist: 56, elev: 62, azim: 90, fov: 38, spline: true},
            {at: 2.6, mode: 'overview', focus: [{p: [44.5, -14.0]}], dist: 54, elev: 62, azim: 90, fov: 38},
            {at: 5.0, mode: 'overview', focus: [{p: [44.5, -12.0]}], dist: 50, elev: 62, azim: 90, fov: 38},
          ],
        }
      : s,
  ),
};

/** V08 (after the V07 review in motion): the trigger-steps bar no longer blinks at the two cuts where the master
 *  camera simply continues (9.2 s and 11.2 s), and the corner inset camera is closer so the short corner, the
 *  press and the return read at phone size. Play, timing, graphics and edit otherwise identical to V07. */
const stepsCont = (s: Shot, fin: boolean, fout: boolean): Shot => ({
  ...s,
  // the run lines that carry over a continuous cut (same master camera) do not fade out / in at the cut
  ov: s.ov?.map((o) => (o.type === 'run' ? {...o, ...(fin && o.from === 0 ? {contIn: true} : {}), ...(fout && o.to === undefined ? {contOut: true} : {})} : o)),
  screen: s.screen?.map((x) => (x.type === 'steps' ? {...x, ...(fin && x.from === 0 ? {fin: 0} : {}), ...(fout && x.to === undefined ? {fout: 0} : {})} : x)),
});
export const offBallTimingV08: Episode = {
  ...offBallTimingV07,
  shots: offBallTimingV07.shots.map((s) => {
    if (s.name === 'simultaneous')
      return {
        ...stepsCont(s, false, true),
        pip: s.pip!.map((p) => ({...p, cam: p.cam.map((k) => ({...k, dist: k.dist * 0.74, elev: k.elev + 4}))})),
      };
    if (s.name === 'trigger') return stepsCont(s, true, true);
    if (s.name === 'delivery') return stepsCont(s, true, false);
    return s;
  }),
};
