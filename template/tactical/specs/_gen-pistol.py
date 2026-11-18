#!/usr/bin/env python3
"""PISTOL (21) (owner choice 2026-11-16 14:42Z: another Spain-method video). Original E2A possession (generic early-offense
pistol / 21 action: wing dribble hand-off straight into a ball screen, generic coaching knowledge, no copied diagram).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Basket at the top (yaw 0): x > 0 is screen-left.
  O1 dribbles to the wing; O2 lifts from the corner and takes the hand-off; O1 clears to the corner.
  O5 sprints up and screens X2 right away; O2 comes off it toward the middle. X2 decides:
  A pistol-a-under  X2 goes UNDER the screen -> O2 stops behind it: pull-up three.
  B pistol-b-over   X2 chases OVER the top -> O2 turns the corner, X5 steps up, pocket pass to the rolling big: layup."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (generic pistol / 21 early-offense action: hand-off into a ball screen, generic coaching knowledge)"
PL = [P("O1", "O", "Point guard: hand-off passer"), P("O2", "O", "Wing: takes the hand-off and the ball screen"),
      P("O3", "O", "Weak-side corner"), P("O4", "O", "Weak-side wing"), P("O5", "O", "Big: sprints into the ball screen, rolls"),
      P("X1", "X", "On the point guard", "O1"), P("X2", "X", "On the wing: under or over", "O2"), P("X3", "X", "Weak-side corner", "O3"),
      P("X4", "X", "Weak-side wing", "O4"), P("X5", "X", "On the big", "O5")]
S = {"O1": [1.2, 9.6], "X1": [1.1, 8.75], "O2": [6.6, 2.0], "X2": [5.75, 2.6], "O5": [0.6, 6.2], "X5": [0.3, 5.4],
     "O3": [-6.6, 1.3], "X3": [-5.6, 2.1], "O4": [-4.9, 7.2], "X4": [-4.1, 6.5]}
HO_O1 = [5.1, 7.6]
HO_O2 = [5.55, 8.35]
SCR = [3.85, 8.1]
PU = [2.5, 8.95]
HO = {"t": 2.45}


def play(kind):
    ho = HO["t"]
    legs = {"O1": [{"at": 0.2, "to": HO_O1, "speed": 3.4},
                   {"at": ho + 0.2, "via": [[5.9, 5.5]], "to": [6.5, 2.8], "speed": 4.5}],
            "X1": [{"at": 0.3, "to": [4.2, 7.2], "speed": 3.0},
                   {"at": ho + 0.5, "to": [5.2, 3.6], "speed": 3.6}],
            "O2": [{"at": 0.3, "via": [[6.6, 5.0]], "to": HO_O2, "speed": 5.0}],
            "X2": [{"at": 0.55, "via": [[5.7, 5.0]], "to": [6.25, 7.75], "speed": 4.5}],
            "O5": [{"at": ho - 1.0, "to": SCR, "speed": 5.0}],
            "X5": [{"at": ho - 0.8, "to": [2.4, 6.8], "speed": 4.2}]}
    acts = {"X3": [st("O2", 0, 6.0)], "X4": [st("O2", 0, 6.0)], "X1": [st("O1", 0, ho)],
            "O5": [{"type": "screen", "from": ho + 0.35, "to": ho + 0.95, "face": "X2"}], "X5": [st("O2", ho, ho + 1.5)]}
    if kind == "under":
        legs["O2"].append({"at": ho + 0.15, "via": [[4.6, 9.0], [3.6, 9.05]], "to": PU, "speed": 4.2})
        legs["X2"].append({"at": ho + 0.45, "via": [[5.0, 7.25], [3.8, 7.0]], "to": [3.5, 6.7], "speed": 4.2})
        legs["O5"].append({"at": ho + 1.2, "to": [4.9, 9.3], "speed": 3.0})       # pops back out
        acts["X2"] = [st("O2", 0, 6.0)]
        acts["O2"] = [{"type": "celebrate", "from": ho + 3.0, "to": ho + 3.8}]
        pu = HO.get("pu", ho + 1.0)
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": ho - 0.3, "dribble": True},
                {"type": "hold", "player": "O1", "from": ho - 0.3, "to": ho},
                {"type": "pass", "from": "O1", "to": "O2", "t0": ho, "t1": ho + 0.22, "style": "handoff"},
                {"type": "hold", "player": "O2", "from": ho + 0.22, "to": pu, "dribble": True},
                {"type": "shot", "player": "O2", "t0": pu, "t1": pu + 1.1, "make": True}]
        marks = {"start": 0, "handoff": ho, "screen": ho + 0.3, "under": ho + 0.95, "pullup": pu, "make": pu + 1.1, "end": ho + 4.6}
        claims = [
            {"type": "near", "a": "O2", "b": "O1", "at": "handoff", "max": 1.05, "says": "A hand-off on the wing..."},
            {"type": "near", "a": "O5", "b": "X2", "at": "under", "max": 1.6, "says": "...then a ball screen right away."},
            {"type": "open", "player": "O2", "at": "pullup", "min": 1.8, "says": "He goes under: pull-up three."},
            {"type": "behind_arc", "player": "O2", "at": "pullup", "says": "Pull-up three."},
            {"type": "order", "marks": ["handoff", "screen", "under", "pullup", "make"], "says": "hand-off, screen, under, pull-up"}]
        return {"id": "pistol-a-under", "title": "Pistol A: he goes under the screen, pull-up three", "duration": ho + 4.6,
                "concept": "pistol", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
                "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O1 dribbles to the wing, O2 lifts and takes the hand-off; O5 screens X2 right away.",
                          "X2 goes under the screen; O2 stops behind it: pull-up three."]}
    legs["O2"].append({"at": ho + 0.15, "via": [[4.6, 9.0], [3.5, 9.0], [2.4, 7.8]], "to": [1.4, 6.4], "speed": 4.4})
    legs["X2"].append({"at": ho + 0.1, "via": [[5.2, 9.35], [4.0, 9.6]], "to": [3.0, 9.25], "speed": 4.4})
    legs["X5"].append({"at": ho + 0.9, "to": [2.05, 5.7], "speed": 3.6})                 # steps up to stop the ball
    legs["O5"].append({"at": ho + 1.0, "via": [[3.4, 4.9]], "to": [0.95, 4.2], "speed": 5.0})
    legs["O5"].append({"at": "+0.2", "to": [0.3, 2.7], "speed": 3.6})            # one dribble to the rim
    acts["X2"] = [st("O2", 0, 6.0)]
    acts["O5"].append({"type": "celebrate", "from": HO.get("pa", ho + 1.75) + 2.0, "to": ho + 4.6})
    pa = HO.get("pa", ho + 1.75)
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": ho - 0.3, "dribble": True},
            {"type": "hold", "player": "O1", "from": ho - 0.3, "to": ho},
            {"type": "pass", "from": "O1", "to": "O2", "t0": ho, "t1": ho + 0.22, "style": "handoff"},
            {"type": "hold", "player": "O2", "from": ho + 0.22, "to": pa, "dribble": True},
            {"type": "pass", "from": "O2", "to": "O5", "t0": pa, "t1": pa + 0.3, "style": "bounce"},
            {"type": "hold", "player": "O5", "from": pa + 0.3, "to": pa + 1.35, "dribble": True},
            {"type": "layup", "player": "O5", "t0": pa + 1.35, "t1": pa + 1.75, "make": True}]
    marks = {"start": 0, "handoff": ho, "screen": ho + 0.3, "over": ho + 0.6, "stepup": ho + 1.4, "pass": pa, "catch": pa + 0.3,
             "finish": pa + 1.35, "make": pa + 1.75, "end": ho + 4.6}
    claims = [
        {"type": "near", "a": "O2", "b": "O1", "at": "handoff", "max": 1.05, "says": "A hand-off on the wing..."},
        {"type": "near", "a": "X2", "b": "O2", "at": "over", "max": 1.6, "says": "He chases over the top."},
        {"type": "near", "a": "X5", "b": "O2", "at": "pass", "max": 1.6, "says": "The big has to step up."},
        {"type": "far", "a": "X5", "b": "O5", "at": "catch", "min": 1.5, "says": "Nobody with the roller."},
        {"type": "near_rim", "player": "O5", "at": "finish", "max": 1.5, "says": "Easy two at the rim."},
        {"type": "order", "marks": ["handoff", "screen", "over", "stepup", "pass", "catch", "finish", "make"], "says": "hand-off, screen, over, pocket pass, layup"}]
    return {"id": "pistol-b-over", "title": "Pistol B: he chases over, the big steps up, pocket pass", "duration": ho + 4.6,
            "concept": "pistol", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
            "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start as pistol-a-under.", "X2 chases over the top; O2 turns the corner; X5 steps up; pocket pass to O5, layup."]}


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
    tr = build(play("under"))["tracks"]["O2"]
    HO["t"] = round(arrive(tr, HO_O2) + 0.05, 2)
    tr = build(play("under"))["tracks"]["O2"]
    HO["pu"] = round(arrive(tr, PU, HO["t"]) + 0.1, 2)
    tb = build(play("over"))["tracks"]
    t_o2 = arrive(tb["O2"], [1.4, 6.4], HO["t"])
    t_o5 = arrive(tb["O5"], [0.95, 4.2], HO["t"])
    HO["pa"] = round(max(t_o2 + 0.05, t_o5 - 0.25), 2)
    print("HO", HO)
    for s in (play("under"), play("over")):
        p = build(s)
        print("built", s["id"], p["duration"])
