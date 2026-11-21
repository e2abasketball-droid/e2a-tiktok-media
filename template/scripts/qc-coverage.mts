// CoverageQA — E2A Dynamic Defensive Coverage (src/t3d/coverage3d.tsx) on a play, WITHOUT rendering.
//   npx tsx scripts/qc-coverage.mts tactical/plays/<id>.json [--scheme 2-3] [--fps 30]
// Checks (FAIL above):
//   mapping     every area contains its own defender (area <-> defender correspondence, every frame)
//   overlap     no two areas overlap (Voronoi gap) -> no double / triple borders
//   court       every area vertex inside the court
//   continuity  area centroid moves ≤ its defender's step + 0.12 m per frame (no jumps; = no flicker / pop)
//   lead        moving: area centre ≤ 0.35 m in front of him along his run; still: the area moves ≤ 8 cm in 0.2 s unless a
//               neighbour (shared Voronoi boundary) or the ball moved
//   seek        same play time -> same polygon (pure function: playback = slow motion = seek)
import fs from 'node:fs';
import type {V2} from '../src/tactical/geometry.ts';
import {coverageState, COVERAGE_SCHEMES} from '../src/t3d/coverage3d.tsx';
import {posAt, sample} from '../src/tactical/play.ts';

const args = process.argv.slice(2);
const file = args[0];
const scheme = args.includes('--scheme') ? args[args.indexOf('--scheme') + 1] : '2-3';
const fps = Number(args[args.indexOf('--fps') + 1]) || 30;
const play = JSON.parse(fs.readFileSync(file, 'utf8'));
// --range t0:t1 limits the check to the play-time span the reel actually shows with coverage on screen
const rg = args.includes('--range') ? args[args.indexOf('--range') + 1].split(':').map(Number) : [0, play.duration];
const sc = COVERAGE_SCHEMES[scheme];
const inside = (p: V2, poly: V2[]) => {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const a = poly[i], b = poly[j];
    if ((a[1] > p[1]) !== (b[1] > p[1]) && p[0] < ((b[0] - a[0]) * (p[1] - a[1])) / (b[1] - a[1] || 1e-9) + a[0]) c = !c;
  }
  return c;
};
/** area-weighted centroid (a vertex average would jump when the clipping changes the vertex distribution) */
const cen = (p: V2[]): V2 => {
  let A = 0, cx = 0, cy = 0;
  for (let i = 0; i < p.length; i++) {
    const a = p[i], b = p[(i + 1) % p.length];
    const c = a[0] * b[1] - b[0] * a[1];
    A += c; cx += (a[0] + b[0]) * c; cy += (a[1] + b[1]) * c;
  }
  return Math.abs(A) < 1e-9 ? p[0] : [cx / (3 * A), cy / (3 * A)];
};
const st = (t: number) => coverageState(play, t, {scheme});
let explained = 0;
let worstMap = '', mapFails = 0, overlapFails = 0, worstOverlap = '', courtFails = 0, maxJump = 0, jumpAt = '', maxLead = -9, leadAt = '', seekFails = 0;
const N = Math.floor(play.duration * fps);
let prev: ReturnType<typeof st> | null = null;
for (let k = Math.ceil(rg[0] * fps); k <= Math.min(N, Math.floor(rg[1] * fps)); k++) {
  const t = k / fps;
  const s = st(t);
  for (const d of s) {
    if (d.poly.length < 3 || !inside(d.pos, d.poly)) { mapFails++; worstMap ||= `${d.id}@${t.toFixed(2)}`; }
    for (const q of d.poly) if (Math.abs(q[0]) > 7.5 || q[1] < 0 || q[1] > 14) { courtFails++; break; }
    for (const e of s) {
      if (e.id <= d.id) continue;
      if (e.poly.some((q) => inside(q, d.poly))) { overlapFails++; worstOverlap ||= `${d.id}/${e.id}@${t.toFixed(2)}`; }
    }
    if (prev) {
      const p = prev.find((x) => x.id === d.id)!;
      const a = cen(p.poly), b = cen(d.poly);
      const j = Math.hypot(b[0] - a[0], b[1] - a[1]) - Math.hypot(d.pos[0] - p.pos[0], d.pos[1] - p.pos[1]);
      if (j > maxJump) { maxJump = j; jumpAt = `${d.id}@${t.toFixed(2)}`; }
    }
  }
  if (k % 6 === 0 && t >= 0.2) {
    const s0 = st(t - 0.2);
    const raw = (id: string, tt: number) => posAt(play.tracks[id], Math.max(0, Math.min(play.duration, tt)));
    const ball = (tt: number) => sample(play, Math.max(0, tt)).ball.pos;
    const ballMove = Math.hypot(ball(t - 0.4)[0] - ball(t - 0.6)[0], ball(t - 0.4)[1] - ball(t - 0.6)[1]) + Math.hypot(ball(t)[0] - ball(t - 0.2)[0], ball(t)[1] - ball(t - 0.2)[1]);
    for (const d of s) {
      const d0 = s0.find((x) => x.id === d.id)!;
      const a = cen(d0.poly), b = cen(d.poly);
      const r1 = raw(d.id, t), r0 = raw(d.id, t - 0.2);
      const dv: V2 = [r1[0] - r0[0], r1[1] - r0[1]];
      const dl = Math.hypot(dv[0], dv[1]);
      if (dl > 0.03) {
        // moving: the area centre must not be out in front of him along his run (egg / ball offset allowance 0.35 m)
        const ahead = ((b[0] - r1[0]) * dv[0] + (b[1] - r1[1]) * dv[1]) / dl - 0.35;
        if (ahead > maxLead) { maxLead = ahead; leadAt = `${d.id}@${t.toFixed(2)} (moving)`; }
      } else {
        // standing still: the area may only change because a neighbour moved (shared boundary) or the ball moved
        const mv = Math.hypot(b[0] - a[0], b[1] - a[1]) - 0.08;
        const neighbour = s.some((e) => e.id !== d.id && Math.hypot(e.pos[0] - d.pos[0], e.pos[1] - d.pos[1]) < 4.5 &&
          Math.hypot(raw(e.id, t)[0] - raw(e.id, t - 0.2)[0], raw(e.id, t)[1] - raw(e.id, t - 0.2)[1]) > 0.1);
        if (mv > 0 && (neighbour || ballMove > 0.5)) explained++;
        else if (mv > maxLead) { maxLead = mv; leadAt = `${d.id}@${t.toFixed(2)} (still)`; }
      }
    }
    const again = st(t);
    if (JSON.stringify(again) !== JSON.stringify(s)) seekFails++;
  }
  prev = s;
}
const out = (ok: boolean, name: string, v: string) => console.log(`${ok ? 'PASS' : 'FAIL'}  [${play.id}] ${name} — ${v}`);
console.log(`coverage ${sc.name} — ${play.id}: play time ${rg[0]}-${rg[1]} s at ${fps} fps, ids ${sc.ids.join(' ')}`);
out(mapFails === 0, 'every area contains its own defender', mapFails ? `${mapFails} misses, first ${worstMap}` : 'all frames');
out(overlapFails === 0, 'no two areas overlap (no double borders)', overlapFails ? `${overlapFails}, first ${worstOverlap}` : '0');
out(courtFails === 0, 'every area inside the court', `${courtFails} area-frames out`);
out(maxJump <= 0.12, 'area centroid moves ≤ its defender\'s step + 0.12 m per frame (no pops)', `max excess ${maxJump.toFixed(3)} m (${jumpAt})`);
out(maxLead <= 0.0, 'area never runs out ahead of its defender, nor moves on its own while he stands still', `max ${maxLead.toFixed(3)} m over the allowance (${leadAt}); ${explained} still-defender changes explained by a moving neighbour / the ball`);
out(seekFails === 0, 'same play time -> same polygons (pure function)', `${seekFails} mismatches`);
