#!/usr/bin/env python3
"""THE EUROSTEP: shots on the master narration (owner brief 2026-11-18 20:25Z, sections 4-7).
Two outputs share the same voice, words and timeline:
  eurostep-main   the Reel
  eurostep-trial  trial-reel copy (owner rule 2026-11-16: never the identical file): other hook framing + hook/close
                  titles ("HE GUARDS LEFT. WATCH WHAT OPENS."), then the ffmpeg variant pass (zoom/grade/EQ).
Graphic grammar (brief §7): gold + numbers = the attacker's counted steps (shoe prints pinned to the floor on the
contact frame, counter GATHER ○○ -> ●● driven by play time); coral = the defender's reaction (hip axis + short trail);
gold lane = the space that opens. Directions are the ATTACKER's (his left = +x)."""
import copy, json, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(D, "eurostep.json")))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
fol = lambda ids, z=0.7, w=0.5: {"follow": ids, "z": z, "window": w}
GOLD = "#E0B455"
CORAL = "#F06A55"
WHITE = "#FFFFFF"
LABELS = ["1 · LEFT", "2 · RIGHT"]
STEP1_AT = [1.12, 4.58]          # left plant (play A and B)
STEP2_AT = [-0.68, 3.38]         # right plant (play A)

HOOK = orb(fol(["O1", "X1"]), 5.6, 64, 20, 46)          # high three-quarter behind the attacker: shoes, base, rim
HOOK_T = orb(fol(["O1", "X1"], 0.6), 7.4, 46, -12, 44)  # trial: higher, from the attacker's left
GATH = orb(fol("O1", 0.8), 4.6, 74, 60, 42)              # right side: dribble hand, ball, right foot
COUNT = orb(fol("O1", 0.6), 6.0, 56, 35, 44)             # a touch wider: hands + base + the left foot landing
SELL = orb(fol("O1", 1.0), 4.8, 68, 25, 42)              # chest and eyes to the left lane
DEF = orb(fol(["O1", "X1"]), 5.5, 66, 10, 44)            # over the attacker's shoulder onto the defender's hips
REVEAL = orb([0.1, 3.6, 0], 8.5, 35, 0, 42)              # stable high axis: both feet, both lanes, rim
FIN = orb(fol("O1", 1.6), 6.5, 80, 70, 44)               # lateral three-quarter: knee, release hand, rim
FIN2 = orb(fol("O1", 1.8), 6.8, 78, 62, 44)
REP = orb([0.2, 4.6, 0], 12.0, 50, 10, 40)               # wide stable replay
REP2 = orb([0.0, 3.4, 0], 10.5, 52, 8, 40)


def prints(n=2, opacity=1.0, play_from=0):
    return [{"type": "print", "player": "O1", "n": k, "color": GOLD, "opacity": opacity, "from": play_from, "to": "@end"} for k in range(1, n + 1)]


def counter(y=262, frm=0, to="@end"):
    return {"type": "stepCount", "player": "O1", "labels": LABELS, "y": y, "from": frm, "to": to}


def shots(v):
    hook_cam = HOOK if v == "main" else HOOK_T
    hook_title = ["WATCH", "HIS FEET"] if v == "main" else ["HE GUARDS LEFT.", "WATCH WHAT OPENS."]
    close_title = ["WHICH SIDE", "DO YOU TRUST?"]
    return [
     {"id": "hook", "name": "Hook: high three-quarter behind O1; the fake lands, X1 loads toward the attacker's left; air on the right. Cut before step 2.",
      "at": 0, "play": "A",
      "remap": [[0, 0.85], ["He's", 1.5], ["wrong", 1.84], ["@end", 1.95]],
      "camera": [key(0, hook_cam), key("@end", orb(fol(["O1", "X1"]), 5.2, 64, 22, 46) if v == "main" else orb(fol(["O1", "X1"], 0.6), 6.8, 48, -10, 44), "inOut")],
      "ov3": [{"type": "hipMark", "player": "X1", "color": CORAL, "from": "wrong-0.1", "to": "@end"},
              {"type": "route", "player": "X1", "t0": 1.7, "t1": 1.95, "trail": True, "color": CORAL, "width": 0.1, "from": "about", "to": "@end"},
              {"type": "glow", "at": [-0.85, 3.2], "r": 0.9, "strength": 0.7, "from": "wrong lane>-0.4", "to": "@end"}],
      "screen": [{"type": "title", "lines": hook_title, "gold": [1], "from": 0.05, "to": "@end", "y": 262, "size": 104 if v == "main" else 84}]},
     {"id": "gather", "name": "Short rewind, last dribble and the gather on the move: hands, ball and the right foot already down",
      "at": "This is-0.08", "play": "A",
      "remap": [[0, 1.95], [0.3, 0.55], ["Secure the", 1.15], ["move.", 1.46], ["move.>+0.1", 1.47], ["@end", 1.48]],
      "camera": [key(0, GATH), key("@end", orb(fol("O1", 0.8), 4.3, 74, 58, 42), "inOut")],
      "ov3": [],
      "screen": [{"type": "rewind", "from": 0, "to": 0.3},
                 {"type": "title", "lines": ["THE EUROSTEP"], "gold": [0], "from": "Eurostep.", "to": "@end", "y": 262, "size": 100},
                 counter(y=420, frm="move.-0.25")]},
     {"id": "count", "name": "Gather -> the left foot lands: print 1 pinned on contact, 1/2, 1 · LEFT",
      "at": "The next-0.1", "play": "A",
      "remap": [[0, 1.44], ["land", 1.53], ["one.", 1.62], ["one.>+0.4", 1.655], ["@end", 1.67]],
      "camera": [key(0, COUNT), key("@end", orb(fol("O1", 0.7), 5.6, 68, 50, 44), "inOut")],
      "ov3": prints(1),
      "screen": [counter()]},
     {"id": "sell", "name": "Sell the left lane: chest and eyes, gold dashed guide from the left foot (the lane he shows)",
      "at": "Plant left-0.1", "play": "A",
      "remap": [[0, 1.57], ["Plant left", 1.62], ["left.>", 1.7], ["eyes.>", 1.8], ["@end", 1.82]],
      "camera": [key(0, SELL), key("@end", orb(fol("O1", 1.0), 4.6, 68, 22, 42), "inOut")],
      "ov3": prints(1) + [{"type": "route", "player": "O1", "t0": 0, "t1": 0, "pts": [STEP1_AT, [1.1, 3.4], [0.75, 2.3]], "dashed": True, "color": GOLD, "width": 0.12, "draw": 0.6, "from": "Sell that", "to": "@end"}],
      "screen": [counter()]},
     {"id": "def", "name": "Now the defender: hips turn after step 1 (coral hip axis), first slide traced; the right side stays open",
      "at": "See his-0.08", "play": "A",
      "remap": [[0, 1.66], ["hips", 1.74], ["turn?>", 1.86], ["opening.", 1.9], ["@end", 1.93]],
      "camera": [key(0, DEF), key("@end", orb(fol(["O1", "X1"]), 5.2, 64, 8, 44), "inOut")],
      "ov3": prints(1) + [{"type": "hipMark", "player": "X1", "color": CORAL, "from": "hips-0.05", "to": "@end"},
                          {"type": "route", "player": "X1", "t0": 1.7, "t1": 1.95, "trail": True, "color": CORAL, "width": 0.1, "from": "hips", "to": "@end"},
                          {"type": "glow", "at": [-0.75, 3.3], "r": 1.0, "strength": 0.8, "from": "That's your", "to": "@end"}],
      "screen": [counter()]},
     {"id": "reveal", "name": "Stable high axis: push off the left, the right foot travels to the open lane, print 2 + 2/2 on contact, gold lane to the rim",
      "at": "Push off-0.1", "play": "A",
      "remap": [[0, 1.8], ["Plant right", 1.93], ["right in", 1.98], ["open lane>", 2.07], ["@end", 2.1]],
      "camera": [key(0, REVEAL), key("@end", orb([0.0, 3.5, 0], 8.0, 36, 0, 42), "inOut")],
      "ov3": prints(2) + [{"type": "route", "player": "X1", "t0": 1.7, "t1": 2.0, "color": CORAL, "width": 0.08, "from": 0, "to": "@end"},
                          {"type": "route", "player": "O1", "t0": 0, "t1": 0, "pts": [STEP2_AT, [-0.55, 2.6], [-0.2, 1.8]], "color": GOLD, "width": 0.16, "draw": 0.5, "from": "open lane", "to": "@end"},
                          {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.7, "strength": 0.6, "from": "open lane", "to": "@end"}],
      "screen": [counter()]},
     {"id": "finish", "name": "Lateral three-quarter on the take-off: right knee loads, right-hand release, off the glass, late contest",
      "at": "Push up-0.12", "play": "A",
      "remap": [[0, 2.08], ["off the right>", 2.3], ["Finish right-handed", 2.42], ["reach.", 3.02], ["@end", 3.5]],
      "camera": [key(0, FIN), key("@end", FIN2, "inOut")],
      "ov3": prints(2, 0.6) + [{"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.6, "strength": 0.5, "from": "Finish right-handed", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["RIGHT FOOT.", "RIGHT HAND."], "gold": [1], "from": "Finish right-handed", "to": "@end-0.15", "y": 262, "size": 96}]},
     {"id": "square", "name": "Same start, same high axis: the defender keeps his chest between ball and rim; step 2 ends in balance",
      "at": "But what-0.1", "play": "B",
      "remap": [[0, 1.2], ["square?", 1.62], ["square?>", 1.98], ["@end", 2.25]],
      "camera": [key(0, REVEAL), key("@end", orb([0.0, 3.7, 0], 8.0, 36, 0, 42), "inOut")],
      "ov3": prints(2) + [{"type": "ring", "player": "X1", "color": CORAL, "size": 0.8, "from": "stays", "to": "@end"}],
      "screen": [counter(), {"type": "stamp", "text": "DEFENDER HOLDS", "tone": "white", "from": "square?>", "to": "@end", "y": 420}]},
     {"id": "read", "name": "Reframe the moment BEFORE the pick-up: the defender is square, read him there",
      "at": "Read his-0.1", "play": "B",
      "remap": [[0, 2.25], [0.3, 1.05], ["position", 1.22], ["pick up", 1.4], ["pick up the ball>", 1.44], ["@end", 1.45]],
      "camera": [key(0, HOOK), key("@end", orb(fol(["O1", "X1"]), 5.2, 64, 18, 46), "inOut")],
      "ov3": [{"type": "ring", "player": "X1", "color": WHITE, "size": 0.8, "from": "position", "to": "@end"}],
      "screen": [{"type": "rewind", "from": 0, "to": 0.3},
                 {"type": "title", "lines": ["READ HIM", "BEFORE THE GATHER"], "gold": [1], "from": "Read his", "to": "@end", "y": 262, "size": 88}]},
     {"id": "replay", "name": "Full speed, one wide stable camera: last dribble, gather, 1, 2, release, glass, net (prints at lower presence)",
      "at": "Here it-0.06", "play": "A",
      "remap": [[0, 0.0], ["Sell left>-0.56", 1.62], ["Sell left>+0.98", 3.16], ["@end", 4.0]],
      "camera": [key(0, REP), key("Sell left", REP), key("Finish#2", REP2, "inOut"), key("@end", REP2)],
      "ov3": prints(2, 0.55),
      "screen": [counter(y=262, to="Finish#2>+0.1"),
                 {"type": "title", "lines": close_title, "gold": [1], "from": "Finish#2>+0.15", "to": "@end", "y": 262, "size": 104}]},
     {"id": "loop", "name": "Match cut back to the hook's stance (loop): the question stays, short logo",
      "at": "Finish#2>+1.55", "play": "A",
      "remap": [[0, 0.62], ["@end", 0.85]],
      "camera": [key(0, orb(fol(["O1", "X1"]), 6.2, 62, 18, 46) if v == "main" else orb(fol(["O1", "X1"], 0.6), 8.0, 46, -12, 44)), key("@end", hook_cam, "inOut")],
      "ov3": [],
      "screen": [{"type": "title", "lines": close_title, "gold": [1], "from": 0, "to": "@end", "y": 262, "size": 104},
                 {"type": "logo", "from": 0.1, "to": "@end"}]},
    ]


VERSIONS = {"main": "eurostep-main", "trial": "eurostep-trial"}
for v, eid in VERSIONS.items():
    ep = copy.deepcopy(base)
    ep["id"], ep["version"] = eid, v
    ep["title"] = "The Eurostep - " + ("Reel" if v == "main" else "trial-reel copy")
    ep.pop("wordsRaw", None)
    ep["shots"] = shots(v)
    for sh in ep["shots"]:
        sh["sfx"] = []
        for o in sh.get("ov3", []):
            if o["type"] in ("print", "glow", "route", "hipMark"):
                if o.get("from") == 0:
                    o["fin"] = 0.001
                if o.get("to") == "@end":
                    o["fout"] = 0.001
    ep["pinV2"] = True
    ep["autoSfx"] = False          # owner rule 2026-11-18: no ball bounces; voice + music only
    ep["keywords"] = ["feet", "wrong lane", "Eurostep", "on the move", "next foot", "step one", "Plant left", "chest and eyes",
                      "hips", "opening", "Push off", "Plant right", "open lane", "Push up", "right-handed", "square",
                      "before you pick up", "full speed", "Sell left", "Cut right", "Finish"]
    ep["subtitleY"] = 1350
    ep["music"] = {"src": "tactical/eurostep/music.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "eurostep.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")
