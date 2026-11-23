# Realism V3.3 — 06 RENDIMIENTO

Máquina: 4 núcleos, 15 GB de RAM, sin GPU.
Render: SwiftShader (`--gl=swangle`), `--concurrency=4`, 1080×1920, 30 fps.
Todas las medidas son de la misma sesión y no hubo dos renders a la vez.

## Benchmark de 10 jugadores, 2 s (60 frames)

| Render | Escena | Tiempo | s/frame |
|---|---|---|---|
| **V3.3** (`rv33-bench-10-v33`) | 5v5 V3.3, 10 jugadores | **158 s** | 2,63 |
| V3.2, rama V3.3 (`rv33-bench-10-v32`) | La misma escena y cámara | 142 s | 2,37 |
| V3.2, bundle base 28b06ea (`rv32-bench-10-v32`) | Escena de benchmark de V3.2 | 170 s | 2,83 |
| V3.2, documentado en V3.2 | Escena de V3.2, otra sesión | 198,4 s | — |

**Lectura:**
- En la misma escena, V3.3 tarda un **+11 %** más que V3.2: 158 s frente a 142 s.
- En esa escena, V3.2 no tiene clips para estos jugadores y cae al movimiento legacy sobre la malla V3.2. El 11 % es, por tanto, el coste del compilador y del movimiento V3.3:
  - solver de contacto;
  - multibote;
  - caché de 10 ms.
- La geometría y los materiales son los mismos.
- La diferencia con los 198,4 s documentados se debe a otra escena y otra sesión. No es una mejora de V3.3.

## Renders de entrega

| Vídeo | Frames | Tiempo | s/frame |
|---|---|---|---|
| 01 contacto V3.2 / V3.3 (dos paneles) | 375 | 694 s | 1,85 |
| 02 debug V3.3 | 375 | 642 s | 1,71 |
| 03 solo movimiento | 375 | 632 s | 1,69 |
| 04 cámara lenta | 306 | 541 s | 1,77 |
| 06 trío | 225 | 336 s | 1,49 |
| 07 5v5 sin gráficos | 330 | 736 s | 2,23 |
| 08 5v5 editorial | 330 | 655 s | 1,98 |

Un Reel 5v5 de ~40 s con V3.3 en esta máquina tardaría unos **1200 frames × ~2,1 s ≈ 42 min**. No es tiempo real.

## Coste en CPU del movimiento (fuera del render)
- Evaluación memoizada en una rejilla de 10 ms y determinista: el resultado no depende del orden de los frames ni de la caché (`qa/determinism_*.json`).
- La compilación de las 10 pistas del 5v5 tarda **28 ms** la primera vez (medido con `npx tsx`). Después se reutiliza de la caché.

## Pendiente
- Sin medición en GPU: la máquina no tiene.
- La concurrencia por encima de 4 no se ha probado.
