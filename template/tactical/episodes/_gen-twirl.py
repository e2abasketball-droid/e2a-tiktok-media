#!/usr/bin/env python3
"""TWIRL ACTION (owner brief 2026-11-16 04:43Z): 9:16, English, 32-34 s. Base fields (voice, gaps, plays).
Shots: _gen-twirl-shots.py once scripts/tactical-voice.py wrote the real word timings."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "twirl-action",
 "title": "TWIRL ACTION: the first screener gets the shot",
 "fps": 30,
 "voiceRaw": "tactical/twirl/voice-raw.wav",
 "wordsRaw": "twirl-action.words-raw.json",
 "voice": "tactical/twirl/voice.wav",
 "voiceMix": "tactical/twirl/voice.mix.wav",
 "preroll": 0.12,
 "tail": 1.4,
 "gaps": [
  {"after": "wrong shooter.", "sec": 0.55, "why": "cut back to the formation"},
  {"after": "the first screener.", "sec": 0.5, "why": "the cutter starts"},
  {"after": "the first screen.", "sec": 0.6, "why": "the curl turns"},
  {"after": "defender inside.", "sec": 0.6, "why": "the help step lands"},
  {"after": "That's the Twirl.", "sec": 1.8, "why": "pass, catch and the three"},
  {"after": "Who gets it?", "sec": 1.05, "why": "let the movement answer first"},
  {"after": "on the move.", "sec": 1.7, "why": "catch on the move, layup"},
  {"after": "Hit the shooter.", "sec": 0.75, "why": "replay A lands"},
  {"after": "Hit the cutter.", "sec": 0.9, "why": "replay B lands"}],
 "plays": {"A": "twirl-a-three", "B": "twirl-b-curl"},
 "pinV2": True,
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "twirl-action.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
