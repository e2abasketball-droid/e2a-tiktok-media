#!/usr/bin/env python3
"""E2A cinematic music library: pick a pre-made track (music/cinematic/), line it up with the episode and premix it.

The tracks were generated once with the E2A ElevenLabs Music account (instrumental, eleven_music_v2_5).
For each episode this script:
  1. picks a track that is long enough, matching the story mood and never one of the last 3 used,
  2. shifts it so the track's climax lands on the episode's payoff cut (or its first drop on the drop cut),
  3. ducks it around the voice and calibrates its level from vo.mp3 with the same code as the synth engine
     (e2a_music.Song.finish), so the voice always wins,
  4. logs the pick in music/history.json and prints the same JSON fields as e2a_music.py.

Usage: e2a_cinematic.py --words words.json --duration 24.8 --voice public/audio/vo.mp3 --out public/music/x.mp3
                        [--story record] [--drop-at 8.0] [--payoff-at 17.1] [--track cine-03]
Exit code 3 (no output written) when no track is long enough: the caller falls back to the synth engine.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e2a_music as M  # noqa: E402

SR = M.SR
LIB = os.path.join(HERE, 'cinematic', 'library.json')
# story type -> preferred moods (first match wins among the tracks not used recently)
MOODS = {
    'record': ['heroic', 'triumphant', 'tension'],
    'highlight': ['heroic', 'hybrid', 'dark'],
    'curiosity': ['tension', 'hybrid', 'heroic'],
    'tactical': ['hybrid', 'tension'],
    'surprise': ['tension', 'dark'],
    'emotion': ['emotional', 'triumphant'],
}


def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(float).reshape(-1, 2).T


def pick(lib, story, total, history, track=None):
    tracks = [t for t in lib['tracks'] if t.get('active', True)]
    if track:
        return next(t for t in tracks if t['id'] == track)
    fits = [t for t in tracks if t['duration'] >= total + 0.3]
    if not fits:
        return None
    recent = [h.get('track') for h in history[-3:]]
    fresh = [t for t in fits if t['id'] not in recent] or fits
    moods = MOODS.get(story, [])
    # least recently used first, then mood preference, then the shorter track
    last_use = {h.get('track'): i for i, h in enumerate(history)}
    # keep the 45 s tracks for videos that need them (a short video would start deep inside a long track)
    fresh.sort(key=lambda t: (t['duration'] > 32 and total < 29, last_use.get(t['id'], -1), moods.index(t['mood']) if t['mood'] in moods else len(moods), t['duration']))
    return fresh[0]


def offset_for(t, total, drop_at, payoff_at):
    """Seconds to skip at the start of the track so its climax (or drop) lands on the episode's cut."""
    room = max(0.0, t['duration'] - total - 0.2)
    if payoff_at is not None and t.get('climax') is not None:
        want = t['climax'] - payoff_at
    elif drop_at is not None and t.get('drop') is not None:
        want = t['drop'] - drop_at
    else:
        want = 0.0
    return float(min(room, max(0.0, want)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--words', required=True)
    ap.add_argument('--duration', type=float, required=True)
    ap.add_argument('--voice', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--story', default='curiosity')
    ap.add_argument('--drop-at', type=float)
    ap.add_argument('--payoff-at', type=float)
    ap.add_argument('--track')
    ap.add_argument('--history', default=os.path.join(HERE, 'history.json'))
    a = ap.parse_args()

    with open(a.words) as f:
        words = json.load(f)
    with open(LIB) as f:
        lib = json.load(f)
    hist = []
    if a.history and os.path.exists(a.history):
        with open(a.history) as f:
            hist = json.load(f)
    t = pick(lib, a.story, a.duration, hist, a.track)
    if t is None:
        print(json.dumps({'error': f'no cinematic track is {a.duration:.1f}s long'}))
        sys.exit(3)
    off = offset_for(t, a.duration, a.drop_at, a.payoff_at)
    x = load(os.path.join(HERE, 'cinematic', t['file']))

    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', a.voice, '-af', 'pan=mono|c0=c0', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    voice = np.frombuffer(raw, np.float32).astype(float)
    ch = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=channels', '-of', 'csv=p=0', a.voice],
                        capture_output=True, text=True).stdout.strip()
    if ch == '1':
        voice = voice * 0.7071  # Remotion plays a mono file at -3 dB per channel
    # same trim + multiband ducking + voice-calibrated level + fades as the synth engine
    y = M.Song.finish(M.Song.__new__(M.Song), x, words, a.duration, off, None, duck=True, voice=voice)
    # leave headroom for the final loudnorm (dense orchestral peaks)
    pk = np.max(np.abs(y))
    if pk > 0.85:
        y = y * (0.85 / pk)
    with tempfile.TemporaryDirectory() as td:
        r = os.path.join(td, 'bed.f32')
        y.T.astype(np.float32).tofile(r)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', r,
                        '-c:a', 'libmp3lame', '-b:a', '256k', a.out], check=True)
    in_video = lambda s: round(s - off, 2) if s is not None and 0 < s - off < a.duration else None
    info = dict(track=t['id'], style='cinematic', mood=t['mood'], bpm=t.get('bpm'), story=a.story, offset=round(off, 2),
                drop=in_video(t.get('drop')), payoff=in_video(t.get('climax')), end_hit=in_video(t.get('end_hit')),
                duration=round(a.duration, 2), out=a.out, source='elevenlabs-music')
    if a.history:
        hist.append({'track': t['id'], 'story': a.story, 'out': a.out})
        with open(a.history, 'w') as f:
            json.dump(hist[-60:], f, indent=1)
    print(json.dumps(info))


if __name__ == '__main__':
    main()
