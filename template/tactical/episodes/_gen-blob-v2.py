#!/usr/bin/env python3
"""BLOB SCREEN-THE-SCREENER V2 CINEMATIC (owner brief E2A_BLOB_V2_MASTER_PROMPT_CINEMATIC_3D_CAMERA_VFX, 2026-11-21).
ONE final ~40 s reel from the SAME plays as V1 (blob-a-rim / blob-b-three, unchanged): only camera grammar, telestration,
voice, music, light and edit change.
  python3 scripts/tactical-voice.py tactical/episodes/blob-v2-voice.json      (ONE new Deuce take, eleven_v4 tags)
  python3 tactical/episodes/_gen-blob-v2.py                                   -> blob-screen-the-screener-v2.json
  node scripts/tactical-props.mjs tactical/episodes/blob-screen-the-screener-v2.json out/blob/<id>.props.json
ShotTimeline = the shot list below: editorialTime (word anchors of the real narration) -> simulationTime (remap keys,
play marks) + branch + camera keys + VFX cues. The plays are never slowed globally: slow motion / freezes / rewinds are
explicit per-shot remaps (O3 still releases at 2.27 s (A) / 3.70 s (B) of SIMULATION time).
CinematicCameraRig presets (camera3d.ts orbit rigs): HERO_ORBIT (spin key, 200 deg around O3), TOP_DOWN (pitch 10 =
80 deg elevation, long lens), SCREEN_CONTACT, PLAYER_FOLLOW, SHOT_HERO, DECISION.
Repo axes: x = -brief x; orbit yaw 0 = camera on the half-court side looking at the basket, yaw 90 = camera at x < 0,
yaw 180 = behind the baseline; pitch from the vertical (90 = horizontal)."""
import json, os, shutil, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
groups = import_module("_gen-blob").groups
orb = lambda tg, dist, pitch, yaw, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None, spin=False: {"at": at, "rig": rig, **({"ease": ease} if ease else {}), **({"spin": True} if spin else {})}
f = lambda ids, z=1.0, w=0.4, lead=0.0: {"follow": ids, "z": z, "window": w, **({"lead": lead} if lead else {})}
EID = "blob-screen-the-screener-v2"
RED, GOLD, CORAL, WHITE = "#E5483A", "#E3BE68", "#F06A55", "#FFFFFF"
RIM = [0.0, 1.575]

# ---------------- CinematicCameraRig presets (probe sheets in out/blob/v2/probe*)
HK0 = orb([-1.4, 1.0, 1.2], 7.5, 70, 150)                  # frame 0: behind O3 (ball), the defense shutting the rim
HK0B = orb([-1.3, 1.15, 1.2], 6.8, 70, 153)                # micro push on WAIT!
HK1 = orb([-2.2, 3.3, 0.6], 13.0, 52, 160)                 # reveal: rise + pull back, O2 open at the top
HK1B = orb([-2.35, 3.55, 0.6], 12.4, 52, 163)
BOX0 = orb(f("O3", 1.1, 0.3), 5.0, 70, 100)                # crane start low behind the inbounder
BOX1 = orb([-0.9, 2.0, 0.6], 14.0, 42, 25)                # crane end: the whole BOX + O3 out of bounds
SCR0 = orb(f(["O2"], 1.0, 0.5), 7.5, 68, -75)              # screen 1: O2 tracked from the side
SCR1 = orb([1.4, 2.5, 0.9], 6.0, 68, -150, 44)            # SCREEN_CONTACT: both feet of O2, X5 meeting him, O5 starting
LAY0 = orb([0.4, 2.0, 1.0], 7.2, 74, -38)                  # O5 cut + pass + rim
LAY1 = orb([-0.25, 1.8, 1.6], 7.0, 78, -18)
RW0 = orb([-0.6, 1.9, 0.9], 10.5, 62, -28)                 # rewind wide
PRE0 = orb([-1.9, 0.6, 1.1], 7.5, 66, 190)                 # B reset: behind the baseline, glides into the orbit start
O3F = f("O3", 1.15, 0.3)
ORB0 = orb(O3F, 3.2, 70, 228, 50)                          # HERO_ORBIT start (behind O3, court + rim beyond)
ORBM = orb(O3F, 4.6, 36, 126, 50)                          # HERO_ORBIT mid: higher, over O3's shoulder (ball visible past the stanchion side)
ORB1 = orb(O3F, 5.6, 50, 25, 50)                            # HERO_ORBIT end (court side, O3 front, ball) = 203 deg
TD0 = orb([-1.0, 3.8, 0.0], 16.0, 10, 0, 40)               # TOP_DOWN (80 deg elevation, basket at the top)
TD1 = orb([-1.3, 4.0, 0.0], 15.0, 10, 0, 40)
TR0 = orb(f("O2", 1.1, 0.4, 0.25), 6.5, 78, 32)            # PLAYER_FOLLOW: low lateral, slightly ahead of O2
TR1 = orb(f("O2", 1.2, 0.4, 0.1), 5.8, 76, 40)
SH0 = orb([-3.0, 4.3, 2.4], 8.0, 76, 47, 48)               # SHOT_HERO: over O2's shoulder, arc + rim
SH1 = orb([-0.7, 2.0, 2.8], 6.5, 80, 40, 44)               # ball through the net
SUM0 = orb([-0.8, 2.6, 0.6], 13.0, 50, -15)                # summary: same box, two reads
SUM1 = orb([-0.9, 2.5, 0.6], 12.0, 52, -6)
DEC0 = orb([-0.8, 2.4, 1.2], 7.0, 66, 135, 46)             # DECISION: just behind X4, rim to one side, O2's lane to the other
DEC1 = orb([-0.8, 2.3, 1.2], 6.4, 67, 140, 46)


def shots():
    sh = []
    # 01 HOOK  (B 2.50 -> 3.66, ball still with O3): WAIT! frame-0 impact on the shut rim, then the 3D reveal of O2
    sh.append({"id": "01-hook", "name": "HOOK: behind O3, defense shuts the rim (B 2.50) -> rise / pull-back reveal of O2 open (B 3.66, pre-pass)",
               "at": 0, "play": "B", "branch": "b",
               "remap": [[0, 2.50], ["WAIT!>", 2.53], ["open?!>", 3.60], ["One-0.08", 3.66]],
               "camera": [key(0, HK0), key("WAIT!>", HK0B, "linear"), key("open?!", HK1, "inOut"), key("One-0.08", HK1B, "linear")],
               "ov3": [{"type": "glow", "hoop": True, "r": 1.4, "color": CORAL, "strength": 0.6, "from": 0, "to": "left"},
                       {"type": "spot", "player": "X4", "r": 0.55, "color": RED, "strength": 0.6, "beam": False, "from": 0.1, "to": "TWO"},
                       {"type": "spot", "player": "O2", "r": 0.7, "color": GOLD, "strength": 0.9, "from": "TWO", "to": "One-0.08"}],
               "screen": [{"type": "flash", "color": "#FFE9C8", "strength": 0.22, "from": 0, "to": 0.25},
                          {"type": "punch", "amount": 0.035, "from": "STOPPED", "to": "layup..."},
                          {"type": "focus", "player": "O2", "r": 380, "strength": 0.45, "from": "TWO", "to": "One-0.08"}]})
    # 02 BOX  (B rewind 3.66 -> 0, the set): crane-back from the inbounder to the whole box
    sh.append({"id": "02-box", "name": "BOX: rewind to the set, crane-back from O3 to the whole BOX (B 0.00 -> 0.45)",
               "at": "One-0.08", "play": "B", "branch": "b",
               "remap": [[0, 3.66, "inOut"], [0.45, 0.0], ["nightmares.", 0.0], ["Watch-0.08", 0.45]],
               "camera": [key(0, BOX0), key(0.45, BOX0, "hold"), key("nightmares.", BOX1, "inOut"), key("Watch-0.08", BOX1, "linear")],
               "ov3": [{"type": "spot", "player": "O3", "r": 0.55, "color": GOLD, "strength": 0.7, "beam": False, "from": 0.45, "to": "inbound."},
                       {"type": "floorText", "text": "INBOUND", "at": [-1.9, -0.6], "yaw": 25, "size": 0.42, "plate": True, "from": "baseline", "to": "Watch-0.08"},
                       {"type": "floorText", "text": "BOX", "at": [0.0, 3.6], "yaw": 25, "size": 0.9, "from": "Two different", "to": "Watch-0.08"}],
               "screen": [{"type": "rewind", "from": 0, "to": 0.45}]})
    # 03 SCREEN 1  (B = A until S050): O2 tracked into the screen, plant at 1.43, SCREEN_CONTACT close-up
    sh.append({"id": "03-screen1", "name": "SCREEN 1: track O2 into the screen; plant 1.43 -> O2 SCREENS X5, X5 blocked, O5 cut (B 0.45 -> 1.58)",
               "at": "Watch-0.08", "play": "B", "branch": "b",
               "remap": [[0, 0.45], ["screens", 1.30], ["FIVE.>", 1.50], ["If-0.08", 1.58]],
               "camera": [key(0, SCR0), key("screens", SCR1, "inOut"), key("If-0.08", SCR1, "linear")],
               "ov3": [{"type": "ring", "player": "O2", "color": GOLD, "size": 0.7, "pulse": True, "from": 0, "to": "screens"},
                       {"type": "route", "player": "O2", "t0": 0.45, "t1": 1.43, "consume": True, "color": GOLD, "width": 0.13, "from": 0.2, "to": "screens"},
                       {"type": "screenTag", "player": "O2", "vs": "X5", "n": 1, "label": "O2 SCREENS X5", "plantAt": 1.4333, "yaw": -150, "labelOffset": [0.5, -0.9], "size": 0.34, "from": "screens", "to": "If-0.08"},
                       {"type": "route", "player": "X5", "t0": 0, "t1": 0, "pts": [[1.88, 2.58], [1.70, 2.49], [1.56, 2.42]], "dashed": True, "color": RED, "width": 0.09, "draw": 0.3, "from": "for", "to": "If-0.08"},
                       {"type": "route", "player": "O5", "t0": 1.5, "t1": 2.35, "fromPlay": "A", "color": GOLD, "width": 0.13, "draw": 0.7, "from": "FIVE.", "to": "If-0.08"}]})
    # 04 READ A: X4 stays, O3 -> O5, layup through the net
    sh.append({"id": "04-layup", "name": "READ A: O5 cuts behind, O3 -> O5, catch, layup, net (A 1.58 -> 3.75)",
               "at": "If-0.08", "play": "A", "branch": "a",
               "remap": [[0, 1.58], ["cuts", "pass"], ["and finishes.", "catch"], ["finishes.>+0.12", "make"], ["But now-0.1", 3.75]],
               "camera": [key(0, LAY0), key("and finishes.", LAY1, "inOut"), key("But now-0.1", LAY1, "linear")],
               "ov3": [{"type": "passLane", "src": "O3", "dst": "O5", "travel": 0.55, "dstAt": 2.6333, "color": WHITE, "from": "cuts-0.1", "to": "and finishes."},
                       {"type": "ballTrail", "len": 0.25, "from": "and finishes.", "to": "But now-0.1"}],
               "screen": [{"type": "stamp", "text": "READ 1: RIM", "tone": "gold", "y": 300, "from": "finishes.>+0.2", "to": "But now-0.1"}]})
    # 05a REWIND (A 3.75 -> 1.40)  05b B RESET: the defense sees it coming (B 1.40 -> 1.62), glide into the orbit start
    sh.append({"id": "05a-rewind", "name": "REHOOK: clean reverse replay of read A to the common moment (A 3.75 -> 1.40)",
               "at": "But now-0.1", "play": "A", "branch": "a",
               "remap": [[0, 3.75, "inOut"], ["defense-0.1", 1.40]],
               "camera": [key(0, LAY1), key("defense-0.1", RW0, "inOut")],
               "ov3": [],
               "screen": [{"type": "rewind", "from": 0, "to": "defense-0.1"}]})
    sh.append({"id": "05b-reset", "name": "READ B RESET: same moment, now X4 reads the cut (B 1.40 -> 1.62)",
               "at": "defense-0.1", "play": "B", "branch": "b",
               "remap": [[0, 1.40], ["They collapse-0.08", 1.62]],
               "camera": [key(0, PRE0), key("They collapse-0.08", ORB0, "inOut")],
               "ov3": [],
               "screen": [{"type": "hud", "tag": "READ 2", "text": "BUT IF THEY HELP?", "y": 300, "from": 0.05, "to": "They collapse-0.08"}]})
    # 06 HERO ORBIT: 200 deg around O3 (ball), simulation slowed 0.22x: X4 collapses on the rim, O3's pass fake to O5
    sh.append({"id": "06-orbit", "name": "HERO ORBIT 200 deg around O3 with the ball (B 1.62 -> 2.25 at ~0.22x): X4 collapses, O3 fakes",
               "at": "They collapse-0.08", "play": "B", "branch": "b",
               "remap": [[0, 1.62], ["Because-0.1", 2.25]],
               "camera": [key(0, ORB0), key(1.44, ORBM, "in", spin=True), key("Because-0.1", ORB1, "out", spin=True)],
               "ov3": [{"type": "glow", "player": "O3", "r": 0.75, "color": GOLD, "strength": 0.45, "from": 0, "to": "Because-0.1"},
                       {"type": "glow", "hoop": True, "r": 1.1, "color": GOLD, "strength": 0.35, "from": 0, "to": "on"},
                       # VFX 06 DEFENSIVE COMMITMENT FLASH: the zone X4 leaves (B 1.6 at -1.88,2.45) + arrow to the rim, as X4 starts to help
                       {"type": "openSpace", "at": [-1.95, 2.5], "r": 0.7, "color": CORAL, "from": "on", "to": "rim.>+0.2"},
                       {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": [[-1.9, 2.45], [-1.5, 2.25], [-1.1, 2.1]], "color": CORAL, "width": 0.11, "draw": 0.3, "from": "on", "to": "rim.>+0.2"},
                       {"type": "spot", "player": "X4", "r": 0.6, "color": CORAL, "strength": 0.8, "beam": False, "from": "collapse", "to": "on"}]})
    # 07 TOP-DOWN: rise to 80 deg, screen 2 (O4 SCREENS X2), O2 curls; recap screen 1 on "the guy who set the first"
    sh.append({"id": "07-topdown", "name": "TOP-DOWN: rise from the orbit; O4 plants 2.87 -> O4 SCREENS X2, O2 curls (ghosts), recap SCREEN 1 (B 2.25 -> 3.20)",
               "at": "Because-0.1", "play": "B", "branch": "b",
               "remap": [[0, 2.25], ["FOUR", 2.50], ["screen...", 2.87], ["for the guy", 2.95], ["the first.>", 3.15], ["TWO escapes-0.08", 3.20]],
               "camera": [key(0, ORB1), key(2.0, TD0, "inOut"), key("TWO escapes-0.08", TD1, "linear")],
               "ov3": [{"type": "spot", "player": "X4", "r": 0.6, "color": RED, "strength": 0.6, "beam": False, "from": 1.3, "to": "second"},
                       {"type": "route", "player": "O4", "t0": 2.25, "t1": 2.87, "consume": True, "color": GOLD, "width": 0.16, "from": "FOUR", "to": "screen..."},
                       {"type": "screenTag", "player": "O4", "vs": "X2", "n": 2, "label": "O4 SCREENS X2", "plantAt": 2.8667, "yaw": 0, "labelOffset": [-2.3, 0.0], "size": 0.55, "from": "screen...", "to": "guy"},
                       {"type": "ghostTrail", "player": "O2", "n": 3, "len": 0.5, "from": "second", "to": "for the guy"},
                       {"type": "route", "player": "X2", "t0": 0, "t1": 0, "pts": [[-0.10, 3.55], [-0.28, 3.85], [-0.42, 4.02]], "dashed": True, "color": RED, "width": 0.12, "draw": 0.3, "from": "screen...", "to": "guy"},
                       {"type": "route", "player": "O2", "t0": 2.87, "t1": 4.37, "color": GOLD, "width": 0.16, "draw": 0.6, "from": "guy", "to": "TWO escapes-0.08"},
                       {"type": "screenTag", "player": "O2", "vs": "X5", "n": 1, "label": "O2 SCREENS X5", "plantAt": 1.4333, "yaw": 0, "labelOffset": [-4.25, -0.2], "size": 0.5, "from": "guy", "to": "TWO escapes-0.08"}]})
    # 08 PLAYER FOLLOW: O2 escapes, X2 late, pass O3 -> O2, catch and release in the same continuous shot
    sh.append({"id": "08-escape", "name": "FOLLOW O2: escapes to the wing, X2 late, O3 -> O2, catch 4.37, release 4.70 (B 3.20 -> 4.86, ~0.43x)",
               "at": "TWO escapes-0.08", "play": "B", "branch": "b",
               "remap": [[0, 3.20], ["late.>", 3.98], ["Catch.", "catch"], ["Set.#2", "release"], ["Set.#2>", 4.86]],
               "camera": [key(0, TR0), key("Catch.", TR1, "inOut"), key("Set.#2>", TR1, "linear")],
               "ov3": [{"type": "ring", "player": "X2", "color": RED, "size": 0.65, "from": "defender", "to": "Catch."},
                       {"type": "openSpace", "at": [-5.2, 6.5], "r": 1.1, "color": GOLD, "from": "outside.", "to": "Catch."},
                       {"type": "passLane", "src": "O3", "dst": "O2", "travel": 0.7, "dstAt": 4.3667, "color": WHITE, "from": "late.-0.1", "to": "Catch."}]})
    # 09 SHOT HERO: arc + rim, ball through the net
    sh.append({"id": "09-three", "name": "SHOT HERO: over O2's shoulder, flight, ball through the net (B 4.86 -> 6.10)",
               "at": "Set.#2>", "play": "B", "branch": "b",
               "remap": [[0, 4.86], ["THREE!>+0.25", "make"], ["Same box-0.1", 6.10]],
               "camera": [key(0, SH0), key("THREE!>", SH1, "inOut"), key("Same box-0.1", SH1, "linear")],
               "ov3": [{"type": "ballTrail", "len": 0.3, "from": 0, "to": "Same box-0.1"}],
               "screen": [{"type": "stamp", "text": "READ 2: THREE", "tone": "gold", "y": 300, "from": "THREE!>+0.4", "to": "Same box-0.1"}]})
    # 10 SUMMARY: same box, X4's two choices (ghost of read A vs read B), no new possession
    sh.append({"id": "10-same", "name": "SAME BOX / DIFFERENT READ: B frozen at 2.30 (X4 at the rim) + ghost of X4 in read A",
               "at": "Same box-0.1", "play": "B", "branch": "b",
               "remap": [[0, 2.30], ["You're-0.1", 2.30]],
               "camera": [key(0, SUM0), key("You're-0.1", SUM1, "linear")],
               "ov3": [{"type": "ghost", "at": [-2.0, 2.6], "color": WHITE, "from": "Same box", "to": "You're-0.1"},
                       {"type": "spot", "player": "X4", "r": 0.6, "color": RED, "strength": 0.8, "beam": False, "from": "screens.#2", "to": "You're-0.1"},
                       {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": [[-1.85, 2.55], [-1.5, 2.3], [-1.2, 2.15]], "color": RED, "width": 0.11, "draw": 0.4, "from": "Different#2", "to": "You're-0.1"}],
               "screen": [{"type": "stamp", "text": "SAME PLAY · NEW READ", "tone": "white", "y": 300, "from": 0.1, "to": "You're-0.1"}]})
    # 11 DECISION: you're X4 (B frozen at 2.50 = the hook's first frame): RIM? then SWITCH?, ends on the hook frame (loop)
    sh.append({"id": "11-decision", "name": "DECISION: behind X4, freeze B 2.50; RIM? (red) then SWITCH? (gold); dolly back to the hook's frame 0",
               "at": "You're-0.1", "play": "B", "branch": "b",
               "remap": [[0, 2.50], ["@end", 2.50]],
               "camera": [key(0, DEC0), key("Comment:", DEC1, "linear"), key("@end", HK0, "inOut")],
               "ov3": [{"type": "ring", "player": "X4", "color": RED, "size": 0.65, "from": 0.1, "to": "@end"},
                       {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": [[-1.0, 2.0], [-0.6, 1.85], [-0.25, 1.7]], "color": RED, "width": 0.13, "draw": 0.35,
                        "label": "RIM?", "labelYaw": 135, "labelOffset": [0.5, 0.0], "labelSize": 0.42, "from": "Protect", "to": "@end"},
                       {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": [[-1.0, 2.15], [-1.2, 3.2], [-1.0, 4.3], [-0.9, 5.0]], "color": GOLD, "width": 0.13, "draw": 0.5,
                        "label": "SWITCH?", "labelYaw": 135, "labelOffset": [0.3, -0.6], "labelSize": 0.42, "from": "switch", "to": "@end"}],
               "screen": [{"type": "freeze", "from": 0.1, "to": "@end"},
                          {"type": "title", "lines": ["RIM", "OR SWITCH?"], "gold": [1], "y": 300, "size": 120, "from": "Comment:", "to": "@end"},
                          {"type": "logo", "from": "SWITCH.#2>", "to": "@end"}]})
    return sh


def build():
    src = json.load(open(os.path.join(D, "blob-v2-voice.json")))
    ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw", "gapFill")}
    ep["id"], ep["title"] = EID, "BLOB Screen-the-Screener V2 cinematic"
    ep["branches"] = {"a": "A", "b": "B"}
    words = json.load(open(os.path.join(D, "blob-v2-voice.words.json")))
    ep["tail"] = round(40.0 - words[-1]["end"], 3)          # 40.00 s = 1200 frames
    ep["env"] = "cinema"
    ep["shots"] = shots()
    ep["pinV2"] = True
    ep["autoSfx"] = False
    ep["keywords"] = ["WAIT!", "STOPPED", "TWO", "wide", "open?!", "FIVE", "finishes.", "rim.", "FOUR", "second", "first.", "THREE!", "X4.", "RIM", "SWITCH."]
    ep["subtitleY"] = 1350
    ep["subtitleYAt"] = [["One-0.08", "If-0.08", 270]]   # box + screen 1: the BOX and the screen own the lower half
    # display text: X-FOUR is spoken, the caption shows the real label X4 (brief: "YOU'RE X4")
    disp = [dict(w, text=w["text"].replace("X-FOUR", "X4")) for w in words]
    ep["subtitleGroups"] = groups(disp)
    ep["subtitleBlock"] = True
    ep["music"] = {"src": "tactical/blob/music-v2.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{EID}.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(disp, open(os.path.join(D, f"{EID}.words.json"), "w"), indent=0)
    print(EID, len(ep["shots"]), "shots, tail", ep["tail"])


if __name__ == "__main__":
    build()
