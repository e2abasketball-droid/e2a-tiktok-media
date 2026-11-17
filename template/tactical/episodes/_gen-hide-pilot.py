#!/usr/bin/env python3
"""HIDE IN GAMES - 9 s pilot (owner brief 2026-11-17 17:09Z, step 1): practice call (0-3 s), match cut into the
game inside the same gesture (3-6 s), plant + slide + show hands + catch (6-9 s). Silent (no narration yet).
  python3 tactical/episodes/_gen-hide-pilot.py [variant]  -> tactical/episodes/hide-pilot.json + props"""
import json, math, os, sys
D = os.path.dirname(os.path.abspath(__file__))
T_ = os.path.dirname(os.path.dirname(D))


def cam(pos, tgt, fov=40):
    d = [pos[i] - tgt[i] for i in range(3)]
    dist = math.sqrt(sum(x * x for x in d))
    return {"type": "orbit", "target": tgt, "dist": round(dist, 3), "pitch": round(math.degrees(math.acos(d[2] / dist)), 2),
            "yaw": round(math.degrees(math.atan2(-d[0], d[1])), 2), "fov": fov}


key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
# side-on medium of #8: camera low on the baseline side of the lane, #8 facing up-court toward the passer
CAM_A = cam([-1.15, 5.0, 1.62], [-3.75, 5.72, 1.28], 40)
# wide from behind the passer's shoulder: passer, defender, receiver and ball in frame
CAM_W = cam([9.8, 9.2, 5.6], [-0.6, 6.1, 0.8], 40)

FACES = {"headScale": 1.38, "nums": {"X8": "14", "X1": "5", "X3": "21"}, "hair": {"O8": "#3A2414", "O1": "#1A120C", "X8": "#2B1A10", "X1": "#4A3020"},
         "skin": {"O8": "#D9A27A", "O1": "#8D5A3B", "X8": "#C68E63", "X1": "#6B4630"}}


def episode():
    shots = [
        {"id": "practice", "name": "Practice: #8 calls for it (warm open gym)", "at": 0, "play": "P", "env": "practice",
         "remap": [[0, 0.0], ["@end", 3.0]], "camera": [key(0, CAM_A), key("@end", CAM_A)]},
        {"id": "game", "name": "Match cut: same gesture, the defender steps in, hands drop", "at": 3.0, "play": "G", "env": "game",
         "remap": [[0, 3.0], ["@end", 6.0]], "camera": [key(0, CAM_A), key("@end", CAM_A)]},
        {"id": "open", "name": "Plant, slide to the open line, show hands, catch", "at": 6.0, "play": "G", "env": "game",
         "remap": [[0, 6.0], ["@end", 9.0]], "camera": [key(0, CAM_A), key(0.85, CAM_W, "inOut"), key("@end", CAM_W)],
         "ov3": [{"type": "passLane", "src": "O1", "dst": "O8", "color": "#C9A24D", "from": 0.95, "to": 2.1}]},
    ]
    return {"id": "hide-pilot", "title": "Hide in games - pilot", "fps": 30, "voice": "tactical/hide/silence.wav",
            "words": [{"text": "pilot", "start": 0.0, "end": 9.0}], "tail": 0.0, "plays": {"P": "hide-pilot-practice", "G": "hide-pilot-game"},
            "shots": shots, "subtitleHide": [[0, 9.5]], "faces": FACES, "pinV2": True,
            "autoSfx": {"bounce": 0.18, "catch": 0.14, "squeak": 0.09, "players": ["O8", "X8"]}}


if __name__ == "__main__":
    ep = episode()
    json.dump(ep, open(os.path.join(D, "hide-pilot.json"), "w"), indent=1)
    ep["plays"] = {k: json.load(open(os.path.join(T_, "tactical", "plays", f"{v}.json"))) for k, v in ep["plays"].items()}
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/hide"
    os.makedirs(out, exist_ok=True)
    json.dump({"episode": ep}, open(os.path.join(out, "hide-pilot.props.json"), "w"))
    print(os.path.join(out, "hide-pilot.props.json"))
