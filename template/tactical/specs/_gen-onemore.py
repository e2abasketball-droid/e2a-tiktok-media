#!/usr/bin/env python3
"""ONE MORE DRIBBLE: reading the last defender in a 2-on-1 (owner brief 2026-11-17 05:40Z). Original E2A possession,
generic coaching knowledge; only the decision/freeze/replay STRUCTURE of the owner's reference is reused.
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Basket at the top (yaw 0): x > 0 is screen-left.
  O4 ball handler on the left, O8 wide on the right, X10 the only defender, centred in front of the rim.
  All three plays share the SAME first T seconds (same legs, same dribble, same ball phase): the decision point.
  A onemore-a-early   early pass: X10 is still central when the ball leaves, he slides and contests the catch.
  B onemore-b-commit  one more dribble toward the rim: X10 plants and steps up to the ball, O8 cuts, pass, layup.
  C onemore-c-stay    same dribble: X10 stays with the pass (shades to O8), the lane is O4's: layup."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T_ = os.path.dirname(os.path.dirname(D))
SRC = "original E2A play (2-on-1 read of the last defender; generic coaching knowledge, no copied possession)"
PL = [{"id": "O4", "team": "O", "role": "Ball handler: pass now or one more dribble"},
      {"id": "O8", "team": "O", "role": "Wide teammate on the right"},
      {"id": "X10", "team": "X", "role": "The only defender: steps up or stays with the pass", "guards": "O4"}]
S = {"O4": [3.0, 12.3], "O8": [-4.1, 11.4], "X10": [0.35, 5.7]}
DEC4 = [2.05, 7.45]     # O4 at the decision point
DEC8 = [-3.65, 6.0]     # O8 wide right at the decision point
DECX = [0.05, 4.65]     # X10 centred, between both, in front of the rim
T = 3.3                 # decision time (ball back in the hand, same pose in all three plays)
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}


def common():
    legs = {"O4": [{"at": 0.0, "via": [[2.85, 10.6]], "to": DEC4, "dur": T}],
            "O8": [{"at": 0.0, "via": [[-4.2, 9.2]], "to": DEC8, "dur": T}],
            "X10": [{"at": 0.9, "to": DECX, "dur": T - 0.9}]}
    ball = [{"type": "hold", "player": "O4", "from": 0, "to": T, "dribble": True}]
    return legs, ball


def arrive(tr, pt, after=0.0, r=0.03):
    for a, b in zip(tr, tr[1:]):
        if b[0] >= after and abs(b[1] - pt[0]) < r and abs(b[2] - pt[1]) < r:
            return b[0]
    return None


TM = {}


def play(kind):
    legs, ball = common()
    acts = {"X10": [st("O4", 0.0, T + 0.2)]}
    if kind == "early":
        p0, p1 = T + 0.15, T + 0.75
        legs["O4"].append({"at": p1 + 0.2, "to": [1.55, 6.5], "speed": 2.2})
        legs["O8"].append({"at": T + 0.02, "to": [-3.1, 5.45], "dur": 0.75})
        legs["X10"].append({"at": p0 + 0.04, "to": [-2.2, 4.95], "dur": 0.8})
        acts["X10"] += [{"type": "contest", "from": p1 + 0.15, "to": p1 + 1.6}]
        b = build_raw(kind, legs, ball + [{"type": "hold", "player": "O4", "from": T, "to": p0}, {"type": "pass", "from": "O4", "to": "O8", "t0": p0, "t1": p1}, {"type": "hold", "player": "O8", "from": p1, "to": p1 + 1.9}], acts)
        tx = arrive(b["tracks"]["X10"], [-2.2, 4.95], p0)
        ball += [{"type": "hold", "player": "O4", "from": T, "to": p0},
                 {"type": "pass", "from": "O4", "to": "O8", "t0": p0, "t1": p1, "style": "chest"},
                 {"type": "hold", "player": "O8", "from": p1, "to": p1 + 1.9}]
        marks = {"start": 0, "decision": T, "release": p0, "slide": p0 + 0.06, "catch": p1, "contest": round(tx, 3), "end": p1 + 1.9}
        claims = [
            {"type": "far", "a": "O8", "b": "X10", "at": "decision", "min": 3.2, "says": "He looks wide open."},
            {"type": "far", "a": "X10", "b": "O8", "at": "release", "min": 3.2, "says": "The defender's still in the middle when the ball leaves."},
            {"type": "near", "a": "X10", "b": "O8", "at": "contest", "max": 1.1, "says": "He's there on the catch."},
            {"type": "order", "marks": ["decision", "release", "slide", "catch", "contest"], "says": "pass, slide, catch contested"}]
        claims = [c for c in claims if c["says"]]
        return {"id": "onemore-a-early", "title": "One more dribble A: early pass, catch contested", "duration": p1 + 1.9,
                "concept": "onemore", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
                "marks": marks, "actions": acts, "claims": claims,
                "notes": ["Shared decision point at T; O4 picks up and passes early.", "X10 is still central at the release and slides to contest the catch."]}
    # B and C: the same extra dribble toward the rim
    if kind == "commit":
        P4 = [1.6, 5.95]
        legs["O4"].append({"at": T, "to": P4, "dur": 0.85})
        plant = T + 0.22
        legs["X10"].append({"at": plant, "to": [1.25, 5.05], "dur": 0.6})
        acts["X10"] = [st("O4", 0.0, T + 1.0)]
        cut0 = T + 0.62
        CATCH = [-2.45, 4.85]
        LAY = [-0.85, 2.6]
        legs["O8"].append({"at": cut0, "via": [[-3.25, 5.5], CATCH], "to": LAY, "speed": 3.6})
        b = build_raw(kind, legs, ball, acts)
        tc = arrive(b["tracks"]["O8"], CATCH, cut0)
        tl = arrive(b["tracks"]["O8"], LAY, cut0)
        p0, p1 = round(tc - 0.42, 3), tc
        legs["X10"].append({"at": p0 + 0.18, "via": [[0.75, 4.0]], "to": [0.4, 3.25], "speed": 4.2})
        acts["X10"] += [{"type": "contest", "from": tl - 0.15, "to": tl + 0.6}]
        ball += [{"type": "hold", "player": "O4", "from": T, "to": T + 0.85, "dribble": True},
                 {"type": "hold", "player": "O4", "from": T + 0.85, "to": p0},
                 {"type": "pass", "from": "O4", "to": "O8", "t0": p0, "t1": p1, "style": "chest"},
                 {"type": "hold", "player": "O8", "from": p1, "to": tl},
                 {"type": "layup", "player": "O8", "t0": tl, "t1": tl + 0.4, "make": True}]
        acts["O8"] = [{"type": "celebrate", "from": tl + 1.0, "to": tl + 1.8}]
        marks = {"start": 0, "decision": T, "plant": plant, "shift": plant + 0.3, "pass": p0, "catch": p1, "layup": tl, "make": tl + 0.4, "end": tl + 2.0}
        claims = [
            {"type": "near", "a": "X10", "b": "O4", "at": "pass", "max": 1.25, "says": "That first step takes him toward the ball."},
            {"type": "far", "a": "X10", "b": "O8", "at": "pass", "min": 3.0, "says": "Now the lane opens."},
            {"type": "open", "player": "O8", "at": "catch", "min": 2.0, "says": "Lead your teammate into the space."},
            {"type": "near_rim", "player": "O8", "at": "layup", "max": 1.5, "says": "#8 receives, cuts and finishes."},
            {"type": "order", "marks": ["decision", "plant", "shift", "pass", "catch", "layup", "make"], "says": "dribble, plant, shift, pass, catch, layup"}]
        return {"id": "onemore-b-commit", "title": "One more dribble B: he steps up, pass, layup", "duration": tl + 2.0,
                "concept": "onemore", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
                "marks": marks, "actions": acts, "claims": claims,
                "notes": ["Same start and decision point; O4 takes one more dribble toward the rim.", "X10 plants and steps up to the ball; O8 cuts into the space, catches in front and lays up."]}
    # C: X10 stays with the pass, O4 keeps the dribble to the rim
    LAY = [0.55, 2.75]
    legs["O4"].append({"at": T, "via": [[1.6, 5.95]], "to": LAY, "speed": 4.4})
    shade = T + 0.22
    legs["X10"].append({"at": shade, "to": [-1.75, 4.85], "dur": 0.7})
    legs["O8"].append({"at": T + 0.3, "to": [-3.75, 5.35], "speed": 2.0})
    acts["X10"] = [st("O4", 0.0, T + 2.5)]
    b = build_raw(kind, legs, ball, acts)
    tl = arrive(b["tracks"]["O4"], LAY, T)
    legs["X10"].append({"at": tl - 0.45, "to": [-0.75, 3.55], "speed": 3.8})
    ball += [{"type": "hold", "player": "O4", "from": T, "to": tl - 0.45, "dribble": True},
             {"type": "hold", "player": "O4", "from": tl - 0.45, "to": tl},
             {"type": "layup", "player": "O4", "t0": tl, "t1": tl + 0.4, "make": True}]
    acts["O4"] = [{"type": "celebrate", "from": tl + 1.0, "to": tl + 1.8}]
    marks = {"start": 0, "decision": T, "stay": shade + 0.72, "lane": T + 0.75, "gather": tl - 0.45, "layup": tl, "make": tl + 0.4, "end": tl + 2.0}
    claims = [
        {"type": "near", "a": "X10", "b": "O8", "at": "stay", "max": 2.75, "says": "He stays with your teammate."},
        {"type": "far", "a": "X10", "b": "O4", "at": "lane", "min": 2.2, "says": "The lane is yours."},
        {"type": "near_rim", "player": "O4", "at": "layup", "max": 1.5, "says": "Go finish."},
        {"type": "order", "marks": ["decision", "stay", "gather", "layup", "make"], "says": "dribble, defender stays, gather, layup"}]
    return {"id": "onemore-c-stay", "title": "One more dribble C: he stays with the pass, finish", "duration": tl + 2.0,
            "concept": "onemore", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
            "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start and the same extra dribble.", "X10 shades to O8 to protect the pass; O4 keeps the dribble, gathers and lays up."]}


def build_raw(kind, legs, ball, acts):
    s = {"id": f"_tmp-{kind}", "title": "tmp", "duration": 12.0, "players": PL, "start": S, "legs": legs, "ball": ball, "actions": acts}
    sp = os.path.join("/tmp", f"_tmp-onemore-{kind}.spec.json")
    json.dump(s, open(sp, "w"))
    out = sp.replace(".spec.json", ".json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T_, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T_, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T_, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


if __name__ == "__main__":
    for k in ("early", "commit", "stay"):
        p = build(play(k))
        print("built", p["id"], round(p["duration"], 2), p["marks"])
