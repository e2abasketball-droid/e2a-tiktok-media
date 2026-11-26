#!/usr/bin/env python3
"""E2A dark techno x industrial breakbeat bed with ACTION-DRIVEN energy states (2026-11-26, ZERO CUT V2 brief sec. 3).
Synthesised here from scratch with numpy: no samples, no third-party recordings, no AI music service, no credits.
Original, owned by E2A, commercial use OK. Default 144 BPM, D Phrygian (D - Eb - Bb - C), minimal melody.

States (from the edit's real animation events + final narration timestamps, never random drops):
  A  HIGH ENERGY   4/4 distorted kick, broken industrial snares (2 + 4 + ghost), 16th metallic hats, rolling
                   offbeat reese bass + sub, dark stabs.
  B  SLOW-MO       SAME tempo, HALF-TIME feel (perceived 72 BPM): no kick at all (an isolated low thud would read as
                   a ball bounce, owner rule: no bounce sounds), one huge reverbed snare/clap on beat 3 of every
                   bar, ticking closed hat on 8ths, sustained sub drone + dark detuned pad, slow filter breathing.
  C  RELEASE       a reversed noise swell + filter riser that resolves EXACTLY on the release time (the cutter's
                   acceleration), then state A at full force with a short low-passed-to-open filter sweep.
  END              loop motif: the bar before the end is B-like with the pad; the last downbeat is the loop point.
  python3 tools/audio/darktech_states.py --plan plan.json --out bed.wav [--stems dir] [--bpm 144]
plan.json = {"duration": s, "states": [[t0, t1, "A"|"B"|"BREAK"], ...], "releases": [t, ...], "hits": [t, ...]}
  releases = state-C payoffs (the beat returns exactly there); hits = dark stab accents on titles (optional).
Stems (--stems): drums.wav, bass.wav, synth.wav, fx.wav + the mix (each 48 kHz stereo)."""
import argparse, json, os, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(11)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def saw(f, n, ph=0.0):
    t = (ph + np.cumsum(np.broadcast_to(f, (n,))) / SR) % 1.0
    return 2 * t - 1


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


def onepole_lp(x, fc):
    fc = np.broadcast_to(np.asarray(fc, float), x.shape[-1:])
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    z = 0.0
    for i in range(x.shape[-1]):
        z = (1 - a[i]) * x[i] + a[i] * z
        y[i] = z
    return y


def reverb(x, secs=1.6, mix=0.5):
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / (secs / 5))
    ir = fft_filt(ir, 300, 6000)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    L = 1 << int(np.ceil(np.log2(len(x) + n)))
    wet = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[:len(x) + n]
    out = np.zeros(len(x) + n)
    out[:len(x)] += x * (1 - mix)
    out += wet * mix * 0.6
    return out


# ---------------------------------------------------------------- instruments
def kick():
    n = int(0.32 * SR)
    t = np.arange(n) / SR
    f = 46 + 140 * np.exp(-t / 0.022)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    click = fft_filt(rng.standard_normal(n), 2000, 8000) * np.exp(-t / 0.003) * 0.6
    return np.tanh(2.6 * (body + click)) * 0.85          # distorted techno kick, always inside the full kit


def snare_ind(vol=1.0, n=int(0.3 * SR)):
    t = np.arange(n) / SR
    noise = fft_filt(rng.standard_normal(n), 900, 7000) * np.exp(-t / 0.09)
    metal = sum(np.sin(2 * np.pi * f * t) for f in (311, 467, 739)) / 3 * np.exp(-t / 0.05)
    return np.tanh(2.2 * (0.8 * noise + 0.4 * metal)) * vol * 0.7


def clap_big(vol=1.0):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for d in (0, 0.011, 0.023):
        i = int(d * SR)
        m = n - i
        x[i:] += fft_filt(rng.standard_normal(m), 1000, 6000) * np.exp(-np.arange(m) / SR / 0.02)
    return reverb(np.tanh(1.8 * x) * vol * 0.6, 2.2, 0.65)


def hat(vol=0.3, open_=False):
    n = int((0.2 if open_ else 0.04) * SR)
    t = np.arange(n) / SR
    noise = fft_filt(rng.standard_normal(n), 6500, 15000)
    ring = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (5400, 7130, 8670)) / 3 * 0.25
    return (noise + ring) * np.exp(-t / (0.08 if open_ else 0.01)) * vol


def tick(vol=0.22):
    n = int(0.02 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t / 0.004) * vol


def stab(notes, n):
    t = np.arange(n) / SR
    x = sum(saw(mtof(m) * d, n, rng.random()) for m in notes for d in (0.995, 1.005)) / (len(notes) * 2)
    x = onepole_lp(x, 900 + 2200 * np.exp(-t / 0.04))
    return np.tanh(1.5 * x) * np.exp(-t / 0.22)


def swell(n, rev=True, lo=800, hi=11000):
    t = np.linspace(0, 1, n)
    x = fft_filt(rng.standard_normal(n), lo, hi)
    return x * ((t ** 2.4) if rev else np.exp(-t * 6)) * 0.4


def put(buf, x, t, g=1.0):
    i = int(round(t * SR))
    if i < 0:
        x = x[-i:]
        i = 0
    if i >= len(buf) or len(x) == 0:
        return
    m = min(len(x), len(buf) - i)
    buf[i:i + m] += x[:m] * g


def write(path, L, R):
    st = np.stack([L, R], 1)
    st = np.clip(st, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stems")
    ap.add_argument("--bpm", type=float, default=144)
    a = ap.parse_args()
    P = json.load(open(a.plan))
    dur = P["duration"]
    N = int((dur + 3) * SR)
    step = 60 / a.bpm / 4
    bar = 16 * step
    states = P["states"]
    releases = sorted(P.get("releases", []))
    hits = P.get("hits", [])

    def state(t):
        for s0, s1, k in states:
            if s0 <= t < s1:
                return k
        return "A"
    drums, bass, synth, fx = (np.zeros(N) for _ in range(4))
    # bars are anchored on t=0 (the hook starts on a downbeat); a release time snaps the grid phase locally:
    # the beat that returns at a release is played AT the release (event-exact), and the grid continues from there
    grid = [0.0]
    for r in releases:
        grid.append(r)
    def grid_t(t):
        g0 = max(g for g in grid if g <= t + 1e-9)
        return g0, (t - g0)
    K = kick()
    prog = [38, 39, 34, 36]     # D Eb Bb C (Phrygian darkness)
    # ---- drums, 16th grid per segment between anchors
    anchors = grid + [dur + 1]
    for gi in range(len(anchors) - 1):
        g0, g1 = anchors[gi], anchors[gi + 1]
        k = 0
        while True:
            t = g0 + k * step
            if t >= min(g1, dur):
                break
            s = k % 16
            b = k // 16
            st_ = state(t + 1e-4)
            if st_ == "A":
                if s % 4 == 0:
                    put(drums, K, t, 1.0)
                if s in (4, 12):
                    put(drums, snare_ind(), t, 1.4)
                if s in (7, 14) and b % 2:
                    put(drums, snare_ind(0.3), t)
                put(drums, hat(0.28 if s % 2 else 0.36, open_=(s % 4 == 2)), t)
            elif st_ == "B":
                if s == 8:
                    put(drums, clap_big(1.0), t, 2.1)        # half-time backbeat (beat 3)
                if s % 2 == 0:
                    put(drums, tick(0.35), t)
                if s == 14 and b % 2:
                    put(drums, hat(0.18, True), t)
            else:   # BREAK: almost empty
                if s == 0:
                    put(drums, tick(0.3), t)
            k += 1
    # ---- bass + synth per bar (bar grid from 0; state sampled per 16th for the bass rhythm)
    nb = int(np.ceil(dur / bar)) + 2
    for b in range(nb):
        t0 = b * bar
        if t0 >= dur:
            break
        root = prog[(b // 2) % 4]
        f = mtof(root - 12)
        for s in range(16):
            t = t0 + s * step
            if t >= dur:
                break
            st_ = state(t + 1e-4)
            n = int(step * SR)
            if st_ == "A" and s % 4 != 0:        # rolling offbeat bass (gaps on the kick)
                tt = np.arange(n) / SR
                r = (saw(f * 0.992, n, rng.random()) + saw(f * 1.008, n, rng.random())) / 2
                r = onepole_lp(r, 260 + 700 * np.exp(-tt / 0.03))
                env = np.minimum(1, tt / 0.004) * np.exp(-tt / 0.09)
                put(bass, (np.tanh(2.2 * r) * 0.6 + 0.3 * np.sin(2 * np.pi * f * tt)) * env, t)
        # sub drone + pad in B / BREAK, per bar (smooth)
        n = int(bar * SR)
        tt = np.arange(n) / SR
        sts = [state(t0 + x * bar / 8 + 1e-4) for x in range(8)]
        wB = np.interp(tt, np.linspace(0, bar, 8), [1.0 if s_ in ("B", "BREAK") else 0.0 for s_ in sts])
        if wB.max() > 0:
            sub = np.sin(2 * np.pi * np.cumsum(np.full(n, f)) / SR) * 0.3
            breath = 0.5 + 0.5 * np.sin(2 * np.pi * tt / (bar / 2) - np.pi / 2)
            pad = sum(saw(mtof(m) * d, n, rng.random()) for m in (root + 12, root + 15, root + 19) for d in (0.996, 1.004)) / 6
            pad = onepole_lp(pad, 350 + 900 * breath)
            put(bass, sub * wB * np.minimum(1, tt / 0.05), t0)
            put(synth, pad * 1.05 * wB, t0)
        # dark stab on bar downbeats in A, every 2 bars
        if state(t0 + 1e-4) == "A" and b % 2 == 0:
            put(synth, stab([root + 24, root + 27, root + 31], int(0.3 * SR)), t0 + 6 * step, 0.45)
    # ---- state C: releases (riser resolves on the release; open filter burst after)
    for r in releases:
        L = 1.6
        put(fx, swell(int(L * SR)), r - L, 0.9)
        put(fx, swell(int(0.8 * SR), False, 200, 6000), r, 0.6)
        put(synth, stab([prog[0] + 24, prog[0] + 27, prog[0] + 31], int(0.5 * SR)), r, 0.8)
    for h in hits:
        put(synth, stab([prog[0] + 24, prog[0] + 27, prog[0] + 31], int(0.4 * SR)), h, 0.55)
    # hook: immediate hit at 0
    put(synth, stab([prog[0] + 24, prog[0] + 27, prog[0] + 31], int(0.6 * SR)), 0.0, 0.9)
    # ---- B sections: low-pass the A remnants (smooth gain) and duck the bass rhythm out
    gB = np.array([1.0 if state(i / SR) in ("B", "BREAK") else 0.0 for i in range(0, N, 480)])
    gB = np.repeat(gB, 480)[:N]
    k = int(0.06 * SR)
    gB = np.convolve(gB, np.ones(k) / k, mode="same")
    # end fade-in-place: the last 30 ms
    e = int(dur * SR)
    for x in (drums, bass, synth, fx):
        x[e:] = 0
        x[e - int(0.03 * SR):e] *= np.linspace(1, 0, int(0.03 * SR))
    # stereo: drums centre, hats/fx widened by a small delay, pad wide
    def wide(x, d=0.011):
        i = int(d * SR)
        return x, np.concatenate([np.zeros(i), x[:-i]])
    dL, dR = drums, drums
    bL, bR = bass, bass
    sL, sR = wide(synth, 0.013)
    fL, fR = wide(fx, 0.017)
    L = 0.9 * dL + 0.85 * bL + 0.6 * sL + 0.55 * fL
    R = 0.9 * dR + 0.85 * bR + 0.6 * sR + 0.55 * fR
    L, R = L[:int(dur * SR)], R[:int(dur * SR)]
    pk = max(np.abs(L).max(), np.abs(R).max()) + 1e-9
    gain = 10 ** (-12 / 20) / pk
    write(a.out, L * gain, R * gain)
    if a.stems:
        os.makedirs(a.stems, exist_ok=True)
        for name, x, w in (("drums", drums, 0.9), ("bass", bass, 0.85), ("synth", synth, 0.6), ("fx", fx, 0.55)):
            y = x[:int(dur * SR)] * w * gain
            write(os.path.join(a.stems, f"{name}.wav"), y, y)
    print("bed", a.out, f"{dur:.2f}s", "states", len(states), "releases", releases)


if __name__ == "__main__":
    main()
