// E2A Football — motion QC on the REAL engine sampling (play.ts bundled with esbuild, no render needed).
// Checks the ball and the players exactly as the video draws them, frame by frame at 30 fps:
//   ball: no teleport (max frame-to-frame speed), never floats on ground passes, never moves before the kick,
//         contact at the kicker's foot at the kick, arrives at the receiver's foot, continuous at the first touch,
//         speed falls during every ground pass (rolling deceleration);
//   players: no instant turns (heading rate), gait phase advances with distance (no skating), and no
//         body interpenetration between players (centres >= 0.55 m).
// Usage: node football/qa/qc_play_motion.mjs <play.json> [out.json]
import {build} from '../remotion/node_modules/esbuild/lib/main.js';
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';

const here = path.dirname(url.fileURLToPath(import.meta.url));
const [playPath, outPath] = process.argv.slice(2);
const tmp = path.join(here, '.qc_play.mjs');
await build({entryPoints: [path.join(here, '../remotion/src/play.ts')], bundle: true, format: 'esm', platform: 'node', outfile: tmp, logLevel: 'error'});
const P = await import(url.pathToFileURL(tmp).href + `?v=${Date.now()}`);
fs.unlinkSync(tmp);
const play = JSON.parse(fs.readFileSync(playPath, 'utf8'));
const res = [];
const add = (check, ok, detail) => res.push({check, status: ok ? 'PASS' : 'FAIL', detail});
const fps = 30;
const N = Math.floor(play.duration * fps);
const ev = [...play.ball.events].sort((a, b) => a.t - b.t);
const hyp = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
const foot = (id, t, ahead = 0.4) => {
  const s = P.playerAt(play, id, t);
  return [s.pos[0] + Math.cos(s.heading) * ahead, s.pos[1] + Math.sin(s.heading) * ahead];
};

// ball: teleport / float
let vmax = 0;
let vAt = 0;
let zmax = 0;
for (let f = 1; f <= N; f++) {
  const a = P.ballAt(play, (f - 1) / fps).pos;
  const b = P.ballAt(play, f / fps).pos;
  const v = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]) * fps;
  if (v > vmax) {
    vmax = v;
    vAt = f / fps;
  }
  zmax = Math.max(zmax, b[2]);
}
add('ball: no teleport (max speed between frames <= 14 m/s on ground passes)', vmax <= 14, `max ${vmax.toFixed(2)} m/s at ${vAt.toFixed(2)} s`);
const groundOnly = ev.every((e) => !['shot', 'cross'].includes(e.type) && (e.height ?? 'ground') === 'ground');
if (groundOnly) add('ball: stays on the grass (no floating) for a ground-pass play', zmax <= P.BALL_R + 0.005, `max centre height ${zmax.toFixed(3)} m (radius ${P.BALL_R})`);

for (const e of ev) {
  if (e.type === 'rest') {
    const nxt = ev.find((x) => x.t > e.t);
    let moved = 0;
    for (let t = e.t; t < (nxt ? nxt.t : play.duration) - 1e-6; t += 1 / 120) moved = Math.max(moved, hyp(P.ballAt(play, t).pos, e.at));
    add(`ball: still at its spot until the kick (${e.at})`, moved < 0.005, `max drift ${moved.toFixed(4)} m`);
  }
  if (!['pass', 'through'].includes(e.type) || !e.t1) continue;
  const tag = `${e.by}->${e.to} ${e.t}s`;
  // contact at the kicker's foot when the kick happens
  const b0 = P.ballAt(play, e.t).pos;
  const kf = foot(e.by, e.t, 0.38);
  add(`kick ${tag}: ball at the kicking foot at contact (<= 0.25 m)`, hyp(b0, kf) <= 0.25, `${hyp(b0, kf).toFixed(3)} m`);
  // the ball does not leave before the kick
  const pre = P.ballAt(play, e.t - 0.1).pos;
  add(`kick ${tag}: ball not moving before the strike`, hyp(pre, b0) < 0.05 || P.ballAt(play, e.t - 0.1).holder === e.by, `moved ${hyp(pre, b0).toFixed(3)} m in the last 0.1 s`);
  // arrival at the receiver
  const b1 = P.ballAt(play, e.t1).pos;
  const rf = foot(e.to, e.t1, 0.4);
  add(`pass ${tag}: arrives at the receiver's foot (<= 0.2 m)`, hyp(b1, rf) <= 0.2, `${hyp(b1, rf).toFixed(3)} m`);
  // speed falls (rolling deceleration), no acceleration mid-way
  const sp = [];
  for (let t = e.t + 0.05; t < e.t1 - 0.05; t += 0.05) sp.push(hyp(P.ballAt(play, t + 0.025).pos, P.ballAt(play, t - 0.025).pos) / 0.05);
  const rises = sp.slice(1).filter((v, i) => v > sp[i] + 0.15).length;
  add(`pass ${tag}: speed only decreases while rolling`, rises === 0, `from ${sp[0].toFixed(1)} to ${sp[sp.length - 1].toFixed(1)} m/s, ${rises} rises`);
  // first touch: velocity continuity (no instant stop)
  if (e.decel !== undefined) {
    const vIn = hyp(P.ballAt(play, e.t1 - 1 / 60).pos, P.ballAt(play, e.t1 - 2 / 60).pos) * 60;
    const vOut = hyp(P.ballAt(play, e.t1 + 1 / 60).pos, P.ballAt(play, e.t1).pos) * 60;
    add(`first touch ${tag}: ball absorbed, not stopped dead (speed after/before >= 0.4)`, vOut / vIn >= 0.4, `in ${vIn.toFixed(2)} m/s, first frame after ${vOut.toFixed(2)} m/s`);
  }
}

// players
for (const p of play.players) {
  let turn = 0;
  let skate = 0;
  for (let f = 1; f <= N; f++) {
    const a = P.playerAt(play, p.id, (f - 1) / fps);
    const b = P.playerAt(play, p.id, f / fps);
    let d = b.heading - a.heading;
    while (d > Math.PI) d -= 2 * Math.PI;
    while (d < -Math.PI) d += 2 * Math.PI;
    turn = Math.max(turn, Math.abs(d) * fps);
    const dist = hyp(a.pos, b.pos);
    const v = dist * fps;
    if (v > 0.3) {
      const expected = (2 * Math.PI * dist) / P.strideLen(v);
      const got = b.phase - a.phase;
      skate = Math.max(skate, Math.abs(got - expected) / Math.max(1e-6, expected));
    }
  }
  add(`${p.id}: no instant turns (heading rate <= 9 rad/s)`, turn <= 9, `max ${turn.toFixed(2)} rad/s`);
  add(`${p.id}: gait phase follows the distance run (foot-sliding proxy, error <= 15 %)`, skate <= 0.15, `max relative error ${(skate * 100).toFixed(1)} %`);
}
let closest = 1e9;
let pair = '';
for (let f = 0; f <= N; f += 2) {
  const t = f / fps;
  for (let i = 0; i < play.players.length; i++)
    for (let j = i + 1; j < play.players.length; j++) {
      const d = hyp(P.playerAt(play, play.players[i].id, t).pos, P.playerAt(play, play.players[j].id, t).pos);
      if (d < closest) {
        closest = d;
        pair = `${play.players[i].id}-${play.players[j].id} at ${t.toFixed(2)} s`;
      }
    }
}
add('players: no body interpenetration (centres >= 0.55 m)', closest >= 0.55, `closest ${closest.toFixed(2)} m (${pair})`);

let bad = 0;
for (const r of res) {
  console.log(`${r.status.padEnd(5)} ${r.check}: ${r.detail}`);
  bad += r.status !== 'PASS';
}
console.log(`${res.length - bad}/${res.length} PASS`);
if (outPath) fs.writeFileSync(outPath, JSON.stringify({play: play.id, results: res}, null, 1));
process.exit(bad ? 1 : 0);
