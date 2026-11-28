# How to make the next Basketball IQ episode with Motion Engine V4

Order matters: basketball first, motion second, camera and graphics last.

1. **Canonical play** from the owner (keyframes, ball events) -> play generator in `tactical/specs/` (copy
   `_gen-iq02.py`, keep `play()` for the tactical truth and add a `play_v2()`-style function for motion layers;
   set `p["v4"] = True`).
2. **Tactical validator**: `npx tsx scripts/dump-play-frames.mts <play> frames.json` (default 120 fps; a 30 fps dump
   misses keyframes that fall between frames) -> `python3 tools/iq_play_validate.py --canonical ... --play ... --frames ...`.
   Must PASS before anything else.
3. **Motion layers**: defenders get `trap` / `help` / `contest` actions; receivers `open` before a catch facing away
   from the passer; cutters a `look` (the read) and a `burst` (the first step); finishes a `layup` event with `hand`,
   `H`, optional `glass`; a sprint from a standing start gets two quick explicit first steps.
4. **Motion validator**: `npx tsx scripts/motion-dump-v4.mts <play> dump.json 60` ->
   `python3 tools/motion/motion_validate.py --dump dump.json --out r.json --md r.md --offset <pre-roll> [--props ep.json]`.
   Fix every defect inside the edited time range, or document why it stays (thresholds are provisional).
5. **Render A (compulsory)**: `python3 tools/motion/diag_episode.py --play <play> --out diag.json` then
   `npx remotion render src/index.ts Tactical3DV2 renderA.mp4 --props=diag.json --muted --width=1920 --height=1080 ...`.
   Look at it (contact sheets of the x0.5 segment) before editing. The validator did not catch O5's split in EP02;
   the render did.
6. **Edit** (copy `tactical/episodes/_gen-iq02v2.py`): env `arena`, graphics gated by the validator's truth windows,
   reuse the approved narration take (never regenerate), no bounce SFX.
7. **Render B** at half scale (`--scale=0.5`), review stills of every shot, fix, then **Render C** (master), QC
   (`qc-video`, floor flicker, loudness), then deliver. Never publish without the owner.

Regression rule: after any engine change, dump EP01 (`iq01-open-player`) and the V1 plays and compare byte for byte
with the dumps taken before the change.
