#!/usr/bin/env python3
"""BLIND PIG (owner brief 2026-11-19, ENCARGO-blind-pig): base episode = the ONE take (ElevenLabs eleven_v4, Deuce,
535 credits) + gaps at acoustic silences only (no re-synthesis, no time-stretch).
  python3 tactical/episodes/_gen-blind-pig.py && python3 scripts/tactical-voice.py tactical/episodes/blind-pig.json
Shots: _gen-blind-pig-shots.py writes blind-pig-main (the Reel).
Structure (brief): contradictory result -> open loop -> mechanism -> payoff -> rehook -> second payoff -> question."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "blind-pig", "title": "Blind Pig", "fps": 30,
 "voiceRaw": "tactical/blindpig/voice-raw.mp3", "wordsRaw": "blind-pig.words-raw.json",
 "voice": "tactical/blindpig/voice.wav", "voiceMix": "tactical/blindpig/voice.mix.wav",
 "preroll": 0.1, "tail": 1.7,
 "gaps": [
  {"after": "the layup.", "sec": 0.95, "why": "result stamp, then the rewind to the start (open loop)"},
  {"after": "on the right.", "sec": 0.55, "why": "lock ring lands on X2"},
  {"after": "high post.", "sec": 0.75, "why": "the entry pass travels O1 -> O4"},
  {"after": "behind him.", "sec": 0.5, "why": "the cut is on, X2 still facing the ball"},
  {"after": "see both.", "sec": 0.95, "why": "freeze: vision conflict (ball vs man)"},
  {"after": "the denial.", "sec": 2.0, "why": "bounce pass, in-stride catch, layup, rim, then the rewind"},
  {"after": "force it.", "sec": 0.5, "why": "the bounce lane is closed (X3 in it)"},
  {"after": "just left.", "sec": 1.55, "why": "kick-out flight, shot, swish, OPEN 3"},
  {"after": "Blind Pig.", "sec": 0.8, "why": "name card + three-step structure"},
  {"after": "Deny the pass...", "sec": 0.35, "why": "DENY? lands before 'or protect the rim?'"}],
 "plays": {"A": "blindpig-a-layup", "B": "blindpig-b-kick"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "blind-pig.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
