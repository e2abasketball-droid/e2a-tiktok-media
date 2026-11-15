#!/usr/bin/env python3
"""Chicago action pilot (owner brief 2026-11-14 18:56Z): pin-down straight into a dribble hand-off.
Original E2A possession (standard FIBA/European half-court concept, generic coaching knowledge, no copied diagram).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Left side = the action side.

Same floor and same first 1.5 s in both cases:
  O1 handler dribbles from the top to the left slot (the hand-off spot).
  O4 walks down and sets the PIN-DOWN for O2, who comes up from the left block to O1.
  X2 guards the shooter O2. O3 right wing, O5 right block keep X3 and X5 on the weak side.
  A  chicago-a-take      X2 TRAILS: O2 takes the ball tight off O1's hip and turns the corner into the paint;
                          X4 (the big) stays deep in the lane, so the pull-up in the paint is open.
  B  chicago-b-backdoor  X2 JUMPS EARLY into the exchange line before the ball changes hands: O1 keeps the ball,
                          O2 plants and cuts backdoor. O4 has popped to the corner and X4 went with him, so the lane
                          is empty; the weak-side help (X5) leaves late, after the bounce pass.
Writes tactical/specs/chicago-*.spec.json; build each with scripts/build-play.mts."""
import json, os

D = os.path.dirname(os.path.abspath(__file__))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
stance = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (standard FIBA/European Chicago action: pin-down into dribble hand-off, generic coaching knowledge)"

PLAYERS = [P("O1", "O", "Handler: the hand-off passer"), P("O2", "O", "Shooter: comes off the pin-down"),
           P("O3", "O", "Right wing"), P("O4", "O", "Big: pin-down screener"), P("O5", "O", "Big, right block"),
           P("X1", "X", "On the handler", "O1"), P("X2", "X", "On the shooter: trails (A) / jumps the hand-off (B)", "O2"),
           P("X3", "X", "Right wing", "O3"), P("X4", "X", "On the screener (the big)", "O4"),
           P("X5", "X", "Weak-side big: the late help", "O5")]
START = {"O1": [-1.2, 8.7], "X1": [-0.9, 7.9], "O2": [-3.7, 1.7], "X2": [-3.2, 2.35], "O4": [-2.3, 5.5],
         "X4": [-1.75, 4.9], "O3": [5.6, 6.4], "X3": [4.8, 5.8], "O5": [3.1, 2.0], "X5": [2.2, 2.5]}
# shared opening (identical in A and B up to 1.5 s)
O1_IN = {"at": 0.35, "to": [-3.45, 7.65], "speed": 2.6}            # dribble to the left slot: the hand-off spot
O4_DOWN = {"at": 0.0, "to": [-3.95, 3.15], "dur": 1.0}               # walk down, set the pin-down facing X2
X4_DOWN = {"at": 0.15, "to": [-2.6, 2.95], "speed": 2.4}
X1_IN = {"at": 0.45, "to": [-2.45, 7.3], "speed": 2.4}              # middle side of the handler


def chicago(kind):
    legs = {"O3": [], "X3": [], "O5": [], "X5": [], "O1": [dict(O1_IN)], "O4": [dict(O4_DOWN)], "X4": [dict(X4_DOWN)],
            "X1": [dict(X1_IN)]}
    acts = {"O4": [{"type": "screen", "from": 1.05, "to": 1.75, "face": "X2"}],
            "X3": [stance("O1", 0, 7.0)], "X1": [stance("O1", 0, 7.0)]}
    if kind == "take":
        # O2 off the pin-down, decelerates INTO the hand-off at O1's hip, then turns the corner downhill
        legs["O2"] = [{"at": 0.75, "via": [[-4.75, 2.55], [-4.85, 4.4], [-4.45, 6.25]], "to": [-4.05, 7.05], "speed": 5.2},
                      {"at": "+0.12", "via": [[-3.25, 6.5], [-2.45, 5.55]], "to": [-1.75, 4.6], "speed": 5.4}]
        # X2 TRAILS: chases the same path behind him, then is caught behind the hand-off (over the top of O1)
        legs["X2"] = [{"at": 1.0, "via": [[-4.55, 2.35], [-5.05, 3.7], [-5.0, 5.4]], "to": [-4.7, 6.55], "speed": 5.0},
                      {"at": "+0.1", "via": [[-4.4, 8.0], [-3.45, 8.6]], "to": [-2.45, 8.05], "speed": 4.0},
                      {"at": "+0.0", "to": [-1.85, 5.75], "speed": 4.4}]
        legs["O4"] += [{"at": 2.0, "to": [-4.4, 2.0], "speed": 2.0}]   # screener slips to the short corner
        legs["X4"] += [{"at": 2.25, "to": [-1.75, 2.75], "speed": 2.6}]  # the big STAYS DEEP: sinks into the lane
        legs["X1"] += [{"at": 3.0, "to": [-2.95, 6.95], "speed": 2.0}]
        ho = HO.get("a", 2.55)  # O2's stop at O1's hip (measured from the first build, see __main__)
        pu = HO.get("pu", 4.15)
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": ho - 0.35, "dribble": True},
                {"type": "hold", "player": "O1", "from": ho - 0.35, "to": ho},
                {"type": "pass", "from": "O1", "to": "O2", "t0": ho, "t1": ho + 0.22, "style": "handoff"},
                {"type": "hold", "player": "O2", "from": ho + 0.22, "to": pu, "dribble": True},
                {"type": "shot", "player": "O2", "t0": pu, "t1": pu + 0.9, "make": True, "three": False}]
        marks = {"start": 0, "pindown": 1.05, "trail": 1.6, "pickup": ho - 0.35, "handoff": ho, "firstStep": ho + 0.4,
                 "turn": ho + 0.75, "pullup": pu, "make": pu + 0.9, "end": 6.4}
        acts["O1"] = [{"type": "screen", "from": ho + 0.15, "to": ho + 1.0, "face": "X2"}]
        acts["X4"] = [stance("O2", 2.4, 6.4)]
        acts["O2"] = [{"type": "celebrate", "from": 5.3, "to": 6.2}]
        claims = [
            {"type": "near", "a": "O4", "b": "X2", "at": "pindown", "max": 1.3, "says": "A pin-down for the shooter."},
            {"type": "far", "a": "X2", "b": "O1", "at": "trail", "min": 4.0, "says": "If he trails..."},
            {"type": "near", "a": "O2", "b": "O1", "at": "handoff", "max": 0.95, "says": "take it tight, off the passer's hip."},
            {"type": "far", "a": "X2", "b": "O2", "at": "turn", "min": 1.6, "says": "The trailer is caught behind the hand-off."},
            {"type": "far", "a": "X4", "b": "O2", "at": "pullup", "min": 1.8, "says": "The big stays deep: room to turn the corner."},
            {"type": "order", "marks": ["pindown", "handoff", "turn", "pullup"], "says": "pin-down, hand-off, turn the corner"}]
        return {"id": "chicago-a-take", "title": "Chicago action A: he trails, take it tight", "duration": 6.4,
                "concept": "chicago-dho", "source": SRC, "squareUp": True,
                "notes": ["O4 pins down for O2; O2 comes up to O1 for the dribble hand-off.",
                          "X2 trails over the top. O2 takes the ball off O1's hip and turns the corner; O1's body screens X2.",
                          "X4 stays deep in the lane: the pull-up in the paint is open."],
                "players": PLAYERS, "start": START, "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims}
    # B: X2 jumps the exchange; O2 plants and goes backdoor; bounce pass beats the late help
    legs["O2"] = [{"at": 0.75, "via": [[-4.75, 2.55], [-4.85, 4.4]], "to": [-4.75, 5.55], "speed": 5.2},
                  {"at": "+0.08", "via": [[-3.85, 4.2], [-2.55, 2.85]], "to": [-1.25, 2.2], "speed": 6.4}]
    legs["X2"] = [{"at": 0.85, "via": [[-3.4, 3.8], [-3.8, 5.3]], "to": [-4.05, 6.55], "speed": 5.4},
                  {"at": "+0.1", "via": [[-4.05, 5.6]], "to": [-3.2, 4.1], "speed": 5.0}]
    legs["O4"] += [{"at": 1.85, "to": [-6.55, 1.35], "speed": 4.2}]   # screener pops to the corner...
    legs["X4"] += [{"at": 1.95, "to": [-5.75, 1.95], "speed": 4.0}]   # ...and his big goes with him: empty lane
    legs["X5"] = [{"at": 3.1, "to": [-0.55, 2.55], "speed": 5.0}]     # weak-side help: leaves on the pass, late
    legs["X1"] += [{"at": 3.2, "to": [-2.6, 6.2], "speed": 2.0}]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": 2.45, "dribble": True},
            {"type": "hold", "player": "O1", "from": 2.45, "to": 3.05},
            {"type": "pass", "from": "O1", "to": "O2", "t0": 3.05, "t1": 3.62, "style": "bounce"},
            {"type": "hold", "player": "O2", "from": 3.62, "to": 3.84},
            {"type": "layup", "player": "O2", "t0": 3.84, "t1": 4.24, "make": True, "contested": True}]
    marks = {"start": 0, "pindown": 1.05, "jump": 1.75, "plant": 2.05, "keep": 2.45, "cut": 2.4, "pass": 3.05,
             "catch": 3.62, "help": 3.62, "finish": 3.84, "make": 4.24, "end": 6.0}
    acts["X2"] = [stance("O1", 1.9, 2.4)]
    acts["X4"] = [stance("O4", 2.0, 6.0)]
    acts["O2"] = [{"type": "celebrate", "from": 4.3, "to": 5.4}]
    claims = [
        {"type": "near", "a": "O4", "b": "X2", "at": "pindown", "max": 1.3, "says": "A pin-down for the shooter."},
        {"type": "near", "a": "X2", "b": "O1", "at": "keep", "max": 1.6, "says": "He jumps the exchange before the ball changes hands."},
        {"type": "far", "a": "O2", "b": "O1", "at": "keep", "min": 1.6, "says": "Keep the ball: no hand-off."},
        {"type": "far", "a": "X4", "b": "O2", "at": "catch", "min": 2.5, "says": "The big went with the screener: the lane is empty."},
        {"type": "far", "a": "X5", "b": "O2", "at": "catch", "min": 1.0, "says": "The pass beats the help."},
        {"type": "near_rim", "player": "O2", "at": "finish", "max": 1.5, "says": "Backdoor to the rim."},
        {"type": "order", "marks": ["pindown", "jump", "plant", "pass", "catch", "finish"], "says": "jump, plant, backdoor, pass"}]
    return {"id": "chicago-b-backdoor", "title": "Chicago action B: he jumps the hand-off, backdoor", "duration": 6.0,
            "concept": "chicago-dho", "source": SRC, "squareUp": True,
            "notes": ["Same start as chicago-a-take.",
                      "X2 jumps into the exchange line before the ball changes hands; O1 keeps the ball.",
                      "O2 plants and cuts backdoor. O4 popped to the corner with X4, so the lane is empty;",
                      "X5 leaves the weak side only on the pass: the bounce pass beats the help."],
            "players": PLAYERS, "start": START, "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims}


HO = {}


def write_build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    with open(sp, "w") as f:
        json.dump(s, f, indent=1)
    out = os.path.join(os.path.dirname(D), "plays", f"{s['id']}.json")
    subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=os.path.dirname(os.path.dirname(D)),
                   check=True, capture_output=True)
    return json.load(open(out))


if __name__ == "__main__":
    import subprocess
    # pass 1: find O2's stop at O1's hip and his stop for the pull-up, then centre the ball events on them
    tr = write_build(chicago("take"))["tracks"]["O2"]
    stops = [tr[i][0] for i in range(1, len(tr)) if tr[i][1:] == tr[i - 1][1:] and tr[i - 1][0] > 0.8]
    HO["a"] = round(stops[0] - 0.08, 3)   # O2 arrives at rest; the exchange straddles his stop
    HO["pu"] = round(tr[-2][0] + 0.12, 3) # pull-up right after the last stop
    for s in (chicago("take"), chicago("backdoor")):
        write_build(s)
        print("wrote", s["id"], HO if s["id"].endswith("take") else "")
