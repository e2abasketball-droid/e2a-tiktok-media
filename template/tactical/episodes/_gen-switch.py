#!/usr/bin/env python3
"""HOW TO PUNISH THE SWITCH (owner brief 2026-11-17 12:50Z): base episode = master voice track (gaps) + word timings.
  python3 scripts/tactical-voice.py tactical/episodes/switch.json
Shots: _gen-switch-shots.py writes switch-main."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
ep = {
 "id": "switch",
 "title": "How to Punish the Switch",
 "fps": 30,
 "voiceRaw": "tactical/switch/voice-raw.mp3",
 "wordsRaw": "switch.words-raw.json",
 "voice": "tactical/switch/voice.wav",
 "voiceMix": "tactical/switch/voice.mix.wav",
 "preroll": 0.12,
 "tail": 2.0,
 "gaps": [
  {"after": "stop you.", "sec": 0.55, "why": "short pause after the hook"},
  {"after": "your mismatch.", "sec": 1.4, "why": "matchups land, cut to the replay"},
  {"after": "on the guard.", "sec": 0.45, "why": "BIG ON GUARD forms"},
  {"after": "on the big.", "sec": 0.45, "why": "SMALL ON BIG forms"},
  {"after": "Now what?", "sec": 1.5, "why": "freeze on the post-switch state"},
  {"after": "inside first.", "sec": 0.6, "why": "ring toward O5"},
  {"after": "have a seal?", "sec": 1.4, "why": "freeze held, then the seal starts"},
  {"after": "guard pinned.", "sec": 0.5, "why": "DEEP SEAL"},
  {"after": "feed him.", "sec": 3.2, "why": "pass, catch, short finish"},
  {"after": "pass is gone?", "sec": 1.6, "why": "ENTRY DENIED"},
  {"after": "Same switch.", "sec": 0.5, "why": "same state"},
  {"after": "in space.", "sec": 0.45, "why": "space in front of O1"},
  {"after": "Change pace.", "sec": 0.5, "why": "hesitation"},
  {"after": "his hip.", "sec": 3.4, "why": "drive, X5 recovers, layup"},
  {"after": "Feed it.", "sec": 2.2, "why": "recap A"},
  {"after": "Attack the big.", "sec": 2.2, "why": "recap B"},
  {"after": "see first?", "sec": 1.4, "why": "INSIDE OR OUTSIDE? readable"}],
 "plays": {"A": "switch-a-seal", "B": "switch-b-drive"},
 "shots": [],
}
json.dump(ep, open(os.path.join(D, "switch.json"), "w"), indent=1, ensure_ascii=False)
print("base written")
