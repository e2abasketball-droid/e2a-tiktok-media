#!/usr/bin/env node
// Automatic QC for a Pro render. Usage: node scripts/qc-pro.mjs final.mp4 [--min 20 --max 26] [--frames outDir]
// Checks format, duration, loudness, black frames, frozen (static) stretches, and extracts a
// contact sheet so a human or a vision model can review framing, subtitles and legibility.
import {execFileSync, spawnSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const file = args[0];
const opt = (k, d) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const min = +opt('--min', 20);
const max = +opt('--max', 26);
const outDir = opt('--frames', path.join(path.dirname(file), 'qc'));
fs.mkdirSync(outDir, {recursive: true});

const probe = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', file]).toString());
const v = probe.streams.find((s) => s.codec_type === 'video');
const a = probe.streams.find((s) => s.codec_type === 'audio');
const dur = +probe.format.duration;
const ff = (filters, extra = []) => spawnSync('ffmpeg', ['-hide_banner', '-nostats', '-i', file, ...extra, ...filters, '-f', 'null', '-'], {encoding: 'utf8'}).stderr;

const loud = ff(['-af', 'ebur128=peak=true', '-vn']);
const I = +(/I:\s+(-?[\d.]+) LUFS/.exec(loud.split('Summary:')[1] ?? '')?.[1] ?? NaN);
const TP = +(/Peak:\s+(-?[\d.]+) dBFS/.exec(loud.split('Summary:')[1] ?? '')?.[1] ?? NaN);

const black = [...ff(['-vf', 'blackdetect=d=0.1:pix_th=0.06', '-an']).matchAll(/black_start:([\d.]+) black_end:([\d.]+)/g)].map((m) => [+m[1], +m[2]]);
const frozen = [...ff(['-vf', 'freezedetect=n=0.002:d=2.5', '-an']).matchAll(/freeze_start: ([\d.]+)[\s\S]*?freeze_end: ([\d.]+)/g)].map((m) => [+m[1], +m[2]]);

// contact sheet: one frame per second, 5 columns
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', file, '-vf', 'fps=1,scale=270:480,tile=5x6:padding=6:color=0x222222', '-frames:v', '1', path.join(outDir, 'contact.jpg')]);
for (const s of [0.5, dur * 0.25, dur * 0.5, dur * 0.75, dur - 0.7]) {
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-ss', s.toFixed(2), '-i', file, '-frames:v', '1', path.join(outDir, `frame_${s.toFixed(1)}.png`)]);
}

const checks = {
  resolution_1080x1920: v.width === 1080 && v.height === 1920,
  fps_30_or_60: ['30/1', '60/1'].includes(v.r_frame_rate),
  h264_yuv420p: v.codec_name === 'h264' && v.pix_fmt === 'yuv420p',
  aac_audio: a?.codec_name === 'aac',
  duration_in_range: dur >= min && dur <= max,
  loudness_near_minus14_lufs: Math.abs(I + 14) <= 1.5,
  true_peak_below_minus1: TP <= -1.0,
  no_black_frames: black.length === 0,
  no_static_stretch_over_2_5s: frozen.length === 0,
  size_under_15MB: fs.statSync(file).size < 15e6,
};
const report = {file, duration: +dur.toFixed(2), sizeMB: +(fs.statSync(file).size / 1e6).toFixed(2), lufs: I, truePeak: TP, black, frozen, contactSheet: path.join(outDir, 'contact.jpg'), checks};
console.log(JSON.stringify(report, null, 1));
fs.writeFileSync(path.join(outDir, 'qc.json'), JSON.stringify(report, null, 1));
const failed = Object.entries(checks).filter(([, ok]) => !ok).map(([k]) => k);
if (failed.length) {
  console.error('QC FAILED: ' + failed.join(', '));
  process.exit(1);
}
console.log('QC OK (technical). Now review contact.jpg: subtitles, framing, legibility, images match narration, facts.');
