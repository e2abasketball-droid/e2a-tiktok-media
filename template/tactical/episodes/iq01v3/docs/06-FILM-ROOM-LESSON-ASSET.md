# 06 · Film Room lesson asset: E2A-IQ-001 V3 (machine-readable version: ../scenario.json)

The course website was **not changed**. This file and the clean render are ready to plug in when the owner decides.

| Field | Value |
|---|---|
| Scenario ID | E2A-IQ-001 · E2A BASKETBALL IQ · Episode 01 · **V3** (V2 = 87a6501, V1 = b25d9f5) |
| Concept | Drive-and-kick read. The receiver whose defender is the low (weak-side) helper is the first kick-out target. |
| Answer | C (O3, left corner) |
| Evidence (measured, play t 1.885 s) | A: X2 1.4 m from O2 (shortest pass, 6.1 m). B: X4 2.1 m from O4 and on the O1→O4 line. C: X3 6.0 m from O3 (pass 8.3 m). X4 is 4.0 m from O3 at the catch. Validator 28/28 (`scripts/test-play.mts`). |
| Limits | True for this possession. An earlier second rotation can change the answer. The video never says the weak corner is always open. |
| Interactive question | Pause at the freeze (edit 4.2 s in the course render, the same edit as hook A). "O1 beats his man to the middle. Who's open: A, B or C?" Per-option feedback is in `scenario.json → quiz`. |
| Teaching points | Read the help, not the ball · the low helper's man is the first kick-out · the easy pass is not always the right pass · check the lane before throwing to the wing · the corner kick beats the second rotation when thrown on time. |
| Lesson line (voice) | "The ball tells you where the play is. The defense tells you where to pass." |
| Renders | Social master `e2a-basketball-iq-01-v3-master-hookA.mp4` (30.8 s) · alt hook `...-v3-alt-hookB.mp4` (32.5 s) · **course clean** `...-v3-course-clean.mp4` (same edit as hook A, no burned subtitles, no big titles, no countdown; A/B/C letters, chips, spotlight, ghost and lanes kept). |
| Captions | `e2a-basketball-iq-01-v3-hookA.srt` (also valid for the course render: same voice and timing) · `...-v3-hookB.srt` |
| Sources | FIBA Basketball Coaching Manual / WABC help-side principles · FIBA court geometry (6.75 m arc, 6.60 m in the corners). |

## Licensing status (what each part is and what is verified)
| Part | Origin | Status |
|---|---|---|
| 3D animation, play, graphics | E2A's own engine (Remotion + three.js) and play file | Own work. Verified. |
| Players | `v33` procedural athlete renderer (own code) | Own work. Verified. No MakeHuman/MPFB assets used. |
| Narrator | ElevenLabs library voice "Nathaniel" (eleven_v4), generated on E2A's ElevenLabs account | Commercial use depends on the account being on a paid plan. Project memory says the owner approved the ElevenLabs licence for new voices. **Assumed, not verified against the plan page in this session.** |
| Music | `darktech_states.py`, generated procedurally by E2A's own script (no samples) | Own work. Verified. |
| Logo | E2A 2026 logo | Owned by E2A. |
| Fonts | The engine's bundled fonts (same as every E2A reel) | Same status as the other E2A reels. Not re-checked here. |

**Course use:** fine for E2A's own Film Room once the ElevenLabs plan point is confirmed. No third-party footage, no player likeness.
