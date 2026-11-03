#!/usr/bin/env python3
"""E2A music engine: original sports instrumentals, composed and mixed to fit each video.

Every bed is synthesised here from scratch (no samples, no third-party recordings), so E2A owns the
result and can use it commercially on Instagram, TikTok and YouTube with no licence or credits.

One call makes the music for one video:
  * picks a track from the library (library.json) that fits the story type, avoiding recent repeats
  * arranges it to the exact video length: hook from frame 0, build, DROP on the reveal sentence,
    break before the payoff, second drop, final hit when the narration ends, tail under the logo
  * mixes it around the narration: bass and kick stay full, mids/highs duck under the voice and
    open up in pauses; a 1.5-4 kHz pocket keeps the ElevenLabs voice clear
  * writes a stereo MP3 meant to be played at volume 1 (it already carries its own fades and ducking)

Usage:
  python3 music/e2a_music.py --story curiosity --words template/src/words.json \
      --out template/public/music.mp3 [--duration 46.2] [--track hype_a] [--seed 7] [--history music/history.json]
Story types: curiosity, record, highlight, tactical, surprise, psychology.
Only numpy and ffmpeg are needed.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np

SR = 44100
SPEECH_SNR = 17.0  # dB: voice over music in 300-4000 Hz while talking
FULL_UNDER = 6.0  # dB: music (all bands, bass included) under the voice while talking
VOICE_REF_SPEECHBAND = -20.0  # dBFS fallback when the narration file is not given
VOICE_REF_FULL = -19.0
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------------------------
# DSP helpers
# ---------------------------------------------------------------------------------------------


def mtof(m):
    return 440.0 * 2 ** ((np.asarray(m, dtype=float) - 69) / 12)


def fft_filter(x, gain_fn):
    n = len(x)
    if n == 0:
        return x
    L = 1 << int(math.ceil(math.log2(n + 1)))
    X = np.fft.rfft(x, L)
    f = np.fft.rfftfreq(L, 1 / SR)
    return np.fft.irfft(X * gain_fn(f), L)[:n]


def lp(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order))


def hp(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (np.maximum(fc, 1e-3) / np.maximum(f, 1e-3)) ** (2 * order))


def bp(lo, hi, order=2):
    a, b = hp(lo, order), lp(hi, order)
    return lambda f: a(f) * b(f)


def peak(fc, gain_db, q=1.0):
    g = 10 ** (gain_db / 20)
    return lambda f: 1 + (g - 1) * np.exp(-0.5 * (np.log2(np.maximum(f, 1) / fc) * q * 2) ** 2)


def env_exp(n, rate):
    return np.exp(-np.arange(n) / SR * rate)


def adsr(n, a=0.005, d=0.1, s=0.7, r=0.05):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-6), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-6)))
    rn = min(n, int(r * SR))
    if rn > 0:
        e[-rn:] *= np.linspace(1, 0, rn)
    return e


_TABLES: dict = {}


def _table(shape, nh):
    key = (shape, nh)
    if key not in _TABLES:
        N = 4096
        ph = np.arange(N) / N * 2 * np.pi
        t = np.zeros(N)
        for k in range(1, nh + 1):
            if shape == 'saw':
                t += np.sin(k * ph) / k
            elif shape == 'square' and k % 2:
                t += np.sin(k * ph) / k
            elif shape == 'tri' and k % 2:
                t += ((-1) ** ((k - 1) // 2)) * np.sin(k * ph) / k ** 2
        if shape == 'sine':
            t = np.sin(ph)
        t /= np.max(np.abs(t)) + 1e-9
        _TABLES[key] = t
    return _TABLES[key]


def osc(freq, n, shape='saw', rng=None, phase=None):
    """Band-limited wavetable oscillator. freq may be a scalar or a per-sample array."""
    fmax = float(np.max(freq))
    nh = max(1, min(64, int(SR / 2 / max(fmax, 1))))
    tbl = _table(shape, nh)
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    p0 = (rng.random() if rng is not None else 0.0) if phase is None else phase
    ph = (p0 + np.cumsum(f) / SR) % 1.0
    idx = ph * len(tbl)
    i0 = idx.astype(int)
    fr = idx - i0
    return tbl[i0] * (1 - fr) + tbl[(i0 + 1) % len(tbl)] * fr


def supersaw(freq, n, rng, voices=5, spread=0.16):
    l = np.zeros(n)
    r = np.zeros(n)
    for v in range(voices):
        det = (v - (voices - 1) / 2) / max(1, (voices - 1) / 2) * spread
        s = osc(freq * 2 ** (det / 12), n, 'saw', rng)
        pan = 0.5 + 0.45 * (det / spread if spread else 0)
        l += s * math.cos(pan * math.pi / 2)
        r += s * math.sin(pan * math.pi / 2)
    return np.stack([l, r]) / math.sqrt(voices)


def reverb(x, secs=1.6, predelay=0.02, damp=6000, seed=1):
    """Convolution reverb with a synthetic decorrelated stereo IR. x: (2, n)."""
    rng = np.random.default_rng(seed)
    n_ir = int(secs * SR)
    t = np.arange(n_ir) / SR
    out = []
    for ch in range(2):
        ir = rng.standard_normal(n_ir) * np.exp(-6.9 * t / secs)
        ir = fft_filter(ir, lp(damp, 1))
        ir = np.concatenate([np.zeros(int(predelay * SR)), ir])
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        L = 1 << int(math.ceil(math.log2(x.shape[1] + len(ir))))
        y = np.fft.irfft(np.fft.rfft(x[ch], L) * np.fft.rfft(ir, L), L)[: x.shape[1]]
        out.append(y)
    return np.stack(out)


def sat(x, drive=1.5):
    return np.tanh(x * drive) / np.tanh(drive)


def pan2(x, pan=0.5):
    return np.stack([x * math.cos(pan * math.pi / 2), x * math.sin(pan * math.pi / 2)]) * math.sqrt(2)


# ---------------------------------------------------------------------------------------------
# One-shots (drums and FX), generated once per render with a fixed seed
# ---------------------------------------------------------------------------------------------


class Kit:
    def __init__(self, seed, style):
        rng = np.random.default_rng(seed)
        self.rng = rng
        noise = lambda s: rng.standard_normal(int(s * SR))
        hard = style in ('trap', 'hype', 'drill')

        n = int(0.55 * SR)
        t = np.arange(n) / SR
        f = 42 + (150 if hard else 120) * np.exp(-t * 38)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (5 if hard else 8))
        click = fft_filter(noise(0.55), bp(1500, 9000)) * np.exp(-t * 260) * 0.35
        self.kick = sat(body + click, 2.2 if hard else 1.6)

        n = int(0.4 * SR)
        t = np.arange(n) / SR
        tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 22) * 0.55
        sn = fft_filter(noise(0.4), bp(900, 9500)) * np.exp(-t * 15)
        self.snare = sat(tone + sn * 0.8, 1.4)

        n = int(0.45 * SR)
        t = np.arange(n) / SR
        cl = np.zeros(n)
        for k, off in enumerate((0, 0.009, 0.019, 0.03)):
            i = int(off * SR)
            cl[i:] += np.exp(-np.arange(n - i) / SR * (140 if k < 3 else 16)) * (1 if k < 3 else 0.9)
        self.clap = fft_filter(noise(0.45) * cl, bp(800, 6000)) * 1.3

        n = int(0.09 * SR)
        self.hat = fft_filter(noise(0.09), hp(7500, 3)) * np.exp(-np.arange(n) / SR * 70) * 0.55
        n = int(0.5 * SR)
        self.ohat = fft_filter(noise(0.5), hp(6500, 3)) * np.exp(-np.arange(n) / SR * 8) * 0.45
        n = int(0.12 * SR)
        t = np.arange(n) / SR
        self.rim = (np.sin(2 * np.pi * 1700 * t) * 0.4 + fft_filter(noise(0.12), bp(2000, 6000))) * np.exp(-t * 60) * 0.5

        n = int(1.0 * SR)
        t = np.arange(n) / SR
        f = 48 + 40 * np.exp(-t * 20)
        self.taiko = sat(
            np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
            + fft_filter(noise(1.0), bp(80, 900)) * np.exp(-t * 14) * 0.6,
            1.8,
        )
        n = int(0.7 * SR)
        t = np.arange(n) / SR
        f = 95 + 60 * np.exp(-t * 18)
        self.tom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + fft_filter(noise(0.7), bp(150, 1500)) * np.exp(-t * 25) * 0.3

        # impact: sub boom + filtered crash, gets reverb later
        n = int(3.0 * SR)
        t = np.arange(n) / SR
        f = 30 + 45 * np.exp(-t * 6)
        boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
        crash = fft_filter(noise(3.0), bp(400, 12000)) * np.exp(-t * 2.8) * 0.5
        self.impact = sat(boom * 1.2 + crash, 1.6)

        # basketball one-shots for the sound design layer
        n = int(0.6 * SR)
        t = np.arange(n) / SR
        self.swish = fft_filter(noise(0.6), bp(1800, 9000)) * (np.sin(np.pi * np.clip(t / 0.35, 0, 1)) ** 2) * 0.7
        n = int(0.35 * SR)
        t = np.arange(n) / SR
        fsq = 1900 + 900 * np.sin(2 * np.pi * 6 * t)
        self.squeak = (osc(fsq, n, 'square', rng) * 0.25 + osc(fsq * 2.01, n, 'tri', rng) * 0.2) * adsr(n, 0.01, 0.08, 0.6, 0.06)
        self.squeak = fft_filter(self.squeak, bp(1200, 7000))

        # ball bounce on hardwood: short low thump + hollow body ring
        n = int(0.35 * SR)
        t = np.arange(n) / SR
        self.bounce = sat(
            np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-t * 60)) / SR) * np.exp(-t * 28)
            + np.sin(2 * np.pi * 420 * t) * np.exp(-t * 45) * 0.25
            + fft_filter(noise(0.35), bp(150, 2500)) * np.exp(-t * 90) * 0.4,
            1.5,
        )
        # bass hit: sub drop for section changes
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        self.bass_hit = sat(np.sin(2 * np.pi * np.cumsum(32 + 70 * np.exp(-t * 9)) / SR) * np.exp(-t * 3.2), 2.0)

    def crowd(self, secs, swell=True):
        """Arena crowd: many band-limited noise 'voices' with slow random swells."""
        n = int(secs * SR)
        out = np.zeros((2, n))
        for v in range(10):
            lo = 250 + self.rng.random() * 500
            band = fft_filter(self.rng.standard_normal(n), bp(lo, lo * 5))
            ctrl = fft_filter(self.rng.standard_normal(n), lp(2.5, 1))
            ctrl = 0.6 + 0.4 * ctrl / (np.max(np.abs(ctrl)) + 1e-9)
            out += pan2(band * ctrl, self.rng.random())
        if swell:
            t = np.linspace(0, 1, n)
            out *= np.sin(np.pi * np.clip(t * 1.25, 0, 1)) ** 0.7
        return out / 10 * 0.9

    def riser(self, secs):
        n = int(secs * SR)
        t = np.arange(n) / SR
        prog = t / secs
        nz = self.rng.standard_normal(n)
        # time-varying band: crossfade across 6 fixed bands as the sweep rises
        bands = [fft_filter(nz, bp(fc * 0.6, fc * 1.6)) for fc in (300, 600, 1200, 2400, 4800, 9000)]
        pos = prog * (len(bands) - 1)
        y = np.zeros(n)
        for i, b in enumerate(bands):
            y += b * np.clip(1 - np.abs(pos - i), 0, 1)
        tone = osc(110 * 2 ** (prog * 2.5), n, 'saw', self.rng) * 0.18
        tone = fft_filter(tone, lp(3000))
        return (y * 0.8 + tone) * prog ** 2.2

    def revcym(self, secs):
        n = int(secs * SR)
        y = fft_filter(self.rng.standard_normal(n), hp(3500)) * np.exp(-np.arange(n) / SR * 3.2)
        return y[::-1] * 0.6


# ---------------------------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------------------------


def i_808(f, dur, rng, glide_from=None, drive=2.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = np.full(n, f)
    if glide_from:
        g = np.exp(-t * 18)
        fr = f + (glide_from - f) * g
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR)
    e = adsr(n, 0.004, 0.9, 0.0, 0.03) * 0.95 + 0.05
    e[-min(n, int(0.03 * SR)):] *= np.linspace(1, 0, min(n, int(0.03 * SR)))
    # harmonics so the bass line is heard on phone speakers
    return sat(s * e, drive) * 0.9


def i_stab(freqs, dur, rng, bright=4200, dark=1100):
    n = int(dur * SR)
    out = np.zeros((2, n))
    for f in freqs:
        bend = f * 2 ** (np.clip(-1 + np.arange(n) / SR / 0.035, -1, 0) / 12)
        out += supersaw(bend, n, rng, 5, 0.14)
    b = np.stack([fft_filter(c, lp(bright)) for c in out])
    d = np.stack([fft_filter(c, lp(dark)) for c in out])
    fe = env_exp(n, 9)
    y = b * fe + d * (1 - fe)
    return y * adsr(n, 0.004, 0.22, 0.45, 0.06) / max(1, len(freqs)) ** 0.6


def i_pad(freqs, dur, rng, cutoff=1500, attack=0.35):
    n = int(dur * SR)
    out = np.zeros((2, n))
    for f in freqs:
        out += supersaw(f, n, rng, 5, 0.2)
    out = np.stack([fft_filter(c, lp(cutoff)) for c in out])
    return out * adsr(n, attack, 1.0, 1.0, 0.4) / max(1, len(freqs)) ** 0.6 * 0.6


def i_pluck(f, dur, rng):
    n = int(dur * SR)
    s = osc(f, n, 'saw', rng) * 0.6 + osc(f * 1.003, n, 'square', rng) * 0.4
    b = fft_filter(s, lp(6500))
    d = fft_filter(s, lp(1200))
    return (b * env_exp(n, 14) + d * env_exp(n, 4) * 0.55) * adsr(n, 0.002, 1, 1, 0.03)


def i_bell(f, dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for ratio, amp, dec in ((1, 1, 2.2), (2.0, 0.5, 3.5), (2.76, 0.35, 5), (5.4, 0.2, 8), (8.93, 0.1, 12)):
        y += amp * np.sin(2 * np.pi * f * ratio * t + rng.random() * 6.28) * np.exp(-t * dec)
    return y * adsr(n, 0.002, 1, 1, 0.05) * 0.5


def i_ep(f, dur, rng):
    """FM electric piano for the hip-hop beds."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    idx = 1.8 * np.exp(-t * 4)
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) * np.exp(-t * 1.6)
    y += 0.25 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 5)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    return y * trem * adsr(n, 0.003, 1, 1, 0.08) * 0.6


def i_string(f, dur, rng):
    n = int(dur * SR)
    s = sum(osc(f * 2 ** (d / 1200), n, 'saw', rng) for d in (-7, 0, 7)) / 3
    s = fft_filter(s, lp(3800))
    return s * adsr(n, 0.004, 0.09, 0.35, 0.03)


def i_braam(f, dur, rng):
    n = int(dur * SR)
    out = supersaw(f, n, rng, 7, 0.25) + supersaw(f * 2, n, rng, 5, 0.2) * 0.6 + supersaw(f / 2, n, rng, 3, 0.1) * 0.8
    out = sat(out, 2.5)
    b = np.stack([fft_filter(c, lp(2600)) for c in out])
    d = np.stack([fft_filter(c, lp(300)) for c in out])
    op = np.clip(np.arange(n) / SR / 0.5, 0, 1)
    return (b * op + d * (1 - op)) * adsr(n, 0.02, 1.2, 0.5, 0.5) * 0.7


# ---------------------------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------------------------

MINOR = [0, 2, 3, 5, 7, 8, 10]
# chord progressions as minor-scale degrees (0-based)
PROGS = {
    'epic': [[0, 5, 2, 6], [0, 6, 5, 6], [0, 5, 3, 4]],
    'trap': [[0, 0, 5, 6], [0, 3, 5, 4], [0, 5, 0, 6]],
    'hiphop': [[0, 3, 5, 4], [0, 5, 3, 6], [0, 6, 5, 3]],
    'drive': [[0, 6, 5, 6], [0, 5, 6, 0], [0, 3, 6, 5]],
    'suspense': [[0, 0, 5, 5], [0, 1, 0, 1], [0, 0, 3, 3]],
}

STYLES = {
    # NBA Hype Music: half-time trap groove, brass stabs, huge 808
    'hype': dict(bpm=(140, 150), prog='epic', drums='trap', bass='808', lead='stab', chords='stab', crowd=True, verb=1.2),
    # Basketball Hip-Hop: boom-bap swing, EP chords, punchy bass, bell hook
    'hiphop': dict(bpm=(88, 96), prog='hiphop', drums='boombap', bass='808short', lead='bell', chords='ep', crowd=False, verb=0.9),
    # Epic Sports Trap: fast hats and rolls, pluck hook, drops
    'trap': dict(bpm=(142, 152), prog='trap', drums='trap', bass='808', lead='pluck', chords='pad', crowd=True, verb=1.0),
    # Cinematic Basketball: taikos, string ostinato, braams on the drops
    'cinematic': dict(bpm=(118, 128), prog='epic', drums='taiko', bass='808short', lead='string', chords='pad', crowd=False, verb=2.2),
    # High-energy sports beat for tactics: driving four-on-the-floor, pluck arps, claps
    'drive': dict(bpm=(122, 128), prog='drive', drums='drive', bass='808short', lead='arp', chords='stab', crowd=False, verb=0.8),
    # Suspense: ticking pulse and tension that explodes late into a hit
    'suspense': dict(bpm=(96, 104), prog='suspense', drums='pulse', bass='808', lead='bell', chords='pad', crowd=False, verb=1.8),
}

# story type -> (preferred styles in rotation order, where the drop goes as a share of the narration)
STORY = {
    'curiosity': (['hiphop', 'trap', 'hype'], 0.22),
    'record': (['cinematic', 'hype'], 0.25),
    'highlight': (['trap', 'hype'], 0.18),
    'tactical': (['drive', 'hiphop'], 0.25),
    'surprise': (['suspense', 'cinematic'], 0.55),
    'psychology': (['cinematic', 'hiphop'], 0.30),
}

PATTERNS = {
    # 16 steps per bar. In half-time trap the snare/clap is on step 8.
    'trap': dict(
        kick=[[0, 10], [0, 7, 10], [0, 3, 10, 13], [0, 6, 10, 11]],
        snare=[[8]],
        hat=list(range(0, 16, 2)),
    ),
    'boombap': dict(kick=[[0, 7, 10], [0, 3, 10], [0, 8, 10, 14]], snare=[[4, 12]], hat=list(range(0, 16, 2))),
    'taiko': dict(kick=[[0, 3, 6, 8, 11, 14], [0, 6, 8, 10, 12, 14]], snare=[[4, 12]], hat=list(range(0, 16, 2))),
    'drive': dict(kick=[[0, 4, 8, 12]], snare=[[4, 12]], hat=[2, 6, 10, 14]),
    'pulse': dict(kick=[[0, 4, 8, 12], [0, 8]], snare=[[12]], hat=list(range(0, 16, 4))),
}


# ---------------------------------------------------------------------------------------------
# Arrangement fitted to the narration
# ---------------------------------------------------------------------------------------------


def sentence_starts(words):
    s = [words[0]['start']]
    for i in range(1, len(words)):
        prev = words[i - 1]['text'].strip()
        if prev.endswith(('.', '?', '!', '...', ':')) or words[i]['start'] - words[i - 1]['end'] > 0.35:
            s.append(words[i]['start'])
    return s


def voice_activity(words, n):
    act = np.zeros(n)
    for w in words:
        a = int(max(0, w['start'] - 0.05) * SR)
        b = int((w['end'] + 0.08) * SR)
        act[a:b] = 1
    # attack 40 ms, release 300 ms (one-pole on a decimated copy for speed)
    dec = 100
    a = act[::dec]
    y = np.zeros_like(a)
    up = 1 - math.exp(-1 / (0.04 * SR / dec))
    dn = 1 - math.exp(-1 / (0.30 * SR / dec))
    v = 0.0
    for i, x in enumerate(a):
        v += (x - v) * (up if x > v else dn)
        y[i] = v
    return np.interp(np.arange(n), np.arange(len(y)) * dec, y)


def plan_sections(words, duration, drop_share, bar, style, drop_at=None, payoff_at=None):
    vstart, vend = words[0]['start'], words[-1]['end']
    starts = sentence_starts(words)
    target = vstart + max(3.5, drop_share * (vend - vstart))
    drop = drop_at if drop_at is not None else min([s for s in starts if s >= target] or [target], key=lambda s: abs(s - target))
    # offset so a bar line lands exactly on the drop
    offset = (-drop) % bar  # music time = video time + offset
    to_mt = lambda vt: vt + offset
    drop_bar = round(to_mt(drop) / bar)
    payoff_t = vstart + 0.78 * (vend - vstart)
    payoff_s = payoff_at if payoff_at is not None else min([s for s in starts if s > drop + 2 * bar] or [payoff_t], key=lambda s: abs(s - payoff_t))
    drop2_bar = max(drop_bar + (2 if payoff_at is not None else 4), round(to_mt(payoff_s) / bar))
    break_bar = max(drop_bar + 2, drop2_bar - (1 if bar > 2.5 else 2))
    end_bar = math.ceil(to_mt(vend) / bar) + 1
    if style == 'suspense':
        # tension holds until the reveal, then one long drop
        break_bar, drop2_bar = drop2_bar, drop2_bar
    secs = []
    build_bar = max(1, drop_bar - (1 if bar > 2.5 else 2))
    secs.append(('intro', 0, build_bar))
    secs.append(('build', build_bar, drop_bar))
    secs.append(('drop', drop_bar, break_bar))
    if drop2_bar > break_bar:
        secs.append(('break', break_bar, drop2_bar))
    secs.append(('drop2', drop2_bar, end_bar))
    return dict(offset=offset, drop=drop, payoff=payoff_s, vend=vend, sections=[s for s in secs if s[2] > s[1]])


# ---------------------------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------------------------


class Song:
    def __init__(self, style, seed, key=None, bpm=None):
        self.style = style
        self.cfg = STYLES[style]
        rng = np.random.default_rng(seed)
        self.rng = rng
        lo, hi = self.cfg['bpm']
        self.bpm = bpm or int(rng.integers(lo, hi + 1))
        self.key = key if key is not None else int(rng.integers(0, 12))
        self.prog = PROGS[self.cfg['prog']][int(rng.integers(0, len(PROGS[self.cfg['prog']])))]
        self.kit = Kit(seed, style)
        self.step = 60 / self.bpm / 4
        self.bar = self.step * 16
        pat = PATTERNS[self.cfg['drums']]
        self.kick_pats = pat['kick']
        self.snare_pat = pat['snare'][0]
        self.hat_pat = pat['hat']
        # 2-bar hook motif: (step, scale degree above chord root, length in steps)
        rhythm_bank = [
            [0, 3, 6, 10, 12, 16, 19, 22, 26],
            [0, 2, 4, 8, 11, 16, 18, 20, 24, 27],
            [0, 6, 8, 14, 16, 22, 24, 28],
            [0, 3, 7, 10, 14, 16, 19, 23, 26, 30],
        ]
        rh = rhythm_bank[int(rng.integers(0, len(rhythm_bank)))]
        degs = [0, 2, 4, 7, 4, 2, 9, 7, 4, 2, 0, 4]
        start = int(rng.integers(0, 4))
        self.motif = [(s, degs[(start + i * int(rng.integers(1, 3))) % len(degs)], 2 if i % 3 else 3) for i, s in enumerate(rh)]

    # pitch helpers ------------------------------------------------------------------------
    def degree(self, d, octave):
        return 12 * (octave + 1) + self.key + MINOR[d % 7] + 12 * (d // 7)

    def chord(self, bar_i, octave=4):
        root = self.prog[bar_i % 4]
        return [self.degree(root, octave), self.degree(root + 2, octave), self.degree(root + 4, octave)]

    # rendering ----------------------------------------------------------------------------
    def render(self, plan, total_secs):
        n = int(total_secs * SR) + SR
        off = plan['offset']
        # buses: drums, bass, music (chords/lead), fx; all stereo
        B = {k: np.zeros((2, n)) for k in ('drums', 'bass', 'music', 'fx', 'verb')}
        rng = self.rng
        kit = self.kit
        step, bar = self.step, self.bar

        def place(bus, sig, t, gain=1.0, pan=0.5):
            i = int(round(t * SR))
            if sig.ndim == 1:
                sig = pan2(sig, pan)
            if i >= n or i + sig.shape[1] <= 0:
                return
            a = max(0, i)
            b = min(n, i + sig.shape[1])
            B[bus][:, a:b] += sig[:, a - i : b - i] * gain

        cfg = self.cfg
        kicks = []
        for name, b0, b1 in plan['sections']:
            full = name in ('drop', 'drop2')
            for bi in range(b0, b1):
                t0 = bi * bar
                last = bi == b1 - 1
                ch = self.chord(bi)
                root = self.prog[bi % 4]
                # ---- drums
                kp = self.kick_pats[(bi * 3 + (1 if full else 0)) % len(self.kick_pats)]
                if name == 'break':
                    kp = []
                if name == 'build' and last:
                    kp = [s for s in kp if s < 8]
                if name == 'intro' and cfg['drums'] in ('trap', 'drive'):
                    kp = kp[:2]
                for s in kp:
                    if cfg['drums'] == 'taiko':
                        place('drums', kit.taiko, t0 + s * step, 0.9, 0.5 + rng.uniform(-0.15, 0.15))
                        if full and s in (0, 8):
                            place('drums', kit.kick, t0 + s * step, 0.8)
                            kicks.append(t0 + s * step)
                    else:
                        place('drums', kit.kick, t0 + s * step, 1.0)
                        kicks.append(t0 + s * step)
                if name != 'break' and (name != 'intro' or cfg['drums'] in ('boombap', 'drive')):
                    for s in self.snare_pat:
                        place('drums', kit.clap if cfg['drums'] in ('trap', 'drive') else kit.snare, t0 + s * step, 0.75)
                        if full and cfg['drums'] in ('trap', 'drive'):
                            place('drums', kit.snare, t0 + s * step, 0.35)
                if cfg['drums'] == 'pulse' and name != 'drop' and name != 'drop2':
                    for s in range(0, 16, 4):
                        place('drums', kit.rim, t0 + s * step, 0.5, 0.65)
                # hats
                if name in ('build', 'drop', 'drop2') or (name == 'intro' and cfg['drums'] != 'taiko'):
                    swing = step * 0.18 if cfg['drums'] == 'boombap' else 0
                    for s in self.hat_pat:
                        place('drums', kit.hat, t0 + s * step + (swing if s % 4 == 2 else 0), 0.55 if s % 4 else 0.7, 0.62)
                    if cfg['drums'] == 'trap' and (full or name == 'build'):
                        # trap rolls on the last beat of every 2nd bar
                        if bi % 2 == 1:
                            div = 3 if bi % 4 == 3 else 2
                            for k in range(4 * div):
                                place('drums', kit.hat, t0 + 12 * step + k * step / div, 0.35 + 0.25 * k / (4 * div), 0.62)
                        if full and bi % 4 == 2:
                            place('drums', kit.ohat, t0 + 14 * step, 0.5, 0.4)
                    if cfg['drums'] == 'drive' and full:
                        for s in range(1, 16, 2):
                            place('drums', kit.hat, t0 + s * step, 0.22, 0.38)
                if cfg['drums'] == 'taiko' and full:
                    for s in (2, 7, 10, 15):
                        place('drums', kit.tom, t0 + s * step, 0.55, 0.3 + 0.4 * (s % 2))
                # fill into the drop / drop2
                if last and name in ('build', 'break'):
                    for k in range(8):
                        place('drums', kit.snare, t0 + 8 * step + k * step, 0.25 + 0.08 * k, 0.5)
                # ---- bass
                bass_note = mtof(self.degree(root, 1 if self.key < 5 else 0))
                if cfg['bass'] == '808' and name != 'break':
                    pts = kp if kp else ([0] if name in ('intro', 'build') else [])
                    for j, s in enumerate(pts):
                        nxt = pts[j + 1] if j + 1 < len(pts) else 16
                        dur = (nxt - s) * step
                        glide = bass_note * 2 if (full and j == len(pts) - 1 and bi % 2) else None
                        place('bass', i_808(bass_note, dur + 0.02, rng, glide), t0 + s * step, 0.8)
                elif cfg['bass'] == '808short' and name != 'break':
                    for s in (kp or [0]):
                        place('bass', i_808(bass_note, step * 3, rng, None, 1.8), t0 + s * step, 0.75)
                # ---- chords
                chord_f = mtof(ch)
                if cfg['chords'] == 'stab' and name != 'intro':
                    hits = [0, 3, 6, 10] if full else [0]
                    for s in hits:
                        place('music', i_stab(chord_f, step * 2.2, rng), t0 + s * step, 0.55 if full else 0.35)
                elif cfg['chords'] == 'ep':
                    for s in (0, 6, 10) if full else (0, 8):
                        place('music', i_ep_chord(chord_f, step * 5, rng), t0 + s * step, 0.5)
                elif cfg['chords'] == 'pad' or name == 'intro':
                    place('music', i_pad(chord_f * (0.5 if name == 'intro' else 1), bar + 0.05, rng, 1200 if name in ('intro', 'break') else 2400), t0, 0.55)
                if name == 'break':
                    # tension bar(s): wide pad, claps on 2 and 4, riser on top
                    place('music', i_pad(chord_f, bar + 0.05, rng, 1800, 0.15), t0, 0.7)
                    for s in (4, 12):
                        place('drums', kit.clap, t0 + s * step, 0.45)
                    place('bass', i_808(bass_note, bar * 0.9, rng, None, 1.5), t0, 0.35)
                # ---- lead / hook
                lead = cfg['lead']
                show_lead = full or (name == 'break' and lead in ('bell', 'string')) or (name == 'build' and lead in ('arp', 'string'))
                if show_lead:
                    half = bi % 2
                    for s, d, ln in self.motif:
                        if (s >= 16) != bool(half):
                            continue
                        ss = s - 16 * half
                        f = mtof(self.degree(root + d, 5))
                        tt = t0 + ss * step
                        if lead == 'stab':
                            place('music', i_stab([f, f / 2], step * ln, rng, 5000, 1500), tt, 0.4, 0.5)
                        elif lead == 'pluck':
                            place('music', i_pluck(f, step * (ln + 2), rng), tt, 0.45, 0.42)
                        elif lead == 'bell':
                            place('music', i_bell(f, step * 6, rng), tt, 0.42, 0.58)
                        elif lead == 'string':
                            pass
                    if lead == 'string':
                        # 16th ostinato on chord tones, the cinematic engine
                        for s in range(16):
                            f = mtof(ch[[0, 1, 2, 1][s % 4]] + (12 if s % 8 >= 4 else 0))
                            place('music', i_string(f, step * 0.9, rng), t0 + s * step, 0.32 if full else 0.2, 0.3 + 0.4 * (s % 2))
                    if lead == 'arp':
                        for s in range(16):
                            f = mtof(ch[s % 3] + 12 * ((s // 3) % 2))
                            place('music', i_pluck(f, step * 1.5, rng), t0 + s * step, 0.26 if full else 0.16, 0.35 + 0.3 * (s % 2))
                # ---- fx on section edges
                if bi == b0 and name in ('drop', 'drop2'):
                    place('fx', kit.impact, t0, 0.55)
                    if cfg['lead'] in ('string', 'stab') or self.style in ('cinematic', 'suspense'):
                        place('music', i_braam(mtof(self.degree(root, 2)), bar * 1.0, rng), t0, 0.45)
                    if cfg['crowd'] and name == 'drop2':
                        place('fx', kit.crowd(bar * 2), t0, 0.35)
                if last and name in ('build', 'break'):
                    r = kit.riser(bar)
                    place('fx', r, t0, 0.35)
                    rc = kit.revcym(bar / 2)
                    place('fx', rc, t0 + bar / 2, 0.45)
        # basketball sound design woven into the bed
        first_bar = plan['sections'][0][1] * bar
        if self.style in ('drive', 'trap', 'hype'):
            for k, s in enumerate((0, 4, 8, 12, 16, 20, 24, 28)):
                place('fx', kit.bounce, off + 0.05 + s * step, 0.55 - 0.03 * k, 0.45)
            place('fx', kit.squeak, off + 0.05 + 22 * step, 0.35, 0.65)
        for name, b0, b1 in plan['sections']:
            if name in ('drop', 'drop2'):
                place('fx', kit.bass_hit, b0 * bar, 0.7)
        # the groove stops dead on the final hit; only the hit and its tail ring under the logo
        end_t = plan['vend'] + 0.12
        ci = int((end_t + off) * SR)
        fade = int(0.03 * SR)
        for k in ('drums', 'bass', 'music', 'fx'):
            if ci < n:
                B[k][:, ci - fade : ci] *= np.linspace(1, 0, fade)
                B[k][:, ci:] = 0
        # first frame: a hit so the video opens with energy
        place('fx', kit.impact, off, 0.42)
        place('fx', kit.impact, end_t + off, 0.75)
        last_chord = mtof(self.chord(0))
        place('music', i_stab(np.concatenate([last_chord, last_chord / 2]), 1.6, rng, 4000, 900), end_t + off, 0.6)
        if self.style in ('cinematic', 'suspense', 'hype'):
            place('music', i_braam(mtof(self.degree(self.prog[0], 2)), 2.2, rng), end_t + off, 0.5)
        place('drums', kit.taiko if self.style == 'cinematic' else kit.kick, end_t + off, 0.9)
        place('fx', kit.bass_hit, end_t + off, 0.8)
        place('fx', kit.swish, end_t + off - 0.28, 0.6, 0.55)
        if self.style in ('hype', 'trap', 'cinematic', 'suspense'):
            place('fx', kit.crowd(2.2, swell=True), end_t + off + 0.05, 0.45)
        cut = ci
        return B, kicks, cut

    def mix(self, B, kicks, words, total_secs, cut_at):
        n = B['drums'].shape[1]
        cfg = self.cfg
        # sidechain: pads/chords/lead pump under the kick
        sc = np.ones(n)
        for k in kicks:
            i = int((k - 0) * SR)
            if 0 <= i < n:
                ln = min(n - i, int(0.25 * SR))
                sc[i : i + ln] = np.minimum(sc[i : i + ln], 1 - 0.45 * np.exp(-np.arange(ln) / SR * 14))
        music = B['music'] * sc
        bass = B['bass']
        # reverb sends
        wet = reverb(music * 0.35 + B['drums'] * 0.12 + B['fx'] * 0.35, cfg['verb'], seed=3)
        bed = B['drums'] * 0.75 + bass * 0.42 + music * 1.25 + B['fx'] * 0.9 + wet * 0.5
        return bed

    def finish(self, bed, words, total_secs, offset, cut_t, duck=True, voice=None):
        """Trim to the video, multiband duck around the voice, master."""
        a = int(offset * SR)
        n = int(total_secs * SR)
        bed = bed[:, a : a + n]
        if bed.shape[1] < n:
            bed = np.pad(bed, ((0, 0), (0, n - bed.shape[1])))
        # high-pass rumble, voice pocket
        bed = np.stack([fft_filter(c, lambda f: hp(32, 2)(f) * peak(38, -3.5, 1.2)(f) * peak(2600, -4.5, 0.7)(f)) for c in bed])
        low = np.stack([fft_filter(c, lp(170, 4)) for c in bed])
        high = bed - low
        if duck and words:
            v = voice_activity(words, n)
            g_low = 1 - 0.30 * v  # -3 dB: kick and bass keep pushing under the voice
            g_high = 10 ** (-(11.0 * v) / 20)  # -11 dB on mids/highs while someone is talking
        else:
            g_low = g_high = np.ones(n)
        y = low * g_low + high * g_high
        y = self.calibrate(y, words, voice)
        # fades: open in 15 ms, close over the last 0.6 s
        fi = int(0.015 * SR)
        y[:, :fi] *= np.linspace(0, 1, fi)
        fo = int(0.6 * SR)
        y[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
        return np.clip(y, -0.98, 0.98)

    def calibrate(self, y, words, voice):
        """Set the bed level from the narration so the voice always wins in the speech band.

        Targets while someone is talking: music at least SPEECH_SNR dB under the voice in 300-4000 Hz,
        and no louder than FULL_UNDER dB under it overall. In pauses the ducking lifts it by ~11 dB."""
        n = y.shape[1]
        act = np.zeros(n, bool)
        for w in words:
            act[int(w['start'] * SR) : int(w['end'] * SR)] = True
        if not act.any():
            return y * 0.25
        db = lambda a: 10 * np.log10(np.mean(a ** 2) + 1e-12)
        if voice is not None:
            v = np.pad(voice, (0, max(0, n - len(voice))))[:n]
            v_sb, v_full = db(fft_filter(v, bp(300, 4000, 4))[act]), db(v[act])
        else:
            v_sb, v_full = VOICE_REF_SPEECHBAND, VOICE_REF_FULL
        # per-channel levels: the mono narration is played at full level on both channels
        m_sb = db(np.concatenate([fft_filter(c, bp(300, 4000, 4))[act] for c in y]))
        m_full = db(np.concatenate([c[act] for c in y]))
        g_db = min(v_sb - SPEECH_SNR - m_sb, v_full - FULL_UNDER - m_full)
        y = y * 10 ** (g_db / 20)
        pk = np.max(np.abs(y))
        if pk > 0.97:
            y = np.tanh(y / pk * 1.4) / np.tanh(1.4) * 0.97
        return y


def i_ep_chord(freqs, dur, rng):
    n = int(dur * SR)
    y = sum(i_ep(f, dur, rng) for f in freqs) / len(freqs) ** 0.6
    return pan2(y, 0.5)


# ---------------------------------------------------------------------------------------------
# Library + selection
# ---------------------------------------------------------------------------------------------


def load_library():
    with open(os.path.join(HERE, 'library.json')) as f:
        return json.load(f)


def pick_track(story, history_path, track=None):
    lib = load_library()
    tracks = {t['id']: t for t in lib['tracks'] if t.get('active', True)}
    if track:
        return tracks[track]
    styles, _ = STORY[story]
    hist = []
    if history_path and os.path.exists(history_path):
        with open(history_path) as f:
            hist = json.load(f)
    recent = [h['track'] for h in hist[-8:]]
    cands = [t for t in tracks.values() if t['style'] in styles]
    # prefer the first style for the story, but never one of the last few tracks used
    cands.sort(key=lambda t: (t['id'] in recent, recent[::-1].index(t['id']) * -1 if t['id'] in recent else 0, styles.index(t['style']), t['id']))
    fresh = [t for t in cands if t['id'] not in recent]
    if fresh:
        first_style = [t for t in fresh if t['style'] == styles[0]]
        pool = first_style or fresh
        return pool[len(hist) % len(pool)]
    return cands[0]


def make(words, story, out, duration=None, track=None, history=None, no_duck=False, voice_path=None, drop_at=None, payoff_at=None):
    t = pick_track(story, history, track)
    vend = words[-1]['end']
    total = duration or vend + 1.5
    song = Song(t['style'], t['seed'], t.get('key'), t.get('bpm'))
    drop_share = STORY[story][1] if story in STORY else 0.25
    plan = plan_sections(words, total, drop_share, song.bar, t['style'], drop_at, payoff_at)
    B, kicks, cut = song.render(plan, total + plan['offset'] + 1)
    bed = song.mix(B, kicks, words, total, cut)
    voice = None
    if voice_path:
        raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', voice_path, '-af', 'pan=mono|c0=c0', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
        voice = np.frombuffer(raw, np.float32).astype(float)
        ch = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=channels', '-of', 'csv=p=0', voice_path],
                            capture_output=True, text=True).stdout.strip()
        if ch == '1':
            voice = voice * 0.7071  # Remotion plays a mono file at -3 dB on each channel (equal-power upmix)
    y = song.finish(bed, words, total, plan['offset'], cut, duck=not no_duck, voice=voice)
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, 'bed.f32')
        y.T.astype(np.float32).tofile(raw)
        subprocess.run(
            ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', raw,
             '-c:a', 'libmp3lame', '-b:a', '256k', out],
            check=True,
        )
    info = dict(track=t['id'], style=t['style'], bpm=song.bpm, key=song.key, story=story,
                drop=round(plan['drop'], 2), payoff=round(plan['payoff'], 2), end_hit=round(plan['vend'] + 0.12, 2),
                sections=[(s, round(b0 * song.bar - plan['offset'], 2), round(b1 * song.bar - plan['offset'], 2)) for s, b0, b1 in plan['sections']],
                duration=round(total, 2), out=out)
    if history:
        hist = []
        if os.path.exists(history):
            with open(history) as f:
                hist = json.load(f)
        hist.append({'track': t['id'], 'story': story, 'out': out})
        with open(history, 'w') as f:
            json.dump(hist[-60:], f, indent=1)
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--words', required=True, help='ElevenLabs word timings JSON: [{text,start,end}]')
    ap.add_argument('--story', default='curiosity', choices=list(STORY))
    ap.add_argument('--out', required=True)
    ap.add_argument('--duration', type=float, help='video length in seconds (default: last word end + 1.5)')
    ap.add_argument('--drop-at', type=float, help='video second where the drop must land (default: the reveal sentence)')
    ap.add_argument('--payoff-at', type=float, help='video second for the second drop (default: the payoff sentence)')
    ap.add_argument('--track', help='force a library track id')
    ap.add_argument('--history', default=os.path.join(HERE, 'history.json'), help='rotation log ("" to disable)')
    ap.add_argument('--voice', help='the narration file (vo.mp3): sets the music level so the voice stays clear')
    ap.add_argument('--no-duck', action='store_true')
    ap.add_argument('--mix-json', help='template/src/music-mix.json: set premixed=true so the template plays the bed at volume 1')
    a = ap.parse_args()
    with open(a.words) as f:
        words = json.load(f)
    info = make(words, a.story, a.out, a.duration, a.track, a.history or None, a.no_duck, a.voice, a.drop_at, a.payoff_at)
    if a.mix_json:
        with open(a.mix_json, 'w') as f:
            json.dump({'premixed': True, 'gain': 1, 'track': info['track']}, f)
    print(json.dumps(info, indent=1))


if __name__ == '__main__':
    main()
