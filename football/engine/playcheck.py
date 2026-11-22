"""Checker for FB-PLAY files (structure + football rules), dependency-free."""
import json
import re

from pitch import Pitch, is_offside_position, offside_line

BALL_TYPES = {"hold", "dribble", "pass", "cross", "through", "shot", "clear", "out"}
MARKS = {"arrow", "passLine", "zone", "defLine", "highlight", "freeze", "label"}
MAX_SPEED = 10.5  # m/s, above elite sprint speed: a keyframe pair faster than this is a data error


def pos(track, t):
    if t <= track[0][0]:
        return track[0][1], track[0][2]
    for (t0, x0, y0), (t1, x1, y1) in zip(track, track[1:]):
        if t0 <= t <= t1:
            k = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    return track[-1][1], track[-1][2]


def check(play):
    err, warn = [], []
    for k in ("id", "version", "title", "pitch", "duration", "teams", "players", "ball"):
        if k not in play:
            err.append(f"missing '{k}'")
    if err:
        return err, warn
    if not re.match(r"^FB-PLAY-[a-z0-9]+(-[a-z0-9]+)*$", play["id"]):
        err.append("id must be FB-PLAY-<slug>")
    if play.get("fictional") is not True:
        err.append("fictional must be true (no real players or clubs)")
    P = Pitch(play["pitch"].get("length", 105.0), play["pitch"].get("width", 68.0))
    T = play["duration"]
    ids = {}
    per_team = {"attack": 0, "defence": 0}
    for p in play["players"]:
        if p["id"] in ids:
            err.append(f"duplicate player id {p['id']}")
        ids[p["id"]] = p
        if p["team"] not in per_team:
            err.append(f"{p['id']}: team must be attack/defence")
            continue
        per_team[p["team"]] += 1
        tr = p["track"]
        if any(len(k) != 3 for k in tr):
            err.append(f"{p['id']}: keyframes are [t, x, y]")
            continue
        if [k[0] for k in tr] != sorted(k[0] for k in tr):
            err.append(f"{p['id']}: keyframe times must increase")
        for t, x, y in tr:
            if not P.inside(x, y, margin=2.0):
                err.append(f"{p['id']}: ({x}, {y}) at {t}s is off the pitch")
            if t < 0 or t > T:
                err.append(f"{p['id']}: keyframe time {t} outside 0..{T}")
        for (t0, x0, y0), (t1, x1, y1) in zip(tr, tr[1:]):
            if t1 > t0 and ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5 / (t1 - t0) > MAX_SPEED:
                err.append(f"{p['id']}: speed above {MAX_SPEED} m/s between {t0}s and {t1}s")
    for team, n in per_team.items():
        if n > 11:
            err.append(f"{team}: {n} players (max 11)")
    holder = None
    for e in sorted(play["ball"]["events"], key=lambda e: e["t"]):
        if e["type"] not in BALL_TYPES:
            err.append(f"ball event type '{e['type']}'")
        for k in ("by", "to"):
            if k in e and e[k] not in ids:
                err.append(f"ball event at {e['t']}s: unknown player {e[k]}")
        if e["type"] in ("pass", "cross", "through") and "to" in e and e.get("by") in ids and e["to"] in ids:
            if ids[e["to"]]["team"] == "attack":
                defenders = [pos(d["track"], e["t"])[0] for d in play["players"] if d["team"] == "defence"]
                if len(defenders) >= 2:
                    bx = pos(ids[e["by"]]["track"], e["t"])[0]
                    rx = pos(ids[e["to"]]["track"], e["t"])[0]
                    if is_offside_position(rx, defenders, bx):
                        err.append(f"{e['to']} is offside at the {e['type']} at {e['t']}s (line x={offside_line(defenders, bx):.1f})")
                else:
                    warn.append(f"offside not checked at {e['t']}s: fewer than 2 defenders in the play")
        holder = e.get("to", e.get("by", holder))
    for m in play.get("marks", []):
        if m["kind"] not in MARKS:
            err.append(f"mark kind '{m['kind']}'")
        if not (0 <= m["t0"] <= m["t1"] <= T):
            err.append(f"mark {m['kind']} times {m['t0']}..{m['t1']} outside 0..{T}")
    return err, warn


def check_file(path):
    with open(path, encoding="utf-8") as fh:
        return check(json.load(fh))
