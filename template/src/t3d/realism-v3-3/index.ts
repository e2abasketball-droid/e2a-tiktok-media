// E2A Realism V3.3 (2026-11-22) — athleteRenderer 'v33' (opt-in; the default stays 'legacy'). V3.3 changes MOTION,
// BALL and CONTACT (library33 / compile33 / motion33 / scene33); it renders on the V3.2 meshes (no new asset), so
// PLAYER3D_V33 points at the V3.2 GLBs and rigs.
import {PLAYER3D_V32} from '../realism-v3-2/index.ts';

export const PLAYER3D_V33 = {...PLAYER3D_V32, version: 'e2a-player-v33 (V3.2 mesh)'};
export {athleteV33} from './scene33.ts';
export {ballV33, ballOwner33, resetV33Caches} from './motion33.ts';
