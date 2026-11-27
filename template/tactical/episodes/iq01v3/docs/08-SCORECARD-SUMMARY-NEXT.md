# 08 · Editorial scorecard, summary, limits and next experiments

## Scorecard (Phase 11). Internal creative assessment, NOT a prediction of performance
Scored by Claude from frame inspection (contact sheets every 1 s plus key stills), measurements (loudness, phone band, SSIM, flicker) and the script. **Nobody listened to the audio.** Narration and audio scores rest on measurements and transcripts only, so treat those two as provisional until a human listens on a phone.

| # | Category | V2 | V3 | Evidence |
|---|---|---|---|---|
| 1 | Hook clarity | 6 | 8 | V2 opened on a static question card. V3 states a conflict in 1.7 s ("The easy pass here is a trap.") over live action, and the "easy" lane to A is drawn on screen. |
| 2 | First-frame impact | 5 | 7 | Frame 0 is now a low, close camera on the ball handler mid-move, with the title already up. It is still a 3D render, not real footage. |
| 3 | Emotional narration | 5 | 7 (provisional) | Deuce: 10.9 st pitch range. Nathaniel: 18.7 st, with a direction tag per phase. Measured, not heard. |
| 4 | Storytelling structure | 6 | 8 | Hook → problem → freeze → 2 s call → misdirection (A, then B) → discovery → reveal → lesson → loop. Every beat is tied to a measured fact. |
| 5 | Visual variety | 6 | 7 | 6 shots and 25+ camera keys. Every freeze moves. One look throughout (HORNS V2 standard); no new 3D environment. |
| 6 | Tactical clarity | 8 | 8 | Same validated play (28/28). Distances shown on screen (1.4 m, 6.0 m). Lanes are 1.6× wider for phones. |
| 7 | Editing rhythm | 6 | 7 | The flattest V2 stretch (5.4–10.4 s, see 01-AUDIT) is now the tilt-per-letter + countdown. The 2.0 s silence is deliberate. |
| 8 | Animation realism | 6 | 6 | No change to models or motion (no Blender/MPFB here, see 05). |
| 9 | Audio quality | 7 | 7 (provisional) | -16.0 LUFS, -1.5 dBTP, LRA 4. Voice 12 LU above the music, ~16 LU in the phone band. No bounce SFX, no crowd, no whooshes. Not heard. |
| 10 | Educational payoff | 7 | 8 | A two-line rule that can be taught ("The ball tells you where the play is. The defense tells you where to pass.") over a top view. |
| 11 | Mobile readability | 7 | 8 | Subtitles at y 1400 with commas. Titles 116 px. Letters and lanes enlarged. Safe margins checked on stills. |
| 12 | Rewatch potential | 6 | 8 | A real loop: the last frame matches frame 0 (court SSIM 0.94 on hook A), plus "Run it back". |

## Versions
- **Version A, competitive (master):** "The easy pass here is a trap." → A/B/C → "Two seconds. Make your call."
- **Version B, curiosity / defensive mistake:** "One defender just left a shooter wide open. Can you spot him?" The same body follows. The opening is 1.76 s longer.
- **Trial file:** hook B through `trial-variant.sh` (3% zoom, grade, voice EQ). Same voice take; no new credits.

## Summary of improvements over V2
New narrator (cast from three profiles, all the same script). A new script built on a real misdirection. The hook starts inside the action. Freezes move. A single misdirection sweep. Discovery with spotlight + ghost. A merged reveal and kick. A top-view lesson. A seamless loop. Lanes sized for phones. A course-clean render. A generator that is fully driven by the voice timings.

## Limits (honest)
- No human listened to any of the audio. Only measurements and the Scribe transcript (101/101 words) were checked.
- No change to 3D models, rigs or motion. Blender/MPFB were not installed (owner decision pending).
- The scores above are one reviewer's judgment and do not predict views or retention.
- The ElevenLabs commercial-use point is assumed from project memory, not re-verified.

## Recommended next experiments (one variable at a time)
1. Post A as the Reel and B as the trial (owner approval required). Compare 3-second hold and average watch time from `analytics-log.csv`.
2. Same edit with Liam (runner-up) as the narrator, as a trial reel, to isolate the narrator variable.
3. Test the length: a 24 s cut without the lesson beat vs. the full 30.8 s.
4. EP02 with the generator pattern from 05, to check how much of V3 really carries over.
