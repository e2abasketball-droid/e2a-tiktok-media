#!/usr/bin/env python3
"""VEER ACTION (owner brief 2026-11-16 03:27Z): 9:16, English, 32-34 s. Base fields (voice, gaps, plays).
Shots: _gen-veer-shots.py once scripts/tactical-voice.py wrote the real word timings."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "veer-action",
 "title": "VEER ACTION: who got him open, where does the pass go",
 "fps": 30,
 "voiceRaw": "tactical/veer/voice-raw.wav",
 "wordsRaw": "veer-action.words-raw.json",
 "voice": "tactical/veer/voice.wav",
 "voiceMix": "tactical/veer/voice.mix.wav",
 "preroll": 0.12,
 "tail": 1.6,
 "gaps": [
  {"after": "open?", "sec": 0.62, "why": "the catch lands, cut back to the start"},
  {"after": "after the pick.", "sec": 1.05, "why": "the big walks up and sets the ball screen"},
  {"after": "steps in to help.", "sec": 1.15, "why": "the help step lands, the big starts to veer"},
  {"after": "That's the Veer.", "sec": 2.55, "why": "pass, catch and the three in the same frame"},
  {"after": "Where's the pass going?", "sec": 1.15, "why": "the viewer anticipates the pass"},
  {"after": "in stride.", "sec": 2.6, "why": "layup and net"},
  {"after": "Kick it out.", "sec": 1.2, "why": "replay A lands before replay B"},
  {"after": "Hit the curl.", "sec": 1.4, "why": "replay B lands"}],
 "plays": {"A": "veer-a-kick", "B": "veer-b-curl"},
 "pinV2": True,
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "veer-action.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
