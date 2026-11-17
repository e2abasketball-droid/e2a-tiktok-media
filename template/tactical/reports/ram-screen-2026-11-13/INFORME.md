# RAM SCREEN: The Screen Before the Screen — informe de producción (2026-11-13)

Rama: `claude/project-thread-rray0k` (e2a-tiktok-media). Sin merge, sin publicación, sin Metricool ni tareas programadas.

## Entregables (`/mnt/project-files/tactical-studio/ram-screen/`)
- `ram-screen-social.mp4`: máster social, 1080×1920, 30 fps, 37,31 s, −14,0 LUFS, TP −1,4 dBTP (ganancia fija, sin loudnorm), 9,1 MB.
- `ram-screen-master-hq.mp4`: render Remotion sin recomprimir (58,7 MB, −16,9 LUFS antes de la ganancia de máster).
- `antes-despues.mp4`: 5,9 s, mismo tramo de las dos lecturas, misma cámara y mismo tiempo de jugada, velocidad normal. ANTES = motor y constructor de `main` (b3f0321) con las mismas specs; DESPUÉS = esta rama.
- `contact-sheet.png`: hoja de contactos por momentos (qc-video).

## Definición validada (antes del render)
RAM = un bloqueo indirecto de un jugador (aquí O4) sobre el defensor del pívot que va a poner el bloqueo directo (X5), para que el pívot llegue con ventaja al bloqueo directo. Fuentes: NBC Sports (NBA glossary: ram screen), Basketball Action Dictionary («Ram»), Hoop Student (ram screen). Coberturas: drop (el grande se hunde, concede el tiro de media distancia) y blitz (dos al balón; contra: short roll), según Basketball For Coaches (drop coverage), Basketball Action Dictionary (identificar coberturas de pick and roll) y Hoops Geek (pick and roll contra blitz).

## Guion final (voz Deuce, ElevenLabs eleven_v4, inglés)
| Tiempo | Bloque | Texto | Rótulo |
|---|---|---|---|
| 0–4,2 | HOOK | The best part of this pick and roll happens before the pick. | BEFORE / THE PICK (congelado en la ventaja de O5) |
| 4,2–9,7 | REWIND + RAM | Rewind. Four screens the big's defender. Now Five has a head start. | RAM SCREEN · 1 · OFF-BALL SCREEN |
| 9,7–13,6 | 2.º BLOQUEO | Five gets there first. Now watch his defender. | 2 · BALL SCREEN · X5 resaltado en «his defender» |
| 13,6–19,6 | LECTURA A | First look. The big drops. The guard has room to pull up. | DROP → PULL-UP, separación X5–O1 medida, PULL-UP +2 |
| 19,6–27,5 | LECTURA B | Same setup. This time, two defenders jump the ball. Hit the short roll. The lane is open. | BLITZ → SHORT ROLL; línea de pase solo con el hueco, carril solo tras la recepción |
| 27,5–33 | COMPARACIÓN | Same two screens, two different reads. Watch where the big goes. | BIG BACK / BIG UP alternados en el mismo eje |
| 33–37,3 | CTA | You're the big. Do you drop or blitz? | DROP / OR BLITZ?, logo E2A discreto; la cámara vuelve al encuadre inicial (loop) |

## Tres momentos donde mejor se ve la mejora
1. **23,3–23,9 s**: pase por encima de la cabeza O1→O5 contra el blitz. El balón sube desde las manos (carga), sale de las manos y llega a las del receptor, sin teletransporte.
2. **17,0–18,6 s**: pull-up de O1. Recogida, tiro con arco continuo y aterrizaje con flexión de rodillas.
3. **7,3–9,7 s**: O5 sale del ram con ventaja. Silueta fuerte frente a O1 ligero, bote vivo de O1 con cadencia según velocidad y cabeza que sigue al balón.

## Cambios en el motor (reutilizables por cualquier episodio)
- `src/tactical/play.ts`: bote vivo con cadencia por velocidad y número entero de botes (el balón vuelve a la mano al final de cada `hold`); el arco del pase sale de las manos del pasador; pase por encima cargado desde un `hold` sin bote; orientación de la mano suavizada (0,15 s); el jugador con balón mira al receptor o al aro (antes, atan2(0,0) provocaba saltos).
- `src/t3d/rig.ts` y `Athlete.tsx`: `PLAYER_BUILD` (complexión por jugador; O1 0,92, O5 1,14), amortiguación al aterrizar, postura `blitz`, brazos por encima de la cabeza, `headYaw` (la cabeza sigue al balón).
- `src/t3d/Scene.tsx`: el balón gira (backspin en vuelo, rodadura al botar).
- `src/t3d/Tactical3D.tsx`: `autoSfx` (bote, recepción, frenada, red, aterrizaje) calculado de los eventos de la jugada y pasado por el remap de cada plano, y `ambience` (bucle de pabellón).
- `scripts/build-play.mts`: tiempos de los puntos intermedios con perfil suavizado y duración mínima por tramo.
- Todo se evalúa desde el tiempo de jugada (`pt`), así que congelar, rebobinar o renderizar desordenado da el mismo resultado (test-motion lo comprueba).

## Cómo activarlo en Tactical3DV2
- Las mejoras de movimiento se aplican solas a cualquier jugada que use el motor.
- Los sonidos por evento y el ambiente se activan en el JSON del episodio:
  ```json
  "autoSfx": {"bounce": 0.2, "catch": 0.13, "squeak": 0.1, "swish": 0.3, "land": 0.08},
  "ambience": {"src": "sfx/arena.mp3", "volume": 0.08}
  ```
- Render:
  ```
  node scripts/tactical-props.mjs tactical/episodes/ram-screen.json /tmp/props.json --music tactical/ram/music.mp3
  npx remotion render src/index.ts Tactical3DV2 out.mp4 --props=/tmp/props.json --gl=swangle --browser-executable=<chrome-headless-shell> --concurrency=4 --timeout=180000
  ```
- Para regenerar el episodio y las jugadas: `python3 tactical/specs/_gen-ram.py`, luego `build-play.mts` para cada spec, y por último `python3 tactical/episodes/_gen-ram-screen.py`.

## Checks
| Check | Resultado |
|---|---|
| test-play RAM (A+B) | 43/43 |
| test-play, todas las jugadas | 220/220 |
| test-motion, todas las jugadas (nuevo) | 82/82 |
| test-stagger (regresión) | 88/88 |
| test-tactical, todas las jugadas | 286/289 (ver notas) |
| qc-tactical3d RAM | 11/11 |
| qc-tactical3d Stagger V2 (regresión) | 11/11 |
| qc-bounds RAM | PASS, 1119 frames, 0 violaciones |
| qc-video máster | PASS (−14,0 LUFS, TP −1,4) |
| tsc | OK |
| tools/tests (unittest) | 103 OK |
| audio-stems | voz −13,7 LUFS; música 20,8 dB por debajo de la voz; peor efecto frente a una palabra −15,4 dB |

Notas sobre test-tactical: ninguno de los tres fallos es una regresión.
- `ram-a-drop` falla «tiro detrás del triple». Es una regla pensada para Elevator; aquí el pull-up de media distancia (6,08 m) es intencionado.
- `stagger-b-backdoor` y su variante lowlock fallan «O2 con espacio». En `main` falla igual.

## Tiempos y dependencias
| Render | Tiempo |
|---|---|
| Máster 1080×1920, 1119 frames | 1963 s (~33 min) |
| Borrador 2 a escala 0,5 | 1851 s |
| Antes/después a escala 0,75 | 319 + 325 s |

No hay dependencias nuevas.

Créditos ElevenLabs:
- Voz: 426 créditos.
- Transcripción Scribe: 156 créditos.

La música es el sintetizador propio (licencia music/synth).

## Limitaciones
- Las dos jugadas comparten alineación y bloqueos hasta ~3,1 s. Las splines de O1 y X5 difieren unos centímetros antes de ese punto (no se nota a la vista).
- Ropa: el tejido se simula con volumen y sombreado del rig, no con física de tela.
- En el hook (1,9 s) O5 roza el borde derecho durante el congelado.
- El sello «PULL-UP +2» queda sobre el tablero en el plano final de la lectura A (se lee, pero detrás del cristal).
- Sin voz de reserva: cualquier cambio de texto necesita una toma nueva.
