#!/usr/bin/env python3
"""E2A SPORTS - CINEMATIC TACTICAL BREAKDOWN: SHUFFLE CUT V1 (owner brief 2026-11-28 09:18Z, production standard
"E2A Elite Basketball Animation V4+"). Edit generator modelled on _gen-iq02v2.py (Motion Engine V4).
Play: tactical/plays/shuffle-cut-v1.json, written by tactical/specs/_gen-shuffle.py from the ONE canonical 5v5 model
tactical/shuffle/e2a_shuffle_cut_v1.json (tools/shuffle_validate.py PASS). Every camera, arrow, label and replay below
reads that play; nothing is animated per shot. Narrator: Nathaniel (eleven_v4), one take (episodes/shuffle/_voice-shuffle.py).
Cameras (brief): A opening close-up, B broadcast wing entry, C low on the screener, D tracking the cutter, E overhead
tactical, F catch + finish, G slow-motion replay. All yaws in [-75, 0]: the basket stays at the top of frame (never flips).
Shots:
 01 HOOK     freeze on the cut (O1 brushing O5, X1 trapped)           ONE SCREEN. ONE CUT.
 02 FULL     the whole play in real time (camera B)                   THE SHUFFLE CUT
 03 SETUP    rewind; ball to the wing; the big man; BACK SCREEN behind X1 (camera B -> C)
 04 CUT      the cutter waits, slow... slow... then explodes (camera D, x0.5 on the burst)
 05 CHASE    slow-motion replay: X1 chases into the screen (camera G)  - claims gated by the validator truth windows
 06 FINISH   pass in stride, layup off the glass (camera F)
 07 RECAP    overhead replay SCREEN / CUT / FINISH, TIMING > SPEED, close + logo (camera E)
  python3 tactical/episodes/_gen-shuffle.py --out props.json [--voice p] [--music p] [--fit ep.json] [--env arena]"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PLAY = json.load(open(os.path.join(T, "tactical", "plays", "shuffle-cut-v1.json")))
VALP = os.path.join(D, "shuffle", "validation", "shuffle-tactical-validation.json")
VAL = json.load(open(VALP if os.path.exists(VALP) else "/tmp/claude-0/sc-val.json"))
CAN = json.load(open(os.path.join(T, "tactical", "shuffle", "e2a_shuffle_cut_v1.json")))
OFF = CAN["coordinates"]["engine_offset_s"]
PL = {"A": PLAY}
M = PLAY["marks"]                                  # engine play time
GOLD, NAVY, WHITE, RED, GREEN = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A", "#3BC46B"
TRUTH = {k: [[a + OFF, b + OFF] for a, b in v] for k, v in VAL["truth_windows_owner_s"].items()}
E = lambda p: [round(-p[0], 3), p[1]]           # owner -> engine
SP = {k: E(v) for k, v in CAN["designed_spots"].items()} if isinstance(CAN["designed_spots"], dict) else {}

LINES = [("hook", "One screen. One cut. And the defender never sees it coming!"), ("name", "This is the Shuffle Cut."),
         ("swing", "First, the ball swings to the wing."), ("watch", "Now watch the big man."),
         ("sets", "He sets the back screen... right behind the defender."), ("waits", "The cutter waits for it."), ("slow", "Slow... slow..."),
         ("explodes", "then he explodes off the screener's shoulder!"), ("chasing", "The defender gets caught chasing, right into the screen."),
         ("stride", "The wing hits the cutter in stride..."), ("layup", "and there's your layup!"), ("scf", "Screen. Cut. Finish."),
         ("timing", "That's why timing matters more than just speed."), ("close", "One screen. Perfect timing. Easy advantage.")]


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

# camera library (engine coordinates: the cut side is engine +x; yaw < 0 looks from that side, basket at the top)
CAM_A = orb(fol(["O1", "X1", "O5"], 1.0), 6.2, 66, -28, 50)                  # A opening close-up
CAM_A2 = orb(fol(["O1", "X1", "O5"], 1.0), 7.0, 62, -22, 52)
CAM_B = orb([1.0, 5.8, 0.0], 20.0, 42, 0, 84)                              # B broadcast (all ten, wing entry)
CAM_B2 = orb([-1.2, 7.4, 0.2], 14.0, 48, -8, 72)
CAM_C = orb(fol(["O5", "X1"], 1.0), 6.0, 74, -40, 52)                       # C low on the screener
CAM_C2 = orb(fol(["O5", "X1", "O1"], 1.0), 7.2, 62, -24, 52)
CAM_D = orb(fol(["O1", "O5", "X1"], 1.0, 0.12), 7.2, 62, -36, 54)          # D tracking the cutter
CAM_D2 = orb(fol(["O1", "X1"], 1.0, 0.2), 7.6, 60, -30, 54)
CAM_G = orb(fol(["X1", "O5", "O1"], 1.0), 6.8, 66, -52, 52)                 # G slow-motion replay
CAM_G2 = orb(fol(["X1", "O5", "O1"], 1.0), 6.4, 68, -60, 50)
CAM_F0 = orb([-1.8, 6.9, 0.4], 16.5, 50, -8, 66)                           # F: the pass lane wing -> cutter
CAM_F = orb([0.8, 3.1, 1.1], 7.8, 72, -58, 50)                              # F: catch, take-off, glass (low, cut side)
CAM_F2 = orb([0.4, 2.2, 1.5], 6.8, 77, -66, 48)
CAM_E = orb([0.3, 5.6, 0.0], 18.8, 12, 0, 78)                               # E overhead tactical
CAM_E2 = orb([0.3, 5.4, 0.0], 18.2, 16, -2, 78)


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
stamp = lambda text, fr, to, y=110: {"type": "stamp", "text": text, "tone": "gold", "y": y, "instant": True, "from": r3(fr), "to": r3(to)}
SCREENTAG = lambda fr, to, yaw=-28, off=(0.9, 0.9), size=0.42: {"type": "screenTag", "player": "O5", "vs": "X1", "n": 1, "label": "BACK SCREEN",
                                                                 "plantAt": M["screen_set"], "yaw": yaw, "labelOffset": list(off), "size": size, "from": r3(fr), "to": r3(to)}
CUTARROW = lambda fr, to, draw=0.55: {"type": "route", "player": "O1", "t0": M["k3"], "t1": M["k5"], "color": GOLD, "draw": draw, "width": 0.17, "consume": True, "from": r3(fr), "to": r3(to)}
HOOK_PT = M["brush"] + 0.02                       # O1 brushing the screener's shoulder, X1 caught on O5


def build(words, voice, music, env):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    t_end = r3(e0("close") + 0.92)
    cuts = {"hook": 0.0, "full": s0("name") - 0.12, "setup": s0("swing") - 0.21, "cut": s0("waits") - 0.11, "chase": s0("chasing") - 0.14,
            "finish": s0("stride") - 0.11, "recap": s0("scf") - 0.2}
    order = list(cuts)
    dur = {k: r3((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k]) for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    Lw = lambda k, i, sh: wd(k, i) - cuts[sh]
    Ee = lambda k, sh: e0(k) - cuts[sh]
    shots = []

    # 01 HOOK: freeze on the cut -----------------------------------------------------------------------------------------
    d = dur["hook"]
    tcut = Lw("hook", 3, "hook")                          # "cut."
    tdef = Lw("hook", 6, "hook")                          # "defender"
    tfz = tcut + 0.1
    rm = [[0, M["k3"] + 0.05], [tfz, HOOK_PT], [d, HOOK_PT]]
    b0, b1 = gate("o1_behind_x1", rm, tfz, d)
    shots.append({"id": "hook", "name": "01 HOOK: One screen. One cut. (freeze on the cut)", "at": 0.0, "play": "A", "remap": rm,
                  "camera": [key(0, CAM_A), key(tfz, CAM_A2, "inOut"), key(d, orb(fol(["O1", "X1", "O5"], 1.0), 6.6, 64, -34, 50), "inOut")],
                  "ov3": [mk("O1", 0.0, d + 0.3), mk("X1", tdef - 0.1, d + 0.3), mk("O5", 0.0, d + 0.3), trail("O1", 0.0, tfz, 0.8),
                          SCREENTAG(0.0, d + 0.3, -30, (0.9, 1.0), 0.36),
                          {"type": "spot", "player": "O1", "r": 0.8, "from": r3(tfz), "to": r3(d)}],
                  "screen": [{"type": "freeze", "from": r3(tfz), "to": r3(d)}, {"type": "punch", "amount": 0.035, "from": r3(tfz), "to": r3(tfz + 0.3)},
                             stamp("E2A SPORTS", 0.0, d),
                             {**ttl(["ONE SCREEN.", "ONE CUT."], [1], Lw("hook", 0, "hook") - 0.05, tdef - 0.2, 250, 116), "noOut": False},
                             focus("X1", tdef - 0.1, d, 240, 0.55),
                             pin("X1", "NEVER SEES IT", max(tdef, b0), min(d, b1), "red", 44)]})

    # 02 FULL PLAY: real time, broadcast camera ---------------------------------------------------------------------------
    d = dur["full"]
    p0 = M["k0"] + 0.1
    rm = [[0, p0], [d, min(PLAY["duration"], p0 + d)]]
    tname = Lw("name", 3, "full")                         # "Shuffle"
    shots.append({"id": "full", "name": "02 FULL PLAY in real time: This is the Shuffle Cut.", "at": cuts["full"], "play": "A", "remap": rm,
                  "camera": [key(0, CAM_B), key(d, CAM_B)],
                  "ov3": [mk("O1", 0.0, d + 0.3), trail("O1", inv(rm, M["k3"]), inv(rm, M["k5"]) + 0.2, 0.9),
                          {"type": "ballTrail", "len": 0.5, "color": GOLD, "from": 0.0, "to": r3(d)}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": 0.25}, stamp("REAL TIME", 0.15, d),
                             {**ttl(["THE", "SHUFFLE CUT"], [1], tname - 0.1, d - 0.15, 250, 112), "noOut": False}]})

    # 03 SETUP: rewind, swing to the wing, the big man, the back screen behind the defender ---------------------------------
    d = dur["setup"]
    rw = 0.35
    tsw, twg = Lw("swing", 3, "setup"), Ee("swing", "setup")             # "swings", end of "wing."
    tbig = Lw("watch", 3, "setup")                                       # "big"
    tscr = Lw("sets", 4, "setup")                                        # "screen..."
    tbeh = Lw("sets", 6, "setup")                                        # "behind"
    rm = [[0, min(PLAY["duration"], p0 + dur["full"])], [rw, M["k0"] - 0.05], [tsw, M["rel1"]], [twg, M["k1"]], [tscr, M["screen_set"] + 0.02],
          [d, M["screen_set"] + 0.12]]
    s0_, s1_ = gate("screen_set", rm, tscr - 0.2, d)
    shots.append({"id": "setup", "name": "03 SETUP: the ball swings to the wing; the big man sets the BACK SCREEN behind the defender",
                  "at": cuts["setup"], "play": "A", "remap": rm,
                  "camera": [key(0, CAM_B), key(rw + 0.2, CAM_B, "inOut"), key(twg + 0.3, CAM_B), key(tbig - 0.1, CAM_B2, "inOut"), key(tbig + 0.5, CAM_C, "inOut"),
                             key(tbeh - 0.1, CAM_C2, "inOut"), key(d, CAM_C2)],
                  "ov3": [{"type": "ballPath", "src": "O2", "dst": "O3", "color": GOLD, "draw": 0.25, "from": r3(tsw - 0.3), "to": r3(twg + 0.5)},
                          mk("O3", tsw, twg + 0.8), mk("O5", tbig - 0.15, d + 0.3), trail("O5", tbig - 0.1, tscr, 0.7),
                          mk("X1", tbeh - 0.2, d + 0.3), SCREENTAG(s0_, d + 0.3),
                          {"type": "vision", "player": "X1", "man": "O1", "split": 70, "len": 2.2, "from": r3(tbeh - 0.1), "to": r3(d + 0.3)}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw}, pin("O3", "WING", twg - 0.3, twg + 0.9, "gold", 44),
                             pin("O5", "BIG MAN", tbig - 0.05, tscr - 0.1, "gold", 46),
                             {**ttl(["BACK", "SCREEN"], [1], s0_, tbeh - 0.15, 250, 112), "noOut": False},
                             pin("X1", "BALL-WATCHING", tbeh, min(d, s1_), "red", 44),
                             stamp("x0.25", tscr, d)]})

    # 04 CUT: waits, slow... slow... explodes -------------------------------------------------------------------------------
    d = dur["cut"]
    rw = 0.3
    twt = Lw("waits", 2, "cut")
    ts1, ts2 = Lw("slow", 0, "cut"), Lw("slow", 1, "cut")
    tex = Lw("explodes", 2, "cut")                                        # "explodes"
    tsh = Lw("explodes", 6, "cut")                                        # "shoulder!"
    rm = [[0, M["screen_set"] + 0.12], [rw, M["k0"] + 0.55], [twt, M["k0"] + 0.75], [ts1, M["k1"] + 0.3], [ts2, M["k2"] + 0.1],
          [tex, M["k3"] + 0.02], [tsh, M["brush"]], [d, M["brush"] + 0.18]]
    shots.append({"id": "cut", "name": "04 CUT: The cutter waits for it. Slow... slow... then he EXPLODES off the screener's shoulder!",
                  "at": cuts["cut"], "play": "A", "remap": rm,
                  "camera": [key(0, CAM_C2), key(rw + 0.3, CAM_D, "inOut"), key(tex - 0.1, CAM_D, "inOut"), key(d, CAM_D2, "inOut")],
                  "ov3": [mk("O1", rw, d + 0.3), mk("O5", 0.0, d + 0.3), mk("X1", 0.0, d + 0.3), SCREENTAG(0.0, d + 0.3),
                          trail("O1", tex - 0.05, d + 0.3, 0.8), CUTARROW(tex - 0.25, d + 0.3)],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw}, pin("O1", "CUTTER", rw + 0.2, ts1 - 0.1, "gold", 46),
                             chip("CHANGE OF PACE", ts1 - 0.05, tex - 0.1, "gold", 330, 58),
                             {"type": "flash", "color": "#FFFFFF", "strength": 0.14, "from": r3(tex), "to": r3(tex + 0.22)},
                             {"type": "punch", "amount": 0.03, "from": r3(tex), "to": r3(tex + 0.3)},
                             {**ttl(["EXPLODE"], [0], tex - 0.02, d - 0.1, 250, 124), "noOut": False},
                             stamp("x0.5", tex, d)]})

    # 05 CHASE: slow-motion replay, X1 caught chasing into the screen --------------------------------------------------------
    d = dur["chase"]
    rw = 0.3
    tch = Lw("chasing", 4, "chase")                                       # "chasing,"
    tin = Lw("chasing", 8, "chase")                                       # "screen."
    rm = [[0, M["brush"] + 0.18], [rw, M["k3"] + 0.02], [tch, M["contact"] - 0.2], [tin, M["contact"] + 0.01], [d, M["contact"] + 0.06]]
    x0, x1 = gate("x1_delayed", rm, tch - 0.3, d)
    shots.append({"id": "chase", "name": "05 CHASE (replay x0.25): The defender gets caught chasing, right into the screen.",
                  "at": cuts["chase"], "play": "A", "remap": rm,
                  "camera": [key(0, CAM_D2), key(rw + 0.2, CAM_G, "inOut"), key(d, CAM_G2, "inOut")],
                  "ov3": [mk("X1", 0.0, d + 0.3), mk("O1", 0.0, d + 0.3), mk("O5", 0.0, d + 0.3), SCREENTAG(0.0, d + 0.3),
                          {"type": "ghostTrail", "player": "X1", "len": 0.5, "n": 5, "color": RED, "from": r3(rw + 0.1), "to": r3(d + 0.3)},
                          {"type": "separation", "a": "X1", "b": "O1", "color": RED, "from": x0, "to": x1},
                          {"type": "lockRing", "player": "X1", "color": RED, "size": 1.0, "from": r3(tin - 0.1), "to": r3(d + 0.3)}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw}, stamp("REPLAY  x0.25", rw, d),
                             pin("X1", "CHASING", tch - 0.1, tin - 0.15, "red", 46),
                             {**ttl(["INTO THE", "SCREEN"], [1], tin - 0.05, d - 0.05, 250, 112), "noOut": False}]})

    # 06 FINISH: pass in stride, layup --------------------------------------------------------------------------------------
    d = dur["finish"]
    tstr = Lw("stride", 5, "finish")                                      # "stride..."
    tth = Lw("layup", 1, "finish")                                        # "there's"
    tly = Lw("layup", 3, "finish")                                        # "layup!"
    rm = [[0, M["contact"] + 0.06], [tstr, M["k5"]], [tth, M["k6"]], [tly + 0.12, M["make"]], [d, min(PLAY["duration"], M["make"] + 0.6)]]
    t_catch, t_make = inv(rm, M["k5"]), inv(rm, M["make"])
    shots.append({"id": "finish", "name": "06 FINISH: The wing hits the cutter in stride... and there's your layup!",
                  "at": cuts["finish"], "play": "A", "remap": rm,
                  "camera": [key(0, CAM_F0), key(t_catch - 0.7, CAM_F0), key(t_catch - 0.05, CAM_F, "inOut"), key(d, CAM_F2, "inOut")],
                  "ov3": [{"type": "ballPath", "src": "O3", "dst": "O1", "color": GOLD, "draw": 0.25, "from": 0.0, "to": r3(t_catch + 0.3)},
                          lane("O3", "O1", GREEN, 0.0, t_catch - 0.1, 1.8), mk("O1", 0.0, t_make), mk("O3", 0.0, t_catch),
                          trail("O1", 0.0, t_make, 0.7),
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.6, "from": r3(t_make), "to": r3(d)}],
                  "screen": [stamp("x0.5", 0.0, t_catch), pin("O1", "IN STRIDE", t_catch - 0.1, tth - 0.05, "gold", 44),
                             chip("LAYUP.", t_make + 0.05, d, "gold", 330, 84),
                             {"type": "micro", "text": "VS. THIS COVERAGE: X1 CHASES, NO SWITCH", "y": 440, "from": r3(t_make + 0.1), "to": r3(d)}]})

    # 07 RECAP: overhead replay SCREEN / CUT / FINISH, timing > speed, close ---------------------------------------------------
    d = dur["recap"]
    rw = 0.35
    tS, tC, tF = Lw("scf", 0, "recap"), Lw("scf", 1, "recap"), Lw("scf", 2, "recap")
    ttm = Lw("timing", 2, "recap")                                        # "timing"
    tcl = L("close", "recap")
    tend = Ee("close", "recap")
    rw = 0.3
    t_mk = 2.7                                    # the replay runs at ~x1.15 from just before the screen to the make
    rm = [[0, min(PLAY["duration"], M["make"] + 0.6)], [rw, M["screen_set"] - 0.05], [t_mk, M["make"]], [d, M["make"]]]
    shots.append({"id": "recap", "name": "07 RECAP (overhead): Screen. Cut. Finish. Timing > speed. One screen. Perfect timing. Easy advantage.",
                  "at": cuts["recap"], "play": "A", "remap": rm,
                  "camera": [key(0, CAM_F2), key(rw + 0.15, CAM_E, "inOut"), key(tcl, CAM_E, "inOut"), key(d, CAM_E2, "inOut")],
                  "ov3": [SCREENTAG(tS - 0.05, d + 0.3, 0, (1.2, 0.6), 0.5), mk("O5", tS - 0.05, d + 0.3), mk("X1", tS - 0.05, d + 0.3),
                          {"type": "arrow3d", "player": "O1", "t0": M["k2"], "t1": M["k6"], "color": GOLD, "width": 0.17, "draw": 0.55,
                           "from": r3(tC - 0.05), "to": r3(d + 0.3)},
                          {"type": "arrow3d", "player": "X1", "t0": M["k3"], "t1": M["k6"], "color": RED, "width": 0.13, "draw": 0.55,
                           "from": r3(tC + 0.3), "to": r3(d + 0.3)},
                          mk("O1", tC - 0.05, d + 0.3),
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.6, "from": r3(tF), "to": r3(d)}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw}, stamp("REPLAY", rw, t_mk),
                             ttl(["SCREEN."], [0], tS - 0.04, tC - 0.06, 250, 124), ttl(["CUT."], [0], tC - 0.04, tF - 0.06, 250, 124),
                             ttl(["FINISH."], [0], tF - 0.04, ttm - 0.12, 250, 124),
                             {**ttl(["TIMING", "> SPEED"], [1], ttm - 0.1, tcl - 0.1, 250, 118), "noOut": False},
                             ttl(["ONE SCREEN.", "PERFECT TIMING."], [1], tcl - 0.05, tend - 0.1, 250, 100),
                             {"type": "logo", "big": False, "y": 1600, "from": r3(tcl + 0.2), "to": r3(d - 0.05)}]})

    kw = ["screen.", "cut.", "never", "Shuffle", "wing.", "big", "back", "behind", "waits", "Slow...", "explodes", "shoulder!", "chasing,",
          "screen.", "stride...", "layup!", "Screen.", "Cut.", "Finish.", "timing", "speed.", "Perfect", "advantage."]
    ep = {"id": "e2a-shuffle-cut-v1", "title": "THE SHUFFLE CUT", "fps": 30, "voice": voice, "tail": r3(t_end - words[-1]["end"]),
          "autoSfx": False, "pinV2": True, "env": env, "athleteRenderer": "v33", "words": words,
          "subtitleGroups": [len(t.split()) for _, t in LINES], "subtitleBlock": True, "subtitleCommas": True, "subtitleY": 1400,
          "keywords": kw, "gradeBottom": 0.3, "shots": shots, "plays": PL}
    if music:
        ep["music"] = {"src": music, "volume": 1}
    meta = {"duration": t_end, "cuts": {k: r3(v) for k, v in cuts.items()}, "dur": dur}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice")
    ap.add_argument("--music")
    ap.add_argument("--fit")
    ap.add_argument("--env", default="arena")
    a = ap.parse_args()
    words = json.load(open(os.path.join(D, "shuffle", "shuffle.words.json")))
    props, meta = build(words, a.voice or "shuffle/voice.mix.wav", a.music, a.env)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"]); ep["plays"] = {k: v["id"] for k, v in PL.items()}
        json.dump(ep, open(a.fit, "w")); json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    print(json.dumps(meta))
