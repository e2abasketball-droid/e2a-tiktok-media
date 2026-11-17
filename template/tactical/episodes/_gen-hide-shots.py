#!/usr/bin/env python3
"""HIDE IN GAMES: shots on the master narration (owner brief 2026-11-17 17:09Z). Original E2A character episode.
  hook      practice: #8 calls for it (warm gym) -> match cut inside the gesture -> game: X8 steps in, hands drop
  eyes      close on #8: his eyes follow the ball
  poss      passer's view: #8 hidden behind the defender, the ball goes the other way
  miss      #8's open shot hits the ring and kicks out
  reset     breathe out (shoulders drop), tap the jersey (1 · RESET), turn and get back
  offers    2 · SHOW A TARGET, offers 1 and 2 (0/3 -> 2/3) while the ball goes elsewhere
  offer3    plant, slide to the open line, show the hands (3/3), the pass line, the catch
  again     3 · ASK AGAIN: the miss, then the next possession in the hook framing: out from behind, hands, catch
  close     E2A sign-off on the practice run-in; ends on the hook's first frame (loop)"""
import json, math, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
T_ = os.path.dirname(os.path.dirname(D))
base = json.load(open(os.path.join(D, "hide.json")))


def cam(pos, tgt, fov=40):
    d = [pos[i] - tgt[i] for i in range(3)]
    dist = math.sqrt(sum(x * x for x in d))
    return {"type": "orbit", "target": tgt, "dist": round(dist, 3), "pitch": round(math.degrees(math.acos(d[2] / dist)), 2),
            "yaw": round(math.degrees(math.atan2(-d[0], d[1])), 2), "fov": fov}


key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
CAM_A = cam([-1.15, 5.0, 1.62], [-3.75, 5.72, 1.28], 40)                     # hook framing (same as the pilot)
CAM_AF = {**CAM_A, "target": {"follow": "O8", "z": 1.28, "offset": [0.25, 0.02], "window": 0.5}}   # hook framing that follows #8
CAM_EYES = {"type": "orbit", "target": {"follow": "O8", "z": 1.8, "window": 0.6}, "dist": 1.5, "pitch": 86, "yaw": -100, "fov": 34}
POV0 = {"type": "pov", "behind": "O1", "look": "O8", "back": 2.3, "height": 2.25, "side": 0.55, "fov": 44, "lookZ": 1.1}
POV1 = {"type": "pov", "behind": "O1", "look": "O3", "back": 2.3, "height": 2.25, "side": 0.55, "fov": 44, "lookZ": 1.1}
MISS = cam([-10.2, 7.4, 3.0], [-3.2, 3.2, 2.1], 42)
MISS_T = cam([-10.2, 7.4, 3.0], [-1.5, 2.0, 2.3], 28)                       # push-in on the rim: impact + lateral rebound
CLOSE = {"type": "orbit", "target": {"follow": "O8", "z": 1.45, "window": 0.6}, "dist": 2.6, "pitch": 84, "yaw": -78, "fov": 38}
WIDE = cam([14.5, 5.8, 13.0], [-0.8, 5.4, 0.4], 44)                        # high, from behind the passer: all three offers in frame
CAM_W = cam([9.8, 9.2, 5.6], [-0.6, 6.1, 0.8], 40)                           # pilot wide: passer, defender, receiver, ball

FACES = {"headScale": 1.38, "nums": {"X8": "14", "X1": "5", "X3": "21"}, "hair": {"O8": "#3A2414", "O1": "#1A120C", "O3": "#2B1A10", "X8": "#2B1A10", "X1": "#4A3020", "X3": "#1A120C"},
         "skin": {"O8": "#D9A27A", "O1": "#8D5A3B", "O3": "#B57A52", "X8": "#C68E63", "X1": "#6B4630", "X3": "#E0B08A"}}


def shots():
    return [
     {"id": "hook", "name": "Practice: #8 calls for it (warm open gym)", "at": 0, "play": "P", "env": "practice",
      "remap": [[0, 1.45], ["practice.>", 3.3], ["@end", 3.62]],
      "camera": [key(0, CAM_A), key("@end", CAM_A)]},
     {"id": "cut", "name": "Match cut inside the gesture: the defender steps in, the hands drop", "at": "So why", "play": "G", "env": "game",
      "remap": [[0, 2.85], ["drop", 3.45], ["games?>", 4.05], ["@end", 4.4]],
      "camera": [key(0, CAM_A), key("@end", CAM_A)]},
     {"id": "eyes", "name": "Close: his eyes follow the ball", "at": "You're-0.12", "play": "G", "env": "game",
      "remap": [[0, 4.4], ["@end", 5.85]],
      "camera": [key(0, CAM_EYES), key("@end", {**CAM_EYES, "dist": 1.3})]},
     {"id": "poss", "name": "Passer's view: #8 hidden behind the defender, the ball goes the other way", "at": "you stop-0.1", "play": "S", "env": "game",
      "remap": [[0, 0.6], ["teammate a", 2.25], ["target.>", 2.95], ["@end", 5.6]],
      "camera": [key(0, POV0), key("target.", POV0), key("target.>+0.9", POV1, "inOut"), key("@end", POV1)]},
     {"id": "miss", "name": "The open shot hits the ring and kicks out", "at": "One.-0.2", "play": "M", "env": "game",
      "remap": [[0, 0.0], ["One.>", 0.62], ["miss,", 1.6], ["@end", 2.12]],
      "camera": [key(0, MISS), key("One.>", MISS), key("miss,-0.2", MISS_T, "inOut"), key("@end", MISS_T)]},
     {"id": "reset", "name": "Breathe out, tap the jersey (1 RESET), get back", "at": "breathe-0.3", "play": "M", "env": "game",
      "remap": [[0, 2.12], ["breathe", 2.2], ["out.>", 3.5], ["Tap", 3.66], ["jersey.>", 4.75], ["Get", 4.95], ["@end", 6.55]],
      "camera": [key(0, CLOSE), key("Get", CLOSE), key("@end", {**CLOSE, "dist": 4.2, "pitch": 80}, "inOut")],
      "screen": [{"type": "step", "n": 1, "text": "RESET", "from": "Tap", "to": "@end"}]},
     {"id": "offers", "name": "2 SHOW A TARGET: offers 1 and 2 while the ball goes elsewhere", "at": "Two.-0.2", "play": "F", "env": "game",
      "remap": [[0, 0.0], ["yourself", 1.05], ["yourself a target.>", 1.85], ["Three times", 2.3], ["passing lane,", 3.45], ["@end", 4.3]],
      "camera": [key(0, WIDE), key("@end", WIDE)],
      "ov3": [{"type": "ring", "player": "O8", "size": 0.85, "from": "yourself", "to": "@end"}],
      "screen": [{"type": "step", "n": 2, "text": "SHOW A TARGET", "from": "Two.", "to": "@end"},
                 {"type": "counter", "steps": ["yourself a target", "passing lane,"], "total": 3, "from": "Two.", "to": "@end"}]},
     {"id": "offer3", "name": "Offer 3: plant, slide to the open line, show the hands, the pass arrives", "at": "show your-0.1", "play": "G", "env": "game",
      "remap": [[0, 6.0], ["show your hands", 6.9], ["and call for it>+0.55", 8.1], ["@end", 8.95]],
      "camera": [key(0, CAM_W), key("@end", CAM_W)],
      "ov3": [{"type": "passLane", "src": "O1", "dst": "O8", "color": "#C9A24D", "from": "show your hands", "to": "and call for it>+0.55"}],
      "screen": [{"type": "step", "n": 2, "text": "SHOW A TARGET", "from": 0, "to": "@end"},
                 {"type": "counter", "steps": ["show your hands"], "base": 2, "total": 3, "from": 0, "to": "@end"}]},
     {"id": "again1", "name": "3 ASK AGAIN: the open miss again", "at": "Three. Missed-0.2", "play": "M", "env": "game",
      "remap": [[0, 0.15], ["shot?>", 1.75], ["@end", 2.2]],
      "camera": [key(0, MISS), key(0.5, MISS), key("shot?>-0.25", MISS_T, "inOut"), key("@end", MISS_T)],
      "screen": [{"type": "step", "n": 3, "text": "ASK AGAIN", "from": "Three. Missed", "to": "@end"}]},
     {"id": "again2", "name": "Next possession, hook framing: out from behind the defender, hands up, catch at the chest", "at": "On the-0.12", "play": "G", "env": "game",
      "remap": [[0, 5.3], ["ask", 6.05], ["again.", 6.9], ["again.>+0.6", 8.1], ["@end", 8.95]],
      "camera": [key(0, CAM_AF), key("@end", CAM_AF)],
      "screen": [{"type": "step", "n": 3, "text": "ASK AGAIN", "from": 0, "to": "@end"}]},
     {"id": "close", "name": "E2A sign-off on the practice run-in, ends on the hook's first frame", "at": "For more-0.15", "play": "P", "env": "practice",
      "remap": [[0, 0.0], ["@end", 1.45]],
      "camera": [key(0, CAM_A), key("@end", CAM_A)],
      "screen": [{"type": "logo", "from": "European", "to": "@end"}]},
    ]


SFX = {"hook": [], "cut": [{"at": 0, "name": "impact", "volume": 0.07}], "eyes": [], "poss": [{"at": "target.", "name": "whoosh", "volume": 0.06}],
       "miss": [], "reset": [{"at": "Tap", "name": "tick", "volume": 0.15}],
       "offers": [{"at": "Two.", "name": "whoosh", "volume": 0.07}, {"at": "yourself a target", "name": "tick", "volume": 0.16}, {"at": "passing lane,", "name": "tick", "volume": 0.16}],
       "offer3": [{"at": "show your hands", "name": "tick", "volume": 0.18}],
       "again1": [{"at": "Three. Missed", "name": "whoosh", "volume": 0.07}], "again2": [], "close": [{"at": 0, "name": "impact", "volume": 0.06}]}

if __name__ == "__main__":
    ep = dict(base)
    ep["id"] = "hide-main"
    ep.pop("wordsRaw", None)
    ep.pop("gaps", None)
    ep["plays"] = {"P": "hide-practice", "G": "hide-pilot-game", "S": "hide-poss", "M": "hide-miss", "F": "hide-offers"}
    ep["shots"] = shots()
    for sh in ep["shots"]:
        sh["sfx"] = SFX[sh["id"]]
    ep["faces"] = FACES
    ep["pinV2"] = True
    ep["autoSfx"] = {"bounce": 0.16, "catch": 0.13, "squeak": 0.08, "swish": 0.3, "land": 0.07, "players": ["O8", "X8"]}
    ep["keywords"] = ["practice", "your hands", "games", "messing up", "target", "breathe out", "jersey", "passing lane", "open shot", "next possession", "again"]
    ep["subtitleGroups"] = [6, 5, 3, 6, 7, 6, 5, 5, 7, 7, 5, 4, 4, 4]
    ep["subtitleHide"] = [["For more-0.05", "basketball.>+3"]]
    ep["music"] = {"src": "tactical/hide/music-mix.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, "hide-main.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "hide.words.json"), os.path.join(D, "hide-main.words.json"))
    ep["words"] = json.load(open(os.path.join(D, "hide.words.json")))
    ep["plays"] = {k: json.load(open(os.path.join(T_, "tactical", "plays", f"{v}.json"))) for k, v in ep["plays"].items()}
    os.makedirs("/tmp/claude-0/hide", exist_ok=True)
    json.dump({"episode": ep}, open("/tmp/claude-0/hide/hide-main.props.json", "w"))
    print("hide-main", len(ep["shots"]), "shots")
