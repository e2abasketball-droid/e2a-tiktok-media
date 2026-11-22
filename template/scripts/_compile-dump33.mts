// diagnosis: print the V3.3 compiled script of one or more players of a play
import fs from 'node:fs';
import {compilePlay33} from '../src/t3d/realism-v3-3/compile33.ts';
const [f, ...ids] = process.argv.slice(2);
const play = JSON.parse(fs.readFileSync(f, 'utf8'));
const c = compilePlay33(play) as any;
for (const id of ids) {
  const x = c[id] ?? c.players?.[id];
  console.log('==', id, JSON.stringify({profile: x.profile, role: x.role, unsupported: x.unsupported, summary: x.summary}));
  for (const s of x.script) console.log('  ', JSON.stringify(s, (k, v) => (typeof v === 'number' ? Math.round(v * 1000) / 1000 : v)));
}
