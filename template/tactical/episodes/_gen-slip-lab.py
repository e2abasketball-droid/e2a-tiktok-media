#!/usr/bin/env python3
"""SLIP vs HEDGE — controlled comparison (master prompt 3D sec. 3 / 6.4 / 11): the SAME play, the SAME fixed camera and
the SAME play-time window rendered twice, once with what a NEW episode gets by default on this branch before today
("current": catch model off, default arena look) and once with today's profile ("new": catchV2 = 2 + env 'academy').
Never delivered as an episode: it feeds comparativa-actual-vs-nuevo.mp4 and the experiment manifest.
  python3 tactical/episodes/_gen-slip-lab.py out_dir   -> out_dir/slip-lab-{current,new}{,-side}.props.json
Shots: 1x from 1.8 to 4.3 s of play (the plant, the slip, the over-the-top pass, the catch, the layup), then the catch
window 2.75-3.45 s again at 0.3x. Camera F34 = frontal three-quarter low from the baseline (hands and ball in frame);
SIDE = lateral (second angle of the same frames)."""
import copy, json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D))
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
play = json.load(open(os.path.join(T, "tactical", "plays", "slip-a-dive.json")))
F34 = {"type": "orbit", "target": [0.7, 4.6, 1.0], "dist": 9.2, "pitch": 68, "yaw": 125, "fov": 42}
SIDE = {"type": "orbit", "target": [0.7, 4.6, 1.1], "dist": 8.6, "pitch": 74, "yaw": -95, "fov": 42}
for cam_id, cam in (("", F34), ("-side", SIDE)):
    for prof in ("current", "new"):
        p = copy.deepcopy(play)
        if prof == "current":
            p.pop("catchV2", None)
        shots = [{"id": "real", "name": f"{prof.upper()} 1x", "at": 0, "play": "A", "remap": [[0, 1.8], [2.5, 4.3]],
                  "camera": [{"at": 0, "rig": cam}], "ov3": [], "screen": [{"type": "hud", "tag": "1×", "text": prof.upper(), "from": 0.05, "to": 2.45}]},
                 {"id": "slow", "name": f"{prof.upper()} 0.3x", "at": 2.5, "play": "A", "remap": [[0, 2.75], [2.33, 3.45]],
                  "camera": [{"at": 0, "rig": cam}], "ov3": [], "screen": [{"type": "hud", "tag": "0.3×", "text": prof.upper(), "from": 0.05, "to": 2.3}]}]
        ep = {"id": f"slip-lab-{prof}{cam_id}", "title": "Slip lab", "fps": 30, "voice": "tactical/blindpig/voice-v2.wav", "tail": 0,
              "autoSfx": False, "pinV2": True, "shots": shots, "keywords": [], "subtitleHide": [[0, 99]],
              "words": [{"text": "lab", "start": 0, "end": 4.83}], "plays": {"A": p}}
        if prof == "new":
            ep["env"] = "academy"
        f = os.path.join(out, f"slip-lab-{prof}{cam_id}.props.json")
        json.dump({"episode": ep}, open(f, "w"))
        print(f)
