# Informe 3D · laboratorio esquelético del bloqueador (fase 3, 2026-11-18)

Rama local `claude/lab-skeletal-screen-roll` (desde `d1d44b7`), sin push ni merge, sin publicación. Todo es opt-in:
el clip solo se activa en `screen-roll-lab` (`play.skel.O5`). «Observado» = medido en la toma; «corregido a mano» =
valor fijado por mí mirando fotograma a fotograma; «estimado» = inferido o supuesto.

## 1. Referencia

| Original | Archivo | Intervalo | Uso |
|---|---|---|---|
| 5452 | `E2A_26_BLOQUEO_GIRO_Y_ROLL_APROXIMACION_OPUESTA_T02.MOV` | 0.97–4.04 s (92 fotogramas a 29,97 fps; 1920×1080 HEVC 10 bits HLG, tonemap hable para pose) | toma principal: aproximación, frenada, bloqueo, apertura, pivote, primeros pasos |
| 5451 | `E2A_26_BLOQUEO_GIRO_Y_ROLL_AL_ARO_T01.MOV` | 1.25–4.30 s (seguido con MediaPipe, solo control cualitativo) | giro al lado contrario: confirma que el espejo de 5452 es el mismo gesto |

**Decisión de lado (medida, corrige lo dicho en la fase 2).** Con la trayectoria real resuelta, 5452 sin espejo gira
~230° entre la cara al defensor y la dirección de carrera; la jugada de laboratorio necesita ~117°. Integrado tal cual
daba pelvis a 1,1–1,3 m de la pista del motor, interpenetración O5–X1 de −0,275 m y deriva de 50 mm. El espejo
(pivote en el antepié DERECHO, se abre a SU IZQUIERDA, pecho hacia O1, como 5451) deja la diferencia en 15°. El clip
usado es `screen-roll-5452m` (`tools/blender/mirror_motion.py`). El .blend/.glb llevan las dos acciones.

**Ajuste de la jugada de laboratorio (solo `screen-roll-lab`).** O5 llega desde el centro (1,98; 7,85) como en la
toma (los últimos metros laterales y la frenada en dos apoyos gira el pecho hacia X1); X5 empieza por dentro. El roll
corre a 4,2 m/s de punta (antes 5,5) para que el clip conserve una cadencia humana (a 1,8× la zancada salía a 20 m/s
de pie); pase, recepción y bandeja 0,3 s más tarde. `test-play` 20/20.

## 2. Movimiento por fase (tiempos de 5452 sin espejo; en el espejo cambian los lados)

| Fase | Medido (MediaPipe heavy + PnP, f≈1400 px, escala MP→m 1,408) | Corregido a mano | Estimado |
|---|---|---|---|
| Aproximación 0.97–1.30 | trayectoria de raíz, braceo, cadencia | elevación de talón L 0.97–1.20 | escala absoluta (sin referencia métrica en plano; altura del modelo 2,08 m) |
| Frenada 1.30–1.87 | R apoya 1.30, L apoya 1.64 abierto, R ajusta 1.84 escalonado, establecido 1.87 | contactos leídos fotograma a fotograma; talones; raíz baja hasta 6 cm donde el pie fijado no alcanzaba | profundidad de flexión de rodilla (cámara frontal: la pelvis baja poco en el clip, ver §6) |
| Bloqueo 1.87–2.74 | base, giro de cabeza hacia el manejador | manos juntas en la ingle 1.80–2.76 (IK de brazo: MediaPipe pierde las manos ahí) | — |
| Apertura + pivote 2.77–3.44 | R se descarga 2.77, paso de apertura 2.80–3.24; pivote L en antepié 2.84–3.27, guiñada −34°→−177° (143°); talón sube ~3.37; despegue 3.40–3.44; orden de giro cabeza → pecho → pelvis (2.90: −139/−127/−95°) | antepié fijo con guiñada suavizada; claves de talón | — |
| Primeros pasos 3.44–4.04 | L aterriza 3.60, R 3.80; mano derecha alta 3.60–3.80 como objetivo; ~2,8 m/s | contactos releídos en recortes; ancla de raíz (de espaldas la profundidad de piernas no es fiable) | trayectoria del pie en vuelo (sustituida en el motor por curva de mínimo jerk entre apoyos) |

Calidad del clip en la toma: deriva del antepié fijado 1,2–4,5 mm por apoyo (`motion.json/stance_qc`). FK del .blend
frente a `motion.json`: 4,8·10⁻⁵ m.

## 3. Personaje C (malla deformable)

Base MakeHuman (`ara3d-data` 1.1.0, CC0-1.0; los JSON `makehuman-data` de npm llevan etiqueta AGPL3 y **no** se usan
para geometría). Proporciones de 5438/5440 (cabeza ≈0,129 H, estimado). Esqueleto reducido de 21 huesos, pesos MH
colapsados (top-4). Equipación E2A navy `#0B1C3D` + oro `#C9A24D`, número 5, pantalón holgado (30 % de peso de muslo
a cadera), zapatillas por envolvente convexa, calcetines, pelo corto, dedos con flexión relajada. Piel con algo de
SSS en Blender; en three.js PBR rugosidad 0,52. Arreglado hoy: el `sheenColor` blanco del glTF volvía la tela
plateada en three.js (tinte oscuro); nombres de hueso saneados por GLTFLoader (`clavicle.L` → `clavicleL`).

## 4. Integración en el motor

- `src/t3d/skelclip.ts`: función pura del tiempo de jugada. Warp por hitos (aproximación y carrera por distancia
  recorrida, bloqueo lineal entre `screen` y `roll`, velocidad 0,55–1,8×); colocación por fase con rotación alrededor
  del pie plantado (frenada, bloqueo, pivote); antepiés fijados en espacio de jugada con IK de dos huesos; **hundimiento
  suave** (≤6 cm) si una pierna fijada no llega; **vuelo** de mínimo jerk entre apoyos con elevación; límite de
  inclinación de cabeza respecto al pecho [−6°, +20°] (en el .blend la cabeza sigue como la capturó MediaPipe);
  mezclas de 0,18 s con `poseAt`; opciones `from`/`to` del clip.
- `src/t3d/SkinnedAthlete.tsx` + `Scene.tsx`: look B (clip sobre el atleta cápsula vía Pose) y C (glb con
  `delayRender`, huesos por fotograma, sin mixer).
- QC: `scripts/qc-contact.mts` añade deriva acumulada del antepié fijado por apoyo (permite rotación alrededor de ese
  punto), deslizamiento por fotograma y velocidad del tobillo en las mezclas.

## 5. QC

| Prueba | A (rig d1d44b7) | B / C (clip) |
|---|---|---|
| `test-play screen-roll-lab` | 20/20 | 20/20 (mismos datos) |
| deriva máx. del antepié fijado por apoyo | — | 1,45 mm (≤5) |
| deslizamiento por fotograma del punto fijado | 0,00 mm | 1,37 mm |
| holgura mínima O5–X1 (cápsulas) | 0,150 m @2.07 | 0,103 m @2.03 |
| tobillo bajo (<16 cm) en las mezclas | — | 272 mm/fotograma (informativo: fin de la mezcla de salida, pie en vuelo bajo) |
| resto de jugadas (9) | `test-play` y `qc-contact` idénticos a `d1d44b7` | — |

`qc-tactical3d`/`qc-bounds` no aplican (la jugada no está en ningún episodio y el laboratorio no lleva gráficos).

## 6. Reproducir

```bash
cd template
python3 tactical/specs/_gen-screen-roll-lab.py && node --experimental-strip-types scripts/build-play.mts \
  tactical/specs/screen-roll-lab.spec.json tactical/plays/screen-roll-lab.json
python3 scripts/screen-roll-lab-compare-bundle.py           # out/lab3/{tactica,34}-{real,slow}-{A,B,C}.bundle.json
npx remotion bundle src/index.ts --out-dir /tmp/rb
npx remotion render /tmp/rb Tactical3DV2 out/x.mp4 --props=out/lab3/<n>.bundle.json --gl=swangle \
  --browser-executable=$CHROME --concurrency=4 --timeout=180000 --scale=0.5
python3 scripts/screen-roll-lab-compose.py <renders + ref-{real,slow}.mp4> <salida>
# Blender (bpy 5.3): tools/blender/{pose_track,pose_solve,retarget,mirror_motion,export_clip,build_blender}.py
```

Tiempos: ver §8. El panel REF se genera con los fotogramas tonemapeados de 5452, en espejo y con el mismo warp del
clip (hitos alineados); fuera de Git.

## 7. Evaluación honesta

- Lo que mejora: el bloqueador frena en dos apoyos, gira el pecho, se abre con la cabeza delante y pivota sobre el
  antepié sin deslizar (1,45 mm), con mano objetivo alta en la salida. La cadencia es la real.
- Lo que no: la sentadilla del bloqueo es poco profunda (la toma frontal no da bien la profundidad; el modelo de 2,08 m
  amplifica la extensión), los ribetes del cuello/sisa se ven ondulados de cerca, la mezcla de salida cambia de fase
  de zancada (tobillo rápido y bajo) y la cabeza del .blend aún mira hacia arriba (solo se corrige en el motor).
- Coste por gesto con este flujo: seguimiento ~5 min, lectura manual de apoyos/hitos 1–2 h, retarget + correcciones
  1–2 h, integración por jugada 1 h si la geometría de la toma se parece a la jugada (si no, hay que espejar o
  re-trazar la jugada, como aquí). Sirve para **paradas defensivas** (apoyos claros, poco vuelo; tomas 5431/5433 desde
  dos vistas) y es caro para **cambios de mano** con balón: las manos de MediaPipe son ruidosas a 30 fps y el balón
  no se sigue; haría falta una toma de detalle a 60 fps y un modelo de mano propio.

## 8. Tiempos de render y entregables

Remotion 4.0.539, `--gl=swangle --scale=0.5 --concurrency=4`, 540×960, contenedor de CPU (con un render EEVEE en
paralelo durante las tres primeras):

| Vista / velocidad | A | B | C |
|---|---|---|---|
| táctica, real (108 fot.) | 321 s | 277 s | 239 s |
| táctica, 0,4× (225 fot.) | 445 s | 441 s | 457 s |
| tres cuartos, real | 187 s | 190 s | 203 s |
| tres cuartos, 0,4× | 357 s | 356 s | 379 s |

La malla deformable (C) no encarece el render frente a la cápsula. EEVEE en Blender: ~85 s por imagen de 520 px.

Entregables (fuera de Git) en `/mnt/project-files/tactical-studio/3d-animation-lab-2026-11-18/`:
`comparativa_{tactica,34}_{real,lenta}.mp4`, `comparativa_combinada.mp4`, `hoja_hitos_REF_vs_ABC.jpg` (frenada,
bloqueo, apertura, pivote, primer paso), `deformacion_C.png` (EEVEE, bloqueo bajo y giro, frente y perfil),
`blender/e2a_bloqueador_lab.blend` (+ `tex/`), `glb/e2a_bloqueador_screen_roll.glb` (1,29 MB, dos acciones),
`datos_pose/` (MediaPipe bruto 5451/5452, solución de cámara, movimiento corregido y su espejo), `renders/` sueltos.

Lectura de la hoja de hitos: B/C reproducen frenada, apertura con cabeza delante, pivote y mano objetivo alta de REF;
A gira en bloque. En el bloqueo REF está más abierto y más bajo que B/C (ver §7).

## 9. Tomas que faltan

- 5452/5451 desde perfil (90°) para medir la flexión real de rodilla y la caída de pelvis en el bloqueo.
- Una medida conocida en plano (cono a distancia medida o altura real del jugador) para escala absoluta.
- Primeros pasos de la carrera desde lateral a 60 fps (vuelo del pie y despegue).
