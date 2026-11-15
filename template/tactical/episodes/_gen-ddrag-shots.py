#!/usr/bin/env python3
"""DOUBLE DRAG - ROLL OR POP? edit (owner brief 2026-11-15 21:45Z), anchored to the real narration
(double-drag.words.json) and to play time. Rigs come from out/flex/fit-search.mts (smallest distance that keeps the
ball, the handler, both screeners and their three defenders inside the safe frame for the whole window) and are
re-checked frame by frame with scripts/frame-fit.mts.
  hook    0-5.7    high 3/4 from half court, play A real time (0.3->6.0): both drags, the split, X4 sinks, the pass to
                   the pop, the three, the net. The frame opens before the ball leaves it.
  replay  5.7-11.3 near-overhead, play A from the screens: 1 and 2 on the screeners, pop, roll, X4's route (slowed).
  readB   11.3-15.1 same high 3/4 frame, play B real time from the same start: X4 stays with the shooter.
  finish  15.1-17.5 lower: the bounce pass inside, the catch, the layup, the late corner help.
  cta     17.5-21.9 back to the split (play A ~1.9-2.4 almost frozen).   ROLL OR POP?
  loop    21.9-end play A 0->0.3 into the first frame."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "double-drag.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=50: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED, GOLD = "#E5483A", "#C9A24D"
T = lambda lines, frm, to, gold=(1,), **k: {"type": "title", "lines": lines, "gold": list(gold), "from": frm, "to": to, "y": 252, "size": 100, **k}
YAW = 10

H = orb([-2.68, 10.47, 0.6], 11.75, 60, YAW)          # play 0.3-4.6, all six + ball
HF = orb([-2.25, 7.17, 0.6], 14.75, 60, YAW)          # play 4.4-5.6, the flight to the net (X5 kept in)
OVER = orb([-1.77, 8.16, 0.6], 17.75, 28, -10, 46)    # near-overhead replay under the title
HB = orb([-2.91, 11.41, 0.6], 11.25, 60, YAW)         # play B 0.3-3.9
LOWB = orb([-0.08, 5.23, 0.6], 9.75, 66, -40)         # play B 3.8-5.4, lower: pass, catch, finish, late help
CTA = orb([-1.85, 9.2, 0.6], 9.75, 60, YAW)           # play A 1.9-2.5 under the question

shots = [
 {"id": "hook", "name": "Hook - two drags, the split, help takes the roll, the pop is open", "at": 0, "play": "A",
  "remap": [[0, 0.3], ["@end", 6.0]],
  "camera": [key(0, H), key(4.1, H), key(4.9, HF, "inOut"), key("@end", HF)],
  "ov3": [], "screen": []},
 {"id": "replay", "name": "Overhead replay - screen order, pop, roll, X4 has to help", "at": 5.7, "play": "A",
  "remap": [[0, 1.0], [1.0, 2.0], [2.5, 2.6], [5.0, 3.3], ["@end", 3.75]],
  "camera": [key(0, OVER)],
  "ov3": [{"type": "ring", "player": "O4", "color": GOLD, "from": 0.1, "to": 1.6},
          {"type": "route", "player": "O4", "t0": 1.95, "t1": 2.8, "trail": True, "color": GOLD, "from": 0.6, "to": 2.2},
          {"type": "ring", "player": "O5", "color": GOLD, "from": 1.7, "to": 3.2},
          {"type": "route", "player": "O5", "t0": 2.25, "t1": 3.3, "trail": True, "color": GOLD, "from": 1.9, "to": 3.4},
          {"type": "route", "player": "X4", "t0": 2.2, "t1": 3.1, "trail": True, "color": RED, "from": 3.4, "to": "@end"}],
  "screen": [T(["DOUBLE DRAG"], 0, "@end", gold=(0,)),
             {"type": "pin", "player": "O4", "text": "1", "tone": "gold", "from": 0.05, "to": 0.85, "size": 44},
             {"type": "pin", "player": "O5", "text": "2", "tone": "gold", "from": 0.05, "to": 0.85, "size": 44}]},
 {"id": "readB", "name": "Variant B - same frame: X4 stays with the shooter", "at": 11.3, "play": "B",
  "remap": [[0, 0.3], ["@end", 4.1]],
  "camera": [key(0, HB)],
  "ov3": [{"type": "ring", "player": "X4", "color": RED, "from": 1.9, "to": 3.3},
          {"type": "ring", "player": "O5", "color": GOLD, "from": 2.4, "to": "@end"}],
  "screen": []},
 {"id": "finish", "name": "Lower - the inside pass, the catch, the finish", "at": 15.1, "play": "B",
  "remap": [[0, 4.1], ["@end", 6.0]],
  "camera": [key(0, LOWB), key("@end", {**LOWB, "dist": 9.5}, "linear")],
  "ov3": [], "screen": [{"type": "pin", "player": "X2", "text": "HELP: LATE", "tone": "red", "from": 0.35, "to": 1.2, "size": 40}]},
 {"id": "cta", "name": "CTA - back to the split: roll or pop?", "at": 17.5, "play": "A",
  "remap": [[0, 1.85], [1.0, 2.25], ["@end", 2.4]],
  "camera": [key(0, CTA), key("@end", {**CTA, "dist": 9.4}, "linear")],
  "ov3": [{"type": "ring", "player": "O4", "color": GOLD, "from": 0.4, "to": "@end"},
          {"type": "ring", "player": "O5", "color": GOLD, "from": 0.4, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["ROLL", "OR POP?"], "gold": [1], "from": 0.5, "to": "@end", "y": 252, "size": 108},
             {"type": "logo", "big": False, "from": "@end-1.3", "to": "@end"}]},
 {"id": "loop", "name": "Loop - the bigs come in, into the first frame", "at": 21.9, "play": "A",
  "remap": [[0, 0.0], ["@end", 0.3]],
  "camera": [key(0, H)], "ov3": [], "screen": []},
]
SFX = {"hook": [{"at": 0.1, "name": "bounce", "volume": 0.09}, {"at": 0.75, "name": "squeak", "volume": 0.08},
                {"at": 3.82, "name": "bounce", "volume": 0.08}, {"at": 5.22, "name": "swish", "volume": 0.16}],
       "replay": [{"at": 1.0, "name": "squeak", "volume": 0.07}],
       "readB": [{"at": 1.6, "name": "squeak", "volume": 0.07}],
       "finish": [{"at": 0.1, "name": "bounce", "volume": 0.09}, {"at": 1.1, "name": "swish", "volume": 0.15}]}
for sh in shots:
    sh["sfx"] = SFX.get(sh["id"], [])
ep["shots"] = shots
ep["tail"] = 3.0
ep["keywords"] = ["Two screens", "split", "Help", "roll", "pop", "OPEN", "pops", "rolls", "has to help", "stays", "shooter"]
# Two screens. | Watch the bigs split. | Help takes the roll. | The pop is OPEN. | First screener pops. | Second screener rolls. |
# Watch the defender | who has to help. | If that defender stays | with the shooter, | look for the roll. | Roll or pop?
ep["subtitleGroups"] = [2, 4, 4, 4, 3, 3, 3, 4, 4, 3, 4, 3]
ep["subtitleBlock"] = True
ep["subtitleHide"] = [[18.0, 40]]
ep["subtitleY"] = 1330
ep["gradeBottom"] = 0.38
ep["autoSfx"] = False
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.05}
ep["music"] = {"src": "tactical/ddrag/music-mix.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots), "words", sum(ep["subtitleGroups"]))
