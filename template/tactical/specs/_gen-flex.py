#!/usr/bin/env python3
"""FLEX ACTION: screen the screener (owner brief 2026-11-15 21:45Z). Original E2A possession (standard flex action,
generic coaching knowledge, no copied diagram).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Half-court view with the basket at the
top (yaw 0): x > 0 is the LEFT of the screen.
  O1 ball, high left. O2 high right (gets the reversal). O3 left corner. O5 left low post (flex screener).
  O4 right wing, holds the weak side. O5 sets the baseline (flex) screen, O3 cuts over it to the right side of the rim;
  after the pass O1 goes down and screens for O5 (screen the screener); O5 comes up to the left elbow.
  A flex-a-elbow  X5 steps to the cut, X3 chases and recovers on the cutter; X5 is late through O1's screen -> O5 elbow jumper.
  B flex-b-rim    X5 stays home with O5, X3 is caught on the flex screen -> O2 hits O3 cutting, layup."""
import json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (standard flex action / screen-the-screener read, generic coaching knowledge)"
PL = [P("O1", "O", "Ball handler, high left; passes, then screens the screener"), P("O2", "O", "High right: gets the reversal, reads"),
      P("O3", "O", "Left corner: flex cutter"), P("O4", "O", "Right wing: weak-side spacing"), P("O5", "O", "Left block: first screener, then the shooter"),
      P("X1", "X", "On O1", "O1"), P("X2", "X", "On O2", "O2"), P("X3", "X", "On the cutter", "O3"),
      P("X4", "X", "Weak side", "O4"), P("X5", "X", "On the first screener", "O5")]
S = {"O1": [3.2, 8.0], "X1": [2.75, 7.3], "O2": [-3.2, 8.0], "X2": [-2.75, 7.15], "O3": [6.6, 1.3], "X3": [5.8, 1.85],
     "O4": [-6.3, 4.8], "X4": [-5.4, 4.6], "O5": [2.25, 2.35], "X5": [1.6, 2.0]}
FLEX = [3.7, 1.35]      # O5's baseline screen spot
DOWN = [3.05, 3.55]     # O1's down screen spot
ELBOW = [2.4, 5.9]
SHARED = {
    "O5": [{"at": 0.25, "to": FLEX, "dur": 0.7}],
    "O3": [{"at": 1.45, "via": [[4.55, 1.95], [3.5, 2.25], [2.2, 1.85], [1.2, 1.55]], "to": [0.5, 1.45], "speed": 5.3}],
    "O1": [{"at": 1.35, "via": [[3.25, 6.0]], "to": DOWN, "speed": 4.8}],
    "X1": [{"at": 1.4, "via": [[2.55, 5.8]], "to": [2.65, 4.1], "speed": 3.9}],
}


def play(kind):
    legs = {k: [dict(l) for l in v] for k, v in SHARED.items()}
    acts = {"X2": [st("O2", 0, 7.2)], "X4": [st("O4", 0, 7.2)], "X1": [st("O1", 0, 1.5)],
            "O5": [{"type": "screen", "from": 0.95, "to": 2.35, "face": "X3"}],
            "O1": [{"type": "screen", "from": TM["set"], "to": 3.95, "face": "X5"}]}
    if kind == "elbow":
        legs["X5"] = [{"at": 1.85, "to": [1.2, 2.55], "dur": 0.5},                                 # the help step toward the cut
                      {"at": 3.1, "to": [2.45, 3.1], "dur": 0.7},                                    # tries to come back...
                      {"at": 3.85, "via": [[2.0, 3.8]], "to": [2.05, 4.0], "speed": 3.4}]            # ...around O1, late
        legs["O3"].append({"at": "+0", "to": [-0.95, 1.15], "dur": 0.8})
        legs["X3"] = [{"at": 1.3, "to": [5.6, 2.4], "dur": 0.45},
                      {"at": 1.85, "via": [[4.6, 2.55], [3.6, 2.7], [2.2, 2.05], [1.0, 1.95]], "to": [0.0, 2.45], "speed": 5.0}]
        legs["O5"].append({"at": 3.05, "via": [[4.6, 3.3], [4.35, 4.45]], "to": ELBOW, "speed": 5.8})
        acts["X5"] = [st("O5", 0, 1.85), st("O3", 1.85, 3.1), {"type": "bump", "from": 3.5, "to": 3.85}, {"type": "contest", "from": 4.95, "to": 5.6}]
        acts["X3"] = [st("O3", 0, 1.5), st("O3", 3.2, 7.2)]
        acts["O5"].append({"type": "gather", "from": 4.5, "to": 4.75})
        acts["O5"].append({"type": "celebrate", "from": 6.3, "to": 7.2})
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": 0.3, "dribble": False},
                {"type": "pass", "from": "O1", "to": "O2", "t0": 0.3, "t1": 0.9, "style": "chest"},
                {"type": "hold", "player": "O2", "from": 0.9, "to": 4.0},
                {"type": "pass", "from": "O2", "to": "O5", "t0": 4.0, "t1": 4.6, "style": "chest"},
                {"type": "hold", "player": "O5", "from": 4.6, "to": 4.95},
                {"type": "shot", "player": "O5", "t0": 4.95, "t1": 6.0, "make": True, "three": False}]
        marks = {"start": 0, "reverse": 0.3, "flex": 0.95, "cut": 1.45, "help": 1.85, "down": 1.45, "set": TM["set"], "up": 3.05,
                 "bump": 3.5, "pass": 4.0, "catch": 4.6, "release": 4.95, "make": 6.0, "end": 7.2}
        claims = [
            {"type": "near", "a": "X5", "b": "O3", "at": "set", "max": 2.2, "says": "the baseline screen pulls help toward the rim"},
            {"type": "near", "a": "X3", "b": "O3", "at": "pass", "max": 1.8, "says": "X3 recovers on the cutter"},
            {"type": "far", "a": "X5", "b": "O5", "at": "catch", "min": 1.0, "says": "Now he's open at the elbow."},
            {"type": "order", "marks": ["reverse", "flex", "cut", "help", "set", "up", "pass", "catch", "release", "make"], "says": "reverse, flex cut, down screen, elbow"}]
        return {"id": "flex-a-elbow", "title": "Flex A: help on the cut, the screener's screener gets the elbow shot", "duration": 7.2,
                "concept": "flex-action", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
                "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O1 reverses to O2; O5 sets the baseline screen; O3 cuts over it to the right side of the rim.",
                          "X5 steps to the cut; O1 goes down and screens for O5; X5 is late around O1; O5 catches at the left elbow."]}
    legs["X5"] = [{"at": 1.2, "to": [3.05, 0.95], "dur": 0.9},                                     # stays home with O5 (baseline side)
                  {"at": 3.1, "to": [3.2, 2.6], "dur": 0.8}]
    legs["X2"] = [{"at": 1.6, "to": [-2.2, 7.9], "dur": 0.5}]
    legs["X3"] = [{"at": 1.3, "to": [5.6, 2.4], "dur": 0.45},
                  {"at": 2.05, "via": [[4.9, 2.6], [3.8, 2.9]], "to": [2.0, 2.5], "speed": 4.0}]  # caught on the flex screen
    legs["O3"].append({"at": "+0", "to": [-0.7, 1.2], "dur": 0.8})                                  # under control for the catch
    legs["O5"].append({"at": 3.05, "via": [[3.8, 3.3]], "to": [3.3, 4.4], "speed": 4.0})
    acts["X5"] = [st("O5", 0, 5.0)]
    acts["X3"] = [st("O3", 0, 1.9), {"type": "bump", "from": 2.15, "to": 2.5}]
    acts["O3"] = [{"type": "celebrate", "from": TB["catch"] + 1.1, "to": 5.0}]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": 0.3, "dribble": False},
            {"type": "pass", "from": "O1", "to": "O2", "t0": 0.3, "t1": 0.9, "style": "chest"},
            {"type": "hold", "player": "O2", "from": 0.9, "to": TB["pass"]},
            {"type": "pass", "from": "O2", "to": "O3", "t0": TB["pass"], "t1": TB["catch"], "style": "chest"},
            {"type": "hold", "player": "O3", "from": TB["catch"], "to": TB["catch"] + 0.3},
            {"type": "layup", "player": "O3", "t0": TB["catch"] + 0.3, "t1": TB["catch"] + 0.7, "make": True}]
    marks = {"start": 0, "reverse": 0.3, "flex": 0.95, "cut": 1.45, "stay": 1.85, "caught": 2.15, "pass": TB["pass"], "catch": TB["catch"],
             "finish": TB["catch"] + 0.3, "make": TB["catch"] + 0.7, "end": 5.0}
    claims = [
        {"type": "near", "a": "X5", "b": "O5", "at": "pass", "max": 1.6, "says": "X5 stays with the screener"},
        {"type": "far", "a": "X3", "b": "O3", "at": "pass", "min": 1.5, "says": "If the cutter's open first..."},
        {"type": "near_rim", "player": "O3", "at": "finish", "max": 1.7, "says": "...hit him at the rim."},
        {"type": "order", "marks": ["reverse", "flex", "cut", "stay", "pass", "catch", "finish", "make"], "says": "reverse, flex cut, pass, layup"}]
    return {"id": "flex-b-rim", "title": "Flex B: X5 stays home, the cutter is open at the rim", "duration": 5.0,
            "concept": "flex-action", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
            "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start as flex-a-elbow.", "X5 stays with O5; X3 is caught on the flex screen; O2 hits O3 in stride, layup."]}


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


TM = {"set": 2.85}
TB = {"pass": 2.3, "catch": 2.95}

if __name__ == "__main__":
    tr = build(play("rim"))["tracks"]
    TM["set"] = round(first_near(tr["O1"], DOWN, 0.03) + 0.08, 2)
    ta = first_near(tr["O3"], [0.5, 1.45], 0.05)
    TB["catch"] = round(ta + 0.2, 2)
    TB["pass"] = round(TB["catch"] - 0.65, 2)
    print("TM", TM, "TB", TB)
    for s in (play("elbow"), play("rim")):
        p = build(s)
        tr = p["tracks"]
        print("built", s["id"], {k: v[-1][0] for k, v in tr.items() if k in ("O1", "O3", "O5", "X5", "X3")})
