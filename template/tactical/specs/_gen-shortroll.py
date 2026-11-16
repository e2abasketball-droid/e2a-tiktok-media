#!/usr/bin/env python3
"""SHORT ROLL 4-ON-3 (owner request 2026-11-16 11:37Z: same method as the Spain pick-and-roll, a similar but different
play). Original E2A possession (standard blitz / short-roll read, generic coaching knowledge, no copied diagram).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Half-court view with the basket at the
top (yaw 0): x < 0 is the RIGHT of the screen.
  O1 top with the ball, O5 sets the ball screen; X1 and X5 trap O1 (two on the ball). O5 short-rolls to the free-throw
  line and catches the pass out of the trap: four on three behind it. O4 in the left corner, O3 left wing, O2 right corner.
  A sr-a-corner  X4 (the low man) steps up to stop O5 -> kick-out to O4 in the corner, open three.
  B sr-b-rim     X4 stays home in the corner -> O5 keeps going, layup."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (standard blitz / short-roll 4-on-3 read, generic coaching knowledge)"
PL = [P("O1", "O", "Ball handler at the top, gets trapped"), P("O2", "O", "Right corner"), P("O3", "O", "Left wing"),
      P("O4", "O", "Left corner: the kick-out shooter"), P("O5", "O", "Screener: short roll to the free-throw line"),
      P("X1", "X", "On the ball: traps", "O1"), P("X2", "X", "Right corner", "O2"), P("X3", "X", "Left wing", "O3"),
      P("X4", "X", "The low man (left corner)", "O4"), P("X5", "X", "On the screener: traps", "O5")]
S = {"O1": [0.9, 9.3], "X1": [0.7, 8.45], "O5": [-1.6, 6.3], "X5": [-1.2, 5.55], "O2": [-6.6, 1.3], "X2": [-5.6, 2.0],
     "O3": [5.2, 6.4], "X3": [4.5, 5.9], "O4": [6.8, 1.3], "X4": [4.7, 2.5]}
SCR = [0.0, 8.5]        # ball screen, on X1's right shoulder
TRAP = [-2.0, 9.05]     # where O1 gets trapped
SHORT = [0.2, 5.9]      # short-roll catch, free-throw line
SHARED = {
    "O5": [{"at": 0.15, "via": [[-1.1, 7.6]], "to": SCR, "speed": 3.6}],
    "O1": [{"at": 1.45, "via": [[0.4, 9.55], [-1.0, 9.45]], "to": TRAP, "speed": 4.4}],
    "X1": [{"at": 1.6, "via": [[0.75, 9.45], [-0.3, 9.95]], "to": [-1.55, 9.8], "speed": 4.2}],
    "X5": [{"at": 0.6, "to": [-1.0, 7.05], "dur": 0.7},
           {"at": 1.55, "to": [-2.65, 8.2], "dur": 0.95}],
}


def play(kind):
    legs = {k: [dict(l) for l in v] for k, v in SHARED.items()}
    acts = {"X2": [st("O2", 0, 7.0)], "X3": [st("O3", 0, 7.0)], "X1": [st("O1", 0, 1.6), st("O1", TB["trap"] - 0.3, TB["catch"])],
            "X5": [st("O1", TB["trap"] - 0.3, TB["catch"])],
            "O5": [{"type": "screen", "from": TM["set"], "to": 2.0, "face": "X1"}]}
    legs["O5"].append({"at": 2.05, "to": SHORT, "dur": 1.05})
    pa, ca = TB["trap"], TB["catch"]
    if kind == "corner":
        legs["X4"] = [{"at": ca - 1.0, "via": [[3.0, 3.5]], "to": [0.95, 4.6], "speed": 4.6},     # the low man steps up
                      {"at": ca + 1.2, "to": [3.4, 3.1], "speed": 3.4}]                          # closes out late
        acts["X4"] = [st("O4", 0, ca - 1.0), st("O5", ca + 0.3, ca + 1.2)]
        acts["O4"] = [{"type": "celebrate", "from": ca + 2.95, "to": 7.0}]
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": pa, "dribble": True},
                {"type": "pass", "from": "O1", "to": "O5", "t0": pa, "t1": ca, "style": "overhead"},
                {"type": "hold", "player": "O5", "from": ca, "to": ca + 0.4},
                {"type": "pass", "from": "O5", "to": "O4", "t0": ca + 0.4, "t1": ca + 1.15, "style": "chest"},
                {"type": "hold", "player": "O4", "from": ca + 1.15, "to": ca + 1.5},
                {"type": "shot", "player": "O4", "t0": ca + 1.5, "t1": ca + 2.55, "make": True}]
        marks = {"start": 0, "set": TM["set"], "use": 1.45, "trap": pa, "catch": ca, "step": ca - 1.0, "kick": ca + 0.4,
                 "kcatch": ca + 1.15, "release": ca + 1.5, "make": ca + 2.55, "end": 7.0}
        claims = [
            {"type": "near", "a": "X1", "b": "O1", "at": "trap", "max": 1.3, "says": "Two on the ball."},
            {"type": "near", "a": "X5", "b": "O1", "at": "trap", "max": 1.3, "says": "Two on the ball."},
            {"type": "near", "a": "X4", "b": "O5", "at": "kick", "max": 1.9, "says": "If the low man steps up to stop him..."},
            {"type": "far", "a": "X4", "b": "O4", "at": "release", "min": 3.0, "says": "...the corner is empty. Open three."},
            {"type": "behind_arc", "player": "O4", "at": "release", "says": "Open three."},
            {"type": "order", "marks": ["set", "use", "trap", "catch", "kick", "kcatch", "release", "make"], "says": "screen, trap, short roll, kick-out, three"}]
        return {"id": "sr-a-corner", "title": "Short roll A: the low man steps up, kick-out to the corner", "duration": 7.0,
                "concept": "short-roll", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
                "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O5 screens for O1; X1 and X5 trap O1; O5 short-rolls to the free-throw line and catches.",
                          "X4 leaves the corner to stop O5; O5 kicks out to O4: open corner three."]}
    legs["O5"].append({"at": ca + 0.25, "to": [0.1, 3.0], "dur": 0.95})
    legs["O5"].append({"at": "+0", "to": [0.05, 2.6], "dur": 0.45})                       # keeps going (dribble)
    legs["X4"] = [{"at": 2.6, "to": [5.4, 2.0], "dur": 0.6}]                                      # stays home in the corner
    legs["X2"] = [{"at": ca + 0.35, "to": [-3.4, 2.45], "dur": 0.8}]                              # late help from the other corner
    acts["X4"] = [st("O4", 0, 7.0)]
    acts["X2"] = [st("O2", 0, ca + 0.35)]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": pa, "dribble": True},
            {"type": "pass", "from": "O1", "to": "O5", "t0": pa, "t1": ca, "style": "overhead"},
            {"type": "hold", "player": "O5", "from": ca, "to": ca + 1.3, "dribble": True},
            {"type": "layup", "player": "O5", "t0": ca + 1.3, "t1": ca + 1.7, "make": True}]
    acts["O5"].append({"type": "celebrate", "from": ca + 2.1, "to": 6.0})
    marks = {"start": 0, "set": TM["set"], "use": 1.45, "trap": pa, "catch": ca, "stay": 2.6, "drive": ca + 0.25,
             "finish": ca + 1.3, "make": ca + 1.7, "end": 6.0}
    claims = [
        {"type": "near", "a": "X1", "b": "O1", "at": "trap", "max": 1.3, "says": "Two on the ball."},
        {"type": "near", "a": "X5", "b": "O1", "at": "trap", "max": 1.3, "says": "Two on the ball."},
        {"type": "near", "a": "X4", "b": "O4", "at": "drive", "max": 1.8, "says": "If he stays home..."},
        {"type": "near_rim", "player": "O5", "at": "finish", "max": 1.5, "says": "The big keeps going. Easy two."},
        {"type": "order", "marks": ["set", "use", "trap", "catch", "drive", "finish", "make"], "says": "screen, trap, short roll, drive, layup"}]
    return {"id": "sr-b-rim", "title": "Short roll B: the low man stays home, the big keeps going", "duration": 6.0,
            "concept": "short-roll", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
            "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start as sr-a-corner.", "X4 stays with O4 in the corner; nobody guards the rim; O5 drives and lays it in."]}


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


TM = {"set": 1.0}
TB = {"trap": 2.4, "catch": 2.9}

if __name__ == "__main__":
    tr = build(play("rim"))["tracks"]
    TM["set"] = round(first_near(tr["O5"], SCR, 0.03) + 0.08, 2)
    t_trap = first_near(tr["O1"], TRAP, 0.05)
    t_short = first_near(tr["O5"], SHORT, 0.05)
    TB["trap"] = round(max(t_trap + 0.3, t_short - 0.5), 2)
    TB["catch"] = round(TB["trap"] + 0.5, 2)
    print("TM", TM, "TB", TB)
    for s in (play("corner"), play("rim")):
        p = build(s)
        print("built", s["id"], p["duration"])
