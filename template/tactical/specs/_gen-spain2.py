#!/usr/bin/env python3
"""Spain Pick & Roll 2.0 (owner brief 2026-11-19): the SAME two reads as spain-a-roll / spain-b-pop (same spots, legs,
ball and claims), plus the `roll` action after O5's ball screen so the default player package drives O5 with the
validated screen-and-roll clip (CLIP_LIBRARY, 5452m). The screen face is a fixed angle (0.7 rad, chest toward X1's
path over the top) so the clip's turn fits the play (added turn <= 35 deg); facing X1's live spot needs 72 deg.
  python3 tactical/specs/_gen-spain2.py && node --experimental-strip-types scripts/build-play.mts tactical/specs/spain2-a-roll.spec.json tactical/plays/spain2-a-roll.json (same for b)"""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
for src, dst, roll_to, title in [("spain-a-roll", "spain2-a-roll", 3.0, "Spain PnR 2.0, read A: X2 stays attached, the roller is free"),
                                 ("spain-b-pop", "spain2-b-pop", 2.6, "Spain PnR 2.0, read B: X2 steps up to stop the roller, O2 pops")]:
    s = json.load(open(os.path.join(D, f"{src}.spec.json")))
    s["id"], s["title"] = dst, title
    acts = []
    for a in s["actions"]["O5"]:
        if a["type"] == "screen":
            acts += [{**a, "face": 0.7}, {"type": "roll", "from": 1.42, "to": roll_to, "face": "O1"}]
        else:
            acts.append(a)
    s["actions"]["O5"] = acts
    json.dump(s, open(os.path.join(D, f"{dst}.spec.json"), "w"), indent=1, ensure_ascii=False)
    print(dst)
