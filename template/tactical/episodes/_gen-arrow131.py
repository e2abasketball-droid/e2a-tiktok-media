#!/usr/bin/env python3
"""E2A 1-3-1 ARROW PRESS -> 1-3-1 ZONE (owner request 2026-11-24) - the edit, as Remotion props for Tactical3DV2.
Companion of the 1-3-1 Zone Defense reel: same format (hook with the result, floor coverage areas in the style of the
2-3 Zone V2 Dynamic Coverage, freeze + annotated reads, closing question, Deuce) and the E2A Basketball Visual
Standard v1 (athleteRenderer v33, env cinema, marker / legend, pins and outcome chips, 2026 logo).
Play (tactical/specs/_gen-arrow131.py): arrow131-press (FULL court).
Timing: --words <words.json> (real narration) or GUIDE timings (no voice yet).
  python3 tactical/episodes/_gen-arrow131.py --out props.json [--words w.json] [--voice path] [--music path] [--fit ep-fit.json]"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PL = {"A": json.load(open(os.path.join(T, "tactical", "plays", "arrow131-press.json")))}
MK = PL["A"]["marks"]
GOLD, NAVY, BLUE, WHITE, CORAL = "#C9A24D", "#0B1C3D", "#8EC5F0", "#FFFFFF", "#F06A55"

LINES = [
    ("hook1", "Half court isn't a line.", 0.15, 1.45),
    ("hook2", "It's a trap.", 1.6, 2.4),
    ("this", "This is the one-three-one arrow press.", 2.8, 5.0),
    ("point", "One at the point.", 5.4, 6.3),
    ("three", "Three across half court.", 6.45, 7.8),
    ("safety", "One safety deep.", 7.95, 8.9),
    ("turns", "The point turns the ball to the sideline.", 9.4, 11.4),
    ("never", "Never let it go middle.", 11.55, 12.8),
    ("crosses", "The ball crosses half court...", 13.2, 14.8),
    ("jumps", "and the wing jumps.", 14.95, 15.9),
    ("trap", "Trap!", 16.05, 16.6),
    ("lines", "The sideline and the half-court line are two extra defenders.", 17.3, 20.4),
    ("middle", "The middle takes away the middle.", 21.0, 22.7),
    ("far", "The far wing reads the cross-court pass.", 22.9, 24.9),
    ("safe", "The safety guards the long pass.", 25.1, 26.8),
    ("escapes", "Now the ball escapes.", 27.5, 28.7),
    ("chase", "Don't chase it.", 28.9, 29.7),
    ("sprint", "Sprint back.", 29.85, 30.6),
    ("same", "Same five players, same spots...", 31.2, 33.0),
    ("becomes", "and the arrow becomes a one-three-one zone.", 33.2, 35.6),
    ("q1", "Would you trap at half court...", 36.3, 38.0),
    ("q2", "or wait in the zone?", 38.15, 39.3),
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
# fit-search (scripts/fit-search.mts, band 380-1330 px, side 20 px, all ten players + ball), basket up, behind the offence
PRESS = orb([0.55, 20.23, 0.6], 25.75, 66, -6)          # the arrow at rest (0) and the bring-up (0.4 -> 3.0)
MID = orb([0.94, 16.25, 0.6], 23.5, 66, -6)            # trap + reads (3.0 -> 4.5), the five defenders across half court
BACK = orb([0.98, 14.11, 0.6], 25.0, 66, -6)       # escape + sprint back (4.4 -> 6.4)
ZONE = orb([0.53, 10.4, 0.6], 24.25, 66, -6)       # the half-court 1-3-1 formed (6.2 -> 8.2)
TURN = orb([2.81, 20.94, 0.6], 15.75, 62, -10)      # the bring-up: O1, X1, X2, X5, O2 (0.3 -> 3.0)
TRAP = orb([6.0, 15.0, 0.6], 10.75, 48, -40)       # the trap on the left sideline just past half court (screen left)
HALF = [[-7.45, 14.0], [7.45, 14.0]]              # the half-court line
SIDE = [[7.45, 16.2], [7.45, 10.6]]               # the left sideline at the trap


def inv(remap, pt):
    for (a, pa), (b, pb) in zip(remap, remap[1:]):
        if pa <= pt <= pb and pb > pa:
            return a + (b - a) * (pt - pa) / (pb - pa)
    raise ValueError(pt)


def cov(fr, to, scheme="arrow-131", **kw):
    return {"type": "coverage", "scheme": scheme, "from": fr, "to": to, **kw}


def gline(pts, fr, to, w=0.14, draw=0.4, color=GOLD):
    return {"type": "route", "player": "X1", "t0": 0, "t1": 0, "pts": pts, "color": color, "width": w, "draw": draw, "noHead": True, "from": fr, "to": to}


def build(words, voice, music):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    cuts = {
        "hook": 0.0,
        "this": s0("this") - 0.15,
        "shape": s0("point") - 0.12,
        "turns": s0("turns") - 0.15,
        "trap": s0("crosses") - 0.12,
        "lines": s0("lines") - 0.15,
        "reads": s0("middle") - 0.15,
        "escape": s0("escapes") - 0.15,
        "zone": s0("same") - 0.15,
        "close": s0("q1") - 0.2,
    }
    t_end = e0("q2") + 1.5
    order = list(cuts)
    dur = {k: (cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k] for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    TR = MK["trap"]
    shots = []

    # 1 HOOK: the result first - the trap just past half court, the half-court line lit gold
    d = dur["hook"]
    lt = L("hook2", "hook")
    rm = [[0, TR - 0.75], [min(0.9, d * 0.4), TR], [d, TR]]
    shots.append({"id": "hook", "name": "HALF COURT IS A TRAP: X1 + X2 trap O1 on the sideline, half-court line lit", "at": 0.0, "play": "A",
                  "remap": rm, "camera": [key(0, TRAP)],
                  "ov3": [gline(HALF, 0.1, d, 0.15, 0.5),
                          {"type": "marker", "player": "X1", "team": "defense", "color": GOLD, "from": 0.5, "to": d},
                          {"type": "marker", "player": "X2", "team": "defense", "color": GOLD, "from": 0.5, "to": d},
                          {"type": "glow", "at": [6.1, 13.0], "r": 1.3, "color": GOLD, "strength": 0.5, "from": lt, "to": d}],
                  "screen": [{"type": "title", "lines": ["HALF COURT"], "gold": [], "from": 0.0, "to": lt, "y": 236, "size": 104},
                             {"type": "title", "lines": ["HALF COURT", "IS A TRAP."], "gold": [1], "from": lt, "to": d - 0.05, "y": 236, "size": 104}]})
    # 2 THIS IS THE ARROW: wide, the five press areas rise, markers attack then defence, legend
    d = dur["this"]
    seq = [("O1", "attack"), ("O2", "attack"), ("O4", "attack"), ("O3", "attack"), ("O5", "attack"),
           ("X1", "defense"), ("X2", "defense"), ("X5", "defense"), ("X3", "defense"), ("X4", "defense")]
    mk = [{"type": "marker", "player": p, "team": tm, "from": round(0.25 + j * 0.14, 3), "to": d - 0.1} for j, (p, tm) in enumerate(seq)]
    shots.append({"id": "this", "name": "This is the 1-3-1 arrow press: press coverage areas + markers", "at": cuts["this"], "play": "A",
                  "remap": [[0, 0.0], [d, 0.0]], "camera": [key(0, PRESS)],
                  "ov3": [cov(0.0, d, mode="full", reveal=0.14), *mk],
                  "screen": [{"type": "title", "lines": ["1-3-1", "ARROW PRESS"], "gold": [1], "from": 0.1, "to": d - 0.1, "y": 236, "size": 100},
                             {"type": "legend", "from": 0.25, "to": d - 0.1, "y": 150}]})
    # 3 SHAPE: ONE at the point / THREE across half court / ONE safety (the arrow), areas one idea at a time
    d = dur["shape"]
    a1, a2 = L("three", "shape"), L("safety", "shape")
    shots.append({"id": "shape", "name": "1 + 3 + 1: X1 / X2-X5-X3 / X4", "at": cuts["shape"], "play": "A",
                  "remap": [[0, 0.0], [d, 0.0]], "camera": [key(0, PRESS)],
                  "ov3": [cov(0.0, a1, mode="active", active=["X1"], dim=0.3, labels="active", labelYaw=0, labelSize=0.85),
                          cov(a1, a2, mode="active", active=["X2", "X5", "X3"], dim=0.3, labels="active", labelYaw=0, labelSize=0.85),
                          gline(HALF, a1, a2, 0.1, 0.4),
                          cov(a2, d, mode="active", active=["X4"], dim=0.3, labels="active", labelYaw=0, labelSize=0.85)],
                  "screen": [{"type": "chip", "text": "1", "tone": "gold", "align": "center", "size": 72, "from": 0.1, "to": a1, "y": 330},
                             {"type": "chip", "text": "3", "tone": "gold", "align": "center", "size": 72, "from": a1, "to": a2, "y": 330},
                             {"type": "chip", "text": "1", "tone": "gold", "align": "center", "size": 72, "from": a2, "to": d, "y": 330}]})
    # 4 TURN IT TO THE SIDELINE: the bring-up (0.3 -> 3.0), X1 on the middle shoulder, NO MIDDLE
    d = dur["turns"]
    b1 = L("never", "turns")
    rm = [[0, 0.3], [d, 3.0]]
    shots.append({"id": "turns", "name": "The point turns the ball to the sideline, never middle", "at": cuts["turns"], "play": "A",
                  "remap": rm, "camera": [key(0, TURN)],
                  "ov3": [cov(0.0, d, mode="active", active=["X1"], dim=0.45),
                          {"type": "marker", "player": "X1", "team": "defense", "color": GOLD, "from": 0.0, "to": d},
                          {"type": "route", "player": "O1", "t0": 0.5, "t1": 3.9, "color": WHITE, "width": 0.09, "draw": 0.5, "from": 0.15, "to": d}],
                  "screen": [{"type": "pin", "player": "X1", "text": "SIDELINE", "tone": "gold", "from": 0.2, "to": b1, "size": 40},
                             {"type": "pin", "player": "X1", "text": "NO MIDDLE", "tone": "white", "from": b1, "to": d, "size": 40}]})
    # 5 CROSSES ... JUMPS ... TRAP: closer, the ball crosses half court, X2 jumps the sideline, freeze on the trap
    d = dur["trap"]
    tj = L("jumps", "trap")
    tt = L("trap", "trap")
    rm = [[0, 2.85], [tj, MK["jump"] + 0.05], [tt, TR], [d, TR]]
    shots.append({"id": "trap", "name": "The ball crosses half court, the wing jumps: TRAP X1 + X2, freeze", "at": cuts["trap"], "play": "A",
                  "remap": rm, "camera": [key(0, TRAP)],
                  "ov3": [cov(0.0, d, mode="active", active=["X1", "X2"], dim=0.35),
                          gline(HALF, 0.0, d, 0.12, 0.35),
                          {"type": "marker", "player": "X2", "team": "defense", "color": GOLD, "from": tj - 0.1, "to": d},
                          {"type": "marker", "player": "X1", "team": "defense", "color": GOLD, "from": tt - 0.1, "to": d}],
                  "screen": [{"type": "freeze", "from": tt, "to": d},
                             {"type": "pin", "player": "X2", "text": "JUMP", "tone": "gold", "from": tj, "to": tt, "size": 40},
                             {"type": "chip", "text": "TRAP.", "tone": "gold", "align": "center", "size": 72, "from": tt, "to": d, "y": 470}]})
    # 6 TWO EXTRA DEFENDERS: still frozen; the sideline then the half-court line light up
    d = dur["lines"]
    w2 = L("lines", "lines") + 1.0
    shots.append({"id": "lines", "name": "The sideline and the half-court line: two extra defenders", "at": cuts["lines"], "play": "A",
                  "remap": [[0, TR], [d, TR]], "camera": [key(0, TRAP)],
                  "ov3": [cov(0.0, d, mode="active", active=["X1", "X2"], dim=0.3),
                          gline(SIDE, 0.15, d, 0.16, 0.4),
                          gline(HALF, w2, d, 0.16, 0.45),
                          {"type": "marker", "player": "X1", "team": "defense", "color": GOLD, "from": 0.0, "to": d},
                          {"type": "marker", "player": "X2", "team": "defense", "color": GOLD, "from": 0.0, "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d},
                             {"type": "chip", "text": "+2 DEFENDERS", "tone": "gold", "align": "center", "size": 64, "from": w2 + 0.3, "to": d, "y": 470}]})
    # 7 THE OTHER THREE: wide on the five, slow (TR -> release), one read at a time with its pass lane
    d = dur["reads"]
    r1, r2 = L("far", "reads"), L("safe", "reads")
    shots.append({"id": "reads", "name": "Middle takes the middle, far wing reads cross-court, safety the long pass", "at": cuts["reads"], "play": "A",
                  "remap": [[0, TR - 0.1], [d, MK["release"] - 0.05]], "camera": [key(0, MID)],
                  "ov3": [cov(0.0, r1, mode="active", active=["X5"], dim=0.4),
                          {"type": "passLane", "src": "O1", "dst": "O4", "color": CORAL, "from": 0.2, "to": r1},
                          cov(r1, r2, mode="active", active=["X3"], dim=0.4),
                          {"type": "passLane", "src": "O1", "dst": "O3", "color": CORAL, "from": r1 + 0.1, "to": r2},
                          cov(r2, d, mode="active", active=["X4"], dim=0.4),
                          {"type": "passLane", "src": "O1", "dst": "O2", "color": CORAL, "from": r2 + 0.1, "to": d}],
                  "screen": [{"type": "pin", "player": "X5", "text": "MIDDLE", "tone": "gold", "from": 0.15, "to": r1 + 0.1, "size": 40},
                             {"type": "pin", "player": "X3", "text": "READ", "tone": "gold", "from": r1, "to": r2 + 0.1, "size": 40},
                             {"type": "pin", "player": "X4", "text": "LONG PASS", "tone": "gold", "from": r2, "to": d, "size": 40}]})
    # 8 ESCAPE: the overhead pass over the trap to the middle; nobody chases, five routes back (trail)
    d = dur["escape"]
    c1, c2 = L("chase", "escape"), L("sprint", "escape")
    rm = [[0, MK["release"] - 0.3], [d, 6.5]]
    routes = [{"type": "route", "player": x, "t0": 4.65, "t1": 7.1, "color": BLUE, "width": 0.08, "trail": True, "from": c2 - 0.2, "to": d}
              for x in ("X1", "X2", "X3", "X4", "X5")]
    shots.append({"id": "escape", "name": "The ball escapes; don't chase it; sprint back (five routes)", "at": cuts["escape"], "play": "A",
                  "remap": rm, "camera": [key(0, MID), key(d, BACK, "inOut")],
                  "ov3": [cov(0.0, c2, mode="full", dim=0.5),
                          {"type": "ballTrail", "len": 0.35, "from": 0.0, "to": inv(rm, MK["escape"]) + 0.2},
                          *routes],
                  "screen": [{"type": "stamp", "text": "ESCAPED", "tone": "white", "y": 250, "from": inv(rm, MK["escape"]) - 0.05, "to": c1 + 0.3, "instant": True},
                             {"type": "chip", "text": "DON'T CHASE", "tone": "white", "align": "center", "size": 60, "from": c1, "to": c2, "y": 470},
                             {"type": "chip", "text": "SPRINT BACK", "tone": "gold", "align": "center", "size": 64, "from": c2, "to": d, "y": 470}]})
    # 9 THE ARROW BECOMES THE ZONE: the defenders arrive, the 1-3-1 zone areas (zone reel) rise on "becomes"
    d = dur["zone"]
    zb = L("becomes", "zone")
    rm = [[0, 6.5], [min(d, zb + 1.2), 7.6], [d, 8.2]]
    shots.append({"id": "zone", "name": "Same five, same spots: the arrow becomes the 1-3-1 zone", "at": cuts["zone"], "play": "A",
                  "remap": rm, "camera": [key(0, BACK), key(min(d, zb + 0.6), ZONE, "inOut"), key(d, ZONE)],
                  "ov3": [cov(zb, d, scheme="1-3-1", mode="full", reveal=0.12, base=MK["end"], labels="all", labelYaw=0, labelSize=0.62)],
                  "screen": [{"type": "title", "lines": ["1-3-1 ZONE"], "gold": [0], "from": zb + 0.3, "to": d - 0.05, "y": 236, "size": 112}]})
    # 10 CLOSE: the zone held, the question, logo
    d = dur["close"]
    q2 = L("q2", "close")
    shots.append({"id": "close", "name": "Would you trap at half court... or wait in the zone? + logo", "at": cuts["close"], "play": "A",
                  "remap": [[0, MK["end"]], [d, MK["end"]]], "camera": [key(0, ZONE)],
                  "ov3": [cov(0.0, d, scheme="1-3-1", mode="full", base=MK["end"], dim=0.5)],
                  "screen": [{"type": "title", "lines": ["TRAP AT", "HALF COURT?"], "gold": [1], "from": 0.1, "to": q2, "y": 236, "size": 100},
                             {"type": "title", "lines": ["OR WAIT IN", "THE ZONE?"], "gold": [1], "from": q2, "to": d, "y": 236, "size": 100},
                             {"type": "logo", "big": False, "from": d - 1.6, "to": d}]})
    ep = {
        "id": "arrow-131", "title": "1-3-1 ARROW PRESS: TRAP AT HALF COURT, THEN THE ZONE", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33",
        "words": words,
        "subtitleGroups": [len(t.split()) for _, t, _, _ in LINES],
        "subtitleBlock": True, "subtitleY": 1390, "subtitleHide": [[t_end - 1.7, 999]],
        "keywords": ["court", "trap.", "arrow", "point.", "Three", "safety", "sideline.", "middle.", "crosses", "jumps.", "Trap!",
                     "extra", "middle.", "cross-court", "long", "escapes.", "chase", "Sprint", "zone.", "zone?"],
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
