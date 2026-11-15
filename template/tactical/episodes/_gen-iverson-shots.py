#!/usr/bin/env python3
"""IVERSON CUT: CATCH OR BACKDOOR? edit (formato Chicago + owner brief 2026-11-15 10:52Z), anchored to the real narration
(iverson-catch-or-backdoor.words.json) and to play time. Both reads on the same side of the axis.
  hook     oblique on the far elbow (play B): X2 sits in the passing lane and denies; cut on the plant.   DENY THE CATCH?
  setup    TOP (basket at the top), play A from the start: the wing, both elbow screens, X2 marked first.   IVERSON CUT
  caseA1   oblique three-quarter, same side: X2 trails over the screens, the pass leaves.   TRAIL -> CATCH
  caseA2   closer three-quarter: hands shown, catch outside the far elbow, face up.
  caseB1   SAME TOP frame, same start: X2 cheats over the top into the passing lane.   DENY -> BACKDOOR
  caseB2   oblique: sell the catch, the plant (the ONE slow motion, ~0.6 s), the cut behind him.
  caseB3   lateral: lead him to the rim, bounce pass, finish.
  cmpA/B   SAME TOP_IN frame: trail -> catch / deny -> backdoor.
  cta      TOP, play B in motion: CATCH OR BACKDOOR?, short logo.
  loop     0.6 s back to the hook frame (play B 0.6 -> 1.0) so the last frame leads into the first."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "iverson-catch-or-backdoor.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
fol = lambda ids, z=1.0, **k: {"follow": ids, "z": z, **k}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED, GOLD = "#E5483A", "#C9A24D"

TOP = orb(fol(["O2", "X2"], 0.0, offset=[0.0, 0.7], window=1.2), 15.5, 4, 0, 42)   # pans with the cutter, basket at the top
TOP_IN = orb(fol(["O2", "X2"], 0.0, offset=[0.0, 0.7], window=1.2), 14.0, 4, 0, 42)
CTA = orb(fol(["O2", "X2"], 0.0, offset=[0.0, -0.7], window=1.2), 15.5, 4, 0, 42)   # players below the question
HOOK = orb(fol(["O2", "X2", "O1"], 0.2, window=0.8), 9.6, 48, 24, 44)
OBL = lambda tg, d=8.6, yaw=30: orb(tg, d, 50, yaw, 44)
SIDE = lambda tg, d=9.2: orb(tg, d, 60, 74, 44)
T = lambda lines, frm, to, gold=(1,), **k: {"type": "title", "lines": lines, "gold": list(gold), "from": frm, "to": to, "y": 252, "size": 100, **k}

shots = [
 {"id": "hook", "name": "Hook — X2 denies at the top (cut on the plant)", "at": 0, "play": "B",
  "remap": [[0, 1.0], ["@end", 3.0]],
  "camera": [key(0, HOOK), key("@end", {**HOOK, "dist": 8.8}, "linear")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0.1, "to": "@end"},
          {"type": "passLane", "src": "O1", "dst": "O2", "from": "top", "to": "@end"}],
  "screen": [T(["DENY", "THE CATCH?"], 0.25, "@end", gold=(0,))], "sfx": []},
 {"id": "setup", "name": "Overhead — Iverson cut from the start: wing, both elbow screens, X2 marked first", "at": "This is-0.15", "play": "A",
  "remap": [[0, 0.0], ["Start", 0.0], ["@end", 2.95]],
  "camera": [key(0, TOP), key("@end", TOP_IN, "inOut")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0.1, "to": "@end"},
          {"type": "route", "player": "O2", "t0": 0.45, "t1": 2.9, "trail": True, "from": "Start", "to": "@end"}],
  "screen": [T(["IVERSON CUT"], "Iverson", "@end", gold=(0,), sub="Wing, over both elbow screens")], "sfx": []},
 {"id": "caseA1", "name": "Case A — X2 trails over the screens, the pass leaves (oblique, same side)", "at": "If your-0.15", "play": "A",
  "remap": [[0, 0.6], ["@end", 2.45]],
  "camera": [key(0, OBL(fol(["O2", "X2"], 0.3), 9.0)), key("@end", OBL(fol(["O2", "X2", "O1"], 0.3), 9.4), "inOut")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"},
          {"type": "separation", "a": "X2", "b": "O2", "from": "TRAILS", "to": "@end"}],
  "screen": [T(["TRAIL", "→ CATCH"], "TRAILS", "@end")], "sfx": []},
 {"id": "caseA2", "name": "Case A — closer: hands shown, catch outside the far elbow, face up", "at": "catch just-0.1", "play": "A",
  "remap": [[0, 2.0], ["@end", 5.6]],
  "camera": [key(0, OBL(fol(["O2", "X2"], 0.3), 7.6, 36)), key("@end", OBL(fol(["O2"], 0.3), 7.0, 40), "inOut")],
  "ov3": [{"type": "passLane", "src": "O1", "dst": "O2", "from": 0, "to": "far elbow.>"}],
  "screen": [T(["TRAIL", "→ CATCH"], 0, "@end"),
             {"type": "stamp", "text": "FACE UP", "from": "face up", "to": "@end", "y": 330}], "sfx": []},
 {"id": "caseB1", "name": "Case B — SAME overhead, same start: X2 cheats over the top into the lane", "at": "Same cut-0.15", "play": "B",
  "remap": [[0, 0.0], ["changes", 0.0], ["@end", 2.43]],
  "camera": [key(0, TOP), key("@end", TOP_IN, "inOut")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "pulse": True, "from": "Watch", "to": "@end"},
          {"type": "route", "player": "X2", "t0": 0.55, "t1": 2.43, "color": RED, "trail": True, "from": "jumps", "to": "@end"}],
  "screen": [T(["DENY", "→ BACKDOOR"], "jumps", "@end")], "sfx": []},
 {"id": "caseB2", "name": "Case B — oblique: sell the catch, the plant (slow motion), the cut behind him", "at": "sell the catch>-0.6", "play": "B",
  "remap": [[0, 2.25], ["Plant", 2.82], ["Plant>+0.15", 3.0, "inOut"], ["@end", 3.85]],
  "camera": [key(0, OBL(fol(["O2", "X2"], 0.3, offset=[0.3, 1.3]), 7.8, 36)), key("@end", OBL(fol(["O2", "X2"], 0.3, offset=[0.3, 1.3]), 8.4, 36), "inOut")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"},
          {"type": "route", "player": "O2", "t0": 2.88, "t1": 4.4, "dashed": True, "draw": 0.6, "from": "Plant", "to": "@end"}],
  "screen": [T(["DENY", "→ BACKDOOR"], 0, "@end")], "sfx": []},
 {"id": "caseB3", "name": "Case B — lateral: lead him to the rim, bounce pass, finish", "at": "Lead-0.1", "play": "B",
  "remap": [[0, 3.6], ["@end", 6.0]],
  "camera": [key(0, SIDE(fol(["O2", "O1"], 0.3), 10.0)), key("rim.", SIDE(fol(["O2"], 0.3, lead=0.2), 8.8), "inOut"),
             key("@end", SIDE([-0.6, 2.4, 1.6], 8.6), "linear")],
  "ov3": [{"type": "passLane", "src": "O1", "dst": "O2", "from": 0.1, "to": "rim."}],
  "screen": [T(["DENY", "→ BACKDOOR"], 0, "BACKDOOR."),
             {"type": "stamp", "text": "BACKDOOR", "badge": "+2", "from": "BACKDOOR.>+0.3", "to": "@end", "y": 330}], "sfx": []},
 {"id": "cmpA", "name": "Repeat — TOP_IN, A: trail -> catch", "at": "If he trails-0.15", "play": "A",
  "remap": [[0, 1.4], ["@end", 2.95]],
  "camera": [key(0, TOP_IN)],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"}],
  "screen": [T(["TRAIL", "→ CATCH"], 0.05, "@end")], "sfx": []},
 {"id": "cmpB", "name": "Repeat — TOP_IN, B: deny -> backdoor", "at": "If he denies-0.15", "play": "B",
  "remap": [[0, 1.3], ["@end", 2.95]],
  "camera": [key(0, TOP_IN)],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"}],
  "screen": [T(["DENY", "→ BACKDOOR"], 0.05, "@end")], "sfx": []},
 {"id": "cta", "name": "CTA — TOP, play B in motion: CATCH OR BACKDOOR?", "at": "Could-0.2", "play": "B",
  "remap": [[0, 0.0], ["@end", 2.4]],
  "camera": [key(0, CTA), key("@end", {**CTA, "dist": 15.0}, "linear")],
  "ov3": [{"type": "ring", "player": "O2", "from": 0, "to": "@end"}, {"type": "ring", "player": "X2", "color": RED, "pulse": True, "from": 0.1, "to": "@end"}],
  "screen": [{"type": "scrim", "opacity": 0.28, "from": "Could-0.1", "to": "@end"},
             {"type": "title", "lines": ["CATCH", "OR BACKDOOR?"], "gold": [1], "from": "Could", "to": "@end", "y": 600, "size": 116},
             {"type": "logo", "big": False, "from": "@end-1.2", "to": "@end"}], "sfx": []},
 {"id": "loop", "name": "Loop — back to the hook frame (play B 0.6 -> 1.0)", "at": 35.36, "play": "B",
  "remap": [[0, 0.6], ["@end", 1.0]],
  "camera": [key(0, HOOK)],
  "ov3": [], "screen": [], "sfx": []},
]
SFX = {'caseA2': [{'at': 1.2, 'name': 'bounce', 'volume': 0.09}], 'caseB2': [{'at': 'Plant', 'name': 'squeak', 'volume': 0.07}], 'caseB3': [{'at': 0.95, 'name': 'bounce', 'volume': 0.1}, {'at': 2.8, 'name': 'swish', 'volume': 0.16}]}
for sh in shots:
    sh["sfx"] = SFX.get(sh["id"], [])
ep["shots"] = shots
ep["keywords"] = ["DENY", "gone", "Iverson cut", "elbow screens", "TRAILS", "show your hands", "catch", "face up",
                  "jumps the passing lane", "sell the catch", "Plant", "cut behind him", "BACKDOOR", "denies", "full speed"]
ep["subtitleHide"] = []
ep["autoSfx"] = False   # brief: at most 4 SFX accents -> explicit per-shot cues only
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.06}
ep["music"] = {"src": "tactical/iverson/music.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots))
