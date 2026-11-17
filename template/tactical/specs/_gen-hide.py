#!/usr/bin/env python3
"""HIDE IN GAMES (owner brief 2026-11-17 17:09Z). Original E2A character episode: #8 calls for the ball all
practice and hides in games. Court: x across, y from the baseline, basket (0, 1.575), metres.
  O1 passer on the right wing (x < 0 is screen-right with the basket at the top), O8 the protagonist on the left wing.
Plays (all share the same O1 / O8 staging so the cuts match):
  hide-pilot-practice  warm gym, no defenders: #8 eyes on the passer, hands open, calls for it
  hide-pilot-game      same first 3 s; X8 steps into the lane, #8 drops his hands and gives half a step;
                       at 6 s he plants, slides to the open line, shows his hands and catches
Expressions (play.expr) are keyed in play time: brow -1 worried .. +1 determined, smile, open (calling), blink, look."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T_ = os.path.dirname(os.path.dirname(D))
SRC = "original E2A character episode (generic coaching knowledge; only the reference's practice/game contrast structure is reused)"
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}

O1 = [3.3, 7.7]          # passer
O8 = [-4.0, 5.7]         # #8 on the wing
O8_BACK = [-4.3, 5.9]    # half step back (away from the ball)
O8_OPEN = [-4.35, 4.05]  # slides down to the open line
X8_LANE = [-3.0, 5.98]   # defender in the passing lane, 1 m off #8
X8_START = [-0.7, 7.3]
X1 = [2.75, 8.45]


def practice():
    return {"id": "hide-pilot-practice", "title": "Hide in games pilot: practice", "duration": 9.0, "source": SRC,
            "players": [P("O1", "O", "Passer"), P("O8", "O", "#8, the protagonist")],
            "start": {"O1": O1, "O8": O8}, "legs": {},
            "ball": [{"type": "hold", "player": "O1", "from": 0, "to": 9.0, "dribble": True}],
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": 9.0, "face": "O8"}],
                        "O8": [{"type": "call", "from": 0.35, "to": 9.0, "face": "O1"}]},
            "expr": {"O8": [{"t": 0, "brow": 0.55, "smile": 0.35, "open": 0.0, "look": "O1"}, {"t": 0.45, "open": 0.65}, {"t": 1.3, "open": 0.15},
                            {"t": 1.9, "open": 0.6}, {"t": 2.6, "open": 0.2}]},
            "marks": {"call": 0.35}}


def game():
    legs = {"O8": [{"at": 3.55, "to": O8_BACK, "dur": 0.55},
                   {"at": 6.05, "to": O8_OPEN, "dur": 0.85}],
            "X8": [{"at": 2.75, "via": [[-1.6, 6.85]], "to": X8_LANE, "dur": 0.85},
                   {"at": 7.55, "to": [-3.55, 5.2], "dur": 0.6}]}
    p0, p1 = 7.45, 8.1
    return {"id": "hide-pilot-game", "title": "Hide in games pilot: game", "duration": 9.0, "source": SRC,
            "players": [P("O1", "O", "Passer"), P("O8", "O", "#8, the protagonist"),
                        P("X1", "X", "On the ball", "O1"), P("X8", "X", "Steps into the lane", "O8")],
            "start": {"O1": O1, "O8": O8, "X1": X1, "X8": X8_START}, "legs": legs,
            "ball": [{"type": "hold", "player": "O1", "from": 0, "to": p0 - 0.2, "dribble": True},
                     {"type": "hold", "player": "O1", "from": p0 - 0.2, "to": p0},
                     {"type": "pass", "from": "O1", "to": "O8", "t0": p0, "t1": p1, "style": "chest"},
                     {"type": "hold", "player": "O8", "from": p1, "to": 9.0}],
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": p0 - 0.2, "face": "O8"}, {"type": "pass", "from": p0 - 0.25, "to": p0 + 0.15, "face": "O8"}],
                        "X1": [{"type": "stance", "from": 0, "to": 9.0, "face": "O1"}],
                        "X8": [{"type": "topLock", "from": 3.3, "to": 7.6, "face": "O8", "side": 1}],
                        "O8": [{"type": "call", "from": 0.35, "to": 3.3, "face": "O1"},
                               {"type": "hide", "from": 3.45, "to": 5.95, "face": "O1"},
                               {"type": "catchReady", "from": 6.85, "to": p1, "face": "O1"},
                               {"type": "call", "from": 6.85, "to": p1 - 0.25, "face": "O1"}]},
            "expr": {"O8": [{"t": 0, "brow": 0.55, "smile": 0.35, "open": 0.0, "look": "O1"}, {"t": 0.45, "open": 0.65}, {"t": 1.3, "open": 0.15},
                            {"t": 1.9, "open": 0.6}, {"t": 2.6, "open": 0.2},
                            {"t": 3.25, "brow": 0.55, "smile": 0.35, "open": 0.1},
                            {"t": 3.6, "brow": -0.8, "smile": 0.0, "open": 0.0, "look": "ball"},
                            {"t": 5.9, "brow": -0.8},
                            {"t": 6.2, "brow": 0.75, "look": "O1"},
                            {"t": 6.9, "open": 0.0}, {"t": 7.1, "open": 0.6}, {"t": 7.5, "open": 0.1},
                            {"t": 8.2, "smile": 0.0}, {"t": 8.6, "smile": 0.4}],
                     "X8": [{"t": 0, "brow": 0.6, "look": "O8"}],
                     "X1": [{"t": 0, "brow": 0.4, "look": "O1"}],
                     "O1": [{"t": 0, "brow": 0.2, "look": "O8"}]},
            "marks": {"call": 0.35, "cut": 3.0, "deny": 3.6, "drop": 3.6, "back": 4.1, "plant": 6.05, "open": 6.9, "show": 6.9, "pass": p0, "catch": p1},
            "claims": [{"type": "near", "a": "X8", "b": "O8", "at": "deny", "max": 2.8, "says": "The defender steps into the lane."},
                       {"type": "open", "player": "O8", "at": "catch", "min": 1.2, "says": "He slides to the open line and catches."}]}


def shift_expr(ex, dt):
    return {k: [{**e, "t": round(e["t"] + dt, 3)} for e in v] for k, v in ex.items()}


def reel_practice():
    """practice for the Reel: #8 jogs into his spot first (the closing shot ends on this run-in, the hook starts
    as his hands come up: the loop joins); then the same call as the pilot, 1.25 s later."""
    s = practice()
    s["id"], s["title"], s["duration"] = "hide-practice", "Hide in games: practice (run-in + call)", 10.5
    s["start"] = {"O1": O1, "O8": [-4.9, 4.2]}
    s["legs"] = {"O8": [{"at": 0.0, "to": O8, "dur": 1.2}]}
    s["ball"] = [{"type": "hold", "player": "O1", "from": 0, "to": 10.5, "dribble": True}]
    s["actions"] = {"O1": [{"type": "dribble", "from": 0, "to": 10.5, "face": "O8"}],
                    "O8": [{"type": "call", "from": 1.6, "to": 10.5, "face": "O1"}]}
    s["expr"] = shift_expr(s["expr"], 1.25)
    s["expr"]["O8"][0]["t"] = 0
    s["marks"] = {"run": 0, "call": 1.6}
    return s


O3 = [5.2, 4.6]
X3 = [4.55, 3.7]


def poss():
    """the possession goes the other way: #8 hidden behind X8, O1 swings it to O3"""
    p0, p1 = 2.3, 2.85
    return {"id": "hide-poss", "title": "Hide in games: the ball goes the other way", "duration": 6.0, "source": SRC,
            "players": [P("O1", "O", "Passer"), P("O8", "O", "#8, hidden"), P("O3", "O", "Other wing"),
                        P("X1", "X", "On the ball", "O1"), P("X8", "X", "In the lane", "O8"), P("X3", "X", "Other wing", "O3")],
            "start": {"O1": O1, "O8": O8_BACK, "O3": O3, "X1": X1, "X8": X8_LANE, "X3": X3},
            "legs": {"O3": [{"at": p1 + 0.2, "to": [5.4, 5.6], "dur": 1.0}], "X3": [{"at": p1, "to": [4.6, 3.4], "dur": 0.9}],
                     "X8": [{"at": p1 + 0.3, "to": [-2.6, 5.4], "dur": 1.0}]},
            "ball": [{"type": "hold", "player": "O1", "from": 0, "to": p0 - 0.2, "dribble": True},
                     {"type": "hold", "player": "O1", "from": p0 - 0.2, "to": p0},
                     {"type": "pass", "from": "O1", "to": "O3", "t0": p0, "t1": p1, "style": "chest"},
                     {"type": "hold", "player": "O3", "from": p1, "to": 6.0, "dribble": True}],
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": p0 - 0.2, "face": "O8"}, {"type": "pass", "from": p0 - 0.25, "to": p0 + 0.15, "face": "O3"}],
                        "O3": [{"type": "catchReady", "from": 1.4, "to": p1, "face": "O1"}],
                        "X1": [{"type": "stance", "from": 0, "to": 6.0, "face": "O1"}],
                        "X3": [{"type": "stance", "from": 0, "to": 6.0, "face": "O3"}],
                        "X8": [{"type": "topLock", "from": 0, "to": 6.0, "face": "O8", "side": 1}],
                        "O8": [{"type": "hide", "from": 0, "to": 6.0, "face": "O1"}]},
            "expr": {"O8": [{"t": 0, "brow": -0.8, "look": "ball"}], "X8": [{"t": 0, "brow": 0.6, "look": "O8"}],
                     "O1": [{"t": 0, "brow": -0.2, "look": "O8"}, {"t": 1.8, "brow": 0.2, "look": "O3"}],
                     "X1": [{"t": 0, "brow": 0.4, "look": "O1"}], "O3": [{"t": 0, "brow": 0.3, "smile": 0.2}], "X3": [{"t": 0, "brow": 0.3}]},
            "marks": {"look": 1.2, "pass": p0, "catch": p1}}


SHOT = [-6.25, 4.35]


def miss():
    """#8's open shot hits the back of the ring and kicks out; exhale, tap the jersey, run back"""
    t0, t1 = 0.45, 1.6
    return {"id": "hide-miss", "title": "Hide in games: the miss and the reset", "duration": 7.8, "source": SRC,
            "players": [P("O8", "O", "#8 shoots"), P("X8", "X", "Late closeout", "O8")],
            "start": {"O8": SHOT, "X8": [-2.7, 5.9]},
            "legs": {"X8": [{"at": 0.0, "to": [-4.6, 5.95], "dur": 0.75}, {"at": 1.75, "to": [-1.9, 3.2], "dur": 1.1}],
                     "O8": [{"at": 4.95, "via": [[-5.6, 6.3]], "to": [-4.4, 9.8], "speed": 4.4}]},
            "ball": [{"type": "hold", "player": "O8", "from": 0, "to": t0},
                     {"type": "shot", "player": "O8", "t0": t0, "t1": t1, "make": False, "side": -1}],
            "actions": {"O8": [{"type": "shoot", "from": t0 - 0.3, "to": t0 + 0.75, "face": 0.25},
                               {"type": "exhale", "from": 2.15, "to": 3.6, "face": 0.25},
                               {"type": "tap", "from": 3.65, "to": 4.75, "face": 0.25}],
                        "X8": [{"type": "contest", "from": 0.35, "to": 1.2, "face": "O8"}]},
            "expr": {"O8": [{"t": 0, "brow": 0.4, "smile": 0, "look": "ball"}, {"t": 1.65, "brow": 0.4}, {"t": 1.9, "brow": -0.75},
                            {"t": 2.15, "blink": 0}, {"t": 2.45, "blink": 1}, {"t": 3.25, "blink": 1}, {"t": 3.5, "blink": 0, "brow": -0.2},
                            {"t": 4.3, "brow": 0.6, "smile": 0.15}],
                     "X8": [{"t": 0, "brow": 0.6, "look": "O8"}, {"t": 1.7, "look": "ball"}]},
            "marks": {"release": t0, "rim": t1, "exhale": 2.15, "tap": 3.65, "back": 4.95}}


def offers():
    """offers 1 and 2: #8 gets into a lane and shows his hands; the ball still goes elsewhere (the count is the offer)"""
    O8A = [-3.55, 7.55]
    O8B = [-6.2, 2.7]
    return {"id": "hide-offers", "title": "Hide in games: offers 1 and 2", "duration": 5.8, "source": SRC,
            "players": [P("O1", "O", "Passer"), P("O8", "O", "#8 offers"), P("O3", "O", "Other wing"),
                        P("X1", "X", "On the ball", "O1"), P("X8", "X", "On #8", "O8"), P("X3", "X", "Other wing", "O3")],
            "start": {"O1": O1, "O8": O8, "O3": O3, "X1": X1, "X8": [-3.1, 5.6], "X3": X3},
            "legs": {"O8": [{"at": 0.35, "to": O8A, "dur": 0.8}, {"at": 2.35, "via": [[-5.0, 5.0]], "to": O8B, "speed": 4.2}],
                     "X8": [{"at": 0.6, "to": [-2.85, 7.0], "dur": 0.8}, {"at": 2.65, "via": [[-4.0, 5.2]], "to": [-5.3, 3.4], "speed": 4.0}]},
            "ball": [{"type": "hold", "player": "O1", "from": 0, "to": 1.55, "dribble": True},
                     {"type": "hold", "player": "O1", "from": 1.55, "to": 1.75},
                     {"type": "pass", "from": "O1", "to": "O3", "t0": 1.75, "t1": 2.3, "style": "chest"},
                     {"type": "hold", "player": "O3", "from": 2.3, "to": 4.1},
                     {"type": "pass", "from": "O3", "to": "O1", "t0": 4.1, "t1": 4.65, "style": "chest"},
                     {"type": "hold", "player": "O1", "from": 4.65, "to": 5.8, "dribble": True}],
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": 1.55, "face": "O8"}, {"type": "pass", "from": 1.5, "to": 1.9, "face": "O3"},
                               {"type": "catchReady", "from": 3.9, "to": 4.65, "face": "O3"}],
                        "O3": [{"type": "catchReady", "from": 1.3, "to": 2.3, "face": "O1"}, {"type": "pass", "from": 3.85, "to": 4.25, "face": "O1"}],
                        "X1": [{"type": "stance", "from": 0, "to": 5.8, "face": "O1"}],
                        "X3": [{"type": "stance", "from": 0, "to": 5.8, "face": "O3"}],
                        "X8": [{"type": "stance", "from": 0, "to": 5.8, "face": "O8"}],
                        "O8": [{"type": "call", "from": 1.05, "to": 1.95, "face": "O1"}, {"type": "call", "from": 3.45, "to": 4.3, "face": "O3"}]},
            "expr": {"O8": [{"t": 0, "brow": 0.6, "look": "O1"}, {"t": 1.05, "open": 0}, {"t": 1.25, "open": 0.6}, {"t": 1.6, "open": 0.1},
                            {"t": 2.4, "look": "O3"}, {"t": 3.45, "open": 0}, {"t": 3.65, "open": 0.6}, {"t": 4.0, "open": 0.1}],
                     "X8": [{"t": 0, "brow": 0.5, "look": "O8"}], "O1": [{"t": 0, "look": "O8"}, {"t": 1.4, "look": "O3"}],
                     "X1": [{"t": 0, "brow": 0.4, "look": "O1"}], "O3": [{"t": 0, "brow": 0.3}], "X3": [{"t": 0, "brow": 0.3}]},
            "marks": {"offer1": 1.15, "pass1": 1.75, "cut": 2.35, "offer2": 3.55, "pass2": 4.1}}


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T_, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T_, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


if __name__ == "__main__":
    for s in (practice(), game(), reel_practice(), poss(), miss(), offers()):
        p = build(s)
        print("built", p["id"], p["duration"])
