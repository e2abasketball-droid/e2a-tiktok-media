#!/usr/bin/env python3
"""Double Drag V2 critical control data (owner brief sec. 7 "Datos críticos de control"), from the SAME pure functions
the render uses (scripts/pose-dump.mts = sample() + poseAt(), qc-catch phase machine). Writes a JSON + Markdown table.
  python3 tactical/episodes/_control-ddtr2.py <out_dir>
Measured (data): X1 route through both screens, X3's first step in stay_home / tag_roll, release and first contact of
each pass, O5's steps to the layup takeoff, O3's soles vs the three-point line at catch / last support / release,
shot results (ball through the rim plane, inside the ring). Repo axes: x > 0 = offence's left; y from the baseline."""
import json, math, os, subprocess, sys, tempfile
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D))
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
RIM = (0.0, 1.575, 3.05)
F = lambda t: round(t * 30, 1)


def dump(play, t0, t1, ids, fps=30):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name
    subprocess.run(["node", "--experimental-strip-types", "scripts/pose-dump.mts", f"tactical/plays/{play}.json", out, str(t0), str(t1), ",".join(ids), "--fps", str(fps)],
                   cwd=T, check=True, capture_output=True)
    return json.load(open(out))["rows"]


def contacts(rows, pid, foot_z=0.115):
    """foot plants: ankle height <= ankleH + 2.5 cm, both sides, plant start frames"""
    ev, prev = [], [False, False]
    for r in rows:
        p = r["players"][pid]; ah = p["dims"]["ankleH"]
        for i in (0, 1):
            down = p["ankle"][i][2] <= ah + 0.025
            if down and not prev[i]:
                ev.append({"S": r["f"], "foot": "L" if i == 0 else "R", "at": [round(p["ankle"][i][0], 2), round(p["ankle"][i][1], 2)]})
            prev[i] = down
    return ev


rep = {}
# 1) X1 route through both screens (A and B identical until S065)
rows = dump("ddtr-a-roll", 0, 2.4, ["X1", "O5", "O4", "O1"])
route = [{"S": r["f"], "X1": [round(c, 2) for c in r["players"]["X1"]["pelvis"][:2]],
          "d_O5": round(math.dist(r["players"]["X1"]["pelvis"][:2], r["players"]["O5"]["pelvis"][:2]), 2),
          "d_O4": round(math.dist(r["players"]["X1"]["pelvis"][:2], r["players"]["O4"]["pelvis"][:2]), 2),
          "d_O1": round(math.dist(r["players"]["X1"]["pelvis"][:2], r["players"]["O1"]["pelvis"][:2]), 2)} for r in rows if r["f"] % 4 == 0]
L = sum(math.dist(rows[i]["players"]["X1"]["pelvis"][:2], rows[i - 1]["players"]["X1"]["pelvis"][:2]) for i in range(1, len(rows)))
O1L = sum(math.dist(rows[i]["players"]["O1"]["pelvis"][:2], rows[i - 1]["players"]["O1"]["pelvis"][:2]) for i in range(1, len(rows)))
rep["X1_route"] = {"samples": route, "path_X1_m": round(L, 2), "path_O1_m": round(O1L, 2),
                   "min_d_O5_S026_S040": min(x["d_O5"] for x in route if 26 <= x["S"] <= 40), "min_d_O4_S050_S066": min(x["d_O4"] for x in route if 50 <= x["S"] <= 66)}
# 2) X3 first step in both branches
for play, br in (("ddtr-a-roll", "stay_home"), ("ddtr-b-skip", "tag_roll")):
    rows = dump(play, 2.0, 3.3, ["X3", "O3"], fps=60)
    p0 = rows[0]["players"]["X3"]["pelvis"][:2]
    first = next((r for r in rows if r["t"] > 2.2 and math.dist(r["players"]["X3"]["pelvis"][:2], p0) > 0.10), None)
    lift = contacts(rows, "X3")
    end = rows[-1]["players"]["X3"]["pelvis"][:2]
    rep[f"X3_{br}"] = {"start_S065": [round(c, 2) for c in p0], "moved_10cm_at_S": round(first["t"] * 30, 1) if first else None,
                       "pelvis_S099": [round(c, 2) for c in end], "displacement_S066_S099_m": round(math.dist(p0, end), 2),
                       "dist_to_O3_S099_m": round(math.dist(end, rows[-1]["players"]["O3"]["pelvis"][:2]), 2),
                       "foot_plants_S060_S099": [dict(c, S=round(c["S"] / 2, 1)) for c in lift][:6]}
# 3) passes: release and first contact (qc-catch phase machine)
qc = os.path.join(OUT, "qc-catch.json")
subprocess.run(["node", "--experimental-strip-types", "scripts/qc-catch.mts", "tactical/plays/ddtr-a-roll.json", "tactical/plays/ddtr-b-skip.json", "--json", qc], cwd=T, capture_output=True)
for play, pas in (("ddtr-a-roll", ("O1", "O5")), ("ddtr-b-skip", ("O1", "O3"))):
    pj = json.load(open(os.path.join(T, "tactical", "plays", f"{play}.json")))
    ev = next(e for e in pj["ball"] if e["type"] == "pass")
    rows = dump(play, ev["t0"] - 0.1, ev["t1"] + 0.1, [pas[0], pas[1]], fps=120)
    rel = next(r for r in rows if r["holder"] is None)
    con = next(r for r in rows if r["t"] >= ev["t1"] - 1e-6)
    rc = pj["players"]
    c = next(x for x in json.load(open(qc)) if x["play"] == play)["catches"][0]
    rep[f"pass_{play}"] = {"style": ev["style"], "release_t0_S": F(ev["t0"]), "ball_free_of_hands_S": round(rel["t"] * 30, 2), "release_ball": [round(v, 2) for v in rel["ball"]],
                           "first_contact_S": F(ev["t1"]), "contact_ball": [round(v, 2) for v in con["ball"]], "flight_s": round(ev["t1"] - ev["t0"], 3),
                           "ball_ahead_of_spine_m": c["ballAhead"], "hands_ahead_m": c["handsAhead"], "hand_ball_gap_m": c["handBall"], "phases": c["phases"]}
# 4) O5: steps from the catch to the layup takeoff (A)
rows = dump("ddtr-a-roll", 3.2, 4.5, ["O5"], fps=60)
pl = contacts(rows, "O5")
air = next((r for r in rows if r["players"]["O5"]["airborne"] > 0.05), None)
rep["O5_layup"] = {"catch_S": 98, "plants_after_catch": [dict(c, S=round(c["S"] / 2, 1)) for c in pl if c["S"] / 2 >= 98][:4],
                   "airborne_from_S": round(air["f"] / 2, 1) if air else None, "release_S": 116}
# 5) O3 soles vs the three-point line (FIBA: 6.75 m arc, 0.90 m from the sideline in the corner = |x| <= 6.60 is inside the arc band; sideline x = 7.50)
rows = dump("ddtr-b-skip", 3.7, 4.5, ["O3"], fps=30)
def soles(r):
    p = r["players"]["O3"]; out = []
    for i in (0, 1):
        for j in ("ankle", "toe"):
            x, y = p[j][i][0], p[j][i][1]
            out.append({"foot": "LR"[i], "joint": j, "x": round(x, 3), "y": round(y, 3), "d_rim": round(math.dist((x, y), RIM[:2]), 3)})
    return out
pick = {"catch_S114": 114, "load_grounded_S125": 125, "release_S133_airborne": 133}
rep["O3_soles"] = {}
for k, f in pick.items():
    r = min(rows, key=lambda r: abs(r["f"] - f)); s = soles(r)
    corner = [x for x in s if x["y"] <= 2.99]   # corner straight: the line is x = 6.60 up to y = 2.99
    rep["O3_soles"][k] = {"min_abs_x_corner": min((abs(x["x"]) for x in corner), default=None), "min_d_rim": min(x["d_rim"] for x in s),
                          "max_abs_x": max(abs(x["x"]) for x in s), "behind_line": all((abs(x["x"]) > 6.60 if x["y"] <= 2.99 else x["d_rim"] > 6.75) for x in s),
                          "inside_court": all(abs(x["x"]) < 7.5 for x in s), "airborne": r["players"]["O3"]["airborne"]}
# 6) shot results
for play, kind, t0, t1 in (("ddtr-a-roll", "layup", 116, 131), ("ddtr-b-skip", "three", 133, 163)):
    rows = dump(play, (t1 - 3) / 30, (t1 + 14) / 30, [], fps=60) if False else None
    tr = os.path.join(OUT, f"ball-{play}.csv")
    subprocess.run(["node", "--experimental-strip-types", "scripts/test-ball.mts", f"tactical/plays/{play}.json", "--trace", tr], cwd=T, capture_output=True)
    pts = [l.split(",") for l in open(tr).read().splitlines()[1:]]
    pts = [(float(p[1]), float(p[2]), float(p[3]), float(p[4])) for p in pts]
    cross = next(p for p in pts if p[0] >= t1 / 30 and p[3] <= RIM[2])
    below = next(p for p in pts if p[0] >= t1 / 30 and p[3] <= RIM[2] - 0.45)
    rep[f"result_{kind}"] = {"release_S": t0, "at_rim_S": t1, "ball_at_rim": [round(v, 3) for v in min(pts, key=lambda p: abs(p[0] - t1 / 30))[1:]],
                             "crosses_rim_plane_S": round(cross[0] * 30, 1), "offset_from_rim_centre_m": round(math.dist(cross[1:3], RIM[:2]), 3),
                             "below_net_S": round(below[0] * 30, 1), "make": True}
json.dump(rep, open(os.path.join(OUT, "control-ddtr2.json"), "w"), indent=1)
print(json.dumps(rep, indent=1)[:6000])
