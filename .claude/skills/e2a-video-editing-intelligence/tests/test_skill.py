#!/usr/bin/env python3
"""Tests for e2a-video-editing-intelligence. Every sample video is generated here with ffmpeg; the
real library is never touched (E2A_EDIT_LIBRARY points at a temporary copy).

  python3 -I .claude/skills/e2a-video-editing-intelligence/tests/test_skill.py [--remotion]

--remotion also renders one still of the applied storyboard with Remotion Pro (about 15 s; uses a
temporary silent voice file that is deleted afterwards).
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCRIPTS = os.path.join(SKILL, "scripts")
REPO = os.path.abspath(os.path.join(SKILL, "..", "..", ".."))
TEMPLATE = os.path.join(REPO, "template")
PY = [sys.executable, "-I"]
ok = fail = 0
results = []


def check(name, cond, info=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"PASS {name}")
    else:
        fail += 1
        print(f"FAIL {name} :: {str(info)[:600]}")
    results.append((name, bool(cond)))


def py(script, *args, env=None):
    return subprocess.run(PY + [os.path.join(SCRIPTS, script), *args], capture_output=True, text=True, env=env)


def ff(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


def jout(r):
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {}


tmp = tempfile.mkdtemp(prefix="e2a-vei-")
env = dict(os.environ, E2A_EDIT_LIBRARY=os.path.join(tmp, "lib"))
shutil.copytree(os.path.join(REPO, "editing-library"), env["E2A_EDIT_LIBRARY"])
try:
    S = os.path.join(tmp, "samples")
    os.makedirs(S)
    # ------------------------------------------------------------------ sample videos
    ff("-f", "lavfi", "-i", "color=c=red:s=360x640:d=2:r=30", "-f", "lavfi", "-i", "testsrc=s=360x640:d=2:r=30",
       "-f", "lavfi", "-i", "color=c=blue:s=360x640:d=2:r=30", "-f", "lavfi", "-i", "sine=f=440:d=6",
       "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v];[3:a]volume='if(between(t,2.5,3.5),0,1)':eval=frame[a]",
       "-map", "[v]", "-map", "[a]", "-pix_fmt", "yuv420p", os.path.join(S, "cuts.mp4"))
    ff("-f", "lavfi", "-i", "mandelbrot=s=1080x1080", "-frames:v", "1", os.path.join(S, "still.png"))
    still = os.path.join(S, "still.png")
    ff("-loop", "1", "-i", still, "-t", "4", "-r", "30", "-vf",
       "zoompan=z='1+0.0025*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=360x640:fps=30", "-pix_fmt", "yuv420p",
       os.path.join(S, "zoom.mp4"))
    ff("-loop", "1", "-i", still, "-t", "4", "-r", "30", "-vf", "crop=360:640:x='t*150':y=0", "-pix_fmt", "yuv420p",
       os.path.join(S, "pan.mp4"))
    ff("-loop", "1", "-i", still, "-t", "4", "-r", "30", "-vf", "crop=360:640:x=360:y='200-t*40'", "-pix_fmt", "yuv420p",
       os.path.join(S, "tilt.mp4"))
    ff("-loop", "1", "-i", still, "-t", "3", "-r", "24", "-vf", "scale=1280:720", "-pix_fmt", "yuv420p", os.path.join(S, "wide24.mp4"))
    ff("-f", "lavfi", "-i", "color=c=0x0B1C3D:s=360x640:d=2:r=30", "-f", "lavfi", "-i", "color=c=0xC9A24D:s=360x640:d=2:r=30",
       "-filter_complex", "[0:v][1:v]xfade=transition=fade:duration=0.6:offset=1.2[v]", "-map", "[v]", "-pix_fmt", "yuv420p",
       os.path.join(S, "dissolve.mp4"))
    open(os.path.join(S, "corrupt.mp4"), "w").write("this is not a video")
    with open(os.path.join(S, "cuts.mp4"), "rb") as f:
        open(os.path.join(S, "truncated.mp4"), "wb").write(f.read()[:1500])
    open(os.path.join(S, "empty.mp4"), "w").close()
    ff("-f", "lavfi", "-i", "sine=f=440:d=2", os.path.join(S, "audio_only.m4a"))
    shutil.copy(os.path.join(S, "cuts.mp4"), os.path.join(S, "same_video_other_name.mp4"))

    def analyse(name, *extra):
        out = os.path.join(tmp, "out_" + name.split(".")[0])
        r = py("analyze_video.py", os.path.join(S, name), out, "--rights", "propio", *extra)
        a = json.load(open(os.path.join(out, "analysis.json"))) if r.returncode == 0 else None
        return r, out, a

    # ------------------------------------------------------------------ 1. duration / fps / resolution
    r, out_c, a = analyse("cuts.mp4", "--ref-id", "R-9001")
    check("T1 analiza un vídeo válido (exit 0)", r.returncode == 0, r.stdout + r.stderr)
    t = a["technical"]
    check("T1 duración, FPS y resolución 9:16", abs(t["duration_s"] - 6) < 0.1 and t["fps"] == 30 and
          (t["width"], t["height"]) == (360, 640) and t["aspect_ratio"] == "9:16", t)
    r2, _, a2 = analyse("wide24.mp4")
    t2 = a2["technical"]
    check("T1 vídeo 16:9 a 24 fps", t2["fps"] == 24 and t2["aspect_ratio"] == "16:9" and t2["orientation"] == "horizontal", t2)

    # ------------------------------------------------------------------ 2. cuts and transitions
    cuts = a["editing"]["cuts"]
    check("T2 detecta los 2 cortes (2 s y 4 s)", len(cuts) == 2 and abs(cuts[0] - 2) < 0.15 and abs(cuts[1] - 4) < 0.15, cuts)
    check("T2 duración de planos", [s["duracion_s"] for s in a["shots"]] == [round(cuts[0], 2), round(cuts[1] - cuts[0], 2), round(6 - cuts[1], 2)], a["shots"])
    check("T2 cortes secos clasificados como corte", all(x["tipo"] == "corte" for x in a["transitions"]["items"]), a["transitions"])
    _, _, ad = analyse("dissolve.mp4")
    tr = ad["transitions"]["items"]
    check("T2 fundido encadenado detectado como transición animada", len(tr) == 1 and tr[0]["tipo"] in ("fundido_encadenado", "transicion_animada")
          and tr[0]["duracion_s"] >= 0.3, tr)
    check("T2 vídeo sin cortes: 0 cortes", analyse("wide24.mp4")[2]["editing"]["cuts"] == [], "")

    # ------------------------------------------------------------------ 3. camera moves (Remotion names)
    cams = {n: analyse(n + ".mp4")[2]["shots"][0]["camara"]["movimiento"] for n in ("zoom", "pan", "tilt")}
    check("T3 zoom de acercamiento → push-in", cams["zoom"] == "push-in", cams)
    check("T3 paneo (imagen hacia la izquierda) → pan-left", cams["pan"] == "pan-left", cams)
    check("T3 inclinación (imagen hacia abajo) → tilt-up", cams["tilt"] == "tilt-up", cams)
    check("T3 plano fijo → static", a2["shots"][0]["camara"]["movimiento"] == "static", a2["shots"][0]["camara"])

    # ------------------------------------------------------------------ 4. frames
    frames = a["frames"]["items"]
    check("T4 fotogramas representativos extraídos", len(frames) >= 4 and all(os.path.exists(os.path.join(out_c, f["file"])) for f in frames), frames)
    check("T4 hoja de contactos", a["frames"]["sheet"] and os.path.exists(os.path.join(out_c, a["frames"]["sheet"])), a["frames"])
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width",
                            "-of", "csv=p=0", os.path.join(out_c, frames[0]["file"])], capture_output=True, text=True)
    check("T4 fotograma a 360 px de ancho", probe.stdout.strip() == "360", probe.stdout)
    fx = os.path.join(tmp, "fx")
    r = py("extract_frames.py", os.path.join(S, "cuts.mp4"), fx, "--times", "0.5,2.5,4.5", "--sheet")
    check("T4 extract_frames.py por tiempos + hoja", r.returncode == 0 and len(glob.glob(os.path.join(fx, "f_*.jpg"))) == 3
          and os.path.exists(os.path.join(fx, "sheet.jpg")), r.stdout + r.stderr)

    # ------------------------------------------------------------------ 5. audio
    au = a["audio"]
    check("T5 sonoridad medida (LUFS)", au["loudness"]["integrated_lufs"] is not None, au["loudness"])
    sil = au["silences"]["items"]
    check("T5 silencio de 2.5 a 3.5 s detectado", any(abs(x - 2.5) < 0.1 and abs(y - 3.5) < 0.1 for x, y in sil), sil)
    check("T5 un tono puro no se confunde con voz", au["voz"]["presente"] is False, au["voz"])
    check("T5 vídeo sin audio: sección audio vacía", a2["audio"] is None and a2["technical"]["has_audio"] is False, a2["audio"])
    r = py("analyze_audio.py", os.path.join(S, "cuts.mp4"))
    check("T5 analyze_audio.py independiente", r.returncode == 0 and jout(r).get("ok"), r.stdout + r.stderr)

    # ------------------------------------------------------------------ 6. valid JSON + report
    r = py("validate_analysis.py", *glob.glob(os.path.join(tmp, "out_*", "analysis.json")))
    check("T6 todos los analysis.json pasan el validador", r.returncode == 0, r.stdout)
    bad = dict(a)
    bad["editing"] = dict(a["editing"], cuts=[4.0, 2.0])
    bp = os.path.join(tmp, "bad.json")
    json.dump(bad, open(bp, "w"))
    r = py("validate_analysis.py", bp)
    check("T6 análisis manipulado rechazado (orden + huella)", r.returncode == 1 and "content_sha256" in r.stdout and "ordenado" in r.stdout, r.stdout)
    json.dump({"schema_version": "x"}, open(bp, "w"))
    check("T6 análisis incompleto rechazado", py("validate_analysis.py", bp).returncode == 1)
    rep = open(os.path.join(out_c, "report.md")).read()
    secs = [f"## {i}." for i in range(1, 13)]
    check("T6 informe Markdown con las 12 secciones", all(s in rep for s in secs), [s for s in secs if s not in rep])
    check("T6 niveles de evidencia en el informe", all(x in rep for x in ("[observación]", "[estimación]", "[hipótesis]")))

    # ------------------------------------------------------------------ 7. corrupt files
    for name, why in (("corrupt.mp4", "texto"), ("truncated.mp4", "truncado"), ("empty.mp4", "vacío"), ("audio_only.m4a", "sin vídeo")):
        r = py("analyze_video.py", os.path.join(S, name), os.path.join(tmp, "bad_" + name))
        j = jout(r)
        check(f"T7 archivo dañado ({why}): falla controlado", r.returncode == 2 and j.get("ok") is False and j.get("reason")
              and "Traceback" not in r.stderr, r.stdout + r.stderr[-300:])

    # ------------------------------------------------------------------ 8. idempotence
    r = py("analyze_video.py", os.path.join(S, "cuts.mp4"), out_c, "--rights", "propio", "--ref-id", "R-9001")
    check("T8 segundo análisis del mismo archivo: no recalcula", jout(r).get("cached") is True, r.stdout)
    h1 = a["meta"]["content_sha256"]
    r = py("analyze_video.py", os.path.join(S, "cuts.mp4"), out_c, "--rights", "propio", "--ref-id", "R-9001", "--force")
    check("T8 recalcular da exactamente las mismas medidas", jout(r).get("content_sha256") == h1, (h1, r.stdout))
    r = py("library.py", "add", out_c, env=env)
    r2 = py("library.py", "add", out_c, env=env)
    check("T8 añadir a la biblioteca dos veces: sin duplicar", r.returncode == 0 and jout(r2).get("unchanged") is True, r.stdout + r2.stdout)
    ix = json.load(open(os.path.join(env["E2A_EDIT_LIBRARY"], "index.json")))
    check("T8 índice con una sola entrada R-9001", sum(1 for x in ix["refs"] if x["ref_id"] == "R-9001") == 1, ix)
    out_o = os.path.join(tmp, "out_other")
    py("analyze_video.py", os.path.join(S, "same_video_other_name.mp4"), out_o, "--rights", "propio", "--ref-id", "R-9002")
    r = py("library.py", "add", out_o, env=env)
    check("T8 mismo vídeo con otro nombre: detectado como duplicado", r.returncode == 10 and jout(r).get("duplicado_de") == "R-9001", r.stdout)
    r = py("library.py", "seen", "x", "--sha256", a["source"]["sha256"], env=env)
    check("T8 seen por huella", r.returncode == 10, r.stdout)

    # ------------------------------------------------------------------ 9. technique selection for a storyboard
    sb = os.path.join(HERE, "fixtures", "storyboard.json")
    ap = os.path.join(tmp, "apply")
    r = py("apply_plan.py", "plan", sb, "--out", ap, env=env)
    check("T9 plan generado", r.returncode == 0, r.stdout + r.stderr)
    plan = json.load(open(os.path.join(ap, "plan.json")))
    sel = [s["id"] for s in plan["selected"]]
    check("T9 elige técnicas y explica por qué", 1 <= len(sel) <= 4 and all(s["por_que"] for s in plan["selected"]), plan["selected"])
    check("T9 una técnica por categoría", len({s["categoria"] for s in plan["selected"]}) == len(sel), sel)
    check("T9 titular → tec-0002 (layout high) aplicada en la escena del titular",
          any(s["id"] == "tec-0002" and any(c["campo"] == "layout" and c["despues"] == "high" for c in s["cambios"]) for s in plan["selected"]),
          plan["selected"])
    check("T9 plan con tiempos por escena", all(s["inicio"] is not None and s["fin"] > s["inicio"] for s in plan["scenes"]), plan["scenes"])
    rej = {x["id"]: x["motivo"] for x in plan["rejected"]}
    check("T9 técnica que cambiaría el final del guion: no se aplica", "tec-0003" in rej and "guion" in rej["tec-0003"], rej)
    ep0 = json.load(open(sb))
    ep1 = json.load(open(os.path.join(ap, "test-storyboard.applied.json")))
    same = all(ep0[k] == ep1[k] for k in ("words", "display", "emphasis", "sources", "social", "title", "voice", "ending"))
    same = same and all({k: v for k, v in s0.items() if k not in ("transition", "camera", "layout", "backdrop", "captions", "sfx", "sfxTransition", "bg")}
                        == {k: v for k, v in s1.items() if k not in ("transition", "camera", "layout", "backdrop", "captions", "sfx", "sfxTransition", "bg")}
                        for s0, s1 in zip(ep0["scenes"], ep1["scenes"]))
    check("T9 guion intacto (narración, textos, datos, fuentes)", same and len(ep0["scenes"]) == len(ep1["scenes"]))
    check("T9 técnicas registradas en el episodio", [x["id"] for x in ep1["techniques"]] == sel, ep1.get("techniques"))
    tac = dict(ep0, style="tactical", id="test-tactical")
    tp = os.path.join(tmp, "tactical.json")
    json.dump(tac, open(tp, "w"))
    r = py("apply_plan.py", "plan", tp, "--out", os.path.join(tmp, "apply_tac"), env=env)
    ptac = json.load(open(os.path.join(tmp, "apply_tac", "plan.json")))
    check("T9 historia táctica: fichas con evitar_en=tactical excluidas", all(s["id"] not in ("tec-0001", "tec-0004") for s in ptac["selected"]),
          [s["id"] for s in ptac["selected"]])
    r = py("apply_plan.py", "plan", sb, "--out", os.path.join(tmp, "apply2"), env=env)
    p2 = json.load(open(os.path.join(tmp, "apply2", "plan.json")))
    check("T9 selección determinista", p2["plan_sha256"] == plan["plan_sha256"], (p2["plan_sha256"], plan["plan_sha256"]))

    # ------------------------------------------------------------------ 10. Remotion compatibility
    check("T10 episodio aplicado pasa el validador de Remotion Pro", plan["validator"]["available"] and plan["validator"]["ok"], plan["validator"])
    check("T10 estándares de calidad del plan cumplidos", all(q["ok"] for q in plan["quality"]), [q for q in plan["quality"] if not q["ok"]])
    lib_t = os.path.join(env["E2A_EDIT_LIBRARY"], "techniques")
    good = json.load(open(os.path.join(lib_t, "tec-0002.json")))
    json.dump(dict(good, id="tec-0901", receta={"scene": {"transition": "glitch-3d", "camera": "orbit"}}), open(os.path.join(lib_t, "tec-0901.json"), "w"))
    json.dump(dict(good, id="tec-0902", receta={"scene": {"lines": ["NUEVO TEXTO"]}}), open(os.path.join(lib_t, "tec-0902.json"), "w"))
    open(os.path.join(lib_t, "tec-0903.json"), "w").write("{roto")
    json.dump(dict(good, id="tec-0904", comprobacion={"texto": "se ve bien", "reglas": []}), open(os.path.join(lib_t, "tec-0904.json"), "w"))
    r = py("library.py", "validate", env=env)
    check("T10 receta no soportada por Remotion rechazada", "glitch-3d" in r.stdout and "orbit" in r.stdout, r.stdout)
    check("T10 receta que toca el guion rechazada", "tec-0902" in r.stdout and "campos del guion" in r.stdout, r.stdout)
    check("T10 JSON roto detectado sin romper", "tec-0903.json: JSON inválido" in r.stdout, r.stdout)
    check("T10 ficha sin regla medible rechazada", "tec-0904" in r.stdout and "reglas" in r.stdout, r.stdout)
    r = py("apply_plan.py", "plan", sb, "--out", os.path.join(tmp, "apply3"), env=env)
    p3 = json.load(open(os.path.join(tmp, "apply3", "plan.json")))
    check("T10 fichas inválidas ignoradas por APPLY", set(p3["invalid_cards"]) >= {"tec-0901.json", "tec-0902.json", "tec-0903.json", "tec-0904.json"}
          and p3["validator"]["ok"], p3["invalid_cards"])
    for x in ("tec-0901", "tec-0902", "tec-0903", "tec-0904"):
        os.remove(os.path.join(lib_t, x + ".json"))
    if "--remotion" in sys.argv:
        voice = os.path.join(TEMPLATE, "public", "audio", "test-storyboard.mp3")
        made_dir = not os.path.isdir(os.path.dirname(voice))
        os.makedirs(os.path.dirname(voice), exist_ok=True)
        ff("-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "22", "-q:a", "9", voice)
        props = os.path.join(tmp, "props.json")
        ep_r = dict(ep1, music={"src": "audio/test-storyboard.mp3", "premixed": True, "engine": "file"})
        json.dump({"episode": ep_r}, open(props, "w"))
        chrome = (glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell") or [None])[0]
        png = os.path.join(tmp, "still.png")
        cmd = ["npx", "remotion", "still", "src/index.ts", "Pro", png, "--frame=180", f"--props={props}", "--log=error"]
        if chrome:
            cmd.append(f"--browser-executable={chrome}")
        rr = subprocess.run(cmd, cwd=TEMPLATE, capture_output=True, text=True)
        os.remove(voice)
        if made_dir:
            os.rmdir(os.path.dirname(voice))
        check("T10 Remotion Pro renderiza el episodio aplicado (still)", rr.returncode == 0 and os.path.exists(png), rr.stdout + rr.stderr)

    # ------------------------------------------------------------------ 11. usage record and rotation
    r = py("apply_plan.py", "plan", sb, "--out", os.path.join(tmp, "apply4"), "--record", env=env)
    u = json.load(open(os.path.join(env["E2A_EDIT_LIBRARY"], "usage.json")))
    check("T11 uso registrado en usage.json", any(x["episode"] == "test-storyboard" and x["techniques"] == sel for x in u["uses"]), u)
    py("apply_plan.py", "plan", sb, "--out", os.path.join(tmp, "apply4"), "--record", env=env)
    u2 = json.load(open(os.path.join(env["E2A_EDIT_LIBRARY"], "usage.json")))
    check("T11 registrar dos veces el mismo episodio no duplica", len(u2["uses"]) == len(u["uses"]), u2)
    other = dict(ep0, id="test-next")
    op = os.path.join(tmp, "next.json")
    json.dump(other, open(op, "w"))
    py("apply_plan.py", "plan", op, "--out", os.path.join(tmp, "apply5"), env=env)
    p5 = json.load(open(os.path.join(tmp, "apply5", "plan.json")))
    check("T11 rotación: el siguiente vídeo penaliza las técnicas recién usadas",
          all(any("rotación" in r_ for r_ in s["por_que"]) for s in p5["selected"] if s["id"] in sel), p5["selected"])

    # ------------------------------------------------------------------ 12. post-render QC
    qcp = os.path.join(tmp, "qc_plan.json")
    json.dump(dict(plan, episode=dict(plan["episode"], duration_s=6.0)), open(qcp, "w"))
    r = py("apply_plan.py", "qc", os.path.join(S, "cuts.mp4"), "--plan", qcp, env=env)
    q = json.load(open(os.path.join(tmp, "qc", "qc.json")))
    check("T12 QC tras el render mide el vídeo y evalúa estándares y reglas",
          {x["codigo"] for x in q["estandares"]} >= {"R1", "R3", "R7"} and not next(x for x in q["estandares"] if x["codigo"] == "R1")["ok"]
          and r.returncode == 1, q)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{ok}/{ok + fail} pruebas OK")
sys.exit(1 if fail else 0)
