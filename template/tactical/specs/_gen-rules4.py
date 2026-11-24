#!/usr/bin/env python3
"""E2A 4 BASKETBALL RULES (owner brief 2026-11-24 "4 RULES EVERY PLAYER MUST KNOW").
Rule demonstrations, one tiny play per demo (1-2 players), checked against the FIBA Official Basketball Rules
(Art. 16 value of goals, Art. 24 dribble, Art. 25 travelling, Art. 33/34 contact & personal foul, team-foul
penalty). Original E2A choreography: no track, drawing or timing of the reference video is copied.

Court: FIBA half court, metres, basket (0, 1.575), y from the baseline; x < 0 = right of the screen at yaw 0.
  rules-travel   O2 passes to O1 (both feet down at the catch). O1 LEGALLY front-pivots on the LEFT foot (right foot
                 steps around) to face the rim. Then, still holding the ball, he LIFTS the pivot foot and PUTS IT BACK
                 DOWN 0.3 m ahead = travelling (Art. 25: the pivot foot may be lifted, but must not return to the floor
                 before the ball leaves the hands for a pass or a shot). Unambiguous: no gather, no dribble.
  rules-dribble  O1 dribbles, ends the dribble (catches the ball with BOTH hands), holds it 1.3 s, then starts a NEW
                 dribble. Nobody else touches the ball = double dribble (Art. 24: no second dribble after the first one
                 ended, unless he lost control after a shot / touch / tap by an opponent etc.). No defender on screen.
  rules-ft       free throw from behind the FT line (5.8 m from the baseline): +1.
  rules-two      jump shot inside the arc (4.8 m from the basket): +2.
  rules-three    jump shot behind the arc (7.2 m): +3.
  rules-line     jump shot with the front toe ON the three-point line: the line is part of the two-point area -> +2.
  rules-foul     O1 drives, X1 grabs his waist with the left hand and holds him: illegal contact that restricts his
                 freedom of movement (holding) -> personal foul, NOT in the act of shooting.
  rules-throwin  consequence when the team is not in the team-foul penalty: throw-in from the sideline, no free throws.
  python3 tactical/specs/_gen-rules4.py -> tactical/plays/rules4-*.json"""
import json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
R4 = lambda v: round(v, 4)
BASKET = (0.0, 1.575)
SRC = "original E2A rule demonstration (FIBA Official Basketball Rules: Art. 16, 24, 25, 33, 34, team-foul penalty)"
BASE = {"v33": "compile", "squareUp": True, "catchV2": 2, "handBallClear": True, "realism": 3}


def still(x, y, dur):
    return [[0.0, R4(x), R4(y)], [R4(dur), R4(x), R4(y)]]


def run(pts, dur, t0=0.0, t1=None, dt=0.1):
    """minimum-jerk move along a polyline between t0 and t1, standing still before / after"""
    t1 = dur if t1 is None else t1
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    L = sum(segs)
    out = []
    t = 0.0
    while t <= dur + 1e-9:
        u = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
        s = L * (10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5)
        acc = 0.0
        p = pts[-1]
        for (a, b), sl in zip(zip(pts, pts[1:]), segs):
            if s <= acc + sl or sl == 0:
                k = 0 if sl == 0 else (s - acc) / sl
                p = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
                break
            acc += sl
        out.append([R4(t), R4(p[0]), R4(p[1])])
        t += dt
    return out


def heading(a, b):
    return math.atan2(b[1] - a[1], b[0] - a[0])


def play(pid, title, dur, players, tracks, ball, actions, marks, notes, **kw):
    p = {"id": pid, "title": title, "branch": {"group": "rules4"}, "duration": dur, "concept": "rules4-" + pid.split("-")[1],
         "source": SRC, **BASE, "players": players, "tracks": tracks, "ball": ball, "actions": actions, "screens": [],
         "marks": marks, "claims": [], "notes": notes}
    p.update(kw)
    return p


OUT = []

# ---------------------------------------------------------------- 1 TRAVELLING
O1T, O2T = (3.4, 7.7), (-0.6, 9.4)
DUR = 5.2
face_pass = heading(O1T, O2T)
face_rim = heading(O1T, BASKET)
turn = math.atan2(math.sin(face_rim - face_pass), math.cos(face_rim - face_pass))
M = {"pass": 0.45, "catch": 1.05, "pivot0": 1.6, "pivot1": 2.3, "lift": 3.0, "land": 3.42, "end": DUR}
# the body centre turns around the pivot point (ball of the left foot, measured on the V3.3 body: qc-rules4 dump) and
# drifts 0.15 m forward during the illegal step, so the pelvis stays over the base (both are 'stand' via v33still)
PV = (3.141, 7.558)
c, s_ = math.cos(turn), math.sin(turn)
v = (O1T[0] - PV[0], O1T[1] - PV[1])
C1 = (PV[0] + v[0] * c - v[1] * s_, PV[1] + v[0] * s_ + v[1] * c)
FW = (math.cos(face_rim), math.sin(face_rim))
C2 = (C1[0] + 0.15 * FW[0], C1[1] + 0.15 * FW[1])


def travel_track(dur):
    out = []
    t = 0.0
    while t <= dur + 1e-9:
        if t <= M["pivot0"]:
            p = O1T
        elif t <= M["pivot1"]:
            u = (t - M["pivot0"]) / (M["pivot1"] - M["pivot0"])
            u = u * u * (3 - 2 * u)
            a = turn * u
            p = (PV[0] + v[0] * math.cos(a) - v[1] * math.sin(a), PV[1] + v[0] * math.sin(a) + v[1] * math.cos(a))
        elif t <= M["lift"] + 0.05:
            p = C1
        elif t <= M["land"] + 0.1:
            u = (t - M["lift"] - 0.05) / (M["land"] + 0.05 - M["lift"])
            u = u * u * (3 - 2 * u)
            p = (C1[0] + (C2[0] - C1[0]) * u, C1[1] + (C2[1] - C1[1]) * u)
        else:
            p = C2
        out.append([R4(t), R4(p[0]), R4(p[1])])
        t += 0.05
    return out


OUT.append(play(
    "rules4-travel", "TRAVELLING: legal front pivot on the left foot, then the pivot foot is lifted and put back down", DUR,
    [{"id": "O1", "team": "O", "role": "Catches, pivots legally, then lifts and re-plants the pivot foot (travel)"},
     {"id": "O2", "team": "O", "role": "Passer"}],
    {"O1": travel_track(DUR), "O2": still(*O2T, DUR)},
    [{"type": "hold", "player": "O2", "from": 0, "to": M["pass"]},
     {"type": "pass", "from": "O2", "to": "O1", "t0": M["pass"], "t1": M["catch"], "style": "chest"},
     {"type": "hold", "player": "O1", "from": M["catch"], "to": DUR}],
    {"O1": [{"type": "face", "from": 0, "to": M["pivot0"], "face": "O2"}, {"type": "face", "from": M["pivot0"], "to": DUR, "face": R4(face_rim)}],
     "O2": [{"type": "face", "from": 0, "to": DUR, "face": "O1"}]},
    M,
    ["Both feet are on the floor at the catch: either foot may become the pivot (Art. 25).",
     "1.6-2.3 s: front pivot on the LEFT foot (legal), the right foot steps around.",
     "3.0 s the LEFT (pivot) foot lifts, 3.42 s it lands again 0.3 m ahead, the ball still in both hands = TRAVEL."],
    v33extra={"O1": [
        {"k": "pivot", "side": 0, "t0": M["pivot0"], "t1": M["pivot1"], "dyaw": R4(turn)},
        {"k": "step", "side": 1, "lift": M["pivot0"] + 0.02, "land": M["pivot1"] - 0.05, "f": -0.05, "l": 0.2, "h": 0.07, "toeOff": 0.2},
        {"k": "step", "side": 0, "lift": M["lift"], "land": M["land"], "f": 0.3, "l": -0.2, "h": 0.13, "heel": -0.06},
    ]},
    v33still={"O1": [[M["pivot0"] - 0.05, DUR]]}))

# ---------------------------------------------------------------- 2 DOUBLE DRIBBLE
A, B = (-2.6, 11.2), (-1.7, 8.0)
DUR = 5.4
M = {"stop": 2.0, "pickup": 2.05, "hold1": 3.35, "end": DUR}
OUT.append(play(
    "rules4-dribble", "DOUBLE DRIBBLE: dribble, two-hand pick-up, hold, dribble again (nobody else touches the ball)", DUR,
    [{"id": "O1", "team": "O", "role": "Dribbles, ends the dribble, holds, dribbles again (illegal)"}],
    {"O1": run([A, B], DUR, 0.0, M["stop"])},
    [{"type": "hold", "player": "O1", "from": 0, "to": M["pickup"], "dribble": True, "hand": 1},
     {"type": "hold", "player": "O1", "from": M["pickup"], "to": M["hold1"]},
     {"type": "hold", "player": "O1", "from": M["hold1"], "to": DUR, "dribble": True, "hand": 1}],
    {"O1": [{"type": "face", "from": 0, "to": DUR, "face": R4(heading(B, BASKET))}]},
    M,
    ["The dribble ends when he catches the ball with both hands (2.05 s, Art. 24).",
     "No shot, no touch by an opponent, no loss of control: a new dribble at 3.35 s is a double dribble."]))

# ---------------------------------------------------------------- 3 SCORING


def shot_play(pid, title, spot, H, notes, t0=1.0, flight=1.05, dur=3.1):
    M = {"release": t0, "make": t0 + flight, "end": dur}
    return play(pid, title, dur, [{"id": "O1", "team": "O", "role": "Shooter"}], {"O1": still(*spot, dur)},
                [{"type": "hold", "player": "O1", "from": 0, "to": t0},
                 {"type": "shot", "player": "O1", "t0": t0, "t1": t0 + flight, "make": True, "H": H}],
                {"O1": [{"type": "face", "from": 0, "to": dur, "face": R4(heading(spot, BASKET))}]}, M, notes)


def at_r(r, deg):
    a = math.radians(deg)
    return (BASKET[0] + r * math.cos(a), BASKET[1] + r * math.sin(a))


FT = (0.0, 6.12)
TWO = (-3.3, 5.05)
THREE = (4.7, 7.3)
OUT.append(shot_play("rules4-ft", "FREE THROW: +1", FT, 0.05, ["Feet behind the free-throw line (5.80 m), set shot with a small rise."], flight=1.1))
OUT.append(shot_play("rules4-two", "INSIDE THE ARC: +2", TWO, 0.38, [f"{math.dist(TWO, BASKET):.2f} m from the basket, inside the 6.75 m arc."]))
OUT.append(shot_play("rules4-three", "BEYOND THE ARC: +3", THREE, 0.42, [f"{math.dist(THREE, BASKET):.2f} m from the basket, both feet behind the arc."], flight=1.15))
# the LINE: body centre placed so the front toe lands on the painted line (QC: scripts/qc-rules4.mts measures it)
LINE_R = float(os.environ.get("RULES4_LINE_R", "6.93"))
LINE = at_r(LINE_R, 116)
OUT.append(shot_play("rules4-line", "ON THE LINE: still +2", LINE, 0.36,
                     ["The three-point line is NOT part of the three-point field goal area (Art. 16): a foot on it = 2 points.",
                      f"Body centre {LINE_R} m from the basket, toe on the line (measured)."], t0=1.5, dur=3.6))

# ---------------------------------------------------------------- 4 FOUL (holding) + THROW-IN
DUR = 4.4
O1a, O1b = (2.2, 8.6), (4.2, 6.2)
X1a, X1b = (1.7, 7.5), (3.62, 6.3)
M = {"drive": 0.55, "grab": 1.05, "stopped": 1.75, "end": DUR}
OUT.append(play(
    "rules4-foul", "HOLDING: X1 grabs O1's waist on the drive and stops him (personal foul, no shot)", DUR,
    [{"id": "O1", "team": "O", "role": "Drives to his right with the ball"},
     {"id": "X1", "team": "X", "role": "Grabs and holds the driver (illegal)", "guards": "O1"}],
    {"O1": run([O1a, O1b], DUR, M["drive"], M["stopped"] + 0.15), "X1": run([X1a, X1b], DUR, M["drive"] + 0.05, M["stopped"])},
    [{"type": "hold", "player": "O1", "from": 0, "to": M["drive"]},
     {"type": "hold", "player": "O1", "from": M["drive"], "to": M["stopped"] + 0.2, "dribble": True, "hand": -1},
     {"type": "hold", "player": "O1", "from": M["stopped"] + 0.2, "to": DUR}],
    {"O1": [{"type": "face", "from": 0, "to": DUR, "face": R4(heading(O1b, BASKET))}], "X1": [{"type": "stance", "from": 0, "to": DUR, "face": "O1"}]},
    M,
    ["Holding: illegal personal contact that restricts the freedom of movement (Art. 33/34).",
     "Not in the act of shooting: if the team is not in the team-foul penalty, the game resumes with a throw-in."],
    v33grab=[{"player": "X1", "target": "O1", "hand": 0, "from": M["grab"], "to": DUR, "reach": 0.72, "z": 0.12}]))

DUR = 3.0
M = {"pass": 1.0, "catch": 1.55, "end": DUR}
OUT.append(play(
    "rules4-throwin", "Consequence: throw-in from the sideline, no free throws", DUR,
    [{"id": "O1", "team": "O", "role": "Inbounder (out of bounds)"}, {"id": "O2", "team": "O", "role": "Receiver"}],
    {"O1": still(7.95, 8.4, DUR), "O2": run([(5.6, 9.6), (5.0, 8.7)], DUR, 0.2, 1.3)},
    [{"type": "hold", "player": "O1", "from": 0, "to": M["pass"]},
     {"type": "pass", "from": "O1", "to": "O2", "t0": M["pass"], "t1": M["catch"], "style": "chest"},
     {"type": "hold", "player": "O2", "from": M["catch"], "to": DUR}],
    {"O1": [{"type": "face", "from": 0, "to": DUR, "face": "O2"}], "O2": [{"type": "face", "from": 0, "to": DUR, "face": "O1"}]},
    M, ["Sideline throw-in: the inbounder stands outside the court."]))

for p in OUT:
    json.dump(p, open(os.path.join(T, "tactical", "plays", p["id"] + ".json"), "w"), indent=1)
    print(p["id"], p["duration"])
print("travel turn (deg)", round(math.degrees(turn), 1))
