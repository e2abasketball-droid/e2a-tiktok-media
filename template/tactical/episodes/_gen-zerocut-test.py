#!/usr/bin/env python3
"""E2A ZERO CUT TEST "aggressive hook" (owner brief 2026-11-26 16:27Z) - Remotion props for Tactical3DV2, trial-Reels
test version. V1 and V2 are untouched; the TEST lives in its own files (zerocut3*).
Structure (all cut points from the real narration words, tactical/episodes/zerocut3/zerocut3-voice.words.json):
  hook      STARTS IN ACTION: the cutter attacks the handoff, his defender jumps it, speed ramp into slow motion, FREEZE
            one frame after the defender lands on the wrong leg (unresolved) + kinetic STOP CALLING YOURSELF ELITE /
            IF YOU CAN'T READ THIS (ELITE, READ THIS in gold)
  name      top-down rewind, ten markers, THE ZERO CUT
  sell      tracking: entry to the big, the guard SELLS the handoff, his defender expects it
  watch     slow motion begins (psychedelic half-time music): the ball, the cutter, the defender
  wrongleg  low three-quarter on X2 (slow motion -> hold): his RIGHT leg (the compiled support, measured) blinks red
  pivot     rewind to the cutter's plant: the gold pivot arc connects the fake-handoff body angle to the real cut
            angle around his hips; he slips behind, the gold lane opens behind the defender
  cutrun    the beat returns on "One pass" exactly when the ball leaves the big's hands: catch in stride, two gather
            steps, take-off at the spot, forward flight to the rim (rebuilt finish), layup
  read2     overhead establish -> push to the low help (rim protected) -> the corner revealed late -> kick, catch, shot
  one/two   ONE CUT / TWO READS with the SAME passer's-view framing (layup vs corner)
  lesson    decision point: the low defender's two possible reactions (ghost), READ THE DEFENSE
  future    the whole action again, slow then full speed on "punish", crane up to BE PART OF THE ELITE OF THE FUTURE
Plays: tactical/specs/_gen-zerocut-test.py -> zerocut3-a-layup (A), zerocut3-b-kick (B).
  python3 tactical/episodes/_gen-zerocut-test.py --out props.json [--voice p] [--music p] [--fit ep.json] [--plan plan.json]"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PL = {k: json.load(open(os.path.join(T, "tactical", "plays", f"{v}.json"))) for k, v in
      {"A": "zerocut3-a-layup", "B": "zerocut3-b-kick"}.items()}
GOLD, NAVY, WHITE, RED = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A"
A, B = PL["A"]["marks"], PL["B"]["marks"]
RIM_LANE = [-0.7, 2.2]
CORNER = [6.6, 1.25]
HELP = [-0.45, 2.95]
# measured on the compiled V3.3 bodies (scripts/_probe-support33.mts): X2 lands on his RIGHT foot at 2.30 s and keeps
# all his weight on it until 2.60 s; O2 plants (right) 2.00-2.15 s, travel 25 deg -> -110 deg by 2.45 s
X2_LOAD = 2.33
O2_FAKE, O2_CUT = 1.95, 2.45
TAKEOFF, LAND = 3.776, 4.45

LINES = [
    ("hook1", "STOP calling yourself ELITE..."), ("hook2", "if you can't READ THIS."),
    ("name", "This is the Zero Cut."), ("sell", "It starts by SELLING the handoff."), ("watch", "Watch the defender."),
    ("weight", "His weight is already on the WRONG leg."), ("dir", "The guard changes direction..."),
    ("slips", "slips BEHIND him..."), ("opens", "and the lane OPENS."), ("nohand", "No handoff. One pass."),
    ("easy", "EASY finish."), ("but", "But if the help defender steps across..."), ("force", "don't force it."),
    ("help", "That rotation leaves the CORNER open."), ("one", "One cut."), ("two", "Two reads."),
    ("elite", "Elite players don't just run plays."), ("read", "They READ the defense."),
    ("future", "The future elite will think faster... read faster... and punish every mistake."),
    ("follow", "Follow E2A... and be part of the elite of the future."),
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
fol = lambda ids, z=1.0, lead=0.0, off=None, win=0.45: {"follow": ids, "z": z, "lead": lead, "window": win, **({"offset": off} if off else {})}
key = lambda at, rig, ease=None, spin=False: {"at": round(at, 3), "rig": rig, **({"ease": ease} if ease else {}), **({"spin": True} if spin else {})}
TOP = orb([0.0, 4.6, 0.0], 18.0, 6, 0, 76)
PASSER = orb([1.3, 4.7, 0.4], 14.0, 48, 40, 52)      # the passer's-view framing used for BOTH reads (one / two / lesson)


def inv(remap, pt):
    for (a, pa), (b, pb) in zip(remap, remap[1:]):
        if pa <= pt <= pb and pb > pa:
            return a + (b - a) * (pt - pa) / (pb - pa)
    raise ValueError(pt)


def ttl(lines, gold, fr, to, y=250, size=104):
    return {"type": "title", "lines": lines, "gold": gold, "reveal": "mask", "from": round(fr, 3), "to": round(to, 3), "y": y, "size": size}


def chip(text, fr, to, tone="gold", y=470, size=60, align="center"):
    return {"type": "chip", "text": text, "tone": tone, "align": align, "size": size, "from": round(fr, 3), "to": round(to, 3), "y": y}


def pin(p, text, fr, to, tone="gold", size=40):
    return {"type": "pin", "player": p, "text": text, "tone": tone, "from": round(fr, 3), "to": round(to, 3), "size": size}


def trail(p, fr, to, ln=0.7):
    return {"type": "motionTrail", "player": p, "len": ln, "color": GOLD if p[0] == "O" else RED, "from": round(fr, 3), "to": round(to, 3)}


def build(words, voice, music):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    t_end = round(e0("follow") + 1.4, 3)
    cuts = {"hook": 0.0, "name": s0("name") - 0.1, "sell": s0("sell") - 0.1, "watch": s0("watch") - 0.1,
            "wrongleg": s0("weight") - 0.1, "pivot": s0("dir") - 0.15, "cutrun": s0("nohand") - 0.1,
            "read2": e0("easy") + 0.55, "one": s0("one") - 0.12, "two": s0("two") - 0.12, "lesson": s0("elite") - 0.12,
            "future": s0("future") - 0.12}
    order = list(cuts)
    dur = {k: round((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k], 3) for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    Lw = lambda k, i, sh: wd(k, i) - cuts[sh]
    E = lambda k, sh: e0(k) - cuts[sh]
    shots = []

    # 1 HOOK: in action -> speed ramp -> freeze one frame after X2 lands on the wrong leg (unresolved) -------------------
    d = dur["hook"]
    t_ramp, fz = 1.25, 2.55
    rm = [[0, 0.95], [t_ramp, 2.2], [fz, X2_LOAD], [d, X2_LOAD]]
    cam = [key(0, orb(fol(["O2", "X2"], 1.0, 0.1), 8.4, 60, 52, 46)),
           key(t_ramp, orb(fol(["O2", "X2"], 0.9), 6.6, 62, 38, 44), "inOut"),
           key(fz, orb(fol(["X2", "O2"], 0.8), 5.6, 64, 26, 44), "out"),
           key(d, orb(fol(["X2", "O2"], 0.8), 5.0, 62, 8, 44), "inOut")]
    shots.append({"id": "hook", "name": "Hook: in action, the defender jumps the handoff, freeze on the mistake (unresolved)", "at": 0.0, "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [trail("O2", 0.0, fz), trail("X2", 0.0, fz, 0.6),
                          {"type": "marker", "player": "X2", "team": "defense", "from": fz, "to": d}],
                  "screen": [ttl(["STOP CALLING", "YOURSELF", "ELITE"], [2], 0.05, s0("hook2") - 0.06, 230, 104),
                             ttl(["IF YOU CAN'T", "READ THIS"], [1], s0("hook2"), d - 0.04, 250, 108),
                             {"type": "freeze", "from": fz, "to": d}]})

    # 2 NAME (top-down): rewind, ten markers, THE ZERO CUT ------------------------------------------------------
    d = dur["name"]
    rw = 0.4
    seq = ["O5", "O2", "O1", "O3", "O4", "X5", "X2", "X1", "X3", "X4"]
    mk = [{"type": "marker", "player": p, "team": "attack" if p[0] == "O" else "defense", "from": round(rw + 0.05 + j * 0.06, 3), "to": d - 0.05}
          for j, p in enumerate(seq)]
    shots.append({"id": "name", "name": "This is the Zero Cut.", "at": cuts["name"], "play": "A",
                  "remap": [[0, X2_LOAD], [rw, 0.0], [d, 0.3]], "camera": [key(0, TOP)],
                  "ov3": [*mk, {"type": "glow", "player": "O1", "r": 1.0, "color": GOLD, "strength": 0.5, "from": rw + 0.3, "to": d}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw}, ttl(["THE", "ZERO CUT"], [1], rw - 0.1, d - 0.05, 236, 112)]})

    # 3 SELL: the guard sells the handoff, his defender EXPECTS it ------------------------------------------------
    d = dur["sell"]
    tsell = Lw("sell", 3, "sell")
    rm = [[0, 0.3], [0.9, A["bigCatch"] + 0.05], [d, 1.95]]
    cam = [key(0, orb(fol(["O5", "O1", "O2", "X2"], 0.6), 14.5, 54, 16, 48)),
           key(1.0, orb(fol(["O2", "X2", "O5"], 0.6, 0.1, [0.0, 0.2]), 12.4, 56, 26, 46), "inOut"),
           key(d, orb(fol(["O2", "X2", "O5"], 0.7, 0.1, [0.3, 0.3]), 10.6, 58, 30, 46), "inOut")]
    shots.append({"id": "sell", "name": "It starts by SELLING the handoff.", "at": cuts["sell"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "ballPath", "src": "O1", "dst": "O5", "color": WHITE, "draw": 0.3,
                           "from": round(inv(rm, A["entry"]) - 0.05, 3), "to": round(inv(rm, A["bigCatch"]) + 0.3, 3)},
                          {"type": "route", "player": "O2", "t0": A["sprint"], "t1": A["plant"], "color": GOLD, "width": 0.1, "draw": 0.4, "consume": True, "from": 0.6, "to": d},
                          trail("O2", 0.9, d), trail("X2", tsell - 0.2, d, 0.6)],
                  "screen": [pin("O5", "BIG", 0.4, 1.3, "white", 38), pin("O2", "FAKE HANDOFF", tsell - 0.1, tsell + 0.75, "gold", 40),
                             pin("X2", "EXPECTS THE HANDOFF", tsell + 0.75, d, "white", 40)]})

    # 4 WATCH: slow motion begins - ball, cutter, defender (three-quarter) -------------------------------------------
    d = dur["watch"]
    rm = [[0, 1.95], [d, 2.17]]
    cam = [key(0, orb(fol(["O2", "X2", "O5"], 0.9, 0.0, [0.6, 0.3]), 9.6, 58, 30, 46)),
           key(d, orb(fol(["X2", "O2"], 0.8, 0.0, [0.2, 0.2]), 7.4, 60, 36, 44), "inOut")]
    shots.append({"id": "watch", "name": "Watch the defender. (slow motion begins)", "at": cuts["watch"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "marker", "player": "O2", "team": "attack", "from": 0.05, "to": d},
                          {"type": "marker", "player": "X2", "team": "defense", "from": 0.15, "to": d}, trail("X2", 0.0, d, 0.6)],
                  "screen": [pin("O2", "CUTTER", 0.1, d, "gold", 36), pin("X2", "DEFENDER", 0.25, d, "white", 40)]})

    # 5 WRONG LEG: low three-quarter on X2, he lands on his RIGHT leg -> blinking red leg -> hold -------------------------
    d = dur["wrongleg"]
    twr = Lw("weight", 6, "wrongleg")       # "WRONG"
    rm = [[0, 2.17], [twr - 0.05, X2_LOAD], [twr + 0.4, X2_LOAD + 0.02], [d, X2_LOAD + 0.03]]
    cam = [key(0, orb(fol(["X2", "O2"], 0.7), 6.2, 60, 42, 44)),
           key(twr, orb(fol("X2", 0.6), 5.0, 62, 30, 42), "inOut"),
           key(d, orb(fol("X2", 0.6), 4.7, 63, 24, 42), "inOut")]
    shots.append({"id": "wrongleg", "name": "His weight is already on the WRONG leg (right leg blinks red)", "at": cuts["wrongleg"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [trail("X2", 0.0, twr, 0.6),
                          {"type": "arrow3d", "player": "X2", "t0": A["sprint"] + 0.25, "t1": X2_LOAD, "color": RED, "width": 0.1, "draw": 0.5,
                           "from": 0.2, "to": twr - 0.2},
                          {"type": "legLoad", "player": "X2", "leg": "R", "color": RED, "blinks": 3, "period": 0.36, "from": twr - 0.12, "to": d}],
                  "screen": [chip("HE JUMPS THE HANDOFF", 0.15, twr - 0.15, "red", 470, 54),
                             chip("WEIGHT ON THE WRONG LEG", twr - 0.1, d, "red", 470, 54)]})

    # 6 PIVOT: rewind to the plant, the gold pivot arc fake angle -> cut angle, slips behind, the lane opens --------------
    d = dur["pivot"]
    rw = 0.3
    tslip, topen = L("slips", "pivot"), L("opens", "pivot")
    rm = [[0, X2_LOAD + 0.03], [rw, 1.9], [tslip - 0.1, O2_CUT + 0.05], [topen, 2.7], [d, 2.8]]
    cam = [key(0, orb(fol("O2", 0.9), 5.0, 56, 40, 44)),
           key(rw + 0.2, orb(fol("O2", 0.9), 4.6, 60, 30, 44), "inOut"),
           key(tslip - 0.1, orb(fol(["O2", "X2"], 0.8), 5.6, 60, 6, 44), "inOut"),
           key(topen, orb(fol(["X2", "O2"], 0.6, 0.0, [0.2, -1.2]), 8.0, 58, -6, 46), "inOut"),
           key(d, orb(fol(["X2", "O2"], 0.6, 0.0, [0.3, -1.5]), 8.6, 58, -12, 46), "inOut")]
    shots.append({"id": "pivot", "name": "The guard changes direction (pivot arc), slips behind him, the lane opens", "at": cuts["pivot"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "pivotArc", "player": "O2", "t0": O2_FAKE, "t1": O2_CUT, "color": GOLD, "draw": 0.9,
                           "from": rw + 0.15, "to": tslip + 0.2},
                          {"type": "legLoad", "player": "X2", "leg": "R", "color": RED, "blinks": 0, "from": tslip - 0.2, "to": topen},
                          trail("O2", tslip - 0.2, d),
                          {"type": "openLane", "anchor": "X2", "target": RIM_LANE, "width": 1.7, "tip": 0.8, "draw": 0.7, "from": topen - 0.35, "to": d}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             chip("FAKE  →  REAL CUT", rw + 0.3, tslip - 0.1, "gold", 470, 54),
                             pin("O2", "BEHIND HIM", tslip, topen - 0.2, "gold", 40),
                             chip("THE LANE OPENS", topen - 0.2, d, "gold", 470, 58)]})

    # 7 CUTRUN: slow first step, the beat returns on "One pass" = the ball leaves the big's hands; catch in stride,
    #   two gather steps, take-off at the spot, forward flight, finish at the rim (one continuous shot) ------------------
    d = dur["cutrun"]
    tone = Lw("nohand", 2, "cutrun")         # "One"
    REL = tone - 0.03
    rm = [[0, 2.4], [REL, A["pass"]], [REL + (A["make"] + 0.1 - A["pass"]) / 0.88, A["make"] + 0.1], [d, A["make"] + 0.1 + (d - REL - (A["make"] + 0.1 - A["pass"]) / 0.88) * 0.8]]
    t_pass, t_catch, t_to, t_land = REL, inv(rm, A["catch"]), inv(rm, TAKEOFF), inv(rm, LAND)
    cam = [key(0, orb(fol(["O2", "X2"], 0.9), 7.0, 58, -8, 46)),
           key(REL, orb(fol(["O2", "O5"], 0.9, 0.05), 7.6, 58, -18, 46), "inOut", True),
           key(t_catch, orb(fol("O2", 1.0, 0.2), 6.4, 60, -28, 46), "inOut"),
           key(t_to, orb(fol("O2", 1.3, 0.1), 5.4, 64, -40, 48), "inOut"),
           key(t_land + 0.2, orb([-0.3, 1.9, 2.0], 5.6, 68, -46, 48), "inOut"),
           key(d, orb([-0.3, 1.9, 1.9], 6.2, 68, -50, 48), "inOut")]
    shots.append({"id": "cutrun", "name": "No handoff. One pass. EASY finish. (one continuous shot, rebuilt finish)", "at": cuts["cutrun"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "openLane", "anchor": "X2", "target": RIM_LANE, "width": 1.6, "tip": 0.8, "draw": 0.0, "from": 0.0, "to": t_catch + 0.1},
                          trail("X2", 0.0, t_catch, 0.5), trail("O2", 0.0, t_to),
                          {"type": "ballPath", "src": "O5", "dst": "O2", "color": GOLD, "draw": 0.2, "from": round(t_pass - 0.1, 3), "to": round(t_catch + 0.3, 3)},
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.5, "from": t_to, "to": d}],
                  "screen": [chip("NO HANDOFF", 0.0, REL, "red", 470, 64),
                             chip("ONE PASS", REL, t_catch + 0.25, "gold", 470, 64),
                             chip("EASY FINISH", t_land - 0.1, d, "gold", 470, 68)]})

    # 8 READ 2: overhead establish -> push to the low help (rim protected) -> the corner revealed late -> kick, shot -------
    d = dur["read2"]
    rw = 0.4
    tacross, tforce, thelp = Lw("but", 5, "read2"), L("force", "read2"), L("help", "read2")
    tcorner = Lw("help", 4, "read2")
    t_kick = E("help", "read2") - 0.25
    rm = [[0, A["make"] + 0.6], [rw, B["sprint"] + 0.6], [tacross - 0.2, B["help"] + 0.35], [t_kick - 0.6, B["kick"] - 0.12], [t_kick, B["kick"]],
          [d, min(B["make"] + 0.1, B["kick"] + (d - t_kick) * 1.05)]]
    t_catch3 = inv(rm, B["catch"])
    cam = [key(0, orb([0.4, 4.6, 0.0], 17.0, 10, 0, 70)),
           key(rw + 1.3, orb([0.6, 4.3, 0.0], 15.5, 16, 0, 64), "inOut"),
           key(tacross, orb([0.2, 3.4, 0.3], 10.4, 50, 26, 50), "inOut"),
           key(thelp - 0.2, orb([0.0, 3.2, 0.4], 9.6, 52, 22, 50), "inOut"),
           key(tcorner, orb([1.5, 4.3, 0.4], 13.2, 48, 38, 52), "inOut"),
           key(t_kick + 0.1, orb([1.3, 4.7, 0.4], 13.6, 48, 40, 52), "inOut"),
           key(d, orb([5.2, 2.0, 0.8], 8.5, 54, 30, 48), "inOut")]
    shots.append({"id": "read2", "name": "Read 2: the help steps across, the corner opens (revealed late), kick to the shooter", "at": cuts["read2"], "play": "B",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "marker", "player": "X3", "team": "defense", "from": rw + 0.2, "to": d},
                          {"type": "route", "player": "O2", "t0": B["cut"], "t1": B["kick"], "color": GOLD, "width": 0.1, "draw": 0.35, "from": rw, "to": thelp},
                          trail("X3", tacross - 0.6, thelp, 0.7),
                          {"type": "ripple", "player": "X3", "color": RED, "r": 0.9, "rings": 2, "period": 1.2, "from": tacross - 0.4, "to": t_kick},
                          {"type": "glow", "hoop": True, "r": 0.9, "color": RED, "strength": 0.35, "from": tacross, "to": tcorner},
                          {"type": "passLane", "src": "O5", "dst": "O2", "color": RED, "from": tforce - 0.05, "to": thelp + 0.6},
                          {"type": "blocked", "at": [-0.75, 3.15], "color": RED, "from": tforce + 0.2, "to": thelp + 0.8},
                          {"type": "marker", "player": "O3", "team": "attack", "from": tcorner - 0.1, "to": d},
                          {"type": "glow", "at": CORNER, "r": 1.4, "color": GOLD, "strength": 0.55, "from": tcorner, "to": d},
                          {"type": "passLane", "src": "O5", "dst": "O3", "color": GOLD, "from": tcorner + 0.3, "to": t_kick},
                          {"type": "ballPath", "src": "O5", "dst": "O3", "color": GOLD, "draw": 0.3, "from": round(t_kick - 0.08, 3), "to": round(t_catch3 + 0.4, 3)}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             pin("X3", "HELP DEFENDER", rw + 0.3, tacross + 0.1, "white", 38),
                             chip("RIM PROTECTED", tacross + 0.15, tforce, "red", 470, 58),
                             chip("DON'T FORCE IT", tforce, tcorner, "red", 470, 60),
                             pin("O3", "OPEN", tcorner + 0.1, d, "gold", 44),
                             chip("CORNER IS OPEN", tcorner + 0.1, t_kick, "gold", 900, 62),
                             chip("KICK IT OUT", t_kick, d, "gold", 470, 62)]})

    # 9 ONE CUT / TWO READS (same passer's-view framing) ---------------------------------------------------------------
    d = dur["one"]
    shots.append({"id": "one", "name": "One cut. (read 1: the layup, passer's view)", "at": cuts["one"], "play": "A",
                  "remap": [[0, A["pass"] - 0.25], [d, min(A["make"] + 0.2, A["pass"] - 0.25 + d * 1.0)]],
                  "camera": [key(0, PASSER), key(d, orb([1.3, 4.7, 0.4], 13.6, 48, 40, 52), "inOut")],
                  "ov3": [trail("O2", 0.0, d), {"type": "ballPath", "src": "O5", "dst": "O2", "color": GOLD, "draw": 0.25, "from": 0.15, "to": d},
                          {"type": "glow", "hoop": True, "r": 1.1, "color": GOLD, "strength": 0.45, "from": d - 0.6, "to": d}],
                  "screen": [ttl(["ONE", "CUT"], [1], 0.05, d, 250, 112), chip("READ 1 · LAYUP", 0.4, d, "gold", 470, 56)]})
    d = dur["two"]
    shots.append({"id": "two", "name": "Two reads. (read 2: the corner, same framing)", "at": cuts["two"], "play": "B",
                  "remap": [[0, B["kick"] - 0.35], [d, min(B["make"], B["kick"] - 0.35 + d * 1.0)]],
                  "camera": [key(0, PASSER), key(d, orb([1.3, 4.7, 0.4], 13.6, 48, 40, 52), "inOut")],
                  "ov3": [{"type": "marker", "player": "X3", "team": "defense", "from": 0.0, "to": d},
                          {"type": "ballPath", "src": "O5", "dst": "O3", "color": GOLD, "draw": 0.3, "from": 0.2, "to": d},
                          {"type": "glow", "at": CORNER, "r": 1.3, "color": GOLD, "strength": 0.55, "from": 0.3, "to": d}],
                  "screen": [ttl(["TWO", "READS"], [1], 0.05, d, 250, 112), chip("READ 2 · CORNER", 0.4, d, "blue", 470, 56)]})

    # 10 LESSON: decision point, the low defender's two possible reactions, READ THE DEFENSE ------------------------------
    d = dur["lesson"]
    tread = Lw("read", 1, "lesson")
    p_dec = A["x2turn"] + 0.05
    shots.append({"id": "lesson", "name": "Elite players don't just run plays. They READ the defense. (decision point)", "at": cuts["lesson"], "play": "A",
                  "remap": [[0, p_dec - 0.25], [0.5, p_dec], [d, p_dec]],
                  "camera": [key(0, orb([1.3, 4.7, 0.4], 13.6, 48, 40, 52)), key(d, orb([1.0, 5.0, 0.4], 13.8, 50, 36, 50), "inOut")],
                  "ov3": [{"type": "marker", "player": "X3", "team": "defense", "from": 0.3, "to": d},
                          {"type": "passLane", "src": "O5", "dst": "O2", "color": GOLD, "from": 0.6, "to": d},
                          {"type": "ghost", "player": "X3", "at": [-0.3, 3.1], "color": RED, "link": True, "from": 1.3, "to": d},
                          {"type": "passLane", "src": "O5", "dst": "O3", "color": GOLD, "from": 1.6, "to": d}],
                  "screen": [{"type": "freeze", "from": 0.5, "to": d},
                             chip("HELP STAYS → LAYUP", 0.5, 1.5, "gold", 470, 54),
                             chip("HELP STEPS ACROSS → CORNER", 1.5, tread - 0.2, "red", 470, 50),
                             ttl(["READ THE", "DEFENSE"], [1], tread - 0.1, d, 250, 112)]})

    # 11 FUTURE: the whole action again (slow -> full speed on "punish"), crane up, BE PART OF THE ELITE OF THE FUTURE ------
    d = dur["future"]
    tthink, tread2, tpun = Lw("future", 4, "future"), Lw("future", 6, "future"), Lw("future", 9, "future")
    tfol = L("follow", "future")
    rm = [[0, 1.3], [tpun, A["pass"]], [tpun + (A["make"] + 0.15 - A["pass"]) / 0.95, A["make"] + 0.15], [d, A["make"] + 0.5]]
    t_make = inv(rm, A["make"])
    cam = [key(0, orb(fol(["O2", "X2", "O5"], 0.9), 9.0, 56, 70, 46)),
           key(tpun, orb(fol(["O2", "X2", "O5"], 0.9), 8.2, 58, 20, 46), "inOut"),
           key(t_make, orb([-0.4, 2.6, 1.2], 7.2, 64, -30, 48), "inOut"),
           key(tfol + 0.3, orb([0.0, 3.6, 0.6], 11.5, 30, -10, 50), "inOut"),
           key(d, orb([0.0, 4.0, 0.4], 14.0, 14, 0, 56), "inOut")]
    shots.append({"id": "future", "name": "The future elite... Follow E2A and be part of the elite of the future.", "at": cuts["future"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [trail("O2", 0.0, t_make), trail("X2", 0.0, tpun, 0.5),
                          {"type": "ballPath", "src": "O5", "dst": "O2", "color": GOLD, "draw": 0.2, "from": round(tpun - 0.1, 3), "to": round(tpun + 0.6, 3)},
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.5, "from": t_make - 0.2, "to": d}],
                  "screen": [chip("THINK FASTER", tthink - 0.05, tread2 - 0.05, "gold", 470, 58),
                             chip("READ FASTER", tread2 - 0.05, tpun - 0.05, "gold", 470, 58),
                             chip("PUNISH EVERY MISTAKE", tpun - 0.05, tfol - 0.1, "red", 470, 56),
                             ttl(["BE PART OF", "THE ELITE OF", "THE FUTURE"], [1, 2], tfol - 0.05, d - 0.05, 230, 98),
                             {"type": "logo", "big": False, "from": tfol + 0.5, "to": d - 0.05}]})
    ep = {
        "id": "zero-cut-test-aggressive", "title": "THE ZERO CUT", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33", "words": words,
        "subtitleGroups": [len(t.split()) for _, t in LINES],
        "subtitleBlock": True, "subtitleY": 1390, "subtitleHide": [[0.0, cuts["name"]]],
        "keywords": ["STOP", "ELITE...", "READ", "THIS.", "Zero", "Cut.", "SELLING", "WRONG", "leg.", "direction...", "BEHIND", "OPENS.",
                     "No", "handoff.", "One", "pass.", "EASY", "steps", "across...", "CORNER", "cut.", "Two", "reads.", "defense.",
                     "faster...", "punish", "E2A...", "elite", "future."],
        "gradeBottom": 0.3, "shots": shots, "plays": PL,
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    rel_one = cuts["cutrun"] + REL
    rel_kick = cuts["read2"] + t_kick
    plan = {"duration": t_end,
            "states": [[0.0, cuts["watch"], "A"], [cuts["watch"], rel_one, "B"], [rel_one, cuts["read2"] + tacross - 0.2, "A"],
                       [cuts["read2"] + tacross - 0.2, rel_kick, "B"], [rel_kick, cuts["lesson"], "A"],
                       [cuts["lesson"], cuts["future"], "B"], [cuts["future"], t_end + 1, "A"]],
            "releases": [round(rel_one, 3), round(rel_kick, 3), round(cuts["future"], 3)],
            "hits": [round(cuts["name"], 3), round(cuts["one"], 3), round(cuts["two"], 3)]}
    meta = {"duration": t_end, "cuts": {k: round(v, 3) for k, v in cuts.items()}, "dur": dur, "plan": plan}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words", default=os.path.join(D, "zerocut3", "zerocut3-voice.words.json"))
    ap.add_argument("--voice", default="zerocut3/voice-test.wav")
    ap.add_argument("--music")
    ap.add_argument("--fit")
    ap.add_argument("--plan")
    a = ap.parse_args()
    words = json.load(open(a.words))
    props, meta = build(words, a.voice, a.music)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"])
        ep["plays"] = {k: v["id"] for k, v in PL.items()}
        json.dump(ep, open(a.fit, "w"))
        json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    if a.plan:
        json.dump(meta["plan"], open(a.plan, "w"), indent=1)
    print(json.dumps({k: meta[k] for k in ("duration", "cuts")}))
