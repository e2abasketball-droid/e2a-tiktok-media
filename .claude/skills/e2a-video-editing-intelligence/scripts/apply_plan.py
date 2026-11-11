#!/usr/bin/env python3
"""APPLY mode: choose techniques from the library for an original E2A episode and plan the edit.

  apply_plan.py plan <episode.json> --out <dir> [--max 4] [--estados propuesta,probada,activa]
                     [--allow-warnings] [--record]
  apply_plan.py qc <render.mp4> --plan <dir>/plan.json         post-render QC against the plan

`plan` reads the episode (narration words + scenes = the storyboard of the Remotion Pro pipeline),
scores every valid technique card, applies the chosen ones ONLY to edit fields (transition, camera,
layout, backdrop, captions, bg treatment, sound effects, hook/ending type, music drop/payoff anchors)
and writes:
  <dir>/<id>.applied.json   the episode with the techniques applied (the original file is never touched)
  <dir>/plan.json           selection, reasons, scene-by-scene timestamps, changes, rules, QC
  <dir>/plan.md             the same plan for people (Spanish)
The script is protected: words, display, emphasis, lines, labels, values, media, sources, social,
title and voice are compared before and after, and the plan fails if anything there changed.
Remotion compatibility: every applied episode is checked with template/scripts/validate-episode.mjs
(the same validator render-pro.sh runs). A technique that adds validator errors is rejected; one that
adds warnings is rejected too unless --allow-warnings.
`--record` stores the selection in editing-library/usage.json (rotation for the next videos).
Nothing is rendered, published or voiced here.
"""
import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import library as L  # noqa: E402
import remotion_options  # noqa: E402
from common import TEMPLATE_DIR, dump_json, load_json, norm_word  # noqa: E402

EDIT_SCENE_KEYS = {"transition", "camera", "layout", "backdrop", "captions", "sfxTransition", "sfx"}
EDIT_EPISODE_KEYS = {"hook", "techniques"}  # ending describes the closing line of the script: protected
EDIT_MUSIC_KEYS = {"dropAt", "payoffAt"}
VALIDATOR = os.path.join(TEMPLATE_DIR, "scripts", "validate-episode.mjs")
AUDIO_MIX = os.path.join(TEMPLATE_DIR, "audio-mix.json")
STYLE_RANGE = {"tactical": (20, 60)}
DEFAULT_RANGE = (20, 26)


# ----------------------------------------------------------------------------- timing (same rules as the validator)
def resolver(ep):
    keys = [norm_word(w["text"]) for w in ep["words"]]

    def resolve(a, off=0.0):
        if isinstance(a, (int, float)):
            return float(a) + off
        phrase, _, occ = str(a).partition("#")
        want = int(occ) - 1 if occ else 0
        p = [norm_word(x) for x in phrase.split() if norm_word(x)]
        seen = 0
        for i in range(len(keys) - len(p) + 1):
            if keys[i:i + len(p)] == p:
                if seen == want:
                    return ep["words"][i]["start"] + off
                seen += 1
        return None
    return resolve


def timeline(ep):
    res = resolver(ep)
    v_end = ep["words"][-1]["end"]
    starts = [0.0 if i == 0 else res(s["at"], s.get("offset", 0)) for i, s in enumerate(ep["scenes"])]
    out = []
    for i, s in enumerate(ep["scenes"]):
        st = starts[i]
        en = starts[i + 1] if i + 1 < len(starts) else v_end + 0.25
        words = [w["text"] for w in ep["words"] if st is not None and en is not None and st - 0.01 <= w["start"] < en]
        out.append({"i": i, "type": s["type"], "at": s.get("at"), "inicio": None if st is None else round(st, 2),
                    "fin": None if en is None else round(en, 2),
                    "dur": None if st is None or en is None else round(en - st, 2), "texto_voz": " ".join(words)})
    total = v_end + 0.25 + (ep.get("outro") or {}).get("seconds", 1.4)
    return out, round(total, 2)


# ----------------------------------------------------------------------------- protection of the script
def script_part(ep):
    e = copy.deepcopy(ep)
    for k in EDIT_EPISODE_KEYS:
        e.pop(k, None)
    for k in EDIT_MUSIC_KEYS:
        (e.get("music") or {}).pop(k, None)
    for s in e["scenes"]:
        for k in EDIT_SCENE_KEYS:
            s.pop(k, None)
        if isinstance(s.get("bg"), dict):
            s["bg"].pop("treatment", None)
    return e


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


# ----------------------------------------------------------------------------- validator
def run_validator(ep, workdir):
    if not shutil.which("node") or not os.path.exists(VALIDATOR):
        return {"available": False, "errors": [], "warnings": []}
    p = os.path.join(workdir, "_candidate.json")
    dump_json(ep, p)
    r = subprocess.run(["node", VALIDATOR, p], capture_output=True, text=True)
    lines = (r.stdout + r.stderr).splitlines()
    os.remove(p)
    return {"available": True, "ok": r.returncode == 0,
            "errors": [l[6:] for l in lines if l.startswith("ERROR ")],
            "warnings": [l[6:] for l in lines if l.startswith("WARN  ")]}


# ----------------------------------------------------------------------------- targets and scoring
def pick_scene(card, tl, ep, taken):
    tgt = card["aplicar_a"]
    st = tgt.get("scene_type")
    pos = tgt.get("posicion", "cualquiera")
    cands = [s for s in tl if (st is None or s["type"] == st) and s["dur"] is not None]
    if not cands:
        return None, f"el episodio no tiene escenas de tipo {st}"
    n = len(tl)
    fixed = {"primera": 0, "segunda": 1, "ultima": n - 1, "penultima": n - 2}
    if pos in fixed:
        i = fixed[pos]
        hit = [s for s in cands if s["i"] == i]
        return (hit[0], None) if hit else (None, f"la escena {pos} no es de tipo {st}")
    if pos == "mas_larga":
        return max(cands, key=lambda s: (s["dur"], -s["i"])), None
    if pos == "climax":
        music = ep.get("music") or {}
        res = resolver(ep)
        t = res(music["payoffAt"]) if music.get("payoffAt") is not None else 0.75 * ep["words"][-1]["end"]
        return min(cands, key=lambda s: (abs(s["inicio"] - t), s["i"])), None
    free = [s for s in cands if s["i"] not in taken] or cands
    return free[len(free) // 2] if st is None else free[0], None


def plan_metrics(tl, scene, total, ep):
    durs = sorted(s["dur"] for s in tl if s["dur"] is not None)
    med = durs[len(durs) // 2] if len(durs) % 2 else (durs[len(durs) // 2 - 1] + durs[len(durs) // 2]) / 2
    sfx_n = sum(len(s.get("sfx", [])) + (1 if s.get("sfxTransition") else 0) for s in ep["scenes"])
    return {"plan.escena_s": scene["dur"] if scene else None, "plan.mediana_escenas_s": round(med, 2),
            "plan.max_escena_s": max(durs), "plan.escenas_n": len(tl), "plan.duracion_s": total, "plan.sfx_n": sfx_n}


def eval_rules(rules, metrics):
    out = []
    for r in rules:
        v = metrics.get(r["metrica"])
        if v is None:
            out.append({**r, "medido": None, "cumple": None})
        else:
            out.append({**r, "medido": v, "cumple": bool(L.OPS[r["op"]](v, r["valor"]))})
    return out


def score_card(c, ep, tl, total, usage, taken):
    style = ep["style"]
    reasons, score = [], 0.0
    if style in c.get("evitar_en", []):
        return None, [f"evitada en historias '{style}'"], None, []
    if style in c.get("para", []):
        score += 3
        reasons.append(f"pensada para historias '{style}'")
    else:
        score -= 2
        reasons.append(f"no está pensada para '{style}' (−2)")
    scene, why = pick_scene(c, tl, ep, taken)
    if scene is None:
        return None, [why], None, []
    bonus = {"activa": 3, "probada": 2, "propuesta": 0}[c["estado"]]
    score += bonus
    reasons.append(f"estado {c['estado']}" + (f" (+{bonus})" if bonus else " (sin uso probado: modo sombra)"))
    obs = sum(1 for e in c["evidencia"] if e["nivel"] == "observacion")
    est = sum(1 for e in c["evidencia"] if e["nivel"] == "estimacion")
    score += 0.5 * obs + 0.25 * est
    reasons.append(f"evidencia: {obs} medida(s), {est} estimación(es) de {', '.join(sorted({e['ref_id'] for e in c['evidencia']}))}")
    rules = eval_rules([r for r in c["comprobacion"]["reglas"] if r["metrica"].startswith("plan.")],
                       plan_metrics(tl, scene, total, ep))
    for r in rules:
        if r["cumple"] is True:
            score += 1
        elif r["cumple"] is False:
            score -= 1.5
    ok = sum(1 for r in rules if r["cumple"])
    if rules:
        reasons.append(f"encaja con el guion: {ok}/{len(rules)} reglas medibles se cumplen ya en el plan")
    recent = usage[-3:]
    if any(c["id"] in u.get("techniques", []) and u.get("episode") != ep["id"] for u in recent):
        score -= 2
        reasons.append("usada en uno de los 3 últimos vídeos (−2, rotación)")
    return round(score, 2), reasons, scene, rules


# ----------------------------------------------------------------------------- applying a card
def apply_card(ep, c, scene, budget):
    """Mutates ep. Returns (changes, notes)."""
    changes, notes = [], []
    r = c["receta"]
    s = ep["scenes"][scene["i"]]
    for k, v in (r.get("scene") or {}).items():
        if k == "bg_treatment":
            if not isinstance(s.get("bg"), dict):
                notes.append("bg_treatment omitido: la escena no tiene foto de fondo")
                continue
            if s["bg"].get("treatment") != v:
                changes.append({"escena": scene["i"], "campo": "bg.treatment", "antes": s["bg"].get("treatment"), "despues": v})
                s["bg"]["treatment"] = v
            continue
        if k == "transition" and scene["i"] == 0:
            notes.append("transition omitida: la primera escena no tiene transición de entrada")
            continue
        if s.get(k) != v:
            changes.append({"escena": scene["i"], "campo": k, "antes": s.get(k), "despues": v})
            s[k] = v
    for name in r.get("sfx", []):
        used = sum(len(x.get("sfx", [])) + (1 if x.get("sfxTransition") else 0) for x in ep["scenes"])
        if used + 1 > budget:
            notes.append(f"efecto '{name}' omitido: se superaría el presupuesto de {budget} efectos")
            continue
        if any(x.get("name") == name for x in s.get("sfx", [])):
            continue
        at = s.get("at", 0) if scene["i"] else 0
        s.setdefault("sfx", []).append({"at": at, "name": name})
        changes.append({"escena": scene["i"], "campo": "sfx", "antes": None, "despues": name})
    for k, v in (r.get("episode") or {}).items():
        if k == "ending" and ep.get("ending"):
            continue  # never relabel the script's ending (checked before applying)
        if ep.get(k) != v:
            changes.append({"escena": None, "campo": k, "antes": ep.get(k), "despues": v})
            ep[k] = v
    for k, v in (r.get("music") or {}).items():
        field = {"payoff_en_esta_escena": "payoffAt", "drop_en_esta_escena": "dropAt"}[k]
        if v and scene["i"] > 0:
            ep.setdefault("music", {})
            if ep["music"].get(field) != s.get("at"):
                changes.append({"escena": scene["i"], "campo": f"music.{field}", "antes": ep["music"].get(field), "despues": s.get("at")})
                ep["music"][field] = s.get("at")
    return changes, notes


# ----------------------------------------------------------------------------- quality standards on the plan
def quality_checks(ep, tl, total, validator, budget):
    q = []
    lo, hi = STYLE_RANGE.get(ep["style"], DEFAULT_RANGE)

    def add(code, ok, text, level="error"):
        q.append({"codigo": code, "ok": bool(ok), "nivel": level if not ok else "ok", "detalle": text})
    add("Q1", lo <= total <= hi, f"duración prevista {total} s (objetivo {lo}–{hi} s)", "aviso")
    long_ = [s for s in tl if s["type"] != "court" and (s["dur"] or 0) > 6]
    add("Q2", not long_, "ninguna escena de más de 6 s" if not long_ else f"escenas largas: {[(s['i'], s['dur']) for s in long_]}", "aviso")
    static = [s for s in tl if ep["scenes"][s["i"]].get("camera") == "static" and s["type"] != "court" and (s["dur"] or 0) > 2.5]
    add("Q3", not static, "sin planos estáticos de más de 2.5 s" if not static else f"estáticas largas: {[(s['i'], s['dur']) for s in static]}", "aviso")
    durs = sorted(s["dur"] for s in tl if s["dur"])
    med = durs[len(durs) // 2]
    add("Q4", 1.5 <= med <= 4.0, f"mediana de escena {med} s (1.5–4 s)", "aviso")
    tr = [s.get("transition", "cut") for s in ep["scenes"][1:]]
    rep = any(tr[i] == tr[i + 1] == tr[i + 2] != "cut" for i in range(len(tr) - 2))
    add("Q5", not rep, "ninguna transición animada tres veces seguidas" if not rep else "transición animada repetida 3 veces seguidas", "aviso")
    cams = {s.get("camera", "push-in") for s in ep["scenes"]}
    add("Q6", len(ep["scenes"]) < 6 or len(cams) >= 3, f"{len(cams)} movimientos de cámara distintos", "aviso")
    sfx_n = sum(len(s.get("sfx", [])) + (1 if s.get("sfxTransition") else 0) for s in ep["scenes"])
    add("Q7", sfx_n <= budget, f"{sfx_n} efectos colocados a mano (presupuesto {budget})")
    slow = []
    for s in tl:
        sc = ep["scenes"][s["i"]]
        if sc["type"] == "headline" and s["dur"]:
            chars = sum(len(x) for x in sc.get("lines", []))
            if chars / 15.0 > s["dur"]:
                slow.append((s["i"], chars, s["dur"]))
    add("Q8", not slow, "titulares legibles a 15 caracteres/s" if not slow else f"titulares sin tiempo de lectura: {slow}", "aviso")
    inside = []
    for s in tl[1:]:
        t = s["inicio"]
        for w in ep["words"]:
            if w["start"] + 0.04 < t < w["end"] - 0.04:
                inside.append((s["i"], w["text"], t))
    add("Q9", not inside, "todos los cortes caen entre palabras (subtítulos y voz sincronizados)" if not inside
        else f"cortes en mitad de palabra: {inside}", "aviso")
    if validator["available"]:
        add("Q10", not validator["errors"], "validador de Remotion Pro sin errores" if not validator["errors"] else f"errores: {validator['errors']}")
    else:
        add("Q10", True, "validador no disponible (node no instalado): comprobar antes de renderizar", "aviso")
    return q


# ----------------------------------------------------------------------------- plan
def make_plan(ep_path, out, max_n=4, estados=("propuesta", "probada", "activa"), allow_warn=False, record=False):
    ep0 = load_json(ep_path)
    if ep0 is None:
        raise SystemExit("episodio ilegible")
    os.makedirs(out, exist_ok=True)
    ep = copy.deepcopy(ep0)
    mix = load_json(AUDIO_MIX, {})
    budget = ep.get("sfxBudget") or (mix.get("sfx") or {}).get("budget", 2)
    tl, total = timeline(ep)
    if any(s["inicio"] is None for s in tl):
        raise SystemExit("hay anclas de escena que no aparecen en la narración: corrige el episodio antes de planificar")
    _, usage = L.usage_counts()
    usage = usage["uses"]
    cards = [c for c in L.valid_cards() if c["estado"] in estados]
    invalid = [os.path.basename(p) for p in L.card_files() if L.load_json(p) is None or L.validate_card(L.load_json(p))]

    scored, rejected = [], []
    taken = set()
    for c in sorted(cards, key=lambda c: c["id"]):
        sc, reasons, scene, rules = score_card(c, ep, tl, total, usage, taken)
        if sc is None:
            rejected.append({"id": c["id"], "nombre": c["nombre"], "motivo": "; ".join(reasons)})
            continue
        scored.append({"card": c, "score": sc, "reasons": reasons, "scene": scene, "rules": rules})
    scored.sort(key=lambda x: (-x["score"], x["card"]["id"]))

    base_val = run_validator(ep, out)
    chosen, cats, fields = [], set(), {}
    for x in scored:
        c = x["card"]
        if len(chosen) >= max_n:
            rejected.append({"id": c["id"], "nombre": c["nombre"], "motivo": f"ya hay {max_n} técnicas (máximo por vídeo)"})
            continue
        if c["categoria"] in cats:
            rejected.append({"id": c["id"], "nombre": c["nombre"], "motivo": f"ya se eligió otra técnica de {c['categoria']}"})
            continue
        if x["score"] <= 0:
            rejected.append({"id": c["id"], "nombre": c["nombre"], "motivo": f"puntuación {x['score']} ≤ 0"})
            continue
        trial = copy.deepcopy(ep)
        changes, notes = apply_card(trial, c, x["scene"], budget)
        clash = [ch for ch in changes if (ch["escena"], ch["campo"]) in fields and ch["campo"] != "sfx"]
        if clash:
            rejected.append({"id": c["id"], "nombre": c["nombre"],
                             "motivo": f"choca con {fields[(clash[0]['escena'], clash[0]['campo'])]} en {clash[0]['campo']}"})
            continue
        want_end = (c["receta"].get("episode") or {}).get("ending")
        if want_end and ep.get("ending") and want_end != ep["ending"]:
            rejected.append({"id": c["id"], "nombre": c["nombre"], "recomendacion": True,
                             "motivo": f"pide un final '{want_end}' y el guion aprobado cierra con '{ep['ending']}': el guion no se cambia"})
            continue
        failing = [r for r in x["rules"] if r["cumple"] is False]
        if failing:
            rejected.append({"id": c["id"], "nombre": c["nombre"], "recomendacion": True,
                             "motivo": "el guion no permite cumplir " + "; ".join(
                                 f"{r['metrica']} {r['op']} {r['valor']} (medido {r['medido']})" for r in failing)
                             + ": cambiarlo alteraría el ritmo de la narración aprobada"})
            continue
        if not changes:
            chosen.append({**x, "changes": [], "notes": notes + ["el episodio ya cumple esta técnica: no hay cambios"]})
            cats.add(c["categoria"])
            continue
        v = run_validator(trial, out)
        new_err = [e for e in v["errors"] if e not in base_val["errors"]]
        new_warn = [w for w in v["warnings"] if w not in base_val["warnings"]]
        if new_err or (new_warn and not allow_warn):
            rejected.append({"id": c["id"], "nombre": c["nombre"],
                             "motivo": "el validador de Remotion Pro lo desaconseja: " + "; ".join(new_err + new_warn)})
            continue
        ep, base_val = trial, v
        for ch in changes:
            fields[(ch["escena"], ch["campo"])] = c["id"]
        cats.add(c["categoria"])
        taken.add(x["scene"]["i"])
        chosen.append({**x, "changes": changes, "notes": notes})

    ep["techniques"] = [{"id": x["card"]["id"], "version": x["card"]["version"], "escena": x["scene"]["i"],
                         "nombre": x["card"]["nombre"]} for x in chosen]
    if digest(script_part(ep)) != digest(script_part(ep0)):
        raise SystemExit("ABORTADO: un cambio habría tocado el guion aprobado (texto, narración, datos o fuentes)")
    final_val = run_validator(ep, out)
    tl2, total2 = timeline(ep)
    qc = quality_checks(ep, tl2, total2, final_val, budget)
    for x in chosen:
        sc = next(s for s in tl2 if s["i"] == x["scene"]["i"])
        x["rules_after"] = eval_rules([r for r in x["card"]["comprobacion"]["reglas"] if r["metrica"].startswith("plan.")],
                                      plan_metrics(tl2, sc, total2, ep))
        x["rules_render"] = [r for r in x["card"]["comprobacion"]["reglas"] if not r["metrica"].startswith("plan.")]

    applied_path = os.path.join(out, f"{ep['id']}.applied.json")
    dump_json(ep, applied_path)
    scene_rows = []
    for s in tl2:
        sc = ep["scenes"][s["i"]]
        scene_rows.append({**s, "transition": sc.get("transition", "cut") if s["i"] else "—", "camera": sc.get("camera", "push-in"),
                           "layout": sc.get("layout", "center"), "sfx": [x["name"] for x in sc.get("sfx", [])],
                           "tecnicas": [x["card"]["id"] for x in chosen if x["scene"]["i"] == s["i"]],
                           "remotion": {k: sc[k] for k in ("transition", "camera", "layout", "backdrop", "captions") if k in sc}})
    plan = {
        "schema": "e2a.apply-plan/1",
        "episode": {"id": ep["id"], "title": ep["title"], "style": ep["style"], "source": os.path.relpath(ep_path),
                    "script_sha256": digest(script_part(ep0)), "duration_s": total2},
        "library_version": (load_json(L.lib("library.json"), {}) or {}).get("version"),
        "mode": "shadow",
        "selected": [{"id": x["card"]["id"], "version": x["card"]["version"], "nombre": x["card"]["nombre"],
                      "categoria": x["card"]["categoria"], "estado": x["card"]["estado"], "score": x["score"],
                      "escena": x["scene"]["i"], "inicio": x["scene"]["inicio"], "fin": x["scene"]["fin"],
                      "por_que": x["reasons"], "cambios": x["changes"], "notas": x["notes"],
                      "reglas_plan": x["rules_after"], "reglas_render": x["rules_render"],
                      "comprobacion": x["card"]["comprobacion"]["texto"]} for x in chosen],
        "rejected": rejected,
        "invalid_cards": invalid,
        "scenes": scene_rows,
        "audio": {"fuente": "template/audio-mix.json (render-pro.sh + episode-music.mjs)",
                  "voz_lufs": (mix.get("voice") or {}).get("targetLufs"), "musica_bajo_voz_db": (mix.get("music") or {}).get("underVoiceDb"),
                  "snr_banda_voz_db": (mix.get("music") or {}).get("speechBandSnrDb"), "ducking_db": (mix.get("music") or {}).get("duckDb"),
                  "silencio_antes_del_payoff_s": (mix.get("music") or {}).get("silenceBeforePayoff"),
                  "master": "-14 LUFS integrado, pico real -1.5 dBTP (loudnorm en render-pro.sh)",
                  "efectos": f"{sum(len(s['sfx']) for s in scene_rows)} de {budget} permitidos",
                  "music_dropAt": (ep.get("music") or {}).get("dropAt"), "music_payoffAt": (ep.get("music") or {}).get("payoffAt")},
        "validator": final_val,
        "quality": qc,
        "applied_episode": os.path.basename(applied_path),
        "render": f"cd template && bash scripts/render-pro.sh <ruta>/{os.path.basename(applied_path)} out/{ep['id']}.mp4 (solo con autorización)",
        "created_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    plan["plan_sha256"] = digest({k: v for k, v in plan.items() if k not in ("created_at",)})
    dump_json(plan, os.path.join(out, "plan.json"))
    with open(os.path.join(out, "plan.md"), "w") as f:
        f.write(render_md(plan))
    if record:
        u = load_json(L.lib("usage.json"), {"uses": []})
        u["uses"] = [x for x in u["uses"] if x.get("episode") != ep["id"]] + [
            {"episode": ep["id"], "date": plan["created_at"][:10], "techniques": [x["id"] for x in plan["selected"]],
             "plan_sha256": plan["plan_sha256"], "library_version": plan["library_version"]}]
        dump_json(u, L.lib("usage.json"))
    return plan


def render_md(p):
    L_ = []
    w = L_.append
    e = p["episode"]
    w(f"# Plan de edición — {e['title']}")
    w("")
    w(f"Episodio `{e['id']}` ({e['style']}) · {e['duration_s']} s · biblioteca v{p['library_version']} · modo {p['mode']}")
    w(f"Guion protegido: huella `{e['script_sha256'][:12]}…` idéntica antes y después (texto, narración, datos y fuentes intactos).")
    w("")
    w("## Técnicas elegidas")
    if not p["selected"]:
        w("- Ninguna técnica aplicable: el episodio se renderiza como está.")
    for s in p["selected"]:
        w(f"### {s['id']} v{s['version']} · {s['nombre']} ({s['categoria']}, {s['estado']}, puntuación {s['score']})")
        w(f"- Dónde: escena {s['escena']} ({s['inicio']}–{s['fin']} s)")
        w(f"- Por qué: " + "; ".join(s["por_que"]))
        for ch in s["cambios"]:
            w(f"- Cambio: `{ch['campo']}` {ch['antes']!s} → **{ch['despues']}**" + (f" (escena {ch['escena']})" if ch["escena"] is not None else " (episodio)"))
        for n in s["notas"]:
            w(f"- Nota: {n}")
        for r in s["reglas_plan"]:
            w(f"- Regla en el plan: {r['metrica']} {r['op']} {r['valor']} → medido {r['medido']} {'✔' if r['cumple'] else '✘'}")
        for r in s["reglas_render"]:
            w(f"- Regla tras el render (QC): {r['metrica']} {r['op']} {r['valor']}")
        w(f"- Comprobación: {s['comprobacion']}")
        w("")
    w("## Técnicas descartadas")
    for r in p["rejected"]:
        w(f"- {r['id']} {r['nombre']}: {r['motivo']}")
    if p["invalid_cards"]:
        w(f"- Fichas inválidas ignoradas: {', '.join(p['invalid_cards'])}")
    w("")
    w("## Plan por escena (tiempos de la narración)")
    w("| # | inicio–fin (s) | tipo | ancla | transición | cámara | layout | efectos | técnicas | voz |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for s in p["scenes"]:
        voz = s["texto_voz"][:60] + ("…" if len(s["texto_voz"]) > 60 else "")
        w(f"| {s['i']} | {s['inicio']}–{s['fin']} | {s['type']} | {s['at']} | {s['transition']} | {s['camera']} | {s['layout']} | "
          f"{', '.join(s['sfx']) or '—'} | {', '.join(s['tecnicas']) or '—'} | {voz} |")
    w("")
    w("## Instrucciones para Remotion Pro")
    w(f"- Archivo listo para renderizar: `{p['applied_episode']}` (mismo formato que `template/episodes/*.json`; solo cambian campos de edición)")
    w("- Campos por escena: " + "; ".join(f"escena {s['i']}: {json.dumps(s['remotion'], ensure_ascii=False)}" for s in p["scenes"] if s["remotion"]))
    w(f"- Render (solo con autorización): `{p['render']}`")
    w("")
    a = p["audio"]
    w("## Mezcla de audio")
    w(f"- {a['fuente']}: voz a {a['voz_lufs']} LUFS, música {a['musica_bajo_voz_db']} dB por debajo de la voz "
      f"({a['snr_banda_voz_db']} dB en la banda de la voz), ducking {a['ducking_db']} dB, silencio de {a['silencio_antes_del_payoff_s']} s antes del payoff")
    w(f"- Master: {a['master']} · efectos: {a['efectos']}")
    w(f"- Música: drop en {a['music_dropAt'] or 'automático (~30%)'}, payoff en {a['music_payoffAt'] or 'automático (~75%)'}")
    w("- Subtítulos: salen de `words` (no se tocan); cada corte cae al inicio de una palabra (Q9).")
    w("")
    w("## Control de calidad del plan")
    v = p["validator"]
    w(f"- Validador de Remotion Pro: {'OK' if v.get('ok') else ('no disponible' if not v['available'] else 'con errores')}"
      + (f" · avisos: {len(v['warnings'])}" if v["available"] else ""))
    for wn in v.get("warnings", []):
        w(f"  - aviso: {wn}")
    for q in p["quality"]:
        w(f"- {q['codigo']} {'✔' if q['ok'] else ('⚠' if q['nivel'] == 'aviso' else '✘')} {q['detalle']}")
    w("")
    w("Tras renderizar: `apply_plan.py qc <video.mp4> --plan plan.json` mide el vídeo y comprueba las reglas de cada técnica.")
    return "\n".join(L_) + "\n"


# ----------------------------------------------------------------------------- post-render QC
def get_path(d, dotted):
    cur = d
    for k in dotted.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def qc_render(video, plan_path, out=None):
    import analyze_video
    plan = load_json(plan_path)
    out = out or os.path.join(os.path.dirname(plan_path), "qc")
    a, _ = analyze_video.analyse(video, out, ref_id=None, title=plan["episode"]["id"], rights="propio")
    dump_json(a, os.path.join(out, "analysis.json"))
    checks = []
    for s in plan["selected"]:
        for r in s["reglas_render"]:
            v = get_path(a, r["metrica"])
            checks.append({"tecnica": s["id"], **r, "medido": v,
                           "cumple": None if v is None else bool(L.OPS[r["op"]](v, r["valor"]))})
    t, au = a["technical"], a.get("audio") or {}
    lufs = (au.get("loudness") or {}).get("integrated_lufs")
    tp = (au.get("loudness") or {}).get("true_peak_dbfs")
    std = [
        ("R1", t["width"] == 1080 and t["height"] == 1920, f"resolución {t['width']}x{t['height']} (1080x1920)"),
        ("R2", t["fps"] in (30.0, 60.0), f"{t['fps']} fps (30 o 60)"),
        ("R3", lufs is not None and abs(lufs + 14) <= 1.0, f"sonoridad {lufs} LUFS (−14 ± 1)"),
        ("R4", tp is not None and tp <= -1.0, f"pico real {tp} dBFS (≤ −1.0)"),
        ("R5", (a["retention"]["primer_corte_s"] or 99) <= 2.5, f"primer cambio de plano a {a['retention']['primer_corte_s']} s (≤ 2.5)"),
        ("R6", a["retention"]["mayor_tramo_sin_cambio_visual_s"] <= 4.0,
         f"mayor tramo sin cambio visual {a['retention']['mayor_tramo_sin_cambio_visual_s']} s (≤ 4)"),
        ("R7", abs(t["duration_s"] - plan["episode"]["duration_s"]) <= 0.5,
         f"duración {t['duration_s']} s frente a {plan['episode']['duration_s']} s del plan"),
    ]
    res = {"video": os.path.basename(video), "tecnicas": checks,
           "estandares": [{"codigo": c, "ok": bool(ok), "detalle": d} for c, ok, d in std]}
    res["ok"] = all(x["ok"] for x in res["estandares"]) and all(x["cumple"] is not False for x in checks)
    dump_json(res, os.path.join(out, "qc.json"))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("episode")
    p.add_argument("--out", required=True)
    p.add_argument("--max", type=int, default=4)
    p.add_argument("--estados", default="propuesta,probada,activa")
    p.add_argument("--allow-warnings", action="store_true")
    p.add_argument("--record", action="store_true")
    q = sub.add_parser("qc")
    q.add_argument("video")
    q.add_argument("--plan", required=True)
    a = ap.parse_args()
    if a.cmd == "plan":
        plan = make_plan(a.episode, a.out, a.max, tuple(a.estados.split(",")), a.allow_warnings, a.record)
        print(json.dumps({"ok": True, "selected": [s["id"] for s in plan["selected"]],
                          "rejected": len(plan["rejected"]), "validator_ok": plan["validator"].get("ok"),
                          "quality_failed": [q["codigo"] for q in plan["quality"] if not q["ok"]],
                          "plan": os.path.join(a.out, "plan.md")}, ensure_ascii=False))
    else:
        r = qc_render(a.video, a.plan)
        print(json.dumps({"ok": r["ok"], "estandares_fallidos": [x["codigo"] for x in r["estandares"] if not x["ok"]],
                          "reglas_fallidas": [f"{x['tecnica']}:{x['metrica']}" for x in r["tecnicas"] if x["cumple"] is False]},
                         ensure_ascii=False))
        sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
