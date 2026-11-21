#!/usr/bin/env python3
"""2-3 Zone: side / 3-4 VALIDATION clips (brief sec. 18 item 7): O5 catch at the nail, O4 catch on the baseline cut,
O2's skip release, O3 catch + shot. Half speed, no overlays, no captions; the plays are the reel's plays.
  python3 tactical/episodes/_validate-zona23.py -> zona23-validate.json (render, then strip the audio: -an)"""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
f = lambda ids, z=1.1, w=0.3: {"follow": ids, "z": z, "window": w}
CLIPS = [("v1-o5-catch", "A", 0.70, 1.50, orb(f(["O5"]), 5.0, 80, 90)),
         ("v2-o4-catch", "A", 2.05, 2.85, orb(f(["O4"]), 5.5, 80, 25)),
         ("v3-o2-skip", "B", 0.95, 1.75, orb(f(["O2"]), 5.5, 80, -60)),
         ("v4-o3-catch-shot", "B", 2.30, 3.45, orb(f(["O3"], 1.4), 6.0, 78, 60))]
src = json.load(open(os.path.join(D, "zona23-voice.json")))
ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw", "gapFill")}
ep.update({"id": "zona23-validate", "title": "2-3 Zone validation clips", "branches": {"a": "A", "b": "B", "c": "C"}, "env": "cinema",
           "pinV2": True, "autoSfx": False, "subtitleHide": [[0, 999]], "tail": 0.0})
shots, at = [], 0.0
for cid, pl, t0, t1, cam in CLIPS:
    d = round(2 * (t1 - t0), 3)
    shots.append({"id": cid, "name": f"{cid}: {pl} {t0} -> {t1} at 0.5x", "at": round(at, 4), "play": pl, "branch": pl.lower(),
                  "remap": [[0, t0], [d, t1]], "camera": [{"at": 0, "rig": cam}], "ov3": [], "screen": []})
    at += d
ep["shots"] = shots
json.dump(ep, open(os.path.join(D, "zona23-validate.json"), "w"), indent=1)
json.dump([{"text": "x", "start": 0, "end": round(at - 0.001, 3)}], open(os.path.join(D, "zona23-validate.words.json"), "w"))
print(len(shots), "clips", round(at, 2), "s", [s["at"] for s in shots])
