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
