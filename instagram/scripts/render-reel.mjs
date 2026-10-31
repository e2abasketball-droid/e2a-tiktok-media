#!/usr/bin/env node
// Usage: node scripts/render-reel.mjs <episode.json> <out.mp4>   (run from anywhere)
// Renders with the pre-installed headless Chromium, then loudness-normalises audio (-14 LUFS) and verifies the MP4.
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../breakdown-template');
const [epArg, outArg] = process.argv.slice(2);
if (!epArg || !outArg) { console.error('usage: render-reel.mjs <episode.json> <out.mp4>'); process.exit(2); }
const epPath = path.resolve(epArg), out = path.resolve(outArg);
const ep = JSON.parse(fs.readFileSync(epPath, 'utf8'));
// narration lives next to the episode json; stage it into the template's public/ so staticFile() can serve it
const staged = `_vo_${ep.id}.mp3`;
fs.copyFileSync(path.join(path.dirname(epPath), ep.voice), path.join(root, 'public', staged));
ep.voice = staged;
const browser = ['/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell', process.env.CHROME_BIN].find((p) => p && fs.existsSync(p));
const raw = out.replace(/\.mp4$/, '.raw.mp4');
const props = path.join(path.dirname(out), `.props-${ep.id}.json`);
fs.writeFileSync(props, JSON.stringify({episode: ep}));
const args = ['remotion', 'render', 'src/index.ts', 'Breakdown', raw, `--props=${props}`, '--codec=h264', '--crf=23', '--pixel-format=yuv420p', '--x264-preset=veryfast', '--concurrency=4', '--audio-codec=aac'];
if (browser) args.push(`--browser-executable=${browser}`);
execFileSync('npx', args, {cwd: root, stdio: 'inherit'});
execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-i', raw, '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-vf', 'scale=in_range=full:out_range=tv,format=yuv420p', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out], {stdio: 'inherit'});
fs.rmSync(raw); fs.rmSync(props); fs.rmSync(path.join(root, 'public', staged), {force: true});
console.log(execFileSync('node', [path.join(path.dirname(fileURLToPath(import.meta.url)), 'verify-reel.mjs'), out, ...process.argv.slice(4)]).toString());
