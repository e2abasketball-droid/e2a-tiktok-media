// Frame-fit probe: projects every player (feet and head) and the ball through the real Tactical3D camera of each
// frame and reports who leaves the frame (or the platform-safe band). Used to compose a shot for the WHOLE path of
// the action before rendering a pixel.
// Run: node --experimental-strip-types scripts/frame-fit.mts <episode.json> <words.json> [--every N] [--ids O1,O3,...]
//   [--shots main,ss] [--top 220] [--bottom 1500] [--side 40]
// Prints one line per flagged frame: frame, shot, player:edge(px). Exit code 1 when anything is flagged.
import fs from 'node:fs';
import {camera3At} from '../src/t3d/camera3d.ts';
import {makeTacticalResolver, localResolver, resolveRemap, remapAt} from '../src/tactical/edit.ts';
import {sample} from '../src/tactical/play.ts';

const a = process.argv.slice(2);
const opt = (k: string, d: string) => (a.includes(k) ? a[a.indexOf(k) + 1] : d);
const ep = JSON.parse(fs.readFileSync(a[0], 'utf8'));
ep.words = JSON.parse(fs.readFileSync(a[1], 'utf8'));
ep.plays = Object.fromEntries(Object.entries(ep.plays).map(([k, v]) => [k, JSON.parse(fs.readFileSync(`tactical/plays/${v}.json`, 'utf8'))]));
const every = Number(opt('--every', '1'));
const idsOpt = opt('--ids', '');
const shotsOpt = opt('--shots', '');
const TOP = Number(opt('--top', '220'));
const BOT = Number(opt('--bottom', '1500'));
const SIDE = Number(opt('--side', '40'));
const W = 1080, H = 1920;
const T = makeTacticalResolver(ep.words);
const total = ep.words.at(-1).end + ep.tail;
const starts = ep.shots.map((s: any, i: number) => (i === 0 ? 0 : T(s.at)));
const sub = (p: number[], q: number[]) => [p[0] - q[0], p[1] - q[1], p[2] - q[2]];
const dot = (p: number[], q: number[]) => p[0] * q[0] + p[1] * q[1] + p[2] * q[2];
const cross = (p: number[], q: number[]) => [p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0]];
const nrm = (p: number[]) => { const l = Math.hypot(...p); return p.map((v) => v / l); };
let bad = 0;
const nF = Math.round(total * 30);
for (let f = 0; f < nF; f += every) {
  const t = f / 30;
  const i = starts.findLastIndex((s: number) => s <= t);
  const shot = ep.shots[i];
  if (shotsOpt && !shotsOpt.split(',').includes(shot.id)) continue;
  const start = starts[i]; const end = starts[i + 1] ?? total;
  const toLocal = localResolver(T, start, end);
  const play = ep.plays[shot.play];
  const lt = t - start; const pt = remapAt(resolveRemap(shot.remap, play, toLocal), lt);
  const cam = camera3At(play, shot.camera.map((k: any) => ({...k, at: toLocal(k.at)})), lt, pt);
  const fw = nrm(sub(cam.target, cam.pos));
  const rt = nrm(cross(fw, cam.up));
  const up = cross(rt, fw);
  const th = Math.tan((cam.fov * Math.PI) / 360);
  const proj = (P: number[]) => {
    const d = sub(P, cam.pos); const z = dot(d, fw);
    return [((dot(d, rt) / (z * th * (W / H))) + 1) / 2 * W, (1 - dot(d, up) / (z * th)) / 2 * H];
  };
  const fr = sample(play, pt);
  const ids = idsOpt ? idsOpt.split(',') : Object.keys(fr.players);
  const out: string[] = [];
  for (const id of ids) {
    const p = fr.players[id]?.pos; if (!p) continue;
    const pts = [proj([p[0], p[1], 0]), proj([p[0], p[1], 2.0])];
    const xs = pts.map((q) => q[0]); const ys = pts.map((q) => q[1]);
    const e: string[] = [];
    if (Math.min(...xs) < SIDE) e.push(`L${Math.round(Math.min(...xs))}`);
    if (Math.max(...xs) > W - SIDE) e.push(`R${Math.round(Math.max(...xs))}`);
    if (Math.min(...ys) < TOP) e.push(`T${Math.round(Math.min(...ys))}`);
    if (Math.max(...ys) > BOT) e.push(`B${Math.round(Math.max(...ys))}`);
    if (e.length) out.push(`${id}:${e.join('/')}`);
  }
  const b = proj(fr.ball.pos as number[]);
  if (b[0] < SIDE || b[0] > W - SIDE || b[1] < 60 || b[1] > BOT) out.push(`ball:${Math.round(b[0])},${Math.round(b[1])}`);
  if (out.length) { bad++; console.log(f, t.toFixed(2), shot.id, out.join(' ')); }
}
console.log(`flagged ${bad} frames`);
process.exit(bad ? 1 : 0);
