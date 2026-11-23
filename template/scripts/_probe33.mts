// diagnosis probe (not part of the QC): body-layer pelvis / root / lat trace of one player
import fs from 'node:fs';
import '../src/t3d/rig.ts';
import '../src/t3d/players/index.ts';
import {posAt} from '../src/tactical/play.ts';
import {PLAYER3D_V32} from '../src/t3d/realism-v3-2/index.ts';
import {motionV33} from '../src/t3d/realism-v3-3/motion33.ts';
const [f, id, a, z] = process.argv.slice(2);
const play = JSON.parse(fs.readFileSync(f, 'utf8'));
const rig = PLAYER3D_V32[play.players.find((p: any) => p.id === id)?.team === 'X' ? 'def' : 'off'].rig;
let prev: any = null;
for (let t = +a; t <= +z; t += 1 / 120) {
  const m = motionV33(play, id, t, rig)!;
  const r = posAt(play.tracks[id], t);
  const p = m.body.pelvis;
  const s = [p[0] - r[0], p[1] - r[1]];
  const h = m.body.h, Rx = Math.cos(h - Math.PI / 2), Ry = Math.sin(h - Math.PI / 2);
  const along = -(s[0] * Ry - s[1] * Rx);
  if (prev) console.log(t.toFixed(3), 'bodyPel v', ((p[0] - prev[0]) * 120).toFixed(2), ((p[1] - prev[1]) * 120).toFixed(2), ((p[2] - prev[2]) * 120).toFixed(2), 'z', p[2].toFixed(3), 'pel-root', s.map((v) => v.toFixed(3)).join(' '), 'bhead', m.body.head.map((v: number) => v.toFixed(3)).join(' '), 'look', JSON.stringify(m.look ?? null), 'h', m.body.h.toFixed(3), 'dotR', (s[0]*Rx+s[1]*Ry).toFixed(4), 'perp', along.toFixed(4), 'root', r.map((v: number) => v.toFixed(4)).join(' '), 'feet', m.body.feet.map((q: any) => q.support.toFixed(2) + '@' + q.g.slice(0, 2).map((v: number) => v.toFixed(2)).join(',')).join(' '));
  prev = p;
}
