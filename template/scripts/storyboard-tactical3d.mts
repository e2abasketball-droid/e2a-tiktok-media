// Prints the real timeline of a Tactical3D episode: shots, anchored screen items, overlays and SFX
// in video seconds. Run: node --experimental-strip-types scripts/storyboard-tactical3d.mts tactical/episodes/<id>.json
import fs from 'node:fs';
import path from 'node:path';
import {localResolver, makeTacticalResolver} from '../src/tactical/edit.ts';
const ep = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const words = JSON.parse(fs.readFileSync(path.join(path.dirname(process.argv[2]), `${ep.id}.words.json`), 'utf8'));
const T = makeTacticalResolver(words);
const total = words[words.length - 1].end + ep.tail;
const starts = ep.shots.map((s: any, i: number) => (i === 0 ? 0 : T(s.at)));
const out: any[] = [];
const sfx: any[] = [];
ep.shots.forEach((s: any, i: number) => {
  const a = starts[i];
  const b = i + 1 < starts.length ? starts[i + 1] : total;
  const L = localResolver(T, a, b);
  const said = words.filter((w: any) => w.start >= a - 0.01 && w.start < b).map((w: any) => w.text).join(' ');
  const items = [
    ...(s.screen ?? []).map((o: any) => `${o.type}${o.text ? ` "${o.text}"` : o.lines ? ` "${o.lines.join(' / ')}"` : o.label ? ` "${o.label}"` : ''} @${(a + L(o.from)).toFixed(2)}`),
    ...(s.ov3 ?? []).map((o: any) => `3D ${o.type}${o.player ? ` ${o.player}` : ''} @${(a + L(o.from)).toFixed(2)}`),
    ...(s.sfx ?? []).map((o: any) => `sfx ${o.name} @${(a + L(o.at)).toFixed(2)}`),
  ];
  for (const o of s.sfx ?? []) sfx.push({shot: s.id, t: +(a + L(o.at)).toFixed(3), name: o.name, volume: o.volume ?? 0.3});
  out.push({shot: s.id, name: s.name, play: s.play, start: +a.toFixed(2), end: +b.toFixed(2), dur: +(b - a).toFixed(2), cameras: s.camera.map((k: any) => k.rig.type + (k.rig.behind ? `:${k.rig.behind}` : '')).join(' → '), said, items});
});
console.log(JSON.stringify({total: +total.toFixed(2), fps: ep.fps ?? 30, voice: ep.voiceMix ?? ep.voice, music: ep.music ?? null, shots: out, sfx}, null, 1));
