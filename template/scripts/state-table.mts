// E2A — state table of a play every 0.1 s (brief BLOB sec. 06 / FASE 1.4): positions (brief axes when --mirror),
// ball owner / phase, for comparing the implementation with the contract.
//   node --experimental-strip-types scripts/state-table.mts tactical/plays/<id>.json [--mirror] > table.csv
import fs from 'node:fs';
import {posAt, sample} from '../src/tactical/play.ts';
const f = process.argv[2];
const mirror = process.argv.includes('--mirror');
const p = JSON.parse(fs.readFileSync(f, 'utf8'));
const ids: string[] = p.players.map((x: {id: string}) => x.id);
console.log(['t', ...ids.flatMap((i) => [`${i}_x`, `${i}_y`]), 'ball_holder', 'ball_x', 'ball_y', 'ball_z'].join(','));
for (let k = 0; k * 0.1 <= p.duration + 1e-9; k++) {
  const t = Math.min(k * 0.1, p.duration);
  const fr = sample(p, t);
  const row = [t.toFixed(1), ...ids.flatMap((i) => {const q = posAt(p.tracks[i], t); return [((mirror ? -1 : 1) * q[0]).toFixed(2), q[1].toFixed(2)];})];
  const b = fr.ball as {holder?: string; pos: number[]};
  row.push(b.holder ?? 'air', ((mirror ? -1 : 1) * b.pos[0]).toFixed(2), b.pos[1].toFixed(2), (b.pos[2] ?? 0).toFixed(2));
  console.log(row.join(','));
}
