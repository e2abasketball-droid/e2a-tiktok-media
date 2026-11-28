#!/usr/bin/env python3
"""E2A BASKETBALL IQ 02 - BEAT THE BLITZ **V2** (owner directive 2026-11-27 23:33Z "Elite 3D animation & cinematic
production overhaul", E2A Basketball Motion Engine V4). Edit generator; V1 (_gen-iq02.py) is untouched.
Play: tactical/plays/iq02-beat-the-blitz-v2.json (same owner keyframes, V4 motion layers; tools/iq_play_validate.py PASS,
tools/motion/motion_validate.py). Same Nathaniel take as V1 (never regenerated). V2 changes vs V1: env 'arena' (fixed
overhead arena light), the X4 reveal re-shot (isolate X4 -> help -> he loses O4 -> track the cutter -> passing window),
the finish slowed x0.5 on the gather / take-off / release from a low weak-side camera, cleaner graphics (world-space
passing lane on the floor instead of a screen chip; Render B review removed a separation ring: too much on screen).
Narrator: Nathaniel (eleven_v4), one fresh take (tactical/episodes/iq02/_voice-iq02.py). 10 shots:
 01 HOOK      the trap closes ("They send TWO at the ball!")           - 2 ON THE BALL only while the validator says so
 02 BLITZ     the outlet leaves O1 before the trap closes
 03 RELEASE   O5 catches the short roll ("Four on three")               - 4 ON 3 only while true
 04 PROBLEM   "Looks easy... until the help moves." (X4 starts moving)
 05 FREEZE    "Drive? Corner? Or cut?" A/B/C + the honest 2.0 s decision window
 06 WHY A     the drive line runs into X4 (BLOCKED)
 07 WHY B     X3 never left the corner (lane BLOCKED)
 08 REVEAL    rewind; X4 steps into the paint and loses the cutter (vision cone, O4's 45 cut, lane OPEN)
 09 FINISH    "THERE'S the pass!" bounce pass around X4, layup
 10 LESSON    "Read the help. Attack the space it leaves." + "Did you see it?" + loop to the hook frame
Every graphic that makes a basketball claim is clipped to the validator's truth window (gate()).
  python3 tactical/episodes/_gen-iq02.py --out props.json [--voice p] [--music p] [--fit ep.json] [--plan plan.json] [--env cinema]"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PLAY = json.load(open(os.path.join(T, "tactical", "plays", "iq02-beat-the-blitz-v2.json")))
VAL = json.load(open(os.path.join(D, "iq02v2", "validation", "iq02v2-tactical-validation.json")))
CAN = json.load(open(os.path.join(T, "tactical", "iq02", "basketball_iq_02_blitz_short_roll.json")))
OFF = CAN["coordinates"]["engine_offset_s"]
PL = {"A": PLAY}
M = PLAY["marks"]
FZ = M["freeze"]
GOLD, NAVY, WHITE, RED, GREEN = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A", "#3BC46B"
TRUTH = {k: [[a + OFF, b + OFF] for a, b in v] for k, v in VAL["truth_windows_owner_s"].items()}   # engine play time
E = lambda p: [round(-p[0], 3), p[1]]           # owner -> engine
KF = {k["k"]: k for k in CAN["keyframes"]}
X4_FZ = E(KF["K3"]["X4"])
HOOK_T0 = 1.30                                   # play time of frame 0 (X5 jumping out of the screen; loop target)

LINES = [("hook", "They send two at the ball!"), ("roll", "Your big catches the short roll."), ("four", "Four on three."),
         ("easy", "Looks easy... until the help moves."), ("q", "Drive? Corner? Or cut?"), ("a", "Drive? The help is already there."),
         ("b", "Corner? His defender never left."), ("watch", "Now watch the weak-side defender."), ("paint", "He steps into the paint..."),
         ("loses", "and loses the cutter!"), ("pass", "There's the pass!"), ("read", "Read the help."), ("attack", "Attack the space it leaves."),
         ("see", "Did you see it?")]
THINK = (10.88, 12.88)                           # the 2.0 s silence inserted after "Or cut?" (_voice-iq02.py)


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
fol = lambda ids, z=1.0, lead=0.0, win=0.45: {"follow": ids, "z": z, "lead": lead, "window": win}
key = lambda at, rig, ease=None: {"at": round(at, 3), "rig": rig, **({"ease": ease} if ease else {})}
r3 = lambda x: round(x, 3)

# camera library (engine coordinates; yaw 0 = behind the top of the key, basket at the top of the frame)
HOOKCAM = orb(fol(["O1", "X1", "X5"], 1.0), 6.4, 70, 20, 50)        # low, behind the ball handler, into the trap
TRAPWIDE = orb(fol(["O1", "X1", "X5", "O5"], 0.8), 9.5, 60, 15, 56)
ROLLCAM = orb([-0.9, 6.6, 0.4], 12.5, 52, 10, 62)                  # the outlet and the catch at the nail
WIDE = orb([0.4, 5.9, 0.0], 17.2, 44, 0, 82)                        # all 10 players (4 on 3 + the trap)
DECIDE = orb([0.6, 5.2, 0.0], 16.8, 42, 0, 84)
DEC_LO = orb([0.6, 5.1, 0.0], 16.2, 48, -5, 84)
WHY_A = (orb([-0.4, 4.6, 0.8], 7.6, 64, 8, 52), orb([-0.3, 4.4, 0.8], 7.0, 62, 2, 50))   # behind O5, X4 on the line
WHY_B = (orb([3.4, 4.0, 0.5], 11.0, 54, 62, 56), orb([4.2, 3.6, 0.5], 10.0, 55, 70, 54))  # O5 -> O3, X3 home
WEAK = orb([1.4, 4.6, 0.5], 11.5, 54, -42, 58)                       # weak side: X4 and O4
WEAK_CLOSE = orb([0.9, 4.2, 0.6], 9.2, 58, -48, 54)
FIN0 = orb(fol(["O5", "O4", "X4"], 0.9), 10.0, 56, -30, 56)
FIN1 = orb(fol(["O4"], 1.1), 7.4, 64, -68, 52)                       # from the weak-side wing, the layup (stanchion off frame)
TOP = orb([0.6, 5.4, 0.0], 17.2, 10, 0, 78)
# V2 reveal + finish rigs (weak side = engine +x; yaw < 0 looks from the weak side, as V1 WEAK / FIN1)
X4ISO = orb(fol(["X4"], 1.0), 6.6, 60, -38, 48)                     # isolate X4 (his eyes on the ball)
X4ISO2 = orb(fol(["X4", "O5"], 0.9), 7.6, 58, -30, 50)              # X4 steps in, the ball handler in frame
CUTCAM = orb(fol(["O4", "X4"], 1.0, 0.15), 8.6, 58, -52, 54)       # O4 behind X4: the separation grows
WINDOW = orb(fol(["O5", "O4", "X4"], 0.9), 10.2, 56, -40, 56)      # the passing window O5 -> O4
FINLOW = orb([0.35, 2.4, 1.25], 7.4, 74, -70, 50)                  # low weak-side wing: gather, take-off, release, glass
FINEND = orb([0.3, 2.1, 1.5], 6.6, 77, -76, 48)


def inv(remap, pt):
    for (a, pa), (b, pb) in zip(remap, remap[1:]):
        if pa <= pt <= pb and pb > pa:
            return a + (b - a) * (pt - pa) / (pb - pa)
    raise ValueError(pt)


def ptime(remap, et):
    for (a, pa), (b, pb) in zip(remap, remap[1:]):
        if a <= et <= b:
            return pa + (pb - pa) * (et - a) / max(1e-9, b - a)
    return remap[-1][1] if et > remap[-1][0] else remap[0][1]


def gate(name, remap, fr, to):
    """clip an edit interval [fr, to] to where the claim `name` is TRUE in play time (validator truth window)"""
    ok = [et / 30 for et in range(int(fr * 30), int(to * 30) + 1) if any(a <= ptime(remap, et / 30) <= b for a, b in TRUTH[name])]
    assert ok, f"claim {name} is never true in [{fr}, {to}]"
    return r3(max(fr, ok[0])), r3(min(to, ok[-1]))


ttl = lambda lines, gold, fr, to, y=250, size=110, **kw: {"type": "title", "lines": lines, "gold": gold, "reveal": "mask", "from": r3(fr), "to": r3(to), "y": y, "size": size, **kw}
chip = lambda text, fr, to, tone="gold", y=330, size=60: {"type": "chip", "text": text, "tone": tone, "align": "center", "size": size, "from": r3(fr), "to": r3(to), "y": y}
pin = lambda p, text, fr, to, tone="gold", size=46: {"type": "pin", "player": p, "text": text, "tone": tone, "from": r3(fr), "to": r3(to), "size": size}
trail = lambda p, fr, to, ln=0.7: {"type": "motionTrail", "player": p, "len": ln, "color": GOLD if p[0] == "O" else RED, "from": r3(fr), "to": r3(to)}
mk = lambda p, fr, to: {"type": "marker", "player": p, "team": "attack" if p[0] == "O" else "defense", "from": r3(fr), "to": r3(to)}
lane = lambda src, dst, col, fr, to, w=1.6: {"type": "passLane", "src": src, "dst": dst, "color": col, "w": w, "from": r3(fr), "to": r3(to)}
focus = lambda p, fr, to, r=240, st=0.6: {"type": "focus", "player": p, "r": r, "strength": st, "from": r3(fr), "to": r3(to)}
LET = {"A": "O5", "B": "O3", "C": "O4"}


def letter(L, fr, to, wrong=None, right=None, size=100):
    it = {"type": "letter", "player": LET[L], "text": L, "from": r3(fr), "to": r3(to), "size": size, "z": 2.3}
    if wrong is not None:
        it["wrong"] = r3(wrong)
    if right is not None:
        it["right"] = r3(right)
    return it


def build(words, voice, music, env):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    t_end = r3(e0("see") + 2.3)
    cuts = {"hook": 0.0, "roll": s0("roll") - 0.25, "easy": s0("easy") - 0.3, "freeze": s0("q") - 0.12, "a": s0("a") - 0.12,
            "b": s0("b") - 0.15, "reveal": e0("b") + 0.35, "pass": s0("pass") - 0.12, "lesson": s0("read") - 0.35, "end": e0("attack") + 0.3}
    order = list(cuts)
    dur = {k: r3((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k]) for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    Lw = lambda k, i, sh: wd(k, i) - cuts[sh]
    Ee = lambda k, sh: e0(k) - cuts[sh]
    shots = []

    # 01 HOOK + 02 BLITZ: the trap closes, the outlet leaves before it shuts -------------------------------------------
    d = dur["hook"]
    tball = Lw("hook", 5, "hook")                         # "ball!"
    rm = [[0, HOOK_T0], [tball, 1.95], [d - 0.35, M["release1"] - 0.02], [d, M["release1"] + 0.12]]
    g0, g1 = gate("two_on_ball", rm, 0.25, d - 0.2)
    shots.append({"id": "hook", "name": "01 HOOK + 02 BLITZ: They send TWO at the ball! (trap closes, outlet recognised)", "at": 0.0, "play": "A",
                  "remap": rm, "camera": [key(0, HOOKCAM), key(tball + 0.2, orb(fol(["O1", "X1", "X5"], 1.0), 7.4, 66, 16, 52), "inOut"),
                                          key(d, TRAPWIDE, "inOut")],
                  "ov3": [mk("X1", 0.15, d + 0.4), mk("X5", 0.25, d + 0.4), mk("O1", 0.0, d + 0.4), trail("X5", 0.0, d, 0.6),
                          {"type": "lockRing", "player": "O1", "color": RED, "size": 1.25, "from": g0, "to": g1}],
                  "screen": [{"type": "stamp", "text": "BASKETBALL IQ", "badge": "EP 02", "tone": "gold", "y": 110, "instant": True, "from": 0.0, "to": r3(d)},
                             {**ttl(["2 ON", "THE BALL"], [1], g0, g1, 250, 116), "noOut": False},
                             pin("X5", "BLITZ", g0 + 0.2, d - 0.05, "red", 44)]})

    # 03 RELEASE: the outlet, the short roll, 4 ON 3 ------------------------------------------------------------------
    d = dur["roll"]
    tcatch = Lw("roll", 2, "roll")                        # "catches"
    tfour = L("four", "roll")
    rm = [[0, M["release1"] + 0.12], [tcatch + 0.12, M["catch1"]], [tfour, M["faceup"] + 0.1], [d, M["faceup"] + 0.32]]
    f0, f1 = gate("four_on_three", rm, tfour - 0.1, d + 0.0)
    shots.append({"id": "roll", "name": "03 RELEASE: Your big catches the short roll. Four on three.", "at": cuts["roll"], "play": "A", "remap": rm,
                  "camera": [key(0, TRAPWIDE), key(tcatch, ROLLCAM, "inOut"), key(d, WIDE, "inOut")],
                  "ov3": [{"type": "ballPath", "src": "O1", "dst": "O5", "color": GOLD, "draw": 0.25, "from": 0.0, "to": r3(tcatch + 0.4)},
                          mk("O5", 0.0, d + 0.3), trail("O5", 0.0, tcatch + 0.3, 0.7),
                          mk("X1", 0.0, d + 0.3), mk("X5", 0.0, d + 0.3),
                          *[mk(p, f0, d + 0.3) for p in ("O2", "O3", "O4", "X2", "X3", "X4")]],
                  "screen": [pin("O5", "SHORT ROLL", 0.15, tfour - 0.1, "gold", 46),
                             {**ttl(["4 ON 3"], [0], f0, f1, 250, 128), "noOut": False},
                             chip("2 STUCK ON THE BALL", f0 + 0.25, f1, "red", 340, 50)]})

    # 04 PROBLEM: looks easy... until the help moves --------------------------------------------------------------------
    d = dur["easy"]
    thelp = Lw("easy", 4, "easy")                         # "help"
    rm = [[0, M["faceup"] + 0.32], [thelp - 0.2, 3.05], [d, FZ - 0.03]]
    pa0, pa1 = gate("x4_in_paint", rm, thelp, d)
    shots.append({"id": "easy", "name": "04 PROBLEM: Looks easy... until the help moves.", "at": cuts["easy"], "play": "A", "remap": rm,
                  # pass 2 (critical review of v1): the wide hold read small on a phone; push in on the paint as the help moves
                  "camera": [key(0, WIDE), key(thelp - 0.3, orb([0.2, 5.2, 0.0], 13.5, 46, -6, 74), "inOut"), key(d - 0.15, DECIDE, "inOut")],
                  "ov3": [*[mk(p, 0.0, d + 0.3) for p in ("O5", "O2", "O3", "O4", "X2", "X3")], mk("X4", thelp - 0.25, d + 0.3),
                          trail("X4", thelp - 0.3, d, 0.6)],
                  "screen": [chip("LOOKS EASY", L("easy", "easy") - 0.05, thelp - 0.15, "gold", 330, 64),
                             pin("X4", "HELP", thelp - 0.05, pa0 if pa0 > thelp + 0.3 else d, "red", 46),
                             *([pin("X4", "IN THE PAINT", pa0, d, "red", 44)] if pa0 > thelp + 0.3 else [])]})

    # 05 FREEZE: Drive? Corner? Or cut? + the 2.0 s decision ----------------------------------------------------------
    d = dur["freeze"]
    tq = [Lw("q", i, "freeze") for i in (0, 1, 3)]
    t0, t1 = THINK[0] - cuts["freeze"], THINK[1] - cuts["freeze"]
    rm = [[0, FZ - 0.03], [0.12, FZ], [d, FZ]]
    four_end = gate("four_on_three", rm, 0.0, d)[1]
    shots.append({"id": "freeze", "name": "05 FREEZE: Drive? Corner? Or cut? (2.0 s decision window)", "at": cuts["freeze"], "play": "A", "remap": rm,
                  "camera": [key(0, DECIDE), key(t0, DECIDE, "inOut"), key(d, DEC_LO, "inOut")],
                  "ov3": [mk("O5", 0.0, d + 0.3), mk("O3", tq[1], d + 0.3), mk("O4", tq[2], d + 0.3), mk("X4", 0.0, d + 0.3), mk("X3", tq[1], d + 0.3),
                          lane("O5", [0.0, 1.575], WHITE, tq[0] + 0.05, d + 0.3), lane("O5", "O3", WHITE, tq[1] + 0.05, d + 0.3),
                          lane("O5", E(KF["K4"]["O4"]), WHITE, tq[2] + 0.05, d + 0.3)],
                  "screen": [{"type": "freeze", "from": 0.12, "to": r3(d)}, {"type": "punch", "amount": 0.035, "from": 0.12, "to": 0.42},
                             letter("A", tq[0], d + 0.3), letter("B", tq[1], d + 0.3), letter("C", tq[2], d + 0.3),
                             {**ttl(["DRIVE? CORNER?", "OR CUT?"], [1], tq[0] - 0.05, t0 - 0.05, 250, 104), "noOut": False},
                             chip("4 ON 3", 0.1, min(four_end, tq[0] - 0.1), "gold", 330, 56),
                             {"type": "countdown", "label": "MAKE YOUR CALL", "from": r3(t0), "to": r3(t1), "y": 250}]})

    # 06 WHY A: the drive runs into X4 -----------------------------------------------------------------------------------
    d = dur["a"]
    tth = Lw("a", 2, "a")                                 # "help"
    shots.append({"id": "a", "name": "06 WHY A: Drive? The help is already there.", "at": cuts["a"], "play": "A", "remap": [[0, FZ], [d, FZ]],
                  "camera": [key(0, DEC_LO), key(0.55, WHY_A[0], "inOut"), key(d, WHY_A[1], "inOut")],
                  "ov3": [mk("O5", 0.0, d), mk("X4", tth - 0.2, d), lane("O5", [0.0, 1.575], WHITE, 0.0, tth - 0.05),
                          lane("O5", [0.0, 1.575], RED, tth - 0.05, d), {"type": "blocked", "at": X4_FZ, "color": RED, "from": r3(tth + 0.1), "to": r3(d)}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": r3(d)}, letter("A", 0.0, d, wrong=tth + 0.15),
                             pin("X4", "IN THE LANE", tth - 0.05, d, "red", 46), chip("DRIVE: BLOCKED", tth + 0.25, d, "red", 330, 58)]})

    # 07 WHY B: X3 never left the corner -----------------------------------------------------------------------------------
    d = dur["b"]
    tdef = Lw("b", 2, "b")                                # "defender"
    tleft = Lw("b", 4, "b")                               # "left."
    shots.append({"id": "b", "name": "07 WHY B: Corner? His defender never left.", "at": cuts["b"], "play": "A", "remap": [[0, FZ], [d, FZ]],
                  "camera": [key(0, WHY_A[1]), key(0.6, WHY_B[0], "inOut"), key(d, WHY_B[1], "inOut")],
                  "ov3": [mk("O3", 0.0, d), mk("X3", tdef - 0.15, d), lane("O5", "O3", WHITE, 0.0, tleft - 0.05), lane("O5", "O3", RED, tleft - 0.05, d),
                          {"type": "separation", "a": "X3", "b": "O3", "color": RED, "from": r3(tdef), "to": r3(d)}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": r3(d)}, letter("B", 0.0, d, wrong=tleft + 0.1),
                             pin("X3", "STILL HOME", tdef, d, "red", 46), chip("CORNER: COVERED", tleft + 0.1, d, "red", 330, 58)]})

    # 08 REVEAL: rewind, X4 steps into the paint and loses the cutter ----------------------------------------------------
    d = dur["reveal"]
    rw = 0.4
    twatch = Lw("watch", 3, "reveal")                     # "weak-side"
    tpaint = Lw("paint", 4, "reveal")                     # "paint..."
    tloses = Lw("loses", 1, "reveal")                     # "loses"
    tcut = Lw("loses", 3, "reveal")                       # "cutter!"
    rm = [[0, FZ], [rw, M["outlet"] - 0.1], [twatch, M["catch1"] - 0.05], [tpaint + 0.2, FZ], [tloses, FZ + 0.12], [d, M["release2"] - 0.04]]
    pa0, _ = gate("x4_in_paint", rm, twatch, d)
    shots.append({"id": "reveal", "name": "08 REVEAL: Now watch the weak-side defender. He steps into the paint... and LOSES the cutter!",
                  "at": cuts["reveal"], "play": "A", "remap": rm,
                  "camera": [key(0, WHY_B[1]), key(rw + 0.15, X4ISO, "inOut"), key(tpaint - 0.2, X4ISO2, "inOut"),
                             key(tloses + 0.1, CUTCAM, "inOut"), key(d, WINDOW, "inOut")],
                  "ov3": [mk("X4", rw, d + 0.3), trail("X4", rw + 0.2, tpaint + 0.3, 0.7),
                          {"type": "lockRing", "player": "X4", "color": RED, "size": 1.0, "from": r3(L("watch", "reveal")), "to": r3(twatch + 1.1)},
                          {"type": "ghost", "player": "X4", "t": KF["K0"]["t"] + OFF, "color": RED, "link": True, "from": r3(tpaint - 0.3), "to": r3(d + 0.3)},
                          {"type": "vision", "player": "X4", "man": "O4", "split": 100, "len": 2.6, "from": r3(tpaint - 0.1), "to": r3(d + 0.3)},
                          mk("O4", tloses - 0.3, d + 0.3), trail("O4", tloses - 0.2, d + 0.3, 0.8),
                          {"type": "route", "player": "O4", "t0": FZ, "t1": M["catch2"], "color": GOLD, "draw": 0.45, "width": 0.16, "consume": True,
                           "from": r3(tloses - 0.25), "to": r3(d + 0.3)},
                          {"type": "openSpace", "at": E([-1.55, 3.0]), "r": 1.2, "color": GOLD, "from": r3(tcut - 0.1), "to": r3(d + 0.3)},
                          lane("O5", "O4", GREEN, tcut + 0.25, d + 0.3, 1.8)],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw}, focus("X4", L("watch", "reveal") - 0.1, tloses, 250, 0.6),
                             pin("X4", "WEAK-SIDE HELP", twatch, tpaint - 0.15, "red", 44),
                             pin("X4", "IN THE PAINT", max(pa0, tpaint - 0.1), tloses - 0.05, "red", 44),
                             pin("O4", "CUTTER", tloses + 0.05, d + 0.3, "gold", 46),
                             {**ttl(["LOSES THE", "CUTTER!"], [1], tloses - 0.05, d + 0.2, 250, 112), "noOut": False}]})

    # 09 FINISH: THERE'S the pass! bounce pass around X4, layup -----------------------------------------------------------
    d = dur["pass"]
    tp = L("pass", "pass")
    # V2: the gather -> take-off -> release -> glass runs at x0.5 (0.7 s of play in 1.4 s), then real time to the make
    rm = [[0, M["release2"] - 0.04], [tp - 0.02, M["release2"] - 0.02], [tp + 0.58, M["catch2"]], [tp + 1.98, M["layup"] + 0.05],
          [tp + 2.6, M["make"] + 0.02], [d, min(PLAY["duration"], M["make"] + 0.4)]]
    t_catch, t_make = inv(rm, M["catch2"]), inv(rm, M["make"])
    shots.append({"id": "pass", "name": "09 FINISH: THERE'S the pass! (bounce pass around X4, layup)", "at": cuts["pass"], "play": "A", "remap": rm,
                  "camera": [key(0, WINDOW), key(tp + 0.2, FIN0, "inOut"), key(t_catch + 0.15, FINLOW, "inOut"), key(d, FINEND, "inOut")],
                  "ov3": [{"type": "ballPath", "src": "O5", "dst": "O4", "color": GOLD, "draw": 0.25, "from": r3(tp), "to": r3(t_catch + 0.35)},
                          lane("O5", "O4", GREEN, 0.0, tp + 0.2, 1.8), mk("O4", 0.0, t_make), mk("X4", 0.0, t_catch + 0.3),
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.6, "from": r3(t_make), "to": r3(d)}],
                  "screen": [letter("C", 0.0, t_catch, right=0.15), pin("O4", "OPEN", 0.05, tp + 0.5, "gold", 46),
                             {"type": "stamp", "text": "x0.5", "tone": "gold", "y": 110, "instant": True, "from": r3(t_catch + 0.05), "to": r3(inv(rm, M["layup"] + 0.05))},
                             chip("LAYUP.", t_make + 0.05, d, "gold", 330, 84)]})

    # 10 LESSON + LOOP ------------------------------------------------------------------------------------------------------
    d = dur["lesson"]
    rw = 0.35
    tatt = L("attack", "lesson")
    rm = [[0, min(PLAY["duration"], M["make"] + 0.55)], [rw, M["catch1"]], [tatt, FZ], [d, FZ + 0.4]]
    shots.append({"id": "lesson", "name": "10 LESSON: Read the help. Attack the space it leaves.", "at": cuts["lesson"], "play": "A", "remap": rm,
                  "camera": [key(0, TOP), key(d, orb([0.6, 5.0, 0.0], 16.6, 14, 0, 78), "inOut")],
                  "ov3": [mk("X4", rw, d + 0.3), {"type": "ghost", "player": "X4", "t": KF["K0"]["t"] + OFF, "color": RED, "link": True, "from": r3(rw + 0.2), "to": r3(d + 0.3)},
                          {"type": "arrow3d", "player": "X4", "t0": KF["K0"]["t"] + OFF, "t1": FZ, "color": RED, "width": 0.15, "draw": 0.5, "from": r3(rw + 0.3), "to": r3(d + 0.3)},
                          {"type": "openSpace", "at": E([-1.55, 3.0]), "r": 1.25, "color": GOLD, "from": r3(tatt), "to": r3(d + 0.3)},
                          {"type": "arrow3d", "player": "O4", "t0": FZ, "t1": M["catch2"], "color": GOLD, "width": 0.16, "draw": 0.5, "from": r3(tatt + 0.15), "to": r3(d + 0.3)}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             ttl(["READ", "THE HELP"], [1], rw - 0.05, tatt - 0.06, 250, 116),
                             ttl(["ATTACK THE SPACE", "IT LEAVES"], [0], tatt - 0.04, d - 0.05, 250, 98)]})
    d = dur["end"]
    tsee = L("see", "end")
    trn = Ee("see", "end") + 0.35
    shots.append({"id": "end", "name": "Did you see it? (rewinds to the hook frame: loop)", "at": cuts["end"], "play": "A",
                  "remap": [[0, FZ + 0.4], [trn, FZ + 0.4], [d, HOOK_T0]],
                  "camera": [key(0, DECIDE), key(trn, DECIDE), key(d, HOOKCAM, "inOut")],
                  "ov3": [mk("O5", 0.0, trn), mk("O3", 0.0, trn), mk("O4", 0.0, trn), mk("X4", 0.0, trn)],
                  "screen": [letter("A", 0.05, trn, wrong=0.06), letter("B", 0.1, trn, wrong=0.11), letter("C", 0.15, trn, right=0.16),
                             ttl(["DID YOU", "SEE IT?"], [1], max(0.0, tsee - 0.15), trn - 0.04, 250, 116),
                             {"type": "rewind", "from": r3(trn), "to": r3(d - 0.4)},
                             {"type": "logo", "big": False, "y": 1600, "from": 0.2, "to": r3(trn)}]})

    kw = ["two", "ball!", "short", "three.", "help", "Drive?", "Corner?", "cut?", "there.", "left.", "weak-side", "paint...", "loses", "cutter!",
          "pass!", "help.", "space", "see"]
    ep = {"id": "iq02-beat-the-blitz-v2", "title": "BEAT THE BLITZ", "fps": 30, "voice": voice, "tail": r3(t_end - words[-1]["end"]),
          "autoSfx": False, "pinV2": True, "env": env, "athleteRenderer": "v33", "words": words,
          "subtitleGroups": [len(t.split()) for _, t in LINES], "subtitleBlock": True, "subtitleCommas": True, "subtitleY": 1400,
          "keywords": kw, "gradeBottom": 0.3, "shots": shots, "plays": PL}
    if music:
        ep["music"] = {"src": music, "volume": 1}
    plan = {"duration": t_end,
            "states": [[0.0, cuts["roll"], "A"], [cuts["roll"], cuts["freeze"], "B"], [cuts["freeze"], THINK[0], "B"], [THINK[0], THINK[1], "BREAK"],
                       [THINK[1], cuts["reveal"], "B"], [cuts["reveal"], cuts["pass"], "A"], [cuts["pass"], cuts["lesson"], "A"],
                       [cuts["lesson"], cuts["end"], "B"], [cuts["end"], t_end + 1, "A"]],
            "releases": [r3(cuts["pass"] + inv(shots[8]["remap"], M["release2"]))], "hits": [r3(cuts["freeze"] + 0.12), r3(cuts["reveal"] + Lw("loses", 1, "reveal"))]}
    meta = {"duration": t_end, "cuts": {k: r3(v) for k, v in cuts.items()}, "think": list(THINK), "plan": plan}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice")
    ap.add_argument("--music")
    ap.add_argument("--fit")
    ap.add_argument("--plan")
    ap.add_argument("--env", default="arena")
    a = ap.parse_args()
    words = json.load(open(os.path.join(D, "iq02", "iq02.words.json")))
    props, meta = build(words, a.voice or "iq02/voice.mix.wav", a.music, a.env)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"]); ep["plays"] = {k: v["id"] for k, v in PL.items()}
        json.dump(ep, open(a.fit, "w")); json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    if a.plan:
        json.dump(meta["plan"], open(a.plan, "w"), indent=1)
    print(json.dumps({k: meta[k] for k in ("duration", "cuts", "think")}))
