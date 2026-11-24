#!/usr/bin/env python3
"""E2A Football — OFF-BALL TIMING validator (FB-SETPIECE-001 V07+): the MASTER MATCH TIMELINE.

A play may carry
  timeline  named events [{id, t, who, kind: ball|run|reaction, what, measure?}] — ONE time source for the
            runs, the ball contacts, the defensive reactions, the camera and the graphics. Reaction events
            have t=None in the spec and are MEASURED from the built tracks (resolve()).
  runs      the run book [{runner, start, trigger, cue, reacts, arrive, arrive_by, r, ball_at?, early, late}]

Automatic checks (numbers only, measured on the same tracks the video draws):
  timeline      ordered; every ball event is an authored contact of the ball script
  run onset     the run really starts when the timeline says (velocity towards its arrival zone)
  trigger       no run starts before its trigger (anticipation allowance 0.35 s — ASSUMPTION, documented)
  arrival       the runner reaches his arrival zone in time; the final receiver arrives WITH the ball
                (not more than 0.5 s early — a receiver waiting in the space is seen and picked up)
  lane          the final receiver does not arrive before the passing lane is open
  reaction      a defender reacting to a run moves >= 0.12 s after the runner (perception + reaction;
                0.12-0.18 s = NEEDS HUMAN REVIEW: ASSUMPTION based on typical simple visual reaction times)
  preparation   every pass / shot is struck with the body facing within 100 deg of the kick direction
  spacing       no two bodies closer than 0.55 m at any instant (no interpenetration)
Human-behaviour judgements (is the decoy convincing, does the run look natural) are NOT automated: they are
listed as NEEDS HUMAN REVIEW.

    python3 football/scripts/fb_timeline.py <play.json>
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fb_motion import track_pos  # noqa: E402
from fb_defence import rough_ball  # noqa: E402

DT = 0.02
ANTICIPATION = 0.35
REACT_MIN = 0.12
REACT_REVIEW = 0.18


def _tools(play):
    byid = {p['id']: p for p in play['players']}
    P = lambda pid, t: track_pos(byid[pid]['track'], t)  # noqa: E731

    def vel(pid, t, h=0.05):
        a, b = P(pid, t - h), P(pid, t + h)
        return ((b[0] - a[0]) / (2 * h), (b[1] - a[1]) / (2 * h))
    return byid, P, vel


def onset(play, pid, after, toward=None, thr=None):
    """first time >= after when the player starts moving: towards `toward` (component >= 0.7 m/s) or, without a
    target, when his speed rises 0.8 m/s above its value at `after` (a defender leaving his position)."""
    _, P, vel = _tools(play)
    t = after
    base = math.hypot(*vel(pid, after))
    while t < play['duration']:
        v = vel(pid, t)
        if toward is not None:
            q = P(pid, t)
            dx, dy = toward[0] - q[0], toward[1] - q[1]
            L = math.hypot(dx, dy) or 1
            if (v[0] * dx + v[1] * dy) / L >= (thr or 0.7):
                return round(t, 2)
        elif math.hypot(*v) - base >= (thr or 0.8):
            return round(t, 2)
        t += DT
    return None


def resolve(spec_or_play):
    """fill the measured reaction times of the timeline (needs built tracks)"""
    for e in spec_or_play.get('timeline', []):
        m = e.get('measure')
        if m and e.get('t') is None:
            e['t'] = onset(spec_or_play, m['onset'], m['after'])
    return spec_or_play


def validate(play):
    res = []

    def add(name, ok, detail, state=None):
        res.append({'check': name, 'status': state or ('PASS' if ok else 'FAIL'), 'detail': detail})

    TL = play.get('timeline')
    if not TL:
        return [{'check': 'timeline block', 'status': 'NOT VERIFIED', 'detail': 'play has no timeline'}]
    byid, P, vel = _tools(play)
    E = {e['id']: e['t'] for e in TL}
    D = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])  # noqa: E731
    ball = lambda t: rough_ball(play['ball']['events'], P, t)  # noqa: E731
    evs = sorted(play['ball']['events'], key=lambda e: e['t'])

    # timeline integrity
    missing = [e['id'] for e in TL if e.get('t') is None]
    add('timeline: every event has a time (reactions measured)', not missing, f'{len(TL)} events' + (f', missing {missing}' if missing else ''))
    ts = [e['t'] for e in TL if e.get('t') is not None]
    add('timeline: events in chronological order', ts == sorted(ts), ' < '.join(f'{e["id"]} {e["t"]:.2f}' for e in TL if e.get('t') is not None))
    contacts = {round(e['t'], 3) for e in evs if e['type'] in ('pass', 'shot', 'hold', 'dribble')} | {round(e['t1'], 3) for e in evs if e.get('t1')}
    bad = [e['id'] for e in TL if e['kind'] == 'ball' and e['id'] != 'PLAYER_A_STARTS_APPROACH' and round(e['t'], 3) not in contacts]
    add('timeline: every ball event is a contact of the ball script', not bad, 'all ball events match' if not bad else f'not matching: {bad}')

    # run book
    for r in play.get('runs', []):
        a = r['runner']
        t_auth = E[r['start']]
        t_on = onset(play, a, max(0.0, t_auth - 0.8), toward=r['arrive'])
        add(f'run onset {a} ({r["start"]})', t_on is not None and abs(t_on - t_auth) <= 0.3,
            f'authored {t_auth:.2f} s, measured {t_on} s (velocity towards the arrival zone >= 0.7 m/s)')
        trig = E[r['trigger']]
        add(f'trigger before run {a}: {r["trigger"]} -> {r["start"]}', t_on is not None and t_on >= trig - ANTICIPATION,
            f'trigger {trig:.2f} s, run {t_on} s (anticipation allowance {ANTICIPATION} s)')
        # arrival
        t_arr = None
        t = t_auth
        while t <= play['duration']:
            if D(P(a, t), r['arrive']) <= r['r']:
                t_arr = round(t, 2)
                break
            t += DT
        add(f'arrival {a} in time (zone r {r["r"]} m by {r["arrive_by"]:.2f} s)', t_arr is not None and t_arr <= r['arrive_by'] + 0.15,
            f'enters the zone at {t_arr} s')
        if r.get('ball_at') is not None:
            ok = t_arr is not None and r['ball_at'] - 0.5 <= t_arr <= r['ball_at'] + 0.1
            add(f'final receiver {a} arrives WITH the ball (not waiting in the space)', ok,
                f'enters at {t_arr} s, ball arrives {r["ball_at"]:.2f} s')
            # passing lane: segment ball(at delivery) -> arrival point clear of defenders by >= 0.8 m
            cut = next(e for e in evs if e['type'] == 'pass' and e.get('to') == a)
            p0 = P(cut['by'], cut['t'])
            dfn = [p['id'] for p in play['players'] if p['team'] == 'defence' and p['role'] != 'GK']

            def seg_d(q, A, B):
                ax, ay = B[0] - A[0], B[1] - A[1]
                u = max(0.0, min(1.0, ((q[0] - A[0]) * ax + (q[1] - A[1]) * ay) / (ax * ax + ay * ay)))
                return math.hypot(A[0] + ax * u - q[0], A[1] + ay * u - q[1])
            t_open = None
            t = cut['t'] - 1.5
            while t <= cut['t1']:
                if all(seg_d(P(d, t), p0, r['arrive']) >= 0.8 for d in dfn):
                    if t_open is None:
                        t_open = round(t, 2)
                else:
                    t_open = None
                t += DT
            add(f'final receiver {a} does not arrive before the lane is open', t_open is not None and t_arr is not None and t_arr >= t_open,
                f'lane open (all defenders >= 0.8 m) from {t_open} s, runner arrives {t_arr} s')
        # defender reaction
        d = r.get('reacts')
        if d and r['start'] != 'LATE_RUNNER_STARTS':
            t_d = onset(play, d, t_on)
            lat = None if t_d is None else round(t_d - t_on, 2)
            st = None
            if lat is not None and REACT_MIN <= lat < REACT_REVIEW:
                st = 'NEEDS HUMAN REVIEW'
            add(f'defender reaction {d} after {a}\'s run (>= {REACT_MIN} s)', lat is not None and lat >= REACT_MIN,
                f'{d} moves {lat} s after {a} (ASSUMPTION: perception + reaction >= {REACT_MIN} s)', st)

    # late runner vs edge defender: D9 only reacts after the runner has started (no telepathic tracking)
    if 'EDGE_DEFENDER_REACTS' in E and 'LATE_RUNNER_STARTS' in E:
        add('edge defender reacts after the late runner starts (no telepathic tracking)', E['EDGE_DEFENDER_REACTS'] > E['LATE_RUNNER_STARTS'] + REACT_MIN,
            f'A6 starts {E["LATE_RUNNER_STARTS"]:.2f} s, D9 reacts {E["EDGE_DEFENDER_REACTS"]:.2f} s')

    # body preparation for every pass / shot
    for e in evs:
        if e['type'] not in ('pass', 'shot'):
            continue
        k = e['by']
        tgt = e.get('target') or (P(e['to'], e['t1']) if e.get('to') else None)
        if tgt is None:
            continue
        q = P(k, e['t'])
        kdir = math.atan2(tgt[1] - q[1], tgt[0] - q[0])
        v = vel(k, e['t'] - 0.05)
        sp = math.hypot(*v)
        body = math.atan2(v[1], v[0]) if sp > 1.0 else kdir  # standing: the body is set to the ball (checked by fb_motion)
        diff = abs((math.degrees(body - kdir) + 180) % 360 - 180)
        add(f'body prepared: {e["type"]} {k} at {e["t"]:.2f} s', diff <= 100 and sp <= 6.0,
            f'body/kick angle {diff:.0f} deg, speed {sp:.1f} m/s (<= 100 deg, <= 6 m/s)')

    # spacing
    ids = list(byid)
    worst, pair, at = 9.9, '-', 0
    t = 0.0
    while t <= play['duration']:
        pos = {i: P(i, t) for i in ids}
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                dd = D(pos[ids[i]], pos[ids[j]])
                if dd < worst:
                    worst, pair, at = dd, f'{ids[i]}-{ids[j]}', t
        t += 0.05
    add('no body interpenetration (centres >= 0.55 m)', worst >= 0.55, f'closest {pair} {worst:.2f} m at {at:.2f} s')

    for name in ('decoy run looks convincing (sprint, not a jog)', 'late run reads as late (not visible from the edge defender)',
                 'defender reactions look human'):
        add(f'visual: {name}', True, 'judgement, not automated', 'NEEDS HUMAN REVIEW')
    return res


def run_table(play):
    """per run: trigger, measured onset, peak speed / acceleration, arrival"""
    _, P, vel = _tools(play)
    E = {e['id']: e['t'] for e in play['timeline']}
    rows = []
    for r in play.get('runs', []):
        a = r['runner']
        t_on = onset(play, a, max(0.0, E[r['start']] - 0.8), toward=r['arrive'])
        vs, t = [], t_on
        while t <= r['arrive_by'] + 0.01:
            vs.append(math.hypot(*vel(a, t)))
            t += 0.1
        acc = max((abs(b - c) / 0.1 for c, b in zip(vs, vs[1:])), default=0)
        rows.append({'runner': a, 'trigger': r['trigger'], 'trigger_t': E[r['trigger']], 'start': t_on, 'peak_speed': round(max(vs), 2),
                     'peak_accel': round(acc, 2), 'arrive_by': r['arrive_by'], 'reacts': r.get('reacts')})
    return rows


def main():
    play = json.load(open(sys.argv[1]))
    res = validate(play)
    bad = 0
    for r in res:
        print(f'{r["status"]:5} [timeline] {r["check"]}: {r["detail"]}')
        bad += r['status'] == 'FAIL'
    if play.get('runs'):
        for row in run_table(play):
            print('RUN', json.dumps(row))
    print(f'{sum(r["status"] == "PASS" for r in res)}/{len(res)} timing checks PASS, {bad} FAIL, '
          f'{sum(r["status"] == "NEEDS HUMAN REVIEW" for r in res)} NEEDS HUMAN REVIEW')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
