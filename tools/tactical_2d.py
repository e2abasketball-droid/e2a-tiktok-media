#!/usr/bin/env python3
"""E2A Tactical — 2D tactical pass (2026-11-20, master prompt 3D sec. 4.2): a clean top view of one or more plays,
numbered players, the ball always visible, metres on the axes, the house camera convention (basket at the TOP, x > 0
on the LEFT of the picture, as seen from half court) and the strong / weak side. Reads the 30 fps dumps written by
template/scripts/play-dump.mts, i.e. the SAME pure functions and timings as the 3D render and the QC.

  python3 tools/tactical_2d.py --dump A.json --dump B.json --out pass2d.mp4 --sheet pass2d-sheet.png \
      [--marks A:show,hedged,slip,pass,catch,finish B:wait,contact,gather,release] [--size 1080]

MP4: each play in turn (title card in the frame), 1x speed, 1 s trail per player, facing tick, the ball (orange, with
its owner or IN FLIGHT and the flight line), pass segments while the ball travels, and the event marks as they pass.
Sheet: one panel per requested mark, the same drawing frozen at that play time (input for authors, animation and QC).
Needs matplotlib + numpy (pip) and ffmpeg."""
import argparse, json, math, subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, Circle, Rectangle  # noqa: E402

NAVY, GOLD, WHITE, RED, ORANGE, WOOD = '#0E2147', '#F2C76A', '#F3F1EC', '#B3261E', '#E2552A', '#E9D2A8'


def court(ax):
    # FIBA half court, metres (repo axes); the picture is flipped so the basket is at the top and x > 0 on the left
    ax.add_patch(Rectangle((-7.5, 0), 15, 14, fc=WOOD, ec='none', zorder=0))
    lw, c = 2.0, '#FFFFFF'
    ax.plot([-7.5, 7.5, 7.5, -7.5, -7.5], [0, 0, 14, 14, 0], color=c, lw=lw, zorder=1)
    ax.add_patch(Rectangle((-2.45, 0), 4.9, 5.8, fc='#16306B', ec=c, lw=lw, alpha=0.9, zorder=1))
    ax.add_patch(Arc((0, 5.8), 3.6, 3.6, theta1=0, theta2=180, ec=c, lw=lw, zorder=1))
    th = math.degrees(math.asin(6.6 / 6.75))
    ax.add_patch(Arc((0, 1.575), 13.5, 13.5, theta1=90 - th, theta2=90 + th, ec=c, lw=lw, zorder=1))
    yc = 1.575 + 6.75 * math.cos(math.radians(th))
    for x in (-6.6, 6.6):
        ax.plot([x, x], [0, yc], color=c, lw=lw, zorder=1)
    ax.add_patch(Arc((0, 14), 3.6, 3.6, theta1=180, theta2=360, ec=c, lw=lw, zorder=1))
    ax.plot([-0.9, 0.9], [1.2, 1.2], color='#333', lw=3, zorder=2)            # backboard
    ax.add_patch(Circle((0, 1.575), 0.23, fc='none', ec=ORANGE, lw=2.2, zorder=2))
    ax.set_xlim(7.9, -7.9)       # x > 0 on the LEFT (house camera: yaw 0 from half court)
    ax.set_ylim(10.6, -0.6)      # basket at the TOP
    ax.set_aspect('equal')
    ax.set_xticks(range(-7, 8, 1))
    ax.set_yticks(range(0, 11, 1))
    ax.tick_params(labelsize=7, colors='#666')
    ax.grid(color='#00000014', lw=0.6)
    for s in ax.spines.values():
        s.set_visible(False)


def draw(ax, d, i, title, marks_seen, trail=30):
    court(ax)
    rows = d['rows']
    r = rows[i]
    bx = r['ball'][0]
    ax.text(5.0 if bx > 0 else -5.0, 10.25, 'STRONG SIDE (ball)', ha='center', fontsize=8, color=NAVY, weight='bold')
    ax.text(-5.0 if bx > 0 else 5.0, 10.25, 'weak side', ha='center', fontsize=8, color='#555')
    for p in d['players']:
        pid = p['id']
        xs = [rows[k]['players'][pid]['x'] for k in range(max(0, i - trail), i + 1)]
        ys = [rows[k]['players'][pid]['y'] for k in range(max(0, i - trail), i + 1)]
        off = p['team'] == 'O'
        ax.plot(xs, ys, color=NAVY if off else RED, lw=1.2, alpha=0.45, zorder=3)
        q = r['players'][pid]
        ax.add_patch(Circle((q['x'], q['y']), 0.36, fc=NAVY if off else WHITE, ec=GOLD if off else RED, lw=2, zorder=5))
        f = q['chestYaw']
        ax.plot([q['x'], q['x'] + 0.62 * math.cos(f)], [q['y'], q['y'] + 0.62 * math.sin(f)], color=GOLD if off else RED, lw=2.2, zorder=4)
        ax.text(q['x'], q['y'], pid, ha='center', va='center', fontsize=7.5, weight='bold', color=WHITE if off else RED, zorder=6)
    b = r['ball']
    if r['phase'] in ('IN_FLIGHT', 'RELEASED'):
        # the pass segment from the release to the catch spot (where the ball WILL be met)
        j0 = max(k for k in range(i + 1) if rows[k]['phase'] in ('OWNED_BY_PASSER', 'HELD', 'GATHER', 'SECURED', 'CONTACT') or k == 0)
        j1 = next((k for k in range(i, len(rows)) if rows[k]['phase'] == 'CONTACT'), len(rows) - 1)
        ax.plot([rows[j0]['ball'][0], rows[j1]['ball'][0]], [rows[j0]['ball'][1], rows[j1]['ball'][1]], ls='--', color=ORANGE, lw=1.6, zorder=4)
    ax.add_patch(Circle((b[0], b[1]), 0.2 + 0.05 * min(b[2], 4) / 4, fc=ORANGE, ec='#222', lw=1, zorder=7))
    label = r['phase'] + (f" · {r['owner']}" if r['owner'] else '') + f"  z {b[2]:.1f} m"
    ax.set_title(f"{title}   t {r['t']:.2f} s   ball: {label}", fontsize=9, loc='left', color=NAVY)
    seen = [f"{k} {v:.2f}" for k, v in sorted(d['marks'].items(), key=lambda kv: kv[1]) if v <= r['t'] + 1e-6 and k not in ('start',)]
    ax.text(7.6, -0.35, '  ·  '.join(seen[-4:]), fontsize=7, color='#333', va='center')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dump', action='append', required=True)
    ap.add_argument('--out')
    ap.add_argument('--sheet')
    ap.add_argument('--marks', nargs='*', default=[])
    ap.add_argument('--size', type=int, default=1080)
    a = ap.parse_args()
    dumps = [json.load(open(p)) for p in a.dump]
    tags = [chr(65 + k) for k in range(len(dumps))]
    if a.out:
        px = a.size
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{px}x{px}', '-r', '30', '-i', '-',
                               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', a.out], stdin=subprocess.PIPE)
        fig = plt.figure(figsize=(px / 100, px / 100), dpi=100)
        for tag, d in zip(tags, dumps):
            for i in range(len(d['rows'])):
                fig.clf()
                ax = fig.add_axes([0.04, 0.03, 0.94, 0.92])
                draw(ax, d, i, f"{tag} · {d['id']}", None)
                fig.canvas.draw()
                ff.stdin.write(np.asarray(fig.canvas.buffer_rgba()).tobytes())
        ff.stdin.close()
        ff.wait()
        print('mp4', a.out)
    if a.sheet:
        want = []
        for spec in a.marks:
            tag, ks = spec.split(':')
            d = dumps[tags.index(tag)]
            want += [(tag, d, k) for k in ks.split(',')]
        n = len(want)
        cols = 4
        rows_ = math.ceil(n / cols)
        fig = plt.figure(figsize=(cols * 4.2, rows_ * 3.6), dpi=110)
        for k, (tag, d, m) in enumerate(want):
            ax = fig.add_subplot(rows_, cols, k + 1)
            t = d['marks'][m]
            i = min(range(len(d['rows'])), key=lambda j: abs(d['rows'][j]['t'] - t))
            draw(ax, d, i, f"{tag} · {m}", None)
            ax.title.set_fontsize(7)
        fig.tight_layout()
        fig.savefig(a.sheet)
        print('sheet', a.sheet)


if __name__ == '__main__':
    main()
