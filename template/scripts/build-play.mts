// E2A Tactical Studio — play builder: a high-level spec (start spots + timed legs at a speed) → play JSON
// with timed waypoints for the Tactical3D engine. The daily routine writes SPECS, not raw waypoints, so a new
// play is mostly "who goes where, when, how fast", and the timing maths is always the same.
//
//   node --experimental-strip-types scripts/build-play.mts tactical/specs/<id>.spec.json [out.json]
//
// Spec:
// {
//   "id", "title", "duration", "players": [...PlayerSpec], "notes": [...],
//   "start": {"O1": [x, y], ...},                         // FIBA half court, metres (basket x=0, y=1.575)
//   "legs": {"O2": [
//      {"at": 0.4, "via": [[-5.6, 2.4], [-5.2, 4.7]], "speed": 4.5},   // run through points at ~speed (m/s)
//      {"at": "+0.2", "to": [-1.2, 9.0], "speed": 5.5},               // "+s" = after the previous leg ends
//      {"until": 6.0}                                                // stand still (optional: implied)
//   ]},
//   "ball": [...BallEvent], "screens": [...], "marks": {...}, "actions": {...}, "claims": [...]
// }
// Each leg starts and ends at rest (the engine's C2 spline eases in and out), so its PEAK speed is above the
// average; the builder scales the leg time so the peak stays at `speed` (×1.5 rule of thumb for cubic ease).
import fs from 'node:fs';

type V2 = [number, number];
type Leg = {at?: number | string; to?: V2; via?: V2[]; speed?: number; until?: number; dur?: number};
type Spec = {
  id: string;
  title: string;
  duration: number;
  players: {id: string; team: 'O' | 'X'; role: string; guards?: string}[];
  start: Record<string, V2>;
  legs?: Record<string, Leg[]>;
  [k: string]: unknown;
};

const EASE = 1.5; // peak / average speed of a rest-to-rest cubic run

export const buildTracks = (spec: Spec): Record<string, [number, number, number][]> => {
  const tracks: Record<string, [number, number, number][]> = {};
  for (const p of spec.players) {
    const s = spec.start[p.id];
    if (!s) throw new Error(`${spec.id}: no start spot for ${p.id}`);
    const wp: [number, number, number][] = [[0, s[0], s[1]]];
    let t = 0;
    let pos: V2 = [...s];
    for (const leg of spec.legs?.[p.id] ?? []) {
      if (leg.until !== undefined) {
        if (leg.until < t) throw new Error(`${spec.id}/${p.id}: until ${leg.until} < ${t}`);
        t = leg.until;
        wp.push([+t.toFixed(3), pos[0], pos[1]]);
        continue;
      }
      const start = typeof leg.at === 'string' ? t + Number(leg.at) : leg.at ?? t;
      if (start < t - 1e-9) throw new Error(`${spec.id}/${p.id}: leg at ${start} starts before the previous one ends (${t})`);
      if (start > t) wp.push([+start.toFixed(3), pos[0], pos[1]]); // stand still until the leg starts
      const pts: V2[] = [...(leg.via ?? []), ...(leg.to ? [leg.to] : [])];
      if (!pts.length) throw new Error(`${spec.id}/${p.id}: leg without points`);
      const seg = [pos, ...pts];
      const lens = seg.slice(1).map((q, i) => Math.hypot(q[0] - seg[i][0], q[1] - seg[i][1]));
      const total = lens.reduce((a, b) => a + b, 0);
      const dur = leg.dur ?? (total * EASE) / (leg.speed ?? 4);
      let acc = 0;
      pts.forEach((q, i) => {
        acc += lens[i];
        wp.push([+(start + (dur * acc) / total).toFixed(3), +q[0].toFixed(3), +q[1].toFixed(3)]);
      });
      t = start + dur;
      pos = pts[pts.length - 1];
    }
    if (t < spec.duration) wp.push([spec.duration, pos[0], pos[1]]);
    else if (t > spec.duration + 1e-9) throw new Error(`${spec.id}/${p.id}: moves until ${t.toFixed(2)} s, after the play ends (${spec.duration})`);
    tracks[p.id] = wp;
  }
  return tracks;
};

export const buildPlay = (spec: Spec) => {
  const {start: _s, legs: _l, ...rest} = spec;
  return {...rest, tracks: buildTracks(spec), ball: spec.ball ?? [], screens: spec.screens ?? [], marks: spec.marks ?? {}, actions: spec.actions ?? {}};
};

if (process.argv[1]?.endsWith('build-play.mts')) {
  const [inp, out] = process.argv.slice(2);
  const spec = JSON.parse(fs.readFileSync(inp, 'utf8')) as Spec;
  const play = buildPlay(spec);
  const dest = out ?? inp.replace(/specs\/(.+)\.spec\.json$/, 'plays/$1.json');
  fs.writeFileSync(dest, JSON.stringify(play, null, 1) + '\n');
  console.log(`wrote ${dest}`);
}
