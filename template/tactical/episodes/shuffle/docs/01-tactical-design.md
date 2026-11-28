# Shuffle Cut V1: tactical design and canonical data

Owner brief 2026-11-28 09:18Z. Original E2A tactical breakdown (not an IQ challenge).

## One shared model

`tactical/specs/_gen-shuffle.py` is the single source. It writes:

- `tactical/shuffle/e2a_shuffle_cut_v1.json`: the canonical owner-coordinate model, with the brief's anchors
  (`anchors_brief`), the anchors used (`anchors_T0`), designed spots, the owner timeline, keyframes K0-K6 (every
  player's position, root velocity, speed, facing target, state, assignment, plus ball owner, screen state and
  defensive reaction), tracks, ball events, screen legality, the coverage, defensive causes, the corrections log and
  the principle sources.
- `tactical/plays/shuffle-cut-v1.json`: the engine play (Motion Engine V4: `screen`, `help`, `contest`,
  `catchReady`, `burst`, `look`, `layup`). The keyframe positions and velocities in the canonical file are sampled
  from this play's own spline (`scripts/sample-play-positions.mts`), so the data and the animation cannot disagree.

Coordinates: owner x < 0 is the left of the overhead diagram (basket at the top), y in metres from the endline.
Engine x = -owner x; engine t = owner t + 0.6 s.

## Stages (owner time)

| Stage | Time | What happens |
|---|---|---|
| A entry | 0.25-0.85 | O2 -> O3 chest pass. O3 V-cuts to (5.85, 8.30) to meet it. O1 does not move toward the cut. |
| B screen | 1.20-2.72 | O5 walks 1.38 m to (-2.50, 7.30), 1.30 m behind X1 (blind side, more than one step away), feet set at 1.25, stationary until 2.70. |
| C cut | 0.30-2.85 | O1 sets up with a slow step up and in to (-3.30, 9.30) (1.15), waits for the screen, plants and bursts at 1.55 (left foot, wide), brushes O5's outside shoulder at 2.20 (0.55 m centre to centre, never through him), catches at (-1.56, 4.43) at 2.85. |
| D defence | 1.20-3.50 | X1 ball-watches, reacts at 1.72 with two explicit first steps, meets O5 at 2.15, is delayed and trails. X5 shows one step and stays with O5 (no switch). X4 stays home on O4 in the corner, stunts late. X2 stays high on O2. X3 pressures O3 from the baseline side. |
| E pass | 2.10-2.85 | O3 -> O1 bounce pass from the hand, led into O1's stride (lane open, 0.61 m clearance from X3). |
| F finish | 2.85-3.95 | Catch on the move, gather, take-off, left-hand layup off the glass (release 3.50), make 3.95, controlled landing. |

## Corrections (minimum necessary, all logged in `corrections_log`)

1. X2 anchor (0.10, 9.35) -> (-0.40, 9.00), moved 0.61 m: at 0.86 m from O2 the entry pass release was inside X2's
   reach (validator BLOCKED). The smallest tested move that leaves the entry OPEN.
2. O5's screen spot: from his anchor 2.37 m from X1 he cannot screen; he walks to a spot 1.30 m behind X1.
3. X3 stays on his anchor through the entry, then closes out to the baseline side; from the anchor the pass to the
   cutter went through him.
4. O3 V-cuts up the wing to receive the entry away from X3's reach.

## Honest scope

This is ONE designed coverage: X1 chases and no one switches. Against a switch, a top-lock or early weak-side help the
shuffle cut does not produce this layup (it creates other advantages: the screener open, a second cutter). The video
says so on screen at the finish ("VS. THIS COVERAGE: X1 CHASES, NO SWITCH") and in no line claims that every shuffle
cut ends in an open layup.

## Principles used (sources)

- FIBA WABC Coaching Manual Level 3, "The Shuffle" (p.168): ball reversal starts the movement; the first cutter cutting
  off the high-post screen is the basic Shuffle Cut.
- FIBA WABC Level 3, blind (back) screens (p.186): set behind the defender, at least one step away.
- FIBA WABC Level 3 (p.165): the cutter does not move until the screener has set.
- Coach's Clipboard (Shuffle Offense; Cutting and Faking; Princeton Offense): O5 screens for O1, who cuts for the
  feeder's pass and the layup; slow then quick; V-cut plant; hands ready.

## Validation

`tools/shuffle_validate.py` (roster, fidelity incl. brief-anchor corrections, bounds, speed and acceleration,
collisions, ball, passes with the reach envelope, screen legality, cut timing, coverage, finish, causes, truth
windows): PASS, 65 pass / 3 warn / 0 fail. Truth windows (owner s): screen set 1.25-2.71, X1 delayed 2.03-3.16,
O1 behind X1 2.19-3.51. Every on-screen claim in the edit is clipped to these windows (`gate()`).
Reports: `../validation/`.
