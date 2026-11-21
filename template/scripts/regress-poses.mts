// Realism V2 regression (2026-11-21): legacy plays (no `realism` key) must give EXACTLY the poses and ball of the
// pre-V2 engine (commit d700987). Hashes every pose joint + ball position at 30 fps and compares with the stored hashes.
//   npx tsx scripts/regress-poses.mts            -> compare with tactical/reports/realism-v2-2026-11-21/regression-hashes.json
//   npx tsx scripts/regress-poses.mts --write    -> (re)write the hashes (only from the baseline engine!)
import fs from 'node:fs';
import crypto from 'node:crypto';
import '../src/t3d/rig.ts';
import {sample} from '../src/tactical/play.ts';
import {poseAt} from '../src/t3d/rig.ts';
import type {PlayWithActions} from '../src/t3d/rig.ts';
const REF = 'tactical/reports/realism-v2-2026-11-21/regression-hashes.json';
const ref = JSON.parse(fs.readFileSync(REF, 'utf8')) as {engine: string; plays: Record<string, string>};
const out: Record<string, string> = {};
let bad = 0;
for (const id of Object.keys(ref.plays)) {
  const play = JSON.parse(fs.readFileSync(`tactical/plays/${id}.json`, 'utf8')) as PlayWithActions & {choreo?: Record<string, unknown>};
  const h = crypto.createHash('sha256');
  for (let k = 0; k <= Math.round(play.duration * 30); k++) {
    const t = k / 30, b = sample(play, t).ball;
    h.update(JSON.stringify(b.pos));
    for (const p of play.players) {
      if (play.choreo?.[p.id]) continue;
      const ps = poseAt(play, p.id, t, {holder: b.holder, pos: b.pos}, [0, 1.575, 3.05]);
      h.update(JSON.stringify([ps.pelvis, ps.chest, ps.head, ps.heading, ps.chestYaw, ps.hip, ps.knee, ps.ankle, ps.toe, ps.shoulder, ps.elbow, ps.wrist, ps.hand]));
    }
  }
  out[id] = h.digest('hex').slice(0, 16);
  const ok = out[id] === ref.plays[id];
  if (!ok) bad++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${id}  ${out[id]}${ok ? '' : ` (expected ${ref.plays[id]})`}`);
}
if (process.argv.includes('--write')) fs.writeFileSync(REF, JSON.stringify({...ref, plays: out}, null, 1) + '\n');
console.log(`${Object.keys(out).length - bad}/${Object.keys(out).length} legacy plays identical to ${ref.engine}`);
process.exitCode = bad ? 1 : 0;
