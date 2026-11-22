#!/usr/bin/env python3
"""E2A Realism V3 (2026-11-22) — TEST fixture, never a social episode: the "ONE CONTINUOUS TAKE" of brief sec. 11.
One main athlete (O1) + a passer (O2, at the top, so the ball never appears out of nowhere), 12.5 s, no cut:
  0.0-1.0  ready stance (balance)                  1.0-2.7  acceleration + sprint (A -> B)
  2.7-4.1  hard deceleration + plant + 75 deg cut  4.1-5.5  two-hand catch of O2's chest pass (eyes on the ball)
  5.5-7.2  control dribble, re-orientation         7.2-9.1  gather + jump shot (release ~7.9 s, make)
  9.1-10.5 landing + recovery                      10.5-12.5 back-pedal into a defensive stance
Both renderers (athleteRenderer 'legacy' / 'v3') play EXACTLY this file: same tracks, ball events, actions, camera.
  python3 tactical/specs/_gen-realism-v3-onetake.py   -> tactical/specs/realism-v3-onetake.spec.json + tactical/plays/
Repo axes: rim at (0, 1.575), the action on the x < 0 side, 30 fps frame numbers below."""
import importlib.util, json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
_s = importlib.util.spec_from_file_location("v2", os.path.join(D, "_gen-chicago-v2.py"))
v2 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(v2)
S, runk, cat = v2.S, v2.runk, v2.cat
st = lambda f, a, b: {"type": "stance", "from": S(a), "to": S(b), "face": f}
face = lambda f, a, b: {"type": "face", "from": S(a), "to": S(b), "face": f}

A = (-6.3, 7.4)      # ready spot (right wing, 45 deg)
B = (-4.05, 3.75)    # plant of the cut (after ~4.3 m of sprint)
C = (-2.35, 4.45)    # catch spot (75 deg cut toward the middle)
DD = (-3.35, 5.55)   # pull-up spot after the control dribble (5.3 m from the rim)
E = (-3.7, 7.05)     # defensive stance after the back-pedal
O2P = (-6.6, 1.3)    # passer in the far corner: behind O1 for the camera, never between them
DUR = 375            # 12.5 s
F_PASS0, F_PASS1 = 124, 140          # chest pass O2 -> O1 (0.53 s of flight), catch at 4.67 s
F_DRIB0, F_DRIB1 = 147, 214          # control dribble 4.9 -> 7.13 s
F_GATHER, F_SHOT, F_MAKE = 214, 236, 266   # gather 7.13, release 7.87, through the net 8.87

O1 = cat(runk([(0, A, 0.0), (30, A, 0.0)]),
         # 1.0 -> 2.7 s: acceleration, 2.7 -> 3.4 s: hard brake into the plant at B
         runk([(30, A, 0.0), (66, (-4.95, 5.1), 5.2), (90, (-4.18, 3.95), 2.6), (99, B, 0.35)]),
         # the cut: plant at B (stopped ~0.1 s), new impulse 75 deg to the left, catch in stride at C
         runk([(102, B, 0.35), (122, (-3.2, 4.15), 3.3), (140, C, 1.4), (147, (-2.33, 4.52), 0.0)]),
         # control dribble: back out to the pull-up spot while turning to face the rim
         runk([(150, (-2.33, 4.52), 0.0), (182, (-2.92, 5.12), 1.2), (214, DD, 0.0)]),
         runk([(214, DD, 0.0), (288, DD, 0.0)]),
         # 9.6 -> 11.3 s: back-pedal into the defensive stance
         runk([(300, DD, 0.0), (322, (-3.5, 6.3), 1.6), (342, E, 0.0), (DUR, E, 0.0)]))
O2 = cat(runk([(0, O2P, 0.0), (DUR, O2P, 0.0)]))


def track(anchors):
    ks = sorted(anchors)
    out = []
    for k in ks:
        w = [S(k), anchors[k][0], anchors[k][1]]
        if out and abs(out[-1][0] - w[0]) < 1e-9:
            out[-1] = w
        else:
            out.append(w)
    if out[-1][0] < S(DUR):
        out.append([S(DUR), out[-1][1], out[-1][2]])
    return out


def spec():
    ball = [{"type": "hold", "player": "O2", "from": 0, "to": S(F_PASS0)},
            {"type": "pass", "from": "O2", "to": "O1", "t0": S(F_PASS0), "t1": S(F_PASS1)},
            {"type": "hold", "player": "O1", "from": S(F_PASS1), "to": S(F_DRIB0)},
            {"type": "hold", "player": "O1", "from": S(F_DRIB0), "to": S(F_DRIB1), "dribble": True, "hand": 1},
            {"type": "hold", "player": "O1", "from": S(F_GATHER), "to": S(F_SHOT)},
            {"type": "shot", "player": "O1", "t0": S(F_SHOT), "t1": S(F_MAKE), "make": True, "three": False}]
    rimA = lambda p: round(math.atan2(1.575 - p[1], 0.0 - p[0]), 4)
    actions = {"O1": [st(rimA(A), 0, 30), face("O2", 100, F_PASS1 + 4), {"type": "catchReady", "from": S(F_PASS1 - 14), "to": S(F_DRIB0 + 2), "face": "O2"}, face(rimA(DD), F_DRIB0 + 8, F_SHOT + 30),
                      st("O2", 312, DUR)],
               "O2": [face("O1", 0, DUR)]}
    s = {"id": "realism-v3-onetake", "title": "Realism V3 one continuous take (TEST fixture): ready, sprint, brake + cut, catch, dribble, jump shot, land, defensive stance",
         "duration": S(DUR), "concept": "realism-v3-test", "test": True, "squareUp": True, "handBallClear": True, "realism": 3,
         "source": "E2A synthetic test fixture (brief Realism V3 sec. 2.2 / 11), no real play copied",
         "players": [{"id": "O1", "team": "O", "role": "Test athlete: every phase of the one-take"},
                     {"id": "O2", "team": "O", "role": "Passer at the top (the ball's origin stays in frame / explained)"}],
         "tracks": {"O1": track(O1), "O2": track(O2)}, "ball": ball, "actions": actions, "screens": [],
         "marks": {"ready": 0, "sprint": S(30), "plant": S(99), "cut": S(102), "pass": S(F_PASS0), "catch": S(F_PASS1), "dribble": S(F_DRIB0),
                   "gather": S(F_GATHER), "release": S(F_SHOT), "make": S(F_MAKE), "land": S(F_SHOT + 22), "backpedal": S(300), "stance": S(342), "end": S(DUR)}}
    return s


if __name__ == "__main__":
    s = spec()
    json.dump(s, open(os.path.join(D, "realism-v3-onetake.spec.json"), "w"), indent=1)
    json.dump(s, open(os.path.join(T, "tactical", "plays", "realism-v3-onetake.json"), "w"), indent=1)
    print("built", s["id"], "dur", s["duration"], "pull-up to rim", round(math.hypot(DD[0], DD[1] - 1.575), 2), "m; pass", round(math.hypot(O2P[0] - C[0], O2P[1] - C[1]), 2), "m")
