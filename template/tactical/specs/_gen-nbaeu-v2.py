#!/usr/bin/env python3
"""NBA vs EuroLeague V2 (2026-11-24): empty-court plays for the scoreboard section (before the tip: no live ball on
court, so the game clocks can honestly sit at Q1 12:00 / 10:00). One hidden ball holder 'R' stands far behind the camera
(the shot hides him); nothing else on the floor. Same court identities as nbaeu-* (NBA Rule 1 / FIBA lines).
  python3 tactical/specs/_gen-nbaeu-v2.py -> tactical/plays/nbaeu-empty-{nba,el}.json"""
import json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
LOOK = {"nba": {"paint": "rgba(28,62,140,0.9)", "word": "NBA", "ink": "rgba(255,255,255,0.88)"},
        "fiba": {"paint": "rgba(168,78,22,0.88)", "word": "EUROLEAGUE", "ink": "rgba(255,255,255,0.88)"}}
for lg, rules in (("nba", "nba"), ("el", "fiba")):
    dur = 8.0
    p = {"id": f"nbaeu-empty-{lg}", "title": f"Empty {lg.upper()} court before the tip (scoreboard background)", "branch": {"group": "nbaeu"},
         "duration": dur, "concept": f"nbaeu-empty-{lg}", "source": "original E2A background (no action)", "v33": "compile", "realism": 3,
         "courtRules": rules, "courtLook": LOOK[rules],
         "players": [{"id": "R", "team": "O", "role": "hidden ball holder far behind the camera"}],
         "tracks": {"R": [[0.0, 0.0, 34.0], [dur, 0.0, 34.0]]},
         "ball": [{"type": "hold", "player": "R", "from": 0, "to": dur}], "actions": {"R": []},
         "screens": [], "marks": {}, "claims": [], "notes": ["Shots must hide R."]}
    json.dump(p, open(os.path.join(T, "tactical", "plays", f"nbaeu-empty-{lg}.json"), "w"), indent=1)
print("ok")

# ---------------------------------------------------------------- V3 (2026-11-24): EuroLeague drive, the big protects the rim
# Same 5 v 5 start as nbaeu-d3s-el. O1 drives middle, X5 (still in the lane: legal in EuroLeague, no defensive 3 s)
# steps up and contests with verticality, the wings X2 / X3 sink to help; O1 stops and kicks out to O2, X2 closes out.
# Offensive 3 s is not involved (O1 is in the lane < 1.5 s, driving). Motion is motivated by the ball, nothing random.
import math as _m
R4 = lambda v: round(v, 4)


def _run(pts, dur, t0, t1, dt=0.1):
    segs = [_m.dist(a, b) for a, b in zip(pts, pts[1:])]
    L = sum(segs) or 1e-9
    out, t = [], 0.0
    while t <= dur + 1e-9:
        u = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
        s = L * (10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5)
        acc, p = 0.0, pts[-1]
        for (a, b), sl in zip(zip(pts, pts[1:]), segs):
            if s <= acc + sl or sl == 0:
                k = 0 if sl == 0 else (s - acc) / sl
                p = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
                break
            acc += sl
        out.append([R4(t), R4(p[0]), R4(p[1])])
        t += dt
    return out


def _chain(dur, *legs):
    """legs = (pts, t0, t1) in order; holds between legs"""
    out = []
    for t in [round(i * 0.1, 4) for i in range(int(round(dur / 0.1)) + 1)]:
        p = legs[0][0][0]
        for pts, t0, t1 in legs:
            if t >= t0:
                p = dict((r[0], (r[1], r[2])) for r in _run(pts, dur, t0, t1))[t] if True else p
        out.append([t, R4(p[0]), R4(p[1])])
    return out


OFF = 1.3   # O1 sizes up the defence at the top for 1.3 s first (lets the scene run at real speed under the voice)
DUR = 5.4 + OFF
BASKET = (0.0, 1.575)
src = json.load(open(os.path.join(T, "tactical", "plays", "nbaeu-d3s-el.json")))
p = json.loads(json.dumps(src))
st = lambda xy: [[0.0, xy[0], xy[1]], [DUR, xy[0], xy[1]]]
O = {"O1": (0.2, 8.9), "O2": (-3.9, 7.0), "O3": (3.9, 7.1), "O4": (-4.7, 1.3), "O5": (3.5, 1.5)}
X = {"X1": (0.15, 7.85), "X2": (-3.3, 6.25), "X3": (3.3, 6.35), "X4": (-3.95, 1.85), "X5": (0.0, 3.35)}
tr = {k: st(v) for k, v in {**O, **X}.items()}
tr["O1"] = _chain(DUR, ([O["O1"], (-0.75, 7.0), (-0.45, 5.2)], 0.9 + OFF, 2.35 + OFF))
tr["X1"] = _chain(DUR, ([X["X1"], (0.75, 6.9), (0.85, 5.95)], 0.85 + OFF, 2.45 + OFF))
tr["X5"] = _chain(DUR, ([X["X5"], (0.2, 3.95)], 1.55 + OFF, 2.3 + OFF))
tr["X2"] = _chain(DUR, ([X["X2"], (-2.55, 5.75)], 1.2 + OFF, 2.3 + OFF), ([(-2.55, 5.75), (-3.35, 6.45)], 3.55 + OFF, 4.3 + OFF))
tr["X3"] = _chain(DUR, ([X["X3"], (2.6, 5.85)], 1.2 + OFF, 2.3 + OFF))
p.update({"id": "nbaeu-drive-el", "concept": "nbaeu-drive-el", "duration": DUR,
          "title": "EuroLeague: the big stays in the lane (legal), O1 drives, X5 protects the rim, kick-out",
          "tracks": tr,
          "ball": [{"type": "hold", "player": "O1", "from": 0, "to": 2.45 + OFF, "dribble": True, "hand": 1},
                   {"type": "hold", "player": "O1", "from": 2.45 + OFF, "to": 3.35 + OFF, "pocket": True},
                   {"type": "pass", "from": "O1", "to": "O2", "t0": 3.35 + OFF, "t1": 3.9 + OFF, "style": "chest"},
                   {"type": "hold", "player": "O2", "from": 3.9 + OFF, "to": DUR, "pocket": True}],
          "marks": {"drive": 0.9 + OFF, "stop": 2.45 + OFF, "contest": 2.2 + OFF, "pass": 3.35 + OFF, "catch": 3.9 + OFF, "end": DUR},
          "notes": ["FIBA / EuroLeague: no defensive 3-second rule; X5 may stay in the lane and protect the rim.",
                    "Offensive 3 s not involved: O1 is in the lane < 1.5 s and is driving; O5 stays outside the lane."]})
acts = p["actions"]
acts["O1"] = [{"type": "face", "from": 0, "to": DUR, "face": R4(_m.atan2(BASKET[1] - 8.9, BASKET[0] - 0.2))}]
acts["O2"] = [{"type": "face", "from": 0, "to": 3.45 + OFF, "face": "O1"}, {"type": "catchReady", "from": 3.45 + OFF, "to": 3.9 + OFF, "face": "O1"}]
acts["X5"] = [{"type": "stance", "from": 0, "to": 2.2 + OFF, "face": "O1"}, {"type": "contest", "from": 2.2 + OFF, "to": 3.2 + OFF},
              {"type": "stance", "from": 3.25 + OFF, "to": DUR, "face": "O1"}]
acts["X2"] = [{"type": "stance", "from": 0, "to": 3.5 + OFF, "face": "O1"}, {"type": "closeout", "from": 3.55 + OFF, "to": 4.3 + OFF},
              {"type": "stance", "from": 4.35 + OFF, "to": DUR, "face": "O2"}]
acts["X3"] = [{"type": "stance", "from": 0, "to": DUR, "face": "O1"}]
acts["X1"] = [{"type": "stance", "from": 0, "to": DUR, "face": "O1"}]
json.dump(p, open(os.path.join(T, "tactical", "plays", "nbaeu-drive-el.json"), "w"), indent=1)
print("drive ok")
