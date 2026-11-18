// QC of the default E2A player meshes (player3d.ts) on a play, WITHOUT rendering: forward kinematics of the mesh skeleton
// from the same bone rotations the render uses, against the engine pose.
//   node --experimental-strip-types scripts/qc-players3d.mts tactical/plays/<id>.json [--fps 30] [--json out.json]
// Checks (FAIL above):
//   ankle     mesh ankle vs engine ankle (rig / choreo players: legs re-solved with the mesh lengths) ≤ 15 mm
//   slide     mesh ankle motion while the engine ankle is still (planted foot) ≤ 2 mm/frame
//   hand      mesh fingertips vs engine hand point (hands on the ball) ≤ 40 mm
//   head      head face pitch within [-35, +15] deg (no head looking up at the sky)
//   seek      the same play time gives the same bones twice (pure function: playback = slow motion = seek)
import fs from 'node:fs';
import path from 'node:path';
import type {PlayWithActions} from '../src/t3d/rig.ts';
import {registerClip} from '../src/t3d/skelclip.ts';
import type {SkelClip} from '../src/t3d/skelclip.ts';
import {PLAYER3D, registerPlayerRig} from '../src/t3d/player3d.ts';
import {meshQC} from '../src/t3d/player3dqc.ts';

for (const v of ['off', 'def'] as const) registerPlayerRig(v, JSON.parse(fs.readFileSync(`src/t3d/players/e2a-${v}.rig.json`, 'utf8')));
for (const f of fs.readdirSync('src/t3d/clips')) if (f.endsWith('.json') && f !== 'registry.json') registerClip(f.replace('.json', ''), JSON.parse(fs.readFileSync(path.join('src/t3d/clips', f), 'utf8')) as SkelClip);
const args = process.argv.slice(2);
const file = args[0];
const fps = Number(args[args.indexOf('--fps') + 1]) || 30;
const play = JSON.parse(fs.readFileSync(file, 'utf8')) as PlayWithActions;
const {plan, checks} = meshQC(play, fps);
console.log(`players3d ${PLAYER3D.version} — ${play.id}: ${Object.values(plan).map((p) => `${p.id}:${p.look}/${p.clip ?? p.anim}`).join(' ')}`);
for (const [name, ok, v] of checks) console.log(`${ok ? 'PASS' : 'FAIL'}  ${name} — ${v}`);
const ji = args.indexOf('--json');
if (ji >= 0) fs.writeFileSync(args[ji + 1], JSON.stringify({play: play.id, plan, checks}, null, 1));
