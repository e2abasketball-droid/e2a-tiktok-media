#!/usr/bin/env python3
"""SPANOULIS ACTION (owner brief 2026-11-17 00:47Z: 3-version experiment). Original E2A possession, a version of the
action associated with Vassilis Spanoulis (not a copy of a real possession): a guard sets a BACKSCREEN for a teammate
cutting to the rim, then comes straight back for a DRIBBLE HAND-OFF. Two threats in a row; his defender decides.
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Basket at the top (yaw 0): x > 0 is screen-left.
  O1 ball handler dribbles from the top to the left slot.   O2 the guard: backscreen on X4, then pops and takes the DHO.
  O3 weak-side wing (spacing).   O4 uses the backscreen: cuts to the rim, then fills the left corner.   O5 right dunker spot.
  A spanoulis-a-trail  X2 helped on the cutter (protects the rim) -> he is late, TRAILS the hand-off -> O2 attacks the gap: layup.
  B spanoulis-b-under  X2 stays attached, then goes UNDER the hand-off to protect the drive -> O2 stops: pull-up three.
  In B the cut is picked up by the low man (X5 steps in at the rim)."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (a version of the Spanoulis action: backscreen then dribble hand-off; generic coaching knowledge, no copied diagram or possession)"
PL = [P("O1", "O", "Ball handler: dribble hand-off"), P("O2", "O", "Guard: backscreen, then the hand-off"),
      P("O3", "O", "Weak-side wing spacing"), P("O4", "O", "Uses the backscreen: cut to the rim"), P("O5", "O", "Big: dunker spot"),
      P("X1", "X", "On the ball handler", "O1"), P("X2", "X", "On the guard: trail or go under", "O2"),
      P("X3", "X", "Weak-side wing", "O3"), P("X4", "X", "Screened by the backscreen", "O4"), P("X5", "X", "On the big: low man", "O5")]
S = {"O1": [-0.9, 9.3], "X1": [-0.65, 8.45], "O2": [3.7, 2.9], "X2": [3.0, 3.1], "O4": [3.35, 7.45], "X4": [2.85, 6.85],
     "O3": [-5.9, 5.8], "X3": [-4.3, 5.2], "O5": [-3.7, 1.5], "X5": [-2.7, 2.2]}
SCR = [2.75, 6.1]          # backscreen spot: on X4's basket side, facing him
HO_O1 = [2.2, 9.05]        # O1 stops here for the hand-off (left slot)
HO_O2 = [2.95, 8.55]       # O2 takes it here, moving toward the middle
POP = [4.4, 7.5]           # O2 pops out after the screen, then comes back to the ball
PU = [1.85, 8.3]          # pull-up spot (B), behind the arc
LAY = [0.3, 2.75]          # layup spot (A)
TM = {"scr": 1.35, "ho": 4.01}


def common():
    s = TM["scr"]
    legs = {"O1": [{"at": 0.3, "to": HO_O1, "speed": 2.6}],
            "X1": [{"at": 0.4, "to": [1.5, 8.55], "speed": 2.4}],
            "O2": [{"at": 0.1, "via": [[3.3, 4.6]], "to": SCR, "speed": 4.6}],
            "O4": [{"at": s + 0.25, "via": [[2.2, 7.2], [1.5, 5.6]], "to": [0.75, 2.55], "speed": 5.8},
                   {"at": "+0.05", "via": [[2.6, 1.3]], "to": [6.3, 1.05], "speed": 4.6}],
            "X4": [{"at": s + 0.8, "via": [[2.05, 6.6], [1.35, 4.6]], "to": [1.5, 3.05], "speed": 5.2},
                   {"at": "+0.05", "via": [[3.2, 2.0]], "to": [5.5, 1.75], "speed": 4.4}]}
    acts = {"O2": [{"type": "screen", "from": s, "to": s + 0.75, "face": "X4"}],
            "X1": [st("O1", 0, 6.5)], "X3": [st("O1", 0, 7.0)], "X4": [st("O4", 0, s + 0.5)]}
    # after the hand-off O1 relocates to the top (spacing), X1 goes with him: the middle opens
    legs["O1"].append({"at": TM["ho"] + 0.15, "to": [-0.2, 10.45], "speed": 3.4})
    legs["X1"].append({"at": TM["ho"] + 0.2, "to": [0.0, 9.65], "speed": 3.0})
    return legs, acts


def play(kind):
    s, ho = TM["scr"], TM["ho"]
    legs, acts = common()
    if kind == "trail":
        # X2 helps on the cutter (bumps him in the lane), then is late back to O2
        legs["X2"] = [{"at": 0.25, "via": [[3.05, 4.3]], "to": [2.65, 5.0], "speed": 4.2},
                      {"at": s + 0.45, "to": [1.95, 4.15], "speed": 4.2},
                      {"at": "+0.15", "via": [[3.3, 5.3]], "to": [4.25, 6.75], "speed": 5.4},
                      {"at": TM["ho"] + 0.2, "via": [[3.5, 7.85], [2.3, 7.2], [1.5, 5.6]], "to": [1.05, 4.15], "speed": 4.7}]
        legs["O2"] += [{"at": s + 0.8, "to": POP, "speed": 4.0},
                       {"at": "+0.0", "to": HO_O2, "speed": 3.6},
                       {"at": "+0.12", "via": [[2.15, 7.9], [1.1, 6.2]], "to": LAY, "speed": 5.6}]
        legs["X5"] = [{"at": ho + 0.6, "to": [-1.25, 2.55], "speed": 3.6}]
        acts["X2"] = [st("O4", s + 0.3, s + 1.0)]
        acts["X5"] = [st("O2", ho, ho + 3.0)]
        lay = TM.get("lay", ho + 1.6)
        acts["O2"].append({"type": "celebrate", "from": lay + 1.0, "to": lay + 1.9})
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": ho - 0.3, "dribble": True},
                {"type": "hold", "player": "O1", "from": ho - 0.3, "to": ho},
                {"type": "pass", "from": "O1", "to": "O2", "t0": ho, "t1": ho + 0.22, "style": "handoff"},
                {"type": "hold", "player": "O2", "from": ho + 0.22, "to": lay, "dribble": True},
                {"type": "layup", "player": "O2", "t0": lay, "t1": lay + 0.4, "make": True}]
        marks = {"start": 0, "screen": s + 0.2, "cut": s + 1.5, "help": s + 1.05, "handoff": ho, "trail": ho + 0.25,
                 "gap": ho + 0.8, "layup": lay, "make": lay + 0.4, "end": lay + 2.0}
        claims = [
            {"type": "near", "a": "O2", "b": "X4", "at": "screen", "max": 1.0, "says": "The guard sets a backscreen..."},
            {"type": "near_rim", "player": "O4", "at": "cut", "max": 2.6, "says": "...sending his teammate straight to the rim."},
            {"type": "near", "a": "X2", "b": "O4", "at": "help", "max": 1.8, "says": "His defender helps on the cut (the first threat)."},
            {"type": "near", "a": "O2", "b": "O1", "at": "handoff", "max": 1.0, "says": "The same guard comes back for the handoff."},
            {"type": "far", "a": "X2", "b": "O2", "at": "handoff", "min": 1.5, "says": "If he trails..."},
            {"type": "near_rim", "player": "O2", "at": "layup", "max": 1.5, "says": "...attack the gap."},
            {"type": "order", "marks": ["screen", "help", "cut", "handoff", "trail", "layup", "make"], "says": "backscreen, cut, hand-off, trail, layup"}]
        return {"id": "spanoulis-a-trail", "title": "Spanoulis A: he trails the hand-off, attack the gap", "duration": lay + 2.0,
                "concept": "spanoulis", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
                "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O2 backscreens X4; O4 cuts to the rim; X2 helps on the cut.", "O2 pops and comes back for the DHO; X2 is late and trails; O2 attacks the gap: layup."]}
    # B: X2 stays attached to O2 (low man X5 takes the cutter), then goes UNDER the hand-off
    legs["X2"] = [{"at": 0.25, "via": [[3.05, 4.3]], "to": [2.65, 5.0], "speed": 4.2},
                  {"at": s + 0.6, "to": [3.75, 6.5], "speed": 4.0},
                  {"at": "+0.0", "via": [[3.0, 7.55]], "to": [2.35, 6.3], "speed": 4.4}]
    legs["X5"] = [{"at": s + 0.5, "to": [-0.55, 2.6], "speed": 4.4}]
    legs["O2"] += [{"at": s + 0.8, "to": POP, "speed": 4.0},
                   {"at": "+0.0", "to": HO_O2, "speed": 3.6},
                   {"at": "+0.12", "to": PU, "speed": 3.6}]
    acts["X2"] = [st("O2", 0, 8.0)]
    acts["X5"] = [st("O4", s + 0.5, s + 2.5)]
    pu = TM.get("pu", ho + 0.9)
    acts["O2"].append({"type": "celebrate", "from": pu + 1.6, "to": pu + 2.4})
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": ho - 0.3, "dribble": True},
            {"type": "hold", "player": "O1", "from": ho - 0.3, "to": ho},
            {"type": "pass", "from": "O1", "to": "O2", "t0": ho, "t1": ho + 0.22, "style": "handoff"},
            {"type": "hold", "player": "O2", "from": ho + 0.22, "to": pu, "dribble": True},
            {"type": "shot", "player": "O2", "t0": pu, "t1": pu + 1.1, "make": True}]
    marks = {"start": 0, "screen": s + 0.2, "cut": s + 1.5, "handoff": ho, "under": ho + 0.4, "pullup": pu, "make": pu + 1.1, "end": pu + 2.5}
    claims = [
        {"type": "near", "a": "O2", "b": "X4", "at": "screen", "max": 1.0, "says": "The guard sets a backscreen..."},
        {"type": "near", "a": "O2", "b": "O1", "at": "handoff", "max": 1.0, "says": "The same guard comes back for the handoff."},
        {"type": "far", "a": "X2", "b": "O4", "at": "cut", "min": 2.0, "says": "His defender stays with him: no help on the cut, the low man takes it."},
        {"type": "open", "player": "O2", "at": "pullup", "min": 1.8, "says": "If he goes under, pull up and shoot."},
        {"type": "behind_arc", "player": "O2", "at": "pullup", "says": "Pull up and shoot (three)."},
        {"type": "order", "marks": ["screen", "cut", "handoff", "under", "pullup", "make"], "says": "backscreen, cut, hand-off, under, pull-up"}]
    return {"id": "spanoulis-b-under", "title": "Spanoulis B: he goes under the hand-off, pull-up three", "duration": pu + 2.5,
            "concept": "spanoulis", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
            "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start as spanoulis-a-trail; X2 stays attached, X5 takes the cutter.", "X2 goes under the hand-off; O2 stops behind it: pull-up three."]}


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
    tr = build(play("trail"))["tracks"]
    TM["scr"] = round(arrive(tr["O2"], SCR) + 0.05, 2)
    tr = build(play("trail"))["tracks"]
    TM["ho"] = round(max(arrive(tr["O2"], HO_O2, TM["scr"]), arrive(tr["O1"], HO_O1)) + 0.02, 2)
    tr = build(play("trail"))["tracks"]
    TM["lay"] = round(arrive(tr["O2"], LAY, TM["ho"]) + 0.02, 2)
    tb = build(play("under"))["tracks"]
    TM["pu"] = round(arrive(tb["O2"], PU, TM["ho"]) + 0.08, 2)
    print("TM", TM)
    for s in (play("trail"), play("under")):
        p = build(s)
        print("built", s["id"], p["duration"])
