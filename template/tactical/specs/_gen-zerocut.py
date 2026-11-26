#!/usr/bin/env python3
"""ZERO CUT (owner master brief 2026-11-26, thread "Producir Reel Zero Cut"; reference = BYU 'Zoom/Zero Cut' TikTok compilation).
The big catches up top; the guard sprints toward him for a dribble handoff; his defender TRAILS and jumps over the top
to beat the handoff; the guard plants (no handoff) and cuts BEHIND him to the rim; the big bounce-passes into space.
  A zerocut-a-layup  the low help (X3, weak side) stays home -> O2 catches in stride and finishes.
  B zerocut-b-kick   X3 steps across to protect the rim -> O5 reads it and skips to O3 in the weak-side corner.
Causal timing (no precognition): X2 follows O2 +0.25 s; X2 commits to the handoff side only after O2 shows his hands;
O2 plants when X2 is committed; X2 turns +0.3 s after the cut starts; (B) X3 helps +0.3 s after the cut starts;
O5 kicks only once the help is committed; X3 closes out +0.2 s after the kick. Nobody teleports, nobody freezes.
Repo axes: x < 0 = the offence's RIGHT = screen RIGHT with the basket-up camera. Basket (0, 1.575).
  python3 tactical/specs/_gen-zerocut.py   (writes tactical/specs/zerocut-{a-layup,b-kick}.spec.json + tactical/plays/)"""
import json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = ("original E2A staging of the 'Zero Cut' (backdoor out of a fake dribble handoff, the counter of the Zoom/DHO "
       "action) as shown in the owner's reference (BYU game clips, labels Trail / Contact / Dime / Leave) and WABC/FIBA "
       "backdoor teaching; production coordinates, no frame or diagram copied")

PLAYERS = [P("O1", "O", "Left slot: enters the ball to the big, keeps the spacing"),
           P("O2", "O", "Right wing: sprints toward the big to sell the handoff, plants, cuts behind his defender (the cutter)"),
           P("O3", "O", "Weak-side (left) corner shooter"),
           P("O4", "O", "Strong-side (right) corner: spacing"),
           P("O5", "O", "Big: pops to the top, catches, the passer (bounce pass / skip pass)"),
           P("X1", "X", "On O1", "O1"),
           P("X2", "X", "On O2: trails the sprint and jumps over the top to beat the handoff", "O2"),
           P("X3", "X", "LOW HELP on O3: stays home (A) / steps across to the rim (B)", "O3"),
           P("X4", "X", "On O4: stays home in the strong-side corner", "O4"),
           P("X5", "X", "On O5: follows the pop, cheats to the handoff side (ready to show on the DHO)", "O5")]

START = {"O1": [2.9, 8.45], "X1": [2.45, 7.45],
         "O2": [-5.6, 5.0], "X2": [-4.95, 4.7],
         "O3": [6.6, 1.25], "X3": [3.35, 2.45],
         "O4": [-6.6, 1.2], "X4": [-5.65, 1.85],
         "O5": [-1.4, 6.1], "X5": [-0.9, 5.45]}
TOP = [-0.6, 8.05]          # O5 catches up top
HAND = [-2.3, 7.3]          # O2's plant = where the handoff would happen (right of the big, a step below him)
OVER = [-2.55, 8.0]         # X2 jumps over the top, between O2 and the handoff
CATCH = [-1.3, 3.55]        # O2 catches in stride
LAY = [-0.72, 2.35]         # layup take-off
HELP = [-0.45, 2.95]        # (B) X3 in front of the rim on the cutter's lane
CLOSE = [5.55, 1.75]        # (B) X3's late closeout
DA, DB = 5.6, 6.4

K = {"pop": 0.1, "pass1": 0.75, "catch1": 1.25, "sprint": 1.1, "show": 1.9, "plant": 2.45, "cut": 2.6,
     "x2turn": 2.9, "pass2": 3.0, "catch2": 3.45, "lay": 3.6, "help": 2.9, "kick": 3.6, "catch3": 4.4, "rel": 4.7,
     "cutSpeed": 6.6}


def common():
    legs = {
        "O5": [{"at": K["pop"], "to": TOP, "speed": 3.8}],
        "X5": [{"at": K["pop"] + 0.25, "to": [-1.45, 7.75], "speed": 3.6}],   # shows on the handoff side
        "O1": [{"at": K["catch1"] + 0.3, "to": [4.55, 7.3], "speed": 2.6}],
        "X1": [{"at": K["catch1"] + 0.55, "to": [3.95, 6.75], "speed": 2.4}],
        # the sprint toward the big (sell the handoff), decelerating into the plant
        "O2": [{"at": K["sprint"], "via": [[-4.1, 6.35]], "to": HAND, "speed": 6.0}],
        # X2 trails on his back hip, then jumps over the top to the handoff side
        "X2": [{"at": K["sprint"] + 0.25, "via": [[-4.35, 6.2]], "to": OVER, "speed": 6.4}],
        "O3": [], "X3": [], "O4": [], "X4": [],
    }
    acts = {
        "O1": [{"type": "face", "from": 0, "to": K["catch1"] + 0.3, "face": "O5"}],
        "X1": [st("O1", 0, DB)],
        "O5": [{"type": "catchReady", "from": K["pop"] + 0.5, "to": K["catch1"], "face": "O1"},
               {"type": "face", "from": K["catch1"] + 0.1, "to": K["pass2"], "face": "O2"}],
        "X5": [st("O5", 0, DB)],
        # O2 sells: eyes, shoulders and hands to the big (the handoff target hand), then the plant and the open step
        "O2": [{"type": "face", "from": K["sprint"], "to": K["show"], "face": "O5"},
               {"type": "call", "from": K["show"], "to": K["plant"], "amt": 0.55},
               {"type": "roll", "from": K["plant"] + 0.02, "to": K["plant"] + 0.62, "face": "O5", "turn": 0.42}],
        # X2 reads the handoff: chest and weight to the big, too late to recover when O2 goes back door
        "X2": [st("O2", 0, K["show"]), {"type": "topLock", "from": K["show"], "to": K["x2turn"] + 0.1, "face": "O5", "side": 1}],
        "X4": [st("O4", 0, DB)],
        "X3": [st("ball", 0, DB)],
        "O3": [], "O4": [],
    }
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": K["pass1"]},
            {"type": "pass", "from": "O1", "to": "O5", "t0": K["pass1"], "t1": K["catch1"], "style": "chest", "eyes": 0.3}]
    return legs, acts, ball


def zero(kind):
    legs, acts, ball = common()
    # X2: human latency, then chases on the cutter's back
    legs["X2"].append({"at": K["x2turn"], "via": [[-2.75, 6.6]], "to": [-2.15, 4.9], "speed": 5.2})
    acts["X2"].append(st("O2", K["x2turn"] + 0.15, DB))
    if kind == "layup":
        legs["O2"].append({"at": K["cut"], "via": [[-2.5, 5.9], [-1.75, 4.3], CATCH], "to": LAY, "speed": K["cutSpeed"]})
        legs["X3"] = [{"at": K["help"] + 0.15, "to": [2.75, 2.65], "speed": 1.6}]           # a look at the cutter, stays home
        acts["O2"].append({"type": "catchReady", "from": K["catch2"] - 0.35, "to": K["catch2"], "face": "O5"})
        acts["O2"].append({"type": "celebrate", "from": K["lay"] + 0.9, "to": DA - 0.1})
        ball += [{"type": "hold", "player": "O5", "from": K["catch1"], "to": K["pass2"]},
                 {"type": "pass", "from": "O5", "to": "O2", "t0": K["pass2"], "t1": K["catch2"], "style": "bounce", "eyes": 0.4, "lead": True},
                 {"type": "hold", "player": "O2", "from": K["catch2"], "to": K["lay"]},
                 {"type": "layup", "player": "O2", "t0": K["lay"], "t1": K["lay"] + 0.42, "make": True}]
        marks = {"start": 0, "pop": K["pop"], "entry": K["pass1"], "bigCatch": K["catch1"], "sprint": K["sprint"],
                 "show": K["show"], "plant": K["plant"], "cut": K["cut"], "x2turn": K["x2turn"], "pass": K["pass2"],
                 "catch": K["catch2"], "finish": K["lay"], "make": K["lay"] + 0.42, "end": DA}
        claims = [
            {"type": "reacts_after", "player": "O2", "event": "entry", "min": 0.2, "says": "The big catches up top. The guard sprints toward him"},
            {"type": "reacts_after", "player": "X2", "event": "sprint", "min": 0.2, "says": "and his defender follows"},
            {"type": "near", "a": "O2", "b": "O5", "at": "plant", "max": 1.9, "says": "selling a handoff (handoff distance)"},
            {"type": "order", "marks": ["cut", "x2turn"], "says": "The cutter slips behind him (X2 turns 0.3 s after the cut starts)"},
            {"type": "far", "a": "X2", "b": "O2", "at": "catch", "min": 1.5, "says": "behind him: X2 is beaten on the catch"},
            {"type": "far", "a": "X3", "b": "O2", "at": "catch", "min": 2.4, "says": "the low help stays home (read A)"},
            {"type": "near_rim", "player": "O2", "at": "finish", "max": 1.6, "says": "takes the pass, and finishes"},
            {"type": "order", "marks": ["pop", "entry", "bigCatch", "show", "plant", "cut", "x2turn", "pass", "catch", "finish", "make"],
             "says": "sell the handoff, cut behind, pass, finish"}]
        return {"id": "zerocut-a-layup", "title": "Zero Cut A: fake handoff, X2 jumps over the top, back cut, bounce pass, layup",
                "duration": DA, "concept": "zero-cut", "source": SRC, "squareUp": True, "catchV2": 2, "handBallClear": True, "v33": "compile", "realism": 3,
                "players": PLAYERS, "start": START, "legs": legs, "ball": ball, "marks": marks, "actions": acts,
                "claims": claims, "screens": [],
                "notes": ["No screen: X2 is beaten by his own anticipation of the handoff.",
                          "O2 plants only when X2 has committed to the top side; X2 turns 0.3 s after the cut starts.",
                          "X3 (low help) takes a look and stays with O3: nobody rotates, the layup is there."]}
    # B: the low help steps across -> the big skips to the corner he left
    legs["O2"].append({"at": K["cut"], "via": [[-2.5, 5.9], [-1.75, 4.3]], "to": [-1.1, 2.75], "speed": K["cutSpeed"]})
    legs["X3"] = [{"at": K["help"], "via": [[1.6, 2.75]], "to": HELP, "speed": 6.6},
                  {"at": K["kick"] + 0.2, "via": [[2.6, 2.4]], "to": CLOSE, "speed": 6.4}]
    if K.get("measure"):
        legs["X3"] = legs["X3"][:1]
    acts["X3"] = [st("ball", 0, K["help"]), st("O2", K["help"] + 0.2, K["kick"] + 0.15),
                  {"type": "closeout", "from": K["kick"] + 0.3, "to": K["rel"] + 0.1}, {"type": "contest", "from": K["rel"], "to": K["rel"] + 0.5}]
    acts["O5"][-1] = {"type": "face", "from": K["catch1"] + 0.1, "to": K["kick"] - 0.3, "face": "O2"}
    acts["O3"] = [{"type": "catchReady", "from": K["kick"] + 0.05, "to": K["catch3"] + 0.05}]
    ball += [{"type": "hold", "player": "O5", "from": K["catch1"], "to": K["kick"]},
             {"type": "pass", "from": "O5", "to": "O3", "t0": K["kick"], "t1": K["catch3"], "style": "overhead", "eyes": 0.35},
             {"type": "hold", "player": "O3", "from": K["catch3"], "to": K["rel"]},
             {"type": "shot", "player": "O3", "t0": K["rel"], "t1": K["rel"] + 1.05, "make": True, "three": True}]
    acts["O3"].append({"type": "celebrate", "from": K["rel"] + 1.2, "to": DB - 0.1})
    marks = {"start": 0, "pop": K["pop"], "entry": K["pass1"], "bigCatch": K["catch1"], "sprint": K["sprint"], "show": K["show"],
             "plant": K["plant"], "cut": K["cut"], "x2turn": K["x2turn"], "help": K["help"], "kick": K["kick"], "catch": K["catch3"],
             "release": K["rel"], "make": K["rel"] + 1.05, "end": DB}
    claims = [
        {"type": "reacts_after", "player": "X3", "event": "cut", "min": 0.25, "says": "If that help steps across (after the cut)"},
        {"type": "near_rim", "player": "X3", "at": "kick", "max": 2.2, "says": "the help steps across to protect the rim"},
        {"type": "reacts_after", "player": "X3", "event": "kick", "min": 0.15, "says": "late closeout after the kick"},
        {"type": "behind_arc", "player": "O3", "at": "catch", "says": "the corner is open"},
        {"type": "open", "player": "O3", "at": "release", "min": 1.8, "says": "the corner is open"},
        {"type": "order", "marks": ["plant", "cut", "help", "kick", "catch", "release", "make"], "says": "Don't force the layup, kick it out"}]
    return {"id": "zerocut-b-kick", "title": "Zero Cut B: the low help steps across, O5 skips to the weak-side corner",
            "duration": DB, "concept": "zero-cut", "source": SRC, "squareUp": True, "catchV2": 2, "handBallClear": True, "v33": "compile", "realism": 3,
            "players": PLAYERS, "start": START, "legs": legs, "ball": ball, "marks": marks, "actions": acts,
            "claims": claims, "screens": [],
            "notes": ["Same start and same sell as zerocut-a-layup.",
                      "X3 leaves O3 0.3 s after the cut starts and steps across in front of the rim.",
                      "O5 does not force the bounce pass: overhead skip to O3, late closeout, three."]}


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
    tr = build(zero("layup"))["tracks"]
    K["catch1"] = round((first_near(tr["O5"], TOP, 0.05) or K["catch1"]) + 0.03, 3)
    K["pass1"] = round(K["catch1"] - 0.5, 3)
    K["sprint"] = round(K["catch1"] - 0.15, 3)          # O2 leaves as the ball arrives up top
    tr = build(zero("layup"))["tracks"]
    arr = first_near(tr["O2"], HAND, 0.03, K["sprint"])
    K["show"] = round(arr - 0.5, 3)                      # hands shown the last strides before the plant
    K["plant"] = arr
    xo = first_near(tr["X2"], OVER, 0.25, K["sprint"])   # X2 committed over the top
    K["cut"] = round(max(arr + 0.12, (xo or arr) + 0.02), 3)
    K["x2turn"] = round(K["cut"] + 0.3, 3)
    K["help"] = round(K["cut"] + 0.3, 3)
    tr = build(zero("layup"))["tracks"]
    c2 = first_near(tr["O2"], CATCH, 0.05, K["cut"])
    K["catch2"] = c2
    K["pass2"] = round(c2 - 0.45, 3)
    tr = build(zero("layup"))["tracks"]
    K["lay"] = round(first_near(tr["O2"], LAY, 0.12, c2) or c2 + 0.2, 3)
    K["measure"] = True
    trb = build(zero("kick"))["tracks"]
    K["measure"] = False
    he = first_near(trb["X3"], HELP, 0.6, K["help"])
    hend = first_near(trb["X3"], HELP, 0.02, K["help"])
    K["kick"] = round(max(he or K["help"] + 0.5, K["cut"] + 0.75, (hend or 0) + 0.05), 3)
    K["catch3"] = round(K["kick"] + 0.78, 3)
    K["rel"] = round(K["catch3"] + 0.32, 3)
    for s in (zero("layup"), zero("kick")):
        build(s)
        print("built", s["id"], json.dumps(s["marks"]))
