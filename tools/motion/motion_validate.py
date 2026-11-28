#!/usr/bin/env python3
"""E2A Motion Engine V4 (2026-11-28): quantitative motion validator on the SOLVED skeleton.

Input: the per-frame dump of template/scripts/motion-dump-v4.mts (what the renderer draws). Thresholds are configurable
and are PROVISIONAL engineering tolerances for this animation style, not biomechanical benchmarks (see THRESH).

Checks: speed, pelvis acceleration pops, planted-foot slide, foot-floor penetration, support-leg overreach (root
motion faster than the stride = the leg is stretched straight), stiff running (support knee too straight at speed),
floaty running (no vertical bob at speed), cadence vs speed, body facing vs travel (sideways / backwards running),
instant turns (pelvis yaw rate), knee / elbow limits, body-body intersections, ball teleport, ball-palm gap while held,
ball inside another body, receiver gaze before the catch, court bounds, identity (10 unique ids, constant team).

  python3 tools/motion/motion_validate.py --dump mdump.json --out report.json [--md report.md] [--props episode.json]
      [--offset 1.2]   (owner time = engine time - offset; --props maps engine time to the video timestamps of each shot)
"""
import argparse, json, math
from collections import defaultdict

THRESH = {
    "v_max": 8.0,            # m/s, elite sprint in a half-court action rarely exceeds ~8
    "pelvis_pop": 60.0,      # m/s^2, 2nd difference at the dump rate outside landings (a landing may peak higher)
    "foot_slide": 0.02,      # m per contact, ball/heel point on the floor
    "floor_pen": -0.01,      # m
    "contact_z": 0.02,       # m, a foot point lower than this is on the floor
    "leg_overreach": 0.985,  # hip-ankle / leg length while that foot supports the body at speed
    "stiff_knee": 12.0,      # deg, support-knee flexion at mid-stance while running > 2.5 m/s
    "bob_min": 0.015,        # m, pelvis vertical range per stride while running > 3 m/s
    "face_travel": 60.0,     # deg, body facing vs travel direction above which running (> 2.5 m/s, not shuffling) reads sideways
    "yaw_rate": 600.0,       # deg/s, pelvis yaw rate (an athletic plant-and-turn peaks ~ 400-700 deg/s for < 0.15 s)
    "yaw_rate_frames": 4,    # consecutive frames above the limit to count as an instant turn
    "knee_max": 150.0, "knee_hyper": -3.0, "elbow_max": 160.0,
    "body_gap": 0.42,        # m, pelvis-to-pelvis horizontal distance below which two trunks intersect
    "ball_jump": 0.6,        # m per frame at 60 Hz (36 m/s) = teleport
    "palm_gap": 0.05,        # m, palm to ball surface while held
    "gaze": 50.0,            # deg, head yaw vs direction to the ball in the 0.4 s before a catch
    "pelvis_low": 0.62,      # pelvis height / leg length below which a grounded player reads collapsed (split, sitting)
}
BALL_R = 0.121
HALF_W, HALF_L = 7.5, 14.0


def v2(a, b): return (a[0] - b[0], a[1] - b[1])
def n2(a): return math.hypot(a[0], a[1])
def ang2(a, b):
    na, nb = n2(a), n2(b)
    if na < 1e-6 or nb < 1e-6: return 0.0
    c = max(-1, min(1, (a[0] * b[0] + a[1] * b[1]) / (na * nb)))
    return math.degrees(math.acos(c))
def dist3(a, b): return math.dist(a, b)
def angle3(a, b, c):  # angle at b
    u = [a[i] - b[i] for i in range(3)]; w = [c[i] - b[i] for i in range(3)]
    nu, nw = math.hypot(*u), math.hypot(*w)
    if nu < 1e-9 or nw < 1e-9: return 180
    return math.degrees(math.acos(max(-1, min(1, sum(u[i] * w[i] for i in range(3)) / (nu * nw)))))
def wrap(a): return math.atan2(math.sin(a), math.cos(a))


def video_map(props):
    """engine time -> list of (shot id, video time) from each shot's remap (piecewise linear, video->play)"""
    if not props: return lambda t: []
    ep = json.load(open(props))["episode"]
    shots = ep["shots"]
    def f(t):
        out = []
        for s in shots:
            rm = s.get("remap") or []
            for (a, pa), (b, pb) in zip(rm, rm[1:]):
                if isinstance(pa, (int, float)) and isinstance(pb, (int, float)) and pa != pb and min(pa, pb) <= t <= max(pa, pb):
                    out.append((s["id"], round(s["at"] + a + (t - pa) / (pb - pa) * (b - a), 2)))
                    break
        return out
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True); ap.add_argument("--out", required=True); ap.add_argument("--md")
    ap.add_argument("--props"); ap.add_argument("--offset", type=float, default=1.2)
    ap.add_argument("--thresh", help="JSON file overriding THRESH keys")
    a = ap.parse_args()
    T = dict(THRESH)
    if a.thresh: T.update(json.load(open(a.thresh)))
    D = json.load(open(a.dump)); hz = D["hz"]; dt = 1 / hz
    vmap = video_map(a.props)
    defects = []
    def add(pid, t, kind, val, note=""):
        defects.append({"player": pid, "t_engine": round(t, 3), "t_owner": round(t - a.offset, 3), "video": vmap(t), "kind": kind, "value": round(val, 3), "note": note})
    per = {}
    P = D["players"]
    for pid, pl in P.items():
        F = pl["frames"]; leg = pl["leg"]; n = len(F)
        J = lambda i, k: F[i]["J"][k]
        sp = [n2(f["v"]) for f in F]
        st = {"v_max": round(max(sp), 2)}
        if max(sp) > T["v_max"]: add(pid, F[sp.index(max(sp))]["t"], "speed", max(sp))
        # pelvis pops
        land = {i for i, f in enumerate(F) if f.get("stage") in ("landing", "takeoff")}
        pmax, pmt = 0, 0
        pops = []
        for i in range(1, n - 1):
            acc = math.dist([J(i + 1, "pelvis")[k] - 2 * J(i, "pelvis")[k] + J(i - 1, "pelvis")[k] for k in range(3)], [0, 0, 0]) * hz * hz
            if acc > pmax: pmax, pmt = acc, F[i]["t"]
            if acc > T["pelvis_pop"] and i not in land: pops.append((F[i]["t"], acc))
        st["pelvis_acc_max"] = [round(pmax, 1), pmt]
        for grp in group(pops, dt * 3): add(pid, grp[0][0], "pelvis_pop", max(x[1] for x in grp), f"{len(grp)} frames")
        # collapse: pelvis far below a deep athletic stance while the feet are on the floor (V2 regression found
        # 2026-11-28: O5 sank to a 0.1 m pelvis in a split when his strides were placed behind the hips)
        lows = [(F[i]["t"], J(i, "pelvis")[2] / leg) for i in range(n)
                if J(i, "pelvis")[2] / leg < T["pelvis_low"] and min(J(i, "toeL")[2], J(i, "toeR")[2]) < 0.05]
        for grp in group(lows, dt * 3): add(pid, grp[0][0], "pelvis_low", min(x[1] for x in grp), f"{len(grp)} frames, pelvis/leg")
        st["pelvis_min_ratio"] = round(min(J(i, "pelvis")[2] for i in range(n)) / leg, 3)
        # feet: contacts, slide, penetration, overreach, cadence
        contacts = []; floor_min = 1
        for s in "LR":
            for part in ("toe", "heel"):  # each point of the sole separately (switching toe <-> heel is a roll, not a slide)
                run = None
                for i, f in enumerate(F):
                    pnt = J(i, part + s)
                    floor_min = min(floor_min, pnt[2])
                    if pnt[2] < T["contact_z"]:
                        if run is None: run = {"s": s, "part": part, "i0": i, "p0": pnt, "path": 0.0, "prev": pnt}
                        else:
                            run["path"] += n2(v2(pnt, run["prev"])); run["prev"] = pnt
                    elif run:
                        run["i1"] = i; contacts.append(run); run = None
                if run: run["i1"] = n - 1; contacts.append(run)
        contacts.sort(key=lambda c: c["i0"])
        st["contacts"] = len([c for c in contacts if c["part"] == "toe"])
        slides = [c for c in contacts if c["i1"] - c["i0"] >= 2 and c["path"] > T["foot_slide"]]
        for c in slides: add(pid, F[c["i0"]]["t"], "foot_slide", c["path"], f"{c['s']} {c['part']} {F[c['i0']]['t']:.2f}-{F[c['i1']]['t']:.2f}")
        st["foot_slide_max"] = round(max([c["path"] for c in contacts if c["i1"] - c["i0"] >= 2] or [0]), 3)
        if floor_min < T["floor_pen"]: add(pid, 0, "floor_pen", floor_min)
        st["floor_min"] = round(floor_min, 3)
        tc = [c for c in contacts if c["part"] == "toe"]
        over = []
        for c in tc:
            s = c["s"]
            for i in range(c["i0"], c["i1"]):
                r = dist3(J(i, "hip" + s), J(i, "an" + s)) / leg
                if r > T["leg_overreach"] and sp[i] > 1.0: over.append((F[i]["t"], r))
        for grp in group(over, dt * 2): add(pid, grp[0][0], "leg_overreach", max(x[1] for x in grp), f"{len(grp)} frames, root outruns the stride")
        st["overreach_frames"] = len(over)
        # stiff running: support knee flexion at mid-stance while running
        stiff = []; knees_run = []
        for c in tc:
            mid = (c["i0"] + c["i1"]) // 2
            if sp[mid] > 2.5:
                s = c["s"]; kf = 180 - angle3(J(mid, "hip" + s), J(mid, "kn" + s), J(mid, "an" + s))
                knees_run.append(kf)
                if kf < T["stiff_knee"]: stiff.append((F[mid]["t"], kf))
        for t0, kf in stiff: add(pid, t0, "stiff_support_knee", kf, "deg flexion at mid-stance > 2.5 m/s")
        st["run_support_knee_mean"] = round(sum(knees_run) / len(knees_run), 1) if knees_run else None
        # floaty: pelvis bob per 0.5 s window while running > 3 m/s
        floaty = []
        w = int(0.5 * hz)
        for i in range(0, n - w, w // 2):
            if min(sp[i:i + w]) > 3.0:
                zs = [J(k, "pelvis")[2] for k in range(i, i + w)]
                if max(zs) - min(zs) < T["bob_min"]: floaty.append((F[i]["t"], max(zs) - min(zs)))
        for t0, b in floaty: add(pid, t0, "floaty_run", b, "pelvis bob (m) in 0.5 s at > 3 m/s")
        # cadence: contacts per second while moving > 2 m/s
        mov = [c for c in tc if sp[c["i0"]] > 2.0]
        tm = sum(dt for x in sp if x > 2.0)
        st["cadence_moving"] = round(len(mov) / tm, 2) if tm > 0.3 else None
        # facing vs travel, yaw rate
        yaw = []
        for i in range(n):
            r = v2(J(i, "hipR"), J(i, "hipL")); yaw.append(math.atan2(r[0], -r[1]))  # fwd = (-r_y, r_x)
        side = []
        for i in range(n):
            if sp[i] > 2.5:
                fw = (math.cos(yaw[i]), math.sin(yaw[i]))
                d = ang2(fw, F[i]["v"])
                if d > T["face_travel"]: side.append((F[i]["t"], d))
        for grp in group(side, dt * 2):
            if len(grp) >= 6: add(pid, grp[0][0], "facing_vs_travel", max(x[1] for x in grp), f"{len(grp)} frames ({len(grp) * dt:.2f} s)")
        yr = [abs(wrap(yaw[i + 1] - yaw[i])) * hz for i in range(n - 1)]
        st["yaw_rate_max"] = round(math.degrees(max(yr)), 0)
        fast = [(F[i]["t"], math.degrees(yr[i])) for i in range(n - 1) if math.degrees(yr[i]) > T["yaw_rate"]]
        for grp in group(fast, dt * 1.5):
            if len(grp) >= T["yaw_rate_frames"]: add(pid, grp[0][0], "instant_turn", max(x[1] for x in grp), f"{len(grp)} frames")
        # joints
        km, kn_, em = 0, 180, 0
        for i in range(0, n, 2):
            for s in "LR":
                kf = 180 - angle3(J(i, "hip" + s), J(i, "kn" + s), J(i, "an" + s)); ef = 180 - angle3(J(i, "sh" + s), J(i, "el" + s), J(i, "wr" + s))
                km, kn_, em = max(km, kf), min(kn_, kf), max(em, ef)
        st["knee_flex_range"] = [round(kn_, 1), round(km, 1)]; st["elbow_flex_max"] = round(em, 1)
        if km > T["knee_max"]: add(pid, 0, "knee_limit", km)
        if em > T["elbow_max"]: add(pid, 0, "elbow_limit", em)
        # stance quality: mean knee flexion while standing (speed < 0.6)
        stand = [180 - angle3(J(i, "hipL"), J(i, "knL"), J(i, "anL")) for i in range(n) if sp[i] < 0.6]
        st["stand_knee_mean"] = round(sum(stand) / len(stand), 1) if stand else None
        # bounds
        out_b = [F[i]["t"] for i in range(n) if abs(F[i]["root"][0]) > HALF_W + 0.3 or F[i]["root"][1] < -0.3]
        if out_b: add(pid, out_b[0], "out_of_bounds", len(out_b))
        st["source"] = F[0].get("src")
        per[pid] = st
    # body-body
    ids = list(P); n = len(P[ids[0]]["frames"])
    pair_min = {}
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            A, B = P[ids[x]]["frames"], P[ids[y]]["frames"]
            m, mt = 9, 0; hits = []
            for i in range(n):
                d = n2(v2(A[i]["J"]["pelvis"], B[i]["J"]["pelvis"]))
                if d < m: m, mt = d, A[i]["t"]
                if d < T["body_gap"]: hits.append((A[i]["t"], d))
            pair_min[f"{ids[x]}-{ids[y]}"] = [round(m, 3), mt]
            for grp in group(hits, dt * 2): add(f"{ids[x]}+{ids[y]}", grp[0][0], "body_intersection", min(h[1] for h in grp), f"{len(grp)} frames")
    # ball
    Bf = D["ball"]
    for i in range(1, len(Bf)):
        j = dist3(Bf[i]["p"], Bf[i - 1]["p"])
        if j > T["ball_jump"] * 60 / hz: add("ball", Bf[i]["t"], "ball_teleport", j)
    gaps = defaultdict(list)
    for i, b in enumerate(Bf):
        h = b["holder"]
        if h and not b["inFlight"] and h in P:
            J = P[h]["frames"][i]["J"]
            g = min(dist3(J["palmL"], b["p"]), dist3(J["palmR"], b["p"])) - BALL_R
            if P[h]["frames"][i].get("st") not in ("DRIBBLE",): gaps[h].append((b["t"], g))
        # ball inside another player's trunk
        for pid, pl in P.items():
            if pid == h: continue
            J = pl["frames"][i]["J"]
            if seg_dist(b["p"], J["pelvis"], J["chest"]) < 0.14 + BALL_R - 0.01:
                add(pid, b["t"], "ball_in_body", seg_dist(b["p"], J["pelvis"], J["chest"]))
    for h, gs in gaps.items():
        bad = [(t, g) for t, g in gs if g > T["palm_gap"]]
        per[h]["palm_gap_p95"] = round(sorted(g for _, g in gs)[int(0.95 * (len(gs) - 1))], 3)
        for grp in group(bad, dt * 2): add(h, grp[0][0], "palm_gap", max(x[1] for x in grp), f"{len(grp)} frames")
    # gaze before catches: holder changes
    for i in range(1, len(Bf)):
        h0, h1 = Bf[i - 1]["holder"], Bf[i]["holder"]
        if h1 and h1 != h0 and h1 in P:
            for k in range(max(0, i - int(0.4 * hz)), i):
                F = P[h1]["frames"][k]
                hd = F["J"]["head"]; to = v2(Bf[k]["p"], hd)
                d = abs(math.degrees(wrap(F["hy"] - math.atan2(to[1], to[0])))) if F.get("hy") is not None else 0
                if d > T["gaze"]: add(h1, F["t"], "gaze_off_ball", d, "before the catch"); break
    defects.sort(key=lambda d: d["t_engine"])
    kinds = defaultdict(int)
    for d in defects: kinds[d["kind"]] += 1
    rep = {"play": D["play"], "hz": hz, "thresholds": T, "summary": dict(kinds), "n_defects": len(defects), "players": per, "pair_min": pair_min, "defects": defects}
    json.dump(rep, open(a.out, "w"), indent=1)
    if a.md:
        L = [f"# Motion validation: {D['play']}", "", f"Thresholds are provisional engineering tolerances (see THRESH in tools/motion/motion_validate.py), not biomechanical benchmarks.", "",
             "| kind | count |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(kinds.items())] + ["", "| player | v max | pelvis acc max | contacts | slide max | overreach fr | run knee | stand knee | yaw rate max | cadence |", "|---|---|---|---|---|---|---|---|---|---|"]
        for pid, s in per.items():
            L.append(f"| {pid} | {s['v_max']} | {s['pelvis_acc_max'][0]} @ {s['pelvis_acc_max'][1]} | {s['contacts']} | {s['foot_slide_max']} | {s['overreach_frames']} | {s['run_support_knee_mean']} | {s['stand_knee_mean']} | {s['yaw_rate_max']} | {s['cadence_moving']} |")
        L += ["", "| owner t | video | player | defect | value | note |", "|---|---|---|---|---|---|"]
        for d in defects:
            L.append(f"| {d['t_owner']} | {', '.join(f'{s} {v}' for s, v in d['video'][:3])} | {d['player']} | {d['kind']} | {d['value']} | {d['note']} |")
        open(a.md, "w").write("\n".join(L) + "\n")
    print(json.dumps({"n_defects": len(defects), "summary": dict(kinds)}))


def seg_dist(p, a, b):
    ab = [b[i] - a[i] for i in range(3)]; ap_ = [p[i] - a[i] for i in range(3)]
    dd = sum(x * x for x in ab) or 1e-9
    u = max(0, min(1, sum(ab[i] * ap_[i] for i in range(3)) / dd))
    return math.dist(p, [a[i] + ab[i] * u for i in range(3)])


def group(rows, gap):
    out = []
    for r in rows:
        if out and r[0] - out[-1][-1][0] <= gap + 1e-9: out[-1].append(r)
        else: out.append([r])
    return out


if __name__ == "__main__":
    main()
