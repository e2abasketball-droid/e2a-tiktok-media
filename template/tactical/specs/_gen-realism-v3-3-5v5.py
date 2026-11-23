#!/usr/bin/env python3
"""E2A Realism V3.3 (2026-11-22) — TEST fixture of the full 5v5 validation (brief V3.3 Gate 4), never a social episode.
A real E2A possession with all 10 players: the Chicago V3 UNDER -> THREE set (tactical/plays/chicago-v3-under-three.json,
pin-down into a dribble hand-off, X2 goes under, O2 rises up for three) UNCHANGED in geometry and relative timing,
shifted by SHIFT s and framed by two choreography extensions so the clip is a 10-18 s one-take:
  setup (0 - SHIFT):   O1 brings the ball up from half court with a live dribble to his spot (0, 9.3), X1 backpedals in
                       front of him, O2 sinks to the low wing, O4 to the elbow-wing, O3 to the corner, O5 to the weak
                       wing; each defender trails his man 0.2-0.4 s later and arrives in his stance
  set (SHIFT - SHIFT+5.0): chicago-v3-under-three, every track / ball event / action / mark + SHIFT
  post (SHIFT+5.0 - END): after the make O4 crashes the rim, X4 boxes him out, the others drift back / relax
The tactical claims of the source play are carried over (marks shifted), the setup and post phases add no claim.
"v33": "compile": every player's motion comes from the V3.3 event compiler (src/t3d/realism-v3-3/compile33.ts),
no per-player hand script.
  python3 tactical/specs/_gen-realism-v3-3-5v5.py -> tactical/specs/realism-v3-3-5v5.spec.json + tactical/plays/"""
import copy, json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
SRC = json.load(open(os.path.join(T, "tactical", "plays", "chicago-v3-under-three.json")))
SHIFT = 3.5
END = 11.0
R4 = lambda v: round(v, 4)

# setup: start spot, leave time, arrival time, lateral bow of the path (m, + = to the left of the travel direction)
SETUP = {
    "O1": ((0.6, 12.6), 0.25, 3.2, 0.25),
    "X1": ((0.35, 11.5), 0.5, 3.3, 0.0),
    "O2": ((-3.4, 7.6), 0.55, 3.0, -0.6),
    "X2": ((-3.0, 6.9), 0.85, 3.25, -0.4),
    "O4": ((-2.3, 9.6), 0.7, 3.1, 0.35),
    "X4": ((-1.9, 8.7), 1.0, 3.35, 0.25),
    "O3": ((3.9, 6.8), 0.4, 2.9, 0.5),
    "X3": ((3.3, 6.3), 0.7, 3.2, 0.35),
    "O5": ((2.8, 10.9), 0.6, 3.0, -0.3),
    "X5": ((2.4, 9.9), 0.9, 3.3, -0.2),
}
# post: (leave time after the set end - SHIFT - 5.0 ... ) target, leave, arrive (absolute)
SET_END = SHIFT + SRC["duration"]


def ease(u):
    return u * u * (3 - 2 * u)


def path(a, b, t0, t1, bow, dt=0.1):
    """eased path a -> b between t0 and t1 with a gentle bow; samples every dt (natural spline runs through them)"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    n = max(2, int(round((t1 - t0) / dt)))
    out = []
    for i in range(n + 1):
        u = i / n
        e = ease(u)
        w = 4 * e * (1 - e) * bow
        out.append([R4(t0 + (t1 - t0) * u), R4(a[0] + dx * e + nx * w), R4(a[1] + dy * e + ny * w)])
    return out


def build():
    play = copy.deepcopy(SRC)
    tracks = {}
    for pid, tr in SRC["tracks"].items():
        start, go, arr, bow = SETUP[pid]
        first = (tr[0][1], tr[0][2])
        pre = [[0.0, start[0], start[1]], [R4(go), start[0], start[1]]] + path(start, first, go, arr, bow)[1:]
        pre.append([SHIFT, first[0], first[1]])
        body = [[R4(w[0] + SHIFT), w[1], w[2]] for w in tr if w[0] + SHIFT > SHIFT + 1e-6]
        tracks[pid] = pre + body
    # X1 stays IN FRONT of the ball handler during the bring-up: his setup path is O1's path + a gap that closes from
    # 1.35 m to the set's 0.98 m only at the arrival (first V3.3 QA: a 0.82 m gap put O1's dribble into X1's thigh)
    o1 = tracks["O1"]
    g0, g1 = (-0.25, -1.35), (SRC["tracks"]["X1"][0][1] - SRC["tracks"]["O1"][0][1], SRC["tracks"]["X1"][0][2] - SRC["tracks"]["O1"][0][2])
    x1 = []
    for w in o1:
        if w[0] > SHIFT + 1e-6:
            break
        u = ease(min(1.0, max(0.0, (w[0] - 2.4) / (SHIFT - 2.4))))
        x1.append([w[0], R4(w[1] + g0[0] + (g1[0] - g0[0]) * u), R4(w[2] + g0[1] + (g1[1] - g0[1]) * u)])
    x1[-1] = [SHIFT, SRC["tracks"]["X1"][0][1], SRC["tracks"]["X1"][0][2]]
    tracks["X1"] = x1 + [w for w in tracks["X1"] if w[0] > SHIFT + 1e-6]
    # post phase (after the make; the source tracks end standing at SET_END)
    rimP = (0.0, 1.575)
    def post(pid, target, go, arr, bow=0.0):
        tr = tracks[pid]
        # the source track stands still at its last spot from its second-to-last key: cut the standing tail at `go`
        assert tr[-1][1:] == tr[-2][1:] and tr[-2][0] <= go + 1e-6, (pid, tr[-2:], go)
        while tr[-1][0] >= go - 1e-6:
            tr.pop()
        last = (tr[-1][1], tr[-1][2])
        tr.append([R4(go), last[0], last[1]])
        tr += path(last, target, go, arr, bow)[1:]
    post("O4", (-2.15, 2.95), SHIFT + 4.05, SHIFT + 5.4, 0.1)    # crash: starts as the shot goes up, held up behind X4
    post("X4", (-1.6, 2.5), SHIFT + 4.25, SHIFT + 5.3, 0.1)    # box-out: reacts 0.2 s later, gets between O4 and the rim
    post("O1", (-0.7, 9.5), SET_END + 0.2, SET_END + 1.6, 0.0)   # drifts back to the top for balance (away from O2)
    post("X1", (-1.5, 8.2), SET_END + 0.4, SET_END + 1.7, 0.0)
    post("O3", (5.4, 2.6), SET_END + 0.1, SET_END + 1.5, 0.0)
    post("X5", (2.6, 5.2), SET_END + 0.2, SET_END + 1.6, 0.0)
    for pid, tr in tracks.items():
        if tr[-1][0] < END:
            tr.append([END, tr[-1][1], tr[-1][2]])
    play["tracks"] = tracks
    # ball: the first hold (live dribble) starts at 0 instead of SHIFT; every other event + SHIFT
    ball = []
    for e in SRC["ball"]:
        e = copy.deepcopy(e)
        for k in ("from", "to", "t0", "t1"):
            if k in e and isinstance(e[k], (int, float)):
                e[k] = R4(e[k] + SHIFT)
        if "present" in e:
            for k in ("from", "peak", "hold", "to"):
                e["present"][k] = R4(e["present"][k] + SHIFT)
        ball.append(e)
    ball[0]["from"] = 0
    play["ball"] = ball
    # actions + SHIFT; setup actions (defenders in stance on their man, offence facing the ball), post actions
    acts = {}
    for pid, lst in SRC["actions"].items():
        acts[pid] = [dict(a, **{"from": R4(a["from"] + SHIFT), "to": R4(a["to"] + SHIFT)}) for a in lst]
    guards = {p["id"]: p.get("guards") for p in SRC["players"]}
    for pid in tracks:
        if pid.startswith("X"):
            acts.setdefault(pid, []).insert(0, {"type": "stance", "from": 0.0, "to": SHIFT, "face": guards.get(pid) or "ball"})
        elif pid != "O1":
            acts.setdefault(pid, []).insert(0, {"type": "face", "from": 0.0, "to": SHIFT, "face": "ball"})
    # the source's last action of each player is stretched to the new end; post: X4 faces the rim side box-out (back to O4)
    for pid, lst in acts.items():
        if lst and abs(lst[-1]["to"] - SET_END) < 1e-6:
            lst[-1]["to"] = END
    acts["X4"] = [a for a in acts["X4"] if a["from"] < SHIFT + 4.25] + [{"type": "stance", "from": R4(SHIFT + 4.25), "to": END, "face": "ball"}]  # box-out: back to O4, eyes on the ball
    for a in acts["X4"]:
        if a["to"] > SHIFT + 4.25 and a["from"] < SHIFT + 4.25:
            a["to"] = R4(SHIFT + 4.25)
    acts["O4"] = [a for a in acts["O4"] if a["from"] < SHIFT + 4.05]
    for a in acts["O4"]:
        if a["to"] > SHIFT + 4.05:
            a["to"] = R4(SHIFT + 4.05)
    acts["O4"].append({"type": "face", "from": R4(SHIFT + 4.05), "to": END, "face": "ball"})  # crash: eyes on the ball
    play["actions"] = acts
    play["marks"] = {k: R4(v + SHIFT) for k, v in SRC["marks"].items()}
    play["marks"].update({"setup": 0.0, "setEnd": SET_END, "end": END})
    play.pop("branch", None)
    play.pop("sclock", None)
    play.update({
        "id": "realism-v3-3-5v5",
        "title": "Realism V3.3 5v5 validation (TEST fixture): Chicago V3 UNDER -> THREE with setup + crash / box-out",
        "duration": END, "test": True, "v33": "compile", "concept": "realism-v3-3-test",
        "source": "E2A test fixture built from the original E2A possession chicago-v3-under-three (" + SRC["concept"] + "), geometry unchanged, + setup / post choreography extensions (brief V3.3 Gate 4)",
        "v33notes": {"shift": SHIFT, "setEnd": SET_END, "extensions": ["setup 0-%.1f s: ball brought up, players to their spots" % SHIFT, "post %.2f-%.1f s: O4 crash, X4 box-out, others drift" % (SET_END, END)]},
    })
    return play


if __name__ == "__main__":
    s = build()
    json.dump(s, open(os.path.join(D, "realism-v3-3-5v5.spec.json"), "w"), indent=1)
    json.dump(s, open(os.path.join(T, "tactical", "plays", "realism-v3-3-5v5.json"), "w"), indent=1)
    print("built", s["id"], "duration", s["duration"], "players", len(s["tracks"]))
