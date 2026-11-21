#!/usr/bin/env python3
"""BLOB camera / pose probe: one play frame per shot from one camera, 1 render frame each, no overlays (brief 08.4
frame-first design: stills before the reel). python3 tactical/episodes/_probe-blob.py probes.json -> blob-probe.json"""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
probes = json.load(open(sys.argv[1]))  # [{"id", "play": "A"|"B", "t": game s, "cam": orbit rig}]
src = json.load(open(os.path.join(D, "blob-voice.json")))
ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw", "gapFill")}
ep.update({"id": "blob-probe", "title": "BLOB probe", "branches": {"a": "A", "b": "B"}, "env": sys.argv[2] if len(sys.argv) > 2 else "academy", "pinV2": True,
           "autoSfx": False, "subtitleHide": [[0, 999]], "tail": 0.0})
ep["shots"] = [{"id": p["id"], "at": round(i / 30 - (0.0005 if i else 0), 4), "play": p["play"], "branch": "a" if p["play"] == "A" else "b",
                "remap": [[0, p["t"]], [1 / 30, p["t"]]], "camera": [{"at": 0, "rig": p["cam"]}], "ov3": p.get("ov3", []),
                "screen": []} for i, p in enumerate(probes)]
n = len(probes)
ep["words"] = []
json.dump(ep, open(os.path.join(D, "blob-probe.json"), "w"), indent=1)
json.dump([{"text": "x", "start": 0, "end": round(n / 30 - 0.001, 4)}], open(os.path.join(D, "blob-probe.words.json"), "w"))
print(n, "probe frames")
