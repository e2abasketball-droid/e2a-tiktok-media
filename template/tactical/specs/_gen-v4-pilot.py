#!/usr/bin/env python3
"""V4 shadow pilot, 16 Nov (owner brief 2026-11-14 16:52Z): the 4 package concepts as executable plays.
Original E2A plays built from standard FIBA/European half-court concepts (generic coaching knowledge, no copied
diagram). Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres.

  S01 v4-horns-twist      execution       horns: first ball screen is switched, the other big re-screens the
                                          switched big ("twist") and the guard turns the corner to the rim
  S02 v4-ice-contain      defensive_read  side ball screen ICED: X1 jumps to the top side, X5 drops to the
                                          baseline side in time, the ball goes back out (no shot)
  S03 v4-ice-reject       counter         same setup, the guard rejects BEFORE the big has dropped: baseline layup
  S04 v4-corner-help      challenge       baseline drive, the corner defender rotates to the rim: kick, corner three
Writes tactical/specs/v4-*.spec.json; build each with scripts/build-play.mts."""
import json, os

D = os.path.dirname(os.path.abspath(__file__))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
stance = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (standard FIBA/European half-court concept, generic coaching knowledge)"


def horns_twist():
    players = [P("O1", "O", "Point guard"), P("O2", "O", "Left corner"), P("O3", "O", "Right corner"),
               P("O4", "O", "Left elbow big: the twist screener"), P("O5", "O", "Right elbow big: first ball screen"),
               P("X1", "X", "On the ball", "O1"), P("X2", "X", "Left corner", "O2"), P("X3", "X", "Right corner", "O3"),
               P("X4", "X", "On the twist screener", "O4"), P("X5", "X", "On the first screener (switches)", "O5")]
    start = {"O1": [0.0, 9.2], "X1": [0.0, 8.3], "O4": [-2.4, 5.9], "X4": [-1.9, 5.2], "O5": [2.4, 5.9], "X5": [1.9, 5.2],
             "O2": [-6.85, 1.2], "X2": [-5.8, 1.9], "O3": [6.85, 1.2], "X3": [5.8, 1.9]}
    legs = {
        "O5": [{"at": 0.0, "to": [0.85, 8.45], "dur": 1.0}, {"at": 1.45, "via": [[2.1, 7.0]], "to": [2.3, 4.6], "speed": 3.6}],
        "O1": [{"at": 1.05, "via": [[1.3, 9.45]], "to": [3.1, 8.5], "speed": 4.2},
               {"at": 2.75, "via": [[2.15, 9.05], [0.55, 7.6], [-0.35, 4.6]], "to": [-0.45, 2.75], "speed": 6.0}],
        "X1": [{"at": 1.15, "to": [0.3, 7.5], "speed": 3.0}, {"at": "+0.05", "via": [[0.7, 6.3]], "to": [1.6, 4.0], "speed": 3.6}],
        "X5": [{"at": 1.0, "via": [[2.6, 6.6]], "to": [2.75, 7.75], "speed": 3.8}, {"at": 3.0, "via": [[2.4, 6.9]], "to": [0.6, 5.0], "speed": 4.4}],
        "O4": [{"at": 0.8, "via": [[-1.0, 7.0], [0.0, 8.5], [1.0, 8.75]], "to": [2.0, 7.95], "speed": 5.2}],
        "X4": [{"at": 1.0, "via": [[-0.4, 6.2], [0.6, 6.7]], "to": [1.0, 7.2], "speed": 4.2}, {"at": 4.2, "to": [0.3, 6.2], "speed": 3.0}],
        "O2": [], "O3": [], "X2": [], "X3": [],
    }
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": 4.85, "dribble": True},
            {"type": "layup", "player": "O1", "t0": 4.85, "t1": 5.25, "make": True}]
    marks = {"start": 0, "screen1": 1.05, "switch": 2.1, "twist": 2.8, "turn": 3.2, "finish": 4.85, "make": 5.25, "end": 6.4}
    acts = {"O5": [{"type": "screen", "from": 1.0, "to": 1.4, "face": "X1"}],
            "O4": [{"type": "screen", "from": 2.75, "to": 3.35, "face": "X5"}, {"type": "celebrate", "from": 5.5, "to": 6.2}],
            "X2": [stance("O1", 0, 6.4)], "X3": [stance("O1", 0, 6.4)], "X1": [stance("O1", 0, 1.1)],
            "X5": [stance("O1", 1.9, 3.0)], "X4": [stance("O1", 2.7, 4.2)]}
    claims = [
        {"type": "near", "a": "O5", "b": "X1", "at": "screen1", "max": 1.0, "says": "Five screens the guard's defender."},
        {"type": "near", "a": "X5", "b": "O1", "at": "switch", "max": 1.6, "says": "The defence switches it: a big on the guard."},
        {"type": "near", "a": "O4", "b": "X5", "at": "twist", "max": 0.95, "says": "Four sets the second screen on the switched big."},
        {"type": "far", "a": "X5", "b": "O1", "at": "finish", "min": 2.0, "says": "The big is caught on the second screen."},
        {"type": "near_rim", "player": "O1", "at": "finish", "max": 1.5, "says": "The guard turns the corner to the rim."},
        {"type": "order", "marks": ["screen1", "switch", "twist", "turn", "finish"], "says": "screen, switch, twist, finish"}]
    return {"id": "v4-horns-twist", "title": "Horns twist: the second screen beats the switch", "duration": 6.4,
            "concept": "horns-twist", "source": SRC,
            "notes": ["Horns: both bigs at the elbows. O5 screens X1, the defence switches (X5 on O1, X1 on O5).",
                      "O4 comes across and screens the switched big X5 the other way (twist).",
                      "O1 turns back to the middle around O4 and finishes at the rim before help arrives."],
            "players": players, "start": start, "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims}


def ice(kind):
    players = [P("O1", "O", "Ball handler, right wing"), P("O2", "O", "Left corner"), P("O3", "O", "Left wing"),
               P("O4", "O", "Top, left slot"), P("O5", "O", "Side ball screener"),
               P("X1", "X", "On the ball: ICE (jumps to the top side)", "O1"), P("X2", "X", "Left corner", "O2"),
               P("X3", "X", "Left wing", "O3"), P("X4", "X", "Top", "O4"), P("X5", "X", "On the screener: drops to the baseline side", "O5")]
    start = {"O1": [5.5, 6.8], "X1": [4.9, 6.0], "O5": [2.2, 5.6], "X5": [1.8, 4.8], "O4": [-1.8, 8.8], "X4": [-1.4, 7.8],
             "O3": [-5.2, 6.4], "X3": [-4.5, 5.6], "O2": [-6.85, 1.2], "X2": [-5.8, 1.9]}
    legs = {"O5": [{"at": 0.0, "to": [4.55, 7.65], "dur": 1.0}],
            "X1": [{"at": 0.55, "to": [5.0, 6.95], "speed": 2.2}],
            "O4": [], "X4": [{"at": 0.8, "to": [0.2, 7.2], "speed": 2.0}], "O3": [], "X3": [], "O2": [], "X2": []}
    acts = {"X2": [stance("O1", 0, 5.0)], "X3": [stance("O1", 0, 5.0)], "X4": [stance("O1", 0, 5.0)],
            "X1": [stance("O1", 0, 1.6)]}
    if kind == "contain":
        legs["O1"] = [{"at": 1.25, "via": [[6.1, 5.4]], "to": [5.9, 3.65], "speed": 4.2}]
        legs["X5"] = [{"at": 0.6, "to": [4.55, 3.15], "speed": 3.6}]
        legs["X1"] += [{"at": 1.55, "via": [[6.35, 5.6]], "to": [6.45, 4.55], "speed": 4.0}]
        legs["O5"] += [{"at": 2.3, "to": [3.4, 8.6], "speed": 3.0}]
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": 3.25, "dribble": True},
                {"type": "pass", "from": "O1", "to": "O5", "t0": 3.25, "t1": 3.85, "style": "chest"},
                {"type": "hold", "player": "O5", "from": 3.85, "to": 5.0}]
        marks = {"start": 0, "screen": 1.05, "ice": 1.2, "baseline": 1.6, "contain": 2.75, "pass": 3.25, "catch": 3.85, "end": 5.0}
        acts["O5"] = [{"type": "screen", "from": 1.05, "to": 2.2, "face": "X1"}]
        acts["X5"] = [stance("O1", 1.6, 5.0)]
        claims = [
            {"type": "near", "a": "X1", "b": "O5", "at": "ice", "max": 1.2, "says": "The guard's defender jumps to the top: the screen is taken away."},
            {"type": "far", "a": "O1", "b": "O5", "at": "contain", "min": 3.0, "says": "The guard can't use the screen; he goes baseline."},
            {"type": "near", "a": "X5", "b": "O1", "at": "contain", "max": 1.6, "says": "The big is already on the baseline side, waiting."},
            {"type": "order", "marks": ["screen", "ice", "baseline", "contain", "pass"], "says": "ice, baseline, contain, ball out"}]
        return {"id": "v4-ice-contain", "title": "ICE the side ball screen: the big is waiting on the baseline", "duration": 5.0,
                "concept": "ice-side-pnr", "source": SRC,
                "notes": ["Side ball screen on the right wing. X1 jumps to the top side (ICE): O1 cannot use the screen.",
                          "X5 drops to the baseline side in time; X1 trails; O1 is contained and passes back out to O5."],
                "players": players, "start": start, "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims}
    legs["O1"] = [{"at": 1.15, "via": [[6.15, 5.2], [4.6, 2.9]], "to": [1.05, 2.35], "speed": 6.2}]
    legs["X5"] = [{"at": 0.0, "to": [3.7, 6.7], "speed": 2.6}, {"at": 1.9, "via": [[3.9, 4.6]], "to": [2.8, 3.55], "speed": 4.2}]
    legs["X1"] += [{"at": 1.45, "via": [[6.5, 5.2]], "to": [5.2, 3.6], "speed": 4.6}]
    legs["O5"] += [{"at": 2.4, "to": [3.6, 8.6], "speed": 3.0}]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": 3.05, "dribble": True},
            {"type": "layup", "player": "O1", "t0": 3.05, "t1": 3.45, "make": True}]
    marks = {"start": 0, "screen": 1.05, "ice": 1.1, "reject": 1.15, "beat": 1.9, "finish": 3.05, "make": 3.45, "end": 4.8}
    acts["O5"] = [{"type": "screen", "from": 1.05, "to": 2.35, "face": "X1"}]
    acts["X5"] = [stance("O5", 0.6, 1.9)]
    acts["O1"] = [{"type": "celebrate", "from": 3.7, "to": 4.6}]
    claims = [
        {"type": "near", "a": "X1", "b": "O5", "at": "ice", "max": 1.2, "says": "They ICE the screen."},
        {"type": "far", "a": "X5", "b": "O1", "at": "beat", "min": 2.0, "says": "The big is still up with the screener: he has not dropped yet."},
        {"type": "far", "a": "X5", "b": "O1", "at": "finish", "min": 1.0, "says": "The big arrives late."},
        {"type": "near_rim", "player": "O1", "at": "finish", "max": 1.5, "says": "Baseline, before the big gets there: layup."},
        {"type": "order", "marks": ["screen", "ice", "reject", "beat", "finish"], "says": "ice, reject, baseline layup"}]
    return {"id": "v4-ice-reject", "title": "Counter to ICE: reject the screen before the big drops", "duration": 4.8,
            "concept": "reject-vs-ice", "source": SRC,
            "notes": ["Same setup as v4-ice-contain. X1 jumps to the top (ICE), but X5 has stepped up with the screener.",
                      "O1 rejects at once, baseline, before X5 can drop: the lane is open for the layup."],
            "players": players, "start": start, "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims}


def corner_help():
    players = [P("O1", "O", "Driver, right slot"), P("O2", "O", "Left corner"), P("O3", "O", "Right corner shooter"),
               P("O4", "O", "Left slot"), P("O5", "O", "Big, left block"),
               P("X1", "X", "On the driver", "O1"), P("X2", "X", "Left corner", "O2"), P("X3", "X", "Right corner: the helper", "O3"),
               P("X4", "X", "Left slot", "O4"), P("X5", "X", "On the big", "O5")]
    start = {"O1": [3.4, 7.6], "X1": [3.0, 6.8], "O3": [6.85, 1.2], "X3": [5.9, 1.9], "O2": [-6.85, 1.2], "X2": [-5.8, 1.9],
             "O4": [-3.0, 7.8], "X4": [-2.5, 6.9], "O5": [-2.1, 2.6], "X5": [-1.5, 2.2]}
    legs = {"O1": [{"at": 0.5, "via": [[3.75, 6.0]], "to": [2.35, 3.45], "speed": 5.6}],
            "X1": [{"at": 0.75, "via": [[3.05, 5.6]], "to": [3.05, 4.6], "speed": 4.4}],
            "X3": [{"at": 1.15, "to": [1.35, 2.3], "speed": 5.2}, {"at": 2.55, "to": [5.0, 1.7], "speed": 5.4}],
            "X5": [{"at": 1.3, "to": [-0.9, 2.3], "speed": 2.0}],
            "O2": [], "O3": [], "O4": [], "O5": [], "X2": [], "X4": []}
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": 2.2, "dribble": True},
            {"type": "pass", "from": "O1", "to": "O3", "t0": 2.2, "t1": 2.75, "style": "chest"},
            {"type": "hold", "player": "O3", "from": 2.75, "to": 3.05},
            {"type": "shot", "player": "O3", "t0": 3.05, "t1": 4.1, "make": True}]
    marks = {"start": 0, "drive": 0.5, "help": 1.9, "decision": 2.1, "kick": 2.2, "catch": 2.75, "release": 3.05, "make": 4.1, "end": 5.6}
    acts = {"X2": [stance("O1", 0, 5.6)], "X4": [stance("O1", 0, 5.6)], "X5": [stance("O1", 0, 5.6)], "X3": [stance("O1", 1.9, 2.55)],
            "O3": [{"type": "celebrate", "from": 4.3, "to": 5.4}]}
    claims = [
        {"type": "near", "a": "X3", "b": "O1", "at": "decision", "max": 1.6, "says": "The corner defender comes to stop the drive."},
        {"type": "far", "a": "X3", "b": "O3", "at": "decision", "min": 4.5, "says": "The help leaves the corner shooter."},
        {"type": "behind_arc", "player": "O3", "at": "release", "says": "Kick: the corner three."},
        {"type": "open", "player": "O3", "at": "release", "min": 1.8, "says": "The closeout is late."},
        {"type": "order", "marks": ["drive", "help", "decision", "kick", "catch", "release", "make"], "says": "drive, help, kick, three"}]
    return {"id": "v4-corner-help", "title": "What would you do? The corner help comes: kick", "duration": 5.6,
            "concept": "wwyd-corner-help", "source": SRC,
            "notes": ["O1 drives from the right slot toward the rim.", "X3 leaves the corner to stop the drive.",
                      "Read: stopped help feet = kick. O1 kicks to O3, who shoots the corner three before X3 recovers."],
            "players": players, "start": start, "legs": legs, "ball": ball, "marks": marks, "actions": acts, "claims": claims}


if __name__ == "__main__":
    for s in (horns_twist(), ice("contain"), ice("reject"), corner_help()):
        with open(os.path.join(D, f"{s['id']}.spec.json"), "w") as f:
            json.dump(s, f, indent=1)
        print("wrote", s["id"])
