#!/usr/bin/env python3
"""CHICAGO ACTION — REALISM V2 reel (owner brief E2A_REALISM_V2_PROMPT_CLAUDE_CODE.md sec. 11, 2026-11-21).
Pin-down -> dribble hand-off to O2. Read A: X2 TRAILS -> one dribble, pull-up. Read B: X2 goes UNDER -> catch off
the hand-off, three. Plays tactical/plays/chicago-v2-{a-trail,b-under}.json (realism: 2, Realism V2 engine + v2 apparel).
ONE Deuce take (public/tactical/chicago-v2/voice-raw.mp3), gaps by scripts/tactical-voice.py:
  python3 scripts/tactical-voice.py tactical/episodes/chicago-v2-voice.json
  python3 tactical/episodes/_gen-chicago-v2.py                    -> chicago-action-v2.json (+ .words.json)
  node scripts/tactical-props.mjs tactical/episodes/chicago-action-v2.json out/blob/chicago-action-v2.props.json
Storyboard: hook ONE SCREEN. / TWO BAD CHOICES. -> overhead, the defender -> PIN-DOWN (3/4, planted screener) ->
HANDOFF (low side, palms on the ball) -> TRAIL = LATE (corner, one dribble, pull-up, +2) -> GO UNDER? (catch, three, +3)
-> recap overhead CHICAGO ACTION -> CTA TRAIL / OR UNDER? with both routes, logo.
Repo axes: x = -brief x; orbit yaw 0 = camera on the half-court side, pitch from vertical."""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
groups = import_module("_gen-blob").groups
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
fol = lambda ids, z=1.0, **k: {"follow": ids, "z": z, **k}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
EID = "chicago-action-v2"
RED, GOLD, COOL, WHITE = "#E5483A", "#FFC447", "#A9C8EE", "#FFFFFF"
PIN = [-4.32, 4.22]
HO = [-3.22, 8.58]

TOP = orb([-2.8, 5.6, 0.0], 19.0, 4, 0, 42)            # near-vertical, basket at the top: x -6.9 .. 1.3 in the 9:16
TOP_IN = orb([-3.0, 6.3, 0.0], 16.0, 4, 0, 42)          # frame (pin-down, O2's start, hand-off, pull-up spot)
HOOK0 = orb([-2.8, 8.6, 1.05], 8.6, 72, 150, 42)       # low side on the hand-off (A/B SIDE camera, a little wider)
HOOK1 = orb([-2.5, 8.5, 1.05], 8.2, 70, 140, 42)
PD0 = orb([-3.9, 5.7, 1.0], 11.0, 68, 62, 40)           # 3/4 on the pin-down (A/B CAM34)
PD1 = orb([-3.6, 6.6, 1.0], 10.5, 66, 70, 40)
HOS = orb([-2.95, 8.25, 1.05], 5.8, 76, 150, 40)        # hand-off close (A/B SIDE)
CHASE = lambda d=9.0, yaw=30: orb(fol(["O2"], 1.2), d, 58, yaw, 42)   # behind O2, rim ahead
RIM_A = orb([-0.25, 4.2, 1.8], 9.5, 60, 24, 42)
FEET0 = orb([-4.32, 4.22, 0.3], 2.6, 76, 115, 40)       # screener's shoes, low (A/B soles camera, closer)
FEET1 = orb([-4.32, 4.22, 0.35], 2.4, 76, 105, 40)
UNDER0 = orb([-3.4, 6.4, 1.0], 10.0, 62, 58, 42)


def shots():
    return [
        {"id": "01-hook", "name": "HOOK: low side on the hand-off, O2 turns the corner round O1 with X2 trailing (A 1.95 -> 3.0)",
         "at": 0, "play": "A", "remap": [[0, 1.95], ["@end", 3.0]],
         "camera": [key(0, HOOK0), key("@end", HOOK1, "inOut")],
         "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0.1, "to": "@end"}],
         "screen": [{"type": "title", "lines": ["ONE SCREEN.", "TWO BAD CHOICES."], "gold": [1], "from": 0, "to": "@end", "y": 250, "size": 96}]},
        {"id": "02-watch", "name": "WATCH THE DEFENDER: overhead, the set before the cut, X2 ringed (A 0 -> 0.55)",
         "at": "Watch-0.1", "play": "A", "remap": [[0, 0.0], ["@end", 0.55]],
         "camera": [key(0, TOP), key("@end", TOP, "linear")],
         "ov3": [{"type": "ring", "player": "X2", "color": RED, "pulse": True, "from": 0.05, "to": "@end"}],
         "screen": [
                    {"type": "pin", "player": "O4", "text": "PIN-DOWN", "from": "decisions.", "to": "@end", "size": 38},
                    {"type": "pin", "player": "O1", "text": "HANDOFF", "from": "seconds.", "to": "@end", "size": 38}]},
        {"id": "03a-feet", "name": "PIN-DOWN hero: low close-up of the screener's shoes planting, both feet on the floor (A 0.85 -> 1.2)",
         "at": "First,-0.1", "play": "A", "remap": [[0, 0.85], ["@end", 1.2]],
         "camera": [key(0, FEET0), key("@end", FEET1, "linear")],
         "ov3": [],
         "screen": [{"type": "title", "lines": ["PIN-DOWN"], "gold": [0], "from": 0.05, "to": "@end", "y": 250, "size": 104}]},
        {"id": "03b-pindown", "name": "PIN-DOWN: 3/4, O4 planted (both feet), O2 flies off, X2 chases (A 1.2 -> 2.2)",
         "at": "pin-down.>", "play": "A", "remap": [[0, 1.2], ["chase.>", 2.05], ["@end", 2.2]],
         "camera": [key(0, PD0), key("@end", PD1, "inOut")],
         "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": -1.85, "from": 0, "to": "@end"},
                 {"type": "route", "player": "O2", "t0": 0.55, "t1": 2.4, "trail": True, "from": "shooter", "to": "@end"},
                 {"type": "route", "player": "X2", "t0": 0.6, "t1": 2.3, "color": RED, "trail": True, "from": 0.3, "to": "@end"}],
         "screen": [{"type": "title", "lines": ["PIN-DOWN"], "gold": [0], "from": 0, "to": "@end", "y": 250, "size": 104}]},
        {"id": "04-handoff", "name": "HANDOFF: low side, O1 presents, palms on the ball, O2 takes it (A 2.05 -> 2.62)",
         "at": "Then,-0.1", "play": "A", "remap": [[0, 2.05], ["@end", 2.62]],
         "camera": [key(0, HOS), key("@end", HOS, "linear")],
         "ov3": [{"type": "ring", "player": "O1", "from": 0.05, "to": "@end"}],
         "screen": [{"type": "title", "lines": ["HANDOFF"], "gold": [0], "from": 0.05, "to": "@end", "y": 250, "size": 104}]},
        {"id": "05-trail", "name": "READ A, TRAIL = LATE: behind O2, corner, one dribble, pull-up, make, +2 (A 2.6 -> 5.0)",
         "at": "Trail-0.1", "play": "A", "remap": [[0, 2.6], ["recover.>", 3.95], ["@end", 5.0]],
         "camera": [key(0, CHASE(8.6, 36)), key("recover.>", CHASE(9.2, 28), "inOut"), key("@end", RIM_A, "inOut")],
         "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "recover."},
                 {"type": "separation", "a": "X2", "b": "O2", "from": "turns", "to": "recover.>"},
                 {"type": "ballTrail", "len": 0.3, "from": "recover.>", "to": "@end-0.2"},
                 {"type": "glow", "hoop": True, "r": 1.1, "color": GOLD, "strength": 0.6, "from": "@end-0.3", "to": "@end"}],
         "screen": [{"type": "title", "lines": ["TRAIL", "= LATE"], "gold": [1], "from": 0.05, "to": "@end", "y": 250, "size": 104},
                    {"type": "stamp", "text": "PULL-UP", "badge": "+2", "from": "@end-0.35", "to": "@end", "y": 330}]},
        {"id": "06-under", "name": "READ B, GO UNDER?: X2 under the pin-down, O2 catches off the hand-off, three, +3 (B 1.25 -> 4.1)",
         "at": "But-0.1", "play": "B", "remap": [[0, 1.25], ["under?>", 2.05], ["up.>", 3.0], ["@end", 4.1]],
         "camera": [key(0, UNDER0), key("under?>", CHASE(8.4, 40), "inOut"), key("up.>", CHASE(9.0, 30), "inOut"), key("@end", RIM_A, "inOut")],
         "ov3": [{"type": "ring", "player": "X2", "color": RED, "pulse": True, "from": 0.45, "to": "space"},
                 {"type": "route", "player": "X2", "t0": 1.25, "t1": 2.6, "color": RED, "trail": True, "from": 0.1, "to": "space"},
                 {"type": "openSpace", "at": [-3.15, 8.35], "r": 1.0, "from": "space", "to": "up.>"},
                 {"type": "ballTrail", "len": 0.3, "from": "up.>", "to": "@end-0.2"},
                 {"type": "glow", "hoop": True, "r": 1.1, "color": GOLD, "strength": 0.6, "from": "@end-0.3", "to": "@end"}],
         "screen": [{"type": "title", "lines": ["GO", "UNDER?"], "gold": [1], "from": 0.05, "to": "@end", "y": 250, "size": 104},
                    {"type": "stamp", "text": "THREE", "badge": "+3", "from": "@end-0.35", "to": "@end", "y": 330}]},
        {"id": "07-recap", "name": "CHICAGO ACTION recap: overhead, the cut off the pin-down into the hand-off (A 0.3 -> 2.7)",
         "at": "That's-0.1", "play": "A", "remap": [[0, 0.3], ["@end", 2.7]],
         "camera": [key(0, TOP), key("@end", TOP_IN, "inOut")],
         "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": -1.85, "from": 0.2, "to": "@end"},
                 {"type": "route", "player": "O2", "t0": 0.3, "t1": 2.7, "trail": True, "color": GOLD, "from": "cut,", "to": "@end"},
                 {"type": "ring", "player": "O1", "from": "handoff#2", "to": "@end"}],
         "screen": [{"type": "title", "lines": ["CHICAGO ACTION"], "gold": [0], "sub": "One cut. One handoff.", "from": 0.05, "to": "@end", "y": 250, "size": 104}]},
        {"id": "08-cta", "name": "CTA: overhead frozen before the choice, X2's two routes TRAIL (red) / UNDER (cool), logo (B 1.2)",
         "at": "You're-0.1", "play": "B", "remap": [[0, 1.2], ["@end", 1.2]],
         "camera": [key(0, TOP_IN), key("@end", {**TOP_IN, "dist": 15.0}, "linear")],
         "ov3": [{"type": "ring", "player": "X2", "color": RED, "pulse": True, "from": 0, "to": "@end"},
                 {"type": "route", "player": "X2", "t0": 0, "t1": 0, "pts": [[-4.95, 3.5], [-5.2, 4.4], [-5.0, 5.6], [-4.55, 6.9], [-4.1, 8.1], [-3.6, 9.0]],
                  "color": RED, "width": 0.14, "draw": 0.45, "label": "TRAIL", "labelYaw": 0, "labelOffset": [-0.9, -2.6], "labelSize": 0.7, "from": "Trail#2", "to": "@end"},
                 {"type": "route", "player": "X2", "t0": 0, "t1": 0, "pts": [[-3.95, 3.45], [-3.2, 3.95], [-2.8, 5.2], [-2.95, 6.35], [-3.3, 7.4]],
                  "color": COOL, "width": 0.14, "draw": 0.45, "label": "UNDER", "labelYaw": 0, "labelOffset": [0.9, 0.0], "labelSize": 0.7, "from": "under?#2", "to": "@end"}],
         "screen": [{"type": "scrim", "opacity": 0.22, "from": 0, "to": "@end"},
                    {"type": "title", "lines": ["TRAIL", "OR UNDER?"], "gold": [1], "from": "Trail#2", "to": "@end", "y": 250, "size": 112},
                    {"type": "micro", "text": "COMMENT: TRAIL / UNDER", "y": 560, "from": "Tell", "to": "@end"},
                    {"type": "logo", "from": "Follow", "to": "@end"}]},
    ]


def build():
    src = json.load(open(os.path.join(D, "chicago-v2-voice.json")))
    ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw", "gapFill")}
    ep["id"], ep["title"] = EID, "Chicago Action (Realism V2): one screen, two bad choices"
    ep["voiceMix"] = "tactical/chicago-v2/voice.mix.wav"
    ep["branches"] = {"a": "A", "b": "B"}
    words = json.load(open(os.path.join(D, "chicago-v2-voice.words.json")))
    ep["tail"] = round(38.0 - words[-1]["end"], 3)          # 38.00 s = 1140 frames
    ep["env"] = "cinema"
    ep["shots"] = shots()
    ep["pinV2"] = True
    ep["autoSfx"] = False
    ep["keywords"] = ["screen", "defender.", "pin-down.", "chase.", "handoff.", "Trail", "recover.", "under?", "rise", "Chicago", "problems.", "read."]
    ep["subtitleY"] = 1350
    ep["subtitleGroups"] = groups(words)
    ep["subtitleBlock"] = True
    ep["music"] = {"src": "tactical/chicago-v2/music.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{EID}.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(words, open(os.path.join(D, f"{EID}.words.json"), "w"), indent=0)
    print(EID, len(ep["shots"]), "shots, tail", ep["tail"])


if __name__ == "__main__":
    build()


def cover(out):
    """clean cover (no text, no overlays, no captions): low side on the hand-off, palms on the ball (A 2.45)"""
    ep = json.load(open(os.path.join(D, f"{EID}.json")))
    plays = {k: json.load(open(os.path.join(os.path.dirname(D), "plays", f"{v}.json"))) for k, v in ep["plays"].items()}
    sh = [{"id": "cover", "name": "cover", "at": 0, "play": "A", "remap": [[0, 2.45], [1.0, 2.45]],
           "camera": [key(0, orb([-2.95, 8.3, 1.15], 6.2, 76, 150, 40))], "ov3": [], "screen": []}]
    e2 = {**ep, "id": f"{EID}-cover", "shots": sh, "words": [{"text": "cover", "start": 0, "end": 1.0}], "plays": plays,
          "subtitleHide": [[0, 99]], "subtitleGroups": [1], "voice": "tactical/chicago-v2/voice-raw.mp3", "tail": 0}
    e2.pop("voiceMix", None)
    json.dump({"episode": e2}, open(out, "w"))
    print("cover props", out)


if __name__ == "__main__" and "--cover" in sys.argv:
    cover(sys.argv[sys.argv.index("--cover") + 1])
