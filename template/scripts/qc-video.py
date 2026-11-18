#!/usr/bin/env python3
"""E2A Tactical Studio — QC on the REAL rendered video (complements qc-tactical3d.mts and qc-bounds.mts,
which judge the episode data and the screen boxes without drawing the 3D scene).

  python3 scripts/qc-video.py tactical/episodes/<id>.json <render.mp4> --out <dir> [--words <words.json>]

Reuses an existing MP4 (no new render). Writes <dir>/qc-video.json (agent-readable) and
<dir>/contact-sheet.png (moments picked from the episode: hook, freeze, screens, decision, catch, result).

Objective checks (FAIL): technical format, loudness −14 ±1 LUFS and true peak ≤ −1 dBTP.
Visual checks not validated on enough episodes yet (WARN):
  transient   1–3 frame "pop" (frame differs from both neighbours while the neighbours match): a near-camera
              occluder or a flash. Validated on Stagger V2 frames 96–97 (the backboard frame bar).
  cuts        hard cuts detected in the video vs the planned shot starts (a cut where none is planned, or a
              planned shot that starts on a cut = informative only).
  flat_band   a wide column band with almost no texture covering most of the height of a frame (big flat
              object in front of the lens).
"""
import argparse, json, os, subprocess, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.dirname(HERE)
SW, SH = 135, 240  # analysis size (1/8)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe(mp4):
    p = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', mp4]).stdout)
    v = next(s for s in p['streams'] if s['codec_type'] == 'video')
    a = next((s for s in p['streams'] if s['codec_type'] == 'audio'), {})
    n, d = map(int, v['r_frame_rate'].split('/'))
    return {'width': v['width'], 'height': v['height'], 'fps': n / d, 'vcodec': v['codec_name'], 'acodec': a.get('codec_name'),
            'duration': float(p['format']['duration']), 'mb': int(p['format']['size']) / 1e6}


def loudness(mp4):
    import re
    e = run(['ffmpeg', '-nostats', '-i', mp4, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
    s = e[e.rfind('Summary:'):]
    return float(re.search(r'I:\s*(-?[\d.]+) LUFS', s).group(1)), float(re.search(r'Peak:\s*(-?[\d.]+) dBFS', s).group(1))


def frames_gray(mp4):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp4, '-vf', f'scale={SW}:{SH},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, SH, SW).astype(np.float32)


def transients(F, fps, k_max=3, spike=4.0):
    """frames n..n+k-1 (k ≤ 3) that jump away from the camera's motion path and come back: the entry and the
    exit differences are ≥ 4× the local per-frame motion (median of ±6 frames around), and frame n-1 is
    close to frame n+k again (≤ 2× the motion expected over k+1 frames)"""
    D = np.array([0.0] + [float(np.abs(F[i] - F[i - 1]).mean()) for i in range(1, len(F))])
    d = lambda a, b: float(np.abs(F[a] - F[b]).mean())
    out, n = [], 1
    while n < len(F) - 1:
        ctx = np.concatenate([D[max(1, n - 6):n], D[n + k_max + 1:n + k_max + 7]])
        med = max(float(np.median(ctx)) if len(ctx) else 1.0, 1.0)
        hit = None
        if D[n] >= max(6.0, spike * med):
            for k in range(1, k_max + 1):
                if n + k >= len(F):
                    break
                if D[n + k] >= spike * med and d(n - 1, n + k) <= 2 * (k + 1) * med:
                    hit = {'frame': n, 'frames': k, 't': round(n / fps, 3), 'enter': round(float(D[n]), 1), 'leave': round(float(D[n + k]), 1),
                           'motion_per_frame': round(med, 1), 'back_to_path': round(d(n - 1, n + k), 1)}
                    break
        if hit:
            out.append(hit)
            n += hit['frames'] + 1
        else:
            n += 1
    return out


def cuts(F, fps, thr=14.0):
    """hard cut = a single-frame jump ≥ 14 (mean abs luma, 0–255) and ≥ 3× both neighbouring frame steps
    (a fast camera move raises several consecutive steps and is not a cut)"""
    D = [0.0] + [float(np.abs(F[i] - F[i - 1]).mean()) for i in range(1, len(F))]
    out = []
    for i in range(1, len(D)):
        nb = max(D[i - 1] if i > 1 else 0.0, D[i + 1] if i + 1 < len(D) else 0.0)
        if D[i] >= thr and D[i] >= 3 * max(nb, 1.0):
            out.append({'frame': i, 't': round(i / fps, 3), 'diff': round(D[i], 1)})
    return out


def flat_band(F, fps, min_cols=0.08, min_rows=0.7):
    """columns whose vertical texture (std of horizontal gradient) is ~0 over ≥70 % of the height, in a
    contiguous band ≥ 8 % of the width"""
    out = []
    for i, f in enumerate(F):
        gx = np.abs(np.diff(f, axis=1))  # SH x SW-1
        flat = (gx < 1.5).mean(axis=0) >= min_rows
        bright = f[:, :-1].mean(axis=0) > 140
        band = flat & bright
        best = cur = 0
        for b in band:
            cur = cur + 1 if b else 0
            best = max(best, cur)
        if best >= min_cols * SW:
            out.append({'frame': i, 't': round(i / fps, 3), 'width_pct': round(100 * best / SW, 1)})
    return out


def pick(moments, n=16, gap=0.45):
    chosen = []
    for prio in (1, 2, 3):
        for m in moments:
            if m['prio'] != prio or len(chosen) >= n:
                continue
            if all(abs(m['t'] - c['t']) >= gap for c in chosen):
                chosen.append(m)
    return sorted(chosen, key=lambda m: m['t'])


def sheet(mp4, items, path, cols=6):
    from PIL import Image, ImageDraw, ImageFont
    tw, th = 270, 480
    rows = (len(items) + cols - 1) // cols
    img = Image.new('RGB', (cols * tw, rows * (th + 34)), (11, 28, 61))
    dr = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
    except OSError:
        font = ImageFont.load_default()
    for k, it in enumerate(items):
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f"{it['t']:.3f}", '-i', mp4, '-frames:v', '1', '-vf', f'scale={tw}:{th}',
                              '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        if len(raw) != tw * th * 3:
            continue
        tile = Image.frombytes('RGB', (tw, th), raw)
        x, y = (k % cols) * tw, (k // cols) * (th + 34)
        img.paste(tile, (x, y))
        col = (255, 90, 90) if it.get('flag') else (201, 162, 77)
        dr.text((x + 6, y + th + 3), f"{it['t']:.2f}s", fill=col, font=font)
        dr.text((x + 6, y + th + 18), it['label'][:34], fill=(255, 255, 255), font=font)
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('episode'); ap.add_argument('mp4'); ap.add_argument('--out', required=True); ap.add_argument('--words')
    ap.add_argument('--config', default=os.path.join(TEMPLATE, '..', 'config', 'tactical_studio.json'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    cfg = json.load(open(a.config)) if os.path.exists(a.config) else {}
    aud = cfg.get('audio', {'lufs_target': -14.0, 'lufs_tolerance': 1.0, 'true_peak_max': -1.0})
    cmd = ['node', '--experimental-strip-types', 'scripts/qc-moments.mts', os.path.abspath(a.episode)] + ([os.path.abspath(a.words)] if a.words else [])
    mo = json.loads(run(cmd, cwd=TEMPLATE, check=True).stdout)
    timing = {'moments_s': round(time.time() - t0, 2)}
    tech = probe(a.mp4)
    I, TP = loudness(a.mp4)
    timing['probe_loudness_s'] = round(time.time() - t0 - timing['moments_s'], 2)
    t1 = time.time()
    F = frames_gray(a.mp4)
    fps = tech['fps']
    tr, ct, fb = transients(F, fps), cuts(F, fps), flat_band(F, fps)
    timing['frame_analysis_s'] = round(time.time() - t1, 2)
    planned = [s['start'] for s in mo['shots'][1:]]
    cut_t = [c['t'] for c in ct]
    unplanned = [c for c in ct if all(abs(c['t'] - p) > 1.5 / fps for p in planned) and not any(abs(c['t'] - x['t']) <= 4 / fps for x in tr)]
    planned_info = [{'shot': s['id'], 'start': round(s['start'], 3), 'hard_cut': any(abs(s['start'] - c) <= 1.5 / fps for c in cut_t)} for s in mo['shots'][1:]]
    items = pick(mo['moments'])
    for x in tr + fb:
        if all(abs(x['t'] - it['t']) > 0.05 for it in items):
            items.append({'t': x['t'], 'label': 'WARN visual defect', 'flag': True, 'kind': 'warn'})
    items.sort(key=lambda m: m['t'])
    t2 = time.time()
    sheet(a.mp4, items, os.path.join(a.out, 'contact-sheet.png'))
    timing['contact_sheet_s'] = round(time.time() - t2, 2)
    checks = {
        'technical': {'pass': tech['width'] == 1080 and tech['height'] == 1920 and tech['fps'] >= 30 and tech['vcodec'] == 'h264', **tech},
        'audio': {'pass': abs(I - aud['lufs_target']) <= aud['lufs_tolerance'] and TP <= aud['true_peak_max'], 'I': I, 'TP': TP,
                  'margin_lu': round(aud['lufs_tolerance'] - abs(I - aud['lufs_target']), 2), 'tp_headroom_db': round(aud['true_peak_max'] - TP, 2)},
    }
    warnings = []
    if tr:
        warnings.append({'check': 'transient', 'why': '1–3 frame pop (near-camera occluder or flash)', 'items': tr})
    if fb:
        warnings.append({'check': 'flat_band', 'why': 'wide flat bright band in front of the lens', 'items': fb})
    if unplanned:
        warnings.append({'check': 'cuts', 'why': 'hard cut where no shot starts', 'items': unplanned})
    timing['total_s'] = round(time.time() - t0, 2)
    rep = {'episode': mo['episode'], 'mp4': os.path.abspath(a.mp4), 'result': 'PASS' if all(c['pass'] for c in checks.values()) else 'FAIL',
           'checks': checks, 'warnings': warnings, 'planned_shots': planned_info, 'moments': items, 'timing': timing,
           'contact_sheet': os.path.join(os.path.abspath(a.out), 'contact-sheet.png'),
           'not_measured': ['player-on-player occlusion (needs depth or an ID pass)', 'text over a key player (needs projected player boxes per frame: see qc-tactical3d rays)']}
    json.dump(rep, open(os.path.join(a.out, 'qc-video.json'), 'w'), indent=1)
    print(json.dumps({'result': rep['result'], 'audio': checks['audio'], 'warnings': [(w['check'], len(w['items'])) for w in warnings], 'timing': timing}))
    sys.exit(0 if rep['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
