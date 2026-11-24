#!/usr/bin/env python3
"""E2A Football — AUDIO-FIRST EDITORIAL LOCK (FB-SETPIECE-001 V09+).

One Deuce take is cut into phrases at its own silences (raw in/out) and each phrase is PLACED at a video time
chosen so that the key word lands on its tactical event (the play clock of the edit is built around these
placements: see remotion/src/episodes/narratedV09.ts). The voice is never time-stretched or pitch-shifted;
only whole phrases move. A phrase can be left out (kept: false) without touching the others.

Outputs
  <out>/voice-placed.wav   the take re-placed on the video timeline (48 kHz mono, 12 ms edge fades)
  <words>                  video-timed words for the subtitles (tags removed, phrase breaks marked)
  <out>/voice-plan.json    the phrase table (raw in/out, video in/out, key word times) for the report

    python3 football/scripts/fb_voice_plan.py <plan.json>
"""
import json
import os
import re
import subprocess
import sys

SR = 48000


def main(plan_path):
    plan = json.load(open(plan_path))
    base = os.path.dirname(os.path.abspath(plan_path))
    raw = os.path.join(base, plan['raw'])
    words = json.load(open(os.path.join(base, plan['words'])))['words']
    out_dir = os.path.join(base, plan['out_dir'])
    os.makedirs(out_dir, exist_ok=True)
    words = [w for w in words if w.get('type', 'word') == 'word' and not re.fullmatch(r'\[.*\]', w['text'])]
    placed, table, inputs, filters = [], [], [], []
    k = 0
    for ph in plan['phrases']:
        a, b = ph['raw']
        off = ph['at'] - a
        ws = [w for w in words if w['start'] >= a - 0.02 and w['start'] < b - 0.05]
        row = {'id': ph['id'], 'text': ' '.join(w['text'] for w in ws), 'raw': [a, b], 'video': [round(a + off, 3), round(b + off, 3)], 'kept': ph.get('kept', True), 'event': ph.get('event', '')}
        table.append(row)
        if not ph.get('kept', True):
            continue
        for i, w in enumerate(ws):
            placed.append({'text': w['text'].strip(), 'start': round(w['start'] + off, 3), 'end': round(w['end'] + off, 3), **({'br': True} if i == len(ws) - 1 or w['text'].rstrip().endswith(('.', '!', '...')) else {})})
        d = b - a
        inputs += ['-ss', f'{a:.3f}', '-t', f'{d:.3f}', '-i', raw]
        ms = int(round((a + off) * 1000))
        filters.append(f'[{k}:a]aresample={SR},aformat=channel_layouts=mono,afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012,adelay={ms}[p{k}]')
        k += 1
    dur = plan['duration']
    mix = ''.join(f'[p{i}]' for i in range(k)) + f'amix=inputs={k}:normalize=0:dropout_transition=0,apad=whole_dur={dur},atrim=0:{dur}[v]'
    wav = os.path.join(out_dir, 'voice-placed.wav')
    subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(filters + [mix]), '-map', '[v]', '-ar', str(SR), '-ac', '1', wav], check=True)
    # overlaps are an error: phrases must not talk over each other
    kept = [r for r in table if r['kept']]
    for x, y in zip(kept, kept[1:]):
        if y['video'][0] < x['video'][1] - 0.01:
            sys.exit(f"phrase overlap: {x['id']} ends {x['video'][1]} > {y['id']} starts {y['video'][0]}")
    json.dump(placed, open(os.path.join(base, plan['words_out']), 'w'), indent=1)
    json.dump({'source': plan.get('source'), 'phrases': table}, open(os.path.join(out_dir, 'voice-plan.json'), 'w'), indent=1)
    for r in table:
        print(f"{r['id']:4} {'KEEP' if r['kept'] else 'DROP'} raw {r['raw'][0]:6.2f}-{r['raw'][1]:6.2f} -> video {r['video'][0]:6.2f}-{r['video'][1]:6.2f}  {r['text']}")
    print(f'{len(placed)} words placed -> {wav}')


if __name__ == '__main__':
    main(sys.argv[1])
