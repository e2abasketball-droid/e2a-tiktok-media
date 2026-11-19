// Camera probe (Blind Pig V2): projects players / ball / rim through candidate orbit rigs at given play times, to choose a
// 9:16 framing before rendering. args: play.json t1,t2,.. '<json list of rigs>' ids (O1,X2,...,ball,rim)
import fs from 'node:fs';
import {camera3At} from '../src/t3d/camera3d.ts';
import {sample} from '../src/tactical/play.ts';
const [pf, ts, rigs, idsS] = process.argv.slice(2);
const play = JSON.parse(fs.readFileSync(pf, 'utf8'));
const W = 1080, H = 1920;
const sub = (p: number[], q: number[]) => [p[0] - q[0], p[1] - q[1], p[2] - q[2]];
const dot = (p: number[], q: number[]) => p[0] * q[0] + p[1] * q[1] + p[2] * q[2];
const cross = (p: number[], q: number[]) => [p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0]];
const nrm = (p: number[]) => { const l = Math.hypot(...p); return p.map((v) => v / l); };
for (const rig of JSON.parse(rigs)) for (const t of ts.split(',').map(Number)) {
  const cam = camera3At(play, [{at: 0, rig}], 0, t);
  const fw = nrm(sub(cam.target, cam.pos)); const rt = nrm(cross(fw, cam.up)); const up = cross(rt, fw);
  const th = Math.tan((cam.fov * Math.PI) / 360);
  const proj = (P: number[]) => { const d = sub(P, cam.pos); const z = dot(d, fw); return [Math.round(((dot(d, rt) / (z * th * (W / H))) + 1) / 2 * W), Math.round((1 - dot(d, up) / (z * th)) / 2 * H)]; };
  const fr = sample(play, t);
  const o = idsS.split(',').map((id) => { if (id === 'rim') return `rim ${proj([0, 1.575, 3.05])}`; if (id === 'ball') return `ball ${proj(fr.ball.pos)}`; const p = fr.players[id].pos; const a = proj([p[0], p[1], 0]); const b = proj([p[0], p[1], 2]); return `${id} ${a[0]},${a[1]}..${b[1]}`; });
  console.log(JSON.stringify([rig.dist, rig.pitch, rig.yaw]), 't' + t, o.join(' | '));
}
