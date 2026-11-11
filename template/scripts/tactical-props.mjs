#!/usr/bin/env node
// Assemble render props for the Tactical composition: episode edit + plays + real word timings.
// Usage: node scripts/tactical-props.mjs tactical/episodes/<id>.json out/props.json [--music public/music/x.mp3]
import fs from 'node:fs';
import path from 'node:path';
const [epFile, out, ...rest] = process.argv.slice(2);
const ep = JSON.parse(fs.readFileSync(epFile, 'utf8'));
const dir = path.dirname(epFile);
const words = JSON.parse(fs.readFileSync(epFile.replace(/\.json$/, '.words.json'), 'utf8'));
const plays = {};
for (const [k, id] of Object.entries(ep.plays)) plays[k] = JSON.parse(fs.readFileSync(path.join(dir, '..', 'plays', `${id}.json`), 'utf8'));
const mi = rest.indexOf('--music');
const music = mi >= 0 ? {src: rest[mi + 1].replace(/^public\//, ''), volume: 1} : ep.music;
const episode = {...ep, voice: ep.voiceMix ?? ep.voice, words, plays, music};
fs.mkdirSync(path.dirname(out), {recursive: true});
fs.writeFileSync(out, JSON.stringify({episode}));
console.log(`props: ${out} (${words.length} words, ${ep.shots.length} shots, plays ${Object.keys(plays).join('+')})`);
