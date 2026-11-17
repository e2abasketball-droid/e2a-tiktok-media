#!/usr/bin/env python3
"""FLOPPY: CURL OR FADE? (owner brief 2026-11-15 10:52Z), 9:16, English, 35-37 s, private review.
Base fields (voice, gaps, plays). Shots: _gen-floppy-shots.py once scripts/tactical-voice.py wrote the real word timings."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "floppy-curl-or-fade",
 "title": "FLOPPY: Curl or Fade? (private review)",
 "fps": 30,
 "voiceRaw": "tactical/floppy/voice-raw.mp3",
 "wordsRaw": "floppy-curl-or-fade.words-raw.json",
 "voice": "tactical/floppy/voice.wav",
 "voiceMix": "tactical/floppy/voice.mix.wav",
 "preroll": 0.12,
 "tail": 2.7,
 "gaps": [
  {"after": "wide open.", "sec": 0.8, "why": "hook: the open corner holds, cut before the shot"},
  {"after": "Watch the defender.", "sec": 1.1, "why": "overhead: O2 reaches the screen, X2 marked"},
  {"after": "finish at the rim.", "sec": 2.0, "why": "the layup drops"},
  {"after": "Different read.", "sec": 0.8, "why": "same overhead, same start"},
  {"after": "fade out.", "sec": 0.55, "why": "cut to the corner angle"},
  {"after": "let it fly.", "sec": 2.4, "why": "the three flies and drops"},
  {"after": "TRAIL, curl.", "sec": 0.8, "why": "repeat A lands"},
  {"after": "corner open, fade.", "sec": 1.2, "why": "repeat B lands"}],
 "plays": {"A": "floppy-a-curl", "B": "floppy-b-fade"},
 "pinV2": True,
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "floppy-curl-or-fade.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
