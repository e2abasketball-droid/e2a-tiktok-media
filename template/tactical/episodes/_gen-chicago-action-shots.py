#!/usr/bin/env python3
"""CHICAGO ACTION pilot edit, anchored to the real narration (chicago-action.words.json) and to play time.
Camera grammar (owner brief 2026-11-14 18:56Z, Elevator reference: floor -> straight overhead, same frame for A and B):
  hook     medium-high on the wing (play B): X2 leaves the trail line and jumps the exchange; the lane is only
           suggested (O2 runs out of frame toward the rim), cut before the basket.   HE JUMPED THE HANDOFF
  setup    TOP: near-vertical overhead (pitch 4, basket at the top), play A from the start: pin-down, the receiver's
           route drawn as he runs it, the hand-off spot.   CHICAGO ACTION
  caseA    oblique three-quarter on the SAME side of the axis (yaw -32): passer's hand -> receiver's hands -> first
           dribble, the turn, the deep big, the pull-up.   TRAILS -> TAKE IT
  caseB1   SAME TOP frame, same start: watch X2's feet (slow motion), FREEZE with X2 in the exchange line and the
           ball still in O1's hands, then the plant (slow).   JUMPS -> BACKDOOR
  caseB2   lateral: the backdoor cut, the bounce pass to the catch, the late help, the finish.
  cmpA/B   SAME TOP frame, same play instant: X2 trailing (A) / X2 in the lane (B).
  cta      TOP, play in motion: CHASE / JUMP / SWITCH?, short logo.
Sound: contact effects only (bounce, catch, squeak, swish, landing) at low level."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "chicago-action.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
fol = lambda ids, z=1.0, **k: {"follow": ids, "z": z, **k}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED, WHITE, GOLD = "#E5483A", "#FFFFFF", "#C9A24D"

TOP = orb([-2.55, 5.0, 0.0], 14.6, 4, 0, 42)          # near-vertical, basket at the top, whole left half visible
TOP_IN = orb([-3.2, 5.6, 0.0], 12.4, 4, 0, 42)        # same axis, slightly closer for the exchange
HOOK = orb([-4.0, 6.0, 0.9], 8.6, 48, -24, 44)        # medium-high on the wing: ball, receiver and his defender
OBL = lambda tg, d=8.4, yaw=42: orb(tg, d, 50, yaw, 44)  # three-quarter oblique, same side of the axis as TOP;
# yaw 42 looks ACROSS the passer-receiver line (yaw -32 put O1's back over the exchange: review fragment 2)
SIDE = lambda tg, d=9.2: orb(tg, d, 64, 74, 44)       # lateral from the left sideline (backdoor cut + pass)

shots = [
 {"id": "hook", "name": "Hook — X2 jumps the exchange, the lane opens (cut before the rim)", "at": 0, "play": "B",
  "remap": [[0, 0.75], ["handoff.>", 2.1], ["@end", 3.0]],
  "camera": [key(0, HOOK), key("@end", {**HOOK, "target": [-3.7, 5.4, 0.9], "dist": 8.2}, "linear")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0.15, "to": "@end"},
          {"type": "route", "player": "X2", "t0": 0.9, "t1": 2.2, "color": RED, "trail": True, "from": "JUMPS", "to": "@end"},
          {"type": "openSpace", "at": [-2.3, 3.1], "r": 1.25, "from": "opened", "to": "@end"}],
  "screen": [{"type": "title", "lines": ["HE JUMPED", "THE HANDOFF"], "gold": [1], "from": "JUMPS", "to": "@end", "y": 250, "size": 104}],
  "sfx": []},
 {"id": "setup", "name": "Overhead — pin-down straight into the hand-off (play A from the start)", "at": "This is-0.15", "play": "A",
  "remap": [[0, 0.1], ["pin-down,", 0.9], ["into a handoff.>", 2.3], ["@end", 2.6]],
  "camera": [key(0, TOP), key("@end", TOP_IN, "inOut")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0.2, "to": "@end"},
          {"type": "screen", "player": "O4", "n": 1, "facing": -0.82, "from": "pin-down,", "to": "@end"},
          {"type": "route", "player": "O2", "t0": 0.75, "t1": 2.5, "trail": True, "from": "pin-down,", "to": "@end"},
          {"type": "ring", "player": "O1", "from": "straight", "to": "@end"}],
  "screen": [{"type": "title", "lines": ["CHICAGO ACTION"], "gold": [0], "sub": "Pin-down into a handoff", "from": "Chicago", "to": "@end", "y": 252, "size": 104},
             {"type": "pin", "player": "X2", "text": "X2", "tone": "red", "from": 0.3, "to": "Chicago-0.05", "size": 44}],
  "sfx": []},
 {"id": "caseA", "name": "Case A — he trails: hand to hands to first dribble, turn the corner, big deep, pull-up", "at": "If he-0.15", "play": "A",
  "remap": [[0, 1.3], ["take", 2.35], ["tight.>", 2.8], ["deep.", 3.75], ["@end-0.35", 5.1], ["@end", 5.25]],
  "camera": [key(0, OBL(fol(["O2", "O1", "X2"], 1.0), 8.8)), key("tight.>", OBL(fol(["O2", "O1", "X2"], 1.0, lead=0.15), 8.4), "inOut"),
             key("deep.", OBL(fol(["O2", "X4"], 1.0), 9.2, 18), "inOut"), key("@end", OBL([-1.2, 3.6, 1.6], 9.6, 14), "linear")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "tight.>"},
          {"type": "separation", "a": "X2", "b": "O2", "from": "tight.>", "to": "deep."},
          {"type": "route", "player": "O2", "t0": 2.6, "t1": 3.85, "trail": True, "from": "Turn", "to": "@end-0.6"},
          {"type": "ring", "player": "X4", "color": RED, "from": "big", "to": "@end-0.6"},
          {"type": "openSpace", "at": [-1.75, 4.6], "r": 1.0, "from": "stays deep", "to": "@end-0.8"}],
  "screen": [{"type": "title", "lines": ["TRAILS", "→ TAKE IT"], "gold": [1], "from": 0.05, "to": "@end", "y": 250, "size": 104},
             {"type": "pin", "player": "X4", "text": "DEEP", "tone": "red", "from": "big", "to": "@end-0.8", "size": 40},
             {"type": "stamp", "text": "PULL-UP", "badge": "+2", "from": "@end-0.55", "to": "@end", "y": 330}],
  "sfx": []},
 {"id": "caseB1", "name": "Case B — same overhead, same start: X2's feet (slow), freeze in the exchange line, the plant", "at": "Now watch-0.2", "play": "B",
  "remap": [[0, 0.55], ["feet.>", 1.3], ["He jumps", 1.72], ["exchange", 2.0], ["Keep the ball.>", 2.05], ["@end", 2.24, "in"]],
  "camera": [key(0, TOP), key("exchange", TOP_IN, "inOut"), key("@end", TOP_IN, "linear")],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "pulse": True, "from": "watch", "to": "@end"},
          {"type": "route", "player": "X2", "t0": 0.85, "t1": 2.2, "color": RED, "trail": True, "from": "feet.", "to": "@end"},
          {"type": "ring", "player": "O1", "from": "before", "to": "@end"},
          {"type": "route", "player": "O2", "t0": 2.15, "t1": 3.65, "dashed": True, "draw": 0.6, "from": "plants,", "to": "@end"}],
  "screen": [{"type": "title", "lines": ["JUMPS", "→ BACKDOOR"], "gold": [1], "from": "He jumps", "to": "@end", "y": 250, "size": 104},
             {"type": "freeze", "label": "BEFORE THE HANDOFF", "from": "exchange+0.15", "to": "Keep the ball.>"},
             ],
  "sfx": []},
 {"id": "caseB2", "name": "Case B — lateral: backdoor cut, bounce pass to the hands, late help, finish", "at": "goes backdoor-0.05", "play": "B",
  "remap": [[0, 2.24], ["pass", 3.0], ["help.>", 3.75], ["@end", 4.6]],
  "camera": [key(0, SIDE(fol(["O2", "O1"], 1.0), 10.0)), key("pass", SIDE(fol(["O2"], 1.0, lead=0.2), 8.6), "inOut"),
             key("@end", SIDE([-1.0, 2.6, 1.6], 8.4), "linear")],
  "ov3": [{"type": "passLane", "src": "O1", "dst": "O2", "from": 0.2, "to": "pass"},
          {"type": "ring", "player": "X5", "color": RED, "from": "beats", "to": "@end-0.5"}],
  "screen": [{"type": "title", "lines": ["JUMPS", "→ BACKDOOR"], "gold": [1], "from": 0, "to": "help.>", "y": 250, "size": 104},
             {"type": "pin", "player": "X5", "text": "LATE", "tone": "red", "from": "beats", "to": "@end-0.5", "size": 40},
             {"type": "stamp", "text": "BACKDOOR", "badge": "+2", "from": "help.>+0.15", "to": "@end", "y": 330}],
  "sfx": []},
 {"id": "cmpA", "name": "Same start — TOP, A: X2 trailing", "at": "Same start-0.1", "play": "A",
  "remap": [[0, 1.75], ["@end", 2.35]],
  "camera": [key(0, TOP_IN)],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"}, {"type": "separation", "a": "X2", "b": "O2", "from": 0.1, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["TRAILS", "→ TAKE IT"], "gold": [1], "from": 0.05, "to": "@end", "y": 250, "size": 104}], "sfx": []},
 {"id": "cmpB", "name": "Same start — TOP, B: X2 in the exchange line", "at": "defender before-0.05", "play": "B",
  "remap": [[0, 1.65], ["@end", 2.2]],
  "camera": [key(0, TOP_IN)],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"}, {"type": "route", "player": "X2", "t0": 0.85, "t1": 2.2, "color": RED, "trail": True, "from": 0, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["JUMPS", "→ BACKDOOR"], "gold": [1], "from": 0.05, "to": "@end", "y": 250, "size": 104}], "sfx": []},
 {"id": "cta", "name": "CTA — TOP, the play in motion: CHASE / JUMP / SWITCH?", "at": "You're guarding-0.2", "play": "B",
  "remap": [[0, 0.6], ["@end", 3.4]],
  "camera": [key(0, TOP), key("@end", {**TOP, "dist": 14.0}, "linear")],
  "ov3": [{"type": "ring", "player": "O2", "from": 0, "to": "@end"}, {"type": "ring", "player": "X2", "color": RED, "pulse": True, "from": 0.1, "to": "@end"}],
  "screen": [{"type": "scrim", "opacity": 0.28, "from": "Chase,-0.2", "to": "@end"},
             {"type": "title", "lines": ["CHASE / JUMP", "/ SWITCH?"], "gold": [1], "from": "Chase,", "to": "@end", "y": 600, "size": 124},
             {"type": "logo", "big": False, "from": "@end-1.1", "to": "@end"}],
  "sfx": []},
]
ep["shots"] = shots
ep["keywords"] = ["JUMPS", "opened the rim", "Chicago action", "pin-down", "handoff", "trails", "tight", "big stays deep",
                  "feet", "exchange", "Keep the ball", "plants", "backdoor", "help", "Read the defender", "Chase", "jump", "switch"]
ep["subtitleHide"] = []
ep["autoSfx"] = {"bounce": 0.12, "catch": 0.09, "squeak": 0.05, "swish": 0.16, "land": 0.05}
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.06}
ep["music"] = {"src": "tactical/chicago/music.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots))
