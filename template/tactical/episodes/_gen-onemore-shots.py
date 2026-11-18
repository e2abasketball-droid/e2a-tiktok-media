#!/usr/bin/env python3
"""ONE MORE DRIBBLE: shots on the master narration (owner brief 2026-11-17 05:40Z).
Two outputs share the same voice, words and timeline:
  onemore-main   the Reel
  onemore-trial  the trial-reel copy (owner rule 2026-11-16: never the identical file): different opening camera and
                 title, a different closing question; the ffmpeg variant pass (zoom/grade/EQ) is applied on top.
Shots (voice anchors):
  hook      0 -> "Freeze"              2-on-1 in motion, #8 ringed on "wide open", HE LOOKS OPEN
  freeze    "Freeze it here ... dribble?"   freeze before the decision, PASS NOW? / ONE MORE DRIBBLE?
  earlyA    "Watch the early pass ... leaves."      tactical cam, release, STILL CENTRAL, catch
  topA      "From up here ... on the catch."        overhead replay of X10's route, CATCH CONTESTED
  rew       rewind 9 frames on the tactical axis back to the decision
  dribbleB  "Same setup. One more dribble. Watch his feet."   play B, the full extra dribble
  lowB      "There. That first step takes him toward the ball."   low shot behind X10, floor mark on his plant
  laneB     "Now the lane opens. Lead your teammate into the space."   overhead, lane line, dashed pass, layup
  hook2     "But what if he stays with the pass?"   play C, same frame, DEFENDER STAYS
  laneC     "Same dribble ... Go finish."   lane arrow, gather, layup (camera lowers at the finish)
  recapB / recapC   "Steps up? Pass." / "Takes away the pass? Finish."   same overhead, same frame
  question  back to the opening frame: PASS NOW OR ONE MORE?
  close     "For more European basketball."   short E2A sign-off, ends on the hook's first frame (loop)"""
import copy, json, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(D, "onemore.json")))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED = "#E5483A"
WHITE = "#FFFFFF"
T = 3.3          # decision point (play time), same in A, B and C
PF = T - 0.04    # freeze pose: ball back in the hand, same in every return

TAC = orb([-0.7, 6.1, 0], 18.5, 42, -22, 42)            # tactical three-quarter: rim, paint, all three players
HOOK0 = orb([-0.8, 8.1, 0.4], 20.5, 45, -14, 42)        # opening: elevated three-quarter, players and rim visible
HOOK1 = orb([-0.6, 6.6, 0.2], 19.5, 43, -22, 42)
TOP = orb([-0.7, 4.7, 0], 16.5, 7, 0, 42)              # overhead used for every distance comparison
LOW = {"type": "pov", "behind": "X10", "look": "O4", "back": 4.4, "height": 1.7, "side": -1.9, "fov": 46, "lookZ": 0.45}
FIN_C = orb([0.4, 3.2, 0.9], 9.0, 58, -8, 44)           # closer three-quarter on O4's finish
FIN_B = orb([-0.9, 3.4, 0.9], 9.4, 58, 6, 44)
# trial-copy opening: overhead start that tilts into the tactical three-quarter
HOOK0_T = orb([-0.6, 7.6, 0], 21.0, 14, 0, 42)


def shots(v):
    hook0, hook1 = (HOOK0, HOOK1) if v == "main" else (HOOK0_T, HOOK1)
    hook_title = ["HE LOOKS OPEN"] if v == "main" else ["WIDE OPEN?"]
    return [
     {"id": "hook", "name": "Hook - the 2-on-1 in motion, #8 looks open", "at": 0, "play": "A",
      "remap": [[0, 0.75], ["mistake?>+0.1", 3.0], ["@end", PF, "out"]],
      "camera": [key(0, hook0), key("@end", hook1, "inOut")],
      "ov3": [{"type": "ring", "player": "O8", "color": "#C9A24D", "from": "wide", "to": "mistake?>", "pulse": True},
              {"type": "ring", "player": "X10", "color": RED, "from": "mistake?>+0.3", "to": "@end"}],
      "screen": [{"type": "title", "lines": hook_title, "gold": [0], "from": "wide", "to": "@end", "y": 262, "size": 108}]},
     {"id": "freeze", "name": "Freeze before the decision: pass now or one more dribble?", "at": "Freeze-0.15", "play": "A",
      "remap": [[0, PF], ["@end", PF]],
      "camera": [key(0, HOOK1), key("here.>", TAC, "inOut"), key("@end", TAC)],
      "ov3": [{"type": "ring", "player": "X10", "color": RED, "from": 0, "to": "@end"},
              {"type": "passLane", "src": "O4", "dst": "O8", "color": WHITE, "from": "Pass now", "to": "dribble?>+1.0"},
              {"type": "passLane", "src": "O4", "dst": [1.5, 5.75], "color": "#C9A24D", "from": "one more", "to": "dribble?>+1.0"}],
      "screen": [{"type": "freeze", "label": "FREEZE", "from": 0.05, "to": "@end"},
                 {"type": "title", "lines": ["PASS NOW?"], "from": "Pass now", "to": "one more-0.05", "y": 262, "size": 108},
                 {"type": "title", "lines": ["PASS NOW?", "ONE MORE DRIBBLE?"], "gold": [1], "from": "one more", "to": "dribble?>+1.0", "y": 262, "size": 96}]},
     {"id": "earlyA", "name": "A - the early pass: still central when the ball leaves", "at": "Watch-0.2", "play": "A",
      "remap": [[0, PF], ["early", T], ["early pass>", "release"], ["leaves.>", 3.62], ["@end", 4.35]],
      "camera": [key(0, TAC), key("@end", orb([-0.9, 6.2, 0], 16.0, 40, 0, 42), "linear")],
      "ov3": [{"type": "ring", "player": "X10", "color": RED, "from": "The defender's", "to": "@end"},
              {"type": "ring", "player": "O8", "from": "leaves.>+0.6", "to": "@end", "pulse": True}],
      "screen": [{"type": "title", "lines": ["THE EARLY PASS"], "from": "Watch", "to": "The defender's-0.05", "y": 262, "size": 104},
                 {"type": "pin", "player": "X10", "text": "STILL CENTRAL", "tone": "red", "from": "still", "to": "leaves.>+0.5"}]},
     {"id": "topA", "name": "A - overhead replay: how little ground he covers, catch contested", "at": "From-0.15", "play": "A",
      "remap": [[0, 3.3], ["how", "release"], ["cover.>", 3.95], ["catch.>", "contest"], ["@end", 4.75]],
      "camera": [key(0, TOP), key("@end", orb([-1.0, 4.7, 0], 16.0, 7, 0, 42), "linear")],
      "ov3": [{"type": "route", "player": "X10", "t0": "slide", "t1": "contest", "trail": True, "width": 0.14, "color": RED, "from": "how", "to": "@end"},
              {"type": "ring", "player": "X10", "color": RED, "from": 0, "to": "@end"}],
      "screen": [{"type": "title", "lines": ["FROM UP HERE"], "from": 0.05, "to": "He's-0.05", "y": 262, "size": 104},
                 {"type": "stamp", "text": "CATCH CONTESTED", "from": "catch", "to": "@end", "y": 330}]},
     {"id": "rew", "name": "Rewind 9 frames on the tactical axis", "at": "Same-0.5", "play": "A",
      "remap": [[0, 4.75], ["@end", PF]],
      "camera": [key(0, TAC), key("@end", TAC)],
      "screen": [{"type": "rewind", "from": 0, "to": "@end"}]},
     {"id": "dribbleB", "name": "B - same setup, one more dribble, watch his feet", "at": "Same-0.2", "play": "B",
      "remap": [[0, PF], ["One more dribble. Watch his", PF], ["@end", 3.47]],
      "camera": [key(0, TAC), key("@end", orb([0.2, 6.2, 0.3], 14.2, 44, -6, 42), "inOut")],
      "ov3": [{"type": "ring", "player": "X10", "color": RED, "from": "Watch his", "to": "@end", "pulse": True}],
      "screen": [{"type": "title", "lines": ["SAME SETUP"], "from": 0.05, "to": "One more dribble. Watch his-0.05", "y": 262, "size": 108},
                 {"type": "title", "lines": ["ONE MORE DRIBBLE"], "gold": [0], "from": "One more dribble. Watch his", "to": "@end", "y": 262, "size": 104}]},
     {"id": "lowB", "name": "B - low shot behind X10: the first step toward the ball", "at": "feet.>+0.15", "play": "B",
      "remap": [[0, 3.5], ["There. That", 3.93], ["toward the ball>", 4.08], ["@end", 4.12]],
      "camera": [key(0, LOW), key("@end", LOW)],
      "ov3": [{"type": "openSpace", "at": [1.19, 4.79], "r": 0.3, "color": RED, "from": "There. That", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["FIRST STEP"], "gold": [0], "from": "There. That", "to": "@end", "y": 262, "size": 108}]},
     {"id": "laneB", "name": "B - overhead: the lane opens, lead pass, catch, layup", "at": "Now the lane-0.15", "play": "B",
      "remap": [[0, 4.12], ["opens.>", "pass"], ["space.>", 5.15], ["space.>+1.9", "make"], ["@end", 6.6]],
      "camera": [key(0, TOP), key("space.>", TOP), key("space.>+1.9", FIN_B, "inOut"), key("@end", FIN_B)],
      "ov3": [{"type": "passLane", "src": "O4", "dst": [-2.45, 4.85], "color": WHITE, "from": "lane", "to": "opens.>"},
              {"type": "route", "player": "O8", "t0": 4.12, "t1": 5.7, "trail": True, "from": "Lead", "to": "space.>+1.2"},
              {"type": "route", "player": "X10", "t0": "plant", "t1": "pass", "color": RED, "width": 0.14, "from": 0, "to": "opens.>"},
              {"type": "ring", "player": "O8", "from": "space.>+1.2", "to": "@end", "pulse": True}],
      "screen": [{"type": "stamp", "text": "LANE OPEN", "from": "opens", "to": "space.>+0.6", "y": 330},
                 {"type": "stamp", "text": "PASS + LAYUP", "badge": "+2", "from": "space.>+1.4", "to": "@end", "y": 330}]},
     {"id": "hook2", "name": "C - second hook: what if he stays with the pass?", "at": "But-0.15", "play": "C",
      "remap": [[0, PF], ["stays", PF], ["@end", 3.72]],
      "camera": [key(0, TAC), key("@end", TAC)],
      "ov3": [{"type": "ring", "player": "X10", "color": RED, "from": "with the pass>", "to": "@end"},
              {"type": "ring", "player": "O8", "from": "with the pass>", "to": "@end"}],
      "screen": [{"type": "rewind", "from": 0, "to": 0.3},
                 {"type": "title", "lines": ["DEFENDER STAYS"], "from": "with the pass>", "to": "@end", "y": 262, "size": 104}]},
     {"id": "laneC", "name": "C - same dribble, he stays, the lane is yours: finish", "at": "Same dribble-0.15", "play": "C",
      "remap": [[0, 3.72], ["with your teammate>", "stay"], ["yours.>", 4.42], ["Go finish>", "layup"], ["@end", 6.6]],
      "camera": [key(0, TAC), key("yours.>", orb([0.0, 5.3, 0.3], 14.0, 42, -4, 42), "inOut"), key("Go finish>-0.1", FIN_C, "inOut"), key("@end", FIN_C)],
      "ov3": [{"type": "ring", "player": "X10", "color": RED, "from": 0, "to": "yours.>"},
              {"type": "route", "player": "O4", "t0": 4.0, "t1": "layup", "from": "The lane is", "to": "Go finish>"},
              {"type": "ring", "player": "O4", "from": "Go finish>", "to": "@end", "pulse": True}],
      "screen": [{"type": "pin", "player": "X10", "text": "STAYS WITH THE PASS", "tone": "red", "from": "stays with your", "to": "yours.>"},
                 {"type": "stamp", "text": "THE LANE IS YOURS", "from": "The lane is", "to": "Go finish>+0.3", "y": 330},
                 {"type": "stamp", "text": "FINISH", "badge": "+2", "from": "Go finish>+0.6", "to": "@end", "y": 330}]},
     {"id": "recapB", "name": "Recap B - steps up: pass (same overhead)", "at": "Steps-0.15", "play": "B",
      "remap": [[0, 3.35], ["up? Pass>", 4.45], ["@end", 4.85]],
      "camera": [key(0, TOP), key("@end", TOP)],
      "ov3": [{"type": "route", "player": "X10", "t0": "plant", "t1": 3.85, "trail": True, "color": RED, "width": 0.14, "from": 0, "to": "@end"},
              {"type": "passLane", "src": "O4", "dst": [-2.45, 4.85], "color": WHITE, "from": "up? Pass", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["STEPS UP", "→ PASS"], "gold": [1], "from": 0.05, "to": "@end", "y": 262, "size": 104}]},
     {"id": "recapC", "name": "Recap C - stays with the pass: finish (same overhead)", "at": "Takes away-0.15", "play": "C",
      "remap": [[0, 3.35], ["pass? Finish>", 4.9], ["@end", 5.05]],
      "camera": [key(0, TOP), key("@end", TOP)],
      "ov3": [{"type": "route", "player": "X10", "t0": 3.5, "t1": 4.3, "trail": True, "color": RED, "width": 0.14, "from": 0, "to": "@end"},
              {"type": "route", "player": "O4", "t0": 3.4, "t1": "layup", "trail": True, "from": "pass? Finish", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["STAYS WITH THE PASS", "→ FINISH"], "gold": [1], "from": 0.05, "to": "@end", "y": 262, "size": 84}]},
     {"id": "question", "name": "Back to the opening frame: pass now or one more?", "at": "pass? Finish>+0.7", "play": "A",
      "remap": [[0, 0.6], ["@end", 2.75]],
      "camera": [key(0, HOOK1), key("@end", TAC, "inOut")],
      "ov3": [{"type": "ring", "player": "X10", "color": RED, "from": 0.3, "to": "@end"}],
      "screen": [{"type": "title", "lines": (["PASS NOW", "OR ONE MORE?"] if v == "main" else ["READ", "THE DEFENDER."]), "gold": [1], "from": 0.05, "to": "@end", "y": 262, "size": 104}]},
     {"id": "close", "name": "E2A sign-off, ends on the hook's first frame (loop)", "at": "For more-0.15", "play": "A",
      "remap": [[0, 0.25], ["basketball.>+0.5", 0.7], ["@end", 0.75]],
      "camera": [key(0, TAC), key("basketball.>+0.5", hook0, "inOut"), key("@end", hook0)],
      "screen": [{"type": "scrim", "opacity": 0.55, "from": 0, "to": "basketball.>+0.45"},
                 {"type": "title", "lines": ["FOR MORE", "EUROPEAN", "BASKETBALL"], "gold": [1, 2], "from": 0.05, "to": "basketball.>+0.45", "y": 560, "size": 132},
                 {"type": "logo", "big": True, "from": "European", "to": "basketball.>+0.45"}]},
    ]


SFX = {"hook": [{"at": 0, "name": "whoosh", "volume": 0.1}],
       "freeze": [{"at": "here.>-0.2", "name": "impact", "volume": 0.08}],
       "earlyA": [{"at": 0, "name": "whip", "volume": 0.08}],
       "topA": [{"at": 0, "name": "tick", "volume": 0.15}],
       "rew": [{"at": 0, "name": "reverse_cymbal", "volume": 0.11}],
       "dribbleB": [],
       "lowB": [{"at": 0, "name": "whoosh", "volume": 0.07}],
       "laneB": [{"at": "opens", "name": "tick", "volume": 0.15}],
       "hook2": [{"at": 0, "name": "reverse_cymbal", "volume": 0.1}],
       "laneC": [{"at": "The lane is", "name": "tick", "volume": 0.15}],
       "recapB": [{"at": 0, "name": "tick", "volume": 0.15}],
       "recapC": [{"at": 0, "name": "tick", "volume": 0.15}],
       "question": [{"at": 0, "name": "whoosh", "volume": 0.08}],
       "close": [{"at": 0, "name": "impact", "volume": 0.07}]}
VERSIONS = {"main": "onemore-main", "trial": "onemore-trial"}
for v, eid in VERSIONS.items():
    ep = copy.deepcopy(base)
    ep["id"], ep["version"] = eid, v
    ep["title"] = "One More Dribble - " + ("Reel" if v == "main" else "trial-reel copy")
    ep.pop("wordsRaw", None)
    ep["shots"] = shots(v)
    plays = {k: json.load(open(os.path.join(os.path.dirname(os.path.dirname(D)), "tactical", "plays", f"{n}.json"))) for k, n in ep["plays"].items()}
    for sh in ep["shots"]:
        for o in sh.get("ov3", []):
            for k in ("t0", "t1"):
                if isinstance(o.get(k), str):
                    o[k] = round(plays[o.get("fromPlay", sh["play"])]["marks"][o[k]], 3)
    for sh in ep["shots"]:
        sh["sfx"] = copy.deepcopy(SFX[sh["id"]])
    ep["pinV2"] = True
    ep["autoSfx"] = {"bounce": 0.16, "catch": 0.12, "squeak": 0.09, "swish": 0.26, "land": 0.07, "players": ["O4", "O8", "X10"]}
    ep["keywords"] = ["wide open", "mistake", "Freeze", "one more dribble", "early pass", "in the middle", "ball leaves", "up here",
                      "on the catch", "his feet", "first step", "toward the ball", "lane opens", "into the space", "what if",
                      "with the pass", "stays with", "Go finish", "Steps up", "Finish"]
    ep["subtitleHide"] = [["For more-0.05", "basketball.>+3"]]
    ep["subtitleGroups"] = [4, 7, 3, 7, 4, 6, 4, 6, 7, 5, 5, 3, 4, 5, 4, 6, 5, 3, 7, 6, 3, 5, 4]
    ep["music"] = {"src": "tactical/onemore/music-mix.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "onemore.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")
