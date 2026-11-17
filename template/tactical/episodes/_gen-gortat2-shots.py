#!/usr/bin/env python3
"""GORTAT SCREEN V2 edit (2026-11-17: wing 45 screen to the right, snake to the middle, left-hand attack): the Elevator 3D structure (same Spain editing system: short top titles per beat, red rings on the
defender who decides, gold routes, freeze, rewind, stamps with +2/+3 badges, compare A/B with arrow titles, scrim CTA).
  hook      ball screen, roll, the big seals his own man.   TWO SCREENS. / ONE BIG MAN. / ONE MOVE. -> FREEZE SEALED.
  reveal    overhead start.                                  THE GORTAT SCREEN
  setup     high ball screen, the drop, the guard keeps his man on his back, the big screens his own defender.
  caseA     low man stays home: the seal opens the lane.     LAYUP +2
  caseB     rewind, the low man helps early: kick-out.       OPEN THREE +3
  cmpA/cmpB STAY HOME -> LAYUP / HELP -> CORNER THREE
  read      the rule: set, feet still, no holding.
  close     scrim, HOW WOULD YOU GUARD IT?, logo."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "gortat-screen-v2.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
T = lambda lines, frm, to, gold=(), size=100, **k: {"type": "title", "lines": lines, "gold": list(gold), "from": frm, "to": to, "y": 252, "size": size, **k}
RED = "#E5483A"
HOOK0 = orb([-3.6, 5.6, 0.9], 12.0, 60, 30, 44)
HOOK1 = orb([-2.4, 4.8, 0.9], 11.0, 60, 30, 44)
SETUP = orb([-3.0, 5.2, 0], 13.5, 60, 30)
WIDE = orb([3.0, 4.4, 0], 20.0, 60, 0)
RIM = orb([0.0, 2.9, 1.2], 6.8, 64, 0, 46)
CORNER = orb([6.3, 1.9, 1.2], 7.4, 60, 0, 46)
SEALCAM = orb([-1.0, 4.4, 0.9], 7.6, 70, 0, 44)
shots = [
 {"id": "hook", "name": "Hook - ball screen, roll, the big seals his own man: SEALED", "at": 0, "play": "A",
  "remap": [[0, 1.2], ["big man", 2.3], ["move", 3.3], ["drop coverage", 4.6], ["coverage.>", 5.15], ["@end", 5.2]],
  "camera": [key(0, HOOK0), key("@end", HOOK1, "inOut")],
  "ov3": [{"type": "ring", "player": "O5", "from": "One big", "to": "@end"},
          {"type": "route", "player": "O5", "t0": 3.69, "t1": 5.21, "trail": True, "from": "move", "to": "@end"},
          {"type": "ring", "player": "X5", "color": RED, "from": "coverage.>-0.3", "to": "@end", "pulse": True}],
  "screen": [T(["TWO SCREENS."], 0.05, "One big-0.05", size=118),
             T(["ONE BIG MAN."], "One big", "And one-0.05", gold=(0,), size=118),
             T(["ONE MOVE."], "And one", "coverage.>-0.35", gold=(0,), size=118),
             {"type": "freeze", "label": "FREEZE", "from": "coverage.>-0.3", "to": "@end"},
             T(["SEALED."], "coverage.>-0.3", "@end", size=140)]},
 {"id": "reveal", "name": "Reveal - the Gortat screen", "at": "This is the Gortat-0.15", "play": "A",
  "remap": [[0, 0.0], ["@end", 0.0]],
  "camera": [key(0, orb([-3.2, 5.8, 0], 14.5, 62, 30)), key("@end", SETUP, "inOut")],
  "ov3": [{"type": "ring", "player": "O5", "from": "Gortat", "to": "@end"}, {"type": "ring", "player": "O1", "from": "Gortat", "to": "@end"}],
  "screen": [T(["THE GORTAT SCREEN"], "Gortat", "@end", gold=(0,), size=100, sub="How to break the drop")]},
 {"id": "setup", "name": "Setup - right wing at 45, ball screen to his right, the drop, snake to the middle, the big screens his own man", "at": "Here's how-0.1", "play": "A",
  "remap": [[0, 0.0], ["The big sets", 0.0], ["sets a ball", 0.3], ["uses it", 1.5], ["to his right,>", 2.7], ["drops back", 2.8], ["rim.>", 3.1],
            ["snakes back", 3.2], ["stuck on his back.>", 4.6], ["instead of rolling", 4.7], ["the big turns", 5.0], ["screens his own", 5.2], ["@end", 5.45]],
  "camera": [key(0, SETUP)],
  "ov3": [{"type": "ring", "player": "O1", "from": "The guard starts", "to": "The big sets"},
          {"type": "ring", "player": "O5", "from": "The big sets", "to": "drops back"},
          {"type": "route", "player": "O1", "t0": 1.45, "t1": 3.2, "draw": 1.0, "from": "uses it", "to": "snakes back"},
          {"type": "ring", "player": "X5", "color": RED, "from": "drops back", "to": "snakes back"},
          {"type": "route", "player": "X5", "t0": 1.2, "t1": 1.8, "trail": True, "width": 0.14, "color": RED, "from": "drops back", "to": "snakes back"},
          {"type": "route", "player": "O1", "t0": 3.2, "t1": 4.75, "draw": 1.0, "from": "snakes back", "to": "instead of rolling"},
          {"type": "ring", "player": "X1", "color": RED, "from": "stuck on his back", "to": "instead of rolling"},
          {"type": "route", "player": "O5", "t0": 3.69, "t1": 5.21, "trail": True, "from": "instead of rolling", "to": "@end"},
          {"type": "ring", "player": "X5", "color": RED, "from": "screens his own", "to": "@end", "pulse": True},
          {"type": "ring", "player": "O5", "from": "screens his own", "to": "@end"}],
  "screen": [T(["RIGHT WING,", "45 DEGREES"], "The guard starts", "The big sets-0.05", gold=(1,), size=100),
             T(["BALL SCREEN.", "HE GOES RIGHT"], "The big sets", "drops back-0.05", gold=(1,), size=96),
             T(["HIS DEFENDER", "DROPS"], "drops back", "snakes back-0.05", gold=(1,), size=100),
             T(["SNAKE BACK", "TO THE MIDDLE"], "snakes back", "instead of rolling-0.05", gold=(1,), size=96),
             T(["THE BIG SCREENS", "HIS OWN MAN"], "instead of rolling", "@end", gold=(1,), size=96)]},
 {"id": "caseA", "name": "Case A - the low man stays home: the seal opens the lane, layup", "at": "First scenario-0.15", "play": "A",
  "remap": [[0, 0.6], ["Watch", 1.2], ["attacks the middle", 3.3], ["left hand,>", 4.6], ["seals his man", 5.1], ["his man,>", 5.25, "out"], ["lane opens", 5.3],
            ["up.>", 5.45], ["Drive", 5.5], ["Finish", 6.0], ["Two points", 6.4], ["points.>", 6.9], ["@end", 7.6]],
  "camera": [key(0, SETUP), key("lane opens", SETUP),
             key("Finish", RIM, "inOut"), key("@end", orb([0.0, 2.7, 1.4], 6.2, 66, 0, 46), "linear")],
  "ov3": [
          {"type": "route", "player": "O1", "t0": 3.2, "t1": 6.0, "trail": True, "from": "attacks the middle", "to": "@end"},
          {"type": "ring", "player": "X5", "color": RED, "from": "seals his man", "to": "Drive", "pulse": True},
          {"type": "ring", "player": "O5", "from": "seals his man", "to": "Drive"},
          {"type": "ring", "player": "O1", "from": "Finish", "to": "@end", "pulse": True}],
  "screen": [T(["CASE A:", "HELP STAYS HOME"], "First scenario", "attacks the middle-0.05", gold=(1,), size=96),
             T(["ATTACK THE MIDDLE", "LEFT HAND"], "attacks the middle", "seals his man-0.05", gold=(1,), size=96),
             T(["THE BIG", "SEALS HIS MAN"], "seals his man", "lane opens-0.05", gold=(1,), size=96),
             {"type": "freeze", "label": "FREEZE", "from": "his man,>-0.25", "to": "lane opens-0.05"},
             {"type": "stamp", "text": "LANE OPEN", "from": "lane opens", "to": "Finish-0.1", "y": 300},
             {"type": "stamp", "text": "LAYUP", "badge": "+2", "from": "points.>-0.2", "to": "@end", "y": 330}]},
 {"id": "caseB", "name": "Case B - the low man helps early: kick-out to the corner, open three", "at": "But what if-0.15", "play": "B",
  "remap": [[0, 0.6], ["helps early", 4.4], ["early?>", 4.6], ["Now the lane", 4.7], ["closed.>", 5.1], ["reads the help", 5.2], ["reads the help.>", 5.4],
            ["steps in", 5.5], ["stop the drive,>", 5.8], ["shooter in the corner", 5.83], ["alone.>", 5.86], ["One quick", 5.88],
            ["and the offense", 6.53], ["open three", 6.9], ["three instead.>", 8.0], ["@end", 8.9]],
  "camera": [key(0, WIDE), key("and the offense", WIDE), key("three instead.>-0.5", CORNER, "inOut"), key("@end", orb([6.3, 1.8, 1.4], 6.9, 62, 0, 46), "linear")],
  "ov3": [{"type": "ring", "player": "X4", "color": RED, "from": "corner defender", "to": "One quick"},
          {"type": "route", "player": "X4", "t0": 4.61, "t1": 5.9, "trail": True, "width": 0.14, "color": RED, "from": "steps in", "to": "One quick"},
          {"type": "ring", "player": "O4", "from": "shooter in the corner", "to": "@end", "pulse": True},
          {"type": "passLane", "src": "O1", "dst": "O4", "from": "One quick", "to": "and the offense"}],
  "screen": [{"type": "rewind", "from": 0, "to": 0.35},
             T(["WHAT IF", "HE HELPS EARLY?"], "corner defender", "So the guard-0.05", gold=(1,), size=100),
             T(["READ", "THE HELP"], "So the guard", "shooter in the corner-0.05", gold=(1,), size=100),
             T(["CORNER", "LEFT ALONE"], "shooter in the corner", "One quick-0.05", gold=(1,), size=100),
             {"type": "stamp", "text": "ONE QUICK KICK-OUT", "from": "One quick", "to": "open three-0.1", "y": 300},
             {"type": "stamp", "text": "OPEN THREE", "badge": "+3", "from": "three instead.>-0.2", "to": "@end", "y": 330}]},
 {"id": "cmpA", "name": "Compare A - stay home: layup", "at": "That's what-0.15", "play": "A",
  "remap": [[0, 2.4], ["Stay home", 4.0], ["@end", 6.7]],
  "camera": [key(0, SETUP)],
  "ov3": [{"type": "ring", "player": "X5", "color": RED, "from": "Stay home", "to": "@end"},
          {"type": "route", "player": "O1", "t0": 3.2, "t1": 6.0, "trail": True, "from": "Stay home", "to": "@end"}],
  "screen": [T(["SO DANGEROUS."], 0.05, "Stay home-0.05", gold=(0,), size=110),
             T(["STAY HOME → LAYUP"], "Stay home", "@end", gold=(0,), size=92)]},
 {"id": "cmpB", "name": "Compare B - help too early: corner three", "at": "Help too-0.15", "play": "B",
  "remap": [[0, 3.8], ["@end", 7.6]],
  "camera": [key(0, WIDE)],
  "ov3": [{"type": "ring", "player": "X4", "color": RED, "from": 0, "to": "@end"},
          {"type": "route", "player": "X4", "t0": 4.61, "t1": 5.9, "trail": True, "width": 0.14, "color": RED, "from": 0, "to": "@end"},
          {"type": "ring", "player": "O4", "from": "corner is wide", "to": "@end"}],
  "screen": [T(["HELP → CORNER THREE"], 0.05, "@end", gold=(0,), size=88)]},
 {"id": "read", "name": "The rule - the screen has to be set: feet still, no holding", "at": "Just remember-0.15", "play": "A",
  "remap": [[0, 5.2], ["Feet still", 5.6], ["@end", 5.65]],
  "camera": [key(0, SEALCAM), key("@end", orb([-1.0, 4.4, 0.9], 7.0, 70, 0, 44), "linear")],
  "ov3": [{"type": "ring", "player": "O5", "from": 0, "to": "@end"},
          {"type": "ring", "player": "X5", "color": RED, "from": 0, "to": "@end"}],
  "screen": [T(["THE SCREEN", "HAS TO BE SET."], 0.05, "Feet still-0.05", gold=(1,), size=100),
             T(["FEET STILL.", "NO HOLDING."], "Feet still", "@end", gold=(1,), size=110)]},
 {"id": "close", "name": "CTA", "at": "How would you-0.15", "play": "A",
  "remap": [[0, 5.3], ["@end", 5.35]],
  "camera": [key(0, SETUP), key("@end", orb([-3.0, 5.2, 0], 12.8, 60, 30), "linear")],
  "ov3": [],
  "screen": [{"type": "scrim", "opacity": 0.55, "from": 0, "to": "@end"},
             {"type": "title", "lines": ["HOW WOULD", "YOU GUARD IT?"], "gold": [1], "from": 0.05, "to": "@end", "y": 600, "size": 140},
             {"type": "logo", "big": True, "from": 0.4, "to": "@end"}]},
]
SFX = {"hook": [{"at": 0, "name": "whoosh", "volume": 0.12}, {"at": "One big", "name": "tick", "volume": 0.15},
                {"at": "coverage.>-0.3", "name": "impact", "volume": 0.1}],
       "reveal": [{"at": 0, "name": "reverse_cymbal", "volume": 0.12}],
       "setup": [{"at": "the big turns", "name": "tick", "volume": 0.17}],
       "caseA": [{"at": "seals his man", "name": "whip", "volume": 0.1}, {"at": "points.>-0.25", "name": "swish", "volume": 0.16}],
       "caseB": [{"at": 0, "name": "whip", "volume": 0.1}, {"at": "three instead.>-0.25", "name": "swish", "volume": 0.16}],
       "cmpA": [{"at": "Stay home", "name": "whoosh", "volume": 0.06}],
       "cmpB": [{"at": 0, "name": "whoosh", "volume": 0.06}],
       "read": [{"at": 0, "name": "tick", "volume": 0.17}],
       "close": [{"at": 0, "name": "impact", "volume": 0.08}]}
for sh in shots:
    sh["sfx"] = SFX[sh["id"]]
ep["shots"] = shots
ep["pinV2"] = True
ep["musicDrop"] = "First scenario-0.2"
ep["musicPayoff"] = "That's what-0.3"
ep["keywords"] = ["gortat", "screen", "drop", "seal", "seals", "lane", "help", "corner", "three", "layup", "set", "holding"]
ep["subtitleHide"] = [[0, "This is the Gortat-0.2"], ["How would you-0.05", 99]]
ep["music"] = {"src": "tactical/gortat2/music-mix.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots))
