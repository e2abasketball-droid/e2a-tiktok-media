// E2A YouTube Comedy — reusable body poses / gestures (patches over the neutral stance).
// Angles in radians. Combine with face patches from FACES.
import type {Face, PosePatch} from './pose';

export const STAND: PosePatch = {lean: 0, roll: 0, sit: 0, spineBend: 0.03, spineTwist: 0, spineSide: 0, lShPitch: 0.05, lShOut: 0.16, lShTwist: 0, lElbow: 0.25, rShPitch: 0.05, rShOut: 0.16, rShTwist: 0, rElbow: 0.25,
  lHip: 0.02, lHipOut: 0.06, lKnee: 0.06, lAnkle: 0, rHip: 0.02, rHipOut: 0.06, rKnee: 0.06, rAnkle: 0, lPoint: 0, rPoint: 0, lift: 0};

/** relaxed teammate stance: weight on one leg, slight hip shift */
export const RELAXED: PosePatch = {...STAND, spineSide: 0.04, roll: -0.02, lHip: 0.05, lKnee: 0.16, lHipOut: 0.1, rHipOut: 0.04, lShOut: 0.12, rShOut: 0.12, lElbow: 0.35, rElbow: 0.3};

/** athletic ready stance */
export const READY: PosePatch = {...STAND, lean: 0.12, lHip: 0.35, rHip: 0.35, lKnee: 0.6, rKnee: 0.6, lAnkle: -0.2, rAnkle: -0.2, lHipOut: 0.14, rHipOut: 0.14, lElbow: 0.9, rElbow: 0.9, lShPitch: 0.35, rShPitch: 0.35};

/** "AND ONE!" celebration: chest out, both arms flexed out wide, head back */
export const FLEX: PosePatch = {...STAND, spineBend: -0.14, lean: -0.05, lShOut: 1.25, rShOut: 1.25, lShPitch: 0.15, rShPitch: 0.15, lShTwist: 1.5, rShTwist: 1.5, lElbow: 1.75, rElbow: 1.75,
  lHipOut: 0.2, rHipOut: 0.2, lKnee: 0.25, rKnee: 0.25, lHip: 0.12, rHip: 0.12, headPitch: -0.12};

/** foul call: left forearm across in front, right hand chops onto it */
export const CHOP_UP: PosePatch = {...STAND, spineBend: 0.08, lShPitch: 1.05, lShOut: 0.25, lShTwist: -1.2, lElbow: 1.45, rShPitch: 1.9, rShOut: 0.3, rElbow: 1.2, rShTwist: 0.2};
export const CHOP_DOWN: PosePatch = {...CHOP_UP, rShPitch: 1.15, rElbow: 0.85};

/** dismissive wave: right hand flicks out, chin up */
export const WAVE_A: PosePatch = {...STAND, rShPitch: 0.75, rShOut: 0.35, rElbow: 1.7, rShTwist: 0.4, headPitch: -0.18, headRoll: 0.08};
export const WAVE_B: PosePatch = {...WAVE_A, rShPitch: 0.9, rShOut: 0.9, rElbow: 0.65};

/** jump shot set + release + follow-through */
export const SHOT_SET: PosePatch = {...STAND, lHip: 0.3, rHip: 0.3, lKnee: 0.55, rKnee: 0.55, lAnkle: -0.15, rAnkle: -0.15, rShPitch: 2.3, rShOut: 0.2, rElbow: 1.9, lShPitch: 2.1, lShOut: 0.45, lElbow: 1.7, headPitch: -0.15};
export const SHOT_RELEASE: PosePatch = {...STAND, lift: 0.25, rShPitch: 2.85, rShOut: 0.15, rElbow: 0.25, lShPitch: 2.4, lShOut: 0.55, lElbow: 0.9, lAnkle: 0.5, rAnkle: 0.5, lKnee: 0.1, rKnee: 0.1, headPitch: -0.2};

/** both arms straight up: "FOUL!" */
export const ARMS_UP: PosePatch = {lShPitch: 2.85, rShPitch: 2.85, lShOut: 0.4, rShOut: 0.4, lElbow: 0.2, rElbow: 0.2, lShTwist: 0, rShTwist: 0};

/** sitting on the floor, legs out, leaning back on the hands */
export const SIT: PosePatch = {sit: 1, lean: -0.22, spineBend: 0.18, lHip: 1.38, rHip: 1.22, lKnee: 0.12, rKnee: 0.55, lHipOut: 0.18, rHipOut: 0.22, lAnkle: 0.3, rAnkle: 0.2,
  lShPitch: -0.45, rShPitch: -0.45, lShOut: 0.32, rShOut: 0.32, lElbow: 0.1, rElbow: 0.1, lift: 0};

/** seated, hands on knees */
export const SIT_REST: PosePatch = {...SIT, lean: -0.05, spineBend: 0.25, lShPitch: 0.55, rShPitch: 0.6, lShOut: 0.25, rShOut: 0.25, lElbow: 0.6, rElbow: 0.5};

/** seated, pointing down at the floor beside him (right hand) */
export const SIT_POINT: PosePatch = {...SIT_REST, rShPitch: 0.35, rShOut: 0.55, rElbow: 0.15, rPoint: 1, rShTwist: 0.2};

/** seated, pointing down at the floor beside him (left hand) */
export const SIT_POINT_L: PosePatch = {...SIT_REST, lShPitch: 0.6, lShOut: 0.5, lElbow: 0.1, lPoint: 1, lShTwist: 0.2};

/** arms crossed (ACE) */
export const CROSSED: PosePatch = {...RELAXED, lShPitch: 0.75, rShPitch: 0.8, lShOut: 0.12, rShOut: 0.12, lShTwist: -1.1, rShTwist: -1.1, lElbow: 1.95, rElbow: 2.0};

// ---------- faces ----------
export const FACES: Record<string, Partial<Face>> = {
  neutral: {browL: 0, browR: 0, browTilt: 0, lid: 0.12, squint: 0, smile: 0, open: 0, wide: 1, smirk: 0},
  triumph: {browL: 0.75, browR: 0.75, browTilt: -0.25, lid: 0, squint: 0.15, smile: 0.35, wide: 1.25},
  shout: {browL: 0.85, browR: 0.85, browTilt: -0.45, lid: 0, squint: 0.25, smile: 0.1, wide: 1.2},
  smug: {browL: 0.5, browR: 0.35, browTilt: 0.1, lid: 0.72, squint: 0.3, smile: 0.5, smirk: 0.5, wide: 1.05},
  deadpan: {browL: -0.1, browR: -0.05, browTilt: 0, lid: 0.45, squint: 0.1, smile: -0.12, wide: 0.9},
  flat: {browL: 0.05, browR: 0.05, browTilt: 0.05, lid: 0.32, squint: 0.05, smile: -0.08, wide: 0.92},
  doubt: {browL: 0.75, browR: -0.15, browTilt: 0.35, lid: 0.25, squint: 0.15, smile: -0.25, smirk: -0.3, wide: 0.9},
  annoyed: {browL: -0.85, browR: -0.85, browTilt: -0.95, lid: 0.32, squint: 0.55, smile: -0.6, wide: 0.95},
  outrage: {browL: 0.9, browR: 0.9, browTilt: -0.7, lid: 0, squint: 0.3, smile: -0.25, wide: 1.25},
  shock: {browL: 1, browR: 1, browTilt: 0.6, lid: -0.05, squint: 0, open: 0.65, smile: -0.2, wide: 0.75},
  serious: {browL: -0.4, browR: -0.4, browTilt: -0.45, lid: 0.3, squint: 0.2, smile: -0.22, wide: 0.85},
  lookAround: {browL: 0.7, browR: 0.7, browTilt: 0.45, lid: 0.05, squint: 0, smile: -0.2, wide: 0.82},
  done: {browL: 0.25, browR: 0.1, browTilt: 0.55, lid: 0.5, squint: 0.05, smile: -0.32, wide: 0.88},
};
