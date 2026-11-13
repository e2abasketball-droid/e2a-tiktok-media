# E2A Tactical engine (pilot 01: Elevator Screen)

`Tactical` is a third Remotion composition, next to `Daily` and `Pro`; neither of those is touched.
It turns three kinds of data into a vertical tactical video:

```
plays/*.json (who runs where, ball events)  ─┐
episodes/<id>.json (shots, camera, overlays) ─┼─> tactical-props.mjs -> Remotion "Tactical" -> MP4
episodes/<id>.words.json (narration timing)  ─┘
```

**Honest scope: this is 2.5D, not real 3D.** A pinhole camera projects a FIBA half court
(metres) onto SVG. The floor, lines, paint and the shapes on the floor are true perspective
polygons. The players are flat figures standing upright on their spot, depth-sorted and scaled
by distance (billboards), and their facing is shown on the floor. There are no meshes, no lighting
model and no occlusion other than painter's order.

## Modules (`src/tactical/`)

| File | Role |
| --- | --- |
| `geometry.ts` | FIBA dimensions, `CameraState` (target, dist, pitch 0 = top-down, yaw, fov, shiftY), `makeProjector`, near-plane clipping (`polyPath`, `segPath`), court lines, three-point test |
| `play.ts` | Play data: waypoints `[t, x, y]` -> C2 clamped splines (stops split runs), facing, ball events (hold, dribble, chest/bounce pass, shot and layup arcs, drop after the make), named marks |
| `camera.ts` | Presets (`top`, `topTight`, `broadcast`, `gapClose`, `gapTop`, `split`…), `follow` (keeps a player or the ball framed), `pov` (eye level behind a defender, can be frozen with `at`), eased blends |
| `edit.ts` | The edit as data: shots anchored to narration phrases, time remap keys (real speed, slow motion, freeze, rewind), overlay and SFX types |
| `Court.tsx` | `TacticalCourt` (wood, planks, navy paint, lines, gold baseline stripe, light pool) and `Basket` |
| `Player.tsx` | `PlayerAvatar` (athletic figure without a face; cross-fades to a numbered token in top-down), shadows, ball |
| `overlays.tsx` | World-space graphics: animated routes, trails, gap corridor, closing "doors", separation, pass lane, open space, shot window, switch arrow, rings, tags |
| `screen.tsx` | Screen-space graphics: titles, result stamps, freeze frame, rewind FX, timing bar, decision branch, fork, kicker, logo |
| `TacticalView.tsx` | One viewport: court -> floor overlays -> shadows -> depth-sorted players, ball and basket -> top overlays |
| `Tactical.tsx` | The composition: lays out shots from the narration, split screen, transitions, subtitles (Pro), grain and vignette, voice, music and SFX |

Colours: offence navy with gold trim, defence white with red, ball orange, offensive routes gold,
defensive routes red, open space as a soft gold highlight (`src/pro/brand.ts`).

## Making a new tactical video

1. Write the play(s) in `tactical/plays/` (coordinates in metres, basket at `(0, 1.575)`, +y towards half court).
2. `node --experimental-strip-types scripts/test-tactical.mts tactical/plays/<a>.json …`: speed, acceleration,
   spacing, bounds, ball speed, pass lanes, receivers, three-point catch, openness, legal screens, case-specific checks.
3. Write the episode in `tactical/episodes/` (script, shots anchored to phrases, camera keys, overlays).
4. Generate the narration once (ElevenLabs, **only with the owner's approval of the credits**), transcribe it
   (Scribe), and save `voiceRaw` and `wordsRaw`.
5. `bash scripts/render-tactical.sh tactical/episodes/<id>.json out/<id>.mp4`: tests, pauses inserted into the
   voice (never sped up), music bed, props, engine QC (players in frame, camera smoothness, play clock), render,
   then H.264 encode at -14 LUFS.
6. Skill QC: `python3 -I .claude/skills/e2a-video-editing-intelligence/scripts/apply_plan.py qc out/<id>.mp4 --plan <plan.json>`.

The script never calls ElevenLabs and never publishes anything.

## Tests and QC in this repo

- `scripts/test-tactical.mts`: tactical accuracy (60 checks for the pilot), JSON report with `TACTICAL_REPORT=…`.
- `scripts/qc-tactical.mts`: engine-level QC of every frame of every shot without rendering.
- `scripts/render-tactical.sh`: the full pipeline above.

Final MP4s are **not** committed (heavy binaries); they are delivered as files.
