// Pin/ring identity probe: for a global time, print where a player's feet, head and pin anchor project
// and which player's body is under the drawn label. Usage: pin-probe.mts <episode.json> <t> <player...>
import fs from 'node:fs';
import path from 'node:path';
import {localResolver, makeTacticalResolver, remapAt, resolveRemap} from '../src/tactical/edit.ts';
import {posAt} from '../src/tactical/play.ts';
import {camera3At} from '../src/t3d/camera3d.ts';
import * as THREE from 'three';
const W3 = (p: number[]) => [p[0], p[2], -p[1]] as [number, number, number];
const projector = (cam: any, W: number, H: number) => {
  const c = new THREE.PerspectiveCamera(cam.fov, W / H, 0.1, 120);
  c.position.set(...W3(cam.pos)); c.up.set(...W3(cam.up)); c.lookAt(...W3(cam.target));
  if (cam.roll) c.rotateZ((cam.roll * Math.PI) / 180);
  c.updateMatrixWorld(); c.updateProjectionMatrix();
  return (p: number[]) => { const v = new THREE.Vector3(...W3(p)).project(c); return {x: ((v.x + 1) / 2) * W, y: ((1 - v.y) / 2) * H}; };
};
const [epFile, tStr, ...ids] = process.argv.slice(2);
const ep = JSON.parse(fs.readFileSync(epFile, 'utf8'));
const words = JSON.parse(fs.readFileSync(path.join(path.dirname(epFile), `${ep.id}.words.json`), 'utf8'));
const plays: any = {};
for (const [k, v] of Object.entries(ep.plays as Record<string, string>)) plays[k] = JSON.parse(fs.readFileSync(`tactical/plays/${v}.json`, 'utf8'));
const T = makeTacticalResolver(words);
const total = words[words.length - 1].end + ep.tail;
const starts = ep.shots.map((s: any, i: number) => (i === 0 ? 0 : T(s.at)));
const t = Number(tStr);
const i = starts.findLastIndex((s: number) => s <= t);
const shot = ep.shots[i];
const end = i + 1 < starts.length ? starts[i + 1] : total;
const toLocal = localResolver(T, starts[i], end);
const play = plays[shot.play];
const lt = t - starts[i];
const pt = remapAt(resolveRemap(shot.remap, play, toLocal), lt);
const cam = camera3At(play, shot.camera.map((k: any) => ({...k, at: toLocal(k.at)})), lt, pt);
const pr = projector(cam as any, 1080, 1920);
console.log(`shot ${shot.id} lt ${lt.toFixed(2)} pt ${pt.toFixed(2)}`);
for (const id of ids.length ? ids : Object.keys(play.tracks)) {
  const p = posAt(play.tracks[id], pt);
  const f = pr([p[0], p[1], 0]), h = pr([p[0], p[1], 2.0]), a = pr([p[0], p[1], 2.25]);
  console.log(`${id} pos ${p[0].toFixed(2)},${p[1].toFixed(2)} feet ${f.x.toFixed(0)},${f.y.toFixed(0)} head ${h.x.toFixed(0)},${h.y.toFixed(0)} pin ${a.x.toFixed(0)},${a.y.toFixed(0)}`);
}
// pins of this shot through the V2 placement
import('../src/t3d/pinPlace.ts').then(({placePin}) => {
  for (const pn of (shot.screen ?? []).filter((o: any) => o.type === 'pin')) {
    const r = placePin(play, pn.player, pt, pr as any, pn.text, pn.size ?? 40, pn.dy, pn.z);
    console.log(`pin ${pn.text}(${pn.player}) anchor ${r.x.toFixed(0)},${r.y.toFixed(0)} dx ${r.dx.toFixed(0)} dy ${r.dy.toFixed(0)} box ${r.box.map((v) => v.toFixed(0)).join(',')} cover ${r.cover.toFixed(2)} on ${r.on}`);
  }
});
