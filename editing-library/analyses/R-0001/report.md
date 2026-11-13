# Análisis de edición — R-0001 Vídeo propio E2A Wembanyama EP03 (prueba)

Esquema `e2a.analysis/1` · skill v1.0.0 · sha256 `8b9b39ba7961…` · derechos: propio

Niveles de evidencia: **observación** = medido directamente; **estimación** = deducido de medidas con un método conocido; **hipótesis** = lectura que hay que confirmar mirando los fotogramas.

## 1. Datos técnicos `[observación]`
- Duración 49.5 s · 30.0 fps · 1080×1920 (9:16, vertical)
- Vídeo h264 yuv420p · audio aac 48000 Hz

## 2. Estructura narrativa `[estimación]`
- Gancho 0–3.0 s: 2 cortes, texto antes de 1 s: sí
- Desarrollo 3.0–12.0 s
- Clímax 12.0–15.0 s (ventana de 3 s con más cortes, movimiento y nivel de audio (entre 20% y 90% del vídeo))
- Desenlace 46.6–49.5 s, silencio final 2.93 s
- Método: energía por segundo = cortes + diferencia de imagen + nivel de audio (z-scores). La lectura del contenido (qué se cuenta) requiere ver el vídeo `[hipótesis]`.

## 3. Cortes y duración de planos `[observación]`
- 17 cortes, 18 planos · mediana 1.85 s · media 2.75 s · mín 0.2 s · máx 8.5 s · 3.43 cortes/10 s
- Cortes (s): 0.2, 1.2, 5.2, 6.2, 12.3, 12.7, 13.0, 13.9, 15.8, 18.3, 26.8, 33.2, 35.0, 40.9, 42.1, 43.8, 46.6

| plano | inicio | dur. (s) | imagen | cámara `[estimación]` | luma | sat. |
|---|---|---|---|---|---|---|
| 1 | 0.0 | 0.2 | en_movimiento | indeterminado | 7.9 | 0.517 |
| 2 | 0.2 | 1.0 | estatica | static | 14.0 | 0.713 |
| 3 | 1.2 | 4.0 | estatica | static | 21.4 | 0.656 |
| 4 | 5.2 | 1.0 | estatica | static | 12.3 | 0.598 |
| 5 | 6.2 | 6.1 | estatica | static | 25.1 | 0.46 |
| 6 | 12.3 | 0.4 | en_movimiento | indeterminado | 18.4 | 0.661 |
| 7 | 12.7 | 0.3 | en_movimiento | indeterminado | 20.3 | 0.672 |
| 8 | 13.0 | 0.9 | en_movimiento | static | 21.1 | 0.667 |
| 9 | 13.9 | 1.9 | estatica | static | 22.8 | 0.662 |
| 10 | 15.8 | 2.5 | estatica | static | 23.1 | 0.73 |
| 11 | 18.3 | 8.5 | estatica | static | 20.3 | 0.648 |
| 12 | 26.8 | 6.4 | estatica | static | 23.7 | 0.533 |
| 13 | 33.2 | 1.8 | estatica | static | 17.6 | 0.658 |
| 14 | 35.0 | 5.9 | estatica | static | 21.9 | 0.654 |
| 15 | 40.9 | 1.2 | estatica | static | 20.4 | 0.427 |
| 16 | 42.1 | 1.7 | estatica | static | 28.1 | 0.469 |
| 17 | 43.8 | 2.8 | estatica | static | 14.5 | 0.682 |
| 18 | 46.6 | 2.9 | estatica | static | 15.8 | 0.392 |

## 4. Movimientos de cámara y cambios de perspectiva `[estimación]`
- Resumen: static ×15, indeterminado ×3
- Cambios de perspectiva entre planos consecutivos (encuadre o luz muy distintos): 3
- Nota: zoom/paneo reales o simulados no se distinguen: en ambos casos el encuadre cambia igual. Nombres de movimiento = los de Remotion Pro (`template/src/pro/camera.tsx`).

## 5. Zooms, paneos, recortes y movimientos simulados `[estimación]`
- Zoom en 0 planos
- Paneo/inclinación en 0 planos

## 6. Transiciones y efectos visuales `[estimación]`
- Tipos: transicion_animada ×7, corte ×5, fundido_encadenado ×3, barrido_con_desenfoque ×2
  - 0.2 s: transicion_animada (0.2 s) — cambio repartido en 0.20 s
  - 5.2 s: fundido_encadenado (0.2 s) — fotograma intermedio ≈ mezcla de ambos planos (1.6 vs 7.2)
  - 6.2 s: fundido_encadenado (0.2 s) — fotograma intermedio ≈ mezcla de ambos planos (3.7 vs 5.5)
  - 12.3 s: transicion_animada (0.3 s) — cambio repartido en 0.30 s
  - 13.0 s: transicion_animada (0.5 s) — cambio repartido en 0.50 s
  - 13.9 s: transicion_animada (0.3 s) — cambio repartido en 0.30 s
  - 18.3 s: fundido_encadenado (0.2 s) — fotograma intermedio ≈ mezcla de ambos planos (2.5 vs 6.8)
  - 26.8 s: transicion_animada (0.4 s) — cambio repartido en 0.40 s
  - 33.2 s: transicion_animada (0.3 s) — cambio repartido en 0.30 s
  - 40.9 s: barrido_con_desenfoque (0.4 s) — nitidez cae a 1.2 desde 7.4 (desenfoque de movimiento)
  - 43.8 s: transicion_animada (0.3 s) — cambio repartido en 0.30 s
  - 46.6 s: barrido_con_desenfoque (0.6 s) — nitidez cae a 1.1 desde 3.7 (desenfoque de movimiento)

## 7. Subtítulos `[estimación]`
- Texto en pantalla en el 99% de los fotogramas muestreados
- Posición: franja al 88% de la altura · bloque de ~96 px
- Ritmo: 0.95 cambios/s, intervalo mediano 1.0 s
- Color dominante: blanco · palabras resaltadas en color: sí
- Aparición: instantánea (aparece de golpe) `[hipótesis]`
- Tipografía: no identificable automáticamente: revisar en los fotogramas (hipótesis visual)

## 8. Gráficos, overlays, máscaras y composiciones `[estimación]`
- rotulo_fijo en franja al 8% de la altura `[estimación]` — cabecera, marca o rótulo presente casi todo el vídeo `[hipótesis]`
- Franjas con texto/gráficos: 8% (0.94), 18% (0.55), 28% (0.22), 38% (0.19), 42% (0.26), 57% (0.17), 88% (0.76)
- máscaras y composiciones complejas no se detectan automáticamente: revisar la hoja de fotogramas

## 9. Color, contraste, iluminación y estética `[observación]`
- Luma media 20.8, contraste 44.1, saturación 0.592, calidez (R−B) -9.7, negros 0.88, blancos 0.01
- Estética: oscuro, contraste medio, muy saturado, neutro `[estimación]`
- Paleta dominante: #101010 (0.809), #101030 (0.079), #F0B010 (0.021), #F0F0F0 (0.011), #303050 (0.01), #303030 (0.007)
- Afinidad con la paleta E2A (píxeles cercanos): azul_marino 0.315, dorado 0.003, dorado_profundo 0.003, blanco 0.011

## 10. Narración, música, efectos, silencios y mezcla
- Sonoridad -14.1 LUFS, pico real -1.6 dBFS, LRA 2.1 LU `[observación]`
- Silencios (< −35 dB, ≥ 0.25 s): 38.11–38.4, 40.5–40.75, 41.71–41.99, 44.28–44.55, 46.58–49.51 `[observación]`
- Voz: sí (93% del tiempo) `[estimación]`
- Música de fondo: no detectada `[estimación]`
- Sin pulso rítmico claro (mejor candidato 109.1 BPM, confianza 0.09) `[estimación]`
- Golpes de audio: 8.48 por 10 s · efectos candidatos fuera de la voz: ninguno `[estimación]`
- Mezcla: voz 11.0 dB sobre el fondo (aproximación: el fondo se mide en las pausas, no debajo de la voz) `[estimación]`
- Reparto de energía: graves 0.225, banda de voz 0.676, agudos 0.021
- Sin transcripción (no se gastan créditos de ElevenLabs en esta fase).

## 11. Sincronización audio, imagen y texto `[estimación]`
- Cortes sobre un golpe de audio (±0.1 s): 1/17 (azar ≈ 0.17)
- Inicios de frase con cambio de texto: 1/2
- Cortes justo después de un silencio: 2
- si la proporción de cortes en golpe supera claramente lo esperado por azar, el montaje está cortado al audio (música o efectos)

## 12. Técnicas de retención y cambios de ritmo `[observación]`
- Primer corte 0.2 s · primer sonido 0.0 s · texto en el primer segundo: sí
- Mayor tramo sin cambio visual 2.9 s · interrupciones de patrón 3
- Ritmo: 4.04 cortes/10 s en la 1ª mitad, 2.83 en la 2ª; variación de planos (CV) 0.87
- cambio visual en el primer 1.5 s: gancho visual rápido `[hipótesis]`
- texto en pantalla desde el primer segundo: el gancho se lee sin audio `[hipótesis]`
- silencio de 2.93 s al final `[observación]`

## Fotogramas representativos
- Hoja de contactos: `frames/sheet.jpg` (20 fotogramas) — material de trabajo: no se sube al repositorio si el vídeo es de terceros
- Tiempos: 0.1, 0.7, 3.2, 5.7, 9.25, 12.5, 12.85, 13.45, 13.5, 14.85, 17.05, 22.55, 30.0, 34.1, 37.95, 41.5, 42.95, 45.2, 48.05, 49.3

## Revisión visual (la completa Claude o una persona mirando la hoja de contactos)
- Qué cuenta el vídeo y cómo se reparte la historia entre gancho, desarrollo, clímax y desenlace `[hipótesis]`
- Tipografía, animación de los subtítulos y gráficos que no se pueden medir `[hipótesis]`
- Técnicas reutilizables para E2A → fichas `tec-NNNN` con `library.py propose` + revisión
