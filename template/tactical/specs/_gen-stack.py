#!/usr/bin/env python3
"""STACK PICK-AND-ROLL (owner choice 2026-11-16 11:40Z: same method as the Spain pick-and-roll, a similar but different
play). Original E2A possession (generic stack ball-screen read, generic coaching knowledge, no copied diagram).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Basket at the top (yaw 0): x > 0 is screen-left.
  O1 top with the ball. O5 sets the ball screen; O2 (the shooter) is stacked right behind him. X5 shows high on the ball.
  O1 turns the corner (x > 0); O5 rolls down the middle, O2 lifts from behind the screen to the arc on the other side.
  X2 (the shooter's defender) is the only one between the roller and the rim: he decides.
  A stack-a-three  X2 helps on the roll -> the pass goes back to O2, open three.
  B stack-b-roll   X2 stays with O2     -> nobody stops the roll, bounce pass, layup."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (generic stack pick-and-roll read, generic coaching knowledge)"
PL = [P("O1", "O", "Ball handler"), P("O2", "O", "Shooter stacked behind the screener"), P("O3", "O", "Spacer, left corner"),
      P("O4", "O", "Spacer, right corner"), P("O5", "O", "Ball screener / roller"),
      P("X1", "X", "On the ball", "O1"), P("X2", "X", "On the stacked shooter: decides", "O2"), P("X3", "X", "Left corner", "O3"),
      P("X4", "X", "Right corner", "O4"), P("X5", "X", "On the screener: shows high", "O5")]
S = {"O1": [0.0, 9.1], "X1": [0.0, 8.25], "O5": [0.9, 6.85], "X5": [1.65, 6.35], "O2": [0.55, 5.75], "X2": [0.05, 4.95],
     "O3": [6.6, 1.3], "X3": [5.6, 2.1], "O4": [-6.6, 1.3], "X4": [-5.6, 2.1]}
SCR = [0.8, 8.2]
POP = [-2.0, 8.7]
BASE = {
    "O5": [{"at": 0.0, "to": SCR, "speed": 3.4}],
    "X5": [{"at": 0.2, "to": [1.45, 7.6], "speed": 2.6},
           {"at": 0.95, "to": [1.85, 8.55], "speed": 3.6}],                       # shows high on the ball
    "O1": [{"at": 0.8, "via": [[1.1, 9.8], [2.35, 9.55]], "to": [2.85, 8.15], "speed": 4.0}],
    "X1": [{"at": 1.4, "via": [[1.1, 9.55]], "to": [2.3, 9.45], "speed": 3.6}],
    "O2": [{"at": 1.15, "via": [[-0.6, 6.55]], "to": POP, "speed": 4.6}],          # lifts out of the stack
}


def play(kind):
    legs = {k: [dict(l) for l in v] for k, v in BASE.items()}
    acts = {"X3": [st("O1", 0, 6.0)], "X4": [st("O1", 0, 6.0)], "X1": [st("O1", 0, 6.0)],
            "X5": [st("O1", 0.9, 2.6)], "O5": [{"type": "screen", "from": 0.85, "to": 1.45, "face": "X1"}]}
    if kind == "three":
        legs["O5"].append({"at": 1.5, "via": [[0.55, 6.6]], "to": [0.6, 4.9], "speed": 4.6})
        legs["X2"] = [{"at": 1.25, "to": [0.3, 3.75], "speed": 3.2},             # helps on the roll
                      {"at": 3.2, "to": [-1.3, 6.3], "speed": 4.4}]               # closes out late
        legs["X5"].append({"at": 2.0, "to": [1.5, 6.4], "speed": 3.6})
        acts["X2"] = [st("O2", 0, 1.25), st("O5", 1.25, 3.2), st("O2", 3.2, 6.0)]
        acts["O2"] = [{"type": "celebrate", "from": 4.75, "to": 5.6}]
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": 2.45, "dribble": True},
                {"type": "pass", "from": "O1", "to": "O2", "t0": 2.45, "t1": 3.1, "style": "chest"},
                {"type": "hold", "player": "O2", "from": 3.1, "to": 3.45},
                {"type": "shot", "player": "O2", "t0": 3.45, "t1": 4.55, "make": True}]
        marks = {"start": 0, "ballscreen": 0.85, "lift": 1.15, "help": 1.25, "roll": 1.5, "pass": 2.45, "catch": 3.1,
                 "release": 3.45, "make": 4.55, "end": 5.6}
        claims = [
            {"type": "near", "a": "X2", "b": "O5", "at": "pass", "max": 1.6, "says": "the shooter's defender helps on the roll"},
            {"type": "far", "a": "X2", "b": "O2", "at": "catch", "min": 3.5, "says": "nobody covers the shooter"},
            {"type": "open", "player": "O2", "at": "release", "min": 2.0, "says": "open three"},
            {"type": "behind_arc", "player": "O2", "at": "catch", "says": "open three"},
            {"type": "order", "marks": ["ballscreen", "lift", "roll", "pass", "catch", "release", "make"], "says": "screen, lift, roll, pass back, three"}]
        return {"id": "stack-a-three", "title": "Stack pick-and-roll A: the shooter's defender helps, pass back for three",
                "duration": 5.6, "concept": "stack-pick-and-roll", "source": SRC, "squareUp": True, "players": PL, "start": S,
                "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O5 screens for O1 with O2 stacked behind him; X5 shows high.",
                          "O5 rolls, O2 lifts to the arc; X2 helps on the roll; O1 passes back to O2: open three."]}
    legs["O5"].append({"at": 1.5, "via": [[0.55, 6.6]], "to": [0.25, 2.85], "speed": 5.3})
    legs["X2"] = [{"at": 1.3, "via": [[-0.7, 6.0]], "to": [-1.85, 7.45], "speed": 4.3}]   # stays with the shooter
    legs["X5"].append({"at": 2.4, "to": [1.2, 5.2], "speed": 4.2})                      # recovers late
    acts["X2"] = [st("O2", 0, 6.0)]
    acts["O5"].append({"type": "celebrate", "from": 4.1, "to": 5.0})
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": 2.35, "dribble": True},
            {"type": "pass", "from": "O1", "to": "O5", "t0": 2.35, "t1": 3.0, "style": "bounce"},
            {"type": "hold", "player": "O5", "from": 3.0, "to": 3.3},
            {"type": "layup", "player": "O5", "t0": 3.3, "t1": 3.7, "make": True}]
    marks = {"start": 0, "ballscreen": 0.85, "lift": 1.15, "stay": 1.3, "roll": 1.5, "pass": 2.35, "catch": 3.0,
             "release": 3.3, "make": 3.7, "end": 5.0}
    claims = [
        {"type": "near", "a": "X2", "b": "O2", "at": "pass", "max": 1.6, "says": "if he stays home"},
        {"type": "far", "a": "X5", "b": "O5", "at": "catch", "min": 2.5, "says": "nobody stops the roll"},
        {"type": "near_rim", "player": "O5", "at": "release", "max": 1.5, "says": "easy two at the rim"},
        {"type": "open", "player": "O5", "at": "release", "min": 1.2, "says": "easy two at the rim"},
        {"type": "order", "marks": ["ballscreen", "lift", "roll", "pass", "catch", "release", "make"], "says": "screen, lift, roll, bounce pass, layup"}]
    return {"id": "stack-b-roll", "title": "Stack pick-and-roll B: the shooter's defender stays home, the roller is alone",
            "duration": 5.0, "concept": "stack-pick-and-roll", "source": SRC, "squareUp": True, "players": PL, "start": S,
            "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start as stack-a-three.", "X2 follows O2 out; nobody between O5 and the rim: bounce pass, layup."]}


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


if __name__ == "__main__":
    for s in (play("three"), play("roll")):
        p = build(s)
        print("built", s["id"], p["duration"])
