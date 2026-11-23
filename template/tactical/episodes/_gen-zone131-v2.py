#!/usr/bin/env python3
"""E2A 1-3-1 ZONE V2 (owner viral-retention brief 2026-11-23) - the edit, as Remotion props for Tactical3DV2.
Same plays, characters (v33), court, light and floor graphics as V1 (tactical/episodes/_gen-zone131.py); the change is
editorial: cold open on the skip in flight (question first), a faster 1/3/1, the corner trap, a one-cut reset, X3 FIRST and
the X4 takeover, then the LATE vs ON TIME payoff as a synchronised split screen from the SAME state (plays B and C are
identical until the skip release; same camera, same clock), and a close that lands on the cold-open frame (loop).
Voice: the approved Deuce take re-edited with scripts/tactical-voice-edit.py (no synthesis, 0 credits).
  python3 tactical/episodes/_gen-zone131-v2.py --out props.json --words w.json [--voice path] [--music path]
                                               [--hook A|B] [--only hook] [--fit ep-fit.json]"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PL = {k: json.load(open(os.path.join(T, "tactical", "plays", f"{v}.json"))) for k, v in
      {"A": "zone131-a-corner-trap", "B": "zone131-b-skip-corner", "C": "zone131-c-early-closeout"}.items()}
GOLD, NAVY, BLUE, WHITE, RED = "#C9A24D", "#0B1C3D", "#8EC5F0", "#FFFFFF", "#E5483A"

# subtitle phrases of the V2 voice edit, in order (tactical/episodes/zone131v2/zone131v2-voice.json)
LINES = [
    ("one", "One defender."), ("two", "Two corners."),
    ("top", "One up top."), ("middle", "Three across the middle."), ("runner", "One runner behind the zone."),
    ("watch", "Watch the ball reach the corner."), ("trap", "The wing and the runner trap."),
    ("elbow", "The top drops to the elbow."), ("inside", "The middle protects inside."),
    ("reset", "Now reset."), ("move", "Move the ball to one wing..."), ("skip", "then skip it straight to the opposite corner."),
    ("first", "The far wing closes out first."), ("sprint", "The runner sprints across to take over."),
    ("late", "If they arrive late..."), ("three", "corner three."), ("recover", "Recover on the pass?"), ("contested", "Contested."),
    ("pressure", "Pressure creates the trap."), ("quick", "Quick passing tests the recovery."),
]


def line_words(words):
    res, i = {}, 0
    norm = lambda s: "".join(c for c in s.lower() if c.isalnum())
    for k, text in LINES:
        n = len(text.split())
        seg = words[i:i + n]
        assert [norm(w["text"]) for w in seg] == [norm(x) for x in text.split()], (k, [w["text"] for w in seg])
        res[k] = seg
        i += n
    assert i == len(words), (i, len(words))
    return res


orb = lambda tg, dist, pitch, yaw=0, fov=50: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
# frame-fit over the whole edit (ten feet + head + ball, band 380-1330, side 20): V1 MAIN was 24.75 m; this is the tightest that keeps
# both corners in (the frame is width-bound): players ~6 % bigger
MAIN = orb([0.3, 8.92, 0.6], 23.25, 52)
PUSH = MAIN                                          # (a push-in loses O2 or O3 at the sides: frame-fit)
HOOK = orb([-0.21, 2.68, 0.6], 13.5, 54, -40)        # cold open: O3, X3, X4 + the ball from 2.25 (fit-search), 40 deg off basket-up
TRAP = orb([5.6, 0.9, 0.6], 10.5, 46)               # V1 trap camera (re-framed), left corner, basket up
SPLIT = orb([-3.8, 0.45, 0.6], 11.0, 46)            # payoff halves 1080x960: O3, X3, X4, X5 + the shot to the rim, B and C
BASE_R = [[0.0, 0.8], [-3.3, 0.78], [-6.55, 0.85]]  # baseline runner path to the RIGHT corner (screen right)
BASE_L = [[0.0, 0.8], [3.3, 0.78], [6.55, 0.85]]


def inv(remap, pt):
    for (a, pa), (b, pb) in zip(remap, remap[1:]):
        if pa <= pt <= pb and pb > pa:
            return a + (b - a) * (pt - pa) / (pb - pa)
    raise ValueError(pt)


def cov(fr, to, **kw):
    return {"type": "coverage", "scheme": "1-3-1", "from": fr, "to": to, **kw}


TITLE = dict(y=236, reveal="block")


def hook_shot(variant, d, lt):
    """cold open, ~2.3 s; lt = local start of 'Two corners.'"""
    # one title that grows a line: the first line never re-enters (no ghost / doubled letters), hard cut at the end
    titles = [{"type": "title", "lines": ["ONE DEFENDER."], "gold": [], "from": 0.0, "to": lt, "size": 104, "noOut": True, "hold": 1, **TITLE},
              {"type": "title", "lines": ["ONE DEFENDER.", "TWO CORNERS."], "gold": [1], "from": lt, "to": d, "size": 104, "hold": 1, "noOut": True, **TITLE}]
    if variant == "A":
        # the skip leaves O2's hands (B 2.1), X3 starts, X4 is still on the left of the rim; the ball is in the air when we cut
        rm = [[0, 2.25], [d - 0.45, 2.8], [d, 2.8]]
        return {"id": "hook", "name": "HOOK A: skip in flight, X4 far from the right corner - cut before the answer", "at": 0.0, "play": "B",
                "remap": rm, "camera": [key(0, HOOK)],
                "ov3": [{"type": "marker", "player": "X4", "team": "defense", "color": GOLD, "ripple": False, "focusKeys": [[0, 1.0]], "from": 0.0, "to": d},
                        {"type": "ring", "player": "X4", "color": GOLD, "size": 1.25, "pulse": True, "from": 0.0, "to": d},
                        {"type": "ballTrail", "len": 0.35, "from": 0.0, "to": d},
                        {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": BASE_R, "color": GOLD, "width": 0.12, "draw": 0.5, "from": 0.1, "to": d},
                        {"type": "ripple", "at": [-6.55, 0.85], "r": 0.7, "rings": 2, "period": 0.8, "color": GOLD, "from": lt, "to": d}],
                "screen": [*titles, {"type": "freeze", "from": d - 0.45, "to": d},
                           {"type": "chip", "text": "CAN HE GET THERE?", "tone": "gold", "align": "center", "size": 54, "from": d - 0.6, "to": d + 0.25, "y": 1240}]}
    # B: the trap on the left, then the open shooter in the far corner lights up (O3) and the runner's distance
    rm = [[0, 3.0], [0.55, 3.5], [d, 3.5]]
    return {"id": "hook", "name": "HOOK B: corner trap freeze, the open opposite corner and X4's distance", "at": 0.0, "play": "A",
            "remap": rm, "camera": [key(0, MAIN), key(d, PUSH, "inOut")],
            "ov3": [cov(0.0, d, mode="active", active=["X2", "X4"], dim=0.35),
                    {"type": "marker", "player": "X4", "team": "defense", "color": GOLD, "ripple": False, "from": 0.0, "to": d},
                    {"type": "marker", "player": "O3", "team": "attack", "color": GOLD, "from": lt - 0.1, "to": d},
                    {"type": "ripple", "at": [-6.88, 1.25], "r": 0.7, "rings": 2, "period": 0.8, "color": GOLD, "from": lt, "to": d},
                    {"type": "route", "player": "X4", "t0": 0, "t1": 0, "pts": [[5.4, 0.85], [0.0, 0.8], [-6.3, 0.95]], "color": GOLD, "width": 0.12, "draw": 0.45, "from": lt, "to": d}],
            "screen": [*titles, {"type": "freeze", "from": 0.55, "to": d},
                       {"type": "chip", "text": "THE HIDDEN WEAKNESS", "tone": "gold", "align": "center", "size": 54, "from": d - 0.6, "to": d + 0.25, "y": 1240}]}


def build(words, voice, music, hook="A", only=None):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    cuts = {"hook": 0.0, "shape": s0("top") - 0.14, "corner": s0("watch") - 0.14, "trap": s0("trap") - 0.14,
            "rot": s0("elbow") - 0.14, "reskip": s0("reset") - 0.12, "first": s0("first") - 0.16, "sprint": s0("sprint") - 0.12,
            "payoff": s0("late") - 0.16, "close": s0("pressure") - 0.2, "loop": s0("quick") - 0.12}
    t_end = e0("quick") + 1.25
    order = list(cuts)
    dur = {k: (cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k] for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    shots = []

    # 1 COLD OPEN (hook A or B)
    shots.append(hook_shot(hook, dur["hook"], L("two", "hook")))
    if only == "hook":
        t_end = dur["hook"]
    else:
        # 2 SHAPE 1 / 3 / 1: one group lit at a time while the camera pushes in a touch
        d = dur["shape"]
        a1, a2 = L("middle", "shape"), L("runner", "shape")
        shots.append({"id": "shape", "name": "1 / 3 / 1: X1, then X2-X5-X3, then X4 (one group at a time)", "at": cuts["shape"], "play": "A",
                      "remap": [[0, 0.0], [d, 0.0]], "camera": [key(0, MAIN), key(d, PUSH, "inOut")],
                      "ov3": [cov(0.0, a1, mode="active", active=["X1"], dim=0.25),
                              {"type": "floorText", "text": "1  UP TOP", "at": [2.6, 7.6], "yaw": 0, "size": 0.75, "plate": True, "from": 0.1, "to": a1},
                              cov(a1, a2, mode="active", active=["X2", "X5", "X3"], dim=0.25),
                              {"type": "floorText", "text": "3  ACROSS", "at": [0.0, 6.35], "yaw": 0, "size": 0.75, "plate": True, "from": a1 + 0.05, "to": a2},
                              cov(a2, d, mode="active", active=["X4"], dim=0.25),
                              {"type": "marker", "player": "X4", "team": "defense", "color": GOLD, "from": a2, "to": d},
                              {"type": "floorText", "text": "1  RUNNER", "at": [0.0, 0.5], "yaw": 0, "size": 0.75, "plate": True, "from": a2 + 0.05, "to": d}],
                      "screen": []})
        # 3 BALL TO THE CORNER: O1 -> O2 -> O4 at ~1.1x (A 0.55 -> 2.98), one pass line at a time
        d = dur["corner"]
        rm = [[0, 0.55], [d, 2.98]]
        shots.append({"id": "corner", "name": "Watch the ball reach the corner: O1 -> O2 -> O4", "at": cuts["corner"], "play": "A",
                      "remap": rm, "camera": [key(0, PUSH)],
                      "ov3": [cov(0.0, d, mode="active", active=["X2", "X4"], dim=0.5),
                              {"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": 0.0, "to": inv(rm, 1.45) + 0.1},
                              {"type": "passLane", "src": "O2", "dst": "O4", "color": WHITE, "from": inv(rm, 2.35), "to": d}],
                      "screen": []})
        # 4 CORNER TRAP: close on the left corner, X2 + X4 close (A 2.98 -> 3.5), short freeze; ONE label set
        d = dur["trap"]
        k = min(0.75, d * 0.35)
        shots.append({"id": "trap", "name": "The wing and the runner trap: X2 + X4 on O4, freeze", "at": cuts["trap"], "play": "A",
                      "remap": [[0, 2.98], [k, 3.5], [d, 3.5]], "camera": [key(0, TRAP)],
                      "ov3": [cov(0.0, d, mode="active", active=["X2", "X4"], dim=0.35)],
                      "screen": [{"type": "punch", "amount": 0.025, "from": k - 0.05, "to": k + 0.3},
                                 {"type": "freeze", "from": k, "to": d},
                                 {"type": "pin", "player": "X2", "text": "X2", "tone": "gold", "from": k, "to": d, "size": 40},
                                 {"type": "pin", "player": "X4", "text": "X4", "tone": "gold", "from": k, "to": d, "size": 40},
                                 {"type": "chip", "text": "CORNER TRAP", "tone": "gold", "align": "center", "size": 64, "from": k + 0.05, "to": d, "y": 470}]})
        # 5 COVERAGE: wide again, A 3.5 -> 4.3, ELBOW then INSIDE (X3 visible on the weak block, no third label)
        d = dur["rot"]
        b1 = L("inside", "rot")
        shots.append({"id": "rot", "name": "The top to the elbow, the middle inside (A 3.5 -> 4.3)", "at": cuts["rot"], "play": "A",
                      "remap": [[0, 3.5], [d, 4.3]], "camera": [key(0, PUSH)],
                      "ov3": [cov(0.0, b1, mode="active", active=["X1"], dim=0.4), cov(b1, d, mode="active", active=["X5"], dim=0.4)],
                      "screen": [{"type": "pin", "player": "X1", "text": "ELBOW", "tone": "gold", "from": 0.1, "to": b1 + 0.05, "size": 40},
                                 {"type": "pin", "player": "X5", "text": "INSIDE", "tone": "gold", "from": b1, "to": d, "size": 40}]})
        # 6 RESET + SKIP in ONE shot: hard cut to B 0 with NEW POSSESSION (0.6 s), O1 -> O2, the skip leaves on "skip"
        d = dur["reskip"]
        tw = wd("move", 0) - cuts["reskip"]
        tsk = wd("skip", 1) - cuts["reskip"]
        rm = [[0, 0.0], [tw, 0.45], [tsk - 0.1, 2.05], [tsk, 2.1], [d, 2.78]]
        shots.append({"id": "reskip", "name": "Now reset (NEW POSSESSION 0.6 s) - O1 -> O2 - SKIP straight to the opposite corner", "at": cuts["reskip"], "play": "B",
                      "remap": rm, "camera": [key(0, MAIN), key(tsk, MAIN), key(d, PUSH, "inOut")],
                      "ov3": [cov(0.0, d, mode="full", dim=0.55, reveal=0.05),
                              {"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": inv(rm, 0.6), "to": inv(rm, 1.45) + 0.1},
                              {"type": "passLane", "src": "O2", "dst": "O3", "color": WHITE, "from": tsk - 0.05, "to": d},
                              {"type": "ballTrail", "len": 0.35, "from": tsk, "to": d}],
                      "screen": [{"type": "flash", "color": "#FFE9C8", "strength": 0.16, "from": 0.0, "to": 0.18},
                                 {"type": "stamp", "text": "NEW POSSESSION", "tone": "white", "y": 250, "from": 0.0, "to": 0.6, "instant": True},
                                 {"type": "pin", "player": "O2", "text": "SKIP", "tone": "gold", "from": tsk - 0.1, "to": tsk + 0.9, "size": 40}]})
        # 7 X3 FIRST: ball still in the air; X3's closeout path lit while he runs it (B 2.78 -> 3.3 catch)
        d = dur["first"]
        rm = [[0, 2.78], [d, 3.3]]
        shots.append({"id": "first", "name": "The far wing closes out first: X3 from the weak-side block, ball in the air", "at": cuts["first"], "play": "B",
                      "remap": rm, "camera": [key(0, PUSH)],
                      "ov3": [cov(0.0, d, mode="active", active=["X3"], dim=0.45),
                              {"type": "marker", "player": "X3", "team": "defense", "color": GOLD, "from": 0.0, "to": d},
                              {"type": "route", "player": "X3", "t0": 2.78, "t1": 4.05, "color": GOLD, "width": 0.09, "draw": 0.35, "consume": True, "from": 0.05, "to": d},
                              {"type": "ballTrail", "len": 0.3, "from": 0.0, "to": d}],
                      "screen": [{"type": "pin", "player": "X3", "text": "X3 • FIRST", "tone": "gold", "from": 0.08, "to": d, "size": 40}]})
        # 8 X4 TAKEOVER: freeze on the catch, X4's whole baseline path draws to the corner + the TAKEOVER spot; resume a beat
        d = dur["sprint"]
        fz = min(1.2, d * 0.55)
        rm = [[0, 3.3], [fz, 3.3], [d, 3.55]]
        shots.append({"id": "sprint", "name": "The runner races across to take over: X4's full baseline path, TAKEOVER", "at": cuts["sprint"], "play": "B",
                      "remap": rm, "camera": [key(0, PUSH)],
                      "ov3": [cov(0.0, d, mode="active", active=["X3", "X4"], dim=0.45),
                              {"type": "marker", "player": "X4", "team": "defense", "color": GOLD, "from": 0.0, "to": d},
                              {"type": "route", "player": "X4", "t0": 3.3, "t1": 5.27, "color": BLUE, "width": 0.1, "draw": 0.55, "from": 0.05, "to": d},
                              {"type": "ripple", "at": [-6.3, 1.0], "r": 0.6, "rings": 2, "period": 0.8, "color": BLUE, "from": 0.55, "to": d}],
                      "screen": [{"type": "freeze", "from": 0.0, "to": fz},
                                 {"type": "pin", "player": "X4", "text": "X4 • TAKEOVER", "tone": "gold", "from": 0.1, "to": d, "size": 40}]})
        # 9 PAYOFF: split screen, SAME state, SAME camera, SAME clock - top B (LATE), bottom C (ON TIME); freeze at the release
        d = dur["payoff"]
        trel = wd("three", 0) - cuts["payoff"]          # "corner three." starts on the release
        tcon = L("contested", "payoff")
        tfly = trel + 0.5
        rm = [[0, 2.98], [trel, 3.68], [tfly, 3.68], [tfly + 1.25, 4.78], [d, 5.45]]
        lab = lambda txt, tone, y, fr, to, size=58: {"type": "chip", "text": txt, "tone": tone, "align": "left", "size": size, "from": fr, "to": to, "y": y}
        shots.append({"id": "payoff", "name": "LATE (B) over ON TIME (C): same skip, same camera, same clock; freeze on the release, OPEN LOOK vs CONTESTED", "at": cuts["payoff"], "play": "B",
                      "remap": rm, "camera": [key(0, SPLIT)],
                      "ov3": [{"type": "marker", "player": "X3", "team": "defense", "color": GOLD, "from": 0.0, "to": d},
                              {"type": "separation", "a": "X3", "b": "O3", "color": RED, "from": trel - 0.05, "to": tfly + 0.3},
                              {"type": "route", "player": "X4", "t0": 2.95, "t1": 5.27, "color": BLUE, "width": 0.08, "trail": True, "from": 0.0, "to": d},
                              {"type": "glow", "hoop": True, "r": 1.0, "color": GOLD, "strength": 0.55, "from": inv(rm, 4.7), "to": d}],
                      "split": {"play": "C", "remap": rm, "camera": [key(0, SPLIT)], "ratio": 0.5,
                                "ov3": [{"type": "marker", "player": "X3", "team": "defense", "color": GOLD, "from": 0.0, "to": d},
                                        {"type": "separation", "a": "X3", "b": "O3", "color": BLUE, "from": trel - 0.05, "to": tfly + 0.3},
                                        {"type": "route", "player": "X4", "t0": 2.95, "t1": 5.13, "color": BLUE, "width": 0.08, "trail": True, "from": 0.0, "to": d}]},
                      "screen": [lab("LATE", "red", 44, 0.0, d), lab("ON TIME", "blue", 1004, 0.0, d),
                                 lab("OPEN LOOK", "gold", 790, trel, d, 54),
                                 lab("CONTESTED", "gold", 1750, tcon, d, 54),
                                 {"type": "freeze", "from": trel, "to": tfly}]})
        # 10 CLOSE: "Pressure creates the trap." - the trap again, wide (A 3.5)
        d = dur["close"]
        shots.append({"id": "close", "name": "Pressure creates the trap (A 3.5, wide)", "at": cuts["close"], "play": "A",
                      "remap": [[0, 3.42], [d, 3.5]], "camera": [key(0, PUSH)],
                      "ov3": [cov(0.0, d, mode="active", active=["X2", "X4"], dim=0.4)], "screen": []})
        # 11 LOOP: "Quick passing tests the recovery." - O1 -> O2 into the cold-open frame (B 1.8), the question
        d = dur["loop"]
        shots.append({"id": "loop", "name": "Quick passing tests the recovery - back to the cold-open frame; WOULD YOUR TEAM RECOVER?", "at": cuts["loop"], "play": "B",
                      "remap": [[0, 0.6], [d, 1.8]], "camera": [key(0, MAIN)],
                      "ov3": [{"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": 0.0, "to": inv([[0, 0.6], [d, 1.8]], 1.45) + 0.1},
                              {"type": "marker", "player": "X4", "team": "defense", "color": GOLD, "ripple": False, "from": d - 1.2, "to": d},
                              {"type": "ring", "player": "X4", "color": GOLD, "size": 1.25, "pulse": True, "from": d - 1.2, "to": d}],
                      "screen": [{"type": "title", "lines": ["WOULD YOUR TEAM", "RECOVER?"], "gold": [1], "from": d - 1.75, "to": d, "size": 92, **TITLE},
                                 {"type": "logo", "big": False, "from": d - 1.1, "to": d}]})
    ep = {
        "id": "zone-131-v2", "title": "1-3-1 ZONE V2: ONE DEFENDER, TWO CORNERS", "fps": 30,
        "voice": voice, "tail": round(t_end - (e0("quick") if only != "hook" else e0("two")), 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33",
        "words": words if only != "hook" else words[:4],
        "subtitleGroups": [len(t.split()) for _, t in LINES] if only != "hook" else [2, 2],
        "subtitleBlock": True, "subtitleY": 1390,
        # payoff split: the caption sits on the seam between the two halves
        "subtitleYAt": [[cuts["payoff"], cuts["close"], 900]],
        # the hook title already says the two lines (no title + caption + chip saying the same thing); the end question too
        "subtitleHide": [[0.0, cuts["shape"]], [t_end - 1.8, 999]],
        "keywords": ["defender.", "corners.", "top.", "zone.", "corner.", "trap.", "elbow.", "inside.", "reset.", "skip",
                     "first.", "sprints", "late...", "three.", "Contested.", "recovery."],
        "gradeBottom": 0.3,
        "shots": shots, "plays": PL,
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    meta = {"duration": round(t_end, 3), "frames": int(round(t_end * 30)), "cuts": {k: round(v, 3) for k, v in cuts.items()},
            "dur": {k: round(v, 3) for k, v in dur.items()}}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words", required=True)
    ap.add_argument("--voice", default="tactical/zone131v2/voice.wav")
    ap.add_argument("--music")
    ap.add_argument("--hook", default="A")
    ap.add_argument("--only")
    ap.add_argument("--fit")
    a = ap.parse_args()
    words = json.load(open(a.words))
    props, meta = build(words, a.voice, a.music, a.hook, a.only)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"])
        ep["plays"] = {k: v["id"] for k, v in PL.items()}
        json.dump(ep, open(a.fit, "w"))
        json.dump(ep["words"], open(a.fit.replace(".json", ".words.json"), "w"))
    print(json.dumps(meta))
