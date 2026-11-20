#!/usr/bin/env python3
"""Pistol Fake Handoff: keep | give side-by-side test (brief sec. 5 "test mas importante" + sec. 7.3).
Same camera, same play frames (S030 -> S066, before the decision point to the first step after it), 0.30x, NO text or
graphics; plus a 'hands' version (close 3/4) with the engine's diagnostic phase box (ball phase, owner, play time S) and
the edit time E burnt in by ffmpeg.
  python3 tactical/episodes/_cmp-pfh.py      -> tactical/episodes/pfh-cmp-*.json + words, out/pfh/pfh-cmp-*.props.json
  render frames 0-119 of each, then tactical/episodes/_cmp-pfh.sh <deliver_dir>"""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, D)
from importlib import import_module  # noqa: E402
g = import_module("_gen-pfh")
S = g.S
DUR = 4.0
VAR = {"keep": ("A", "keep"), "give": ("B", "give")}
for br, (play, branch) in VAR.items():
    for kind, cam, scr in (("clean", g.FAKE, []), ("hands", g.HOOK, [{"type": "debugPhase", "label": br.upper(), "from": 0, "to": DUR}])):
        src = json.load(open(os.path.join(D, "pfh-a.json")))
        ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw", "gapFill", "music")}
        eid = f"pfh-cmp-{br}-{kind}"
        ep.update({"id": eid, "title": f"Pistol Fake Handoff test {br} {kind}", "branches": {"keep": "A", "give": "B"}, "env": "academy",
                   "pinV2": True, "autoSfx": False, "subtitleHide": [[0, 999]],
                   "shots": [{"id": "t", "name": f"{br} S030->S066 0.30x", "at": 0, "play": play, "branch": branch,
                              "remap": [[0, S(30)], [DUR, S(66)]], "camera": [{"at": 0, "rig": cam}], "ov3": [], "screen": scr}]})
        json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1)
        json.dump(json.load(open(os.path.join(D, "pfh-a.words.json"))), open(os.path.join(D, f"{eid}.words.json"), "w"))
        print(eid)
