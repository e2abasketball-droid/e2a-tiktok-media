# 01 · Audit of V1 (e2a-basketball-iq-01-social.mp4, 32.7 s, commit b25d9f5)

How it was checked: frame grabs (contact sheets every 0.5 s plus the key frames), `qc-video.py`, `qc-floor-flicker.py`,
ffmpeg ebur128 loudness, Scribe re-transcription of the voice. **I cannot listen to audio.** Every audio judgement below
comes from measurements (loudness, pitch range, gaps, sibilance ratio, transcript accuracy), not from listening.

| # | Point | Timestamp | Finding | Severity |
|---|---|---|---|---|
| 1 | First frame | 0.0 | Close shot behind the ball handler, plus stamp and a two-line title. Text-heavy, and it does not show the question (no letters, no full floor). As a thumbnail it reads as "a player dribbling". | High |
| 2 | Hook | 0.0–3.8 | The line "He beats his man, and here comes the help" describes the action but asks nothing. The actual question ("Who's open?") lands at 3.8 s. | High |
| 3 | Narrator | whole | Deuce (eleven_v3). Pitch range 8.9 semitones and sibilance 0.115 (measured): even and clear, but the hook is delivered at the same intensity as the explanation. 81/81 words recognised by Scribe. | Medium |
| 4 | Dead air / static time | 3.1–10.4, 14.7–23.2, 29.4–32.7 | About 19 of 32.7 s are frozen frames: question freeze 7.3 s, three reveals 8.5 s, end 3.3 s. The camera barely drifts during them. The 2.1 s THINK silence has no visible deadline. | High |
| 5 | Phone readability | 3.1–10.4 | Question frame: players about 75–110 px tall on 1920. Letters (92 px) readable. Chips duplicate the subtitles, so the eye has three text blocks to read. | Medium |
| 6 | Player scale / angle | whole | Wide, basket-up angle is tactically clear, but the same framing repeats (question, end). Reveal close-ups at 10 m expose X2's pinch pose. | Medium |
| 7 | Motion realism | 0.6–1.9 (play time) | X1 stops dead at about 1.64 s while O1 keeps going (reads as a mannequin). X2's pinch pose looks stiff in close-up. Other motion OK (28/28 physics checks). | Medium |
| 8 | Graphics | whole | Clean E2A palette, but the chips repeat the narration word for word, and there is no spotlight or before/after to show where X3 started. | Medium |
| 9 | Music / dialogue balance | whole | -14.6 LUFS, -1.3 dBTP. Music about 9 dB under the voice, with a silent pad during THINK. Balance is fine. Loudness is hotter than the -16 LUFS target of this brief. | Low |
| 10 | Reveal | 21.2–23.2 | C, the answer, gets only 2.0 s, the shortest reveal, while A and B get 2.5 s and 4.0 s. The payoff is under-weighted. | High |
| 11 | CTA and loop | 29.4–32.7 | "Tell us what you picked" comes after the answer is shown, so it is a weak comment prompt. The end camera differs from the first frame, so the loop is not seamless. | Medium |
| 12 | Subtitles | 3.1–7.0 | The burned-in subtitles drop the commas ("A B OR C?") because the engine strips trailing commas. Gold keyword emphasis is used on 23 words, which is too many to stand out. | Medium |

## Priorities for V2
1. Put the question on frame 0 (frame-0 letters, full floor, title) and ask it in the first 3 s.
2. Replace the passive think beat with an honest, visible 2.0 s decision window.
3. Keep every freeze moving (camera arcs and pushes), and cut the frozen time.
4. Give the answer (C) the biggest beat, and show *why* with a spotlight and a ghost of where the helper started.
5. Close the loop: the last frame equals the first frame.
6. Fix subtitle commas, cut the keyword count, and fix X1's dead stop.
