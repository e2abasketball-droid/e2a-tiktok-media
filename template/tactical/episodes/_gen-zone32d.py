#!/usr/bin/env python3
"""E2A 3-2 ZONE DEFENSE (owner master brief 2026-11-25) - the edit, as Remotion props for Tactical3DV2.
Defensive-series format of the 2-3 Zone MASTER / 1-3-1 Zone (coverage areas, one tactical camera basket up, freeze +
pins, closing CTA) with the E2A Basketball Visual Standard v1 (athleteRenderer v33, env cinema, marker / legend, short
pins and outcome chips) and the Floor Graphics Stability Standard (one coverage overlay per shot, activeKeys
cross-fades, stable: true, no abutting overlays, fin/fout 0 on same-frame cuts).
Rotation system: produccion/zone32d-2026-11-25/REGLAS-ROTACION-3-2.md. Plays: tactical/specs/_gen-zone32d.py
  A zone32d-a-wing-corner, B zone32d-b-high-post, C zone32d-c-shot-boxout, D zone32d-d-swing.
Words: --words <words.json> (real Deuce take, tactical/episodes/zone32d/zone32d-voice.words.json, already shifted by
the preroll) or the GUIDE timings below.
  python3 tactical/episodes/_gen-zone32d.py --out props.json [--words w.json] [--voice path] [--music path] [--fit ep.json]
  [--trial]  trial-reel variant: same voice take, different opening frame (overhead start), mirrored title colours"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PL = {k: json.load(open(os.path.join(T, "tactical", "plays", f"{v}.json"))) for k, v in
      {"A": "zone32d-a-wing-corner", "B": "zone32d-b-high-post", "C": "zone32d-c-shot-boxout", "D": "zone32d-d-swing"}.items()}
GOLD, NAVY, BLUE, WHITE, AMBER = "#C9A24D", "#0B1C3D", "#8EC5F0", "#FFFFFF", "#F2A33A"

LINES = [
    ("hook1", "Want to SHUT DOWN perimeter shooters?", 0.1, 2.4),
    ("hook2", "This is how the three-two zone works.", 2.5, 4.7),
    ("top", "Three defenders up top.", 4.9, 6.3),
    ("low", "Two down low.", 6.4, 7.4),
    ("goal", "Control the wings... and make outside shots difficult.", 7.5, 11.1),
    ("wing", "Ball to the wing: the nearest defender closes out...", 11.3, 14.3),
    ("shift", "and EVERYONE shifts to protect the gaps.", 14.3, 17.0),
    ("corner", "Ball in the corner?", 17.2, 18.3),
    ("steps", "The bottom defender steps out.", 18.4, 20.2),
    ("others", "The others rotate to protect the paint and cover the weak side.", 20.4, 24.1),
    ("watch", "But watch the high post.", 24.3, 25.7),
    ("inside", "If the ball gets inside, the middle defender must react,", 25.8, 29.4),
    ("adjust", "and the whole defense has to adjust.", 29.5, 31.7),
    ("great", "The three-two is great at contesting perimeter shots.", 31.9, 34.7),
    ("but", "But the corners, the high post and defensive rebounding can become problems.", 34.8, 39.6),
    ("box", "Find a body. Box out.", 39.8, 42.0),
    ("five", "Five defenders. One connected unit.", 42.2, 44.9),
    ("follow", "Follow for more European basketball.", 45.0, 47.0),
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
# fit-search (scripts/fit-search.mts, safe band 380-1330 px, all ten feet + head + ball, side 20 px), basket up
MAIN = orb([0.0, 8.4, 0.6], 24.75, 48)           # A/B/C/D whole plays: every player and the ball in the band
CORNER = orb([-1.0, 5.85, 0.6], 20.5, 50, -10)    # A 2.7-4.4: all five defenders + O2, O4, O5, right side closer
HOOK = orb([-5.0, 5.3, 1.0], 8.2, 68, 38)      # three-quarter on the right wing: O2 + X3 closeout (Camera B)
CONTEST = orb([4.8, 5.2, 1.1], 8.4, 68, -38)       # three-quarter on the left wing: O3 + X2 contest (Camera B)
BOXCAM = orb([2.2, 5.9, 0.6], 16.8, 55, 18)   # C 2.6-3.7: strong-side box-outs closer (O1 O3 O5 X1 X2 X4)
TOPV = orb([0.0, 7.2, 0.6], 25.5, 70)             # trial opening: near overhead


def inv(remap, pt):
    for (a, pa), (b, pb) in zip(remap, remap[1:]):
        if pa <= pt <= pb and pb > pa:
            return a + (b - a) * (pt - pa) / (pb - pa)
    raise ValueError(pt)


def cov(fr, to, **kw):
    return {"type": "coverage", "scheme": "3-2", "stable": True, "from": fr, "to": to, **kw}


def route(pid, play, t0, t1, fr, to, color=GOLD, **kw):
    return {"type": "route", "player": pid, "t0": t0, "t1": t1, "color": color, "width": 0.09, "draw": 0.45, "consume": True,
            "from": fr, "to": to, **kw}


def build(words, voice, music, trial=False):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    cuts = {"hook": 0.0, "reveal": s0("hook2") - 0.1, "shape": s0("top") - 0.12, "shift": s0("wing") - 0.15,
            "corner": s0("corner") - 0.15, "hp": s0("watch") - 0.15, "contest": s0("great") - 0.15,
            "weak": s0("but") - 0.1, "box": s0("box") - 0.12, "close": s0("five") - 0.15}
    t_end = e0("follow") + 1.35
    order = list(cuts)
    dur = {k: (cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k] for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    Lw = lambda k, i, sh: wd(k, i) - cuts[sh]
    shots = []
    A, Bp, C, Dp = PL["A"]["marks"], PL["B"]["marks"], PL["C"]["marks"], PL["D"]["marks"]

    # 1 HOOK (Camera B): O2 catches on the right wing, loads, X3 closes out under control: no shot
    d = dur["hook"]
    rm = [[0, 0.55], [d, 2.45]]
    if trial:
        shots.append({"id": "hook", "name": "TRIAL hook: overhead, ball to the wing, the closeout lit", "at": 0.0, "play": "A",
                      "remap": rm, "camera": [key(0, TOPV)],
                      "ov3": [{"type": "marker", "player": "X3", "team": "defense", "color": GOLD, "from": 0.0, "to": d},
                              {"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": inv(rm, 0.7), "to": inv(rm, 1.32) + 0.1},
                              route("X3", "A", 0.75, 1.95, inv(rm, 0.8), d)],
                      "screen": [{"type": "title", "lines": ["SHUT DOWN", "THE SHOOTERS."], "gold": [0], "from": 0.0, "to": d - 0.05, "y": 236, "size": 100}]})
    else:
        shots.append({"id": "hook", "name": "Want to SHUT DOWN perimeter shooters? O2 catches, X3 closes out, no shot", "at": 0.0, "play": "A",
                      "remap": rm, "camera": [key(0, HOOK), key(d, orb([-5.0, 5.3, 1.0], 7.4, 66, 34), "inOut")],
                      "ov3": [{"type": "ring", "player": "X3", "color": GOLD, "size": 1.1, "pulse": True, "from": inv(rm, 1.35), "to": d},
                              {"type": "glow", "player": "O2", "r": 1.0, "color": AMBER, "strength": 0.4, "from": inv(rm, 1.4), "to": d}],
                      "screen": [{"type": "title", "lines": ["SHUT DOWN", "THE SHOOTERS."], "gold": [0], "from": 0.0, "to": d - 0.05, "y": 236, "size": 100},
                                 {"type": "pin", "player": "X3", "text": "CLOSEOUT", "tone": "gold", "from": inv(rm, 1.6), "to": d, "size": 40}]})
    # 2 REVEAL (Camera A): rewind to the base 3-2, coverage areas rise, markers attack then defence, title
    d = dur["reveal"]
    seq = [("O1", "attack"), ("O3", "attack"), ("O2", "attack"), ("O5", "attack"), ("O4", "attack"),
           ("X1", "defense"), ("X2", "defense"), ("X3", "defense"), ("X4", "defense"), ("X5", "defense")]
    rw = 0.55
    mk = [{"type": "marker", "player": p, "team": tm, "from": round(rw + 0.2 + j * 0.14, 3), "to": d - 0.05} for j, (p, tm) in enumerate(seq)]
    shots.append({"id": "reveal", "name": "This is how the 3-2 zone works: rewind to the base shape, areas + markers, title", "at": cuts["reveal"], "play": "A",
                  "remap": [[0, 2.45], [rw, 0.0], [d, 0.0]], "camera": [key(0, MAIN)],
                  "ov3": [cov(rw, d, mode="full", reveal=0.12), *mk],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             {"type": "title", "lines": ["3-2 ZONE", "DEFENSE"], "gold": [0], "from": rw, "to": d - 0.05, "y": 236, "size": 112},
                             {"type": "legend", "from": rw + 0.2, "to": d - 0.05, "y": 150}]})
    # 3 SHAPE: 3 UP TOP (X1 X2 X3) / 2 DOWN LOW (X4 X5) / the goal: the wings
    d = dur["shape"]
    a1, a2 = L("low", "shape"), L("goal", "shape")
    shots.append({"id": "shape", "name": "Three up top, two down low, control the wings", "at": cuts["shape"], "play": "A",
                  "remap": [[0, 0.0], [d, 0.0]], "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="active", active=["X1", "X2", "X3"], dim=0.3, fin=0,
                              activeKeys=[[0.0, ["X1", "X2", "X3"]], [a1, ["X4", "X5"]], [a2, ["X2", "X3"]]]),
                          {"type": "floorText", "text": "3 UP TOP", "at": [0.0, 9.0], "yaw": 0, "size": 0.75, "plate": True, "from": 0.1, "to": a1},
                          {"type": "floorText", "text": "2 DOWN LOW", "at": [0.0, 3.95], "yaw": 0, "size": 0.75, "plate": True, "from": a1 + 0.05, "to": a2},
                          {"type": "glow", "at": [-5.9, 6.2], "r": 1.25, "color": GOLD, "strength": 0.45, "from": a2 + 0.1, "to": d},
                          {"type": "glow", "at": [5.9, 6.2], "r": 1.25, "color": GOLD, "strength": 0.45, "from": a2 + 0.1, "to": d}],
                  "screen": [{"type": "chip", "text": "CONTROL THE WINGS", "tone": "gold", "align": "center", "size": 60, "from": a2 + 0.1, "to": d, "y": 470}]})
    # 4 SHIFT: O1 -> O2, X3 closes out, then every defender's path, progressively
    d = dur["shift"]
    te = Lw("shift", 1, "shift")             # "EVERYONE"
    rm = [[0, 0.3], [te, 1.7], [d, A["shifted"] + 0.15]]
    shots.append({"id": "shift", "name": "Ball to the wing: X3 closes out, EVERYONE shifts (X1 elbow, X2 middle, X5 block, X4 rim)", "at": cuts["shift"], "play": "A",
                  "remap": rm, "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="active", active=["X3"], dim=0.45, fin=0,
                              activeKeys=[[0.0, ["X3"]], [te, ["X1", "X2", "X3", "X4", "X5"]]]),
                          {"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": inv(rm, 0.7), "to": inv(rm, 1.32) + 0.15},
                          route("X3", "A", 0.75, 1.95, inv(rm, 0.8), d),
                          route("X1", "A", 0.85, 1.85, te, d),
                          route("X5", "A", 0.9, 1.7, te + 0.15, d),
                          route("X2", "A", 0.9, 1.85, te + 0.3, d),
                          route("X4", "A", 0.95, 1.85, te + 0.45, d)],
                  "screen": [{"type": "pin", "player": "X3", "text": "CLOSEOUT", "tone": "gold", "from": inv(rm, 1.4), "to": te, "size": 40},
                             {"type": "chip", "text": "SHIFT AS A UNIT", "tone": "gold", "align": "center", "size": 60, "from": te + 0.2, "to": d, "y": 470}]})
    # 5 CORNER ROTATION (Camera C, subtle push): O2 -> O4; X5 out, X4 across, X3 cuts off, X1 high post, X2 weak block
    d = dur["corner"]
    ts = L("steps", "corner")
    to_ = L("others", "corner")
    tp = Lw("others", 5, "corner")           # "paint"
    tw = Lw("others", 9, "corner")           # "weak"
    rm = [[0, 2.45], [ts, 2.95], [to_, 3.95], [d - 0.6, 4.25], [d, 4.25]]
    shots.append({"id": "corner", "name": "Corner rotation: X5 steps out, X4 slides across, X3 cuts off, X1 high post, X2 weak block", "at": cuts["corner"], "play": "A",
                  "remap": rm, "camera": [key(0, MAIN), key(0.9, CORNER, "inOut"), key(d, CORNER)],
                  "ov3": [cov(0.0, d, mode="active", active=["X5"], dim=0.45, fin=0,
                              activeKeys=[[0.0, ["X5"]], [to_, ["X5", "X4"]], [tw, ["X5", "X4", "X2"]]]),
                          {"type": "passLane", "src": "O2", "dst": "O4", "color": WHITE, "from": inv(rm, 2.7), "to": inv(rm, 3.3) + 0.15},
                          route("X5", "A", 2.8, 3.95, inv(rm, 2.85), d),
                          route("X4", "A", 2.85, 4.0, to_, d, color=BLUE),
                          route("X3", "A", 2.87, 3.7, to_ + 0.2, d, color=BLUE),
                          route("X1", "A", 2.95, 3.75, to_ + 0.35, d, color=BLUE),
                          route("X2", "A", 2.95, 4.0, tw - 0.1, d, color=BLUE),
                          {"type": "glow", "hoop": True, "r": 1.3, "color": GOLD, "strength": 0.5, "from": tp, "to": d}],
                  "screen": [{"type": "chip", "text": "CORNER ROTATION", "tone": "gold", "align": "center", "size": 60, "from": 0.15, "to": to_, "y": 1250},
                             {"type": "pin", "player": "X5", "text": "STEPS OUT", "tone": "gold", "from": ts + 0.2, "to": d, "size": 38},
                             {"type": "pin", "player": "X4", "text": "ACROSS", "tone": "white", "from": to_ + 0.4, "to": d, "size": 36},
                             {"type": "pin", "player": "X2", "text": "WEAK SIDE", "tone": "white", "from": tw, "to": d, "size": 36},
                             {"type": "chip", "text": "PROTECT THE PAINT", "tone": "gold", "align": "center", "size": 60, "from": tp, "to": d, "y": 1250},
                             {"type": "freeze", "from": d - 0.6, "to": d}]})
    # 6 HIGH POST: new possession; O5 flashes behind X1, bounce entry, X1 reacts, wings pinch, lows wall the paint
    d = dur["hp"]
    ti = L("inside", "hp")
    tr = Lw("inside", 9, "hp")               # "react,"
    ta = L("adjust", "hp")
    rm = [[0, 0.2], [ti, Bp["nail"]], [tr, Bp["entryCatch"] + 0.15], [ta, Bp["entryCatch"] + 0.55], [d - 0.5, Bp["react"] + 0.1], [d, Bp["react"] + 0.1]]
    shots.append({"id": "hp", "name": "High-post threat: O5 flashes, entry, X1 reacts, the zone changes shape", "at": cuts["hp"], "play": "B",
                  "remap": rm, "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="active", active=["X1"], dim=0.45,
                              activeKeys=[[0.0, ["X1"]], [ta, ["X1", "X2", "X3", "X4", "X5"]]]),
                          {"type": "glow", "at": [0.2, 5.85], "r": 1.2, "color": AMBER, "strength": 0.6, "from": 0.2, "to": d},
                          route("O5", "B", 0.5, 1.75, 0.3, ti + 0.6, color=WHITE),
                          {"type": "passLane", "src": "O1", "dst": "O5", "color": WHITE, "from": inv(rm, 1.95), "to": inv(rm, 2.42) + 0.15},
                          route("X1", "B", 2.15, 3.0, tr - 0.2, d),
                          route("X2", "B", 2.2, 2.95, ta, d, color=BLUE),
                          route("X3", "B", 2.2, 2.95, ta, d, color=BLUE),
                          route("X4", "B", 2.25, 3.0, ta + 0.2, d, color=BLUE),
                          route("X5", "B", 2.25, 3.0, ta + 0.2, d, color=BLUE)],
                  "screen": [{"type": "flash", "color": "#FFE9C8", "strength": 0.14, "from": 0.0, "to": 0.2},
                             {"type": "chip", "text": "HIGH-POST THREAT", "tone": "red", "align": "center", "size": 60, "from": 0.2, "to": ta, "y": 470},
                             {"type": "pin", "player": "X1", "text": "REACT", "tone": "gold", "from": tr + 0.3, "to": d, "size": 40},
                             {"type": "chip", "text": "THE ZONE ADJUSTS", "tone": "gold", "align": "center", "size": 60, "from": ta + 0.1, "to": d, "y": 470},
                             {"type": "freeze", "from": d - 0.5, "to": d}]})
    # 7 STRENGTH (Camera B): O3 on the left wing, X2 closes out and contests the three (miss)
    d = dur["contest"]
    rm = [[0, 0.55], [d - 0.2, C["release"] + 0.55], [d, C["release"] + 0.62]]
    shots.append({"id": "contest", "name": "Great at contesting perimeter shots: X2 contests O3's three", "at": cuts["contest"], "play": "C",
                  "remap": rm, "camera": [key(0, CONTEST), key(d, orb([4.8, 5.2, 1.3], 7.8, 66, -34), "inOut")],
                  "ov3": [{"type": "ring", "player": "X2", "color": GOLD, "size": 1.1, "pulse": True, "from": inv(rm, 1.2), "to": d},
                          {"type": "ballTrail", "len": 0.3, "from": inv(rm, C["release"]), "to": d}],
                  "screen": [{"type": "chip", "text": "PERIMETER COVERAGE", "tone": "gold", "align": "center", "size": 60, "from": 0.2, "to": d, "y": 470},
                             {"type": "pin", "player": "X2", "text": "CONTEST", "tone": "gold", "from": inv(rm, C["release"]) - 0.1, "to": d, "size": 40}]})
    # 8 WEAKNESSES: freeze with the ball in the air (Camera A), CORNERS / HIGH POST / REBOUNDING in turn
    d = dur["weak"]
    pt = C["release"] + 0.62
    tc, th, trb = Lw("but", 2, "weak"), Lw("but", 4, "weak"), Lw("but", 8, "weak")
    shots.append({"id": "weak", "name": "But: corners, high post, rebounding (freeze, amber areas in turn)", "at": cuts["weak"], "play": "C",
                  "remap": [[0, pt], [d, pt]], "camera": [key(0, MAIN)],
                  "ov3": [{"type": "glow", "at": [-6.6, 1.0], "r": 1.3, "color": AMBER, "strength": 0.6, "from": tc - 0.1, "to": d},
                          {"type": "glow", "at": [6.6, 1.0], "r": 1.3, "color": AMBER, "strength": 0.6, "from": tc - 0.1, "to": d},
                          {"type": "glow", "at": [0.0, 5.85], "r": 1.2, "color": AMBER, "strength": 0.6, "from": th - 0.1, "to": d},
                          {"type": "glow", "hoop": True, "r": 1.4, "color": AMBER, "strength": 0.6, "from": trb - 0.1, "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d},
                             {"type": "chip", "text": "CORNERS", "tone": "red", "align": "left", "size": 52, "from": tc, "to": d, "y": 430},
                             {"type": "chip", "text": "HIGH POST", "tone": "red", "align": "center", "size": 52, "from": th, "to": d, "y": 500},
                             {"type": "chip", "text": "REBOUNDING", "tone": "red", "align": "right", "size": 52, "from": trb, "to": d, "y": 570}]})
    # 9 BOX OUT: resume, all five find a body and box out (Camera A, slow)
    d = dur["box"]
    rm = [[0, pt], [d, C["box"] + 0.25]]
    mk = [{"type": "marker", "player": p, "team": "defense", "color": GOLD, "from": 0.15 + j * 0.12, "to": d} for j, p in enumerate(["X2", "X1", "X3", "X4", "X5"])]
    shots.append({"id": "box", "name": "Find a body. Box out: X2-O3, X1-O1, X3-O2, X4-O5, X5-O4", "at": cuts["box"], "play": "C",
                  "remap": rm, "camera": [key(0, MAIN), key(min(1.7, d * 0.7), BOXCAM, "inOut"), key(d, BOXCAM)],
                  "ov3": [*mk,
                          *[{"type": "separation", "a": x, "b": o, "color": GOLD, "from": 0.6, "to": d} for x, o in
                            [("X2", "O3"), ("X1", "O1"), ("X3", "O2"), ("X4", "O5"), ("X5", "O4")]]],
                  "screen": [{"type": "chip", "text": "BOX OUT", "tone": "gold", "align": "center", "size": 64, "from": 0.2, "to": d, "y": 470},
                             {"type": "pin", "player": "X4", "text": "FIND A BODY", "tone": "gold", "from": min(1.2, d * 0.45), "to": d, "size": 36},
                             {"type": "pin", "player": "X2", "text": "BOX OUT", "tone": "white", "from": min(1.4, d * 0.5), "to": d, "size": 36}]})
    # 10 CLOSE: one connected unit (D swing), CTA, logo; ends on the hook's situation (ball right wing, X3 closed out)
    d = dur["close"]
    rm = [[0, 0.0], [d, PL["D"]["duration"]]]
    shots.append({"id": "close", "name": "Five defenders. One connected unit. Follow for more European basketball.", "at": cuts["close"], "play": "D",
                  "remap": rm, "camera": [key(0, MAIN)],
                  "ov3": [cov(0.0, d, mode="full", dim=0.55),
                          {"type": "passLane", "src": "O1", "dst": "O3", "color": WHITE, "from": inv(rm, 0.5), "to": inv(rm, 1.1) + 0.1},
                          {"type": "passLane", "src": "O3", "dst": "O1", "color": WHITE, "from": inv(rm, 2.15), "to": inv(rm, 2.7) + 0.1},
                          {"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": inv(rm, 3.55), "to": inv(rm, 4.15) + 0.1}],
                  "screen": [{"type": "title", "lines": ["FIVE DEFENDERS.", "ONE UNIT."], "gold": [1], "from": 0.1, "to": L("follow", "close") - 0.05, "y": 236, "size": 96},
                             {"type": "title", "lines": ["FOLLOW FOR MORE", "EUROPEAN BASKETBALL"], "gold": [1], "from": L("follow", "close"), "to": d, "y": 236, "size": 84},
                             {"type": "logo", "big": False, "from": d - 1.6, "to": d}]})
    ep = {
        "id": "zone-32-defense" + ("-trial" if trial else ""), "title": "3-2 ZONE DEFENSE", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33",
        "words": words,
        "subtitleGroups": [len(t.split()) for _, t, _, _ in LINES],
        "subtitleBlock": True, "subtitleY": 1390, "subtitleHide": [[t_end - 1.7, 999]],
        "keywords": ["SHUT", "DOWN", "three-two", "Three", "top.", "Two", "low.", "wings...", "closes", "out...", "EVERYONE", "shifts",
                     "corner?", "steps", "paint", "weak", "high", "post.", "react,", "contesting", "corners,", "rebounding", "body.", "Box", "out.",
                     "One", "connected", "unit."],
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
    ap.add_argument("--fit")
    ap.add_argument("--trial", action="store_true")
    a = ap.parse_args()
    words = json.load(open(a.words)) if a.words else guide_words()
    props, meta = build(words, a.voice, a.music, a.trial)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"])
        ep["plays"] = {k: v["id"] for k, v in PL.items()}
        json.dump(ep, open(a.fit, "w"))
        json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    print(json.dumps(meta))
