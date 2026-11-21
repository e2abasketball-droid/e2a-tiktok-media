#!/usr/bin/env python3
"""2-3 ZONE V2 — DYNAMIC COVERAGE (owner brief E2A_23_ZONE_V2_DYNAMIC_COVERAGE_PROMPT.md, 2026-11-21 16:09Z).
Built on the V1 scene (same plays A / B / C, same composition Tactical3DV2, same V1 take + ONE pickup):
  python3 tactical/episodes/_splice-zona23-v2.py                       (V1 take + pickup -> voice-v2-raw.wav + words)
  python3 scripts/tactical-voice.py tactical/episodes/zona23-v2-voice.json
  python3 tactical/episodes/_gen-zona23-v2.py                          -> zona-2-3-zone-v2.json
  node scripts/tactical-props.mjs tactical/episodes/zona-2-3-zone-v2.json out/blob/zona-2-3-zone-v2.props.json
Graphics: E2A Dynamic Defensive Coverage (src/t3d/coverage3d.tsx) replaces the V1 zoneGrid. Modes per shot:
FULL (formation), ACTIVE (2-3 responsibilities for the action), CLEAN (catches, finishes, shots).
Repo axes: x = -brief x; orbit yaw 0 = camera on the half-court side, yaw 90 = camera at repo x < 0; pitch from vertical."""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
groups = import_module("_gen-blob").groups
orb = lambda tg, dist, pitch, yaw, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None, spin=False: {"at": at, "rig": rig, **({"ease": ease} if ease else {}), **({"spin": True} if spin else {})}
f = lambda ids, z=1.0, w=0.4, lead=0.0: {"follow": ids, "z": z, "window": w, **({"lead": lead} if lead else {})}
EID = "zona-2-3-zone-v2"
GOLD, CORAL, COOL, WHITE = "#FFC447", "#F06A55", "#A9C8EE", "#FFFFFF"
NAIL = [0.0, 5.8]
GAP = [-0.45, 2.55]          # the space X5 leaves when he steps up (between his spot and the rim, O4's side)


def cov(mode="full", **kw):
    return {"type": "coverage", "scheme": "2-3", "mode": mode, "labelYaw": 90, **kw}


# ---------------------------------------------------------------- cameras (probe stills in /tmp/claude-0/z23v2/)
HK0 = orb([0.0, 4.9, 0.5], 14.5, 50, 30, 42)              # hook f0: elevated, from the side, centre = between the five
HK1 = orb([0.0, 4.6, 0.4], 15.5, 42, 92, 40)              # ... orbit ~60 deg to a semi-top that reads 2 + 3
HK2 = orb([-0.2, 4.0, 0.4], 14.0, 40, 104, 40)            # ... drifting toward the gap on OPEN
TD0 = orb([0.0, 5.5, 0.0], 23.0, 1.5, 90, 40)             # TRUE perpendicular top-down (five areas)
TD1 = orb([0.0, 5.5, 0.0], 22.5, 1.5, 90, 40)
TR0 = orb([0.6, 5.5, 0.0], 22.5, 4, 90, 40)               # top while the ball goes to the wing, slight turn
TR1 = orb([1.0, 5.2, 0.0], 22.0, 10, 78, 40)
FL0 = orb([-0.8, 4.3, 0.6], 15.5, 36, 128, 42)            # READ 01, 3/4 mid height: O5 + X5 + O4 + rim + window
FL1 = orb([-1.3, 3.6, 0.6], 14.0, 40, 118, 42)            # ... no cut on the catch, keeps moving to the step-up
SU1 = orb([-1.7, 2.8, 0.8], 11.5, 48, 108, 44)            # step-up / cut: same 3/4 side as READ 01, closer (no cut)
BL1 = orb([-0.7, 1.9, 1.4], 7.6, 66, 98, 44)              # finish at the rim, same side (no whip)
CL0 = orb([0.0, 4.4, 0.5], 14.5, 36, 125, 40)             # the collapse: orbit around the whole set
CL1 = orb([0.0, 4.4, 0.5], 14.0, 34, 70, 40)
R2 = orb([1.0, 5.6, 0.5], 18.0, 34, 84, 40)               # READ 02: wide, ball side and weak side in frame
SK0 = orb([3.2, 6.2, 1.2], 11.0, 60, 60, 44)              # skip: behind O2's shoulder, O2 big at the release ...
SK1 = orb([-0.6, 5.2, 1.0], 15.5, 46, 88, 42)             # ... rises wide over the whole flight
WS0 = orb([-3.8, 4.2, 0.6], 12.0, 44, 120, 42)            # weak side: X4's distance to O3 (elevated, close)
WS1 = orb([-4.4, 4.2, 0.6], 11.0, 48, 70, 42)
TH0 = orb(f(["O3"], 1.4, 0.4), 6.2, 74, 32, 44)           # THREE (V1 preset): low, clean, shooter + rim
TH1 = orb([-1.6, 2.2, 2.6], 7.4, 80, 32, 44)
SL0 = orb([-1.3, 5.0, 0.0], 25.0, 1.5, 90, 40)            # slow pass: top-down
SL1 = orb([-1.4, 5.0, 0.0], 24.5, 3, 92, 40)
CT0 = orb([0.0, 6.5, 0.4], 19.5, 26, 92, 40)              # CTA: elevated, both options, slight lateral move ...
CT1 = orb([0.0, 6.2, 0.4], 18.5, 32, 76, 40)              # ... and back to the hook frame for the loop


def shots():
    sh = []
    # 01 HOOK — orbit around the formation centre while the five areas appear (top 2, then bottom 3); A runs at 0.5x:
    # O5 flashes, catch on WATCH, X5 steps up and THE GAP OPENS on OPEN (only after X5 has moved: gapReveal trigger)
    sh.append({"id": "01-hook", "name": "HOOK: elevated orbit around the five, areas appear, flash + catch, X5 steps up, the gap opens on OPEN (A 0 -> 1.75)",
               "at": 0, "play": "A", "branch": "a",
               "remap": [[0, 0.0], [1.0, 0.0], ["OPEN.", 1.45], ["Two-0.1", 1.85]],
               "camera": [key(0, HK0), key("WATCH", HK1, "inOut", spin=True), key("Two-0.1", HK2, "out")],
               "ov3": [cov("full", reveal=0.2, **{"from": 0, "to": "WATCH", "fin": 0.01, "fout": 0.3}),
                       cov("active", active=["X5"], dim=0.5, **{"from": "WATCH-0.3", "to": "Two-0.1", "fin": 0.3}),
                       {"type": "gapReveal", "at": GAP, "r": 1.05, "trigger": {"id": "X5", "dist": 0.3}, "arrowFrom": "O4", "arrowTo": [-1.35, 1.9], "from": "WATCH", "to": "Two-0.1"}],
               "screen": [{"type": "flash", "color": "#FFE9C8", "strength": 0.16, "from": 0, "to": 0.2},
                          {"type": "stamp", "text": "THE 2-3 ZONE", "tone": "white", "y": 300, "instant": True, "from": 0, "to": "WATCH"},
                          {"type": "micro", "text": "ILLUSTRATIVE COVERAGE", "y": 300, "from": "WATCH", "to": "Two-0.1"}]})
    # 02 TOP 2 / BOTTOM 3 — true top-down held ~4.5 s: X1/X2 active, then X3/X4/X5, then the whole structure
    sh.append({"id": "02-shape", "name": "TOP 2 / BOTTOM 3: perpendicular top-down, ACTIVE X1 X2 -> X3 X4 X5 -> FULL with labels (A 0)",
               "at": "Two-0.1", "play": "A", "branch": "a",
               "remap": [[0, 0.0], ["These-0.1", 0.0]],
               "camera": [key(0, TD0), key("These-0.1", TD1, "linear")],
               "ov3": [cov("active", active=["X1", "X2"], labels="active", dim=0.4, **{"from": 0, "to": "Three", "fin": 0.2, "fout": 0.2}),
                       cov("active", active=["X3", "X4", "X5"], labels="active", dim=0.4, **{"from": "Three-0.1", "to": "That's", "fin": 0.2, "fout": 0.25}),
                       cov("full", labels="all", **{"from": "That's-0.15", "to": "These-0.1", "fin": 0.25})]})
    # 03 MOVE WITH THE BALL — O1 -> O2: the areas slide AND deform with the real defenders; X1's previous spot as a ghost
    sh.append({"id": "03-move", "name": "THE AREAS MOVE: top, O1 -> O2 to the wing, areas slide + deform, ghost of X1 (B 0 -> 1.30)",
               "at": "These-0.1", "play": "B", "branch": "b",
               "remap": [[0, 0.0], ["boxes", 0.15], ["ball.>", 1.30], ["First,-0.12", 1.30]],
               "camera": [key(0, TR0), key("First,-0.12", TR1, "inOut")],
               "ov3": [cov("full", **{"from": 0, "to": "First,-0.12", "fin": 0.01}),
                       {"type": "passLane", "src": "O1", "dst": "O2", "travel": 0.6, "dstAt": 0.9333, "color": WHITE, "from": "boxes-0.2", "to": "with"},
                       {"type": "covGhost", "id": "X1", "at": 0.0, "from": "with", "to": "First,-0.12"}]})
    # 04 READ 01 FLASH — one continuous 3/4 mid-height camera from the flash through the catch to the step-up (no cut on the catch)
    sh.append({"id": "04-flash", "name": "READ 01: O5 flashes to the nail, X1/X2 pinch, catch, X5 steps up: the gap opens behind him (A 0 -> 1.40)",
               "at": "First,-0.12", "play": "A", "branch": "a",
               "remap": [[0, 0.0], ["flash", 0.05], ["line.", 1.033], ["steps", 1.40]],
               "camera": [key(0, FL0), key("line.", FL1, "inOut"), key("steps", FL1, "linear")],
               "ov3": [{"type": "route", "player": "O5", "t0": 0.0, "t1": 1.0, "consume": True, "color": GOLD, "width": 0.1, "from": 0.1, "to": "line.>"},
                       cov("active", active=["X1", "X2", "X5"], dim=0.45, **{"from": 0, "to": "steps", "fin": 0.01}),
                       {"type": "gapReveal", "at": GAP, "r": 1.05, "trigger": {"id": "X5", "dist": 0.3}, "from": "center", "to": "steps"}],
               "screen": [{"type": "hud", "tag": "READ 01", "text": "ATTACK THE NAIL", "y": 300, "from": 0.05, "to": "line."}]})
    # 05 CUT + LAYUP — X5 committed: pass lane to the cutter while the window exists, then CLEAN for the catch and finish
    sh.append({"id": "05-layup", "name": "IF THE CENTER STEPS UP: gap + lane to O4, O5 -> O4, CLEAN catch + layup, +2 (A 1.40 -> 3.45)",
               "at": "steps", "play": "A", "branch": "a",
               "remap": [[0, 1.40], ["Layup.+0.12", 3.2], ["But-0.1", 3.45]],
               "camera": [key(0, FL1), key("behind.", SU1, "inOut"), key("Layup.", BL1, "inOut"), key("But-0.1", BL1, "linear")],
               "ov3": [cov("active", active=["X5", "X4"], vulnerable=["X5"], dim=0.4, **{"from": 0, "to": "behind.", "fin": 0.01, "fout": 0.35}),
                       {"type": "gapReveal", "at": GAP, "r": 1.05, "trigger": {"id": "X5", "dist": 0.3}, "arrowFrom": "O4", "arrowTo": [-1.35, 1.9], "from": 0, "to": "slips"},
                       {"type": "passLane", "src": "O5", "dst": "O4", "travel": 0.47, "dstAt": 2.4, "color": GOLD, "from": "cutter", "to": "behind.+0.2"},
                       {"type": "ballTrail", "len": 0.25, "from": "behind.", "to": "Layup.+0.15"},
                       {"type": "glow", "hoop": True, "r": 1.1, "color": GOLD, "strength": 0.6, "from": "Layup.+0.12", "to": "But-0.1"}],
               "screen": [{"type": "flash", "color": "#FFE3A3", "strength": 0.2, "from": "Layup.+0.12", "to": "Layup.+0.4"},
                          {"type": "stamp", "text": "+2", "tone": "gold", "y": 300, "from": "Layup.+0.15", "to": "But-0.1"}]})
    # 06 REHOOK — the collapse, replayed: the five converge on the nail catch (real positions), hull now vs before
    sh.append({"id": "06-collapse", "name": "BUT WHAT HAPPENS WHEN THE DEFENSE COLLAPSES?: orbit, A replay 0.55 -> 1.70, areas compress with the real defenders, hull vs ghost hull",
               "at": "But-0.1", "play": "A", "branch": "a",
               "remap": [[0, 0.55], ["collapses?", 1.45], ["Now-0.1", 1.70]],
               "camera": [key(0, CL0), key("Now-0.1", CL1, "inOut")],
               "ov3": [cov("active", active=["X1", "X2", "X5"], dim=0.5, compress=0.25, **{"from": 0, "to": "Now-0.1", "fin": 0.2}),
                       {"type": "covHull", "base": 0.0, "from": "happens", "to": "Now-0.1"}],
               "screen": [{"type": "hud", "tag": "REPLAY", "text": "THE ZONE COLLAPSES", "y": 300, "from": 0.05, "to": "Now-0.1"}]})
    # 07 READ 02 — wide: where the ball comes from and where it goes; ball-side areas active
    sh.append({"id": "07-read2", "name": "READ 02: wide, O1 -> O2, the zone shifts to the ball (B 0 -> 0.95)",
               "at": "Now-0.1", "play": "B", "branch": "b",
               "remap": [[0, 0.0], ["pull", 0.25], ["wing...>", 0.93], ["and-0.06", 0.95]],
               "camera": [key(0, R2), key("and-0.06", SK0, "inOut")],
               "ov3": [cov("active", active=["X1", "X3"], dim=0.55, **{"from": 0, "to": "and-0.06", "fin": 0.01}),
                       {"type": "passLane", "src": "O1", "dst": "O2", "travel": 0.6, "dstAt": 0.9333, "color": WHITE, "from": "pull-0.1", "to": "wing...>"}],
               "screen": [{"type": "hud", "tag": "READ 02", "text": "BALL TO THE WING", "y": 300, "from": 0.05, "to": "wing..."}]})
    # 08 SKIP — behind O2 (big at the release), camera rises over the flight; X4's real closeout route appears with the release
    sh.append({"id": "08-skip", "name": "SKIP: behind O2, release on SKIP, rises wide over the flight; areas follow the defenders; X4 closeout route (B 0.95 -> 1.75)",
               "at": "and-0.06", "play": "B", "branch": "b",
               "remap": [[0, 0.95], ["SKIP.", 1.467], ["weak-side-0.12", 1.75]],
               "camera": [key(0, SK0), key("throw>", SK0, "linear"), key("weak-side-0.12", SK1, "inOut")],
               "ov3": [cov("full", **{"from": 0, "to": "weak-side-0.12", "fin": 0.01}),
                       {"type": "ballTrail", "len": 0.35, "from": "SKIP.", "to": "weak-side-0.12"},
                       {"type": "closeout", "id": "X4", "t0": 1.467, "t1": 2.93, "label": False, "from": "SKIP.+0.15", "to": "weak-side-0.12"}]})
    # 09 TWO JOBS — freeze with the ball in the air: RIM? or CLOSE?; resume: real closeout, distance, shot window, LATE
    sh.append({"id": "09-jobs", "name": "TWO JOBS: weak side, freeze B 1.75 (RIM? / CLOSE?), resume: X4 real route + distance, O3 catch, shot window, LATE at the release",
               "at": "weak-side-0.12", "play": "B", "branch": "b",
               "remap": [[0, 1.75], ["shooter.>", 1.75], ["step.>", 2.93]],
               "camera": [key(0, WS0), key("shooter.>", WS1, "inOut", spin=True), key("step.>", TH0, "inOut")],
               "ov3": [cov("active", active=["X4"], dim=0.4, **{"from": 0, "to": "late-0.3", "fin": 0.01, "fout": 0.3}),
                       {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": [[-4.4, 2.75], [-3.3, 2.2], [-2.1, 1.85], [-1.2, 1.7]], "color": COOL, "width": 0.09, "draw": 0.35,
                        "label": "RIM?", "labelYaw": 95, "labelOffset": [-0.3, 0.7], "labelSize": 0.55, "from": "guard", "to": "late-0.2"},
                       {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": [[-4.5, 2.95], [-4.9, 3.7], [-5.3, 4.4], [-5.6, 4.9]], "color": GOLD, "width": 0.09, "draw": 0.35,
                        "label": "CLOSE?", "labelYaw": 95, "labelOffset": [0.7, 0.3], "labelSize": 0.55, "from": "close", "to": "late-0.2"},
                       {"type": "closeout", "id": "X4", "t0": 1.467, "t1": 2.93, "late": 2.93, "from": "late-0.3", "to": "step.>"},
                       {"type": "shotWindow", "shooter": "O3", "t0": 2.5667, "t1": 2.93, "defender": "X4", "from": "late", "to": "step.>"}],
               "screen": [{"type": "freeze", "from": 0.05, "to": "shooter.>"}]})
    # 10 THREE — CLEAN: close on the shooter, catch / set / jump / release / flight / net
    sh.append({"id": "10-three", "name": "THREE POINTS: CLEAN, close on O3 + rim, net, +3 (B 2.93 -> 4.30)",
               "at": "step.>", "play": "B", "branch": "b",
               "remap": [[0, 2.93], ["points.>+0.1", 4.10], ["But#2-0.1", 4.30]],
               "camera": [key(0, TH0), key("points.>", TH1, "inOut"), key("But#2-0.1", TH1, "linear")],
               "ov3": [{"type": "ballTrail", "len": 0.3, "from": 0, "to": "points.>"},
                       {"type": "glow", "hoop": True, "r": 1.1, "color": GOLD, "strength": 0.6, "from": "points.", "to": "But#2-0.1"}],
               "screen": [{"type": "flash", "color": "#FFE3A3", "strength": 0.2, "from": "points.", "to": "points.+0.3"},
                          {"type": "stamp", "text": "+3", "tone": "gold", "y": 300, "from": "points.", "to": "But#2-0.1"}]})
    # 11 TOO SLOW — same set, O2 holds: X2 starts coral at the skip and turns back to normal as he really gets to the wing;
    # X4 resets to the short corner (V2 tactical audit: no double team on O3, see _gen-zone23.py C)
    sh.append({"id": "11-slow", "name": "TOO SLOW: top-down, O2 holds, late skip; X2 recovers to the wing (coral -> normal from his real distance), X4 resets to the short corner, O3 contested (C 1.10 -> 3.45)",
               "at": "But#2-0.1", "play": "C", "branch": "c",
               "remap": [[0, 1.10], ["resets.", 3.30], ["Your-0.1", 3.45]],
               "camera": [key(0, SL0), key("Your-0.1", SL1, "linear")],
               "ov3": [cov("active", active=["X2", "X4"], recover={"ids": ["X2"], "t0": 2.2, "t1": 3.3}, dim=0.5, **{"from": 0, "to": "Your-0.1", "fin": 0.01}),
                       {"type": "ring", "player": "O3", "color": COOL, "size": 0.7, "from": "resets.-0.3", "to": "Your-0.1"}],
               "screen": [{"type": "hud", "tag": "TOO SLOW", "text": "THE ZONE HAS TIME", "y": 300, "from": "pass", "to": "Your-0.1"}]})
    # 12 YOUR CALL — the two decisions from the point guard's seat: NAIL (gold, into the gap) or SKIP (cool, wing to wing);
    # ends on the hook's frame-0 camera and state (A 0) for the loop
    sh.append({"id": "12-cta", "name": "YOUR CALL: NAIL route vs SKIP arc from the point guard's seat, title, logo; camera returns to the hook frame (A 0)",
               "at": "Your-0.1", "play": "A", "branch": "a",
               "remap": [[0, 0.0], ["@end", 0.0]],
               "camera": [key(0, CT0), key("below.", CT1, "inOut"), key("@end-0.45", HK0, "inOut"), key("@end", HK0, "linear")],
               "ov3": [cov("full", dim=0.5, **{"from": 0, "to": "@end-0.4", "fout": 0.35}),
                       {"type": "route", "player": "O1", "t0": 0, "t1": 0, "pts": [[0.0, 8.5], [0.15, 7.4], [0.25, 6.4], [0.3, 5.9]], "color": GOLD, "width": 0.16, "draw": 0.45,
                        "label": "NAIL", "labelYaw": 92, "labelOffset": [1.2, -0.2], "labelSize": 0.7, "from": "NAIL...", "to": "@end-0.4"},
                       {"type": "route", "player": "O2", "t0": 0, "t1": 0, "pts": [[6.0, 6.3], [3.2, 7.4], [0.0, 7.8], [-3.2, 7.4], [-6.0, 6.3]], "color": COOL, "width": 0.16, "draw": 0.5,
                        "label": "SKIP", "labelYaw": 92, "labelOffset": [0.9, 0.0], "labelSize": 0.7, "from": "SKIP#2", "to": "@end-0.4"}],
               "screen": [{"type": "title", "lines": ["NAIL", "OR SKIP?"], "gold": [0], "y": 300, "size": 120, "from": "call:", "to": "@end"},
                          {"type": "micro", "text": "YOU HAVE THE BALL", "y": 560, "from": "Your", "to": "NAIL..."},
                          {"type": "micro", "text": "COMMENT: NAIL / SKIP", "y": 560, "from": "Comment", "to": "@end"},
                          {"type": "logo", "from": "below.", "to": "@end"}]})
    return sh


def build():
    src = json.load(open(os.path.join(D, "zona23-v2-voice.json")))
    ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw", "gapFill")}
    ep["id"], ep["title"] = EID, "2-3 Zone V2: dynamic defensive coverage"
    ep["voiceMix"] = "tactical/zona23/voice-v2.mix.wav"
    ep["branches"] = {"a": "A", "b": "B", "c": "C"}
    words = json.load(open(os.path.join(D, "zona23-v2-voice.words.json")))
    ep["tail"] = round(40.0 - words[-1]["end"], 3)          # 40.00 s = 1200 frames
    ep["env"] = "cinema"
    ep["shots"] = shots()
    ep["pinV2"] = True
    ep["autoSfx"] = False
    ep["keywords"] = ["FIVE", "GAP...", "OPEN.", "two-three", "flash", "steps", "Layup.", "collapses?", "SKIP.", "jobs:", "late", "THREE", "slowly?", "resets.", "NAIL...", "SKIP?"]
    ep["subtitleY"] = 1350
    # action shots: captions lower, off the ball, hands, feet and the gap (owner V2 sec. 15)
    # finish at the rim: the action fills the lower two thirds, the top is the stands -> caption above it (inside the
    # safe area, under the +2 stamp); elsewhere the default 1350, the lowest position the safe area allows (qc-bounds)
    ep["subtitleYAt"] = [["Layup.-0.3", "But-0.1", 520]]
    ep["subtitleGroups"] = groups(words)
    ep["subtitleBlock"] = True
    ep["music"] = {"src": "tactical/zona23/music-v2.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{EID}.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(words, open(os.path.join(D, f"{EID}.words.json"), "w"), indent=0)
    print(EID, len(ep["shots"]), "shots, tail", ep["tail"])


if __name__ == "__main__":
    build()
