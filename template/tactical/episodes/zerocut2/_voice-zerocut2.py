#!/usr/bin/env python3
"""ZERO CUT V2 narration: the V1 hook (approved take, flow QarXx5mV4GLHeDHp93XQ, 0 new credits) + ONE new Deuce take
for the V2 script (eleven_v3, 552 cr, flow nUrkOIITd3O7IWu5dSDe, Scribe 0 cr). No regeneration, no time-stretch, no pitch
change: the take is split inside its own natural gaps (measured with silencedetect) and silences are inserted where the
edit needs room (slow motion, payoffs, the closing question). 15 ms fades at every splice.
Writes public/zerocut2/voice-v2.wav (48 kHz mono) + zerocut2-voice.words.json (tags removed, times on the V2 timeline).
  python3 tactical/episodes/zerocut2/_voice-zerocut2.py"""
import json, os, subprocess
import numpy as np
SR = 48000
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(os.path.dirname(D)))
HOOK_RAW = os.path.join(T, "public/zerocut/deuce-take-raw.mp3")
V2_RAW = os.path.join(T, "public/zerocut2/deuce-v2-raw.mp3")
HOOK_END = 3.73
# (raw start, raw end, silence AFTER) - split points are mid-gap of the take's measured silences
SEGS = [(0.00, 5.27, 1.00),    # This is the ZERO CUT. The guard SELLS a handoff. Watch how his defender reacts.
        (5.27, 6.74, 0.70),    # He follows the ball...            (slow motion, half-time music)
        (6.74, 8.04, 0.70),    # shifts his weight...
        (8.04, 10.44, 0.60),   # and opens the lane BEHIND him.    (reveal hold)
        (10.44, 14.10, 0.30),  # NO HANDOFF! The guard CUTS, the big finds him,   (beat returns on NO)
        (14.10, 15.95, 2.00),  # and it's an EASY finish.          (layup payoff + overhead establish)
        (15.95, 18.12, 0.50),  # But if the low defender STEPS ACROSS,
        (18.12, 19.47, 0.50),  # don't force the layup.
        (19.47, 22.67, 1.30),  # That help leaves the CORNER open. FIND THE SHOOTER.   (the shot)
        (22.67, 23.68, 0.90),  # One cut.        (read 1)
        (23.68, 24.67, 1.10),  # Two reads.      (read 2)
        (24.67, 26.74, 0.50),  # Great players don't just run plays.
        (26.74, 28.45, 0.90),  # They READ the defense.
        (28.45, 29.12, 0.30),  # So...
        (29.12, 30.99, 0.40),  # do you think you have what it takes...
        (30.99, 99.0, 0.0)]    # to go PRO?
HOOK_GAP = 0.55
F = int(0.015 * SR)


def load(p):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True, check=True).stdout, dtype=np.float32).copy()


def fade(s, i=True, o=True):
    s = s.copy()
    if i: s[:F] *= np.linspace(0, 1, F)
    if o: s[-F:] *= np.linspace(1, 0, F)
    return s


h = load(HOOK_RAW)[:int(HOOK_END * SR)]
v = load(V2_RAW)
# loudness match: the new take to the hook's RMS (speech parts only)
def act_rms(x):
    fr = x[: len(x) // 480 * 480].reshape(-1, 480)
    r = np.sqrt((fr ** 2).mean(1))
    return np.sqrt((r[r > r.max() * 0.1] ** 2).mean())
v *= act_rms(h) / act_rms(v)
parts = [fade(h, False, True), np.zeros(int(HOOK_GAP * SR), np.float32)]
t = HOOK_END + HOOK_GAP
offs = []   # (raw start, raw end, output start)
for a, b, g in SEGS:
    seg = v[int(a * SR):min(len(v), int(b * SR))]
    offs.append((a, b, t))
    parts += [fade(seg), np.zeros(int(g * SR), np.float32)]
    t += len(seg) / SR + g
y = np.concatenate(parts)
out = os.path.join(T, "public/zerocut2/voice-v2.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", out],
               input=y.astype(np.float32).tobytes(), check=True)
res = []
for w in json.load(open(os.path.join(T, "tactical/episodes/zerocut/zerocut-voice.words-raw.json")))["words"]:
    if w["text"].startswith("[") or w.get("type") != "word":
        continue
    if w["end"] > HOOK_END + 0.05:
        break
    res.append({"text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3)})
for w in json.load(open(os.path.join(D, "zerocut2-voice.words-raw.json")))["words"]:
    if w["text"].startswith("[") or w["text"].endswith("]") or w.get("type") != "word":
        continue
    for a, b, o in offs:
        m = (w["start"] + w["end"]) / 2  # Scribe boundaries drift ~0.1 s: decide by the word midpoint, clamp to the segment
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
hookn = sum(1 for w in res if w["start"] < HOOK_END + 0.01)
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
json.dump(res, open(os.path.join(D, "zerocut2-voice.words.json"), "w"), indent=0)
print(f"voice {len(y)/SR:.2f} s, {len(res)} words, last word ends {res[-1]['end']}")
for a, b, o in offs:
    print(f"  raw {a:5.2f}-{b:5.2f} -> {o:6.2f}")
