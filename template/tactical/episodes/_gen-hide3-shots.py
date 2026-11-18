#!/usr/bin/env python3
"""HIDE IN GAMES V3 (owner brief 2026-11-17 21:31Z), ~56.9 s. 0-24.7 s = V2 shots and timing (hook, contrast, the
full miss, the doubt possession); then:
  hideB   passer framing: half a hand comes up on "His hands drop." and goes back, X8 keeps covering, pass to O3
  reset   shorter, medium from the side away from X8: exhale, light tap, eyes back to the ball
  askP    SAME passer framing: a beat of doubt, eyes to the passer, plant, slide, the lane opens, hands, call, catch
  read    from the corner behind O4: #8 ready to shoot, X4 closes out from the help (high hand), eyes rim -> X4 -> O4,
          the extra pass, O4 controls (slowed to ~0.68x so the reason is visible)
  drive   high coach angle: O4 attacks the closeout, X8 helps, #8 drifts and gets the kick-out
  relo    tele medium on #8: square, read X8's closeout, swing to O3, relocate with eyes on the ball
  final   wide: the ball keeps moving, MAKE THE NEXT READ on the last line, discreet logo"""
import importlib.util, json, math, os, shutil, sys
D = os.path.dirname(os.path.abspath(__file__))
T_ = os.path.dirname(os.path.dirname(D))
_s = importlib.util.spec_from_file_location("s2", os.path.join(D, "_gen-hide2-shots.py"))
s2 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(s2)
cam, follow, key = s2.cam, s2.follow, s2.key
MISS3Q, FLOOR, WIDE_P, CLOSE_R, MED_H = s2.MISS3Q, s2.FLOOR, s2.WIDE_P, s2.CLOSE_R, s2.MED_H
base = json.load(open(os.path.join(D, "hide3.json")))

MED_R3 = follow(*json.loads(os.environ.get("MR3", "[0.8, 2.6, 1.6, 1.35]")))            # reset: away from X8's arm
READ = cam(*json.loads(os.environ.get("RD", "[[-9.0, -3.6, 5.6], [-4.75, 2.6, 1.0], 38]")))  # behind O4 in the corner
COACH = cam(*json.loads(os.environ.get("CO", "[[2.6, 12.8, 7.6], [-3.6, 2.8, 0.4], 42]")))  # high coach angle, left side
RELO = follow(*json.loads(os.environ.get("RL", "[5.0, 1.0, 2.1, 1.45, 28]")))            # tele medium on #8
WIDE_F = follow(*json.loads(os.environ.get("WF", "[6.2, 0.9, 3.4, 1.25, 38]")))      # final: #8 relocating, eyes on the ball
MED_H3 = follow(*json.loads(os.environ.get("MH3", "[0.9, 2.6, 1.75, 1.5]")))            # doubt medium: away from X8's arm
SWING = cam(*json.loads(os.environ.get("SW", "[[2.8, 17.0, 7.0], [1.8, 7.2, 0.6], 46]")))  # the ball keeps moving (top/right)
FACES = dict(s2.FACES)
FACES["nums"] = {**FACES["nums"], "X4": "11", "O4": "4"}
FACES["hair"] = {**FACES["hair"], "O4": "#1A120C", "X4": "#3A2414"}
FACES["skin"] = {**FACES["skin"], "O4": "#7A4E33", "X4": "#D7A27C"}


def shots():
    v2 = {s["id"]: s for s in s2.shots()}
    out = [v2[k] for k in ("hook", "react", "practice", "game", "miss")]
    out += [
     {"id": "hideA", "name": "Possession 2, medium: looks at the passer, then briefly down (doubt)", "at": "Next-0.15", "play": "H", "env": "game",
      "remap": [[0, 0], ["What if", 2.85], ["@end", 4.5]],
      "camera": [key(0, MED_H3), key("@end", {**MED_H3, "dist": round(MED_H3["dist"] * 0.92, 3)})],
      "screen": [{"type": "title", "lines": ["WHAT IF I", "MISS AGAIN?"], "gold": [1], "from": "What if", "to": "@end"}]},
     {"id": "hideB", "name": "Passer framing: half a hand comes up and goes back, the pass goes to O3", "at": "again?>+0.15", "play": "H", "env": "game",
      "remap": [[0, 4.5], ["@end", 9.05]],
      "camera": [key(0, WIDE_P), key("@end", WIDE_P)]},
     {"id": "reset", "name": "Short pause, medium: exhale, light tap, eyes back to the ball", "at": "Breathe-0.15", "play": "A", "env": "game",
      "remap": [[0, 0.15], ["@end", 3.3]],
      "camera": [key(0, MED_R3), key("@end", {**MED_R3, "dist": round(MED_R3["dist"] * 0.94, 3)})]},
     {"id": "askP", "name": "Possession 3, same passer framing: doubt, eyes, plant, slide, lane, hands, call, catch", "at": "spot.>+0.4", "play": "A", "env": "game",
      "remap": [[0, 3.3], ["Move", 4.65], ["you.>", 5.95], ["Show", 6.85], ["Call", 8.25], ["@end", 9.55]],
      "camera": [key(0, WIDE_P), key("@end", WIDE_P)],
      "ov3": [{"type": "passLane", "src": "O1", "dst": "O8", "color": "#C9A24D", "from": "you.>-0.35", "to": "Show+0.45"}]},
     {"id": "read", "name": "Corner angle: ready to shoot, the closeout, rim -> defender -> teammate, extra pass, O4 controls", "at": "Call for it.>+0.47", "play": "A", "env": "game",
      "remap": [[0, 9.55], ["One more", 12.05], ["@end", 12.95]],
      "camera": [key(0, READ), key("@end", {**READ, "dist": round(READ["dist"] * 0.95, 3)}, "inOut")],
      "ov3": [{"type": "passLane", "src": "O8", "dst": "O4", "color": "#C9A24D", "from": "He sees", "to": "teammate open.>+0.2"}]},
     {"id": "drive", "name": "Coach angle: O4 attacks the closeout, X8 helps, #8 drifts and gets the kick-out", "at": "One more pass.>+0.45", "play": "A", "env": "game",
      "remap": [[0, 12.95], ["@end", 15.2]],
      "camera": [key(0, COACH), key("@end", {**COACH, "dist": round(COACH["dist"] * 0.96, 3)})]},
     {"id": "relo", "name": "Tele medium on #8: square, read the closeout, swing, relocate with eyes on the ball", "at": "Even-0.55", "play": "A", "env": "game",
      "remap": [[0, 15.2], ["@end", 18.2]],
      "camera": [key(0, RELO), key("@end", RELO)]},
     {"id": "swing", "name": "High angle: the ball keeps moving, O1 attacks, everybody moves", "at": "of the game.>+0.3", "play": "A", "env": "game",
      "remap": [[0, 18.2], ["@end", 21.6]],
      "camera": [key(0, SWING), key("@end", {**SWING, "dist": round(SWING["dist"] * 0.95, 3)})]},
     {"id": "final", "name": "#8 relocating with eyes on the ball while the possession keeps running, MAKE THE NEXT READ", "at": "Read-0.3", "play": "A", "env": "game",
      "remap": [[0, 21.6], ["@end", 23.3]],
      "camera": [key(0, WIDE_F), key("@end", {**WIDE_F, "dist": round(WIDE_F["dist"] * 0.93, 3)}, "inOut")],
      "screen": [{"type": "title", "lines": ["MAKE THE", "NEXT READ"], "gold": [1], "from": "Read-0.1", "to": "@end"},
                 {"type": "logo", "from": "front of you.>+0.05", "to": "@end"}]},
    ]
    return out


SFX = {"game": [{"at": 0, "name": "whoosh", "volume": 0.05}], "reset": [{"at": "out.>+0.6", "name": "tick", "volume": 0.07}]}


def groups(words, mx=7):
    """subtitle cues (3-7 words): each sentence on its own, a long sentence split into near-equal chunks of <= mx words;
    a sentence under 3 words joins the next one when the pair stays <= 7"""
    sents, cur = [], 0
    for w in words:
        cur += 1
        if w["text"].endswith((".", "?", "!")):
            sents.append(cur)
            cur = 0
    if cur:
        sents.append(cur)
    i = 0
    while i < len(sents) - 1:
        if sents[i] < 3 and sents[i] + sents[i + 1] <= 7:
            sents[i + 1] += sents[i]
            sents.pop(i)
            continue
        i += 1
    out = []
    for n in sents:
        if n == 12:   # "What separates good players / from great ones / is what they do next."
            out += [4, 3, 5]
            continue
        k = -(-n // mx)
        base, extra = divmod(n, k)
        out += [base + (1 if j < extra else 0) for j in range(k)]
    return out


if __name__ == "__main__":
    ep = dict(base)
    ep["id"] = "hide3-main"
    ep.pop("wordsRaw", None)
    ep.pop("gaps", None)
    ep["plays"] = {"P": "h2-practice", "M": "h2-miss", "H": "h3-hide", "A": "h3-ask"}
    ep["shots"] = shots()
    for sh in ep["shots"]:
        sh["sfx"] = SFX.get(sh["id"], [])
    ep["faces"] = FACES
    ep["pinV2"] = True
    ep["autoSfx"] = {"bounce": 0.15, "catch": 0.2, "squeak": 0.08, "swish": 0.0, "rim": 0.42, "land": 0.16, "players": ["O8", "X8", "O1", "O4", "X4"]}
    ep["keywords"] = ["missed shot", "practice", "game starts", "rim", "miss again", "somewhere else", "next spot", "show your hands",
                      "closes out", "teammate open", "one more pass", "what they do next", "read the play"]
    words = json.load(open(os.path.join(D, "hide3.words.json")))
    ep["subtitleGroups"] = groups(words)
    ep["subtitleYAt"] = [["Next-0.15", "again?>+0.15", 1345], ["Breathe-0.15", "spot.>+0.4", 1345], ["Even-0.55", "of the game.>+0.3", 1345],
                        ["Call for it.>+0.47", "One more pass.>+0.45", 330]]  # read: subtitles above the action (hands, ball, catch)
    ep["music"] = {"src": "tactical/hide3/music-mix.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, "hide3-main.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "hide3.words.json"), os.path.join(D, "hide3-main.words.json"))
    ep["words"] = words
    ep["plays"] = {k: json.load(open(os.path.join(T_, "tactical", "plays", f"{v}.json"))) for k, v in ep["plays"].items()}
    os.makedirs("/tmp/claude-0/hide3", exist_ok=True)
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/hide3/hide3-main.props.json"
    json.dump({"episode": ep}, open(out, "w"))
    print("hide3-main", len(ep["shots"]), "shots", "groups", ep["subtitleGroups"])
