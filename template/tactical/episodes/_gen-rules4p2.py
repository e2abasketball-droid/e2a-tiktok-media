#!/usr/bin/env python3
"""E2A - 4 BASKETBALL RULES EVERY PLAYER NEEDS TO UNDERSTAND, PART 2 (owner brief 2026-11-25).
HOOK (4 teasers, no results shown) -> 01 8 SECONDS -> 02 BACKCOURT -> 03 OFFENSIVE 3 SECONDS -> 04 GOALTENDING -> CLOSE
(short question). Same look as Part 1 (athleteRenderer v33, env cinema, 2026 logo, Floor Graphics Stability Standard) with
the Part 2 opt-ins: rules3d paint / centerLine / rimLine and the screen `clock` (one box, stepping count, time-skip mark).
Plays: tactical/specs/_gen-rules4p2.py (rules4p2-*), every rule moment measured on the V3.3 bodies (play marks).
Narration: Deuce, eleven_v3 (script produccion/rules4p2-2026-11-25/GUION-FINAL.md). Until the take exists the edit runs
on placeholder word times (--placeholder writes them); the real Scribe words drop in with no other change.
  python3 tactical/episodes/_gen-rules4p2.py --words W.json --voice rules4p2/voice.wav --music rules4p2/music.wav --out props.json
Options: --hook A (default: the four teasers in rule order, title on the last plate) | B (goaltending freeze first,
title on the first plate). --trial (grade/zoom are applied at encode time; the edit is the same)."""
import argparse, json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
IDS = ["eight", "back", "three", "goal"]
PL = {k: json.load(open(os.path.join(T, "tactical", "plays", f"rules4p2-{k}.json"))) for k in IDS}
MK = {k: PL[k]["marks"] for k in IDS}
GOLD, NAVY, WHITE, RED, GREEN = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A", "#2FBF71"

LINES = [
    ("hook", "Here are FOUR MORE basketball rules every player needs to understand."),
    ("a1", "First: EIGHT SECONDS."),
    ("a2", "You've got eight seconds to get the ball into the frontcourt..."),
    ("a3", "and when you're dribbling, BOTH feet AND the ball need to cross!"),
    ("b1", "Second: BACKCOURT."),
    ("b2", "Once your team has control up front, you can't send the ball back over the line and get it back."),
    ("b3", "That's a BACKCOURT violation."),
    ("c1", "Third: watch the paint."),
    ("c2", "Stay in there for more than three seconds on offense while your team controls the ball?"),
    ("c3", "Violation."),
    ("g1", "And this last one catches players out."),
    ("g2", "The shot is coming down, still above the rim..."),
    ("g3", "and the defender touches it?"),
    ("g4", "That's GOALTENDING! The basket counts!"),
    ("e1", "Which rule catches you out?"),
]
# subtitle blocks (words per block, max two lines on screen): split at the natural breath
GROUPS = [5, 6, 3, 5, 6, 5, 7, 2, 6, 7, 7, 4, 4, 6, 5, 5, 1, 7, 4, 4, 5, 3, 3, 5]
NW = sum(len(t.split()) for _, t in LINES)
assert sum(GROUPS) == NW, (sum(GROUPS), NW)

norm = lambda s: "".join(c for c in s.lower() if c.isalnum())


def placeholder_words():
    """estimated word times (speech ~2.9 words/s, breath gaps) so the edit can be built before the voice exists"""
    out, t = [], 0.08
    for key, text in LINES:
        for w in text.split():
            n = len(norm(w))
            d = 0.07 + 0.045 * n + (0.1 if w.isupper() and n > 2 else 0)
            out.append({"text": w, "start": round(t, 3), "end": round(t + d, 3)})
            t += d + 0.03 + (0.25 if w.endswith("...") else 0)
        t += 0.4 if key in ("hook", "a3", "b3", "c3", "g4") else 0.18
    return out


def line_words(words):
    res, i = {}, 0
    for key, text in LINES:
        n = len(text.split())
        seg = words[i:i + n]
        assert [norm(w["text"]) for w in seg] == [norm(x) for x in text.split()], (key, [w["text"] for w in seg])
        res[key] = seg
        i += n
    assert i == len(words), (i, len(words))
    return res


orb = lambda tg, dist, pitch, yaw=0, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": round(at, 3), "rig": rig, **({"ease": ease} if ease else {})}
fol = lambda ids, z=0.8, off=None: {"follow": ids, "z": z, **({"offset": off} if off else {}), "window": 0.6}

# cameras (frame-fit + stills; no orbit spins, no 180-degree moves)
EIGHT_A = orb(fol("O1", 0.5), 9.0, 52, 28, 40)                 # elevated 3/4 behind the ball, the line across the frame
EIGHT_FEET = orb([0.55, 13.95, 0.2], 3.6, 50, 28, 38)         # close: ball, line and both feet
BACK_A = orb([-0.9, 14.95, 0.5], 14.0, 46, 12, 42)              # elevated: passer, line, trajectory, receiver
THREE_A = orb([0.8, 5.4, 0.6], 12.5, 64, 10, 42)              # the paint and the ball handler at the top
GOAL_WIDE = orb([-1.4, 3.3, 1.3], 12, 72, 75, 40)            # shooter + defender, rim in frame
GOAL_CLOSE = orb([-0.2, 1.95, 3.0], 4.6, 84, 75, 38)          # close at ring height: ball, hand, ring line


def build(words, voice, music, hook="A"):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, t: next(w for w in W[k] if norm(w["text"]) == norm(t))
    ws = lambda k, t: wd(k, t)["start"]
    we = lambda k, t: wd(k, t)["end"]
    t_end = round(e0("e1") + 1.2, 3)
    hd = max(0.82, round((s0("a1") - 0.1) / 4, 3))
    cuts = {"h1": 0.0, "h2": hd, "h3": 2 * hd, "h4": 3 * hd,
            "eight": s0("a1") - 0.1, "back": s0("b1") - 0.1, "three": s0("c1") - 0.1, "goal": s0("g1") - 0.1,
            "end": s0("e1") - 0.12}
    order = list(cuts)
    dur = {k: round((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k], 3) for i, k in enumerate(order)}
    L = lambda t, sh: round(t - cuts[sh], 3)
    shots = []

    # ------------------------------------------------------------------ HOOK: four teasers, no result shown
    m8, mb, m3, mg = MK["eight"], MK["back"], MK["three"], MK["goal"]
    plates = {
        "eight": dict(name="HOOK 8 s: crossing half court under pressure (before the 8)", play="eight",
                      remap=[[0, m8["eight"] - 1.15], [1, m8["eight"] - 0.2]], camera=[key(0, EIGHT_A)],
                      ov3=[{"type": "centerLine", "color": GOLD, "from": 0.0, "to": 9, "fin": 0, "fout": 0}]),
        "back": dict(name="HOOK backcourt: the pass goes back over the line (before the catch)", play="back",
                     remap=[[0, mb["pass"] - 0.15], [1, mb["pass"] + 0.45]], camera=[key(0, BACK_A)],
                     ov3=[{"type": "centerLine", "color": GOLD, "from": 0.0, "to": 9, "fin": 0, "fout": 0},
                          {"type": "ballTrail", "len": 0.6, "from": 0.1, "to": 9}]),
        "three": dict(name="HOOK 3 s: the big lingers in the paint", play="three",
                      remap=[[0, m3["one"]], [1, m3["two"] + 0.1]], camera=[key(0, THREE_A)],
                      ov3=[{"type": "paint", "opacity": 0.2, "from": 0.0, "to": 9, "fin": 0.15, "fout": 0}]),
        "goal": dict(name="HOOK goaltending: the defender rises to the falling ball, small freeze BEFORE the touch", play="goal",
                     remap=[[0, mg["contact"] - 0.28], [0.55, mg["contact"] - 0.09], [1, mg["contact"] - 0.09]], camera=[key(0, GOAL_CLOSE)],
                     ov3=[{"type": "rimLine", "from": 0.0, "to": 9, "fin": 0.1, "fout": 0}]),
    }
    seq = ["eight", "back", "three", "goal"] if hook == "A" else ["goal", "eight", "back", "three"]
    title_slot = "h4" if hook == "A" else "h1"
    for slot, name in zip(("h1", "h2", "h3", "h4"), seq):
        p = dict(plates[name])
        d = dur[slot]
        p["remap"] = [[round(a * d if a <= 1 else a, 3), b] for a, b in p["remap"]]
        p["ov3"] = [{**o, "to": d} for o in p["ov3"]]
        scr = []
        if name == "goal":
            scr.append({"type": "freeze", "from": round(0.55 * d, 3), "to": d})
        if slot == title_slot:
            scr.append({"type": "title", "lines": ["4 MORE RULES", "EVERY PLAYER NEEDS"], "gold": [0], "from": 0.05, "to": d - 0.05, "y": 236, "size": 92})
        shots.append({"id": slot, "at": cuts[slot], **p, "screen": scr})

    # ------------------------------------------------------------------ 01 EIGHT SECONDS
    sh = "eight"
    d = dur[sh]
    t8 = min(L(we("a2", "frontcourt..."), sh) + 0.15, d - 2.2)
    t5 = t8 - 3.0                                             # 5 -> 8 in real time
    assert t5 >= 0.55, t5
    t_skip = round(min(0.45, t5 * 0.45), 3)
    rm = [[0, 0.0], [t5, m8["eight"] - 3.0], [t8, m8["eight"]], [d, m8["eight"]]]
    t_cross = L(ws("a3", "cross!"), sh)
    t_both = L(ws("a3", "BOTH"), sh)
    S = lambda **kw: shots.append(kw)
    S(id=sh, name="01 8 SECONDS: count 1 > time skip > 5, 6, 7 real time; at 8 the ball bounced in the frontcourt, right foot still behind the line",
      at=cuts[sh], play="eight", remap=rm,
      camera=[key(0, EIGHT_A), key(t8 + 0.25, EIGHT_A), key(t8 + 1.25, EIGHT_FEET, "inOut"), key(d, EIGHT_FEET)],
      ov3=[{"type": "centerLine", "color": GOLD, "draw": 0.5, "from": 0.0, "to": d, "fin": 0.1},
           {"type": "ballRing", "color": GREEN, "from": t8, "to": d, "fin": 0.1},
           {"type": "footRing", "player": "O1", "foot": "L", "color": GREEN, "r": 0.2, "from": t_both, "to": d, "fin": 0.15},
           {"type": "footRing", "player": "O1", "foot": "R", "color": RED, "r": 0.2, "from": t_both, "to": d, "fin": 0.15}],
      screen=[{"type": "section", "n": "01", "text": "8 SECONDS", "y": 200, "from": 0.05, "to": min(d, t5 + 1.2)},
              {"type": "clock", "label": "SECONDS", "y": 470, "align": "right", "size": 112, "from": 0.1, "to": d,
               "steps": [{"at": 0, "text": "1"}, {"at": t_skip, "text": "", "skip": True}, {"at": round(t5 - 0.1, 3), "text": "5"},
                         {"at": round(t5 + 0.9, 3), "text": "6"}, {"at": round(t5 + 1.9, 3), "text": "7"},
                         {"at": round(t8 - 0.1, 3), "text": "8", "tone": "red"}]},
              {"type": "freeze", "from": t8, "to": d},
              {"type": "verdict", "text": "8-SECOND VIOLATION", "tone": "red", "y": 330, "from": round(t8 + 0.3, 3), "to": d, "size": 60}])

    # ------------------------------------------------------------------ 02 BACKCOURT
    sh = "back"
    d = dur[sh]
    t_ctrl, t_send = L(ws("b2", "control"), sh), L(ws("b2", "send"), sh)
    t_over, t_get = L(ws("b2", "over"), sh), L(ws("b2", "get"), sh)
    t_viol = L(ws("b3", "That's"), sh)
    t_catch = min(t_get, t_viol - 0.3)
    rm = [[0, 0.0], [t_ctrl, 0.7], [t_send, mb["pass"] - 0.05], [t_catch, mb["catch"]], [d, mb["catch"]]]
    S(id=sh, name="02 BACKCOURT: frontcourt control, pass back over the line, O2 (backcourt) first to touch = BACKCOURT VIOLATION",
      at=cuts[sh], play="back", remap=rm, camera=[key(0, BACK_A)],
      ov3=[{"type": "centerLine", "color": GOLD, "draw": 0.5, "from": 0.0, "to": d, "fin": 0.1},
           {"type": "ballTrail", "len": 0.9, "from": t_send - 0.05, "to": t_catch + 0.1},
           {"type": "handRing", "player": "O2", "hand": 1, "from": t_catch, "to": d}],
      screen=[{"type": "section", "n": "02", "text": "BACKCOURT", "y": 200, "from": 0.05, "to": min(d, t_ctrl + 0.6)},
              {"type": "chip", "text": "FRONTCOURT CONTROL", "tone": "gold", "align": "center", "size": 54, "from": t_ctrl, "to": t_over, "y": 330},
              {"type": "freeze", "from": t_catch, "to": d},
              {"type": "verdict", "text": "BACKCOURT VIOLATION", "tone": "red", "y": 330, "from": t_viol, "to": d, "size": 60}])

    # ------------------------------------------------------------------ 03 OFFENSIVE 3 SECONDS
    sh = "three"
    d = dur[sh]
    t_paint = L(ws("c1", "paint."), sh)
    t_v = min(L(ws("c3", "Violation."), sh), d - 1.0)
    t_in = t_v - (m3["viol"] - m3["enter"])                  # entry -> violation in real time
    assert t_in >= 0.5, t_in
    rm = [[0, 0.0], [t_in, m3["enter"]], [t_v, m3["viol"]], [d, m3["viol"]]]
    S(id=sh, name="03 OFFENSIVE 3 SECONDS: paint lit, 1-2-3 from the first foot in, violation after MORE than 3 s",
      at=cuts[sh], play="three", remap=rm, camera=[key(0, THREE_A)],
      ov3=[{"type": "paint", "opacity": 0.22, "from": min(t_paint, t_in), "to": d, "fin": 0.3}],
      screen=[{"type": "section", "n": "03", "text": "3 SECONDS", "y": 200, "from": 0.05, "to": min(d, t_in + 1.0)},
              {"type": "clock", "label": "IN THE PAINT", "y": 470, "align": "right", "size": 112, "from": round(t_in + 0.9, 3), "to": d,
               "steps": [{"at": 0, "text": "1"}, {"at": 1.0, "text": "2"}, {"at": 2.0, "text": "3"},
                         {"at": round(t_v - t_in - 0.9, 3), "text": "3", "tone": "red"}]},
              {"type": "freeze", "from": t_v, "to": d},
              {"type": "verdict", "text": "OFFENSIVE 3 SECONDS", "tone": "red", "y": 330, "from": t_v, "to": d, "size": 60}])

    # ------------------------------------------------------------------ 04 GOALTENDING
    sh = "goal"
    d = dur[sh]
    t_rel = L(we("g1", "out."), sh)
    t_down, t_rim = L(ws("g2", "down,"), sh), L(ws("g2", "above"), sh)
    t_touch = L(we("g3", "touches"), sh)
    t_gt, t_cnt = L(ws("g4", "That's"), sh), L(ws("g4", "basket"), sh)
    # brief slow motion only around the contact (the last 0.12 s of play over ~0.9 s of screen), freeze at the touch
    slow0 = max(t_rim + 0.3, t_touch - 0.9)
    rm = [[0, 0.0], [t_rel, mg["release"]], [slow0, mg["contact"] - 0.12], [t_touch, mg["contact"]], [d, mg["contact"]]]
    S(id=sh, name="04 GOALTENDING: two-point shot, the ball descends entirely above the ring, X5 touches it = GOALTENDING, +2",
      at=cuts[sh], play="goal", remap=rm,
      camera=[key(0, GOAL_WIDE), key(t_down - 0.2, GOAL_WIDE), key(slow0, GOAL_CLOSE, "inOut"), key(d, GOAL_CLOSE)],
      ov3=[{"type": "rimLine", "from": t_rim, "to": d, "fin": 0.2},
           {"type": "handRing", "player": "X5", "hand": 0, "from": t_touch, "to": d}],
      screen=[{"type": "section", "n": "04", "text": "ABOVE THE RIM", "y": 200, "from": 0.05, "to": min(d, t_rel + 0.4)},
              {"type": "chip", "text": "DESCENDING", "tone": "gold", "align": "center", "size": 54, "from": t_down, "to": t_touch, "y": 330},
              {"type": "freeze", "from": t_touch, "to": d},
              {"type": "verdict", "text": "GOALTENDING", "tone": "red", "y": 330, "from": t_gt, "to": d, "size": 64},
              {"type": "score", "text": "+2", "sub": "THE BASKET COUNTS", "y": 440, "size": 150, "from": t_cnt, "to": d}])

    # ------------------------------------------------------------------ CLOSE: the question
    sh = "end"
    d = dur[sh]
    S(id=sh, name="CLOSE: which rule catches you out? (wide 8-second frame, the line lit)", at=cuts[sh], play="eight",
      remap=[[0, m8["eight"] - 1.6], [d, m8["eight"] - 0.4]], camera=[key(0, EIGHT_A)],
      ov3=[{"type": "centerLine", "color": GOLD, "from": 0.0, "to": d, "fin": 0}],
      screen=[{"type": "scrim", "opacity": 0.35, "from": 0.0, "to": d},
              {"type": "title", "lines": ["WHICH RULE", "CATCHES YOU OUT?"], "gold": [1], "from": 0.05, "to": d, "y": 236, "size": 100},
              {"type": "micro", "text": "1 · 8 SECONDS   2 · BACKCOURT   3 · 3 SECONDS   4 · GOALTENDING", "y": 1255, "from": 0.3, "to": d},
              {"type": "logo", "big": False, "from": max(0.2, d - 1.3), "to": d}])

    ep = {
        "id": "rules4p2", "title": "4 BASKETBALL RULES EVERY PLAYER NEEDS TO UNDERSTAND - PART 2", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33",
        "words": words,
        "subtitleGroups": GROUPS,
        "subtitleBlock": True, "subtitleY": 1390,
        "keywords": ["FOUR", "MORE", "EIGHT", "SECONDS.", "BOTH", "AND", "cross!", "BACKCOURT.", "BACKCOURT", "paint.",
                     "three", "Violation.", "down,", "above", "touches", "GOALTENDING!", "counts!", "Which"],
        "gradeBottom": 0.3,
        "shots": shots, "plays": {k: PL[k] for k in IDS},
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    meta = {"duration": t_end, "cuts": {k: round(v, 3) for k, v in cuts.items()}, "hook": hook}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words")
    ap.add_argument("--placeholder", help="write placeholder word times to this file and use them")
    ap.add_argument("--voice", default="tactical/realism-v3-3/silence.mp3")
    ap.add_argument("--music")
    ap.add_argument("--hook", default="A", choices=["A", "B"])
    ap.add_argument("--fit", help="also write a frame-fit episode (plays by name) + its words file")
    a = ap.parse_args()
    if a.placeholder:
        words = placeholder_words()
        json.dump(words, open(a.placeholder, "w"))
    else:
        words = json.load(open(a.words))
    props, meta = build(words, a.voice, a.music, a.hook)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"])
        ep["plays"] = {k: f"rules4p2-{k}" for k in IDS}
        json.dump(ep, open(a.fit, "w"))
        json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    print(json.dumps(meta))
