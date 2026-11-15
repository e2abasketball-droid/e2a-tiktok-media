#!/usr/bin/env python3
"""IVERSON CUT: CATCH OR BACKDOOR? (owner brief 2026-11-15 10:52Z), 9:16, English, 35-37 s, private review.
Base fields (voice, gaps, plays). Shots: _gen-iverson-shots.py once scripts/tactical-voice.py wrote the real word timings."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "iverson-catch-or-backdoor",
 "title": "IVERSON CUT: Catch or Backdoor? (private review)",
 "fps": 30,
 "voiceRaw": "tactical/iverson/voice-raw.mp3",
 "wordsRaw": "iverson-catch-or-backdoor.words-raw.json",
 "voice": "tactical/iverson/voice.wav",
 "voiceMix": "tactical/iverson/voice.mix.wav",
 "preroll": 0.12,
 "tail": 2.2,
 "gaps": [
  {"after": "he's gone.", "sec": 0.75, "why": "hook: the deny holds, cut on the plant"},
  {"after": "elbow screens.", "sec": 1.3, "why": "overhead: O2 clears the second screen"},
  {"after": "you can face up.", "sec": 1.6, "why": "the catch, the face-up"},
  {"after": "what changes.", "sec": 0.65, "why": "same overhead, same start"},
  {"after": "sell the catch.", "sec": 0.6, "why": "the plant"},
  {"after": "your BACKDOOR.", "sec": 2.1, "why": "catch, layup, make"},
  {"after": "trails, catch.", "sec": 0.6, "why": "repeat A lands"},
  {"after": "denies, cut.", "sec": 0.75, "why": "repeat B lands"}],
 "plays": {"A": "iverson-a-catch", "B": "iverson-b-backdoor"},
 "pinV2": True,
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "iverson-catch-or-backdoor.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
