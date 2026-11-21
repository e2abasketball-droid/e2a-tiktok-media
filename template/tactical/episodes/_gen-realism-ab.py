#!/usr/bin/env python3
"""REALISM V2 — private A/B (D7, owner brief E2A_REALISM_V2_PROMPT_CLAUDE_CODE.md sec. 10): the SAME Chicago action take
(chicago-v2-a-trail: O2's cut, O4's planted pin-down, X2 trailing, O1's dribble hand-off and the catch), the SAME two
cameras, the SAME play-time windows, no music, no overlays. Rendered twice:
  BASELINE  engine of commit d700987 (git worktree, e2a-player-v1, no realism module)  -> the play's `realism` key is
            ignored by that engine
  V2        this branch with play.realism = 2 (body-frame held ball, trunk contact solver, event continuity, v2 apparel
            + cloth2 secondary motion)
Never an episode for social: it feeds the side-by-side comparison and the close-up stills.
  python3 tactical/episodes/_gen-realism-ab.py out_dir   -> out_dir/realism-ab.props.json (+ realism-ab-stills-*.props.json)
Shots: CAM 3/4 (low, from the right sideline / half-court corner) play 0.35 -> 2.95 s at 0.45x; CAM SIDE (low, close on
the hand-off) play 1.90 -> 2.98 s at 0.22x. Total 10.5 s."""
import copy, json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D))
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
play = json.load(open(os.path.join(T, "tactical", "plays", "chicago-v2-a-trail.json")))
CAM34 = {"type": "orbit", "target": [-3.9, 5.7, 1.0], "dist": 11.0, "pitch": 68, "yaw": 62, "fov": 40}
SIDE = {"type": "orbit", "target": [-2.95, 8.25, 1.05], "dist": 5.4, "pitch": 76, "yaw": 150, "fov": 40}
W1 = (0.35, 2.95, 0.45)
W2 = (1.90, 2.98, 0.22)
d1 = round((W1[1] - W1[0]) / W1[2], 3)
d2 = round((W2[1] - W2[0]) / W2[2], 3)
shots = [{"id": "c34", "name": "3/4", "at": 0, "play": "A", "remap": [[0, W1[0]], [d1, W1[1]]], "camera": [{"at": 0, "rig": CAM34}], "ov3": [], "screen": []},
         {"id": "side", "name": "side", "at": d1, "play": "A", "remap": [[0, W2[0]], [d2, W2[1]]], "camera": [{"at": 0, "rig": SIDE}], "ov3": [], "screen": []}]
total = round(d1 + d2, 3)
ep = {"id": "realism-ab", "title": "Realism V2 A/B", "fps": 30, "voice": "tactical/zona23/pickup-v2-raw.mp3", "tail": 0,
      "autoSfx": False, "pinV2": True, "env": "cinema", "shots": shots, "keywords": [], "subtitleHide": [[0, 99]],
      "words": [{"text": "lab", "start": 0, "end": total}], "plays": {"A": play}}
json.dump({"episode": ep}, open(os.path.join(out, "realism-ab.props.json"), "w"))
print("realism-ab", total, "s =", round(total * 30), "frames")
# close-up stills (1 frame each, 2 s episode): jersey neck/armpit/hem, hand-ball at the hand-off, soles of the screener
CLOSE = {
    "dho": ({"type": "orbit", "target": [-2.95, 8.25, 1.05], "dist": 2.6, "pitch": 80, "yaw": 150, "fov": 38}, [2.30, 2.40, 2.47, 2.53, 2.60]),
    "dho2": ({"type": "orbit", "target": [-2.95, 8.25, 1.05], "dist": 2.6, "pitch": 78, "yaw": 20, "fov": 38}, [2.40, 2.53]),
    "jersey": ({"type": "orbit", "target": {"follow": "O2", "z": 1.35}, "dist": 3.0, "pitch": 80, "yaw": 95, "fov": 36}, [0.5, 1.2, 1.6, 2.0, 2.6, 3.0]),
    "soles": ({"type": "orbit", "target": [-4.32, 4.22, 0.25], "dist": 2.4, "pitch": 74, "yaw": 115, "fov": 40}, [1.0, 1.3, 1.6, 2.0]),
}
for k, (cam, times) in CLOSE.items():
    sh = []
    for i, t in enumerate(times):
        sh.append({"id": f"{k}{i}", "name": k, "at": i * 0.5, "play": "A", "remap": [[0, t], [0.5, t]], "camera": [{"at": 0, "rig": cam}], "ov3": [], "screen": []})
    e2 = dict(ep, id=f"realism-ab-{k}", shots=sh, words=[{"text": "lab", "start": 0, "end": len(times) * 0.5}])
    json.dump({"episode": e2}, open(os.path.join(out, f"realism-ab-{k}.props.json"), "w"))
    print(k, "frames", [i * 15 for i in range(len(times))])
# D5 apparel contact sheet + turntable (v1 vs v2 apparel): one player per pose, camera on him, same frames both engines
#   still: O1 at the top before the action; sprint: O2 off the pin-down; stop: O2 picks up for the pull-up;
#   cut-90: O2 turning the corner round O1; screen: O4 planted; dho: O1 presenting; shot: O2 at the release
fo = lambda pid, d=3.4, pitch=80, yaw=95, z=1.2: {"type": "orbit", "target": {"follow": pid, "z": z}, "dist": d, "pitch": pitch, "yaw": yaw, "fov": 36}
POSES = [("still", "O1", 0.05, 95), ("sprint", "O2", 1.55, 60), ("stop", "O2", 3.56, 40), ("cut90", "O2", 2.75, 120),
         ("screen", "O4", 1.6, 150), ("dho", "O1", 2.47, 20), ("shot", "O2", 3.95, 30)]
TURN = [("turn000", "O4", 1.6, 0), ("turn090", "O4", 1.6, 90), ("turn180", "O4", 1.6, 180), ("turn270", "O4", 1.6, 270)]
sh = []
for i, (nm, pid, t, yaw) in enumerate(POSES + TURN):
    sh.append({"id": nm, "name": nm, "at": i * 0.5, "play": "A", "remap": [[0, t], [0.5, t]], "camera": [{"at": 0, "rig": fo(pid, yaw=yaw)}], "ov3": [], "screen": []})
e2 = dict(ep, id="realism-ab-apparel", shots=sh, words=[{"text": "lab", "start": 0, "end": len(sh) * 0.5}])
json.dump({"episode": e2}, open(os.path.join(out, "realism-ab-apparel.props.json"), "w"))
print("apparel frames", [(nm, i * 15) for i, (nm, *_ ) in enumerate(POSES + TURN)])
