#!/usr/bin/env python3
"""SPAIN PICK & ROLL 2.0 (owner brief 2026-11-19, ENCARGO-spain-pnr-2): base episode = the ONE approved take
(ElevenLabs eleven_v4, Deuce) + gaps at acoustic silences only (no re-synthesis, no time-stretch).
  python3 tactical/episodes/_gen-spain-pnr-2.py && python3 scripts/tactical-voice.py tactical/episodes/spain-pnr-2.json
Shots: _gen-spain-pnr-2-shots.py writes spain-pnr-2-main (the Reel). Same story as E2A-TACTICAL-2026-11-15-V02
(spain-pick-and-roll-1115, the published original): one ball screen + one back screen, two reads (roll / pop)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "spain-pnr-2", "title": "Spain Pick & Roll 2.0", "fps": 30,
 "voiceRaw": "tactical/spain2/voice-raw.mp3", "wordsRaw": "spain-pnr-2.words-raw.json",
 "voice": "tactical/spain2/voice.wav", "voiceMix": "tactical/spain2/voice.mix.wav",
 "preroll": 0.1, "tail": 1.3,
 "gaps": [
  {"after": "Two screens.", "sec": 0.6, "why": "micro-freeze: SCREEN 1 then SCREEN 2 pulse"},
  {"after": "This is Spain.", "sec": 0.65, "why": "SPAIN / PICK & ROLL title lands and clears"},
  {"after": "at the top.", "sec": 0.35, "why": "ball-screen contact ripple"},
  {"after": "to stop the roll.", "sec": 1.0, "why": "back-screen contact, freeze, the defender who decides"},
  {"after": "takes the roller.", "sec": 0.6, "why": "freeze: OPEN window in the paint"},
  {"after": "Pocket pass.", "sec": 0.4, "why": "the pass line travels, the ball follows"},
  {"after": "at the rim.", "sec": 1.5, "why": "layup + rim flash + EASY 2, then rewind: SAME ACTION. DIFFERENT READ."},
  {"after": "is free.", "sec": 0.3, "why": "spotlight moves to O2"},
  {"after": "Open three.", "sec": 1.3, "why": "ball flight, swish, OPEN 3"},
  {"after": "too much.", "sec": 0.35, "why": "the trapped defender"},
  {"after": "something up.", "sec": 0.55, "why": "two ghost routes, two endpoints"},
  {"after": "guarding Spain?", "sec": 0.3, "why": "ROLL? / POP?"}],
 "plays": {"A": "spain2-a-roll", "B": "spain2-b-pop"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "spain-pnr-2.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
