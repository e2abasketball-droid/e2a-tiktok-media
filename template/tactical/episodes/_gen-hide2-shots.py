#!/usr/bin/env python3
"""HIDE IN GAMES V2 (owner brief 2026-11-17 19:28Z), 53.3 s: one missed shot and the next two possessions.
  hook     3/4 on the rim and #8: the miss hits the ring in the first second (ONE MISSED SHOT)
  react    medium: the arm comes down, the shoulders fall
  practice floor level, warm gym: catch, square up, the ball goes up -> match cut on the rise
  game     same framing in the game, the rise completes
  miss     3/4: release, rim, landing, eyes follow the rebound, X8 takes it and the game goes on (no voice around the impact)
  hideA    possession 2, medium: half a hand comes up and goes back (WHAT IF I MISS AGAIN?)
  hideB    behind the passer: X8 in the lane, #8 stays, O3 offers, the pass goes to O3
  reset    medium in a pause: exhale, short tap on the jersey, eyes back on the passer
  askP     possession 3, SAME passer framing as hideB: plant, slide, the lane opens (gold line), hands, catch
  askAlt   the ask again from the other side (slow)
  shot     3/4 (the opening framing): catch, square up, release while X8 is late
  final    medium on #8 after the release (E2A sign-off)
  arc      3/4: the ball near the rim -> loops into the hook"""
import json, math, os, shutil, sys
D = os.path.dirname(os.path.abspath(__file__))
T_ = os.path.dirname(os.path.dirname(D))
base = json.load(open(os.path.join(D, "hide2.json")))


def cam(pos, tgt, fov=40):
    d = [pos[i] - tgt[i] for i in range(3)]
    dist = math.sqrt(sum(x * x for x in d))
    return {"type": "orbit", "target": tgt, "dist": round(dist, 3), "pitch": round(math.degrees(math.acos(d[2] / dist)), 2),
            "yaw": round(math.degrees(math.atan2(-d[0], d[1])), 2), "fov": fov}


def follow(dx, dy, z, dz=1.45, fov=38, who="O8"):
    """orbit that follows a player, camera at offset (dx, dy) metres and height z"""
    dist = math.sqrt(dx * dx + dy * dy + (z - dz) ** 2)
    return {"type": "orbit", "target": {"follow": who, "z": dz, "window": 0.6}, "dist": round(dist, 3),
            "pitch": round(math.degrees(math.acos((z - dz) / dist)), 2), "yaw": round(math.degrees(math.atan2(-dx, dy)), 2), "fov": fov}


key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
MISS3Q = cam([-10.0, 7.0, 1.7], [-1.6, 3.2, 2.0], 46)        # rim + #8 in the same 3/4 (hook, miss, last shot, loop)
FLOOR = cam([-7.9, 6.6, 1.1], [-4.2, 3.9, 1.55], 40)       # floor level, practice == game for the match cut
WIDE_P = cam([9.5, 14.5, 6.0], [-1.0, 7.0, 0.6], 46)          # behind the passer: #8, X8, O3 and the ball (possessions 2 and 3)
SIDE_A = cam([-1.6, 3.0, 1.55], [-4.35, 4.3, 1.35], 38)       # the ask from the other side
CLOSE_R = follow(*json.loads(os.environ.get("CR", "[2.4, -0.6, 1.6]")))       # front of #8 at the shot spot (reaction / final)
MED_H = follow(*json.loads(os.environ.get("MH", "[1.9, 2.05, 1.7, 1.5]")))        # possession 2 medium (face, hand)
MED_R = follow(*json.loads(os.environ.get("MR", "[2.1, 2.3, 1.6, 1.35]")))       # reset: shoulders, hands, torso

FACES = {"headScale": 1.38, "nums": {"X8": "14", "X1": "5", "X3": "21"},
         "hair": {"O8": "#3A2414", "O1": "#1A120C", "O3": "#2B1A10", "X8": "#2B1A10", "X1": "#4A3020", "X3": "#1A120C"},
         "skin": {"O8": "#D9A27A", "O1": "#8D5A3B", "O3": "#B57A52", "X8": "#C68E63", "X1": "#6B4630", "X3": "#E0B08A"}}


def shots():
    return [
     {"id": "hook", "name": "3/4: the open miss hits the ring in the first second", "at": 0, "play": "M", "env": "game",
      "remap": [[0, 3.33], [0.5, 3.65], ["@end", 3.95]],
      "camera": [key(0, MISS3Q), key("@end", MISS3Q)],
      "screen": [{"type": "title", "lines": ["ONE MISSED SHOT"], "gold": [0], "from": 0.1, "to": "@end"}]},
     {"id": "react", "name": "Medium: the arm comes down, the shoulders fall", "at": "suddenly,", "play": "M", "env": "game",
      "remap": [[0, 3.78], ["ball.>", 5.3], ["@end", 5.6]],
      "camera": [key(0, CLOSE_R), key("@end", {**CLOSE_R, "dist": round(CLOSE_R["dist"] * 0.9, 3)})]},
     {"id": "practice", "name": "Practice, floor level: catch, square up, the ball goes up", "at": "In-0.15", "play": "P", "env": "practice",
      "remap": [[0, 0.6], ["@end", 3.78]],
      "camera": [key(0, FLOOR), key("@end", FLOOR)]},
     {"id": "game", "name": "Match cut on the rise: the same shot in the game", "at": "game", "play": "M", "env": "game",
      "remap": [[0, 2.18], ["@end", 2.42]],
      "camera": [key(0, FLOOR), key("@end", FLOOR)]},
     {"id": "miss", "name": "3/4: release, rim, landing, rebound, the game goes on", "at": "starts.>", "play": "M", "env": "game",
      "remap": [[0, 2.42], ["rim.>+0.4", 3.65], ["rim.>+1.7", 4.4], ["@end", 6.6]],
      "camera": [key(0, MISS3Q), key("rim.>+1.2", MISS3Q), key("@end", {**MISS3Q, "fov": 48}, "inOut")]},
     {"id": "hideA", "name": "Possession 2, medium: half a hand comes up and goes back", "at": "Next-0.15", "play": "H", "env": "game",
      "remap": [[0, 0.9], ["What if", 2.05], ["again?>", 2.95], ["@end", 3.15]],
      "camera": [key(0, MED_H), key("@end", {**MED_H, "dist": round(MED_H["dist"] * 0.92, 3)})],
      "screen": [{"type": "title", "lines": ["WHAT IF I", "MISS AGAIN?"], "gold": [1], "from": "What if", "to": "@end"}]},
     {"id": "hideB", "name": "Behind the passer: #8 stays hidden, the pass goes to O3", "at": "again?>+0.15", "play": "H", "env": "game",
      "remap": [[0, 3.15], ["The pass", 5.15], ["else.>", 6.0], ["@end", 7.6]],
      "camera": [key(0, WIDE_P), key("@end", WIDE_P)]},
     {"id": "reset", "name": "Pause, medium: exhale, short tap, eyes back on the passer", "at": "Give-0.15", "play": "A", "env": "game",
      "remap": [[0, 0.3], ["Breathe-0.4", 1.6], ["out.>+0.15", 3.3], ["out.>+0.25", 3.4], ["out.>+0.85", 4.0], ["Find+0.1", 4.25], ["@end", 5.45]],
      "camera": [key(0, MED_R), key("@end", MED_R)]},
     {"id": "askP", "name": "Possession 3, passer framing: plant, slide, the lane opens, hands, catch", "at": "Move-0.25", "play": "A", "env": "game",
      "remap": [[0, 5.6], ["Move", 5.9], ["you.>", 6.75], ["Show", 7.2], ["Call", 7.85], ["Call for it.>+0.75", 8.8], ["@end", 9.05]],
      "camera": [key(0, WIDE_P), key("@end", WIDE_P)],
      "ov3": [{"type": "passLane", "src": "O1", "dst": "O8", "color": "#C9A24D", "from": "you.>-0.35", "to": "Show+0.45"}]},
     {"id": "askAlt", "name": "The ask again, from the other side (slow)", "at": "Call for it.>+1.15", "play": "A", "env": "game",
      "remap": [[0, 7.3], ["@end", 8.25]],
      "camera": [key(0, SIDE_A), key("@end", SIDE_A)]},
     {"id": "shot", "name": "3/4: catch, square up, release while X8 is late", "at": "nervous.", "play": "A", "env": "game",
      "remap": [[0, 8.55], ["shoots.", 10.6], ["@end", 10.95]],
      "camera": [key(0, MISS3Q), key("@end", MISS3Q)]},
     {"id": "final", "name": "Medium on #8 after the release, E2A sign-off", "at": "shoots.>+0.75", "play": "A", "env": "game",
      "remap": [[0, 10.88], ["@end", 11.9]],
      "camera": [key(0, CLOSE_R), key("@end", {**CLOSE_R, "dist": round(CLOSE_R["dist"] * 1.12, 3)})],
      "screen": [{"type": "logo", "from": "For more", "to": "@end"}]},
     {"id": "arc", "name": "3/4: the ball near the rim (loops into the hook)", "at": "basketball.>+1.17", "play": "A", "env": "game",
      "remap": [[0, 11.33], ["@end", 11.47]],
      "camera": [key(0, MISS3Q), key("@end", MISS3Q)]},
    ]


SFX = {"hook": [], "react": [], "practice": [], "game": [{"at": 0, "name": "whoosh", "volume": 0.05}], "miss": [], "hideA": [], "hideB": [],
       "reset": [{"at": "out.>+0.3", "name": "tick", "volume": 0.08}], "askP": [], "askAlt": [], "shot": [], "final": [], "arc": []}

if __name__ == "__main__":
    ep = dict(base)
    ep["id"] = "hide2-main"
    ep.pop("wordsRaw", None)
    ep.pop("gaps", None)
    ep["plays"] = {"P": "h2-practice", "M": "h2-miss", "H": "h2-hide", "A": "h2-ask"}
    ep["shots"] = shots()
    for sh in ep["shots"]:
        sh["sfx"] = SFX[sh["id"]]
    ep["faces"] = FACES
    ep["pinV2"] = True
    ep["autoSfx"] = {"bounce": 0.15, "catch": 0.2, "squeak": 0.08, "swish": 0.0, "rim": 0.42, "land": 0.16, "players": ["O8", "X8", "O1"]}
    ep["keywords"] = ["missed shot", "practice", "game starts", "rim", "miss again", "somewhere else", "one job", "next spot", "show your hands", "anyway", "shoots"]
    ep["subtitleGroups"] = [3, 7, 5, 3, 4, 5, 3, 6, 5, 3, 5, 4, 6, 7, 6, 3, 5, 6, 4]
    ep["subtitleHide"] = [["For more-0.05", "basketball.>+3"]]
    ep["subtitleYAt"] = [["Next-0.15", "again?>+0.15", 1345], ["Give-0.15", "Move-0.25", 1345]]
    ep["music"] = {"src": "tactical/hide2/music-mix.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, "hide2-main.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "hide2.words.json"), os.path.join(D, "hide2-main.words.json"))
    ep["words"] = json.load(open(os.path.join(D, "hide2.words.json")))
    ep["plays"] = {k: json.load(open(os.path.join(T_, "tactical", "plays", f"{v}.json"))) for k, v in ep["plays"].items()}
    os.makedirs("/tmp/claude-0/hide2", exist_ok=True)
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/hide2/hide2-main.props.json"
    json.dump({"episode": ep}, open(out, "w"))
    print("hide2-main", len(ep["shots"]), "shots")
