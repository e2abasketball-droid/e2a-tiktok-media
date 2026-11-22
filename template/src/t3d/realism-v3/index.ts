// E2A Realism V3 (2026-11-22) — asset manifest + feature flag of the V3 athlete renderer.
//   athleteRenderer: 'legacy' (DEFAULT, every existing episode: e2a-player-v1 / Realism V2-V3 apparel, unchanged pixels)
//                    'v3'     (opt-in per episode / shot / split): AthleteV3 = public/players3d/e2a_player_{off,def}_v3.glb
//                             (27 bones with fingers, knee / elbow / hip correctives, tube-cut shorts with cloth attributes,
//                             Fourier-smoothed trims) driven by athleteV3.ts, V3 jersey texture (crisp number)
// Rollback = leave the flag unset (or 'legacy'). Rebuild the assets: tools/blender/build_player.py --rig v3 --garment v3.
import type {RigV3} from './athleteV3.ts';
import off from './rigs/e2a-off-v3.rig.json';
import def from './rigs/e2a-def-v3.rig.json';

//                    'v31'    (opt-in, Realism V3.1): e2a_player_{off,def}_v31.glb + AUTHORED body motion for players with a
//                             hand-keyed clip (realism-v3-1/motion.ts), engine pose (V3 bridge) for the others
//                    'v32'    (opt-in, Realism V3.2): e2a_player_{off,def}_v32.glb + the parametrised motion library
//                             (realism-v3-2/), separate jersey / shorts cloth; Test A / B can swap motion or mesh
export type AthleteRenderer = 'legacy' | 'v3' | 'v31' | 'v32';
export const DEFAULT_ATHLETE_RENDERER: AthleteRenderer = 'legacy';
export const isV3 = (r?: AthleteRenderer) => (r ?? DEFAULT_ATHLETE_RENDERER) === 'v3';
export const isV31 = (r?: AthleteRenderer) => (r ?? DEFAULT_ATHLETE_RENDERER) === 'v31';
export const isV32 = (r?: AthleteRenderer) => (r ?? DEFAULT_ATHLETE_RENDERER) === 'v32';

export const PLAYER3D_V3 = {
  version: 'e2a-player-v3',
  off: {glb: 'players3d/e2a_player_off_v3.glb', rig: off as unknown as RigV3},
  def: {glb: 'players3d/e2a_player_def_v3.glb', rig: def as unknown as RigV3},
};
