#!/usr/bin/env python3
"""DOUBLE DRAG EN TRANSICION (owner brief E2A-prompt-Claude-Double-Drag-en-transicion.md, 2026-11-20).
Two staggered ball screens ON X1 during the push (O5 first, then O4); O5 rolls, O4 pops to the high slot; the weak-side
corner defender X3 decides.
  A ddtr-a-roll  X3 stays connected to O3 -> O1 leads O5 in stride (S084 -> S095), left-hand layup (release ~S113).
  B ddtr-b-skip  X3 steps in to tag the roll from S066 -> O1 skips it over the top to O3 (S086 -> S108), corner three.

The brief's anchor table (sec. 5) is used AS DATA: every S-clock anchor becomes a waypoint at S/30 s. Axis mapping:
the brief uses x > 0 = offence's RIGHT (from half court looking at the basket); the repo uses x > 0 = LEFT of the house
camera = offence's LEFT, so repo x = -brief x (same mirror as Blind Pig V2). y, z unchanged (y = 0 baseline, rim at
(0, 1.575, 3.05)).
Changes to the anchors (documented, sec. 5 allows them):
  - O5 holds ONE spot S032-S048 (brief S036 (-1.12, 8.10) / S050 (-1.12, 8.00) -> (-1.12, 8.05) both ends: a legal,
    stationary screen, FIBA 33.7); O4 holds ONE spot S053-S070 ((0.55, 7.52)/(0.55, 7.44) -> (0.55, 7.48)).
  - extra anchors only where the brief leaves a gap (listed in ADJUST), never moving an anchor's time.
  python3 tactical/specs/_gen-ddrag-tr.py   (writes tactical/specs/ddtr-{a-roll,b-skip}.spec.json + plays)"""
import json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
S = lambda n: round(n / 30, 4)
M = lambda p: [round(-p[0], 3), p[1]]   # brief axes -> repo axes
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = ("E2A didactic construction (owner brief 'Double Drag en transicion', S-clock anchors S000-S158) on: FIBA Europe "
       "Coaching Certificate terminology (Drag / Double Drag, on-ball screens); NBA.com Schuhmann 'Two Screens for Walker'; "
       "Hooper University 'Golden State Warriors Split Action' (first screener rolls, second pops); WABC level 1 (help and "
       "recover); FIBA 2026 arts. 2, 14, 16, 24, 25, 33.7")

PLAYERS = [P("O1", "O", "Point guard: pushes the ball, uses both drags"),
           P("O2", "O", "Strong-side wide runner: right corner (offence's right)"),
           P("O3", "O", "Weak-side corner shooter (offence's left)"),
           P("O4", "O", "Second screener: pops to the high slot"),
           P("O5", "O", "First screener: rolls to the rim"),
           P("X1", "X", "On the ball: chases over both screens", "O1"),
           P("X2", "X", "On O2", "O2"),
           P("X3", "X", "Weak-side corner defender: stays (A) / tags the roll (B) = THE CHOICE", "O3"),
           P("X4", "X", "On the popper: brief containment of the guard", "O4"),
           P("X5", "X", "On the roller: steps up, loses the rim side", "O5")]

# ---- brief sec. 5 anchors (brief axes), S -> (x, y)
OFF = {
 "O1": {0: (-2.40, 13.40), 18: (-2.25, 10.75), 36: (-1.80, 8.87), 50: (-0.22, 8.98), 65: (1.25, 8.06), 75: (2.45, 7.36), 84: (3.17, 6.52), 94: (3.56, 5.98), 105: (3.76, 5.60), 120: (3.86, 5.45), 138: (3.91, 5.42)},
 "O2": {0: (5.70, 8.40), 18: (5.94, 6.20), 36: (6.35, 3.90), 50: (6.62, 2.30), 65: (6.86, 1.43), 75: (6.86, 1.38), 138: (6.87, 1.45)},
 "O3": {0: (-5.85, 8.10), 18: (-6.03, 6.10), 36: (-6.44, 4.20), 50: (-6.75, 2.97), 65: (-7.00, 2.33), 75: (-6.99, 2.34), 138: (-6.95, 2.35)},
 "O4": {0: (-0.40, 13.76), 18: (0.25, 11.46), 36: (0.57, 9.15), 53: (0.55, 7.48), 67: (0.55, 7.48), 84: (-0.38, 8.84), 94: (-1.11, 9.34), 105: (-1.32, 9.48), 120: (-1.36, 9.49), 138: (-1.34, 9.51)},
 "O5": {0: (-0.28, 12.60), 18: (-0.91, 9.55), 32: (-1.12, 8.05), 48: (-1.12, 8.05), 65: (-0.95, 6.38), 75: (-0.93, 5.22), 84: (-0.89, 4.15), 94: (-0.58, 3.03), 105: (-0.37, 2.18), 120: (-0.62, 1.83), 138: (-0.95, 1.78)},
}
DEF = {
 "X1": {0: (-2.15, 11.85), 18: (-2.19, 9.80), 36: (-2.10, 8.33), 50: (-1.24, 9.40), 65: (0.48, 8.83), 75: (1.52, 8.67), 84: (2.30, 7.57), 94: (3.02, 6.68), 105: (3.30, 6.30), 120: (3.52, 6.20), 138: (3.64, 6.14)},
 "X2": {0: (4.88, 6.58), 18: (5.08, 4.84), 36: (5.30, 3.60), 50: (5.75, 2.80), 65: (5.65, 2.15), 75: (5.55, 2.17), 84: (5.50, 2.24), 94: (5.39, 2.24), 105: (5.15, 2.29), 120: (5.02, 2.35), 138: (4.96, 2.39)},
 "X3": {0: (-5.32, 6.93), 18: (-5.32, 4.96), 36: (-5.56, 3.77), 50: (-5.56, 3.08), 65: (-5.43, 2.86), 66: (-5.43, 2.86), 75: (-5.37, 2.90), 84: (-5.42, 2.85), 94: (-5.44, 2.85), 105: (-5.42, 2.86), 120: (-5.42, 2.85), 138: (-5.41, 2.84)},
 "X4": {0: (1.85, 9.20), 18: (1.51, 8.68), 36: (1.55, 7.94), 50: (1.38, 6.97), 65: (1.94, 7.12), 75: (3.30, 6.65), 84: (3.85, 6.35), 94: (3.93, 7.10), 105: (2.82, 7.88), 120: (1.34, 8.53), 138: (-0.19, 9.02)},
 "X5": {0: (-0.65, 9.92), 18: (0.10, 8.89), 36: (-0.15, 7.06), 50: (0.02, 7.05), 65: (-0.02, 6.89), 75: (-0.05, 6.02), 84: (-0.04, 5.28), 94: (-0.03, 4.14), 105: (0.03, 3.25), 120: (0.20, 2.64), 138: (0.48, 2.62)},
}
# B (sec. 5 "Cambio de B"): shared until S065
B_X3 = {66: (-5.43, 2.86), 75: (-4.84, 2.77), 84: (-3.83, 2.69), 94: (-2.55, 2.71), 101: (-2.09, 2.78), 108: (-2.40, 2.73), 123: (-4.06, 2.58), 142: (-5.49, 2.53), 162: (-5.86, 2.53)}
B_O5 = {75: (-0.93, 5.22), 84: (-0.89, 4.15), 94: (-0.58, 3.03), 101: (-0.32, 2.58), 108: (-0.20, 2.28), 123: (0.39, 2.21), 138: (1.00, 2.25), 156: (1.08, 2.31)}
B_O3 = {75: (-6.99, 2.34), 156: (-6.91, 2.40)}
B_X5 = {105: (0.03, 3.13), 120: (0.85, 2.95), 138: (1.45, 2.95), 156: (1.55, 2.90)}   # B: X5 trails O5 (brief gives no B column)
ADJUST = [   # anchors moved or added (reported in the tactical sheet); times never moved unless said
 "O5: screen hold S032-S048 (brief: both feet set 'cerca de S031'; arriving at S031 from the flying start was a 24 m/s2 stop)",
 "O1 (B): eyes/shoulders to O3 from S076 (not S070): turning to the far corner while still driving right twisted the dribbling arm (mesh hand 42 mm off the ball)",
 "O1 (B): pick-up S077 (A S080): the overhead skip needs the ball loaded above the head before S086 (0.12 m hand gap when the pick-up and the load overlapped)",
 "O3 (B): shot S127 -> S157 (brief window S121-S127; with the catch at S114 a S124 shot left a 0.17 s gather and a 0.105 m hand gap)",
 "O4: screen hold S053-S067 (brief 'aprox. S053-S070'; X1 is past him at ~S065) and anchor S075 (0.28, 7.80) dropped, spline S067 -> S084 (the stop -> pop start in 0.17 s was a 41 m/s2 jerk)",
 "X5 (A): S105 (0.03, 3.13) -> (0.03, 3.25), S120 (0.25, 2.51) -> (0.20, 2.64), S138 y 2.56 -> 2.62: O5 open >= 1.0 m at the release (was 0.97 m)",
 "X5 (B): new anchors S120 (0.85, 2.95), S138 (1.45, 2.95), S156 (1.55, 2.90): trails O5 (A anchors put him through O5 at S118-S123)",
 "A pass: release S084 kept, catch S098 (was S095): flight 0.47 s, ~11 m/s (14.1 m/s broke the 14 m/s cap and the 10 cm/120 Hz catch continuity)",
 "B pass: release S086 kept, catch S114 (was S108; O3 'control estable' ~S115): flight 0.93 s, ~11.6 m/s over 10.8 m (14.8 m/s broke both checks)",
 "X3: stop S065-S066 in A and B (the brief's 'planta inicial' at S066; B's own S066 coordinate (-5.40, 2.88) -> the shared S065 spot): X3 is still at the decision and B only diverges after it",
 "X3 (B): S108 (-2.73, 2.69) -> (-2.40, 2.73): the brake-and-reverse in 0.23 s was a 31 m/s2 jerk (he still brakes at S101 and closes out from S108)",
 "X4: S084 (4.04, 6.18) -> (3.85, 6.35): smaller containment step, the reversal back to O4 was 25 m/s2",
 "V2 (2026-11-20, owner brief Double-Drag-V2 sec. 5.3/5.4): DUR S158 -> S200; A layup S113 -> S116 (O5 controls 0.6 s before the gather: catch, two steps, takeoff readable), make S131; B shot S127 -> S133 (the auto 'shoot' load began 0.5 s before t0 = BEFORE the catch at S114: catch, absorb and load were one blur), make S163 + ball through the net, O3's follow-through and landing to S193",
 "X3 (B, V2): closeout anchors S138 -> S142, S156 -> S162 (the release moved to S133; O3 keeps >= 1.8 m at the release = the late closeout the brief describes)",
 "O3 (V2 control data): x -0.12 m from S050 on (S065 (-6.88, 2.33) -> (-7.00, 2.33), B (-6.87/-6.79) -> (-6.99/-6.91)): at the catch his inner toe was at |x| 6.593 m, ON the corner line (|x| 6.60 = 2 points); now every sole is >= 6.70 m out and <= 7.0 m (sideline 7.50)",
 "O1 (B, V2 pass fix 2026-11-20): pick-up S077 -> S074 and the skip is a PHASED overhead throw (engine opt-in 'phased'): gather to the chest pocket in the pass frame S074-S080, load just above the forehead S079.1-S083 (1.86 m), push forward + up S083-S086, release S086 at 2.00 m, 0.40 m toward O3 (the old load went straight up on X4's side to 2.05 m, arms locked S082-S086, off hand 0.7-1.3 m off the ball S077-S081); follow-through along the pass line",
 "all players: first waypoint flagged 'fly' (new engine option): the S-clock begins mid-transition; clamped runs started from rest (O5 30 m/s2 at S000)"]
DUR = S(200)   # V2 (2026-11-20): S158 -> S200, the B three is seen through the net (+8-15 frames) and the A layup lands


def track(anchors, dur=DUR):
    ks = sorted(anchors)
    wp = [[S(k), *M(anchors[k])] for k in ks]
    # flying start: the S-clock begins mid-transition, so the first run is already at speed at S000 (engine 'fly' flag)
    if len(wp) > 1 and wp[1][1:] != wp[0][1:]:
        wp[0].append("fly")
    if wp[-1][0] < dur:
        wp.append([dur, wp[-1][1], wp[-1][2]])
    return wp


def tracks(kind):
    tr = {pid: track(a) for pid, a in {**OFF, **DEF}.items()}
    if kind == "b":
        x3 = {k: v for k, v in DEF["X3"].items() if k <= 65}
        x3.update(B_X3)
        tr["X3"] = track(x3)
        o5 = {k: v for k, v in OFF["O5"].items() if k <= 65}
        o5.update(B_O5)
        tr["O5"] = track(o5)
        o3 = {k: v for k, v in OFF["O3"].items() if k <= 65}
        o3.update(B_O3)
        tr["O3"] = track(o3)
        x5 = {k: v for k, v in DEF["X5"].items() if k <= 94}
        x5.update(B_X5)
        tr["X5"] = track(x5)
    return tr


def actions(kind):
    a = {
        "O5": [{"type": "screen", "from": S(32), "to": S(48), "face": "X1"}],
        "O4": [{"type": "screen", "from": S(53), "to": S(67), "face": "X1"}],
        "X1": [st("O1", 0, DUR)],
        "X2": [st("ball", S(30), DUR)],
        "X4": [st("O1", S(50), S(90)), st("O4", S(92), DUR)],
        "X5": [st("O1", S(36), S(60))],
        "O2": [], "O3": [],
        "X3": [st("ball", S(20), DUR)] if kind == "a" else [st("ball", S(20), S(66)), st("O5", S(67), S(100)), {"type": "closeout", "from": S(104), "to": S(124)}, {"type": "contest", "from": S(122), "to": S(140)}],
        "O1": [{"type": "face", "from": S(70 if kind == "a" else 76), "to": S(84 if kind == "a" else 86), "face": "O5" if kind == "a" else "O3"}],
    }
    if kind == "a":
        a["X5"].append({"type": "contest", "from": S(110), "to": S(128)})
        a["O5"].append({"type": "celebrate", "from": S(146), "to": DUR - 0.05})
    else:
        a["O3"] = [{"type": "catchReady", "from": S(96), "to": S(114), "face": "O1"}, {"type": "celebrate", "from": S(170), "to": DUR - 0.05}]
    return a


def ball(kind):
    pick = 80 if kind == "a" else 74   # B: pick-up S074 (V2 pass fix: gather 0.2 s -> chest -> load -> push -> release S086)
    ev = [{"type": "hold", "player": "O1", "from": 0, "to": S(pick), "dribble": True, "hand": -1, "cross": [S(40)]}]   # pick-up S080 (brief S079-S080)
    if kind == "a":
        ev += [{"type": "hold", "player": "O1", "from": S(80), "to": S(84)},
               {"type": "pass", "from": "O1", "to": "O5", "t0": S(84), "t1": S(98), "style": "chest", "eyes": 0.45, "lead": True},
               {"type": "hold", "player": "O5", "from": S(98), "to": S(116)},
               {"type": "layup", "player": "O5", "t0": S(116), "t1": S(131), "make": True}]
    else:
        ev += [{"type": "hold", "player": "O1", "from": S(74), "to": S(86)},
               {"type": "pass", "from": "O1", "to": "O3", "t0": S(86), "t1": S(114), "style": "overhead", "eyes": 0.4, "phased": True},
               {"type": "hold", "player": "O3", "from": S(114), "to": S(133)},
               {"type": "shot", "player": "O3", "t0": S(133), "t1": S(163), "make": True, "three": True}]
    return ev


def spec(kind):
    s = {"id": "ddtr-a-roll" if kind == "a" else "ddtr-b-skip",
         "title": ("Double Drag in transition A: X3 stays home, roll pass in stride, left-hand layup" if kind == "a" else
                   "Double Drag in transition B: X3 tags the roll, skip to the corner, three"),
         "duration": DUR, "concept": "double-drag-transition", "source": SRC, "squareUp": True, "catchV2": 2,
         "players": PLAYERS, "tracks": tracks(kind), "ball": ball(kind), "actions": actions(kind), "screens": [],
         "sclock": {"fps": 30, "mirrorX": True, "shared_until": 65, "anchors": "brief sec. 5", "adjust": ADJUST}}
    common = {"start": 0, "screen1": S(32), "screen1off": S(48), "screen2": S(53), "screen2hit": S(62), "screen2off": S(67), "cross": S(40), "gather": S(80)}
    if kind == "a":
        s["marks"] = {**common, "decide": S(66), "pass": S(84), "catch": S(98), "release": S(116), "make": S(131), "end": DUR}
        s["claims"] = [
            {"type": "near", "a": "O5", "b": "X1", "at": "screen1", "max": 1.6, "says": "the guard gets two screens in a row (1st: O5 on X1)"},
            {"type": "near", "a": "O4", "b": "X1", "at": "screen2hit", "max": 1.8, "says": "two screens in a row (2nd: O4 on X1)"},
            {"type": "far", "a": "O4", "b": "O5", "at": "pass", "min": 4.0, "says": "The first screener dives. The second steps out to the arc."},
            {"type": "near", "a": "X3", "b": "O3", "at": "pass", "max": 1.7, "says": "Stay with his shooter?"},
            {"type": "near_rim", "player": "O5", "at": "release", "max": 1.5, "says": "Hit the roller in stride."},
            {"type": "order", "marks": ["screen1", "screen1off", "screen2", "screen2off", "pass", "catch", "release", "make"], "says": "two screens, roll, layup"}]
        s["notes"] = ["Brief sec. 5 anchors (mirrored to repo axes). X3 stays connected to O3.",
                      "O1 leads O5 in stride (S084 -> S095); O5 finishes on the left of the rim, release ~S113."]
    else:
        s["marks"] = {**common, "gather": S(74), "decide": S(66), "tag": S(75), "pass": S(86), "catch": S(114), "release": S(133), "make": S(163), "end": DUR}
        s["claims"] = [
            {"type": "reacts_after", "player": "X3", "event": "decide", "min": 0.05, "says": "This time, he steps in to tag the roll."},
            {"type": "far", "a": "X3", "b": "O3", "at": "pass", "min": 2.5, "says": "See what he just left?"},
            {"type": "behind_arc", "player": "O3", "at": "catch", "says": "Skip it to the corner."},
            {"type": "open", "player": "O3", "at": "release", "min": 1.0, "says": "Skip it to the corner (late closeout)."},
            {"type": "order", "marks": ["screen1", "screen2", "decide", "tag", "pass", "catch", "release", "make"], "says": "two screens, tag, skip, three"}]
        s["notes"] = ["Same as ddtr-a-roll until S065.", "X3 steps in from S066; O1 reads it and skips over the top (S086 -> S108); late closeout; corner three."]
    return s


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T, "tactical", "plays", f"{s['id']}.json")
    # tracks are given as waypoints (S-clock anchors): the play IS the spec, no leg builder
    json.dump(s, open(out, "w"), indent=1)
    return s


if __name__ == "__main__":
    for k in ("a", "b"):
        s = build(spec(k))
        print("built", s["id"], json.dumps(s["marks"]))
