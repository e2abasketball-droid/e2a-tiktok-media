#!/usr/bin/env python3
"""DOUBLE DRAG: roll or pop? (owner brief 2026-11-15 21:45Z). Original E2A possession (standard double-drag ball
screen in early offence, generic coaching knowledge, no copied diagram).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Half-court view with the basket at the
top (yaw 0): x < 0 is the RIGHT of the screen.
  O1 brings the ball from the high right. O4 and O5 set staggered drag screens; O1 uses both toward the middle.
  O4 (first screener) pops to the right perimeter behind the arc; O5 (second) rolls. O2 and O3 fill the corners.
  A ddrag-a-pop   X1 trails, X5 contains the ball, X4 sinks to stop O5's roll -> O1 hits O4 popping, three.
  B ddrag-b-roll  X4 stays with O4, X5 contains, X1 trails -> O1 hits O5 rolling, finish at the rim."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (standard double-drag ball screen, pop or roll read, generic coaching knowledge)"
PL = [P("O1", "O", "Ball handler, brings it from the high right"), P("O2", "O", "Right corner"), P("O3", "O", "Left corner"),
      P("O4", "O", "First screener: pops to the right perimeter"), P("O5", "O", "Second screener: rolls"),
      P("X1", "X", "On the ball, trails over the screens", "O1"), P("X2", "X", "On the right corner", "O2"),
      P("X3", "X", "On the left corner", "O3"), P("X4", "X", "On the popper: the helper", "O4"),
      P("X5", "X", "On the roller: contains the ball", "O5")]
S = {"O1": [-4.4, 10.6], "X1": [-3.85, 9.85], "O2": [-6.6, 1.3], "X2": [-5.7, 1.95], "O3": [6.6, 1.3], "X3": [5.7, 1.95],
     "O4": [-1.7, 11.2], "X4": [-1.55, 10.15], "O5": [-0.1, 10.9], "X5": [-0.2, 9.75]}
S4 = [-2.85, 10.0]      # first drag screen (higher, nearer the ball)
S5 = [-1.55, 9.05]      # second drag screen (lower, toward the middle): staggered
POP = [-5.0, 7.7]       # O4's pop: right perimeter, behind the arc (7.8 m)
DRIVE = [[-3.4, 9.35], [-2.1, 8.35], [-0.6, 7.25]]
PICK = [0.85, 6.35]     # O1's pick-up spot in the middle
SHARED = {
    "O4": [{"at": 0.15, "to": S4, "dur": 0.8}],
    "O5": [{"at": 0.2, "to": S5, "dur": 0.95}],
    "O1": [{"at": 0.45, "to": [-4.1, 10.2], "dur": 0.5},
           {"at": 1.3, "via": DRIVE, "to": PICK, "speed": 5.0}],
    "X1": [{"at": 0.5, "to": [-3.45, 10.15], "dur": 0.5},
           {"at": 1.35, "via": [[-2.95, 10.75], [-2.0, 10.55], [-1.2, 9.9]], "to": [-0.35, 8.4], "speed": 4.2},
           {"at": "+0", "to": [0.15, 7.45], "dur": 0.6}],
    "X5": [{"at": 0.3, "to": [-0.95, 8.25], "dur": 0.75},          # drop below the second screen
           {"at": 1.7, "to": [1.55, 6.0], "dur": 0.95}],           # contains the ball in the middle
    "O4p": [],
}


def play(kind):
    legs = {k: [dict(l) for l in v] for k, v in SHARED.items() if v}
    acts = {"X2": [st("O2", 0, 6.6)], "X3": [st("O3", 0, 6.6)], "X1": [st("O1", 0, 1.35)],
            "O4": [{"type": "screen", "from": TM["s4"], "to": 1.9, "face": "X1"}],
            "O5": [{"type": "screen", "from": TM["s5"], "to": 2.2, "face": "X1"}]}
    legs["O4"].append({"at": 1.95, "via": [[-3.9, 9.1]], "to": POP, "speed": 3.8})
    acts["X1"].append({"type": "bump", "from": 1.55, "to": 1.8})
    if kind == "pop":
        legs["O5"].append({"at": 2.25, "via": [[-1.05, 6.6]], "to": [-0.3, 3.5], "speed": 4.4})
        legs["X4"] = [{"at": 0.15, "to": [-3.3, 8.2], "dur": 1.1},             # under the first screen
                      {"at": 2.2, "via": [[-2.4, 6.4]], "to": [-1.15, 4.45], "speed": 4.2},   # sinks to the roll
                      {"at": TB["passA"] + 0.3, "to": [-2.9, 5.7], "dur": 0.8}]   # closes out late
        legs["O1"].append({"at": "+0", "to": [0.95, 6.05], "dur": 0.45})
        acts["X4"] = [st("O5", 2.2, TB["passA"] + 0.3)]
        acts["X5"] = [st("O1", 1.7, TB["passA"])]
        acts["O4"].append({"type": "celebrate", "from": TB["passA"] + 2.2, "to": 6.6})
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": TB["passA"], "dribble": True},
                {"type": "pass", "from": "O1", "to": "O4", "t0": TB["passA"], "t1": TB["passA"] + 0.6, "style": "chest"},
                {"type": "hold", "player": "O4", "from": TB["passA"] + 0.6, "to": TB["passA"] + 0.95},
                {"type": "shot", "player": "O4", "t0": TB["passA"] + 0.95, "t1": TB["passA"] + 2.0, "make": True}]
        pa = TB["passA"]
        marks = {"start": 0, "s4": TM["s4"], "s5": TM["s5"], "use": 1.3, "pop": 1.95, "roll": 2.25, "sink": 2.2, "pass": pa,
                 "catch": pa + 0.6, "release": pa + 0.95, "make": pa + 2.0, "end": 6.6}
        claims = [
            {"type": "near", "a": "X4", "b": "O5", "at": "pass", "max": 1.6, "says": "Help takes the roll."},
            {"type": "far", "a": "X4", "b": "O4", "at": "catch", "min": 3.0, "says": "The pop is open."},
            {"type": "behind_arc", "player": "O4", "at": "release", "says": "First screener pops."},
            {"type": "far", "a": "X1", "b": "O1", "at": "pass", "min": 1.0, "says": "X1 trails over the screens"},
            {"type": "order", "marks": ["s4", "s5", "use", "pop", "roll", "pass", "catch", "release", "make"], "says": "two screens, pop, roll, pass to the pop"}]
        return {"id": "ddrag-a-pop", "title": "Double drag A: help takes the roll, the pop is open", "duration": 6.6,
                "concept": "double-drag", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
                "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O4 and O5 set staggered drag screens; O1 uses both toward the middle; X1 trails, X5 contains.",
                          "O4 pops behind the arc, O5 rolls; X4 sinks to the roll; O1 hits O4 for three."]}
    legs["O5"].append({"at": 2.25, "via": [[-1.05, 6.6]], "to": [-0.55, 4.6], "speed": 4.4})
    legs["O5"].append({"at": "+0", "to": [-0.2, 2.85], "dur": 0.75})        # under control for the catch
    legs["X4"] = [{"at": 0.15, "to": [-3.3, 8.2], "dur": 1.1},
                  {"at": 2.1, "via": [[-3.9, 8.1]], "to": [-4.3, 7.15], "speed": 3.6}]   # stays with the shooter
    legs["O1"].append({"at": "+0", "to": [0.95, 6.15], "dur": 0.3})
    legs["X2"] = [{"at": TB["passB"], "to": [-4.5, 2.35], "dur": 0.9}]                  # late help from the corner
    acts["X4"] = [st("O4", 2.1, 6.0)]
    acts["X5"] = [st("O1", 1.7, 6.0)]
    acts["X2"] = [st("O2", 0, TB["passB"])]
    pb = TB["passB"]; cb = TB["catchB"]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": pb, "dribble": True},
            {"type": "pass", "from": "O1", "to": "O5", "t0": pb, "t1": cb, "style": "bounce"},
            {"type": "hold", "player": "O5", "from": cb, "to": cb + 0.3},
            {"type": "layup", "player": "O5", "t0": cb + 0.3, "t1": cb + 0.7, "make": True}]
    acts["O5"].append({"type": "celebrate", "from": cb + 1.0, "to": 6.0})
    marks = {"start": 0, "s4": TM["s4"], "s5": TM["s5"], "use": 1.3, "pop": 1.95, "roll": 2.25, "stay": 2.1, "pass": pb,
             "catch": cb, "finish": cb + 0.3, "make": cb + 0.7, "end": 6.0}
    claims = [
        {"type": "near", "a": "X4", "b": "O4", "at": "pass", "max": 1.6, "says": "If that defender stays with the shooter..."},
        {"type": "far", "a": "X4", "b": "O5", "at": "pass", "min": 3.0, "says": "...look for the roll."},
        {"type": "near_rim", "player": "O5", "at": "finish", "max": 1.6, "says": "finish at the rim"},
        {"type": "order", "marks": ["s4", "s5", "use", "pop", "roll", "pass", "catch", "finish", "make"], "says": "two screens, pop, roll, pass to the roll"}]
    return {"id": "ddrag-b-roll", "title": "Double drag B: X4 stays with the pop, hit the roll", "duration": 6.0,
            "concept": "double-drag", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
            "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start as ddrag-a-pop.", "X4 stays with O4; X5 contains O1; O1 bounces it to O5 rolling; layup."]}


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


def pos(tr, t):
    for a, b in zip(tr, tr[1:]):
        if a[0] <= t <= b[0]:
            u = (t - a[0]) / max(1e-9, b[0] - a[0])
            return [a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u]
    return tr[-1][1:3]


def first_near(tr, pt, r=0.05, after=0.0):
    t = after
    while t <= tr[-1][0]:
        q = pos(tr, t)
        if ((q[0] - pt[0]) ** 2 + (q[1] - pt[1]) ** 2) ** 0.5 <= r:
            return t
        t += 0.005
    return None


TM = {"s4": 1.0, "s5": 1.2}
TB = {"passA": 3.0, "passB": 2.85, "catchB": 3.3}

if __name__ == "__main__":
    tr = build(play("roll"))["tracks"]
    TM["s4"] = round(first_near(tr["O4"], S4, 0.03) + 0.08, 2)
    TM["s5"] = round(first_near(tr["O5"], S5, 0.03) + 0.08, 2)
    t1 = first_near(tr["O1"], PICK, 0.05)
    TB["passA"] = round(t1 + 0.35, 2)
    tc = first_near(tr["O5"], [-0.2, 2.85], 0.12)
    TB["catchB"] = round(tc, 2)
    TB["passB"] = round(tc - 0.45, 2)
    print("TM", TM, "TB", TB)
    for s in (play("pop"), play("roll")):
        p = build(s)
        print("built", s["id"], p["duration"])
