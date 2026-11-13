// E2A Tactical Studio — GENERIC tactical validator for any play (the per-play suites test-tactical.mts and
// test-stagger.mts stay as regression tests for Elevator and Stagger).
//
//   node --experimental-strip-types scripts/test-play.mts tactical/plays/<id>.json [...] [--report out.json]
//
// 1. Generic physics and basketball checks every play must pass: 5 v 5, no teleports or jerks, no overlapping
//    bodies, in bounds, the ball always held / in flight, open passing lanes, believable pass speeds, a shooter
//    behind the arc and open, layups at the rim, screeners stationary while they screen (legal screens).
// 2. The play's own CLAIMS: what the narration says must be true on the court ("X2 is trapped at the release",
//    "the help comes late"). A claim without `says` is refused: every claim must be tied to the script.
import fs from 'node:fs';
import {FIBA, isThree, distToBasket} from '../src/tactical/geometry.ts';
import {posAt, sample} from '../src/tactical/play.ts';

type V2 = [number, number];
type Claim = {type: string; says: string; [k: string]: unknown};
const args = process.argv.slice(2);
const repIdx = args.indexOf('--report');
const reportPath = repIdx >= 0 ? args[repIdx + 1] : undefined;
const files = args.filter((f, i) => f.endsWith('.json') && (repIdx < 0 || i !== repIdx + 1));
const DT = 1 / 120;
const BODY = 0.25;
const d2 = (a: number[], b: number[]) => Math.hypot(a[0] - b[0], a[1] - b[1]);
let failed = 0;
const results: {play: string; check: string; ok: boolean; value: string}[] = [];
const check = (play: string, name: string, ok: boolean, value: string) => {
  results.push({play, check: name, ok, value});
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  [${play}] ${name} — ${value}`);
};

for (const f of files) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const p: any = JSON.parse(fs.readFileSync(f, 'utf8'));
  const O = p.players.filter((x: {team: string}) => x.team === 'O');
  const X = p.players.filter((x: {team: string}) => x.team === 'X');
  const ids: string[] = p.players.map((x: {id: string}) => x.id);
  const T = (v: unknown): number => (typeof v === 'number' ? v : p.marks?.[v as string]);
  check(p.id, '5 attackers and 5 defenders', O.length === 5 && X.length === 5, `${O.length} O / ${X.length} X`);
  check(p.id, 'every player has a track over the whole play', ids.every((i) => p.tracks[i] && p.tracks[i][0][0] === 0 && p.tracks[i].at(-1)[0] >= p.duration - 1e-9), 'tracks');
  check(p.id, 'every defender guards an existing attacker', X.every((x: {guards?: string}) => x.guards && ids.includes(x.guards)), X.map((x: {guards?: string}) => x.guards).join(','));

  let vmax = 0, vWho = '', amax = 0, aWho = '';
  for (const id of ids) {
    let prevV = [0, 0];
    for (let t = 0; t <= p.duration; t += DT) {
      const a = posAt(p.tracks[id], t);
      const b = posAt(p.tracks[id], t + DT);
      const v = [(b[0] - a[0]) / DT, (b[1] - a[1]) / DT];
      const s = Math.hypot(v[0], v[1]);
      if (s > vmax) [vmax, vWho] = [s, `${id}@${t.toFixed(2)}`];
      if (t > 0) {
        const acc = Math.hypot(v[0] - prevV[0], v[1] - prevV[1]) / DT;
        if (acc > amax) [amax, aWho] = [acc, `${id}@${t.toFixed(2)}`];
      }
      prevV = v;
    }
  }
  check(p.id, 'top speed ≤ 7.5 m/s (no teleports)', vmax <= 7.5, `${vmax.toFixed(2)} m/s (${vWho})`);
  check(p.id, 'acceleration ≤ 22 m/s² (no jerks)', amax <= 22, `${amax.toFixed(1)} m/s² (${aWho})`);

  let minGap = 99, gapWho = '';
  for (let t = 0; t <= p.duration; t += 1 / 60) {
    const fr = sample(p, t);
    for (let i = 0; i < ids.length; i++)
      for (let j = i + 1; j < ids.length; j++) {
        const g = d2(fr.players[ids[i]].pos, fr.players[ids[j]].pos);
        if (g < minGap) [minGap, gapWho] = [g, `${ids[i]}-${ids[j]}@${t.toFixed(2)}`];
      }
  }
  check(p.id, 'no two bodies overlap (≥ 0.5 m centre to centre)', minGap >= 2 * BODY - 1e-6, `${minGap.toFixed(2)} m (${gapWho})`);
  const oob = ids.filter((id) => p.tracks[id].some((w: number[]) => Math.abs(w[1]) > FIBA.halfW - 0.2 || w[2] < 0.2 || w[2] > FIBA.halfL));
  check(p.id, 'everyone stays in bounds', oob.length === 0, oob.join(',') || 'ok');

  let bmax = 0, lost = 0;
  let prevB = sample(p, 0).ball.pos;
  for (let t = DT; t <= p.duration; t += DT) {
    const b = sample(p, t).ball;
    bmax = Math.max(bmax, Math.hypot(b.pos[0] - prevB[0], b.pos[1] - prevB[1]) / DT);
    if (!b.holder && !b.inFlight && !b.event) lost++;
    prevB = b.pos;
  }
  check(p.id, 'ball horizontal speed ≤ 15 m/s and continuous', bmax <= 15, `${bmax.toFixed(1)} m/s`);
  check(p.id, 'ball always held, in flight or dropping after a make', lost === 0, `${lost} orphan samples`);

  for (const e of p.ball) {
    if (e.type === 'pass') {
      let near = 99, who = '';
      for (let t = e.t0 + 0.04; t <= e.t1 - 0.04; t += DT) {
        const fr = sample(p, t);
        if (fr.ball.pos[2] > 2.4) continue;
        for (const x of X) {
          const g = d2(fr.ball.pos, fr.players[x.id].pos);
          if (g < near) [near, who] = [g, `${x.id}@${t.toFixed(2)}`];
        }
      }
      check(p.id, `pass ${e.from}→${e.to}: lane open (ball ≥ 0.6 m from every defender)`, near >= 0.6, `${near.toFixed(2)} m (${who})`);
      const len = d2(posAt(p.tracks[e.from], e.t0), posAt(p.tracks[e.to], e.t1));
      const sp = len / (e.t1 - e.t0);
      check(p.id, `pass ${e.from}→${e.to}: speed 6–14 m/s`, sp >= 6 && sp <= 14, `${sp.toFixed(1)} m/s over ${len.toFixed(1)} m`);
      const rv = Math.hypot(...(sample(p, e.t1).players[e.to].vel as [number, number]));
      check(p.id, `pass ${e.from}→${e.to}: receiver under control at the catch (≤ 3.5 m/s)`, rv <= 3.5, `${rv.toFixed(2)} m/s`);
    }
    if (e.type === 'shot' || e.type === 'layup') {
      const fr = sample(p, e.t0);
      const at = fr.players[e.player].pos;
      const near = Math.min(...X.map((x: {id: string}) => d2(at, fr.players[x.id].pos)));
      if (e.type === 'shot' && e.three !== false) {
        check(p.id, `${e.player} shoots from behind the FIBA 3-pt line`, isThree(at), `${distToBasket(at).toFixed(2)} m from the basket`);
        check(p.id, `shot flight 0.9–1.3 s`, e.t1 - e.t0 >= 0.9 && e.t1 - e.t0 <= 1.3, `${(e.t1 - e.t0).toFixed(2)} s`);
      }
      if (e.type === 'layup') check(p.id, `${e.player} lays up within 1.5 m of the rim`, distToBasket(at) <= 1.5, `${distToBasket(at).toFixed(2)} m`);
      // a jump shot needs a real closeout gap; at the rim, late help may arrive but not be in contact
      const need = e.type === 'shot' ? 1.8 : 1.0;
      if (e.contested !== true) check(p.id, `${e.player} is open (nearest defender ≥ ${need} m)`, near >= need, `${near.toFixed(2)} m`);
    }
  }

  // legal screens: a screener is stationary while the screen is live (moving screen = foul)
  for (const [id, acts] of Object.entries(p.actions ?? {}) as [string, {type: string; from: number; to: number}[]][]) {
    for (const a of acts.filter((x) => x.type === 'screen')) {
      let vs = 0;
      for (let t = a.from + 0.1; t <= a.to - 0.05; t += DT) vs = Math.max(vs, d2(posAt(p.tracks[id], t), posAt(p.tracks[id], t + DT)) / DT);
      check(p.id, `${id} screen ${a.from}–${a.to}s is legal (stationary ≤ 0.15 m/s)`, vs <= 0.15, `${vs.toFixed(3)} m/s`);
    }
  }

  // claims tied to the narration
  for (const c of (p.claims ?? []) as Claim[]) {
    if (!c.says) {
      check(p.id, `claim ${c.type} has a narration line`, false, 'missing "says"');
      continue;
    }
    const lbl = `claim "${c.says}"`;
    const at = T(c.at);
    const fr = at !== undefined ? sample(p, at) : undefined;
    const pos = (id: string) => fr!.players[id].pos as V2;
    switch (c.type) {
      case 'open': {
        const near = Math.min(...X.map((x: {id: string}) => d2(pos(c.player as string), pos(x.id))));
        check(p.id, lbl, near >= (c.min as number), `nearest defender ${near.toFixed(2)} m (≥ ${c.min})`);
        break;
      }
      case 'far': {
        const g = d2(pos(c.a as string), pos(c.b as string));
        check(p.id, lbl, g >= (c.min as number), `${c.a}–${c.b} ${g.toFixed(2)} m (≥ ${c.min})`);
        break;
      }
      case 'near': {
        const g = d2(pos(c.a as string), pos(c.b as string));
        check(p.id, lbl, g <= (c.max as number), `${c.a}–${c.b} ${g.toFixed(2)} m (≤ ${c.max})`);
        break;
      }
      case 'behind_arc':
        check(p.id, lbl, isThree(pos(c.player as string)), `${distToBasket(pos(c.player as string)).toFixed(2)} m`);
        break;
      case 'near_rim': {
        const dd = distToBasket(pos(c.player as string));
        check(p.id, lbl, dd <= (c.max as number), `${dd.toFixed(2)} m (≤ ${c.max})`);
        break;
      }
      case 'reacts_after': {
        const wp = p.tracks[c.player as string];
        const t0 = T(c.event);
        const p0 = posAt(wp, t0);
        let moved = p.duration;
        for (let t = t0 - 1; t <= p.duration; t += DT) if (t >= 0 && d2(posAt(wp, t), p0) > 0.05) { moved = t; break; }
        check(p.id, lbl, moved - t0 >= (c.min as number), `moves ${(moved - t0).toFixed(2)} s after ${c.event} (≥ ${c.min})`);
        break;
      }
      case 'order': {
        const ts = (c.marks as string[]).map(T);
        check(p.id, lbl, ts.every((v, i) => v !== undefined && (i === 0 || v > ts[i - 1])), ts.join(' < '));
        break;
      }
      default:
        check(p.id, lbl, false, `unknown claim type ${c.type}`);
    }
  }
}

if (reportPath) fs.writeFileSync(reportPath, JSON.stringify({passed: results.filter((r) => r.ok).length, failed, results}, null, 1));
console.log(`\n${results.length - failed}/${results.length} generic tactical checks passed`);
process.exit(failed ? 1 : 0);
