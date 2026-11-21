// CameraQA (2026-11-21, BLOB V2 cinematic): measures what the cinematic camera moves actually do, frame by frame,
// from the same camera3At() the renderer uses (seek = playback), so "orbit 200 deg" or "top-down 80 deg" is a
// measured number, not a claim.
//
//   node --experimental-strip-types scripts/qc-camera.mts tactical/episodes/<id>.json [--json out.json]
//        [--orbit <shotId>:<player>[:<minDeg>]] [--topdown <shotId>[:<minElev>[:<minHoldS>]]] [--max-turn 12]
//
// Per shot: azimuth sweep around the camera target (unwrapped, deg), elevation range (deg above the horizon),
// max turn speed (deg/frame of view direction), max position step (m/frame), horizon roll.
// Checks:
//   --orbit   the sweep of the named shot is >= minDeg (default 200) AND the player stays inside the frame
//             (x 60..1020, y 230..1560) on every frame of the sweep
//   --topdown the named shot reaches >= minElev (default 75) deg elevation and holds it >= minHoldS (default 2) s
//   always    horizon roll |roll| <= 1 deg on every frame; view turn <= --max-turn deg/frame inside shots
import fs from 'node:fs';
import path from 'node:path';
import * as THREE from 'three';
import {localResolver, makeTacticalResolver, remapAt, resolveRemap} from '../src/tactical/edit.ts';
import {posAt} from '../src/tactical/play.ts';
import type {CamKey3} from '../src/t3d/camera3d.ts';
import {camera3At} from '../src/t3d/camera3d.ts';

const args = process.argv.slice(2);
const opt = (k: string) => (args.includes(k) ? args[args.indexOf(k) + 1] : undefined);
const epFile = args[0];
const ep = JSON.parse(fs.readFileSync(epFile, 'utf8'));
const words = JSON.parse(fs.readFileSync(path.join(path.dirname(epFile), `${ep.id}.words.json`), 'utf8'));
const plays: Record<string, any> = {};
for (const [k, v] of Object.entries(ep.plays as Record<string, string>)) plays[k] = JSON.parse(fs.readFileSync(`tactical/plays/${v}.json`, 'utf8'));
const fps = ep.fps ?? 30;
const W = 1080, H = 1920;
const total = words[words.length - 1].end + ep.tail;
const T = makeTacticalResolver(words);
const starts: number[] = ep.shots.map((s: any, i: number) => (i === 0 ? 0 : T(s.at)));
const maxTurn = Number(opt('--max-turn') ?? 12);
const [orbShot, orbPlayer, orbMin] = (opt('--orbit') ?? '').split(':');
const [tdShot, tdElev, tdHold] = (opt('--topdown') ?? '').split(':');

const W3 = (p: number[]) => new THREE.Vector3(p[0], p[2], -p[1]);
const project = (cam: any, p: number[]) => {
  const c = new THREE.PerspectiveCamera(cam.fov, W / H, 0.1, 120);
  c.position.copy(W3(cam.pos));
  c.up.copy(W3(cam.up));
  c.lookAt(W3(cam.target));
  c.updateMatrixWorld();
  c.updateProjectionMatrix();
  const v = W3(p).project(c);
  return {x: ((v.x + 1) / 2) * W, y: ((1 - v.y) / 2) * H, z: v.z};
};
const deg = (r: number) => (r * 180) / Math.PI;

type Row = {id: string; start: number; end: number; sweep: number; elevMin: number; elevMax: number; maxTurn: number; maxStep: number; maxRoll: number; holdTop: number; subjectOut: number};
const rows: Row[] = [];
ep.shots.forEach((shot: any, i: number) => {
  const start = starts[i];
  const end = i + 1 < starts.length ? starts[i + 1] : total;
  const toLocal = localResolver(T, start, end);
  const play = plays[shot.play];
  const rm = resolveRemap(shot.remap, play, toLocal);
  const keys: CamKey3[] = shot.camera.map((k: any) => ({...k, at: toLocal(k.at)}));
  const minE = Number(tdElev || 75);
  let az0: number | null = null, azPrev = 0, unwrap = 0, azMin = 0, azMax = 0;
  let elevMin = 99, elevMax = -99, turn = 0, step = 0, roll = 0, hold = 0, holdBest = 0, out = 0;
  let prevDir: THREE.Vector3 | null = null, prevPos: number[] | null = null;
  const n = Math.round((end - start) * fps);
  for (let f = 0; f < n; f++) {
    const lt = f / fps;
    const pt = remapAt(rm, lt);
    const cam: any = camera3At(play, keys, lt, pt);
    const d = [cam.pos[0] - cam.target[0], cam.pos[1] - cam.target[1], cam.pos[2] - cam.target[2]];
    const horiz = Math.hypot(d[0], d[1]);
    const elev = deg(Math.atan2(d[2], horiz));
    elevMin = Math.min(elevMin, elev);
    elevMax = Math.max(elevMax, elev);
    if (elev >= minE) { hold += 1 / fps; holdBest = Math.max(holdBest, hold); } else hold = 0;
    const az = deg(Math.atan2(d[0], d[1]));
    if (az0 === null) { az0 = az; azPrev = az; }
    let da = az - azPrev;
    while (da > 180) da -= 360;
    while (da < -180) da += 360;
    if (horiz > 0.3) unwrap += da; // azimuth is meaningless straight overhead
    azPrev = az;
    azMin = Math.min(azMin, unwrap);
    azMax = Math.max(azMax, unwrap);
    roll = Math.max(roll, Math.abs(cam.roll ?? 0));
    const dir = W3(cam.target).sub(W3(cam.pos)).normalize();
    if (prevDir) turn = Math.max(turn, deg(prevDir.angleTo(dir)));
    if (prevPos) step = Math.max(step, Math.hypot(...cam.pos.map((v: number, k: number) => v - prevPos![k])));
    prevDir = dir;
    prevPos = cam.pos;
    if (shot.id === orbShot && orbPlayer) {
      const p = posAt(play.tracks[orbPlayer], Math.max(0, Math.min(play.duration, pt)));
      const q = project(cam, [p[0], p[1], 1.0]);
      if (q.x < 60 || q.x > 1020 || q.y < 230 || q.y > 1560 || q.z > 1) out++;
    }
  }
  rows.push({id: shot.id, start, end, sweep: azMax - azMin, elevMin, elevMax, maxTurn: turn, maxStep: step, maxRoll: roll, holdTop: holdBest, subjectOut: out});
});

const results: {check: string; ok: boolean; value: string}[] = [];
const check = (name: string, ok: boolean, value: string) => {
  results.push({check: name, ok, value});
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name} — ${value}`);
};
console.log('shot            start   end   sweep°  elev° min..max  turn°/f  step m/f  roll°  top-hold s');
for (const r of rows)
  console.log(`${r.id.padEnd(14)} ${r.start.toFixed(2).padStart(6)} ${r.end.toFixed(2).padStart(6)} ${r.sweep.toFixed(0).padStart(6)}  ${r.elevMin.toFixed(0).padStart(5)}..${r.elevMax.toFixed(0).padEnd(5)} ${r.maxTurn.toFixed(2).padStart(7)} ${r.maxStep.toFixed(2).padStart(8)} ${r.maxRoll.toFixed(1).padStart(6)} ${r.holdTop.toFixed(2).padStart(8)}`);
if (orbShot) {
  const r = rows.find((x) => x.id === orbShot)!;
  const min = Number(orbMin || 200);
  check(`orbit ${orbShot}: sweep >= ${min} deg around the subject`, r.sweep >= min, `${r.sweep.toFixed(1)} deg in ${(r.end - r.start).toFixed(2)} s`);
  check(`orbit ${orbShot}: ${orbPlayer} inside the safe frame on every frame`, r.subjectOut === 0, `${r.subjectOut} frames out`);
}
if (tdShot) {
  const r = rows.find((x) => x.id === tdShot)!;
  const hold = Number(tdHold || 2);
  check(`top-down ${tdShot}: elevation >= ${tdElev || 75} deg held >= ${hold} s`, r.elevMax >= Number(tdElev || 75) && r.holdTop >= hold, `max ${r.elevMax.toFixed(1)} deg, held ${r.holdTop.toFixed(2)} s`);
}
check('horizon level (|roll| <= 1 deg) on every frame', rows.every((r) => r.maxRoll <= 1), `max ${Math.max(...rows.map((r) => r.maxRoll)).toFixed(2)} deg`);
const worst = rows.reduce((a, b) => (b.maxTurn > a.maxTurn ? b : a));
check(`view turn <= ${maxTurn} deg/frame inside shots`, worst.maxTurn <= maxTurn, `${worst.maxTurn.toFixed(2)} deg/frame (${worst.id})`);
const out = opt('--json');
if (out) fs.writeFileSync(out, JSON.stringify({rows, results}, null, 1));
process.exitCode = results.every((r) => r.ok) ? 0 : 1;
