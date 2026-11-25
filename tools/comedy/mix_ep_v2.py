#!/usr/bin/env python3
"""E2A YouTube Comedy - episode audio master, V02 (dialogue + music bed with ducking).

1. Builds the dialogue stem on the ANIMATION clock (dialogue.wav + light gym reverb + room tone
   + the few one-shots in sfx.json) - the same clock as lines.json.
2. Applies the picture edit (music.json -> edit.cuts / old_end) so the stem matches the episode.
3. Adds the music bed on the EPISODE clock: automatic ducking under every spoken line
   (attack/release envelope from the dialogue itself) + scripted comedy automation
   (level offsets and musical stops, see music.json).
4. Two-pass loudnorm to -14 LUFS / -1.5 dBTP (YouTube).

Usage: python3 tools/comedy/mix_ep_v2.py <episode_dir> <sfx_dir> <out.wav> [--stems <dir>]
No ball-bounce SFX: only the cues listed in sfx.json are used."""
import json, os, subprocess, sys, wave
import numpy as np
from numpy.fft import rfft, irfft

SR = 48000
args = sys.argv[1:]
ep, sfx_dir, out = args[0], args[1], args[2]
stems = args[args.index('--stems') + 1] if '--stems' in args else None
template_dir = os.path.dirname(os.path.dirname(os.path.abspath(ep)))  # template/
cfg = json.load(open(os.path.join(ep, 'sfx.json')))
mus = json.load(open(os.path.join(ep, 'music.json')))


def load(path, ch=2):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64).reshape(-1, ch).T


def onepole(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    from scipy.signal import lfilter  # noqa
    return lfilter([1 - a], [1, -a], x, axis=-1)


try:
    import scipy  # noqa
    def lowpass(x, fc):
        return onepole(onepole(x, fc), fc)
except ImportError:  # pragma: no cover
    def lowpass(x, fc):
        a = np.exp(-2 * np.pi * fc / SR)
        for _ in range(2):
            y = np.zeros_like(x)
            acc = np.zeros(x.shape[0])
            for i in range(x.shape[1]):
                acc = (1 - a) * x[:, i] + a * acc
                y[:, i] = acc
            x = y
        return x


def write(path, x):
    pcm = (np.clip(x.T, -1, 1) * 32767).astype(np.int16)
    w = wave.open(path, 'wb'); w.setnchannels(x.shape[0]); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()


rng = np.random.default_rng(11)
# ---------------- 1. dialogue stem, animation clock ----------------
N0 = int(cfg['duration'] * SR)
d = load(os.path.join(ep, 'dialogue.wav'), 1)[0]
d = np.pad(d, (0, max(0, N0 - len(d))))[:N0]
L = int(0.7 * SR)
tt = np.arange(L) / SR
irs = []
for pre in (0.012, 0.017):
    ir = rng.standard_normal(L) * np.exp(-tt / 0.16)
    ir[: int(pre * SR)] = 0
    irs.append(ir / np.sqrt(np.sum(ir ** 2)))
wet = 10 ** (-19 / 20)
n = 1 << int(np.ceil(np.log2(N0 + L)))
Dd = rfft(d, n)
voice = np.stack([d + wet * irfft(Dd * rfft(irs[0], n), n)[:N0], d + wet * irfft(Dd * rfft(irs[1], n), n)[:N0]])
fx = np.zeros((2, N0))
noise = rng.standard_normal((2, N0))
noise = lowpass(noise, 900)
noise *= 10 ** (-56 / 20) / (np.sqrt(np.mean(noise ** 2)) + 1e-12)
fx += noise
for c in cfg['cues']:
    x = load(os.path.join(sfx_dir, c['file']))
    if c.get('trim'):
        x = x[:, : int(c['trim'] * SR)]
    if c.get('lowpass'):
        x = lowpass(x, c['lowpass'])
    f = int(c.get('fade', 0.03) * SR)
    if f:
        x[:, -f:] *= np.linspace(1, 0, f)
    x *= 10 ** (c['gain_db'] / 20)
    s0 = int(c['at'] * SR)
    e = min(N0, s0 + x.shape[1])
    fx[:, s0:e] += x[:, : e - s0]
    print('cue', c['file'], 'anim', c['at'], c['gain_db'], 'dB')

# ---------------- 2. picture edit ----------------
cuts = mus['edit']['cuts']
old_end = mus['edit']['old_end']


def edit(x):
    segs, prev = [], 0.0
    for a, b in cuts + [[old_end, old_end]]:
        segs.append(x[:, int(prev * SR):int(a * SR)].copy())
        prev = b
    # 5 ms fade out / in on every splice (all edits fall in room tone); keeps the exact length
    xf = int(0.005 * SR)
    for i, s in enumerate(segs):
        if i > 0 and s.shape[1] > xf:
            s[:, :xf] *= np.linspace(0, 1, xf)
        if i < len(segs) - 1 and s.shape[1] > xf:
            s[:, -xf:] *= np.linspace(1, 0, xf)
    return np.concatenate(segs, axis=1)


voice = edit(voice)
fx = edit(fx)
N = voice.shape[1]
dur = N / SR
print(f'episode length {dur:.3f} s')

# ---------------- 3. music bed ----------------
m = load(os.path.join(template_dir, mus['file']))
off = int(mus.get('start_offset', 0) * SR)
m = m[:, off:off + N]
if m.shape[1] < N:
    raise SystemExit('music shorter than the episode')
# normalise the bed to 0 dBFS RMS reference, then the gain curve sets the level
m /= np.sqrt(np.mean(m ** 2))
# speech activity from the (edited) dry dialogue: 10 ms RMS frames, above -42 dBFS = speech
hop = int(0.01 * SR)
dry = voice.mean(0)
fr = np.array([np.sqrt(np.mean(dry[i:i + hop] ** 2)) for i in range(0, N, hop)])
act = (20 * np.log10(fr + 1e-9) > -42).astype(float)
# bridge tiny gaps inside a line (< 180 ms) so the bed doesn't pump between words
gap = int(0.18 / 0.01)
i = 0
while i < len(act):
    if act[i] == 0:
        j = i
        while j < len(act) and act[j] == 0:
            j += 1
        if 0 < i and j < len(act) and j - i < gap:
            act[i:j] = 1
        i = j
    else:
        i += 1
# attack / release smoothing (look-ahead by the attack so the duck lands before the first word)
atk, rel = mus['attack'], mus['release']
la = int(atk / 0.01)
act = np.concatenate([act[la:], np.zeros(la)])
env = np.zeros_like(act)
ka, kr = 1 - np.exp(-0.01 / atk), 1 - np.exp(-0.01 / rel)
v = 0.0
for k, a in enumerate(act):
    v += (a - v) * (ka if a > v else kr)
    env[k] = v
g_db = mus['bed_db'] + (mus['under_speech_db'] - mus['bed_db']) * env
# scripted automation (episode clock), with short ramps
tf = np.arange(len(g_db)) * 0.01
mute = np.ones_like(g_db)
for au in mus['automation']:
    a, b = au['from'], au['to']
    if au.get('mute'):
        # 30 ms out, 80 ms back in: a musical stop, not a fade
        w = np.clip(np.minimum((tf - a) / 0.03, (b - tf) / 0.08), 0, 1)
        mute *= 1 - w
    else:
        w = np.clip(np.minimum((tf - a) / 0.25, (b - tf) / 0.25), 0, 1)
        g_db += au['db'] * w
gain = 10 ** (g_db / 20) * mute
gain_s = np.interp(np.arange(N) / SR, tf, gain)
music = m * gain_s
# loop-friendly ends: 40 ms in, 150 ms out
fi, fo = int(0.04 * SR), int(0.15 * SR)
music[:, :fi] *= np.linspace(0, 1, fi)
music[:, -fo:] *= np.linspace(1, 0, fo)

mix = voice + fx + music
f = int(0.02 * SR)
mix[:, :f] *= np.linspace(0, 1, f)
mix[:, -f:] *= np.linspace(1, 0, f)
if stems:
    os.makedirs(stems, exist_ok=True)
    write(os.path.join(stems, 'stem_dialogue.wav'), np.clip(voice, -1, 1))
    write(os.path.join(stems, 'stem_fx_roomtone.wav'), np.clip(fx, -1, 1))
    write(os.path.join(stems, 'stem_music.wav'), np.clip(music, -1, 1))
peak = np.max(np.abs(mix))
if peak > 0.95:
    mix *= 0.95 / peak
tmp = out + '.raw.wav'
write(tmp, mix)

# ---------------- 4. loudness ----------------
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
js = json.loads(r[r.rfind('{'):r.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
      f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', af, '-ar', str(SR), out], check=True)
os.remove(tmp)
print('wrote', out, 'input I', js['input_i'])
