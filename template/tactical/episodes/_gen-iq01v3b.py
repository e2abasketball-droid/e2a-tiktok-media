#!/usr/bin/env python3
"""E2A BASKETBALL IQ 01 V3 - TRIAL VERSION B "READ THE DEFENSE" (owner directive 2026-11-27 21:38Z).
Same play and concept as the V3 master (iq01-open-player, the low helper X3 leaves O3 open), told a different way:
NO A/B/C, NO countdown, NO "make your call". The story follows the DEFENDER instead of the decision:
  1 "You're watching the wrong player": front-on duel O1 vs X1 (camera on the basket side), ball ring, then the camera
    leaves the ball and swings across the floor to X3.
  2 "Watch this defender": follow X3 (sideline-high), vision cone ball/man, elastic tether X3-O3 that stretches and turns
    coral as he steps into the paint, O3 drifts out of frame ("left behind").
  3 "Now look what he leaves behind": freeze, crane to the CORNER (behind O3, the shooter's view), ghost of X3's start,
    open corridor from X3 to O3, beam spot on O3, measured 6.0 M, "THAT'S YOUR PASSING WINDOW".
  4 "Kick it": high top-side view, real speed, ball path, second rotation late, THREE.
  5 "Great passers ... about to be open": the passer's view (over O1's shoulder), replay of X3 leaving, separation grows live.
  6 "Did you catch it the first time?": back to the opening duel (loop).
  python3 tactical/episodes/_gen-iq01v3b.py --out props.json [--music p] [--fit ep.json] [--plan plan.json]"""
import argparse, importlib.util, json, os

D = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("g3", os.path.join(D, "_gen-iq01v3.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
PL, SC, M, DEC = g.PL, g.SC, g.M, g.DEC
GOLD, WHITE, RED = g.GOLD, g.WHITE, g.RED
orb, fol, key, r3, ttl, chip, pin, trail, mk, lane, focus, inv = g.orb, g.fol, g.key, g.r3, g.ttl, g.chip, g.pin, g.trail, g.mk, g.lane, g.focus, g.inv

LINES = [("hook", "You're watching the wrong player."), ("eyes", "Your eyes go to the ball,"),
         ("not", "but that's not where the answer is."), ("watch", "Watch this defender."),
         ("guard", "He's guarding the corner,"), ("drive", "the drive starts,"), ("paint", "and he steps into the paint."),
         ("behind", "Now look what he leaves behind!"), ("window", "That's your passing window!"), ("kick", "Kick it."),
         ("late", "The next rotation is a step too late."), ("great", "Great passers don't just see who's open."),
         ("about", "They see who's about to be open."), ("catch", "Did you catch it the first time?")]
T0 = 0.0                                                     # play time on frame 0 (O1 dribbling, before his drive)
# cameras (probed with scripts/cam-probe.mts on this play)
FRONT0 = orb([-3.2, 7.3, 0.9], 5.8, 74, 180, 50)             # basket side, front-on duel O1 vs X1
FRONT1 = orb([-3.1, 7.2, 1.0], 5.0, 76, 174, 46)
XFOL = orb(fol(["X3"], 0.9, 0.0, 0.6), 7.5, 66, 228, 52)     # high sideline follow on X3; O3 drifts out to the right
CORNER = orb([4.8, 3.0, 0.9], 7.5, 64, 255, 54)              # behind O3: the shooter's view, X3 gone into the paint
CORNER_HI = orb([3.0, 3.4, 0.6], 10.5, 60, 260, 56)          # same side, higher: O1 -> O3 lane readable
KICK0 = orb([2.6, 3.0, 0.6], 12.0, 52, 35, 58)               # top-left high: O1, ball path, O3, rim
KICK1 = orb([2.8, 2.8, 0.7], 11.0, 54, 30, 56)
POV0 = orb([2.6, 3.2, 0.8], 7.6, 68, 77, 56)                 # over O1's shoulder toward the weak corner
POV1 = orb([2.8, 3.1, 0.8], 7.0, 70, 79, 54)


def line_words(words):
    return g.line_words(words, LINES)


def build(words, voice, music):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    t_end = r3(e0("catch") + 0.6)
    cuts = {"wrong": 0.0, "defender": s0("watch") - 0.12, "behind": s0("behind") - 0.14, "kick": s0("kick") - 0.12,
            "pov": s0("great") - 0.12, "end": s0("catch") - 0.1}
    order = list(cuts)
    dur = {k: r3((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k]) for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    Lw = lambda k, i, sh: wd(k, i) - cuts[sh]
    E = lambda k, sh: e0(k) - cuts[sh]
    shots = []

    # 1 THE WRONG PLAYER -------------------------------------------------------------------------------------------
    d = dur["wrong"]
    tball, tnot = Lw("eyes", 5, "wrong"), L("not", "wrong")
    shots.append({"id": "wrong", "name": "You're watching the wrong player. Your eyes go to the ball, but that's not where the answer is.",
                  "at": 0.0, "play": "A", "remap": [[0, T0], [d, 0.45]],
                  "camera": [key(0, FRONT0), key(tnot + 0.85, FRONT1, "inOut"), key(d, XFOL, "inOut")],      # quick whip off the ball
                  "ov3": [{"type": "ballRing", "color": WHITE, "from": r3(tball - 0.15), "to": r3(tnot + 0.6)},
                          mk("X3", d - 0.9, d + 0.5)],
                  "screen": [{"type": "stamp", "text": "BASKETBALL IQ", "badge": "EP 01", "tone": "gold", "y": 110, "instant": True, "from": 0.0, "to": r3(tnot)},
                             {**ttl(["YOU'RE WATCHING", "THE WRONG PLAYER"], [1], -0.8, E("hook", "wrong") + 0.35, 250, 104), "noOut": False},
                             chip("NOT THE ANSWER", tnot + 0.35, d - 0.25, "red", 330, 58)]})

    # 2 WATCH THIS DEFENDER ----------------------------------------------------------------------------------------
    d = dur["defender"]
    tdef = Lw("watch", 2, "defender")
    tg, tdr, tp = L("guard", "defender"), L("drive", "defender"), Lw("paint", 2, "defender")      # "steps"
    tpe = E("paint", "defender")
    # play holds before the drive, then runs at ~0.5x so "he steps into the paint" lands on his real help step
    rm = [[0, 0.45], [tdr - 0.1, 0.5], [tpe + 0.1, DEC], [d, DEC]]
    shots.append({"id": "defender", "name": "Watch this defender. He's guarding the corner, the drive starts, and he steps into the paint.",
                  "at": cuts["defender"], "play": "A", "remap": rm,
                  "camera": [key(0, XFOL), key(d, orb(fol(["X3"], 0.9, 0.0, 0.6), 7.0, 64, 222, 52), "inOut")],
                  "ov3": [mk("X3", 0.0, d), {"type": "lockRing", "player": "X3", "color": RED, "size": 0.95, "from": r3(tdef - 0.05), "to": r3(tdef + 1.2)},
                          {"type": "vision", "player": "X3", "man": "O3", "split": 110, "len": 2.6, "from": r3(tg - 0.1), "to": r3(tpe)},
                          {"type": "tether", "a": "X3", "b": "O3", "rest": 3.1, "snap": 5.2, "from": r3(tg + 0.2), "to": r3(d)},
                          trail("O1", tdr, tpe + 0.3, 0.7), trail("X3", tp - 0.3, d, 0.7)],
                  "screen": [focus("X3", 0.0, d, 260, 0.55),
                             pin("X3", "WATCH HIM", tdef - 0.05, tg - 0.05, "gold", 46),
                             chip("GUARDING THE CORNER", tg - 0.05, tdr - 0.05, "gold", 330, 56),
                             pin("X3", "INTO THE PAINT", tp - 0.05, d, "red", 46),
                             {"type": "freeze", "from": r3(tpe + 0.1), "to": d}]})

    # 3 WHAT HE LEAVES BEHIND (freeze, the shooter's view) -----------------------------------------------------------
    d = dur["behind"]
    tlook, tbeh = L("behind", "behind"), Lw("behind", 4, "behind")
    twin, tpas = L("window", "behind"), Lw("window", 2, "behind")
    shots.append({"id": "behind", "name": "Now look what he leaves behind! That's your passing window!", "at": cuts["behind"], "play": "A",
                  "remap": [[0, DEC], [d, DEC]],
                  "camera": [key(0, orb(fol(["X3"], 0.9, 0.0, 0.6), 7.0, 64, 222, 52)), key(tbeh + 0.2, CORNER, "inOut"),
                             key(twin + 0.15, CORNER, "inOut"), key(d, CORNER_HI, "inOut")],
                  "ov3": [mk("X3", 0.0, d), {"type": "ghost", "player": "X3", "t": 0.0, "color": RED, "link": True, "from": r3(tlook), "to": d},
                          {"type": "openLane", "anchor": "X3", "target": "O3", "width": 1.6, "tip": 1.0, "color": GOLD, "draw": 0.6, "chevrons": True,
                           "from": r3(tbeh - 0.1), "to": r3(twin + 0.3)},
                          {"type": "spot", "player": "O3", "color": GOLD, "r": 1.2, "strength": 0.8, "beam": True, "from": r3(tbeh), "to": d},
                          mk("O3", tbeh, d),
                          {"type": "separation", "a": "X3", "b": "O3", "color": GOLD, "from": r3(tbeh + 0.2), "to": r3(twin + 0.2)},
                          lane("O3", GOLD, twin + 0.1, d, 1.8)],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d}, {"type": "punch", "amount": 0.03, "from": r3(tbeh), "to": r3(tbeh + 0.3)},
                             pin("O3", "OPEN", tbeh + 0.15, twin - 0.05, "gold", 50),
                             pin("X3", f"{SC['choices'][2]['defender_distance_m']:.1f} M", tbeh + 0.3, twin - 0.05, "gold", 44),
                             {**ttl(["THAT'S YOUR", "PASSING WINDOW"], [1], tpas - 0.1, d - 0.05, 250, 106), "noOut": False}]})

    # 4 KICK IT (real speed, top-left high) --------------------------------------------------------------------------
    d = dur["kick"]
    tk = L("kick", "kick")
    tnext = Lw("late", 1, "kick")
    rm = [[0, DEC], [max(0.05, tk - 0.1), DEC], [tk + 0.12, M["kick"]], [d, min(PL["A"]["duration"], M["kick"] + (d - tk - 0.12))]]
    t_catch, t_make = inv(rm, M["catch"]), inv(rm, M["make"])
    shots.append({"id": "kick", "name": "Kick it. The next rotation is a step too late.", "at": cuts["kick"], "play": "A", "remap": rm,
                  "camera": [key(0, KICK0), key(d, KICK1, "inOut")],
                  "ov3": [{"type": "ballPath", "src": "O1", "dst": "O3", "color": GOLD, "draw": 0.3, "from": r3(tk), "to": r3(t_catch + 0.3)},
                          mk("O3", 0.0, t_catch + 0.5), mk("X4", tnext - 0.2, d), trail("X4", tnext - 0.2, d, 0.6),
                          {"type": "separation", "a": "X4", "b": "O3", "color": RED, "from": r3(tnext), "to": r3(t_make - 0.15)},
                          {"type": "ripple", "player": "O3", "color": GOLD, "r": 1.0, "rings": 2, "period": 0.8, "from": r3(t_catch - 0.05), "to": r3(t_catch + 0.8)},
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.55, "from": r3(t_make), "to": d}],
                  "screen": [chip("LATE", tnext + 0.1, t_make - 0.1, "red", 330, 70),
                             chip("THREE.", t_make + 0.05, d, "gold", 330, 80)]})

    # 5 THE PASSER'S VIEW: who's ABOUT to be open --------------------------------------------------------------------
    d = dur["pov"]
    rw = 0.35
    tab = Lw("about", 3, "pov")                                    # "about"
    rm = [[0, min(PL["A"]["duration"], M["make"] + 0.3)], [rw, 1.0], [d - 0.4, DEC], [d, DEC]]
    shots.append({"id": "pov", "name": "Great passers don't just see who's open. They see who's about to be open. (over the passer's shoulder)",
                  "at": cuts["pov"], "play": "A", "remap": rm,
                  "camera": [key(0, POV0), key(d, POV1, "inOut")],
                  "ov3": [mk("X3", rw, d), trail("X3", rw + 0.3, d, 0.8),
                          {"type": "separation", "a": "X3", "b": "O3", "color": GOLD, "from": r3(rw + 0.2), "to": d},
                          {"type": "ghost", "player": "X3", "t": 0.0, "color": RED, "link": True, "from": r3(tab - 0.2), "to": d},
                          lane("O3", GOLD, tab + 0.2, d, 1.6)],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             ttl(["SEE WHO'S", "ABOUT TO BE OPEN"], [1], tab - 0.15, d - 0.05, 250, 100)]})

    # 6 DID YOU CATCH IT? back to the opening duel (loop) ------------------------------------------------------------
    d = dur["end"]
    shots.append({"id": "end", "name": "Did you catch it the first time? (rewinds to the opening frame)", "at": cuts["end"], "play": "A",
                  "remap": [[0, DEC], [0.25, DEC], [d - 0.3, T0], [d, T0]],
                  "camera": [key(0, POV1), key(d - 0.3, FRONT0, "inOut"), key(d, FRONT0)],
                  "ov3": [],
                  "screen": [{"type": "rewind", "from": 0.0, "to": r3(d - 0.4)},
                             ttl(["CATCH IT THE", "FIRST TIME?"], [1], 0.0, d - 0.4, 318, 100),
                             {"type": "logo", "big": False, "y": 1600, "from": 0.1, "to": r3(d - 0.4)}]})

    kw = ["wrong", "ball,", "answer", "defender.", "corner,", "drive", "paint.", "behind!", "window!", "late.", "about", "open.", "first"]
    ep = {"id": "iq01v3b-read-the-defense", "title": "YOU'RE WATCHING THE WRONG PLAYER", "fps": 30,
          "voice": voice, "tail": r3(t_end - words[-1]["end"]), "autoSfx": False, "pinV2": True, "env": "cinema",
          "athleteRenderer": "v33", "words": words, "subtitleGroups": [len(t.split()) for _, t in LINES],
          "subtitleBlock": True, "subtitleCommas": True, "subtitleCase": "sentence", "subtitleSize": 60, "subtitleY": 1330,
          "keywords": kw, "gradeBottom": 0.3, "shots": shots, "plays": PL}
    if music:
        ep["music"] = {"src": music, "volume": 1}
    plan = {"duration": t_end,
            "states": [[0.0, cuts["defender"], "B"], [cuts["defender"], cuts["behind"], "A"], [cuts["behind"], cuts["behind"] + L("window", "behind"), "BREAK"],
                       [cuts["behind"] + L("window", "behind"), cuts["pov"], "A"], [cuts["pov"], cuts["end"], "B"], [cuts["end"], t_end + 1, "A"]],
            "releases": [r3(cuts["kick"] + tk)], "hits": [r3(cuts["behind"] + L("window", "behind"))]}
    meta = {"duration": t_end, "cuts": {k: r3(v) for k, v in cuts.items()}, "plan": plan}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice", default="iq01v3b/voice.mix.wav")
    ap.add_argument("--music")
    ap.add_argument("--fit")
    ap.add_argument("--plan")
    a = ap.parse_args()
    words = json.load(open(os.path.join(D, "iq01v3b", "iq01v3b.words.json")))
    props, meta = build(words, a.voice, a.music)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"]); ep["plays"] = {k: v["id"] for k, v in PL.items()}
        json.dump(ep, open(a.fit, "w")); json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    if a.plan:
        json.dump(meta["plan"], open(a.plan, "w"), indent=1)
    print(json.dumps({k: meta[k] for k in ("duration", "cuts")}))
