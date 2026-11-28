# EP02 "Beat the Blitz" V1: forensic motion audit

Owner directive 2026-11-27 23:33Z (Part I). Source audited: the real V1 pipeline at media commit `dbb0e0f`
(play `tactical/plays/iq02-beat-the-blitz.json`, renderer `athleteRenderer: v33`, env `cinema`), not the exported MP4.

## How the audit was made

| Evidence | What it is | File |
|---|---|---|
| Solved skeleton dump | every joint of all 10 players at 60 Hz, computed by the same code path as the render (`scene33.athleteV33`) | `template/scripts/motion-dump-v4.mts` |
| Quantitative validator | foot slide (toe and heel tracked separately), pelvis pops, leg overreach, pelvis collapse, facing vs travel, gaze before a catch, ball inside the body, palm gap, ball teleport | `tools/motion/motion_validate.py` |
| Render A (fixed wide camera, no overlays, real time + x0.5) | the whole possession without cuts | `v2/diagnostics/renderA-v1-fixed-camera.mp4` in the delivery folder |
| Compiled motion script | the primitives the play compiles to (`compile33.ts`): what the engine was asked to do | probe of `compilePlay33` / `buildClip` |

Thresholds in the validator are provisional engineering tolerances, not biomechanical benchmarks. No rigging defect is
claimed from a still image: the skeleton is the procedural V3.3 rig (MakeHuman CC0 mesh), and every defect below is tied
to a measured joint trajectory or to the compiled script.

## Structural defects (what the engine was asked to do was wrong)

Video times are V1 MP4 times (`e2a-basketball-iq-02-beat-the-blitz-v1.mp4`). Owner time = engine time - 1.2 s.

| # | V1 video | Player | Observed | Technical cause | Evidence | Correction (V2) | Validation |
|---|---|---|---|---|---|---|---|
| S1 | 24.9-25.7 | O4 | The "layup" is a standing hop with the ball raised: no gather, no knee drive, no one-hand release, no glass | `compile33` had no layup primitive (`unsupported: no layup primitive yet`) and compiled the layup event to a jump shot, H = 0.22 m, catch-to-release 0.65 s | compiled script; Render A V1 frames at engine 4.55-5.15 | new `layup` primitive: gather on the catch (zero step), knee-drive leg, take-off off the right foot, left-hand release, banked off the glass, landing absorption | Render A V2 stills (gather, knee drive, release, net); `motion_validate` palm gap 0 frames |
| S2 | 19.0-22.9 | O4 | The 45-degree cut starts as one continuous run: no read, no plant, no first-step burst; he simply drifts into the cut | the track has a single `run` segment 1.32-4.66 s; nothing in the script tied the start of the cut to X4 leaving him | compiled script | `look` at X4 before the catch (the read), forced `burst` step (plant wide on the right foot at 2.67 s, the moment O5 catches) | Render A V2; burst step in the step list |
| S3 | 7.4-9.0, 20.5-23.0 | X4 | Steps into the paint in an upright stance with generic arms, overshoots his spot by ~0.3 m and drifts back | no `help` stance; X4 was "moving" the whole time, so the still/stance never applied | track speed 3.5-4.4 s; skeleton | `help` stance (wide, low, wall arms) with `v33still` over planted feet + two short steps back up toward the ball | Render A V2; `motion_validate` X4 clean in the reveal window |
| S4 | 25.2-26.5 | X4 | After the layup he stands, then walks 0.7 m at 1.5 m/s | V1 track tail after K5 | track | late recovery toward the rim and a `contest` action (tactical data change, documented) | tactical validator PASS (layup still uncontested: nearest defender 2.07 m at release) |
| S5 | 0.6-2.5 | X1, X5 | The blitz reads as two defenders standing with generic defence arms | no trap stance or trap arms | compiled script | `trap` stance (wide, low) and `trap` arms (high and wide, active hands) on both trappers | Render A V2 frames 2.2-2.75 |
| S6 | 2.68-3.26 | O5 | Catches running away from the passer: head 95 degrees off the ball 0.4 s before the catch, the ball passes INSIDE his trunk | `catchSpot` is in front of the chest facing the basket while the body faces the path | `gaze_off_ball 95.5`, `ball_in_body` 0.10-0.25 m (5 frames) | `open` segments (chest and hands square to the passer for the last 0.3 s), then a front pivot on the right foot to face up | V2 validator: no gaze or ball-in-body defect |
| S7 | 25.8-26.5 | ball | After the make the ball follows the engine model, not the v33 contact model | `ballV33` falls back to `engineBall` after the last flight | code | unchanged in V2 (the ball drops through the net and is off the focus of the shot); listed as a known limitation | Render C review |
| S8 | whole video | O2, O3, X2, X3 | The four static players stand in `ready` the whole possession | canonical file keeps them static (owner keyframes) | track | unchanged by design (the play is not redesigned); listed as a known limitation | - |

## Measured defects (validator, V1)

Pre-roll rows (owner time below 0) are never shown in the edit (the edit starts at engine 1.3 s).

| Owner t | V1 video | Player | Defect | Value | Note |
|---|---|---|---|---|---|
| 0.267 | 0.31 | O5 | pelvis pop | 81.7 m/s^2 | 1 frame |
| 0.55 | 0.84 | X4 | facing vs travel | 72 deg | 0.13 s: shuffling at 2.5 m/s |
| 0.567 | 0.88 | X4 | pelvis pop | 246.7 m/s^2 | 4 frames: a shuffle at sprint speed (legs at full reach, pelvis dropped 0.2 m) |
| 0.567 | 0.88 | X4 | foot slide | 0.03 m | left toe 1.77-2.12 |
| 0.567 | 0.88 | X4 | leg overreach | 0.999 | 2 frames |
| 0.583 | 0.91 | X5 | leg overreach | 0.999 | 2 frames |
| 1.067 | 2.68 | O5 | gaze off the ball | 95.5 deg | before the catch |
| 1.35-1.417 | 3.15-3.26 | O5 | ball inside the body | 0.10-0.25 m | 5 frames |
| 3.517 | 24.83 | O4 | leg overreach | 0.999 | 1 frame |
| 3.6, 3.683 | 24.96, 25.08 | O4 | pelvis pop | 71.0, 64.1 m/s^2 | the hop "layup" |

Full tables: `iq02v2/validation/motion-validation-v1.md` (+ `.json`).

## What V1 already did well (kept)

Feet are step-planned and planted by `realism-v3-3` (measured slide under 2 cm everywhere except the X4 shuffle);
passes are physical bounce passes validated in 3D against every defender's reach; keyframes K0-K5 reproduce the owner
file within 3 cm.
