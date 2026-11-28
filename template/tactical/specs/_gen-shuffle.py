#!/usr/bin/env python3
"""E2A SPORTS - CINEMATIC TACTICAL BREAKDOWN: SHUFFLE CUT V1 (owner brief 2026-11-28 09:18Z).

ONE canonical 5v5 possession. This file is the single source of truth: it writes
  tactical/shuffle/e2a_shuffle_cut_v1.json   the canonical play (K0..K6, every player, states, causes, corrections)
  tactical/plays/shuffle-cut-v1.json          the engine play (Motion Engine V4) that every shot, replay and graphic uses

Coordinates (owner, as in the brief): origin = centre of the attacking endline, x lateral (negative = LEFT of the
overhead diagram, basket at the top), y toward half court, basket (0, 1.575). Player CENTRES, metres.
Engine mapping (same as Basketball IQ 02): engine x = -owner x, engine y = owner y, engine t = owner t + PRE.

Coaching basis (principles only, nothing copied):
  - FIBA WABC Coaching Manual Level 3, 2.1.3 "The Shuffle" (manual p.168): reversing the ball starts the movement;
    the first cutter cutting off the high-post screen is the basic Shuffle Cut.
  - WABC 2.2.4 Blind (back) screens (p.186): set behind the defender, at least one step away from his current
    position; effective against a defender who is denying or whose man has just passed.
  - WABC 2.1.1 layer 8 (p.165): the cutter does not move until the screener has set ("listen for the feet").
  - Coach's Clipboard, Shuffle Offense: O5 screens for O1, who cuts off the screen looking for the pass from the
    feeder O3 for the lay-up; Cutting and Faking: slow fake, quick cut, quick strong first step; V-cut: plant hard and
    push off in the direction of the cut. Princeton: cutters always have their hands ready.
  python3 tactical/specs/_gen-shuffle.py
"""
import json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PRE = 0.6                       # engine pre-roll (s) before K0: players alive, O2 finishes his dribble
DUR = 5.4                       # engine duration (owner -0.6 .. 4.8)
r3 = lambda x: round(x, 3)
E = lambda p: [r3(-p[0]), r3(p[1])]          # owner -> engine
HOOP = (0.0, 1.575)

# ------------------------------------------------------------------------------------------------ owner anchors (T0)
ANCHOR = {"O1": (-3.70, 8.90), "O2": (0.20, 10.20), "O3": (5.50, 7.20), "O4": (-6.65, 2.70), "O5": (-1.55, 6.30),
          "X1": (-3.15, 8.05), "X2": (-0.40, 9.00), "X3": (4.70, 6.90), "X4": (-5.70, 3.10), "X5": (-0.85, 5.75)}
# the brief's T0 coordinates exactly as given (2026-11-28 09:18Z); ANCHOR differs only where corrections_log says so (X2)
ANCHOR_BRIEF = {**ANCHOR, "X2": (0.10, 9.35)}

# ------------------------------------------------------------------------------------------------ the designed spots
S = (-2.50, 7.30)          # O5's back-screen spot: 1.30 m behind X1 (basket side), out of his vision
A = (-3.30, 9.30)          # end of O1's slow set-up step (up and in, as if to receive the reversal): the V-cut plant
P1 = (-3.05, 7.30)         # O1 brushes O5's left (outside) shoulder: 0.55 m centre to centre, no gap for X1
C = (-1.56, 4.43)          # O1's catch on the move (gather on the catch)
R = (-0.65, 2.45)          # layup release spot (left side of the rim, left hand)
L = (-0.47, 2.08)          # landing

# ------------------------------------------------------------------------------------------------ owner timeline
M = {"start": -PRE, "k0": 0.0, "rel1": 0.25, "k1": 0.85, "x1_set": 1.20, "x3_set": 2.00, "screen_set": 1.25, "k2": 1.30, "k3": 1.55,
     "x1_react": 1.72, "k4": 2.10, "rel2": 2.10, "contact": 2.15, "brush": 2.20, "clear": 2.65, "screen_release": 2.70,
     "k5": 2.85, "k6": 3.50, "make": 3.95, "end": DUR - PRE}

# ------------------------------------------------------------------------------------------------ tracks (owner)
# each list: (owner t, (x, y)); two equal consecutive points = a stop (the engine spline starts/ends a run at rest)
TR = {
    # O1: alive, slow set-up step up and in (change of pace), STOP = plant, explosive cut tight off O5, catch, layup
    "O1": [(-PRE, (-3.78, 8.80)), (0.0, ANCHOR["O1"]), (0.30, ANCHOR["O1"]), (1.15, A), (1.55, A),
           (2.20, P1), (2.85, C), (3.50, R), (3.80, L), (DUR - PRE, L)],
    # O2: finishes his dribble to the top, holds, passes to O3, then spaces one step left (available for reversal)
    "O2": [(-PRE, (0.70, 10.70)), (0.0, ANCHOR["O2"]), (0.95, ANCHOR["O2"]), (1.75, (-0.30, 10.15)), (DUR - PRE, (-0.30, 10.15))],
    # O3: V-cuts up the wing to meet the pass, catches, squares up, reads the cut, passes, then holds
    "O3": [(-PRE, (5.40, 7.05)), (0.0, ANCHOR["O3"]), (0.80, (5.85, 8.30)), (DUR - PRE, (5.85, 8.30))],
    # O4: left-corner spacer: stays (weight shifts only)
    "O4": [(-PRE, (-6.62, 2.78)), (0.0, ANCHOR["O4"]), (2.0, ANCHOR["O4"]), (2.6, (-6.60, 2.80)), (DUR - PRE, (-6.60, 2.80))],
    # O5: from the high post up and out to the screen spot; feet set at 1.25 (stationary to 2.45); then steps to the ball
    "O5": [(-PRE, (-1.40, 6.05)), (0.0, ANCHOR["O5"]), (0.25, ANCHOR["O5"]), (1.20, S), (2.72, S), (3.35, (-2.15, 8.05)),
           (DUR - PRE, (-2.15, 8.05))],
    # X1: follows O1's set-up (ball side, denying), chases O1, runs into the screen (contact), goes through behind
    # him, trails and contests late from behind
    "X1": [(-PRE, (-3.20, 7.95)), (0.0, ANCHOR["X1"]), (0.45, ANCHOR["X1"]), (1.20, (-2.60, 8.60)), (1.70, (-2.60, 8.60)),
           (2.15, (-2.52, 7.93)), (2.24, (-2.52, 7.93)), (2.50, (-2.92, 7.78)), (2.72, (-3.12, 7.28)), (2.95, (-2.95, 6.55)), (3.50, (-1.65, 3.75)),
           (4.05, (-1.20, 3.05)), (DUR - PRE, (-1.20, 3.05))],
    # X2: jumps to the ball on the entry, stays high and connected to O2
    "X2": [(-PRE, (-0.30, 9.15)), (0.0, ANCHOR["X2"]), (0.40, ANCHOR["X2"]), (1.00, (0.20, 9.15)), (1.85, (0.20, 9.15)),
           (2.45, (0.00, 8.90)), (DUR - PRE, (0.10, 8.90))],
    # X3: gives the catch (no full deny), closes out to the BASELINE side (no baseline drive), sinks after the pass
    "X3": [(-PRE, (4.65, 6.80)), (0.0, ANCHOR["X3"]), (1.00, ANCHOR["X3"]), (2.00, (6.45, 7.30)), (2.28, (6.45, 7.30)),
           (3.10, (5.75, 7.05)), (DUR - PRE, (5.75, 7.05))],
    # X4: connected to O4 in the corner; a stunt step toward the lane after the catch, back
    "X4": [(-PRE, (-5.75, 3.05)), (0.0, ANCHOR["X4"]), (3.00, ANCHOR["X4"]), (3.35, (-5.30, 3.12)), (4.00, (-5.55, 3.08)),
           (DUR - PRE, (-5.55, 3.08))],
    # X5: follows O5 up (ball side, denying the post entry), shows one step at the cutter (controlled help), recovers to
    # O5 when he steps to the ball
    "X5": [(-PRE, (-0.75, 5.60)), (0.0, ANCHOR["X5"]), (0.40, ANCHOR["X5"]), (1.30, (-1.75, 7.05)), (1.85, (-1.75, 7.05)),
           (2.20, (-1.98, 6.72)), (2.86, (-1.98, 6.72)), (3.45, (-1.60, 7.60)), (DUR - PRE, (-1.55, 7.55))],
}

KEYS = [("K0", 0.0, "Initial formation: O2 has the ball at the top"),
        ("K1", 0.85, "Wing pass completed: O3 catches on the right wing"),
        ("K2", 1.30, "O5's back screen established (feet set at 1.25, 1.30 m behind X1)"),
        ("K3", 1.55, "O1 plants (end of the slow set-up) and starts using the screen"),
        ("K4", 2.10, "X1 runs into the screen and is delayed; O1 enters the passing window; O3 releases"),
        ("K5", 2.85, "O1 catches on the move (gather)"),
        ("K6", 3.50, "O1 releases the left-hand layup off the glass")]

STATE = {  # intended movement state per keyframe (verified against the dump by tools/shuffle_validate.py)
    "K0": {"O1": "set (alive)", "O2": "holding (ball)", "O3": "ready", "O4": "spacing", "O5": "ready", "X1": "deny stance",
           "X2": "on-ball stance", "X3": "deny stance", "X4": "stance (corner)", "X5": "post stance"},
    "K1": {"O1": "slow set-up step", "O2": "follow-through", "O3": "catch, square up", "O4": "spacing", "O5": "walking to the screen",
           "X1": "following O1 (ball side)", "X2": "jump to the ball", "X3": "closeout (baseline side)", "X4": "stance", "X5": "following O5"},
    "K2": {"O1": "slow set-up step", "O2": "spacing left", "O3": "triple threat", "O4": "spacing", "O5": "SCREEN SET (stationary)",
           "X1": "deny stance", "X2": "stance", "X3": "on-ball pressure", "X4": "stance", "X5": "post denial"},
    "K3": {"O1": "PLANT (V-cut)", "O2": "spacing", "O3": "reading the cut", "O4": "spacing", "O5": "screen (stationary)",
           "X1": "stance (screen behind him)", "X2": "stance", "X3": "on-ball pressure", "X4": "stance", "X5": "post denial"},
    "K4": {"O1": "sprint (brushing O5)", "O2": "spacing", "O3": "PASS release", "O4": "spacing", "O5": "screen (stationary, contact)",
           "X1": "CONTACT with the screen (delayed)", "X2": "sinking", "X3": "pressure, reacts to the pass", "X4": "stance", "X5": "show (controlled help)"},
    "K5": {"O1": "CATCH on the move", "O2": "spacing", "O3": "follow-through", "O4": "spacing", "O5": "stepping to the ball",
           "X1": "chasing (trailing)", "X2": "stance high", "X3": "sinking", "X4": "stance", "X5": "recovering to O5"},
    "K6": {"O1": "LAYUP release (airborne)", "O2": "spacing", "O3": "watching", "O4": "spacing", "O5": "available high",
           "X1": "late contest from behind", "X2": "stance high", "X3": "sinking", "X4": "stunt step", "X5": "with O5"},
}
BALL_OWNER = {"K0": "O2", "K1": "O3", "K2": "O3", "K3": "O3", "K4": "O3 (release)", "K5": "O1", "K6": "O1 (release)"}
SCREEN_STATE = {"K0": "none", "K1": "O5 approaching", "K2": "SET (legal: stationary, 1.30 m behind X1, outside his vision)",
                "K3": "set", "K4": "set, X1 in contact", "K5": "released (X1 through)", "K6": "none"}
FACING = {  # intended facing target per player (the engine's action list): verified as angles in the dump
    "K0": {"O1": "ball", "O2": "O3", "O3": "O2", "O4": "ball", "O5": "ball", "X1": "O1", "X2": "O2", "X3": "O3", "X4": "O4", "X5": "O5"},
    "K1": {"O1": "ball", "O2": "O3", "O3": "O2", "O4": "ball", "O5": "screen spot", "X1": "O1", "X2": "ball", "X3": "O3", "X4": "O4", "X5": "O5"},
    "K2": {"O1": "ball", "O2": "ball", "O3": "rim", "O4": "ball", "O5": "X1", "X1": "O1", "X2": "O2", "X3": "O3", "X4": "O4", "X5": "O5"},
    "K3": {"O1": "ball", "O2": "ball", "O3": "O1", "O4": "ball", "O5": "X1", "X1": "O1", "X2": "O2", "X3": "O3", "X4": "O4", "X5": "O5"},
    "K4": {"O1": "path (head to the ball)", "O2": "ball", "O3": "O1", "O4": "ball", "O5": "X1", "X1": "O1 (path)", "X2": "ball", "X3": "O3", "X4": "ball", "X5": "O1"},
    "K5": {"O1": "path (catching)", "O2": "ball", "O3": "O1", "O4": "ball", "O5": "ball", "X1": "path", "X2": "ball", "X3": "ball", "X4": "ball", "X5": "O5"},
    "K6": {"O1": "rim", "O2": "ball", "O3": "ball", "O4": "ball", "O5": "ball", "X1": "O1", "X2": "ball", "X3": "ball", "X4": "ball", "X5": "O5"},
}
REACTION = {
    "K0": "none (formation)", "K1": "X3 closes out high on the catch; X2 jumps to the ball; X5 follows O5 up",
    "K2": "X1 stays ball side of O1, denying (he does not see O5 behind him)",
    "K3": "none yet: X1 reacts 0.17 s after the plant",
    "K4": "X1 turns to chase and runs into O5's chest: delayed ~0.4 s; X5 shows one step at the cutter but stays attached to O5",
    "K5": "X1 trails ~1.7 m; X4 stays connected to O4 (corner shooter, no rotation); X2 stays high on O2",
    "K6": "X1 contests late from behind (~1.6 m); X5 recovers to O5"}

CAUSES = {  # owner times; every defender movement onset must follow a declared cause by >= 0.15 s
    "X1": [{"t": -PRE, "cause": "pre-roll: guards O1"}, {"t": 0.30, "cause": "O1 starts his set-up step up and in: follows, ball side"},
           {"t": 1.55, "cause": "O1 plants and cuts: chases"}],
    "X2": [{"t": -PRE, "cause": "pre-roll: guards O2"}, {"t": 0.25, "cause": "O2 passes to O3: jumps to the ball"},
           {"t": 1.55, "cause": "O1 cuts: sinks a step, stays high on O2"}],
    "X3": [{"t": -PRE, "cause": "pre-roll: guards O3"}, {"t": 0.85, "cause": "O3 catches: closeout to baseline-side pressure"},
           {"t": 2.10, "cause": "O3 passes: jumps to the ball / sinks"}],
    "X4": [{"t": -PRE, "cause": "pre-roll: guards O4"}, {"t": 2.85, "cause": "O1 catches in the lane: stunt step, stays with O4"}],
    "X5": [{"t": -PRE, "cause": "pre-roll: guards O5"}, {"t": 0.25, "cause": "O5 moves up to screen: follows, ball side"},
           {"t": 1.55, "cause": "O1 cuts off the screen: shows one step (controlled help)"},
           {"t": 2.70, "cause": "O5 releases the screen and steps to the ball: recovers"}],
}


def lerp_track(tr, t):
    """owner position by linear interpolation of the authored points (the engine spline passes through them exactly)"""
    if t <= tr[0][0]:
        return tr[0][1]
    for (t0, p0), (t1, p1) in zip(tr, tr[1:]):
        if t0 <= t <= t1:
            u = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            return (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)
    return tr[-1][1]


def kf_pos(pid, t):
    for (tt, p) in TR[pid]:
        if abs(tt - t) < 1e-9:
            return p
    return lerp_track(TR[pid], t)


def engine_tracks():
    out = {}
    for pid, pts in TR.items():
        wps = []
        for i, (t, p) in enumerate(pts):
            w = [r3(t + PRE), *E(p)]
            if i == 0:
                w.append("fly")      # the pre-roll starts in motion (players are alive before K0)
            wps.append(w)
        out[pid] = wps
    return out


def et(t):
    return r3(t + PRE)


ST = lambda f, a, b: {"type": "stance", "from": et(a), "to": et(b), "face": f}
FACE = lambda f, a, b: {"type": "face", "from": et(a), "to": et(b), "face": f}


def play():
    acts = {
        "O1": [FACE("ball", -PRE, 1.5), {"type": "catchReady", "from": et(M["rel2"] - 0.1), "to": et(M["k5"] + 0.05), "face": "O3"}],
        "O2": [FACE("O3", -PRE, M["rel1"] + 0.2), FACE("ball", M["rel1"] + 0.25, M["end"])],
        "O3": [{"type": "catchReady", "from": et(M["rel1"] - 0.05), "to": et(M["k1"] + 0.05), "face": "O2"},
               FACE("rim", M["k1"] + 0.1, M["k3"] - 0.05), FACE("O1", M["k3"], M["rel2"] + 0.3), FACE("ball", M["rel2"] + 0.35, M["end"])],
        "O4": [FACE("ball", -PRE, M["end"])],
        "O5": [FACE("ball", -PRE, 0.2), {"type": "screen", "from": et(M["screen_set"] + 0.02), "to": et(M["screen_release"]), "face": "X1"},
               FACE("ball", M["screen_release"] + 0.05, M["end"])],
        "X1": [ST("O1", -PRE, M["end"]),
               {"type": "contest", "from": et(M["k6"] - 0.15), "to": et(M["make"]), "face": "O1"}],
        "X2": [ST("O2", -PRE, M["rel1"] + 0.1), ST("ball", M["rel1"] + 0.15, M["end"])],
        "X3": [ST("O3", -PRE, M["end"])],
        "X4": [ST("O4", -PRE, M["k5"]), ST("ball", M["k5"] + 0.05, M["end"])],
        "X5": [ST("O5", -PRE, 1.80), {"type": "help", "from": et(1.85), "to": et(2.80), "face": "O1"}, ST("O5", 2.85, M["end"])],
    }
    ball = [{"type": "hold", "player": "O2", "from": 0, "to": et(-0.05), "dribble": True, "hand": 1},
            {"type": "hold", "player": "O2", "from": et(-0.05), "to": et(M["rel1"])},
            {"type": "pass", "from": "O2", "to": "O3", "t0": et(M["rel1"]), "t1": et(M["k1"]), "style": "chest", "eyes": 0.2},
            {"type": "hold", "player": "O3", "from": et(M["k1"]), "to": et(M["rel2"])},
            {"type": "pass", "from": "O3", "to": "O1", "t0": et(M["rel2"]), "t1": et(M["k5"]), "style": "bounce", "ballistic": True,
             "lead": True, "eyes": 0.15},
            {"type": "hold", "player": "O1", "from": et(M["k5"]), "to": et(M["k6"])},
            {"type": "layup", "player": "O1", "t0": et(M["k6"]), "t1": et(M["make"]), "make": True, "hand": -1, "H": 0.45,
             "glass": [0.27, 3.42]}]
    players = [{"id": "O1", "team": "O", "role": "Shuffle cutter (left slot): set-up step, cuts off O5's back screen, catches, layup"},
               {"id": "O2", "team": "O", "role": "Point / entry passer: passes to O3, spaces, available for reversal"},
               {"id": "O3", "team": "O", "role": "Feeder (right wing): catches, squares up, passes to the cutter"},
               {"id": "O4", "team": "O", "role": "Left-corner spacer: keeps X4 away from the action"},
               {"id": "O5", "team": "O", "role": "High-post screener: legal stationary back screen on X1, then steps to the ball"},
               {"id": "X1", "team": "X", "guards": "O1", "role": "Denies O1 ball side, chases, is delayed by the screen"},
               {"id": "X2", "team": "X", "guards": "O2", "role": "Stays high and connected to O2"},
               {"id": "X3", "team": "X", "guards": "O3", "role": "High-side pressure on the wing passer"},
               {"id": "X4", "team": "X", "guards": "O4", "role": "Stays connected to O4 in the corner (too far to contest)"},
               {"id": "X5", "team": "X", "guards": "O5", "role": "Stays with O5, one show step of controlled help"}]
    marks = {k: et(v) for k, v in M.items() if k not in ("start", "end")}
    marks.update({"start": 0.0, "end": DUR})
    return {"id": "shuffle-cut-v1", "title": "E2A Shuffle Cut V1 (back screen at the high post, chase coverage, layup)",
            "duration": DUR, "concept": "shuffle-cut", "kitSet": "iq", "source": "Original E2A 5v5 possession (owner brief 2026-11-28).",
            "squareUp": True, "catchV2": 2, "handBallClear": True, "v33": "compile", "realism": 3, "v4": True,
            "canonical": "tactical/shuffle/e2a_shuffle_cut_v1.json", "players": players, "tracks": engine_tracks(),
            "ball": ball, "marks": marks, "actions": acts, "claims": [], "screens": [],
            "coords": {"system": "repo (engine)", "owner_to_engine": f"x = -owner x, y = owner y, t = owner t + {PRE}", "basket": [0, 1.575]},
            "v33extra": v33extra(), "v33still": v33still(),
            "notes": ["Generated by tactical/specs/_gen-shuffle.py from the canonical possession."]}


def v33extra():
    return {
        # O1: eyes on the ball during the slow set-up, the V-cut plant (left foot, push off into the cut), head to the
        # passer while cutting, hands ready
        "O1": [{"k": "look", "t": et(0.4), "at": "O3", "b": 0.25},
               {"k": "look", "t": et(1.2), "at": "X1", "b": 0.2},
               {"k": "burst", "t": et(M["k3"] + 0.02), "side": 0, "wide": 0.3},
               {"k": "look", "t": et(1.85), "at": "O3", "b": 0.18},
               {"k": "look", "t": et(M["k5"] + 0.12), "at": "rim", "b": 0.15}],
        "O3": [{"k": "look", "t": et(M["k3"] - 0.2), "at": "O1", "b": 0.2}],
        "O5": [{"k": "look", "t": et(0.35), "at": "X1", "b": 0.2}, {"k": "look", "t": et(2.45), "at": "ball", "b": 0.2}],
        # X1: two quick first steps out of his stance into the chase (a sprint from a standing start, IQ02 lesson),
        # eyes on O1 the whole time (he never sees O5 behind him)
        "X1": [{"k": "step", "side": 0, "lift": et(1.72), "land": et(1.86), "f": 0.12, "l": -0.12, "h": 0.06, "heel": 0.0, "toeOff": 0.6},
               {"k": "step", "side": 1, "lift": et(1.87), "land": et(2.03), "f": 0.26, "l": 0.1, "h": 0.08, "heel": 0.05, "toeOff": 0.55},
               {"k": "look", "t": et(1.6), "at": "O1", "b": 0.12}, {"k": "look", "t": et(2.45), "at": "O1", "b": 0.15}],
        "X5": [{"k": "look", "t": et(1.65), "at": "O1", "b": 0.15}, {"k": "look", "t": et(2.4), "at": "O5", "b": 0.18}],
        "X4": [{"k": "look", "t": et(2.2), "at": "ball", "b": 0.2}],
    }


def v33still():
    return {"O3": [[et(M["k1"] + 0.05), DUR]]}


def sample_engine(play_path, owner_times):
    """positions / velocities exactly as the engine spline draws them (scripts/sample-play-positions.mts)"""
    import subprocess
    out = subprocess.run(["npx", "tsx", "scripts/sample-play-positions.mts", play_path, *[str(et(t)) for t in owner_times]],
                         cwd=T, capture_output=True, text=True, check=True).stdout
    raw = json.loads(out)
    return {t: raw[str(et(t)) if str(et(t)) in raw else repr(float(et(t)))] for t in owner_times}


def canonical(sampled):
    kfs = []
    for k, t, what in KEYS:
        row = {"k": k, "t": t, "what": what, "ball_owner": BALL_OWNER[k], "screen_state": SCREEN_STATE[k],
               "defensive_reaction": REACTION[k], "players": {}}
        for pid in TR:
            ex, ey, vx, vy = sampled[t][pid]
            row["players"][pid] = {"pos": [r3(-ex), r3(ey)], "root_velocity": [r3(-vx), r3(vy)], "speed": r3(math.hypot(vx, vy)), "facing_target": FACING[k][pid], "state": STATE[k][pid],
                                   "assignment": ("guards " + pid.replace("X", "O")) if pid[0] == "X" else "offence"}
        kfs.append(row)
    return {
        "schema": "e2a-tactical-play/1", "id": "e2a_shuffle_cut_v1", "episode": "Shuffle Cut: the screen you never see coming",
        "status": "CANONICAL (designed from the owner brief 2026-11-28 09:18Z). Every render, replay and graphic is generated from this file.",
        "originality": "Original E2A 5v5 possession. Coaching principles only; no copied diagrams, footage or graphics.",
        "principle_sources": [
            "FIBA WABC Coaching Manual Level 3, 2.1.3 'The Shuffle' (manual p.168): ball reversal starts the movement; the first cutter cutting off the high-post screen is the basic Shuffle Cut",
            "FIBA WABC Level 3, 2.2.4 Blind (back) screens (p.186): set behind the defender, at least one step away from his current position",
            "FIBA WABC Level 3, 2.1.1 layer 8 (p.165): the cutter does not move until the screener has set",
            "Coach's Clipboard, Shuffle Offense: O5 screens for O1, who cuts off the screen looking for the feeder's pass for the lay-up",
            "Coach's Clipboard, Cutting and Faking: slow fake then quick cut, quick strong first step; V-cut: plant, push off toward the cut",
            "Coach's Clipboard, Pete Carril's Princeton Offense: cutters have their hands ready, looking for the pass"],
        "coordinates": {"system": "owner", "origin": "centre of the attacking endline", "x": "lateral metres; negative = LEFT of the overhead diagram (basket at the top)",
                        "y": "metres from the endline toward half court", "hoop": [0, 1.575, 3.05], "units": "player centres",
                        "engine_mapping": "engine x = -owner x, engine y = owner y, engine t = owner t + engine_offset_s", "engine_offset_s": PRE},
        "anchors_brief": {k: list(v) for k, v in ANCHOR_BRIEF.items()},
        "anchors_T0": {k: list(v) for k, v in ANCHOR.items()},
        "designed_spots": {"screen_spot_O5": list(S), "O1_setup_plant": list(A), "O1_brush_point": list(P1), "O1_catch": list(C),
                           "O1_release": list(R), "O1_landing": list(L)},
        "timeline_owner_s": M,
        "players": play()["players"],
        "keyframes": kfs,
        "tracks_owner": {k: [[r3(t), [r3(p[0]), r3(p[1])]] for t, p in v] for k, v in TR.items()},
        "ball_events": [
            {"t": 0.0, "event": "O2 holds the ball at the top (live dribble ended at -0.05)"},
            {"t": 0.25, "event": "release O2 -> O3 (chest)"}, {"t": 0.85, "event": "O3 catches (K1)"},
            {"t": 2.10, "event": "release O3 -> O1 (bounce, lead pass into the cut)"}, {"t": 2.85, "event": "O1 catches on the move (K5)"},
            {"t": 3.50, "event": "layup release, left hand, off the glass (K6)"}, {"t": 3.95, "event": "make"}],
        "screen": {"screener": "O5", "screened": "X1", "type": "back (blind) screen at the high post", "set_at": M["screen_set"],
                   "released_at": M["screen_release"], "spot": list(S),
                   "legality": ["stationary from set to release (<= 0.15 m/s)", "set >= 1.2 m (one normal step) from X1, who is stationary when it is set",
                                "behind X1 (outside his field of vision), so the one-step rule applies", "the defender moves into the screener, never the reverse",
                                "the screener stays within his cylinder (feet shoulder width, arms in)"]},
        "coverage": {"name": "chase (trail) the cutter, no switch", "X1": "chases and is delayed", "X5": "shows one step, stays with O5 (no switch)",
                     "X4": "stays home on the corner shooter", "X2": "stays high on O2", "X3": "pressure on the ball from the baseline side (takes the baseline drive away)",
                     "honesty": "This is ONE designed coverage. Against a switch, a top-lock or early weak-side help the shuffle cut does not produce this layup; it then creates other advantages (screener open, second cutter)."},
        "defensive_causes": CAUSES,
        "corrections_log": [
            {"date": "2026-11-28", "what": "anchors T0", "change": "nine of ten anchors kept exactly (centre to centre >= 0.85 m, all in bounds, O4 outside the corner three)"},
            {"date": "2026-11-28", "what": "X2 anchor (0.10, 9.35) -> (-0.40, 9.00), moved 0.61 m", "change": "at 0.86 m from O2 the release of the entry pass (0.44 m in front of O2's chest, toward O3) is inside X2's reach envelope (validator: BLOCKED, -0.19 m). Smallest move tested that leaves the entry OPEN (>= 0.30 m clearance): 1.34 m from O2, on his left hip, still connected and on the top side. Positions 0.25-0.54 m away stayed CONTESTED"},
            {"date": "2026-11-28", "what": "screen spot", "change": "O5 starts at (-1.55, 6.30), 2.37 m from X1: too far for a screen. He walks 1.38 m up and out to (-2.50, 7.30), 1.30 m behind X1 (one normal step + bodies), and sets his feet 0.30 s before O1 plants"},
            {"date": "2026-11-28", "what": "X3", "change": "X3's anchor (4.70, 6.90) is on the low (lane) side of O3: an O3 -> cutter pass from there goes through him (0.06 m). He stays at the anchor through the entry pass (he gives the catch, no full deny), then closes out to the baseline side (6.45, 7.30), 1.17 m from O3: normal pressure that takes the baseline drive away; the pass to the cutter goes to the middle, away from him (validator: 0.6 m clearance)"},
            {"date": "2026-11-28", "what": "O3", "change": "O3 V-cuts 1.15 m up the wing to meet the entry pass at (5.85, 8.30): with X3 at his anchor the catch spot is 1.7 m from X3's shoulders (OPEN); a catch at the anchor spot is inside X3's reach"}]
    }


if __name__ == "__main__":
    p = play()
    os.makedirs(os.path.join(T, "tactical", "shuffle"), exist_ok=True)
    out = os.path.join(T, "tactical", "plays", "shuffle-cut-v1.json")
    json.dump(p, open(out, "w"), indent=1)
    can = canonical(sample_engine(out, [k[1] for k in KEYS]))
    cout = os.path.join(T, "tactical", "shuffle", "e2a_shuffle_cut_v1.json")
    json.dump(can, open(cout, "w"), indent=1)
    print("wrote", out, "and", cout)
