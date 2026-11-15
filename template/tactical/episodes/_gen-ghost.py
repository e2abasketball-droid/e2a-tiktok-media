#!/usr/bin/env python3
"""GHOST SCREEN (owner brief 2026-11-15 17:22Z), 9:16, English, 33 s, built on the Stagger premium look.
Base fields (voice, gaps, plays). Shots: _gen-ghost-shots.py once scripts/tactical-voice.py wrote the real word timings."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "ghost-screen",
 "title": "GHOST SCREEN: two defenders, two outcomes",
 "fps": 30,
 "voiceRaw": "tactical/ghost/voice-raw.mp3",
 "wordsRaw": "ghost-screen.words-raw.json",
 "voice": "tactical/ghost/voice.wav",
 "voiceMix": "tactical/ghost/voice.mix.wav",
 "preroll": 0.12,
 "tail": 3.0,
 "gaps": [
  {"after": "either one.", "sec": 3.2, "why": "0:03.3-0:06: the pass, the catch and the three to the net, no voice"},
  {"after": "HIS FEET.", "sec": 2.4, "why": "the slow motion on the plant foot, back to real speed on the pop"},
  {"after": "hit the shooter.", "sec": 1.2, "why": "the release and X1 closing out late"},
  {"after": "this time.", "sec": 0.35, "why": "X2's shoulder stays on the shooter"},
  {"after": "stays with him.", "sec": 0.45, "why": "X2 follows the shooter all the way out"},
  {"after": "toward the screen.", "sec": 0.45, "why": "X1 has jumped: the other shoulder is open"},
  {"after": "OTHER WAY.", "sec": 3.3, "why": "the layup, the late help, the net"}],
 "plays": {"A": "ghost-a-three", "B": "ghost-b-reject"},
 "pinV2": True,
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "ghost-screen.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
