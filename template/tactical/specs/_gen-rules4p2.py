#!/usr/bin/env python3
"""E2A 4 BASKETBALL RULES, PART 2 (owner brief 2026-11-25): 8 seconds, backcourt, offensive 3 seconds, goaltending.
One tiny play per rule, checked against the FIBA Official Basketball Rules (Art. 28, 30, 26, 31). Original E2A
choreography. Same engine and opt-ins as Part 1 (tactical/specs/_gen-rules4.py).

Court: offence attacks the basket at (0, 1.575), y from that baseline; FULL court (`court: 'full'`) for 8 s / backcourt:
the half-court line is y = 14, the offence's backcourt is y 14..28. x < 0 = right of the screen at yaw 0.
  rules4p2-eight      O1 brings the ball up against X1's pressure. The count is already at 5 when the clip opens (the
                      edit says so); 6, 7, 8 run in real time. At 8 the ball has bounced in the frontcourt and his left
                      foot is over the line, but his right foot is still in the backcourt: a dribbler is in the frontcourt
                      only when BOTH feet AND the ball touch it (Art. 28.1.3) -> 8-second violation.
  rules4p2-back       O1 dribbles in the frontcourt (team control there), picks up, passes back over the half-court line;
                      O2, a team-mate standing in the backcourt, is the first to touch it -> backcourt violation (Art. 30:
                      last touched by the team in the frontcourt, first touched by the team in the backcourt). No defender
                      touches the ball; X1 guards O1 away from the passing lane.
  rules4p2-three      O1 dribbles at the top, O5 walks into the restricted area and stays (small posture shifts, no
                      attempt to leave, no shot, team in control of a live ball in the frontcourt, game clock running)
                      -> offensive 3 seconds after more than 3 consecutive seconds (Art. 26).
  rules4p2-goal       O1 shoots a two (4.3 m). On the way DOWN, with the ball entirely above the ring and still able to
                      enter the basket, X5 jumps and touches it -> goaltending, the basket counts: +2 (Art. 31.2.1 and
                      31.3.1). Not basket interference: the ball has not touched the ring, nobody reaches through it.
  python3 tactical/specs/_gen-rules4p2.py -> tactical/plays/rules4p2-*.json"""
import json, math, os, sys

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, D)
R4 = lambda v: round(v, 4)
BASKET = (0.0, 1.575)
SRC = "original E2A rule demonstration (FIBA Official Basketball Rules: Art. 26, 28, 30, 31)"
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


def cruise(pts, dur, t0, t1, dt=0.1, ease=0.6):
    """constant-speed move with short ease-in / ease-out (a run that keeps its pace, unlike min-jerk)"""
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    L = sum(segs)
    T = t1 - t0
    v = L / (T - ease / 2)  # trapezoid: accel ease/2, cruise, decel ease/2

    def s_of(t):
        if t <= t0:
            return 0.0
        if t >= t1:
            return L
        u = t - t0
        a = v / (ease / 2)
        if u < ease / 2:
            return 0.5 * a * u * u
        if u > T - ease / 2:
            w = T - u
            return L - 0.5 * a * w * w
        return 0.5 * a * (ease / 2) ** 2 + v * (u - ease / 2)

    out = []
    t = 0.0
    while t <= dur + 1e-9:
        s = s_of(t)
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


def legs(parts, dur, dt=0.1):
    """several min-jerk legs [(pts, t0, t1), ...] back to back: stops at each corner (no instant turn)"""
    tr = [run(pts, dur, t0, t1, dt) for pts, t0, t1 in parts]
    out = []
    for i, row in enumerate(tr[0]):
        t = row[0]
        k = 0
        for j, (_, t0, _) in enumerate(parts):
            if t >= t0:
                k = j
        out.append(tr[k][i])
    return out


def heading(a, b):
    return math.atan2(b[1] - a[1], b[0] - a[0])


def play(pid, title, dur, players, tracks, ball, actions, marks, notes, **kw):
    p = {"id": pid, "title": title, "branch": {"group": "rules4p2"}, "duration": dur, "concept": pid,
         "source": SRC, **BASE, "players": players, "tracks": tracks, "ball": ball, "actions": actions, "screens": [],
         "marks": marks, "claims": [], "notes": notes}
    p.update({k: v for k, v in kw.items() if v is not None})
    return p


OUT = []
P = dict(a.split("=") for a in sys.argv[1:])
f = lambda k, d: float(P.get(k, d))

# ---------------------------------------------------------------- 1 EIGHT SECONDS (full court)
DUR = f("dur8", 5.35)
M = {"arrive": f("arrive", 5.0), "eight": f("eight", 3.867), "end": DUR}
O1S, O1E = (1.6, f("o1sy", 19.44)), (0.75, f("o1y", 12.54))
X1S, X1E = (1.2, f("x1sy", 18.1)), (0.55, f("x1y", 11.2))
OUT.append(play(
    "rules4p2-eight", "8 SECONDS: the dribbler is still straddling the half-court line when the 8 runs out", DUR,
    [{"id": "O1", "team": "O", "role": "Brings the ball up under pressure, straddles the line at 8"},
     {"id": "X1", "team": "X", "role": "Pressures the ball all the way (never touches it)", "guards": "O1"}],
    {"O1": cruise([O1S, O1E], DUR, 0.0, M["arrive"]),
     "X1": cruise([X1S, X1E], DUR, 0.0, M["arrive"] - 0.15)},
    [{"type": "hold", "player": "O1", "from": 0, "to": DUR, "dribble": True, "hand": 1}],
    {"O1": [{"type": "face", "from": 0, "to": DUR, "face": R4(heading(O1S, O1E))}],
     "X1": [{"type": "face", "from": 0, "to": DUR, "face": R4(heading(X1E, O1E))}]},
    M,
    ["Count already at 5 when the clip starts (labelled in the edit); 6/7/8 in real time.",
     "At 8 (" + str(M["eight"]) + " s): ball bounces at y 13.64, left foot planted over the line (13.67-13.86), right foot still behind it (14.16-14.35) -> not yet in the "
     "frontcourt (Art. 28.1.3) -> 8-second violation."],
    court="full",
    v33extra=({"O1": [{"k": "step", "side": int(f("side", 0)), "lift": R4(M["arrive"] - 0.1), "land": R4(M["arrive"] + 0.18),
                       "f": f("lf", 0.42), "l": 0.05, "h": 0.1}]} if f("lf", 0) > 0 else None),
    v33still={"O1": [[R4(M["arrive"] - 0.1), DUR]], "X1": [[R4(M["arrive"]), DUR]]}))

# ---------------------------------------------------------------- 2 BACKCOURT (full court)
DUR = 4.4
M = {"pick": f("pick", 1.25), "pass": f("bpass", 1.75), "catch": f("bcatch", 2.5), "end": DUR}
O1B, O2B = (2.4, f("o1by", 11.3)), (-2.6, f("o2by", 17.6))
X1B = (1.4, 9.4)
OUT.append(play(
    "rules4p2-back", "BACKCOURT: frontcourt control, pass back over the line, a team-mate in the backcourt touches it first", DUR,
    [{"id": "O1", "team": "O", "role": "Has the ball in the frontcourt, passes it back over the line"},
     {"id": "O2", "team": "O", "role": "Team-mate in the backcourt, first to touch it (illegal)"},
     {"id": "X1", "team": "X", "role": "Guards O1 from the basket side, away from the passing lane", "guards": "O1"}],
    {"O1": run([(2.9, 10.4), O1B], DUR, 0.0, M["pick"]),
     "O2": still(O2B[0], O2B[1], DUR),
     "X1": run([(1.7, 8.6), X1B], DUR, 0.0, M["pick"])},
    [{"type": "hold", "player": "O1", "from": 0, "to": M["pick"], "dribble": True, "hand": 1},
     {"type": "hold", "player": "O1", "from": M["pick"], "to": M["pass"]},
     {"type": "pass", "from": "O1", "to": "O2", "t0": M["pass"], "t1": M["catch"], "style": "chest"},
     {"type": "hold", "player": "O2", "from": M["catch"], "to": DUR}],
    {"O1": [{"type": "face", "from": 0, "to": M["pick"], "face": R4(heading((2.9, 10.4), O1B))},
            {"type": "face", "from": M["pick"], "to": DUR, "face": R4(heading(O1B, O2B))}],
     "O2": [{"type": "face", "from": 0, "to": DUR, "face": R4(heading(O2B, O1B))}],
     "X1": [{"type": "face", "from": 0, "to": DUR, "face": "O1"}]},
    M,
    ["O1 has both feet and the ball in the frontcourt (team control there) and is the last to touch it there.",
     "O2 stands in the backcourt (y > 14) and is the first to touch it -> backcourt violation (Art. 30)."],
    court="full"))

# ---------------------------------------------------------------- 3 OFFENSIVE THREE SECONDS (half court)
DUR = 6.4
# 'enter' = first frame a foot of O5 touches the restricted area (lines included), measured on the V3.3 bodies
M = {"enter": f("enter", 0.78), "settle": 1.65, "one": None, "two": None, "three": None, "viol": None, "end": DUR}
for i, k in enumerate(("one", "two", "three")):
    M[k] = R4(M["enter"] + i + 1)
M["viol"] = R4(M["enter"] + 3.1)  # MORE than 3 consecutive seconds
O1H = [(-1.2, 8.7), (0.9, 8.5), (-0.6, 8.8)]
O5S, O5P = (3.6, 5.0), (0.75, 3.7)
OUT.append(play(
    "rules4p2-three", "OFFENSIVE 3 SECONDS: O5 stays in the restricted area while his team has the ball", DUR,
    [{"id": "O1", "team": "O", "role": "Keeps the ball at the top (live ball, team control)"},
     {"id": "O5", "team": "O", "role": "Steps into the paint and stays there (illegal after 3 s)"},
     {"id": "X1", "team": "X", "role": "Guards O1", "guards": "O1"},
     {"id": "X5", "team": "X", "role": "Guards O5 from the basket side", "guards": "O5"}],
    {"O1": legs([([O1H[0], O1H[1]], 0.2, 2.3), ([O1H[1], O1H[2]], 2.55, 4.7)], DUR),
     "O5": run([O5S, O5P], DUR, 0.2, 1.6),
     "X1": legs([([(-1.0, 7.4), (0.7, 7.25)], 0.3, 2.4), ([(0.7, 7.25), (-0.5, 7.5)], 2.65, 4.8)], DUR),
     "X5": run([(2.6, 3.6), (0.6, 2.75)], DUR, 0.3, 1.65)},
    [{"type": "hold", "player": "O1", "from": 0, "to": DUR, "dribble": True, "hand": 1}],
    {"O1": [{"type": "face", "from": 0, "to": DUR, "face": R4(heading((0, 8.7), BASKET))}],
     "O5": [{"type": "face", "from": 0, "to": M["settle"], "face": R4(heading(O5S, O5P))},
            {"type": "face", "from": M["settle"], "to": DUR, "face": R4(heading(O5P, (0, 8.7)))}],
     "X1": [{"type": "face", "from": 0, "to": DUR, "face": "O1"}],
     "X5": [{"type": "face", "from": 0, "to": DUR, "face": "O5"}]},
    M,
    ["O5's both feet are inside the restricted area from 'enter'; his team controls a live ball in the frontcourt, the game clock runs.",
     "No attempt to leave, no shot, not dribbling to shoot -> violation after more than 3 consecutive seconds (Art. 26)."],
    v33still={"O5": [[1.65, DUR]]}))

# ---------------------------------------------------------------- 4 GOALTENDING (half court)
DUR = 4.0
M = {"release": f("release", 1.25), "land": f("land", 2.1), "touch": f("touch", 2.03), "end": DUR}
# 'contact' = first frame X5's palm is on the ball (palm-to-centre 0.14 m), measured on the V3.3 bodies: ball centre 3.31 m
# (bottom 3.19 > ring 3.05), falling at 2.9 m/s, 0.31 m from the ring centre; the hand stays outside the cylinder
M["contact"] = f("contact", 2.033)
O1G = (-2.55, 4.95)
X5S, X5J = (1.25, 3.9), (f("x5x", 0.0), f("x5y", 2.35))
OUT.append(play(
    "rules4p2-goal", "GOALTENDING: X5 touches the shot on its way DOWN, entirely above the ring -> the two points count", DUR,
    [{"id": "O1", "team": "O", "role": "Shoots a two"},
     {"id": "X5", "team": "X", "role": "Jumps and touches the descending ball above the ring (illegal)", "guards": "O1"}],
    {"O1": still(O1G[0], O1G[1], DUR),
     "X5": run([X5S, X5J], DUR, 0.35, M["touch"] - 0.75)},
    [{"type": "hold", "player": "O1", "from": 0, "to": M["release"]},
     {"type": "shot", "player": "O1", "t0": M["release"], "t1": M["land"], "make": True}],
    {"O1": [{"type": "face", "from": 0, "to": DUR, "face": R4(heading(O1G, BASKET))}],
     "X5": [{"type": "face", "from": 0, "to": DUR, "face": R4(heading(X5J, O1G))}]},
    M,
    ["Ball descending, entirely above the ring (centre >= 3.05 + r), not yet touched the ring, still able to enter: "
     "X5's touch = goaltending, the basket counts (Art. 31.2.1, 31.3.1).",
     "The edit freezes at the touch and awards +2; the ball's later path is not shown."],
    v33extra={"X5": [{"k": "jumpshot", "release": R4(M["touch"] + f("tlead", 0.0)), "H": f("H", 0.65)}]},
    v33still={"X5": [[R4(M["touch"] - 0.75), DUR]]},
    v33grab=[{"player": "X5", "target": "ball", "hand": int(f("hand", 0)), "from": R4(M["touch"] - 0.32),
              "to": R4(M["touch"] + 0.3), "reach": f("reach", 0.9)}]))

for p in OUT:
    path = os.path.join(T, "tactical", "plays", p["id"] + ".json")
    json.dump(p, open(path, "w"), indent=1)
    print("wrote", path)
