# Preset de narración E2A «Energía educativa» v1 (Reel 4 Rules, 2026-11-24)

Sirve para cualquier Reel de reglas o fundamentos. Objetivo: un comunicador deportivo joven, con autoridad y curiosidad, que no grita todo el rato. La energía viene de la variación, no del volumen.

## 1. Toma (con créditos y con autorización previa del propietario)
- Voz: Deuce `DaueUomjhh8LFuAV8aGj`. No se cambia la identidad.
- Modelo: `eleven_v3`, una sola toma (`generations_count 1`).
- Coste: las marcas cuentan como caracteres (unos +20-40 %). Antes de pedir el visto bueno, pide siempre `estimate_only`. En este Reel: 734 caracteres = 733 créditos.
- Marcas por fase, una al principio de cada frase y nunca dentro de una palabra:
  - Hook: `[confident]`.
  - Explicación: `[clear]` / `[firmly]`.
  - Subida: `[building]`.
  - Palabra de impacto: `[excited]` / `[shouting]` (solo para UNA palabra: VIOLATION!, THREE!).
  - Giro: `[playful]` / `[emphatic]`.
  - Cierre: `[upbeat]`.
- Puntuación que dirige:
  - MAYÚSCULAS en la palabra clave.
  - «...» para la pausa de suspense (antes de revelar la infracción).
  - «?» en la pregunta que prepara la respuesta.
  - «!» solo en la respuesta.
- Las marcas no se oyen: se comprueba con la transcripción de Scribe (0 créditos). Las etiquetas aparecen como palabras entre corchetes y se eliminan del archivo de palabras.

Plantilla de texto (4 Rules):
```
[confident] These are the FOUR RULES every basketball player needs to understand.
[clear] First: TRAVELING. Catch the ball, set your pivot foot... [building] then lift it and put it back down while you're still holding the ball? [excited] That's a TRAVEL!
[energetic] Second: DOUBLE DRIBBLE. Stop your dribble, hold the ball... [pause] and start bouncing again? [shouting] VIOLATION!
[excited] Third: SCORING. Free throw: ONE! Inside the arc: TWO! [shouting] Beyond the arc: THREE! [playful] But step on that line? Still two!
[firmly] Fourth: FOULS. Push or hold an opponent and restrict their movement? That's a foul. [emphatic] But remember: not every foul means free throws.
[upbeat] Four rules. Play smarter. Follow E2A for more!
```

## 2. Postproducción (sin créditos), en este orden
1. **Énfasis por palabra:** `template/scripts/voice-emphasis.py`. Nuevo en este Reel.
   - Sube SOLO las palabras clave que la toma entrega más bajas que la explicación.
   - Ganancia fija con rampas de 25 ms en los huecos. Sin cambio de tono ni de tiempo.
   - Archivo: `tactical/episodes/rules4/rules4-voice-emphasis.json`.
   - Escalera de números: ONE +3,5 · TWO +4,5 · THREE +6 dB, para que el crescendo sea real.
2. **Curva por frase:** `template/scripts/voice-dynamics.py --preserve`, que nunca baja una frase.
   - Archivo: `rules4-voice-dynamics.json`.
   - Fases A hook / B explicación / C activación / D matiz / E cierre.
3. **Mezcla:** música original `music/e2a_music.py --no-sfx` (sin botes), ducking, −14 LUFS y TP ≤ −1 dBTP.

## 3. Curva de energía (la del brief, en dB frente a la explicación)
| Parte | Energía | Curva | Palabra que sube |
|---|---|---|---|
| Hook | 8/10 | +2 | FOUR RULES, EVERY |
| Traveling | 7 → 8 | 0 → +2,5 | TRAVEL! |
| Double dribble | 8,5 | +0,5 → +3 | pausa «...» y VIOLATION! |
| Scoring | 9 | +1,5 → +3 | ONE < TWO < THREE |
| Fouls | 7,5 | +0,5 → +1,5 | «not every foul» |
| Cierre | 8 | +1,5 / +2 | smarter, more (no se apaga) |

## 4. QC de voz (obligatorio)
Se mide con `template/scripts/voice-energy-qc.py` (0 créditos) y se anota en la entrega:
- **Variación de tono** (F0, semitonos p5–p95 y desviación).
  - 4 Rules: 10,2 st y 3,61 st.
  - Arrow V3: 8,9 / 3,28. HORNS: 9,8 / 3,51. Zone 1-3-1: 9,8 / 3,13.
- **Rango de energía** de la toma, p10–p95.
  - 4 Rules: 23,6 dB en bruto y 20,6 dB final.
  - Arrow V3: 22,4. HORNS: 15,6. Zone: 15,1.
- **Nivel de cada palabra clave** frente a la explicación: ninguna palabra de impacto puede quedar más de 3 dB por debajo de la explicación.
- Sin silencios > 0,7 s dentro del guion, sin clipping y −14 LUFS.

## 5. Reglas
- No aceptar una toma plana por estar técnicamente bien. Si los números de energía caen por debajo de los de Arrow V3, se propone otra toma al propietario.
- Nunca regenerar sin autorización ni para el trial: el trial reutiliza la misma toma.
- No cambiar automáticamente los vídeos ya terminados.
