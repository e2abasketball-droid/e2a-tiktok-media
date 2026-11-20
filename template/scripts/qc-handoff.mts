// QC for hand-off plays (2026-11-20, Pistol Fake Handoff, brief sec. 6 "Pruebas antes de marcar listo"):
//   1. no fingers inside someone else's ball: every player who neither holds the ball nor is inside his reach window
//      for a pass/hand-off to him (nor is the hand-off passer) keeps both fingertips outside the ball (>= BALL_R - 1 cm)
//   2. play.expect.owner {player, from, to}: ONE owner in the window (keep: O2 never loses the ball during the fake):
//      ballPhase owner / sample holder stays `player`, no pass starts in the window
//   3. play.expect.transfer {from, to, t0, t1}: exactly ONE hand-off from -> to in the window, both reachable: at some
//      common instant both players have a fingertip on the ball (<= 0.15 m from its centre) and their chests are <= 1.2 m
//      apart; the receiver owns it at the end
// Usage: node --experimental-strip-types scripts/qc-handoff.mts play.json [...]   (exit 1 on any FAIL)
import fs from 'node:fs';
import {ballPhase, sample} from '../src/tactical/play.ts';
import {BALL_R, poseAt} from '../src/t3d/rig.ts';
import {FIBA} from '../src/tactical/geometry.ts';

const RIM = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ] as [number, number, number];
const DT = 1 / 60;
let fails = 0;
const res = (ok: boolean, name: string, msg: string) => {
  if (!ok) fails++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name} — ${msg}`);
};
type Ev = {type: string; from?: string; to?: string; player?: string; t0?: number; t1?: number; style?: string};
for (const pf of process.argv.slice(2)) {
  const p = JSON.parse(fs.readFileSync(pf, 'utf8'));
  const ids: string[] = Object.keys(p.tracks);
  const ev: Ev[] = p.ball;
  const exempt = (id: string, t: number) =>
    ev.some((e) => e.type === 'pass' && e.to === id && t >= (e.t1 ?? 0) - 0.32 && t <= (e.t1 ?? 0) + 1e-6) ||
    ev.some((e) => e.type === 'pass' && e.style === 'handoff' && e.from === id && t >= (e.t0 ?? 0) - 0.02 && t <= (e.t1 ?? 0) + 0.2);
  // 1. fingers outside the ball
  let worst = {d: 9, who: '', t: 0};
  for (let t = 0; t <= p.duration + 1e-9; t += DT) {
    const b = sample(p, t).ball;
    if (b.pos[2] < 0.3) continue;   // dribble bottom / floor: the hand is not near
    for (const id of ids) {
      if (b.holder === id || exempt(id, t)) continue;
      const ps = poseAt(p, id, t, {holder: b.holder, pos: b.pos as [number, number, number]}, RIM);
      for (const h of ps.hand) {
        const d = Math.hypot(h[0] - b.pos[0], h[1] - b.pos[1], h[2] - b.pos[2]);
        if (d < worst.d) worst = {d, who: id, t};
      }
    }
  }
  res(worst.d >= BALL_R - 0.01, `[${p.id}] no fingers inside someone else's ball (non-holder fingertip >= ${(BALL_R - 0.01).toFixed(3)} m from the ball centre)`,
    `${worst.d.toFixed(3)} m (${worst.who}@${worst.t.toFixed(2)}s)`);
  const ex = p.expect ?? {};
  // 2. one owner
  if (ex.owner) {
    const {player, from, to} = ex.owner;
    let bad = '';
    for (let t = from; t <= to + 1e-9 && !bad; t += DT) {
      const ph = ballPhase(p, t); const h = sample(p, t).ball.holder;
      if ((ph.owner && ph.owner !== player) || (h && h !== player) || ph.phase === 'IN_FLIGHT' || ph.phase === 'RELEASED') bad = `${ph.phase} owner ${ph.owner ?? '-'} holder ${h ?? '-'} @${t.toFixed(2)}s`;
    }
    const passes = ev.filter((e) => e.type === 'pass' && (e.t0 ?? 0) >= from && (e.t0 ?? 0) <= to);
    if (!bad && passes.length) bad = `pass ${passes[0].from}->${passes[0].to} @${passes[0].t0}`;
    res(!bad, `[${p.id}] one owner ${player} from ${from.toFixed(2)} to ${to.toFixed(2)} s (no transfer during the fake)`, bad || `${player} throughout`);
  }
  // 3. single legal transfer, both reachable
  if (ex.transfer) {
    const {from, to, t0, t1} = ex.transfer;
    const hs = ev.filter((e) => e.type === 'pass' && (e.t0 ?? 0) >= t0 - 1e-6 && (e.t0 ?? 0) <= t1);
    const one = hs.length === 1 && hs[0].from === from && hs[0].to === to && hs[0].style === 'handoff';
    res(one, `[${p.id}] exactly one hand-off ${from} -> ${to} in ${t0.toFixed(2)}-${t1.toFixed(2)} s`, hs.map((e) => `${e.style} ${e.from}->${e.to}@${e.t0}`).join(', ') || 'none');
    let both = {t: -1, gap: 9};
    for (let t = t0; t <= t1 + 1e-9; t += DT) {
      const b = sample(p, t).ball;
      const tip = (id: string) => {
        const ps = poseAt(p, id, t, {holder: b.holder, pos: b.pos as [number, number, number]}, RIM);
        return {d: Math.min(...ps.hand.map((h) => Math.hypot(h[0] - b.pos[0], h[1] - b.pos[1], h[2] - b.pos[2]))), c: ps.chest};
      };
      const a = tip(from), r = tip(to);
      const gap = Math.hypot(a.c[0] - r.c[0], a.c[1] - r.c[1]);
      if (a.d <= 0.15 && r.d <= 0.15 && gap <= 1.2) { both = {t, gap}; break; }
    }
    res(both.t >= 0, `[${p.id}] both pairs of hands on the ball at one instant, chests <= 1.2 m apart`, both.t >= 0 ? `@${both.t.toFixed(2)}s, chests ${both.gap.toFixed(2)} m` : 'never');
    const endOwner = ballPhase(p, t1).owner;
    res(endOwner === to, `[${p.id}] ${to} owns the ball at ${t1.toFixed(2)} s`, `${endOwner ?? '-'}`);
  }
}
process.exit(fails ? 1 : 0);
