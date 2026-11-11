#!/usr/bin/env python3
"""Build the narration track of a tactical episode: insert breathing pauses after given phrases
(never speeding the voice up), add a pre-roll and shift the real word timings accordingly.
Usage: python3 scripts/tactical-voice.py tactical/episodes/<id>.json
Reads episode.voiceRaw / episode.wordsRaw / episode.pauses, writes episode.voice (wav in public/) and
<id>.words.json next to the episode."""
import json, os, re, subprocess, sys

ep_file = sys.argv[1]
ep = json.load(open(ep_file))
words = json.load(open(os.path.join(os.path.dirname(ep_file), ep['wordsRaw'])))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
keys = [norm(w['text']) for w in words]

def find_end(phrase):
    p = [norm(x) for x in phrase.split() if norm(x)]
    for i in range(len(keys) - len(p) + 1):
        if keys[i:i + len(p)] == p:
            return i + len(p) - 1
    raise SystemExit(f'pause anchor not found: {phrase}')

cuts = []  # (word index after which to insert, seconds)
for pz in ep.get('pauses', []):
    cuts.append((find_end(pz['after']), float(pz['sec'])))
cuts.sort()
pre = float(ep.get('preroll', 0))
src = os.path.join('public', ep['voiceRaw'])
# cut points: the middle of the silence after the word
pieces, shift_at, t0 = [], [], 0.0
for idx, sec in cuts:
    nxt = words[idx + 1]['start'] if idx + 1 < len(words) else words[idx]['end'] + 0.2
    cut = (words[idx]['end'] + nxt) / 2
    pieces.append((t0, cut))
    shift_at.append((idx, sec))
    t0 = cut
pieces.append((t0, None))
tmp = '/tmp/tactical-voice'
os.makedirs(tmp, exist_ok=True)
lst = []
def sil(name, sec):
    path = f'{tmp}/{name}.wav'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', f'{sec:.3f}', path], check=True)
    return path
if pre > 0:
    lst.append(sil('pre', pre))
for k, (a, b) in enumerate(pieces):
    path = f'{tmp}/p{k}.wav'
    args = ['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ss', f'{a:.3f}'] + (['-to', f'{b:.3f}'] if b else []) + ['-ac', '1', '-ar', '44100', path]
    subprocess.run(args, check=True)
    lst.append(path)
    if k < len(shift_at):
        lst.append(sil(f'gap{k}', shift_at[k][1]))
with open(f'{tmp}/list.txt', 'w') as f:
    f.writelines(f"file '{p}'\n" for p in lst)
out = os.path.join('public', ep['voice'])
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/list.txt', '-c:a', 'pcm_s16le', out], check=True)
# shifted timings
res, add, j = [], pre, 0
for i, w in enumerate(words):
    res.append({'text': w['text'], 'start': round(w['start'] + add, 3), 'end': round(w['end'] + add, 3)})
    while j < len(shift_at) and shift_at[j][0] == i:
        add += shift_at[j][1]
        j += 1
wf = ep_file.replace('.json', '.words.json')
json.dump(res, open(wf, 'w'))
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
print(json.dumps({'voice': out, 'words': wf, 'duration': round(dur, 3), 'last_word_end': res[-1]['end'], 'pauses_added': round(sum(s for _, s in shift_at) + pre, 2)}))
