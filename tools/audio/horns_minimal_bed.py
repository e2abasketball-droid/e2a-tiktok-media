#!/usr/bin/env python3
"""E2A minimal instrumental bed for HORNS: THE DEFENDER'S DILEMMA (2026-11-23).
Synthesised here from scratch with numpy (no samples, no third-party recordings, no AI service, no credits):
E2A owns it. Calm, modern, minimalist: a soft filtered pad on a slow four-chord loop, a sub pulse on the beat,
a quiet high tick on the off-beats, and at most two soft accents (low swells) where the edit needs them.
No percussion that resembles a ball bounce, no squeaks, no whooshes.
  python3 tools/audio/horns_minimal_bed.py --duration 43.0 --accents 16.57,34.67 --out bed.wav [--bpm 84]
Writes a 48 kHz stereo WAV peaking at about -14 dBFS (the mix sets the final level under the voice)."""
import argparse
import wave

import numpy as np

SR = 48000


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def adsr(n, a, r):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lowpass(x, fc):
    # one-pole, run twice (12 dB / oct)
    a = np.exp(-2 * np.pi * fc / SR)
    for _ in range(2):
        y = np.empty_like(x)
        acc = 0.0
        for i in range(len(x)):  # small signals only (per chord), fine for a 45 s bed
            acc = (1 - a) * x[i] + a * acc
            y[i] = acc
        x = y
    return x


def saw(f, n, phase=0.0):
    t = np.arange(n) / SR
    return 2 * ((f * t + phase) % 1.0) - 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--accents", default="")
    ap.add_argument("--bpm", type=float, default=84)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    N = int(a.duration * SR)
    L = np.zeros(N)
    R = np.zeros(N)
    beat = 60.0 / a.bpm
    bar = 4 * beat
    # D minor colour: Dm9 - Bbmaj7 - Fmaj7/A - Csus2 (one chord per bar), voiced around middle C
    chords = [[50, 57, 60, 64, 65], [46, 53, 57, 62, 65], [45, 53, 57, 60, 64], [48, 55, 60, 62, 67]]
    bass = [38, 34, 33, 36]
    nb = int(np.ceil(a.duration / bar)) + 1
    rng = np.random.default_rng(23)
    for b in range(nb):
        t0 = b * bar
        i0 = int(t0 * SR)
        n = int((bar + 0.6) * SR)
        if i0 >= N:
            break
        n = min(n, N - i0)
        ch = chords[b % 4]
        pad = np.zeros(n)
        for k, note in enumerate(ch):
            f = midi(note)
            pad += 0.5 * saw(f * 1.003, n, rng.random()) + 0.5 * saw(f * 0.997, n, rng.random())
        pad = lowpass(pad / len(ch), 900 + 300 * np.sin(b * 0.7) ** 2)
        pad *= adsr(n, 0.9, 0.8) * 0.32
        L[i0:i0 + n] += pad
        R[i0:i0 + n] += np.roll(pad, int(0.011 * SR))
        # sub pulse on every beat (sine, short decay): felt more than heard
        for q in range(4):
            j = int((t0 + q * beat) * SR)
            m = int(0.42 * SR)
            if j >= N:
                break
            m = min(m, N - j)
            tt = np.arange(m) / SR
            s = np.sin(2 * np.pi * midi(bass[b % 4]) * tt) * np.exp(-tt * 7.5) * 0.30
            L[j:j + m] += s
            R[j:j + m] += s
        # quiet high tick on the off-beats (band-passed noise, 25 ms): time keeping only
        for q in range(4):
            j = int((t0 + (q + 0.5) * beat) * SR)
            m = int(0.025 * SR)
            if j + m >= N:
                break
            nz = rng.standard_normal(m)
            nz = nz - lowpass(nz, 5000)
            e = np.exp(-np.arange(m) / SR * 160) * 0.035
            L[j:j + m] += nz * e * 0.8
            R[j:j + m] += nz * e
    # soft accents: a low swell (filtered noise + sub) that peaks ON the cut
    for s in [float(x) for x in a.accents.split(",") if x]:
        j0 = int((s - 0.9) * SR)
        m = int(1.6 * SR)
        if j0 < 0 or j0 + m >= N:
            continue
        tt = np.arange(m) / SR
        env = np.where(tt < 0.9, (tt / 0.9) ** 2, np.exp(-(tt - 0.9) * 4.0))
        sw = lowpass(rng.standard_normal(m), 400) * 0.9 + np.sin(2 * np.pi * 55 * tt) * 0.5
        L[j0:j0 + m] += sw * env * 0.22
        R[j0:j0 + m] += sw * env * 0.22
    # fades: 0.4 s in, 2.5 s out
    fi, fo = int(0.4 * SR), int(2.5 * SR)
    for ch in (L, R):
        ch[:fi] *= np.linspace(0, 1, fi)
        ch[-fo:] *= np.linspace(1, 0, fo)
    st = np.stack([L, R], 1)
    st *= 10 ** (-14 / 20) / max(1e-9, np.abs(st).max())
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())
    print("bed", a.out, round(a.duration, 2), "s")


if __name__ == "__main__":
    main()
