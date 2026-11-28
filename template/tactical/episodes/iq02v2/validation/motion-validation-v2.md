# Motion validation: iq02-beat-the-blitz-v2

Thresholds are provisional engineering tolerances (see THRESH in tools/motion/motion_validate.py), not biomechanical benchmarks.

| kind | count |
|---|---|
| facing_vs_travel | 1 |
| leg_overreach | 5 |
| pelvis_low | 2 |
| pelvis_pop | 5 |

| player | v max | pelvis acc max | contacts | slide max | overreach fr | run knee | stand knee | yaw rate max | cadence |
|---|---|---|---|---|---|---|---|---|---|
| O1 | 1.91 | 18.2 @ 1.9833 | 9 | 0.01 | 0 | None | 60.7 | 278.0 | None |
| O2 | 0.08 | 8.7 @ 5.8333 | 2 | 0.0 | 0 | None | 57.2 | 280.0 | None |
| O3 | 0.31 | 12.2 @ 5.8167 | 3 | 0.001 | 0 | None | 63.4 | 117.0 | None |
| O4 | 3.76 | 64.1 @ 5.1167 | 14 | 0.008 | 1 | 67.1 | 61.0 | 265.0 | 2.69 |
| O5 | 4.16 | 273.3 @ 0.4333 | 10 | 0.019 | 3 | 64.8 | 63.7 | 345.0 | 3.41 |
| X1 | 2.05 | 56.9 @ 5.9 | 8 | 0.012 | 0 | None | 75.6 | 173.0 | None |
| X2 | 0.24 | 27.4 @ 5.8667 | 3 | 0.004 | 0 | None | 77.0 | 276.0 | None |
| X3 | 0.51 | 33.5 @ 5.9333 | 4 | 0.002 | 0 | None | 78.7 | 140.0 | None |
| X4 | 4.75 | 62.8 @ 5 | 14 | 0.005 | 1 | 70.1 | 68.1 | 278.0 | 2.93 |
| X5 | 2.0 | 117.1 @ 0.5 | 13 | 0.016 | 2 | None | 58.6 | 297.0 | None |

| owner t | video | player | defect | value | note |
|---|---|---|---|---|---|
| -0.9 |  | O5 | pelvis_low | 0.392 | 11 frames, pelvis/leg |
| -0.8 |  | X5 | pelvis_low | 0.576 | 6 frames, pelvis/leg |
| -0.783 |  | O5 | pelvis_pop | 273.328 | 3 frames |
| -0.783 |  | O5 | leg_overreach | 0.999 | 2 frames, root outruns the stride |
| -0.717 |  | X5 | leg_overreach | 0.999 | 2 frames, root outruns the stride |
| -0.7 |  | X5 | pelvis_pop | 117.096 | 1 frames |
| -0.667 |  | O5 | pelvis_pop | 105.243 | 3 frames |
| 0.25 | hook 0.28, end 32.69 | O5 | leg_overreach | 0.997 | 1 frames, root outruns the stride |
| 0.917 | hook 2.37, reveal 17.8, end 32.19 | O5 | facing_vs_travel | 119.609 | 16 frames (0.27 s) |
| 3.317 | pass 24.39, lesson 26.7 | O4 | leg_overreach | 0.999 | 1 frames, root outruns the stride |
| 3.783 | pass 25.31, lesson 26.65 | X4 | leg_overreach | 0.998 | 1 frames, root outruns the stride |
| 3.8 | pass 25.33, lesson 26.65 | X4 | pelvis_pop | 62.839 | 1 frames |
| 3.9 | pass 25.48, lesson 26.64 | O4 | pelvis_pop | 64.065 | 2 frames |
