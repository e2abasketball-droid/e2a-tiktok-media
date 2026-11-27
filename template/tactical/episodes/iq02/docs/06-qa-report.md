# Basketball IQ 02 "Beat the Blitz": QA report (v1, 2026-11-27)

Status: **delivered for owner review, NOT published.** Nothing was scheduled in Metricool.

## Checks that were actually executed

| Check | Tool | Result |
|---|---|---|
| Tactical validation (roster, keyframe fidelity, bounds, speeds/accelerations, collisions, ball, passes with 3D reach, decision lanes A/B/C, truth windows, defensive causes, cut vision cone, finish, legal screen) | `tools/iq_play_validate.py` on the 120 fps engine frame dump | **PASS: 55 pass, 2 warnings, 0 fail** |
| Warning 1 | validator | O5 first step out of the screen 11.4 m/s² (above the 10 m/s² warning line, below the 14 m/s² fail line). Inherent to the owner's keyframes. |
| Warning 2 | validator | X4 braking 10.9 m/s² after K3 (X4 passes through K3 still sliding; a dead stop would need 18-22 m/s²). |
| Decision at the freeze (2.30 s) | validator | A DRIVE BLOCKED, B CORNER BLOCKED, **C CUT OPEN**: matches the script's answer. |
| Engine unit tests | `scripts/test-play.mts` | 27/27 |
| Episode 01 regression | EP01 play tests | 28/28 (EP01 renders unaffected; new engine features are opt-in) |
| Video format | ffprobe | h264 1080x1920, 30 fps, AAC, 32.8 s |
| Video/audio QC | `scripts/qc-video.py` | PASS, I -16.2 LUFS, TP -1.5 dBTP; 1 transient warning at 9.2 s = the intended freeze punch (inspected) |
| Floor-graphics flicker | `scripts/qc-floor-flicker.py` | 984 frames, 0 bad, 0 blinks in the frozen span |
| Narrator | `narrator.py check` + LTAS comparison vs the EP01 V3 reference | OK; master take LTAS 0.992, -0.9 st, range 20.1 st |
| Script vs audio | ElevenLabs Scribe transcription | Matches except one ambiguity (below) |
| Sound effects | edit source | No ball-bounce or dribble SFX. Audio = Nathaniel voice + original generated music bed. |
| Graphics truth | edit `gate()` | Each claim ("two on the ball", "4 on 3", "X4 in the paint") is only on screen inside the validator's truth window |
| Blender scene | bpy 5.3.0, Cycles CPU | Scene opens, 10 players + ball keyed from the dump, 8 cameras; test renders from cameras A and E match the preview |
| Critical self-review of v1 stills | manual (Claude) | Two fixes made in v2: layup camera blocked by the stanchion; "Looks easy" wide shot too small on a phone (push-in added) |

## Checks NOT performed (need a human)

1. **No human listening.** Scribe heard "catch is" where the script says "catches". Needs one listen on headphones.
2. **No human watch on a real phone** (readability of labels, pacing, captions safe zones).
3. **Reveal shot gold-marker jitter** (max 7.5 px, p99 1.13 px, during the rewind/camera transition) was measured but not inspected frame by frame.
4. **Blender scene is a blocking/layout scene with proxy players**, not the final character render. The deformable E2A rig was not used there.
5. **No rig/animation changes** were reviewed by the 3D animation specialist.
6. **Length is 32.8 s**, just under the 33-38 s target. Left as is because the voice take ends there; adding air would mean padding.
7. Alternative key lines (173 cr) were generated but **not spliced** (+4 semitones off the master take). A human can decide if any is better.

## Credits

ElevenLabs on EP02: 609 (master take) + 173 (alt key lines) + 126 + 35 (Scribe) = **943**. Never regenerate the master take.
