#!/usr/bin/env python3
"""VEER ACTION (owner brief 2026-11-16 03:27Z). Original E2A possession (standard veer / ball screen into a down screen
for the shooter, generic coaching knowledge, no copied diagram).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Yaw 0 = basket at the top, x<0 = screen RIGHT.
  O1 top, ball in the right hand. O5 comes up from the right elbow and screens X1 on his x<0 shoulder.
  O1 comes off tight and attacks the right lane to the nail; X5 sits in drop.
  O2 (shooter) waits LOW on the right (x<0), the side O5 veers to. X2 guards him.
  After the ball screen O5 does NOT roll: he veers down to the right and plants a down screen on X2.
  A veer-a-kick   X2 takes a real help step to the drive (chest to the ball) -> O5 screens him -> O2 shoulder to shoulder
                  off the screen up to the right wing -> O1 kicks it out -> three, X2 late.
  B veer-b-curl   X2 stays attached to O2 (no help) -> trails on his back over the screen -> O2 plants, curls tight around
                  O5 into the lane -> O1 leads him -> catch in stride, layup; X5 late from the drop.
Weak side: O3 left corner, O4 left wing."""
import json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (standard veer action: ball screen into a down screen for the shooter, generic coaching knowledge)"
PL = [P("O1", "O", "Guard, top: uses the ball screen, attacks the lane, reads the corner defender"),
      P("O2", "O", "Shooter: waits low on the right, comes off the veer screen"),
      P("O3", "O", "Left corner"), P("O4", "O", "Left wing"),
      P("O5", "O", "Big: ball screen, then veers into a down screen on the shooter's defender"),
      P("X1", "X", "On the ball", "O1"), P("X2", "X", "On the shooter: helps (A) / chases (B)", "O2"),
      P("X3", "X", "Left corner", "O3"), P("X4", "X", "Left wing", "O4"), P("X5", "X", "On the big: drop", "O5")]
S = {"O1": [1.25, 8.85], "X1": [1.0, 8.0], "O5": [-1.7, 5.7], "X5": [-1.0, 4.9], "O2": [-6.0, 2.6], "X2": [-5.2, 2.85],
     "O3": [6.4, 1.5], "X3": [5.55, 2.2], "O4": [4.9, 7.1], "X4": [4.15, 6.45]}
BALLSCR = [0.22, 8.2]
NAIL = [-1.3, 6.25]
VEER = [-4.5, 4.6]
WING = [-5.5, 6.75]
T1 = {"set": 0.95, "drive": 1.1}


def shared():
  return {
    "O5": [{"at": 0.0, "to": BALLSCR, "speed": 5.2},
           {"at": 2.4, "via": [[-1.5, 8.7], [-3.5, 6.55]], "to": VEER, "speed": 6.3}],   # veers instead of rolling, brakes, plants
    "O1": [{"at": T1["drive"], "via": [[-0.18, 8.8]], "to": NAIL, "speed": 3.7}],               # tight off the screen, attacks the lane
    "X1": [{"at": T1["drive"] + 0.3, "via": [[0.65, 8.95], [-0.15, 9.0]], "to": [-0.85, 7.35], "speed": 4.0}],  # hit by the screen, over the top, trails
    "X5": [{"at": 0.3, "to": [-0.35, 5.6], "dur": 0.9}],                                  # drop
}
TA, TB = {}, {}
DUR_A, DUR_B = 7.6, 8.2


def play(kind):
    legs = {k: [dict(l) for l in v] for k, v in shared().items()}
    acts = {"X3": [st("O3", 0, 8)], "X4": [st("O4", 0, 8)], "X1": [st("O1", 0, 1.15), {"type": "bump", "from": 1.12, "to": 1.42}],
            "O5": [{"type": "screen", "from": T1["set"], "to": 2.35, "face": "X1"}],
            "X5": [st("O1", 0, 8)]}
    if kind == "kick":
        a = TA
        dur = DUR_A
        legs["X2"] = [{"at": 1.5, "to": [-3.85, 3.75], "dur": 0.7},                              # the help step, chest to the ball
                      {"at": a["go"] + 0.5, "via": [[-3.35, 4.15]], "to": [-3.55, 4.45], "speed": 3.2}]  # around the screen, late
        legs["O2"] = [{"at": a["go"], "via": [[-5.12, 4.25]], "to": WING, "speed": 5.8}]
        legs["O1"].append({"at": a["go"] - 0.15, "to": [-1.75, 7.0], "dur": 0.7})               # hang dribble back up: a clear passing line over the screen
        legs["O1"].append({"at": "+0.35", "to": [-1.4, 7.3], "dur": 0.8})
        acts["O5"].append({"type": "screen", "from": a["set"] - 0.05, "to": a["go"] + 1.0, "face": "X2"})
        acts["X2"] = [st("O2", 0, 1.5), st("O1", 1.5, a["go"] + 0.5), {"type": "bump", "from": a["go"] + 0.45, "to": a["go"] + 0.75},
                      {"type": "contest", "from": a["rel"] + 0.05, "to": a["rel"] + 0.8}]
        acts["O2"] = [{"type": "gather", "from": a["catch"] - 0.08, "to": a["rel"]}, {"type": "celebrate", "from": a["rel"] + 1.3, "to": dur}]
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": a["pass"], "dribble": True, "hand": 1},
                {"type": "pass", "from": "O1", "to": "O2", "t0": a["pass"], "t1": a["catch"], "style": "chest"},
                {"type": "hold", "player": "O2", "from": a["catch"], "to": a["rel"]},
                {"type": "shot", "player": "O2", "t0": a["rel"], "t1": a["rel"] + 1.1, "make": True, "three": True}]
        marks = {"start": 0, "screen1": T1["set"], "drive": T1["drive"], "help": 1.5, "veer": 2.4, "set": a["set"], "go": a["go"],
                 "pass": a["pass"], "catch": a["catch"], "release": a["rel"], "make": a["rel"] + 1.1, "end": dur}
        claims = [
            {"type": "near", "a": "X2", "b": "O1", "at": "set", "max": 3.6, "says": "The corner defender steps in to help."},
            {"type": "far", "a": "X2", "b": "O2", "at": "pass", "min": 1.4, "says": "That's the Veer."},
            {"type": "behind_arc", "player": "O2", "at": "catch", "says": "Help? Kick it out."},
            {"type": "open", "player": "O2", "at": "release", "min": 1.3, "says": "open three"},
            {"type": "order", "marks": ["screen1", "drive", "help", "veer", "set", "go", "pass", "catch", "release", "make"], "says": "ball screen, drive, help, veer, kick-out, three"}]
        return {"id": "veer-a-kick", "title": "Veer A: the corner defender helps, the big screens him, kick-out three",
                "duration": dur, "concept": "veer-action", "source": SRC, "squareUp": True, "players": PL, "start": S,
                "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O5 sets the ball screen, then veers down instead of rolling and plants a down screen on X2.",
                          "X2 helped on O1's drive; O2 comes off shoulder to shoulder to the right wing; kick-out, three."]}
    b = TB
    dur = DUR_B
    legs["X2"] = [{"at": 1.6, "to": [-5.05, 2.95], "dur": 0.4},                                   # stays attached
                  {"at": b["go"] + 0.58, "via": [[-5.85, 3.5], [-5.85, 4.65], [-5.55, 5.65]], "to": [-4.8, 6.15], "speed": 4.9},  # trails over the top
                  {"at": "+0", "via": [[-3.6, 5.6]], "to": [-2.75, 4.7], "speed": 5.0}]       # chases late
    legs["O2"] = [{"at": b["go"], "via": [[-5.35, 4.2], [-5.42, 4.95], [-5.05, 5.6], [-4.25, 5.78], [-3.3, 5.15], [-2.4, 4.1], [-1.6, 3.15]], "to": [-0.7, 2.35], "speed": 4.25}]
    legs["X5"].append({"at": b["catch"] - 0.55, "to": [0.2, 3.35], "dur": 0.95})              # late help from the drop
    acts["O5"].append({"type": "screen", "from": b["set"] - 0.05, "to": b["go"] + 1.2, "face": "X2"})
    acts["X2"] = [st("O2", 0, b["go"] + 0.1)]
    acts["X5"] = [st("O1", 0, b["catch"] - 0.55), {"type": "contest", "from": b["lay"] - 0.05, "to": b["lay"] + 0.5}]
    acts["O2"] = [{"type": "celebrate", "from": b["lay"] + 0.9, "to": dur}]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": b["pass"], "dribble": True, "hand": 1},
            {"type": "pass", "from": "O1", "to": "O2", "t0": b["pass"], "t1": b["catch"], "style": "bounce" if False else "chest"},
            {"type": "hold", "player": "O2", "from": b["catch"], "to": b["lay"]},
            {"type": "layup", "player": "O2", "t0": b["lay"], "t1": b["lay"] + 0.4, "make": True}]
    marks = {"start": 0, "screen1": T1["set"], "drive": T1["drive"], "veer": 2.4, "set": b["set"], "go": b["go"], "plant": b["plant"],
             "pass": b["pass"], "catch": b["catch"], "finish": b["lay"], "make": b["lay"] + 0.4, "end": dur}
    claims = [
        {"type": "near", "a": "X2", "b": "O2", "at": "plant", "max": 1.4, "says": "Now watch what happens when he chases."},
        {"type": "near_rim", "player": "O2", "at": "finish", "max": 1.6, "says": "He curls inside."},
        {"type": "far", "a": "X2", "b": "O2", "at": "catch", "min": 1.0, "says": "The guard hits him in stride."},
        {"type": "order", "marks": ["screen1", "drive", "veer", "set", "go", "plant", "pass", "catch", "finish", "make"], "says": "ball screen, veer, chase, curl, layup"}]
    return {"id": "veer-b-curl", "title": "Veer B: the shooter's defender chases, the shooter curls inside for a layup",
            "duration": dur, "concept": "veer-action", "source": SRC, "squareUp": True, "players": PL, "start": S,
            "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same ball screen, drive and veer as veer-a-kick.",
                      "X2 stays attached and trails over the top; O2 plants and curls tight around O5 into the lane; O1 leads him, layup."]}


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


if __name__ == "__main__":
    TA.update(set=3.4, go=3.45, pass_=4.0, catch=4.6, rel=4.9)
    TA["pass"], TA["catch"], TA["rel"] = 4.0, 4.6, 4.9
    TB.update(set=3.4, go=3.45, plant=3.9, pass_=4.2, catch=4.6, lay=5.0)
    TB["pass"] = 4.2
    tr = build(play("kick"))["tracks"]
    T1["set"] = round(first_near(tr["O5"], BALLSCR, 0.02) + 0.03, 3)
    T1["drive"] = round(T1["set"] + 0.12, 3)
    tr = build(play("kick"))["tracks"]
    setT = round(first_near(tr["O5"], VEER, 0.02) + 0.05, 3)
    for d in (TA, TB):
        d["set"], d["go"] = setT, round(setT + 0.12, 3)
    tr = build(play("kick"))["tracks"]
    TA["catch"] = round(first_near(tr["O2"], WING, 0.2, TA["go"]), 3)
    TA["pass"] = round(TA["catch"] - 0.62, 3)
    TA["rel"] = round(TA["catch"] + 0.36, 3)
    tr = build(play("curl"))["tracks"]
    TB["plant"] = round(first_near(tr["O2"], [-5.42, 4.95], 0.25, TB["go"]), 3)
    TB["catch"] = round(first_near(tr["O2"], [-2.4, 4.1], 0.2, TB["go"]), 3)
    TB["pass"] = round(TB["catch"] - 0.36, 3)
    TB["lay"] = round(first_near(tr["O2"], [-0.95, 2.55], 0.2, TB["catch"]), 3)
    for s in (play("kick"), play("curl")):
        build(s)
        print("built", s["id"], json.dumps(s["marks"]))
