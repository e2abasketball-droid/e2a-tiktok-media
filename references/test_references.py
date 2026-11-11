#!/usr/bin/env python3
"""Robustness tests for the edit-reference library (P2-P5 of the proposal). Run:
    python3 -I references/test_references.py
Uses a synthetic video made with ffmpeg; touches nothing outside a temp folder."""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PY = [sys.executable, "-I"]
ok = fail = 0


def check(name, cond, info=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"PASS {name}")
    else:
        fail += 1
        print(f"FAIL {name} {info}")


def run(args, **kw):
    return subprocess.run(PY + args, capture_output=True, text=True, **kw)


tmp = tempfile.mkdtemp()
try:
    # synthetic reference: 3 shots (2 s red still, 2 s zooming test pattern, 2 s blue) + tone with a gap
    vid = os.path.join(tmp, "ref.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y",
                    "-f", "lavfi", "-i", "color=c=red:s=360x640:d=2:r=30",
                    "-f", "lavfi", "-i", "testsrc=s=360x640:d=2:r=30",
                    "-f", "lavfi", "-i", "color=c=blue:s=360x640:d=2:r=30",
                    "-f", "lavfi", "-i", "sine=f=440:d=6",
                    "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]",
                    "-map", "[v]", "-map", "3:a", "-shortest", "-pix_fmt", "yuv420p", vid], check=True)

    out = os.path.join(tmp, "R-0001")
    r = run([os.path.join(HERE, "analyze_reference.py"), vid, out, "--ref-id", "R-0001"])
    check("P7 analiza un vídeo válido", r.returncode == 0, r.stdout + r.stderr)
    m = json.load(open(os.path.join(out, "measures.json")))
    cuts = m["editing"]["cuts"]
    check("P7 detecta los 2 cortes", len(cuts) == 2 and abs(cuts[0] - 2) < 0.3 and abs(cuts[1] - 4) < 0.3, cuts)
    check("P7 hoja de contactos", os.path.exists(os.path.join(out, "sheet.jpg")))
    check("P7 mide el audio", m["audio"] and m["audio"]["integrated_lufs"] is not None, m["audio"])

    bad = os.path.join(tmp, "bad.mp4")
    open(bad, "w").write("not a video")
    r = run([os.path.join(HERE, "analyze_reference.py"), bad, os.path.join(tmp, "R-0002")])
    check("P3 archivo dañado: falla controlado (exit 2 + motivo)", r.returncode == 2 and '"ok": false' in r.stdout, r.stdout)

    # library on a copy so the real index is untouched
    lib = os.path.join(tmp, "lib")
    shutil.copytree(HERE, lib, ignore=shutil.ignore_patterns("__pycache__"))
    open(os.path.join(lib, "index.json"), "w").write('{"refs": []}')
    L = os.path.join(lib, "library.py")
    r = run([L, "seen", "https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUvWx/view"])
    check("P4 referencia nueva", r.returncode == 0)
    entry = os.path.join(tmp, "e.json")
    json.dump({"ref_id": "R-0001", "source_key": "https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUvWx/view?usp=x",
               "status": "analyzed", "sha256": m["sha256"]}, open(entry, "w"))
    run([L, "record", entry])
    r = run([L, "seen", "1AbCdEfGhIjKlMnOpQrStUvWx"])
    check("P4 misma referencia: no se repite", r.returncode == 10)
    r = run([L, "seen", "otro-nombre", "--sha256", m["sha256"]])
    check("P4 mismo vídeo con otro nombre: no se repite", r.returncode == 10)
    r = run([L, "next-id"])
    check("P4 siguiente id", r.stdout.strip() == "R-0002", r.stdout)

    good = json.load(open(os.path.join(HERE, "techniques", "_example.json")))
    good["id"] = "tec-0001"
    json.dump(good, open(os.path.join(lib, "techniques", "tec-0001.json"), "w"))
    broken = dict(good, id="tec-0002", receta={"scene": {"transition": "glitch-3d", "camera": "orbit"}})
    json.dump(broken, open(os.path.join(lib, "techniques", "tec-0002.json"), "w"))
    open(os.path.join(lib, "techniques", "tec-0003.json"), "w").write("{roto")
    r = run([L, "validate"])
    check("P5 ficha válida aceptada", "1/3 fichas válidas" in r.stdout, r.stdout)
    check("P5 recetas no soportadas por Remotion rechazadas", "glitch-3d" in r.stdout and "orbit" in r.stdout, r.stdout)
    check("P5 JSON roto detectado sin romper", "tec-0003.json: JSON inválido" in r.stdout, r.stdout)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{ok}/{ok + fail} pruebas OK")
sys.exit(1 if fail else 0)
