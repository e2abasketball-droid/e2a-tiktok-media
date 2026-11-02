export type Pt = [number, number]; // court feet: x 0..50 (left→right), y 0..47 (baseline→half-court)
export type Waypoint = {t: number; x: number; y: number; dribble?: boolean};
export type Word = {w: string; s: number; e: number};
export type Player = {id: string; team: 'o' | 'd'; label: string; path: Waypoint[]};
export type BallPoint = {t: number; at?: string; x?: number; y?: number};
export type ArrowKind = 'cut' | 'pass' | 'dribble' | 'screen';
export type Arrow = {kind: ArrowKind; from: Pt | string; to: Pt | string; t0: number; t1: number; show?: number};
export type Highlight = {x: number; y: number; r: number; t0: number; t1: number};
export type Step = {t0: number; t1: number; tag: string; label: string; focus?: {x: number; y: number; zoom: number}};
export type Sfx = {t: number; file: 'whoosh' | 'pop' | 'catch' | 'swish' | 'sting'; volume?: number};
export type Episode = {
  id: string; // e.g. "ep02-horns"
  title: string; // cover title
  kicker: string; // e.g. "OFFENCE"
  concept: string;
  durationSec: number;
  voice: string; // file in public/ (narration mp3)
  words: Word[];
  players: Player[];
  ball: BallPoint[];
  arrows: Arrow[];
  highlights: Highlight[];
  steps: Step[];
  sfx: Sfx[];
};
