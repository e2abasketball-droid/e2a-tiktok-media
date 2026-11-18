#!/usr/bin/env python3
"""HIDE IN GAMES V3: narration gaps (owner brief 2026-11-17 21:31Z, 56-58 s). Composite raw take from
_gen-hide3-voice.py (V2 take reused + one new take for the ending). Gaps up to 'somewhere else.' are the V2 ones,
so the first 24.75 s keep the V2 sync. Writes tactical/episodes/hide3.json; then scripts/tactical-voice.py."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
G = [("want the ball.", 1.2, "reaction: the arm comes down"),
     ("without thinking.", 1.1, "practice: catch, square up"),
     ("game starts.", 2.2, "match cut on the rise, the shot leaves"),
     ("hits the rim.", 3.8, "no narration around the impact and the first reaction; rebound, the game goes on"),
     ("thinking is,", 0.7, "doubt: looks at the passer, then down"),
     ("miss again?", 1.3, "passer framing: half a hand comes up"),
     ("hands drop.", 0.45, "the hand goes back, the defender keeps covering"),
     ("somewhere else.", 1.55, "the pass goes to O3"),
     ("Breathe out.", 1.1, "exhale, light jersey tap"),
     ("next spot.", 2.1, "eyes back on the ball"),
     ("can see you.", 1.3, "plant, hip, slide: the lane opens"),
     ("your hands.", 0.8, "hands up"),
     ("Call for it.", 1.0, "the pass and the catch, ready to shoot"),
     ("closes out.", 0.4, "the closeout, high hand"),
     ("teammate open.", 0.55, "eyes to the corner, the extra pass leaves"),
     ("One more pass.", 4.2, "the teammate controls, players keep moving"),
     ("players miss.", 0.7, "a breath before the lesson"),
     ("of the game.", 1.0, "the possession keeps running"),
     ("do next.", 1.4, "back to #8 relocating, eyes on the ball")]
ep = {"id": "hide3", "title": "Hide in games V3", "fps": 30, "voiceRaw": "tactical/hide3/voice-raw.mp3", "wordsRaw": "hide3.words-raw.json",
      "voice": "tactical/hide3/voice.wav", "voiceMix": "tactical/hide3/voice.mix.wav", "preroll": 0.0, "tail": 0.6,
      "gaps": [{"after": a, "sec": s, "why": w} for a, s, w in G],
      "plays": {}, "shots": []}
json.dump(ep, open(os.path.join(D, "hide3.json"), "w"), indent=1)
print("ok")
