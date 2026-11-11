#!/usr/bin/env python3
"""Validate analysis.json files (schema e2a.analysis/1) before they enter the library.

  python3 validate_analysis.py <analysis.json> [...]     exit 0 = all valid, 1 = some invalid

Checks the structure (required sections and types), then the meaning: timestamps inside the
video, cuts sorted, shots covering the whole video without gaps, every measured block tagged with
an evidence level, sha256 present, frames kept as relative paths, and the content hash matching
(so a hand-edited analysis is detected).
"""
import hashlib
import json
import sys

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ANALYSIS_SCHEMA, LEVELS  # noqa: E402

REQUIRED = {
    "schema_version": str, "source": dict, "technical": dict, "editing": dict, "shots": list,
    "transitions": dict, "camera": dict, "rhythm": dict, "structure": dict, "text": dict,
    "overlays": dict, "color": dict, "sync": dict, "retention": dict, "frames": dict, "meta": dict,
}
LEVELLED = ["technical", "editing", "transitions", "camera", "rhythm", "text", "overlays", "color", "sync", "retention"]


def _levels(obj, path, errs):
    """Every dict that declares a level must use one of the three known ones."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("nivel", "lectura_nivel", "aparicion_nivel", "estetica_nivel") and v not in LEVELS:
                errs.append(f"{path}.{k}: nivel desconocido {v!r}")
            _levels(v, f"{path}.{k}", errs)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _levels(v, f"{path}[{i}]", errs)


def validate(a):
    errs = []
    if not isinstance(a, dict):
        return ["no es un objeto JSON"]
    for k, t in REQUIRED.items():
        if k not in a:
            errs.append(f"falta la sección {k}")
        elif not isinstance(a[k], t):
            errs.append(f"{k} debe ser {t.__name__}")
    if errs:
        return errs
    if a["schema_version"] != ANALYSIS_SCHEMA:
        errs.append(f"schema_version {a['schema_version']} != {ANALYSIS_SCHEMA}")
    for k in LEVELLED:
        if a[k].get("nivel") not in LEVELS:
            errs.append(f"{k}.nivel ausente o desconocido")
    _levels(a, "$", errs)
    t = a["technical"]
    for k in ("duration_s", "fps", "width", "height"):
        if not isinstance(t.get(k), (int, float)) or t[k] <= 0:
            errs.append(f"technical.{k} inválido")
    if errs:
        return errs
    dur = t["duration_s"]
    s = a["source"]
    if not (isinstance(s.get("sha256"), str) and len(s["sha256"]) == 64):
        errs.append("source.sha256 ausente")
    if s.get("rights") not in ("propio", "tercero"):
        errs.append("source.rights debe ser propio o tercero")
    cuts = a["editing"].get("cuts", [])
    if cuts != sorted(cuts):
        errs.append("editing.cuts no está ordenado")
    if any(c <= 0 or c >= dur for c in cuts):
        errs.append("editing.cuts tiene tiempos fuera del vídeo")
    shots = a["shots"]
    if not shots:
        errs.append("shots vacío")
    else:
        if abs(shots[0]["inicio"]) > 0.01 or abs(shots[-1]["fin"] - dur) > 0.05:
            errs.append("los planos no cubren el vídeo de principio a fin")
        for p, q in zip(shots, shots[1:]):
            if abs(p["fin"] - q["inicio"]) > 0.01:
                errs.append(f"hueco o solape entre planos {p['n']} y {q['n']}")
        if len(shots) != len(cuts) + 1:
            errs.append("número de planos != cortes + 1")
        for sh in shots:
            if sh["duracion_s"] <= 0:
                errs.append(f"plano {sh['n']} con duración no positiva")
            if "movimiento" not in sh.get("camara", {}):
                errs.append(f"plano {sh['n']} sin estimación de cámara")
    st = a["structure"]
    for k in ("gancho", "desarrollo", "climax", "desenlace"):
        seg = st.get(k)
        if not seg or not (0 <= seg["inicio"] <= seg["fin"] <= dur + 0.01):
            errs.append(f"structure.{k} fuera del vídeo o ausente")
    for f in a["frames"].get("items", []):
        if os.path.isabs(f["file"]):
            errs.append("frames con ruta absoluta (deben ser relativas a la carpeta del análisis)")
            break
        if not (0 <= f["t"] <= dur):
            errs.append(f"fotograma fuera del vídeo: {f['t']}")
    au = a.get("audio")
    if t.get("has_audio") and au is None:
        errs.append("el vídeo tiene audio pero no hay sección audio")
    if au and "error" not in au:
        for a_, b_ in au["silences"]["items"]:
            if not (0 <= a_ <= b_ <= dur + 0.1):
                errs.append(f"silencio fuera del vídeo: {a_}-{b_}")
    m = a["meta"]
    body = {k: v for k, v in a.items() if k != "meta"}
    h = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if m.get("content_sha256") != h:
        errs.append("content_sha256 no coincide: el análisis se ha editado a mano o está incompleto")
    return errs


def main():
    files = sys.argv[1:]
    if not files:
        print(__doc__)
        sys.exit(1)
    bad = 0
    for p in files:
        try:
            with open(p) as f:
                e = validate(json.load(f))
        except (OSError, ValueError) as ex:
            e = [f"JSON ilegible: {ex}"]
        print(f"{p}: " + ("OK" if not e else "; ".join(e[:12])))
        bad += bool(e)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
