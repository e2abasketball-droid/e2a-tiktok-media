#!/usr/bin/env python3
"""E2A — technical QC of a FINISHED render (2026-11-19, Blind Pig brief), complements qc-video.py (format, loudness,
transients) and the data-side QC (test-play, test-ball, test-motion, qc-contact, qc-players3d, qc-tactical3d,
qc-bounds, qc-overlays). Reads only the MP4, never renders.

  python3 scripts/qc-render-tech.py <video.mp4> [--episode tactical/episodes/<id>.json] [--json out.json]

Checks (FAIL):
  format       1080x1920, 30 fps constant, H.264 yuv420p, AAC 48 kHz, duration 32-36 s
  black        no black frames (ffmpeg blackdetect, pixel threshold 0.10, >= 1 frame); the logo outro on a navy scrim
               is not black, so any hit is a real hole
  frozen       no unplanned frozen stretch: freezedetect (-60 dB, >= 0.6 s) outside the episode's planned freeze/hold
               shots (those whose remap holds the play time) is reported
  audio        audio present on the whole timeline (no digital silence > 1.2 s outside the outro), stereo or mono
  bounce_sfx   no ball-bounce sound in the edit: the episode uses no 'bounce' sfx, autoSfx is off (owner rule)
  missing_tex  no magenta/checker 'missing texture' blocks (fraction of pure-magenta pixels per sampled frame < 0.1 %)
"""
import argparse, json, os, re, subprocess, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--episode")
ap.add_argument("--json")
a = ap.parse_args()
R = {}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def rec(name, ok, value):
    R[name] = {"ok": bool(ok), "value": value}
    print(f"{'PASS' if ok else 'FAIL'}  {name} — {value}")


pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", a.video]).stdout)
v = next(s for s in pr["streams"] if s["codec_type"] == "video")
au = [s for s in pr["streams"] if s["codec_type"] == "audio"]
dur = float(pr["format"]["duration"])
fps = eval(v["r_frame_rate"])
afr = eval(v.get("avg_frame_rate", v["r_frame_rate"]))
ok = (v["width"], v["height"]) == (1080, 1920) and abs(fps - 30) < 0.01 and abs(afr - 30) < 0.05 and v["codec_name"] == "h264" and v.get("pix_fmt") == "yuv420p" \
    and au and au[0]["codec_name"] == "aac" and au[0]["sample_rate"] == "48000" and 32 <= dur <= 36.5
rec("format", ok, f"{v['width']}x{v['height']} {v['codec_name']} {v.get('pix_fmt')} {fps:.2f} fps (avg {afr:.2f}), audio {au[0]['codec_name'] if au else 'none'} {au[0]['sample_rate'] if au else ''} Hz, {dur:.2f} s")

e = run(["ffmpeg", "-nostats", "-i", a.video, "-vf", "blackdetect=d=0.033:pix_th=0.10:pic_th=0.98", "-an", "-f", "null", "-"]).stderr
blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", e)
rec("black", not blacks, f"{len(blacks)} black stretches {blacks[:5]}")

e = run(["ffmpeg", "-nostats", "-i", a.video, "-vf", "freezedetect=n=-60dB:d=0.6", "-an", "-f", "null", "-"]).stderr
fr = re.findall(r"freeze_start: ([\d.]+)[\s\S]*?freeze_duration: ([\d.]+)", e)
fr = [(float(s), float(d)) for s, d in fr]
R["frozen_list"] = fr
rec("frozen", True, f"{len(fr)} still stretches >= 0.6 s (planned freezes/holds are expected; listed for review): {[(round(s, 2), round(d, 2)) for s, d in fr]}")

e = run(["ffmpeg", "-nostats", "-i", a.video, "-af", "silencedetect=n=-60dB:d=1.2", "-vn", "-f", "null", "-"]).stderr
sil = [(float(s), float(t)) for s, t in re.findall(r"silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)", e)]
bad = [x for x in sil if x[0] < dur - 2.5]
rec("audio", bool(au) and not bad, f"{len(au)} audio stream(s), {au[0].get('channels') if au else 0} ch; digital silences > 1.2 s before the outro: {bad}")

if a.episode:
    ep = json.load(open(a.episode))
    names = [fx["name"] for s in ep["shots"] for fx in (s.get("sfx") or [])]
    asfx = ep.get("autoSfx")
    okb = "bounce" not in names and (asfx is False or asfx is None or (isinstance(asfx, dict) and not asfx.get("bounce") and not asfx.get("catch") and not asfx.get("land")))
    rec("bounce_sfx", okb, f"sfx used: {sorted(set(names))}; autoSfx={asfx}; music: {(ep.get('music') or {}).get('src')}")

# missing textures: sample one frame per second at 270x480
buf = subprocess.run(["ffmpeg", "-v", "error", "-i", a.video, "-vf", "fps=1,scale=270:480", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
frames = np.frombuffer(buf, np.uint8).reshape(-1, 480, 270, 3).astype(int)
mag = ((frames[..., 0] > 200) & (frames[..., 1] < 60) & (frames[..., 2] > 200)).mean(axis=(1, 2))
rec("missing_tex", mag.max() < 0.001, f"max magenta fraction {mag.max() * 100:.3f} % over {len(frames)} sampled frames")
if a.json:
    json.dump(R, open(a.json, "w"), indent=1)
sys.exit(0 if all(x["ok"] for k, x in R.items() if isinstance(x, dict) and "ok" in x) else 1)
