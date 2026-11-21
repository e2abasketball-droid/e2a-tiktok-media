#!/usr/bin/env python3
"""BLOB BOX SCREEN-THE-SCREENER (owner master brief E2A_CLAUDE_MASTER_BLOB_SCREEN_THE_SCREENER_40S.md, 2026-11-20).
Baseline out of bounds, box set. O3 inbounds from the right of the basket (out of bounds); O2 (right elbow) cross-screens
X5 for O5 (left block), O5 cuts under the screen to the rim.
  A  blob-a-rim    X4 stays home (half a step high, watching O4): O3 -> O5, catch, right-hand layup (make).
  B  blob-b-three  X4 drops to protect the rim (decision at gameTime 1.65 s): O3 FAKES to O5 (ball never leaves him),
                   O4 down-screens X2 ("screen the screener"), O2 curls to the right wing, O3 -> O2, catch, three (make).
Both branches are the SAME possession to frame S049 (1.633 s, < 1.65 s X4 decision): identical tracks, actions, ball.
Game clock: t = 0 is the ball at O3's disposal out of bounds (FIBA 5-second count). Anchors are frames S(n) = n/30 s.
Axis mapping (as Pistol / Double Drag): brief x > 0 = right seen from half court looking at the basket = offence's
RIGHT; repo x > 0 = offence's LEFT, so repo x = -brief x; y (from the baseline) unchanged; rim (0, 1.575, 3.05).
  python3 tactical/specs/_gen-blob.py   (writes tactical/specs/blob-{a-rim,b-three}.spec.json + tactical/plays/)"""
import json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
S = lambda n: round(n / 30, 4)
M = lambda p: [round(-p[0], 3), p[1]]   # brief axes -> repo axes
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": S(a), "to": S(b), "face": f}
SRC = ("E2A didactic construction (owner master brief 'BLOB Box Screen-the-Screener', sec. 04-06, 11, 12) on: FIBA "
       "WABC Coaching Manual level 2 (box set out of bounds: screen for the inside cutter, the screener becomes the "
       "second option; 'screen the screener'); FIBA Official Basketball Rules 2026 arts. 17 (throw-in, 5 seconds, the "
       "thrower out of bounds) and 33.7 (screening: legal when stationary, both feet on the floor).")
SHARED = 49          # last shared frame (X4's decision at gameTime 1.65 s = S049.5)
DUR = {"a": 120, "b": 186}

PLAYERS = [P("O1", "O", "Safety: left elbow, lifts to the left wing (-4.7, 7.2); never cuts, never a third finish"),
           P("O2", "O", "Right elbow: FIRST screener (cross screen on X5 for O5), then the shooter off O4's down screen (B)"),
           P("O3", "O", "Inbounder out of bounds right of the basket (3.50, -0.85): passes to O5 (A) / fakes O5, passes to O2 (B)"),
           P("O4", "O", "Right block: SECOND screener, down screen on X2 (B); lifts slightly in A"),
           P("O5", "O", "Left block: cuts under O2's screen to the rim; layup (A) / occupies the short paint (B)"),
           P("X1", "X", "On O1: stays with the safety", "O1"),
           P("X2", "X", "On O2: trails him to the first screen on the inside, is screened by O4 (B), late closeout", "O2"),
           P("X3", "X", "On the inbounder: in the court, hands active; bites on the pass fake (B)", "O3"),
           P("X4", "X", "On O4 = THE DEFENDER WHO DECIDES: stays home (A) / drops to protect the rim at 1.65 s (B)", "O4"),
           P("X5", "X", "On O5: basket side, meets O2's screen, trails O5 under it", "O5")]

# ---- brief sec. 04.2 starts (brief axes) and E2A anchors (frames). Common part (both branches) <= S049.
COMMON = {
 "O3": {0: (3.50, -0.85)},
 # O2: load, step to the middle, run down the lane, decelerate, both feet planted at S043 (1.43 s), screen point
 # (-1.35, 2.60) = brief (-1.35, 3.00) 0.40 m toward the baseline (see ADJUST)
 "O2": {0: (2.15, 5.55), 8: (2.08, 5.58), 16: (1.35, 5.22), 24: (0.45, 4.52), 32: (-0.42, 3.68), 38: (-0.98, 3.02),
        43: (-1.30, 2.65), 46: (-1.35, 2.60)},
 # O5: waits for the screen, sets X5 with a step out, then the cut (S046) down the outside and under the screen
 "O5": {0: (-2.20, 2.85), 20: (-2.25, 2.87), 34: (-2.31, 2.91), 40: (-2.38, 2.92), 46: (-2.50, 2.84)},
 "O4": {0: (2.35, 2.85), 40: (2.36, 2.88)},
 "O1": {0: (-2.25, 5.60), 15: (-2.30, 5.66), 40: (-3.20, 6.22)},
 "X1": {0: (-2.15, 5.05), 18: (-2.20, 5.10), 45: (-3.00, 5.66)},
 # X2 trails O2 on his INSIDE (basket side) to the first screen
 "X2": {0: (2.30, 4.80), 10: (2.15, 4.72), 20: (1.32, 4.42), 30: (0.32, 3.62), 40: (-0.35, 3.08), 46: (-0.55, 3.05)},
 "X3": {0: (3.10, 0.75)},
 "X4": {0: (1.85, 2.35), 30: (1.86, 2.42), 46: (1.88, 2.45)},
 # X5: basket side, sees the screener arrive (half a step up-left), tries the short way (S054) and meets O2
 "X5": {0: (-1.90, 2.40), 20: (-1.90, 2.42), 38: (-1.86, 2.50), 46: (-1.86, 2.55)},
}
A = {
 "O5": {50: (-2.54, 2.55), 56: (-2.38, 2.03), 62: (-1.70, 1.86), 68: (-0.85, 1.90), 74: (-0.05, 1.93), 79: (0.55, 1.95),
        84: (0.78, 1.86), 88: (0.70, 1.74), 102: (0.45, 1.62), 120: (0.55, 1.90)},
 "X5": {50: (-1.92, 2.60), 54: (-1.86, 2.62), 60: (-1.95, 2.45), 66: (-1.75, 2.20), 72: (-1.25, 2.05), 78: (-0.70, 2.05),
        88: (-0.45, 2.10), 102: (-0.25, 2.12), 120: (-0.20, 2.15)},
 "O2": {74: (-1.35, 2.60), 86: (-1.22, 3.05), 100: (-0.98, 3.65), 120: (-0.70, 4.05)},
 "X2": {74: (-0.55, 3.05), 90: (-0.40, 3.35), 105: (-0.25, 3.75), 120: (-0.15, 4.05)},
 "O4": {58: (2.35, 2.88), 75: (2.22, 3.20), 95: (1.95, 3.62), 120: (1.92, 3.68)},
 "X4": {58: (1.92, 2.52), 70: (1.98, 2.60), 80: (1.95, 2.55), 88: (1.62, 2.30), 98: (1.25, 2.05), 120: (1.15, 2.05)},
 "O1": {70: (-4.30, 6.90), 85: (-4.70, 7.20), 120: (-4.70, 7.22)},
 "X1": {75: (-3.95, 6.40), 90: (-4.20, 6.65), 120: (-4.22, 6.66)},
 "X3": {68: (3.10, 0.75), 78: (2.95, 0.92), 95: (2.70, 1.05), 120: (2.65, 1.10)},
 "O3": {100: (3.50, -0.85), 120: (3.45, -0.70)},
}
B = {
 "O5": {50: (-2.54, 2.55), 56: (-2.38, 2.03), 62: (-1.70, 1.86), 68: (-0.85, 1.95), 74: (-0.22, 2.00), 80: (0.00, 2.05),
        110: (0.02, 2.08), 150: (-0.05, 2.10), 186: (-0.10, 2.15)},
 # X5 trails O5 0.12-0.14 m lower than in A at S066-S072: O2 starts his curl at S066 right above him (qc-contact O2-X5 -0.078 m @2.27 s)
 "X5": {50: (-1.92, 2.60), 54: (-1.86, 2.62), 60: (-1.95, 2.45), 66: (-1.75, 2.06), 72: (-1.25, 1.96), 78: (-0.78, 2.08),
        90: (-0.72, 2.15), 150: (-0.70, 2.18), 186: (-0.70, 2.20)},
 # X4 decision: head/shoulders at S050, lateral drop S050 -> S069 to (1.1, 2.1) (brief), holds the help, recovers late
 "X4": {50: (1.88, 2.45), 53: (1.82, 2.41), 58: (1.58, 2.28), 63: (1.30, 2.16), 69: (1.10, 2.10), 92: (1.12, 2.12), 104: (1.45, 2.60),
        118: (2.05, 3.45), 132: (2.55, 4.20), 150: (2.75, 4.55), 186: (2.75, 4.60)},
 # O4 reads X4's help, leaves the block at S057 (1.9 s), plants the down screen at S086 on X2's chase line
 "O4": {57: (2.35, 2.88), 64: (2.05, 3.28), 72: (1.30, 3.82), 78: (0.80, 4.08), 82: (0.55, 4.18), 85: (0.47, 4.20), 86: (0.47, 4.20),
        106: (0.47, 4.20), 120: (0.70, 4.05), 150: (1.10, 3.70), 186: (1.15, 3.65)},
 # O2 holds the screen to S066 (O5 is past), then the curl over the top of O4 to the right wing; catch S130 at (5.2, 6.5)
 "O2": {66: (-1.35, 2.60), 70: (-1.31, 2.71), 76: (-1.06, 3.20), 82: (-0.62, 3.88), 90: (0.20, 4.80), 98: (1.30, 5.32), 106: (2.65, 5.74),
        114: (3.85, 6.12), 120: (4.55, 6.33), 126: (5.02, 6.45), 131: (5.20, 6.50), 186: (5.20, 6.50)},
 # X2: trails on the inside, meets O4 at S090, goes around under him, late closeout (contest after the release)
 "X2": {66: (-0.55, 3.05), 72: (-0.45, 3.18), 80: (-0.18, 3.48), 86: (-0.10, 3.55), 89: (-0.03, 3.56), 93: (0.20, 3.54), 98: (0.66, 3.60), 104: (1.30, 3.98),
        112: (2.15, 4.55), 121: (3.00, 5.10), 131: (3.40, 5.40), 142: (3.50, 5.58), 156: (4.30, 5.98), 186: (4.40, 6.02)},
 "O1": {70: (-4.30, 6.90), 85: (-4.70, 7.20), 186: (-4.70, 7.22)},
 "X1": {75: (-3.95, 6.40), 90: (-4.20, 6.65), 186: (-4.22, 6.66)},
 # X3: bites on the pass fake toward the paint (S064 -> S074), then tries to recover the angle to the wing
 "X3": {62: (3.10, 0.75), 70: (2.88, 0.88), 78: (2.80, 0.92), 100: (3.05, 1.05), 120: (3.30, 1.25), 186: (3.30, 1.30)},
 # O3: out of bounds until the release (S113); steps in legally afterwards (S125 ->)
 "O3": {118: (3.50, -0.85), 130: (3.42, -0.45), 150: (3.25, 0.30), 186: (3.20, 0.45)},
}
ADJUST = [
 "O2 screen 1: brief test point (-1.35, 3.00) -> (-1.35, 2.60) (0.40 m, inside the brief's 0.15-0.45 m tolerance): at 3.00 the screen was 0.6 m ABOVE X5's chase line (X5 starts basket side at (-1.90, 2.40) and O5 cuts under at y ~1.9-2.0), i.e. a screen on an empty spot (sec. 04.4 'regla de oro'); at 2.60 he plants 0.55 m on X5's ball side, so X5's short way to the right block runs into him and X5 has to trail O5 underneath",
 "O5 cut: from the left block down the OUTSIDE of X5 and under the screen (passes O2 at 0.73-0.83 m, y 1.86-1.95); the brief's 'y ~2.10-2.25' is 0.15-0.3 m lower here because X5 sits at y 2.4-2.6 (two bodies need >= 0.5 m)",
 "O4 screen 2: brief test point (0.15, 4.40) -> (0.45, 4.20) (0.36 m), the 'micro-adjustment to X2's real chase line' the brief asks for: X2 trails on O2's inside, O2 curls over the TOP of O4 (0.53-0.58 m from his centre), X2 runs into O4 at S090 (0.60 m) and goes around under him",
 "O2 route B: brief via-point (0.75, 4.90) -> (0.20, 4.80)/(1.30, 5.32) (curl over the top of O4); (2.7, 5.75) and the catch (5.20, 6.50) kept; catch 7.16 m from the basket (FIBA 6.75 m, both feet 0.41 m behind the line)",
 "B pass O3 -> O2: release S111 (3.70 s, brief 3.85-4.05), catch S131 (4.37 s, brief ~4.25): 7.6 m in 0.67 s = 11.4 m/s (qc-catch: <= 12 m/s at the contact); the brief's 3.85 -> 4.25 window would need 19 m/s, so the release is 0.15 s earlier (still 1.3 s inside the 5 s)",
 "A pass O3 -> O5: release S068 (2.27 s), catch S079 (2.63 s, brief ~2.55): 3.96 m at 10.8 m/s; layup take-off S088 (2.93 s), make S102 (3.40 s, brief release 3.35, net 3.55)",
 "B shot: catch S131, gather to S141 (4.70 s), shot S141 -> S172 (flight 1.03 s, make); brief window 4.35-5.15",
 "X2 start (2.25, 5.00) -> (2.30, 4.80) (0.2 m): at 0.56 m from O2 their arms interpenetrated in the stance (qc-contact -0.12 m)",
 "O5 set-up step S034-S050 0.1-0.15 m wider (away from X5): arms touched at 1.47 s (qc-contact -0.08 m)",
]
DUR_S = {k: S(v) for k, v in DUR.items()}


def track(anchors, dur):
    ks = sorted(anchors)
    wp = [[S(k), *M(anchors[k])] for k in ks]
    if wp[-1][0] < dur:
        wp.append([dur, wp[-1][1], wp[-1][2]])
    return wp


def tracks(kind):
    br = A if kind == "a" else B
    out = {}
    for pid, a in COMMON.items():
        an = dict(a)
        an.update(br.get(pid, {}))
        out[pid] = track(an, DUR_S[kind])
    return out


def actions(kind):
    a_ = kind == "a"
    dur = DUR[kind]
    act = {
        "O1": [{"type": "face", "from": S(90), "to": S(dur), "face": "ball"}],
        "O2": [{"type": "screen", "from": S(43), "to": S(74 if a_ else 66), "face": "X5"}],
        "O3": [{"type": "face", "from": 0, "to": S(40), "face": "O5"},
               {"type": "face", "from": S(40), "to": S(68 if a_ else 74), "face": "O5"}],
        "O5": [{"type": "face", "from": S(52), "to": S(74), "face": "O3"}],
        "O4": [],
        "X1": [st("O1", 0, dur)],
        "X3": [st("ball", 0, dur)],
        "X5": [st("O5", 0, 52), {"type": "bump", "from": S(52), "to": S(58)}, st("O5", 60, dur)],
    }
    if a_:
        act["O5"].append({"type": "catchReady", "from": S(72), "to": S(79), "face": "O3"})
        act["X4"] = [st("O4", 0, 80), st("O5", 82, dur)]
        act["X2"] = [st("O2", 0, dur)]
    else:
        act["O3"].append({"type": "face", "from": S(84), "to": S(111), "face": "O2"})
        act["O4"] = [{"type": "screen", "from": S(86), "to": S(106), "face": "X2"}]
        act["O2"].append({"type": "catchReady", "from": S(118), "to": S(131), "face": "O3"})
        act["X4"] = [st("O4", 0, 49), st("O5", 50, 96), st("O2", 98, dur)]
        act["X2"] = [st("O2", 0, 131), {"type": "closeout", "from": S(131), "to": S(141)}, {"type": "contest", "from": S(141), "to": S(158)}]
    return act


def ball(kind):
    if kind == "a":
        return [{"type": "hold", "player": "O3", "from": 0, "to": S(68), "pocket": True},
                {"type": "pass", "from": "O3", "to": "O5", "t0": S(68), "t1": S(79), "style": "chest", "eyes": 0.3, "lead": True},
                {"type": "hold", "player": "O5", "from": S(79), "to": S(88), "pocket": True},
                {"type": "layup", "player": "O5", "t0": S(88), "t1": S(102), "make": True}]
    return [{"type": "hold", "player": "O3", "from": 0, "to": S(111), "pocket": True,
             "present": {"toward": "O5", "from": S(60), "peak": S(65), "hold": S(68), "to": S(76), "amt": 0.14, "dz": 0.02}},
            {"type": "pass", "from": "O3", "to": "O2", "t0": S(111), "t1": S(131), "style": "overhead", "eyes": 0.4, "lead": True, "phased": True},
            {"type": "hold", "player": "O2", "from": S(131), "to": S(141), "pocket": True},
            {"type": "shot", "player": "O2", "t0": S(141), "t1": S(172), "make": True, "three": True}]


def spec(kind):
    a_ = kind == "a"
    sid = "blob-a-rim" if a_ else "blob-b-three"
    s = {"id": sid,
         "title": ("BLOB box (A): X4 stays home, O2 screens for O5, O3 -> O5, layup" if a_ else
                   "BLOB box (B): X4 protects the rim, O3 fakes, O4 screens the screener, O3 -> O2, three"),
         "duration": DUR_S[kind], "concept": "blob-box-screen-the-screener", "source": SRC, "squareUp": True, "catchV2": 2,
         "handBallClear": True, "players": PLAYERS, "tracks": tracks(kind), "ball": ball(kind), "actions": actions(kind),
         "screens": [],
         # FIBA art. 17: the thrower stays out of bounds until the release, release < 5 s (test-play 'inbound' checks)
         "inbound": {"player": "O3", "release": S(68) if a_ else S(111), "limit": 5.0, "margin": 0.5},
         "sclock": {"fps": 30, "mirrorX": True, "shared_until": SHARED, "anchors": "E2A anchors on brief sec. 04-05", "adjust": ADJUST},
         "expect": {"owner": {"player": "O3", "from": 0, "to": S(67 if a_ else 110)}}}
    common = {"start": 0, "screen1": S(43), "cut": S(46), "decide": S(50)}
    if a_:
        s["marks"] = {**common, "pass": S(68), "catch": S(79), "gather": S(88), "make": S(102), "end": s["duration"]}
        s["claims"] = [
            {"type": "near", "a": "O2", "b": "X5", "at": "cut", "max": 0.8, "says": "He screens for FIVE."},
            {"type": "open", "player": "O5", "at": "catch", "min": 1.0, "says": "If the defense stays home... easy layup."},
            {"type": "near_rim", "player": "O5", "at": "gather", "max": 1.0, "says": "easy layup"},
            {"type": "order", "marks": ["screen1", "cut", "pass", "catch", "gather", "make"], "says": "screen, cut, pass, layup"}]
    else:
        s["marks"] = {**common, "fake": S(65), "screen2": S(86), "screen2hit": S(90), "pass": S(111), "catch": S(131),
                      "release": S(141), "make": S(172), "end": s["duration"]}
        s["claims"] = [
            {"type": "near", "a": "O2", "b": "X5", "at": "cut", "max": 0.8, "says": "He screens for FIVE."},
            {"type": "reacts_after", "player": "X4", "event": "decide", "min": 0.0, "says": "But what if they protect the rim?"},
            {"type": "near_rim", "player": "X4", "at": "fake", "max": 1.6, "says": "But what if they protect the rim? (X4 at the rim when O3 fakes)"},
            {"type": "near", "a": "O4", "b": "X2", "at": "screen2hit", "max": 0.8, "says": "FOUR screens for TWO."},
            {"type": "behind_arc", "player": "O2", "at": "catch", "says": "Two escapes to the wing. Catch. Three."},
            {"type": "open", "player": "O2", "at": "release", "min": 1.8, "says": "Catch. Three."},
            {"type": "order", "marks": ["screen1", "cut", "decide", "fake", "screen2", "screen2hit", "pass", "catch", "release", "make"],
             "says": "screen, help, fake, screen the screener, pass, three"}]
    return s


if __name__ == "__main__":
    for k in ("a", "b"):
        s = spec(k)
        json.dump(s, open(os.path.join(D, f"{s['id']}.spec.json"), "w"), indent=1)
        json.dump(s, open(os.path.join(T, "tactical", "plays", f"{s['id']}.json"), "w"), indent=1)
        print("built", s["id"], json.dumps(s["marks"]))
