# 05 · Component library (data-driven, Tactical3DV2)

All components are opt-in screen or 3D items driven by the episode JSON. Generator: `tactical/episodes/_gen-iq01v2.py`.
Scenario data: `tactical/episodes/iq01v2/scenario.json`. To build EP02, write a new play spec and scenario.json and reuse the generator pattern.

| Brief name | Engine item | Where | Data |
|---|---|---|---|
| BasketballIQHook | `open` shot pattern: frame-0 `letter` + `marker` items with negative `from` (fully formed on frame 0), `stamp instant`, `title` | generator | hook lines per variant (`HOOK_LINES`) |
| TacticalFreeze | `remap` flat segment + moving `camera` keys + `freeze` tag | engine (existing) | `decide` mark of the play |
| PlayerChoiceLabels | `letter` screen item (badge, `wrong` = grey + red slash, `right` = gold + glow) | `src/t3d/Tactical3D.tsx` (V1) | `scenario.choices[].letter/player` |
| **DecisionCountdown** (new) | `{type:'countdown', label, from, to, y}`: a gold bar that empties over exactly [from, to] plus a whole-second numeral | `src/t3d/Tactical3D.tsx` | `scenario.decision_window` (must equal the silence inserted into the voice) |
| HelpDefenderSpotlight | `focus` screen vignette + `marker` + `pin` on the helper | engine (existing) | helper id |
| Before/After | `ghost` 3D item (`player`, `t: 0`, `link: true`): translucent column at the starting spot, linked to the live player | engine (existing) | start time |
| RevealSequence | shots `a` / `b` / `c`: `separation` (distance), `passLane` white → red, `blocked`, `openSpace`, `pin` with the measured metres | generator | `scenario.choices[].defender_distance_m` |
| E2ABrandOutro | `end` shot: camera lands on the frame-0 rig (loop), `stamp`, small `logo` (2026 logo) | generator | – |
| Subtitles with commas (new flag) | episode `subtitleCommas: true` keeps list commas ("A, B, or C?") | `src/t3d/screen3d.tsx` | – |
| Mix loudness (new flag) | `voice-dynamics.py --mix-lufs -16` (default stays -14) | `scripts/voice-dynamics.py` | – |

Everything new is opt-in. Existing episodes and the daily task render exactly as before.
