#!/usr/bin/env python3
"""ELEVATOR SCREEN 3D edit: the V2 pilot's story beats, told with the Spain pick-and-roll editing system
(short top titles per beat, red rings/labels on the defender who decides, gold routes, freeze, rewind, stamps with
+3/+2 badges, compare A/B with arrow titles, scrim CTA with the logo).
  hook      the cut through the corridor, the doors close on the chaser.   TWO SCREENS. / ONE TINY GAP. / ONE DECISION. -> FREEZE TRAPPED.
  reveal    overhead start.                         THE ELEVATOR SCREEN
  setup     side by side, narrow gap, the cut, the doors close.
  caseA     he chases: caught behind the screens, freeze, pass on time, catch, shoot.   OPEN THREE +3
  caseB     rewind, the early switch: the screener slips, one quick pass.                LAYUP +2
  cmpA/cmpB CHASE -> OPEN THREE / SWITCH -> SLIP
  read      THE BEST OFFENSES / READ THE DEFENSE.
  close     scrim, HOW WOULD YOU GUARD IT?, logo."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "elevator-3d.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
T = lambda lines, frm, to, gold=(), size=100, **k: {"type": "title", "lines": lines, "gold": list(gold), "from": frm, "to": to, "y": 252, "size": size, **k}
RED = "#E5483A"
HOOK0 = orb([0.0, 6.4, 0.9], 9.0, 60, 0, 44)
HOOK1 = orb([0.0, 6.6, 0.9], 10.0, 60, 0, 44)
SETUP = orb([1.3, 8.0, 0], 13.5, 60, 0)
READ_B = orb([1.5, 5.6, 0], 14.0, 60, -10)
SHOOT = orb([-0.3, 8.4, 1.2], 6.8, 60, -5, 46)
RIM = orb([0.4, 2.6, 1.2], 6.8, 64, 15, 46)
shots = [
 {"id": "hook", "name": "Hook - two screens, one tiny gap, the doors close on the chaser: TRAPPED", "at": 0, "play": "A",
  "remap": [[0, 0.5], ["gap.>", 1.7], ["decision", 2.05], ["defense.>", 2.45], ["@end", 2.5]],
  "camera": [key(0, HOOK0), key("@end", HOOK1, "inOut")],
  "ov3": [{"type": "ring", "player": "O4", "from": "Two", "to": "@end"},
          {"type": "ring", "player": "O5", "from": "Two", "to": "@end"},
          {"type": "route", "player": "O2", "t0": 0.6, "t1": 2.4, "trail": True, "from": "One tiny", "to": "@end"},
          {"type": "ring", "player": "X2", "color": RED, "from": "defense.>-0.3", "to": "@end", "pulse": True}],
  "screen": [T(["TWO SCREENS."], 0.05, "One tiny-0.05", size=118),
             T(["ONE TINY GAP."], (), "One tiny", "And one-0.05", gold=(0,), size=118) if False else T(["ONE TINY GAP."], "One tiny", "And one-0.05", gold=(0,), size=118),
             T(["ONE DECISION."], "And one", "defense.>-0.35", gold=(0,), size=118),
             {"type": "freeze", "label": "FREEZE", "from": "defense.>-0.3", "to": "@end"},
             T(["TRAPPED."], "defense.>-0.3", "@end", size=140)]},
 {"id": "reveal", "name": "Reveal - the elevator screen", "at": "This is the elevator-0.15", "play": "A",
  "remap": [[0, 0.0], ["@end", 0.0]],
  "camera": [key(0, orb([1.5, 7.6, 0], 13.5, 62, 0)), key("@end", SETUP, "inOut")],
  "ov3": [{"type": "ring", "player": "O4", "from": "elevator", "to": "@end"}, {"type": "ring", "player": "O5", "from": "elevator", "to": "@end"}],
  "screen": [T(["THE ELEVATOR SCREEN"], "elevator", "@end", gold=(0,), size=100, sub="Two ways to punish the defense")]},
 {"id": "setup", "name": "Setup - side by side, the narrow gap, the cut, the doors close", "at": "Here's how-0.1", "play": "A",
  "remap": [[0, 0.0], ["cuts straight", 0.7], ["through,>", 1.95], ["close the gap", 1.95], ["doors.>", 2.35], ["@end", 2.4]],
  "camera": [key(0, SETUP)],
  "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": -1.5708, "from": "side by side", "to": "@end"},
          {"type": "screen", "player": "O5", "n": 2, "facing": -1.5708, "from": "side by side", "to": "@end"},
          {"type": "route", "player": "O2", "t0": 0.6, "t1": 2.4, "draw": 1.0, "from": "cuts straight", "to": "@end"},
          {"type": "ring", "player": "O2", "from": "The shooter cuts", "to": "@end"}],
  "screen": [T(["TWO SCREENERS", "SIDE BY SIDE"], "Two players", "narrow-0.05", gold=(1,), size=96),
             T(["A NARROW GAP"], "narrow", "The shooter cuts-0.05", gold=(0,), size=100),
             T(["THE SHOOTER", "CUTS THROUGH"], "The shooter cuts", "close the gap-0.05", gold=(1,), size=96),
             T(["THE DOORS CLOSE"], "close the gap", "@end", gold=(0,), size=100)]},
 {"id": "caseA", "name": "Case A - he chases: caught behind the screens, pass on time, catch, shoot, three", "at": "First scenario-0.15", "play": "A",
  "remap": [[0, 0.45], ["Watch", 0.6], ["escapes", 1.55], ["middle,>", 1.9], ["caught", 2.15], ["behind the screens,>", 2.35, "out"], ["delivers", 2.35],
            ["time.>", 2.6], ["Catch", 2.65], ["Shoot", 3.05], ["Three points", 3.6], ["points.>", 4.15], ["@end", 4.6]],
  "camera": [key(0, SETUP), key("time.>-0.2", SETUP), key("Shoot", SHOOT, "inOut"), key("@end", orb([-0.3, 8.4, 1.3], 6.2, 62, -5, 46), "linear")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": "follows", "to": "delivers"},
          {"type": "route", "player": "X2", "t0": 0.6, "t1": 2.4, "trail": True, "width": 0.14, "color": RED, "from": "follows", "to": "delivers"},
          {"type": "route", "player": "O2", "t0": 0.6, "t1": 2.4, "trail": True, "from": "escapes", "to": "@end"},
          {"type": "passLane", "src": "O1", "dst": "O2", "from": "delivers", "to": "time.>"},
          {"type": "ring", "player": "O2", "from": "Catch", "to": "@end", "pulse": True},
          {"type": "separation", "a": "O2", "b": "X2", "from": "Shoot", "to": "@end"}],
  "screen": [T(["CASE A: HE CHASES"], "First scenario", "caught-0.05", size=96),
             T(["CAUGHT BEHIND", "THE SCREENS"], "caught", "delivers-0.05", gold=(1,), size=96),
             {"type": "freeze", "label": "FREEZE", "from": "behind the screens,>-0.25", "to": "delivers-0.05"},
             {"type": "stamp", "text": "RIGHT ON TIME", "from": "delivers", "to": "Catch-0.1", "y": 300},
             {"type": "stamp", "text": "OPEN THREE", "badge": "+3", "from": "points.>-0.2", "to": "@end", "y": 330}]},
 {"id": "caseB", "name": "Case B - the early switch: the screener slips, one quick pass, layup", "at": "But what if-0.15", "play": "B",
  "remap": [[0, 0.3], ["switches", 0.95], ["early?>", 1.15], ["reads", 1.3], ["switch.>", 1.4], ["jumps", 1.45], ["perimeter,>", 1.7],
            ["slips", 1.8], ["lane.>", 1.95], ["One quick", 2.0], ["quick pass,>", 2.45], ["layup", 2.75], ["instead.>", 3.05], ["@end", 3.9]],
  "camera": [key(0, READ_B), key("quick pass,>-0.2", READ_B), key("instead.>-0.3", RIM, "inOut"), key("@end", orb([0.4, 2.4, 1.4], 6.2, 66, 15, 46), "linear")],
  "ov3": [{"type": "ring", "player": "X5", "color": RED, "from": "switches", "to": "One quick"},
          {"type": "route", "player": "X5", "t0": 1.0, "t1": 2.35, "trail": True, "width": 0.14, "color": RED, "from": "jumps", "to": "One quick"},
          {"type": "route", "player": "O5", "t0": 1.3, "t1": 2.5, "trail": True, "from": "slips", "to": "@end"},
          {"type": "passLane", "src": "O1", "dst": "O5", "from": "One quick", "to": "quick pass,>"},
          {"type": "ring", "player": "O5", "from": "layup", "to": "@end", "pulse": True}],
  "screen": [{"type": "rewind", "from": 0, "to": 0.35},
             T(["WHAT IF", "THEY SWITCH?"], "switches", "slips-0.05", gold=(1,), size=100),
             T(["THE SCREENER SLIPS"], "slips", "One quick-0.05", gold=(0,), size=96),
             {"type": "stamp", "text": "ONE QUICK PASS", "from": "One quick", "to": "layup-0.1", "y": 300},
             {"type": "stamp", "text": "LAYUP", "badge": "+2", "from": "instead.>-0.2", "to": "@end", "y": 330}]},
 {"id": "cmpA", "name": "Compare A - chase the shooter: open three", "at": "That's what-0.15", "play": "A",
  "remap": [[0, 0.6], ["Chase the", 1.4], ["@end", 4.2]],
  "camera": [key(0, SETUP)],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": "Chase the", "to": "@end"},
          {"type": "route", "player": "O2", "t0": 0.6, "t1": 2.4, "trail": True, "from": "Chase the", "to": "@end"}],
  "screen": [T(["SO DANGEROUS."], 0.05, "Chase the-0.05", gold=(0,), size=110),
             T(["CHASE → OPEN THREE"], "Chase the", "@end", gold=(0,), size=92)]},
 {"id": "cmpB", "name": "Compare B - switch too aggressively: the slip", "at": "Switch too-0.15", "play": "B",
  "remap": [[0, 0.9], ["@end", 3.1]],
  "camera": [key(0, READ_B)],
  "ov3": [{"type": "ring", "player": "X5", "color": RED, "from": 0, "to": "@end"},
          {"type": "route", "player": "O5", "t0": 1.3, "t1": 2.5, "trail": True, "from": 0, "to": "@end"}],
  "screen": [T(["SWITCH → SLIP"], 0.05, "@end", gold=(0,), size=96)]},
 {"id": "read", "name": "Read the defense - both answers on one picture", "at": "The best-0.15", "play": "A",
  "remap": [[0, 0.65], ["@end", 0.75]],
  "camera": [key(0, SETUP), key("@end", orb([1.76, 8.3, 0], 14.2, 62, 0), "linear")],
  "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": -1.5708, "from": 0, "to": "@end"},
          {"type": "screen", "player": "O5", "n": 2, "facing": -1.5708, "from": 0, "to": "@end"},
          {"type": "route", "player": "O2", "t0": 0.6, "t1": 2.4, "draw": 0.6, "from": "offenses", "to": "@end"},
          {"type": "route", "player": "O5", "fromPlay": "B", "t0": 1.3, "t1": 2.5, "draw": 0.6, "color": "#FFFFFF", "from": "offenses", "to": "@end"}],
  "screen": [T(["THE BEST OFFENSES", "DON'T JUST RUN IT."], 0.05, "They read-0.05", gold=(), size=92),
             T(["THEY READ", "THE DEFENSE."], "They read", "@end", gold=(1,), size=110)]},
 {"id": "close", "name": "CTA", "at": "How would you-0.15", "play": "A",
  "remap": [[0, 0.75], ["@end", 0.8]],
  "camera": [key(0, orb([1.76, 8.3, 0], 14.2, 62, 0)), key("@end", orb([1.76, 8.3, 0], 13.4, 60, 0), "linear")],
  "ov3": [],
  "screen": [{"type": "scrim", "opacity": 0.55, "from": 0, "to": "@end"},
             {"type": "title", "lines": ["HOW WOULD", "YOU GUARD IT?"], "gold": [1], "from": 0.05, "to": "@end", "y": 600, "size": 140},
             {"type": "logo", "big": True, "from": 0.4, "to": "@end"}]},
]
SFX = {"hook": [{"at": 0, "name": "whoosh", "volume": 0.12}, {"at": "One tiny", "name": "tick", "volume": 0.15},
                {"at": "defense.>-0.3", "name": "impact", "volume": 0.1}],
       "reveal": [{"at": 0, "name": "reverse_cymbal", "volume": 0.12}],
       "setup": [{"at": "close the gap", "name": "tick", "volume": 0.17}],
       "caseA": [{"at": "caught", "name": "whip", "volume": 0.1}, {"at": "points.>-0.25", "name": "swish", "volume": 0.16}],
       "caseB": [{"at": 0, "name": "whip", "volume": 0.1}, {"at": "instead.>-0.25", "name": "swish", "volume": 0.16}],
       "cmpA": [{"at": "Chase the", "name": "whoosh", "volume": 0.06}],
       "cmpB": [{"at": 0, "name": "whoosh", "volume": 0.06}],
       "read": [{"at": 0, "name": "tick", "volume": 0.17}],
       "close": [{"at": 0, "name": "impact", "volume": 0.08}]}
for sh in shots:
    sh["sfx"] = SFX[sh["id"]]
ep["shots"] = shots
ep["pinV2"] = True
ep["musicDrop"] = "First scenario-0.2"
ep["musicPayoff"] = "That's what-0.3"
ep["keywords"] = ["elevator", "screen", "gap", "doors", "chase", "switch", "slip", "three", "layup", "read", "defense"]
ep["subtitleHide"] = [[0, "This is the elevator-0.2"], ["How would you-0.05", 99]]
ep["music"] = {"src": "tactical/elevator3d/music-mix.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots))
