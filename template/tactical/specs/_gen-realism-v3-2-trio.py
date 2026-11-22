#!/usr/bin/env python3
"""E2A Realism V3.2 (2026-11-22) — TEST fixture of the 3-player interaction (brief V3.2 sec. 13), never a social episode.
  O1  passer at the top of the key: triple threat facing O2, two-hand chest pass at 2.70 s, relaxed after
  O2  right side: V-cut (goes down 0.70 s, plants his LEFT foot at 1.433 s, cuts up to the wing), 1-2 stop catch at
      3.20 s, jump shot (release 4.80 s, make 5.80 s), lands and recovers
  X2  denies O2: reacts to the cut 0.25 s later (trails him down and up), closes out when the ball arrives: sprint
      then chop steps (4.10-4.60 s) to 0.95 m in front of O2 on the rim side, contest hand up through the release
Causality: X2's moves start AFTER O2's (0.25 s reaction), the closeout starts after the catch; the pass flight passes
above / outside X2 (checked by scripts/qc-realism-v32.mts: ball vs bodies).
  python3 tactical/specs/_gen-realism-v3-2-trio.py -> tactical/specs/realism-v3-2-trio.spec.json + tactical/plays/"""
import importlib.util, json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
_s = importlib.util.spec_from_file_location("v2", os.path.join(D, "_gen-chicago-v2.py"))
v2 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(v2)
S, runk, cat = v2.S, v2.runk, v2.cat
st = lambda f, a, b: {"type": "stance", "from": S(a), "to": S(b), "face": f}
face = lambda f, a, b: {"type": "face", "from": S(a), "to": S(b), "face": f}
DUR = 225  # 7.5 s
F_GO, F_PLANT, F_PASS0, F_CATCH, F_SHOT, F_MAKE = 21, 43, 81, 96, 144, 174
F_CO0, F_CO1 = 123, 138
O1P = (0.0, 8.2)
O2A, O2V, O2W, O2S = (4.6, 3.0), (3.9, 2.15), (5.3, 5.9), (5.35, 6.05)
rim = (0.0, 1.575)
dr = ((rim[0] - O2S[0]) / math.hypot(rim[0] - O2S[0], rim[1] - O2S[1]), (rim[1] - O2S[1]) / math.hypot(rim[0] - O2S[0], rim[1] - O2S[1]))
XC = (round(O2S[0] + dr[0] * 0.95, 3), round(O2S[1] + dr[1] * 0.95, 3))  # closeout spot
O1 = runk([(0, O1P, 0.0), (DUR, O1P, 0.0)])
O2 = cat(runk([(0, O2A, 0.0), (F_GO, O2A, 0.0)]),
         runk([(F_GO, O2A, 0.0), (F_PLANT, O2V, 0.6)]),
         runk([(F_PLANT, O2V, 0.6), (F_PLANT + 22, (4.55, 3.95), 3.6), (F_CATCH, O2W, 1.0), (F_CATCH + 6, O2S, 0.0)]),
         runk([(F_CATCH + 6, O2S, 0.0), (DUR, O2S, 0.0)]))
X2A = (3.85, 3.75)
X2 = cat(runk([(0, X2A, 0.0), (F_GO + 8, X2A, 0.0)]),
         runk([(F_GO + 8, X2A, 0.0), (F_PLANT + 9, (3.35, 2.95), 0.7)]),
         runk([(F_PLANT + 9, (3.35, 2.95), 0.7), (90, (4.1, 4.0), 2.6), (F_CO0, (4.45, 4.95), 1.4)]),
         runk([(F_CO0, (4.45, 4.95), 1.4), (F_CO1, XC, 0.0)]),
         runk([(F_CO1, XC, 0.0), (DUR, XC, 0.0)]))


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
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": S(F_PASS0)},
            {"type": "pass", "from": "O1", "to": "O2", "t0": S(F_PASS0), "t1": S(F_CATCH)},
            {"type": "hold", "player": "O2", "from": S(F_CATCH), "to": S(F_SHOT)},
            {"type": "shot", "player": "O2", "t0": S(F_SHOT), "t1": S(F_MAKE), "make": True, "three": False}]
    rimA = lambda p: round(math.atan2(rim[1] - p[1], rim[0] - p[0]), 4)
    actions = {"O1": [face("O2", 0, DUR)],
               "O2": [face("O1", 0, F_GO), {"type": "catchReady", "from": S(F_CATCH - 14), "to": S(F_CATCH + 6), "face": "O1"}, face(rimA(O2S), F_CATCH + 6, DUR)],
               "X2": [st("O2", 0, F_GO + 8), face("O2", F_GO + 8, DUR)]}
    return {"id": "realism-v3-2-trio", "title": "Realism V3.2 3-player interaction (TEST fixture): V-cut, pass, catch, brake, jump shot, closeout",
            "duration": S(DUR), "concept": "realism-v3-2-test", "test": True, "squareUp": True, "handBallClear": True, "realism": 3,
            "source": "E2A synthetic test fixture (brief Realism V3.2 sec. 13), generic V-cut / closeout, no real play copied",
            "players": [{"id": "O1", "team": "O", "role": "Passer at the top of the key"},
                        {"id": "O2", "team": "O", "role": "Receiver: V-cut, catch, brake, jump shot"},
                        {"id": "X2", "team": "X", "role": "Defender of O2: trails the cut 0.25 s late, closes out", "guards": "O2"}],
            "tracks": {"O1": track(O1), "O2": track(O2), "X2": track(X2)}, "ball": ball, "actions": actions, "screens": [],
            "marks": {"cutGo": S(F_GO), "plant": S(F_PLANT), "pass": S(F_PASS0), "catch": S(F_CATCH), "release": S(F_SHOT), "make": S(F_MAKE),
                      "closeout": S(F_CO0), "closeoutEnd": S(F_CO1), "end": S(DUR)}}


if __name__ == "__main__":
    s = spec()
    json.dump(s, open(os.path.join(D, "realism-v3-2-trio.spec.json"), "w"), indent=1)
    json.dump(s, open(os.path.join(T, "tactical", "plays", "realism-v3-2-trio.json"), "w"), indent=1)
    print("built", s["id"], "closeout spot", XC)
