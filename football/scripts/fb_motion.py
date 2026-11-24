#!/usr/bin/env python3
"""E2A Football — motion authoring for set-piece plays (FB-SETPIECE-001+).

Instead of hand-placing sparse keys (Catmull-Rom tangents overshoot around holds), each player is
described by WAYPOINTS with a position AND a velocity. Between two waypoints the motion is a quintic
Hermite with zero acceleration at both ends (minimum-jerk family): players accelerate and brake
progressively, never at constant speed, and a hold is a true standstill. The result is sampled every
0.1 s into the `track` keys that play.ts already interpolates.

`validate()` checks the physical limits (speed, acceleration, turn) and the set-piece rules that can be
computed from the data (corner arc, 9.15 m, onside at each pass, defender clearance of a pass lane).

Usage:  python3 football/scripts/fb_motion.py build <spec.json> <out_play.json>
        python3 football/scripts/fb_motion.py check <play.json>
"""
import json
import math
import sys

DT_KEYS = 0.1
HL, HW = 52.5, 34.0


def quintic(p0, v0, p1, v1, T, u):
    """position at u in [0,1] of a quintic with end positions/velocities and zero end accelerations"""
    u2, u3, u4, u5 = u * u, u ** 3, u ** 4, u ** 5
    h0 = 1 - 10 * u3 + 15 * u4 - 6 * u5
    h1 = u - 6 * u3 + 8 * u4 - 3 * u5
    h4 = 10 * u3 - 15 * u4 + 6 * u5
    h5 = -4 * u3 + 7 * u4 - 3 * u5
    return [h0 * p0[k] + h1 * T * v0[k] + h4 * p1[k] + h5 * T * v1[k] for k in range(2)]


def sample_waypoints(wps, duration):
    """wps: [{t, p:[x,y], v:[vx,vy]}] sorted; holds before the first and after the last"""
    keys = []
    n = int(round(duration / DT_KEYS))
    for i in range(n + 1):
        t = i * DT_KEYS
        if t <= wps[0]['t']:
            p = wps[0]['p']
        elif t >= wps[-1]['t']:
            p = wps[-1]['p']
        else:
            j = max(k for k in range(len(wps) - 1) if wps[k]['t'] <= t)
            a, b = wps[j], wps[j + 1]
            T = b['t'] - a['t']
            p = quintic(a['p'], a.get('v', [0, 0]), b['p'], b.get('v', [0, 0]), T, (t - a['t']) / T)
        keys.append([round(t, 3), round(p[0], 3), round(p[1], 3)])
    return keys


def _clamped_spline(ts, xs, v0, v1):
    """C2 cubic spline through (ts, xs) with end velocities v0, v1; returns the knot velocities"""
    n = len(ts)
    h = [ts[i + 1] - ts[i] for i in range(n - 1)]
    # unknowns: second derivatives M_i; clamped end conditions
    A = [[0.0] * n for _ in range(n)]
    r = [0.0] * n
    A[0][0], A[0][1] = 2 * h[0], h[0]
    r[0] = 6 * ((xs[1] - xs[0]) / h[0] - v0)
    A[n - 1][n - 2], A[n - 1][n - 1] = h[-1], 2 * h[-1]
    r[n - 1] = 6 * (v1 - (xs[-1] - xs[-2]) / h[-1])
    for i in range(1, n - 1):
        A[i][i - 1], A[i][i], A[i][i + 1] = h[i - 1], 2 * (h[i - 1] + h[i]), h[i]
        r[i] = 6 * ((xs[i + 1] - xs[i]) / h[i] - (xs[i] - xs[i - 1]) / h[i - 1])
    # Thomas algorithm
    c = [0.0] * n
    d = [0.0] * n
    for i in range(n):
        a_ = A[i][i - 1] if i > 0 else 0.0
        b_ = A[i][i] - a_ * (c[i - 1] if i > 0 else 0.0)
        c[i] = (A[i][i + 1] if i < n - 1 else 0.0) / b_
        d[i] = (r[i] - a_ * (d[i - 1] if i > 0 else 0.0)) / b_
    M = [0.0] * n
    for i in range(n - 1, -1, -1):
        M[i] = d[i] - (c[i] * M[i + 1] if i < n - 1 else 0.0)
    return M


def sample_spline(wps, duration):
    """V03+ authoring ('interp': 'spline'): within each moving chunk (between two holds) the route is a C2 cubic
    spline in time through the waypoints, clamped to the given start/end velocities (default 0). Acceleration
    is continuous everywhere (no zero-acceleration kinks at via points as with the quintic segments)."""
    chunks = []
    cur = [wps[0]]
    for w in wps[1:]:
        if w['p'] == cur[-1]['p'] and not cur[-1].get('v') and not w.get('v'):
            if len(cur) > 1:
                chunks.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if len(cur) > 1:
        chunks.append(cur)
    keys = []
    n = int(round(duration / DT_KEYS))
    for i in range(n + 1):
        t = i * DT_KEYS
        p = None
        for ch in chunks:
            if ch[0]['t'] <= t <= ch[-1]['t']:
                ts = [w['t'] for w in ch]
                out = []
                for k in range(2):
                    xs = [w['p'][k] for w in ch]
                    M = _clamped_spline(ts, xs, ch[0].get('v', [0, 0])[k], ch[-1].get('v', [0, 0])[k])
                    j = max(m for m in range(len(ts) - 1) if ts[m] <= t)
                    hh = ts[j + 1] - ts[j]
                    a, b = ts[j + 1] - t, t - ts[j]
                    out.append(M[j] * a ** 3 / (6 * hh) + M[j + 1] * b ** 3 / (6 * hh) + (xs[j] / hh - M[j] * hh / 6) * a + (xs[j + 1] / hh - M[j + 1] * hh / 6) * b)
                p = out
                break
        if p is None:
            prev = [w for w in wps if w['t'] <= t]
            p = (prev[-1] if prev else wps[0])['p']
        keys.append([round(t, 3), round(p[0], 3), round(p[1], 3)])
    return keys


def build(spec):
    play = {k: v for k, v in spec.items() if k not in ('motion', 'interp', 'behaviours')}
    out = []
    for p in spec['players']:
        q = dict(p)
        wps = spec['motion'].get(p['id'])
        if wps:
            q['track'] = sample_spline(wps, spec['duration']) if spec.get('interp') == 'spline' else sample_waypoints(wps, spec['duration'])
        out.append(q)
    if spec.get('behaviours'):
        # V05+: defenders driven by reusable behaviours (mark / zone / press / chase) reacting to the attack
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from fb_defence import resolve
        resolve(spec, out, track_pos)
    play['players'] = out
    return play


# ---------------------------------------------------------------- validation (python mirror of play.ts)

def track_pos(tr, t):
    if len(tr) == 1 or t <= tr[0][0]:
        return tr[0][1:3]
    if t >= tr[-1][0]:
        return tr[-1][1:3]
    i = 0
    while i < len(tr) - 2 and t > tr[i + 1][0]:
        i += 1
    n = len(tr)

    def tan(k):
        a, b = tr[max(0, k - 1)], tr[min(n - 1, k + 1)]
        dt = b[0] - a[0]
        return [(b[1] - a[1]) / dt, (b[2] - a[2]) / dt] if dt > 0 else [0, 0]

    t0, x0, y0 = tr[i]
    t1, x1, y1 = tr[i + 1]
    h = t1 - t0
    u = (t - t0) / h
    m0, m1 = tan(i), tan(i + 1)
    h00 = 2 * u ** 3 - 3 * u ** 2 + 1
    h10 = u ** 3 - 2 * u ** 2 + u
    h01 = -2 * u ** 3 + 3 * u ** 2
    h11 = u ** 3 - u ** 2
    return [h00 * x0 + h10 * h * m0[0] + h01 * x1 + h11 * h * m1[0], h00 * y0 + h10 * h * m0[1] + h01 * y1 + h11 * h * m1[1]]


def seg_dist(q, a, b):
    L2 = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
    s = max(0, min(1, ((q[0] - a[0]) * (b[0] - a[0]) + (q[1] - a[1]) * (b[1] - a[1])) / L2)) if L2 > 0 else 0
    return math.hypot(q[0] - a[0] - (b[0] - a[0]) * s, q[1] - a[1] - (b[1] - a[1]) * s)


def validate(play):
    res = []

    def add(name, ok, detail):
        res.append({'check': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})

    byid = {p['id']: p for p in play['players']}
    dt = 1 / 120
    n = int(play['duration'] / dt)
    # physical limits
    for p in play['players']:
        pos = [track_pos(p['track'], i * dt) for i in range(n + 1)]
        sp = [math.hypot(pos[i + 1][0] - pos[i][0], pos[i + 1][1] - pos[i][1]) / dt for i in range(n)]
        acc = [(sp[i + 6] - sp[i]) / (6 * dt) for i in range(0, n - 6)]
        vmax = max(sp)
        amax = max(abs(a) for a in acc) if acc else 0
        add(f'speed {p["id"]}', vmax <= 8.5, f'max {vmax:.2f} m/s (limit 8.5)')
        add(f"acceleration {p['id']}", amax <= 6.0, f"max |a| {amax:.2f} m/s2 (limit 6.0: elite sprint starts reach 6-7)")
        # constant-speed check: no plateau of exactly constant non-zero speed longer than 0.6 s
        plateau = 0
        best = 0
        for i in range(1, n):
            if sp[i] > 0.5 and abs(sp[i] - sp[i - 1]) < 1e-4:
                plateau += dt
                best = max(best, plateau)
            else:
                plateau = 0
        add(f'varying speed {p["id"]}', best < 0.6, f'longest constant-speed plateau {best:.2f} s')
    sp_ = play.get('setPiece', {})
    ev = sorted(play['ball']['events'], key=lambda e: e['t'])
    if sp_.get('type') == 'corner':
        cx, cy = sp_['corner']
        rest = next(e for e in ev if e['type'] == 'rest')
        d = math.hypot(rest['at'][0] - cx, rest['at'][1] - cy)
        add('Law 17: ball inside the corner arc (r 1 m)', d <= 1.0 - 0.11, f'ball centre {d:.2f} m from the corner point')
        first = next(e for e in ev if e['t'] > rest['t'] and e['type'] in ('pass', 'cross', 'shot'))
        for p in play['players']:
            if p['team'] != 'defence':
                continue
            dmin = min(math.hypot(track_pos(p['track'], t)[0] - cx, track_pos(p['track'], t)[1] - cy) - 1.0 for t in [i * dt for i in range(int(first['t'] / dt) + 1)])
            add(f'Law 17: {p["id"]} >= 9.15 m from the corner arc until the kick', dmin >= 9.15, f'closest {dmin:.2f} m from the arc')
        add('Law 17: ball kicked by the attacking team', byid[first['by']]['team'] == 'attack', f'kicker {first["by"]}')
        # kicker must not touch it again before another player
        nxt = [e for e in ev if e['t'] > first['t'] and e.get('by')]
        add('Law 17: kicker does not touch the ball twice in a row', not nxt or nxt[0]['by'] != first['by'], f'next touch by {nxt[0]["by"] if nxt else "-"}')
    # offside at each pass after the first (attack towards +x)
    for e in ev:
        if e['type'] not in ('pass', 'through', 'cross') or not e.get('to'):
            continue
        if sp_.get('type') == 'corner' and e is next(x for x in ev if x['type'] in ('pass', 'cross')):
            add(f'Law 11: pass {e["by"]}->{e["to"]} at {e["t"]}', True, 'received directly from a corner kick: no offside offence')
            continue
        rx = track_pos(byid[e['to']]['track'], e['t'])[0]
        defs = sorted((track_pos(p['track'], e['t'])[0] for p in play['players'] if p['team'] == 'defence'), reverse=True)
        bx = track_pos(byid[e['by']]['track'], e['t'])[0]
        line = max(defs[1] if len(defs) > 1 else -1e9, bx)
        ok = rx <= line or rx <= 0
        add(f'Law 11: {e["to"]} onside at pass {e["by"]}->{e["to"]} ({e["t"]} s)', ok, f'receiver x {rx:.2f}, ball x {bx:.2f}, second-last defender x {defs[1] if len(defs) > 1 else "-"}')
        # lane clearance: no defender within 1.2 m of the straight pass line while the ball travels
        a = track_pos(byid[e['by']]['track'], e['t'])
        b = e.get('target') or track_pos(byid[e['to']]['track'], e['t1'])
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        worst = 1e9
        who = '-'
        for p in play['players']:
            if p['team'] != 'defence':
                continue
            for k in range(11):
                tt = e['t'] + (e['t1'] - e['t']) * k / 10
                q = track_pos(p['track'], tt)
                s = max(0, min(1, ((q[0] - a[0]) * (b[0] - a[0]) + (q[1] - a[1]) * (b[1] - a[1])) / (L * L)))
                c = [a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s]
                dd = math.hypot(q[0] - c[0], q[1] - c[1])
                if dd < worst:
                    worst, who = dd, p['id']
        add(f'pass lane {e["by"]}->{e["to"]} clear of defenders (>= 1.2 m)', worst >= 1.2, f'closest {who} {worst:.2f} m')
        if play.get('animV2'):
            # V03+: team-mates must not stand in the lane either (the ball would pass through them)
            wa, wh = 1e9, '-'
            for p in play['players']:
                if p['team'] != 'attack' or p['id'] in (e['by'], e['to']):
                    continue
                for k in range(11):
                    tt = e['t'] + (e['t1'] - e['t']) * k / 10
                    dd = seg_dist(track_pos(p['track'], tt), a, b)
                    if dd < wa:
                        wa, wh = dd, p['id']
            add(f'pass lane {e["by"]}->{e["to"]} clear of team-mates (>= 0.8 m)', wa >= 0.8, f'closest {wh} {wa:.2f} m')
        if e.get('decel') is not None:
            T = e['t1'] - e['t']
            k = max(0, min(0.9, e['decel'] * T * T / (2 * L)))
            v0, v1 = (1 + k) * L / T, (1 - k) * L / T
            add(f'ground pass speed {e["by"]}->{e["to"]} plausible (3-14 m/s)', 3 <= v1 and v0 <= 14, f'{L:.1f} m in {T:.2f} s: leaves {v0:.1f} m/s, arrives {v1:.1f} m/s, decel {e["decel"]} m/s2')
    # shots (V03+): the goal is legal and physically clean
    for e in ev:
        if e['type'] != 'shot':
            continue
        tx, ty = e['target']
        lift = e.get('lift', 0.4)
        add(f'Law 10: shot by {e["by"]} wholly crosses the goal line', tx >= HL + 0.06 + 0.11, f'ball centre x {tx:.2f} (line outer edge {HL + 0.06:.2f} + radius 0.11)')
        add(f'Law 10: shot by {e["by"]} between the posts', abs(ty) <= 3.66 - 0.06 - 0.11, f'|y| {abs(ty):.2f} m (inner post face 3.60, ball radius 0.11)')
        add(f'Law 10: shot by {e["by"]} under the crossbar', 0.11 + lift <= 2.44 - 0.06 - 0.11, f'max ball centre height {0.11 + lift:.2f} m')
        a = track_pos(byid[e['by']]['track'], e['t'])
        # the lane starts 0.5 m in front of the strike point: a player behind the shooter cannot block it
        L0 = math.hypot(tx - a[0], ty - a[1])
        a = [a[0] + (tx - a[0]) * 0.5 / L0, a[1] + (ty - a[1]) * 0.5 / L0]
        worst, who = 1e9, '-'
        for p in play['players']:
            if p['id'] == e['by'] or p['role'] == 'GK':
                continue
            for k in range(11):
                tt = e['t'] + (e['t1'] - e['t']) * k / 10
                dd = seg_dist(track_pos(p['track'], tt), a, [tx, ty])
                if dd < worst:
                    worst, who = dd, p['id']
        add(f'shot lane {e["by"]} clear of every outfield player (>= 1.0 m)', worst >= 1.0, f'closest {who} {worst:.2f} m')
        for p in play['players']:
            if p['role'] != 'GK' or p['team'] == byid[e['by']]['team']:
                continue
            dive = next((x for x in p.get('actions', []) if x['type'] == 'dive'), None)
            q = track_pos(p['track'], e['t1'])
            reach = 1.15 + 1.0 if dive else 1.0  # body shift of the dive + arms
            dd = seg_dist(q, a, [tx, ty])
            add(f'keeper {p["id"]} beaten fairly (ball path beyond reach {reach:.2f} m)', dd >= reach + 0.15, f'keeper {dd:.2f} m from the ball path at the arrival, {"dives" if dive else "no dive"}')
            if dive:
                add(f'keeper {p["id"]} reacts after the strike', dive['t0'] >= e['t'] + 0.08, f'dive starts {dive["t0"] - e["t"]:.2f} s after the strike')
    # nobody runs through a corner flagpost (body radius ~0.25 m)
    for p in play['players']:
        dmin = min(min(math.hypot(track_pos(p['track'], i * dt)[0] - sx * HL, track_pos(p['track'], i * dt)[1] - sy * HW) for sx in (1, -1) for sy in (1, -1)) for i in range(0, n + 1, 4))
        add(f'{p["id"]} clear of the corner flagposts (>= 0.35 m)', dmin >= 0.35, f'closest {dmin:.2f} m')
    # players stay on the pitch or within 3 m of it
    for p in play['players']:
        out = max(max(abs(k[1]) - HL, abs(k[2]) - HW) for k in p['track'])
        add(f'{p["id"]} within the field of play surroundings', out <= 3.0, f'max {out:.2f} m outside the lines')
    return res


def main():
    cmd = sys.argv[1]
    if cmd == 'build':
        spec = json.load(open(sys.argv[2]))
        play = build(spec)
        json.dump(play, open(sys.argv[3], 'w'), indent=1)
        res = validate(play)
    else:
        res = validate(json.load(open(sys.argv[2])))
    bad = 0
    for r in res:
        print(f'{r["status"]:5} {r["check"]}: {r["detail"]}')
        bad += r['status'] != 'PASS'
    print(f'{len(res) - bad}/{len(res)} PASS')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
