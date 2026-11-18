#!/usr/bin/env python3
"""Render props for the Break the 3-2 versions: {"episode": ep + plays inlined + the shared master words}.
  python3 tactical/episodes/_bundle-zone32.py out_dir"""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D))
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for eid in ("zone32-main", "zone32-trial"):
    ep = json.load(open(os.path.join(D, f"{eid}.json")))
    ep["words"] = json.load(open(os.path.join(D, f"{eid}.words.json")))
    ep["plays"] = {k: json.load(open(os.path.join(T, "tactical", "plays", f"{v}.json"))) for k, v in ep["plays"].items()}
    json.dump({"episode": ep}, open(os.path.join(out, f"{eid}.props.json"), "w"))
    print(os.path.join(out, f"{eid}.props.json"))
