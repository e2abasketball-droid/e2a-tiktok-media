# EP02 V2: pipeline diagnosis, root causes and fixes

## Pipeline (as found)

```
canonical owner file (K0..K5, ball events)
  -> tactical/specs/_gen-iq02.py            tracks (root paths), actions, ball events      [SIMULATION / TACTICAL]
  -> realism-v3-3/compile33.ts              play -> script of motion primitives per player  [MOTION: what to do]
  -> realism-v3-3/library33.ts buildClip    footsteps, heading, lean, drop, arms, look keys [MOTION: how]
  -> realism-v3-3/motion33.ts               feet (plant, pivot), body, shot phase, arms, ball contact, ball flights
  -> scene33.athleteV33 -> Tactical3D.tsx   skinned MakeHuman (CC0) rig in three.js / Remotion [RENDER]
  -> tactical/episodes/_gen-iq02.py         shots, remaps, cameras, overlays, subtitles     [CAMERA / GRAPHICS / EDIT]
```

The tactical path and the human motion were already two layers (the track is the truth for position and timing; the
motion library decides the body). The V1 defects came from the motion layer missing basketball primitives, not from
the tactical data, with two exceptions (the post-K5 tails of X4 and O4).

## Root causes

1. **Missing primitives.** No layup, no trap or help stance, no read-and-burst start, no catch-facing on the move. The
   compiler fell back to the nearest generic primitive (jump shot, run, defence arms).
2. **Heading-relative stride placement.** A body turned away from its path (opening to the passer) placed its strides
   behind the hips. Found in V2 development: O5 sank to a 0.1 m pelvis in a split (Render A V2 first pass, engine
   2.8-3.4 s). The validator had no check for it; `pelvis_low` was added.
3. **Footwork mode merge.** The 0.6 s piece merge could turn a 2.5 m/s sprint into a shuffle (X4, V1 hook 0.88 s).
4. **Unreachable release point.** The first V4 layup release point was beyond arm reach (palm 9.5 cm off the ball
   for 3 frames before release).
5. **Track tails after K5** made X4 drift and O4 keep running after the layup.

## Fixes (all opt-in: a play without `play.v4` and without the new primitives compiles byte-identically)

| Layer | Change | File |
|---|---|---|
| tactical data | V2 play file `iq02-beat-the-blitz-v2.json` (V1 file untouched); X4 tail: late recovery toward the rim (engine 5.5 s); O4 tail: run ends at the layup landing (5.32 s); layup event: `hand -1`, `H 0.45`, `glass [0.27, 3.42]`; actions `trap` (X1, X5), `help` (X4), `contest` (X4), O5 facing rim then O4 | `tactical/specs/_gen-iq02.py` `play_v2()` (`--v2`) |
| motion primitives | `layup`, `burst`, `look`, `open`, stances `trap` / `help`, move arms `trap` / `wall` | `realism-v3-3/library33.ts` |
| compile | `play.v4`: trap/help stance from actions, layup gather steps from the take-off time, footwork pieces split at trap/help windows, a shuffle piece faster than 2.1 m/s is run instead | `realism-v3-3/compile33.ts` |
| motion evaluation | layup shot phase (short dip, forward trunk in the air), knee-drive swing (foot under the driven knee, relative to the body), one-hand layup arm (`layupOut`: gather -> rip -> release -> follow-through, off arm shields), glass bank flight (two arcs), trap / wall arm modes, strides of an `open` run placed along the travel direction, reachable layup release point | `realism-v3-3/motion33.ts` |
| lighting | env `arena`: one fixed overhead key on the court (shadows straight under the players, identical in every shot), hemisphere + fills, no camera-relative lights | `Court3D.tsx` `ArenaLightsV4`, `Scene.tsx`, `Tactical3D.tsx` |
| validation | skeleton dump, motion validator (new `pelvis_low` check), fixed-camera diagnostic builder | `scripts/motion-dump-v4.mts`, `tools/motion/motion_validate.py`, `tools/motion/diag_episode.py` |

## Data changes and why (Part V: "correct the underlying tactical data and document the changes")

| Change | V1 | V2 | Why |
|---|---|---|---|
| X4 after K5 | drifted 0.7 m at walking speed after the layup | recovers toward the rim, contests late (`contest` action) | a beaten help defender turns and chases; the validator still finds the layup uncontested (2.07 m at release) |
| O4 after K5 | kept travelling 0.5 m after the release (arrived 0.2 s after the landing) | the run ends at the landing (5.32 s) | the body travels in the air and stops on landing |
| layup | `layup` event rendered as a jump shot | left-hand finish off the right foot, banked off the glass | approach from the left wing on the 45 line: the ball stays on the side away from X4, who helps from the middle |
| X4 first steps | 3 long strides for 2 m from a standing start | 2 quick first steps (explicit) then strides | a defender sprinting to help takes short quick first steps |

Keyframes K0-K5 and every ball event time are unchanged. `tools/iq_play_validate.py` on the V2 play: PASS 55 / 2 warn /
0 fail (same as V1).

## Regression

- EP01 (`iq01-open-player`): solved-skeleton dump byte-identical before and after.
- EP02 V1 play: solved-skeleton dump byte-identical before and after (a first draft changed the global `screen` stance
  width; reverted).
