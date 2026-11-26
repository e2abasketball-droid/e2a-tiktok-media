#!/usr/bin/env python3
"""ZERO CUT TEST (aggressive hook) narration: ONE Deuce take for the whole test script (eleven_v3, 627 cr, owner OK
2026-11-26 16:34Z, flow 5HsMMzH5GjBovsSMW6K5, Scribe 0 cr). No regeneration, no time-stretch, no pitch change: the take
is split inside its own natural gaps (silencedetect -38 dB) and silences are inserted where the edit needs room.
15 ms fades at every splice. Writes public/zerocut3/voice-test.wav (48 kHz) + zerocut3-voice.words.json.
  python3 tactical/episodes/zerocut3/_voice-zerocut3.py"""
import json, os, subprocess
import numpy as np
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(os.path.dirname(D)))
RAW = os.path.join(T, "public/zerocut3/deuce-test-raw.mp3")
# (raw start, raw end, silence AFTER) - split points are mid-gap of the take's measured silences
SEGS = [(0.00, 2.73, 0.12),    # STOP calling yourself ELITE...
        (2.73, 4.64, 0.45),    # if you can't READ THIS.
        (4.64, 5.97, 0.30),    # This is the Zero Cut.
        (5.97, 8.21, 0.45),    # It starts by SELLING the handoff.
        (8.21, 9.47, 0.55),    # Watch the defender.                     (slow motion starts)
        (9.47, 12.14, 1.10),   # His weight is already on the WRONG leg.  (red leg blinks, hold)
        (12.14, 13.90, 0.45),  # The guard changes direction...           (hip pivot arc)
        (13.90, 15.43, 0.25),  # slips BEHIND him...
        (15.43, 16.84, 0.45),  # and the lane OPENS.
        (16.84, 18.95, 0.15),  # No handoff. One pass.                    (beat returns on "One pass")
        (18.95, 20.19, 1.55),  # EASY finish.                             (layup payoff + overhead establish)
        (20.19, 22.38, 0.55),  # But if the help defender steps across...
        (22.38, 23.57, 0.40),  # don't force it.
        (23.57, 25.99, 1.35),  # That rotation leaves the CORNER open.    (kick, catch, shot)
        (25.99, 26.98, 0.80),  # One cut.
        (26.98, 28.00, 0.90),  # Two reads.
        (28.00, 30.27, 0.40),  # Elite players don't just run plays.
        (30.27, 32.02, 0.85),  # They READ the defense.
        (32.02, 37.30, 0.45),  # The future elite will think faster... read faster... and punish every mistake.
        (37.30, 99.0, 0.0)]    # Follow E2A... and be part of the elite of the future.
F = int(0.015 * SR)


def load(p):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True, check=True).stdout, dtype=np.float32).copy()


def fade(s, i=True, o=True):
    s = s.copy()
    if i: s[:F] *= np.linspace(0, 1, F)
    if o: s[-F:] *= np.linspace(1, 0, F)
    return s


v = load(RAW)
parts, t, offs = [], 0.0, []
for a, b, g in SEGS:
    seg = v[int(a * SR):min(len(v), int(b * SR))]
    offs.append((a, min(b, len(v) / SR), t))
    parts += [fade(seg, a > 0, True), np.zeros(int(g * SR), np.float32)]
    t += len(seg) / SR + g
y = np.concatenate(parts)
out = os.path.join(T, "public/zerocut3/voice-test.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", out],
               input=y.astype(np.float32).tobytes(), check=True)
res = []
for w in json.load(open(os.path.join(D, "zerocut3-voice.words-raw.json")))["words"]:
    if w["text"].startswith("[") or w["text"].endswith("]") or w.get("type") != "word":
        continue
    for a, b, o in offs:
        m = (w["start"] + w["end"]) / 2  # decide by the word midpoint, clamp to the segment
        if a <= m < b:
            res.append({"text": w["text"], "start": round(max(o, w["start"] - a + o), 3), "end": round(min(b, w["end"]) - a + o, 3)})
            break
# onset correction: Scribe's word clock drifts on this take (up to ~0.35 s late on "So..."). Per segment, the first
# word is snapped to the measured speech onset (20 ms frames, -35 dB re the take's peak frame) and the segment's words
# move with it; word ends are clamped so words never overlap.
fr = y[: len(y) // 960 * 960].reshape(-1, 960)
lev = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
thr = lev.max() - 35
def onset(t0, t1):
    i0, i1 = int(t0 / 0.02), int(t1 / 0.02)
    for i in range(i0, min(i1, len(lev))):
        if lev[i] > thr and (i + 2 < len(lev) and lev[i + 1] > thr):
            return i * 0.02
    return None
hookn = 0
segs_out = [(o, o + (b - a)) for a, b, o in offs]
for si, (o0, o1) in enumerate(segs_out):
    idx = [i for i in range(hookn, len(res)) if o0 - 0.01 <= res[i]["start"] < o1]
    if not idx:
        continue
    on = onset(o0, min(o1, o0 + 1.0))
    if on is None:
        continue
    dlt = on - res[idx[0]]["start"]
    if abs(dlt) > 0.04:
        for i in idx:
            res[i]["start"] = round(max(o0, res[i]["start"] + dlt), 3)
            res[i]["end"] = round(min(o1, res[i]["end"] + dlt), 3)
for i in range(len(res) - 1):
    res[i]["end"] = round(min(res[i]["end"], res[i + 1]["start"]), 3)
json.dump(res, open(os.path.join(D, "zerocut3-voice.words.json"), "w"), indent=0)
print(f"voice {len(y)/SR:.2f} s, {len(res)} words, last word ends {res[-1]['end']}")
for a, b, o in offs:
    print(f"  raw {a:5.2f}-{b:5.2f} -> {o:6.2f}")
