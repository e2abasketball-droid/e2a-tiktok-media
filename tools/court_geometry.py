#!/usr/bin/env python3
"""E2A court geometry (FIBA, metres) in the OWNER coordinate system used by the Basketball IQ play files.

Owner system: origin at the centre of the attacking endline; x lateral (-7.5..7.5, negative = LEFT of the overhead
diagram with the basket at the top); y from the endline (0..14); z up. Hoop (0, 1.575, 3.05). Nail (0, 5.80).
Engine system (template/src/tactical): engine x = -owner x, same y, engine t = owner t + offset.

Also: the reach envelope used to decide whether a pass lane is OPEN / CONTESTED / BLOCKED.
Pure functions, no dependencies beyond the standard library.
"""
import math

HALF_W = 7.5
HALF_L = 14.0
HOOP = (0.0, 1.575, 3.05)
NAIL = (0.0, 5.80)
KEY_HALF_W = 2.45          # FIBA lane 4.90 m wide
FT_Y = 5.80                # free-throw line 5.80 m from the endline (the nail sits on it)
THREE_R = 6.75
CORNER_X = 6.60
RESTRICTED_R = 1.25
BALL_R = 0.12
BODY_R = 0.25              # body radius used for collisions (0.5 m centre to centre)


def to_engine(p):
    return [-p[0], p[1]] + list(p[2:])


def to_owner(p):
    return [-p[0], p[1]] + list(p[2:])


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def dist3(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def dist_to_hoop(p):
    return math.hypot(p[0] - HOOP[0], p[1] - HOOP[1])


def in_bounds(p, margin=0.2):
    return abs(p[0]) <= HALF_W - margin and margin <= p[1] <= HALF_L - margin


def in_paint(p):
    return abs(p[0]) <= KEY_HALF_W and 0 <= p[1] <= FT_Y


def is_three(p):
    join_y = HOOP[1] + math.sqrt(THREE_R ** 2 - CORNER_X ** 2)
    return abs(p[0]) >= CORNER_X if p[1] <= join_y else dist_to_hoop(p) >= THREE_R


def seg_point(a, b, p):
    """closest point on segment a-b to p (2D), its parameter u and the distance"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    q = (a[0] + dx * u, a[1] + dy * u)
    return q, u, math.hypot(p[0] - q[0], p[1] - q[1])


def angle_deg(v, w):
    n = math.hypot(*v) * math.hypot(*w)
    if n == 0:
        return 0.0
    c = max(-1.0, min(1.0, (v[0] * w[0] + v[1] * w[1]) / n))
    return math.degrees(math.acos(c))


# --- reach envelope ------------------------------------------------------------------------------------------------
# A defender can touch a ball whose centre is within ARM + BALL_R of either shoulder, the shoulders at 0.82 H, 0.21 m
# either side of the body axis; ARM = 0.44 H (shoulder to fingertips, anthropometric ~0.44-0.45 of stature).
# A "lunge" (one quick step / arm extension, up to 0.35 m) starts only after a 0.25 s reaction and grows at 2.5 m/s.
REACT_S = 0.25
LUNGE_M = 0.35
LUNGE_RATE = 2.5
CONTEST_MARGIN = 0.30      # clearance below this = CONTESTED: the ball passes within 0.30 m of the fingertips of a defender who has already reacted and lunged


def shoulders(pos, fdir, height):
    """two shoulder points (3D) of a player at pos (2D) facing the unit direction fdir (owner frame)"""
    n = math.hypot(*fdir) or 1.0
    fx, fy = fdir[0] / n, fdir[1] / n
    lx, ly = fy, -fx            # lateral unit vector
    z = 0.82 * height
    return [(pos[0] + lx * 0.21, pos[1] + ly * 0.21, z), (pos[0] - lx * 0.21, pos[1] - ly * 0.21, z)]


def lunge_after(seconds):
    """extra reach a defender has gained `seconds` after he could first see the ball leave the passer"""
    return min(LUNGE_M, max(0.0, seconds - REACT_S) * LUNGE_RATE)


def reach_clearance(ball, pos, fdir, height, extra=0.0):
    """metres between the ball surface and the defender's fingertip envelope (negative = he can touch it)"""
    arm = 0.44 * height + extra
    d = min(dist3(ball, s) for s in shoulders(pos, fdir, height))
    # the body itself (a vertical capsule, radius BODY_R, up to the head) also blocks
    body = math.hypot(ball[0] - pos[0], ball[1] - pos[1]) - BODY_R if ball[2] <= height else 9.0
    return min(d - arm, body) - BALL_R


def lane_state(clearance):
    if clearance < 0:
        return "BLOCKED"
    if clearance < CONTEST_MARGIN:
        return "CONTESTED"
    return "OPEN"


def engine_heading_to_owner_dir(h):
    """engine heading (radians, direction (cos h, sin h) in engine coordinates) -> owner-frame unit vector"""
    return (-math.cos(h), math.sin(h))


# --- physical bounce pass ----------------------------------------------------------------------------------------
G_ACC = 9.81
RESTITUTION = 0.78         # basketball on hardwood, vertical coefficient of restitution ~0.75-0.8


def bounce_split(T, z0, z1, e=RESTITUTION, r=BALL_R):
    """fraction k of the flight at which a bounce pass must hit the floor so that the vertical speed after the bounce is
    e x the speed before it (two gravity parabolas: release z0 -> floor -> catch z1, flight time T)"""
    def ratio(k):
        t1, t2 = k * T, (1 - k) * T
        down = (z0 - r) / t1 + G_ACC * t1 / 2
        up = (z1 - r) / t2 + G_ACC * t2 / 2
        return up / down
    lo, hi = 0.15, 0.85               # ratio grows with k
    for _ in range(60):
        mid = (lo + hi) / 2
        if ratio(mid) < e:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def bounce_z(u, T, z0, z1, e=RESTITUTION, r=BALL_R):
    k = bounce_split(T, z0, z1, e, r)
    if u < k:
        s, t1 = u / k, k * T
        return z0 + (r - z0) * s + 0.5 * G_ACC * t1 * t1 * s * (1 - s)
    s, t2 = (u - k) / (1 - k), (1 - k) * T
    return r + (z1 - r) * s + 0.5 * G_ACC * t2 * t2 * s * (1 - s)
