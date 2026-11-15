#!/usr/bin/env python3
"""DOUBLE DRAG: roll or pop? (owner brief 2026-11-15 21:45Z): 9:16, English, ~23 s. Base fields (voice, gaps, plays).
Shots: _gen-ddrag-shots.py once scripts/tactical-voice.py wrote the real word timings."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "double-drag", "title": "DOUBLE DRAG: roll or pop?", "fps": 30,
 "voiceRaw": "tactical/ddrag/voice-raw.mp3", "wordsRaw": "double-drag.words-raw.json",
 "voice": "tactical/ddrag/voice.wav", "voiceMix": "tactical/ddrag/voice.mix.wav",
 "preroll": 0.1, "tail": 3.2,
 "gaps": [
  {"after": "is OPEN.", "sec": 0.78, "why": "the three to the net, then the cut to the overhead replay"},
  {"after": "has to help.", "sec": 0.72, "why": "the pass to the pop, then the cut to the same start for B"},
  {"after": "for the roll.", "sec": 4.08, "why": "the inside pass, the catch and the finish with court sound only"}],
 "plays": {"A": "ddrag-a-pop", "B": "ddrag-b-roll"}, "pinV2": True, "shots": [],
}
json.dump(ep, open(os.path.join(D, "double-drag.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
