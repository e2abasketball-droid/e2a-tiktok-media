#!/usr/bin/env python3
"""FLOPPY: CURL OR FADE? edit (formato Chicago + owner brief 2026-11-15 10:52Z), anchored to the real narration
(floppy-curl-or-fade.words.json) and to play time. Both reads on the RIGHT side of the screen (court x<0 with yaw 0).
  hook     oblique on the strong-side wing (play B): X2 went under, the corner is empty; cut before the shot.  WIDE OPEN
  setup    TOP (basket at the top), play A from the start: under the rim, the screens, X2 marked first.   FLOPPY
  caseA1   oblique three-quarter, same side of the axis: X2 on the back hip, the tight curl.   TRAIL -> CURL
  caseA2   low lateral: catch on the move, finish at the rim.
  caseB1   SAME TOP frame, same start: X2 shortcuts through the paint (the ONE slow motion, ~0.7 s).   UNDER -> FADE
  caseB2   oblique toward the corner: the fade, feet behind the line, the three.
  cmpA/B   SAME TOP_IN frame: trail -> curl / under + open corner -> fade.
  cta      TOP, play A in motion: CURL OR FADE?, short logo.
  loop     0.6 s back to the hook frame (play B 0 -> 0.4) so the last frame leads into the first.
Sound: contact effects only, at most 4 accents."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "floppy-curl-or-fade.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
fol = lambda ids, z=1.0, **k: {"follow": ids, "z": z, **k}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED, GOLD = "#E5483A", "#C9A24D"

TOP = orb(fol(["O2", "X2"], 0.0, offset=[0.0, 0.7], window=1.2), 15.5, 4, 0, 42)   # pans with the cutter, basket at the top
TOP_IN = orb(fol(["O2", "X2"], 0.0, offset=[0.0, 0.7], window=1.2), 14.0, 4, 0, 42)
CTA = orb(fol(["O2", "X2"], 0.0, offset=[0.0, -0.7], window=1.2), 15.5, 4, 0, 42)   # players below the question
HOOK = orb([-4.5, 2.0, 0.2], 13.0, 50, 90, 44)   # from the half-court side: paint at the top, the empty corner below
OBL = lambda tg, d=8.4, yaw=34: orb(tg, d, 50, yaw, 44)
LOW = lambda tg, d=8.0: orb(tg, d, 30, 58, 44)
CORNER = lambda tg, d=8.6: orb(tg, d, 42, 50, 44)
T = lambda lines, frm, to, gold=(1,), **k: {"type": "title", "lines": lines, "gold": list(gold), "from": frm, "to": to, "y": 252, "size": 100, **k}

shots = [
 {"id": "hook", "name": "Hook — X2 went under, the corner is empty (cut before the shot)", "at": 0, "play": "B",
  "remap": [[0, 0.4], ["@end", 3.0]],
  "camera": [key(0, HOOK), key("@end", {**HOOK, "target": [-4.9, 1.8, 0.2], "dist": 12.4}, "linear")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0.1, "to": "@end"},
          {"type": "openSpace", "at": [-6.5, 1.3], "r": 0.95, "from": "corner", "to": "@end"}],
  "screen": [{**T(["WIDE OPEN"], "wide-0.1", "@end", gold=(0,)), "y": 960}], "sfx": []},   # beside the empty corner, clear of the players at the top
 {"id": "setup", "name": "Overhead — Floppy from the start: under the rim, pick a screen, X2 marked first", "at": "This is-0.15", "play": "A",
  "remap": [[0, 0.0], ["Start", 0.0], ["@end", 2.9]],
  "camera": [key(0, TOP), key("@end", TOP_IN, "inOut")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0.1, "to": "@end"},
          {"type": "route", "player": "O2", "t0": 0.5, "t1": 2.9, "trail": True, "from": "Start", "to": "@end"}],
  "screen": [T(["FLOPPY"], "Floppy", "@end", gold=(0,), sub="Under the rim, pick a screen")], "sfx": []},
 {"id": "caseA1", "name": "Case A — X2 on the back hip: the tight curl (oblique, same side)", "at": "If he's-0.15", "play": "A",
  "remap": [[0, 0.7], ["curl", 1.85], ["@end", 2.95]],
  "camera": [key(0, OBL(fol(["O2", "X2"], 0.3), 8.6)), key("@end", OBL(fol(["O2", "X2"], 0.3, lead=0.15), 7.8), "inOut")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"},
          {"type": "route", "player": "O2", "t0": 1.8, "t1": 2.9, "trail": True, "from": "curl", "to": "@end"}],
  "screen": [T(["TRAIL", "→ CURL"], "back hip", "@end")], "sfx": []},
 {"id": "caseA2", "name": "Case A — low lateral: catch on the move, finish at the rim", "at": "Catch on-0.05", "play": "A",
  "remap": [[0, 2.65], ["@end", 5.6]],
  "camera": [key(0, LOW(fol(["O2"], 1.0), 8.4)), key("@end", LOW([-0.6, 2.2, 1.6], 7.6), "inOut")],
  "ov3": [],
  "screen": [T(["TRAIL", "→ CURL"], 0, "@end")], "sfx": []},
 {"id": "caseB1", "name": "Case B — SAME overhead, same start: X2 shortcuts the paint (slow motion)", "at": "Same setup-0.15", "play": "B",
  "remap": [[0, 0.0], ["Different", 0.0], ["shortcuts", 1.2], ["paint", 1.45, "inOut"], ["@end", 2.35]],
  "camera": [key(0, TOP), key("@end", TOP_IN, "inOut")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "pulse": True, "from": "Different", "to": "@end"},
          {"type": "openSpace", "at": [-6.6, 1.3], "r": 1.2, "from": "leaves", "to": "@end"}],
  "screen": [T(["UNDER", "→ FADE"], "shortcuts", "@end")], "sfx": []},
 {"id": "caseB2", "name": "Case B — toward the corner: the fade, feet behind the line, the three", "at": "fade out-0.05", "play": "B",
  "remap": [[0, 1.5], ["@end", 6.0]],
  "camera": [key(0, OBL(fol(["O2", "X2"], 0.3), 9.4)), key("let", OBL(fol(["O2"], 0.3), 8.4), "inOut"),
             key("@end", OBL([-5.6, 1.7, 0.6], 9.6), "linear")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": 0.7},
          {"type": "route", "player": "O2", "t0": 1.5, "t1": 3.0, "trail": True, "from": 0.1, "to": "line"}],
  "screen": [T(["UNDER", "→ FADE"], 0, "fly."),
             {"type": "stamp", "text": "THREE", "badge": "+3", "from": "fly.>+0.6", "to": "@end", "y": 330}], "sfx": []},
 {"id": "cmpA", "name": "Repeat — TOP_IN, A: trail -> curl", "at": "TRAIL,-0.15", "play": "A",
  "remap": [[0, 1.4], ["@end", 2.9]],
  "camera": [key(0, TOP_IN)],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"}],
  "screen": [T(["TRAIL", "→ CURL"], 0.05, "@end")], "sfx": []},
 {"id": "cmpB", "name": "Repeat — TOP_IN, B: under + open corner -> fade", "at": "UNDER with-0.15", "play": "B",
  "remap": [[0, 1.1], ["@end", 3.2]],
  "camera": [key(0, TOP_IN)],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"},
          {"type": "openSpace", "at": [-6.6, 1.3], "r": 1.2, "from": 0.1, "to": "@end"}],
  "screen": [T(["UNDER + OPEN CORNER", "→ FADE"], 0.05, "@end", size=84)], "sfx": []},
 {"id": "cta", "name": "CTA — TOP, play A in motion: CURL OR FADE?", "at": "Which-0.2", "play": "A",
  "remap": [[0, 0.3], ["@end", 3.6]],
  "camera": [key(0, CTA), key("@end", {**CTA, "dist": 14.6}, "linear")],
  "ov3": [{"type": "ring", "player": "O2", "from": 0, "to": "@end"}, {"type": "ring", "player": "X2", "color": RED, "pulse": True, "from": 0.1, "to": "@end"}],
  "screen": [{"type": "scrim", "opacity": 0.28, "from": "Which-0.1", "to": "@end"},
             {"type": "title", "lines": ["CURL", "OR FADE?"], "gold": [1], "from": "Which", "to": "@end", "y": 600, "size": 124},
             {"type": "logo", "big": False, "from": "@end-1.2", "to": "@end"}], "sfx": []},
 {"id": "loop", "name": "Loop — back to the hook frame (play B 0 -> 0.4)", "at": 35.4, "play": "B",
  "remap": [[0, 0.0], ["@end", 0.4]],
  "camera": [key(0, HOOK)],
  "ov3": [], "screen": [], "sfx": []},
]
SFX = {'caseA2': [{'at': 1.63, 'name': 'swish', 'volume': 0.16}], 'caseB1': [{'at': 'shortcuts', 'name': 'squeak', 'volume': 0.07}], 'caseB2': [{'at': 1.82, 'name': 'bounce', 'volume': 0.09}, {'at': 3.55, 'name': 'swish', 'volume': 0.16}]}
for sh in shots:
    sh["sfx"] = SFX.get(sh["id"], [])
ep["shots"] = shots
ep["keywords"] = ["UNDER", "wide open", "Floppy", "screen", "defender", "back hip", "curl", "finish", "shortcuts", "corner",
                  "fade out", "behind the line", "TRAIL", "fade", "Which read"]
ep["subtitleHide"] = []
ep["autoSfx"] = False   # brief: at most 4 SFX accents -> explicit per-shot cues only
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.06}
ep["music"] = {"src": "tactical/floppy/music.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots))
