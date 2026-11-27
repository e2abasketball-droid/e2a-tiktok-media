# Basketball IQ 02 "Beat the Blitz": script and narration

**Narrator:** E2A standard (Nathaniel - Live Football Commentator, `9rR45HW0vcBmpCbkc4m9`, `eleven_v4`, 1 take, no voice settings). `tools/narrator.py check` printed `OK: E2A narrator standard`.
**Generation:** flow `00N67gIgNnqYisFd5RPg`. Master take `JIW1EcKC1WB5WCujPk5q` (609 credits, 22.96 s). Alternative key lines `Pk957tK9NrdCA2NdWFl8` (173 credits, 6.4 s). Scribe: master 126 credits (67 words), alternatives 35 credits.
**Files:** `public/iq02/nathaniel-iq02-take-raw.mp3` (never regenerate), `public/iq02/nathaniel-iq02-alt-keylines-raw.mp3`, `public/iq02/voice.wav` (take + inserted silences), `voice.mix.wav`, `music.wav`, `mix.wav`.

## Prompt as performed (built by `tools/narrator.py params`)
| # | Direction tag | Line | Storyboard shot |
|---|---|---|---|
| 1 | explosive, confident | They send TWO at the ball! | 01 hook / 02 blitz |
| 2 | fast, challenging | Your big catches the short roll. Four on three. | 03 release |
| 3 | controlled curiosity | Looks easy... until the help moves. | 04 problem |
| 4 | quick decision challenge | Drive? Corner? Or cut? (then 2.0 s silence) | 05 freeze |
| 5 | measured, confident | Drive? The help is already there. | 06 why A |
| 6 | (same) | Corner? His defender never left. | 07 why B |
| 7 | intrigued, focused | Now watch the weak-side defender. | 08 reveal |
| 8 | building intensity | He steps into the paint... | 08 reveal |
| 9 | high-energy reveal | and LOSES the cutter! | 08 reveal |
| 10 | decisive | THERE'S the pass! | 09 finish |
| 11 | lower, authoritative (the one "low" tag) | Read the help. Attack the space it leaves. | 10 lesson |
| 12 | short, energetic ending | Did you see it? | 10 close + loop |

Changes from the preferred script, and why:
- "Watch number four's defender" became "Now watch the weak-side defender." (the option the directive allowed; viewers do not see jersey numbers reliably on a phone).
- Shots 06 and 07 ("Why A", "Why B") needed lines. I added "Drive? The help is already there." and "Corner? His defender never left." Both are validated claims: A is BLOCKED (X4 is 0.06 m from O5's line to the rim) and B is BLOCKED (X3 is home, 1.12 m from O3).
- Lesson: "Read the help. Attack the space it leaves." (preferred script) rather than the storyboard's "Hit the space it leaves."

## Objective checks of the take (Claude did not listen)
| Take | LTAS corr. vs V3 reference | Median pitch vs ref | Pitch range | Pause share | Clipping |
|---|---|---|---|---|---|
| Master IQ02 | 0.992 | -0.9 st | 20.1 st (ref 17.2) | 0.28 | 0 |
| Alternative key lines | 0.961 | +4.1 st | 16.1 st | 0.30 | 0 |

- Scribe transcribed every word except one ambiguity: "catches" was transcribed as "catch is". The subtitles use the script word. **A human should listen to "Your big catches the short roll" (raw take 2.30–2.60 s).**
- The alternative take sits 4 semitones higher (more excited). It is **not spliced** into the master, because a 4-semitone jump inside one continuous performance would be audible. It is delivered for review. If the owner prefers one of its lines, the edit can swap that line without a new generation.

## Edit of the take (no regeneration, no time-stretch, no pitch change)
The take is split in the middle of the gaps between lines, and only silence is inserted (`_voice-iq02.py`): +0.9 s after the hook (blitz beat), +0.7 s after "Four on three.", +0.4 s, **+2.0 s decision window after "Or cut?"** (the on-screen countdown lasts exactly this silence), +0.9 s (rewind), +2.4 s after "THERE'S the pass!" (pass and layup at real speed) and +0.4 s.

## Audio chain
`scripts/voice-dynamics.py --preserve --mix-lufs -16` (the standard chain). The bed is `tools/audio/darktech_states.py` at 140 BPM: synthesised in numpy, no samples, owned by E2A. Its states follow the edit: A (high energy) for the hook, B (half-time) for the explanation, BREAK during the 2.0 s decision, A for the reveal and the finish, B for the lesson. No bounce or dribble sounds, no crowd, no whooshes.
