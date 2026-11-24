#!/usr/bin/env python3
"""NBA vs EuroLeague V2 (2026-11-24): empty-court plays for the scoreboard section (before the tip: no live ball on
court, so the game clocks can honestly sit at Q1 12:00 / 10:00). One hidden ball holder 'R' stands far behind the camera
(the shot hides him); nothing else on the floor. Same court identities as nbaeu-* (NBA Rule 1 / FIBA lines).
  python3 tactical/specs/_gen-nbaeu-v2.py -> tactical/plays/nbaeu-empty-{nba,el}.json"""
import json, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
LOOK = {"nba": {"paint": "rgba(28,62,140,0.9)", "word": "NBA", "ink": "rgba(255,255,255,0.88)"},
        "fiba": {"paint": "rgba(168,78,22,0.88)", "word": "EUROLEAGUE", "ink": "rgba(255,255,255,0.88)"}}
for lg, rules in (("nba", "nba"), ("el", "fiba")):
    dur = 8.0
    p = {"id": f"nbaeu-empty-{lg}", "title": f"Empty {lg.upper()} court before the tip (scoreboard background)", "branch": {"group": "nbaeu"},
         "duration": dur, "concept": f"nbaeu-empty-{lg}", "source": "original E2A background (no action)", "v33": "compile", "realism": 3,
         "courtRules": rules, "courtLook": LOOK[rules],
         "players": [{"id": "R", "team": "O", "role": "hidden ball holder far behind the camera"}],
         "tracks": {"R": [[0.0, 0.0, 34.0], [dur, 0.0, 34.0]]},
         "ball": [{"type": "hold", "player": "R", "from": 0, "to": dur}], "actions": {"R": []},
         "screens": [], "marks": {}, "claims": [], "notes": ["Shots must hide R."]}
    json.dump(p, open(os.path.join(T, "tactical", "plays", f"nbaeu-empty-{lg}.json"), "w"), indent=1)
print("ok")
