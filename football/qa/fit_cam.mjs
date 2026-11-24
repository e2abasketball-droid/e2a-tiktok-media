// E2A Football — camera FIT for a tactical key: the closest overview camera (smallest distance) whose frame keeps
// the given players (and points) inside a target rectangle for every sampled play time of the window. Uses the
// same camAt/projector as the video. Prints the best focus point + distance.
// Usage: node football/qa/fit_cam.mjs '<json>'
//   json = {t0, t1, ids: ['A4','A6'], pts: [[52.5,0]], azim: 0, elev: 68, fov: 40, rect: [x0,y0,x1,y1], margin: 30}
import {build} from '../remotion/node_modules/esbuild/lib/main.js';
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';

const here = path.dirname(url.fileURLToPath(import.meta.url));
const src = path.join(here, '../remotion/src');
const cfg = JSON.parse(process.argv[2]);
const entry = path.join(here, `.fit_entry_${process.pid}.ts`);
const tmp = path.join(here, `.fit_${process.pid}.mjs`);
fs.writeFileSync(entry, `export {camAt, projector} from ${JSON.stringify(path.join(src, 'camera.ts'))};\nexport {playerAt} from ${JSON.stringify(path.join(src, 'play.ts'))};\nimport p from ${JSON.stringify(path.join(here, '../tactical-library/plays/FB-PLAY-SP001-V07-off-ball-timing.json'))};\nexport const play = p;\n`);
await build({entryPoints: [entry], bundle: true, format: 'esm', platform: 'node', outfile: tmp, logLevel: 'error', nodePaths: [path.join(here, '../remotion/node_modules')]});
const M = await import(url.pathToFileURL(tmp).href);
fs.unlinkSync(tmp);
fs.unlinkSync(entry);
const {t0, t1, ids = [], pts = [], azim = 0, elev = 68, fov = 40, rect = [64, 230, 920, 1310], margin = 30, lift = 0} = cfg;
const times = [];
for (let t = t0; t <= t1 + 1e-6; t += Math.max(0.05, (t1 - t0) / 20)) times.push(t);
const P = [];
for (const t of times) {
  for (const id of ids) P.push([...M.playerAt(M.play, id, t).pos, 1.0], [...M.playerAt(M.play, id, t).pos, 0]);
  for (const p of pts) P.push([p[0], p[1], 0.2]);
}
const xs = P.map((p) => p[0]);
const ys = P.map((p) => p[1]);
const cx0 = (Math.min(...xs) + Math.max(...xs)) / 2;
const cy0 = (Math.min(...ys) + Math.max(...ys)) / 2;
const fits = (fx, fy, dist) => {
  const cam = M.camAt(M.play, [{at: 0, mode: 'overview', focus: [{p: [fx, fy]}], dist, elev, azim, fov, lift}], 0, t0);
  const pr = M.projector(cam, 1080, 1920);
  for (const p of P) {
    const q = pr(p);
    if (!q.visible || q.x < rect[0] + margin || q.x > rect[2] - margin || q.y < rect[1] + margin || q.y > rect[3] - margin) return false;
  }
  return true;
};
let best = null;
for (let dist = 18; dist <= 60 && !best; dist += 0.5)
  for (let dx = -8; dx <= 8 && !best; dx += 0.4)
    for (let dy = -8; dy <= 8 && !best; dy += 0.4) if (fits(cx0 + dx, cy0 + dy, dist)) best = {focus: [+(cx0 + dx).toFixed(1), +(cy0 + dy).toFixed(1)], dist};
console.log(JSON.stringify(best ?? 'no fit'));
