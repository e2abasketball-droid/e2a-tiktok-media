#!/usr/bin/env python3
"""ONE MORE DRIBBLE (owner brief 2026-11-17 05:40Z): base episode = master voice track (gaps) + shared word timings.
  python3 scripts/tactical-voice.py tactical/episodes/onemore.json
Shots: _gen-onemore-shots.py writes onemore-main (Reel) and onemore-trial (trial-reel variant, same voice)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "onemore",
 "title": "One More Dribble: read the last defender in a 2-on-1",
 "fps": 30,
 "voiceRaw": "tactical/onemore/voice-raw.mp3",
 "wordsRaw": "onemore.words-raw.json",
 "voice": "tactical/onemore/voice.wav",
 "voiceMix": "tactical/onemore/voice.mix.wav",
 "preroll": 0.12,
 "tail": 2.4,
 "gaps": [
  {"after": "a mistake?", "sec": 1.6, "why": "the play runs into the decision"},
  {"after": "Freeze it here.", "sec": 0.5, "why": "freeze lands"},
  {"after": "one more dribble?", "sec": 1.5, "why": "freeze held ~1 s after the question, both options drawn"},
  {"after": "the early pass.", "sec": 0.45, "why": "pass leaves"},
  {"after": "ball leaves.", "sec": 1.9, "why": "pass flight, the catch"},
  {"after": "to cover.", "sec": 0.45, "why": "overhead route grows"},
  {"after": "on the catch.", "sec": 2.0, "why": "CATCH CONTESTED"},
  {"after": "Same setup.", "sec": 0.45, "why": "rewind lands"},
  {"after": "One more dribble.", "sec": 0.7, "why": "the full extra dribble"},
  {"after": "his feet.", "sec": 0.6, "why": "cut to the low shot"},
  {"after": "toward the ball.", "sec": 1.4, "why": "his weight shifts"},
  {"after": "into the space.", "sec": 3.6, "why": "pass, catch, layup"},
  {"after": "with the pass?", "sec": 1.6, "why": "second hook, scene clean"},
  {"after": "Same dribble.", "sec": 0.5, "why": "X10 stays"},
  {"after": "is yours.", "sec": 0.5, "why": "penetration arrow"},
  {"after": "Go finish.", "sec": 3.1, "why": "gather, steps, layup"},
  {"after": "Steps up? Pass.", "sec": 1.8, "why": "recap fragment 1"},
  {"after": "pass? Finish.", "sec": 2.4, "why": "recap fragment 2 + PASS NOW OR ONE MORE?"}],
 "plays": {"A": "onemore-a-early", "B": "onemore-b-commit", "C": "onemore-c-stay"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "onemore.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
