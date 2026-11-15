#!/usr/bin/env python3
"""FLEX ACTION - SCREEN THE SCREENER edit (owner brief 2026-11-15 21:45Z), anchored to the real narration
(flex-action.words.json) and to play time. Every camera looks from the SAME side (the left sideline, x>0, where the
baseline screen, the flex cut start, the down screen and the elbow all happen), so the cut always runs across the
screen the same way and O1 and O5 never stack at the second screen.
  main    0-4.85   play A real time (0.35->5.2): reversal, O5's baseline screen, cut, X5's help step, down screen,
                   O5 up, pass, catch, release. Gold ring on O5 for 0.5 s. The rim cut only after the release.
  rim     4.85-5.9 the ball to the net.
  flex    5.9-9.5  replay from before the baseline screen; X5's help step at 0.5x.   FLEX ACTION
  ss      9.5-14.5 replay from the cut, real time: the passer screens the screener, gold on O5 gone at the catch,
                   catch at the elbow, release, make.   SCREEN THE SCREENER
  varB    14.5-18.6 SAME frame, play B from the same start: X5 stays home, X3 late, O2 hits O3 in stride, layup.
  cta     18.6-23.6 play A almost frozen with O3 at the rim and O5 about to come up.   RIM OR ELBOW?
  loop    23.6-end play A 0->0.35 into the first frame."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "flex-action.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED, GOLD = "#E5483A", "#C9A24D"
T = lambda lines, frm, to, gold=(1,), **k: {"type": "title", "lines": lines, "gold": list(gold), "from": frm, "to": to, "y": 252, "size": 100, **k}
YAW = float(os.environ.get("FLEX_YAW", -100))   # left sideline, slightly toward half court (frame-fit search)

# every rig below comes from out/flex/fit-search.mts: the smallest distance that keeps the listed players (feet and
# head) and the ball inside x 60..1020, y 260/440..1280 (above the subtitles; 440 under a title) for the whole window,
# vertically centred. scripts/frame-fit.mts re-checks the blended camera frame by frame.
O = lambda x, y, d, fov=50, p=60: orb([x, y, 0.6], d, p, YAW, fov)
P1 = O(6.86, 3.75, 12.25)      # play 0.35-2.3: reversal, baseline screen, cut, help step (all eight)
P2 = O(4.21, 3.36, 10.0)       # play 2.0-5.0: down screen, O5 up, pass, catch, release (all eight)
P3 = O(1.01, 3.55, 12.75)      # play 4.6-6.25: the flight and the net with O5, X5, O1, X1, O3, X3
FLEX0 = O(4.94, 0.83, 10.25, 46)   # replay: baseline screen, X5's step, the cutter, X3 (title above)
# the second-screen replay looks from the top-left (yaw -20, tactical height): O5 curls round O1 laterally on screen,
# so the two never stack (from the sideline O5 runs in front of O1)
SSB = orb([2.78, 4.5, 0.6], 11.0, 42, -20, 50)   # play 2.0-4.7: O1, X1, O5, X5 under the title
SSC = orb([0.9, 4.34, 0.6], 13.75, 38, -20, 50)  # play 4.6-6.1: the shot and the net
VB1 = O(6.9, 3.64, 12.75)      # play B 0.7-2.4 (all eight)
VB2 = O(3.64, 3.05, 11.25)     # play B 2.2-4.8: the pass, the catch, the layup
CTA = O(1.74, 3.4, 14.0, 46)   # play A 2.45-2.9 (all eight) under the question

shots = [
 {"id": "main", "name": "Main - reversal, baseline screen, cut, help step, down screen, elbow three... jumper", "at": 0, "play": "A",
  "remap": [[0, 0.35], ["@end", 6.25]],
  "camera": [key(0, P1), key(1.6, P1), key(2.6, P2, "inOut"), key(4.0, P2), key(5.2, P3, "inOut"), key("@end", P3)],
  "ov3": [{"type": "ring", "player": "O5", "color": GOLD, "size": 0.8, "from": 0, "to": 0.5}],
  "screen": []},
 {"id": "flex", "name": "Replay - the baseline screen pulls help (X5's step at 0.5x)", "at": 5.9, "play": "A",
  "remap": [[0, 0.6], [1.2, 1.8], [2.4, 2.4], ["@end", 2.72]],
  "camera": [key(0, FLEX0)],
  "ov3": [{"type": "ring", "player": "O5", "color": GOLD, "size": 0.7, "from": 0.2, "to": 1.3},
          {"type": "route", "player": "X5", "t0": 1.85, "t1": 2.35, "trail": True, "color": RED, "from": 1.25, "to": 2.9}],
  "screen": [T(["FLEX ACTION"], 0, "@end", gold=(0,))]},
 {"id": "ss", "name": "Replay - the passer screens the screener, catch at the elbow", "at": 9.5, "play": "A",
  "remap": [[0, 2.0], [0.8, 2.8], [2.6, 3.95], [3.25, 4.6], ["@end", 6.4]],
  "camera": [key(0, SSB), key(3.3, SSB), key(4.2, SSC, "inOut"), key("@end", SSC)],
  "ov3": [{"type": "ring", "player": "O5", "color": GOLD, "from": 0.2, "to": 3.25},
          {"type": "route", "player": "O5", "t0": 3.05, "t1": 4.0, "trail": True, "color": GOLD, "from": 1.6, "to": 3.25}],
  "screen": [T(["SCREEN", "THE SCREENER"], 0.5, 3.6)]},
 {"id": "varB", "name": "Variant B - same frame: X5 stays, X3 late, hit the cutter", "at": 14.5, "play": "B",
  "remap": [[0, 0.7], ["@end", 4.8]],
  "camera": [key(0, VB1), key(1.0, VB1), key(1.9, VB2, "inOut"), key("@end", VB2)],
  "ov3": [{"type": "ring", "player": "X5", "color": RED, "from": 1.2, "to": 1.9},
          {"type": "ring", "player": "O3", "color": GOLD, "from": 1.95, "to": 2.75}],
  "screen": [{"type": "pin", "player": "X3", "text": "LATE", "tone": "red", "from": 1.55, "to": 2.2, "size": 40}]},
 {"id": "cta", "name": "CTA - rim or elbow? both destinations", "at": 18.6, "play": "A",
  "remap": [[0, 2.45], [1.2, 2.8], ["@end", 2.9]],
  "camera": [key(0, CTA), key("@end", {**CTA, "dist": 13.6}, "linear")],
  "ov3": [{"type": "ring", "player": "O3", "color": GOLD, "from": 0.4, "to": "@end"},
          {"type": "ring", "player": "O5", "color": GOLD, "from": 0.4, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["RIM", "OR ELBOW?"], "gold": [1], "from": 0.26, "to": "@end", "y": 252, "size": 108},
             {"type": "logo", "big": False, "from": "@end-1.3", "to": "@end"}]},
 {"id": "loop", "name": "Loop - the reversal into the first frame", "at": 23.6, "play": "A",
  "remap": [[0, 0.0], ["@end", 0.35]],
  "camera": [key(0, P1)], "ov3": [], "screen": []},
]
SFX = {"main": [{"at": 0.1, "name": "bounce", "volume": 0.09}, {"at": 0.9, "name": "squeak", "volume": 0.08},
                {"at": 2.7, "name": "squeak", "volume": 0.08}, {"at": 4.25, "name": "bounce", "volume": 0.08}, {"at": 5.65, "name": "swish", "volume": 0.16}],
       "flex": [{"at": 1.55, "name": "squeak", "volume": 0.07}],
       "ss": [{"at": 4.85, "name": "swish", "volume": 0.13}],
       "varB": [{"at": 2.72, "name": "bounce", "volume": 0.08}, {"at": 3.42, "name": "swish", "volume": 0.14}]}
for sh in shots:
    sh["sfx"] = SFX.get(sh["id"], [])
ep["shots"] = shots
ep["tail"] = 3.9
ep["keywords"] = ["first screener", "baseline screen", "pulls help", "screens for the screener", "OPEN", "elbow",
                  "cutter's open", "at the rim"]
ep["subtitleGroups"] = [4, 3, 4, 4, 5, 3, 4, 3, 3, 5, 5, 3]
ep["subtitleBlock"] = True
ep["subtitleHide"] = [[18.86, 40]]
ep["subtitleY"] = 1330
ep["gradeBottom"] = 0.38
ep["autoSfx"] = False
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.05}
ep["music"] = {"src": "tactical/flex/music-mix.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots), "words", sum(ep["subtitleGroups"]))
