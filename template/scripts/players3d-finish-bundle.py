# E2A 3D (2026-11-19) — short sample of the DEFAULT finish (players + graphics) on the screen-and-roll lab play, built
# like a normal episode (anchored to words, remaps, cameras, world graphics, titles, subtitles) WITHOUT any character /
# style field: what a new episode inherits. Silent lab voice (no ElevenLabs), no SFX.
#   python3 scripts/players3d-finish-bundle.py out/lab4/finish.bundle.json
import json, os, sys
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
play = json.load(open(os.path.join(T, "tactical/plays/screen-roll-lab.json")))
play.pop("skel", None)  # nothing opt-in: the clip is chosen by the engine from the actions
SILENCE = "tactical/_lab/silence.wav"
W = lambda t, a, b: {"text": t, "start": a, "end": b}
words = [W("The", 0.2, 0.3), W("big", 0.32, 0.5), W("sets", 0.52, 0.75), W("the", 0.77, 0.85), W("screen.", 0.88, 1.35),
         W("He", 3.0, 3.1), W("opens,", 3.12, 3.5), W("pivots", 3.7, 4.1), W("and", 4.15, 4.25), W("rolls.", 4.3, 4.85),
         W("Pass,", 6.4, 6.75), W("layup.", 6.9, 7.45)]
TACT = {"type": "orbit", "target": [3.0, 6.0, 0.9], "dist": 12.5, "pitch": 58, "yaw": -22, "fov": 40}
ep = {
    "id": "players3d-finish", "title": "E2A default finish sample (players3d e2a-player-v1)", "fps": 30,
    "voice": SILENCE, "voiceMix": SILENCE, "tail": 1.0, "words": words, "keywords": ["screen.", "rolls.", "layup."], "pinV2": True,
    "autoSfx": False, "plays": {"A": play},
    "shots": [
        {"id": "set", "name": "approach and screen", "at": 0, "play": "A", "remap": [[0, 0.35], ["He", 3.35]],
         "camera": [{"at": 0, "rig": TACT}],
         "ov3": [{"type": "ring", "player": "O1", "from": 0.2, "to": "He"},
                 {"type": "screen", "player": "O5", "n": 1, "from": "screen.", "to": "He"},
                 {"type": "ring", "player": "X1", "color": "#B8322A", "from": "screen.>", "to": "He"}],
         "screen": [{"type": "title", "lines": ["SCREEN", "AND ROLL"], "gold": [0], "from": 0.15, "to": "He-0.1", "y": 262, "size": 96}]},
        {"id": "pivot", "name": "open, pivot, roll (0.4x)", "at": "He", "play": "A", "remap": [[0, 2.3], ["Pass,", 3.6]],
         "camera": [{"at": 0, "rig": {"type": "orbit", "target": {"follow": "O5", "z": 1.0, "window": 0.25}, "dist": 6.2, "pitch": 76, "yaw": -40, "fov": 42}}],
         "ov3": [{"type": "route", "player": "O5", "t0": 2.45, "t1": 3.9, "trail": True, "from": "opens,", "to": "@end"},
                 {"type": "ring", "player": "O5", "from": "pivots", "to": "@end"}],
         "screen": [{"type": "pin", "player": "O5", "text": "PIVOT", "tone": "gold", "from": "pivots", "to": "rolls."},
                    {"type": "pin", "player": "O5", "text": "ROLL", "tone": "gold", "from": "rolls.", "to": "@end"},
                    {"type": "stamp", "text": "0.4x", "tone": "white", "from": "He", "to": "@end", "y": 300}]},
        {"id": "finish", "name": "pass and layup", "at": "Pass,", "play": "A", "remap": [[0, 3.6], ["@end", 5.0]],
         "camera": [{"at": 0, "rig": TACT}],
         "ov3": [{"type": "passLane", "src": "O1", "dst": "O5", "from": 0, "to": "layup."},
                 {"type": "ring", "player": "O5", "from": 0, "to": "@end"}],
         "screen": [{"type": "title", "lines": ["OPEN", "AT THE RIM"], "gold": [1], "from": "layup.", "to": "@end", "y": 262, "size": 96}]},
    ],
}
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(T, "out/lab4/finish.bundle.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"episode": ep}, open(out, "w"))
print(out)
