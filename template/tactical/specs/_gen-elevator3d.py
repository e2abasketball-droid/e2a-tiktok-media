#!/usr/bin/env python3
"""ELEVATOR SCREEN in the real-3D engine (owner 2026-11-16 15:46Z: "reproducir el vídeo de elevator screen con el sistema
de edición de spain pick and roll ... prácticamente igual, mejorando gráficos y personajes 3D").
Same possession as the 2.5D pilot (tactical/plays/elevator-a-chase.json / elevator-b-switch.json): every player's path
is converted waypoint by waypoint (same spots, same times) into build-play legs, so the 3D plays match the original.
  A elev3d-a-chase   X2 chases the shooter through the corridor, the doors close on him: catch and shoot three.
  B elev3d-b-switch  X5 jumps out early to switch: O5 slips, bounce pass, layup."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
st = lambda f, a, b: {"type": "stance", "from": a, "to": b, "face": f}
SRC = "original E2A play (elevator screen, generic coaching knowledge); same possession as the E2A 2.5D pilot 01"


def legs_from(tr, cut=None):
    """contiguous movement (no stop between waypoints) becomes ONE leg with vias and the same total duration"""
    if cut is not None:
        tr = [r for r in tr if r[0] <= cut]
    out, cur = [], None
    for a, b in zip(tr, tr[1:]):
        if abs(a[1] - b[1]) < 1e-6 and abs(a[2] - b[2]) < 1e-6:
            cur = None
            continue
        pt = [round(b[1], 3), round(b[2], 3)]
        if cur and abs(cur["_end"] - a[0]) < 1e-6:
            cur["via"].append(cur["to"]); cur["to"] = pt; cur["dur"] = round(b[0] - cur["at"], 3); cur["_end"] = b[0]
        else:
            cur = {"at": round(a[0], 3), "via": [], "to": pt, "dur": round(b[0] - a[0], 3), "_end": b[0]}
            out.append(cur)
    for l in out:
        l.pop("_end")
        if not l["via"]:
            l.pop("via")
    return out


O2_CUT = [{"at": 0, "to": [-1.15, 1.4], "dur": 0.55},
          {"at": 0.68, "via": [[-0.75, 1.7], [-0.4, 2.85], [-0.15, 4.5], [0, 5.8], [0, 6.7], [-0.15, 7.9]], "to": [-0.25, 8.75], "dur": 1.72}]
X2_START = {"at": 0, "to": [-1.45, 1.95], "dur": 0.5}


def conv(src, nid, title, extra, cut=None, patch=None, override=None):
    p = json.load(open(os.path.join(T, "tactical", "plays", f"{src}.json")))
    for k, tr in (patch or {}).items():
        p["tracks"][k] = tr
    start = {k: [tr[0][1], tr[0][2]] for k, tr in p["tracks"].items()}
    legs = {k: legs_from(tr, (cut or {}).get(k)) for k, tr in p["tracks"].items()}
    legs.update(override or {})
    players = []
    for x in p["players"]:
        q = {"id": x["id"], "team": x["team"], "role": x["role"]}
        if x.get("guards"):
            q["guards"] = x["guards"]
        players.append(q)
    s = {"id": nid, "title": title, "duration": p["duration"], "concept": "elevator", "source": SRC, "squareUp": True,
         "players": players, "start": start, "legs": legs, "ball": p["ball"], "marks": p["marks"], "notes": p["notes"]}
    s.update(extra)
    if nid.endswith("chase"):
        s["marks"] = {**s["marks"], "inGap": 1.75, "through": 1.9, "doorsClosed": 2.32, "contact": 2.4}
    return s


A = conv("elevator-a-chase", "elev3d-a-chase", "Elevator screen A: he chases, the doors close, catch and shoot", {
    "actions": {"O4": [{"type": "screen", "from": 2.35, "to": 3.2, "face": "X2"}], "O5": [{"type": "screen", "from": 2.35, "to": 3.2, "face": "X2"}],
                "X1": [st("O1", 0, 4.8)], "X3": [st("O3", 0, 4.8)], "X4": [st("O4", 0, 3.3)], "X5": [st("O5", 0, 3.3)],
                "O2": [{"type": "celebrate", "from": 4.2, "to": 4.8}]},
    "claims": [{"type": "near", "a": "O4", "b": "O5", "at": "doorsClosed", "max": 0.8, "says": "the doors close"},
               {"type": "far", "a": "X2", "b": "O2", "at": "release", "min": 1.8, "says": "Catch. Shoot."},
               {"type": "behind_arc", "player": "O2", "at": "catch", "says": "Three points."},
               {"type": "order", "marks": ["cut", "inGap", "through", "doorsClosed", "catch", "release", "make"], "says": "cut, through, doors, pass, three"}]},
    cut={"O4": 3.3, "O5": 3.3, "X4": 3.3, "X5": 3.3},
    override={"O2": O2_CUT,
              "X2": [X2_START, {"at": 0.78, "via": [[-1.1, 2.3], [-0.65, 3.6], [-0.4, 4.4]], "to": [0.0, 5.1], "dur": 1.6},
                     {"at": 2.4, "via": [[-0.7, 5.3], [-1.05, 6.2]], "to": [-0.95, 7.0], "dur": 1.0}],
              "O4": [{"at": 1.85, "to": [-0.3, 5.8], "dur": 0.45}], "O5": [{"at": 1.85, "to": [0.3, 5.8], "dur": 0.45}]})
B = conv("elevator-b-switch", "elev3d-b-switch", "Elevator screen B: the early switch, the screener slips, layup", {
    "actions": {"X1": [st("O1", 0, 3.9)], "X3": [st("O1", 0, 3.9)], "X4": [st("O4", 0, 3.9)], "X2": [st("O2", 0, 3.9)],
                "O5": [{"type": "celebrate", "from": 3.3, "to": 3.9}]},
    "claims": [{"type": "near_rim", "player": "O5", "at": "release", "max": 1.5, "says": "a layup opportunity"},
               {"type": "far", "a": "X5", "b": "O5", "at": "catch", "min": 2.5, "says": "the screener slips into the open lane"},
               {"type": "order", "marks": ["cut", "x5Leaves", "read", "pass", "catch", "release", "make"], "says": "switch, slip, pass, layup"}]},
    override={"O2": O2_CUT,
              "X2": [X2_START, {"at": 0.78, "via": [[-1.1, 2.3], [-0.65, 3.6], [-0.4, 4.4], [-0.1, 5.6], [-0.2, 7.1]], "to": [-0.35, 7.9], "dur": 2.3}]},
    patch={"X4": [[0, -1.25, 4.9], [1.75, -1.25, 4.9], [2.45, -2.2, 6.35], [3.1, -1.55, 5.1], [3.5, -1.4, 4.8], [3.9, -1.4, 4.8]], "O5": [[0, 0.85, 5.8], [1.3, 0.85, 5.8], [1.75, 1.35, 4.85], [2.15, 1.3, 3.6], [2.5, 0.6, 2.5], [3.9, 0.6, 2.5]]})


def build(s):
    sp = os.path.join(D, f"{s['id']}.spec.json")
    json.dump(s, open(sp, "w"), indent=1)
    out = os.path.join(T, "tactical", "plays", f"{s['id']}.json")
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/build-play.mts", sp, out], cwd=T, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])
    return json.load(open(out))


if __name__ == "__main__":
    for s in (A, B):
        print("built", s["id"], build(s)["duration"])
