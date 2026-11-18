#!/usr/bin/env python3
"""CHICAGO ACTION pilot (owner brief 2026-11-14 18:56Z): "Take the Handoff or Cut Backdoor?", 9:16, English.
Base fields (voice, gaps, plays). Shots are added by _gen-chicago-action-shots.py once the real word timings exist
(scripts/tactical-voice.py writes chicago-action.words.json)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "chicago-action",
 "title": "CHICAGO ACTION: Take the Handoff or Cut Backdoor? (private review pilot)",
 "fps": 30,
 "voiceRaw": "tactical/chicago/voice-raw.mp3",
 "wordsRaw": "chicago-action.words-raw.json",
 "voice": "tactical/chicago/voice.wav",
 "voiceMix": "tactical/chicago/voice.mix.wav",
 "preroll": 0.12,
 "tail": 1.7,
 "gaps": [
  {"after": "opened the rim.", "sec": 0.7, "why": "hook: the lane is suggested, cut before the basket"},
  {"after": "Chicago action.", "sec": 0.35, "why": "CHICAGO ACTION title lands"},
  {"after": "into a handoff.", "sec": 1.5, "why": "overhead: the receiver's route reaches the hand-off spot"},
  {"after": "take it tight.", "sec": 0.3, "why": "the exchange at the passer's hip"},
  {"after": "stays deep.", "sec": 1.4, "why": "the pull-up flies and drops"},
  {"after": "watch his feet.", "sec": 1.0, "why": "slow motion on the defender's jump"},
  {"after": "changes hands.", "sec": 0.45, "why": "X2 in the exchange line, the ball still with the passer"},
  {"after": "Keep the ball.", "sec": 0.35, "why": "the plant"},
  {"after": "beats the help.", "sec": 1.3, "why": "catch, layup, make"},
  {"after": "touch the ball.", "sec": 0.4, "why": "both decision frames read"}],
 "plays": {"A": "chicago-a-take", "B": "chicago-b-backdoor"},
 "pinV2": True,
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "chicago-action.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
