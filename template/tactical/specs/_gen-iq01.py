#!/usr/bin/env python3
"""E2A BASKETBALL IQ 01 - "CAN YOU FIND THE OPEN PLAYER?" (owner master brief 2026-11-26 20:56Z).
4 v 4 half court, drive-and-kick against low-man help:
  O1 (right slot) beats X1 to the middle; X3, the weak-side LOW helper, rotates to the rim to stop the drive and leaves
  O3 in the weak-side corner; X4 (weak-side wing) shows a stunt but keeps O4; X2 pinches but stays with O2.
  The challenge freezes the play when X3 is committed: A = O2 (right corner), B = O4 (left wing), C = O3 (left corner).
  Answer C, for a concrete reason in THIS possession: X3 is at the rim; the next rotation (X4) is 3.8 m away, still
  responsible for O4, and cannot get to the corner before the catch.
Causal timing (no precognition): X1 reacts 0.2 s after the first step; X3 leaves his spot 0.3 s after the drive
starts (he is already in help); X3 closes out 0.2 s after the kick; X4 reacts 0.25 s after the kick.
Coordinates. The brief uses x = lateral (+ = the offence's RIGHT), y = depth from the baseline. The repo engine uses
x < 0 = the offence's RIGHT (= screen RIGHT with the basket-up camera), so repo x = -brief x; y is the same.
Basket centre (0, 1.575); FIBA half court 15 x 14 m; 3-pt line 6.75 m, corners 6.60 m.
  python3 tactical/specs/_gen-iq01.py   (writes tactical/specs/iq01-*.spec.json + tactical/plays/iq01-*.json)"""
import json, os, subprocess, sys

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
B = lambda x, y: [round(-x, 3), y]          # brief coordinates -> repo coordinates
SRC = ("original E2A 4v4 drive-and-kick staging; WABC/FIBA Coaching Manual Level 1-2 principles (ball-you-man help, "
       "low-man help on penetration, help and recover, closeouts); production coordinates, no diagram copied")

PLAYERS = [P("O1", "O", "Ball handler: right slot, drives middle past X1"),
           P("O2", "O", "Strong-side (right) corner: answer A"),
           P("O3", "O", "Weak-side (left) corner shooter: answer C (the open player)"),
           P("O4", "O", "Weak-side (left) wing: answer B"),
           P("X1", "X", "On the ball: beaten on the first step, chases on the hip", "O1"),
           P("X2", "X", "On O2: pinches a step, stays home in the strong-side corner", "O2"),
           P("X3", "X", "Weak-side LOW helper on O3: rotates to the rim to stop the drive (the key defender)", "O3"),
           P("X4", "X", "On O4: sags in help, stunts, keeps O4 (cannot cover the corner too)", "O4")]

START = {"O1": B(3.3, 7.6), "X1": B(3.0, 6.8),
         "O2": B(6.9, 2.2), "X2": B(6.3, 2.8),
         "O3": B(-6.9, 2.2), "X3": B(-4.1, 3.3),
         "O4": B(-5.5, 7.3), "X4": B(-4.3, 6.3)}
GATHER = B(1.0, 3.95)     # O1's jump stop in the lane (the freeze is just before it)
HELP = B(0.2, 3.0)        # X3 in front of the rim, on the drive line
X1END = B(1.75, 4.6)      # X1 trailing on O1's hip
X2PINCH = B(5.75, 3.0)    # X2's pinch: one step to the ball, still within reach of O2
X4SAG = B(-3.95, 5.95)    # X4 sinks (stunt) toward the drive
X4STEP = B(-4.4, 5.2)   # X4's late step toward the corner after the kick (he stays with O4)
CLOSE = B(-5.75, 2.55)    # X3's late closeout spot (short of O3)

K = {"drive": 0.6, "x1": 0.8, "help": 0.9, "sag": 1.0, "pinch": 1.05, "gather": 1.85, "kick": 2.15, "catch": 2.95, "rel": 3.3,
     "driveSpeed": 5.8}
DUR = 5.6


def play():
    legs = {
        "O1": [{"at": K["drive"], "via": [B(2.15, 6.55)], "to": GATHER, "speed": K["driveSpeed"]}],
        "X1": [{"at": K["x1"], "via": [B(2.55, 6.0)], "to": X1END, "speed": 5.6}],
        "X3": [{"at": K["help"], "via": [B(-1.8, 3.2)], "to": HELP, "speed": 6.6},
               {"at": K["kick"] + 0.2, "via": [B(-2.6, 2.75)], "to": CLOSE, "speed": 6.6}],
        "X2": [{"at": K["pinch"], "to": X2PINCH, "speed": 2.2},
               {"at": K["kick"] + 0.3, "to": B(6.35, 2.65), "speed": 2.4}],
        "X4": [{"at": K["sag"], "to": X4SAG, "speed": 2.6},
               {"at": K["kick"] + 0.25, "to": X4STEP, "speed": 3.0}],
        "O2": [], "O3": [], "O4": [],
    }
    if K.get("measure"):
        legs["X3"] = legs["X3"][:1]
    acts = {
        "O1": [{"type": "face", "from": 0, "to": K["drive"], "face": "X1"}],
        "X1": [st("O1", 0, DUR)],
        "X2": [st("O2", 0, K["pinch"]), st("O1", K["pinch"], K["kick"] + 0.2), st("O2", K["kick"] + 0.25, DUR)],
        "X3": [st("O1", 0, K["kick"] + 0.15), {"type": "closeout", "from": K["kick"] + 0.3, "to": K["rel"] + 0.1},
               {"type": "contest", "from": K["rel"], "to": K["rel"] + 0.55}],
        "X4": [st("O1", 0, K["kick"] + 0.2), st("O4", K["kick"] + 0.25, DUR)],
        "O2": [{"type": "face", "from": 0, "to": DUR, "face": "O1"}],
        "O4": [{"type": "face", "from": 0, "to": DUR, "face": "O1"}],
        "O3": [{"type": "face", "from": 0, "to": K["kick"], "face": "O1"},
               {"type": "catchReady", "from": K["kick"] + 0.05, "to": K["catch"] + 0.05, "face": "O1"},
               {"type": "celebrate", "from": K["rel"] + 1.25, "to": DUR - 0.05}],
    }
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": K["gather"], "dribble": True, "hand": 1},
            {"type": "hold", "player": "O1", "from": K["gather"], "to": K["kick"]},
            {"type": "pass", "from": "O1", "to": "O3", "t0": K["kick"], "t1": K["catch"], "style": "overhead", "arc": 2.9, "eyes": 0.3},
            {"type": "hold", "player": "O3", "from": K["catch"], "to": K["rel"]},
            {"type": "shot", "player": "O3", "t0": K["rel"], "t1": K["rel"] + 1.05, "make": True, "three": True}]
    marks = {"start": 0, "drive": K["drive"], "x1": K["x1"], "help": K["help"], "beat": K.get("beat", K["drive"] + 0.45),
             "decide": K.get("decide", K["gather"] - 0.1), "gather": K["gather"], "kick": K["kick"], "catch": K["catch"],
             "release": K["rel"], "make": K["rel"] + 1.05, "end": DUR}
    claims = [
        {"type": "reacts_after", "player": "X1", "event": "drive", "min": 0.15, "says": "He beats his man (X1 reacts to the first step)"},
        {"type": "reacts_after", "player": "X3", "event": "drive", "min": 0.25, "says": "Here comes the help (X3 rotates after the drive starts)"},
        {"type": "near_rim", "player": "X3", "at": "decide", "max": 2.4, "says": "He leaves the corner to stop the drive"},
        {"type": "far", "a": "X3", "b": "O3", "at": "decide", "min": 5.5, "says": "C: his defender is at the rim"},
        {"type": "near", "a": "X2", "b": "O2", "at": "decide", "max": 1.75, "says": "A? His defender is still home"},
        {"type": "near", "a": "X4", "b": "O4", "at": "decide", "max": 2.4, "says": "B? Still guarded"},
        {"type": "far", "a": "X4", "b": "O3", "at": "decide", "min": 4.2, "says": "the next rotation (X4) is far from the corner"},
        {"type": "far", "a": "X4", "b": "O3", "at": "catch", "min": 3.2, "says": "The next rotation is too late (X4 at the catch)"},
        {"type": "near", "a": "X4", "b": "O4", "at": "catch", "max": 2.5, "says": "X4 keeps O4 (no full rotation before the catch)"},
        {"type": "reacts_after", "player": "X4", "event": "kick", "min": 0.2, "says": "X4 reacts to the pass, not before it"},
        {"type": "behind_arc", "player": "O3", "at": "catch", "says": "Kick it to the corner (a corner three)"},
        {"type": "open", "player": "O3", "at": "release", "min": 2.0, "says": "C is open: a clean look"},
        {"type": "order", "marks": ["drive", "help", "decide", "gather", "kick", "catch", "release", "make"],
         "says": "drive, help, decision, kick, catch, shot"}]
    return {"id": "iq01-open-player", "title": "Basketball IQ 01: drive and kick, the low-man help leaves the weak-side corner",
            "duration": DUR, "concept": "drive-and-kick", "format": "4v4", "kitSet": "iq", "source": SRC, "squareUp": True, "catchV2": 2,
            "handBallClear": True, "v33": "compile", "realism": 3,
            "players": PLAYERS, "start": START, "legs": legs, "ball": ball, "marks": marks, "actions": acts,
            "claims": claims, "screens": [],
            "coords": {"system": "repo", "x": "lateral, x < 0 = offence's right", "y": "depth from the baseline", "basket": [0, 1.575],
                       "brief": "repo x = -brief x"},
            "notes": ["4 v 4: four attackers, four defenders, one ball; nobody leaves the floor.",
                      "Letters at the freeze: A = O2 (right corner), B = O4 (left wing), C = O3 (left corner).",
                      "X3 starts in help (between O3 and the lane) and rotates 0.3 s after the drive starts.",
                      "X4 sags and stunts, then reacts to the kick: he keeps O4 and never reaches the corner before the catch.",
                      "X2 pinches one step and stays within reach of O2."]}


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
            return round(t, 3)
        t += 0.005
    return None


if __name__ == "__main__":
    K["measure"] = True
    tr = build(play())["tracks"]
    K["measure"] = False
    g = first_near(tr["O1"], GATHER, 0.03, K["drive"])
    K["gather"] = g
    # O1 is past X1 when his y drops below X1's (he has turned the corner on him)
    t = K["drive"]
    while pos(tr["O1"], t)[1] > pos(tr["X1"], t)[1] - 0.05 and t < g:
        t += 0.005
    K["beat"] = round(t, 3)
    h = first_near(tr["X3"], HELP, 0.45, K["help"])
    K["decide"] = round(min(h or g - 0.1, g - 0.08), 3)
    K["kick"] = round(max(g + 0.28, (first_near(tr["X3"], HELP, 0.03, K["help"]) or 0) + 0.05), 3)
    K["catch"] = round(K["kick"] + 0.8, 3)
    K["rel"] = round(K["catch"] + 0.33, 3)
    s = play()
    p = build(s)
    print("built", s["id"], json.dumps(s["marks"]))
