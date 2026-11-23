#!/usr/bin/env python3
"""E2A Football — QC of a rendered MP4 (no re-render).

  python3 football/qa/qc_render.py <video.mp4> [--out qc.json] [--silent]

FAIL checks: 1080x1920, 30 fps, h264 + aac, 30-45 s (division.json), loudness -14 +-1 LUFS and true peak
<= -1 dBTP (skipped with --silent), no black frames. WARN checks: 1-3 frame "pops" (a frame that differs
from both neighbours while the neighbours match) and hard cuts (listed for the editor to compare).
Same thresholds idea as the shared qc-video.py, which needs a basketball episode file and so is not used.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
import fb_lib as L  # noqa: E402

SW, SH = 135, 240


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate:format=duration', '-of', 'json', path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(path):
    r = subprocess.run(['ffmpeg', '-nostats', '-i', path, '-map', '0:a', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    I = TP = None
    for line in r.stderr.splitlines()[::-1]:
        s = line.strip()
        if s.startswith('I:') and I is None:
            I = float(s.split()[1])
        if s.startswith('Peak:') and TP is None:
            TP = float(s.split()[1])
    return I, TP


def frames(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={SW}:{SH},format=gray', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, SH, SW).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--out')
    ap.add_argument('--silent', action='store_true')
    a = ap.parse_args()
    spec = L.division()['video']
    res = []

    def add(name, ok, detail, level='FAIL'):
        res.append({'check': name, 'status': 'PASS' if ok else level, 'detail': detail})

    p = probe(a.video)
    v = [s for s in p['streams'] if s['codec_type'] == 'video'][0]
    au = [s for s in p['streams'] if s['codec_type'] == 'audio']
    dur = float(p['format']['duration'])
    add('format 1080x1920', (v['width'], v['height']) == (1080, 1920), f"{v['width']}x{v['height']}")
    add('30 fps', v['r_frame_rate'] in ('30/1', '30000/1000'), v['r_frame_rate'])
    add('codecs h264 + aac', v['codec_name'] == 'h264' and bool(au) and au[0]['codec_name'] == 'aac', f"{v['codec_name']} + {au[0]['codec_name'] if au else 'none'}")
    ds = spec.get('duration_s', {'min': 30, 'max': 45})
    lo, hi = ds['min'], ds['max']
    add(f'duration {lo}-{hi} s', lo <= dur <= hi + 0.05, f'{dur:.2f} s')
    if a.silent:
        res.append({'check': 'loudness', 'status': 'SKIPPED', 'detail': 'silent cut (no voice, no music)'})
    else:
        I, TP = loudness(a.video)
        add('loudness -14 +-1 LUFS', I is not None and abs(I + 14) <= 1, f'I={I} LUFS')
        add('true peak <= -1 dBTP', TP is not None and TP <= -1.0, f'TP={TP} dBTP')
    F = frames(a.video)
    mean = F.mean(axis=(1, 2))
    black = [int(i) for i in np.where(mean < 6)[0]]
    add('no black frames', not black, f'{len(black)} black frames' + (f' (first {black[:5]})' if black else ''))
    d = np.abs(np.diff(F, axis=0)).mean(axis=(1, 2))
    pops = []
    for i in range(1, len(F) - 1):
        a1 = d[i - 1]
        a2 = d[i]
        nb = np.abs(F[i + 1] - F[i - 1]).mean()
        if a1 > 12 and a2 > 12 and nb < 0.35 * min(a1, a2):
            pops.append(i)
    add('no 1-frame pops', not pops, f'{len(pops)} frames' + (f': {pops[:10]}' if pops else ''), level='WARN')
    cuts = [round((i + 1) / 30, 2) for i in np.where(d > 22)[0]]
    res.append({'check': 'hard cuts (info)', 'status': 'INFO', 'detail': ', '.join(map(str, cuts[:20])) or 'none'})
    for r in res:
        print(f"{r['status']:8} {r['check']} — {r['detail']}")
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as fh:
            json.dump({'video': os.path.basename(a.video), 'duration': dur, 'checks': res}, fh, indent=1)
    sys.exit(1 if any(r['status'] == 'FAIL' for r in res) else 0)


if __name__ == '__main__':
    main()
