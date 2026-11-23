# Realism V3.3 — 08 REPRODUCE

Versiones: Node v22.23.5, Remotion 4.0.539, Chrome for Testing 157.0.8103.78 (headless shell, `--gl=swangle`), Python 3.13.18, bpy 5.3.0, ffmpeg 6.1.1. Máquina de 4 núcleos, 15 GB y sin GPU.

Semillas: deterministas por jugador (`SEEDS` en `clips33.ts`: O1 11, O2 23, X2 37, O3 41, O4 53, O5 61, X1 71, X3 83, X4 97, X5 101). No hay aleatoriedad en tiempo de render.

```bash
git checkout claude/realism-v3-3
cd template && npm ci
# jugada 5v5 (opcional: ya está versionada)
python3 tactical/specs/_gen-realism-v3-3-5v5.py
# QC (mismos detectores V3.2 + anatómico); salida JSON + filas + CSV por frame
npx tsx scripts/qc-realism-v33.mts tactical/plays/realism-v3-2-abc.json --players O1 --motion v33 --json abc.json --frames abc_rows.json --csv abc.csv
npx tsx scripts/qc-realism-v33.mts tactical/plays/realism-v3-2-trio.json --players O1,O2,X2 --motion v33 --json trio.json --frames trio_rows.json --csv trio.csv
npx tsx scripts/qc-realism-v33.mts tactical/plays/realism-v3-3-5v5.json --players O1,O2,O3,O4,O5,X1,X2,X3,X4,X5 --motion v33 --json 5v5.json --frames 5v5_rows.json --csv 5v5.csv
#   --motion engine | v31 | v32 para las referencias; --rig off|def para el test de dos cuerpos
npx tsx scripts/qc-determinism-v33.mts tactical/plays/realism-v3-3-5v5.json
npx tsx scripts/test-play.mts tactical/plays/realism-v3-3-5v5.json
npx tsc --noEmit -p . && bash scripts/smoke-realism.sh
# renders (mudos, sin voz ni créditos)
python3 tactical/episodes/_gen-realism-v3-3.py /tmp/rv33
npx remotion bundle --out-dir /tmp/rv33-bundle
npx remotion render /tmp/rv33-bundle Tactical3DV2 out/07_fullcourt_v33_raw.mp4 --props=/tmp/rv33/rv33-full-raw.props.json \
  --gl=swangle --concurrency=4 --muted --timeout=300000 --browser-executable=<chrome-headless-shell>
#   props: contact (01), debug (02), motion (03), slow (04), trio (06), full-raw (07), full-ed (08), bench-10-v33 (09)
# tela L2 (Gate 3)
python3 -I ../tools/blender/cloth_bake_l2_v33.py -- public/players3d/e2a_player_off_v32.glb l2.json jersey_l2_morph.glb 90
npx tsx scripts/qc-cloth-l2-v33.mts jersey_l2_morph.glb
# radios anatómicos
python3 -I tools/blender/measure_anat_v33.py -- public/players3d/e2a_player_off_v32.glb
```

Activar V3.3 en un episodio: `"athleteRenderer": "v33"` en el episodio, el plano o el panel. **Por defecto sigue siendo `legacy`.**
Para que una jugada use el compilador en todos sus jugadores: `"v33": "compile"` en la jugada. Sin esa clave, V3.3 solo anima a los jugadores con un guion de compatibilidad V3.2 y el resto usa la pose del motor; el QA lo cuenta como `legacy-fallback`.

**Salida esperada:**
- QC: abc 2 filas, trío 5, 5v5 20.
- Determinismo: PASS.
- test-play del 5v5: 23/23.
- tsc sin errores.
