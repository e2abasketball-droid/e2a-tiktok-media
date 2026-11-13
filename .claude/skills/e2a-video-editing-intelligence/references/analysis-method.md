# Método de análisis (ANALYZE)

Todo se mide con `ffmpeg`/`ffprobe` y `numpy`. El vídeo se decodifica dos veces:

- **baja resolución** en gris, 10 fps, lado largo 128 px: cortes y movimiento de imagen;
- **resolución media** en color, 5 fps (2 fps si dura más de 4 min), lado largo 320 px: cámara,
  color, texto y gráficos.

Parámetros (`PARAMS` en `analyze_video.py`) y una huella del código se guardan en `meta`: si cambian,
el análisis guardado se recalcula. Mismo archivo + mismo código = mismas medidas (determinista).

| # | Dimensión | Cómo se mide | Nivel | Límites conocidos |
|---|---|---|---|---|
| 1 | Duración, FPS, resolución, formato | `ffprobe` | observación | — |
| 2 | Estructura gancho / desarrollo / clímax / desenlace | energía por segundo = z(cortes) + z(diferencia de imagen) + z(nivel de audio). Gancho = primeros 3 s (o 15%); clímax = ventana de 3 s con más energía entre el 20% y el 90%; desenlace = último plano largo o último 15% | estimación | No sabe qué se cuenta: la lectura narrativa es hipótesis y se hace mirando la hoja de contactos |
| 3 | Cortes y duración de planos | diferencia media absoluta entre fotogramas + distancia de histogramas; umbral = max(3, 6 × mediana). Un pico de un fotograma = corte; varios = transición animada. Mínimo 0.2 s entre cortes | observación | Cortes entre planos casi idénticos pueden pasar; destellos muy rápidos pueden contar como corte |
| 4 | Movimientos de cámara / cambios de perspectiva | correlación de fase (traslación) + búsqueda de escala bilineal entre fotogramas a 0.4 s; se acumula por plano. Solo cuenta un paso si el modelo global explica el cambio (error ajustado < 60% del bruto). Nombres de Remotion Pro: `push-in`, `pull-out`, `pan-left` (la imagen va a la izquierda), `pan-right`, `tilt-up` (la imagen baja), `tilt-down`, `drift`, `static`. Cambio de perspectiva = luz o movimiento muy distintos entre planos seguidos | estimación | Movimiento real y simulado (Ken Burns) son indistinguibles; con objetos grandes en movimiento se marca hipótesis |
| 5 | Zooms, paneos, recortes, movimiento simulado | lo anterior: `zoom_total`, `desplazamiento_x/y` (fracción del cuadro), `temblor` (variación del paso) | estimación | Recortes estáticos (reencuadres) no se distinguen de un plano nuevo |
| 6 | Transiciones y efectos visuales | en cada evento animado: pico de luminancia → `flash`; mínimo < 14 → `fundido_a_negro`; caída de nitidez > 45% → `barrido_con_desenfoque`; fotograma intermedio ≈ mezcla de ambos planos → `fundido_encadenado`; si no, `transicion_animada`. Destellos dentro de un plano: salto de luminancia > 35 | estimación (corte seco: observación) | Glitch, máscaras y transiciones 3D quedan como `transicion_animada` |
| 7 | Subtítulos (posición, tamaño, ritmo, animación, color) | densidad de bordes horizontales fuertes por franjas del 5% de la altura; franja de subtítulos = la que cambia con más frecuencia mientras hay texto; alto del bloque en px de origen; cambios/s; color dominante de los píxeles claros; palabras resaltadas si conviven blanco y amarillo/dorado; aparición progresiva si el cambio dura ≥ 2 muestras | estimación (aparición: hipótesis) | Sin OCR: no lee el texto ni identifica la fuente. La tipografía siempre es hipótesis visual |
| 8 | Gráficos, overlays, máscaras, composiciones | píxeles con bordes que no cambian en todo el vídeo por zonas (logos, marcadores); franjas de texto presentes > 85% del tiempo (rótulos fijos); bandas negras; vídeo horizontal sobre fondo desenfocado (centro nítido, bordes suaves); pantalla dividida (línea fija en el centro) | estimación (lectura: hipótesis) | Máscaras y composiciones complejas: revisión visual |
| 9 | Color, contraste, iluminación, estética | luma media, desviación (contraste), saturación (solo píxeles con brillo > 40), calidez R−B, % negros/blancos por plano y global; paleta (cuantización 8 niveles/canal); afinidad con la paleta E2A (píxeles a < 45 de distancia RGB); etiquetas oscuro/luminoso, contraste, saturación, cálido/frío | observación (etiquetas: estimación) | La gradación exacta (LUT) no se identifica |
| 10 | Narración, música, efectos, silencios, mezcla | EBU R128 (`ebur128`): LUFS, pico real, LRA; `silencedetect` −35 dB ≥ 0.25 s; espectro a 50 ms: voz = energía 300–3400 Hz modulada a 3–8 Hz y repartida en armónicos (un tono puro no cuenta); música = energía tonal fuera de la voz; golpes = picos de flujo espectral; tempo = autocorrelación de los golpes 70–180 BPM (fiable si confianza ≥ 0.3); margen voz/fondo en las pausas; efectos candidatos = golpes fuertes fuera de la voz | observación (loudness, silencios) / estimación | Sin transcripción (no se gastan créditos). El margen voz/fondo se mide en las pausas, no debajo de la voz |
| 11 | Sincronía audio–imagen–texto | cortes a ±0.1 s de un golpe de audio comparado con lo esperable por azar; cortes en el pulso si hay tempo fiable; inicios de frase con cambio de subtítulo (±0.4 s); cortes justo tras un silencio | estimación | Depende de la calidad de golpes y voz |
| 12 | Retención y cambios de ritmo | primer corte, primer sonido, texto en el primer segundo, mayor tramo sin cambio visual (cortes + destellos + cambios de subtítulo), interrupciones de patrón (planos < 50% de la mediana, destellos), cortes por ventana de 5 s y cambios bruscos (≥ 3), aceleración 1ª vs 2ª mitad, CV de planos, bucle (último ≈ primer fotograma), silencio final | observación (lecturas: hipótesis/estimación) | Medimos el montaje, no la retención real (eso son métricas de la plataforma) |

## Fotogramas

`frames/f_<segundos>.jpg` (360 px de ancho) en el centro de cada plano (máx. 22), al inicio, en el
clímax y al final, y `frames/sheet.jpg` con el tiempo impreso. Son material de trabajo: **no se
suben al repositorio** si el vídeo es de terceros. La hoja de contactos es la base de la revisión
visual que hace Claude.

## Fallos controlados

Archivo vacío, texto con extensión `.mp4`, MP4 truncado, archivo sin pista de vídeo o duración cero:
`analyze_video.py` sale con código 2 y `{"ok": false, "reason": "..."}`. El llamador registra el fallo
(`library.py fail`) y sigue con la siguiente referencia.
