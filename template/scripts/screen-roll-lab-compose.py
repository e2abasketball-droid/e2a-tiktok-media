# E2A 3D lab, phase 3 — side-by-side comparison A | B | C | REF (ffmpeg), with phase captions in engine time.
# Inputs: renders of scripts/screen-roll-lab-compare-bundle.py (540x960 each, --scale=0.5) and the REF panel (5452,
# mirrored, time-warped by the same milestones as the clip; built outside the repo, never committed).
# Usage: python3 scripts/screen-roll-lab-compose.py RENDER_DIR OUT_DIR
import json, os, subprocess, sys

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# engine milestones of the lab play (skelPlan knots, see INFORME): brake 0.92, set 1.42, open 2.45, release 3.24
PHASES = [("APROXIMACION", 0.0, 0.92), ("FRENADA EN 2 APOYOS", 0.92, 1.42), ("BLOQUEO", 1.42, 2.45),
          ("APERTURA + PIVOTE", 2.45, 3.24), ("PRIMEROS PASOS", 3.24, 9.0)]
REMAP = {"real": (0.3, 1.0), "slow": (0.75, 0.4)}  # play time = p0 + video time * rate
LABELS = {"A": "A  rig d1d44b7", "B": "B  clip + capsula", "C": "C  clip + malla", "REF": "REF  5452 (espejo)"}


def esc(s):
    return s.replace(":", "\\:").replace("'", "")


outs = []
for view in ("tactica", "34"):
    for speed in ("real", "slow"):
        p0, rate = REMAP[speed]
        ins = [f"{src}/{view}-{speed}-{L}.mp4" for L in "ABC"] + [f"{src}/ref-{speed}.mp4"]
        fl = []
        for k, L in enumerate(["A", "B", "C", "REF"]):
            fl.append(f"[{k}:v]scale=540:960,setsar=1,drawbox=x=0:y=0:w=540:h=56:color=black@0.55:t=fill,"
                      f"drawtext=fontfile={FONT}:text='{esc(LABELS[L])}':x=16:y=14:fontsize=28:fontcolor=white[v{k}]")
        cap = []
        for name, a, b in PHASES:
            ta, tb = (a - p0) / rate, (b - p0) / rate
            cap.append(f"drawtext=fontfile={FONT}:text='{esc(name)}':x=(w-tw)/2:y=h-70:fontsize=34:fontcolor=0xC9A24D:"
                       f"box=1:boxcolor=black@0.6:boxborderw=12:enable='between(t,{max(0, ta):.3f},{tb:.3f})'")
        sp = "VELOCIDAD REAL" if speed == "real" else "CAMARA LENTA 0.4x (remap del motor)"
        cap.append(f"drawtext=fontfile={FONT}:text='{esc(sp)}':x=w-tw-20:y=h-130:fontsize=24:fontcolor=white")
        fc = ";".join(fl) + ";[v0][v1][v2][v3]hstack=inputs=4[s];[s]" + ",".join(cap) + "[o]"
        out = f"{dst}/comparativa_{view}_{'real' if speed == 'real' else 'lenta'}.mp4"
        cmd = ["ffmpeg", "-v", "error", "-y"] + sum([["-i", i] for i in ins], []) + [
            "-filter_complex", fc, "-map", "[o]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-r", "30", "-shortest", out]
        subprocess.run(cmd, check=True)
        outs.append(out)
        print(out)
# combined: the four comparisons one after another
lst = f"{dst}/_concat.txt"
open(lst, "w").write("".join(f"file '{os.path.abspath(o)}'\n" for o in outs))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{dst}/comparativa_combinada.mp4"], check=True)
os.remove(lst)
print(f"{dst}/comparativa_combinada.mp4")
