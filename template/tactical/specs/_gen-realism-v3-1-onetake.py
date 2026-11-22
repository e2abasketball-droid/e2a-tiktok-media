#!/usr/bin/env python3
"""E2A Realism V3.1 (2026-11-22) — TEST fixture, never a social episode: the 12.5 s one-take of brief V3.1 sec. 8.
One main athlete (O1) + a passer (O2, at the top of the key, in front of the cut), no cut in the camera:
  0.0-1.5  ready / intent                      1.5-3.0  accelerate (A -> B)
  3.0-4.5  brake, right-foot plant, 80 deg cut 4.5-6.0  catch of O2's chest pass at 4.933 s, 1-2 stop, pivot to the rim
  6.0-7.0  jab + ONE bounce on a step-back     7.0-9.5  gather, dip, jump shot (release 8.20 s, make 9.20 s)
  9.5-11.5 land, recover, back-pedal           11.5-12.5 defensive stance (hold)
Both renderers play EXACTLY this file (same tracks, ball events, engine actions); athleteRenderer 'v31' replaces only
O1's body motion by the hand-keyed clip in src/t3d/realism-v3-1/clips.ts (same timings, the track is its root).
  python3 tactical/specs/_gen-realism-v3-1-onetake.py -> tactical/specs/realism-v3-1-onetake.spec.json + tactical/plays/"""
import importlib.util, json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
_s = importlib.util.spec_from_file_location("v2", os.path.join(D, "_gen-chicago-v2.py"))
v2 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(v2)
S, runk, cat = v2.S, v2.runk, v2.cat
st = lambda f, a, b: {"type": "stance", "from": S(a), "to": S(b), "face": f}
face = lambda f, a, b: {"type": "face", "from": S(a), "to": S(b), "face": f}
add = lambda p, d, k: (round(p[0] + d[0] * k, 3), round(p[1] + d[1] * k, 3))

A = (-6.3, 7.4)
B = (-4.05, 3.75)
dAB = ((B[0] - A[0]) / math.hypot(B[0] - A[0], B[1] - A[1]), (B[1] - A[1]) / math.hypot(B[0] - A[0], B[1] - A[1]))
P1, P2 = add(A, dAB, 2.7), add(A, dAB, 3.75)
dc = (math.cos(math.radians(22)), math.sin(math.radians(22)))
C = add(B, dc, 2.9)
C1 = add(C, dc, 0.12)
rim = (0.0, 1.575)
rd = ((rim[0] - C1[0]) / math.hypot(rim[0] - C1[0], rim[1] - C1[1]), (rim[1] - C1[1]) / math.hypot(rim[0] - C1[0], rim[1] - C1[1]))
DD = add(C1, rd, -1.0)
E = add(DD, rd, -1.5)
O2P = (0.0, 8.8)  # top of the key: in front of the cut, never on the camera line
DUR = 375
F_PASS0, F_PASS1 = 132, 148           # 4.40 -> 4.933 s
F_DRIB0, F_DRIB1 = 184, 202           # 6.133 -> 6.733 s: one bounce
F_SHOT, F_MAKE = 246, 276             # release 8.20, through the net 9.20

O1 = cat(runk([(0, A, 0.0), (45, A, 0.0)]),
         runk([(45, A, 0.0), (81, P1, 4.6), (92, P2, 2.6), (99, B, 0.6), (112, add(B, dc, 0.8), 3.4), (138, add(B, dc, 2.35), 2.4), (148, C, 0.9), (156, C1, 0.0)]),
         runk([(156, C1, 0.0), (184, C1, 0.0)]),
         runk([(184, C1, 0.0), (195, add(C1, rd, -0.5), 2.0), (205, DD, 0.3), (210, DD, 0.0)]),
         runk([(210, DD, 0.0), (300, DD, 0.0)]),
         runk([(300, DD, 0.0), (318, add(DD, rd, -0.75), 1.7), (336, E, 0.2), (342, E, 0.0), (DUR, E, 0.0)]))
# pass-and-cut: after the pass O2 cuts to the right block (6.0-7.6 s), out of the follow camera's line of sight
O2B = (2.6, 3.2)
O2 = cat(runk([(0, O2P, 0.0), (180, O2P, 0.0)]), runk([(180, O2P, 0.0), (204, add(O2P, (0.48, -0.88), 2.4), 3.6), (228, O2B, 0.0)]), runk([(228, O2B, 0.0), (DUR, O2B, 0.0)]))


def track(anchors):
    out = []
    for k in sorted(anchors):
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
            {"type": "hold", "player": "O1", "from": S(F_DRIB1), "to": S(F_SHOT)},
            {"type": "shot", "player": "O1", "t0": S(F_SHOT), "t1": S(F_MAKE), "make": True, "three": False}]
    rimA = lambda p: round(math.atan2(rim[1] - p[1], rim[0] - p[0]), 4)
    actions = {"O1": [st(rimA(A), 0, 45), face("O2", 105, F_PASS1 + 4), {"type": "catchReady", "from": S(F_PASS1 - 14), "to": S(F_PASS1 + 6), "face": "O2"},
                      face(rimA(C1), 158, F_SHOT + 30), st(rimA(E), 336, DUR)],
               "O2": [face("O1", 0, DUR)]}
    return {"id": "realism-v3-1-onetake", "title": "Realism V3.1 one continuous take (TEST fixture): ready, accelerate, brake + cut, catch, pivot, one bounce, jump shot, land, defensive stance",
            "duration": S(DUR), "concept": "realism-v3-1-test", "test": True, "squareUp": True, "handBallClear": True, "realism": 3,
            "source": "E2A synthetic test fixture (brief Realism V3.1 sec. 8), no real play copied",
            "players": [{"id": "O1", "team": "O", "role": "Test athlete: every phase of the one-take"},
                        {"id": "O2", "team": "O", "role": "Passer at the top of the key (in front of the cut)"}],
            "tracks": {"O1": track(O1), "O2": track(O2)}, "ball": ball, "actions": actions, "screens": [],
            "marks": {"ready": 0, "accelerate": 1.5, "plant": 3.28, "pass": S(F_PASS0), "catch": S(F_PASS1), "pivot": 5.3, "bounce": S(F_DRIB0),
                      "gather": S(F_DRIB1), "takeoff": 7.95, "release": S(F_SHOT), "land": 8.58, "make": S(F_MAKE), "backpedal": 10.0, "stance": 11.44, "end": S(DUR)}}


if __name__ == "__main__":
    s = spec()
    json.dump(s, open(os.path.join(D, "realism-v3-1-onetake.spec.json"), "w"), indent=1)
    json.dump(s, open(os.path.join(T, "tactical", "plays", "realism-v3-1-onetake.json"), "w"), indent=1)
    print("built", s["id"], "C", C, "C1", C1, "D", DD, "E", E, "pull-up to rim", round(math.hypot(DD[0] - rim[0], DD[1] - rim[1]), 2), "m; pass",
          round(math.hypot(O2P[0] - C[0], O2P[1] - C[1]), 2), "m")
