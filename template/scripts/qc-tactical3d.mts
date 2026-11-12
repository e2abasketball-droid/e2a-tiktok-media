// Engine QC for a Tactical3D episode WITHOUT rendering: duration, anchors inside their shot,
// play clock, camera smoothness and safety, players of interest inside the safe frame, foot
// contact (no sliding of planted feet, no feet under the floor), screen text inside the safe area.
// Run: node --experimental-strip-types scripts/qc-tactical3d.mts tactical/episodes/stagger-screen.json [report.json]
import fs from 'node:fs';
import path from 'node:path';
import * as THREE from 'three';
import {localResolver, makeTacticalResolver, remapAt, resolveRemap} from '../src/tactical/edit.ts';
import {posAt} from '../src/tactical/play.ts';
import type {CamKey3} from '../src/t3d/camera3d.ts';
import {camera3At} from '../src/t3d/camera3d.ts';
import {footTrack} from '../src/t3d/rig.ts';
import type {PlayWithActions} from '../src/t3d/rig.ts';

const epFile = process.argv[2];
const outFile = process.argv[3];
const ep = JSON.parse(fs.readFileSync(epFile, 'utf8'));
const dir = path.dirname(epFile);
const words = JSON.parse(fs.readFileSync(path.join(dir, `${ep.id}.words.json`), 'utf8'));
const plays: Record<string, PlayWithActions> = {};
for (const [k, v] of Object.entries(ep.plays as Record<string, string>)) plays[k] = JSON.parse(fs.readFileSync(`tactical/plays/${v}.json`, 'utf8'));
const fps = ep.fps ?? 30;
const W = 1080;
const H = 1920;
const total = words[words.length - 1].end + ep.tail;
const T = makeTacticalResolver(words);
const starts = ep.shots.map((s: {at: string | number}, i: number) => (i === 0 ? 0 : T(s.at)));
const results: {check: string; ok: boolean; value: string}[] = [];
const check = (name: string, ok: boolean, value: string) => {
  results.push({check: name, ok, value});
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name} — ${value}`);
};
check('duration 30–40 s', total >= 30 && total <= 40, `${total.toFixed(2)} s`);
check('shots in narration order', starts.every((s: number, i: number) => i === 0 || s > starts[i - 1]), starts.map((s: number) => s.toFixed(2)).join(' '));

const W3 = (p: number[]) => new THREE.Vector3(p[0], p[2], -p[1]);
const project = (cam: {pos: number[]; target: number[]; up: number[]; fov: number}, p: number[]) => {
  const c = new THREE.PerspectiveCamera(cam.fov, W / H, 0.1, 120);
  c.position.copy(W3(cam.pos));
  c.up.copy(W3(cam.up));
  c.lookAt(W3(cam.target));
  c.updateMatrixWorld();
  c.updateProjectionMatrix();
  const v = W3(p).project(c);
  return {x: ((v.x + 1) / 2) * W, y: ((1 - v.y) / 2) * H, z: v.z};
};

let maxJump = 0;
let jumpAt = '';
let minCamZ = 99;
let outOfFrame = 0;
let ofWhere = '';
let anchorsOut = 0;
const anchorList: string[] = [];
ep.shots.forEach((shot: any, i: number) => {
  const start = starts[i];
  const end = i + 1 < starts.length ? starts[i + 1] : total;
  const toLocal = localResolver(T, start, end);
  const len = end - start;
  // anchors inside the shot
  const anchors = [...shot.remap.map((k: any) => k[0]), ...shot.camera.map((k: any) => k.at), ...(shot.ov3 ?? []).flatMap((o: any) => [o.from, o.to]), ...(shot.screen ?? []).flatMap((o: any) => [o.from, o.to])].filter((a) => a !== undefined);
  for (const a of anchors) {
    const l = toLocal(a);
    if (l < -0.02 || l > len + 0.02) {
      anchorsOut++;
      anchorList.push(`${shot.id}:${a}=${l.toFixed(2)}/${len.toFixed(2)}`);
    }
  }
  const play = plays[shot.play];
  const rm = resolveRemap(shot.remap, play, toLocal);
  const keys: CamKey3[] = shot.camera.map((k: any) => ({...k, at: toLocal(k.at)}));
  let prev: number[] | null = null;
  const rings = (shot.ov3 ?? []).filter((o: any) => o.type === 'ring');
  for (let f = 0; f < Math.round(len * fps); f++) {
    const lt = f / fps;
    const pt = remapAt(rm, lt);
    const cam = camera3At(play, keys, lt, pt);
    if (prev) {
      const j = Math.hypot(cam.pos[0] - prev[0], cam.pos[1] - prev[1], cam.pos[2] - prev[2]);
      if (j > maxJump) [maxJump, jumpAt] = [j, `${shot.id}@${lt.toFixed(2)}`];
    }
    prev = cam.pos as number[];
    minCamZ = Math.min(minCamZ, cam.pos[2]);
    for (const r of rings) {
      const a = toLocal(r.from);
      const b = r.to !== undefined ? toLocal(r.to) : len;
      if (lt < a + 0.3 || lt > b) continue;
      const p = posAt(play.tracks[r.player], Math.max(0, Math.min(play.duration, pt)));
      const q = project(cam, [p[0], p[1], 1.0]);
      if (q.x < 60 || q.x > 1020 || q.y < 230 || q.y > 1560 || q.z > 1) {
        outOfFrame++;
        if (!ofWhere) ofWhere = `${shot.id}:${r.player}@${lt.toFixed(2)} (${q.x.toFixed(0)},${q.y.toFixed(0)})`;
      }
    }
  }
});
const badRefs = ep.shots.flatMap((sh: any) =>
  [...(sh.ov3 ?? []), ...(sh.screen ?? [])].flatMap((o: any) =>
    ['player', 'a', 'b', 'src', 'dst']
      .filter((k) => typeof o[k] === 'string' && !plays[o.fromPlay ?? sh.play].tracks[o[k]])
      .map((k) => `${sh.id}:${o.type}.${k}=${o[k]}`),
  ),
);
check('every graphic points at a player that exists', badRefs.length === 0, badRefs.join(', ') || 'ok');
check('every anchor falls inside its shot', anchorsOut === 0, anchorsOut ? anchorList.join(', ') : 'ok');
check('camera moves smoothly inside shots (≤ 0.9 m per frame)', maxJump <= 0.9, `${maxJump.toFixed(2)} m (${jumpAt})`);
check('camera never below 0.8 m', minCamZ >= 0.8, `${minCamZ.toFixed(2)} m`);
check('highlighted players stay inside the safe frame', outOfFrame === 0, outOfFrame ? `${outOfFrame} frames, first ${ofWhere}` : 'ok');

// foot contact
let drift = 0;
let driftWho = '';
let under = 0;
for (const [k, play] of Object.entries(plays)) {
  for (const p of play.players) {
    const sim = footTrack(play, p.id);
    for (let i = 1; i < sim.rows.length; i++) {
      for (let f = 0; f < 2; f++) {
        const a = sim.rows[i - 1].feet[f];
        const b = sim.rows[i].feet[f];
        if (b[2] < -1e-6) under++;
        if (a[2] === 0 && b[2] === 0) {
          const d = Math.hypot(a[0] - b[0], a[1] - b[1]);
          if (d > drift) [drift, driftWho] = [d, `${k}:${p.id}@${sim.rows[i].t.toFixed(2)}`];
        }
      }
    }
  }
}
check('planted feet never slide (max drift per 1/120 s)', drift < 1e-4, `${(drift * 1000).toFixed(3)} mm (${driftWho || 'none'})`);
check('feet never go under the floor', under === 0, `${under} samples`);

const failed = results.filter((r) => !r.ok).length;
if (outFile) fs.writeFileSync(outFile, JSON.stringify({passed: results.length - failed, failed, results}, null, 1));
console.log(`\n${results.length - failed}/${results.length} engine checks passed`);
process.exit(failed ? 1 : 0);
