#!/usr/bin/env python3
"""E2A Realism V3.2 (2026-11-22) — TEST fixture of the Legacy / V3.1 / V3.2 comparison (A/B/C), never a social episode.
O1's track, ball events and engine actions are IDENTICAL to realism-v3-1-onetake (same choreography, same event times:
run start 1.5 s, plant 3.28 s, catch 4.933 s, bounce 6.13-6.73 s, release 8.20 s, landing ~8.56 s). Only the passer O2
moves differently AFTER his pass: in V3.1's fixture he cut to the right block and crossed between the follow camera and
O1 at ~6.75 s (owner review); here he drifts back and to his right, away from the camera line (checked per frame by
scripts/qc-realism-v32.mts, visibility section).
  python3 tactical/specs/_gen-realism-v3-2-abc.py -> tactical/specs/realism-v3-2-abc.spec.json + tactical/plays/"""
import importlib.util, json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
_s = importlib.util.spec_from_file_location("ot", os.path.join(D, "_gen-realism-v3-1-onetake.py"))
ot = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ot)
runk, cat, add = ot.runk, ot.cat, ot.add
O2P, DUR = ot.O2P, ot.DUR
O2END = (1.9, 9.9)  # back and to his right: behind O1's catch spot, off the 3/4 camera line
O2 = cat(runk([(0, O2P, 0.0), (180, O2P, 0.0)]), runk([(180, O2P, 0.0), (204, add(O2P, (0.85, 0.53), 0.9), 1.6), (228, O2END, 0.0)]), runk([(228, O2END, 0.0), (ot.DUR, O2END, 0.0)]))


def spec():
    s = ot.spec()
    s["id"] = "realism-v3-2-abc"
    s["title"] = "Realism V3.2 A/B/C fixture: the V3.1 one-take (same O1 track and ball events), passer drifts away from the camera line"
    s["concept"] = "realism-v3-2-test"
    s["source"] = "E2A synthetic test fixture (brief Realism V3.2 sec. 10), derived from realism-v3-1-onetake; no real play copied"
    s["players"][1]["role"] = "Passer at the top of the key; after the pass drifts back-right (never between the camera and O1)"
    s["tracks"]["O2"] = ot.track(O2)
    s["v31clip"] = {"O1": "realism-v3-1-onetake:O1"}
    s["v32clip"] = {"O1": "realism-v3-1-onetake:O1"}
    return s


if __name__ == "__main__":
    s = spec()
    json.dump(s, open(os.path.join(D, "realism-v3-2-abc.spec.json"), "w"), indent=1)
    json.dump(s, open(os.path.join(T, "tactical", "plays", "realism-v3-2-abc.json"), "w"), indent=1)
    print("built", s["id"], "O2 end", O2END)
