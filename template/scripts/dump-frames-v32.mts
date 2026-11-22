// E2A Realism V3.2 (2026-11-22) — per-frame dump of what the renderer feeds a skinned athlete (bones, hips, scale,
// corrective weights, cloth uniforms, ball) for the mesh-level QC in Python (scripts/qc_cloth_v32.py).
//   npx tsx scripts/dump-frames-v32.mts <play.json> --renderer v31|v32 [--players O1,O2] [--fps 30] [--t0 0 --t1 12.5] --out f.json
// Same code path as Scene.tsx (motionV3x -> framesV3x, clothV3x), evaluated in Node: no browser, deterministic.
import fs from 'node:fs';
import '../src/t3d/rig.ts';
import '../src/t3d/players/index.ts';
import {FIBA} from '../src/tactical/geometry.ts';
import type {V3} from '../src/tactical/geometry.ts';
import {sample} from '../src/tactical/play.ts';
import {poseAt} from '../src/t3d/rig.ts';
import type {PlayWithActions} from '../src/t3d/rig.ts';
import {meshScale} from '../src/t3d/skelclip.ts';
import {clothAt} from '../src/t3d/cloth2.ts';
import {PLAYER3D_V31} from '../src/t3d/realism-v3-1/index.ts';
import {clothV31, framesV31, motionV31} from '../src/t3d/realism-v3-1/motion.ts';
import {bonesV3} from '../src/t3d/realism-v3/athleteV3.ts';
import {PLAYER3D_V32} from '../src/t3d/realism-v3-2/index.ts';
import {athleteV32} from '../src/t3d/realism-v3-2/scene32.ts';

const args = process.argv.slice(2);
const opt = (k: string, d: string) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const file = args[0];
const play = JSON.parse(fs.readFileSync(file, 'utf8')) as PlayWithActions;
const renderer = opt('--renderer', 'v32');
const ids = opt('--players', 'O1').split(',');
const fps = Number(opt('--fps', '30'));
const t0 = Number(opt('--t0', '0')), t1 = Number(opt('--t1', String(play.duration)));
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const r5 = (x: number) => Math.round(x * 1e5) / 1e5;
const out: Record<string, unknown[]> = {};
for (const id of ids) {
  const variant = play.players.find((p) => p.id === id)!.team === 'X' ? 'def' : 'off';
  const rows: unknown[] = [];
  for (let f = Math.round(t0 * fps); f <= Math.round(t1 * fps); f++) {
    const t = f / fps;
    const ball = sample(play, t).ball;
    let row: Record<string, unknown>;
    if (renderer === 'v31') {
      const rig = PLAYER3D_V31[variant].rig;
      const m = motionV31(play, id, t, rig);
      const pose = m ? m.pose : poseAt(play, id, t, {holder: ball.holder, pos: ball.pos, lag: sample(play, Math.max(0, t - 0.2)).ball.pos}, RIM);
      const sc = meshScale(rig, pose);
      const fr = m ? framesV31(rig, m) : bonesV3(rig, pose, sc, {pos: ball.pos, held: ball.holder === id});
      const cl = (m ? clothV31(play, id, t, rig) : undefined) ?? clothAt(play, id, t);
      row = {t, sc, bones: fr.bones, hips: fr.hips, morph: fr.morph, cloth: {jersey: cl, shorts: cl}, ball: m?.ball ?? ball.pos};
    } else {
      const rig = PLAYER3D_V32[variant].rig;
      const a = athleteV32(play, id, t, rig, {holder: ball.holder, pos: ball.pos, lag: sample(play, Math.max(0, t - 0.2)).ball.pos});
      row = {t, sc: a.sc, bones: a.fr.bones, hips: a.fr.hips, morph: a.fr.morph, cloth: a.cloth, ball: a.ball ?? ball.pos, debug: a.debug};
    }
    rows.push(JSON.parse(JSON.stringify(row, (_k, v) => (typeof v === 'number' ? r5(v) : v))));
  }
  out[id] = rows;
}
fs.writeFileSync(opt('--out', '/dev/stdout'), JSON.stringify({play: play.id, renderer, fps, players: out}));
