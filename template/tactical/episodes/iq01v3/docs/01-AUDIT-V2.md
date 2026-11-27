# 01 · Forensic audit of the V2 master (e2a-basketball-iq-01-v2-master-hookA.mp4, 33.64 s)

Method: frame grabs (1 fps and 2 fps sheets plus key frames), a per-second motion measure (mean absolute frame difference
at 10 fps, scaled 135×240), ffmpeg ebur128, the Scribe transcript, pitch/pause/sibilance metrics of the voice, and the
play validator. **I cannot listen.** Statements about the voice come from measurements and the transcript, not from listening.

## Per-second motion (higher = more visual change)
```
0 0.8  1 3.2  2 7.7  3 14.2  4 13.4  5 3.0  6 1.0  7 0.7  8 0.4  9 0.8  10 2.5  11 7.3  12 3.6  13 5.5  14 3.1  15 12.1
16 4.3 17 5.5 18 5.0 19 2.4 20 3.6 21 3.9 22 5.5 23 5.0 24 7.0 25 5.4 26 6.0 27 4.0 28 7.8 29 3.9 30 3.8 31 1.9 32 4.1 33 0.8
```
**5.4–10.4 s is the flattest stretch of the video:** five seconds of the same wide frame (freeze, A/B/C, countdown), with motion under 1.0. The opening second is also almost still (0.8).

## 1.1 Hook strength
| Time | Finding | Fix in V3 |
|---|---|---|
| 0.0–2.8 | Frame 0 shows the full floor from high and far. The players are about 100 px tall, and the letters and title are clear. It reads as "a diagram", not as action. Without audio, the challenge comes only from the text ("THREE TEAMMATES / ONE RIGHT PASS"). | Open **close to the drive** (low, behind the ball handler, mid-stride), with a spoken challenge on frame 0, then a fast reframe to the options. |
| 0.0–2.8 | "Three teammates. One right pass." is a rule, not a conflict. Nothing is at stake in the first second. | Use a stronger first line built around the trap ("The easy pass is a trap", Concept A). |

## 1.2 Visual stimulation
| Time | Finding | Fix |
|---|---|---|
| 0.0–1.0 | Static frame (arc too slow to register). | Start in motion. |
| 5.4–10.4 | One wide framing for 5 s: freeze, letters, title, countdown. | Split it: the freeze lands on a push-in, the letters arrive with a fast reframe across the three options, and the countdown plays over a slow low orbit. |
| 11.7–17.9 | A and B are two near-identical oblique close-ups (same lens, same move). | Treat A and B as one continuous "misdirection" move from A to B. |
| 28.3–30.9 | Top-down lesson is a new angle (good), but its graphics are small. | Keep the angle, but make the lesson graphic bigger. |
| 30.9–33.6 | End returns to the same wide frame as 0.0 and 5.4. It is the third time we see it. | End on a different closing frame that still matches the opening for the loop. |

## 1.3 Storytelling tension
- The question is on screen at 0.0 and spoken at 6.4 ("A, B, or C?"). Six seconds between the visual question and the spoken one is slack.
- A (11.7) and B (14.9) are shown and rejected before the helper is explained (17.9). The viewer learns "not A, not B" before learning *why C*. This is a process of elimination, not a discovery.
- The payoff (C, 22.2) arrives 12 s after the decision window. That is too long, and the middle sags.
- V3 order: **trap (A looks easy) → the helper is the discovery → C revealed by the helper's movement → kick**. B is folded into the misdirection beat.

## 1.4 Voice performance (Deuce, eleven_v3; measured)
- Pitch range 8.9–12.9 semitones across the V1/V2 takes. Delivery is clear and word-perfect (81/81), but the narrow range points to an even, explanatory tone. That matches the brief's complaint.
- Pace is about 2.6 words per second, with frequent pauses of 0.3–0.6 s between short sentences. Rhythm is repetitive: short sentence, pause, short sentence.
- Stress placement is decent ("That's the read. C."), but the reveal line is no more energetic than the explanation lines. The `[slowly]` tag made it calmer, not more exciting.
- Sync: lines start 0.1–0.3 s after their picture cue (fine).
- V3: recast the narrator (three voices tested), direct each line by emotional phase, and cut dead pauses.

## 1.5 Basketball clarity
- Positions support C (X3 6.0 m from O3, X2 1.4 m from O2, X4 in the O1→O4 lane, X4 4.0 m from O3 at the catch). Validator 28/28.
- Risk: in the wide frame, X3's rotation is hard to see at 100 px. The viewer may not register *who* left the corner until the replay at 17.9.
- Risk: "B? His defender is sitting in the passing lane." The lane graphic is clear, but on a phone the B close-up doesn't show O1, so the viewer has to infer the lane direction.

## 1.6 Visual design
| Element | Status | V3 action |
|---|---|---|
| A/B/C badges | Clear, 96 px. Off-screen ones are dropped (fixed in V2). | Keep. Add a short "lock-on" ring pulse when each letter is named. |
| Freeze tag | Small "FREEZE" chip, top right. | Keep. |
| Help callouts | Red pin "LOW HELP" plus spotlight. Works. | Make it the centre of the reveal (bigger, longer). |
| Arrows / lanes | Lanes are thin dashed lines, hard to see at 100 px. | Thicker lanes with distinct states (available, contested, blocked, revealed). |
| Replay | "REWIND" tag only. | Keep, used fewer times (two rewinds in V2 is one too many). |
| Subtitles | Readable, 18 gold keywords, at 1390 px. | Fewer gold words, phrase-level. |
| Typography | Titles at top-left are consistent but repetitive (6 titles). | Fewer, bigger, phrase-led titles only on key beats. |
| Logo | Small 2026 logo at the end. | Keep. |

## 1.7 3D realism (from frames)
- Proportions and kits fine (v33 bodies, IQ kits).
- X1 no longer stops dead (V2 fix). X2's pinch pose is still slightly stiff in close-up.
- The defensive stance of X3 during the rotation reads upright in the replay close-up.
- Shadows are present (contact shadows in v33). Arena lighting is even but flat: the court reads bright in the middle and players don't separate strongly from the floor in wide shots.
- The pass is a clean arc. The catch-and-shoot reads well.
- V3 priorities: stronger player/floor separation (grade + vignette + rim light within the existing env), lower camera heights near the action, and keeping close-ups away from X2.

## Summary of V2 problems (ranked)
1. Passive hook (wide diagram, rule-style line).
2. A 5 s static block at 5.4–10.4.
3. Elimination order (A, B, then why) delays the discovery. The payoff comes 12 s after the decision.
4. Even, explanatory voice with a narrow pitch range.
5. A and B close-ups repeat the same move.
6. Lane graphics too thin for phones; X3's rotation not readable in the wide shot.
