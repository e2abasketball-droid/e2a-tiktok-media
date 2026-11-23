#!/usr/bin/env python3
"""E2A 1-3-1 ZONE: THE TRAP AND THE RACE TO RECOVER (owner master brief 2026-11-23, E2A_CLAUDE_MASTER_131_ZONE_40S_REALISM.md).
Variant: HALF-COURT 1-3-1 with BASELINE-CORNER traps (ball-side wing + tail). Not the extended wing trap, not the
FIBA match-up 1-3-1. Numbering (brief sec. 2, The Hoops Geek convention): X1 chaser/top, X2 LEFT wing, X3 RIGHT wing,
X4 tail/warrior (baseline runner), X5 center.

Original E2A choreography (brief sec. 5-7: planning anchors, not coordinates taken from an article).
Repo axes: x = -brief x (brief x < 0 = the offence's LEFT). With the HORNS camera (behind the offence, basket up) the
offence's LEFT (repo x > 0) is on the LEFT of the screen. Basket (0, 1.575), y from the baseline, FIBA 6.75 m arc,
corner straights at |x| = 6.6 m.
  A zone131-a-corner-trap  O1 -> O2 (left wing), O2 -> O4 (left corner): X4 closes out from the block, X2 follows the
                           pass down the sideline: TRAP X2 + X4; X1 drops to the ball-side elbow, X5 fronts the
                           ball-side block, X3 sinks to the weak-side block. O4 picks the ball up; no steal is shown.
  B zone131-b-skip-corner  same entry, O2 throws a DIRECT overhead skip to O3 (right corner). X3 (weak-side wing) closes
                           out FIRST but reads it late; X4 sprints along the baseline to take over (bump, X3 back to the
                           wing). O3 catches behind the arc and shoots before the contest: three.
  C zone131-c-early-closeout  identical to B up to the skip release; X3 breaks ON the release: hand up at the shot,
                           contested, miss; X4 arrives and bumps, X3 returns to the wing.
Tracks: Catmull-Rom path + Hermite speed profile sampled every 0.1 s (Mover from the HORNS spec).
  python3 tactical/specs/_gen-zone131.py -> tactical/plays/zone131-{a-corner-trap,b-skip-corner,c-early-closeout}.json"""
import json, os, sys
from importlib import import_module

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, D)
Mover = import_module("_gen-horns-roll-pop").Mover

SRC = ("original E2A didactic choreography (owner master brief '1-3-1 Zone 40s Realism', sec. 2, 5-7) on the half-court "
       "corner-trapping 1-3-1 as described by Basketball For Coaches '1-3-1 Zone Defense', The Hoops Geek '1-3-1 Zone "
       "Defense' and 'trapping the baseline corners', Coach's Clipboard '1-3-1 zone' and Championship Productions "
       "'basic half-court slides and traps' (pages NOT reachable from the render container on 2026-11-23: rules taken "
       "from the brief's cited summary); FIBA court 28 x 15 m, 6.75 m arc. No diagram, frame or track copied.")

ZONE = {"type": "1-3-1", "variant": "half-court, baseline-corner trap (ball-side wing + tail)",
        "areas": {"X1": "top / chaser: point and passing lane to the wing, drops to the ball-side elbow",
                  "X2": "left wing: left wing + high left corner, traps the left corner with X4",
                  "X3": "right wing: right wing, sinks to the weak-side block, FIRST closeout on a skip to the right corner",
                  "X4": "tail / warrior: the whole baseline, both corners over time (never at once)",
                  "X5": "center: high post / low post between the ball and the rim"}}

# ------------------------------------------------------------------ spots (repo axes)
O1S, O2S, O3S, O4S, O5S = (0.0, 9.2), (6.1, 6.0), (-6.88, 1.25), (6.88, 1.25), (0.0, 5.7)
X1S, X2S, X3S, X4S, X5S = (0.0, 7.6), (3.4, 5.2), (-3.4, 5.2), (0.0, 2.0), (0.0, 4.1)
X1_SH = (1.55, 7.75)      # X1 shades to the ball side: denies the reversal, eyes on the high post
X2_ON = (5.3, 5.0)        # X2 on O2, baseline side (O4 in the corner behind him), off the skip line
X3_WB = (-2.05, 2.75)     # X3 sunk to the weak-side (right) block
X4_LB = (2.65, 1.5)       # X4 shaded to the ball-side (left) block / short corner, reading O4
X5_BS = (1.15, 3.75)      # X5 between the ball and the rim, toward the ball side

PASS1, CATCH1 = 0.7, 1.45  # O1 -> O2 (both plays)


def entry():
    """0 -> 2.3 s: the zone in its 1-3-1 shape, the ball to the left wing, the zone shifts (shared by A, B and C)"""
    m = {}
    m["O1"] = Mover(O1S).hold(1.6).move(1.6, 2.3, [(0.6, 9.05)])
    m["O2"] = Mover((6.35, 6.6)).move(0.25, 1.35, [O2S])                 # lifts to the wing, stops before the catch
    m["O3"] = Mover(O3S)
    m["O4"] = Mover((6.7, 1.6)).move(0.4, 1.3, [O4S])
    m["O5"] = Mover(O5S).move(1.5, 2.2, [(0.55, 5.6)])                   # a step to the ball side: a real high-post threat
    m["X1"] = Mover(X1S).move(0.85, 1.65, [X1_SH])
    m["X2"] = Mover(X2S).move(0.8, 1.7, [(4.6, 5.25), X2_ON])
    m["X3"] = Mover(X3S).move(0.95, 2.05, [(-2.9, 3.9), X3_WB])
    m["X4"] = Mover(X4S).move(1.0, 2.0, [(1.6, 1.7), X4_LB])
    m["X5"] = Mover(X5S).move(1.0, 1.9, [X5_BS])
    return m


def build(kind):
    m = entry()
    if kind == "a":
        PASS2, CATCH2 = 2.35, 2.85
        END = 6.5
        # X4 sprints from the block to the corner on the pass (baseline side of O4), X2 runs down the sideline (top side)
        m["X4"].move(2.4, 3.45, [(4.6, 1.2), (6.0, 0.95)])
        m["X2"].move(2.45, 3.45, [(5.9, 3.6), (6.55, 2.2)])
        m["X1"].move(2.55, 3.45, [(2.35, 6.2)])                           # ball-side elbow
        m["X5"].move(2.6, 3.5, [(2.25, 2.95)])                            # fronts the ball-side block, stays in the paint
        m["X3"].move(2.7, 3.4, [(-1.55, 2.85)])                           # weak-side block, a step to the middle
        m["O2"].move(3.0, 4.1, [(5.7, 7.1)])                              # clears up out of the trap
        m["O5"].move(3.2, 4.0, [(1.25, 5.45)])
        m["O1"].move(3.4, 4.3, [(1.5, 8.85)])
        m["O3"].move(3.6, 4.4, [(-6.8, 1.6)])
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": PASS1},
                {"type": "pass", "from": "O1", "to": "O2", "t0": PASS1, "t1": CATCH1, "style": "chest", "eyes": 0.3},
                {"type": "hold", "player": "O2", "from": CATCH1, "to": PASS2},
                {"type": "pass", "from": "O2", "to": "O4", "t0": PASS2, "t1": CATCH2, "style": "chest", "eyes": 0.3},
                {"type": "hold", "player": "O4", "from": CATCH2, "to": END}]
        acts = {"X4": [{"type": "stance", "from": 0, "to": 2.4, "face": "ball"}, {"type": "closeout", "from": 3.2, "to": END, "face": "O4"}],
                "X2": [{"type": "stance", "from": 0, "to": 2.45, "face": "O2"}, {"type": "closeout", "from": 3.3, "to": END, "face": "O4"}],
                "O4": [{"type": "catchReady", "from": 2.1, "to": CATCH2, "face": "O2"}, {"type": "face", "from": CATCH2, "to": END, "face": 2.6}],
                "O2": [{"type": "catchReady", "from": 0.9, "to": CATCH1, "face": "O1"}, {"type": "face", "from": CATCH1, "to": END, "face": "ball"}]}
        marks = {"passCorner": PASS2, "cornerCatch": CATCH2, "wingTrap": 3.45, "tailTrap": 3.35, "trap": 3.5, "x1Elbow": 3.45,
                 "x5Deny": 3.5, "x3Weak": 3.4, "end": END}
        claims = [
            {"type": "near", "a": "X4", "b": "O4", "at": "trap", "max": 1.2, "says": "The wing and the runner trap. (X4 on the baseline side)"},
            {"type": "near", "a": "X2", "b": "O4", "at": "trap", "max": 1.2, "says": "The wing and the runner trap. (X2 on the top side)"},
            {"type": "far", "a": "X2", "b": "X4", "at": "trap", "min": 0.9, "says": "the two trappers take two angles, no collision"},
            {"type": "near", "a": "X1", "b": "O5", "at": "x1Elbow", "max": 2.8, "says": "The top drops to the elbow. (guards the high post, not O2)"},
            {"type": "far", "a": "X1", "b": "O2", "at": "x1Elbow", "min": 2.5, "says": "X1 at the elbow is NOT man-to-man on O2"},
            {"type": "near", "a": "X5", "b": "O4", "at": "x5Deny", "max": 5.0, "says": "The middle protects inside. (ball-side block)"},
            {"type": "far", "a": "X5", "b": "O4", "at": "x5Deny", "min": 3.5, "says": "X5 is not a third trapper"},
            {"type": "far", "a": "X3", "b": "O3", "at": "x3Weak", "min": 4.0, "says": "And the far wing drops. (weak-side block, not the corner)"},
            {"type": "order", "marks": ["passCorner", "cornerCatch", "tailTrap", "trap"], "says": "Watch the ball reach the corner. The wing and the runner trap."}]
        meta = {"id": "zone131-a-corner-trap", "title": "1-3-1 zone (A): ball to the left corner, X2 + X4 trap, X1 elbow, X5 inside, X3 weak block"}
    else:
        early = kind == "c"
        REL, CATCH = 2.1, 3.3                       # DIRECT skip O2 -> O3, overhead, 13.8 m in 1.2 s
        SHOT0 = 3.68
        SHOT1 = SHOT0 + 1.1
        END = 5.5 if early else 6.0
        # ---- the zone moves on the pass (both branches)
        # X4: a long baseline sprint from the left block under the rim to the right corner (never through the paint)
        x4go = REL + (0.08 if early else 0.22)
        m["X4"].move(x4go, x4go + 2.05, [(1.0, 0.95), (-2.0, 0.85), (-4.6, 0.9), (-6.05, 0.95)])
        m["X1"].move(REL + 0.15, REL + 1.25, [(-0.6, 7.3), (-1.75, 6.75)])     # to the new ball side: denies the return, high post
        m["X5"].move(REL + 0.2, REL + 1.3, [(-0.95, 3.05)])                    # recovers the right block, stays near the rim
        m["X2"].move(REL + 0.25, REL + 1.45, [(3.9, 3.8), (2.15, 2.85)])       # leaves the old strong side, drops to the weak block
        m["O5"].move(REL + 0.4, REL + 1.3, [(-0.55, 5.45)])
        m["O1"].move(REL + 0.3, REL + 1.3, [(-0.6, 8.95)])
        m["O4"].move(REL + 0.5, REL + 1.4, [(6.75, 1.55)])
        if early:
            # X3 breaks ON the release (eyes on the passer), a high-side route off the ball line; hands up at the shot
            x3a, x3b = REL + 0.02, REL + 1.33
            m["X3"].move(x3a, x3b, [(-3.6, 2.95), (-5.15, 2.95), (-6.1, 2.3)])
        else:
            # X3 is late: ball-watching for ~0.6 s, then the same closeout route; arrives during the shot
            # (he reacts, but his first steps are a drift while he watches the flight; the burst comes late)
            x3a, x3b = REL + 0.12, REL + 1.95
            m["X3"].move(x3a, REL + 0.7, [(-2.55, 2.85)], 0.0, 1.5)
            m["X3"].move(REL + 0.7, x3b, [(-3.7, 2.95), (-5.15, 2.95), (-6.1, 2.3)], 1.5, 0.0)
        # the BUMP: X4 takes O3 (baseline side), X3 goes back up to his wing
        x4b = x4go + 2.05
        m["X4"].move(x4b + 0.25, x4b + 0.9, [(-6.25, 1.0)])
        m["X3"].move(max(x3b, x4b) + 0.3, max(x3b, x4b) + 1.35, [(-4.9, 3.6), (-3.6, 4.7)])
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": PASS1},
                {"type": "pass", "from": "O1", "to": "O2", "t0": PASS1, "t1": CATCH1, "style": "chest", "eyes": 0.3},
                {"type": "hold", "player": "O2", "from": CATCH1, "to": REL},
                {"type": "pass", "from": "O2", "to": "O3", "t0": REL, "t1": CATCH, "style": "overhead", "eyes": 0.4, "phased": True, "arc": 3.3},
                {"type": "hold", "player": "O3", "from": CATCH, "to": SHOT0},
                {"type": "shot", "player": "O3", "t0": SHOT0, "t1": SHOT1, **({"make": False, "side": -1, "contested": True} if early else {"make": True})}]
        x3c = x3b - 0.35
        acts = {"X3": [{"type": "stance", "from": 0, "to": x3a, "face": "ball"},
                       {"type": "closeout", "from": x3c, "to": max(x3b, x4b) + 0.3, "face": "O3"},
                       *([{"type": "contest", "from": SHOT0, "to": SHOT0 + 0.6, "face": "O3"}] if early else []),
                       {"type": "stance", "from": max(x3b, x4b) + 0.3, "to": END, "face": "ball"}],
                "X4": [{"type": "stance", "from": 0, "to": x4go, "face": "ball"}, {"type": "closeout", "from": x4b - 0.2, "to": END, "face": "O3"}],
                "X2": [{"type": "stance", "from": 0, "to": REL, "face": "O2"}, {"type": "stance", "from": REL, "to": END, "face": "ball"}],
                "O3": [{"type": "catchReady", "from": REL + 0.3, "to": CATCH, "face": "O2"}],
                "O2": [{"type": "catchReady", "from": 0.9, "to": CATCH1, "face": "O1"}, {"type": "face", "from": CATCH1, "to": REL, "face": "O3"}]}
        marks = {"skip": REL, "skipCatch": CATCH, "x3Go": x3a, "x4Go": x4go, "x3Arrive": x3b, "x4Arrive": x4go + 2.05, "release": SHOT0, "x4Bump": x4b + 0.9, "x3Back": max(x3b, x4b) + 1.35}
        if not early:
            marks["make"] = SHOT1
        marks["end"] = END
        claims = [
            {"type": "behind_arc", "player": "O3", "at": "skipCatch", "says": "skip it straight to the opposite corner (catch behind the arc)"},
            {"type": "behind_arc", "player": "O3", "at": "release", "says": "corner three (feet behind the FIBA line at the release)"},
            {"type": "far", "a": "X4", "b": "O3", "at": "skip", "min": 8.0, "says": "One defender. Two corners. (X4 is on the far side at the skip)"},
            {"type": "order", "marks": ["skip", "x4Go", "skipCatch", "x4Bump"], "says": "The runner sprints across to take over."},
            {"type": "order", "marks": ["x4Bump", "x3Back"], "says": "the bump: X4 takes the corner, X3 goes back to the wing"},
            {"type": "order", "marks": ["x3Go", "x4Go"], "says": "The far wing closes out first."},
            {"type": "order", "marks": ["x3Arrive", "x4Arrive"], "says": "The far wing closes out first. The runner sprints across to take over."},
        ]
        if early:
            claims += [
                {"type": "near", "a": "X3", "b": "O3", "at": "release", "max": 1.35, "says": "Recover on the pass? Contested."},
            ]
            meta = {"id": "zone131-c-early-closeout", "title": "1-3-1 zone (C): same skip, X3 breaks on the release, contested; X4 bumps"}
        else:
            claims += [
                {"type": "open", "player": "O3", "at": "release", "min": 1.8, "says": "If they arrive late... corner three."},
                {"type": "near", "a": "X3", "b": "O3", "at": "make", "max": 1.6, "says": "The far wing closes out first (he gets there, late)."},
                {"type": "far", "a": "X4", "b": "O3", "at": "release", "min": 1.8, "says": "X4 still on his way along the baseline at the release"},
            ]
            meta = {"id": "zone131-b-skip-corner", "title": "1-3-1 zone (B): O1 -> O2, DIRECT skip O2 -> O3, X3 first closeout (late), X4 baseline sprint + bump, three"}
    for p in m.values():
        if p.v == 0:
            p.hold(END)
    for pid, p in m.items():
        assert abs(p.v) < 1e-9, (pid, "still running at the end")
    base = {"X1": [{"type": "stance", "from": 0, "to": END, "face": "ball"}],
            "X5": [{"type": "stance", "from": 0, "to": END, "face": "ball"}],
            "X2": [{"type": "stance", "from": 0, "to": END, "face": "ball"}],
            "X3": [{"type": "stance", "from": 0, "to": END, "face": "ball"}],
            "X4": [{"type": "stance", "from": 0, "to": END, "face": "ball"}],
            "O1": [{"type": "face", "from": 0, "to": END, "face": "ball"}],
            "O3": [{"type": "face", "from": 0, "to": END, "face": "ball"}],
            "O4": [{"type": "face", "from": 0, "to": END, "face": "ball"}],
            "O5": [{"type": "face", "from": 0, "to": END, "face": "ball"}]}
    base.update(acts)
    play = {
        **meta, "duration": END, "concept": "zone-1-3-1-corner-trap-and-skip", "source": SRC,
        "v33": "compile", "squareUp": True, "catchV2": 2, "handBallClear": True, "realism": 3,
        "players": [
            {"id": "O1", "team": "O", "role": "Point guard: first pass to the left wing"},
            {"id": "O2", "team": "O", "role": "Left wing: passes to the corner (A) / throws the DIRECT skip to O3 (B, C)"},
            {"id": "O3", "team": "O", "role": "Right corner shooter, feet behind the line"},
            {"id": "O4", "team": "O", "role": "Left corner: receives and gets trapped (A), holds X4 on the left (B, C)"},
            {"id": "O5", "team": "O", "role": "High post: a real inside threat, never touches the skip"},
            {"id": "X1", "team": "X", "role": "CHASER / TOP: shades the ball, drops to the ball-side elbow"},
            {"id": "X2", "team": "X", "role": "LEFT WING: on the ball at the wing, traps the left corner with X4"},
            {"id": "X3", "team": "X", "role": "RIGHT WING: weak-side block, FIRST closeout on the skip, then bumped back"},
            {"id": "X4", "team": "X", "role": "TAIL / WARRIOR: baseline, traps the left corner, sprints the baseline on the skip"},
            {"id": "X5", "team": "X", "role": "CENTER: between ball and rim, denies the post"},
        ],
        "zone": ZONE,
        "tracks": {pid: p.wp for pid, p in m.items()},
        "ball": ball, "actions": base, "screens": [],
        "marks": {"start": 0, "wingPass": PASS1, "wingCatch": CATCH1, "x4Shade": 2.05, **marks},
        "claims": [
            {"type": "far", "a": "X1", "b": "X4", "at": "start", "min": 5.0, "says": "One up top. One runner behind the zone."},
            {"type": "near", "a": "X2", "b": "X3", "at": "start", "max": 7.0, "says": "Three across the middle. (X2-X5-X3 line)"},
            {"type": "near", "a": "X4", "b": "O4", "at": "x4Shade", "max": 4.5, "says": "X4 shades to the ball side once the ball is on the wing"},
            *claims],
        "notes": ["Half-court corner-trapping 1-3-1 only: trap = ball-side wing + tail; skip to the far corner = weak-side wing first, tail bumps.",
                  "No steal is shown in A; the late/early outcome of B/C belongs to this execution, not to every 1-3-1."],
    }
    return play


if __name__ == "__main__":
    A, B, C = build("a"), build("b"), build("c")
    for pid in B["tracks"]:
        b = [w for w in B["tracks"][pid] if w[0] <= 2.1 + 1e-9]
        c = [w for w in C["tracks"][pid] if w[0] <= 2.1 + 1e-9]
        assert b == c, pid
    for p in (A, B, C):
        json.dump(p, open(os.path.join(T, "tactical", "plays", p["id"] + ".json"), "w"), indent=1)
        print("built", p["id"], p["duration"], "s")
