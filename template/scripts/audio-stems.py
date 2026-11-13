#!/usr/bin/env python3
"""Rebuild the audio stems of a Tactical3D episode offline (voice, music, SFX) exactly as the
composition places them, then measure each stem and the mix: integrated loudness (EBU R128),
true peak, per-effect level and how often an effect competes with the narration.

  node --experimental-strip-types scripts/storyboard-tactical3d.mts tactical/episodes/<id>.json > tl.json
  python3 scripts/audio-stems.py tl.json --out /tmp/stems [--gain-db 2.4] [--json report.json]

No normalisation is applied: --gain-db is a fixed master gain (the same number goes to the final encode).
"""
import argparse
import json
import os
import re
import subprocess

import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')


def load(path, mono_gain=1.0):
    info = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=channels', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.split()
    ch = int(info[0]) if info else 2
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    if ch == 1:
        x *= mono_gain  # ffmpeg -ac 2 copies a mono channel to both sides at unity
    return x


def write(path, x):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_s24le', path], input=x.astype(np.float32).tobytes())
    p.check_returncode() if hasattr(p, 'check_returncode') else None


def r128(path):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    summ = out[out.rfind('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+|-inf)', summ).group(1).replace('-inf', '-120'))
    return {'I': g('I'), 'LRA': g('LRA'), 'TP': g('Peak')}


def rms_db(x, a, b):
    seg = x[max(0, int(a * SR)):max(0, int(b * SR))]
    return float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)) if len(seg) else -120.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('timeline')
    ap.add_argument('--out', required=True)
    ap.add_argument('--gain-db', type=float, default=0.0)
    ap.add_argument('--json')
    ap.add_argument('--words', help='episode words.json: per-word check that no effect covers a word')
    a = ap.parse_args()
    tl = json.load(open(a.timeline))
    os.makedirs(a.out, exist_ok=True)
    n = int(round(tl['total'] * tl['fps'])) / tl['fps']
    N = int(n * SR)
    stems = {k: np.zeros((N, 2), np.float32) for k in ('voice', 'music', 'sfx')}

    def place(k, x, t, vol):
        i = int(round(t * SR))
        x = x[: max(0, N - i)] * vol
        stems[k][i:i + len(x)] += x

    place('voice', load(os.path.join(PUBLIC, tl['voice'])), 0, 1.0)
    if tl.get('music') and tl['music'].get('src'):
        place('music', load(os.path.join(PUBLIC, tl['music']['src'])), 0, tl['music'].get('volume', 1.0))
    events = []
    for e in tl['sfx']:
        t = round(e['t'] * tl['fps']) / tl['fps']  # Sequence starts on a whole frame
        x = load(os.path.join(PUBLIC, 'sfx', e['name'] + '.mp3'))[: int(2.5 * SR)]
        place('sfx', x, t, e['volume'])
        events.append({**e, 't': t})
    g = 10 ** (a.gain_db / 20)
    for k in stems:
        stems[k] *= g
    mix = stems['voice'] + stems['music'] + stems['sfx']
    rep = {'gain_db': a.gain_db, 'duration': n}
    for k, x in {**stems, 'mix': mix}.items():
        p = os.path.join(a.out, f'{k}.wav')
        write(p, x)
        rep[k] = r128(p)
    # narration activity on 50 ms frames
    v = stems['voice'].mean(1)
    s = stems['sfx'].mean(1)
    m = stems['music'].mean(1)
    H = int(0.05 * SR)
    fr = lambda y: 20 * np.log10(np.sqrt(np.mean(y[: len(y) // H * H].reshape(-1, H) ** 2, axis=1)) + 1e-9)
    vf, sf, mf = fr(v), fr(s), fr(m)
    speech = vf > (vf.max() - 30)
    rep['music_under_speech_db'] = float(np.median(mf[speech] - vf[speech]))
    rep['music_in_pauses_dbfs'] = float(np.median(mf[~speech & (np.arange(len(vf)) * 0.05 < n - 1.0)]))
    comp = speech & (sf > vf - 10)
    rep['sfx_competing_frames'] = int(comp.sum())
    rep['sfx_competing_at'] = [round(i * 0.05, 2) for i in np.flatnonzero(comp)][:20]
    rep['sfx_events'] = []
    for e in events:
        t0, t1 = e['t'], e['t'] + 0.6
        peak = float(20 * np.log10(np.abs(stems['sfx'][int(t0 * SR):int(t1 * SR)]).max() + 1e-9))
        rep['sfx_events'].append({'t': e['t'], 'name': e['name'], 'volume': e['volume'], 'rms_600ms_dbfs': round(rms_db(stems['sfx'], t0, t1), 1), 'peak_dbfs': round(peak, 1), 'voice_rms_dbfs': round(rms_db(stems['voice'], t0, t1), 1)})
    if a.words:
        ws = json.load(open(a.words))
        rows = []
        for w in ws:
            vr = rms_db(stems['voice'], w['start'], w['end'])
            sr_ = rms_db(stems['sfx'], w['start'], w['end'])
            mr = rms_db(stems['music'], w['start'], w['end'])
            rows.append({'word': w['text'], 't': round(w['start'], 2), 'voice_db': round(vr, 1), 'sfx_minus_voice_db': round(sr_ - vr, 1), 'music_minus_voice_db': round(mr - vr, 1)})
        rep['words_sfx_within_12db'] = [r for r in rows if r['sfx_minus_voice_db'] > -12]
        rep['worst_sfx_vs_word_db'] = max(r['sfx_minus_voice_db'] for r in rows)
        rep['worst_music_vs_word_db'] = max(r['music_minus_voice_db'] for r in rows)
        rep['median_music_vs_word_db'] = float(np.median([r['music_minus_voice_db'] for r in rows]))
    print(json.dumps(rep, indent=1))
    if a.json:
        json.dump(rep, open(a.json, 'w'), indent=1)


if __name__ == '__main__':
    main()
