#!/usr/bin/env python3
"""E2A Tactical Studio V4 — SHADOW planner for 4 videos a day (owner brief 2026-11-14 16:28Z).

What it does (read-only, never writes to Metricool, has no Metricool code at all):
  * one plan per Sydney date with 4 distinct ids E2A-TACTICAL-<date>-S01..S04 (S = shadow: the V3 publisher
    only accepts V<nn> ids of its own config, so a shadow id can never be published);
  * 4 formats, one per slot: execution, defensive_read, counter, challenge ("What would you do?");
  * picks a concept per slot from config/tactical_concepts.v4.json with the studio's own repeat_check
    (45-day window, same family+variant or concept overlap blocks), against the live ledger history, the
    pre-ledger history and the other slots of the same day;
  * checks every slot against the REAL calendar read-back with the studio's own collisions() (any post on
    our networks within ±60 min blocks, trial reels included) and also against the IG trial reel that the
    owner's rule adds 2 h after each planned reel; a blocked slot gets the nearest free time or stays empty;
  * at most max_videos_per_day (4): a 5th request is rejected, never queued;
  * destinations = videos × 3 networks (12 for a full day), create calls = 1 grouped call per video;
  * budget estimate from MEASURED costs against the V4 budget_per_day, with the exact missing amount.

It refuses to run when the profile is not a shadow profile (mode shadow, verifier blocked, S ids) or when the
V4 shadow production is revoked (profile status REVOKED or the file state/tactical-v4/REVOKED exists).

  python3 tools/tactical_planner_v4.py plan 2026-11-16 --readback cal.json [--used plays.jsonl] [--out plan.json]
  python3 tools/tactical_planner_v4.py schedule        # data-based alternative grid from the best-time evidence
"""
import argparse
import datetime as dt
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tactical_studio as ts  # noqa: E402

ROOT = ts.ROOT
PROFILE = os.path.join(ROOT, "config", "tactical_studio.v4-shadow.json")
CONCEPTS = os.path.join(ROOT, "config", "tactical_concepts.v4.json")
REVOKED_FLAG = os.path.join(ROOT, "state", "tactical-v4", "REVOKED")
BEST_TIME = os.path.join(ROOT, "produccion", "tactical", "v4", "evidencia", "best-time-2026-11-08_14.json")
FORMATS = ("execution", "defensive_read", "counter", "challenge")

# Measured per video (evidence: produccion/tactical/v4/COSTES.md). Max values are used for the budget check.
MEASURED = {
    "voice_credits": {"samples": {"ram-v2": 348, "ram-v1": 426, "hammer": 447, "spain": 478, "flare": 508}, "max": 508},
    "scribe_credits": {"samples": {"ram-v2": 94, "ram-v1": 156, "flare": 166}, "max": 166},
    "render_s": {"samples": {"tactical-quality": 1700, "ram-v2": 1858, "ram-v1": 1960}, "max": 1960},
}


class PlanError(ValueError):
    pass


def load_profile(path=PROFILE):
    with open(path, encoding="utf-8") as f:
        c = json.load(f)
    check_shadow(c)
    return c


def check_shadow(c):
    """The planner only runs on a shadow profile. Anything that could publish is refused."""
    bad = []
    if c.get("publishing", {}).get("mode") != "shadow":
        bad.append(f"publishing.mode={c.get('publishing', {}).get('mode')!r}")
    if c.get("delegation", {}).get("verifier") != "blocked":
        bad.append(f"delegation.verifier={c.get('delegation', {}).get('verifier')!r}")
    if "-S{n" not in c.get("content_id", ""):
        bad.append(f"content_id={c.get('content_id')!r} (shadow ids must use S<nn>)")
    if sorted(c.get("formats", [])) != sorted(FORMATS):
        bad.append(f"formats={c.get('formats')}")
    if bad:
        raise PlanError("not a V4 shadow profile: " + ", ".join(bad))


def check_not_revoked(c, flag=REVOKED_FLAG):
    if "REVOKED" in str(c.get("status", "")).upper() or os.path.exists(flag):
        raise PlanError("V4 shadow production is revoked (profile status or state/tactical-v4/REVOKED): nothing is planned")


def load_concepts(path=CONCEPTS):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _hm(s):
    h, m = map(int, s.split(":"))
    return h * 60 + m


def _fmt(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def _at(d, minutes, c):
    return dt.datetime(d.year, d.month, d.day, minutes // 60, minutes % 60, tzinfo=ts.sydney(c))


def _calendar_times(readback, c):
    out = []
    for p in readback.get("data", readback):
        nets = {x.get("network") for x in p.get("providers", [])}
        if not nets & set(ts.NETWORKS):
            continue
        try:
            out.append((ts._post_time(p, c), p.get("id")))
        except (KeyError, ValueError):
            out.append((None, p.get("id")))
    return out


def free_time(d, minutes, taken, cal, c, trial_offset):
    """True when a reel at `minutes` (and its +trial_offset IG trial reel) is more than the collision window away
    from every calendar post and every other planned reel/trial of the day."""
    win = c["collision_window_min"]
    mine = [minutes] + ([minutes + trial_offset] if trial_offset else [])
    others = []
    for t in taken:
        others += [t] + ([t + trial_offset] if trial_offset else [])
    for a in mine:
        if any(abs(a - b) <= win for b in others):
            return False
        at = _at(d, a, c) if a < 24 * 60 else _at(d + dt.timedelta(days=1), a - 24 * 60, c)
        for t, _ in cal:
            if t is None or abs((t - at).total_seconds()) <= win * 60:
                return False
    return True


def plan_day(date, readback, used=(), requested=None, c=None, concepts=None, trial_reels=True, flag=REVOKED_FLAG,
             live=None):
    """Plan one Sydney date. `requested` = number of videos asked for (default: every slot). `live` maps a slot
    number to the Metricool id of the LIVE V3 video already scheduled in it (from the studio ledger): that slot
    is reported as covered by the live pilot (the two current videos keep running) instead of re-planned.
    Returns the plan; never writes anywhere. Raises PlanError for a revoked or non-shadow profile."""
    live = {int(k): str(v) for k, v in (live or {}).items()}
    c = c or load_profile()
    check_shadow(c)
    check_not_revoked(c, flag)
    concepts = concepts or load_concepts()
    d = date if isinstance(date, dt.date) else dt.date.fromisoformat(date)
    slots = ts.slot_numbers(c)
    cap = c["max_videos_per_day"]
    requested = len(slots) if requested is None else int(requested)
    rejected = []
    if requested > cap:
        rejected = [{"n": n, "why": f"max_videos_per_day={cap}: video {n} rejected (never queued, never moved to another day)"}
                    for n in range(cap + 1, requested + 1)]
    want = [n for n in slots if n <= min(requested, cap)]
    trial = c["schedule"]["trial_reel_offset_min"] if trial_reels else 0
    cal = _calendar_times(readback, c)
    history = list(used) + list(concepts.get("pre_ledger_history", []))
    videos, taken, families = [], [], set()
    for n in want:
        s = c["slots"][str(n)]
        cid = ts.content_id(d, n, c)
        ts.parse_cid(cid, c)  # the id is valid for this profile
        base = _hm(s["time"])
        row = {"cid": cid, "n": n, "format": s["format"], "label": s["label"], "slot_initial": s["time"]}
        if n in live:
            mine = [t for t, i in cal if str(i) == live[n]]
            if mine and mine[0] == _at(d, base, c):
                taken.append(base)
                row.update(status="live_v3", time=s["time"], metricool_id=live[n], trial_reel=_fmt(base + trial) if trial else None,
                           why="slot already holds the live V3 video (pilot keeps running); shadow does not duplicate it")
                videos.append(row)
                continue
        hits = [h for h in ts.collisions(readback, d, c) if h["slot"] in (n, "?")]
        time = None
        if free_time(d, base, taken, cal, c, trial):
            time = base
        else:
            row["blocked_by"] = hits or [{"why": "own trial reel / another planned slot within the window"}]
            for step in range(30, 3 * 60 + 1, 30):  # nearest free half hour, earlier first, 08:00–21:00
                for m in (base - step, base + step):
                    if 8 * 60 <= m <= 21 * 60 and free_time(d, m, taken, cal, c, trial):
                        time = m
                        break
                if time is not None:
                    break
        if time is None:
            row.update(status="empty", why="no free time within ±3 h that keeps the ±60 min window (incl. trial reels)")
            videos.append(row)
            continue
        pick, skipped = None, []
        for k in [x for x in concepts["concepts"] if x["format"] == s["format"]]:
            if k["family"].lower() in families:
                skipped.append({"id": k["id"], "why": "same family already planned today"})
                continue
            rc = ts.repeat_check(k["family"], k["variant"], k["concepts"], d, plays=history, c=c)
            if rc["ok"]:
                pick = k
                break
            skipped.append({"id": k["id"], "why": rc["blocked_by"]})
        if not pick:
            row.update(status="empty", why=f"no unrepeated {s['format']} concept left", skipped=skipped)
            videos.append(row)
            continue
        taken.append(time)
        families.add(pick["family"].lower())
        history.append({"cid": cid, "date": d.isoformat(), "family": pick["family"], "variant": pick["variant"],
                        "concepts": pick["concepts"], "play_id": pick["id"]})
        row.update(status="planned", time=_fmt(time), moved=time != base, concept=pick["id"], family=pick["family"],
                   variant=pick["variant"], question=pick["question"], cta=pick["cta"], play=pick["play"],
                   play_status=pick["play_status"], skipped=skipped,
                   trial_reel=_fmt(time + trial) if trial else None,
                   destinations=[f"{cid}:{net}" for net in ts.NETWORKS])
        videos.append(row)
    planned = [v for v in videos if v["status"] == "planned"]
    history_out = history[len(list(used)) + len(concepts.get("pre_ledger_history", [])):]
    dests = [x for v in planned for x in v["destinations"]]
    return {"date": d.isoformat(), "profile": c["version"], "mode": "shadow", "dry_run": True, "writes": [],
            "videos": videos, "rejected": rejected, "destinations": dests, "n_destinations": len(dests),
            "create_calls_planned": len(planned), "budget": budget(len(planned), c), "_new_history": history_out}


def plan_range(start, days, readback, used=(), live_by_date=None, **kw):
    """Consecutive days share the repetition history: a concept planned on day 1 blocks it on day 2."""
    d0 = start if isinstance(start, dt.date) else dt.date.fromisoformat(start)
    hist, out = list(used), []
    for i in range(days):
        d = d0 + dt.timedelta(days=i)
        p = plan_day(d, readback, hist, live=(live_by_date or {}).get(d.isoformat()), **kw)
        hist += p.pop("_new_history")
        out.append(p)
    return out


def budget(n, c):
    """Worst-case measured cost for n videos against the profile's per-day budget."""
    b = c["budget_per_day"]
    need = {"voice_takes": n, "voice_credits": n * MEASURED["voice_credits"]["max"],
            "scribe_credits": n * MEASURED["scribe_credits"]["max"], "final_renders": n,
            "create_calls": n, "publications": n * len(ts.NETWORKS),
            "render_s": n * MEASURED["render_s"]["max"]}
    over = {k: {"need": v, "limit": b[k], "missing": v - b[k]} for k, v in need.items() if k in b and v > b[k]}
    return {"need": need, "limit": {k: b[k] for k in need if k in b}, "ok": not over, "over": over,
            "credits_per_video_max": MEASURED["voice_credits"]["max"] + MEASURED["scribe_credits"]["max"]}


def spend_guard(spent, kind, amount, c):
    """Explicit budget control for shadow spend (same rule as Studio.spend): refuse anything past the limit."""
    lim = c["budget_per_day"].get(kind)
    if lim is None:
        raise PlanError(f"no budget defined for {kind!r}: refused")
    if spent.get(kind, 0) + amount > lim:
        raise PlanError(f"budget {kind}: {spent.get(kind, 0)}+{amount} > {lim}")
    spent[kind] = spent.get(kind, 0) + amount
    return spent


def best_schedule(path=BEST_TIME, k=4, trial_offset=120, window=60, start="08:00", end="21:00", step=30):
    """Data-based grid: maximise the summed audience-activity score (each network normalised to its own max,
    averaged over 7 days) under the collision rule, with or without the +2 h trial reels."""
    data = json.load(open(path, encoding="utf-8"))["data"]
    score = [0.0] * 24
    for dd in data.values():
        mx = max(max(v) for v in dd.values())
        for v in dd.values():
            for h in range(24):
                score[h] += v[h] / mx / (7 * len(data))

    def s(m):
        a, f = divmod(m, 60)
        return score[a] * (1 - f / 60) + score[min(a + 1, 23)] * f / 60

    def ok(sl, off):
        if any(abs(a - b) <= window for a, b in itertools.combinations(sl, 2)):
            return False
        return not off or not any(abs(a + off - b) <= window for a in sl for b in sl)

    cands = range(_hm(start), _hm(end) + 1, step)
    out = {}
    for name, off in (("with_trial_reels", trial_offset), ("without_trial_reels", 0)):
        best = max(((sum(s(m) for m in sl), sl) for sl in itertools.combinations(cands, k) if ok(sl, off)), default=None)
        out[name] = {"slots": [_fmt(m) for m in best[1]], "score": round(best[0], 3)} if best else None
    base = tuple(_hm(x) for x in ("10:00", "13:00", "16:00", "19:00"))
    out["initial_10_13_16_19"] = {"score": round(sum(s(m) for m in base), 3), "valid_with_trial_reels": ok(base, trial_offset)}
    out["hourly_score"] = {f"{h:02d}": round(score[h], 3) for h in range(6, 23)}
    out["note"] = "Metricool best-time = audience activity, not retention; re-check after 4 weeks of 4/day data"
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("plan"); p.add_argument("date"); p.add_argument("--readback", required=True)
    p.add_argument("--used"); p.add_argument("--requested", type=int); p.add_argument("--out")
    p.add_argument("--no-trial-reels", action="store_true"); p.add_argument("--days", type=int, default=1)
    p.add_argument("--live", help='JSON {"<date>": {"1": "<metricool id>", ...}} of live V3 videos')
    sp.add_parser("schedule")
    a = ap.parse_args(argv)
    if a.cmd == "plan":
        used = ts.read_plays(a.used) if a.used else []
        out = plan_range(a.date, a.days, json.load(open(a.readback)), used, json.loads(a.live) if a.live else None,
                         requested=a.requested, trial_reels=not a.no_trial_reels)
    else:
        out = best_schedule()
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    if getattr(a, "out", None):
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(txt + "\n")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
