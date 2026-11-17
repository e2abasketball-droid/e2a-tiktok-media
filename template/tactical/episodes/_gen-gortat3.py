#!/usr/bin/env python3
"""GORTAT SCREEN (owner 2026-11-16 16:55Z): same format as Elevator 3D (66 s, Spain editing system, Tactical3DV2).
V3 2026-11-17 01:17Z: the big rolls and seals first, then the guard snakes to the middle; same V2 take with the two sentences swapped (0 cr). V2 2026-11-17: wing (45) screen to the right, snake to the middle; new Deuce take (1 generation, 1,136 cr). Gaps mirror the Elevator beats. Base fields; shots: _gen-gortat2-shots.py."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "gortat-screen-v3",
 "title": "The Gortat Screen: How to Break the Drop Coverage",
 "fps": 30,
 "voiceRaw": "tactical/gortat3/voice-raw.wav",
 "wordsRaw": "gortat-screen-v3.words-raw.json",
 "voice": "tactical/gortat3/voice.wav",
 "voiceMix": "tactical/gortat3/voice.mix.wav",
 "preroll": 0.15,
 "tail": 1.4,
 "gaps": [
  {"after": "the drop coverage.", "sec": 0.85, "why": "hook -> title: dramatic beat on the freeze (SEALED.)"},
  {"after": "This is the Gortat screen.", "sec": 0.55, "why": "title lands before the explanation"},
  {"after": "stuck on his back.", "sec": 0.6, "why": "block change: setup -> Case A"},
  {"after": "Watch what happens.", "sec": 0.55, "why": "the play starts at real speed"},
  {"after": "Drive. Finish. Two points.", "sec": 0.85, "why": "layup drops, LAYUP +2"},
  {"after": "an open three instead.", "sec": 0.75, "why": "three drops; block change -> comparison"},
  {"after": "corner is wide open.", "sec": 0.75, "why": "side-by-side summary holds before the rule"}],
 "plays": {"A": "gortat3-a-seal", "B": "gortat3-b-kick"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "gortat-screen-v3.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
