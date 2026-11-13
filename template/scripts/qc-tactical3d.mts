// Engine QC for a Tactical3D episode WITHOUT rendering: duration, anchors inside their shot,
// play clock, camera smoothness and safety, players of interest inside the safe frame, foot
// contact (no sliding of planted feet, no feet under the floor), screen text inside the safe area.
// Scene clearance (2026-11-13): the camera must stay clear of the basket structure (board, frame, arm,
// stanchion, base, rim) and never sit behind the glass with the board in view (the Stagger V2 frame-96
// white bar and the haze before it). Rays from the camera to highlighted players that hit that geometry
// are reported as WARN (approximate occlusion: boxes, not meshes; players are not occluders).
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

const warnings: {check: string; value: string}[] = [];
const warn = (name: string, value: string) => {
  warnings.push({check: name, value});
  console.log(`WARN  ${name} — ${value}`);
};
// basket structure in court coordinates (x lateral, y from the baseline, z up), boxes [min, max];
// mirrors src/t3d/Court3D.tsx (glass + frame, support arm, stanchion, padded base, rim)
type Box = {id: string; min: number[]; max: number[]};
const STRUCT: Box[] = [
  {id: 'board', min: [-0.92, 1.18, 2.88], max: [0.92, 1.22, 3.97]},
  {id: 'arm', min: [-0.08, -0.3, 3.02], max: [0.08, 1.2, 3.18]},
  {id: 'stanchion', min: [-0.14, -0.44, 0], max: [0.14, -0.16, 3.2]},
  {id: 'base', min: [-0.71, -1.41, 0], max: [0.71, 0.01, 0.93]},
  {id: 'rim', min: [-0.25, 1.2, 3.0], max: [0.25, 1.82, 3.1]},
];
const CLEAR = 0.5; // m between the camera and any structure (near plane 0.1 m + lens margin)
const boxDist = (p: number[], b: Box) => Math.hypot(...[0, 1, 2].map((k) => Math.max(b.min[k] - p[k], 0, p[k] - b.max[k])));
const rayHit = (o: number[], q: number[], b: Box) => {
  let t0 = 0, t1 = 1;
  for (let k = 0; k < 3; k++) {
    const d = q[k] - o[k];
    if (Math.abs(d) < 1e-9) { if (o[k] < b.min[k] || o[k] > b.max[k]) return false; continue; }
    let a = (b.min[k] - o[k]) / d, c = (b.max[k] - o[k]) / d;
    if (a > c) [a, c] = [c, a];
    t0 = Math.max(t0, a); t1 = Math.min(t1, c);
    if (t0 > t1) return false;
  }
  return true;
};
const BOARD_Y = 1.2;

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

// fraction of a 9x16 grid of view rays that cross the glass rectangle (plane y = BOARD_Y)
const glassCover = (cam: {pos: number[]; target: number[]; up: number[]; fov: number}) => {
  const c = new THREE.PerspectiveCamera(cam.fov, W / H, 0.1, 120);
  c.position.copy(W3(cam.pos));
  c.up.copy(W3(cam.up));
  c.lookAt(W3(cam.target));
  c.updateMatrixWorld();
  c.updateProjectionMatrix();
  let hit = 0, n = 0;
  for (let i = 0; i < 9; i++)
    for (let j = 0; j < 16; j++) {
      n++;
      const v = new THREE.Vector3(-1 + (2 * (i + 0.5)) / 9, -1 + (2 * (j + 0.5)) / 16, 0.5).unproject(c);
      const d = [v.x - c.position.x, -(v.z - c.position.z), v.y - c.position.y]; // back to court coords
      if (d[1] <= 1e-6) continue;
      const t = (BOARD_Y - cam.pos[1]) / d[1];
      const x = cam.pos[0] + d[0] * t, z = cam.pos[2] + d[2] * t;
      if (t > 0 && Math.abs(x) <= 0.9 && z >= 2.9 && z <= 3.95) hit++;
    }
  return hit / n;
};

let maxJump = 0;
let jumpAt = '';
let minCamZ = 99;
const ofByShot: Record<string, number> = {};
let outOfFrame = 0;
let ofWhere = '';
let anchorsOut = 0;
let minClear = 99, clearWho = '', clearFrames = 0;
let glassFrames = 0, glassWho = '', glassWarn = 0, glassMax = 0, glassMaxWho = '';
let occl = 0, occlWho = '';
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
    const gt = (start + lt).toFixed(3);
    for (const b of STRUCT) {
      const d = boxDist(cam.pos as number[], b);
      if (d < minClear) [minClear, clearWho] = [d, `${shot.id}@${gt}s ${b.id}`];
      if (d < CLEAR) clearFrames++;
    }
    // behind the glass: share of the picture seen THROUGH the tinted glass (grid of view rays vs the board)
    if (cam.pos[1] < BOARD_Y) {
      const cover = glassCover(cam);
      if (cover > glassMax) [glassMax, glassMaxWho] = [cover, `${shot.id}@${gt}s`];
      if (cover > 0.1) { glassFrames++; if (!glassWho) glassWho = `${shot.id}@${gt}s (${(cover * 100).toFixed(0)} % of the picture through the glass)`; }
      else if (cover > 0.02) glassWarn++;
    }
    for (const r of rings) {
      const a = toLocal(r.from);
      const b = r.to !== undefined ? toLocal(r.to) : len;
      if (lt < a + 0.3 || lt > b) continue;
      const p = posAt(play.tracks[r.player], Math.max(0, Math.min(play.duration, pt)));
      const q = project(cam, [p[0], p[1], 1.0]);
      if (STRUCT.some((b) => rayHit(cam.pos as number[], [p[0], p[1], 1.2], b))) {
        occl++;
        if (!occlWho) occlWho = `${shot.id}:${r.player}@${(start + lt).toFixed(3)}s`;
      }
      if (q.x < 60 || q.x > 1020 || q.y < 230 || q.y > 1560 || q.z > 1) {
        outOfFrame++;
        ofByShot[`${shot.id}:${r.player}`] = (ofByShot[`${shot.id}:${r.player}`] ?? 0) + 1;
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
check(`camera stays ≥ ${CLEAR} m from the basket structure`, clearFrames === 0, `${clearFrames} frame-structure hits, min ${minClear.toFixed(2)} m (${clearWho})`);
check('camera never films through the backboard glass (> 10 % of the picture)', glassFrames === 0, glassFrames ? `${glassFrames} frames, first ${glassWho}` : `max ${(glassMax * 100).toFixed(0)} %${glassMaxWho ? ' (' + glassMaxWho + ')' : ''}`);
if (glassWarn) warn('part of the picture (2–10 %) seen through the backboard glass', `${glassWarn} frames`);
if (occl) warn('highlighted player hidden behind the basket structure (ray vs boxes, approximate)', `${occl} frames, first ${occlWho}`);
check('highlighted players stay inside the safe frame', outOfFrame === 0, outOfFrame ? `${outOfFrame} frames, first ${ofWhere}; by shot ${Object.entries(ofByShot).map(([k, v]) => `${k}=${v}`).join(' ')}` : 'ok');

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
if (outFile) fs.writeFileSync(outFile, JSON.stringify({passed: results.length - failed, failed, results, warnings}, null, 1));
console.log(`\n${results.length - failed}/${results.length} engine checks passed`);
process.exit(failed ? 1 : 0);
