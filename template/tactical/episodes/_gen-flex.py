#!/usr/bin/env python3
"""FLEX ACTION: screen the screener (owner brief 2026-11-15 21:45Z): 9:16, English, ~25 s. Base fields (voice, gaps, plays).
Shots: _gen-flex-shots.py once scripts/tactical-voice.py wrote the real word timings."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "flex-action", "title": "FLEX ACTION: screen the screener", "fps": 30,
 "voiceRaw": "tactical/flex/voice-raw.mp3", "wordsRaw": "flex.words-raw.json",
 "voice": "tactical/flex/voice.wav", "voiceMix": "tactical/flex/voice.mix.wav",
 "preroll": 0.1, "tail": 3.3,
 "gaps": [
  {"after": "first screener.", "sec": 1.9, "why": "the flex cut and X5's help step, court sound only"},
  {"after": "gets the shot.", "sec": 1.46, "why": "the release, the cut to the rim, the net"},
  {"after": "toward the rim.", "sec": 0.9, "why": "back to O1 going down"},
  {"after": "at the elbow.", "sec": 1.9, "why": "the elbow shot to the net, then the cut back to the same start"},
  {"after": "at the rim.", "sec": 1.0, "why": "the layup and the net before the question"}],
 "plays": {"A": "flex-a-elbow", "B": "flex-b-rim"}, "pinV2": True, "shots": [],
}
json.dump(ep, open(os.path.join(D, "flex-action.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
