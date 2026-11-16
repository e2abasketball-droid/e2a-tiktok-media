#!/usr/bin/env python3
"""SHORT ROLL 4-ON-3 (owner 2026-11-16 14:41Z "otro vídeo parecido"; recommended option): Spain pick-and-roll method.
Base fields (voice, gaps, plays). Shots: _gen-short-roll-shots.py once tactical-voice.py wrote the words."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "short-roll",
 "title": "The Short Roll: Four on Three",
 "fps": 30,
 "voiceRaw": "tactical/shortroll/voice-raw.mp3",
 "wordsRaw": "short-roll.words-raw.json",
 "voice": "tactical/shortroll/voice.wav",
 "voiceMix": "tactical/shortroll/voice.mix.wav",
 "preroll": 0.12,
 "tail": 1.4,
 "gaps": [
  {"after": "Two on the ball.", "sec": 0.7, "why": "hook titles land"},
  {"after": "four on three.", "sec": 1.0, "why": "the big turns: 4 ON 3 lands"},
  {"after": "the corner is empty.", "sec": 0.9, "why": "freeze: the corner shooter is alone"},
  {"after": "Open three.", "sec": 1.8, "why": "ball flight to the swish + OPEN THREE"},
  {"after": "Easy two.", "sec": 1.5, "why": "layup lands + EASY TWO"},
  {"after": "give something up.", "sec": 1.0, "why": "title holds before the CTA"}],
 "plays": {"A": "sr-a-corner", "B": "sr-b-rim"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "short-roll.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
