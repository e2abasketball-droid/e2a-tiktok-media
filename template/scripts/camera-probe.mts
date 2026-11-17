// Camera probe: prints the Tactical3D camera position (court coords x, y, z) and the shot for each frame,
// replicating the Tactical3D layout (anchored shots + remap). Used to trace the 3.2 s backboard band.
// Run: node --experimental-strip-types scripts/camera-probe.mts <episode.json> <words.json> <frame0> <frame1>
import fs from 'node:fs';
import {camera3At} from '../src/t3d/camera3d.ts';
import {makeTacticalResolver, localResolver, resolveRemap, remapAt} from '../src/tactical/edit.ts';
const ep = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
ep.words = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
ep.plays = Object.fromEntries(Object.entries(ep.plays).map(([k, v]) => [k, JSON.parse(fs.readFileSync(`tactical/plays/${v}.json`, 'utf8'))]));
const T = makeTacticalResolver(ep.words);
const total = ep.words.at(-1).end + ep.tail;
const starts = ep.shots.map((s: any, i: number) => (i === 0 ? 0 : T(s.at)));
const [f0, f1] = process.argv.slice(4).map(Number);
for (let f = f0; f <= f1; f++) {
  const t = f / 30;
  const i = starts.findLastIndex((s: number) => s <= t);
  const shot = ep.shots[i]; const start = starts[i]; const end = starts[i + 1] ?? total;
  const toLocal = localResolver(T, start, end);
  const play = ep.plays[shot.play];
  const lt = t - start; const pt = remapAt(resolveRemap(shot.remap, play, toLocal), lt);
  const cam = camera3At(play, shot.camera.map((k: any) => ({...k, at: toLocal(k.at)})), lt, pt);
  console.log(f, t.toFixed(3), shot.id, 'lt', lt.toFixed(3), 'pos(court x,y,z)', cam.pos.map((v) => v.toFixed(2)).join(','));
}
