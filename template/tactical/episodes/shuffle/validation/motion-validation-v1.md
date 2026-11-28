# Motion validation: shuffle-cut-v1

Thresholds are provisional engineering tolerances (see THRESH in tools/motion/motion_validate.py), not biomechanical benchmarks.

| kind | count |
|---|---|
| leg_overreach | 6 |
| palm_gap | 1 |
| pelvis_pop | 1 |

| player | v max | pelvis acc max | contacts | slide max | overreach fr | run knee | stand knee | yaw rate max | cadence |
|---|---|---|---|---|---|---|---|---|---|
| O1 | 5.16 | 353.5 @ 3.7 | 14 | 0.01 | 2 | 75.2 | 57.2 | 280.0 | 3.75 |
| O2 | 1.77 | 18.5 @ 0.5833 | 6 | 0.008 | 0 | None | 53.2 | 271.0 | None |
| O3 | 1.93 | 11.9 @ 1.65 | 5 | 0.001 | 1 | None | 65.2 | 348.0 | None |
| O4 | 0.28 | 14.4 @ 5.0833 | 4 | 0.002 | 0 | None | 61.9 | 52.0 | None |
| O5 | 2.18 | 18.7 @ 1.3333 | 6 | 0.008 | 1 | None | 60.5 | 272.0 | None |
| X1 | 6.26 | 41.9 @ 0.0167 | 17 | 0.02 | 0 | 74.0 | 70.4 | 291.0 | 3.45 |
| X2 | 1.55 | 48.3 @ 3.2 | 8 | 0.007 | 0 | None | 62.8 | 269.0 | None |
| X3 | 2.69 | 35.6 @ 2.4 | 8 | 0.006 | 2 | 56.9 | 62.8 | 275.0 | 1.94 |
| X4 | 1.54 | 34.6 @ 5.1167 | 4 | 0.011 | 0 | None | 78.0 | 274.0 | None |
| X5 | 2.63 | 30.7 @ 3.5167 | 11 | 0.012 | 3 | None | 64.3 | 347.0 | 2.93 |

| owner t | video | player | defect | value | note |
|---|---|---|---|---|---|
| 0.383 |  | O3 | leg_overreach | 0.995 | 1 frames, root outruns the stride |
| 0.7 |  | O5 | leg_overreach | 0.999 | 1 frames, root outruns the stride |
| 0.833 |  | X5 | leg_overreach | 0.999 | 1 frames, root outruns the stride |
| 1.783 |  | X3 | leg_overreach | 0.999 | 2 frames, root outruns the stride |
| 3.083 |  | O1 | leg_overreach | 0.999 | 2 frames, root outruns the stride |
| 3.117 |  | X5 | leg_overreach | 0.999 | 2 frames, root outruns the stride |
| 3.5 |  | O1 | palm_gap | 0.055 | 1 frames |
| 3.7 |  | O1 | pelvis_pop | 67.166 | 1 frames |
