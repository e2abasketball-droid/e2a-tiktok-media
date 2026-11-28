#!/usr/bin/env python3
"""E2A BASKETBALL IQ 02 - BEAT THE BLITZ (owner master directive 2026-11-27 22:14Z).
Builds the ENGINE play tactical/plays/iq02-beat-the-blitz.json from the CANONICAL owner file
tactical/iq02/basketball_iq_02_blitz_short_roll.json. K0..K5 are reproduced exactly (waypoints at the keyframe times);
only the 1.2 s pre-roll before K0, the subtle stance shifts of the four static players and the outcome after K5 are
E2A additions (listed in the canonical file under e2a_additions).
Coordinates: owner x -> engine x = -x; engine t = owner t + 1.2.
  python3 tactical/specs/_gen-iq02.py        (then: python3 ../tools/iq_play_validate.py ...)"""
import sys
import json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
CAN = json.load(open(os.path.join(T, "tactical", "iq02", "basketball_iq_02_blitz_short_roll.json")))
OFF = CAN["coordinates"]["engine_offset_s"]
KF = {k["k"]: k for k in CAN["keyframes"]}
KT = {k: v["t"] + OFF for k, v in KF.items()}          # engine times of the keyframes
K0 = KF["K0"]
E = lambda p: [round(-p[0], 3), round(p[1], 3)]       # owner -> engine
r3 = lambda x: round(x, 3)
DUR = 6.2


def kp(pid, k):
    """owner position of pid at keyframe k (players absent from a keyframe keep their K0 spot: the static four)"""
    return KF[k].get(pid, K0[pid])


def wp(t, p):
    return [r3(t), *E(p)]


def hold(t, p, dt=0.02):
    """two equal waypoints = a stop (splits the engine's spline runs)"""
    return [wp(t, p), wp(t + dt, p)]


def tracks():
    tr = {}
    # O1: dribbles into the ball screen (pre-roll), comes off it to K1, is pushed back by the trap (K2, K3), then stays
    tr["O1"] = [wp(0, [5.75, 10.30]), wp(KT["K0"], kp("O1", "K0")), *hold(KT["K1"], kp("O1", "K1")),
                wp(KT["K2"], kp("O1", "K2")), wp(KT["K3"], kp("O1", "K3")), wp(DUR, kp("O1", "K3"))]
    # O5: comes up from the elbow, SETS the screen (stationary 0.45 s before K0), short-rolls to the nail
    tr["O5"] = [wp(0, [2.45, 8.05]) + ["fly"], wp(0.75, kp("O5", "K0")), wp(KT["K0"], kp("O5", "K0")),
                wp(KT["K1"], kp("O5", "K1")), wp(KT["K2"], kp("O5", "K2")), wp(KT["K3"], kp("O5", "K3")),
                wp(KT["K4"], kp("O5", "K4")), wp(KT["K5"], kp("O5", "K5")), wp(DUR, kp("O5", "K5"))]
    # X1: follows O1 into the screen, then traps (small shuffles K0..K3)
    tr["X1"] = [wp(0, [5.45, 9.70]), wp(1.0, kp("X1", "K0")), wp(KT["K0"] + 0.05, kp("X1", "K0")),
                wp(KT["K1"], kp("X1", "K1")), wp(KT["K2"], kp("X1", "K2")), wp(KT["K3"], kp("X1", "K3")), wp(DUR, kp("X1", "K3"))]
    # X5: follows O5 up to the screen level, leaves him to blitz 0.05 s after K0, recovers after the outlet
    tr["X5"] = [wp(0, [2.6, 7.1]) + ["fly"], wp(0.85, kp("X5", "K0")), wp(KT["K0"] + 0.05, kp("X5", "K0")),
                wp(KT["K1"], kp("X5", "K1")), wp(KT["K2"], kp("X5", "K2")), wp(KT["K3"], kp("X5", "K3")),
                wp(KT["K4"], kp("X5", "K4")), wp(KT["K5"], kp("X5", "K5")), wp(5.45, [1.95, 6.70]), wp(DUR, [1.95, 6.70])]
    # X4: in help on O4; reacts to X5 leaving the roller (tag), steps into the paint as the outlet arrives (stops at K3,
    # the freeze), settles (K4), turns too late after the pass (K5 and after)
    tr["X4"] = [wp(0, [-3.62, 7.34]), wp(0.9, kp("X4", "K0")), wp(KT["K0"] + 0.25, kp("X4", "K0")),
                wp(KT["K1"], kp("X4", "K1")), wp(KT["K2"], kp("X4", "K2")), wp(KT["K3"], kp("X4", "K3")),
                wp(KT["K4"], kp("X4", "K4")), wp(KT["K5"], kp("X4", "K5")), wp(5.5, [0.0, 3.05]), wp(DUR, [0.0, 3.05])]
    # O4: weak-side wing, lifts a step (K1, K2), 45-degree cut behind X4 (K2 -> K5), lands under the rim
    tr["O4"] = [wp(0, [-5.05, 8.22]), wp(0.9, kp("O4", "K0")), wp(KT["K0"], kp("O4", "K0")),
                wp(KT["K1"], kp("O4", "K1")), wp(KT["K2"], kp("O4", "K2")), wp(KT["K3"], kp("O4", "K3")),
                wp(KT["K4"], kp("O4", "K4")), wp(KT["K5"], kp("O4", "K5")), wp(5.45, [-0.35, 1.25]), wp(DUR, [-0.35, 1.25])]
    # the static four: K0 spots, weight shifts <= 0.15 m (alive, not frozen)
    tr["O2"] = [wp(0, [6.80, 2.50]), wp(1.4, kp("O2", "K0")), wp(DUR, kp("O2", "K0"))]
    tr["O3"] = [wp(0, [-6.80, 2.62]), wp(1.4, kp("O3", "K0")), wp(4.3, kp("O3", "K0")), wp(4.9, [-6.78, 2.45]), wp(DUR, [-6.78, 2.45])]
    tr["X2"] = [wp(0, [6.00, 2.98]), wp(1.4, kp("X2", "K0")), wp(2.2, kp("X2", "K0")), wp(2.9, [5.82, 2.98]), wp(DUR, [5.82, 2.98])]
    tr["X3"] = [wp(0, [-6.00, 2.95]), wp(1.4, kp("X3", "K0")), wp(2.2, kp("X3", "K0")), wp(2.9, [-5.82, 2.98]),
                wp(4.35, [-5.82, 2.98]), wp(5.0, [-5.95, 2.80]), wp(DUR, [-5.95, 2.80])]
    return tr


ST = lambda f, a, b: {"type": "stance", "from": r3(a), "to": r3(b), "face": f}
FACE = lambda f, a, b: {"type": "face", "from": r3(a), "to": r3(b), "face": f}

M = {"start": 0.0, "screen": 0.75, "k0": KT["K0"], "blitz": KT["K0"] + 0.05, "outlet": KT["K1"], "k1": KT["K1"],
     "release1": 0.86 + OFF, "catch1": 1.45 + OFF, "faceup": 1.55 + OFF, "k2": KT["K2"], "freeze": KT["K3"], "decide": KT["K3"],
     "load": 2.32 + OFF, "release2": 2.48 + OFF, "catch2": 3.05 + OFF, "layup": 3.70 + OFF, "make": 3.70 + OFF + 0.45, "end": DUR}
M = {k: r3(v) for k, v in M.items()}


def play():
    acts = {
        "O1": [FACE("X1", 0, M["k0"]), FACE("O5", M["outlet"] - 0.1, M["release1"] + 0.2), FACE("X5", M["release1"] + 0.3, DUR)],
        "O5": [{"type": "screen", "from": 0.8, "to": M["k0"], "face": "X1"}, FACE("O1", M["k1"], M["catch1"])],
        "O4": [FACE("O1", 0, M["k2"]), {"type": "catchReady", "from": r3(M["release2"] - 0.05), "to": r3(M["catch2"] + 0.05), "face": "O5"},
               {"type": "celebrate", "from": r3(M["make"] + 0.25), "to": DUR}],
        "O2": [FACE("O1", 0, M["catch1"]), FACE("O5", M["catch1"], DUR)],
        "O3": [FACE("O1", 0, M["catch1"]), FACE("O5", M["catch1"], DUR)],
        "X1": [ST("O1", 0, DUR)],
        "X5": [ST("O5", 0, M["blitz"]), ST("O1", M["blitz"], M["catch1"] + 0.3), ST("O5", M["catch1"] + 0.35, DUR)],
        "X4": [ST("O1", 0, M["catch1"] - 0.2), ST("O5", M["catch1"] - 0.15, M["catch2"] + 0.1), ST("O4", M["catch2"] + 0.2, DUR)],
        "X3": [ST("O1", 0, M["catch1"]), ST("O5", M["catch1"], DUR)],
        "X2": [ST("O1", 0, M["catch1"]), ST("O5", M["catch1"], DUR)],
    }
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": M["outlet"], "dribble": True, "hand": -1},
            {"type": "hold", "player": "O1", "from": M["outlet"], "to": M["release1"], "hand": -1},
            {"type": "pass", "from": "O1", "to": "O5", "t0": M["release1"], "t1": M["catch1"], "style": "bounce", "ballistic": True, "eyes": 0.25},
            {"type": "hold", "player": "O5", "from": M["catch1"], "to": M["release2"]},
            {"type": "pass", "from": "O5", "to": "O4", "t0": M["release2"], "t1": M["catch2"], "style": "bounce", "ballistic": True,
             "lead": True, "eyes": 0.12},
            {"type": "hold", "player": "O4", "from": M["catch2"], "to": M["layup"]},
            {"type": "layup", "player": "O4", "t0": M["layup"], "t1": M["make"], "make": True}]
    claims = [
        {"type": "near", "a": "X1", "b": "O1", "at": "k1", "max": 1.6, "says": "They send TWO at the ball!"},
        {"type": "near", "a": "X5", "b": "O1", "at": "k1", "max": 1.6, "says": "They send TWO at the ball!"},
        {"type": "far", "a": "X5", "b": "O5", "at": "catch1", "min": 2.5, "says": "Your big catches the short roll. Four on three."},
        {"type": "near_rim", "player": "X4", "at": "freeze", "max": 2.8, "says": "He steps into the paint..."},
        {"type": "far", "a": "X4", "b": "O4", "at": "freeze", "min": 3.5, "says": "AND LOSES THE CUTTER!"},
        {"type": "near", "a": "X3", "b": "O3", "at": "freeze", "max": 1.2, "says": "Corner? (X3 is home)"},
        {"type": "near", "a": "X2", "b": "O2", "at": "freeze", "max": 1.2, "says": "(the strong-side corner is home too)"},
        {"type": "open", "player": "O4", "at": "catch2", "min": 2.0, "says": "THERE'S THE PASS!"},
        {"type": "order", "marks": ["screen", "k0", "blitz", "outlet", "release1", "catch1", "faceup", "freeze", "release2", "catch2", "layup", "make"],
         "says": "screen, blitz, outlet, short roll, freeze, pass, layup"}]
    players = [{"id": p["id"], "team": p["team"], "role": p["role"], **({"guards": p["guards"]} if "guards" in p else {})} for p in CAN["players"]]
    return {"id": "iq02-beat-the-blitz", "title": "Basketball IQ 02: Beat the Blitz (short roll 4 on 3, X4 helps, 45 cut)",
            "duration": DUR, "concept": "blitz-short-roll", "kitSet": "iq", "source": CAN["originality"], "squareUp": True, "catchV2": 2,
            "handBallClear": True, "v33": "compile", "realism": 3, "canonical": "tactical/iq02/basketball_iq_02_blitz_short_roll.json",
            "players": players, "tracks": tracks(), "ball": ball, "marks": M, "actions": acts, "claims": claims, "screens": [],
            "coords": {"system": "repo (engine)", "owner_to_engine": "x = -owner x, y = owner y, t = owner t + %.1f" % OFF,
                       "basket": [0, 1.575]},
            "notes": ["K0..K5 at engine times %s reproduced exactly from the canonical owner file." % {k: r3(v) for k, v in KT.items()},
                      "Pre-roll 0..1.2 s, the static four's weight shifts and the outcome after K5 are E2A additions."]}


def play_v2():
    """V2 (2026-11-28, E2A Motion Engine V4): SAME owner keyframes K0..K5 and ball events, with the motion layers the V1
    possession lacked. Tactical data changes (documented in docs/v2/02-root-cause-and-fixes.md):
      - X4 after K5: recovers toward the rim and contests late (V1: drifted 0.7 m at walking speed after the layup)
      - O4 after K5: the run ends at the layup landing (V1: kept travelling 0.5 m after the release)
      - layup event: left-hand finish off the right foot, banked off the glass (V1: rendered as a standing jump shot)
    Motion layers (compiled by realism-v3-3 with play.v4): trap stance X1/X5, help stance X4, O4 read + burst, O5 opens
    to the passer before the catch, faces up and reads X4, X4 late contest."""
    p = play()
    p["id"] = "iq02-beat-the-blitz-v2"
    p["v4"] = True
    tr = p["tracks"]
    tr["X4"] = tr["X4"][:-2] + [wp(5.5, [-0.1, 2.85]), wp(DUR, [-0.1, 2.85])]
    tr["O4"] = tr["O4"][:-2] + [wp(5.32, [-0.42, 1.38]), wp(DUR, [-0.42, 1.38])]
    A = p["actions"]
    tb = M["blitz"]
    A["X1"] = [ST("O1", 0, tb), {"type": "trap", "from": r3(tb + 0.05), "to": r3(M["release1"] + 0.12), "face": "O1"}, ST("O1", M["release1"] + 0.15, DUR)]
    A["X5"] = [ST("O5", 0, tb), {"type": "trap", "from": r3(tb + 0.12), "to": r3(M["release1"] + 0.12), "face": "O1"},
               ST("O1", M["release1"] + 0.15, M["catch1"] + 0.3), ST("O5", M["catch1"] + 0.35, DUR)]
    A["X4"] = [ST("O1", 0, M["catch1"] - 0.2), ST("O5", M["catch1"] - 0.15, M["freeze"] - 0.05),
               {"type": "help", "from": r3(M["freeze"] - 0.05), "to": r3(M["catch2"] + 0.05), "face": "O5"},
               ST("O4", M["catch2"] + 0.1, M["layup"] - 0.12),
               {"type": "contest", "from": r3(M["layup"] - 0.1), "to": r3(M["make"] + 0.15), "face": "O4"}, ST("O4", M["make"] + 0.2, DUR)]
    A["O5"] = [{"type": "screen", "from": 0.8, "to": M["k0"], "face": "X1"}, FACE("O1", M["k1"], M["catch1"]),
               FACE("rim", M["catch1"] + 0.12, M["release2"] - 0.22), FACE("O4", M["release2"] - 0.2, M["release2"] + 0.4)]
    for e in p["ball"]:
        if e["type"] == "layup":
            e["hand"] = -1                      # left hand: approach from the left side, ball on the side away from X4
            e["H"] = 0.45
            e["glass"] = [0.27, 3.42]           # engine x (the cutter's side of the square), height on the board
    rd = M["catch1"]                            # O5 catches: the read starts
    # O5's front pivot after the catch: from facing O1 (the passer) to facing the rim (engine coordinates)
    o5 = [-kp("O5", "K2")[0], kp("O5", "K2")[1]]; o1 = [-kp("O1", "K1")[0], kp("O1", "K1")[1]]
    a_pass = math.atan2(o1[1] - o5[1], o1[0] - o5[0]); a_rim = math.atan2(1.575 - o5[1], 0 - o5[0])
    PIV5 = r3(math.atan2(math.sin(a_rim - a_pass), math.cos(a_rim - a_pass)))
    p["v33extra"] = {
        "O5": [{"k": "open", "t0": r3(M["outlet"] + 0.15), "t1": r3(M["catch1"] - 0.32), "at": "O1", "max": 1.1},
               # the last 0.3 s: chest and hands square to the passer (catch facing the ball), then a front pivot to face up
               {"k": "open", "t0": r3(M["catch1"] - 0.32), "t1": r3(M["catch1"] + 0.1), "at": "O1", "max": 3.1},
               {"k": "pivot", "side": 1, "t0": r3(M["catch1"] + 0.14), "t1": r3(M["catch1"] + 0.62), "dyaw": PIV5},
               {"k": "look", "t": r3(M["outlet"] - 0.05), "at": "O1", "b": 0.2},
               {"k": "look", "t": r3(M["catch1"] + 0.3), "at": "X4", "b": 0.18},
               {"k": "look", "t": r3(M["release2"] - 0.45), "at": "O4", "b": 0.15}],
        "O4": [{"k": "look", "t": r3(rd - 0.55), "at": "X4", "b": 0.22},           # reads X4 leaving him
               {"k": "burst", "t": r3(rd + 0.02), "side": 1, "wide": 0.3},        # plants the right foot, explodes on the 45 cut
               {"k": "look", "t": r3(rd + 0.3), "at": "ahead", "b": 0.2},
               {"k": "look", "t": r3(M["release2"] - 0.35), "at": "O5", "b": 0.18}],
        "X4": [{"k": "step", "side": 0, "lift": 1.47, "land": 1.63, "f": 0.12, "l": -0.12, "h": 0.06, "heel": 0.0, "toeOff": 0.6},
               {"k": "step", "side": 1, "lift": 1.64, "land": 1.84, "f": 0.28, "l": 0.1, "h": 0.09, "heel": 0.05, "toeOff": 0.55},  # quick first steps of the sprint to the help (V2a: 3 long strides for 2 m)
               {"k": "step", "side": 0, "lift": 3.96, "land": 4.12, "f": 0.02, "l": -0.05, "h": 0.05, "toeOff": 0.2},   # two short steps back up
               {"k": "step", "side": 1, "lift": 4.14, "land": 4.3, "f": 0.02, "l": 0.05, "h": 0.05, "toeOff": 0.2},    # toward the ball (help -> show)
               {"k": "look", "t": r3(M["catch1"] - 0.6), "at": "O5", "b": 0.25},
               {"k": "look", "t": r3(M["release2"] + 0.05), "at": "ball", "b": 0.1},
               {"k": "look", "t": r3(M["catch2"] + 0.05), "at": "O4", "b": 0.12}],
    }
    p["v33still"] = {"X4": [[3.74, 4.42]], "O5": [[r3(M["catch1"] + 0.1), 3.44]]}      # X4 is set in the help spot: the body works over planted feet + 2 steps
    p["notes"] = p["notes"] + ["V2 (Motion Engine V4): see play_v2() in tactical/specs/_gen-iq02.py for every change."]
    return p


if __name__ == "__main__":
    if "--v2" in sys.argv:
        p = play_v2()
        out = os.path.join(T, "tactical", "plays", "iq02-beat-the-blitz-v2.json")
        json.dump(p, open(out, "w"), indent=1)
        print("wrote", out)
        sys.exit(0)
    p = play()
    out = os.path.join(T, "tactical", "plays", "iq02-beat-the-blitz.json")
    json.dump(p, open(out, "w"), indent=1)
    print("wrote", out, json.dumps(M))
