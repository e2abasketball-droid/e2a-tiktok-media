# Basketball IQ 02: Blender scene

**What exists:** `iq02-beat-the-blitz-scene.blend` (Blender 5.3 file, built with `bpy` 5.3.0 installed from PyPI in the container) from `tools/blender/iq_scene_from_play.py`.
- FIBA half court (floor, endline, sidelines, lane, 3-point line, free-throw circle), hoop at 3.05 m, backboard.
- 10 player proxies (capsule body, head, chest marker for the body heading). Heights come from the engine (`PLAYER_HEIGHTS`). Offence is white/gold, defence navy/red.
- The ball (radius 0.121 m).
- All of it keyed at 30 fps for 187 frames from the **validated** engine frame dump: exactly the motion that passed `tools/iq_play_validate.py`. Marker `K0` at frame 37.
- The directive's eight cameras as named static views: A overhead tactical, B high wide, C behind the ball handler, D behind the short roll, E weak-side wing, F baseline, G low corner, H X4 isolation.
- Coordinates: engine frame (right-handed, like Blender). Camera A looks straight down with the basket at the top, so it matches the owner's diagram (ball side on the right).

**Verified (executed):** the file was built, reopened, and rendered with Cycles CPU from cameras A and E at the freeze frame (frame 106). X4 sits at engine (-0.35, 4.05) = owner (0.35, 4.05) = K3.

**Not done, and why:**
- This is a **blocking/layout** scene with proxies, not the final character render. The deformable E2A player rig (`tools/blender/build_blender.py`) needs the MakeHuman/MPFB assets, which are not in this container, and the v1 video is rendered by the Remotion/three.js engine (the E2A production renderer).
- Workbench/EEVEE cannot run here (no EGL/GPU), so only Cycles CPU test renders were possible.
- No character-animation changes were made to the rig for EP02. The animation quality is the current engine (v33 renderer, realism 3).
