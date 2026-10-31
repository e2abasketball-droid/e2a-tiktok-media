#!/usr/bin/env node
// Technical QC for a rendered Reel (SPEC §13/§15): 1080x1920, 30fps, 60-90s (or --allow-short), h264+aac, <15MB, has audio.
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
const f = process.argv[2]; const short = process.argv.includes('--allow-short');
const j = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', f]).toString());
const v = j.streams.find((s) => s.codec_type === 'video'), a = j.streams.find((s) => s.codec_type === 'audio');
const dur = +j.format.duration, size = fs.statSync(f).size / 1e6;
const checks = {
  resolution: v.width === 1080 && v.height === 1920, fps: v.r_frame_rate === '30/1', video_codec: v.codec_name === 'h264',
  audio_codec: a?.codec_name === 'aac', pix_fmt: v.pix_fmt === 'yuv420p', duration: short || (dur >= 60 && dur <= 90), size_under_15MB: size < 15,
};
let mean = null;
try { const o = execFileSync('ffmpeg', ['-i', f, '-af', 'volumedetect', '-vn', '-f', 'null', '-'], {stdio: ['ignore', 'pipe', 'pipe']}); } catch (e) { mean = /mean_volume: (-?[\d.]+)/.exec(e.stderr?.toString() ?? '')?.[1]; }
if (mean === null) { const r = execFileSync('sh', ['-c', `ffmpeg -i "${f}" -af volumedetect -vn -f null - 2>&1 | grep mean_volume || true`]).toString(); mean = /mean_volume: (-?[\d.]+)/.exec(r)?.[1] ?? null; }
checks.audio_not_silent = mean !== null && +mean > -60;
console.log(JSON.stringify({file: f, duration: dur, sizeMB: +size.toFixed(2), mean_volume_db: mean, checks}, null, 1));
if (Object.values(checks).some((c) => !c)) { console.error('QC FAILED'); process.exit(1); }
console.log('QC OK');
