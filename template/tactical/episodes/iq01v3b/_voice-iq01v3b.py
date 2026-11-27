#!/usr/bin/env python3
"""BASKETBALL IQ 01 V3 - TRIAL VERSION B ("READ THE DEFENSE", owner directive 2026-11-27 21:38Z).
A FRESH performance by the official E2A narrator (Nathaniel 9rR45HW0vcBmpCbkc4m9, eleven_v4, 585 cr, flow 6GOo3uZ0cfVXdKo1XftG,
Scribe 132 cr, 75/75 words). The take is used as performed: no cuts, no inserted silences, no time-stretch.
  python3 tactical/episodes/iq01v3b/_voice-iq01v3b.py  -> public/iq01v3b/voice.wav + iq01v3b.words.json"""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(os.path.dirname(D)))
RAW = os.path.join(T, "public/iq01v3b/nathaniel-v3b-take-raw.mp3")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", RAW, "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", os.path.join(T, "public/iq01v3b/voice.wav")], check=True)
raw = json.load(open(os.path.join(D, "iq01v3b-voice.words-raw.json")))
raw = raw["words"] if isinstance(raw, dict) else raw
res = [{"text": w["text"].replace("’", "'"), "start": round(w["start"], 3), "end": round(w["end"], 3)}
       for w in raw if w.get("type", "word") == "word" and not w["text"].startswith("[")]
for i in range(len(res) - 1):
    res[i]["end"] = round(min(res[i]["end"], res[i + 1]["start"]), 3)
# script punctuation (Scribe merges sentences): the performance is exclamatory on these two lines
FIX = {("behind.", "That's"): ("behind!", "That's"), ("window.", "Kick"): ("window!", "Kick"), ("open,", "they"): ("open.", "They")}
for i in range(len(res) - 1):
    k = (res[i]["text"], res[i + 1]["text"])
    if k in FIX:
        res[i]["text"], res[i + 1]["text"] = FIX[k]
json.dump(res, open(os.path.join(D, "iq01v3b.words.json"), "w"), indent=0)
print(len(res), "words, last ends", res[-1]["end"])
