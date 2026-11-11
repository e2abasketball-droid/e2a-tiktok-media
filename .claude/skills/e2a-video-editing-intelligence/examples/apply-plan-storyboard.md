# Plan de edición — TEST storyboard for the editing-intelligence skill (not for publication)

Episodio `test-storyboard` (player) · 22.2 s · biblioteca v1.0.0 · modo shadow
Guion protegido: huella `dbb8fc1010f8…` idéntica antes y después (texto, narración, datos y fuentes intactos).

## Técnicas elegidas
### tec-0005 v1 · Barrido rápido al cambiar de bloque (transicion, propuesta, puntuación 5.25)
- Dónde: escena 1 (1.86–5.31 s)
- Por qué: pensada para historias 'player'; estado propuesta (sin uso probado: modo sombra); evidencia: 0 medida(s), 1 estimación(es) de R-0001; encaja con el guion: 2/2 reglas medibles se cumplen ya en el plan
- Cambio: `transition` cut → **whip** (escena 1)
- Regla en el plan: plan.escenas_n >= 5 → medido 7 ✔
- Regla en el plan: plan.escena_s >= 2 → medido 3.45 ✔
- Comprobación: la escena con barrido dura al menos 2 s y el vídeo tiene 5 escenas o más (si no, el barrido se nota repetido)

### tec-0004 v1 · Gancho legible sin sonido con cambio antes de 1 s (narrativa, propuesta, puntuación 4.5)
- Dónde: escena 0 (0.0–1.86 s)
- Por qué: pensada para historias 'player'; estado propuesta (sin uso probado: modo sombra); evidencia: 1 medida(s), 0 estimación(es) de R-0001; encaja con el guion: 1/1 reglas medibles se cumplen ya en el plan
- Nota: transition omitida: la primera escena no tiene transición de entrada
- Nota: el episodio ya cumple esta técnica: no hay cambios
- Regla en el plan: plan.escena_s <= 2.5 → medido 1.86 ✔
- Regla tras el render (QC): retention.primer_corte_s <= 2.5
- Comprobación: la primera escena dura 2.5 s o menos y el primer corte del render llega antes de 2.5 s

### tec-0002 v2 · Titular corto con una sola palabra clave en dorado (tipografia, propuesta, puntuación 4.25)
- Dónde: escena 2 (5.31–7.84 s)
- Por qué: pensada para historias 'player'; estado propuesta (sin uso probado: modo sombra); evidencia: 0 medida(s), 1 estimación(es) de R-0001; encaja con el guion: 1/1 reglas medibles se cumplen ya en el plan
- Cambio: `layout` None → **high** (escena 2)
- Cambio: `transition` punch → **cut** (escena 2)
- Regla en el plan: plan.escena_s <= 4 → medido 2.53 ✔
- Regla tras el render (QC): text.texto_en_pantalla_pct >= 0.6
- Comprobación: como máximo una palabra en dorado por titular y texto en pantalla en al menos el 60% de los fotogramas del render

## Técnicas descartadas
- tec-0003 Cierre con pregunta al espectador y logo en silencio: pide un final 'debate' y el guion aprobado cierra con 'fact': el guion no se cambia
- tec-0001 Cifra que crece en un plano largo y estático: el guion no permite cumplir plan.escena_s >= 4 (medido 2.54): cambiarlo alteraría el ritmo de la narración aprobada

## Plan por escena (tiempos de la narración)
| # | inicio–fin (s) | tipo | ancla | transición | cámara | layout | efectos | técnicas | voz |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0–1.86 | stat | 0 | — | push-in | center | — | tec-0004 | Eighteen seasons. One team. |
| 1 | 1.86–5.31 | media | Reggie Miller played | whip | pan-right | center | — | tec-0005 | Reggie Miller played every one of them for the Pacers. |
| 2 | 5.31–7.84 | headline | No trade | cut | drift | high | — | tec-0002 | No trade. No move. Just Indiana. |
| 3 | 7.84–13.06 | media | When he retired | cut | push-in | center | — | — | When he retired in two thousand five, nobody in league histo… |
| 4 | 13.06–15.61 | stat | Two thousand five hundred | flash | pull-out | center | — | — | Two thousand five hundred sixty of them. |
| 5 | 15.61–18.75 | headline | Ray Allen | slide-up | tilt-up | center | — | — | Ray Allen needed until twenty eleven to pass him. |
| 6 | 18.75–21.0 | stat | Loyalty and range | cut | push-in | center | — | — | Loyalty and range, in one career. |

## Instrucciones para Remotion Pro
- Archivo listo para renderizar: `test-storyboard.applied.json` (mismo formato que `template/episodes/*.json`; solo cambian campos de edición)
- Campos por escena: escena 0: {"camera": "push-in"}; escena 1: {"transition": "whip", "camera": "pan-right"}; escena 2: {"transition": "cut", "camera": "drift", "layout": "high"}; escena 3: {"transition": "cut", "camera": "push-in"}; escena 4: {"transition": "flash", "camera": "pull-out"}; escena 5: {"transition": "slide-up", "camera": "tilt-up"}; escena 6: {"transition": "cut", "camera": "push-in"}
- Render (solo con autorización): `cd template && bash scripts/render-pro.sh <ruta>/test-storyboard.applied.json out/test-storyboard.mp4 (solo con autorización)`

## Mezcla de audio
- template/audio-mix.json (render-pro.sh + episode-music.mjs): voz a -16 LUFS, música 21 dB por debajo de la voz (23 dB en la banda de la voz), ducking 8 dB, silencio de 0.6 s antes del payoff
- Master: -14 LUFS integrado, pico real -1.5 dBTP (loudnorm en render-pro.sh) · efectos: 0 de 2 permitidos
- Música: drop en automático (~30%), payoff en automático (~75%)
- Subtítulos: salen de `words` (no se tocan); cada corte cae al inicio de una palabra (Q9).

## Control de calidad del plan
- Validador de Remotion Pro: OK · avisos: 0
- Q1 ✔ duración prevista 22.2 s (objetivo 20–26 s)
- Q2 ✔ ninguna escena de más de 6 s
- Q3 ✔ sin planos estáticos de más de 2.5 s
- Q4 ✔ mediana de escena 2.54 s (1.5–4 s)
- Q5 ✔ ninguna transición animada tres veces seguidas
- Q6 ✔ 5 movimientos de cámara distintos
- Q7 ✔ 0 efectos colocados a mano (presupuesto 2)
- Q8 ✔ titulares legibles a 15 caracteres/s
- Q9 ✔ todos los cortes caen entre palabras (subtítulos y voz sincronizados)
- Q10 ✔ validador de Remotion Pro sin errores

Tras renderizar: `apply_plan.py qc <video.mp4> --plan plan.json` mide el vídeo y comprueba las reglas de cada técnica.
