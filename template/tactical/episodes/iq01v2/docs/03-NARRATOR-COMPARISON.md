# 03 · Narrator comparison (Deuce, ElevenLabs)

Voice: Deuce (`DaueUomjhh8LFuAV8aGj`). Same test text for all three:
"Three teammates. One right pass. Freeze. Where does the ball go? A, B, or C? You've got two seconds. That's the read. C. Most players watch the ball. Great players watch the help."

**Limitation: I cannot listen.** The choice is based on objective metrics (`voice_metrics.py`: duration, pause structure,
pitch range from F0, loudness range, sibilance energy ratio 5–10 kHz) and Scribe transcripts (all three word-perfect).

| Test | Model / direction | Duration | Pitch range | Sibilance | Reading |
|---|---|---|---|---|---|
| T1 | eleven_v3, [confident][dramatically], caps for stress | 15.2 s | 9.0 st | 0.122 | About as flat as V1 (8.9 st). The drama tags did not add much movement. |
| T2 | eleven_v4, same tags | 15.8 s | 13.6 st | **0.263** | Most pitch movement, but about twice the sibilance of the others, so there is a risk of harsh S's on phone speakers. Rejected. |
| T3 | eleven_v3, [serious] + [slowly] on the answer | 13.3 s | 12.9 st | 0.135 | Pitch movement close to T2, sibilance close to V1, and the tightest pauses. **Chosen.** |
| V1 | eleven_v3 take | – | 8.9 st | 0.115 | Reference. |

Final take: eleven_v3, T3 direction ([serious] opening, [slowly] on "That's the read. C."), default settings (no conservative
changes needed). One take of 34.1 s holds the whole master script plus the hook B line. 492 credits; Scribe 187 credits. The tests
cost 254 + 254 + 198 = 706 credits (their transcripts were free). Total V2 voice spend: 1,385 credits. Post-production, with no regeneration: split at natural gaps, the 2.0 s decision silence inserted,
then `voice-dynamics.py --preserve` (EQ, gentle compression, per-line gain only inside pauses).
