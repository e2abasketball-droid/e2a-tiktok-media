#!/usr/bin/env python3
"""ZERO CUT V2 (owner brief 2026-11-26 13:18Z "ZERO CUT V2 - complete cinematic re-edit"): same action and same two reads
as V1 (_gen-zerocut.py, imported, V1 plays untouched), with the motion fixes the V1 audit found:
  1. O2 no longer STOPS at the handoff spot: V1 built the sell and the cut as two rest-to-rest legs, so O2 stood still
     0.21 s at the fake handoff and the V3.3 compiler (plants need >= 1.3 m/s on both sides of the turn) wrote NO plant.
     V2 merges the two runs into one spline through the handoff spot: O2 decelerates into it (~2.5 m/s), plants the
     outside foot and accelerates out of it -> a real compiled 'plant' with cut angle (weight transfer, explosive step).
  2. X2 commits and recovers LATE: he stays locked over the top 0.38 s after the cut starts (V1 0.30) and his recovery
     starts slower (turn + first steps) before he chases.
  3. The finish: the cutter catches in stride further from the rim (V1 caught 1.3 m from the take-off spot and
     finished with a 0.22 m hop shot). V2: catch ~2.0 m out, two gather steps, layup take-off H 0.5 m (layup ball
     event 'H', opt-in in compile33), so the catch -> gather -> finish momentum is continuous.
  python3 tactical/specs/_gen-zerocut-v2.py   (writes tactical/specs/zerocut2-*.spec.json + tactical/plays/zerocut2-*.json)"""
import importlib.util, json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
spec = importlib.util.spec_from_file_location("zc1", os.path.join(D, "_gen-zerocut.py"))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
K = V.K

V.CATCH = [-1.75, 4.35]     # catch in stride, ~2 m before the take-off
V.LAY = [-0.75, 2.4]        # take-off spot (the run eases into it: the two gather steps)
V.HAND = [-2.2, 7.38]       # fake-handoff spot a touch closer to the big (handoff distance)
LAYUP_H = 0.5
X2_LATE = 0.38


def zero2(kind):
    s = V.zero(kind)
    s["id"] = s["id"].replace("zerocut-", "zerocut2-")
    s["title"] = s["title"].replace("Zero Cut", "Zero Cut V2")
    if kind == "layup":
        for e in s["ball"]:
            if e["type"] == "layup":
                e["H"] = LAYUP_H
        # catch in stride: the cut leg passes the catch spot, no extra via between the catch and the take-off
        for leg in s["legs"]["O2"]:
            if leg.get("at") == K["cut"]:
                leg["via"] = [[-2.5, 5.9], V.CATCH]
                leg["to"] = V.LAY
    s["notes"] = s.get("notes", []) + ["V2: O2 runs THROUGH the fake handoff (one spline, compiled plant), X2 recovers late, "
                                      "catch in stride + two gather steps + layup take-off."]
    return s


def build2(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    p = json.load(open(out))
    # merge O2's two runs: drop the standing pair at the handoff spot, keep ONE waypoint there at the plant time
    tr = p["tracks"]["O2"]
    hx, hy = V.HAND
    idx = [i for i, w in enumerate(tr) if abs(w[1] - hx) < 1e-6 and abs(w[2] - hy) < 1e-6]
    if len(idx) == 2 and idx[1] == idx[0] + 1:
        a, b = tr[idx[0]][0], tr[idx[1]][0]
        tp = round((a + b) / 2 - 0.04, 3)
        tr[idx[0]] = [tp, hx, hy]
        del tr[idx[1]]
        # explosive first step out of the plant: the next waypoint 0.45 s after it, the rest of the run shifted with it
        j = idx[0] + 1
        if j < len(tr) - 1:
            # cut run re-timed: first waypoint 0.5 s after the plant, later intervals x1.3 (V1 pace was a sprint the
            # pass could not lead without precognition)
            t_prev_old, t_prev_new = tr[j][0], tp + 0.5
            tr[j][0] = round(t_prev_new, 3)
            for k in range(j + 1, len(tr) - 1):
                d = tr[k][0] - t_prev_old
                t_prev_old = tr[k][0]
                t_prev_new = t_prev_new + d * 1.3
                tr[k][0] = round(t_prev_new, 3)
        p["tracks"]["O2"] = tr
        p.setdefault("marks", {})
    json.dump(p, open(out, "w"), indent=1)
    return p


def run(cmd):
    r = subprocess.run(cmd, cwd=T, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


if __name__ == "__main__":
    # timing measured like V1, then V2 offsets
    tr = build2(zero2("layup"))["tracks"]
    K["catch1"] = round((V.first_near(tr["O5"], V.TOP, 0.05) or K["catch1"]) + 0.03, 3)
    K["pass1"] = round(K["catch1"] - 0.5, 3)
    K["sprint"] = round(K["catch1"] - 0.15, 3)
    tr = build2(zero2("layup"))["tracks"]
    arr = V.first_near(tr["O2"], V.HAND, 0.06, K["sprint"]) or K["plant"]
    K["show"] = round(arr - 0.5, 3)
    K["plant"] = round(arr, 3)
    xo = V.first_near(tr["X2"], V.OVER, 0.25, K["sprint"])
    K["cut"] = round(max(arr + 0.06, (xo or arr) + 0.02), 3)
    K["x2turn"] = round(K["cut"] + X2_LATE, 3)
    K["help"] = round(K["cut"] + 0.3, 3)
    for _ in range(2):
        tr = build2(zero2("layup"))["tracks"]
        c2 = V.first_near(tr["O2"], V.CATCH, 0.06, K["cut"])
        K["catch2"] = c2
        K["pass2"] = round(max(c2 - 0.55, K["x2turn"] + 0.03), 3)
    tr = build2(zero2("layup"))["tracks"]
    K["lay"] = round(V.first_near(tr["O2"], V.LAY, 0.1, K["catch2"]) or K["catch2"] + 0.6, 3)
    K["measure"] = True
    trb = build2(zero2("kick"))["tracks"]
    K["measure"] = False
    he = V.first_near(trb["X3"], V.HELP, 0.6, K["help"])
    hend = V.first_near(trb["X3"], V.HELP, 0.02, K["help"])
    K["kick"] = round(max(he or K["help"] + 0.5, K["cut"] + 0.75, (hend or 0) + 0.05), 3)
    K["catch3"] = round(K["kick"] + 0.78, 3)
    K["rel"] = round(K["catch3"] + 0.32, 3)
    for s in (zero2("layup"), zero2("kick")):
        p = build2(s)
        print("built", s["id"], json.dumps(s["marks"]))
        print("  O2", [w for w in p["tracks"]["O2"]][:8])
