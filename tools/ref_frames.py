#!/usr/bin/env python3
"""Referencias de vídeo para el agente e2a-3d-animation (sin red, sin credenciales).

Trabaja sobre una copia LOCAL de la referencia (descargada del conector de Drive o subida por el
propietario). Nunca copia vídeos al repositorio: la caché por defecto vive fuera de Git.

  find   NOMBRE [--dir D ...]           busca un archivo por nombre (sin distinguir mayúsculas) en las carpetas
  probe  VIDEO                          duración, resolución (con rotación aplicada), FPS, códec, tamaño, hash
  frames VIDEO --at 0.7,2.5,4.4 [--out DIR] [--width 720]
                                        extrae fotogramas exactos (ffmpeg -ss después de -i) + hoja de contacto
  check  NOMBRE --at ... [--dir D ...]  find + probe + frames en un paso; escribe report.json

Carpetas por defecto (en este orden; se pueden añadir con --dir o la variable E2A_REFS_DIRS, separadas por ':'):
  /mnt/project-files/tactical-studio/referencias-3d   (carpeta compartida del proyecto, fuera de Git)
  /mnt/project-files/uploads                          (archivos subidos por el propietario desde la app)
  ~/e2a-refs                                          (carpeta local en el ordenador del propietario / Remote Control)
  /mnt/project-files (solo primer nivel)              (archivos que el propietario sube a la Biblioteca con su nombre)
Salida por defecto: /mnt/project-files/tactical-studio/referencias-3d/_inspeccion/<nombre>/
"""
import argparse, hashlib, json, os, subprocess, sys

DEFAULT_DIRS = ["/mnt/project-files/tactical-studio/referencias-3d", "/mnt/project-files/uploads", os.path.expanduser("~/e2a-refs")]
SHALLOW_DIRS = ["/mnt/project-files"]  # raíz de la Biblioteca del proyecto: solo archivos de primer nivel (no se recorre entera)
OUT_ROOT = "/mnt/project-files/tactical-studio/referencias-3d/_inspeccion"
VIDEO_EXT = (".mov", ".mp4", ".m4v", ".mkv", ".avi")


def dirs(extra):
    env = [d for d in os.environ.get("E2A_REFS_DIRS", "").split(":") if d]
    return [d for d in (extra or []) + env + DEFAULT_DIRS if os.path.isdir(d)]


def find(name, extra=None):
    want = name.lower()
    hits = []
    for d in dirs(extra):
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower() == want or (not os.path.splitext(want)[1] and os.path.splitext(f)[0].lower() == want):
                    hits.append(os.path.join(root, f))
    for d in [x for x in SHALLOW_DIRS if os.path.isdir(x)]:
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if os.path.isfile(p) and (f.lower() == want or (not os.path.splitext(want)[1] and os.path.splitext(f)[0].lower() == want)):
                hits.append(p)
    return hits


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"ffprobe falló ({r.returncode}): {r.stderr.strip()}")
    j = json.loads(r.stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    rot = int(v.get("tags", {}).get("rotate", rot))
    w, h = int(v["width"]), int(v["height"])
    dw, dh = (h, w) if abs(rot) % 180 == 90 else (w, h)
    num, den = map(int, v["avg_frame_rate"].split("/"))
    rnum, rden = map(int, v["r_frame_rate"].split("/"))
    return {"path": path, "bytes": os.path.getsize(path), "sha256": _sha(path),
            "duration_s": round(float(j["format"]["duration"]), 3),
            "coded_wh": [w, h], "rotation_deg": rot, "display_wh": [dw, dh],
            "fps_avg": round(num / den, 3) if den else None, "fps_r": round(rnum / rden, 3) if rden else None,
            "frames": int(v["nb_frames"]) if v.get("nb_frames", "").isdigit() else None,
            "vcodec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
            "color": {k: v.get(k) for k in ("color_transfer", "color_primaries", "color_space")},
            "creation_time": j["format"].get("tags", {}).get("creation_time")}


def frames(path, at, out, width=720):
    os.makedirs(out, exist_ok=True)
    got = []
    for t in at:
        dst = os.path.join(out, f"t{t:.2f}s.jpg")
        # -ss after -i = frame-accurate decode; ffmpeg applies the display rotation automatically
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ss", f"{t:.3f}", "-frames:v", "1",
                            "-vf", f"scale={width}:-2", "-q:v", "3", dst], capture_output=True, text=True)
        if r.returncode or not os.path.exists(dst):
            raise SystemExit(f"ffmpeg no pudo extraer {t}s: {r.stderr.strip()}")
        got.append({"t": t, "file": dst})
    sheet = os.path.join(out, "contact.jpg")
    ins = sum((["-i", g["file"]] for g in got), [])
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", f"hstack=inputs={len(got)}", sheet], check=True)
    return {"frames": got, "contact_sheet": sheet}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("find"); a.add_argument("name"); a.add_argument("--dir", action="append")
    a = sp.add_parser("probe"); a.add_argument("video")
    a = sp.add_parser("frames"); a.add_argument("video"); a.add_argument("--at", required=True); a.add_argument("--out"); a.add_argument("--width", type=int, default=720)
    a = sp.add_parser("check"); a.add_argument("name"); a.add_argument("--at", required=True); a.add_argument("--dir", action="append"); a.add_argument("--out"); a.add_argument("--width", type=int, default=720)
    a = p.parse_args(argv)
    if a.cmd == "find":
        print(json.dumps({"searched": dirs(a.dir), "hits": find(a.name, a.dir)}, indent=1, ensure_ascii=False))
    elif a.cmd == "probe":
        print(json.dumps(probe(a.video), indent=1, ensure_ascii=False))
    else:
        at = [float(x) for x in a.at.split(",")]
        path = a.video if a.cmd == "frames" else None
        if a.cmd == "check":
            hits = find(a.name, a.dir)
            if not hits:
                print(json.dumps({"ok": False, "step": "find", "error": f"{a.name} no está en ninguna carpeta local",
                                  "searched": dirs(a.dir)}, indent=1, ensure_ascii=False))
                return 3
            path = hits[0]
        base = os.path.splitext(os.path.basename(path))[0]
        out = a.out or os.path.join(OUT_ROOT, base)
        rep = {"ok": True, "probe": probe(path), **frames(path, at, out, a.width)}
        rep["probe"]["duration_s"] < max(at) and rep.update(ok=False, error="un tiempo pedido supera la duración")
        with open(os.path.join(out, "report.json"), "w") as f:
            json.dump(rep, f, indent=1, ensure_ascii=False)
        print(json.dumps(rep, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
