#!/usr/bin/env python3
"""Motion review props for Tactical3DV2: whole possessions at normal speed with ONE fixed three-quarter
camera (feet and ball visible), no graphics, no subtitles. Used to judge animation before editing.
  python3 tactical/review/make-review-props.py out.json playA.json [playB.json ...] [--cam x,y,z,dist,pitch,yaw,fov] [--from t0] [--to t1] [--speed s]
--speed 0.25 gives the slow-motion check of the same stretch (remap only, the play is still evaluated by play time)."""
import json, sys, argparse
ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('plays', nargs='+')
ap.add_argument('--cam', default='0.0,6.8,0.9,15.5,52,-38,40')
ap.add_argument('--from', dest='t0', type=float, default=0.0)
ap.add_argument('--to', dest='t1', type=float, default=None)
ap.add_argument('--speed', type=float, default=1.0)
ap.add_argument('--voice', default='tactical/ram/voice.wav')
a = ap.parse_args()
x, y, z, dist, pitch, yaw, fov = [float(v) for v in a.cam.split(',')]
cam = {"type": "orbit", "target": [x, y, z], "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
plays, shots, t = {}, [], 0.0
for i, f in enumerate(a.plays):
    p = json.load(open(f)); k = chr(65 + i); plays[k] = p
    t1 = min(a.t1 if a.t1 is not None else p['duration'], p['duration'])
    length = (t1 - a.t0) / a.speed
    shots.append({"id": k.lower(), "at": round(t, 3), "name": p['id'], "play": k, "remap": [[0, a.t0], [round(length, 3), t1]], "camera": [{"at": 0, "rig": cam}]})
    t += length
words = [{"text": ".", "start": 0.0, "end": 0.01}]
ep = {"id": "motion-review", "title": "motion review", "fps": 30, "voice": a.voice, "words": words, "tail": round(t - 0.01, 3),
      "subtitleHide": [[0, t + 1]], "plays": plays, "shots": shots}
json.dump({"episode": ep}, open(a.out, 'w'))
print(f"{a.out}: {len(shots)} shots, {t:.2f} s")
