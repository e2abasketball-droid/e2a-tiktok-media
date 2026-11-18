#!/usr/bin/env python3
"""HOW TO BREAK A 3-2 ZONE (owner brief 2026-11-18 02:54Z). Original E2A possession, generic coaching knowledge.
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Basket at the top (yaw 0): x > 0 is screen-LEFT,
so the owner's "right" side (O3 corner, O4 short corner) is x < 0.
  Shared start (same in A and B, up to the catch T): O1 (left slot, x>0) swings to O2 (right slot); X1 (middle of the top
  line, close to the high post) steps up to the ball; the gap opens behind him; O5 waits low on the weak side (x>0), plants
  and flashes to the nail, shows his hands; bounce pass by X1's inside hip, through the top line; catch, faces the rim.
  A zone32-a-cut     X4 (low, right) steps up to O5; O4 cuts behind him from the short corner; O5 leads him to the rim;
                     X5 starts the help from the weak side, late; layup.
  B zone32-b-corner  X4 and X5 sink to close the cut; O5 kicks out to O3 in the right corner; X3 recovers from the top,
                     the ball beats him; O3 catches with his feet behind the arc and shoots, make."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T_ = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (generic high-post attack against a 3-2 zone: swing, flash to the nail, read the low defender; no copied possession)"
PL = [P("O1", "O", "Left guard: opens with the ball, swings it"), P("O2", "O", "Right guard: receives the swing, hits the nail"),
      P("O3", "O", "Right corner shooter, behind the arc"), P("O4", "O", "Right short corner: cuts behind the low defender"),
      P("O5", "O", "Big: waits low on the weak side, flashes to the nail"),
      P("X1", "X", "Middle of the top line", "O1"), P("X2", "X", "Top line, left wing", "O1"), P("X3", "X", "Top line, right wing", "O2"),
      P("X4", "X", "Low line, right", "O4"), P("X5", "X", "Low line, left", "O5")]
NAIL = [0.1, 5.85]
S = {"O1": [2.55, 9.15], "O2": [-3.2, 9.0], "O3": [-6.85, 1.05], "O4": [-3.75, 1.1], "O5": [2.75, 3.35],
     "X1": [0.35, 7.35], "X2": [3.0, 7.95], "X3": [-4.05, 6.45], "X4": [-2.05, 2.85], "X5": [2.0, 2.95]}
TM = {}


def common():
    legs = {"X1": [{"at": 0.6, "via": [[-1.0, 8.35]], "to": [-2.0, 8.95], "dur": 1.0}],
            "X2": [{"at": 0.85, "to": [2.15, 7.05], "dur": 0.85}],
            "X3": [{"at": 0.9, "to": [-3.85, 6.75], "dur": 0.7}],
            "O5": [{"at": 1.5, "via": [[1.75, 4.45]], "to": NAIL, "dur": 1.0}],
            "O1": [{"at": 1.3, "to": [2.95, 9.05], "dur": 0.7}]}
    acts = {"X1": [st("O1", 0, 0.6), st("O2", 0.6, 2.95)], "X2": [st("O1", 0, 1.2), st("O2", 1.2, 9)], "X3": [st("O2", 0, 2.4)],
            "X4": [st("O2", 0, 2.6)], "X5": [st("O2", 0, 2.6)],
            "O5": [{"type": "catchReady", "from": 2.1, "to": 3.05}]}
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": 0.55},
            {"type": "pass", "from": "O1", "to": "O2", "t0": 0.55, "t1": 1.12, "style": "chest"},
            {"type": "hold", "player": "O2", "from": 1.12, "to": 2.5},
            {"type": "pass", "from": "O2", "to": "O5", "t0": 2.5, "t1": 3.0, "style": "bounce"},
            {"type": "hold", "player": "O5", "from": 3.0, "to": 3.45}]
    legs["X1"].append({"at": 2.65, "to": [-1.0, 7.3], "dur": 0.75})       # recovers toward the nail: the gap closes
    marks = {"start": 0, "swing": 0.55, "swingCatch": 1.12, "x1step": 0.6, "x1set": 1.6, "plant": 1.5, "flash": 1.62,
             "nail": 2.48, "hands": 2.1, "pass": 2.5, "catch": 3.0, "decision": 3.45}
    return legs, acts, ball, marks


def build_raw(kind, legs, ball, acts):
    s = {"id": f"_tmp-{kind}", "title": "tmp", "duration": 9.0, "players": PL, "start": S, "legs": legs, "ball": ball, "actions": acts}
    sp = os.path.join("/tmp", f"_tmp-zone32-{kind}.spec.json")
    json.dump(s, open(sp, "w"))
    out = sp.replace(".spec.json", ".json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T_, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


def arrive(tr, pt, after=0.0, r=0.03):
    for a, b in zip(tr, tr[1:]):
        if b[0] >= after and abs(b[1] - pt[0]) < r and abs(b[2] - pt[1]) < r:
            return b[0]
    return None


def play(kind):
    legs, acts, ball, marks = common()
    T = marks["decision"]
    if kind == "cut":
        legs["X4"] = [{"at": 3.02, "via": [[-1.75, 3.75]], "to": [-1.05, 4.75], "dur": 0.85}]     # steps up to the catch
        acts["X4"] = [st("O2", 0, 2.8), st("O5", 2.8, 9)]
        cut0 = 3.32
        LAY = [0.05, 2.3]
        legs["O4"] = [{"at": cut0, "via": [[-2.55, 1.6], [-1.1, 2.0]], "to": LAY, "speed": 5.8}]
        b = build_raw(kind, legs, ball, acts)
        arr = arrive(b["tracks"]["O4"], LAY, cut0)
        p0 = arr - 0.55
        p1 = arr - 0.08
        legs["X5"] = [{"at": p0 - 0.05, "to": [1.05, 2.45], "speed": 4.4}]                          # help starts, late
        acts["X5"] = [st("O2", 0, 2.8), st("O5", 2.8, p0), st("O4", p0, 9)]
        acts["X1"].append(st("O5", 2.95, 9))
        acts["X3"].append(st("O5", 2.4, 9))
        ball[-1]["to"] = p0
        ball += [{"type": "pass", "from": "O5", "to": "O4", "t0": p0, "t1": p1, "style": "bounce"},
                 {"type": "hold", "player": "O4", "from": p1, "to": arr + 0.08},
                 {"type": "layup", "player": "O4", "t0": arr + 0.08, "t1": arr + 0.5, "make": True}]
        acts["O4"] = [{"type": "celebrate", "from": arr + 1.2, "to": arr + 2.0}]
        marks.update({"x4step": 3.02, "x4set": 3.87, "cut": cut0, "lead": p0, "cutCatch": p1, "x5help": p0 - 0.05,
                      "layup": arr + 0.08, "make": arr + 0.5, "end": arr + 2.2})
        claims = [
            {"type": "near", "a": "X1", "b": "O2", "at": "x1set", "max": 1.7, "says": "The middle defender steps up."},
            {"type": "far", "a": "X1", "b": "O5", "at": "nail", "min": 1.6, "says": "Hit him before the gap closes (nail open)."},
            {"type": "near", "a": "X4", "b": "O5", "at": "x4set", "max": 1.6, "says": "If he steps up..."},
            {"type": "near_rim", "player": "O4", "at": "layup", "max": 1.5, "says": "Lead the cutter to the rim."},
            {"type": "order", "marks": ["swing", "x1set", "flash", "nail", "pass", "catch", "x4step", "cut", "lead", "layup", "make"], "says": "swing, step, flash, catch, step up, cut, layup"}]
        return {"id": "zone32-a-cut", "title": "Break the 3-2 A: low defender steps up, cut behind him", "duration": arr + 2.2,
                "concept": "zone", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
                "marks": marks, "actions": acts, "claims": claims,
                "notes": ["Swing, X1 steps up, O5 flashes to the nail.", "X4 steps up to O5; O4 cuts behind him; lead pass; X5 late; layup."]}
    # B: the low line sinks, the corner opens
    legs["X4"] = [{"at": 3.05, "to": [-1.45, 2.25], "dur": 0.6}]
    legs["X5"] = [{"at": 3.05, "to": [0.85, 2.35], "dur": 0.6}]
    acts["X4"] = [st("O2", 0, 2.8), st("O5", 2.8, 9)]
    acts["X5"] = [st("O2", 0, 2.8), st("O5", 2.8, 9)]
    legs["O4"] = [{"at": 3.32, "to": [-2.75, 1.45], "dur": 0.55}, {"at": 4.3, "to": [-3.3, 1.3], "dur": 0.6}]   # cut shut, drifts back
    p0 = 4.02
    p1 = p0 + 0.62
    legs["X3"].append({"at": p0 + 0.05, "via": [[-4.9, 4.6]], "to": [-5.95, 2.35], "speed": 5.6})                  # recovers from the top
    acts["X3"] = [st("O2", 0, 2.4), st("O5", 2.4, p0 + 0.1), {"type": "contest", "from": p1 + 0.45, "to": p1 + 1.4, "face": "O3"}]
    acts["X1"].append(st("O5", 2.95, 9))
    ball[-1]["to"] = p0
    sh = p1 + 0.3
    ball += [{"type": "pass", "from": "O5", "to": "O3", "t0": p0, "t1": p1, "style": "chest"},
             {"type": "hold", "player": "O3", "from": p1, "to": sh},
             {"type": "shot", "player": "O3", "t0": sh, "t1": sh + 1.1, "make": True}]
    acts["O3"] = [{"type": "catchReady", "from": p0 - 0.3, "to": p1 + 0.05}, {"type": "celebrate", "from": sh + 1.7, "to": sh + 2.4}]
    marks.update({"sink": 3.05, "sunk": 3.65, "cut": 3.32, "kick": p0, "x3rec": p0 + 0.05, "cornerCatch": p1, "shot": sh,
                  "make": sh + 1.1, "end": sh + 2.5})
    claims = [
        {"type": "near", "a": "X1", "b": "O2", "at": "x1set", "max": 1.7, "says": "Same swing, same step."},
        {"type": "near_rim", "player": "X4", "at": "sunk", "max": 1.8, "says": "They sink to protect the rim."},
        {"type": "far", "a": "X3", "b": "O3", "at": "cornerCatch", "min": 2.0, "says": "The ball beats the defender (corner open)."},
        {"type": "order", "marks": ["swing", "x1set", "nail", "catch", "sink", "kick", "cornerCatch", "shot", "make"], "says": "catch, sink, kick-out, shot"}]
    return {"id": "zone32-b-corner", "title": "Break the 3-2 B: low line sinks, kick to the corner", "duration": sh + 2.5,
            "concept": "zone", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
            "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same swing, step and flash.", "X4 and X5 sink; kick-out to O3; X3 recovers late; corner three."]}


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T_, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T_, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


if __name__ == "__main__":
    for k in ("cut", "corner"):
        p = build(play(k))
        print("built", p["id"], round(p["duration"], 2), {k: round(v, 2) for k, v in p["marks"].items()})
