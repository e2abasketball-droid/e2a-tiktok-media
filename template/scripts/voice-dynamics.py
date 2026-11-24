#!/usr/bin/env python3
"""E2A Voice Dynamics (2026-11-24, Arrow Press 1-3-1 V2) - credit-free post-production of an existing narrator take.

Does NOT regenerate or alter the narrator (same take, same timbre, no pitch/time change). It only shapes what is there:
  1. tone     highpass 85 Hz, -2 dB @ 300 Hz (boxiness of a deep voice), +3 dB @ 2.8 kHz Q 1.4 (presence, intelligibility on
              phone speakers), -1.5 dB @ 7 kHz + de-esser (sibilance kept near the original balance)
  2. control  moderate compression (thr -24 dB, 2.5:1, attack 8 ms, release 140 ms)
  3. curve    per-phrase gain automation following an emotional curve: every line of the script gets a target offset
              (dB, relative to the explanation level). The gain changes only inside the pauses between lines (ramps
              <= 60 ms), never inside a word, so it sounds like delivery, not like a fader.
     --preserve (expressive takes, e.g. eleven_v3 with emotion tags): never turns a line down, only lifts a line that
              falls more than --tol dB under its target, so the take's own peaks and dips survive; gentler
              compression (thr -18 dB, 1.6:1).
  4. level    static gain to -16 LUFS (voice stem) + limiter; no dynamic loudnorm (it would undo the curve)
  5. mix      (optional --music) music ducked under the voice (sidechain), voice-to-music balance, final static gain
              to -14 LUFS integrated, true peak <= -1 dBTP (alimiter at -1.5 dBFS), 48 kHz.

Curve file (JSON): {"lines": [["Half court isn't a line.", 1.0, "A"], ...]} - the lines in order, matching the words
file exactly (same text as the take), the offset in dB and the phase label (A hook, B explanation, C activation,
D reads, E conclusion).

  python3 scripts/voice-dynamics.py --voice public/x/voice.wav --words w.json --curve c.json --out voice-v2.wav \
      [--music public/x/music.wav --mix-out mix.wav --music-gain -3 --duration 42.246] [--report r.json]
"""
import argparse, json, subprocess, sys
import numpy as np

SR = 48000
TONE = ("highpass=f=85,equalizer=f=300:t=q:w=1.0:g=-2,equalizer=f=2800:t=q:w=1.4:g=3,equalizer=f=7000:t=q:w=1.5:g=-1.5,"
        "deesser=i=0.45,acompressor=threshold=-24dB:ratio=2.5:attack=8:release=140:makeup=2")


def dec(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path] + (["-af", af] if af else []) + ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).copy()


def enc(x, path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", path],
                   input=x.astype(np.float32).tobytes(), check=True)


def lufs(path_or_x):
    if not isinstance(path_or_x, str):
        enc(path_or_x, "/dev/shm/_vd_tmp.wav")
        path_or_x = "/dev/shm/_vd_tmp.wav"
    out = subprocess.run(["ffmpeg", "-nostats", "-i", path_or_x, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    s = out[out.rfind("Summary:"):]
    val = lambda key: float(s.split(key)[1].split()[0])
    return {"I": val("I:"), "LRA": val("LRA:"), "TP": val("Peak:")}


def norm(s):
    return "".join(c for c in s.lower() if c.isalnum())


def lines_of(words, curve):
    res, i = [], 0
    for text, off, ph in curve:
        n = len(text.split())
        seg = words[i:i + n]
        if [norm(w["text"]) for w in seg] != [norm(x) for x in text.split()]:
            sys.exit(f"curve/words mismatch at {text!r}: {[w['text'] for w in seg]}")
        res.append({"text": text, "off": off, "phase": ph, "a": seg[0]["start"], "b": seg[-1]["end"]})
        i += n
    if i != len(words):
        sys.exit(f"curve covers {i} of {len(words)} words")
    return res


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True)
    ap.add_argument("--words", required=True)
    ap.add_argument("--curve", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--music")
    ap.add_argument("--mix-out")
    ap.add_argument("--music-gain", type=float, default=0.0, help="dB on the music bed before ducking")
    ap.add_argument("--duration", type=float)
    ap.add_argument("--max-gain", type=float, default=6.0)
    ap.add_argument("--report")
    ap.add_argument("--preserve", action="store_true",
                    help="expressive take: never turn a line down; only lift lines more than --tol dB under their target")
    ap.add_argument("--tol", type=float, default=1.5)
    a = ap.parse_args()

    words = json.load(open(a.words))
    curve = json.load(open(a.curve))["lines"]
    L = lines_of(words, curve)
    # the compressor threshold assumes a take at about -23 LUFS (ElevenLabs v2 level); a hotter take (v3 shouting comes
    # in near -15 LUFS) is brought there first, otherwise the whole take sits above threshold and the peaks get squashed
    pre = -23.0 - lufs(a.voice)["I"]
    tone = TONE.replace("acompressor=threshold=-24dB:ratio=2.5", "acompressor=threshold=-18dB:ratio=1.6") if a.preserve else TONE
    x = dec(a.voice, f"volume={pre:.2f}dB," + tone)
    # 3 curve: level of each line after tone + compression, target = reference (median of phase B) + offset
    lev = [rms_db(x[int(l["a"] * SR):int(l["b"] * SR)]) for l in L]
    refs = [v for v, l in zip(lev, L) if l["phase"] == "B"] or lev
    ref = float(np.median(refs))
    gains = [float(np.clip(ref + l["off"] - v, -a.max_gain, a.max_gain)) for v, l in zip(lev, L)]
    if a.preserve:
        # keep the performance: a line that already sits above its target keeps its level (0 dB); a line that falls more
        # than tol under it is lifted to (target - tol)
        gains = [float(min(a.max_gain, max(0.0, g - a.tol))) for g in gains]
    env = np.zeros(len(x), dtype=np.float64)
    # gain of line k holds from the middle of the pause before it to the middle of the pause after it; the change is
    # a raised-cosine ramp centred in the pause, at most 60 ms and never longer than the pause
    bounds = [0.0] + [(L[k]["b"] + L[k + 1]["a"]) / 2 for k in range(len(L) - 1)] + [len(x) / SR]
    for k, g in enumerate(gains):
        env[int(bounds[k] * SR):int(bounds[k + 1] * SR)] = g
    for k in range(len(L) - 1):
        gap = max(0.0, L[k + 1]["a"] - L[k]["b"])
        r = min(0.06, gap * 0.9)
        if r < 0.004:
            continue
        c = bounds[k + 1]
        i0, i1 = int((c - r / 2) * SR), int((c + r / 2) * SR)
        u = np.linspace(0, 1, i1 - i0)
        env[i0:i1] = gains[k] + (gains[k + 1] - gains[k]) * (0.5 - 0.5 * np.cos(np.pi * u))
    y = x * (10 ** (env / 20)).astype(np.float32)
    # 4 level: static gain to -16 LUFS, limiter
    m = lufs(y)
    y = y * 10 ** ((-16.0 - m["I"]) / 20)
    enc(y, "/dev/shm/_vd_pre.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/dev/shm/_vd_pre.wav", "-af", "aresample=192000,alimiter=limit=0.794:attack=2:release=40:level=false,aresample=48000",
                    "-ar", str(SR), "-c:a", "pcm_s24le", a.out], check=True)
    out_lev = [rms_db(dec(a.out)[int(l["a"] * SR):int(l["b"] * SR)]) for l in L]
    rep = {"tone": tone, "reference_db": round(ref, 2), "voice_in": lufs(a.voice), "voice_out": lufs(a.out),
           "lines": [{"text": l["text"], "phase": l["phase"], "target_off": l["off"], "level_in_db": round(v, 2), "gain_db": round(g, 2),
                      "level_out_rel_db": round(o - float(np.median([oo for oo, ll in zip(out_lev, L) if ll["phase"] == "B"])), 2)}
                     for l, v, g, o in zip(L, lev, gains, out_lev)]}
    # 5 mix
    if a.music and a.mix_out:
        dur = a.duration or len(y) / SR
        fc = (f"[1:a]aformat=sample_rates={SR}:channel_layouts=mono,volume={a.music_gain}dB,apad,atrim=0:{dur}[m];"
              f"[0:a]aformat=sample_rates={SR}:channel_layouts=mono,apad,atrim=0:{dur},asplit=2[v][k];"
              f"[m][k]sidechaincompress=threshold=0.04:ratio=5:attack=25:release=350:makeup=1[md];"
              f"[v][md]amix=inputs=2:normalize=0:duration=first[o]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.out, "-i", a.music, "-filter_complex", fc, "-map", "[o]",
                        "-ar", str(SR), "-c:a", "pcm_s24le", "/dev/shm/_vd_mix.wav"], check=True)
        mm = lufs("/dev/shm/_vd_mix.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/dev/shm/_vd_mix.wav", "-af",
                        f"volume={-14.0 - mm['I']:.2f}dB,aresample=192000,alimiter=limit=0.84:attack=2:release=50:level=false,aresample=48000", "-ar", str(SR),
                        "-c:a", "pcm_s24le", a.mix_out], check=True)
        rep["mix"] = lufs(a.mix_out)
    if a.report:
        json.dump(rep, open(a.report, "w"), indent=1)
    print(json.dumps({k: rep[k] for k in rep if k != "lines" and k != "tone"}))
    for r in rep["lines"]:
        print(f"{r['phase']} {r['gain_db']:+5.1f} dB  out {r['level_out_rel_db']:+5.1f}  {r['text']}")


if __name__ == "__main__":
    main()
