#!/usr/bin/env python3
"""Audio analysis for ANALYZE: loudness, silences, hits, tempo, voice / music / effects and mix.

  python3 analyze_audio.py <video_or_audio> [--json out.json]

Measured with ffmpeg (EBU R128 loudness, silencedetect) and numpy (short-time spectrum).
What each field is:
  observacion  loudness, true peak, LRA, silences, transient hits (direct measurements)
  estimacion   tempo, voice presence, music bed presence, voice-over-music margin (inferred from spectra)
No transcription is done here (that would need ElevenLabs Scribe credits).
"""
import argparse
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EST, HYP, OBS, AnalysisError, run  # noqa: E402

SR = 16000
HOP = 800          # 50 ms
WIN = 1024


def loudness(path):
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    s = out[out.rfind("Summary:"):] if "Summary:" in out else ""
    def grab(rx):
        m = re.search(rx, s)
        return float(m.group(1)) if m else None
    return {"integrated_lufs": grab(r"I:\s+(-?[0-9.]+) LUFS"), "lra_lu": grab(r"LRA:\s+([0-9.]+) LU"),
            "true_peak_dbfs": grab(r"Peak:\s+(-?[0-9.]+) dBFS"), "nivel": OBS}


def silences(path, noise_db=-35, min_d=0.25):
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af",
               f"silencedetect=n={noise_db}dB:d={min_d}", "-f", "null", "-"])
    st = [float(x) for x in re.findall(r"silence_start: (-?[0-9.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    if len(en) < len(st):  # silence running to the end
        dur = re.findall(r"Duration: (\d+):(\d+):([0-9.]+)", out)
        if dur:
            h, m, sec = dur[0]
            en.append(int(h) * 3600 + int(m) * 60 + float(sec))
    return [[round(max(0, a), 2), round(b, 2)] for a, b in zip(st, en)]


def pcm(path):
    raw = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR),
               "-f", "s16le", "-"], binary=True)
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if len(x) < SR // 4:
        raise AnalysisError("pista de audio vacía o demasiado corta")
    return x


def spectra(x):
    n = 1 + max(0, (len(x) - WIN) // HOP)
    idx = np.arange(WIN)[None, :] + HOP * np.arange(n)[:, None]
    frames = x[np.minimum(idx, len(x) - 1)] * np.hanning(WIN)[None, :]
    mag = np.abs(np.fft.rfft(frames, axis=1)) + 1e-9
    freqs = np.fft.rfftfreq(WIN, 1 / SR)
    return mag, freqs


def analyse(path, duration=None):
    res = {"loudness": loudness(path), "silences": {"items": silences(path), "umbral_db": -35, "nivel": OBS}}
    x = pcm(path)
    duration = duration or len(x) / SR
    mag, f = spectra(x)
    t = (np.arange(len(mag)) * HOP + WIN / 2) / SR
    power = (mag ** 2)
    total = power.sum(axis=1)
    db = 10 * np.log10(total / WIN + 1e-12)
    speech_band = power[:, (f >= 300) & (f <= 3400)].sum(axis=1)
    low = power[:, f < 250].sum(axis=1)
    high = power[:, f > 4000].sum(axis=1)
    flat = np.exp(np.mean(np.log(mag), axis=1)) / np.mean(mag, axis=1)  # spectral flatness 0..1

    # transient hits: positive spectral flux peaks (cuts, impacts, beats, syllable onsets)
    flux = np.maximum(np.diff(np.log(mag), axis=0), 0).mean(axis=1)
    flux = np.concatenate([[0], flux])
    thr = flux.mean() + 2.0 * flux.std()
    peaks = [i for i in range(1, len(flux) - 1) if flux[i] > thr and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]]
    hit_times = [round(float(t[i]), 2) for i in peaks]
    strength = [float(flux[i] / (thr + 1e-9)) for i in peaks]
    res["hits"] = {"times": hit_times[:200], "per_10s": round(len(peaks) / max(duration, 1) * 10, 2),
                   "strong": [ht for ht, s in zip(hit_times, strength) if s > 2.0][:60], "nivel": OBS}

    # tempo: autocorrelation of the onset envelope between 70 and 180 BPM
    env = flux - flux.mean()
    tempo = None
    if len(env) > 60:
        ac = np.correlate(env, env, mode="full")[len(env) - 1:]
        lo, hi = int(np.ceil(60 / 180 * SR / HOP)), int(60 / 70 * SR / HOP)
        if hi < len(ac) and ac[0] > 0:
            lag = lo + int(np.argmax(ac[lo:hi]))
            conf = float(ac[lag] / ac[0])
            tempo = {"bpm": round(60 * SR / HOP / lag, 1), "confianza": round(conf, 2), "fiable": conf >= 0.3, "nivel": EST}
    res["tempo"] = tempo

    # voice presence: energy in the speech band that is modulated at syllable rate (3-8 Hz)
    win = int(1.0 * SR / HOP)
    voice = np.zeros(len(mag), dtype=bool)
    sb_db = 10 * np.log10(speech_band + 1e-12)
    band = (f >= 300) & (f <= 3400)
    sb_peak = power[:, band].max(axis=1) * 3  # peak bin + its two window neighbours
    for i in range(0, len(mag), win // 2):
        seg = sb_db[i:i + win]
        if len(seg) < win // 2:
            continue
        spec = np.abs(np.fft.rfft(seg - seg.mean()))
        mf = np.fft.rfftfreq(len(seg), HOP / SR)
        syl = spec[(mf >= 3) & (mf <= 8)].sum() / (spec[mf > 0.5].sum() + 1e-9)
        ratio = speech_band[i:i + win].sum() / (total[i:i + win].sum() + 1e-12)
        # a voice spreads its energy over many harmonics; a tone or a beep puts it in one peak
        loud = db[i:i + win] > db.max() - 35
        pk = sb_peak[i:i + win] / (speech_band[i:i + win] + 1e-12)
        peaky = float(np.median(pk[loud])) if loud.any() else 9.0
        if syl > 0.35 and ratio > 0.45 and peaky < 1.2 and np.median(db[i:i + win]) > db.max() - 35:
            voice[i:i + win] = True
    voice_share = float(voice.mean())
    loud_floor = db.max() - 40
    non_voice = (~voice) & (db > loud_floor)
    music = non_voice & (flat < 0.25)
    res["voz"] = {"presente": voice_share > 0.15, "proporcion": round(voice_share, 2),
                  "tramos": _spans(t, voice)[:40], "nivel": EST,
                  "metodo": "energía 300-3400 Hz modulada a 3-8 Hz (ritmo silábico)"}
    res["musica"] = {"presente": float(music.mean()) > 0.1 or (voice_share > 0.15 and float(np.median(flat[voice])) < 0.2),
                     "proporcion_sin_voz": round(float(music.mean()), 2), "nivel": EST,
                     "metodo": "energía tonal (baja planitud espectral) fuera de la voz"}
    margin = None
    if voice.any() and non_voice.any():
        # voice-over-bed margin: level while talking vs level of the bed between phrases
        margin = round(float(np.median(db[voice]) - np.median(db[non_voice])), 1)
    res["mezcla"] = {"voz_sobre_fondo_db": margin, "nivel": EST,
                     "nota": "aproximación: el fondo se mide en las pausas, no debajo de la voz"}
    res["bandas"] = {"graves_pct": round(float(low.sum() / total.sum()), 3),
                     "voz_pct": round(float(speech_band.sum() / total.sum()), 3),
                     "agudos_pct": round(float(high.sum() / total.sum()), 3), "nivel": OBS}
    # effects: strong hits outside voice spans that are not on the tempo grid
    sfx = [h for h in res["hits"]["strong"] if not voice[min(len(voice) - 1, int(h * SR / HOP))]]
    res["efectos_candidatos"] = {"times": sfx[:40], "nivel": HYP if sfx else EST,
                                 "nota": "golpes fuertes fuera de la voz: impactos, whooshes o golpes de música"}
    res["envolvente_db_p10_p50_p90"] = [round(float(np.percentile(db, p)), 1) for p in (10, 50, 90)]
    res["_curve"] = {"t": t[::4].round(2).tolist(), "db": db[::4].round(1).tolist()}  # for structure/sync
    return res


def _spans(t, mask):
    spans, start = [], None
    for i, m in enumerate(mask):
        if m and start is None:
            start = t[i]
        if not m and start is not None:
            spans.append([round(float(start), 2), round(float(t[i]), 2)])
            start = None
    if start is not None:
        spans.append([round(float(start), 2), round(float(t[-1]), 2)])
    return spans



def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media")
    ap.add_argument("--json")
    a = ap.parse_args()
    try:
        r = analyse(a.media)
    except AnalysisError as e:
        print(json.dumps({"ok": False, "reason": str(e)}, ensure_ascii=False))
        sys.exit(2)
    r.pop("_curve", None)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(r, f, indent=1, ensure_ascii=False)
    print(json.dumps({"ok": True, **{k: r[k] for k in ("loudness", "tempo")}, "voz": r["voz"]["presente"],
                      "musica": r["musica"]["presente"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
