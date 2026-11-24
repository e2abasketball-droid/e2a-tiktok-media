#!/usr/bin/env python3
"""FB-SETPIECE-001 V07 — SHORT CORNER · NEAR-POST DECOY + LATE ARRIVAL · OFF-BALL TIMING (training proposal).

V07 = the V05 play (same defence, same ball, same finish) with subtle PRE-RUN behaviour (A4 feint step away
before the near-post sprint, A6 two slow steps away from the edge defender before his run, A9 small shuffle),
plus the MASTER MATCH TIMELINE: named events (one time source for runs, ball contacts, defensive reactions,
camera and graphics) and a RUN BOOK (trigger, runner, defender who reacts, path, arrival zone, intended effect,
too early / too late) validated by scripts/fb_timeline.py.

Defence designed FIRST (mixed system, 11 v 11), then the attack. Attackers and the keeper follow authored
waypoints (C2 splines); every outfield defender follows reusable BEHAVIOURS (scripts/fb_defence.py) that
react to the attackers and the ball with a reaction delay, so no defender is hand-placed out of the way.

    python3 football/tactical-library/setpieces/gen/FB-SETPIECE-001-V07.gen.py
writes  football/tactical-library/setpieces/FB-SETPIECE-001-V07.spec.json
        football/tactical-library/plays/FB-PLAY-SP001-V07-off-ball-timing.json
and runs fb_motion.py (rules/physics), fb_tactics.py (tactics) and fb_timeline.py (off-ball timing).
"""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SPEC = os.path.join(ROOT, 'tactical-library/setpieces/FB-SETPIECE-001-V07.spec.json')
PLAY = os.path.join(ROOT, 'tactical-library/plays/FB-PLAY-SP001-V07-off-ball-timing.json')
D = 10.4


def W(t, p, v=None):
    d = {'t': t, 'p': list(p)}
    if v:
        d['v'] = list(v)
    return d


def still(p, drift=None, t0=3.0, t1=8.0):
    if not drift:
        return [W(0, p)]
    return [W(0, p), W(t0, p), W(t1, (p[0] + drift[0], p[1] + drift[1]))]


players = [
    ('A1', 'attack', 'GK', 1), ('A2', 'attack', 'REST', 2), ('A3', 'attack', 'REST', 3), ('A4', 'attack', 'DECOY', 4),
    ('A5', 'attack', 'FAR', 5), ('A6', 'attack', 'SCORER', 6), ('A7', 'attack', 'TAKER', 7), ('A8', 'attack', 'EDGE', 8),
    ('A9', 'attack', 'DECOY2', 9), ('A10', 'attack', 'SHORT', 10), ('A11', 'attack', 'FAR', 11),
    ('D1', 'defence', 'GK', 1), ('D2', 'defence', 'POST', 2), ('D3', 'defence', 'ZONE', 3), ('D4', 'defence', 'SHORT', 4),
    ('D5', 'defence', 'ZONE', 5), ('D6', 'defence', 'ZONE', 6), ('D7', 'defence', 'MARK', 7), ('D8', 'defence', 'MARK', 8),
    ('D9', 'defence', 'EDGE', 9), ('D10', 'defence', 'MARK', 10), ('D11', 'defence', 'OUTLET', 11),
]

# ------------------------------------------------------------------ timeline (play seconds)
T_KICK = 3.0      # short corner A7 -> A10
T_RECV = 3.7      # A10 controls
T_RET = 4.3       # A10 returns it (trigger for the box: the ball is now live near the byline)
T_RET1 = 4.95     # A7 receives on the move
T_CUT = 6.5       # cutback A7 -> A6
T_CUT1 = 7.75     # A6 meets it first time
T_SHOT1 = 8.33    # ball crosses the line

M = {
    # A7 taker: run-up, short corner, steps inside along the byline, receives the return, carries to the box corner
    'A7': [W(0, (54.2, -32.3)), W(1.5, (54.2, -32.3)), W(T_KICK, (52.33, -33.59), (-1.7, 0.6)), W(3.6, (51.7, -32.4), (-0.7, 2.4)),
           W(T_RET1, (51.25, -27.6), (-0.3, 3.4)), W(5.75, (50.8, -23.6), (-0.35, 3.4)), W(T_CUT, (50.35, -20.6), (-0.2, 1.6)),
           W(7.3, (50.15, -19.8), (-0.1, 0.4)), W(8.4, (50.1, -19.6))],
    # A10 short option: shows for the ball from the box corner, controls, returns, then drifts in for a rebound
    'A10': [W(0, (46.9, -24.4)), W(1.15, (46.9, -24.4)), W(T_RECV, (48.38, -29.85), (0.25, -0.5)),
            W(T_RET, (48.45, -29.95)), W(T_RET + 0.25, (48.45, -29.95)), W(7.4, (47.2, -24.6)), W(8.6, (46.9, -23.6))],
    # A4 near-post decoy (V07): a small feint step towards the far post, then a REAL sprint to the near post
    'A4': [W(0, (44.3, -8.8)), W(3.0, (44.3, -8.8)), W(3.7, (44.2, -8.5)), W(4.05, (44.2, -8.5)), W(4.6, (44.75, -8.15)),
           W(5.1, (46.15, -7.35)), W(5.55, (47.95, -6.3)), W(5.95, (49.0, -5.6)), W(6.5, (49.45, -5.25)), W(7.2, (49.6, -5.15))],
    # A9 second decoy: attacks the front of the six-yard box a beat later, through the central zone
    'A9': [W(0, (44.2, 1.0)), W(3.9, (44.2, 1.0)), W(4.85, (43.95, 1.3)), W(6.3, (45.7, -1.5), (1.8, -3.0)), W(7.1, (46.8, -3.5), (1.0, -2.0)), W(8.0, (47.2, -4.3), (0.2, -0.4)), W(8.8, (47.3, -4.5))],
    # A6 scorer: second line, starts deep and on the blind side of the edge defender, times a late arrival
    'A6': [W(0, (33.4, 2.6)), W(3.1, (33.4, 2.6)), W(4.4, (32.85, 3.15)), W(5.4, (34.35, 1.75), (1.6, -1.4)), W(6.55, (38.6, -2.3), (4.6, -3.4)),
           W(T_CUT1, (43.25, -6.35), (2.6, -1.3)), W(8.5, (44.4, -6.6), (0.9, -0.1)), W(9.4, (44.7, -6.5))],
    'A5': [W(0, (45.4, 3.4)), W(5.2, (45.4, 3.4)), W(7.4, (46.5, 3.9)), W(8.4, (46.7, 4.0))],
    'A11': [W(0, (46.3, 6.4)), W(5.4, (46.3, 6.4)), W(7.8, (46.5, 6.0))],
    'A8': still((34.6, 10.4), (1.6, -1.8), 5.6, 8.6),
    'A2': still((12.0, -7.0), (1.5, 0.6), 3.5, 8.5),
    'A3': still((12.0, 6.5), (1.5, -0.6), 3.5, 8.5),
    'A1': still((-44.0, 0.0), (3.0, 0.0), 3.0, 9.0),
    # D1 keeper (authored, checked by the keeper validator): centre-near, shifts to the near post as the ball
    # comes along the byline, shuffles back across during the cutback and is SET (feet planted) at the strike
    'D1': [W(0, (51.75, -0.6)), W(4.4, (51.75, -0.6)), W(6.45, (51.85, -2.45)), W(T_CUT + 0.1, (51.85, -2.45)),
           W(7.62, (51.5, -1.55)), W(T_CUT1 + 0.12, (51.48, -1.5)), W(9.2, (51.48, -1.5))],
}

beh = {
    # post player at the near post (keeps the offside line on the goal line, guards the near-post corner)
    'D2': [{'t0': 0, 'type': 'hold', 'p': [52.0, -3.95]}],
    # D4 short-corner defender: 9.15 m+ from the arc, presses the receiver from the inside, beaten by the return,
    # recovers from behind A7 (the pressure that forces an early delivery)
    'D4': [{'t0': 0, 'type': 'hold', 'p': [44.85, -27.05]},
           {'t0': T_KICK, 'type': 'press', 'target': 'A10', 'stop': 1.75, 'goal': [40.0, -24.0], 'react': 0.22, 'w': 3.6},
           {'t0': T_RET + 0.3, 'type': 'chase', 'target': 'A7', 'gap': 1.85, 'goal': [41.0, -31.0], 'react': 0.3, 'w': 3.4, 'vmax': 7.0},
           {'t0': T_CUT + 0.25, 'type': 'to', 'p': [49.3, -22.0], 'w': 2.5}],
    # zonal line on the six-yard box: front post zone, central zone, far zone
    'D3': [{'t0': 0, 'type': 'zone', 'p': [49.1, -7.7], 'shade': 'ball', 'k': 0.07, 'max': 1.2, 'react': 0.3}],
    # D5 central zone: correctly shifts towards the near post when the ball is wide and two runners attack it,
    # then has to come back when the ball goes backwards — the step he cannot recover is the finishing lane
    'D5': [{'t0': 0, 'type': 'zone', 'p': [47.5, -0.6], 'shade': 'ball', 'k': 0.03, 'max': 0.6, 'react': 0.3},
           {'t0': 5.6, 'type': 'to', 'p': [49.1, -2.75], 'w': 3.2},
           {'t0': T_CUT + 0.38, 'type': 'to', 'p': [48.3, -3.3], 'w': 3.0}],
    'D6': [{'t0': 0, 'type': 'zone', 'p': [47.5, 5.6], 'shade': 'ball', 'k': 0.04, 'max': 0.9, 'react': 0.3}],
    # man-markers, goal-side, ball-side biased
    'D7': [{'t0': 0, 'type': 'mark', 'target': 'A4', 'gap': 1.15, 'ball': 0.3, 'react': 0.15}],
    'D8': [{'t0': 0, 'type': 'mark', 'target': 'A9', 'gap': 1.05, 'ball': 0.0, 'react': 0.15}],
    'D10': [{'t0': 0, 'type': 'mark', 'target': 'A5', 'gap': 0.95, 'ball': 0.15, 'react': 0.3}],
    # D9 edge of the box (second balls, cutback zone): ball-oriented; reacts to A6 only once the runner
    # passes his shoulder, then chases
    'D9': [{'t0': 0, 'type': 'zone', 'p': [38.6, -4.4], 'shade': 'ball', 'k': 0.05, 'max': 0.8, 'react': 0.3},
           {'t0': 6.7, 'type': 'chase', 'target': 'A6', 'gap': 1.3, 'goal': [30.0, -2.0], 'react': 0.32, 'w': 3.8, 'amax': 4.2},
           {'t0': T_CUT1 + 0.15, 'type': 'to', 'p': [42.3, -5.6], 'w': 2.6, 'amax': 4.2}],
    'D11': [{'t0': 0, 'type': 'hold', 'p': [24.0, -6.0]}, {'t0': 8.6, 'type': 'to', 'p': [25.2, -5.2], 'w': 2.0}],
}

events = [
    {'t': 0.0, 'type': 'rest', 'at': [52.0, -33.4]},
    {'t': T_KICK, 'type': 'pass', 'by': 'A7', 'to': 'A10', 't1': T_RECV, 'height': 'ground', 'decel': 1.8, 'foot': 'inside'},
    {'t': T_RECV, 'type': 'hold', 'by': 'A10'},
    {'t': T_RET, 'type': 'pass', 'by': 'A10', 'to': 'A7', 't1': T_RET1, 'height': 'ground', 'decel': 1.8, 'foot': 'inside'},
    {'t': T_RET1, 'type': 'dribble', 'by': 'A7'},
    {'t': T_CUT, 'type': 'pass', 'by': 'A7', 'to': 'A6', 't1': T_CUT1, 'height': 'ground', 'decel': 2.0, 'foot': 'inside'},
    {'t': T_CUT1, 'type': 'shot', 'by': 'A6', 't1': T_SHOT1, 'target': [52.75, 3.2], 'lift': 0.1, 'net': [54.05, 3.3], 'foot': 'inside'},
]

tactics = {
    'name': 'SHORT CORNER — NEAR-POST DECOY + LATE ARRIVAL',
    'status': 'training proposal (invented routine, fictional teams; not a real team\'s play)',
    'kick': T_KICK, 'trigger': T_RET, 'delivery': T_CUT, 'strike': T_CUT1,
    'scorer': 'A6', 'keeper': 'D1',
    'marks': [['D7', 'A4'], ['D8', 'A9'], ['D10', 'A5']],
    'zones': ['D3', 'D5', 'D6'], 'post': 'D2', 'short': 'D4', 'edge': 'D9', 'outlet': 'D11',
    'compromised': 'D5', 'late': 'D9',
}

# ------------------------------------------------------------------ MASTER MATCH TIMELINE (V07)
# One time source. Ball events are the authored contacts; run / reaction onsets are the authored starts and are
# re-measured from the built tracks by fb_timeline.py (the video, graphics and camera read these names).
timeline = [
    {'id': 'PLAYER_A_STARTS_APPROACH', 't': 1.5, 'who': ['A7'], 'kind': 'ball', 'what': 'A7 starts the approach to the ball'},
    {'id': 'CORNER_KICK_CONTACT', 't': T_KICK, 'who': ['A7'], 'kind': 'ball', 'what': 'short corner A7 -> A10'},
    {'id': 'DEFENDER_D_STEPS_OUT', 't': None, 'who': ['D4'], 'kind': 'reaction', 'measure': {'onset': 'D4', 'after': T_KICK},
     'what': 'D4 leaves his position to press A10'},
    {'id': 'PLAYER_B_RECEIVES', 't': T_RECV, 'who': ['A10'], 'kind': 'ball', 'what': 'A10 controls, body open to return'},
    {'id': 'DECOY_RUN_BEGINS', 't': 4.05, 'who': ['A4'], 'kind': 'run', 'what': 'A4 sprints to the near post (after a feint step away)'},
    {'id': 'RETURN_PASS_CONTACT', 't': T_RET, 'who': ['A10'], 'kind': 'ball', 'what': 'A10 returns it behind D4 (the box trigger)'},
    {'id': 'MARKER_FOLLOWS_DECOY', 't': None, 'who': ['D7'], 'kind': 'reaction', 'measure': {'onset': 'D7', 'after': 4.1},
     'what': 'D7 goes with A4 (goal-side)'},
    {'id': 'LATE_RUNNER_STARTS', 't': 4.4, 'who': ['A6'], 'kind': 'run', 'what': 'A6 leaves his hiding spot, still slow'},
    {'id': 'SECOND_DECOY_BEGINS', 't': 4.85, 'who': ['A9'], 'kind': 'run', 'what': 'A9 attacks the front of the six-yard box'},
    {'id': 'TAKER_RECEIVES_RETURN', 't': T_RET1, 'who': ['A7'], 'kind': 'ball', 'what': 'A7 receives on the move, facing the box'},
    {'id': 'LATE_RUNNER_ACCELERATES', 't': 5.4, 'who': ['A6'], 'kind': 'run', 'what': 'A6 accelerates from D9\'s blind side'},
    {'id': 'DEFENSIVE_LINE_ADJUSTS', 't': None, 'who': ['D5'], 'kind': 'reaction', 'measure': {'onset': 'D5', 'after': 5.5},
     'what': 'central zone D5 shifts towards the near post where both runs arrive'},
    {'id': 'FINAL_PASS_CONTACT', 't': T_CUT, 'who': ['A7'], 'kind': 'ball', 'what': 'cutback A7 -> space in front of the spot'},
    {'id': 'EDGE_DEFENDER_REACTS', 't': None, 'who': ['D9'], 'kind': 'reaction', 'measure': {'onset': 'D9', 'after': 6.6},
     'what': 'D9 turns and chases A6 (too late)'},
    {'id': 'FINAL_RECEIVER_ARRIVES', 't': T_CUT1, 'who': ['A6'], 'kind': 'ball', 'what': 'A6 meets the cutback in stride'},
    {'id': 'SHOT_CONTACT', 't': T_CUT1, 'who': ['A6'], 'kind': 'ball', 'what': 'first-time side-foot finish, far corner'},
    {'id': 'KEEPER_DIVES', 't': T_CUT1 + 0.17, 'who': ['D1'], 'kind': 'reaction', 'what': 'D1 dives (set at the strike)'},
    {'id': 'BALL_CROSSES_GOAL_LINE', 't': T_SHOT1, 'who': [], 'kind': 'ball', 'what': 'goal'},
]

# RUN BOOK: what every important run is for, and what happens if it is badly timed
runs = [
    {'runner': 'A4', 'role': ['THE DECOY'], 'start': 'DECOY_RUN_BEGINS', 'trigger': 'PLAYER_B_RECEIVES',
     'cue': 'ON THE FIRST TOUCH', 'reacts': 'D7', 'arrive': [48.6, -5.8], 'arrive_by': 6.25, 'r': 1.0,
     'intent': 'pull D7 to the near post and give the zonal line a first runner to cover',
     'early': 'arrives before the return: D7 and D5 settle again before the cutback, the line is not moving when the ball arrives',
     'late': 'arrives after the cutback: the line never moves, the middle stays crowded'},
    {'runner': 'A9', 'role': ['THE SPACE CREATOR'], 'start': 'SECOND_DECOY_BEGINS', 'trigger': 'DECOY_RUN_BEGINS',
     'cue': 'A BEAT LATER', 'reacts': 'D8', 'arrive': [46.8, -3.5], 'arrive_by': 7.1, 'r': 1.0,
     'intent': 'second runner into the same zone: takes D8 and pulls the central zone D5 towards the near post',
     'early': 'both runs arrive together: one movement of the line, D5 can stay central',
     'late': 'D5 is not pulled before the cutback: the finishing lane stays closed'},
    {'runner': 'A6', 'role': ['THE LATE RUNNER', 'THE FINAL RECEIVER'], 'start': 'LATE_RUNNER_STARTS', 'trigger': 'RETURN_PASS_CONTACT',
     'cue': 'ON THE RETURN · WAIT · NOW', 'reacts': 'D9', 'arrive': [43.25, -6.35], 'arrive_by': T_CUT1, 'ball_at': T_CUT1, 'r': 0.6,
     'accel': 'LATE_RUNNER_ACCELERATES',
     'intent': 'arrive in the space the shifted line leaves, from the edge defender\'s blind side, exactly as the ball arrives',
     'early': 'waits in the space: D9 sees him and the zone recovers, the cutback is blocked',
     'late': 'the ball runs past the spot before he gets there (or he meets it off balance)'},
]
roles = {'THE DECOY': ['A4'], 'THE SPACE CREATOR': ['A9', 'A4'], 'THE LATE RUNNER': ['A6'], 'THE FINAL RECEIVER': ['A6'],
         'THE DEFENSIVE REFERENCE': ['D5', 'D9']}

spec = {
    'id': 'FB-PLAY-SP001-V07-off-ball-timing', 'version': 7,
    'title': 'Short corner: near-post decoy + late arrival', 'duration': D,
    'receivePose': True, 'animV2': True, 'headLook': True, 'interp': 'spline',
    'teams': {'attack': {'name': 'Navy (fictional)', 'colour': '#0B1C3D'}, 'defence': {'name': 'White (fictional)', 'colour': '#F4F5F7'}},
    'setPiece': {'type': 'corner', 'corner': [52.5, -34.0], 'side': 'right corner, attacking towards +x',
                 'roles': {'A': 'A7', 'B': 'A10', 'C': 'A4', 'D': 'A9', 'E': 'A6', 'GK': 'D1'},
                 'fragment': '11 v 11, mixed defence (post + 3 zonal + 3 man-markers + short + edge + outlet + keeper).'},
    'tactics': tactics,
    'timeline': timeline,
    'runs': runs,
    'offBallRoles': roles,
    'players': [{'id': i, 'team': t, 'role': r, 'number': n} for i, t, r, n in players],
    'ball': {'events': events},
    'motion': M,
    'behaviours': beh,
}
spec['players'][[p['id'] for p in spec['players']].index('D1')]['actions'] = [{'type': 'dive', 't0': T_CUT1 + 0.17, 't1': T_CUT1 + 0.72, 'side': 1}]

here = os.path.join(ROOT, 'scripts')
# measured reaction times (D4 steps out, D7 follows, D5 shifts, D9 reacts) come from the built tracks
sys.path.insert(0, here)
sys.dont_write_bytecode = True
import fb_motion  # noqa: E402
import fb_timeline  # noqa: E402
built = fb_timeline.resolve(fb_motion.build(json.loads(json.dumps(spec))))
meas = {e['id']: e['t'] for e in built['timeline']}
for e in spec['timeline']:
    e['t'] = meas[e['id']]
spec['timeline'].sort(key=lambda e: e['t'])
json.dump(spec, open(SPEC, 'w'), indent=1)
r1 = subprocess.run([sys.executable, os.path.join(here, 'fb_motion.py'), 'build', SPEC, PLAY], capture_output=True, text=True)
r2 = subprocess.run([sys.executable, os.path.join(here, 'fb_tactics.py'), PLAY], capture_output=True, text=True)
r3 = subprocess.run([sys.executable, os.path.join(here, 'fb_timeline.py'), PLAY], capture_output=True, text=True)
out = r1.stdout + r2.stdout + r3.stdout + r1.stderr + r2.stderr + r3.stderr
print(out if '-v' in sys.argv else '\n'.join(l for l in out.splitlines() if not l.startswith('PASS ')))
sys.exit(r1.returncode or r2.returncode or r3.returncode)
