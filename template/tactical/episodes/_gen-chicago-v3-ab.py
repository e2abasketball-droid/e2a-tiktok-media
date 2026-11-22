#!/usr/bin/env python3
"""CHICAGO V3 — PRIVATE diagnostics (never a social episode), owner brief sec. 9 + 13.5:
  chicago-v3-ab.props.json        5-8 s same-camera A/B clip, split screen: TOP = V2 engine/apparel (the V2 TRAIL play,
                                  realism 2), BOTTOM = V3 (the V3 TRAIL play, realism 3: garment3, layup grip, net snap).
                                  Both share the same set (pin-down + DHO) to the hand-off: 3/4 on the pin-down (play
                                  0.8 -> 2.0 at 0.4x) then low 3/4 on the hand-off (2.0 -> 2.95 at 0.25x). No overlays.
  chicago-v3-cloth-ab.props.json  8 apparel checks x 2 (V2 then V3), same camera, same play time, still frames:
                                  front / side / back (O4 planted), sprint (O2 off the pin-down), sudden stop (O2 1-2 stop
                                  behind the arc), cutter turning (O2 turning the corner), hand-off high arms (O1), jumper
                                  landing (O2). V2 = the same V3 play with realism 2 (identical tracks, v2 cloth).
  python3 tactical/episodes/_gen-chicago-v3-ab.py <out_dir>"""
import copy, json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D))
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
L = lambda n: json.load(open(os.path.join(T, "tactical", "plays", f"{n}.json")))
def r2(p):
    q = copy.deepcopy(p); q["realism"] = 2; q["id"] += "-r2"; return q
V2A, V3D, V3U = L("chicago-v2-a-trail"), L("chicago-v3-trail-drive"), L("chicago-v3-under-three")
orb = lambda tg, dist, pitch, yaw, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
base = {"fps": 30, "voice": "tactical/chicago-v2/voice.wav", "tail": 0, "autoSfx": False, "pinV2": True, "env": "cinema", "keywords": [], "subtitleHide": [[0, 99]]}
# ---- A/B clip (split: V2 top, V3 bottom)
CAM34 = orb([-3.9, 5.7, 1.0], 9.6, 68, 62)
SIDE = orb([-2.95, 8.25, 1.0], 5.6, 76, 150)
W1, W2 = (0.8, 2.0, 0.4), (2.0, 2.95, 0.25)
d1, d2 = round((W1[1] - W1[0]) / W1[2], 3), round((W2[1] - W2[0]) / W2[2], 3)
chip = lambda txt, tone, y: {"type": "chip", "text": txt, "tone": tone, "y": y, "from": 0, "to": "@end", "size": 44}
def sh(i, at, w, d, cam):
    return {"id": f"ab{i}", "name": "ab", "at": at, "play": "V2", "remap": [[0, w[0]], [d, w[1]]], "camera": [{"at": 0, "rig": cam}], "ov3": [],
            "split": {"play": "V3", "remap": [[0, w[0]], [d, w[1]]], "camera": [{"at": 0, "rig": cam}]},
            "screen": [chip("V2  (BASELINE)", "red", 40), chip("V3  (GARMENT3 + CONTACTS)", "blue", 1000)]}
shots = [sh(1, 0, W1, d1, CAM34), sh(2, d1, W2, d2, SIDE)]
total = round(d1 + d2, 3)
ep = {**base, "id": "chicago-v3-ab", "title": "Chicago V3 A/B (private)", "shots": shots, "words": [{"text": "lab", "start": 0, "end": total}], "plays": {"V2": V2A, "V3": V3D}}
json.dump({"episode": ep}, open(os.path.join(out, "chicago-v3-ab.props.json"), "w"))
print("ab", total, "s =", round(total * 30), "frames")
# ---- cloth A/B stills: 8 checks, V2 block then V3 block (0.5 s each, still)
fo = lambda pid, yaw, d=3.3, z=1.05, pitch=80: orb({"follow": pid, "z": z, "window": 0.2}, d, pitch, yaw, 36)
CHECKS = [("view 0", "D", "O1", 1.2, 0), ("view 90", "D", "O1", 1.2, 90), ("view 180", "D", "O1", 1.2, 180), ("sprint", "D", "O2", 1.55, 60),
          ("stop", "U", "O2", 2.82, 40), ("turn", "D", "O2", 2.95, 120), ("dho-arms", "D", "O1", 2.47, 20), ("landing", "U", "O2", 3.78, 30)]
shots = []
for k, ver in enumerate(("2", "3")):
    for i, (nm, pl, pid, t, yaw) in enumerate(CHECKS):
        shots.append({"id": f"{nm}-v{ver}", "name": nm, "at": (k * len(CHECKS) + i) * 0.5, "play": pl + ver, "remap": [[0, t], [0.5, t]],
                      "camera": [{"at": 0, "rig": fo(pid, yaw)}], "ov3": [], "screen": []})
ep = {**base, "id": "chicago-v3-cloth-ab", "title": "Chicago V3 cloth A/B (private)", "shots": shots, "words": [{"text": "lab", "start": 0, "end": len(shots) * 0.5}],
      "plays": {"D2": r2(V3D), "D3": V3D, "U2": r2(V3U), "U3": V3U}}
json.dump({"episode": ep}, open(os.path.join(out, "chicago-v3-cloth-ab.props.json"), "w"))
print("cloth frames", [(s["id"], i * 15) for i, s in enumerate(shots)])
