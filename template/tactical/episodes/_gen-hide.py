#!/usr/bin/env python3
"""HIDE IN GAMES: narration gaps (owner brief 2026-11-17 17:09Z). One Deuce eleven_v4 take (456 credits),
Scribe word timings (0 credits). Writes tactical/episodes/hide.json; then scripts/tactical-voice.py builds the track."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
G = [("drop in games?", 1.2, "match cut lands, hands drop"),
     ("messing up,", 0.32, "eyes follow the ball"),
     ("teammate a target.", 2.6, "passer's view: #8 hidden, the ball goes the other way"),
     ("One.", 0.7, "the shot hits the rim"),
     ("a miss,", 0.45, "ball off the rim"),
     ("breathe out.", 0.9, "shoulders drop on the exhale"),
     ("your jersey.", 0.55, "1 RESET on the tap"),
     ("Get back.", 1.4, "turns and runs back"),
     ("Two.", 0.45, "2 SHOW A TARGET"),
     ("yourself a target.", 0.6, "first offer"),
     ("and call for it.", 3.4, "offers 2 and 3, 3/3, full catch"),
     ("for it. Three.", 0.45, "3 ASK AGAIN"),
     ("an open shot?", 0.9, "the miss again"),
     ("next possession,", 0.25, "back to the hook framing"),
     ("for it again.", 2.8, "hands up, catch at the chest")]
ep = {"id": "hide", "title": "Hide in games", "fps": 30, "voiceRaw": "tactical/hide/voice-raw.mp3", "wordsRaw": "hide.words-raw.json",
      "voice": "tactical/hide/voice.wav", "voiceMix": "tactical/hide/voice.mix.wav", "preroll": 0.12, "tail": 1.8,
      "gaps": [{"after": a, "sec": s, "why": w} for a, s, w in G],
      "plays": {}, "shots": []}
json.dump(ep, open(os.path.join(D, "hide.json"), "w"), indent=1)
print("ok")
