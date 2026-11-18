#!/usr/bin/env python3
"""THE EUROSTEP (owner brief 2026-11-18 20:25Z): one authored master take + the 'defender stays square' variant.
  python3 tactical/specs/_gen-eurostep.py   -> tactical/plays/euro-a.json, euro-b.json
Footwork is AUTHORED (src/t3d/choreo.ts), not gait-simulated: every plant has its own time and spot.
Directions are the ATTACKER's, facing the rim: he drives toward -y, so his LEFT = +x and his RIGHT = -x.
Count (FIBA 2026 art. 25.2.1 / NBA rule 10 XIII): the right foot is already down when the dribble ends (gather);
step 1 = the next foot to land (left), step 2 = the right; the right foot takes off, the ball leaves the right hand
before any foot lands again.
Both plays share every key up to the first counted step (same start, same approach, same fake)."""
import json, math, os

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(D), "plays")
PI = math.pi
H0 = -PI / 2          # attacker heading (toward the baseline)
HX = PI / 2           # defender heading (toward the attacker)
r3 = lambda v: round(v, 4)

# ---------------- milestones (play clock, seconds) ----------------
M = {"start": 0.0, "lastBounce": 1.2775, "rPlant": 1.33, "gather": 1.46, "step1": 1.62, "react": 1.72, "push1": 1.86,
     "step2": 1.98, "takeoff": 2.2, "release": 2.48, "land": 2.82, "glass": 2.98, "make": 3.16}


def lstep(foot, lift, land, x, y, yaw, **k):
    return {"foot": foot, "lift": lift, "land": land, "at": [x, y], "yaw": r3(yaw), **k}


# ---------------- attacker O1 (1.88 m, light guard) ----------------
O1_FEET0 = [[0.47, 10.45, r3(H0 + 0.12)], [0.2, 10.28, r3(H0 - 0.12)]]
O1_APPROACH = [
    lstep(0, 0.02, 0.30, 0.40, 9.72, H0 + 0.1),
    lstep(1, 0.20, 0.52, 0.22, 9.00, H0 - 0.1),
    lstep(0, 0.42, 0.74, 0.42, 8.15, H0 + 0.1),
    lstep(1, 0.64, 0.96, 0.20, 7.25, H0 - 0.1),
    lstep(0, 0.86, 1.16, 0.42, 6.35, H0 + 0.1),
    lstep(1, 1.06, M["rPlant"], 0.22, 5.50, H0 - 0.08),                     # right foot down BEFORE the gather
    lstep(0, 1.25, M["step1"], 1.12, 4.58, H0 + 0.45, h=0.15),               # step 1: LEFT, toward the left lane
]
O1_A = O1_APPROACH + [
    lstep(1, 1.50, M["step2"], -0.68, 3.38, H0 - 0.25, h=0.17),            # step 2: RIGHT, the open lane
    lstep(0, M["push1"], M["land"], -0.36, 2.32, H0 + 0.05, h=0.3, drive=0.9),  # left knee drives, lands after the release
    lstep(1, M["takeoff"], 2.90, -0.66, 2.18, H0 - 0.1, h=0.25),            # take-off foot
]
O1_B = O1_APPROACH + [
    lstep(1, 1.50, M["step2"], -0.32, 3.9, H0 - 0.2, h=0.16),             # shorter step 2: the lane is not there
    lstep(0, M["push1"], 4.2, 0.1, 3.95, H0 + 0.05, h=0.32, drive=0.7, hover=0.3),   # balanced on the 2nd step, left foot stays up
]
# pelvis keys [t, x, y, z]
O1_PEL_COMMON = [
    [0.00, 0.33, 10.25, 0.95], [0.30, 0.32, 9.62, 0.91], [0.52, 0.31, 8.93, 0.905], [0.74, 0.32, 8.10, 0.9],
    [0.96, 0.30, 7.22, 0.9], [1.16, 0.33, 6.38, 0.9], [1.33, 0.30, 5.62, 0.885], [1.46, 0.38, 5.16, 0.875],
    [1.62, 0.72, 4.76, 0.86], [1.72, 0.84, 4.55, 0.8],
]


def jump(t0, z0, t1, z1, x0, y0, x1, y1, n=8):
    """ballistic pelvis between take-off and touch-down (exact parabola, constant horizontal speed)"""
    T = t1 - t0
    vz = (z1 - z0 + 0.5 * 9.8 * T * T) / T
    out = []
    for i in range(1, n):
        u = i / n
        tt = T * u
        out.append([r3(t0 + tt), r3(x0 + (x1 - x0) * u), r3(y0 + (y1 - y0) * u), r3(z0 + vz * tt - 4.9 * tt * tt)])
    return out


O1_PEL_A = O1_PEL_COMMON + [[1.86, 0.64, 4.2, 0.84], [1.98, -0.12, 3.62, 0.84], [2.08, -0.42, 3.4, 0.78],
                            [2.20, -0.58, 3.14, 0.97]] + jump(2.20, 0.97, 2.82, 0.95, -0.58, 3.14, -0.52, 2.36) + \
           [[2.82, -0.52, 2.36, 0.95], [2.95, -0.51, 2.24, 0.8], [3.30, -0.49, 2.12, 0.9], [4.0, -0.46, 2.08, 0.94]]
O1_PEL_B = O1_PEL_COMMON + [[1.86, 0.6, 4.34, 0.85], [1.98, 0.05, 4.06, 0.86], [2.10, -0.18, 3.94, 0.8],
                            [2.35, -0.24, 3.9, 0.84], [3.6, -0.24, 3.9, 0.85]]
# body keys [t, heading, hipOff, chestOff, lean, roll]
O1_BODY_COMMON = [
    [0.0, H0, 0, 0, 0.22, 0], [1.33, H0, 0, 0, 0.3, 0], [1.46, H0 + 0.05, 0, 0.06, 0.27, 0.03],
    [1.62, H0 + 0.22, 0.05, 0.3, 0.17, 0.14], [1.75, H0 + 0.25, 0.05, 0.33, 0.14, 0.17],
]
O1_BODY_A = O1_BODY_COMMON + [[1.88, H0 + 0.05, -0.05, 0.05, 0.22, 0.02], [1.98, H0 - 0.25, -0.05, -0.35, 0.22, -0.14],
                              [2.10, H0 - 0.22, -0.05, -0.38, 0.24, -0.12], [2.20, H0 - 0.1, 0, -0.3, 0.1, -0.05],
                              [2.48, H0 - 0.05, 0, -0.2, 0.02, 0], [2.82, H0, 0, 0, 0.1, 0], [3.4, H0 + 0.15, 0, 0.1, 0.06, 0]]
O1_BODY_B = O1_BODY_COMMON + [[1.88, H0 + 0.05, -0.05, 0.05, 0.2, 0.02], [1.98, H0 - 0.15, -0.05, -0.25, 0.16, -0.08],
                              [2.15, H0 - 0.12, -0.04, -0.3, 0.12, -0.06], [3.6, H0 - 0.12, -0.04, -0.3, 0.12, -0.06]]
RIMP = [0, 1.575, 3.05]
LANE_L = [1.45, 2.2, 1.3]
O1_LOOK_A = [[0, 0.1, 2.6, 2.0], [1.44, 0.15, 2.4, 2.1], [1.58, *LANE_L], [1.8, *LANE_L], [1.98, *RIMP], [2.9, *RIMP], [3.4, 0, 3.5, 1.6]]
O1_LOOK_B = [[0, 0.1, 2.6, 2.0], [1.44, 0.15, 2.4, 2.1], [1.58, *LANE_L], [1.8, *LANE_L], [1.98, 0.1, 3.1, 1.6], [3.6, 0.1, 3.1, 1.6]]
# ball in O1's body frame [t, fwd, side(+ = his right), zRel to the pelvis]
O1_BALL_COMMON = [[M["gather"], 0.32, 0.22, 0.04], [1.62, 0.31, -0.08, 0.17], [1.75, 0.29, -0.13, 0.2], [1.90, 0.26, 0.05, 0.25]]
O1_BALL_A = O1_BALL_COMMON + [[1.98, 0.23, 0.24, 0.23], [2.10, 0.21, 0.28, 0.29], [2.20, 0.23, 0.25, 0.45], [2.38, 0.3, 0.22, 0.84],
                              [M["release"], 0.36, 0.2, 1.02]]
O1_BALL_B = O1_BALL_COMMON + [[1.98, 0.23, 0.24, 0.23], [2.15, 0.21, 0.27, 0.28], [3.6, 0.21, 0.27, 0.28]]

# ---------------- defender X1 (1.91 m) ----------------
X1_FEET0 = [[-0.05, 6.25, r3(HX + 0.15)], [0.45, 6.25, r3(HX - 0.15)]]
X1_BACK = []
ys = [5.85, 5.45, 5.05, 4.65, 4.25, 3.85, 3.48, 3.15]
for i, y in enumerate(ys):
    foot = 1 if i % 2 == 0 else 0
    lift = 0.10 + 0.18 * i
    X1_BACK.append(lstep(foot, r3(lift), r3(lift + 0.2), 0.47 if foot else -0.03, y, HX - 0.15 if foot else HX + 0.15, h=0.06))
X1_A = X1_BACK + [
    lstep(1, 1.76, 1.92, 1.05, 2.95, HX - 0.35, h=0.07),     # slide toward the attacker's LEFT (his right): he bought step 1
    lstep(0, 1.92, 2.05, 0.5, 2.9, HX - 0.1, h=0.06),
    lstep(0, 2.12, 2.32, 0.16, 2.6, HX + 0.55, h=0.09),     # recovery: drop step back toward the open lane
    lstep(1, 2.30, 2.48, 0.68, 2.45, HX + 0.25, h=0.08),
]
X1_B = X1_BACK + [
    lstep(0, 1.84, 1.98, -0.16, 3.0, HX + 0.12, h=0.05),     # stays square: half a step that keeps both lanes
    lstep(1, 1.96, 2.10, 0.42, 3.0, HX - 0.12, h=0.05),
]
X1_PEL_COMMON = [[0, 0.2, 6.2, 0.8]] + [[r3(0.3 + 0.18 * i), 0.21, r3(ys[i] + 0.25), 0.8] for i in range(len(ys))] + [[1.62, 0.22, 3.27, 0.78]]
X1_PEL_A = X1_PEL_COMMON + [[1.72, 0.26, 3.2, 0.77], [1.82, 0.5, 3.1, 0.74], [1.95, 0.76, 2.98, 0.76], [2.05, 0.76, 2.94, 0.77],
                            [2.18, 0.58, 2.8, 0.82], [2.35, 0.44, 2.64, 0.9], [2.55, 0.4, 2.54, 0.96], [2.9, 0.4, 2.5, 0.9], [3.6, 0.36, 2.46, 0.88]]
X1_PEL_B = X1_PEL_COMMON + [[1.72, 0.22, 3.22, 0.77], [1.85, 0.2, 3.16, 0.76], [2.0, 0.12, 3.1, 0.76], [2.15, 0.12, 3.08, 0.77], [3.6, 0.12, 3.08, 0.78]]
X1_BODY_COMMON = [[0, HX, 0, 0, 0.3, 0], [1.62, HX, 0, 0, 0.3, 0]]
X1_BODY_A = X1_BODY_COMMON + [[1.72, HX - 0.05, -0.15, -0.05, 0.3, -0.03], [1.82, HX - 0.12, -0.48, -0.22, 0.28, -0.12],
                              [1.95, HX - 0.12, -0.38, -0.18, 0.28, -0.1], [2.10, HX + 0.05, 0.15, 0.1, 0.25, 0.04],
                              [2.30, HX + 0.25, 0.6, 0.35, 0.18, 0.1], [2.6, HX + 0.25, 0.45, 0.3, 0.1, 0.05], [3.2, HX + 0.1, 0.1, 0.1, 0.15, 0]]
X1_BODY_B = X1_BODY_COMMON + [[1.75, HX, 0, 0, 0.3, 0], [1.95, HX + 0.04, 0.02, 0.02, 0.29, 0], [3.6, HX + 0.04, 0.02, 0.02, 0.29, 0]]


def play(pid, title, o1steps, o1pel, o1body, o1look, o1ball, x1steps, x1pel, x1body, finish, dur):
    o1 = {"feet0": O1_FEET0, "steps": o1steps, "pelvis": o1pel, "body": [[r3(v) for v in k] for k in o1body], "look": o1look,
          "arms": "attacker", "ev": {"gather": M["gather"]}, "ballKeys": o1ball, "dribble": {"from": 0.0, "n": 4}}
    x1 = {"feet0": X1_FEET0, "steps": x1steps, "pelvis": x1pel, "body": [[r3(v) for v in k] for k in x1body], "arms": "defender", "ev": {}}
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": M["release"] if finish else dur}]
    if finish:
        o1["ev"].update({"release": M["release"], "land": M["land"]})
        o1["flight"] = {"glass": [-0.3, 1.336, 3.36], "tGlass": M["glass"], "rim": [-0.03, 1.56, 3.09], "tRim": M["make"]}
        x1["contest"] = {"from": 2.28, "peak": 2.6, "to": 2.95, "hand": 0}
        ball.append({"type": "layup", "player": "O1", "t0": M["release"], "t1": M["make"], "make": True})
    tracks = {}
    for pid_, pel in (("O1", o1pel), ("X1", x1pel)):
        tracks[pid_] = []
        t = 0.0
        while t <= dur + 1e-9:
            # sample the same Hermite the engine uses (approximation here: piecewise linear on dense keys is enough for overlays)
            k = max(i for i in range(len(pel)) if pel[i][0] <= t) if t >= pel[0][0] else 0
            a, b = pel[k], pel[min(k + 1, len(pel) - 1)]
            u = 0 if b[0] == a[0] else (t - a[0]) / (b[0] - a[0])
            tracks[pid_].append([r3(t), r3(a[1] + (b[1] - a[1]) * u), r3(a[2] + (b[2] - a[2]) * u)])
            t = round(t + 0.1, 4)
    marks = dict(M) if finish else {k: v for k, v in M.items() if v <= M["step2"]}
    return {
        "id": pid, "title": title, "duration": dur,
        "concept": "Eurostep: the first counted step sells a lane, the second takes the space the defender gave",
        "source": "owner brief 2026-11-18 (FIBA/WABC L2 2.5.1, FIBA terminology, FIBA rules 2026 art. 24.1.2/25.2.1, NBA rule 10 XIII)",
        "players": [{"id": "O1", "team": "O", "role": "Ball handler: gather on the right foot, 1 LEFT, 2 RIGHT, right-hand finish"},
                    {"id": "X1", "team": "X", "role": "On-ball defender retreating between the ball and the rim", "guards": "O1"}],
        "ball": ball, "ballHolder": "O1", "marks": marks, "actions": {}, "tracks": tracks,
        "choreo": {"O1": o1, "X1": x1},
        "notes": ["The right foot is planted 0.13 s (4 frames) before the gather.",
                  "Same keys for both plays until step 1 lands; B: the defender keeps his chest between ball and rim."],
    }


A = play("euro-a", "Eurostep: he buys step 1", O1_A, O1_PEL_A, O1_BODY_A, O1_LOOK_A, O1_BALL_A, X1_A, X1_PEL_A, X1_BODY_A, True, 4.0)
B = play("euro-b", "Eurostep: he stays square", O1_B, O1_PEL_B, O1_BODY_B, O1_LOOK_B, O1_BALL_B, X1_B, X1_PEL_B, X1_BODY_B, False, 3.0)
for p in (A, B):
    json.dump(p, open(os.path.join(OUT, p["id"] + ".json"), "w"), indent=1)
    print("wrote", p["id"], len(p["choreo"]["O1"]["steps"]), "O1 steps")
