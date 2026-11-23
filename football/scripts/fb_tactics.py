#!/usr/bin/env python3
"""E2A Football — TACTICAL validator for set-piece plays (FB-SETPIECE-001 V05+).

The rules/physics validator (fb_motion.py) proves that a play is legal and humanly possible. This one asks
the questions a first-team analyst asks, with numbers (metres, seconds, degrees):

  structure   11 v 11; the box is defended compactly at the kick (no attacker free in the box)
  marking     each man-marker stays goal-side and tight until the trigger
  pressure    the passer is under pressure at the delivery (not an artificial free cross)
  shift       the defensive line really shifts (the decoy moves defenders, it is not decoration)
  advantage   the scorer is NOT free from the start, and his separation at the strike is a few steps only
  view        the late runner arrives from outside the edge defender's field of view (orientation only)
  keeper      logical position on the ball-goal bisector, feet set at the strike, reaction after the strike
  contact     no attacker-defender contact (no illegal block / impeding with contact) during the move

    python3 football/scripts/fb_tactics.py <play.json>
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fb_motion import track_pos  # noqa: E402
from fb_defence import rough_ball  # noqa: E402

HL = 52.5
POSTS = ((HL, -3.66), (HL, 3.66))


def validate(play):
    res = []

    def add(name, ok, detail, state=None):
        res.append({'check': name, 'status': state or ('PASS' if ok else 'FAIL'), 'detail': detail})

    T = play.get('tactics')
    if not T:
        return [{'check': 'tactics block', 'status': 'NOT VERIFIED', 'detail': 'play has no tactics block'}]
    byid = {p['id']: p for p in play['players']}
    P = lambda pid, t: track_pos(byid[pid]['track'], t)  # noqa: E731
    D = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])  # noqa: E731
    ball = lambda t: rough_ball(play['ball']['events'], P, t)  # noqa: E731
    att = [p['id'] for p in play['players'] if p['team'] == 'attack']
    dfn = [p['id'] for p in play['players'] if p['team'] == 'defence']
    tk, tt, td, ts = T['kick'], T['trigger'], T['delivery'], T['strike']
    sc, gk = T['scorer'], T['keeper']
    inbox = lambda q: q[0] >= 36.0 and abs(q[1]) <= 20.16  # noqa: E731

    def vel(pid, t, h=0.05):
        a, b = P(pid, t - h), P(pid, t + h)
        return ((b[0] - a[0]) / (2 * h), (b[1] - a[1]) / (2 * h))

    def facing(pid, t):
        v = vel(pid, t)
        if math.hypot(*v) > 2.0:
            return math.atan2(v[1], v[0])
        b, q = ball(t), P(pid, t)
        return math.atan2(b[1] - q[1], b[0] - q[0])

    # structure
    add('11 v 11 on the pitch', len(att) == 11 and len(dfn) == 11, f'{len(att)} attackers, {len(dfn)} defenders')
    box_d = [d for d in dfn if inbox(P(d, tk))]
    add('compact box at the kick (>= 8 defenders incl. keeper inside the box)', len(box_d) >= 8, f'{len(box_d)} inside the box: {", ".join(box_d)}')
    far = max(D(P(d, tk), (HL, 0)) for d in box_d)
    add('no box defender artificially far from goal at the kick (<= 16 m from goal centre)', far <= 16.0, f'farthest {far:.1f} m')
    worst, who = 0, '-'
    for a in att:
        q = P(a, tk)
        if inbox(q):
            dmin = min(D(q, P(d, tk)) for d in dfn)
            if dmin > worst:
                worst, who = dmin, a
    add('no attacker free inside the box at the kick (nearest defender <= 3.0 m)', worst <= 3.0, f'worst {who}: {worst:.2f} m')
    # marking
    for dd, aa in T['marks']:
        n = int((tt + 0.6) / 0.05)
        dist = [D(P(dd, i * 0.05), P(aa, i * 0.05)) for i in range(n)]
        # goal-side = nearer the goal mouth (segment between the posts) than his attacker
        mouth = lambda q: math.hypot(HL - q[0], max(0.0, abs(q[1]) - 3.66))  # noqa: E731
        gs = all(mouth(P(dd, i * 0.05)) < mouth(P(aa, i * 0.05)) + 0.2 for i in range(n))
        add(f'marking {dd} on {aa}: tight and goal-side until the trigger (<= 1.6 m)', max(dist) <= 1.6 and gs, f'max {max(dist):.2f} m, goal-side {"yes" if gs else "NO"}')
    # pressure on the passer
    passer = next(e['by'] for e in play['ball']['events'] if e['type'] in ('pass', 'cross') and abs(e['t'] - td) < 1e-6)
    dp = min(D(P(passer, td), P(d, td)) for d in dfn)
    add(f'delivery under pressure (nearest defender to {passer} at the cutback <= 3.0 m: one sprint step, ~0.5 s to tackle)', dp <= 3.0, f'{dp:.2f} m')
    # shift
    cp = T['compromised']
    s0, s1 = P(cp, tt), P(cp, td + 0.2)
    add(f'defensive shift is real ({cp} moves >= 1.5 m towards the near post)', D(s0, s1) >= 1.5 and s1[1] < s0[1], f'{D(s0, s1):.2f} m, y {s0[1]:.2f} -> {s1[1]:.2f}')
    # advantage: not free from the start, a few steps at the strike, a short window
    q0 = P(sc, tk)
    add(f'scorer {sc} not free in the box from the start (outside the box at the kick)', not inbox(q0), f'{sc} at ({q0[0]:.1f}, {q0[1]:.1f})')
    sep_d = min(D(P(sc, td), P(d, td)) for d in dfn)
    sep_s = min(D(P(sc, ts), P(d, ts)) for d in dfn if d != gk)
    add(f'scorer accompanied at the delivery (nearest defender <= 3.5 m)', sep_d <= 3.5, f'{sep_d:.2f} m')
    add('momentary advantage at the strike: 1.2-3.5 m from the nearest outfield defender', 1.2 <= sep_s <= 3.5, f'{sep_s:.2f} m')
    win = sum(0.05 for i in range(int(tk / 0.05), int(ts / 0.05) + 1)
              if inbox(P(sc, i * 0.05)) and min(D(P(sc, i * 0.05), P(d, i * 0.05)) for d in dfn if d != gk) > 2.0)
    add('advantage window is short (scorer in the box > 2 m from everyone for <= 1.5 s)', win <= 1.5, f'{win:.2f} s')
    # view (orientation only)
    late = T['late']
    angs = []
    for i in range(int((tt + 0.5) / 0.05), int((td - 0.1) / 0.05)):
        t = i * 0.05
        f = facing(late, t)
        q, r = P(late, t), P(sc, t)
        a = math.atan2(r[1] - q[1], r[0] - q[0])
        angs.append(abs(math.degrees(math.atan2(math.sin(a - f), math.cos(a - f)))))
    add(f'late run starts outside {late}\'s orientation (> 100 deg off his facing) until the delivery', min(angs) > 100, f'min {min(angs):.0f} deg (orientation, not attention)')
    rec = D(P(late, ts), P(sc, ts))
    add(f'{late} closes but cannot block: 1.0-3.5 m behind the scorer at the strike', 1.0 <= rec <= 3.5, f'{rec:.2f} m')
    # keeper
    shot = next(e for e in play['ball']['events'] if e['type'] == 'shot')
    a = P(sc, ts)
    g = P(gk, ts)
    angs = [math.atan2(p[1] - a[1], p[0] - a[0]) for p in POSTS]
    bis = (angs[0] + angs[1]) / 2
    y_opt = a[1] + (g[0] - a[0]) * math.tan(bis)
    add('keeper on the ball-goal bisector at the strike (<= 0.8 m off)', abs(g[1] - y_opt) <= 0.8, f'{abs(g[1] - y_opt):.2f} m off (optimal y {y_opt:.2f}, keeper y {g[1]:.2f})')
    gv = math.hypot(*vel(gk, ts))
    add('keeper set at the strike (speed <= 1.0 m/s)', gv <= 1.0, f'{gv:.2f} m/s')
    dive = next((x for x in byid[gk].get('actions', []) if x['type'] == 'dive'), None)
    if dive:
        r = dive['t0'] - shot['t']
        add('keeper reacts after the strike (0.12-0.30 s, no anticipation)', 0.12 <= r <= 0.30, f'{r:.2f} s')
    L = D(a, shot['target'])
    fl = shot['t1'] - shot['t']
    add('shot is hard to stop (flight <= 0.65 s, placed <= 0.6 m inside the post)', fl <= 0.65 and 3.66 - abs(shot['target'][1]) <= 0.6, f'{L:.1f} m in {fl:.2f} s ({L / fl:.1f} m/s), {3.66 - abs(shot["target"][1]):.2f} m inside the post')
    # contact
    worst, pair = 1e9, '-'
    for i in range(int(tk / 0.05), int(ts / 0.05)):
        t = i * 0.05
        for x in att:
            for y in dfn:
                d = D(P(x, t), P(y, t))
                if d < worst:
                    worst, pair = d, f'{x}-{y} at {t:.2f} s'
    add('no contact between opponents during the move (>= 0.6 m: no block, no holding)', worst >= 0.6, f'closest {pair}: {worst:.2f} m')
    return res


def main():
    play = json.load(open(sys.argv[1]))
    res = validate(play)
    bad = 0
    for r in res:
        print(f'{r["status"]:5} [tactics] {r["check"]}: {r["detail"]}')
        bad += r['status'] == 'FAIL'
    print(f'{len(res) - bad}/{len(res)} tactical checks PASS')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
