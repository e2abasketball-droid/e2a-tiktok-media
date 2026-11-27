#!/usr/bin/env python3
"""E2A Basketball IQ tactical preview (2026-11-27, EP02): overhead diagrams of ALL 10 players, drawn in the OWNER
coordinate system (basket at the top, negative x on the left), from the engine frame dump (what the render draws).
Panels: K0..K5 with 0.8 s trails, plus the freeze with the three decision lanes coloured by the validator's states.
Writes an HTML page and (with --png) a PNG via the pre-installed Chromium / Playwright.

  python3 tools/iq_tactical_preview.py --canonical ... --frames frames.json --report val.json --out preview.html [--png preview.png]
"""
import argparse, json, math, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import court_geometry as G  # noqa: E402

NAVY, GOLD, WHITE, RED, GREY = "#0B1C3D", "#C9A24D", "#FFFFFF", "#E5483A", "#8A93A6"
STATE_COL = {"OPEN": "#3BC46B", "CONTESTED": "#F2B233", "BLOCKED": RED}
S = 30  # px per metre


def court():
    W, Hh = G.HALF_W, 10.6           # show y 0..10.6 (the action)
    X = lambda x: (x + W) * S
    Y = lambda y: y * S
    s = [f'<rect x="0" y="0" width="{2 * W * S}" height="{Hh * S}" fill="#13284f"/>']
    ln = lambda pts: '<polyline fill="none" stroke="#d8dde8" stroke-opacity="0.55" stroke-width="2" points="' + " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in pts) + '"/>'
    s.append(ln([(-W, 0), (W, 0)]))
    s.append(ln([(-G.KEY_HALF_W, 0), (-G.KEY_HALF_W, G.FT_Y), (G.KEY_HALF_W, G.FT_Y), (G.KEY_HALF_W, 0)]))
    jy = G.HOOP[1] + math.sqrt(G.THREE_R ** 2 - G.CORNER_X ** 2)
    a0 = math.asin((jy - G.HOOP[1]) / G.THREE_R)
    arc = [(G.HOOP[0] + G.THREE_R * math.cos(a), G.HOOP[1] + G.THREE_R * math.sin(a)) for a in [a0 + (math.pi - 2 * a0) * i / 60 for i in range(61)]]
    s.append(ln([(G.CORNER_X, 0), (G.CORNER_X, jy)] + arc + [(-G.CORNER_X, jy), (-G.CORNER_X, 0)]))
    s.append(ln([(1.8 * math.cos(a), G.FT_Y + 1.8 * math.sin(a)) for a in [i * math.pi / 30 for i in range(31)]]))
    s.append(f'<circle cx="{X(0)}" cy="{Y(G.HOOP[1])}" r="{0.23 * S}" fill="none" stroke="{GOLD}" stroke-width="3"/>')
    s.append(f'<line x1="{X(-0.9)}" y1="{Y(1.2)}" x2="{X(0.9)}" y2="{Y(1.2)}" stroke="#ffffff" stroke-width="4"/>')
    s.append(f'<circle cx="{X(0)}" cy="{Y(G.NAIL[1])}" r="3" fill="{GOLD}"/>')
    return s, X, Y, 2 * W * S, Hh * S


def panel(frames, off, t, title, sub, lanes=None, trail=0.8, can=None):
    s, X, Y, w, h = court()
    pos = lambda f, i: (-f["P"][i][0], f["P"][i][1])
    fps = 120
    idx = lambda tt: min(len(frames) - 1, max(0, round((tt + off) * fps)))
    f = frames[idx(t)]
    ids = list(f["P"])
    for i in ids:
        pts = [pos(frames[n], i) for n in range(idx(t - trail), idx(t) + 1, 4)]
        col = GOLD if i[0] == "O" else RED
        s.append('<polyline fill="none" stroke="%s" stroke-opacity="0.55" stroke-width="3" stroke-dasharray="%s" points="%s"/>' % (
            col, "" if i[0] == "O" else "6 5", " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in pts)))
    if lanes:
        for (a, b, st, lab, lp) in lanes:
            s.append(f'<line x1="{X(a[0]):.1f}" y1="{Y(a[1]):.1f}" x2="{X(b[0]):.1f}" y2="{Y(b[1]):.1f}" stroke="{STATE_COL[st]}" stroke-width="5" stroke-opacity="0.9"/>')
            s.append(f'<text x="{X(lp[0]):.1f}" y="{Y(lp[1]):.1f}" fill="{STATE_COL[st]}" font-size="16" font-weight="800" text-anchor="middle" '
                     f'stroke="#0B1C3D" stroke-width="4" paint-order="stroke">{lab} {st}</text>')
    for i in ids:
        p = pos(f, i)
        hd = G.engine_heading_to_owner_dir(f["P"][i][4])
        if i[0] == "O":
            s.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="13" fill="{WHITE}" stroke="{GOLD}" stroke-width="3"/>')
            s.append(f'<text x="{X(p[0]):.1f}" y="{Y(p[1]) + 5:.1f}" fill="{NAVY}" font-size="13" font-weight="900" text-anchor="middle">{i[1]}</text>')
        else:
            s.append(f'<line x1="{X(p[0]):.1f}" y1="{Y(p[1]):.1f}" x2="{X(p[0] + hd[0] * 0.7):.1f}" y2="{Y(p[1] + hd[1] * 0.7):.1f}" stroke="{RED}" stroke-width="2"/>')
            s.append(f'<rect x="{X(p[0]) - 12:.1f}" y="{Y(p[1]) - 12:.1f}" width="24" height="24" rx="5" fill="{RED}"/>')
            s.append(f'<text x="{X(p[0]):.1f}" y="{Y(p[1]) + 5:.1f}" fill="{WHITE}" font-size="13" font-weight="900" text-anchor="middle">X{i[1]}</text>')
    b = (-f["B"][0], f["B"][1], f["B"][2])
    s.append(f'<circle cx="{X(b[0]):.1f}" cy="{Y(b[1]):.1f}" r="{5 + b[2] * 2:.1f}" fill="#F08A24" stroke="#000" stroke-width="1.5"/>')
    head = f'<div class="p"><div class="h"><b>{title}</b><span>{sub}</span></div><svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
    return head + "".join(s) + "</svg></div>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--png")
    a = ap.parse_args()
    can = json.load(open(a.canonical))
    dump = json.load(open(a.frames))
    rep = json.load(open(a.report))
    off = can["coordinates"]["engine_offset_s"]
    F = dump["frames"]
    notes = {"K0": "screen set, X5 at the level, O1 has the ball", "K1": "TWO ON THE BALL, outlet recognised (0.80), release 0.86",
             "K2": "O5 caught (1.45), faces up at the nail: 4 ON 3", "K3": "FREEZE: X4 in the paint, O4 starts behind him",
             "K4": "O4 catches the bounce pass (3.05)", "K5": "layup release (3.70)"}
    P = [panel(F, off, k["t"], f"{k['k']}  t = {k['t']:.2f} s", notes[k["k"]]) for k in can["keyframes"]]
    fz = F[round((can["decision"]["freeze_t"] + off) * 120)]
    pos = lambda i: (-fz["P"][i][0], fz["P"][i][1])
    dl = rep["decision_lanes"]
    k4 = can["keyframes"][4]["O4"]
    lanes = [(pos("O5"), (0, G.HOOP[1]), dl["A_drive"]["state"], "A DRIVE", (2.4, 2.6)), (pos("O5"), pos("O3"), dl["B_corner"]["state"], "B CORNER", (-4.6, 2.2)),
             (pos("O5"), k4, dl["C_cut"]["state"], "C CUT", (-2.6, 3.1))]
    P.append(panel(F, off, can["decision"]["freeze_t"], "DECISION at the freeze (2.30 s)", "lane states computed by tools/iq_play_validate.py", lanes, 1.5))
    css = ("body{margin:0;background:#081428;color:#fff;font-family:Inter,Arial,sans-serif}.g{display:grid;grid-template-columns:repeat(4,max-content);gap:14px;padding:16px}"
           ".p{background:#0B1C3D;border:1px solid #23375f;border-radius:10px;padding:8px}.h{display:flex;flex-direction:column;margin:0 0 6px 2px}"
           ".h b{color:#C9A24D;font-size:17px}.h span{color:#c9d1e0;font-size:12.5px}h1{font-size:22px;margin:16px 16px 0;color:#C9A24D}"
           "p.k{margin:4px 16px;color:#c9d1e0;font-size:13px}")
    verdict = f"Validator verdict: {rep['verdict']} ({rep['passed']} pass, {rep['warnings']} warn, {rep['failed']} fail)."
    html = (f"<!doctype html><html><head><meta charset='utf-8'><title>IQ 02 tactical preview</title><style>{css}</style></head><body>"
            f"<h1>Basketball IQ 02 - Beat the Blitz: tactical preview (all 10 players)</h1>"
            f"<p class='k'>Owner coordinates, basket at the top, negative x on the left. White circles = offence, red squares = defence (line = body heading). Trails = last 0.8 s. Orange = ball (bigger = higher). {verdict}</p>"
            f"<div class='g'>{''.join(P)}</div></body></html>")
    open(a.out, "w").write(html)
    print("wrote", a.out)
    if a.png:
        js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1960,height:900},deviceScaleFactor:%d});"
              "await p.goto('file://%s');await p.screenshot({path:'%s',fullPage:true});await b.close();})();") % (1, os.path.abspath(a.out), os.path.abspath(a.png))
        subprocess.run(["node", "-e", js], check=True)
        print("wrote", a.png)


if __name__ == "__main__":
    main()
