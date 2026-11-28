# Animation resources audit and motion-reference library (Part VII)

Rule followed: nothing was purchased, no licence was assumed, no copyrighted footage was copied into the video.

## Resources checked in this environment (2026-11-28)

| Resource | Status here | Licence position | Used in V2 |
|---|---|---|---|
| E2A rig (`src/t3d/players/e2a-off.rig.json`, `e2a-def.rig.json`) | present; the rig records its source as "MakeHuman base mesh (ara3d-data 1.1.0)" | MakeHuman base mesh assets are published as CC0 (as recorded in the repo and in earlier E2A work); keep the attribution note | yes (all players) |
| Blender + Rigify | Blender is not installed as an application; `bpy` can be pip-installed in a venv (used for EP02 V1 layout scene). No Rigify add-on folder was found on disk | Blender / Rigify are GPL; output files are not restricted. Not verified that the pip `bpy` wheel ships Rigify | no |
| Mixamo | not reachable without an Adobe account; nothing downloaded | Adobe terms not assumed; would need the owner's account and a licence read before any use | no |
| Motion capture data (e.g. CMU Graphics Lab Motion Capture Database) | not downloaded | the CMU site states its own terms; must be read and confirmed by the owner before use | no |
| MPFB (MakeHuman plugin for Blender) | not installed (same as the 2026-11-19 audit) | GPL / CC0 assets | no |

Conclusion: V2 motion is procedural (hand-authored primitives evaluated per frame), on the CC0 mesh already in use.
No external animation clips or mocap were used, so nothing in the export depends on a third-party motion licence.

## Motion-reference library (what each primitive was checked against)

The references are coaching / rules knowledge and our own diagnostic renders, not copied footage. Where a number is
used it is an engineering tolerance chosen for the engine and checked in Render A, not a scientific benchmark.

| Ref | Movement | Source | Licence / rights | How it was used |
|---|---|---|---|---|
| R1 | Layup footwork: gather on the catch, two steps, take-off off the foot opposite the hand, knee drive | FIBA Official Basketball Rules, Art. 25 (travelling, gather and "zero step") as a public rules text | public rules document; cited, not reproduced | step sequence and timing of the `layup` primitive; the tactical validator checks catch-to-release 0.45-0.9 s |
| R2 | Opening to the passer before a catch, front pivot to face up | standard coaching teaching points (catch facing the ball, pivot on the ball of the foot) | general knowledge, no material copied | `open` + `pivot` on O5 |
| R3 | Help-side stance (wide, low, hands out), late recovery | standard coaching teaching points | general knowledge | `help` stance, `wall` arms, X4 recovery |
| R4 | Blitz / trap stance (wide, low, hands high and active) | standard coaching teaching points | general knowledge | `trap` stance and arms |
| R5 | First-step burst out of a read (push foot wide and behind the hips) | standard coaching teaching points | general knowledge | `burst` primitive |
| R6 | E2A Render A diagnostics (fixed wide camera, x0.5) | own renders | E2A-owned | every motion change was accepted or rejected by looking at these |

If the owner wants motion-capture realism next, the cheapest legal route is a dataset whose terms explicitly allow
commercial use, checked clip by clip, or filming E2A's own players (with consent) as reference.
