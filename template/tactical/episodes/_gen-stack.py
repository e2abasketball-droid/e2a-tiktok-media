#!/usr/bin/env python3
"""STACK PICK-AND-ROLL (owner choice 2026-11-16 11:40Z): same method as the Spain pick-and-roll reel (hook, setup, case A,
case B, takeaway, CTA). Base fields (voice, gaps, plays). Shots: _gen-stack-shots.py once tactical-voice.py wrote the words."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "stack-pick-and-roll",
 "title": "The Stack Pick-and-Roll: Two Threats",
 "fps": 30,
 "voiceRaw": "tactical/stack/voice-raw.mp3",
 "wordsRaw": "stack-pick-and-roll.words-raw.json",
 "voice": "tactical/stack/voice.wav",
 "voiceMix": "tactical/stack/voice.mix.wav",
 "preroll": 0.12,
 "tail": 1.4,
 "gaps": [
  {"after": "Two threats.", "sec": 0.7, "why": "hook titles land"},
  {"after": "right behind the big.", "sec": 1.0, "why": "screen set, the shooter lifts out of the stack"},
  {"after": "nobody covers the shooter.", "sec": 0.9, "why": "freeze: the shooter is alone"},
  {"after": "Open three.", "sec": 1.8, "why": "ball flight to the swish + OPEN THREE"},
  {"after": "Easy two at the rim.", "sec": 1.5, "why": "layup lands + EASY TWO"},
  {"after": "give something up.", "sec": 1.0, "why": "title holds before the CTA"}],
 "plays": {"A": "stack-a-three", "B": "stack-b-roll"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "stack-pick-and-roll.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
