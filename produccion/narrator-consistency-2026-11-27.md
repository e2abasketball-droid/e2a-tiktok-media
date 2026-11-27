# Narrator consistency test, 2026-11-27 (E2A Narration Standard v1)

**Test take:** a new script (not used in any video), generated with exactly what `tools/narrator.py params` outputs: Nathaniel `9rR45HW0vcBmpCbkc4m9`, `eleven_v4`, 1 take, phase tags, no voice settings.
283 credits. Flow `6GOo3uZ0cfVXdKo1XftG`, generation `Hb57bunYvV6BVM8iUZel`. File: `assets/audio/narrator-consistency-test-2026-11-27.mp3`.
> [intriguing, confident] Stop watching the ball handler. [low, building suspense] Look at the help side... [rising intensity] the defender takes one step too many, [energetic reveal] and THAT's the open man! [slower, confident teaching] Read the defense first. Then make the pass.

**Reference:** `assets/audio/narrator-reference-v3.mp3` (the raw take behind the approved master).
**Method:** `python3 tools/narrator_compare.py` (objective proxies). **Claude did not listen to any of these files.** A human listen on a phone is still the real test of naturalness and energy.

| Take | Identity: LTAS corr. vs ref | LTAS diff (dB) | Median pitch vs ref | Pitch range (st) | Pause share | Clipping |
|---|---|---|---|---|---|---|
| Reference V3 (Nathaniel) | 1.000 | 0.00 | 0 | 17.2 | 0.23 | 0 |
| **Consistency test (standard)** | **0.978** | 1.93 | -2.3 st | **16.5** | 0.25 | 0 |
| Trial "Read the defense" take | 0.974 | 2.27 | -3.9 st | 16.0 | 0.25 | 0 |
| Casting line, Nathaniel (same voice) | 0.996 | 0.79 | 0 | 18.9 | 0.26 | 0 |
| Control: Liam (other voice) | 0.963 | 2.65 | -0.4 st | 19.4 | 0.34 | 0 |
| Control: Ra McQueen (other voice) | 0.859 | 4.73 | +2.7 st | 16.3 | 0.55 | 0 |
| Control: Deuce (old narrator) | 0.918 | 5.26 | -1.3 st | 11.7 | 0.30 | 0 |

## What this shows (and what it does not)
- **Voice identity: confirmed by the generation record.** ElevenLabs returned voice `9rR45HW0vcBmpCbkc4m9`, "Nathaniel - Live Football Commentator", model `eleven_v4`. That is the strongest evidence.
- **Spectrum:** the acoustic proxy agrees. The new takes sit closer to the reference than Deuce or Ra McQueen do.
- **Limit of the proxy:** the proxy cannot cleanly separate Nathaniel from Liam (0.963), so it supports the record but does not replace it.
- **Expressiveness preserved:** pitch range is 16–16.5 semitones against 17.2 in the reference (Deuce: 11.7). There is still clear intonation movement, and no clipping or level jumps.
- **Register difference:** both new takes sit lower in pitch: -2.3 and -3.9 semitones in median. They used more `[low ...]` / suspense lines and fewer high-energy lines than the V3 master.
- **Rule added to the standard:** use a `low` tag for at most one line. Keep the hook and reveal on the high-energy tags, so the brightness of the approved master carries over.
- **Pronunciation:** Scribe transcribed the trial take word-perfect (75/75). The test take was not transcribed.
- **Artifacts:** none measurable (no clipping, no dropouts).
- **Remaining uncertainty:** the connector does not publish the numeric similarity default. "Not set", the same as the approved take, is the recorded configuration.
