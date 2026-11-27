#!/usr/bin/env python3
"""E2A BASKETBALL IQ 01 V3 - complete creative rebuild (Master Production Directive V3.0, 2026-11-27).
V1 (b25d9f5) and V2 (87a6501, tag iq01-v2-reference) stay untouched. Narrator: Nathaniel (eleven_v4), one take.
Story (Concept A "THE TRAP"): the easy pass is a trap -> live drive, the help comes -> FREEZE, A/B/C -> honest 2.0 s call
-> misdirection: A looks easy (man home) sweeping to B (defender in the lane) in ONE move -> discovery: the low helper left
the corner (spotlight + ghost) -> "There! That's your window. C!" -> kick and three at real speed -> lesson (ball vs defense)
-> "Run it back": the play rewinds to the hook's first frame (loop).
  python3 tactical/episodes/_gen-iq01v3.py --hook A|B --out props.json [--voice p] [--music p] [--fit ep.json] [--plan plan.json] [--env cinema|game]"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PL = {"A": json.load(open(os.path.join(T, "tactical", "plays", "iq01-open-player.json")))}
SC = json.load(open(os.path.join(D, "iq01v3", "scenario.json")))
GOLD, NAVY, WHITE, RED = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A"
M = PL["A"]["marks"]
DEC = M["decide"]
LET = {c["letter"]: c["player"] for c in SC["choices"]}
DIST = {c["letter"]: c["defender_distance_m"] for c in SC["choices"]}
HOOK_T0 = 0.5                                       # play time on frame 0 (O1 a step before his drive)

HOOK_LINES = {"A": [("hook", "The easy pass here is a trap.")],
              "B": [("hook", "One defender just left a shooter wide open."), ("hook2", "Can you spot him?")]}
BODY = [("beats", "He beats his man and the help is coming."), ("freeze", "Freeze."), ("abc", "A, B, or C?"),
        ("two", "Two seconds. Make your call."), ("a", "A looks easy."), ("ahome", "But his man is still home."),
        ("b", "B? His defender is sitting in the lane."), ("watch", "Now watch the low defender."),
        ("left", "He left the corner to stop the drive."), ("there", "There! That's your window."), ("c", "C!"),
        ("kick", "Kick it."), ("late", "The next rotation is a step too late."),
        ("ball", "The ball tells you where the play is."), ("def", "The defense tells you where to pass."),
        ("see", "Did you see it before the reveal?"), ("run", "Run it back.")]


def line_words(words, lines):
    res, i = {}, 0
    norm = lambda s: "".join(c for c in s.lower() if c.isalnum())
    for k, text in lines:
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
# camera library (all probed with scripts/cam-probe.mts on this play)
HOOKCAM = orb(fol(["O1", "X1"], 0.9), 6.8, 70, 4, 48)          # low, behind the ball handler, mid-stride
DRIVECAM = orb(fol(["O1", "X1", "X3"], 0.9, 0.15), 10.5, 60, -6, 56)
DECIDE = orb([0.0, 4.8, 0.0], 17.0, 46, 0, 84)               # all 8 players inside the 9:16 frame
DEC_L = orb([0.0, 4.8, 0.0], 16.4, 47, 7, 84)                 # tilts toward A (right corner)
DEC_R = orb([0.0, 4.8, 0.0], 16.4, 47, -7, 84)                # tilts toward C (left corner)
LOWORB = orb([0.0, 4.6, 0.0], 16.2, 52, -4, 84)               # decision window: lower, slow orbit
WEAK = orb([2.6, 3.9, 0.4], 14.0, 50, -75, 58)
CAM_A = (orb([-5.3, 3.3, 0.5], 10.2, 52, -24, 52), orb([-5.6, 3.1, 0.5], 9.6, 53, -32, 50))
CAM_B = (orb([3.0, 6.3, 0.5], 12.0, 48, -50, 60), orb([3.2, 6.4, 0.5], 11.0, 49, -56, 60))
CAM_C = (orb([4.6, 2.9, 0.4], 11.2, 52, -52, 54), orb([4.8, 2.8, 0.4], 10.0, 54, -48, 52))  # O3, X3, O1, X4 in frame
TOP = orb([0.0, 4.4, 0.0], 17.6, 10, 0, 76)


def inv(remap, pt):
    for (a, pa), (b, pb) in zip(remap, remap[1:]):
        if pa <= pt <= pb and pb > pa:
            return a + (b - a) * (pt - pa) / (pb - pa)
    raise ValueError(pt)


ttl = lambda lines, gold, fr, to, y=250, size=110, **kw: {"type": "title", "lines": lines, "gold": gold, "reveal": "mask", "from": r3(fr), "to": r3(to), "y": y, "size": size, **kw}
chip = lambda text, fr, to, tone="gold", y=330, size=60: {"type": "chip", "text": text, "tone": tone, "align": "center", "size": size, "from": r3(fr), "to": r3(to), "y": y}
pin = lambda p, text, fr, to, tone="gold", size=46: {"type": "pin", "player": p, "text": text, "tone": tone, "from": r3(fr), "to": r3(to), "size": size}
trail = lambda p, fr, to, ln=0.7: {"type": "motionTrail", "player": p, "len": ln, "color": GOLD if p[0] == "O" else RED, "from": r3(fr), "to": r3(to)}
mk = lambda p, fr, to: {"type": "marker", "player": p, "team": "attack" if p[0] == "O" else "defense", "from": r3(fr), "to": r3(to)}
lane = lambda dst, col, fr, to, w=1.6: {"type": "passLane", "src": "O1", "dst": dst, "color": col, "w": w, "from": r3(fr), "to": r3(to)}
focus = lambda p, fr, to, r=240, st=0.6: {"type": "focus", "player": p, "r": r, "strength": st, "from": r3(fr), "to": r3(to)}


def letter(L, fr, to, wrong=None, right=None, size=100):
    it = {"type": "letter", "player": LET[L], "text": L, "from": r3(fr), "to": r3(to), "size": size, "z": 2.2}
    if wrong is not None:
        it["wrong"] = r3(wrong)
    if right is not None:
        it["right"] = r3(right)
    return it


def build(words, voice, music, hook, env):
    lines = HOOK_LINES[hook] + BODY
    W = line_words(words, lines)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    t_end = r3(e0("run") + 0.55)
    think = SC["decision_window"]
    t0 = e0("two") + 0.17                              # the 2.0 s silence inserted after "Make your call."
    t1 = t0 + think["seconds"]
    cuts = {"drive": 0.0, "ab": s0("a") - 0.12, "replay": s0("watch") - 0.1, "c": s0("there") - 0.1,
            "lesson": s0("ball") - 0.1, "end": s0("see") - 0.1}
    order = list(cuts)
    dur = {k: r3((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k]) for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    Lw = lambda k, i, sh: wd(k, i) - cuts[sh]
    E = lambda k, sh: e0(k) - cuts[sh]
    shots = []

    # 1 HOOK + DRIVE + FREEZE + A/B/C + DECISION (one continuous shot, starts in the action) -----------------------
    d = dur["drive"]
    fz = L("freeze", "drive")
    tb = L("beats", "drive")
    thelp = Lw("beats", 5, "drive")                     # "help"
    tabc = [Lw("abc", i, "drive") for i in (0, 1, 3)]
    th_end = E("hook", "drive") if hook == "A" else E("hook2", "drive")
    # speed ramp: hook at 0.35x (O1 starts his drive under the line), drive at 0.8x, last 0.3 s into the freeze at 0.25x
    rm = [[0, HOOK_T0], [th_end, 1.05], [fz - 0.45, DEC - 0.12], [fz, DEC], [d, DEC]]
    cam = [key(0, HOOKCAM), key(th_end, orb(fol(["O1", "X1"], 0.9), 8.2, 64, 0, 52), "inOut"),
           key(fz - 0.3, DRIVECAM, "inOut"), key(fz + 0.35, DECIDE, "inOut"),
           key(tabc[0], DEC_L, "inOut"), key(tabc[2] + 0.2, DEC_R, "inOut"), key(t0, DECIDE, "inOut"),
           key(t1, LOWORB, "inOut"), key(d, LOWORB)]
    scr = [{"type": "stamp", "text": "BASKETBALL IQ", "badge": "EP 01", "tone": "gold", "y": 110, "instant": True, "from": 0.0, "to": fz - 0.05}]
    ov = [trail("O1", 0.0, fz), mk("O1", -0.8, fz)]
    if hook == "A":
        scr += [{**ttl(["THE EASY PASS", "IS A TRAP"], [1], -0.8, th_end + 0.15, 250, 112), "noOut": False}]
        ov += [lane("O2", WHITE, 0.55, th_end + 0.2, 1.3)]     # the "easy" pass to the right corner, shown and doubted
    else:
        scr += [{**ttl(["ONE DEFENDER", "LEFT HIM OPEN"], [1], -0.8, th_end + 0.15, 250, 112), "noOut": False}]
        ov += [mk("X1", -0.8, th_end), mk("X2", -0.8, th_end), mk("X3", -0.8, th_end), mk("X4", -0.8, th_end)]
    ov += [trail("X3", thelp - 0.4, fz, 0.6), mk("X3", thelp - 0.2, fz + 0.3),
           mk("O2", tabc[0], d), mk("O4", tabc[1], d), mk("O3", tabc[2], d),
           lane("O2", WHITE, tabc[0] + 0.05, d), lane("O4", WHITE, tabc[1] + 0.05, d), lane("O3", WHITE, tabc[2] + 0.05, d)]
    scr += [pin("X3", "HELP", thelp - 0.05, fz - 0.05, "red", 46),
            {"type": "freeze", "from": r3(fz), "to": d}, {"type": "punch", "amount": 0.035, "from": r3(fz), "to": r3(fz + 0.3)},
            ttl(["A, B", "OR C?"], [1], tabc[0] - 0.05, t0 - 0.05, 250, 116),
            letter("A", tabc[0], d), letter("B", tabc[1], d), letter("C", tabc[2], d),
            {"type": "countdown", "label": "MAKE YOUR CALL", "from": r3(t0), "to": r3(t1), "y": 250}]
    shots.append({"id": "drive", "name": f"HOOK {hook} in the action -> drive -> FREEZE -> A/B/C -> 2.0 s call", "at": 0.0, "play": "A",
                  "remap": rm, "camera": cam, "ov3": ov, "screen": scr})

    # 2 MISDIRECTION: A looks easy -> man still home -> sweep to B -> defender in the lane (one continuous move) ------
    d = dur["ab"]
    teasy, thome = Lw("a", 2, "ab"), Lw("ahome", 4, "ab")
    tman = Lw("ahome", 2, "ab")
    tB, tlane = L("b", "ab"), Lw("b", 7, "ab")
    shots.append({"id": "ab", "name": "Misdirection: A looks easy, man still home; B, defender in the lane", "at": cuts["ab"], "play": "A",
                  "remap": [[0, DEC], [d, DEC]],
                  "camera": [key(0, LOWORB), key(0.5, CAM_A[0], "inOut"), key(tB - 0.25, CAM_A[1], "inOut"),
                             key(tB + 0.35, CAM_B[0], "inOut"), key(d, CAM_B[1], "inOut")],
                  "ov3": [mk("O2", 0.0, tB), lane("O2", GOLD, 0.05, tman), mk("X2", tman - 0.1, tB),
                          {"type": "separation", "a": "X2", "b": "O2", "color": RED, "from": r3(tman), "to": r3(tB)},
                          mk("O4", tB - 0.1, d), mk("X4", tB + 0.2, d), lane("O4", WHITE, tB - 0.1, tlane - 0.1),
                          lane("O4", RED, tlane - 0.1, d), {"type": "blocked", "at": SC["spots"]["X4SAG"], "color": RED, "from": r3(tlane), "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d},
                             letter("A", 0.0, tB, wrong=thome), letter("B", tB - 0.3, d, wrong=tlane + 0.1),
                             chip("LOOKS EASY", teasy - 0.1, tman - 0.05, "gold", 330, 64),
                             pin("X2", f"{DIST['A']:.1f} M", tman + 0.05, tB, "red", 46),
                             chip("STILL HOME", thome - 0.15, tB - 0.05, "red", 330, 64),
                             chip("IN THE LANE", tlane - 0.2, d, "red", 330, 64)]})

    # 3 DISCOVERY: rewind, the low helper (spotlight + ghost of where he started) -------------------------------------
    d = dur["replay"]
    rw = 0.35
    tlow, tleft, tcorner = Lw("watch", 3, "replay"), Lw("left", 1, "replay"), Lw("left", 3, "replay")
    rm = [[0, DEC], [rw, 0.6], [tleft + 0.15, 1.25], [d - 0.2, DEC], [d, DEC]]
    shots.append({"id": "replay", "name": "Now watch the low defender. He left the corner to stop the drive.", "at": cuts["replay"], "play": "A",
                  "remap": rm, "camera": [key(0, WEAK), key(d, orb([2.4, 3.6, 0.4], 12.6, 52, -70, 56), "inOut")],
                  "ov3": [mk("X3", tlow - 0.15, d), trail("X3", tleft - 0.3, d, 0.6),
                          {"type": "ghost", "player": "X3", "t": 0.0, "color": RED, "link": True, "from": r3(tleft), "to": d},
                          {"type": "arrow3d", "player": "X3", "t0": M["help"], "t1": DEC, "color": RED, "width": 0.14, "draw": 0.5, "from": r3(tleft + 0.1), "to": d},
                          {"type": "openSpace", "at": SC["spots"]["CORNER_GAP"], "r": 1.3, "color": GOLD, "from": r3(tcorner), "to": d}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw}, focus("X3", tlow - 0.1, d, 250, 0.6),
                             pin("X3", "LOW HELP", tlow, d, "red", 46), letter("C", rw, d, size=88),
                             chip("HE LEFT THE CORNER", tcorner - 0.1, d, "red", 330, 62)]})

    # 4 THE WINDOW: C + kick + three at real speed (one shot) -----------------------------------------------------
    d = dur["c"]
    tthere, tC, tk = L("there", "c"), L("c", "c"), L("kick", "c")
    tnext = Lw("late", 1, "c")
    rm = [[0, DEC], [tk - 0.12, DEC], [tk + 0.1, M["kick"]], [d, min(PL["A"]["duration"], M["kick"] + (d - tk - 0.1))]]
    t_catch, t_make = inv(rm, M["catch"]), inv(rm, M["make"])
    shots.append({"id": "c", "name": "There! That's your window. C! Kick it. The next rotation is a step too late.", "at": cuts["c"], "play": "A", "remap": rm,
                  "camera": [key(0, CAM_C[0]), key(tk - 0.1, CAM_C[1], "inOut"), key(t_catch, orb([3.6, 3.4, 0.5], 12.0, 50, -74, 55), "inOut"),
                             key(d, orb([4.4, 3.2, 0.6], 10.8, 53, -74, 52), "inOut")],
                  "ov3": [mk("O3", 0.0, t_catch + 0.4), mk("X3", 0.0, tk),
                          {"type": "separation", "a": "X3", "b": "O3", "color": GOLD, "from": 0.15, "to": r3(tk)},
                          {"type": "openSpace", "at": SC["spots"]["CORNER_GAP"], "r": 1.35, "color": GOLD, "from": 0.1, "to": r3(tk + 0.3)},
                          lane("O3", GOLD, tC - 0.05, tk + 0.05, 1.8),
                          {"type": "ballPath", "src": "O1", "dst": "O3", "color": GOLD, "draw": 0.3, "from": r3(tk), "to": r3(t_catch + 0.35)},
                          mk("X4", tnext - 0.2, d), trail("X4", tnext - 0.2, d, 0.6),
                          {"type": "separation", "a": "X4", "b": "O3", "color": RED, "from": r3(tnext), "to": r3(t_make - 0.2)},
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.55, "from": r3(t_make), "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": r3(tk - 0.12)},
                             ttl(["THAT'S THE", "WINDOW"], [1], tthere + 0.15, tk - 0.05, 250, 116),
                             letter("C", 0.0, t_catch, right=tC), pin("X3", f"{DIST['C']:.1f} M", 0.2, tC - 0.05, "gold", 46),
                             chip("2ND ROTATION: A STEP LATE", tnext - 0.1, t_make - 0.1, "red", 330, 56),
                             chip("THREE.", t_make + 0.05, d, "gold", 330, 80)]})

    # 5 LESSON: the ball vs the defense (top view) ------------------------------------------------------------------
    d = dur["lesson"]
    rw = 0.35
    tdf = L("def", "lesson")
    rm = [[0, min(PL["A"]["duration"], M["make"] + 0.3)], [rw, 0.9], [tdf + 0.35, DEC], [d, DEC]]
    shots.append({"id": "lesson", "name": "The ball tells you where the play is. The defense tells you where to pass.", "at": cuts["lesson"], "play": "A", "remap": rm,
                  "camera": [key(0, TOP), key(d, orb([0.0, 4.3, 0.0], 16.4, 14, 0, 76), "inOut")],
                  "ov3": [{"type": "ballRing", "color": WHITE, "from": r3(rw), "to": r3(tdf)}, mk("X3", tdf - 0.1, d),
                          {"type": "ghost", "player": "X3", "t": 0.0, "color": RED, "link": True, "from": r3(tdf), "to": d},
                          {"type": "arrow3d", "player": "X3", "t0": M["help"], "t1": DEC, "color": RED, "width": 0.15, "draw": 0.4, "from": r3(tdf), "to": d},
                          lane("O3", GOLD, tdf + 0.5, d, 1.8)],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             ttl(["THE BALL:", "WHERE THE PLAY IS"], [0], rw - 0.05, tdf - 0.06, 250, 96),
                             ttl(["THE DEFENSE:", "WHERE TO PASS"], [0], tdf - 0.04, d - 0.05, 250, 104)]})

    # 6 LOOP: "Run it back" - the play rewinds to the hook's first frame, camera lands on the hook rig -------------
    d = dur["end"]
    trn = L("run", "end")
    shots.append({"id": "end", "name": "Did you see it before the reveal? Run it back. (rewinds to frame 0)", "at": cuts["end"], "play": "A",
                  "remap": [[0, DEC], [trn, DEC], [d, HOOK_T0]],
                  "camera": [key(0, DECIDE), key(trn, DECIDE), key(d, HOOKCAM, "inOut")],
                  "ov3": [mk("O2", 0.0, trn), mk("O4", 0.0, trn), mk("O3", 0.0, trn), mk("O1", trn, d + 0.5)],
                  "screen": [letter("A", 0.05, trn), letter("B", 0.1, trn), letter("C", 0.15, trn),
                             ttl(["DID YOU", "SEE IT?"], [1], 0.0, trn - 0.04, 250, 116),
                             {"type": "rewind", "from": r3(trn), "to": r3(d - 0.4)},          # chip top 258: title sits below it
                             ttl(["RUN IT", "BACK"], [1], trn - 0.02, d - 0.4, 318, 116),     # gone 0.4 s before the end: clean loop frame
                             {"type": "logo", "big": False, "y": 1600, "from": 0.2, "to": r3(trn)}]})
    kw = ["trap.", "open.", "help", "Freeze.", "C?", "call.", "easy.", "home.", "lane.", "low", "corner", "window.", "C!", "late.",
          "ball", "defense", "back."]
    ep = {"id": f"iq01v3-open-player-{hook}", "title": "CAN YOU FIND THE OPEN PLAYER?", "fps": 30,
          "voice": voice, "tail": r3(t_end - words[-1]["end"]), "autoSfx": False, "pinV2": True, "env": env,
          "athleteRenderer": "v33", "words": words, "subtitleGroups": [len(t.split()) for _, t in lines],
          "subtitleBlock": True, "subtitleCommas": True, "subtitleY": 1400, "keywords": kw, "gradeBottom": 0.3,
          "shots": shots, "plays": PL}
    if music:
        ep["music"] = {"src": music, "volume": 1}
    rel_kick = cuts["c"] + tk
    plan = {"duration": t_end,
            "states": [[0.0, fz, "A"], [fz, t0, "B"], [t0, t1, "BREAK"], [t1, cuts["replay"], "B"], [cuts["replay"], cuts["c"], "A"],
                       [cuts["c"], cuts["lesson"], "A"], [cuts["lesson"], cuts["end"], "B"], [cuts["end"], t_end + 1, "A"]],
            "releases": [r3(rel_kick)], "hits": [r3(fz), r3(cuts["c"] + tC)]}
    meta = {"duration": t_end, "cuts": {k: r3(v) for k, v in cuts.items()}, "think": [r3(t0), r3(t1)], "freeze": r3(fz), "plan": plan}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--hook", default="A")
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice")
    ap.add_argument("--music")
    ap.add_argument("--fit")
    ap.add_argument("--plan")
    ap.add_argument("--env", default="cinema")
    a = ap.parse_args()
    words = json.load(open(os.path.join(D, "iq01v3", f"iq01v3-{a.hook}.words.json")))
    props, meta = build(words, a.voice or f"iq01v3/voice-{a.hook}.mix.wav", a.music, a.hook, a.env)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"]); ep["plays"] = {k: v["id"] for k, v in PL.items()}
        json.dump(ep, open(a.fit, "w")); json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    if a.plan:
        json.dump(meta["plan"], open(a.plan, "w"), indent=1)
    print(json.dumps({k: meta[k] for k in ("duration", "cuts", "think", "freeze")}))
