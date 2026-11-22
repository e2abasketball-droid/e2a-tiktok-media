// E2A Realism V3.2 (2026-11-22) — the SCRIPTS of the V3.2 test plays: each player's clip is built by library.ts from a
// handful of primitives with event times taken from the play (ball events, track phases) and a per-player seed. No
// per-frame or per-joint hand keys (V3.1 clips.ts keyed every channel by hand for one player of one play).
import type {Play} from '../../tactical/play.ts';
import type {Clip32, Seg} from './library.ts';
import {buildClip} from './library.ts';

const hA = -1.0184; // one-take: A -> B (the start faces the acceleration line)

/** O1 of the one-take (realism-v3-1-onetake, realism-v3-2-abc: identical O1 track and ball events) */
const onetakeO1: Seg[] = [
  {k: 'stand', t0: 0, t1: 1.5, pose: 'ready', face: hA},
  {k: 'move', t0: 1.5, t1: 3.28, mode: 'run'},
  {k: 'plant', t: 3.28, side: 1, cut: 1.4},
  {k: 'move', t0: 3.28, t1: 4.93, mode: 'run'},
  // 1-2 stop into the catch: right foot at the catch, left foot after
  {k: 'step', side: 1, lift: 4.68, land: 4.93, f: 0.16, l: 0.12, heel: -0.16, h: 0.1},
  {k: 'step', side: 0, lift: 4.9, land: 5.12, f: 0.2, l: -0.18, heel: -0.1, h: 0.08},
  {k: 'catch', t: 148 / 30, from: 'O2'},
  // front pivot on the right foot to face the rim
  {k: 'pivot', side: 1, t0: 5.3, t1: 5.84, dyaw: -1.65},
  {k: 'step', side: 0, lift: 5.32, land: 5.8, f: 0.04, l: -0.2, h: 0.07, toeOff: 0.2},
  {k: 'step', side: 1, lift: 5.84, land: 6.0, f: 0.0, l: 0.19, h: 0.05, toeOff: 0.2},
  {k: 'stand', t0: 5.84, t1: 7.4, pose: 'triple', face: 'rim'},
  // jab, one bounce on a step-back, 1-2 gather into the shot
  {k: 'step', side: 1, lift: 6.04, land: 6.16, f: 0.3, l: 0.17, heel: -0.08, h: 0.06},
  {k: 'dribble', push: 6.15, floor: 6.42, catch: 6.72},
  {k: 'step', side: 1, lift: 6.24, land: 6.52, f: -0.14, l: 0.2, h: 0.1, toeOff: 0.5},
  {k: 'step', side: 0, lift: 6.38, land: 6.68, f: -0.06, l: -0.2, h: 0.1},
  {k: 'step', side: 1, lift: 6.74, land: 6.92, f: 0.05, l: 0.17, h: 0.06},
  {k: 'step', side: 0, lift: 6.86, land: 7.04, f: -0.02, l: -0.17, h: 0.06},
  {k: 'stand', t0: 7.4, t1: 9.3, pose: 'ready', face: 'rim'},
  {k: 'jumpshot', release: 246 / 30, H: 0.5},
  {k: 'step', side: 0, lift: 9.05, land: 9.3, f: 0.0, l: -0.2, h: 0.05, toeOff: 0.2},
  {k: 'stand', t0: 9.3, t1: 10.0, pose: 'ready', face: 'rim'},
  {k: 'move', t0: 10.0, t1: 11.1, mode: 'backpedal', face: 'rim'},
  {k: 'step', side: 0, lift: 11.12, land: 11.32, f: 0.03, l: -0.22, h: 0.05, toeOff: 0.15},
  {k: 'step', side: 1, lift: 11.3, land: 11.46, f: -0.03, l: 0.22, h: 0.05, toeOff: 0.15},
  {k: 'stand', t0: 11.1, t1: 12.5, pose: 'defense', face: 'rim'},
];

/** the 3-player interaction (realism-v3-2-trio, tactical/specs/_gen-realism-v3-2-trio.py): O1 passes, O2 V-cuts,
 *  catches, brakes and shoots, X2 trails the cut and closes out. Event times come from the play file. */
const trio = (play: Play): Record<string, Seg[]> => {
  const m = (play as Play & {marks: Record<string, number>}).marks;
  return {
    O1: [
      {k: 'stand', t0: 0, t1: m.pass + 0.6, pose: 'triple', face: 'O2'},
      {k: 'pass', t: m.pass, to: 'O2'},
      {k: 'stand', t0: m.pass + 0.6, t1: play.duration, pose: 'relaxed', face: 'O2'},
    ],
    O2: [
      {k: 'stand', t0: 0, t1: m.cutGo, pose: 'ready', face: 'O1'},
      {k: 'move', t0: m.cutGo, t1: m.plant, mode: 'run'},
      {k: 'plant', t: m.plant, side: 0, cut: -1.3},
      {k: 'move', t0: m.plant, t1: m.catch, mode: 'run'},
      {k: 'step', side: 0, lift: m.catch - 0.24, land: m.catch, f: 0.16, l: -0.12, heel: -0.18, h: 0.1},
      {k: 'step', side: 1, lift: m.catch - 0.02, land: m.catch + 0.2, f: 0.2, l: 0.17, heel: -0.1, h: 0.08},
      {k: 'catch', t: m.catch, from: 'O1'},
      {k: 'stand', t0: m.catch + 0.2, t1: play.duration, pose: 'ready', face: 'rim'},
      {k: 'jumpshot', release: m.release, H: 0.46},
    ],
    X2: [
      {k: 'stand', t0: 0, t1: m.cutGo + 0.25, pose: 'defense', face: 'O2'},
      {k: 'move', t0: m.cutGo + 0.25, t1: m.closeout, mode: 'run'},
      {k: 'move', t0: m.closeout, t1: m.closeoutEnd, mode: 'shuffle', face: 'O2'},
      {k: 'stand', t0: m.closeoutEnd, t1: m.release + 0.5, pose: 'closeout', face: 'O2'},
      {k: 'stand', t0: m.release + 0.5, t1: play.duration, pose: 'defense', face: 'O2'},
    ],
  };
};

const SEEDS: Record<string, number> = {O1: 11, O2: 23, X2: 37, O3: 41, O4: 53, O5: 61, X1: 71, X3: 83, X4: 97, X5: 101};
const cache = new Map<string, Clip32 | null>();

/** the V3.2 clip of a player in a play (benchmark copies map players to a source play / player via `v32clip`) */
export const clip32For = (play: Play, id: string): Clip32 | null => {
  const key = `${play.id}|${id}`;
  const hit = cache.get(key);
  if (hit !== undefined) return hit;
  let out: Clip32 | null = null;
  const map = (play as Play & {v32clip?: Record<string, string>}).v32clip;
  const src = map?.[id];
  const pid = src ? src.split(':')[0] : play.id;
  const who = src ? src.split(':')[1] : id;
  const seed = SEEDS[id] ?? (id.charCodeAt(0) * 31 + Number(id.slice(1) || 0) * 7);
  if ((pid === 'realism-v3-1-onetake' || pid === 'realism-v3-2-abc') && who === 'O1') out = buildClip(play, id, onetakeO1, {seed, timing: 1, amp: 1}, 'V3.2 library: one-take O1');
  else if (pid === 'realism-v3-2-trio' && play.id === 'realism-v3-2-trio') {
    const sc = trio(play)[who];
    if (sc) out = buildClip(play, id, sc, {seed, timing: 1, amp: 1}, `V3.2 library: trio ${who}`);
  }
  cache.set(key, out);
  return out;
};
