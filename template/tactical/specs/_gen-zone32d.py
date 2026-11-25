#!/usr/bin/env python3
"""E2A 3-2 ZONE DEFENSE (owner master brief 2026-11-25, thread "Producir Reel zona 3-2"). The DEFENCE series after
2-3 Zone and 1-3-1 Zone. Rotation rules: produccion/zone32d-2026-11-25/REGLAS-ROTACION-3-2.md (one system, used by
every play below). Not the offence reel "How to break a 3-2 zone" (_gen-zone32.py, plays zone32-a/b): those plays
are left untouched.

System (conventional half-court 3-2, "low defender takes the corner" variant):
  X1 top-middle, X2 LEFT wing, X3 RIGHT wing (the three on ONE line, ~free-throw-line-extended: a 3-2, not a 1-2-2
  with the point out high), X4 LEFT low, X5 RIGHT low.
  Ball top      X1 on the ball; X2/X3 sag to the elbows-extended between ball and wing; X4/X5 on the blocks.
  Ball wing     ball-side wing closes out; X1 drops to the ball-side elbow (high post); weak-side wing drops to the
                middle (free-throw line); ball-side low to the ball-side block; weak-side low to the front of the rim.
  Ball corner   ball-side LOW closes out; weak-side low slides across to the ball-side block; ball-side wing cuts off
                the pass out of the corner (between wing and corner); X1 high post; weak-side wing drops to the
                weak-side block (rim + weak-side rebound).
  High post     X1 (the middle of the top line) reacts: turns and drops onto the receiver; both wings pinch to the
                elbows (dig, still in the wing lanes); both lows step up a stride to wall the paint, never leave it.
  Shot          the nearest wing contests; on the release all five find a body and box out (back to the man, face
                the rim): wing->shooter, X1->top, weak-side wing->weak-side wing, lows->bigs/corner.
Repo axes: x = -brief x. With the basket-up camera behind the offence, the offence's RIGHT (x < 0) is screen RIGHT.
Basket (0, 1.575), FIBA 6.75 m arc, corner straights |x| = 6.6 m, free-throw line y = 5.8, lane |x| <= 2.45.
  A zone32d-a-wing-corner   O1 -> O2 (right wing): everyone shifts; O2 -> O4 (right corner): corner rotation.
  B zone32d-b-high-post     O1 at the right slot, O5 flashes from the weak-side short corner to the high post,
                            bounce pass by X1's inside hip; X1 reacts, wings pinch, lows wall the paint.
  C zone32d-c-shot-boxout   O1 -> O3 (left wing), X2 closes out and contests, miss; all five box out.
  D zone32d-d-swing         ending: O1 -> O3 -> O1 -> O2, the zone shifts with every pass (one connected unit).
  python3 tactical/specs/_gen-zone32d.py -> tactical/plays/zone32d-*.json"""
import json, os, sys
from importlib import import_module

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, D)
Mover = import_module("_gen-horns-roll-pop").Mover

SRC = ("original E2A didactic choreography (owner master brief '3-2 Zone Defense', 2026-11-25) on the conventional "
       "half-court 3-2 zone, 'low defender takes the corner' rotation as summarised by HoopTactics '3-2 Zone' and "
       "Coach's Clipboard (search snippets 2026-11-25: 'Baseline defender X5 is on ball, X4 covers low post area, X3 "
       "drops to weakside baseline, X2 cuts off pass out of corner and X1 defends the high post area'; 'the ball-side "
       "low defender steps out to the corner, the weak-side low defender rotates to the ball-side block'). Source pages "
       "NOT reachable from the render container (DNS blocked), so not live-verified. No diagram, frame or track copied.")

ZONE = {"type": "3-2", "variant": "half-court 3-2, low defender takes the corner (ball-side low out, weak-side low across)",
        "areas": {"X1": "top-middle: the ball at the top, the high post / ball-side elbow on any pass",
                  "X2": "left wing: left wing; drops to the middle (ball right wing) or the weak-side block (ball right corner)",
                  "X3": "right wing: right wing; cuts off the pass out of the right corner",
                  "X4": "left low: left block + left corner; slides across to the right block when the ball goes to the right corner",
                  "X5": "right low: right block + right corner; front of the rim when the ball is on the left"},
        "rules": "produccion/zone32d-2026-11-25/REGLAS-ROTACION-3-2.md"}

# ------------------------------------------------------------------ spots (repo axes)
O1S, O2S, O3S, O4S, O5S = (0.0, 9.1), (-5.9, 6.2), (5.9, 6.75), (-6.85, 1.2), (3.3, 1.45)
X1S, X2S, X3S, X4S, X5S = (0.0, 7.75), (3.95, 6.75), (-3.95, 6.75), (2.05, 2.55), (-2.05, 2.55)
# ball on the RIGHT wing (O2)
W_X3, W_X1, W_X2, W_X5, W_X4 = (-5.05, 5.55), (-1.45, 6.15), (0.95, 5.65), (-2.45, 2.3), (0.35, 2.35)
# ball in the RIGHT corner (O4)
C_X5, C_X4, C_X3, C_X1, C_X2 = (-5.95, 1.45), (-1.75, 2.05), (-4.55, 4.0), (-1.0, 5.55), (1.35, 2.45)
# ball on the LEFT wing (O3): mirror of the right wing
mir = lambda p: (-p[0], p[1])
L_X2, L_X1, L_X3, L_X4, L_X5 = (5.25, 5.95), mir(W_X1), mir(W_X2), mir(W_X5), mir(W_X4)

PLAYERS = [
    {"id": "O1", "team": "O", "role": "Point guard at the top"},
    {"id": "O2", "team": "O", "role": "Right wing shooter"},
    {"id": "O3", "team": "O", "role": "Left wing shooter"},
    {"id": "O4", "team": "O", "role": "Right corner"},
    {"id": "O5", "team": "O", "role": "Big: left short corner, flashes to the high post (B), crashes the glass (C)"},
    {"id": "X1", "team": "X", "role": "TOP-MIDDLE: the ball at the top, then the high post"},
    {"id": "X2", "team": "X", "role": "LEFT WING: closes out left, drops to the middle / weak-side block"},
    {"id": "X3", "team": "X", "role": "RIGHT WING: closes out right, cuts off the pass out of the corner"},
    {"id": "X4", "team": "X", "role": "LEFT LOW: left block / corner; slides across the lane"},
    {"id": "X5", "team": "X", "role": "RIGHT LOW: right block / corner closeout; front of the rim"},
]


def start(o1=O1S):
    m = {k: Mover(v) for k, v in {"O1": o1, "O2": O2S, "O3": O3S, "O4": O4S, "O5": O5S,
                                  "X1": X1S, "X2": X2S, "X3": X3S, "X4": X4S, "X5": X5S}.items()}
    return m


def shift_right_wing(m, t):
    """ball O1 -> O2 released at t (catch t + 0.62): the whole zone shifts on the pass"""
    m["X3"].move(t + 0.12, t + 1.0, [(-4.75, 5.75), W_X3])          # closeout, arrives ~0.3 s after the catch
    m["X1"].move(t + 0.15, t + 1.05, [W_X1])                         # ball-side elbow / high post
    m["X2"].move(t + 0.2, t + 1.15, [(2.4, 6.2), W_X2])              # weak-side wing to the middle
    m["X5"].move(t + 0.2, t + 1.0, [W_X5])                           # ball-side block
    m["X4"].move(t + 0.25, t + 1.15, [(1.2, 2.45), W_X4])            # front of the rim


def shift_left_wing(m, t):
    m["X2"].move(t + 0.15, t + 1.1, [(4.6, 6.2), L_X2])
    m["X1"].move(t + 0.15, t + 1.05, [L_X1])
    m["X3"].move(t + 0.2, t + 1.15, [(-2.4, 6.2), L_X3])
    m["X4"].move(t + 0.2, t + 1.0, [L_X4])
    m["X5"].move(t + 0.25, t + 1.15, [(-1.2, 2.45), L_X5])


def finish(m, END, meta, ball, acts, marks, claims, notes):
    for p in m.values():
        if p.v == 0:
            p.hold(END)
    for pid, p in m.items():
        assert abs(p.v) < 1e-9, (pid, "still running at the end")
    base = {pid: [{"type": "stance" if pid[0] == "X" else "face", "from": 0, "to": END, "face": "ball"}] for pid in m}
    base.update(acts)
    return {**meta, "duration": END, "concept": "zone-3-2-defense", "source": SRC,
            "v33": "compile", "squareUp": True, "catchV2": 2, "handBallClear": True, "realism": 3,
            "players": PLAYERS, "zone": ZONE, "tracks": {pid: p.wp for pid, p in m.items()},
            "ball": ball, "actions": base, "screens": [], "marks": {"start": 0, **marks},
            "claims": [
                {"type": "near", "a": "X1", "b": "X2", "at": "start", "max": 4.3, "says": "Three defenders up top (X1-X2 on one line)"},
                {"type": "near", "a": "X1", "b": "X3", "at": "start", "max": 4.3, "says": "Three defenders up top (X1-X3 on one line)"},
                {"type": "far", "a": "X4", "b": "X5", "at": "start", "min": 3.6, "says": "Two down low (one per block)"},
                *claims],
            "notes": notes}


def build_a():
    m = start()
    P1, C1 = 0.7, 1.32          # O1 -> O2 (right wing)
    P2, C2 = 2.75, 3.3          # O2 -> O4 (right corner)
    END = 5.4
    m["O2"].move(0.2, 0.9, [(-6.0, 6.05)])                           # a step to the arc, ready to catch
    shift_right_wing(m, P1)
    m["O1"].move(1.5, 2.3, [(-0.6, 9.0)])
    # the corner rotation (on the pass O2 -> O4)
    m["X5"].move(P2 + 0.05, P2 + 1.15, [(-4.4, 1.75), C_X5])         # ball-side low steps out (baseline side of the line)
    m["X4"].move(P2 + 0.1, P2 + 1.15, [(-0.7, 2.2), C_X4])           # weak-side low slides across the lane to the block
    m["X3"].move(P2 + 0.12, P2 + 0.95, [C_X3])                       # cuts off the pass out of the corner
    m["X1"].move(P2 + 0.2, P2 + 1.0, [C_X1])                         # high post
    m["X2"].move(P2 + 0.2, P2 + 1.25, [(1.3, 4.2), C_X2])            # weak-side wing drops to the weak-side block
    m["O2"].move(P2 + 0.6, P2 + 1.5, [(-5.4, 6.7)])                  # spaces up after the pass
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": P1},
            {"type": "pass", "from": "O1", "to": "O2", "t0": P1, "t1": C1, "style": "chest", "eyes": 0.3},
            {"type": "hold", "player": "O2", "from": C1, "to": P2},
            {"type": "pass", "from": "O2", "to": "O4", "t0": P2, "t1": C2, "style": "chest", "eyes": 0.3},
            {"type": "hold", "player": "O4", "from": C2, "to": END}]
    acts = {"X3": [{"type": "stance", "from": 0, "to": P1 + 0.05, "face": "ball"},
                   {"type": "closeout", "from": P1 + 0.55, "to": P1 + 1.6, "face": "O2"},
                   {"type": "stance", "from": P1 + 1.6, "to": END, "face": "ball"}],
            "X5": [{"type": "stance", "from": 0, "to": P2 + 0.05, "face": "ball"},
                   {"type": "closeout", "from": P2 + 0.55, "to": END, "face": "O4"}],
            "O2": [{"type": "catchReady", "from": 0.9, "to": C1, "face": "O1"}, {"type": "face", "from": C1, "to": P2 - 0.25, "face": "rim"},
                   {"type": "face", "from": P2 - 0.25, "to": P2 + 0.6, "face": "O4"}],
            "O4": [{"type": "catchReady", "from": P2 - 0.2, "to": C2, "face": "O2"}, {"type": "face", "from": C2, "to": END, "face": "rim"}]}
    marks = {"wingPass": P1, "wingCatch": C1, "closeout": P1 + 0.95, "shifted": P1 + 1.15, "cornerPass": P2, "cornerCatch": C2,
             "x5Out": P2 + 1.2, "rotated": P2 + 1.25, "end": END}
    claims = [
        {"type": "order", "marks": ["wingPass", "wingCatch", "closeout"], "says": "the nearest defender closes out (after the pass)"},
        {"type": "near", "a": "X3", "b": "O2", "at": "closeout", "max": 1.3, "says": "the nearest defender closes out"},
        {"type": "near", "a": "X1", "b": "O2", "at": "shifted", "max": 5.0, "says": "everyone shifts (X1 to the ball-side elbow)"},
        {"type": "far", "a": "X1", "b": "O1", "at": "shifted", "min": 2.4, "says": "X1 has left the top: he guards the high post, not O1"},
        {"type": "near_rim", "player": "X4", "at": "shifted", "max": 1.4, "says": "to protect the gaps (weak-side low in front of the rim)"},
        {"type": "near", "a": "X5", "b": "O4", "at": "x5Out", "max": 1.2, "says": "the bottom defender steps out"},
        {"type": "near_rim", "player": "X4", "at": "rotated", "max": 2.2, "says": "protect the paint (X4 across to the ball-side block)"},
        {"type": "near_rim", "player": "X2", "at": "rotated", "max": 1.9, "says": "cover the weak side (X2 drops to the weak-side block)"},
        {"type": "far", "a": "X3", "b": "O4", "at": "rotated", "min": 2.5, "says": "X3 is not a second trapper: he cuts off the pass out of the corner"},
        {"type": "far", "a": "X4", "b": "X2", "at": "rotated", "min": 2.4, "says": "two separate defenders under the rim (no double team in the paint)"},
        {"type": "order", "marks": ["cornerPass", "cornerCatch", "x5Out"], "says": "When the ball reaches the corner, the bottom defender steps out"}]
    meta = {"id": "zone32d-a-wing-corner", "title": "3-2 zone (A): ball to the right wing (all five shift), then the right corner (X5 out, X4 across, X3 cuts off, X1 high post, X2 weak block)"}
    return finish(m, END, meta, ball, acts, marks, claims,
                  ["One rotation system: low defender takes the corner. No trap is shown; X3 does not double the corner."])


def build_b():
    O1B = (-2.3, 9.0)
    m = start(O1B)
    m["X1"] = Mover((-2.15, 7.85))                                     # on the ball at the right slot
    m["X3"] = Mover((-4.45, 6.55))
    m["X2"] = Mover((1.8, 6.7))
    REL, CATCH = 2.0, 2.42
    END = 5.0
    m["O5"].move(0.5, 1.75, [(2.4, 3.3), (0.95, 5.0), (0.2, 5.85)])   # flash from the weak-side short corner to the nail
    # the reaction (on the catch)
    m["X1"].move(REL + 0.15, REL + 1.0, [(-1.1, 7.15), (-0.25, 6.85)])  # turns and drops onto the receiver, top side
    m["X2"].move(REL + 0.2, REL + 0.95, [(2.25, 5.75)])               # pinches to the left elbow (dig, still in the lane to O3)
    m["X3"].move(REL + 0.2, REL + 0.95, [(-3.0, 5.65)])               # pinches to the right elbow (lane to O2)
    m["X4"].move(REL + 0.25, REL + 1.0, [(1.25, 3.4)])                # walls the paint, a stride up
    m["X5"].move(REL + 0.25, REL + 1.0, [(-1.25, 3.4)])
    m["O1"].move(REL + 0.4, REL + 1.2, [(-3.0, 8.6)])
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": REL},
            {"type": "pass", "from": "O1", "to": "O5", "t0": REL, "t1": CATCH, "style": "bounce", "eyes": 0.35},
            {"type": "hold", "player": "O5", "from": CATCH, "to": END}]
    acts = {"X1": [{"type": "stance", "from": 0, "to": REL + 0.1, "face": "O1"}, {"type": "stance", "from": REL + 0.1, "to": END, "face": "O5"}],
            "O5": [{"type": "catchReady", "from": 1.5, "to": CATCH, "face": "O1"}, {"type": "face", "from": CATCH + 0.35, "to": END, "face": "rim"}]}
    marks = {"flash": 0.5, "nail": 1.75, "entry": REL, "entryCatch": CATCH, "react": REL + 1.0, "end": END}
    claims = [
        {"type": "far", "a": "X1", "b": "O5", "at": "entry", "min": 2.0, "says": "watch the high post: the gap behind X1 when he is on the ball"},
        {"type": "near", "a": "X1", "b": "O5", "at": "react", "max": 1.4, "says": "the middle defender must react"},
        {"type": "near_rim", "player": "X4", "at": "react", "max": 2.6, "says": "the entire defense adjusts (lows wall the paint, stay home)"},
        {"type": "near_rim", "player": "X5", "at": "react", "max": 2.6, "says": "the entire defense adjusts (lows wall the paint, stay home)"},
        {"type": "far", "a": "X2", "b": "O5", "at": "react", "min": 1.6, "says": "wings pinch, they do not double: still in the lanes to the wings"},
        {"type": "far", "a": "X3", "b": "O5", "at": "react", "min": 1.6, "says": "wings pinch, they do not double: still in the lanes to the wings"},
        {"type": "order", "marks": ["entry", "entryCatch", "react"], "says": "If the ball gets inside, the middle defender must react"}]
    meta = {"id": "zone32d-b-high-post", "title": "3-2 zone (B): O5 flashes to the high post behind X1, bounce entry; X1 reacts, wings pinch, lows wall the paint"}
    return finish(m, END, meta, ball, acts, marks, claims,
                  ["The high post is not undefended: X1 recovers onto it; the zone changes shape (compresses) and the corners/wings open."])


def build_c():
    m = start()
    P1, C1 = 0.6, 1.2           # O1 -> O3 (left wing)
    SH0, SH1 = 1.95, 3.05       # contested three, miss
    END = 4.3
    m["O3"].move(0.1, 0.8, [(6.0, 6.55)])
    shift_left_wing(m, P1)
    # box-out on the release: everyone finds a body, back to the man, face the rim
    B0 = SH0 + 0.3
    m["O1"].move(B0, B0 + 1.0, [(0.3, 7.7)])
    m["X1"].move(B0, B0 + 0.9, [(0.75, 6.55)])
    m["O2"].move(B0, B0 + 1.0, [(-4.7, 5.0)])
    m["X3"].move(B0, B0 + 0.9, [(-3.55, 4.35)])
    m["O4"].move(B0, B0 + 1.0, [(-4.5, 1.75)])
    m["X5"].move(B0, B0 + 0.9, [(-3.25, 1.95)])
    m["O5"].move(B0, B0 + 1.0, [(2.75, 1.95)])
    m["X4"].move(B0 + 0.05, B0 + 0.85, [(1.9, 2.05)])
    m["X2"].move(SH0 + 0.75, SH0 + 1.35, [(5.05, 5.75)])                # lands from the contest, turns, seals the shooter
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": P1},
            {"type": "pass", "from": "O1", "to": "O3", "t0": P1, "t1": C1, "style": "chest", "eyes": 0.3},
            {"type": "hold", "player": "O3", "from": C1, "to": SH0},
            {"type": "shot", "player": "O3", "t0": SH0, "t1": SH1, "make": False, "side": 1, "contested": True}]
    box = lambda pid, man: [{"type": "stance", "from": B0 + 0.35, "to": END, "face": "rim"}]
    acts = {"X2": [{"type": "stance", "from": 0, "to": P1 + 0.05, "face": "ball"},
                   {"type": "closeout", "from": P1 + 0.5, "to": SH0, "face": "O3"},
                   {"type": "contest", "from": SH0, "to": SH0 + 0.65, "face": "O3"},
                   {"type": "stance", "from": SH0 + 0.85, "to": END, "face": "rim"}],
            "X1": [{"type": "stance", "from": 0, "to": B0 + 0.35, "face": "ball"}, *box("X1", "O1")],
            "X3": [{"type": "stance", "from": 0, "to": B0 + 0.35, "face": "ball"}, *box("X3", "O2")],
            "X4": [{"type": "stance", "from": 0, "to": B0 + 0.35, "face": "ball"}, *box("X4", "O5")],
            "X5": [{"type": "stance", "from": 0, "to": B0 + 0.35, "face": "ball"}, *box("X5", "O4")],
            "O3": [{"type": "catchReady", "from": 0.85, "to": C1, "face": "O1"}],
            **{o: [{"type": "face", "from": 0, "to": END, "face": "ball"}] for o in ("O1", "O2", "O4", "O5")}}
    marks = {"leftPass": P1, "leftCatch": C1, "closeout": P1 + 0.95, "release": SH0, "rim": SH1, "box": B0 + 0.9, "end": END}
    claims = [
        {"type": "behind_arc", "player": "O3", "at": "release", "says": "contesting perimeter shots (the shooter is behind the arc)"},
        {"type": "near", "a": "X2", "b": "O3", "at": "release", "max": 1.3, "says": "great at contesting perimeter shots"},
        {"type": "near", "a": "X5", "b": "O4", "at": "box", "max": 1.6, "says": "find a body (X5 on O4)"},
        {"type": "near", "a": "X4", "b": "O5", "at": "box", "max": 1.2, "says": "find a body (X4 on O5)"},
        {"type": "near", "a": "X3", "b": "O2", "at": "box", "max": 1.6, "says": "find a body (X3 on O2, weak side)"},
        {"type": "near", "a": "X1", "b": "O1", "at": "box", "max": 1.4, "says": "find a body (X1 on O1)"},
        {"type": "near", "a": "X2", "b": "O3", "at": "box", "max": 1.6, "says": "find a body (X2 on the shooter)"},
        {"type": "order", "marks": ["release", "box"], "says": "On every shot: find a body. Box out."}]
    meta = {"id": "zone32d-c-shot-boxout", "title": "3-2 zone (C): ball to the left wing, X2 contests the three (miss), all five box out"}
    return finish(m, END, meta, ball, acts, marks, claims,
                  ["Box-out = a body between each offensive player and the rim, facing the rim; the rebound itself is not shown."])


def build_d():
    m = start()
    P1, C1 = 0.5, 1.1           # O1 -> O3
    P2, C2 = 2.15, 2.7          # O3 -> O1 (reversal)
    P3, C3 = 3.55, 4.15         # O1 -> O2
    END = 5.6
    shift_left_wing(m, P1)
    # back to the top: everyone returns to the base 3-2 on the reversal
    m["X2"].move(P2 + 0.1, P2 + 1.15, [X2S])
    m["X1"].move(P2 + 0.05, P2 + 1.0, [X1S])
    m["X3"].move(P2 + 0.1, P2 + 1.3, [X3S])
    m["X4"].move(P2 + 0.15, P2 + 1.1, [X4S])
    m["X5"].move(P2 + 0.15, P2 + 1.2, [X5S])
    shift_right_wing(m, P3)
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": P1},
            {"type": "pass", "from": "O1", "to": "O3", "t0": P1, "t1": C1, "style": "chest", "eyes": 0.3},
            {"type": "hold", "player": "O3", "from": C1, "to": P2},
            {"type": "pass", "from": "O3", "to": "O1", "t0": P2, "t1": C2, "style": "chest", "eyes": 0.3},
            {"type": "hold", "player": "O1", "from": C2, "to": P3},
            {"type": "pass", "from": "O1", "to": "O2", "t0": P3, "t1": C3, "style": "chest", "eyes": 0.3},
            {"type": "hold", "player": "O2", "from": C3, "to": END}]
    acts = {"O3": [{"type": "catchReady", "from": 0.75, "to": C1, "face": "O1"}],
            "O1": [{"type": "catchReady", "from": P2 + 0.2, "to": C2, "face": "O3"}],
            "O2": [{"type": "catchReady", "from": P3 + 0.2, "to": C3, "face": "O1"}]}
    marks = {"p1": P1, "c1": C1, "p2": P2, "c2": C2, "back": P2 + 1.3, "p3": P3, "c3": C3, "right": P3 + 1.15, "end": END}
    claims = [
        {"type": "near", "a": "X2", "b": "O3", "at": "p2", "max": 1.3, "says": "Five defenders. (left wing closed out)"},
        {"type": "near", "a": "X3", "b": "O2", "at": "right", "max": 1.3, "says": "One connected unit. (right wing closed out)"},
        {"type": "order", "marks": ["p1", "c1", "p2", "c2", "p3", "c3"], "says": "the ball travels around the perimeter"}]
    meta = {"id": "zone32d-d-swing", "title": "3-2 zone (D): ball swung left, back to the top, right; the zone shifts on every pass"}
    return finish(m, END, meta, ball, acts, marks, claims, ["Ending / loop: the base 3-2 is reached again at the reversal."])


if __name__ == "__main__":
    for p in (build_a(), build_b(), build_c(), build_d()):
        json.dump(p, open(os.path.join(T, "tactical", "plays", p["id"] + ".json"), "w"), indent=1)
        print("built", p["id"], p["duration"], "s")
