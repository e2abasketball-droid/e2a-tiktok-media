#!/usr/bin/env python3
"""ZERO CUT TEST "aggressive hook" (owner brief 2026-11-26 16:27Z): the V2 plays (_gen-zerocut-v2.py, imported, V2 plays
untouched) with a rebuilt FINISH. V2 compiled the layup as a 1-2 stop into a vertical jump shot at the take-off spot
(the track ended at rest on LAY 0.3 s after the take-off), which read as "a short static shot". TEST:
  - the run keeps its speed into the take-off (catch in stride ~4 m/s, two gather steps), the take-off is AT the spot
    and the body keeps travelling forward through the air to a landing spot under the rim (LAND, ~1.3 m/s drift);
  - take-off H 0.5 and the opt-in `reach` release (arm extended up and forward toward the rim, motion33).
  python3 tactical/specs/_gen-zerocut-test.py   (writes tactical/specs/zerocut3-*.spec.json + tactical/plays/zerocut3-*.json)"""
import importlib.util, json, os

D = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("zc2", os.path.join(D, "_gen-zerocut-v2.py"))
V2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V2)
V, K = V2.V, V2.K
LAND = [-0.3, 1.8]
H = 0.5
_zero2, _build2 = V2.zero2, V2.build2


def zero3(kind):
    s = _zero2(kind)
    s["id"] = s["id"].replace("zerocut2-", "zerocut3-")
    s["title"] = s["title"].replace("Zero Cut V2", "Zero Cut TEST")
    if kind == "layup":
        for e in s["ball"]:
            if e["type"] == "layup":
                e["H"] = H
                e["reach"] = True
    return s


FINAL = [False]


def build3(s):
    p = _build2(s)
    if FINAL[0] and s["id"].endswith("layup"):
        rel = next(e for e in p["ball"] if e["type"] == "layup")["t0"]
        tk = round(rel + 0.035 - (2 * H / 9.81) ** 0.5, 3)
        tr = p["tracks"]["O2"]
        i = max(j for j, w in enumerate(tr) if abs(w[1] - V.LAY[0]) < 1e-6 and abs(w[2] - V.LAY[1]) < 1e-6 and w[0] < p["duration"] - 0.01)
        tl = round(rel + 0.30, 3)
        tr[i] = [tk, *V.LAY]
        tr[i + 1:] = [[tl, *LAND], [round(p["duration"], 3), *LAND]]
        p["tracks"]["O2"] = tr
        out = os.path.join(V2.T, "tactical", "plays", f"{s['id']}.json")
        json.dump(p, open(out, "w"), indent=1)
    return p


V2.zero2, V2.build2 = zero3, build3
if __name__ == "__main__":
    import runpy
    # re-run V2's measuring main with the TEST builders (same timing logic, zerocut3-* outputs)
    g = vars(V2)
    exec(compile(open(os.path.join(D, "_gen-zerocut-v2.py")).read().split('if __name__ == "__main__":')[1].replace("\n    ", "\n"), "main", "exec"), g)
    # the timing is measured on the V2 finish; the rebuilt finish is applied to the final plays only
    FINAL[0] = True
    for s in (zero3("layup"), zero3("kick")):
        p = build3(s)
        print("final", s["id"], "O2 tail", p["tracks"]["O2"][-4:])
