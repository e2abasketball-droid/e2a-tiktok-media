// Which character and animation each player of a play / episode bundle will use in Tactical3D(V2), and why.
//   node --experimental-strip-types scripts/players3d-plan.mts <play.json | bundle.json | episode.json> [--json out.json]
// Same pure function as the render (src/t3d/player3d.ts planPlayers3d) + a check that the .glb files exist and parse.
import fs from 'node:fs';
import path from 'node:path';
import {PLAYER3D, describePlan, planPlayers3d, registerPlayerRig} from '../src/t3d/player3d.ts';
import {registerClip} from '../src/t3d/skelclip.ts';
import type {SkelClip} from '../src/t3d/skelclip.ts';
import type {PlayWithActions} from '../src/t3d/rig.ts';

for (const v of ['off', 'def'] as const) registerPlayerRig(v, JSON.parse(fs.readFileSync(`src/t3d/players/e2a-${v}.rig.json`, 'utf8')));
for (const f of fs.readdirSync('src/t3d/clips')) if (f.endsWith('.json')) registerClip(f.replace('.json', ''), JSON.parse(fs.readFileSync(path.join('src/t3d/clips', f), 'utf8')) as SkelClip);
const args = process.argv.slice(2);
const file = args[0];
const jsonAt = args.indexOf('--json');
const d = JSON.parse(fs.readFileSync(file, 'utf8'));
const ep = d.episode ?? (d.shots ? d : null);
const plays: Record<string, PlayWithActions> = {};
if (ep) {
  for (const [k, v] of Object.entries(ep.plays as Record<string, unknown>)) plays[k] = typeof v === 'string' ? JSON.parse(fs.readFileSync(`tactical/plays/${v}.json`, 'utf8')) : (v as PlayWithActions);
} else plays[d.id] = d;
// glb check (GLB header + JSON chunk)
const glb: Record<string, string> = {};
for (const v of ['off', 'def'] as const) {
  const p = path.join('public', PLAYER3D[v].glb);
  try {
    const b = fs.readFileSync(p);
    const ok = b.readUInt32LE(0) === 0x46546c67;
    const j = JSON.parse(b.subarray(20, 20 + b.readUInt32LE(12)).toString('utf8'));
    const anims = (j.animations ?? []).map((a: {name: string}) => a.name);
    glb[v] = ok ? `ok ${PLAYER3D[v].glb} ${(b.length / 1e6).toFixed(2)} MB, ${j.skins?.[0]?.joints?.length} joints, actions ${anims.join(',')}` : 'bad header';
  } catch (e) {
    glb[v] = `MISSING ${p}: ${(e as Error).message}`;
  }
}
const out: Record<string, unknown> = {version: PLAYER3D.version, glb, plays: {}};
console.log(`players3d ${PLAYER3D.version}`);
for (const [v, s] of Object.entries(glb)) console.log(`  glb ${v}: ${s}`);
const force = ep?.players3d === 'A' ? 'A' : undefined;
for (const [k, play] of Object.entries(plays)) {
  const plan = planPlayers3d(play, {force, faces: !!ep?.faces});
  (out.plays as Record<string, unknown>)[k] = plan;
  console.log(`  play ${k} (${play.id}): ${describePlan(plan).join(' | ')}`);
}
if (jsonAt >= 0) fs.writeFileSync(args[jsonAt + 1], JSON.stringify(out, null, 1));
