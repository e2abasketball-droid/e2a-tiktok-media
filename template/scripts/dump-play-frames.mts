// E2A — dump what the engine DRAWS for a play (2026-11-27, Basketball IQ 02 validator): player centres, velocities,
// simulated body headings (rig.ts), heights, and the 3D ball, sampled at 1/fps s. The Python validator
// (tools/iq_play_validate.py) checks this dump, so it validates the render's own motion, not the authoring file.
//   node --experimental-strip-types scripts/dump-play-frames.mts tactical/plays/<id>.json out.json [fps=120]
import fs from 'node:fs';
import {sample} from '../src/tactical/play.ts';
import {bodyRowAt, PLAYER_HEIGHTS} from '../src/t3d/rig.ts';

const [inp, out, fpsArg] = process.argv.slice(2);
const play = JSON.parse(fs.readFileSync(inp, 'utf8'));
const fps = Number(fpsArg ?? 120);
const ids: string[] = play.players.map((p: {id: string}) => p.id);
const frames = [];
for (let i = 0; i <= Math.round(play.duration * fps); i++) {
  const t = i / fps;
  const f = sample(play, t);
  const P: Record<string, number[]> = {};
  for (const id of ids) {
    const s = f.players[id];
    const row = bodyRowAt(play, id, t) as {heading?: number};
    P[id] = [s.pos[0], s.pos[1], s.vel[0], s.vel[1], row?.heading ?? s.facing, s.facing];
  }
  frames.push({t: +t.toFixed(4), P, B: f.ball.pos, h: f.ball.holder ?? null, fl: f.ball.inFlight ?? null});
}
fs.writeFileSync(out, JSON.stringify({play: play.id, fps, heights: Object.fromEntries(ids.map((i) => [i, PLAYER_HEIGHTS[i]])), frames}));
console.log(`wrote ${out}: ${frames.length} frames`);
