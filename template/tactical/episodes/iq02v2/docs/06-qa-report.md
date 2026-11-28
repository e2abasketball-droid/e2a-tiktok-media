# EP02 "Beat the Blitz" V2: QA report (Part XIII-XIV)

Final file: `e2a-basketball-iq-02-beat-the-blitz-v2.mp4` (1080x1920, 30 fps, 32.8 s, H.264 + AAC 48 kHz).
V1 is preserved unchanged (file, play, generator, engine behaviour for the V1 play). Not published.

## Render stages

| Stage | What | Result |
|---|---|---|
| Render A V1 | fixed wide camera 1920x1080, no overlays, real time + x0.5, pre-change engine | `renderA-v1-fixed-camera.mp4`; the basis of the V1 audit |
| Render A V2 pass 1 | same camera, V4 motion | reviewed: layup, trap, help, burst rendered; **O5 collapsed into a split after the catch** (engine 2.8-3.4 s) -> fixed (stride placement), new validator check |
| Render A V2 final | same camera after the fixes | `renderA-v2-fixed-camera.mp4`; reviewed on contact sheets of the x0.5 segment (catch, pivot, cut, gather, take-off, release, landing, X4 recovery) |
| Render B | the full V2 edit at half resolution (540x960) | reviewed shot by shot; changes: one floor graphic removed from the reveal (too busy). It also exposed a renderer fault: ~6 % of frames tiled when four browser tabs render in parallel (`qc-floor-flicker`: 59 bad frames). Kept as the preview of record, with that fault |
| Render C | the master, single browser tab | `qc-floor-flicker`: 984 frames, **0 bad**, 0 blinks in the frozen decision window |

## Checks

| Check | Tool | Result |
|---|---|---|
| Tactical truth (keyframes, speeds, collisions, real passes in 3D, A/B/C lanes, truth windows, the cut, the finish) | `tools/iq_play_validate.py` on the V2 play | **PASS 55 / 2 warn / 0 fail** (warns: O5 11.4 m/s^2 and X4 10.9 m/s^2 acceleration, under the 14 limit; same class as V1) |
| Generic play checks | `scripts/test-play.mts` | V2 27/27, EP01 28/28 |
| Motion (skeleton) | `tools/motion/motion_validate.py` | V1: 23 defects, 16 inside the edit. V2: 13, **6 inside the edit**, all 1-2 frames (see below) |
| Regression | skeleton dumps compared byte for byte | EP01 identical; EP02 V1 play identical |
| Video / audio | `scripts/qc-video.py` (-16 LUFS config) | **PASS**: I -16.2 LUFS, TP -1.2 dBTP; 1 transient warning = the intended freeze punch (same as V1) |
| Floor graphics flicker | `scripts/qc-floor-flicker.py` | 0 bad frames, 0 blinks |
| Audio content | edit source | same Nathaniel take as V1 (not regenerated), same music bed, no ball-bounce SFX |

### Motion defects left inside the edit (V2)

| Owner t | Video | Player | Defect | Why it stays |
|---|---|---|---|---|
| 0.25 | 0.28 | O5 | leg reach 0.997, 1 frame | under one frame at the hook's speed-up; not visible in review |
| 0.917 | 2.37 | O5 | facing vs travel 120 deg, 0.27 s | intended: he opens to the passer while rolling (the V1 defect was the opposite) |
| 3.317 | 24.39 | O4 | leg reach 0.999, 1 frame | last stride into the gather |
| 3.783, 3.8 | 25.31 | X4 | leg reach 0.998 + pelvis 62.8 m/s^2, 1 frame | start of his late recovery |
| 3.9 | 25.48 | O4 | pelvis 64.1 m/s^2, 2 frames | in the air after the release: a kink where the follow-through hands over to the descent; limit is 60 |

Thresholds are provisional engineering tolerances, not biomechanical benchmarks.

## Final checklist

- [x] canonical play, 10 players and every keyframe kept; data changes documented (`02-root-cause-and-fixes.md`)
- [x] O4: read (look at X4), plant and first-step burst at the defensive trigger (O5's catch), not before it
- [x] finish: gather on the catch, two steps, take-off off the right foot, knee drive, left-hand release protected from X4, glass bank, landing
- [x] blitz: two trappers in a trap stance with active hands; X4: help stance, then a late recovery
- [x] ball: held in the hand until release (palm gap fixed), physical bounce passes, no teleport
- [x] fixed overhead arena light, identical in every shot
- [x] Render A, B and C made and inspected
- [x] same narrator take, no bounce SFX, -16 LUFS
- [ ] human listen / watch on a phone by the owner (not done by me)

## Uncertainties and known limits

1. Stylised real-time 3D, not photoreal. No motion blur, simple skin and cloth.
2. The procedural motion is not motion capture. It reads as basketball in review but is not validated against measured athlete data.
3. The four static players (O2, O3, X2, X3) stand still as in the canonical file; they get no weight shifts.
4. After the make the ball uses the engine's rim/net model, not the hand-contact model (as V1).
5. The wide shots (freeze, 4 on 3, lesson) keep V1 framing; on a phone the players there are small.
6. The renderer fault with four parallel tabs is not root-caused in the engine; renders are now made with one tab (`--concurrency=1`), which was as fast here because the software GPU process is the bottleneck.
