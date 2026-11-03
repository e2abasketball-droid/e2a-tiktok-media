#!/usr/bin/env node
// Validates an episode JSON before rendering. Fails on anything that would produce a broken or
// misleading video; warns on editing choices that hurt retention.
// Usage: node scripts/validate-episode.mjs episodes/<id>.json
import fs from 'node:fs';

const file = process.argv[2];
const ep = JSON.parse(fs.readFileSync(file, 'utf8'));
const errors = [];
const warns = [];
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]/g, '');
const keys = ep.words.map((w) => norm(w.text));
const resolve = (a, off = 0) => {
  if (typeof a === 'number') return a + off;
  const [phrase, occ] = a.split('#');
  const want = occ ? parseInt(occ, 10) - 1 : 0;
  const p = phrase.split(/\s+/).map(norm).filter(Boolean);
  let seen = 0;
  for (let i = 0; i + p.length <= keys.length; i++) {
    if (p.every((w, k) => keys[i + k] === w)) {
      if (seen === want) return ep.words[i].start + off;
      seen++;
    }
  }
  errors.push(`anchor not found in narration: "${a}"`);
  return NaN;
};

for (const k of ['id', 'title', 'style', 'voice', 'words', 'scenes', 'sources']) if (!ep[k]) errors.push(`missing field: ${k}`);
if (!['record', 'player', 'tactical', 'comparison', 'curiosity'].includes(ep.style)) errors.push(`unknown style ${ep.style}`);
if (!ep.sources?.length) errors.push('sources[] is empty: every fact must be checked against a source');
if (ep.words.some((w, i) => i && w.start < ep.words[i - 1].start)) errors.push('word timings are not in order');

const vEnd = ep.words.at(-1).end;
const total = vEnd + 0.25 + (ep.outro?.seconds ?? 1.4);
if (['record', 'curiosity', 'player', 'comparison'].includes(ep.style) && (total < 20 || total > 26))
  warns.push(`duration ${total.toFixed(1)}s is outside the 20-25 s target for ${ep.style}`);
if (ep.words[0].start > 0.4) warns.push('narration starts late: the hook must be heard in the first 0.4 s');

const starts = ep.scenes.map((s, i) => (i === 0 ? 0 : resolve(s.at, s.offset ?? 0)));
starts.forEach((s, i) => {
  if (i && s <= starts[i - 1]) errors.push(`scene ${i} starts before scene ${i - 1}`);
});
ep.scenes.forEach((s, i) => {
  const end = i + 1 < starts.length ? starts[i + 1] : vEnd + 0.25;
  const d = end - starts[i];
  if (s.type !== 'court' && d > 6) warns.push(`scene ${i} (${s.type}) lasts ${d.toFixed(1)} s: split it or add beats/callouts`);
  if (s.camera === 'static' && s.type !== 'court' && d > 2.5) warns.push(`scene ${i} is static for ${d.toFixed(1)} s`);
  if (s.type === 'media') {
    const m = s.media;
    if (!m?.credit || !m?.license) errors.push(`scene ${i}: media needs credit and license`);
    if (!fs.existsSync(new URL(`../public/${m?.src}`, import.meta.url))) errors.push(`scene ${i}: media file missing public/${m?.src}`);
    if (/ai|generated|higgsfield/i.test(`${m?.credit} ${m?.license}`) && m?.kind !== 'recreation') errors.push(`scene ${i}: AI imagery must use kind "recreation" so it is labelled on screen`);
  }
  for (const a of [...(s.beats ?? []), ...(s.callouts ?? []).map((c) => c.at), ...(s.items ?? []).map((x) => x.at)]) resolve(a);
  if (s.second) resolve(s.second.at);
});
const types = ep.scenes.map((s) => s.type);
types.forEach((t, i) => {
  if (i >= 2 && t === types[i - 1] && t === types[i - 2]) warns.push(`three "${t}" scenes in a row (scenes ${i - 2}-${i}): vary the visuals`);
});
if (ep.scenes.length < Math.floor(vEnd / 4.5)) warns.push(`only ${ep.scenes.length} scenes for ${vEnd.toFixed(0)} s of narration: aim for a new visual every 2-4 s`);
if (!ep.scenes.some((s) => s.type === 'media')) warns.push('no real photo/footage scenes: add licensed media when it exists for this story');

warns.forEach((w) => console.warn('WARN  ' + w));
errors.forEach((e) => console.error('ERROR ' + e));
if (errors.length) process.exit(1);
console.log(`episode OK: ${ep.scenes.length} scenes, ${total.toFixed(1)} s`);
