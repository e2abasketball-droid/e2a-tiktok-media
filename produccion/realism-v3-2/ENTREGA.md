# E2A Realism V3.2 «Human Motion & Cloth Refinement»: entrega

Fecha: 22-11-2026.

- Rama `claude/realism-v3-2`, creada desde `claude/realism-v3-1` (`e014de3`). Sin merge, sin `main`, sin publicar.
- Coste 0 €: ni ElevenLabs ni servicios de pago.
- Carpeta de entrega: `/mnt/project-files/tactical-studio/realism-v3-2/`.

## 1. Resumen honesto

- **Defectos de ropa de la revisión: corregidos en origen y medidos.**
  - Pico del pantalón: el bajo se movía 13,2 cm; ahora 0,85 cm.
  - Casco del tirante: estiramiento 3,39 → 1,89 (P95 1,20).
  - Picos laterales del bajo: 376 frames por encima de 1,3 → 0.
  - La causa principal era que el pantalón usaba los uniforms de tela de la camiseta. A eso se sumaban pesos de piel que saltaban de una fila de vértices a la siguiente.
- **Movimiento.** Hay una biblioteca paramétrica nueva: 9 primitivas, con variación por semilla. Mueve con el mismo código el one-take y un trío (pase, corte, recepción, tiro y closeout).
  - Tiro en suspensión acoplado: carga → impulso → vuelo balístico → release 35 ms antes del ápice → follow-through → aterrizaje → recuperación.
  - Máquina de estados del balón explícita.
  - Pelvis sin picos fuera de los aterrizajes; las palmas a 1,2 cm del balón.
- **Lo que no es mejor.**
  - En el one-take, el clip V3.1 tecleado a mano y la biblioteca V3.2 empatan en número de defectos de QC (27 y 27).
  - V3.2 gana en el release y el agarre, y pierde en roces del balón con el cuerpo (≤ 3,7 cm).
  - La ventaja real de V3.2 es que no hay que teclear cada jugador.
- **Zapatilla: parcial.** Horma de caña media con cuello, contrafuerte, panel de cordones y flexión en la bola del pie. Sin cordones ni lengüeta en geometría.
- **Sin cambios.**
  - Legacy sigue por defecto y con los mismos píxeles: 0 píxeles distintos en 10 frames.
  - V3.1 sigue seleccionable, con los mismos píxeles y su GLB recompilado bit a bit.
  - Ninguna mejora viene de luz o materiales: el test A compara el movimiento con materiales neutros y la misma malla.

## 2. Entregables (en la carpeta de entrega)

| # del brief | Archivo |
|---|---|
| 1 Auditoría de V3.1 | `produccion/realism-v3-2/AUDIT.md` §1 |
| 2 Defectos corregidos con evidencia | `AUDIT.md` §1-2 y `qa/defect_sheet.jpg` (V3.1 y V3.2 en el mismo instante del MP4 exportado, con la métrica) |
| 3 Modelos editables | `assets/e2a_player_{off,def}_v32.blend`, `public/players3d/e2a_player_{off,def}_v32.glb` (+ procedencia), rigs en `src/t3d/realism-v3-2/rigs/`. Las animaciones son código paramétrico (`library.ts`, `clips32.ts`) |
| 4 Deformación de camiseta y pantalón | `videos/04_cloth_slowmo_run_brake_turn_jump.mp4`, `videos/03_testB_character_cloth.mp4`, QC de tela en `QA.md` §4 |
| 5 Recepción y tiro | `videos/05_side_catch_and_shoot.mp4`, `videos/07_debug_contacts.mp4` |
| 6 Legacy / V3.1 / V3.2 | `videos/01_abc_legacy_v31_v32_testC.mp4` (= test C), `videos/02_testA_motion_only.mp4`, `qa/abc_contact_sheet.jpg` |
| 7 Interacción de tres jugadores | `videos/06_trio_O1_O2_X2.mp4` (QC en `QA.md` §3) |
| 8 Informe de calidad | `produccion/realism-v3-2/QA.md`, `METRICS.json`, `qa/*.json` |
| 9 Rendimiento | `QA.md` §7, `bench/` |
| 10 Integración | `produccion/realism-v3-2/INTEGRACION.md` |
| 11 Rama separada | `claude/realism-v3-2` (sin PR ni merge) |
| 12 Reproducción | §3 de este documento |

## 3. Reproducir

```bash
cd /home/user/e2a-tiktok-media
# assets (bpy 5.3 headless; cada variante en su carpeta, las texturas van a <dir>/tex)
python -I tools/blender/build_player.py -- --variant off --rig v3 --garment v32 --body v31 --shoe v32 \
  --out-blend B/e2a_player_off_v32.blend --out-glb B/e2a_player_off_v32.glb \
  --out-rig B/e2a-off-v32.rig.json --out-meta B/e2a_player_off_v32.meta.json        # ídem --variant def
python -I tools/blender/export_qc_mesh.py -- B/e2a_player_off_v32.blend B/v32_off.npz  # malla para el QC de tela
# jugadas y props
python3 template/tactical/specs/_gen-realism-v3-2-abc.py
python3 template/tactical/specs/_gen-realism-v3-2-trio.py
python3 template/tactical/episodes/_gen-realism-v3-2.py <props_dir>
# QC
cd template
npx tsc --noEmit -p . && bash scripts/smoke-realism.sh
npx tsx scripts/qc-realism-v32.mts tactical/plays/realism-v3-2-abc.json --players O1 --motion v32 --json s.json --frames rows.json   # también v31 / engine
npx tsx scripts/qc-realism-v32.mts tactical/plays/realism-v3-2-trio.json --players O1,O2,X2 --motion v32 --json t.json --frames trows.json
npx tsx scripts/qc-realism-v32.mts tactical/plays/realism-v3-2-abc.json --players O1 --motion v32 --props <props_dir>/rv32-abc.props.json --json vis.json  # visibilidad
npx tsx scripts/dump-frames-v32.mts tactical/plays/realism-v3-2-abc.json --renderer v32 --players O1 --fps 30 --out f.json
python -I scripts/qc_cloth_v32.py -- B/v32_off.npz f.json --rig src/t3d/realism-v3-2/rigs/e2a-off-v32.rig.json --v32 --out cloth.json
# render (CPU, SwiftShader)
npx remotion bundle src/index.ts --out-dir <bundle>
npx remotion render <bundle> Tactical3DV2 out/abc.mp4 --props=<props_dir>/rv32-abc.props.json --gl=swangle --concurrency=4 --muted
#   ídem testA, testB, side, slow-run, slow-jump, trio, debug, bench-1-v32, bench-10-v32
ffmpeg -f concat -safe 0 -i slow.txt -c copy out/cloth_slowmo.mp4     # slow-run + slow-jump
python3 scripts/defect_sheet_v32.py out/abc.mp4 defect_sheet.jpg --note 't|etiqueta|V3.1|V3.2' ...
```

Se usó el ejecutable `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`.

## 4. Siguiente paso propuesto

Solo después de la revisión del propietario:

1. Zapatilla con cordones y lengüeta en geometría.
2. Reducir los roces del balón con el cuerpo en el bolsillo y en el bote.
3. Reintentar la tela L2 con pinning y límite de estiramiento.
4. Guiones V3.2 para los 10 jugadores de una jugada táctica real.
