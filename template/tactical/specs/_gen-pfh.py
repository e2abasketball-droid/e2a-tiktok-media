#!/usr/bin/env python3
"""PISTOL FAKE HANDOFF in transition (owner brief E2A-Prompt-Claude-Pistol-Fake-Handoff-PCD.md, 2026-11-20).
O1 kicks the ball ahead to the right wing O2 and chases his pass for the handoff back.
  keep  pfh-keep  X2 bites on the handoff (turns + steps inside) -> O2 KEEPS it (O1 runs by empty-handed), first
                  dribble to the baseline, right-hand layup (make).
  give  pfh-give  same entry; X2 holds the baseline angle -> O2 really hands off to O1 (one transfer), O1 attacks the
                  middle; the branch closes on O1's first steps.
The brief's anchor tables (sec. 4) are used AS DATA (S-clock anchor -> waypoint at S/30 s). Axis mapping as in Double
Drag / Blind Pig: brief x > 0 = offence's RIGHT; repo x > 0 = offence's LEFT, so repo x = -brief x. y, z unchanged.
  python3 tactical/specs/_gen-pfh.py   (writes tactical/specs/pfh-{keep,give}.spec.json + tactical/plays/)"""
import json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
S = lambda n: round(n / 30, 4)
M = lambda p: [round(-p[0], 3), p[1]]   # brief axes -> repo axes
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = ("E2A didactic construction (owner brief 'Pistol Fake Handoff en transicion', S-clock anchors S000-S126) on: FIBA "
       "WABC Coaching Manual level 3 sec. 2.3.1 (Pistol entry: pass ahead to the wing, the passer follows for the return); "
       "WABC level 2 sec. 2.1.1 (fake hand-off: the receiver who has not dribbled fakes and attacks when the ball "
       "defender anticipates); Tanner Massey 'Early Offense Pistol' (family reference '21 Keep'); FIBA Official Rules "
       "2026 v1.1 arts. 24 (dribble), 25 (travelling), 33 (contact).")

PLAYERS = [P("O1", "O", "Point guard: kicks the ball ahead to the wing and chases his pass for the handoff back"),
           P("O2", "O", "Right wing: catches ahead, sells the handoff, keeps it (keep) / gives it (give)"),
           P("O3", "O", "Weak-side runner: fills the left corner"),
           P("O4", "O", "Weak-side wing: fills the left slot"),
           P("O5", "O", "Trailer big: runs the middle to the high slot"),
           P("X1", "X", "On O1: chases him after the pass", "O1"),
           P("X2", "X", "On O2 = THE DEFENDER WHO DECIDES: bites on the handoff (keep) / holds the baseline (give)", "O2"),
           P("X3", "X", "Weak-side corner", "O3"),
           P("X4", "X", "Weak-side slot", "O4"),
           P("X5", "X", "On O5: starts high, late help from the top", "O5")]

# ---- brief sec. 4 anchors (brief axes), branch keep
OFF = {
 "O1": {0: (2.50, 13.40), 10: (2.85, 12.00), 29: (3.90, 9.05), 43: (4.72, 7.36), 51: (4.93, 6.55), 59: (4.35, 5.98), 72: (3.42, 6.03), 90: (2.90, 6.70), 110: (2.57, 7.15), 126: (2.56, 7.19)},
 "O2": {0: (5.75, 9.42), 10: (5.78, 8.31), 29: (5.70, 6.73), 43: (5.70, 6.55), 51: (5.70, 6.55), 59: (6.12, 5.97), 72: (5.97, 4.39), 90: (3.86, 2.75), 110: (1.35, 1.95), 126: (0.81, 1.89)},
 "O3": {0: (-6.62, 6.10), 10: (-6.71, 5.22), 29: (-6.84, 2.61), 43: (-6.86, 1.77), 51: (-6.87, 1.77), 59: (-6.87, 1.77), 72: (-6.86, 1.77), 90: (-6.85, 1.79), 110: (-6.80, 1.79), 126: (-6.77, 1.80)},
 "O4": {0: (-4.20, 11.65), 10: (-4.45, 10.37), 29: (-4.78, 8.18), 43: (-4.77, 7.34), 51: (-4.75, 7.29), 59: (-4.75, 7.31), 72: (-4.68, 7.39), 90: (-4.62, 7.48), 110: (-4.58, 7.51), 126: (-4.54, 7.44)},
 "O5": {0: (0.40, 13.50), 10: (0.47, 12.39), 29: (0.62, 10.23), 43: (0.70, 8.74), 51: (0.75, 8.52), 59: (0.79, 8.43), 72: (0.88, 8.35), 90: (0.98, 8.18), 110: (1.05, 7.84), 126: (1.09, 7.54)},
}
DEF = {
 "X1": {0: (2.78, 12.25), 10: (2.95, 10.95), 29: (3.45, 8.08), 43: (3.93, 7.72), 51: (4.06, 6.90), 59: (3.62, 6.40), 72: (2.69, 6.49), 90: (2.12, 6.82), 110: (1.84, 7.16), 126: (1.90, 7.27)},
 "X2": {0: (5.02, 8.21), 10: (5.01, 7.56), 29: (4.94, 6.10), 43: (4.95, 5.60), 51: (4.45, 5.90), 59: (4.06, 5.22), 72: (5.04, 5.12), 90: (4.88, 4.40), 110: (3.06, 3.56), 126: (2.81, 3.63)},
 "X3": {0: (-5.60, 4.91), 10: (-5.67, 3.91), 29: (-5.68, 2.60), 43: (-5.68, 2.44), 51: (-5.64, 2.46), 59: (-5.63, 2.47), 72: (-5.60, 2.53), 90: (-5.51, 2.63), 110: (-5.42, 2.66), 126: (-5.42, 2.67)},
 "X4": {0: (-3.97, 10.33), 10: (-3.89, 9.12), 29: (-3.91, 7.03), 43: (-3.93, 6.81), 51: (-3.93, 6.79), 59: (-3.90, 6.81), 72: (-3.80, 6.78), 90: (-3.67, 6.72), 110: (-3.60, 6.73), 126: (-3.57, 6.75)},
 "X5": {0: (0.57, 11.53), 10: (0.65, 10.58), 29: (0.81, 8.97), 43: (1.10, 7.93), 51: (1.15, 7.84), 59: (1.33, 7.21), 72: (1.86, 5.77), 90: (3.05, 4.13), 110: (2.15, 3.26), 126: (1.96, 3.18)},
}
# keep: O2 stays planted until the first dribble is out of his hand (S054) -> extra anchor S054 at the S051 spot
KEEP_EXTRA = {"O1": {51: (4.70, 6.55)},
              "O2": {54: (5.70, 6.55), 55: (5.705, 6.54), 59: (5.78, 6.36), 66: (6.06, 5.55), 72: (6.05, 4.75)},
              "X2": {38: (4.95, 5.63), 44: (4.95, 5.60), 47: (4.925, 5.625), 51: (4.86, 5.69), 55: (4.80, 5.53), 59: (4.70, 5.30)}}
# give (brief sec. 4 'Rama give', E2A layout): shared to S043, then X2 holds the baseline angle, O2 hands off at S050-S052,
# O1 takes it toward the middle, X1 chases, X5 steps up; the branch closes on O1's first steps (DUR_GIVE)
GIVE = {
 "O1": {43: (4.72, 7.36), 51: (4.86, 6.55), 59: (4.58, 6.08), 72: (3.40, 5.22), 90: (2.15, 4.38), 100: (1.70, 4.05)},
 "O2": {43: (5.70, 6.55), 51: (5.70, 6.55), 60: (5.72, 6.55), 85: (6.00, 6.35), 100: (6.05, 6.30)},
 "X2": {43: (4.95, 5.60), 51: (5.15, 5.55), 59: (5.18, 5.55), 72: (5.18, 5.58), 90: (5.30, 5.55), 100: (5.32, 5.55)},
 "X1": {43: (3.93, 7.72), 51: (4.06, 6.90), 59: (4.00, 6.62), 72: (3.55, 6.08), 90: (2.60, 5.25), 100: (2.25, 4.95)},
 "X5": {43: (1.10, 7.93), 51: (1.15, 7.84), 59: (1.33, 7.21), 72: (1.75, 6.20), 90: (1.45, 5.10), 100: (1.40, 4.80)},
}
ADJUST = [
 "O2 (keep): first steps S054 -> S072 re-anchored (S059 (5.88, 6.22), S066 (6.10, 5.45), S072 (6.05, 4.75); brief S059 (6.12, 5.97), S072 (5.97, 4.39)): the brief's 0.71 m in 5 frames from a standstill was an 82 m/s2 start",
 "O2 (keep): S110 (1.45, 1.99) -> (1.35, 1.95): layup take-off inside 1.5 m of the rim",
 "X2 (keep): settled S038-S045 at the S043 spot (extra anchors), the bite starts after the offer is visible (S045)",
 "X1: S010 (3.16, 10.95) -> (2.95, 10.95): the kick-ahead lane was 0.59 m from X1 (>= 0.6 m)",
 "give: X5 S072-S100 re-laid (stepped into O1 at S093, 0.37 m); handoff S048 -> S055 (0.23 s, both pairs of hands on the ball)",
 "O2 (keep): extra anchor S054 = the S051 spot: he stays on both feet until the first dribble has left his hand (FIBA art. 24/25: the pivot foot may not be lifted before the ball is released for the dribble). The brief's S051 -> S059 run is kept (now S054 -> S059)",
 "O2: the held ball sits in front of the CHEST (engine opt-in hold.pocket, rig heading), not along the travel facing, so it stays in front of the trunk while he turns to O1",
 "O1 (keep): S051 (4.93, 6.55) -> (4.70, 6.55): he runs by 1.0 m inside O2 (at 0.77 m the offered ball was inside his trunk, qc-catch); give keeps (4.80, 6.55) to take the ball",
 "fake (keep): the ball travels 0.10 m toward O1 and 5 cm down S043 -> S049, stays to S051 (O1 runs by, hands offered, no contact), back to the pocket by S054 (hold.present); O2's hands never leave it",
 "give: E2A layout after S043 (the brief gives X2 (5.04, 5.72) at S051 only): one handoff O2 -> O1 S047 -> S055 (style handoff: both pairs of hands ride the same ball; O1 owns it at S055), O1 dribbles to the middle",
 "engine opt-in play.handBallClear (rig): a player who neither holds the ball nor reaches for a pass to him keeps his fingers out of it; O1's run swing + offered hand put a fingertip 4 cm from the ball centre at S045 (inside the ball) in both branches -> now >= 0.15 m in keep (hands offered, no touch)",
 "first floor contact of O2's dribble ~S058-S060 (brief 'aprox. S062-S064'): the dribble starts at S054 so the ball is out before the first step",
]
DUR_KEEP = S(170)
DUR_GIVE = S(110)


def track(anchors, dur):
    ks = sorted(anchors)
    wp = [[S(k), *M(anchors[k])] for k in ks]
    if len(wp) > 1 and wp[1][1:] != wp[0][1:]:
        wp[0].append("fly")
    if wp[-1][0] < dur:
        wp.append([dur, wp[-1][1], wp[-1][2]])
    return wp


def tracks(kind):
    dur = DUR_KEEP if kind == "keep" else DUR_GIVE
    base = {pid: dict(a) for pid, a in {**OFF, **DEF}.items()}
    if kind == "keep":
        for pid, ex in KEEP_EXTRA.items():
            base[pid].update(ex)
    else:
        for pid, g in GIVE.items():
            a = {k: v for k, v in base[pid].items() if k <= 43}
            a.update(g)
            base[pid] = a
        base = {pid: {k: v for k, v in a.items() if k <= 100} for pid, a in base.items()}
    return {pid: track(a, dur) for pid, a in base.items()}


def actions(kind):
    keep = kind == "keep"
    dur = DUR_KEEP if keep else DUR_GIVE
    a = {
        "O1": [{"type": "face", "from": S(34), "to": S(50 if keep else 45), "face": "O2"},
               {"type": "catchReady", "from": S(43), "to": S(50 if keep else 48), "face": "O2"}],
        "O2": [{"type": "face", "from": S(38), "to": S(52), "face": "O1"}],
        "O3": [{"type": "call", "from": S(32), "to": S(52)}],
        "O4": [{"type": "call", "from": S(24), "to": S(44)}],
        "O5": [],
        "X1": [st("O1", 0, dur)],
        "X3": [st("ball", S(10), dur)],
        "X4": [st("ball", S(10), dur)],
    }
    if keep:
        # X2: guards O2, then BITES: chest + front hand to the handoff point (O1's run) S045-S055, re-plants, chases
        a["X2"] = [st("O2", 0, S(44)), {"type": "topLock", "from": S(45), "to": S(55), "face": "O1", "side": 1},
                   st("O2", S(57), dur)]
        a["X5"] = [st("O5", 0, S(58)), st("O2", S(60), S(104)), {"type": "contest", "from": S(106), "to": S(122)}]
    else:
        a["X2"] = [st("O2", 0, dur)]
        a["X5"] = [st("O5", 0, S(54)), st("O1", S(56), dur)]
    return a


def ball(kind):
    ev = [{"type": "hold", "player": "O1", "from": 0, "to": S(10), "dribble": True, "hand": 1},
          {"type": "pass", "from": "O1", "to": "O2", "t0": S(10), "t1": S(29), "style": "chest", "eyes": 0.35, "lead": True}]
    if kind == "keep":
        ev += [{"type": "hold", "player": "O2", "from": S(29), "to": S(54), "pocket": True,
                "present": {"toward": "O1", "from": S(43), "peak": S(49), "hold": S(51), "to": S(54), "amt": 0.10, "dz": -0.05}},
               {"type": "hold", "player": "O2", "from": S(54), "to": S(100), "dribble": True, "hand": 1},
               {"type": "hold", "player": "O2", "from": S(100), "to": S(110), "pocket": True},
               {"type": "layup", "player": "O2", "t0": S(110), "t1": S(124), "make": True}]
    else:
        ev += [{"type": "hold", "player": "O2", "from": S(29), "to": S(47), "pocket": True,
                "present": {"toward": "O1", "from": S(42), "peak": S(47), "to": S(60), "amt": 0.17, "dz": -0.05}},
               {"type": "pass", "from": "O2", "to": "O1", "t0": S(47), "t1": S(55), "style": "handoff"},
               {"type": "hold", "player": "O1", "from": S(55), "to": S(65), "pocket": True},
               {"type": "hold", "player": "O1", "from": S(65), "to": DUR_GIVE, "dribble": True, "hand": 1}]
    return ev


def spec(kind):
    keep = kind == "keep"
    s = {"id": f"pfh-{kind}",
         "title": ("Pistol Fake Handoff (keep): X2 bites on the handoff, O2 keeps it, baseline drive, layup" if keep else
                   "Pistol Fake Handoff (give): X2 holds the baseline, O2 hands off to O1 for real"),
         "duration": DUR_KEEP if keep else DUR_GIVE, "concept": "pistol-fake-handoff", "source": SRC, "squareUp": False, "catchV2": 2, "handBallClear": True,
         "players": PLAYERS, "tracks": tracks(kind), "ball": ball(kind), "actions": actions(kind), "screens": [],
         "sclock": {"fps": 30, "mirrorX": True, "shared_until": 43, "anchors": "brief sec. 4", "adjust": ADJUST},
         # scripts/qc-handoff.mts: keep = O2 never loses the ball during the fake (catch to the layup gather);
         # give = ONE hand-off O2 -> O1, both pairs of hands on the ball at one instant
         "expect": ({"owner": {"player": "O2", "from": S(30), "to": S(100)}} if keep else
                    {"transfer": {"from": "O2", "to": "O1", "t0": S(43), "t1": S(60)}})}
    common = {"start": 0, "kick": S(10), "catch": S(29), "settle": S(43), "offer": S(49)}
    if keep:
        s["marks"] = {**common, "bite": S(51), "keep": S(54), "bounce": S(59), "gather": S(100), "release": S(114), "make": S(124), "end": s["duration"]}
        s["claims"] = [
            {"type": "reacts_after", "player": "X2", "event": "settle", "min": 0.05, "says": "Now watch his defender. He bites on the handoff."},
            {"type": "near", "a": "O1", "b": "O2", "at": "bite", "max": 1.4, "says": "The guard chases his pass (handoff distance)."},
            {"type": "near_rim", "player": "O2", "at": "gather", "max": 2.6, "says": "There goes the baseline."},
            {"type": "order", "marks": ["kick", "catch", "settle", "offer", "bite", "keep", "bounce", "gather", "release", "make"], "says": "kick ahead, fake, keep, baseline, layup"}]
    else:
        s["marks"] = {**common, "handoff": S(47), "owner": S(55), "end": s["duration"]}
        s["claims"] = [
            {"type": "near", "a": "O1", "b": "O2", "at": "handoff", "max": 1.2, "says": "look for the handoff back"},
            {"type": "order", "marks": ["kick", "catch", "settle", "handoff", "owner"], "says": "kick ahead, real handoff"}]
    return s


if __name__ == "__main__":
    for k in ("keep", "give"):
        s = spec(k)
        json.dump(s, open(os.path.join(D, f"{s['id']}.spec.json"), "w"), indent=1)
        json.dump(s, open(os.path.join(T, "tactical", "plays", f"{s['id']}.json"), "w"), indent=1)
        print("built", s["id"], json.dumps(s["marks"]))
