"""Shared helpers for the e2a-video-editing-intelligence skill (ffmpeg/ffprobe wrappers, paths, ids).

Only the Python standard library, numpy and the ffmpeg/ffprobe binaries are used, so every script
runs in a Claude Code cloud container without installing anything.
"""
import hashlib
import json
import os
import re
import subprocess

SKILL_VERSION = "1.0.0"
ANALYSIS_SCHEMA = "e2a.analysis/1"
TECHNIQUE_SCHEMA = "e2a.technique/1"

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_DIR = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", ".."))
LIBRARY_DIR = os.environ.get("E2A_EDIT_LIBRARY", os.path.join(REPO_DIR, "editing-library"))
TEMPLATE_DIR = os.path.join(REPO_DIR, "template")

# Evidence levels used everywhere: what was measured, what was inferred from measures, what is a guess.
OBS, EST, HYP = "observacion", "estimacion", "hipotesis"
LEVELS = (OBS, EST, HYP)


class AnalysisError(Exception):
    """A reference that cannot be analysed (corrupt file, no video stream...). Callers record it and move on."""


def run(cmd, binary=False, check=True):
    p = subprocess.run(cmd, capture_output=True)
    if check and p.returncode != 0:
        raise AnalysisError(f"{os.path.basename(cmd[0])} failed: {p.stderr.decode(errors='ignore').strip()[-300:]}")
    if binary:
        return p.stdout
    return p.stdout.decode(errors="ignore") + p.stderr.decode(errors="ignore")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path):
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        raise AnalysisError("archivo vacío o inexistente")
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path])
    try:
        data = json.loads(out[out.index("{"):])
    except ValueError as e:
        raise AnalysisError("ffprobe no devolvió datos legibles") from e
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if v is None:
        raise AnalysisError("el archivo no contiene pista de vídeo")
    a = next((s for s in data["streams"] if s.get("codec_type") == "audio"), None)
    fps = _ratio(v.get("avg_frame_rate")) or _ratio(v.get("r_frame_rate")) or 0.0
    w, h = int(v["width"]), int(v["height"])
    dur = float(data["format"].get("duration") or v.get("duration") or 0)
    if dur <= 0:
        raise AnalysisError("duración desconocida o cero")
    g = _gcd(w, h)
    return {
        "duration_s": round(dur, 3),
        "fps": round(fps, 3),
        "width": w,
        "height": h,
        "aspect_ratio": f"{w // g}:{h // g}",
        "orientation": "vertical" if h > w else ("horizontal" if w > h else "cuadrado"),
        "video_codec": v.get("codec_name"),
        "pix_fmt": v.get("pix_fmt"),
        "has_audio": a is not None,
        "audio_codec": a.get("codec_name") if a else None,
        "audio_sample_rate": int(a["sample_rate"]) if a and a.get("sample_rate") else None,
        "size_bytes": int(data["format"].get("size", 0)),
    }


def _ratio(s):
    if not s or "/" not in s:
        return None
    n, d = s.split("/")
    try:
        return float(n) / float(d) if float(d) else None
    except ValueError:
        return None


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a or 1


def dump_json(obj, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False, sort_keys=False)
        f.write("\n")


def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def norm_word(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())
