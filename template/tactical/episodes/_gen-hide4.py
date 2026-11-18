#!/usr/bin/env python3
"""HIDE IN GAMES V4: narration gaps (owner brief 2026-11-18 02:39Z, 54 s, windows 0/3.4/8.3/14.0/20.4/26.0/33.3/42.1/54).
Composite raw take from _gen-hide4-voice.py. Pauses 0.15-0.35 s inside a block, 0.35-0.60 s between blocks; every gap
over 0.60 s names the visible/audible action that justifies it. Writes tactical/episodes/hide4.json; then
scripts/tactical-voice.py (only room tone is inserted, the voice is never stretched)."""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
G = [("the ball.", 0.30, "hook -> practice memory"),
     ("calls for it.", 0.30, "warm practice -> game, same framing"),
     ("hearing that miss.", 1.00, "brief rebound memory + short rim echo, #8 looks at the passer"),
     ("miss again?", 0.45, "the hand comes back at the end of the question"),
     ("his hands.", 0.45, "half a hand rises"),
     ("them back.", 1.00, "the hand is back down; cut to the passer's POV, #14 in the line"),
     ("right at him.", 0.25, ""),
     ("in the way.", 0.25, ""),
     ("somewhere else.", 2.30, "the pass travels to O3 and is caught, #8's eyes follow it; new possession"),
     ("about the shot.", 0.30, ""),
     ("one job.", 0.40, "exhale, eyes up to the passer"),
     ("open again.", 0.75, "first step to the space, #14 moves with him"),
     ("get free.", 0.30, ""),
     ("defender follows.", 1.00, "#14 keeps the line closed: no window, #8 hesitates"),
     ("calls again.", 0.45, "the pass leaves as the line opens"),
     ("pass comes.", 0.35, "the catch"),
     ("ready to shoot.", 0.30, ""),
     ("defender closes.", 0.35, "eyes to the corner"),
     ("teammate's open.", 0.30, ""),
     ("one more pass.", 3.30, "the extra pass travels, #4 catches and attacks, #8 relocates"),
     ("best players miss.", 0.50, ""),
     ("of the game.", 0.50, ""),
     ("do next.", 1.10, "callback: #8 plants and asks; back to the live possession"),
     ("it again.", 0.60, "own short pause before the last line")]
ov = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
ep = {"id": "hide4", "title": "Hide in games V4", "fps": 30, "voiceRaw": "tactical/hide4/voice-raw.mp3", "wordsRaw": "hide4.words-raw.json",
      "voice": "tactical/hide4/voice.wav", "voiceMix": "tactical/hide4/voice.mix.wav", "preroll": 0.0, "tail": 0.5,
      "gaps": [{"after": a, "sec": ov.get(a, s), "why": w} for a, s, w in G],
      "plays": {}, "shots": []}
json.dump(ep, open(os.path.join(D, "hide4.json"), "w"), indent=1)
print("ok")
