#!/usr/bin/env python3
"""E2A Football — QC of the FB SPACE CREATION VISUALIZER (V09+). Same formula as spaceState() in
remotion/src/overlays3d.tsx, on the same tracks: the graphic cannot invent an advantage the play does not show.

  not open from the start   when the zone first appears it is COVERED (u < 0.3): a defender is next to it
  caused by a defender      the defender who covered it at the start has moved >= 1.0 m further away by the time
                            the zone is fully open, and that move starts after his measured reaction
  proportional              the drawn radius never exceeds the real gap (nearest defender - 2.7 m) nor 1.7 m
  temporary                 the light ends when the runner occupies the zone or a defender closes it
  window                    when the zone is open and for how long (play seconds)

    python3 football/scripts/fb_space.py <play.json> <cx> <cy> <runner> <t_show> [react_event]
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fb_motion import track_pos  # noqa: E402

COVERED, OPEN, RMAX = 3.2, 4.3, 1.7


def state(play, c, runner, t):
    best, who = 1e9, None
    for p in play['players']:
        if p['team'] != 'defence' or p.get('role') == 'GK':
            continue
        q = track_pos(p['track'], t)
        d = math.hypot(q[0] - c[0], q[1] - c[1])
        if d < best:
            best, who = d, p['id']
    u = max(0.0, min(1.0, (best - COVERED) / (OPEN - COVERED)))
    r = min(RMAX, max(0.0, best - 2.7))
    rp = next(p for p in play['players'] if p['id'] == runner)
    q = track_pos(rp['track'], t)
    occ = max(0.0, min(1.0, (math.hypot(q[0] - c[0], q[1] - c[1]) - 0.6) / 1.4))
    return best, who, u, r, occ


def main(path, cx, cy, runner, t_show, react=None):
    play = json.load(open(path))
    c = (cx, cy)
    by = {p['id']: p for p in play['players']}
    ev = {e['id']: e['t'] for e in play.get('timeline', [])}
    res = []
    add = lambda ok, name, detail: res.append(('PASS' if ok is True else ok if isinstance(ok, str) else 'FAIL', name, detail))  # noqa: E731
    d0, who0, u0, _, _ = state(play, c, runner, t_show)
    add(u0 < 0.3, 'not open from the start', f'at play {t_show:.2f} s the nearest defender {who0} is {d0:.2f} m away (u={u0:.2f}: covered)')
    ts = [t_show + k * 0.02 for k in range(int((play['duration'] - t_show) / 0.02))]
    S = [(t, *state(play, c, runner, t)) for t in ts]
    t_half = next((t for t, d, w, u, r, o in S if u >= 0.5), None)
    t_full = next((t for t, d, w, u, r, o in S if u >= 0.999), None)
    if t_full is None:
        add(False, 'opens', 'the zone never becomes open')
    else:
        q0 = track_pos(by[who0]['track'], t_show)
        q1 = track_pos(by[who0]['track'], t_full)
        moved = math.hypot(q1[0] - c[0], q1[1] - c[1]) - math.hypot(q0[0] - c[0], q0[1] - c[1])
        add(moved >= 1.0, 'caused by a defender moving', f'{who0} goes from {math.hypot(q0[0]-c[0], q0[1]-c[1]):.2f} m to {math.hypot(q1[0]-c[0], q1[1]-c[1]):.2f} m from the zone (+{moved:.2f} m) between play {t_show:.2f} and {t_full:.2f} s')
        if react and react in ev:
            add(t_half >= ev[react], 'opens after the defensive reaction', f'half open at play {t_half:.2f} s; {react} at {ev[react]:.2f} s')
    over = [(t, r, d) for t, d, w, u, r, o in S if u * o > 0.01 and (r > RMAX + 1e-9 or r > d - 2.7 + 1e-9)]
    add(not over, 'proportional to the real gap', 'drawn radius <= min(1.7 m, nearest defender - 2.7 m) at every frame' if not over else f'{len(over)} frames too big')
    lit = [(t, u * o) for t, d, w, u, r, o in S]
    on = [t for t, l in lit if l > 0.5]
    t_end = next((t for t, l in lit if t > (t_full or 0) and l < 0.05), None)
    end_why = None
    if t_end is not None:
        _, _, u_e, _, o_e = state(play, c, runner, t_end)
        end_why = 'the runner occupies it' if o_e < 0.05 else 'a defender closes it'
    add(t_end is not None, 'temporary', f'lit (>50 %) from play {on[0]:.2f} to {on[-1]:.2f} s ({on[-1]-on[0]:.2f} s), gone at {t_end:.2f} s: {end_why}' if on and t_end else 'never ends')
    peak = max(S, key=lambda x: x[4])
    print(json.dumps({'zone': c, 'runner': runner, 'covered_by': who0, 'covered_dist': round(d0, 2), 'half_open': t_half, 'open': t_full, 'gone': t_end, 'max_radius_m': round(peak[4], 2), 'max_gap_m': round(peak[1], 2)}))
    for s, n, d in res:
        print(f'{s:5} [space] {n}: {d}')
    print(f"{sum(1 for s, _, _ in res if s == 'PASS')}/{len(res)} space checks PASS")


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], float(a[1]), float(a[2]), a[3], float(a[4]), a[5] if len(a) > 5 else None)
