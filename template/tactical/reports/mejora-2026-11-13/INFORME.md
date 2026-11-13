# Tactical Studio: mejora de edición, realismo 3D y QC (2026-11-13)

Rama `claude/project-thread-rray0k`, base `main` b3f0321. Nada fusionado, publicado ni reprogramado. Sin créditos de voz y sin instalar herramientas.

## 1. Qué cambia y qué mejora se ve
- **Franja de luz a 3,2 s eliminada.** Basta con una clave de cámara del episodio (`hook`, 2,9 s: pitch 70 → 60). La cámara pasa por encima del tablero en lugar de atravesarlo. Se mantienen la identidad azul marino y dorado, la apertura detrás del defensor, SCREEN 1/2, las dos lecturas, el guion y la voz.
- **El freeze queda más limpio.** Antes la cámara filmaba a través del cristal tintado durante unos 0,3 s, entre los fotogramas 89 y 97, y la imagen se veía velada (luma de unos 83 a 91). Ahora la luma es estable, de unos 99.
- **Hay un QC nuevo sobre el vídeo real**, que revisa la hoja de contactos por anclas, los transitorios de un solo fotograma, las bandas planas brillantes, los cortes no previstos y la sonoridad. El QC del motor añade dos comprobaciones geométricas: la holgura de cámara respecto a la estructura de la canasta y que no se filme a través del cristal.
- **Prototipo de top-lock más bajo y abierto** entre 19 y 21 s, opcional y aislado.

## 2. Causa de la franja y prueba
- **Causa.** La interpolación del plano `hook`, entre la clave de 2,9 s (órbita pitch 70, yaw 200) y la clave final (yaw 160), deja la cámara detrás del plano del tablero (y 0,9–1,14 m, con el tablero en y = 1,2) y a la altura del tablero (z 3,7–3,9 m). En los fotogramas 96 y 97 la cámara cruza el marco lateral blanco del tablero (x = −0,9), que es la franja. Entre los fotogramas 89 y 97 filma a través del cristal, que es el velo.
- **Prueba por aislamiento.** Se volvieron a renderizar los fotogramas 90–99 ocultando solo el cristal y el marco (parche temporal `isolation-hide-board.diff`, ya revertido). La franja desaparece: la barra mide 0 y la luma es normal. La sonda de cámara (`scripts/camera-probe.mts`) da la posición de cámara en cada fotograma.

  | | Fotograma 96 | Fotograma 97 | Luma 91–95 |
  |---|---|---|---|
  | Antes | barra de 110 px, luma 123 | barra de 12 px | ≈ 83–91 |
  | Después | 0, luma 99 | 0 | ≈ 99 |

  Con pitch 60, en los fotogramas 95–97 la cámara está a z ≈ 4,79 m, por encima del borde superior del tablero (3,95 m).
- **Validación de la corrección:**
  - **Franja:** desaparece en el render completo (clip y comparación).
  - **Legibilidad de la jugada:** los mismos jugadores, anillos y titulares, con encuadre equivalente y algo más alto.
  - **Duración:** 33,344 s, idéntica.
  - **Audio:** la mezcla es idéntica a la de referencia. El residuo tras alinear la ganancia queda en −33 dB, que es solo la codificación AAC. Con la misma ganancia fija de máster de V2 (+2,48 dB) da −14,3 LUFS / −2,3 dBTP, igual que la referencia.
  - **Controles:** pasan todos (sección 4).

## 3. Rutas
Entregables en `/mnt/project-files/tactical-studio/mejora-2026-11-13/`:
- `antes-despues-franja.mp4`: 2,6–4,4 s, primero a velocidad real y después a 25 %.
- `comparacion-franja.jpg`: fotogramas 90, 96 y 100 del render completo, antes y después.
- `aislamiento-tablero.jpg`: prueba con tablero oculto.
- `contact-sheet-stagger-antes.png`, `contact-sheet-stagger-despues.png` y `contact-sheet-flare-control.png`.
- `toplock-antes-despues.mp4` y `toplock-comparacion.jpg`.
- Este informe y `apertura-AB.md`.

En el repositorio (rama `claude/project-thread-rray0k`):

| Commit | Contenido | Archivos |
|---|---|---|
| `839a190` | Corrección | `tactical/episodes/stagger-screen-v2.json` (pitch), `scripts/qc-tactical3d.mts`, `scripts/camera-probe.mts` |
| `6bed73f` | QC de vídeo | `scripts/qc-moments.mts`, `scripts/qc-video.py`, JSON de evidencia en `tactical/reports/mejora-2026-11-13/` |
| `0d5729e` | Prototipo | `src/t3d/rig.ts`, `src/t3d/episode.ts`, `tactical/plays/stagger-b-backdoor-lowlock.json`, `plays.B` del episodio V2, `scripts/pose-compare.mts` |
| (último) | Documentación | este informe y `produccion/tactical/experimentos/apertura-AB.md` |

## 4. Resultados de los controles
| Control | Resultado |
|---|---|
| test-stagger (todas las jugadas, incluida la lowlock) | **88/88 PASS** |
| qc-tactical3d, Stagger V2 antes de la corrección | FAIL en holgura (41 contactos, mínimo 0,00 m en hook a 2,93 s) y FAIL en cristal (8 fotogramas desde 2,97 s); WARN de oclusión |
| qc-tactical3d, Stagger V2 después | **11/11 PASS**: holgura mínima 0,61 m, cristal máximo 0 % |
| qc-tactical3d, controles | hammer-screen 11/11; spain-pick-and-roll 11/11 con WARN de cristal del 4 % (bajo el umbral del 10 %) |
| qc-bounds, Stagger V2 (props por defecto) | **PASS**: 1000 fotogramas, 3394 cajas, 0 violaciones, 12 s |
| qc-video, Stagger master antes | PASS de formato y audio (−14,3 / −2,2); WARN transitorio y WARN banda plana en el fotograma 96 (31,9 % del ancho) |
| qc-video, Stagger después | **PASS, 0 avisos** (−14,3 / −2,3); 19,6 s |
| qc-video, control Flare (14 nov) | **PASS, 0 avisos** (−14,0 / −1,9); 16,4 s |
| tools/tests (tactical_studio y publisher) | 103/103 OK |
| tsc --noEmit | OK |

**El episodio de control pasa.** El nuevo detector salta solo en el caso real y no da falsos positivos en Flare.

Tiempos:
- Render completo: 1700 s.
- qc-video: unos 20 s por vídeo, porque reutiliza el MP4 existente.
- qc-bounds: 12 s.

Avisos sobre los controles:
- Stagger V1 sigue con el mismo fallo de cámara (comparte la clave). No lo he tocado porque no se pidió y ya no se usa.
- elevator-screen falla por duración (65,9 s): es un episodio antiguo y el fallo es previo a esta rama.

**Audio (enmascaramiento).** La mezcla no cambia, así que siguen valiendo las mediciones de `audio-stems-v2.json`:
- Música 24,3 dB por debajo de la voz y −40 dBFS en las pausas.
- 25 tramos de 50 ms en los que un SFX compite con la voz, concentrados en 2,1–3,4 s (impact_big y whooshes).

No propongo cambios de volumen: los márgenes son amplios y no se ha medido un problema de inteligibilidad.

**Lo que no mide el QC:**
- La oclusión entre jugadores.
- El texto sobre un jugador clave.

Ambos figuran como `not_measured` en el informe y se revisan en la hoja de contactos.

## 5. Prototipo, experimento y herramientas
### Prototipo top-lock (19–21 s)
- **Cambio.** Las acciones `topLock` aceptan `pose: 'low'`, que baja la pelvis, ensancha la base, abre la cadera hacia el cortador y pone la mano de negación en la línea de pase. Sin `pose`, el rig es idéntico, así que el resto de jugadas y episodios no cambian. Solo lo usa Stagger V2, mediante `stagger-b-backdoor-lowlock`. La cámara y la luz son las mismas, y se comparan los mismos fotogramas (540–650).
- **Medición (pose-compare):**

  | Métrica | Antes | Después |
  |---|---|---|
  | Pelvis | 0,87 m | 0,81 m |
  | Rodilla | 111° | 103° |
  | Inclinación del tronco | 8,7° | 1,9° |
  | Apertura de cadera | 12° | 19° |
  | Base | 0,53 m | 0,57 m |
  | Mano de negación | 1,50 m | 1,51 m |
  | Fotogramas con brazos cruzando a otro jugador | 14 | 8 |

  - Pies: sin deslizamiento (0,000 mm) y 0 muestras bajo el suelo.
  - Persiste el contacto con O2, que es propio de un top-lock; la métrica es aproximada.
- **Resultado visual:** el cambio es sutil desde esta cámara. X2 se ve algo más bajo, con el tronco más vertical y la cadera más girada hacia el cortador. El brazo de negación sigue cruzando por delante de O2 en algunos fotogramas, aunque menos. Mejora el realismo sin afectar a la lectura. Recomiendo revisarlo en `toplock-antes-despues.mp4` antes de integrarlo. Si se quiere un efecto más visible, el siguiente paso sería un plano más bajo y lateral en ese momento, que es un cambio de cámara y no del rig.
- **Texto «CHASE → THREE».** Propuesta: «TRAIL → OPEN THREE». En inglés de entrenador, *trail* es el término estándar para perseguir por detrás el bloqueo. Fuentes:
  - [FIBA WABC, defensa de stagger](https://wabc.fiba.com/?p=500)
  - [Coach Hoops, top-lock](https://coachhoops.substack.com/p/top-lock)
  - [Hoop Tactics, tipos de bloqueo sin balón](https://hooptactics.net/premium/player/offskilldevelopment/screensoffballtypes.php)
  - [FastModel, Stagger Cuts](https://www.fastmodelsports.com/library/basketball/fastdraw/293705/play-Stagger-Cuts)

  El titular está anclado a la palabra «Chase» de la narración, así que cambiarlo exige cambiar la frase y generar voz nueva. **Queda como propuesta**: no se ha tocado el guion ni se han gastado créditos.

### Experimento de retención
Diseño completo en `produccion/tactical/experimentos/apertura-AB.md`, sin programar:
- **Diseño:** A (detrás del defensor) frente a B (segundo bloqueo visible en menos de 1 s), cruzado en las franjas de 10:00 y 13:00, con un mínimo de 6 pares.
- **Métricas:** a 24 h, 72 h y 7 d.
- **Métrica primaria:** «Stayed to watch» en Shorts.
- **Criterio:** test de signos; adoptar B si gana al menos 5 de 6 pares con una mediana de +3 puntos.

### Herramientas candidatas (ninguna instalada)
1. **[YouTube Analytics API](https://developers.google.com/youtube/analytics/metrics)**
   - Licencia y coste: gratis (cuota de Google).
   - Permisos: OAuth de solo lectura `yt-analytics.readonly` sobre el canal.
   - Datos accedidos: métricas de vídeo propias.
   - Qué aporta: `engagedViews` y `averageViewPercentage` por vídeo, que Metricool no da.
   - Límite: «Stayed to watch» solo aparece en YouTube Studio ([ayuda](https://support.google.com/youtube/answer/12220281)). Mientras tanto, conviene copiarlo a mano una vez por semana.
   - Prueba mínima: una consulta de un Short publicado. Es un éxito si devuelve `averageViewPercentage`. Se revierte revocando el token.
   - **Recomendada** para el experimento.
2. **Blender headless ([bpy 5.3.0 en PyPI](https://pypi.org/project/bpy/))**
   - Licencia y coste: GPL, gratis.
   - Permisos y datos: sin red y sin datos de cuentas.
   - Qué aporta: rig, IK y física más realistas para las poses.
   - Coste de adopción: dependencia pesada (unos 400 MB) y compatibilidad con Python 3.13 por confirmar. Cambiaría el pipeline de render.
   - Prueba mínima: en un venv aparte, renderizar un fotograma del top-lock. Es un éxito si sale en menos de 60 s en este contenedor. Se revierte borrando el venv.
   - **No recomendada todavía**: el rig actual ya cubre los criterios medidos.
3. **[PySceneDetect 0.7.3](https://www.scenedetect.com/)**
   - Licencia y coste: BSD-3, gratis.
   - Permisos y datos: solo el MP4 local.
   - Qué aporta: contraste independiente de los cortes y transitorios de qc-video.
   - Prueba mínima: `scenedetect -i master.mp4 detect-content list-scenes` sobre Stagger antes y Flare. Es un éxito si coincide con los cortes previstos y marca el fotograma 96. Se revierte desinstalando el paquete.
   - **Opcional**: qc-video ya detecta el caso real.

**Metricool.** Su conector no respondía en esta sesión (error 502), así que no he podido volver a probar la lectura por vídeo. Según la verificación del 2026-11-06 (rama P2-A del Knowledge Hub):
- Da IGRE24/IGRE26 (Instagram) y YTVP08 (YouTube), con los que se calcula el % medio visto sin herramientas nuevas.
- No da la retención de Instagram ni las métricas de visionado de TikTok, que llegan nulas.

## 6. Qué se puede integrar ya y cómo revertir cada cambio
| Cambio | ¿Integrar ya? | Revertir |
|---|---|---|
| Corrección de cámara (pitch 60) | Sí. Es la única diferencia visual del vídeo corregido. | `git revert 839a190`, o volver a poner `"pitch": 70` en la clave de 2,9 s |
| Nuevos checks de qc-tactical3d | Sí. Los FAIL solo saltan si la cámara toca la estructura. | El mismo commit, o borrar el bloque marcado como *scene clearance* |
| qc-video y qc-moments | Sí, como paso de aviso: no bloquean salvo por formato y sonoridad. Para el gate diario falta enlazarlo en `tactical_studio.py`, que no he tocado. | `git revert 6bed73f`; no lo usa nada más |
| Top-lock bajo | Tras revisarlo visualmente | `git revert 0d5729e`, o solo `plays.B` → `stagger-b-backdoor` en el JSON y `B: playB` en `episode.ts` |
| «TRAIL → OPEN THREE» | No, requiere voz nueva | — |
| Experimento A/B y herramientas | Requieren decisión | — |

No verificado:
- El vídeo completo con el prototipo: solo se renderizó el tramo de 18–21,7 s (111 fotogramas). Fuera de ese tramo el rig no cambia.
- La lectura actual de Metricool (502).
- La compatibilidad real de bpy con Python 3.13.
