// E2A Realism V3 (2026-11-22) — numeric QA of the V3 athlete on a play (default: the one-take test fixture).
//   npx tsx scripts/qc-realism-v3.mts [play.json] [--player O1] [--json out.json]
// Per frame (30 fps) of the player while he HOLDS the ball (not in flight, not dribbling in the air):
//   fingertip / thumb / palm gap to the ball surface, legacy (e2a-player-v1 hand, open) vs V3 (grip solve)
// and over the whole play: corrective morph weights (min / max / frames active), head pitch fix, finger curl range.
import fs from 'node:fs';
import '../src/t3d/rig.ts';
import '../src/t3d/players/index.ts';
import {FIBA} from '../src/tactical/geometry.ts';
import type {V3} from '../src/tactical/geometry.ts';
import {sample} from '../src/tactical/play.ts';
import {poseAt} from '../src/t3d/rig.ts';
import type {PlayWithActions} from '../src/t3d/rig.ts';
import {meshScale} from '../src/t3d/skelclip.ts';
import {PLAYER3D_V3} from '../src/t3d/realism-v3/index.ts';
import {bonesV3, legacyTipGap, weightShift} from '../src/t3d/realism-v3/athleteV3.ts';
let weights: {f: number; drop: number; tilt: number; brake: number; lat: number}[] | undefined;

const args = process.argv.slice(2);
const opt = (k: string, d: string) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const file = args.find((a) => a.endsWith('.json') && args[args.indexOf(a) - 1] !== '--json') ?? 'tactical/plays/realism-v3-onetake.json';
const play = JSON.parse(fs.readFileSync(file, 'utf8')) as PlayWithActions;
const id = opt('--player', 'O1');
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const variant = play.players.find((p) => p.id === id)!.team === 'X' ? 'def' : 'off';
const rig = PLAYER3D_V3[variant].rig;
const N = Math.round(play.duration * 30);
const q = (xs: number[], p: number) => {
  const s = [...xs].sort((a, b) => a - b);
  return s.length ? s[Math.min(s.length - 1, Math.floor(p * (s.length - 1)))] : NaN;
};
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const morphs: Record<string, number[]> = {};
const held: {f: number; legacy: number; v3: number; thumbL: number; thumbV: number; palm: number; side: string}[] = [];
const curls: number[] = [];
for (let f = 0; f <= N; f++) {
  const t = f / 30;
  const b = sample(play, t).ball;
  const lag = sample(play, Math.max(0, t - 0.2)).ball.pos;
  const pose = poseAt(play, id, t, {holder: b.holder, pos: b.pos, lag}, RIM);
  const sc = meshScale(rig, pose);
  const ws = weightShift(play, id, t);
  const fr = bonesV3(rig, pose, sc, {pos: b.pos, held: b.holder === id}, ws);
  (weights ??= []).push({f, drop: ws.drop, tilt: Math.hypot(ws.tilt[0], ws.tilt[1]), brake: ws.brake, lat: ws.lat});
  for (const [k, v] of Object.entries(fr.morph)) (morphs[k] ??= []).push(v);
  const ev = b.event as {type?: string; dribble?: boolean} | undefined;
  if (b.holder === id && ev?.type === 'hold') {
    const lg = legacyTipGap(rig, pose, sc, b.pos);
    // the hand nearer the ball is the contact hand
    const gi = fr.grip.reduce((a, g) => (g.palmGap < a.palmGap ? g : a));
    const li = lg.find((x) => x.side === gi.side)!;
    if (gi.w > 0.5 && !ev.dribble) held.push({f, legacy: li.tipGap, v3: gi.tipGap, thumbL: li.thumbGap, thumbV: gi.thumbGap, palm: gi.palmGap, side: gi.side});
    curls.push(gi.curl);
  }
}
const col = (k: 'legacy' | 'v3' | 'thumbL' | 'thumbV' | 'palm') => held.map((h) => h[k] * 1000);
const out = {
  play: play.id, player: id, frames: N + 1, rig: rig.version,
  grip: {
    framesHeldTwoHand: held.length,
    tipGapMm: {legacy: {p50: r3(q(col('legacy'), 0.5)), p95: r3(q(col('legacy'), 0.95)), max: r3(Math.max(...col('legacy')))},
               v3: {p50: r3(q(col('v3'), 0.5)), p95: r3(q(col('v3'), 0.95)), max: r3(Math.max(...col('v3'))), min: r3(Math.min(...col('v3')))}},
    absTipGapMm: {legacy: {p50: r3(q(col('legacy').map(Math.abs), 0.5)), within10: held.filter((h) => Math.abs(h.legacy) <= 0.01).length},
                  v3: {p50: r3(q(col('v3').map(Math.abs), 0.5)), within10: held.filter((h) => Math.abs(h.v3) <= 0.01).length}},
    thumbGapMm: {legacy: r3(q(col('thumbL'), 0.5)), v3: r3(q(col('thumbV'), 0.5))},
    palmGapMm: {p50: r3(q(col('palm'), 0.5))},
    curlRad: {min: r3(Math.min(...curls)), max: r3(Math.max(...curls))},
  },
  weight: (() => {
    const W = weights ?? [];
    const top = (k: 'drop' | 'tilt') => W.reduce((m, x) => (x[k] > m[k] ? x : m), W[0]);
    const d = top('drop'), tl = top('tilt');
    return {maxDropCm: r3(d.drop * 100), atS: r3(d.f / 30), maxTiltDeg: r3((tl.tilt * 180) / Math.PI), tiltAtS: r3(tl.f / 30), framesDropOver2cm: W.filter((x) => x.drop > 0.02).length,
            at: Object.fromEntries([60, 85, 95, 99, 105, 115, 300, 322].map((f) => [f, {dropCm: r3(W[f].drop * 100), tiltDeg: r3((W[f].tilt * 180) / Math.PI), brake: r3(W[f].brake), lat: r3(W[f].lat)}]))};
  })(),
  morphs: Object.fromEntries(Object.entries(morphs).map(([k, v]) => [k, {max: r3(Math.max(...v)), min: r3(Math.min(...v)), framesOver0_25: v.filter((x) => x > 0.25).length}])),
  morphAt: Object.fromEntries([95, 140, 226, 262, 350].map((f) => [f, Object.fromEntries(Object.entries(morphs).map(([k, v]) => [k, r3(v[f])]))])),
};
console.log(JSON.stringify(out, null, 1));
if (args.includes('--json')) fs.writeFileSync(opt('--json', 'qc-realism-v3.json'), JSON.stringify(out, null, 1));
