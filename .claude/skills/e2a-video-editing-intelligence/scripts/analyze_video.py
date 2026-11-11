#!/usr/bin/env python3
"""ANALYZE mode: measure how a reference video is edited and write analysis.json + report.md.

  python3 analyze_video.py <video> <out_dir> [--ref-id R-0001] [--title "..."] [--source-key KEY]
                           [--rights propio|tercero] [--force]

Output in <out_dir>:
  analysis.json   structured analysis (schema e2a.analysis/1), every item tagged with its evidence level
  report.md       the same analysis in Spanish for people, 12 sections
  frames/         representative frames + sheet.jpg (working material: never committed for third-party videos)

Idempotent: if <out_dir>/analysis.json already belongs to the same file (sha256), the same skill
version and the same parameters, nothing is recomputed (use --force to redo it). The measures are
deterministic, so re-running gives the same numbers; only meta.analyzed_at changes.

Evidence levels (common.py): observacion = measured directly; estimacion = inferred from measures
with a known method; hipotesis = a reading that needs a human look at the frames.
Only ffmpeg/ffprobe, Python and numpy are used.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (ANALYSIS_SCHEMA, EST, HYP, OBS, SKILL_VERSION, AnalysisError, dump_json,  # noqa: E402
                    load_json, probe, sha256)
import analyze_audio  # noqa: E402
import extract_frames as xf  # noqa: E402

PARAMS = {"low_fps": 10, "mid_fps": 5, "mid_long_side": 320, "cut_k": 6.0, "cut_min": 3.0,
          "min_shot_s": 0.2, "static_diff": 1.2}
E2A_PALETTE = {"azul_marino": (11, 28, 61), "dorado": (201, 162, 77), "dorado_profundo": (169, 132, 47),
               "blanco": (255, 255, 255)}


# ----------------------------------------------------------------------------- decoding
def mid_frames(path, info, fps):
    """Colour frames for camera, colour, text and overlay measures (uint8, n x h x w x 3)."""
    w, h = xf.low_size(info["width"], info["height"], long_side=PARAMS["mid_long_side"])
    raw = xf.run(["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "error", "-i", path, "-an", "-vf",
                  f"fps={fps},scale={w}:{h}:flags=area,format=rgb24", "-f", "rawvideo", "-"], binary=True)
    n = len(raw) // (w * h * 3)
    if n < 1:
        raise AnalysisError("no se pudieron decodificar fotogramas")
    return np.frombuffer(raw[: n * w * h * 3], dtype=np.uint8).reshape(n, h, w, 3)


def luma(rgb):
    rgb = rgb.astype(np.float32)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


# ----------------------------------------------------------------------------- cuts and transitions
def detect_events(gray, fps):
    """Frame-difference events. Returns (events, diff curve). kind: hard (one frame) or animated."""
    if len(gray) < 3:
        return [], np.zeros(0)
    d = np.abs(np.diff(gray, axis=0)).mean(axis=(1, 2))
    # histogram distance catches cuts between pictures of similar brightness
    hists = np.stack([np.histogram(g, bins=32, range=(0, 255))[0] for g in gray]).astype(np.float32)
    hists /= hists.sum(axis=1, keepdims=True) + 1e-9
    hd = 0.5 * np.abs(np.diff(hists, axis=0)).sum(axis=1) * 100  # 0..100
    score = np.maximum(d, hd * 0.6)
    thr = max(PARAMS["cut_min"], PARAMS["cut_k"] * float(np.median(score)))
    hot = score > thr
    events, i = [], 0
    while i < len(hot):
        if not hot[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(hot) and (hot[j + 1] or (j + 2 < len(hot) and hot[j + 2])):
            j += 1
        peak = i + int(np.argmax(score[i:j + 1]))
        events.append({"i0": i, "i1": j + 1, "t": round((peak + 1) / fps, 2), "dur": round((j - i + 1) / fps, 2),
                       "kind": "hard" if j == i else "animated", "score": round(float(score[peak]), 1)})
        i = j + 1
    return events, score


def classify_transition(gray, ev, fps):
    """Name an event from the frames around it. Returns (tipo, nivel, evidencia)."""
    a = gray[max(0, ev["i0"] - 1)]
    b = gray[min(len(gray) - 1, ev["i1"] + 1)]
    mids = gray[ev["i0"]:ev["i1"] + 1]
    la, lb = float(a.mean()), float(b.mean())
    lm = np.array([float(m.mean()) for m in mids]) if len(mids) else np.array([(la + lb) / 2])
    sharp = lambda f: float(np.abs(np.diff(f, axis=1)).mean())  # noqa: E731
    sa, sb = sharp(a), sharp(b)
    sm = min(sharp(m) for m in mids) if len(mids) else (sa + sb) / 2
    if ev["kind"] == "hard":
        if lm.max() > max(la, lb) + 35:
            return "flash", EST, f"pico de luminancia {lm.max():.0f} frente a {max(la, lb):.0f}"
        return "corte", OBS, "cambio completo entre dos fotogramas consecutivos"
    if lm.max() > max(la, lb) + 35:
        return "flash", EST, f"pico de luminancia {lm.max():.0f} frente a {max(la, lb):.0f}"
    if lm.min() < 14 and min(la, lb) > 25:
        return "fundido_a_negro", EST, f"luminancia mínima {lm.min():.0f}"
    if sm < 0.55 * min(sa, sb):
        return "barrido_con_desenfoque", EST, f"nitidez cae a {sm:.1f} desde {min(sa, sb):.1f} (desenfoque de movimiento)"
    if len(mids):
        k = len(mids) // 2
        blend = 0.5 * (a + b)
        e_blend = float(np.abs(mids[k] - blend).mean())
        e_end = min(float(np.abs(mids[k] - a).mean()), float(np.abs(mids[k] - b).mean()))
        if e_blend < 0.7 * e_end:
            return "fundido_encadenado", EST, f"fotograma intermedio ≈ mezcla de ambos planos ({e_blend:.1f} vs {e_end:.1f})"
    return "transicion_animada", EST, f"cambio repartido en {ev['dur']:.2f} s"


# ----------------------------------------------------------------------------- camera (global motion)
def _window2d(h, w):
    return np.outer(np.hanning(h), np.hanning(w)).astype(np.float32)


def phase_shift(a, b, win):
    """Translation of b relative to a in pixels (dx, dy) and peak sharpness, by phase correlation."""
    A = np.fft.rfft2((a - a.mean()) * win)
    B = np.fft.rfft2((b - b.mean()) * win)
    R = A.conj() * B
    R /= np.abs(R) + 1e-9
    r = np.fft.irfft2(R, s=a.shape)
    iy, ix = np.unravel_index(int(np.argmax(r)), r.shape)
    peak = float(r[iy, ix])
    def sub(c, n, axis_vals):
        l, m, rr = axis_vals
        den = l - 2 * m + rr
        off = 0.5 * (l - rr) / den if abs(den) > 1e-9 else 0.0
        v = c + off
        return v - n if v > n / 2 else v
    h, w = r.shape
    dy = sub(iy, h, (r[(iy - 1) % h, ix], r[iy, ix], r[(iy + 1) % h, ix]))
    dx = sub(ix, w, (r[iy, (ix - 1) % w], r[iy, ix], r[iy, (ix + 1) % w]))
    return dx, dy, peak


def warp(img, s, dx=0.0, dy=0.0):
    """Scale img by s about its centre and shift by (dx, dy), bilinear."""
    h, w = img.shape
    cy, cx = (h - 1) / 2, (w - 1) / 2
    ys = (np.arange(h) - cy - dy) / s + cy
    xs = (np.arange(w) - cx - dx) / s + cx
    ys = np.clip(ys, 0, h - 1.001)
    xs = np.clip(xs, 0, w - 1.001)
    y0, x0 = ys.astype(int), xs.astype(int)
    fy, fx = (ys - y0)[:, None], (xs - x0)[None, :]
    a = img[y0][:, x0]
    b = img[y0][:, x0 + 1]
    c = img[y0 + 1][:, x0]
    d = img[y0 + 1][:, x0 + 1]
    return a * (1 - fy) * (1 - fx) + b * (1 - fy) * fx + c * fy * (1 - fx) + d * fy * fx


def scale_step(a, b, dx, dy):
    """Best zoom factor taking a to b (after removing the translation), parabolic refinement."""
    h, w = a.shape
    m = (slice(int(h * 0.18), int(h * 0.82)), slice(int(w * 0.18), int(w * 0.82)))
    grid = np.linspace(0.94, 1.06, 25)
    errs = np.array([float(np.abs(warp(a, s, dx, dy)[m] - b[m]).mean()) for s in grid])
    k = int(np.argmin(errs))
    if 0 < k < len(grid) - 1:
        l, c, r = errs[k - 1], errs[k], errs[k + 1]
        den = l - 2 * c + r
        off = 0.5 * (l - r) / den if den > 1e-9 else 0
        return float(grid[k] + off * (grid[1] - grid[0])), float(errs[k]), float(np.abs(a[m] - b[m]).mean())
    return float(grid[k]), float(errs[k]), float(np.abs(a[m] - b[m]).mean())


def camera_for_shot(gm, fps, i0, i1):
    """Global motion over one shot from mid-res grey frames gm[i0:i1]. Template names: pan-left means the
    picture moves left and tilt-up means it moves down, as in template/src/pro/camera.tsx."""
    seg = gm[i0:i1]
    if len(seg) < 3:
        return {"movimiento": "indeterminado", "nivel": EST, "motivo": "plano demasiado corto"}
    h, w = seg.shape[1:]
    win = _window2d(h, w)
    step = 2 if len(seg) > 4 else 1
    dxs, dys, logs, resid, peaks, raws = [], [], [], [], [], []
    unexplained = 0
    for k in range(0, len(seg) - step, step):
        a, b = seg[k], seg[k + step]
        dx, dy, pk = phase_shift(a, b, win)
        s, e_fit, e_raw = scale_step(a, b, dx, dy)
        raws.append(e_raw)
        if e_raw < 0.4 or e_fit > 0.6 * e_raw:
            # nothing changes, or a global move does not explain the change (objects, graphics, text)
            dx = dy = 0.0
            s = 1.0
            unexplained += e_raw >= 0.4
        dxs.append(dx / w)
        dys.append(dy / h)
        logs.append(np.log(s))
        resid.append(e_fit)
        peaks.append(pk)
    dur = (i1 - i0) / fps
    tx, ty, tz = float(np.sum(dxs)), float(np.sum(dys)), float(np.exp(np.sum(logs)))
    jitter = float(np.std(np.diff(dxs))) if len(dxs) > 2 else 0.0
    move = "static"
    if abs(np.log(tz)) > np.log(1.035) and abs(np.log(tz)) / max(dur, 0.1) > 0.004:
        move = "push-in" if tz > 1 else "pull-out"
    elif max(abs(tx), abs(ty)) > 0.035:
        if abs(tx) >= abs(ty):
            move = "pan-left" if tx < 0 else "pan-right"
        else:
            move = "tilt-up" if ty > 0 else "tilt-down"
    elif max(abs(tx), abs(ty)) > 0.012 or abs(np.log(tz)) > np.log(1.012):
        move = "drift"
    out = {"movimiento": move, "zoom_total": round(tz, 3), "desplazamiento_x": round(tx, 3),
           "desplazamiento_y": round(ty, 3), "temblor": round(jitter, 4), "nivel": EST,
           "metodo": "correlación de fase + búsqueda de escala entre fotogramas a 0.4 s"}
    if jitter > 0.01 and move in ("static", "drift"):
        out["nota"] = "movimiento irregular: cámara en mano o sacudida simulada"
    if float(np.median(raws)) < 0.4:
        out["nota"] = "imagen sin cambios"
    elif unexplained > len(raws) / 2:
        out["nivel"] = HYP
        out["nota"] = "la imagen cambia pero no como un movimiento de cámara: objetos, gráficos o texto animado"
    return out


# ----------------------------------------------------------------------------- colour
def color_stats(rgb_frames):
    f = rgb_frames.astype(np.float32)
    y = luma(rgb_frames)
    mx, mn = f.max(axis=-1), f.min(axis=-1)
    lit = mx > 40  # saturation of near-black pixels is noise
    sat = ((mx - mn) / (mx + 1e-6))[lit] if lit.any() else np.zeros(1)
    warmth = float((f[..., 0] - f[..., 2]).mean())
    return {"luma_media": round(float(y.mean()), 1), "contraste_std": round(float(y.std()), 1),
            "saturacion_media": round(float(sat.mean()), 3), "calidez_r_menos_b": round(warmth, 1),
            "negros_pct": round(float((y < 20).mean()), 3), "blancos_pct": round(float((y > 235).mean()), 3)}


def palette(rgb_frames, n=6):
    px = rgb_frames[:, ::2, ::2].reshape(-1, 3).astype(np.int32)
    q = (px // 32) * 32 + 16
    keys = q[:, 0] * 65536 + q[:, 1] * 256 + q[:, 2]
    vals, counts = np.unique(keys, return_counts=True)
    order = np.argsort(-counts)[:n]
    tot = counts.sum()
    out = [{"hex": "#%02X%02X%02X" % (v // 65536, (v // 256) % 256, v % 256), "proporcion": round(float(counts[k] / tot), 3)}
           for k, v in zip(order, vals[order])]
    brand = {}
    for name, c in E2A_PALETTE.items():
        dist = np.sqrt(((px - np.array(c)) ** 2).sum(axis=1))
        brand[name] = round(float((dist < 45).mean()), 3)
    return out, brand


def aesthetic_labels(c):
    lab = []
    lab.append("oscuro" if c["luma_media"] < 70 else ("luminoso" if c["luma_media"] > 160 else "luminosidad media"))
    lab.append("alto contraste" if c["contraste_std"] > 60 else ("contraste suave" if c["contraste_std"] < 30 else "contraste medio"))
    lab.append("desaturado" if c["saturacion_media"] < 0.15 else ("muy saturado" if c["saturacion_media"] > 0.45 else "saturación media"))
    lab.append("cálido" if c["calidez_r_menos_b"] > 12 else ("frío" if c["calidez_r_menos_b"] < -12 else "neutro"))
    return lab


# ----------------------------------------------------------------------------- text, subtitles, overlays
def text_profile(gray):
    """Per frame and row: share of pixels with strong horizontal contrast (letters make many)."""
    gx = np.abs(np.diff(gray, axis=2))
    bright = gray[:, :, 1:] > 150
    dark = gray[:, :, 1:] < 110
    mask = (gx > 55) & (bright | dark)
    return mask.mean(axis=2), mask  # (n, h)


def detect_text(rgb, gray, fps, height_src):
    n, h, w = gray.shape
    prof, mask = text_profile(gray)
    nb = 20
    band_h = h // nb
    bands = prof[:, : band_h * nb].reshape(n, nb, band_h).mean(axis=2)  # (n, nb)
    base = float(np.median(bands))
    on = bands > max(0.06, 3 * base)
    presence = on.mean(axis=0)
    text_share = float(on.any(axis=1).mean())
    items = {"texto_en_pantalla_pct": round(text_share, 3), "nivel": EST,
             "metodo": "densidad de bordes horizontales fuertes por franja de 5% de altura"}
    occupied = [k for k in range(nb) if presence[k] > 0.15]
    items["franjas_ocupadas"] = [{"y_pct": round((k + 0.5) / nb * 100), "presencia": round(float(presence[k]), 2)} for k in occupied]
    # subtitle band: the band (top 10%..bottom 5%) whose content changes most often while present
    best, best_rate = None, 0.0
    change_times = []
    for k in occupied:
        if not (2 <= k <= nb - 2):
            continue
        rows = slice(k * band_h, (k + 1) * band_h)
        m = mask[:, rows, :].astype(np.float32)
        ch = np.abs(np.diff(m, axis=0)).mean(axis=(1, 2))
        present = on[1:, k] | on[:-1, k]
        ev = (ch > 0.04) & present
        rate = float(ev.sum()) / max(n / fps, 0.1)
        if rate > best_rate:
            best, best_rate = k, rate
            change_times = [round((i + 1) / fps, 2) for i in np.where(ev)[0]]
    if best is not None and best_rate > 0.3:
        # contiguous text rows around the band give the text height
        k0 = best
        while k0 - 1 >= 0 and presence[k0 - 1] > 0.15:
            k0 -= 1
        k1 = best
        while k1 + 1 < nb and presence[k1 + 1] > 0.15:
            k1 += 1
        rows = slice(k0 * band_h, (k1 + 1) * band_h)
        sel = on[:, best]
        lit = rgb[sel][:, rows] if sel.any() else rgb[:, rows]
        y = luma(lit)
        brightpx = lit[y > 170].astype(np.float32)
        col = None
        if len(brightpx) > 50:
            r, g, b = brightpx.mean(axis=0)
            col = "blanco" if min(r, g, b) > 200 and max(r, g, b) - min(r, g, b) < 30 else (
                "amarillo/dorado" if r > 170 and g > 130 and b < 120 else "#%02X%02X%02X" % (int(r), int(g), int(b)))
            yellow = ((brightpx[:, 0] > 180) & (brightpx[:, 1] > 140) & (brightpx[:, 2] < 110)).mean()
            white = (brightpx.min(axis=1) > 200).mean()
        else:
            yellow = white = 0.0
        gaps = np.diff(change_times) if len(change_times) > 1 else np.array([])
        # appearance: does a change spread over several samples (pop/typewriter) or one (instant)?
        runs, cur = [], 1
        for a_, b_ in zip(change_times, change_times[1:]):
            if b_ - a_ <= 1.01 / fps:
                cur += 1
            else:
                runs.append(cur)
                cur = 1
        runs.append(cur)
        anim = "progresiva (escala, tecleo o palabra a palabra)" if np.median(runs) >= 2 else "instantánea (aparece de golpe)"
        items["subtitulos"] = {
            "probable": True, "nivel": EST,
            "posicion_y_pct": round((best + 0.5) / nb * 100),
            "alto_bloque_px_aprox": int(round((k1 - k0 + 1) * band_h * height_src / h)),
            "cambios_por_s": round(best_rate, 2),
            "intervalo_mediano_s": round(float(np.median(gaps)), 2) if len(gaps) else None,
            "color_dominante": col,
            "palabras_resaltadas_en_color": bool(white > 0.2 and yellow > 0.08),
            "aparicion": anim,
            "aparicion_nivel": HYP,
            "cambios_t": change_times[:120],
            "tipografia": "no identificable automáticamente: revisar en los fotogramas (hipótesis visual)",
        }
    else:
        items["subtitulos"] = {"probable": False, "nivel": EST, "motivo": "ninguna franja de texto cambia de forma regular"}
    return items, on


def detect_overlays(gray, rgb):
    n, h, w = gray.shape
    if n < 6:
        return {"items": [], "nivel": EST}
    std = gray.std(axis=0)
    med = np.median(gray, axis=0)
    edges = np.abs(np.diff(med, axis=1))[:, :] > 40
    edges = np.pad(edges, ((0, 0), (0, 1)))
    moving = float(np.median(np.abs(np.diff(gray, axis=0)).mean(axis=(1, 2)))) > 1.0
    static = (std < 6) & edges
    items = []
    regions = {"esquina_sup_izq": (slice(0, h // 5), slice(0, w // 3)), "esquina_sup_der": (slice(0, h // 5), slice(2 * w // 3, w)),
               "esquina_inf_izq": (slice(4 * h // 5, h), slice(0, w // 3)), "esquina_inf_der": (slice(4 * h // 5, h), slice(2 * w // 3, w)),
               "franja_superior": (slice(0, h // 8), slice(0, w)), "franja_inferior": (slice(7 * h // 8, h), slice(0, w))}
    for name, (ys, xs) in regions.items():
        share = float(static[ys, xs].mean())
        if share > 0.02 and moving:
            items.append({"tipo": "grafico_fijo", "zona": name, "proporcion_bordes_fijos": round(share, 3), "nivel": EST,
                          "lectura": "logo, marca de agua, marcador o cartela fija (confirmar en fotogramas)", "lectura_nivel": HYP})
    # letterbox / pillarbox: rows or columns almost always black
    rows_black = (gray.mean(axis=(0, 2)) < 18) & (gray.std(axis=(0, 2)) < 6)
    cols_black = (gray.mean(axis=(0, 1)) < 18) & (gray.std(axis=(0, 1)) < 6)
    if rows_black[: h // 6].all() or rows_black[-h // 6:].all():
        items.append({"tipo": "bandas_negras_horizontales", "nivel": OBS})
    if cols_black[: w // 8].all() or cols_black[-w // 8:].all():
        items.append({"tipo": "bandas_negras_verticales", "nivel": OBS})
    # horizontal clip on a vertical canvas over a blurred copy: sharp middle, soft top and bottom
    sharp_rows = np.abs(np.diff(gray, axis=2)).mean(axis=(0, 2))
    if h > w:
        top, mid, bot = sharp_rows[: h // 4].mean(), sharp_rows[3 * h // 8: 5 * h // 8].mean(), sharp_rows[-h // 4:].mean()
        if mid > 2.2 * max(top, bot) and max(top, bot) > 0.3:
            items.append({"tipo": "video_horizontal_sobre_fondo_desenfocado", "nivel": EST,
                          "nitidez_centro_vs_bordes": round(float(mid / max(top, bot)), 2)})
    # split screen: a straight line that stays in the middle
    colprof = np.abs(np.diff(gray.mean(axis=1), axis=1)).mean(axis=0)
    rowprof = np.abs(np.diff(gray.mean(axis=2), axis=1)).mean(axis=0)
    cx, cy = w // 2, h // 2
    if colprof[cx - 3:cx + 3].max() > 6 * np.median(colprof) and colprof[cx - 3:cx + 3].max() > 4:
        items.append({"tipo": "pantalla_dividida_vertical", "nivel": EST})
    if rowprof[cy - 4:cy + 4].max() > 6 * np.median(rowprof) and rowprof[cy - 4:cy + 4].max() > 4:
        items.append({"tipo": "pantalla_dividida_horizontal", "nivel": EST})
    return {"items": items, "nivel": EST,
            "nota": "máscaras y composiciones complejas no se detectan automáticamente: revisar la hoja de fotogramas"}


# ----------------------------------------------------------------------------- helpers
def zscore(x):
    x = np.asarray(x, dtype=np.float64)
    s = x.std()
    return (x - x.mean()) / s if s > 1e-9 else np.zeros_like(x)


def per_second(times, duration, width=1.0):
    nb = max(1, int(np.ceil(duration / width)))
    c = np.zeros(nb)
    for t in times:
        c[min(nb - 1, int(t / width))] += 1
    return c


def near(times, targets, tol):
    targets = np.asarray(sorted(targets))
    if not len(times) or not len(targets):
        return 0
    hit = 0
    for t in times:
        k = np.searchsorted(targets, t)
        best = min(abs(t - targets[j]) for j in (k - 1, k) if 0 <= j < len(targets))
        hit += best <= tol
    return hit


# ----------------------------------------------------------------------------- main analysis
def code_sha256():
    """Hash of the measuring code: a cached analysis made by older code is recomputed."""
    h = hashlib.sha256()
    here = os.path.dirname(os.path.abspath(__file__))
    for name in ("analyze_video.py", "analyze_audio.py", "extract_frames.py", "common.py"):
        with open(os.path.join(here, name), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:16]


def analyse(path, out_dir, ref_id=None, title=None, source_key=None, rights="tercero", force=False):
    info = probe(path)
    digest = sha256(path)
    cached = load_json(os.path.join(out_dir, "analysis.json"))
    if (not force and cached and cached.get("source", {}).get("sha256") == digest
            and cached.get("meta", {}).get("code_sha256") == code_sha256() and cached.get("meta", {}).get("params") == PARAMS):
        return cached, True

    dur = info["duration_s"]
    lf = PARAMS["low_fps"]
    gray = xf.low_frames(path, info["width"], info["height"], fps=lf)
    mf = PARAMS["mid_fps"] if dur <= 240 else 2
    rgb = mid_frames(path, info, mf)
    gm = luma(rgb).astype(np.float32)

    # cuts / transitions
    events, score = detect_events(gray, lf)
    events = [e for e in events if PARAMS["min_shot_s"] <= e["t"] <= dur - PARAMS["min_shot_s"]]
    merged = []
    for e in events:
        if merged and e["t"] - merged[-1]["t"] < PARAMS["min_shot_s"]:
            continue
        merged.append(e)
    trans = []
    for e in merged:
        tipo, lvl, why = classify_transition(gray, e, lf)
        trans.append({"t": e["t"], "duracion_s": e["dur"], "tipo": tipo, "nivel": lvl, "evidencia": why})
    cuts = [e["t"] for e in merged]
    bounds = [0.0] + cuts + [dur]
    shots = []
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        i0, i1 = int(round(a * lf)), max(int(round(b * lf)), int(round(a * lf)) + 1)
        seg = gray[i0:min(i1, len(gray))]
        diffs = np.abs(np.diff(seg, axis=0)).mean(axis=(1, 2)) if len(seg) > 1 else np.zeros(1)
        motion = float(np.median(diffs))
        changes = float((diffs > 0.8).sum()) / max(b - a, 0.1) if len(diffs) > 2 else 0.0
        m0, m1 = int(round(a * mf)) + (1 if k else 0), max(int(round(b * mf)) - 1, int(round(a * mf)) + 1)
        cam = camera_for_shot(gm, mf, m0, min(m1, len(gm)))
        c = color_stats(rgb[m0:max(m0 + 1, min(m1, len(rgb)))])
        shots.append({"n": k + 1, "inicio": round(a, 2), "fin": round(b, 2), "duracion_s": round(b - a, 2),
                      "movimiento_imagen": round(motion, 2),
                      "imagen": "estatica" if motion < PARAMS["static_diff"] else ("en_movimiento" if motion < 8 else "rapida"),
                      "cambios_graficos_por_s": round(changes, 2), "camara": cam, "color": c,
                      "nivel": OBS})
    lens = np.array([s["duracion_s"] for s in shots])

    # perspective changes: consecutive shots with very different framing (colour + layout)
    persp = 0
    for s0, s1 in zip(shots, shots[1:]):
        if abs(s0["color"]["luma_media"] - s1["color"]["luma_media"]) > 25 or s0["camara"]["movimiento"] != s1["camara"]["movimiento"]:
            persp += 1

    # colour
    gcol = color_stats(rgb)
    pal, brand = palette(rgb)
    lum_curve = gm.mean(axis=(1, 2))
    flashes = [round((i + 1) / mf, 2) for i in range(1, len(lum_curve) - 1)
               if lum_curve[i] > lum_curve[i - 1] + 35 and lum_curve[i] > lum_curve[i + 1] + 20]

    # text, subtitles, overlays
    text, text_on = detect_text(rgb, gm, mf, info["height"])
    overlays = detect_overlays(gm, rgb)
    sub_y = text["subtitulos"].get("posicion_y_pct") if text["subtitulos"].get("probable") else None
    for b in text["franjas_ocupadas"]:
        if b["presencia"] >= 0.85 and (sub_y is None or abs(b["y_pct"] - sub_y) > 7):
            overlays["items"].append({"tipo": "rotulo_fijo", "zona": f"franja al {b['y_pct']}% de la altura",
                                      "presencia": b["presencia"], "nivel": EST,
                                      "lectura": "cabecera, marca o rótulo presente casi todo el vídeo", "lectura_nivel": HYP})

    # audio
    audio = None
    if info["has_audio"]:
        try:
            audio = analyze_audio.analyse(path, dur)
        except AnalysisError as e:
            audio = {"error": str(e), "nivel": OBS}
    curve = audio.pop("_curve", None) if audio and "error" not in audio else None

    # rhythm: pace per 5 s window
    win = 5.0
    pace = per_second(cuts, dur, win)
    pace_list = [{"desde": round(i * win, 1), "cortes": int(c)} for i, c in enumerate(pace)]
    first_half = sum(1 for t in cuts if t < dur / 2) / max(dur / 2, 1) * 10
    second_half = sum(1 for t in cuts if t >= dur / 2) / max(dur / 2, 1) * 10
    rhythm = {"cortes_por_10s": round(len(cuts) / max(dur, 1) * 10, 2), "por_ventana_5s": pace_list,
              "cortes_10s_primera_mitad": round(first_half, 2), "cortes_10s_segunda_mitad": round(second_half, 2),
              "variacion_planos_cv": round(float(lens.std() / lens.mean()), 2) if len(lens) > 1 else 0.0,
              "cambios_de_ritmo": [], "nivel": OBS}
    for i in range(1, len(pace)):
        if abs(pace[i] - pace[i - 1]) >= 3:
            rhythm["cambios_de_ritmo"].append({"t": round(i * win, 1), "de": int(pace[i - 1]), "a": int(pace[i])})

    # structure (estimated): energy per second = cuts + motion + audio level
    nb = max(1, int(np.ceil(dur)))
    cut_s = per_second(cuts, dur)
    mot_s = np.array([float(score[int(i * lf):int((i + 1) * lf)].mean()) if int(i * lf) < len(score) else 0 for i in range(nb)])
    aud_s = np.zeros(nb)
    if curve:
        ct, cd = np.array(curve["t"]), np.array(curve["db"])
        for i in range(nb):
            sel = (ct >= i) & (ct < i + 1)
            aud_s[i] = cd[sel].mean() if sel.any() else (cd.min() if len(cd) else 0)
    energy = zscore(cut_s) + zscore(mot_s) + zscore(aud_s)
    sm = np.convolve(energy, np.ones(3) / 3, mode="same")
    hook_end = round(min(3.0, max(1.0, dur * 0.15)), 2)
    lo, hi = int(dur * 0.2), max(int(dur * 0.2) + 1, int(dur * 0.9))
    peak = lo + int(np.argmax(sm[lo:hi])) if hi > lo and hi <= len(sm) else int(np.argmax(sm))
    climax = [round(max(hook_end, peak - 1.0), 2), round(min(dur, peak + 2.0), 2)]
    last_long = shots[-1]["inicio"] if shots and shots[-1]["duracion_s"] >= 1.5 else round(dur * 0.85, 2)
    res_start = round(max(climax[1], min(last_long, dur - 1.0)), 2)
    ending_silence = None
    if audio and "silences" in audio:
        for a_, b_ in audio["silences"]["items"]:
            if b_ >= dur - 0.15 and b_ - a_ >= 0.4:
                ending_silence = round(b_ - a_, 2)
    structure = {
        "gancho": {"inicio": 0.0, "fin": hook_end, "cortes": int(sum(1 for t in cuts if t < hook_end)),
                   "texto_antes_de_1s": bool(text_on[: max(1, int(mf))].any()), "nivel": EST},
        "desarrollo": {"inicio": hook_end, "fin": climax[0], "nivel": EST},
        "climax": {"inicio": climax[0], "fin": climax[1], "nivel": EST,
                   "motivo": "ventana de 3 s con más cortes, movimiento y nivel de audio (entre 20% y 90% del vídeo)"},
        "desenlace": {"inicio": res_start, "fin": dur, "silencio_final_s": ending_silence, "nivel": EST},
        "metodo": "energía por segundo = cortes + diferencia de imagen + nivel de audio (z-scores)",
    }
    if climax[0] <= hook_end:
        structure["desarrollo"]["nota"] = "sin desarrollo claro: el pico llega justo después del gancho"

    # sync
    sync = {"nivel": EST}
    if audio and "hits" in audio:
        hits = audio["hits"]["times"]
        tol = max(0.1, 1.0 / lf)
        on_hit = near(cuts, hits, tol)
        chance = min(1.0, len(hits) / max(dur, 1) * 2 * tol)
        sync["cortes_en_golpe_de_audio"] = {"n": int(on_hit), "de": len(cuts),
                                            "proporcion": round(on_hit / len(cuts), 2) if cuts else None,
                                            "esperado_por_azar": round(chance, 2), "tolerancia_s": tol}
        if audio.get("tempo") and audio["tempo"]["confianza"] > 0.3 and cuts:
            period = 60 / audio["tempo"]["bpm"]
            ph = [((t / period) % 1) for t in cuts]
            dev = [min(p, 1 - p) * period for p in ph]
            sync["cortes_en_el_pulso"] = {"desviacion_mediana_s": round(float(np.median(dev)), 3),
                                          "en_pulso_pct": round(float(np.mean(np.array(dev) < 0.08)), 2)}
        voz = audio.get("voz", {})
        if voz.get("presente") and text.get("subtitulos", {}).get("probable"):
            starts = [a_ for a_, _ in voz["tramos"]]
            ch = text["subtitulos"]["cambios_t"]
            sync["texto_y_voz"] = {"inicios_de_frase_con_cambio_de_texto": int(near(starts, ch, 0.4)), "frases": len(starts)}
        sil = [a_ for a_, b_ in audio["silences"]["items"]]
        sync["cortes_tras_silencio"] = int(near(cuts, [b_ for _, b_ in audio["silences"]["items"]], 0.25))
        _ = sil
    sync["lectura"] = ("si la proporción de cortes en golpe supera claramente lo esperado por azar, el montaje está "
                       "cortado al audio (música o efectos)")

    # retention
    visual_events = sorted(set(cuts + flashes + (text.get("subtitulos", {}).get("cambios_t") or [])))
    gaps = np.diff([0.0] + visual_events + [dur])
    first_sound = None
    if audio and "silences" in audio:
        first = [b_ for a_, b_ in audio["silences"]["items"] if a_ <= 0.05]
        first_sound = round(first[0], 2) if first else 0.0
    med = float(np.median(lens)) if len(lens) else dur
    interrupts = [s["inicio"] for s in shots[1:] if s["duracion_s"] < 0.5 * med] + flashes
    first_last = float(np.abs(gm[0] - gm[-1]).mean()) if len(gm) > 1 else 99
    retention = {
        "primer_corte_s": cuts[0] if cuts else None,
        "primer_sonido_s": first_sound,
        "texto_en_el_primer_segundo": structure["gancho"]["texto_antes_de_1s"],
        "mayor_tramo_sin_cambio_visual_s": round(float(gaps.max()), 2),
        "interrupciones_de_patron": len(set(round(x, 1) for x in interrupts)),
        "cambios_de_ritmo": len(rhythm["cambios_de_ritmo"]),
        "bucle_inicio_final": first_last < 12,
        "diferencia_primer_ultimo_fotograma": round(first_last, 1),
        "nivel": OBS,
        "lecturas": [],
    }
    L = retention["lecturas"]
    if cuts and cuts[0] <= 1.5:
        L.append({"texto": "cambio visual en el primer 1.5 s: gancho visual rápido", "nivel": HYP})
    if retention["texto_en_el_primer_segundo"]:
        L.append({"texto": "texto en pantalla desde el primer segundo: el gancho se lee sin audio", "nivel": HYP})
    if retention["mayor_tramo_sin_cambio_visual_s"] > 4:
        L.append({"texto": f"tramo de {retention['mayor_tramo_sin_cambio_visual_s']} s sin cambio visual: riesgo de abandono o pausa deliberada", "nivel": HYP})
    if second_half > first_half * 1.3:
        L.append({"texto": "el montaje se acelera en la segunda mitad (escalada hacia el clímax)", "nivel": EST})
    if retention["bucle_inicio_final"]:
        L.append({"texto": "el último fotograma se parece al primero: posible bucle para repetir la vista", "nivel": HYP})
    if ending_silence:
        L.append({"texto": f"silencio de {ending_silence} s al final", "nivel": OBS})

    # frames and contact sheet (shot middles, the hook and the climax)
    frames_dir = os.path.join(out_dir, "frames")
    mids = [round((s["inicio"] + s["fin"]) / 2, 2) for s in shots]
    if len(mids) > 22:
        idx = np.linspace(0, len(mids) - 1, 22).round().astype(int)
        mids = [mids[i] for i in sorted(set(idx))]
    times = sorted(set([0.1] + mids + [round(sum(climax) / 2, 2), round(max(0.1, dur - 0.2), 2)]))
    files = xf.extract(path, frames_dir, times)
    sheet = xf.contact_sheet(files, os.path.join(frames_dir, "sheet.jpg"))
    frames = {"items": [{"t": f["t"], "file": os.path.relpath(f["file"], out_dir)} for f in files],
              "sheet": os.path.relpath(sheet, out_dir) if sheet else None,
              "nota": "material de trabajo: no se sube al repositorio si el vídeo es de terceros"}

    analysis = {
        "schema_version": ANALYSIS_SCHEMA,
        "ref_id": ref_id,
        "source": {"title": title or os.path.basename(path), "key": source_key or os.path.basename(path),
                   "sha256": digest, "rights": rights, "size_bytes": info["size_bytes"]},
        "technical": {**{k: info[k] for k in ("duration_s", "fps", "width", "height", "aspect_ratio", "orientation",
                                               "video_codec", "pix_fmt", "has_audio", "audio_codec", "audio_sample_rate")},
                      "nivel": OBS},
        "editing": {"cuts": cuts, "n_planos": len(shots),
                    "plano_mediano_s": round(float(np.median(lens)), 2) if len(lens) else None,
                    "plano_medio_s": round(float(lens.mean()), 2) if len(lens) else None,
                    "plano_min_s": round(float(lens.min()), 2) if len(lens) else None,
                    "plano_max_s": round(float(lens.max()), 2) if len(lens) else None,
                    "planos_estaticos_pct": round(float(np.mean([s["imagen"] == "estatica" for s in shots])), 2),
                    "cambios_de_perspectiva": persp, "nivel": OBS},
        "shots": shots,
        "transitions": {"items": trans, "resumen": _count([t["tipo"] for t in trans]), "nivel": EST},
        "camera": {"resumen": _count([s["camara"]["movimiento"] for s in shots]), "nivel": EST,
                   "nota": "zoom/paneo reales o simulados no se distinguen: en ambos casos el encuadre cambia igual"},
        "rhythm": rhythm,
        "structure": structure,
        "text": text,
        "overlays": overlays,
        "color": {"global": gcol, "estetica": aesthetic_labels(gcol), "estetica_nivel": EST, "paleta": pal,
                  "afinidad_paleta_e2a": brand, "flashes": flashes, "nivel": OBS},
        "audio": audio,
        "sync": sync,
        "retention": retention,
        "frames": frames,
    }
    content = json.dumps(analysis, sort_keys=True, ensure_ascii=False)
    analysis["meta"] = {"skill_version": SKILL_VERSION, "code_sha256": code_sha256(), "params": PARAMS,
                        "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
                        "analyzed_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "tools": "ffmpeg/ffprobe + numpy"}
    return analysis, False


def _count(xs):
    out = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("out_dir")
    ap.add_argument("--ref-id")
    ap.add_argument("--title")
    ap.add_argument("--source-key")
    ap.add_argument("--rights", choices=["propio", "tercero"], default="tercero")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    try:
        os.makedirs(a.out_dir, exist_ok=True)
        analysis, cached = analyse(a.video, a.out_dir, a.ref_id, a.title, a.source_key, a.rights, a.force)
        if not cached:
            dump_json(analysis, os.path.join(a.out_dir, "analysis.json"))
            import report
            with open(os.path.join(a.out_dir, "report.md"), "w") as f:
                f.write(report.render(analysis))
    except AnalysisError as e:
        print(json.dumps({"ok": False, "reason": str(e)}, ensure_ascii=False))
        sys.exit(2)
    t = analysis["technical"]
    print(json.dumps({"ok": True, "cached": cached, "out": a.out_dir, "duration_s": t["duration_s"], "fps": t["fps"],
                      "resolution": f"{t['width']}x{t['height']}", "cuts": len(analysis["editing"]["cuts"]),
                      "content_sha256": analysis["meta"]["content_sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
