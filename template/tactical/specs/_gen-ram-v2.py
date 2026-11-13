#!/usr/bin/env python3
"""RAM SCREEN V2 (2026-11-13): the V1 possessions re-animated for weight and readability.
Same alignment and the same ram screen in A and B; changes vs V1:
- O4 arrives a beat earlier, decelerates and plants (screen from 1.05) before X5 gets there;
- X5 absorbs the screen ('bump' 1.5–1.85: recoil, forearms up) and goes AROUND O4 on the inside -> the half step;
- O5 loads (automatic anticipation in the rig), runs off the ram and PLANTS the ball screen at 2.9 (before O1 uses it at 3.2);
- O1: brake + 'gather' before the pull-up (A); reads X5's rise and passes into the gap (B);
- O5 short roll (B): hands open to the passer (catchReady facing O1) and body turned to the lane;
- help defenders face the ball ('ball'), X2 is the late help in B, X3 stays home on the shooter.
Writes ram-v2-a-drop.spec.json and ram-v2-b-blitz.spec.json (build with scripts/build-play.mts)."""
import json, os, subprocess, copy
D = os.path.dirname(os.path.abspath(__file__))
subprocess.run(["python3", os.path.join(D, "_gen-ram.py")], check=True, capture_output=True)
for kind in ("a-drop", "b-blitz"):
    s = json.load(open(os.path.join(D, f"ram-{kind}.spec.json")))
    s["id"] = f"ram-v2-{kind}"
    s["squareUp"] = True   # receivers face the passer while the ball travels (play.ts, opt-in per play)
    L, A = s["legs"], s["actions"]
    # O4: earlier, decisive arrival, then the plant
    L["O4"][0] = {"at": 0.05, "to": [-2.15, 4.35], "dur": 1.0}
    A["O4"] = [{"type": "screen", "from": 1.05, "to": 2.1, "face": "X5"}]
    # X5: steps into O4, absorbs, then goes around on the inside (loses the half step)
    L["X5"][0] = {"at": 1.1, "to": [-1.6, 3.85], "dur": 0.45}
    if kind == "a-drop":
        L["X5"][1] = {"at": 1.85, "via": [[-1.25, 4.85], [-0.55, 6.1]], "to": [0.0, 7.4], "dur": 1.3}
    else:
        L["X5"][1] = {"at": 1.85, "via": [[-1.25, 4.85], [-0.55, 6.1], [0.0, 7.6]], "to": [-0.5, 10.35], "dur": 2.0}
    A["X5"] = [{"type": "stance", "from": 0, "to": 1.1, "face": "O5"}, {"type": "bump", "from": 1.5, "to": 1.85, "face": "O4"}]
    # O5: off the ram with the head start, ball screen planted at 2.9
    L["O5"][0] = {"at": 0.8, "via": [[-3.2, 5.0], [-2.3, 7.4]], "to": [0.85, 8.95], "dur": 2.1}
    # help side reads the ball
    for d, g in (("X2", "O2"), ("X3", "O3")):
        A[d] = [{"type": "stance", "from": 0, "to": 6.6, "face": "ball"}]
    A["X4"] = [{"type": "stance", "from": 0, "to": 1.0, "face": "O4"}, {"type": "stance", "from": 1.0, "to": 6.6, "face": "ball"}]
    if kind == "a-drop":
        L["X5"] = L["X5"][:2] + [{"at": 3.15, "to": [-0.55, 5.25], "dur": 1.35}]          # contain steps back, chest to the ball
        A["X5"] += [{"type": "stance", "from": 2.9, "to": 5.2, "face": "O1"}]
        A["O5"] = [{"type": "screen", "from": 2.85, "to": 3.95, "face": "X1"}]
        A["O1"] = [{"type": "gather", "from": 4.08, "to": 4.42}, {"type": "celebrate", "from": 5.75, "to": 6.4}]
    else:
        A["X5"] += [{"type": "blitz", "from": 3.25, "to": 4.15, "face": "O1"}]
        A["O5"] = [{"type": "screen", "from": 2.85, "to": 3.4, "face": "X1"},
                   {"type": "catchReady", "from": 3.6, "to": 4.4, "face": "O1"},
                   {"type": "celebrate", "from": 5.95, "to": 6.45}]
        A["X2"] = [{"type": "stance", "from": 0, "to": 4.3, "face": "ball"}, {"type": "stance", "from": 4.3, "to": 6.5, "face": "O5"}]
    s["notes"] = s.get("notes", []) + ["V2: O4 plants first; X5 absorbs the screen and goes around it (half step lost); O5 loads and plants the ball screen."]
    json.dump(s, open(os.path.join(D, f"ram-v2-{kind}.spec.json"), "w"), indent=1)
print("ok")
