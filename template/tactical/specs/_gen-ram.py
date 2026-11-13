#!/usr/bin/env python3
"""RAM SCREEN (2026-11-13): two possessions from the SAME alignment, identical until the ball screen (3.1 s).
A = drop (X5 sinks, X1 chases over -> O1 pull-up two), B = blitz (X5 + X1 trap the ball -> short roll -> layup).
Sources: NBC Sports NBA glossary 'ram screen'; Basketball Action Dictionary 'Ram'; drop/blitz coverage guides.
Writes tactical/specs/ram-a-drop.spec.json and ram-b-blitz.spec.json; build with scripts/build-play.mts."""
import json, copy, os
D = os.path.dirname(os.path.abspath(__file__))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
players = [P("O1", "O", "Point guard, ball handler"), P("O2", "O", "Shooter, right corner"), P("O3", "O", "Wing, right"),
           P("O4", "O", "Ram screener (first, off the ball)"), P("O5", "O", "Big: uses the ram, sets the ball screen"),
           P("X1", "X", "On the ball", "O1"), P("X2", "X", "Weak-side corner (low man)", "O2"), P("X3", "X", "Right wing", "O3"),
           P("X4", "X", "On the ram screener", "O4"), P("X5", "X", "The big's defender (the read)", "O5")]
start = {"O1": [1.7, 9.6], "X1": [1.4, 8.7], "O5": [-2.5, 2.9], "X5": [-1.9, 3.5], "O4": [-3.6, 6.6], "X4": [-2.6, 6.1],
         "O2": [6.6, 1.4], "X2": [5.4, 2.2], "O3": [5.3, 6.9], "X3": [4.4, 6.3]}
# ---- shared first 3.1 s (the ram screen) ----
common_legs = {
    "O1": [{"at": 0.3, "to": [1.9, 9.8], "speed": 1.4}],
    "O4": [{"at": 0.1, "to": [-2.15, 4.35], "speed": 4.5}, {"at": 2.15, "via": [[-3.6, 3.3]], "to": [-5.9, 2.2], "speed": 5.0}],
    "O5": [{"at": 0.8, "via": [[-3.2, 5.0], [-2.3, 7.4]], "to": [0.85, 8.95], "dur": 2.3}],
    "X5": [{"at": 1.15, "to": [-1.75, 3.95], "speed": 2.2}, {"at": 1.85, "via": [[-0.85, 5.1]], "to": [0.0, 7.4], "dur": 1.25}],
    "X4": [{"at": 0.4, "to": [-1.35, 6.5], "speed": 2.0}, {"at": 2.3, "via": [[-2.9, 4.4]], "to": [-5.0, 2.9], "speed": 4.8}],
    "X1": [], "O2": [], "O3": [], "X2": [], "X3": [{"at": 1.4, "to": [4.1, 6.1], "speed": 1.2}],
}
marks_common = {"start": 0, "ram": 1.2, "contact": 1.55, "lead": 2.45, "ballscreen": 3.1}
stance = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
claims_common = [
    {"type": "near", "a": "O4", "b": "X5", "at": "contact", "max": 0.9, "says": "Four screens the big's defender."},
    {"type": "far", "a": "O5", "b": "X5", "at": "lead", "min": 2.0, "says": "Now Five has a head start."},
    {"type": "near", "a": "O5", "b": "X1", "at": "ballscreen", "max": 1.0, "says": "Five gets there first."},
]

def spec(kind):
    s = {"id": f"ram-{kind}", "players": players, "start": start}
    legs = copy.deepcopy(common_legs)
    acts = {"O4": [{"type": "screen", "from": 1.2, "to": 2.1, "face": "X5"}],
            "X4": [stance("O4", 0, 6.5)], "X2": [stance("O1", 0, 6.5)], "X3": [stance("O1", 0, 6.5)],
            "X1": [stance("O1", 0, 3.15)], "X5": [stance("O5", 0, 1.2), {"type": "stance", "from": 1.45, "to": 1.85, "face": "O4"}]}
    if kind == "a-drop":
        s.update(title="RAM screen — Read A: drop. X5 sinks, X1 chases over, O1 pulls up", duration=6.6)
        s["notes"] = ["O4 screens X5 (ram); O5 comes off it with a head start and screens X1.",
                      "X1 goes over the screen and trails; X5 drops to the paint: the space is in front of O1.",
                      "O1 stops on two feet and rises for a mid-range pull-up."]
        legs["O1"] += [{"at": 2.75, "via": [[0.9, 9.95], [-0.2, 9.2]], "to": [-1.15, 7.55], "dur": 1.6}]
        legs["X1"] = [{"at": 3.3, "via": [[1.55, 10.15]], "to": [-0.45, 9.5], "dur": 1.4},
                      {"at": 4.75, "to": [-0.8, 8.55], "dur": 0.7}]
        legs["X5"] += [{"at": 3.1, "to": [-0.55, 5.25], "speed": 2.6}]
        legs["O5"] += [{"at": 4.05, "to": [0.75, 5.3], "speed": 4.2}]
        s["ball"] = [{"type": "hold", "player": "O1", "from": 0, "to": 4.1, "dribble": True},
                     {"type": "hold", "player": "O1", "from": 4.1, "to": 4.6},
                     {"type": "shot", "player": "O1", "t0": 4.6, "t1": 5.55, "make": True, "three": False}]
        acts["O5"] = [{"type": "screen", "from": 3.1, "to": 3.95, "face": "X1"}]
        acts["X5"] += [stance("O1", 3.15, 5.2)]
        acts["X1"] += [{"type": "contest", "from": 4.75, "to": 5.25}]
        acts["O1"] = [{"type": "celebrate", "from": 5.75, "to": 6.4}]
        s["marks"] = {**marks_common, "use": 3.2, "drop": 3.6, "gather": 4.1, "release": 4.6, "make": 5.55, "end": 6.6}
        s["claims"] = claims_common + [
            {"type": "far", "a": "X5", "b": "O1", "at": "release", "min": 2.2, "says": "The big drops."},
            {"type": "open", "player": "O1", "at": "release", "min": 1.8, "says": "The guard has room to pull up."},
            {"type": "order", "marks": ["ram", "contact", "lead", "ballscreen", "use", "release", "make"], "says": "ram screen, ball screen, pull-up"}]
    else:
        s.update(title="RAM screen — Read B: blitz. X5 and X1 trap the ball, O5 short rolls and finishes", duration=6.5)
        s["notes"] = ["Same alignment and the same ram screen until the ball screen.",
                      "X5 jumps up to the level of the ball with X1: two on the ball.",
                      "O5 slips into the short roll, catches, one dribble and finishes; the weak-side help stays home."]
        legs["O1"] += [{"at": 2.75, "via": [[0.9, 10.0]], "to": [0.25, 10.25], "dur": 1.0}]
        legs["X5"] = [legs["X5"][0], {"at": 1.85, "via": [[-0.85, 5.1], [0.0, 7.4]], "to": [-0.5, 10.35], "dur": 1.95}, {"at": 4.45, "to": [-0.15, 7.6], "speed": 5.0}]
        legs["X1"] = [{"at": 2.95, "via": [[1.6, 9.6]], "to": [0.85, 10.7], "dur": 1.1}]
        legs["O5"] += [{"at": 3.45, "to": [0.15, 6.5], "dur": 0.95}, {"at": 4.45, "to": [0.1, 2.85], "dur": 1.05}]
        legs["X2"] = [{"at": 4.25, "to": [4.05, 2.7], "dur": 0.65}, {"at": "+0.1", "to": [5.6, 2.0], "dur": 0.75}]
        s["ball"] = [{"type": "hold", "player": "O1", "from": 0, "to": 3.75, "dribble": True},
                     {"type": "hold", "player": "O1", "from": 3.75, "to": 4.0},
                     {"type": "pass", "from": "O1", "to": "O5", "t0": 4.0, "t1": 4.38, "style": "overhead"},
                     {"type": "hold", "player": "O5", "from": 4.38, "to": 4.62},
                     {"type": "hold", "player": "O5", "from": 4.62, "to": 5.0, "dribble": True},
                     {"type": "hold", "player": "O5", "from": 5.0, "to": 5.35},
                     {"type": "layup", "player": "O5", "t0": 5.35, "t1": 5.72, "make": True}]
        acts["O5"] = [{"type": "screen", "from": 3.1, "to": 3.5, "face": "X1"}, {"type": "celebrate", "from": 5.95, "to": 6.45}]
        acts["X5"] += [{"type": "blitz", "from": 3.3, "to": 4.15, "face": "O1"}]
        acts["X1"] += [{"type": "blitz", "from": 3.55, "to": 4.2, "face": "O1"}]
        acts["X2"] = [stance("O1", 0, 4.3), stance("O5", 4.3, 6.5)]
        s["marks"] = {**marks_common, "use": 3.2, "blitz": 3.3, "trap": 3.98, "pass": 4.0, "catch": 4.38, "drive": 4.62, "release": 5.35, "make": 5.72, "end": 6.5}
        s["claims"] = claims_common + [
            {"type": "near", "a": "X5", "b": "O1", "at": "trap", "max": 1.2, "says": "two defenders jump the ball."},
            {"type": "near", "a": "X1", "b": "O1", "at": "trap", "max": 1.2, "says": "two defenders jump the ball."},
            {"type": "far", "a": "X5", "b": "O5", "at": "catch", "min": 2.5, "says": "Hit the short roll."},
            {"type": "open", "player": "O5", "at": "release", "min": 1.2, "says": "The lane is open."},
            {"type": "near_rim", "player": "O5", "at": "release", "max": 1.5, "says": "The lane is open."},
            {"type": "order", "marks": ["ram", "contact", "lead", "ballscreen", "blitz", "trap", "pass", "catch", "release", "make"], "says": "ram screen, blitz, short roll, layup"}]
    s["legs"] = legs
    s["actions"] = acts
    s["screens"] = []
    return s

for k in ("a-drop", "b-blitz"):
    json.dump(spec(k), open(os.path.join(D, f"ram-{k}.spec.json"), "w"), indent=1)
print("ok")
