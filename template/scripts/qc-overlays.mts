// E2A Tactical3D — overlay budget QC (2026-11-19, Blind Pig brief: "max 3 tactical overlays on screen at the same
// time"). Counts, on every video frame, the TACTICAL overlays that are visible: every 3D telestration item (ov3) and the
// screen pins / HUD chips. Not counted (they are not tactical overlays): titles, stamps, subtitles, freeze corners,
// rewind tag, focus vignette, grade, punch / whip / flash, scrim and logo. An item is visible from its `from` anchor
// until its `to` anchor (the engine fades it in and out inside that window), so this is the strict count.
// Also refuses any screen-marker overlay or "SCREEN" text when the episode says `noScreens` (Blind Pig: no screens).
//   node --experimental-strip-types scripts/qc-overlays.mts tactical/episodes/<id>.json [--max 3] [--json out.json]
import fs from 'node:fs';
import path from 'node:path';
import {localResolver, makeTacticalResolver} from '../src/tactical/edit.ts';

const args = process.argv.slice(2);
const epPath = args[0];
const max = args.includes('--max') ? Number(args[args.indexOf('--max') + 1]) : 3;
const jsonOut = args.includes('--json') ? args[args.indexOf('--json') + 1] : undefined;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const ep: any = JSON.parse(fs.readFileSync(epPath, 'utf8'));
const words = JSON.parse(fs.readFileSync(epPath.replace(/\.json$/, '.words.json'), 'utf8'));
const T = makeTacticalResolver(words);
const fps = ep.fps ?? 30;
const total = words[words.length - 1].end + ep.tail;
const starts = ep.shots.map((s: {at: unknown}, i: number) => (i === 0 ? 0 : T(s.at as string)));
const SCREEN_TACTICAL = new Set(['pin', 'hud']);

let worst = 0;
let worstAt = '';
const over: {t: number; shot: string; n: number; items: string[]}[] = [];
const hist: Record<number, number> = {};
const nFrames = Math.floor(total * fps);
for (let f = 0; f < nFrames; f++) {
  const t = f / fps;
  let i = starts.length - 1;
  while (i > 0 && t < starts[i]) i--;
  const shot = ep.shots[i];
  const s0 = starts[i];
  const s1 = i + 1 < starts.length ? starts[i + 1] : total;
  const L = localResolver(T, s0, s1);
  const lt = t - s0;
  const live = (items: {type: string; from: unknown; to?: unknown}[] = []) =>
    items.filter((o) => {
      const a = L(o.from);
      const b = o.to !== undefined ? L(o.to) : s1 - s0;
      return lt >= a && lt < b;
    });
  const tac = [...live(shot.ov3).map((o: {type: string; player?: string}) => `${o.type}${o.player ? ':' + o.player : ''}`),
    ...live(shot.screen).filter((o: {type: string}) => SCREEN_TACTICAL.has(o.type)).map((o: {type: string; text?: string}) => `${o.type}:${o.text ?? ''}`)];
  hist[tac.length] = (hist[tac.length] ?? 0) + 1;
  if (tac.length > worst) [worst, worstAt] = [tac.length, `${shot.id}@${t.toFixed(2)}s (${tac.join(', ')})`];
  if (tac.length > max) over.push({t: +t.toFixed(3), shot: shot.id, n: tac.length, items: tac});
}
const screenWords = ep.noScreens
  ? ep.shots.flatMap((s: {id: string; ov3?: {type: string}[]; screen?: {type: string; text?: string; lines?: string[]; sub?: string}[]}) => [
      ...(s.ov3 ?? []).filter((o) => o.type === 'screen').map(() => `${s.id}: screen marker`),
      ...(s.screen ?? []).filter((o) => /SCREEN/i.test([o.text, ...(o.lines ?? []), o.sub].join(' '))).map((o) => `${s.id}: "${o.text ?? o.lines?.join(' / ')}"`)])
  : [];
const ok = over.length === 0;
console.log(`${ok ? 'PASS' : 'FAIL'}  tactical overlays on screen ≤ ${max} on every frame — max ${worst} at ${worstAt}; ${over.length} frames over`);
console.log(`INFO  frames by overlay count: ${Object.entries(hist).map(([k, v]) => `${k}:${v}`).join('  ')} (of ${nFrames})`);
if (ep.noScreens) console.log(`${screenWords.length ? 'FAIL' : 'PASS'}  no screen marker / no "SCREEN" label (action without screens) — ${screenWords.join('; ') || 'none'}`);
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify({episode: path.basename(epPath), max, worst, worstAt, framesOver: over, histogram: hist, screenLabels: screenWords}, null, 1));
process.exit(ok && !screenWords.length ? 0 : 1);
