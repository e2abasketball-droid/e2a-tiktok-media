// E2A Motion Engine V4 (2026-11-28) — per-frame dump of the SOLVED skeleton of every player (same code path as the
// render: realism-v3-3/scene33.athleteV33) plus the tactical root, its velocity and the ball, for the motion validator
// tools/motion/motion_validate.py. Nothing here changes motion; it only measures it.
//   npx tsx scripts/motion-dump-v4.mts <play.json> <out.json> [hz=60]
import fs from 'node:fs';
import '../src/t3d/rig.ts';
import '../src/t3d/players/index.ts';
import type {V3} from '../src/tactical/geometry.ts';
import {posAt, sample} from '../src/tactical/play.ts';
import type {PlayWithActions} from '../src/t3d/rig.ts';
import {qconj, qmul, qrot} from '../src/t3d/skelclip.ts';
import {fkHeads, palmWorld} from '../src/t3d/realism-v3/athleteV3.ts';
import {PLAYER3D_V32} from '../src/t3d/realism-v3-2/index.ts';
import {athleteV33} from '../src/t3d/realism-v3-3/scene33.ts';
import {ballV33, ballOwner33, resetV33Caches} from '../src/t3d/realism-v3-3/motion33.ts';

const [file, outF, hzS] = process.argv.slice(2);
const play = JSON.parse(fs.readFileSync(file, 'utf8')) as PlayWithActions;
const HZ = Number(hzS ?? 60);
const N = Math.round(play.duration * HZ);
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a: V3, k: number): V3 => [a[0] * k, a[1] * k, a[2] * k];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const r4 = (v: V3) => v.map((x) => Math.round(x * 10000) / 10000);
const rigOf = (id: string) => PLAYER3D_V32[play.players.find((p) => p.id === id)?.team === 'X' ? 'def' : 'off'].rig;
resetV33Caches();
const ids = play.players.map((p) => p.id);
const players: Record<string, unknown> = {};
for (const id of ids) {
  const rig = rigOf(id);
  const by = new Map(rig.bones.map((x) => [x.name, x] as const));
  const R = rig.restJoints;
  const rows: unknown[] = [];
  let arm = 0, leg = 0;
  for (let f = 0; f <= N; f++) {
    const t = f / HZ;
    const b = sample(play, t).ball;
    const a = athleteV33(play, id, t, rig, {holder: b.holder, pos: b.pos, lag: sample(play, Math.max(0, t - 0.2)).ball.pos});
    const at = fkHeads(rig, a.fr.bones, a.fr.hips, a.sc);
    const pt = (bone: string, k: string): V3 => {
      const fb = by.get(bone)!;
      const D = qmul(a.fr.bones[bone], qconj(fb.R));
      return add(at(bone), qrot(D, mul(sub(R[k], fb.head), a.sc)));
    };
    arm = (len(sub(R.elbowL, R.shoulderL)) + len(sub(R.wristL, R.elbowL))) * a.sc;
    leg = (len(sub(R.kneeL, R.hipL)) + len(sub(R.ankleL, R.kneeL))) * a.sc;
    const j: Record<string, V3> = {pelvis: at('hips'), chest: at('chest'), neck: at('neck'), head: at('head')};
    for (const s of ['L', 'R']) {
      j[`sh${s}`] = at(`upperarm.${s}`); j[`el${s}`] = at(`forearm.${s}`); j[`wr${s}`] = at(`hand.${s}`);
      j[`hip${s}`] = at(`thigh.${s}`); j[`kn${s}`] = at(`shin.${s}`); j[`an${s}`] = at(`foot.${s}`);
      j[`heel${s}`] = pt(`foot.${s}`, `heel${s}`); j[`toe${s}`] = pt(`foot.${s}`, `ball${s}`);
      j[`palm${s}`] = palmWorld(rig, a.fr.bones, a.fr.hips, a.sc, s as 'L' | 'R');
    }
    const tr = play.tracks[id];
    const p0 = posAt(tr, Math.max(0, t - 0.5 / HZ)), p1 = posAt(tr, Math.min(play.duration, t + 0.5 / HZ));
    const root = posAt(tr, t);
    const J: Record<string, number[]> = {};
    for (const k of Object.keys(j)) J[k] = r4(j[k]);
    rows.push({t: Math.round(t * 10000) / 10000, root: [root[0], root[1]].map((x) => Math.round(x * 10000) / 10000),
      v: [(p1[0] - p0[0]) * HZ, (p1[1] - p0[1]) * HZ].map((x) => Math.round(x * 1000) / 1000),
      J, hy: a.pose.headYaw, cy: a.pose.chestYaw, hd: (a.pose as {heading?: number}).heading ?? null,
      feet: a.debug?.feet.map((q) => ({planted: q.planted, support: Math.round(q.support * 100) / 100})) ?? null,
      st: a.debug?.state ?? null, stage: a.debug?.stage ?? null, src: a.source});
  }
  players[id] = {arm, leg, team: play.players.find((p) => p.id === id)?.team, frames: rows};
}
const ball: unknown[] = [];
for (let f = 0; f <= N; f++) {
  const t = f / HZ;
  const s = sample(play, t).ball;
  ball.push({t: Math.round(t * 10000) / 10000, p: r4(ballV33(play, t)), holder: s.holder ?? null, inFlight: !!s.inFlight, owner: (ballOwner33 as unknown as (p: unknown, t: number) => unknown)(play, t) ?? null});
}
fs.writeFileSync(outF, JSON.stringify({play: play.id, hz: HZ, duration: play.duration, marks: (play as {marks?: unknown}).marks ?? {}, players, ball}));
console.log(`motion-dump-v4 ${play.id}: ${ids.length} players, ${N + 1} frames at ${HZ} Hz -> ${outF}`);
