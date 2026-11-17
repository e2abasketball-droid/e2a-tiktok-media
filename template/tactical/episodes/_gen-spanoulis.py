#!/usr/bin/env python3
"""SPANOULIS ACTION (owner brief 2026-11-17 00:47Z): ONE master narration (Deuce, 1 take) shared by three versions.
This base episode only builds the master voice track (gaps) and the shared word timings:
  python3 scripts/tactical-voice.py tactical/episodes/spanoulis.json
Versions: _gen-spanoulis-shots.py writes spanoulis-main / spanoulis-trial-01 / spanoulis-trial-02."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "spanoulis",
 "title": "Spanoulis Action: One Screen, Two Threats",
 "fps": 30,
 "voiceRaw": "tactical/spanoulis/voice-raw.mp3",
 "wordsRaw": "spanoulis.words-raw.json",
 "voice": "tactical/spanoulis/voice.wav",
 "voiceMix": "tactical/spanoulis/voice.mix.wav",
 "preroll": 0.12,
 "tail": 2.0,
 "gaps": [
  {"after": "can't stop both.", "sec": 1.0, "why": "hook lands, rewind"},
  {"after": "before the handoff.", "sec": 0.45, "why": "setup settles"},
  {"after": "straight to the rim.", "sec": 1.5, "why": "the cutter reaches the rim"},
  {"after": "so dangerous.", "sec": 0.9, "why": "freeze on the guard"},
  {"after": "comes back for the handoff.", "sec": 0.6, "why": "the hand-off happens"},
  {"after": "watch his defender.", "sec": 0.45, "why": "ring on his defender"},
  {"after": "attack the gap.", "sec": 2.2, "why": "drive to the layup + ATTACK THE GAP"},
  {"after": "pull up and shoot.", "sec": 2.3, "why": "ball flight to the swish + PULL-UP THREE"},
  {"after": "different answers.", "sec": 1.2, "why": "recap title holds"}],
 "plays": {"A": "spanoulis-a-trail", "B": "spanoulis-b-under"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "spanoulis.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
