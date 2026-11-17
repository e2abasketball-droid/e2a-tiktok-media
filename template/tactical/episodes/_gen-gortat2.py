#!/usr/bin/env python3
"""GORTAT SCREEN (owner 2026-11-16 16:55Z): same format as Elevator 3D (66 s, Spain editing system, Tactical3DV2).
V2 2026-11-17: wing (45) screen to the right, snake to the middle; new Deuce take (1 generation, 1,136 cr). Gaps mirror the Elevator beats. Base fields; shots: _gen-gortat2-shots.py."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "gortat-screen-v2",
 "title": "The Gortat Screen: How to Break the Drop Coverage",
 "fps": 30,
 "voiceRaw": "tactical/gortat2/voice-raw.mp3",
 "wordsRaw": "gortat-screen-v2.words-raw.json",
 "voice": "tactical/gortat2/voice.wav",
 "voiceMix": "tactical/gortat2/voice.mix.wav",
 "preroll": 0.15,
 "tail": 1.4,
 "gaps": [
  {"after": "the drop coverage.", "sec": 0.85, "why": "hook -> title: dramatic beat on the freeze (SEALED.)"},
  {"after": "This is the Gortat screen.", "sec": 0.55, "why": "title lands before the explanation"},
  {"after": "own defender in the paint.", "sec": 0.6, "why": "block change: setup -> Case A"},
  {"after": "Watch what happens.", "sec": 0.55, "why": "the play starts at real speed"},
  {"after": "Drive. Finish. Two points.", "sec": 0.85, "why": "layup drops, LAYUP +2"},
  {"after": "an open three instead.", "sec": 0.75, "why": "three drops; block change -> comparison"},
  {"after": "corner is wide open.", "sec": 0.75, "why": "side-by-side summary holds before the rule"}],
 "plays": {"A": "gortat2-a-seal", "B": "gortat2-b-kick"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "gortat-screen-v2.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
