#!/usr/bin/env python3
"""BLOB BOX SCREEN-THE-SCREENER (owner master brief, 2026-11-20): ONE final ~40 s reel, both reads in the same video.
  A = play blob-a-rim    (X4 stays home: O3 -> O5, layup)
  B = play blob-b-three  (X4 protects the rim: fake, O4 screens the screener, O3 -> O2, three)
Pipeline:
  python3 tactical/specs/_gen-blob.py                         plays + QC claims
  python3 scripts/tactical-voice.py tactical/episodes/blob-voice.json   (ONE Deuce take, gaps, digital silence)
  python3 tactical/episodes/_gen-blob.py                      -> blob-box-screen-the-screener-v1.json
  python3 tactical/episodes/_bundle-blind-pig.py out/blob blob-box-screen-the-screener-v1
  bash out/blob/render.sh blob-box-screen-the-screener-v1
  python3 tactical/episodes/_finish-blob.py <deliver_dir>
Editorial clock != game clock: every shot remaps editorial time to the play's game time (slow motion / freezes are
editorial; the plays themselves are real-time and legal: O3 releases at 2.27 s (A) and 3.77 s (B)).
The brief's cut table (sec. 07) assumed a 40.0 s read; Deuce's single take speaks 34.8 s, so the 11 shots keep their
order and content but cut on the narration (table vs real in the PCD sheet).
Repo axes: x = -brief x; orbit yaw 0 = camera on the half-court side, yaw -90 = camera at x > 0 (the brief's LEFT),
pitch from the vertical (90 = horizontal). Voice + music only (autoSfx False), no ball / bounce SFX."""
import json, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
orb = lambda tg, dist, pitch, yaw, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
EID = "blob-box-screen-the-screener-v1"
RED = "#E5483A"
GOLD = "#E3BE68"

# ---- cameras (probe sheets out/blob/probe*-sheet.jpg)
HOOK0 = orb({"follow": ["O2", "X4", "O3"], "z": 0.1, "window": 0.5}, 10.2, 57, -40)          # 3/4 high from the brief's left (probe 4: the low courtside versions
# were cut by near players and hid O2 in the screen cluster; owner note 2026-11-20): O2 unoccluded in front, X4 at the rim,
# O3 with the ball out of bounds at the top
HOOK1 = orb({"follow": ["O2", "X4", "O3"], "z": 0.1, "window": 0.5}, 9.6, 57, -34)         # short lateral dolly / push-in
HIGH0 = orb([-1.9, 4.7, 0.6], 12.0, 55, -30)          # TACTICAL_3Q_HIGH over the paint and the right wing
HIGH1 = orb([-3.8, 5.8, 0.6], 11.5, 56, -26)
COURT = orb([-0.4, 2.4, 0.9], 9.0, 72, -40)           # courtside start of the rise
BOX = orb([0.0, 2.5, 0.6], 12.5, 54, -38)            # box + O3 out of bounds
SCR0 = orb([0.5, 3.4, 0.8], 9.0, 62, -25)             # lateral-high over the right half of the box, O2 coming down
SCR1 = orb([0.6, 2.6, 0.8], 8.6, 64, -50)             # diagonal: O5's whole cut under the screen
RIMA0 = orb([-0.2, 2.2, 1.0], 8.0, 74, -12)           # A: pass, catch, layup
RIMA1 = orb([-0.1, 1.9, 1.6], 7.6, 76, -16)
HELP0 = orb([-0.6, 1.9, 0.9], 7.6, 76, -40)           # B: lower, X4's step to the rim, the fake
HELP1 = orb([-0.4, 2.0, 0.9], 7.0, 76, -36)
O2DET = orb([1.2, 2.95, 0.9], 5.8, 64, 35)   # chest + feet of O2 leaving screen 1
WIDE7 = orb([-0.2, 3.9, 0.6], 10.5, 58, 5)
DS0 = orb([-0.6, 4.4, 0.6], 10.0, 58, -45)            # down screen: O4, X2, O2, X4/O5 still visible
DS1 = orb([-1.8, 4.9, 0.6], 10.5, 58, -35)
SHOOT0 = orb([-4.6, 5.2, 1.1], 7.5, 70, 10)           # SHOT_FOLLOW, side-on: O2's two hands and feet at the catch, the closeouts
RIMB = orb([-0.8, 2.4, 2.5], 7.0, 78, 25)             # RIM_PAYOFF
TAC = orb([-0.5, 3.2, 0.6], 12.5, 52, -32)            # same camera for both reads (shot 10)
CLOSE0 = orb([-0.2, 2.5, 1.0], 9.5, 70, -30)          # final freeze, slight orbit, ends on the hook frame
CLOSE1 = HOOK0


def shots():
    sh = []
    # 01 HOOK: B 2.45 -> 2.95: X4 has shut the rim (O5 sealed), ball still with O3, O2 leaves screen 1 in front (gold ring + focus)
    sh.append({"id": "01-hook", "name": "HOOK (3/4 high, B 2.45 -> 2.95): X4 shuts the rim, ball still with O3, O2 (gold ring, focus) leaves screen 1 toward O4",
               "at": 0, "play": "B", "branch": "b",
               "remap": [[0, 2.45], ["so-0.06", 2.95]],
               "camera": [key(0, HOOK0), key("so-0.06", HOOK1, "linear")],
               "ov3": [{"type": "spot", "player": "X4", "r": 0.5, "color": RED, "strength": 0.55, "from": 0.2, "to": "so-0.06"},
                       {"type": "ring", "player": "O2", "color": GOLD, "size": 0.75, "pulse": True, "from": 0.7, "to": "so-0.06"}],
               "screen": [{"type": "focus", "player": "O2", "r": 0.9, "strength": 0.35, "from": 0.7, "to": "so-0.06"}]})
    # 02 so how is HE open: high 3/4, O2 ring, X2 ghost, freeze before the catch (game 2.6 -> 4.15, freeze)
    sh.append({"id": "02-how", "name": "HOW IS HE OPEN (TACTICAL_3Q_HIGH, B 2.60 -> 4.15 + freeze before the catch): O2 gold ring, X2 ghost where he should be",
               "at": "so-0.06", "play": "B", "branch": "b",
               "remap": [[0, 2.95], ["open?>", 4.2], ["On-0.06", 4.2]],
               "camera": [key(0, HIGH0), key("open?>", HIGH1, "inOut")],
               "ov3": [{"type": "ring", "player": "O2", "color": GOLD, "size": 0.6, "from": 0.15, "to": "On-0.06"},
                       {"type": "ghost", "player": "X2", "t": 4.2, "at": [-4.45, 5.85], "color": "#C8CDD6", "from": "HE", "to": "On-0.06"}],
               "screen": [{"type": "freeze", "from": "open?>", "to": "On-0.06"}]})
    # 03 rewind to the box (O3 out of bounds), freeze, O5 pulse
    sh.append({"id": "03-box", "name": "BOX (rewind, courtside -> 3/4 high, A 0.0 freeze, then 0.0 -> 0.5): four in the box, O3 behind the baseline, O5 highlighted",
               "at": "On-0.06", "play": "A", "branch": "a",
               "remap": [[0, 4.2, "inOut"], [0.35, 0.0], ["the big.>", 0.0], ["But watch-0.1", 0.5]],
               "camera": [key(0, COURT), key(1.4, BOX, "inOut")],
               "ov3": [{"type": "floorText", "text": "BOX", "at": [0.0, 4.25], "size": 0.9, "color": GOLD, "plate": False, "yaw": -38, "from": 0.6, "to": "everyone"},
                       {"type": "spot", "player": "O5", "r": 0.45, "color": GOLD, "strength": 0.6, "from": "everyone", "to": "But watch-0.1"},
                       {"type": "floorText", "text": "INBOUNDER", "at": [-3.5, -1.55], "size": 0.42, "color": "#FFFFFF", "plate": True, "yaw": -38, "from": "baseline", "to": "big."}],
               "screen": [{"type": "rewind", "from": 0, "to": 0.35}]})
    # 04 O2 comes down and plants screen 1 on X5, O5 cuts under
    sh.append({"id": "04-screen1", "name": "SCREEN 1 (lateral-high -> diagonal, A 0.5 -> 1.85): O2 from the right elbow, plants on X5, O5 waits then cuts under",
               "at": "But watch-0.1", "play": "A", "branch": "a",
               "remap": [[0, 0.5], ["screens", 1.40], ["FIVE.>", 1.72], ["If-0.12", 1.85]],
               "camera": [key(0, SCR0), key("He screens", SCR0), key("FIVE.>", SCR1, "inOut")],
               "ov3": [{"type": "route", "player": "O2", "t0": 0.25, "t1": 1.43, "width": 0.09, "draw": 0.8, "color": GOLD, "from": 0.1, "to": "FIVE."},
                       {"type": "print", "player": "O2", "n": 2, "color": GOLD, "from": "screens", "to": "If-0.12"},
                       {"type": "route", "player": "O5", "t0": 1.5, "t1": 2.63, "width": 0.08, "draw": 0.5, "color": "#FFFFFF", "dashed": True, "from": "FIVE.", "to": "If-0.12"}],
               "screen": [{"type": "pin", "player": "O2", "text": "2", "tone": "gold", "from": "watch number", "to": "He screens"}]})
    # 05 READ 1: X4 stays home -> pass, catch, layup, net
    sh.append({"id": "05-layup", "name": "READ 1 (A 1.85 -> 3.75): X4 high with O4, X5 trailing; O3 -> O5, catch, layup, net",
               "at": "If-0.12", "play": "A", "branch": "a",
               "remap": [[0, 1.85], ["home…>", "catch"], ["easy layup.>+0.05", "make"], ["But what-0.1", 3.75]],
               "camera": [key(0, RIMA0), key("easy", RIMA0), key("easy layup.>", RIMA1, "inOut")],
               "ov3": [{"type": "ballPath", "src": "O3", "dst": "O5", "draw": 0.3, "color": GOLD, "from": 0.4, "to": "home…>"}],
               "screen": [{"type": "stamp", "text": "READ 1: RIM", "tone": "gold", "y": 300, "from": "easy layup.>+0.12", "to": "But what-0.1"}]})
    # 06 rewind, B: X4 helps (decision 1.65), NO PASS, the fake
    sh.append({"id": "06-help", "name": "READ 2 SAME SET (rewind, B 1.45 -> 2.30): X4 drops to the rim, HELP, O3 fakes, NO PASS",
               "at": "But what-0.1", "play": "B", "branch": "b",
               "remap": [[0, 3.75, "inOut"], [0.3, 1.45], ["rim?>", 2.17], ["The first-0.1", 2.30]],
               "camera": [key(0, HELP0), key("The first-0.1", HELP1, "linear")],
               "ov3": [{"type": "spot", "player": "X4", "r": 0.5, "color": RED, "strength": 0.6, "from": 0.6, "to": "The first-0.1"},
                       {"type": "floorText", "text": "HELP", "at": [-0.2, 2.9], "size": 0.45, "color": RED, "plate": True, "yaw": -38, "from": "protect", "to": "The first-0.1"},
                       {"type": "passLane", "src": "O3", "dst": "O5", "color": RED, "from": "rim?", "to": "rim?>+0.55"}],
               "screen": [{"type": "rewind", "from": 0, "to": 0.3},
                          {"type": "stamp", "text": "NO PASS", "tone": "white", "y": 300, "from": "rim?", "to": "rim?>+0.55"}]})
    # 07 the first screener isn't finished: O2 detail -> wide (parallel action, B 1.95 -> 2.75)
    sh.append({"id": "07-screener", "name": "THE SCREENER ISN'T DONE (O2 detail -> 3/4 wide, B 1.95 -> 2.75): O2 leaves screen 1, X2 trails, O4 leaves the block",
               "at": "The first-0.1", "play": "B", "branch": "b",
               "remap": [[0, 1.95], ["finished.>", 2.62], ["FOUR-0.1", 2.75]],
               "camera": [key(0, O2DET), key(0.5, O2DET), key("finished.>", WIDE7, "inOut")],
               "ov3": [{"type": "ring", "player": "O2", "color": GOLD, "size": 0.55, "from": 0.1, "to": "FOUR-0.1"}],
               "screen": [{"type": "stamp", "text": "NOW WATCH 2", "tone": "gold", "y": 300, "from": "isn't", "to": "FOUR-0.1"}]})
    # 08 FOUR screens for TWO: O4 planted, X2 runs into him (freeze), O2 curls out
    sh.append({"id": "08-screen2", "name": "SCREEN THE SCREENER (3/4 moderate, B 2.75 -> 3.75, freeze at X2's contact 3.0): O4 down-screens X2, O2 curls over the top",
               "at": "FOUR-0.1", "play": "B", "branch": "b",
               "remap": [[0, 2.75], ["for TWO.>", 3.0], ["the screener.", 3.0], ["Two escapes-0.1", 3.75]],
               "camera": [key(0, DS0), key("the screener.", DS0), key("Two escapes-0.1", DS1, "inOut")],
               "ov3": [{"type": "ring", "player": "X2", "color": RED, "size": 0.5, "from": "for TWO.", "to": "Two escapes-0.1"},
                       {"type": "route", "player": "O2", "t0": 2.2, "t1": 4.33, "width": 0.09, "draw": 0.6, "color": GOLD, "from": "Screen…", "to": "Two escapes-0.1"}],
               "screen": [{"type": "freeze", "from": "for TWO.>", "to": "the screener."},
                          {"type": "stamp", "text": "1ST: O2 → O5", "tone": "white", "y": 300, "from": 0.15, "to": "Screen…"},
                          {"type": "stamp", "text": "2ND: O4 → O2", "tone": "gold", "y": 300, "from": "Screen…", "to": "Two escapes-0.1"}]})
    # 09 two escapes to the wing: pass, catch, three, net
    sh.append({"id": "09-three", "name": "READ 2 PAYOFF (SHOT_FOLLOW -> RIM_PAYOFF, B 3.70 -> 5.95): O3 -> O2, two-hand catch, feet behind the arc, three, net",
               "at": "Two escapes-0.1", "play": "B", "branch": "b",
               "remap": [[0, 3.70], ["Catch.", "catch"], ["Three.", "release"], ["Three.>+0.55", "make"], ["Same box-0.1", 5.95]],
               "camera": [key(0, SHOOT0), key("Three.+0.12", SHOOT0), key("Three.>+0.05", RIMB, "inOut")],
               "ov3": [{"type": "ballPath", "src": "O3", "dst": "O2", "draw": 0.3, "color": GOLD, "from": 0.2, "to": "Catch."},
                       {"type": "spot", "player": "O2", "r": 0.45, "color": GOLD, "strength": 0.5, "from": "Catch.", "to": "Three.+0.2"}],
               "screen": [{"type": "stamp", "text": "READ 2: THREE", "tone": "gold", "y": 300, "from": "Three.>+0.62", "to": "Same box-0.1"}]})
    # 10 same box, two reads: alternating, SAME camera (brief allows two alternating shots instead of a split)
    sh.append({"id": "10a-stays", "name": "TWO READS (TAC, A 1.30 -> 2.45): X4 STAYS",
               "at": "Same box-0.1", "play": "A", "branch": "a",
               "remap": [[0, 1.30], ["Same action.-0.1", 2.45]],
               "camera": [key(0, TAC)],
               "ov3": [{"type": "route", "player": "X4", "t0": 1.3, "t1": 2.6, "width": 0.08, "draw": 0.4, "color": RED, "from": 0.2, "to": "Same action.-0.1"}],
               "screen": [{"type": "stamp", "text": "X4 STAYS", "tone": "white", "y": 300, "from": 0.05, "to": "Same action.-0.1"}]})
    sh.append({"id": "10b-helps", "name": "TWO READS (TAC, B 1.30 -> 2.75): X4 HELPS",
               "at": "Same action.-0.1", "play": "B", "branch": "b",
               "remap": [[0, 1.30], ["You're-0.1", 2.75]],
               "camera": [key(0, TAC)],
               "ov3": [{"type": "route", "player": "X4", "t0": 1.3, "t1": 2.4, "width": 0.08, "draw": 0.4, "color": RED, "from": 0.2, "to": "You're-0.1"},
                       {"type": "route", "player": "O4", "t0": 1.9, "t1": 2.9, "width": 0.08, "draw": 0.4, "color": GOLD, "from": 0.6, "to": "You're-0.1"}],
               "screen": [{"type": "stamp", "text": "X4 HELPS", "tone": "gold", "y": 300, "from": 0.05, "to": "You're-0.1"}]})
    # 11 you're X4: freeze at the decision (B 1.70), RIM / SWITCH on the floor, logo, back to the hook frame (loop)
    sh.append({"id": "11-call", "name": "YOUR CALL (freeze B 1.70, slow orbit back to the hook camera): RIM / SWITCH floor arrows, logo",
               "at": "You're-0.1", "play": "B", "branch": "b",
               "remap": [[0, 1.70], ["@end", 1.75]],
               "camera": [key(0, CLOSE0), key("RIM or SWITCH.", CLOSE0), key("@end", CLOSE1, "inOut")],
               "ov3": [{"type": "route", "player": "X4", "pts": [[-1.88, 2.45], [-1.45, 2.25], [-1.0, 2.05]], "t0": 0, "t1": 1, "width": 0.11, "draw": 0.5,
                        "color": RED, "from": "Protect#2", "to": "@end-0.6"},
                       {"type": "route", "player": "X4", "pts": [[-1.88, 2.45], [-1.6, 3.6], [-1.2, 4.6]], "t0": 0, "t1": 1, "width": 0.15, "draw": 0.5,
                        "color": GOLD, "from": "switch onto", "to": "@end-0.6"},
                       {"type": "floorText", "text": "RIM", "at": [-0.65, 1.95], "size": 0.5, "color": RED, "plate": True, "yaw": -30, "from": "rim#2", "to": "@end-0.6"}],
               "screen": [{"type": "stamp", "text": "SWITCH ONTO 2?", "tone": "gold", "y": 300, "from": "switch onto", "to": "@end-0.6"},
                          {"type": "logo", "from": "SWITCH#2>", "to": "@end"}]})
    return sh


def groups(words):
    """caption units: one sentence per unit (3-7 words), split long ones; '…' ends a unit too"""
    out, cur = [], []
    for w in words:
        cur.append(w["text"])
        if w["text"][-1] in ".?!…:" or (w["text"].endswith(",") and len(cur) >= 3):
            n = len(cur)
            while n > 6:
                out.append(n // 2); n -= n // 2
            out.append(n); cur = []
    if cur:
        out.append(len(cur))
    return out


def build():
    src = json.load(open(os.path.join(D, "blob-voice.json")))
    ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw", "gapFill")}
    ep["id"], ep["title"] = EID, "BLOB Box Screen-the-Screener"
    ep["branches"] = {"a": "A", "b": "B"}
    ep["tail"] = 1.12                     # last word 38.88 s + 1.12 = 40.00 s = 1200 frames
    ep["env"] = "academy"
    ep["shots"] = shots()
    ep["pinV2"] = True
    ep["autoSfx"] = False
    ep["keywords"] = ["HE", "TWO", "FIVE", "FOUR", "easy layup", "protect the rim", "screener", "Screen… the screener", "Three", "X-four", "RIM", "SWITCH"]
    ep["subtitleY"] = 1350
    ep["subtitleYAt"] = [[0, "On-0.06", 270]]   # hook: O2 (gold ring) owns the lower middle; the caption sits over the stands
    words = json.load(open(os.path.join(D, "blob-voice.words.json")))
    ep["subtitleGroups"] = groups(words)
    ep["subtitleBlock"] = True
    ep["music"] = {"src": "tactical/blob/music.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{EID}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "blob-voice.words.json"), os.path.join(D, f"{EID}.words.json"))
    print(EID, len(ep["shots"]), "shots", ep["subtitleGroups"])


if __name__ == "__main__":
    build()
