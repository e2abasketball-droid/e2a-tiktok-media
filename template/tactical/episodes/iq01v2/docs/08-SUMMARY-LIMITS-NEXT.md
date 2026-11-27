# 08 · Summary, limitations, next experiments

## What changed (V1 → V2)
1. Frame 0 is the question: full 4v4, A/B/C badges and the challenge title, with the camera already moving.
2. A new hook ("Three teammates. One right pass.") puts the rule of the game in the first 2.5 s. Alternative hook B: "One defender gives this whole play away."
3. An honest 2.0 s decision window: a new countdown component whose bar lasts exactly the silence inserted into the voice.
4. No dead freezes: every frozen moment has a camera arc or push. The reveals are reordered A → B → the helper → C, so the answer comes last and lands hardest.
5. Why C, made visible: spotlight on the low helper, a ghost of his starting spot linked to where he ends up (before/after), measured distances on screen (1.4 M, 6.0 M).
6. The C reveal and the kick are one shot. "2ND ROTATION: A STEP LATE" is backed by the measurement (4.0 m at the catch).
7. Seamless loop ("Run it back" lands on the frame-0 framing).
8. Motion: X1 no longer stops dead; he keeps working on the hip and sinks after the kick. 28/28 checks still pass.
9. Subtitles keep their commas. Gold keywords cut from 23 to 18. Mastered to -16 LUFS / -1.5 dBFS.
10. Reusable, data-driven components (scenario.json + generator) for the next IQ episodes.

## Limitations (honest)
- I cannot listen. Narrator choice and mix balance are based on measurements, not hearing. **Please check by ear**, especially the decision silence and the music under "Two seconds".
- In the question frame the players are still small (~100 px) because all 8 must fit in 9:16. The close-ups carry the detail.
- The music is the in-house generated bed (darktech states); it is original but simple.
- X2's pinch pose is still a bit stiff in the A close-up (camera kept at about 10 m so it isn't exposed).
- The metres shown are engine measurements of this animated possession, not of a real game.
- No engagement claims: V2 has no performance data yet. Use analytics-log.csv to compare hook A and hook B.

## Next experiments
- Post hook A as the Reel and hook B as the trial reel. Compare 3 s hold, average watch time, completion and A/B/C comments at 24 h and 72 h.
- Test a 1.5 s versus 2.0 s decision window on EP02.
- A pinned comment with the answer explanation, to measure saves.
- EP02: the same component set, a different help situation (tag on the roller, nail help).
