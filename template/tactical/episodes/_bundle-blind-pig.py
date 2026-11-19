#!/usr/bin/env python3
"""Render props for Blind Pig: {"episode": ep + plays inlined + words}.
  python3 tactical/episodes/_bundle-blind-pig.py out_dir [episode_id ...]"""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D))
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for eid in (sys.argv[2:] or ["blind-pig-main"]):
    ep = json.load(open(os.path.join(D, f"{eid}.json")))
    ep["words"] = json.load(open(os.path.join(D, f"{eid}.words.json")))
    ep["plays"] = {k: json.load(open(os.path.join(T, "tactical", "plays", f"{v}.json"))) for k, v in ep["plays"].items()}
    json.dump({"episode": ep}, open(os.path.join(out, f"{eid}.props.json"), "w"))
    print(os.path.join(out, f"{eid}.props.json"))
