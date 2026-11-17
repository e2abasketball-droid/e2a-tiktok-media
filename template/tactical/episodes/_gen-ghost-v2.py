#!/usr/bin/env python3
"""GHOST SCREEN V2 (owner brief 2026-11-15 19:27Z): 9:16, English, ~28 s. Base fields (voice, gaps, plays).
Shots: _gen-ghost-v2-shots.py once scripts/tactical-voice.py wrote the real word timings."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "ghost-screen-v2",
 "title": "GHOST SCREEN V2: who fakes, who reacts, what opens",
 "fps": 30,
 "voiceRaw": "tactical/ghost2/voice-raw.mp3",
 "wordsRaw": "ghost-screen-v2.words-raw.json",
 "voice": "tactical/ghost2/voice.wav",
 "voiceMix": "tactical/ghost2/voice.mix.wav",
 "preroll": 0.1,
 "tail": 1.45,
 "gaps": [
  {"after": "hit the pop.", "sec": 1.3, "why": "the release and the late close-out, then the cut back to the same start"},
  {"after": "STAYS WITH HIM.", "sec": 0.74, "why": "X2 rides the pop; the eye moves to X1 before he jumps"},
  {"after": "and drive.", "sec": 0.44, "why": "the layup and the net before the question"}],
 "plays": {"A": "ghost2-a-three", "B": "ghost2-b-reject"},
 "pinV2": True,
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "ghost-screen-v2.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
