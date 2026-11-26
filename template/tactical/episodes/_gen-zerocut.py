#!/usr/bin/env python3
"""E2A ZERO CUT (owner master brief 2026-11-26, HIGH-RETENTION EDITION) - the edit, as Remotion props for Tactical3DV2.
E2A Basketball Visual Standard v1 (athleteRenderer v33, env cinema, markers, short pins) + Floor Graphics Stability
Standard (one floor area per idea, no abutting fades) + the brief's camera system:
  A PLAYER TRACKING (orbit following O2/X2)  B DEFENDER POV (pov behind X2)  C DYNAMIC ORBIT (spin round O2/O5 on the
  plant)  D TACTICAL TOP-DOWN  E CINEMATIC FINISH (orbit following the cutter to the rim).
Effects: motionTrail (gold attack / red defence), footRing on X2's plant foot, openLane (NEW, telestration3d-bp.tsx)
behind the beaten defender, ballPath on the real pass, ONE freeze in the development (+ the hook's), masked titles.
Plays: tactical/specs/_gen-zerocut.py -> zerocut-a-layup (A), zerocut-b-kick (B).
Words: tactical/episodes/zerocut/zerocut-voice.words.json (the ONE Deuce take, silences inserted, 40.1 s).
  python3 tactical/episodes/_gen-zerocut.py --out props.json [--voice path] [--music path] [--fit ep.json] [--trial]
  --trial: trial-reel variant (same voice take): wider hook framing, different hook title split, mirrored chip colours"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PL = {k: json.load(open(os.path.join(T, "tactical", "plays", f"{v}.json"))) for k, v in
      {"A": "zerocut-a-layup", "B": "zerocut-b-kick"}.items()}
GOLD, NAVY, WHITE, RED, AMBER = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A", "#F2A33A"
A, B = PL["A"]["marks"], PL["B"]["marks"]
RIM_LANE = [-0.7, 2.2]

LINES = [
    ("hook1", "You're NEVER going PRO"), ("hook2", "if you can't READ this."),
    ("name", "It's called the ZERO CUT."), ("sell", "It starts by selling a handoff."),
    ("big", "The big catches up top."), ("guard", "The guard sprints toward him,"), ("follows", "and his defender follows."),
    ("thinks", "He thinks the ball's coming sideways."), ("feet", "WATCH HIS FEET."),
    ("nohand", "But there's NO HANDOFF!"), ("slips", "The cutter slips behind him,"), ("takes", "takes the pass, and finishes."),
    ("r1", "Sell the handoff,"), ("r2", "cut behind the defender,"), ("r3", "and force the low help to choose."),
    ("help", "If that help steps across,"), ("open", "the CORNER IS OPEN."),
    ("force", "Don't force the layup"), ("kick", "kick it out."),
    ("same", "Same action."), ("two", "Two reads."), ("iq", "That's BASKETBALL IQ."),
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
key = lambda at, rig, ease=None, spin=False: {"at": at, "rig": rig, **({"ease": ease} if ease else {}), **({"spin": True} if spin else {})}
TOP = orb([0.0, 4.6, 0.0], 18.0, 6, 0, 76)          # D tactical top-down
TOPB = orb([0.5, 5.0, 0.0], 24.5, 32, 0, 50)          # D for read B (left corner included)


def inv(remap, pt):
    for (a, pa), (b, pb) in zip(remap, remap[1:]):
        if pa <= pt <= pb and pb > pa:
            return a + (b - a) * (pt - pa) / (pb - pa)
    raise ValueError(pt)


def ttl(lines, gold, fr, to, y=250, size=104):
    return {"type": "title", "lines": lines, "gold": gold, "reveal": "mask", "from": fr, "to": to, "y": y, "size": size}


def chip(text, fr, to, tone="gold", y=470, size=60, align="center"):
    return {"type": "chip", "text": text, "tone": tone, "align": align, "size": size, "from": fr, "to": to, "y": y}


def pin(p, text, fr, to, tone="gold", size=40):
    return {"type": "pin", "player": p, "text": text, "tone": tone, "from": fr, "to": to, "size": size}


def trail(p, fr, to, ln=0.7):
    return {"type": "motionTrail", "player": p, "len": ln, "color": GOLD if p[0] == "O" else RED, "from": fr, "to": to}


def build(words, voice, music, trial=False):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    t_end = round(e0("iq") + 0.75, 3)
    cuts = {"hook": 0.0, "name": s0("name") - 0.1, "sell": s0("big") - 0.12, "feet": s0("thinks") - 0.12,
            "cut": s0("nohand") - 0.1, "replay": s0("r1") - 0.12, "read2": s0("help") - 0.12,
            "same": s0("same") - 0.1, "twoA": s0("two") - 0.1, "twoB": s0("two") + 0.4, "iq": s0("iq") - 0.08,
            "loop": t_end - 0.6}
    order = list(cuts)
    dur = {k: round((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k], 3) for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    Lw = lambda k, i, sh: wd(k, i) - cuts[sh]
    E = lambda k, sh: e0(k) - cuts[sh]
    shots = []
    HOOK0 = 1.3       # play time of the hook's first frame (and of the loop's last frames)

    # 1 HOOK: tracking -> zoom to X2's feet as he anticipates -> O2 changes direction -> camera turns with the cut ->
    #   gold lane where the space opened -> freeze at the max advantage
    d = dur["hook"]
    fz = 2.9
    rm = [[0, HOOK0], [1.15, A["cut"]], [2.5, A["catch"] - 0.15], [fz, A["catch"]], [d, A["catch"]]]
    if trial:
        cam = [key(0, orb(fol(["O2", "X2"], 0.8), 10.5, 52, 22, 48)), key(1.3, orb(fol(["O2", "X2"], 0.8), 9.0, 54, 10, 48), "inOut"),
               key(fz, orb(fol(["O2", "X2"], 0.8), 9.5, 55, -8, 48), "inOut"), key(d, orb(fol(["O2", "X2"], 0.8), 9.3, 55, -9, 48))]
    else:
        cam = [key(0, orb(fol(["O2", "X2"], 1.0), 7.6, 63, 38, 46)),
               key(0.55, orb(fol("X2", 0.4), 4.6, 64, 30, 44), "inOut"),
               key(1.2, orb(fol(["X2", "O2"], 0.7), 6.2, 63, 24, 46), "inOut"),
               key(2.0, orb(fol(["O2", "X2"], 0.9, 0.15), 8.4, 60, -12, 48), "inOut", True),
               key(fz, orb(fol(["O2", "X2"], 0.9), 7.8, 60, -18, 48), "out"),
               key(d, orb(fol(["O2", "X2"], 0.9), 7.5, 60, -20, 48))]
    t1, t2 = ((["NEVER GOING", "PRO?"], [1]), (["NOT IF YOU", "CAN'T READ THIS"], [1])) if trial else \
             ((["YOU'RE NEVER", "GOING PRO"], [1]), (["IF YOU CAN'T", "READ THIS"], [1]))
    shots.append({"id": "hook", "name": "Hook: X2 bites on the handoff, O2 cuts behind him, gold lane, freeze", "at": 0.0, "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [trail("O2", 0.0, fz), trail("X2", 0.0, fz, 0.6),
                          {"type": "footRing", "player": "X2", "foot": "L", "color": RED, "r": 0.26, "from": 0.4, "to": 1.3},
                          {"type": "openLane", "anchor": "X2", "target": RIM_LANE, "width": 1.6, "tip": 0.8, "draw": 0.4, "from": 2.35, "to": d},
                          {"type": "separation", "a": "X2", "b": "O2", "color": GOLD, "from": fz + 0.05, "to": d}],
                  "screen": [ttl(*t1, 0.0, s0("hook2") - 0.06), ttl(*t2, s0("hook2"), d - 0.04),
                             {"type": "freeze", "from": fz, "to": d}]})

    # 2 NAME (D top-down): rewind to the start, the ten players, THE ZERO CUT, gold trace to the ball, the handoff it sells
    d = dur["name"]
    rw = 0.5
    seq = ["O5", "O2", "O1", "O3", "O4", "X5", "X2", "X1", "X3", "X4"]
    mk = [{"type": "marker", "player": p, "team": "attack" if p[0] == "O" else "defense", "from": round(rw + 0.15 + j * 0.1, 3), "to": d - 0.05}
          for j, p in enumerate(seq)]
    ts = L("sell", "name")
    shots.append({"id": "name", "name": "It's called the Zero Cut. It starts by selling a handoff.", "at": cuts["name"], "play": "A",
                  "remap": [[0, A["catch"]], [rw, 0.0], [ts, 0.0], [d, 0.0]], "camera": [key(0, TOP)],
                  "ov3": [*mk,
                          {"type": "glow", "player": "O1", "r": 1.0, "color": GOLD, "strength": 0.5, "from": rw + 0.3, "to": ts},
                          {"type": "route", "player": "O5", "t0": 0.05, "t1": A["bigCatch"], "color": WHITE, "width": 0.08, "draw": 0.45, "from": rw + 0.6, "to": d},
                          {"type": "route", "player": "O2", "t0": A["sprint"], "t1": A["plant"], "color": GOLD, "width": 0.1, "draw": 0.5, "dashed": True, "from": ts + 0.15, "to": d}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             ttl(["THE", "ZERO CUT"], [1], rw - 0.1, d - 0.05, 236, 112),
                             pin("O2", "HANDOFF?", ts + 0.5, d, "white", 38)]})

    # 3 SELL (A tracking): O1 -> O5 up top, O2 sprints toward the big, X2 trails
    d = dur["sell"]
    tb, tg_, tf = L("big", "sell"), L("guard", "sell"), L("follows", "sell")
    rm = [[0, 0.1], [tb + 0.5, A["entry"] + 0.1], [E("big", "sell"), A["bigCatch"] + 0.05], [tg_ + 0.3, A["sprint"] + 0.25],
          [E("follows", "sell"), A["show"] + 0.15], [d, A["show"] + 0.32]]
    cam = [key(0, orb(fol(["O5", "O1", "O2", "X2"], 0.6), 15.5, 54, 16, 48)),
           key(tg_, orb(fol(["O2", "X2", "O5"], 0.6, 0.1, [0.0, 0.2]), 13.8, 56, 26, 46), "inOut"),
           key(d, orb(fol(["O2", "X2", "O5"], 0.6, 0.1, [0.5, 0.3]), 13.6, 58, 26, 46), "inOut")]
    shots.append({"id": "sell", "name": "The big catches up top; the guard sprints toward him, his defender follows", "at": cuts["sell"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "ballPath", "src": "O1", "dst": "O5", "color": WHITE, "draw": 0.3, "from": inv(rm, A["entry"]) - 0.05, "to": inv(rm, A["bigCatch"]) + 0.3},
                          {"type": "route", "player": "O2", "t0": A["sprint"], "t1": A["plant"], "color": GOLD, "width": 0.1, "draw": 0.4, "consume": True, "from": tg_, "to": d},
                          trail("O2", tg_ + 0.3, d), trail("X2", tf, d, 0.6)],
                  "screen": [pin("O5", "BIG", tb + 0.2, tg_, "white", 38), pin("O2", "SELL IT", tg_ + 0.3, tf, "gold", 40),
                             pin("X2", "TRAIL", tf + 0.1, d, "white", 38)]})

    # 4 FEET (B defender POV -> low push to the feet, slow motion): the sideways expectation, the wrong plant
    d = dur["feet"]
    tw = L("feet", "feet")
    rm = [[0, A["show"] + 0.32], [tw, A["plant"] - 0.05], [d, A["plant"] + 0.12]]
    cam = [key(0, {"type": "pov", "behind": "X2", "look": "O5", "back": 2.4, "height": 1.85, "fov": 52, "lookZ": 1.2}),
           key(tw - 0.6, {"type": "pov", "behind": "X2", "look": "O5", "back": 2.2, "height": 1.75, "fov": 50, "lookZ": 1.1}, "inOut"),
           key(tw + 0.15, orb(fol("X2", 0.35), 3.9, 62, 28, 44), "inOut"),
           key(d, orb(fol("X2", 0.35), 3.7, 62, 24, 44))]
    shots.append({"id": "feet", "name": "He thinks the ball's coming sideways. WATCH HIS FEET.", "at": cuts["feet"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "passLane", "src": "O5", "dst": [-2.55, 7.6], "color": WHITE, "from": 0.4, "to": tw - 0.1},
                          {"type": "footRing", "player": "X2", "foot": "L", "color": RED, "r": 0.28, "from": tw - 0.05, "to": d},
                          {"type": "hipMark", "player": "X2", "color": RED, "from": tw + 0.4, "to": d}],
                  "screen": [chip("HE EXPECTS THE HANDOFF", 0.35, tw - 0.1, "red", 470, 54),
                             chip("WEIGHT ON THE WRONG FOOT", tw + 0.2, d, "red", 470, 54)]})

    # 5 CUT (C orbit on the plant -> E finish cam): no handoff, back cut, open lane, ONE freeze, pass, layup
    d = dur["cut"]
    tn, tsl, tk = L("nohand", "cut"), L("slips", "cut"), L("takes", "cut")
    tfin = Lw("takes", 3, "cut")
    FZ0 = Lw("slips", 3, "cut") + 0.25                                 # after "behind him,": X2 is beaten
    fzp = A["x2turn"] + 0.18
    rm = [[0, A["plant"] + 0.12], [tsl, A["cut"] + 0.12], [FZ0, fzp], [FZ0 + 0.55, fzp], [tk + 0.55, A["pass"] + 0.1],
          [tfin + 0.2, A["finish"] + 0.05], [d - 0.4, A["make"] + 0.3], [d, A["make"] + 0.6]]
    cam = [key(0, orb(fol(["O2", "O5"], 1.0), 6.5, 62, 34, 46)),
           key(tsl, orb(fol(["O2", "X2"], 1.0), 6.6, 62, -8, 46), "inOut", True),         # dynamic orbit on the plant
           key(FZ0, orb(fol(["O2", "X2"], 0.9), 7.2, 58, -14, 46), "out"),
           key(FZ0 + 0.55, orb(fol(["O2", "X2"], 0.9), 7.2, 58, -14, 46)),
           key(tk + 0.6, orb(fol("O2", 1.1, 0.2), 6.6, 64, -24, 48), "inOut"),            # cinematic finish: with the cutter
           key(d, orb([-0.5, 2.4, 1.6], 6.4, 66, -28, 48), "inOut")]
    shots.append({"id": "cut", "name": "But there's NO HANDOFF! The cutter slips behind him, takes the pass, and finishes.", "at": cuts["cut"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [trail("O2", tsl - 0.3, tk + 0.6), trail("X2", tsl, FZ0 + 0.55, 0.5),
                          {"type": "openLane", "anchor": "X2", "target": RIM_LANE, "width": 1.6, "tip": 0.8, "draw": 0.5, "from": inv(rm, A["x2turn"]) - 0.05, "to": tk + 0.5},
                          {"type": "separation", "a": "X2", "b": "O2", "color": GOLD, "from": FZ0 + 0.03, "to": FZ0 + 0.55},
                          {"type": "ballPath", "src": "O5", "dst": "O2", "color": GOLD, "draw": 0.25, "from": inv(rm, A["pass"]) - 0.1, "to": inv(rm, A["catch"]) + 0.35},
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.5, "from": tfin, "to": d}],
                  "screen": [{"type": "flash", "color": "#FFE9C8", "strength": 0.12, "from": tn - 0.05, "to": tn + 0.15},
                             chip("NO HANDOFF", tn, tsl, "red", 470, 64),
                             {"type": "freeze", "from": FZ0, "to": FZ0 + 0.55},
                             pin("O2", "BACK CUT", tsl + 0.2, FZ0 + 0.55, "gold", 40),
                             chip("LAYUP.", tfin + 0.3, d, "gold", 470, 72)]})

    # 6 REPLAY (D top-down, play B): three phases; the low help starts to react
    d = dur["replay"]
    t2, t3 = L("r2", "replay"), L("r3", "replay")
    rw = 0.4
    rm = [[0, A["make"] + 0.6], [rw, B["sprint"]], [t2, B["plant"]], [t3, B["x2turn"]], [d, B["help"] + 0.55]]
    shots.append({"id": "replay", "name": "Sell the handoff, cut behind the defender, force the low help to choose", "at": cuts["replay"], "play": "B",
                  "remap": rm, "camera": [key(0, orb([-1.8, 5.4, 0.0], 16.5, 34, 0, 50)), key(t3 - 0.3, orb([-1.8, 5.2, 0.0], 16.0, 34, 0, 50), "inOut"),
                                         key(d, orb([0.9, 4.0, 0.0], 18.5, 36, 0, 50), "inOut")],
                  "ov3": [{"type": "route", "player": "O2", "t0": B["sprint"], "t1": B["plant"], "color": GOLD, "width": 0.1, "draw": 0.35, "from": rw, "to": d},
                          {"type": "route", "player": "O2", "t0": B["cut"], "t1": B["kick"], "color": GOLD, "width": 0.1, "draw": 0.35, "from": t2, "to": d},
                          trail("X2", rw, t3, 0.6),
                          {"type": "marker", "player": "X3", "team": "defense", "from": t3 - 0.1, "to": d},
                          trail("X3", t3 + 0.2, d, 0.6)],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             {"type": "step", "n": 1, "text": "SELL THE HANDOFF", "from": rw, "to": t2, "y": 430},
                             {"type": "step", "n": 2, "text": "CUT BEHIND", "from": t2, "to": t3, "y": 430},
                             {"type": "step", "n": 3, "text": "MAKE THE HELP CHOOSE", "from": t3, "to": d, "y": 430},
                             pin("X3", "LOW HELP", t3 + 0.3, d, "white", 38)]})

    # 7 READ 2 (three-quarter from the weak side): the help steps across, corner open, skip pass, three
    d = dur["read2"]
    to_, tfc, tkk = L("open", "read2"), L("force", "read2"), L("kick", "read2")
    rm = [[0, B["help"] + 0.55], [to_, B["help"] + 1.0], [tkk, B["kick"]], [tkk + 0.95, B["catch"] + 0.1], [d - 0.35, B["make"]], [d, B["make"] + 0.15]]
    cam = [key(0, orb([2.7, 4.3, 0.0], 19.5, 36, 0, 48)), key(tkk - 0.2, orb([2.9, 4.1, 0.0], 19.0, 36, -4, 48), "inOut"),
           key(d, orb([3.8, 3.2, 0.3], 16.0, 42, -10, 48), "inOut")]
    shots.append({"id": "read2", "name": "If that help steps across, the corner is open. Don't force the layup, kick it out.", "at": cuts["read2"], "play": "B",
                  "remap": rm, "camera": cam,
                  "ov3": [trail("X3", 0.0, to_ + 0.3, 0.6),
                          {"type": "marker", "player": "X3", "team": "defense", "from": 0.0, "to": d},
                          {"type": "glow", "at": [6.6, 1.25], "r": 1.4, "color": GOLD, "strength": 0.55, "from": to_, "to": d},
                          {"type": "passLane", "src": "O5", "dst": "O2", "color": RED, "from": tfc - 0.05, "to": tkk},
                          {"type": "blocked", "at": [-0.7, 3.0], "color": RED, "from": tfc + 0.15, "to": tkk + 0.2},
                          {"type": "ballPath", "src": "O5", "dst": "O3", "color": GOLD, "draw": 0.3, "from": inv(rm, B["kick"]) - 0.1, "to": inv(rm, B["catch"]) + 0.4}],
                  "screen": [pin("X3", "STEPS ACROSS", 0.2, to_, "white", 38),
                             pin("O3", "OPEN", to_ + 0.1, d, "gold", 44),
                             chip("CORNER IS OPEN", to_ + 0.2, tfc, "gold", 470, 62),
                             chip("KICK IT OUT", tkk, d, "gold", 470, 64)]})

    # 8-10 CLOSE: same action (frozen at the plant) -> read 1 layup -> read 2 corner three -> BASKETBALL IQ + logo
    d = dur["same"]
    shots.append({"id": "same", "name": "Same action.", "at": cuts["same"], "play": "A", "remap": [[0, A["plant"]], [d, A["plant"]]],
                  "camera": [key(0, orb([-1.4, 6.6, 0.6], 11.0, 44, 12, 48)), key(d, orb([-1.4, 6.6, 0.6], 10.4, 44, 8, 48), "inOut")],
                  "ov3": [{"type": "footRing", "player": "X2", "foot": "L", "color": RED, "r": 0.26, "from": 0.0, "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d}, chip("SAME ACTION", 0.05, d, "gold", 470, 66)]})
    d = dur["twoA"]
    shots.append({"id": "twoA", "name": "Two reads (1): layup", "at": cuts["twoA"], "play": "A", "remap": [[0, A["finish"] + 0.1], [d, A["finish"] + 0.25]],
                  "camera": [key(0, orb([-0.6, 2.6, 1.3], 7.2, 64, -24, 48))],
                  "ov3": [{"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.5, "from": 0.0, "to": d}],
                  "screen": [chip("READ 1 · LAYUP", 0.0, d, "gold", 470, 60)]})
    d = dur["twoB"]
    shots.append({"id": "twoB", "name": "Two reads (2): corner three", "at": cuts["twoB"], "play": "B", "remap": [[0, B["release"] - 0.1], [d, B["release"] + 0.35]],
                  "camera": [key(0, orb([6.0, 1.7, 1.3], 7.8, 64, -40, 48))],
                  "ov3": [{"type": "glow", "at": [6.6, 1.25], "r": 1.3, "color": GOLD, "strength": 0.55, "from": 0.0, "to": d}],
                  "screen": [chip("READ 2 · CORNER", 0.0, d, "white" if trial else "blue", 470, 60)]})
    d = dur["iq"]
    shots.append({"id": "iq", "name": "That's BASKETBALL IQ. (logo)", "at": cuts["iq"], "play": "B",
                  "remap": [[0, B["make"] - 0.25], [d, B["end"]]], "camera": [key(0, TOPB), key(d, orb([0.5, 5.0, 0.0], 23.0, 30, 0, 50), "inOut")],
                  "ov3": [], "screen": [ttl(["BASKETBALL", "IQ"], [1], 0.05, d, 250, 120), {"type": "logo", "big": False, "from": 0.35, "to": d}]})
    # 11 LOOP: back to the hook's first frame (tracking O2/X2 at play HOOK0) so the reel loops on itself
    d = dur["loop"]
    hk = shots[0]["camera"][0]["rig"]
    shots.append({"id": "loop", "name": "Loop ending: the hook's opening frame", "at": cuts["loop"], "play": "A",
                  "remap": [[0, HOOK0 - 0.55], [d, HOOK0]], "camera": [key(0, hk)],
                  "ov3": [trail("O2", 0.0, d), trail("X2", 0.0, d, 0.6)], "screen": []})
    for s in shots:
        for it in s["screen"]:
            if it["type"] == "chip" and it["tone"] == "white":
                it["tone"] = "blue"
    ep = {
        "id": "zero-cut" + ("-trial" if trial else ""), "title": "THE ZERO CUT", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33", "words": words,
        "subtitleGroups": [len(t.split()) for _, t in LINES],
        "subtitleBlock": True, "subtitleY": 1390, "subtitleHide": [[0.0, cuts["name"]], [cuts["iq"], 999]],
        "keywords": ["NEVER", "PRO", "READ", "ZERO", "CUT.", "handoff.", "sprints", "follows.", "sideways.", "WATCH", "HIS", "FEET.",
                     "NO", "HANDOFF!", "behind", "finishes.", "handoff,", "low", "help", "choose.", "CORNER", "IS", "OPEN.",
                     "kick", "out.", "Two", "reads."],
        "gradeBottom": 0.3, "shots": shots, "plays": PL,
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    return {"episode": ep}, {"duration": t_end, "cuts": {k: round(v, 3) for k, v in cuts.items()}, "dur": dur}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words", default=os.path.join(D, "zerocut", "zerocut-voice.words.json"))
    ap.add_argument("--voice", default="zerocut/voice-final.wav")
    ap.add_argument("--music")
    ap.add_argument("--fit")
    ap.add_argument("--trial", action="store_true")
    a = ap.parse_args()
    words = json.load(open(a.words))
    props, meta = build(words, a.voice, a.music, a.trial)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"])
        ep["plays"] = {k: v["id"] for k, v in PL.items()}
        json.dump(ep, open(a.fit, "w"))
        json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    print(json.dumps(meta))
