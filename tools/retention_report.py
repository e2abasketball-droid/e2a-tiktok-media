#!/usr/bin/env python3
"""E2A V4 retention report from a Metricool analytics snapshot (owner brief 2026-11-14 16:28Z).

Rules: never infer retention from views; never declare a winner by volume. Every ratio carries its numerator,
denominator and N; a missing metric is labelled MISSING, not estimated. Metricool returns LIFETIME values at the
time of the read, so a 24 h / 72 h / 7 d window only exists if a snapshot was taken at that age (± tolerance).

  python3 tools/retention_report.py produccion/tactical/v4/retencion/snapshot-*.json [--md]
"""
import argparse
import datetime as dt
import glob
import json
import sys

WINDOWS = {"24h": 24, "72h": 72, "7d": 168}
TOL_H = 6


def window_of(age_h):
    for k, h in WINDOWS.items():
        if abs(age_h - h) <= TOL_H:
            return k
    return f"other ({age_h:.1f} h)"


def instagram_rows(snap):
    cols = snap["instagram_cols"]
    reg = {r.get("ig_reel"): r for r in snap["registry"]}
    taken = dt.datetime.fromisoformat(snap["taken_at"].replace("Z", "+00:00"))
    out = []
    for row in snap["instagram"]:
        r = dict(zip(cols, row))
        meta = reg.get(r["reel_id"])
        if not meta:
            continue
        pub = dt.datetime.fromisoformat(meta["published_utc"].replace("Z", "+00:00"))
        age = (taken - pub).total_seconds() / 3600
        dur = meta.get("duration_s")
        reach = r["reach"]
        out.append({
            "key": meta["key"], "format": meta["format"], "age_h": round(age, 1), "window": window_of(age),
            "duration_s": dur, "reach": reach,
            # Metricool avg watch time = total watch time / reach (checked: 821779.5 / 46359 = 17.73 ≈ 17.744)
            "avg_watch_s": r["avg_watch_s"],
            "avg_watch_pct": round(100 * r["avg_watch_s"] / dur, 1) if dur else "MISSING (duration)",
            "skip_rate_3s_pct": r["skip_rate_3s"], "view_rate_3s_pct": r["view_rate_3s"],
            "retention_IGRE27": r["retention(IGRE27)"] if r["retention(IGRE27)"] is not None else "MISSING",
            "saves_per_1000_reach": round(1000 * r["saves"] / reach, 1) if reach else None,
            "shares_per_1000_reach": round(1000 * r["shares"] / reach, 1) if reach else None,
            "denominator": f"reach={reach} (people), N=1 post",
        })
    return out


def report(paths):
    rows, missing = [], set()
    for p in paths:
        s = json.load(open(p))
        rows += [dict(r, snapshot=s["taken_at"]) for r in instagram_rows(s)]
        missing |= {f"tiktok: {m}" for m in s["tiktok"]["missing"]} | {f"youtube: {m}" for m in s["youtube"]["missing"]}
    by_window = {}
    for r in rows:
        by_window.setdefault(r["window"], []).append(r)
    comparable = {k: v for k, v in by_window.items() if k in WINDOWS and len({x["format"] for x in v}) > 1}
    return {"rows": rows, "missing": sorted(missing), "comparable_windows": sorted(comparable),
            "verdict": "no winner: comparisons need the same window, same format family and N ≥ 3 per arm" if not any(
                len(v) >= 6 for v in comparable.values()) else "enough rows for a descriptive comparison (still no causal claim)"}


def md(rep):
    h = "| pieza | formato | edad | ventana | dur. s | alcance | media vista s | % medio visto | salto 3 s % | guardados ‰ | compartidos ‰ |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
    for r in rep["rows"]:
        h += (f"| {r['key']} | {r['format']} | {r['age_h']} h | {r['window']} | {r['duration_s']} | {r['reach']} | {r['avg_watch_s']} | "
              f"{r['avg_watch_pct']} | {r['skip_rate_3s_pct']} | {r['saves_per_1000_reach']} | {r['shares_per_1000_reach']} |\n")
    return h + "\nFaltan: " + "; ".join(rep["missing"]) + f"\n\nVeredicto: {rep['verdict']}\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshots", nargs="+")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    paths = [p for g in a.snapshots for p in glob.glob(g)]
    rep = report(paths)
    print(md(rep) if a.md else json.dumps(rep, indent=1, ensure_ascii=False))
    sys.exit(0)
