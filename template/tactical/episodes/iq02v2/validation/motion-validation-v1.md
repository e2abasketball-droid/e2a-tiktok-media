# Motion validation: iq02-beat-the-blitz

Thresholds are provisional engineering tolerances (see THRESH in tools/motion/motion_validate.py), not biomechanical benchmarks.

| kind | count |
|---|---|
| ball_in_body | 5 |
| facing_vs_travel | 1 |
| foot_slide | 1 |
| gaze_off_ball | 1 |
| leg_overreach | 6 |
| pelvis_low | 2 |
| pelvis_pop | 7 |

| player | v max | pelvis acc max | contacts | slide max | overreach fr | run knee | stand knee | yaw rate max | cadence |
|---|---|---|---|---|---|---|---|---|---|
| O1 | 1.91 | 18.2 @ 1.9833 | 9 | 0.01 | 0 | None | 60.7 | 278.0 | None |
| O2 | 0.08 | 8.7 @ 5.8333 | 2 | 0.0 | 0 | None | 57.2 | 280.0 | None |
| O3 | 0.31 | 12.2 @ 5.8167 | 3 | 0.001 | 0 | None | 63.4 | 117.0 | None |
| O4 | 3.75 | 71.0 @ 4.8 | 14 | 0.007 | 1 | 64.9 | 59.6 | 266.0 | 3.11 |
| O5 | 4.16 | 274.8 @ 0.4333 | 11 | 0.019 | 3 | 64.8 | 59.5 | 313.0 | 2.73 |
| X1 | 2.05 | 56.9 @ 5.9 | 8 | 0.012 | 0 | None | 75.6 | 173.0 | None |
| X2 | 0.24 | 27.4 @ 5.8667 | 3 | 0.004 | 0 | None | 77.0 | 276.0 | None |
| X3 | 0.51 | 33.5 @ 5.9333 | 4 | 0.002 | 0 | None | 78.7 | 140.0 | None |
| X4 | 4.76 | 246.7 @ 1.7833 | 13 | 0.03 | 2 | 74.2 | 73.3 | 276.0 | 3.24 |
| X5 | 2.0 | 117.1 @ 0.5 | 13 | 0.016 | 4 | None | 58.9 | 297.0 | None |

| owner t | video | player | defect | value | note |
|---|---|---|---|---|---|
| -0.9 |  | O5 | pelvis_low | 0.392 | 11 frames, pelvis/leg |
| -0.8 |  | X5 | pelvis_low | 0.576 | 6 frames, pelvis/leg |
| -0.783 |  | O5 | leg_overreach | 0.999 | 2 frames, root outruns the stride |
| -0.767 |  | O5 | pelvis_pop | 274.767 | 2 frames |
| -0.717 |  | X5 | leg_overreach | 0.999 | 2 frames, root outruns the stride |
| -0.7 |  | X5 | pelvis_pop | 117.096 | 1 frames |
| -0.667 |  | O5 | pelvis_pop | 105.243 | 3 frames |
| 0.267 | hook 0.31, end 32.67 | O5 | pelvis_pop | 81.657 | 1 frames |
| 0.267 | hook 0.31, end 32.67 | O5 | leg_overreach | 0.999 | 1 frames, root outruns the stride |
| 0.55 | hook 0.84, end 32.46 | X4 | facing_vs_travel | 72.046 | 8 frames (0.13 s) |
| 0.567 | hook 0.88, end 32.45 | X4 | pelvis_pop | 246.702 | 4 frames |
| 0.567 | hook 0.88, end 32.45 | X4 | foot_slide | 0.03 | L toe 1.77-2.12 |
| 0.567 | hook 0.88, end 32.45 | X4 | leg_overreach | 0.999 | 2 frames, root outruns the stride |
| 0.583 | hook 0.91, end 32.44 | X5 | leg_overreach | 0.999 | 2 frames, root outruns the stride |
| 1.067 | roll 2.68, reveal 17.76, end 32.07 | O5 | gaze_off_ball | 95.538 | before the catch |
| 1.35 | roll 3.15, reveal 17.69, end 31.86 | O5 | ball_in_body | 0.209 |  |
| 1.367 | roll 3.18, reveal 17.68, end 31.85 | O5 | ball_in_body | 0.115 |  |
| 1.383 | roll 3.21, reveal 17.68, end 31.84 | O5 | ball_in_body | 0.099 |  |
| 1.4 | roll 3.24, reveal 17.68, end 31.83 | O5 | ball_in_body | 0.164 |  |
| 1.417 | roll 3.26, reveal 17.67, end 31.81 | O5 | ball_in_body | 0.248 |  |
| 3.517 | pass 24.83, lesson 26.68 | O4 | leg_overreach | 0.999 | 1 frames, root outruns the stride |
| 3.6 | pass 24.96, lesson 26.67 | O4 | pelvis_pop | 70.961 | 1 frames |
| 3.683 | pass 25.08, lesson 26.66 | O4 | pelvis_pop | 64.139 | 1 frames |
