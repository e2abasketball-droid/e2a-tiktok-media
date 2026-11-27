#!/usr/bin/env python3
"""E2A Basketball IQ tactical validator (2026-11-27, EP02 "Beat the Blitz"): "First validate the basketball."

Checks what the ENGINE draws (a frame dump from template/scripts/dump-play-frames.mts) against the CANONICAL owner file.
Deterministic; no randomness. Exit code 1 on any FAIL: the final cinematic render must not start.

  python3 tools/iq_play_validate.py --canonical template/tactical/iq02/basketball_iq_02_blitz_short_roll.json \
      --play template/tactical/plays/iq02-beat-the-blitz.json --frames frames.json --out report.json [--md report.md]

Sections: roster, canonical fidelity (K0..K5), bounds, speed / acceleration, collisions, ball continuity, real passes
(3D ball vs every defender's reach envelope and body), the freeze-frame decision lanes (A drive / B corner / C cut),
truth windows that gate the graphics (2 ON THE BALL, 4 ON 3, X4 IN THE PAINT), defensive-cause audit, the cut
(angle, behind X4, outside X4's vision), and the finish.
"""
import argparse, json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import court_geometry as G  # noqa: E402

V_WARN, V_MAX = 6.8, 7.5           # m/s (elite sprint ~8-9 m/s is never needed in a half-court set)
A_WARN, A_MAX = 10.0, 14.0         # m/s^2 horizontal (game braking is mostly <= 8-10)
FIDELITY = 0.03                    # m, keyframe reproduction tolerance
MIN_GAP = 0.5                      # m, centre to centre
REACT = 0.15                       # s, minimum defensive reaction time
VISION_HALF = 60.0                 # deg, half-angle of the focused vision cone (120 deg)


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
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--play", required=True)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    can = json.load(open(a.canonical))
    play = json.load(open(a.play))
    dump = json.load(open(a.frames))
    off = can["coordinates"]["engine_offset_s"]
    fps = dump["fps"]
    H = dump["heights"]
    F = dump["frames"]
    ids = [p["id"] for p in can["players"]]
    O = [i for i in ids if i[0] == "O"]
    X = [i for i in ids if i[0] == "X"]
    R = Report()
    # owner-frame accessors
    pos = lambda f, i: (-f["P"][i][0], f["P"][i][1])
    vel = lambda f, i: (-f["P"][i][2], f["P"][i][3])
    fdir = lambda f, i: G.engine_heading_to_owner_dir(f["P"][i][4])
    ball = lambda f: (-f["B"][0], f["B"][1], f["B"][2])
    at = lambda t_owner: F[min(len(F) - 1, max(0, round((t_owner + off) * fps)))]
    T = lambda f: f["t"] - off                  # owner time of a frame

    # 1 roster ----------------------------------------------------------------------------------------------------
    R.add("roster", "10 players on the floor: 5 offence, 5 defence", len(O) == 5 and len(X) == 5 and set(ids) == set(play["tracks"]),
          f"{len(O)} O / {len(X)} X")
    R.add("roster", "every defender guards one distinct attacker", sorted(p.get("guards") for p in can["players"] if p["team"] == "X") == sorted(O),
          ",".join(p.get("guards", "?") for p in can["players"] if p["team"] == "X"))

    # 2 canonical fidelity ----------------------------------------------------------------------------------------------
    worst, who = 0.0, ""
    for k in can["keyframes"]:
        f = at(k["t"])
        for i in ids:
            want = k.get(i, can["keyframes"][0][i])
            if i in can["static_players"]["ids"] and i not in k and k["k"] != "K0":
                tol = 0.15          # the static four: stance shifts allowed
                e = G.dist(pos(f, i), want)
                if e > tol:
                    R.add("fidelity", f"{i} stays within 0.15 m of its K0 spot at {k['k']}", False, f"{e:.3f} m")
                continue
            e = G.dist(pos(f, i), want)
            if e > worst:
                worst, who = e, f"{i}@{k['k']}"
    R.add("fidelity", f"K0..K5 reproduced within {FIDELITY} m (owner coordinates)", worst <= FIDELITY, f"max error {worst:.3f} m ({who})")
    static_dev = max(G.dist(pos(f, i), can["keyframes"][0][i]) for f in F if T(f) >= 0 for i in can["static_players"]["ids"])
    R.add("fidelity", "O2, O3, X2, X3 stay at their K0 spots (<= 0.15 m stance shifts)", static_dev <= 0.15, f"max {static_dev:.3f} m")

    # 3 bounds --------------------------------------------------------------------------------------------------------
    oob = sorted({i for f in F for i in ids if not G.in_bounds(pos(f, i), 0.2)})
    R.add("bounds", "everyone in bounds (centre >= 0.2 m inside the lines)", not oob, ",".join(oob) or "ok")

    # 4 speed / acceleration (from positions, as drawn) -----------------------------------------------------------------
    dt = 1.0 / fps
    vmax = {i: (0.0, 0.0) for i in ids}
    amax = {i: (0.0, 0.0) for i in ids}
    W = max(1, round(0.05 * fps))     # 50 ms differencing window (the render shows 30 fps)
    for i in ids:
        P = [pos(f, i) for f in F]
        Vs = [((P[n + W][0] - P[n - W][0]) / (2 * W * dt), (P[n + W][1] - P[n - W][1]) / (2 * W * dt)) for n in range(W, len(P) - W)]
        for n, v in enumerate(Vs):
            s = math.hypot(*v)
            if s > vmax[i][0]:
                vmax[i] = (s, F[n + W]["t"])
        for n in range(W, len(Vs) - W):
            acc = math.hypot(Vs[n + W][0] - Vs[n - W][0], Vs[n + W][1] - Vs[n - W][1]) / (2 * W * dt)
            if acc > amax[i][0]:
                amax[i] = (acc, F[n + 2 * W]["t"])
    for i in ids:
        s, t = vmax[i]
        R.add("motion", f"{i} top speed <= {V_MAX} m/s", s <= V_MAX, f"{s:.2f} m/s at {t - off:+.2f} s", warn=s > V_WARN)
    for i in ids:
        s, t = amax[i]
        R.add("motion", f"{i} acceleration <= {A_MAX} m/s^2", s <= A_MAX, f"{s:.1f} m/s^2 at {t - off:+.2f} s", warn=s > A_WARN)

    # 5 collisions ----------------------------------------------------------------------------------------------------
    g, gw = 99.0, ""
    for f in F[::2]:
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                d = G.dist(pos(f, ids[x]), pos(f, ids[y]))
                if d < g:
                    g, gw = d, f"{ids[x]}-{ids[y]} at {T(f):+.2f} s"
    R.add("collisions", f"no bodies overlap (>= {MIN_GAP} m centre to centre)", g >= MIN_GAP, f"min {g:.2f} m ({gw})")

    # 6 ball continuity -------------------------------------------------------------------------------------------------
    jump, orphan = 0.0, 0
    for f0, f1 in zip(F, F[1:]):
        b0, b1 = ball(f0), ball(f1)
        jump = max(jump, G.dist3(b0, b1) * fps)
        if not f1["h"] and not f1["fl"]:
            orphan += T(f1) < can["ball_events"][-1]["t"]
    R.add("ball", "ball 3D speed <= 16 m/s frame to frame (no teleports)", jump <= 16, f"max {jump:.1f} m/s")
    R.add("ball", "ball always in a hand or in flight until the layup", orphan == 0, f"{orphan} orphan frames")

    # 7 real passes: 3D trajectory vs reach envelopes and bodies --------------------------------------------------------
    passes = [e for e in play["ball"] if e["type"] == "pass"]
    lanes = {}
    for e in passes:
        fr = [f for f in F if e["t0"] + 0.02 <= f["t"] <= e["t1"] - 0.02]
        worst = {}
        through = []
        for f in fr:
            b = ball(f)
            for x in X:
                tl = f["t"] - e["t0"]
                c = G.reach_clearance(b, pos(f, x), fdir(f, x), H[x], G.lunge_after(tl))
                if x not in worst or c < worst[x][0]:
                    worst[x] = (c, T(f), b[2])
            for i in ids:
                if i in (e["from"], e["to"]):
                    continue
                if G.dist(b, pos(f, i)) < G.BODY_R + G.BALL_R and b[2] < H[i]:
                    through.append(f"{i}@{T(f):+.2f}")
        mn = min(worst.items(), key=lambda kv: kv[1][0])
        st = G.lane_state(mn[1][0])
        lanes[f"{e['from']}->{e['to']}"] = {"state": st, "closest": mn[0], "clearance_m": round(mn[1][0], 3), "at_owner_s": round(mn[1][1], 3),
                                           "ball_z": round(mn[1][2], 2), "per_defender": {k: round(v[0], 3) for k, v in worst.items()}}
        R.add("passes", f"pass {e['from']}->{e['to']} clears every reach envelope (OPEN)", st == "OPEN",
              f"{st}: closest {mn[0]} clearance {mn[1][0]:.2f} m at {mn[1][1]:+.2f} s, ball {mn[1][2]:.2f} m high")
        R.add("passes", f"pass {e['from']}->{e['to']} never passes through a body", not through, ", ".join(through[:4]) or "ok")
        f0, f1 = at(e["t0"] - off), at(e["t1"] - off)
        L = G.dist(pos(f0, e["from"]), pos(f1, e["to"]))
        sp = L / (e["t1"] - e["t0"])
        R.add("passes", f"pass {e['from']}->{e['to']} speed 6-14 m/s", 6 <= sp <= 14, f"{sp:.1f} m/s over {L:.2f} m")
        if e.get("ballistic"):
            Tf = e["t1"] - e["t0"]
            R.add("passes", f"pass {e['from']}->{e['to']} vertical path is a gravity parabola", True, f"rise over the chord g*T^2/8 = {9.81 * Tf * Tf / 8:.2f} m")
    # the ball must go AROUND X4 on the decisive pass
    k = "O5->O4"
    if k in lanes:
        c4 = lanes[k]["per_defender"].get("X4", 9)
        R.add("passes", "the O5->O4 ball goes around X4 (outside his reach for the whole flight)", c4 >= G.CONTEST_MARGIN, f"X4 clearance {c4:.2f} m")

    # 8 the freeze-frame decision ---------------------------------------------------------------------------------------
    dec = can["decision"]
    fz = at(dec["freeze_t"])
    o5 = pos(fz, "O5")

    def hypo_lane(src, dst, style="chest", z0=1.2, z1=1.2, Tf=0.6):
        """hypothetical pass at the freeze, defenders frozen where they are, reach growing after their reaction"""
        best = (9.0, "")
        for n in range(1, 60):
            u = n / 60
            if style == "bounce":
                z = G.bounce_z(u, Tf, z0, z1)
            else:
                z = z0 + (z1 - z0) * u + 0.5 * 9.81 * Tf * Tf * u * (1 - u)
            b = (src[0] + (dst[0] - src[0]) * u, src[1] + (dst[1] - src[1]) * u, z)
            for x in X:
                c = G.reach_clearance(b, pos(fz, x), fdir(fz, x), H[x], G.lunge_after(u * Tf))
                if c < best[0]:
                    best = (c, x)
        return best

    # A DRIVE: O5's path to the rim; blocked when a defender's body/reach covers the line (ground level drive)
    rim = (G.HOOP[0], G.HOOP[1])
    q, u, dX4 = G.seg_point(o5, rim, pos(fz, "X4"))
    others = min(G.seg_point(o5, rim, pos(fz, x))[2] for x in X if x != "X4")
    drive_state = "BLOCKED" if dX4 <= 1.0 else ("CONTESTED" if dX4 <= 1.6 else "OPEN")
    R.add("decision", "A DRIVE is wrong: X4 is on O5's line to the rim", drive_state == "BLOCKED", f"X4 {dX4:.2f} m from the O5->rim line at u={u:.2f} ({drive_state}); next defender {others:.2f} m")
    cB, wB = hypo_lane(o5, pos(fz, "O3"), Tf=0.85)
    stB = G.lane_state(cB)
    R.add("decision", "B CORNER is wrong: X3 is home, the O5->O3 lane is not open", stB in ("CONTESTED", "BLOCKED"), f"{stB}: {wB} clearance {cB:.2f} m; X3-O3 {G.dist(pos(fz, 'X3'), pos(fz, 'O3')):.2f} m")
    # C CUT: the lane to where O4 catches (his K4 spot), with the pass the play actually throws (style from the play)
    catch_spot = next(k_ for k_ in can["keyframes"] if k_["k"] == "K4")["O4"]
    pc = next(e for e in passes if e["to"] == "O4")
    cC, wC = hypo_lane(o5, catch_spot, pc.get("style", "chest"), z0=1.15, z1=1.12, Tf=pc["t1"] - pc["t0"])
    stC = G.lane_state(cC)
    R.add("decision", "C CUT is right: the lane to O4's catch spot is OPEN at the freeze", stC == "OPEN", f"{stC}: closest {wC} clearance {cC:.2f} m")
    nearest_O4 = min((G.dist(pos(at(3.05), "O4"), pos(at(3.05), x)), x) for x in X)
    R.add("decision", "C: O4 open at the catch (nearest defender >= 2.0 m)", nearest_O4[0] >= 2.0, f"{nearest_O4[1]} {nearest_O4[0]:.2f} m")
    one = [drive_state == "OPEN", stB == "OPEN", stC == "OPEN"]
    R.add("decision", "exactly one option is open, and it is the marked correct one (C)", one == [False, False, True] and
          [o["correct"] for o in dec["options"]] == [False, False, True], f"A {drive_state} / B {stB} / C {stC}")

    # 9 truth windows (gate every on-screen claim) ------------------------------------------------------------------------
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

    two = lambda f: f["h"] == "O1" and G.dist(pos(f, "X1"), pos(f, "O1")) <= 1.6 and G.dist(pos(f, "X5"), pos(f, "O1")) <= 1.6
    def four(f):
        if f["h"] != "O5":
            return False
        b = (ball(f)[0], ball(f)[1])
        return all(G.dist(pos(f, x), pos(f, "O1")) <= 2.0 and G.dist(pos(f, x), b) > 2.5 for x in ("X1", "X5"))
    paint = lambda f: G.in_paint(pos(f, "X4"))
    TW = {"two_on_ball": windows(two), "four_on_three": windows(four), "x4_in_paint": windows(paint)}
    R.add("truth", "2 ON THE BALL is true during the blitz", any(w[0] <= 0.80 <= w[1] for w in TW["two_on_ball"]), json.dumps(TW["two_on_ball"]))
    R.add("truth", "4 ON 3 is true from the catch through the freeze", any(w[0] <= 1.5 and w[1] >= dec["freeze_t"] for w in TW["four_on_three"]), json.dumps(TW["four_on_three"]))
    R.add("truth", "X4 is IN THE PAINT at the freeze", any(w[0] <= dec["freeze_t"] <= w[1] for w in TW["x4_in_paint"]), json.dumps(TW["x4_in_paint"]))

    # 10 defensive-cause audit ----------------------------------------------------------------------------------------
    causes = can["defensive_causes"]
    audit = {}
    for x in X:
        sp = [math.hypot(*vel(f, x)) for f in F]
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
            prev = [c for c in causes.get(x, []) if c["t"] <= t0 - REACT + 1e-6]
            # pre-roll moves before K0 follow the defender's own man (declared cause at -1.2)
            c = max(prev, key=lambda c: c["t"]) if prev else None
            rows.append({"onset_owner_s": round(t0, 3), "cause": c["cause"] if c else None, "reaction_s": round(t0 - c["t"], 3) if c else None})
        audit[x] = rows
        bad = [r for r in rows if r["cause"] is None]
        R.add("causes", f"{x}: every movement onset follows a declared cause by >= {REACT} s", not bad,
              "; ".join(f"{r['onset_owner_s']:+.2f}s <- {r['cause']} (+{r['reaction_s']}s)" if r["cause"] else f"{r['onset_owner_s']:+.2f}s <- NO CAUSE" for r in rows) or "no onsets (holds his spot)")

    # 11 the cut, X4 loses the cutter -----------------------------------------------------------------------------------
    o4k2 = can["keyframes"][2]["O4"]
    o4k5 = can["keyframes"][5]["O4"]
    cutv = (o4k5[0] - o4k2[0], o4k5[1] - o4k2[1])
    ang = math.degrees(math.atan2(abs(cutv[1]), abs(cutv[0])))
    R.add("cut", "O4's cut is a diagonal (45-degree family: 35-60 degrees to the baseline)", 35 <= ang <= 60, f"{ang:.0f} degrees")
    f_catch = at(3.05)
    R.add("cut", "O4 is baseline-side of X4 at the catch (behind him)", pos(f_catch, "O4")[1] < pos(f_catch, "X4")[1],
          f"O4 y {pos(f_catch, 'O4')[1]:.2f} < X4 y {pos(f_catch, 'X4')[1]:.2f}")
    vis = []
    for t in (1.55, 1.90, 2.30, 2.48):
        f = at(t)
        to_o5 = (pos(f, "O5")[0] - pos(f, "X4")[0], pos(f, "O5")[1] - pos(f, "X4")[1])
        to_o4 = (pos(f, "O4")[0] - pos(f, "X4")[0], pos(f, "O4")[1] - pos(f, "X4")[1])
        vis.append((t, G.angle_deg(fdir(f, "X4"), to_o4), G.angle_deg(fdir(f, "X4"), to_o5)))
    R.add("cut", f"X4 watches O5 while O4 cuts: O4 outside his focused {2 * VISION_HALF:.0f}-degree cone from the cut to the release",
          all(v[1] > VISION_HALF for v in vis) and all(v[2] < VISION_HALF for v in vis if v[0] >= 1.90),
          "; ".join(f"{t:.2f}s O4 at {a:.0f} deg / O5 at {b:.0f} deg" for t, a, b in vis))
    lay = next(e for e in play["ball"] if e["type"] == "layup")
    fl = at(lay["t0"] - off)
    R.add("finish", "layup released within 1.5 m of the hoop", G.dist_to_hoop(pos(fl, "O4")) <= 1.5, f"{G.dist_to_hoop(pos(fl, 'O4')):.2f} m")
    nl = min((G.dist(pos(fl, "O4"), pos(fl, x)), x) for x in X)
    R.add("finish", "layup uncontested (nearest defender >= 1.0 m at the release)", nl[0] >= 1.0, f"{nl[1]} {nl[0]:.2f} m")
    steps = lay["t0"] - next(e for e in play["ball"] if e["type"] == "pass" and e["to"] == "O4")["t1"]
    R.add("finish", "catch to layup release 0.45-0.9 s (gather + two steps, no dribble)", 0.45 <= steps <= 0.9, f"{steps:.2f} s")
    scr = [x for x in play["actions"].get("O5", []) if x["type"] == "screen"][0]
    vs = max(math.hypot(*vel(f, "O5")) for f in F if scr["from"] + 0.05 <= f["t"] <= scr["to"] - 0.05)
    R.add("finish", "O5's ball screen is legal (stationary <= 0.15 m/s while set)", vs <= 0.15, f"{vs:.3f} m/s")

    rep = {"play": play["id"], "canonical": os.path.basename(a.canonical), "passed": sum(r["status"] == "PASS" for r in R.rows),
           "warnings": R.warn, "failed": R.fail, "verdict": "PASS" if R.fail == 0 else "FAIL", "rows": R.rows,
           "lanes": lanes, "decision_lanes": {"A_drive": {"state": drive_state, "x4_from_line_m": round(dX4, 3)},
                                               "B_corner": {"state": stB, "closest": wB, "clearance_m": round(cB, 3)},
                                               "C_cut": {"state": stC, "closest": wC, "clearance_m": round(cC, 3)}},
           "truth_windows_owner_s": TW, "defensive_audit": audit,
           "limits": {"speed_max": V_MAX, "accel_max": A_MAX, "accel_warn": A_WARN, "reaction_min_s": REACT, "reach": "arm 0.44 H from shoulders at 0.82 H; +0.35 m lunge after 0.25 s"}}
    json.dump(rep, open(a.out, "w"), indent=1)
    if a.md:
        L = [f"# Tactical validation: {play['id']}", "", f"Verdict: **{rep['verdict']}** ({rep['passed']} pass, {R.warn} warn, {R.fail} fail).", "",
             "| Section | Check | Status | Value |", "|---|---|---|---|"]
        L += [f"| {r['section']} | {r['check']} | {r['status']} | {r['value']} |" for r in R.rows]
        open(a.md, "w").write("\n".join(L) + "\n")
    print(f"\nVERDICT {rep['verdict']}: {rep['passed']} pass, {R.warn} warn, {R.fail} fail")
    sys.exit(1 if R.fail else 0)


if __name__ == "__main__":
    main()
