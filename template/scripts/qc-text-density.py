#!/usr/bin/env python3
"""Text density timeline of an episode (props JSON): every on-screen text region (screen items + subtitles) with its
level (1 main data, 2 identification, 3 subtitle, 4 extra info), size, position, duration, overlap and repeats.
  python3 scripts/qc-text-density.py props.json [--md out.md] [--json out.json]
Pure reading of the props: no render needed. 2026-11-24 (NBA vs EuroLeague V3 QA B)."""
import argparse, json
LEVEL = {"score": 1, "count3": 1, "fouls": 1, "scoreboard": 1, "verdict": 1, "title": 1, "arcKey": 1, "clocks": 1,
         "league": 2, "leagueLogo": 2, "logo": 2, "section": 4, "chip": 4, "micro": 4, "freeze": 4, "stamp": 4}
TEXTLESS = {"scrim", "whip", "flash", "punch", "tint", "grade", "focus"}


def label(it):
    t = it["type"]
    if t in ("title",): return " / ".join(it["lines"])
    if t == "freeze": return f"FREEZE tag '{it.get('label', 'FREEZE')}'" if it.get("label", "FREEZE") else "freeze corners (no text)"
    if t == "fouls": return f"fouls 1-{it['max']} + FOULED OUT" + (f" + header '{it.get('label', 'PERSONAL FOULS')}'" if it.get("label", "PERSONAL FOULS") else "")
    if t == "scoreboard": return f"board {it['league']} {it.get('period')} {it['clock']}" + (" + teams/scores" if it.get("teams") else "") + (" + shot clock" if it.get("shot", 24) is not None else "")
    if t == "arcKey": return " | ".join(f"{r['league']} {r['value']}" for r in it["rows"])
    if t == "count3": return "count 1-2-3"
    if t in ("league", "leagueLogo"): return f"{t} {it['league']}"
    if t == "logo": return "E2A logo"
    return str(it.get("text", t)) + (f" ({it['sub']})" if it.get("sub") else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("props"); ap.add_argument("--md"); ap.add_argument("--json")
    a = ap.parse_args()
    ep = json.load(open(a.props))["episode"]
    shots = ep["shots"]
    ends = [s["at"] for s in shots[1:]] + [ep["words"][-1]["end"] + ep["tail"]]
    T = ends[-1]
    regs = []
    for s, e in zip(shots, ends):
        for it in s.get("screen", []):
            if it["type"] in TEXTLESS: continue
            if it["type"] == "freeze" and not it.get("label", "FREEZE"): continue
            t0 = max(s["at"], s["at"] + it.get("from", 0) + it.get("delay", 0))
            t1 = min(e, s["at"] + (it.get("to", 99) if it.get("to") is not None else 99))
            if t1 - t0 < 0.05: continue
            # continuous items repeated across shots (negative from) count once
            same = next((r for r in regs if r["label"] == label(it) and abs(r["t1"] - t0) < 0.05), None)
            if same: same["t1"] = round(t1, 2); continue
            regs.append({"t0": round(t0, 2), "t1": round(t1, 2), "type": it["type"], "level": LEVEL.get(it["type"], 4), "label": label(it),
                         "y": it.get("y"), "size": it.get("size"), "shot": s["id"]})
    # subtitles: hidden ranges
    hide = ep.get("subtitleHide", [])
    sub_on = [w for w in ep["words"] if not any(h0 <= w["start"] < h1 for h0, h1 in hide)]
    sub_txt = " ".join(w["text"] for w in sub_on).lower()
    for r in regs:
        r["dur"] = round(r["t1"] - r["t0"], 2)
        txt = r["label"].lower()
        r["repeatsSubtitle"] = any(len(x) > 3 and x in sub_txt for x in txt.replace("/", " ").split() if x.isalpha()) if r["type"] in ("title", "chip", "micro", "section") else False
    # max simultaneous informative regions (levels 1 and 4) + subtitle
    peak, peak_t, over = 0, 0, []
    t = 0.0
    while t < T:
        info = [r for r in regs if r["t0"] <= t < r["t1"] and r["level"] in (1, 4)]
        sub = any(w["start"] - 0.03 <= t < w["end"] + 0.35 for w in sub_on)
        n = len(info) + (1 if sub else 0)
        if n > peak: peak, peak_t = n, t
        if n > 2: over.append(round(t, 1))
        t += 0.1
    lv = {k: sum(1 for r in regs if r["level"] == k) for k in (1, 2, 4)}
    summary = {"regions": len(regs), "byLevel": lv, "peakInformative": peak, "peakAt": round(peak_t, 1), "secondsAbove2": round(len(over) * 0.1, 1),
               "subtitleWords": len(sub_on), "totalWords": len(ep["words"]), "subtitleCase": ep.get("subtitleCase", "upper")}
    if a.json: json.dump({"summary": summary, "regions": regs}, open(a.json, "w"), indent=1)
    if a.md:
        L = [f"| De | A | Dur. | Nivel | Tipo | Texto | y | tamaño | ¿Repite subtítulo? |", "|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(regs, key=lambda r: r["t0"]):
            L.append(f"| {r['t0']:.2f} | {r['t1']:.2f} | {r['dur']:.2f} | {r['level']} | {r['type']} | {r['label']} | {r['y'] or ''} | {r['size'] or ''} | {'sí' if r['repeatsSubtitle'] else 'no'} |")
        open(a.md, "w").write("\n".join(L) + "\n")
    print(json.dumps(summary))


main()
