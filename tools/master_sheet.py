#!/usr/bin/env python3
"""E2A V4 common tactical master: ONE versioned sheet per play revision that ties the social 9:16 cut and the clean
Course3D 16:9 clip to the same play id + play sha + engine hash (owner brief 2026-11-14 16:28Z).

  python3 tools/master_sheet.py <play_id> --social <9x16.mp4> [--episode <episode.json>] [--course <16x9.mp4> --from 0 --to 6.6]
      [--out template/tactical/sheets]

The sheet is named <play_id>@<play_sha[:8]>.json, so a changed play gets a new sheet and an old sheet stays valid
for the media it lists. `check` recomputes every hash and fails when a file or the play changed.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tactical_studio as ts  # noqa: E402

PLAYS = os.path.join(ts.TEMPLATE, "tactical", "plays")
SHEETS = os.path.join(ts.TEMPLATE, "tactical", "sheets")
PROFILES = {"social": {"id": "tactical3dv2-social", "width": 1080, "height": 1920, "layers": "voice, subtitles, pins, titles, music"},
            "course": {"id": "course3d-0.2", "width": 1280, "height": 720, "layers": "court+athletes+ball only, mirrored x"}}


def probe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                          "-of", "json", p], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    n, d = map(int, v["r_frame_rate"].split("/"))
    return {"width": v["width"], "height": v["height"], "fps": round(n / d, 3), "duration_s": round(float(j["format"]["duration"]), 3),
            "audio": any(s["codec_type"] == "audio" for s in j["streams"])}


def media(p, profile):
    m = {"file": os.path.basename(p), "sha256": ts.sha256(p), **probe(p), "profile": PROFILES[profile]["id"]}
    want = PROFILES[profile]
    m["profile_ok"] = (m["width"], m["height"]) == (want["width"], want["height"])
    return m


def make(play_id, social=None, episode=None, course=None, seg=None, out=SHEETS):
    pf = os.path.join(PLAYS, f"{play_id}.json")
    psha = ts.sha256(pf)
    sheet = {"schema": "e2a-tactical-master/1", "play_id": play_id, "play_sha256": psha,
             "play_file": os.path.relpath(pf, ts.ROOT), "engine_sha256": ts.engine_hash(), "profiles": PROFILES, "outputs": {}}
    if episode:
        sheet["episode"] = {"file": os.path.relpath(os.path.abspath(episode), ts.ROOT), "sha256": ts.sha256(episode)}
    if social:
        sheet["outputs"]["social_9x16"] = media(social, "social")
    if course:
        sheet["outputs"]["course_16x9"] = {**media(course, "course"), "segment": seg}
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"{play_id}@{psha[:8]}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sheet, f, indent=1)
    return path, sheet


def check(sheet_path, media_dir):
    s = json.load(open(sheet_path))
    bad = []
    if ts.sha256(os.path.join(ts.ROOT, s["play_file"])) != s["play_sha256"]:
        bad.append("play changed since the sheet: make a new sheet")
    for k, m in s["outputs"].items():
        p = os.path.join(media_dir, m["file"])
        if not os.path.exists(p) or ts.sha256(p) != m["sha256"]:
            bad.append(f"{k}: {m['file']} missing or changed")
        if not m.get("profile_ok"):
            bad.append(f"{k}: not the {m['profile']} size")
    return {"ok": not bad, "problems": bad}


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("make"); p.add_argument("play_id"); p.add_argument("--social"); p.add_argument("--episode")
    p.add_argument("--course"); p.add_argument("--from", dest="frm", type=float, default=0.0); p.add_argument("--to", type=float)
    p.add_argument("--out", default=SHEETS)
    p = sp.add_parser("check"); p.add_argument("sheet"); p.add_argument("--media", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "make":
        path, s = make(a.play_id, a.social, a.episode, a.course, {"from": a.frm, "to": a.to}, a.out)
        print(path)
        print(json.dumps(s, indent=1))
    else:
        r = check(a.sheet, a.media)
        print(json.dumps(r, indent=1))
        return 0 if r["ok"] else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
