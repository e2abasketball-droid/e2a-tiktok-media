#!/usr/bin/env python3
"""GHOST SCREEN: two defenders, two outcomes (owner brief 2026-11-15 17:22Z). Original E2A possession (standard
ghost / slip-out action, generic coaching knowledge, no copied diagram).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. With the house cameras (yaw 0, basket at
the top) x < 0 is the RIGHT of the screen.
  O1 top, a step left of centre (x>0), ball in the RIGHT hand. O2 right wing (x<0). X1 on the ball, X2 on O2.
  O2 jogs up to X1's screen-side shoulder (the side O1 would use = O1's right = x<0), plants ~1.2 m short of X1
  and pops back to the right wing behind the arc. The approach and pop are IDENTICAL in A and B.
  A ghost-a-three   X2 steps to the ball (anticipating a switch/hedge), X1 stays late on the ball -> pass, three, X1 late.
  B ghost-b-reject  X2 stays with O2 out to the wing; X1 jumps toward the screen side -> crossover to the LEFT hand,
                    drive the left lane (x>0), layup; X5 helps late from the right block.
Spacing: O3 left corner, O4 right corner, O5 right dunker spot (X5 = the help, far from the left lane)."""
import json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (standard ghost screen / slip-out read, generic coaching knowledge)"
PL = [P("O1", "O", "Ball handler, top (a step left), ball in the right hand"), P("O2", "O", "Shooter: right wing, ghost screen"),
      P("O3", "O", "Left corner"), P("O4", "O", "Right corner"), P("O5", "O", "Right dunker spot"),
      P("X1", "X", "On the ball", "O1"), P("X2", "X", "On the shooter: steps to the ball (A) / stays (B)", "O2"),
      P("X3", "X", "Left corner", "O3"), P("X4", "X", "Right corner", "O4"), P("X5", "X", "Help from the right block", "O5")]
S = {"O1": [0.9, 9.0], "X1": [0.75, 8.15], "O2": [-4.95, 6.6], "X2": [-4.25, 7.25], "O3": [6.6, 1.4], "X3": [5.65, 2.15],
     "O4": [-6.6, 1.4], "X4": [-5.7, 2.15], "O5": [-2.55, 1.15], "X5": [-1.95, 2.0]}
PLANT = [-0.5, 8.0]
POP = [-4.85, 7.25]
SHARED = {
    "O1": [{"at": 1.25, "to": [0.6, 8.8], "dur": 0.45}],            # sells the screen: a hard step to his right
    "O2": [{"at": 0.5, "via": [[-3.4, 7.3]], "to": PLANT, "speed": 3.4},   # jogs up with intent
           {"at": "+0.17", "via": [[-2.2, 7.8]], "to": POP, "speed": 6.0}],  # plant, hips open, pop
    "X2": [{"at": 0.8, "via": [[-2.9, 8.05]], "to": [-1.45, 8.55], "speed": 3.6}],  # trails on the high (ball) side
}
TM = {}


DB = 12.4


def play(kind):
    legs = {k: [dict(l) for l in v] for k, v in SHARED.items()}
    acts = {"X3": [st("O3", 0, 7.2)], "X4": [st("O4", 0, 7.2)], "X1": [st("O1", 0, 2.5)],
            "O2": [{"type": "gather", "from": TM["arrive"] - 0.06, "to": TM["arrive"] + 0.2}]}
    if kind == "three":
        a = TM["A"]
        legs["X2"].append({"at": 2.45, "to": [0.0, 9.65], "dur": 0.72})            # the step to the ball
        legs["X2"].append({"at": a["pass"] + 0.45, "to": [-1.9, 9.0], "dur": 0.9})     # too late to recover
        legs["X1"] = [{"at": 2.15, "to": [0.62, 8.12], "dur": 0.4},
                      {"at": a["pass"] + 0.12, "via": [[-1.4, 8.0]], "to": [-3.95, 7.55], "speed": 6.2}]  # late close-out
        acts["X1"] = [st("O1", 0, a["pass"] + 0.1), {"type": "contest", "from": a["rel"] + 0.05, "to": a["rel"] + 0.75}]
        acts["X2"] = [st("O1", 2.45, a["pass"] + 0.2)]
        acts["X5"] = [st("O5", 0, 7.2)]
        acts["O2"].append({"type": "celebrate", "from": a["rel"] + 1.25, "to": 7.2})
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": a["pass"], "dribble": True, "hand": 1},
                {"type": "pass", "from": "O1", "to": "O2", "t0": a["pass"], "t1": a["catch"], "style": "chest"},
                {"type": "hold", "player": "O2", "from": a["catch"], "to": a["rel"]},
                {"type": "shot", "player": "O2", "t0": a["rel"], "t1": a["rel"] + 1.1, "make": True, "three": True}]
        marks = {"start": 0, "approach": 0.5, "jab": 1.25, "step": 2.45, "plant": TM["arrive"], "pop": TM["arrive"] + 0.17,
                 "pass": a["pass"], "catch": a["catch"], "release": a["rel"], "make": a["rel"] + 1.1, "end": 7.2}
        claims = [
            {"type": "far", "a": "O2", "b": "X1", "at": "plant", "min": 1.0, "says": "Pop before contact."},
            {"type": "near", "a": "X2", "b": "O1", "at": "pass", "max": 1.3, "says": "When both defenders take the ball..."},
            {"type": "near", "a": "X1", "b": "O1", "at": "pass", "max": 1.3, "says": "When both defenders take the ball..."},
            {"type": "behind_arc", "player": "O2", "at": "catch", "says": "...hit the shooter."},
            {"type": "open", "player": "O2", "at": "release", "min": 1.5, "says": "He beat two defenders without touching either one."},
            {"type": "order", "marks": ["approach", "jab", "step", "plant", "pass", "catch", "release", "make"], "says": "sell, step, pop, pass, three"}]
        return {"id": "ghost2-a-three", "title": "Ghost screen A: both defenders take the ball, the shooter pops for three",
                "duration": 7.2, "concept": "ghost-screen", "source": SRC, "squareUp": True, "players": PL, "start": S,
                "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O2 sells a ball screen on X1's screen-side shoulder, plants ~1.2 m short and pops to the right wing.",
                          "X2 steps to the ball before the pass; X1 stays on the ball and closes out late.", "Chest pass, catch behind the arc, three."]}
    b = TM["B"]
    legs["X2"].append({"at": 2.75, "via": [[-2.8, 8.45]], "to": [-4.05, 8.0], "dur": 1.45})   # stays with the shooter, all the way out
    legs["O1"].append({"at": 3.55, "to": [0.85, 9.05], "dur": 0.7})                                # re-sets, dribble alive
    legs["O1"].append({"at": b["sell"], "to": [-0.45, 8.6], "dur": 0.85})                          # keeps selling: attacks the screen side
    legs["X1"] = [{"at": b["jump"], "to": [-1.05, 7.95], "dur": 0.72},                         # jumps toward the screen side
                  {"at": b["cross"] + 0.3, "via": [[0.3, 7.6], [1.4, 6.0]], "to": [1.55, 4.6], "speed": 5.6}]  # chases late
    legs["O1"].append({"at": b["cross"] + 0.05, "via": [[0.5, 8.2], [1.75, 6.6], [1.7, 4.4]], "to": [0.7, 2.6], "speed": 6.4})
    legs["X5"] = [{"at": b["help"], "to": [-0.3, 2.45], "speed": 5.2}]                       # late help from the block
    acts["X1"] = [st("O1", 0, b["cross"] + 0.3)]
    acts["X2"] = [st("O2", 2.75, DB)]
    acts["X3"] = [st("O3", 0, DB)]
    acts["X4"] = [st("O4", 0, DB)]
    acts["X5"] = [st("O5", 0, b["help"]), {"type": "contest", "from": b["lay"] - 0.05, "to": b["lay"] + 0.5}]
    acts["O1"] = [{"type": "celebrate", "from": b["lay"] + 0.9, "to": DB}]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": b["lay"], "dribble": True, "hand": 1, "cross": [b["cross"]]},
            {"type": "layup", "player": "O1", "t0": b["lay"], "t1": b["lay"] + 0.4, "make": True}]
    marks = {"start": 0, "approach": 0.5, "jab": 1.25, "plant": TM["arrive"], "pop": TM["arrive"] + 0.17, "follow": 2.75,
             "sell": b["sell"], "jump": b["jump"], "cross": b["cross"], "drive": b["cross"] + 0.05, "beat": b["beat"], "help": b["help"],
             "finish": b["lay"], "make": b["lay"] + 0.4, "end": DB}
    claims = [
        {"type": "far", "a": "O2", "b": "X1", "at": "plant", "min": 1.0, "says": "Same fake."},
        {"type": "near", "a": "X2", "b": "O2", "at": "cross", "max": 2.0, "says": "His defender stays with him."},
        {"type": "far", "a": "X1", "b": "O1", "at": "beat", "min": 0.9, "says": "Cross back and attack the other way."},
        {"type": "near_rim", "player": "O1", "at": "finish", "max": 1.6, "says": "...attack the other way."},
        {"type": "far", "a": "X5", "b": "O1", "at": "finish", "min": 0.8, "says": "The help is late."},
        {"type": "near", "a": "X1", "b": "O1", "at": "cross", "max": 1.2, "says": "Yours jumps toward the screen."},
        {"type": "order", "marks": ["approach", "jab", "plant", "follow", "sell", "jump", "cross", "drive", "help", "finish", "make"], "says": "follow, sell, jump, cross back, layup"}]
    return {"id": "ghost2-b-reject", "title": "Ghost screen B: X2 stays home, X1 jumps the screen, reject the other way",
            "duration": DB, "concept": "ghost-screen", "source": SRC, "squareUp": True, "players": PL, "start": S,
            "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start, same approach, same dribble as ghost-a-three.", "O1 keeps selling with two dribbles to the screen side; X1 jumps over to cut him off.",
                      "X2 keeps his shoulder to the shooter and follows him out; X1 jumps toward the screen side.",
                      "O1 crosses to his left hand, wins X1's hip and attacks the left lane; X5 helps late from the right block."]}


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


def first_near(tr, pt, r=0.35, after=0.0):
    t = after
    while t <= tr[-1][0]:
        q = pos(tr, t)
        if ((q[0] - pt[0]) ** 2 + (q[1] - pt[1]) ** 2) ** 0.5 <= r:
            return t
        t += 0.005
    return None


if __name__ == "__main__":
    TM.update(arrive=2.63, A={"pass": 3.2, "catch": 3.9, "rel": 4.25}, B={"sell": 5.75, "jump": 6.4, "cross": 8.1, "beat": 8.85, "help": 9.25, "lay": 9.85})
    tr = build(play("three"))["tracks"]
    TM["arrive"] = round(first_near(tr["O2"], PLANT, 0.02) or 2.63, 3)
    pop_end = first_near(tr["O2"], POP, 0.15, TM["arrive"] + 0.3)
    TM["A"]["catch"] = round(pop_end, 3)
    TM["A"]["pass"] = round(pop_end - 0.62, 3)
    TM["A"]["rel"] = round(pop_end + 0.38, 3)
    tr = build(play("reject"))["tracks"]
    lay = first_near(tr["O1"], [0.7, 2.6], 0.25, TM["B"]["cross"]) or 9.85
    TM["B"]["lay"] = round(lay, 3)
    TM["B"]["help"] = round(lay - 0.6, 3)
    TM["B"]["beat"] = round(first_near(tr["O1"], [1.75, 6.6], 0.3, TM["B"]["cross"]) or 8.85, 3)
    for s in (play("three"), play("reject")):
        build(s)
        print("built", s["id"], json.dumps(s["marks"]))
