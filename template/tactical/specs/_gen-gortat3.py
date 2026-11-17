#!/usr/bin/env python3
"""GORTAT SCREEN V3 (owner 2026-11-17 01:17Z: the big rolls and seals FIRST, then the guard attacks the middle). Based on V2 (owner correction 2026-11-17 00:10Z): the ball screen is on the WING (45 degrees, right side of the
court), the guard uses it to his RIGHT, then snakes back to the middle; the big turns and screens his own drop defender
(the Gortat screen) so the guard attacks the middle with his LEFT hand.
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Offense right side = x < 0.
  A gortat3-a-seal   help stays home -> O1 attacks the middle, layup.
  B gortat3-b-kick   X4 (low man, weak-side/left corner) helps -> kick-out to O4 in the left corner: open three."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (generic high pick-and-roll vs drop + 'Gortat' seal screen on the drop big, generic coaching knowledge)"
PL = [P("O1", "O", "Ball handler: comes off the ball screen, attacks the lane"),
      P("O2", "O", "Strong-side corner"), P("O3", "O", "Weak-side wing"),
      P("O4", "O", "Weak-side corner shooter"), P("O5", "O", "Big: ball screen, then the Gortat screen on his own man"),
      P("X1", "X", "On the ball: chases over, stuck on the back hip", "O1"), P("X2", "X", "Strong-side corner", "O2"),
      P("X3", "X", "Weak-side wing", "O3"), P("X4", "X", "Low man: stays home or helps", "O4"),
      P("X5", "X", "On the big: drop coverage", "O5")]
S = {"O1": [-5.1, 7.2], "X1": [-4.5, 6.55], "O5": [-2.0, 5.3], "X5": [-1.6, 4.7],
     "O2": [-6.75, 1.3], "X2": [-5.8, 2.0], "O3": [4.9, 7.2], "X3": [4.1, 6.5], "O4": [6.8, 1.2], "X4": [4.5, 2.3]}
SCR = [-4.98, 6.11]        # ball screen spot (on X1's baseline side = the guard's right)
SEAL = [-1.05, 4.0]       # Gortat screen spot
DROP = [-1.6, 3.35]        # where X5 sits in the drop
OFF = [-4.9, 4.55]         # the guard comes off the screen
GATHER_A = [0.3, 2.55]     # layup (middle, left hand)
GATHER_B = [-0.4, 4.6]     # stops in the middle, kicks out
TM = {"seal": 4.3, "pa": 8.0, "lay": 8.0, "roll": 2.5, "help": 6.0, "go": 4.5}


def base():
    legs = {"O5": [{"at": 0.2, "to": SCR, "speed": 3.6},
                   {"at": TM["roll"], "via": [[-3.2, 4.3]], "to": SEAL, "speed": 6.2}],
            "O1": [{"at": 1.45, "via": [[-5.75, 6.6]], "to": [-5.6, 5.2], "speed": 3.0},
                   {"at": "+0.0", "to": OFF, "speed": 3.0},
                   {"at": TM["go"], "via": [[-3.4, 4.95]], "to": [-1.9, 5.35], "speed": 3.3}],
            "X1": [{"at": 1.6, "via": [[-5.45, 7.05], [-6.1, 6.0]], "to": [-5.7, 4.95], "speed": 3.2},
                   {"at": TM["go"] + 0.1, "via": [[-4.3, 5.85]], "to": [-2.8, 6.15], "speed": 4.2}],
            "X5": [{"at": 1.2, "to": DROP, "speed": 2.6}]}
    acts = {"O5": [{"type": "screen", "from": 1.45, "to": 2.0, "face": "X1"}],
            "X5": [st("O1", 0, 8.0)], "X2": [st("O1", 0, 8.0)], "X3": [st("O1", 0, 8.0)], "X4": [st("O1", 0, 8.0)],
            "X1": [st("O1", 0, 1.2)]}
    return legs, acts


def play(kind):
    legs, acts = base()
    seal = TM["seal"]
    acts["O5"].append({"type": "screen", "from": seal, "to": seal + 3.4, "face": "X5"})
    if kind == "seal":
        legs["O1"].append({"at": "+0.0", "via": [[-0.6, 4.9]], "to": GATHER_A, "speed": 4.6})
        legs["X1"].append({"at": "+0.0", "via": [[-1.4, 5.95]], "to": [-0.6, 4.8], "speed": 3.3})
        legs["X4"] = [{"at": 2.0, "to": [5.2, 1.9], "speed": 2.0}]                  # stays home on the shooter
        lay = TM["lay"]
        acts["O1"] = [{"type": "celebrate", "from": lay + 1.3, "to": lay + 2.4}]
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": lay, "dribble": True},
                {"type": "layup", "player": "O1", "t0": lay, "t1": lay + 0.4, "make": True}]
        marks = {"start": 0, "screen": 1.45, "over": 2.1, "drop": 2.4, "seal": seal, "drive": TM["go"] + 0.2,
                 "finish": lay, "make": lay + 0.4, "end": lay + 2.4}
        claims = [
            {"type": "near", "a": "O5", "b": "X1", "at": "screen", "max": 1.0, "says": "The big sets a ball screen on the wing..."},
            {"type": "far", "a": "X5", "b": "O1", "at": "drop", "min": 2.5, "says": "...and his defender drops back to protect the rim."},
            {"type": "near", "a": "O5", "b": "X5", "at": "seal", "max": 1.0, "says": "The big turns and screens his own defender in the paint."},
            {"type": "far", "a": "X5", "b": "O1", "at": "finish", "min": 1.5, "says": "The big defender is sealed: the middle is open."},
            {"type": "near_rim", "player": "O1", "at": "finish", "max": 1.5, "says": "Drive. Finish. Two points."},
            {"type": "order", "marks": ["screen", "drop", "seal", "drive", "finish", "make"], "says": "ball screen, drop, seal, layup"}]
        return {"id": "gortat3-a-seal", "title": "Gortat A: the drop big gets sealed, layup", "duration": lay + 2.4,
                "concept": "gortat-screen", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs,
                "ball": ball, "marks": marks, "actions": acts, "claims": claims,
                "notes": ["High ball screen; X5 drops; X1 chases over and trails.",
                          "O5 rolls and screens X5 in the paint (stationary); X4 stays home; O1 layup."]}
    pa = TM["pa"]
    legs["O1"].append({"at": "+0.0", "to": GATHER_B, "speed": 4.2})
    legs["X1"].append({"at": "+0.0", "to": [-1.5, 5.6], "speed": 4.0})
    legs["X4"] = [{"at": TM["help"], "via": [[2.4, 2.9]], "to": [0.25, 3.3], "speed": 5.2}]     # low man rotates to the middle
    legs["X3"] = [{"at": pa + 0.3, "to": [5.0, 4.2], "speed": 4.0}]                   # late closeout from the wing
    acts["X3"] = [st("O4", pa + 0.3, 8.0)]
    acts["O4"] = [{"type": "celebrate", "from": pa + 2.5, "to": pa + 3.4}]
    t1 = pa + 0.65
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": pa, "dribble": True},
            {"type": "pass", "from": "O1", "to": "O4", "t0": pa, "t1": t1},
            {"type": "hold", "player": "O4", "from": t1, "to": t1 + 0.35},
            {"type": "shot", "player": "O4", "t0": t1 + 0.35, "t1": t1 + 1.45, "make": True}]
    marks = {"start": 0, "screen": 1.45, "over": 2.1, "drop": 2.4, "seal": seal, "help": pa - 0.1, "pass": pa,
             "catch": t1, "shoot": t1 + 0.35, "make": t1 + 1.45, "end": pa + 3.4}
    claims = [
        {"type": "near", "a": "O5", "b": "X5", "at": "seal", "max": 1.0, "says": "Same seal on the drop big."},
        {"type": "near", "a": "X4", "b": "O1", "at": "help", "max": 2.2, "says": "The corner defender steps in to stop the drive."},
        {"type": "open", "player": "O4", "at": "shoot", "min": 1.8, "says": "The shooter in the corner is left alone."},
        {"type": "behind_arc", "player": "O4", "at": "shoot", "says": "Open three."},
        {"type": "order", "marks": ["screen", "drop", "seal", "help", "pass", "catch", "shoot", "make"], "says": "seal, help, kick-out, three"}]
    return {"id": "gortat3-b-kick", "title": "Gortat B: the low man helps, kick-out corner three", "duration": pa + 3.4,
            "concept": "gortat-screen", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs,
            "ball": ball, "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start as gortat-a-seal.", "X4 rotates to stop the drive; O1 kicks to O4 in the corner: open three."]}


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


def arrive(tr, pt, after=0.0, r=0.03):
    for a, b in zip(tr, tr[1:]):
        if b[0] >= after and abs(b[1] - pt[0]) < r and abs(b[2] - pt[1]) < r:
            return b[0]
    return None


if __name__ == "__main__":
    ta = build(play("seal"))["tracks"]
    TM["roll"] = round(arrive(ta["O1"], [-5.6, 5.2], 1.5) + 0.05, 2)
    ta = build(play("seal"))["tracks"]
    TM["seal"] = round(arrive(ta["O5"], SEAL, 1.9) + 0.1, 2)
    TM["go"] = round(TM["seal"] + 0.15, 2)
    TM["help"] = round(TM["go"] + 1.35, 2)
    ta = build(play("seal"))["tracks"]
    TM["lay"] = round(arrive(ta["O1"], GATHER_A, 2.0) + 0.05, 2)
    tb = build(play("kick"))["tracks"]
    TM["pa"] = round(max(arrive(tb["O1"], GATHER_B, 2.0), arrive(tb["X4"], [0.25, 3.3], 2.0) - 0.15) + 0.05, 2)
    print("TM", TM)
    for s in (play("seal"), play("kick")):
        p = build(s)
        print("built", s["id"], p["duration"])
