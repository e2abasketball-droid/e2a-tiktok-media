#!/usr/bin/env python3
"""HIDE IN GAMES V2 (owner brief 2026-11-17 19:28Z): one missed shot and the next two possessions.
Court: x across, y from the baseline, basket (0, 1.575), metres. Same staging as V1 (_gen-hide.py).
  h2-practice  warm gym: O1 -> O8 on the open line, #8 catches, squares and rises (made, never seen landing)
  h2-miss      game, SAME timing as practice: catch, rise, the open shot hits the back of the ring and kicks out;
               #8 holds the follow-through, his eyes follow the ball, he lands and his shoulders fall; X8 takes
               the rebound and the game goes on
  h2-hide      possession 2 (ball already up): #8 behind X8, half a hand comes up and goes back, O3 pops into a
               lane, O1 passes to O3
  h2-ask       possession 3, SAME start as h2-hide: a pause (exhale, short jersey tap, eyes back on the passer),
               then plant, slide to the open line, the lane opens, hands up, two-hand catch at the chest,
               square up and shoot while X8 recovers late"""
import json, os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__))
T_ = os.path.dirname(os.path.dirname(D))
SRC = "original E2A character episode V2 (generic coaching knowledge)"
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}

O1 = [3.3, 7.7]
X1 = [2.75, 8.45]
O3 = [5.2, 4.6]
X3 = [4.55, 3.7]
# possessions 2 and 3 (V2): O3 at the top so the passer framing holds #8, X8, O1 and O3; X1 on the basket side of O1
O3T = [0.6, 10.3]
X3T = [0.7, 9.4]
X1T = [2.7, 6.5]
O8_BACK = [-4.3, 5.9]
X8_LANE = [-3.0, 5.98]
O8_OPEN = [-4.35, 4.05]
REB = json.load(open(os.path.join(D, "h2-rebound.json"))) if os.path.exists(os.path.join(D, "h2-rebound.json")) else [-2.4, 0.6]

# shared shot timing (practice == game for the match cut)
PASS0, CATCH, SHOT0, SHOT1 = 0.85, 1.5, 2.5, 3.65


def shot_core(make):
    return [{"type": "hold", "player": "O1", "from": 0, "to": PASS0 - 0.2, "dribble": True},
            {"type": "hold", "player": "O1", "from": PASS0 - 0.2, "to": PASS0},
            {"type": "pass", "from": "O1", "to": "O8", "t0": PASS0, "t1": CATCH, "style": "chest"},
            {"type": "hold", "player": "O8", "from": CATCH, "to": SHOT0},
            {"type": "shot", "player": "O8", "t0": SHOT0, "t1": SHOT1, **({} if make else {"make": False, "side": 1})}]


O8_SHOT_ACTS = [{"type": "catchReady", "from": CATCH - 0.5, "to": CATCH + 0.05, "face": "O1"},
                {"type": "gather", "from": CATCH, "to": SHOT0 - 0.45, "face": 0.3}]


LEAD = 1.6


def shift(ev, dt):
    out = []
    for e in ev:
        e = dict(e)
        for k in ("from", "to", "t0", "t1", "t", "at"):
            if k in e and isinstance(e[k], (int, float)) and not (k == "from" and e[k] == 0 and e.get("type") in ("hold", "dribble")):
                e[k] = round(e[k] + dt, 3)
        out.append(e)
    return out


def practice():
    s = practice0()
    s["duration"] = round(4.6 + LEAD, 2)
    s["ball"] = shift(s["ball"], LEAD)
    s["actions"] = {k: shift(v, LEAD) for k, v in s["actions"].items()}
    s["expr"] = {k: [{**e, "t": round(e["t"] + LEAD, 3) if e["t"] else 0} for e in v] for k, v in s["expr"].items()}
    s["marks"] = {k: round(v + LEAD, 3) for k, v in s["marks"].items()}
    return s


def practice0():
    return {"id": "h2-practice", "title": "Hide V2: practice shot", "duration": 4.6, "source": SRC,
            "players": [P("O1", "O", "Passer"), P("O8", "O", "#8")],
            "start": {"O1": O1, "O8": O8_OPEN}, "legs": {},
            "ball": shot_core(True),
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": PASS0 - 0.2, "face": "O8"}],
                        "O8": O8_SHOT_ACTS + [{"type": "shoot", "from": SHOT0 - 0.5, "to": SHOT0 + 0.9, "face": 0.3}]},
            "expr": {"O8": [{"t": 0, "brow": 0.55, "smile": 0.3, "look": "ball"}, {"t": CATCH, "smile": 0.1, "brow": 0.6}]},
            "marks": {"catch": CATCH, "rise": SHOT0 - 0.5, "release": SHOT0}}


def miss():
    t1 = SHOT1
    return {"id": "h2-miss", "title": "Hide V2: the open miss", "duration": 9.6, "source": SRC,
            "players": [P("O1", "O", "Passer"), P("O8", "O", "#8 shoots"), P("O3", "O", "Other wing"),
                        P("X1", "X", "On the ball", "O1"), P("X8", "X", "Late closeout, rebound", "O8"), P("X3", "X", "Other wing", "O3")],
            "start": {"O1": O1, "O8": O8_OPEN, "O3": O3, "X1": X1, "X8": [-1.8, 6.3], "X3": X3},
            "legs": {"X8": [{"at": CATCH - 0.15, "to": [-3.6, 4.85], "dur": 0.85}, {"at": t1 + 0.05, "to": REB, "speed": 3.6},
                            {"at": t1 + 2.1, "via": [[-1.0, 4.5]], "to": [0.6, 8.0], "speed": 3.6}],
                     "X3": [{"at": t1 - 0.2, "to": [2.2, 2.6], "dur": 0.9}, {"at": t1 + 1.9, "to": [3.5, 9.8], "speed": 3.8}],
                     "O3": [{"at": t1 - 0.1, "to": [3.0, 3.2], "dur": 0.9}, {"at": t1 + 2.0, "to": [4.6, 10.2], "speed": 3.6}],
                     "X1": [{"at": t1 + 2.1, "to": [1.6, 11.5], "speed": 3.5}],
                     "O1": [{"at": t1 + 1.4, "via": [[4.2, 9.2]], "to": [3.6, 11.4], "speed": 3.2}],
                     "O8": [{"at": t1 + 2.6, "via": [[-3.8, 6.0]], "to": [-2.6, 9.6], "speed": 3.2}]},
            "ball": shot_core(False) + [{"type": "hold", "player": "X8", "from": t1 + 1.4, "to": 9.6, "dribble": True}],
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": PASS0 - 0.2, "face": "O8"}],
                        "X1": [{"type": "stance", "from": 0, "to": t1 + 1.6, "face": "O1"}],
                        "X3": [{"type": "stance", "from": 0, "to": t1 - 0.3, "face": "O3"}],
                        "X8": [{"type": "contest", "from": SHOT0 - 0.15, "to": SHOT0 + 0.55, "face": "O8"}],
                        "O8": O8_SHOT_ACTS + [{"type": "shoot", "from": SHOT0 - 0.5, "to": t1 + 0.12, "face": 0.3},
                                              {"type": "exhale", "from": t1 + 0.3, "to": t1 + 2.3, "face": "ball"}]},
            "expr": {"O8": [{"t": 0, "brow": 0.55, "smile": 0.2, "look": "ball"}, {"t": CATCH, "smile": 0.0, "brow": 0.6},
                            {"t": t1, "brow": 0.6, "open": 0.0}, {"t": t1 + 0.18, "brow": -0.2, "open": 0.35},
                            {"t": t1 + 0.6, "brow": -0.85, "open": 0.1}, {"t": t1 + 1.1, "blink": 0}, {"t": t1 + 1.3, "blink": 1},
                            {"t": t1 + 1.7, "blink": 1}, {"t": t1 + 1.9, "blink": 0, "brow": -0.7}],
                     "X8": [{"t": 0, "brow": 0.6, "look": "O8"}, {"t": t1 - 0.1, "look": "ball"}],
                     "O1": [{"t": 0, "look": "O8"}, {"t": t1 - 0.2, "look": "ball"}],
                     "X1": [{"t": 0, "brow": 0.4, "look": "O1"}, {"t": t1, "look": "ball"}],
                     "O3": [{"t": 0, "look": "ball"}], "X3": [{"t": 0, "look": "ball"}]},
            "marks": {"catch": CATCH, "rise": SHOT0 - 0.5, "release": SHOT0, "land": SHOT0 + 0.3, "rim": t1, "reb": t1 + 1.55},
            "claims": [{"type": "open", "player": "O8", "at": "release", "min": 1.0, "says": "The shot is open."}]}


def hide():
    """possession 2: the ball is up; half a hand comes up (1.9-3.0) and goes back; O3 pops into a lane; O1 passes to O3"""
    p0, p1 = 5.2, 5.6
    return {"id": "h2-hide", "title": "Hide V2: possession 2, he hides", "duration": 8.4, "source": SRC,
            "players": [P("O1", "O", "Passer"), P("O8", "O", "#8, hidden"), P("O3", "O", "Offers the lane"),
                        P("X1", "X", "On the ball", "O1"), P("X8", "X", "In the lane", "O8"), P("X3", "X", "Other wing", "O3")],
            "start": {"O1": O1, "O8": O8_BACK, "O3": O3T, "X1": X1T, "X8": X8_LANE, "X3": X3T},
            "legs": {"O3": [{"at": 3.6, "to": [-0.9, 10.0], "dur": 0.9}], "X3": [{"at": 3.85, "to": [-0.7, 8.85], "dur": 0.9}],
                     "X8": [{"at": p1 + 0.3, "to": [-2.6, 5.4], "dur": 1.0}]},
            "ball": [{"type": "hold", "player": "O1", "from": 0, "to": p0 - 0.2, "dribble": True},
                     {"type": "hold", "player": "O1", "from": p0 - 0.2, "to": p0},
                     {"type": "pass", "from": "O1", "to": "O3", "t0": p0, "t1": p1, "style": "chest"},
                     {"type": "hold", "player": "O3", "from": p1, "to": 8.4, "dribble": True}],
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": p0 - 0.2, "face": "O8"}],
                        "O3": [{"type": "catchReady", "from": 4.4, "to": p1, "face": "O1"}],
                        "X1": [{"type": "stance", "from": 0, "to": 8.4, "face": "O1"}],
                        "X3": [{"type": "stance", "from": 0, "to": 8.4, "face": "O3"}],
                        "X8": [{"type": "stance", "from": 0, "to": 3.05, "face": "O8"}, {"type": "topLock", "from": 3.05, "to": 8.4, "face": "O8", "side": 1}],
                        "O8": [{"type": "hide", "from": 0, "to": 1.85, "face": "O1"},
                               {"type": "call", "from": 1.9, "to": 3.0, "face": "O1", "amt": 0.45},
                               {"type": "hide", "from": 2.95, "to": 8.4, "face": "O1"}]},
            "expr": {"O8": [{"t": 0, "brow": -0.6, "look": "ball"}, {"t": 1.7, "brow": -0.2, "look": "O1"}, {"t": 2.0, "open": 0.12},
                            {"t": 2.6, "brow": -0.3}, {"t": 2.9, "brow": -0.85, "open": 0.0, "look": "ball"}, {"t": 8.4, "brow": -0.85}],
                     "X8": [{"t": 0, "brow": 0.6, "look": "O8"}],
                     "O1": [{"t": 0, "brow": 0.0, "look": "O8"}, {"t": 4.0, "brow": 0.2, "look": "O3"}],
                     "X1": [{"t": 0, "brow": 0.4, "look": "O1"}], "O3": [{"t": 0, "brow": 0.3, "smile": 0.2}], "X3": [{"t": 0, "brow": 0.3}]},
            "marks": {"half": 1.9, "drop": 2.95, "pop": 3.6, "look": 4.0, "pass": p0, "catch": p1}}


def ask():
    """possession 3, same start as h2-hide: a pause (exhale 1.6, short tap 3.4, eyes on the passer 4.2), then plant,
    slide (the lane opens 6.6), hands up 7.35, pass 8.15, two-hand catch 8.8, square up, shoot 10.1"""
    go, opn, hands, p0, p1 = 5.9, 6.6, 7.35, 8.15, 8.8
    s0, s1 = 10.6, 11.75
    D_ = 12.2
    return {"id": "h2-ask", "title": "Hide V2: possession 3, he asks again", "duration": D_, "source": SRC,
            "players": [P("O1", "O", "Passer"), P("O8", "O", "#8 asks again"), P("O3", "O", "Other wing"),
                        P("X1", "X", "On the ball", "O1"), P("X8", "X", "In the lane, recovers late", "O8"), P("X3", "X", "Other wing", "O3")],
            "start": {"O1": O1, "O8": O8_BACK, "O3": O3T, "X1": X1T, "X8": X8_LANE, "X3": X3T},
            "legs": {"O8": [{"at": go, "to": O8_OPEN, "dur": 0.85}],
                     "X8": [{"at": p1 + 0.55, "to": [-3.6, 5.1], "dur": 1.0}]},
            "ball": [{"type": "hold", "player": "O1", "from": 0, "to": p0 - 0.2, "dribble": True},
                     {"type": "hold", "player": "O1", "from": p0 - 0.2, "to": p0},
                     {"type": "pass", "from": "O1", "to": "O8", "t0": p0, "t1": p1, "style": "chest"},
                     {"type": "hold", "player": "O8", "from": p1, "to": s0},
                     {"type": "shot", "player": "O8", "t0": s0, "t1": s1}],
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": p0 - 0.2, "face": "O8"}],
                        "X1": [{"type": "stance", "from": 0, "to": D_, "face": "O1"}],
                        "X3": [{"type": "stance", "from": 0, "to": D_, "face": "O3"}],
                        "X8": [{"type": "stance", "from": 0, "to": 4.3, "face": "O8"}, {"type": "topLock", "from": 4.3, "to": p1 + 0.5, "face": "O8", "side": 1},
                               {"type": "contest", "from": s0 - 0.05, "to": s0 + 0.5, "face": "O8"}],
                        "O8": [{"type": "hide", "from": 0, "to": 1.6, "face": "O1"},
                               {"type": "exhale", "from": 1.6, "to": 3.3, "face": "O1"},
                               {"type": "tap", "from": 3.4, "to": 4.0, "face": "O1"},
                               {"type": "gather", "from": go - 0.35, "to": go + 0.05, "face": "O1"},
                               {"type": "catchReady", "from": hands, "to": p1 + 0.05, "face": "O1"},
                               {"type": "call", "from": hands, "to": p0 + 0.2, "face": "O1"},
                               {"type": "gather", "from": p1 + 0.05, "to": s0 - 0.45, "face": 0.3},
                               {"type": "shoot", "from": s0 - 0.5, "to": s0 + 1.1, "face": 0.3}]},
            "expr": {"O8": [{"t": 0, "brow": -0.7, "look": "ball"}, {"t": 1.6, "blink": 0}, {"t": 1.85, "blink": 1}, {"t": 2.6, "blink": 1},
                            {"t": 2.85, "blink": 0, "brow": -0.45}, {"t": 3.4, "brow": -0.25}, {"t": 4.2, "brow": 0.1, "look": "O1"},
                            {"t": 4.8, "brow": 0.4}, {"t": hands, "open": 0.0}, {"t": hands + 0.2, "open": 0.55}, {"t": p0 + 0.1, "open": 0.1},
                            {"t": p1 + 0.2, "brow": 0.7, "look": "ball"}, {"t": s0 + 0.8, "brow": 0.7}],
                     "X8": [{"t": 0, "brow": 0.6, "look": "O8"}, {"t": p0, "brow": -0.2, "look": "ball"}, {"t": p1 + 0.2, "look": "O8"}],
                     "O1": [{"t": 0, "brow": 0.0, "look": "O8"}, {"t": opn, "brow": 0.4}],
                     "X1": [{"t": 0, "brow": 0.4, "look": "O1"}], "O3": [{"t": 0, "brow": 0.3}], "X3": [{"t": 0, "brow": 0.3}]},
            "marks": {"exhale": 1.6, "tap": 3.4, "eyes": 4.2, "plant": go - 0.35, "go": go, "open": opn, "hands": hands,
                      "pass": p0, "catch": p1, "square": p1 + 0.05, "release": s0, "rim": s1},
            "claims": [{"type": "open", "player": "O8", "at": "catch", "min": 1.2, "says": "He slides to the open line and catches."}]}


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T_, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T_, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


if __name__ == "__main__":
    for s in (practice(), miss(), hide(), ask()):
        p = build(s)
        print("built", p["id"], p["duration"])
