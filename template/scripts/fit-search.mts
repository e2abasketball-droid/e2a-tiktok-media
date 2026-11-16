// Camera fit search: smallest orbit distance that keeps the listed players (feet+head) and the ball inside the safe
// frame over a play window. Usage: node --experimental-strip-types scripts/fit-search.mts <play> <t0> <t1> <ids> [--fov 50 --top 260 --bottom 1280 --yaws ... --pitches ... --noball --rim]
// grid search for a static orbit that keeps ids (feet+head) and the ball inside the safe frame over a play window
import fs from 'node:fs';
import {toCam} from '../src/t3d/camera3d.ts';
import {sample} from '../src/tactical/play.ts';
const [playId, t0s, t1s, idsS, ...rest] = process.argv.slice(2);
const opt = (k: string, d: string) => (rest.includes(k) ? rest[rest.indexOf(k) + 1] : d);
const play = JSON.parse(fs.readFileSync(`tactical/plays/${playId}.json`, 'utf8'));
const ids = idsS.split(',');
const t0 = +t0s, t1 = +t1s;
const TOP = +opt('--top', '330'), BOT = +opt('--bottom', '1300'), SIDE = +opt('--side', '60');
const fov = +opt('--fov', '44');
const yaws = opt('--yaws', '-120,-110,-100,-90,-80,-70,-60,-50,-40,-30,-20,-10,0').split(',').map(Number);
const pitches = opt('--pitches', '30,38,46,54').split(',').map(Number);
const ball = !rest.includes('--noball');
const W = 1080, H = 1920;
const sub = (p: number[], q: number[]) => [p[0] - q[0], p[1] - q[1], p[2] - q[2]];
const dot = (p: number[], q: number[]) => p[0] * q[0] + p[1] * q[1] + p[2] * q[2];
const cross = (p: number[], q: number[]) => [p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0]];
const nrm = (p: number[]) => { const l = Math.hypot(...p); return p.map((v) => v / l); };
const frames: number[][][] = [];
for (let t = t0; t <= t1 + 1e-6; t += 0.1) {
  const fr = sample(play, t); const pts: number[][] = [];
  for (const id of ids) { const p = fr.players[id].pos; pts.push([p[0], p[1], 0], [p[0], p[1], 2.0]); }
  if (ball) pts.push(fr.ball.pos as number[]);
  if (rest.includes('--rim')) pts.push([0, 1.575, 3.05], [0, 1.2, 3.6]); // rim + backboard top: the reads keep the basket in frame
  frames.push(pts);
}
const all = frames.flat();
const cx = all.reduce((s, p) => s + p[0], 0) / all.length, cy = all.reduce((s, p) => s + p[1], 0) / all.length;
const res: any[] = [];
for (const yaw of yaws) for (const pitch of pitches) for (let dx = -5; dx <= 5; dx += 0.5) for (let dy = -5; dy <= 5; dy += 0.5) {
  for (let dist = 7; dist <= 22; dist += 0.25) {
    const cam = toCam({target: [cx + dx, cy + dy, 0.6], dist, pitch, yaw, fov});
    const fw = nrm(sub(cam.target, cam.pos)); const rt = nrm(cross(fw, cam.up)); const up = cross(rt, fw);
    const th = Math.tan((fov * Math.PI) / 360);
    let ok = true; let minM = 1e9; let y0 = 1e9, y1 = -1e9;
    for (const P of all) {
      const d = sub(P, cam.pos); const z = dot(d, fw);
      const x = ((dot(d, rt) / (z * th * (W / H))) + 1) / 2 * W; const y = (1 - dot(d, up) / (z * th)) / 2 * H;
      const m = Math.min(x - SIDE, W - SIDE - x, y - TOP, BOT - y);
      if (m < 0) { ok = false; break; } minM = Math.min(minM, m); y0 = Math.min(y0, y); y1 = Math.max(y1, y);
    }
    if (ok && Math.abs((y0 + y1) / 2 - (TOP + BOT) / 2) < +opt('--vc', '90')) { res.push({yaw, pitch, target: [+(cx + dx).toFixed(2), +(cy + dy).toFixed(2)], dist, minM: Math.round(minM), y: [Math.round(y0), Math.round(y1)]}); break; }
  }
}
res.sort((a, b) => a.dist - b.dist);
const best: Record<string, any> = {};
for (const r of res) { const k = `${r.yaw}/${r.pitch}`; if (!best[k]) best[k] = r; }
console.log(Object.values(best).sort((a: any, b: any) => a.dist - b.dist).slice(0, 14).map((r: any) => JSON.stringify(r)).join('\n'));
