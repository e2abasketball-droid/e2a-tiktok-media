#!/usr/bin/env python3
"""ELEVATOR SCREEN 3D (owner 2026-11-16 15:46Z): the 66 s Elevator Screen pilot (V2) rebuilt in the real-3D engine with the
Spain pick-and-roll editing system. SAME narration take (no new voice), SAME gaps as V2, same story beats.
Base fields; shots: _gen-elevator3d-shots.py."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
v2 = json.load(open(os.path.join(D, "elevator-screen.json")))
ep = {
 "id": "elevator-3d",
 "title": "The Elevator Screen: Two Ways to Punish the Defense (3D)",
 "fps": 30,
 "voiceRaw": "tactical/elevator/voice-raw.mp3",
 "wordsRaw": "elevator-3d.words-raw.json",
 "voice": "tactical/elevator3d/voice.wav",
 "voiceMix": "tactical/elevator3d/voice.mix.wav",
 "preroll": 0.15,
 "tail": 1.4,
 "gaps": v2["gaps"],
 "plays": {"A": "elev3d-a-chase", "B": "elev3d-b-switch"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "elevator-3d.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
