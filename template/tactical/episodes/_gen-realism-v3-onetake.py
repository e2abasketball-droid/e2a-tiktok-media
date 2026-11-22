#!/usr/bin/env python3
"""E2A Realism V3 (2026-11-22) — props of the ONE CONTINUOUS TAKE test renders (TEST, never a social episode).
Same play (tactical/plays/realism-v3-onetake.json), same cameras, same lights for both renderers; only the episode flag
`athleteRenderer` changes ('legacy' = the production E2A player e2a-player-v1 + Realism V2/V3 apparel, 'v3' = AthleteV3).
  python3 tactical/episodes/_gen-realism-v3-onetake.py <out_dir>
writes <out_dir>/rv3-{legacy,v3}.props.json (12.5 s, lateral 3/4 at human height, one take, no cut),
       <out_dir>/rv3-sbs.props.json (split: LEGACY top / V3 bottom, same clock, same camera),
       <out_dir>/rv3-hero-{legacy,v3}.props.json (close jersey / arm camera, 12.5 s),
       <out_dir>/rv3-close-{legacy,v3}.props.json + rv3-sbs-close.props.json (closer 3/4, body ~60 % of the height) and
       <out_dir>/rv3-bench-{1,2,5,10}.props.json (render benchmark: n athletes, 60 frames, v3)."""
import copy, json, os, sys

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(T, "out", "rv3")
os.makedirs(out, exist_ok=True)
PLAY = json.load(open(os.path.join(T, "tactical", "plays", "realism-v3-onetake.json")))
DUR = PLAY["duration"]
orb = lambda tg, dist, pitch, yaw, fov=34: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
# lateral 3/4 at human height (camera ~1.45 m above the floor), following O1 with a 0.8 s window (weight, no step jitter)
SIDE = orb({"follow": "O1", "z": 1.05, "window": 0.8}, 8.6, 84, -68)
HERO = orb({"follow": "O1", "z": 1.25, "window": 0.5}, 3.6, 82, -58, 32)
base = {"fps": 30, "voice": "tactical/chicago-v2/voice.wav", "tail": 0, "autoSfx": False, "pinV2": True, "env": "cinema", "keywords": [],
        "subtitleHide": [[0, 999]], "words": [{"text": "test", "start": 0, "end": DUR}], "gradeBottom": 0.25}


def one(name, renderer, cam, play=PLAY, extra=None):
    sh = {"id": name, "name": name, "at": 0, "play": "P", "remap": [[0, 0], [DUR, DUR]], "camera": [{"at": 0, "rig": cam}], "ov3": [], "screen": []}
    if extra:
        sh.update(extra)
    ep = {**base, "id": f"realism-v3-{name}", "title": f"Realism V3 test {name}", "athleteRenderer": renderer, "shots": [sh], "plays": {"P": play}}
    json.dump({"episode": ep}, open(os.path.join(out, f"rv3-{name}.props.json"), "w"))


one("legacy", "legacy", SIDE)
one("v3", "v3", SIDE)
# second pass (2026-11-22): a CLOSER same-camera 3/4 (full body ~60 % of the frame height) so the A/B reads on a phone
CLOSE = orb({"follow": "O1", "z": 0.98, "window": 0.6}, 5.3, 84, -62, 34)
one("close-legacy", "legacy", CLOSE)
one("close-v3", "v3", CLOSE)
one("sbs-close", "legacy", CLOSE, extra={"split": {"play": "P", "remap": [[0, 0], [DUR, DUR]], "camera": [{"at": 0, "rig": CLOSE}], "athleteRenderer": "v3"},
                                         "screen": [{"type": "chip", "text": "LEGACY", "tone": "red", "y": 40, "from": 0, "to": "@end", "size": 46},
                                                    {"type": "chip", "text": "V3", "tone": "blue", "y": 1000, "from": 0, "to": "@end", "size": 46}]})
one("hero-legacy", "legacy", HERO)
one("hero-v3", "v3", HERO)
chip = lambda txt, tone, y: {"type": "chip", "text": txt, "tone": tone, "y": y, "from": 0, "to": "@end", "size": 46}
one("sbs", "legacy", SIDE, extra={"split": {"play": "P", "remap": [[0, 0], [DUR, DUR]], "camera": [{"at": 0, "rig": SIDE}], "athleteRenderer": "v3"},
                                  "screen": [chip("LEGACY", "red", 40), chip("V3", "blue", 1000)]})
# benchmark: n copies of the athlete side by side (same motion, offset tracks), wide fixed camera, 2 s
for n in (1, 2, 5, 10):
    p = copy.deepcopy(PLAY)
    p["id"] = f"realism-v3-bench-{n}"
    p["players"] = []
    p["tracks"] = {}
    p["actions"] = {}
    for k in range(n):
        pid = f"O{k + 1}" if k < 5 else f"X{k - 4}"
        p["players"].append({"id": pid, "team": "O" if k < 5 else "X", "role": "bench copy"})
        dx, dy = (k % 5) * 1.6 - 3.2, (k // 5) * 2.4
        p["tracks"][pid] = [[w[0], round(w[1] + dx + 3.0, 3), round(w[2] + dy, 3)] for w in PLAY["tracks"]["O1"]]
        # face / catch targets name O2 (absent with n = 1): the copies keep only the actions without a player target
        p["actions"][pid] = [x for x in PLAY["actions"]["O1"] if not isinstance(x.get("face"), str)]
    p["ball"] = [{"type": "hold", "player": "O1", "from": 0, "to": DUR, "dribble": True, "hand": 1}]
    sh = {"id": "bench", "name": "bench", "at": 0, "play": "P", "remap": [[0, 1.0], [2.0, 3.0]],
          "camera": [{"at": 0, "rig": orb([-1.0, 5.8, 1.0], 17, 72, 60, 40)}], "ov3": [], "screen": []}
    for r in ("legacy", "v3"):
        ep = {**base, "id": f"realism-v3-bench-{n}-{r}", "title": "bench", "athleteRenderer": r, "words": [{"text": "b", "start": 0, "end": 2.0}],
              "shots": [sh], "plays": {"P": p}}
        json.dump({"episode": ep}, open(os.path.join(out, f"rv3-bench-{n}-{r}.props.json"), "w"))
print("props in", out, "duration", DUR, "s =", round(DUR * 30), "frames")
