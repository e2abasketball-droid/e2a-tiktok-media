#!/usr/bin/env python3
"""E2A Realism V3.3 (2026-11-22) — props of the V3.3 TEST renders (never a social episode, muted, no voice spend).
Same play / camera / FOV / lights / grade / clock inside each comparison; only the athlete switches change.
  python3 tactical/episodes/_gen-realism-v3-3.py <out_dir>
writes <out_dir>/rv33-*.props.json:
  contact      01 V3.2 vs V3.3, 2 stacked panels, realism-v3-2-abc (same choreography the V3.2 A/B/C used), close follow
  debug        02 V3.3 contact / ball-state overlay (feet, palms, ball halo) on the catch, shot and dribble
  motion       03 motion only: neutral grey, the same V3.2 mesh, V3.2 vs V3.3 motion (2 panels)
  slow         04 V3.3 slow motion 0.5x: catch, gather, jump shot, landing
  trio         06 V3.3 three players (realism-v3-2-trio), wide fixed camera (same as V3.2 06)
  full-raw     07 5v5 (realism-v3-3-5v5), all 10 players V3.3 compiled, wide FIXED camera, no overlay
  full-ed      08 the same 5v5 one-take with the E2A editorial layer (palette chips, 2026 logo) - camera unchanged
  bench-10-v33 09 performance (2 s, 10 athletes, same layout as the V3.2 bench)"""
import copy, json, os, sys

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(T, "out", "rv33")
os.makedirs(out, exist_ok=True)
ld = lambda n: json.load(open(os.path.join(T, "tactical", "plays", n + ".json")))
ABC, TRIO, FULL5 = ld("realism-v3-2-abc"), ld("realism-v3-2-trio"), ld("realism-v3-3-5v5")
DUR = ABC["duration"]
orb = lambda tg, dist, pitch, yaw, fov=34: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
base = {"fps": 30, "voice": "tactical/realism-v3-3/silence.mp3", "tail": 0, "autoSfx": False, "pinV2": True, "env": "cinema", "keywords": [],
        "subtitleHide": [[0, 999]], "gradeBottom": 0.25}
chip = lambda txt, tone, y, size=40, a=0, z="@end": {"type": "chip", "text": txt, "tone": tone, "y": y, "from": a, "to": z, "size": size}
PCAM = orb({"follow": "O1", "z": 1.3, "window": 0.6}, 5.0, 86, -62, 38)  # = V3.2 A/B/C panel camera
FULLR = lambda d: [[0, 0], [d, d]]
# 5v5: one wide FIXED camera over the strong side + top (the whole set, the corner O3 and the weak wing O5 in frame)
CAM5 = orb([0.3, 6.0, 0.5], 26.5, 40, 0, 48)  # behind the offence, rim at the top (stills check 2026-11-22)


def write(name, ep):
    json.dump({"episode": ep}, open(os.path.join(out, f"rv33-{name}.props.json"), "w"))


def panels_ep(name, title, panels, chips, play=ABC, remap=None):
    remap = remap or FULLR(DUR)
    dur = remap[-1][0]
    sh = {"id": name, "name": name, "at": 0, "play": "P", "remap": remap, "camera": [{"at": 0, "rig": PCAM}], "ov3": [],
          "screen": [chip(t, tone, 24 + (1920 // len(panels)) * i) for i, (t, tone) in enumerate(chips)], "panels": panels}
    write(name, {**base, "id": f"realism-v3-3-{name}", "title": title, "athleteRenderer": "legacy", "words": [{"text": "test", "start": 0, "end": dur}],
                 "shots": [sh], "plays": {"P": play}})


def single_ep(name, title, cam, sw, play=ABC, remap=None, screen=()):
    remap = remap or FULLR(play["duration"])
    dur = remap[-1][0]
    sh = {"id": name, "name": name, "at": 0, "play": "P", "remap": remap, "camera": [{"at": 0, "rig": cam}], "ov3": [],
          "screen": list(screen), **{k: v for k, v in sw.items() if k != "athleteRenderer"}}
    write(name, {**base, "id": f"realism-v3-3-{name}", "title": title, "athleteRenderer": sw.get("athleteRenderer", "legacy"),
                 "words": [{"text": "test", "start": 0, "end": dur}], "shots": [sh], "plays": {"P": play}})


cam = [{"at": 0, "rig": PCAM}]
P = lambda **k: {"play": "P", "remap": FULLR(DUR), "camera": cam, **k}
SW = {"athleteRenderer": "v33"}
panels_ep("contact", "Realism V3.3 contact V3.2 vs V3.3", [P(athleteRenderer="v32"), P(athleteRenderer="v33")], [("V3.2", "blue"), ("V3.3", "gold")])
single_ep("debug", "Realism V3.3 contact debug", orb({"follow": "O1", "z": 1.0, "window": 0.6}, 5.0, 82, -62, 36), {**SW, "debug32": True},
          screen=[chip("V3.3  DEBUG", "gold", 40)])
panels_ep("motion", "Realism V3.3 motion only", [P(athleteRenderer="v32", neutral=True), P(athleteRenderer="v33", neutral=True)],
          [("MOTION V3.2", "blue"), ("MOTION V3.3", "gold")])
single_ep("slow", "Realism V3.3 slow motion catch and jump shot", orb({"follow": "O1", "z": 1.2, "window": 0.5}, 3.8, 86, -62, 34), SW,
          remap=[[0, 4.4], [10.2, 9.5]], screen=[chip("V3.3  0.5x", "gold", 40)])
single_ep("trio", "Realism V3.3 three players", orb([3.1, 5.8, 1.4], 12.0, 76, 22, 50), SW, play=TRIO, screen=[chip("V3.3  O1 / O2 / X2", "gold", 40)])
single_ep("full-raw", "Realism V3.3 5v5 raw", CAM5, SW, play=FULL5, screen=[])
M = FULL5["marks"]
ed = [{"type": "title", "lines": ["CHICAGO", "UNDER → THREE"], "gold": [1], "from": 0.0, "to": 2.6, "y": 210, "size": 84},
      chip("BALL UP · 5 ON 5", "blue", 1700, 46, 0.3, 3.4),
      chip("PIN-DOWN", "gold", 230, 56, M["pindown"] - 0.1, M["handoff"] - 0.2),
      chip("HANDOFF", "gold", 230, 56, M["handoff"] - 0.2, M["gather"]),
      chip("X2 GOES UNDER", "red", 1700, 46, M["fork"], M["release"]),
      chip("THREE", "gold", 230, 64, M["release"] - 0.1, M["make"] + 0.6),
      chip("BOX OUT", "blue", 1700, 46, M["make"] - 0.2, 10.4),
      {"type": "logo", "y": 1480, "width": 240, "from": 9.6, "to": "@end"}]
single_ep("full-ed", "Realism V3.3 5v5 editorial", CAM5, SW, play=FULL5, screen=ed)
# performance bench: 10 compiled athletes (the 5v5 play itself), 2 s window
sh = {"id": "bench", "name": "bench", "at": 0, "play": "P", "remap": [[0, 5.0], [2.0, 7.0]], "camera": [{"at": 0, "rig": CAM5}], "ov3": [], "screen": []}
write("bench-10-v33", {**base, "id": "realism-v3-3-bench-10-v33", "title": "bench", "athleteRenderer": "v33", "words": [{"text": "b", "start": 0, "end": 2.0}],
                       "shots": [sh], "plays": {"P": FULL5}})
write("bench-10-v32", {**base, "id": "realism-v3-3-bench-10-v32", "title": "bench", "athleteRenderer": "v32", "words": [{"text": "b", "start": 0, "end": 2.0}],
                       "shots": [dict(sh)], "plays": {"P": FULL5}})
print("props in", out)
