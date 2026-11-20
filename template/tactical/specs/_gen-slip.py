#!/usr/bin/env python3
"""SLIP vs HARD HEDGE (2026-11-20, master prompt 3D/edit "next reel"): one ball screen, two reads of the SAME start.
Catalog concept `slip-vs-hedge` (config/tactical_concepts.v4.json, never produced before).

  A (main action): X5, the screener's defender, jumps out to hedge BEFORE the screen lands. The paint behind him is
    empty, so O5 never makes contact: he plants his outside foot, opens to the rim and dives. O1 picks up the dribble
    and throws OVER the top (loaded overhead pass); O5 catches in stride (catchV2) and finishes; X3, the weak-side low
    man, rotates late (his stimulus is the release of the pass).
  B (logical counter): X5 WAITS (drop, below the screen). There is no gap behind him, so O5 sets a legal screen
    (stationary, FIBA art. 33.7), X1 runs into it, O1 comes off it, brakes on two feet in front of the drop and pulls up.

Court (repo units, src/tactical/geometry.ts): metres on a FIBA half court, x across (-7.5..7.5), y from the baseline,
basket (0, 1.575), 3-pt line 6.75 m. Camera convention of the house: yaw 0 = from half court, x > 0 = LEFT of the
screen. The ball is on the left slot (x > 0): the weak side is x < 0 (X3 = low man).

Causal timing (no precognition; every defender moves after a stimulus he can SEE, with a human latency):
  O5 starts up to screen at K.up; X5 reads it +0.25 s (A: sprints out to the hedge spot; B: steps to the drop spot);
  A: O5 plants only once X5 is already above the screen line (X5 arrives first: "before the screen lands");
     O1 picks up the dribble when X5 arrives in front of him, loads, releases over the top; X3 starts +0.2 s after
     the release; X1 never meets a screen (no contact in A).
  B: O5 is stationary 0.1 s before X1 reaches him (legal screen); X1's bump +0.05 s after contact; O1 leaves on the
     contact; X5 retreats while O1 comes off (he is guarding the roll), X1 chases over the top, late.
  python3 tactical/specs/_gen-slip.py   (writes tactical/specs/slip-{a-dive,b-pullup}.spec.json + plays)"""
import json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = ("original E2A staging of the slip-vs-hard-hedge ball-screen counter (Hooper University 'Ball Screen Offense - "
       "Beating The Hard Hedge'; Breakthrough Basketball '3 Offensive Counters For The Hard Hedge'; FIBA 2026 art. 33.7 "
       "screening, art. 25 travelling); production coordinates")

PLAYERS = [P("O1", "O", "Ball handler, left slot"),
           P("O2", "O", "Right wing, spacing"),
           P("O3", "O", "Right corner, spacing"),
           P("O4", "O", "Left corner, spacing"),
           P("O5", "O", "The screener: slips (A) / sets the screen (B)"),
           P("X1", "X", "On the ball", "O1"),
           P("X2", "X", "On the right wing", "O2"),
           P("X3", "X", "Weak-side low man: late rotation in A", "O3"),
           P("X4", "X", "Left corner, stays home", "O4"),
           P("X5", "X", "The screener's defender: shows early (A) / waits in the drop (B) = THE READ", "O5")]

START = {"O1": [2.45, 9.05], "X1": [2.3, 8.05],
         "O5": [0.65, 5.55], "X5": [0.15, 5.15],
         "O2": [-4.9, 6.7], "X2": [-4.05, 6.05],
         "O3": [-6.6, 1.35], "X3": [-4.45, 2.45],
         "O4": [6.6, 1.35], "X4": [5.25, 2.25]}

APPROACH = [1.3, 7.9]      # A: where O5 is when he sees X5 already out (0.8 m short of X1: no contact)
SCREEN = [1.5, 8.15]       # B: the screen spot on X1's middle hip
HEDGE = [1.7, 9.3]          # A: X5 above the screen line, in front of O1's turn
DROP = [0.85, 6.55]        # B: X5 waits below the screen
DROP2 = [0.55, 4.6]        # B: X5 retreats to protect the rim / roll
CATCH5 = [0.45, 4.45]      # A: in-stride catch spot (lead pass)
LAY5 = [0.2, 2.85]         # A: layup spot (1.27 m from the basket)
PULL = [-0.45, 6.45]       # B: pull-up spot at the right elbow (4.9 m: a two)

K = {"x1top": 1.2, "up": 0.35, "x5go": 0.6, "plant": 2.3, "slip": 2.4, "pick": 2.0, "pass": 2.45, "catch": 2.93, "lay": 3.3,
     "slipSpeed": 6.0, "contact": 1.95, "use": 2.0, "gather": 3.05, "rel": 3.35}
DA, DB = 5.4, 5.6


def common(kind):
    legs = {
        "O5": [{"at": K["up"], "to": APPROACH if kind == "a" else SCREEN, "speed": 2.15 if kind == "a" else 2.7}],
        "O1": [], "X1": [], "O2": [], "X2": [], "O3": [], "O4": [], "X3": [], "X4": []}
    acts = {
        "X1": [st("O1", 0, 2.4)],
        "X2": [st("ball", 0, 6)], "X4": [st("ball", 0, 6)],
        "X3": [st("ball", 0, 6)],
        "O1": [{"type": "face", "from": 0, "to": 1.2, "face": "O5"}]}
    return legs, acts


def slip_a():
    legs, acts = common("a")
    # X5 reads O5's run up and SHOWS EARLY: past O5's middle side, above the screen line, before O5 gets there
    legs["X5"] = [{"at": K["x5go"], "via": [[0.45, 7.35]], "to": HEDGE, "speed": 6.4}]
    acts["X5"] = [st("O5", 0, K["x5go"] - 0.05), {"type": "blitz", "from": K["x5go"] + 0.75, "to": K["catch"] + 0.1, "face": "O1"}]
    # O5: plant the outside foot, open to the rim, dive behind the hedge; one leg so the catch is in stride
    legs["O5"].append({"at": K["slip"], "via": [[0.95, 6.35], CATCH5], "to": LAY5, "speed": K["slipSpeed"]})
    # O1: live dribble, retreat dribble to the sideline as the hedge arrives (opens the passing angle), picks up, loads
    legs["O1"] = [{"at": K["pick"] - 0.8, "to": [3.25, 9.05], "speed": 1.7}]
    # X1 hears the screen coming and jumps to the TOP side to go over it (the over-the-top lane stays clear of him)
    legs["X1"] = [{"at": K["x1top"], "via": [[2.0, 8.75]], "to": [2.7, 9.65], "speed": 2.6}]
    # X3: the low man rotates after the release (late tag), X4 stays with the corner
    legs["X3"] = [{"at": K["pass"] + 0.2, "to": [-1.25, 3.05], "speed": 5.2}]
    acts["X3"] = [st("ball", 0, K["pass"] + 0.15), {"type": "contest", "from": K["lay"] - 0.05, "to": K["lay"] + 0.5}]
    acts["X1"] = [st("O1", 0, K["pass"] + 0.3), {"type": "stance", "from": K["pass"] + 0.3, "to": DA, "face": "ball"}]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": K["pick"], "dribble": True},
            {"type": "hold", "player": "O1", "from": K["pick"], "to": K["pass"]},
            {"type": "pass", "from": "O1", "to": "O5", "t0": K["pass"], "t1": K["catch"], "style": "overhead", "eyes": 0.5, "lead": True},
            {"type": "hold", "player": "O5", "from": K["catch"], "to": K["lay"]},
            {"type": "layup", "player": "O5", "t0": K["lay"], "t1": K["lay"] + 0.4, "make": True}]
    acts["O1"].append({"type": "face", "from": K["pick"] - 0.4, "to": K["pass"] + 0.2, "face": "O5"})
    acts["O5"] = [{"type": "celebrate", "from": K["lay"] + 0.9, "to": DA - 0.1}]
    marks = {"start": 0, "up": K["up"], "show": K["x5go"], "hedged": K["hedged"], "plant": K["plant"], "slip": K["slip"],
             "pick": K["pick"], "pass": K["pass"], "catch": K["catch"], "finish": K["lay"], "make": K["lay"] + 0.4, "end": DA}
    claims = [
        {"type": "reacts_after", "player": "X5", "event": "up", "min": 0.2, "says": "He jumps out (after the screener starts up)"},
        {"type": "near", "a": "X5", "b": "O1", "at": "hedged", "max": 2.4, "says": "Before the screen even lands, he's already out."},
        {"type": "far", "a": "O5", "b": "X1", "at": "plant", "min": 0.55, "says": "So the screener slips (no contact with X1)"},
        {"type": "far", "a": "X5", "b": "O5", "at": "catch", "min": 3.0, "says": "and dive behind him"},
        {"type": "reacts_after", "player": "X3", "event": "pass", "min": 0.15, "says": "the low man is late"},
        {"type": "near_rim", "player": "O5", "at": "finish", "max": 1.5, "says": "Layup."},
        {"type": "order", "marks": ["up", "show", "hedged", "pick", "plant", "slip", "pass", "catch", "finish", "make"],
         "says": "show early, slip, over the top, layup"}]
    return {"id": "slip-a-dive", "title": "Slip vs hard hedge A: the big's defender shows early, the screener slips, layup",
            "duration": DA, "concept": "slip-vs-hedge", "source": SRC, "squareUp": True, "catchV2": 2, "players": PLAYERS,
            "start": START, "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims, "screens": [],
            "notes": ["O5 walks up to screen X1; X5 reads it and jumps out above the screen line BEFORE O5 arrives.",
                      "O5 never touches X1: plant, open up, dive into the empty paint behind X5.",
                      "O1 retreats half a step, picks up, loaded overhead pass over the hedge; catch in stride, layup.",
                      "X3 rotates only after the release: late."]}


def slip_b():
    legs, acts = common("b")
    # X5 WAITS: a drop step below the screen, then retreats while O1 comes off it
    legs["X5"] = [{"at": K["x5go"], "to": DROP, "speed": 2.4}, {"at": K["use"] + 0.25, "to": DROP2, "speed": 2.6}]
    acts["X5"] = [st("O5", 0, K["x5go"] - 0.05), st("O1", K["x5go"] + 0.2, DB)]
    # O5: legal screen (stationary) on X1's middle hip, then a short roll
    acts["O5"] = [{"type": "screen", "from": K["contact"] - 0.15, "to": K["use"] + 0.75, "face": "X1"}]
    legs["O5"].append({"at": K["use"] + 0.85, "to": [1.1, 5.5], "speed": 3.2})
    # X1 runs into it (bump), then chases over the top, late
    legs["X1"] = [{"at": K["use"] - 0.05, "to": [2.0, 8.4], "speed": 1.8},
                  {"at": K["use"] + 0.5, "via": [[1.9, 9.2]], "to": [0.6, 8.3], "speed": 3.2}]
    acts["X1"] = [st("O1", 0, K["use"]), {"type": "bump", "from": K["use"] + 0.05, "to": K["use"] + 0.4, "face": "O5"},
                  {"type": "contest", "from": K["rel"] - 0.05, "to": K["rel"] + 0.5}]
    # O1 comes off the screen over its top, brakes on two feet at the elbow, pull-up
    legs["O1"] = [{"at": K["use"], "via": [[1.45, 9.15], [0.25, 8.45], [-0.4, 7.4]], "to": PULL, "speed": 4.1}]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": K["gather"], "dribble": True},
            {"type": "hold", "player": "O1", "from": K["gather"], "to": K["rel"]},
            {"type": "shot", "player": "O1", "t0": K["rel"], "t1": K["rel"] + 0.95, "make": True, "three": False, "side": -1}]
    acts["O1"] += [{"type": "gather", "from": K["gather"] - 0.05, "to": K["gather"] + 0.28}, {"type": "celebrate", "from": K["rel"] + 1.3, "to": DB - 0.1}]
    marks = {"start": 0, "up": K["up"], "wait": K["x5go"], "contact": K["contact"], "use": K["use"], "bump": K["use"] + 0.3, "gather": K["gather"],
             "release": K["rel"], "make": K["rel"] + 0.95, "end": DB}
    claims = [
        {"type": "reacts_after", "player": "X5", "event": "up", "min": 0.2, "says": "But this time he waits."},
        {"type": "far", "a": "X5", "b": "O1", "at": "contact", "min": 2.4, "says": "he waits (no show)"},
        {"type": "near", "a": "O5", "b": "X1", "at": "bump", "max": 0.6, "says": "Now the screen is real."},
        {"type": "far", "a": "X5", "b": "O1", "at": "release", "min": 1.8, "says": "the big is back in the paint"},
        {"type": "open", "player": "O1", "at": "release", "min": 1.8, "says": "Space for the pull-up."},
        {"type": "order", "marks": ["up", "wait", "contact", "use", "gather", "release", "make"], "says": "wait, screen, pull-up"}]
    return {"id": "slip-b-pullup", "title": "Slip vs hard hedge B: the big's defender waits, the screen is set, pull-up",
            "duration": DB, "concept": "slip-vs-hedge", "source": SRC, "squareUp": True, "players": PLAYERS,
            "start": START, "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims, "screens": [],
            "notes": ["Same start as slip-a-dive until X5's first step (0.6 s).",
                      "X5 waits below the screen: no gap behind him, so O5 sets a legal, stationary screen on X1.",
                      "O1 comes off over the top, two-foot brake at the right elbow, pull-up two in front of the drop."]}


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
    K["hedged"] = 1.8
    # pass 1 (A): when is X5 out, when does O5 reach the approach spot -> plant after X5 is out
    tr = build(slip_a())["tracks"]
    K["hedged"] = first_near(tr["X5"], HEDGE, 0.06) or 1.8
    arr5 = first_near(tr["O5"], APPROACH, 0.03) or 1.9
    K["plant"] = round(max(arr5, K["hedged"] + 0.1), 3)
    K["slip"] = round(K["plant"] + 0.1, 3)
    K["pick"] = round(K["hedged"] + 0.05, 3)            # the hedge is in front of him: pick up, load
    K["pass"] = round(max(K["pick"] + 0.42, K["slip"] + 0.38), 3)
    K["catch"] = round(K["pass"] + 0.58, 3)
    best = None
    for k in range(0, 40):
        K["slipSpeed"] = round(7.6 - 0.06 * k, 3)
        tr = build(slip_a())["tracks"]
        c = first_near(tr["O5"], CATCH5, 0.04, K["slip"])
        if c is not None and (best is None or abs(c - K["catch"]) < best[0]):
            best = (abs(c - K["catch"]), K["slipSpeed"], c)
    K["slipSpeed"], K["catch"] = best[1], best[2]
    K["pass"] = round(K["catch"] - 0.58, 3)
    tr = build(slip_a())["tracks"]
    K["lay"] = round(first_near(tr["O5"], LAY5, 0.15, K["catch"]) or K["catch"] + 0.35, 3)
    # B: screen contact = when X1 would meet O5 (O5 stationary first), O1 uses it on contact
    trb = build(slip_b())["tracks"]
    arrS = first_near(trb["O5"], SCREEN, 0.03) or 1.8
    K["contact"] = round(arrS + 0.15, 3)
    K["use"] = round(K["contact"] + 0.05, 3)
    trb = build(slip_b())["tracks"]
    K["gather"] = round((first_near(trb["O1"], PULL, 0.25, K["use"]) or K["use"] + 1.0), 3)
    K["rel"] = round(K["gather"] + 0.42, 3)
    for s in (slip_a(), slip_b()):
        build(s)
        print("built", s["id"], json.dumps(s["marks"]))
    print("K", json.dumps(K))
