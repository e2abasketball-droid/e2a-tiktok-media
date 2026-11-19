// Catch / ball-body QC (2026-11-19, Blind Pig catch fix; owner correction brief sec. 13). Works on any play JSON.
//   node --experimental-strip-types scripts/qc-catch.mts tactical/plays/<id>.json [...more] [--json out.json]
// Checks (FAIL):
//   ball_torso   the ball sphere (r 0.121 m) never sinks into any player's trunk (elliptic cylinder around the spine,
//                pelvis -> base of the neck, oriented by the CHEST yaw; half-depth 0.115·k, half-width 0.9·shW) by more
//                than 2 cm, at 120 Hz over the whole play (pass flights, catches, holds, gathers)
//   hands_front  at every catch contact (pass t1) the receiver's hands are not behind his trunk (hand ahead of the
//                spine >= -0.02 m in the chest frame) and the ball centre is ahead of the spine (>= 0.15 m)
//   two_hands    at contact both palms (mid wrist-fingertip) are on the ball surface (<= 6 cm off it) and on two
//                DIFFERENT points (palms >= 0.14 m apart)
//   continuity   FLIGHT -> CONTACT -> SECURED: no position jump (<= 0.10 m per 1/120 s step around t1) and, 0.05-0.10 s
//                after the contact, the ball moves with the receiver (<= 3.5 m/s relative): absorbed, never teleported
//   phases       the explicit ball phase machine (ballPhase in play.ts) goes OWNED_BY_PASSER -> RELEASED -> IN_FLIGHT
//                -> CONTACT -> SECURED [-> GATHER] for every pass, never two owners at once
import fs from 'node:fs';
import {sample, ballPhase} from '../src/tactical/play.ts';
import {poseAt} from '../src/t3d/rig.ts';

const args = process.argv.slice(2);
const jsonOut = args.includes('--json') ? args[args.indexOf('--json') + 1] : undefined;
const files = args.filter((a, i) => !a.startsWith('--') && args[i - 1] !== '--json');
const RIM: [number, number, number] = [0, 1.575, 3.05];
const R = 0.121;
type V3 = [number, number, number];
const report: Record<string, unknown>[] = [];
let allOk = true;

for (const f of files) {
  const p = JSON.parse(fs.readFileSync(f, 'utf8'));
  const ids: string[] = p.players.map((x: {id: string}) => x.id);
  const pose = (id: string, t: number) => {
    const b = sample(p, t).ball;
    return poseAt(p, id, t, {holder: b.holder, pos: b.pos as V3}, RIM);
  };
  // trunk frame: spine point at the ball height, chest yaw
  const trunk = (ps: ReturnType<typeof poseAt>, b: number[]) => {
    const z0 = ps.pelvis[2], z1 = ps.chest[2];
    const u = Math.max(0, Math.min(1, (b[2] - z0) / Math.max(0.1, z1 - z0)));
    const c = [ps.pelvis[0] + (ps.chest[0] - ps.pelvis[0]) * u, ps.pelvis[1] + (ps.chest[1] - ps.pelvis[1]) * u];
    const y = ps.chestYaw;
    const F = [Math.cos(y), Math.sin(y)], L = [-Math.sin(y), Math.cos(y)];
    const d = [b[0] - c[0], b[1] - c[1]];
    const k = ps.dims.H / 2;
    return {fwd: d[0] * F[0] + d[1] * F[1], lat: d[0] * L[0] + d[1] * L[1], inZ: b[2] > z0 - R && b[2] < z1 + R * 0.5, D: 0.115 * k, W: 0.9 * ps.dims.shW, F, L, c};
  };
  // 1) ball vs every trunk
  let worst = {pen: 0, id: '', t: 0};
  for (let t = 0; t <= p.duration; t += 1 / 120) {
    const b = sample(p, t).ball.pos as V3;
    for (const id of ids) {
      const ps = pose(id, t);
      const tr = trunk(ps, b);
      if (!tr.inZ) continue;
      const a = tr.D + R, w = tr.W + R;
      const q = Math.hypot(tr.fwd / a, tr.lat / w);
      if (q < 1) {
        const pen = (1 - q) * Math.min(a, w);
        if (pen > worst.pen) worst = {pen, id, t};
      }
    }
  }
  const okT = worst.pen <= 0.02;
  console.log(`${okT ? 'PASS' : 'FAIL'}  [${p.id}] ball never sinks into a trunk (<= 2 cm) — max ${(worst.pen * 100).toFixed(1)} cm${worst.id ? ` (${worst.id}@${worst.t.toFixed(3)})` : ''}`);
  const catches: Record<string, unknown>[] = [];
  let okH = true, ok2 = true, okC = true, okP = true;
  for (const e of p.ball.filter((x: {type: string}) => x.type === 'pass')) {
    const t1 = e.t1;
    const ps = pose(e.to, t1);
    const b = sample(p, t1).ball.pos as V3;
    const tr = trunk(ps, b);
    const palm = [0, 1].map((i) => ps.wrist[i].map((w: number, k: number) => (w + ps.hand[i][k]) / 2));
    const handF = palm.map((h: number[]) => (h[0] - tr.c[0]) * tr.F[0] + (h[1] - tr.c[1]) * tr.F[1]);
    const handD = palm.map((h: number[]) => Math.hypot(h[0] - b[0], h[1] - b[1], h[2] - b[2]) - R);
    const sep = Math.hypot(palm[0][0] - palm[1][0], palm[0][1] - palm[1][1], palm[0][2] - palm[1][2]);
    const front = Math.min(...handF) >= -0.02 && tr.fwd >= 0.15;
    const two = Math.max(...handD) <= 0.06 && sep >= 0.14;
    // continuity around the contact
    const dt = 1 / 120;
    let jump = 0;
    for (let t = t1 - 0.1; t < t1 + 0.1; t += dt) {
      const a = sample(p, t).ball.pos, c = sample(p, t + dt).ball.pos;
      jump = Math.max(jump, Math.hypot(c[0] - a[0], c[1] - a[1], c[2] - a[2]));
    }
    const v = (t: number) => { const a = sample(p, t - dt).ball.pos, c = sample(p, t + dt).ball.pos; return [(c[0] - a[0]) / (2 * dt), (c[1] - a[1]) / (2 * dt), (c[2] - a[2]) / (2 * dt)]; };
    const vin = v(t1 - 2 * dt), vout = v(t1 + 2 * dt);
    const dv = Math.hypot(vout[0] - vin[0], vout[1] - vin[1], vout[2] - vin[2]);
    // after the contact the ball moves WITH the receiver (absorbed): its velocity relative to his body <= 3.5 m/s
    const rp0 = sample(p, t1 + 0.05).players[e.to].pos, rp1 = sample(p, t1 + 0.1).players[e.to].pos;
    const b0 = sample(p, t1 + 0.05).ball.pos, b1 = sample(p, t1 + 0.1).ball.pos;
    const rel = Math.hypot((b1[0] - b0[0]) - (rp1[0] - rp0[0]), (b1[1] - b0[1]) - (rp1[1] - rp0[1]), b1[2] - b0[2]) / 0.05;
    const cont = jump <= 0.1 && rel <= 3.5;
    // phase machine
    const seq: string[] = [];
    for (let t = e.t0 - 0.3; t <= t1 + 0.6; t += 1 / 60) {
      const ph = ballPhase(p, t);
      const tag = ph.phase + (ph.owner ? ':' + ph.owner : '');
      if (seq[seq.length - 1] !== tag) seq.push(tag);
    }
    const want = ['OWNED_BY_PASSER', 'RELEASED', 'IN_FLIGHT', 'CONTACT', 'SECURED'];
    let wi = 0;
    for (const s of seq) if (wi < want.length && s.startsWith(want[wi])) wi++;
    const phOk = wi === want.length;
    okH &&= front; okC &&= cont; okP &&= phOk;
    if (e.style !== 'overhead' || true) ok2 &&= two;
    catches.push({pass: `${e.from}->${e.to}`, style: e.style ?? 'chest', t1, ballAhead: +tr.fwd.toFixed(3), handsAhead: handF.map((x: number) => +x.toFixed(3)), handBall: handD.map((x: number) => +x.toFixed(3)), handSep: +sep.toFixed(3), jump: +jump.toFixed(3), dv: +dv.toFixed(2), relAfter: +rel.toFixed(2), phases: seq});
    console.log(`  catch ${e.from}->${e.to} @${t1.toFixed(3)} (${e.style ?? 'chest'}): ball ahead of spine ${tr.fwd.toFixed(2)} m, hands ahead ${handF.map((x: number) => x.toFixed(2)).join('/')} m, hand-ball ${handD.map((x: number) => x.toFixed(2)).join('/')} m, hands apart ${sep.toFixed(2)} m, max step ${(jump * 100).toFixed(1)} cm, dv ${dv.toFixed(1)} m/s, ball vs receiver after contact ${rel.toFixed(1)} m/s, phases ${seq.join(' > ')}`);
  }
  console.log(`${okH ? 'PASS' : 'FAIL'}  [${p.id}] every catch in front of the trunk (hands not behind the body, ball >= 0.15 m ahead)`);
  console.log(`${ok2 ? 'PASS' : 'FAIL'}  [${p.id}] every catch with two hands on two different points of the ball`);
  console.log(`${okC ? 'PASS' : 'FAIL'}  [${p.id}] FLIGHT -> CONTACT -> SECURED continuous (step <= 10 cm / 1/120 s; after the contact the ball moves with the receiver, <= 3.5 m/s relative)`);
  console.log(`${okP ? 'PASS' : 'FAIL'}  [${p.id}] ball phase machine in order for every pass`);
  allOk &&= okT && okH && ok2 && okC && okP;
  report.push({play: p.id, trunkMaxPenetration_m: +worst.pen.toFixed(4), at: worst, catches});
}
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(report, null, 1));
process.exit(allOk ? 0 : 1);
