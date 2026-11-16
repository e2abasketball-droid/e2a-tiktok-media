#!/usr/bin/env python3
"""TWIRL ACTION (owner brief 2026-11-16 04:43Z). Original E2A possession (stagger screens where the first screener
'twirls' off the second screen; generic coaching knowledge, no copied diagram).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Yaw 0 = basket at the top, x<0 = screen RIGHT.
  O1 passer at the top, slides right with the ball. Stagger on the right: O4 (first screener) low, O5 (second) higher.
  O2 (cutter) starts in the right corner, curls TIGHT around O4 towards the rim; X2 trails on his back.
  A twirl-a-three  X4 steps IN to stop the curl -> O4 pivots, uses O5's screen, flares out to the right wing ->
                   O1 hits him -> three; X4 recovers late from inside around O5.
  B twirl-b-curl   X4 stays UP with O4 (top side, follows him over O5) -> the lane is empty -> O1 leads the cutter,
                   catch on the move, layup. X5 stays high with O5.
Weak side: O3 left corner."""
import json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (standard twirl action: stagger screens, first screener uses the second screen; generic coaching knowledge)"
PL = [P("O1", "O", "Passer at the top: reads the first screener's defender"),
      P("O2", "O", "Cutter: curls the first screen to the rim"),
      P("O3", "O", "Left corner"),
      P("O4", "O", "First screener: screens for the cutter, then twirls off the second screen to the wing"),
      P("O5", "O", "Second screener, high"),
      P("X1", "X", "On the ball", "O1"), P("X2", "X", "On the cutter: trails", "O2"),
      P("X3", "X", "Left corner", "O3"), P("X4", "X", "On the first screener: helps (A) / stays up (B)", "O4"),
      P("X5", "X", "On the second screener: stays high", "O5")]
S = {"O1": [1.4, 8.6], "X1": [1.15, 7.8], "O2": [-6.3, 1.4], "X2": [-5.55, 1.3], "O4": [-3.5, 3.0], "X4": [-2.8, 3.2],
     "O5": [-4.3, 5.3], "X5": [-2.95, 6.2], "O3": [6.3, 1.5], "X3": [5.5, 2.1]}
TOP = [-0.9, 8.6]
WING = [-5.9, 6.7]
CURL = [[-5.75, 2.5], [-4.2, 3.6], [-3.5, 4.2], [-2.6, 4.3]]   # tight around O4, towards the rim
CATCH_B = [-1.75, 3.85]
LAY_B = [-0.8, 2.5]
TW = {"go": 2.4, "cut": 0.9}
TA, TB = {}, {}
DUR_A, DUR_B = 7.6, 7.4


def base():
    return {
        "O1": [{"at": 0.15, "to": TOP, "dur": 1.6}],                                          # slides right with the ball
        "X1": [{"at": 0.25, "to": [0.05, 7.95], "dur": 1.6}],
        "O2": [],
        "O4": [{"at": TW["go"], "via": [[-4.35, 3.9], [-4.95, 4.85], [-5.35, 5.7]], "to": WING, "speed": 5.6}],  # pivot, out over O5
    }


def play(kind):
    legs = base()
    acts = {"X3": [st("O3", 0, 8)], "X1": [st("O1", 0, 8)], "X5": [st("O1", 0, 8)],
            "O4": [{"type": "screen", "from": 0.0, "to": TW["go"] - 0.05, "face": "X2"}],
            "O5": [{"type": "screen", "from": 0.0, "to": TW["go"] + 1.3, "face": "X4"}]}
    c = TW["cut"]
    if kind == "three":
        a, dur = TA, DUR_A
        legs["O2"] = [{"at": c, "via": CURL + [[-1.3, 4.55], [0.3, 4.45]], "to": [1.9, 3.8], "speed": 3.6}]
        legs["X2"] = [{"at": c + 0.45, "via": [[-5.3, 2.25], [-4.65, 3.15], [-4.2, 4.15], [-3.3, 4.75], [-2.2, 4.85]], "to": [-0.6, 5.0], "speed": 3.6}]
        legs["X4"] = [{"at": a["help"], "to": [-2.05, 3.5], "dur": 0.55},                      # the help step on the curl
                      {"at": a["rec"], "via": [[-3.0, 4.65], [-3.55, 5.75]], "to": [-4.4, 6.35], "speed": 3.7}]
        acts["X4"] = [st("O2", 0, a["rec"]), {"type": "bump", "from": a["rec"] + 0.45, "to": a["rec"] + 0.75},
                      {"type": "contest", "from": a["rel"] + 0.05, "to": a["rel"] + 0.8}]
        acts["X2"] = [st("O2", 0, 8)]
        acts["O4"] += [{"type": "gather", "from": a["catch"] - 0.08, "to": a["rel"]}, {"type": "celebrate", "from": a["rel"] + 1.3, "to": dur}]
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": a["pass"], "dribble": True, "hand": 1},
                {"type": "pass", "from": "O1", "to": "O4", "t0": a["pass"], "t1": a["catch"], "style": "chest"},
                {"type": "hold", "player": "O4", "from": a["catch"], "to": a["rel"]},
                {"type": "shot", "player": "O4", "t0": a["rel"], "t1": a["rel"] + 1.1, "make": True, "three": True}]
        marks = {"start": 0, "cut": c, "turn": a["turn"], "help": a["help"], "twirl": TW["go"], "pass": a["pass"],
                 "catch": a["catch"], "release": a["rel"], "make": a["rel"] + 1.1, "end": dur}
        claims = [
            {"type": "near", "a": "X4", "b": "O2", "at": "twirl", "max": 2.2, "says": "That pulls the screener's defender inside."},
            {"type": "far", "a": "X4", "b": "O4", "at": "pass", "min": 1.6, "says": "That's the Twirl."},
            {"type": "behind_arc", "player": "O4", "at": "catch", "says": "Help on the curl? Hit the shooter."},
            {"type": "open", "player": "O4", "at": "release", "min": 1.3, "says": "open three"},
            {"type": "order", "marks": ["cut", "turn", "help", "twirl", "pass", "catch", "release", "make"], "says": "curl, help, twirl, three"}]
        return {"id": "twirl-a-three", "title": "Twirl A: the screener's defender helps on the curl, the screener twirls out for three",
                "duration": dur, "concept": "twirl-action", "source": SRC, "squareUp": True, "players": PL, "start": S,
                "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O2 curls O4 tight; X4 steps in to stop the curl.", "O4 pivots, uses O5's screen and flares to the wing; O1 hits him, three."]}
    b, dur = TB, DUR_B
    legs["O2"] = [{"at": c, "via": CURL + [CATCH_B, [-1.3, 3.15]], "to": LAY_B, "speed": 3.6}]
    legs["X2"] = [{"at": c + 0.45, "via": [[-5.3, 2.25], [-4.65, 3.15], [-4.2, 4.15], [-3.3, 4.75], [-2.4, 4.6]], "to": [-1.7, 4.0], "speed": 3.6}]
    legs["X4"] = [{"at": b["up"], "to": [-3.0, 3.5], "dur": 0.42},
                  {"at": TW["go"], "via": [[-3.3, 4.0], [-3.6, 4.75], [-3.75, 5.7], [-4.35, 6.35]], "to": [-5.05, 6.5], "speed": 4.6}]  # steps UP with his man, over the top of O5
    legs["X5"] = [{"at": b["catch"] - 0.2, "to": [-2.3, 5.2], "dur": 0.8}]                    # stays high, late
    acts["X4"] = [st("O4", 0, 8)]
    acts["X2"] = [st("O2", 0, 8)]
    acts["O2"] = [{"type": "celebrate", "from": b["lay"] + 0.9, "to": dur}]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": b["pass"], "dribble": True, "hand": 1},
            {"type": "pass", "from": "O1", "to": "O2", "t0": b["pass"], "t1": b["catch"], "style": "chest"},
            {"type": "hold", "player": "O2", "from": b["catch"], "to": b["lay"]},
            {"type": "layup", "player": "O2", "t0": b["lay"], "t1": b["lay"] + 0.4, "make": True}]
    marks = {"start": 0, "cut": c, "turn": b["turn"], "up": b["up"], "twirl": TW["go"], "pass": b["pass"], "catch": b["catch"],
             "finish": b["lay"], "make": b["lay"] + 0.4, "end": dur}
    claims = [
        {"type": "near", "a": "X4", "b": "O4", "at": "twirl", "max": 1.3, "says": "This time, the defender stays up."},
        {"type": "far", "a": "X2", "b": "O2", "at": "catch", "min": 0.9, "says": "Now the cutter's open."},
        {"type": "near_rim", "player": "O2", "at": "finish", "max": 1.6, "says": "Hit him on the move."},
        {"type": "order", "marks": ["cut", "up", "turn", "pass", "catch", "finish", "make"], "says": "curl, stay up, pass to the cutter, layup"}]
    return {"id": "twirl-b-curl", "title": "Twirl B: the screener's defender stays up, the cutter is open on the curl",
            "duration": dur, "concept": "twirl-action", "source": SRC, "squareUp": True, "players": PL, "start": S,
            "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same stagger and curl as twirl-a-three.", "X4 stays up with O4 over the second screen; O1 leads O2 on the curl, layup."]}


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
    TA.update(turn=1.8, help=1.6, rec=3.0, pass_=3.5, catch=4.0, rel=4.3)
    TA["pass"], TB_ = 3.5, None
    TB.update(turn=1.8, up=2.0, pass_=3.0, catch=3.4, lay=3.8)
    TB["pass"] = 3.0
    tr = build(play("three"))["tracks"]
    turn = round(first_near(tr["O2"], CURL[1], 0.15, TW["cut"]), 3)        # cutter turning around O4
    past = round(first_near(tr["O2"], CURL[2], 0.15, TW["cut"]), 3)        # cutter past the screen
    TW["go"] = round(past + 0.2, 3)
    for d in (TA, TB):
        d["turn"] = turn
    TA["help"] = round(turn + 0.02, 3)
    TB["up"] = round(turn - 0.3, 3)
    tr = build(play("three"))["tracks"]
    TA["catch"] = round(first_near(tr["O4"], WING, 0.2, TW["go"]), 3)
    TA["pass"] = round(TA["catch"] - 0.62, 3)
    TA["rel"] = round(TA["catch"] + 0.36, 3)
    TA["rec"] = round(TA["pass"] - 0.3, 3)
    tr = build(play("curl"))["tracks"]
    TB["catch"] = round(first_near(tr["O2"], CATCH_B, 0.2, TW["cut"]), 3)
    TB["pass"] = round(TB["catch"] - 0.45, 3)
    TB["lay"] = round(first_near(tr["O2"], LAY_B, 0.2, TB["catch"]), 3)
    for s in (play("three"), play("curl")):
        build(s)
        print("built", s["id"], json.dumps(s["marks"]))
