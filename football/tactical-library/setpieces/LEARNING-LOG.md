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

## FB-SETPIECE-001 V07 — Off-ball timing (2026-11-24, owner directive V07 "off-ball intelligence")

### PERMANENT RULE (owner, applies to every set-piece video from now on)
**THE BALL IS VISIBLE. THE MOVEMENT IS THE STORY.** OFF-BALL FIRST: name the decoy, the space creator, the
late runner, the final receiver and the defensive reference; show WHEN each one moves and WHY. "No necesito más
gráficos porque sí. Necesito gráficos más inteligentes." Research rule unchanged: FIFA Training Centre and IFAB
were DNS-blocked from the sandbox (2026-11-24) → not consulted, rules from memory, NEEDS REVIEW.

### V06 → V07 (problem · measured cause · fix · component · reuse)
Measured with the new `qa/qc_edit.mjs` (same camera + play functions as the video, safe area of a Short).
| # | Owner problem (V06) | Measured cause | Fix | Component | Reuse |
|---|---|---|---|---|---|
| P1 | Camera follows the ball at the corner | kick → delivery: 3.37 s of 5.77 s showed only the corner area, 2.4 s the box | CAMERA A master view behind the attack (azimuth 0, high) holds the box; the corner plays in a 3.9 s inset (CAMERA B) placed on empty grass | `Shot.pip` in FBTactical3D | Every set piece with action far from the box |
| P2 | Timing of the run starts unclear | Labels were names (DECOY, LATE RUN), not cues; no shared clock | MASTER MATCH TIMELINE (18 named events, reactions measured from the tracks) + run cues (ON THE FIRST TOUCH, ON THE RETURN, WAIT, NOW) placed at the measured instants + trigger steps bar driven by play time | spec `timeline`/`runs`, `scripts/fb_timeline.py`, `ev()` in play.ts, screen `cue`/`steps` | Every play: author the timeline first, edit by event names |
| P3 | Too many players/arrows at 8-13 s | All runs same weight; up to 8 pitch graphics + 3 labels | Focus shift (non-protagonists desaturated, `dim` on athlete materials), role-based lines (only the decisive run is solid gold), max 2 labels | `Shot.focus`, `run.role` | Same |
| P4 | Replay too long | 6.6 s replay | 4.4 s reveal from the master angle with ghosts at the real positions of the key moments, numbered 1-2-3 | overlay `ghost` | Same |
| P5 | Arrows too big | Head min 0.32 m half-width, width 0.085-0.11 | Role widths 0.04-0.075, head scale 0.5-0.7 | `ribbon2(headK)` | Same |
| P6 | Finish lacks impact | Behind-net view, the strike not always in frame | CAMERA C behind the shooter (contact, keeper, ball in), micro slow motion by remap only, reverse net-side payoff, gold edge accent | screen `accent` | FB GOAL PAYOFF SYSTEM |
| P7 | Static close | 3.8 s static payoff + 1.2 s end card | 2.9 s rising camera over the live play, title, discreet signature (0 s static) | screen `sig` | Same |
| P8 | Body animation | Runs started from a standstill, no pre-run | Pre-run behaviour: A4 feint step + real sprint (4.8 m/s), A6 hides two slow steps then accelerates, A9 shuffle; all within physics limits | spec V07 | Same |
Also: V06 rewound the play at the cut to the goal camera (8.49 → 7.62 s): 'live' shots now share one clock and the
edit QC fails on any restart/rewind.

Framing rule learnt (replaces the V05 one when the corner is in an inset): with the corner in a picture-in-picture,
the master camera goes BEHIND THE ATTACK (azimuth 0, elevation ~70, focus = box point + 0.75 × late runner) —
the run depth (x 33 → 52.5) becomes the vertical of the Short and players are larger than in the azimuth-90 wide.
The single wide shot (azimuth 90, corner at the bottom) was tested: the late runner is in the safe frame only
5.43 of 7.4 s (fails), so the PiP version was chosen. Check framing with `qc_edit.mjs` BEFORE rendering.

## FB-SETPIECE-001 V09 — Narrated release candidate (2026-11-24, owner directive V09)

Play unchanged (V07 tracks). What V09 adds and how to reuse it:
| # | Owner ask | How it was done | Component | Reuse |
|---|---|---|---|---|
| N1 | Narration synced to the action, voice never slowed | AUDIO-FIRST LOCK: one Deuce take (eleven_v3) is cut at its own silences; each phrase is placed at a video time so its key word lands on its event; the picture clock is then built around the placements. A phrase can be dropped (P4) without touching the others; overlaps fail | `scripts/fb_voice_plan.py`, `episodes/narratedV09.ts` (LIVE_KEYS / REPLAY_KEYS) | Every narrated set piece: generate the take, align (Scribe), place, THEN finish the picture |
| N2 | Match time separate from video time | Two monotone cubic clocks (live, replay), 1/30 s dense remap; live never rewinds | `mono()` + `remapOf()` | Same |
| N3 | Show the space being created, never an already-free zone | FB SPACE CREATION VISUALIZER: state A covered (dashed ring + line to the nearest defender), lit only when that defender has moved away (u from 3.2 → 4.3 m), radius = min(1.7, gap − 2.7 m), off when the runner occupies it or a defender closes it | overlay `space` + `spaceState()`; QC `scripts/fb_space.py` (5/5 PASS) | Any play with a created space |
| N4 | Mobile framing with room for subtitles + YouTube UI | Camera FIT search: closest overview camera keeping the protagonists, the space and the goal mouth inside 64-920 × 230-1310 for the whole window | `qa/fit_cam.mjs` | Fit every master shot before rendering |
| N5 | Corner pace ~0.85× | Rate test clips 1.00/0.90/0.85/0.80 rendered; the voice fixed the final rate at 0.82× (kick → NOW) | `cornerRateTest(k)` | Test pace on short clips first |
| N6 | Subtitles legible, gold only on key words | 'keys' mode: navy band, white text, gold on movement/defender/defence/space/now/timed/time, hidden under titles | `Subtitles mode='keys'` | Same |
| N7 | Close over action, not over the finish | Titles placed on empty grass under the box (y 1060/1150) after a first render put them over the shot and the keeper | episode `close` shot | Check the close frames for title vs ball/keeper overlap |
| N8 | Music without bounces/SFX | In-house library (licensed music/synth/*) through a wrapper that zeroes the FX bus after rendering; shared engine untouched, rotation history not written | `scripts/fb_music.py` | Same |
Lesson: an audio cut must end below about −50 dB; the first plan cut "goes." at −35 dB (raw 7.83 → 7.88 s fixed it).
