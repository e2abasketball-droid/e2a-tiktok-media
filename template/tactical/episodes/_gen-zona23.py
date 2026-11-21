#!/usr/bin/env python3
"""2-3 ZONE 40 s CINEMATIC (owner master brief E2A_CLAUDE_MASTER_23_ZONE_40S_CINEMATIC.md, 2026-11-21).
ONE final ~40 s reel. Plays (tactical/specs/_gen-zone23.py, QC'd with test-play / qc-contact / qc-catch):
  A zone23-a-nail  flash to the nail, X5 steps up after the catch, O4 cuts behind X4, high-low layup
  B zone23-b-skip  O1 -> O2, DIRECT skip O2 -> O3, X2 / X4 late, three
  C zone23-c-slow  same set, O2 holds the ball too long, the zone resets, O3 contested
  python3 scripts/tactical-voice.py tactical/episodes/zona23-voice.json      (ONE Deuce take, eleven_v4 tags)
  python3 tactical/episodes/_gen-zona23.py                                   -> zona-2-3-zone.json
  node scripts/tactical-props.mjs tactical/episodes/zona-2-3-zone.json out/blob/zona-2-3-zone.props.json
Editorial time (word anchors of the real narration) is separate from game time (remap keys per shot): slow motion,
freezes and resets are explicit per shot; the plays themselves are never re-timed.
Repo axes: x = -brief x (brief x < 0 = LEFT seen from half court); orbit yaw 0 = camera on the half-court side,
yaw 90 = camera at repo x < 0 (brief RIGHT sideline, O3's side), pitch from the vertical (10 = top-down)."""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
groups = import_module("_gen-blob").groups
orb = lambda tg, dist, pitch, yaw, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None, spin=False: {"at": at, "rig": rig, **({"ease": ease} if ease else {}), **({"spin": True} if spin else {})}
f = lambda ids, z=1.0, w=0.4, lead=0.0: {"follow": ids, "z": z, "window": w, **({"lead": lead} if lead else {})}
EID = "zona-2-3-zone"
RED, GOLD, CORAL, WHITE = "#E5483A", "#E3BE68", "#F06A55", "#FFFFFF"
M = lambda p: [round(-p[0], 3), p[1]]
NAIL = [0.0, 5.8]
# brief sec. 11.1 areas (brief axes) -> repo axes [x0, x1, y0, y1]
BR = {"X1": (-4.3, 0.4, 5.0, 8.1), "X2": (-0.4, 4.3, 5.0, 8.1), "X3": (-7.0, -1.7, 0.6, 5.1), "X4": (1.7, 7.0, 0.6, 5.1), "X5": (-2.5, 2.5, 0.6, 5.75)}
AREAS = {k: [round(-v[1], 2), round(-v[0], 2), v[2], v[3]] for k, v in BR.items()}
LAB = {"X1": "TOP", "X2": "TOP", "X3": "LOW", "X4": "LOW", "X5": "MIDDLE"}
LPOS = {"X1": "hi", "X2": "hi", "X3": "lo", "X4": "lo", "X5": "hi"}


def zg(**kw):
    return {"type": "zoneGrid", "areas": AREAS, **kw}


# ---------------- CinematicCameraRig presets (camera3d.ts orbit rigs; probe stills in out/blob/z23/)
# 9:16: the zone spans 14 m of court width, so the wide / top views look ACROSS the court (yaw ~90): court width runs
# up the frame, baseline -> top of the key across it; the basket sits on the right of frame.
HK0 = orb([0.0, 5.4, 0.9], 9.8, 54, 8, 46)                 # hook frame 0 (coordinator note): close, behind the ball handler, on the nail gap
HKW = orb([0.0, 4.4, 0.4], 17.5, 44, 72)                   # the whole 5v5 semi-top (CTA end)
HK1 = orb([0.0, 4.6, 0.4], 16.5, 40, 100, 40)              # ... ~30 deg later
HN = orb([0.0, 5.6, 0.6], 10.0, 42, 104, 40)               # push toward the nail ("Right HERE")
HN2 = orb([0.0, 5.0, 0.4], 13.5, 30, 98, 40)               # ... starts rising toward the true top after HERE
TD0 = orb([0.0, 4.4, 0.0], 21.0, 12, 90, 40)               # TRUE TOP: 78 deg, rim visible on the right
TD1 = orb([0.0, 4.5, 0.0], 20.5, 12, 90, 40)
TR0 = orb([0.0, 4.8, 0.0], 21.0, 14, 90, 40)               # top that turns ~20 deg while the ball goes to the wing
TR1 = orb([0.4, 4.8, 0.0], 21.0, 16, 70, 40)
FL0 = orb([0.3, 5.4, 0.6], 11.5, 40, 128, 42)              # flash: top 3/4 from the right-elbow side ...
FL1 = orb(f(["O5"], 1.0, 0.5), 8.5, 60, 112, 42)           # ... down to a lateral on O5 at the nail
SU0 = orb([-1.4, 3.6, 0.9], 10.5, 58, -25, 44)               # step-up: low 3/4, X5 and O5 + O4 beyond
SU1 = orb([-1.2, 3.4, 0.9], 10.5, 60, -18, 44)
BL0 = orb(f(["O4"], 1.0, 0.4, 0.2), 7.5, 66, 40, 44)      # baseline tracking of the cutter toward the rim
BL1 = orb([-0.4, 1.7, 1.5], 7.0, 72, 22, 44)
SQ0 = orb([0.0, 4.2, 0.6], 14.0, 34, 120, 40)              # squeeze: orbit around the whole set (freeze)
SQ1 = orb([0.0, 4.2, 0.6], 13.5, 32, 70, 40)
R2 = orb([2.2, 5.2, 0.5], 16.0, 30, 82, 40)                # READ 02: semi-top, ball to the left wing
SK0 = orb([3.6, 6.0, 1.2], 9.5, 76, 92, 46)                # skip: courtside lateral close to O2 ...
SK1 = orb([0.0, 5.6, 1.6], 15.0, 56, 106, 44)              # ... rises and opens over the whole skip
WS0 = orb([-4.0, 4.0, 0.8], 11.0, 52, 120, 44)             # weak side half orbit (decision X4)
WS1 = orb([-4.6, 4.3, 0.8], 10.0, 56, 60, 44)
TH0 = orb(f(["O3"], 1.4, 0.4), 6.2, 74, 32, 44)               # THREE: low, clean, shooter + rim
TH1 = orb([-1.6, 2.2, 2.6], 7.4, 80, 32, 44)
SL0 = orb([-1.1, 4.6, 0.0], 26.5, 12, 90, 40)               # slow pass: top-down comparison
SL1 = orb([-1.15, 4.8, 0.0], 26.0, 13, 92, 40)
CT0 = orb([0.0, 4.6, 0.0], 20.0, 16, 96, 40)               # CTA: top with a slight circular turn back to the hook
CT1 = HKW


def shots():
    sh = []
    # 01 HOOK: neutral set (A 0.00 frozen), five areas rise in quick sequence, the centre shaded
    sh.append({"id": "01-hook", "name": "HOOK: opens close behind the ball handler on the nail gap, orbits up/out to the whole 5v5 while the five areas rise (A 0.00)",
               "at": 0, "play": "A", "branch": "a",
               "remap": [[0, 0.0], ["Right...", 0.0]],
               "camera": [key(0, HK0), key("defenders.", HK0, "linear"), key("Right...", HK1, "inOut", spin=True)],
               "ov3": [zg(stagger=0.09, from_=0.0, to="Right...", fin=0.01),
                       {"type": "glow", "at": NAIL, "r": 1.0, "color": GOLD, "strength": 0.6, "from": 0, "to": "Right..."}],
               "screen": [{"type": "flash", "color": "#FFE9C8", "strength": 0.18, "from": 0, "to": 0.22},
                          {"type": "stamp", "text": "THE 2-3 ZONE", "tone": "white", "y": 300, "from": 0, "to": "ONE"},
                          {"type": "micro", "text": "ILLUSTRATIVE COVERAGE", "y": 300, "from": "ONE+0.05", "to": "Right..."}]})
    # 02 RIGHT HERE: push to the nail; spotlight + promise ring land on HERE
    sh.append({"id": "02-here", "name": "RIGHT HERE: orbit continues and pushes to the nail, ring + RIGHT HERE on HERE (A 0.00)",
               "at": "Right...", "play": "A", "branch": "a",
               "remap": [[0, 0.0], ["Two-0.1", 0.0]],
               "camera": [key(0, HK1), key("HERE.", HN, "inOut"), key("HERE.>+0.15", HN, "linear"), key("Two-0.1", HN2, "in")],
               "ov3": [zg(dim=0.55, from_=0, to="Two-0.1", fin=0.01),
                       {"type": "ripple", "at": NAIL, "r": 1.1, "rings": 3, "period": 0.9, "color": GOLD, "from": "HERE.", "to": "Two-0.1"},
                       {"type": "floorText", "text": "RIGHT HERE", "at": [0.0, 4.75], "yaw": 104, "size": 0.55, "plate": True, "from": "HERE.+0.1", "to": "Two-0.1"}]})
    # 03 THE 2-3: true top; TWO up top (X1 X2), THREE low (X3 X4 X5)
    sh.append({"id": "03-shape", "name": "THE 2-3: true top-down, X1/X2 TOP then X3/X4/X5 LOW + MIDDLE (A 0.00)",
               "at": "Two-0.1", "play": "A", "branch": "a",
               "remap": [[0, 0.0], ["These-0.1", 0.0]],
               "camera": [key(0, HN2), key(1.1, TD0, "out"), key("These-0.1", TD1, "linear")],
               "ov3": [zg(select=["X1", "X2"], only=True, from_=0, to="Three", fin=0.01),
                       {"type": "floorText", "text": "TOP 2", "at": [0.0, 6.5], "yaw": 90, "size": 0.8, "plate": True, "from": "Two", "to": "Three"},
                       zg(select=["X3", "X4", "X5"], only=True, from_="Three", to="These-0.1", fin=0.01),
                       {"type": "floorText", "text": "BOTTOM 3", "at": [0.0, 2.3], "yaw": 90, "size": 0.8, "plate": True, "from": "Three", "to": "These-0.1"}]})
    # 04 THE BOXES MOVE: the ball goes to the left wing (B 0 -> 1.3), the areas slide with their defenders
    sh.append({"id": "04-move", "name": "BOXES MOVE WITH THE BALL: top turning ~20 deg, O1 -> O2, the areas slide and overlap (B 0.00 -> 1.30)",
               "at": "These-0.1", "play": "B", "branch": "b",
               "remap": [[0, 0.0], ["boxes", 0.15], ["ball.>", 1.30], ["First,-0.12", 1.30]],
               "camera": [key(0, TD1), key("First,-0.12", TR1, "inOut")],
               "ov3": [zg(select=["X1", "X3"], selectAt=0.9, from_=0, to="First,-0.12", fin=0.01),
                       {"type": "ballTrail", "len": 0.3, "from": 0, "to": "First,-0.12"}]})
    # 05 FLASH: READ 01, O5 curls to the nail (gold path on the floor), X1 / X2 pinch, catch on "line."
    sh.append({"id": "05-flash", "name": "READ 01 FLASH: O5 curls to the nail, X1/X2 pinch, O1 -> O5, catch (A 0.00 -> 1.10)",
               "at": "First,-0.12", "play": "A", "branch": "a",
               "remap": [[0, 0.0], ["flash", 0.05], ["line.", 1.033], ["If-0.1", 1.10]],
               "camera": [key(0, FL0), key("line.", FL1, "inOut"), key("If-0.1", FL1, "linear")],
               "ov3": [{"type": "route", "player": "O5", "t0": 0.0, "t1": 1.0, "consume": True, "color": GOLD, "width": 0.12, "from": 0.1, "to": "line.>"},
                       {"type": "ring", "player": "O5", "color": GOLD, "size": 0.7, "pulse": True, "from": "line.", "to": "If-0.1"},
                       zg(dim=0.5, select=["X1", "X2"], from_=0, to="If-0.1", fin=0.01)],
               "screen": [{"type": "hud", "tag": "READ 01", "text": "ATTACK THE NAIL", "y": 300, "from": 0.05, "to": "line."}]})
    # 06 STEP UP: X5's area opens forward with him, SPACE OPENS behind; O4 starts the cut
    sh.append({"id": "06-stepup", "name": "IF THE CENTER STEPS UP: low 3/4, X5 steps up after the catch, O4 starts behind X4 (A 1.10 -> 1.78)",
               "at": "If-0.1", "play": "A", "branch": "a",
               "remap": [[0, 1.10], ["slips", 1.78]],
               "camera": [key(0, SU0), key("slips", SU1, "inOut")],
               "ov3": [zg(select=["X5"], dim=0.45, from_=0, to="slips", fin=0.01),
                       {"type": "floorText", "text": "SPACE OPENS", "at": [-1.3, 2.3], "yaw": -20, "size": 0.5, "plate": True, "from": "steps up", "to": "slips"},
                       {"type": "route", "player": "O4", "t0": 1.2, "t1": 2.4, "color": GOLD, "width": 0.12, "draw": 0.5, "from": "cutter", "to": "slips"}]})
    # 07 LAYUP: baseline tracking, O5 -> O4, catch, layup, ball through the net on "Layup.", +2
    sh.append({"id": "07-layup", "name": "LAYUP: baseline tracking of O4, O5 -> O4, catch, layup, net, +2 (A 1.78 -> 3.45)",
               "at": "slips", "play": "A", "branch": "a",
               "remap": [[0, 1.78], ["Layup.+0.12", 3.2], ["So-0.1", 3.45]],
               "camera": [key(0, BL0), key("Layup.", BL1, "inOut"), key("So-0.1", BL1, "linear")],
               "ov3": [{"type": "ballTrail", "len": 0.25, "from": 0, "to": "Layup.+0.15"},
                       {"type": "glow", "hoop": True, "r": 1.1, "color": GOLD, "strength": 0.6, "from": "Layup.+0.12", "to": "So-0.1"}],
               "screen": [{"type": "flash", "color": "#FFE3A3", "strength": 0.2, "from": "Layup.+0.12", "to": "Layup.+0.4"},
                          {"type": "stamp", "text": "+2", "tone": "gold", "y": 300, "from": "Layup.+0.15", "to": "So-0.1"}]})
    # 08 SQUEEZE: freeze at O5's catch, orbit around the set; the areas compress to the middle, X5 / X4 lit
    sh.append({"id": "08-squeeze", "name": "SO THE ZONE SQUEEZES THE MIDDLE: freeze A 1.60, orbit, areas compress, high post red (A 1.60 frozen)",
               "at": "So-0.1", "play": "A", "branch": "a",
               "remap": [[0, 1.60], ["Now-0.1", 1.60]],
               "camera": [key(0, SQ0), key("Now-0.1", SQ1, "inOut")],
               "ov3": [zg(select=["X5", "X4"], compress=1.0, compressIn=0.9, from_=0, to="Now-0.1"),
                       {"type": "glow", "at": NAIL, "r": 0.9, "color": RED, "strength": 0.5, "from": "squeezes", "to": "Now-0.1"}],
               "screen": [{"type": "freeze", "from": 0.05, "to": "Now-0.1"}]})
    # 09 READ 02: reset; semi-top, O1 -> O2 to the left wing, the areas shift left
    sh.append({"id": "09-read2", "name": "READ 02: reset, semi-top, O1 -> O2, the zone shifts to the ball (B 0.00 -> 0.93)",
               "at": "Now-0.1", "play": "B", "branch": "b",
               "remap": [[0, 0.0], ["pull", 0.25], ["wing...>", 0.93], ["and-0.06", 0.95]],
               "camera": [key(0, R2), key("and-0.06", SK0, "inOut")],
               "ov3": [{"type": "passLane", "src": "O1", "dst": "O2", "travel": 0.6, "dstAt": 0.9333, "color": WHITE, "from": "pull-0.1", "to": "wing...>"},
                       zg(select=["X1", "X3"], from_=0, to="and-0.06", fin=0.01)],
               "screen": [{"type": "hud", "tag": "READ 02", "text": "BALL TO THE WING", "y": 300, "from": 0.05, "to": "wing..."}]})
    # 10 SKIP: courtside lateral near O2, release on "SKIP.", rise to a 3/4 that shows the whole flight
    sh.append({"id": "10-skip", "name": "SKIP: courtside on O2, release 1.47 on SKIP, camera rises over the whole flight (B 0.95 -> 1.75)",
               "at": "and-0.06", "play": "B", "branch": "b",
               "remap": [[0, 0.95], ["SKIP.", 1.467], ["weak-side-0.12", 1.75]],
               "camera": [key(0, SK0), key("throw>", SK0, "linear"), key("weak-side-0.12", SK1, "inOut")],
               "ov3": [{"type": "ballTrail", "len": 0.35, "from": "SKIP.", "to": "weak-side-0.12"},
                       zg(dim=0.6, pulse={"at": 1.467, "ids": ["X2", "X4"], "dur": 0.8}, from_=0, to="weak-side-0.12", fin=0.01)]})
    # 11 TWO JOBS: freeze with the ball in the air (B 1.75); X4 fork RIM? / CLOSE?; "One late step." resumes to the release
    sh.append({"id": "11-jobs", "name": "TWO JOBS: half orbit on the weak side, freeze B 1.75, X4 fork RIM? / CLOSE?; resumes: X4 late, O3 catch 2.57, release 2.93",
               "at": "weak-side-0.12", "play": "B", "branch": "b",
               "remap": [[0, 1.75], ["shooter.>", 1.75], ["step.>", 2.93]],
               "camera": [key(0, WS0), key("shooter.>", WS1, "inOut", spin=True), key("step.>", TH0, "inOut")],
               "ov3": [zg(select=["X4"], dim=0.4, from_=0, to="step.>", fin=0.01),
                       {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": [[-4.4, 2.75], [-3.3, 2.2], [-2.1, 1.85], [-1.2, 1.7]], "color": RED, "width": 0.12, "draw": 0.35,
                        "label": "RIM?", "labelYaw": 95, "labelOffset": [0.0, -0.6], "labelSize": 0.6, "from": "guard", "to": "late-0.2"},
                       {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": [[-4.5, 2.95], [-4.9, 3.7], [-5.3, 4.4], [-5.6, 4.9]], "color": GOLD, "width": 0.12, "draw": 0.35,
                        "label": "CLOSE?", "labelYaw": 95, "labelOffset": [0.7, 0.3], "labelSize": 0.6, "from": "close", "to": "step.>"}],
               "screen": [{"type": "freeze", "from": 0.05, "to": "shooter.>"}]})
    # 12 THREE: low clean frame of rim + shooter, ball in on "points.", +3
    sh.append({"id": "12-three", "name": "THREE POINTS: low shot of shooter + rim, flight, net, +3 (B 2.93 -> 4.30)",
               "at": "step.>", "play": "B", "branch": "b",
               "remap": [[0, 2.93], ["points.>+0.1", 4.10], ["But-0.1", 4.30]],
               "camera": [key(0, TH0), key("points.>", TH1, "inOut"), key("But-0.1", TH1, "linear")],
               "ov3": [{"type": "ballTrail", "len": 0.3, "from": 0, "to": "points.>"},
                       {"type": "glow", "hoop": True, "r": 1.1, "color": GOLD, "strength": 0.6, "from": "points.", "to": "But-0.1"}],
               "screen": [{"type": "flash", "color": "#FFE3A3", "strength": 0.2, "from": "points.", "to": "points.+0.3"},
                          {"type": "stamp", "text": "+3", "tone": "gold", "y": 300, "from": "points.", "to": "But-0.1"}]})
    # 13 TOO SLOW: same set, O2 holds; top-down comparison, the zone resets, O3 contested
    sh.append({"id": "13-slow", "name": "TOO SLOW: top-down, O2 holds 1.3 s, skip late, X2 / X4 there with the catch (C 1.10 -> 3.45)",
               "at": "But-0.1", "play": "C", "branch": "c",
               "remap": [[0, 1.10], ["resets.", 3.30], ["Your-0.1", 3.45]],
               "camera": [key(0, SL0), key("Your-0.1", SL1, "linear")],
               "ov3": [zg(tone="red", dim=0.7, select=["X2", "X4"], selectAt=1.5, from_=0, to="Your-0.1", fin=0.01),
                       {"type": "ring", "player": "O3", "color": RED, "size": 0.7, "from": "resets.-0.35", "to": "Your-0.1"}],
               "screen": [{"type": "hud", "tag": "TOO SLOW", "text": "BALL HELD 1.3 s", "y": 300, "from": "pass", "to": "Your-0.1"},
                          {"type": "tint", "strength": 0.45, "from": "slowly?", "to": "Your-0.1"}]})
    # 14 CTA: top with a slight turn back to the hook frame; NAIL lit, SKIP arc wing to wing, comment prompt, logo
    sh.append({"id": "14-cta", "name": "YOUR CALL: NAIL lit, SKIP arc wing to wing, comment, logo; camera turns back to the hook frame (B 0.95 frozen)",
               "at": "Your-0.1", "play": "B", "branch": "b",
               "remap": [[0, 0.95], ["@end", 0.95]],
               "camera": [key(0, CT0), key("below.", CT1, "inOut", spin=True), key("@end", CT1, "linear")],
               "ov3": [zg(dim=0.5, from_=0, to="@end"),
                       {"type": "ripple", "at": NAIL, "r": 1.0, "rings": 3, "period": 0.9, "color": GOLD, "from": "NAIL...", "to": "@end"},
                       {"type": "route", "player": "O2", "t0": 0, "t1": 0, "pts": [[6.0, 6.3], [3.2, 7.4], [0.0, 7.8], [-3.2, 7.4], [-6.0, 6.3]], "color": GOLD, "width": 0.22, "draw": 0.5,
                        "from": "SKIP#2", "to": "@end"}],
               "screen": [{"type": "title", "lines": ["NAIL", "OR SKIP?"], "gold": [0], "y": 300, "size": 120, "from": "call:", "to": "@end"},
                          {"type": "micro", "text": "COMMENT: NAIL / SKIP", "y": 560, "from": "Comment", "to": "@end"},
                          {"type": "logo", "from": "below.", "to": "@end"}]})
    # from_ (python keyword clash) -> from
    for s in sh:
        for o in s["ov3"]:
            if "from_" in o:
                o["from"] = o.pop("from_")
    return sh


def build():
    src = json.load(open(os.path.join(D, "zona23-voice.json")))
    ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw", "gapFill")}
    ep["id"], ep["title"] = EID, "2-3 Zone: five defenders, one gap"
    ep["voiceMix"] = "tactical/zona23/voice.mix.wav"
    ep["branches"] = {"a": "A", "b": "B", "c": "C"}
    words = json.load(open(os.path.join(D, "zona23-voice.words.json")))
    ep["tail"] = round(40.0 - words[-1]["end"], 3)          # 40.00 s = 1200 frames
    ep["env"] = "cinema"
    ep["shots"] = shots()
    ep["pinV2"] = True
    ep["autoSfx"] = False
    ep["keywords"] = ["FIVE", "ONE", "HERE.", "two-three", "flash", "steps up,", "Layup.", "squeezes", "SKIP.", "two jobs:", "late", "THREE", "slowly?", "resets.", "NAIL...", "SKIP?"]
    ep["subtitleY"] = 1350
    ep["subtitleGroups"] = groups(words)
    ep["subtitleBlock"] = True
    ep["music"] = {"src": "tactical/zona23/music.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{EID}.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(words, open(os.path.join(D, f"{EID}.words.json"), "w"), indent=0)
    print(EID, len(ep["shots"]), "shots, tail", ep["tail"])


if __name__ == "__main__":
    build()
