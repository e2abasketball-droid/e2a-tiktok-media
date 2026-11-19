#!/usr/bin/env python3
"""BLIND PIG (owner brief 2026-11-19, ENCARGO-blind-pig): DENY -> HIGH-POST FLASH -> BACKDOOR -> LAYUP.
Triangle-offence counter (NBA Coaches Playbook, Tex Winter / Phil Jackson): the player due to receive the reversal is
denied; a post flashes to the high post, catches, and the denied player speed-cuts behind his defender for a short
pass to the rim. NO SCREENS in this action: no player has a `screen` action, nobody is labelled a screen.
Secondary read (B, "rehook"): if the low defender (X3) leaves his shooter to help on the cutter, the high-post passer
kicks out to the shooter he left. That is OUR staging's counter, not a universal Blind Pig rule.

Court (repo units, verified in src/tactical/geometry.ts and scripts/build-play.mts): metres on a FIBA half court,
x across (-7.5..7.5 = the 15 m width), y from the baseline (0..14 = half of the 28 m length), basket (0, 1.575),
free-throw line y = 5.8, lane |x| <= 2.45, three-point line 6.75 m (corners x = +-6.6). These are PRODUCTION
coordinates (our staging), not a historical diagram. With the house cameras (yaw 0 = from half court, basket at the
top) x < 0 is on the RIGHT of the screen: "the defender on the right" = X2 at the right slot (x < 0).

Causal timing (no precognition): every defender moves only after his stimulus, with a human latency:
  X2 follows O2's V-cut (+0.25 s) into the passing lane; O4 flashes only AFTER the denial exists;
  X4 trails the flash (+0.25 s); O2 plants and cuts only once O1's entry pass is out (O4's catch is possible);
  X2 turns and chases +0.28 s after the cut starts; (B) X3 starts to help +0.3 s after the cut starts and helps
  progressively; X3 closes out only after the kick-out leaves O4's hands (+0.2 s).
  python3 tactical/specs/_gen-blindpig.py   (writes tactical/specs/blindpig-{a-layup,b-kick}.spec.json + plays)"""
import json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A staging of the Triangle 'Blind Pig' counter (NBA Coaches Playbook description; WABC/FIBA backdoor teaching); production coordinates"

PLAYERS = [P("O1", "O", "Passer, left slot: threatens the reversal, enters to the high post"),
           P("O2", "O", "Right slot: sells the catch, cuts backdoor (the cutter)"),
           P("O3", "O", "Right corner shooter (spacing; kick-out target in B)"),
           P("O4", "O", "Big: flashes from the lane to the high post, the passer"),
           P("O5", "O", "Big: posts on the left block, keeps X5 busy (no screen)"),
           P("X1", "X", "On the ball", "O1"),
           P("X2", "X", "Denies the reversal pass (the defender on the right)", "O2"),
           P("X3", "X", "Low defender on the right corner: stays (A) / helps on the cutter (B)", "O3"),
           P("X4", "X", "Trails O4's flash", "O4"),
           P("X5", "X", "Behind O5 on the left block", "O5")]

START = {"O1": [2.6, 8.4], "X1": [2.95, 7.7],
         "O2": [-4.35, 6.55], "X2": [-3.7, 6.0],
         "O3": [-6.6, 1.25], "X3": [-5.35, 2.05],
         "O4": [1.2, 3.35], "X4": [0.8, 2.75],
         "O5": [2.55, 1.9], "X5": [2.0, 1.55]}

# key timings (play seconds); measured / refined in __main__ from the built tracks
K = {"cutSpeed": 6.6, "vcut": 0.1, "deny": 1.25, "flash": 1.45, "entry": 2.0, "catch4": 2.45, "plant": 2.1, "cut": 2.18,
     "x2turn": 2.46, "look4": 2.62, "pass2": 3.15, "catch2": 3.62, "lay": 3.74,
     "help": 2.48, "kick": 3.22, "catch3": 3.92, "rel": 4.2}

PLANT = [-3.05, 8.3]          # O2's sell spot at the right slot
DENY = [-2.45, 7.95]          # X2 in the passing lane, a step off O2 toward the ball
HIGH = [-0.25, 5.85]          # high post (just above the free-throw line, middle)
X4_TRAIL = [0.55, 5.2]        # X4 arrives late, on O4's back (left) hip: out of the pass to the right block
CATCH2 = [-1.15, 3.15]        # O2 catches in stride
LAYSPOT = [-0.62, 2.3]


def common(kind):
    legs = {
        # O2 V-cut: from the wing up to the right slot, decelerates, sells the catch (shows a hand)
        "O2": [{"at": K["vcut"], "via": [[-3.9, 7.4]], "to": PLANT, "speed": 4.6},
               # small sell step toward the ball while the entry pass is in the air ... then plant and backdoor
               ],
        # X2 follows the V-cut with latency and takes the passing lane (denial exists ~K.deny)
        "X2": [{"at": K["vcut"] + 0.25, "via": [[-3.3, 7.1]], "to": DENY, "speed": 4.4}],
        # O4 flashes ONLY after the denial exists
        "O4": [{"at": K["flash"], "via": [[0.75, 4.55]], "to": HIGH, "speed": 5.4}],
        # X4 trails the flash (+0.25 s)
        "X4": [{"at": K["flash"] + 0.25, "via": [[0.9, 4.3]], "to": X4_TRAIL, "speed": 4.6}],
        "O1": [], "X1": [{"at": K["entry"] + 0.25, "to": [2.35, 7.0], "speed": 2.0}],
        "O5": [], "X5": [],
        "O3": [], "X3": [],
    }
    acts = {
        "O1": [{"type": "face", "from": 0, "to": K["flash"] - 0.05, "face": "O2"}],          # eyes on the reversal, not the post
        "O2": [{"type": "call", "from": 0.95, "to": K["plant"] - 0.05, "amt": 0.55}],         # shows a hand, sells the catch
        "X2": [{"type": "topLock", "from": K["deny"] - 0.2, "to": K["x2turn"], "face": "O2"}],
        "X1": [st("O1", 0, K["entry"] + 0.2)],
        "O5": [{"type": "seal", "from": 0.2, "to": 5.6, "face": "O1"}],                         # posts up, stationary: no screen
        "X5": [st("O5", 0, 5.6)],
        "X4": [st("O4", K["flash"] + 0.9, 5.6)],
        "X3": [st("O3", 0, K["help"])],
        "O3": [{"type": "catchReady", "from": 0.0, "to": 0.0001}],
    }
    acts["O3"] = []
    # O4: catch facing the passer, chin the ball, head first, then the chest turns to the cutter / the read
    acts["O4"] = []   # facing from play.ts: squares up to the passer for the catch, then to the receiver 0.8 s before his pass
    return legs, acts


def blindpig(kind):
    legs, acts = common(kind)
    # O2: plant (the entry is in the air) and cut behind X2: one leg from the plant through the catch to the layup,
    # so the catch is in stride (the leg only brakes into the gather at its end)
    legs["O2"].append({"at": K["cut"], "via": [[-3.0, 7.05], [-2.05, 4.75], CATCH2], "to": LAYSPOT, "speed": K["cutSpeed"]})
    # X2: human latency before he turns, then chases on the cutter's back
    legs["X2"].append({"at": K["x2turn"], "via": [[-2.75, 6.7], [-2.05, 4.75]], "to": [-1.75, 3.9], "speed": 5.4})
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": K["entry"]},
            {"type": "pass", "from": "O1", "to": "O4", "t0": K["entry"], "t1": K["catch4"], "style": "chest"}]
    if kind == "layup":
        legs["X3"] = [{"at": K["help"] + 0.3, "to": [-4.9, 2.25], "speed": 1.6}]                 # a look, then stays home
        acts["X3"] = [st("O3", 0, 5.6)]
        ball += [{"type": "hold", "player": "O4", "from": K["catch4"], "to": K["pass2"]},
                 {"type": "pass", "from": "O4", "to": "O2", "t0": K["pass2"], "t1": K["catch2"], "style": "bounce", "eyes": 0.45, "lead": True},
                 {"type": "hold", "player": "O2", "from": K["catch2"], "to": K["lay"]},
                 {"type": "layup", "player": "O2", "t0": K["lay"], "t1": K["lay"] + 0.4, "make": True}]
        acts["O2"].append({"type": "celebrate", "from": K["lay"] + 0.8, "to": 5.5})
        marks = {"start": 0, "vcut": K["vcut"], "deny": K["deny"], "flash": K["flash"], "entry": K["entry"], "plant": K["plant"],
                 "cut": K["cut"], "catch4": K["catch4"], "x2turn": K["x2turn"], "look": K["look4"], "pass": K["pass2"],
                 "catch": K["catch2"], "finish": K["lay"], "make": K["lay"] + 0.4, "end": 5.6}
        claims = [
            {"type": "near", "a": "X2", "b": "O2", "at": "deny", "max": 1.0, "says": "He jumps into the passing lane"},
            {"type": "reacts_after", "player": "O4", "event": "deny", "min": 0.15, "says": "so the big flashes to the high post"},
            {"type": "reacts_after", "player": "X4", "event": "flash", "min": 0.2, "says": "the big flashes to the high post (X4 trails)"},
            {"type": "reacts_after", "player": "X2", "event": "cut", "min": 0.22, "says": "then cuts behind him (X2 turns late)"},
            {"type": "far", "a": "X2", "b": "O2", "at": "catch", "min": 1.5, "says": "Now the defender can't see both."},
            {"type": "near_rim", "player": "O2", "at": "finish", "max": 1.5, "says": "and gave up the layup"},
            {"type": "order", "marks": ["vcut", "deny", "flash", "entry", "plant", "cut", "catch4", "look", "pass", "catch", "finish", "make"],
             "says": "One pass changes the angle. The next one beats the denial."}]
        return {"id": "blindpig-a-layup", "title": "Blind Pig A: deny, high-post flash, backdoor, layup", "duration": 5.6, "concept": "blind-pig",
                "source": SRC, "squareUp": True, "players": PLAYERS, "start": START, "legs": legs, "ball": ball, "marks": marks,
                "actions": acts, "claims": claims, "screens": [],
                "notes": ["O1 threatens the reversal to O2; X2 jumps into the passing lane.",
                          "Only after the denial exists O4 flashes from the lane to the high post; O1 enters to him.",
                          "With the entry in the air O2 plants and cuts behind X2; X2 turns late.",
                          "O4 chins it, head first, bounce pass into space; O2 finishes in stride. No screens."]}
    # B: the low defender helps -> kick out to the shooter he left
    legs["O2"][-1] = {"at": K["cut"], "via": [[-3.0, 7.05], [-2.05, 4.75]], "to": [-1.45, 3.05], "speed": 6.6}
    legs["X3"] = [{"at": K["help"], "via": [[-4.6, 2.55]], "to": [-2.75, 2.75], "speed": 4.8},       # progressive help
                  {"at": K["kick"] + 0.22, "to": [-4.95, 2.3], "speed": 4.6}]
    if K.get("helpEnd", 0) > 50:
        legs["X3"] = legs["X3"][:1]                                                               # measuring pass only                          # late closeout
    acts["X3"] = [st("O3", 0, K["help"] - 0.05), {"type": "stance", "from": K["help"] + 0.25, "to": K["kick"] + 0.15, "face": "O2"},
                  {"type": "closeout", "from": K["kick"] + 0.25, "to": K["rel"] + 0.1}, {"type": "contest", "from": K["rel"] - 0.05, "to": K["rel"] + 0.55}]
    acts["O3"] = [{"type": "catchReady", "from": K["kick"] + 0.05, "to": K["catch3"] + 0.05}]
    ball += [{"type": "hold", "player": "O4", "from": K["catch4"], "to": K["kick"]},
             {"type": "pass", "from": "O4", "to": "O3", "t0": K["kick"], "t1": K["catch3"], "style": "overhead", "eyes": 0.4},
             {"type": "hold", "player": "O3", "from": K["catch3"], "to": K["rel"]},
             {"type": "shot", "player": "O3", "t0": K["rel"], "t1": K["rel"] + 1.05, "make": True, "three": True}]
    acts["O3"].append({"type": "celebrate", "from": K["rel"] + 1.25, "to": 6.2})
    marks = {"start": 0, "vcut": K["vcut"], "deny": K["deny"], "flash": K["flash"], "entry": K["entry"], "plant": K["plant"],
             "cut": K["cut"], "catch4": K["catch4"], "x2turn": K["x2turn"], "help": K["help"], "look": K["look4"], "kick": K["kick"],
             "catch": K["catch3"], "release": K["rel"], "make": K["rel"] + 1.05, "end": 6.4}
    claims = [
        {"type": "near", "a": "X2", "b": "O2", "at": "deny", "max": 1.0, "says": "He jumps into the passing lane"},
        {"type": "reacts_after", "player": "O4", "event": "deny", "min": 0.15, "says": "so the big flashes to the high post"},
        {"type": "reacts_after", "player": "X3", "event": "cut", "min": 0.25, "says": "But if the low defender helps"},
        {"type": "near", "a": "X3", "b": "O2", "at": "kick", "max": 1.9, "says": "if the low defender helps (on the cutter)"},
        {"type": "reacts_after", "player": "X3", "event": "kick", "min": 0.15, "says": "Kick it out to the shooter he just left (late closeout)"},
        {"type": "behind_arc", "player": "O3", "at": "catch", "says": "Kick it out to the shooter he just left."},
        {"type": "open", "player": "O3", "at": "release", "min": 1.8, "says": "the shooter he just left"},
        {"type": "order", "marks": ["deny", "flash", "entry", "cut", "help", "kick", "catch", "release", "make"], "says": "don't force it. Kick it out"}]
    return {"id": "blindpig-b-kick", "title": "Blind Pig B (rehook): the low defender helps, kick out to the shooter", "duration": 6.4,
            "concept": "blind-pig", "source": SRC, "squareUp": True, "players": PLAYERS, "start": START, "legs": legs, "ball": ball,
            "marks": marks, "actions": acts, "claims": claims, "screens": [],
            "notes": ["Same start as blindpig-a-layup.",
                      "X3 leaves O3 progressively to help on O2's cut.",
                      "O4 does not force the bounce pass: overhead kick-out to O3 in the right corner, late closeout, three.",
                      "This counter is our staging's read, not a universal Blind Pig rule."]}


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
            return round(t, 3)
        t += 0.005
    return None


if __name__ == "__main__":
    # pass 1: measure the runs, then time the ball on them (catches land where the players really are)
    tr = build(blindpig("layup"))["tracks"]
    K["deny"] = first_near(tr["X2"], DENY, 0.03) or K["deny"]
    K["flash"] = round(K["deny"] + 0.2, 3)             # the flash answers the denial (stimulus + reaction)
    tr = build(blindpig("layup"))["tracks"]
    arr4 = first_near(tr["O4"], HIGH, 0.08) or K["catch4"]
    K["catch4"] = round(arr4 + 0.02, 3)
    K["entry"] = round(K["catch4"] - 0.48, 3)
    K["plant"] = round(K["entry"] + 0.1, 3)           # the entry is out: the catch is possible -> plant
    K["cut"] = round(K["plant"] + 0.22, 3)
    K["x2turn"] = round(K["cut"] + 0.28, 3)            # X2's human latency
    K["help"] = round(K["cut"] + 0.32, 3)              # (B) X3's latency
    K["pass2"] = round(K["catch4"] + 0.66, 3)          # catch, chin it (~0.2 s), head first (eyes 0.45 s), pass
    K["look4"] = round(K["pass2"] - 0.45, 3)
    K["catch2"] = round(K["pass2"] + 0.42, 3)
    # O2's cut speed so that he reaches the catch spot exactly when the bounce pass arrives (in stride)
    best = None
    for k in range(0, 26):
        K["cutSpeed"] = round(7.2 - 0.06 * k, 3)
        tr = build(blindpig("layup"))["tracks"]
        c2 = first_near(tr["O2"], CATCH2, 0.04, K["cut"])
        if c2 is not None and (best is None or abs(c2 - K["catch2"]) < best[0]):
            best = (abs(c2 - K["catch2"]), K["cutSpeed"], c2)
    K["cutSpeed"], c2 = best[1], best[2]
    K["catch2"] = c2
    K["pass2"] = round(c2 - 0.42, 3)
    K["look4"] = round(K["pass2"] - 0.45, 3)
    tr = build(blindpig("layup"))["tracks"]
    K["lay"] = round((first_near(tr["O2"], LAYSPOT, 0.12, c2) or c2 + 0.2), 3)
    K["helpEnd"] = 99
    trb = build(blindpig("kick"))["tracks"]
    K["helpEnd"] = first_near(trb["X3"], [-2.75, 2.75], 0.005, K["help"])
    K["kick"] = round(max(K["helpEnd"] + 0.04, K["catch4"] + 0.7), 3)   # the help is committed -> kick out
    K["catch3"] = round(K["kick"] + 0.72, 3)
    K["rel"] = round(K["catch3"] + 0.3, 3)
    for s in (blindpig("layup"), blindpig("kick")):
        build(s)
        print("built", s["id"], json.dumps(s["marks"]))
    print("cutSpeed", K["cutSpeed"])
