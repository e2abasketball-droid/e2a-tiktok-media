#!/usr/bin/env python3
"""2-3 ZONE: FIVE DEFENDERS, ONE DEADLY GAP (owner master brief E2A_CLAUDE_MASTER_23_ZONE_40S_CINEMATIC.md, 2026-11-21).
Half court, FIBA. Offence 1-2-2 look: O1 top with the ball, O2 left wing, O3 right wing (shooter), O4 right short corner,
O5 left slot. Defence 2-3 zone: X1/X2 top, X3/X4 low, X5 middle.
  A  zone23-a-nail   O5 flashes to the nail (curved), O1 -> O5, X5 steps up AFTER the catch, X4 hesitates between
                     the short corner and the middle (0.2 s), O4 cuts baseline BEHIND X4, O5 -> O4, layup (make).
  B  zone23-b-skip   X1/X2 squeeze the nail, O1 -> O2 (left wing), X1 closes during the flight, X3 bumps and drops,
                     O2 throws a DIRECT skip O2 -> O3 (overhead, arc), X2 recovers from the nail, X4 is held by O4's
                     baseline fake and closes out late; O3 catch-and-shoot three (make).
  C  zone23-c-slow   same set-up as B, but O2 holds the ball (~1.3 s more): X2 and X4 get there before the catch;
                     O3 catches with the closeout on him and does NOT shoot (zone resets).
Brief axes (sec. 5.1): x < 0 = LEFT seen from half court looking at the basket. Repo axes (as BLOB/Pistol): repo x = -brief x;
y from the baseline unchanged; rim (0, 1.575, 3.05). Anchors are frames S(n) = n/30 s (game clock, t = 0 = neutral set).
  python3 tactical/specs/_gen-zone23.py   (writes tactical/specs/zone23-{a-nail,b-skip,c-slow}.spec.json + tactical/plays/)"""
import json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
S = lambda n: round(n / 30, 4)
M = lambda p: [round(-p[0], 3), p[1]]   # brief axes -> repo axes
P = lambda i, t, r: {"id": i, "team": t, "role": r}
st = lambda f, a, b: {"type": "stance", "from": S(a), "to": S(b), "face": f}
SRC = ("E2A didactic construction (owner master brief '2-3 Zone 40s cinematic', sec. 2, 5-10) on: basketballforcoaches.com "
       "'2-3 zone defense' (top two / bottom three, high post, bump, skip rotations, closeouts); breakthroughbasketball.com "
       "2-3 zone principles and 'attacking the 2-3 zone' (high post, short corner, high-low); FIBA WABC coaching manual "
       "(attacking zones: high post, skip pass, 2-on-1 on the weak side); FIBA court 28 x 15 m, three-point line 6.75 m.")
DUR = {"a": 112, "b": 135, "c": 120}

PLAYERS = [P("O1", "O", "Point (0, 8.90) with the ball: entry pass to the nail (A) / to the left wing (B, C); stays high (balance)"),
           P("O2", "O", "Left wing (-6.25, 5.90): spacing in A; catches and throws the DIRECT skip to O3 in B (late in C)"),
           P("O3", "O", "Right wing shooter (6.30, 5.90), 7.64 m from the rim (FIBA 6.75): catch-and-shoot three in B"),
           P("O4", "O", "Right short corner (5.45, 1.95), outside the restricted area: baseline cut behind X4 + layup (A); baseline fake that holds X4 (B)"),
           P("O5", "O", "Left slot (-3.60, 5.60): curved flash to the nail and catch (A); nail threat that holds X2 (B, C), never receives"),
           P("X1", "X", "Zone top-left: pinches the nail (A); closes to O2 during the flight O1 -> O2 (B)"),
           P("X2", "X", "Zone top-right: pinches the nail, active hand on O5 (A); sinks to the nail, recovers late to O3 after the skip (B)"),
           P("X3", "X", "Zone low-left: compresses to the rim (A); bump to the left wing, then back down (B)"),
           P("X4", "X", "Zone low-right = THE DECIDER: short corner (O4) or help; hesitates 0.2 s (A); held by O4's fake, late closeout (B)"),
           P("X5", "X", "Zone middle: protects the rim; steps up to the high post only AFTER O5's catch (A); stays home (B)")]

START = {"O1": (0.0, 8.90), "O2": (-6.25, 5.90), "O3": (6.30, 5.90), "O4": (5.45, 1.95), "O5": (-3.60, 5.60),
         "X1": (-1.90, 6.80), "X2": (1.90, 6.80), "X3": (-4.15, 3.20), "X4": (4.15, 3.20), "X5": (0.00, 3.40)}

def mj(f0, f1, p0, p1, ctrl=None, step=2):
    """minimum-jerk move (zero speed and acceleration at both ends) from p0 at frame f0 to p1 at frame f1, along a
    quadratic Bezier through `ctrl` (curved run) parametrised by arc length: peak speed 1.875 d/T, peak accel 5.77 d/T^2.
    The clamped track spline through these 2-frame samples starts and stops without the velocity jump of a bare run."""
    c = ctrl or ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    bz = lambda u: ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1])
    us = [i / 400 for i in range(401)]
    pts = [bz(u) for u in us]
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    L = cum[-1]
    out = {}
    fs = list(range(f0, f1, step)) + [f1]
    for fr in fs:
        x = (fr - f0) / (f1 - f0)
        w = 10 * x ** 3 - 15 * x ** 4 + 6 * x ** 5
        target = w * L
        j = next((k for k in range(len(cum)) if cum[k] >= target - 1e-12), len(cum) - 1)
        if j == 0:
            q = pts[0]
        else:
            r = (target - cum[j - 1]) / max(1e-12, cum[j] - cum[j - 1])
            q = (pts[j - 1][0] + (pts[j][0] - pts[j - 1][0]) * r, pts[j - 1][1] + (pts[j][1] - pts[j - 1][1]) * r)
        out[fr] = (round(q[0], 3), round(q[1], 3))
    out[f0], out[f1] = tuple(p0), tuple(p1)
    return out


def cat(*parts):
    d = {}
    for p in parts:
        d.update(p)
    return d


# ---------------------------------------------------------------- A: flash to the nail, high-low, layup
NAIL = (-0.55, 5.55)
X5UP = (-1.05, 4.45)     # brief "for example (-1.2, 4.65)": 1.44 m from his spot, reachable in 0.67 s (accel <= 19 m/s^2)
A = {
 "O1": {12: (0.0, 8.90), 18: (0.05, 8.86), 30: (0.15, 8.78), 60: (0.20, 8.70)},
 # curved flash: dips DOWN (y 5.2, away from X1's pinch line), sprint (~6 m/s), brakes, stops at the nail at S030, catch S031
 "O5": mj(0, 30, START["O5"], NAIL, ctrl=(-2.35, 4.80)),
 "X1": {10: (-1.85, 6.66), 20: (-1.58, 6.38), 35: (-1.45, 6.26), 70: (-1.40, 6.22)},
 "X2": {10: (1.82, 6.70), 22: (1.32, 6.32), 34: (0.88, 6.15), 70: (0.90, 6.12)},
 # X5 stands in his stance until the CATCH (S031), then steps up to his defensive left (never through O5's chest);
 # after O5's pass (S058) he changes feet too late (S062) and tries to get back to the rim
 "X5": cat(mj(31, 51, START["X5"], X5UP, ctrl=(-0.25, 4.05)), mj(62, 94, X5UP, (-0.42, 2.95), ctrl=(-0.95, 3.55)), {112: (-0.42, 2.95)}),
 # O4 starts the cut when X5 has committed (S036), runs the baseline BEHIND X4, catch on the move S072, layup S078
 "O4": cat(mj(36, 92, START["O4"], (0.60, 1.45), ctrl=(3.10, 1.18)), {112: (0.60, 1.45)}),
 # X4 shades to the middle on the flash, HESITATES S039 -> S045 (short corner or help), then chases from behind O4
 "X4": cat(mj(10, 39, START["X4"], (3.56, 2.94), ctrl=(3.95, 3.02)), {45: (3.56, 2.94)}, mj(45, 96, (3.56, 2.94), (1.55, 2.05), ctrl=(2.75, 2.25)),
           {112: (1.55, 2.05)}),
 "X3": {31: (-4.02, 3.12), 45: (-3.22, 2.72), 70: (-2.95, 2.55), 112: (-2.90, 2.50)},
 "O2": {40: (-6.18, 6.00), 112: (-6.15, 6.02)},
 "O3": {60: (6.22, 5.86), 112: (6.20, 5.85)},
}
# ---------------------------------------------------------------- B: entry to the left wing, DIRECT skip, three
X1W = (-5.35, 6.70)      # X1's closeout spot on O2: TOP side (he comes from the top), 1.2 m from O2, off the skip line
X2N = (0.50, 5.22)       # X2 sunk under the nail (O5 threat), 0.7 m below the skip line
B = {
 "O1": {10: (0.0, 8.90), 22: (-0.20, 8.82), 40: (-0.40, 8.70), 135: (-0.40, 8.70)},
 # O5 threatens the nail with a short move and keeps X2 honest; never receives
 "O5": cat(mj(0, 24, START["O5"], (-2.05, 5.40), ctrl=(-2.80, 5.30)), mj(30, 60, (-2.05, 5.40), (-1.88, 5.32)), {135: (-1.88, 5.32)}),
 # X1 pinches, then slides to the wing UNDER the O1 -> O2 lane and a step behind the ball; closes out from the top
 "X1": cat(mj(6, 44, START["X1"], X1W, ctrl=(-3.70, 5.85)), {48: X1W}, mj(48, 80, X1W, (-4.60, 6.40)), {135: (-4.60, 6.40)}),
 # X2 sinks to the nail, reacts 0.23 s after the skip release (S044 -> S051), long recovery BELOW the skip line, chop steps
 "X2": cat(mj(0, 34, START["X2"], X2N, ctrl=(1.10, 6.05)), {51: X2N}, mj(51, 106, X2N, (5.20, 5.72), ctrl=(3.10, 5.05)), {135: (5.20, 5.72)}),
 # X3 bumps to the wing while X1 travels, then drops back to the low-left / rim
 "X3": {14: (-4.60, 3.70), 26: (-4.98, 4.28), 34: (-4.90, 4.10), 46: (-4.20, 3.40), 70: (-3.60, 3.00), 92: (-2.80, 2.60), 135: (-2.70, 2.55)},
 # X4 watches O4 (baseline fake S030-S052) and follows it, then the late closeout S052 -> S094 (hands up at the release)
 "X4": cat(mj(0, 24, START["X4"], (4.35, 2.86)), {36: (4.35, 2.86)}, mj(36, 46, (4.35, 2.86), (4.45, 2.80)), {54: (4.45, 2.80)},
           mj(54, 96, (4.45, 2.80), (5.80, 5.10), ctrl=(4.95, 3.70)), {135: (5.80, 5.10)}),
 "O4": cat(mj(27, 41, START["O4"], (5.05, 1.60)), mj(41, 56, (5.05, 1.60), (5.40, 1.90)), {135: (5.40, 1.90)}),
 "X5": {26: (-0.45, 3.30), 46: (-0.40, 3.25), 60: (0.25, 3.15), 86: (0.60, 2.80), 135: (0.60, 2.62)},
 "O2": {18: (-6.20, 5.95), 135: (-6.20, 5.95)},
 "O3": {55: (6.30, 5.90), 135: (6.30, 5.90)},
}
# ---------------------------------------------------------------- C: same set-up, the ball stays in O2's hands too long
C = {k: {f: p for f, p in v.items() if f <= 34} for k, v in B.items()}
C["O1"] = B["O1"]
C["O5"] = B["O5"]
C["O2"] = {18: (-6.20, 5.95), 120: (-6.20, 5.95)}
C["X1"] = cat(mj(6, 44, START["X1"], X1W, ctrl=(-3.70, 5.85)), {120: X1W})
# X2 is not fooled for long: back to the right gap while O2 holds, then a SHORT closeout -> there before the catch (S099)
C["X2"] = cat(mj(0, 34, START["X2"], X2N, ctrl=(1.10, 6.05)), {40: X2N}, mj(40, 70, X2N, (2.80, 5.20)), mj(70, 104, (2.80, 5.20), (5.45, 5.25)),
              {120: (5.45, 5.25)})
C["X3"].update({46: (-4.20, 3.40), 70: (-3.60, 3.00), 120: (-3.40, 2.90)})
# X4 is free of his doubt (O4 does nothing new): he is already sliding up when the skip leaves
C["X4"] = cat(mj(0, 24, START["X4"], (4.35, 2.86)), {40: (4.35, 2.86)}, mj(40, 100, (4.35, 2.86), (6.00, 4.75), ctrl=(4.95, 3.70)), {120: (6.00, 4.75)})
C["O4"] = {36: (5.40, 1.90), 120: (5.40, 1.90)}
C["O4"] = cat(mj(30, 54, START["O4"], (5.40, 1.90)), {120: (5.40, 1.90)})
C["X5"].update({46: (-0.40, 3.25), 75: (0.25, 3.15), 120: (0.40, 3.00)})
C["O3"] = {55: (6.30, 5.90), 120: (6.30, 5.90)}

# zone defence (2026-11-21): no man-to-man `guards`; each defender owns a floor AREA (test-play checks this instead)
ZONE = {"type": "2-3", "areas": {"X1": "top-left (nail / left elbow / left wing)", "X2": "top-right (nail / right elbow / right wing)",
                                  "X3": "low-left (left block / left corner)", "X4": "low-right (right block / short corner / right corner)",
                                  "X5": "middle (rim / dunker spots / high post)"}}

ADJUST = [
 "Brief event table times are previs targets (sec. 7, 8: 'adapt after simulating the rigs'). Pass speeds kept <= 12 m/s at the contact (qc-catch), runs <= 6 m/s and <= 22 m/s^2 (minimum-jerk moves, mj()):",
 "A O5 flash: brief 0.15 -> 0.55 s for 3.05 m (7.6 m/s, ~40 m/s^2) -> S000 -> S030 (1.00 s, 6.0 m/s peak, 19 m/s^2); curved down to y ~5.2 (1.1 m under X1's pinch line) so O5 never crosses X1; stops at the nail, catch S031",
 "A O1 -> O5: release S021 (0.70 s, brief 0.70), catch S031 (1.03 s, brief 1.04)",
 "A X5 stands still until the catch (S031), then steps up to (-1.05, 4.45) at S051 (1.70 s; brief 'for example (-1.2, 4.65)' at 1.28 s: 1.44 m from rest in 0.25 s is not humanly possible)",
 "A O4 cut starts S036 (1.20 s, brief 1.28) when X5 is committed; O5 -> O4 release S058 (1.93 s, brief 1.95), catch on the move S072 (2.40 s, brief 2.25: 4.7 m in 0.30 s would be 15.8 m/s, above the 12 m/s catch limit); layup S078 -> S096 (2.60 -> 3.20 s, brief 2.55 -> 3.30)",
 "A X4 hesitation S039 -> S045 (0.20 s standing, brief 0.15-0.25 s), then the chase from BEHIND O4 (never in front of him, >= 1 m at the catch)",
 "B O1 -> O2: brief 0.35 -> 0.72 s for 6.93 m (18.7 m/s) -> S010 -> S028 (0.33 -> 0.93 s, 11.5 m/s)",
 "B skip O2 -> O3 DIRECT: release S044 (1.47 s, brief 1.05-1.30; O2 needs 0.5 s from the catch to load an overhead with both hands on the ball), catch S077 (2.57 s, brief 2.20): 12.5 m in 1.10 s overhead with an arc",
 "B O3 catch-and-shoot: gather S077 -> S088, release S088 (2.93 s, brief 2.70), make S119 (3.97 s, brief 3.65-4.10). O3 is >= 1.8 m clear at the catch; X4's late closeout is ~1.1 m away, hands up, at the release (late contest, no contact): shown as a late step, never 'wide open'",
 "B X1 closes out on O2 from the TOP (-5.35, 6.70), runs UNDER the O1 -> O2 lane a step behind the ball; X2 sinks UNDER the nail (0.50, 5.22), 0.7 m below the skip line",
 "C (slow): identical to B to S034; O2 holds to S066 (+0.73 s vs B), skip S066 -> S099; X2 (1.1 m) and X4 arrive with the catch, O3 does not shoot",
]


def track(anchors, dur):
    ks = sorted(anchors)
    wp = [[S(k), *M(anchors[k])] for k in ks]
    if wp[-1][0] < dur:
        wp.append([dur, wp[-1][1], wp[-1][2]])
    return wp


def tracks(kind):
    br = {"a": A, "b": B, "c": C}[kind]
    out = {}
    for pid, p0 in START.items():
        an = {0: p0}
        an.update(br.get(pid, {}))
        out[pid] = track(an, S(DUR[kind]))
    return out


def actions(kind):
    d = DUR[kind]
    act = {pid: [] for pid in START}
    if kind == "a":
        act["O1"] = [{"type": "face", "from": S(10), "to": S(21), "face": "O5"}, {"type": "face", "from": S(21), "to": S(d), "face": "ball"}]
        act["O5"] = [{"type": "catchReady", "from": S(20), "to": S(31), "face": "O1"}, {"type": "face", "from": S(34), "to": S(58), "face": "O4"}]
        act["O4"] = [{"type": "face", "from": 0, "to": S(38), "face": "ball"}, {"type": "catchReady", "from": S(62), "to": S(72), "face": "O5"}]
        act["X1"] = [st("ball", 0, d)]
        act["X2"] = [st("ball", 0, d)]
        act["X3"] = [st("ball", 0, d)]
        act["X4"] = [st("ball", 0, 46), st("O4", 48, d)]
        act["X5"] = [st("ball", 0, 31), st("O5", 33, 60), st("ball", 62, d)]
        act["O2"] = [{"type": "face", "from": 0, "to": S(d), "face": "ball"}]
        act["O3"] = [{"type": "face", "from": 0, "to": S(d), "face": "ball"}]
    else:
        rel, cat = (44, 77) if kind == "b" else (66, 99)
        act["O1"] = [{"type": "face", "from": 0, "to": S(10), "face": "O2"}, {"type": "face", "from": S(10), "to": S(d), "face": "ball"}]
        act["O2"] = [{"type": "catchReady", "from": S(14), "to": S(28), "face": "O1"}, {"type": "face", "from": S(30), "to": S(rel), "face": "O3"}]
        act["O3"] = [{"type": "face", "from": 0, "to": S(rel - 12), "face": "ball"}, {"type": "catchReady", "from": S(rel + 12), "to": S(cat), "face": "O2"}]
        act["O4"] = [{"type": "face", "from": 0, "to": S(d), "face": "ball"}]
        act["O5"] = [{"type": "face", "from": 0, "to": S(d), "face": "ball"}]
        act["X1"] = [st("ball", 0, d)]
        act["X3"] = [st("ball", 0, d)]
        act["X5"] = [st("ball", 0, d)]
        if kind == "b":
            act["X2"] = [st("ball", 0, 79), {"type": "closeout", "from": S(79), "to": S(88)}, {"type": "contest", "from": S(88), "to": S(106)}]
            act["X4"] = [st("O4", 0, 54), st("ball", 56, 86), {"type": "contest", "from": S(88), "to": S(112)}]
        else:
            act["X2"] = [st("ball", 0, 90), {"type": "closeout", "from": S(90), "to": S(99)}, {"type": "contest", "from": S(99), "to": S(120)}]
            act["X4"] = [st("ball", 0, 96), {"type": "contest", "from": S(99), "to": S(120)}]
    return act


def ball(kind):
    if kind == "a":
        return [{"type": "hold", "player": "O1", "from": 0, "to": S(21), "pocket": True},
                {"type": "pass", "from": "O1", "to": "O5", "t0": S(21), "t1": S(31), "style": "chest", "eyes": 0.3, "lead": True},
                {"type": "hold", "player": "O5", "from": S(31), "to": S(58), "pocket": True},
                {"type": "pass", "from": "O5", "to": "O4", "t0": S(58), "t1": S(72), "style": "chest", "eyes": 0.3, "lead": True},
                {"type": "hold", "player": "O4", "from": S(72), "to": S(78), "pocket": True},
                {"type": "layup", "player": "O4", "t0": S(78), "t1": S(96), "make": True}]
    rel, cat = (44, 77) if kind == "b" else (66, 99)
    ev = [{"type": "hold", "player": "O1", "from": 0, "to": S(10), "pocket": True},
          {"type": "pass", "from": "O1", "to": "O2", "t0": S(10), "t1": S(28), "style": "chest", "eyes": 0.3, "lead": True},
          {"type": "hold", "player": "O2", "from": S(28), "to": S(rel), "pocket": True},
          {"type": "pass", "from": "O2", "to": "O3", "t0": S(rel), "t1": S(cat), "style": "overhead", "eyes": 0.4, "lead": True, "phased": True}]
    if kind == "b":
        ev += [{"type": "hold", "player": "O3", "from": S(cat), "to": S(88), "pocket": True},
               {"type": "shot", "player": "O3", "t0": S(88), "t1": S(119), "make": True, "contested": True}]
    else:
        ev += [{"type": "hold", "player": "O3", "from": S(cat), "to": S(DUR["c"]), "pocket": True}]
    return ev


def spec(kind):
    sid = {"a": "zone23-a-nail", "b": "zone23-b-skip", "c": "zone23-c-slow"}[kind]
    title = {"a": "2-3 zone (A): flash to the nail, X5 steps up, O4 cuts behind X4, high-low layup",
             "b": "2-3 zone (B): O1 -> O2, DIRECT skip O2 -> O3, X2 and X4 late, three",
             "c": "2-3 zone (C, too slow): same set as B, O2 holds, the zone resets, O3 is contested"}[kind]
    s = {"id": sid, "title": title, "duration": S(DUR[kind]), "concept": "zone-2-3-nail-and-skip", "source": SRC, "squareUp": True,
         "catchV2": 2, "handBallClear": True, "players": PLAYERS, "tracks": tracks(kind), "ball": ball(kind), "actions": actions(kind),
         "screens": [], "zone": ZONE, "sclock": {"fps": 30, "mirrorX": True, "anchors": "E2A anchors on brief sec. 7-9", "adjust": ADJUST},
         "expect": {"owner": {"player": "O1", "from": 0, "to": S(20 if kind == "a" else 9)}}}
    if kind == "a":
        s["marks"] = {"start": 0, "flash": S(3), "nail": S(26), "pass": S(21), "catch": S(31), "stepup": S(42), "cut": S(38),
                      "pass2": S(58), "catch2": S(72), "gather": S(78), "make": S(96), "end": s["duration"]}
        s["claims"] = [
            {"type": "reacts_after", "player": "X5", "event": "catch", "min": 0.0, "says": "If the center steps up (after the catch)"},
            {"type": "near", "a": "O5", "b": "X5", "at": "pass2", "max": 1.4, "says": "X5 has stepped up to O5 when O5 passes"},
            {"type": "open", "player": "O4", "at": "catch2", "min": 0.8, "says": "a cutter slips behind"},
            {"type": "near_rim", "player": "O4", "at": "gather", "max": 1.4, "says": "Layup."},
            {"type": "order", "marks": ["flash", "pass", "catch", "cut", "stepup", "pass2", "catch2", "gather", "make"], "says": "flash, entry, step up, cut, high-low, layup"}]
    elif kind == "b":
        s["marks"] = {"start": 0, "pass": S(10), "catch": S(28), "skip": S(44), "react": S(51), "skipcatch": S(77), "release": S(88),
                      "make": S(119), "end": s["duration"]}
        s["claims"] = [
            {"type": "behind_arc", "player": "O3", "at": "skipcatch", "says": "...and throw the SKIP. THREE points."},
            {"type": "behind_arc", "player": "O3", "at": "release", "says": "THREE points (feet behind the FIBA line at the release)"},
            {"type": "open", "player": "O3", "at": "skipcatch", "min": 1.8, "says": "nobody can contest at the catch (brief sec. 8, 2.20 s)"},
            {"type": "open", "player": "O3", "at": "release", "min": 1.0, "says": "One late step. (late contest, hands up, no contact)"},
            {"type": "order", "marks": ["pass", "catch", "skip", "react", "skipcatch", "release", "make"], "says": "entry, skip, late closeout, three"}]
    else:
        s["marks"] = {"start": 0, "pass": S(10), "catch": S(28), "skip": S(66), "skipcatch": S(99), "end": s["duration"]}
        s["claims"] = [
            {"type": "near", "a": "O3", "b": "X2", "at": "skipcatch", "max": 1.3, "says": "But pass slowly? The zone resets."},
            {"type": "order", "marks": ["pass", "catch", "skip", "skipcatch"], "says": "entry, (too long), skip, contested"}]
    return s


if __name__ == "__main__":
    # FIBA three: O3 (brief 6.30, 5.90) -> distance to the rim
    print("O3 to rim", round(math.hypot(6.30, 5.90 - 1.575), 2), "m (FIBA 6.75)")
    for k in ("a", "b", "c"):
        s = spec(k)
        json.dump(s, open(os.path.join(D, f"{s['id']}.spec.json"), "w"), indent=1)
        json.dump(s, open(os.path.join(T, "tactical", "plays", f"{s['id']}.json"), "w"), indent=1)
        print("built", s["id"], json.dumps(s["marks"]))
