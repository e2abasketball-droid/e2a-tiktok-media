// E2A Tactical Studio — AUDIO LOCK guard (Chicago V3 brief sec. 0 / 13.4, 2026-11-22). Generic for any episode that
// declares `audioReuseOnly: true` and/or `disallowTTS: true`:
//   1. the episode lists an `audioLock` and every locked file (voice, voice mix, music, word timings) exists and has
//      exactly the recorded sha256: the reel can only use the existing, already-paid audio;
//   2. the episode's own audio paths (voice, voiceMix, music.src) are all locked files (nothing unlocked sneaks in);
//   3. no generation request is carried by the episode (no voiceRaw take request, no TTS / voice-generation keys);
//   4. the scripts of this episode's pipeline (generator, finish, props, render) contain no TTS / ElevenLabs endpoint or
//      SDK (api.elevenlabs.io, xi-api-key, elevenlabs imports, text_to_speech, creative_generate_speech, Scribe, gTTS,
//      Polly, Azure / Google TTS);
//   5. scripts/tactical-voice.py refuses to run on the episode (exit != 0) — the only local script that rebuilds a voice.
//   node scripts/test-audio-lock.mjs tactical/episodes/<id>.json [pipeline scripts...]
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';

const epFile = process.argv[2];
const ep = JSON.parse(fs.readFileSync(epFile, 'utf8'));
const extra = process.argv.slice(3);
let failed = 0;
const check = (name, ok, value) => {
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name} — ${value}`);
};
const sha = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
check('episode declares audioReuseOnly + disallowTTS', ep.audioReuseOnly === true && ep.disallowTTS === true, `audioReuseOnly=${ep.audioReuseOnly} disallowTTS=${ep.disallowTTS}`);
const lock = ep.audioLock ?? {};
const files = {...(lock.files ?? {})};
for (const [rel, want] of Object.entries(files)) {
  const f = path.join('public', rel);
  const ok = fs.existsSync(f) && sha(f) === want;
  check(`locked audio ${rel} unchanged`, ok, fs.existsSync(f) ? sha(f).slice(0, 16) : 'MISSING');
}
for (const [rel, want] of Object.entries(lock.words ?? {})) {
  const ok = fs.existsSync(rel) && sha(rel) === want;
  check(`locked word timings ${rel} unchanged`, ok, fs.existsSync(rel) ? sha(rel).slice(0, 16) : 'MISSING');
  const wEp = path.join(path.dirname(epFile), `${ep.id}.words.json`);
  if (fs.existsSync(wEp) && fs.existsSync(rel)) {
    const a = JSON.parse(fs.readFileSync(rel, 'utf8')), b = JSON.parse(fs.readFileSync(wEp, 'utf8'));
    check('episode words = locked word timings (same words, same times)', JSON.stringify(a) === JSON.stringify(b), `${b.length} words`);
  }
}
const used = [ep.voice, ep.voiceMix, ep.music?.src].filter(Boolean);
check('every audio path of the episode is a locked file', used.length > 0 && used.every((u) => u in files), used.join(', '));
check('no ambience / sfx layers added', !ep.ambience && (ep.autoSfx === false || ep.autoSfx === undefined) && ep.shots.every((s) => !(s.sfx ?? []).length), `autoSfx=${ep.autoSfx}`);
const genKeys = ['voiceRaw', 'wordsRaw', 'gaps', 'tts', 'ttsModel', 'voiceId', 'voice_id', 'modelId', 'generate'];
const carried = genKeys.filter((k) => k in ep);
check('no generation request carried by the episode', carried.length === 0, carried.join(',') || 'none');
const BAD = [/api\.elevenlabs\.io/i, /xi-api-key/i, /from\s+elevenlabs|import\s+elevenlabs|require\(['"]elevenlabs|@elevenlabs\//i, /text[_-]to[_-]speech/i,
  /creative_generate_speech|creative_transcribe_audio|speech_to_text|scribe_v\d/i, /gtts|pyttsx|polly\.|synthesize_speech|texttospeech|cognitiveservices.*speech/i];
const id = ep.id;
const pipeline = [
  `tactical/episodes/_gen-${id.replace('-action', '')}.py`, `tactical/episodes/_finish-${id.replace('-action', '')}.py`,
  'scripts/tactical-props.mjs', 'scripts/render-tactical.sh', ...extra,
].filter((f, i, a) => fs.existsSync(f) && a.indexOf(f) === i);
for (const f of pipeline) {
  const src = fs.readFileSync(f, 'utf8').split('\n').filter((l) => !/^\s*(#|\/\/|\*)/.test(l)).join('\n');
  const hit = BAD.find((r) => r.test(src));
  check(`pipeline script ${f} has no TTS / ElevenLabs call`, !hit, hit ? `matches ${hit}` : 'clean');
}
const r = spawnSync('python3', ['scripts/tactical-voice.py', epFile], {encoding: 'utf8'});
check('tactical-voice.py refuses this episode', r.status !== 0 && /REFUSED/.test(r.stderr + r.stdout), `exit ${r.status}: ${(r.stderr || r.stdout).trim().split('\n').pop()}`);
console.log(failed ? `\n${failed} audio-lock check(s) FAILED` : `\naudio lock OK: ELEVENLABS_CREDITS_SPENT_FOR_V3 = ${lock.elevenlabsCreditsSpentForV3 ?? '?'} (workflow assertion: reuse only)`);
process.exit(failed ? 1 : 0);
