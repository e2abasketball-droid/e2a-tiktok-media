#!/usr/bin/env python3
"""HOW TO PUNISH THE SWITCH (owner brief 2026-11-17 12:50Z). Original E2A possession, generic coaching knowledge.
High ball screen, the defence SWITCHES: X5 (big) takes the guard, X1 (small) takes the roller.
Court: x across (-7.5..7.5), y from the baseline, basket (0, 1.575), metres. Basket at the top (yaw 0): x > 0 is screen-left.
  O1 starts top, slightly left (x > 0); O5 screens on his right side (x < 0 side) and O1 comes off toward x < 0.
  Both plays share the SAME first T seconds (screen, switch, new matchups): the decision point.
  A switch-a-seal   inside: O5 seals the small (X1 pinned behind him, rim side), O1 keeps the dribble, steps to a better
                    angle, feeds the post; O5 finishes short.
  B switch-b-drive  outside: X1 fronts the post (entry denied), O1 changes pace on X5 and beats his outside hip; the
                    weak-side help (X4) rotates late, layup."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T_ = os.path.dirname(os.path.dirname(D))
P = lambda i, t, r, g=None: {"id": i, "team": t, "role": r, **({"guards": g} if g else {})}
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (generic high pick-and-roll against a switch, punish the mismatch inside or outside; no copied possession)"
PL = [P("O1", "O", "Guard: uses the ball screen, then reads the switch"), P("O2", "O", "Left wing spacing"),
      P("O3", "O", "Right corner spacing"), P("O4", "O", "Left corner spacing"), P("O5", "O", "Big: ball screen, then posts the small"),
      P("X1", "X", "Starts on the guard, switches onto the big", "O1"), P("X2", "X", "Left wing", "O2"),
      P("X3", "X", "Right corner", "O3"), P("X4", "X", "Left corner: low man, late help", "O4"),
      P("X5", "X", "Starts on the big, switches onto the guard", "O5")]
S = {"O1": [1.55, 9.55], "X1": [1.2, 8.8], "O5": [-1.6, 6.6], "X5": [-1.1, 6.0],
     "O2": [5.4, 6.6], "X2": [4.6, 6.1], "O3": [-6.7, 1.4], "X3": [-5.7, 2.0], "O4": [6.6, 1.4], "X4": [3.6, 2.5]}
SCR = [0.45, 8.8]          # screen spot, on X1's x<0 side, facing him
POST_A = [-1.15, 3.4]      # O5's deep seal
X1_A = [-0.45, 2.65]       # X1 pinned behind, rim side
POST_B = [-0.7, 3.7]
X1_B = [-1.2, 4.45]        # X1 fronting: body in the passing line
O1_SW = [-1.95, 7.45]      # O1 after the switch, contained on the perimeter
X5_SW = [-1.55, 6.55]      # X5 in front of him
T = 3.6                    # decision point (same in A and B)
TM = {}


def common():
    legs = {"O5": [{"at": 0.0, "via": [[-0.4, 7.9]], "to": SCR, "dur": 1.05},
                   {"at": 1.95, "via": [[-0.4, 7.4]], "to": [-0.95, 5.0], "dur": 1.55}],
            "O1": [{"at": 0.75, "via": [[0.6, 9.75], [-0.6, 9.3]], "to": O1_SW, "dur": 2.3}],
            "X1": [{"at": 1.25, "to": [0.95, 8.95], "dur": 0.5},
                   {"at": 2.05, "via": [[0.2, 7.6]], "to": [-0.45, 5.55], "dur": 1.45}],
            "X5": [{"at": 0.2, "to": [-0.55, 7.95], "dur": 0.9},
                   {"at": 1.75, "to": X5_SW, "dur": 1.1}],
            "X4": [{"at": 1.5, "to": [3.1, 2.6], "dur": 1.2}]}
    acts = {"O5": [{"type": "screen", "from": 1.1, "to": 1.9, "face": "X1"}],
            "X1": [st("O1", 0, 1.3)], "X5": [st("O1", 1.8, T + 0.6)], "X2": [st("O2", 0, 12)], "X3": [st("O3", 0, 12)],
            "X4": [st("O1", 0, 12)]}
    ball = [{"type": "hold", "player": "O1", "from": 0, "to": T, "dribble": True}]
    marks = {"start": 0, "screen": 1.15, "switch": 1.85, "x5step": 1.8, "x1turn": 2.05, "decision": T}
    return legs, acts, ball, marks


def build_raw(kind, legs, ball, acts):
    s = {"id": f"_tmp-{kind}", "title": "tmp", "duration": 14.0, "players": PL, "start": S, "legs": legs, "ball": ball, "actions": acts}
    sp = os.path.join("/tmp", f"_tmp-switch-{kind}.spec.json")
    json.dump(s, open(sp, "w"))
    out = sp.replace(".spec.json", ".json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T_, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


def arrive(tr, pt, after=0.0, r=0.03):
    for a, b in zip(tr, tr[1:]):
        if b[0] >= after and abs(b[1] - pt[0]) < r and abs(b[2] - pt[1]) < r:
            return b[0]
    return None


def play(kind):
    legs, acts, ball, marks = common()
    if kind == "seal":
        legs["O5"].append({"at": T + 0.05, "to": POST_A, "dur": 0.75})
        legs["X1"].append({"at": T, "via": [[-0.3, 4.2]], "to": X1_A, "dur": 1.05})
        acts["O5"].append({"type": "seal", "from": T + 0.6, "to": T + 2.6, "face": "O1"})
        acts["X1"] = [st("O1", 0, 1.3), st("O5", T + 0.7, T + 3.0)]
        ANG = [-3.15, 7.05]
        legs["O1"].append({"at": T + 0.85, "to": ANG, "dur": 0.7})
        p0 = T + 1.62
        p1 = p0 + 0.42
        LAY = [-1.25, 2.4]
        legs["O5"].append({"at": p1 + 0.3, "to": LAY, "dur": 0.75})
        lay = p1 + 1.05
        legs["X1"].append({"at": p1 + 0.25, "to": [-0.15, 2.05], "dur": 0.5})
        ball += [{"type": "hold", "player": "O1", "from": T, "to": p0 - 0.15, "dribble": True},
                 {"type": "hold", "player": "O1", "from": p0 - 0.15, "to": p0},
                 {"type": "pass", "from": "O1", "to": "O5", "t0": p0, "t1": p1, "style": "bounce"},
                 {"type": "hold", "player": "O5", "from": p1, "to": lay},
                 {"type": "layup", "player": "O5", "t0": lay, "t1": lay + 0.4, "make": True}]
        acts["O5"].append({"type": "celebrate", "from": lay + 1.0, "to": lay + 1.8})
        marks.update({"seal": T + 0.8, "angle": T + 0.85, "angled": T + 1.55, "pass": p0, "catch": p1, "layup": lay, "make": lay + 0.4, "end": lay + 2.0})
        claims = [
            {"type": "near", "a": "X5", "b": "O1", "at": "decision", "max": 1.3, "says": "Big on the guard. The drive's cut off."},
            {"type": "near", "a": "X1", "b": "O5", "at": "decision", "max": 1.3, "says": "Small on the big."},
            {"type": "near", "a": "X1", "b": "O5", "at": "seal", "max": 1.2, "says": "He's got the guard pinned."},
            {"type": "near_rim", "player": "O5", "at": "layup", "max": 1.5, "says": "...and feed him (short finish)."},
            {"type": "order", "marks": ["screen", "switch", "decision", "seal", "angle", "pass", "catch", "layup", "make"], "says": "screen, switch, seal, angle, pass, catch, finish"}]
        return {"id": "switch-a-seal", "title": "Punish the switch A: deep seal, feed the post", "duration": lay + 2.0,
                "concept": "switch", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
                "marks": marks, "actions": acts, "claims": claims,
                "notes": ["Ball screen, switch: X5 on O1, X1 on O5.", "O5 seals X1 behind him; O1 keeps the dribble, steps to a better angle, bounce pass, short finish."]}
    # B: entry denied, attack the big
    legs["O5"].append({"at": T + 0.05, "to": POST_B, "dur": 0.75})
    legs["X1"].append({"at": T + 0.15, "via": [[-1.05, 5.35]], "to": X1_B, "dur": 0.8})
    acts["X1"] = [st("O1", 0, 1.3), st("O1", T + 0.6, T + 4.2)]
    hes = T + 1.1
    legs["O1"].append({"at": hes, "to": [-2.05, 7.25], "dur": 0.55})            # hesitation: slows, sits
    go = hes + 0.6
    LAY = [-0.8, 2.35]
    legs["O1"].append({"at": go, "via": [[-3.0, 6.0], [-2.45, 3.75]], "to": LAY, "speed": 5.6})
    b = build_raw(kind, legs, ball, acts)
    lay = arrive(b["tracks"]["O1"], LAY, go)
    legs["X5"].append({"at": go + 0.2, "via": [[-2.55, 5.85]], "to": [-2.25, 4.0], "speed": 5.0})
    legs["X4"].append({"at": go + 0.55, "to": [0.85, 2.55], "speed": 4.2})
    ball += [{"type": "hold", "player": "O1", "from": T, "to": lay - 0.4, "dribble": True},
             {"type": "hold", "player": "O1", "from": lay - 0.4, "to": lay},
             {"type": "layup", "player": "O1", "t0": lay, "t1": lay + 0.4, "make": True}]
    acts["X5"] = [st("O1", 1.8, go + 0.4)]
    acts["X4"] = [st("O1", 0, 12)]
    acts["O1"] = [{"type": "celebrate", "from": lay + 1.0, "to": lay + 1.8}]
    marks.update({"deny": T + 1.0, "hesitate": hes, "go": go, "hip": go + 0.9, "layup": lay, "make": lay + 0.4, "end": lay + 2.0})
    claims = [
        {"type": "near", "a": "X5", "b": "O1", "at": "decision", "max": 1.3, "says": "Same switch: the big is on the guard."},
        {"type": "near", "a": "X1", "b": "O5", "at": "deny", "max": 1.0, "says": "But what if that entry pass is gone? (X1 fronts)"},
        {"type": "far", "a": "O1", "b": "X5", "at": "hip", "min": 0.9, "says": "Change pace. Get past his hip."},
        {"type": "near_rim", "player": "O1", "at": "layup", "max": 1.5, "says": "Attack the big (finish at the rim)."},
        {"type": "order", "marks": ["screen", "switch", "decision", "deny", "hesitate", "go", "hip", "layup", "make"], "says": "screen, switch, deny, change of pace, past his hip, layup"}]
    return {"id": "switch-b-drive", "title": "Punish the switch B: entry denied, attack the big", "duration": lay + 2.0,
            "concept": "switch", "source": SRC, "squareUp": True, "players": PL, "start": S, "legs": legs, "ball": ball,
            "marks": marks, "actions": acts, "claims": claims,
            "notes": ["Same screen and switch.", "X1 fronts the post; O1 hesitates on X5, then beats his outside hip; X4 rotates late; layup."]}


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T_, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T_, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


if __name__ == "__main__":
    for k in ("seal", "drive"):
        p = build(play(k))
        print("built", p["id"], round(p["duration"], 2), {k: round(v, 2) for k, v in p["marks"].items()})
