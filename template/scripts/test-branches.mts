// E2A Tactical Studio — DEFENSIVE BRANCH contract (Chicago V3 brief sec. 4 / 13.3, 2026-11-22; generic for any pair).
// Two plays that are two READS of the same action declare `branch: {group, read, result, fork, offenceSharedUntil,
// payoff}`. This test proves the branches are the SAME setup and DIFFERENT outcomes, so a caption cannot hide the same
// action twice:
//   1. every player track and the ball are identical (≤ 3 mm) from 0 to `fork` (the shared frame of the choice);
//   2. every OFFENSIVE track (and the ball) stays identical until `offenceSharedUntil` (only the defence has read);
//   3. the declared result matches the ball events: drive_finish = a made LAYUP within 1.5 m of the rim;
//      three_point_shot = a made SHOT released with the shooter's feet behind the three-point line;
//   4. the two results differ and the shooter's end spots are ≥ 4 m apart (different end states).
//   node --experimental-strip-types scripts/test-branches.mts tactical/plays/a.json tactical/plays/b.json
import fs from 'node:fs';
import {distToBasket, isThree} from '../src/tactical/geometry.ts';
import {posAt, sample} from '../src/tactical/play.ts';
await import('../src/t3d/rig.ts');
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const plays: any[] = process.argv.slice(2).filter((f) => f.endsWith('.json')).map((f) => JSON.parse(fs.readFileSync(f, 'utf8')));
let failed = 0;
const check = (name: string, ok: boolean, value: string) => {
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name} — ${value}`);
};
check('two plays given, both with branch metadata in the same group', plays.length === 2 && plays.every((p) => p.branch) && plays[0].branch.group === plays[1].branch.group,
  plays.map((p) => `${p.id}:${p.branch?.group}`).join(' / '));
const [A, B] = plays;
const fork = Math.min(A.branch.fork, B.branch.fork);
const offShared = Math.min(A.branch.offenceSharedUntil, B.branch.offenceSharedUntil);
const ids: string[] = A.players.map((p: {id: string}) => p.id);
const team: Record<string, string> = Object.fromEntries(A.players.map((p: {id: string; team: string}) => [p.id, p.team]));
const diff = (t1: number, filter: (id: string) => boolean) => {
  let worst = 0, who = '', ball = 0, bwho = '';
  for (let t = 0; t <= t1 + 1e-9; t += 1 / 120) {
    for (const id of ids.filter(filter)) {
      const a = posAt(A.tracks[id], t), b = posAt(B.tracks[id], t);
      const d = Math.hypot(a[0] - b[0], a[1] - b[1]);
      if (d > worst) [worst, who] = [d, `${id}@${t.toFixed(3)}`];
    }
    const ba = sample(A, t).ball.pos, bb = sample(B, t).ball.pos;
    const d = Math.hypot(ba[0] - bb[0], ba[1] - bb[1], ba[2] - bb[2]);
    if (d > ball) [ball, bwho] = [d, `ball@${t.toFixed(3)}`];
  }
  return {worst, who, ball, bwho};
};
const s1 = diff(fork, () => true);
// tracks: ≤ 3 mm (posAt is a spline: the first key AFTER the hand-off bends the last 2 frames before it by ~2 mm). The DRAWN ball (rig hooks: hands, trunk solver) may differ by < 1.5 cm before the hand-off because the
// giver's heading filter looks ~0.6 s ahead along his own (branch-specific) track: invisible, but reported.
check(`all 10 players identical until the fork (${fork.toFixed(3)} s)`, s1.worst <= 0.003, `max ${(s1.worst * 100).toFixed(2)} cm ${s1.who}`);
check(`drawn ball identical until the fork (≤ 1.5 cm)`, s1.ball <= 0.015, `max ${(s1.ball * 100).toFixed(2)} cm ${s1.bwho}`);
const s2 = diff(offShared, (id) => team[id] === 'O');
check(`offence tracks identical until the hand-off (${offShared.toFixed(3)} s): only the defence has read`, s2.worst <= 0.003, `max ${(s2.worst * 100).toFixed(2)} cm ${s2.who}`);
check(`drawn ball identical until the hand-off (≤ 1.5 cm)`, s2.ball <= 0.015, `max ${(s2.ball * 100).toFixed(2)} cm ${s2.bwho}`);
// the defender who makes the read: `branch.reader` (HORNS 2026-11-23: X4), X2 by default (Chicago)
const reader: string = A.branch.reader ?? 'X2';
const x2fork = (p: typeof A) => {
  const a = posAt(p.tracks[reader] ?? p.tracks[ids.find((i) => team[i] === 'X')!], fork + 0.6);
  return a;
};
const xa = x2fork(A), xb = x2fork(B);
check(`the defence actually reads differently after the fork (${reader} ≥ 0.5 m apart at fork + 0.6 s)`, Math.hypot(xa[0] - xb[0], xa[1] - xb[1]) >= 0.5, `${Math.hypot(xa[0] - xb[0], xa[1] - xb[1]).toFixed(2)} m`);
const ends: Record<string, [number, number]> = {};
for (const p of plays) {
  const ev = p.ball.filter((e: {type: string}) => e.type === 'shot' || e.type === 'layup');
  const last = ev.at(-1);
  const who = last?.player;
  const at = who ? posAt(p.tracks[who], last.t0) : [0, 0];
  ends[p.id] = who ? posAt(p.tracks[who], p.duration) as [number, number] : [0, 0];
  if (p.branch.result === 'drive_finish') {
    check(`[${p.id}] ${p.branch.read} -> drive_finish: last ball event is a made LAYUP within 1.5 m of the rim`, last?.type === 'layup' && last.make !== false && distToBasket(at) <= 1.5,
      `${last?.type} make=${last?.make} at ${distToBasket(at).toFixed(2)} m`);
    const dribbles = p.ball.filter((e: {type: string; player?: string; dribble?: boolean; from?: number}) => e.type === 'hold' && e.player === who && e.dribble && e.from >= p.branch.offenceSharedUntil);
    check(`[${p.id}] the drive is a live dribble before the gather (no carry)`, dribbles.length >= 1, `${dribbles.length} dribble hold(s)`);
  } else if (p.branch.result === 'rim_finish') {
    // a CATCH-and-finish at the rim (roll man): made layup within 1.5 m, the finisher caught a pass after the fork
    check(`[${p.id}] ${p.branch.read} -> rim_finish: last ball event is a made LAYUP within 1.5 m of the rim`, last?.type === 'layup' && last.make !== false && distToBasket(at) <= 1.5,
      `${last?.type} make=${last?.make} at ${distToBasket(at).toFixed(2)} m`);
    const fed = p.ball.filter((e: {type: string; to?: string; t0?: number}) => e.type === 'pass' && e.to === who && (e.t0 ?? 0) >= p.branch.fork);
    check(`[${p.id}] the finisher catches a pass after the read (no carry)`, fed.length >= 1, `${fed.length} pass(es) to ${who}`);
  } else if (p.branch.result === 'three_point_shot') {
    check(`[${p.id}] ${p.branch.read} -> three_point_shot: last ball event is a made SHOT released behind the arc`, last?.type === 'shot' && last.make !== false && isThree(at as [number, number]),
      `${last?.type} make=${last?.make} at ${distToBasket(at).toFixed(2)} m from the basket`);
  } else check(`[${p.id}] known result`, false, String(p.branch.result));
  check(`[${p.id}] payoff metadata matches the ball event`, !!last && p.branch.payoff?.type === last.type && Math.abs(p.branch.payoff.t - last.t1) < 1e-3, JSON.stringify(p.branch.payoff));
}
check('the two branches have different results', A.branch.result !== B.branch.result, `${A.branch.result} vs ${B.branch.result}`);
const de = Math.hypot(ends[A.id][0] - ends[B.id][0], ends[A.id][1] - ends[B.id][1]);
check('different end states: the finishers end ≥ 4 m apart', de >= 4, `${de.toFixed(2)} m`);
console.log(failed ? `\n${failed} branch check(s) FAILED` : '\nall branch checks passed');
process.exit(failed ? 1 : 0);
