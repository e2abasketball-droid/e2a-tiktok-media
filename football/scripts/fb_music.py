#!/usr/bin/env python3
"""E2A Football — music bed from the E2A in-house library (music/e2a_music.py, original compositions owned by
E2A, cleared for commercial use: config/asset_licences.json 'music/synth/*'). The shared engine is USED, never
modified: this wrapper only removes its sound-effects bus (ball bounces, sneaker squeak, net swish, impacts,
risers, crowd) after rendering, because the owner rules are 'no ball-bounce sound' and 'voice + subtle music,
no artificial effects'. Rotation history is not written (history=None) so basketball's rotation is untouched.

    python3 football/scripts/fb_music.py --words <video-timed words.json> --voice <voice.wav> --out bed.mp3 \
        --duration 30.2 --track drive_b --drop-at 19.5 --payoff-at 21.0
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'music'))
import e2a_music  # noqa: E402

_render = e2a_music.Song.render


def render_no_fx(self, plan, total_secs):
    B, kicks, cut = _render(self, plan, total_secs)
    B['fx'] = B['fx'] * 0.0  # no bounce / squeak / swish / impacts / risers / crowd
    return B, kicks, cut


e2a_music.Song.render = render_no_fx

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--words', required=True)
    ap.add_argument('--voice', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--duration', type=float, required=True)
    ap.add_argument('--track', default='drive_b')
    ap.add_argument('--story', default='tactical')
    ap.add_argument('--drop-at', type=float)
    ap.add_argument('--payoff-at', type=float)
    a = ap.parse_args()
    words = json.load(open(a.words))
    info = e2a_music.make(words, a.story, a.out, a.duration, a.track, None, False, a.voice, a.drop_at, a.payoff_at)
    print(json.dumps(info, indent=1))
