#!/usr/bin/env python3
"""E2A - 4 RULES EVERY PLAYER MUST KNOW (owner brief 2026-11-24). Rules / fundamentals format:
HOOK (4-shot montage: travel, double dribble, +3, foul) -> 01 TRAVELING -> 02 DOUBLE DRIBBLE -> 03 SCORING
(+1 / +2 / +3 / on the line = 2) -> 04 FOULS (holding -> personal foul -> throw-in, not free throws) -> CLOSE (loops
into the hook's first frame: same play, same camera, the ball in the hands just before the pivot foot lifts).
E2A Basketball Visual Standard v1 (athleteRenderer v33, env cinema, 2026 logo), Floor Graphics Stability Standard
(one ring per idea, cross-fades, stable floor meshes), new rules overlays (src/t3d/rules3d.tsx: footRing, ballRing,
handRing, area2, arc3) and screen items (score, verdict, section).
Plays: tactical/specs/_gen-rules4.py (rules4-*). Narration: the owner-approved eleven_v3 Deuce take (words from Scribe).
  python3 tactical/episodes/_gen-rules4.py --words W.json --voice rules4/voice.wav --music rules4/music.wav --out props.json
Options: --trial (alternative hook order + grade/zoom for the IG trial copy, same voice)."""
import argparse, json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
IDS = ["travel", "dribble", "ft", "two", "three", "line", "foul", "throwin"]
PL = {k: json.load(open(os.path.join(T, "tactical", "plays", f"rules4-{k}.json"))) for k in IDS}
GOLD, NAVY, WHITE, RED, GREEN = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A", "#2FBF71"

LINES = [
    ("hook", "These are the FOUR RULES every basketball player needs to understand."),
    ("t1", "First: TRAVELING."),
    ("t2", "Catch the ball, set your pivot foot..."),
    ("t3", "then lift it and put it back down while you're still holding the ball?"),
    ("t4", "That's a TRAVEL!"),
    ("d1", "Second: DOUBLE DRIBBLE."),
    ("d2", "Stop your dribble, hold the ball..."),
    ("d3", "and start bouncing again?"),
    ("d4", "VIOLATION!"),
    ("s1", "Third: SCORING."),
    ("s2", "Free throw: ONE!"),
    ("s3", "Inside the arc: TWO!"),
    ("s4", "Beyond the arc: THREE!"),
    ("s5", "But step on that line?"),
    ("s6", "Still two!"),
    ("f1", "Fourth: FOULS."),
    ("f2", "Push or hold an opponent and restrict their movement?"),
    ("f3", "That's a foul."),
    ("f4", "But remember: not every foul means free throws."),
    ("e1", "Four rules."),
    ("e2", "Play smarter."),
    ("e3", "Follow E2A for more!"),
]
# subtitle chunks (words per block): long lines split at the natural breath
GROUPS = [5, 6, 2, 7, 8, 6, 3, 3, 6, 4, 1, 2, 3, 4, 4, 5, 2, 2, 5, 4, 3, 2, 6, 2, 2, 4]
assert sum(GROUPS) == 101

norm = lambda s: "".join(c for c in s.lower() if c.isalnum())


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


def yaw_from(dx, dy):
    """orbit yaw that puts the camera on the (dx, dy) side of its target (camera3d: back(yaw) = (-sin, cos))"""
    return round(math.degrees(math.atan2(-dx, dy)), 2)


orb = lambda tg, dist, pitch, yaw=0, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": round(at, 3), "rig": rig, **({"ease": ease} if ease else {})}
fol = lambda ids, z=0.8, off=None: {"follow": ids, "z": z, **({"offset": off} if off else {}), "window": 0.5}

# cameras (checked with frame-fit + stills; no orbit spins, no 180-degree moves)
TRAVEL_A = orb([2.75, 7.25, 0.7], 7.4, 68, -110, 38)
TRAVEL_FEET = orb([3.05, 7.35, 0.5], 5.2, 64, -110, 38)                      # push-in to the feet (ball still in frame)
DRIB_A = orb(fol("O1", 0.6), 7.5, 64, 110, 40)
DRIB_HANDS = orb(fol("O1", 0.6), 6.0, 66, 110, 40)
SCORE_FT = orb([0.0, 4.6, 0.7], 12.0, 60, 0, 44)
SCORE_B = orb([0.0, 4.4, 0.0], 18.0, 46, 0, 44)
SCORE_2 = orb([-2.6, 4.2, 0.4], 13.5, 54, 44, 44)
SCORE_3 = orb([3.6, 5.8, 0.4], 15.0, 54, -39.5, 44)
LINE_FEET = orb([-3.03, 7.6, 0.2], 3.0, 58, -20, 38)                       # detail: front toe on the line
LINE_WIDE = orb([-2.4, 6.4, 0.4], 14.0, 54, 26, 44)
FOUL_A = orb(fol(["O1", "X1"], 0.6), 8.0, 64, -60, 40)
FOUL_HAND = orb(fol(["O1", "X1"], 0.8), 6.3, 66, -60, 40)
THROW = orb([6.49, 8.1, 0.0], 11.75, 40, 90, 42)


def build(words, voice, music, trial=False):
    W = line_words(words)
    by = {}
    for k, seg in W.items():
        for w in seg:
            by.setdefault(norm(w["text"]), []).append(w)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, t: next(w for w in W[k] if norm(w["text"]) == norm(t))
    ws = lambda k, t: wd(k, t)["start"]
    we = lambda k, t: wd(k, t)["end"]
    t_end = round(e0("e3") + 0.5, 3)
    cuts = {
        "h1": 0.0, "h2": 0.95, "h3": 1.95, "h4": 2.95,
        "travel": s0("t1") - 0.12,
        "dribble": s0("d1") - 0.1,
        "ft": s0("s1") - 0.1,
        "two": s0("s3") - 0.1,
        "three": s0("s4") - 0.1,
        "lineD": s0("s5") - 0.08,
        "lineW": s0("s6") - 0.06,
        "foul": s0("f1") - 0.1,
        "throw": s0("f4") - 0.1,
        "end": s0("e1") - 0.08,
    }
    order = list(cuts)
    dur = {k: round((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k], 3) for i, k in enumerate(order)}
    L = lambda t, sh: round(t - cuts[sh], 3)
    shots = []
    S = lambda **kw: shots.append(kw)

    # ------------------------------------------------------------------ HOOK: four 1 s plates, one idea each
    d = dur["h1"]
    S(id="h1", name="HOOK 1 travel: the pivot foot lifts and lands, red ring", at=cuts["h1"], play="travel",
      remap=[[0, 2.95], [0.62, 3.45], [d, 3.45]], camera=[key(0, TRAVEL_A), key(d, TRAVEL_FEET, "inOut")],
      ov3=[{"type": "footRing", "player": "O1", "foot": "L", "color": RED, "from": 0.0, "to": d, "fin": 0, "fout": 0}],
      screen=[{"type": "verdict", "text": "TRAVEL", "tone": "red", "y": 330, "from": 0.58, "to": d, "size": 62}])
    d = dur["h2"]
    S(id="h2", name="HOOK 2 double dribble: held ball goes back to the floor", at=cuts["h2"], play="dribble",
      remap=[[0, 3.05], [0.68, 3.68], [d, 3.68]], camera=[key(0, DRIB_HANDS)],
      ov3=[{"type": "ballRing", "color": RED, "from": 0.5, "to": d, "fout": 0}],
      screen=[{"type": "verdict", "text": "DOUBLE DRIBBLE", "tone": "red", "y": 330, "from": 0.6, "to": d, "size": 62}])
    d = dur["h3"]
    S(id="h3", name="HOOK 3 three: clean arc, +3", at=cuts["h3"], play="three",
      remap=[[0, 0.72], [0.86, 2.17], [d, 2.25]], camera=[key(0, SCORE_3)],
      ov3=[{"type": "ballTrail", "len": 0.35, "from": 0.1, "to": 0.86}],
      screen=[{"type": "score", "text": "+3", "y": 560, "size": 200, "from": 0.8, "to": d}])
    d = dur["h4"]
    S(id="h4", name="HOOK 4 foul: the grab, freeze, FOUL; title", at=cuts["h4"], play="foul",
      remap=[[0, 0.8], [0.5, 1.4], [d, 1.4]], camera=[key(0, FOUL_HAND)],
      ov3=[{"type": "handRing", "player": "X1", "hand": 0, "from": 0.3, "to": d, "fout": 0}],
      screen=[{"type": "freeze", "from": 0.5, "to": d},
              {"type": "verdict", "text": "FOUL", "tone": "red", "y": 1180, "from": 0.5, "to": d, "size": 62},
              {"type": "title", "lines": ["4 RULES", "EVERY PLAYER NEEDS"], "gold": [0], "from": 0.05, "to": d - 0.05, "y": 236, "size": 96}])

    # ------------------------------------------------------------------ 01 TRAVELING
    sh = "travel"
    d = dur[sh]
    t_catch, t_set, t_foot = L(we("t2", "ball,"), sh), L(ws("t2", "set"), sh), L(we("t2", "foot..."), sh)
    t_lift, t_down = L(ws("t3", "lift"), sh), L(we("t3", "down"), sh)
    t_while, t_trav = L(ws("t3", "while"), sh), L(ws("t4", "That's"), sh)
    rm = [[0, 0.0], [L(s0("t2"), sh), 0.5], [t_catch, 1.12], [t_set + 0.25, 1.62], [t_foot, 2.35], [t_lift, 2.98],
          [t_down - 0.1, 3.45], [d, 3.45]]
    S(id=sh, name="01 TRAVELING: catch, legal pivot on the left foot, the pivot foot lifts and lands = TRAVEL", at=cuts[sh], play="travel",
      remap=rm, camera=[key(0, TRAVEL_A), key(t_lift - 0.2, TRAVEL_A), key(t_lift + 0.5, TRAVEL_FEET, "inOut"), key(d, TRAVEL_FEET)],
      ov3=[{"type": "footRing", "player": "O1", "foot": "L", "color": GOLD, "from": L(ws("t2", "pivot"), sh), "to": t_lift + 0.15, "fout": 0.15},
           {"type": "footRing", "player": "O1", "foot": "L", "color": RED, "from": t_lift, "to": d, "fin": 0.15, "fout": 0.2},
           {"type": "ballRing", "color": GOLD, "from": t_while, "to": t_trav, "fout": 0.15}],
      screen=[{"type": "section", "n": "01", "text": "TRAVELING", "y": 200, "from": 0.05, "to": d},
              {"type": "pin", "player": "O1", "text": "PIVOT FOOT", "tone": "gold", "z": 0.05, "dy": 70, "from": L(ws("t2", "pivot"), sh), "to": t_lift, "size": 38},
              {"type": "verdict", "text": "LEGAL PIVOT", "tone": "green", "y": 330, "from": t_foot - 0.55, "to": t_lift - 0.05, "size": 52},
              {"type": "pin", "player": "O1", "text": "LIFTED", "tone": "red", "z": 0.05, "dy": 70, "from": t_lift + 0.15, "to": t_down, "size": 38},
              {"type": "freeze", "from": t_down - 0.1, "to": d},
              {"type": "chip", "text": "STILL HOLDING THE BALL", "tone": "gold", "align": "center", "size": 54, "from": t_while, "to": t_trav, "y": 330},
              {"type": "verdict", "text": "TRAVEL", "tone": "red", "y": 330, "from": t_trav, "to": d, "size": 70}])

    # ------------------------------------------------------------------ 02 DOUBLE DRIBBLE
    sh = "dribble"
    d = dur[sh]
    t_stop, t_dend = L(ws("d2", "Stop"), sh), L(we("d2", "dribble,"), sh)
    t_hold, t_hend = L(ws("d2", "hold"), sh), L(we("d2", "ball..."), sh)
    t_again, t_viol = L(ws("d3", "and"), sh), L(ws("d4", "VIOLATION!"), sh)
    rm = [[0, 0.15], [t_stop, 1.55], [t_dend - 0.05, 2.12], [t_hend, 3.28], [t_again + 0.15, 3.42], [L(we("d3", "again?"), sh) - 0.35, 3.66], [d, 3.66]]
    S(id=sh, name="02 DOUBLE DRIBBLE: dribble, two-hand pick-up (ended), hold, dribble again = VIOLATION", at=cuts[sh], play="dribble",
      remap=rm, camera=[key(0, DRIB_A), key(t_dend - 0.3, DRIB_A), key(t_hold + 0.4, DRIB_HANDS, "inOut"), key(d, DRIB_HANDS)],
      ov3=[{"type": "ballRing", "color": GOLD, "from": t_dend - 0.1, "to": t_again + 0.2, "fout": 0.15},
           {"type": "ballRing", "color": RED, "from": L(we("d3", "again?"), sh) - 0.4, "to": d, "fin": 0.12}],
      screen=[{"type": "section", "n": "02", "text": "DOUBLE DRIBBLE", "y": 200, "from": 0.05, "to": d},
              {"type": "chip", "text": "DRIBBLE ENDED", "tone": "gold", "align": "center", "size": 56, "from": t_dend - 0.1, "to": t_again, "y": 330},
              {"type": "freeze", "from": L(we("d3", "again?"), sh) - 0.35, "to": d},
              {"type": "verdict", "text": "DOUBLE DRIBBLE", "tone": "red", "y": 330, "from": t_viol, "to": d, "size": 64}])

    # ------------------------------------------------------------------ 03 SCORING
    sh = "ft"
    d = dur[sh]
    t_one = L(ws("s2", "ONE!"), sh)
    rel = L(ws("s2", "Free"), sh) - 0.05
    S(id=sh, name="03 SCORING: free throw = +1 (camera behind the shooter, FT line lit)", at=cuts[sh], play="ft",
      remap=[[0, 0.2], [rel, 1.0], [t_one + 0.05, 2.1], [d, 2.5]], camera=[key(0, SCORE_FT)],
      ov3=[{"type": "route", "player": "O1", "t0": 0, "t1": 0, "pts": [[-1.8, 5.8], [1.8, 5.8]], "color": GOLD, "width": 0.1, "draw": 0.4, "noHead": True, "from": 0.2, "to": d},
           {"type": "ballTrail", "len": 0.35, "from": rel, "to": t_one}],
      screen=[{"type": "section", "n": "03", "text": "SCORING", "y": 200, "from": 0.05, "to": d},
              {"type": "score", "text": "+1", "sub": "FREE THROW", "y": 560, "from": t_one, "to": d}])
    sh = "two"
    d = dur[sh]
    t_two = L(ws("s3", "TWO!"), sh)
    S(id=sh, name="+2 inside the arc (elevated, two-point area lit)", at=cuts[sh], play="two",
      remap=[[0, 0.85], [t_two + 0.05, 2.05], [d, 2.4]], camera=[key(0, SCORE_2)],
      ov3=[{"type": "area2", "opacity": 0.3, "from": 0.0, "to": d, "fin": 0.25},
           {"type": "ballTrail", "len": 0.35, "from": 0.1, "to": t_two}],
      screen=[{"type": "score", "text": "+2", "sub": "INSIDE THE ARC", "y": 560, "from": t_two, "to": d}])
    sh = "three"
    d = dur[sh]
    t_three = L(ws("s4", "THREE!"), sh)
    S(id=sh, name="+3 beyond the arc (elevated, arc traced)", at=cuts[sh], play="three",
      remap=[[0, 0.82], [t_three + 0.12, 2.17], [d, 2.6]], camera=[key(0, SCORE_3)],
      ov3=[{"type": "arc3", "width": 0.12, "draw": 0.45, "from": 0.0, "to": d, "fin": 0.15},
           {"type": "ballTrail", "len": 0.35, "from": 0.15, "to": t_three + 0.1}],
      screen=[{"type": "score", "text": "+3", "sub": "BEYOND THE ARC", "y": 560, "from": t_three + 0.1, "to": d}])
    sh = "lineD"
    d = dur[sh]
    S(id=sh, name="ON THE LINE: detail, the front toe on the three-point line", at=cuts[sh], play="line",
      remap=[[0, 0.35], [d, 1.15]], camera=[key(0, LINE_FEET)],
      ov3=[{"type": "arc3", "width": 0.11, "from": 0.0, "to": d, "fin": 0.12, "fout": 0},
           {"type": "footRing", "player": "O1", "foot": "L", "color": RED, "r": 0.2, "from": 0.25, "to": d, "fout": 0}],
      screen=[{"type": "chip", "text": "TOE ON THE LINE", "tone": "red", "align": "center", "size": 56, "from": 0.3, "to": d, "y": 330}])
    sh = "lineW"
    d = dur[sh]
    t_still = L(ws("s6", "two!"), sh)
    S(id=sh, name="Still two: the shot from the line goes in, +2", at=cuts[sh], play="line",
      remap=[[0, 1.38], [t_still + 0.1, 2.55], [d, 2.95]], camera=[key(0, LINE_WIDE)],
      ov3=[{"type": "arc3", "width": 0.11, "from": 0.0, "to": d, "fin": 0}, {"type": "ballTrail", "len": 0.35, "from": 0.05, "to": t_still}],
      screen=[{"type": "score", "text": "+2", "sub": "ON THE LINE = 2", "y": 560, "from": t_still + 0.05, "to": d}])

    # ------------------------------------------------------------------ 04 FOULS
    sh = "foul"
    d = dur[sh]
    t_push, t_hold = L(ws("f2", "Push"), sh), L(ws("f2", "hold"), sh)
    t_restr, t_foul = L(ws("f2", "restrict"), sh), L(ws("f3", "That's"), sh)
    t_frz = L(we("f2", "movement?"), sh) - 0.55
    rm = [[0, 0.0], [t_push, 0.55], [t_hold + 0.1, 1.12], [t_restr + 0.1, 1.75], [t_frz, 1.98], [d, 1.98]]
    S(id=sh, name="04 FOULS: X1 grabs the driver's waist and stops him = PERSONAL FOUL", at=cuts[sh], play="foul",
      remap=rm, camera=[key(0, FOUL_A), key(t_hold, FOUL_A), key(t_hold + 0.8, FOUL_HAND, "inOut"), key(d, FOUL_HAND)],
      ov3=[{"type": "handRing", "player": "X1", "hand": 0, "from": t_hold + 0.12, "to": d}],
      screen=[{"type": "section", "n": "04", "text": "FOULS", "y": 200, "from": 0.05, "to": d},
              {"type": "pin", "player": "X1", "text": "HOLDING", "tone": "red", "from": t_hold + 0.15, "to": t_restr, "size": 40},
              {"type": "chip", "text": "RESTRICTS MOVEMENT", "tone": "red", "align": "center", "size": 54, "from": t_restr, "to": t_foul, "y": 330},
              {"type": "freeze", "from": t_frz, "to": d},
              {"type": "verdict", "text": "PERSONAL FOUL", "tone": "red", "y": 330, "from": t_foul, "to": d, "size": 64}])
    sh = "throw"
    d = dur[sh]
    t_not = L(ws("f4", "not"), sh)
    S(id=sh, name="No shot, no team-foul penalty: throw-in from the sideline, no free throws", at=cuts[sh], play="throwin",
      remap=[[0, 0.2], [t_not, 1.0], [t_not + 0.55, 1.55], [d, 2.6]], camera=[key(0, THROW)],
      ov3=[{"type": "route", "player": "O1", "t0": 0, "t1": 0, "pts": [[7.5, 6.4], [7.5, 11.0]], "color": WHITE, "width": 0.1, "draw": 0.4, "noHead": True, "from": 0.1, "to": d},
           {"type": "ballTrail", "len": 0.3, "from": t_not - 0.05, "to": t_not + 0.6}],
      screen=[{"type": "chip", "text": "NO SHOT → THROW-IN", "tone": "gold", "align": "center", "size": 56, "from": 0.15, "to": t_not - 0.05, "y": 330},
              {"type": "title", "lines": ["NOT EVERY FOUL", "= FREE THROWS"], "gold": [1], "from": t_not, "to": d - 0.05, "y": 236, "size": 92},
              {"type": "micro", "text": "NON-SHOOTING FOUL · TEAM NOT IN PENALTY", "y": 1255, "from": t_not + 0.3, "to": d - 0.1}])

    # ------------------------------------------------------------------ CLOSE (loops into h1)
    sh = "end"
    d = dur[sh]
    e2, e3 = L(s0("e2"), sh), L(s0("e3"), sh)
    S(id=sh, name="CLOSE: four rules, play smarter, follow E2A; the frame leads back into the hook", at=cuts[sh], play="travel",
      remap=[[0, 2.45], [d, 2.95]], camera=[key(0, TRAVEL_A)],
      ov3=[{"type": "footRing", "player": "O1", "foot": "L", "color": GOLD, "from": 0.1, "to": d, "fout": 0}],
      screen=[{"type": "title", "lines": ["4 RULES."], "gold": [0], "from": 0.05, "to": e2, "y": 236, "size": 120},
              {"type": "title", "lines": ["PLAY", "SMARTER."], "gold": [1], "from": e2, "to": e3, "y": 236, "size": 112},
              {"type": "title", "lines": ["FOLLOW", "E2A"], "gold": [1], "from": e3, "to": d, "y": 236, "size": 112},
              {"type": "logo", "big": False, "from": e3, "to": d}])

    ep = {
        "id": "rules4-trial" if trial else "rules4", "title": "4 RULES EVERY PLAYER MUST KNOW", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33",
        "words": words,
        "subtitleGroups": GROUPS,
        "subtitleBlock": True, "subtitleY": 1390,
        "keywords": ["FOUR", "RULES", "TRAVELING.", "pivot", "TRAVEL!", "DOUBLE", "DRIBBLE.", "VIOLATION!", "SCORING.", "ONE!", "TWO!",
                     "THREE!", "line?", "two!", "FOULS.", "foul.", "free", "throws.", "smarter."],
        "gradeBottom": 0.3,
        "shots": shots, "plays": {k: PL[k] for k in IDS},
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    meta = {"duration": t_end, "cuts": {k: round(v, 3) for k, v in cuts.items()}}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words", required=True)
    ap.add_argument("--voice", default="tactical/realism-v3-3/silence.mp3")
    ap.add_argument("--music")
    ap.add_argument("--trial", action="store_true")
    ap.add_argument("--fit", help="also write a frame-fit episode (plays by name) + its words file")
    a = ap.parse_args()
    words = json.load(open(a.words))
    props, meta = build(words, a.voice, a.music, a.trial)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"])
        ep["plays"] = {k: f"rules4-{k}" for k in IDS}
        json.dump(ep, open(a.fit, "w"))
        json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    print(json.dumps(meta))
