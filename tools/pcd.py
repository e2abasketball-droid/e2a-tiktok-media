#!/usr/bin/env python3
"""Ficha PCD (Promesa, Curiosidad, Disruptividad) de la apertura de un vídeo E2A — 2026-11-20, encargo
"Double Drag V2 y método PCD". La ficha se rellena ANTES del storyboard y el gate `scripted` la comprueba.

  python3 tools/pcd.py new  --cid <id> --out produccion/tactical/pcd/<id>.md [--ficha <FICHA-TACTICA.md>] [--title T]
        crea la ficha desde la plantilla produccion/tactical/pcd/PLANTILLA-PCD.md; con --ficha hereda título,
        jugadas y las dos lecturas (A/B) como BORRADOR (cuenta como vacío hasta que alguien lo revise)
  python3 tools/pcd.py check <ficha-pcd.md> [--stage script|render]
        script: los 11 campos rellenos (sin TODO ni BORRADOR) y >= 2 aperturas candidatas con una elegida
        render: además los puntos 1-5 de la puerta editorial marcados [x] (6 = datos, se rellena tras publicar)
  En el guion (guion.txt del gate `T script`), primera línea:  PCD: produccion/tactical/pcd/<id>.md
  tools/tactical_studio.py script_check() lee esa línea y rechaza el guion si la ficha no pasa `--stage script`.
Plantilla y versiones anteriores: git log -- produccion/tactical/pcd/PLANTILLA-PCD.md (recuperar con git show <sha>:<ruta>)."""
import argparse, json, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(R, "produccion", "tactical", "pcd", "PLANTILLA-PCD.md")
FIELDS = ["Público y momento", "Promesa", "Curiosidad", "Disruptividad", "Comienzo visible", "Primera evidencia",
          "Primer desenlace", "Reenganche", "Segundo desenlace", "Variante de guion", "Pregunta final"]
EMPTY = re.compile(r"^\s*(TODO|BORRADOR\b|—|-|\.\.\.)?\s*$|^\s*(TODO|BORRADOR)\b", re.I)


def parse(text):
    """fields = '- **<Campo>:** respuesta' lines; candidates = '- H-x: ...'; chosen = '- Elegida: ...';
    gate = '- [x] N. ...' lines under '## Puerta editorial'"""
    f, cands, chosen, gate = {}, [], "", {}
    for line in text.splitlines():
        m = re.match(r"^\s*-\s*\*\*(.+?)(?:\s*\(.*?\))?:\*\*\s*(.*)$", line)
        if m:
            name = m.group(1).strip()
            for k in FIELDS:
                if name.lower().startswith(k.lower()):
                    f[k] = m.group(2).strip()
        m = re.match(r"^\s*-\s*(H-[A-Z0-9]+)\s*:\s*(.*)$", line)
        if m:
            cands.append((m.group(1), m.group(2).strip()))
        m = re.match(r"^\s*-\s*Elegida\s*:\s*(.*)$", line, re.I)
        if m:
            chosen = m.group(1).strip()
        m = re.match(r"^\s*-\s*\[([ xX])\]\s*(\d)\.", line)
        if m:
            gate[int(m.group(2))] = m.group(1).lower() == "x"
    return {"fields": f, "candidates": cands, "chosen": chosen, "gate": gate}


def check(path, stage="script"):
    p = parse(open(path, encoding="utf-8").read())
    missing = [k for k in FIELDS if EMPTY.search(p["fields"].get(k, "") or "")]
    cands = [c for c in p["candidates"] if c[1] and not EMPTY.search(c[1])]
    if len(cands) < 2:
        missing.append("aperturas candidatas (>= 2)")
    if not p["chosen"] or EMPTY.search(p["chosen"]):
        missing.append("apertura elegida")
    if stage == "render":
        missing += [f"puerta editorial {n}" for n in range(1, 6) if not p["gate"].get(n)]
    return {"ok": not missing, "stage": stage, "missing": missing, "candidates": len(cands), "path": os.path.relpath(path, R)}


def from_ficha(path):
    """what a tactical sheet already says: title, plays and the two reads (A/B)"""
    t = open(path, encoding="utf-8").read()
    title = next((l.lstrip("# ").strip() for l in t.splitlines() if l.startswith("# ")), os.path.basename(path))
    plays = sorted(set(re.findall(r"template/tactical/plays/[\w.-]+\.json", t)))
    reads = re.findall(r"^\s*-\s*([AB])\s*:\s*(.+)$", t, re.M)
    return {"title": re.sub(r"^Ficha táctica:\s*", "", title), "plays": plays, "A": next((r[1] for r in reads if r[0] == "A"), ""),
            "B": next((r[1] for r in reads if r[0] == "B"), ""), "ficha": os.path.relpath(path, R) if path.startswith(R) else path}


def new(cid, out, ficha=None, title=None):
    tpl = open(TEMPLATE, encoding="utf-8").read()
    body = tpl.split("<!-- FICHA -->", 1)[1]
    info = from_ficha(ficha) if ficha else {"title": title or cid, "plays": [], "A": "", "B": "", "ficha": "—"}
    head = [f"# Ficha PCD — {title or info['title']}", "",
            f"**Episodio:** `{cid}`. **Ficha táctica:** `{info['ficha']}`. **Jugadas:** {', '.join(f'`{p}`' for p in info['plays']) or '—'}.",
            f"**Generada:** `python3 tools/pcd.py new --cid {cid} --out {os.path.relpath(out, R)}{' --ficha ' + info['ficha'] if ficha else ''}` "
            "(plantilla `produccion/tactical/pcd/PLANTILLA-PCD.md`). Rellénala antes del storyboard; `python3 tools/pcd.py check` la valida.", ""]
    def fill(b, field, text):
        return re.sub(rf"^(- \*\*{field}[^\n]*?:\*\*) TODO$", lambda m: f"{m.group(1)} {text}", b, count=1, flags=re.M)
    if info["A"]:
        body = fill(body, "Primer desenlace", f"BORRADOR (de la ficha, lectura A): {info['A']}")
    if info["B"]:
        body = fill(body, "Segundo desenlace", f"BORRADOR (de la ficha, lectura B): {info['B']}")
        body = fill(body, "Reenganche", "BORRADOR: misma jugada desde el mismo fotograma de decisión; ¿qué abre la otra respuesta del defensor?")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(head) + body.lstrip("\n"))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("new"); a.add_argument("--cid", required=True); a.add_argument("--out", required=True)
    a.add_argument("--ficha"); a.add_argument("--title")
    b = sp.add_parser("check"); b.add_argument("file"); b.add_argument("--stage", choices=["script", "render"], default="script")
    x = ap.parse_args()
    if x.cmd == "new":
        print(new(x.cid, os.path.abspath(x.out), os.path.abspath(x.ficha) if x.ficha else None, x.title))
    else:
        r = check(x.file, x.stage)
        print(json.dumps(r, ensure_ascii=False))
        sys.exit(0 if r["ok"] else 1)
