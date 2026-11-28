// E2A (2026-11-28, Shuffle Cut): sample the engine's track spline (posAt / velAt) of every player at given times, so the
// canonical keyframes store exactly what the engine draws. npx tsx scripts/sample-play-positions.mts <play.json> t1 t2 ...
import fs from 'node:fs';
import {posAt, velAt} from '../src/tactical/play.ts';
const [inp, ...ts] = process.argv.slice(2);
const play = JSON.parse(fs.readFileSync(inp, 'utf8'));
const out: Record<string, Record<string, number[]>> = {};
for (const t of ts.map(Number)) {
  const row: Record<string, number[]> = {};
  for (const p of play.players) {
    const q = posAt(play.tracks[p.id], t), v = velAt(play.tracks[p.id], t);
    row[p.id] = [q[0], q[1], v[0], v[1]];
  }
  out[String(t)] = row;
}
console.log(JSON.stringify(out));
