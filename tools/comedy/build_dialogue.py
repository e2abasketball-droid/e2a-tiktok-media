#!/usr/bin/env python3
"""E2A YouTube Comedy - dialogue builder.
Cuts the chosen ElevenLabs takes, places each line on the episode timeline, levels them,
and writes: dialogue.wav (48 kHz mono), lines.json (global word times + per-character mouth
envelopes at 30 fps) for the Remotion episode. Usage:
  python3 tools/comedy/build_dialogue.py <takes_dir> <episode_spec.json> <out_dir>
The spec lists lines: {id, who, take, cut:[a,b], at, gain_db?, words:[[text, start, end],...]}
(word times relative to the take file, from ElevenLabs Scribe)."""
import json, subprocess, sys, os
import numpy as np

SR = 48000
FPS = 30
takes, spec_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
spec = json.load(open(spec_path))
os.makedirs(out, exist_ok=True)

def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

dur = spec['duration']
N = int(dur * SR)
mix = np.zeros(N)
# one mouth envelope per speaking character (EP001: AND1 + ACE; EP002 adds BUCKETS)
env = {c: np.zeros(int(dur * FPS) + 1) for c in sorted({'AND1', 'ACE'} | {L['who'] for L in spec['lines']})}
lines_out = []
for L in spec['lines']:
    x = load(os.path.join(takes, L['take'] + '.mp3'))
    a, b = L['cut']
    seg = x[int(a * SR):int(b * SR)].copy()
    # 12 ms fades so cuts never click
    f = int(0.012 * SR)
    seg[:f] *= np.linspace(0, 1, f)
    seg[-f:] *= np.linspace(1, 0, f)
    # level: speech RMS (frames above -45 dBFS) to the target, then per-line trim
    fr = int(0.02 * SR)
    rms = np.array([np.sqrt(np.mean(seg[i:i + fr] ** 2)) for i in range(0, len(seg) - fr, fr)])
    act = rms[rms > 10 ** (-45 / 20)]
    cur = 20 * np.log10(np.sqrt(np.mean(act ** 2)))
    g = spec['target_rms_db'] - cur + L.get('gain_db', 0)
    seg *= 10 ** (g / 20)
    s0 = int(L['at'] * SR)
    mix[s0:s0 + len(seg)] += seg[:max(0, N - s0)]
    # mouth envelope (30 fps): smoothed RMS, 0..1
    hop = SR // FPS
    e = np.array([np.sqrt(np.mean(seg[i:i + hop] ** 2)) if i < len(seg) else 0 for i in range(0, len(seg), hop)])
    e = np.clip((20 * np.log10(e + 1e-9) + 42) / 30, 0, 1)
    k0 = int(round(L['at'] * FPS))
    for i, v in enumerate(e):
        if k0 + i < len(env[L['who']]):
            env[L['who']][k0 + i] = max(env[L['who']][k0 + i], v)
    words = [{'text': w, 'start': round(L['at'] + s - a, 3), 'end': round(L['at'] + e2 - a, 3)} for w, s, e2 in L['words']]
    lines_out.append({'id': L['id'], 'who': L['who'], 'start': round(L['at'], 3), 'end': round(L['at'] + (b - a), 3), 'gain_db': round(g, 1),
                      'text': L['text'], 'words': words})
    print(f"{L['id']:10s} {L['who']:5s} at {L['at']:6.2f}  len {b - a:4.2f}  gain {g:+5.1f} dB  {L['text']}")

peak = np.max(np.abs(mix))
print('peak dBFS', round(20 * np.log10(peak), 2))
if peak > 0.89:
    mix *= 0.89 / peak
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
import wave
w = wave.open(os.path.join(out, 'dialogue.wav'), 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
json.dump({'duration': dur, 'fps': FPS, 'lines': lines_out, 'mouth': {k: [round(float(v), 3) for v in vv] for k, vv in env.items()}}, open(os.path.join(out, 'lines.json'), 'w'))
print('wrote', out)
