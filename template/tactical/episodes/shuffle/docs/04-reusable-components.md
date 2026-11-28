# Shuffle Cut V1: reusable components

New files only; no earlier approved asset was overwritten (EP01/EP02 files untouched).

| Component | File | Reuse |
|---|---|---|
| Canonical play generator (owner coords -> engine play + canonical JSON with keyframes sampled from the engine spline) | `tactical/specs/_gen-shuffle.py` | Template for any screen-and-cut action: designed spots, timeline, tracks, ball events, actions, `v33extra` first steps, corrections log |
| Spline sampler | `scripts/sample-play-positions.mts` | `posAt` / `velAt` of every player at any engine times, as JSON (keyframe data that matches the render exactly) |
| Shuffle validator | `../tools/shuffle_validate.py` | Screen legality (stationary, step distance, blind angle, behind the defender, contact), cut timing (onset after the set, brush distance, burst, change of pace), coverage checks, truth windows, brief-anchor corrections |
| Tactical diagram from the simulation | `../tools/shuffle_diagram.py` | Static PNG/SVG of the formation and the engine paths, owner convention, E2A palette |
| Diagnostic camera rig `half` | `../tools/motion/diag_episode.py` | Fixed half-court camera for Render A of any half-court action |
| Edit generator with gated claims | `tactical/episodes/_gen-shuffle.py` | Camera library A-G for a cut on the left side (yaw in [-66, 0], basket never flips), `SCREENTAG` / `CUTARROW` helpers, truth-window `gate()` |
| Voice assembly | `tactical/episodes/shuffle/_voice-shuffle.py` | Inserts pauses into one take (here 1.9 s so the full play runs in real time) without regenerating the voice |

Graphic overlays used (engine, existing): `screenTag` (back-screen floor stencil), `route` (consumed cut arrow),
`ghostTrail` (pursuit), `separation`, `passLane`, `ballPath`, `vision`, `lockRing`, `glow`, `spot`, `arrow3d`;
screen layer `title` (mask reveal), `stamp`, `pin`, `chip`, `freeze`, `rewind`, `punch`, `flash`, `focus`, `micro`, `logo`.

Pipeline (one command each, from `template/`):

```
python3 tactical/specs/_gen-shuffle.py
npx tsx scripts/dump-play-frames.mts tactical/plays/shuffle-cut-v1.json frames.json 120
python3 ../tools/shuffle_validate.py --canonical tactical/shuffle/e2a_shuffle_cut_v1.json --play tactical/plays/shuffle-cut-v1.json --frames frames.json --out val.json
npx tsx scripts/motion-dump-v4.mts tactical/plays/shuffle-cut-v1.json motion.json 60
python3 ../tools/motion/motion_validate.py --dump motion.json --out mv.json --md mv.md --offset 0.6
python3 tactical/episodes/shuffle/_voice-shuffle.py
python3 ../tools/narrator.py process --voice public/shuffle/voice.wav --words tactical/episodes/shuffle/shuffle.words.json --curve tactical/episodes/shuffle/voice-dynamics.json --out public/shuffle/voice.mix.wav --music public/shuffle/music.wav --mix-out public/shuffle/mix.wav --duration 36.75 --run
python3 tactical/episodes/_gen-shuffle.py --out props.json --fit ep.json
npx remotion render src/index.ts Tactical3DV2 out.mp4 --props=props.json --muted --concurrency=1 --crf=16
ffmpeg -i out.mp4 -i public/shuffle/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 224k -ar 48000 -shortest -movflags +faststart e2a-shuffle-cut-v1.mp4
```
