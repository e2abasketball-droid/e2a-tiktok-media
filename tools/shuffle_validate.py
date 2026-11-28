#!/usr/bin/env python3
"""E2A tactical validator for the SHUFFLE CUT (2026-11-28): "the basketball must be accurate".

Checks what the ENGINE draws (frame dump of template/scripts/dump-play-frames.mts, 120 fps) against the canonical
possession tactical/shuffle/e2a_shuffle_cut_v1.json. Deterministic. Exit code 1 on any FAIL.

  python3 tools/shuffle_validate.py --canonical template/tactical/shuffle/e2a_shuffle_cut_v1.json \
      --play template/tactical/plays/shuffle-cut-v1.json --frames frames.json --out report.json [--md report.md]

Sections: roster, fidelity (T0 anchors + K0..K6), bounds, speed / acceleration, collisions, ball, passes (3D ball vs
reach envelopes and bodies), SCREEN legality (stationary, one step, blind side, defender moves into the screener, contact),
CUT (timing after the entry and the set screen, never through the screener, tight brush, plant), coverage (X1 delayed
and trailing, X5 attached, X4 home and too far, X2 high, X3 pressure, nobody frozen), finish, defensive causes, and the
truth windows that gate every graphic (SCREEN SET, X1 DELAYED, LANE OPEN).
"""
import argparse, json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import court_geometry as G  # noqa: E402

V_WARN, V_MAX = 6.8, 7.5
A_WARN, A_MAX = 10.0, 14.0
FIDELITY = 0.03
MIN_GAP = 0.5
REACT = 0.15
VISION_HALF = 60.0
SCREEN_STEP = 1.2          # m centre to centre at the set: one normal step (~0.7 m) + two half-bodies
SCREEN_STILL = 0.15        # m/s


class Report:
    def __init__(self):
        self.rows, self.fail, self.warn = [], 0, 0

    def add(self, section, name, ok, value, warn=False):
        st = "PASS" if ok and not warn else ("WARN" if ok else "FAIL")
        self.rows.append({"section": section, "check": name, "status": st, "value": value})
        self.fail += st == "FAIL"
        self.warn += st == "WARN"
        print(f"{st}  [{section}] {name} - {value}")


def main():
    ap = argparse.ArgumentParser()
    for k in ("--canonical", "--play", "--frames", "--out"):
        ap.add_argument(k, required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    can = json.load(open(a.canonical))
    play = json.load(open(a.play))
    dump = json.load(open(a.frames))
    off = can["coordinates"]["engine_offset_s"]
    fps = dump["fps"]
    H = dump["heights"]
    F = dump["frames"]
    M = can["timeline_owner_s"]
    ids = [p["id"] for p in can["players"]]
    O = [i for i in ids if i[0] == "O"]
    X = [i for i in ids if i[0] == "X"]
    R = Report()
    pos = lambda f, i: (-f["P"][i][0], f["P"][i][1])
    vel = lambda f, i: (-f["P"][i][2], f["P"][i][3])
    spd = lambda f, i: math.hypot(*vel(f, i))
    fdir = lambda f, i: G.engine_heading_to_owner_dir(f["P"][i][4])
    ball = lambda f: (-f["B"][0], f["B"][1], f["B"][2])
    at = lambda t: F[min(len(F) - 1, max(0, round((t + off) * fps)))]
    T = lambda f: f["t"] - off
    D = lambda f, i, j: G.dist(pos(f, i), pos(f, j))
    span = lambda t0, t1: [f for f in F if t0 <= T(f) <= t1]

    # 1 roster
    R.add("roster", "10 players: 5 offence, 5 defence, all tracked", len(O) == 5 and len(X) == 5 and set(ids) == set(play["tracks"]), f"{len(O)} O / {len(X)} X")
    R.add("roster", "every defender guards one distinct attacker", sorted(p.get("guards") for p in can["players"] if p["team"] == "X") == sorted(O),
          ",".join(p.get("guards", "?") for p in can["players"] if p["team"] == "X"))

    # 2 fidelity
    f0 = at(0.0)
    e0 = max((G.dist(pos(f0, i), can["anchors_T0"][i]), i) for i in ids)
    R.add("fidelity", f"T0 anchors reproduced within {FIDELITY} m", e0[0] <= FIDELITY, f"max {e0[0]:.3f} m ({e0[1]})")
    if "anchors_brief" in can:   # every departure from the brief's T0 coordinates must be a documented correction
        moved = {i: G.dist(can["anchors_brief"][i], can["anchors_T0"][i]) for i in ids}
        moved = {i: d for i, d in moved.items() if d > 1e-6}
        logged = " ".join(json.dumps(c) for c in can.get("corrections_log", []))
        undoc = [i for i in moved if i not in logged]
        R.add("fidelity", "brief T0 anchors kept except documented minimum corrections", not undoc,
              ", ".join(f"{i} moved {d:.2f} m" for i, d in moved.items()) or "none moved")
    worst = (0.0, "")
    for k in can["keyframes"]:
        f = at(k["t"])
        for i in ids:
            e = G.dist(pos(f, i), k["players"][i]["pos"])
            if e > worst[0]:
                worst = (e, f"{i}@{k['k']}")
    R.add("fidelity", f"K0..K6 reproduced within {FIDELITY} m (all ten players)", worst[0] <= FIDELITY, f"max {worst[0]:.3f} m ({worst[1]})")

    # 3 bounds
    oob = sorted({i for f in F for i in ids if not G.in_bounds(pos(f, i), 0.2)})
    R.add("bounds", "everyone in bounds (centre >= 0.2 m inside the lines)", not oob, ",".join(oob) or "ok")

    # 4 speed / acceleration
    dt = 1.0 / fps
    W = max(1, round(0.05 * fps))
    for i in ids:
        P = [pos(f, i) for f in F]
        Vs = [((P[n + W][0] - P[n - W][0]) / (2 * W * dt), (P[n + W][1] - P[n - W][1]) / (2 * W * dt)) for n in range(W, len(P) - W)]
        vm = max((math.hypot(*v), F[n + W]["t"] - off) for n, v in enumerate(Vs))
        am = max((math.hypot(Vs[n + W][0] - Vs[n - W][0], Vs[n + W][1] - Vs[n - W][1]) / (2 * W * dt), F[n + 2 * W]["t"] - off) for n in range(W, len(Vs) - W))
        R.add("motion", f"{i} top speed <= {V_MAX} m/s", vm[0] <= V_MAX, f"{vm[0]:.2f} m/s at {vm[1]:+.2f} s", warn=vm[0] > V_WARN)
        R.add("motion", f"{i} acceleration <= {A_MAX} m/s^2", am[0] <= A_MAX, f"{am[0]:.1f} m/s^2 at {am[1]:+.2f} s", warn=am[0] > A_WARN)

    # 5 collisions
    g = (99.0, "")
    for f in F[::2]:
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                d = D(f, ids[x], ids[y])
                if d < g[0]:
                    g = (d, f"{ids[x]}-{ids[y]} at {T(f):+.2f} s")
    R.add("collisions", f"no bodies overlap (>= {MIN_GAP} m centre to centre)", g[0] >= MIN_GAP, f"min {g[0]:.2f} m ({g[1]})")

    # 6 ball
    jump, orphan = 0.0, 0
    for fa, fb in zip(F, F[1:]):
        jump = max(jump, G.dist3(ball(fa), ball(fb)) * fps)
        if not fb["h"] and not fb["fl"] and T(fb) < M["k6"]:
            orphan += 1
    R.add("ball", "ball 3D speed <= 16 m/s frame to frame (no teleports)", jump <= 16, f"max {jump:.1f} m/s")
    R.add("ball", "ball always in a hand or in flight until the layup", orphan == 0, f"{orphan} orphan frames")

    # 7 passes
    lanes = {}
    for e in [e for e in play["ball"] if e["type"] == "pass"]:
        fr = [f for f in F if e["t0"] + 0.02 <= f["t"] <= e["t1"] - 0.02]
        worst, through = {}, []
        for f in fr:
            b = ball(f)
            for x in X:
                c = G.reach_clearance(b, pos(f, x), fdir(f, x), H[x], G.lunge_after(f["t"] - e["t0"]))
                if x not in worst or c < worst[x][0]:
                    worst[x] = (c, T(f), b[2])
            for i in ids:
                if i not in (e["from"], e["to"]) and G.dist(b, pos(f, i)) < G.BODY_R + G.BALL_R and b[2] < H[i]:
                    through.append(f"{i}@{T(f):+.2f}")
        mn = min(worst.items(), key=lambda kv: kv[1][0])
        st = G.lane_state(mn[1][0])
        key = f"{e['from']}->{e['to']}"
        lanes[key] = {"state": st, "closest": mn[0], "clearance_m": round(mn[1][0], 3), "per_defender": {k: round(v[0], 3) for k, v in worst.items()}}
        R.add("passes", f"pass {key} clears every reach envelope (OPEN)", st == "OPEN", f"{st}: closest {mn[0]} {mn[1][0]:.2f} m at {mn[1][1]:+.2f} s, ball {mn[1][2]:.2f} m")
        R.add("passes", f"pass {key} never passes through a body", not through, ", ".join(through[:4]) or "ok")
        fa, fb = at(e["t0"] - off), at(e["t1"] - off)
        L = G.dist(pos(fa, e["from"]), pos(fb, e["to"]))
        sp = L / (e["t1"] - e["t0"])
        R.add("passes", f"pass {key} speed 6-14 m/s", 6 <= sp <= 14, f"{sp:.1f} m/s over {L:.2f} m")

    # 8 the screen
    sc = can["screen"]
    t_set, t_rel = sc["set_at"], sc["released_at"]
    vs = max(spd(f, "O5") for f in span(t_set + 0.05, t_rel - 0.05))
    R.add("screen", "O5 is stationary while the screen is set (<= 0.15 m/s)", vs <= SCREEN_STILL, f"max {vs:.3f} m/s from {t_set:.2f} to {t_rel:.2f} s")
    fs = at(t_set)
    dset = D(fs, "O5", "X1")
    R.add("screen", f"set at least one normal step from X1 (>= {SCREEN_STEP} m centre to centre)", dset >= SCREEN_STEP, f"{dset:.2f} m at {t_set:.2f} s")
    to5 = (pos(fs, "O5")[0] - pos(fs, "X1")[0], pos(fs, "O5")[1] - pos(fs, "X1")[1])
    ang = G.angle_deg(fdir(fs, "X1"), to5)
    R.add("screen", "blind (back) screen: set outside X1's focused vision", ang > VISION_HALF, f"O5 at {ang:.0f} deg from X1's facing")
    R.add("screen", "set behind X1 (basket side)", G.dist_to_hoop(pos(fs, "O5")) < G.dist_to_hoop(pos(fs, "X1")),
          f"O5 {G.dist_to_hoop(pos(fs, 'O5')):.2f} m / X1 {G.dist_to_hoop(pos(fs, 'X1')):.2f} m from the hoop")
    win = span(t_set, t_rel)
    dmin = min((D(f, "O5", "X1"), T(f)) for f in win)
    R.add("screen", "the screen is effective: X1 reaches O5's body (contact <= 0.65 m)", dmin[0] <= 0.65, f"min {dmin[0]:.2f} m at {dmin[1]:+.2f} s")
    fc = at(dmin[1])
    R.add("screen", "the defender moves into the screener, not the reverse", spd(fc, "O5") <= SCREEN_STILL and spd(fc, "X1") > 0.3,
          f"at contact O5 {spd(fc, 'O5'):.2f} m/s, X1 {spd(fc, 'X1'):.2f} m/s")
    still_x1 = max(spd(f, "X1") for f in span(t_set - 0.1, t_set + 0.1))
    R.add("screen", "X1 is (near) stationary when the blind screen is set (one-step rule applies)", still_x1 <= 0.6, f"X1 {still_x1:.2f} m/s")

    # 9 the cut
    on = next(T(f) for f in F if T(f) > M["k1"] and spd(f, "O1") > 1.5)
    R.add("cut", "O1 does not cut before the entry catch and the set screen (+0.15 s)", on >= max(M["k1"], t_set) + 0.15, f"cut onset {on:+.2f} s; catch {M['k1']:.2f}, set {t_set:.2f}")
    d15 = min((D(f, "O1", "O5"), T(f)) for f in span(M["k3"], M["k5"]))
    R.add("cut", "O1 never passes through the screener (>= 0.5 m)", d15[0] >= 0.5, f"min {d15[0]:.2f} m at {d15[1]:+.2f} s")
    R.add("cut", "O1 cuts tight off the screen (brush: <= 0.75 m)", d15[0] <= 0.75, f"min {d15[0]:.2f} m")
    plant = [s for s in play.get("v33extra", {}).get("O1", []) if s["k"] == "burst"]
    R.add("cut", "a plant / first-step burst at the start of the cut", bool(plant) and abs(plant[0]["t"] - off - M["k3"]) < 0.1, f"burst at {plant[0]['t'] - off:+.2f} s" if plant else "none")
    vset = max(spd(f, "O1") for f in span(0.3, M["k3"] - 0.05))
    vcut = max(spd(f, "O1") for f in span(M["k3"], M["k5"]))
    R.add("cut", "change of pace: slow set-up then explosive cut (cut >= 3x set-up speed)", vcut >= 3 * vset, f"set-up {vset:.2f} m/s, cut {vcut:.2f} m/s")
    cv = (can["designed_spots"]["O1_catch"][0] - can["designed_spots"]["O1_setup_plant"][0], can["designed_spots"]["O1_catch"][1] - can["designed_spots"]["O1_setup_plant"][1])
    R.add("cut", "the cut goes toward the basket (dy < 0, diagonal)", cv[1] < 0 and abs(cv[0]) > 0.5, f"{math.degrees(math.atan2(-cv[1], cv[0])):.0f} deg to the baseline")

    # 10 coverage
    fk5 = at(M["k5"])
    sep = D(fk5, "X1", "O1")
    R.add("coverage", "X1 is delayed: >= 1.5 m behind O1 at the catch", sep >= 1.5, f"{sep:.2f} m")
    R.add("coverage", "X1 trails (farther from the hoop than O1) at the catch", G.dist_to_hoop(pos(fk5, "X1")) > G.dist_to_hoop(pos(fk5, "O1")),
          f"X1 {G.dist_to_hoop(pos(fk5, 'X1')):.2f} / O1 {G.dist_to_hoop(pos(fk5, 'O1')):.2f} m from the hoop")
    x5 = max(D(f, "X5", "O5") for f in F if T(f) >= 0)
    R.add("coverage", "X5 stays attached to O5 (no switch, <= 1.6 m)", x5 <= 1.6, f"max {x5:.2f} m")
    x4 = min(D(f, "X4", "O1") for f in span(M["k5"], M["k6"]))
    R.add("coverage", "X4 too far to contest the cut (>= 3.0 m from O1, catch to release)", x4 >= 3.0, f"min {x4:.2f} m")
    x4h = max(D(f, "X4", "O4") for f in F if T(f) >= 0)
    R.add("coverage", "X4 stays connected to O4 (<= 1.6 m)", x4h <= 1.6, f"max {x4h:.2f} m")
    x2 = min(pos(f, "X2")[1] for f in F if T(f) >= 0)
    R.add("coverage", "X2 stays high (y >= 8.0 m) and connected to O2 (<= 1.6 m)", x2 >= 8.0 and max(D(f, "X2", "O2") for f in F if T(f) >= 0) <= 1.6, f"min y {x2:.2f} m")
    hold3 = span(M.get("x3_set", M["k1"] + 0.2), M["rel2"])
    p3 = [D(f, "X3", "O3") for f in hold3]
    R.add("coverage", "X3 pressures the passer after his closeout (0.6-1.4 m until the pass)", 0.6 <= min(p3) and max(p3) <= 1.4, f"{min(p3):.2f}-{max(p3):.2f} m")
    frozen = [x for x in X if sum(G.dist(pos(fa, x), pos(fb, x)) for fa, fb in zip(F[::6], F[6::6]) if T(fa) >= 0) < 0.3]
    R.add("coverage", "no defender is motionless (each moves >= 0.3 m)", not frozen, ",".join(frozen) or "all move")

    # 11 finish
    lay = next(e for e in play["ball"] if e["type"] == "layup")
    fl = at(lay["t0"] - off)
    R.add("finish", "layup released within 1.5 m of the hoop", G.dist_to_hoop(pos(fl, "O1")) <= 1.5, f"{G.dist_to_hoop(pos(fl, 'O1')):.2f} m")
    nl = min((D(fl, "O1", x), x) for x in X)
    R.add("finish", "nearest defender >= 1.0 m at the release (late contest only)", nl[0] >= 1.0, f"{nl[1]} {nl[0]:.2f} m")
    catch = next(e for e in play["ball"] if e["type"] == "pass" and e["to"] == "O1")["t1"]
    R.add("finish", "catch to release 0.45-0.9 s (gather + two steps, no dribble)", 0.45 <= lay["t0"] - catch <= 0.9, f"{lay['t0'] - catch:.2f} s")
    R.add("finish", "left-side approach finished with the left hand off the glass", lay.get("hand") == -1 and "glass" in lay and pos(fl, "O1")[0] < 0, f"hand {lay.get('hand')}, x {pos(fl, 'O1')[0]:.2f}")

    # 12 defensive causes
    audit = {}
    for x in X:
        sp = [spd(f, x) for f in F]
        onsets, still = [], 0
        for n, s in enumerate(sp):
            if s < 0.3:
                still += 1
            else:
                if s >= 0.6 and still >= round(0.1 * fps):
                    onsets.append(T(F[n]))
                if s >= 0.6:
                    still = 0
        rows = []
        for t0 in onsets:
            prev = [c for c in can["defensive_causes"].get(x, []) if c["t"] <= t0 - REACT + 1e-6]
            c = max(prev, key=lambda c: c["t"]) if prev else None
            rows.append({"onset": round(t0, 3), "cause": c["cause"] if c else None, "reaction": round(t0 - c["t"], 3) if c else None})
        audit[x] = rows
        R.add("causes", f"{x}: every movement onset follows a declared cause by >= {REACT} s", all(r["cause"] for r in rows),
              "; ".join(f"{r['onset']:+.2f}s <- {r['cause']} (+{r['reaction']}s)" if r["cause"] else f"{r['onset']:+.2f}s <- NO CAUSE" for r in rows) or "no onsets")

    # 13 truth windows (gate the graphics)
    def windows(pred):
        out, cur = [], None
        for f in F:
            ok = pred(f)
            if ok and cur is None:
                cur = T(f)
            if not ok and cur is not None:
                out.append([round(cur, 3), round(T(f), 3)])
                cur = None
        if cur is not None:
            out.append([round(cur, 3), round(T(F[-1]), 3)])
        return out
    S = can["screen"]["spot"]
    TW = {"screen_set": windows(lambda f: t_set <= T(f) <= t_rel and G.dist(pos(f, "O5"), S) <= 0.05 and spd(f, "O5") <= SCREEN_STILL),
          "x1_delayed": windows(lambda f: M["k3"] <= T(f) <= M["k5"] + 0.3 and (D(f, "X1", "O5") <= 0.75 or D(f, "X1", "O1") >= 1.5)),
          "o1_behind_x1": windows(lambda f: T(f) >= M["k3"] and G.dist_to_hoop(pos(f, "O1")) + 0.3 < G.dist_to_hoop(pos(f, "X1")) and T(f) <= M["k6"])}
    R.add("truth", "SCREEN SET is true from the set to K4", any(w[0] <= M["k2"] and w[1] >= M["k4"] for w in TW["screen_set"]), json.dumps(TW["screen_set"]))
    R.add("truth", "X1 DELAYED is true at K4 and at the catch", any(w[0] <= M["k4"] and w[1] >= M["k5"] for w in TW["x1_delayed"]), json.dumps(TW["x1_delayed"]))
    R.add("truth", "O1 BEHIND X1 (closer to the rim) from the brush to the release", any(w[0] <= M["brush"] + 0.05 and w[1] >= M["k6"] - 0.01 for w in TW["o1_behind_x1"]), json.dumps(TW["o1_behind_x1"]))

    rep = {"play": play["id"], "passed": sum(r["status"] == "PASS" for r in R.rows), "warnings": R.warn, "failed": R.fail,
           "verdict": "PASS" if R.fail == 0 else "FAIL", "rows": R.rows, "lanes": lanes, "truth_windows_owner_s": TW, "defensive_audit": audit,
           "limits": {"speed_max": V_MAX, "accel_max": A_MAX, "screen_step_m": SCREEN_STEP, "screen_still_mps": SCREEN_STILL, "reaction_min_s": REACT}}
    json.dump(rep, open(a.out, "w"), indent=1)
    if a.md:
        L = [f"# Tactical validation: {play['id']}", "", f"Verdict: **{rep['verdict']}** ({rep['passed']} pass, {R.warn} warn, {R.fail} fail).", "",
             "| Section | Check | Status | Value |", "|---|---|---|---|"] + [f"| {r['section']} | {r['check']} | {r['status']} | {r['value']} |" for r in R.rows]
        open(a.md, "w").write("\n".join(L) + "\n")
    print(f"\nVERDICT {rep['verdict']}: {rep['passed']} pass, {R.warn} warn, {R.fail} fail")
    sys.exit(1 if R.fail else 0)


if __name__ == "__main__":
    main()
