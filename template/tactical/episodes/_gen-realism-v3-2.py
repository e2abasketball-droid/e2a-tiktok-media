#!/usr/bin/env python3
"""E2A Realism V3.2 (2026-11-22) — props of the V3.2 TEST renders (never a social episode, no audio).
Same play / camera / FOV / lights / grade / clock for every generation in a comparison; only the athlete switches change
(athleteRenderer legacy | v31 | v32, athleteMotion engine | v31 | v32, athleteMesh v31 | v32, neutral, debug32).
  python3 tactical/episodes/_gen-realism-v3-2.py <out_dir>
writes <out_dir>/rv32-*.props.json:
  abc            A/B/C 12.5 s, 3 stacked panels LEGACY / V3.1 / V3.2 (same choreography, events, camera, lights) = Test C
  testA          Motion only: neutral grey materials, the SAME V3.2 mesh, motion engine / V3.1 / V3.2 (3 panels)
  testB          Character & cloth: the SAME V3.2 motion, mesh + cloth V3.1 / V3.2 (2 panels)
  slow-run       cloth slow motion 0.5x, close: run, cut, 1-2 stop, catch, pivot (play 1.5 -> 5.9 s)
  slow-jump      cloth slow motion 0.5x, close: gather, jump shot, landing (play 7.2 -> 9.5 s)
  side           side view of the catch and shoot (play 4.3 -> 9.7 s), shooting side
  trio           3-player interaction (realism-v3-2-trio): pass, V-cut, catch, brake, shot, chase + closeout, wide
  debug          contact / ball-state debug overlay (feet discs, palms, ball halo) on the catch and shoot
  stills-*       1-frame gates are rendered from these props with --frames (see produccion/realism-v3-2/QA.md)
  bench-{1,10}-v32  performance (2 s, n athletes, V3.2), same layout as the V3.1 bench."""
import copy, json, os, sys

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(T, "out", "rv32")
os.makedirs(out, exist_ok=True)
PLAY = json.load(open(os.path.join(T, "tactical", "plays", "realism-v3-2-abc.json")))
TRIO = json.load(open(os.path.join(T, "tactical", "plays", "realism-v3-2-trio.json")))
DUR = PLAY["duration"]
orb = lambda tg, dist, pitch, yaw, fov=34: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
base = {"fps": 30, "voice": "tactical/chicago-v2/voice.wav", "tail": 0, "autoSfx": False, "pinV2": True, "env": "cinema", "keywords": [],
        "subtitleHide": [[0, 999]], "gradeBottom": 0.25}
chip = lambda txt, tone, y: {"type": "chip", "text": txt, "tone": tone, "y": y, "from": 0, "to": "@end", "size": 40}
# a panel is 1080 x 640 (3 panels): a close 3/4 follow, the full body ~60 % of the panel height, room for the jump
PCAM = orb({"follow": "O1", "z": 1.3, "window": 0.6}, 5.0, 86, -62, 38)  # head room for the jump shot apex
FULL = [[0, 0], [DUR, DUR]]


def write(name, ep):
    json.dump({"episode": ep}, open(os.path.join(out, f"rv32-{name}.props.json"), "w"))


def panels_ep(name, title, panels, chips, play=PLAY, remap=FULL, renderer="legacy"):
    dur = remap[-1][0]
    sh = {"id": name, "name": name, "at": 0, "play": "P", "remap": remap, "camera": [{"at": 0, "rig": PCAM}], "ov3": [],
          "screen": [chip(t, tone, 24 + (1920 // len(panels)) * i) for i, (t, tone) in enumerate(chips)], "panels": panels}
    write(name, {**base, "id": f"realism-v3-2-{name}", "title": title, "athleteRenderer": renderer, "words": [{"text": "test", "start": 0, "end": dur}],
                 "shots": [sh], "plays": {"P": play}})


def single_ep(name, title, cam, sw, play=PLAY, remap=FULL, chips=()):
    dur = remap[-1][0]
    sh = {"id": name, "name": name, "at": 0, "play": "P", "remap": remap, "camera": [{"at": 0, "rig": cam}], "ov3": [],
          "screen": [chip(t, tone, y) for t, tone, y in chips], **{k: v for k, v in sw.items() if k != "athleteRenderer"}}
    write(name, {**base, "id": f"realism-v3-2-{name}", "title": title, "athleteRenderer": sw.get("athleteRenderer", "legacy"),
                 "words": [{"text": "test", "start": 0, "end": dur}], "shots": [sh], "plays": {"P": play}})


cam = [{"at": 0, "rig": PCAM}]
P = lambda **k: {"play": "P", "remap": FULL, "camera": cam, **k}
# 1 / Test C: A/B/C full visual
panels_ep("abc", "Realism V3.2 A/B/C", [P(athleteRenderer="legacy"), P(athleteRenderer="v31"), P(athleteRenderer="v32")],
          [("LEGACY", "red"), ("V3.1", "blue"), ("V3.2", "gold")])
# Test A: motion only (neutral materials, same V3.2 mesh)
panels_ep("testA", "Realism V3.2 Test A motion only",
          [P(athleteRenderer="v32", athleteMotion=m, athleteMesh="v32", neutral=True) for m in ("engine", "v31", "v32")],
          [("MOTION LEGACY", "red"), ("MOTION V3.1", "blue"), ("MOTION V3.2", "gold")])
# Test B: character & cloth (same V3.2 motion)
sh2 = lambda: {"play": "P", "remap": FULL, "camera": [{"at": 0, "rig": orb({"follow": "O1", "z": 1.15, "window": 0.6}, 4.4, 86, -62, 32)}]}
panels_ep("testB", "Realism V3.2 Test B character and cloth",
          [{**sh2(), "athleteRenderer": "v32", "athleteMotion": "v32", "athleteMesh": m} for m in ("v31", "v32")],
          [("MESH + CLOTH V3.1", "blue"), ("MESH + CLOTH V3.2", "gold")])
# slow motion cloth tests (0.5x), close framing
CLOSE = orb({"follow": "O1", "z": 0.95, "window": 0.5}, 3.1, 86, -62, 32)
SW32 = {"athleteRenderer": "v32"}
single_ep("slow-run", "Realism V3.2 cloth slow motion run", CLOSE, SW32, remap=[[0, 1.5], [8.8, 5.9]], chips=[("V3.2  0.5x", "gold", 40)])
single_ep("slow-jump", "Realism V3.2 cloth slow motion jump", orb({"follow": "O1", "z": 1.25, "window": 0.5}, 3.6, 87, -62, 34), SW32,
          remap=[[0, 7.2], [4.6, 9.5]], chips=[("V3.2  0.5x", "gold", 40)])
# side view of the catch and shoot (camera on the shooting-arm side, perpendicular to the shot line)
single_ep("side", "Realism V3.2 side catch and shoot", orb({"follow": "O1", "z": 1.35, "window": 0.7}, 4.8, 88, 110, 34), SW32,
          remap=[[0, 4.3], [5.4, 9.7]], chips=[("V3.2  SIDE", "gold", 40)])
# 3-player interaction (wide fixed camera on the action)
single_ep("trio", "Realism V3.2 three players", orb([3.1, 5.8, 1.4], 12.0, 76, 22, 50), SW32, play=TRIO,
          remap=[[0, 0], [TRIO["duration"], TRIO["duration"]]], chips=[("V3.2  O1 / O2 / X2", "gold", 40)])
# contact / ball-state debug overlay
single_ep("debug", "Realism V3.2 contact debug", orb({"follow": "O1", "z": 1.0, "window": 0.6}, 5.0, 82, -62, 36), {**SW32, "debug32": True},
          remap=[[0, 4.3], [5.4, 9.7]], chips=[("V3.2  DEBUG", "gold", 40)])
# performance bench: n athletes on copies of the O1 track, V3.2 library clip
for n in (1, 10):
    p = copy.deepcopy(PLAY)
    p["id"] = f"realism-v3-2-bench-{n}"
    p["players"], p["tracks"], p["actions"], p["v31clip"], p["v32clip"] = [], {}, {}, {}, {}
    for k in range(n):
        pid = f"O{k + 1}" if k < 5 else f"X{k - 4}"
        p["players"].append({"id": pid, "team": "O" if k < 5 else "X", "role": "bench copy"})
        dx, dy = (k % 5) * 1.6 - 3.2, (k // 5) * 2.4
        p["tracks"][pid] = [[w[0], round(w[1] + dx + 3.0, 3), round(w[2] + dy, 3)] for w in PLAY["tracks"]["O1"]]
        p["actions"][pid] = [x for x in PLAY["actions"]["O1"] if not isinstance(x.get("face"), str)]
        p["v32clip"][pid] = "realism-v3-2-abc:O1"
    p["ball"] = [{"type": "hold", "player": "O1", "from": 0, "to": DUR, "dribble": True, "hand": 1}]
    sh = {"id": "bench", "name": "bench", "at": 0, "play": "P", "remap": [[0, 1.5], [2.0, 3.5]],
          "camera": [{"at": 0, "rig": orb([-1.0, 5.8, 1.0], 17, 72, 60, 40)}], "ov3": [], "screen": []}
    ep = {**base, "id": f"realism-v3-2-bench-{n}-v32", "title": "bench", "athleteRenderer": "v32", "words": [{"text": "b", "start": 0, "end": 2.0}],
          "shots": [sh], "plays": {"P": p}}
    write(f"bench-{n}-v32", ep)
print("props in", out, "duration", DUR, "s")
