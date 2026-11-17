#!/usr/bin/env python3
"""HOW TO PUNISH THE SWITCH: shots on the master narration (owner brief 2026-11-17 12:50Z).
Two outputs share the same voice, words and timeline:
  switch-main   the Reel
  switch-trial  the trial-reel copy (owner rule 2026-11-16: never the identical file): different opening camera and
                title, a different closing question; the ffmpeg variant pass (zoom/grade/EQ) is applied on top.
Shots (voice anchors):
  hook      0 -> "Big on the guard"       ball screen in motion, SWITCH! on the swap
  replay    "Big on the guard ... Now what?"   elevated replay, BIG ON GUARD / SMALL ON BIG
  freeze    0.95 s freeze on the post-switch frame: INSIDE OR OUTSIDE?, fine ring on O5
  insideA   "Look inside first ... seal?"  A develops: O5 seals X1 behind him
  sealA     "He's got the guard pinned ... feed him."  DEEP SEAL, lateral step on "change the angle", dashed pass, finish
  rew       9-frame rewind to the same post-switch frame
  denyB     "But what if that entry pass is gone?"  ENTRY DENIED, short line to O5 cut at X1
  driveB    "Same switch ... Get past his hip."  overhead, change of pace, drive arrow, X5 recovers late
  recapA / recapB   "Deep seal? Feed it." / "Entry denied and space outside? Attack the big."  same overhead framing
  question  the post-switch frame again: INSIDE OR OUTSIDE?
  close     "For more European basketball."  short E2A sign-off, ends on the hook's first frame (loop)"""
import copy, json, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(D, "switch.json")))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED = "#E5483A"
WHITE = "#FFFFFF"
GOLD = "#C9A24D"
T = 3.6          # decision point (play time), same in A and B
PF = T - 0.04    # post-switch frame used for every return
H0 = 0.5         # hook's first play time (the close ends here, so the loop joins)

TAC = orb([-0.9, 5.6, 0], 19.0, 42, -12, 42)            # tactical three-quarter: rim, paint, the four players of the action
HOOK0 = orb([-0.2, 7.6, 0.4], 21.5, 46, -8, 42)         # opening: elevated, the ball screen up top and the rim
HOOK1 = orb([-0.6, 6.6, 0.2], 20.0, 44, -12, 42)
REP = orb([-0.6, 6.4, 0.3], 17.0, 50, -16, 42)          # elevated replay of the switch
POST = orb([-1.0, 4.6, 0.4], 13.5, 46, -14, 42)         # closer on the post
TOP = orb([-0.9, 5.2, 0], 16.5, 7, 0, 42)              # overhead used for the drive and both recaps
FIN_A = orb([-0.9, 3.2, 0.9], 9.4, 56, -10, 44)
TOP_IN = orb([-1.0, 4.0, 0], 14.0, 12, 0, 42)       # overhead push-in on the finish
HOOK0_T = orb([-0.4, 7.0, 0], 21.0, 14, 0, 42)          # trial copy: overhead start that tilts into the three-quarter


def shots(v):
    hook0 = HOOK0 if v == "main" else HOOK0_T
    hook_title = ["PICK YOUR", "MISMATCH"] if v == "main" else ["WHICH", "MISMATCH?"]
    return [
     {"id": "hook", "name": "Hook - ball screen, the switch, SWITCH! on the swap", "at": 0, "play": "A",
      "remap": [[0, H0], ["you.>", "switch"], ["@end", 3.0, "out"]],
      "camera": [key(0, hook0), key("@end", HOOK1, "inOut")],
      "ov3": [{"type": "ring", "player": "O5", "color": GOLD, "from": 0.2, "to": "you.>"}],
      "screen": [{"type": "stamp", "text": "SWITCH!", "from": "you.>-0.12", "to": "Now pick-0.05", "y": 330},
                 {"type": "title", "lines": hook_title, "gold": [1], "from": "Now pick", "to": "@end", "y": 262, "size": 108}]},
     {"id": "replay", "name": "Elevated replay: big on the guard, small on the big", "at": "Big on the guard-0.15", "play": "A",
      "remap": [[0, 1.55], ["Big on the guard>", 2.2], ["Small on the big>", 2.9], ["what?>", PF]],
      "camera": [key(0, REP), key("@end", TAC, "inOut")],
      "ov3": [{"type": "ring", "player": "X5", "color": RED, "from": "Big on the guard", "to": "@end"},
              {"type": "ring", "player": "X1", "color": RED, "from": "Small on the big", "to": "@end"}],
      "screen": [{"type": "pin", "player": "X5", "text": "BIG ON GUARD", "tone": "red", "from": "Big on the guard", "to": "@end"},
                 {"type": "pin", "player": "X1", "text": "SMALL ON BIG", "tone": "red", "from": "Small on the big", "to": "@end"}]},
     {"id": "freeze", "name": "Freeze 0.95 s on the post-switch frame: inside or outside?", "at": "what?>+0.05", "play": "A",
      "remap": [[0, PF], ["@end", PF]],
      "camera": [key(0, TAC), key("@end", TAC)],
      "ov3": [{"type": "ring", "player": "O5", "color": GOLD, "size": 0.8, "from": 0, "to": "@end"}],
      "screen": [{"type": "freeze", "label": "FREEZE", "from": 0.03, "to": "@end"},
                 {"type": "title", "lines": ["INSIDE", "OR OUTSIDE?"], "gold": [0], "from": 0.03, "to": "@end", "y": 262, "size": 108}]},
     {"id": "insideA", "name": "A - look inside first: O5 seals the small behind him", "at": "Look-0.45", "play": "A",
      "remap": [[0, PF], ["inside first.>", 3.85], ["a seal?>", 4.3]],
      "camera": [key(0, TAC), key("@end", POST, "inOut")],
      "ov3": [{"type": "ring", "player": "O5", "color": GOLD, "size": 0.8, "from": 0, "to": "@end"}],
      "screen": [{"type": "title", "lines": ["LOOK INSIDE"], "gold": [0], "from": 0.05, "to": "@end", "y": 262, "size": 108}]},
     {"id": "sealA", "name": "A - deep seal, change the angle, feed him, short finish", "at": "He's-0.15", "play": "A",
      "remap": [[0, 4.3], ["pinned.>", 4.42], ["change the", "angle"], ["angle,>", "angled"], ["feed him", "pass"],
                ["him.>", "catch"], ["him.>+1.05", "layup"], ["him.>+1.5", "make"], ["@end", 7.6]],
      "camera": [key(0, POST), key("feed him", POST), key("him.>+0.9", FIN_A, "inOut"), key("@end", FIN_A)],
      "ov3": [{"type": "ring", "player": "X1", "color": RED, "from": 0, "to": "change the"},
              {"type": "route", "player": "O1", "t0": "angle", "t1": "angled", "trail": True, "from": "change the", "to": "him.>"},
              {"type": "passLane", "src": "O1", "dst": "O5", "color": WHITE, "from": "feed him", "to": "him.>"},
              {"type": "ring", "player": "O5", "from": "him.>+1.0", "to": "@end", "pulse": True}],
      "screen": [{"type": "stamp", "text": "DEEP SEAL", "from": "He's", "to": "him.>+0.9", "y": 330},
                 {"type": "stamp", "text": "FEED THE POST", "badge": "+2", "from": "him.>+1.5", "to": "@end", "y": 330}]},
     {"id": "rew", "name": "Rewind 9 frames to the post-switch frame", "at": "But-0.45", "play": "A",
      "remap": [[0, 7.6], ["@end", PF]],
      "camera": [key(0, TAC), key("@end", TAC)],
      "screen": [{"type": "rewind", "from": 0, "to": "@end"}]},
     {"id": "denyB", "name": "B - same frame, X1 fronts: the entry pass is gone", "at": "But-0.15", "play": "B",
      "remap": [[0, PF], ["what if", PF], ["gone?>", 4.6], ["@end", 4.64]],
      "camera": [key(0, TAC), key("@end", POST, "inOut")],
      "ov3": [{"type": "passLane", "src": "O1", "dst": [-1.2, 4.75], "color": RED, "from": "entry pass", "to": "@end"},
              {"type": "ring", "player": "X1", "color": RED, "from": "gone?", "to": "@end"}],
      "screen": [{"type": "stamp", "text": "ENTRY DENIED", "from": "gone?", "to": "@end", "y": 330}]},
     {"id": "driveB", "name": "B - overhead: big in space, change pace, past his hip, layup", "at": "Same-0.15", "play": "B",
      "remap": [[0, 4.64], ["in space.>", 4.7], ["Change pace>", 5.22], ["Get past", "go"], ["hip.>", "hip"],
                ["hip.>+0.75", "layup"], ["hip.>+1.15", "make"], ["@end", 8.3]],
      "camera": [key(0, TOP), key("Get past", TOP), key("@end", TOP_IN, "inOut")],
      "ov3": [{"type": "ring", "player": "X5", "color": RED, "from": "Same", "to": "Get past"},
              {"type": "route", "player": "O1", "t0": "go", "t1": "layup", "from": "Change pace", "to": "hip.>+0.75"},
              {"type": "route", "player": "X5", "t0": "go", "t1": "layup", "color": RED, "width": 0.14, "trail": True, "from": "Get past", "to": "hip.>+0.75"},
              {"type": "ring", "player": "O1", "from": "hip.>+0.75", "to": "@end", "pulse": True}],
      "screen": [{"type": "pin", "player": "X5", "text": "BIG IN SPACE", "tone": "red", "from": "Now you've", "to": "Change pace-0.05"},
                 {"type": "stamp", "text": "CHANGE PACE", "from": "Change pace", "to": "hip.>+0.6", "y": 330},
                 {"type": "stamp", "text": "ATTACK THE BIG", "badge": "+2", "from": "hip.>+1.15", "to": "@end", "y": 330}]},
     {"id": "recapA", "name": "Recap A - deep seal: feed it (same overhead)", "at": "Deep-0.15", "play": "A",
      "remap": [[0, 4.0], ["Feed it", "pass"], ["Feed it>", "catch"], ["@end", 6.5]],
      "camera": [key(0, TOP), key("@end", TOP)],
      "ov3": [{"type": "ring", "player": "O5", "color": GOLD, "from": 0, "to": "@end"},
              {"type": "passLane", "src": "O1", "dst": "O5", "color": WHITE, "from": "Feed it", "to": "Feed it>+0.4"}],
      "screen": [{"type": "title", "lines": ["DEEP SEAL", "→ FEED IT"], "gold": [1], "from": 0.05, "to": "@end", "y": 262, "size": 104}]},
     {"id": "recapB", "name": "Recap B - space outside: drive (same overhead)", "at": "Entry denied-0.15", "play": "B",
      "remap": [[0, 4.3], ["outside?>", 4.9], ["Attack", "go"], ["Attack the big>", 6.5], ["@end", 7.2]],
      "camera": [key(0, TOP), key("@end", TOP)],
      "ov3": [{"type": "ring", "player": "X1", "color": RED, "from": 0, "to": "Attack"},
              {"type": "route", "player": "O1", "t0": "go", "t1": "layup", "trail": True, "from": "Attack", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["SPACE OUTSIDE", "→ DRIVE"], "gold": [1], "from": 0.05, "to": "@end", "y": 262, "size": 100}]},
     {"id": "question", "name": "Back to the post-switch frame: inside or outside?", "at": "What did-0.3", "play": "A",
      "remap": [[0, 3.1], ["@end", PF]],
      "camera": [key(0, HOOK1), key("@end", TAC, "inOut")],
      "ov3": [{"type": "ring", "player": "O5", "color": GOLD, "size": 0.8, "from": 0.2, "to": "@end"}],
      "screen": [{"type": "title", "lines": (["INSIDE", "OR OUTSIDE?"] if v == "main" else ["WHAT DID", "YOU SEE FIRST?"]), "gold": [1], "from": 0.05, "to": "@end", "y": 262, "size": 104 if v == "main" else 96}]},
     {"id": "close", "name": "E2A sign-off, ends on the hook's first frame (loop)", "at": "For more-0.15", "play": "A",
      "remap": [[0, 0.2], ["basketball.>+0.5", H0 - 0.05], ["@end", H0]],
      "camera": [key(0, TAC), key("basketball.>+0.5", hook0, "inOut"), key("@end", hook0)],
      "screen": [{"type": "scrim", "opacity": 0.55, "from": 0, "to": "basketball.>+0.45"},
                 {"type": "title", "lines": ["FOR MORE", "EUROPEAN", "BASKETBALL"], "gold": [1, 2], "from": 0.05, "to": "basketball.>+0.45", "y": 560, "size": 132},
                 {"type": "logo", "big": True, "from": "European", "to": "basketball.>+0.45"}]},
    ]


SFX = {"hook": [{"at": 0, "name": "whoosh", "volume": 0.1}, {"at": "you.>-0.12", "name": "impact", "volume": 0.08}],
       "replay": [{"at": 0, "name": "whip", "volume": 0.07}],
       "freeze": [{"at": 0, "name": "impact", "volume": 0.08}],
       "insideA": [],
       "sealA": [{"at": "He's", "name": "tick", "volume": 0.15}],
       "rew": [{"at": 0, "name": "reverse_cymbal", "volume": 0.11}],
       "denyB": [{"at": "gone?", "name": "tick", "volume": 0.15}],
       "driveB": [{"at": 0, "name": "whoosh", "volume": 0.07}, {"at": "Change pace", "name": "tick", "volume": 0.15}],
       "recapA": [{"at": 0, "name": "tick", "volume": 0.15}],
       "recapB": [{"at": 0, "name": "tick", "volume": 0.15}],
       "question": [{"at": 0, "name": "whoosh", "volume": 0.08}],
       "close": [{"at": 0, "name": "impact", "volume": 0.07}]}
VERSIONS = {"main": "switch-main", "trial": "switch-trial"}
for v, eid in VERSIONS.items():
    ep = copy.deepcopy(base)
    ep["id"], ep["version"] = eid, v
    ep["title"] = "How to Punish the Switch - " + ("Reel" if v == "main" else "trial-reel copy")
    ep.pop("wordsRaw", None)
    ep["shots"] = shots(v)
    plays = {k: json.load(open(os.path.join(os.path.dirname(os.path.dirname(D)), "tactical", "plays", f"{n}.json"))) for k, n in ep["plays"].items()}
    for sh in ep["shots"]:
        rm = sh.get("remap", [])
        for r in rm:
            if isinstance(r[1], str):
                r[1] = round(plays[sh["play"]]["marks"][r[1]], 3)
        for o in sh.get("ov3", []):
            for k in ("t0", "t1"):
                if isinstance(o.get(k), str):
                    o[k] = round(plays[o.get("fromPlay", sh["play"])]["marks"][o[k]], 3)
        sh["sfx"] = copy.deepcopy(SFX[sh["id"]])
    ep["pinV2"] = True
    ep["autoSfx"] = {"bounce": 0.16, "catch": 0.12, "squeak": 0.09, "swish": 0.26, "land": 0.07, "players": ["O1", "O5", "X1", "X5"]}
    ep["keywords"] = ["switched", "mismatch", "on the guard", "on the big", "cut off", "inside", "a seal", "pinned", "dribble",
                      "change the angle", "entry pass", "Same switch", "in space", "his hip", "Deep seal",
                      "Entry denied", "Attack the big", "see first"]
    ep["subtitleHide"] = [["For more-0.05", "basketball.>+3"]]
    ep["subtitleGroups"] = [5, 4, 4, 4, 6, 3, 6, 5, 3, 6, 3, 5, 5, 4, 6, 4, 5, 3, 5, 4]
    ep["music"] = {"src": "tactical/switch/music-mix.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "switch.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")
