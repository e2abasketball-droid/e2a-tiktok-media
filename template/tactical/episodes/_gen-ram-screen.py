#!/usr/bin/env python3
"""Edit of 'RAM SCREEN: The Screen Before the Screen' (2026-11-13). Every cut, freeze and graphic is anchored
to the real narration (ram-screen.words.json) and to play marks; regenerate after changing gaps or plays.
Shot plan = the owner's brief: hook (live, low 3/4, freeze on O5's half step) / rewind + ram screen /
ball screen + open question / Read A drop / Read B blitz (cut to the same point, same axis) / matched
comparison big back - big up / CTA ending on the opening camera so the loop makes sense."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, 'ram-screen.json')
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
fol = lambda ids, z=1.0, **k: {"follow": ids, "z": z, **k}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
CAM_OPEN = orb([0.2, 7.9, 1.0], 9.8, 79, -36, 44)      # low three-quarter, behind the ball side
CAM_D = orb([0.6, 8.5, 1.0], 9.2, 57, -48)               # the axis where A and B diverge (same in both)
CAM_C = orb([0.1, 7.8, 0.5], 14.0, 46, -15, 40)          # comparison: X5 back (y~5) and X5 up (y~10) in one frame
O4_FACE, O5_FACE = -0.785, -0.427

shots = [
 {"id": "hook", "name": "Hook — live possession, freeze on O5's head start", "at": 0, "play": "A",
  "remap": [[0, 1.1], [1.55, 2.05, "out"], ["the pick.>-0.35", 2.15], ["@end", 2.8, "in"]],
  "camera": [key(0, CAM_OPEN), key(1.6, orb(fol(["O5", "X5", "O4"]), 9.4, 70, -34, 44), "out"),
             key("the pick.>-0.35", orb(fol(["O5", "X5", "O4"]), 9.0, 70, -34, 44), "linear"),
             key("@end", orb(fol(["O5", "O1"], 1.1), 9.5, 72, -40, 44), "inOut")],
  "ov3": [{"type": "ring", "player": "O5", "from": 1.5, "to": "the pick.>-0.3", "pulse": True},
          {"type": "ring", "player": "X5", "from": 1.6, "to": "the pick.>-0.3"},
          {"type": "separation", "a": "O5", "b": "X5", "from": 1.7, "to": "the pick.>-0.3"}],
  "screen": [{"type": "freeze", "label": "FREEZE", "from": 1.6, "to": "the pick.>-0.3"},
             {"type": "title", "lines": ["BEFORE", "THE PICK"], "gold": [1], "from": "before-0.05", "to": "@end", "y": 260, "size": 124}],
  "sfx": [{"at": 0, "name": "whoosh", "volume": 0.1}, {"at": 1.6, "name": "impact", "volume": 0.08}]},
 {"id": "reveal", "name": "Rewind + the first screen (ram)", "at": "Rewind.-0.12", "play": "A",
  "remap": [[0, 2.8], [0.55, 0.35, "inOut"], ["Four", 0.95], ["screens", 1.2], ["defender.>", 1.62], ["head start>", 2.5], ["@end", 2.95]],
  "camera": [key(0, orb([-0.6, 7.0, 1.1], 9.5, 72, -40, 44)), key("Four-0.3", orb([-2.3, 3.7, 0.4], 11.0, 50, -38), "inOut"),
             key("head start", orb([-1.1, 5.4, 0.4], 12.0, 50, -42), "linear"), key("@end", orb([0.2, 7.6, 0.6], 12.0, 52, -46), "inOut")],
  "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": O4_FACE, "from": "screens", "to": "@end"},
          {"type": "ring", "player": "X5", "from": "big's", "to": "@end"},
          {"type": "route", "player": "O5", "t0": 0.85, "t1": 3.05, "draw": 1.2, "from": "Now Five", "to": "@end"},
          {"type": "separation", "a": "O5", "b": "X5", "from": "head start", "to": "@end"}],
  "screen": [{"type": "rewind", "from": 0, "to": 0.55},
             {"type": "title", "lines": ["RAM SCREEN"], "gold": [0], "sub": "The screen before the screen", "from": "Four", "to": "@end", "y": 250, "size": 116},
             {"type": "pin", "player": "O4", "text": "1 · OFF-BALL SCREEN", "from": "screens", "to": "@end", "z": 0, "dy": 70, "size": 44}],
  "sfx": [{"at": 0, "name": "reverse_cymbal", "volume": 0.14}, {"at": "screens", "name": "tick", "volume": 0.17}]},
 {"id": "ballscreen", "name": "Second screen — the open question", "at": "Five gets-0.15", "play": "A",
  "remap": [[0, 2.72], ["first.>", 3.1, "out"], ["Now watch", 3.12], ["@end", 3.14]],
  "camera": [key(0, orb([0.3, 8.0, 0.8], 11.0, 52, -46)), key("first.>", CAM_D, "out"), key("@end", {**CAM_D, "dist": 8.6}, "linear")],
  "ov3": [{"type": "screen", "player": "O5", "n": 2, "facing": O5_FACE, "from": "first-0.2", "to": "@end"},
          {"type": "ring", "player": "O5", "from": 0, "to": "Now watch"},
          {"type": "ring", "player": "X5", "pulse": True, "from": "his defender", "to": "@end"}],
  "screen": [{"type": "pin", "player": "O5", "text": "2 · BALL SCREEN", "from": "gets", "to": "@end", "dy": -90, "size": 44},
             {"type": "freeze", "label": "FREEZE", "from": "Now watch", "to": "@end"},
             {"type": "pin", "player": "X5", "text": "X5", "tone": "red", "from": "his defender", "to": "@end", "size": 48}],
  "sfx": [{"at": "his defender", "name": "tick", "volume": 0.17}]},
 {"id": "readA", "name": "Read A — drop: the big sinks, the guard pulls up", "at": "First look-0.15", "play": "A",
  "remap": [[0, 3.05], ["drops.>", 4.0], ["pull-0.12", 4.1], ["@end-0.9", 5.85], ["@end", 6.3]],
  "camera": [key(0, CAM_D), key("The big", orb(fol(["O1", "X5"]), 9.5, 60, -62), "inOut"),
             key("pull-0.12", orb(fol(["O1", "X5"]), 9.0, 64, -40), "inOut"),
             key("up.>-0.1", orb([-0.6, 5.6, 1.6], 9.6, 68, -14, 44), "inOut"),
             key("up.>+0.55", orb([-0.5, 4.4, 2.0], 9.0, 70, 10, 44), "inOut"), key("@end", orb([-0.3, 3.4, 2.3], 8.4, 72, 8, 44), "linear")],
  "ov3": [{"type": "route", "player": "X1", "t0": 3.1, "t1": 4.5, "trail": True, "width": 0.12, "from": 0, "to": "drops.>"},
          {"type": "ring", "player": "X5", "from": "The big", "to": "pull"},
          {"type": "separation", "a": "X5", "b": "O1", "from": "drops-0.2", "to": "pull+0.3"},
          {"type": "ring", "player": "O1", "from": "room", "to": "up.>"}],
  "screen": [{"type": "title", "lines": ["DROP", "→ PULL-UP"], "gold": [1], "from": "The big", "to": "up.>+0.9", "y": 260, "size": 112},
             {"type": "freeze", "label": "FREEZE", "from": "drops.>", "to": "pull-0.15"},
             {"type": "stamp", "text": "PULL-UP", "badge": "+2", "from": "up.>+0.95", "to": "@end", "y": 330}],
  "sfx": []},
 {"id": "readB", "name": "Read B — blitz: two on the ball, short roll, layup", "at": "Same setup-0.15", "play": "B",
  "remap": [[0, 2.95], ["This time", 3.06], ["ball.>", 3.97], ["Hit", 4.0], ["short roll.>", 4.4], ["lane", 4.62], ["open.>", 5.35], ["@end", 6.45]],
  "camera": [key(0, CAM_D), key("This time", CAM_D, "linear"), key("jump", orb([-0.3, 10.0, 1.0], 13.0, 55, -30), "inOut"),
             key("short roll.>", orb(fol(["O5", "X5"]), 11.2, 64, -52), "inOut"),
             key("open.>", orb([1.6, 2.6, 1.6], 11.2, 72, -80, 44), "inOut"), key("@end", orb([0.8, 2.3, 1.9], 9.8, 74, -80, 44), "linear")],
  "ov3": [{"type": "ring", "player": "X5", "from": "two defenders", "to": "Hit"},
          {"type": "ring", "player": "X1", "from": "two defenders", "to": "Hit"},
          {"type": "passLane", "src": "O1", "dst": "O5", "from": "Hit", "to": "short roll.>"},
          {"type": "ring", "player": "O5", "from": "Hit", "to": "open.>"},
          {"type": "route", "player": "O5", "t0": 4.45, "t1": 5.35, "trail": True, "from": "lane", "to": "open.>+0.3"},
          {"type": "ring", "player": "X2", "from": "lane+0.3", "to": "open.>"}],
  "screen": [{"type": "title", "lines": ["BLITZ", "→ SHORT ROLL"], "gold": [1], "from": "two defenders", "to": "open.>+0.65", "y": 260, "size": 112},
             {"type": "stamp", "text": "SHORT ROLL", "badge": "+2", "from": "open.>+0.7", "to": "@end", "y": 330}],
  "sfx": []},
 {"id": "cmpA1", "name": "Compare — big back", "at": "Same two-0.15", "play": "A", "remap": [[0, 3.85], ["@end", 4.1]],
  "camera": [key(0, CAM_C)], "ov3": [{"type": "ring", "player": "X5", "from": 0, "to": "@end"}, {"type": "separation", "a": "X5", "b": "O1", "from": 0.1, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["BIG BACK"], "from": 0.05, "to": "@end", "y": 270, "size": 122}], "sfx": [{"at": 0, "name": "whip", "volume": 0.06}]},
 {"id": "cmpB1", "name": "Compare — big up", "at": "two different-0.1", "play": "B", "remap": [[0, 3.82], ["@end", 3.98]],
  "camera": [key(0, CAM_C)], "ov3": [{"type": "ring", "player": "X5", "from": 0, "to": "@end"}, {"type": "ring", "player": "X1", "from": 0, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["BIG UP"], "gold": [0], "from": 0.05, "to": "@end", "y": 270, "size": 122}], "sfx": [{"at": 0, "name": "whip", "volume": 0.06}]},
 {"id": "cmpA2", "name": "Compare — big back (2)", "at": "Watch where-0.1", "play": "A", "remap": [[0, 3.95], ["@end", 4.15]],
  "camera": [key(0, CAM_C)], "ov3": [{"type": "ring", "player": "X5", "from": 0, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["BIG BACK"], "from": 0.05, "to": "@end", "y": 270, "size": 122}], "sfx": [{"at": 0, "name": "whip", "volume": 0.06}]},
 {"id": "cmpB2", "name": "Compare — big up (2)", "at": "goes.>+0.15", "play": "B", "remap": [[0, 3.9], ["@end", 4.0]],
  "camera": [key(0, CAM_C)], "ov3": [{"type": "ring", "player": "X5", "from": 0, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["BIG UP"], "gold": [0], "from": 0.05, "to": "@end", "y": 270, "size": 122}], "sfx": [{"at": 0, "name": "whip", "volume": 0.06}]},
 {"id": "cta", "name": "CTA — both options on the decision frame, camera back to the opening", "at": "You're-0.15", "play": "A",
  "remap": [[0, 3.1], ["@end", 3.1]],
  "camera": [key(0, CAM_C), key("@end", CAM_OPEN, "inOut")],
  "ov3": [{"type": "ring", "player": "X5", "pulse": True, "from": 0, "to": "@end"},
          {"type": "route", "player": "X5", "t0": 3.1, "t1": 4.35, "color": "#E5483A", "draw": 0.5, "from": "drop", "to": "@end"},
          {"type": "route", "player": "X5", "fromPlay": "B", "t0": 3.0, "t1": 3.75, "color": "#FFFFFF", "dashed": True, "draw": 0.5, "from": "blitz?", "to": "@end"}],
  "screen": [{"type": "pin", "player": "X5", "text": "YOU", "tone": "red", "from": "You're", "to": "@end", "size": 50},
             {"type": "scrim", "opacity": 0.35, "from": "Do you-0.1", "to": "@end"},
             {"type": "title", "lines": ["DROP", "OR BLITZ?"], "gold": [1], "from": "Do you-0.05", "to": "@end", "y": 600, "size": 140},
             {"type": "logo", "big": False, "from": "You're the big.>", "to": "@end"}],
  "sfx": [{"at": "Do you", "name": "tick", "volume": 0.15}]},
]
ep["shots"] = shots
ep["keywords"] = ["ram", "screens", "head start", "first", "drops", "pull up", "two defenders", "short roll", "lane", "drop", "blitz"]
ep["subtitleHide"] = []
ep["autoSfx"] = {"bounce": 0.2, "catch": 0.13, "squeak": 0.1, "swish": 0.3, "land": 0.08}
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.08}
ep["music"] = {"src": "tactical/ram/music.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots))
