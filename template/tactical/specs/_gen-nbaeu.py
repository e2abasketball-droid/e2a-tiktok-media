#!/usr/bin/env python3
"""E2A NBA vs EUROLEAGUE (owner brief 2026-11-24 "4 RULES THAT CHANGE THE GAME"). Original E2A choreography.
Court: same world for both leagues (basket centre fixed at (0, 1.575)); only the painted lines change per play
(`courtRules`: 'fiba' = EuroLeague, FIBA OBR 2024 Art. 2; 'nba' = NBA Rule 1). See src/tactical/geometry.ts COURTS.
  nbaeu-three-el / -nba   the SAME shot from the SAME spot, 7.00 m straight out from the basket centre:
                          EuroLeague arc 6.75 m -> both feet outside = 3 points; NBA arc 7.24 m -> inside = 2 points.
  nbaeu-foul-el / -nba    X1 holds the driver's waist (a plain personal foul, no shot, no rough contact).
  nbaeu-walkoff           the player with his 5th (EuroLeague) foul walks to the bench (fouled out, not ejected).
  nbaeu-d3s-nba / -el     5 v 5, offence in control in its frontcourt (O1 dribbling at the top). X5 stands in the middle
                          of the lane, > 1 arm's length from every attacker, not guarding anyone, for 3+ s.
                          NBA Rule 10 Sec. VII: defensive 3 seconds -> technical foul (1 FT) and the offence keeps the ball.
                          EuroLeague (FIBA): no defensive 3-second rule; O5 stays OUTSIDE the lane (offensive 3 s applies
                          to both leagues and is not what is shown).
  python3 tactical/specs/_gen-nbaeu.py -> tactical/plays/nbaeu-*.json"""
import copy, json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
R4 = lambda v: round(v, 4)
BASKET = (0.0, 1.575)
SRC = "original E2A rule demonstration (NBA Rule 1, 3, 10 Sec. VII; FIBA OBR 2024 Art. 2, 8, 40; EuroLeague = FIBA rules)"
BASE = {"v33": "compile", "squareUp": True, "catchV2": 2, "handBallClear": True, "realism": 3}
LOOK = {"nba": {"paint": "rgba(28,62,140,0.9)", "word": "NBA", "ink": "rgba(255,255,255,0.88)"},
        "fiba": {"paint": "rgba(168,78,22,0.88)", "word": "EUROLEAGUE", "ink": "rgba(255,255,255,0.88)"}}


def still(x, y, dur):
    return [[0.0, R4(x), R4(y)], [R4(dur), R4(x), R4(y)]]


def run(pts, dur, t0=0.0, t1=None, dt=0.1):
    t1 = dur if t1 is None else t1
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    L = sum(segs)
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


heading = lambda a, b: math.atan2(b[1] - a[1], b[0] - a[0])


def play(pid, title, dur, players, tracks, ball, actions, marks, notes, rules, **kw):
    p = {"id": pid, "title": title, "branch": {"group": "nbaeu"}, "duration": dur, "concept": pid, "source": SRC, **BASE,
         "courtRules": rules, "courtLook": LOOK[rules], "players": players, "tracks": tracks, "ball": ball, "actions": actions,
         "screens": [], "marks": marks, "claims": [], "notes": notes}
    p.update(kw)
    return p


OUT = []
# ---------------------------------------------------------------- THREE: same spot, two line sets
SPOT_R = float(os.environ.get("NBAEU_SPOT_R", "7.05"))
SPOT = (0.0, BASKET[1] + SPOT_R)
DUR, T0, FL = 3.6, 1.3, 1.15
for rules, tag, pts in (("fiba", "el", "3 (outside the 6.75 m arc)"), ("nba", "nba", "2 (inside the 7.24 m arc)")):
    OUT.append(play(f"nbaeu-three-{tag}", f"SAME SHOT, {SPOT_R:.2f} m: {pts}", DUR,
                    [{"id": "O1", "team": "O", "role": "Shooter (same spot in both leagues)"}],
                    {"O1": still(*SPOT, DUR)},
                    [{"type": "hold", "player": "O1", "from": 0, "to": T0},
                     {"type": "shot", "player": "O1", "t0": T0, "t1": T0 + FL, "make": True, "H": 0.42}],
                    {"O1": [{"type": "face", "from": 0, "to": DUR, "face": R4(heading(SPOT, BASKET))}]},
                    {"release": T0, "make": T0 + FL, "end": DUR},
                    [f"Body centre {SPOT_R:.2f} m straight out from the basket centre (top of the key).",
                     f"Value: {pts}. QC: scripts/qc-nbaeu.mts measures both soles against both arcs."], rules))

# ---------------------------------------------------------------- FOUL (holding, from the 4 Rules play) on both courts
foul = json.load(open(os.path.join(T, "tactical", "plays", "rules4-foul.json")))
for rules, tag in (("fiba", "el"), ("nba", "nba")):
    p = copy.deepcopy(foul)
    p.update({"id": f"nbaeu-foul-{tag}", "concept": f"nbaeu-foul-{tag}", "branch": {"group": "nbaeu"}, "courtRules": rules, "courtLook": LOOK[rules], "source": SRC})
    OUT.append(p)

# ---------------------------------------------------------------- WALK-OFF: fouled out, walks to the bench
DUR = 4.0
X0 = (3.45, 6.55)
OUT.append(play("nbaeu-walkoff", "FOULED OUT: the player leaves the court (5th foul, EuroLeague)", DUR,
                [{"id": "X1", "team": "X", "role": "Fouled out: walks to the bench"}, {"id": "O1", "team": "O", "role": "Driver"}],
                {"X1": run([X0, (5.6, 7.6), (8.3, 8.6)], DUR, 0.25, DUR - 0.2), "O1": still(4.45, 5.75, DUR)},
                [{"type": "hold", "player": "O1", "from": 0, "to": DUR}],
                {"X1": [{"type": "face", "from": 0, "to": DUR, "face": R4(heading(X0, (8.3, 8.6)))}],
                 "O1": [{"type": "face", "from": 0, "to": DUR, "face": "X1"}]},
                {"walk": 0.25, "end": DUR}, ["Disqualified by the foul count (FIBA Art. 40), not ejected for conduct."], "fiba"))

# ---------------------------------------------------------------- DEFENSIVE 3 SECONDS, 5 v 5
DUR = 6.0
O = {"O1": (0.2, 8.9), "O2": (-3.9, 7.0), "O3": (3.9, 7.1), "O4": (-4.7, 1.3), "O5": (3.5, 1.5)}
X = {"X1": (0.15, 7.85), "X2": (-3.3, 6.25), "X3": (3.3, 6.35), "X4": (-3.95, 1.85), "X5": (0.0, 3.35)}
MOVE = {"X5": [(0.0, 3.35), (0.15, 3.55), (-0.1, 3.4)]}  # small shuffles in the middle of the lane, never near anyone
for rules, tag in (("nba", "nba"), ("fiba", "el")):
    tracks = {k: still(*v, DUR) for k, v in O.items()}
    tracks["O1"] = run([O["O1"], (0.6, 8.7), (0.2, 8.9)], DUR, 0.2, DUR - 0.3)
    for k, v in X.items():
        tracks[k] = still(*v, DUR)
    tracks["X5"] = run(MOVE["X5"], DUR, 0.4, DUR - 0.4)
    acts = {k: [{"type": "face", "from": 0, "to": DUR, "face": "O1"}] for k in O if k != "O1"}
    acts["O1"] = [{"type": "face", "from": 0, "to": DUR, "face": R4(heading(O["O1"], BASKET))}]
    for k in X:
        acts[k] = [{"type": "stance", "from": 0, "to": DUR, "face": "O1" if k in ("X1", "X5") else {"X2": "O2", "X3": "O3", "X4": "O4"}[k]}]
    OUT.append(play(f"nbaeu-d3s-{tag}", "DEFENSIVE 3 SECONDS: X5 in the lane, not guarding anyone, offence in control in the frontcourt", DUR,
                    [{"id": k, "team": "O", "role": r} for k, r in (("O1", "Ball handler, top"), ("O2", "Right wing"), ("O3", "Left wing"), ("O4", "Corner"), ("O5", "Short corner, OUTSIDE the lane"))] +
                    [{"id": k, "team": "X", "role": r, **({"guards": "O" + k[1]} if k != "X5" else {})} for k, r in (("X1", "On the ball"), ("X2", "Guards O2"), ("X3", "Guards O3"), ("X4", "Guards O4"), ("X5", "In the lane, guarding nobody"))],
                    tracks,
                    [{"type": "hold", "player": "O1", "from": 0, "to": DUR, "dribble": True, "hand": 1}],
                    acts, {"count0": 1.0, "count3": 4.0, "end": DUR},
                    ["Offence in control of the ball in its frontcourt (O1 dribbling, no shot).",
                     "X5 > 1 m (arm's length) from every attacker for the whole play; O5 outside the lane.",
                     "NBA: count 1-2-3 from 1.0 s -> defensive 3 seconds (technical foul, 1 FT, offence keeps the ball).",
                     "EuroLeague: same picture, no defensive 3-second rule."], rules))

for p in OUT:
    json.dump(p, open(os.path.join(T, "tactical", "plays", p["id"] + ".json"), "w"), indent=1)
    print(p["id"], p["duration"])
# arm's-length check for X5 (track level; the body QC is scripts/qc-nbaeu.mts)
d = min(math.dist(X["X5"], o) for o in O.values())
print("X5 nearest attacker (m)", round(d, 2), "| O5 outside lane:", abs(O["O5"][0]) > 2.45)
