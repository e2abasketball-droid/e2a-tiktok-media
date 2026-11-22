# Realism V3 — QA report (gates A–E, §12)

Rama `claude/realism-v3`, 22-11-2026. Todo lo que sigue se midió de verdad; si algo no se pudo medir, se indica.

La métrica automática sirve para detectar fallos. **No sustituye la revisión visual**, que está al final del informe.

Fixture del one-take (`template/tactical/plays/realism-v3-onetake.json`):
- 12,5 s, 375 frames a 30 fps.
- O1 es el atleta. O2 es el pasador, situado en la esquina para que el balón no salga de la nada.
- Los dos renderers usan **la misma jugada, la misma cámara y las mismas luces**. Solo cambia el flag `athleteRenderer`.

El informe recoge el estado final, tras la **segunda pasada** que pidió el coordinador:
- silueta de la ropa;
- envoltura de los dedos sobre el balón;
- peso visible en la frenada;
- side-by-side más cerrado.

Los números de la primera pasada aparecen como "1ª" cuando ayudan a la comparación.

---

## Gate A — Estructura del asset (`qa/glb.json`)

| GLB | Bytes | Triángulos | Vértices | Primitivas (draw calls por jugador) | Materiales | Imágenes | URIs externas | Huesos | Morph targets |
|---|---|---|---|---|---|---|---|---|---|
| `e2a_player_off_v2.glb` (legacy) | 1 320 852 | 29 318 | 15 907 | 11 | 8 | 2 (embebidas) | 0 | 21 | 0 |
| `e2a_player_def_v2.glb` (legacy) | 1 298 848 | 29 386 | 15 945 | 11 | 8 | 2 | 0 | 21 | 0 |
| `e2a_player_off_v3.glb` | 1 471 924 | 28 662 | 15 580 | 11 | 8 | 2 | 0 | **27** | **6** |
| `e2a_player_def_v3.glb` | 1 457 584 | 28 670 | 15 584 | 11 | 8 | 2 | 0 | **27** | **6** |

- **Huesos.** Son los 21 de `e2a-player-v1` más `fingers1`, `fingers2` y `thumb` en cada mano.
- **Morph targets:** `knee.L/R`, `elbow.L/R`, `hip.L/R`.
  - En el cuerpo son delta-mush.
  - `hip.*` se traslada también a los shorts.
  - Delta máximo en bind: rodilla 8,0 cm, codo 3,7 cm, cadera en shorts 2,4 cm.
- **Pesos de los correctivos en el one-take (`qa/qc-realism-v3.json`):**

  | Correctivo | Peso máx. | Frames con peso > 0,25 |
  |---|---|---|
  | Rodilla L / R | 0,89 / 0,92 | 335 / 350 |
  | Codo L | 1,0 | 168 |
  | Cadera L / R | 1,0 / 1,0 | 228 / 271 |

- **Clonado.** Se hace con `SkeletonUtils.clone` por jugador, con clave `v3:<id>`.
  - El benchmark de 10 atletas se renderiza con 10 esqueletos independientes (5 con kit off y 5 con kit def).
  - Comprobado en un frame: `qa/benchmark.txt` y el vídeo bench-10.
- **Determinismo del build legacy.** `build_player.py --garment v2` sigue dando el sha `f46cb06d…` después de todos los cambios (comprobado tres veces).
- **Licencias:** ver `LICENCIAS_V3.md`. Hay un hueco en el registro, que está documentado.

**Resultado: PASS.**

---

## Gate B — Movimiento

Comandos:
- `npx tsx scripts/qc-realism.mts tactical/plays/realism-v3-onetake.json [--v3]`. El modo `--v3` es nuevo: aplica `bonesV3`, la capa de peso y los morphs.
- `test-motion`: 7/7.
- `test-play`: 12/13. El único fallo es "5 atacantes y 5 defensores", que no aplica a un fixture de 2 jugadores.

| Check | Legacy | V3 |
|---|---|---|
| foot_plant | WARN: peor deriva 4,4 cm (O1 L @6,67 s), 1 apoyo > 2 cm | **igual (4,4 cm)**: la capa de peso de V3 re-resuelve las piernas por IK sin mover los tobillos |
| root_foot | PASS: 688°/s, 0 frames deslizando | igual |
| ik_reach | WARN: brazo saturado en el 10 % de frames-mano; 0 codos ni rodillas invertidos | igual |
| **Peso en frenada y corte (nuevo, V3)** | sin capa extra; el motor ya baja algo la cadera en la frenada | caída de cadera de hasta **6,0 cm** (@2,33 s); inclinación del tronco de hasta **11,5°** (@2,4 s); 16 frames con caída > 2 cm |

**Limitación de la capa de peso.** El pico cae al inicio de la deceleración (2,2–2,6 s). En el apoyo del corte (3,3 s) la capa ya está casi a 0 por dos motivos:
- la velocidad media de la ventana es baja;
- la aceleración del nuevo impulso no es una frenada.

Se ve en `qa/brake_weight_sbs_close.jpg`: hay diferencia a 2,33 y 2,5 s, y ninguna a 3,3 s.

**Resultado: WARN.**

---

## Gate C — Balón y contacto

Comandos: `qc-realism`, `test-ball` (6/7) y `scripts/qc-realism-v3.mts` (nuevo).

| Medida | Legacy | V3 1ª pasada | **V3 final** |
|---|---|---|---|
| ball_continuity | PASS: 3,75 cm / 1,58 m/s, 0 violaciones | igual | igual |
| swept_ball | PASS: 1,6 cm en la cabeza @7,729 s | FAIL 2,1 cm | **FAIL 2,1 cm**: la corrección de cabeza de +7° adelanta la cabeza hacia el release |
| contact_pose (palma, del motor) | FAIL: palma hundida 6,4 cm @7,37 s; la más cercana a 27,2 cm @7,27 s | igual | igual |
| test-ball "mano en el balón sostenido" | FAIL: 0,288 m @7,27 s | igual | igual |
| Punta ↔ superficie del balón, 28 frames sostenidos a dos manos | mediana \|gap\| 38,2 mm; 5/28 frames ≤ 10 mm | 20,6 mm; 7/28 | **7,4 mm; 17/28 frames ≤ 10 mm**; p95 6,9 mm |
| Pulgar ↔ superficie (mediana) | −39,9 mm (dentro del balón) | +0,4 mm | +0,4 mm |
| Palma ↔ superficie (mediana) | −17,3 mm: el motor coloca la palma dentro del balón | igual | igual |

**Qué cambia en V3 final.** La envoltura usa una búsqueda 2-D, con un ángulo de nudillo y otro de articulación media. La articulación media y la punta quedan sobre la superficie.

**Lo que no se arregla.** La palma la coloca el motor (`rig.ts`), igual para ambos renderers. En 11 de los 28 frames la mano está demasiado hundida o demasiado lejos para que los dedos compensen.

**Resultado: FAIL**, compartido con legacy. V3 mejora claramente la parte de dedos.

---

## Gate D — Ropa

Comandos: `qc-realism` (cloth_clip, cloth_stability) y revisión visual.

| Check | Legacy | V3 1ª pasada | **V3 final** |
|---|---|---|---|
| Piel fuera de la ropa > 1 cm durante > 3 frames | 2,2 cm @8,00 s | 1,9 cm (17,1 cm antes de arreglar los pesos del tubo) | **1,6 cm @11,33 s** |
| Brazo dentro de la camiseta > 1 cm | 5,0 cm @4,93 s | 4,9 cm | 5,0 cm @4,93 s |
| Shorts atravesando la camiseta | 3,2 cm @3,33 s | 0,7 cm | **2,7 cm @3,33 s**: peor que en la 1ª pasada, por las perneras más holgadas y la camiseta ajustada a la cadera |
| Estiramiento de aristas de la camiseta, p99,9 / máx | ×2,28 / ×3,69 | ×2,31 / ×3,45 | ×2,32 / ×3,44 |
| Estiramiento en la zona del número, máx | ×1,72 | ×2,08 | **×1,61** |
| Aceleración del bajo frente a la pelvis, p99 / máx | 19,1 / 69,1 m/s² | 19,0 / 70,0 | **17,3 / 59,3 m/s²** |

Cambios de geometría en la segunda pasada (`build_player.py --garment v3`):
- **Camiseta.**
  - Cae desde los hombros y se ajusta hacia la cadera: el radio objetivo pasa del pecho al cuerpo + 2,2–3,6 cm.
  - Ya no hay panel de espalda recto ni aro dorado en el bajo (el ribete queda solo en cuello y sisas).
- **Shorts.**
  - Perneras más holgadas: holgura de 1,6 cm en la entrepierna a 5,4 cm en el bajo.
  - La banda de tela libre es más larga: `_E2A_HEM` 0,9 en los últimos 18 cm.
  - La espalda de cada pernera cae recta desde la sección más ancha del glúteo.
  - El asiento hace de puente sobre el pliegue glúteo (máximo 3 cm de relleno).

**Resultado: FAIL**, en ambos renderers.

---

## Gate E — Render y producción

| Check | Resultado | Evidencia |
|---|---|---|
| `tsc --noEmit` | PASS (rc 0) | `qa/regress-poses.txt` |
| Hash de poses legacy (`regress-poses`) | PASS: 12/12 jugadas idénticas a d700987; 2/2 Chicago V2 idénticas a 8e418e9 | `qa/regress-poses.txt` |
| Píxeles legacy: bundle de 4682d58 frente al bundle final, sin flag | **PASS: 8/8 stills con hash idéntico, maxdiff 0**. Frames: chicago-action-v3 f200/f600, chicago-action-v2 f300/f700, zona-2-3-zone-v2 f300, blob-screen-the-screener-v2 f300 y one-take legacy f95/f350 | `qa/pixel-regression.txt` |
| Mismo frame dos veces (V3, en frío, orden 301 → 12 → 129 → 12) | PASS: f12 da el mismo sha256 las dos veces | `qa/seek.txt` |
| Still en frío frente al mismo frame alcanzado en secuencia | casi idéntico: 6 / 3 / 12 píxeles distintos de 2 073 600 (máx. 17/255). Son píxeles sueltos de gradas y suelo (filas 600–900), no del atleta. Tolerancia declarada: ≤ 20 píxeles y ≤ 20/255 | `qa/seek.txt` |
| Formato de los MP4 | los 6 vídeos: 1080×1920, 30 fps, 375 frames, 12,5 s, h264, sin audio (`ffprobe`) | `qa/videos.txt` |
| Copia en project-files | el almacenamiento compartido cambia el contenedor (unos 6 KB). El vídeo decodificado es idéntico: md5 de frames igual en origen y copia (`b1b514…` legacy, `709045…` hero) | sesión |

### Tiempos de render del one-take

375 frames, `--concurrency=4`, 4 CPU sin GPU (swangle).

| Vídeo | Tiempo real | ms/frame |
|---|---|---|
| baseline_legacy | 774 s | 2064 |
| prototype_v3 (final) | 561 s | 1496 |
| side_by_side (2 escenas) | 669 s | 1784 |
| side_by_side_close (2 escenas) | 732 s | 1953 |
| hero_jersey_closeup (V3) | 662 s | 1766 |
| hero legacy | 658 s | 1755 |

Los tiempos varían con la carga de la máquina: el legacy se renderizó mientras corrían a la vez scripts de QA, así que no indica que V3 sea más rápido.

### Benchmark de 1/2/5/10 atletas

Condiciones: 60 frames (2 s), 1080×1920, cámara fija abierta, mismo movimiento desplazado, bundle final, en serie y sin otras tareas. Datos en `qa/benchmark.txt`.

| Atletas | Legacy, tiempo real (s/frame) | V3, tiempo real (s/frame) | V3 / legacy | RSS pico del sistema legacy / V3 (MB)\* |
|---|---|---|---|---|
| 1 | 112,8 s (1,88) | 114,8 s (1,91) | +1,8 % | 5800 / 5949 |
| 2 | 112,5 s (1,88) | 119,6 s (1,99) | +6,3 % | 5850 / 6037 |
| 5 | 132,0 s (2,20) | 145,2 s (2,42) | +10,0 % | 5873 / 6292 |
| 10 | 156,9 s (2,62) | 191,4 s (3,19) | **+22,0 %** | 6084 / 6857 |

\* Cómo se mide el RSS:
- Es la suma de todos los procesos chrome, node y ffmpeg de la máquina, incluidos los del propio agente.
- En reposo, esa suma era de 2669 MB.
- El render atribuible es aproximadamente el pico menos 2,7 GB: unos 3,1 GB con 1 legacy y unos 4,2 GB con 10 V3.
- No se midió la VRAM porque no hay GPU.

El tiempo real incluye el arranque del navegador y la carga del bundle, unos 100 s fijos. El coste marginal por atleta es pequeño en legacy y mayor en V3 por:
- los morphs;
- la búsqueda 2-D de dedos;
- la capa de peso, que llama a `sample()` 9 veces por jugador y frame.

**Estimación con 10 atletas en 30–40 s (900–1200 frames):** unos 48–64 min en legacy y unos 58–77 min en V3 en esta máquina. Es una extrapolación lineal de 3,19 s/frame, no una medición.

---

## Matriz de incidencias `[segundo, player, tipo, gravedad, causa probable, arreglo, evidencia]`

| # | Segundo | Player | Tipo | Gravedad | Causa probable | Arreglo | Evidencia |
|---|---|---|---|---|---|---|---|
| 1 | 2,0–2,2 (sprint) | O1 (V3) | Pernera levantada que dejaba ver el muslo "roto" | Alta | El tubo V3 llevaba un 30 % de peso de cadera y se quedaba atrás; además se ocultaba la piel bajo el short | **ARREGLADO**: pesos de muslo en el tubo y 10 cm de piel conservada. QC: 17,1 → 1,6 cm | `qa/sprint_fix_before_after.jpg` |
| 2 | 4,67 | O1 | Pico de velocidad del balón (22,4 m/s) en la recepción | Media (motor) | `catchV2: 2` es discontinuo si el receptor sigue moviéndose | Se quitó `catchV2` del fixture. Pendiente arreglarlo en el motor | sesión (`bspeed.mts`) |
| 3 | 4,6–5,0 y 10,5–12,5 | O1 | Abultamiento del glúteo en los shorts con la cadera flexionada | Media | LBS en el asiento + shorts todavía ajustados al cuerpo | PARCIAL: correctivo `hip.*`, espalda de las perneras cayendo recta y puente del asiento. Menos visible que en la 1ª pasada, pero sigue | `contact_sheets/contact_hero_v3.jpg` f140, f351 |
| 4 | 7,27–7,37 | O1 | Palma 6,4 cm dentro del balón / una mano a 27 cm en el gather | Media (motor) | El IK de brazos del motor no respeta la superficie del balón | Pendiente: IK de muñeca V3 contra la superficie | qc contact_pose, test-ball |
| 5 | 7,729 | O1 (V3) | El balón roza la cabeza 2,1 cm en el release | Baja | +7° de barbilla abajo en V3 | Pendiente: anular la corrección de cabeza con el balón por encima de los ojos | qc swept_ball |
| 6 | 3,33 | O1 (V3) | Shorts atravesando la camiseta 2,7 cm | Media | Perneras más holgadas + camiseta ajustada a la cadera | Pendiente: subir la holgura mínima entre camiseta y cintura del short en la zona frontal | qc cloth_clip |
| 7 | 3,3 (apoyo del corte) | O1 (V3) | No hay peso visible en el apoyo | Media | La capa usa la deceleración de la pista, que en el apoyo es casi nula | Pendiente: añadir un término de "carga en el apoyo" leído de los eventos de pie del motor | `qa/brake_weight_sbs_close.jpg` |
| 8 | todo | O1 | La cara y el cuerpo siguen leyéndose como maniquí (cara neutra, piel sin poros, pelo como casquete) | Alta (estética) | Sin MPFB ni texturas de piel; el cuerpo MakeHuman es CC0 base | Bloqueado en este entorno (descarga MPFB 403, sin pintado de texturas) | contact sheets |
| 9 | — | fixture | `test-play` "5v5" falla | Info | El fixture tiene 2 jugadores a propósito | — | `qa/tests.txt` |
| 10 | — | clips | Los jugadores con clip esquelético (`spec`) siguen en legacy aunque el flag sea `v3` | Info | No hay clips V3 de 27 huesos | Pendiente: retarget | `Scene.tsx` |

---

## Revisión visual (honesta)

Fuentes:
- `contact_sheets/contact_sbs_close.jpg`, `contact_hero_v3.jpg` y `contact_hero_legacy.jpg`;
- `qa/captures_legacy_vs_v3.jpg`;
- `qa/brake_weight_sbs_close.jpg`.

### Mejora objetiva, visible en primer plano y en el side-by-side cercano

- **Dorsal.** Más nítido, con keyline; la zona del número se estira menos (×1,61 frente a ×1,72).
- **Camiseta.**
  - Ya no es una caja: la espalda sigue el cuerpo y se estrecha hacia la cadera.
  - Desaparece el aro rígido del bajo.
  - Sin las "arrugas-bulto" de legacy en la espalda.
- **Shorts.**
  - Perneras separadas y holgadas que se mueven con la tela.
  - Sin el hueco del muslo al esprintar, defecto que legacy también tiene en f60.
- **Dedos.** Envuelven el balón en bote y en el gather (mediana de 38 → 7 mm). El pulgar ya no atraviesa el balón.
- **Frenada (2,2–2,6 s).** La cadera baja y el tronco va atrás de forma visible en el side-by-side cercano.

### Lo que sigue pareciendo artificial

- **Cuerpo y cara.**
  - Cara sin rasgos ni textura.
  - Pelo en casquete.
  - Piel sin variación.
  - Con la cámara del one-take original (abierta), legacy y V3 se ven casi iguales.
- **Shorts todavía pegados al glúteo** en cuclillas (11,7 s), aunque menos.
- **Camiseta.** Ahora parece más una camiseta ajustada que una de baloncesto holgada. Es el compromiso que deja el criterio "drape + taper" sin simulación de tela.
- **Apoyo del corte (3,3 s).** No transmite más peso que legacy.
- **Gather (7,1–7,4 s).** Una mano se separa del balón en ambos renderers (motor).

**No es fotorrealista ni está listo para producción.** Es un prototipo detrás de un flag, con mejoras medibles en dedos, ropa y peso en la frenada, y con defectos abiertos documentados.
