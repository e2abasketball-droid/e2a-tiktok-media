// E2A Realism V3.3 — determinism test: every player's bones and the ball must be a pure function of (play, id, t, rig).
// Evaluates all frames in ascending, descending and seeded-random order (caches reset before each pass, and a second
// random pass WITHOUT reset, i.e. with warm caches from another order) and reports the max difference.
//   tsx scripts/qc-determinism-v33.mts tactical/plays/<play>.json [--fps 30] [--json out.json]
import fs from 'node:fs';
import '../src/t3d/rig.ts';
import '../src/t3d/players/index.ts';
import {sample} from '../src/tactical/play.ts';
import {PLAYER3D_V33, athleteV33, ballV33, resetV33Caches} from '../src/t3d/realism-v3-3/index.ts';

const args = process.argv.slice(2);
const file = args[0];
const opt = (k: string, d: string) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const FPS = +opt('--fps', '30');
const play = JSON.parse(fs.readFileSync(file, 'utf8'));
const ids: string[] = play.players.map((p: {id: string}) => p.id);
const rigOf = (id: string) => PLAYER3D_V33[play.players.find((p: {id: string; team: string}) => p.id === id)?.team === 'X' ? 'def' : 'off'].rig;
const N = Math.floor(play.duration * FPS);
const frames = [...Array(N + 1).keys()];

const evalFrame = (f: number): number[] => {
  const t = f / FPS;
  const b = sample(play, t).ball;
  const out: number[] = [...ballV33(play, t)];
  for (const id of ids) {
    const a = athleteV33(play, id, t, rigOf(id), {holder: b.holder, pos: b.pos, lag: sample(play, Math.max(0, t - 0.2)).ball.pos});
    out.push(...a.fr.hips);
    for (const k of Object.keys(a.fr.bones).sort()) out.push(...a.fr.bones[k]);
  }
  return out;
};
const run = (order: number[], reset = true) => {
  if (reset) resetV33Caches();
  const r = new Map<number, number[]>();
  for (const f of order) r.set(f, evalFrame(f));
  return r;
};
let seed = 12345;
const rnd = () => ((seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff);
const shuffled = [...frames].sort(() => rnd() - 0.5);
const t0 = Date.now();
const A = run(frames);
const D = run([...frames].reverse());
const R = run(shuffled);
const W = run([...shuffled].reverse(), false);
const diff = (X: Map<number, number[]>) => {
  let m = 0, at = -1;
  for (const f of frames) {
    const a = A.get(f)!, x = X.get(f)!;
    for (let i = 0; i < a.length; i++) {
      const d = Math.abs(a[i] - x[i]);
      if (d > m) { m = d; at = f; }
    }
  }
  return {maxAbsDiff: m, atFrame: at};
};
const res = {play: play.id, fps: FPS, frames: frames.length, players: ids.length, values: A.get(0)!.length, descending: diff(D), random: diff(R), randomWarm: diff(W), seconds: (Date.now() - t0) / 1000};
const ok = res.descending.maxAbsDiff === 0 && res.random.maxAbsDiff === 0 && res.randomWarm.maxAbsDiff === 0;
console.log(`qc-determinism-v33 ${play.id}: ${ok ? 'PASS (bit-identical)' : 'FAIL'}`, JSON.stringify(res));
if (args.includes('--json')) fs.writeFileSync(opt('--json', ''), JSON.stringify({...res, pass: ok}, null, 1));
process.exit(ok ? 0 : 1);
