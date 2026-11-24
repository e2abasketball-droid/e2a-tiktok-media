# Arrow Press 1-3-1 V2: informe final de QA

Todas las medidas se han tomado sobre los **MP4 exportados** (`E2A-ARROW-PRESS-131-V2.mp4` y la trial), con `scripts/qc-floor-flicker.py`. Los datos completos están en `qc-final.json`.

## 1. Parpadeos corregidos: tramos congelados (solo pueden cambiar los gráficos)

| Tramo | V1 dif. media / p99 | V1 parpadeos | V1 caídas | **V2 dif. media / p99** | **V2 parpadeos** | **V2 caídas** |
|---|---|---|---|---|---|---|
| 5,0–9,7 s (1 + 3 + 1) | 0,94 / 3,51 | 19 | 8 | **0,10 / 0,73** | **0** | 3* |
| 17,25–22,05 s (TRAP + 2 defensores) | 2,03 / 5,92 | 31 | 45 | **0,11 / 1,30** | **0** | **0** |
| 37,75–40,5 s (zona + pregunta) | 0,87 / 3,64 | 7 | 13 | **0,19 / 1,41** | **0** | 2* |

\* No son parpadeos de la pista. Lo he comprobado fotograma a fotograma en la hoja de contactos:
- 5,6 s: cambio de subtítulo y salida del título y la leyenda;
- 6,8 s: el relevo X1 → X2-X5-X3, un fundido cruzado de 0,35 s (a mitad del fundido el color está entre azul y oro);
- 39,4 s: cambio de título de la pregunta.

**Fotogramas malos (oscuros o en mosaico):** V1 0 tras el parche · V2 **0 sin parche** (un solo render) · trial 0.

**Cortes sobre el mismo fotograma:** 18,30 s: 2,74 → **0,34** · 37,82 s: 1,05 → **0,05**.

## 2. Estabilidad de luminancia y opacidad del oro (jitter, p99)

| Plano | V1 | V2 |
|---|---|---|
| hook | 0,022 | 0,008 |
| this + shape | 0,222 | 0,195 (incluye el reveal y los marcadores de entrada, que son a propósito) |
| turns | 0,098 | 0,101 (el balón y X1 se mueven; el área sigue al defensor) |
| trap + lines | 0,218 | **0,011** |
| reads | 0,275 | **0,108** |
| escape | 0,332 | **0,067** |
| zone + close | 0,310 | **0,115** |

El único pico que queda en trap + lines (17,2 s) es el **acento del FREEZE en «Trap!»**: un escalón único y buscado, no un pulso. Ya estaba en V1.

## 3. Anclaje espacial y 4. todas las cámaras

- Todas las áreas y líneas son mallas 3D del suelo dentro de la misma escena y la misma cámara. No hay capas 2D de pista.
- Revisados los 7 planos y las 6 cámaras (TRAP, PRESS, TURN, MID, BACK y ZONE): ninguna capa se separa ni vibra. Ver `E2A-ARROW-PRESS-131-V2-CONTACT.jpg` y la comparación de gráficos.
- Frame-fit: las mismas marcas que V1, solo los primeros planos del trap, a propósito: 48 hook, 58 turns y 127 trap+lines (antes 70 + 57). **No hay ningún cambio de cámara.**

## 5. Audio (sin créditos, la misma toma de Deuce)

| | V1 máster | V2 |
|---|---|---|
| Integrado | −14,2 LUFS | **−14,2 LUFS** |
| True peak | −0,9 dBTP | **−1,5 dBTP** |
| LRA | 3,1 LU | 2,1 LU (voz más controlada; la variación va ahora por frase y con intención, ver tabla) |
| Presencia (2–4 kHz frente a 150–500 Hz) | −15,8 dB | **−12,2 dB (+3,6)** |
| Sibilancia (5–9 kHz frente a 2–4 kHz) | −2,6 dB | −3,2 dB (no sube) |

**Curva emocional.** Nivel de cada frase en dB relativo a la explicación (fase B):

| Frase | Fase | V1 | **V2** |
|---|---|---|---|
| Half court isn't a line. | A | +1,0 | **+1,4** |
| It's a trap. | A | **−4,0** | **+2,3** |
| Never let it go middle. | C | +3,5 | +1,0 |
| The ball crosses half court... | C | +3,9 | +1,0 |
| and the wing jumps. | C | +1,1 | **+2,0** |
| Trap! | C | +0,3 | **+2,6** |
| Now the ball escapes. | C | +4,2 | +1,5 |
| Don't chase it. | C | −0,4 | +0,7 |
| Sprint back. | C | **−4,1** | **+1,6** |
| The middle / far wing / safety | D | −0,5 / +2,3 / +2,1 | **0 / 0 / 0** |
| and the arrow becomes a 1-3-1 zone | E | +1,5 | +1,0 |
| or wait in the zone? | E | −0,8 | 0 |

En V1 los remates quedaban enterrados y había picos donde no tocaba. En V2 la intensidad sigue a la historia. Los cambios de ganancia ocurren solo en las pausas.

**Límite honesto:** la postproducción ajusta nivel, presencia y control, pero **no puede cambiar la entonación**. Si se quiere más interpretación, hace falta una toma nueva. Está preparada en `VOICE-REGEN-SCRIPT.md` (unos 610 créditos, sin ejecutar).

## 6. Errores tácticos

- **Ninguno introducido.** La jugada `arrow131-press.json` no se ha tocado: test-play 23/23.
- Las posiciones, los tiempos de la jugada y las cámaras son los mismos.
- Único ajuste de montaje: el escape empieza 0,25 s más tarde, para que el tiempo no vuelva atrás en el corte.

## 7. Regresión del motor

- Props V1 renderizadas con el código anterior y con el nuevo: los fotogramas 200, 450, 620 y 760 son **idénticos píxel a píxel** (diferencia 0).
- Todo es opt-in (`activeKeys`, `stable`, `fin/fout = 0`).
- `tsc` limpio.
- No cambia el motor predeterminado y no se ha fusionado nada.

## 8. Parámetros del MP4

| | V2 | Trial |
|---|---|---|
| Vídeo | 1080×1920, 30 fps, H.264 High, yuv420p, CRF 16, unos 4,0 Mbps, faststart | 3 % zoom, +sat/contraste/nitidez, CRF 19 |
| Audio | AAC 192 kbps, 48 kHz, mono | AAC 256 kbps, EQ suave |
| Duración | 42,25 s | 42,26 s |
| Sonoridad | −14,2 LUFS, −1,5 dBTP | −15,3 LUFS, −1,5 dBTP |
| SSIM frente a V2 | — | 0,69 |

La voz es la misma toma en las dos versiones.

## 9. Rendimiento del render

| | V1 | V2 |
|---|---|---|
| Pasadas | 2 renders completos con Chromium (concurrency 4 y 2) + 151 stills rehechos + mezcla | **1 render** con headless shell, concurrency 4 |
| Tiempo | Bastante más que una pasada (no lo cronometré; estimación > 1,5 h) | **36,9 min** |
| Fotogramas malos | Unos 50 % en la 1.ª pasada | **0** |

## Defectos pendientes (conocidos, no ocultos)

1. Entonación de la voz: solo se arregla con una toma nueva (con créditos y con tu OK).
2. La pausa entre frases, el texto y el orden de V1 no han cambiado, a propósito (restricción 12).
3. Las etiquetas del suelo de la zona final (tamaño 0,62) se leen en el móvil, pero son pequeñas. No se han tocado, porque no son parte del encargo.
4. El acento del FREEZE (desaturación instantánea en «Trap!») sigue siendo instantáneo. Es un efecto del motor común a todos los reels, así que no lo he cambiado aquí.
