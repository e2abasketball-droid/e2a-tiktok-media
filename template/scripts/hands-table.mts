// Hands table (2026-11-20, Pistol Fake Handoff): for each play frame S, the ball phase/owner (play.ts ballPhase), the
// ball's world position and the distance from the ball to each hand of the listed players (rig poses, same S).
// Used for the keep/give hands test labels and the contact before/at/after sheets.
//   node --experimental-strip-types scripts/hands-table.mts tactical/plays/pfh-give.json O1,O2 43 60 [step] > table.json
import fs from 'node:fs';
import {ballPhase, sample} from '../src/tactical/play.ts';
import {poseAt} from '../src/t3d/rig.ts';
import {FIBA} from '../src/tactical/geometry.ts';
const [pf, idsS, f0, f1, st] = process.argv.slice(2);
const p = JSON.parse(fs.readFileSync(pf, 'utf8'));
const RIM = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ] as [number, number, number];
const ids = idsS.split(',');
const rows = [];
for (let f = +f0; f <= +f1 + 1e-9; f += +(st ?? 1)) {
  const t = f / 30; const b = sample(p, t).ball; const ph = ballPhase(p, t);
  const hands: Record<string, number[]> = {};
  for (const id of ids) {
    const ps = poseAt(p, id, t, {holder: b.holder, pos: b.pos as [number, number, number]}, RIM);
    hands[id] = ps.hand.map((h: number[]) => +Math.hypot(...h.map((v, i) => v - b.pos[i])).toFixed(3));
  }
  rows.push({S: f, t: +t.toFixed(4), phase: ph.phase, owner: ph.owner ?? null, holder: b.holder ?? null, ball: b.pos.map((v: number) => +v.toFixed(3)), hands});
}
console.log(JSON.stringify(rows));
