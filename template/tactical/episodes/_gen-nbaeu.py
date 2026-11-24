#!/usr/bin/env python3
"""E2A - NBA VS EUROLEAGUE: 4 RULES THAT CHANGE THE GAME (owner brief 2026-11-24).
Same format as "4 Rules" (hook, 4 numbered sections, energetic narration, 3D demos, close with a question), upgraded:
two court identities on ONE world (only the painted lines change: src/tactical/geometry.ts COURTS), regulation clocks
(no running clock), the real NBA/FIBA arcs with the same 7.00 m shot on both, a player's personal-foul track, a 5 v 5
defensive 3 seconds count. E2A Basketball Visual Standard v1 (v33, cinema, 2026 logo), Floor Graphics Stability Standard.
  python3 tactical/episodes/_gen-nbaeu.py --words W.json --voice nbaeu/voice.wav --music nbaeu/music.wav --out props.json
  --placeholder   synthesise word timings from the script (preview before the narration exists)
  --trial         alternative hook order + title for the IG trial copy (same voice)"""
import argparse, json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
IDS = ["three-el", "three-nba", "foul-el", "foul-nba", "walkoff", "d3s-nba", "d3s-el"]
PL = {k: json.load(open(os.path.join(T, "tactical", "plays", f"nbaeu-{k}.json"))) for k in IDS}
GOLD, NAVY, WHITE, RED, GREEN = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A", "#2FBF71"
NBA_C, EL_C = "#4F8BFF", "#FF9A3C"   # floor-graphic versions of the league tones (a touch lighter than the tags)
BASKET_Y = 1.575
SPOT = PL["three-el"]["tracks"]["O1"][0][1:]  # body centre 7.05 m: every sole point between the two painted lines (qc-nbaeu)

LINES = [
    ("h1", "Same sport."),
    ("h2", "Different rules."),
    ("h3", "Here's NBA versus EuroLeague!"),
    ("t1", "Rule one: GAME TIME."),
    ("t2", "NBA quarters are twelve minutes..."),
    ("t3", "FORTY-EIGHT!"),
    ("t4", "EuroLeague plays ten..."),
    ("t5", "FORTY!"),
    ("a1", "Rule two: the THREE-POINT LINE."),
    ("a2", "NBA: seven point two four metres."),
    ("a3", "EuroLeague: six point seven five."),
    ("a4", "Same shot, seven metres out."),
    ("a5", "EuroLeague?"),
    ("a6", "THREE!"),
    ("a7", "NBA?"),
    ("a8", "Just TWO!"),
    ("f1", "Rule three: FOUL OUT."),
    ("f2", "EuroLeague: FIVE!"),
    ("f3", "And you're out."),
    ("f4", "NBA?"),
    ("f5", "SIX!"),
    ("d1", "And the BIG one..."),
    ("d2", "DEFENSIVE THREE SECONDS."),
    ("d3", "In the NBA, a defender can't stay in the paint without guarding someone."),
    ("d4", "One... two... three..."),
    ("d5", "TECHNICAL FOUL!"),
    ("d6", "EuroLeague?"),
    ("d7", "No defensive three-second rule."),
    ("d8", "The big can stay home and protect the rim."),
    ("e1", "Which rules do you prefer?"),
]
norm = lambda s: "".join(c for c in s.lower() if c.isalnum())


def placeholder_words():
    """rough timing for previews: 0.3 s per word + 0.04 s per letter, pauses after '...', '?', '!' and '.'"""
    out, t = [], 0.15
    for _, text in LINES:
        for w in text.split():
            d = 0.2 + 0.035 * len(norm(w))
            out.append({"text": w, "start": round(t, 3), "end": round(t + d, 3)})
            t += d + 0.05
            if w.endswith("..."):
                t += 0.3
            elif w[-1] in "?!.":
                t += 0.18
    return out


def line_words(words):
    """map the script lines onto the transcript; Scribe may merge / split hyphenated numbers, so match on letters"""
    res, i = {}, 0
    for key, text in LINES:
        target = norm(text)
        got, seg = "", []
        while i < len(words) and len(got) < len(target):
            seg.append(words[i])
            got += norm(words[i]["text"])
            i += 1
        assert got == target, (key, got, target)
        res[key] = seg
    assert i == len(words), (i, len(words))
    return res


orb = lambda tg, dist, pitch, yaw=0, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": round(at, 3), "rig": rig, **({"ease": ease} if ease else {})}

# cameras (frame-fit checked; no orbit spins)
WIDE_HI = orb([0.0, 5.8, 0.0], 23.5, 46, 0, 44)          # whole half court from behind half court, both arcs readable
WIDE_HI_IN = orb([0.0, 5.6, 0.0], 21.5, 44, 0, 44)
TIME_BG = orb([0.0, 6.0, 0.0], 24.0, 50, 8, 44)
ARCS = orb([0.0, 7.0, 0.0], 13.5, 26, 0, 40)               # top of the key, tilted: arcs + the shooter's feet
ARCS_FEET = orb([0.0, 8.5, 0.1], 6.8, 24, 0, 38)
SHOT = orb([0.0, 6.8, 1.0], 16.0, 50, 0, 42)               # behind/above the shooter: feet on the floor + ball into the rim
FOUL_A = orb({"follow": ["O1", "X1"], "z": 0.6, "window": 0.5}, 8.4, 62, -60, 40)
WALK = orb({"follow": ["X1"], "z": 0.8, "window": 0.6}, 9.0, 60, -75, 42)
D3S = orb([0.06, 5.5, 0.0], 22.5, 38, 0, 44)                # elevated, very clear: whole lane + all 10 players
D3S_IN = orb([0.0, 4.6, 0.0], 16.0, 40, 0, 42)


def build(words, voice, music, trial=False):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, t: next(w for w in W[k] if norm(w["text"]).startswith(norm(t)))
    ws = lambda k, t: wd(k, t)["start"]
    t_end = round(e0("e1") + 0.45, 3)
    cuts = {
        "h1": 0.0, "h2": s0("h2") - 0.06, "h3": s0("h3") - 0.06,
        "time": s0("t1") - 0.1, "timeEL": s0("t4") - 0.08,
        "arcs": s0("a1") - 0.1, "el3": s0("a5") - 0.1, "nba2": s0("a7") - 0.08,
        "foulEL": s0("f1") - 0.1, "walk": s0("f3") - 0.08, "foulNBA": s0("f4") - 0.08,
        "d3s": s0("d1") - 0.1, "d3sEL": s0("d6") - 0.08,
        "end": s0("e1") - 0.08,
    }
    order = list(cuts)
    dur = {k: round((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k], 3) for i, k in enumerate(order)}
    L = lambda t, sh: round(t - cuts[sh], 3)
    shots = []
    S = lambda **kw: shots.append(kw)

    # ------------------------------------------------------------------ HOOK (0-~4 s): two courts, one clean switch
    first, second = ("nba", "el") if trial else ("el", "nba")
    P = {"el": "d3s-el", "nba": "d3s-nba"}
    AC = {"el": (EL_C, "fiba", "40 MIN"), "nba": (NBA_C, "nba", "48 MIN")}
    sh = "h1"
    d = dur[sh]
    c, r, mins = AC[first]
    S(id=sh, name=f"HOOK 1 {first.upper()} court: arc traced, league tag, {mins}", at=cuts[sh], play=P[first],
      remap=[[0, 0.6], [d, 0.6 + d]], camera=[key(0, WIDE_HI), key(d, WIDE_HI_IN)],
      ov3=[{"type": "arc3", "rules": r, "color": c, "width": 0.13, "draw": 0.55, "z": 0.014, "from": 0.05, "to": d, "fout": 0}],
      screen=[{"type": "league", "league": first, "y": 170, "from": 0.0, "to": d, "size": 70},
              {"type": "chip", "text": mins, "tone": "gold", "align": "center", "size": 62, "from": 0.25, "to": d, "y": 300}])
    sh = "h2"
    d = dur[sh]
    c, r, mins = AC[second]
    S(id=sh, name=f"HOOK 2 {second.upper()} court (whip in): arc traced, league tag, {mins}", at=cuts[sh], play=P[second],
      remap=[[0, 0.6 + dur["h1"]], [d, 0.6 + dur["h1"] + d]], camera=[key(0, WIDE_HI_IN), key(d, WIDE_HI)],
      ov3=[{"type": "arc3", "rules": r, "color": c, "width": 0.13, "draw": 0.5, "z": 0.014, "from": 0.0, "to": d, "fin": 0, "fout": 0}],
      screen=[{"type": "whip", "amount": 0.9, "dir": 1, "from": 0.0, "to": 0.22},
              {"type": "league", "league": second, "y": 170, "from": 0.0, "to": d, "size": 70},
              {"type": "chip", "text": mins, "tone": "gold", "align": "center", "size": 62, "from": 0.15, "to": d, "y": 300}])
    sh = "h3"
    d = dur[sh]
    S(id=sh, name="HOOK 3 NBA vs EUROLEAGUE: both arcs on one floor + the defender camped in the lane", at=cuts[sh], play="d3s-nba",
      remap=[[0, 1.0], [d, 1.0 + d]], camera=[key(0, D3S), key(d, orb([0.06, 5.4, 0.0], 21.0, 38, 0, 44))],
      ov3=[{"type": "arc3", "rules": "nba", "color": NBA_C, "width": 0.12, "z": 0.014, "from": 0.0, "to": d, "fin": 0.12, "fout": 0},
           {"type": "arc3", "rules": "fiba", "color": EL_C, "width": 0.12, "z": 0.016, "from": 0.0, "to": d, "fin": 0.12, "fout": 0},
           {"type": "lane", "rules": "nba", "color": RED, "opacity": 0.16, "from": 0.15, "to": d, "fin": 0.2, "fout": 0},
           {"type": "footRing", "player": "X5", "foot": "L", "color": RED, "r": 0.5, "from": 0.2, "to": d, "fout": 0}],
      screen=[{"type": "vs", "y": 150, "size": 104, "from": 0.0, "to": d}])

    # ------------------------------------------------------------------ 01 GAME TIME: regulation clocks, not a running clock
    sh = "time"
    d = dur[sh]
    clocks = {"type": "clocks", "nba": L(s0("t2"), sh), "nbaTotal": L(ws("t3", "FORTY"), sh), "el": L(s0("t4"), sh),
              "elTotal": L(ws("t5", "FORTY"), sh), "y": 560, "sub": "REGULATION TIME · 4 QUARTERS"}
    S(id=sh, name="01 GAME TIME: NBA 4 x 12:00 = 48", at=cuts[sh], play="d3s-nba",
      remap=[[0, 1.2], [d, 1.2 + d * 0.6]], camera=[key(0, TIME_BG), key(d, orb([0.0, 6.2, 0.0], 18.0, 46, 4, 44))],
      screen=[{"type": "scrim", "opacity": 0.62, "from": 0, "to": d},
              {"type": "section", "n": "01", "text": "GAME TIME", "y": 200, "from": 0.05, "to": d},
              {**clocks, "from": 0.0, "to": d}])
    sh = "timeEL"
    d = dur[sh]
    off = cuts["timeEL"] - cuts["time"]
    S(id=sh, name="01 GAME TIME: EuroLeague 4 x 10:00 = 40 (same clocks, court switches under them)", at=cuts[sh], play="d3s-el",
      remap=[[0, 1.2 + off * 0.6], [d, 1.2 + (off + d) * 0.6]], camera=[key(0, orb([0.0, 6.2, 0.0], 18.0, 46, 4, 44)), key(d, orb([0.0, 6.0, 0.0], 17.2, 46, 0, 44))],
      screen=[{"type": "scrim", "opacity": 0.62, "from": -off, "to": d},
              {"type": "section", "n": "01", "text": "GAME TIME", "y": 200, "from": -off, "to": d},
              {**{k: (v - off if isinstance(v, float) else v) for k, v in clocks.items()}, "from": -off, "to": d}])

    # ------------------------------------------------------------------ 02 THREE-POINT LINE
    sh = "arcs"
    d = dur[sh]
    t_nba, t_el, t_same = L(s0("a2"), sh), L(s0("a3"), sh), L(s0("a4"), sh)
    S(id=sh, name="02 THREE-POINT LINE: both real arcs on one floor (NBA 7.24 m / 6.71 m corners, FIBA 6.75 m), the 7.00 m spot", at=cuts[sh], play="three-nba",
      remap=[[0, 0.0], [d, 0.6]], camera=[key(0, ARCS), key(t_same, ARCS), key(d, ARCS_FEET, "inOut")],
      ov3=[{"type": "arc3", "rules": "nba", "color": NBA_C, "width": 0.14, "draw": 0.6, "z": 0.014, "from": t_nba, "to": d, "fout": 0},
           {"type": "measure", "end": [0.0, round(BASKET_Y + 7.24, 3)], "color": NBA_C, "width": 0.08, "draw": 0.45, "from": t_nba + 0.2, "to": t_el, "fout": 0.15},
           {"type": "arc3", "rules": "fiba", "color": EL_C, "width": 0.14, "draw": 0.6, "z": 0.016, "from": t_el, "to": d, "fout": 0},
           {"type": "measure", "end": [0.0, round(BASKET_Y + 6.75, 3)], "color": EL_C, "width": 0.08, "draw": 0.45, "from": t_el + 0.2, "to": t_same, "fout": 0.15},
           {"type": "measure", "end": SPOT, "color": WHITE, "width": 0.08, "draw": 0.45, "from": t_same, "to": d, "fout": 0},
           {"type": "footRing", "player": "O1", "foot": "L", "color": GOLD, "r": 0.42, "from": t_same + 0.2, "to": d, "fout": 0}],
      screen=[{"type": "section", "n": "02", "text": "THREE-POINT LINE", "y": 200, "from": 0.05, "to": d},
              {"type": "league", "league": "nba", "y": 330, "from": t_nba, "to": t_el, "size": 58},
              {"type": "score", "text": "7.24 m", "sub": "TOP OF THE ARC · CORNERS 6.71 m", "y": 450, "size": 150, "from": t_nba + 0.25, "to": t_el},
              {"type": "league", "league": "el", "y": 330, "from": t_el, "to": t_same, "size": 58},
              {"type": "score", "text": "6.75 m", "sub": "TOP OF THE ARC · CORNERS 6.60 m", "y": 450, "size": 150, "from": t_el + 0.25, "to": t_same},
              {"type": "chip", "text": "SAME SPOT → 7 m", "tone": "gold", "align": "center", "size": 60, "from": t_same + 0.1, "to": d, "y": 330}])
    rel, make = PL["three-el"]["marks"]["release"], PL["three-el"]["marks"]["make"]
    for sh, pid, lg, word_line, word, val, sub, c, r in (
            ("el3", "three-el", "el", "a6", "THREE", "+3", "OUTSIDE 6.75 m", EL_C, "fiba"),
            ("nba2", "three-nba", "nba", "a8", "TWO", "+2", "INSIDE 7.24 m", NBA_C, "nba")):
        d = dur[sh]
        t_w = L(ws(word_line, word), sh)
        # the whole shooting motion is on screen (from 0.3 s before the release) and the ball drops through the rim during
        # the number word; real speed when the word leaves time for it, else at most 1.1x
        need = make - (rel - 0.3)
        if t_w >= need:
            t_mk, p0, spd = t_w, make - t_w, 1.0
        else:
            spd = 1.1
            t_mk, p0 = need / spd, rel - 0.3
        t_w = round(t_mk, 3)
        S(id=sh, name=f"{lg.upper()}: the same 7 m shot = {val} (speed {spd})", at=cuts[sh], play=pid,
          remap=[[0, round(p0, 3)], [t_w, make], [d, min(PL[pid]["duration"], make + (d - t_w))]], camera=[key(0, SHOT)],
          ov3=[{"type": "arc3", "rules": r, "color": c, "width": 0.13, "z": 0.014, "from": 0.0, "to": d, "fin": 0},
               {"type": "footRing", "player": "O1", "foot": "L", "color": GOLD, "r": 0.42, "from": 0.0, "to": max(0.1, t_w - (make - rel) + 0.05), "fin": 0},
               {"type": "ballTrail", "len": 0.35, "from": max(0.0, t_w - (make - rel)), "to": t_w + 0.1}],
          screen=[{"type": "whip", "amount": 0.7, "dir": -1 if lg == "el" else 1, "from": 0.0, "to": 0.2},
                  {"type": "league", "league": lg, "y": 200, "from": 0.0, "to": d, "size": 66},
                  {"type": "score", "text": val, "sub": sub, "y": 600, "size": 220, "from": t_w, "to": d}])

    # ------------------------------------------------------------------ 03 FOUL OUT: one player's personal fouls
    sh = "foulEL"
    d = dur[sh]
    t5 = L(ws("f2", "FIVE"), sh)
    ticks = [round(t5 - 0.6 + 0.15 * i, 3) for i in range(5)]
    grab = 1.05
    S(id=sh, name="03 FOUL OUT: EuroLeague, the 5th personal foul", at=cuts[sh], play="foul-el",
      remap=[[0, max(0.0, grab - (ticks[0] - 0.05))], [ticks[0] - 0.05, grab], [d, min(1.98, grab + (d - ticks[0]) * 0.8)]], camera=[key(0, FOUL_A)],
      ov3=[{"type": "handRing", "player": "X1", "hand": 0, "from": ticks[0], "to": d}],
      screen=[{"type": "section", "n": "03", "text": "FOUL OUT", "y": 200, "from": 0.05, "to": d},
              {"type": "fouls", "league": "el", "max": 5, "ticks": ticks, "out": L(s0("f3"), sh), "y": 330, "from": 0.15, "to": d}])
    sh = "walk"
    d = dur[sh]
    off = cuts["walk"] - cuts["foulEL"]
    S(id=sh, name="EuroLeague: 5 fouls = the player leaves the game (walks to the bench)", at=cuts[sh], play="walkoff",
      remap=[[0, 0.1], [d, 0.1 + d]], camera=[key(0, WALK)],
      ov3=[{"type": "footRing", "player": "X1", "foot": "L", "color": RED, "r": 0.4, "from": 0.0, "to": d, "fin": 0}],
      screen=[{"type": "section", "n": "03", "text": "FOUL OUT", "y": 200, "from": -off, "to": d},
              {"type": "fouls", "league": "el", "max": 5, "ticks": [round(x - off, 3) for x in ticks], "out": 0.0, "y": 330, "from": -off, "to": d}])
    sh = "foulNBA"
    d = dur[sh]
    t6 = L(ws("f5", "SIX"), sh)
    ticks6 = [round(0.12 + 0.1 * i, 3) for i in range(5)] + [t6]
    S(id=sh, name="NBA: the 6th personal foul = disqualified", at=cuts[sh], play="foul-nba",
      remap=[[0, max(0.0, grab - t6 + 0.05)], [t6 - 0.05, grab], [d, min(1.98, grab + (d - t6) * 0.8)]], camera=[key(0, FOUL_A)],
      ov3=[{"type": "handRing", "player": "X1", "hand": 0, "from": t6 - 0.05, "to": d}],
      screen=[{"type": "whip", "amount": 0.7, "dir": 1, "from": 0.0, "to": 0.2},
              {"type": "section", "n": "03", "text": "FOUL OUT", "y": 200, "from": 0.0, "to": d},
              {"type": "fouls", "league": "nba", "max": 6, "ticks": ticks6, "out": t6 + 0.05, "y": 330, "from": 0.0, "to": d}])

    # ------------------------------------------------------------------ 04 DEFENSIVE 3 SECONDS (the big one)
    sh = "d3s"
    d = dur[sh]
    t_title, t_nba = L(s0("d2"), sh), L(s0("d3"), sh)
    t_guard = L(ws("d3", "without"), sh)
    c1, c2, c3 = (L(ws("d4", w), sh) for w in ("One", "two", "three"))
    t_tech = L(s0("d5"), sh)
    # play clock: the count starts at 'One' = play mark count0 (1.0 s); real speed after the title
    p_one = PL["d3s-nba"]["marks"]["count0"]
    S(id=sh, name="04 DEFENSIVE 3 SECONDS (NBA): offence in control, X5 in the lane guarding nobody, 1-2-3, technical foul", at=cuts[sh], play="d3s-nba",
      # game clock: one second of play per spoken count ("One" = 1 s in the lane ... the technical at 3.1 s)
      remap=[[0, max(0.0, p_one - c1 * 0.3)], [c1, p_one], [c2, p_one + 1.0], [c3, p_one + 2.0], [t_tech, p_one + 3.1], [d, p_one + 3.1]],
      camera=[key(0, D3S), key(d, orb([0.06, 5.4, 0.0], 21.5, 38, 0, 44))],
      ov3=[{"type": "lane", "rules": "nba", "color": RED, "opacity": 0.16, "from": t_title, "to": d, "fin": 0.25, "fout": 0},
           {"type": "footRing", "player": "X5", "foot": "L", "color": WHITE, "r": 1.15, "from": t_guard, "to": c1, "fout": 0.15},
           {"type": "footRing", "player": "X5", "foot": "L", "color": RED, "r": 0.5, "from": c1, "to": d, "fin": 0.12, "fout": 0}],
      screen=[{"type": "section", "n": "04", "text": "THE BIG ONE", "y": 200, "from": 0.05, "to": t_title},
              {"type": "title", "lines": ["DEFENSIVE", "3 SECONDS"], "gold": [1], "from": t_title, "to": t_nba + 0.6, "y": 200, "size": 104},
              {"type": "league", "league": "nba", "y": 170, "from": t_nba + 0.6, "to": d, "size": 62},
              {"type": "chip", "text": "BALL IN THE FRONTCOURT", "tone": "gold", "align": "center", "size": 48, "from": t_nba + 0.6, "to": t_guard, "y": 300},
              {"type": "chip", "text": "NOT GUARDING ANYONE", "tone": "red", "align": "center", "size": 54, "from": t_guard, "to": c1, "y": 300},
              {"type": "micro", "text": "NOBODY WITHIN ARM'S LENGTH", "y": 390, "from": t_guard + 0.2, "to": c1},
              {"type": "count3", "ticks": [c1, c2, c3], "from": c1, "to": t_tech, "y": 290, "size": 200},
              {"type": "freeze", "from": t_tech, "to": d},
              {"type": "verdict", "text": "DEFENSIVE 3 SECONDS", "tone": "red", "y": 300, "from": t_tech, "to": d, "size": 60},
              {"type": "micro", "text": "TECHNICAL FOUL · 1 FREE THROW · BALL KEPT", "y": 410, "from": t_tech + 0.25, "to": d}])
    sh = "d3sEL"
    d = dur[sh]
    t_no, t_big = L(s0("d7"), sh), L(s0("d8"), sh)
    p0 = p_one + 0.2
    S(id=sh, name="EuroLeague: the same picture, no defensive 3-second rule; the big can stay and protect the rim", at=cuts[sh], play="d3s-el",
      remap=[[0, p0], [d, min(PL["d3s-el"]["duration"], p0 + d)]], camera=[key(0, D3S), key(t_big, D3S), key(d, orb([0.0, 3.2, 0.3], 9.6, 40, 0, 42), "inOut")],
      ov3=[{"type": "lane", "rules": "fiba", "color": GREEN, "opacity": 0.14, "from": 0.0, "to": d, "fin": 0.2, "fout": 0},
           {"type": "footRing", "player": "X5", "foot": "L", "color": GREEN, "r": 0.5, "from": 0.0, "to": d, "fin": 0.12, "fout": 0}],
      screen=[{"type": "whip", "amount": 0.7, "dir": -1, "from": 0.0, "to": 0.2},
              {"type": "league", "league": "el", "y": 170, "from": 0.0, "to": d, "size": 62},
              {"type": "verdict", "text": "NO DEFENSIVE 3-SECOND RULE", "tone": "green", "y": 300, "from": t_no, "to": d, "size": 52},
              {"type": "chip", "text": "CAN STAY → PROTECT THE RIM", "tone": "gold", "align": "center", "size": 52, "from": t_big, "to": d, "y": 410},
              {"type": "micro", "text": "OFFENSIVE 3 SECONDS STILL APPLIES", "y": 510, "from": t_big + 0.3, "to": d}])

    # ------------------------------------------------------------------ CLOSE: both courts, the question
    sh = "end"
    d = dur[sh]
    S(id=sh, name="CLOSE: NBA court on top, EuroLeague court below, Which rules do you prefer?", at=cuts[sh], play="d3s-nba",
      remap=[[0, 2.0], [d, 2.0 + d]], camera=[key(0, orb([0.0, 5.0, 0.0], 15.5, 44, 0, 40))],
      split={"play": "d3s-el", "remap": [[0, 2.0], [d, 2.0 + d]], "camera": [key(0, orb([0.0, 5.0, 0.0], 15.5, 44, 0, 40))], "ratio": 0.5},
      screen=[{"type": "league", "league": "nba", "y": 70, "from": 0.0, "to": d, "size": 56, "align": "left"},
              {"type": "league", "league": "el", "y": 1000, "from": 0.0, "to": d, "size": 56, "align": "left"},
              {"type": "title", "lines": ["WHICH RULES", "DO YOU PREFER?"], "gold": [1], "from": 0.05, "to": d, "y": 640, "size": 104, "noOut": True},
              {"type": "logo", "big": False, "from": 0.2, "to": d}])

    groups = []
    for k, seg in W.items():
        n = len(seg)
        while n > 6:
            groups.append(4)
            n -= 4
        groups.append(n)
    ep = {
        "id": "nbaeu-trial" if trial else "nbaeu", "title": "NBA VS EUROLEAGUE: 4 RULES THAT CHANGE THE GAME", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33", "words": words, "subtitleGroups": groups, "subtitleBlock": True, "subtitleY": 1390,
        "subtitleHide": [[round(cuts["end"], 3), t_end]],
        "keywords": ["NBA", "EuroLeague", "EuroLeague!", "EuroLeague?", "GAME", "TIME.", "twelve", "FORTY-EIGHT!", "ten...", "FORTY!", "THREE-POINT",
                     "THREE!", "TWO!", "FIVE!", "SIX!", "FOUL", "OUT.", "BIG", "DEFENSIVE", "SECONDS.", "TECHNICAL", "FOUL!", "No", "rim."],
        "gradeBottom": 0.3, "shots": shots, "plays": {k: PL[k] for k in IDS},
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    return {"episode": ep}, {"duration": t_end, "cuts": {k: round(v, 3) for k, v in cuts.items()}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words")
    ap.add_argument("--placeholder", action="store_true")
    ap.add_argument("--voice", default="tactical/realism-v3-3/silence.mp3")
    ap.add_argument("--music")
    ap.add_argument("--trial", action="store_true")
    a = ap.parse_args()
    words = placeholder_words() if a.placeholder else json.load(open(a.words))
    props, meta = build(words, a.voice, a.music, a.trial)
    json.dump(props, open(a.out, "w"))
    print(json.dumps(meta))
