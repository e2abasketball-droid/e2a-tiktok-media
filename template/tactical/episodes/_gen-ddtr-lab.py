#!/usr/bin/env python3
"""CURRENT vs NEW, controlled comparison for Double Drag (master prompt 3D sec. 3 / 6.4 / 11): the SAME play
(ddtr-a-roll), the SAME fixed camera, the SAME play-time window, rendered twice:
  current = what a new episode got by default before 2026-11-20 (catch model off, default arena look);
  new     = today's profile (catchV2 = 2 + env 'academy').
Never delivered as an episode; it feeds comparativa/comparativa-actual-vs-nuevo.mp4 and the experiment manifest.
  python3 tactical/episodes/_gen-ddtr-lab.py out_dir   -> out_dir/ddtr-lab-{current,new}.props.json
Shots: 1x from S078 to S132 (pass, catch in stride, layup), then the catch window S092-S104 again at 0.3x.
Camera = the episode's PAY camera (lateral-mid from the ball side), fixed."""
import copy, json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D))
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
play = json.load(open(os.path.join(T, "tactical", "plays", "ddtr-a-roll.json")))
S = lambda n: round(n / 30, 4)
CAM = {"type": "orbit", "target": [-0.6, 3.4, 1.1], "dist": 10.5, "pitch": 64, "yaw": 68, "fov": 44}
for prof in ("current", "new"):
    p = copy.deepcopy(play)
    if prof == "current":
        p.pop("catchV2", None)
    real = S(132) - S(78)
    slow = (S(104) - S(92)) / 0.3
    shots = [{"id": "real", "name": f"{prof.upper()} 1x", "at": 0, "play": "A", "remap": [[0, S(78)], [real, S(132)]],
              "camera": [{"at": 0, "rig": CAM}], "ov3": [], "screen": [{"type": "hud", "tag": "1×", "text": prof.upper(), "from": 0.05, "to": real - 0.05}]},
             {"id": "slow", "name": f"{prof.upper()} 0.3x", "at": real, "play": "A", "remap": [[0, S(92)], [slow, S(104)]],
              "camera": [{"at": 0, "rig": CAM}], "ov3": [], "screen": [{"type": "hud", "tag": "0.3×", "text": prof.upper(), "from": 0.05, "to": slow - 0.05}]}]
    ep = {"id": f"ddtr-lab-{prof}", "title": "Double Drag lab", "fps": 30, "voice": "tactical/ddtr/voice-a.wav", "tail": 0,
          "autoSfx": False, "pinV2": True, "shots": shots, "keywords": [], "subtitleHide": [[0, 99]],
          "words": [{"text": "lab", "start": 0, "end": round(real + slow, 3)}], "plays": {"A": p}}
    if prof == "new":
        ep["env"] = "academy"
    f = os.path.join(out, f"ddtr-lab-{prof}.props.json")
    json.dump({"episode": ep}, open(f, "w"))
    print(f)
