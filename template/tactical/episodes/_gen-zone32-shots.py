#!/usr/bin/env python3
"""HOW TO BREAK A 3-2 ZONE: shots on the master narration (owner brief 2026-11-18 02:54Z).
Two outputs share the same voice, words and timeline:
  zone32-main   the Reel
  zone32-trial  the trial-reel copy (owner rule 2026-11-16: never the identical file): overhead opening that tilts down,
                other hook/close titles; the ffmpeg variant pass (zoom/grade/EQ) is applied on top.
Effects: the reusable 3D `wall` overlay (overlays3d.tsx) tied to X2-X1-X3 (top line) and X4-X5 (low line).
Colours (brief): solid gold = offensive movement, dashed gold = pass, ice white = defensive structure."""
import copy, json, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(D, "zone32.json")))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
GOLD = "#E0B455"
ICE = "#E4F4FF"
WHITE = "#FFFFFF"
NAIL = [0.1, 5.85]
TOPC = ["X2", "X1", "X3"]
LOWC = ["X4", "X5"]
PASS_IN = {"from": "O2", "to": "O5"}
CATCH = 3.0       # O5's catch at the nail (same frame in A and B)

LOW0 = orb([-0.5, 6.4, 0.6], 11.5, 64, 22, 46)        # low three-quarter behind O2: top line, ball, O5 behind
LOW1 = orb([-0.5, 6.3, 0.6], 10.6, 63, 18, 46)
TAC = orb([-1.0, 6.5, 0], 24.0, 50, -10, 42)           # tactical, rim at the top: all ten players
TAC2 = orb([-0.75, 6.5, 0], 19.5, 50, -3, 42)          # a touch closer: pass, flash and catch together
LOWD = orb([-1.5, 2.8, 0], 18.5, 50, -38, 42)         # low line, cutter, corner and rim
FIN_A = orb([-0.6, 3.4, 0.9], 8.6, 66, -24, 46)       # low three-quarter on the cut and layup
CORN = orb([-4.8, 2.8, 1.3], 8.8, 68, 125, 48)         # low three-quarter on the corner catch and shot
REP = orb([-1.5, 5.5, 0], 24.0, 30, -6, 44)           # elevated replay (same orientation)
CLOSE0 = orb([-0.5, 6.4, 0.6], 11.0, 64, 22, 46)
CLOSE1 = orb([-0.3, 6.0, 0.6], 9.6, 63, 16, 46)
TOP_T = orb([-0.6, 6.4, 0], 17.0, 12, 0, 42)          # trial: overhead start


def wall_top(**k):
    return {"type": "wall", "chain": TOPC, "pass": PASS_IN, **k}


def wall_low(**k):
    return {"type": "wall", "chain": LOWC, **k}


def shots(v):
    hook0 = LOW0 if v == "main" else TOP_T
    hook_title = ["BREAK", "THE 3–2"] if v == "main" else ["CAN YOU", "BREAK IT?"]
    close_title = ["THROUGH", "THE ZONE"] if v == "main" else ["ONE PASS.", "NO WALL."]
    return [
     {"id": "hook", "name": "Hook: low three-quarter on the top line, ball in O2's hands, O5 behind; cut before the pass crosses", "at": 0, "play": "A",
      "remap": [[0, 1.15], ["Wall.", 1.6], ["it.>+0.2", 2.47]],
      "camera": [key(0, hook0), key("@end", LOW1, "inOut")],
      "ov3": [wall_top(**{"draw": 0.55, "from": "Wall.-0.1", "to": "@end"}),
              {"type": "ring", "player": "O5", "color": GOLD, "size": 0.8, "from": "Watch what", "to": "@end"}],
      "screen": [{"type": "title", "lines": hook_title, "gold": [1], "from": 0.05, "to": "@end", "y": 262, "size": 124}]},
     {"id": "shape", "name": "Tactical: three up, two down, the defender in the middle", "at": "Three up-0.2", "play": "A",
      "remap": [[0, 0.0], ["@end", 0.4]],
      "camera": [key(0, TAC), key("@end", TAC)],
      "ov3": [wall_top(**{"draw": 0.45, "rise": 0.3, "from": "Three up", "to": "@end"}),
              wall_low(**{"draw": 0.35, "rise": 0.3, "from": "Two down", "to": "@end"}),
              {"type": "ring", "player": "X1", "color": WHITE, "size": 0.85, "from": "the defender in", "to": "middle.>+0.6"}],
      "screen": [{"type": "stamp", "text": "3 UP", "from": "Three up", "to": "Two down-0.05", "y": 330},
                 {"type": "stamp", "text": "2 LOW", "from": "Two down", "to": "Watch the defender-0.05", "y": 330},
                 {"type": "pin", "player": "X1", "text": "MIDDLE", "tone": "white", "from": "the defender in", "to": "@end"}]},
     {"id": "swing", "name": "Guards either side of X1, swing, X1 steps up, the panel opens, the nail lights after the step", "at": "Put a guard-0.15", "play": "A",
      "remap": [[0, 0.4], ["Swing the", 0.5], ["ball.>", 1.15], ["steps up.>", 1.62], ["@end", 1.66]],
      "camera": [key(0, TAC), key("@end", TAC2, "inOut")],
      "ov3": [wall_top(**{"open": {"pt0": 1.0, "pt1": 1.62, "w": 1.5}, "from": 0, "to": "@end"}),
              wall_low(**{"opacity": 0.8, "from": 0, "to": "@end"}),
              {"type": "ring", "player": "O1", "color": GOLD, "size": 0.85, "from": "guard on", "to": "Swing the"},
              {"type": "ring", "player": "O2", "color": GOLD, "size": 0.85, "from": "either side", "to": "Swing the"},
              {"type": "passLane", "src": "O1", "dst": "O2", "color": GOLD, "from": "Swing the", "to": "ball.>+0.2"},
              {"type": "ring", "player": "X1", "color": WHITE, "size": 0.85, "from": "The middle defender", "to": "@end"},
              {"type": "glow", "at": NAIL, "r": 1.3, "from": "steps up.>+0.05", "to": "@end"}],
      "screen": [{"type": "stamp", "text": "SWING", "from": "Swing the", "to": "The middle defender-0.05", "y": 330},
                 {"type": "stamp", "text": "HE STEPS UP", "from": "The middle defender", "to": "@end", "y": 330}]},
     {"id": "flash", "name": "O5 flashes to the nail (gold route as he runs), pass through the gap, crack, catch", "at": "Now your big-0.1", "play": "A",
      "remap": [[0, 1.5], ["line.>", 2.47], ["Hit him", 2.5], ["closes.>+0.55", CATCH], ["@end", 3.25]],
      "camera": [key(0, TAC2), key("@end", TAC2)],
      "ov3": [wall_top(**{"open": {"pt0": 1.0, "pt1": 1.62, "w": 1.5}, "crack": {"dur": 0.6}, "from": 0, "to": "@end"}),
              wall_low(**{"opacity": 0.8, "from": 0, "to": "@end"}),
              {"type": "glow", "at": NAIL, "r": 1.3, "from": 0, "to": "@end"},
              {"type": "route", "player": "O5", "t0": "plant", "t1": "nail", "trail": True, "color": GOLD, "from": 0, "to": "@end"},
              {"type": "passLane", "src": "O2", "dst": "O5", "color": GOLD, "from": "Hit him", "to": "closes.>+0.5"}],
      "screen": [{"type": "stamp", "text": "HIT THE NAIL", "from": "Hit him", "to": "@end", "y": 330}]},
     {"id": "lowfocus", "name": "Ball in O5's hands: watch the low defender (white ring on X4); O4, corner and rim visible", "at": "Now watch-0.1", "play": "A",
      "remap": [[0, 3.0], ["@end", 3.04]],
      "camera": [key(0, TAC2), key("defender.>", LOWD, "inOut"), key("@end", LOWD)],
      "ov3": [wall_top(**{"opacity": 0.3, "from": 0, "to": "@end"}),
              wall_low(**{"from": 0, "to": "@end"}),
              {"type": "ring", "player": "X4", "color": WHITE, "pulse": True, "from": "low defender", "to": "@end"},
              {"type": "ring", "player": "O5", "color": GOLD, "size": 0.8, "from": 0, "to": "@end"}],
      "screen": [{"type": "pin", "player": "X4", "text": "LOW DEFENDER", "tone": "white", "from": "low defender", "to": "@end"}]},
     {"id": "stepA", "name": "A: X4 steps up, O4 cuts behind him (route as he goes), lead pass", "at": "If he steps-0.1", "play": "A",
      "remap": [[0, 3.04], ["up,>", 3.55], ["him.>", 4.0], ["Lead the", "lead"], ["cutter>", 4.3]],
      "camera": [key(0, LOWD), key("@end", LOWD)],
      "ov3": [wall_top(**{"opacity": 0.3, "from": 0, "to": "@end"}),
              wall_low(**{"from": 0, "to": "@end"}),
              {"type": "ring", "player": "X4", "color": WHITE, "from": 0, "to": "cut behind"},
              {"type": "route", "player": "O4", "t0": "cut", "t1": "cutCatch", "color": GOLD, "draw": 0.6, "from": "cut behind", "to": "@end"},
              {"type": "passLane", "src": "O5", "dst": "O4", "color": GOLD, "from": "Lead the", "to": "@end"},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 1.0, "from": "Lead the", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["STEP UP", "→ CUT BEHIND"], "gold": [1], "from": "steps up,", "to": "@end", "y": 262, "size": 100}]},
     {"id": "finA", "name": "A: low three-quarter: the catch on the move and the layup; X5 late", "at": "cutter>-0.05", "play": "A",
      "remap": [[0, 4.3], ["rim.>+0.2", "layup"], ["rim.>+0.6", "make"], ["@end", 6.3]],
      "camera": [key(0, FIN_A), key("@end", orb([-0.4, 3.0, 1.0], 8.0, 64, -20, 46), "inOut")],
      "ov3": [wall_low(**{"opacity": 0.7, "from": 0, "to": "@end"}),
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 1.0, "from": 0, "to": "@end"}],
      "screen": []},
     {"id": "rew", "name": "8-frame rewind to the same catch, same framing", "at": "Same catch-0.3", "play": "A",
      "remap": [[0, 5.2], ["@end", CATCH]],
      "camera": [key(0, LOWD), key("@end", LOWD)],
      "ov3": [wall_top(**{"opacity": 0.3, "from": 0, "to": "@end"}), wall_low(**{"from": 0, "to": "@end"})],
      "screen": [{"type": "rewind", "from": 0, "to": "@end"}]},
     {"id": "sinkB", "name": "B: same catch, the low line sinks, the corner lights, kick-out (dashed gold)", "at": "Same catch-0.03", "play": "B",
      "remap": [[0, CATCH], ["Same catch>", 3.05], ["If they sink", 3.08], ["rim,>", 3.65], ["opens.>", 3.95], ["Make the kick-out", "kick"], ["kick-out.>", "cornerCatch"]],
      "camera": [key(0, LOWD), key("@end", LOWD)],
      "ov3": [wall_top(**{"opacity": 0.3, "from": 0, "to": "@end"}),
              wall_low(**{"from": 0, "to": "@end"}),
              {"type": "ring", "player": "O5", "color": GOLD, "size": 0.8, "from": 0, "to": "If they sink"},
              {"type": "glow", "player": "O3", "r": 1.1, "from": "the corner", "to": "@end"},
              {"type": "ring", "player": "O3", "color": GOLD, "from": "the corner", "to": "@end"},
              {"type": "route", "player": "X3", "t0": "x3rec", "t1": "cornerCatch", "color": ICE, "width": 0.12, "trail": True, "from": "kick-out", "to": "@end"},
              {"type": "passLane", "src": "O5", "dst": "O3", "color": GOLD, "from": "Make the kick-out", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["SINK IN", "→ CORNER"], "gold": [1], "from": "If they sink", "to": "@end", "y": 262, "size": 100}]},
     {"id": "shotB", "name": "B: corner catch, feet behind the arc, shot to the net", "at": "kick-out.>+0.02", "play": "B",
      "remap": [[0, "cornerCatch"], ["@end-0.6", "make"], ["@end", 6.5]],
      "camera": [key(0, CORN), key("@end", orb([-4.4, 2.6, 1.6], 8.2, 66, 120, 48), "inOut")],
      "ov3": [{"type": "glow", "player": "O3", "r": 1.0, "from": 0, "to": "@end"},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.6, "strength": 0.6, "from": 0, "to": "@end"}],
      "screen": []},
     {"id": "replay", "name": "Elevated replay in three beats: swing, nail catch, low defender's step", "at": "Move the middle-0.1", "play": "A",
      "remap": [[0, 0.5], ["the middle.>", 1.62], ["Touch", 2.3], ["nail.>", CATCH], ["Make the low", 3.02], ["Choose.>", 3.85], ["@end", 3.9]],
      "camera": [key(0, REP), key("@end", REP)],
      "ov3": [wall_top(**{"open": {"pt0": 1.0, "pt1": 1.62, "w": 1.5}, "opacity": 0.85, "from": 0, "to": "@end"}),
              wall_low(**{"from": 0, "to": "@end"}),
              {"type": "ring", "player": "X1", "color": WHITE, "size": 0.85, "from": 0, "to": "Touch"},
              {"type": "route", "player": "O5", "t0": "plant", "t1": "nail", "trail": True, "color": GOLD, "from": "Touch", "to": "@end"},
              {"type": "glow", "at": NAIL, "r": 1.2, "from": "Touch", "to": "Make the low"},
              {"type": "ring", "player": "X4", "color": WHITE, "pulse": True, "from": "Make the low", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["MOVE THE MIDDLE"], "gold": [0], "from": 0.05, "to": "Touch-0.03", "y": 262, "size": 96},
                 {"type": "title", "lines": ["TOUCH THE NAIL"], "gold": [0], "from": "Touch", "to": "Make the low-0.03", "y": 262, "size": 96},
                 {"type": "title", "lines": ["MAKE HIM", "CHOOSE"], "gold": [1], "from": "Make the low", "to": "@end", "y": 262, "size": 100}]},
     {"id": "close", "name": "Back to the hook's low shot: the pending pass crosses, the panel breaks around the crossing, O5 catches", "at": "For more-0.25", "play": "A",
      "remap": [[0, 2.2], ["European>", 3.15], ["@end", 3.4]],
      "camera": [key(0, CLOSE0), key("@end", CLOSE1, "inOut")],
      "ov3": [wall_top(**{"shatter": {"r": 0.55, "n": 14, "seed": 32, "dur": 0.42}, "from": 0, "to": "@end"}),
              {"type": "glow", "at": NAIL, "r": 1.1, "from": 0, "to": "@end"}],
      "screen": [{"type": "title", "lines": close_title, "gold": [1], "from": "more", "to": "@end", "y": 262, "size": 124},
                 {"type": "logo", "from": "European", "to": "@end"}]},
    ]


VERSIONS = {"main": "zone32-main", "trial": "zone32-trial"}
plays = {k: json.load(open(os.path.join(os.path.dirname(os.path.dirname(D)), "tactical", "plays", f"{n}.json"))) for k, n in base["plays"].items()}
for v, eid in VERSIONS.items():
    ep = copy.deepcopy(base)
    ep["id"], ep["version"] = eid, v
    ep["title"] = "How to Break a 3-2 Zone - " + ("Reel" if v == "main" else "trial-reel copy")
    ep.pop("wordsRaw", None)
    ep["shots"] = shots(v)
    for sh in ep["shots"]:
        for r in sh.get("remap", []):
            if isinstance(r[1], str):
                r[1] = round(plays[sh["play"]]["marks"][r[1]], 3)
        for o in sh.get("ov3", []):
            for k in ("t0", "t1"):
                if isinstance(o.get(k), str):
                    o[k] = round(plays[o.get("fromPlay", sh["play"])]["marks"][o[k]], 3)
        sh["sfx"] = []
        # continuous effects across cuts: no fade at a cut (from 0 / to @end), so the wall never blinks
        for o in sh.get("ov3", []):
            if o["type"] in ("wall", "glow", "route"):
                if o.get("from") == 0:
                    o["fin"] = 0.001
                if o.get("to") == "@end":
                    o["fout"] = 0.001
    ep["pinV2"] = True
    ep["autoSfx"] = False          # owner rule 2026-11-18: no ball bounces; voice + music only
    ep["keywords"] = ["wall", "one pass", "Three up", "Two down", "in the middle", "Swing the ball", "steps up", "flashes",
                      "foul line", "gap closes", "low defender", "cut behind", "to the rim", "Same catch", "sink",
                      "corner opens", "kick-out", "Touch the nail", "choose"]
    ep["subtitleGroups"] = [6, 7, 4, 6, 6, 3, 5, 4, 4, 6, 5, 7, 6, 5, 4, 3, 3, 3, 3, 5, 4]
    ep["subtitleY"] = 1500
    ep["subtitleHide"] = [["For more-0.05", "basketball.>+3"]]
    ep["music"] = {"src": "tactical/zone32/music.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "zone32.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")
