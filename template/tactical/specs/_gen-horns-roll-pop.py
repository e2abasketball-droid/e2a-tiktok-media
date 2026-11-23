#!/usr/bin/env python3
"""E2A HORNS: THE DEFENDER'S DILEMMA (owner brief 2026-11-22, E2A_HORNS_ROLL_POP_MASTER.md).
Technical name: Horns High Ball Screen, 5 rolls, 4 pops. Original E2A possession built from generic coaching
knowledge (FIBA Europe coaching "Horns", The Hoops Geek "Horns PnR/PnP", Basketball for Coaches "Horns Pick and
Roll"): no diagram, track or choreography copied, and NOT v4-horns-twist.json (a different play: second screen +
switches; only its court system was checked).

Court: FIBA half court, metres, basket (0, 1.575), y from the baseline. Camera behind the offence with the basket at
the top (yaw 0): x < 0 is the RIGHT of the screen = the offence's RIGHT.
  O1 top with the ball, O5 RIGHT elbow, O4 LEFT elbow, O3 RIGHT corner, O2 LEFT corner. X1..X5 guard O1..O5.
  Shared (0 - FORK): O1 walks the ball up, the bigs and the corners settle (Horns 1-2-2), O5 walks up and PLANTS a
  ball screen on X1's right hip, O1 dribbles off O5's right shoulder, X1 fights over the top and trails, X5 steps out
  and contains the ball (show), O5 opens and ROLLS to the rim, O4 POPS from the left elbow behind the arc.
  FORK = the one decision frame: X4 (O4's man) is in the gap between the roller and the popper.
  A horns-rp-a-help  X4 TAGS the roll (steps into O5's lane) -> O1 throws the overhead kick-out to O4, catch and
                     shoot behind the arc, X4 closes out late.
  B horns-rp-b-stay  X4 STAYS with O4 -> X5 still on the ball, X1 still behind: O1 bounces it to O5 rolling,
                     O5 finishes at the rim (V3.3 has no layup primitive: a two-foot power finish from 1.4 m).
Tracks are sampled here (Catmull-Rom path + Hermite speed profile, every 0.1 s) so a run can CROSS the fork at speed
and continue differently in each branch; every sample before the fork is the same in A and B.
  python3 tactical/specs/_gen-horns-roll-pop.py -> tactical/plays/horns-rp-a-help.json, horns-rp-b-stay.json"""
import copy, json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
R4 = lambda v: round(v, 4)
DT = 0.1

SRC = ("original E2A possession (Horns 1-2-2: high ball screen, the screener rolls, the opposite elbow pops; "
       "generic coaching knowledge checked against FIBA Europe coaching 'Horns', The Hoops Geek 'Horns PnR/PnP' "
       "(2025-06-18) and Basketball for Coaches 'Horns Pick and Roll'; no diagram or track copied)")

# ------------------------------------------------------------------ spots
RIGHT_ELBOW, LEFT_ELBOW = (-2.45, 5.85), (2.45, 5.85)
TOP = (0.35, 9.5)          # O1 after the set-up step (to his left, the screen comes from his right)
X1_SET = (0.3, 8.55)       # X1 in front of O1
SC = (-0.5, 8.23)          # O5's screen: on X1's right hip (0.86 m), feet planted
OP = (-3.0, 8.0)           # where O1 is stopped by X5's show (above the right elbow extended)
X5_SHOW = (-3.6, 7.35)     # X5 in front of the drive, on O1's downhill side
POP = (4.95, 6.9)          # O4's pop: left slot, 7.27 m from the basket (FIBA arc 6.75 m)
GAP = (2.3, 5.35)          # X4 in the gap between the roll and the pop
FORK = 6.75

# ------------------------------------------------------------------ motion primitives


def catmull(pts, n=40):
    """smooth path through the control points (centripetal-ish uniform Catmull-Rom), dense samples"""
    if len(pts) == 2:
        return [(pts[0][0] + (pts[1][0] - pts[0][0]) * i / n, pts[0][1] + (pts[1][1] - pts[0][1]) * i / n) for i in range(n + 1)]
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for k in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[k - 1], P[k], P[k + 1], P[k + 2]
        for i in range(n):
            u = i / n
            u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u3) for j in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def arclen(path):
    s = [0.0]
    for a, b in zip(path, path[1:]):
        s.append(s[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return s


def at_s(path, S, s):
    s = max(0.0, min(S[-1], s))
    i = 1
    while i < len(S) - 1 and S[i] < s:
        i += 1
    a, b = path[i - 1], path[i]
    w = (s - S[i - 1]) / max(1e-9, S[i] - S[i - 1])
    return (a[0] + (b[0] - a[0]) * w, a[1] + (b[1] - a[1]) * w)


class Mover:
    """one player's sampled track: stand / move(t0, t1, pts, v0, v1)"""

    def __init__(self, start):
        self.wp = [[0.0, start[0], start[1]]]
        self.pos = tuple(start)
        self.t = 0.0
        self.v = 0.0

    def move(self, t0, t1, pts, v0=0.0, v1=0.0):
        assert t0 >= self.t - 1e-9, (t0, self.t)
        assert abs(v0 - self.v) < 1e-6 or t0 > self.t + 1e-9 and v0 == 0, ('speed jump', v0, self.v)
        if t0 > self.t + 1e-9:
            assert self.v == 0, 'stopped mid-run'
            self.wp.append([R4(t0), R4(self.pos[0]), R4(self.pos[1])])
        path = catmull([self.pos] + list(pts))
        S = arclen(path)
        L, Tm = S[-1], t1 - t0
        assert v0 * Tm <= 3 * L + 1e-6 and v1 * Tm <= 3 * L + 1e-6, ('overshoot', pts, v0, v1, L, Tm)
        n = max(2, int(round(Tm / DT)))
        for i in range(1, n + 1):
            u = i / n
            h10, h01, h11 = u ** 3 - 2 * u * u + u, -2 * u ** 3 + 3 * u * u, u ** 3 - u * u
            s = h10 * Tm * v0 + h01 * L + h11 * Tm * v1
            p = at_s(path, S, s)
            self.wp.append([R4(t0 + Tm * u), R4(p[0]), R4(p[1])])
        self.pos, self.t, self.v = tuple(pts[-1]), t1, v1
        return self

    def hold(self, t):
        assert self.v == 0
        if t > self.t + 1e-9:
            self.wp.append([R4(t), R4(self.pos[0]), R4(self.pos[1])])
            self.t = t
        return self

    def at(self, t):
        for a, b in zip(self.wp, self.wp[1:]):
            if a[0] <= t <= b[0]:
                w = (t - a[0]) / max(1e-9, b[0] - a[0])
                return (a[1] + (b[1] - a[1]) * w, a[2] + (b[2] - a[2]) * w)
        return tuple(self.wp[-1][1:])


def shared():
    """every player's track from 0 to the fork (runs that cross the fork end AT the fork with their speed)"""
    m = {}
    # O1 walks the ball up and sets his man up (a step to his left), then uses the screen to his right
    m["O1"] = Mover((0.45, 11.7)).move(0.3, 2.7, [(0.1, 10.3), (0.0, 9.55)]).move(3.35, 3.95, [TOP])
    m["O1"].move(5.25, 6.6, [(-0.65, 9.22), (-1.9, 8.78), OP])
    # X1 picks him up in front, mirrors the set-up step, fights OVER the top of the screen and trails
    # (gap to O1 1.45 m -> 1.0 m only at the arrival: a 1.0 m gap on the move put O1's dribble into X1's thigh, QC 1.6 s)
    m["X1"] = Mover((0.42, 10.25))
    for w in m["O1"].wp:
        if 0.3 < w[0] <= 2.7 + 1e-9:
            u = min(1.0, max(0.0, (w[0] - 2.1) / 0.6))
            u = u * u * (3 - 2 * u)
            m["X1"].wp.append([w[0], R4(w[1] - 0.03 + 0.05 * u), R4(w[2] - 1.45 + 0.45 * u)])
    m["X1"].pos, m["X1"].t = tuple(m["X1"].wp[-1][1:]), 2.7
    m["X1"].move(3.45, 4.05, [X1_SET])
    m["X1"].move(5.5, 6.95, [(0.05, 9.4), (-0.95, 9.85), (-2.05, 9.45), (-2.85, 8.95)])
    # the bigs settle at the elbows (from above, never under the rim), then O5 walks up and plants the screen
    m["O5"] = Mover((-2.05, 7.0)).move(1.0, 2.2, [RIGHT_ELBOW]).move(3.9, 5.1, [(-1.7, 7.15), SC])
    m["O5"].move(6.0, FORK, [(-0.85, 7.35), (-0.92, 6.5)], 0.0, 4.4)
    m["O4"] = Mover((2.1, 7.0)).move(0.8, 2.0, [LEFT_ELBOW]).move(6.0, 7.15, [(3.6, 6.3), POP])
    # bigs' defenders: in the lane side of their man, X5 follows O5 up (level of the screen), then shows on the ball
    m["X5"] = Mover((-1.6, 5.9)).move(1.2, 2.4, [(-1.95, 4.95)]).move(4.1, 5.2, [(-1.75, 6.3), (-1.45, 7.15)])
    m["X5"].move(5.55, 6.5, [(-2.45, 7.3), X5_SHOW])
    m["X4"] = Mover((1.65, 5.95)).move(1.05, 2.25, [(1.95, 4.95)]).move(6.05, 6.6, [GAP])
    # corners: fill, then stay alive with small shifts at different times (never sync, never into the paint)
    m["O2"] = Mover((6.35, 2.05)).move(0.6, 1.6, [(6.6, 1.3)]).move(4.4, 5.0, [(6.5, 1.5)]).move(6.2, 6.7, [(6.6, 1.35)])
    m["X2"] = Mover((5.4, 2.4)).move(0.85, 1.85, [(5.7, 1.95)]).move(4.6, 5.15, [(5.6, 2.1)]).move(6.4, FORK, [(5.75, 2.0)])
    m["O3"] = Mover((-6.3, 2.1)).move(0.4, 1.5, [(-6.6, 1.3)]).move(5.1, 5.7, [(-6.45, 1.55)])
    m["X3"] = Mover((-5.35, 2.4)).move(0.7, 1.7, [(-5.7, 1.95)]).move(5.25, 5.85, [(-5.55, 2.15)])
    return m


def branch(kind):
    m = shared()
    if kind == "help":
        # X4 TAGS the roll: two hard steps into O5's lane, between him and the rim; O5 is slowed and stops
        m["O5"].move(FORK, 7.3, [(-0.78, 5.5), (-0.7, 4.78)], 4.4, 0.0).move(8.4, 8.9, [(-0.6, 4.35)])
        m["X4"].move(6.8, 7.7, [(1.0, 4.6), (-0.12, 4.18)])
        PICK, PASS, CATCH = 7.4, 7.55, 8.2
        GATHER, MAKE = CATCH + 0.45, CATCH + 0.45 + 1.05
        # the closeout starts 0.4 s after the ball leaves O1 (he reads the pass), arrives after the release
        m["X4"].move(PASS + 0.4, PASS + 1.55, [(1.6, 5.4), (3.95, 6.08)])
        m["X5"].move(7.95, 9.1, [(-2.6, 6.2), (-1.75, 5.25)])
        m["X1"].move(7.15, 7.7, [(-2.65, 8.5)])
        m["X2"].move(8.0, 8.5, [(5.6, 2.15)])
        END = 10.4
        # same live dribble as B up to PICK (the read), then O1 picks it up for the two-hand overhead kick-out
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": PICK, "dribble": True, "hand": 0},
                {"type": "hold", "player": "O1", "from": PICK, "to": PASS, "pocket": True},
                {"type": "pass", "from": "O1", "to": "O4", "t0": PASS, "t1": CATCH, "style": "overhead"},
                {"type": "hold", "player": "O4", "from": CATCH, "to": GATHER},
                {"type": "shot", "player": "O4", "t0": GATHER, "t1": MAKE, "make": True}]
        acts = {"X4": [{"type": "stance", "from": 0, "to": 6.8, "face": "O4"},
                       {"type": "stance", "from": 6.8, "to": PASS + 0.4, "face": "O5"},
                       {"type": "closeout", "from": PASS + 0.4, "to": PASS + 1.55},
                       {"type": "contest", "from": PASS + 1.55, "to": MAKE}],
                "O4": [{"type": "face", "from": 0, "to": 6.6, "face": "ball"},
                       {"type": "catchReady", "from": 6.9, "to": CATCH, "face": "O1"},
                       {"type": "face", "from": MAKE, "to": END, "face": "ball"}],
                "O5": [{"type": "face", "from": 0, "to": 5.1, "face": "ball"},
                       {"type": "screen", "from": 5.15, "to": 5.95, "face": "X1"},
                       {"type": "face", "from": 6.0, "to": END, "face": "ball"}]}
        marks = {"helpTag": 6.8, "kickOut": PASS, "popCatch": CATCH, "popRelease": GATHER, "make": MAKE}
        claims = [
            {"type": "near", "a": "X4", "b": "O5", "at": "kickOut", "max": 1.6, "says": "If he tags the roll,"},
            {"type": "far", "a": "X4", "b": "O4", "at": "kickOut", "min": 3.0, "says": "Four is open"},
            {"type": "behind_arc", "player": "O4", "at": "popRelease", "says": "open for three"},
            {"type": "open", "player": "O4", "at": "popRelease", "min": 1.8, "says": "Four is open for three"},
            {"type": "reacts_after", "player": "X4", "event": "decision", "min": 0.03, "says": "the help comes from the decision frame"},
            {"type": "order", "marks": ["screenSet", "screenUse", "rollPop", "decision", "helpTag", "kickOut", "popCatch", "popRelease", "make"],
             "says": "screen, roll + pop, the help, the kick-out, the three"}]
        meta = {"id": "horns-rp-a-help", "title": "HORNS roll + pop, A: X4 tags the roll, kick-out to the pop, three",
                "branch": {"group": "horns-roll-pop", "read": "HELP", "result": "three_point_shot", "reader": "X4", "fork": FORK,
                           "offenceSharedUntil": FORK, "payoff": {"type": "shot", "three": True, "make": True, "t": MAKE}}}
    else:
        # X4 STAYS with O4: he follows the pop and stays a step off him; the roll is left to X5 (still on the ball)
        m["X4"].move(6.8, 7.55, [(3.3, 5.75), (4.12, 6.2)])
        # O5 keeps rolling, slows into the catch, gathers and finishes off two feet
        # he rolls hard, then opens his chest to the passer (O1 is BEHIND him, up-court right) and shows his hands: a
        # catch on the run with the back to the ball flew the pass through his head (QC 7.97 s); then one gather step
        m["O5"].move(FORK, 7.75, [(-0.78, 5.2), (-0.56, 3.55)], 4.4, 0.0).move(8.15, 8.63, [(-0.36, 2.85)])
        PICK, PASS, CATCH = 7.4, 7.55, 8.0
        GATHER = 8.85      # 0.85 s after the catch: a full two-foot power finish, not the quick low jump
        MAKE = GATHER + 0.45
        m["X5"].move(7.55, 8.65, [(-2.45, 6.0), (-1.4, 4.55)])
        m["X1"].move(7.45, 8.05, [(-2.6, 8.45)])
        m["X3"].move(7.85, 8.4, [(-5.25, 2.25)])     # a look at the roll, never leaves the corner
        END = 9.9
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": PICK, "dribble": True, "hand": 0},
                {"type": "hold", "player": "O1", "from": PICK, "to": PASS, "pocket": True},
                {"type": "pass", "from": "O1", "to": "O5", "t0": PASS, "t1": CATCH, "style": "chest"},
                {"type": "hold", "player": "O5", "from": CATCH, "to": GATHER},
                {"type": "layup", "player": "O5", "t0": GATHER, "t1": MAKE, "make": True}]
        acts = {"X4": [{"type": "stance", "from": 0, "to": END, "face": "O4"}],
                "O4": [{"type": "face", "from": 0, "to": END, "face": "ball"}],
                "O5": [{"type": "face", "from": 0, "to": 5.1, "face": "ball"},
                       {"type": "screen", "from": 5.15, "to": 5.95, "face": "X1"},
                       {"type": "catchReady", "from": 6.9, "to": CATCH, "face": "O1"},
                       {"type": "face", "from": MAKE, "to": END, "face": "ball"}]}
        marks = {"stay": 6.8, "rollPass": PASS, "rollCatch": CATCH, "finish": GATHER, "make": MAKE}
        claims = [
            {"type": "near", "a": "X4", "b": "O4", "at": "rollCatch", "max": 1.8, "says": "If he stays with Four,"},
            {"type": "far", "a": "X4", "b": "O5", "at": "rollCatch", "min": 3.5, "says": "the pass inside might be there"},
            {"type": "far", "a": "X5", "b": "O5", "at": "rollCatch", "min": 2.0, "says": "X5 is still on the ball"},
            {"type": "far", "a": "X1", "b": "O1", "at": "decision", "min": 1.0, "says": "X1 is still behind"},
            {"type": "near_rim", "player": "O5", "at": "finish", "max": 1.6, "says": "finish near the rim"},
            {"type": "order", "marks": ["screenSet", "screenUse", "rollPop", "decision", "stay", "rollPass", "rollCatch", "finish", "make"],
             "says": "screen, roll + pop, X4 stays, the pass inside, the finish"}]
        meta = {"id": "horns-rp-b-stay", "title": "HORNS roll + pop, B: X4 stays with the pop, pass to the roll",
                "branch": {"group": "horns-roll-pop", "read": "STAY", "result": "rim_finish", "reader": "X4", "fork": FORK,
                           "offenceSharedUntil": FORK, "payoff": {"type": "layup", "make": True, "t": MAKE}}}
    for p in m.values():
        if p.v == 0:
            p.hold(END)
    for pid, p in m.items():
        assert abs(p.v) < 1e-9, (pid, 'still running at the end')
    base_acts = {
        "X1": [{"type": "stance", "from": 0, "to": END, "face": "O1"}],
        "X2": [{"type": "stance", "from": 0, "to": END, "face": "O2"}],
        "X3": [{"type": "stance", "from": 0, "to": END, "face": "O3"}],
        "X5": [{"type": "stance", "from": 0, "to": 5.5, "face": "O5"}, {"type": "stance", "from": 5.5, "to": 7.6, "face": "O1"},
               {"type": "stance", "from": 7.6, "to": END, "face": "O5"}],
        "O2": [{"type": "face", "from": 0, "to": END, "face": "ball"}],
        "O3": [{"type": "face", "from": 0, "to": END, "face": "ball"}],
    }
    base_acts.update(acts)
    play = {
        **meta, "duration": END, "concept": "horns-high-pnr-roll-opposite-pop", "source": SRC,
        "v33": "compile", "v33profile": {"O4": {"intensity": 1.08}, "O5": {"intensity": 1.08}}, "squareUp": True, "catchV2": 2, "handBallClear": True, "realism": 3,
        "players": [
            {"id": "O1", "team": "O", "role": "Point guard at the top: uses O5's screen going right, reads X4"},
            {"id": "O2", "team": "O", "role": "Left corner shooter: spacing, ties X2"},
            {"id": "O3", "team": "O", "role": "Right corner shooter: spacing, ties X3"},
            {"id": "O4", "team": "O", "role": "Left elbow big: NOT the screener, pops behind the arc"},
            {"id": "O5", "team": "O", "role": "Right elbow big: sets the ball screen on X1, rolls to the rim"},
            {"id": "X1", "team": "X", "role": "On the ball: fights over the screen, trails", "guards": "O1"},
            {"id": "X2", "team": "X", "role": "Left corner: stays home", "guards": "O2"},
            {"id": "X3", "team": "X", "role": "Right corner: stays home", "guards": "O3"},
            {"id": "X4", "team": "X", "role": "THE KEY DEFENDER: guards the popper, must choose help or stay", "guards": "O4"},
            {"id": "X5", "team": "X", "role": "Screener's man: shows and contains the ball, then recovers", "guards": "O5"},
        ],
        "tracks": {pid: p.wp for pid, p in m.items()},
        "ball": ball,
        "actions": base_acts,
        "screens": [],
        "marks": {"start": 0, "align": 2.4, "setUp": 3.35, "screenApproach": 3.9, "screenSet": 5.1, "screenUse": 5.25,
                  "rollPop": 6.0, "decision": FORK, **marks, "end": END},
        "claims": [
            {"type": "near", "a": "O5", "b": "X1", "at": "screenSet", "max": 1.0, "says": "The guard takes Five's screen."},
            {"type": "far", "a": "O4", "b": "O5", "at": "decision", "min": 5.0, "says": "Five rolls, Four pops: the bigs split"},
            {"type": "near", "a": "X5", "b": "O1", "at": "decision", "max": 1.2, "says": "X5 contains the ball"},
            *claims],
        "notes": ["Horns 1-2-2: O1 top, O4/O5 elbows, O2/O3 corners; O5 screens X1 and rolls, O4 pops (the OTHER big).",
                  "Shared to the fork (%.2f s): X4 in the gap between the roll and the pop." % FORK,
                  "Coverage is illustrative (X5 shows/contains, X1 over the top), not 'what every defence does'."],
    }
    return play


if __name__ == "__main__":
    A, B = branch("help"), branch("stay")
    # the shared part must be sample-identical: compare every waypoint up to the fork
    for pid in A["tracks"]:
        a = [w for w in A["tracks"][pid] if w[0] <= FORK + 1e-9]
        b = [w for w in B["tracks"][pid] if w[0] <= FORK + 1e-9]
        assert a == b, pid
    for p in (A, B):
        out = os.path.join(T, "tactical", "plays", p["id"] + ".json")
        json.dump(p, open(out, "w"), indent=1)
        print("built", p["id"], p["duration"], "s")
