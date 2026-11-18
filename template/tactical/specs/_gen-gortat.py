#!/usr/bin/env python3
"""GORTAT SCREEN (owner request 2026-11-16 16:55Z, same format as Elevator 3D). Original E2A possession
(generic coaching knowledge: high pick-and-roll vs drop coverage; the roller turns and seals his OWN defender in the paint).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Basket at the top (yaw 0): x > 0 is screen-left.
  O5 sets a high ball screen for O1; X5 drops to protect the rim; X1 chases over and is kept on O1's back hip.
  O5 rolls but stops in the paint and screens X5 (stationary, no hold): the Gortat screen. O1 attacks the lane.
  A gortat-a-seal    X4 (low man, weak-side corner) stays home -> lane open: O1 layup.
  B gortat-b-kick    X4 rotates in to stop the drive -> O1 kicks to O4 in the weak-side corner: open three."""
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
S = {"O1": [-0.35, 9.6], "X1": [-0.3, 8.75], "O5": [1.4, 6.3], "X5": [0.95, 5.6],
     "O2": [6.75, 1.3], "X2": [5.8, 2.0], "O3": [-5.0, 7.2], "X3": [-4.2, 6.5], "O4": [-6.8, 1.2], "X4": [-4.6, 2.3]}
SCR = [0.35, 8.8]          # ball screen spot (right of X1)
SEAL = [0.85, 4.55]        # Gortat screen spot
DROP = [0.12, 4.25]        # where X5 sits in the drop
GATHER_A = [0.95, 2.5]     # layup
GATHER_B = [1.55, 3.95]    # stops the drive, kicks out
TM = {"seal": 3.0, "pa": 3.4, "lay": 3.5}


def base():
    legs = {"O5": [{"at": 0.2, "to": SCR, "speed": 3.6},
                   {"at": 2.45, "via": [[0.75, 7.0]], "to": SEAL, "speed": 5.0}],
            "O1": [{"at": 1.05, "via": [[0.9, 9.9]], "to": [2.0, 8.3], "speed": 3.0},
                   {"at": "+0.0", "to": [1.8, 5.6], "speed": 4.4}],
            "X1": [{"at": 1.25, "via": [[-0.1, 9.75], [1.4, 10.15]], "to": [2.6, 8.4], "speed": 3.2},
                   {"at": "+0.0", "to": [2.3, 5.9], "speed": 4.4}],
            "X5": [{"at": 1.0, "to": DROP, "speed": 2.6}]}
    acts = {"O5": [{"type": "screen", "from": 1.25, "to": 1.8, "face": "X1"}],
            "X5": [st("O1", 0, 8.0)], "X2": [st("O1", 0, 8.0)], "X3": [st("O1", 0, 8.0)], "X4": [st("O1", 0, 8.0)],
            "X1": [st("O1", 0, 1.2)]}
    return legs, acts


def play(kind):
    legs, acts = base()
    seal = TM["seal"]
    acts["O5"].append({"type": "screen", "from": seal, "to": seal + 1.4, "face": "X5"})
    if kind == "seal":
        legs["O1"].append({"at": "+0.0", "via": [[1.7, 3.9]], "to": GATHER_A, "speed": 4.6})
        legs["X1"].append({"at": "+0.0", "via": [[2.25, 4.1]], "to": [1.95, 3.0], "speed": 4.3})
        legs["X4"] = [{"at": 2.0, "to": [-5.2, 1.9], "speed": 2.0}]                  # stays home on the shooter
        lay = TM["lay"]
        acts["O1"] = [{"type": "celebrate", "from": lay + 1.3, "to": lay + 2.4}]
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": lay, "dribble": True},
                {"type": "layup", "player": "O1", "t0": lay, "t1": lay + 0.4, "make": True}]
        marks = {"start": 0, "screen": 1.25, "over": 1.9, "drop": 2.2, "seal": seal, "drive": seal + 0.2,
                 "finish": lay, "make": lay + 0.4, "end": lay + 2.4}
        claims = [
            {"type": "near", "a": "O5", "b": "X1", "at": "screen", "max": 1.0, "says": "The big sets a high ball screen..."},
            {"type": "far", "a": "X5", "b": "O1", "at": "drop", "min": 2.5, "says": "...and his defender drops back to protect the rim."},
            {"type": "near", "a": "O5", "b": "X5", "at": "seal", "max": 1.0, "says": "The big turns and screens his own defender in the paint."},
            {"type": "far", "a": "X5", "b": "O1", "at": "finish", "min": 1.5, "says": "The big defender is sealed: the lane is open."},
            {"type": "near_rim", "player": "O1", "at": "finish", "max": 1.5, "says": "Drive. Finish. Two points."},
            {"type": "order", "marks": ["screen", "over", "drop", "seal", "drive", "finish", "make"], "says": "ball screen, drop, seal, layup"}]
        return {"id": "gortat-a-seal", "title": "Gortat A: the drop big gets sealed, layup", "duration": lay + 2.4,
                "concept": "gortat-screen", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs,
                "ball": ball, "marks": marks, "actions": acts, "claims": claims,
                "notes": ["High ball screen; X5 drops; X1 chases over and trails.",
                          "O5 rolls and screens X5 in the paint (stationary); X4 stays home; O1 layup."]}
    pa = TM["pa"]
    legs["O1"].append({"at": "+0.0", "to": GATHER_B, "speed": 4.2})
    legs["X1"].append({"at": "+0.0", "to": [2.3, 4.9], "speed": 4.0})
    legs["X4"] = [{"at": 3.0, "via": [[-2.4, 2.5]], "to": [0.55, 2.55], "speed": 5.2}]     # low man rotates to the rim
    legs["X3"] = [{"at": pa + 0.3, "to": [-5.0, 4.2], "speed": 4.0}]                   # late closeout from the wing
    acts["X3"] = [st("O4", pa + 0.3, 8.0)]
    acts["O4"] = [{"type": "celebrate", "from": pa + 2.5, "to": pa + 3.4}]
    t1 = pa + 0.65
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": pa, "dribble": True},
            {"type": "pass", "from": "O1", "to": "O4", "t0": pa, "t1": t1},
            {"type": "hold", "player": "O4", "from": t1, "to": t1 + 0.35},
            {"type": "shot", "player": "O4", "t0": t1 + 0.35, "t1": t1 + 1.45, "make": True}]
    marks = {"start": 0, "screen": 1.25, "over": 1.9, "drop": 2.2, "seal": seal, "help": pa - 0.1, "pass": pa,
             "catch": t1, "shoot": t1 + 0.35, "make": t1 + 1.45, "end": pa + 3.4}
    claims = [
        {"type": "near", "a": "O5", "b": "X5", "at": "seal", "max": 1.0, "says": "Same seal on the drop big."},
        {"type": "near", "a": "X4", "b": "O1", "at": "help", "max": 2.2, "says": "The corner defender steps in to stop the drive."},
        {"type": "open", "player": "O4", "at": "shoot", "min": 1.8, "says": "The shooter in the corner is left alone."},
        {"type": "behind_arc", "player": "O4", "at": "shoot", "says": "Open three."},
        {"type": "order", "marks": ["screen", "drop", "seal", "help", "pass", "catch", "shoot", "make"], "says": "seal, help, kick-out, three"}]
    return {"id": "gortat-b-kick", "title": "Gortat B: the low man helps, kick-out corner three", "duration": pa + 3.4,
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
    TM["seal"] = round(arrive(ta["O5"], SEAL, 1.9) + 0.1, 2)
    ta = build(play("seal"))["tracks"]
    TM["lay"] = round(arrive(ta["O1"], GATHER_A, 2.0) + 0.05, 2)
    tb = build(play("kick"))["tracks"]
    TM["pa"] = round(max(arrive(tb["O1"], GATHER_B, 2.0), arrive(tb["X4"], [0.55, 2.55], 2.0) - 0.15) + 0.05, 2)
    print("TM", TM)
    for s in (play("seal"), play("kick")):
        p = build(s)
        print("built", s["id"], p["duration"])
