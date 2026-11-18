#!/usr/bin/env python3
"""HIDE IN GAMES V4 (owner brief 2026-11-18 02:39Z). Same cast and court side as V3: O1 with the ball at the top,
#8 (O8) on the left wing guarded by #14 (X8), #4 (O4) in the corner on that side, O3 at the top/right; X4 sunk in
the paint. Practice is the V2 play (h2-practice).
  h4-miss  the miss: the shooting arm stays up after the rim, the eyes follow the rebound, then the arm drops and the
           torso turns to get back; the others react to the ball
  h4-hide  possession 2: avoids the passer's gaze, thought (looks at O1, half a hand up, back at the end of the
           question), a second half hand pulled back from the passer's view, #14 in the line, the ball goes to O3
           and the possession goes on while #8 stays still
  h4-ask   possession 3 (play time = episode time - 20.2 s up to the catch): exhale, eyes up to the passer, ATTEMPT 1
           (step to the space, #14 follows and keeps the line, both plant feet, hesitation), ATTEMPT 2 (exhale on the
           move, jab, load on the plant foot, change of direction, separation to the wing, eyes to O1, hands), the
           pass leaves after the line opens, two-hand catch ready to shoot; #14 recovers while the ball travels and
           arrives with a high hand; X4 still sunk -> O4 open; eyes rim -> #14 -> O4, extra pass, O4 controls and
           attacks, #8 relocates watching the play, the ball keeps moving"""
import importlib.util, os
D = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("h2", os.path.join(D, "_gen-hide2.py"))
h2 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(h2)
P, build = h2.P, h2.build
SRC = "original E2A character episode V4 (generic coaching knowledge)"
O1, O3T, X3T, X1T, O8_BACK, X8_LANE, O8_OPEN = h2.O1, h2.O3T, h2.X3T, h2.X1T, h2.O8_BACK, h2.X8_LANE, h2.O8_OPEN
O4 = [-6.75, 1.25]      # corner, #8's side
X4 = [-1.75, 2.15]      # sunk in the paint
A1 = [-4.5, 7.35]       # attempt 1: step up toward the space
X8_A1 = [-3.3, 7.15]    # #14 follows and stays in the line O1 -> #8
A2 = [-4.6, 7.95]       # attempt 2: jab up, plant here
X8_A2 = [-3.45, 7.75]   # #14 bites on the jab
X8_LATE = [-3.5, 6.75]  # #14 reacts late to the change of direction
X8_CLOSE = [-3.8, 4.8]  # closeout spot: high hand, top side of #8
CAST = [P("O1", "O", "Passer"), P("O8", "O", "#8"), P("O3", "O", "Top"), P("O4", "O", "Corner"),
        P("X1", "X", "On the ball", "O1"), P("X8", "X", "#14 on #8", "O8"), P("X3", "X", "Top", "O3"), P("X4", "X", "Sunk in the paint", "O4")]
START = {"O1": O1, "O8": O8_BACK, "O3": O3T, "O4": O4, "X1": X1T, "X8": X8_LANE, "X3": X3T, "X4": X4}


def miss():
    s = h2.miss()
    t1 = h2.SHOT1
    s["id"], s["title"], s["source"] = "h4-miss", "Hide V4: the open miss, arm held, eyes on the rebound", SRC
    s["legs"]["O8"] = [{"at": t1 + 1.55, "via": [[-3.9, 5.6]], "to": [-2.6, 9.6], "speed": 3.2}]
    s["actions"]["O8"] = h2.O8_SHOT_ACTS + [{"type": "shoot", "from": h2.SHOT0 - 0.5, "to": t1 + 0.55, "face": 0.3},
                                            {"type": "exhale", "from": t1 + 0.75, "to": t1 + 1.6, "face": "ball"}]
    s["actions"]["O1"] = [{"type": "dribble", "from": 0, "to": h2.PASS0 - 0.2, "face": "O8"}]
    s["expr"]["O8"] = [{"t": 0, "brow": 0.55, "smile": 0.2, "look": "ball"}, {"t": h2.CATCH, "smile": 0.0, "brow": 0.6, "look": "rim"},
                       {"t": t1, "brow": 0.6, "open": 0.0, "look": "ball"}, {"t": t1 + 0.18, "brow": -0.2, "open": 0.35},
                       {"t": t1 + 0.6, "brow": -0.85, "open": 0.1}, {"t": t1 + 1.15, "blink": 0}, {"t": t1 + 1.3, "blink": 1, "look": "down"},
                       {"t": t1 + 1.6, "blink": 1}, {"t": t1 + 1.75, "blink": 0, "brow": -0.7}, {"t": t1 + 2.3, "look": "ball"}]
    s["marks"]["armDown"] = t1 + 0.55
    return s


def hide():
    """episode time = play time + 7.3"""
    h1, h1b, h2_, h2b = 1.3, 2.2, 3.1, 4.75        # thought hand up/back; second half hand up/back
    p0, p1, D_ = 9.75, 10.15, 13.4
    return {"id": "h4-hide", "title": "Hide V4: possession 2, he hides", "duration": D_, "source": SRC, "players": CAST, "start": START,
            "legs": {"O3": [{"at": 8.3, "to": [-0.9, 10.0], "dur": 0.9}], "X3": [{"at": 8.55, "to": [-0.7, 8.85], "dur": 0.9}],
                     "X8": [{"at": p1 + 0.4, "to": [-2.6, 5.4], "dur": 1.0}],
                     "O1": [{"at": p1 + 0.6, "to": [2.4, 8.8], "dur": 1.4}], "X1": [{"at": p1 + 0.8, "to": [1.8, 7.7], "dur": 1.3}],
                     "O4": [{"at": p1 + 0.9, "to": [-6.5, 2.1], "dur": 1.2}]},
            "ball": [{"type": "hold", "player": "O1", "from": 0, "to": p0 - 0.2, "dribble": True},
                     {"type": "hold", "player": "O1", "from": p0 - 0.2, "to": p0},
                     {"type": "pass", "from": "O1", "to": "O3", "t0": p0, "t1": p1, "style": "chest"},
                     {"type": "hold", "player": "O3", "from": p1, "to": D_, "dribble": True}],
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": p0 - 0.2, "face": "O8"}],
                        "O3": [{"type": "catchReady", "from": 8.9, "to": p1, "face": "O1"}],
                        "O4": [{"type": "stance", "from": 0, "to": D_, "face": "O1", "pose": "high"}],
                        "X1": [{"type": "stance", "from": 0, "to": D_, "face": "O1"}],
                        "X3": [{"type": "stance", "from": 0, "to": D_, "face": "O3"}],
                        "X4": [{"type": "stance", "from": 0, "to": D_, "face": "O1"}],
                        "X8": [{"type": "stance", "from": 0, "to": 2.6, "face": "O8"}, {"type": "topLock", "from": 2.6, "to": D_, "face": "O8", "side": 1}],
                        "O8": [{"type": "hide", "from": 0, "to": h1, "face": "O1"},
                               {"type": "call", "from": h1, "to": h1b, "face": "O1", "amt": 0.35},
                               {"type": "hide", "from": h1b, "to": h2_, "face": "O1"},
                               {"type": "call", "from": h2_, "to": h2b, "face": "O1", "amt": 0.45},
                               {"type": "hide", "from": h2b, "to": D_, "face": "O1"}]},
            "expr": {"O8": [{"t": 0, "brow": -0.6, "look": "ball"}, {"t": 0.35, "brow": -0.75, "look": "down"},
                            {"t": 1.1, "brow": -0.2, "look": "O1"}, {"t": 1.4, "open": 0.1}, {"t": 2.1, "brow": -0.7, "open": 0.0},
                            {"t": 2.45, "look": "down"}, {"t": 2.95, "brow": -0.3, "look": "O1"}, {"t": 3.3, "open": 0.12},
                            {"t": 4.1, "brow": -0.45}, {"t": 4.7, "brow": -0.85, "open": 0.0, "look": "down"}, {"t": 5.3, "look": "ball"},
                            {"t": D_, "brow": -0.85}],
                     "X8": [{"t": 0, "brow": 0.6, "look": "O8"}],
                     "O1": [{"t": 0, "brow": 0.0, "look": "O8"}, {"t": 8.4, "brow": 0.2, "look": "O3"}, {"t": p1, "look": "ball"}],
                     "X1": [{"t": 0, "brow": 0.4, "look": "O1"}], "O3": [{"t": 0, "brow": 0.3, "smile": 0.2}], "X3": [{"t": 0, "brow": 0.3}],
                     "O4": [{"t": 0, "brow": 0.2, "look": "ball"}], "X4": [{"t": 0, "brow": 0.4, "look": "ball"}]},
            "marks": {"avoid": 0.35, "thought": 1.1, "half": h1, "back": h1b, "half2": h2_, "drop": h2b, "pop": 8.3, "pass": p0, "catch": p1}}


def ask():
    """play time = episode time - 20.2 s (until the catch)"""
    ex0, eyes = 0.5, 2.3
    a1, a1p = 3.8, 5.8                     # attempt 1: first step (cut), both feet planted
    see = 6.4                              # sees #14 in the line: hesitation
    jab, plant, go, wing = 8.35, 9.25, 9.65, 10.8
    hands, call, p0, p1 = 11.0, 11.3, 12.8, 13.45
    q0 = round(p1 + 2.9, 2)
    q1 = round(q0 + 0.5, 2)
    k0, k1 = q1 + 2.4, q1 + 2.95           # kick-out O4 -> O8
    s0, s1 = q1 + 3.65, q1 + 4.2           # swing O8 -> O3
    u0, u1 = q1 + 5.0, q1 + 5.4            # swing O3 -> O1
    D_ = round(q1 + 11.6, 2)
    return {"id": "h4-ask", "title": "Hide V4: possession 3, two attempts, the catch and the extra pass", "duration": D_, "source": SRC,
            "players": CAST, "start": START,
            "legs": {"O8": [{"at": a1, "to": A1, "dur": a1p - a1},
                            {"at": jab, "to": A2, "dur": plant - jab},
                            {"at": go, "to": O8_OPEN, "dur": wing - go},
                            {"at": q0 + 0.3, "via": [[-4.9, 4.6]], "to": [-5.55, 5.55], "dur": 1.3},
                            {"at": q1 + 1.3, "to": [-5.9, 3.6], "dur": 1.0},
                            {"at": s0 + 0.5, "via": [[-6.0, 4.6]], "to": [-6.2, 6.3], "dur": 1.5}, {"at": s0 + 3.7, "to": [-4.9, 8.1], "dur": 1.7}],
                     "X8": [{"at": a1 + 0.25, "to": X8_A1, "dur": a1p - a1 + 0.1},
                            {"at": jab + 0.2, "to": X8_A2, "dur": plant - jab},
                            {"at": go + 0.4, "to": X8_LATE, "dur": 0.75},
                            {"at": p0 + 0.08, "to": X8_CLOSE, "dur": p1 + 1.25 - p0 - 0.08},
                            {"at": q1 + 0.45, "to": [-2.6, 2.6], "dur": 1.1},
                            {"at": k0 + 0.2, "to": [-5.35, 2.95], "dur": 0.9}, {"at": s0 + 0.5, "to": [-5.2, 5.4], "dur": 1.4},
                            {"at": s0 + 2.3, "to": [-3.0, 5.0], "dur": 1.2}],
                     "X4": [{"at": q0 + 0.2, "to": [-4.4, 1.9], "dur": 0.9},
                            {"at": q1 + 0.75, "to": [-3.3, 1.5], "dur": 1.1},
                            {"at": k1 + 0.3, "via": [[-1.8, 2.45]], "to": [1.4, 2.4], "dur": 1.9}, {"at": u1 + 2.15, "to": [1.9, 3.2], "dur": 1.0}],
                     "O4": [{"at": q1 + 0.55, "via": [[-5.6, 0.72]], "to": [-3.6, 0.8], "dur": 1.2}, {"at": k1 + 0.05, "to": [2.8, 1.35], "dur": 1.9},
                            {"at": u1 + 0.95, "to": [6.0, 2.0], "dur": 1.4}],
                     "O1": [{"at": q0 + 0.2, "to": [2.0, 8.9], "dur": 1.4}, {"at": u1 + 0.45, "to": [4.0, 6.6], "dur": 1.6}, {"at": u1 + 2.1, "to": [2.9, 4.6], "dur": 1.4}],
                     "X1": [{"at": q0 + 0.4, "to": [1.5, 7.8], "dur": 1.3}, {"at": u1 + 0.55, "to": [3.4, 7.1], "dur": 1.6}, {"at": u1 + 2.2, "to": [2.4, 5.0], "dur": 1.4}],
                     "O3": [{"at": 1.0, "to": [1.2, 10.6], "dur": 1.6}, {"at": q0 + 0.3, "to": [-1.9, 8.5], "dur": 1.5}, {"at": u1 + 1.15, "to": [-0.6, 9.8], "dur": 1.4}],
                     "X3": [{"at": 1.2, "to": [1.1, 9.7], "dur": 1.6}, {"at": q0 + 0.5, "to": [-1.5, 7.4], "dur": 1.4},
                            {"at": s1 - 0.2, "to": [-1.85, 7.55], "dur": 0.6}, {"at": u1 + 1.35, "to": [-1.2, 9.0], "dur": 1.4}]},
            "ball": [{"type": "hold", "player": "O1", "from": 0, "to": p0 - 0.2, "dribble": True},
                     {"type": "hold", "player": "O1", "from": p0 - 0.2, "to": p0},
                     {"type": "pass", "from": "O1", "to": "O8", "t0": p0, "t1": p1, "style": "chest"},
                     {"type": "hold", "player": "O8", "from": p1, "to": q0},
                     {"type": "pass", "from": "O8", "to": "O4", "t0": q0, "t1": q1, "style": "chest"},
                     {"type": "hold", "player": "O4", "from": q1, "to": q1 + 0.5},
                     {"type": "hold", "player": "O4", "from": q1 + 0.5, "to": q1 + 1.85, "dribble": True},
                     {"type": "hold", "player": "O4", "from": q1 + 1.85, "to": k0},
                     {"type": "pass", "from": "O4", "to": "O8", "t0": k0, "t1": k1, "style": "chest"},
                     {"type": "hold", "player": "O8", "from": k1, "to": s0},
                     {"type": "pass", "from": "O8", "to": "O3", "t0": s0, "t1": s1, "style": "chest"},
                     {"type": "hold", "player": "O3", "from": s1, "to": u0},
                     {"type": "pass", "from": "O3", "to": "O1", "t0": u0, "t1": u1, "style": "chest"},
                     {"type": "hold", "player": "O1", "from": u1, "to": D_, "dribble": True}],
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": p0 - 0.2, "face": "O8"}],
                        "X1": [{"type": "stance", "from": 0, "to": D_, "face": "O1"}],
                        "X3": [{"type": "stance", "from": 0, "to": D_, "face": "O3"}],
                        "O4": [{"type": "stance", "from": 0, "to": q0 - 0.9, "face": "O1", "pose": "high"},
                               {"type": "catchReady", "from": q0 - 0.85, "to": q1 + 0.05, "face": "O8"},
                               {"type": "gather", "from": q1 + 0.05, "to": q1 + 0.5, "face": "X4"}],
                        "X4": [{"type": "stance", "from": 0, "to": q0 + 0.15, "face": "O1"},
                               {"type": "closeout", "from": q0 + 0.2, "to": q1 + 0.55, "face": "O4"},
                               {"type": "stance", "from": q1 + 0.75, "to": k1, "face": "O4"}],
                        "X8": [{"type": "stance", "from": 0, "to": a1 + 0.2, "face": "O8"},
                               {"type": "topLock", "from": a1 + 0.25, "to": go + 0.35, "face": "O8", "side": 1},
                               {"type": "closeout", "from": p0 + 0.1, "to": q0 + 0.35, "face": "O8"},
                               {"type": "stance", "from": q1 + 1.4, "to": k0 + 0.1, "face": "O4"},
                               {"type": "closeout", "from": k0 + 0.45, "to": s0 + 0.4, "face": "O8"},
                               {"type": "stance", "from": s0 + 1.9, "to": D_, "face": "O8"}],
                        "O8": [{"type": "hide", "from": 0, "to": ex0, "face": "O1"},
                               {"type": "exhale", "from": ex0, "to": 1.8, "face": "O1"},
                               {"type": "stance", "from": 2.4, "to": a1 - 0.05, "face": "O1", "pose": "high"},
                               {"type": "gather", "from": a1p - 0.2, "to": a1p + 0.45, "face": "O1"},
                               {"type": "hide", "from": see + 0.1, "to": jab - 0.3, "face": "O1"},
                               {"type": "exhale", "from": jab - 0.35, "to": jab + 0.55, "face": "O1"},
                               {"type": "gather", "from": plant - 0.25, "to": go + 0.1, "face": "O1"},
                               {"type": "catchReady", "from": hands, "to": p1 + 0.05, "face": "O1"},
                               {"type": "call", "from": call, "to": p0 + 0.2, "face": "O1"},
                               {"type": "gather", "from": p1 + 0.05, "to": q0 - 0.1, "face": -0.52},
                               {"type": "catchReady", "from": q1 + 0.3, "to": k1 + 0.05, "face": "O4"},
                               {"type": "gather", "from": k1 + 0.05, "to": s0 - 0.1, "face": -0.33},
                               {"type": "catchReady", "from": s1 + 0.6, "to": D_, "face": "O3"}]},
            "expr": {"O8": [{"t": 0, "brow": -0.7, "look": "ball"}, {"t": ex0 + 0.1, "blink": 0}, {"t": ex0 + 0.3, "blink": 1}, {"t": 1.1, "blink": 1},
                            {"t": 1.3, "blink": 0, "brow": -0.4}, {"t": eyes, "brow": 0.1, "look": "O1"},
                            {"t": a1, "brow": 0.3}, {"t": see, "brow": -0.3, "look": "X8"}, {"t": see + 0.6, "brow": -0.6, "look": "down"},
                            {"t": see + 1.1, "look": "O1"}, {"t": jab - 0.3, "brow": -0.1}, {"t": plant, "brow": 0.35},
                            {"t": wing - 0.4, "brow": 0.55, "look": "O1"}, {"t": call, "open": 0.0}, {"t": call + 0.15, "open": 0.55},
                            {"t": p0 + 0.15, "open": 0.1, "look": "ball"}, {"t": p1 + 0.1, "brow": 0.7, "open": 0.0, "look": "rim"},
                            {"t": p1 + 1.2, "brow": 0.5, "look": "X8"}, {"t": p1 + 2.2, "brow": 0.6, "look": "O4"}, {"t": q1 + 0.1, "look": "ball"},
                            {"t": k1 + 0.1, "look": "rim"}, {"t": k1 + 0.45, "look": "X8"}, {"t": s0 - 0.35, "look": "O3"}, {"t": s1, "look": "ball"}, {"t": D_, "brow": 0.6}],
                     "X8": [{"t": 0, "brow": 0.6, "look": "O8"}, {"t": p0, "brow": 0.8, "look": "ball"}, {"t": p0 + 0.3, "look": "O8"},
                            {"t": q0 + 0.05, "look": "ball"}, {"t": k0 + 0.3, "brow": 0.7, "look": "O8"}, {"t": s0 + 0.1, "look": "ball"}],
                     "X4": [{"t": 0, "brow": 0.4, "look": "ball"}, {"t": q0, "brow": 0.8, "look": "O4"}, {"t": q1 + 0.6, "look": "ball"}],
                     "O4": [{"t": 0, "brow": 0.2, "look": "ball"}, {"t": q0 - 0.85, "brow": 0.6, "open": 0.3, "look": "O8"}, {"t": q0, "open": 0.0},
                            {"t": q0 + 0.1, "look": "ball"}],
                     "O1": [{"t": 0, "brow": 0.0, "look": "O8"}, {"t": wing - 0.3, "brow": 0.4}, {"t": q0, "look": "ball"}],
                     "X1": [{"t": 0, "brow": 0.4, "look": "O1"}], "O3": [{"t": 0, "brow": 0.3}], "X3": [{"t": 0, "brow": 0.3}]},
            "marks": {"exhale": ex0, "eyes": eyes, "step1": a1, "plant1": a1p, "see": see, "jab": jab, "plant": plant, "go": go, "wing": wing,
                      "hands": hands, "call": call, "pass": p0, "catch": p1, "rim": p1 + 0.1, "closeout": p0 + 0.08, "seesX8": p1 + 1.2,
                      "seesO4": p1 + 2.2, "extra": q0, "o4catch": q1, "kick": k0, "kcatch": k1, "swing": s0, "swing2": u0},
            "claims": [{"type": "open", "player": "O8", "at": "catch", "min": 1.6, "says": "He catches after the change of direction, ready to shoot."},
                       {"type": "open", "player": "O4", "at": "o4catch", "min": 2.0, "says": "His defender is still in the paint: one more pass."}]}


if __name__ == "__main__":
    for s in (miss(), hide(), ask()):
        p = build(s)
        print("built", p["id"], p["duration"])
