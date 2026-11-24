// E2A Football — EDIT QC on the real episode data (no render needed): the episode .ts is bundled with esbuild
// and sampled at 30 fps with the SAME camera and play functions the video uses. Objective editing metrics only
// (seconds, counts, visibility of points in the frame) — no invented attention metrics.
//   continuity   'live' shots continue the play clock across cuts (no restart / rewind at a cut); a shot named
//                or kinded 'replay' may rewind
//   framing      seconds the main picture shows the box action vs only the corner while the ball is at the
//                corner (kick -> delivery); runner / decoy / reacting defenders visible during their runs
//   finish       shooter, ball and keeper in frame at the strike; ball in frame when it crosses the line
//   structure    shot durations, cuts, replay length, freeze length, static end (scrim/end card) length,
//                max simultaneous pitch graphics and labels
// Usage: node football/qa/qc_edit.mjs <episode.ts> <exportName> [out.json]
import {build} from '../remotion/node_modules/esbuild/lib/main.js';
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';

const here = path.dirname(url.fileURLToPath(import.meta.url));
const [epPath, name, outPath] = process.argv.slice(2);
const tmp = path.join(here, `.qc_edit_${process.pid}.mjs`);
const entry = path.join(here, `.qc_edit_entry_${process.pid}.ts`);
const src = path.join(here, '../remotion/src');
fs.writeFileSync(
  entry,
  `export {${name} as EP} from ${JSON.stringify(path.resolve(epPath))};\nexport {camAt, projector} from ${JSON.stringify(path.join(src, 'camera.ts'))};\nexport {playerAt, ballAt} from ${JSON.stringify(path.join(src, 'play.ts'))};\n`,
);
const stub = {
  name: 'stub',
  setup(b) {
    b.onResolve({filter: /^(remotion|@remotion\/fonts)$/}, (a) => ({path: a.path, namespace: 'stub'}));
    b.onLoad({filter: /.*/, namespace: 'stub'}, () => ({contents: 'export const staticFile=(x)=>x; export const loadFont=()=>{};', loader: 'js'}));
  },
};
await build({entryPoints: [entry], bundle: true, format: 'esm', platform: 'node', outfile: tmp, logLevel: 'error', plugins: [stub], nodePaths: [path.join(here, '../remotion/node_modules')], jsx: 'automatic'});
const M = await import(url.pathToFileURL(tmp).href + `?v=${Date.now()}`);
fs.unlinkSync(tmp);
fs.unlinkSync(entry);
const ep = M.EP;
const play = ep.play;
const fps = 30;
const W = 1080;
const H = 1920;
// V09: SAFE_BOTTOM env = top of the subtitle band (action must stay above it); DUR env = 'min-max' seconds
const SAFE = {top: 220, bottom: +(process.env.SAFE_BOTTOM ?? 1920 - 440), left: 64, right: 1080 - 160};
const [DMIN, DMAX] = (process.env.DUR ?? '23-29').split('-').map(Number);

const remapAt = (r, lt) => {
  if (lt <= r[0][0]) return r[0][1];
  for (let i = 0; i < r.length - 1; i++) {
    const [a, pa] = r[i];
    const [b, pb] = r[i + 1];
    if (lt <= b) return pa + ((pb - pa) * (lt - a)) / Math.max(1e-6, b - a);
  }
  return r[r.length - 1][1];
};
const T = play.tactics ?? {};
const evs = [...play.ball.events].sort((a, b) => a.t - b.t);
const KICK = T.kick ?? evs.find((e) => e.type === 'pass').t;
const CUT = T.delivery;
const STRIKE = T.strike;
const GOAL = evs.find((e) => e.type === 'shot').t1;
const runs = [
  {id: 'A4', t0: 4.05, t1: 6.3, what: 'decoy run'},
  {id: 'A9', t0: 4.85, t1: 7.1, what: 'second decoy run'},
  {id: 'A6', t0: 4.4, t1: STRIKE, what: 'late run'},
  {id: 'D7', t0: 4.3, t1: 6.3, what: 'marker follows the decoy'},
  {id: 'D5', t0: 5.6, t1: 6.6, what: 'central zone shifts'},
  {id: 'D9', t0: 6.6, t1: 7.5, what: 'edge defender reaction (turn + first steps of the chase; the finish camera C is not counted)'},
];

const N = Math.round(ep.duration * fps);
const frames = [];
for (let f = 0; f < N; f++) {
  const t = f / fps;
  let si = 0;
  while (si < ep.shots.length - 1 && t >= ep.shots[si + 1].from) si++;
  const shot = ep.shots[si];
  const lt = t - shot.from;
  const pt = remapAt(shot.remap, lt);
  const cam = M.camAt(play, shot.cam, lt, pt);
  const proj = M.projector(cam, W, H);
  const vis = (p, z = 1.0) => {
    const q = proj([p[0], p[1], z]);
    return q.visible && q.x >= SAFE.left && q.x <= SAFE.right && q.y >= SAFE.top && q.y <= SAFE.bottom;
  };
  const end = si + 1 < ep.shots.length ? ep.shots[si + 1].from : ep.duration;
  const live = (items = []) => items.filter((o) => lt >= o.from && lt < (o.to ?? end - shot.from));
  const close = shot.name === 'close';
  const replay = !close && (shot.kind === 'replay' || /replay|reveal/.test(shot.name));
  // V09: what the inset and the subtitles could hide (key players, the ball, the space)
  const pips = (shot.pip ?? []).filter((p) => lt >= p.from && lt < p.to);
  const inRect = (r, p, z = 1.0) => { const q = proj([p[0], p[1], z]); return q.visible && q.x >= r.x - 10 && q.x <= r.x + r.w + 10 && q.y >= r.y - 10 && q.y <= r.y + r.h + 10; };
  const keyPts = Object.fromEntries(['A4', 'A6', 'A7', 'A9', 'D7', 'D9'].map((id) => [id, M.playerAt(play, id, pt).pos]));
  const spaceOv = (shot.ov ?? []).find((o) => o.type === 'space');
  if (spaceOv) keyPts.SPACE = spaceOv.c;
  keyPts.BALL = M.ballAt(play, pt).pos.slice(0, 2);
  const hiddenByPip = pips.length ? Object.keys(keyPts).filter((k) => pips.some((r) => inRect(r, keyPts[k], k === 'SPACE' || k === 'BALL' ? 0.1 : 1.0))) : [];
  frames.push({
    t, si, name: shot.name, replay, close, pt, hiddenByPip, frozen: (shot.freeze ?? []).some(([a, b]) => lt >= a && lt < b),
    box: vis([41.5, 0]) && vis([48.5, -5.5]),
    corner: vis([52.5, -34]),
    ball: vis(M.ballAt(play, pt).pos.slice(0, 2), 0.11),
    p: Object.fromEntries(['A4', 'A6', 'A7', 'A9', 'D1', 'D5', 'D7', 'D9'].map((id) => [id, vis(M.playerAt(play, id, pt).pos)])),
    nov: live(shot.ov).length,
    nlab: live(shot.screen).filter((s) => ['chip', 'cue', 'pin', 'stamp'].includes(s.type)).length,
    static: live(shot.screen).some((s) => s.type === 'scrim' || s.type === 'end'),
    pip: (shot.pip ?? []).some((p) => lt >= p.from && lt < p.to),
    xy: process.env.DEBUG ? Object.fromEntries(['A6', 'A4', 'D9'].map((id) => { const q = proj([...M.playerAt(play, id, pt).pos, 1.0]); return [id, [Math.round(q.x), Math.round(q.y)]]; }).concat([['G', ((q) => [Math.round(q.x), Math.round(q.y)])(proj([52.5, 0, 0]))]])) : undefined,
  });
}
const sec = (fs_) => +(fs_.length / fps).toFixed(2);
const res = [];
const add = (check, status, detail) => res.push({check, status, detail});

// continuity
const jumps = [];
for (let i = 1; i < ep.shots.length; i++) {
  const a = frames.filter((x) => x.si === i - 1);
  const b = frames.filter((x) => x.si === i);
  if (!a.length || !b.length || b[0].replay || b[0].close) continue;
  const prev = [...frames.filter((x) => x.si < i && !x.replay)].pop();
  if (!prev) continue;
  const d = b[0].pt - prev.pt;
  if (d < -0.02 || d > 0.2) jumps.push(`${prev.name} -> ${b[0].name}: play ${prev.pt.toFixed(2)} -> ${b[0].pt.toFixed(2)} s`);
}
add('continuity: live shots continue the play clock across cuts (no restart / rewind)', jumps.length ? 'FAIL' : 'PASS', jumps.length ? jumps.join('; ') : 'all live cuts continuous');

// framing during the corner phase (first pass of the play, not the replay)
const corner = frames.filter((x) => !x.replay && x.pt >= KICK && x.pt < CUT);
const onBoxCorner = corner.filter((x) => x.box);
const cornerOnly = corner.filter((x) => !x.box && (x.corner || x.p.A7));
add('framing: box action in the main picture while the ball is at the corner (kick -> delivery)', onBoxCorner.length / Math.max(1, corner.length) >= 0.8 ? 'PASS' : 'FAIL',
  `${sec(onBoxCorner)} s of ${sec(corner)} s show the box; ${sec(cornerOnly)} s show only the corner area`);
for (const r of runs) {
  const fr = frames.filter((x) => !x.replay && x.pt >= r.t0 && x.pt <= r.t1);
  const v = fr.filter((x) => x.p[r.id]);
  add(`visible: ${r.id} ${r.what} (play ${r.t0}-${r.t1.toFixed(2)} s)`, v.length / Math.max(1, fr.length) >= 0.8 ? 'PASS' : 'FAIL', `${sec(v)} of ${sec(fr)} s in the safe frame`);
}
// finish
const at = (pt0) => frames.filter((x) => !x.replay && Math.abs(x.pt - pt0) < 0.04);
const fs1 = at(STRIKE);
const okS = fs1.some((x) => x.p.A6 && x.ball && x.p.D1);
add('finish: shooter, ball and keeper in frame at the strike', okS ? 'PASS' : 'FAIL', okS ? 'yes' : `frames at strike: ${fs1.map((x) => `${x.name} A6 ${x.p.A6} ball ${x.ball} D1 ${x.p.D1}`).join(' | ')}`);
const fg = at(GOAL);
add('finish: ball in frame when it crosses the line', fg.some((x) => x.ball) ? 'PASS' : 'FAIL', fg.map((x) => x.name).join(', ') || 'no frame at the goal time');

// structure
const shots = ep.shots.map((s, i) => ({name: s.name, from: s.from, dur: +(((ep.shots[i + 1]?.from ?? ep.duration) - s.from)).toFixed(2), kind: s.kind ?? (/replay/.test(s.name) ? 'replay' : 'live')}));
const rep = frames.filter((x) => x.replay);
const stat = frames.filter((x) => x.static);
const metrics = {
  duration: ep.duration,
  shots,
  cuts: ep.shots.length - 1,
  replay_s: sec(rep),
  freeze_s: sec(frames.filter((x) => x.frozen)),
  static_end_s: sec(stat),
  pip_s: sec(frames.filter((x) => x.pip)),
  corner_phase_s: sec(corner),
  corner_phase_box_s: sec(onBoxCorner),
  corner_phase_corner_only_s: sec(cornerOnly),
  max_pitch_graphics: Math.max(...frames.map((x) => x.nov)),
  max_labels: Math.max(...frames.map((x) => x.nlab)),
  run_visible_s: Object.fromEntries(runs.map((r) => [r.id, sec(frames.filter((x) => !x.replay && x.pt >= r.t0 && x.pt <= r.t1 && x.p[r.id]))])),
};
add('structure: replay <= 5 s', metrics.replay_s <= 5 ? 'PASS' : 'FAIL', `${metrics.replay_s} s`);
add('structure: static ending <= 1.2 s', metrics.static_end_s <= 1.2 ? 'PASS' : 'FAIL', `${metrics.static_end_s} s with scrim / end card`);
add(`structure: duration ${DMIN}-${DMAX} s`, ep.duration >= DMIN && ep.duration <= DMAX ? 'PASS' : 'FAIL', `${ep.duration} s`);
const hid = frames.filter((x) => x.hiddenByPip.length);
add('inset: the picture-in-picture hides no key player, the ball or the space', hid.length ? 'FAIL' : 'PASS', hid.length ? [...new Set(hid.flatMap((x) => x.hiddenByPip))].join(', ') + ` (${sec(hid)} s, first at ${hid[0].t.toFixed(2)} s)` : `${metrics.pip_s} s of inset checked`);
metrics.close_s = sec(frames.filter((x) => x.close));
add('structure: <= 3 labels at once', metrics.max_labels <= 3 ? 'PASS' : 'FAIL', `max ${metrics.max_labels}`);

if (process.env.DEBUG) for (const x of frames.filter((x, i) => i % 6 === 0)) console.log(x.t.toFixed(1), x.name, x.pt.toFixed(2), 'A6', x.p.A6, 'D9', x.p.D9, 'A4', x.p.A4, JSON.stringify(x.xy));
for (const r of res) console.log(`${r.status.padEnd(5)} [edit] ${r.check}: ${r.detail}`);
console.log('METRICS', JSON.stringify(metrics));
const bad = res.filter((r) => r.status === 'FAIL').length;
console.log(`${res.length - bad}/${res.length} edit checks PASS`);
if (outPath) fs.writeFileSync(outPath, JSON.stringify({results: res, metrics}, null, 1));
process.exit(bad ? 1 : 0);
