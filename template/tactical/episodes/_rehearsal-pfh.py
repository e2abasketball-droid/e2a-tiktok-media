#!/usr/bin/env python3
"""Pistol Fake Handoff: hands rehearsal (real vs fake handoff) before the reel (brief sec. 6 / 7.3).
One episode where every shot is ONE play frame (S clock) seen from one camera, 2 render frames per shot, no overlays,
no titles, no subtitles. Render it as an image sequence, then tools: tactical/episodes/_sheet-pfh.py.
  python3 tactical/episodes/_rehearsal-pfh.py            -> tactical/episodes/pfh-rehearsal.json (+ words) + out/pfh/pfh-rehearsal.props.json
Cameras: C34 = close 3/4 from the inside-high (O2's chest, both pairs of hands, X2 behind the ball);
         LAT = lateral, perpendicular to the O1-O2 line (camera on the half-court side, low);
         GAME = the reel's high game view (same rig as the give/keep mirror)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__)); T = os.path.dirname(os.path.dirname(D))
orb = lambda tg, dist, pitch, yaw, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
S = lambda n: round(n / 30, 4)
CAMS = {"C34": orb([-5.3, 6.2, 1.0], 5.4, 60, -20, 40),
        "LAT": orb([-5.25, 6.45, 1.0], 6.0, 80, -4, 40),
        "GAME": orb([-5.0, 5.6, 0.7], 7.6, 54, -15, 44)}
FR = {"keep": [43, 47, 49, 51, 53, 54, 56, 59, 62, 66, 72],
      "give": [43, 45, 47, 49, 51, 53, 55, 58, 62]}
NF = 2


def shots():
    out, k = [], 0
    for br, play in (("keep", "A"), ("give", "B")):
        for cam in ("C34", "LAT", "GAME"):
            for f in FR[br]:
                out.append({"id": f"{br}-{cam}-S{f:03d}", "at": round(k * NF / 30, 4), "play": play, "branch": br,
                            "remap": [[0, S(f)], [NF / 30, S(f)]], "camera": [{"at": 0, "rig": CAMS[cam]}], "ov3": [], "screen": []})
                k += 1
    return out


if __name__ == "__main__":
    src = json.load(open(os.path.join(D, "pfh-a.json")))
    ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw")}
    ep.update({"id": "pfh-rehearsal", "title": "Pistol Fake Handoff rehearsal", "branches": {"keep": "A", "give": "B"},
               "env": "academy", "pinV2": True, "autoSfx": False, "shots": shots(), "subtitleHide": [[0, 999]]})
    ep.pop("music", None)
    json.dump(ep, open(os.path.join(D, "pfh-rehearsal.json"), "w"), indent=1)
    json.dump(json.load(open(os.path.join(D, "pfh-a.words.json"))), open(os.path.join(D, "pfh-rehearsal.words.json"), "w"))
    index = [{"frame": i * NF, "shot": s["id"]} for i, s in enumerate(ep["shots"])]
    os.makedirs(os.path.join(T, "out", "pfh"), exist_ok=True)
    json.dump(index, open(os.path.join(T, "out", "pfh", "pfh-rehearsal.index.json"), "w"), indent=0)
    print(len(index), "shots ->", len(index) * NF, "frames")
