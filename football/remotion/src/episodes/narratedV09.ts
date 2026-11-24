// FB-SETPIECE-001 V09 — NARRATED RELEASE CANDIDATE. Built ON the V08 edit (same play, same master camera
// language, same corner picture-in-picture); what changes:
//   * AUDIO-FIRST LOCK: one Deuce take cut into phrases (public/v09/plan.json, scripts/fb_voice_plan.py); the
//     live play clock below is built so that each key word lands on its event (MATCH TIME vs VIDEO TIME: the
//     play is never changed, only how fast the edit plays it). The PiP reads the SAME clock (same shot pt).
//   * corner phase ~0.5 play-s per video-s (V08: 0.6) = about 0.85x V08's editorial speed.
//   * FB SPACE CREATION VISUALIZER ('space' overlay): the zone's state is computed from the play every frame.
//   * closer mobile framing, smoother cut into the finish, close integrated into the end of the replay.
// SHOW THE SPACE. EXPLAIN THE TIMING. REWARD WITH THE GOAL.
import playJson from '../../../tactical-library/plays/FB-PLAY-SP001-V07-off-ball-timing.json';
import wordsJson from './v09-words.json';
import type {Episode, Shot} from '../FBTactical3D';
import type {FBPlay, V2} from '../play';
import {ev} from '../play';
import type {Word} from '../screen';
import {GOLD, WHITE} from '../brand';

const play = playJson as unknown as FBPlay;
const E = (id: string) => ev(play, id);

const KICK = E('CORNER_KICK_CONTACT');
const DECOY = E('DECOY_RUN_BEGINS');
const LATE = E('LATE_RUNNER_STARTS');
const D7_FOLLOWS = E('MARKER_FOLLOWS_DECOY');
const DECOY2 = E('SECOND_DECOY_BEGINS');
const ACCEL = E('LATE_RUNNER_ACCELERATES');
const SHIFT = E('DEFENSIVE_LINE_ADJUSTS');
const CUT = E('FINAL_PASS_CONTACT');
const STRIKE = E('SHOT_CONTACT');

/** the space the play opens: where the late runner strikes (measured: nearest outfield defender 3.0 m while D7
 *  marks A4 next to it, 4.4 m once D7 has followed the decoy; D9 closes to 3.05 m only at the strike) */
const STRIKE_AT: V2 = [43.25, -6.35];
const D5_START: V2 = [47.5, -1.2];
const SPACE = {type: 'space' as const, c: STRIKE_AT, runner: 'A6'};

// ---------- MATCH TIME vs VIDEO TIME ----------
/** monotone cubic (Fritsch-Carlson) through [video s, play s] keys: never runs backwards, flat where two keys
 *  share a play time (a pause), no visible kinks between rates */
const mono = (keys: [number, number][]) => {
  const n = keys.length;
  const x = keys.map((k) => k[0]);
  const y = keys.map((k) => k[1]);
  const d = x.slice(1).map((xi, i) => (y[i + 1] - y[i]) / (xi - x[i]));
  const m = y.map((_, i) => (i === 0 ? d[0] : i === n - 1 ? d[n - 2] : d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2));
  for (let i = 0; i < n - 1; i++) {
    if (d[i] === 0) {
      m[i] = 0;
      m[i + 1] = 0;
      continue;
    }
    const a = m[i] / d[i];
    const b = m[i + 1] / d[i];
    const s = a * a + b * b;
    if (s > 9) {
      const t = 3 / Math.sqrt(s);
      m[i] = t * a * d[i];
      m[i + 1] = t * b * d[i];
    }
  }
  return (v: number) => {
    if (v <= x[0]) return y[0];
    if (v >= x[n - 1]) return y[n - 1];
    let i = 0;
    while (i < n - 2 && v > x[i + 1]) i++;
    const h = x[i + 1] - x[i];
    const u = (v - x[i]) / h;
    const u2 = u * u;
    const u3 = u2 * u;
    return (2 * u3 - 3 * u2 + 1) * y[i] + (u3 - 2 * u2 + u) * h * m[i] + (-2 * u3 + 3 * u2) * y[i + 1] + (u3 - u2) * h * m[i + 1];
  };
};
/** LIVE clock (one function for every live shot and its PiP). Word anchors from public/v09/plan.json:
 *  'touch' 7.83 = B receives 3.70 · 'goes' 8.55 = decoy 4.05-4.21 · 'runner' 9.40 = late start 4.40 ·
 *  'NOW' 11.30 = accelerates 5.40 · 'defence' 13.03 ~ D5 shift 5.78 · pause 14.75-16.45 at 6.45 under
 *  'The SPACE is open' · 'cutback' 17.26 (contact 16.95) · 'First' 19.50 = strike 7.75 · goal 8.33 at 21.0 */
export const LIVE_KEYS: [number, number][] = [
  [0, 0.9], [6.4, 2.95], [7.9, 3.7], [8.6, 4.08], [9.3, 4.42], [11.3, 5.4], [12.45, 5.78], [14.6, 6.43], [14.75, 6.45],
  [16.45, 6.45], [16.95, 6.5], [19.0, 7.6], [19.5, 7.75], [20.2, 7.92], [21.0, 8.33], [21.9, 8.75],
];
const LIVE = mono(LIVE_KEYS);
/** REPLAY clock: 'leaves' 23.47 · 'opens' 24.92 · 'arrives' 26.43 (A6 in the zone 7.58) */
export const REPLAY_KEYS: [number, number][] = [[21.9, 4.0], [23.4, 4.55], [24.4, 5.15], [25.3, 5.5], [26.7, 7.4], [27.4, 7.75], [29.0, 8.33], [30.2, 8.8]];
const REPLAY = mono(REPLAY_KEYS);
/** dense remap for a shot [from, to) sampled from a clock every 1/30 s */
const remapOf = (clock: (v: number) => number, from: number, to: number): [number, number][] => {
  const out: [number, number][] = [];
  for (let v = from; v < to + 1e-6; v += 1 / 30) out.push([+(v - from).toFixed(4), +clock(v).toFixed(4)]);
  return out;
};

// ---------- narration (video-timed words from the single take) ----------
const words = (wordsJson as Word[]).map((w) => ({...w, text: w.text.replace(/\.\.\.$/, '…')}));
export const SCRIPT_V09 = words;

const MASTER = {mode: 'overview' as const, azim: 0, fov: 40, lift: 0};
const STEPS_Y = 222;
const STEPS_X = 178;
const STEPS: [string, number][] = [['CORNER', KICK], ['DECOY', DECOY], ['REACTION', D7_FOLLOWS], ['LATE RUN', ACCEL], ['FINISH', STRIKE]];

// shot boundaries (video s)
const S_CORNER = 6.4;
const S_SPACE = 12.0;
const S_DELIV = 16.95;
const S_GOAL = 19.0;
const S_PAY = 21.0;
const S_REP = 21.9;
const S_CLOSE = 26.9;
const END = 30.2;

const shots: Shot[] = [
  // 01 HOOK + SETUP (0-6.4): the organised box with the goal, then the two protagonists named by the voice
  {
    name: 'hook-setup',
    kind: 'live',
    from: 0,
    remap: remapOf(LIVE, 0, S_CORNER),
    cam: [
      // keys fitted with qa/fit_cam.mjs: closest camera that keeps the decoy, the runner, their markers and the
      // space above the subtitle band (y 1310) for the whole window
      {at: 0, ...MASTER, focus: [{p: [39.0, -3.4]}], dist: 46, elev: 68, spline: true},
      {at: 3.4, ...MASTER, focus: [{p: [38.2, -3.6]}], dist: 40, elev: 64},
      {at: 6.4, ...MASTER, focus: [{p: [37.5, -3.3]}], dist: 39.5, elev: 61},
    ],
    ov: [
      {from: 2.6, to: S_CORNER, type: 'ring', player: 'A4', color: WHITE},
      {from: 3.8, to: S_CORNER, type: 'ring', player: 'A6', color: GOLD},
    ],
    focus: [{from: 3.4, to: S_CORNER, keep: ['A4', 'A6', 'A7', 'A10', 'D7', 'D9'], k: 0.6}],
    screen: [
      {from: 0.1, to: 2.4, type: 'title', lines: ['THE GOAL STARTS', 'OFF THE BALL.'], gold: [1], y: 330, size: 88},
      {from: 3.95, to: 6.35, type: 'chip', player: 'A4', text: 'THE DECOY', tone: 'white', dy: 110, dx: 70},
      {from: 5.15, to: 6.35, type: 'chip', player: 'A6', text: 'THE RUNNER', tone: 'gold', dy: -105, dx: 40},
    ],
  },
  // 02 CORNER (6.4-12.0, play 2.95-5.62): the corner in the inset, the box in the main picture. One action at a
  // time: CORNER -> DECOY -> DEFENSIVE REACTION -> LATE RUN. The space is shown as COVERED (D7 next to it).
  {
    name: 'corner',
    kind: 'live',
    from: S_CORNER,
    remap: remapOf(LIVE, S_CORNER, S_SPACE),
    cam: [
      {at: 0, ...MASTER, focus: [{p: [37.5, -3.3]}], dist: 39.5, elev: 61, spline: true},
      {at: 5.6, ...MASTER, focus: [{p: [37.5, -3.1]}], dist: 39.5, elev: 61},
    ],
    pip: [
      {
        from: 0.0,
        to: 4.15, // kick (6.5) -> first touch -> return -> A7 receives the return (4.95 = 10.45): then it has nothing new to say
        x: 650, // right-hand grass below the near-post area: clear of the runner (left), the decoy and the space
        y: 960,
        w: 290,
        h: 320,
        label: 'CORNER',
        style: 'min',
        cam: [
          {at: 0, mode: 'tracking', focus: [{player: 'A7'}, {player: 'A10'}, {player: 'D4', w: 0.8}], dist: 10.8, elev: 44, azim: -40, fov: 38, lift: 1.4, spline: true},
          {at: 2.0, mode: 'tracking', focus: [{player: 'A10'}, {player: 'D4'}, {player: 'A7', w: 0.9}], dist: 10.2, elev: 44, azim: -36, fov: 38, lift: 1.4},
          {at: 4.15, mode: 'tracking', focus: [{player: 'A7'}, {ball: true, w: 0.6}], dist: 10.6, elev: 46, azim: -30, fov: 38, lift: 1.6},
        ],
      },
    ],
    focus: [{from: 0.5, to: 5.6, keep: ['A4', 'D7', 'A6', 'A7', 'A9', 'D8', 'D9'], k: 0.5}],
    ov: [
      {from: 0.0, to: 2.3, type: 'link', a: 'D7', b: 'A4', color: WHITE},
      {from: 1.1, to: 2.3, type: 'halo', player: 'A4'},
      {from: 2.15, type: 'run', player: 'A4', t0: DECOY, t1: 6.6, role: 'decoy', trail: true, contOut: true},
      {from: 1.6, type: 'space' as const, c: STRIKE_AT, runner: 'A6', contOut: true},
      {from: 3.05, type: 'run', player: 'D7', t0: D7_FOLLOWS - 0.05, t1: 6.6, role: 'defence', trail: true, contOut: true},
      {from: 2.55, to: 3.3, type: 'halo', player: 'A6'},
      {from: 2.9, type: 'run', player: 'A6', t0: LATE, t1: STRIKE, role: 'decisive', trail: true, contOut: true},
      {from: 3.75, type: 'run', player: 'A9', t0: DECOY2, t1: 7.2, role: 'support', trail: true, contOut: true},
    ],
    screen: [
      {from: 0.1, type: 'steps', steps: STEPS, y: STEPS_Y, x: STEPS_X, fout: 0},
      {from: 1.35, to: 2.6, type: 'cue', player: 'A4', kicker: 'TRIGGER', text: 'FIRST TOUCH', dy: 125, dx: 90},
      {from: 3.05, to: 4.3, type: 'chip', player: 'D7', text: 'MARKER FOLLOWS', tone: 'red', dy: -105, dx: 70},
      {from: 3.1, to: 4.85, type: 'cue', player: 'A6', kicker: 'LATE RUNNER', text: 'WAIT', dy: 125, dx: 120},
      {from: 4.88, to: 5.6, type: 'cue', player: 'A6', text: 'NOW', now: true, dy: 125, dx: 110},
    ],
  },
  // 03 SPACE CREATION (12.0-16.95, play 5.62-6.50): two runs drag the defence to the near post; D7 has left the
  // spot; a 1.7 s pause at 6.45 while the voice says the space is open; play resumes into the cutback
  {
    name: 'space',
    kind: 'live',
    from: S_SPACE,
    remap: remapOf(LIVE, S_SPACE, S_DELIV),
    freeze: [[14.75 - S_SPACE, 16.45 - S_SPACE]],
    cam: [
      {at: 0, ...MASTER, focus: [{p: [37.5, -3.1]}], dist: 39.5, elev: 61, spline: true},
      {at: 2.7, ...MASTER, focus: [{p: [38.9, -4.4]}], dist: 34.5, elev: 60},
      {at: 4.95, ...MASTER, focus: [{p: [41.0, -4.2]}], dist: 29, elev: 60},
    ],
    focus: [
      {from: 0, to: 2.6, keep: ['A4', 'D7', 'A6', 'A7', 'A9', 'D8', 'D5', 'D9'], k: 0.5},
      {from: 2.6, to: 4.6, keep: ['D7', 'A4', 'A6', 'A7', 'D9', 'D5'], k: 0.72},
    ],
    ov: [
      {from: 0, type: 'run', player: 'A4', t0: DECOY, t1: 6.6, role: 'decoy', trail: true, contIn: true},
      {from: 0, type: 'run', player: 'D7', t0: D7_FOLLOWS - 0.05, t1: 6.6, role: 'defence', trail: true, contIn: true},
      {from: 0, type: 'run', player: 'A9', t0: DECOY2, t1: 7.2, role: 'support', trail: true, contIn: true},
      {from: 0, type: 'run', player: 'A6', t0: LATE, t1: STRIKE, role: 'decisive', trail: true, contIn: true, contOut: true},
      {from: 0, ...SPACE, contIn: true, contOut: true},
      {from: 0.35, to: 4.6, type: 'circle', c: D5_START, r: 0.55, color: WHITE, dashed: true, width: 0.04},
      {from: 0.35, to: 4.6, type: 'run', player: 'D5', t0: SHIFT - 0.2, t1: 6.5, role: 'defence', trail: true},
      {from: 2.85, to: 4.4, type: 'cone', player: 'D9', dir: 'heading', len: 3.2, half: 0.4, color: WHITE, opacity: 0.12},
    ],
    screen: [
      {from: 0, to: 2.7, type: 'steps', steps: STEPS, y: STEPS_Y, x: STEPS_X, fin: 0},
      {from: 4.5, type: 'steps', steps: STEPS, y: STEPS_Y, x: STEPS_X, fout: 0},
      {from: 2.75, to: 4.45, type: 'tag', text: 'PAUSE', icon: 'pause'},
      {from: 2.85, to: 4.4, type: 'chip', player: 'D7', text: 'MARKER PULLED AWAY', tone: 'red', dy: -105, dx: 40},
      {from: 2.95, to: 4.4, type: 'chip', p: STRIKE_AT, z: 0.1, text: 'SPACE', tone: 'gold', dy: -95, dx: -40},
    ],
  },
  // 04 DELIVERY (16.95-19.0, play 6.50-7.60): the cutback travels to where the runner will be; the camera comes
  // down towards the shooter's side so the cut into the finish keeps the attacking direction
  {
    name: 'delivery',
    kind: 'live',
    from: S_DELIV,
    remap: remapOf(LIVE, S_DELIV, S_GOAL),
    cam: [
      {at: 0, ...MASTER, focus: [{p: [41.0, -4.2]}], dist: 29, elev: 60, spline: true},
      {at: 1.1, mode: 'overview', focus: [{p: [41.7, -4.8]}], dist: 21, elev: 46, azim: 16, fov: 40},
      {at: 2.05, mode: 'tracking', focus: [{player: 'A6', w: 1.0}, {ball: true, w: 0.6}, {p: [48.0, -3.0], w: 0.8}], dist: 17, elev: 24, azim: 32, fov: 42, lift: 0.4},
    ],
    ov: [
      {from: 0, type: 'run', player: 'A6', t0: LATE, t1: STRIKE, role: 'decisive', trail: true, contIn: true},
      {from: 0, to: 1.0, type: 'run', player: 'A4', t0: DECOY, t1: 6.6, role: 'decoy', trail: true, contIn: true},
      {from: 0, ...SPACE, noRef: true, contIn: true},
      {from: 0.05, type: 'pass', t0: CUT, t1: STRIKE, color: GOLD, trail: true, width: 0.055},
    ],
    focus: [{from: 0, to: 2.05, keep: ['A6', 'A7', 'D9', 'D5', 'D1'], k: 0.35}],
    screen: [{from: 0, to: 1.8, type: 'steps', steps: STEPS, y: STEPS_Y, x: STEPS_X, fin: 0}],
  },
  // 05 THE GOAL (19.0-21.0, play 7.60-8.33): camera C behind the shooter's side, same attacking direction;
  // slower around the contact (editorial only), the keeper's dive and the ball into the far corner
  {
    name: 'goal',
    kind: 'live',
    from: S_GOAL,
    remap: remapOf(LIVE, S_GOAL, S_PAY),
    cam: [
      {at: 0, mode: 'detail', focus: [{p: [45.6, -4.6]}, {player: 'A6', w: 0.6}], dist: 13.5, elev: 13, azim: 36, fov: 46, z: 1.0, spline: true},
      {at: 0.9, mode: 'detail', focus: [{p: [47.6, -2.2]}], dist: 12.0, elev: 10, azim: 40, fov: 46, z: 1.0},
      {at: 2.0, mode: 'detail', focus: [{p: [50.4, 0.6]}], dist: 10.8, elev: 9, azim: 44, fov: 44, z: 1.0},
    ],
  },
  // 06 PAYOFF (21.0-21.9): the net side, one gold breath
  {
    name: 'payoff',
    kind: 'live',
    from: S_PAY,
    remap: remapOf(LIVE, S_PAY, S_REP),
    cam: [
      {at: 0, mode: 'detail', focus: [{p: [50.0, -2.0]}], dist: 13, elev: 12, azim: 214, fov: 46, z: 1.0},
      {at: 0.9, mode: 'detail', focus: [{p: [49.2, -3.4]}], dist: 14, elev: 14, azim: 208, fov: 46, z: 1.0},
    ],
    screen: [{from: 0, to: 0.9, type: 'accent'}],
  },
  // 07 TACTICAL REPLAY (21.9-27.1, play 4.0-7.6): only the mechanism — the marker leaves with the decoy, the
  // space lights up when (and only while) it is really open, the runner's line, the arrival
  {
    name: 'replay',
    kind: 'replay',
    from: S_REP,
    remap: remapOf(REPLAY, S_REP, S_CLOSE),
    cam: [
      {at: 0, ...MASTER, focus: [{p: [37.9, -3.5]}], dist: 40.5, elev: 64, spline: true},
      {at: 5.0, ...MASTER, focus: [{p: [39.2, -4.1]}], dist: 36, elev: 63},
    ],
    focus: [{from: 0.1, to: 5.0, keep: ['A4', 'D7', 'A6', 'A7', 'D9'], k: 0.55}],
    ov: [
      {from: 0, to: 1.6, type: 'halo', player: 'A4'},
      {from: 0, to: 2.4, type: 'link', a: 'D7', b: 'A4', color: WHITE, width: 0.035},
      {from: 0.4, type: 'run', player: 'A4', t0: DECOY, t1: 6.6, role: 'decoy', trail: true},
      {from: 0.9, type: 'ghost', player: 'D7', times: [D7_FOLLOWS], color: WHITE, opacity: 0.5, ringsOnly: true},
      {from: 0.9, type: 'run', player: 'D7', t0: D7_FOLLOWS - 0.05, t1: 6.6, role: 'defence', trail: true},
      {from: 0, ...SPACE, contOut: true},
      {from: 2.4, type: 'run', player: 'A6', t0: LATE, t1: STRIKE, role: 'decisive', trail: true, contOut: true},
      {from: 4.2, type: 'pass', t0: CUT, t1: STRIKE, color: GOLD, trail: true, width: 0.05, contOut: true},
    ],
    screen: [{from: 0, to: 5.0, type: 'tag', text: 'REPLAY', icon: 'replay'}],
  },
  // 08 CLOSE (27.1-30.2): the replay runs on into the finish while the lesson appears with the voice
  {
    name: 'close',
    kind: 'replay',
    from: S_CLOSE,
    remap: remapOf(REPLAY, S_CLOSE, END),
    cam: [
      {at: 0, ...MASTER, focus: [{p: [39.2, -4.1]}], dist: 36, elev: 63, spline: true},
      {at: 3.3, ...MASTER, focus: [{p: [43.1, -3.1]}], dist: 25.5, elev: 62},
    ],
    ov: [
      {from: 0, type: 'run', player: 'A6', t0: LATE, t1: STRIKE, role: 'decisive', trail: true, contIn: true},
      {from: 0, to: 1.4, type: 'pass', t0: CUT, t1: STRIKE, color: GOLD, trail: true, width: 0.05, contIn: true},
      // echo of the space it attacked (same place, same size it had when open), only under CREATE THE SPACE
      {from: 0.6, to: 1.6, type: 'zone', c: STRIKE_AT, r: [1.6, 1.6], color: GOLD},
    ],
    screen: [
      // titles sit in the empty grass under the box (y 1060-1240): the shot, the keeper and the net stay clear
      {from: 0.7, type: 'title', lines: ['CREATE THE SPACE.'], y: 1060, size: 74},
      {from: 1.5, type: 'title', lines: ['TIME THE RUN.'], gold: [0], y: 1150, size: 74},
      {from: 2.3, type: 'sig'},
    ],
  },
];

export const narratedV09: Episode = {
  id: 'FB-SETPIECE-001',
  title: 'Short corner: near-post decoy + late arrival (narrated release candidate)',
  duration: END,
  play,
  words,
  keywords: ['movement', 'defender', 'defence', 'space', 'now', 'timed', 'time'],
  look: 'day',
  grade: 'clean',
  graphicsV2: true,
  subtitles: true,
  subtitleStyle: 'keys',
  subtitleSize: 50,
  subtitleY: 1340,
  subtitleHide: [[0, 2.45], [27.4, END]],
  music: {src: 'v09/mix.wav', volume: 1},
  shots,
};
/** silent picture (QC stills / fragments, same edit) */
export const narratedV09Silent: Episode = {...narratedV09, music: undefined};

/** corner-speed test (directive 3): the V08 corner phase (play 2.95 -> 5.62, box + inset) at V08's editorial
 *  rate (0.60 play s per video s) times k; silent, no graphics change */
export const cornerRateTest = (k: number): Episode => {
  const r = 0.6 * k;
  const d = (5.62 - 2.95) / r;
  const c = shots[1];
  return {
    ...narratedV09Silent,
    subtitles: false,
    duration: +d.toFixed(2),
    shots: [{...c, from: 0, remap: [[0, 2.95], [d, 5.62]], ov: [], screen: [{from: 0.1, type: 'tag', text: `${k.toFixed(2)}x`, icon: 'slow'}], pip: c.pip!.map((p) => ({...p, to: d}))}],
  };
};
