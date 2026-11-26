#!/usr/bin/env python3
"""E2A ZERO CUT V2 (owner brief 2026-11-26 13:18Z "ZERO CUT V2 - complete cinematic re-edit") - Remotion props for
Tactical3DV2. V1 (_gen-zerocut.py, e2a-zero-cut-social.mp4) is untouched; V2 lives in its own files (zerocut2*).
Structure (all cut points from the real narration words, tactical/episodes/zerocut2/zerocut2-voice.words.json):
  hook      aggressive tracking, X2 bites, O2 escapes, gold lane, freeze + kinetic title (starts on the action)
  name      top-down rewind, ten markers, THE ZERO CUT
  sell      tracking: entry to the big, O2 sells the handoff, X2 trails ("Watch how his defender reacts")
  D1-D3     the defender sequence in SLOW MOTION (half-time music): geometry (3/4) -> commitment (planted foot, hips)
            -> the mistake revealed (red commitment arrow + gold space behind him)
  cutrun    ONE continuous shot: the plant in slow motion ("NO HANDOFF!"), the beat returns on "CUTS" exactly when
            O2 accelerates, pass, catch in stride, gather, layup - no cut between pass and catch (no ball teleport)
  read2     overhead establish (real speed) -> slow push to the low help and the corner -> kick, shot
  one/two   ONE CUT / TWO READS with the SAME passer's-view framing (layup vs corner)
  lesson    decision point: the low defender's two possible reactions (ghost), READ THE DEFENSE
  challenge slow push to X2 anticipating the handoff, DO YOU HAVE WHAT IT TAKES?, ends on the hook's first frame
Plays: tactical/specs/_gen-zerocut-v2.py -> zerocut2-a-layup (A), zerocut2-b-kick (B).
  python3 tactical/episodes/_gen-zerocut-v2.py --out props.json [--voice p] [--music p] [--fit ep.json] [--plan plan.json]"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PL = {k: json.load(open(os.path.join(T, "tactical", "plays", f"{v}.json"))) for k, v in
      {"A": "zerocut2-a-layup", "B": "zerocut2-b-kick"}.items()}
GOLD, NAVY, WHITE, RED = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A"
A, B = PL["A"]["marks"], PL["B"]["marks"]
RIM_LANE = [-0.7, 2.2]
CORNER = [6.6, 1.25]
HELP = [-0.45, 2.95]
HOOK0 = 1.85   # play time of the hook's first frame = the challenge's last frame (loop)

LINES = [
    ("hook1", "You're NEVER going PRO"), ("hook2", "if you can't READ this."),
    ("name", "This is the ZERO CUT."), ("sell", "The guard SELLS a handoff."), ("watch", "Watch how his defender reacts."),
    ("follows", "He follows the ball..."), ("weight", "shifts his weight..."), ("opens", "and opens the lane BEHIND him."),
    ("nohand", "NO HANDOFF!"), ("cuts", "The guard CUTS,"), ("finds", "the big finds him,"), ("easy", "and it's an EASY finish."),
    ("but", "But if the low defender STEPS ACROSS,"), ("force", "don't force the layup."),
    ("help", "That help leaves the CORNER open."), ("find", "FIND THE SHOOTER."),
    ("one", "One cut."), ("two", "Two reads."), ("great", "Great players don't just run plays."), ("read", "They READ the defense."),
    ("so", "So..."), ("doyou", "do you think you have what it takes..."), ("pro", "to go PRO?"),
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
    t_end = round(e0("pro") + 1.45, 3)
    cuts = {"hook": 0.0, "name": s0("name") - 0.1, "sell": s0("sell") - 0.1, "d1": e0("watch") + 0.08,
            "d2": s0("follows") - 0.05, "d3": s0("weight") - 0.15, "cutrun": e0("opens") + 0.05,
            "read2": e0("easy") + 0.55, "one": s0("one") - 0.12, "two": s0("two") - 0.12, "lesson": s0("great") - 0.12,
            "challenge": s0("so") - 0.15}
    order = list(cuts)
    dur = {k: round((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k], 3) for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    Lw = lambda k, i, sh: wd(k, i) - cuts[sh]
    E = lambda k, sh: e0(k) - cuts[sh]
    shots = []

    # 1 HOOK -------------------------------------------------------------------------------------------------
    d = dur["hook"]
    fz = 3.25
    rm = [[0, HOOK0], [1.1, A["cut"]], [2.4, A["pass"] + 0.15], [fz, A["catch"] + 0.08], [d, A["catch"] + 0.08]]
    cam = [key(0, orb(fol(["O2", "X2"], 1.0), 7.6, 63, 38, 46)),
           key(0.55, orb(fol("X2", 0.4), 4.8, 64, 30, 44), "inOut"),
           key(1.15, orb(fol(["X2", "O2"], 0.7), 6.2, 63, 24, 46), "inOut"),
           key(2.1, orb(fol(["O2", "X2"], 0.9, 0.15), 8.2, 60, -12, 48), "inOut", True),
           key(fz, orb(fol(["O2", "X2"], 0.9), 8.0, 60, -18, 48), "out"),
           key(d, orb(fol(["O2", "X2"], 0.9), 7.7, 60, -20, 48))]
    shots.append({"id": "hook", "name": "Hook: X2 bites on the handoff, O2 escapes behind him, gold lane, freeze", "at": 0.0, "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [trail("O2", 0.0, fz), trail("X2", 0.0, fz, 0.6),
                          {"type": "footRing", "player": "X2", "foot": "L", "color": RED, "r": 0.26, "from": 0.3, "to": 1.2},
                          {"type": "openLane", "anchor": "X2", "target": RIM_LANE, "width": 1.6, "tip": 0.8, "draw": 0.4,
                           "from": round(inv(rm, A["x2turn"]) - 0.05, 3), "to": d},
                          {"type": "separation", "a": "X2", "b": "O2", "color": GOLD, "from": fz + 0.05, "to": d}],
                  "screen": [ttl(["YOU'RE NEVER", "GOING PRO"], [1], 0.0, s0("hook2") - 0.06),
                             ttl(["IF YOU CAN'T", "READ THIS"], [1], s0("hook2"), d - 0.04),
                             {"type": "freeze", "from": fz, "to": d}]})

    # 2 NAME (top-down): rewind, ten markers, THE ZERO CUT ------------------------------------------------------
    d = dur["name"]
    rw = 0.45
    seq = ["O5", "O2", "O1", "O3", "O4", "X5", "X2", "X1", "X3", "X4"]
    mk = [{"type": "marker", "player": p, "team": "attack" if p[0] == "O" else "defense", "from": round(rw + 0.1 + j * 0.08, 3), "to": d - 0.05}
          for j, p in enumerate(seq)]
    shots.append({"id": "name", "name": "This is the Zero Cut.", "at": cuts["name"], "play": "A",
                  "remap": [[0, A["catch"] + 0.08], [rw, 0.0], [d, 0.25]], "camera": [key(0, TOP)],
                  "ov3": [*mk, {"type": "glow", "player": "O1", "r": 1.0, "color": GOLD, "strength": 0.5, "from": rw + 0.3, "to": d}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw}, ttl(["THE", "ZERO CUT"], [1], rw - 0.1, d - 0.05, 236, 112)]})

    # 3 SELL (A tracking) ------------------------------------------------------------------------------------
    d = dur["sell"]
    tw = L("watch", "sell")
    rm = [[0, 0.25], [1.0, A["bigCatch"] + 0.05], [tw, A["show"] + 0.1], [d, A["plant"] - 0.02]]
    cam = [key(0, orb(fol(["O5", "O1", "O2", "X2"], 0.6), 15.0, 54, 16, 48)),
           key(1.0, orb(fol(["O2", "X2", "O5"], 0.6, 0.1, [0.0, 0.2]), 13.0, 56, 26, 46), "inOut"),
           key(d, orb(fol(["O2", "X2", "O5"], 0.7, 0.1, [0.3, 0.3]), 11.0, 58, 30, 46), "inOut")]
    shots.append({"id": "sell", "name": "The guard SELLS a handoff. Watch how his defender reacts.", "at": cuts["sell"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "ballPath", "src": "O1", "dst": "O5", "color": WHITE, "draw": 0.3,
                           "from": round(inv(rm, A["entry"]) - 0.05, 3), "to": round(inv(rm, A["bigCatch"]) + 0.3, 3)},
                          {"type": "route", "player": "O2", "t0": A["sprint"], "t1": A["plant"], "color": GOLD, "width": 0.1, "draw": 0.4, "consume": True, "from": 0.7, "to": d},
                          trail("O2", 1.0, d), trail("X2", tw - 0.3, d, 0.6)],
                  "screen": [pin("O5", "BIG", 0.5, 1.4, "white", 38), pin("O2", "SELLS IT", 1.2, tw, "gold", 40),
                             pin("X2", "WATCH HIM", tw + 0.1, d, "white", 40)]})

    # 4 D1 GEOMETRY (three-quarter: passer, cutter, defender together; slow motion begins) --------------------------
    d = dur["d1"]
    rw = 0.35
    p_d1 = A["show"] - 0.35
    rm = [[0, A["plant"] - 0.02], [rw, p_d1], [d, p_d1 + 0.12]]
    cam = [key(0, orb(fol(["O2", "X2", "O5"], 0.9, 0.0, [0.6, 0.3]), 10.6, 56, 24, 46)), key(d, orb(fol(["O2", "X2", "O5"], 0.9, 0.0, [0.6, 0.3]), 10.0, 58, 20, 46), "inOut")]
    shots.append({"id": "d1", "name": "D1 geometry: the ballhandler, the cutter and his defender (slow motion)", "at": cuts["d1"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "passLane", "src": "O5", "dst": [-2.35, 7.25], "color": WHITE, "from": rw + 0.1, "to": d},
                          {"type": "marker", "player": "O5", "team": "attack", "from": rw, "to": d},
                          {"type": "marker", "player": "O2", "team": "attack", "from": rw + 0.1, "to": d},
                          {"type": "marker", "player": "X2", "team": "defense", "from": rw + 0.2, "to": d}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw}, pin("O5", "BALL", rw + 0.1, d, "white", 36),
                             pin("O2", "CUTTER", rw + 0.2, d, "gold", 36), pin("X2", "DEFENDER", rw + 0.3, d, "white", 36)]})

    # 5 D2 COMMITMENT (low three-quarter on X2: he follows the ball, the planted foot, the hips) ----------------------
    d = dur["d2"]
    tball = Lw("follows", 3, "d2")
    rm = [[0, p_d1 + 0.12], [d, A["plant"] - 0.12]]
    cam = [key(0, orb(fol(["X2", "O2"], 0.7), 6.4, 60, 44, 44)), key(d, orb(fol("X2", 0.7), 5.4, 63, 30, 44), "inOut")]
    shots.append({"id": "d2", "name": "D2 commitment: he follows the ball (slow motion)", "at": cuts["d2"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [trail("X2", 0.0, d, 0.6),
                          {"type": "passLane", "src": "O5", "dst": [-2.35, 7.25], "color": WHITE, "from": 0.0, "to": tball + 0.3},
                          {"type": "footRing", "player": "X2", "foot": "L", "color": RED, "r": 0.28, "from": tball, "to": d},
                          {"type": "hipMark", "player": "X2", "color": RED, "from": tball + 0.3, "to": d}],
                  "screen": [chip("HE FOLLOWS THE BALL", 0.15, d, "red", 470, 56)]})

    # 6 D3 THE MISTAKE (rise above X2: red commitment arrow, gold space opens behind him) ------------------------------
    d = dur["d3"]
    tbeh = Lw("opens", 4, "d3")
    rm = [[0, A["plant"] - 0.12], [d, A["plant"] + 0.02]]
    cam = [key(0, orb(fol("X2", 0.6), 5.0, 62, 24, 44)),
           key(min(d - 0.2, tbeh - 0.6), orb(fol(["X2", "O2"], 0.6, 0.0, [0.3, -1.2]), 8.4, 56, -4, 46), "inOut"),
           key(d, orb(fol(["X2", "O2"], 0.6, 0.0, [0.3, -1.5]), 8.8, 56, -10, 46), "inOut")]
    shots.append({"id": "d3", "name": "D3 the mistake: weight on the handoff side, the lane behind him opens", "at": cuts["d3"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "footRing", "player": "X2", "foot": "L", "color": RED, "r": 0.28, "from": 0.0, "to": tbeh - 0.3},
                          {"type": "arrow3d", "player": "X2", "t0": A["sprint"] + 0.25, "t1": A["plant"], "color": RED, "width": 0.12, "draw": 0.6,
                           "from": 0.5, "to": d},
                          {"type": "openLane", "anchor": "X2", "target": RIM_LANE, "width": 1.7, "tip": 0.8, "draw": 0.7, "from": tbeh - 0.45, "to": d}],
                  "screen": [chip("WEIGHT ON THE WRONG SIDE", 0.1, tbeh - 0.5, "red", 470, 54),
                             chip("THE LANE OPENS BEHIND HIM", tbeh - 0.35, d, "gold", 470, 56)]})

    # 7 CUTRUN: ONE continuous shot. plant (slow) -> beat back on "CUTS" = acceleration -> pass -> catch -> layup ----------
    d = dur["cutrun"]
    tno, tcuts = L("nohand", "cutrun"), L("cuts", "cutrun") + Lw("cuts", 2, "cutrun") - L("cuts", "cutrun")
    REL = tcuts - 0.05                                   # music release = O2's first explosive step
    p_rel = A["cut"] + 0.02
    rm = [[0, A["plant"] + 0.02], [REL, p_rel], [REL + 0.9, p_rel + 0.9], [REL + 0.9 + (A["make"] + 0.2 - p_rel - 0.9) / 0.85, A["make"] + 0.2],
          [d, A["make"] + 0.75]]
    t_pass, t_catch, t_fin = inv(rm, A["pass"]), inv(rm, A["catch"]), inv(rm, A["finish"])
    cam = [key(0, orb(fol(["O2", "X2"], 0.9), 7.4, 58, -6, 46)),
           key(REL - 0.25, orb(fol(["O2", "X2"], 0.95, 0.05), 6.3, 60, -22, 46), "inOut", True),
           key(t_catch, orb(fol("O2", 1.0, 0.25), 6.2, 63, -26, 48), "inOut"),
           key(t_fin + 0.2, orb(fol("O2", 1.1, 0.1), 5.6, 66, -30, 48), "inOut"),
           key(d, orb([-0.55, 2.4, 1.7], 6.2, 66, -34, 48), "inOut")]
    shots.append({"id": "cutrun", "name": "NO HANDOFF! The guard CUTS, the big finds him, EASY finish (one continuous shot)", "at": cuts["cutrun"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "openLane", "anchor": "X2", "target": RIM_LANE, "width": 1.6, "tip": 0.8, "draw": 0.0, "from": 0.0, "to": t_catch + 0.2},
                          trail("X2", REL - 0.2, t_catch, 0.5), trail("O2", REL - 0.1, t_fin),
                          {"type": "arrow3d", "player": "O2", "t0": A["cut"], "t1": A["finish"], "color": GOLD, "width": 0.13, "draw": 0.55, "consume": True,
                           "from": REL - 0.35, "to": t_catch + 0.1},
                          {"type": "ballPath", "src": "O5", "dst": "O2", "color": GOLD, "draw": 0.22, "from": round(t_pass - 0.08, 3), "to": round(t_catch + 0.35, 3)},
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.5, "from": t_fin, "to": d}],
                  "screen": [chip("NO HANDOFF", tno - 0.05, REL, "red", 470, 64),
                             pin("O2", "BACK CUT", REL, t_catch, "gold", 40),
                             chip("LAYUP.", t_fin + 0.35, d, "gold", 470, 72)]})

    # 8 READ 2: overhead establish (real speed) -> slow push to the low help + corner -> kick, catch, shot -------------
    d = dur["read2"]
    rw = 0.4
    tacross, tforce, thelp, tfind = Lw("but", 5, "read2"), L("force", "read2"), L("help", "read2"), L("find", "read2")
    tcorner = Lw("help", 4, "read2")
    t_kick = tfind + 0.05
    rm = [[0, A["make"] + 0.75], [rw, B["sprint"] + 0.6], [tacross - 0.2, B["help"] + 0.35], [t_kick - 0.6, B["kick"] - 0.12], [t_kick, B["kick"]],
          [d, min(B["make"] + 0.1, B["kick"] + (d - t_kick) * 1.05)]]
    t_catch3 = inv(rm, B["catch"])
    cam = [key(0, orb([0.4, 4.6, 0.0], 17.0, 10, 0, 70)),
           key(rw + 1.3, orb([0.6, 4.3, 0.0], 15.5, 16, 0, 64), "inOut"),
           key(tacross, orb([1.6, 4.0, 0.3], 12.6, 46, 32, 52), "inOut"),
           key(thelp - 0.2, orb([1.5, 4.5, 0.4], 13.2, 48, 38, 52), "inOut"),
           key(t_kick + 0.1, orb([1.3, 4.7, 0.4], 13.6, 48, 40, 52), "inOut"),
           key(d, orb([5.2, 2.0, 0.8], 8.5, 54, 30, 48), "inOut")]
    shots.append({"id": "read2", "name": "Read 2: the low help steps across, the corner opens, find the shooter", "at": cuts["read2"], "play": "B",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "marker", "player": "X3", "team": "defense", "from": rw + 0.2, "to": d},
                          {"type": "marker", "player": "O3", "team": "attack", "from": rw + 0.3, "to": d},
                          {"type": "route", "player": "O2", "t0": B["cut"], "t1": B["kick"], "color": GOLD, "width": 0.1, "draw": 0.35, "from": rw, "to": thelp},
                          trail("X3", tacross - 0.6, thelp, 0.7),
                          {"type": "ripple", "player": "X3", "color": RED, "r": 0.9, "rings": 2, "period": 1.2, "from": tacross - 0.4, "to": t_kick},
                          {"type": "passLane", "src": "O5", "dst": "O2", "color": RED, "from": tforce - 0.05, "to": thelp + 0.2},
                          {"type": "blocked", "at": [-0.75, 3.15], "color": RED, "from": tforce + 0.2, "to": thelp + 0.4},
                          {"type": "glow", "at": CORNER, "r": 1.4, "color": GOLD, "strength": 0.55, "from": tcorner, "to": d},
                          {"type": "passLane", "src": "O5", "dst": "O3", "color": GOLD, "from": tcorner + 0.3, "to": t_kick},
                          {"type": "ballPath", "src": "O5", "dst": "O3", "color": GOLD, "draw": 0.3, "from": round(t_kick - 0.08, 3), "to": round(t_catch3 + 0.4, 3)}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             pin("X3", "LOW HELP", rw + 0.3, tacross - 0.2, "white", 38),
                             pin("X3", "STEPS ACROSS", tacross - 0.2, thelp, "white", 38),
                             chip("DON'T FORCE IT", tforce, thelp, "red", 470, 60),
                             pin("O3", "OPEN", tcorner + 0.1, d, "gold", 44),
                             chip("CORNER IS OPEN", tcorner + 0.1, tfind, "gold", 470, 62),
                             chip("FIND THE SHOOTER", tfind, d, "gold", 470, 62)]})

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

    # 10 LESSON: the decision point, the low defender's two possible reactions, READ THE DEFENSE --------------------------
    d = dur["lesson"]
    tread = Lw("read", 1, "lesson")
    p_dec = A["x2turn"] + 0.05
    shots.append({"id": "lesson", "name": "Great players don't just run plays. They READ the defense. (decision point)", "at": cuts["lesson"], "play": "A",
                  "remap": [[0, p_dec - 0.25], [0.5, p_dec], [d, p_dec]],
                  "camera": [key(0, orb([1.3, 4.7, 0.4], 13.6, 48, 40, 52)), key(d, orb([1.0, 5.0, 0.4], 13.8, 50, 36, 50), "inOut")],
                  "ov3": [{"type": "marker", "player": "X3", "team": "defense", "from": 0.3, "to": d},
                          {"type": "footRing", "player": "X3", "foot": "L", "color": RED, "r": 0.26, "from": 0.6, "to": d},
                          {"type": "passLane", "src": "O5", "dst": "O2", "color": GOLD, "from": 0.6, "to": d},
                          {"type": "ghost", "player": "X3", "at": [-0.3, 3.1], "color": RED, "link": True, "from": 1.7, "to": d},
                          {"type": "passLane", "src": "O5", "dst": "O3", "color": GOLD, "from": 2.0, "to": d}],
                  "screen": [{"type": "freeze", "from": 0.5, "to": d},
                             chip("HELP STAYS → LAYUP", 0.6, 1.9, "gold", 470, 54),
                             chip("HELP STEPS ACROSS → CORNER", 1.9, tread - 0.2, "red", 470, 50),
                             ttl(["READ THE", "DEFENSE"], [1], tread - 0.1, d, 250, 112)]})

    # 11 CHALLENGE: slow push to X2 anticipating the handoff -> the hook's first frame (loop) ------------------------------
    d = dur["challenge"]
    tdo = L("doyou", "challenge")
    hk = shots[0]["camera"][0]["rig"]
    shots.append({"id": "challenge", "name": "So, do you think you have what it takes to go pro? (slow push to the defender, loop)", "at": cuts["challenge"], "play": "A",
                  "remap": [[0, HOOK0 - 0.55], [d, HOOK0]],
                  "camera": [key(0, orb(fol(["O2", "X2", "O5"], 0.9), 11.5, 52, 60, 46)),
                             key(d * 0.55, orb(fol(["O2", "X2"], 1.0), 9.0, 58, 48, 46), "inOut"),
                             key(d - 0.4, hk, "inOut"), key(d, hk)],
                  "ov3": [trail("X2", 0.0, d, 0.5), {"type": "marker", "player": "X2", "team": "defense", "from": 0.2, "to": d - 0.6}],
                  "screen": [ttl(["DO YOU HAVE", "WHAT IT TAKES?"], [1], tdo - 0.1, d - 0.12, 250, 104),
                             {"type": "logo", "big": False, "from": tdo + 0.4, "to": d - 0.12}]})
    ep = {
        "id": "zero-cut-v2", "title": "THE ZERO CUT", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33", "words": words,
        "subtitleGroups": [len(t.split()) for _, t in LINES],
        "subtitleBlock": True, "subtitleY": 1390, "subtitleHide": [[0.0, cuts["name"]]],
        "keywords": ["NEVER", "PRO", "READ", "ZERO", "CUT.", "SELLS", "defender", "ball...", "weight...", "BEHIND", "NO", "HANDOFF!",
                     "CUTS,", "EASY", "STEPS", "ACROSS,", "CORNER", "FIND", "THE", "SHOOTER.", "One", "Two", "reads.", "defense.",
                     "takes...", "PRO?"],
        "gradeBottom": 0.3, "shots": shots, "plays": PL,
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    rel_cut = cuts["cutrun"] + REL
    rel_kick = cuts["read2"] + t_kick
    plan = {"duration": t_end,
            "states": [[0.0, cuts["d1"], "A"], [cuts["d1"], rel_cut, "B"], [rel_cut, cuts["read2"] + tacross - 0.2, "A"],
                       [cuts["read2"] + tacross - 0.2, rel_kick, "B"], [rel_kick, cuts["lesson"], "A"],
                       [cuts["lesson"], cuts["challenge"], "B"], [cuts["challenge"], t_end + 1, "A"]],
            "releases": [round(rel_cut, 3), round(rel_kick, 3), round(cuts["challenge"], 3)],
            "hits": [round(cuts["name"], 3), round(cuts["one"], 3), round(cuts["two"], 3)]}
    meta = {"duration": t_end, "cuts": {k: round(v, 3) for k, v in cuts.items()}, "dur": dur, "plan": plan}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words", default=os.path.join(D, "zerocut2", "zerocut2-voice.words.json"))
    ap.add_argument("--voice", default="zerocut2/voice-v2.wav")
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
