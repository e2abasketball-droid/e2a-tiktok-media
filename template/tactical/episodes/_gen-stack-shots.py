#!/usr/bin/env python3
"""STACK PICK-AND-ROLL edit, built shot for shot on the Spain pick-and-roll method (most viral E2A reel, 1.28 M IG views):
  hook      tight, the screen and the stacked shooter.            ONE PICK-AND-ROLL. / TWO THREATS.
  setup     wide, basket at the top: ball screen, shooter stacked behind the big, he lifts as the big rolls.
  caseA     X2 helps on the roll: freeze, the shooter is alone, pass it back, push to the shooter.  OPEN THREE +3
  caseB     rewind, X2 stays home: the big rolls alone, bounce pass, push to the rim.          EASY TWO +2
  takeaway  both answers drawn on the same picture.   ONE SCREEN. / TWO THREATS BEHIND IT. -> THE DEFENCE / GIVES SOMETHING UP.
  close     scrim, HOW WOULD YOU GUARD IT?, logo."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "stack-pick-and-roll.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
GOLD = "#C9A24D"
SCREEN_FACING = 3.1416        # O5 at (0.8, 8.2) faces X1 at (0, 8.25)
SETUP0 = orb([0.6, 6.2, 0], 15.5, 48, 0, 40)
SETUP1 = orb([0.4, 6.0, 0], 14.5, 48, 0, 40)
SET_A = orb([0.58, 8.39, 0], 12.0, 54, 0)
SET_B = orb([0.58, 8.6, 0], 13.0, 54, 0)
READ = orb([0.85, 9.85, 0], 13.2, 62, -10)      # fit-search: ball, shooter, roller, X2 over both read windows
shots = [
 {"id": "hook", "name": "Hook - one pick-and-roll, two threats", "at": 0, "play": "A",
  "remap": [[0, 0.3], ["@end", 1.15]],
  "camera": [key(0, orb([0.6, 7.0, 1.0], 9.0, 52, 10, 46)), key("@end", orb([0.6, 6.8, 0.9], 10.5, 55, 0, 46), "inOut")],
  "ov3": [{"type": "ring", "player": "O5", "from": "One", "to": "@end"},
          {"type": "ring", "player": "O2", "from": "Two", "to": "@end", "pulse": True}],
  "screen": [{"type": "title", "lines": ["ONE PICK-AND-ROLL."], "from": 0.05, "to": "Two-0.05", "y": 270, "size": 96},
             {"type": "title", "lines": ["TWO THREATS."], "gold": [0], "from": "Two", "to": "@end", "y": 270, "size": 130}]},
 {"id": "setup", "name": "Setup - ball screen, shooter stacked behind the big", "at": "The stack-0.15", "play": "A",
  "remap": [[0, 0.0], ["ball screen", 0.85], ["shooter hiding", 1.05], ["big.>", 1.2, "inOut"], ["@end", 1.7]],
  "camera": [key(0, SET_A), key("@end", SET_B, "linear")],
  "ov3": [{"type": "screen", "player": "O5", "n": 1, "facing": SCREEN_FACING, "from": "ball screen-0.2", "to": "@end"},
          {"type": "route", "player": "O2", "t0": 1.15, "t1": 2.3, "draw": 1.0, "from": "big.>", "to": "@end"},
          {"type": "route", "player": "O5", "t0": 1.5, "t1": 2.6, "draw": 1.0, "from": "big.>", "to": "@end"},
          {"type": "ring", "player": "X2", "from": "big.>", "to": "@end"}],
  "screen": [{"type": "title", "lines": ["STACK PICK-AND-ROLL"], "gold": [0], "sub": "A shooter stacked behind the screener",
              "from": "stack", "to": "ball screen-0.05", "y": 252, "size": 100},
             {"type": "title", "lines": ["BALL SCREEN", "+ A SHOOTER BEHIND IT"], "gold": [1], "from": "ball screen", "to": "big.>+0.3", "y": 252, "size": 96},
             {"type": "pin", "player": "O2", "text": "SHOOTER", "from": "big.>+0.45", "to": "@end", "dy": -90, "size": 44}]},
 {"id": "caseA", "name": "Case A - X2 helps on the roll, the shooter is alone, pass it back, three", "at": "If the shooter's-0.1", "play": "A",
  "remap": [[0, 1.2], ["helps", 1.45], ["roll.>", 1.95], ["nobody", 2.2], ["covers the shooter.>", 2.4, "out"], ["Pass it", 2.45],
            ["back.>", 3.1], ["Open three", 3.45], ["@end", 5.0]],
  "camera": [key(0, READ), key("back.>-0.3", READ),
             key("Open three.>+0.3", orb([-2.1, 8.0, 1.2], 6.8, 60, -5, 46), "inOut"), key("@end", orb([-2.1, 8.0, 1.3], 6.2, 62, -5, 46), "linear")],
  "ov3": [{"type": "ring", "player": "X2", "from": "helps", "to": "Pass it"},
          {"type": "route", "player": "X2", "t0": 1.25, "t1": 2.2, "trail": True, "width": 0.14, "from": "helps", "to": "Pass it"},
          {"type": "route", "player": "O2", "t0": 1.15, "t1": 2.3, "trail": True, "from": "nobody", "to": "@end"},
          {"type": "passLane", "src": "O1", "dst": "O2", "from": "Pass it", "to": "back.>"},
          {"type": "ring", "player": "O2", "from": "Open three", "to": "@end", "pulse": True},
          {"type": "separation", "a": "O2", "b": "X2", "from": "Open three", "to": "@end"}],
  "screen": [{"type": "pin", "player": "X2", "text": "HELPS ON THE ROLL", "tone": "red", "from": "helps", "to": "Pass it"},
             {"type": "pin", "player": "O2", "text": "ALONE", "from": "nobody", "to": "Pass it"},
             {"type": "freeze", "label": "FREEZE", "from": "covers the shooter.>-0.25", "to": "Pass it-0.05"},
             {"type": "stamp", "text": "PASS IT BACK", "from": "Pass it", "to": "Open three-0.1", "y": 300},
             {"type": "stamp", "text": "OPEN THREE", "badge": "+3", "from": "Open three.>+0.35", "to": "@end", "y": 330}]},
 {"id": "caseB", "name": "Case B - X2 stays home, the big rolls alone, bounce pass, layup", "at": "If he stays-0.15", "play": "B",
  "remap": [[0, 1.2], ["stays", 1.4], ["home.>", 1.75], ["rolls alone", 1.95], ["alone.>", 2.3, "out"], ["Bounce", 2.35],
            ["Bounce pass.>", 3.0], ["Easy two", 3.15], ["rim.>", 3.75], ["@end", 4.4]],
  "camera": [key(0, READ), key("Bounce-0.1", READ), key("rim.>-0.3", orb([0.0, 2.5, 1.2], 6.8, 64, 20, 46), "inOut"), key("@end", orb([0.0, 2.3, 1.4], 6.2, 66, 20, 46), "linear")],
  "ov3": [{"type": "ring", "player": "X2", "from": "stays", "to": "Bounce-0.2"},
          {"type": "route", "player": "O5", "t0": 1.5, "t1": 3.0, "trail": True, "from": "rolls alone", "to": "@end"},
          {"type": "passLane", "src": "O1", "dst": "O5", "from": "Bounce", "to": "Bounce pass.>"},
          {"type": "ring", "player": "O5", "from": "Easy two", "to": "@end", "pulse": True}],
  "screen": [{"type": "rewind", "from": 0, "to": 0.35},
             {"type": "pin", "player": "X2", "text": "STAYS HOME", "tone": "red", "from": "stays", "to": "Bounce-0.2"},
             {"type": "pin", "player": "O5", "text": "ALONE", "from": "rolls alone", "to": "Bounce"},
             {"type": "stamp", "text": "BOUNCE PASS", "from": "Bounce", "to": "Easy two-0.1", "y": 300},
             {"type": "stamp", "text": "EASY TWO", "badge": "+2", "from": "rim.>-0.2", "to": "@end", "y": 330}]},
 {"id": "takeaway", "name": "Takeaway - one screen, two threats behind it", "at": "One screen-0.15", "play": "A",
  "remap": [[0, 1.0], ["@end", 1.1]],
  "camera": [key(0, SETUP1), key("@end", orb([0.4, 6.0, 0], 13.5, 40, 0, 40), "linear")],
  "ov3": [{"type": "screen", "player": "O5", "n": 1, "facing": SCREEN_FACING, "from": 0, "to": "@end"},
          {"type": "route", "player": "O5", "fromPlay": "B", "t0": 1.5, "t1": 3.0, "draw": 0.6, "from": "two threats behind", "to": "@end"},
          {"type": "route", "player": "O2", "t0": 1.15, "t1": 2.3, "draw": 0.6, "color": "#FFFFFF", "from": "two threats behind", "to": "@end"}],
  "screen": [{"type": "title", "lines": ["ONE SCREEN.", "TWO THREATS", "BEHIND IT."], "gold": [1, 2], "from": 0.05, "to": "The defence-0.05", "y": 252, "size": 92},
             {"type": "title", "lines": ["THE DEFENCE", "GIVES SOMETHING UP."], "gold": [1], "from": "The defence", "to": "@end", "y": 252, "size": 100}]},
 {"id": "close", "name": "CTA", "at": "How-0.15", "play": "A",
  "remap": [[0, 1.1], ["@end", 1.15]],
  "camera": [key(0, orb([0.4, 6.0, 0], 13.5, 40, 0, 40)), key("@end", orb([0.4, 6.0, 0], 12.6, 38, 0, 40), "linear")],
  "ov3": [],
  "screen": [{"type": "scrim", "opacity": 0.55, "from": 0, "to": "@end"},
             {"type": "title", "lines": ["HOW WOULD", "YOU GUARD IT?"], "gold": [1], "from": 0.05, "to": "@end", "y": 600, "size": 140},
             {"type": "logo", "big": True, "from": "Follow", "to": "@end"}]},
]
SFX = {"hook": [{"at": 0, "name": "whoosh", "volume": 0.12}, {"at": "Two", "name": "impact", "volume": 0.09}],
       "setup": [{"at": 0, "name": "reverse_cymbal", "volume": 0.12}, {"at": "ball screen", "name": "tick", "volume": 0.17},
                 {"at": "shooter hiding", "name": "tick", "volume": 0.17}],
       "caseA": [{"at": "helps", "name": "whip", "volume": 0.1}, {"at": "Open three.>+0.3", "name": "swish", "volume": 0.16}],
       "caseB": [{"at": 0, "name": "whip", "volume": 0.1}, {"at": "rim.>-0.25", "name": "swish", "volume": 0.16}],
       "takeaway": [{"at": 0, "name": "tick", "volume": 0.17}],
       "close": [{"at": 0, "name": "impact", "volume": 0.08}]}
for sh in shots:
    sh["sfx"] = SFX[sh["id"]]
ep["shots"] = shots
ep["pinV2"] = True
ep["musicDrop"] = "If the shooter's"
ep["musicPayoff"] = "One screen"
ep["keywords"] = ["stack pick-and-roll", "two threats", "ball screen", "shooter", "helps", "nobody covers", "pass it back",
                  "open three", "stays home", "rolls alone", "bounce pass", "easy two"]
ep["subtitleHide"] = [[0, "The stack-0.2"], ["How-0.05", "basketball.>+2"]]
ep["music"] = {"src": "tactical/stack/music-mix.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots))
