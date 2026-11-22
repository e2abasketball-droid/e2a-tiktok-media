# E2A Realism V3.2: QA

Fecha: 22-11-2026. Rama `claude/realism-v3-2`. Todos los vídeos citados se verificaron sobre el MP4 exportado:

- `ffprobe`: códec, resolución, fps, número de frames y duración;
- extracción de frames con `ffmpeg` para las hojas de contactos.

Las métricas de movimiento y de tela se midieron con el **mismo código que pinta el render**:

- `scene32.athleteV32` → `framesV32` / `bonesV3`;
- la malla exportada del `.blend` con el mismo skinning y el mismo shader de tela.

## 1. Herramientas y umbrales

| QC | Comando | Umbral (provisional, de tamaños del deporte) |
|---|---|---|
| Movimiento por frame (120 Hz) | `npx tsx scripts/qc-realism-v32.mts <play> --players .. --motion v32\|v31\|engine [--props ep.props.json] --json s.json --frames rows.json` | Ver lista abajo |
| Tela por frame (30 Hz, malla) | `npx tsx scripts/dump-frames-v32.mts <play> --renderer v32 --players O1 --fps 30 --out f.json` + `python -I scripts/qc_cloth_v32.py -- mesh.npz f.json --rig rig.json --v32 --out q.json` (malla: `python -I tools/blender/export_qc_mesh.py -- player.blend mesh.npz`) | Estiramiento > 1,25 visible, > 1,3 defecto en el bajo; pico de Laplaciano > 2 cm; penetración < −3 cm |
| Hoja de defectos | `python3 scripts/defect_sheet_v32.py abc.mp4 out.jpg --note 't\|etiqueta\|V3.1\|V3.2' ...` | Lee los frames del MP4 exportado |

Umbrales del QC de movimiento:

- deslizamiento del pie < 2 cm por contacto;
- suelo > −1 cm;
- pelvis < 60 m/s² fuera de aterrizajes;
- manos < 400 m/s²;
- hueco de palma con balón ≤ 5 cm;
- balón dentro de una cápsula del cuerpo: más de 1 cm.

## 2. Movimiento: one-take (`realism-v3-2-abc`, O1, 12,5 s), misma malla V3.2 para los tres

| Métrica | Motor (legacy) | V3.1 (clip a mano) | V3.2 (biblioteca) |
|---|---|---|---|
| Filas de defecto (total) | 218 | 27 | 27 |
| Deslizamiento del pie máx. / contactos > 2 cm | 51,6 cm / 28 | 0,6 cm / 0 | 1,6 cm / 0 |
| Suelo mín. | −4,1 cm | 0 | 0 |
| Pelvis: acel. máx. / filas > 60 m/s² fuera de aterrizajes | 671 m/s² / 51 | 232 (7,95 s) / 3 | 237 (8,55 s, aterrizaje) / **0** |
| Muñeca: acel. máx. | 5786 m/s² | 2640 (release 8,275 s) | 994 (recepción del bote, 6,725 s) |
| Hueco de palma con balón (sin botes): mediana / P95 / máx. | −0,9 / 4,7 / 20,4 cm | 1,2 / 1,2 / 4,2 cm | 1,2 / 1,2 / 1,8 cm |
| Balón dentro del cuerpo (muestras a 120 Hz) | 26 | 45 | 86 (máx. 3,7 cm: pecho tras la recepción, muslo en el bote, antebrazo en el bolsillo) |
| Flexión de rodilla máx. | 107° | 98° | 103° |
| Muestras ocluidas (cámara del A/B/C) | — | 0 | 0 |

Lectura honesta:

- En esta jugada, el clip V3.1 tecleado a mano y la biblioteca V3.2 quedan empatados en número de defectos.
- V3.2 gana en dos cosas: el release (la muñeca sin el pico de 2640 m/s²) y el agarre (máximo de 1,8 cm frente a 4,2).
- V3.2 pierde en roces del balón con el cuerpo.
- Lo que V3.2 aporta sobre V3.1 es que **no está tecleado**: la misma biblioteca mueve a los tres jugadores del trío desde 5-9 primitivas por jugador.

## 3. Movimiento: trío (`realism-v3-2-trio`, 7,5 s)

| Jugador | Motor: filas / deslizamiento máx. | V3.2: filas / deslizamiento máx. | V3.2: pelvis máx. | V3.2: hueco de palma (P95 / máx.) | V3.2: balón-cuerpo |
|---|---|---|---|---|---|
| O1 (pasador) | 7 / 11,9 cm | 0 / 0 | 36 m/s² | 1,2 / 1,2 cm | 0 |
| O2 (corte en V, recepción, tiro) | 125 / 40,4 cm | 21 / 0,3 cm | 194 m/s² (impulso del salto, 4,53 s) | 1,2 / 1,2 cm | 60 muestras, ≤ 1,8 cm (antebrazo) |
| X2 (persecución y closeout) | 53 / 23,5 cm | 2 / 0,7 cm | 54 m/s² | — | — |

Causalidad del trío:

- El primer contacto de O2 es a 3,192 s; el pase llega a 3,2 s.
- El balón sale de O1 en `m.pass` (2,7 s), con las palmas en el balón hasta el release (1,2 cm).
- El balón no atraviesa a ningún jugador: los roces se quedan en ≤ 1,8 cm de antebrazo de O2 durante el bolsillo.

## 4. Tela (one-take, O1)

| Métrica | V3.1 completo | Asset V3.2 + movimiento y tela V3.1 (aísla el asset) | V3.2 completo |
|---|---|---|---|
| Camiseta: estiramiento máx. del tirante (t) | 3,39 (3,33 s) | 1,71 | 1,89 (3,27 s); P95 1,20 |
| Camiseta: estiramiento máx. del bajo / frames > 1,3 | 2,15 / 376 | 1,36 / 8 | 1,29 / **0** |
| Camiseta: desplazamiento máx. | 12,7 cm | 12,3 cm | 6,0 cm (límite `maxDisp`) |
| Shorts: estiramiento máx. del bajo / frames > 1,3 | 2,13 / 89 | 1,42 / 11 | 1,07 / **0** |
| Shorts: desplazamiento máx. | 13,2 cm (4,03 s) | 5,5 cm | **0,85 cm** |
| Shorts: P99 del estiramiento | 1,81 | 1,52 | 1,59 (en la entrepierna, que no se ve) |
| Frames con penetración < −3 cm (camiseta / shorts) | 9 / 19 | 9 / 11 | 8 / 8 |

Observación visual: en la frenada con el muslo izquierdo alto (3,6 s), la pernera ancha deja ver el ribete del bajo en escorzo. El QC no marca estiramiento en el bajo (1,03); el estiramiento del pantalón está en la entrepierna. Se deja anotado para la revisión.

## 5. Legacy y V3.1 sin cambios, determinismo

- **Regresión de píxeles** (`qa/pixel-regression.txt`).
  - Se compararon el bundle de V3.1 (el de los renders V3.1 entregados) y el bundle V3.2.
  - Props `rv31-legacy` y `rv31-v31`, frames 0/100/148/245/360.
  - Resultado: **0 píxeles distintos** en los 10 pares.
- **Build**: `--garment v31 --shoe v31` recompilado tras los cambios. GLB sha `dce47ae8…` y rig JSON idénticos a los instalados.
- **Smoke de legacy** (`bash scripts/smoke-realism.sh`):
  - 12/12 jugadas legacy idénticas a `d700987`;
  - test-play y QC de contacto/recepción/mano a mano en PASS;
  - rc 0.
- **`npx tsc --noEmit`**: sin errores.
- **Determinismo**: dos stills en frío del mismo frame dan sha256 idéntico.
  - A/B/C, frame 245: `63c13fd3…`.
  - Trío, frame 140: `160ef6f4…`.
- **`scripts/test-play.mts` en las jugadas de prueba V3.2**. Sus FAIL son por diseño de las pruebas, no de V3.2:
  - «5 atacantes y 5 defensores»: las pruebas tienen 2 o 3 jugadores.
  - Aceleración del track > 22 m/s² en el plant: abc 32,6 m/s², trío 36,7 m/s². Es la frenada del track autorado. El one-take V3.1 da los mismos 2 FAIL.
  - «O2 libre»: el closeout lo cubre a propósito.

## 6. Renders (verificados con `ffprobe` sobre el MP4)

| Archivo | Contenido | Frames / duración | Tiempo de render | s/frame | Pico RSS |
|---|---|---|---|---|---|
| `01_abc_legacy_v31_v32_testC.mp4` | A/B/C = test C (visual completo) | 375 / 12,5 s | 913,5 s | 2,44 | 5,5 GB |
| `02_testA_motion_only.mp4` | Test A: movimiento motor / V3.1 / V3.2 con materiales neutros, misma malla V3.2 | 375 / 12,5 s | 731,4 s | 1,95 | 4,8 GB |
| `03_testB_character_cloth.mp4` | Test B: malla y tela V3.1 frente a V3.2, mismo movimiento V3.2 | 375 / 12,5 s | 700,8 s | 1,87 | 4,5 GB |
| `04_cloth_slowmo_run_brake_turn_jump.mp4` | Tela a 0,5×: carrera, corte, parada en 1-2, recepción, pivote (8,8 s) y tiro y aterrizaje (4,6 s), encuadre cerrado | 402 / 13,4 s | 516,5 + 238,2 s | 1,96 / 1,73 | 3,6 GB |
| `05_side_catch_and_shoot.mp4` | Vista lateral de la recepción y el tiro, del lado del brazo de tiro | 162 / 5,4 s | 268,0 s | 1,65 | 3,5 GB |
| `06_trio_O1_O2_X2.mp4` | Pase, corte en V, recepción, frenada, tiro, persecución y closeout | 225 / 7,5 s | 345,4 s | 1,54 | 3,7 GB |
| `07_debug_contacts.mp4` | Pies apoyados (verde) o en el aire (rojo), palmas, estado del balón | 162 / 5,4 s | 266,7 s | 1,65 | 3,6 GB |
| `bench/bench-{1,10}-v32.mp4` | 2 s con 1 o 10 atletas V3.2 | 60 / 2 s | 105,4 / 198,4 s | 1,76 / 3,31 | 3,3 / 4,3 GB |

Todos los MP4 son h264, 1080×1920 y 30 fps. Las salidas de `ffprobe` están en `bench/` de la carpeta de entrega.

## 7. Rendimiento (10 jugadores)

| Benchmark de 2 s, mismo encuadre | Legacy | V3.1 | V3.2 |
|---|---|---|---|
| 1 atleta | 104,3 s | 105,4 s | 105,4 s |
| 10 atletas | 164,1 s | 192,4 s | 198,4 s (+21 % sobre legacy, +3 % sobre V3.1) |
| Pico RSS con 10 | 3,4 GB | 4,2 GB | 4,3 GB |

- CPU del movimiento V3.2: 2,0 ms por jugador y frame (`motionV32`) más 1,6 ms de huesos.
- Con 10 jugadores son unos 36 ms por frame: no es el cuello de botella. El coste está en el rasterizado por software.
- Las cifras de legacy y V3.1 son las del benchmark V3.1, en la misma máquina, con props idénticas salvo el renderer.
- No se afirma tiempo real.

## 8. Lo que no se cumple o queda parcial

- **Zapatilla**: parcial. La horma se lee como zapatilla de baloncesto de caña media en el render lateral y en el lento, pero no tiene cordones ni lengüeta en geometría. Se ve en `qa/shoe_v32_blender.png` y `04_cloth_slowmo…`.
- **Tela**:
  - Sigue siendo procedural (muelle en el shader más correctivos). L2 no se reintentó.
  - En la frenada con el muslo alto (3,6 s) la pernera ancha deja ver el ribete del bajo. Es geometría de pantalón ancho, no un pico: el bajo se estira 1,03.
- **Balón contra cuerpo**: roces de hasta 3,7 cm, que son las cápsulas aproximadas del QC.
  - Pecho justo después de la recepción.
  - Muslo durante el bote.
  - Antebrazo de tiro con el balón en el bolsillo.
- **Muñeca en la recepción del bote**: 994 m/s² (6,725 s). Es un impulso de contacto, por encima del umbral de 400.
- **Oclusión de ~6,75 s**: resuelta por la coreografía de la jugada de prueba (O2 se aparta tras el pase), no por el movimiento. QC de rayos: 0 muestras ocluidas en V3.1 y en V3.2 con la misma jugada.
- **Encuadre del A/B/C**:
  - Los paneles son de 1080×640. La cámara de seguimiento deja sitio para el salto, así que el cuerpo ocupa ~45 % del alto del panel.
  - Para el detalle están el test B, el lento y la vista lateral (cuerpo al 70-90 % del alto).
