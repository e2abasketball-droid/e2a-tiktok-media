#!/usr/bin/env python3
"""Edit of 'RAM SCREEN V2' (2026-11-13), from the owner's V2 brief. Every cut and graphic is anchored to the
real narration (ram-screen-v2.words.json) and to play time; regenerate after changing gaps or plays.
One visual focus per moment; each shot reveals something new:
  hook      low 3/4 on O5 escaping while X5 goes around O4 (cut before the result)
  reveal    short rewind, high angle: O4 plants, X5 absorbs and goes around, O5 escapes -> RAM SCREEN
  question  the ball screen, X5 pinned (pin anchored to his real head), his first step opens the reads
  readA1/2  drop: separation, brake, rise, release and landing -> cut behind the shooter: flight, make, then +2
  readB1/2  blitz from the same instant on the same axis -> the gap, the pass in flight to the offered hands,
            the first step and the finish in ONE vertical axis (O1 bottom, O5 middle, rim top)
  cmpA/cmpB same camera, same play instant: X5 back (A) / X5 up (B)
  cta       DROP OR BLITZ?, discreet logo, camera back to the hook's framing (loop)
Sound: contact effects only (bounce, brake, catch, net, landing) at low level, no whooshes/impacts."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, 'ram-screen-v2.json')
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
fol = lambda ids, z=1.0, **k: {"follow": ids, "z": z, **k}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED, WHITE = "#E5483A", "#FFFFFF"

CAM_HOOK = orb(fol(["O5", "X5"], 1.0), 8.6, 68, -28, 44)        # low three-quarter, O5 running at camera, X5 behind
CAM_HIGH = orb([-1.6, 5.6, 0.4], 13.5, 46, -34, 42)             # high angle on the ram (O4, X5, O5 in one frame)
CAM_D = orb([0.5, 8.4, 1.0], 10.0, 56, -46)                      # divergence axis, identical in A and B
CAM_C = orb([0.0, 8.0, 0.5], 14.5, 46, -18, 40)                  # comparison: X5 back (y~5.5) and X5 up (y~10.3)

shots = [
 {"id": "hook", "name": "Hook — O5 escapes, X5 goes around the first screen", "at": 0, "play": "A",
  "remap": [[0, 1.0], ["@end", 3.15]],
  "camera": [key(0, CAM_HOOK), key("@end", orb(fol(["O5", "X5"], 1.0), 8.2, 70, -34, 44), "linear")],
  "ov3": [{"type": "ring", "player": "O5", "from": 0.35, "to": "@end"},
          {"type": "ring", "player": "X5", "color": RED, "from": 0.6, "to": "@end"},
          {"type": "separation", "a": "O5", "b": "X5", "from": 1.0, "to": "@end"}],
  "screen": [],
  "sfx": []},
 {"id": "reveal", "name": "Rewind, high angle: the first screen and the head start", "at": "Watch the first-0.15", "play": "A",
  "remap": [[0, 3.15], [0.4, 0.55, "inOut"], ["the first screen.>", 1.35], ["head start.>", 2.45], ["@end", 2.95]],
  "camera": [key(0, orb([-1.2, 6.0, 0.5], 12.5, 48, -32, 42)), key(0.4, CAM_HIGH, "inOut"),
             key("head start.>", orb([-0.9, 6.4, 0.5], 13.5, 48, -38, 42), "inOut"), key("@end", orb([-0.3, 7.2, 0.6], 13.0, 50, -42, 42), "linear")],
  "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": -0.785, "from": "the first", "to": "@end"},
          {"type": "ring", "player": "X5", "color": RED, "from": "It gives", "to": "@end"},
          {"type": "route", "player": "O5", "t0": 0.85, "t1": 2.95, "draw": 1.3, "from": "gives Five", "to": "@end"},
          {"type": "separation", "a": "O5", "b": "X5", "from": "head start", "to": "@end"}],
  "screen": [{"type": "rewind", "from": 0, "to": 0.4},
             {"type": "title", "lines": ["RAM SCREEN"], "gold": [0], "sub": "The screen before the screen", "from": "head start.>-0.1", "to": "@end", "y": 250, "size": 112}],
  "sfx": [{"at": 0, "name": "reverse_cymbal", "volume": 0.05}]},
 {"id": "question", "name": "The ball screen — watch the big's defender", "at": "Now watch-0.12", "play": "A",
  "remap": [[0, 2.85], ["defender.>", 3.15], ["@end", 3.4]],
  "camera": [key(0, orb([0.4, 8.2, 1.0], 10.6, 56, -44)), key("defender.>", CAM_D, "inOut"), key("@end", {**CAM_D, "dist": 9.6}, "linear")],
  "ov3": [{"type": "screen", "player": "O5", "n": 2, "facing": -0.427, "from": 0.1, "to": "@end"},
          {"type": "ring", "player": "X5", "color": RED, "pulse": True, "from": "big's defender", "to": "@end"}],
  "screen": [{"type": "pin", "player": "X5", "text": "X5", "tone": "red", "from": "big's defender", "to": "@end", "size": 48}],
  "sfx": []},
 {"id": "readA1", "name": "Read A — drop: X5 backs up, O1 brakes, rises, releases, lands", "at": "He backs-0.15", "play": "A",
  "remap": [[0, 3.25], ["backs up.>", 3.95], ["That's enough", 4.12], ["the pull-up", 4.5], ["@end", 4.98]],
  "camera": [key(0, CAM_D), key("backs up.>", orb(fol(["O1", "X5"], 1.1), 9.4, 62, -64), "inOut"),
             key("the pull-up", orb(fol("O1", 1.3), 7.2, 64, -52, 44), "inOut"), key("@end", orb(fol("O1", 1.4), 7.0, 64, -48, 44), "linear")],
  "ov3": [{"type": "ring", "player": "X5", "color": RED, "from": 0, "to": "That's enough"},
          {"type": "separation", "a": "X5", "b": "O1", "from": "backs up.>-0.2", "to": "the pull-up"},
          {"type": "ring", "player": "O1", "from": "enough room", "to": "the pull-up"}],
  "screen": [{"type": "title", "lines": ["DROP", "→ PULL-UP"], "gold": [1], "from": "He backs", "to": "@end", "y": 260, "size": 108}],
  "sfx": []},
 {"id": "readA2", "name": "Read A — behind the shooter: flight, make, then the result", "at": "pull-up.>+0.15", "play": "A",
  "remap": [[0, 4.85], [1.05, 5.62], ["@end-0.5", 6.15], ["@end", 6.3]],
  "camera": [key(0, orb([-0.7, 5.6, 1.8], 9.4, 68, 8, 44)), key(1.05, orb([-0.4, 4.4, 2.1], 8.8, 70, 9, 44), "inOut"), key("@end", orb([-0.4, 4.2, 2.1], 8.6, 70, 9, 44), "linear")],
  "ov3": [],
  "screen": [{"type": "stamp", "text": "PULL-UP", "badge": "+2", "from": 1.25, "to": "@end", "y": 330}],
  "sfx": []},
 {"id": "readB1", "name": "Read B — same instant, same axis: X5 jumps the ball", "at": "Same setup-0.15", "play": "B",
  "remap": [[0, 2.1], ["Now both", 3.0], ["the ball.>", 3.75], ["@end", 3.85]],
  "camera": [key(0, CAM_D), key("Now both", CAM_D, "linear"), key("the ball.>", orb([-0.1, 9.9, 1.0], 12.6, 56, -38), "inOut"), key("@end", orb([-0.1, 9.9, 1.0], 12.4, 56, -38), "linear")],
  "ov3": [{"type": "ring", "player": "X5", "color": RED, "from": "Now both", "to": "@end"},
          {"type": "ring", "player": "X1", "color": RED, "from": "both defenders", "to": "@end"}],
  "screen": [{"type": "title", "lines": ["BLITZ", "→ SHORT ROLL"], "gold": [1], "from": "Now both", "to": "@end", "y": 260, "size": 108}],
  "sfx": []},
 {"id": "readB2", "name": "Read B — the gap, the pass to the offered hands, the steps, the finish", "at": "Five is open-0.6", "play": "B",
  "remap": [[0, 3.85], ["open on-0.1", 4.38], ["short roll.>", 4.62], ["@end-1.3", 5.75], ["@end", 6.3]],
  "camera": [key(0, orb([0.4, 8.6, 1.4], 9.6, 66, 4, 44)), key("open on-0.1", orb(fol("O5", 1.3, lead=0.2), 8.8, 68, 4, 44), "inOut"),
             key("@end-1.3", orb([0.1, 3.4, 1.9], 8.4, 72, 4, 44), "inOut"), key("@end", orb([0.1, 3.2, 2.0], 8.2, 72, 4, 44), "linear")],
  "ov3": [{"type": "passLane", "src": "O1", "dst": "O5", "from": 0.25, "to": "open on-0.1"},
          {"type": "ring", "player": "O5", "from": "open on-0.1", "to": "short roll.>+0.4"},
          {"type": "route", "player": "O5", "t0": 4.45, "t1": 5.4, "trail": True, "from": "short roll.>", "to": "@end-0.9"}],
  "screen": [{"type": "title", "lines": ["BLITZ", "→ SHORT ROLL"], "gold": [1], "from": 0, "to": "@end-1.3", "y": 260, "size": 108},
             {"type": "stamp", "text": "SHORT ROLL", "badge": "+2", "from": "@end-1.05", "to": "@end", "y": 330}],
  "sfx": []},
 {"id": "cmpA", "name": "Same play — X5 back (A)", "at": "Same play-0.15", "play": "A", "remap": [[0, 3.72], ["@end", 3.8]],
  "camera": [key(0, CAM_C)], "ov3": [{"type": "ring", "player": "X5", "color": RED, "from": 0, "to": "@end"}, {"type": "separation", "a": "X5", "b": "O1", "from": 0.1, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["BIG BACK"], "from": 0.05, "to": "@end", "y": 270, "size": 120}], "sfx": []},
 {"id": "cmpB", "name": "Same play — X5 up (B)", "at": "play.>+0.75", "play": "B", "remap": [[0, 3.72], ["@end", 3.8]],
  "camera": [key(0, CAM_C)], "ov3": [{"type": "ring", "player": "X5", "color": RED, "from": 0, "to": "@end"}, {"type": "separation", "a": "X5", "b": "O1", "from": 0.1, "to": "@end"}],
  "screen": [{"type": "title", "lines": ["BIG UP"], "gold": [0], "from": 0.05, "to": "@end", "y": 270, "size": 120}], "sfx": []},
 {"id": "cta", "name": "CTA — both options on the decision frame, back to the hook framing", "at": "Where would-0.25", "play": "A",
  "remap": [[0, 3.1], ["@end", 3.1]],
  "camera": [key(0, CAM_C), key("@end", CAM_HOOK, "inOut")],
  "ov3": [{"type": "ring", "player": "X5", "color": RED, "pulse": True, "from": 0, "to": "@end"},
          {"type": "route", "player": "X5", "t0": 3.1, "t1": 4.45, "color": RED, "draw": 0.5, "from": 0.2, "to": "@end"},
          {"type": "route", "player": "X5", "fromPlay": "B", "t0": 3.0, "t1": 3.8, "color": WHITE, "dashed": True, "draw": 0.5, "from": 0.5, "to": "@end"}],
  "screen": [{"type": "scrim", "opacity": 0.3, "from": "put the big?-0.2", "to": "@end"},
             {"type": "title", "lines": ["DROP", "OR BLITZ?"], "gold": [1], "from": "put the big?", "to": "@end", "y": 600, "size": 136},
             {"type": "logo", "big": False, "from": "put the big?>", "to": "@end"}],
  "sfx": []},
]
ep["shots"] = shots
ep["pinV2"] = True
ep["keywords"] = ["first screen", "head start", "defender", "backs up", "pull-up", "both defenders", "open", "short roll", "big"]
ep["subtitleHide"] = []
# light, contact-only sound (owner 2026-11-13: remove loud effects)
ep["autoSfx"] = {"bounce": 0.12, "catch": 0.09, "squeak": 0.05, "swish": 0.16, "land": 0.05}
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.06}
ep["music"] = {"src": "tactical/ram-v2/music.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots))
