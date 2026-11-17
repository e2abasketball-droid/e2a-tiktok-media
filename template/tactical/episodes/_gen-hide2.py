#!/usr/bin/env python3
"""HIDE IN GAMES V2: narration gaps (owner brief 2026-11-17 19:28Z). One Deuce eleven_v4 take (692 credits),
Scribe word timings (0 credits). Writes tactical/episodes/hide2.json; then scripts/tactical-voice.py builds the track."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
G = [("want the ball.", 1.2, "reaction: the arm comes down"),
     ("without thinking.", 1.1, "practice: catch, square up"),
     ("game starts.", 2.2, "match cut on the rise, the shot leaves"),
     ("hits the rim.", 3.8, "no narration around the impact and the first reaction; rebound, the game goes on"),
     ("thinking is,", 0.7, "half a hand comes up and goes back"),
     ("miss again?", 1.3, "short pause before the story resumes"),
     ("hands drop.", 0.45, "behind the passer"),
     ("somewhere else.", 2.2, "the pass goes to O3"),
     ("one job.", 0.7, "pause between actions"),
     ("Breathe out.", 1.6, "exhale, short tap on the jersey"),
     ("next spot.", 2.0, "eyes back on the passer"),
     ("can see you.", 1.2, "plant and slide, the lane opens"),
     ("your hands.", 0.8, "hands up"),
     ("Call for it.", 3.3, "the pass and the two-hand catch"),
     ("still nervous.", 0.5, "the ask from the other angle"),
     ("it anyway.", 0.8, "back to the catch"),
     ("he shoots.", 2.4, "ball in flight")]
ep = {"id": "hide2", "title": "Hide in games V2", "fps": 30, "voiceRaw": "tactical/hide2/voice-raw.mp3", "wordsRaw": "hide2.words-raw.json",
      "voice": "tactical/hide2/voice.wav", "voiceMix": "tactical/hide2/voice.mix.wav", "preroll": 0.0, "tail": 1.6,
      "gaps": [{"after": a, "sec": s, "why": w} for a, s, w in G],
      "plays": {}, "shots": []}
json.dump(ep, open(os.path.join(D, "hide2.json"), "w"), indent=1)
print("ok")
