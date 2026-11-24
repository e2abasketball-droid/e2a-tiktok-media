#!/usr/bin/env python3
"""E2A - NBA VS EUROLEAGUE V2 (owner brief 2026-11-24 22:19 Madrid): same 3D scenes as V1 (tactical/episodes/_gen-nbaeu.py,
kept untouched), rebuilt around a conversational narration (Deuce take B, one continuous eleven_v3 take):
  * E2A League Comparison Intro: NBA court on top, EuroLeague court below, the official league logos on white plates
    (public/leagues/nba.svg|png, public/leagues/euroleague.svg|png; when a file is missing a marked PLACEHOLDER is drawn)
  * E2A Broadcast Scoreboard: two original broadcast-style boards, Q1 12:00 (NBA) and Q1 10:00 (EuroLeague), before the
    tip (empty courts, no live ball = clocks honestly stopped), same scale, only the two game clocks are highlighted.
    NO total game time anywhere (script, subtitles, graphics).
  * the voice explains, the graphics carry the numbers.
  python3 tactical/episodes/_gen-nbaeu-v2.py --words W.json --voice nbaeu-v2/voice.wav --music nbaeu-v2/music.mp3 --out props.json
  --placeholder   synthesise word timings from the script (preview before the narration exists)"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
IDS = ["three-el", "three-nba", "foul-el", "foul-nba", "walkoff", "d3s-nba", "d3s-el", "empty-nba", "empty-el"]
PL = {k: json.load(open(os.path.join(T, "tactical", "plays", f"nbaeu-{k}.json"))) for k in IDS}
GOLD, NAVY, WHITE, RED, GREEN = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A", "#2FBF71"
NBA_C, EL_C = "#4F8BFF", "#FF9A3C"
BASKET_Y = 1.575
SPOT = PL["three-el"]["tracks"]["O1"][0][1:]


def logo_file(name):
    for ext in ("svg", "png"):
        if os.path.exists(os.path.join(T, "public", "leagues", f"{name}.{ext}")):
            return f"leagues/{name}.{ext}"
    return None


LOGO = {"nba": logo_file("nba"), "el": logo_file("euroleague")}
# plates sized to the real artwork proportions (Wikimedia Commons metadata, 2026-11-24): NBA 915 x 2079 (0.44:1, tall),
# EuroLeague 960 x 219 (4.38:1, wide). The files are NOT in the project: no licence confirmed for commercial use.

LINES = [
    ("o1", "NBA and EuroLeague look pretty similar."),
    ("o2", "But the rules can change the game."),
    ("o3", "Watch this."),
    ("q1", "In the NBA, each quarter lasts twelve minutes."),
    ("q2", "In EuroLeague, it's ten."),
    ("a1", "Now check this shot."),
    ("a2", "From the exact same spot, it's a three in EuroLeague..."),
    ("a3", "but only two in the NBA."),
    ("a4", "Different arc."),
    ("f1", "Fouls?"),
    ("f2", "Five and you're out in EuroLeague."),
    ("f3", "In the NBA, it's six."),
    ("d1", "And this one actually changes defense."),
    ("d2", "In the NBA, you can't just camp in the paint for more than three seconds without actively guarding anyone."),
    ("d3", "That's defensive three seconds."),
    ("d4", "EuroLeague doesn't have that violation, so bigs can protect the rim differently."),
    ("e1", "Which rules would you rather play under?"),
]
norm = lambda s: "".join(c for c in s.lower() if c.isalnum())
FORBIDDEN = ["48", "40 min", "forty", "total", "per game", "game length"]   # no total game time, anywhere


def placeholder_words():
    out, t = [], 0.15
    for _, text in LINES:
        for w in text.split():
            d = 0.18 + 0.03 * len(norm(w))
            out.append({"text": w, "start": round(t, 3), "end": round(t + d, 3)})
            t += d + 0.04
            if w[-1] in "?!.":
                t += 0.3
    return out


def line_words(words):
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

# cameras (V1, frame-fit checked) + V2 intro / scoreboard backgrounds
ARCS = orb([0.0, 7.0, 0.0], 13.5, 26, 0, 40)
ARCS_FEET = orb([0.0, 8.5, 0.1], 6.8, 24, 0, 38)
SHOT = orb([0.0, 6.8, 1.0], 16.0, 50, 0, 42)
FOUL_A = orb({"follow": ["O1", "X1"], "z": 0.6, "window": 0.5}, 8.4, 62, -60, 40)
WALK = orb({"follow": ["X1"], "z": 0.8, "window": 0.6}, 9.0, 60, -75, 42)
D3S = orb([0.06, 5.5, 0.0], 22.5, 38, 0, 44)
HALF_A = orb([0.0, 5.0, 0.0], 17.0, 44, 0, 40)        # split halves: short push-in (no spin)
HALF_B = orb([0.0, 5.0, 0.0], 15.5, 44, 0, 40)
BOARD_A = orb([0.0, 6.0, 0.0], 24.0, 50, 6, 44)        # empty court behind the scoreboards, slow drift
BOARD_B = orb([0.0, 6.0, 0.0], 22.0, 48, 0, 44)
TEAMS = [{"name": "NAVY", "color": NAVY, "score": 0}, {"name": "WHITE", "color": "#F2F2F2", "score": 0}]


def build(words, voice, music):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, t: next(w for w in W[k] if norm(w["text"]).startswith(norm(t)))
    ws = lambda k, t: wd(k, t)["start"]
    t_end = round(e0("e1") + 1.15, 3)
    rel, make = PL["three-el"]["marks"]["release"], PL["three-el"]["marks"]["make"]
    lead = make - (rel - 0.3)                      # whole shooting motion before the number word (EuroLeague shot)
    MID = 0.8                                      # NBA shot = the same shot again, picked up in flight (ball 0.8 s from the rim)
    cuts = {"intro": 0.0, "qNBA": s0("q1") - 0.1, "qEL": s0("q2") - 0.08, "arcs": s0("a1") - 0.1,
            "el3": min(ws("a2", "it's") - 0.08, ws("a2", "three") - lead / 1.1), "nba2": ws("a3", "two") - MID,
            "arcsB": s0("a4") - 0.08, "foulEL": s0("f1") - 0.1}
    t_out = ws("f2", "out")
    if s0("f3") - (t_out + 0.35) >= 0.9:
        cuts["walk"] = t_out + 0.35
    cuts.update({"foulNBA": s0("f3") - 0.08, "d3s": s0("d1") - 0.1, "d3sEL": s0("d4") - 0.08, "end": s0("e1") - 0.08})
    order = list(cuts)
    dur = {k: round((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k], 3) for i, k in enumerate(order)}
    L = lambda t, sh: round(t - cuts[sh], 3)
    shots = []
    S = lambda **kw: shots.append(kw)

    # ------------------------------------------------------------------ E2A LEAGUE COMPARISON INTRO (0 - ~5.5 s)
    sh = "intro"
    d = dur[sh]
    t_r = L(s0("o2"), sh)
    S(id=sh, name="INTRO: NBA court on top, EuroLeague court below, official logos (or marked placeholders), arcs traced on 'rules'", at=0.0, play="d3s-nba",
      remap=[[0, 0.4], [d, 0.4 + d * 0.5]], camera=[key(0, HALF_A), key(d, HALF_B, "inOut")],
      ov3=[{"type": "arc3", "rules": "nba", "color": NBA_C, "width": 0.13, "draw": 0.6, "z": 0.014, "from": t_r, "to": d, "fout": 0}],
      split={"play": "d3s-el", "remap": [[0, 0.4], [d, 0.4 + d * 0.5]], "camera": [key(0, HALF_A), key(d, HALF_B, "inOut")], "ratio": 0.5, "seam": "brand",
             "ov3": [{"type": "arc3", "rules": "fiba", "color": EL_C, "width": 0.13, "draw": 0.6, "z": 0.014, "from": t_r + 0.15, "to": d, "fout": 0}]},
      screen=[{"type": "leagueLogo", "league": "nba", "src": LOGO["nba"], "y": 40, "w": 220, "h": 330, "from": 0.0, "to": d, "delay": max(0.0, L(ws("o1", "NBA"), sh) - 0.05)},
              {"type": "leagueLogo", "league": "el", "src": LOGO["el"], "y": 1040, "w": 600, "h": 180, "from": 0.0, "to": d, "delay": L(ws("o1", "EuroLeague"), sh)}])

    # ------------------------------------------------------------------ 01 QUARTER LENGTH: E2A Broadcast Scoreboard
    sh = "qNBA"
    d = dur[sh]
    off = cuts["qEL"] - cuts["qNBA"]
    t_hl = L(ws("q2", "ten") + 0.2, "qEL")
    board = lambda lg, clock, y, t0, sh_: {"type": "scoreboard", "league": lg, "logo": LOGO[lg], "teams": TEAMS, "period": "Q1", "clock": clock,
                                          "shot": 24, "highlight": round(t_hl + (cuts["qEL"] - cuts[sh_]), 3), "y": y, "from": t0, "to": 99}
    S(id=sh, name="QUARTER LENGTH: NBA board Q1 12:00 (before the tip, empty NBA court)", at=cuts[sh], play="empty-nba", hide=["R"],
      remap=[[0, 0.0], [d, d]], camera=[key(0, BOARD_A), key(d + dur["qEL"], BOARD_B)],
      screen=[{"type": "scrim", "opacity": 0.5, "from": 0, "to": d},
              {"type": "section", "n": "01", "text": "QUARTER LENGTH", "y": 300, "from": 0.05, "to": d},
              {**board("nba", "12:00", 600, 0.1, sh), "to": d}])
    sh = "qEL"
    d = dur[sh]
    S(id=sh, name="QUARTER LENGTH: EuroLeague board Q1 10:00 under it (court switches to EuroLeague), both clocks highlighted", at=cuts[sh], play="empty-el", hide=["R"],
      remap=[[0, off], [d, off + d]], camera=[key(-off, BOARD_A), key(d, BOARD_B)],
      screen=[{"type": "scrim", "opacity": 0.5, "from": -off, "to": d},
              {"type": "section", "n": "01", "text": "QUARTER LENGTH", "y": 300, "from": -off, "to": d},
              {**board("nba", "12:00", 600, round(0.1 - off, 3), "qEL"), "to": d},
              {**board("el", "10:00", 820, 0.05, "qEL"), "to": d},
              {"type": "chip", "text": "MINUTES PER QUARTER", "tone": "gold", "align": "center", "size": 46, "from": t_hl + 0.1, "to": d, "y": 1060}])

    # ------------------------------------------------------------------ 02 THREE-POINT LINE (V1 scenes)
    sh = "arcs"
    d = dur[sh]
    t_same = L(s0("a2"), sh)
    S(id=sh, name="02 THREE-POINT LINE: both real arcs, the shooter's spot", at=cuts[sh], play="three-nba",
      remap=[[0, 0.0], [d, 0.4]], camera=[key(0, ARCS), key(d, orb([0.0, 7.4, 0.05], 12.0, 26, 0, 40))],
      ov3=[{"type": "arc3", "rules": "nba", "color": NBA_C, "width": 0.14, "draw": 0.5, "z": 0.014, "from": 0.1, "to": d, "fout": 0},
           {"type": "arc3", "rules": "fiba", "color": EL_C, "width": 0.14, "draw": 0.5, "z": 0.016, "from": 0.35, "to": d, "fout": 0},
           {"type": "footRing", "player": "O1", "foot": "L", "color": GOLD, "r": 0.42, "from": 0.2, "to": d, "fout": 0},
           {"type": "measure", "end": SPOT, "color": WHITE, "width": 0.08, "draw": 0.4, "from": max(0.5, t_same - 0.1), "to": d, "fout": 0}],
      screen=[{"type": "section", "n": "02", "text": "THREE-POINT LINE", "y": 200, "from": 0.05, "to": d},
              {"type": "chip", "text": "SAME SPOT → 7 m", "tone": "gold", "align": "center", "size": 60, "from": max(0.5, t_same), "to": d, "y": 330}])
    for sh, pid, lg, line, word, val, sub, c, r in (
            ("el3", "three-el", "el", "a2", "three", "+3", "OUTSIDE 6.75 m", EL_C, "fiba"),
            ("nba2", "three-nba", "nba", "a3", "two", "+2", "INSIDE 7.24 m", NBA_C, "nba")):
        d = dur[sh]
        t_w = L(ws(line, word), sh)
        if sh == "nba2":
            t_mk, p0, spd = t_w, make - t_w, 1.0
        elif t_w >= lead:
            t_mk, p0, spd = t_w, make - t_w, 1.0
        else:
            spd = min(1.1, lead / max(t_w, 0.01))
            t_mk, p0 = lead / spd, rel - 0.3
        t_w = round(t_mk, 3)
        S(id=sh, name=f"{lg.upper()}: the same 7 m shot = {val} (speed {spd:.2f})", at=cuts[sh], play=pid,
          remap=[[0, round(p0, 3)], [t_w, make], [d, min(PL[pid]["duration"], make + (d - t_w))]], camera=[key(0, SHOT)],
          ov3=[{"type": "arc3", "rules": r, "color": c, "width": 0.13, "z": 0.014, "from": 0.0, "to": d, "fin": 0},
               {"type": "footRing", "player": "O1", "foot": "L", "color": GOLD, "r": 0.42, "from": 0.0, "to": max(0.1, t_w - (make - rel) + 0.05), "fin": 0},
               {"type": "ballTrail", "len": 0.35, "from": max(0.0, t_w - (make - rel)), "to": t_w + 0.1}],
          screen=[{"type": "whip", "amount": 0.6, "dir": -1 if lg == "el" else 1, "from": 0.0, "to": 0.2},
                  {"type": "league", "league": lg, "y": 200, "from": 0.0, "to": d, "size": 66},
                  {"type": "score", "text": val, "sub": sub, "y": 600, "size": 220, "from": t_w, "to": d}]
          + ([{"type": "chip", "text": "SAME SPOT → 7 m", "tone": "gold", "align": "center", "size": 60, "from": 0.0, "to": round(max(0.3, t_w - (make - rel)), 3), "y": 330, "fin": 0}] if sh == "el3" else []))
    sh = "arcsB"
    d = dur[sh]
    S(id=sh, name="Different arc: both arcs measured from the basket centre (NBA 7.24 m / corners 6.71, FIBA 6.75 m / corners 6.60)", at=cuts[sh], play="three-el",
      remap=[[0, 3.4], [d, 3.4]], camera=[key(0, orb([0.0, 6.6, 0.0], 14.5, 30, 0, 42))],
      ov3=[{"type": "arc3", "rules": "nba", "color": NBA_C, "width": 0.14, "z": 0.014, "from": 0.0, "to": d, "fin": 0.1, "fout": 0},
           {"type": "arc3", "rules": "fiba", "color": EL_C, "width": 0.14, "z": 0.016, "from": 0.0, "to": d, "fin": 0.1, "fout": 0},
           {"type": "measure", "end": [0.35, round(BASKET_Y + 7.24, 3)], "color": NBA_C, "width": 0.08, "draw": 0.4, "from": 0.1, "to": d, "fout": 0},
           {"type": "measure", "end": [-0.35, round(BASKET_Y + 6.75, 3)], "color": EL_C, "width": 0.08, "draw": 0.4, "from": 0.2, "to": d, "fout": 0}],
      screen=[{"type": "section", "n": "02", "text": "THREE-POINT LINE", "y": 200, "from": 0.0, "to": d},
              {"type": "league", "league": "nba", "y": 330, "from": 0.1, "to": d, "size": 50, "align": "left"},
              {"type": "score", "text": "7.24 m", "sub": "CORNERS 6.71 m", "y": 410, "size": 120, "from": 0.15, "to": d},
              {"type": "league", "league": "el", "y": 640, "from": 0.25, "to": d, "size": 50, "align": "left"},
              {"type": "score", "text": "6.75 m", "sub": "CORNERS 6.60 m", "y": 720, "size": 120, "from": 0.3, "to": d}])

    # ------------------------------------------------------------------ 03 PERSONAL FOULS (V1 scenes, faster)
    sh = "foulEL"
    d = dur[sh]
    t5 = L(ws("f2", "Five"), sh)
    ticks = [round(max(0.2, t5 - 0.6) + (min(0.6, t5 - 0.2) / 4) * i, 3) for i in range(4)] + [round(t5, 3)]
    grab = 1.05
    S(id=sh, name="03 PERSONAL FOULS: EuroLeague, 5th foul = out", at=cuts[sh], play="foul-el",
      remap=[[0, max(0.0, grab - (ticks[0] - 0.05))], [ticks[0] - 0.05, grab], [d, min(1.98, grab + (d - ticks[0]) * 0.8)]], camera=[key(0, FOUL_A)],
      ov3=[{"type": "handRing", "player": "X1", "hand": 0, "from": ticks[0], "to": d}],
      screen=[{"type": "section", "n": "03", "text": "PERSONAL FOULS", "y": 200, "from": 0.05, "to": d},
              {"type": "fouls", "league": "el", "max": 5, "ticks": ticks, "out": L(t_out, sh), "y": 330, "from": 0.1, "to": d}])
    if "walk" in cuts:
        sh = "walk"
        d = dur[sh]
        off = cuts["walk"] - cuts["foulEL"]
        S(id=sh, name="EuroLeague: fouled out, walks to the bench", at=cuts[sh], play="walkoff",
          remap=[[0, 0.1], [d, 0.1 + d]], camera=[key(0, WALK)],
          ov3=[{"type": "footRing", "player": "X1", "foot": "L", "color": RED, "r": 0.4, "from": 0.0, "to": d, "fin": 0}],
          screen=[{"type": "section", "n": "03", "text": "PERSONAL FOULS", "y": 200, "from": -off, "to": d},
                  {"type": "fouls", "league": "el", "max": 5, "ticks": [round(x - off, 3) for x in ticks], "out": 0.0, "y": 330, "from": -off, "to": d}])
    sh = "foulNBA"
    d = dur[sh]
    t6 = L(ws("f3", "six"), sh)
    ticks6 = [round(0.12 + min(0.1, (t6 - 0.3) / 5) * i, 3) for i in range(5)] + [t6]
    S(id=sh, name="NBA: 6th personal foul = fouled out", at=cuts[sh], play="foul-nba",
      remap=[[0, max(0.0, grab - t6 + 0.05)], [t6 - 0.05, grab], [d, min(1.98, grab + (d - t6) * 0.8)]], camera=[key(0, FOUL_A)],
      ov3=[{"type": "handRing", "player": "X1", "hand": 0, "from": t6 - 0.05, "to": d}],
      screen=[{"type": "whip", "amount": 0.6, "dir": 1, "from": 0.0, "to": 0.2},
              {"type": "section", "n": "03", "text": "PERSONAL FOULS", "y": 200, "from": 0.0, "to": d},
              {"type": "fouls", "league": "nba", "max": 6, "ticks": ticks6, "out": t6 + 0.05, "y": 330, "from": 0.0, "to": d}])

    # ------------------------------------------------------------------ 04 DEFENSIVE 3 SECONDS (V1 5 v 5, real game clock)
    sh = "d3s"
    d = dur[sh]
    t_expl, t_tech = L(s0("d2"), sh), L(s0("d3"), sh)
    c1 = round(t_tech - 3.1, 3)
    c2, c3 = round(c1 + 1.0, 3), round(c1 + 2.0, 3)
    p_one = PL["d3s-nba"]["marks"]["count0"]
    P1 = round(min(PL["d3s-nba"]["duration"] - 3.15, max(p_one, c1)), 3)
    scr = [{"type": "title", "lines": ["DEFENSIVE", "3 SECONDS"], "gold": [1], "from": 0.05, "to": t_expl + 0.3, "y": 200, "size": 104},
           {"type": "league", "league": "nba", "y": 170, "from": t_expl + 0.3, "to": d, "size": 62}]
    if c1 - (t_expl + 0.3) >= 0.9:
        scr.append({"type": "chip", "text": "BALL IN THE FRONTCOURT", "tone": "gold", "align": "center", "size": 48, "from": t_expl + 0.3, "to": c1, "y": 300})
    scr += [{"type": "count3", "ticks": [c1, c2, c3], "from": c1, "to": t_tech, "y": 290, "size": 200},
            {"type": "micro", "text": "IN THE LANE · NOT GUARDING ANYONE", "y": 600, "from": c1 + 0.1, "to": t_tech},
            {"type": "freeze", "from": t_tech, "to": d},
            {"type": "verdict", "text": "DEFENSIVE 3 SECONDS", "tone": "red", "y": 300, "from": t_tech, "to": d, "size": 60},
            {"type": "micro", "text": "TECHNICAL FOUL · 1 FREE THROW · BALL KEPT", "y": 410, "from": t_tech + 0.25, "to": d}]
    S(id=sh, name="04 DEFENSIVE 3 SECONDS (NBA): offence in control, X5 in the lane guarding nobody, 1 s per count, technical at 3.1 s", at=cuts[sh], play="d3s-nba",
      # any 3.1 s window of the play is legal (qc-nbaeu: X5 in the lane, nobody within 1.2 m, O1 in control for the whole
      # play); the count runs at real speed, the approach before it at the speed that fits
      remap=[[0, 0.0], [c1, P1], [t_tech, P1 + 3.1], [d, P1 + 3.1]],
      camera=[key(0, D3S), key(d, orb([0.06, 5.4, 0.0], 21.5, 38, 0, 44))],
      ov3=[{"type": "lane", "rules": "nba", "color": RED, "opacity": 0.16, "from": 0.1, "to": d, "fin": 0.25, "fout": 0},
           {"type": "footRing", "player": "X5", "foot": "L", "color": WHITE, "r": 1.15, "from": t_expl + 0.3, "to": c1, "fout": 0.15},
           {"type": "footRing", "player": "X5", "foot": "L", "color": RED, "r": 0.5, "from": c1, "to": d, "fin": 0.12, "fout": 0}],
      screen=scr)
    sh = "d3sEL"
    d = dur[sh]
    t_big = L(ws("d4", "bigs"), sh)
    p0 = p_one + 0.2
    S(id=sh, name="EuroLeague: no defensive 3-second rule; bigs can protect the rim", at=cuts[sh], play="d3s-el",
      remap=[[0, p0], [d, min(PL["d3s-el"]["duration"], p0 + d)]], camera=[key(0, D3S), key(t_big, D3S), key(d, orb([0.0, 3.2, 0.3], 9.6, 40, 0, 42), "inOut")],
      ov3=[{"type": "lane", "rules": "fiba", "color": GREEN, "opacity": 0.14, "from": 0.0, "to": d, "fin": 0.2, "fout": 0},
           {"type": "footRing", "player": "X5", "foot": "L", "color": GREEN, "r": 0.5, "from": 0.0, "to": d, "fin": 0.12, "fout": 0}],
      screen=[{"type": "whip", "amount": 0.6, "dir": -1, "from": 0.0, "to": 0.2},
              {"type": "league", "league": "el", "y": 170, "from": 0.0, "to": d, "size": 62},
              {"type": "verdict", "text": "NO DEFENSIVE 3-SECOND RULE", "tone": "green", "y": 300, "from": 0.25, "to": d, "size": 52},
              {"type": "chip", "text": "BIGS CAN STAY → PROTECT THE RIM", "tone": "gold", "align": "center", "size": 50, "from": t_big, "to": d, "y": 410},
              {"type": "micro", "text": "OFFENSIVE 3 SECONDS STILL APPLIES", "y": 510, "from": t_big + 0.3, "to": d}])

    # ------------------------------------------------------------------ CLOSE: both leagues, the question
    sh = "end"
    d = dur[sh]
    S(id=sh, name="CLOSE: NBA top / EuroLeague bottom, Which rules would you rather play under?", at=cuts[sh], play="d3s-nba",
      remap=[[0, 2.0], [d, 2.0 + d]], camera=[key(0, HALF_B)],
      split={"play": "d3s-el", "remap": [[0, 2.0], [d, 2.0 + d]], "camera": [key(0, HALF_B)], "ratio": 0.5, "seam": "brand"},
      screen=[{"type": "leagueLogo", "league": "nba", "src": LOGO["nba"], "y": 40, "w": 120, "h": 180, "from": 0.0, "to": d, "align": "left"},
              {"type": "leagueLogo", "league": "el", "src": LOGO["el"], "y": 1000, "w": 320, "h": 100, "from": 0.0, "to": d, "align": "left"},
              {"type": "title", "lines": ["WHICH RULES", "WOULD YOU", "PLAY UNDER?"], "gold": [1, 2], "from": 0.05, "to": d, "y": 560, "size": 96, "noOut": True},
              {"type": "logo", "big": False, "from": 0.2, "to": d}])

    groups = []
    for k, seg in W.items():
        n = len(seg)
        while n > 6:
            groups.append(4)
            n -= 4
        groups.append(n)
    ep = {
        "id": "nbaeu-v2", "title": "NBA VS EUROLEAGUE V2", "fps": 30, "voice": voice, "tail": round(t_end - words[-1]["end"], 3),
        "autoSfx": False, "pinV2": True, "env": "cinema", "athleteRenderer": "v33", "words": words, "subtitleGroups": groups,
        "subtitleBlock": True, "subtitleY": 1390, "subtitleHide": [[0.0, round(cuts["qNBA"], 3)], [round(cuts["end"], 3), t_end]],
        "keywords": ["NBA", "NBA,", "NBA.", "EuroLeague", "EuroLeague,", "EuroLeague.", "EuroLeague...", "twelve", "ten.", "three", "two", "arc.",
                     "Five", "six.", "defensive", "seconds.", "rim"],
        "gradeBottom": 0.3, "shots": shots, "plays": {k: PL[k] for k in IDS},
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    vis = [str(it.get(k)) for s_ in shots for it in s_.get("screen", []) for k in ("text", "lines", "sub", "clock", "teams") if k in it]
    txt = " ".join(vis).lower() + " " + " ".join(t for _, t in LINES).lower() + " " + " ".join(w["text"] for w in words).lower()
    bad = [f for f in FORBIDDEN if f in txt]
    assert not bad, f"total game time leaked: {bad}"
    return {"episode": ep}, {"duration": t_end, "cuts": {k: round(v, 3) for k, v in cuts.items()}, "logos": LOGO}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words")
    ap.add_argument("--placeholder", action="store_true")
    ap.add_argument("--voice", default="tactical/realism-v3-3/silence.mp3")
    ap.add_argument("--music")
    a = ap.parse_args()
    words = placeholder_words() if a.placeholder else json.load(open(a.words))
    props, meta = build(words, a.voice, a.music)
    json.dump(props, open(a.out, "w"))
    print(json.dumps(meta))
