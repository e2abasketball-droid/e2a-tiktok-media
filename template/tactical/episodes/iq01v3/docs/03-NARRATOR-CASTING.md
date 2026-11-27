# 03 · Narrator casting (ElevenLabs)

Same test script for every voice ("Wait. Which pass are you making? … The defense tells you where to pass."), with the same per-phrase direction tags.
**I cannot listen to audio.** The ranking uses measurements (pause structure, pitch range from F0, phrase-level pitch/level
contrast, sibilance energy 5–10 kHz) plus Scribe transcripts. **Please listen to the four files in `narrator-casting/`. If your ear disagrees, the swap is one regeneration.**

| Profile | Voice (id) | Model | Duration | Dead air (pauses ≥0.15 s) | Pitch range | Sibilance | Hook / reveal / lesson median F0 | Words |
|---|---|---|---|---|---|---|---|---|
| A · High-energy analyst | Nathaniel, "Live Football Commentator" (9rR45HW0vcBmpCbkc4m9) | eleven_v4 | 17.5 s | **2.6 s** (least) | 18.7 st | 0.145 | 250 / 246 / 129 Hz | 50/50 |
| B · Cinematic storyteller | Ra McQueen (BC4NS8v47Nx7XkOSLEK7) | eleven_v4 | 16.0 s | 3.9 s | 18.9 st | **0.177** (highest) | 242 / 278 / 160 Hz; level swings 11 dB between phrases | 50/50 |
| C · Viral creator | Liam (TX3LPaxmHKxFdv7VOQHJ) | eleven_v4 | 16.3 s | 3.4 s | 19.3 st | **0.126** (lowest) | 229 / 283 / 123 Hz | 50/50 |
| Reference | Deuce (DaueUomjhh8LFuAV8aGj) | eleven_v3 | 20.4 s | 5.8 s | **10.9 st** | 0.111 | – | – |

Readings:
- All three new voices have about **1.7× Deuce's pitch movement**, and all drop about an octave from the reveal to the lesson. The direction tags work; the expression is in the performance, not in volume.
- Ra McQueen gets part of his contrast from loudness (11 dB between phrases), which the brief warns against, and has the most sibilance.
- Liam builds the most from hook to reveal and is the cleanest on sibilance, but his profile is "creator", not "analyst".
- **Choice: Nathaniel.** He has the least dead air, an even level (contrast from pitch and pace, not volume) and the closest fit to "passionate analyst with coach intelligence". British English.
- Runner-up: Liam. Worth an A/B on a future episode, with the narrator recorded in the analytics log.

Cost: casting 4 × 362 credits + 3 transcriptions (274). Full take 693 + Scribe 176. **V3 voice total: 2,591 credits.**
