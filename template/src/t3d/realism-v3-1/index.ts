// E2A Realism V3.1 (2026-11-22) — asset manifest of the V3.1 athlete (athleteRenderer 'v31', opt-in; the default stays
// 'legacy', see realism-v3/index.ts). Rebuild: tools/blender/build_player.py --rig v3 --garment v31 --body v31 --shoe v31.
//   public/players3d/e2a_player_{off,def}_v31.glb  athletic body, sole slab, loose jersey / shorts (V3 rig: 27 bones)
//   motion.ts / clips.ts                           hand-keyed body motion for players with an authored clip
import type {RigV3} from '../realism-v3/athleteV3.ts';
import off from './rigs/e2a-off-v31.rig.json';
import def from './rigs/e2a-def-v31.rig.json';

export const PLAYER3D_V31 = {
  version: 'e2a-player-v31',
  off: {glb: 'players3d/e2a_player_off_v31.glb', rig: off as unknown as RigV3},
  def: {glb: 'players3d/e2a_player_def_v31.glb', rig: def as unknown as RigV3},
};
