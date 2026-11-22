"""E2A Football — pitch model (metres). Origin = centre spot; x along the length (attack towards +x), y across
the width; z up. Laws of the Game (IFAB) markings; the default pitch is the common 105 × 68 m."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Pitch:
    length: float = 105.0
    width: float = 68.0
    goal_width: float = 7.32
    goal_height: float = 2.44
    penalty_depth: float = 16.5
    penalty_width: float = 40.32
    goal_area_depth: float = 5.5
    goal_area_width: float = 18.32
    penalty_spot: float = 11.0
    centre_circle_r: float = 9.15

    @property
    def half_l(self):
        return self.length / 2

    @property
    def half_w(self):
        return self.width / 2

    def inside(self, x, y, margin=0.0):
        return abs(x) <= self.half_l + margin and abs(y) <= self.half_w + margin

    def in_penalty_area(self, x, y, side=+1):
        x0 = side * self.half_l
        return side * (x0 - x) <= self.penalty_depth and side * (x0 - x) >= 0 and abs(y) <= self.penalty_width / 2


def offside_line(defenders_x, ball_x, attack=+1, half_l=52.5):
    """x of the offside line for an attack towards `attack` (+1/-1): the second-last defender (goalkeeper
    included), or the ball if it is nearer the goal line; never inside the attacker's own half."""
    if len(defenders_x) < 2:
        raise ValueError('need at least two defending players (goalkeeper included)')
    depth = sorted((attack * x for x in defenders_x), reverse=True)
    line = max(depth[1], attack * ball_x, 0.0)
    return attack * min(line, half_l)


def is_offside_position(attacker_x, defenders_x, ball_x, attack=+1):
    return attack * attacker_x > attack * offside_line(defenders_x, ball_x, attack)
