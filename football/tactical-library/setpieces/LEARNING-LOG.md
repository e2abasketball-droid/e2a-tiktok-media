# Set Pieces Studio — learning log

One entry per video. Read it before starting the next one: a problem solved here is solved in the shared
Football component, with a test, and must not be solved again.

## FB-SETPIECE-001 — The simple short corner (2026-11-23)

### Capabilities added (reusable)
- **Motion authoring with waypoints** (`scripts/fb_motion.py`): position + velocity per waypoint, quintic
  minimum-jerk segments (zero acceleration at both ends), real standstills. Replaces hand keys whose
  Catmull-Rom tangents drifted around holds.
- **Rules + physics validator** (`fb_motion.py check`): Law 17 (ball in the corner area, 9.15 m from the arc
  until the kick, kicker no double touch), Law 11 (no offside from a corner kick; onside at every later pass),
  pass-lane clearance, speed ≤ 8.5 m/s, acceleration ≤ 6 m/s², no constant-speed plateaus, flagpost clearance.
- **Ground pass physics v2** (`play.ts`, event field `decel`): the pass starts where the ball really is (no
  snap), constant rolling deceleration from a measured value (1.8 m/s²), speed only falls.
- **Absorbed first touch** (`cushion`): the arriving ball keeps its speed for a few cm in front of the foot and
  is absorbed, so the ball never stops dead.
- **Ball at rest** (`rest` event): a set-piece ball lies still on its spot until the kick.
- **Reception pose** (`athlete.tsx`, `receivePose`): receiving foot meets the ball and gives with it, head down.
- **Idle weight shift**: players waiting are never frozen.
- **Corner flagposts** (1.6 m, gold flag) in the shared pitch.
- **Graphics**: `circle` (ghost of a start spot, legal-distance arc), `arrow` (straight option arrow), pass line
  `trail` mode (the line follows the real ball, head at the ball).
- **Camera `lift`**: frames the action above the subtitle band without changing the angle.
- **Motion QC on the real engine** (`qa/qc_play_motion.mjs`): teleport, floating, ball still before the kick,
  contact at the foot, arrival at the foot, rolling deceleration, absorbed touch, turn rate, foot-sliding proxy,
  body interpenetration — without rendering.

### Errors found → fixes
| Error (where found) | Fix (component) | Test |
|---|---|---|
| Accelerations 12–17 m/s² (validator) | longer reaction windows, single minimum-jerk segment for the defender | `test_rules_and_physics_validator` |
| Taker's run-up passed 0.30 m from the flagpost (validator) | run-up from behind the goal line, infield side | flagpost check |
| Ball would snap from the corner spot to the foot at the kick | pass v2 starts from the real ball position | `qc_play_motion` contact check |
| Overview too wide, players tiny, action under the subtitles (stills) | closer cameras + `lift`; subtitles at y 1345 for this episode | visual |
| Pin labels could overlap the logo bug (stills) | pins clamped 90 px below the safe top | visual |
| Stamps collided with the PAUSE tag (stills) | stamps at y 310 | visual |
| V01: pass line drawn ahead of the ball (video review) | `trail` pass line | visual |
| V01: B cropped at the frame edge, D in the foreground covering subtitles (video review) | re-framed shots 03 and 05 | visual |

### Quality limitations (still below standard)
- Players are stylised capsules; the kick is a generic right-foot swing (no inside-foot specific pose, the
  ball is struck from the body's centre line).
- The reception pose is a single generic cushion; no orientated first touch yet.
- No head/eye tracking (the head only pitches); no arm-out balance on turns.
- The defender's press ends in a simple stop; no side-on "jockey" stance.
- The goalkeeper and the near-post defender are static context (by design at level 1).
- Rules text not re-read from the IFAB document in this session (network blocked): NEEDS REVIEW.

### Next video requirements (FB-SETPIECE-002, one-two corner) — only after the owner approves 001
1. Orientated first touch (control away from pressure) as a ball event + pose.
2. Inside-foot pass pose with the ball offset to the striking foot.
3. Change of pace inside a run (waypoints already support it) and a sharper cut with plant foot.
4. Head turn towards the ball for receivers (scanning).
Reuse unchanged: fb_motion.py, pass v2, cushion, rest, cameras A/B with lift, trail lines, QC scripts.

## FB-SETPIECE-001 V03 — The Short Corner Cutback (2026-11-23, after the owner's V02 review)

Owner's 10 problems with V02 → what changed in the reusable engine (problem · technical cause · fix · component · reuse).

| # | Problem | Technical cause | Fix | Component | Reuse |
|---|---|---|---|---|---|
| 1 | Pitch too dark | Night floodlight preset + grass detail texture on a mid-grey base (sRGB 128 ≈ 0.22 linear: the texture divided the grass colour by ~4.5), vignette and top/bottom falloff | `look: 'day'`: sun + sky fill, light detail texture (base 214), natural stripes, crowd-textured stands, sky background, exposure 1.08; `grade: 'clean'` (no vignette) | pitch3d.tsx (Lights/Grass/Surroundings), FBTactical3D.tsx | Any episode: `look: 'day'`, `grade: 'clean'` (defaults keep old episodes identical) |
| 2 | No spatial context | Hook started on a close camera | One continuous opening move (stadium → attacking third → corner) with `spline: true` camera keys (Catmull-Rom, no stop at mid keys) | camera.ts `camSpline` | Every opening / any long camera move |
| 3 | Rigid players | v1 gait: small arm/knee amplitudes, forward gait even when moving sideways/backwards, generic instep kick | `animV2`: speed-driven stride and knee drive, arms bent and swinging, lean from speed + acceleration, level head, backpedal and side-steps, side-foot technique (leg external rotation, plant leg, follow-through), keeper set stance, defender guard stance, keeper dive v2 | athlete.tsx `computePoseV2`, play.ts Kick.inside | `animV2: true` in a play |
| 4 | Too much empty grass | Cameras too far / wrong azimuth for a vertical frame | Cameras chosen so the action runs along the frame's vertical axis (goal at the top) | episode cameras | Rule of thumb in this log |
| 5/9/10 | Too long, no finish, nothing memorable | Level-1 play ended on a pass | New 3-pass play ending in a legal goal + behind-the-goal net angle | spec V03, qc | — |
| 6 | White flashes | `flash` on every shot | Removed (cut on the action) | episode | — |
| 7 | Graphics not professional | Straight ribbons, thick rings, flat zones, big stamps | Graphics v2: Chaikin-smoothed tapered ribbons with notched heads and dark under-stroke, curved arrows, thin proportioned rings, radial soft zones, compact label chips | overlays3d.tsx (`graphicsV2`), screen.tsx `Chip` | `graphicsV2: true` |
| 8 | Irrelevant messages | ONSIDE / 9.15 m / ONE PASS stamps | Only SHORT PASS, DEFENDER STEPS OUT, RETURN, CUTBACK, FINISH | episode | — |

Motion authoring: `interp: 'spline'` (C2 clamped cubic splines per moving chunk) replaced the quintic-per-segment
for V03: the quintic forces zero acceleration at every via point, which produced 10-24 m/s² spikes; the spline
kept every player ≤ 6 m/s². Dribble touches now fade in/out (no ball jump when a carrier slows before a pass).

Validator additions: shot legality (wholly over the line, between the posts, under the bar), shot lane clear of
all outfield players, keeper beaten fairly (reach model 2.15 m with a dive), dive after the strike, pass lanes
clear of team-mates. Engine QC additions: goal really crosses the line in the rendered ball, net hit + ball
settles, ball never passes through a player, shot speed ≤ 32 m/s.

## FB-SETPIECE-001 V05 — Near-post decoy + late arrival (2026-11-23, owner directive V05 "first-team standard")

### PERMANENT METHOD (owner rule, applies to every set-piece video from now on)
TACTICAL RESEARCH → REALISTIC DEFENSIVE STRUCTURE → OFFENSIVE ROUTINE DESIGN → DEFENSIVE CHALLENGE →
TACTICAL VALIDATION → 3D ANIMATION → CINEMATIC EDITING → QUALITY CONTROL → HUMAN REVIEW.
"A simple, credible play perfectly represented beats a spectacular play that would never work against an organised defence."
Research rule: only cite sources actually read; if a source cannot be reached, say so (V05: thefa.com, theifab.com,
spielverlagerung.com and elitesoccercoaching.net all failed DNS from the sandbox → rules from memory, NEEDS REVIEW).

### V04 → V05 (problem · cause · fix · component · reuse)
| # | Owner problem (V04) | Technical cause | Fix | Component | Reuse |
|---|---|---|---|---|---|
| 01 | Too much space in the box | Defenders were hand-placed waypoints; nothing tied them to the attackers | Defence designed first: mixed system (post + 3 zones + 3 markers + short + edge + outlet + GK), 9 in the box at the kick; every outfield defender driven by behaviours | `scripts/fb_defence.py` (`behaviours` in a spec) | Any set piece: write `behaviours` instead of defender waypoints |
| 02 | Passive defenders | No reaction model | `mark` (goal-side, ball-biased, reaction delay), `zone` (shade towards ball/player, capped), `press` (stop short, inside), `chase` (recovery run), `to`; critically damped follower with velocity feed-forward, speed/accel clamps | fb_defence.py | Same |
| 03 | Goal looked predetermined | Scorer free from the start | Scorer starts outside the box; advantage comes from a shift (D5 1.75 m to the near post) + a late run from the edge defender's blind side; 3.0 m at the strike, window 1.4 s | spec V05 + `scripts/fb_tactics.py` | Tactical validator on every play with a `tactics` block |
| 04 | No collective coordination | Runs were independent | Trigger = the return pass; decoy 1 → decoy 2 (+0.5 s) → late runner, timed to the delivery | spec V05 | — |
| 05 | Finish / keeper not credible | Keeper shift arbitrary | Keeper near post with the ball wide, shuffles back during the cutback, SET at the strike (0.18 m/s), 0.25 m off the bisector, dive 0.17 s after the strike; low far-corner shot 0.46 m inside the post at 23 m/s | fb_tactics keeper checks | Every goal |
| 06 | Replay too long | 7.2 s + payoff overview | 6.6 s analytical replay from above (same orientation as the opening), one 0.6 s pause on the cutback | episode | — |
| 07 | Graphics descriptive | Only passes/runs/zone | Marking links, red defensive shift + ghost start ring, orientation cone, passing window, finishing lane, runs drawn in play time (timing) | overlays3d.tsx `link`, `cone`, `run.trail` | `graphicsV2` episodes |

Other engine changes: `headLook` (heads turn to the ball, fade when it is behind; old plays unchanged),
shot-lane check starts 0.5 m in front of the strike (a player behind the shooter cannot block), generator kept in
the repo (`tactical-library/setpieces/gen/FB-SETPIECE-001-V05.gen.py`) so the spec is reproducible.

Framing rule learnt: for a corner from the right, an overhead at azimuth 90 (camera on the corner side, looking
across the pitch) puts the goal line vertical on the right, the corner at the bottom and the box in the middle —
passer, shifted line, late runner and finishing zone all fit the vertical frame. Azimuth 60-80 loses the passer.
