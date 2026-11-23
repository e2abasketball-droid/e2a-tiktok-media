#!/usr/bin/env python3
"""E2A 1-3-1 ZONE: THE TRAP AND THE RACE TO RECOVER (owner master brief 2026-11-23) - the edit, as Remotion props for
Tactical3DV2. Format of the 2-3 Zone MASTER (hook with the key defender, floor coverage areas, freeze + annotated
reads, two contrasted outcomes, closing question) with the E2A Basketball Visual Standard v1 (athleteRenderer v33,
env cinema, marker / legend, one clear tactical camera basket up, short pins and outcome chips).
Plays (tactical/specs/_gen-zone131.py): A zone131-a-corner-trap, B zone131-b-skip-corner (late), C zone131-c-early-closeout.
Timing: --words <words.json> (real narration) or the GUIDE timings below (no voice yet: VISUAL_MASTER_PENDING_AUDIO).
Every shot is anchored to the line(s) it illustrates, so a real take only moves cuts.
  python3 tactical/episodes/_gen-zone131.py --out props.json [--words w.json] [--voice path] [--music path] [--fit ep-fit.json]"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PL = {k: json.load(open(os.path.join(T, "tactical", "plays", f"{v}.json"))) for k, v in
      {"A": "zone131-a-corner-trap", "B": "zone131-b-skip-corner", "C": "zone131-c-early-closeout"}.items()}
GOLD, NAVY, BLUE, WHITE = "#C9A24D", "#0B1C3D", "#8EC5F0", "#FFFFFF"

# the master script (brief sec. 3), one entry per subtitle line; GUIDE start/end in video seconds
LINES = [
    ("one", "One defender.", 0.15, 0.95),
    ("two", "Two corners.", 1.1, 1.9),
    ("gamble", "That's the gamble of the one-three-one.", 2.3, 4.2),
    ("top", "One up top.", 4.9, 5.7),
    ("middle", "Three across the middle.", 5.85, 7.1),
    ("runner", "One runner behind the zone.", 7.25, 8.6),
    ("watch", "Watch the ball reach the corner.", 9.2, 10.8),
    ("trap", "The wing and the runner trap.", 12.0, 13.7),
    ("elbow", "The top drops to the elbow.", 15.3, 16.6),
    ("inside", "The middle protects inside.", 16.8, 18.0),
    ("far", "And the far wing drops.", 18.2, 19.3),
    ("reset", "Now reset.", 19.9, 20.7),
    ("move", "Move the ball to one wing...", 21.3, 22.7),
    ("skip", "then skip it straight to the opposite corner.", 22.9, 25.1),
    ("first", "The far wing closes out first.", 26.3, 27.9),
    ("sprint", "The runner sprints across to take over.", 28.6, 30.6),
    ("late", "If they arrive late...", 32.0, 33.1),
    ("three", "corner three.", 33.3, 34.3),
    ("recover", "Recover on the pass?", 35.8, 36.9),
    ("contested", "Contested.", 37.0, 37.7),
    ("thats", "That's the one-three-one.", 38.5, 39.7),
    ("pressure", "Pressure creates the trap.", 39.85, 41.0),
    ("quick", "Quick passing tests the recovery.", 41.1, 42.6),
]


def guide_words():
    out = []
    for _, text, a, b in LINES:
        ws = text.split()
        tot = sum(len(w) + 1 for w in ws)
        t = a
        for w in ws:
            d = (b - a) * (len(w) + 1) / tot
            out.append({"text": w, "start": round(t, 3), "end": round(t + d * 0.92, 3)})
            t += d
    return out


def line_words(words):
    res, i = {}, 0
    norm = lambda s: "".join(c for c in s.lower() if c.isalnum())
    for key, text, _, _ in LINES:
        n = len(text.split())
        seg = words[i:i + n]
        assert [norm(w["text"]) for w in seg] == [norm(x) for x in text.split()], (key, [w["text"] for w in seg])
        res[key] = seg
        i += n
    assert i == len(words), (i, len(words))
    return res


orb = lambda tg, dist, pitch, yaw=0, fov=50: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
# fit-search (scripts/fit-search.mts, safe band 380-1330 px, all ten feet + head + ball, side 20 px): basket up, behind the offence
MAIN = orb([0.3, 7.81, 0.6], 24.75, 48)            # A 0-5.4 / B 0-5.4: every player and the ball in the band
TOPV = orb([0.12, 8.84, 0.6], 26.5, 24)            # near top-down for the shape (A frozen 0)
TRAP = orb([5.5, 1.3, 0.6], 10.5, 50)              # A 2.9-3.6: O4, X2, X4, O2 (left corner, screen left), basket up
THREE = orb([-3.4, 1.5, 1.2], 16.0, 58)            # B 3.3-4.9 / C 3.4-5.3: O3, X3, X4 + the shot to the rim, basket up
BASE_L = [[0.0, 0.8], [3.3, 0.78], [6.55, 0.85]]   # baseline runner path, to the LEFT corner (screen left)
BASE_R = [[0.0, 0.8], [-3.3, 0.78], [-6.55, 0.85]]


def inv(remap, pt):
    """local shot second where a piecewise-linear remap reaches play time pt"""
    for (a, pa), (b, pb) in zip(remap, remap[1:]):
        if pa <= pt <= pb and pb > pa:
            return a + (b - a) * (pt - pa) / (pb - pa)
    raise ValueError(pt)


def cov(fr, to, **kw):
    return {"type": "coverage", "scheme": "1-3-1", "from": fr, "to": to, **kw}


def build(words, voice, music):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    cuts = {
        "hook": 0.0,
        "gamble": s0("gamble") - 0.15,
        "shape": s0("top") - 0.12,
        "corner": s0("watch") - 0.15,
        "trap": s0("trap") - 0.12,
        "rot": s0("elbow") - 0.15,
        "reset": s0("reset") - 0.15,
        "skip": s0("move") - 0.12,
        "first": s0("first") - 0.15,
        "sprint": s0("sprint") - 0.15,
        "three": s0("late") - 0.12,
        "ontime": s0("recover") - 0.25,
        "close": s0("pressure") - 0.15,
    }
    t_end = e0("quick") + 1.45
    order = list(cuts)
    dur = {k: (cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k] for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]          # line start in shot-local seconds
    Le = lambda k, sh: e0(k) - cuts[sh]
    shots = []

    # 1 HOOK: the formation (A 0), X4 lit gold, the baseline path drawn to one corner, then to the other
    d = dur["hook"]
    lt = L("two", "hook")
    shots.append({"id": "hook", "name": "ONE DEFENDER. TWO CORNERS. X4 lit, the baseline runner path to each corner in turn", "at": 0.0, "play": "A",
                  "remap": [[0, 0.0], [d, 0.0]], "camera": [key(0, MAIN)],
                  "ov3": [{"type": "marker", "player": "X4", "team": "defense", "color": GOLD, "ripple": False, "focusKeys": [[0, 1.0]], "from": 0.0, "to": d},
                          {"type": "ring", "player": "X4", "color": GOLD, "size": 1.25, "pulse": True, "from": 0.0, "to": d},
                          {"type": "glow", "at": [0.0, 2.0], "r": 1.0, "color": GOLD, "strength": 0.55, "from": 0.0, "to": d},
                          {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": BASE_L, "color": GOLD, "width": 0.15, "draw": 0.45, "from": 0.2, "to": d},
                          {"type": "ripple", "at": [6.55, 0.85], "r": 0.7, "rings": 2, "period": 0.8, "color": GOLD, "from": 0.65, "to": lt + 0.2},
                          {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": BASE_R, "color": GOLD, "width": 0.15, "draw": 0.45, "from": lt, "to": d},
                          {"type": "ripple", "at": [-6.55, 0.85], "r": 0.7, "rings": 2, "period": 0.8, "color": GOLD, "from": lt + 0.45, "to": d}],
                  "screen": [{"type": "title", "lines": ["ONE DEFENDER."], "gold": [], "from": 0.0, "to": lt, "y": 236, "size": 104},
                             {"type": "title", "lines": ["ONE DEFENDER.", "TWO CORNERS."], "gold": [1], "from": lt, "to": d - 0.05, "y": 236, "size": 104}]})
    # 2 GAMBLE: the five coverage areas rise; markers reveal attack then defence; legend; 1-3-1 ZONE
    d = dur["gamble"]
    seq = [("O1", "attack"), ("O2", "attack"), ("O5", "attack"), ("O4", "attack"), ("O3", "attack"),
           ("X1", "defense"), ("X2", "defense"), ("X5", "defense"), ("X3", "defense"), ("X4", "defense")]
    mk = [{"type": "marker", "player": p, "team": tm, "from": round(0.25 + j * 0.16, 3), "to": d - 0.1} for j, (p, tm) in enumerate(seq)]
    shots.append({"id": "gamble", "name": "That's the gamble of the 1-3-1: coverage areas + attack/defence markers", "at": cuts["gamble"], "play": "A",
                  "remap": [[0, 0.0], [d, 0.0]], "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="full", reveal=0.14), *mk],
                  "screen": [{"type": "title", "lines": ["1-3-1 ZONE"], "gold": [0], "from": 0.1, "to": d - 0.1, "y": 236, "size": 112},
                             {"type": "legend", "from": 0.25, "to": d - 0.1, "y": 150}]})
    # 3 SHAPE: near top-down; ONE up top (X1), THREE across (X2 X5 X3), ONE runner (X4)
    d = dur["shape"]
    a1, a2 = L("middle", "shape"), L("runner", "shape")
    shots.append({"id": "shape", "name": "1 + 3 + 1: X1 / X2-X5-X3 / X4 in sequence, near top-down", "at": cuts["shape"], "play": "A",
                  "remap": [[0, 0.0], [d, 0.0]], "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, a1, mode="active", active=["X1"], dim=0.3),
                          {"type": "floorText", "text": "CHASER", "at": [0.0, 9.0], "yaw": 0, "size": 0.7, "plate": True, "from": 0.15, "to": a1},
                          cov(a1, a2, mode="active", active=["X2", "X5", "X3"], dim=0.3),
                          {"type": "floorText", "text": "WINGS + CENTER", "at": [0.0, 6.55], "yaw": 0, "size": 0.7, "plate": True, "from": a1 + 0.1, "to": a2},
                          cov(a2, d, mode="active", active=["X4"], dim=0.3),
                          {"type": "floorText", "text": "TAIL", "at": [0.0, 0.55], "yaw": 0, "size": 0.7, "plate": True, "from": a2 + 0.1, "to": d}],
                  "screen": []})
    # 4 BALL TO THE CORNER: O1 -> O2 -> O4 (A 0.3 -> 2.95), one pass line at a time, the areas follow the ball
    d = dur["corner"]
    rm = [[0, 0.25], [d, 2.98]]
    shots.append({"id": "corner", "name": "Watch the ball reach the corner: O1 -> O2 -> O4", "at": cuts["corner"], "play": "A",
                  "remap": rm, "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="active", active=["X2", "X4"], dim=0.5),
                          {"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": inv(rm, 0.7), "to": inv(rm, 1.45) + 0.1},
                          {"type": "passLane", "src": "O2", "dst": "O4", "color": WHITE, "from": inv(rm, 2.35), "to": d}],
                  "screen": []})
    # 5 CORNER TRAP: closer on the left corner, X2 + X4 close (A 2.95 -> 3.5), freeze on the trap
    d = dur["trap"]
    k = min(1.0, d * 0.35)
    shots.append({"id": "trap", "name": "The wing and the runner trap: X2 + X4 on O4, freeze", "at": cuts["trap"], "play": "A",
                  "remap": [[0, 2.98], [k, 3.5], [d, 3.5]], "camera": [key(0, TRAP)],
                  "ov3": [cov(0.0, d, mode="active", active=["X2", "X4"], dim=0.35),
                          {"type": "marker", "player": "X2", "team": "defense", "color": GOLD, "from": k - 0.1, "to": d},
                          {"type": "marker", "player": "X4", "team": "defense", "color": GOLD, "from": k - 0.1, "to": d}],
                  "screen": [{"type": "freeze", "from": k, "to": d},
                             {"type": "pin", "player": "X2", "text": "X2", "tone": "gold", "from": k, "to": d, "size": 40},
                             {"type": "pin", "player": "X4", "text": "X4", "tone": "gold", "from": k, "to": d, "size": 40},
                             {"type": "chip", "text": "CORNER TRAP", "tone": "gold", "align": "center", "size": 64, "from": k + 0.1, "to": d, "y": 470}]})
    # 6 ROTATIONS: wide again, A 3.5 -> 4.4 (slow), ELBOW / PAINT / WEAK BLOCK one at a time
    d = dur["rot"]
    b1, b2 = L("inside", "rot"), L("far", "rot")
    shots.append({"id": "rot", "name": "Top to the elbow, middle inside, far wing drops (A 3.5 -> 4.4)", "at": cuts["rot"], "play": "A",
                  "remap": [[0, 3.5], [d, 4.4]], "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, b1, mode="active", active=["X1"], dim=0.4),
                          cov(b1, b2, mode="active", active=["X5"], dim=0.4),
                          cov(b2, d, mode="active", active=["X3"], dim=0.4)],
                  "screen": [{"type": "pin", "player": "X1", "text": "ELBOW", "tone": "gold", "from": 0.15, "to": b1 + 0.1, "size": 40},
                             {"type": "pin", "player": "X5", "text": "PAINT", "tone": "gold", "from": b1, "to": b2 + 0.1, "size": 40},
                             {"type": "pin", "player": "X3", "text": "WEAK BLOCK", "tone": "gold", "from": b2, "to": d, "size": 40}]})
    # 7 RESET: hard editorial cut to a NEW possession (B 0 frozen)
    d = dur["reset"]
    shots.append({"id": "reset", "name": "Now reset: NEW POSSESSION", "at": cuts["reset"], "play": "B",
                  "remap": [[0, 0.0], [d, 0.0]], "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="full", reveal=0.07, dim=0.6)],
                  "screen": [{"type": "flash", "color": "#FFE9C8", "strength": 0.16, "from": 0.0, "to": 0.2},
                             {"type": "stamp", "text": "NEW POSSESSION", "tone": "white", "y": 250, "from": 0.0, "to": d, "instant": True}]})
    # 8 SKIP: O1 -> O2 (B 0.3 -> 1.45), O2 loads, release on "skip", flight at ~0.45x
    d = dur["skip"]
    tsk = wd("skip", 1) - cuts["skip"]
    rm = [[0, 0.3], [tsk, 2.1], [d, 2.55]]
    shots.append({"id": "skip", "name": "Move the ball to one wing, then SKIP straight to the opposite corner", "at": cuts["skip"], "play": "B",
                  "remap": rm, "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="full", dim=0.55),
                          {"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": inv(rm, 0.7), "to": inv(rm, 1.45) + 0.1},
                          {"type": "passLane", "src": "O2", "dst": "O3", "color": WHITE, "from": tsk, "to": d},
                          {"type": "ballTrail", "len": 0.35, "from": tsk, "to": d}],
                  "screen": [{"type": "pin", "player": "O2", "text": "SKIP", "tone": "gold", "from": tsk - 0.1, "to": tsk + 1.0, "size": 40}]})
    # 9 FIRST CLOSEOUT: freeze with the ball in the air, X3's route lit (FIRST), then resume to the catch
    d = dur["first"]
    fz = min(0.7, d * 0.3)
    rm = [[0, 2.55], [fz, 2.55], [d, 3.0]]
    shots.append({"id": "first", "name": "The far wing closes out first: X3 from the weak-side block", "at": cuts["first"], "play": "B",
                  "remap": rm, "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="active", active=["X3"], dim=0.4),
                          {"type": "marker", "player": "X3", "team": "defense", "color": GOLD, "from": 0.0, "to": d},
                          {"type": "route", "player": "X3", "t0": 2.55, "t1": 4.05, "color": GOLD, "width": 0.09, "draw": 0.4, "consume": True, "from": 0.1, "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": fz},
                             {"type": "pin", "player": "X3", "text": "FIRST", "tone": "gold", "from": 0.1, "to": d, "size": 40}]})
    # 10 RUNNER: X4's baseline route fills as he runs it (trail), the ball arrives (B 3.0 -> 3.62)
    d = dur["sprint"]
    shots.append({"id": "sprint", "name": "The runner sprints across to take over: X4's path fills at his speed", "at": cuts["sprint"], "play": "B",
                  "remap": [[0, 3.0], [d, 3.62]], "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="active", active=["X3", "X4"], dim=0.4),
                          {"type": "route", "player": "X4", "t0": 2.32, "t1": 4.37, "color": BLUE, "width": 0.09, "trail": True, "from": 0.0, "to": d},
                          {"type": "marker", "player": "X4", "team": "defense", "color": GOLD, "from": 0.0, "to": d}],
                  "screen": [{"type": "pin", "player": "X4", "text": "RECOVER", "tone": "white", "from": 0.2, "to": d, "size": 40}]})
    # 11 LATE -> CORNER THREE: closer on the right corner, catch-and-shoot, the ball in (B 3.62 -> 4.95)
    d = dur["three"]
    tmk = PL["B"]["marks"]["make"]
    rm = [[0, 3.62], [d - 0.55, tmk], [d, tmk + 0.25]]
    shots.append({"id": "three", "name": "If they arrive late... corner three (feet behind the line, ball in)", "at": cuts["three"], "play": "B",
                  "remap": rm, "camera": [key(0, THREE)],
                  "ov3": [{"type": "ballTrail", "len": 0.3, "from": inv(rm, 3.68), "to": d - 0.4},
                          {"type": "glow", "hoop": True, "r": 1.0, "color": GOLD, "strength": 0.55, "from": d - 0.6, "to": d}],
                  "screen": [{"type": "pin", "player": "X3", "text": "LATE", "tone": "white", "from": 0.1, "to": 1.2, "size": 40},
                             {"type": "chip", "text": "THREE.", "tone": "gold", "align": "right", "size": 64, "from": d - 0.6, "to": d, "y": 1230}]})
    # 12 ON TIME: same skip, C from 2.0: X3 breaks on the release, contest, miss; X4 arrives and bumps X3 back
    d = dur["ontime"]
    tc = L("contested", "ontime")
    rm = [[0, 2.0], [tc, 3.72], [d, 5.4]]
    shots.append({"id": "ontime", "name": "Recover on the pass? Contested. X4 bumps, X3 back to the wing (C 2.0 -> 5.4)", "at": cuts["ontime"], "play": "C",
                  "remap": rm, "camera": [key(0, MAIN), key(max(0.4, tc - 0.5), THREE, "inOut"), key(d, THREE)],
                  "ov3": [{"type": "marker", "player": "X3", "team": "defense", "color": GOLD, "from": 0.0, "to": tc + 0.6},
                          {"type": "route", "player": "X4", "t0": 2.18, "t1": 5.13, "color": BLUE, "width": 0.08, "trail": True, "from": 0.0, "to": d}],
                  "screen": [{"type": "stamp", "text": "ON TIME", "tone": "gold", "y": 250, "from": 0.0, "to": 0.9, "instant": True},
                             {"type": "chip", "text": "CONTESTED.", "tone": "gold", "align": "right", "size": 64, "from": tc, "to": tc + 1.3, "y": 1230},
                             {"type": "pin", "player": "X4", "text": "BUMP", "tone": "white", "from": inv(rm, 4.45), "to": d, "size": 40}]})
    # 13 CLOSE: the shape again (A 0) - same frame as the hook for the loop; TRAP OR RECOVER?, logo
    d = dur["close"]
    shots.append({"id": "close", "name": "Pressure creates the trap, quick passing tests the recovery; TRAP OR RECOVER?", "at": cuts["close"], "play": "A",
                  "remap": [[0, 0.0], [d, 0.0]], "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="full", dim=0.5),
                          {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": BASE_L, "color": GOLD, "width": 0.07, "draw": 0.5, "from": 0.3, "to": d},
                          {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": BASE_R, "color": GOLD, "width": 0.07, "draw": 0.5, "from": 0.3, "to": d}],
                  "screen": [{"type": "title", "lines": ["PRESSURE.", "RECOVERY."], "gold": [0], "from": 0.2, "to": d - 1.75, "y": 236, "size": 96},
                             {"type": "title", "lines": ["TRAP OR", "RECOVER?"], "gold": [0], "from": d - 1.7, "to": d, "y": 236, "size": 100},
                             {"type": "logo", "big": False, "from": d - 1.6, "to": d}]})
    ep = {
        "id": "zone-131", "title": "1-3-1 ZONE: THE TRAP AND THE RACE TO RECOVER", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33",
        "words": words,
        "subtitleGroups": [len(t.split()) for _, t, _, _ in LINES],
        "subtitleBlock": True, "subtitleY": 1390, "subtitleHide": [[t_end - 1.7, 999]],
        "keywords": ["One", "Two", "corners.", "one-three-one.", "corner.", "trap.", "elbow.", "inside.", "drops.", "reset.", "skip",
                     "first.", "sprints", "late...", "three.", "Contested.", "Pressure", "recovery."],
        "gradeBottom": 0.3,
        "shots": shots, "plays": PL,
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    meta = {"duration": round(t_end, 3), "cuts": {k: round(v, 3) for k, v in cuts.items()}}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words")
    ap.add_argument("--voice", default="tactical/realism-v3-3/silence.mp3")
    ap.add_argument("--music")
    ap.add_argument("--fit", help="also write a frame-fit episode (plays by name) + its words file")
    a = ap.parse_args()
    words = json.load(open(a.words)) if a.words else guide_words()
    props, meta = build(words, a.voice, a.music)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"])
        ep["plays"] = {k: v["id"] for k, v in PL.items()}
        json.dump(ep, open(a.fit, "w"))
        json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    print(json.dumps(meta))
