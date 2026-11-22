#!/usr/bin/env python3
"""E2A Realism V3.1 (2026-11-22) — props of the V3.1 test renders (TEST, never a social episode, no audio).
Same play (tactical/plays/realism-v3-1-onetake.json), same camera / FOV / lights / grade / start frame for every
renderer; only the episode (or split) flag `athleteRenderer` changes ('legacy' default vs 'v31').
  python3 tactical/episodes/_gen-realism-v3-1-onetake.py <out_dir>
writes <out_dir>/rv31-{legacy,v31}.props.json (12.5 s, 3/4 follow camera, full body ~65 % of the frame height),
       <out_dir>/rv31-ab.props.json  (LOCKED A/B: split, LEGACY top / V3.1 bottom, same clock, same camera rig),
       <out_dir>/rv31-ab-close.props.json (the same locked A/B, closer: body ~60-70 % of each half),
       <out_dir>/rv31-gate1.props.json (Gate 1: 2 s of the acceleration, v31), <out_dir>/rv31-wide-{legacy,v31}.props.json
       (wide fixed camera, technical diagnostics) and <out_dir>/rv31-bench-{1,10}-{legacy,v31}.props.json (2 s, n athletes)."""
import copy, json, os, sys

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(T, "out", "rv31")
os.makedirs(out, exist_ok=True)
PLAY = json.load(open(os.path.join(T, "tactical", "plays", "realism-v3-1-onetake.json")))
DUR = PLAY["duration"]
orb = lambda tg, dist, pitch, yaw, fov=34: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
# 3/4 follow at human height: full body ~65 % of the frame height (brief V3.1 sec. 8)
CAM = orb({"follow": "O1", "z": 1.18, "window": 0.6}, 5.2, 84, -62, 34)
WIDE = orb([-3.0, 5.2, 1.0], 12.5, 78, -62, 40)
base = {"fps": 30, "voice": "tactical/chicago-v2/voice.wav", "tail": 0, "autoSfx": False, "pinV2": True, "env": "cinema", "keywords": [],
        "subtitleHide": [[0, 999]], "words": [{"text": "test", "start": 0, "end": DUR}], "gradeBottom": 0.25}
chip = lambda txt, tone, y: {"type": "chip", "text": txt, "tone": tone, "y": y, "from": 0, "to": "@end", "size": 46}


def one(name, renderer, cam, play=PLAY, extra=None, remap=None, words=None):
    rm = remap or [[0, 0], [DUR, DUR]]
    sh = {"id": name, "name": name, "at": 0, "play": "P", "remap": rm, "camera": [{"at": 0, "rig": cam}], "ov3": [], "screen": []}
    if extra:
        sh.update(extra)
    ep = {**base, "id": f"realism-v3-1-{name}", "title": f"Realism V3.1 test {name}", "athleteRenderer": renderer, "shots": [sh], "plays": {"P": play}}
    if words:
        ep["words"] = words
    json.dump({"episode": ep}, open(os.path.join(out, f"rv31-{name}.props.json"), "w"))


one("legacy", "legacy", CAM)
one("v31", "v31", CAM)
one("ab", "legacy", CAM, extra={"split": {"play": "P", "remap": [[0, 0], [DUR, DUR]], "camera": [{"at": 0, "rig": CAM}], "athleteRenderer": "v31"},
                                "screen": [chip("LEGACY", "red", 40), chip("V3.1", "blue", 1000)]})
# closer locked A/B (coordinator review): same constraints, the full body ~60-70 % of each half's height
CLOSE = orb({"follow": "O1", "z": 1.1, "window": 0.6}, 3.8, 85, -62, 34)
one("ab-close", "legacy", CLOSE, extra={"split": {"play": "P", "remap": [[0, 0], [DUR, DUR]], "camera": [{"at": 0, "rig": CLOSE}], "athleteRenderer": "v31"},
                                        "screen": [chip("LEGACY", "red", 40), chip("V3.1", "blue", 1000)]})
one("wide-legacy", "legacy", WIDE)
one("wide-v31", "v31", WIDE)
one("gate1", "v31", CAM, remap=[[0, 1.5], [2.0, 3.5]], words=[{"text": "g", "start": 0, "end": 2.0}])
for n in (1, 10):
    p = copy.deepcopy(PLAY)
    p["id"] = f"realism-v3-1-bench-{n}"
    p["players"], p["tracks"], p["actions"], p["v31clip"] = [], {}, {}, {}
    for k in range(n):
        pid = f"O{k + 1}" if k < 5 else f"X{k - 4}"
        p["players"].append({"id": pid, "team": "O" if k < 5 else "X", "role": "bench copy"})
        dx, dy = (k % 5) * 1.6 - 3.2, (k // 5) * 2.4
        p["tracks"][pid] = [[w[0], round(w[1] + dx + 3.0, 3), round(w[2] + dy, 3)] for w in PLAY["tracks"]["O1"]]
        p["actions"][pid] = [x for x in PLAY["actions"]["O1"] if not isinstance(x.get("face"), str)]
        p["v31clip"][pid] = "realism-v3-1-onetake:O1"
    p["ball"] = [{"type": "hold", "player": "O1", "from": 0, "to": DUR, "dribble": True, "hand": 1}]
    sh = {"id": "bench", "name": "bench", "at": 0, "play": "P", "remap": [[0, 1.5], [2.0, 3.5]],
          "camera": [{"at": 0, "rig": orb([-1.0, 5.8, 1.0], 17, 72, 60, 40)}], "ov3": [], "screen": []}
    for r in ("legacy", "v31"):
        ep = {**base, "id": f"realism-v3-1-bench-{n}-{r}", "title": "bench", "athleteRenderer": r, "words": [{"text": "b", "start": 0, "end": 2.0}],
              "shots": [sh], "plays": {"P": p}}
        json.dump({"episode": ep}, open(os.path.join(out, f"rv31-bench-{n}-{r}.props.json"), "w"))
print("props in", out, "duration", DUR, "s")
