#!/usr/bin/env python3
"""E2A edit-reference library: index (no duplicates) and technique cards (validated).

  python3 references/library.py seen <drive_id_or_url> [--sha256 H]  -> exit 0 if new, 10 if already processed
  python3 references/library.py next-id                              -> next free R-NNNN
  python3 references/library.py record <ref.json>                    -> add/replace one entry in index.json
  python3 references/library.py validate [card.json ...]             -> validate cards (all by default)
  python3 references/library.py next-tec                             -> next free tec-NNNN

Cards live in references/techniques/tec-NNNN.json. Every recipe value must be something the
Remotion Pro template already understands (template/src/pro/types.ts), so a card can never
break a render. A card that fails validation is ignored by production, never fatal.
"""
import json, os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "index.json")
TECH = os.path.join(HERE, "techniques")

STORY = {"record", "player", "tactical", "comparison", "curiosity"}
CATEGORIES = {"cortes", "ritmo", "animacion", "transicion", "efectos", "sonido", "subtitulos",
              "tipografia", "narrativa", "camara", "estructura"}
TRANSITION = {"cut", "whip", "punch", "flash", "zoom-through", "slide-up"}
CAMERA = {"push-in", "pull-out", "pan-left", "pan-right", "tilt-up", "tilt-down", "drift", "static"}
LAYOUT = {"center", "low", "high", "compact", "corner"}
HOOK = {"stat-slam", "photo-line", "split", "clock"}
ENDING = {"debate", "surprise", "fact", "emotion"}
SCENE_TYPES = {"media", "headline", "stat", "scoreboard", "timeline", "split", "court"}
SFX = {"whoosh", "whip", "impact", "riser", "tick", "bounce", "shutter", "buzzer", "bass_hit",
       "impact_big", "swish", "squeak", "crowd_cheer", "reverse_cymbal"}
TREATMENT = {"duotone", "tint", "blur"}
STATUS = {"propuesta", "probada", "activa", "descartada"}
NEW_PRIMITIVE_OK = "requiere_codigo"  # a card may flag that it needs a new Remotion option


def load_index():
    try:
        with open(INDEX) as f:
            return json.load(f)
    except Exception:
        return {"refs": []}


def save_index(ix):
    with open(INDEX, "w") as f:
        json.dump(ix, f, indent=1, ensure_ascii=False)
        f.write("\n")


def norm(key):
    key = key.strip()
    m = re.search(r"/d/([A-Za-z0-9_-]{20,})", key)
    if m:
        return m.group(1)
    return key.split("?")[0].rstrip("/") if key.startswith("http") else key


def seen(key, sha=None):
    k = norm(key)
    for r in load_index()["refs"]:
        if r.get("source_key") == k or (sha and r.get("sha256") == sha):
            return r
    return None


def next_id(prefix, existing):
    n = 0
    for e in existing:
        m = re.match(prefix + r"-(\d+)$", e or "")
        if m:
            n = max(n, int(m.group(1)))
    return f"{prefix}-{n + 1:04d}"


def validate_card(c):
    err = []
    req = ["id", "nombre", "categoria", "para", "receta", "comprobacion", "origen", "estado"]
    for k in req:
        if k not in c:
            err.append(f"falta {k}")
    if err:
        return err
    if not re.match(r"tec-\d{4}$", c["id"]):
        err.append("id debe ser tec-NNNN")
    if c["categoria"] not in CATEGORIES:
        err.append(f"categoria desconocida: {c['categoria']}")
    for s in c.get("para", []) + c.get("evitar_en", []):
        if s not in STORY:
            err.append(f"tipo de historia desconocido: {s}")
    if c["estado"] not in STATUS:
        err.append(f"estado desconocido: {c['estado']}")
    r = c["receta"]
    if not isinstance(r, dict) or not r:
        err.append("receta vacía")
        return err
    sc = r.get("scene", {})
    checks = [("transition", TRANSITION), ("camera", CAMERA), ("layout", LAYOUT), ("type", SCENE_TYPES)]
    for key, allowed in checks:
        v = sc.get(key)
        vals = v if isinstance(v, list) else ([v] if v is not None else [])
        for x in vals:
            if x not in allowed:
                err.append(f"scene.{key} no soportado por Remotion Pro: {x}")
    if "bg_treatment" in sc and sc["bg_treatment"] not in TREATMENT:
        err.append(f"scene.bg_treatment no soportado: {sc['bg_treatment']}")
    ep = r.get("episode", {})
    if "hook" in ep and ep["hook"] not in HOOK:
        err.append(f"episode.hook no soportado: {ep['hook']}")
    if "ending" in ep and ep["ending"] not in ENDING:
        err.append(f"episode.ending no soportado: {ep['ending']}")
    for s in r.get("sfx", []):
        if s not in SFX:
            err.append(f"sfx no soportado: {s}")
    if r.get(NEW_PRIMITIVE_OK) and c["estado"] == "activa":
        err.append("una técnica que requiere código nuevo no puede estar activa")
    if len(c["comprobacion"]) < 10:
        err.append("comprobacion demasiado vaga")
    o = c["origen"]
    if re.search(r"https?://", str(o)) and "privad" not in str(o).lower():
        pass  # links are allowed: they point at the reference, nothing is copied
    return err


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "seen":
        sha = sys.argv[sys.argv.index("--sha256") + 1] if "--sha256" in sys.argv else None
        r = seen(sys.argv[2], sha)
        print(json.dumps(r or {"new": True}, ensure_ascii=False))
        sys.exit(10 if r else 0)
    if cmd == "next-id":
        print(next_id("R", [r.get("ref_id") for r in load_index()["refs"]]))
        return
    if cmd == "next-tec":
        print(next_id("tec", [os.path.basename(p)[:-5] for p in glob.glob(os.path.join(TECH, "tec-*.json"))]))
        return
    if cmd == "record":
        with open(sys.argv[2]) as f:
            entry = json.load(f)
        for k in ("ref_id", "source_key", "status"):
            if k not in entry:
                sys.exit(f"falta {k}")
        entry["source_key"] = norm(entry["source_key"])
        if entry["status"] not in {"analyzed", "failed"}:
            sys.exit("status debe ser analyzed o failed")
        ix = load_index()
        ix["refs"] = [r for r in ix["refs"] if r.get("ref_id") != entry["ref_id"]] + [entry]
        save_index(ix)
        print("ok")
        return
    if cmd == "validate":
        files = sys.argv[2:] or sorted(glob.glob(os.path.join(TECH, "tec-*.json")))
        bad = 0
        for p in files:
            try:
                with open(p) as f:
                    c = json.load(f)
                e = validate_card(c)
            except Exception as ex:
                e = [f"JSON inválido: {ex}"]
            if e:
                bad += 1
                print(f"{os.path.basename(p)}: " + "; ".join(e))
        print(f"{len(files) - bad}/{len(files)} fichas válidas")
        sys.exit(1 if bad else 0)
    sys.exit(f"comando desconocido: {cmd}")


if __name__ == "__main__":
    main()
