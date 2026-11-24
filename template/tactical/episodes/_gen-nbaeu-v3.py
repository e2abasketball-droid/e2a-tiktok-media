#!/usr/bin/env python3
"""E2A - NBA VS EUROLEAGUE V3 (owner brief 2026-11-24 23:40 Madrid): "SHOW THE RULE. DON'T JUST WRITE THE RULE."
Same narration as V2, untouched (public/nbaeu-v2/voice.wav, word timings nbaeu-v2/nbaeu-v2-voice.words.json, same music).
V2 (tactical/episodes/_gen-nbaeu-v2.py) and V1 stay reproducible; nothing global changes (every V3 look is an opt-in).
  --hook A   "Same Game, Different Rules": hero close-up of the shooter on the NBA court, the camera rises while the
             EuroLeague court slides in underneath (animated split), the same shot in both, +2 / +3 teaser
  --hook B   "Cinematic Dual Court": one full court, the highlighted three-point line goes NBA -> FIBA -> both while the
             camera moves, the league IDs sit on the line between them, then the court splits into the two leagues
  python3 tactical/episodes/_gen-nbaeu-v3.py --hook A --out props.json   (voice/words/music default to the V2 files)"""
import argparse, copy, importlib.util, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
spec = importlib.util.spec_from_file_location("v2", os.path.join(D, "_gen-nbaeu-v2.py"))
V2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V2)
LINES, norm, line_words, orb, key, FORBIDDEN = V2.LINES, V2.norm, V2.line_words, V2.orb, V2.key, V2.FORBIDDEN
LOGO, PLATE = V2.LOGO, V2.PLATE
GOLD, WHITE, RED, GREEN = V2.GOLD, V2.WHITE, V2.RED, V2.GREEN
NBA_C, EL_C = V2.NBA_C, V2.EL_C
BASKET_Y = V2.BASKET_Y

IDS = ["three-el", "three-nba", "foul-el", "foul-nba", "d3s-nba", "d3s-el", "drive-el", "empty-nba", "empty-el"]
PL = {}
for k in IDS:
    p = copy.deepcopy(json.load(open(os.path.join(T, "tactical", "plays", f"nbaeu-{k}.json"))))
    # V3: no giant NBA / EUROLEAGUE word on the floor (the key colour + the league ID identify the court)
    if p.get("courtLook"):
        p["courtLook"]["word"] = ""
    PL[k] = p

# ------------------------------------------------------------------ cameras (pitch = degrees from vertical)
HERO = orb({"follow": ["O1"], "z": 1.25, "window": 0.5}, 3.3, 80, -32, 38)      # shoulder-height 3/4 back on the shooter
RISE = orb([0.0, 5.3, 1.0], 10.8, 56, -10, 42)                                  # both courts: shooter + rim in frame
RISE2 = orb([0.0, 5.2, 1.0], 10.2, 56, -6, 42)
B_OPEN = orb([0.0, 6.9, 0.0], 13.5, 22, 0, 40)                                  # hook B: the arcs from above
B_MOVE = orb([0.0, 6.4, 0.3], 12.5, 36, 14, 40)
TACT = orb([0.0, 6.7, 0.0], 13.5, 30, 0, 40)                                    # the spot on the floor, both arcs
SHOT_CLOSE = orb([0.0, 5.3, 1.6], 9.6, 64, -16, 42)                             # closer shot camera, same in both leagues
ARCS_B = orb([0.0, 6.6, 0.0], 14.5, 30, 0, 42)
FOUL_A = V2.FOUL_A
D34 = orb([0.4, 5.6, 0.0], 19.5, 42, -26, 44)                                   # elevated 3/4, same in both d3s scenes
D34_IN = orb([0.3, 5.5, 0.0], 18.5, 42, -26, 44)
D34_RIM = orb([0.2, 4.2, 0.4], 14.0, 46, -26, 42)
BOARD_A, BOARD_B = V2.BOARD_A, V2.BOARD_B

SUB_CHARS = 26          # one line at 54 px sentence case


def sub_groups(W):
    groups = []
    for _, seg in W.items():
        cur, n = [], 0
        for w in seg:
            if cur and n + len(w["text"]) + 1 > SUB_CHARS:
                groups.append(len(cur))
                cur, n = [], 0
            cur.append(w)
            n += len(w["text"]) + 1
            if w["text"][-1] in ",." and n > 12 and w is not seg[-1]:
                groups.append(len(cur))
                cur, n = [], 0
        if cur:
            groups.append(len(cur))
    return groups


def build(words, voice, music, hook):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, t: next(w for w in W[k] if norm(w["text"]).startswith(norm(t)))
    ws = lambda k, t: wd(k, t)["start"]
    t_end = round(e0("e1") + 1.15, 3)
    rel, make = PL["three-el"]["marks"]["release"], PL["three-el"]["marks"]["make"]
    cuts = {"intro": 0.0, "qNBA": s0("q1") - 0.1, "qEL": s0("q2") - 0.08, "el3": s0("a1") - 0.1,
            "nba2": ws("a3", "but") - 0.5, "arcsB": s0("a4") - 0.08, "foulEL": s0("f1") - 0.1, "foulNBA": s0("f3") - 0.08,
            "d3s": s0("d1") - 0.1, "d3sEL": e0("d3") + 0.15, "end": s0("e1") - 0.08}
    order = list(cuts)
    dur = {k: round((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k], 3) for i, k in enumerate(order)}
    L = lambda t, sh: round(t - cuts[sh], 3)
    shots = []
    S = lambda **kw: shots.append(kw)
    tab = lambda lg, dock, t0, to, delay=0.0: {"type": "leagueLogo", "variant": "tab", "dock": dock, "league": lg, "src": LOGO[lg], "plate": PLATE[lg],
                                                "y": 960, "w": 150 if lg == "nba" else 330, "h": 96, "from": t0, "to": to, "delay": delay}

    # ------------------------------------------------------------------ HOOK (0 - ~5.7 s)
    sh = "intro"
    d = dur[sh]
    t_make = L(ws("o3", "Watch"), sh) - 0.3                       # both balls drop just before "Watch this"
    rm = [[0, 0.0], [round(t_make - (make - 1.0), 3), 1.0], [round(t_make, 3), make], [d, round(min(3.55, make + (d - t_make) * 0.7), 3)]]
    t_rules = L(ws("o2", "rules"), sh)
    arcs_top = [{"type": "arc3", "rules": "nba", "color": NBA_C, "width": 0.12, "draw": 0.5, "z": 0.014, "from": t_rules, "to": d, "fout": 0}]
    arcs_bot = [{"type": "arc3", "rules": "fiba", "color": EL_C, "width": 0.12, "draw": 0.5, "z": 0.014, "from": t_rules + 0.15, "to": d, "fout": 0}]
    ring = lambda t0: {"type": "footRing", "player": "O1", "foot": "L", "color": GOLD, "r": 0.4, "from": t0, "to": round(t_make - (make - rel) + 0.05, 3)}
    teaser = [{"type": "score", "text": "+2", "enter": "depth", "y": 250, "size": 150, "from": t_make, "to": d, "out": round(d - 0.35, 3)},
              {"type": "score", "text": "+3", "enter": "depth", "y": 1210, "size": 150, "from": round(t_make + 0.05, 3), "to": d, "out": round(d - 0.35, 3)}]
    if hook == "A":
        t_split0, t_split1 = L(ws("o1", "EuroLeague"), sh) - 0.05, L(ws("o1", "look"), sh) + 0.25
        camA = [key(0, HERO), key(t_split0 + 0.1, orb({"follow": ["O1"], "z": 1.3, "window": 0.5}, 4.2, 74, -28, 38), "inOut"), key(t_split1 + 0.6, RISE, "inOut"), key(d, RISE2, "inOut")]
        S(id=sh, name="HOOK A Same Game, Different Rules: hero close-up of the NBA shooter, the camera rises, the EuroLeague court slides in underneath, same shot, +2 / +3",
          at=0.0, play="three-nba", remap=rm,
          camera=camA,
          ov3=arcs_top + [ring(t_split1)],
          split={"play": "three-el", "remap": rm, "camera": camA, "seam": "brand",
                 "ratioKeys": [[0.0, 1.0], [t_split0, 1.0], [t_split1, 0.5]], "ov3": arcs_bot + [ring(t_split1)]},
          screen=[tab("nba", "above", round(t_split1 - 0.05, 3), d), tab("el", "below", round(t_split1 + 0.1, 3), d)] + teaser)
    else:
        t_nba, t_el = L(ws("o1", "NBA"), sh), L(ws("o1", "EuroLeague"), sh)
        t_split0, t_split1 = L(ws("o2", "But"), sh) - 0.05, L(ws("o2", "rules"), sh) + 0.2
        S(id=sh, name="HOOK B Cinematic Dual Court: one court, the highlighted three-point line NBA -> FIBA -> both, league IDs on the line between them, then the split",
          at=0.0, play="three-nba", remap=rm,
          camera=[key(0, B_OPEN), key(t_split0, B_MOVE, "inOut"), key(t_split1 + 0.5, RISE, "inOut"), key(d, RISE2, "inOut")],
          ov3=[{"type": "arc3", "rules": "nba", "color": NBA_C, "width": 0.14, "draw": 0.5, "z": 0.014, "from": t_nba, "to": d, "fout": 0},
               {"type": "arc3", "rules": "fiba", "color": EL_C, "width": 0.14, "draw": 0.5, "z": 0.016, "from": t_el, "to": round(t_split1, 3), "fout": 0.3},
               ring(round(t_el + 0.4, 3))],
          split={"play": "three-el", "remap": rm, "camera": [key(0, B_MOVE), key(t_split1 + 0.5, RISE, "inOut"), key(d, RISE2, "inOut")], "seam": "brand",
                 "ratioKeys": [[0.0, 1.0], [t_split0, 1.0], [t_split1, 0.5]], "ov3": arcs_bot + [ring(t_split1)]},
          screen=[tab("nba", "above", t_nba, d), tab("el", "below", t_el, d)] + teaser)

    # ------------------------------------------------------------------ 01 QUARTERS: two equal compact boards, nothing else
    t_hl = L(ws("q2", "ten") + 0.2, "qEL")
    board = lambda lg, clock, y, t0, sh_: {"type": "scoreboard", "league": lg, "logo": LOGO[lg], "plate": PLATE[lg], "teams": None, "period": "Q1", "clock": clock,
                                          "shot": None, "width": 700, "highlight": round(t_hl + (cuts["qEL"] - cuts[sh_]), 3), "y": y, "from": t0, "to": 99}
    sh = "qNBA"
    d = dur[sh]
    off = cuts["qEL"] - cuts["qNBA"]
    S(id=sh, name="QUARTERS: NBA board Q1 12:00 (before the tip, empty NBA court)", at=cuts[sh], play="empty-nba", hide=["R"],
      remap=[[0, 0.0], [d, d]], camera=[key(0, BOARD_A), key(d + dur["qEL"], BOARD_B)],
      screen=[{"type": "scrim", "opacity": 0.45, "from": 0, "to": d}, {**board("nba", "12:00", 640, 0.1, sh), "to": d}])
    sh = "qEL"
    d = dur[sh]
    S(id=sh, name="QUARTERS: EuroLeague board Q1 10:00 under it, both clocks highlighted", at=cuts[sh], play="empty-el", hide=["R"],
      remap=[[0, off], [d, off + d]], camera=[key(-off, BOARD_A), key(d, BOARD_B)],
      screen=[{"type": "scrim", "opacity": 0.45, "from": -off, "to": d},
              {**board("nba", "12:00", 640, round(0.1 - off, 3), "qEL"), "to": d},
              {**board("el", "10:00", 840, 0.05, "qEL"), "to": d}])

    # ------------------------------------------------------------------ 02 THREE-POINT LINE: same shot, different value
    sh = "el3"
    d = dur[sh]
    t_from = L(s0("a2"), sh)
    t3 = L(ws("a2", "three"), sh)
    t_rel = t3 - (make - rel)
    S(id=sh, name="EuroLeague: the spot between the two arcs, the camera comes down behind the shooter, the full shot = +3", at=cuts[sh], play="three-el",
      remap=[[0, 0.0], [round(t_rel - 0.3, 3), rel - 0.3], [t3, make], [d, round(min(3.6, make + (d - t3)), 3)]],
      camera=[key(0, TACT), key(t_from, TACT, "inOut"), key(round(t_rel - 0.2, 3), SHOT_CLOSE, "inOut")],
      ov3=[{"type": "arc3", "rules": "nba", "color": NBA_C, "width": 0.13, "draw": 0.5, "z": 0.014, "from": 0.1, "to": round(t_from + 0.4, 3), "fout": 0.3},
           {"type": "arc3", "rules": "fiba", "color": EL_C, "width": 0.13, "draw": 0.5, "z": 0.016, "from": 0.3, "to": d, "fout": 0},
           {"type": "footRing", "player": "O1", "foot": "L", "color": GOLD, "r": 0.42, "from": 0.2, "to": round(t_rel + 0.05, 3), "fout": 0.15},
           {"type": "ballTrail", "len": 0.35, "from": round(t_rel, 3), "to": round(t3 + 0.1, 3)}],
      screen=[{"type": "league", "league": "el", "y": 200, "from": round(t_from, 3), "to": d, "size": 48, "align": "left"},
              {"type": "score", "text": "+3", "enter": "depth", "y": 560, "size": 240, "from": t3, "to": d, "out": round(d - 0.3, 3)}])
    sh = "nba2"
    d = dur[sh]
    p_in = 1.05                                                    # match cut: the identical shot from the same launch moment
    t2 = round(make - p_in, 3)
    S(id=sh, name="NBA: match cut, the identical shot (same spot, camera, launch moment) = +2", at=cuts[sh], play="three-nba",
      remap=[[0, p_in], [t2, make], [d, round(min(3.6, make + (d - t2)), 3)]], camera=[key(0, SHOT_CLOSE)],
      ov3=[{"type": "arc3", "rules": "nba", "color": NBA_C, "width": 0.13, "z": 0.014, "from": 0.0, "to": d, "fin": 0, "fout": 0},
           {"type": "footRing", "player": "O1", "foot": "L", "color": GOLD, "r": 0.42, "from": 0.0, "to": round(rel - p_in + 0.05, 3), "fin": 0, "fout": 0.15},
           {"type": "ballTrail", "len": 0.35, "from": round(rel - p_in, 3), "to": round(t2 + 0.1, 3)}],
      screen=[{"type": "league", "league": "nba", "y": 200, "from": 0.0, "to": d, "size": 48, "align": "left"},
              {"type": "score", "text": "+2", "enter": "depth", "y": 560, "size": 240, "from": t2, "to": d, "out": round(d - 0.25, 3)}])
    sh = "arcsB"
    d = dur[sh]
    S(id=sh, name="Different arc: both arcs, one colour key (no corner distances)", at=cuts[sh], play="three-el",
      remap=[[0, 3.5], [d, 3.5]], camera=[key(0, ARCS_B), key(d, orb([0.0, 6.4, 0.0], 13.8, 30, 0, 42))],
      ov3=[{"type": "arc3", "rules": "nba", "color": NBA_C, "width": 0.14, "draw": 0.4, "z": 0.014, "from": 0.0, "to": d, "fout": 0},
           {"type": "arc3", "rules": "fiba", "color": EL_C, "width": 0.14, "draw": 0.4, "z": 0.016, "from": 0.1, "to": d, "fout": 0}],
      screen=[{"type": "arcKey", "rows": [{"league": "nba", "color": NBA_C, "value": "7.24 m"}, {"league": "el", "color": EL_C, "value": "6.75 m"}], "y": 230, "from": 0.15, "to": d}])

    # ------------------------------------------------------------------ 03 FOULS: circles + one FOULED OUT, no header
    sh = "foulEL"
    d = dur[sh]
    t5 = L(ws("f2", "Five"), sh)
    t_out = L(ws("f2", "out"), sh)
    ticks = [round(max(0.2, t5 - 0.6) + (min(0.6, t5 - 0.2) / 4) * i, 3) for i in range(4)] + [round(t5, 3)]
    grab = 1.05
    S(id=sh, name="FOULS EuroLeague: 1-5, the 5th = FOULED OUT", at=cuts[sh], play="foul-el",
      remap=[[0, max(0.0, grab - (ticks[0] - 0.05))], [ticks[0] - 0.05, grab], [d, min(1.98, grab + (d - ticks[0]) * 0.8)]], camera=[key(0, FOUL_A)],
      ov3=[{"type": "handRing", "player": "X1", "hand": 0, "from": ticks[0], "to": d}],
      screen=[{"type": "league", "league": "el", "y": 200, "from": 0.0, "to": d, "size": 48, "align": "left"},
              {"type": "fouls", "league": "el", "max": 5, "ticks": ticks, "out": t_out, "label": "", "y": 300, "from": 0.1, "to": d}])
    sh = "foulNBA"
    d = dur[sh]
    t6 = L(ws("f3", "six"), sh)
    ticks6 = [round(0.12 + min(0.1, (t6 - 0.3) / 5) * i, 3) for i in range(5)] + [t6]
    S(id=sh, name="FOULS NBA: 1-6, the 6th = FOULED OUT", at=cuts[sh], play="foul-nba",
      remap=[[0, max(0.0, grab - t6 + 0.05)], [t6 - 0.05, grab], [d, min(1.98, grab + (d - t6) * 0.8)]], camera=[key(0, FOUL_A)],
      ov3=[{"type": "handRing", "player": "X1", "hand": 0, "from": t6 - 0.05, "to": d}],
      screen=[{"type": "league", "league": "nba", "y": 200, "from": 0.0, "to": d, "size": 48, "align": "left"},
              {"type": "fouls", "league": "nba", "max": 6, "ticks": ticks6, "out": t6 + 0.05, "label": "", "y": 300, "from": 0.0, "to": d}])

    # ------------------------------------------------------------------ 04 DEFENSIVE 3 SECONDS (NBA), elevated 3/4
    sh = "d3s"
    d = dur[sh]
    t_expl, t_tech = L(s0("d2"), sh), L(s0("d3"), sh)
    c1 = round(t_tech - 3.1, 3)
    c2, c3 = round(c1 + 1.0, 3), round(c1 + 2.0, 3)
    p_one = PL["d3s-nba"]["marks"]["count0"]
    P1 = round(min(PL["d3s-nba"]["duration"] - 3.15, max(p_one, c1)), 3)
    S(id=sh, name="D3S NBA: offence in control, X5 in the lane guarding nobody (discreet red ring), 1-2-3 at real speed, verdict + small freeze", at=cuts[sh], play="d3s-nba",
      remap=[[0, 0.0], [c1, P1], [t_tech, P1 + 3.1], [d, P1 + 3.1]],
      camera=[key(0, D34), key(t_tech, D34_IN, "inOut")],
      ov3=[{"type": "lane", "rules": "nba", "color": RED, "opacity": 0.12, "from": round(t_expl, 3), "to": d, "fin": 0.3, "fout": 0},
           {"type": "footRing", "player": "X5", "foot": "L", "color": RED, "r": 0.5, "from": round(c1 - 0.6, 3), "to": d, "fin": 0.2, "fout": 0}],
      screen=[{"type": "league", "league": "nba", "y": 200, "from": 0.0, "to": d, "size": 48, "align": "left"},
              {"type": "count3", "ticks": [c1, c2, c3], "from": c1, "to": t_tech, "y": 270, "size": 170},
              {"type": "freeze", "label": "", "from": t_tech, "to": d},
              {"type": "verdict", "text": "DEFENSIVE 3 SECONDS", "tone": "red", "y": 320, "from": t_tech, "to": d, "size": 60}])
    sh = "d3sEL"
    d = dur[sh]
    dv = PL["drive-el"]
    t_prot = L(ws("d4", "protect"), sh)
    p0 = round(dv["marks"]["contest"] - t_prot, 3)
    t_so = L(ws("d4", "so"), sh)
    S(id=sh, name="D3S EuroLeague: same attackers, same camera; O1 drives, X5 (legally in the lane) steps up and contests, kick-out", at=cuts[sh], play="drive-el",
      remap=[[0, max(0.0, p0)], [d, round(min(dv["duration"], max(0.0, p0) + d), 3)]],
      camera=[key(0, D34), key(round(t_so, 3), D34, "inOut"), key(d, D34_RIM, "inOut")],
      ov3=[{"type": "lane", "rules": "fiba", "color": GREEN, "opacity": 0.12, "from": 0.0, "to": d, "fin": 0.25, "fout": 0},
           {"type": "footRing", "player": "X5", "foot": "L", "color": GREEN, "r": 0.5, "from": 0.0, "to": d, "fin": 0.2, "fout": 0}],
      screen=[{"type": "whip", "amount": 0.4, "dir": -1, "from": 0.0, "to": 0.18},
              {"type": "league", "league": "el", "y": 200, "from": 0.0, "to": d, "size": 48, "align": "left"},
              {"type": "verdict", "text": "NO DEFENSIVE 3-SECOND RULE", "tone": "green", "y": 320, "from": 0.3, "to": round(t_so, 3), "size": 50},
              {"type": "verdict", "text": "PROTECT THE RIM", "tone": "green", "y": 320, "from": round(t_prot - 0.1, 3), "to": d, "size": 56}])

    # ------------------------------------------------------------------ CLOSE: the question, then a discreet E2A logo (loops to the hook)
    sh = "end"
    d = dur[sh]
    t_q = L(e0("e1"), sh)
    S(id=sh, name="CLOSE: NBA top / EuroLeague bottom (the hook's framing, loops to the opening), one question, E2A logo after it", at=cuts[sh], play="three-nba",
      remap=[[0, 0.2], [d, 0.2 + d * 0.3]], camera=[key(0, RISE2), key(d, RISE, "inOut")],
      split={"play": "three-el", "remap": [[0, 0.2], [d, 0.2 + d * 0.3]], "camera": [key(0, RISE2), key(d, RISE, "inOut")], "ratio": 0.5, "seam": "brand"},
      screen=[tab("nba", "above", 0.0, d), tab("el", "below", 0.0, d),
              {"type": "scrim", "opacity": 0.3, "from": 0.0, "to": d},
              {"type": "title", "lines": ["WHICH RULES WOULD", "YOU PLAY UNDER?"], "gold": [], "from": 0.05, "to": d, "y": 330, "size": 82, "noOut": True},
              {"type": "logo", "big": False, "y": 905, "width": 124, "from": round(t_q + 0.1, 3), "to": d}])

    ep = {
        "id": f"nbaeu-v3-{hook.lower()}", "title": "NBA VS EUROLEAGUE V3", "fps": 30, "voice": voice, "tail": round(t_end - words[-1]["end"], 3),
        "autoSfx": False, "pinV2": True, "env": "cinema", "athleteRenderer": "v33", "words": words, "subtitleGroups": sub_groups(W),
        "subtitleBlock": True, "subtitleCase": "sentence", "subtitleSize": 54, "subtitleY": 1400, "subtitleYAt": [[round(cuts["el3"] + 1.0, 3), round(cuts["arcsB"], 3), 1230]],
        "subtitleHide": [[0.0, round(cuts["qNBA"], 3)], [round(cuts["end"], 3), t_end]],
        "keywords": ["twelve", "ten.", "three", "two", "Five", "six.", "arc.", "rim"],
        "gradeBottom": 0.3, "shots": shots, "plays": {k: PL[k] for k in IDS},
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    vis = [str(it.get(k)) for s_ in shots for it in s_.get("screen", []) for k in ("text", "lines", "sub", "clock", "teams", "rows") if k in it]
    txt = " ".join(vis).lower() + " " + " ".join(t for _, t in LINES).lower() + " " + " ".join(w["text"] for w in words).lower()
    bad = [f for f in FORBIDDEN if f in txt]
    assert not bad, f"total game time leaked: {bad}"
    return {"episode": ep}, {"duration": t_end, "cuts": {k: round(v, 3) for k, v in cuts.items()}, "logos": LOGO, "hook": hook}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--hook", choices=["A", "B"], default="A")
    ap.add_argument("--words", default=os.path.join(D, "nbaeu-v2", "nbaeu-v2-voice.words.json"))
    ap.add_argument("--voice", default="nbaeu-v2/voice.wav")
    ap.add_argument("--music", default="nbaeu-v2/music.mp3")
    a = ap.parse_args()
    words = json.load(open(a.words))
    props, meta = build(words, a.voice, a.music, a.hook)
    json.dump(props, open(a.out, "w"))
    print(json.dumps(meta))
