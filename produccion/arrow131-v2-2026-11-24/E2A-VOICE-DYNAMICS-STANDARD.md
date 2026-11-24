# E2A Voice Dynamics Standard v1

Origen: Arrow Press 1-3-1 V2 (2026-11-24). Narrador: Deuce (`DaueUomjhh8LFuAV8aGj`, `eleven_multilingual_v2`). No se cambia nunca la identidad del narrador.

## Curva emocional (siempre la misma estructura)

| Fase | Qué es | Nivel vs explicación | Entrega |
|---|---|---|---|
| **A Hook** | La frase gancho y su remate | +1,5 / +2,5 dB (el remate por encima de la primera frase) | Seguridad y punch, frase corta |
| **B Explicación** | Presentar el sistema | 0 dB (referencia) | Clara, ritmo medio |
| **C Activación** | El momento de la acción (cruza, salta, ¡trap!, escapa, sprint) | +1 → +3 dB, pico en la palabra clave | Urgencia, frases cortas |
| **D Lecturas** | Qué hace cada defensor | 0 dB | Control, foco, sin prisa |
| **E Conclusión** | La idea final y la pregunta | −0,5 → +1 dB | Cálida, pregunta abierta |

Regla: la palabra de acción no puede quedar por debajo de la explicación. En V1, «It's a trap.» estaba 5 dB por debajo de «Half court isn't a line.», y «Sprint back.» 5 dB por debajo de la media.

## Postproducción sin créditos (`template/scripts/voice-dynamics.py`)

1. **Tono:**
   - highpass a 85 Hz;
   - −2 dB a 300 Hz (caja de una voz grave);
   - +3 dB a 2,8 kHz con Q 1,4 (presencia en el altavoz del móvil);
   - −1,5 dB a 7 kHz y de-esser (la sibilancia no sube más que la presencia).
2. **Compresión moderada:** umbral −24 dB, 2,5:1, ataque 8 ms, release 140 ms.
3. **Curva:** ganancia por frase según el archivo de curva.
   - Los cambios ocurren solo en las pausas, con rampas ≤ 60 ms. Nunca dentro de una palabra.
   - Ganancia máxima ±6 dB.
4. **Nivel de la voz:** ganancia estática a −16 LUFS y limitador sobremuestreado a −2 dBFS. Sin loudnorm dinámico, que borraría la curva.
5. **Mezcla:**
   - música con ducking por sidechain (umbral 0,04, 5:1, ataque 25 ms, release 350 ms);
   - ganancia estática a **−14 LUFS integrados**;
   - limitador sobremuestreado (×4) a −1,5 dBFS, con **true peak ≤ −1 dBTP**;
   - 48 kHz;
   - sin sonidos de bote.

```bash
python3 scripts/voice-dynamics.py --voice public/<reel>/voice.wav --words <words.json> \
  --curve tactical/episodes/<reel>/<reel>-voice-dynamics.json --out voice-v2.wav \
  --music public/<reel>/music.wav --mix-out mix.wav --duration <s> --report voice-report.json
```

El archivo de curva tiene una línea por frase del guion, en orden: `["texto", offset_dB, "fase"]`. Ejemplo: `template/tactical/episodes/arrow131/arrow131-voice-dynamics.json`.

## Si hace falta una toma nueva (con créditos y con autorización del propietario)

- Se mantienen la misma voz y el mismo modelo.
- El guion se marca por fases con puntuación, que es lo que `eleven_multilingual_v2` entiende:
  - frases cortas en C;
  - «!» solo en la palabra clave;
  - «...» para la pausa de suspense.
- Ajustes para más expresión: stability 0,35–0,40, similarity 0,75, style 0,35–0,45, speaker boost activado. Una sola toma (generations_count 1).
- Antes de gastar, decisión del propietario con una tarjeta y el coste estimado. 1 carácter ≈ 1 crédito: el guion completo de este reel son 610 caracteres.
- Después se aplica igualmente esta postproducción.

## QC de voz

- Tabla del nivel de cada frase relativo a la fase B. La fase C debe estar por encima de B y la frase clave en lo más alto.
- LUFS integrados, true peak y LRA del máster.
- Presencia (2–4 kHz frente a 150–500 Hz) y sibilancia (5–9 kHz frente a 2–4 kHz) comparadas con la versión anterior.
- Clip A/B de los momentos clave para escuchar.
