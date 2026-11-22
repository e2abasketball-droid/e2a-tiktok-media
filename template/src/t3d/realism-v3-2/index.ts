// E2A Realism V3.2 (2026-11-22) — asset manifest of the V3.2 athlete (athleteRenderer 'v32', opt-in; the default stays
// 'legacy'). Rebuild: tools/blender/build_player.py --rig v3 --garment v32 --body v31 --shoe v32 (see produccion/realism-v3-2).
//   public/players3d/e2a_player_{off,def}_v32.glb  V3.1 body + stabilised apparel (smoothed hem weights, strap / fold
//                                                  correctives, separate shorts cloth), modelled shoe last
//   library.ts / clips32.ts / motion32.ts / cloth32.ts / scene32.ts   parametrised motion library and runtime
import type {RigV3} from '../realism-v3/athleteV3.ts';
import off from './rigs/e2a-off-v32.rig.json';
import def from './rigs/e2a-def-v32.rig.json';

export const PLAYER3D_V32 = {
  version: 'e2a-player-v32',
  off: {glb: 'players3d/e2a_player_off_v32.glb', rig: off as unknown as RigV3},
  def: {glb: 'players3d/e2a_player_def_v32.glb', rig: def as unknown as RigV3},
};
