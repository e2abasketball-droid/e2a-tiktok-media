# Tactical validation: iq02-beat-the-blitz

Verdict: **PASS** (55 pass, 2 warn, 0 fail).

| Section | Check | Status | Value |
|---|---|---|---|
| roster | 10 players on the floor: 5 offence, 5 defence | PASS | 5 O / 5 X |
| roster | every defender guards one distinct attacker | PASS | O1,O2,O3,O4,O5 |
| fidelity | K0..K5 reproduced within 0.03 m (owner coordinates) | PASS | max error 0.007 m (X2@K0) |
| fidelity | O2, O3, X2, X3 stay at their K0 spots (<= 0.15 m stance shifts) | PASS | max 0.122 m |
| bounds | everyone in bounds (centre >= 0.2 m inside the lines) | PASS | ok |
| motion | O1 top speed <= 7.5 m/s | PASS | 1.90 m/s at +0.14 s |
| motion | O2 top speed <= 7.5 m/s | PASS | 0.08 m/s at -0.50 s |
| motion | O3 top speed <= 7.5 m/s | PASS | 0.30 m/s at +3.40 s |
| motion | O4 top speed <= 7.5 m/s | PASS | 3.75 m/s at +2.51 s |
| motion | O5 top speed <= 7.5 m/s | PASS | 4.15 m/s at +0.62 s |
| motion | X1 top speed <= 7.5 m/s | PASS | 2.04 m/s at -0.70 s |
| motion | X2 top speed <= 7.5 m/s | PASS | 0.24 m/s at +1.35 s |
| motion | X3 top speed <= 7.5 m/s | PASS | 0.51 m/s at +3.47 s |
| motion | X4 top speed <= 7.5 m/s | PASS | 4.74 m/s at +1.90 s |
| motion | X5 top speed <= 7.5 m/s | PASS | 1.99 m/s at -1.15 s |
| motion | O1 acceleration <= 14.0 m/s^2 | PASS | 5.0 m/s^2 at +0.77 s |
| motion | O2 acceleration <= 14.0 m/s^2 | PASS | 0.2 m/s^2 at +0.17 s |
| motion | O3 acceleration <= 14.0 m/s^2 | PASS | 1.5 m/s^2 at +3.68 s |
| motion | O4 acceleration <= 14.0 m/s^2 | PASS | 6.5 m/s^2 at +4.21 s |
| motion | O5 acceleration <= 14.0 m/s^2 | WARN | 11.4 m/s^2 at +0.13 s |
| motion | X1 acceleration <= 14.0 m/s^2 | PASS | 6.7 m/s^2 at -0.23 s |
| motion | X2 acceleration <= 14.0 m/s^2 | PASS | 1.0 m/s^2 at +1.68 s |
| motion | X3 acceleration <= 14.0 m/s^2 | PASS | 2.3 m/s^2 at +3.78 s |
| motion | X4 acceleration <= 14.0 m/s^2 | WARN | 10.9 m/s^2 at +2.36 s |
| motion | X5 acceleration <= 14.0 m/s^2 | PASS | 5.9 m/s^2 at +4.22 s |
| collisions | no bodies overlap (>= 0.5 m centre to centre) | PASS | min 0.63 m (X1-X5 at +1.98 s) |
| ball | ball 3D speed <= 16 m/s frame to frame (no teleports) | PASS | max 9.6 m/s |
| ball | ball always in a hand or in flight until the layup | PASS | 0 orphan frames |
| passes | pass O1->O5 clears every reach envelope (OPEN) | PASS | OPEN: closest X1 clearance 0.40 m at +0.88 s, ball 1.06 m high |
| passes | pass O1->O5 never passes through a body | PASS | ok |
| passes | pass O1->O5 speed 6-14 m/s | PASS | 8.1 m/s over 4.79 m |
| passes | pass O1->O5 vertical path is a gravity parabola | PASS | rise over the chord g*T^2/8 = 0.43 m |
| passes | pass O5->O4 clears every reach envelope (OPEN) | PASS | OPEN: closest X4 clearance 0.36 m at +2.88 s, ball 0.78 m high |
| passes | pass O5->O4 never passes through a body | PASS | ok |
| passes | pass O5->O4 speed 6-14 m/s | PASS | 6.2 m/s over 3.54 m |
| passes | pass O5->O4 vertical path is a gravity parabola | PASS | rise over the chord g*T^2/8 = 0.40 m |
| passes | the O5->O4 ball goes around X4 (outside his reach for the whole flight) | PASS | X4 clearance 0.36 m |
| decision | A DRIVE is wrong: X4 is on O5's line to the rim | PASS | X4 0.06 m from the O5->rim line at u=0.41 (BLOCKED); next defender 4.30 m |
| decision | B CORNER is wrong: X3 is home, the O5->O3 lane is not open | PASS | BLOCKED: X3 clearance -1.16 m; X3-O3 1.12 m |
| decision | C CUT is right: the lane to O4's catch spot is OPEN at the freeze | PASS | OPEN: closest X4 clearance 0.41 m |
| decision | C: O4 open at the catch (nearest defender >= 2.0 m) | PASS | X4 2.59 m |
| decision | exactly one option is open, and it is the marked correct one (C) | PASS | A BLOCKED / B BLOCKED / C OPEN |
| truth | 2 ON THE BALL is true during the blitz | PASS | [[0.425, 0.867]] |
| truth | 4 ON 3 is true from the catch through the freeze | PASS | [[1.458, 2.483]] |
| truth | X4 is IN THE PAINT at the freeze | PASS | [[1.683, 5.0]] |
| causes | X1: every movement onset follows a declared cause by >= 0.15 s | PASS | no onsets (holds his spot) |
| causes | X2: every movement onset follows a declared cause by >= 0.15 s | PASS | no onsets (holds his spot) |
| causes | X3: every movement onset follows a declared cause by >= 0.15 s | PASS | no onsets (holds his spot) |
| causes | X4: every movement onset follows a declared cause by >= 0.15 s | PASS | +0.30s <- X5 leaves the roller to blitz: weak-side tag responsibility (+0.25s); +3.41s <- pass O5 -> O4 released: turns, too late (+0.928s) |
| causes | X5: every movement onset follows a declared cause by >= 0.15 s | PASS | +0.15s <- screen set at K0: blitz, leaves O5 to trap O1 (+0.15s); +2.30s <- O1 releases the outlet to O5: recover (+1.44s) |
| cut | O4's cut is a diagonal (45-degree family: 35-60 degrees to the baseline) | PASS | 57 degrees |
| cut | O4 is baseline-side of X4 at the catch (behind him) | PASS | O4 y 3.55 < X4 y 4.03 |
| cut | X4 watches O5 while O4 cuts: O4 outside his focused 120-degree cone from the cut to the release | PASS | 1.55s O4 at 152 deg / O5 at 1 deg; 1.90s O4 at 135 deg / O5 at 10 deg; 2.30s O4 at 76 deg / O5 at 6 deg; 2.48s O4 at 70 deg / O5 at 2 deg |
| finish | layup released within 1.5 m of the hoop | PASS | 0.93 m |
| finish | layup uncontested (nearest defender >= 1.0 m at the release) | PASS | X4 2.07 m |
| finish | catch to layup release 0.45-0.9 s (gather + two steps, no dribble) | PASS | 0.65 s |
| finish | O5's ball screen is legal (stationary <= 0.15 m/s while set) | PASS | 0.000 m/s |
