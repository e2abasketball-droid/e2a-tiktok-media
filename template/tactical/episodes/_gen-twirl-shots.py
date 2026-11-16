#!/usr/bin/env python3
"""TWIRL ACTION edit (owner brief 2026-11-16 04:43Z), anchored to the real narration (twirl-action.words.json) and to
play time. Same look as the Veer / Spain pick-and-roll reels: short top title per beat, high 3/4 tactical camera, red
ring/label on the ONE defender who decides (X4, the first screener's defender), gold routes on the offence, CTA over
the moving play. Every read uses one camera family (yaw -15, pitch 62) so the viewer compares the same picture.
  hook    play A: the cutter turns to the rim, the first screener starts out; cut before the pass.  WRONG SHOOTER?
  loop1   back to the stagger: thin gold ring on the first screener, ball in the passer's hands.      STAGGER
  dev     the curl around screen 1 (CURL), X4 steps in to stop it (HELP) before O4 leaves.
  resp1   O4 pivots, takes screen 2, flares to the wing (gold route appears on the pivot), pass, three. TWIRL ACTION
  hook2   play B, same frame and start: X4 stays up with his man; hold just before the pass.          WHO GETS IT?
  resp2   the lane is open: pass in front of the cutter (HIT THE CURL), catch on the move, layup.
  cmpA    play A from the cutter's turn, ring on X4 only.   HELP → THREE
  cmpB    play B from the cutter's turn, ring on X4 only.   STAY UP → CURL
  cta     play A back to the instant before the hook's first frame."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "twirl-action.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED, GOLD = "#E5483A", "#C9A24D"
T = lambda lines, frm, to, gold=(0,), **k: {"type": "title", "lines": lines, "gold": list(gold), "from": frm, "to": to, "y": 252, "size": 100, **k}
SETUP = orb([-1.34, 6.69, 0.6], 17.25, 48, -10)   # the stagger with the passer still at the top left
READ = orb([-2.06, 6.44, 0.6], 16.0, 48, -10)     # the read frame: passer, cutter, both screeners, X4
TWIRL = orb([-2.84, 6.68, 0.6], 16.5, 48, -10)    # O4 out to the wing, pass, three
HOOK = orb([-1.76, 6.69, 0.6], 13.5, 48, -10)     # tight on the curl and the first screener
FINISH = orb([-1.94, 2.94, 0.6], 12.25, 48, -10)  # push in for the layup
SCR1 = -2.62   # O4 faces the corner (X2 comes from there)
SCR2 = -0.49   # O5 faces the lane (X4 comes from there)

shots = [
 {"id": "hook", "name": "Hook - the cutter turns to the rim, the first screener starts out; cut before the pass", "at": 0, "play": "A",
  "remap": [[0, 2.1], ["shooter.>", 3.1], ["@end", 3.35]],
  "camera": [key(0, HOOK)],
  "ov3": [{"type": "ring", "player": "O2", "color": GOLD, "size": 0.75, "pulse": True, "from": 0.1, "to": "@end"},
          {"type": "route", "player": "O2", "t0": 1.0, "t1": 3.0, "trail": True, "color": GOLD, "from": 0.1, "to": "@end"}],
  "screen": [T(["WRONG", "SHOOTER?"], 0, "@end", gold=(1,), size=110)]},
 {"id": "loop1", "name": "Loop 1 - back to the stagger: ring on the first screener, ball with the passer", "at": "It starts-0.25", "play": "A",
  "remap": [[0, 0.0], ["Watch", 0.15], ["@end", 0.9]],
  "camera": [key(0, SETUP)],
  "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": SCR1, "from": "stagger-0.2", "to": "@end"},
          {"type": "screen", "player": "O5", "n": 2, "facing": SCR2, "from": "stagger", "to": "@end"},
          {"type": "ring", "player": "O4", "color": GOLD, "size": 0.6, "from": "first screener-0.1", "to": "@end"}],
  "screen": [T(["STAGGER"], "starts", "@end", size=104)]},
 {"id": "dev", "name": "Development - the curl around screen 1, X4 steps in to stop it before O4 leaves", "at": "The cutter-0.1", "play": "A",
  "remap": [[0, 0.9], ["curls", 1.55], ["first screen.>", 2.3], ["inside", 2.6], ["@end", 2.82]],
  "camera": [key(0, SETUP), key("curls", READ, "inOut"), key("@end", READ)],
  "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": SCR1, "from": 0, "to": "@end"},
          {"type": "ring", "player": "O4", "color": GOLD, "size": 0.6, "from": 0, "to": "@end"},
          {"type": "route", "player": "O2", "t0": 0.9, "t1": 2.9, "trail": True, "color": GOLD, "from": "curls-0.2", "to": "@end"},
          {"type": "ring", "player": "X4", "color": RED, "pulse": True, "from": "pulls-0.1", "to": "@end"},
          {"type": "route", "player": "X4", "t0": 2.4, "t1": 2.95, "trail": True, "color": RED, "width": 0.16, "from": "pulls", "to": "@end"}],
  "screen": [{"type": "pin", "player": "O2", "text": "CURL", "tone": "gold", "from": "curls-0.1", "to": "pulls", "size": 42},
             {"type": "pin", "player": "X4", "text": "HELP", "tone": "red", "from": "pulls", "to": "@end", "size": 42}]},
 {"id": "resp1", "name": "Answer 1 - the first screener twirls off screen 2 to the wing; pass and the three", "at": "And the first-0.15", "play": "A",
  "remap": [[0, 2.82], ["TAKES", 2.95], ["second screen.>", 3.4], ["Twirl.>", 4.25], ["@end", 6.0]],
  "camera": [key(0, READ), key("TAKES+0.2", TWIRL, "inOut"), key("@end", TWIRL)],
  "ov3": [{"type": "route", "player": "O2", "t0": 0.9, "t1": 2.9, "trail": True, "color": GOLD, "from": 0, "to": "That's"},
          {"type": "route", "player": "O4", "t0": 2.85, "t1": 4.2, "trail": True, "color": GOLD, "from": "TAKES-0.1", "to": "Twirl.>+0.3"},
          {"type": "screen", "player": "O5", "n": 2, "facing": SCR2, "from": "TAKES-0.1", "to": "Twirl.>"},
          {"type": "ring", "player": "X4", "color": RED, "from": 0, "to": "Twirl.>"}],
  "screen": [T(["TWIRL ACTION"], "second screen.>-0.2", "Twirl.>+0.2", size=112),
             {"type": "pin", "player": "O4", "text": "1ST SCREENER", "tone": "gold", "from": 0, "to": "TAKES+0.4", "size": 38}]},
 {"id": "hook2", "name": "Hook 2 - same frame and start; X4 stays up with his man; hold just before the pass", "at": "Same setup-0.25", "play": "B",
  "remap": [[0, 1.2], ["stays", 2.0], ["up.>", 2.35], ["gets it?>", 2.5], ["@end", 2.54]],
  "camera": [key(0, READ)],
  "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": SCR1, "from": 0, "to": "@end"},
          {"type": "screen", "player": "O5", "n": 2, "facing": SCR2, "from": 0, "to": "@end"},
          {"type": "ring", "player": "X4", "color": RED, "pulse": True, "from": "defender stays-0.2", "to": "@end"}],
  "screen": [T(["WHO GETS IT?"], "Who-0.05", "@end", size=104),
             {"type": "pin", "player": "X4", "text": "STAYS UP", "tone": "red", "from": "stays", "to": "@end", "size": 40}]},
 {"id": "resp2", "name": "Answer 2 - pass in front of the cutter, catch on the move, layup", "at": "Now the-0.15", "play": "B",
  "remap": [[0, 2.54], ["Hit him", 2.6], ["move.>", 3.25], ["@end", 4.75]],
  "camera": [key(0, READ), key("move.>-0.3", READ), key("move.>+0.7", FINISH, "inOut"), key("@end", FINISH)],
  "ov3": [{"type": "route", "player": "O2", "t0": 0.9, "t1": 3.95, "trail": True, "color": GOLD, "from": 0, "to": "move.>+0.4"},
          {"type": "ring", "player": "X4", "color": RED, "from": 0, "to": "move.>"}],
  "screen": [T(["HIT THE CURL"], "Hit him-0.05", "move.>+0.3", size=104)]},
 {"id": "cmpA", "name": "Compare A - from the cutter's turn: X4 helps, hit the shooter", "at": "Help on-0.25", "play": "A",
  "remap": [[0, 2.15], ["@end", 4.45]],
  "camera": [key(0, TWIRL)],
  "ov3": [{"type": "ring", "player": "X4", "color": RED, "pulse": True, "from": 0, "to": "@end"}],
  "screen": [T(["HELP → THREE"], 0.05, "@end", gold=(0,), size=96)]},
 {"id": "cmpB", "name": "Compare B - from the cutter's turn: X4 stays up, hit the cutter", "at": "Stay up?-0.3", "play": "B",
  "remap": [[0, 2.15], ["@end", 3.95]],
  "camera": [key(0, TWIRL)],
  "ov3": [{"type": "ring", "player": "X4", "color": RED, "pulse": True, "from": 0, "to": "@end"}],
  "screen": [T(["STAY UP → CURL"], 0.05, "@end", gold=(0,), size=96)]},
 {"id": "cta", "name": "CTA - over the court, back to the instant before the hook's first frame", "at": "For more-0.3", "play": "A",
  "remap": [[0, 0.3], [2.4, 1.8], ["@end", 2.09]],
  "camera": [key(0, SETUP), key(1.6, SETUP), key(2.6, HOOK, "inOut"), key("@end", HOOK)],
  "ov3": [],
  "screen": [T(["FOR MORE", "EUROPEAN BASKETBALL"], 0.2, "@end-0.25", gold=(1,), size=92),
             {"type": "logo", "big": False, "from": 0.6, "to": "@end-0.25"}]},
]
SFX = {"hook": [{"at": 1.2, "name": "squeak", "volume": 0.1}],
       "loop1": [{"at": 0, "name": "whoosh", "volume": 0.08}],
       "dev": [{"at": "curls", "name": "squeak", "volume": 0.1}, {"at": "pulls", "name": "squeak", "volume": 0.1}],
       "resp1": [{"at": "TAKES-0.1", "name": "squeak", "volume": 0.14}, {"at": "second screen.>-0.2", "name": "impact_big", "volume": 0.16},
                 {"at": "@end-0.55", "name": "swish", "volume": 0.17}],
       "hook2": [{"at": "it?>", "name": "tick", "volume": 0.08}],
       "resp2": [{"at": "Hit him", "name": "bounce", "volume": 0.07}, {"at": "@end-0.5", "name": "swish", "volume": 0.16}],
       "cmpA": [{"at": 0, "name": "whoosh", "volume": 0.06}],
       "cmpB": [{"at": 0, "name": "whoosh", "volume": 0.06}],
       "cta": []}
for sh in shots:
    sh["sfx"] = SFX.get(sh["id"], [])
ep["shots"] = shots
ep["keywords"] = ["WRONG", "stagger", "first screener", "curls", "inside", "TAKES", "second screen", "Twirl", "stays up", "gets it",
                  "open", "move", "shooter", "cutter", "European"]
ep["subtitleGroups"] = [5, 5, 2, 2, 3, 3, 2, 2, 2, 4, 2, 2, 3, 2, 2, 4, 3, 4, 5, 4, 3, 2, 3, 4]
ep["subtitleBlock"] = True
ep["subtitleHide"] = [[0, "shooter.>+0.4"], ["For more-0.3", 40]]
ep["subtitleY"] = 1400
ep["gradeBottom"] = 0.38
ep["autoSfx"] = False
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.05}
ep["music"] = {"src": "tactical/twirl/music-mix.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
w = json.load(open(os.path.join(D, "twirl-action.words.json")))
print("shots", len(shots), "groups", sum(ep["subtitleGroups"]), "words", len(w))
