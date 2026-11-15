#!/usr/bin/env python3
"""GHOST SCREEN edit (owner brief 2026-11-15 17:22Z), anchored to the real narration (ghost-screen.words.json) and to
play time. Keeps three Stagger premium devices: the 3/4 opening with the action already moving, the cut to the tactical
camera to explain, and gold on the floor to guide the eye. Basket at the top in every tactical shot (yaw 0).
  hook    0-3.3    3/4 high, play A real time: O2 comes in to X1, X2 steps to the ball, plant and pop.   ZERO CONTACT
  triple  3.3-6.0  elevated, play A real time: pass, catch on the wing, three to the net, X1 late.
  ghost   6.0-10.5 oblique on the four players, play A from before the fake; the ONE slow motion on the plant.   GHOST SCREEN
  caseA   10.5-16.6 TACTICAL (basket at the top), play A real time: X2's step first, TWO ON THE BALL, pass line, X1 late.
  caseB   16.6-23.9 SAME tactical frame, play B real time from the same bounce (match cut): X2 stays, X1 jumps, free side,
                   REJECT on the first step.
  finish  23.9-27.3 low 3/4: the drive, the gather, the layup, the late help, the net.
  cta     27.3-32.3 tactical, play A just before the pass: both defenders on the ball, O2 alone.   WHO'S GOT THE SHOOTER?
  loop    32.3-33.0 back to the hook frame and the approach (play A 0 -> 0.7)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "ghost-screen.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
fol = lambda ids, z=1.0, **k: {"follow": ids, "z": z, **k}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED, GOLD = "#E5483A", "#C9A24D"
T = lambda lines, frm, to, gold=(1,), **k: {"type": "title", "lines": lines, "gold": list(gold), "from": frm, "to": to, "y": 252, "size": 100, **k}

HOOK = orb([-1.2, 8.0, 0.6], 8.8, 58, -48, 44)
HIGH = orb([-1.7, 4.1, 1.8], 11.8, 50, -4, 44)
GHO = orb(fol(["O1", "X1", "O2", "X2"], 0.5, window=1.2), 8.6, 56, 28, 44)
TACT = orb(fol(["O1", "X1", "O2", "X2"], 0.0, offset=[0.0, -1.2], window=1.4), 17.5, 28, 0, 42)
LOW = lambda tg, d=8.0, yaw=38: orb(tg, d, 68, yaw, 46)

shots = [
 {"id": "hook", "name": "Hook - 3/4 high: O2 comes in to X1, X2 steps to the ball, plant and pop", "at": 0, "play": "A",
  "remap": [[0, 0.0], ["@end", 3.3]],
  "camera": [key(0, HOOK), key("@end", {**HOOK, "dist": 8.0}, "linear")],
  "ov3": [], "screen": [T(["ZERO", "CONTACT"], 2.9, "@end")]},
 {"id": "triple", "name": "Elevated - the pass, the catch on the wing, the three to the net", "at": 3.3, "play": "A",
  "remap": [[0, 3.3], ["@end", 6.0]],
  "camera": [key(0, HIGH), key("@end", {**HIGH, "dist": 10.4}, "linear")],
  "ov3": [], "screen": [{"type": "stamp", "text": "OPEN THREE", "badge": "+3", "from": 2.0, "to": "@end", "y": 520}]},
 {"id": "ghost", "name": "Back to before the fake - the plant foot (the one slow motion)", "at": 6.0, "play": "A",
  "remap": [[0, 0.8], [1.65, 2.45], [3.05, 2.85], ["@end", 4.3]],
  "camera": [key(0, GHO), key("@end", {**GHO, "dist": 8.2}, "linear")],
  "ov3": [{"type": "ring", "player": "O2", "color": GOLD, "size": 0.7, "from": 1.79, "to": 3.25}],
  "screen": [{"type": "rewind", "from": 0, "to": 0.5}, T(["GHOST", "SCREEN"], 0.5, "@end", sub="Sell it. Pop before contact.")]},
 {"id": "caseA", "name": "Tactical - case A real time: X2 steps to the ball, two on the ball, pass, X1 late", "at": 10.5, "play": "A",
  "remap": [[0, 0.1], ["@end", 6.2]],
  "camera": [key(0, TACT)],
  "ov3": [{"type": "route", "player": "X2", "t0": 2.4, "t1": 3.2, "trail": True, "color": RED, "from": 2.3, "to": 3.45},
          {"type": "passLane", "src": "O1", "dst": "O2", "from": 3.34, "to": 4.0}],
  "screen": [T(["TWO ON", "THE BALL"], 2.85, 4.05),
             {"type": "pin", "player": "X1", "text": "LATE", "tone": "red", "from": 4.05, "to": 5.2, "size": 40}]},
 {"id": "caseB", "name": "Tactical - case B, same frame, same bounce: X2 stays, X1 jumps, cross back", "at": 16.6, "play": "B",
  "remap": [[0, 0.1], ["@end", 7.4]],
  "camera": [key(0, TACT)],
  "ov3": [{"type": "route", "player": "X2", "t0": 2.7, "t1": 4.3, "trail": True, "color": RED, "from": 2.75, "to": 4.5},
          {"type": "route", "player": "X1", "t0": 4.8, "t1": 5.6, "trail": True, "color": RED, "from": 4.75, "to": 6.1},
          {"type": "openSpace", "at": [1.7, 6.4], "r": 1.1, "from": 6.2, "to": 6.95}],
  "screen": [T(["REJECT"], 6.85, "@end", gold=(0,))]},
 {"id": "finish", "name": "Low 3/4 - the drive, the layup, the late help", "at": 23.9, "play": "B",
  "remap": [[0, 7.4], ["@end", 10.8]],
  "camera": [key(0, LOW([0.5, 3.5, 1.5], 10.6, 26)), key(1.2, LOW([0.2, 2.6, 1.7], 9.2, 30), "inOut"), key("@end", LOW([0.1, 2.4, 1.6], 8.8, 32), "linear")],
  "ov3": [], "screen": [T(["REJECT"], 0, 0.9, gold=(0,)),
                        {"type": "pin", "player": "X5", "text": "HELP: LATE", "tone": "red", "from": 0.05, "to": 1.0, "size": 40}]},
 {"id": "cta", "name": "CTA - back to case A before the pass: both on the ball, the shooter alone", "at": 27.3, "play": "A",
  "remap": [[0, 2.2], ["@end", 7.2]],
  "camera": [key(0, {**TACT, "dist": 18.2}), key("@end", {**TACT, "target": fol(["O2", "X1", "X2"], 0.0, offset=[0.0, -1.2], window=1.4), "dist": 18.2}, "inOut")],
  "ov3": [{"type": "ring", "player": "O2", "color": GOLD, "from": 1.6, "to": "@end"}],
  "screen": [{"type": "scrim", "opacity": 0.24, "from": 1.6, "to": "@end"},
             {"type": "title", "lines": ["WHO'S GOT", "THE SHOOTER?"], "gold": [1], "from": 1.7, "to": "@end", "y": 252, "size": 108},
             {"type": "logo", "big": False, "from": "@end-1.6", "to": "@end"}]},
 {"id": "loop", "name": "Loop - back to the hook frame and the approach", "at": 32.3, "play": "A",
  "remap": [[0, 0.0], ["@end", 0.7]],
  "camera": [key(0, HOOK)], "ov3": [], "screen": []},
]
SFX = {"hook": [{"at": 0.29, "name": "bounce", "volume": 0.1}, {"at": 2.55, "name": "squeak", "volume": 0.08}],
       "triple": [{"at": 0.77, "name": "bounce", "volume": 0.09}, {"at": 2.25, "name": "swish", "volume": 0.16}],
       "finish": [{"at": 1.3, "name": "swish", "volume": 0.14}]}
for sh in shots:
    sh["sfx"] = SFX.get(sh["id"], [])
ep["shots"] = shots
ep["keywords"] = ["TWO DEFENDERS", "ghost screen", "WATCH HIS FEET", "Pop", "both defenders", "shooter", "Same fake",
                  "defender", "jumps", "OTHER WAY", "Who's got the shooter"]
ep["subtitleGroups"] = [4, 4, 4, 3, 3, 3, 6, 3, 7, 5, 5, 4, 3, 6]
ep["subtitleHide"] = []
ep["autoSfx"] = False
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.06}
ep["music"] = {"src": "tactical/ghost/music-mix.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots))
