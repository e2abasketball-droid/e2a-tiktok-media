# Tactical Studio V4 — Auditoría (en curso, 2026-11-14/15)

Convención: **[VISTO]** = medido o visto en el MP4/datos reales. **[INFERIDO]** = deducido del diseño del engine o del episodio, sin confirmación visual.

## Observación independiente del propietario (2026-11-14 16:30Z) — RAM Screen V2
Fuente: propietario, ffprobe/ffmpeg sobre el MP4 completo `ram-screen-v2-social.mp4`.

- [VISTO, verificado por Claude] 34.069 s, 1080×1920, 30 fps, 9.08 MB, −14.0 LUFS integrado, pico −1.5 dBFS.
- [VISTO, propietario] 0–2 s: encuadre cerrado con acción, pero no queda claro a quién mirar en la primera lectura.
- [VISTO, propietario; coherente con el episodio] título «RAM SCREEN» ≈8 s (shot `reveal`, aparece en «head start»), rótulo DROP → PULL-UP ≈12 s (shot `readA1`), BLITZ → SHORT ROLL ≈20 s (shot `readB1`).
- [VISTO, verificado por Claude] `antes-despues-v2.mp4` dura 6.6 s y **no tiene pista de audio**: no sirve para concluir nada sobre ritmo completo ni mezcla.

### Uso: selección del A/B editorial
- **Control:** RAM V2 tal cual (misma voz, misma mezcla, misma jugada).
- **Variante (un solo cambio editorial: cámara/encuadre de apertura y eje):** abrir en plano táctico alto con la decisión (X5 y el balón) y la pista visibles desde el primer segundo; sostener el eje durante el bloqueo; mover la cámara solo para revelar la ventaja.
- Audio y datos de jugada idénticos (mismo voice.mix, mismas plays) para atribuir cualquier cambio de retención a la edición cuando haya datos.

## Pruebas de movimiento y balón en las 14 jugadas (datos de la jugada, 2026-11-15)
`test-motion.mts`: 0 fallos en las 14 jugadas. `test-ball.mts` [VISTO en los datos; sin ver aún en vídeo cómo se nota]:

| Jugada | Fallo | Valor |
|---|---|---|
| hammer-b-rim (se publica el 15 nov 10:00) | el balón salta | 206 m/s a 2,054 s (límite 20) |
| hammer-b-rim | los botes de O1 no llegan al suelo | 5 botes, el peor a 0,173 m |
| elevator-a-chase | salto de balón | 20,3 m/s a 1,462 s |
| spain-a-roll (se publica el 15 nov 13:00) | salto de balón | 22,7 m/s a 3,000 s |
| example-pin-down | salto de balón | 20,7 m/s a 1,862 s |
| elevator-b-switch | mano separada del balón | 0,152 m (O1, 1,72 s) |
| stagger-b-backdoor (y lowlock) | mano separada del balón | 0,103 m (O2, 2,20 s) |
| RAM V1, RAM V2, Spain B, Hammer A, Stagger A | sin fallos | — |

## Fotogramas RAM V2 control frente a la variante B (render a escala 0,5, frames 0/45/120/200/300) [VISTO]
- **Control, f0 (0,0 s):** plano cerrado a la altura de los jugadores; ocupan el cuadro el 5, el 4 y dos defensores; **no se ve el balón ni el aro**. Coincide con tu lectura de que no queda claro a quién mirar.
- **Control, f45 (1,5 s):** primer anillo rojo bajo el bloqueo; el balón sigue fuera de cuadro.
- **Control, f120–f300:** el plano alto aparece en el rewind (≈4 s); el eje gira de −22° a −46° entre planos.
- **Variante B, f0:** plano alto en el que se ven a la vez el aro, la zona, los cuatro jugadores del bloqueo y el base con el balón (abajo). Los jugadores salen más pequeños.
- **Variante B, f45–f200:** el mismo encuadre y el mismo eje (−30°), sin deriva; el anillo y la ruta se leen sobre la pista.
- **Variante B, f300:** el mismo eje con un empuje leve sobre X5 y la etiqueta X5 legible.
- [INFERIDO] Con los jugadores más pequeños puede bajar la sensación de acción en 0–2 s. Es justo lo que mide el experimento (salto en 3 s).
