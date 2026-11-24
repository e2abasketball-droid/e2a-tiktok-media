# Arrow Press 1-3-1 V2: diagnóstico (fase 0–1)

## Qué se auditó

- **Archivo:** `E2A-ARROW-PRESS-131-MASTER.mp4` (V1). Se ha conservado sin tocar.
  - 1080×1920, 30 fps, 1.268 fotogramas, 42,27 s.
  - H.264 High a unos 6,8 Mbps; AAC mono a 48 kHz.
  - −14,2 LUFS, LRA 3,1.
- **Composición:** `Tactical3DV2`.
  - athleteRenderer `v33` (jugada `"v33":"compile"`), env `cinema`.
  - Pista completa opt-in (`court: 'full'`).
  - Montaje `tactical/episodes/_gen-arrow131.py`.
- **Copia reproducible:** la rama `claude/project-thread-cpevo1`, commits c931b1a → d514bf7, con las props V1 regeneradas con `_gen-arrow131.py`.

## Tabla de defectos

| # | Defecto | Dónde (s) | Causa real verificada | Corrección V2 |
|---|---|---|---|---|
| 1 | Saltos de luminancia y textura del suelo | Repartidos por todo el vídeo, sobre todo en 10–19 | V1 mezclaba fotogramas de **3 renders**: Chromium a concurrency 4, Chromium a concurrency 2 y 151 stills PNG. Esa mezcla tapaba los fotogramas en mosaico o negros de Chromium con la textura de pista completa. Cada cambio de fuente da una diferencia de unos 5,7 en un plano congelado (dentro de un mismo render: 0,1). | **Un solo render** con chrome-headless-shell a concurrency 4: 0 fotogramas malos y sin parches. |
| 2 | Las áreas «parpadean» en cada cambio de jugador activo | 5,6–9,7 (1+3+1), 22–29 (lecturas) | Superposiciones de cobertura encadenadas: la anterior se funde 0,25 s, la siguiente entra 0,25 s, y el área cae casi a 0 y vuelve. | Una superposición por idea con `activeKeys`: fundido cruzado de 0,35 s sin caída. |
| 3 | Destello en cortes invisibles (mismo fotograma, misma cámara) | 5,64 · 18,30 · 37,82 | El corte reinicia las áreas, las líneas (se vuelven a dibujar), las esquinas del FREEZE y los marcadores. | Los planos con el mismo fotograma ahora son uno solo (this+shape, trap+lines, zone+close). Diferencia en esos cortes: 0,98 / 2,74 / 1,05 → 1,15 (es el fundido cruzado buscado, no un corte) / 0,34 / 0,05. |
| 4 | Bordes dorados que «respiran» | 10–13,6 (subida del balón) | Grosor y opacidad del borde dependían de la velocidad del defensor. La referencia del balón eran 5 muestras, que hacían aliasing con el bote. | `stable: true`: sin modulación por velocidad y referencia de 21 muestras. |
| 5 | Pulso al aparecer las áreas | 3,2–5 | Pulso del reveal. | Desactivado con `stable`. |
| 6 | Dos círculos sobre el mismo defensor | turns, trap, lines | Marcador más área activa del mismo jugador. | Marcador quitado donde el área ya está activa. Los pins siguen. |
| 7 | Voz sin presencia ni energía | Todo, sobre todo los remates | La mezcla V1 no tenía la cadena de voz estándar (sin EQ de presencia ni compresión). Los remates quedaban **por debajo** de la explicación: «It's a trap.» −5 dB frente a la frase anterior, «Sprint back.» −5 dB, «Trap!» −1 dB. | Cadena sin créditos y curva A–E por frase (ver QA). Toma nueva preparada, sin ejecutar. |
| 8 | Volvía 0,25 s atrás en el corte lecturas → escape | 29,07 | El remap de escape empezaba en release −0,3 y lecturas terminaba en release −0,05. | Escape empieza en release −0,05: tiempo continuo. No cambia la táctica, solo dónde empieza el plano. |

## Descartado (comprobado, no era la causa)

- **Cambios en el orden de transparencias de three.js:** los marcadores siempre van más cerca que las mallas de cobertura.
- **Z-fighting:** lift de 5–18 mm con polygonOffset; la precisión de profundidad a 25 m es de unos 0,4 mm.
