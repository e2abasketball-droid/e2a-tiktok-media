#!/usr/bin/env python3
"""HIDE IN GAMES V3 (owner brief 2026-11-17 21:31Z): the two possessions after the miss, now with the same five
players each (O1 passer, O8, O3 top, O4 weak-side corner; X4 in help in the paint, as weak-side help does with the
ball on the other side). Practice and the miss are the V2 plays (h2-practice, h2-miss), unchanged.
  h3-hide  possession 2: doubt (looks at the passer, then briefly down), half a hand comes up and goes back while X8
           keeps covering, O3 pops, O1 passes to O3
  h3-ask   possession 3, SAME start: short pause (exhale, light tap, eyes back), doubt for a beat, eyes to the passer,
           plant -> hip -> slide to the open line, hands, catch ready to shoot (feet set, chest to the rim). X4 closes
           out from the help AFTER the pass leaves (sprint, short braking steps, high hand); #8 reads rim -> X4 -> O4
           and makes the extra pass to the corner; O4 has turned his body and shown his hands, catches and attacks the
           closeout; X8 rotates; #8 relocates up the wing with his hands ready, eyes on the ball"""
import importlib.util, json, os
D = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("h2", os.path.join(D, "_gen-hide2.py"))
h2 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(h2)
P, SRC, build = h2.P, "original E2A character episode V3 (generic coaching knowledge)", h2.build
O1, O3T, X3T, X1T, O8_BACK, X8_LANE, O8_OPEN = h2.O1, h2.O3T, h2.X3T, h2.X1T, h2.O8_BACK, h2.X8_LANE, h2.O8_OPEN
O4 = [-6.75, 1.25]      # weak-side corner
X4 = [-1.9, 1.95]       # weak-side help in the paint (ball on the right)

CAST = [P("O1", "O", "Passer"), P("O8", "O", "#8"), P("O3", "O", "Top"), P("O4", "O", "Weak-side corner"),
        P("X1", "X", "On the ball", "O1"), P("X8", "X", "In the lane", "O8"), P("X3", "X", "Top", "O3"), P("X4", "X", "Help, closes out", "O4")]
START = {"O1": O1, "O8": O8_BACK, "O3": O3T, "O4": O4, "X1": X1T, "X8": X8_LANE, "X3": X3T, "X4": X4}


def hide():
    """possession 2. 0-4.5 medium (doubt: O1 at 1.3, down 2.25-2.85); 4.5- passer framing: half hand 4.9-5.9, pass to O3"""
    p0, p1, D_ = 6.5, 6.9, 9.6
    return {"id": "h3-hide", "title": "Hide V3: possession 2, he hides", "duration": D_, "source": SRC, "players": CAST, "start": START,
            "legs": {"O3": [{"at": 5.6, "to": [-0.9, 10.0], "dur": 0.9}], "X3": [{"at": 5.85, "to": [-0.7, 8.85], "dur": 0.9}],
                     "X8": [{"at": p1 + 0.3, "to": [-2.6, 5.4], "dur": 1.0}]},
            "ball": [{"type": "hold", "player": "O1", "from": 0, "to": p0 - 0.2, "dribble": True},
                     {"type": "hold", "player": "O1", "from": p0 - 0.2, "to": p0},
                     {"type": "pass", "from": "O1", "to": "O3", "t0": p0, "t1": p1, "style": "chest"},
                     {"type": "hold", "player": "O3", "from": p1, "to": D_, "dribble": True}],
            "actions": {"O1": [{"type": "dribble", "from": 0, "to": p0 - 0.2, "face": "O8"}],
                        "O3": [{"type": "catchReady", "from": 6.1, "to": p1, "face": "O1"}],
                        "O4": [{"type": "stance", "from": 0, "to": D_, "face": "O1", "pose": "high"}],
                        "X1": [{"type": "stance", "from": 0, "to": D_, "face": "O1"}],
                        "X3": [{"type": "stance", "from": 0, "to": D_, "face": "O3"}],
                        "X4": [{"type": "stance", "from": 0, "to": D_, "face": "O1"}],
                        "X8": [{"type": "stance", "from": 0, "to": 6.0, "face": "O8"}, {"type": "topLock", "from": 6.0, "to": D_, "face": "O8", "side": 1}],
                        "O8": [{"type": "hide", "from": 0, "to": 4.9, "face": "O1"},
                               {"type": "call", "from": 4.9, "to": 5.95, "face": "O1", "amt": 0.45},
                               {"type": "hide", "from": 5.9, "to": D_, "face": "O1"}]},
            "expr": {"O8": [{"t": 0, "brow": -0.5, "look": "ball"}, {"t": 1.3, "brow": -0.2, "look": "O1"}, {"t": 2.25, "brow": -0.75, "look": "down"},
                            {"t": 2.85, "look": "ball"}, {"t": 3.4, "brow": -0.8}, {"t": 4.8, "brow": -0.25, "look": "O1"}, {"t": 5.0, "open": 0.12},
                            {"t": 5.6, "brow": -0.4}, {"t": 5.9, "brow": -0.85, "open": 0.0, "look": "down"}, {"t": 6.35, "look": "ball"}, {"t": D_, "brow": -0.85}],
                     "X8": [{"t": 0, "brow": 0.6, "look": "O8"}],
                     "O1": [{"t": 0, "brow": 0.0, "look": "O8"}, {"t": 5.95, "brow": 0.2, "look": "O3"}],
                     "X1": [{"t": 0, "brow": 0.4, "look": "O1"}], "O3": [{"t": 0, "brow": 0.3, "smile": 0.2}], "X3": [{"t": 0, "brow": 0.3}],
                     "O4": [{"t": 0, "brow": 0.2}], "X4": [{"t": 0, "brow": 0.4}]},
            "marks": {"doubt": 1.3, "down": 2.25, "half": 4.9, "drop": 5.9, "pop": 5.6, "pass": p0, "catch": p1}}


def ask():
    """possession 3, same start. pause: exhale 0.3, tap 1.7, eyes 2.3; doubt 3.6-4.4 (down 3.85); eyes to the passer 4.3,
    plant 4.65 (foot -> hip -> hands), slide 4.95-5.95, hands 6.85, call 8.25, pass 8.6, catch 9.25 ready to shoot;
    X4 closes out from 9.4 (after the pass left), eyes rim 9.37 -> X4 10.4 -> O4 11.0, extra pass 11.55 -> 12.05;
    O4 rips and drives baseline, X8 helps, #8 drifts behind the help and gets the kick-out (14.45 -> 15.0); X8 closes
    out again, #8 swings it to O3 (15.7 -> 16.25) and relocates, O3 -> O1 (17.05 -> 17.45): the possession keeps running"""
    plant, go, opn, hands, call, p0, p1 = 4.65, 4.95, 5.7, 6.85, 8.25, 8.6, 9.25
    q0, q1 = p1 + 2.3, p1 + 2.8
    k0, k1 = q1 + 2.4, q1 + 2.95          # kick-out O4 -> O8
    s0, s1 = q1 + 3.65, q1 + 4.2          # swing O8 -> O3
    u0, u1 = q1 + 5.0, q1 + 5.4           # swing O3 -> O1
    D_ = round(q1 + 11.35, 2)
    return {"id": "h3-ask", "title": "Hide V3: possession 3, he asks, catches and makes the extra pass", "duration": D_, "source": SRC,
            "players": CAST, "start": START,
            "legs": {"O8": [{"at": go, "to": O8_OPEN, "dur": 1.0},
                            {"at": q0 + 0.3, "via": [[-4.9, 4.6]], "to": [-5.55, 5.55], "dur": 1.3},
                            {"at": q1 + 1.3, "to": [-5.9, 3.6], "dur": 1.0},
                            {"at": s0 + 0.5, "via": [[-6.0, 4.6]], "to": [-6.2, 6.3], "dur": 1.5}, {"at": s0 + 3.7, "to": [-4.9, 8.1], "dur": 1.7}],
                     "X8": [{"at": p1 + 0.55, "to": [-3.15, 5.55], "dur": 0.9}, {"at": q1 + 0.45, "to": [-2.75, 1.85], "dur": 1.0},
                            {"at": k0 + 0.2, "to": [-5.35, 2.95], "dur": 0.9}, {"at": s0 + 0.5, "to": [-5.2, 5.4], "dur": 1.4},
                            {"at": s0 + 2.3, "to": [-3.0, 5.0], "dur": 1.2}],
                     "X4": [{"at": p1 + 0.15, "to": [-3.0, 2.55], "dur": 0.75}, {"at": p1 + 0.9, "to": [-3.5, 3.0], "dur": 0.62},
                            {"at": q0 + 0.12, "to": [-3.95, 3.35], "dur": 0.7},
                            {"at": k1 + 0.1, "to": [1.4, 2.2], "dur": 1.9}, {"at": u1 + 2.15, "to": [1.9, 3.2], "dur": 1.0}],
                     "O4": [{"at": q1 + 0.55, "via": [[-5.6, 0.72]], "to": [-3.6, 0.8], "dur": 1.2}, {"at": k1 + 0.05, "to": [2.8, 1.35], "dur": 1.9},
                            {"at": u1 + 0.95, "to": [6.0, 2.0], "dur": 1.4}],
                     "O1": [{"at": q0 + 0.2, "to": [2.0, 8.9], "dur": 1.4}, {"at": u1 + 0.45, "to": [4.0, 6.6], "dur": 1.6}, {"at": u1 + 2.1, "to": [2.9, 4.6], "dur": 1.4}],
                     "X1": [{"at": q0 + 0.4, "to": [1.5, 7.8], "dur": 1.3}, {"at": u1 + 0.55, "to": [3.4, 7.1], "dur": 1.6}, {"at": u1 + 2.2, "to": [2.4, 5.0], "dur": 1.4}],
                     "O3": [{"at": q0 + 0.3, "to": [-1.9, 8.5], "dur": 1.5}, {"at": u1 + 1.15, "to": [-0.6, 9.8], "dur": 1.4}], "X3": [{"at": q0 + 0.5, "to": [-1.5, 7.4], "dur": 1.4},
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
                        "O4": [{"type": "stance", "from": 0, "to": q0 - 0.55, "face": "O1", "pose": "high"},
                               {"type": "catchReady", "from": q0 - 0.5, "to": q1 + 0.05, "face": "O8"},
                               {"type": "gather", "from": q1 + 0.05, "to": q1 + 0.5, "face": "X4"}],
                        "X4": [{"type": "stance", "from": 0, "to": p1 + 0.1, "face": "O1"},
                               {"type": "closeout", "from": p1 + 0.25, "to": q0 + 0.3, "face": "O8"},
                               {"type": "stance", "from": q0 + 0.6, "to": k1, "face": "O4"}],
                        "X8": [{"type": "stance", "from": 0, "to": 3.6, "face": "O8"}, {"type": "topLock", "from": 3.6, "to": p1 + 0.5, "face": "O8", "side": 1},
                               {"type": "stance", "from": q1 + 1.2, "to": k0 + 0.1, "face": "O4"},
                               {"type": "closeout", "from": k0 + 0.45, "to": s0 + 0.4, "face": "O8"},
                               {"type": "stance", "from": s0 + 1.9, "to": D_, "face": "O8"}],
                        "O8": [{"type": "hide", "from": 0, "to": 0.3, "face": "O1"},
                               {"type": "exhale", "from": 0.3, "to": 1.6, "face": "O1"},
                               {"type": "tap", "from": 1.7, "to": 2.15, "face": "O1"},
                               {"type": "hide", "from": 3.6, "to": 4.45, "face": "O1"},
                               {"type": "gather", "from": plant, "to": go + 0.05, "face": "O1"},
                               {"type": "catchReady", "from": hands, "to": p1 + 0.05, "face": "O1"},
                               {"type": "call", "from": call, "to": p0 + 0.2, "face": "O1"},
                               {"type": "gather", "from": p1 + 0.05, "to": q0 - 0.1, "face": -0.52},
                               {"type": "catchReady", "from": q1 + 0.3, "to": k1 + 0.05, "face": "O4"},
                               {"type": "gather", "from": k1 + 0.05, "to": s0 - 0.1, "face": -0.33},
                               {"type": "catchReady", "from": s1 + 0.6, "to": D_, "face": "O3"}]},
            "expr": {"O8": [{"t": 0, "brow": -0.7, "look": "ball"}, {"t": 0.35, "blink": 0}, {"t": 0.55, "blink": 1}, {"t": 1.1, "blink": 1},
                            {"t": 1.3, "blink": 0, "brow": -0.45}, {"t": 1.7, "brow": -0.25}, {"t": 2.3, "brow": 0.05, "look": "O1"},
                            {"t": 3.6, "brow": -0.5}, {"t": 3.85, "look": "down"}, {"t": 4.3, "brow": 0.2, "look": "O1"},
                            {"t": 4.7, "brow": 0.45}, {"t": call, "open": 0.0}, {"t": call + 0.15, "open": 0.55}, {"t": p0 + 0.15, "open": 0.1},
                            {"t": p0 + 0.15, "look": "ball"}, {"t": p1 + 0.12, "brow": 0.7, "open": 0.0, "look": "rim"}, {"t": p1 + 1.15, "brow": 0.5, "look": "X4"},
                            {"t": p1 + 1.75, "brow": 0.6, "look": "O4"}, {"t": q1 + 0.1, "look": "ball"}, {"t": k1 + 0.1, "look": "rim"},
                            {"t": k1 + 0.45, "look": "X8"}, {"t": s0 - 0.35, "look": "O3"}, {"t": s1, "look": "ball"}, {"t": D_, "brow": 0.6}],
                     "X8": [{"t": 0, "brow": 0.6, "look": "O8"}, {"t": p0, "brow": -0.2, "look": "ball"}, {"t": k0 + 0.3, "brow": 0.7, "look": "O8"}, {"t": s0 + 0.1, "look": "ball"}],
                     "X4": [{"t": 0, "brow": 0.4, "look": "ball"}, {"t": p1, "brow": 0.8, "look": "O8"}, {"t": q0 + 0.05, "look": "ball"}],
                     "O4": [{"t": 0, "brow": 0.2, "look": "ball"}, {"t": q0 - 0.5, "brow": 0.6, "open": 0.3}, {"t": q0, "open": 0.0}],
                     "O1": [{"t": 0, "brow": 0.0, "look": "O8"}, {"t": opn, "brow": 0.4}, {"t": q0, "look": "ball"}],
                     "X1": [{"t": 0, "brow": 0.4, "look": "O1"}], "O3": [{"t": 0, "brow": 0.3}], "X3": [{"t": 0, "brow": 0.3}]},
            "marks": {"exhale": 0.3, "tap": 1.7, "eyes": 2.3, "doubt": 3.6, "plant": plant, "go": go, "open": opn, "hands": hands, "call": call,
                      "pass": p0, "catch": p1, "rim": p1 + 0.12, "closeout": p1 + 0.15, "seesX4": p1 + 1.15, "seesO4": p1 + 1.75,
                      "extra": q0, "o4catch": q1, "kick": k0, "kcatch": k1, "swing": s0, "swing2": u0},
            "claims": [{"type": "open", "player": "O8", "at": "catch", "min": 1.6, "says": "He catches on the open line, ready to shoot."},
                       {"type": "open", "player": "O4", "at": "o4catch", "min": 2.0, "says": "The help left the corner: one more pass."}]}


if __name__ == "__main__":
    for s in (hide(), ask()):
        p = build(s)
        print("built", p["id"], p["duration"])
