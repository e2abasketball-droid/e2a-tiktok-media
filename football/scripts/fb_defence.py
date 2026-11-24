#!/usr/bin/env python3
"""E2A Football — reusable DEFENSIVE BEHAVIOURS for set pieces (FB-SETPIECE-001 V05+).

A defender's movement is not drawn by hand: it is the reaction to what the attackers and the ball do.
In a spec, a player may carry a list of behaviour phases instead of (or after) waypoints:

    "behaviours": {"D7": [
        {"t0": 0,   "type": "hold",  "p": [45.6, -6.9]},
        {"t0": 0,   "type": "mark",  "target": "A4", "gap": 0.9, "ball": 0.25, "react": 0.25},
        {"t0": 4.9, "type": "zone",  "p": [47.4, -0.6], "shade": "ball", "k": 0.08, "max": 1.6},
        {"t0": 3.0, "type": "press", "target": "A10", "stop": 1.4, "react": 0.2},
        {"t0": 7.0, "type": "to",    "p": [48.0, -3.0]}
    ]}

  hold  — stand on a spot (idle; the engine still adds weight shifts)
  mark  — stay `gap` m goal-side of the mark, biased `ball` (0..1) towards the ball side; follows with a
          reaction delay `react` (s) — the delay is what lets a well-timed run gain a step
  zone  — defend a spot; shade towards the ball (or a player) by k x distance, capped at `max` m
  press — close down a player and stop `stop` m from him on the goal side (pressing trigger)
  chase — run after a player who has gone past (recovery run), `gap` m behind/goal-side
  to    — move to a point (drop, recover a zone)

The desired point is then FOLLOWED by a critically damped second-order body (natural frequency `w`,
default 4 rad/s) whose speed and acceleration are clamped (default 7.6 m/s, 4.8 m/s2). So the result
accelerates, brakes and turns like a person and never teleports, and the rules/physics validator in
fb_motion.py checks it like any other route.
"""
import math

DT = 1 / 120
GOAL = (52.5, 0.0)


def _unit(dx, dy):
    L = math.hypot(dx, dy)
    return (dx / L, dy / L) if L > 1e-9 else (0.0, 0.0)


def rough_ball(events, pos_of, t):
    """ball position good enough to aim shading/bias at (holder, or linear between passer and receiver)"""
    ev = sorted(events, key=lambda e: e['t'])
    cur = ev[0]
    for e in ev:
        if e['t'] <= t:
            cur = e
    if cur['type'] == 'rest':
        return tuple(cur['at'])
    if cur['type'] in ('pass', 'through', 'cross', 'shot') and t < cur.get('t1', cur['t']):
        a = pos_of(cur['by'], cur['t'])
        b = cur.get('target') or pos_of(cur['to'], cur['t1'])
        u = (t - cur['t']) / (cur['t1'] - cur['t'])
        return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    if cur['type'] == 'shot':
        return tuple(cur.get('net') or cur['target'])
    return tuple(pos_of(cur.get('to') or cur['by'], t))


def desired(ph, t, pos_of, ball_at):
    """target point for one behaviour phase at time t"""
    kind = ph['type']
    rt = max(0.0, t - ph.get('react', 0.25))
    if kind in ('hold', 'to'):
        return tuple(ph['p'])
    if kind == 'zone':
        p = ph['p']
        src = ball_at(rt) if ph.get('shade', 'ball') == 'ball' else pos_of(ph['shade'], rt)
        dx, dy = (src[0] - p[0]) * ph.get('k', 0.1), (src[1] - p[1]) * ph.get('k', 0.1)
        L = math.hypot(dx, dy)
        m = ph.get('max', 1.5)
        if L > m:
            dx, dy = dx * m / L, dy * m / L
        return (p[0] + dx, p[1] + dy)
    tgt = pos_of(ph['target'], rt)
    goal = tuple(ph.get('goal', GOAL))
    if kind == 'mark':
        b = ball_at(rt)
        gb = ph.get('ball', 0.25)
        ref = (goal[0] * (1 - gb) + b[0] * gb, goal[1] * (1 - gb) + b[1] * gb)
        ux, uy = _unit(ref[0] - tgt[0], ref[1] - tgt[1])
        g = ph.get('gap', 1.0)
        return (tgt[0] + ux * g, tgt[1] + uy * g)
    if kind == 'press':
        ux, uy = _unit(goal[0] - tgt[0], goal[1] - tgt[1])
        s = ph.get('stop', 1.4)
        return (tgt[0] + ux * s, tgt[1] + uy * s)
    if kind == 'chase':
        ux, uy = _unit(goal[0] - tgt[0], goal[1] - tgt[1])
        g = ph.get('gap', 0.6)
        return (tgt[0] + ux * g, tgt[1] + uy * g)
    raise ValueError(f'unknown behaviour {kind}')


def simulate(phases, duration, pos_of, ball_at, start=None):
    """follow the desired point with a damped, speed/acceleration-limited body; returns 0.1 s track keys"""
    phases = sorted(phases, key=lambda ph: ph['t0'])

    def active(t):
        cur = phases[0]
        for ph in phases:
            if ph['t0'] <= t + 1e-9:
                cur = ph
        return cur

    x = list(start or desired(phases[0], 0.0, pos_of, ball_at))
    v = [0.0, 0.0]
    keys = []
    n = int(round(duration / DT))
    for i in range(n + 1):
        t = i * DT
        if i % 12 == 0:
            keys.append([round(t, 3), round(x[0], 3), round(x[1], 3)])
        ph = active(t)
        d = desired(ph, t, pos_of, ball_at)
        # feed-forward of the target's own velocity: a marker runs WITH his man (no extra lag beyond `react`)
        dp = desired(ph, max(0.0, t - 0.05), pos_of, ball_at) if ph['type'] != 'hold' else d
        vd = ((d[0] - dp[0]) / 0.05, (d[1] - dp[1]) / 0.05) if t >= 0.05 else (0.0, 0.0)
        w = ph.get('w', 4.0)
        vmax = ph.get('vmax', 7.6)
        amax = ph.get('amax', 4.8)
        ax = w * w * (d[0] - x[0]) + 2 * w * (vd[0] - v[0])
        ay = w * w * (d[1] - x[1]) + 2 * w * (vd[1] - v[1])
        A = math.hypot(ax, ay)
        if A > amax:
            ax, ay = ax * amax / A, ay * amax / A
        v[0] += ax * DT
        v[1] += ay * DT
        V = math.hypot(*v)
        if V > vmax:
            v[0], v[1] = v[0] * vmax / V, v[1] * vmax / V
        # standing still: kill sub-centimetre creep so idle players do not drift
        if ph['type'] == 'hold' and math.hypot(d[0] - x[0], d[1] - x[1]) < 0.01 and V < 0.02:
            v = [0.0, 0.0]
        x[0] += v[0] * DT
        x[1] += v[1] * DT
    return keys


def resolve(spec, players_out, track_pos):
    """fill 'track' for every player that has behaviours, in the listed order (a behaviour may react to
    attackers, to waypoint-driven players and to defenders resolved before it)"""
    beh = spec.get('behaviours') or {}
    if not beh:
        return players_out
    byid = {p['id']: p for p in players_out}

    def pos_of(pid, t):
        return track_pos(byid[pid]['track'], t)

    def ball_at(t):
        return rough_ball(spec['ball']['events'], pos_of, t)

    for pid, phases in beh.items():
        start = None
        if phases and phases[0]['type'] in ('hold', 'to'):
            start = phases[0]['p']
        byid[pid]['track'] = simulate(phases, spec['duration'], pos_of, ball_at, start)
    return players_out
