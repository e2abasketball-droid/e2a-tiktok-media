# E2A 3D lab, phase 3 — bundles (props) for the A/B/C comparison of the screener (O5) in the screen-and-roll lab play.
# Same play, cameras, light, court and play-time remaps for the three looks; only play.skel.O5.look changes:
#   A = procedural rig + capsule athlete (engine of d1d44b7: rig.ts / Athlete.tsx are untouched by the lab)
#   B = skeletal clip (5452, mirrored) on the capsule athlete, through the Pose adapter of skelclip.ts
#   C = skeletal clip on the deformable mesh (public/lab3d/e2a_bloqueador_screen_roll.glb)
# Silent (lab WAV), subtitles hidden. Usage (from template/):
#   python3 tactical/specs/_gen-screen-roll-lab.py && node --experimental-strip-types scripts/build-play.mts \
#       tactical/specs/screen-roll-lab.spec.json tactical/plays/screen-roll-lab.json
#   python3 scripts/screen-roll-lab-compare-bundle.py   -> out/lab3/<view>-<speed>-<look>.bundle.json
import copy, json, os, subprocess

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
play = json.load(open(os.path.join(T, "tactical/plays/screen-roll-lab.json")))
SILENCE = "tactical/_lab/silence.wav"
wav = os.path.join(T, "public", SILENCE)
os.makedirs(os.path.dirname(wav), exist_ok=True)
if not os.path.exists(wav):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "12", wav], check=True)

# vertical tactical view: screener, handler and both defenders in frame (as in phase 2, target moved with the new approach)
TACT = [{"at": 0, "rig": {"type": "orbit", "target": [3.3, 6.4, 0.9], "dist": 12.5, "pitch": 62, "yaw": -22, "fov": 40}}]
# three-quarter close-up of the screener, head to feet (follows the engine track of O5, so it is identical for A/B/C)
CLOSE = [{"at": 0, "rig": {"type": "orbit", "target": {"follow": "O5", "z": 1.0, "window": 0.25}, "dist": 5.6, "pitch": 82, "yaw": -40, "fov": 42}}]
SPEEDS = {
    # real speed: approach -> brake -> set -> hold -> open + pivot -> first strides (play 0.3–3.9 s)
    "real": {"len": 3.6, "remap": [[0, 0.3], [3.6, 3.9]]},
    # engine slow motion 0.4x over play 0.75–3.75 s (brake 0.9–1.4, set, open 2.45, pivot 2.5–3.2, first strides)
    "slow": {"len": 7.5, "remap": [[0, 0.75], [7.5, 3.75]]},
}
VIEWS = {"tactica": {"camera": TACT, "hide": []},
         "34": {"camera": CLOSE, "hide": ["O1", "O2", "O3", "O4", "X1", "X2", "X3", "X4", "X5"]}}
out_dir = os.path.join(T, "out/lab3")
os.makedirs(out_dir, exist_ok=True)
for vname, v in VIEWS.items():
    for sname, s in SPEEDS.items():
        for look in "ABC":
            p = copy.deepcopy(play)
            p["skel"]["O5"]["look"] = look
            n = 4
            words = [{"text": "lab", "start": round(0.1 + i * (s["len"] - 0.4) / n, 3), "end": round(0.3 + i * (s["len"] - 0.4) / n, 3)} for i in range(n)]
            ep = {
                "id": f"screen-roll-lab3-{vname}-{sname}-{look}", "title": f"Lab 3 — screener {look} ({vname}, {sname})", "fps": 30,
                "voice": SILENCE, "voiceMix": SILENCE, "tail": round(s["len"] - words[-1]["end"], 3), "words": words, "keywords": [],
                "subtitleHide": [[0, 99]], "plays": {"A": p},
                "shots": [{"id": "lab", "name": "lab", "at": 0, "play": "A", "remap": s["remap"], "camera": v["camera"], "hide": v["hide"]}],
            }
            out = os.path.join(out_dir, f"{vname}-{sname}-{look}.bundle.json")
            json.dump({"episode": ep}, open(out, "w"))
            print(out, s["len"], "s")
