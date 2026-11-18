#!/usr/bin/env python3
"""PISTOL (21) edit, shot for shot on the Spain pick-and-roll method:
  hook      the hand-off and the big already sprinting in.        ONE HANDOFF. / ONE SCREEN.
  setup     basket at the top: dribble to the wing, hand-off, ball screen right away.
  caseA     X2 goes under: he stops behind the screen, push to the shooter.   PULL-UP THREE +3
  caseB     rewind, X2 chases over: the big steps up, freeze, pocket pass, push to the rim.   EASY TWO +2
  takeaway  TWO ACTIONS. / ONE SECOND APART. -> THE DEFENCE / GIVES SOMETHING UP.
  close     scrim, HOW WOULD YOU GUARD IT?, logo."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "pistol.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
SCREEN_FACING = 0.0           # O5 at (3.85, 8.1) faces X2 coming from the wing (+x)
SETUP = orb([3.4, 8.92, 0], 14.5, 62, 0)
SETUP2 = orb([3.6, 8.6, 0], 13.8, 62, 0)
READ = orb([4.2, 7.8, 0], 13.5, 62, -10)     # fit-search: ball, O2, X2, O5, X5 over read A
READ_B = orb([3.7, 7.5, 0], 17.0, 58, -10)   # read B: the roll to (0.95, 4.2) in frame
TAKE = orb([2.6, 6.4, 0], 15.5, 56, 0)
shots = [
 {"id": "hook", "name": "Hook - one hand-off, one screen", "at": 0, "play": "A",
  "remap": [[0, 1.3], ["@end", 2.6]],
  "camera": [key(0, orb([4.6, 8.4, 1.0], 9.0, 54, 0, 46)), key("@end", orb([4.3, 8.4, 0.9], 10.5, 56, -5, 46), "inOut")],
  "ov3": [{"type": "ring", "player": "O1", "from": "One", "to": "@end"},
          {"type": "ring", "player": "O5", "from": "One screen", "to": "@end", "pulse": True}],
  "screen": [{"type": "title", "lines": ["ONE HANDOFF."], "from": 0.05, "to": "One screen-0.05", "y": 270, "size": 110},
             {"type": "title", "lines": ["ONE SCREEN."], "gold": [0], "from": "One screen", "to": "@end", "y": 270, "size": 124}]},
 {"id": "setup", "name": "Setup - dribble to the wing, hand-off, ball screen right away", "at": "The pistol-0.15", "play": "A",
  "remap": [[0, 0.3], ["handoff on", 1.6], ["wing.>", 2.3], ["ball screen", 2.6], ["away.>", 2.8], ["@end", 2.9]],
  "camera": [key(0, SETUP), key("@end", SETUP2, "linear")],
  "ov3": [{"type": "route", "player": "O2", "t0": 0.3, "t1": 2.3, "draw": 1.0, "from": "handoff on", "to": "@end"},
          {"type": "screen", "player": "O5", "n": 1, "facing": SCREEN_FACING, "from": "ball screen-0.2", "to": "@end"},
          {"type": "ring", "player": "X2", "from": "away.>", "to": "@end"}],
  "screen": [{"type": "title", "lines": ["THE PISTOL"], "gold": [0], "sub": "Also called 21", "from": "pistol", "to": "handoff on-0.05", "y": 252, "size": 104},
             {"type": "title", "lines": ["HAND-OFF ON THE WING"], "from": "handoff on", "to": "ball screen-0.05", "y": 252, "size": 88},
             {"type": "title", "lines": ["HAND-OFF ON THE WING", "+ BALL SCREEN"], "gold": [1], "from": "ball screen", "to": "@end", "y": 252, "size": 88}]},
 {"id": "caseA", "name": "Case A - X2 goes under, he stops behind it, pull-up three", "at": "If his-0.1", "play": "A",
  "remap": [[0, 2.8], ["goes under", 3.0], ["under the screen.>", 3.3], ["stops behind", 3.5], ["it.>", 3.73], ["@end", 5.3]],
  "camera": [key(0, READ), key("it.>-0.3", READ), key("Pull-up three.>+0.2", orb([2.6, 8.7, 1.2], 6.8, 60, -5, 46), "inOut"),
             key("@end", orb([2.6, 8.7, 1.3], 6.2, 62, -5, 46), "linear")],
  "ov3": [{"type": "ring", "player": "X2", "from": "goes under", "to": "Pull-up"},
          {"type": "route", "player": "X2", "t0": 2.75, "t1": 3.7, "trail": True, "width": 0.14, "color": "#E5483A", "from": "goes under", "to": "Pull-up"},
          {"type": "screen", "player": "O5", "n": 1, "facing": SCREEN_FACING, "from": 0, "to": "Pull-up"},
          {"type": "route", "player": "O2", "t0": 2.45, "t1": 3.7, "trail": True, "from": "stops behind", "to": "@end"},
          {"type": "ring", "player": "O2", "from": "Pull-up", "to": "@end", "pulse": True},
          {"type": "separation", "a": "O2", "b": "X2", "from": "Pull-up", "to": "@end"}],
  "screen": [{"type": "title", "lines": ["HE GOES UNDER"], "from": "goes under", "to": "Pull-up-0.05", "y": 252, "size": 96},
             {"type": "stamp", "text": "PULL-UP THREE", "badge": "+3", "from": "Pull-up three.>+0.35", "to": "@end", "y": 330}]},
 {"id": "caseB", "name": "Case B - X2 chases over, the big steps up, pocket pass, layup", "at": "If he chases-0.15", "play": "B",
  "remap": [[0, 2.6], ["chases over", 2.9], ["top.>", 3.3], ["big has", 3.6], ["step up.>", 4.7, "out"], ["Pocket", 4.78],
            ["Pocket pass.>", 5.08], ["Easy two", 5.6], ["rim.>", 6.45], ["@end", 6.85]],
  "camera": [key(0, READ_B), key("Pocket pass.>-0.25", READ_B), key("rim.>", orb([0.4, 2.6, 1.2], 6.8, 64, 15, 46), "inOut"),
             key("@end", orb([0.4, 2.4, 1.4], 6.2, 66, 15, 46), "linear")],
  "ov3": [{"type": "ring", "player": "X2", "from": "chases over", "to": "big has"},
          {"type": "route", "player": "X2", "t0": 2.4, "t1": 3.4, "trail": True, "width": 0.14, "color": "#E5483A", "from": "chases over", "to": "big has"},
          {"type": "ring", "player": "X5", "from": "big has", "to": "Pocket"},
          {"type": "route", "player": "O5", "t0": 3.3, "t1": 5.1, "trail": True, "from": "step up.>-0.4", "to": "@end"},
          {"type": "passLane", "src": "O2", "dst": "O5", "from": "Pocket", "to": "Pocket pass.>"},
          {"type": "ring", "player": "O5", "from": "Easy two", "to": "@end", "pulse": True}],
  "screen": [{"type": "rewind", "from": 0, "to": 0.35},
             {"type": "pin", "player": "X2", "text": "CHASES OVER", "tone": "red", "from": "chases over", "to": "big has"},
             {"type": "title", "lines": ["THE BIG STEPS UP"], "from": "big has", "to": "Pocket-0.05", "y": 252, "size": 96},
             {"type": "freeze", "label": "FREEZE", "from": "step up.>-0.25", "to": "Pocket-0.05"},
             {"type": "stamp", "text": "POCKET PASS", "from": "Pocket", "to": "Easy two-0.1", "y": 300},
             {"type": "stamp", "text": "EASY TWO", "badge": "+2", "from": "rim.>-0.2", "to": "@end", "y": 330}]},
 {"id": "takeaway", "name": "Takeaway - two actions, one second apart", "at": "Two actions-0.15", "play": "A",
  "remap": [[0, 2.55], ["@end", 2.7]],
  "camera": [key(0, TAKE), key("@end", TAKE)],
  "ov3": [{"type": "screen", "player": "O5", "n": 1, "facing": SCREEN_FACING, "from": 0, "to": "@end"},
          {"type": "route", "player": "O2", "t0": 2.45, "t1": 3.7, "draw": 0.6, "from": "one second", "to": "@end"},
          {"type": "route", "player": "O5", "fromPlay": "B", "t0": 3.3, "t1": 5.1, "draw": 0.6, "color": "#FFFFFF", "from": "one second", "to": "@end"}],
  "screen": [{"type": "title", "lines": ["TWO ACTIONS.", "ONE SECOND APART."], "gold": [1], "from": 0.05, "to": "The defence-0.05", "y": 252, "size": 92},
             {"type": "title", "lines": ["THE DEFENCE", "GIVES SOMETHING UP."], "gold": [1], "from": "The defence", "to": "@end", "y": 252, "size": 100}]},
 {"id": "close", "name": "CTA", "at": "How-0.15", "play": "A",
  "remap": [[0, 2.7], ["@end", 2.75]],
  "camera": [key(0, TAKE), key("@end", orb([2.6, 6.4, 0], 14.5, 56, 0), "linear")],
  "ov3": [],
  "screen": [{"type": "scrim", "opacity": 0.55, "from": 0, "to": "@end"},
             {"type": "title", "lines": ["HOW WOULD", "YOU GUARD IT?"], "gold": [1], "from": 0.05, "to": "@end", "y": 600, "size": 140},
             {"type": "logo", "big": True, "from": "Follow", "to": "@end"}]},
]
SFX = {"hook": [{"at": 0, "name": "whoosh", "volume": 0.12}, {"at": "One screen", "name": "impact", "volume": 0.09}],
       "setup": [{"at": 0, "name": "reverse_cymbal", "volume": 0.12}, {"at": "handoff on", "name": "tick", "volume": 0.17},
                 {"at": "ball screen", "name": "tick", "volume": 0.17}],
       "caseA": [{"at": "goes under", "name": "whip", "volume": 0.1}, {"at": "Pull-up three.>+0.3", "name": "swish", "volume": 0.16}],
       "caseB": [{"at": 0, "name": "whip", "volume": 0.1}, {"at": "rim.>-0.25", "name": "swish", "volume": 0.16}],
       "takeaway": [{"at": 0, "name": "tick", "volume": 0.17}],
       "close": [{"at": 0, "name": "impact", "volume": 0.08}]}
for sh in shots:
    sh["sfx"] = SFX[sh["id"]]
ep["shots"] = shots
ep["pinV2"] = True
ep["musicDrop"] = "If his"
ep["musicPayoff"] = "Two actions"
ep["keywords"] = ["pistol", "handoff", "ball screen", "goes under", "pull-up three", "chases over", "step up", "pocket pass", "easy two"]
ep["subtitleHide"] = [[0, "The pistol-0.2"], ["How-0.05", "basketball.>+2"]]
ep["music"] = {"src": "tactical/pistol/music-mix.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots))
