#!/usr/bin/env python3
"""E2A BASKETBALL IQ 01 - "CAN YOU FIND THE OPEN PLAYER?" (owner brief 2026-11-26 20:56Z) - Remotion props for
Tactical3DV2 (E2A Basketball Visual Standard v1: v33 players, env cinema, marker overlays, one clear tactical cam).
ACTION -> QUESTION -> THINK -> REPLAY -> REVEAL -> EXPLANATION -> PAYOFF. All cut points come from the real narration
words (tactical/episodes/iq01/iq01-voice.words.json, one Deuce take, silences inserted, never stretched).
  q        ACTION + QUESTION + THINK: one continuous shot. O1 beats X1, X3 rotates (speed ramp), pull-out to the full
           4v4 floor, FREEZE on "Freeze it", letters A (O2) / B (O4) / C (O3) on the words, ~2 s think, LOCK IT IN
  replay   rewind, slow-motion replay framed on the weak side: X3 leaves the corner to stop the drive
  a / b / c the frozen decision moment, one receiver at a time: A X2 still home (separation), B X4 in the passing lane
           (blocked lane), C X3 at the rim (6 m gap, gold open space). Letters never move to another player.
  kick     real speed: kick, X4 reacts late (2nd rotation too late), catch, corner three
  lesson   rewind, top view: don't watch the ball, watch the help (X3's rotation)
  end      the question frame again, neutral letters: DID YOU FIND HIM? A, B OR C? (loop + comments)
Play: tactical/specs/_gen-iq01.py -> iq01-open-player (4 v 4).
  python3 tactical/episodes/_gen-iq01.py --out props.json [--voice p] [--music p] [--fit ep.json] [--plan plan.json] [--trial]"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PL = {"A": json.load(open(os.path.join(T, "tactical", "plays", "iq01-open-player.json")))}
GOLD, NAVY, WHITE, RED = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A"
M = PL["A"]["marks"]
DEC = M["decide"]
CORNER = [6.9, 2.2]
LET = {"A": "O2", "B": "O4", "C": "O3"}

LINES = [
    ("hook", "He beats his man, and here comes the help."), ("freeze", "Freeze it."), ("who", "Who's open?"),
    ("abc", "A, B, or C?"), ("lock", "Lock it in."), ("watch", "Now watch the low defender."),
    ("leaves", "He leaves the corner to stop the drive."), ("a", "A, his defender is still home."),
    ("b", "B, still guarded, and his defender is sitting in the passing lane."), ("c", "C, wide open."),
    ("kick", "Kick it to the corner."), ("late", "The next rotation is too late."), ("ball", "Don't watch the ball."),
    ("help", "Watch the help."), ("find", "Did you find him?"), ("tell", "Tell us what you picked."),
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
key = lambda at, rig, ease=None: {"at": round(at, 3), "rig": rig, **({"ease": ease} if ease else {})}
BROAD = orb([0.0, 4.1, 0.0], 19.5, 34, 0, 76)          # the question frame: all 8 players, basket up
BROAD2 = orb([0.0, 4.1, 0.0], 18.9, 35, 0, 76)
WEAK = orb([2.6, 3.9, 0.4], 14.5, 46, -75, 58)          # weak side: driver, X3, X4, O3 corner


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


def letter(L, fr, to, wrong=None, right=None, size=92):
    it = {"type": "letter", "player": LET[L], "text": L, "from": round(fr, 3), "to": round(to, 3), "size": size, "z": 2.2}
    if wrong is not None:
        it["wrong"] = round(wrong, 3)
    if right is not None:
        it["right"] = round(right, 3)
    return it


def mk(p, fr, to):
    return {"type": "marker", "player": p, "team": "attack" if p[0] == "O" else "defense", "from": round(fr, 3), "to": round(to, 3)}


def build(words, voice, music, trial=False):
    W = line_words(words)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    t_end = round(e0("tell") + 1.3, 3)
    cuts = {"q": 0.0, "replay": s0("watch") - 0.12, "a": s0("a") - 0.1, "b": s0("b") - 0.1, "c": s0("c") - 0.1,
            "kick": s0("kick") - 0.15, "lesson": s0("ball") - 0.12, "end": s0("find") - 0.12}
    order = list(cuts)
    dur = {k: round((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k], 3) for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    Lw = lambda k, i, sh: wd(k, i) - cuts[sh]
    E = lambda k, sh: e0(k) - cuts[sh]
    shots = []

    # wrong / right reveal times (edit time) for the letters
    tA, tB, tC = s0("a") + 0.35, s0("b") + 0.35, s0("c") + 0.2

    # 1 ACTION + QUESTION + THINK (one continuous shot) ------------------------------------------------------------
    d = dur["q"]
    fz = L("freeze", "q")
    tw, tabc = L("who", "q"), [Lw("abc", i, "q") for i in (0, 1, 3)]
    tthink, tlock = E("abc", "q") + 0.1, L("lock", "q")
    p0 = 0.35 if trial else 0.0
    rm = [[0, p0], [1.45, 1.45], [2.35, 1.72], [fz, DEC], [d, DEC]]
    if trial:
        cam = [key(0, orb(fol(["O1", "X1", "X3"], 0.8), 14.0, 46, 0, 58)),
               key(1.6, orb(fol(["O1", "X3"], 0.8), 15.0, 40, 0, 62), "inOut"),
               key(fz, BROAD, "inOut"), key(d, BROAD2, "inOut")]
    else:
        cam = [key(0, orb(fol(["O1", "X1"], 0.8), 9.5, 58, -10, 50)),
               key(1.5, orb(fol(["O1", "X1", "X3"], 0.8), 11.0, 52, -6, 54), "inOut"),
               key(fz, BROAD, "inOut"), key(d, BROAD2, "inOut")]
    shots.append({"id": "q", "name": "ACTION + QUESTION + THINK: drive, help, freeze, A / B / C, think, lock it in", "at": 0.0, "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [trail("O1", 0.0, fz), trail("X3", 1.1, fz, 0.6),
                          mk("O2", tabc[0], d), mk("O4", tabc[1], d), mk("O3", tabc[2], d),
                          {"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": tabc[0] + 0.05, "to": d},
                          {"type": "passLane", "src": "O1", "dst": "O4", "color": WHITE, "from": tabc[1] + 0.05, "to": d},
                          {"type": "passLane", "src": "O1", "dst": "O3", "color": WHITE, "from": tabc[2] + 0.05, "to": d}],
                  "screen": [{"type": "stamp", "text": "BASKETBALL IQ", "badge": "EP 01", "tone": "gold", "y": 110, "instant": True, "from": 0.0, "to": fz - 0.05},
                             ttl(["CAN YOU FIND", "THE OPEN PLAYER?"] if not trial else ["WHO'S OPEN?", "FIND HIM"], [1], 0.0 if not trial else 0.1, fz - 0.06, 300, 96),
                             {"type": "freeze", "from": fz, "to": d},
                             ttl(["WHO'S", "OPEN?"], [1], tw - 0.05, tthink, 250, 112),
                             letter("A", tabc[0], d), letter("B", tabc[1], d), letter("C", tabc[2], d),
                             chip("YOUR CALL: A, B OR C", tthink, tlock - 0.05, "gold", 300, 60),
                             ttl(["LOCK IT", "IN"], [1], tlock - 0.05, d - 0.05, 250, 112)]})

    # 2 REPLAY (rewind, slow motion on the weak side): X3 leaves the corner to stop the drive ---------------------------
    d = dur["replay"]
    rw = 0.45
    tlow, tleave, tcorner, tdrive = Lw("watch", 3, "replay"), Lw("leaves", 1, "replay"), Lw("leaves", 3, "replay"), Lw("leaves", 7, "replay")
    rm = [[0, DEC], [rw, 0.55], [tleave, 1.15], [d - 0.35, DEC], [d, DEC]]
    cam = [key(0, WEAK), key(d, orb([2.6, 3.8, 0.4], 13.6, 47, -72, 57), "inOut")]
    shots.append({"id": "replay", "name": "Replay: now watch the low defender. He leaves the corner to stop the drive.", "at": cuts["replay"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [mk("X3", tlow - 0.1, d),
                          {"type": "arrow3d", "player": "X3", "t0": M["help"], "t1": DEC, "color": RED, "width": 0.12, "draw": 0.5, "from": tleave - 0.1, "to": d},
                          {"type": "openSpace", "at": [6.5, 2.4], "r": 1.25, "color": GOLD, "from": tcorner, "to": d},
                          trail("X3", tleave - 0.3, d, 0.6), trail("O1", rw, d, 0.6)],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             pin("X3", "LOW HELP", tlow, tleave - 0.05, "white", 40),
                             pin("X3", "STOPS THE DRIVE", tdrive - 0.25, d, "white", 40),
                             letter("C", rw, d, size=80),
                             chip("HE LEAVES THE CORNER", tcorner - 0.1, d, "red", 470, 58)]})

    # 3-5 THE DECISION MOMENT, ONE RECEIVER AT A TIME (frozen at DEC) ----------------------------------------------
    d = dur["a"]
    rm = [[0, DEC], [d, DEC]]
    shots.append({"id": "a", "name": "A? His defender is still home.", "at": cuts["a"], "play": "A", "remap": rm,
                  "camera": [key(0, orb([-5.5, 3.1, 0.5], 10.0, 50, -32, 50)), key(d, orb([-5.8, 2.9, 0.5], 9.3, 52, -36, 50), "inOut")],
                  "ov3": [mk("O2", 0.1, d), mk("X2", 0.3, d), {"type": "separation", "a": "X2", "b": "O2", "color": RED, "from": 0.5, "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d}, letter("A", 0.0, d, wrong=tA - cuts["a"]),
                             chip("A · HIS DEFENDER IS HOME", 0.35, d, "red", 470, 58)]})
    d = dur["b"]
    tlane = Lw("b", 9, "b")
    shots.append({"id": "b", "name": "B? Still guarded, and his defender is sitting in the passing lane.", "at": cuts["b"], "play": "A", "remap": [[0, DEC], [d, DEC]],
                  "camera": [key(0, orb([2.6, 5.8, 0.5], 10.4, 48, -30, 52)), key(d, orb([2.7, 5.8, 0.5], 9.8, 49, -33, 52), "inOut")],
                  "ov3": [mk("O4", 0.1, d), mk("X4", 0.3, d), {"type": "separation", "a": "X4", "b": "O4", "color": RED, "from": 0.5, "to": tlane - 0.2},
                          {"type": "passLane", "src": "O1", "dst": "O4", "color": RED, "from": tlane - 0.4, "to": d},
                          {"type": "blocked", "at": [3.95, 5.95], "color": RED, "from": tlane - 0.1, "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d}, letter("A", 0.0, d, wrong=0.0), letter("B", 0.0, d, wrong=tB - cuts["b"]),
                             chip("B · STILL GUARDED", 0.35, tlane - 0.35, "red", 470, 58),
                             chip("DEFENDER IN THE LANE", tlane - 0.3, d, "red", 470, 58)]})
    d = dur["c"]
    shots.append({"id": "c", "name": "C, wide open.", "at": cuts["c"], "play": "A", "remap": [[0, DEC], [d, DEC]],
                  "camera": [key(0, orb([3.6, 3.0, 0.4], 12.0, 48, -60, 54)), key(d, orb([3.7, 3.0, 0.4], 11.4, 49, -62, 54), "inOut")],
                  "ov3": [mk("O3", 0.05, d), mk("X3", 0.2, d),
                          {"type": "separation", "a": "X3", "b": "O3", "color": GOLD, "from": 0.35, "to": d},
                          {"type": "openSpace", "at": [6.5, 2.4], "r": 1.3, "color": GOLD, "from": 0.3, "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d}, letter("C", 0.0, d, right=tC - cuts["c"]),
                             letter("A", 0.0, d, wrong=0.0), letter("B", 0.0, d, wrong=0.0),
                             chip("C · WIDE OPEN", 0.3, d, "gold", 470, 66)]})

    # 6 KICK (real speed): kick, X4's second rotation too late, catch, corner three --------------------------------
    d = dur["kick"]
    tk = Lw("kick", 0, "kick")
    tnext, tlate = Lw("late", 1, "kick"), Lw("late", 4, "kick")
    rm = [[0, DEC + 0.12], [tk + 0.1, M["kick"]], [d, min(PL["A"]["duration"], M["kick"] + (d - tk - 0.1))]]
    t_catch, t_rel, t_make = inv(rm, M["catch"]), inv(rm, M["release"]), inv(rm, M["make"])
    cam = [key(0, WEAK), key(t_catch, orb([3.6, 3.5, 0.5], 12.5, 49, -75, 55), "inOut"),
           key(d, orb([4.6, 3.2, 0.6], 11.0, 52, -75, 52), "inOut")]
    shots.append({"id": "kick", "name": "Kick it to the corner. The next rotation is too late.", "at": cuts["kick"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [{"type": "ballPath", "src": "O1", "dst": "O3", "color": GOLD, "draw": 0.3, "from": round(tk, 3), "to": round(t_catch + 0.35, 3)},
                          mk("X4", tnext - 0.2, d), trail("X4", tnext - 0.2, d, 0.6), trail("X3", t_catch - 0.3, d, 0.6),
                          {"type": "separation", "a": "X4", "b": "O3", "color": RED, "from": tnext, "to": tlate + 0.5},
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.5, "from": t_make, "to": d}],
                  "screen": [letter("C", 0.0, t_catch, right=0.0, size=80),
                             chip("2ND ROTATION: TOO LATE", tnext - 0.1, max(tnext + 0.8, t_make - 0.05), "red", 470, 56),
                             chip("THREE.", t_make + 0.05, d, "gold", 470, 76)]})

    # 7 LESSON (rewind, top view): don't watch the ball, watch the help -------------------------------------------
    d = dur["lesson"]
    rw = 0.4
    th = L("help", "lesson")
    rm = [[0, min(PL["A"]["duration"], M["make"] + 0.3)], [rw, 0.9], [th + 0.3, DEC], [d, DEC]]
    shots.append({"id": "lesson", "name": "Don't watch the ball. Watch the help.", "at": cuts["lesson"], "play": "A", "remap": rm,
                  "camera": [key(0, orb([0.0, 4.6, 0.0], 19.0, 12, 0, 76)), key(d, orb([0.0, 4.6, 0.0], 18.6, 14, 0, 76), "inOut")],
                  "ov3": [{"type": "ballRing", "color": WHITE, "from": rw, "to": th},
                          mk("X3", th - 0.1, d),
                          {"type": "arrow3d", "player": "X3", "t0": M["help"], "t1": DEC, "color": RED, "width": 0.13, "draw": 0.4, "from": th, "to": d},
                          {"type": "openSpace", "at": [6.5, 2.4], "r": 1.25, "color": GOLD, "from": th + 0.3, "to": d}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             ttl(["DON'T WATCH", "THE BALL"], [1], rw - 0.05, th - 0.08, 250, 104),
                             ttl(["WATCH", "THE HELP"], [1], th - 0.05, d - 0.05, 250, 112)]})

    # 8 END: the question frame again, neutral letters (loop + comments) ---------------------------------------------
    d = dur["end"]
    tt = L("tell", "end")
    shots.append({"id": "end", "name": "Did you find him? Tell us what you picked. (question frame, loop)", "at": cuts["end"], "play": "A",
                  "remap": [[0, DEC], [d, DEC]], "camera": [key(0, BROAD2), key(d, BROAD, "inOut")],
                  "ov3": [mk("O2", 0.1, d), mk("O4", 0.15, d), mk("O3", 0.2, d)],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d},
                             letter("A", 0.1, d), letter("B", 0.15, d), letter("C", 0.2, d),
                             ttl(["DID YOU", "FIND HIM?"], [1], 0.0, tt - 0.05, 250, 112),
                             ttl(["A, B OR C?", "COMMENT IT"], [0], tt - 0.02, d - 0.1, 250, 100),
                             {"type": "logo", "big": False, "y": 1560, "from": tt + 0.3, "to": d - 0.05}]})
    ep = {
        "id": "iq01-open-player" + ("-trial" if trial else ""), "title": "CAN YOU FIND THE OPEN PLAYER?", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33", "words": words,
        "subtitleGroups": [len(t.split()) for _, t in LINES],
        "subtitleBlock": True, "subtitleY": 1390,
        "keywords": ["beats", "help.", "Freeze", "open?", "A,", "B,", "C?", "Lock", "low", "defender.", "corner", "home.", "guarded,",
                     "lane.", "wide", "open.", "Kick", "corner.", "late.", "ball.", "help.", "find", "picked."],
        "gradeBottom": 0.3, "shots": shots, "plays": PL,
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    rel_kick = cuts["kick"] + tk
    plan = {"duration": t_end,
            "states": [[0.0, cuts["q"] + fz, "A"], [cuts["q"] + fz, tthink, "B"], [tthink, tlock - 0.05, "BREAK"], [tlock - 0.05, rel_kick, "B"], [rel_kick, cuts["lesson"], "A"],
                       [cuts["lesson"], cuts["end"], "B"], [cuts["end"], t_end + 1, "A"]],
            "releases": [round(rel_kick, 3)],
            "hits": [round(cuts["q"] + fz, 3), round(tlock - 0.05, 3), round(tC, 3), round(cuts["end"], 3)]}
    meta = {"duration": t_end, "cuts": {k: round(v, 3) for k, v in cuts.items()}, "dur": dur, "plan": plan}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words", default=os.path.join(D, "iq01", "iq01-voice.words.json"))
    ap.add_argument("--voice", default="iq01/voice.mix.wav")
    ap.add_argument("--music")
    ap.add_argument("--fit")
    ap.add_argument("--plan")
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
    if a.plan:
        json.dump(meta["plan"], open(a.plan, "w"), indent=1)
    print(json.dumps({k: meta[k] for k in ("duration", "cuts")}))
