# Estándares de calidad

Se suman a los del pipeline (`template/scripts/validate-episode.mjs` y `template/scripts/qc-pro.mjs`),
no los sustituyen. Los valores de mezcla salen de `template/audio-mix.json`: si se cambian allí,
el plan los refleja.

## En el plan (`apply_plan.py plan`, antes de renderizar)

| Código | Regla | Gravedad |
|---|---|---|
| Q1 | Duración prevista 20–26 s (tácticos 20–60 s) | aviso |
| Q2 | Ninguna escena de más de 6 s (salvo `court`) | aviso |
| Q3 | Ningún plano con cámara `static` de más de 2.5 s (salvo `court`) | aviso |
| Q4 | Mediana de escena entre 1.5 y 4 s | aviso |
| Q5 | Ninguna transición animada (no `cut`) tres veces seguidas | aviso |
| Q6 | Con 6 escenas o más, al menos 3 movimientos de cámara distintos | aviso |
| Q7 | Efectos colocados a mano ≤ presupuesto (`sfxBudget` o `audio-mix.json` → 2) | error |
| Q8 | Titulares con tiempo de lectura: caracteres / 15 ≤ duración de la escena | aviso |
| Q9 | Ningún corte cae en mitad de una palabra (subtítulos y voz sincronizados) | aviso |
| Q10 | El validador de Remotion Pro no da errores | error |

Además, cada técnica se aplica de una en una y se vuelve a pasar el validador: si una técnica añade
un error o un aviso nuevo, se descarta y el plan explica por qué (con `--allow-warnings` se aceptan
avisos). El guion se protege con una huella: si cambiara, el plan se aborta.

## En el render (`apply_plan.py qc <video> --plan plan.json`)

| Código | Regla |
|---|---|
| R1 | 1080 × 1920 |
| R2 | 30 o 60 fps |
| R3 | Sonoridad integrada −14 ± 1 LUFS (master de `render-pro.sh`) |
| R4 | Pico real ≤ −1.0 dBTP (el master apunta a −1.5) |
| R5 | Primer cambio de plano ≤ 2.5 s |
| R6 | Ningún tramo de más de 4 s sin cambio visual (corte, destello o cambio de subtítulo) |
| R7 | Duración del render = duración del plan ± 0.5 s |

Y las reglas de cada técnica elegida (`comprobacion.reglas` con métricas del análisis). `qc` sale con
código 1 si algo falla; el resultado queda en `qc/qc.json` junto al plan.

## Mezcla (referencia, de `template/audio-mix.json`)

Voz −16 LUFS antes del master; música 21 dB por debajo de la voz (23 dB en la banda de la voz);
ducking 8 dB; silencio de 0.6 s antes del payoff; efectos −8 dB y como mucho 2 automáticos; master
−14 LUFS / −1.5 dBTP. Jerarquía: 1 voz, 2 música, 3 efectos.

## Lo que se evita (del brief del propietario)

Planos estáticos largos sin razón, transiciones repetidas, efectos por todas partes, música que tapa
la voz, subtítulos desincronizados, textos imposibles de leer, finales que no cierran, y cualquier
cambio del guion aprobado para "encajar" una técnica.
