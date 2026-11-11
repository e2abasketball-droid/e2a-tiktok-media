#!/usr/bin/env python3
"""Persistent, versioned technique library (editing-library/ at the repository root).

  library.py seen <drive_id|url|name> [--sha256 H]      exit 0 = new, 10 = already in the library
  library.py next-id | next-tec                          next free R-NNNN / tec-NNNN
  library.py add <analysis_dir> [--source-key K]         store analysis.json + report.md, index it (no duplicates)
  library.py fail <R-id> <source_key> "<reason>" [--title T] [--kind file|link]
  library.py propose <analysis.json> [--write]           draft technique cards from the measures (estado propuesta)
  library.py validate [card.json ...]                    validate cards against the schema and Remotion Pro options
  library.py list                                        techniques with status and use count
  library.py status <tec-id> <propuesta|probada|activa|descartada> "<why>"
  library.py bump "<change>"                             new library version + CHANGELOG line

The library never stores videos, frames or audio: only measures (analysis.json), reports and
technique cards written in our own words. Frames of third-party videos stay in scratch folders.
Override the location with E2A_EDIT_LIBRARY (the tests do).
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import remotion_options  # noqa: E402
from common import LIBRARY_DIR, TECHNIQUE_SCHEMA, dump_json, load_json  # noqa: E402
from validate_analysis import validate as validate_analysis  # noqa: E402

CATEGORIES = ["cortes", "ritmo", "animacion", "transicion", "efectos", "sonido", "subtitulos", "tipografia",
              "narrativa", "camara", "estructura", "color", "composicion"]
STATUS = ["propuesta", "probada", "activa", "descartada"]
POSITIONS = ["primera", "segunda", "ultima", "penultima", "climax", "mas_larga", "cualquiera"]
OPS = {"<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, ">": lambda a, b: a > b,
       "==": lambda a, b: a == b, "!=": lambda a, b: a != b}
PLAN_METRICS = ["plan.escena_s", "plan.mediana_escenas_s", "plan.max_escena_s", "plan.escenas_n", "plan.duracion_s",
                "plan.sfx_n"]


def lib(*p):
    return os.path.join(os.environ.get("E2A_EDIT_LIBRARY", LIBRARY_DIR), *p)


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_index():
    return load_json(lib("index.json"), {"refs": []})


def save_index(ix):
    ix["refs"].sort(key=lambda r: r.get("ref_id", ""))
    dump_json(ix, lib("index.json"))


def norm_key(key):
    key = (key or "").strip()
    m = re.search(r"/d/([A-Za-z0-9_-]{20,})", key) or re.search(r"[?&]id=([A-Za-z0-9_-]{20,})", key)
    if m:
        return m.group(1)
    return key.split("?")[0].rstrip("/") if key.startswith("http") else key


def seen(key, sha=None):
    k = norm_key(key)
    for r in load_index()["refs"]:
        if (k and r.get("source_key") == k) or (sha and r.get("sha256") == sha):
            return r
    return None


def next_id(prefix, existing):
    n = 0
    for e in existing:
        m = re.match(prefix + r"-(\d+)$", e or "")
        if m:
            n = max(n, int(m.group(1)))
    return f"{prefix}-{n + 1:04d}"


def card_files():
    return sorted(glob.glob(lib("techniques", "tec-*.json")))


# ----------------------------------------------------------------------------- validation
def validate_card(c, opts=None):
    opts = opts or remotion_options.load()
    err = []
    req = ["schema", "id", "version", "nombre", "categoria", "descripcion", "para", "aplicar_a", "receta",
           "comprobacion", "evidencia", "origen", "estado"]
    for k in req:
        if k not in c:
            err.append(f"falta {k}")
    if err:
        return err
    if c["schema"] != TECHNIQUE_SCHEMA:
        err.append(f"schema debe ser {TECHNIQUE_SCHEMA}")
    if not re.match(r"tec-\d{4}$", str(c["id"])):
        err.append("id debe ser tec-NNNN")
    if not isinstance(c["version"], int) or c["version"] < 1:
        err.append("version debe ser un entero >= 1")
    if c["categoria"] not in CATEGORIES:
        err.append(f"categoria desconocida: {c['categoria']}")
    for s in list(c.get("para", [])) + list(c.get("evitar_en", [])):
        if s not in opts["StoryType"]:
            err.append(f"tipo de historia desconocido: {s}")
    if set(c.get("para", [])) & set(c.get("evitar_en", [])):
        err.append("un tipo de historia no puede estar en para y en evitar_en")
    if c["estado"] not in STATUS:
        err.append(f"estado desconocido: {c['estado']}")
    tgt = c["aplicar_a"]
    if not isinstance(tgt, dict):
        err.append("aplicar_a debe ser un objeto")
    else:
        if tgt.get("scene_type") is not None and tgt["scene_type"] not in opts["SceneType"]:
            err.append(f"aplicar_a.scene_type no existe en Remotion Pro: {tgt['scene_type']}")
        if tgt.get("posicion", "cualquiera") not in POSITIONS:
            err.append(f"aplicar_a.posicion desconocida: {tgt.get('posicion')}")
    r = c["receta"]
    if not isinstance(r, dict) or not r:
        err.append("receta vacía")
        return err
    unknown = set(r) - {"scene", "episode", "sfx", "music"}
    if unknown:
        err.append(f"receta con claves desconocidas: {sorted(unknown)}")
    for key, val in (r.get("scene") or {}).items():
        if key not in remotion_options.SCENE_EDIT_FIELDS:
            err.append(f"scene.{key} no es un campo de edición de Remotion Pro (los campos del guion no se tocan)")
            continue
        enum = remotion_options.SCENE_EDIT_FIELDS[key]
        if enum is None:
            if not isinstance(val, bool):
                err.append(f"scene.{key} debe ser true/false")
        elif val not in opts[enum]:
            err.append(f"scene.{key} no soportado por Remotion Pro: {val}")
    for key, val in (r.get("episode") or {}).items():
        enum = remotion_options.EPISODE_EDIT_FIELDS.get(key)
        if enum is None:
            err.append(f"episode.{key} no es un campo de edición")
        elif val not in opts[enum]:
            err.append(f"episode.{key} no soportado: {val}")
    for s in r.get("sfx", []):
        if s not in opts["SfxName"]:
            err.append(f"sfx no soportado: {s}")
    for key in (r.get("music") or {}):
        if key not in ("payoff_en_esta_escena", "drop_en_esta_escena"):
            err.append(f"music.{key} no soportado (usa payoff_en_esta_escena o drop_en_esta_escena)")
    if c.get("requiere_codigo") and c["estado"] == "activa":
        err.append("una técnica que requiere código nuevo no puede estar activa")
    comp = c["comprobacion"]
    if not isinstance(comp, dict) or len(comp.get("texto", "")) < 10:
        err.append("comprobacion.texto ausente o demasiado vago")
    else:
        if not comp.get("reglas"):
            err.append("comprobacion.reglas vacío: hace falta al menos una regla medible")
        for rule in comp.get("reglas", []):
            if rule.get("op") not in OPS or not isinstance(rule.get("valor"), (int, float, bool)):
                err.append(f"regla mal formada: {rule}")
            elif not (rule.get("metrica", "").startswith("plan.") and rule["metrica"] in PLAN_METRICS
                      or re.match(r"^(editing|retention|rhythm|structure|audio|color|text|technical)\.[a-z0-9_.]+$",
                                  rule.get("metrica", ""))):
                err.append(f"métrica desconocida: {rule.get('metrica')}")
    if not isinstance(c["evidencia"], list) or not c["evidencia"]:
        err.append("evidencia vacía: cada técnica nace de al menos una referencia medida")
    else:
        for ev in c["evidencia"]:
            if ev.get("nivel") not in ("observacion", "estimacion", "hipotesis"):
                err.append("evidencia sin nivel válido")
    return err


# ----------------------------------------------------------------------------- proposals from measures
def propose(a):
    """Draft cards from an analysis. Each draft is only a starting point (estado propuesta): Claude or a
    person must confirm it on the contact sheet before it is used, and rewrite the description."""
    ref = a.get("ref_id") or "R-????"
    out = []
    e, rt, st, sb = a["editing"], a["retention"], a["structure"], a["text"]["subtitulos"]
    au = a.get("audio") or {}

    def card(nombre, cat, desc, target, receta, texto, reglas, medidas, nivel="observacion", para=None, evitar=None):
        out.append({"schema": TECHNIQUE_SCHEMA, "id": None, "version": 1, "nombre": nombre, "categoria": cat,
                    "descripcion": desc, "para": para or ["record", "player", "comparison", "curiosity"],
                    "evitar_en": evitar or [], "aplicar_a": target, "receta": receta,
                    "comprobacion": {"texto": texto, "reglas": reglas},
                    "evidencia": [{"ref_id": ref, "medidas": medidas, "nivel": nivel}],
                    "origen": f"{ref} ({a['source']['rights']})", "estado": "propuesta", "requiere_codigo": False,
                    "creada": now()[:10], "actualizada": now()[:10]})

    longest = max(a["shots"], key=lambda s: s["duracion_s"]) if a["shots"] else None
    if longest and e["plano_mediano_s"] and longest["duracion_s"] >= 2.5 * e["plano_mediano_s"] and longest["duracion_s"] >= 4:
        card("Plano largo de énfasis entre planos cortos", "ritmo",
             f"Un plano de {longest['duracion_s']} s (desde {longest['inicio']} s) contrasta con una mediana de "
             f"{e['plano_mediano_s']} s: la pausa marca el dato central.",
             {"scene_type": "stat", "posicion": "mas_larga"}, {"scene": {"camera": "push-in"}},
             "la escena del dato dura entre 3 y 6 s y la mediana del resto queda por debajo de 3 s",
             [{"metrica": "plan.escena_s", "op": ">=", "valor": 3}, {"metrica": "plan.escena_s", "op": "<=", "valor": 6},
              {"metrica": "plan.mediana_escenas_s", "op": "<=", "valor": 3}],
             {"plano_largo_s": longest["duracion_s"], "mediana_s": e["plano_mediano_s"]})
    if rt["primer_corte_s"] is not None and rt["primer_corte_s"] <= 1.0 and st["gancho"]["texto_antes_de_1s"]:
        card("Gancho legible sin sonido con cambio antes de 1 s", "estructura",
             f"Texto en pantalla desde el primer segundo y primer cambio de imagen a {rt['primer_corte_s']} s.",
             {"posicion": "primera"}, {"scene": {"transition": "cut", "camera": "push-in"}},
             "la primera escena dura 2.5 s o menos y el primer corte del render llega antes de 2.5 s",
             [{"metrica": "plan.escena_s", "op": "<=", "valor": 2.5}, {"metrica": "retention.primer_corte_s", "op": "<=", "valor": 2.5}],
             {"primer_corte_s": rt["primer_corte_s"], "texto_antes_de_1s": True})
    sil = st["desenlace"].get("silencio_final_s")
    if sil and sil >= 1.0:
        card("Cierre en silencio tras la última frase", "sonido",
             f"El vídeo termina con {sil} s de silencio: el final respira y no compite con la música.",
             {"posicion": "ultima"}, {"scene": {"camera": "static", "transition": "cut"}, "music": {"payoff_en_esta_escena": True}},
             "el render termina con al menos 0.8 s por debajo de −35 dB",
             [{"metrica": "structure.desenlace.silencio_final_s", "op": ">=", "valor": 0.8}],
             {"silencio_final_s": sil})
    if sb.get("probable") and sb.get("palabras_resaltadas_en_color"):
        card("Subtítulo con palabra clave en color", "subtitulos",
             f"Subtítulos blancos a {sb['posicion_y_pct']}% de la altura con palabras destacadas en color; cambian cada "
             f"{sb['intervalo_mediano_s']} s.", {"posicion": "cualquiera"}, {"scene": {"captions": "low"}},
             "el render muestra subtítulos en la franja inferior en al menos el 60% de los fotogramas",
             [{"metrica": "text.texto_en_pantalla_pct", "op": ">=", "valor": 0.6}],
             {"posicion_y_pct": sb["posicion_y_pct"], "intervalo_mediano_s": sb["intervalo_mediano_s"]}, nivel="estimacion")
    anim = [t for t in a["transitions"]["items"] if t["tipo"] in ("barrido_con_desenfoque", "transicion_animada")]
    if len(anim) >= 3:
        card("Transiciones animadas cortas entre bloques", "transicion",
             f"{len(anim)} cambios animados de ~{round(sum(t['duracion_s'] for t in anim) / len(anim), 2)} s marcan los bloques.",
             {"posicion": "segunda"}, {"scene": {"transition": "whip"}},
             "las transiciones animadas duran menos de 0.6 s y no se repiten tres veces seguidas",
             [{"metrica": "plan.escenas_n", "op": ">=", "valor": 5}],
             {"transiciones_animadas": len(anim)}, nivel="estimacion")
    if au and "loudness" in au and au["loudness"]["integrated_lufs"] is not None:
        _ = au
    return out


# ----------------------------------------------------------------------------- commands
def cmd_add(a):
    d = a.analysis_dir
    analysis = load_json(os.path.join(d, "analysis.json"))
    if analysis is None:
        sys.exit("no hay analysis.json en la carpeta")
    errs = validate_analysis(analysis)
    if errs:
        sys.exit("análisis inválido: " + "; ".join(errs[:5]))
    rid = analysis.get("ref_id")
    if not rid:
        sys.exit("el análisis no tiene ref_id (usa --ref-id al analizar)")
    key = norm_key(a.source_key or analysis["source"]["key"])
    dup = seen(key, analysis["source"]["sha256"])
    if dup and dup["ref_id"] != rid:
        print(json.dumps({"ok": False, "duplicado_de": dup["ref_id"]}, ensure_ascii=False))
        sys.exit(10)
    dest = lib("analyses", rid)
    os.makedirs(dest, exist_ok=True)
    shutil.copy(os.path.join(d, "analysis.json"), os.path.join(dest, "analysis.json"))
    if os.path.exists(os.path.join(d, "report.md")):
        shutil.copy(os.path.join(d, "report.md"), os.path.join(dest, "report.md"))
    ix = load_index()
    old = next((r for r in ix["refs"] if r["ref_id"] == rid), {})
    entry = {"ref_id": rid, "source_key": key, "source_title": analysis["source"]["title"],
             "kind": a.kind, "rights": analysis["source"]["rights"], "status": "analyzed", "reason": "",
             "sha256": analysis["source"]["sha256"], "analyzed_at": analysis["meta"]["analyzed_at"],
             "content_sha256": analysis["meta"]["content_sha256"], "cards": old.get("cards", []),
             "summary": old.get("summary", "")}
    if old == entry:
        print(json.dumps({"ok": True, "unchanged": True, "ref_id": rid}))
        return
    ix["refs"] = [r for r in ix["refs"] if r["ref_id"] != rid] + [entry]
    save_index(ix)
    print(json.dumps({"ok": True, "ref_id": rid, "stored": os.path.relpath(dest, lib())}, ensure_ascii=False))


def cmd_fail(a):
    ix = load_index()
    entry = {"ref_id": a.ref_id, "source_key": norm_key(a.source_key), "source_title": a.title or a.source_key,
             "kind": a.kind, "status": "failed", "reason": a.reason, "sha256": "", "analyzed_at": now(), "cards": [],
             "summary": ""}
    ix["refs"] = [r for r in ix["refs"] if r["ref_id"] != a.ref_id] + [entry]
    save_index(ix)
    print(json.dumps({"ok": True, "ref_id": a.ref_id, "status": "failed"}))


def cmd_validate(files):
    files = files or card_files()
    opts = remotion_options.load()
    bad = 0
    for p in files:
        try:
            with open(p) as f:
                e = validate_card(json.load(f), opts)
        except (OSError, ValueError) as ex:
            e = [f"JSON inválido: {ex}"]
        if e:
            bad += 1
            print(f"{os.path.basename(p)}: " + "; ".join(e))
    print(f"{len(files) - bad}/{len(files)} fichas válidas (opciones Remotion leídas de {opts['_source']})")
    return 1 if bad else 0


def valid_cards():
    opts = remotion_options.load()
    out = []
    for p in card_files():
        c = load_json(p)
        if c and not validate_card(c, opts):
            out.append(c)
    return out


def usage_counts():
    u = load_json(lib("usage.json"), {"uses": []})
    counts = {}
    for x in u["uses"]:
        for t in x.get("techniques", []):
            counts[t] = counts.get(t, 0) + 1
    return counts, u


def cmd_propose(a):
    analysis = load_json(a.analysis)
    if analysis is None or validate_analysis(analysis):
        sys.exit("análisis inválido o ilegible")
    drafts = propose(analysis)
    if not a.write:
        print(json.dumps(drafts, indent=1, ensure_ascii=False))
        return
    written = []
    for c in drafts:
        c["id"] = next_id("tec", [os.path.basename(p)[:-5] for p in card_files()])
        errs = validate_card(c)
        if errs:
            print(f"borrador descartado ({c['nombre']}): {errs}")
            continue
        dump_json(c, lib("techniques", f"{c['id']}.json"))
        written.append(c["id"])
    ix = load_index()
    for r in ix["refs"]:
        if r["ref_id"] == analysis.get("ref_id"):
            r["cards"] = sorted(set(r.get("cards", []) + written))
    save_index(ix)
    print(json.dumps({"ok": True, "written": written}))


def cmd_status(a):
    p = lib("techniques", f"{a.tec_id}.json")
    c = load_json(p)
    if c is None:
        sys.exit("ficha no encontrada")
    if a.estado not in STATUS:
        sys.exit("estado desconocido")
    if a.estado == "activa" and c.get("requiere_codigo"):
        sys.exit("requiere código nuevo: no puede activarse")
    c.setdefault("historial", []).append({"fecha": now()[:10], "de": c["estado"], "a": a.estado, "motivo": a.why})
    c["estado"] = a.estado
    c["version"] = int(c.get("version", 1)) + 1
    c["actualizada"] = now()[:10]
    dump_json(c, p)
    print(json.dumps({"ok": True, "id": a.tec_id, "estado": a.estado, "version": c["version"]}))


def cmd_bump(change):
    meta = load_json(lib("library.json"), {"version": "1.0.0"})
    ma, mi, pa = (int(x) for x in meta["version"].split("."))
    meta["version"] = f"{ma}.{mi + 1}.0"
    meta["updated"] = now()
    dump_json(meta, lib("library.json"))
    with open(lib("CHANGELOG.md"), "a") as f:
        f.write(f"\n## {meta['version']} — {now()[:10]}\n- {change}\n")
    print(meta["version"])


def cmd_list():
    counts, _ = usage_counts()
    opts = remotion_options.load()
    for p in card_files():
        c = load_json(p)
        if c is None:
            print(f"{os.path.basename(p)}: JSON ilegible")
            continue
        ok = "ok" if not validate_card(c, opts) else "INVÁLIDA"
        print(f"{c['id']} v{c.get('version')} [{c['estado']}] {c['categoria']}: {c['nombre']} — usada {counts.get(c['id'], 0)} veces ({ok})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("seen"); s.add_argument("key"); s.add_argument("--sha256")  # noqa: E702
    sub.add_parser("next-id"); sub.add_parser("next-tec"); sub.add_parser("list")  # noqa: E702
    s = sub.add_parser("add"); s.add_argument("analysis_dir"); s.add_argument("--source-key"); s.add_argument("--kind", default="file")  # noqa: E702
    s = sub.add_parser("fail"); s.add_argument("ref_id"); s.add_argument("source_key"); s.add_argument("reason")  # noqa: E702
    s.add_argument("--title"); s.add_argument("--kind", default="file")  # noqa: E702
    s = sub.add_parser("propose"); s.add_argument("analysis"); s.add_argument("--write", action="store_true")  # noqa: E702
    s = sub.add_parser("validate"); s.add_argument("files", nargs="*")  # noqa: E702
    s = sub.add_parser("status"); s.add_argument("tec_id"); s.add_argument("estado"); s.add_argument("why")  # noqa: E702
    s = sub.add_parser("bump"); s.add_argument("change")  # noqa: E702
    a = ap.parse_args()
    if a.cmd == "seen":
        r = seen(a.key, a.sha256)
        print(json.dumps(r or {"new": True}, ensure_ascii=False))
        sys.exit(10 if r else 0)
    if a.cmd == "next-id":
        print(next_id("R", [r.get("ref_id") for r in load_index()["refs"]]))
    elif a.cmd == "next-tec":
        print(next_id("tec", [os.path.basename(p)[:-5] for p in card_files()]))
    elif a.cmd == "add":
        cmd_add(a)
    elif a.cmd == "fail":
        cmd_fail(a)
    elif a.cmd == "propose":
        cmd_propose(a)
    elif a.cmd == "validate":
        sys.exit(cmd_validate(a.files))
    elif a.cmd == "status":
        cmd_status(a)
    elif a.cmd == "bump":
        cmd_bump(a.change)
    elif a.cmd == "list":
        cmd_list()


if __name__ == "__main__":
    main()
