// E2A Tactical engine — the EDIT is data too: shots anchored to the narration, each with a time
// remap (real speed, slow motion, freeze, rewind, speed ramps), camera keys and overlays.
import type {CamKey} from './camera.ts';
import type {Play} from './play.ts';
import {mark} from './play.ts';

export type Anchor = string | number;
/** time inside a shot: number = seconds from the shot start, string = phrase in the narration */
export type LocalT = Anchor;

/** [local time, play time or mark, ease of the segment that ENDS here] */
export type RemapKey = [LocalT, number | string, ('linear' | 'inOut' | 'out' | 'in')?];

export type Overlay = {
  type:
    | 'ring'
    | 'route'
    | 'trail'
    | 'corridor'
    | 'doors'
    | 'separation'
    | 'passLane'
    | 'openSpace'
    | 'shotWindow'
    | 'switch'
    | 'label'
    | 'contact'
    | 'title'
    | 'stamp'
    | 'freeze'
    | 'rewind'
    | 'timing'
    | 'branch'
    | 'logo'
    | 'dim'
    | 'flash'
    | 'kicker'
    | 'fork';
  from: LocalT;
  to?: LocalT;
  /** which panel in a split shot (0 left, 1 right) */
  panel?: number;
  [k: string]: unknown;
};

export type SfxCue = {at: LocalT; name: string; volume?: number};

export type Panel = {play: string; remap: RemapKey[]; camera: CamKey[]; label?: string; result?: string};

export type Shot = {
  id: string;
  /** narration anchor where the shot starts (the first shot starts at 0) */
  at: Anchor;
  offset?: number;
  name: string;
  play?: string; // play id
  remap?: RemapKey[];
  camera?: CamKey[];
  /** two synchronised viewports (comparison) */
  split?: [Panel, Panel];
  overlays?: Overlay[];
  sfx?: SfxCue[];
  /** how the shot enters: cut (default), flash, whip */
  enter?: 'cut' | 'flash' | 'whip';
  /** dim defenders/offence to focus attention */
  focus?: 'O' | 'X';
  /** players not drawn (e.g. the defender whose eyes are the camera) */
  hide?: string[];
  /** local seconds after which hidden players reappear */
  hideUntil?: number;
};

export type TacticalEpisode = {
  id: string;
  title: string;
  fps?: 30 | 60;
  voice: string;
  words: {text: string; start: number; end: number}[];
  tail: number;
  music?: {src?: string; volume?: number};
  plays: Record<string, Play>;
  shots: Shot[];
  techniques?: {id: string; name: string; shots: string[]; how: string}[];
  emphasis?: string[];
  display?: Record<string, string>;
};

const EASE = {
  linear: (x: number) => x,
  inOut: (x: number) => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2),
  out: (x: number) => 1 - (1 - x) * (1 - x),
  in: (x: number) => x * x,
};

/** play time for a local time, given remap keys already resolved to numbers */
export const remapAt = (keys: [number, number, keyof typeof EASE | undefined][], lt: number): number => {
  if (!keys.length) return lt;
  if (lt <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [a0, p0] = keys[i];
    const [a1, p1, e] = keys[i + 1];
    if (lt >= a0 && lt <= a1) {
      const u = (lt - a0) / Math.max(1e-6, a1 - a0);
      return p0 + (p1 - p0) * EASE[e ?? 'linear'](u);
    }
  }
  return keys[keys.length - 1][1];
};

export const resolveRemap = (keys: RemapKey[], play: Play, toLocal: (a: LocalT) => number) =>
  keys.map(([l, p, e]) => [toLocal(l), typeof p === 'string' ? mark(play, p) : p, e] as [number, number, keyof typeof EASE | undefined]);

/** playback speed (play seconds per real second) at local time — used for motion-blur and SFX logic */
export const speedAt = (keys: [number, number, keyof typeof EASE | undefined][], lt: number) => (remapAt(keys, lt + 1 / 120) - remapAt(keys, lt - 1 / 120)) * 60;
