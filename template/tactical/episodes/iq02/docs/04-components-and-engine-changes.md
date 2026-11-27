# Basketball IQ 02: reusable components and engine changes

Everything new is **opt-in**. Plays and episodes that do not set the new flags render exactly as before. EP01 regression: `scripts/test-play.mts tactical/plays/iq01-open-player.json` passed 28/28 after the changes.

## New tools (repo root `tools/`)
| File | What it does | Reuse |
|---|---|---|
| `court_geometry.py` | FIBA geometry in the owner coordinate system (hoop, nail, paint, 3-pt line); owner <-> engine mapping; reach envelope (shoulders at 0.82 H, arm 0.44 H, a 0.35 m lunge that starts after a 0.25 s reaction and grows at 2.5 m/s); lane states OPEN / CONTESTED (< 0.30 m clearance) / BLOCKED; physical bounce pass (two gravity parabolas, COR 0.78) | every Basketball IQ / Film Room episode |
| `iq_play_validate.py` | the deterministic tactical validator: roster, keyframe fidelity, bounds, speed/acceleration, collisions, ball continuity, real passes in 3D vs reach and bodies, the freeze-frame A/B/C lanes, truth windows that gate the graphics, defensive-cause audit, the cut, the finish, legal screen. Exit 1 on any FAIL | gate before every cinematic render |
| `iq_tactical_preview.py` | overhead preview of all 10 players (keyframe panels with trails + the decision panel coloured by lane state), HTML + PNG | sign-off sheet for the owner / coaches |
| `blender/iq_scene_from_play.py` | Blender blocking scene from the validated frame dump: court, 10 proxies with headings, the ball, eight named cameras A-H | staging and camera work in Blender |

## New template pieces
| File | What it does |
|---|---|
| `template/scripts/dump-play-frames.mts` | dumps what the engine DRAWS (positions, velocities, rig body headings, heights, 3D ball) at 120 fps, so validation checks the render's motion rather than the authoring file |
| `template/tactical/iq02/basketball_iq_02_blitz_short_roll.json` | the canonical owner file (keyframes, ball events, decision, truth conditions, defensive causes, future variants, corrections log) |
| `template/tactical/specs/_gen-iq02.py` | canonical -> engine play (`tactical/plays/iq02-beat-the-blitz.json`), keyframes as exact waypoints |
| `template/tactical/episodes/_gen-iq02.py` | the 10-shot edit; `gate()` clips every claim graphic to the validator's truth window |
| `template/tactical/episodes/iq02/_voice-iq02.py` | splits the take mid-gap and inserts only silence (the 2.0 s decision window and beats) |

## Engine changes (opt-in)
| Where | Flag | Effect |
|---|---|---|
| `src/tactical/play.ts` pass event | `ballistic: true` | chest / overhead passes follow a true gravity parabola (rise above the chord g·T²/8); bounce passes use the physical two-parabola bounce (`ballisticBounceZ`, mirrored by `court_geometry.bounce_z`) |
| `src/tactical/play.ts` pass event | `load: s` | overhead load window (default 0.35 s). Added for a clean freeze; not used in the final EP02 play (both passes are bounce passes) |
| `src/t3d/rig.ts` | `load` on the pass | the overhead arm pose starts with the ball when `load` is set |
| `src/t3d/telestration3d-bp.tsx` ballPath | (ballistic passes only) | the bounce ring sits where the physical bounce actually hits the floor |

## Remotion / overlay usage (existing components, no new design copied)
Stamp, title (mask reveal), chip, pin, letter (wrong/right), freeze, punch, countdown, rewind, focus, logo; 3D: marker, motionTrail, lockRing, ghost, vision, route, openSpace, passLane (OPEN / BLOCKED colouring), blocked, separation, ballPath, glow, arrow3d. All of these are E2A's own components (Basketball Visual Standard v1).
