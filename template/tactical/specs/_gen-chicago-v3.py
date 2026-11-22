#!/usr/bin/env python3
"""CHICAGO ACTION V3 (owner master brief 432aece7-E2A_CHICAGO_ACTION_V3_MASTER_NO_ELEVENLABS.md sec. 4 + 15 phase 2,
2026-11-22): ONE shared pin-down -> dribble hand-off, TWO defensive reads with two DIFFERENT payoffs.
  TRAIL -> DRIVE   chicago-v3-trail-drive   X2 chases over the pin-down and over the hand-off (round O1's top side): O2
                   turns the corner, attacks the lane on two dribbles, gathers, two legal steps and a right-hand layup
                   (make, through the net). X4 leaves the short roller late and contests from the help side (no contact).
  UNDER -> THREE   chicago-v3-under-three   X2 goes under the pin-down and under the hand-off: O2 stops behind the arc
                   off the hand-off (1-2 stop), three (make). Tracks of the V2 B read (validated), realism 3.
Shared fork: every player and the ball are IDENTICAL in both branches until FORK = S026 (0.867 s): X2 has read the
screen. After it only X2 differs until the hand-off contact (S072); then the offence answers the defence.
Built on tactical/specs/_gen-chicago-v2.py (same court axes, same shared set, same pin-down, same hand-off).
  python3 tactical/specs/_gen-chicago-v3.py   (writes tactical/specs/chicago-v3-*.spec.json + tactical/plays/)
Semantic roles (brief sec. 4, from the actual tracks): O1 = ball-handler (DHO giver), O2 = cutter / receiver /
decision-maker, O4 = pin-down screener, O3 / O5 = weak-side spacers, X2 = the cutter's defender (the read), X4 = the
screener's defender (late help in TRAIL), X1 / X3 / X5 = assignments, help line and recovery."""
import json, math, os, sys
from importlib import util
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
_s = util.spec_from_file_location("v2", os.path.join(D, "_gen-chicago-v2.py"))
v2 = util.module_from_spec(_s)
_out, sys.stdout = sys.stdout, open(os.devnull, "w")
_s.loader.exec_module(v2)
sys.stdout = _out
S, run, runv, cat, face, st, START = v2.S, v2.run, v2.runv, v2.cat, v2.face, v2.st, v2.START
POCKET = 5                     # ball protected in the pocket after the transfer, then the first attack dribble
FORK = 26                      # X2's read: until here both branches are the same frame-for-frame
F_OFFER, F_HO, F_HO1 = v2.F_OFFER, v2.F_HO, v2.F_HO1
HO, O1HO, PIN = v2.HO, v2.O1HO, v2.PIN

# ---------------------------------------------------------------- TRAIL -> DRIVE
# O2 after the hand-off: tight turn round O1's top side, downhill to the right block, gather at G, two steps, take-off at
# TK (1.05 m from the rim centre, right side of the rim), floats under the rim and lands at LAND.
TK = (-0.62, 2.42)
LAND = (-0.46, 1.86)
DRV_PTS = v2.CUTPTS + [(-2.78, 8.74), (-2.12, 8.5), (-1.45, 7.85), (-1.05, 6.5), (-0.88, 5.05), (-0.72, 3.65), TK, LAND]
DRV_V = v2.CUTV + [3.2, 3.6, 4.4, 5.0, 5.0, 4.3, 3.4, 0.0]
O2D, O2D_F = runv(DRV_PTS, DRV_V, 6, F_HO)
TK_F = int(round(O2D_F[-2]))
GATHER_F = TK_F - 13           # ball picked up: ~0.43 s, two steps, take-off
LAY_T0 = S(TK_F + 2)           # release on the way up
LAY_T1 = S(TK_F + 14)          # ball through the rim
DUR_D = TK_F + 62
# X2 trails: over the pin-down (V2 A route) and over the hand-off round O1's top, then chases O2 down the lane, a step
# and a half behind; never through a body (test-play overlaps)
X2D, X2D_F = runv([START["X2"], (-4.95, 3.5), (-5.2, 4.4), (-5.0, 5.6), (-4.55, 6.9), (-4.1, 8.1), (-3.6, 9.0), (-2.65, 9.2),
                   (-1.95, 8.75), (-1.5, 7.6), (-1.28, 6.1), (-1.18, 4.7), (-1.12, 3.75)],
                  [0.0, 2.6, 4.3, 5.0, 4.6, 3.9, 3.4, 3.4, 4.2, 5.2, 5.4, 4.4, 0.0], 2, 51)
# X4 (on the short roller O4): sees the drive late, steps across and contests the layup from the help side
X4_HELP0 = int(round(TK_F - 26))

TRAIL = {
    "O2": cat(v2.COMMON["O2"], {k: v for k, v in v2.O2B.items() if k <= F_HO}, {k: v for k, v in O2D.items() if k > F_HO}, {DUR_D: LAND}),
    "X2": cat(X2D, {DUR_D: (-1.12, 3.75)}),
    "O1": cat(v2.COMMON["O1"], {84: O1HO}, run(84, 124, [O1HO, (-2.9, 6.3), (-2.6, 4.4)]), {DUR_D: (-2.6, 4.4)}),
    "X1": cat(v2.COMMON["X1"], run(74, 90, [(-2.25, 7.42), (-2.15, 6.95)]), run(90, 126, [(-2.15, 6.95), (-2.2, 5.9), (-2.05, 4.55)]), {DUR_D: (-2.05, 4.55)}),
    "O4": cat(v2.COMMON["O4"], run(66, 100, [PIN, (-3.6, 3.6), (-2.75, 3.25)]), {DUR_D: (-2.75, 3.25)}),
    "X4": cat(v2.COMMON["X4"], run(63, 100, [(-3.78, 4.48), (-2.98, 4.14), (-2.12, 3.6)]), {X4_HELP0: (-2.12, 3.6)},
              run(X4_HELP0, TK_F - 6, [(-2.12, 3.6), (-1.72, 3.05), (-1.55, 2.6)]), {DUR_D: (-1.55, 2.6)}),
    "X3": cat(v2.COMMON["X3"], run(84, 112, [(4.0, 2.55), (3.0, 2.6)]), {DUR_D: (3.0, 2.6)}),
    "X5": cat(v2.COMMON["X5"], run(84, 110, [(3.55, 6.0), (2.4, 5.4)]), {DUR_D: (2.4, 5.4)}),
    "O3": cat(v2.COMMON["O3"], run(86, 110, [(6.2, 1.4), (6.25, 1.75)]), {DUR_D: (6.25, 1.75)}),
    "O5": cat(v2.COMMON["O5"], {DUR_D: (5.75, 7.75)}),
}


def fork_x2(x2):
    """X2 holds his start spot until FORK in both branches (the shared frame of the choice)"""
    out = {k: v for k, v in x2.items() if k > FORK}
    out[0] = START["X2"]
    out[FORK] = START["X2"]
    return out


TRAIL["X2"] = fork_x2(TRAIL["X2"])
# UNDER -> THREE: the V2 B read (X2 starts at S026 there already: 0.85 s), same shared set
UNDER = {k: dict(v) for k, v in v2.B.items()}
UNDER["X2"] = fork_x2(v2.B["X2"])
DUR = {"trail": DUR_D, "under": v2.DUR["b"]}


def tracks(br):
    out = {}
    for pid, p0 in START.items():
        an = {0: p0}
        an.update(br[pid])
        out[pid] = v2.track(an, S(DUR["trail" if br is TRAIL else "under"]))
    return out


def ball_trail():
    ev = v2.ball("a")[:3]
    ev += [{"type": "hold", "player": "O2", "from": S(F_HO1), "to": S(F_HO1 + POCKET), "pocket": True},
           {"type": "hold", "player": "O2", "from": S(F_HO1 + POCKET), "to": S(GATHER_F), "dribble": True, "hand": 1},
           {"type": "hold", "player": "O2", "from": S(GATHER_F), "to": LAY_T0},
           {"type": "layup", "player": "O2", "t0": LAY_T0, "t1": LAY_T1, "make": True}]
    return ev


def actions_trail():
    d = DUR_D
    act = v2.actions("a")
    act["O2"] = [face("O4", 0, 16), {"type": "catchReady", "from": S(F_HO - 9), "to": S(F_HO1), "face": "O1"},
                 {"type": "celebrate", "from": S(TK_F + 36), "to": S(TK_F + 56)}]
    act["X2"] = [st("O2", 0, 16)]
    act["X4"] = [st("O4", 0, X4_HELP0), st("O2", X4_HELP0, TK_F + 2), {"type": "contest", "from": S(TK_F + 2), "to": S(TK_F + 17)}]
    act["X1"] = [st("O1", 0, d)]
    act["O4"] = [face("O2", 0, 24), {"type": "screen", "from": S(30), "to": S(66), "face": v2.PIN_FACE}, face("ball", 70, d)]
    return act


def branch_meta(read, result, payoff):
    return {"group": "chicago-v3", "read": read, "result": result, "fork": S(FORK), "shared": "chicago-v3-shared",
            "sharedUntil": S(FORK), "offenceSharedUntil": S(F_HO), "payoff": payoff}


def spec(kind):
    if kind == "trail":
        s = {"id": "chicago-v3-trail-drive", "title": "Chicago action V3 - TRAIL -> DRIVE: X2 trails, O2 turns the corner, two dribbles, layup",
             "duration": S(DUR_D), "tracks": tracks(TRAIL), "ball": ball_trail(), "actions": actions_trail()}
        s["marks"] = {"start": 0, "fork": S(FORK), "pindown": S(30), "cut": S(16), "pass_screen": S(41), "offer": S(F_OFFER), "handoff": S(F_HO),
                      "transfer": S(F_HO1), "corner": S(F_HO1 + 10), "gather": S(GATHER_F), "takeoff": S(TK_F), "layup": LAY_T0, "make": LAY_T1, "end": S(DUR_D)}
        s["claims"] = [
            {"type": "near", "a": "O4", "b": "X2", "at": "pass_screen", "max": 1.5, "says": "First, the pin-down."},
            {"type": "far", "a": "X2", "b": "O2", "at": "handoff", "min": 1.3, "says": "his defender has to chase (trails over the top)"},
            {"type": "near", "a": "O1", "b": "O2", "at": "handoff", "max": 0.95, "says": "straight into the handoff (hand to hand)"},
            {"type": "far", "a": "X2", "b": "O2", "at": "gather", "min": 1.3, "says": "Trail him, and he turns the corner before you recover."},
            {"type": "far", "a": "X4", "b": "O2", "at": "layup", "min": 0.8, "says": "late help contest from the weak side, no contact"},
            {"type": "order", "marks": ["fork", "pindown", "pass_screen", "offer", "handoff", "transfer", "corner", "gather", "takeoff", "layup", "make"], "says": "pin-down, hand-off, drive, layup"}]
        s["branch"] = branch_meta("TRAIL", "drive_finish", {"type": "layup", "make": True, "t": LAY_T1})
    else:
        b = v2.spec("b")
        s = {"id": "chicago-v3-under-three", "title": "Chicago action V3 - UNDER -> THREE: X2 goes under, O2 stops behind the arc, three",
             "duration": b["duration"], "tracks": tracks(UNDER), "ball": b["ball"], "actions": b["actions"], "marks": {**b["marks"], "fork": S(FORK)},
             "claims": b["claims"]}
        s["branch"] = branch_meta("UNDER", "three_point_shot", {"type": "shot", "three": True, "make": True, "t": b["marks"]["make"]})
    base = v2.spec("b")
    s.update({"concept": "chicago-pin-down-dho", "source": base["source"], "squareUp": True, "catchV2": 2, "handBallClear": True, "realism": 3,
              "players": base["players"], "screens": [], "sclock": {**base["sclock"], "v3": "branches share the set until fork (brief V3 sec. 4)"}})
    s["players"] = [dict(p) for p in s["players"]]
    for p in s["players"]:
        if p["id"] == "O2":
            p["role"] = "Cutter / receiver: low right wing, off the pin-down, takes the hand-off (TRAIL: drive + layup / UNDER: three)"
        if p["id"] == "X2":
            p["role"] = "On the cutter: the read - TRAILS (drive) / goes UNDER (three)"
        if p["id"] == "X4" and kind == "trail":
            p["role"] = "On the screener: stays with the short roll, late help contest on the layup (no contact)"
    return s


if __name__ == "__main__":
    print("O2 drive frames", O2D_F, "take-off", TK_F, "gather", GATHER_F, "layup", LAY_T0, LAY_T1, "dur", DUR_D)
    print("X2 trail frames", X2D_F)
    print("take-off to rim", round(math.hypot(TK[0], TK[1] - 1.575), 2), "m")
    for k in ("trail", "under"):
        s = spec(k)
        json.dump(s, open(os.path.join(D, f"{s['id']}.spec.json"), "w"), indent=1)
        json.dump(s, open(os.path.join(T, "tactical", "plays", f"{s['id']}.json"), "w"), indent=1)
        print("built", s["id"], json.dumps(s["marks"]))
