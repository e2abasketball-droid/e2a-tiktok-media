#!/usr/bin/env python3
"""Floppy (curl / fade) and Iverson cut (catch / backdoor): owner brief 2026-11-15 10:52Z.
Original E2A possessions (standard FIBA/European half-court concepts, generic coaching knowledge, no copied diagram).
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. With the house cameras (yaw 0 = from
half court, basket at the top) x < 0 appears on the RIGHT of the screen, so "right side" in the brief = x < 0.

FLOPPY  O2 starts under the rim. O5 screens on the right block (x<0), O4 on the left block. O1 at the top, a step to
        the right (same spot in A and B). Right corner kept empty; X3/X4 separated on the weak side.
  A floppy-a-curl  X2 chases on O2's back hip -> O2 rubs O5's shoulder and CURLS tight to the rim, lead pass, layup.
  B floppy-b-fade  X2 shortcuts UNDER through the paint -> O2 FADES to the right corner, feet behind the line, three.
IVERSON O2 starts on the left wing (x>0) and sprints right over both elbow screens (O4 left elbow, O5 right elbow)
        to the extended right elbow. O1 at the top, a step to the right.
  A iverson-a-catch     X2 trails -> catch outside the far elbow, face up.
  B iverson-b-backdoor  X2 jumps the passing lane near the 2nd screen -> sell, plant, backdoor, lead bounce pass, layup.
Writes tactical/specs/<id>.spec.json and builds tactical/plays/<id>.json with scripts/build-play.mts."""
import json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC_F = "original E2A play (standard FIBA/European floppy action, generic coaching knowledge)"
SRC_I = "original E2A play (standard FIBA/European Iverson cut, generic coaching knowledge)"

# ---------------------------------------------------------------- FLOPPY
FP = [P("O1", "O", "Passer, top (a step to the right)"), P("O2", "O", "Shooter: starts under the rim"),
      P("O3", "O", "Weak-side wing"), P("O4", "O", "Screener, left block"), P("O5", "O", "Screener, right block (the side used)"),
      P("X1", "X", "On the passer", "O1"), P("X2", "X", "On the shooter: trails (A) / shortcuts under (B)", "O2"),
      P("X3", "X", "Weak-side wing", "O3"), P("X4", "X", "On the left screener", "O4"), P("X5", "X", "On the right screener", "O5")]
FS = {"O1": [-1.5, 8.7], "X1": [-0.45, 8.05], "O2": [0.0, 1.0], "X2": [0.45, 1.55], "O5": [-2.75, 2.05],
      "X5": [-2.15, 2.85], "O4": [2.75, 2.05], "X4": [2.15, 2.85], "O3": [5.9, 6.4], "X3": [5.1, 5.85]}
F_RUN = [{"at": 0.55, "via": [[-1.3, 0.85], [-2.55, 1.1], [-3.3, 1.7]], "to": [-3.6, 2.7], "speed": 5.0}]


def floppy(kind):
    legs = {"O2": [dict(l) for l in F_RUN], "X1": [], "O1": [], "O3": [], "X3": [], "O4": [], "X4": []}
    acts = {"O5": [{"type": "screen", "from": 0.3, "to": 2.6, "face": "X2"}],
            "O4": [{"type": "screen", "from": 0.3, "to": 2.0, "face": "X2"}],
            "X1": [st("O1", 0, 6.0)], "X3": [st("O1", 0, 6.0)], "X4": [st("O2", 0, 6.0)]}
    if kind == "curl":
        # rub O5's top shoulder, curl tight back to the rim
        legs["O2"].append({"at": "+0.0", "via": [[-3.35, 3.6], [-2.45, 3.85]], "to": [-1.45, 3.25], "speed": 4.6})
        legs["O2"].append({"at": "+0.0", "to": [-0.55, 2.55], "speed": 4.4})
        # X2 chases on the back hip: same path ~1 m behind, then stuck behind the curl
        legs["X2"] = [{"at": 0.8, "via": [[-1.0, 1.2], [-2.3, 1.2], [-3.4, 1.55]], "to": [-3.8, 2.95], "speed": 4.9},
                      {"at": "+0.0", "via": [[-3.15, 3.85]], "to": [-2.25, 3.75], "speed": 4.6}]
        legs["X5"] = [{"at": 0.6, "to": [-4.4, 4.45], "speed": 2.4}]  # X5 shows high/outside: rim left open
        c = F_CURL
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": c["pass"]},
                {"type": "pass", "from": "O1", "to": "O2", "t0": c["pass"], "t1": c["catch"], "style": "chest"},
                {"type": "hold", "player": "O2", "from": c["catch"], "to": c["lay"], "dribble": True},
                {"type": "layup", "player": "O2", "t0": c["lay"], "t1": c["lay"] + 0.4, "make": True}]
        marks = {"start": 0, "screen": 0.3, "run": 0.55, "trail": c["rub"], "rub": c["rub"], "curl": c["rub"] + 0.15,
                 "pass": c["pass"], "catch": c["catch"], "finish": c["lay"], "make": c["lay"] + 0.4, "end": 5.6}
        acts["X5"] = [st("O2", 0.6, 5.6)]
        acts["O2"] = [{"type": "celebrate", "from": c["lay"] + 0.7, "to": 5.5}]
        claims = [
            {"type": "near", "a": "O2", "b": "O5", "at": "rub", "max": 1.3, "says": "Curl tight off the screen."},
            {"type": "near", "a": "X2", "b": "O2", "at": "trail", "max": 1.9, "says": "He's on your back hip."},
            {"type": "far", "a": "X5", "b": "O2", "at": "catch", "min": 1.3, "says": "Catch on the move."},
            {"type": "near_rim", "player": "O2", "at": "finish", "max": 1.6, "says": "Finish at the rim."},
            {"type": "order", "marks": ["screen", "run", "rub", "pass", "catch", "finish"], "says": "screen, rub, curl, pass, layup"}]
        return {"id": "floppy-a-curl", "title": "Floppy A: he trails, curl to the rim", "duration": 5.6, "concept": "floppy",
                "source": SRC_F, "squareUp": True, "players": FP, "start": FS, "legs": legs, "ball": ball,
                "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O2 starts under the rim; O5 screens on the right block, O4 on the left.",
                          "X2 chases on O2's back hip; O2 rubs O5's shoulder and curls tight.",
                          "X5 shows high and outside: the rim is open. Lead chest pass, layup."]}
    # fade: fade to the right corner, feet behind the line
    legs["O2"][0] = {"at": 0.55, "via": [[-1.3, 0.85], [-2.55, 1.1]], "to": [-3.45, 1.55], "speed": 5.0}
    legs["O2"].append({"at": "+0.0", "via": [[-5.0, 1.45]], "to": [-6.95, 1.25], "speed": 4.6})
    # X2 SHORTCUTS UNDER: through the paint, inside the screen, to wait for the curl
    legs["X2"] = [{"at": 0.75, "via": [[-0.55, 2.65], [-1.3, 3.65]], "to": [-2.2, 4.05], "speed": 4.6},
                  {"at": "+0.15", "to": [-3.1, 3.05], "speed": 3.6}]
    legs["X5"] = [{"at": 0.8, "to": [-1.65, 2.45], "speed": 1.6}]  # X5 sinks to take away the curl
    f = F_FADE
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": f["pass"]},
            {"type": "pass", "from": "O1", "to": "O2", "t0": f["pass"], "t1": f["catch"], "style": "overhead"},
            {"type": "hold", "player": "O2", "from": f["catch"], "to": f["rel"]},
            {"type": "shot", "player": "O2", "t0": f["rel"], "t1": f["rel"] + 1.1, "make": True, "three": True}]
    marks = {"start": 0, "screen": 0.3, "run": 0.55, "under": 1.4, "fade": f["fade"], "pass": f["pass"],
             "catch": f["catch"], "release": f["rel"], "make": f["rel"] + 1.1, "end": 6.0}
    acts["X5"] = [st("O2", 0.8, 6.0)]
    acts["X2"] = [{"type": "contest", "from": f["rel"] - 0.1, "to": f["rel"] + 0.6}]
    acts["O2"] = [{"type": "celebrate", "from": f["rel"] + 1.2, "to": 6.0}]
    claims = [
        {"type": "near", "a": "O2", "b": "O5", "at": "fade", "max": 1.4, "says": "Off the screen."},
        {"type": "far", "a": "X2", "b": "O2", "at": "catch", "min": 3.0, "says": "He shortcuts through the paint and leaves the corner."},
        {"type": "behind_arc", "player": "O2", "at": "catch", "says": "Get your feet behind the line."},
        {"type": "open", "player": "O2", "at": "release", "min": 2.5, "says": "Let it fly."},
        {"type": "order", "marks": ["screen", "run", "under", "fade", "pass", "catch", "release", "make"], "says": "under, fade, pass, three"}]
    return {"id": "floppy-b-fade", "title": "Floppy B: he goes under, fade to the corner", "duration": 6.0, "concept": "floppy",
            "source": SRC_F, "squareUp": True, "players": FP, "start": FS, "legs": legs, "ball": ball,
            "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start as floppy-a-curl.",
                      "X2 shortcuts under, through the paint; X5 sinks to take away the curl.",
                      "O2 fades to the right corner, feet behind the line; overhead pass from O1; three."]}


# ---------------------------------------------------------------- IVERSON
IP = [P("O1", "O", "Passer, top (a step to the right)"), P("O2", "O", "Cutter: left wing to the far elbow"),
      P("O3", "O", "Left corner"), P("O4", "O", "Screener, left elbow"), P("O5", "O", "Screener, right elbow"),
      P("X1", "X", "On the passer", "O1"), P("X2", "X", "On the cutter: trails (A) / denies (B)", "O2"),
      P("X3", "X", "Left corner", "O3"), P("X4", "X", "On the left-elbow screener", "O4"), P("X5", "X", "On the right-elbow screener", "O5")]
IS = {"O1": [-1.0, 9.3], "X1": [0.05, 8.75], "O2": [5.3, 6.7], "X2": [4.5, 7.6], "O4": [2.35, 6.05],
      "X4": [1.75, 5.35], "O5": [-2.35, 6.05], "X5": [-1.75, 5.35], "O3": [6.6, 1.3], "X3": [5.75, 2.0]}
I_RUN = {"at": 0.45, "via": [[3.9, 6.95], [2.35, 6.95], [0.0, 7.0], [-2.3, 6.95]], "speed": 5.6}


def iverson(kind):
    legs = {"X1": [], "O3": [], "X3": []}
    acts = {"O4": [{"type": "screen", "from": 0.3, "to": 1.6, "face": "X2"}],
            "O5": [{"type": "screen", "from": 0.3, "to": 2.2, "face": "X2"}],
            "X1": [st("O1", 0, 6.0)], "X3": [st("O1", 0, 6.0)], "X4": [st("O1", 0, 6.0)]}
    # the bigs pop away after the screens: O4 to the left slot, O5 to the right short corner? no: top-left, the lane stays empty
    legs["O4"] = [{"at": 1.7, "to": [3.4, 7.9], "speed": 3.0}]
    legs["X4"] = [{"at": 1.8, "to": [2.6, 6.6], "speed": 2.8}]
    legs["O5"] = [{"at": 2.25, "to": [0.9, 8.0], "speed": 3.6}]
    legs["X5"] = [{"at": 2.3, "to": [0.55, 7.1], "speed": 3.4}]
    if kind == "catch":
        legs["O2"] = [{**I_RUN, "to": [-3.95, 6.75]}]
        legs["X2"] = [{"at": 0.9, "via": [[3.7, 7.45], [2.0, 7.1], [0.0, 6.95]], "to": [-2.3, 6.85], "speed": 5.2}]
        c = I_CATCH
        ball = [{"type": "hold", "player": "O1", "from": 0, "to": c["pass"]},
                {"type": "pass", "from": "O1", "to": "O2", "t0": c["pass"], "t1": c["catch"], "style": "chest"},
                {"type": "hold", "player": "O2", "from": c["catch"], "to": 5.6}]
        marks = {"start": 0, "screen1": c["s1"], "screen2": c["s2"], "trail": c["s2"], "pass": c["pass"],
                 "catch": c["catch"], "faceup": c["catch"] + 0.5, "end": 5.6}
        acts["X2"] = [st("O2", c["catch"], 5.6)]
        claims = [
            {"type": "near", "a": "O2", "b": "O4", "at": "screen1", "max": 1.4, "says": "Sprint over both elbow screens."},
            {"type": "near", "a": "O2", "b": "O5", "at": "screen2", "max": 1.4, "says": "Sprint over both elbow screens."},
            {"type": "far", "a": "X2", "b": "O2", "at": "catch", "min": 1.3, "says": "If your defender trails..."},
            {"type": "open", "player": "O2", "at": "catch", "min": 1.3, "says": "catch just outside the far elbow."},
            {"type": "order", "marks": ["screen1", "screen2", "pass", "catch", "faceup"], "says": "over both screens, catch, face up"}]
        return {"id": "iverson-a-catch", "title": "Iverson cut A: he trails, catch at the far elbow", "duration": 5.6,
                "concept": "iverson-cut", "source": SRC_I, "squareUp": True, "players": IP, "start": IS, "legs": legs,
                "ball": ball, "marks": marks, "actions": acts, "claims": claims,
                "notes": ["O2 sprints from the left wing over both elbow screens.",
                          "X2 trails a step behind. O2 shows his hands, catches outside the far elbow and faces up."]}
    b = I_BACK
    legs["O2"] = [{**I_RUN, "via": I_RUN["via"][:3], "to": [-2.75, 7.05]},
                  {"at": "+0.0", "to": [-3.15, 7.25], "dur": 0.3},                 # sell the catch: a step up to the ball
                  {"at": "+0.06", "via": [[-2.6, 5.5]], "to": [-1.1, 3.0], "speed": 6.0},  # plant, diagonal backdoor
                  {"at": "+0.06", "to": [-0.55, 2.25], "speed": 3.8}]
    # X2 cheats ahead over the top and steps into the passing lane near the 2nd screen
    legs["X2"] = [{"at": 0.55, "via": [[3.4, 7.75], [1.6, 7.85], [-0.6, 7.95]], "to": [-2.55, 8.0], "speed": 5.6},
                  {"at": "+0.1", "to": [-2.75, 7.95], "dur": 0.35},
                  {"at": "+0.25", "to": [-2.4, 6.2], "speed": 3.6}]
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": b["pass"]},
            {"type": "pass", "from": "O1", "to": "O2", "t0": b["pass"], "t1": b["catch"], "style": "bounce"},
            {"type": "hold", "player": "O2", "from": b["catch"], "to": b["lay"]},
            {"type": "layup", "player": "O2", "t0": b["lay"], "t1": b["lay"] + 0.4, "make": True}]
    marks = {"start": 0, "screen1": b["s1"], "screen2": b["s2"], "deny": b["deny"], "sell": b["sell"], "plant": b["plant"],
             "pass": b["pass"], "catch": b["catch"], "finish": b["lay"], "make": b["lay"] + 0.4, "end": 6.0}
    acts["X2"] = [{"type": "topLock", "from": b["deny"] - 0.2, "to": b["plant"] + 0.15, "face": "O2"}]
    acts["O2"] = [{"type": "celebrate", "from": b["lay"] + 0.7, "to": 6.0}]
    claims = [
        {"type": "near", "a": "O2", "b": "O4", "at": "screen1", "max": 1.4, "says": "Sprint over both elbow screens."},
        {"type": "near", "a": "X2", "b": "O2", "at": "deny", "max": 1.4, "says": "If he jumps the passing lane..."},
        {"type": "far", "a": "X2", "b": "O2", "at": "catch", "min": 1.6, "says": "Cut behind him."},
        {"type": "far", "a": "X4", "b": "O2", "at": "catch", "min": 2.5, "says": "Lead him to the rim."},
        {"type": "near_rim", "player": "O2", "at": "finish", "max": 1.6, "says": "That's your backdoor."},
        {"type": "order", "marks": ["screen1", "screen2", "deny", "sell", "plant", "pass", "catch", "finish"], "says": "deny, sell, plant, backdoor"}]
    return {"id": "iverson-b-backdoor", "title": "Iverson cut B: he denies, backdoor", "duration": 6.0,
            "concept": "iverson-cut", "source": SRC_I, "squareUp": True, "players": IP, "start": IS, "legs": legs,
            "ball": ball, "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same start as iverson-a-catch.",
                      "X2 cheats over the top and steps into the passing lane near the second screen.",
                      "O2 sells the catch, plants and cuts backdoor behind X2's hip; O1 leads him with a bounce pass."]}


F_CURL = {"rub": 1.75, "pass": 2.05, "catch": 2.55, "lay": 2.85}
F_FADE = {"fade": 1.45, "pass": 2.0, "catch": 2.8, "rel": 3.1}
I_CATCH = {"s1": 0.9, "s2": 1.7, "pass": 1.95, "catch": 2.45}
I_BACK = {"s1": 0.9, "s2": 1.6, "deny": 1.7, "sell": 1.9, "plant": 2.2, "pass": 2.45, "catch": 3.0, "lay": 3.2}


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


def pos(tr, t):
    for a, b in zip(tr, tr[1:]):
        if a[0] <= t <= b[0]:
            u = (t - a[0]) / max(1e-9, b[0] - a[0])
            return [a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u]
    return tr[-1][1:3]


def first_near(tr, pt, r=0.35, after=0.0):
    t = after
    while t <= tr[-1][0]:
        q = pos(tr, t)
        if ((q[0] - pt[0]) ** 2 + (q[1] - pt[1]) ** 2) ** 0.5 <= r:
            return t
        t += 0.01
    return None


if __name__ == "__main__":
    import sys
    # pass 1 builds, then time the ball on the measured runs (the catch lands where the cutter is)
    tr = build(floppy("curl"))["tracks"]["O2"]
    rub = first_near(tr, [-3.6, 2.7], 0.2) or 1.75
    cat = first_near(tr, [-1.95, 3.6], 0.06, rub) or rub + 0.8
    F_CURL.update(rub=round(rub, 3), catch=round(cat, 3), pass_=0, lay=round(first_near(tr, [-0.85, 2.78], 0.08, cat) or cat + 0.3, 3))
    F_CURL["pass"] = round(cat - 0.42, 3)
    tr = build(floppy("fade"))["tracks"]["O2"]
    fd = first_near(tr, [-3.45, 1.55], 0.3) or 1.45
    arr = first_near(tr, [-6.95, 1.25], 0.12, fd) or fd + 0.8
    F_FADE.update(fade=round(fd, 3), catch=round(arr + 0.05, 3), pass_=0)
    F_FADE["pass"] = round(arr + 0.05 - 0.78, 3)
    F_FADE["rel"] = round(arr + 0.4, 3)
    tr = build(iverson("catch"))["tracks"]["O2"]
    s1 = first_near(tr, [2.35, 7.15], 0.4) or 0.9
    s2 = first_near(tr, [-2.3, 7.15], 0.4, s1) or 1.7
    arr = first_near(tr, [-3.95, 6.75], 0.12, s2) or s2 + 0.4
    I_CATCH.update(s1=round(s1, 3), s2=round(s2, 3), catch=round(arr + 0.02, 3))
    I_CATCH["pass"] = round(arr + 0.02 - 0.5, 3)
    tr = build(iverson("backdoor"))["tracks"]["O2"]
    s1 = first_near(tr, [2.35, 7.15], 0.4) or 0.9
    s2 = first_near(tr, [0.0, 7.2], 0.4, s1) or 1.5
    sell = first_near(tr, [-2.75, 7.05], 0.12, s2) or s2 + 0.4
    plant = first_near(tr, [-3.15, 7.25], 0.05, sell) or sell + 0.35
    cat = first_near(tr, [-1.1, 3.0], 0.03, plant) or plant + 0.6
    lay = first_near(tr, [-0.8, 2.6], 0.06, cat) or cat + 0.3
    I_BACK.update(s1=round(s1, 3), s2=round(s2, 3), deny=round(sell - 0.15, 3), sell=round(sell, 3), plant=round(plant, 3),
                  catch=round(cat, 3), lay=round(lay, 3))
    I_BACK["pass"] = round(cat - 0.55, 3)
    for s in (floppy("curl"), floppy("fade"), iverson("catch"), iverson("backdoor")):
        build(s)
        print("built", s["id"], json.dumps({k: v for k, v in s["marks"].items()}))
