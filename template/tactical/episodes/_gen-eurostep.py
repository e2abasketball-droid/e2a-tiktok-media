#!/usr/bin/env python3
"""THE EUROSTEP (owner brief 2026-11-18 20:25Z): base episode = master voice track (gaps) + word timings.
  python3 scripts/tactical-voice.py tactical/episodes/eurostep.json
Shots: _gen-eurostep-shots.py writes eurostep-main / eurostep-trial."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "eurostep", "title": "The Eurostep", "fps": 30,
 "voiceRaw": "tactical/eurostep/voice-raw.mp3", "wordsRaw": "eurostep.words-raw.json",
 "voice": "tactical/eurostep/voice.wav", "voiceMix": "tactical/eurostep/voice.mix.wav",
 "preroll": 0.1, "tail": 2.4,
 "gaps": [
  {"after": "wrong lane.", "sec": 0.3, "why": "hook cuts on the defender's load"},
  {"after": "on the move.", "sec": 0.55, "why": "gather lands, GATHER + empty counter"},
  {"after": "is step one.", "sec": 1.1, "why": "left foot lands: print 1, 1/2"},
  {"after": "Plant left.", "sec": 0.6, "why": "the sell starts"},
  {"after": "chest and eyes.", "sec": 0.8, "why": "chest/eyes to the left lane"},
  {"after": "hips turn?", "sec": 0.9, "why": "defender's hips and first slide"},
  {"after": "your opening.", "sec": 0.6, "why": "right side space"},
  {"after": "off the left.", "sec": 0.45, "why": "push"},
  {"after": "open lane.", "sec": 1.2, "why": "right foot lands: print 2, 2/2, gold lane"},
  {"after": "off the right.", "sec": 0.35, "why": "take-off"},
  {"after": "his reach.", "sec": 1.5, "why": "glass, net, landing"},
  {"after": "stays square?", "sec": 0.7, "why": "same start, defender holds"},
  {"after": "pick up the ball.", "sec": 0.9, "why": "reframe before the pick-up"},
  {"after": "full speed.", "sec": 0.35, "why": "replay starts"},
  {"after": "Sell left.", "sec": 0.15, "why": "replay beat"},
  {"after": "Cut right.", "sec": 0.15, "why": "replay beat"}],
 "plays": {"A": "euro-a", "B": "euro-b"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "eurostep.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
