"""What the Remotion Pro template accepts, read from template/src/pro/types.ts so the technique
validator never drifts from the code. Falls back to the values known at skill v1.0.0 if the file
cannot be read (for example when the library is used outside the repository)."""
import os
import re

from common import TEMPLATE_DIR

TYPES_TS = os.path.join(TEMPLATE_DIR, "src", "pro", "types.ts")

FALLBACK = {
    "StoryType": ["record", "player", "tactical", "comparison", "curiosity"],
    "CameraMove": ["push-in", "pull-out", "pan-left", "pan-right", "tilt-up", "tilt-down", "drift", "static"],
    "Transition": ["cut", "whip", "punch", "flash", "zoom-through", "slide-up"],
    "SfxName": ["whoosh", "whip", "impact", "riser", "tick", "bounce", "shutter", "buzzer", "bass_hit", "impact_big",
                "swish", "squeak", "crowd_cheer", "reverse_cymbal"],
    "Backdrop": ["arena", "navy", "spotlight", "archive"],
    "Layout": ["center", "low", "high", "compact", "corner"],
    "SceneType": ["media", "headline", "stat", "scoreboard", "timeline", "split", "court"],
    "Treatment": ["duotone", "tint", "blur"],
    "Hook": ["stat-slam", "photo-line", "split", "clock"],
    "Ending": ["debate", "surprise", "fact", "emotion"],
    "Captions": ["low", "high"],
}


def _union(src, name):
    m = re.search(rf"export type {name}\s*=\s*([^;]+);", src)
    return re.findall(r"'([^']+)'", m.group(1)) if m else None


def load():
    opts = {k: list(v) for k, v in FALLBACK.items()}
    try:
        with open(TYPES_TS) as f:
            src = f.read()
    except OSError:
        opts["_source"] = "fallback"
        return opts
    for name in ("StoryType", "CameraMove", "Transition", "SfxName", "Backdrop", "Layout"):
        vals = _union(src, name)
        if vals:
            opts[name] = vals
    types = re.findall(r"type:\s*'([a-z]+)'", src)
    if types:
        opts["SceneType"] = sorted(set(types), key=types.index)
    m = re.search(r"treatment\?:\s*([^}]+)\}", src)
    if m:
        opts["Treatment"] = re.findall(r"'([^']+)'", m.group(1))
    for key, field in (("Hook", "hook"), ("Ending", "ending")):
        m = re.search(rf"\n\s*{field}\?:\s*([^;]+);", src)
        if m:
            opts[key] = re.findall(r"'([^']+)'", m.group(1))
    m = re.search(r"captions\?:\s*([^;]+);", src)
    if m:
        opts["Captions"] = re.findall(r"'([^']+)'", m.group(1))
    opts["_source"] = os.path.relpath(TYPES_TS, os.path.dirname(TEMPLATE_DIR))
    return opts


# Edit fields APPLY may change in a scene (never the script: words, lines, labels, values, media, sources)
SCENE_EDIT_FIELDS = {"transition": "Transition", "camera": "CameraMove", "layout": "Layout", "backdrop": "Backdrop",
                     "captions": "Captions", "bg_treatment": "Treatment", "sfxTransition": None}
EPISODE_EDIT_FIELDS = {"hook": "Hook", "ending": "Ending"}
