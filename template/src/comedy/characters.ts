// E2A YouTube Comedy — the cast. Change a look here and every episode follows.
import type {Look} from './toon';

/** AND1 — "The And-One Guy": black jersey, gold trim, #11, black/gold headband, huge brows. */
export const AND1: Look = {
  id: 'and1',
  skin: '#7B4B2F',
  hair: '#120C08',
  hairStyle: 'fade',
  jersey: '#121214',
  trim: '#C9A24D',
  number: '11',
  numColor: '#E3BE68',
  shorts: '#121214',
  shoe: '#1A1A1C',
  shoeAccent: '#C9A24D',
  sock: '#F2F2F0',
  headband: {base: '#111113', stripe: '#C9A24D'},
  wristband: '#C9A24D',
  brow: 1.55,
  browColor: '#0E0906',
  iris: '#4A2A14',
  build: 1.06,
};

/** ACE — "The Normal Teammate": blue jersey #4, white trim, curly top, calm. */
export const ACE: Look = {
  id: 'ace',
  skin: '#D8A57E',
  hair: '#3A2516',
  hairStyle: 'curls',
  jersey: '#1F5FB8',
  trim: '#F4F4F2',
  number: '4',
  numColor: '#F4F4F2',
  shorts: '#1F5FB8',
  shoe: '#F2F2F0',
  shoeAccent: '#1F5FB8',
  sock: '#F2F2F0',
  brow: 1.05,
  browColor: '#2A1A10',
  iris: '#3B5A2A',
  build: 1.0,
};

/** BUCKETS — "The Ball Hog" (EP002): purple #7, white trim, lime shoes + wristband, tall flat-top, cocky grin, expressive brows. */
export const BUCKETS: Look = {
  id: 'buckets',
  skin: '#A86F48',
  hair: '#17100B',
  hairStyle: 'flattop',
  jersey: '#4E2378',
  trim: '#F6F1E8',
  number: '7',
  numColor: '#F6F1E8',
  shorts: '#4E2378',
  shoe: '#B8E04A',
  shoeAccent: '#4E2378',
  sock: '#F2F2F0',
  wristband: '#B8E04A',
  brow: 1.35,
  browColor: '#120C08',
  iris: '#3A2412',
  build: 1.05,
};

/** pickup-game defenders (EP002, non-speaking): plain grey practice tops, no branding */
export const DEF1: Look = {
  id: 'def1',
  skin: '#C68E66',
  hair: '#2A1C12',
  hairStyle: 'fade',
  jersey: '#8D939C',
  trim: '#5C626B',
  number: '2',
  numColor: '#F4F4F2',
  shorts: '#3A3F47',
  shoe: '#2A2D33',
  shoeAccent: '#8D939C',
  sock: '#F2F2F0',
  brow: 1.0,
  browColor: '#1E140C',
  iris: '#3A2A1A',
  build: 1.04,
};
export const DEF2: Look = {
  ...DEF1,
  id: 'def2',
  skin: '#6E4128',
  hair: '#0E0A07',
  hairStyle: 'curls',
  number: '9',
  build: 1.08,
};
