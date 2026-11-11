# Piloto 01 — Elevator Screen: Two Ways to Punish the Defense

Informe de producción · 2026-11-11 · rama `claude/project-thread-iqip2t` (sin merge) · **no publicado**

## A. Vídeo

- `elevator-screen-pilot01.mp4`: 1080×1920, 60 fps, H.264 yuv420p, AAC 48 kHz, ~75,5 s, máster a −14 LUFS / −1,5 dBTP.
- Lo produce el código de la rama (composición `Tactical`). El MP4 no está en Git; se entrega como archivo.
- Valores medidos en el MP4 final: ver «F. Calidad».

## B. Guion

Es el guion aprobado, palabra por palabra (Hook / Setup / Case A / Case B / Conclusión). No se ha cambiado ni una palabra.

- Narración ElevenLabs con la voz **Deuce** (eleven_v4), en **una sola toma** (≈1.150 créditos, autorizados).
- Tiempos por palabra con Scribe (0 créditos).
- Se insertaron 10 pausas para respirar entre bloques. La voz nunca se acelera.
- Resultado: 63,0 s de voz pasan a 73,0 s.

## C. Storyboard frente a render

| Escena pedida | Plano(s) en el render | Qué se ve | Estado |
|---|---|---|---|
| 01 Hook, POV del defensor, «TRAPPED.» | s01-hook (0–7,9 s) | Cámara a la altura de los ojos detrás de X2. Las «puertas» (O4/O5) se cierran. Freeze + «TRAPPED.» | ✔ |
| 02 Rewind + grúa a cenital, «THE ELEVATOR SCREEN» | s02-reveal | Rebobinado visible y grúa del POV a la vista cenital. Título con «ELEVATOR» en dorado | ✔ |
| 03 Setup | s03-setup | Cenital → plano cercano del hueco. Anillos en los bloqueadores, pasillo del hueco, ruta de O2, barra de tiempos y freeze | ✔ |
| 04 Caso A, «CASE A — CHASE» / «OPEN THREE» | s04-caseA, s05-replayA, s06-shotA | Tiempo real en vista broadcast. Repetición cenital con estela de X2, puertas, separación, línea de pase y espacio abierto. Tiro a nivel de pista con arco y sello «OPEN THREE» | ✔ |
| 05 Transición, «BUT WHAT IF THE DEFENSE SWITCHES?» | s07a-rewind, s07b-fork | Rebobinado al inicio y bifurcación «SAME START», con flecha de cambio de X5 | ✔ |
| 06 Caso B, «CASE B — SWITCH» / «SLIP TO THE RIM» | s08-caseB-read, s09-slip | Lectura (O5 ve el salto de X5), freeze, carril abierto, pase picado y bandeja. Sello «SLIP TO THE RIM» | ✔ |
| 07 Pantalla partida, CHASE vs AGGRESSIVE SWITCH | s10-compare | Dos vistas sincronizadas con la misma salida y resultados «OPEN THREE» / «SLIP TO THE RIM» | ✔ (ver limitaciones) |
| 08 «READ THE DEFENSE.» / «HOW WOULD YOU GUARD IT?» + logo | s11-takeaway | Diagrama de decisión, títulos finales y logo E2A discreto | ✔ |

Las capturas de cada escena, sacadas del MP4 final, están en la hoja de contactos y en `capturas/`.

## D. Técnicas de edición

Se cargó la skill `e2a-video-editing-intelligence` (SKILL.md) y se consultó la biblioteca v1.0.0. Se ejecutó APPLY sobre una réplica del storyboard en formato Pro (`elevator-screen.storyboard-proxy.json`), porque APPLY solo admite ese formato.

| ID | Nombre | Decisión de la skill | Dónde | Cambio | Resultado visual | Validación |
|---|---|---|---|---|---|---|
| tec-0005 | Barrido rápido al cambiar de bloque | **Elegida** (0,25) | s04 (entrada Caso A), s07b (bifurcación), s08 (entrada Caso B) | Transición cut → **whip** | Barrido con desenfoque de movimiento al cambiar de bloque | Regla de la skill: escena ≥ 2 s y ≥ 5 escenas (11 escenas, la más corta 3,4 s) ✔. QC R1–R7 sobre el MP4 |
| tec-0001 | Cifra que crece en plano largo | Descartada («evitar en tactical») | — | — | — | — |
| tec-0004 | Gancho legible sin sonido con cambio antes de 1 s | Descartada («evitar en tactical») | — | — | — | — |
| tec-0003 | Cierre con pregunta y logo en silencio | Descartada (−0,5) | — | — | — | — |
| tec-0002 | Titular con una palabra clave en dorado | Descartada (−3,25) | — | — | — | — |

**Uso fuera de la selección de la skill.** Los titulares con una palabra en dorado («THE **ELEVATOR** SCREEN», «CASE A — **CHASE**») y el cierre con pregunta + logo **no** los eligió la skill: los pidió el brief (escenas 02, 04 y 08). Su puntuación en la biblioteca era negativa para historias tácticas, y aquí queda dicho.

Técnicas propias del motor (no vienen de la biblioteca): POV del defensor, rebobinado visible, freeze con anotaciones, repetición desde otro ángulo, cámara lenta en el pase y el tiro, flash en la repetición, pantalla partida sincronizada y barra de tiempos.

**Validador de la skill.** Daba errores Q10 (fuentes vacías, final «question» desconocido) porque la réplica Pro no es un episodio Pro real, y un aviso Q1 por duración (el brief pide 75–90 s). Q9 avisaba de cortes a mitad de palabra; se corrigió y se comprobó por script.

## E. Arquitectura

Ver `template/TACTICAL.md`. Resumen:

- **Datos:** las jugadas (`tactical/plays/*.json`) y la edición (`tactical/episodes/*.json`).
- **Componentes:** `TacticalCourt`, `Basket`, `PlayerAvatar`, `TacticalView`, los overlays de pista y de pantalla, la cámara (presets, follow, pov) y el remapeo de tiempo.
- **Pipeline:** `scripts/render-tactical.sh` (tests → voz → música → props → QC de motor → render → máster).

**Es 2.5D, no 3D real:** pista en perspectiva real con jugadores planos («billboards») ordenados por profundidad.

## F. Calidad

| Control | Resultado |
|---|---|
| Tests tácticos (60 comprobaciones, cubren los 12 puntos del brief) | **60/60** (`tactical-tests.json`) |
| QC de motor, fotograma a fotograma (jugadores en cuadro, cámara sin saltos, reloj de juego) | **12/12 planos ok** (`qc-engine.json`) |
| Formato del MP4 | ver `qc-final.txt` |
| QC de la skill R1–R7 | ver `qc-final.txt` |
| Fotogramas negros / congelados no intencionados | ver `qc-final.txt` |
| Revisión visual (render v1 → v2) | ver errores 13–14 |

**Errores encontrados y corregidos** (no se oculta ninguno):

1. Tirones de aceleración y cuerpos solapados en las jugadas → retiming, splines C2 y reajuste de X2/X4/X5/O4/O5.
2. Fotograma entero naranja: la cámara POV estaba pegada al aro → POV más atrás y la canasta se omite si está a menos de 1,2 m.
3. POV demasiado cerca y con anillos en el suelo → reencuadre y sin anillos en el POV.
4. La barra del poste cruzaba la vista broadcast → poste eliminado.
5. Etiquetas superpuestas → recolocadas y cámaras más cerradas.
6. Cortes a mitad de palabra (Q9 de la skill) → offsets ajustados.
7. El ancla «screens,» apuntaba a la primera aparición → «behind the screens».
8. Claves de remapeo de s04 desordenadas → corregidas.
9. La dirección del POV giraba durante el rebobinado → POV congelado (`at`).
10. Grúa y movimientos demasiado rápidos según el QC de motor → alargados; s07a con cámara fija y corte barrido.
11. Nombres de parámetros de overlays chocaban con from/to → renombrados.
12. El primer render usó props antiguas → se paró y se repitió.
13. (Revisión del v1) Pantalla partida pequeña, con mucho fondo vacío → paneles más altos (960 → 1070 px) y cámara más cenital.
14. (Revisión del v1) La barra de tiempos tocaba los subtítulos → subida 60 px.

## G. Limitaciones

- 2.5D: los jugadores son figuras planas. No hay oclusión real entre cuerpos más allá del orden por profundidad, ni iluminación 3D.
- Pantalla partida: cada panel mide 540 px de ancho, así que los jugadores se ven pequeños en móvil. Las etiquetas se reducen.
- Las jugadas están escritas a mano (coordenadas en metros); no salen de vídeo real ni de tracking.
- La biblioteca de técnicas solo tenía 5 técnicas y ninguna pensada para «tactical». La skill aportó poco y el resto es criterio propio, documentado arriba.
- Duración de 75,4 s: dentro del rango pedido, pero la skill avisa de que es larga para su regla general.
- Render en la nube: ~6 min por versión a 60 fps. Una toma nueva de voz cuesta créditos y necesita aprobación.

## H. Cinco mejoras

1. Un editor de jugadas (o importar coordenadas desde un diagrama o un CSV) en vez de escribir waypoints a mano.
2. Variantes de pantalla partida en vertical (arriba/abajo) para que cada caso tenga 1080 px de ancho.
3. Añadir a la biblioteca técnicas «tactical» medidas (freeze + anotación, rebobinado, repetición desde otro ángulo), para que la skill pueda elegirlas.
4. Sonido: SFX de zapatillas y red sincronizados con los eventos de la jugada (ya existen los marcadores).
5. Una plantilla de episodio «2 casos» parametrizada (jugada base + dos defensas), para producir la serie solo con datos.

## Qué se puede automatizar

- Ya está automatizado y probado: tests tácticos, QC de motor, pausas de voz, música, props, render, máster y QC de la skill (`render-tactical.sh`).
- Automatizable a continuación:
  - Generación del episodio a partir del guion + plantilla «2 casos».
  - Hoja de contactos y capturas en el mismo script.
  - Subida privada a Drive.
- Requiere decisión humana siempre: gastar créditos de ElevenLabs, publicar y tocar Metricool.
