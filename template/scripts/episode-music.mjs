#!/usr/bin/env node
// Build the music bed for a Pro episode with the E2A music engine (../music/e2a_music.py) and write
// the render props with episode.music = {src, premixed: true}. Called by render-pro.sh.
// The drops land on scene cuts: the cut nearest 30% of the narration (reveal) and nearest 75% (payoff),
// unless the episode sets music.dropAt / music.payoffAt (anchors, like scene "at").
// Usage: node scripts/episode-music.mjs episodes/<id>.json <props.json>
// If python3 or the engine is missing, or music.engine is "file", the episode is passed through unchanged.
// The bed comes from the cinematic library (music/e2a_cinematic.py) unless music.engine is "synth".
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const [epFile, propsOut] = process.argv.slice(2);
const ep = JSON.parse(fs.readFileSync(epFile, 'utf8'));
const write = (e) => fs.writeFileSync(propsOut, JSON.stringify({episode: e}));
const engine = new URL('../../music/e2a_music.py', import.meta.url).pathname;

// Narration first: clean and level the voice once (settings in audio-mix.json -> voice), so the music and
// effects are measured against the voice the viewer will hear. The original file is left untouched.
const MIX = JSON.parse(fs.readFileSync(new URL('../audio-mix.json', import.meta.url), 'utf8'));
{
  const v = MIX.voice;
  const src = `public/${ep.voice}`;
  const out = ep.voice.replace(/\.[a-z0-9]+$/i, '') + '.mix.mp3';
  const chain = [
    `highpass=f=${v.highpassHz}`,
    `equalizer=f=${v.presenceHz}:t=q:w=1.0:g=${v.presenceDb}`,
    `acompressor=threshold=${v.compressThresholdDb}dB:ratio=${v.compressRatio}:attack=8:release=120`,
    `loudnorm=I=${v.targetLufs}:TP=${v.peakLimitDb}:LRA=7`,
  ].join(',');
  try {
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', src, '-af', chain, '-ac', '1', '-ar', '44100', '-c:a', 'libmp3lame', '-b:a', '192k', `public/${out}`]);
    ep.voice = out;
    console.log(`voice: ${src} -> public/${out} (${v.targetLufs} LUFS, presence +${v.presenceDb} dB)`);
  } catch (e) {
    console.log(`voice: processing skipped (${e.message.split('\n')[0]}), using ${src} as-is`);
  }
}

if (ep.music?.engine === 'file' || !fs.existsSync(engine)) {
  console.log(`music: using ${ep.music?.src ?? 'music.mp3'} as-is`);
  write(ep);
  process.exit(0);
}

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
  throw new Error(`music anchor not found in narration: "${a}"`);
};

const vStart = ep.words[0].start;
const vEnd = ep.words.at(-1).end;
const total = vEnd + 0.25 + (ep.outro?.seconds ?? 1.4);
const cuts = ep.scenes.slice(1).map((s) => resolve(s.at, s.offset ?? 0));
const nearest = (share, after = -1) => {
  const target = vStart + share * (vEnd - vStart);
  const c = cuts.filter((x) => x > after + 2.5);
  return c.length ? c.reduce((a, b) => (Math.abs(b - target) < Math.abs(a - target) ? b : a)) : undefined;
};
const STORY = {record: 'record', player: 'highlight', tactical: 'tactical', comparison: 'curiosity', curiosity: 'curiosity'};
const story = ep.music?.story ?? STORY[ep.style] ?? 'curiosity';
const dropAt = ep.music?.dropAt !== undefined ? resolve(ep.music.dropAt) : nearest(story === 'surprise' ? 0.55 : 0.3);
const payoffAt = ep.music?.payoffAt !== undefined ? resolve(ep.music.payoffAt) : nearest(0.75, dropAt ?? 0);

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'e2a-music-'));
const wordsFile = path.join(tmp, 'words.json');
fs.writeFileSync(wordsFile, JSON.stringify(ep.words));
const src = `music/${ep.id}.mp3`;
const args = [engine, '--words', wordsFile, '--story', story, '--duration', total.toFixed(3), '--voice', `public/${ep.voice}`, '--out', `public/${src}`];
if (dropAt !== undefined) args.push('--drop-at', dropAt.toFixed(3));
if (payoffAt !== undefined) args.push('--payoff-at', payoffAt.toFixed(3));
if (ep.music?.track) args.push('--track', ep.music.track);
fs.mkdirSync('public/music', {recursive: true});
// Default bed: the E2A cinematic library (ElevenLabs Music tracks, music/cinematic/), lined up with the cuts.
// music.engine "synth" forces the procedural engine; it is also the fallback when no track is long enough.
const cine = new URL('../../music/e2a_cinematic.py', import.meta.url).pathname;
let info;
if (ep.music?.engine !== 'synth' && fs.existsSync(cine)) {
  const cargs = [cine, '--words', wordsFile, '--story', story, '--duration', total.toFixed(3), '--voice', `public/${ep.voice}`, '--out', `public/${src}`];
  if (dropAt !== undefined) cargs.push('--drop-at', dropAt.toFixed(3));
  if (payoffAt !== undefined) cargs.push('--payoff-at', payoffAt.toFixed(3));
  if (ep.music?.cinematicTrack) cargs.push('--track', ep.music.cinematicTrack);
  try {
    info = JSON.parse(execFileSync('python3', cargs).toString());
  } catch (e) {
    console.log(`music: cinematic library not used (${String(e.stdout ?? e.message).trim()}), falling back to the synth engine`);
  }
}
info ??= JSON.parse(execFileSync('python3', args).toString());
console.log(`music: ${info.track} (${info.style}, ${info.bpm} bpm) drop ${info.drop}s payoff ${info.payoff}s end hit ${info.end_hit ?? '-'}s${info.offset !== undefined ? ` (track offset ${info.offset}s)` : ''}`);
// log the edit choices next to the music rotation (music/history.json is committed with each day's videos),
// so the validator can rotate hooks and endings across videos
const histFile = new URL('../../music/history.json', import.meta.url).pathname;
try {
  const hist = JSON.parse(fs.readFileSync(histFile, 'utf8'));
  if (hist.length) Object.assign(hist[hist.length - 1], {episode: ep.id, hook: ep.hook ?? 'stat-slam', ending: ep.ending ?? null});
  fs.writeFileSync(histFile, JSON.stringify(hist, null, 1));
} catch {}
write({...ep, music: {...ep.music, src, premixed: true, hits: [info.drop ?? dropAt, info.payoff ?? payoffAt].filter((x) => typeof x === 'number')}});
