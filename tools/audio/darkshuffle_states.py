#!/usr/bin/env python3
"""E2A dark UK-garage shuffle x psychedelic half-time bed with ACTION-DRIVEN states (2026-11-26, ZERO CUT TEST
"aggressive hook" brief sec. 7). Synthesised from scratch with numpy (instruments from darktech_states.py + new ones):
no samples, no third-party recordings, no AI music service, no credits. Original, owned by E2A, commercial use OK.
ONE identity for the whole track: same tempo (default 136 BPM), same key (D Phrygian: D - Eb - Bb - C), same reese
bass voice and the same chord colour in both states, so the slow-motion world is the SAME song turned inside out.

  A  SHUFFLE      2-step garage drums with a swung 16th grid (shuffle ~58 %): kick on 1 and the "and" of 3 (never
                  alone: always inside the full kit, owner rule: nothing that reads as a ball bounce), tight clap +
                  snare on 2 and 4, swung closed hats + shaker, metallic rim clicks on the off-16ths, a syncopated dark
                  reese bassline with a 1/8 filter wobble (ducked under the kick), filtered minor stabs on swung steps.
  B  PSYCHEDELIC  SAME tempo, HALF-TIME feel. No kick. One huge reverbed clap on beat 3, soft ticks on 8ths, a sub
                  drone on the bar root, a swirling chorus pad (slow pitch-drifting voices, auto-pan round the head),
                  a hypnotic 16th arpeggio of the SAME chord through a ping-pong tape delay, slow filter breathing.
  C  RELEASE      a short filtered swell resolves EXACTLY on the release time (the cutter's acceleration) and state A
                  returns there at full force (the grid restarts on the release: event-exact).
  python3 tools/audio/darkshuffle_states.py --plan plan.json --out bed.wav [--stems dir] [--bpm 136] [--swing 0.58]
plan.json = {"duration": s, "states": [[t0, t1, "A"|"B"|"BREAK"], ...], "releases": [t, ...], "hits": [t, ...]}"""
import argparse, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import darktech_states as dt  # noqa: E402

SR = dt.SR
rng = np.random.default_rng(23)
mtof, saw, fft_filt, onepole_lp, reverb, put, write = dt.mtof, dt.saw, dt.fft_filt, dt.onepole_lp, dt.reverb, dt.put, dt.write


# ---------------------------------------------------------------- instruments (new)
def kick_garage():
    n = int(0.26 * SR)
    t = np.arange(n) / SR
    f = 52 + 120 * np.exp(-t / 0.018)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.11)
    click = fft_filt(rng.standard_normal(n), 2500, 9000) * np.exp(-t / 0.002) * 0.7
    return np.tanh(2.0 * (body + click)) * 0.8


def clap_tight(vol=1.0):
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for d in (0, 0.008, 0.017):
        i = int(d * SR)
        m = n - i
        x[i:] += fft_filt(rng.standard_normal(m), 1100, 7500) * np.exp(-np.arange(m) / SR / 0.016)
    body = dt.snare_ind(0.5, n)
    return reverb(np.tanh(1.6 * (x + body)) * vol * 0.6, 0.6, 0.25)


def rim(vol=0.3):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 1730 * t) + 0.6 * np.sin(2 * np.pi * 2610 * t)) * np.exp(-t / 0.008)
    return x * vol


def shaker(vol=0.12):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return fft_filt(rng.standard_normal(n), 7000, 16000) * np.minimum(1, t / 0.006) * np.exp(-t / 0.018) * vol


def reese(f, n, wob=None, cut=420):
    t = np.arange(n) / SR
    r = (saw(f * 0.991, n, rng.random()) + saw(f * 1.009, n, rng.random()) + 0.5 * saw(f * 2.003, n, rng.random())) / 2.5
    fc = cut + (wob if wob is not None else 0) * np.ones(n)
    r = onepole_lp(r, fc)
    r = onepole_lp(r, fc * 1.3)
    return np.tanh(2.6 * r) * 0.6 + 0.2 * np.sin(2 * np.pi * f * t)


def chorus_pad(notes, n, depth=0.006):
    """swirling pad: detuned voices whose pitch drifts slowly, through a vectorised chorus (two modulated delay taps)"""
    t = np.arange(n) / SR
    x = np.zeros(n)
    for j, m in enumerate(notes):
        for d in (0.994, 1.0, 1.006):
            drift = 1 + 0.003 * np.sin(2 * np.pi * (0.07 + 0.03 * j) * t + rng.random() * 6)
            x += saw(mtof(m) * d * drift, n, rng.random())
    x /= len(notes) * 3
    x = fft_filt(x, 120, 2600)
    idx = np.arange(n, dtype=float)
    taps = []
    for rate, ph in ((0.21, 0.0), (0.33, 2.1)):
        dl = (0.012 + depth * (1 + np.sin(2 * np.pi * rate * t + ph))) * SR
        taps.append(np.interp(idx - dl, idx, x, left=0.0))
    return x, taps[0], taps[1]


def pingpong(x, d, fb=0.55, reps=6, hi=4200):
    """tape-ish ping-pong delay: each repeat darker, alternate sides"""
    n = len(x)
    L, R = x.copy(), x.copy() * 0.6
    y = x
    for k in range(1, reps + 1):
        y = fft_filt(y, 180, hi * (0.85 ** k)) * fb
        i = int(round(d * k * SR))
        if i >= n:
            break
        tgt = L if k % 2 == 0 else R
        tgt[i:] += y[:n - i]
    return L, R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stems")
    ap.add_argument("--bpm", type=float, default=136)
    ap.add_argument("--swing", type=float, default=0.58)
    a = ap.parse_args()
    P = json.load(open(a.plan))
    dur = P["duration"]
    N = int((dur + 3) * SR)
    step = 60 / a.bpm / 4
    sw = (a.swing - 0.5) * 2 * step          # delay of every odd 16th
    bar = 16 * step
    states = P["states"]
    releases = sorted(P.get("releases", []))
    hits = P.get("hits", [])

    def state(t):
        for s0, s1, k in states:
            if s0 <= t < s1:
                return k
        return "A"
    drums, bass, synth, fx, perc = (np.zeros(N) for _ in range(5))
    padL, padR = np.zeros(N), np.zeros(N)
    duck = np.ones(N)
    K = kick_garage()
    prog = [38, 39, 34, 36]                 # D Eb Bb C
    anchors = [0.0] + releases + [dur + 1]
    # ---------------- drums + bass on a 16th grid that restarts on every release (event-exact returns)
    for gi in range(len(anchors) - 1):
        g0, g1 = anchors[gi], anchors[gi + 1]
        k = 0
        while True:
            t = g0 + k * step
            if t >= min(g1, dur):
                break
            s, b = k % 16, k // 16
            ts = t + (sw if s % 2 else 0.0)
            st_ = state(t + 1e-4)
            root = prog[(int((t + 1e-6) / bar) // 2) % 4]
            f = mtof(root - 12)
            if st_ == "A":
                kicks = (0, 10) if b % 2 == 0 else (0, 10, 13)
                if s in kicks:
                    put(drums, K, ts, 1.0)
                    i = int(ts * SR)
                    m = min(N - i, int(0.16 * SR))
                    if m > 0:
                        duck[i:i + m] = np.minimum(duck[i:i + m], 1 - 0.7 * np.exp(-np.arange(m) / SR / 0.06))
                if s in (4, 12):
                    put(drums, clap_tight(), ts, 1.25)
                if s == 15 and b % 2:
                    put(drums, dt.snare_ind(0.25), ts)
                if s % 2:
                    put(perc, dt.hat(0.3), ts)
                if s in (2, 6, 10, 14):
                    put(perc, dt.hat(0.2, open_=(s == 14)), ts)
                put(perc, shaker(0.1 + 0.05 * (s % 2)), ts)
                if s in (3, 9) or (s == 7 and b % 2):
                    put(perc, rim(0.28), ts)
                # syncopated garage reese line: long on 1, pushes on the swung 7 and on 10
                ln = {0: 5, 7: 2, 10: 4}.get(s)
                if ln:
                    n = int(ln * step * SR)
                    tt = np.arange(n) / SR
                    wob = 900 * (0.5 + 0.5 * np.sin(2 * np.pi * tt / (2 * step) - np.pi / 2))
                    note = f * (2 ** (3 / 12) if s == 7 and b % 4 == 3 else 1)
                    env = np.minimum(1, tt / 0.006) * np.minimum(1, (n / SR - tt) / 0.03)
                    put(bass, reese(note, n, wob, 520) * env, ts)
                # dark filtered stabs on swung steps, every bar (garage organ feel, minor colour)
                if s in (3, 11) and b % 2 == 0:
                    put(synth, dt.stab([root + 24, root + 27, root + 31], int(0.2 * SR)), ts, 0.5)
            elif st_ == "B":
                if s == 8:
                    put(drums, dt.clap_big(1.0), t, 1.8)        # half-time backbeat (beat 3)
                if s % 2 == 0:
                    put(drums, dt.tick(0.26), t)
                if s == 14 and b % 2:
                    put(drums, dt.hat(0.14, True), ts)
            else:
                if s == 0:
                    put(drums, dt.tick(0.3), t)
            k += 1
    # ---------------- B world per bar: sub drone, swirling chorus pad, hypnotic arp through ping-pong delay
    arpL, arpR = np.zeros(N), np.zeros(N)
    nb = int(np.ceil(dur / bar)) + 2
    for b in range(nb):
        t0 = b * bar
        if t0 >= dur:
            break
        root = prog[(b // 2) % 4]
        f = mtof(root - 12)
        n = int(bar * SR)
        tt = np.arange(n) / SR
        sts = [state(t0 + x * bar / 8 + 1e-4) for x in range(8)]
        wB = np.interp(tt, np.linspace(0, bar, 8), [1.0 if s_ in ("B", "BREAK") else 0.0 for s_ in sts])
        if wB.max() <= 0:
            continue
        sub = np.sin(2 * np.pi * np.cumsum(np.full(n, f)) / SR) * 0.26 * np.minimum(1, tt / 0.05)
        put(bass, sub * wB, t0)
        dry, c1, c2 = chorus_pad([root + 12, root + 15, root + 19, root + 22], n)
        breath = 0.5 + 0.5 * np.sin(2 * np.pi * tt / (bar / 2) - np.pi / 2)
        pan = 0.5 + 0.5 * np.sin(2 * np.pi * (t0 + tt) / (bar * 1.5))
        pl = (0.6 * dry + c1) * (0.45 + 0.55 * breath) * wB
        pr = (0.6 * dry + c2) * (0.45 + 0.55 * breath) * wB
        put(padL, pl * (0.55 + 0.45 * pan), t0)
        put(padR, pr * (1.0 - 0.45 * pan), t0)
        # arp: 16ths over the chord, soft, filtered; the delay smears it into a hypnotic swirl
        notes = [root + 24, root + 27, root + 31, root + 34, root + 31, root + 27]
        for s in range(16):
            m = int(step * SR * 0.9)
            ta = np.arange(m) / SR
            fq = mtof(notes[s % len(notes)])
            v = (np.sin(2 * np.pi * fq * ta) + 0.3 * saw(fq, m, 0.0)) * np.minimum(1, ta / 0.003) * np.exp(-ta / 0.07)
            g = float(np.interp(s * step, tt, wB)) * (0.16 + 0.1 * (s % 4 == 0))
            put(arpL, v * g, t0 + s * step)
    aL, aR = pingpong(arpL, 3 * step)
    # ---------------- releases (C) and hits
    for r in releases:
        Ls = 1.1
        put(fx, dt.swell(int(Ls * SR), True, 600, 7000), r - Ls, 0.55)
        put(synth, dt.stab([prog[0] + 24, prog[0] + 27, prog[0] + 31], int(0.45 * SR)), r, 0.7)
    for h in hits:
        put(synth, dt.stab([prog[0] + 24, prog[0] + 27, prog[0] + 31], int(0.35 * SR)), h, 0.45)
    put(synth, dt.stab([prog[0] + 24, prog[0] + 27, prog[0] + 31], int(0.5 * SR)), 0.0, 0.8)
    # ---------------- end: last 30 ms fade in place
    e = int(dur * SR)
    for x in (drums, bass, synth, fx, perc, padL, padR, aL, aR):
        x[e:] = 0
        x[e - int(0.03 * SR):e] *= np.linspace(1, 0, int(0.03 * SR))
    bass_d = bass * duck
    i = int(0.012 * SR)
    sL, sR = synth, np.concatenate([np.zeros(i), synth[:-i]])
    fL, fR = fx, np.concatenate([np.zeros(int(0.017 * SR)), fx[:-int(0.017 * SR)]])
    pL, pR = perc, np.concatenate([np.zeros(int(0.009 * SR)), perc[:-int(0.009 * SR)]])
    L = 0.9 * drums + 0.8 * pL + 0.6 * bass_d + 0.55 * sL + 0.45 * fL + 0.75 * padL + 0.7 * aL
    R = 0.9 * drums + 0.8 * pR + 0.6 * bass_d + 0.55 * sR + 0.45 * fR + 0.75 * padR + 0.7 * aR
    L, R = L[:e], R[:e]
    pk = max(np.abs(L).max(), np.abs(R).max()) + 1e-9
    gain = 10 ** (-12 / 20) / pk
    write(a.out, L * gain, R * gain)
    if a.stems:
        os.makedirs(a.stems, exist_ok=True)
        for name, l_, r_ in (("drums", 0.9 * drums, 0.9 * drums), ("perc", 0.8 * pL, 0.8 * pR), ("bass", 0.6 * bass_d, 0.6 * bass_d), ("synth", 0.55 * sL, 0.55 * sR),
                             ("fx", 0.45 * fL, 0.45 * fR), ("pad", 0.75 * padL, 0.75 * padR), ("arp", 0.7 * aL, 0.7 * aR)):
            write(os.path.join(a.stems, f"{name}.wav"), l_[:e] * gain, r_[:e] * gain)
    print("bed", a.out, f"{dur:.2f}s", "states", len(states), "releases", releases)


if __name__ == "__main__":
    main()
