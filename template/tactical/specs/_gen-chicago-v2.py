#!/usr/bin/env python3
"""CHICAGO ACTION V2 (owner master brief E2A_REALISM_V2_PROMPT_CLAUDE_CODE.md sec. 11, 2026-11-21): PIN-DOWN straight into a
DRIBBLE HAND-OFF to the SAME receiver. Original E2A possession (standard FIBA / European Chicago action, generic coaching
knowledge, no copied diagram). Different from the 15 Nov pilot (chicago-a-take / chicago-b-backdoor: left side, backdoor B).

Brief axes: x across, y from the offensive baseline, the action on the brief's RIGHT. Repo axes (as BLOB / zone 2-3):
repo x = -brief x (the action is on repo x < 0), y unchanged, rim (0, 1.575, 3.05). Frames S(n) = n / 30 s.

  O1 handler, top (0.0, 9.3) [brief (0, 10.8): 2.5 m behind the arc is too deep for a 2-dribble entry; ADJUST]
  O2 shooter, low right wing (brief (5.3, 3.0)) -> pin-down -> hand-off from O1 on the right slot
  O4 screener (brief (4.1, 5.7)): walks down, PLANTS (both feet, stationary) before X2 can reach him, releases, short roll
  O3 left corner (brief (-6.2, 1.4)), O5 left wing high (brief (-5.6, 7.5)): spacing, small purposeful moves
  X1..X5 man-to-man on O1..O5.
  A  chicago-v2-a-trail  X2 TRAILS over the pin-down and over the hand-off: O2 turns the corner round O1 (O1's body screens
                         X2), ONE attack dribble, decelerates, pull-up jumper from mid-range (make). X1 does not switch.
  B  chicago-v2-b-under  X2 GOES UNDER the pin-down and under the hand-off: O2 catches off the hand-off behind the arc, a
                         1-2 stop and a three (make). X2 arrives late from below (late contest, no contact).
Ball state chain (brief 11.2): O1 controlled (dribble) -> O1 DHO offer (pocket + present) -> hand-off transfer -> O2 controlled
-> [A dribble -> pick-up -> shot release | B gather -> shot release] -> flight -> rim -> net.
  python3 tactical/specs/_gen-chicago-v2.py   (writes tactical/specs/chicago-v2-*.spec.json + tactical/plays/)"""
import json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
S = lambda n: round(n / 30, 4)
M = lambda p: (round(-p[0], 3), p[1])  # brief axes -> repo axes
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": S(a), "to": S(b), "face": f}
face = lambda f, a, b: {"type": "face", "from": S(a), "to": S(b), "face": f}
SRC = ("original E2A possession (standard FIBA/European Chicago action: pin-down into a dribble hand-off to the same receiver; "
       "generic coaching knowledge, brief sec. 11 references Dr. Dish / Online Basketball Playbook / Coach's Clipboard read only "
       "as concept, no diagram copied). FIBA court 28 x 15 m, three-point line 6.75 m.")


def crs(pts, n=400):
    """Catmull-Rom (centripetal-ish, uniform) through pts, densely sampled, with arc length"""
    P_ = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(n):
            u = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u * u +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u ** 3) for j in (0, 1)))
    out.append(tuple(pts[-1]))
    cum = [0.0]
    for i in range(1, len(out)):
        cum.append(cum[-1] + math.hypot(out[i][0] - out[i - 1][0], out[i][1] - out[i - 1][1]))
    return out, cum


def run(f0, f1, pts, v0=0.0, v1=0.0, step=3):
    """a run along a smooth curve through pts (brief axes are NOT applied here: repo coordinates) from frame f0 to f1,
    entry speed v0 and exit speed v1 (m/s); the arc length follows a cubic Hermite (continuous speed across runs that
    share an end speed), so a cutter can take the hand-off IN STRIDE instead of stopping at it"""
    curve, cum = crs(pts)
    L = cum[-1]
    Tt = (f1 - f0) / 30
    out = {}
    frames = list(range(f0, f1, step)) + [f1]
    for fr in frames:
        x = (fr - f0) / (f1 - f0)
        h10, h01, h11 = x ** 3 - 2 * x * x + x, -2 * x ** 3 + 3 * x * x, x ** 3 - x * x
        s = h10 * Tt * v0 + h01 * L + h11 * Tt * v1
        s = max(0.0, min(L, s))
        j = next((k for k in range(len(cum)) if cum[k] >= s - 1e-12), len(cum) - 1)
        if j == 0:
            q = curve[0]
        else:
            r = (s - cum[j - 1]) / max(1e-12, cum[j] - cum[j - 1])
            q = (curve[j - 1][0] + (curve[j][0] - curve[j - 1][0]) * r, curve[j - 1][1] + (curve[j][1] - curve[j - 1][1]) * r)
        out[fr] = (round(q[0], 3), round(q[1], 3))
    out[f0], out[f1] = tuple(pts[0]), tuple(pts[-1])
    return out


def runk(keys, step=3):
    """one smooth curve through all key points (tangent-continuous: no kink at the hand-off), timed by keys
    [(frame, (x, y), speed m/s), ...]: between two keys the arc length is a cubic Hermite with the key speeds"""
    pts = [k[1] for k in keys]
    n = 400
    curve, cum = crs(pts, n)
    sk = [cum[min(i * n, len(cum) - 1)] for i in range(len(pts))]
    out = {}
    for (fa, pa, va), (fb, pb, vb), sa, sb in zip(keys, keys[1:], sk, sk[1:]):
        Tt = (fb - fa) / 30
        for fr in list(range(fa, fb, step)) + [fb]:
            x = (fr - fa) / (fb - fa)
            h10, h01, h11 = x ** 3 - 2 * x * x + x, -2 * x ** 3 + 3 * x * x, x ** 3 - x * x
            s = sa + h10 * Tt * va + h01 * (sb - sa) + h11 * Tt * vb
            j = next((k for k in range(len(cum)) if cum[k] >= s - 1e-12), len(cum) - 1)
            if j == 0:
                q = curve[0]
            else:
                r = (s - cum[j - 1]) / max(1e-12, cum[j] - cum[j - 1])
                q = (curve[j - 1][0] + (curve[j][0] - curve[j - 1][0]) * r, curve[j - 1][1] + (curve[j][1] - curve[j - 1][1]) * r)
            out[fr] = (round(q[0], 3), round(q[1], 3))
    for fr, p_, _ in keys:
        out[fr] = tuple(p_)
    return out


def runv(pts, speeds, anchor_i, anchor_f, step=2):
    """speed-driven run: one smooth curve through pts with a speed (m/s) at every point; the time between two points is
    their curve distance / mean speed, and the whole run is shifted so that point `anchor_i` is reached at frame
    `anchor_f` (e.g. the hand-off contact). Returns ({frame: (x, y)}, [frame of each point]). Float frames allowed."""
    n = 400
    curve, cum = crs(pts, n)
    sk = [cum[min(i * n, len(cum) - 1)] for i in range(len(pts))]
    tk = [0.0]
    for i in range(1, len(pts)):
        tk.append(tk[-1] + (sk[i] - sk[i - 1]) / max(0.05, 0.5 * (speeds[i] + speeds[i - 1])))
    fk = [anchor_f + 30 * (t - tk[anchor_i]) for t in tk]
    out = {}
    for i in range(len(pts) - 1):
        fa, fb, sa, sb, va, vb = fk[i], fk[i + 1], sk[i], sk[i + 1], speeds[i], speeds[i + 1]
        Tt = (fb - fa) / 30
        m = max(1, int(round((fb - fa) / step)))
        for k in range(m + 1):
            x = k / m
            h10, h01, h11 = x ** 3 - 2 * x * x + x, -2 * x ** 3 + 3 * x * x, x ** 3 - x * x
            sv = sa + h10 * Tt * va + h01 * (sb - sa) + h11 * Tt * vb
            j = next((q for q in range(len(cum)) if cum[q] >= sv - 1e-12), len(cum) - 1)
            if j == 0:
                q_ = curve[0]
            else:
                r = (sv - cum[j - 1]) / max(1e-12, cum[j] - cum[j - 1])
                q_ = (curve[j - 1][0] + (curve[j][0] - curve[j - 1][0]) * r, curve[j - 1][1] + (curve[j][1] - curve[j - 1][1]) * r)
            out[round(fa + (fb - fa) * x, 3)] = (round(q_[0], 3), round(q_[1], 3))
    return out, [round(x, 3) for x in fk]


def cat(*parts):
    d = {}
    for p in parts:
        d.update(p)
    return d


PLAYERS = [P("O1", "O", "Handler at the top: dribbles to the right slot, offers and hands the ball off to O2, his body screens X2"),
           P("O2", "O", "Shooter: low right wing, jab, comes up off the pin-down, takes the hand-off (A: one dribble + pull-up / B: three)"),
           P("O3", "O", "Left corner: spacing (lifts a step when the ball turns the corner)"),
           P("O4", "O", "Screener: walks down, PLANTS the pin-down on X2 (stationary at contact), then a short roll"),
           P("O5", "O", "Left wing high: spacing, keeps X5 honest"),
           P("X1", "X", "On the handler: stays with O1, does NOT switch", "O1"),
           P("X2", "X", "On the shooter: TRAILS (A) / goes UNDER (B)", "O2"),
           P("X3", "X", "On the corner: sinks to the help line, recovers", "O3"),
           P("X4", "X", "On the screener: stays attached to O4 (pin-down, roll)", "O4"),
           P("X5", "X", "On the weak wing: sinks, helps the nail, recovers", "O5")]

# repo coordinates (x = -brief x)
START = {"O1": (0.0, 9.3), "X1": (-0.25, 8.35), "O2": (-5.3, 3.0), "X2": (-4.62, 3.18), "O4": (-4.1, 5.7), "X4": (-3.45, 5.15),
         "O3": (6.2, 1.4), "X3": (4.95, 2.15), "O5": (5.6, 7.5), "X5": (4.3, 6.45)}
PIN = (-4.32, 4.22)        # O4's pin-down spot: planted S030 -> S066, facing the baseline (X2)
HO = (-3.22, 8.58)
PULL = (-0.38, 6.78)       # A pull-up spot (nail side, 5.22 m)
O1HO = (-2.62, 7.9)        # O1 at the hand-off (stopped, facing O2's arrival)
F_OFFER, F_HO = 62, 72     # O1 presents the ball (pocket + present) / contact (pass t0); transfer to S076
F_HO1 = 78

DUR = {"a": 165, "b": 150}

# ---------------------------------------------------------------- shared opening (identical in A and B up to S045)
COMMON = {
    # O1: two dribbles to the right slot, arrives S040 and waits with a live dribble, then offers the ball
    "O1": cat(run(4, 40, [START["O1"], (-1.35, 8.95), O1HO]), {60: O1HO}),
    # O4 walks down and PLANTS: stationary from S030 (6 frames before X2 can reach him) to S066
    "O4": cat(run(0, 30, [START["O4"], (-4.25, 4.9), PIN]), {66: PIN}),
    "X4": cat(run(2, 32, [START["X4"], (-3.75, 4.75), (-3.78, 4.48)]), {62: (-3.78, 4.48)}),
    # O2: jab toward the baseline (sets X2 up), then explodes up the wing, outside O4's shoulder (0.7 m centre-centre)
    "O2": run(2, 13, [START["O2"], (-5.1, 2.62)], 0, 0),
    "X1": cat(run(6, 42, [START["X1"], (-1.25, 8.05), (-2.25, 7.42)]), {56: (-2.25, 7.42)}),
    "X3": cat(run(30, 60, [START["X3"], (4.0, 2.55)]), {75: (4.0, 2.55)}),
    "X5": cat(run(28, 62, [START["X5"], (3.55, 6.0)]), {75: (3.55, 6.0)}),
    "O3": {80: (6.2, 1.4)},
    "O5": cat(run(20, 50, [START["O5"], (5.75, 7.75)]), {80: (5.75, 7.75)}),
}
# O2's cut: S027 (from the jab) -> passes O4 ~S046 -> curls round O1's TOP side -> hand-off contact S072 IN STRIDE (~3 m/s)
CUTPTS = [(-5.1, 2.62), (-5.12, 3.6), (-5.02, 4.35), (-4.75, 5.6), (-4.35, 6.85), (-3.95, 7.95), HO]
CUTV = [0.0, 3.2, 4.6, 5.2, 5.0, 4.0, 3.0]
O2A, O2A_F = runv(CUTPTS + [(-2.78, 8.74), (-2.1, 8.62), (-1.38, 8.05), (-0.82, 7.32), (-0.5, 6.92), PULL], CUTV + [3.0, 3.2, 3.5, 3.2, 1.6, 0.0], 6, F_HO)
O2B, O2B_F = runv(CUTPTS + [(-2.92, 8.68), (-2.72, 8.7)], CUTV + [1.6, 0.0], 6, F_HO)
# the pin-down screener SETS his angle (chest to where X2 starts) and holds it: tracking the moving defender turned
# him ~150 deg on the spot (qc-realism blocking: a screener that keeps re-stepping is not a set screen)
PIN_FACE = round(math.atan2(START["X2"][1] - PIN[1], START["X2"][0] - PIN[0]), 4)
X2A, X2A_F = runv([START["X2"], (-4.95, 3.5), (-5.2, 4.4), (-5.0, 5.6), (-4.55, 6.9), (-4.1, 8.1), (-3.6, 9.0), (-2.6, 9.15), (-1.75, 8.72), (-1.3, 8.3)],
                  [0.0, 2.6, 4.3, 5.0, 4.6, 3.9, 3.4, 3.3, 2.4, 0.0], 2, 51)
X2B, X2B_F = runv([START["X2"], (-3.95, 3.45), (-3.2, 3.95), (-2.8, 5.2), (-2.95, 6.35), (-3.3, 7.4)], [0.0, 2.8, 4.2, 4.4, 3.0, 0.0], 1, 41)
print("O2 A frames", O2A_F, "\nO2 B frames", O2B_F, "\nX2 A frames", X2A_F, "\nX2 B frames", X2B_F)
PULL_F = int(math.ceil(O2A_F[-1]))   # O2 stopped: the pull-up starts here

A = {
    # after the hand-off O2 turns the corner round O1 (to the middle, then downhill), ONE dribble, stops S098: pull-up
    "O2": cat(COMMON["O2"], O2A, {DUR["a"]: PULL}),
    # X2 reacts 3 frames after the cut, goes OVER the pin-down (outside O4, behind O2) and over the hand-off (round O1's top)
    "X2": cat(X2A, {DUR["a"]: (-1.3, 8.3)}),
    # O1: after the hand-off he holds his spot 0.4 s (his body is in X2's way), then rolls to the paint
    "O1": cat(COMMON["O1"], {84: O1HO}, run(84, 124, [O1HO, (-2.9, 6.3), (-2.6, 4.4)]), {DUR["a"]: (-2.6, 4.4)}),
    # X1 stays with O1: a short show at the turn of the corner, back to O1 (no switch)
    "X1": cat(COMMON["X1"], run(74, 88, [(-2.25, 7.42), (-1.98, 7.3)]), run(90, 126, [(-1.98, 7.3), (-2.15, 5.9), (-2.05, 4.55)]), {DUR["a"]: (-2.05, 4.55)}),
    # O4 releases S066 and rolls short (lane line), X4 stays attached (inside)
    "O4": cat(COMMON["O4"], run(66, 100, [PIN, (-3.6, 3.6), (-2.75, 3.25)]), {DUR["a"]: (-2.75, 3.25)}),
    "X4": cat(COMMON["X4"], run(63, 100, [(-3.78, 4.48), (-2.98, 4.14), (-2.12, 3.6)]), {DUR["a"]: (-2.12, 3.6)}),
    "X3": cat(COMMON["X3"], run(84, 112, [(4.0, 2.55), (3.1, 2.7)]), {DUR["a"]: (3.1, 2.7)}),
    "X5": cat(COMMON["X5"], run(84, 110, [(3.55, 6.0), (2.55, 5.6)]), {DUR["a"]: (2.55, 5.6)}),
    "O3": cat(COMMON["O3"], run(86, 110, [(6.2, 1.4), (6.25, 1.75)]), {DUR["a"]: (6.25, 1.75)}),
    "O5": cat(COMMON["O5"], {DUR["a"]: (5.75, 7.75)}),
}

B = {
    # O2 takes the hand-off and stops behind the arc (1-2 stop), gathers, three
    "O2": cat(COMMON["O2"], O2B, {DUR["b"]: (-2.72, 8.7)}),
    # X2 goes UNDER: inside O4 (between O4 and the rim), then under O1, arrives late from below: contest at ~1.2 m
    "X2": cat(X2B, {DUR["b"]: (-3.3, 7.4)}),
    "O1": cat(COMMON["O1"], {DUR["b"]: O1HO}),
    "X1": cat(COMMON["X1"], run(74, 92, [(-2.25, 7.42), (-1.85, 7.25)]), {DUR["b"]: (-1.85, 7.25)}),
    "O4": cat(COMMON["O4"], run(66, 100, [PIN, (-3.6, 3.6), (-2.75, 3.25)]), {DUR["b"]: (-2.75, 3.25)}),
    "X4": cat(COMMON["X4"], run(63, 100, [(-3.78, 4.48), (-2.98, 4.14), (-2.12, 3.6)]), {DUR["b"]: (-2.12, 3.6)}),
    "X3": cat(COMMON["X3"], {DUR["b"]: (4.0, 2.55)}),
    "X5": cat(COMMON["X5"], run(84, 104, [(3.55, 6.0), (3.15, 6.2)]), {DUR["b"]: (3.15, 6.2)}),
    "O3": cat(COMMON["O3"], {DUR["b"]: (6.2, 1.4)}),
    "O5": cat(COMMON["O5"], {DUR["b"]: (5.75, 7.75)}),
}


def track(anchors, dur):
    ks = sorted(anchors)
    wp = [[S(k), anchors[k][0], anchors[k][1]] for k in ks]
    # equal consecutive points end a run (rest); collapse exact duplicates in time
    out = []
    for w in wp:
        if out and abs(out[-1][0] - w[0]) < 1e-9:
            out[-1] = w
        else:
            out.append(w)
    if out[-1][0] < dur:
        out.append([dur, out[-1][1], out[-1][2]])
    return out


def tracks(kind):
    br = {"a": A, "b": B}[kind]
    out = {}
    for pid, p0 in START.items():
        an = {0: p0}
        an.update(br.get(pid, COMMON.get(pid, {})))
        out[pid] = track(an, S(DUR[kind]))
    return out


def ball(kind):
    ev = [{"type": "hold", "player": "O1", "from": 0, "to": S(F_OFFER), "dribble": True, "hand": 1},
          # the OFFER: ball picked up into O1's pocket and presented toward O2 (both hands on it), never thrown
          {"type": "hold", "player": "O1", "from": S(F_OFFER), "to": S(F_HO), "pocket": True,
           "present": {"toward": "O2", "from": S(F_OFFER + 2), "peak": S(F_HO - 2), "hold": S(F_HO + 6), "to": S(F_HO + 10), "amt": 0.05, "dz": -0.06}},
          {"type": "pass", "from": "O1", "to": "O2", "t0": S(F_HO), "t1": S(F_HO1), "style": "handoff"}]
    if kind == "a":
        ev += [{"type": "hold", "player": "O2", "from": S(F_HO1), "to": S(F_HO1 + 3), "pocket": True},
               {"type": "hold", "player": "O2", "from": S(F_HO1 + 3), "to": S(PULL_F - 8), "dribble": True, "hand": 1},
               {"type": "hold", "player": "O2", "from": S(PULL_F - 8), "to": S(PULL_F + 1)},
               {"type": "shot", "player": "O2", "t0": S(PULL_F + 1), "t1": S(PULL_F + 29), "make": True, "three": False}]
    else:
        ev += [{"type": "hold", "player": "O2", "from": S(F_HO1), "to": S(88), "pocket": True},
               {"type": "shot", "player": "O2", "t0": S(88), "t1": S(118), "make": True, "contested": True}]
    return ev


def actions(kind):
    d = DUR[kind]
    act = {pid: [] for pid in START}
    act["O4"] = [face("O2", 0, 24), {"type": "screen", "from": S(30), "to": S(66), "face": PIN_FACE}, face("ball", 70, d)]
    act["O1"] = [face("O2", 44, F_HO1 + 6), {"type": "screen", "from": S(F_HO1 + 2), "to": S(84 if kind == "a" else 86), "face": "X2"},
                 face("ball", 90, d)]
    act["O2"] = [face("O4", 0, 16), {"type": "catchReady", "from": S(F_HO - 9), "to": S(F_HO1), "face": "O1"}]
    act["X1"] = [st("O1", 0, d)]
    act["X3"] = [st("ball", 0, d)]
    act["X5"] = [st("ball", 0, d)]
    act["O3"] = [face("ball", 0, d)]
    act["O5"] = [face("ball", 0, d)]
    if kind == "a":
        act["X2"] = [st("O2", 0, 16), {"type": "contest", "from": S(PULL_F + 3), "to": S(PULL_F + 29)}]
        act["X4"] = [st("O4", 0, d)]
        act["O2"] += [{"type": "celebrate", "from": S(140), "to": S(160)}]
    else:
        act["X2"] = [st("O2", 0, 16), {"type": "closeout", "from": S(80), "to": S(92)}, {"type": "contest", "from": S(92), "to": S(116)}]
        act["X4"] = [st("O4", 0, d)]
        act["O2"] += [{"type": "celebrate", "from": S(128), "to": S(146)}]
    return act


ADJUST = [
    "O1 start (0, 9.3) instead of the brief (0, 10.8): 10.8 is 2.5 m behind the arc; two dribbles to the slot keep the timing tight",
    "Brief coordinates are guidance (sec. 11.2): repo x = -brief x. O2 (5.3, 3.0) -> (-5.3, 3.0); O4 (4.1, 5.7) -> (-4.1, 5.7); O3 corner (-6.2, 1.4) -> (6.2, 1.4); O5 (-5.6, 7.5) -> (5.6, 7.5)",
    "Pin-down: O4 PLANTED S030 -> S066 at (-4.32, 4.22); X2 cannot reach his body before S034 (test-play screens stationary, qc-realism blocking)",
    "Hand-off ON O1's TOP side (O2 curls round the handler, then turns the corner): O1's body is the second obstacle for a trailing X2",
    "A pull-up at (-0.38, 6.78): 5.2 m from the rim (mid-range); B three at (-2.72, 8.7): 7.6 m (FIBA 6.75 + margin for the feet)",
]


def spec(kind):
    sid = {"a": "chicago-v2-a-trail", "b": "chicago-v2-b-under"}[kind]
    title = {"a": "Chicago action (A): X2 trails - turn the corner, one dribble, pull-up",
             "b": "Chicago action (B): X2 goes under - catch off the hand-off, three"}[kind]
    s = {"id": sid, "title": title, "duration": S(DUR[kind]), "concept": "chicago-pin-down-dho", "source": SRC, "squareUp": True,
         "catchV2": 2, "handBallClear": True, "realism": 2, "players": PLAYERS, "tracks": tracks(kind), "ball": ball(kind), "actions": actions(kind),
         "screens": [], "sclock": {"fps": 30, "mirrorX": True, "anchors": "E2A anchors on brief sec. 11.2", "adjust": ADJUST}}
    common = {"start": 0, "pindown": S(30), "cut": S(16), "pass_screen": S(41), "offer": S(F_OFFER), "handoff": S(F_HO), "transfer": S(F_HO1)}
    if kind == "a":
        s["marks"] = {**common, "dribble": S(F_HO1 + 2), "pickup": S(PULL_F - 8), "pullup": S(PULL_F + 1), "make": S(PULL_F + 29), "end": s["duration"]}
        s["claims"] = [
            {"type": "near", "a": "O4", "b": "X2", "at": "pass_screen", "max": 1.5, "says": "First, the pin-down."},
            {"type": "far", "a": "X2", "b": "O2", "at": "handoff", "min": 1.3, "says": "his defender has to chase (trails over the top)"},
            {"type": "far", "a": "X2", "b": "O2", "at": "pullup", "min": 1.6, "says": "Trail him, and he turns the corner before you recover."},
            {"type": "near", "a": "O1", "b": "O2", "at": "handoff", "max": 0.95, "says": "straight into the handoff (hand to hand)"},
            {"type": "near", "a": "X1", "b": "O1", "at": "pullup", "max": 1.8, "says": "X1 does not switch: he stays with O1"},
            {"type": "order", "marks": ["pindown", "pass_screen", "offer", "handoff", "dribble", "pickup", "pullup", "make"], "says": "pin-down, hand-off, one dribble, pull-up"}]
    else:
        s["marks"] = {**common, "gather": S(84), "release": S(88), "make": S(118), "end": s["duration"]}
        s["claims"] = [
            {"type": "near", "a": "O4", "b": "X2", "at": "pass_screen", "max": 1.6, "says": "pin-down (X2 under it)"},
            {"type": "behind_arc", "player": "O2", "at": "release", "says": "a shooter space to rise up (three, feet behind the line)"},
            {"type": "far", "a": "X2", "b": "O2", "at": "transfer", "min": 1.6, "says": "But go under? Now you leave a shooter space"},
            {"type": "open", "player": "O2", "at": "release", "min": 1.0, "says": "late contest from under, no contact"},
            {"type": "near", "a": "O1", "b": "O2", "at": "handoff", "max": 0.95, "says": "the handoff (hand to hand)"},
            {"type": "order", "marks": ["pindown", "pass_screen", "offer", "handoff", "transfer", "gather", "release", "make"], "says": "pin-down, hand-off, three"}]
    return s


if __name__ == "__main__":
    print("A pull-up to rim", round(math.hypot(1.5, 6.62 - 1.575), 2), "m; B three", round(math.hypot(2.72, 8.7 - 1.575), 2), "m; HO", round(math.hypot(*HO) if False else math.hypot(HO[0], HO[1] - 1.575), 2))
    for k in ("a", "b"):
        s = spec(k)
        json.dump(s, open(os.path.join(D, f"{s['id']}.spec.json"), "w"), indent=1)
        json.dump(s, open(os.path.join(T, "tactical", "plays", f"{s['id']}.json"), "w"), indent=1)
        print("built", s["id"], json.dumps(s["marks"]))
