// Video timecodes of play marks: for every shot, the first frame where the remapped play time crosses each mark.
// Run: node --experimental-strip-types scripts/mark-times.mts tactical/episodes/<id>.json
import fs from 'node:fs';
import path from 'node:path';
import {makeTacticalResolver, localResolver, resolveRemap, remapAt} from '../src/tactical/edit.ts';
const ep = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const words = JSON.parse(fs.readFileSync(path.join(path.dirname(process.argv[2]), `${ep.id}.words.json`), 'utf8'));
const plays = Object.fromEntries(Object.entries(ep.plays).map(([k, v]) => [k, JSON.parse(fs.readFileSync(`tactical/plays/${v}.json`, 'utf8'))]));
const T = makeTacticalResolver(words);
const total = words.at(-1).end + ep.tail;
const starts = ep.shots.map((s: any, i: number) => (i === 0 ? 0 : T(s.at)));
ep.shots.forEach((sh: any, i: number) => {
  const st = starts[i], en = starts[i + 1] ?? total, play = plays[sh.play];
  const keys = resolveRemap(sh.remap, play, localResolver(T, st, en));
  const hits: string[] = [];
  let prev = remapAt(keys, 0);
  for (let f = Math.round(st * 30) + 1; f < Math.round(en * 30); f++) {
    const pt = remapAt(keys, f / 30 - st);
    for (const [m, v] of Object.entries(play.marks as Record<string, number>)) if (prev < v && pt >= v) hits.push(`${m}@${(f / 30).toFixed(2)}`);
    prev = pt;
  }
  console.log(`${sh.id} ${st.toFixed(2)}-${en.toFixed(2)} play ${sh.play} ${remapAt(keys, 0).toFixed(2)}->${remapAt(keys, en - st).toFixed(2)} | ${hits.join(' ')}`);
});
