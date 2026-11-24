#!/usr/bin/env python3
"""E2A 1-3-1 ARROW PRESS ("presion en flecha"): three-quarter-court 1-3-1 trap that falls back into the half-court
1-3-1 zone (owner request 2026-11-24, companion of the 1-3-1 Zone Defense reel). FULL-COURT play (`court: 'full'`).
Numbering kept from the 1-3-1 zone reel: X1 point (top), X2 LEFT wing (repo x > 0), X3 RIGHT wing, X5 middle,
X4 safety (= the tail of the half-court zone). Offence attacks the near basket (y = 0); half court y = 14; the
offence's backcourt is y 14..28. Repo axes as in _gen-zone131.py (offence's LEFT = repo x > 0 = screen left).

Original E2A didactic choreography, one possession (no inbound shown: O1 has the ball after the throw-in):
  0.0-3.9  the arrow (X1 at the far free-throw line, X2-X5-X3 across half court, X4 deep). X1 shades O1's middle
           shoulder and turns him to the LEFT sideline; X2 gives ground, O1 crosses half court (~3.4 s) and X2 jumps
           the sideline: TRAP X1 + X2 in the half-court corner (sideline + half-court line = two extra defenders:
           backcourt rule). X5 slides to the ball-side middle lane, X3 sinks to read the cross-court pass to O3, X4
           shades to the ball side to guard the long pass up the sideline (O2).
  4.55     the ball ESCAPES: O1 picks up and throws an overhead pass over the trap to O4 flashing to the high middle.
  4.7-7.1  nobody chases: the five sprint back to the half-court 1-3-1 spots of the zone reel (X1 top, X2/X3 wings,
           X5 centre, X4 tail) while O4 dribbles to the top; the offence fills its half-court spots.
  python3 tactical/specs/_gen-arrow131.py -> tactical/plays/arrow131-press.json"""
import json, math, os, sys
from importlib import import_module

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, D)
Mover = import_module("_gen-horns-roll-pop").Mover

SRC = ("original E2A didactic choreography of the three-quarter-court 1-3-1 trapping press (point turns the ball to a "
       "sideline, ball-side wing traps just after half court, middle denies the middle, weak wing reads the cross-court "
       "pass, safety guards the long pass; on an escape the press sprints back into the 1-3-1 half-court zone). "
       "Coaching pages were not reachable from the render container on 2026-11-24 (network policy): rules follow "
       "standard 1-3-1 press teaching, NOT live-verified. FIBA court 28 x 15 m. No diagram, frame or track copied.")

ZONE = {"type": "1-3-1 press -> 1-3-1 zone", "variant": "three-quarter court arrow, sideline trap after half court",
        "areas": {"X1": "point: turns the ball to the sideline, never lets it go middle; traps from behind",
                  "X2": "left wing: gives ground, then jumps the sideline after half court (trap with X1)",
                  "X3": "right wing: sinks to read the cross-court pass",
                  "X5": "middle: takes away the middle lane",
                  "X4": "safety: the long pass up the sideline and the rim"}}

TRAP_T = 3.95
REL, CATCH = 4.55, 5.15
END = 8.2


def build():
    m = {}
    # ---- offence
    m["O1"] = Mover((1.2, 24.2)).hold(0.5).move(0.5, 3.9, [(2.6, 22.0), (4.6, 18.8), (5.8, 15.5), (6.1, 13.0)])
    m["O2"] = Mover((6.2, 19.0)).move(0.6, 3.0, [(6.35, 14.0), (6.4, 9.4)])
    m["O3"] = Mover((-5.8, 19.5)).move(0.8, 3.4, [(-6.0, 15.0), (-6.0, 11.0)])
    m["O4"] = Mover((-0.6, 17.5)).move(1.6, 3.4, [(-1.0, 13.0)]).move(4.15, 4.95, [(-0.6, 11.4)])
    m["O5"] = Mover((-1.6, 7.5)).move(0.5, 2.5, [(-1.2, 4.6)])
    # ---- the arrow
    m["X1"] = Mover((0.4, 22.4)).move(0.55, 3.95, [(1.3, 21.9), (3.15, 18.9), (4.6, 15.9), (5.25, 13.8)])
    m["X2"] = Mover((4.3, 15.4)).move(1.2, 2.85, [(4.9, 13.6)]).move(3.0, 3.85, [(6.5, 12.15)])
    m["X5"] = Mover((0.0, 15.6)).move(2.0, 3.9, [(2.3, 12.6)])
    m["X3"] = Mover((-4.3, 15.4)).move(2.2, 4.0, [(-2.9, 10.2)])
    m["X4"] = Mover((0.0, 8.0)).move(2.0, 3.8, [(3.9, 8.0)])
    # ---- the escape: everyone sprints back into the half-court 1-3-1 (spots of the zone reel)
    m["X5"].move(4.65, 6.9, [(0.6, 8.6), (0.0, 4.3)])
    m["X2"].move(4.7, 7.1, [(4.6, 8.4), (3.4, 5.2)])
    m["X4"].move(4.7, 6.8, [(1.4, 3.6), (0.0, 2.0)])
    m["X1"].move(4.85, 7.0, [(3.3, 11.6), (0.4, 8.2)])
    m["X3"].move(4.8, 6.8, [(-3.4, 5.2)])
    m["O4"].move(5.45, 6.6, [(0.3, 9.7)])
    m["O1"].move(5.2, 7.4, [(6.2, 9.5), (6.1, 6.2)])
    m["O2"].move(5.0, 6.8, [(6.88, 1.3)])
    m["O3"].move(5.0, 7.0, [(-6.1, 6.0)])
    m["O5"].move(5.3, 6.6, [(-2.6, 2.4)])
    for p in m.values():
        p.hold(END)
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": 3.9, "dribble": True},
            {"type": "hold", "player": "O1", "from": 3.9, "to": REL},
            {"type": "pass", "from": "O1", "to": "O4", "t0": REL, "t1": CATCH, "style": "overhead", "eyes": 0.35, "phased": True, "arc": 3.0},
            {"type": "hold", "player": "O4", "from": CATCH, "to": 5.45},
            {"type": "hold", "player": "O4", "from": 5.45, "to": 6.6, "dribble": True},
            {"type": "hold", "player": "O4", "from": 6.6, "to": END}]
    acts = {"X1": [{"type": "stance", "from": 0, "to": 3.2, "face": "O1"}, {"type": "closeout", "from": 3.2, "to": 4.8, "face": "O1"}, {"type": "stance", "from": 4.8, "to": END, "face": "ball"}],
            "X2": [{"type": "stance", "from": 0, "to": 3.2, "face": "ball"}, {"type": "closeout", "from": 3.2, "to": 4.7, "face": "O1"}, {"type": "stance", "from": 4.7, "to": END, "face": "ball"}],
            "X3": [{"type": "stance", "from": 0, "to": END, "face": "ball"}],
            "X4": [{"type": "stance", "from": 0, "to": END, "face": "ball"}],
            "X5": [{"type": "stance", "from": 0, "to": END, "face": "ball"}],
            "O1": [{"type": "face", "from": 3.9, "to": REL, "face": "O4"}],
            "O4": [{"type": "catchReady", "from": 4.2, "to": CATCH, "face": "O1"}, {"type": "face", "from": 6.6, "to": END, "face": 270}],
            "O2": [{"type": "face", "from": 0, "to": END, "face": "ball"}],
            "O3": [{"type": "face", "from": 0, "to": END, "face": "ball"}],
            "O5": [{"type": "face", "from": 0, "to": END, "face": "ball"}]}
    marks = {"start": 0, "go": 0.5, "halfCourt": 3.4, "jump": 3.2, "trap": TRAP_T, "release": REL, "escape": CATCH,
             "back": 4.7, "zone": 7.1, "end": END}
    claims = [
        {"type": "far", "a": "X1", "b": "X4", "at": "start", "min": 12.0, "says": "One at the point. One safety deep."},
        {"type": "near", "a": "X2", "b": "X3", "at": "start", "max": 9.0, "says": "Three across half court. (X2-X5-X3 line)"},
        {"type": "near", "a": "X1", "b": "O1", "at": "go", "max": 2.2, "says": "The point turns the ball to the sideline."},
        {"type": "near", "a": "X1", "b": "O1", "at": "trap", "max": 1.3, "says": "Trap! (X1 from behind)"},
        {"type": "near", "a": "X2", "b": "O1", "at": "trap", "max": 1.2, "says": "and the wing jumps. Trap!"},
        {"type": "far", "a": "X1", "b": "X2", "at": "trap", "min": 1.2, "says": "two trappers, two angles, no collision"},
        {"type": "order", "marks": ["halfCourt", "trap"], "says": "The ball crosses half court... and the wing jumps."},
        {"type": "far", "a": "X5", "b": "O1", "at": "trap", "min": 2.5, "says": "The middle takes away the middle (not a third trapper)"},
        {"type": "far", "a": "X3", "b": "O3", "at": "trap", "min": 2.5, "says": "The far wing reads the cross-court pass (in the lane, not on O3)"},
        {"type": "near", "a": "X4", "b": "O2", "at": "trap", "max": 3.5, "says": "The safety guards the long pass."},
        {"type": "order", "marks": ["release", "back", "zone"], "says": "Now the ball escapes. Don't chase it. Sprint back."},
    ]
    play = {
        "id": "arrow131-press", "title": "1-3-1 arrow press: sideline trap after half court, escape, back into the 1-3-1 zone",
        "duration": END, "concept": "press-1-3-1-arrow-to-zone", "source": SRC, "court": "full",
        "v33": "compile", "squareUp": True, "catchV2": 2, "handBallClear": True, "realism": 3,
        "players": [
            {"id": "O1", "team": "O", "role": "Ball handler: brings it up, gets trapped, escapes with an overhead pass"},
            {"id": "O2", "team": "O", "role": "Left sideline runner: the long pass up the line"},
            {"id": "O3", "team": "O", "role": "Right side: the cross-court target"},
            {"id": "O4", "team": "O", "role": "Middle: flashes to the high middle, receives the escape pass"},
            {"id": "O5", "team": "O", "role": "Deep post"},
            {"id": "X1", "team": "X", "role": "POINT: turns the ball to the sideline, traps from behind, then top of the zone"},
            {"id": "X2", "team": "X", "role": "LEFT WING: jumps the sideline after half court (trap), then left wing of the zone"},
            {"id": "X3", "team": "X", "role": "RIGHT WING: reads the cross-court pass, then right wing of the zone"},
            {"id": "X4", "team": "X", "role": "SAFETY: the long pass and the rim, then the tail of the zone"},
            {"id": "X5", "team": "X", "role": "MIDDLE: takes away the middle lane, then centre of the zone"},
        ],
        "zone": ZONE,
        "tracks": {pid: p.wp for pid, p in m.items()},
        "ball": ball, "actions": acts, "screens": [], "marks": marks, "claims": claims,
        "notes": ["Three-quarter-court 1-3-1 press only; the trap is legal and needs no steal to succeed (no steal shown).",
                  "The escape outcome belongs to this execution: the lesson is the recovery into the half-court zone."],
    }
    # sanity: O1 crossed half court before the trap closes (half-court line = extra defender)
    y = m["O1"].at(TRAP_T)[1]
    assert y < 14.0, y
    cross = next(w[0] for w in m["O1"].wp if w[2] < 14.0)
    play["marks"]["halfCourt"] = round(cross, 3)
    return play


if __name__ == "__main__":
    P = build()
    json.dump(P, open(os.path.join(T, "tactical", "plays", P["id"] + ".json"), "w"), indent=1)
    print("built", P["id"], P["duration"], "s, crosses half court at", P["marks"]["halfCourt"])
