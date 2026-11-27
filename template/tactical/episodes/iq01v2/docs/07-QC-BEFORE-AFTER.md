# 07 · QC report, before/after (checked on the rendered files, not on the plan)

| Gate | V1 social | V2 master (hook A) | V2 alt (hook B) |
|---|---|---|---|
| Duration | 32.7 s | 33.64 s | 33.60 s |
| Question on screen | 3.8 s | **0.0 s** (letters on frame 0) | 0.0 s |
| Question spoken | 3.8 s ("Who's open?") | 0.2 s (the challenge), 6.4 s ("A, B, or C?") | 6.4 s |
| Visible decision deadline | none (2.1 s silent hold) | **2.0 s bar = exactly the inserted silence** (9.45–11.45) | same (9.41–11.41) |
| Frozen time with a static camera | ~19 s, mostly static | 0 s: every freeze has an arc or push (frozen play spans: 0–2.7, 5.4–17.9, 22.1–24.3, 30.3–33.6) | same |
| Answer (C) beat | 2.0 s | 2.3 s frozen + 3.8 s real-speed kick and three, in one shot | same |
| Loop | end camera ≠ first frame | last frame ≈ first frame (SSIM 0.91 on the court area; the overlay text differs) | same |
| qc-video | PASS | **PASS** (-16 LUFS target config) | **PASS** |
| Loudness / true peak | -14.6 LUFS / -1.3 dBTP | **-16.0 LUFS / -1.5 dBFS** | -16.0 / -1.5 |
| Floor flicker (qc-floor-flicker) | 0 bad / 980 | **0 bad / 1008**, 0 blinks | 0 bad / 1008 |
| Subtitle punctuation | "A B OR C?" | "A, B, OR C?" | same |
| Scribe accuracy (voice) | 81/81 | 81/81 + hook B 7/7 words | – |
| Play validator | 28/28 | 28/28 (after the X1 fix) | – |
| Players in question frame | ~75–110 px | ~95–110 px (all 8 must fit in 9:16, so they can't be much bigger; close-ups do that job) | – |
| Bounce SFX / fake crowd / whooshes | none | none (voice + generated music bed only) | none |

Trial file: `e2a-basketball-iq-01-v2-hookB-trial.mp4` = hook B through `scripts/trial-variant.sh` (3% zoom, grade, voice EQ). SSIM 0.54 against hook B; -16.5 LUFS / -1.2 dBFS.

Inspected by eye on frames: contact sheets at 2 fps and 1 fps, plus the key frames (0, the countdown, each reveal, the kick, the loop). **Audio is not listened to**: checked by loudness, peak, the voice-over-music relationship (voice stem -16.3 LUFS versus the -16.0 mix, so the music sits well below it), and silence placement.
