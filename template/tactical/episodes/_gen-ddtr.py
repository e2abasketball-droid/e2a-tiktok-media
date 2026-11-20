#!/usr/bin/env python3
"""DOUBLE DRAG EN TRANSICION, episode A + hook variant B (owner brief E2A-prompt-Claude-Double-Drag-en-transicion.md,
sec. 7 storyboard, 2026-11-20). Plays: ddtr-a-roll (A: X3 stays, roll pass in stride) / ddtr-b-skip (B: X3 tags, skip).
  python3 scripts/tactical-voice.py tactical/episodes/ddtr-a.json          (voice A, gaps; B voice = hook B spliced in)
  python3 tactical/episodes/_gen-ddtr.py                                   -> ddtr-main-a.json, ddtr-main-b.json
  python3 tactical/episodes/_bundle-blind-pig.py out/ddtr ddtr-main-a ddtr-main-b
Hook B changes ONLY the opening voice + its title (same shot, camera, music, graphics, duration: brief sec. 2).
Look: env 'academy' (matte floor, cloth sheen), catch model catchV2 = 2 in the plays. No ball / bounce SFX (autoSfx off,
music --no-sfx); no screen SFX. At most 3 ov3 overlays per shot. Cameras probed with scripts/cam-probe.mts."""
import copy, json, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
orb = lambda tg, dist, pitch, yaw, fov=46: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
S = lambda n: round(n / 30, 4)
RED = "#E5483A"

CHOICE = orb([3.6, 3.7, 0.5], 15.5, 42, -108)        # 3/4 high from the offence's LEFT corner: O3, X3, O5, O1 in one line
CHOICE_IN = orb([3.5, 3.8, 0.5], 14.5, 43, -108)
PUSH0 = orb([1.0, 9.6, 0.5], 21, 50, 15)           # chase of O1 from half court (both screeners arriving, corners)
PUSH1 = orb([0.2, 7.2, 0.5], 17, 52, 15)
SPLIT = orb([0.3, 6.3, 0.3], 15, 38, -12)          # high, from behind: the dive goes up the picture, the pop comes down
PAY = orb([-0.6, 3.4, 1.1], 12, 62, 68)            # lateral-mid from the ball side: O1's pass, O5's hands, X5 late, rim
PAY1 = orb([-0.5, 3.0, 1.2], 11, 63, 68)
GAME = orb([2.4, 5.2, 0.5], 19, 50, -112)          # single wide shot at 1x (choice family, wider)
SKIP = orb([1.5, 4.2, 0.4], 19, 48, -100)          # wider: the skip from O1 to the corner, X3 caught inside
SHOT = orb([3.4, 2.3, 1.8], 12.5, 62, -128)        # corner 3/4: feet behind the arc, release, closeout, ball to the rim

HOOK_END = "As-0.1"


def opening(variant):
    title = (["ONE STEP", "CHANGES THE SHOT"] if variant == "a" else ["STOP THE LAYUP.", "LOSE THE CORNER."])
    return [{"id": "hook", "name": f"HOOK {variant.upper()} (cam CHOICE): B S060->S079, X3's first step inside; O3 in the corner, O5 rolling, O1 with the ball; no pass, no basket",
             "at": 0, "play": "B",
             "remap": [[0, S(60)], [0.5, S(64)], [2.4, S(76)], [HOOK_END, S(79)]],
             "camera": [key(0, CHOICE), key(HOOK_END, CHOICE_IN, "linear")],
             "ov3": [{"type": "lockRing", "player": "X3", "from": -0.8, "to": HOOK_END}],   # already locked on frame 0
             "screen": [{"type": "title", "lines": title, "gold": [1], "from": -0.6, "to": HOOK_END, "y": 1580, "size": 92}]}]


def body():
    sh = []
    sh.append({"id": "push", "name": "PUSH (cam chase): A S000->S070, the guard brings it up, O5 then O4 set the two drags on X1",
               "at": HOOK_END, "play": "A",
               "remap": [[0, 0.0], ["two", S(40)], ["row.", S(58)], ["Watch-0.1", S(70)]],
               "camera": [key(0, PUSH0), key("two", PUSH1, "inOut"), key("Watch-0.1", PUSH1)],
               "ov3": [{"type": "spot", "player": "O5", "r": 0.8, "from": "screens-0.3", "to": "in"},
                       {"type": "spot", "player": "O4", "r": 0.8, "from": "row.", "to": "Watch-0.1"}],
               "screen": [{"type": "pin", "player": "O5", "text": "1ST SCREEN", "from": "gets", "to": "two+0.3", "size": 38},
                          {"type": "pin", "player": "O4", "text": "2ND SCREEN", "from": "a", "to": "row.+0.2", "size": 38}]})
    sh.append({"id": "split", "name": "SPLIT (cam high): A S047->S084, O5 dives (ROLL), O4 steps out to the arc (POP)",
               "at": "Watch-0.1", "play": "A",
               "remap": [[0, S(47)], ["dive.", S(60)], ["second", S(68)], ["arc.", S(80)], ["Now-0.15", S(84)]],
               "camera": [key(0, SPLIT), key("Now-0.15", SPLIT)],
               "ov3": [{"type": "arrow3d", "player": "O5", "t0": S(48), "t1": S(100), "draw": 0.5, "from": "first", "to": "Now-0.15"},
                       {"type": "arrow3d", "player": "O4", "t0": S(67), "t1": S(100), "draw": 0.5, "from": "second", "to": "Now-0.15"}],
               "screen": [{"type": "pin", "player": "O5", "text": "ROLL", "from": "dive.", "to": "arc.-0.25", "size": 40},
                          {"type": "pin", "player": "O4", "text": "POP", "from": "arc.-0.2", "to": "Now-0.15", "size": 40}]})
    sh.append({"id": "choice", "name": "CHOICE (cam CHOICE, same as the hook): A S065->S084, X3 ring again, then the line to O5",
               "at": "Now-0.15", "play": "A",
               "remap": [[0, S(62)], ["choice.", S(76)], ["shooter?", S(81)], ["Hit-0.05", S(84)]],
               "camera": [key(0, CHOICE), key("Hit-0.05", CHOICE_IN, "linear")],
               "ov3": [{"type": "lockRing", "player": "X3", "from": "corner defender", "to": "Hit-0.05"},
                       {"type": "tether", "a": "X3", "b": "O3", "rest": 1.6, "snap": 3.3, "from": "Stay", "to": "Hit-0.05"},
                       {"type": "passLane", "src": "O1", "dst": "O5", "color": "#F2C76A", "from": "choice.>", "to": "Stay"}],
               "screen": [{"type": "pin", "player": "X3", "text": "STAYS", "from": "Stay", "to": "Hit-0.05", "size": 40}]})
    sh.append({"id": "payoff", "name": "PAYOFF A (cam lateral-mid): pass S084, catch in stride S098, left-hand layup S113, make S128",
               "at": "Hit-0.05", "play": "A",
               "remap": [[0, S(84)], ["stride.", S(98)], ["stride.>", S(116)], ["Here-0.2", S(134)]],
               "camera": [key(0, PAY), key("Here-0.2", PAY1, "inOut")],
               "ov3": [{"type": "ballPath", "src": "O1", "dst": "O5", "draw": 0.35, "from": 0.0, "to": "stride.-0.1"},
                       {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "Here-0.75", "to": "Here-0.2"}],
               "screen": [{"type": "stamp", "text": "LAYUP", "from": "Here-0.7", "to": "Here-0.2", "y": 600}]})
    sh.append({"id": "real", "name": "GAME SPEED (cam wide): A S000->S135 at 1x, no graphics but the chip",
               "at": "Here-0.2", "play": "A",
               "remap": [[0, 0.0], [4.5, 4.5], ["Same-0.15", 4.55]],
               "camera": [key(0, GAME), key("Same-0.15", GAME)],
               "screen": [{"type": "hud", "tag": "1×", "text": "GAME SPEED", "from": 0.05, "to": "Same-0.25"}]})
    sh.append({"id": "rehook", "name": "SAME PLAY (cam CHOICE): rewind, B S060->S086, X3 plants inside and tags the roll",
               "at": "Same-0.15", "play": "B",
               "remap": [[0, S(84)], [0.3, S(58), "inOut"], ["time,", S(64)], ["tag", S(76)], ["See-0.1", S(85)]],
               "camera": [key(0, CHOICE), key("See-0.1", CHOICE_IN, "linear")],
               "ov3": [{"type": "lockRing", "player": "X3", "from": "play.", "to": "See-0.1"},
                       {"type": "spot", "player": "O5", "r": 0.8, "from": "tag", "to": "See-0.1"}],
               "screen": [{"type": "rewind", "from": 0, "to": 0.3},
                          {"type": "pin", "player": "X3", "text": "TAG", "tone": "red", "from": "tag", "to": "See-0.1", "size": 40}]})
    sh.append({"id": "skip", "name": "SKIP (cam wide): X3's empty spot, the overhead skip S086 -> catch S114 behind the arc",
               "at": "See-0.1", "play": "B",
               "remap": [[0, S(85)], ["left?>", S(87)], ["to the corner.", S(112)], ["to the corner.>+0.1", S(116)]],
               "camera": [key(0, SKIP), key("to the corner.>+0.1", SKIP)],
               "ov3": [{"type": "ghost", "player": "X3", "t": S(66), "link": True, "from": "what", "to": "to the corner.>+0.1"},
                       {"type": "ballPath", "src": "O1", "dst": "O3", "draw": 0.35, "from": "Skip", "to": "to the corner.>"},
                       {"type": "spot", "player": "O3", "r": 0.9, "from": "to the corner.-0.2", "to": "to the corner.>+0.1"}],
               "screen": []})
    sh.append({"id": "shot3", "name": "SHOT (cam corner 3/4, no cut during the release): feet behind the arc, release S127, late closeout, make",
               "at": "to the corner.>+0.1", "play": "B",
               "remap": [[0, S(116)], ["That's-0.25", S(157)]],
               "camera": [key(0, SHOT), key("That's-0.25", SHOT)],
               "ov3": [{"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "That's-0.55", "to": "That's-0.25"}],
               "screen": [{"type": "stamp", "text": "CORNER THREE", "from": "That's-0.6", "to": "That's-0.25", "y": 760}]})
    sh.append({"id": "name", "name": "NAME (cam high): A at the split, ROLL and POP arrows, DOUBLE DRAG",
               "at": "That's-0.25", "play": "A",
               "remap": [[0, S(66)], ["You're-0.1", S(80)]],
               "camera": [key(0, SPLIT), key("You're-0.1", SPLIT)],
               "ov3": [{"type": "arrow3d", "player": "O5", "t0": S(48), "t1": S(100), "draw": 0.3, "from": 0.0, "to": "You're-0.1"},
                       {"type": "arrow3d", "player": "O4", "t0": S(67), "t1": S(100), "draw": 0.3, "from": 0.0, "to": "You're-0.1"}],
               "screen": [{"type": "title", "lines": ["DOUBLE DRAG"], "sub": "ROLL. POP. ONE CHOICE.", "gold": [0], "from": "Double-0.05", "to": "You're-0.1", "y": 236, "size": 112}]})
    sh.append({"id": "microA", "name": "MICRO REPLAY 1/2 (cam CHOICE): A, X3 stays -> the roller",
               "at": "You're-0.1", "play": "A",
               "remap": [[0, S(64)], ["Help-0.1", S(90)]],
               "camera": [key(0, CHOICE_IN), key("Help-0.1", CHOICE_IN)],
               "ov3": [{"type": "lockRing", "player": "X3", "from": 0.0, "to": "Help-0.1"}],
               "screen": [{"type": "title", "lines": ["HELP", "OR STAY HOME?"], "gold": [1], "from": 0.0, "to": "Help-0.1", "y": 1580, "size": 92}]})
    sh.append({"id": "microB", "name": "MICRO REPLAY 2/2 (cam CHOICE): B, X3 steps in; ends on the hook's gesture (loop), small logo",
               "at": "Help-0.1", "play": "B",
               "remap": [[0, S(62)], ["home?>", S(77)], ["@end", S(79)]],
               "camera": [key(0, CHOICE), key("@end", CHOICE_IN, "linear")],
               "ov3": [{"type": "lockRing", "player": "X3", "from": 0.0, "to": "@end"}],
               "screen": [{"type": "title", "lines": ["HELP", "OR STAY HOME?"], "gold": [1], "from": 0.0, "to": "home?>", "y": 1580, "size": 92},
                          {"type": "freeze", "label": "YOUR CALL", "from": "home?>", "to": "@end"},
                          {"type": "logo", "from": "home?>-0.1", "to": "@end"}]})
    return sh


def groups(words):
    """caption units (brief sec. 7 'grupos muy cortos'): one sentence per unit, split at a comma when longer than 5"""
    out, cur = [], []
    for w in words:
        cur.append(w["text"])
        if w["text"][-1] in ".?!" or (w["text"].endswith(",") and len(cur) >= 3):
            n = len(cur)
            while n > 6:
                out.append(n // 2); n -= n // 2
            out.append(n); cur = []
    if cur:
        out.append(len(cur))
    return out


def build(variant):
    src = json.load(open(os.path.join(D, "ddtr-a.json")))
    ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw")}
    eid = f"ddtr-main-{variant}"
    ep["id"], ep["title"] = eid, "Double Drag"
    ep["voice"] = f"tactical/ddtr/voice-{variant}.wav"
    ep["voiceMix"] = f"tactical/ddtr/voice-{variant}.mix.wav"
    ep["env"] = "academy"
    ep["shots"] = opening(variant) + body()
    ep["pinV2"] = True
    ep["autoSfx"] = False
    ep["keywords"] = ["One step", "two screens", "dive", "arc", "choice", "shooter", "roller", "stride", "game speed",
                      "Same play", "tag the roll", "just left", "corner", "Double Drag", "Help", "stay home", "Stop the layup", "Lose the corner"]
    ep["subtitleHide"] = [[0, "As-0.05"], ["That's-0.3", "home?>+5"]]
    ep["subtitleY"] = 1560
    words = json.load(open(os.path.join(D, f"ddtr-{variant}.words.json")))
    ep["subtitleGroups"] = groups(words)
    ep["subtitleBlock"] = True
    ep["subtitleYAt"] = [["See-0.1", "to the corner.>+0.1", 330]]   # O3 sits low in the skip shot: captions to the top
    ep["music"] = {"src": "tactical/ddtr/music.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, f"ddtr-{variant}.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")


if __name__ == "__main__":
    for v in ("a", "b"):
        build(v)
