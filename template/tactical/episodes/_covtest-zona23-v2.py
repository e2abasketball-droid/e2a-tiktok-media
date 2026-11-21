#!/usr/bin/env python3
"""2-3 Zone V2 GATE (owner V2 brief sec. 16): 7 s before/after coverage test on the SAME scene, camera and timing.
  old = V1 zoneGrid (zone3d.tsx)     new = E2A Dynamic Defensive Coverage (coverage3d.tsx)
  0.0-2.2  B 0.00 frozen: the five areas appear (top 2, then bottom 3), ball in the centre
  2.2-5.8  B 0.00 -> 1.30 at ~0.36x: O1 -> O2 to the wing, the defenders shift, the areas change
  5.8-7.0  B 1.30 -> 1.45
  python3 tactical/episodes/_covtest-zona23-v2.py -> zona23-v2-covtest-{old,new}.json (no audio, no captions)"""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
g1 = import_module("_gen-zona23")
orb = lambda tg, dist, pitch, yaw, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
TOP = orb([0.0, 5.1, 0.0], 22.0, 8, 90)
REMAP = [[0, 0.0], [2.2, 0.0], [5.8, 1.30], [7.0, 1.45]]
OLD = [dict(g1.zg(stagger=0.09, select=["X1", "X3"], selectAt=3.0), **{"from": 0, "to": 7.0, "fin": 0.01})]
NEW = [{"type": "coverage", "mode": "full", "reveal": 0.22, "labels": "all", "labelYaw": 90, "from": 0, "to": 3.1, "fin": 0.01, "fout": 0.3},
       {"type": "coverage", "mode": "active", "active": ["X1", "X3", "X5"], "labels": "active", "labelYaw": 90, "from": 2.8, "to": 7.0, "fin": 0.3}]
src = json.load(open(os.path.join(D, "zona23-voice.json")))
for tag, ov in (("old", OLD), ("new", NEW)):
    ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw", "gapFill")}
    ep.update({"id": f"zona23-v2-covtest-{tag}", "title": f"2-3 Zone V2 coverage gate ({tag})", "branches": {"a": "A", "b": "B", "c": "C"},
               "env": "cinema", "pinV2": True, "autoSfx": False, "subtitleHide": [[0, 999]], "tail": 0.0})
    ep["shots"] = [{"id": "gate", "name": f"coverage gate {tag}", "at": 0, "play": "B", "branch": "b", "remap": REMAP,
                    "camera": [{"at": 0, "rig": TOP}], "ov3": ov, "screen": []}]
    json.dump(ep, open(os.path.join(D, f"zona23-v2-covtest-{tag}.json"), "w"), indent=1)
    json.dump([{"text": "x", "start": 0, "end": 6.999}], open(os.path.join(D, f"zona23-v2-covtest-{tag}.words.json"), "w"))
print("ok")
