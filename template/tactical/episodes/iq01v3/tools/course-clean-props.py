#!/usr/bin/env python3
"""Course-ready clean props for the E2A Film Room (V3, 2026-11-27): same edit, same voice, same 3D teaching marks
(A/B/C letters, chips, spotlights, lanes, rings), but NO burned-in subtitles (the course player shows the SRT),
NO big hook/section titles and NO social countdown (the course asks the question itself, as an interactive pause).
  python3 course-clean-props.py props-A.json props-course.json"""
import json, sys
DROP = {"title", "countdown"}
p = json.load(open(sys.argv[1]))
ep = p["episode"]
ep["subtitleHide"] = [[0, 999]]
for s in ep["shots"]:
    s["screen"] = [x for x in s.get("screen", []) if x.get("type") not in DROP]
ep["id"] = ep["id"] + "-course"
json.dump(p, open(sys.argv[2], "w"))
print("clean props:", sys.argv[2], "shots", len(ep["shots"]))
