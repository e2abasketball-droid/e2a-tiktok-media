#!/usr/bin/env python3
"""DOUBLE DRAG EN TRANSICION V2 + PCD hooks (owner brief E2A-prompt-Claude-Double-Drag-V2-y-metodo-PCD.md, 2026-11-20).
Tactical branches (inside the files): stay_home = play A ddtr-a-roll (X3 stays, roll pass, layup)
                                      tag_roll  = play B ddtr-b-skip (X3 steps in, skip, corner three)
Edit variants (file names): V2-Hook-A ("Layup or three? Watch this foot.") / V2-Hook-B ("Take away the layup. What opens
up?"): SAME hook shot, camera, remap, duration, music and body; only the opening voice + its two title cards change.
  python3 scripts/tactical-voice.py tactical/episodes/ddtr2-a.json     (one Deuce take; gaps)
  python3 tactical/episodes/_voice-ddtr2.py                            (hook B take spliced in; mixes)
  python3 tactical/episodes/_gen-ddtr2.py                              -> ddtr2-main-a.json, ddtr2-main-b.json
  python3 tactical/episodes/_bundle-blind-pig.py out/ddtr2 ddtr2-main-a ddtr2-main-b
PCD sheet of this reel: produccion/tactical/pcd/double-drag-transicion-V2.md (template: FORMATO-CHICAGO.md "Ficha PCD").
Cameras chosen with scripts/cam-probe.mts + projected-separation grids (ball vs defenders' bodies, receiver's front,
rim and receiver inside the 9:16 safe frame); numbers in the delivery's control data. No ball / bounce SFX, no GAME
SPEED shot (dropped: the S/E ratio of the body is not 1:1 everywhere and the new script has no slot for it)."""
import json, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
orb = lambda tg, dist, pitch, yaw, fov=46: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
S = lambda n: round(n / 30, 4)
RED = "#E5483A"

# the decision composition (hook, stay_home choice, tag_roll rehook, close): 3/4 medium-high from the weak side;
# X3 ~330 px tall (110 px at 360 px width), O3 in the corner below him, O5 + O1 + ball upper right, rim at the left edge
HOOK = orb([3.0, 3.7, 0.6], 12, 48, -100)
HOOK_IN = orb([3.0, 3.6, 0.6], 11.2, 48, -100)       # slow push-in (composition, no nervous zoom)
SCREENS0 = orb([-0.2, 9.4, 0.6], 12, 56, -100)       # 3/4 from the weak-side wing: X1 separated from X4/X5/O5 (>= 170 px)
SCREENS1 = orb([-0.8, 8.0, 0.6], 12, 56, -100)
SPLIT = orb([0.3, 6.3, 0.3], 15, 38, -12)            # short high look: dive up the picture, pop down
PAY0 = orb([-1.2, 5.0, 1.0], 11, 62, -128)           # weak-side baseline 3/4: O1's release in frame, O5's FRONT at the
PAY1 = orb([0.3, 2.4, 1.2], 11, 62, -128)            # catch (66 deg), ball >= 130 px from X5's body, rim in frame
SKIP0 = orb([0.5, 4.6, 1.0], 11, 68, 80)             # ball side, low: the skip flies away, O3 catches FACING the camera
SKIP1 = orb([5.4, 2.7, 1.0], 11, 68, 80)
SHOT = orb([4.0, 2.0, 1.6], 13, 64, -50)             # weak wing: O3 in profile (load, release), rim and net in frame;
#   preview 1 had O3 at x 110 px (cropped, the V1 fault): now O3 x 250, rim x 870, X3 >= 140 px from O3

HOOK_END = 3.257      # = "Two"-0.1 in both voice tracks (the body is sample-identical from the splice at 3.168 s)
HOOK_REMAP = [[0, S(65)], [0.4, S(68)], [2.5, S(79)], [HOOK_END, S(83)]]   # X3 weight shift from S066.5 (E 0.2 s), right foot off the floor S068 (E 0.4 s); pass (S086) hidden


def opening(variant):
    c1, c2, sw = ((["LAYUP OR THREE?"], ["WATCH THIS FOOT"], "Watch-0.12") if variant == "a" else
                  (["TAKE AWAY THE LAYUP"], ["WHAT OPENS UP?"], "What-0.12"))
    return [{"id": "hook", "name": f"HOOK {variant.upper()} (cam HOOK, tag_roll S065->S083): X3 loads and steps inside; O3 in the corner, O5 rolling; no pass, no result",
             "at": 0, "play": "B", "branch": "tag_roll",
             "remap": HOOK_REMAP,
             "camera": [key(0, HOOK), key(HOOK_END, HOOK_IN, "linear")],
             "ov3": [{"type": "spot", "player": "X3", "r": 0.42, "color": RED, "strength": 0.55, "from": 0.15, "to": 2.3}],   # small foot mark on the load
             "screen": [{"type": "title", "lines": c1, "gold": [], "from": -0.6, "to": sw, "y": 252, "size": 76},
                        {"type": "title", "lines": c2, "gold": [0], "from": sw, "to": HOOK_END, "y": 252, "size": 76}]}]


def body():
    sh = []
    sh.append({"id": "screens", "name": "TWO SCREENS (cam 3/4 weak wing): stay_home S018->S064, O5 sets on X1 (S032), then O4 (S053); X1's long route",
               "at": HOOK_END, "play": "A", "branch": "stay_home",
               "remap": [[0, S(18)], ["The first-0.1", S(64)]],
               "camera": [key(0, SCREENS0), key("The first-0.1", SCREENS1, "inOut")],
               "ov3": [{"type": "spot", "player": "O5", "r": 0.55, "strength": 0.5, "from": "screens", "to": "transition."},
                       {"type": "spot", "player": "O4", "r": 0.55, "strength": 0.5, "from": "transition.+0.3", "to": "The first-0.1"}],
               "screen": []})
    sh.append({"id": "split", "name": "SPLIT (cam high, short): stay_home S056->S092, O5 dives (ROLL), O4 opens (POP); thin arrows born with the move",
               "at": "The first-0.1", "play": "A", "branch": "stay_home",
               "remap": [[0, S(56)], ["rolls.>", S(72)], ["pops.>", S(88)], ["If-0.15", S(92)]],
               "camera": [key(0, SPLIT), key("If-0.15", SPLIT)],
               "ov3": [{"type": "arrow3d", "player": "O5", "t0": S(56), "t1": S(98), "draw": 0.6, "from": "screener", "to": "pops."},
                       {"type": "arrow3d", "player": "O4", "t0": S(67), "t1": S(96), "draw": 0.6, "from": "second", "to": "If-0.4"}],
               "screen": [{"type": "pin", "player": "O5", "text": "ROLL", "from": "rolls.", "to": "The second", "size": 38},
                          {"type": "pin", "player": "O4", "text": "POP", "from": "pops.", "to": "If-0.4", "size": 38}]})
    sh.append({"id": "choice", "name": "STAY HOME (cam HOOK, same composition): stay_home S062->S081, X3 holds near O3; one brief ring",
               "at": "If-0.15", "play": "A", "branch": "stay_home",
               "remap": [[0, S(62)], ["home,>", S(78)], ["hit-0.1", S(81)]],
               "camera": [key(0, HOOK), key("hit-0.1", HOOK_IN, "linear")],
               "ov3": [{"type": "lockRing", "player": "X3", "from": "corner", "to": "home,>"}],
               "screen": []})
    sh.append({"id": "payoff", "name": "PAYOFF stay_home (cam weak-side baseline 3/4): O1 picks up S080, pass S084, catch in front S098, two steps, release S116, make S131, landing",
               "at": "hit-0.1", "play": "A", "branch": "stay_home",
               "remap": [[0, S(80)], ["stride.", S(94)], ["stride.>", S(106)], ["stride.>+1.04", S(131)], ["Same-0.15", S(142)]],
               "camera": [key(0, PAY0), key("stride.", PAY1, "inOut"), key("Same-0.15", PAY1)],
               "ov3": [{"type": "ballPath", "src": "O1", "dst": "O5", "draw": 0.3, "from": 0.12, "to": "roller>"}],   # off 5+ frames before the hands
               "screen": []})
    sh.append({"id": "rehook", "name": "SAME PLAY (cam HOOK): rewind, tag_roll S058->S068, X3's first step inside (same decision frame as stay_home)",
               "at": "Same-0.15", "play": "B", "branch": "tag_roll",
               "remap": [[0, S(100)], [0.35, S(58), "inOut"], ["Now", S(62)], ["He-0.15", S(68)], ["He-0.1", S(69)]],
               "camera": [key(0, HOOK), key("He-0.1", HOOK_IN, "linear")],
               "ov3": [{"type": "spot", "player": "X3", "r": 0.42, "color": RED, "strength": 0.55, "from": "watch him", "to": "He-0.1"}],
               "screen": [{"type": "rewind", "from": 0, "to": 0.35}]})
    sh.append({"id": "tag", "name": "TAG (cam HOOK_IN): tag_roll S069->S089, X3 goes to the roll line, O1 turns to the corner, release S086",
               "at": "He-0.1", "play": "B", "branch": "tag_roll",
               "remap": [[0, S(69)], ["roll.>", S(79)], ["leave?>", S(85)], ["Skip-0.1", S(86)], ["Skip+0.0", S(89)]],
               "camera": [key(0, HOOK_IN), key("Skip+0.0", HOOK_IN)],
               "ov3": [{"type": "ghost", "player": "X3", "t": S(66), "link": True, "from": "Who", "to": "Skip+0.0"}],
               "screen": []})
    sh.append({"id": "skip", "name": "SKIP (cam ball side, low, pans with the ball): tag_roll S089->S121 at 1x, O3 catches facing the camera, absorbs, starts the load",
               "at": "Skip+0.0", "play": "B", "branch": "tag_roll",
               "remap": [[0, S(89)], [round(32 / 30, 4), S(121)]],
               "camera": [key(0, SKIP0), key(round(25 / 30, 4), SKIP1, "inOut"), key(round(32 / 30, 4), SKIP1)],
               "ov3": [{"type": "ballPath", "src": "O1", "dst": "O3", "draw": 0.3, "from": 0.0, "to": round(16 / 30, 4)}],   # off ~9 frames before the hands
               "screen": []})
    sh.append({"id": "shot3", "name": "CORNER THREE (cam weak wing, O3 in profile): tag_roll S121->S193 at ~1x, release S133, ball through the rim S163-S166, net, follow-through, landing",
               "at": f"Skip+{round(32 / 30, 4)}", "play": "B", "branch": "tag_roll",
               "remap": [[0, S(121)], ["That's-0.15", S(193)]],
               "camera": [key(0, SHOT)],
               "screen": []})
    sh.append({"id": "close", "name": "CLOSE (cam HOOK): back to the decision frame, tag_roll S060->S080 (the step again, loops into the hook); small title, question, logo",
               "at": "That's-0.15", "play": "B", "branch": "tag_roll",
               "remap": [[0, S(60)], ["@end", S(80)]],
               "camera": [key(0, HOOK), key("@end", HOOK_IN, "linear")],
               "ov3": [{"type": "lockRing", "player": "X3", "from": "You're", "to": "@end"}],
               "screen": [{"type": "title", "lines": ["DOUBLE DRAG"], "gold": [0], "from": "That's", "to": "You're-0.1", "y": 252, "size": 72},
                          {"type": "title", "lines": ["HELP", "OR STAY HOME?"], "gold": [1], "from": "You're-0.1", "to": "@end", "y": 252, "size": 76},
                          {"type": "logo", "from": "stay home?>-0.1", "to": "@end"}]})
    return sh


def groups(words):
    """caption units: one sentence per unit, split at a comma when longer than 5"""
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
    src = json.load(open(os.path.join(D, "ddtr2-a.json")))
    ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw")}
    eid = f"ddtr2-main-{variant}"
    ep["id"], ep["title"] = eid, "Double Drag"
    ep["variant"] = f"V2-Hook-{variant.upper()}"
    ep["branches"] = {"stay_home": "A", "tag_roll": "B"}
    ep["voice"] = f"tactical/ddtr/v2-voice-{variant}.wav"
    ep["voiceMix"] = f"tactical/ddtr/v2-voice-{variant}.mix.wav"
    ep["env"] = "academy"
    ep["shots"] = opening(variant) + body()
    ep["pinV2"] = True
    ep["autoSfx"] = False
    ep["keywords"] = ["foot", "rolls", "pops", "corner defender", "roller", "Same play", "step in", "corner", "Double Drag", "Help", "stay home", "layup", "three"]
    ep["subtitleHide"] = [[0, "Two-0.05"], ["That's-0.3", "stay home?>+5"]]   # title cards own the hook and the close
    ep["subtitleY"] = 1360
    words = json.load(open(os.path.join(D, f"ddtr2-{variant}.words.json")))
    ep["subtitleGroups"] = groups(words)
    ep["subtitleBlock"] = True
    ep["subtitleYAt"] = [["If-0.15", "hit-0.1", 300], ["Same-0.15", "Skip+0.0", 300], [f"Skip+{round(32 / 30, 4)}", "That's-0.15", 300]]   # X3's feet are low in the HOOK camera
    ep["music"] = {"src": "tactical/ddtr/v2-music.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, f"ddtr2-{variant}.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")


if __name__ == "__main__":
    for v in ("a", "b"):
        build(v)
