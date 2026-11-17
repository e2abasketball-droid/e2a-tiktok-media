// E2A Tactical Studio — key moments of a Tactical3D episode, chosen from the episode itself (word anchors,
// screen graphics, play marks), for the contact sheet and the video QC (scripts/qc-video.py).
//   node --experimental-strip-types scripts/qc-moments.mts tactical/episodes/<id>.json [words.json] > moments.json
// Each moment: {t, label, shot, kind}. Kinds: shot (start of a shot), freeze, title, stamp, mark (a play mark
// such as screen1, catch, release, make reached on screen, i.e. through the shot's time remap).
import fs from 'node:fs';
import path from 'node:path';
import {localResolver, makeTacticalResolver, remapAt, resolveRemap} from '../src/tactical/edit.ts';

const epFile = process.argv[2];
const ep = JSON.parse(fs.readFileSync(epFile, 'utf8'));
const words = JSON.parse(fs.readFileSync(process.argv[3] ?? path.join(path.dirname(epFile), `${ep.id}.words.json`), 'utf8'));
const plays: Record<string, any> = {};
for (const [k, v] of Object.entries(ep.plays as Record<string, string | object>))
  plays[k] = typeof v === 'string'
    ? JSON.parse(fs.readFileSync([`tactical/plays/${v}.json`, path.join(path.dirname(epFile), `${v}.json`)].find((f) => fs.existsSync(f))!, 'utf8'))
    : v;
const fps = ep.fps ?? 30;
const T = makeTacticalResolver(words);
const total = words[words.length - 1].end + ep.tail;
const starts = ep.shots.map((s: any, i: number) => (i === 0 ? 0 : T(s.at)));
const out: {t: number; label: string; shot: string; kind: string; prio: number}[] = [];
ep.shots.forEach((shot: any, i: number) => {
  const start = starts[i];
  const end = i + 1 < starts.length ? starts[i + 1] : total;
  const toLocal = localResolver(T, start, end);
  const play = plays[shot.play];
  const rm = resolveRemap(shot.remap, play, toLocal);
  out.push({t: start + Math.min(0.2, (end - start) / 3), label: `${shot.id}: start`, shot: shot.id, kind: 'shot', prio: 2});
  for (const s of shot.screen ?? []) {
    if (!['freeze', 'title', 'stamp'].includes(s.type)) continue;
    const a = start + toLocal(s.from);
    const txt = s.type === 'freeze' ? 'FREEZE' : (s.lines ?? [s.text]).join(' ');
    out.push({t: Math.min(end - 0.05, a + (s.type === 'freeze' ? 0.35 : 0.3)), label: `${shot.id}: ${s.type} ${txt}`.slice(0, 48), shot: shot.id, kind: s.type, prio: s.type === 'freeze' ? 1 : 3});
  }
  // play marks as they appear on screen (first frame of the shot where the remapped play time reaches the mark)
  const seen = new Set<string>();
  for (let f = 0; f < Math.round((end - start) * fps); f++) {
    const pt = remapAt(rm, f / fps);
    for (const [m, v] of Object.entries(play.marks ?? {}) as [string, number][]) {
      if (m === 'start' || m === 'end' || seen.has(m)) continue;
      if (pt >= v - 1e-6 && (f === 0 ? false : remapAt(rm, (f - 1) / fps) < v - 1e-6)) {
        seen.add(m);
        out.push({t: start + f / fps, label: `${shot.id}: ${m}`, shot: shot.id, kind: 'mark', prio: 1});
      }
    }
  }
});
out.sort((a, b) => a.t - b.t);
console.log(JSON.stringify({episode: ep.id, total, fps, shots: ep.shots.map((s: any, i: number) => ({id: s.id, start: starts[i]})), moments: out}, null, 1));
