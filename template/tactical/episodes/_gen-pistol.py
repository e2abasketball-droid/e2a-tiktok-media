#!/usr/bin/env python3
"""PISTOL (21) (owner choice 2026-11-16 14:42Z): Spain pick-and-roll method. Base fields (voice, gaps, plays).
Shots: _gen-pistol-shots.py once tactical-voice.py wrote the words."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "pistol",
 "title": "The Pistol: Hand-off into a Ball Screen",
 "fps": 30,
 "voiceRaw": "tactical/pistol/voice-raw.mp3",
 "wordsRaw": "pistol.words-raw.json",
 "voice": "tactical/pistol/voice.wav",
 "voiceMix": "tactical/pistol/voice.mix.wav",
 "preroll": 0.12,
 "tail": 1.4,
 "gaps": [
  {"after": "One screen.", "sec": 0.7, "why": "hook titles land"},
  {"after": "ball screen right away.", "sec": 1.0, "why": "hand-off and screen in the same breath"},
  {"after": "stops behind it.", "sec": 0.5, "why": "he rises"},
  {"after": "Pull-up three.", "sec": 1.8, "why": "ball flight to the swish + OPEN THREE"},
  {"after": "has to step up.", "sec": 0.8, "why": "freeze: the roller is alone"},
  {"after": "Easy two at the rim.", "sec": 1.5, "why": "layup lands + EASY TWO"},
  {"after": "one second apart.", "sec": 0.5, "why": "title lands"},
  {"after": "give something up.", "sec": 1.0, "why": "title holds before the CTA"}],
 "plays": {"A": "pistol-a-under", "B": "pistol-b-over"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "pistol.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
