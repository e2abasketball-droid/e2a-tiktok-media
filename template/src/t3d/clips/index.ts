// E2A 3D engine — LAB: registry of skeletal clips bundled with the engine (see ../skelclip.ts).
// Each clip is exported by tools/blender/export_clip.py; the matching mesh + skeleton + action is the .glb in public/lab3d/.
import {registerClip} from '../skelclip.ts';
import type {SkelClip} from '../skelclip.ts';
import screenRoll5452 from './screen-roll-5452.json';
import screenRoll5452m from './screen-roll-5452m.json';

registerClip('screen-roll-5452', screenRoll5452 as unknown as SkelClip);
// mirrored take (pivot on the right ball, opens to his left): matches the lab play geometry, see the lab INFORME
registerClip('screen-roll-5452m', screenRoll5452m as unknown as SkelClip);
export const CLIP_GLB: Record<string, string> = {
  'screen-roll-5452': 'lab3d/e2a_bloqueador_screen_roll.glb',
  'screen-roll-5452m': 'lab3d/e2a_bloqueador_screen_roll.glb',
};
