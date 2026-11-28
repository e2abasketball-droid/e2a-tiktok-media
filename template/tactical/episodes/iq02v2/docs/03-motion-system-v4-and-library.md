# E2A Basketball Motion Engine V4: movement system and animation library

V4 is a set of opt-in layers on top of `realism-v3-3` (procedural, step-planned motion on the MakeHuman CC0 rig).
It is not motion capture and does not claim biomechanical accuracy; the numbers below are engineering choices checked
against the motion validator and against Render A, not measured athlete data.

## The five layers (Part II-IV)

| Layer | What decides it | Where |
|---|---|---|
| 1. Locomotion states | `compile33` modes per piece: `stand` (with pose), `run`, `shuffle`, `backpedal`; V4 adds stances `trap` and `help`, and turns a shuffle faster than 2.1 m/s into a run | `compile33.ts` `modeAt` / `pushMove` |
| 2. Foot locking | every step is planned (lift, land, offset); a planted foot never moves except by an explicit pivot about the ball of the foot; V4 places the strides of an `open` run along the travel direction | `library33.ts` steps, `motion33.ts` `footAt0` / `plantedAt` / `anchorOf` |
| 3. Centre of mass and weight transfer | pelvis drop and lean per stance and speed, stride bob, shot phase (gather, dip, load, take-off, flight, landing absorption, recovery) | `library33.ts` drop/lean keys, `motion33.ts` `shotPhase` |
| 4. Turns and plants | heading rate-limited to 6 rad/s, `plant` (braking cut), V4 `burst` (push foot wide and behind, explosive first step), `pivot` | `library33.ts` |
| 5. Basketball actions | catch, pass (chest, bounce, overhead, handoff), jump shot, V4 `layup`, screen, closeout, trap, help, contest, look | `library33.ts` + `motion33.ts` arm modes |

## V4 primitives (play `v33extra` or compiled from actions)

| Primitive | Fields | What it does | Used in EP02 V2 |
|---|---|---|---|
| `layup` | `release`, `H` (apex rise, m), `hand` (1 right, -1 left); ball event may add `glass: [x, z]` | gather on the catch (zero step), short penultimate dip, take-off foot opposite the hand, knee drive of the other leg (foot rides under the knee), one-hand release above the head, off arm shields, follow-through, landing absorption; ball flight banks off the glass | O4 finish: `hand -1`, `H 0.45`, glass at engine x 0.27, z 3.42 |
| `burst` | `t`, `side`, `wide` | forced step: the push foot lands wide (0.3 m) and slightly behind the hips, trunk leans forward after it; the first step of a cut | O4 at 2.67 s (O5's catch) |
| `look` | `t`, `at` (player, `ball`, `ahead`), `b` | head and eyes turn to a target (the read) | O4 reads X4; X4 watches O5 / the ball / too late O4; O5 reads X4, then O4 |
| `open` | `t0`, `t1`, `at`, `max` | the body turns toward a target while the feet keep running the path (opening to the passer) | O5 before the catch |
| `pivot` | `side`, `t0`, `t1`, `dyaw` | rotation on the ball of a planted foot | O5 front pivot after the catch (2.6 rad) |
| stance `trap` | action `{type: 'trap'}` | wide (0.18), low, hands high and wide, active | X1, X5 blitz |
| stance `help` | action `{type: 'help'}` | wide, low (drop 0.23), hands out at chest height ("wall") | X4 in the paint |
| move `arms` | `trap` / `wall` | arms of a shuffle piece inside a trap / help window | X1, X5, X4 |

## Animation library (what exists after V4)

Offence: stand (ready, triple threat, relaxed), run (speed-scaled cadence, stride and arm swing), plant cut, burst,
catch on the move, open to the passer, front pivot, chest / bounce / overhead pass, handoff, jump shot (catch-and-shoot
timing), layup (left or right hand, off the glass or direct), screen set.

Defence: defence stance, shuffle, backpedal, closeout, trap, help (wall), contest, run to recover.

Not in the library yet (honest list): dribble moves and crossovers on the v33 path, euro step and reverse layup,
dunk, rebound box-out, contact between bodies (screens are near-contact, not physical), sliding on a screen.

## How to use it in a new play

1. Write tracks and ball events in the play generator as before; set `p["v4"] = True`.
2. Add actions (`trap`, `help`, `contest`) to defenders; add `v33extra` primitives for reads, bursts, opens, pivots.
3. Put a `layup` ball event with `hand`, `H`, optional `glass`; the compiler builds the gather steps from the take-off.
4. Run `npx tsx scripts/motion-dump-v4.mts <play> dump.json 60` and
   `python3 tools/motion/motion_validate.py --dump dump.json --out r.json --md r.md --offset <pre-roll>`.
5. Render A with `tools/motion/diag_episode.py` (fixed wide camera, x0.5) and look at it before editing.
