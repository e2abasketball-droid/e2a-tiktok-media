#!/usr/bin/env python3
"""Measure each track in this folder (duration, first drop, climax) and write library.json.
Run after adding or replacing a track: python3 music/cinematic/analyse.py
Hand edits to mood/bpm/active in library.json are kept."""
import json
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 8000
HOP = 0.05


def env_db(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    h = int(HOP * SR)
    e = np.array([np.sqrt(np.mean(x[i:i + h] ** 2) + 1e-12) for i in range(0, len(x) - h, h)])
    return 20 * np.log10(e), len(x) / SR


def biggest_rise(db, t0, t1, win=1.0):
    """Time of the strongest jump in loudness (mean of the next `win` s minus the previous `win` s)."""
    w = int(win / HOP)
    a, b = max(w, int(t0 / HOP)), min(len(db) - w, int(t1 / HOP))
    if b <= a:
        return None
    rise = [db[i:i + w].mean() - db[i - w:i].mean() for i in range(a, b)]
    i = int(np.argmax(rise))
    return round((a + i) * HOP, 2) if rise[i] > 1.5 else None


def main():
    path = os.path.join(HERE, 'library.json')
    old = {}
    if os.path.exists(path):
        with open(path) as f:
            old = {t['id']: t for t in json.load(f)['tracks']}
    tracks = []
    for fn in sorted(os.listdir(HERE)):
        if not fn.endswith('.mp3'):
            continue
        tid = fn[:-4]
        db, dur = env_db(os.path.join(HERE, fn))
        t = dict(old.get(tid, {}))
        t.update(id=tid, file=fn, duration=round(dur, 2),
                 drop=biggest_rise(db, 4.0, 12.0),
                 climax=biggest_rise(db, dur * 0.45, dur * 0.8),
                 end_hit=None)
        t.setdefault('mood', 'heroic')
        t.setdefault('active', True)
        tracks.append(t)
    with open(path, 'w') as f:
        json.dump({'source': 'ElevenLabs Music (eleven_music_v2_5, instrumental), E2A account, flow sAIdo6G6uFvhdvAaxyVU',
                   'tracks': tracks}, f, indent=1)
    for t in tracks:
        print(t['id'], t['duration'], 'drop', t['drop'], 'climax', t['climax'], t['mood'])


if __name__ == '__main__':
    main()
