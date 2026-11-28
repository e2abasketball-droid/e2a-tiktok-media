#!/usr/bin/env python3
"""E2A Shuffle Cut V1: static tactical diagram (deliverable 1) drawn from the canonical model and the engine frame dump,
i.e. the same simulation as the 3D render (no hand-drawn paths). Owner convention: basket at the TOP, owner x < 0 on the
LEFT. Paths are the engine positions (engine x = -owner x) between the given owner times.

  python3 tools/shuffle_diagram.py --canonical template/tactical/shuffle/e2a_shuffle_cut_v1.json \
      --frames frames.json --out diagram.png [--svg diagram.svg]
frames.json: template/scripts/dump-play-frames.mts output (any fps)."""
import argparse, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, Circle, Rectangle, FancyArrowPatch  # noqa: E402

NAVY, GOLD, GOLD_D, WHITE, RED, GREEN = "#0B1C3D", "#C9A24D", "#A9842F", "#FFFFFF", "#E5483A", "#3BC46B"


def court(ax):
    lw, c = 1.6, "#D9DEE8"
    ax.add_patch(Rectangle((-7.5, 0), 15, 11.0, fc=NAVY, ec="none", zorder=0))
    ax.plot([-7.5, 7.5], [0, 0], color=c, lw=lw)
    ax.add_patch(Rectangle((-2.45, 0), 4.9, 5.8, fc="#13284F", ec=c, lw=lw, zorder=1))
    ax.add_patch(Arc((0, 5.8), 3.6, 3.6, theta1=0, theta2=180, ec=c, lw=lw, zorder=1))
    ax.add_patch(Arc((0, 1.575), 13.5, 13.5, theta1=12.4, theta2=180 - 12.4, ec=c, lw=lw, zorder=1))
    ax.plot([-6.6, -6.6], [0, 2.99], color=c, lw=lw); ax.plot([6.6, 6.6], [0, 2.99], color=c, lw=lw)
    ax.add_patch(Circle((0, 1.575), 0.23, fc="none", ec=GOLD, lw=2, zorder=2))
    ax.plot([-0.9, 0.9], [1.2, 1.2], color=WHITE, lw=3, zorder=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--svg")
    a = ap.parse_args()
    can = json.load(open(a.canonical))
    fr = json.load(open(a.frames))
    off = can["coordinates"]["engine_offset_s"]
    F = fr["frames"]

    def path(pid, t0, t1):
        return [(-f["P"][pid][0], f["P"][pid][1]) for f in F if t0 + off - 1e-6 <= f["t"] <= t1 + off + 1e-6]

    tl = can["timeline_owner_s"]
    k0 = {k: v for k, v in can["anchors_T0"].items()}
    fig, ax = plt.subplots(figsize=(9, 7.6), dpi=200)
    fig.patch.set_facecolor(NAVY)
    court(ax)

    def arrow(pts, col, ls="-", lw=3.0, z=4):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=col, lw=lw, ls=ls, zorder=z, solid_capstyle="round")
        ax.add_patch(FancyArrowPatch(pts[-4] if len(pts) > 4 else pts[0], pts[-1], arrowstyle="-|>", mutation_scale=22, color=col, lw=0, zorder=z + 1))

    # 1 entry pass O2 -> O3 (dashed), 2 O5 to the screen spot, 3 the shuffle cut, X1 chase, 4 O3 -> O1 pass
    o2, o3 = k0["O2"], path("O3", tl.get("k1", 0.85), tl.get("k1", 0.85))[0]
    arrow([o2, ((o2[0] + o3[0]) / 2, (o2[1] + o3[1]) / 2 + 0.25), o3], WHITE, "--", 2.0)
    arrow(path("O3", 0.0, 0.85), WHITE, "-", 1.6)
    arrow(path("O5", 0.25, 1.20), GOLD, "-", 2.4)
    s = can["designed_spots"]["screen_spot_O5"]
    ax.plot([s[0] - 0.5, s[0] + 0.5], [s[1] + 0.38, s[1] + 0.38], color=GOLD, lw=6, zorder=6, solid_capstyle="butt")
    arrow(path("O1", 0.30, 1.55), WHITE, ":", 2.0)
    arrow(path("O1", 1.55, 3.50), GOLD, "-", 3.6, 7)
    arrow(path("X1", 1.70, 3.50), RED, "-", 2.2, 5)
    cpos = can["designed_spots"]["O1_catch"]
    arrow([o3, cpos], GREEN, "--", 2.2)
    for pid, (x, y) in k0.items():
        o = pid[0] == "O"
        ax.add_patch(Circle((x, y), 0.36, fc=WHITE if o else NAVY, ec=GOLD if o else RED, lw=2.2, zorder=9))
        ax.text(x, y, pid, ha="center", va="center", fontsize=8, fontweight="bold", color=NAVY if o else WHITE, zorder=10)
    for lbl, (x, y), col in [("1 entry pass", (2.2, 9.55), WHITE), ("2 back screen", (s[0] - 3.1, s[1] + 0.2), GOLD),
                             ("3 shuffle cut", (cpos[0] - 3.3, cpos[1] - 0.6), GOLD), ("X1 chases", (-4.6, 5.2), RED),
                             ("4 pass in stride", (1.0, 5.4), GREEN)]:
        ax.text(x, y, lbl, color=col, fontsize=9, fontweight="bold", zorder=11)
    ax.text(-7.3, 12.35, "E2A SPORTS  |  SHUFFLE CUT V1", color=GOLD, fontsize=12, fontweight="bold", va="top")
    ax.text(-7.3, 11.55, "T0 formation + engine paths (canonical 5v5 model). One designed coverage: X1 chases, no switch.",
            color=WHITE, fontsize=7.5, va="top")
    ax.set_xlim(-7.6, 7.6); ax.set_ylim(12.6, -0.3)   # basket at the top
    ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(a.out, facecolor=NAVY, bbox_inches="tight")
    if a.svg:
        fig.savefig(a.svg, facecolor=NAVY, bbox_inches="tight")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
