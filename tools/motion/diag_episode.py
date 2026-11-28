#!/usr/bin/env python3
"""E2A Motion Engine V4 (2026-11-28): RENDER A props, the compulsory animation diagnostic.

One fixed wide camera, the whole possession, no tactical overlays, no titles, no voice, no music, so cinematic cuts
cannot hide a motion defect. Segment 1 plays in real time, segment 2 repeats the possession at --slow speed.

  python3 tools/motion/diag_episode.py --play template/tactical/plays/<play>.json --out props.json [--slow 0.5]
      [--cam wide|low] [--renderer v33] [--neutral]
Render (landscape, the whole half court): npx remotion render src/index.ts Tactical3DV2 out.mp4 --props=props.json --muted --width=1920 --height=1080
"""
import argparse, json

CAMS = {  # orbit rigs (engine coordinates): target, dist, pitch (0 = straight down), yaw, fov
    "wide": {"type": "orbit", "target": [0.0, 4.6, 0.0], "dist": 15.5, "pitch": 50, "yaw": 0, "fov": 46},
    "low": {"type": "orbit", "target": [0.2, 5.0, 0.6], "dist": 15.5, "pitch": 62, "yaw": 0, "fov": 72},
    "fin": {"type": "orbit", "target": [0.4, 2.4, 1.3], "dist": 7.5, "pitch": 76, "yaw": 70, "fov": 50},
    "nail": {"type": "orbit", "target": [-0.6, 6.4, 1.1], "dist": 7.5, "pitch": 74, "yaw": 160, "fov": 50},
    "side": {"type": "orbit", "target": [0.0, 5.0, 0.6], "dist": 15.0, "pitch": 64, "yaw": -90, "fov": 70},
}

ap = argparse.ArgumentParser()
ap.add_argument("--play", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--slow", type=float, default=0.5)
ap.add_argument("--cam", default="wide")
ap.add_argument("--renderer", default="v33")
ap.add_argument("--neutral", action="store_true", help="neutral grey materials (motion-only read)")
ap.add_argument("--env", default="cinema")
ap.add_argument("--t0", type=float, default=0.0)
ap.add_argument("--t1", type=float)
a = ap.parse_args()
play = json.load(open(a.play))
t0, t1 = a.t0, a.t1 if a.t1 is not None else play["duration"]
real = round(t1 - t0, 3)
slow = round(real / a.slow, 3) if a.slow else 0
cam = [{"at": 0, "rig": CAMS[a.cam]}]
shots = [{"id": "diag-real", "name": "RENDER A real time", "at": 0.0, "play": "A", "remap": [[0, t0], [real, t1]], "camera": cam, "ov3": [], "screen": [],
          "neutral": a.neutral}]
if slow:
    shots.append({"id": "diag-slow", "name": f"RENDER A x{a.slow}", "at": real, "play": "A", "remap": [[0, t0], [slow, t1]], "camera": cam, "ov3": [],
                  "screen": [{"type": "stamp", "text": f"x{a.slow} SLOW", "tone": "gold", "y": 110, "instant": True, "from": 0.0, "to": slow}], "neutral": a.neutral})
ep = {"id": play["id"] + "-diag", "title": "RENDER A", "fps": 30, "voice": "iq02/voice.mix.wav", "tail": 0.0, "autoSfx": False, "pinV2": True, "env": a.env,
      "athleteRenderer": a.renderer, "words": [{"word": " ", "text": " ", "start": round(real + slow - 0.02, 3), "end": round(real + slow, 3)}], "shots": shots, "plays": {"A": play}}
json.dump({"episode": ep}, open(a.out, "w"))
print(json.dumps({"duration": real + slow, "shots": len(shots)}))
