# E2A 3D lab — render bundles (props) for the screen-and-roll lab play, WITHOUT narration:
#   * a silent WAV (ffmpeg, git-ignored) instead of a voice, placeholder words with the subtitles hidden;
#   * one fixed three-quarter camera that keeps the screener (O5) and the handler (O1) in the same vertical frame;
#   * two cuts of the SAME play and camera: real speed, and an engine slow motion (play-time remap at 0.4x)
#     centred on the plant, the weight transfer and the first step of the roll.
# Usage (from template/):
#   python3 tactical/specs/_gen-screen-roll-lab.py && node --experimental-strip-types scripts/build-play.mts \
#       tactical/specs/screen-roll-lab.spec.json tactical/plays/screen-roll-lab.json
#   python3 scripts/screen-roll-lab-bundle.py            -> out/lab/screen-roll-lab-{real,slow}.bundle.json
import json, os, subprocess

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
play = json.load(open(os.path.join(T, "tactical/plays/screen-roll-lab.json")))
SILENCE = "tactical/_lab/silence.wav"
wav = os.path.join(T, "public", SILENCE)
os.makedirs(os.path.dirname(wav), exist_ok=True)
if not os.path.exists(wav):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "12", wav], check=True)

CAMERA = [{"at": 0, "rig": {"type": "orbit", "target": [3.7, 6.5, 0.9], "dist": 12.0, "pitch": 62, "yaw": -22, "fov": 40}}]
# close-up on the screener alone (the references are solo takes; front three-quarter as in 5449) for the reference-vs-render sheet
CLOSE = [{"at": 0, "rig": {"type": "orbit", "target": {"follow": "O5", "z": 1.0, "window": 0.2}, "dist": 5.4, "pitch": 82, "yaw": -55, "fov": 42}}]
CUTS = {
    # real speed: approach -> plant -> hold -> open step -> roll -> catch (play 0.3–4.6 s = 4.3 s of video)
    "real": {"len": 4.3, "remap": [[0, 0.3], [4.3, 4.6]]},
    # engine slow motion 0.4x over play 1.15–3.35 s (plant 1.42, hold, open step 2.45, first steps 2.75–3.2)
    "slow": {"len": 5.5, "remap": [[0, 1.15], [5.5, 3.35]]},
    # close-up of the screener at real speed (play 0.3–4.6 s), only for stills
    "close": {"len": 4.3, "remap": [[0, 0.3], [4.3, 4.6]], "camera": CLOSE,
              "hide": ["O1", "O2", "O3", "O4", "X1", "X2", "X3", "X4", "X5"]},
}
# character views of the screener (heading ≈ -10°, facing X1): front, three-quarter, profile (his left), back.
# Frozen play time: 2.0 s = screen crouch (knee flexion), 2.62 s = hip/chest twist of the roll.
VIEWS = {"front": -100, "34": -55, "profile": -10, "back": 80}
for vname, yaw in VIEWS.items():
    for pt in (2.0, 2.62):
        CUTS[f"view-{vname}-{pt}"] = {"len": 1.0, "remap": [[0, pt], [1.0, pt]], "hide": ["O1", "O2", "O3", "O4", "X1", "X2", "X3", "X4", "X5"],
                                      "camera": [{"at": 0, "rig": {"type": "orbit", "target": [4.45, 7.65, 1.0], "dist": 4.6, "pitch": 84, "yaw": yaw, "fov": 40}}]}
os.makedirs(os.path.join(T, "out/lab"), exist_ok=True)
for name, c in CUTS.items():
    n = 4
    words = [{"text": "lab", "start": round(0.1 + i * (c["len"] - 0.4) / n, 3), "end": round(0.3 + i * (c["len"] - 0.4) / n, 3)} for i in range(n)]
    tail = round(c["len"] - words[-1]["end"], 3)
    ep = {
        "id": f"screen-roll-lab-{name}", "title": f"Lab — screen and roll ({name})", "fps": 30,
        "voice": SILENCE, "voiceMix": SILENCE, "tail": tail, "words": words, "keywords": [],
        "subtitleHide": [[0, 99]], "plays": {"A": play},
        "shots": [{"id": "lab", "name": "lab", "at": 0, "play": "A", "remap": c["remap"], "camera": c.get("camera", CAMERA), "hide": c.get("hide", [])}],
    }
    out = os.path.join(T, f"out/lab/screen-roll-lab-{name}.bundle.json")
    json.dump({"episode": ep}, open(out, "w"))
    print(out, f"{c['len']} s")
