#!/usr/bin/env python3
"""HIDE IN GAMES V4 (owner brief 2026-11-18 02:39Z), ~53.5 s. Three moments: the miss changes him, the first attempt to
get back into the play fails, he tries again (catch, read, extra pass). Shot list (episode time from hide4.words.json):
  hook      3/4: rim impact at 0.6 s, the shooting arm stays up (ONE MISS)
  react     front medium: the arm drops, the eyes follow the rebound, he looks away
  back      wide follow: the torso turns to get back, the others react to the ball
  practice  warm gym, floor level: hands up, chest open (calls for it)
  game      SAME framing in the game: hands down, behind #14 (match cut on the hands)
  memory    3/4: brief memory of the rebound, quiet rim echo
  gaze      close: he avoids the passer's gaze
  thought   medium, hand visible: looks at the passer, half a hand, back at the end of the question (WHAT IF I MISS AGAIN?)
  pov       over #1's shoulder: #14 in the line, the second half hand goes back
  passer    behind the passer: O3 pops, the pass goes there (exit and catch on the same axis)
  still     tele medium: #8 stays still, eyes on the ball, the possession goes on
  reset     NEW possession, floor level: exhale, eyes up to the passer, ready; cut on his first step
  att1      raised 3/4: attempt 1, #14 follows and keeps the line, both plant feet, hesitation
  att2      low follow from the sideline: jab, load on the plant foot (ring), change of direction, separation, hands
            (CALL FOR IT AGAIN), the line opens (gold line)
  catch     behind the passer: the pass leaves after the line appears, two-hand catch ready to shoot
  read1     front medium from the rim side: ready to shoot, eyes rim -> #14 arriving with a high hand (0.69x)
  read2     high from the right baseline: #4 open, his defender still in the paint, eyes to #4, the pass (line on release)
  corner    cut on the pass: #4's full catch, #8 relocating
  drive     coach angle: #4 attacks, #14 helps, #8 drifts and gets it back
  relo      tele medium on #8: square, read, swing, relocate
  swing     high angle: the ball keeps moving
  cb1/cb2   callbacks: the plant foot, the hands asking
  final     live possession, #8 relocating with eyes on the ball, MAKE THE NEXT READ + discreet E2A signature"""
import importlib.util, json, os, shutil, sys
D = os.path.dirname(os.path.abspath(__file__))
T_ = os.path.dirname(os.path.dirname(D))
_s = importlib.util.spec_from_file_location("s2", os.path.join(D, "_gen-hide2-shots.py"))
s2 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(s2)
_s3 = importlib.util.spec_from_file_location("s3", os.path.join(D, "_gen-hide3-shots.py"))
s3 = importlib.util.module_from_spec(_s3)
_s3.loader.exec_module(s3)
cam, follow, key = s2.cam, s2.follow, s2.key
E = lambda n, d: json.loads(os.environ.get(n, json.dumps(d)))
MISS3Q, FLOOR, WIDE_P, CLOSE_R = s2.MISS3Q, s2.FLOOR, s2.WIDE_P, s2.CLOSE_R
FLOOR_G = cam(*E("FG", [[-7.85, 8.45, 1.1], [-4.15, 5.75, 1.55], 40]))            # FLOOR shifted to #8's game spot
BACK = follow(*E("BK", [-3.4, -3.0, 3.0, 1.2, 44]))
GAZE = follow(*E("GZ", [2.3, 1.3, 1.75, 1.52, 30]))
MED_T = follow(*E("MT", [1.3, 2.3, 1.7, 1.45, 38]))                                        # thought: face + hand
POV = cam(*E("PV", [[5.6, 9.3, 2.4], [-4.2, 5.85, 1.2], 30]))                         # over #1's shoulder
STILL = follow(*E("ST", [2.6, 1.6, 1.85, 1.5, 28]))
RESET = follow(*E("RS", [1.3, 2.4, 1.35, 1.45, 36]))
ATT1 = cam(*E("A1", [[-8.5, 13.8, 5.2], [-3.9, 6.6, 0.6], 40]))
ATT2 = follow(*E("A2", [-4.2, 2.2, 2.4, 0.8, 44]))
CATCH = cam(*E("CT", [[1.2, 10.2, 3.8], [-3.9, 4.8, 1.1], 40]))
READ1 = follow(*E("R1", [2.7, 0.5, 1.8, 1.4, 40]))
READ2 = cam(*E("R2", [[-10.6, -1.4, 6.2], [-4.3, 2.6, 0.5], 44]))
CORNER = cam(*E("CN", [[-2.4, -2.6, 2.5], [-6.0, 2.0, 1.0], 42]))
COACH, RELO, SWING, WIDE_F = s3.COACH, s3.RELO, s3.SWING, s3.WIDE_F
FACES = s3.FACES
base = json.load(open(os.path.join(D, "hide4.json")))
P0 = 20.2    # h4-ask play time = episode time - P0 (until the catch)
Q1 = 13.45 + 3.3 + 0.5   # O4 catch, play time


def shots():
    return [
     {"id": "hook", "name": "3/4: rim impact at 0.6 s, the arm stays up", "at": 0, "play": "M", "env": "game",
      "remap": [[0, 3.05], [0.6, 3.65], ["@end", 4.2]],
      "camera": [key(0, MISS3Q), key("@end", MISS3Q)],
      "screen": [{"type": "title", "lines": ["ONE MISS"], "gold": [0], "from": 0.05, "to": "@end"}]},
     {"id": "react", "name": "Front medium: the arm drops, eyes on the rebound, he looks away", "at": "Now he's", "play": "M", "env": "game",
      "remap": [[0, 4.2], ["@end", 5.45]],
      "camera": [key(0, CLOSE_R), key("@end", {**CLOSE_R, "dist": round(CLOSE_R["dist"] * 0.92, 3)})]},
     {"id": "back", "name": "Wide follow: the torso turns to get back, the others react to the ball", "at": "passes him", "play": "M", "env": "game",
      "remap": [[0, 5.45], ["@end", 6.6]],
      "camera": [key(0, BACK), key("@end", BACK)]},
     {"id": "practice", "name": "Warm practice, floor level: hands up, chest open", "at": "In-0.15", "play": "P", "env": "practice",
      "remap": [[0, 1.95], ["calls", 2.75], ["@end", 3.08]],
      "camera": [key(0, FLOOR), key("@end", FLOOR)]},
     {"id": "game", "name": "Same framing in the game: hands down behind #14 (match cut on the hands)", "at": "Now he keeps-0.05", "play": "H", "env": "game",
      "remap": [[0, 0.0], ["@end", 0.2]],
      "camera": [key(0, FLOOR_G), key("@end", FLOOR_G)]},
     {"id": "memory", "name": "3/4: brief memory of the rebound, quiet rim echo", "at": "hearing", "play": "M", "env": "game", "autoGain": 0,
      "remap": [[0, 3.45], ["@end", 4.45]],
      "camera": [key(0, {**MISS3Q, "fov": 40}), key("@end", {**MISS3Q, "fov": 38})]},
     {"id": "gaze", "name": "Close: he avoids the passer's gaze", "at": "miss.#2>-0.05", "play": "H", "env": "game",
      "remap": [[0, 0.2], ["@end", 0.95]],
      "camera": [key(0, GAZE), key("@end", {**GAZE, "dist": round(GAZE["dist"] * 0.95, 3)})]},
     {"id": "thought", "name": "Medium: looks at the passer, half a hand, back at the end of the question", "at": "What if-0.17", "play": "H", "env": "game",
      "remap": [[0, 0.95], ["@end", 4.55]],
      "camera": [key(0, MED_T), key("@end", {**MED_T, "dist": round(MED_T["dist"] * 0.93, 3)})],
      "screen": [{"type": "title", "lines": ["WHAT IF I", "MISS AGAIN?"], "gold": [1], "from": "What if", "to": "again?>+0.35"}]},
     {"id": "pov", "name": "Over #1's shoulder: #14 in the line, the hand goes back", "at": "Then-0.05", "play": "H", "env": "game",
      "remap": [[0, 4.55], ["@end", 6.45]],
      "camera": [key(0, POV), key("@end", POV)]},
     {"id": "passer", "name": "Behind the passer: O3 pops, the pass goes there", "at": "His teammate-0.05", "play": "H", "env": "game",
      "remap": [[0, 6.45], ["@end", 11.3]],
      "camera": [key(0, WIDE_P), key("@end", WIDE_P)]},
     {"id": "still", "name": "Tele medium: #8 stays still, eyes on the ball", "at": "else.>+0.15", "play": "H", "env": "game",
      "remap": [[0, 11.3], ["@end", 13.05]],
      "camera": [key(0, STILL), key("@end", STILL)]},
     {"id": "reset", "name": "New possession, floor level: exhale, eyes up, ready", "at": "He's still-0.05", "play": "A", "env": "game",
      "remap": [[0, 0.15], ["@end", 3.75]],
      "camera": [key(0, RESET), key("@end", {**RESET, "dist": round(RESET["dist"] * 0.9, 3)})]},
     {"id": "att1", "name": "Raised 3/4: attempt 1, #14 follows, no window", "at": "Get open", "play": "A", "env": "game",
      "remap": [[0, 3.75], ["@end", 8.65]],
      "camera": [key(0, ATT1), key("@end", ATT1)],
      "ov3": [{"type": "passLane", "src": "O1", "dst": "O8", "color": "#B23A3A", "from": "follows.>-0.5", "to": "follows.>+0.4"}]},
     {"id": "att2", "name": "Low follow: jab, plant (ring), change of direction, separation, hands", "at": "So he plants-0.35", "play": "A", "env": "game",
      "remap": [[0, 8.65], ["@end", 11.8]],
      "camera": [key(0, ATT2), key("@end", ATT2)],
      "ov3": [{"type": "ring", "player": "O8", "size": 0.7, "from": "plants,-0.2", "to": "direction,"},
              {"type": "passLane", "src": "O1", "dst": "O8", "color": "#C9A24D", "from": "calls again-0.25", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["CALL FOR IT", "AGAIN"], "gold": [1], "from": "calls again-0.05", "to": "@end"}]},
     {"id": "catch", "name": "Behind the passer: the pass after the line appears, two-hand catch", "at": "This time-0.33", "play": "A", "env": "game",
      "remap": [[0, 11.8], ["@end", 13.77]],
      "camera": [key(0, CATCH), key("@end", CATCH)]},
     {"id": "read1", "name": "Front medium: ready to shoot, eyes rim -> #14 arriving with a high hand", "at": "He's ready-0.1", "play": "A", "env": "game",
      "remap": [[0, 13.77], ["@end", 15.6]],
      "camera": [key(0, READ1), key("@end", {**READ1, "dist": round(READ1["dist"] * 1.06, 3)})]},
     {"id": "read2", "name": "High from the right baseline: #4 open, his defender in the paint, the pass", "at": "His teammate's-0.1", "play": "A", "env": "game",
      "remap": [[0, 15.6], ["@end", 16.78]],
      "camera": [key(0, READ2), key("@end", READ2)],
      "ov3": [{"type": "ring", "player": "O4", "size": 0.8, "from": "His teammate's+0.1", "to": "@end"}]},
     {"id": "corner", "name": "Cut on the pass: #4's full catch, #8 relocating", "at": "pass.#2>-0.55", "play": "A", "env": "game",
      "remap": [[0, 16.78], ["@end", Q1 + 1.0]],
      "camera": [key(0, CORNER), key("@end", CORNER)],
      "ov3": [{"type": "passLane", "src": "O8", "dst": "O4", "color": "#C9A24D", "from": 0, "to": 0.7}]},
     {"id": "drive", "name": "Coach angle: #4 attacks, #14 helps, #8 drifts and gets it back", "at": "pass.#2>+1.0", "play": "A", "env": "game",
      "remap": [[0, Q1 + 1.0], ["@end", Q1 + 3.2]],
      "camera": [key(0, COACH), key("@end", {**COACH, "dist": round(COACH["dist"] * 0.96, 3)})]},
     {"id": "relo", "name": "Tele medium on #8: square, read, swing, relocate", "at": "Even-0.15", "play": "A", "env": "game",
      "remap": [[0, Q1 + 3.2], ["@end", Q1 + 6.3]],
      "camera": [key(0, RELO), key("@end", RELO)]},
     {"id": "swing", "name": "High angle: the ball keeps moving", "at": "of the game.>+0.25", "play": "A", "env": "game",
      "remap": [[0, Q1 + 6.3], ["@end", Q1 + 10.0]],
      "camera": [key(0, SWING), key("@end", {**SWING, "dist": round(SWING["dist"] * 0.95, 3)})]},
     {"id": "cb1", "name": "Callback: the plant foot", "at": "do next.>+0.1", "play": "A", "env": "game", "autoGain": 0.6,
      "remap": [[0, 9.0], ["@end", 9.75]],
      "camera": [key(0, ATT2), key("@end", ATT2)],
      "ov3": [{"type": "ring", "player": "O8", "size": 0.7, "from": 0, "to": "@end"}]},
     {"id": "cb2", "name": "Callback: the hands asking", "at": "Ask-0.1", "play": "A", "env": "game", "autoGain": 0.6,
      "remap": [[0, 11.15], ["@end", 12.2]],
      "camera": [key(0, MED_T), key("@end", MED_T)]},
     {"id": "final", "name": "Live possession, #8 relocating with eyes on the ball, MAKE THE NEXT READ", "at": "Make-0.25", "play": "A", "env": "game",
      "remap": [[0, Q1 + 10.4], ["@end", Q1 + 12.3]],
      "camera": [key(0, WIDE_F), key("@end", {**WIDE_F, "dist": round(WIDE_F["dist"] * 0.93, 3)}, "inOut")],
      "screen": [{"type": "title", "lines": ["MAKE THE", "NEXT READ"], "gold": [1], "from": "Make-0.1", "to": "@end"},
                 {"type": "logo", "from": "read.>-0.3", "to": "@end"}]},
    ]


SFX = {"memory": [{"at": "hearing+0.12", "name": "rim", "volume": 0.13}, {"at": "hearing+0.32", "name": "rim", "volume": 0.05}],
       "reset": [{"at": 0, "name": "whoosh", "volume": 0.06}],
       "final": [{"at": "read.>-0.6", "name": "arena", "volume": 0.09}], "game": [{"at": 0, "name": "whoosh", "volume": 0.04}]}


if __name__ == "__main__":
    ep = dict(base)
    ep["id"] = "hide4-main"
    ep.pop("wordsRaw", None)
    ep.pop("gaps", None)
    ep["plays"] = {"P": "h2-practice", "M": "h4-miss", "H": "h4-hide", "A": "h4-ask"}
    ep["shots"] = shots()
    for sh in ep["shots"]:
        sh["sfx"] = SFX.get(sh["id"], [])
    ep["faces"] = FACES
    ep["pinV2"] = True
    ep["autoSfx"] = {"bounce": 0.15, "catch": 0.24, "squeak": 0.12, "swish": 0.0, "rim": 0.45, "land": 0.16, "players": ["O8", "X8", "O1", "O4", "X4"]}
    ep["keywords"] = ["one miss", "calls for it", "miss again", "pulls them back", "somewhere else", "one job", "get open again",
                      "defender follows", "changes direction", "pass comes", "ready to shoot", "teammate's open", "one more pass",
                      "part of the game", "what they do next", "ask for it again", "next read"]
    words = json.load(open(os.path.join(D, "hide4.words.json")))
    g = s3.groups(words)
    if g[0] < 3:   # "One miss." + the next sentence -> "One miss. Now he's hoping" / "nobody passes him the ball."
        n = g[0] + g[1] + g[2]   # the 8-word sentence was split [4, 4]
        g = [-(-n // 2), n // 2] + g[3:]
    i = 0
    for j, n in enumerate(g):   # "So he plants," / "changes direction, and calls again."
        if words[i]["text"] == "So" and words[i + 2]["text"] == "plants," and n == 4 and g[j + 1] == 4:
            g[j], g[j + 1] = 3, 5
            break
        i += n
    ep["subtitleGroups"] = g
    ep["subtitleYAt"] = [["What if-0.17", "Then-0.05", 1345], ["He's ready-0.1", "pass.#2>-0.55", 330]]
    ep["music"] = {"src": "tactical/hide4/music-mix.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, "hide4-main.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "hide4.words.json"), os.path.join(D, "hide4-main.words.json"))
    ep["words"] = words
    ep["plays"] = {k: json.load(open(os.path.join(T_, "tactical", "plays", f"{v}.json"))) for k, v in ep["plays"].items()}
    os.makedirs("/tmp/claude-0/hide4", exist_ok=True)
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/hide4/hide4-main.props.json"
    json.dump({"episode": ep}, open(out, "w"))
    print("hide4-main", len(ep["shots"]), "shots", "groups", ep["subtitleGroups"])
