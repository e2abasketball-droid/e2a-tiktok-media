#!/usr/bin/env python3
"""E2A BASKETBALL IQ 01 V2 - "CAN YOU FIND THE OPEN PLAYER?" rebuild (owner brief 2026-11-26 23:38Z).
V1 (tactical/episodes/_gen-iq01.py, commit b25d9f5) stays untouched and recoverable.
Architecture: HOOK (question frame, letters on frame 0) -> ACTION (rewind, drive, help) -> FREEZE + A/B/C -> honest
2.0 s DECISION window (bar = the real inserted silence) -> A (easy pass, defender home) -> B (lane) -> REPLAY of the low
defender (spotlight + ghost of where he started) -> C (the read) + KICK at real speed (2nd rotation a step late) ->
LESSON (top view) -> LOOP (camera lands on the exact frame-0 framing).
Every freeze has a moving camera. Scenario data (letters, distances, cues) lives in tactical/episodes/iq01v2/scenario.json.
  python3 tactical/episodes/_gen-iq01v2.py --hook A|B --out props.json [--voice p] [--music p] [--fit ep.json] [--plan plan.json]"""
import argparse, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
PL = {"A": json.load(open(os.path.join(T, "tactical", "plays", "iq01-open-player.json")))}
SC = json.load(open(os.path.join(D, "iq01v2", "scenario.json")))
GOLD, NAVY, WHITE, RED = "#C9A24D", "#0B1C3D", "#FFFFFF", "#E5483A"
M = PL["A"]["marks"]
DEC = M["decide"]
LET = {c["letter"]: c["player"] for c in SC["choices"]}
DIST = {c["letter"]: c["defender_distance_m"] for c in SC["choices"]}

HOOK_LINES = {"A": [("hook", "Three teammates. One right pass.")],
              "B": [("hook", "One defender gives this whole play away.")]}
BODY = [("beats", "He beats his man."), ("help", "Here comes the help."), ("freeze", "Freeze."), ("abc", "A, B, or C?"),
        ("two", "Two seconds."), ("a", "A is the easy pass."), ("ahome", "But his defender stayed home."),
        ("b", "B? His defender is sitting in the passing lane."), ("watch", "Now watch the low defender."),
        ("left", "He left the corner to stop the drive."), ("read", "That's the read. C."), ("kick", "Kick it."),
        ("late", "The next rotation is a step too late."), ("ball", "Stop watching the ball."), ("helpw", "Watch the help."),
        ("got", "Got it in two seconds?"), ("run", "Run it back.")]


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
DECIDE = orb([0.0, 4.8, 0.0], 17.0, 46, 0, 84)       # the question frame: all 8 players inside a 9:16 frame (cam-probe), ~100 px
OPEN = orb([0.0, 4.8, 0.0], 16.6, 46, 6, 84)         # frame 0 AND the last frame (seamless loop)
PUSH = orb([0.0, 4.8, 0.0], 16.6, 47, -3, 84)        # slow push during the decision window
WEAK = orb([2.6, 3.9, 0.4], 14.5, 46, -75, 58)       # weak side: driver, X3, X4, O3 corner
CAM_A = (orb([-5.3, 3.3, 0.5], 10.6, 50, -26, 52), orb([-5.7, 3.0, 0.5], 9.6, 52, -36, 50))
CAM_B = (orb([3.0, 6.3, 0.5], 12.0, 48, -50, 60), orb([3.2, 6.4, 0.5], 11.0, 49, -56, 60))  # O1 -> O4 lane + X4 in it
CAM_C = (orb([3.6, 3.0, 0.4], 12.4, 48, -56, 55), orb([3.8, 3.0, 0.4], 11.6, 49, -62, 54))


def inv(remap, pt):
    for (a, pa), (b, pb) in zip(remap, remap[1:]):
        if pa <= pt <= pb and pb > pa:
            return a + (b - a) * (pt - pa) / (pb - pa)
    raise ValueError(pt)


r3 = lambda x: round(x, 3)
ttl = lambda lines, gold, fr, to, y=250, size=104: {"type": "title", "lines": lines, "gold": gold, "reveal": "mask", "from": r3(fr), "to": r3(to), "y": y, "size": size}
chip = lambda text, fr, to, tone="gold", y=470, size=60: {"type": "chip", "text": text, "tone": tone, "align": "center", "size": size, "from": r3(fr), "to": r3(to), "y": y}
pin = lambda p, text, fr, to, tone="gold", size=44: {"type": "pin", "player": p, "text": text, "tone": tone, "from": r3(fr), "to": r3(to), "size": size}
trail = lambda p, fr, to, ln=0.7: {"type": "motionTrail", "player": p, "len": ln, "color": GOLD if p[0] == "O" else RED, "from": r3(fr), "to": r3(to)}
mk = lambda p, fr, to: {"type": "marker", "player": p, "team": "attack" if p[0] == "O" else "defense", "from": r3(fr), "to": r3(to)}
lane = lambda dst, col, fr, to: {"type": "passLane", "src": "O1", "dst": dst, "color": col, "from": r3(fr), "to": r3(to)}
focus = lambda p, fr, to, r=230, st=0.55: {"type": "focus", "player": p, "r": r, "strength": st, "from": r3(fr), "to": r3(to)}


def letter(L, fr, to, wrong=None, right=None, size=96):
    it = {"type": "letter", "player": LET[L], "text": L, "from": r3(fr), "to": r3(to), "size": size, "z": 2.2}
    if wrong is not None:
        it["wrong"] = r3(wrong)
    if right is not None:
        it["right"] = r3(right)
    return it


def build(words, voice, music, hook):
    lines = HOOK_LINES[hook] + BODY
    W = line_words(words, lines)
    s0 = lambda k: W[k][0]["start"]
    e0 = lambda k: W[k][-1]["end"]
    wd = lambda k, i: W[k][i]["start"]
    t_end = r3(e0("run") + 0.5)
    cuts = {"open": 0.0, "q": s0("beats") - 0.1, "a": s0("a") - 0.12, "b": s0("b") - 0.1, "replay": s0("watch") - 0.12,
            "c": s0("read") - 0.12, "lesson": s0("ball") - 0.12, "end": s0("got") - 0.12}
    order = list(cuts)
    dur = {k: r3((cuts[order[i + 1]] if i + 1 < len(order) else t_end) - cuts[k]) for i, k in enumerate(order)}
    L = lambda k, sh: s0(k) - cuts[sh]
    Lw = lambda k, i, sh: wd(k, i) - cuts[sh]
    E = lambda k, sh: e0(k) - cuts[sh]
    think = SC["decision_window"]
    t_think0 = think["edit_start_s"][hook]
    t_think1 = t_think0 + think["seconds"]
    shots = []

    # 1 HOOK: the question frame on frame 0 (letters already up, camera already moving) --------------------------
    d = dur["open"]
    scr = [{"type": "stamp", "text": "BASKETBALL IQ", "badge": "EP 01", "tone": "gold", "y": 110, "instant": True, "from": 0.0, "to": d},
           letter("A", -0.8, d), letter("B", -0.8, d), letter("C", -0.8, d)]   # negative start: fully formed on frame 0
    ov = [mk("O2", -0.8, d), mk("O4", -0.8, d), mk("O3", -0.8, d)]
    if hook == "A":
        t1 = Lw("hook", 2, "open")
        scr += [{**ttl(["THREE", "TEAMMATES"], [1], -0.8, t1 - 0.04, 250, 112), "noOut": True},
                ttl(["ONE RIGHT", "PASS"], [0], t1, d, 250, 112)]
        ov += [lane("O2", WHITE, t1 + 0.05, d), lane("O4", WHITE, t1 + 0.1, d), lane("O3", WHITE, t1 + 0.15, d)]
    else:
        t1 = Lw("hook", 3, "open")
        scr += [{**ttl(["ONE DEFENDER", "GIVES IT AWAY"], [0], -0.8, d), "noOut": True}]
        ov += [mk("X1", -0.8, d), mk("X2", -0.8, d), mk("X3", -0.8, d), mk("X4", -0.8, d)]
    shots.append({"id": "open", "name": f"HOOK {hook}: the question frame on frame 0, camera arcing", "at": 0.0, "play": "A",
                  "remap": [[0, DEC], [d, DEC]], "camera": [key(0, OPEN), key(d, orb([0.0, 4.8, 0.0], 16.2, 47, 2, 84), "inOut")],
                  "ov3": ov, "screen": scr})

    # 2 ACTION + FREEZE + A/B/C + DECISION WINDOW (one continuous shot) ------------------------------------------
    d = dur["q"]
    rw = 0.35
    fz = L("freeze", "q")
    thelp = L("help", "q")
    tabc = [Lw("abc", i, "q") for i in (0, 1, 3)]
    c0, c1 = t_think0 - cuts["q"], t_think1 - cuts["q"]
    rm = [[0, DEC], [rw, 0.3], [rw + 1.15, 1.45], [fz, DEC], [d, DEC]]
    cam = [key(0, orb(fol(["O1", "X1"], 0.8), 9.0, 60, -8, 50)),
           key(rw + 0.9, orb(fol(["O1", "X1", "X3"], 0.8), 11.0, 52, -5, 56), "inOut"),
           key(fz, DECIDE, "inOut"), key(c0, orb([0.0, 4.8, 0.0], 16.8, 46, 1, 84), "inOut"), key(c1, PUSH, "inOut"), key(d, PUSH)]
    shots.append({"id": "q", "name": "ACTION: rewind, drive, help -> FREEZE -> A/B/C -> 2.0 s decision window", "at": cuts["q"], "play": "A",
                  "remap": rm, "camera": cam,
                  "ov3": [trail("O1", rw, fz), trail("X3", thelp - 0.2, fz, 0.6), mk("X3", thelp - 0.1, fz + 0.4),
                          mk("O2", tabc[0], d), mk("O4", tabc[1], d), mk("O3", tabc[2], d),
                          lane("O2", WHITE, tabc[0] + 0.05, d), lane("O4", WHITE, tabc[1] + 0.05, d), lane("O3", WHITE, tabc[2] + 0.05, d)],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             pin("X3", "HELP", thelp, fz - 0.05, "red", 44),
                             {"type": "freeze", "from": fz, "to": d},
                             ttl(["FREEZE."], [0], fz - 0.03, tabc[0] - 0.05, 250, 120),
                             ttl(["A, B", "OR C?"], [1], tabc[0] - 0.03, c0 - 0.05, 250, 112),
                             letter("A", tabc[0], d), letter("B", tabc[1], d), letter("C", tabc[2], d),
                             {"type": "countdown", "label": "YOUR CALL", "from": r3(c0), "to": r3(c1), "y": 260}]})

    # 3 A: the easy pass, defender home ------------------------------------------------------------------------
    d = dur["a"]
    teasy, thome = Lw("a", 3, "a"), Lw("ahome", 4, "a")
    tdef = Lw("ahome", 2, "a")
    shots.append({"id": "a", "name": "A is the easy pass. But his defender stayed home.", "at": cuts["a"], "play": "A", "remap": [[0, DEC], [d, DEC]],
                  "camera": [key(0, PUSH), key(0.55, CAM_A[0], "inOut"), key(d, CAM_A[1], "inOut")],
                  "ov3": [mk("O2", 0.0, d), lane("O2", WHITE, 0.1, tdef), mk("X2", tdef - 0.1, d),
                          {"type": "separation", "a": "X2", "b": "O2", "color": RED, "from": r3(tdef), "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d}, letter("A", 0.0, d, wrong=thome),
                             letter("B", 0.0, d), letter("C", 0.0, d),
                             chip("EASY PASS", teasy - 0.05, tdef - 0.05, "gold", 320, 60),
                             pin("X2", f"{DIST['A']:.1f} M", tdef + 0.1, d, "red", 46),
                             chip("DEFENDER HOME", thome - 0.1, d, "red", 320, 60)]})

    # 4 B: defender in the passing lane ------------------------------------------------------------------------
    d = dur["b"]
    tdef, tlane = Lw("b", 2, "b"), Lw("b", 7, "b")
    shots.append({"id": "b", "name": "B? His defender is sitting in the passing lane.", "at": cuts["b"], "play": "A", "remap": [[0, DEC], [d, DEC]],
                  "camera": [key(0, CAM_A[1]), key(0.6, CAM_B[0], "inOut"), key(d, CAM_B[1], "inOut")],
                  "ov3": [mk("O4", 0.0, d), mk("X4", tdef - 0.1, d), lane("O4", WHITE, 0.1, tlane - 0.15),
                          lane("O4", RED, tlane - 0.15, d), {"type": "blocked", "at": SC["spots"]["X4SAG"], "color": RED, "from": r3(tlane), "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d},   # A is off-frame here: no badge (it would clamp to the edge)
                             letter("B", 0.0, d, wrong=tlane + 0.1),
                             chip("DEFENDER IN THE LANE", tlane - 0.2, d, "red", 470, 60)]})

    # 5 REPLAY: the low defender (spotlight + ghost of where he started) ---------------------------------------
    d = dur["replay"]
    rw = 0.4
    tlow, tleft, tcorner = Lw("watch", 3, "replay"), Lw("left", 1, "replay"), Lw("left", 3, "replay")
    rm = [[0, DEC], [rw, 0.6], [tleft + 0.2, 1.2], [d - 0.3, DEC], [d, DEC]]
    shots.append({"id": "replay", "name": "Now watch the low defender. He left the corner to stop the drive.", "at": cuts["replay"], "play": "A",
                  "remap": rm, "camera": [key(0, WEAK), key(d, orb([2.6, 3.8, 0.4], 13.4, 47, -71, 57), "inOut")],
                  "ov3": [mk("X3", tlow - 0.15, d), trail("X3", tleft - 0.3, d, 0.6),
                          {"type": "ghost", "player": "X3", "t": 0.0, "color": RED, "link": True, "from": r3(tleft), "to": d},
                          {"type": "arrow3d", "player": "X3", "t0": M["help"], "t1": DEC, "color": RED, "width": 0.12, "draw": 0.5, "from": r3(tleft + 0.1), "to": d},
                          {"type": "openSpace", "at": SC["spots"]["CORNER_GAP"], "r": 1.25, "color": GOLD, "from": r3(tcorner), "to": d}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw}, focus("X3", tlow - 0.1, d, 250, 0.5),
                             pin("X3", "LOW HELP", tlow, d, "red", 44), letter("C", rw, d, size=84),
                             chip("HE LEFT THE CORNER", tcorner - 0.1, d, "red", 470, 58)]})

    # 6 C (the read) + KICK at real speed -----------------------------------------------------------------------
    d = dur["c"]
    tC = Lw("read", 3, "c")
    tk = L("kick", "c")
    tnext = Lw("late", 1, "c")
    rm = [[0, DEC], [tk - 0.1, DEC], [tk + 0.12, M["kick"]], [d, min(PL["A"]["duration"], M["kick"] + (d - tk - 0.12))]]
    t_catch, t_make = inv(rm, M["catch"]), inv(rm, M["make"])
    shots.append({"id": "c", "name": "That's the read. C. Kick it. The next rotation is a step too late.", "at": cuts["c"], "play": "A", "remap": rm,
                  "camera": [key(0, CAM_C[0]), key(tk, CAM_C[1], "inOut"), key(t_catch, orb([3.6, 3.5, 0.5], 12.5, 49, -75, 55), "inOut"),
                             key(d, orb([4.6, 3.2, 0.6], 11.2, 52, -75, 52), "inOut")],
                  "ov3": [mk("O3", 0.0, t_catch + 0.4), mk("X3", 0.1, tk),
                          {"type": "separation", "a": "X3", "b": "O3", "color": GOLD, "from": 0.3, "to": r3(tk)},
                          {"type": "openSpace", "at": SC["spots"]["CORNER_GAP"], "r": 1.3, "color": GOLD, "from": r3(tC - 0.1), "to": r3(tk + 0.3)},
                          {"type": "ballPath", "src": "O1", "dst": "O3", "color": GOLD, "draw": 0.3, "from": r3(tk), "to": r3(t_catch + 0.35)},
                          mk("X4", tnext - 0.2, d), trail("X4", tnext - 0.2, d, 0.6),
                          {"type": "separation", "a": "X4", "b": "O3", "color": RED, "from": r3(tnext), "to": r3(t_make - 0.2)},
                          {"type": "glow", "hoop": True, "r": 1.2, "color": GOLD, "strength": 0.5, "from": r3(t_make), "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": r3(tk - 0.1)},
                             letter("C", 0.0, t_catch, right=tC), letter("A", 0.0, tk, wrong=0.0), letter("B", 0.0, tk, wrong=0.0),
                             pin("X3", f"{DIST['C']:.1f} M", 0.35, tC - 0.05, "gold", 46),
                             chip(f"C · WIDE OPEN · {DIST['C']:.1f} M", tC, tk - 0.05, "gold", 470, 62),
                             chip("2ND ROTATION: A STEP LATE", tnext - 0.1, t_make - 0.1, "red", 470, 56),
                             chip("THREE.", t_make + 0.05, d, "gold", 470, 76)]})

    # 7 LESSON (rewind, top view): stop watching the ball, watch the help -------------------------------------------
    d = dur["lesson"]
    rw = 0.4
    th = L("helpw", "lesson")
    rm = [[0, min(PL["A"]["duration"], M["make"] + 0.3)], [rw, 0.9], [th + 0.35, DEC], [d, DEC]]
    shots.append({"id": "lesson", "name": "Stop watching the ball. Watch the help.", "at": cuts["lesson"], "play": "A", "remap": rm,
                  "camera": [key(0, orb([0.0, 4.6, 0.0], 19.0, 12, 0, 76)), key(d, orb([0.0, 4.4, 0.0], 17.4, 16, 0, 76), "inOut")],
                  "ov3": [{"type": "ballRing", "color": WHITE, "from": r3(rw), "to": r3(th)}, mk("X3", th - 0.1, d),
                          {"type": "ghost", "player": "X3", "t": 0.0, "color": RED, "link": True, "from": r3(th), "to": d},
                          {"type": "arrow3d", "player": "X3", "t0": M["help"], "t1": DEC, "color": RED, "width": 0.13, "draw": 0.4, "from": r3(th), "to": d}],
                  "screen": [{"type": "rewind", "from": 0.0, "to": rw},
                             ttl(["STOP WATCHING", "THE BALL"], [1], rw - 0.05, th - 0.06, 250, 100),
                             ttl(["WATCH", "THE HELP"], [1], th - 0.04, d - 0.05, 250, 116)]})

    # 8 END -> LOOP: back to the question frame; the camera lands exactly on frame 0's framing --------------------
    d = dur["end"]
    tr_ = L("run", "end")
    shots.append({"id": "end", "name": "Got it in two seconds? Run it back. (lands on frame 0)", "at": cuts["end"], "play": "A",
                  "remap": [[0, DEC], [d, DEC]], "camera": [key(0, DECIDE), key(d, OPEN, "inOut")],
                  "ov3": [mk("O2", 0.0, d), mk("O4", 0.0, d), mk("O3", 0.0, d)] + ([mk("X1", 0, d), mk("X2", 0, d), mk("X3", 0, d), mk("X4", 0, d)] if hook == "B" else []),
                  "screen": [letter("A", 0.05, d), letter("B", 0.1, d), letter("C", 0.15, d),
                             ttl(["GOT IT IN", "2 SECONDS?"], [1], 0.0, tr_ - 0.05, 250, 108),
                             ttl(["RUN IT", "BACK"], [1], tr_ - 0.03, d, 250, 116),
                             {"type": "stamp", "text": "BASKETBALL IQ", "badge": "EP 01", "tone": "gold", "y": 110, "from": r3(tr_), "to": d},
                             {"type": "logo", "big": False, "y": 1600, "from": r3(tr_ + 0.1), "to": d}]})
    kw = ["teammates.", "right", "defender", "away.", "help.", "Freeze.", "C?", "seconds.", "easy", "home.", "lane.", "low",
          "corner", "read.", "C.", "late.", "help.", "back."]
    ep = {"id": f"iq01v2-open-player-{hook}", "title": "CAN YOU FIND THE OPEN PLAYER?", "fps": 30,
          "voice": voice, "tail": r3(t_end - words[-1]["end"]), "autoSfx": False, "pinV2": True, "env": "cinema",
          "athleteRenderer": "v33", "words": words, "subtitleGroups": [len(t.split()) for _, t in lines],
          "subtitleBlock": True, "subtitleCommas": True, "subtitleY": 1390, "keywords": kw, "gradeBottom": 0.3, "shots": shots, "plays": PL}
    if music:
        ep["music"] = {"src": music, "volume": 1}
    q = cuts["q"]
    rel_kick = cuts["c"] + tk
    plan = {"duration": t_end,
            "states": [[0.0, q + fz, "A"], [q + fz, t_think0, "B"], [t_think0, t_think1, "BREAK"], [t_think1, rel_kick, "B"],
                       [rel_kick, cuts["lesson"], "A"], [cuts["lesson"], cuts["end"], "B"], [cuts["end"], t_end + 1, "A"]],
            "releases": [r3(rel_kick)], "hits": [r3(q + fz), r3(cuts["c"] + tC)]}
    meta = {"duration": t_end, "cuts": {k: r3(v) for k, v in cuts.items()}, "think": [t_think0, t_think1], "plan": plan}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--hook", default="A")
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice")
    ap.add_argument("--music")
    ap.add_argument("--fit")
    ap.add_argument("--plan")
    a = ap.parse_args()
    words = json.load(open(os.path.join(D, "iq01v2", f"iq01v2-{a.hook}.words.json")))
    props, meta = build(words, a.voice or f"iq01v2/voice-{a.hook}.mix.wav", a.music, a.hook)
    json.dump(props, open(a.out, "w"))
    if a.fit:
        ep = dict(props["episode"]); ep["plays"] = {k: v["id"] for k, v in PL.items()}
        json.dump(ep, open(a.fit, "w")); json.dump(words, open(a.fit.replace(".json", ".words.json"), "w"))
    if a.plan:
        json.dump(meta["plan"], open(a.plan, "w"), indent=1)
    print(json.dumps({k: meta[k] for k in ("duration", "cuts", "think")}))
