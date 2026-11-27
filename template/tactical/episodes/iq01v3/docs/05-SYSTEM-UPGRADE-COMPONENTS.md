# 05 · System upgrade and reusable components (V3, 2026-11-27)

## What V3 adds to the engine (opt-in only, nothing changes for other episodes)
| Component | Where | What it does | How to reuse |
|---|---|---|---|
| `passLane.w` | `src/t3d/overlays3d.tsx` | Width scale for pass lanes (ribbon × w, arrow head × √w). Default 1 = unchanged. | `{"type":"passLane","src":"O1","dst":"O3","w":1.6}`. Use 1.5–1.7 for lanes that must read on a phone in a full-floor shot. |
| Course-clean props | `tactical/episodes/iq01v3/tools/course-clean-props.py` | From any finished props: hides the burned-in subtitles (`subtitleHide`), drops big titles and the social countdown, keeps every 3D teaching mark and the voice. | `python3 course-clean-props.py props.json props-course.json`, then render as usual. |
| V3 generator pattern | `tactical/episodes/_gen-iq01v3.py` | Builds the whole edit from the word timings. Shot cuts, the 2.0 s decision window, the freeze, the titles and the music plan (A/B/BREAK states + kick release) all follow the voice. A new take or a new hook needs no hand timing. | Copy it for the next IQ episode, then change `HOOK_LINES`, `BODY`, cameras and the play file. |
| Hook-in-action opening | generator, shot `drive` | The video starts at play t 0.5 with a speed ramp (0.3× → 0.8× → 0.25× into the freeze), not on a static question card. | `HOOK_T0` plus the remap points of the first shot. |
| Misdirection sweep | generator, shot `ab` | One continuous camera move: wrong answer A (lane turns red + measured separation + strike), then wrong answer B (lane blocked), then on to the real answer. | `CAM_A` → `CAM_B` keys and the `lane()` / `sep` items. |
| Loop end | generator, shot `end` | The play rewinds to the hook's first play frame while the camera flies back into the hook rig. Overlays finish 0.4 s early, so the last frame matches frame 0. Measured: court SSIM 0.94 (hook A). | Same remap and camera trick for any episode with a looping ending. |
| One-take, two-hook voice | `tactical/episodes/iq01v3/_voice-iq01v3.py` | One paid take contains both hooks. The script cuts the take at the silences, inserts the honest 2.0 s silence and restores the punctuation Scribe drops. | `HOOKS` / `BODY` ranges + the `FIX` dictionary. |

Reused unchanged from V2: the countdown item, `subtitleCommas`, `voice-dynamics.py --mix-lufs -16`, `darktech_states.py`, `qc-video.py` + `qc-config-16lufs.json`, `qc-floor-flicker.py`, `trial-variant.sh`, `make-srt.py`.

## 3D animation and lighting (Phase 6): what was done and what was not
- **Done:** cameras rebuilt for every shot (low follow in the hook, tilt toward each option, weak-side oblique for the discovery, a C oblique with all four actors, top view for the lesson). `env cinema` kept. A `--env game` test still showed no visible gain, so it was not used. Athletes use the `v33` renderer, which is the HORNS V2 standard.
- **Not done:** no new player model, rig, cloth or motion capture. The X1 chase legs from V2 were kept.
- **Dependencies checked on 2026-11-27 (not assumed):** no `blender` binary, no `bpy` module and no MakeHuman/MPFB in this environment. `tools/blender/` only holds a measurement script. The MakeHuman CC0 player branch (`lab-mpfb-default-player`) is not merged, and its MPFB ZIPs are still pending. Installing Blender plus MPFB means a ~300 MB download. Both are GPL / CC0 licensed and usable commercially for the output. This was **not installed**: the directive asks to report dependencies first.

## Recommended next system steps
1. Promote `passLane.w` into the HORNS V2 standard for full-floor lanes.
2. Turn `_gen-iq01v3.py` into a parameterised `iq-episode` generator (scenario.json in, props out), so EP02+ only needs a play file and a script.
3. Decide on the Blender/MPFB install (owner approval) before any character work.
