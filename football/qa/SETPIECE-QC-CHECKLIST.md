# E2A Football — Set-piece QC checklist (FB-SETPIECE-xxx)

States: **PASS** verified · **FAIL** error found · **NEEDS REVIEW** needs a visual/human judgement · **NOT TESTED** could not be checked.
Every row says HOW it was checked: `auto` (script), `visual` (frames inspected by Claude), `owner` (owner's review).
A video is never "approved" on automatic checks alone: the owner's review is the last row.

| # | Dimension | Check | How |
|---|---|---|---|
| 1.1 | Tactical | Ball inside the corner area; opponents ≥ 9.15 m from the arc until the kick; kicker does not touch twice; onside at every later pass; pass lanes clear (≥ 1.2 m) | auto `scripts/fb_motion.py check` |
| 1.2 | Tactical | Defensive reaction plausible (timing after the kick, path, final spacing) | visual + owner |
| 1.3 | Tactical | Script claims match the animation (no invented goal/chance) | visual (script vs frames) |
| 1.4 | Tactical | Rules text checked against the current IFAB edition | owner / NOT TESTED if offline |
| 2.1 | Animation | No teleport, no floating, ball still before the kick, contact at the foot, arrival at the foot, rolling deceleration, absorbed first touch | auto `qa/qc_play_motion.mjs` |
| 2.2 | Animation | No instant turns, gait follows distance (foot-sliding proxy), no interpenetration, speed limits, acceleration limits, no constant-speed plateaus, clear of flagposts | auto (both scripts) |
| 2.3 | Animation | Visible foot sliding, foot through the ground, pose pops | visual (stills at 15 fps around contacts) |
| 2.4 | Animation | Spatial continuity across cuts (same positions in consecutive shots at the same play time) | auto (remaps) + visual |
| 3.1 | Visual | Pitch credible, lines crisp, corner area and flag correct, lighting/shadows coherent | visual |
| 3.2 | Visual | Players readable on a phone; framing inside the safe area (top 220, bottom 440, right 160) | visual |
| 3.3 | Visual | Graphics legible, never two competing graphics, palette only navy/gold/deep gold/white (+ red for the defence) | visual |
| 4.1 | Editorial | Hook in frame 1 (no black, no logo intro); visual question; controlled reveal; clear payoff; no dead pauses | visual + owner |
| 5.1 | Technical | MP4 plays, 1080×1920, ≥ 30 fps, H.264 yuv420p, duration in range, no black/frozen-by-error frames, no 1-frame pops | auto `qa/qc_render.py` |
| 5.2 | Technical | Subtitles/text never cut or overlapping the logo/tag | visual |
| 6 | Owner | The owner approves the video | owner |
