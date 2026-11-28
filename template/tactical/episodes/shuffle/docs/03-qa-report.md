# Shuffle Cut V1: QA report

Master `e2a-shuffle-cut-v1.mp4`: 1080x1920, 30 fps, H.264 (CRF 16), AAC 224 kbps 48 kHz, 36.75 s,
sha256 `aead0960a4aadee5...`. Not published.

## Process followed (brief order)

1. Canonical 5v5 model and K0-K6 -> tactical validator PASS before any render.
2. Render A: continuous fixed-camera diagnostic (rig `half`, arena env, real time then x0.5), reviewed with contact
   sheets: the play reads, no player through another, ball always owned or in flight.
3. Edit written; framing checked with `frame-fit` on every frame before rendering.
4. Render B (half scale) reviewed; fixes: BACK SCREEN floor label moved inside the frame in close shots (it was cut at
   the right edge), recap remap had a 0.3 s jump at the rewind (two keys at the same edit time) -> one continuous
   x1.15 replay; FINISH title held to the next line.
5. Render C master (concurrency 1), audio muxed, QC below.

## Automated checks

| Check | Result |
|---|---|
| Tactical validator `tools/shuffle_validate.py` | PASS 65 / 3 warn / 0 fail (`validation/shuffle-tactical-validation.json`) |
| Entry pass O2 -> O3 | OPEN, 0.32 m clearance from X2's reach |
| Pass O3 -> O1 | OPEN, 0.61 m clearance from X3 |
| Screen legality | stationary from 1.25 to 2.70 (owner s), set >= 1.2 m from X1, blind side, behind X1, X1 moves into the screener; O1 never closer than 0.5 m centre to centre to O5 |
| Cut timing | O1 bursts after the screen is set (+0.30 s), change of pace >= 3x |
| Coverage | X1 trails at the catch, X5 stays with O5, X4 home (>= 3 m from O1, <= 1.6 m from O4), X2 high, X3 pressures the passer, no frozen defender |
| Brief anchors | 9 of 10 exactly; X2 moved 0.61 m, documented (`corrections_log`) |
| `qc-video.py` (16 LUFS config) | PASS: -16.0 LUFS integrated, true peak -1.4 dBTP |
| `qc-floor-flicker.py` | 0 bad frames / 1100, 0 blinks in the frozen span |
| `frame-fit` | wide shots (full play, setup wing entry, recap) keep all ten players in the safe band; only 10 frames flagged, all inside the camera move at the start of the recap (27.5-27.8 s) |
| Basket orientation | every camera yaw in [-66, 0]: the basket is at the top of the frame in every shot |
| Narrator | the exact approved voice: Nathaniel, eleven_v4, one take (731 credits), never regenerated; pauses inserted by editing, not by a new take |
| SFX | `autoSfx: false`; no bounce sound, no whooshes, no crowd; music bed = licensed E2A cinematic `cine-10` |

## Known limitations (honest list)

Motion validator (`validation/motion-validation-v1.md`), 8 small defects, none hidden by a cut:

| Owner t | Video (approx.) | Player | Defect | Note |
|---|---|---|---|---|
| 0.38, 0.70, 0.83 | before the visible play | O3, O5, X5 | leg overreach (1 frame each) | root outruns the stride for one frame |
| 1.78 | ~16.6 s (x0.4) | X3 | leg overreach (2 frames) | closeout start, X3 off frame in this shot |
| 3.08, 3.12 | ~25.1 s | O1, X5 | leg overreach (2 frames) | O1 after the catch, X5 off frame |
| 3.50 | ~25.8 s | O1 | palm gap 5.5 cm (1 frame) | at the layup release |
| 3.70 | ~26.1 s | O1 | pelvis pop (1 frame) | landing |

Acceleration warnings (below the 14 m/s^2 limit): O1 12.1 m/s^2 at the burst, X1 13.5 at the contact with O5,
X5 11.4 at his show.

Other notes:
- The hook close-up does not show the ball (it is with O3 on the wing); the full play follows 4 s later.
- In the hook, the BACK SCREEN floor label sits just under the NEVER SEES IT pin for ~1.5 s.
- The 1-3 frame transitions at the start of camera moves can briefly crop edge players (frame-fit list above).
- One designed coverage only; the finish carries the on-screen caption "VS. THIS COVERAGE: X1 CHASES, NO SWITCH".

## Human checks not done

Nobody has watched the master on a phone with sound. Recommended before any publication: one listen for the voice
over the music at the accents ("explodes", "screen.", "layup!") and one watch of the 15-27 s section at full speed.
