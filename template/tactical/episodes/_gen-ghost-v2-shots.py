#!/usr/bin/env python3
"""GHOST SCREEN V2 edit (owner brief 2026-11-15 19:27Z), anchored to the real narration (ghost-screen-v2.words.json)
and to play time. Every camera looks from the SAME side of the court (the shooter's wing, x<0: yaw ~80), so the pop
always comes toward the viewer and the reject drive always runs the same way across the screen.
  hook    0-3.4    3/4 high from the side, play A 1.35->4.75 real time: the screener 2 steps from X1, X2 steps to the
                   ball, plant, pop, pass, catch, release in ONE shot (pan to the catch).   THIS SCREEN NEVER HAPPENS
  rim     3.4-5.5  the ball to the net after the release.
  name    5.5-10.0 closer, same side: the plant foot and the gap to X1; 0.8x on the turn only.   GHOST SCREEN
  read1   10.0-14.3 high, same side: X2's step (short red arrow), pass, catch behind the arc, X1 late.   HIT THE POP
  read2   14.3-21.9 SAME frame, same start (play B): X2 rides the pop (red ring), X1 jumps, crossover, the camera
                   follows the first step.   REJECT THE SCREEN
  layup   21.9-23.85 lower, same direction of travel: gather, layup, late help, net.
  cta     23.85-27.1 back to play A at X2's step: shooter, his defender and the ball in one frame.  WHO'S GOT THE SHOOTER?
  loop    27.1-end  the screener's approach (play A 0.75->1.35) into the first frame."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "ghost-screen-v2.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
fol = lambda ids, z=1.0, **k: {"follow": ids, "z": z, **k}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED, GOLD = "#E5483A", "#C9A24D"
T = lambda lines, frm, to, gold=(1,), **k: {"type": "title", "lines": lines, "gold": list(gold), "from": frm, "to": to, "y": 252, "size": 100, **k}
YAW = 62

HOOK0 = orb([-1.5, 8.2, 0.4], 10.8, 58, YAW, 44)            # screener near the centre, O1/X1 behind, the wing below
HOOK1 = orb([-3.6, 7.6, 0.8], 9.0, 56, YAW + 4, 44)        # settled on the catch and the release
RIM = orb([-1.6, 3.2, 2.2], 10.6, 58, YAW - 8, 44)
NAME0 = orb([-0.7, 8.6, 0.3], 7.8, 52, YAW, 44)
NAME1 = orb([-3.0, 7.7, 0.5], 7.8, 50, YAW + 4, 44)
HIGH = orb([-1.6, 8.0, 0.0], 13.0, 26, YAW, 42)           # the read frame: handler, both defenders and the pop spot
DRIVE = orb(fol(["O1", "X1"], 0.0, window=0.9), 12.5, 26, YAW, 42)
LOW = lambda tg, d, yaw=YAW: orb(tg, d, 64, yaw, 46)

shots = [
 {"id": "hook", "name": "Hook - the screener comes in, X2 steps to the ball, pop, pass, three (one shot)", "at": 0, "play": "A",
  "remap": [[0, 1.35], ["@end", 4.75]],
  "camera": [key(0, HOOK0), key(1.25, HOOK0), key(2.6, HOOK1, "inOut"), key("@end", HOOK1)],
  "ov3": [{"type": "ring", "player": "O2", "color": GOLD, "size": 0.8, "from": 0, "to": 0.45}],
  "screen": [T(["THIS SCREEN", "NEVER HAPPENS"], 0, 2.35)]},
 {"id": "rim", "name": "The ball to the net", "at": 3.4, "play": "A",
  "remap": [[0, 4.75], ["@end", 6.85]],
  "camera": [key(0, RIM), key("@end", {**RIM, "dist": 9.8}, "linear")],
  "ov3": [], "screen": []},
 {"id": "name", "name": "Name it - closer, same side: plant foot and gap to X1, 0.8x on the turn", "at": 5.5, "play": "A",
  "remap": [[0, 1.3], [0.6, 1.9], [1.9125, 2.95], ["@end", 5.54]],
  "camera": [key(0, NAME0), key(1.9, NAME0), key(3.0, NAME1, "inOut"), key("@end", NAME1)],
  "ov3": [{"type": "ring", "player": "O2", "color": GOLD, "size": 0.7, "from": 1.1, "to": 2.3}],
  "screen": [T(["GHOST SCREEN"], 0, "Sell-0.1", gold=(0,)),
             T(["SELL THE BLOCK"], "Sell-0.1", "pop-0.1", gold=(0,), size=88),
             T(["POP BEFORE CONTACT"], "pop-0.1", "@end", gold=(0,), size=80)]},
 {"id": "read1", "name": "Read 1 - X2 steps to the ball (short arrow), hit the pop", "at": 10.0, "play": "A",
  "remap": [[0, 1.07], ["@end", 5.37]],
  "camera": [key(0, HIGH), key(2.6, HIGH), key(3.4, {**HIGH, "target": [-2.6, 7.8, 0.0]}, "inOut")],
  "ov3": [{"type": "route", "player": "X2", "t0": 2.45, "t1": 3.17, "trail": True, "color": RED, "from": 1.35, "to": 2.38}],
  "screen": [T(["HIT THE POP"], 2.1, "@end", gold=(0,)),
             {"type": "pin", "player": "X1", "text": "LATE", "tone": "red", "from": 3.35, "to": "@end", "size": 40}]},
 {"id": "read2", "name": "Read 2 - same frame, same start: X2 stays, X1 jumps, reject", "at": 14.3, "play": "B",
  "remap": [[0, 1.07], ["@end", 8.67]],
  "camera": [key(0, HIGH), key(5.6, HIGH), key(7.0, {**DRIVE, "dist": 12.5}, "inOut"), key("@end", {**DRIVE, "dist": 12.5})],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 1.65, "to": 3.3},
          {"type": "route", "player": "X1", "t0": 6.4, "t1": 7.12, "trail": True, "color": RED, "from": 5.3, "to": 6.9},
          {"type": "route", "player": "O1", "t0": 8.1, "t1": 9.2, "trail": True, "color": GOLD, "from": 7.05, "to": "@end"}],
  "screen": [T(["SAME FAKE"], 0.1, 1.5, gold=(0,)),
             T(["REJECT", "THE SCREEN"], 7.05, "@end")]},
 {"id": "layup", "name": "Layup - lower, same direction: gather, layup, late help, net", "at": 21.9, "play": "B",
  "remap": [[0, 8.67], ["@end", 10.62]],
  "camera": [key(0, LOW([1.4, 5.8, 1.1], 10.2)), key("@end", LOW([0.4, 2.6, 1.6], 8.6), "inOut")],
  "ov3": [], "screen": [{"type": "pin", "player": "X5", "text": "HELP: LATE", "tone": "red", "from": 1.0, "to": 1.75, "size": 40, "dy": -150}]},
 {"id": "cta", "name": "CTA - back to play A at X2's step: who's got the shooter?", "at": 23.85, "play": "A",
  "remap": [[0, 2.2], [1.0, 2.7], ["@end", 2.86]],
  "camera": [key(0, {**HIGH, "target": [-0.6, 8.3, 0.0], "dist": 11.0}), key("@end", {**HIGH, "target": [-0.6, 8.3, 0.0], "dist": 10.4}, "linear")],
  "ov3": [{"type": "ring", "player": "O2", "color": GOLD, "from": 0.9, "to": "@end"},
          {"type": "ring", "player": "X2", "color": RED, "from": 0.9, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["WHO'S GOT", "THE SHOOTER?"], "gold": [1], "from": "Who's-0.15", "to": "@end", "y": 252, "size": 104},
             {"type": "logo", "big": False, "from": "@end-1.3", "to": "@end"}]},
 {"id": "loop", "name": "Loop - the screener's approach into the first frame", "at": 27.1, "play": "A",
  "remap": [[0, 0.75], ["@end", 1.35]],
  "camera": [key(0, HOOK0)], "ov3": [], "screen": []},
]
SFX = {"hook": [{"at": 0.05, "name": "bounce", "volume": 0.1}, {"at": 1.2, "name": "squeak", "volume": 0.09},
                {"at": 2.72, "name": "bounce", "volume": 0.08}],
       "rim": [{"at": 0.8, "name": "swish", "volume": 0.16}],
       "name": [{"at": 1.43, "name": "squeak", "volume": 0.08}],
       "read1": [{"at": 3.0, "name": "bounce", "volume": 0.07}],
       "read2": [{"at": 7.05, "name": "bounce", "volume": 0.09}],
       "layup": [{"at": 1.6, "name": "swish", "volume": 0.14}]}
for sh in shots:
    sh["sfx"] = SFX.get(sh["id"], [])
ep["shots"] = shots
ep["keywords"] = ["ghost screen", "BEFORE CONTACT", "steps toward", "hit the pop", "STAYS WITH HIM", "jumps", "REJECT IT"]
# sense units; the hook title, GHOST SCREEN and the closing question replace the subtitle while they say the same words
ep["subtitleGroups"] = [4, 5, 2, 4, 3, 4, 4, 4, 3, 2, 5, 3, 6, 4, 4, 5, 4]
ep["subtitleBlock"] = True
ep["subtitleHide"] = [[0, "HAPPENS.>+0.3"], [5.5, 10.32], ["Who's-0.15", 40]]
ep["subtitleY"] = 1330
ep["gradeBottom"] = 0.38
ep["autoSfx"] = False
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.05}
ep["music"] = {"src": "tactical/ghost2/music-mix.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots), "words", sum(ep["subtitleGroups"]))
