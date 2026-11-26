#!/usr/bin/env python3
"""E2A fast sports drum & bass / breakbeat bed (2026-11-26, ZERO CUT reel) - synthesised here from scratch with numpy
(no samples, no third-party recordings, no AI music service, no credits): original, owned by E2A, commercial use OK.
168 BPM two-step breakbeat (kick 1 + the 'and' of 3, snares on 2 and 4, 8th/16th hats), detuned reese bass + sub,
minor stabs (F minor: Fm - Db - Ab - Eb). Arrangement follows the edit (brief sec. 8):
  hook (immediate hit, filter riser into the freeze) -> stable groove -> reduced (no kick, low-pass) under the
  defensive mistake -> impact + full energy on the cut/layup -> steady groove -> short break + two hits ->
  final bar that ends on the downbeat so the reel loops.
NO ball-bounce sounds: no isolated low 'thud' hits, no bounce samples, no ambience. The kick is short (45 ms pitch
drop + beater click) and always sits inside the full kit.
  python3 tools/audio/zerocut_dnb.py --cuts cuts.json --duration 40.87 --out bed.wav [--bpm 168] [--seed 7]
cuts.json = the edit's {"cuts": {...}} (tactical/episodes/_gen-zerocut.py meta)."""
import argparse, json, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def saw(f, n, ph=0.0):
    t = (ph + np.cumsum(np.broadcast_to(f, (n,))) / SR) % 1.0
    # polyBLEP-free but softened: sum of 18 harmonics via FFT-free additive is slow; use naive saw + lowpass later
    return 2 * t - 1


def onepole_lp(x, fc):
    fc = np.broadcast_to(np.asarray(fc, float), x.shape[-1:])
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    z = 0.0
    for i in range(x.shape[-1]):
        z = (1 - a[i]) * x[i] + a[i] * z
        y[i] = z
    return y


def fft_filt(x, lo=None, hi=None, order=2):
    n = len(x)
    L = 1 << int(np.ceil(np.log2(n + 1)))
    X = np.fft.rfft(x, L)
    f = np.fft.rfftfreq(L, 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    return np.fft.irfft(X * g, L)[:n]


def kick(n=int(0.16 * SR)):
    t = np.arange(n) / SR
    f = 52 + 120 * np.exp(-t / 0.018)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07)
    click = fft_filt(rng.standard_normal(n), 2500, 9000) * np.exp(-t / 0.004) * 0.5
    return np.tanh(1.6 * (body + click)) * 0.9


def snare(n=int(0.22 * SR), vol=1.0):
    t = np.arange(n) / SR
    noise = fft_filt(rng.standard_normal(n), 1200, 9500) * np.exp(-t / 0.075)
    tone = (np.sin(2 * np.pi * 196 * t) + 0.5 * np.sin(2 * np.pi * 330 * t)) * np.exp(-t / 0.035)
    return np.tanh(1.4 * (0.75 * noise + 0.45 * tone)) * vol * 0.8


def hat(n=int(0.05 * SR), open_=False, vol=0.35):
    if open_:
        n = int(0.22 * SR)
    t = np.arange(n) / SR
    x = fft_filt(rng.standard_normal(n), 7000, 16000) * np.exp(-t / (0.09 if open_ else 0.012))
    return x * vol


def swell(n, rise=True):
    t = np.linspace(0, 1, n)
    x = fft_filt(rng.standard_normal(n), 1500, 12000)
    return x * (t ** 2 if rise else np.exp(-t * 5)) * 0.35


def chord_notes(root):
    return [root, root + 3 + (1 if root % 12 in (1, 8) else 0), root + 7]   # minor on F, major on Db/Ab, Eb


def stab(freqs, n):
    t = np.arange(n) / SR
    x = sum(saw(mtof(m) * d, n, rng.random()) for m in freqs for d in (0.997, 1.003)) / (len(freqs) * 2)
    x = onepole_lp(x, 1800 + 3000 * np.exp(-t / 0.05))
    return x * np.exp(-t / 0.16)


def put(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= buf.shape[-1] or i < 0:
        return
    m = min(len(x), buf.shape[-1] - i)
    buf[..., i:i + m] += x[:m] * g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cuts", required=True)
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bpm", type=float, default=168)
    a = ap.parse_args()
    C = json.load(open(a.cuts))["cuts"]
    dur = a.duration
    N = int(dur * SR) + SR
    step = 60 / a.bpm / 4
    bar = 16 * step
    drums, bass, music, fx = (np.zeros(N) for _ in range(4))
    # intensity per time
    REDUCE = (C["feet"], C["cut"])
    BREAK = (C["same"], C["twoA"])
    DROP = C["cut"]
    def section(t):
        if REDUCE[0] <= t < REDUCE[1]:
            return "reduce"
        if BREAK[0] <= t < BREAK[1]:
            return "break"
        if DROP <= t < C["replay"]:
            return "drop"
        return "groove"
    nb = int(np.ceil(dur / bar)) + 1
    K, S = kick(), snare()
    for b in range(nb):
        for s in range(16):
            t = b * bar + s * step
            if t >= dur:
                break
            sec = section(t)
            if t >= C["name"] - 0.6 and t < C["name"] and sec == "groove":   # freeze in the hook: hats only + riser
                if s % 2 == 0:
                    put(drums, hat(), t)
                continue
            if sec == "break":
                if s % 4 == 0:
                    put(drums, hat(vol=0.25), t)
                continue
            if sec != "reduce" and (s in (0, 10) or (b % 4 == 3 and s == 7)):
                put(drums, K, t, 1.0)
            if s in (4, 12):
                put(drums, S, t, 0.55 if sec == "reduce" else 1.0)
            if sec != "reduce" and s in (7, 15) and b % 2:
                put(drums, snare(vol=0.25), t)
            if s % 2 == 0:
                put(drums, hat(open_=(s == 14)), t, 0.8 if sec != "reduce" else 0.55)
            elif sec in ("drop",) or (sec == "groove" and b % 2):
                put(drums, hat(vol=0.18), t)
    # reese + sub, chord per bar
    prog = [41, 37, 44, 39]   # F2 Db2 Ab2 Eb2 (midi)
    for b in range(nb):
        t0 = b * bar
        if t0 >= dur:
            break
        n = int(bar * SR)
        root = prog[b % 4] - 12
        f = mtof(root)
        tt = np.arange(n) / SR
        r = (saw(f * 0.993, n, rng.random()) + saw(f * 1.007, n, rng.random()) + 0.5 * saw(f * 2.003, n, rng.random())) / 2.5
        sec = section(t0 + 0.01)
        cutoff = 380 + 520 * (0.5 + 0.5 * np.sin(2 * np.pi * tt / (bar / 2)))
        if sec == "reduce":
            cutoff = cutoff * 0.55
        r = onepole_lp(onepole_lp(r, cutoff), cutoff * 1.4)
        sub = np.sin(2 * np.pi * np.cumsum(np.full(n, f)) / SR) * 0.6
        env = np.ones(n); env[:int(0.01 * SR)] = np.linspace(0, 1, int(0.01 * SR)); env[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
        g = 0.0 if sec == "break" else 1.0
        put(bass, (np.tanh(1.8 * r) * 0.55 + sub) * env * g, t0)
        # stabs: downbeat + the 'and' of 2 (offbeat), more in the drop
        notes = chord_notes(prog[b % 4] + 24)
        if sec != "break":
            put(music, stab(notes, int(0.35 * SR)), t0, 0.5 if sec == "reduce" else 0.75)
            put(music, stab(notes, int(0.25 * SR)), t0 + 6 * step, 0.45 if sec != "drop" else 0.65)
            if sec == "drop":
                put(music, stab(notes, int(0.2 * SR)), t0 + 11 * step, 0.5)
        # pad under the reduced section
        if sec == "reduce":
            pad = sum(np.sin(2 * np.pi * mtof(m) * tt) for m in chord_notes(prog[b % 4] + 12)) / 3
            put(music, pad * np.minimum(1, tt / 0.3) * 0.25, t0)
    # impacts & risers on the edit (cuts)
    put(fx, swell(int(0.55 * SR)), C["name"] - 0.55)                 # riser into the reveal (hook freeze)
    put(fx, swell(int(0.9 * SR), False), C["name"], 0.8)
    put(fx, swell(int(0.8 * SR)), DROP - 0.8)                          # riser into NO HANDOFF
    put(fx, swell(int(1.4 * SR), False), DROP, 1.0)
    for k in ("twoA", "twoB", "iq"):
        put(music, stab(chord_notes(41 + 24), int(0.4 * SR)), C[k], 0.9)
    put(fx, swell(int(1.0 * SR), False), C["replay"], 0.5)
    put(fx, swell(int(0.9 * SR), False), C["read2"], 0.45)
    # first hit at 0 (no slow intro)
    put(music, stab(chord_notes(41 + 24), int(0.5 * SR)), 0.0, 1.0)
    put(fx, swell(int(0.8 * SR), False), 0.0, 0.8)
    # hook freeze: high-pass the drums into the reveal
    i0, i1 = int((C["name"] - 0.6) * SR), int(C["name"] * SR)
    seg = drums[i0:i1].copy(); drums[i0:i1] = fft_filt(seg, 900)
    # reduce section: low-pass the stabs
    i0, i1 = int(REDUCE[0] * SR), int(REDUCE[1] * SR)
    music[i0:i1] = fft_filt(music[i0:i1], None, 1400)
    mix = 0.9 * drums + 0.75 * bass + 0.55 * music + 0.5 * fx
    n = int(dur * SR)
    mix = mix[:n]
    # stereo: hats/stabs slightly wide via Haas on music+fx
    wide = 0.55 * music + 0.5 * fx
    d = int(0.011 * SR)
    L = mix
    R = mix - wide[:n] + np.concatenate([np.zeros(d), wide[:n - d]])
    st = np.stack([L, R])
    st = np.tanh(st * 1.1) / 1.1
    st *= 10 ** (-12 / 20) / (np.max(np.abs(st)) + 1e-9)
    fade = int(0.012 * SR)
    st[:, -fade:] *= np.linspace(1, 0, fade)
    pcm = (np.clip(st.T, -1, 1) * 32767).astype("<i2")
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(f"bed {dur:.2f} s, {a.bpm} BPM, bar {bar:.3f} s -> {a.out}")


if __name__ == "__main__":
    main()
